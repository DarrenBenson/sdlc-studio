"""Hidden-suite pytest configuration for change-request-ledger-drift.

The workspace under test is supplied via the required ``--workspace``
flag. Workspace modules are imported with the workspace directory
appended to the END of ``sys.path``, so workspace files can never
shadow the standard library; every import is undone at teardown so
repeated scoring runs in one process stay independent.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_MODULE_NAMES = ("models", "validation", "dedupe", "refunds", "ledger")


def pytest_addoption(parser):
    parser.addoption(
        "--workspace",
        action="store",
        required=True,
        help="path to the workspace directory to score",
    )


@pytest.fixture(scope="session")
def workspace(request) -> Path:
    path = Path(request.config.getoption("--workspace")).resolve()
    if not path.is_dir():
        pytest.exit(f"--workspace does not point at a directory: {path}", returncode=4)
    return path


@pytest.fixture(scope="session")
def mod(workspace):
    """Namespace of freshly imported workspace modules."""
    saved = {
        name: sys.modules.pop(name)
        for name in _MODULE_NAMES
        if name in sys.modules
    }
    sys.path.append(str(workspace))
    try:
        imported = {
            name: importlib.import_module(name) for name in _MODULE_NAMES
        }
        yield SimpleNamespace(**imported)
    finally:
        sys.path.remove(str(workspace))
        for name in _MODULE_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)
