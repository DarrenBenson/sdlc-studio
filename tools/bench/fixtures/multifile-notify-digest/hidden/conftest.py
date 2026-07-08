"""Pytest plumbing for the hidden acceptance suite.

Copy this directory somewhere outside the candidate workspace, then
point --workspace at the implementation under test:

    PYTHONSAFEPATH=1 python3 -m pytest <copy> -q --workspace /path/to/workspace
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKSPACE_MODULES = (
    "models",
    "store",
    "routing",
    "throttle",
    "quiet_hours",
    "audit_log",
    "cli",
)


def pytest_addoption(parser):
    parser.addoption(
        "--workspace",
        action="store",
        required=True,
        help="path to the workspace directory containing the service modules",
    )


@pytest.fixture(scope="session")
def workspace(request):
    """Import the workspace's modules with the workspace on sys.path.

    The path goes at position 0 so the modules' own cross-imports
    resolve against the workspace; both the path entry and the imported
    modules are removed again when the session ends.
    """
    root = Path(request.config.getoption("--workspace")).resolve()
    if not root.is_dir():
        pytest.exit(f"--workspace is not a directory: {root}", returncode=4)
    sys.path.insert(0, str(root))
    for name in WORKSPACE_MODULES:
        sys.modules.pop(name, None)
    try:
        modules = {name: importlib.import_module(name) for name in WORKSPACE_MODULES}
        yield SimpleNamespace(**modules)
    finally:
        sys.path.remove(str(root))
        for name in WORKSPACE_MODULES:
            sys.modules.pop(name, None)


@pytest.fixture
def service(workspace):
    """A fresh notification service per test."""
    return workspace.routing.NotificationService()
