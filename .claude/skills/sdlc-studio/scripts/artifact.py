#!/usr/bin/env python3
"""Deterministic artifact create + close cascade.

`new` creates ANY numbered/indexed artifact (epic, story, plan, bug, cr, rfc, test-spec,
workflow) as a structured scaffold AND wires it: allocate a collision-free id, render a
valid file (required sections so it passes validate), append the index data-table row
(built generically from that index's own header), recompute counts, and wire cross-links
(a story into its parent epic's Story Breakdown). `close` terminal-transitions an artifact
and cascades (reusing transition). The agent fills the scaffold's content; the wiring is
deterministic. This replaces the ~10-step hand cascade (the v2.x friction).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import conventions, sdlc_md, tiers  # noqa: E402
import file_finding  # noqa: E402  (reuse _slug, _next_number, append_index_row)
import reconcile  # noqa: E402
import triage_noise  # noqa: E402  (v3 triage noise controls; dormant on v2)
import transition  # noqa: E402

# The disp-id form per type (cr/rfc carry a dash: `CR-0001`, every other type `US0001`).
# The one per-type fact this module owns - the statuses beside it are NOT restated here.
_DASH = {
    "epic": False,
    "story": False,
    "plan": False,
    "test-spec": False,
    "workflow": False,
    "bug": False,
    "cr": True,
    "rfc": True,
}

# Per-type create status, terminal (close) status, and disp-id form. The two statuses are
# DERIVED from the status vocabulary in `lib.sdlc_md` - the one authority the validator, the
# transition gate and the archiver already read - so a vocab change lands in one file rather
# than silently drifting between three copies of the same table.
SPEC = {
    t: {"status": sdlc_md.create_status(t),
        "terminal": sdlc_md.default_terminal_status(t),
        "dash": dash}
    for t, dash in _DASH.items()
}
_PREFIX_TYPE = {sdlc_md.ARTIFACT_TYPES[t][1].upper(): t for t in SPEC}

# Scaffold richness, lean to rich - from lib.tiers, the one authority the creator, the
# validator, the transition gate and the conformance backstop all share. `planning` is the
# pre-implementation tier: the sections a story must settle to be planned and prioritised
# (ACs with Verify + Verification target, scope, technical notes) and none of the
# implementation furniture. Creation stamps ONLY `planning` (`> **Template:** planning`); a
# `full` stamp is written by `promote` alone, and only after it has added the sections - which
# is what lets the gate check a `full` claim instead of believing it.
MINIMAL, PLANNING, FULL = tiers.MINIMAL, tiers.PLANNING, tiers.FULL
TEMPLATE_TIERS = tiers.TEMPLATE_TIERS
TIER_FIELD = tiers.TIER_FIELD


def _disp(type_: str, n: int) -> str:
    p = sdlc_md.ARTIFACT_TYPES[type_][1]
    return f"{p}-{n:04d}" if SPEC[type_]["dash"] else f"{p}{n:04d}"


def _schema_v3(root: Path) -> bool:
    """True when the project opted into schema v3 (`schema_version: 3` in `.config.yaml`).
    Thin alias for the shared `sdlc_md.is_schema_v3` (one authority; both degrade to v2 on a
    PyYAML-less machine)."""
    return sdlc_md.is_schema_v3(root)


def _alloc_ids(root: Path, type_: str) -> tuple[str, str]:
    """(file_id, disp) for a new artifact, era-aware. v2 allocates the next sequential number
    (file_id `CR0001`, disp `CR-0001`); v3 mints a collision-checked short ULID where the
    file_id and disp are the single canonical form `BG-01JQK3F8`."""
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    if _schema_v3(root):
        ident = sdlc_md.mint_v3_id(root, type_)  # the one shared era-v3 allocator
        return ident, ident
    n = file_finding._next_number(root, type_)
    return f"{prefix}{n:04d}", _disp(type_, n)


def _create_status(type_: str, root: Path) -> str:
    """The status a freshly-filed artefact starts in. Findings (bug/cr/rfc) land in `inbox`
    under schema v3 (EP0014), so a different seat triages them into the workflow proper;
    every other type - and all types under v2 - keeps its per-type SPEC create status."""
    if type_ in sdlc_md.FINDING_TYPES and _schema_v3(root):
        return sdlc_md.INBOX_STATUS
    return SPEC[type_]["status"]


def _text(f: dict, key: str, placeholder: str) -> str:
    """Caller-supplied content for one section, else the scaffold placeholder the agent fills.
    Free text is prose-safed (markdown-safe plus the metadata-line guard), so a creator never
    mints a lint-red artefact nor a body line a reader takes for provenance."""
    val = f.get(key)
    return file_finding._prose_safe(val) if isinstance(val, str) and val.strip() else placeholder


def _list(f: dict, key: str) -> list[str]:
    items = f.get(key)
    return [file_finding._md_safe(i) for i in items if str(i).strip()] \
        if isinstance(items, list) else []


TARGET_TIERS = ("functional", "conversational", "soak", "live")


def _target_of(f: dict) -> str:
    """The Verification target tier for supplied ACs, validated - or "" when none is given.

    An unknown tier is REFUSED, never written: `transition`'s depth-parity gate matches the
    tier against its own table and ignores what it does not recognise, so a typo'd target
    would quietly drop the story out of the gate it was meant to opt into."""
    val = str(f.get("target") or "").strip()
    if not val:
        return ""
    if val.lower() not in TARGET_TIERS:
        raise ValueError(f"unknown verification target {val!r} "
                         f"(expected one of {', '.join(TARGET_TIERS)})")
    return val.lower()


def _verifiers_of(f: dict) -> list[str]:
    """The executable checks supplied alongside the ACs, VERBATIM.

    Never markdown-safed. A Verify line is a command `verify_ac` reads back and runs, and
    markdown-safing an underscore rewrites it: `rg -q my_token src/` becomes
    ``rg -q `my_token` src/``. For a list-form verb (pytest and friends, `shell=False`) those
    backticks are only a corrupted literal argument - the check silently stops checking what it
    says it checks. For a SHELL-backed verb, `_build_command` returns a string run under
    `shell=True`, and the same rewrite is command substitution: the backticked token executes.
    Verbatim is the only form that is both correct and safe. A line break is refused - it would
    inject a second directive line into the AC block, and only the first is the one anyone read.
    That refusal is the shared one (`require_single_line`), so a Verify expression and every
    other single-line field are judged by one rule and one character class.
    """
    out: list[str] = []
    for i, v in enumerate((f.get("verify") or []), 1):
        s = str(v)
        if not s.strip():
            continue
        out.append(sdlc_md.require_single_line(f"verify[{i}]", s.strip()))
    return out


def _story_acs(f: dict) -> str:
    """The Acceptance Criteria body. Supplied criteria render as real, id'd ACs; with none
    supplied the scaffold keeps its `{{placeholder}}` slots, which the validator reports as
    unfilled - a scaffold is not yet a specified story, and the creator does not pretend it is.

    A supplied criterion may carry its executable check (`--verify`, positional with `--ac`)
    and its verification target. Both are written only when given: there is no honest default
    for a Verify line - a placeholder would fail the validator, and `manual` would assert a
    proof nobody ran. An AC with no Verify line is reported by conformance's `verifiable`
    stage, which is the system saying so out loud rather than papering over it."""
    acs = _list(f, "acs")
    if not acs:
        return ("### AC1: {{define}}\n\n- **Given** {{context}}\n- **When** {{action}}\n"
                "- **Then** {{outcome}}\n- **Verify:** {{executable check}}\n")
    verifies = _verifiers_of(f)
    target = _target_of(f)
    out: list[str] = []
    for i, a in enumerate(acs, 1):
        out.append(f"- **AC{i}:** {a}\n")
        if i <= len(verifies):
            out.append(f"  - **Verify:** {verifies[i - 1]}\n")
        if target:
            out.append(f"  - **Verification target:** {target}\n")
    return "".join(out)


# The unfilled size slot, in the scale's own words - so a scaffold the caller never sized names
# the vocabulary rather than an empty line. A bug or a CR never reaches it (the grooming gate
# refuses an unsized one before any render); it is the honest placeholder for every other path.
_POINTS_SLOT = "{{" + "|".join(str(p) for p in sdlc_md.POINTS_SCALE) + "}}"


def _sizing_line(type_: str, f: dict) -> str:
    """The sizing metadata line for a type, from `--size` or `--points`. A REQUEST or CONTAINER
    (cr/rfc/epic) carries a T-shirt `Size`; a DELIVERY unit (story/bug) carries `Points`. Written
    by the SAME writers the finding filer uses (`file_finding._size_line`), so the two creation
    paths cannot disagree on what a type is sized by (LL0016 - the bug this closes was the two
    creators writing different shapes for the same type). The wrong sizing flag for the type is
    WARNED, never silently dropped (LL0008/BG0149 - a story's `--points` used to vanish)."""
    delivery = type_ in ("story", "bug")
    wrong = f.get("points") if not delivery else f.get("size")
    if str(wrong or "").strip():
        want, got = (("--size", "--points") if not delivery else ("--points", "--size"))
        carries = ("a T-shirt Size" if not delivery else "Points")
        print(f"warning: a {type_} carries {carries}, so {got} was ignored - pass {want}. "
              f"Nothing was sized.", file=sys.stderr)
    if delivery:
        return f"> **Points:** {f['points']}\n" if str(f.get("points") or "").strip() else ""
    return file_finding._size_line(f)


def _render(type_: str, disp: str, title: str, today: str, f: dict) -> str:
    st = f.get("_status") or SPEC[type_]["status"]
    # Provenance stamp - marks this artifact as tool-created (deterministic path). Raised-by is
    # the typed authorship of record, stamped at creation from --author (defaulting to the
    # invoking agent), so a schema-v3 artefact is never born failing its own authorship rule.
    head = (f"# {disp}: {title}\n\n> **Status:** {st}\n> **Created:** {today}\n"
            f"> **Created-by:** sdlc-studio new\n"
            f"> **Raised-by:** {f.get('_raised_by') or sdlc_md.DEFAULT_AGENT_AUTHOR}\n")
    # The tier stamp the promotion gate reads. Written ONLY for `planning` - the tier that
    # owes the project a promotion before implementation. An unstamped artefact is not
    # planning-tier, so nothing that predates the tier is gated by it.
    if f.get("_tier") == PLANNING:
        head += f"> **{TIER_FIELD}:** {PLANNING}\n"
    # Record-only tranche reference: written ONLY as orchestrator pass-through (when the caller
    # supplies it); sdlc-studio never allocates it. Absent otherwise.
    if str(f.get("tranche") or "").strip():
        head += f"> **Tranche:** {str(f['tranche']).strip()}\n"
    # The files this unit will touch, in the ONE shape the planner parses - rendered by the same
    # writer the finding filer uses, so the two creation paths cannot disagree about what the
    # field looks like. Accepted for every type; DEMANDED of a bug and a CR (`check_groomed`).
    head += file_finding._affects_line(f)
    # The Author cell names the same authorship of record stamped above - never a literal, and
    # a name rather than the typed triple (which is `Raised-by`'s job). One shared row writer
    # with the filer, so both escape a `|` in a name instead of shifting the columns.
    rev = (f"\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
           f"{file_finding.rev_row(today, f, 'Created via `new` (deterministic)')}\n")
    if type_ == "story":
        # The Persona line is written only when a persona is named: an absent optional field is
        # honestly absent, never an unresolved placeholder in the metadata block.
        persona = f"> **Persona:** {f['persona']}\n" if str(f.get("persona") or "").strip() else ""
        return (head + f"> **Epic:** {f.get('epic') or '-'}\n" + _sizing_line("story", f) + persona +
                "\n## User Story\n\n**As a** {{role}}\n**I want** {{capability}}\n"
                "**So that** {{benefit}}\n\n## Acceptance Criteria\n\n" + _story_acs(f) + rev)
    if type_ == "epic":
        acs = _list(f, "acs")
        ac_body = ("\n## Acceptance Criteria\n\n" + "".join(f"- [ ] {a}\n" for a in acs)) if acs else ""
        return (head + _sizing_line("epic", f) + "\n## Summary\n\n" +
                _text(f, "summary", "{{what this epic groups}}") +
                "\n\n## Story Breakdown\n\n_No stories yet._\n" + ac_body + rev)
    if type_ == "cr":
        acs = _list(f, "acs")
        ac_body = "".join(f"- [ ] {a}\n" for a in acs) if acs else "- [ ] {{criterion}}\n"
        return (head + f"> **Priority:** {f.get('priority', 'Medium')}\n"
                f"> **Type:** {f.get('ctype', 'Feature')}\n" + _sizing_line("cr", f) + "\n"
                "## Summary\n\n" + _text(f, "summary", "{{what changes and why}}") +
                "\n\n## Impact\n\n" + _text(f, "impact", "{{who this affects and what breaks}}") +
                "\n\n## Acceptance Criteria\n\n" + ac_body + rev)
    if type_ == "rfc":
        options = _list(f, "options")
        opt_body = ("".join(f"- **{o}**\n" for o in options) if options
                    else "- **Option A** {{...}}\n")
        return (head + _sizing_line("rfc", f) + "\n## Summary\n\n" +
                _text(f, "summary", "{{the unsettled design}}") +
                "\n\n## Design Options\n\n" + opt_body +
                "\n## Recommendation\n\n" + _text(f, "recommendation", "TBD") +
                "\n\n## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | {{decision}} | Open |\n" + rev)
    if type_ == "bug":
        # Points are the job SIZE of the fix; Severity is its urgency. Two axes, and the planner
        # sizes on the first: a bug created without one is a unit `sprint plan` refuses.
        return (head + f"> **Severity:** {f.get('severity', 'Medium')}\n" + _sizing_line("bug", f) +
                "\n## Summary\n\n" + _text(f, "summary", "{{symptom}}") +
                "\n\n## Steps to Reproduce\n\n" + _text(f, "steps", "{{steps}}") +
                "\n\n## Proposed Fix\n\n" + _text(f, "fix", "{{fix}}") + "\n" + rev)
    return head + "\n## Overview\n\n" + _text(f, "summary", "{{purpose}}") + "\n" + rev


def _core_template(type_: str) -> Path:
    return tiers.core_template(type_)


def _planning_template(type_: str) -> Path:
    """The lean pre-implementation body for a type. Defined for the two types whose full
    template has a structural floor a planning artefact cannot get under (story ~171 lines,
    epic ~148); every other type's minimal scaffold is already that lean, and `_graft` falls
    back to it when this file does not exist."""
    return tiers.planning_template(type_)


_AC_HEAD_RE = re.compile(r"^##\s+Acceptance Criteria\b.*$", re.M | re.I)
_IMPACT_HEAD_RE = re.compile(r"^##\s+(?:Impact|Motivation)\b.*$", re.M | re.I)


def _fill_acs(body: str, type_: str, f: dict) -> str:
    """Write the caller's criteria into a grafted template's Acceptance Criteria section,
    replacing its placeholder block."""
    acs = _list(f, "acs")
    if not acs or type_ not in ("story", "cr", "epic"):
        return body
    m = _AC_HEAD_RE.search(body)
    if not m:
        return body
    rest = body[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)  # `### ACn` subsections belong to this section
    tail = rest[nxt.start():] if nxt else ""
    filled = _story_acs(f) if type_ == "story" else "".join(f"- [ ] {a}\n" for a in acs)
    return f"{body[:m.end()]}\n\n{filled}\n{tail}"


def _fill_impact(body: str, type_: str, f: dict) -> str:
    """Write a CR's impact statement and size estimate directly under its Impact heading.
    The rich template heads straight into subsections, leaving the heading itself bodiless -
    which reads as no impact statement at all."""
    if type_ != "cr":
        return body
    block = ""
    if str(f.get("impact") or "").strip():
        block += f"\n\n{file_finding._prose_safe(f['impact'])}"
    # A CR is a REQUEST - it carries a T-shirt Size, not points (the Size line is in the metadata
    # head, written by _sizing_line; nothing points-shaped belongs in the CR body now).
    m = _IMPACT_HEAD_RE.search(body)
    if not block or not m:
        return body
    # the remainder already opens on its own blank line - do not stack a second (MD012)
    return f"{body[:m.end()]}{block}{body[m.end():]}"


# Each caller-supplied field and the section headings it may land under, in preference
# order. A creator that accepts content and silently drops it is worse than one that never
# accepted it: the caller gets exit 0 and a clean validator over an artefact its words never
# reached. Nothing supplied is ever dropped - a template with no matching heading gets the
# section appended rather than losing the content.
_CONTENT_SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("summary", ("Summary", "Overview")),
    ("steps", ("Steps to Reproduce", "Reproduction")),
    ("fix", ("Proposed Fix", "Fix")),
    ("options", ("Design Options", "Options")),
    ("recommendation", ("Recommendation",)),
)
_REV_SECTION_RE = re.compile(r"^##\s+Revision History\b.*$", re.M | re.I)


def _rendered(key: str, f: dict) -> str:
    """One field's content as the markdown its section takes: a bullet list for the list
    fields, markdown-safed prose otherwise. Empty when the caller supplied nothing."""
    if key in ("options", "acs"):
        items = _list(f, key)
        return "".join(f"- **{o}**\n" for o in items) if items else ""
    val = f.get(key)
    return f"{file_finding._prose_safe(val)}\n" if isinstance(val, str) and val.strip() else ""


def _put_section(body: str, names: tuple[str, ...], content: str) -> str:
    """Replace the body of the first section named in `names` with `content`, or append the
    section (before Revision History) when the template carries no such heading.

    Only the PROSE body above the first `###` subsection is replaced: a template's `###`
    scaffold prompts (a bug's `### Files Modified`/`### Tests Added`, an RFC's `### Option A`)
    survive when the caller supplies the parent field, so an agent filling the artefact keeps
    the guidance rather than having the supplied content silently swallow it."""
    for name in names:
        m = re.search(rf"^##\s+{re.escape(name)}\b.*$", body, re.M | re.I)
        if not m:
            continue
        rest = body[m.end():]
        # Stop at the first `###` subsection or the next `##` heading, whichever comes first -
        # the prose above the first subsection is replaced; the subsections beneath it are kept.
        nxt = re.search(r"^(?:##|###)\s", rest, re.M)
        tail = rest[nxt.start():] if nxt else ""
        return f"{body[:m.end()]}\n\n{content}\n{tail}"
    section = f"## {names[0]}\n\n{content}"
    m = _REV_SECTION_RE.search(body)
    return f"{body[:m.start()]}{section}\n{body[m.start():]}" if m \
        else f"{body.rstrip()}\n\n{section}"


def _fill_content(body: str, type_: str, f: dict) -> str:
    """Land the content the caller HAS in the grafted template. The graft leaves every
    unsupplied slot as a `{{placeholder}}` for the agent, but supplied content must reach the
    artefact - otherwise a batch that names its criteria still mints a scaffold the validator
    rejects, which is how a decomposition ends up hand-stamping thirty files."""
    for key, names in _CONTENT_SECTIONS:
        content = _rendered(key, f)
        if content:
            body = _put_section(body, names, content)
    return _fill_impact(_fill_acs(body, type_, f), type_, f)


def _graft(minimal: str, core_path: Path, type_: str = "", f: dict | None = None) -> str:
    """The deterministic provenance head (identical to minimal, so validate/
    provenance behave the same) followed by the section body of `core_path`.
    Unsupplied placeholders stay unresolved for the agent. Falls back to minimal when the
    template has no `## ` section body to graft."""
    if "\n## " not in minimal or not core_path.exists():
        return minimal
    # provenance + metadata block. rstrip the trailing newline the metadata block ends on, or
    # the join below stacks a second blank line before the first heading (MD012).
    head = minimal[:minimal.index("\n## ")].rstrip("\n")
    core = re.sub(r"^<!--.*?-->\n+", "", core_path.read_text(encoding="utf-8"),
                  count=1, flags=re.DOTALL)
    lines = core.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), None)
    if start is None:  # no section body to graft - keep minimal
        return minimal
    body = "\n".join(lines[start:]).rstrip()
    # rstrip again: a section appended at the end of the body must not leave a trailing
    # blank line once the file's closing newline is added (MD012).
    return f"{head}\n\n{_fill_content(body, type_, f or {}).rstrip()}\n"


def _render_full(type_: str, disp: str, title: str, today: str, f: dict) -> str:
    """`--template full`: minimal head + the rich body from `templates/core/<type>.md`."""
    return _graft(_render(type_, disp, title, today, f), _core_template(type_), type_, f)


def _render_planning(type_: str, disp: str, title: str, today: str, f: dict) -> str:
    """`--template planning`: the lean pre-implementation body, plus the tier stamp that
    tells the transition gate this story owes a promotion before it can be implemented."""
    f = {**f, "_tier": PLANNING}
    return _graft(_render(type_, disp, title, today, f), _planning_template(type_), type_, f)


def _select_render(root: Path, type_: str, template: str | None):
    """The renderer for one scaffold: a project-declared template
    (conventions.templates.<type>) wins over --template minimal/planning/full so the
    scaffold matches the house shape the read-side checks expect; declared but
    missing fails loud rather than silently falling back to the skill shape."""
    proj = conventions.template_for(type_, root)
    if proj is not None:
        if not proj.exists():
            raise conventions.ConventionsError(
                f"conventions.templates.{type_} declares {proj}, which does not exist")
        return lambda t, disp, title, today, f: _graft(
            _render(t, disp, title, today, f), proj, t, f)
    if template == FULL:
        return _render_full
    return _render_planning if template == PLANNING else _render


def _skill_root() -> Path:
    """The skill directory (…/sdlc-studio/), where templates live - this script is in scripts/."""
    return Path(__file__).resolve().parent.parent


def _index_template(type_: str) -> Path:
    return file_finding.index_template_path(type_)


def _ensure_index(root: Path, type_: str, today: str) -> bool:
    """Create a missing `<dir>/_index.md` on the empty-project first run.
    Delegates to the shared `file_finding.ensure_index` (also used by `init`)."""
    return file_finding.ensure_index(root, type_, today)


def _header_cells(root: Path, type_: str) -> list[str] | None:
    idx = Path(root) / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not idx.exists():
        return None
    found = sdlc_md.find_data_header(idx.read_text(encoding="utf-8").splitlines())
    return found[1] if found else None


def _find_epic(root: Path, epic_id: str) -> Path | None:
    """The epic file whose id matches exactly (never a substring: EP001 != EP0010). Uses the
    era-aware `extract_record_id`: `split('-')[0]` yielded just `EP` for a v3 ULID filename
    (`EP-01JQK3F8-reading.md`), so story-to-epic wiring failed on the default schema."""
    eid = sdlc_md.norm_id(epic_id)
    return next((p for p in sdlc_md.artifact_files("epic", Path(root))
                 if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == eid), None)


def _wire_story_to_epic(root: Path, epic_id: str, disp: str, title: str,
                        file_id: str, slug: str) -> bool:
    """Append the story to its parent epic's Story Breakdown (idempotent)."""
    ep = _find_epic(root, epic_id)
    if ep is None:
        return False
    text = ep.read_text(encoding="utf-8")
    line = f"- [ ] [{disp}: {title}](../stories/{file_id}-{slug}.md)"
    if f"[{disp}:" in text or f"[{disp}]" in text:  # already wired (exact, not substring: US0001 != US00012)
        return True
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().lower().startswith("## story breakdown"):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("## "):
                j += 1
            # Insert after the LAST list item, preserving the section's existing structure
            # (prose, internal blanks) - a full rebuild would collapse blanks and orphan a
            # list against neighbouring prose (MD032). Only an item-less section is rebuilt.
            last_item = max((k for k in range(i + 1, j)
                             if lines[k].strip().startswith("- [")), default=None)
            if last_item is not None:
                lines.insert(last_item + 1, line)
                nxt = last_item + 2  # guard: a blank before the next heading (no orphan)
                if nxt < len(lines) and lines[nxt].lstrip().startswith("## "):
                    lines.insert(nxt, "")
            else:  # empty section (e.g. "_No stories yet._") - rebuild cleanly
                keep = [lines[k] for k in range(i + 1, j)
                        if lines[k].strip() and not lines[k].strip().startswith("_No stories")]
                lines[i:j] = [lines[i], ""] + keep + [line, ""]
            ep.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False


# Meta-artifacts: tool-created, outside the status machinery (no status vocab, no
# transition gate, no conformance stage). A handoff belongs here for the same reason a
# retro does - it is a generated record OF a run, not a unit of work that moves through one.
META = ("retro", "review", "handoff")


def _render_meta(type_: str, disp: str, title: str, today: str, f: dict | None = None) -> str:
    """Retro renders from the shipped retro template (id/title/date filled, the
    rest left as authoring scaffold); review gets a minimal findings scaffold; a handoff
    renders the GENERATED body its caller supplies (there is no authoring scaffold to
    fill - every section is derived from the run, and an unsupplied body says so plainly
    rather than leaving a placeholder nothing will ever substitute)."""
    f = f or {}
    if type_ == "handoff":
        meta = "".join(f"> **{k}:** {v}\n" for k, v in (f.get("meta") or []))
        body = f.get("body") or (
            "## Where to pick up\n\n_Not generated._ A handoff is a JOIN over the run's own "
            "evidence: run `handoff generate` at the close so this document names what "
            "remains, with each item's pointer and suitability tag.\n")
        return (f"# {disp}: {title}\n\n> **Date:** {today}\n"
                f"> **Created-by:** sdlc-studio new\n{meta}\n{body}"
                f"\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"| {today} | sdlc-studio | Generated at the run close (`handoff generate`) |\n")
    if type_ == "retro":
        tmpl = Path(__file__).resolve().parent.parent / "templates" / "reviews" / "retro.md"
        if tmpl.exists():
            text = tmpl.read_text(encoding="utf-8")
            text = re.sub(r"^<!--.*?-->\n+", "", text, count=1, flags=re.DOTALL)
            text = text.replace("RETRO-{{retro_id}}", disp)
            text = text.replace("{{sprint_title}}", title).replace("{{date}}", today)
            return text
    return (f"# {disp}: {title}\n\n> **Date:** {today}\n"
            f"> **Created-by:** sdlc-studio new\n\n"
            f"## Scope\n\n{{{{scope}}}}\n\n## Findings\n\n{{{{findings}}}}\n\n"
            f"## Verdict\n\n{{{{verdict}}}}\n\n"
            f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            f"| {today} | {{{{author}}}} | Created via `new` (deterministic) |\n")


def _ensure_meta_index(root: Path, rel: str, type_: str, today: str) -> bool:
    """Create `<rel>/_index.md` from `templates/indexes/<type>.md` when it is missing, so a
    project's FIRST retro/review/handoff is INDEXED rather than a missing-index reconcile
    drift item the operator then clears by hand. Delegates to `file_finding.write_empty_index`,
    the one index-writer that also backs `file_finding.ensure_index` (pipeline types), so a
    meta index is rendered identically to a pipeline one - carrying the same blank-collapse.
    Idempotent; never clobbers an existing index. Returns True iff it created the file."""
    idx = root / rel / "_index.md"
    tmpl = _skill_root() / "templates" / "indexes" / f"{type_}.md"
    return file_finding.write_empty_index(idx, tmpl, today)


def meta_new(repo_root: Path | str, type_: str, title: str, fields: dict | None = None,
             dry_run: bool = False) -> dict:
    """Create a retro/review: allocated id, rendered file, and an index row. The meta index is
    bootstrapped on the first create when missing (retros/, reviews/, handoffs/), so a
    project's first retro/review lands indexed rather than as reconcile drift; a project that
    has deleted its index still gets one re-seeded, and the row is appended to it."""
    if type_ not in META:
        raise ValueError(f"unknown meta type {type_!r} (expected {'|'.join(META)})")
    import next_id
    root = Path(repo_root)
    f = dict(fields or {})
    sdlc_md.check_creator_fields({**f, "title": title})  # refuse an injected line before any write
    today = f.get("date") or date.today().isoformat()
    # Serialise allocate -> collision-check -> write -> index-append against concurrent
    # writers (retro/review/handoff ids are always sequential, the case the lock most
    # matters for), so two waves closing at once never mint the same id or clobber the index.
    with sdlc_md.allocation_lock(root):
        n = next_id.allocate_number(type_, root)
        rel, prefix = next_id.META_TYPES[type_]
        file_id = f"{prefix}{n:04d}"
        disp = f"{prefix}-{n:04d}"
        slug = file_finding._slug(title)
        path = root / rel / f"{file_id}-{slug}.md"
        if path.exists():
            raise FileExistsError(path)
        if dry_run:
            # Predict indexing honestly (like new()'s dry-run): a row lands when the meta index
            # exists with a data header, OR would be bootstrapped from a shipped index template.
            idx = root / rel / "_index.md"
            has_header = idx.exists() and sdlc_md.find_data_header(
                idx.read_text(encoding="utf-8").splitlines()) is not None
            would_bootstrap = (not idx.exists()) and (
                _skill_root() / "templates" / "indexes" / f"{type_}.md").exists()
            return {"id": disp, "file_id": file_id, "path": str(path),
                    "indexed": has_header or would_bootstrap,
                    "epic_linked": None, "dry_run": True}
        path.parent.mkdir(parents=True, exist_ok=True)
        sdlc_md.atomic_write(path, _render_meta(type_, disp, title, today, f))
        _ensure_meta_index(root, rel, type_, today)  # bootstrap the meta index on first use
        indexed = False
        index_path = root / rel / "_index.md"
        if index_path.exists():
            lines = index_path.read_text(encoding="utf-8").splitlines()
            hdr = sdlc_md.find_data_header(lines)
            if hdr is not None:
                row = sdlc_md.row_from_header(hdr[1], f"[{disp}]({file_id}-{slug}.md)", title,
                                              "--", {"date": today, **f})
                # bound the scan to the DATA table itself: stop at the first
                # non-table line so a later link-first table never attracts the row
                pos = hdr[0] + 2  # past header + separator
                j = pos
                while j < len(lines) and lines[j].strip().startswith("|"):
                    j += 1
                pos = j
                lines.insert(pos, row)
                sdlc_md.atomic_write(index_path, "\n".join(lines) + "\n")
                indexed = True
    return {"id": disp, "file_id": file_id, "path": str(path), "indexed": indexed,
            "epic_linked": None, "dry_run": False}


def new(repo_root: Path | str, type_: str, title: str, fields: dict | None = None,
        dry_run: bool = False) -> dict:
    if type_ not in SPEC:
        raise ValueError(f"unknown type {type_!r} (expected one of {', '.join(SPEC)})")
    root = Path(repo_root)
    f = dict(fields or {})
    # Refuse a field that would break out of its metadata line, index cell or bullet BEFORE
    # anything is allocated or written - a half-created artefact carrying injected lines is
    # worse than no artefact. One guard, every field, at the top of the one create path.
    sdlc_md.check_creator_fields({**f, "title": title})
    # A CR/bug criterion is prose: refuse a command-shaped `Verify:` written into it, from the
    # SAME authority the filer uses, so the two creation paths cannot disagree about what a
    # CR/bug acceptance criterion means (nothing executes it - only a story's Verify line runs).
    file_finding.check_prose_acs(type_, f)
    f["date"] = f.get("date") or date.today().isoformat()
    # A bug or a CR created here is a unit `sprint plan` will be asked to plan, and this is a
    # documented create path - not a side door. So it answers to the SAME grooming demand as the
    # finding filer, from the same authority: the body about to be written is judged by the
    # planner's own `breakdown` predicate, and refused here if the planner would refuse it there.
    if type_ in file_finding.GROOMED_TYPES:
        preview = _select_render(root, type_, f.get("template"))
        file_finding.check_groomed(root, type_, preview(type_, "PREVIEW", title, f["date"], f))
    if type_ == "story":
        if not f.get("epic"):
            # Lite profile has no epic layer: a story sits directly under the PRD. Every
            # other profile keeps the epic mandatory so no story is silently orphaned.
            if sdlc_md.profile(root) != "lite":
                raise ValueError("a story needs --epic <EPxxxx>")
        elif _find_epic(root, f["epic"]) is None:
            # Fail fast before writing - a story wired to a non-existent epic is an orphan whose
            # dangling link only surfaces at the next integrity run.
            raise ValueError(f"epic {f['epic']} not found - create it first, or fix the id")
        _target_of(f)      # refuse an unknown target / multi-line Verify BEFORE any write,
        _verifiers_of(f)   # so a bad field never half-creates an artefact
    # Serialise allocate -> collision-check -> write -> index-append against concurrent
    # writers, so two agents in one wave never mint the same id or clobber the index.
    with sdlc_md.allocation_lock(root):
        file_id, disp = _alloc_ids(root, type_)
        slug = file_finding._slug(title)
        path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / f"{file_id}-{slug}.md"
        if path.exists():
            raise FileExistsError(path)
        # Triage noise controls (v3 findings only, dormant on v2): a Low-severity finding folds
        # into a themed consolidation CR; the session cap refuses a flood loudly. Routed here too
        # so `artifact new` is not a bypass of the file_finding path.
        sev = f.get("severity") or f.get("priority")
        if type_ in sdlc_md.FINDING_TYPES and triage_noise.should_consolidate(root, sev):
            if dry_run:
                return {"id": None, "file_id": None, "path": None,
                        "consolidated": True, "dry_run": True}
            res = triage_noise.consolidate_low_finding(root, type_, title, f, f["date"])
            res.setdefault("indexed", True)
            return res
        if dry_run:  # preview: write nothing, report what would happen
            idx_exists = _header_cells(root, type_) is not None
            would_create_index = (not idx_exists) and _index_template(type_).exists()
            return {"id": disp, "file_id": file_id, "path": str(path),
                    "indexed": idx_exists or would_create_index,
                    "would_create_index": would_create_index,
                    "epic_linked": (type_ == "story" and bool(f.get("epic"))) or None,
                    "dry_run": True}
        if type_ in sdlc_md.FINDING_TYPES:
            triage_noise.enforce_session_cap(root)  # refuse the N+1th finding loudly (v3)
        f["_status"] = _create_status(type_, root)  # era-aware: findings file into inbox under v3
        f["_raised_by"] = sdlc_md.authorship_value(f.get("author"), root)
        # The index Author column takes the resolved NAME, exactly as the filer's does: two
        # creators, one column, one behaviour - never the raw triple, never a discarded identity.
        f["author"] = sdlc_md.authorship_name(f["_raised_by"])
        render = _select_render(root, type_, f.get("template"))
        body = render(type_, disp, title, f["date"], f)
        prov = str(f.get("provenance") or "").strip()
        if prov:
            # The trust-boundary stamp the verify_ac shell gate reads: an ingested artefact
            # (e.g. created --from-issue) carries its origin mechanically, on EVERY render
            # path, so the control has a writer - not just prose. Inserted after Created-by.
            body = re.sub(r"(^> \*\*Created-by:\*\*.*$)",
                          rf"\1\n> **Provenance:** {prov}", body, count=1, flags=re.MULTILINE)
        sdlc_md.atomic_write(path, body)
        if type_ in sdlc_md.FINDING_TYPES:
            triage_noise.record_creation(root)  # count this minted finding (session budget)
        index_created = _ensure_index(root, type_, f["date"])  # greenfield first run
        header = _header_cells(root, type_)
        indexed = False
        if header:
            row = sdlc_md.row_from_header(header, f"[{disp}]({file_id}-{slug}.md)", title,
                                          f["_status"], f)
            indexed = file_finding.append_index_row(root, type_, row)
        linked = _wire_story_to_epic(root, f["epic"], disp, title, file_id, slug) \
            if (type_ == "story" and f.get("epic")) else None
    return {"id": disp, "file_id": file_id, "path": str(path),
            "indexed": indexed, "index_created": index_created,
            "epic_linked": linked, "dry_run": False}


def new_batch(repo_root: Path | str, type_: str, items: list[dict],
              template: str = "full", dry_run: bool = False) -> dict:
    """Create many artifacts of one type in a single atomic pass.

    Reserve a contiguous id block up front (LL0002: reserve before writing), render each
    file (full template by default - batch is the fan-out case where structure must be
    guaranteed), append every index row, and wire each story into its parent epic - one pass.
    All-or-nothing: a missing epic or a file collision aborts before any write. `--dry-run`
    returns the full id map and planned wiring."""
    if type_ not in SPEC:
        raise ValueError(f"unknown type {type_!r}")
    root = Path(repo_root)
    today = date.today().isoformat()
    if not items:
        raise ValueError("batch is empty")
    # Validate the whole batch BEFORE writing anything (atomic) - a story wired to a
    # missing epic is an orphan; a colliding id would corrupt the run.
    groom_preview = (_select_render(root, type_, template)
                     if type_ in file_finding.GROOMED_TYPES else None)
    for i, it in enumerate(items, 1):
        try:  # an injected line in item N aborts the batch here, before any id is reserved
            sdlc_md.check_creator_fields(it)
            file_finding.check_prose_acs(type_, it)  # ... as does a pseudo-`Verify:` criterion
            if groom_preview is not None:  # ... as does a bug/CR the planner would refuse to plan
                file_finding.check_groomed(root, type_, groom_preview(
                    type_, "PREVIEW", str(it.get("title") or ""), today, {**it, "date": today}))
        except ValueError as exc:
            raise ValueError(f"batch item {i}: {exc}") from exc
    if type_ == "story":
        for it in items:
            if not it.get("epic"):
                raise ValueError("each story item needs an 'epic'")
            if _find_epic(root, it["epic"]) is None:
                raise ValueError(f"epic {it['epic']} not found - create it first")
            _target_of(it)      # a bad target or Verify in item N must abort the whole
            _verifiers_of(it)   # batch here, not after items 1..N-1 are already on disk
    # CR0183/BG0076: allocate the id block + write all files under the advisory lock,
    # so a concurrent `new`/`new_batch` cannot mint an overlapping id block.
    with sdlc_md.allocation_lock(root):
        v3 = _schema_v3(root)
        create_status = _create_status(type_, root)  # era-aware: findings file into inbox under v3
        n0 = None if v3 else file_finding._next_number(root, type_)
        prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
        d = root / sdlc_md.ARTIFACT_TYPES[type_][0]
        taken: set[str] = set()  # ids minted earlier in THIS batch (before any file is written)
        plan = []
        for i, it in enumerate(items):
            if not it.get("title"):
                raise ValueError("each item needs a 'title'")
            if v3:
                for _ in range(16):
                    file_id = f"{prefix}-{sdlc_md.short_ulid()}"
                    if file_id not in taken and not (d.exists() and any(d.glob(f"{file_id}-*.md"))):
                        break
                else:
                    file_id = f"{prefix}-{sdlc_md.new_ulid()[:12]}"
                taken.add(file_id)
                n, disp = None, file_id
            else:
                n = n0 + i
                file_id = f"{prefix}{n:04d}"
                disp = _disp(type_, n)
            slug = file_finding._slug(it["title"])
            path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / f"{file_id}-{slug}.md"
            if path.exists():
                raise FileExistsError(f"{path} (batch aborted, nothing written)")
            plan.append({"n": n, "file_id": file_id, "disp": disp,
                         "slug": slug, "path": path, "item": it})
        if dry_run:
            return {"type": type_, "count": len(plan), "template": template, "dry_run": True,
                    "ids": [{"id": p["disp"], "path": str(p["path"]),
                             "epic": p["item"].get("epic")} for p in plan]}
        render = _select_render(root, type_, template)
        _ensure_index(root, type_, today)
        created = []
        for p in plan:
            it = p["item"]
            f = dict(it)
            f["date"] = today
            f["_status"] = create_status
            f["_raised_by"] = sdlc_md.authorship_value(f.get("author"), root)
            f["author"] = sdlc_md.authorship_name(f["_raised_by"])  # index cell: the name
            p["path"].parent.mkdir(parents=True, exist_ok=True)
            sdlc_md.atomic_write(p["path"], render(type_, p["disp"], it["title"], today, f))
            header = _header_cells(root, type_)
            link = f"[{p['disp']}]({p['file_id']}-{p['slug']}.md)"
            if header:
                row = sdlc_md.row_from_header(header, link, it["title"], create_status, f)
                file_finding.append_index_row(root, type_, row)
            if type_ == "story":
                _wire_story_to_epic(root, it["epic"], p["disp"], it["title"], p["file_id"], p["slug"])
            created.append({"id": p["disp"], "file_id": p["file_id"], "path": str(p["path"])})
        return {"type": type_, "count": len(created), "template": template,
                "created": created, "dry_run": False}


def infer_type_from_id(artifact_id: str) -> str | None:
    """Artifact type from an id's LEADING alpha prefix (`BG0007`, `CR-0003`, and the v3
    `BG-01JQK3F8` all yield `BG`). Collecting every alpha character breaks on ULIDs, whose
    random tail contains letters."""
    m = re.match(r"[A-Za-z]+", artifact_id.strip())
    return _PREFIX_TYPE.get(m.group(0).upper()) if m else None


def close(repo_root: Path | str, artifact_id: str, status: str | None = None,
          metrics: dict | None = None, dry_run: bool = False, force: bool = False,
          triaged_by: str | None = None) -> dict:
    """Terminal-transition an artifact and cascade (reuse transition), then record a
    telemetry event. Telemetry is advisory - it never affects the
    close result (the recorder swallows its own failures). `force` bypasses the story->Done
    AC-verify gate; it is inert for non-story types."""
    type_ = infer_type_from_id(artifact_id)
    if type_ is None:
        raise ValueError(f"cannot infer type from id {artifact_id!r}")
    # The default close target comes from the shared vocab authority, not from a table this
    # module keeps - so `close` and the vocab can never disagree about what closed means.
    st = status or sdlc_md.default_terminal_status(type_)
    if dry_run:  # preview the transition target, write nothing, record nothing
        return {"id": artifact_id, "type": type_, "to": st, "dry_run": True}
    # transition records one telemetry event on entering the terminal set (and none on an
    # idempotent re-close); pass the metrics through so close does not double-record.
    return transition.transition(repo_root, artifact_id, st, force=force,
                                 metrics=metrics, triaged_by=triaged_by)


_SECTION_SPLIT_RE = re.compile(r"^(##\s+.*)$", re.M)


def _tier_of(text: str) -> str | None:
    """The artefact's declared template tier - one authority (lib.tiers)."""
    return tiers.tier_of(text)


def _sections(text: str) -> list[tuple[str, str]]:
    """(heading text, block) for every `## ` section, in document order. A block runs to the
    next `## ` heading, with the template's horizontal-rule separators trimmed - promotion
    joins blocks with a blank line, so a stray `---` would render as a rule mid-document."""
    out: list[tuple[str, str]] = []
    parts = _SECTION_SPLIT_RE.split(text)
    for i in range(1, len(parts), 2):
        head = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        block = f"{head}{body}".rstrip()
        while block.endswith("---"):  # drop the trailing rule (and the blank line above it)
            block = block[: -len("---")].rstrip()
        out.append((head[2:].strip(), block))
    return out


def _head_key(heading: str) -> str:
    return heading.strip().lower()


def promote(repo_root: Path | str, artifact_id: str, to: str = FULL) -> dict:
    """Promote a planning-tier artefact to the full tier.

    Every `## ` section the full template mandates and this artefact does not yet carry is
    grafted in, in template order, with everything already written preserved verbatim; the
    tier stamp is then re-cut to `full`. This is the remedy the transition gate names: a lean
    story reaches implementation by GAINING the sections it was allowed to defer (the
    constraint chain, edge cases, test scenarios, the rollback envelope), never by having the
    gate waived. Idempotent - an artefact that is not planning-tier is already promoted and is
    left untouched."""
    if to != FULL:
        raise ValueError(f"promote --to {to!r}: the only promotion target is {FULL!r}")
    root = Path(repo_root)
    hit = sdlc_md.find_by_id(root, artifact_id)
    if hit is None:
        raise ValueError(f"no artifact found for id {artifact_id!r}")
    path, type_ = hit
    text = path.read_text(encoding="utf-8")
    tier = _tier_of(text)
    # Promotion is owed whenever the artefact declares the planning tier OR is missing sections
    # the full tier carries - which is also the remedy for an artefact whose `full` stamp was
    # rewritten without the work. Nothing to add and nothing to correct is already promoted.
    if tier != PLANNING and not tiers.missing_sections(text, type_):
        return {"id": artifact_id, "type": type_, "path": str(path), "from": tier or FULL,
                "to": tier or FULL, "promoted": False, "added": []}
    core = _core_template(type_)
    if not core.exists():
        raise ValueError(f"no full template for type {type_!r} - nothing to promote into")
    core_body = re.sub(r"^<!--.*?-->\n+", "", core.read_text(encoding="utf-8"),
                       count=1, flags=re.DOTALL)
    head = text[: text.index("\n## ")] if "\n## " in text else text.rstrip()
    have = {_head_key(h): b for h, b in _sections(text)}
    tmpl = _sections(core_body)
    tmpl_keys = {_head_key(h) for h, _ in tmpl}
    # sections this artefact has that the template does not know about (an agent's own
    # additions) keep their place ahead of the revision log rather than being pushed past it
    extra = [b for h, b in _sections(text) if _head_key(h) not in tmpl_keys]
    blocks: list[str] = []
    added: list[str] = []
    for heading, block in tmpl:
        key = _head_key(heading)
        if key == "revision history":
            blocks.extend(extra)
            extra = []
        if key in have:
            blocks.append(have[key])
        else:
            blocks.append(block)
            added.append(heading)
    blocks.extend(extra)  # a template with no revision log - keep the additions at the end
    body = "\n\n".join(b for b in blocks if b.strip())
    new_text = transition._upsert_field(f"{head.rstrip()}\n\n{body}\n", TIER_FIELD, FULL)
    sdlc_md.atomic_write(path, new_text)
    return {"id": artifact_id, "type": type_, "path": str(path), "from": tier or MINIMAL,
            "to": FULL, "promoted": True, "added": added}


def cmd_promote(args: argparse.Namespace) -> int:
    r = promote(args.root, args.id, to=args.to)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    elif r["promoted"]:
        print(f"promoted {r['id']} {r['from']} -> {r['to']} "
              f"({len(r['added'])} section(s) added: {', '.join(r['added']) or 'none'})")
    else:
        print(f"{r['id']} is already {r['to']}-tier - nothing to promote")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    f = {k: v for k, v in {"epic": args.epic, "priority": args.priority, "ctype": args.ctype,
                           "severity": args.severity, "author": args.author,
                           "template": args.template, "persona": args.persona,
                           "summary": args.summary, "steps": args.steps, "fix": args.fix,
                           "impact": args.impact, "points": args.points,
                           "size": args.size,
                           "affects": args.affects,
                           "acs": args.ac, "verify": args.verify, "target": args.target,
                           "options": args.option,
                           "recommendation": args.recommendation,
                           "provenance": getattr(args, "provenance", None)}.items() if v}
    try:
        if args.type in META:
            r = meta_new(args.root, args.type, args.title, f, dry_run=args.dry_run)
        else:
            r = new(args.root, args.type, args.title, f, dry_run=args.dry_run)
    except conventions.ConventionsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    verb = "would create" if r.get("dry_run") else "created"
    if args.format == "json":
        print(json.dumps(r, indent=2))
    elif r.get("consolidated") or r.get("consolidated_into"):
        # a Low finding folded into a themed consolidation CR - its result has its own shape
        # (no epic wiring, no per-finding index row), so print it by that shape
        if r.get("dry_run"):
            print("would consolidate this Low finding into a themed CR (no artefact minted)")
        else:
            print(f"consolidated into {r['consolidated_into']} "
                  f"({Path(r['path']).name}, created={bool(r.get('created'))})")
    else:
        print(f"{verb} {r['id']} -> {r['path']} "
              f"(indexed={r.get('indexed')}, epic_linked={r.get('epic_linked')})")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    items = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if not isinstance(items, list):
        print("error: --spec must be a JSON list of items", file=sys.stderr)
        return 1
    try:
        r = new_batch(args.root, args.type, items, template=args.template, dry_run=args.dry_run)
    except conventions.ConventionsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0
    verb = "would create" if r.get("dry_run") else "created"
    print(f"batch: {verb} {r['count']} {args.type}(s) (template={r['template']})")
    for row in (r.get("ids") or r.get("created") or []):
        print(f"  {row['id']} -> {row['path']}")
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    # Orchestrated close (one call = stamp + verdict + transition): every step is durable,
    # so a refusal at the transition leaves the stamp/verdict recorded and a re-run
    # completes. NOTE a re-run appends a fresh verdict row (append-only audit log,
    # latest-wins for gates) - clear the refusal before retrying to keep the log tight.
    # Self-review refuses BEFORE any write.
    depth = getattr(args, "depth", None)
    reviewer = getattr(args, "reviewer", None)
    author = getattr(args, "author", None)
    if reviewer or author:
        if not (reviewer and author and args.verdict):
            print("error: orchestrated close needs --verdict, --reviewer AND --author "
                  "(or none of reviewer/author for the plain close)", file=sys.stderr)
            return 2
        import critic
        if critic._id(reviewer) == critic._id(author):
            print("error: reviewer == author - independence is the floor; a self-review "
                  "never clears the critiqued gate, so nothing was written", file=sys.stderr)
            return 2
    if depth and not args.dry_run:
        transition.annotate(args.root, args.id, "Verification depth", depth)
    if reviewer and not args.dry_run:
        import critic
        critic.record_verdict(args.root, args.id, args.verdict, reviewer, author,
                              issues=getattr(args, "issues", "") or "")
    metrics = {}
    if args.iterations is not None:
        metrics["iterations"] = int(args.iterations)
    if args.verdict:
        metrics["critic_verdict"] = args.verdict
    if args.wall_time_s is not None:
        metrics["wall_time_s"] = int(args.wall_time_s)
    if args.stages:
        metrics["stages"] = args.stages
    r = close(args.root, args.id, args.status, metrics or None, dry_run=args.dry_run,
              force=getattr(args, "force", False),
              triaged_by=getattr(args, "triaged_by", None))
    verb = "would close" if r.get("dry_run") else "closed"
    print(json.dumps(r, indent=2) if args.format == "json" else f"{verb} {args.id}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic artifact create + close.")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="Create + wire any numbered artifact.")
    n.add_argument("--type", required=True, choices=tuple(SPEC) + META)
    n.add_argument("--title", required=True)
    n.add_argument("--epic", help="parent epic (required for a story)")
    n.add_argument("--priority")
    n.add_argument("--ctype", help="cr type")
    n.add_argument("--severity", help="bug severity")
    n.add_argument("--provenance",
                   help="origin stamp for ingested content (e.g. 'external' for a GitHub "
                        "issue body) - the verify_ac shell gate refuses shell/eval/http "
                        "verbs on externally-stamped artifacts")
    n.add_argument("--author",
                   help="authorship of record, stamped as `Raised-by`: 'Name; type; version' "
                        "(type is human|persona|agent) or a bare name; defaults to the "
                        "invoking agent (SDLC_AUTHOR when set)")
    # Content the validator demands of a filled artefact. Supply it here and the artefact is
    # born clean; omit it and the scaffold keeps the slot for the agent to fill.
    n.add_argument("--persona", help="story: the persona it serves")
    n.add_argument("--summary", help="the Summary/Overview section")
    n.add_argument("--steps", help="bug: steps to reproduce (the evidence a bug must carry)")
    n.add_argument("--fix", help="bug: proposed fix")
    n.add_argument("--impact", help="cr: who this affects and what breaks")
    # No argparse `choices`: a bare "invalid choice" teaches nothing, and the reason the scale
    # has no 7 is the whole lesson. `sdlc_md.check_points` - shared with the finding filer - is
    # what refuses it, with the scale in the message.
    n.add_argument("--points",
                   help="the job SIZE of a DELIVERY unit (a story or a bug) on the modified "
                        f"Fibonacci scale ({', '.join(str(p) for p in sdlc_md.POINTS_SCALE)}) - "
                        "RELATIVE to units already delivered, not its urgency and not a time "
                        "prediction. `sprint plan` refuses to plan a delivery unit nobody sized. "
                        "A value off the scale is refused, never rounded. A cr/rfc/epic takes "
                        "--size, not --points")
    n.add_argument("--size",
                   help="the T-shirt SIZE of a REQUEST or CONTAINER (a cr, rfc or epic) - "
                        f"{' / '.join(sdlc_md.SIZE_SCALE)} - sized coarsely before it is "
                        "decomposed into the delivery units that carry story points. A story or "
                        "bug takes --points, not --size")
    n.add_argument("--affects",
                   help="comma-separated files this unit will touch, written as the `Affects` "
                        "metadata line the planner reads. Required for a bug and a cr: "
                        "`sprint plan` refuses a unit that names no files - it cannot size one, "
                        "nor see two units colliding on the same file")
    n.add_argument("--ac", action="append", help="story/cr acceptance criterion (repeatable)")
    n.add_argument("--verify", action="append",
                   help="story: the executable check for the AC in the same position "
                        "(repeatable; pairs with --ac). Omit it and the AC carries no Verify "
                        "line - which conformance reports, rather than inventing one")
    n.add_argument("--target", choices=("functional", "conversational", "soak", "live"),
                   help="story: the Verification target tier written on each supplied AC")
    n.add_argument("--option", action="append", help="rfc design option (repeatable)")
    n.add_argument("--recommendation", help="rfc: the recommended option")
    n.add_argument("--template", choices=TEMPLATE_TIERS, default=MINIMAL,
                   help="scaffold richness: minimal (default); planning (story/epic: ACs with "
                        "Verify + Verification target, scope, technical notes - no "
                        "implementation furniture, and `promote` is required before an "
                        "implementation status); or the full templates/core body")
    n.add_argument("--root", default=".")
    n.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    n.add_argument("--format", choices=("text", "json"), default="text")
    n.set_defaults(func=cmd_new)
    b = sub.add_parser("batch", help="Create many artifacts of one type in one atomic pass.")
    b.add_argument("--type", required=True, choices=tuple(SPEC))
    b.add_argument("--spec", required=True, help="JSON file: a list of {title, epic?, ...} items")
    b.add_argument("--template", choices=TEMPLATE_TIERS, default=FULL,
                   help="batch defaults to full (the fan-out case); --template planning is the "
                        "lean pre-implementation tier for a decomposition; minimal opts out")
    b.add_argument("--root", default=".")
    b.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview the id map; write nothing")
    b.add_argument("--format", choices=("text", "json"), default="text")
    b.set_defaults(func=cmd_batch)
    c = sub.add_parser("close", help="Terminal-transition an artifact + cascade + record telemetry.")
    c.add_argument("--id", required=True)
    c.add_argument("--status", help="override the per-type terminal status")
    c.add_argument("--force", action="store_true",
                   help="bypass the story->Done AC-verify gate (inert for non-stories)")
    c.add_argument("--iterations", help="run metric: iterations to green (telemetry)")
    c.add_argument("--verdict", help="run metric: critic verdict (telemetry)")
    c.add_argument("--wall-time-s", dest="wall_time_s", help="run metric: wall time (telemetry)")
    c.add_argument("--stages", help="run metric: stages passed (telemetry)")
    c.add_argument("--depth", help="orchestrated close: stamp '> **Verification depth:**' "
                                   "before transitioning (no more hand edits)")
    c.add_argument("--reviewer", help="orchestrated close: record the critic verdict under "
                                      "this reviewer (must differ from --author)")
    c.add_argument("--author", help="orchestrated close: the authoring seat the verdict "
                                    "judges (reviewer != author enforced up front)")
    c.add_argument("--issues", help="orchestrated close: critic verdict issues/tier note")
    c.add_argument("--triaged-by", dest="triaged_by",
                   help="v3 finding close: the triaging seat as 'Name; type; version' - lets "
                        "the one-call close clear the inbox triage gate too")
    c.add_argument("--root", default=".")
    c.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_close)
    pr = sub.add_parser("promote", help="Promote a planning-tier artifact to the full "
                                        "template (adds the deferred sections; idempotent).")
    pr.add_argument("--id", required=True, help="Artifact id, e.g. US0023 / EP0007")
    pr.add_argument("--to", choices=(FULL,), default=FULL,
                    help="promotion target (full - the tier implementation requires)")
    pr.add_argument("--root", default=".")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_promote)
    r = sub.add_parser("revision", help="Append a dated Revision History row per id (batch).")
    sdlc_md.add_ids_argument(r, help_="artifact ids; repeat --id or pass --ids as one comma list")
    r.add_argument("--note", required=True, help="the Change cell text")
    r.add_argument("--author", help="the Author cell (default: sdlc)")
    r.add_argument("--date", help="override the Date cell (default: today)")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_revision)
    sdlc_md.add_global_root(p)
    return p


_REV_HEAD_RE = re.compile(r"^##\s+Revision History\s*$", re.MULTILINE)


def cmd_revision(args: argparse.Namespace) -> int:
    """Append one dated Revision History row per id - the deterministic
    close-out verb. A file without a Revision History section is refused
    loudly (never silently skipped); one refusal does not abort the batch."""
    import audit
    root = Path(args.root)
    today = args.date or date.today().isoformat()
    author = args.author or "sdlc"
    # The three cells this verb writes. Refused up front, once: they are the same for every id
    # in the batch, so a break in one would corrupt every row it touched.
    sdlc_md.check_creator_fields({"date": today, "author": author, "note": args.note})
    ids = sdlc_md.resolve_ids(args)
    if not ids:
        print("specify at least one id: --id (repeatable) or --ids as a comma list",
              file=sys.stderr)
        return 2
    refused = 0
    for rid in ids:
        found = audit.find_artifact(root, rid)
        if found is None:
            print(f"error: {rid}: no artifact file found", file=sys.stderr)
            refused += 1
            continue
        path, _type = found
        text = path.read_text(encoding="utf-8")
        m = _REV_HEAD_RE.search(text)
        if not m:
            print(f"error: {rid}: no '## Revision History' section in {path.name} "
                  f"- add the table before recording revisions", file=sys.stderr)
            refused += 1
            continue
        # append after the LAST table row of the section (contiguous | rows)
        lines = text.splitlines()
        head_ln = text[:m.start()].count("\n")
        j = head_ln + 1
        last_row = None
        while j < len(lines):
            s = lines[j].strip()
            if s.startswith("|"):
                last_row = j
            elif s.startswith("## ") or (last_row is not None and s and not s.startswith("|")):
                break
            j += 1
        if last_row is None:
            print(f"error: {rid}: Revision History section has no table in {path.name}",
                  file=sys.stderr)
            refused += 1
            continue
        row = sdlc_md.join_row([today, author, args.note])
        lines.insert(last_row + 1, row)
        path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""),
                        encoding="utf-8")
        print(f"revision recorded: {rid} ({path.name})")
    return 1 if refused else 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
