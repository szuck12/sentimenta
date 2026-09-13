# backend/conftest.py
# Root pytest hooks: the --runmodel gate for real-model tests.

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the --runmodel flag used to gate model tests."""
    parser.addoption(
        "--runmodel",
        action="store_true",
        default=False,
        help=(
            "Run tests marked 'model' that download and execute the "
            "real Hugging Face model."
        ),
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip model-marked tests unless --runmodel was passed."""
    if config.getoption("--runmodel"):
        return
    skip = pytest.mark.skip(
        reason="need --runmodel to run real model tests"
    )
    for item in items:
        if "model" in item.keywords:
            item.add_marker(skip)
