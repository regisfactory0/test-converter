"""Acceptance tests: the `conv --distance` command line."""

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

import conv.cli

pytestmark = pytest.mark.feature("cli-distance")

CONV = Path(sys.executable).parent / "conv"
DISTANCE_LINE = (
    "distance: mm (millimetre), cm (centimetre), m (metre), km (kilometre), "
    "in (inch), ft (foot), yd (yard), mi (mile)\n"
)


def run_conv(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed `conv` console script."""
    return subprocess.run(
        [str(CONV), *args], capture_output=True, text=True, timeout=30, check=False
    )


def assert_one_error_line(result: subprocess.CompletedProcess[str]) -> str:
    """The run failed with exit 1, empty stdout, no traceback and one `conv: error:` line."""
    assert result.returncode == 1, result
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    lines = result.stderr.splitlines()
    assert len(lines) == 1, result.stderr
    assert lines[0].startswith("conv: error:")
    return lines[0]


@pytest.mark.parametrize("flag", ["--distance", "-d"])
def test_distance_flag(flag: str) -> None:
    """AC-7.1: `conv --distance 1 mi km` and `conv -d 1 mi km` print exactly `1.609344`."""
    result = run_conv(flag, "1", "mi", "km")
    assert result.stdout == "1.609344\n"
    assert result.stderr == ""
    assert result.returncode == 0


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("100", "km", "mi"), "62.137119\n"),
        (("1", "m", "ft"), "3.28084\n"),
        (("5280", "ft", "mi"), "1.0\n"),
        (("1", "ft", "in"), "12.0\n"),
        (("1", "yd", "cm"), "91.44\n"),
    ],
)
def test_distance_output_format(args: tuple[str, ...], expected: str) -> None:
    """AC-7.2: distance results are rounded to 6 places and printed as repr, exit 0."""
    result = run_conv("-d", *args)
    assert result.stdout == expected
    assert result.returncode == 0


def test_negative_value_after_flag() -> None:
    """AC-7.3: `conv -d -3 ft m` reads -3 as a value and rejects it as negative, exit 1."""
    line = assert_one_error_line(run_conv("-d", "-3", "ft", "m"))
    assert "negative" in line.lower()


def test_zero_after_flag() -> None:
    """AC-7.3: `conv -d 0 ft m` prints `0.0`, exit 0."""
    result = run_conv("-d", "0", "ft", "m")
    assert result.stdout == "0.0\n"
    assert result.returncode == 0


def test_flag_after_positionals() -> None:
    """AC-7.4: `conv 1 mi km --distance` prints `1.609344`, exit 0."""
    result = run_conv("1", "mi", "km", "--distance")
    assert result.stdout == "1.609344\n"
    assert result.returncode == 0


@pytest.mark.parametrize(
    "args",
    [("abc", "m", "ft"), ("nan", "m", "ft"), ("1", "C", "F"), ("1e308", "mi", "mm")],
)
def test_invalid_distance_input(args: tuple[str, ...]) -> None:
    """AC-7.5: invalid numbers, non-distance units and overflow give one error line, exit 1."""
    line = assert_one_error_line(run_conv("-d", *args))
    if args[1] == "C":
        assert "C" in line.removeprefix("conv: error:")


@pytest.mark.parametrize("args", [(), ("1", "m"), ("1", "m", "ft", "in")])
def test_distance_wrong_argument_count(args: tuple[str, ...]) -> None:
    """AC-7.6: a wrong positional count with the flag shows usage plus an error line, exit 1."""
    result = run_conv("-d", *args)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    lines = result.stderr.splitlines()
    assert any(line.lower().startswith("usage") for line in lines), result.stderr
    assert any(line.startswith("conv: error:") for line in lines), result.stderr


@pytest.mark.parametrize("flag", ["--distance", "-d"])
def test_distance_list(flag: str) -> None:
    """AC-7.7: `conv --distance --list` / `conv -d --list` print exactly the distance line."""
    result = run_conv(flag, "--list")
    assert result.stdout == DISTANCE_LINE
    assert result.returncode == 0


def test_distance_list_with_conversion_arguments() -> None:
    """AC-7.7: `conv -d --list 1 m ft` writes a `conv: error:` line, exit 1."""
    result = run_conv("-d", "--list", "1", "m", "ft")
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert any(line.startswith("conv: error:") for line in result.stderr.splitlines())


def test_plain_list_unchanged() -> None:
    """AC-7.7: plain `conv --list` still prints only temperature (AC-4.1 unchanged)."""
    result = run_conv("--list")
    assert result.stdout == "temperature: C (celsius), F (fahrenheit), K (kelvin)\n"
    assert result.returncode == 0


def test_help_mentions_distance() -> None:
    """AC-7.8: `conv --help` mentions `--distance` on stdout, exit 0."""
    result = run_conv("--help")
    assert result.returncode == 0
    assert "--distance" in result.stdout


def test_main_uses_distance_registry(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC-7.9: main(["--distance", …]) calls convert once with a distance-only registry."""
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_convert(*args: Any, **kwargs: Any) -> float:
        calls.append((args, kwargs))
        return 1.5

    monkeypatch.setattr(conv.cli, "convert", fake_convert)
    assert conv.cli.main(["--distance", "1", "mi", "km"]) == 0
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0] == 1.0
    assert args[1:3] == ("mi", "km")
    registry = kwargs["registry"] if "registry" in kwargs else args[3]
    assert registry is not None
    assert [quantity.name for quantity in registry.quantities()] == ["distance"]
    assert capsys.readouterr().out == "1.5\n"
