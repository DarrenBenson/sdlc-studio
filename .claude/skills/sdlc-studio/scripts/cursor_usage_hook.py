#!/usr/bin/env python3
"""The Cursor CLI's `afterAgentResponse` hook: appends each response's token usage to the ledger
the Cursor token reader (`lib/meter_cursor.py`) reads a Cursor CLI run's tokens from.

The CLI pipes the hook a JSON payload on stdin, and its 2026.10.22-27dcf5f build sets
`input_tokens`, `output_tokens`, `cache_read_tokens` and `cache_write_tokens` on it. For each
payload that is a JSON object, one line is appended to `meter_cursor.LEDGER_REL` under the
workspace root (`--root` verbatim, else the workspace `sdlc_md.resolve_root` discovers at or
above the working directory, which is the working directory itself when none is found): the
time, the event, the conversation and generation ids and the model, each a string of at most
`MAX_TEXT` characters or null, and the four counts, each a number as the payload gave it or null. The response's text is not written.
The reader, not the hook, judges each count: a line it cannot read is skipped and counted there.

Nothing is appended when the payload is not a JSON object, or when the root holds no
`sdlc-studio/` directory, or when the ledger cannot be written, and the hook then says why on
stderr. Whatever the payload, it exits 0 and prints nothing on stdout.

Usage, as the `afterAgentResponse` entry of the project's `.cursor/hooks.json`:
    python3 .claude/skills/sdlc-studio/scripts/cursor_usage_hook.py
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import meter_cursor, sdlc_md  # noqa: E402

#: The longest id or model name a line keeps; a longer one is cut to it.
MAX_TEXT = 200
#: The payload's strings each line keeps beside the counts.
KEPT = ("conversation_id", "generation_id", "model")


def ledger_line(payload: dict) -> str:
    """The ledger line for one `afterAgentResponse` payload, newline included."""
    def text(value):
        return value[:MAX_TEXT] if isinstance(value, str) else None

    def number(value):
        return value if isinstance(value, (int, float)) else None
    row = {"at": sdlc_md.now_iso8601(), "event": meter_cursor.HOOK_EVENT,
           **{k: text(payload.get(k)) for k in KEPT},
           **{f: number(payload.get(f)) for f in meter_cursor.LEDGER_FIELDS}}
    return json.dumps(row, sort_keys=True) + "\n"


def append(root: Path, raw: bytes) -> str | None:
    """Append the line for the payload `raw` to `root`'s ledger. None once it is written, else
    the reason nothing was."""
    try:
        payload = json.loads(raw)
    except ValueError:
        payload = None
    if not isinstance(payload, dict):
        return "the payload on stdin is not a JSON object, so no line is appended"
    if not (root / "sdlc-studio").is_dir():
        return f"{root} holds no sdlc-studio/ directory, so no ledger is kept there"
    ledger = meter_cursor.ledger_path(root)
    try:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(ledger, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, ledger_line(payload).encode("utf-8"))
        finally:
            os.close(fd)
    except OSError as exc:
        return f"the ledger {ledger} could not be written ({type(exc).__name__})"
    return None


def build_parser() -> argparse.ArgumentParser:
    """The hook's command line: `--root` alone."""
    parser = argparse.ArgumentParser(description=(
        "Append the token usage of the afterAgentResponse payload on stdin to the workspace's "
        "Cursor usage ledger."))
    # A string, not a `Path`: `sdlc_md.resolve_root` reads the family default `.` as "discover
    # it", and `Path(".")` would compare unequal to it and be honoured as a named root.
    parser.add_argument("--root", default=".",
                        help="the workspace root (default: the workspace discovered at or above "
                             "the working directory)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Anchored before the payload is read: a hook fired from a subdirectory of the workspace
    # writes the ledger at the workspace root, where the meter reads it.
    args.root = sdlc_md.resolve_root(args)
    why = append(args.root, sys.stdin.buffer.read())
    if why:
        print(f"cursor_usage_hook: {why}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
