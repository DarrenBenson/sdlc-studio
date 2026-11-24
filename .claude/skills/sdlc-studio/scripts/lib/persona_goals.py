"""The one reader of a persona card's End goals, and the lint over the lines each one carries.

An End goal is a numbered line under the card's `## End Goals` heading (a Negative card's
`End Goals (stated to exclude)` too). A goal its author means to check carries its own lines,
nested (indented) beneath its number:

    1. A booking confirmed on the phone is still there after the app restarts
       - **Verify:** pytest tests/test_bookings.py::BookingTests::test_survives_restart
       - **Applies-to:** `app/bookings/`

Applies-to patterns are written in the TRD component dialect, the rule `sprint._component_names`
applies to a unit's TRD constraints: whole path segments, case-sensitive; a pattern ending `/`
names every file beneath that directory wherever it sits in the path, any other pattern the
path's trailing segments, with `*` inside one segment. `**` is not part of it, so the lint names
it rather than the shared matcher widening for one reader.

HTML comments and fenced code are skipped, so the template's commented example is never read as
one of a card's End goals. A `<!--` inside a fenced block or an inline code span opens no
comment. A numbered line still holding a `{{...}}` placeholder is not a goal, and nothing nested
under it is attached to the goal above. Nor is a nested line under an unindented paragraph that
follows a blank line, such as a `Notes:` paragraph: that paragraph ends the goal above it. A
goal's second nested Verify line is not read (the first stands) and is a finding.
"""
from __future__ import annotations

import re
from typing import Callable, NamedTuple

from . import sdlc_md

GOAL_VERIFY = "persona-goal-verify"
GOAL_SCOPE = "persona-goal-scope"

_SECTION_RE = re.compile(r"^##\s+End Goals\b", re.I)
_HEADING_RE = re.compile(r"^#{1,2}\s")
_GOAL_RE = re.compile(r"^\s*(\d+)[.)]\s+(.+?)\s*$")
_NESTED_RE = re.compile(r"^\s+[-*]\s+\*\*(Verify|Applies-to)(?::\*\*|\*\*:)\s*(.*?)\s*$", re.I)


class EndGoal(NamedTuple):
    """One End goal: its number as on the card, its text, its Verify expression (None when it
    carries no Verify line, else the first it carries), its Applies-to patterns (empty when it
    carries none) and any further Verify lines after the first (unread, linted as findings)."""
    number: str
    text: str
    verify: str | None
    applies_to: tuple[str, ...]
    extra_verifies: tuple[str, ...]


_CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)")


def _comment_open(text: str) -> int:
    """The index of the first `<!--` in `text` that is not inside an inline code span, or -1."""
    spans = [m.span() for m in _CODE_SPAN_RE.finditer(text)]
    start = text.find("<!--")
    while start >= 0:
        if not any(lo <= start < hi for lo, hi in spans):
            return start
        start = text.find("<!--", start + 4)
    return -1


def _visible_lines(text: str) -> list[str]:
    """The card's lines with HTML comments blanked out and fenced code dropped. A fence marker
    inside a comment is comment text; a `<!--` inside a fenced block or an inline code span is
    code text."""
    out: list[str] = []
    fence = None
    in_comment = False
    for line in text.splitlines():
        kept, rest = "", line
        if not in_comment:
            was_open = fence is not None
            fence, is_fence = sdlc_md.fence_step(line.lstrip(), fence)
            if is_fence or was_open:
                continue
        while rest:
            if in_comment:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    in_comment, rest = False, rest[end + 3:]
            else:
                start = _comment_open(rest)
                if start < 0:
                    kept, rest = kept + rest, ""
                else:
                    kept, rest, in_comment = kept + rest[:start], rest[start + 4:], True
        out.append(kept)
    return out


def _patterns(value: str) -> tuple[str, ...]:
    """The patterns an Applies-to line names: its backticked spans, or failing those the
    comma- or space-separated words."""
    ticked = re.findall(r"`([^`]+)`", value)
    words = ticked or re.split(r"[,\s]+", value)
    return tuple(w.strip() for w in words if w.strip())


def end_goals(text: str) -> list[EndGoal]:
    """Every End goal on the card, numbered as on the card, with the Verify and Applies-to lines
    nested under it."""
    raw: list[dict] = []
    inside = False
    current: dict | None = None
    after_blank = False
    for line in _visible_lines(text):
        if _HEADING_RE.match(line):
            inside, current = bool(_SECTION_RE.match(line)), None
            continue
        if not inside:
            continue
        if not line.strip():
            after_blank = True
            continue
        was_blank, after_blank = after_blank, False
        nested = _NESTED_RE.match(line)
        if nested:
            if current is not None:
                if nested.group(1).lower() == "verify":
                    if current["verify"] is None:
                        current["verify"] = nested.group(2)
                    else:
                        current["extra_verifies"] += (nested.group(2),)
                else:
                    current["applies_to"] += _patterns(nested.group(2))
            continue
        m = _GOAL_RE.match(line)
        if m:
            current = None
            if "{{" not in m.group(2):   # an unfilled template End goal is not one
                current = {"number": m.group(1), "text": m.group(2), "verify": None,
                           "applies_to": (), "extra_verifies": ()}
                raw.append(current)
        elif was_blank and not line[0].isspace():
            current = None   # an unindented paragraph after a blank line ends the goal above
    return [EndGoal(**g) for g in raw]


def _without_globstar(pattern: str) -> str:
    """The trailing-`/` form that names what a `**` pattern meant: the directory above its
    first `**` segment, or, for a leading `**`, the trailing segments after it."""
    segs = pattern.split("/")
    i = next(k for k, s in enumerate(segs) if s == "**" or "**" in s)
    head = "/".join(s for s in segs[:i] if s)
    if head:
        return head + "/"
    return "/".join(s for s in segs[i + 1:] if s) or "/"


def findings(goals: list[EndGoal], lint_verifier: Callable[[str], str | None]
             ) -> list[tuple[str, str, str]]:
    """`(rule, goal number, message)` for each End goal whose own lines are not in a form the
    tooling can read: a Verify that is empty, an unfilled placeholder or one `lint_verifier`
    (verify_ac's lint) flags, or a second Verify line; an Applies-to with no Verify to check it, or written with `**`."""
    out: list[tuple[str, str, str]] = []
    for g in goals:
        n = g.number
        if g.verify is not None:
            expr = g.verify.strip("`").strip()
            if not expr:
                out.append((GOAL_VERIFY, n, f"End goal {n}: its Verify line names no check"))
            elif "{{" in expr:
                out.append((GOAL_VERIFY, n, f"End goal {n}: its Verify `{expr}` is an unfilled "
                                            "template placeholder"))
            elif (nudge := lint_verifier(expr)):
                out.append((GOAL_VERIFY, n, f"End goal {n}: its Verify `{expr}` - {nudge}"))
        for extra in g.extra_verifies:
            out.append((GOAL_VERIFY, n, f"End goal {n}: a second Verify "
                                        f"`{extra.strip('`').strip()}` is not read; only its "
                                        f"first Verify `{(g.verify or '').strip('`').strip()}` "
                                        "is, so keep one Verify line per goal"))
        if g.applies_to and g.verify is None:
            out.append((GOAL_SCOPE, n, f"End goal {n}: Applies-to "
                                       f"{', '.join(f'`{p}`' for p in g.applies_to)} but no "
                                       "Verify, so no check covers the files it scopes"))
        for p in g.applies_to:
            if "**" in p:
                out.append((GOAL_SCOPE, n, f"End goal {n}: Applies-to `{p}` uses `**`, which the "
                                           "Applies-to dialect does not read (it matches one "
                                           f"literal segment); write `{_without_globstar(p)}` - "
                                           "a pattern ending `/` names every file beneath "
                                           "that directory"))
    return out
