#!/usr/bin/env python3
"""Check the specs' countable claims against a census of what the repo actually ships.

A skill-development CI tool (lives in tools/).

The TRD and TSD make claims a reader takes as fact: "60+ scripts", "50+ reference files".
Those were exact numbers once and went stale by about a fifth before anyone noticed, which is
why they are now growth-tolerant bands. A band still rots - it just rots downward, and it rots
silently, because nothing counts the tree and compares.

THE EXPECTED VALUE IS NEVER STORED. Every check counts the shipped set at run time, so the
number moves with the repo and adding or removing a script cannot put the guard out of date.
A guard carrying its own copy of the answer is a second place for the answer to be wrong.

An UNCHECKABLE claim is reported and fails, never skipped. A claim naming a census this tool
does not know, or carrying a number it cannot parse, is a claim nobody is checking - and a
silent skip is indistinguishable from a pass, which is the failure mode the whole tool exists
to remove.

Usage:
    python3 tools/check_spec_claims.py [--root DIR]

Exits non-zero on any contradicted or uncheckable claim.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_DIR = ".claude/skills/sdlc-studio"

#: The documents whose countable claims are held. A spec absent from the tree is not a failure -
#: a consuming project need not carry every one of them.
SPEC_FILES = ("sdlc-studio/trd.md", "sdlc-studio/tsd.md", "sdlc-studio/prd.md")

#: census name -> how to count it. Each is a GLOB over the shipped tree, counted at run time.
#: Adding a census here is how a new kind of claim becomes checkable; nothing else changes.
CENSUSES: dict = {
    "scripts": f"{SKILL_DIR}/scripts/*.py",
    "reference files": f"{SKILL_DIR}/reference-*.md",
    "help files": f"{SKILL_DIR}/help/*.md",
    "best-practice files": f"{SKILL_DIR}/best-practices/*.md",
    "lib modules": f"{SKILL_DIR}/scripts/lib/*.py",
}

#: The nouns a claim may use for each census, so prose can read naturally. Longest first, so
#: "best-practice files" is not matched as "files" by a shorter alternative.
_NOUNS: dict = {
    "scripts": ("scripts",),
    "reference files": ("reference files", "reference docs"),
    "help files": ("help files", "help pages"),
    "best-practice files": ("best-practice files", "best practice files"),
    "lib modules": ("lib modules", "shared modules"),
}

#: `60+ scripts` / `50+ reference files`. The `+` is what makes it a BAND: the claim is a
#: floor, so the census must be at or above it.
_BAND = re.compile(
    r"(?<![\w.])(\d+)\s*\+\s*(" + "|".join(
        re.escape(n) for names in _NOUNS.values() for n in sorted(names, key=len, reverse=True)
    ) + r")\b", re.IGNORECASE)

#: A PATH-AWARE band: a row naming its own glob and a count, e.g. `` `help/*.md` (40+ files) ``
#: or `` `templates/` (80+ files) ``. Five band-shaped claims in the target documents were
#: silently unchecked because their noun (`files`, `modules`) is too generic to register - and
#: registering `files` would match anything. The row already names the census; read it from
#: there rather than from a noun registry that cannot grow to cover it.
_PATH_BAND = re.compile(
    r"`(?P<path>[A-Za-z0-9_./*-]+)`\s*\((?P<n>\d+)\s*\+\s*(?P<noun>[a-z]+)\)",
    re.IGNORECASE)

#: A band inside one of these is not a claim about the shipped tree: a fenced example, a URL, or
#: a historical aside. Four such were flagged as findings by the first version.
_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _live_lines(text: str):
    """Lines outside fenced blocks, so a band in an example is not read as a claim."""
    fence = None
    for line in text.splitlines():
        state, is_fence = fence_step(line.lstrip(), fence)
        if is_fence or fence is not None:
            fence = state
            continue
        fence = state
        if "http://" in line or "https://" in line:
            continue
        yield line


def fence_step(stripped: str, fence):
    """Minimal CommonMark fence state machine - the same rule the artefact writers use."""
    marker = "`" if stripped.startswith("```") else ("~" if stripped.startswith("~~~") else None)
    if marker is None:
        return fence, False
    run = len(stripped) - len(stripped.lstrip(marker))
    if fence is None:
        return (marker, run), True
    if marker == fence[0] and run >= fence[1] and not stripped[run:].strip():
        return None, True
    return fence, True


def path_band_errors(root: Path, rel: str, text: str) -> list:
    """Every `` `<glob>` (N+ <noun>) `` claim the tree contradicts."""
    out = []
    for line in _live_lines(text):
        for m in _PATH_BAND.finditer(line):
            path, claimed = m.group("path"), int(m.group("n"))
            pattern = path.rstrip("/") + "/**/*" if path.endswith("/") else path
            # A row's glob is written from inside the SKILL tree (`help/*.md`), which is where
            # a reader of that table stands. Resolved there first, then at the repo root, so
            # either convention works and neither silently counts zero.
            counted = 0
            for base in (root / SKILL_DIR, root):
                counted = len([p for p in base.glob(pattern) if p.is_file()])
                if counted:
                    break
            if counted == 0:
                out.append(f"{rel}: {m.group(0)!r} names a path that matches NOTHING on disk - "
                           f"the claim cannot be checked and is not a claim that passed")
            elif counted < claimed:
                out.append(f"{rel}: {m.group(0)!r} claims at least {claimed}, and the tree "
                           f"holds {counted}")
    return out


#: An explicit marker for a claim the author wants checked but whose prose the pattern above
#: cannot read: `<!-- derived: scripts >= 60 -->`. Reported as UNCHECKABLE when its census is
#: unknown or its number unparseable, never skipped.
#: `.*?` rather than `[^>]*?`: the body carries `>=`, so excluding `>` made every marker
#: unmatchable - and an unmatchable marker is silently unchecked, which is the exact failure
#: this tool exists to remove.
_MARKER = re.compile(r"<!--\s*derived:\s*(.*?)\s*-->", re.IGNORECASE | re.DOTALL)


#: A TIMING claim, marked because prose cannot be trusted to carry a bound unambiguously:
#: `<!-- measured: total <= 400s -->`. The lane name is a key of the recorded timing series.
_TIMING = re.compile(r"<!--\s*measured:\s*([\w.\-]+)\s*(<=|>=)\s*(\d+(?:\.\d+)?)\s*s\s*-->",
                     re.IGNORECASE)

#: Where the gate records what its lanes actually cost.
TIMINGS_REL = "sdlc-studio/.local/gate-timings.json"


def recorded_timings(root: Path) -> dict:
    """lane -> the recorded series, or `{}` when nothing has been measured.

    `{}` is "nothing measured", which is NOT the same as "measured and fast". The caller must
    keep those apart, because treating an absent measurement as agreement is how a timing claim
    survives every run that never took the measurement it asserts.
    """
    import json  # noqa: PLC0415 - only this path needs it
    try:
        data = json.loads((root / TIMINGS_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _median(values: list) -> float | None:
    nums = sorted(float(v) for v in values if isinstance(v, (int, float)))
    if not nums:
        return None
    mid = len(nums) // 2
    return nums[mid] if len(nums) % 2 else (nums[mid - 1] + nums[mid]) / 2


def timing_errors(root: Path, rel: str, text: str) -> list[str]:
    """Every timing claim in `text` that the recorded measurements contradict or cannot check.

    The MEDIAN of the series, not the best run: a bound justified by the fastest measurement
    ever taken is a bound nobody experiences, and this project has already corrected one
    performance claim built from a cherry-picked pair.
    """
    out: list[str] = []
    unverifiable: list[str] = []
    series = recorded_timings(root)
    for m in _TIMING.finditer(text):
        lane, op, bound = m.group(1), m.group(2), float(m.group(3))
        measured = _median(series.get(lane) or []) if isinstance(series.get(lane), list) else None
        if measured is None:
            # REPORTED, not failed. The timing store is machine-local and gitignored, so a
            # fresh clone and CI have none - failing there would make the lane unusable and it
            # would be switched off, which is worse than a stated gap. "Never a pass" is
            # honoured by saying so; it is not honoured by refusing a commit for lacking a
            # measurement nobody could have taken. A CONTRADICTED measurement still fails.
            unverifiable.append(
                f"{rel}: {m.group(0)!r} is UNVERIFIABLE here - no measurement is recorded for "
                f"lane {lane!r} (the timing store is machine-local). An absent measurement is "
                f"not agreement, and this is not a pass - it is a gap, stated")
            continue
        ok = measured <= bound if op == "<=" else measured >= bound
        if not ok:
            out.append(
                f"{rel}: {m.group(0)!r} asserts {lane} {op} {bound:g}s, and the recorded "
                f"median is {measured:g}s")
    for note in unverifiable:
        print(f"SPEC-CLAIMS note: {note}", file=sys.stderr)
    return out


def census_count(root: Path, name: str) -> int | None:
    """How many of `name` the repo ships right now, or None when the census is unknown."""
    pattern = CENSUSES.get(name)
    if pattern is None:
        return None
    return len(list(root.glob(pattern)))


def _census_for_noun(noun: str) -> str | None:
    low = noun.strip().lower()
    for census, nouns in _NOUNS.items():
        if low in [n.lower() for n in nouns]:
            return census
    return None


def claims_in(text: str) -> list[dict]:
    """Every countable claim a document makes: `{kind, census, claimed, raw}`.

    `census` is None for a marked claim naming something unknown - deliberately kept in the
    list rather than dropped, because a claim nobody can check is the finding.
    """
    found: list[dict] = []
    for m in _BAND.finditer(text):
        census = _census_for_noun(m.group(2))
        found.append({"kind": "band", "census": census, "claimed": int(m.group(1)),
                      "raw": m.group(0)})
    for m in _MARKER.finditer(text):
        body = m.group(1)
        parsed = re.match(r"(.+?)\s*>=\s*(\d+)\s*$", body)
        if not parsed:
            found.append({"kind": "marker", "census": None, "claimed": None, "raw": m.group(0)})
            continue
        name = parsed.group(1).strip().lower()
        found.append({"kind": "marker",
                      "census": name if name in CENSUSES else None,
                      "claimed": int(parsed.group(2)), "raw": m.group(0)})
    return found


def check(root: Path) -> list[str]:
    """Every contradicted or uncheckable claim, as messages. Empty means the specs are true."""
    errors: list[str] = []
    for rel in SPEC_FILES:
        path = root / rel
        if not path.is_file():
            continue          # a project need not carry every spec
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{rel}: could not be read ({exc}) - its claims are UNCHECKED")
            continue
        for claim in claims_in(text):
            if claim["census"] is None or claim["claimed"] is None:
                errors.append(
                    f"{rel}: {claim['raw']!r} is marked derivable but cannot be checked - "
                    f"the census is unknown or the number unparseable. A claim nobody checks "
                    f"is not a claim that passed")
                continue
            counted = census_count(root, claim["census"])
            if counted is None:                       # unreachable via claims_in, kept honest
                errors.append(f"{rel}: {claim['raw']!r} names census "
                              f"{claim['census']!r}, which has no counter")
                continue
            if counted < claim["claimed"]:
                errors.append(
                    f"{rel}: {claim['raw']!r} claims at least {claim['claimed']} "
                    f"{claim['census']}, and the repo ships {counted}")
        errors.extend(timing_errors(root, rel, text))
        errors.extend(path_band_errors(root, rel, text))
    return errors



# ---------------------------------------------------------------------------
# Claim drift: a diff whose code and whose own prose disagree (US0583).
# ---------------------------------------------------------------------------
# Every blocking finding of RUN-01KYX375's corrected review loop was this shape - a changelog
# fragment or docstring stating a value the code in the SAME diff had moved past. BG0471 is the
# specimen: the collapse signal moved from exit 2 to exit 3 and two prose sites kept saying 2,
# one of them the docstring of the very test asserting 3. Each was decidable from the diff alone
# and instead cost an adversarial review round.
#
# Scope, accurately: the lane reads prose from TWO places, and the second is the surprising one.
#
#   1. Prose the diff ADDS. A commit contradicting its own new paperwork.
#   2. The STANDING changelog.d/ corpus, read whole on every run, whether or not the diff
#      touches it. This is deliberate - BG0471's shape is a fragment written weeks ago that a
#      later commit quietly made false, and a diff-only scan cannot see it by construction.
#
# The second is why the lane is not cheap and not quiet, and it is the half a reader needs to
# know about. An earlier version of this comment described only the first and said the scope was
# "deliberately narrow", which stayed on the page after `_standing_prose` landed in the same
# sprint - the drift shape this lane exists to catch, in the lane's own paperwork (BG0480).
#
# What keeps it from becoming noise is not narrow input but a DISCRIMINATING match: a finding
# needs a real replacement (an added line carrying the new value) and a shared subject between
# the prose and the changed code, not merely a shared digit (BG0479).

#: Files whose ADDED lines are read as prose making claims about the change.
_PROSE_SUFFIXES = (".md", ".rst", ".txt")

#: Append-only RECORD files: tables of events, not prose about behaviour. A row states that
#: somebody judged something on a date; it makes no claim a diff could contradict. Matched on
#: the path so a new ledger under `reviews/` is covered without editing a second list.
_LEDGER_DIRS = ("sdlc-studio/reviews/",)
_LEDGER_NAMES = ("critic-verdicts.md", "signoff-record.md", "evidence-record.md",
                 "sprint-review-record.md", "plan-review-verdicts.md")


def _is_ledger(path: str) -> bool:
    """Whether `path` is an append-only record rather than prose making claims."""
    norm = str(path).replace("\\", "/")
    return (any(seg in norm for seg in _LEDGER_DIRS)
            or norm.rsplit("/", 1)[-1] in _LEDGER_NAMES)

#: A bare integer, the only claim shape decided mechanically here. A full natural-language claim
#: check is not mechanisable; a changed literal contradicted by its own prose is, and it covers
#: every finding the corrected review loop returned.
_INT_RE = re.compile(r"(?<![\w.])(\d{1,6})(?![\w.])")


def _diff_files(diff: str):
    """Yield (path, added, removed) per file in a unified diff."""
    path, added, removed = None, [], []
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            if path is not None:
                yield path, added, removed
            parts = line.split(" b/", 1)
            path, added, removed = (parts[1].strip() if len(parts) == 2 else ""), [], []
        elif line.startswith(("+++ ", "--- ", "@@")):
            continue
        elif line.startswith("+") and path is not None:
            added.append(line[1:])
        elif line.startswith("-") and path is not None:
            removed.append(line[1:])
    if path is not None:
        yield path, added, removed



def _diff_hunks(diff: str):
    """Yield (path, [(header, added, removed, context), ...]) per file - the hunk-level view.

    `_diff_files` aggregates a whole file, which is the right shape for asking whether a file
    was touched and the wrong one for asking what a change replaced.
    """
    path, hunks = None, []
    hdr, added, removed, around = None, [], [], []
    def flush():
        if hdr is not None:
            hunks.append((hdr, added[:], removed[:], around[:]))
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            flush()
            if path is not None:
                yield path, hunks
            parts = line.split(" b/", 1)
            path, hunks = (parts[1].strip() if len(parts) == 2 else ""), []
            hdr, added, removed, around = None, [], [], []
        elif line.startswith("@@"):
            flush()
            # git puts the enclosing definition after the second `@@`, which is often the only
            # place the subject's NAME appears in a one-line change.
            hdr, added, removed = line, [], []
            around = [line.split("@@", 2)[-1]]
        elif line.startswith(("+++ ", "--- ")):
            continue
        elif line.startswith("+") and hdr is not None:
            added.append(line[1:])
        elif line.startswith("-") and hdr is not None:
            removed.append(line[1:])
        elif line.startswith(" ") and hdr is not None:
            # A CONTEXT line. `-    return 2` -> `+    return 3` names nothing on its own; the
            # `def collapse():` it sits under is what the prose refers to. Dropping these made
            # the subject test unsatisfiable for exactly the change shape it targets.
            around.append(line[1:])
    flush()
    if path is not None:
        yield path, hunks

def _standing_prose(root) -> list[tuple[str, str]]:
    """The unit paperwork a diff's code can contradict without touching it.

    `changelog.d/` only. These fragments assemble into `CHANGELOG.md` at release, so a stale
    claim there ships as the contract - which is exactly how BG0471 escaped: the fragment was
    written in one commit saying the signal exits 2, the code moved to 3 in a later commit that
    never reopened the fragment, and no single-diff check could ever have seen the pair.

    Deliberately NOT the whole repository. A repo-wide scan finds a contradiction somewhere on
    every commit, which is how a guard becomes noise and then gets switched off. This directory
    is small, purpose-built, and is the unit's own statement of what it did.
    """
    out = []
    d = Path(root) / "changelog.d"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.md")):
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    out.append((f"changelog.d/{f.name}", line))
        except OSError:
            continue
    return out


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

# Words that identify nothing. An identifier set that includes `self` or `return` matches
# almost any prose, which would restore exactly the indiscriminate behaviour the token
# requirement exists to remove.
_STOP_TOKENS = frozenset({
    "self", "return", "import", "from", "none", "true", "false", "and", "not", "for",
    "the", "this", "that", "with", "def", "class", "elif", "else", "len", "str", "int",
})


def _tokens(text: str) -> set:
    return {t.lower() for t in _IDENT_RE.findall(text)} - _STOP_TOKENS


def _context_tokens(path: str, added, removed, around=()) -> set:
    """What the changed code is ABOUT: identifiers off the hunk, plus the file's own stem.

    The stem is included because a fragment often names the file rather than the symbol
    ("check_spec_claims now reads ..."), and that is a genuine reference to the subject.
    """
    out = _tokens(" ".join(list(added) + list(removed) + list(around)))
    stem = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    out |= _tokens(stem)
    return out


def _prose_tokens(line: str) -> set:
    return _tokens(line)


#: Below this, a shared prefix stops being evidence of a shared subject: `let` would tie
#: `letter` to `letting`. At four, `cell` still ties `cells` and nothing accidental survives.
_STEM_FLOOR = 4


def _shares_subject(context: set, prose: set) -> bool:
    """Whether the prose names something the changed code names.

    Exact equality is too brittle for English: the fixture that pins BG0471's own shape has
    `def collapse()` in the code and "when the suite collapses" in the prose, which is plainly
    the same subject and shares no token exactly. So a prefix of at least `_STEM_FLOOR`
    characters counts, which covers ordinary inflection without letting unrelated words match.
    """
    if context & prose:
        return True
    for c in context:
        for p in prose:
            shorter, longer = (c, p) if len(c) <= len(p) else (p, c)
            if len(shorter) >= _STEM_FLOOR and longer.startswith(shorter):
                return True
    return False


def claim_drift(diff: str, root=None) -> list[dict]:
    """Findings where this diff's prose still states a literal this diff's code REPLACED.

    The signal is the value the change moved AWAY from, not any number the code happens to
    lack. A first implementation asked whether the prose named a number absent from the code
    side, and a real staged diff sank it immediately: 23KB of changed code contains very nearly
    every small integer, so the prose always intersected and nothing was ever flagged. The
    criterion says "changing a literal while its own prose still states the OLD value", and that
    is both what BG0471 was and what discriminates.

    ADVISORY by construction: the caller reports these on a channel that does not influence the
    exit code (D0105).
    """
    replaced, prose_added = {}, []
    for path, hunks in _diff_hunks(diff):
        if _is_ledger(path):
            # An append-only LEDGER is not prose making claims about the code. A verdict row
            # records a judgement somebody made; it asserts nothing about how anything behaves,
            # so it cannot be in drift with a diff by construction. Reading it as prose fired on
            # the verdict log every time a diff touched `critic.py`, because every row carries
            # a reviewer id containing the word `critic`.
            continue
        if path.endswith(_PROSE_SUFFIXES):
            prose_added.extend(
                (path, line) for _h, added, _r, _c in hunks for line in added)
            continue
        # PER HUNK, not per file. A file-wide comparison dilutes to nothing on any real diff:
        # gate_timing.py's own repair mentions 2 in a dozen places, so `2` appeared on both
        # sides and never read as replaced - the replay over commit 67fc683f found zero, which
        # is what sent this design back a second time. A hunk is the smallest unit in which
        # "this line used to say X and now says Y" is a fact rather than an aggregate.
        for _hdr, added, removed, around in hunks:
            old_nums = {n for line in removed for n in _INT_RE.findall(line)}
            new_nums = {n for line in added for n in _INT_RE.findall(line)}
            if not new_nums:
                # Nothing on the added side carries an integer, so `old_nums - new_nums` is the
                # WHOLE removed set and every number in it reads as replaced - by a value that
                # does not exist. The finding then prints `carries ''`, naming no code the reader
                # can act on. Replayed over the 40 commits to 3570c94a this replay measured
                # 135 of 215 findings, 63%; the independent seat that raised it measured 191
                # of 235 on the same window, the gap being the changelog corpus that grew
                # between the two runs. Both are recorded in the evidence file rather than
                # reconciled into one, because neither reproduced the other. This is what a
                # pure deletion, or a `-RETRIES = 2` / `+RETRIES = LIMIT` hunk, produces. There
                # is no replacement to reason about here, so the correct output is nothing
                # (BG0479).
                continue
            for gone in old_nums - new_nums:
                # carry the value it moved TO, so prose that narrates the change honestly
                # ("was 2, is now 3") can be told from prose still asserting the old one
                replaced.setdefault(gone, (path, next(
                    (l.strip() for l in added if _INT_RE.search(l)), ""), new_nums,
                    _context_tokens(path, added, removed, around)))
    # `not replaced` is deliberately not tested: with nothing replaced the intersection
    # below is empty on every line, so the extra clause would be an unreachable guard -
    # the dead-defence shape BG0413 shipped. Mutation caught it here too.
    # The unit's own standing paperwork, which a diff can contradict without touching it.
    if root is not None:
        prose_added.extend(_standing_prose(root))
    if not prose_added:
        return []
    findings = []
    for prose_path, prose_line in prose_added:
        prose_nums = set(_INT_RE.findall(prose_line))
        for stale in prose_nums & set(replaced):
            code_path, code_line, new_nums, context = replaced[stale]
            if not _shares_subject(context, _prose_tokens(prose_line)):
                # A shared DIGIT is not a shared subject. `== 6` becoming `== 7` matched two
                # changelog fragments about the commit gate and about TRD enumerations, neither
                # of which had anything to do with the column count that changed - they merely
                # contained the digit. Small integers occur in ordinary prose for ordinary
                # reasons, so the prose must also name something the changed code names: an
                # identifier off the hunk, or the file's own stem. This is the difference
                # between "states the old value of this thing" and "contains this digit"
                # (BG0479).
                continue
            if prose_nums & new_nums:
                # The prose names the NEW value too, so it is narrating the change rather than
                # asserting the old one - "the exit code was 2 ... it is now 3" is current, and
                # flagging it is the noise that gets a lane switched off. The replay found this
                # immediately: the first firing run's loudest hits were all honest narration.
                continue
            findings.append({"prose_file": prose_path, "prose": prose_line.strip()[:160],
                             "code_file": code_path, "code": code_line,
                             "stale_value": stale})
            break
    return findings


#: A ticked acceptance criterion in an added line.
_TICK_RE = re.compile(r"^\s*-\s*\[x\]\s*(.+)$", re.IGNORECASE)
#: The surface a criterion names: a path in a Verify line, or a bare path in the criterion text.
_SURFACE_RE = re.compile(r"([\w./-]+\.(?:py|sh|md|ya?ml|json|ts|js))")


def ticked_over_untouched(diff: str) -> list[dict]:
    """Criteria ticked in this diff whose named surface this diff does not touch (US0584).

    BG0472's shape: two criteria of BG0460 were recorded met while `git diff` disproved both -
    one over a story byte-identical to the base ref, one over verifiers that never called the
    function they name. Both ticks passed the close.

    A criterion naming NO surface is reported as `unjudgeable` rather than dropped: an
    unanswerable check must never read the same as a satisfied one, which is the rule this whole
    batch exists to enforce. An UNTICKED criterion claims nothing and is not judged.
    """
    touched, units = set(), []
    for path, added, _removed in _diff_files(diff):
        touched.add(path)
        if "/stories/" in path or "/bugs/" in path or "/change-requests/" in path:
            units.append((path, added))
    findings = []
    for path, added in units:
        unit = re.search(r"((?:US|BG|CR)[-\d]*\d)", path)
        unit = unit.group(1) if unit else path
        pending = None
        for line in added:
            tick = _TICK_RE.match(line)
            if tick:
                if pending is not None:          # the previous tick named no surface of its own
                    findings.append({"unit": unit, "kind": "unjudgeable",
                                     "criterion": pending, "surface": None})
                pending = tick.group(1).strip()
                # a surface named inside the criterion text itself counts
                found = _SURFACE_RE.findall(pending)
                if found:
                    pending = None
                    if not any(s in touched for s in found):
                        findings.append({"unit": unit, "kind": "untouched",
                                         "criterion": tick.group(1).strip(),
                                         "surface": found[0]})
                continue
            if pending is not None and "Verify:" in line:
                found = _SURFACE_RE.findall(line)
                if found and not any(s in touched for s in found):
                    findings.append({"unit": unit, "kind": "untouched",
                                     "criterion": pending, "surface": found[0]})
                pending = None
        if pending is not None:
            findings.append({"unit": unit, "kind": "unjudgeable",
                             "criterion": pending, "surface": None})
    return findings


#: Where the lane's measured yield accumulates. The DECISION to make this lane blocking is
#: explicitly out of the sprint that ships it - the lane arrives here, so a sprint's worth of
#: yield cannot exist yet. What must exist is the number, so that decision has something to read
#: rather than an impression (D0105).
#:
#: Under `.local/`, following TIMINGS_REL above - the precedent this repo already set for
#: state a hook writes on every commit. The first version wrote to a TRACKED path, so every
#: commit left the tree dirty with a modified file the author never touched and the hook
#: never staged (BG0481).
_YIELD_REL = "sdlc-studio/.local/claim-drift-yield.json"

#: Where it used to live. Carried over once when the new file is absent, so counts
#: accumulated before the move are not silently restarted by the move itself.
_YIELD_LEGACY_REL = "sdlc-studio/retros/evidence/claim-drift-yield.json"


def record_yield(root, diff: str) -> dict:
    """Accumulate this run's claim-drift findings into the evidence record."""
    path = Path(root) / _YIELD_REL
    legacy = Path(root) / _YIELD_LEGACY_REL
    if not path.exists() and legacy.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        rec = {"runs": 0, "findings": 0, "runs_with_findings": 0}
    found = len(claim_drift(diff, root)) + len(ticked_over_untouched(diff))
    rec["runs"] = int(rec.get("runs", 0)) + 1
    rec["findings"] = int(rec.get("findings", 0)) + found
    if found:
        rec["runs_with_findings"] = int(rec.get("runs_with_findings", 0)) + 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec

def main(argv: list[str] | None = None, stdin_text: str | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    parser.add_argument("--claim-drift", metavar="DIFF",
                        help="also report claim drift over a unified diff ('-' reads stdin). "
                             "ADVISORY: these findings never change the exit code")
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.claim_drift:
        diff = stdin_text if args.claim_drift == "-" and stdin_text is not None else (
            sys.stdin.read() if args.claim_drift == "-"
            else Path(args.claim_drift).read_text(encoding="utf-8"))
        record_yield(root, diff)
        for f in ticked_over_untouched(diff):
            if f["kind"] == "unjudgeable":
                print(f"CLAIM-DRIFT: {f['unit']} ticks {f['criterion']!r}, which names no "
                      f"surface this run can check - reported, never counted as passing",
                      file=sys.stderr)
            else:
                print(f"CLAIM-DRIFT: {f['unit']} ticks {f['criterion']!r} while this diff does "
                      f"not touch {f['surface']}", file=sys.stderr)
        for f in claim_drift(diff, root):
            # Reported on its own channel and NOT folded into `errors`: the spec-claim errors
            # below keep the blocking contract they have today, and this lane is advisory while
            # its yield is measured (D0105). One script, two severities, stated rather than
            # discovered by whoever adds the next lane.
            print(f"CLAIM-DRIFT: {f['prose_file']} says {f['prose']!r} while "
                  f"{f['code_file']} in this diff carries {f['code']!r}", file=sys.stderr)
    errors = check(root)
    for err in errors:
        print(f"SPEC-CLAIMS: {err}", file=sys.stderr)
    if errors:
        return 1
    counted = {name: census_count(root, name) for name in CENSUSES}
    print("Spec claims agree with the census: "
          + ", ".join(f"{n}={c}" for n, c in sorted(counted.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
