#!/usr/bin/env python3
"""Every boundary AGENTS.md names has a hook invocation behind it.

AGENTS.md says two lanes bind "at the push and release boundaries" and spells the boundaries as
`gate.py --boundary push|release`. For a whole release cycle nothing invoked either: there was no
`.githooks/pre-push`, and the release boundary had no caller at all. A boundary documented into a
hook nobody wrote is the rule-with-no-gate shape AGENTS.md itself names as the weakest fix, so this
reads the roster from the document and demands an INVOCATION for each name it finds.

    python3 tools/boundary_roster.py            # this tree: exit 1 naming any unbound boundary
    python3 tools/boundary_roster.py --agents F --hooks D   # a fixture roster and hooks directory

Reads INVOCATION lines only, never comments, in both spellings the gate accepts (`--boundary <b>`
and `SDLC_GATE_BOUNDARY=<b>`). A roster that parses to NO boundary is refused as unreadable rather
than passed as empty: "nothing to check" and "checked nothing" must never read the same.
Repo-only tooling, pure stdlib.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROSTER = re.compile(r"gate\.py --boundary ([a-z][a-z|]*)")
FLAG = re.compile(r"gate\.py\b[^#\n]*--boundary\s+([a-z]+)")
ENV = re.compile(r"SDLC_GATE_BOUNDARY=([a-z]+)[^#\n]*gate\.py")


def roster_boundaries(text: str) -> set[str]:
    """The boundary names the roster spells, `push|release` split on the bar."""
    out: set[str] = set()
    for m in ROSTER.finditer(text):
        out.update(p for p in m.group(1).split("|") if p)
    return out


def bound_boundaries(hooks_dir: Path) -> set[str]:
    """The boundaries some hook INVOKES the gate at - invocation lines only, never comments."""
    out: set[str] = set()
    for hook in sorted(p for p in hooks_dir.iterdir() if p.is_file()):
        for line in hook.read_text(encoding="utf-8", errors="replace").splitlines():
            code = line.split("#", 1)[0]
            for rx in (FLAG, ENV):
                m = rx.search(code)
                if m:
                    out.add(m.group(1))
    return out


def check(agents_md: Path, hooks_dir: Path) -> tuple[set[str], set[str], list[str]]:
    """`(read, bound, missing)`; `missing` carries the refusal lines, empty means the roster holds."""
    read = roster_boundaries(agents_md.read_text(encoding="utf-8"))
    if not read:
        return read, set(), [f"{agents_md} names no boundary in the shape `gate.py --boundary a|b` - "
                             "a roster read as empty is REFUSED, not passed"]
    bound = bound_boundaries(hooks_dir)
    missing = [f"boundary `{b}` is named in {agents_md.name} and no hook under {hooks_dir} invokes "
               f"`gate.py --boundary {b}` (or `SDLC_GATE_BOUNDARY={b}`)" for b in sorted(read - bound)]
    return read, bound, missing


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--agents", default=str(REPO / "AGENTS.md"))
    p.add_argument("--hooks", default=str(REPO / ".githooks"))
    args = p.parse_args(argv)
    read, bound, missing = check(Path(args.agents), Path(args.hooks))
    print(f"boundary-roster: read {', '.join(sorted(read)) or 'nothing'} from {Path(args.agents).name}; "
          f"bound by a hook: {', '.join(sorted(bound)) or 'nothing'}")
    for line in missing:
        print(f"boundary-roster: REFUSED - {line}", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
