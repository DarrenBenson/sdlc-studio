"""Provides the `workspace` fixture from a --workspace CLI flag, so the hidden suite can
be pointed at any arm's solution directory at scoring time without editing the test file."""
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--workspace", action="store", required=True,
                      help="path to the arm's solution workspace to score")


@pytest.fixture
def workspace(request) -> Path:
    return Path(request.config.getoption("--workspace")).resolve()
