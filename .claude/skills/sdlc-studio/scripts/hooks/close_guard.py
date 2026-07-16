#!/usr/bin/env python3
"""A Claude Code **Stop hook** that reminds the agent of an owed sprint close before a turn ends.

Wire it into a project's `.claude/settings.json` under `hooks.Stop` (see below). On every turn end
it asks the deterministic detector "is a sprint close owed right now?" - a delivery unit that reached
terminal since the close-owed baseline with no retro accounting for it - and if so, it BLOCKS the stop
once, feeding the reminder back to the model so the close-down is surfaced at the exact moment the
agent would otherwise walk away from it. This is the harness enforcing the Definition of Done's close
clause, not the agent's recall: the same reasoning that put the quality gate in a pre-commit hook
rather than a checklist. Opt-in - a project that finds a per-turn reminder too eager simply does not
wire it, and `gate --require-close` still guards the push/release moment.

It never HARD-locks. It surfaces the obligation and lets the agent act (run the retro) or continue;
loop prevention keeps it from re-blocking a turn it already blocked. Default-allow on any doubt: a
malformed stdin, an unbaselined project, or a detector error all exit 0 (allow), because a hook that
blocks a turn on its own bug is worse than a missed reminder.

settings.json (consuming project):

    {
      "hooks": {
        "Stop": [
          { "hooks": [
              { "type": "command",
                "command": "python3 .claude/skills/sdlc-studio/scripts/hooks/close_guard.py" }
          ] }
        ]
      }
    }

Contract (Claude Code Stop hook): reads a JSON event on stdin; to block, prints
`{"decision": "block", "reason": "..."}` on stdout and exits 0; to allow, exits 0 with no decision.
Pure stdlib.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# The hook lives at scripts/hooks/close_guard.py; the detector is its parent (scripts/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _read_event() -> dict:
    """Parse the Stop event from stdin, tolerating an empty or malformed payload (-> {})."""
    try:
        raw = sys.stdin.read()
    except Exception:  # noqa: BLE001 - no stdin is not a reason to block a turn
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _root_from(event: dict) -> Path:
    """Where the project is: the event's cwd if present, else the process cwd."""
    cwd = event.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and cwd else Path(os.getcwd())


def decide(event: dict) -> dict | None:
    """The reminder decision, or None to allow the stop. A dict is a `{"decision": "block", ...}`
    payload. Kept pure (no I/O) so it is trivially testable."""
    # Loop prevention: if the field is exposed and set, this stop is already the continuation of a
    # prior block - do not block again. When it is absent, Claude Code's internal loop resolution
    # handles it, so a single once-per-turn block is safe.
    if event.get("stop_hook_active"):
        return None
    root = _root_from(event)
    try:
        import close_owed
        report = close_owed.owed(root)
    except Exception:  # noqa: BLE001 - a detector error must never block a turn
        return None
    if not report.get("baselined") or not report.get("owed"):
        return None
    ids = [cid for cid, _ in report["owed"]]
    shown = ", ".join(ids[:8]) + (f", +{len(ids) - 8} more" if len(ids) > 8 else "")
    reason = (
        f"A sprint close is owed before this turn ends: {len(ids)} delivery unit(s) reached a "
        f"terminal state with no retro accounting for them ({shown}). This is the Definition of "
        f"Done's close clause - a sprint is complete only when the close gate is green, never at "
        f"'deployed'. Write the batch retro (retro.py), extract its lessons, then run "
        f"`gate --require-retro RETROxxxx` and show it green. If a close is genuinely not owed here "
        f"(e.g. these predate adoption), run `close_owed.py baseline` to record that once."
    )
    return {"decision": "block", "reason": reason}


def main() -> int:
    decision = decide(_read_event())
    if decision is not None:
        print(json.dumps(decision))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
