#!/usr/bin/env python3
"""refine - decompose a request (RFC/CR) into an epic and stories, with the links wired.

A request sits in the DISCOVERY backlog; it becomes DELIVERY work only by being broken down into
the units that deliver it. `refine` is that step made a command: it validates the request is
refinable, creates an epic and its stories, and writes the bidirectional `Parent:` /
`Decomposed-into:` links the two-backlog gates verify - the wiring an operator otherwise does by
hand. It is also the migration tool: refining an old childless CR into stories is exactly what an
upgrading project must do.

This module is the DETERMINISTIC CORE (US0129): given the request, an epic title and the story
breakdown (title + points), it creates and wires everything atomically-enough (it validates the
whole breakdown before minting anything, so a bad point value mints nothing). Proposing a GOOD
breakdown is a judgement the agent/operator makes and passes in; refine does not invent it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from lib import sdlc_md
except ImportError:  # invoked from inside scripts/
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib import sdlc_md

import artifact


# The T-shirt Size an epic is born with, from the story-point total it decomposes into. A coarse
# read-off, never a measurement: the epic's real size is its `Derived Point Total`, which reconcile
# keeps equal to the sum of its stories' points. The band edges mirror the Fibonacci scale.
def _tshirt_for(total: int) -> str:
    return sdlc_md.size_for_points(total)   # the ONE point->size band (shared with the migration)


def _insert_after_status(path: Path, line: str) -> None:
    """Insert a `> **Field:** value` metadata line immediately after the `> **Status:**` line -
    the one field every artefact carries, so the insertion point is universal. Raises if the file
    has no Status line: writing nothing there would leave a ONE-SIDED link (a link the two-backlog
    gates would then flag as asymmetry), so a missing Status is a loud failure, never a silent
    no-op."""
    text = path.read_text(encoding="utf-8")
    out: list[str] = []
    done = False
    for ln in text.splitlines():
        out.append(ln)
        if not done and ln.lstrip().startswith("> **Status:**"):
            out.append(line)
            done = True
    if not done:
        raise ValueError(f"{path.name} has no `> **Status:**` line to anchor the link after")
    sdlc_md.atomic_write(path, "\n".join(out) + ("\n" if text.endswith("\n") else ""))


_DECOMPOSED_LINE_RE = re.compile(r"(?m)^(>?\s*\*\*Decomposed-into:\*\*)\s*.*$")


def _write_decomposed(path: Path, ids: list[str]) -> None:
    """Set the request's `Decomposed-into:` to `ids` - de-duplicated (by normalised id) and
    order-preserving, so an incremental `add` APPENDS a new epic without ever losing or duplicating
    an earlier one. Updates the existing line in place when there is one (the `add` path), else
    inserts one after `Status:` (the first `apply`). This is the append-only guarantee the earlier
    slices depend on."""
    seen: set[str] = set()
    ordered: list[str] = []
    for i in ids:
        k = sdlc_md.norm_id(i)
        if k and k not in seen:
            seen.add(k)
            ordered.append(i)
    line = f"> **Decomposed-into:** {', '.join(ordered)}"
    text = path.read_text(encoding="utf-8")
    if _DECOMPOSED_LINE_RE.search(text):
        new = _DECOMPOSED_LINE_RE.sub(lambda m: line, text, count=1)
        sdlc_md.atomic_write(path, new)
    else:
        _insert_after_status(path, line)


def _decompose(repo_root, rid: str, rpath: Path, epic_title: str,
               stories: list[tuple[str, int, str | None]], total: int,
               existing_children: list[str]) -> tuple[str, list[str]]:
    """Mint the epic + its stories and wire everything under ONE rollback guard, then set the
    request's `Decomposed-into:` to `existing_children` + the new epic (append-only). The shared
    core of `apply` (existing_children=[]) and `add` (existing_children=the request's current
    epics): a single atomic mint, so a mid-create failure leaves the backlog untouched. Returns
    (epic_id, story_ids)."""
    root = Path(repo_root)
    minted: list[Path] = []
    try:
        ep = artifact.new(root, "epic", epic_title,
                          {"size": _tshirt_for(total),
                           "summary": f"Decomposed from {rid}. Delivers the work {rid} requested."})
        epic_id = ep["id"]
        epic_path = Path(ep["path"])
        minted.append(epic_path)
        story_ids: list[str] = []
        for title, points, affects in stories:
            fields = {"epic": epic_id, "points": points}
            if affects:
                fields["affects"] = affects
            s = artifact.new(root, "story", title, fields)
            minted.append(Path(s["path"]))
            story_ids.append(s["id"])
        _insert_after_status(epic_path, f"> **Parent:** {rid}")
        _insert_after_status(epic_path, f"> **Derived Point Total:** {total}")
        _write_decomposed(rpath, [*existing_children, epic_id])
    except BaseException:
        for p in minted:
            try:
                p.unlink()
            except OSError:
                pass
        raise
    return epic_id, story_ids


def parse_story_spec(spec: str) -> tuple[str, int, str | None]:
    """A `--story` value: `title|points` or `title|points|affects`. Returns (title, points,
    affects|None). Points are validated against the Fibonacci scale here, before anything is
    minted, so a bad breakdown fails loud and empty."""
    parts = [p.strip() for p in spec.split("|")]
    if len(parts) < 2 or not parts[0]:
        raise ValueError(f"story spec {spec!r} must be 'title|points' (optional '|affects')")
    title = parts[0]
    points = sdlc_md.check_points(parts[1])          # raises on an off-scale value
    affects = parts[2] if len(parts) > 2 and parts[2] else None
    return title, points, affects


# The status a request moves to once it is decomposed and being delivered via its children. It
# reaches its TERMINAL status only by derivation (G2), when the children are done - this is just
# the "now being worked" signal. A request already terminal or without a working state is left be.
_WORKING_STATUS = {"cr": "In Progress", "rfc": "In Review"}

# The review seats a refine consult surfaces open questions to - the Three Amigos, by role.
_AMIGO_ROLES = ("engineering", "product", "qa")


def refine(repo_root: Path | str, request_id: str, epic_title: str,
           stories: list[tuple[str, int, str | None]], questions: list[str] | None = None,
           dry_run: bool = False) -> dict:
    """Decompose `request_id` into an epic titled `epic_title` holding `stories`
    (title, points, affects?). Writes the bidirectional links and rolls the epic's point total.

    Validates ALL INPUT before minting anything - the request must resolve, be a request type and
    not already decomposed; every story's points must be on the scale (parsed already); every title
    (epic and stories) must be a single line the creators will accept. Only after that does it mint,
    and if a create still fails part-way (a rare IO error), it ROLLS BACK the files it wrote. So a
    bad breakdown, or a failure mid-mint, leaves the backlog untouched - refine never
    half-decomposes a request."""
    root = Path(repo_root)
    refinable(root, request_id)   # SHARED validation: non-request / already-decomposed refusals
    rpath, rtype = sdlc_md.find_by_id(root, request_id)
    if not stories:
        raise ValueError("refine needs at least one --story: an empty decomposition delivers "
                         "nothing, which is exactly what the UNDECOMPOSED check flags.")
    # Validate EVERY title up front - `require_single_line` runs inside `artifact.new` mid-loop, so
    # without this a bad title (a stray newline in an agent-proposed story) would raise only after
    # the epic and earlier stories are already on disk, orphaned. The request must also carry a
    # Status line, or the `Decomposed-into:` write would fail after the children exist.
    sdlc_md.require_single_line("epic title", epic_title)
    for title, _, _ in stories:
        sdlc_md.require_single_line("story title", title)
    if sdlc_md.extract_field(rpath.read_text(encoding="utf-8"), "Status") is None:
        raise ValueError(f"{request_id} has no `> **Status:**` line - cannot wire its "
                         f"`Decomposed-into:` link; fix the request first.")
    rid = sdlc_md.extract_record_id(rpath.stem) or request_id
    total = sum(p for _, p, _ in stories)
    open_questions = [q for q in (questions or []) if q.strip()]
    if dry_run:
        return {"request": rid, "epic": "(dry-run)", "epic_size": _tshirt_for(total),
                "stories": [t for t, _, _ in stories], "points": total,
                "open_questions": open_questions, "dry_run": True}

    epic_id, story_ids = _decompose(root, rid, rpath, epic_title, stories, total,
                                    existing_children=[])
    # 4. close the loop on the request's status: it is now being DELIVERED via its children, so it
    # moves to its working state (it reaches terminal only by derivation, G2). Best-effort - if a
    # gate we do not force past declines the move, the decomposition still stands.
    moved_to = None
    working = _WORKING_STATUS.get(rtype)
    vocab = sdlc_md.status_vocab(rtype, root)
    cur = sdlc_md.canonical_status(sdlc_md.extract_field(rpath.read_text(encoding="utf-8"),
                                                         "Status"), vocab)
    if working and cur != working and not sdlc_md.is_terminal_status(rtype, cur or ""):
        import transition   # local import: transition pulls critic/plan_review; keep off load
        try:
            transition.transition(root, rid, working)
            moved_to = working
        except (ValueError, FileNotFoundError):
            pass
    return {"request": rid, "epic": epic_id, "epic_size": _tshirt_for(total),
            "stories": story_ids, "points": total, "status": moved_to,
            "open_questions": open_questions, "amigo_roles": list(_AMIGO_ROLES),
            "dry_run": False}


def refine_add(repo_root: Path | str, request_id: str, epic_title: str,
               stories: list[tuple[str, int, str | None]], dry_run: bool = False) -> dict:
    """Append a FURTHER epic + stories to an ALREADY-decomposed request.

    The inverse precondition of `refine` (apply): a request delivered in slices - one epic per
    sprint - grows its Decomposed-into over several refines, so `add` requires the request to be
    decomposed already and APPENDS (never clobbers) the new epic to its existing children. Shares
    apply's up-front validation and atomic mint (`_decompose`), so a bad breakdown or a mid-create
    failure mints nothing. Does NOT re-move the request status - it is already working."""
    root = Path(repo_root)
    hit = sdlc_md.find_by_id(root, request_id)
    if not hit:
        raise ValueError(f"no artefact found for id {request_id!r}")
    rpath, rtype = hit
    if not sdlc_md.is_request(rtype):
        raise ValueError(f"refine takes a REQUEST (RFC/CR); {request_id} is a {rtype}.")
    existing = sdlc_md.decomposed_ids(rpath.read_text(encoding="utf-8"))
    if not existing:
        raise ValueError(f"{request_id} is not decomposed yet - use `refine apply` for its first "
                         f"epic; `refine add` appends a further one to an already-decomposed request.")
    if not stories:
        raise ValueError("refine add needs at least one --story.")
    sdlc_md.require_single_line("epic title", epic_title)
    for title, _, _ in stories:
        sdlc_md.require_single_line("story title", title)
    rid = sdlc_md.extract_record_id(rpath.stem) or request_id
    total = sum(p for _, p, _ in stories)
    if dry_run:
        return {"request": rid, "epic": "(dry-run)", "epic_size": _tshirt_for(total),
                "stories": [t for t, _, _ in stories], "points": total,
                "existing_epics": existing, "dry_run": True}
    epic_id, story_ids = _decompose(root, rid, rpath, epic_title, stories, total,
                                    existing_children=existing)
    return {"request": rid, "epic": epic_id, "epic_size": _tshirt_for(total),
            "stories": story_ids, "points": total, "existing_epics": existing,
            "all_epics": [*existing, epic_id], "dry_run": False}


def _section(text: str, heading: str) -> str:
    """The body under a `## Heading`, trimmed, or '' - so `show` can surface a request's Summary,
    Impact and Design Options without the reader opening the file."""
    lines = text.splitlines()
    out: list[str] = []
    grabbing = False
    for ln in lines:
        if ln.startswith("## "):
            if grabbing:
                break
            grabbing = ln[3:].strip().lower() == heading.lower()
            continue
        if grabbing:
            out.append(ln)
    return "\n".join(out).strip()


def refinable(repo_root: Path | str, request_id: str) -> dict:
    """Validate that `request_id` can be refined and gather what an operator needs to propose the
    breakdown: its type, summary, impact/design, and any open decisions. Raises the SAME refusals
    `refine` does (non-request, already-decomposed), so `show` and `apply` agree on what refinable
    means - a request that `show` accepts is one `apply` will."""
    root = Path(repo_root)
    hit = sdlc_md.find_by_id(root, request_id)
    if not hit:
        raise ValueError(f"no artefact found for id {request_id!r}")
    rpath, rtype = hit
    if not sdlc_md.is_request(rtype):
        raise ValueError(f"refine takes a REQUEST (RFC/CR); {request_id} is a {rtype}.")
    text = rpath.read_text(encoding="utf-8")
    existing = sdlc_md.decomposed_ids(text)
    if existing:
        raise ValueError(f"{request_id} is already decomposed into {', '.join(existing)}.")
    return {"id": sdlc_md.extract_record_id(rpath.stem) or request_id, "type": rtype,
            "title": sdlc_md.extract_h1_title(text) or "",
            "summary": _section(text, "Summary"),
            "detail": _section(text, "Impact") or _section(text, "Design Options"),
            "open_decisions": _section(text, "Open Decisions")}


def cmd_show(args: argparse.Namespace) -> int:
    try:
        info = refinable(args.root, args.request)
    except (ValueError, FileNotFoundError) as exc:
        print(f"not refinable: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(info, indent=2))
        return 0
    print(f"{info['id']} ({info['type']}): {info['title']}\n")
    if info["summary"]:
        print(f"Summary:\n{info['summary']}\n")
    if info["detail"]:
        print(f"Impact / design:\n{info['detail']}\n")
    if info["open_decisions"]:
        print(f"Open decisions (resolve with the amigos before refining):\n{info['open_decisions']}\n")
    print("Propose the breakdown, then:\n"
          f"  refine apply --request {info['id']} --epic-title \"...\" "
          "--story \"title|points\" --story \"title|points|affects\" ...")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    try:
        stories = [parse_story_spec(s) for s in (args.story or [])]
        result = refine(args.root, args.request, args.epic_title, stories,
                        questions=args.question, dry_run=args.dry_run)
    except (ValueError, FileNotFoundError) as exc:
        print(f"refine refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    verb = "would refine" if result["dry_run"] else "refined"
    print(f"{verb} {result['request']} -> {result['epic']} ({result['epic_size']}, "
          f"{result['points']} pts) with {len(result['stories'])} story(ies): "
          f"{', '.join(result['stories'])}")
    if result.get("status"):
        print(f"  {result['request']} moved to {result['status']} - it reaches terminal only by "
              f"derivation, when its children are done")
    if result.get("open_questions"):
        roles = ", ".join(result.get("amigo_roles", []))
        print(f"  {len(result['open_questions'])} open question(s) for the Three-Amigos consult "
              f"({roles}) - settle before building:")
        for q in result["open_questions"]:
            print(f"    - {q}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    try:
        stories = [parse_story_spec(s) for s in (args.story or [])]
        result = refine_add(args.root, args.request, args.epic_title, stories, dry_run=args.dry_run)
    except (ValueError, FileNotFoundError) as exc:
        print(f"refine add refused: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    verb = "would add" if result["dry_run"] else "added"
    print(f"{verb} {result['epic']} ({result['epic_size']}, {result['points']} pts, "
          f"{len(result['stories'])} story(ies): {', '.join(result['stories'])}) to "
          f"{result['request']}")
    if not result["dry_run"]:
        print(f"  {result['request']} now decomposed into {', '.join(result['all_epics'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="refine", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="Decompose a request into an epic + stories, links wired")
    a.add_argument("--request", required=True, help="the RFC/CR to decompose")
    a.add_argument("--epic-title", dest="epic_title", required=True,
                   help="title for the epic the request becomes")
    a.add_argument("--story", action="append", metavar="TITLE|POINTS[|AFFECTS]",
                   help="a story in the breakdown: 'title|points' or 'title|points|affects'. "
                        "Repeatable. Points must be on the Fibonacci scale.")
    a.add_argument("--question", action="append", metavar="TEXT",
                   help="an open question for the Three-Amigos consult, surfaced at apply time. "
                        "Repeatable.")
    a.add_argument("--dry-run", action="store_true", help="validate and report; mint nothing")
    a.add_argument("--root", default=".")   # de-duped by add_global_root; enables `apply --root`
    sdlc_md.add_format_arg(a)
    a.set_defaults(func=cmd_apply)

    ad = sub.add_parser("add", help="Append a FURTHER epic + stories to an already-decomposed "
                                    "request (a later slice of a large request)")
    ad.add_argument("--request", required=True, help="the already-decomposed RFC/CR to add to")
    ad.add_argument("--epic-title", dest="epic_title", required=True,
                    help="title for the new epic to append")
    ad.add_argument("--story", action="append", metavar="TITLE|POINTS[|AFFECTS]",
                    help="a story in the new epic: 'title|points' or 'title|points|affects'. "
                         "Repeatable. Points must be on the Fibonacci scale.")
    ad.add_argument("--dry-run", action="store_true", help="validate and report; mint nothing")
    ad.add_argument("--root", default=".")
    sdlc_md.add_format_arg(ad)
    ad.set_defaults(func=cmd_add)

    s = sub.add_parser("show", help="Show a request's content to inform the breakdown, and "
                                    "confirm it is refinable")
    s.add_argument("--request", required=True, help="the RFC/CR to inspect")
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
