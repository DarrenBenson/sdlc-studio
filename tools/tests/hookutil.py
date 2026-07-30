"""Shared reader for what the commit hooks actually invoke.

Four separate test files each carried their own copy of the hook's tool list, and adding one
lane turned 41 tests red for a reason none of them was about. One reader, derived from the
hook, so a lane added to the gate reaches every fixture at once.
"""
from __future__ import annotations

import re
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / ".githooks"


def hook_skill_scripts(*hooks: str) -> list[str]:
    """Every `.claude/skills/.../scripts/*.py` the named hooks invoke, as repo-relative paths.

    A lane may invoke a SKILL script rather than a `tools/` checker - the verify-ratchet lane
    does - and a fixture that stubs only `tools/` leaves that lane running the real script
    against a fixture workspace. One reader for each shape, both derived from the hook.

    Both spellings of the path are read: written out in full, and through the hook's own
    `$skill` variable. A lane using the variable was invisible here, so the promise above - one
    reader, so a lane added to the gate reaches every fixture at once - held only for lanes that
    happened to spell it the long way, and the two that did not were hand-listed in one fixture.
    """
    names: set = set()
    for hook in (hooks or ("pre-commit", "commit-msg")):
        path = HOOKS / hook
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        names.update(re.findall(r"--\s+python3\s+(\.claude/skills/[A-Za-z0-9_./-]+\.py)", text))
        # `skill=".claude/skills/sdlc-studio/scripts"` then `-- python3 "$skill/x.py"`. Read the
        # assignment from the hook rather than assuming the path.
        var = re.search(r'^skill="([^"]+)"', text, re.M)
        if var:
            names.update(f"{var.group(1)}/{n}" for n in
                         re.findall(r'--\s+python3\s+"\$skill/([A-Za-z0-9_./-]+\.py)"', text))
    return sorted(names)


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


def seed_verify_baseline(root) -> None:
    """Write an EMPTY verify-lint baseline into a fixture workspace.

    The verify-ratchet lane refuses an unrecorded tolerated set, by design - an absent baseline
    means nothing can be held to it. A fixture workspace has no duplicate groups, so the honest
    baseline is an empty one, and writing it here keeps every hook fixture consistent instead of
    four copies deciding separately."""
    import json
    from pathlib import Path as _P
    dest = _P(root) / "sdlc-studio" / ".verify-lint-baseline.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        dest.write_text(json.dumps({"groups": {}}) + "\n", encoding="utf-8")
