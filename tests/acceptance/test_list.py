"""Acceptance tests: `conv --list`."""

import subprocess
import sys
from pathlib import Path

import pytest

from conv.cli import main
from conv.registry import Quantity, Unit, build_default_registry

CONV = Path(sys.executable).parent / "conv"


def run_conv(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed `conv` console script."""
    return subprocess.run(
        [str(CONV), *args], capture_output=True, text=True, timeout=30, check=False
    )


def test_list_default() -> None:
    """AC-4.1: `conv --list` prints exactly the temperature line, exit 0."""
    result = run_conv("--list")
    assert result.stdout == "temperature: C (celsius), F (fahrenheit), K (kelvin)\n"
    assert result.returncode == 0


def test_list_sorts_quantities_keeps_unit_order(capsys: pytest.CaptureFixture[str]) -> None:
    """AC-4.2: quantities print one per line, alphabetically; units in registration order."""
    registry = build_default_registry()
    registry.register(
        Quantity(
            name="mass",
            base="kg",
            units=(Unit(symbol="kg", name="kilogram"), Unit(symbol="g", name="gram", factor=0.001)),
        )
    )
    registry.register(
        Quantity(
            name="length",
            base="m",
            units=(
                Unit(symbol="km", name="kilometre", factor=1000.0),
                Unit(symbol="m", name="metre"),
            ),
        )
    )
    assert main(["--list"], registry=registry) == 0
    assert capsys.readouterr().out == (
        "length: km (kilometre), m (metre)\n"
        "mass: kg (kilogram), g (gram)\n"
        "temperature: C (celsius), F (fahrenheit), K (kelvin)\n"
    )


@pytest.mark.parametrize("args", [("--list", "1", "C", "F"), ("1", "C", "F", "--list")])
def test_list_with_conversion_arguments(args: tuple[str, ...]) -> None:
    """AC-4.3: `--list` combined with conversion arguments is an error, exit 1."""
    result = run_conv(*args)
    assert result.returncode == 1
    assert any(line.startswith("conv: error:") for line in result.stderr.splitlines())
    assert "Traceback" not in result.stderr
