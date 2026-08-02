"""Put this directory on `sys.path` for every module here, under both runners.

These tests import sibling fixture modules by bare name (`import test_precommit_window_guard`).
That resolves under `unittest discover`, which puts the start directory on the path, and NOT
under pytest - which `verify_ac` invokes to check a criterion. So a story's own verifier could
not run, while the same module passed in the suite.

A per-file `sys.path.insert` fixes one module and has to be remembered by the next author.
A conftest fixes every module here at once and cannot be forgotten, which is the point:
this is the second time the same import gap has been filed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
