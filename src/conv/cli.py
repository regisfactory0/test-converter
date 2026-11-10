"""The ``conv`` command line.

Stub: argument handling, output and errors are built by the CLI features.
"""

from conv.core import convert
from conv.registry import Registry

__all__ = ["convert", "main"]


def main(argv: list[str] | None = None, registry: Registry | None = None) -> int:
    """Run ``conv`` with ``argv`` (default: the process arguments); return the exit code."""
    return 0
