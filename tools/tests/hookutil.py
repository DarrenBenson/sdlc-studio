"""Shared reader for what the commit hooks actually invoke.

Four separate test files each carried their own copy of the hook's tool list, and adding one
lane turned 41 tests red for a reason none of them was about. One reader, derived from the
hook, so a lane added to the gate reaches every fixture at once.
"""
from __future__ import annotations

import re
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / ".githooks"


def hook_tool_scripts(*hooks: str) -> list[str]:
    """Every `tools/*.py` the named hooks invoke (default: both), as bare filenames.

    Reads the INVOCATION form (`-- python3 tools/x.py`) only, so example prose in a hook's
    comments does not enter a fixture as an imaginary lane.
    """
    names: set = set()
    for hook in (hooks or ("pre-commit", "commit-msg")):
        path = HOOKS / hook
        if not path.is_file():
            continue
        names.update(re.findall(r"--\s+python3\s+tools/([A-Za-z0-9_]+\.py)",
                                path.read_text(encoding="utf-8")))
    return sorted(names)
