#!/usr/bin/env python3
"""Advisory check: do the project's state documents still tell the truth?

`sdlc-studio/reviews/LATEST.md` is the project's state anchor - read first after every reset. It
drifts silently: it once claimed 606 tests (was 622), ~66 disclosure advisories (was 0), and a
workstream "deferred" (was shipped), and nothing caught it. This check compares the facts LATEST.md
*claims* against reality and flags the mismatches. The same treatment is given to the TRD's census
counts, which rotted the same way. Advisory (never blocks) and skill-only (no-op where there is no
SKILL.md). It only checks a fact a document actually states - it never demands one, and it reports
the claims it could not find as UNCHECKED rather than counting them as green.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _skill_dir(root: Path) -> Path:
    return root / ".claude" / "skills" / "sdlc-studio"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _true_version(skill_dir: Path) -> str | None:
    m = re.search(r'^\s*version:\s*"([\d.]+)"', _read(skill_dir / "SKILL.md"), re.M)
    return m.group(1) if m else None


def _true_test_count(skill_dir: Path) -> int:
    tdir = skill_dir / "scripts" / "tests"
    return sum(len(re.findall(r"^\s*def test_", _read(f), re.M))
               for f in sorted(tdir.glob("test_*.py"))) if tdir.is_dir() else 0


def _true_disclosure_count(root: Path) -> int | None:
    try:
        import disclosure
        r = disclosure.check(root)
        return len(r["findings"]) if r["applicable"] else None
    except Exception:  # noqa: BLE001 - the freshness check must never crash the gate
        return None


# LATEST.md phrasings that assert a sign-off or closure is still OUTSTANDING. Kept to the words
# that mean "not done yet" so the check never fires on a document reporting the opposite (a
# sign-off that LANDED, a run that CLOSED). If none of these match, the anchor states no such
# claim and this check stays silent - it only ever checks a fact the document actually makes.
_SIGNOFF_OUTSTANDING = (
    re.compile(r"sign-?off\b[^.\n]{0,40}?\b(?:owed|outstanding|pending|awaited|awaiting|"
               r"not\s+landed|still\s+needed)\b", re.I),
    re.compile(r"\b(?:owed|outstanding|pending|awaiting)\b[^.\n]{0,25}?sign-?off\b", re.I),
    re.compile(r"\bnot\s+(?:yet\s+)?closed\b", re.I),
    re.compile(r"\bunreviewed\b", re.I),
)

# A COUNT of review rounds the anchor narrates. The number leads, only review adjectives may sit
# between it and the word, so an ordinal ("round 3", "one of the rounds") is not misread. Shared
# in spirit with run_state's ledger check - both read a count off prose to compare with the data.
_ROUND_COUNT_RE = re.compile(
    r"\b(\d+|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+"
    r"(?:(?:independent|adversarial|review|close|closing|full)\s+){0,3}rounds?\b", re.I)
_WORD_NUMBERS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def _claims_signoff_outstanding(text: str) -> bool:
    return any(p.search(text) for p in _SIGNOFF_OUTSTANDING)


def _claimed_round_count(text: str) -> int | None:
    m = _ROUND_COUNT_RE.search(text)
    if not m:
        return None
    tok = m.group(1).lower()
    return _WORD_NUMBERS.get(tok, None) if tok in _WORD_NUMBERS else int(tok)


def _close_landed(root: Path, state: dict) -> bool:
    """True when the run's own record says the close it describes has LANDED: the run carries an
    `ended_at` (or a terminal outcome), and `close_owed` reports nothing still owed. Both are read
    from state the anchor claims to summarise, so a LATEST.md still calling the sign-off owed is
    contradicted by the very run it narrates. When a close is GENUINELY owed the anchor is right,
    so this returns False and nothing is flagged."""
    try:
        from lib import run_state
        ended = bool(state.get("ended_at")) or state.get("outcome") in run_state.CLOSED
    except Exception:  # noqa: BLE001 - never crash the gate
        ended = bool(state.get("ended_at"))
    if not ended:
        return False
    try:
        import close_owed
        rep = close_owed.owed(root)
        if rep.get("owed") or rep.get("velocity_owed"):
            return False
    except Exception:  # noqa: BLE001 - close_owed is advisory here; absence is not a landing claim
        pass
    return True


# --- claim-anchored census counts ---------------------------------------------------------------
# The predecessor guard read the FIRST match of a count pattern anywhere in the document and
# compared it as a floor, so an exact claim that had rotted upward ("58 scripts", 67 present)
# satisfied `actual >= claimed` and the guard reported green on the very numbers it existed to
# catch. Two rules replace that, and both are properties of the CLAIM rather than of the file:
#
#   * every occurrence of a claim is checked, not the first - a claim is a sentence, and each
#     sentence that makes it is judged on its own, so a stale restatement cannot shelter behind a
#     correct one earlier in the file;
#   * the comparison form is read off the claim's own wording - "60+ scripts" is a floor, "58
#     scripts" is an exact count - so a number written as exact is judged as exact.
#
# Nothing here consults a file mtime or a "last verified" stamp. The verdict is computed from the
# measured value, so a stale number cannot pass by sitting in a recently-touched or freshly stamped
# file, and a document nobody checked is not mistaken for one whose counts match: a claim the
# document does not make is returned UNCHECKED, never counted as a pass.
_CENSUS_MEASURES = {
    "scripts": lambda sd: len(list((sd / "scripts").glob("*.py"))),
    "reference files": lambda sd: len(list(sd.glob("reference-*.md"))),
    "help files": lambda sd: len(list((sd / "help").glob("*.md"))),
}
_CENSUS_CLAIMS = {
    "scripts": re.compile(r"(\d+)(\+?)\s+scripts\b", re.I),
    "reference files": re.compile(r"(\d+)(\+?)\s+reference\s+files?\b", re.I),
    "help files": re.compile(r"(\d+)(\+?)\s+help\s+files?\b", re.I),
}
# A floor claim ("60+") is honest while reality sits above it, but a floor left far enough behind
# is as stale as a wrong exact number - it was the floor reading that let "58 scripts" pass at 67.
# The band is stated here rather than left implicit so the finding can name the rule it applied.
_FLOOR_STALE_RATIO = 1.25

# A document's revision history NARRATES the claims it used to make, usually quoting the stale
# number beside its correction. Those are not current assertions, so the census scan stops at the
# history heading; scanning it would make every correction re-report the defect it fixed.
_HISTORY_HEADING = re.compile(r"^#{1,3}\s+(?:Revision\s+History|Changelog)\s*$", re.I | re.M)


def _current_body(text: str) -> str:
    m = _HISTORY_HEADING.search(text)
    return text[: m.start()] if m else text


def _claim_quote(text: str, m: re.Match) -> str:
    """The claim's own words - a bounded window around the match, so a finding names the sentence
    that is wrong rather than a line number that moves the next time the file is edited."""
    return " ".join(text[max(0, m.start() - 40): m.end() + 40].split())


def census_claims(repo_root: Path | str = ".", doc: str = "sdlc-studio/trd.md") -> dict:
    """Check every census count `doc` currently claims against the measured workspace.

    Returns {checked, unchecked, findings, applicable, document}. `checked` carries one record per
    occurrence, each holding the measured `actual` alongside the `claimed` value - the verdict is
    derived from that number, which is what makes 'the counts match' distinguishable from 'nobody
    looked'. `unchecked` names the claims the document does not make.
    """
    root = Path(repo_root)
    skill_dir = _skill_dir(root)
    path = root / doc
    if not (skill_dir / "SKILL.md").exists() or not path.exists():
        return {"checked": [], "unchecked": [], "findings": [], "applicable": False,
                "document": doc}
    body = _current_body(_read(path))
    checked: list[dict] = []
    unchecked: list[str] = []
    findings: list[dict] = []
    for name, pattern in _CENSUS_CLAIMS.items():
        matches = list(pattern.finditer(body))
        if not matches:
            unchecked.append(name)
            continue
        actual = _CENSUS_MEASURES[name](skill_dir)
        for m in matches:
            claimed, is_floor = int(m.group(1)), m.group(2) == "+"
            if is_floor:
                ok = claimed <= actual < claimed * _FLOOR_STALE_RATIO
                why = (f"a floor claim holds while the count sits in [{claimed}, "
                       f"{claimed * _FLOOR_STALE_RATIO:g})")
            else:
                ok = claimed == actual
                why = "an exact claim holds only on the exact count"
            record = {"claim": name, "claimed": claimed, "actual": actual,
                      "form": "floor" if is_floor else "exact", "ok": ok,
                      "quote": _claim_quote(body, m)}
            checked.append(record)
            if not ok:
                findings.append({
                    "kind": "census-drift",
                    "detail": (f"{doc} claims {claimed}{'+' if is_floor else ''} {name}; "
                               f"{actual} counted in the workspace ({why}) - stale claim: "
                               f"\"{record['quote']}\""),
                })
    return {"checked": checked, "unchecked": unchecked, "findings": findings,
            "applicable": True, "document": doc}


def check(repo_root: Path | str = ".") -> dict:
    """Findings (all advisory). {findings, ok, applicable, census}. Applicable only on the skill
    repo with a LATEST.md or a TRD present; only facts those documents state are checked."""
    root = Path(repo_root)
    skill_dir = _skill_dir(root)
    latest = root / "sdlc-studio" / "reviews" / "LATEST.md"
    census = census_claims(root)
    if not (skill_dir / "SKILL.md").exists() or not (latest.exists() or census["applicable"]):
        return {"findings": [], "ok": True, "applicable": False, "census": census}
    findings: list[dict] = list(census["findings"])
    text = _read(latest) if latest.exists() else ""

    def claim(pattern: str):
        m = re.search(pattern, text, re.I)
        return m.group(1) if m else None

    # version
    cv, tv = claim(r"project version:\**\s*([\d.]+)"), _true_version(skill_dir)
    if cv and tv and cv != tv:
        findings.append({"kind": "version-drift",
                         "detail": f"LATEST.md says version {cv}; SKILL.md is {tv}"})
    # test count
    ct = claim(r"([\d,]+)\s+script tests")
    if ct:
        ct_n, tt = int(ct.replace(",", "")), _true_test_count(skill_dir)
        if ct_n != tt:
            findings.append({"kind": "test-count-drift",
                             "detail": (f"LATEST.md says {ct_n} tests; {tt} test functions "
                                        f"counted statically in scripts/tests (the runner may "
                                        f"report fewer for skips/subclasses - claim this number)")})
    # disclosure count
    cd = claim(r"disclosure[^\d]{0,8}(\d+)")
    if cd is not None:
        td = _true_disclosure_count(root)
        if td is not None and int(cd) != td:
            findings.append({"kind": "disclosure-drift",
                             "detail": f"LATEST.md says disclosure {cd}; actual is {td}"})
    # the two load-bearing claims a resuming agent acts on - has the owed sign-off landed, and
    # does the narrated round count match the run's ledger. Both compared against state the tool
    # already holds; the document being wrong here sends a fresh context looking for a signature
    # that arrived and re-reviewing a repair already judged.
    try:
        from lib import run_state
        state = run_state.read(root)
    except Exception:  # noqa: BLE001 - an unreadable run state must not crash the advisory gate
        state = {}
    # sign-off / closure the anchor calls outstanding, once the run says it landed
    if _claims_signoff_outstanding(text) and _close_landed(root, state):
        findings.append({"kind": "signoff-drift",
                         "detail": ("LATEST.md still calls a sign-off or closure outstanding, but "
                                    "the run carries an end and close_owed reports none owed - the "
                                    "signature it says is owed has landed. A resuming agent will "
                                    "hunt for an owed sign-off that arrived")})
    # round count the anchor narrates, against the run's own review ledger
    claimed = _claimed_round_count(text)
    if claimed is not None:
        try:
            ledger = len(run_state.review_rounds(root))
        except Exception:  # noqa: BLE001 - never crash the gate
            ledger = 0
        if ledger and claimed != ledger:
            findings.append({"kind": "round-count-drift",
                             "detail": (f"LATEST.md narrates {claimed} review round(s); the run "
                                        f"ledger (review_rounds) holds {ledger} - claim the "
                                        f"ledger's count, not a smaller number beside it")})
    # anchor-window ceiling: the anchor is re-read at every session start, so
    # it must stay a WINDOW (current state + one-line history), not a ledger
    # of full past-sprint paragraphs duplicating the retros
    from lib import sdlc_md
    try:
        ceiling = int(sdlc_md.project_override(root, "docs.latest_max_lines", 80))
    except (TypeError, ValueError):
        ceiling = 80
    n_lines = len(text.splitlines())
    if n_lines > ceiling:
        findings.append({"kind": "anchor-ledger",
                         "detail": (f"LATEST.md is {n_lines} lines (> {ceiling}, "
                                    f"docs.latest_max_lines) and is re-read every session "
                                    f"start - move past-sprint paragraphs to their retros "
                                    f"and keep one History line each")})
    return {"findings": findings, "ok": not findings, "applicable": True, "census": census}


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Flag stale facts in LATEST.md (advisory).")
    ap.add_argument("--root", default=".")
    sdlc_md.add_format_arg(ap)
    args = ap.parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    r = check(args.root)
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0  # advisory: report, never fail
    if not r["applicable"]:
        print("doc-freshness: N/A (not the skill repo, or no state documents)")
        return 0
    if r["ok"]:
        print("doc-freshness: state documents are fresh")
    else:
        print(f"doc-freshness: {len(r['findings'])} stale claim(s):")
        for f in r["findings"]:
            print(f"  [{f['kind']}] {f['detail']}")
    # Say what was actually verified. A silent green cannot tell a document whose counts were
    # measured and matched from one that states no count at all, and the two are different facts.
    census = r.get("census") or {}
    if census.get("applicable"):
        passed = sum(1 for c in census["checked"] if c["ok"])
        print(f"  census: {passed}/{len(census['checked'])} claim(s) in "
              f"{census['document']} verified against the measured count"
              + (f"; not stated (unchecked): {', '.join(census['unchecked'])}"
                 if census["unchecked"] else ""))
    return 0  # advisory: report, never fail


if __name__ == "__main__":
    raise SystemExit(main())
