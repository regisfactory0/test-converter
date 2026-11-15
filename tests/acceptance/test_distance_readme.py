"""Acceptance tests: the README documents distance mode and keeps "Adding a quantity"."""

from pathlib import Path

import pytest

pytestmark = pytest.mark.feature("cli-distance")

README = Path(__file__).resolve().parents[2] / "README.md"


def section(title: str) -> str:
    """The text of the README's `## <title>` section, up to the next `## ` heading."""
    lines = README.read_text(encoding="utf-8").splitlines()
    heading = f"## {title}"
    assert heading in lines, f"README has no {heading!r} section"
    start = lines.index(heading) + 1
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def test_readme_keeps_adding_a_quantity() -> None:
    """AC-D.1: the README keeps its "Adding a quantity" section."""
    assert "register" in section("Adding a quantity")


def test_readme_distance_section() -> None:
    """AC-D.2: the README's "Distance" section shows `--distance`, `-d --list` and the library."""
    text = section("Distance")
    assert "conv --distance" in text
    assert "conv -d --list" in text
    assert "build_distance_registry()" in text
