from pathlib import Path

from conv import convert
from conv.registry import Registry

README = Path(__file__).resolve().parents[2] / "README.md"
HEADING = "## Adding a quantity"
FENCE_OPEN = "```python"
FENCE_CLOSE = "```"


def _section_lines() -> list[str]:
    lines = README.read_text(encoding="utf-8").splitlines()
    assert HEADING in lines, "README.md has no '## Adding a quantity' heading"
    rest = lines[lines.index(HEADING) + 1 :]
    end = next((i for i, line in enumerate(rest) if line.startswith("## ")), len(rest))
    return rest[:end]


def _python_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    current: list[str] | None = None
    for line in lines:
        if current is None:
            if line.strip() == FENCE_OPEN:
                current = []
        elif line.strip() == FENCE_CLOSE:
            blocks.append("\n".join(current))
            current = None
        else:
            current.append(line)
    return blocks


def test_adding_a_quantity_section_has_exactly_one_python_block() -> None:
    assert len(_python_blocks(_section_lines())) == 1


def test_adding_a_quantity_example_runs_and_converts_km_to_m() -> None:
    (block,) = _python_blocks(_section_lines())
    namespace: dict[str, object] = {}

    exec(compile(block, "README.md", "exec"), namespace)

    registry = namespace["registry"]
    assert isinstance(registry, Registry)
    assert convert(1, "km", "m", registry=registry) == 1000.0
    assert registry.find("km") is not None
