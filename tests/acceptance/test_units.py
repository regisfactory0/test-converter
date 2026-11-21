"""Acceptance tests: `conv --units`."""

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.feature("list-supported-units")

CONV = Path(sys.executable).parent / "conv"
UNITS_OUTPUT = (
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


def run_conv(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed `conv` console script."""
    return subprocess.run(
        [str(CONV), *args], capture_output=True, text=True, timeout=30, check=False
    )


@pytest.mark.parametrize("args", [("--units",), ("-d", "--units"), ("--units", "--distance")])
def test_units_lists_every_unit(args: tuple[str, ...]) -> None:
    """AC-8.1: `conv --units` (with or without `-d`) prints the 13 lines, exit 0."""
    result = run_conv(*args)
    assert result.stdout == UNITS_OUTPUT
    assert len(result.stdout.splitlines()) == 13
    assert result.stderr == ""
    assert result.returncode == 0


@pytest.mark.parametrize(
    "args",
    [
        ("--units", "1", "C", "F"),
        ("1", "C", "F", "--units"),
        ("--units", "--list"),
        ("--list", "--units"),
        ("-d", "--units", "1", "m", "ft"),
    ],
)
def test_units_with_other_arguments(args: tuple[str, ...]) -> None:
    """AC-8.2: `--units` with other arguments ends in one `conv: error:` line, exit 1."""
    result = run_conv(*args)
    assert result.returncode == 1, result
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    lines = result.stderr.splitlines()
    assert lines, result.stderr
    assert lines[-1].startswith("conv: error:")
    assert sum(line.startswith("conv: error:") for line in lines) == 1


def test_units_built_from_registry_data(capsys: pytest.CaptureFixture[str]) -> None:
    """AC-8.3: an extra quantity in the registry is listed; groups alphabetical, units in order."""
    from conv.cli import main
    from conv.registry import Quantity, Unit, build_default_registry

    registry = build_default_registry()
    registry.register(
        Quantity(
            name="area",
            base="a",
            units=(
                Unit(symbol="a", name="are", factor=1.0),
                Unit(symbol="ha", name="hectare", factor=100.0),
            ),
        )
    )
    assert main(["--units"], registry=registry) == 0
    assert capsys.readouterr().out == "area:\n  a (are)\n  ha (hectare)\n" + UNITS_OUTPUT
