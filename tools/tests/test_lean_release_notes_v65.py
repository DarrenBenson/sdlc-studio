"""US1327: the v6.5.0 release notes lead with what changed for the person answering for the release.

The reader is a head of engineering on 6.4.0 deciding whether her teams take 6.5 to the change
board. Each check is a function returning its problems, run on the notes and on a control it must
refuse: the 6.4.0 notes as they stand and with the version changed, a draft composed from the 6.5
changelog fragments, a theme with its units cut, a quality count with its decision cut or changed,
a changed default with its replacement cut, a Breaking fragment left out, a refusal the code does
not make, a configuration default `reference-config.md` contradicts, and a cost figure with its
report cut, its value changed, summed across reports or its report unsigned. The decisions, the
defaults and the figures are read from their sources when the test runs, never typed here; the
Won't Fix counts are read from the bug corpus as the commit that recorded each decision left it,
so a bug reopened since or a later Won't Fix bug citing the decision leaves them as ruled; and the
upgrade path is checked by running the notes' own steps on projects
v6.4.0's `init.py` created.

The 6.5.0 skill is the v6.5.0 tag's tree once the tag exists, and before then this tree with its
version read as 6.5.0, so the checks judge 6.5.0's own CLI before the cut and after it. The
CHANGELOG link is judged against the layout the CHANGELOG has at the time: `[Unreleased]` before
the cut, `[6.5.0]` after it. The BG1613 clause is judged on that bug's status at the commit that
cut 6.5.0, so a later fix of it leaves the clause true.
"""
# test-census-subject: docs/release-notes-v6.5.0.md
from __future__ import annotations

import json
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SKILL_REL = ".claude/skills/sdlc-studio"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.append(str(REPO / SKILL_REL / "scripts" / "tests"))
import gitutil  # noqa: E402
from test_lean_release_notes_v6 import (  # noqa: E402
    UNIT_ID, _blank, changelog_sections, section, sections, units)
from test_lean_release_notes_v61 import _norm, _run  # noqa: E402
from test_lean_release_notes_v62 import _blocks, _cli, _extract, _tree  # noqa: E402
from test_lean_release_notes_v64 import (  # noqa: E402
    COST, REPORT_ID, _flat, report_figures, shipped)

NOTES = REPO / "docs" / "release-notes-v6.5.0.md"
NOTES_64_REL = "docs/release-notes-v6.4.0.md"
CHANGELOG = REPO / "CHANGELOG.md"
FRAGMENTS = REPO / "changelog.d"
REPORTS = REPO / "sdlc-studio" / "reports"
DECISIONS_REL = "sdlc-studio/decisions.md"
DECISIONS = REPO / DECISIONS_REL
BUGS = REPO / "sdlc-studio" / "bugs"
TAG = "v6.5.0"

#: A unit or a decision a theme may name as what delivered it.
ID = re.compile(rf"{UNIT_ID.pattern}|\bD\d{{4}}\b")
DECISION_ID = re.compile(r"\bD\d{4}\b")
#: Each theme of the first section -> the units or decisions its bullet names, and no others.
THEMES = {
    "6.5 ships with fewer than 50 open defects and none at medium or above":
        {"D0560", "D0563", "D0564", "D0613"},
    "every persona and seat card is held to a written standard before it frames a brief, and "
    "the goal review says when nothing can check the goal":
        {"US1036", "US1039", "US1040", "US1046", "US1052", "US1053", "US1054", "US1055",
         "US1056", "US1057", "US1322", "CR0748"},
    "a sprint walks a wave from build to paperwork and wakes the model only at a refusal, a "
    "warning, a reject, a rebase conflict or the wave's end, and the author's own mutants reach "
    "the reviewer replayed":
        {"US1192", "US1193", "US1195", "US1196", "US1197", "US1198", "US1200", "US1201",
         "US1202"},
    "a delegated signature names the decision that authorised it, and a run awaiting its "
    "signature no longer holds up the next": {"US1290", "US1291", "US1292", "US1293"},
    "a configuration a project switched on is never read as off, because pyyaml is required":
        {"US1296", "US1297", "US1298", "US1299"},
    "a red ci run on main is answered by a written policy": {"US1236", "US1237", "US1238"},
    "sdlc studio is documented as a harness-agnostic agent skill":
        {"US1315", "US1316", "US1317", "US1318", "US1319", "US1320", "US1321"},
    "filing and planning catch overlap before a run pays for it": {"US1314", "US1324", "US1326"},
}
#: Contributor tooling, named only under the contributors heading.
CONTRIBUTORS = {"US1190", "US1191", "US1313"}
#: A unit id a section outside the themes may name: the open bug the upgrade path discloses.
ALLOWED_OUTSIDE = {"Upgrading from 6.4": {"BG1613"}}
QUALITY = ("D0560", "D0563", "D0564", "D0613")
COUNT_LINE = re.compile(r"^\*\*v6\.5\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$")
#: A sentence that talks about open defects, their severity or a Won't Fix list.
OPEN_TALK = re.compile(r"(?i)\bopen (?:defects?|bugs?)\b|\b(?:defects?|bugs?)\b[^.]*\bopen\b|"
                       r"\bMedium\b|Won't Fix")
#: A whole number that is not part of a version, an id, a price or a hyphenated word.
WHOLE = re.compile(r"(?<![\w.$-])\d[\d,]*(?![\w]|\.\d)")
NO_OTHER = re.compile(r"No 6\.5 fragment is filed under Removed or Security\.")
BREAKING_SAID = re.compile(r"Filed under Breaking: ([^.]*)\.")
#: Each change a 6.4 habit meets, label -> (what names its bullet, what the bullet must also
#: say before its `Instead:`, what its `Instead:` clause must carry).
CHANGES = {
    "PyYAML required": (
        r"^- \*\*PyYAML is required\.\*\*",
        (r"`install\.sh` and `install\.ps1` refuse", r"exits 1",
         r"`python3 -m pip install pyyaml`", r"`gate\.py` exits 2 before any lane"),
        r"`python3 -m pip install pyyaml`"),
    "the retired key": (r"`require_ac_verification` is retired",
                        (r"`migrate --apply` removes it",), r"`quality\.done_requires_verified`"),
    "the persona standard": (
        r"breaks the persona standard frames no brief",
        (r"`persona_resolve\.py resolve` exits 1",
         r"`critic\.py brief` and the other briefs exit 2",
         r"`persona_review\.py brief --card <card> --seat <seat>`",
         r"`personas\.standard: report`"),
        r"`persona_review\.py check`"),
    "the delegated signature": (
        r"`sprint sign --delegated` needs `--decision`",
        (r"\baccepted\b", r"`--decision` without `--delegated` is refused"),
        r"`--delegated --decision <id>`"),
    "the duplicate filing": (r"`file_finding\.py file` refuses a duplicate",
                             (r"exits 1", r"nothing written"), r"`--distinct-from <id>`"),
    "the Definition of Ready at Done": (
        r"`transition\.py set --status Done` refuses a Draft or Proposed story",
        (r"Definition of Ready",), r"`Affects`"),
    "the run slot": (r"awaiting its signature no longer holds the run slot",
                     (r"`sprint plan --write`",), r"`sprint sign`"),
    "the Delivered status": (r"RFC gains a Delivered status", (r"`reconcile apply`",),
                             r"\bDelivered\b"),
    "the Risk-class raise": (r"`reconcile\.py apply` raises a story's stamped `Risk-class`",
                             (r"never lowered",), r"component map"),
    "the second review seat": (r"second review seat is product on the shipped seats",
                               (r"building seat",), r"`critic\.py brief --seat <seat>`"),
}
#: A claim that a copied 6.4 card naming "the Primary persona, Sam" is refused.
SAM = re.compile(r"\bSam\b")
REFUSED = re.compile(r"(?i)\b(?:refus\w*|block\w*|reported as)\b")
UPGRADE = r"^Upgrading from 6\.4$"
STAMP = "sdlc-studio/.version stale (skill 6.4.0 -> 6.5.0)"
#: Each kind of change the dry run lists for a 6.4 project -> what the notes quote for it.
QUOTES = {"stale-version": STAMP, "persona-standard": "set personas.standard: report",
          "retired-config-key": "require_ac_verification removed"}
#: The keys 6.5 adds -> what reads the default `reference-config.md` states for each.
NEW_KEYS = {
    "personas.standard": r"^\| `personas\.standard` \| `([^`]+)` \|",
    "ci.wait_timeout_minutes": r"^\| `ci\.wait_timeout_minutes` \|.*\| `([^`]+)` \|\s*$",
    "ci.rerun_limit": r"^\| `ci\.rerun_limit` \|.*\| `([^`]+)` \|\s*$",
    "review.rendered_paths": r"^\| `review\.rendered_paths` \| `([^`]+)` \|",
}
WAIT_KEY = "`ci.wait_timeout_minutes`"
BOUNDS = re.compile(r"(?i)\b(?:bounds|gives up|times out|stops waiting|caps)\b")
CLOSED = {"Fixed", "Verified", "Closed", "Won't Fix", "Superseded", "Duplicate", "Done"}
#: The signed reports of the runs that built 6.5, runs sixteen to twenty-six.
RUNS_65 = {f"RPT{n:04d}" for n in range(35, 46)}
#: Each fixture project the upgrade steps run on -> (how it differs from a bare 6.4 project,
#: the kinds the dry run lists, the files `--apply` changes, the config keys it changes).
VARIANTS = {
    "a 6.4 project": ((), ("stale-version",), ["sdlc-studio/.version"], []),
    "a 6.4 project holding its own seat cards": (
        ("cards",), ("stale-version", "persona-standard"),
        ["sdlc-studio/.config.yaml", "sdlc-studio/.version"], ["personas.standard"]),
    "a 6.4 project carrying require_ac_verification": (
        ("legacy",), ("stale-version", "retired-config-key"),
        ["sdlc-studio/.config.yaml", "sdlc-studio/.version"], ["require_ac_verification"]),
}
_FIX: dict[str, object] = {}
#: A `migrate.py` that reports the stamp the notes quote but writes a file of its own, and on
#: `--apply` a config key of its own, the control `step_problems` must refuse on both steps.
_STRAY = """import json, sys
from pathlib import Path
root = Path(sys.argv[sys.argv.index("--root") + 1])
(root / "stray.txt").write_text(" ".join(sys.argv[1:]))
if "--apply" in sys.argv:
    with open(root / "sdlc-studio" / ".config.yaml", "a", encoding="utf-8") as cfg:
        cfg.write("\\nstray: 1\\n")
print(json.dumps({"deterministic": [{"kind": "stale-version", "detail": "%s"}]}))
""" % STAMP


def at_cut(rel: str) -> str:
    """`rel` at the commit that cut 6.5.0: the v6.5.0 tag's tree once this clone holds the tag,
    else the working tree, which is what the cut will tag."""
    ref = _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify", f"refs/tags/{TAG}")
    if ref.returncode != 0:
        return (REPO / rel).read_text(encoding="utf-8")
    proc = _run("git", "-C", str(REPO), "show", f"{TAG}:{rel}")
    if proc.returncode != 0:
        raise AssertionError(f"git show {TAG}:{rel} failed: {proc.stderr}")
    return proc.stdout


def entries_65(changelog: str, fragments: Path = FRAGMENTS) -> list[tuple[str, frozenset, str]]:
    """(section, the unit ids it is known by, body) of each 6.5 entry wherever the layout holds
    it at the time: each bullet of the `## [6.5.0]` section's subsections once the cut has
    written it, known by the ids its text names; the pending `changelog.d/` fragments only
    before then, each known by its file name (a fragment present after the cut belongs to the
    next release)."""
    cut = re.search(r"^## \[6\.5\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    out = []
    if cut:
        for m in re.finditer(r"^### (\w+)\n(.*?)(?=^### |\Z)", cut.group(1), re.M | re.S):
            for bullet in re.split(r"\n(?=- )", m.group(2).strip()):
                if bullet.strip():
                    out.append((m.group(1), frozenset(UNIT_ID.findall(bullet)), bullet))
        return out
    for p in sorted(fragments.glob("*.md")) if fragments.is_dir() else []:
        head, _, body = p.read_text(encoding="utf-8").partition("\n")
        m = re.match(r"<!-- section: (\w+) -->", head)
        out.append((m.group(1) if m else "", frozenset({p.stem}), body))
    return out


def lead_problems(text: str, changelog: str) -> list[str]:
    """AC1: a one-sentence headline naming 6.5.0 as current, a first section holding the eight
    themes and nothing else, each naming exactly its units or decisions, no unit id outside a
    theme bullet but in the known-issues, sources and contributors passages, the Breaking
    sentence and the bug the upgrade path names, the contributor tooling named under the
    contributors heading alone, and the CHANGELOG section holding 6.5's entries linked."""
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.5\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.5.0 the current release: "
                        f"{headline[:120]!r}")
    blank = _blank(text)
    firsts = sections(blank)
    first = firsts[0][1] if firsts else ""
    bullets, paras = _blocks(first)
    problems += [f"the first section holds text outside its theme bullets: "
                 f"{' '.join(p.split())[:80]!r}" for p in paras]
    problems += [f"the first section lists a theme that is not one of the eight: "
                 f"{' '.join(b.split())[:80]!r}" for b in bullets
                 if not any(theme in _norm(b) for theme in THEMES)]
    rest = blank
    for theme, want in THEMES.items():
        hits = [b for b in bullets if theme in _norm(b)]
        if not hits:
            problems.append(f"the first section lists no theme {theme[:60]!r}")
            continue
        if len(hits) > 1:
            problems.append(f"the first section lists the theme {theme[:60]!r} {len(hits)} times")
        rest = rest.replace(hits[0], "", 1)
        named = set(ID.findall(hits[0]))
        if not named:
            problems.append(f"the theme {theme[:60]!r} names no unit")
            continue
        problems += [f"the theme {theme[:60]!r} does not name {u}" for u in sorted(want - named)]
        problems += [f"the theme {theme[:60]!r} names {u}, not one of its units"
                     for u in sorted(named - want)]
    rest = BREAKING_SAID.sub("", rest)
    for heading, sbody in sections(rest):
        if re.search(r"known issues|sources|contributors", heading, re.I):
            continue
        allowed = ALLOWED_OUTSIDE.get(heading, set())
        problems += [f"unit id {m} outside a theme, under '{heading}'"
                     for m in UNIT_ID.findall(sbody) if m not in allowed]
    for heading, sbody in sections(blank):
        named = set(UNIT_ID.findall(sbody)) & CONTRIBUTORS
        if re.search(r"contributors", heading, re.I):
            problems += [f"the contributors heading does not name {u}"
                         for u in sorted(CONTRIBUTORS - named)]
        else:
            problems += [f"{u} is named outside the contributors heading, under '{heading}'"
                         for u in sorted(named)]
    if not any(re.search(r"contributors", h, re.I) for h, _b in sections(blank)):
        problems.append("the notes have no contributors heading")
    labels = changelog_sections(changelog)
    linked = {labels.get(a) for a in re.findall(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)", text)}
    want = "6.5.0" if "6.5.0" in labels.values() else "Unreleased"
    if want not in linked:
        problems.append(f"no link to the CHANGELOG's {want} section")
    return problems


def decision_rows(path: Path = DECISIONS) -> dict[str, str]:
    """Each decision id -> its whole row in the decisions log."""
    text = path.read_text(encoding="utf-8")
    return {m.group(1): m.group(0) for m in re.finditer(r"^\| (D\d{4}) \|.*$", text, re.M)}


def wont_fix(bugs: Path | None = None) -> dict[str, int]:
    """Each quality decision -> the bugs at Won't Fix whose Resolution section names it, in
    `bugs`, or where `BUGS` points when the call is made."""
    bugs = BUGS if bugs is None else bugs
    counts = dict.fromkeys(QUALITY, 0)
    for p in sorted(bugs.glob("BG*.md")):
        text = p.read_text(encoding="utf-8")
        status = re.search(r"^> \*\*Status:\*\* (.*)$", text, re.M)
        if not status or status.group(1).strip() != "Won't Fix":
            continue
        res = re.search(r"^## Resolution[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        for dec in counts:
            counts[dec] += bool(res and re.search(rf"\b{dec}\b", res.group(1)))
    return counts


def ruled_at(dec: str) -> str:
    """The commit that recorded `dec`'s row in the decisions log: the oldest commit whose change
    adds or removes the row, which is the one that added it, never HEAD, a later commit that
    edits the row in place, or one that removes it. That commit applied its Won't Fix list."""
    proc = _run("git", "-C", str(REPO), "log", "--reverse", "--format=%H", "-S", f"| {dec} |",
                "--", "sdlc-studio/decisions.md")
    commits = proc.stdout.split()
    if proc.returncode != 0 or not commits:
        raise AssertionError(f"git log found no commit recording {dec} (exit {proc.returncode}): "
                             f"{proc.stderr.strip()}")
    return commits[0]


def ruled_counts(decisions: tuple[str, ...] = ("D0564", "D0613")) -> dict[str, int]:
    """Each Won't Fix decision -> `wont_fix`'s count for it in the bug corpus as the commit that
    recorded the decision left it, never the working tree, so a bug reopened since, or a later
    Won't Fix bug citing the decision, leaves the count as ruled."""
    out = {}
    for dec in decisions:
        commit = ruled_at(dec)
        found = _run("git", "-C", str(REPO), "grep", "-l", "-F", dec, commit, "--",
                     "sdlc-studio/bugs")
        if found.returncode not in (0, 1):
            raise AssertionError(f"git grep failed at {commit}: {found.stderr.strip()}")
        with tempfile.TemporaryDirectory() as d:
            for ref in found.stdout.splitlines():
                blob = _run("git", "-C", str(REPO), "show", ref)
                if blob.returncode != 0:
                    raise AssertionError(f"git show {ref} failed: {blob.stderr.strip()}")
                (Path(d) / ref.rsplit("/", 1)[1]).write_text(blob.stdout, encoding="utf-8")
            out[dec] = wont_fix(Path(d))[dec]
    return out


def quality_problems(text: str, rows: dict[str, str],
                     closed: dict[str, int] | None) -> list[str]:
    """AC2: the quality theme states D0560's bar, the count the drive started from, the re-check
    by two independent seats (D0563) and both Won't Fix lists, and leaves the count at the cut to
    the disclosure line. Every number in a sentence about open defects, their severity or a Won't
    Fix list, anywhere but the disclosure line, is carried by the quality decision named nearest
    after it in that sentence (or, with none after, the nearest before), and each Won't Fix count
    equals the bugs at Won't Fix whose Resolution names its decision (`closed`, as
    `ruled_counts` reads them; None judges no count against the corpus)."""
    problems = []
    for unit in units(text):
        if COUNT_LINE.match(unit.strip()) or not OPEN_TALK.search(unit):
            continue
        counts = [(m.start(), m.group().replace(",", "")) for m in WHOLE.finditer(unit)]
        if not counts:
            continue
        named = [(m.start(), m.group()) for m in DECISION_ID.finditer(unit)]
        if not named:
            problems.append(f"a count with no decision named: {unit.strip()[:140]!r}")
            continue
        for at, value in counts:
            after = [d for pos, d in named if pos > at]
            dec = after[0] if after else [d for pos, d in named if pos < at][-1]
            if dec not in QUALITY:
                problems.append(f"{dec}, named for {value}, is not one of the decisions the 6.5 "
                                f"bar rests on")
            elif not re.search(rf"(?<![\d.]){value}(?!\d)", rows.get(dec, "")):
                problems.append(f"{dec} does not carry the count {value}")
    bullets = _blocks((sections(_blank(text)) or [("", "")])[0][1])[0]
    hits = [" ".join(b.split()) for b in bullets if next(iter(THEMES)) in _norm(b)]
    if not hits:
        return problems + ["no quality theme to read the bar from"]
    theme = hits[0]
    bar = re.search(r"fewer than (\d+) open bugs and none at Medium or above", rows["D0560"])
    if not bar or (f"fewer than {bar.group(1)} open defects and none at Medium or above"
                   not in theme):
        problems.append("the theme does not state D0560's bar")
    start = re.search(r"(\d+) bugs were open \((\d+) Low, (\d+) Medium\) after run ([\w-]+)",
                      rows["D0560"])
    if not start or (f"{start.group(1)} open bugs after run {start.group(4)}, {start.group(3)} "
                     f"of them Medium") not in theme:
        problems.append("the theme does not state the count the drive started from")
    recheck = [u for u in units(theme) if "re-checked every open bug at HEAD" in u]
    if not recheck or "D0563" not in recheck[0] or "second, independent" not in recheck[0]:
        problems.append("the theme does not state the re-check by two independent seats (D0563)")
    for dec, rx in (("D0564", r"approved (\d+) of"), ("D0613", r"(\d+) Low bugs move to Won't")):
        said = re.search(rf"\b(\d+)\b[^.;()]*\({dec}\)", theme)
        if not said:
            problems.append(f"the theme does not state {dec}'s Won't Fix list")
            continue
        carried = re.search(rx, rows.get(dec, ""))
        if not carried or carried.group(1) != said.group(1):
            problems.append(f"the theme gives {dec}'s Won't Fix list as {said.group(1)}, where "
                            f"{dec} approves {carried.group(1) if carried else 'no count'}")
        if closed is not None and closed.get(dec) != int(said.group(1)):
            problems.append(f"the bug corpus holds {closed.get(dec)} bugs at Won't Fix under "
                            f"{dec}, "
                            f"where the notes say {said.group(1)}")
    if not re.search(r"count this release ships with is the disclosure line", theme):
        problems.append("the theme does not leave the count at the cut to the disclosure line")
    return problems


def breaking_problems(text: str, entries: list[tuple[str, frozenset, str]]) -> list[str]:
    """AC3: the notes name every entry filed under Breaking, and say none is filed under Removed
    or Security exactly when none is. Before the cut each entry is known by its fragment's id;
    after it, a Breaking bullet whose text names no id is matched by count."""
    body = section(text, r"^Changed defaults and new refusals$") or ""
    flat = " ".join(_blank(body).split())
    said = BREAKING_SAID.search(flat)
    named = set(UNIT_ID.findall(said.group(1))) if said else set()
    filed = [ids for s, ids, _b in entries if s == "Breaking"]
    other = [s for s, _ids, _b in entries if s in ("Removed", "Security")]
    problems = []
    if other and NO_OTHER.search(flat):
        problems.append(f"the notes say no fragment is Removed or Security, but {len(other)} are")
    if not other and not NO_OTHER.search(flat):
        problems.append("the notes do not state that no 6.5 fragment is filed under Removed or "
                        "Security")
    if filed and not said:
        return problems + ["the section names no entry filed under Breaking"]
    known = set().union(*filed) if filed else set()
    problems += [f"the section does not name {u}, filed under Breaking"
                 for u in sorted(known - named)]
    if all(filed):
        problems += [f"the section names {u} as Breaking, which no Breaking entry records"
                     for u in sorted(named - known)]
    elif len(named) != len(filed):
        problems.append(f"the section names {len(named)} Breaking entries, where {len(filed)} "
                        f"are filed")
    return problems


def changed_problems(text: str, entries: list[tuple[str, frozenset, str]]) -> list[str]:
    """AC3: each listed change a 6.4 habit meets in exactly one bullet, saying what it must,
    beside what to do instead, no bullet but a listed change, and no text but the paragraph
    naming the Breaking entries outside them."""
    body = section(text, r"^Changed defaults and new refusals$")
    if body is None:
        return ["no 'Changed defaults and new refusals' section"]
    found, paras = _blocks(body)
    bullets = [" ".join(b.split()) for b in found]
    problems = [f"the section holds text outside its change bullets: {' '.join(p.split())[:80]!r}"
                for p in paras if not NO_OTHER.search(" ".join(p.split()))]
    for b in bullets:
        if "Instead:" not in b:
            problems.append(f"a change named with no replacement: {b[:90]!r}")
        elif len(re.findall(r"\w[\w-]*", b.partition("Instead:")[2])) < 3:
            problems.append(f"a change whose `Instead:` says nothing: {b[:90]!r}")
        named = [label for label, (names, _s, _i) in CHANGES.items() if re.search(names, b)]
        if not named:
            problems.append(f"a bullet no listed change names: {b[:90]!r}")
        elif len(named) > 1:
            problems.append(f"one bullet names {len(named)} listed changes ({', '.join(named)})")
    for label, (names, says, instead) in CHANGES.items():
        hits = [b for b in bullets if re.search(names, b)]
        if not hits:
            problems.append(f"the section never names {label}")
            continue
        if len(hits) > 1:
            problems.append(f"{label} is named by {len(hits)} bullets")
        hit = hits[0]
        problems += [f"{label} does not say {rx!r}" for rx in says
                     if not re.search(rx, hit.partition("Instead:")[0])]
        if not re.search(instead, hit.partition("Instead:")[2]):
            problems.append(f"{label} is named with no replacement beside it")
    return problems + breaking_problems(text, entries)


def false_refusal_problems(text: str, blocks: int | None) -> list[str]:
    """AC3: no sentence says a copied 6.4 card naming "the Primary persona, Sam" is refused while
    `persona_review.py check` finds nothing that blocks on the 6.4.0 cards verbatim (`blocks`).
    None, where the CLI could not be run, judges nothing."""
    if blocks is None or blocks > 0:
        return []
    return [f"a refusal the code does not make (the 6.4.0 cards verbatim report blocks={blocks}): "
            f"{u.strip()[:120]!r}" for u in units(text) if SAM.search(u) and REFUSED.search(u)]


def _steps(text: str) -> list[tuple[str, list[str]]]:
    """(script, arguments) of each `python3 .../scripts/<script>` step in the upgrade section's
    code, in order."""
    old = section(text, UPGRADE) or ""
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    out = []
    for line in (fence.group(1) if fence else "").splitlines():
        argv = shlex.split(line, comments=True)
        if argv[:1] == ["python3"] and argv[1:2] and "/scripts/" in argv[1]:
            out.append((argv[1].rsplit("/", 1)[1], argv[2:]))
    return out


def upgrade_problems(text: str) -> list[str]:
    """AC4: install PyYAML, then reinstall, then `migrate` and `migrate --apply`, with what each
    lists or writes for a 6.4 project as the notes say it. `config_problems` judges the keys and
    `bg1613_problems` the wait-timeout clause."""
    old = section(text, UPGRADE)
    if old is None:
        return ["no 'Upgrading from 6.4' section"]
    problems = []
    if not re.search(r"(?i)\breinstall\b", old) or "latest published release" not in old:
        problems.append("the path does not say to reinstall for the latest published release")
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    lines = (fence.group(1) if fence else "").splitlines()
    pip = [i for i, ln in enumerate(lines) if ln.strip() == "python3 -m pip install pyyaml"]
    curls = [i for i, ln in enumerate(lines) if ln.startswith("curl ")]
    if not curls:
        problems.append("the path gives no reinstall command")
    if not pip or (curls and pip[0] > curls[0]):
        problems.append("the path does not install PyYAML before reinstalling")
    given = {ln.strip() for ln in at_cut("docs/INSTALL.md").splitlines()}
    problems += [f"the reinstall line is not one docs/INSTALL.md gives: {lines[i][:90]!r}"
                 for i in curls if lines[i].strip() not in given]
    steps = _steps(text)
    dry = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" not in a]
    wet = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" in a]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the steps are not `migrate` then `migrate --apply`")
    flat = " ".join(old.split())
    para = lambda lead: re.search(rf"\*\*`{lead}`\*\*,? (.*?)(?= \*\*|$)", flat)  # noqa: E731
    dry_para, apply = (m.group(1) if m else "" for m in (para("migrate"), para("migrate --apply")))
    if not re.search(r"\bwrites nothing\b", dry_para):
        problems.append("the path does not say the dry run writes nothing")
    problems += [f"the path does not quote `{q}` as what the dry run lists"
                 for q in QUOTES.values() if f"`{q}`" not in dry_para]
    if not re.search(r"writes exactly what the dry run listed", apply) or not re.search(
            r"changes nothing else", apply):
        problems.append("the path does not say `migrate --apply` writes what the dry run listed "
                        "and nothing else")
    return problems


def stated_defaults(reference: str | None = None) -> dict:
    """The default 6.5's `reference-config.md` states for each key 6.5 adds, or None where it
    states none."""
    reference = at_cut(f"{SKILL_REL}/reference-config.md") if reference is None else reference
    out = {}
    for key, rx in NEW_KEYS.items():
        m = re.search(rx, reference, re.M)
        out[key] = m.group(1) if m else None
    return out


def config_problems(old: str, stated: dict) -> list[str]:
    """AC4: the upgrade section names each key 6.5 adds with the default `reference-config.md`
    states for it, and names no other key as one 6.5 adds."""
    said: dict[str, str] = {}
    for bullet in _blocks(old)[0]:
        m = re.match(r"- (.*?) default `([^`]*)`", " ".join(bullet.split()))
        if m:
            for key in re.findall(r"`([a-z_]+(?:\.[a-z_]+)+)`", m.group(1)):
                said[key] = m.group(2)
    problems = []
    for key, want in stated.items():
        if want is None:
            problems.append(f"reference-config.md states no default for {key}")
        elif key not in said:
            problems.append(f"the path does not name {key} with its default")
        elif said[key] != want:
            problems.append(f"the path gives {key} the default {said[key]!r}, and "
                            f"reference-config.md states {want!r}")
    problems += [f"the path names {key}, a key 6.5 does not add" for key in said
                 if key not in stated]
    return problems


def bug_status(bug: str = "BG1613") -> str:
    """`bug`'s status at the commit that cut 6.5.0, read from its file."""
    paths = sorted(BUGS.glob(f"{bug}-*.md"))
    if not paths:
        raise AssertionError(f"no {bug} file under sdlc-studio/bugs/ to read its status from")
    text = at_cut(paths[0].relative_to(REPO).as_posix())
    m = re.search(r"^> \*\*Status:\*\* (.*)$", text, re.M)
    return m.group(1).strip() if m else ""


def bg1613_problems(text: str, status: str) -> list[str]:
    """AC4: no sentence says `ci.wait_timeout_minutes` bounds a wait, and while BG1613 is open
    (`status`) the key's bullet says no script in 6.5.0 reads it and names BG1613."""
    flat = " ".join(text.split())
    problems = [f"a claim that ci.wait_timeout_minutes bounds a wait: {s[:120]!r}"
                for s in re.split(r"(?<=[.;])\s", flat) if WAIT_KEY in s and BOUNDS.search(s)]
    if status in CLOSED:
        return problems
    bullet = [" ".join(b.split()) for b in _blocks(section(text, UPGRADE) or "")[0]
              if b.startswith(f"- {WAIT_KEY}")]
    if not bullet or not re.search(r"no script in 6\.5\.0 reads it", bullet[0]) or (
            "BG1613" not in bullet[0]):
        problems.append(f"BG1613 is {status} at the cut, and the path does not say no script in "
                        f"6.5.0 reads ci.wait_timeout_minutes, naming BG1613")
    return problems


def _config(project: Path) -> dict[str, str]:
    import yaml  # noqa: PLC0415 - the shipped config reader needs it too
    path = project / "sdlc-studio" / ".config.yaml"
    return _flat(yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}


def run_steps(text: str, scripts: Path, project: Path) -> list[dict]:
    """What each of the notes' steps did, run in their order on `project`: its script, its
    arguments, its process, the files it changed, the config keys it changed, the project's
    `personas.standard` after it and its version stamp."""
    out = []
    for script, argv in _steps(text):
        before, cfg_before = _tree(project), _config(project)
        proc = _cli(scripts, project, script, *argv, "--format", "json")
        after, cfg_after = _tree(project), _config(project)
        stamp = project / "sdlc-studio" / ".version"
        out.append({
            "script": script, "argv": argv, "proc": proc,
            "moved": sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k)),
            "keys": sorted(k for k in set(cfg_before) | set(cfg_after)
                           if cfg_before.get(k) != cfg_after.get(k)),
            "standard": cfg_after.get("personas.standard"),
            "stamp": stamp.read_text(encoding="utf-8") if stamp.is_file() else ""})
    return out


def step_problems(text: str, runs: list[dict], variant: str) -> list[str]:
    """AC4: the notes' steps, as `run_steps` ran them on a 6.4 project of the kind `variant`
    names, do what the notes say: the dry run writes nothing and lists only what the notes
    quote, and `--apply` writes exactly the files and config keys it listed, stamped 6.5.0."""
    _how, kinds, moved_want, keys_want = VARIANTS[variant]
    problems = []
    flat = " ".join(text.split())
    for run in runs:
        script, argv, proc, moved = run["script"], run["argv"], run["proc"], run["moved"]
        shown = " ".join([script, *argv])
        if proc.returncode != 0:
            problems.append(f"the step `{shown}` is refused by the shipped CLI "
                            f"(exit {proc.returncode}): {proc.stderr.strip()[:120]}")
            continue
        if script != "migrate.py":
            problems.append(f"the step `{shown}` is not a `migrate` step")
            continue
        listed = json.loads(proc.stdout)["deterministic"]
        if "--apply" not in argv:
            if moved:
                problems.append(f"the dry run `{shown}` wrote {moved}")
            for d in listed:
                quote = QUOTES.get(d.get("kind"))
                if quote is None or quote not in d["detail"]:
                    problems.append(f"the dry run lists {d['detail']!r} for {variant}, which the "
                                    f"notes do not name")
                elif f"`{quote}`" not in flat:
                    problems.append(f"the dry run lists {d['detail']!r}, which the notes do not "
                                    f"quote")
            problems += [f"the dry run lists no {k} for {variant}" for k in kinds
                         if k not in {d.get("kind") for d in listed}]
            continue
        if moved != moved_want:
            problems.append(f"`{shown}` changed {moved} for {variant}, not {moved_want}")
        if 'skill_version: "6.5.0"' not in run["stamp"]:
            problems.append(f"`{shown}` did not stamp 6.5.0: {run['stamp']!r}")
        if run["keys"] != keys_want:
            problems.append(f"`{shown}` changed the config keys {run['keys']} for {variant}, not "
                            f"{keys_want}")
        if "personas.standard" in keys_want and run["standard"] != "report":
            problems.append(f"`{shown}` did not set personas.standard: report for {variant}")
    return problems


def cost_problems(text: str, reports: Path = REPORTS) -> list[str]:
    """AC5: each sentence or row stating a cost figure names a signed report of a run that built
    6.5, and each figure is one the report named nearest before it (or, with none before, the
    first after it) carries in its committed JSON."""
    problems = []
    for unit in units(text):
        if COUNT_LINE.match(unit.strip()):
            continue
        figures = [(m.start(), next(g for g in m.groups() if g).replace(",", ""))
                   for m in COST.finditer(unit)]
        if not figures:
            continue
        named = [(m.start(), m.group()) for m in REPORT_ID.finditer(unit)]
        if not named:
            problems.append(f"a cost figure with no report named: {unit.strip()[:140]!r}")
            continue
        for at, value in figures:
            before = [rpt for pos, rpt in named if pos < at]
            rpt = before[-1] if before else named[0][1]
            if rpt not in RUNS_65:
                problems.append(f"{rpt}, named for {value}, is not the report of a run that "
                                f"built 6.5")
                continue
            carried, why = report_figures(rpt, reports)
            if why:
                problems.append(f"{rpt}, named for {value}, {why}")
            elif value not in carried:
                problems.append(f"{rpt} does not carry the figure {value}")
    return problems


def setUpModule() -> None:
    """Three 6.4 projects made by v6.4.0's own `init.py` (bare, holding the 6.4.0 amigo cards as
    its own seat cards, and carrying `require_ac_verification`), and the 6.5.0 skill: the v6.5.0
    tag's tree, or before the tag this tree with its version read as 6.5.0, the cut's one change
    to it. A tree that is not a git clone holds no v6.4.0 tree: the checks that run the CLI are
    skipped there, naming why, and the checks of the text still run. A clone lacking the v6.4.0
    tag fails rather than skips."""
    top = _run("git", "-C", str(REPO), "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO.resolve():
        _FIX["skip"] = ("this tree is not a git clone, so it holds no v6.4.0 tree to make a "
                        "6.4 project from")
        return
    home = Path(tempfile.mkdtemp(prefix="us1327_"))
    _FIX["home"] = home
    skill64 = _extract("v6.4.0", home)
    if skill64 is None:
        raise AssertionError("this clone has no v6.4.0 tag to make a 6.4 project from: fetch tags")
    bare = home / "p64"
    bare.mkdir()
    proc = _cli(skill64 / "scripts", bare, "init.py", "run")
    if proc.returncode != 0:
        raise AssertionError(f"v6.4.0's init.py failed: {proc.stdout}{proc.stderr}")
    projects = {}
    for variant, (how, _k, _m, _c) in VARIANTS.items():
        project = home / f"v{len(projects)}"
        shutil.copytree(bare, project)
        if "cards" in how:
            seats = project / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            for card in sorted((skill64 / "templates" / "personas" / "amigos").glob("*.md")):
                shutil.copy(card, seats / card.name)
        if "legacy" in how:
            cfg = project / "sdlc-studio" / ".config.yaml"
            cfg.write_text(cfg.read_text(encoding="utf-8") + "\nrequire_ac_verification: true\n",
                           encoding="utf-8")
        projects[variant] = project
    skill65 = _extract(TAG, home)
    if skill65 is None:
        skill65 = home / "v6.5.0-pending" / "sdlc-studio"
        shutil.copytree(REPO / SKILL_REL, skill65,
                        ignore=shutil.ignore_patterns("tests", "__pycache__", ".local"))
        md = skill65 / "SKILL.md"
        md.write_text(re.sub(r'(?m)^(  version: )"[^"]+"$', r'\1"6.5.0"',
                             md.read_text(encoding="utf-8"), count=1), encoding="utf-8")
    _FIX.update(projects=projects, scripts=skill65 / "scripts")


def tearDownModule() -> None:
    if "home" in _FIX:
        shutil.rmtree(_FIX["home"], ignore_errors=True)


class ReleaseNotesTests(unittest.TestCase):

    def setUp(self) -> None:
        self.text = NOTES.read_text(encoding="utf-8")
        self.changelog = CHANGELOG.read_text(encoding="utf-8")

    def mutant(self, old: str, new: str) -> str:
        """The notes with `old`, which must occur exactly once, replaced."""
        self.assertEqual(1, self.text.count(old), f"mutant anchor not unique: {old[:60]!r}")
        return self.text.replace(old, new)

    def assertFlags(self, problems: list[str], expected: str) -> None:
        self.assertTrue([p for p in problems if expected in p],
                        f"no problem naming {expected!r}: {problems}")

    def needs_cli(self) -> None:
        """Skip the rest of a test where `setUpModule` found no git clone to build from, once a
        second signal agrees: a tree holding `.git` is a clone, and its CLI checks must run."""
        if "skip" in _FIX:
            self.assertFalse((REPO / ".git").exists(), "a git clone skipped the CLI checks")
            self.skipTest(str(_FIX["skip"]))

    def project(self, variant: str) -> Path:
        """A fresh copy of the 6.4 project `variant` names."""
        d = Path(tempfile.mkdtemp(prefix="us1327_p_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        shutil.copytree(_FIX["projects"][variant], d / "p")
        return d / "p"

    def test_the_notes_lead_with_what_changed_for_you(self) -> None:
        """AC1. MUTANTS: the tree at HEAD, which holds no notes (setUp cannot read them); the
        6.4.0 notes as they stand (headline '6.4.0 is the current release') and with the version
        changed (no 6.5 theme); a draft composed from the 6.5 fragments, whose ids sit outside
        any theme; a theme with its units cut, one short (US1326 dropped) or one over (US1239
        added); contributor tooling in a theme (US1190) or under Sources (US1313); a ninth
        theme, as a bullet or a paragraph; a theme listed twice; the `#unreleased` link left in
        place after the cut moved 6.5's entries under [6.5.0]."""
        lead = lambda text: lead_problems(text, self.changelog)  # noqa: E731
        copied = shipped(NOTES_64_REL)
        self.assertFlags(lead(copied), "the opening")
        self.assertFlags(lead(copied.replace("6.4.0", "6.5.0")), "lists no theme")
        fragments = "\n".join(body for _s, _ids, body in entries_65(self.changelog))
        self.assertTrue(UNIT_ID.search(fragments), "premise: the 6.5 entries name units")
        composed = self.mutant("\n## Changed defaults", f"\n{fragments}\n\n## Changed defaults")
        self.assertFlags(lead(composed), "outside a theme")
        self.assertFlags(lead(self.mutant(" Delivered by US1314,\n  US1324 and US1326.", "")),
                         "names no unit")
        self.assertFlags(lead(self.mutant("US1324 and US1326.", "and US1324.")),
                         "does not name US1326")
        self.assertFlags(lead(self.mutant("Delivered by US1236, US1237 and US1238.",
                                          "Delivered by US1236, US1237, US1239 and US1238.")),
                         "names US1239, not one of its units")
        self.assertFlags(lead(self.mutant("Delivered by US1192, US1193,",
                                          "Delivered by US1190, US1192, US1193,")),
                         "US1190 is named outside the contributors heading")
        self.assertFlags(lead(self.mutant("| PyYAML is required | US1296",
                                          "| PyYAML is required | US1313, US1296")),
                         "US1313 is named outside the contributors heading")
        self.assertFlags(lead(self.mutant("Delivered by US1190, US1191 and US1313.",
                                          "Delivered by US1190 and US1191.")),
                         "the contributors heading does not name US1313")
        self.assertFlags(lead(self.mutant("## For contributors to this repository",
                                          "## Tooling for this repository")),
                         "no contributors heading")
        self.assertFlags(lead(self.mutant("reads it (BG1613).", "reads it (BG1613, BG1497).")),
                         "unit id BG1497 outside a theme, under 'Upgrading from 6.4'")
        ninth = "- **Installs are faster.** Install is quicker.\n"
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"{ninth}\n## Changed defaults")), "not one of the eight")
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"\n{ninth[2:]}\n## Changed defaults")),
                         "outside its theme bullets")
        self.assertFlags(lead(self.mutant(
            "\n## Changed defaults",
            "- **A red CI run on main is answered by a written policy.**\n\n## Changed defaults")),
            "2 times")
        self.assertEqual([], lead(self.text))

        before = re.sub(r"#650---\d{4}-\d{2}-\d{2}\)", "#unreleased)", self.text)
        self.assertIn("](../CHANGELOG.md#unreleased)", before)
        cut = "## [Unreleased]\n\n## [6.5.0] - 2026-11-26\n\n## [6.4.0] - 2026-11-16\n"
        precut = "## [Unreleased]\n\n## [6.4.0] - 2026-11-16\n"
        self.assertEqual([], lead_problems(before, precut))
        self.assertFlags(lead_problems(before, cut), "6.5.0 section")
        self.assertEqual([], lead_problems(before.replace("#unreleased)", "#650---2026-11-26)"),
                                           cut))

    def test_the_quality_figures_name_their_decisions(self) -> None:
        """AC2. MUTANTS: the 6.4.0 notes with the version changed (no quality theme); a count with
        its decision cut (D0560 dropped from the bar); a count the named decision does not carry
        (139 read as 140, 99 as 98); a count read against a decision the bar does not rest on
        (D0613 renamed D0630); an open-defect count stated outside the disclosure line, with no
        decision or with D0560 named; the re-check's second seat cut; the disclosure sentence
        reworded; a decisions log whose D0564 row approves another count; a Won't Fix count the
        bug corpus as the ruling left it does not hold, and the counts read from the working
        tree, where a D0613 bug reopened since (BG0971) and a later Won't Fix bug citing D0564
        would move them to 127 and 140. `wont_fix` is checked on a fixture corpus: a bug at Won't
        Fix naming the decision outside its Resolution, or naming it while still open, is not
        counted. `ruled_at` naming any commit but the one that added each row (622cb4156 for D0564,
        e8bed39a5 for D0613), such as HEAD, fails here as on the fixture repository of
        `RulingCommitTests`. The corpus is read through git, so that subtest alone is skipped in a
        tree that is not a git clone."""
        rows = decision_rows()
        quality = lambda text: quality_problems(text, rows, None)  # noqa: E731
        self.assertFlags(quality(shipped(NOTES_64_REL).replace("6.4.0", "6.5.0")),
                         "no quality theme")
        self.assertFlags(quality(self.mutant("Medium or above (D0560).**", "Medium or above.**")),
                         "a count with no decision named")
        self.assertFlags(quality(self.mutant("139 Low bugs", "140 Low bugs")),
                         "D0564 does not carry the count 140")
        self.assertFlags(quality(self.mutant("99 of them Medium", "98 of them Medium")),
                         "the count the drive started from")
        self.assertFlags(quality(self.mutant("(D0613)", "(D0630)")),
                         "D0630, named for 128, is not one of the decisions")
        stray = "\n6.5 ships with 46 open defects, all Low.\n"
        self.assertFlags(quality(self.mutant("\n**v6.5.0 discloses",
                                             f"{stray}\n**v6.5.0 discloses")),
                         "a count with no decision named")
        named = "\n6.5 ships with 46 open defects, all Low (D0560).\n"
        self.assertFlags(quality(self.mutant("\n**v6.5.0 discloses",
                                             f"{named}\n**v6.5.0 discloses")),
                         "D0560 does not carry the count 46")
        self.assertFlags(quality(self.mutant("a second, independent", "a second")),
                         "re-check by two independent seats")
        self.assertFlags(quality(self.mutant("The count this release ships",
                                             "The tally this release ships")),
                         "disclosure line")
        moved = {**rows, "D0564": rows["D0564"].replace("approved 139 of", "approved 138 of")}
        self.assertFlags(quality_problems(self.text, moved, None), "where D0564 approves 138")
        self.assertEqual([], quality(self.text))

        head = "# BG{n}: x\n\n> **Status:** {status}\n\n## Summary\n\n{summary}\n\n"
        with tempfile.TemporaryDirectory() as d:
            for n, status, summary, resolution in (
                    ("0001", "Won't Fix", "x", "Approved under D0613."),
                    ("0002", "Won't Fix", "Named in D0613 here only.", "Approved by the operator."),
                    ("0003", "Open", "x", "Proposed under D0613."),
                    ("0004", "Won't Fix", "x",
                     "Approved under D0564.\n\n## Revision History\n\nD0613")):
                (Path(d) / f"BG{n}-x.md").write_text(
                    head.format(n=n, status=status, summary=summary)
                    + f"## Resolution\n\n{resolution}\n", encoding="utf-8")
            self.assertEqual({"D0560": 0, "D0563": 0, "D0564": 1, "D0613": 1}, wont_fix(Path(d)))

        with self.subTest("the Won't Fix counts, read from the corpus as each ruling left it"):
            self.needs_cli()
            for dec, added in (("D0564", "622cb4156"), ("D0613", "e8bed39a5")):
                commit = ruled_at(dec)
                self.assertTrue(commit.startswith(added), f"{dec} read at {commit}, not {added}")
                at, before = (_run("git", "-C", str(REPO), "show", f"{ref}:{DECISIONS_REL}")
                              for ref in (commit, f"{commit}^"))
                self.assertIn(f"| {dec} |", at.stdout, f"{dec}'s row is not in the log at {commit}")
                self.assertNotIn(f"| {dec} |", before.stdout,
                                 f"{dec}'s row is already in the log before {commit}")
            ruled = ruled_counts()
            self.assertEqual([], quality_problems(self.text, rows, ruled))
            self.assertFlags(quality_problems(self.mutant("139 Low bugs", "140 Low bugs"), rows,
                                              ruled), "where the notes say 140")
            self.assertFlags(quality_problems(self.text, rows, {**ruled, "D0613": 127}),
                             "the bug corpus holds 127 bugs at Won't Fix under D0613")
            # The live corpus moved after the rulings: a D0613 bug reopened, and a later Won't
            # Fix bug citing D0564. The counts read as ruled stay where they were.
            with tempfile.TemporaryDirectory() as d:
                live = Path(d) / "bugs"
                shutil.copytree(BUGS, live)
                for bug in live.glob("BG0971-*.md"):
                    bug.write_text(re.sub(r"(?m)^> \*\*Status:\*\* .*$", "> **Status:** Open",
                                          bug.read_text(encoding="utf-8"), count=1),
                                   encoding="utf-8")
                (live / "BG-ZZZZZZZZ-a-later-wont-fix-fixture.md").write_text(
                    "# BG9999: later\n\n> **Status:** Won't Fix\n\n## Resolution\n\n"
                    "Won't Fix on the grounds D0564 accepted.\n", encoding="utf-8")
                self.assertEqual(wont_fix(BUGS)["D0564"] + 1, wont_fix(live)["D0564"],
                                 "premise: the later bug moves the live D0564 count")
                with mock.patch.dict(ruled_counts.__globals__, BUGS=live):
                    self.assertEqual(ruled, ruled_counts())

    def test_every_changed_behaviour_names_what_to_do(self) -> None:
        """AC3. MUTANTS: a section copied from the entries filed under Changed alone, which never
        names the delegated signature (filed under Added); the PyYAML bullet with its 'Instead:'
        cut; an added bullet whose 'Instead:' says nothing, one no listed change names, and a
        change given as a paragraph; a Breaking entry left out (BG1063), and one named that no
        entry files (US1296); the no-Removed statement cut, and kept beside a Removed entry; a
        bullet naming two listed changes; the persona bullet with its exit 1 cut; the US1054
        fragment's claim that a copied 6.4 card naming "the Primary persona, Sam" is refused,
        which `persona_review.py check` refutes on the 6.4.0 cards verbatim (that subtest alone
        is skipped in a tree that is not a git clone). After the cut a Breaking bullet that names
        no id is matched by count."""
        entries = entries_65(self.changelog)
        self.assertGreater(len(entries), 1, "premise: the 6.5 entries are read")
        changed = ("## Changed defaults and new refusals\n\n"
                   + "\n".join(b for s, _ids, b in entries if s == "Changed") + "\n")
        self.assertFlags(changed_problems(changed, entries),
                         "never names the delegated signature")
        self.assertFlags(changed_problems(self.mutant(
            "\n  Instead: run `python3 -m pip install pyyaml` before installing or upgrading the "
            "skill.", ""), entries), "a change named with no replacement")
        tail = "\n## Upgrading from 6.4"
        for bullet, expected in (
                ("- **`foo` now refuses bar.** Instead: .\n", "`Instead:` says nothing"),
                ("- **`foo` now refuses bar.** Instead: pass `--bar` to keep it.\n",
                 "a bullet no listed change names"),
                ("\n`foo` now refuses bar. Instead: pass `--bar` to keep it.\n",
                 "outside its change bullets")):
            with self.subTest(added=bullet):
                self.assertFlags(changed_problems(self.mutant(tail, f"{bullet}{tail}"), entries),
                                 expected)
        self.assertFlags(changed_problems(self.mutant(
            "Filed under Breaking: US1299 and BG1063.", "Filed under Breaking: US1299."),
            entries), "does not name BG1063, filed under Breaking")
        self.assertFlags(changed_problems(self.mutant(
            "Filed under Breaking: US1299 and BG1063.",
            "Filed under Breaking: US1299, US1296 and BG1063."), entries),
            "names US1296 as Breaking")
        self.assertFlags(changed_problems(self.mutant(
            "Filed under Breaking: US1299 and BG1063.", "Breaking: none."), entries),
            "names no entry filed under Breaking")
        self.assertFlags(changed_problems(self.mutant(
            "No 6.5 fragment is filed under Removed or Security. ", ""), entries),
            "do not state that no 6.5 fragment")
        self.assertFlags(breaking_problems(self.text, [*entries, ("Removed", frozenset(), "- x")]),
                         "but 1 are")
        self.assertFlags(changed_problems(self.mutant(
            "- **An RFC gains a Delivered status.**",
            "- **An RFC gains a Delivered status, and `file_finding.py file` refuses a "
            "duplicate.**"), entries), "names 2 listed changes")
        self.assertFlags(changed_problems(self.mutant(
            "`persona_resolve.py resolve` exits 1, and",
            "`persona_resolve.py resolve` refuses, and"),
            entries), "does not say '`persona_resolve\\\\.py resolve` exits 1'")
        self.assertEqual([], changed_problems(self.text, entries))

        cut = ("## [Unreleased]\n\n## [6.5.0] - 2026-11-26\n\n### Breaking\n\n- **PyYAML.** Gone.\n"
               "- **The key is retired.** Gone.\n\n### Fixed\n\n- **Mended (BG1655).**\n\n"
               "## [6.4.0] - 2026-11-16\n")
        after = entries_65(cut, FRAGMENTS)
        self.assertEqual(["Breaking", "Breaking", "Fixed"], [s for s, _i, _b in after])
        self.assertEqual([], breaking_problems(self.text, after))
        one = cut.replace("- **The key is retired.** Gone.\n", "")
        self.assertFlags(breaking_problems(self.text, entries_65(one, FRAGMENTS)),
                         "names 2 Breaking entries, where 1 are filed")

        sam = self.mutant("\n  Instead: run `persona_review.py check`",
                          " A copied 6.4 product card naming \"the Primary persona, Sam\" is "
                          "refused.\n  Instead: run `persona_review.py check`")
        self.assertFlags(false_refusal_problems(sam, 0), "a refusal the code does not make")
        self.assertEqual([], false_refusal_problems(sam, 1))
        self.assertEqual([], false_refusal_problems(sam, None))
        with self.subTest("the 6.4.0 cards verbatim, judged by the 6.5.0 persona standard"):
            self.needs_cli()
            proc = _cli(_FIX["scripts"], self.project("a 6.4 project holding its own seat cards"),
                        "persona_review.py", "check", "--format", "json")
            self.assertEqual(0, proc.returncode, proc.stderr)
            blocks = json.loads(proc.stdout)["summary"]["blocks"]
            self.assertFlags(false_refusal_problems(sam, blocks), "blocks=0")
            self.assertEqual([], false_refusal_problems(self.text, blocks))

    def test_the_64_upgrade_path_is_given(self) -> None:
        """AC4. MUTANTS: the PyYAML install cut, or given after the reinstall; notes telling a 6.4
        project a reinstall is all it needs (no `migrate` lines); the two `migrate` steps in the
        wrong order; a step naming a flag the shipped CLI refuses (`--write` for `--apply`); the dry
        run's 'writes nothing' cut; the reinstall URL misspelt (`instal.sh`); `--apply` said to
        write more than the dry run listed; the dry run's version stamp misquoted, and its persona
        line unquoted; a default `reference-config.md` contradicts (`2` for `1`);
        `reference-config.md` with a default moved, and with a row cut; `review.rendered_paths` left
        out, and a key 6.5 does not add named; a claim that `ci.wait_timeout_minutes` bounds a wait;
        the BG1613 clause cut while BG1613 is open, or with BG1613 alone cut; a `migrate.py` that
        writes a file and a config key of its own, on a bare project and on one holding seat cards.
        The notes' own steps are run on three projects v6.4.0's `init.py` made: in a tree that is
        not a git clone that part is skipped, and every check of the text still runs."""
        old = section(self.text, UPGRADE)
        steps = [ln for ln in old.splitlines() if "/migrate.py" in ln and ln.startswith("python3")]
        self.assertEqual(2, len(steps), steps)
        self.assertFlags(upgrade_problems(self.mutant("python3 -m pip install pyyaml\ncurl",
                                                      "curl")),
                         "does not install PyYAML before reinstalling")
        swapped = self.mutant("python3 -m pip install pyyaml\ncurl -fsSL", "curl -fsSL")
        swapped = swapped.replace(steps[0], f"python3 -m pip install pyyaml\n{steps[0]}", 1)
        self.assertFlags(upgrade_problems(swapped), "does not install PyYAML before reinstalling")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps) + "\n", "")),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps),
                                                      "\n".join(reversed(steps)))),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("main/install.sh |", "main/instal.sh |")),
                         "not one docs/INSTALL.md gives")
        self.assertFlags(upgrade_problems(self.mutant("is the dry run: it writes nothing.",
                                                      "is the dry run.")),
                         "does not say the dry run writes nothing")
        self.assertFlags(upgrade_problems(self.mutant("writes exactly what the dry run listed",
                                                      "writes what it finds")),
                         "writes what the dry run listed")
        self.assertFlags(upgrade_problems(self.mutant("also `set personas.standard: report`",
                                                      "also the persona standard")),
                         "does not quote `set personas.standard: report`")
        self.assertEqual([], upgrade_problems(self.text))

        stated = stated_defaults()
        self.assertEqual({"personas.standard": "block", "ci.wait_timeout_minutes": "30",
                          "ci.rerun_limit": "1", "review.rendered_paths": "[]"}, stated,
                         "premise: reference-config.md states the four keys' defaults")
        path = lambda text: section(text, UPGRADE)  # noqa: E731
        self.assertFlags(config_problems(path(self.mutant("- `ci.rerun_limit`, default `1`:",
                                                          "- `ci.rerun_limit`, default `2`:")),
                                         stated), "reference-config.md states '1'")
        reference = at_cut(f"{SKILL_REL}/reference-config.md")
        moved = re.sub(r"(?m)^(\| `personas\.standard` \| )`block`", r"\g<1>`report`", reference)
        self.assertFlags(config_problems(old, stated_defaults(moved)),
                         "reference-config.md states 'report'")
        cut = re.sub(r"(?m)^\| `ci\.rerun_limit` \|.*\n", "", reference)
        self.assertFlags(config_problems(old, stated_defaults(cut)),
                         "states no default for ci.rerun_limit")
        start = self.text.index("- `review.rendered_paths`, default")
        dropped = self.text[:start] + self.text[self.text.index("\n## What the 6.5 runs", start):]
        self.assertFlags(config_problems(path(dropped), stated),
                         "does not name review.rendered_paths")
        extra = self.mutant("- `ci.rerun_limit`, default", "- `sprint.fresh_session`, default "
                            "`warn`: x.\n- `ci.rerun_limit`, default")
        self.assertFlags(config_problems(path(extra), stated),
                         "names sprint.fresh_session, a key 6.5 does not add")
        self.assertEqual([], config_problems(old, stated))

        status = bug_status("BG1613")
        bounds = self.mutant("documented as the limit on the one blocking watch",
                             "bounds the one blocking watch")
        self.assertFlags(bg1613_problems(bounds, "Fixed"), "bounds a wait")
        cut = self.mutant(", but no script in 6.5.0 reads it (BG1613).", ".")
        self.assertFlags(bg1613_problems(cut, "Open"), "BG1613 is Open at the cut")
        self.assertEqual([], bg1613_problems(cut, "Fixed"))
        self.assertFlags(bg1613_problems(self.mutant("reads it (BG1613).", "reads it."), "Open"),
                         "naming BG1613")
        self.assertEqual([], bg1613_problems(self.text, status))

        self.needs_cli()
        scripts = _FIX["scripts"]
        bare, cards = "a 6.4 project", "a 6.4 project holding its own seat cards"
        # The notes' own steps run once on each project; a mutant of the notes' prose alone is
        # judged against those runs, since its steps are the same.
        runs = {v: run_steps(self.text, scripts, self.project(v)) for v in VARIANTS}
        refused = self.mutant('migrate.py" --apply ', 'migrate.py" --write ')
        self.assertFlags(step_problems(refused, run_steps(refused, scripts, self.project(bare)),
                                       bare), "refused by the shipped CLI")
        misquoted = self.mutant("(skill 6.4.0 -> 6.5.0)`", "(skill 6.3.0 -> 6.5.0)`")
        self.assertEqual(_steps(self.text), _steps(misquoted))
        self.assertFlags(step_problems(misquoted, runs[bare], bare), "do not quote")
        unquoted = self.mutant("also `set personas.standard: report`", "also the persona line")
        self.assertFlags(step_problems(unquoted, runs[cards], cards), "do not quote")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "migrate.py").write_text(_STRAY, encoding="utf-8")
            stray = step_problems(self.text, run_steps(self.text, Path(d), self.project(bare)),
                                  bare)
            held = step_problems(self.text, run_steps(self.text, Path(d), self.project(cards)),
                                 cards)
        self.assertFlags(stray, "the dry run `migrate.py` wrote")
        self.assertFlags(stray, "not ['sdlc-studio/.version']")
        self.assertFlags(stray, "did not stamp 6.5.0")
        self.assertFlags(stray, "changed the config keys ['stray']")
        self.assertFlags(held, "the dry run lists no persona-standard")
        self.assertFlags(held, "did not set personas.standard: report")
        for variant in VARIANTS:
            with self.subTest(variant):
                self.assertEqual([], step_problems(self.text, runs[variant], variant))

    def test_every_cost_figure_names_its_signed_report(self) -> None:
        """AC5. MUTANTS: a figure's row with its report cut; a dollar figure and a points figure
        each changed; a figure's report renamed to one that does not carry it (RPT0036) and to
        one that is not a 6.5 run's (RPT0034); a sum across reports no single report carries
        ($2,240 over 671 points); two reports in one sentence with their figures swapped; the
        named report's committed JSON unsigned, and absent."""
        figures = [m for u in units(self.text) for m in COST.finditer(u)]
        self.assertGreaterEqual(len(figures), 22, "premise: the notes state cost figures")
        self.assertFlags(cost_problems(self.mutant("| RPT0035 | sixteen |", "| | sixteen |")),
                         "a cost figure with no report named")
        self.assertFlags(cost_problems(self.mutant("$102.01", "$120.01")),
                         "RPT0035 does not carry the figure 120.01")
        self.assertFlags(cost_problems(self.mutant("| 51 points |", "| 52 points |")),
                         "RPT0035 does not carry the figure 52")
        self.assertFlags(cost_problems(self.mutant("| RPT0035 | sixteen |",
                                                   "| RPT0036 | sixteen |")),
                         "RPT0036 does not carry the figure 102.01")
        self.assertFlags(cost_problems(self.mutant("| RPT0035 | sixteen |",
                                                   "| RPT0034 | sixteen |")),
                         "is not the report of a run that built 6.5")
        # Two reports in one sentence: each figure is read against the report named before it.
        paired = "\nRPT0044 recorded $161.82 and RPT0045 recorded $362.06.\n"
        self.assertEqual([], cost_problems(self.mutant("\n## Known issues",
                                                       f"{paired}\n## Known issues")))
        swapped = "\nRPT0044 recorded $362.06 and RPT0045 recorded $161.82.\n"
        self.assertFlags(cost_problems(self.mutant("\n## Known issues",
                                                   f"{swapped}\n## Known issues")),
                         "RPT0044 does not carry the figure 362.06")
        total = "\nRPT0045 closed the drive at $2,240 over 671 points.\n"
        summed = cost_problems(self.mutant("\n## Known issues", f"{total}\n## Known issues"))
        self.assertFlags(summed, "RPT0045 does not carry the figure 2240")
        self.assertFlags(summed, "RPT0045 does not carry the figure 671")
        with tempfile.TemporaryDirectory() as d:
            for n in sorted(RUNS_65):
                page = json.loads((REPORTS / f"{n}.json").read_text(encoding="utf-8"))
                if n == "RPT0044":
                    page["signature"] = None
                if n != "RPT0045":
                    (Path(d) / f"{n}.json").write_text(json.dumps(page), encoding="utf-8")
            fixture = cost_problems(self.text, Path(d))
        self.assertFlags(fixture, "RPT0044, named for 55, is not signed")
        self.assertFlags(fixture, "RPT0045, named for 77, has no committed JSON")
        self.assertEqual([], cost_problems(self.text))


class RulingCommitTests(unittest.TestCase):
    """`ruled_at` names the commit that added a decision's row, and `ruled_counts` reads the
    corpus there, on a repository built here, so it runs in any tree with git on the path."""

    BUG = "# BG{n}: x\n\n> **Status:** {status}\n\n## Resolution\n\nWon't Fix under D0564.\n"

    def commit(self, root: Path, row: str | None, statuses: dict[str, str], message: str) -> str:
        """Write the decisions log holding `row` (or none) and each bug at its status, commit
        them, and return the commit."""
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "decisions.md").write_text(
            "# Decisions\n\n| ID | Decision |\n| --- | --- |\n" + (f"{row}\n" if row else ""),
            encoding="utf-8")
        for n, status in statuses.items():
            (bugs / f"BG{n}-x.md").write_text(self.BUG.format(n=n, status=status), encoding="utf-8")
        ident = ("-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false")
        gitutil.git([*ident, "add", "-A"], cwd=root)
        gitutil.git([*ident, "commit", "-q", "-m", message], cwd=root)
        return gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()

    def test_the_ruling_commit_is_the_one_that_added_the_row(self) -> None:
        """MUTANTS: `ruled_at` returning HEAD; the newest commit whose change adds or removes the
        row (`commits[-1]`); the log read newest first (`--reverse` dropped); a decision with no
        row read as a commit rather than refused. The fixture adds D0564's row with two bugs at
        Won't Fix, then edits the row in place and reopens one bug, then removes the row and
        reopens the other: HEAD holds none at Won't Fix, the edit one, the ruling two."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], cwd=root)
            self.commit(root, None, {"0001": "Open", "0002": "Open"}, "base")
            ruled = self.commit(root, "| D0564 | approve two |",
                                {"0001": "Won't Fix", "0002": "Won't Fix"}, "rule")
            self.commit(root, "| D0564 | approve two, as amended |",
                        {"0001": "Open", "0002": "Won't Fix"}, "amend the row in place")
            head = self.commit(root, None, {"0001": "Open", "0002": "Open"}, "remove the row")
            self.assertNotEqual(ruled, head)
            self.assertEqual(0, wont_fix(root / "sdlc-studio" / "bugs")["D0564"],
                             "premise: HEAD's corpus holds no bug at Won't Fix")
            with mock.patch.dict(ruled_at.__globals__, REPO=root):
                self.assertEqual(ruled, ruled_at("D0564"))
                self.assertEqual({"D0564": 2}, ruled_counts(("D0564",)))
                with self.assertRaisesRegex(AssertionError, "no commit recording D0999"):
                    ruled_at("D0999")


if __name__ == "__main__":
    unittest.main()
