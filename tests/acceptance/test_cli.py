"""Acceptance tests: the `conv <value> <from> <to>` command line."""

import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

import pytest

import conv.cli
from conv.cli import main

CONV = Path(sys.executable).parent / "conv"
PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"


def run_conv(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed `conv` console script."""
    return subprocess.run(
        [str(CONV), *args], capture_output=True, text=True, timeout=30, check=False
    )


def assert_one_error_line(result: subprocess.CompletedProcess[str]) -> str:
    """The run failed with exit 1, empty stdout and one `conv: error:` line on stderr."""
    assert result.returncode == 1
    assert result.stdout == ""
    lines = result.stderr.splitlines()
    assert len(lines) == 1, result.stderr
    assert lines[0].startswith("conv: error:")
    return lines[0]


def test_convert_100_c_f() -> None:
    """AC-3.1: `conv 100 C F` prints exactly `212.0`, nothing on stderr, exit 0."""
    result = run_conv("100", "C", "F")
    assert result.stdout == "212.0\n"
    assert result.stderr == ""
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("100", "F", "C"), "37.777778\n"),
        (("98.6", "F", "C"), "37.0\n"),
        (("32", "F", "C"), "0.0\n"),
        (("273.15", "K", "C"), "0.0\n"),
        (("37", "C", "F"), "98.6\n"),
    ],
)
def test_output_rounded_to_six_places(args: tuple[str, ...], expected: str) -> None:
    """AC-3.2: output is the repr of the result rounded to 6 places; -0.0 prints as 0.0."""
    result = run_conv(*args)
    assert result.stdout == expected
    assert result.returncode == 0


def test_negative_value_is_not_an_option() -> None:
    """AC-3.3: `conv -40 C F` prints `-40.0`, exit 0."""
    result = run_conv("-40", "C", "F")
    assert result.stdout == "-40.0\n"
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("args", "expected"),
    [(("0", "C", "K"), "273.15\n"), (("1e3", "K", "C"), "726.85\n")],
)
def test_kelvin_output(args: tuple[str, ...], expected: str) -> None:
    """AC-3.4: `conv 0 C K` prints `273.15`; `conv 1e3 K C` prints `726.85`."""
    result = run_conv(*args)
    assert result.stdout == expected
    assert result.returncode == 0


@pytest.mark.parametrize("value", ["abc", "", "nan", "inf", "NaN"])
def test_invalid_number(value: str) -> None:
    """AC-3.5: an invalid number gives one `conv: error:` line, empty stdout, exit 1."""
    assert_one_error_line(run_conv(value, "C", "F"))


def test_overflow_is_an_error() -> None:
    """AC-3.5, AC-1.9: `conv 1e308 C F` overflows and fails like an invalid number, exit 1."""
    assert_one_error_line(run_conv("1e308", "C", "F"))


def test_unknown_unit() -> None:
    """AC-3.6: `conv 10 C X` gives one `conv: error:` line naming X, exit 1."""
    line = assert_one_error_line(run_conv("10", "C", "X"))
    assert "X" in line.removeprefix("conv: error:")


def test_below_absolute_zero() -> None:
    """AC-3.7: `conv -500 F C` gives one `conv: error:` line mentioning absolute zero, exit 1."""
    line = assert_one_error_line(run_conv("-500", "F", "C"))
    assert "absolute zero" in line.lower()


@pytest.mark.parametrize("args", [(), ("100",), ("100", "C"), ("100", "C", "F", "K")])
def test_wrong_argument_count(args: tuple[str, ...]) -> None:
    """AC-3.8: a wrong argument count shows a usage line and a `conv: error:` line, exit 1."""
    result = run_conv(*args)
    assert result.returncode == 1
    lines = result.stderr.splitlines()
    assert any(line.lower().startswith("usage") for line in lines), result.stderr
    assert any(line.startswith("conv: error:") for line in lines), result.stderr


def test_help() -> None:
    """AC-3.9: `conv --help` prints usage to stdout, exit 0."""
    result = run_conv("--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_main_delegates_to_convert(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC-3.10: main(argv) returns the exit code and calls the library's convert."""
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_convert(*args: Any, **kwargs: Any) -> float:
        calls.append((args, kwargs))
        return 42.0

    monkeypatch.setattr(conv.cli, "convert", fake_convert)
    exit_code = main(["100", "C", "F"])
    assert exit_code == 0
    assert len(calls) == 1
    args, _ = calls[0]
    assert args[0] == 100.0
    assert args[1:3] == ("C", "F")
    assert capsys.readouterr().out == "42.0\n"


def test_main_returns_one_on_error(capsys: pytest.CaptureFixture[str]) -> None:
    """AC-3.10: main(argv) returns 1 for invalid input instead of exiting."""
    assert main(["10", "C", "X"]) == 1
    assert capsys.readouterr().err.startswith("conv: error:")


@pytest.mark.parametrize(
    "args",
    [
        ("abc", "C", "F"),
        ("", "C", "F"),
        ("nan", "C", "F"),
        ("inf", "C", "F"),
        ("1e308", "C", "F"),
        ("10", "C", "X"),
        ("10", "", "F"),
        ("10", "°C", "F"),
        ("-500", "F", "C"),
        (),
        ("100",),
        ("100", "C", "F", "K"),
        ("--bogus",),
    ],
)
def test_no_traceback(args: tuple[str, ...]) -> None:
    """AC-3.11: no invalid input prints a Python traceback; each exits 1 with `conv: error:`."""
    result = run_conv(*args)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "conv: error:" in result.stderr


def test_runs_fast() -> None:
    """Performance: `conv 100 C F` finishes in under 0.5 s."""
    run_conv("100", "C", "F")  # warm the file cache
    start = time.perf_counter()
    result = run_conv("100", "C", "F")
    elapsed = time.perf_counter() - start
    assert result.stdout == "212.0\n"
    assert elapsed < 0.5


def test_no_runtime_dependencies() -> None:
    """Security: the package declares no runtime dependencies."""
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    assert project["dependencies"] == []
    assert project["scripts"]["conv"] == "conv.cli:main"
