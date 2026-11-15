"""Skips the tests of features not built yet when SKIP_UNBUILT_FEATURES=1."""

import os
from pathlib import Path

import pytest

BACKLOG = Path(__file__).resolve().parents[2] / "specs" / "features" / "backlog"


def pytest_configure(config):
    config.addinivalue_line("markers", "feature(slug): the feature this test belongs to")


def pytest_collection_modifyitems(config, items):
    if os.environ.get("SKIP_UNBUILT_FEATURES") != "1":
        return
    for item in items:
        marker = item.get_closest_marker("feature")
        if marker and (BACKLOG / marker.args[0]).is_dir():
            slug = marker.args[0]
            item.add_marker(pytest.mark.skip(reason=f"feature {slug} is not built yet"))
