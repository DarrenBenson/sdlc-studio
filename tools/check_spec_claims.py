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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repo root")
    args = parser.parse_args(argv)
    root = Path(args.root)
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
