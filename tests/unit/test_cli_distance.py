"""Unit tests: `-d` / `--distance` flag handling in `main` with a fresh distance registry."""

import pytest

import conv.cli
from conv.cli import main
from conv.registry import Quantity, Registry, Unit, build_default_registry, build_distance_registry

Capsys = pytest.CaptureFixture[str]

DISTANCE_LIST = (
    "distance: mm (millimetre), cm (centimetre), m (metre), km (kilometre), "
    "in (inch), ft (foot), yd (yard), mi (mile)\n"
)


def run(capsys: Capsys, *argv: str, registry: Registry | None = None) -> tuple[int, str, str]:
    code = main(list(argv), registry, distance_registry=build_distance_registry())
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def widget_registry() -> Registry:
    registry = Registry()
    registry.register(
        Quantity(
            name="widget",
            base="w",
            units=(Unit("w", "widget"), Unit("v", "vat", factor=2.0)),
        )
    )
    return registry


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


@pytest.mark.parametrize("flag", ["-d", "--distance"])
def test_flag_converts_distance_and_prints_rounded_repr(capsys: Capsys, flag: str) -> None:
    assert run(capsys, flag, "1", "mi", "km") == (0, "1.609344\n", "")


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (("100", "km", "mi"), "62.137119\n"),
        (("1", "m", "ft"), "3.28084\n"),
        (("5280", "ft", "mi"), "1.0\n"),
        (("1", "ft", "in"), "12.0\n"),
        (("1", "yd", "cm"), "91.44\n"),
    ],
)
def test_distance_conversions_use_six_place_rounding(
    capsys: Capsys, argv: tuple[str, ...], expected: str
) -> None:
    assert run(capsys, "-d", *argv) == (0, expected, "")


@pytest.mark.parametrize(
    "argv",
    [
        ("-d", "1", "mi", "km"),
        ("1", "-d", "mi", "km"),
        ("1", "mi", "-d", "km"),
        ("1", "mi", "km", "-d"),
        ("1", "mi", "km", "--distance"),
        ("--distance", "1", "mi", "km"),
    ],
)
def test_flag_is_accepted_in_any_position(capsys: Capsys, argv: tuple[str, ...]) -> None:
    assert run(capsys, *argv) == (0, "1.609344\n", "")


@pytest.mark.parametrize(
    "argv",
    [
        ("-d", "-d", "1", "mi", "km"),
        ("-d", "--distance", "1", "mi", "km"),
        ("--distance", "1", "-d", "mi", "km", "--distance"),
    ],
)
def test_repeated_flag_is_the_same_as_one(capsys: Capsys, argv: tuple[str, ...]) -> None:
    assert run(capsys, *argv) == (0, "1.609344\n", "")


@pytest.mark.parametrize("flag", ["-d", "--distance"])
def test_negative_value_after_flag_is_read_as_a_number(capsys: Capsys, flag: str) -> None:
    code, out, err = run(capsys, flag, "-3", "ft", "m")
    line = assert_single_error(code, out, err)
    assert "negative" in line
    assert "unrecognized option" not in line


@pytest.mark.parametrize("value", ["0", "-0", "0.0"])
def test_zero_prints_zero_point_zero(capsys: Capsys, value: str) -> None:
    assert run(capsys, "-d", value, "ft", "m") == (0, "0.0\n", "")


@pytest.mark.parametrize(
    ("argv", "unit"),
    [
        (("-d", "1", "C", "F"), "C"),
        (("-d", "1", "m", "K"), "K"),
        (("-d", "1", "celsius", "m"), "celsius"),
    ],
)
def test_temperature_units_are_errors_in_distance_mode(
    capsys: Capsys, argv: tuple[str, ...], unit: str
) -> None:
    code, out, err = run(capsys, *argv)
    assert unit in assert_single_error(code, out, err)


@pytest.mark.parametrize("value", ["abc", "nan", "NaN", "inf", "-inf", "1,5", ""])
def test_invalid_numbers_are_one_error_line(capsys: Capsys, value: str) -> None:
    code, out, err = run(capsys, "-d", value, "m", "ft")
    assert "invalid number" in assert_single_error(code, out, err)


def test_overflowing_result_is_an_error_not_inf(capsys: Capsys) -> None:
    assert_single_error(*run(capsys, "-d", "1e308", "mi", "mm"))


@pytest.mark.parametrize(
    "argv",
    [("-d",), ("-d", "1", "m"), ("-d", "1", "m", "ft", "in"), ("--distance",), ("-d", "-d")],
)
def test_wrong_argument_count_prints_usage_and_error(capsys: Capsys, argv: tuple[str, ...]) -> None:
    assert_usage_and_error(*run(capsys, *argv))


def test_unknown_option_with_flag_prints_usage_and_error(capsys: Capsys) -> None:
    assert_usage_and_error(*run(capsys, "-d", "--bogus", "1", "m", "ft"))


@pytest.mark.parametrize(
    "argv",
    [("--distance", "--list"), ("-d", "--list"), ("--list", "-d"), ("--list", "--distance")],
)
def test_list_with_flag_prints_only_the_distance_quantity(
    capsys: Capsys, argv: tuple[str, ...]
) -> None:
    assert run(capsys, *argv) == (0, DISTANCE_LIST, "")


def test_list_with_flag_and_other_arguments_prints_usage_and_error(capsys: Capsys) -> None:
    assert_usage_and_error(*run(capsys, "-d", "--list", "1", "m", "ft"))


def test_list_without_flag_does_not_show_distance(capsys: Capsys) -> None:
    code, out, err = run(capsys, "--list")
    assert (code, err) == (0, "")
    assert out.startswith("temperature:")
    assert "distance" not in out


@pytest.mark.parametrize(
    "argv", [("--help",), ("-h",), ("-d", "--help"), ("--distance", "-h"), ("--help", "-d")]
)
def test_help_mentions_distance_flags_and_returns_zero(
    capsys: Capsys, argv: tuple[str, ...]
) -> None:
    code, out, err = run(capsys, *argv)
    assert (code, err) == (0, "")
    assert "-d, --distance" in out


def test_registry_parameter_is_ignored_in_distance_mode(capsys: Capsys) -> None:
    other = widget_registry()
    assert run(capsys, "-d", "1", "mi", "km", registry=other) == (0, "1.609344\n", "")
    assert_single_error(*run(capsys, "-d", "1", "w", "v", registry=other))
    assert run(capsys, "-d", "--list", registry=other) == (0, DISTANCE_LIST, "")


def test_registry_parameter_serves_runs_without_flag(capsys: Capsys) -> None:
    assert run(capsys, "4", "v", "w", registry=widget_registry()) == (0, "8.0\n", "")


def test_without_flag_distance_units_are_unknown(capsys: Capsys) -> None:
    code, out, err = run(capsys, "1", "mi", "km")
    assert "mi" in assert_single_error(code, out, err)


def test_without_flag_temperature_still_converts(capsys: Capsys) -> None:
    assert run(capsys, "100", "C", "F") == (0, "212.0\n", "")


def test_negative_temperature_value_without_flag_is_unchanged(capsys: Capsys) -> None:
    assert run(capsys, "-40", "C", "F") == (0, "-40.0\n", "")


def test_custom_distance_registry_is_used_in_distance_mode(capsys: Capsys) -> None:
    custom = Registry()
    custom.register(
        Quantity(
            name="distance",
            base="x",
            units=(Unit("x", "ex"), Unit("y", "why", factor=3.0)),
        )
    )
    code = main(["-d", "2", "y", "x"], distance_registry=custom)
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "6.0\n", "")


def test_distance_mode_defaults_to_builtin_distance_registry(capsys: Capsys) -> None:
    code = main(["-d", "1", "mi", "km"], build_default_registry())
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (0, "1.609344\n", "")


def test_convert_receives_the_distance_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_convert(*args: object, **kwargs: object) -> float:
        calls.append((args, kwargs))
        return 1.0

    monkeypatch.setattr(conv.cli, "convert", fake_convert)
    distance = build_distance_registry()
    assert main(["--distance", "1", "mi", "km"], distance_registry=distance) == 0
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == (1.0, "mi", "km")
    assert kwargs["registry"] is distance
