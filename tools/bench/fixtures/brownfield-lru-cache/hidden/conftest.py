"""Provides the `lru_cache_cls` fixture from a --workspace CLI flag, so the hidden suite
can be pointed at any arm's solution directory at scoring time without editing the test file."""
import importlib.util
import sys
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--workspace", action="store", required=True,
                      help="path to the arm's solution workspace to score")


@pytest.fixture
def lru_cache_cls(request):
    workspace = Path(request.config.getoption("--workspace")).resolve()
    spec = importlib.util.spec_from_file_location("lru_cache_under_test", workspace / "lru_cache.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lru_cache_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod.LRUCache
