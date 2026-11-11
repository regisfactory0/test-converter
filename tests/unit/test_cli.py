"""Unit tests: argument parsing and output formatting through `main(argv)`."""

import pytest

import conv.cli
from conv.cli import main
from conv.registry import Quantity, Registry, Unit, build_default_registry

Capsys = pytest.CaptureFixture[str]


def run(capsys: Capsys, *argv: str) -> tuple[int, str, str]:
    code = main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def assert_single_error(code: int, out: str, err: str) -> str:
    assert code == 1
    assert out == ""
    assert "Traceback" not in err
    lines = err.splitlines()
    assert len(lines) == 1, err
    assert lines[0].startswith("conv: error:")
    return lines[0]


def assert_usage_and_error(code: int, out: str, err: str) -> None:
    assert code == 1
    assert out == ""
    assert "Traceback" not in err
    lines = err.splitlines()
    assert len(lines) == 2, err
    assert lines[0].startswith("usage:")
    assert lines[1].startswith("conv: error:")


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (("100", "C", "F"), "212.0\n"),
        (("100", "F", "C"), "37.777778\n"),
        (("-40", "C", "F"), "-40.0\n"),
        (("0", "C", "K"), "273.15\n"),
        (("1e3", "K", "C"), "726.85\n"),
        (("32", "F", "C"), "0.0\n"),
        (("-0.0", "C", "C"), "0.0\n"),
        (("-1e-9", "C", "C"), "0.0\n"),
        (("-1e-3", "C", "C"), "-0.001\n"),
        (("100", "celsius", "FAHRENHEIT"), "212.0\n"),
        (("100", "c", "f"), "212.0\n"),
    ],
)
def test_prints_rounded_repr_and_returns_zero(
    capsys: Capsys, argv: tuple[str, ...], expected: str
) -> None:
    assert run(capsys, *argv) == (0, expected, "")


def test_negative_exponent_value_is_a_value_not_an_option(capsys: Capsys) -> None:
    line = assert_single_error(*run(capsys, "-1e3", "C", "F"))
    assert "absolute zero" in line


@pytest.mark.parametrize("value", ["abc", "", "nan", "inf", "-inf", "NaN", "Infinity", "1e400"])
def test_invalid_number_is_one_error_line(capsys: Capsys, value: str) -> None:
    line = assert_single_error(*run(capsys, value, "C", "F"))
    assert "invalid number" in line


def test_unknown_unit_error_names_the_unit(capsys: Capsys) -> None:
    line = assert_single_error(*run(capsys, "10", "C", "X"))
    assert "X" in line


def test_below_absolute_zero_error_mentions_absolute_zero(capsys: Capsys) -> None:
    line = assert_single_error(*run(capsys, "-500", "F", "C"))
    assert "absolute zero" in line


def test_overflow_is_an_error_not_inf(capsys: Capsys) -> None:
    assert_single_error(*run(capsys, "1e308", "C", "F"))


@pytest.mark.parametrize(
    "argv",
    [(), ("100",), ("100", "C"), ("100", "C", "F", "extra")],
    ids=["none", "one", "two", "four"],
)
def test_wrong_argument_count_prints_usage_and_error(capsys: Capsys, argv: tuple[str, ...]) -> None:
    assert_usage_and_error(*run(capsys, *argv))


@pytest.mark.parametrize("option", ["--", "--list", "--bogus", "-x", "-"])
def test_unknown_option_prints_usage_and_error(capsys: Capsys, option: str) -> None:
    assert_usage_and_error(*run(capsys, option, "C", "F"))


@pytest.mark.parametrize(
    "argv",
    [("--help",), ("-h",), ("100", "C", "F", "--help"), ("--help", "x")],
)
def test_help_goes_to_stdout_and_returns_zero(capsys: Capsys, argv: tuple[str, ...]) -> None:
    code, out, err = run(capsys, *argv)
    assert code == 0
    assert out.startswith("usage:")
    assert err == ""


def test_main_reads_process_arguments_when_argv_is_none(
    capsys: Capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["conv", "100", "C", "F"])
    assert main() == 0
    assert capsys.readouterr().out == "212.0\n"


def test_calls_library_convert_with_parsed_value_and_units(
    capsys: Capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[object, ...]] = []

    def fake_convert(value: float, from_unit: str, to_unit: str, **kwargs: object) -> float:
        calls.append((value, from_unit, to_unit, kwargs))
        return 1.23456789

    monkeypatch.setattr(conv.cli, "convert", fake_convert)
    assert run(capsys, "-4.5", "foo", "bar") == (0, "1.234568\n", "")
    assert calls == [(-4.5, "foo", "bar", {"registry": None})]


def test_registry_is_passed_through_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = Registry()
    seen: list[object] = []

    def fake_convert(value: float, from_unit: str, to_unit: str, registry: object = None) -> float:
        seen.append(registry)
        return 0.0

    monkeypatch.setattr(conv.cli, "convert", fake_convert)
    assert main(["1", "a", "b"], registry) == 0
    assert seen == [registry]


def test_custom_registry_units_convert(capsys: Capsys) -> None:
    registry = build_default_registry()
    registry.register(
        Quantity(
            name="amount",
            base="u",
            units=(
                Unit(symbol="u", name="unit"),
                Unit(symbol="ku", name="kilounit", factor=1000.0),
            ),
        )
    )
    code = main(["2", "ku", "u"], registry)
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "2000.0\n", "")


def test_default_registry_does_not_know_custom_units(capsys: Capsys) -> None:
    assert_single_error(*run(capsys, "2", "ku", "u"))


def test_library_error_message_is_relayed_on_one_line(
    capsys: Capsys, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_convert(*args: object, **kwargs: object) -> float:
        raise conv.cli.ConversionError("boom")

    monkeypatch.setattr(conv.cli, "convert", failing_convert)
    assert run(capsys, "1", "C", "F") == (1, "", "conv: error: boom\n")
