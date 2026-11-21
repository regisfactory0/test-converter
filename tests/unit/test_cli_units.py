"""Unit tests: the `--units` branch of `main` with fresh in-memory registries."""

import pytest

from conv.cli import main
from conv.registry import Quantity, Registry, Unit, build_default_registry, build_distance_registry

Capsys = pytest.CaptureFixture[str]

FULL_LIST = (
    "distance:\n"
    "  mm (millimetre)\n"
    "  cm (centimetre)\n"
    "  m (metre)\n"
    "  km (kilometre)\n"
    "  in (inch)\n"
    "  ft (foot)\n"
    "  yd (yard)\n"
    "  mi (mile)\n"
    "temperature:\n"
    "  C (celsius)\n"
    "  F (fahrenheit)\n"
    "  K (kelvin)\n"
)
TEMPERATURE_LIST = "temperature: C (celsius), F (fahrenheit), K (kelvin)\n"
DISTANCE_LIST = (
    "distance: mm (millimetre), cm (centimetre), m (metre), km (kilometre), "
    "in (inch), ft (foot), yd (yard), mi (mile)\n"
)


def run(
    capsys: Capsys,
    *argv: str,
    registry: Registry | None = None,
    distance_registry: Registry | None = None,
) -> tuple[int, str, str]:
    code = main(
        list(argv),
        registry if registry is not None else build_default_registry(),
        distance_registry=(
            distance_registry if distance_registry is not None else build_distance_registry()
        ),
    )
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def quantity(name: str, *units: Unit) -> Quantity:
    return Quantity(name=name, base=units[0].symbol, units=units)


def registry_with(*quantities: Quantity) -> Registry:
    registry = Registry()
    for item in quantities:
        registry.register(item)
    return registry


def area_registry() -> Registry:
    registry = build_default_registry()
    registry.register(quantity("area", Unit("a", "are"), Unit("ha", "hectare", factor=100.0)))
    return registry


def assert_usage_and_error(code: int, out: str, err: str) -> None:
    assert code == 1
    assert out == ""
    assert "Traceback" not in err
    lines = err.splitlines()
    assert len(lines) == 2, err
    assert lines[0].startswith("usage:")
    assert lines[1].startswith("conv: error:")


@pytest.mark.parametrize("argv", [["--units"], ["-d", "--units"], ["--distance", "--units"]])
def test_units_prints_every_unit_grouped_by_quantity(capsys: Capsys, argv: list[str]) -> None:
    assert run(capsys, *argv) == (0, FULL_LIST, "")


def test_units_flag_order_with_distance_flag_does_not_matter(capsys: Capsys) -> None:
    assert run(capsys, "--units", "-d") == (0, FULL_LIST, "")


def test_units_without_registries_uses_the_built_in_ones(capsys: Capsys) -> None:
    assert main(["--units"]) == 0
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == (FULL_LIST, "")


@pytest.mark.parametrize(
    "argv",
    [
        ["--units", "1", "C", "F"],
        ["--units", "--list"],
        ["--list", "--units"],
        ["-d", "--units", "--list"],
        ["--units", "1", "m", "km", "-d"],
        ["--units", "extra"],
        ["--units", "--units"],
    ],
)
def test_units_with_other_arguments_prints_usage_and_error(capsys: Capsys, argv: list[str]) -> None:
    assert_usage_and_error(*run(capsys, *argv))


def test_units_lists_a_quantity_added_to_the_registry_in_name_order(capsys: Capsys) -> None:
    code, out, err = run(capsys, "--units", registry=area_registry())
    assert (code, err) == (0, "")
    assert out == ("area:\n  a (are)\n  ha (hectare)\n" + FULL_LIST)


def test_units_with_distance_flag_lists_the_extra_quantity_too(capsys: Capsys) -> None:
    code, out, err = run(capsys, "-d", "--units", registry=area_registry())
    assert (code, err) == (0, "")
    assert out.startswith("area:\n  a (are)\n  ha (hectare)\ndistance:\n")


def test_units_lists_units_in_registration_order_not_alphabetical(capsys: Capsys) -> None:
    registry = registry_with(quantity("zeta", Unit("z", "zed"), Unit("b", "bee"), Unit("a", "ay")))
    code, out, err = run(capsys, "--units", registry=registry)
    assert (code, err) == (0, "")
    assert out.startswith("distance:\n")
    assert out.endswith("zeta:\n  z (zed)\n  b (bee)\n  a (ay)\n")


def test_units_lists_a_custom_distance_registry(capsys: Capsys) -> None:
    custom = registry_with(quantity("reach", Unit("r", "rod"), Unit("p", "pole", factor=2.0)))
    code, out, err = run(capsys, "--units", distance_registry=custom)
    assert (code, err) == (0, "")
    assert out == (
        "reach:\n  r (rod)\n  p (pole)\n"
        "temperature:\n  C (celsius)\n  F (fahrenheit)\n  K (kelvin)\n"
    )
    assert "distance" not in out


def test_units_with_distance_flag_uses_custom_distance_registry_and_kept_registry(
    capsys: Capsys,
) -> None:
    custom = registry_with(quantity("reach", Unit("r", "rod")))
    code, out, err = run(capsys, "-d", "--units", distance_registry=custom)
    assert (code, err) == (0, "")
    assert out == "reach:\n  r (rod)\ntemperature:\n  C (celsius)\n  F (fahrenheit)\n  K (kelvin)\n"


def test_units_does_not_mutate_the_registries(capsys: Capsys) -> None:
    registry = area_registry()
    distance = build_distance_registry()
    before = (registry.quantities(), distance.quantities())
    run(capsys, "--units", registry=registry, distance_registry=distance)
    assert (registry.quantities(), distance.quantities()) == before


def test_list_output_is_unchanged_by_the_units_flag(capsys: Capsys) -> None:
    assert run(capsys, "--list") == (0, TEMPERATURE_LIST, "")
    assert run(capsys, "-d", "--list") == (0, DISTANCE_LIST, "")


def test_conversion_is_unchanged_by_the_units_flag(capsys: Capsys) -> None:
    assert run(capsys, "100", "C", "F") == (0, "212.0\n", "")
    assert run(capsys, "-d", "1", "mi", "km") == (0, "1.609344\n", "")


def test_usage_and_help_mention_units(capsys: Capsys) -> None:
    code, out, err = run(capsys, "--help")
    assert (code, err) == (0, "")
    assert out.splitlines()[0].endswith("| conv --units")
    assert "--units" in out
