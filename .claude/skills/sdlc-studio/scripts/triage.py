#!/usr/bin/env python3
"""triage - decompose an Issue (a raw defect report) into the bugs that deliver its fix, wired.

An Issue sits in the DISCOVERY backlog: a symptom someone reported, not yet reproduced or scoped.
It becomes DELIVERY work only by being triaged into concrete, reproducible bugs - the units a
sprint plans and closes on executable acceptance. `triage` is that step made a command, the
defect-side mirror of `refine`: it validates the Issue is triageable, mints the bugs, and writes
the bidirectional `Parent:` / `Decomposed-into:` links the two-backlog gates verify - the wiring
an operator otherwise does by hand.

Where `refine` turns a request into an epic + stories (two levels), `triage` turns an Issue
DIRECTLY into bugs (one level): a bug is already the concrete delivery unit, so no container is
minted. An Issue that turns out to be a change rather than a defect is NOT triaged into a story
here (a story needs an epic parent); file a CR for it and `refine` that instead - `triage`
surfaces that option but keeps the defect path clean.

Atomicity mirrors `refine`: the whole breakdown is validated before anything is minted (a bad
point value mints nothing), and a failure mid-create rolls back the bugs already written, so
`triage` never half-decomposes an Issue.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    from lib import sdlc_md
except ImportError:  # invoked from inside scripts/
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib import sdlc_md

import artifact
import persona_resolve


# The status an Issue moves to once it is triaged and being delivered via its bugs. It reaches its
# TERMINAL status (Resolved) only by derivation (G2), when the bugs are all resolved - this is just
# the "now being worked" signal, the analogue of refine moving a CR to In Progress.
_WORKING_STATUS = "Triaged"


def parse_bug_spec(spec: str) -> tuple[str, int, str, str | None]:
    """A `--bug` value: `title|points|severity` or `title|points|severity|affects`. Returns
    (title, points, severity, affects|None). Points are validated against the Fibonacci scale
    here, before anything is minted, so a bad breakdown fails loud and empty. Severity defaults to
    Medium when the field is blank (an empty `title|3|` third cell)."""
    parts = [p.strip() for p in spec.split("|")]
    if len(parts) < 2 or not parts[0]:
        raise ValueError(f"bug spec {spec!r} must be 'title|points' "
                         "(optional '|severity', '|severity|affects')")
    title = parts[0]
    points = sdlc_md.check_points(parts[1])          # raises on an off-scale value
    severity = (parts[2].strip() if len(parts) > 2 and parts[2].strip() else "Medium")
    affects = parts[3] if len(parts) > 3 and parts[3] else None
    return title, points, severity, affects


def triageable(repo_root: Path | str, issue_id: str) -> dict:
    """Validate that `issue_id` can be triaged and gather what an operator needs to propose the
    bugs: its title, report, and severity. Raises the refusals `triage` enforces (non-issue,
    already-triaged), so `show` and `apply` agree on what triageable means - an Issue that `show`
    accepts is one `apply` will."""
    root = Path(repo_root)
    hit = sdlc_md.find_by_id(root, issue_id)
    if not hit:
        raise ValueError(f"no artefact found for id {issue_id!r}")
    ipath, itype = hit
    if itype != "issue":
        raise ValueError(f"triage takes an ISSUE; {issue_id} is a {itype}. "
                         f"(A request (RFC/CR) is refined, not triaged - use refine.py.)")
    text = ipath.read_text(encoding="utf-8")
    existing = sdlc_md.decomposed_ids(text)
    if existing:
        raise ValueError(f"{issue_id} is already triaged into {', '.join(existing)}.")
    return {"id": sdlc_md.extract_record_id(ipath.stem) or issue_id, "type": itype,
            "title": sdlc_md.extract_h1_title(text) or "",
            "severity": sdlc_md.extract_field(text, "Severity") or "-",
            "report": _section(text, "Report") or _section(text, "Summary"),
            "observed": _section(text, "Observed")}


def _section(text: str, heading: str) -> str:
    """The body under a `## Heading`, trimmed, or '' - so `show` can surface an Issue's Report and
    Observed sections without the reader opening the file."""
    out: list[str] = []
    grabbing = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            if grabbing:
                break
            grabbing = ln[3:].strip().lower() == heading.lower()
            continue
        if grabbing:
            out.append(ln)
    return "\n".join(out).strip()


def _decompose(root: Path, iid: str, ipath: Path,
               bugs: list[tuple[str, int, str, str | None]]) -> list[str]:
    """Mint the bugs and wire each under ONE rollback guard, then set the Issue's
    `Decomposed-into:` to them. A single atomic mint, so a mid-create failure leaves the backlog
    untouched. Returns the bug ids."""
    minted: list[Path] = []
    try:
        bug_ids: list[str] = []
        for title, points, severity, affects in bugs:
            fields = {"points": points, "severity": severity}
            if affects:
                fields["affects"] = affects
            # consolidate=False: a triaged bug is a deliberate decomposition unit, not agent
            # finding-noise, so it mints an individual bug regardless of severity. Without this a
            # Low-severity bug would be folded into a consolidation CR on a v3 project, and the
            # wiring below would then mis-parent that CR to the Issue.
            b = artifact.new(root, "bug", title, fields, consolidate=False)
            if b.get("consolidated") or not b.get("path") \
                    or not sdlc_md.norm_id(b.get("id") or "").startswith("BG"):
                # defence in depth: if a mint ever returns something other than an individual bug,
                # fail loud (and roll back) rather than wire a non-bug as the Issue's child.
                raise ValueError(f"triage expected an individual bug for {title!r}, got {b!r}")
            minted.append(Path(b["path"]))
            bug_ids.append(b["id"])
            sdlc_md.insert_after_status(Path(b["path"]), f"> **{sdlc_md.PARENT_FIELD}:** {iid}")
        sdlc_md.write_decomposed(ipath, bug_ids)
    except BaseException:
        for p in minted:
            try:
                p.unlink()
            except OSError:
                pass
        raise
    return bug_ids


def triage(repo_root: Path | str, issue_id: str,
           bugs: list[tuple[str, int, str, str | None]],
           questions: list[str] | None = None, dry_run: bool = False,
           skip_personas: bool = False) -> dict:
    """Triage `issue_id` into `bugs` (title, points, severity, affects?). Writes the bidirectional
    links and moves the Issue to its working state.

    Validates ALL INPUT before minting anything - the Issue must resolve, be an issue and not
    already triaged; every bug's points must be on the scale (parsed already); every title must be
    a single line the creator will accept. Only after that does it mint, and if a create fails
    part-way it ROLLS BACK the bugs it wrote. So a bad breakdown, or a failure mid-mint, leaves the
    backlog untouched - triage never half-decomposes an Issue."""
    root = Path(repo_root)
    triageable(root, issue_id)   # SHARED validation: non-issue / already-triaged refusals
    ipath, _ = sdlc_md.find_by_id(root, issue_id)
    if not bugs:
        raise ValueError("triage needs at least one --bug: an empty triage delivers nothing, "
                         "which is exactly what the UNDECOMPOSED check flags. If the Issue is not "
                         "a real defect, close it as Won't Fix rather than triaging it to nothing.")
    for title, _, _, _ in bugs:
        sdlc_md.require_single_line("bug title", title)
    if sdlc_md.extract_field(ipath.read_text(encoding="utf-8"), "Status") is None:
        raise ValueError(f"{issue_id} has no `> **Status:**` line - cannot wire its "
                         f"`Decomposed-into:` link; fix the Issue first.")
    # Pre-flight EVERY bug through a dry-run mint before minting any. Grooming (a resolvable
    # Affects, Points on the scale) is enforced INSIDE artifact.new per-bug, so without this a
    # later bug failing grooming would leave an earlier bug's file AND index row behind - the
    # rollback in `_decompose` unlinks minted files, but an index row is appended as each file is
    # written and is not unwound. The dry-run runs the same grooming/field guards and writes
    # nothing, so a bad breakdown fails loud and empty here, before anything is minted (refine's
    # up-front-validation discipline, applied to the check that runs per-artefact rather than once).
    for title, points, severity, affects in bugs:
        bf = {"points": points, "severity": severity}
        if affects:
            bf["affects"] = affects
        # consolidate=False so the preflight faithfully mirrors the real mint (see _decompose):
        # otherwise a Low-severity bug's dry-run would report a consolidation, diverging from the
        # individual bug the real mint now produces.
        artifact.new(root, "bug", title, bf, dry_run=True, consolidate=False)
    iid = sdlc_md.extract_record_id(ipath.stem) or issue_id
    total = sum(p for _, p, _, _ in bugs)
    open_questions = [q for q in (questions or []) if q.strip()]
    # Resolve the Three-Amigos panel UP FRONT (read-only), QA-LED: a triage is where "is this
    # reproducible? what is the real defect?" get answered BY the seats, so a broken project seat
    # card fails before anything is minted (triage's fail-empty discipline). `--skip-personas`
    # bypasses resolution entirely (byte-equivalent, no framing).
    amigo_consult = persona_resolve.consult(root, persona_resolve.TRIAGE_PANEL, open_questions,
                                            skip_personas=skip_personas)
    if dry_run:
        return {"issue": iid, "bugs": [t for t, _, _, _ in bugs], "points": total,
                "open_questions": open_questions, "consult": amigo_consult, "dry_run": True}

    bug_ids = _decompose(root, iid, ipath, bugs)
    # close the loop on the Issue's status: it is now being DELIVERED via its bugs, so it moves to
    # Triaged (it reaches Resolved only by derivation, G2). Best-effort - if a gate we do not force
    # past declines the move, the triage still stands.
    moved_to = None
    vocab = sdlc_md.status_vocab("issue", root)
    cur = sdlc_md.canonical_status(
        sdlc_md.extract_field(ipath.read_text(encoding="utf-8"), "Status"), vocab)
    if cur != _WORKING_STATUS and not sdlc_md.is_terminal_status("issue", cur or ""):
        import transition   # local import: transition pulls critic/plan_review; keep off load
        try:
            transition.transition(root, iid, _WORKING_STATUS)
            moved_to = _WORKING_STATUS
        except (ValueError, FileNotFoundError):
            pass
    # Record the consult on the Issue itself (audit trail): which seats were consulted and the open
    # questions. Best-effort - the triage stands even if the record write fails.
    if amigo_consult.get("questions"):
        try:
            persona_resolve.record_consult(ipath, amigo_consult, date.today().isoformat())
        except (OSError, ValueError):
            pass
    return {"issue": iid, "bugs": bug_ids, "points": total, "status": moved_to,
            "open_questions": open_questions, "consult": amigo_consult,
            "dry_run": False}


def cmd_show(args: argparse.Namespace) -> int:
    try:
        info = triageable(args.root, args.issue)
    except (ValueError, FileNotFoundError) as exc:
        print(f"not triageable: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(info, indent=2))
        return 0
    print(f"{info['id']} (issue, severity {info['severity']}): {info['title']}\n")
    if info["report"]:
        print(f"Report:\n{info['report']}\n")
    if info["observed"]:
        print(f"Observed:\n{info['observed']}\n")
    print("Propose the bugs, then:\n"
          f"  triage apply --issue {info['id']} "
          "--bug \"title|points|severity\" --bug \"title|points|severity|affects\" ...\n"
          "If it is really a change, not a defect: file a CR and refine that instead.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    try:
        bugs = [parse_bug_spec(b) for b in (args.bug or [])]
        result = triage(args.root, args.issue, bugs, questions=args.question, dry_run=args.dry_run,
                        skip_personas=getattr(args, "skip_personas", False))
    except (ValueError, FileNotFoundError, persona_resolve.RenderError) as exc:
        print(f"triage refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    verb = "would triage" if result["dry_run"] else "triaged"
    print(f"{verb} {result['issue']} -> {len(result['bugs'])} bug(s) "
          f"({result['points']} pts): {', '.join(result['bugs'])}")
    if result.get("status"):
        print(f"  {result['issue']} moved to {result['status']} - it reaches Resolved only by "
              f"derivation, when its bugs are all resolved")
    if result.get("open_questions"):
        consult = result.get("consult") or {}
        panel = ", ".join(f"{p['seat']} ({p['role']})" for p in consult.get("panel", []))
        lead = consult.get("lead")
        lead_note = f"{lead} leads; " if lead else ""
        print(f"  {len(result['open_questions'])} open question(s) for the Three-Amigos consult "
              f"({lead_note}{panel}) - settle before building:")
        for q in result["open_questions"]:
            print(f"    - {q}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="triage", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="Decompose an Issue into bugs, links wired")
    a.add_argument("--issue", required=True, help="the Issue to triage")
    a.add_argument("--bug", action="append", metavar="TITLE|POINTS[|SEVERITY[|AFFECTS]]",
                   help="a bug in the triage: 'title|points', '|severity', '|severity|affects'. "
                        "Repeatable. Points must be on the Fibonacci scale.")
    a.add_argument("--question", action="append", metavar="TEXT",
                   help="an open question for the Three-Amigos consult, surfaced at apply time and "
                        "directed at the resolved seats (QA-led). Repeatable.")
    a.add_argument("--skip-personas", action="store_true",
                   help="force the generic path: resolve no amigo seats, no framing (byte-equivalent)")
    a.add_argument("--dry-run", action="store_true", help="validate and report; mint nothing")
    a.add_argument("--root", default=".")
    sdlc_md.add_format_arg(a)
    a.set_defaults(func=cmd_apply)

    s = sub.add_parser("show", help="Show an Issue's report to inform the triage, and confirm it "
                                    "is triageable")
    s.add_argument("--issue", required=True, help="the Issue to inspect")
    s.add_argument("--root", default=".")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)

    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
