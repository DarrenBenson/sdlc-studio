#!/usr/bin/env python3
"""Lift the audit run id out of `Raised-by` prose into a readable `Audit-run` field.

108 findings record the run that raised them inside a sentence, so counting a class across runs
meant a regex over free text where a field read will do. This moves the datum without inventing
one: the id is already written down, and only its location changes.

WHAT IS NOT DONE HERE, deliberately. The LENS is not derived. `detector-owed` groups by lens, the
prose carries none, and guessing 108 lenses from sentences written for another purpose would be
inventing evidence at scale - which is the class this project files bugs about. Each backfilled
finding records its lens as explicitly UNKNOWN, and `detector-owed` counts an unknown lens as
unattributable rather than as a lens named "unknown": five runs sharing one placeholder would
otherwise read as a detector owed on every one of them. Lens data starts with the next real run.

THE TWO RULES THE PROSE ALREADY SETTLES, so neither is a judgement call:

  Twelve findings name TWO ids, in the shape `adversarial audit <A> carry-over, run <B>`. `B` is
  the run that filed it and `A` is the earlier run it carried over from, which the sentence says
  outright. All twelve match that shape; none needs a choice made for it.

  The register rows this seeds are stamped `backfilled`, never `recorded`. These ids were minted by
  nothing this project runs - they are harness workflow ids lifted from prose - and laundering them
  into the same authority as a measured run would let a verdict rest on unverifiable strings.

Usage:
    python3 backfill_audit_runs.py plan   [--root DIR] [--format json]
    python3 backfill_audit_runs.py apply  [--root DIR] [--dry-run]
    python3 backfill_audit_runs.py check  [--root DIR]

`check` is the standing sweep and is the verb a guard runs: it exits non-zero when any finding
names a run in prose that its metadata field does not carry. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

#: Where findings live, with the id prefixes each directory may hold.
FINDING_DIRS = (("bugs", ("BG",)), ("change-requests", ("CR",)), ("rfcs", ("RFC",)))

#: The lens value a backfilled finding carries. `detector_owed` treats it as unattributable, so it
#: can never be mistaken for a real lens - five runs sharing one placeholder would otherwise read
#: as a detector owed on every one of them. Shared with that reader, never re-typed.
LENS_UNKNOWN = sdlc_md.LENS_UNKNOWN

_RUN_ID = re.compile(r"wf_[a-z0-9]+(?:-[a-z0-9]+)*", re.IGNORECASE)
#: `run <id>` names the run that FILED the finding.
_FILED_BY = re.compile(r"\brun\s+(wf_[a-z0-9]+(?:-[a-z0-9]+)*)", re.IGNORECASE)
#: `<id> carry-over` names an EARLIER run the finding was carried over from.
#: BOTH word orders, and case-folded. Measured over the 1438 `Raised-by` lines in this corpus:
#: 13 write `<id> carry-over` and NONE writes `carry-over from <id>` - so the second order is
#: defensive, not observed, and this comment previously claimed the opposite. The case-fold is
#: the half that was earning its place: an id in any other case simply did not match, and a
#: pattern that silently matches nothing is how the disambiguation quietly stopped happening.
_CARRIED = re.compile(
    r"(wf_[a-z0-9]+(?:-[a-z0-9]+)*)\s+carry-over|carry-over\s+(?:from\s+)?(wf_[a-z0-9]+(?:-[a-z0-9]+)*)",
    re.IGNORECASE)


class Ambiguous(ValueError):
    """A `Raised-by` line naming several run ids that the prose does not disambiguate.

    Raised rather than resolved by picking one: the whole value of this pass is that it moves a
    datum somebody already wrote, and a coin toss between two ids would be a fabricated one.
    """


def filing_run(raised_by: str) -> str | None:
    """The run that filed this finding, from its `Raised-by` line. None when it names none.

    With one id, that is the answer. With several, the prose settles it: `run <B>` is the filing
    run and `<A> carry-over` is the earlier one. Anything else raises rather than guessing.
    """
    ids = list(dict.fromkeys(_RUN_ID.findall(raised_by or "")))
    if not ids:
        return None
    if len(ids) == 1:
        return ids[0]
    # EVERY `run <id>`, not the first. Returning on the first match made the Ambiguous refusal
    # reachable only when NO `run <id>` appeared at all - so a line naming two filing runs was
    # resolved by document order, which is precisely the guess the refusal exists to prevent.
    filed_ids = list(dict.fromkeys(m.group(1) for m in _FILED_BY.finditer(raised_by)))
    carried_m = _CARRIED.search(raised_by)
    carried_id = (carried_m.group(1) or carried_m.group(2)) if carried_m else None
    # A carry-over id is not a filing candidate: naming it is what disambiguates the pair.
    candidates = [i for i in filed_ids if i != carried_id]
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        raise Ambiguous(
            f"names {len(candidates)} filing runs ({', '.join(candidates)}) and the prose does "
            f"not say which filed it - refusing to pick one by document order, because a guess "
            f"here is a fabricated provenance")
    raise Ambiguous(
        f"names {len(ids)} run ids ({', '.join(ids)}) and the prose does not say which filed it - "
        f"refusing to pick one, because a guess here is a fabricated provenance")


def scan(repo_root: Path | str) -> dict:
    """`{rows, ambiguous}`. A row per finding whose prose names a run.

    `rows` carry `{id, path, run, stamped}` - `stamped` is the run its metadata field already
    holds, so a second pass is a no-op rather than a rewrite.
    """
    root = Path(repo_root)
    rows, ambiguous = [], []
    for rel, prefixes in FINDING_DIRS:
        d = root / "sdlc-studio" / rel
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name == "_index.md":
                continue
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec or rec[:2] not in prefixes and rec[:3] not in prefixes:
                continue
            text = sdlc_md.read_text_safe(path)
            raised = sdlc_md.extract_field(text, "Raised-by") or ""
            try:
                run = filing_run(raised)
            except Ambiguous as exc:
                ambiguous.append({"id": rec, "path": str(path), "why": str(exc)})
                continue
            if not run:
                continue
            rows.append({"id": rec, "path": str(path), "run": run,
                         "stamped": (sdlc_md.extract_field(text, "Audit-run") or "").strip()})
    return {"rows": rows, "ambiguous": ambiguous}


def _insert_after(text: str, anchor_field: str, lines: str) -> str:
    """Put `lines` immediately after the `> **<anchor_field>:**` line, keeping the block together."""
    out = []
    placed = False
    for line in text.splitlines(keepends=True):
        out.append(line)
        if not placed and line.lstrip().startswith(f"> **{anchor_field}:**"):
            out.append(lines)
            placed = True
    if not placed:                      # no anchor: leave the file alone rather than guess a spot
        return text
    return "".join(out)


def apply(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Stamp `Audit-run` and `Audit-lens` on every finding whose prose names a run.

    Returns `{stamped, already, ambiguous, runs}`. Idempotent: a finding whose field already holds
    the right run is left untouched, so re-running changes nothing.
    """
    root = Path(repo_root)
    found = scan(root)
    stamped, already = [], []
    for row in found["rows"]:
        if row["stamped"] == row["run"]:
            already.append(row["id"])
            continue
        if dry_run:
            stamped.append(row["id"])
            continue
        path = Path(row["path"])
        text = path.read_text(encoding="utf-8")
        block = (f"> **Audit-lens:** {LENS_UNKNOWN}\n"
                 f"> **Audit-run:** {row['run']}\n")
        updated = _insert_after(text, "Raised-by", block)
        if updated == text:
            continue
        path.write_text(updated, encoding="utf-8")
        stamped.append(row["id"])
    runs = sorted({r["run"] for r in found["rows"]})
    if not dry_run and runs:
        _seed_register(root, runs)
    return {"stamped": stamped, "already": already,
            "ambiguous": found["ambiguous"], "runs": runs}


def _seed_register(repo_root: Path | str, runs: list) -> None:
    """Record each run in the register, stamped `backfilled`. Existing rows are left alone."""
    import audit_cost  # noqa: PLC0415 - local: this seeds the register, it does not own it
    held = audit_cost.register(repo_root)["runs"]
    for run in runs:
        if run in held:
            continue
        audit_cost.record(repo_root, {
            "run_id": run, "provenance": audit_cost.PROVENANCE_BACKFILLED,
            "notes": "seeded by backfill_audit_runs from findings' Raised-by prose - asserted, "
                     "never measured here"})


def check(repo_root: Path | str) -> list:
    """Every finding naming a run in prose that its metadata field does not carry."""
    found = scan(repo_root)
    errors = [f"{r['id']}: names run {r['run']} in prose but its Audit-run field holds "
              f"{r['stamped'] or 'nothing'}"
              for r in found["rows"] if r["stamped"] != r["run"]]
    errors += [f"{a['id']}: {a['why']}" for a in found["ambiguous"]]
    return errors


def build_parser() -> argparse.ArgumentParser:
    """The parser, as a module-level function so the surface can be enumerated without
    running the command. `lib/surface.py` walks every one of these; a parser built inside
    `main()` is invisible to it, which is a verb no coverage number can count."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, helptext in (("plan", "report the mapping without writing"),
                           ("apply", "stamp the fields and seed the register"),
                           ("check", "refuse when prose and field disagree")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--root", default=".")
        p.add_argument("--format", choices=("text", "json"), default="text")
        if name == "apply":
            p.add_argument("--dry-run", action="store_true")
    # Uniform family grammar: `--root` valid before OR after the verb, with the
    # per-subcommand copies re-pointed to SUPPRESS so a value given first is not
    # clobbered by a subparser default. Must run AFTER every subparser exists.
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # ANCHOR BEFORE DISPATCH. A bare `--root .` taken from the cwd means a run from a
    # subdirectory reads an empty tree, or writes into a stray one, and exits 0. The shared
    # resolver discovers the project the cwd sits below.
    args.root = str(sdlc_md.resolve_root(args))
    root = Path(args.root)

    if args.cmd == "check":
        errors = check(root)
        if args.format == "json":
            print(json.dumps({"errors": errors}, indent=2))
        else:
            for e in errors:
                print(f"BACKFILL: {e}", file=sys.stderr)
            if not errors:
                print("every finding that names a run in prose carries it as a field too.")
        return 1 if errors else 0

    if args.cmd == "plan":
        found = scan(root)
        owed = [r for r in found["rows"] if r["stamped"] != r["run"]]
        if args.format == "json":
            print(json.dumps(found, indent=2))
            return 0
        print(f"{len(found['rows'])} finding(s) name a run in prose; {len(owed)} need stamping.")
        for run in sorted({r["run"] for r in found["rows"]}):
            n = sum(1 for r in found["rows"] if r["run"] == run)
            print(f"  {run}: {n}")
        for a in found["ambiguous"]:
            print(f"  AMBIGUOUS {a['id']}: {a['why']}", file=sys.stderr)
        return 0

    res = apply(root, dry_run=args.dry_run)
    if args.format == "json":
        print(json.dumps(res, indent=2))
        return 0
    verb = "would stamp" if args.dry_run else "stamped"
    print(f"{verb} {len(res['stamped'])} finding(s); {len(res['already'])} already carried it; "
          f"{len(res['runs'])} run(s) in the register: {', '.join(res['runs'])}")
    for a in res["ambiguous"]:
        print(f"AMBIGUOUS {a['id']}: {a['why']}", file=sys.stderr)
    return 1 if res["ambiguous"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
