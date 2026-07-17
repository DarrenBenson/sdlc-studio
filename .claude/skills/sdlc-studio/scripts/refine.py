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
from datetime import date
from pathlib import Path

try:
    from lib import sdlc_md
except ImportError:  # invoked from inside scripts/
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib import sdlc_md

import artifact
import persona_resolve


# The T-shirt Size an epic is born with, from the story-point total it decomposes into. A coarse
# read-off, never a measurement: the epic's real size is its `Derived Point Total`, which reconcile
# keeps equal to the sum of its stories' points. The band edges mirror the Fibonacci scale.
def _tshirt_for(total: int) -> str:
    return sdlc_md.size_for_points(total)   # the ONE point->size band (shared with the migration)


# The Parent / Decomposed-into link writers moved to `lib.sdlc_md` (beside the link READERS
# `parent_ref` / `decomposed_ids`) when `triage` became the second caller - LL0016: extract the
# shared definition BEFORE the second caller, not after. These thin aliases keep the module-local
# names (and refine's tests) working; both ceremonies now write links through one authority.
_insert_after_status = sdlc_md.insert_after_status
_write_decomposed = sdlc_md.write_decomposed


_CRITERION_RE = re.compile(r"^-\s*\[\s?\]\s+(.+?)\s*$", re.M)


def _ac_heading(criterion: str, limit: int = 100) -> str:
    """The AC heading taken from a request criterion: one line, truncated at a word boundary
    when long, and never ending in punctuation. A generated heading must pass markdownlint
    MD026 (no trailing punctuation) in any project that lints its workspace, so no trailing
    ellipsis or full stop is appended."""
    text = " ".join(criterion.split())
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] or text[:limit]
    return text.rstrip(" .,;:!?…")


def _request_criteria(text: str) -> list[str]:
    """The request's own `- [ ]` acceptance criteria, in order."""
    return _CRITERION_RE.findall(_section(text, "Acceptance Criteria"))


def _seed_acs(story_path: Path, criteria: list[str], redistribute_note: bool) -> None:
    """Replace the story's placeholder AC scaffold with one AC block per request
    criterion: the criterion is the title and the Then; Given/When and the Verify
    stay explicit placeholders - seeding TRANSCRIBES what the request already
    states, it never fabricates executability (validate keeps flagging the
    placeholders until the author fills them)."""
    text = story_path.read_text(encoding="utf-8")
    blocks = []
    if redistribute_note:
        blocks.append("> Seeded from the request's full criteria list - redistribute "
                      "across this epic's stories as you groom them.\n")
    for i, criterion in enumerate(criteria, 1):
        title = _ac_heading(criterion)
        blocks.append(f"### AC{i}: {title}\n\n"
                      f"- **Given** {{{{context}}}}\n- **When** {{{{action}}}}\n"
                      f"- **Then** {criterion}\n- **Verify:** {{{{executable check}}}}\n")
    seeded = "## Acceptance Criteria\n\n" + "\n".join(blocks) + "\n"
    # callable replacement: criterion text is DATA, never a regex template - a
    # criterion containing \1 or C:\temp must land verbatim, not crash the mint
    # or corrupt the story via escape expansion
    new = re.sub(r"## Acceptance Criteria\n.*?(?=## Revision History)", lambda m: seeded,
                 text, count=1, flags=re.S)
    sdlc_md.atomic_write(story_path, new)


def _decompose(repo_root, rid: str, rpath: Path, epic_title: str,
               stories: list[tuple[str, int, str | None]], total: int,
               existing_children: list[str],
               seed_criteria: list[str] | None = None) -> tuple[str, list[str]]:
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
        for idx, (title, points, affects) in enumerate(stories):
            fields = {"epic": epic_id, "points": points}
            if affects:
                fields["affects"] = affects
            s = artifact.new(root, "story", title, fields)
            minted.append(Path(s["path"]))
            story_ids.append(s["id"])
            # Record the ORIGINATING request on the story: in a shared batch epic (refine --into)
            # the epic's stories deliver different requests, so which story delivers which request
            # must be machine-resolvable, not only in the title. A secondary traceability link -
            # the story's Parent stays the epic, so derivation and the link gates are untouched.
            _insert_after_status(Path(s["path"]), f"> **Delivers:** {rid}")
            # seed the FIRST story with the request's criteria (all of them - a
            # multi-story breakdown redistributes during grooming); later stories
            # keep the bare scaffold
            if idx == 0 and seed_criteria:
                _seed_acs(Path(s["path"]), seed_criteria,
                          redistribute_note=len(stories) > 1)
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


def _roll_point_total(epic_path: Path, add: int) -> None:
    """Roll the epic's `Derived Point Total` up by `add` (the stories a further request added via
    `--into`). Absent, it is inserted; present, it is incremented in place. The T-shirt Size is a
    read-off of this total and is re-derived by reconcile, so only the number is written here."""
    text = epic_path.read_text(encoding="utf-8")
    cur = sdlc_md.extract_field(text, "Derived Point Total")
    if cur is not None and str(cur).strip().isdigit():
        new_total = int(str(cur).strip()) + add
        new = re.sub(r"(?im)^(\s*>\s*\*\*Derived Point Total:\*\*\s*)\d+\s*$",
                     lambda m: f"{m.group(1)}{new_total}", text, count=1)
        sdlc_md.atomic_write(epic_path, new)
    else:
        _insert_after_status(epic_path, f"> **Derived Point Total:** {add}")


def _decompose_into(repo_root, rid: str, rpath: Path, epic_id: str,
                    stories: list[tuple[str, int, str | None]], total: int,
                    existing_children: list[str],
                    seed_criteria: list[str] | None = None) -> tuple[str, list[str]]:
    """Mint the request's stories UNDER an existing epic (`--into`), roll that epic's point total,
    and wire the request's `Decomposed-into:`. The `--into` sibling of `_decompose`: it never mints
    an epic, so a themed batch epic can hold the stories of several small requests instead of each
    minting a singleton container. Same atomic-mint/rollback guard - a mid-create failure leaves the
    backlog untouched. The target epic is validated by the caller BEFORE anything is minted."""
    root = Path(repo_root)
    epic_path = sdlc_md.find_by_id(root, epic_id)[0]
    minted: list[Path] = []
    try:
        story_ids: list[str] = []
        for idx, (title, points, affects) in enumerate(stories):
            fields = {"epic": epic_id, "points": points}
            if affects:
                fields["affects"] = affects
            s = artifact.new(root, "story", title, fields)
            minted.append(Path(s["path"]))
            story_ids.append(s["id"])
            _insert_after_status(Path(s["path"]), f"> **Delivers:** {rid}")  # originating request
            if idx == 0 and seed_criteria:
                _seed_acs(Path(s["path"]), seed_criteria, redistribute_note=len(stories) > 1)
        # Back-link: the shared epic names THIS request as a parent too (it already names the one
        # it was minted for). A batch epic carries one `Parent:` line per request it delivers, so
        # the child->parent link resolves both ways for each - the symmetry the link gates check.
        if sdlc_md.norm_id(rid) not in {sdlc_md.norm_id(x) for x in sdlc_md.parent_refs(
                epic_path.read_text(encoding="utf-8"))}:
            _insert_after_status(epic_path, f"> **Parent:** {rid}")
        _roll_point_total(epic_path, total)
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

def _validate_into_target(root: Path, into_epic: str) -> None:
    """Refuse (before anything is minted) an `--into` target that is unknown, not an epic, or
    terminal - a closed epic cannot take new stories, and only an epic holds stories at all."""
    hit = sdlc_md.find_by_id(root, into_epic)
    if not hit:
        raise ValueError(f"--into target {into_epic} does not exist; nothing minted")
    epath, etype = hit
    if etype != "epic":
        raise ValueError(f"--into target {into_epic} is a {etype}, not an epic; only an epic "
                         f"holds stories. Nothing minted")
    estatus = sdlc_md.canonical_status(
        sdlc_md.extract_field(epath.read_text(encoding="utf-8"), "Status"),
        sdlc_md.status_vocab("epic", root))
    if sdlc_md.is_terminal_status("epic", estatus or ""):
        raise ValueError(f"--into target {into_epic} is terminal ({estatus}); a closed epic "
                         f"cannot take new stories. Nothing minted")


def refine(repo_root: Path | str, request_id: str, epic_title: str | None,
           stories: list[tuple[str, int, str | None]], questions: list[str] | None = None,
           dry_run: bool = False, skip_personas: bool = False,
           seed_acs: bool = True, into_epic: str | None = None) -> dict:
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
    # Exactly one of a new-epic title or an --into target - a request becomes one epic, whether
    # freshly minted or the shared batch container it joins.
    if bool(into_epic) == bool(epic_title):
        raise ValueError("refine needs EITHER --epic-title (mint a new epic) OR --into EPxxxx "
                         "(decompose into an existing epic), not both and not neither")
    if into_epic:
        _validate_into_target(root, into_epic)   # refuse a bad target BEFORE anything is minted
    else:
        sdlc_md.require_single_line("epic title", epic_title)
    for title, _, _ in stories:
        sdlc_md.require_single_line("story title", title)
    if sdlc_md.extract_field(rpath.read_text(encoding="utf-8"), "Status") is None:
        raise ValueError(f"{request_id} has no `> **Status:**` line - cannot wire its "
                         f"`Decomposed-into:` link; fix the request first.")
    rid = sdlc_md.extract_record_id(rpath.stem) or request_id
    total = sum(p for _, p, _ in stories)
    open_questions = [q for q in (questions or []) if q.strip()]
    # Resolve the Three-Amigos panel UP FRONT (read-only), engineering-led: a refine is where the
    # request's open questions get answered BY the seats, so a broken project seat card is a
    # refine-blocking problem, caught before anything is minted (refine's fail-empty discipline).
    # `--skip-personas` bypasses resolution entirely (byte-equivalent, no framing), the escape hatch.
    amigo_consult = persona_resolve.consult(root, persona_resolve.REFINE_PANEL, open_questions,
                                            skip_personas=skip_personas)
    if dry_run:
        return {"request": rid, "epic": into_epic or "(dry-run)", "epic_size": _tshirt_for(total),
                "stories": [t for t, _, _ in stories], "points": total,
                "open_questions": open_questions, "consult": amigo_consult, "dry_run": True}

    seed_criteria = (_request_criteria(rpath.read_text(encoding="utf-8"))
                     if seed_acs else None)
    if into_epic:
        epic_id, story_ids = _decompose_into(root, rid, rpath, into_epic, stories, total,
                                             existing_children=[], seed_criteria=seed_criteria)
    else:
        epic_id, story_ids = _decompose(root, rid, rpath, epic_title, stories, total,
                                        existing_children=[], seed_criteria=seed_criteria)
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
    # Record the consult on the request itself (audit trail): which seats were consulted and the
    # open questions. Best-effort - the decomposition stands even if the record write fails.
    if amigo_consult.get("questions"):
        try:
            persona_resolve.record_consult(rpath, amigo_consult, date.today().isoformat())
        except (OSError, ValueError):
            pass
    return {"request": rid, "epic": epic_id, "epic_size": _tshirt_for(total),
            "stories": story_ids, "points": total, "status": moved_to,
            "open_questions": open_questions, "consult": amigo_consult,
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


def refinable(repo_root: Path | str, request_id: str, allow_decomposed: bool = False) -> dict:
    """Validate that `request_id` can be refined and gather what an operator needs to propose the
    breakdown: its type, summary, impact/design, any open decisions, and its existing epics. Raises
    the SAME refusals `refine` does (non-request, already-decomposed), so `apply` and `show` agree
    on what refinable means - a request that `apply` accepts is one it will refine.

    `allow_decomposed` relaxes ONLY the already-decomposed refusal, for `show`: once `refine add`
    exists, an operator planning the NEXT slice of a request needs to see its content AND its
    current epics, which `show` is the natural home for. The returned `decomposed_into` lists the
    existing epics either way (empty when none), so a caller can tell a first `apply` from an `add`.
    `apply` keeps the strict precondition (default False); `show` passes True and stays read-only."""
    root = Path(repo_root)
    hit = sdlc_md.find_by_id(root, request_id)
    if not hit:
        raise ValueError(f"no artefact found for id {request_id!r}")
    rpath, rtype = hit
    if not sdlc_md.is_request(rtype):
        raise ValueError(f"refine takes a REQUEST (RFC/CR); {request_id} is a {rtype}.")
    text = rpath.read_text(encoding="utf-8")
    existing = sdlc_md.decomposed_ids(text)
    if existing and not allow_decomposed:
        raise ValueError(f"{request_id} is already decomposed into {', '.join(existing)}.")
    return {"id": sdlc_md.extract_record_id(rpath.stem) or request_id, "type": rtype,
            "title": sdlc_md.extract_h1_title(text) or "",
            "summary": _section(text, "Summary"),
            "detail": _section(text, "Impact") or _section(text, "Design Options"),
            "open_decisions": _section(text, "Open Decisions"),
            "decomposed_into": existing}


def cmd_show(args: argparse.Namespace) -> int:
    try:
        # show is READ-ONLY and accepts an already-decomposed request: it exists to inform a
        # breakdown, including the NEXT slice of a request already part-refined (an `add`). It
        # refuses only a non-request or an unresolvable id.
        info = refinable(args.root, args.request, allow_decomposed=True)
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
    existing = info.get("decomposed_into") or []
    if existing:
        # Already part-refined: name its epics and steer to `add` (which APPENDS a slice), not
        # `apply` (which is the first decomposition and would refuse a decomposed request).
        print(f"Already decomposed into: {', '.join(existing)}\n")
        print("Add the NEXT slice (appends a further epic):\n"
              f"  refine add --request {info['id']} --epic-title \"...\" "
              "--story \"title|points\" --story \"title|points|affects\" ...")
    else:
        print("Propose the breakdown, then:\n"
              f"  refine apply --request {info['id']} --epic-title \"...\" "
              "--story \"title|points\" --story \"title|points|affects\" ...")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    try:
        stories = [parse_story_spec(s) for s in (args.story or [])]
        result = refine(args.root, args.request, args.epic_title, stories,
                        questions=args.question, dry_run=args.dry_run,
                        skip_personas=getattr(args, "skip_personas", False),
                        seed_acs=getattr(args, "seed_acs", True),
                        into_epic=getattr(args, "into_epic", None))
    except (ValueError, FileNotFoundError, persona_resolve.RenderError) as exc:
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
        consult = result.get("consult") or {}
        panel = ", ".join(f"{p['seat']} ({p['role']})" for p in consult.get("panel", []))
        lead = consult.get("lead")
        lead_note = f"{lead} leads; " if lead else ""
        print(f"  {len(result['open_questions'])} open question(s) for the Three-Amigos consult "
              f"({lead_note}{panel}) - settle before building:")
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
    a.add_argument("--epic-title", dest="epic_title",
                   help="title for the NEW epic the request becomes (omit when using --into)")
    a.add_argument("--into", dest="into_epic", metavar="EPxxxx",
                   help="decompose the request's stories INTO this existing OPEN epic (a shared "
                        "batch container) instead of minting a new one - the request's "
                        "Decomposed-into points at it and its point total rolls up. A terminal, "
                        "non-epic, or unknown target is refused with nothing minted")
    a.add_argument("--story", action="append", metavar="TITLE|POINTS[|AFFECTS]",
                   help="a story in the breakdown: 'title|points' or 'title|points|affects'. "
                        "Repeatable. Points must be on the Fibonacci scale.")
    a.add_argument("--question", action="append", metavar="TEXT",
                   help="an open question for the Three-Amigos consult, surfaced at apply time "
                        "and directed at the resolved seats (engineering-led). Repeatable.")
    a.add_argument("--no-seed-acs", action="store_false", dest="seed_acs", default=True,
                   help="mint bare AC scaffolds instead of seeding from the request's "
                        "acceptance criteria")
    a.add_argument("--skip-personas", action="store_true",
                   help="force the generic path: resolve no amigo seats, no framing (byte-equivalent)")
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
