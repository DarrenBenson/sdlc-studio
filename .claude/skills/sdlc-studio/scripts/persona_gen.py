#!/usr/bin/env python3
"""Deterministic floor of team/stakeholder persona generation.

The generation itself is model-driven (reference-persona-generate.md, the
Analyse -> Present -> Ask -> Generate flow); this helper owns the mechanical parts the
flow must not improvise:

    stamp    mark a just-generated card `generated (provisional - unverified)` with a
             content hash, so authored and generated cards are mechanically distinguishable
    classify report a card's provenance class: authored / generated-pristine /
             generated-edited (stamp present but content hash mismatch - an operator
             edited it, so never-clobber now treats it as authored)
    accept   clear the provisional label on generated cards (the flow's batch-accept
             close for TEAM seats, and `persona review`'s accept path) - the stamp is
             replaced with a dated `reviewed` marker, the hash retired

The stamp is an HTML comment beside the `<!-- role: ... -->` idiom seat cards already
carry - deliberately NOT the `> **Provenance:**` artefact field, which is a
verify_ac shell-gate control with different semantics. Hashing excludes the stamp
line itself, so re-stamping is stable. Pure stdlib.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# The machine-readable generation stamp. Example:
#   <!-- provenance: generated provisional-unverified hash=sha256:ab12... -->
STAMP_RE = re.compile(
    r"<!--\s*provenance:\s*generated\s+provisional-unverified\s+hash=sha256:([0-9a-f]{16})\s*-->")
REVIEWED_RE = re.compile(r"<!--\s*provenance:\s*reviewed\s+(\d{4}-\d{2}-\d{2})\s*-->")


def _body_hash(text: str) -> str:
    """Short content hash of a card EXCLUDING any provenance stamp line (stable across
    stamp/re-stamp; whitespace-normalised at line ends only)."""
    lines = [ln for ln in text.splitlines()
             if not STAMP_RE.search(ln) and not REVIEWED_RE.search(ln)]
    canon = "\n".join(ln.rstrip() for ln in lines)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def classify(path: Path | str) -> str:
    """'authored' (no generation stamp), 'generated-pristine' (stamp present, hash
    matches), or 'generated-edited' (stamp present, hash differs - the operator edited a
    generated card; never-clobber treats it as authored from here on)."""
    text = Path(path).read_text(encoding="utf-8")
    m = STAMP_RE.search(text)
    if not m:
        return "authored"
    return "generated-pristine" if m.group(1) == _body_hash(text) else "generated-edited"


def stamp(path: Path | str) -> str:
    """Mark a just-generated card provisional-unverified with its content hash. Replaces
    an existing stamp (re-stamp after regeneration); refuses to stamp over a `reviewed`
    marker - an accepted card that gets regenerated must first lose its acceptance
    deliberately. Returns the class after stamping."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if REVIEWED_RE.search(text):
        raise ValueError(f"{p} carries a reviewed marker - it is an accepted card; "
                         "remove the marker deliberately before regenerating over it")
    text = "\n".join(ln for ln in text.splitlines() if not STAMP_RE.search(ln))
    line = f"<!-- provenance: generated provisional-unverified hash=sha256:{_body_hash(text)} -->"
    # place beside the role comment when present, else at the top
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if "<!-- role:" in ln:
            lines.insert(i + 1, line)
            break
    else:
        lines.insert(0, line)
    sdlc_md.atomic_write(p, "\n".join(lines) + ("\n" if text.endswith("\n") else "\n"))
    return classify(p)


def accept(path: Path | str, today: str | None = None) -> bool:
    """Clear a generated card's provisional label (batch-accept / persona review): the
    stamp becomes a dated `reviewed` marker. True when a label was cleared; False when
    the card was not provisional (authored or already reviewed) - never an error, so a
    batch accept over a mixed directory is safe."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if not STAMP_RE.search(text):
        return False
    marker = f"<!-- provenance: reviewed {today or sdlc_md.now_date()} -->"
    text = STAMP_RE.sub(marker, text, count=1)
    sdlc_md.atomic_write(p, text)
    return True


def provisional_seats(root: Path | str) -> list[str]:
    """Filenames of seat/stakeholder cards still carrying the provisional stamp - the
    status advisory reads this (a label nobody surfaces is a label nobody clears)."""
    out: list[str] = []
    for sub in ("seats", "stakeholders"):
        d = Path(root) / "sdlc-studio" / "personas" / sub
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            if STAMP_RE.search(p.read_text(encoding="utf-8")):
                out.append(f"{sub}/{p.name}")
    return out


def _paths(args: argparse.Namespace) -> list[Path]:
    if args.file:
        return [Path(args.file)]
    root = Path(args.root)
    out = []
    for sub in ("seats", "stakeholders"):
        d = root / "sdlc-studio" / "personas" / sub
        if d.is_dir():
            out.extend(sorted(d.glob("*.md")))
    return out


def cmd_stamp(args: argparse.Namespace) -> int:
    try:
        cls = stamp(args.file)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"stamped {args.file}: {cls}")
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    rows = {str(p): classify(p) for p in _paths(args)}
    if getattr(args, "format", "text") == "json":
        print(json.dumps(rows, indent=2))
    else:
        for k, v in rows.items():
            print(f"{v:20} {k}")
    return 0


def cmd_accept(args: argparse.Namespace) -> int:
    cleared = [str(p) for p in _paths(args) if accept(p)]
    print(f"accepted {len(cleared)} card(s)" + (f": {', '.join(cleared)}" if cleared else ""))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Deterministic floor of persona generation.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stamp", help="Mark a just-generated card provisional with its content hash.")
    s.add_argument("--file", required=True)
    s.set_defaults(func=cmd_stamp)
    c = sub.add_parser("classify", help="authored / generated-pristine / generated-edited per card.")
    c.add_argument("--file")
    c.add_argument("--root", default=".")
    sdlc_md.add_format_arg(c)
    c.set_defaults(func=cmd_classify)
    a = sub.add_parser("accept", help="Clear provisional labels (batch-accept / persona review).")
    a.add_argument("--file")
    a.add_argument("--root", default=".")
    a.set_defaults(func=cmd_accept)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
