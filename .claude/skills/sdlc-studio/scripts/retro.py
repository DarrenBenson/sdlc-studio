#!/usr/bin/env python3
"""The deterministic retro spine: parse a retro, extract its lessons, and prove every
finding was dispositioned.

The retro was the only enforced ceremony with no script behind it. `gate.py` therefore
had nothing to interrogate but the filesystem - a glob for the filename - so an
empty file with the right name passed it. A gate is only as good as the thing it
can interrogate; this is that thing.

Everything here is mechanical, because everything here CAN be. Parsing a `## Lessons`
heading is parsing. Checking each finding is filed or declined is a set difference.
Judgement is reserved for what a lesson MEANS, never for whether the plumbing ran.

Subcommands:

  validate  content check - required sections, at least one real lesson, and every
            finding dispositioned. This is what the gate calls instead of a glob.
  extract   lift the `## Lessons` bullets into the project lessons log (`lessons add`),
            so a lesson written in a retro reaches the store that the next sprint reads.
  dispose   report every finding and its disposition; non-zero while any is undecided.
            The read-only half of `validate`, for a human deciding what to file.

The disposition rule. A finding is dispositioned when it is either filed as
an artefact (`CR0123` / `BG0045`) or DECLINED WITH A REASON. Declining is a first-class
answer and is equally green, so honesty costs exactly what noise costs and there is
nothing to game. What does not pass is silence: a finding written down and left to rot.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lessons  # noqa: E402  (sibling - the store a retro's lessons are extracted into)

RETRO_DIR = "sdlc-studio/retros"

# The sections a retro must carry. Absence is a structural failure, not a style note:
# each is a question the ceremony exists to ask, and a retro that skips one did not
# hold the ceremony.
REQUIRED_SECTIONS = (
    "Delivered",
    "What went well",
    "What was hard / what stalled",
    "Lessons",
    "Actions raised",
)

# `## Heading` -> body, to the next `##` of the same level.
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")

# A bullet that carries content. `{{placeholder}}` is a scaffold, not an answer - the
# template ships with them and a retro that still has them was never filled in.
BULLET_RE = re.compile(r"^\s*[-*]\s+(.*\S)\s*$")
PLACEHOLDER_RE = re.compile(r"\{\{.*?\}\}")

# A disposition is an artefact id, or an explicit decline carrying a reason.
#
# `LL` counts. Some findings are not tickets: the right outcome is a habit, and a habit's
# durable form is a recorded lesson. Refusing to accept one would push those findings toward a
# decline, which loses the lesson, or toward a make-work CR, which is the noise the decline path
# exists to prevent. It is no cheaper to game than declining, which is already free.
ARTEFACT_ID_RE = re.compile(r"\b((?:CR|BG|US|RFC|EP|LL)-?\d{4})\b", re.IGNORECASE)
DECLINED_RE = re.compile(r"^\s*declined\s*:\s*(.+\S)\s*$", re.IGNORECASE)

# A row in the `## Actions raised` table: | finding | disposition |
ROW_RE = re.compile(r"^\s*\|(?!\s*[-:]+\s*\|)([^|]+)\|([^|]+)\|\s*$")


def find_retro(root, retro_id: str) -> Path | None:
    """The retro file for an id. One glob, shared, so the gate and this script cannot
    disagree about which file they are talking about."""
    d = Path(root) / RETRO_DIR
    if not d.is_dir():
        return None
    hits = sorted(p for p in d.glob(f"{retro_id}*.md") if p.is_file())
    return hits[0] if hits else None


def sections(text: str) -> dict[str, list[str]]:
    """Map `## Heading` -> its body lines. Headings are matched on their exact text, so a
    renamed section reads as a MISSING section rather than silently passing - a retro
    that quietly dropped `Lessons` is the thing this is here to catch."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        m = SECTION_RE.match(line)
        if m:
            current = m.group(1).strip()
            out[current] = []
            continue
        if current is not None:
            out[current].append(line)
    return out


def _real_bullets(body: list[str]) -> list[str]:
    """Bullets with content in them. A `{{placeholder}}` bullet is the template talking,
    not the author, and counts as nothing."""
    found = []
    for line in body:
        m = BULLET_RE.match(line)
        if not m:
            continue
        text = m.group(1).strip()
        if not text or PLACEHOLDER_RE.search(text):
            continue
        # An HTML comment is template guidance, not an answer.
        text = re.sub(r"<!--.*?-->", "", text).strip()
        if text:
            found.append(text)
    return found


def lessons_in(text: str) -> list[str]:
    """The retro's lessons, as written. This is the input `extract` lifts into the store."""
    return _real_bullets(sections(text).get("Lessons", []))


def dispositions_in(text: str) -> list[dict]:
    """Every row of `## Actions raised`, with its disposition classified.

    Returns one dict per finding: {finding, raw, state, detail}, where state is
    'filed' (an artefact id), 'declined' (with a reason) or 'undecided' (anything
    else - blank, a placeholder, or a bare 'declined' with no reason).
    """
    rows = []
    for line in sections(text).get("Actions raised", []):
        m = ROW_RE.match(line)
        if not m:
            continue
        finding, disp = m.group(1).strip(), m.group(2).strip()
        # The template's own header row is not a finding.
        if finding.lower() in {"finding", "issue"} or not finding:
            continue
        state, detail = "undecided", ""
        if PLACEHOLDER_RE.search(disp) or not disp:
            state = "undecided"
        elif ARTEFACT_ID_RE.search(disp):
            state, detail = "filed", ARTEFACT_ID_RE.search(disp).group(1).upper()
        elif (d := DECLINED_RE.match(disp)) and not PLACEHOLDER_RE.search(d.group(1)):
            state, detail = "declined", d.group(1).strip()
        rows.append({"finding": finding, "raw": disp, "state": state, "detail": detail})
    return rows


def validate(root, retro_id: str) -> dict:
    """The content check the gate calls. Errors are blocking; each names its own remedy.

    This is deliberately NOT a glob. A 0-byte file called RETRO9999.md satisfied
    the old leg, so the one gate that made the retrospective un-skippable was the one an
    agent could satisfy with `touch`. Existence is not evidence.
    """
    path = find_retro(root, retro_id)
    if path is None:
        return {"ok": False, "id": retro_id, "path": None, "errors": [
            f"no retro file for {retro_id} in {RETRO_DIR}/ - write it before closing "
            f"the sprint (artifact.py new --type retro)"]}

    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    present = sections(text)
    for want in REQUIRED_SECTIONS:
        if want not in present:
            errors.append(
                f"missing section '## {want}' - a retro that skips it did not ask the "
                f"question the section exists to ask")

    if "Lessons" in present and not lessons_in(text):
        errors.append(
            "no lesson recorded - '## Lessons' is empty or still holds its "
            "{{placeholder}}. A sprint that taught nothing is a claim, not a default; "
            "if it truly taught nothing, say so in a bullet")

    rows = dispositions_in(text)
    if "Actions raised" in present and not rows:
        errors.append(
            "'## Actions raised' has no rows - answer the question: are there any CRs or "
            "Bugs to raise for the issues found? To say no, record a row declining it "
            "with a reason. Silence is not an answer")
    undecided = [r for r in rows if r["state"] == "undecided"]
    for r in undecided:
        errors.append(
            f"finding not dispositioned: {r['finding'][:60]!r} - file it (BG/CR id) or "
            f"decline it with a reason ('declined: <why>')")

    return {
        "ok": not errors,
        "id": retro_id,
        "path": str(path),
        "errors": errors,
        "lessons": lessons_in(text),
        "findings": rows,
        "filed": [r["detail"] for r in rows if r["state"] == "filed"],
        "declined": [r["finding"] for r in rows if r["state"] == "declined"],
    }


def cmd_validate(args) -> int:
    res = validate(args.root, args.id)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        if res["ok"]:
            n_l, n_f = len(res["lessons"]), len(res["findings"])
            print(f"retro {res['id']}: ok - {n_l} lesson(s), {n_f} finding(s) all dispositioned "
                  f"({len(res['filed'])} filed, {len(res['declined'])} declined)")
        else:
            print(f"retro {res['id']}: FAIL")
            for e in res["errors"]:
                print(f"  - {e}")
    return 0 if res["ok"] else 1


def cmd_dispose(args) -> int:
    """Read-only: what has been decided, and what still needs deciding."""
    res = validate(args.root, args.id)
    if res["path"] is None:
        print(f"retro {args.id}: not found", file=sys.stderr)
        return 1
    rows = res["findings"]
    if args.format == "json":
        print(json.dumps({"id": res["id"], "findings": rows}, indent=2))
        return 0 if all(r["state"] != "undecided" for r in rows) else 1
    if not rows:
        print(f"retro {res['id']}: no findings recorded under '## Actions raised'")
        return 1
    for r in rows:
        mark = {"filed": "filed   ", "declined": "declined", "undecided": "UNDECIDED"}[r["state"]]
        extra = f" -> {r['detail']}" if r["detail"] else ""
        print(f"  [{mark}] {r['finding'][:64]}{extra}")
    left = sum(1 for r in rows if r["state"] == "undecided")
    print(f"\n{len(rows)} finding(s), {left} undecided")
    if left:
        print("file each with scripts/file_finding.py, or decline it with a reason "
              "('declined: <why>') - both are green, silence is not")
    return 1 if left else 0


def cmd_extract(args) -> int:
    """Lift the retro's lessons into the project store, so a lesson written in a retro
    reaches the digest the next sprint plan prints. Without this the retro is a diary.

    Idempotent by content: a lesson already in the store is not added twice, so running
    extract on the same retro repeatedly converges rather than duplicating.
    """
    res = validate(args.root, args.id)
    if res["path"] is None:
        print(f"retro {args.id}: not found", file=sys.stderr)
        return 1
    found = res["lessons"]
    if not found:
        print(f"retro {args.id}: no lessons to extract")
        return 0

    log = lessons.default_project_file(args.root)
    existing_text = log.read_text(encoding="utf-8") if log.is_file() else lessons.PROJECT_HEADER
    existing = lessons.parse_project_lessons(existing_text)
    have = {e.get("title", "").strip().lower() for e in existing}

    added, skipped = [], []
    for text in found:
        if text.strip().lower() in have:
            skipped.append(text)
            continue
        added.append(text)

    if args.dry_run:
        for t in added:
            print(f"  + would add: {t[:70]}")
        for t in skipped:
            print(f"  = already recorded: {t[:70]}")
        print(f"\n{len(added)} to add, {len(skipped)} already present")
        return 0

    log.parent.mkdir(parents=True, exist_ok=True)
    for text in added:
        rc = lessons.cmd_add(argparse.Namespace(
            title=text, body=f"Recorded from retro {res['id']}.", root=args.root,
            tags="", origin=res["id"], epic=None, wave=None,
            validity_days=lessons.DEFAULT_VALIDITY_DAYS, global_=False,
            project_file=str(log), lessons_dir=None, format="text"))
        if rc != 0:
            print(f"failed to record: {text[:60]}", file=sys.stderr)
            return rc

    print(f"retro {res['id']}: {len(added)} lesson(s) extracted, {len(skipped)} already present")
    if added:
        print("regenerate the summary so the next sprint reads them: lessons.py summary")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name, fn, helptext in (
        ("validate", cmd_validate, "content check: sections, lessons, dispositions (the gate's leg)"),
        ("dispose", cmd_dispose, "report each finding and whether it is filed, declined or undecided"),
        ("extract", cmd_extract, "lift the retro's lessons into the project lessons log"),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--id", required=True, help="retro id, e.g. RETRO0022")
        p.add_argument("--format", choices=("text", "json"), default="text")
        if name == "extract":
            p.add_argument("--dry-run", action="store_true")
        p.set_defaults(func=fn)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
