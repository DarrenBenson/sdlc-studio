"""US1136: the v6.3.0 release notes lead with what changed for the person using it.

The reader is a founder-engineer on 6.2.0 deciding whether to take 6.3. Each check is a function
returning its problems, run on the notes and on a control it must refuse: the 6.2.0 notes with
the version changed, a draft composed from the changelog fragments, a theme with its units cut, a
changed default with its replacement cut, a breaking change no fragment records, a figure with
its source cut or its value changed. The figures `figure_sources` pins are read from their
sources when the test runs, never typed here. The release-strategy, lane-brief, stale-selector,
Cursor-base, commit-msg-hook and agent-definition bullets are then run on the 6.3.0 skill, and
the upgrade path by running the notes' own steps on a project v6.2.0's `init.py` created.

The 6.3.0 skill is the v6.3.0 tag's tree once the tag exists, and before then this tree with its
version read as 6.3.0, so the checks judge 6.3.0's own CLI before the cut and after it. The
CHANGELOG link is judged against the layout the CHANGELOG has at the time: `[Unreleased]` before
the cut, `[6.3.0]` after it.
"""
# test-census-subject: docs/release-notes-v6.3.0.md
from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_REL = ".claude/skills/sdlc-studio"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.append(str(REPO / SKILL_REL / "scripts" / "tests"))
import gitutil  # noqa: E402
from test_lean_release_notes_v6 import (  # noqa: E402
    NOT_A_FIGURE, UNIT_ID, _blank, changelog_sections, section, sections, units)
from test_lean_release_notes_v61 import _norm, _run  # noqa: E402
from test_lean_release_notes_v62 import (  # noqa: E402
    _blocks, _cli, _const, _extract, _figure, _tree, pin_problems)

NOTES = REPO / "docs" / "release-notes-v6.3.0.md"
NOTES_62 = REPO / "docs" / "release-notes-v6.2.0.md"
CHANGELOG = REPO / "CHANGELOG.md"
FRAGMENTS = REPO / "changelog.d"
REPORTS = REPO / "sdlc-studio" / "reports"
BUGS = REPO / "sdlc-studio" / "bugs"

#: Each theme of the first section -> the units its bullet names, and no others.
THEMES = {
    "a run's cost is measured on whichever harness ran it":
        {"US0986", "US0987", "US0988", "US0989", "US1127"},
    "the report states the run's cost in us dollars and shows where it went":
        {"US1122", "US1123", "US1124", "US1135"},
    "a lane runs headless in any harness's cli, lands in one command and spawns lean agents":
        {"US1126", "US1120", "US1132"},
    "the gates and commit checks are faster and truer": {"US1112", "US1113", "US1133"},
}
#: What a figure's sentence or row may name as its source.
SOURCE = re.compile(r"RPT\d{4}|(?i:changelog)|known-issues|brief states|prompt template")
#: The release numbers themselves, and an exit status, are not figures.
RELEASE = re.compile(r"\b6\.[23]\b(?!\.\d)|\b(?:at )?exits? \d\b")
COUNT_LINE = re.compile(r"^\*\*v6\.3\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$")
NO_BREAKING = re.compile(r"No 6\.3 fragment is filed under Breaking or Removed\.")
SECURITY_ROW = re.compile(r"^\| Security fix \| BG1213 \|", re.M)
AGENTS = (".claude/agents/sdlc-builder.md", ".claude/agents/sdlc-reviewer.md")
#: Each change a 6.2 habit meets, label -> (what names its bullet, what the bullet must also
#: say, what its `Instead:` clause must carry).
CHANGES = {
    "release_strategy": (r"`release_strategy` now ships as",
                         (r"no branch and no pull request", r"6\.2's `pr-required` default"),
                         r"`release_strategy: pr-required`"),
    "lane land": (r"`sprint\.py lane land`, not the builder,",
                  (r"no longer prints a commit step or a `critic\.py self-check record` command",
                   r"`sdlc-studio/\.local/lane/`"),
                  r"`sprint\.py lane land --worktree <path> --units <id>`"),
    "the tool-call budget": (r"tool-call budget", (r"`HANDOFF\.md`",), r"below \d+k tokens"),
    "the agent definitions": (r"`init` drafts the `sdlc-builder` and `sdlc-reviewer`",
                              (r"`\.claude/agents/`", r"only if absent"),
                              r"delete it and run `init\.py run` again, which changes no other file"),
    "the stale selector": (r"`gate\.py --run-tests` refuses", (r"exits 2 before any test runs",),
                           r"correct or remove the selector"),
    "the meter selection": (r"no longer guesses between harnesses",
                            (r"name every candidate", r"`opencode\.db`"),
                            r"set `SDLC_STUDIO_HARNESS`"),
    "the Cursor base security fix": (r"^- \*\*Security fix:",
                                     (r"`SDLC_STUDIO_CURSOR_API`", r"refused before any request",
                                      r"cleartext"), r"an https base"),
    "the verify workers": (r"runs criteria side by side", (r"`SDLC_VERIFY_WORKERS`",),
                           r"`SDLC_VERIFY_WORKERS=1`"),
    "the Refs refusal": (r"given `--write-trailers` refuses a `Refs:` line",
                         (r"two or more ids", r"runs `--strict` alone, so it meets no new refusal",
                          r"under `--strict` refuses a `Refs:` line"), r"`Mentions: <id>`"),
    "the verifier process group": (r"whole process group",
                                   (r"SIGTERM, SIGINT and SIGHUP", r"listed under Known issues",
                                    r"no longer reaches a running verifier"),
                                   r"background children"),
    "the light APPROVE": (r"light APPROVE can stop counting", (r"`--tier light`",), r"full tier"),
    "the report cost rows": (r"new cost rows", (r"re-derives unchanged",), r"`pricing\.models`"),
    "the AGENTS.md starter": (r"`AGENTS\.md` starter is shorter",
                              (r"`reference-doctrine\.md#working-habits`", r"not rewritten"),
                              r"working habits there"),
    "the push-boundary lesson": (r"shipped lesson runs the full suite", (), r"before each push"),
}
#: What a bullet naming `--force` must say beside it: the flag rewrites more than one file, and
#: the two it leaves (US1139 AC5): `sdlc-studio/.version` and an `_index.md` that exists.
FORCE_SAYS = re.compile(r"rewrites the files `init` seeds, (.+?) among them, though it leaves "
                        r"`sdlc-studio/\.version` alone and skips an `_index\.md` that exists")
#: Each pinned figure -> what reads it from the notes, whitespace folded: the first section's,
#: then the changed-behaviour section's.
LEAD_FIGURES = {
    "RPT0027's dollar cost, points and dollars per point":
        r"RPT0027, [^$]*?states \$([\d,.]+) over ([\d,]+) delivered points, \$([\d.]+) a point",
}
CHANGED_FIGURES = {
    "the shipped release_strategy": r"`release_strategy` now ships as `([^`]+)`",
    "the lane budget": r"a budget of (\d+) calls plus (\d+) per point",
    "the resume ceiling": r"context is below (\d+k) tokens",
}
#: Round 1's wording of the three passages its REJECT and BG1190's status refuted.
ROUND1_REFS = (
    "- **`engagement_floor.py check-commit-msg` refuses a `Refs:` line no staged file supports.**\n"
    "  On a subject naming two or more ids, a `Refs:` line naming a unit that owns none of the "
    "staged\n  files is refused.\n  Instead: write `Mentions: <id>` for an id the commit only "
    "mentions, and pass\n  `--write-trailers` in your commit-msg hook to have the trailers written "
    "for you.\n")
ROUND1_AGENTS = ("  Instead: in an existing project, run `init.py run` again to add them; an edited "
                 "definition is\n  left alone unless you pass `--force`, and a harness with no agent "
                 "config falls back to\n  `general-purpose`.\n")
ROUND1_VERIFIER = (
    "- **A verifier that outruns its timeout loses its whole process group.** Its children are\n"
    "  killed with it, and importing `verify_ac` on the main thread installs SIGTERM, SIGINT and\n"
    "  SIGHUP handlers that kill every running verifier's group.\n"
    "  Instead: do not rely on a verifier's background children outliving it.\n")
_FIX: dict[str, Path | str] = {}
#: A `migrate.py` and `init.py` that report what the notes quote but write files of their own,
#: the control `step_problems` must refuse on every step.
_STRAY = """import json, sys
from pathlib import Path
root = Path(sys.argv[sys.argv.index("--root") + 1])
(root / "stray.txt").write_text(" ".join(sys.argv), encoding="utf-8")
if sys.argv[0].endswith("init.py"):
    (root / "sdlc-studio" / ".config.yaml").write_text("release_strategy: trunk\\n", encoding="utf-8")
    sys.exit(0)
if "--apply" in sys.argv:
    (root / "sdlc-studio" / ".version").write_text('skill_version: "6.3.0"\\n', encoding="utf-8")
print(json.dumps({"deterministic": [{"detail": "sdlc-studio/.version stale (skill 6.2.0 -> 6.3.0)"}]}))
"""
#: A child that loads the 6.3.0 Cursor reader with every HTTP open recorded and refused, then
#: reads one base: it prints the reading and whether a request was attempted.
_CURSOR = """import json, sys, urllib.error, urllib.request
calls = []
def _open(self, req, *a, **k):
    calls.append(getattr(req, "full_url", req))
    raise urllib.error.URLError("refused by the test")
urllib.request.OpenerDirector.open = _open
sys.path[:0] = [sys.argv[1]]
from lib import meter_cursor
got = meter_cursor.read(".", {"CURSOR_API_KEY": "k-secret", "SDLC_STUDIO_CURSOR_AGENT_ID": "a1",
                              "SDLC_STUDIO_CURSOR_API": sys.argv[2]})
print(json.dumps({"tokens": got.get("tokens"), "reason": got.get("reason", ""), "calls": len(calls)}))
"""


def entries_63(changelog: str, fragments: Path = FRAGMENTS) -> list[tuple[str, str]]:
    """(section, body) of each 6.3 entry wherever the layout holds it at the time: the
    `## [6.3.0]` section's subsections once the cut has written it, the pending `changelog.d/`
    fragments only before then (a fragment present after the cut belongs to the next release)."""
    cut = re.search(r"^## \[6\.3\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    if cut:
        return [(m.group(1), m.group(2)) for m in
                re.finditer(r"^### (\w+)\n(.*?)(?=^### |\Z)", cut.group(1), re.M | re.S)]
    out = []
    for p in sorted(fragments.glob("*.md")) if fragments.is_dir() else []:
        head, _, body = p.read_text(encoding="utf-8").partition("\n")
        m = re.match(r"<!-- section: (\w+) -->", head)
        out.append((m.group(1) if m else "", body))
    return out


def shipped(rel: str) -> str:
    """`rel` as 6.3.0 ships it: at the v6.3.0 tag once this clone holds it, else in this tree."""
    if _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify",
            "refs/tags/v6.3.0").returncode != 0:
        return (REPO / rel).read_text(encoding="utf-8")
    proc = _run("git", "-C", str(REPO), "show", f"v6.3.0:{rel}")
    if proc.returncode != 0:
        raise AssertionError(f"git show v6.3.0:{rel} failed: {proc.stderr}")
    return proc.stdout


def figure_sources(report: str | None = None) -> dict:
    """Each figure `LEAD_FIGURES` and `CHANGED_FIGURES` read from the notes, label -> its value
    as read now from what decides it at 6.3.0, or None where that source no longer reads: the
    shipped `config-defaults.yaml`, the lane-budget constants in `sprint.py`, the resume ceiling
    in `reference-agent-prompt-template.md`, and RPT0027's Estimates, or `report` in their place."""
    import yaml  # noqa: PLC0415 - config.py, whose defaults this reads, needs it too
    defaults = yaml.safe_load(shipped(f"{SKILL_REL}/templates/config-defaults.yaml")) or {}
    sprint = shipped(f"{SKILL_REL}/scripts/sprint.py")
    template = " ".join(shipped(f"{SKILL_REL}/reference-agent-prompt-template.md").split())
    if report is None:
        found = sorted(REPORTS.glob("RPT0027-*.md"))
        report = found[0].read_text(encoding="utf-8") if found else ""
    row = lambda name, rx: re.search(rf"^\| {name} \| [^|]* \| {rx} \|", report, re.M)  # noqa: E731
    dollars, points, per = (row("Dollar cost", r"\$([\d,.]+)"), row("Points", r"([\d,]+)"),
                            row("Dollars per point", r"\$([\d.]+)"))
    resume = re.search(r"context is below (\d+k) tokens", template)

    def held(*values: object) -> tuple[str, ...] | None:
        return None if any(v is None for v in values) else tuple(_figure(v) for v in values)
    return {
        "the shipped release_strategy": held(defaults.get("release_strategy")),
        "the lane budget": held(_const(sprint, "LANE_CALLS_FIXED"),
                                _const(sprint, "LANE_CALLS_PER_POINT")),
        "the resume ceiling": held(resume.group(1)) if resume else None,
        "RPT0027's dollar cost, points and dollars per point":
            held(dollars.group(1), points.group(1), per.group(1)) if dollars and points and per
            else None,
    }


def figure_problems(text: str) -> list[str]:
    """Every sentence or table row holding a figure names its source."""
    problems = []
    # A code span becomes a word, so a sentence opening with one still starts a new unit.
    for unit in units(re.sub(r"`[^`\n]*`", "Code", _blank(text))):
        if COUNT_LINE.match(unit.strip()):
            continue       # written by `known_issues.py write`; its paragraph names the page
        if re.search(r"\d", RELEASE.sub("", NOT_A_FIGURE.sub("", unit))) and not SOURCE.search(unit):
            problems.append(f"a figure with no source: {unit.strip()[:140]!r}")
    return problems


def lead_problems(text: str, changelog: str, figures: dict | None = None) -> list[str]:
    """AC1: a one-sentence headline naming 6.3.0 as current, a first section holding the four
    themes and nothing else, each naming exactly its units, no unit id outside a theme bullet but
    in the known-issues and sources passages, the CHANGELOG section holding 6.3's entries linked,
    no figure without its source, and each first-section figure equal to its source's value."""
    if figures is None:
        figures = figure_sources()
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.3\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.3.0 the current release: "
                        f"{headline[:120]!r}")
    blank = _blank(text)
    firsts = sections(blank)
    first = firsts[0][1] if firsts else ""
    bullets, paras = _blocks(first)
    problems += [f"the first section holds text outside its theme bullets: "
                 f"{' '.join(p.split())[:80]!r}" for p in paras]
    problems += [f"the first section lists a theme that is not one of the four: "
                 f"{' '.join(b.split())[:80]!r}" for b in bullets
                 if not any(theme in _norm(b) for theme in THEMES)]
    rest = blank
    for theme, want in THEMES.items():
        hits = [b for b in bullets if theme in _norm(b)]
        if not hits:
            problems.append(f"the first section lists no theme {theme!r}")
            continue
        if len(hits) > 1:
            problems.append(f"the first section lists the theme {theme!r} {len(hits)} times")
        rest = rest.replace(hits[0], "", 1)
        named = set(UNIT_ID.findall(hits[0]))
        if not named:
            problems.append(f"the theme {theme!r} names no unit")
            continue
        problems += [f"the theme {theme!r} does not name {u}" for u in sorted(want - named)]
        problems += [f"the theme {theme!r} names {u}, not one of its units"
                     for u in sorted(named - want)]
    for heading, sbody in sections(rest):
        if re.search(r"known issues|sources", heading, re.I):
            continue
        problems += [f"unit id {m} outside a theme, under '{heading}'"
                     for m in UNIT_ID.findall(sbody)]
    labels = changelog_sections(changelog)
    linked = {labels.get(a) for a in re.findall(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)", text)}
    want = "6.3.0" if "6.3.0" in labels.values() else "Unreleased"
    if want not in linked:
        problems.append(f"no link to the CHANGELOG's {want} section")
    return problems + figure_problems(text) + pin_problems(first, LEAD_FIGURES, figures)


def breaking_problems(text: str, entries: list[tuple[str, str]]) -> list[str]:
    """AC2: the notes say no 6.3 fragment is filed under Breaking or Removed exactly when none
    is, claim no breaking change when none is filed, and name BG1213 as the security fix."""
    problems = [] if SECURITY_ROW.search(text) else [
        "the sources do not name BG1213 as the security fix"]
    filed = [s for s, _b in entries if s in ("Breaking", "Removed")]
    said = bool(NO_BREAKING.search(" ".join(_blank(text).split())))
    if filed:
        return problems + ([f"the notes say no fragment is Breaking or Removed, but {len(filed)} "
                            f"are"] if said else [])
    problems += [] if said else ["the notes do not state that no 6.3 fragment is filed under "
                                 "Breaking or Removed"]
    problems += [f"a heading claims a breaking change no fragment records: {h!r}"
                 for h in re.findall(r"^#{1,6} (.*)$", _blank(text), re.M)
                 if re.search(r"(?i)\bbreaking\b|\bremoved\b", h)]
    problems += [f"a sentence claims a breaking change no fragment records: {u[:100]!r}"
                 for u in units(text) if re.search(r"(?i)\bbreaking\b", u)
                 and not NO_BREAKING.search(u)]
    return problems


def changed_problems(text: str, entries: list[tuple[str, str]],
                     figures: dict | None = None) -> list[str]:
    """AC2: each listed change a 6.2 habit meets in exactly one bullet, beside what to do
    instead, no bullet but a listed change, no text but the no-Breaking paragraph outside them,
    and each figure the section states equal to its source's value."""
    body = section(text, r"^Changed defaults and new refusals$")
    if body is None:
        return ["no 'Changed defaults and new refusals' section"]
    if figures is None:
        figures = figure_sources()
    found, paras = _blocks(body)
    bullets = [" ".join(b.split()) for b in found]
    problems = [f"the section holds text outside its change bullets: {' '.join(p.split())[:80]!r}"
                for p in paras if not NO_BREAKING.search(" ".join(p.split()))]
    for b in bullets:
        if "Instead:" not in b:
            problems.append(f"a change named with no replacement: {b[:90]!r}")
        elif len(re.findall(r"\w[\w-]*", b.partition("Instead:")[2])) < 3:
            problems.append(f"a change whose `Instead:` says nothing: {b[:90]!r}")
        if "`--force`" in b and not FORCE_SAYS.search(b):
            problems.append(f"a bullet names `--force` and not what it rewrites and what it "
                            f"leaves: {b[:90]!r}")
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
    return (problems + pin_problems(body, CHANGED_FIGURES, figures)
            + breaking_problems(text, entries))


#: BG1190's Status in the corpus the v6.3.0 tag holds. The notes describe that corpus and stay as
#: shipped; the live corpus has moved on since (BG1190 is Fixed), so it no longer decides.
BG1190_AT_RELEASE = "Open"


def open_problems(text: str, status: str = BG1190_AT_RELEASE) -> list[str]:
    """BG1190's fix landed while its review found a regression, so the bug was Open at the cut:
    the notes say it stays open under Known issues while the corpus they describe does, and list
    it behind no theme."""
    known = " ".join((section(text, r"^Known issues$") or "").split())
    says = re.search(r"BG1190 stays open", known)
    problems = []
    if status == "Open" and not says:
        problems.append("BG1190 is Open and the Known issues section does not say it stays open")
    if status != "Open" and says:
        problems.append(f"the notes say BG1190 stays open, and the corpus records it {status}")
    if status == "Open" and re.search(r"^\| The gates and commit checks[^\n]*\bBG1190\b", text,
                                      re.M):
        problems.append("BG1190 is Open and the Sources table lists it behind a theme")
    return problems


def _steps(text: str) -> list[tuple[str, list[str]]]:
    """(script, arguments) of each `python3 .../scripts/<script>` step in the upgrade section's
    code, in order."""
    old = section(text, r"^Upgrading from 6\.2$") or ""
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    out = []
    for line in (fence.group(1) if fence else "").splitlines():
        argv = shlex.split(line, comments=True)
        if argv[:1] == ["python3"] and argv[1:2] and "/scripts/" in argv[1]:
            out.append((argv[1].rsplit("/", 1)[1], argv[2:]))
    return out


def upgrade_problems(text: str) -> list[str]:
    """AC3: reinstall, `migrate` then `migrate --apply` then `init.py run`, and what each
    reports for a 6.2 project, as the notes say it."""
    old = section(text, r"^Upgrading from 6\.2$")
    if old is None:
        return ["no 'Upgrading from 6.2' section"]
    problems = []
    if not re.search(r"(?i)\breinstall\b", old) or "latest published release" not in old:
        problems.append("the path does not say to reinstall for the latest published release")
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    given = {ln.strip() for ln in shipped("docs/INSTALL.md").splitlines()}
    curls = [ln for ln in (fence.group(1) if fence else "").splitlines() if ln.startswith("curl ")]
    if not curls:
        problems.append("the path gives no reinstall command")
    problems += [f"the reinstall line is not one docs/INSTALL.md gives: {ln[:90]!r}"
                 for ln in curls if ln.strip() not in given]
    steps = _steps(text)
    dry = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" not in a]
    wet = [i for i, (s, a) in enumerate(steps) if s == "migrate.py" and "--apply" in a]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the steps are not `migrate` then `migrate --apply`")
    init = [i for i, (s, a) in enumerate(steps) if s == "init.py" and a[:1] == ["run"]]
    if not (init and wet and wet[0] < init[0]):
        problems.append("the steps do not end with `init.py run` after `migrate --apply`")
    flat = " ".join(old.split())
    para = lambda lead: re.search(rf"\*\*`{lead}`\*\*,? (.*?)(?= \*\*`|$)", flat)  # noqa: E731
    dry_para, apply, again = (m.group(1) if m else "" for m in
                              (para("migrate"), para("migrate --apply"), para("init.py run")))
    if not re.search(r"\bwrites nothing\b", dry_para):
        problems.append("the path does not say the dry run writes nothing")
    if not re.search(r"`sdlc-studio/\.version stale \(skill 6\.2\.0 -> 6\.3\.0\)`", dry_para):
        problems.append("the path does not quote the version stamp the dry run reports")
    if not re.search(r"writes that stamp to `sdlc-studio/\.version` and changes nothing else",
                     apply):
        problems.append("the path does not say `migrate --apply` writes the stamp and nothing else")
    if re.search(r"(?i)\bremoves\b", apply):
        problems.append("the path says `migrate --apply` removes something")
    if not re.search(r"never set it now reads `trunk`", apply):
        problems.append("the path does not say a project that never set release_strategy reads "
                        "`trunk`")
    if not (all(f"`{a}`" in again for a in AGENTS) and "leaves every file you have as it is"
            in again):
        problems.append("the path does not say `init.py run` adds the two agent definitions and "
                        "leaves every file you have as it is")
    return problems


def step_problems(text: str, scripts: Path, project: Path) -> list[str]:
    """AC3: the notes' steps, run in their order on `project` (a 6.2 project), do what the
    notes say: the dry run writes nothing and reports exactly the version stamp the notes quote,
    `--apply` writes `sdlc-studio/.version` alone, stamped 6.3.0, and `init.py run` adds both
    agent definitions and changes no file that was there."""
    problems = []
    flat = " ".join(text.split())
    for script, argv in _steps(text):
        before = _tree(project)
        extra = ("--format", "json") if script == "migrate.py" else ()
        proc = _cli(scripts, project, script, *argv, *extra)
        shown = " ".join([script, *argv])
        if proc.returncode != 0:
            problems.append(f"the step `{shown}` is refused by the shipped CLI "
                            f"(exit {proc.returncode}): {proc.stderr.strip()[:120]}")
            continue
        after = _tree(project)
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if script == "init.py":
            problems += [f"`{shown}` changed {k}, a file that was there" for k in moved
                         if k in before]
            problems += [f"`{shown}` did not add {a}" for a in AGENTS if a not in after]
            continue
        details = [d["detail"] for d in json.loads(proc.stdout)["deterministic"]]
        if "--apply" not in argv:
            if moved:
                problems.append(f"the dry run `{shown}` wrote {moved}")
            problems += [f"the dry run reports {d!r}, which the notes do not quote"
                         for d in details if f"`{d}`" not in flat]
            if not details:
                problems.append("the dry run reports no version stamp for a 6.2 project")
        else:
            if moved != ["sdlc-studio/.version"]:
                problems.append(f"`{shown}` changed {moved}, not `sdlc-studio/.version` alone")
            stamp = (project / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            if 'skill_version: "6.3.0"' not in stamp:
                problems.append(f"`{shown}` did not stamp 6.3.0: {stamp!r}")
    return problems


def setUpModule() -> None:
    """A 6.2 project made by v6.2.0's own `init.py`, and the 6.3.0 skill: the v6.3.0 tag's tree,
    or before the tag this tree with a 6.2.0 version read as 6.3.0, the cut's one change to it.
    A tree that is not a git clone holds neither tag: the checks that run the CLI are skipped
    there, naming why, and the checks of the text still run. A clone lacking the v6.2.0 tag
    fails rather than skips."""
    top = _run("git", "-C", str(REPO), "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO.resolve():
        _FIX["skip"] = ("this tree is not a git clone, so it holds no v6.2.0 tree to make a "
                        "6.2 project from")
        return
    home = Path(tempfile.mkdtemp(prefix="us1136_"))
    _FIX["home"] = home
    skill62 = _extract("v6.2.0", home)
    if skill62 is None:
        raise AssertionError("this clone has no v6.2.0 tag to make a 6.2 project from: fetch tags")
    project = home / "p62"
    project.mkdir()
    proc = _cli(skill62 / "scripts", project, "init.py", "run")
    if proc.returncode != 0:
        raise AssertionError(f"v6.2.0's init.py failed: {proc.stdout}{proc.stderr}")
    skill63 = _extract("v6.3.0", home)
    if skill63 is None:
        skill63 = home / "v6.3.0-pending" / "sdlc-studio"
        shutil.copytree(REPO / SKILL_REL, skill63,
                        ignore=shutil.ignore_patterns("tests", "__pycache__", ".local"))
        md = skill63 / "SKILL.md"
        md.write_text(re.sub(r'(?m)^(  version: )"6\.2\.0"$', r'\1"6.3.0"',
                             md.read_text(encoding="utf-8")), encoding="utf-8")
    _FIX.update(project=project, scripts=skill63 / "scripts", skill62=skill62)


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

    def swap(self, start: str, stop: str, new: str) -> str:
        """The notes with the passage from `start` up to `stop` replaced by `new`."""
        self.assertEqual(1, self.text.count(start), f"anchor not unique: {start[:60]!r}")
        i = self.text.index(start)
        return self.text[:i] + new + self.text[self.text.index(stop, i):]

    def assertFlags(self, problems: list[str], expected: str) -> None:
        self.assertTrue([p for p in problems if expected in p],
                        f"no problem naming {expected!r}: {problems}")

    def needs_cli(self) -> None:
        """Skip the rest of a test where `setUpModule` found no git clone to build from, once a
        second signal agrees: a tree holding `.git` is a clone, and its CLI checks must run."""
        if "skip" in _FIX:
            self.assertFalse((REPO / ".git").exists(), "a git clone skipped the CLI checks")
            self.skipTest(str(_FIX["skip"]))

    def project(self) -> Path:
        """A fresh copy of the 6.2 project."""
        d = Path(tempfile.mkdtemp(prefix="us1136_p_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        shutil.copytree(_FIX["project"], d / "p")
        return d / "p"

    def test_the_notes_lead_with_what_changed_for_you(self) -> None:
        """AC1. MUTANTS: the 6.2.0 notes as they stand (headline '6.2.0 is the current release')
        and with the version changed (no 6.3 theme); a draft composed from the 6.3 fragments,
        whose ids sit outside any theme; a theme with its units cut, one short (US1133 dropped)
        or one over (US1118 added); a fifth theme, as a bullet or a paragraph; a theme listed
        twice; '$118.38' with its RPT0027 source cut, and read as '$181.38'; the notes as they
        stand against an RPT0027 whose points moved; the `#unreleased` link left in place after
        the cut moved 6.3's entries under [6.3.0]."""
        figs = figure_sources()
        self.assertTrue(all(figs.values()), f"premise: every figure's source reads: {figs}")
        lead = lambda text: lead_problems(text, self.changelog, figs)  # noqa: E731
        copied = NOTES_62.read_text(encoding="utf-8")
        self.assertFlags(lead(copied), "the opening")
        self.assertFlags(lead(copied.replace("6.2.0", "6.3.0")), "no theme")
        fragments = "\n".join(body for _section, body in entries_63(self.changelog))
        self.assertTrue(UNIT_ID.search(fragments), "premise: the 6.3 entries name their units")
        composed = self.mutant("\n## Changed defaults", f"\n{fragments}\n\n## Changed defaults")
        self.assertFlags(lead(composed), "outside a theme")
        self.assertFlags(lead(self.mutant(" Delivered by US1126, US1120 and US1132.", "")),
                         "names no unit")
        self.assertFlags(lead(self.mutant("Delivered by US1112, US1113 and US1133.",
                                          "Delivered by US1112 and US1113.")),
                         "does not name US1133")
        self.assertFlags(lead(self.mutant("Delivered by US1126, US1120 and US1132.",
                                          "Delivered by US1126, US1118, US1120 and US1132.")),
                         "names US1118, not one of its units")
        self.assertFlags(lead(self.mutant(
            "RPT0027, the report of the last run before this release, states",
            "The last run before this release states")), "a figure with no source")
        self.assertFlags(lead(self.mutant("states $118.38 over", "states $181.38 over")),
                         "where its source reads")
        fifth = "- **Installs are faster.** Install is quicker.\n"
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"{fifth}\n## Changed defaults")), "not one of the four")
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"\n{fifth[2:]}\n## Changed defaults")),
                         "outside its theme bullets")
        self.assertFlags(lead(self.mutant(
            "\n## Changed defaults",
            "- **The gates and commit checks are faster and truer.**\n\n## Changed defaults")),
            "2 times")
        report = sorted(REPORTS.glob("RPT0027-*.md"))[0].read_text(encoding="utf-8")
        moved = re.sub(r"^(\| Points \| [^|]* \| )(\d+)",
                       lambda m: f"{m.group(1)}{int(m.group(2)) + 1}", report, count=1, flags=re.M)
        self.assertNotEqual(report, moved)
        self.assertFlags(lead_problems(self.text, self.changelog, figure_sources(moved)),
                         "where its source reads")
        self.assertEqual([], lead(self.text))

        before = re.sub(r"#630---\d{4}-\d{2}-\d{2}\)", "#unreleased)", self.text)
        self.assertIn("](../CHANGELOG.md#unreleased)", before)
        cut = "## [Unreleased]\n\n## [6.3.0] - 2026-11-09\n\n## [6.2.0] - 2026-11-02\n"
        precut = "## [Unreleased]\n\n## [6.2.0] - 2026-11-02\n"
        self.assertEqual([], lead_problems(before, precut, figs))
        self.assertFlags(lead_problems(before, cut, figs), "6.3.0 section")
        self.assertEqual([], lead_problems(before.replace("#unreleased)", "#630---2026-11-09)"),
                                           cut, figs))

    def test_every_changed_behaviour_names_what_to_do(self) -> None:
        """AC2. MUTANTS: a section copied from the entries filed under Changed alone, which never
        names the Cursor security fix (filed under Fixed); the release-strategy bullet with its
        'Instead:' cut; the security bullet cut, and its Sources row naming BG1213 cut; an added
        bullet whose 'Instead:' says nothing, one no listed change names, and a change given as
        a paragraph; `trunk` read as `pr-required`, the lane budget's 13 as 31 and the resume
        ceiling's 100k as 200k; a 'Breaking changes' section no fragment records; the
        no-Breaking statement cut, and kept beside a Breaking entry. The release-strategy,
        lane-brief, stale-selector and Cursor-base bullets are then run on the 6.3.0 skill, each
        refusal beside a positive control."""
        entries = entries_63(self.changelog)
        self.assertGreater(len(entries), 1, "premise: the 6.3 entries are read")
        self.assertEqual([], [s for s, _b in entries if s in ("Breaking", "Removed")])
        figs = figure_sources()
        self.assertTrue(all(figs.values()), f"premise: every figure's source reads: {figs}")
        changed = ("## Changed defaults and new refusals\n\n"
                   + "\n".join(b for s, b in entries if s == "Changed") + "\n")
        self.assertFlags(changed_problems(changed, entries, figs),
                         "never names the Cursor base security fix")
        self.assertFlags(changed_problems(self.mutant(
            "\n  Instead: set `release_strategy: pr-required` in `sdlc-studio/.config.yaml` to "
            "keep a branch\n  and a pull request per change.", ""), entries, figs),
            "a change named with no replacement")
        start = self.text.index("- **Security fix:")
        stop = self.text.index("- **The release verify lane runs criteria", start)
        self.assertFlags(changed_problems(self.text[:start] + self.text[stop:], entries, figs),
                         "never names the Cursor base security fix")
        self.assertFlags(changed_problems(self.mutant("| Security fix | BG1213 |\n", ""),
                                          entries, figs), "BG1213")
        tail = "\n## Upgrading from 6.2"
        for bullet, expected in (
                ("- **`foo` now refuses bar.** Instead: .\n", "`Instead:` says nothing"),
                ("- **`foo` now refuses bar.** Instead: pass `--bar` to keep it.\n",
                 "a bullet no listed change names"),
                ("\n`foo` now refuses bar. Instead: pass `--bar` to keep it.\n",
                 "outside its change bullets")):
            with self.subTest(added=bullet):
                self.assertFlags(changed_problems(self.mutant(tail, f"{bullet}{tail}"), entries,
                                                  figs), expected)
        for old, new in (("now ships as `trunk`.", "now ships as `pr-required`."),
                         ("25 calls plus\n  13 per point", "25 calls plus\n  31 per point"),
                         ("below 100k tokens", "below 200k tokens")):
            with self.subTest(figure=new):
                self.assertFlags(changed_problems(self.mutant(old, new), entries, figs),
                                 "where its source reads")
        self.assertFlags(changed_problems(self.mutant(
            tail, "\n## Breaking changes\n\n- **`migrate` is gone.** Instead: reinstall.\n" + tail),
            entries, figs), "a heading claims")
        self.assertFlags(changed_problems(self.mutant(
            "No 6.3 fragment is filed under Breaking or Removed. ", ""), entries, figs),
            "do not state")
        self.assertFlags(changed_problems(self.text, entries + [("Breaking", "- **x.** y\n")],
                                          figs), "but 1 are")
        refs = ("- **A commit-msg hook given", "- **A verifier that outruns")
        self.assertFlags(changed_problems(self.swap(*refs, ROUND1_REFS), entries, figs),
                         "a bullet no listed change names")
        self.assertFlags(changed_problems(self.swap(*refs, ROUND1_REFS), entries, figs),
                         "never names the Refs refusal")
        agents = ("  Instead: in an existing project, run `init.py run`", "- **`gate.py --run-tests`")
        self.assertFlags(changed_problems(self.swap(*agents, ROUND1_AGENTS), entries, figs),
                         "names `--force` and not what it rewrites and what it leaves")
        said = re.search(r"rewrites the files `init`\s+seeds, .+? that exists\.", self.text, re.S)
        self.assertIsNotNone(said, "premise: the bullet says what --force rewrites and leaves")
        round2 = ("rewrites every file `init` writes, `.config.yaml`, `AGENTS.md`, `CLAUDE.md` "
                  "and `decisions.md` among them.")
        self.assertFlags(changed_problems(self.mutant(said.group(0), round2), entries, figs),
                         "names `--force` and not what it rewrites and what it leaves")
        leaves = re.search(r", though it\s+leaves `sdlc-studio/\.version` alone and skips an "
                           r"`_index\.md` that exists", self.text)
        self.assertIsNotNone(leaves, "premise: the bullet names the two files --force leaves")
        self.assertFlags(changed_problems(self.mutant(leaves.group(0), ""), entries, figs),
                         "names `--force` and not what it rewrites and what it leaves")
        self.assertFlags(changed_problems(self.swap(*agents, ROUND1_AGENTS), entries, figs),
                         "the agent definitions is named with no replacement")
        verifier = ("- **A verifier that outruns", "- **A light APPROVE")
        self.assertFlags(changed_problems(self.swap(*verifier, ROUND1_VERIFIER), entries, figs),
                         "does not say 'no longer reaches a running verifier'")
        if _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify",
                "refs/tags/v6.3.0").returncode == 0:   # a copy with no history has no tag to read
            page = next(iter(sorted(BUGS.glob("BG1190-*.md"))))
            found = re.search(r"^> \*\*Status:\*\* (\w+)",
                              shipped(page.relative_to(REPO).as_posix()), re.M)
            self.assertEqual(BG1190_AT_RELEASE, found and found.group(1),
                             "premise: the corpus at the v6.3.0 tag records BG1190 Open")
        unsaid = self.swap("BG1190 stays open:", "**v6.3.0 discloses", "")
        self.assertFlags(open_problems(unsaid, "Open"), "does not say it stays open")
        self.assertFlags(open_problems(self.text, "Fixed"), "the corpus records it Fixed")
        self.assertFlags(open_problems(self.mutant("US1133, BG1160, BG1167, BG1183, BG1187, BG1217 |",
                                                   "US1133, BG1160, BG1167, BG1183, BG1187, BG1190, "
                                                   "BG1217 |"), "Open"), "behind a theme")
        self.assertEqual([], open_problems(self.text))
        self.assertEqual([], changed_problems(self.text, entries, figs))

        self.needs_cli()
        import yaml  # noqa: PLC0415
        scripts = _FIX["scripts"]
        with self.subTest(claim="6.2's shipped default was pr-required"):
            old = yaml.safe_load((_FIX["skill62"] / "templates" / "config-defaults.yaml")
                                 .read_text(encoding="utf-8"))
            self.assertEqual("pr-required", old["release_strategy"])
        root = self.project()
        with self.subTest(claim="a 6.2 project that never set it reads trunk; pr-required keeps"):
            show = lambda: json.loads(_cli(scripts, root, "config.py", "show", "--key",  # noqa: E731
                                           "release_strategy").stdout)
            self.assertEqual(figs["the shipped release_strategy"], (show(),))
            config = root / "sdlc-studio" / ".config.yaml"
            config.write_text(config.read_text(encoding="utf-8") + "\nrelease_strategy: pr-required\n",
                              encoding="utf-8")
            self.assertEqual("pr-required", show())
        with self.subTest(claim="gate.py --run-tests refuses a missing path, exit 2, no test run"):
            (root / "tests").mkdir(exist_ok=True)
            (root / "tests" / "test_ok.py").write_text("def test_ok():\n    assert True\n",
                                                       encoding="utf-8")
            r = _cli(scripts, root, "gate.py", "--run-tests", "tests/test_gone.py")
            self.assertEqual(2, r.returncode, r.stdout + r.stderr)
            self.assertIn("tests/test_gone.py", r.stderr)
            self.assertIn("no test ran", r.stderr)
        with self.subTest(claim="the brief leaves the commit to lane land and states the budget"):
            (root / "sdlc-studio" / "stories" / "US0101-widget.md").write_text(
                "# US0101: widget\n\n> **Status:** Ready\n> **Points:** 3\n> **Epic:** EP0001\n"
                "> **Affects:** tests/test_ok.py\n\n## Acceptance Criteria\n\n- **AC1:** works\n"
                "  - **Verify:** shell true\n", encoding="utf-8")
            r = _cli(scripts, root, "sprint.py", "lane", "brief", "--units", "US0101")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            fixed, per = (int(v) for v in figs["the lane budget"])
            self.assertIn(f"Budget: {fixed + 3 * per} tool calls", r.stdout)
            self.assertIn("sdlc-studio/.local/lane/", r.stdout)
            self.assertIn("sprint lane land", r.stdout)
            self.assertNotIn("git commit", r.stdout)
            self.assertNotIn("critic.py self-check record", r.stdout)
        cursor = lambda base: json.loads(subprocess.run(  # noqa: E731
            [sys.executable, "-I", "-B", "-c", _CURSOR, str(scripts), base], capture_output=True,
            text=True, check=True, timeout=60, cwd=str(root),
            env=gitutil.git_env(PYTHONDONTWRITEBYTECODE="1")).stdout)
        for base in ("http://example.invalid", "http://localhost:9"):
            with self.subTest(claim=f"the Cursor meter refuses {base} before any request"):
                got = cursor(base)
                self.assertEqual((None, 0), (got["tokens"], got["calls"]), got)
                self.assertIn("SDLC_STUDIO_CURSOR_API", got["reason"])
                self.assertNotIn(base.split("//")[1], got["reason"])
        with self.subTest(claim="the control: http on a loopback IP is requested"):
            got = cursor("http://127.0.0.1:9")
            self.assertEqual((None, 1), (got["tokens"], got["calls"]), got)
        gate_md = (scripts.parent / "help" / "gate.md").read_text(encoding="utf-8")
        hook = re.findall(r'engagement_floor\.py" check-commit-msg ((?:--[\w-]+ )*)"\$1"', gate_md)
        self.assertEqual(["--strict "], hook, "the hook help/gate.md gives runs --strict alone")
        self.commit_msg_claims(scripts, hook[0].split())
        self.agent_definition_claims(scripts)

    def commit_msg_claims(self, scripts: Path, flags: list[str]) -> None:
        """The Refs bullet run on a staged fixture where US0101 owns the staged file and US0102
        owns none: the shipped hook's flags pass each message 6.2.0's check passes
        and pass the `Refs:` line no staged file supports, and `--write-trailers` refuses it,
        takes the `Mentions:` line instead, and writes both lines where none were given."""
        root = self.project()
        git = lambda *a: subprocess.run(["git", "-C", str(root), *a], capture_output=True,  # noqa: E731
                                        text=True, check=True, timeout=60, env=gitutil.git_env())
        git("init", "-q")
        (root / "src").mkdir()
        for unit, path in (("US0101", "src/a.py"), ("US0102", "src/b.py")):
            (root / "sdlc-studio" / "stories" / f"{unit}-w.md").write_text(
                f"# {unit}: w\n\n> **Status:** Ready\n> **Affects:** {path}\n", encoding="utf-8")
        (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        git("add", "src/a.py")
        msg = root.parent / "COMMIT_EDITMSG"

        def floor(skill: Path, text: str, *extra: str) -> tuple[int, str]:
            msg.write_text(text, encoding="utf-8")
            r = _cli(skill, root, "engagement_floor.py", "check-commit-msg", *flags, *extra, str(msg))
            return r.returncode, msg.read_text(encoding="utf-8")

        subject = "feat(US0101, US0102): widget\n"
        both = subject + "\nRefs: US0101, US0102\n"
        mention = subject + "\nRefs: US0101\nMentions: US0102\n"
        for text in (subject, both, mention):
            with self.subTest(claim="the shipped hook meets no new refusal", message=text):
                old, new = floor(_FIX["skill62"] / "scripts", text)[0], floor(scripts, text)[0]
                self.assertFalse(new and not old, f"6.2.0 passes it and 6.3.0 exits {new}")
        with self.subTest(claim="the shipped hook passes the unsupported Refs: line"):
            self.assertEqual(0, floor(scripts, both)[0])
            self.assertEqual(1, floor(scripts, subject)[0], "control: the check runs")
        with self.subTest(claim="--write-trailers refuses it under --strict; Mentions passes"):
            self.assertEqual(1, floor(scripts, both, "--write-trailers")[0])
            self.assertEqual(0, floor(scripts, mention, "--write-trailers")[0])
        with self.subTest(claim="left out, the flag writes the trailers"):
            code, written = floor(scripts, subject, "--write-trailers")
            self.assertEqual(0, code, written)
            self.assertIn("Refs: US0101", written)
            self.assertIn("Mentions: US0102", written)

    def agent_definition_claims(self, scripts: Path) -> None:
        """The agent-definitions bullet run on a 6.2 project: `init.py run` leaves an edited
        definition alone; deleting it and running `init.py run` again restores the shipped one
        and changes no other file; `--force` rewrites each file the bullet names."""
        root = self.project()
        self.assertEqual(0, _cli(scripts, root, "init.py", "run").returncode)
        agent = root / AGENTS[0]
        drafted = agent.read_text(encoding="utf-8")
        agent.write_text(drafted + "\nedited\n", encoding="utf-8")
        with self.subTest(claim="an edited definition is left alone"):
            self.assertEqual(0, _cli(scripts, root, "init.py", "run").returncode)
            self.assertEqual(drafted + "\nedited\n", agent.read_text(encoding="utf-8"))
        with self.subTest(claim="delete it and run init.py run again, which changes no other file"):
            agent.unlink()
            before = _tree(root)
            self.assertEqual(0, _cli(scripts, root, "init.py", "run").returncode)
            after = _tree(root)
            self.assertEqual([AGENTS[0]], sorted(k for k in set(before) | set(after)
                                                 if before.get(k) != after.get(k)))
            self.assertEqual(drafted, agent.read_text(encoding="utf-8"))
        flat = " ".join(self.text.split())
        said = FORCE_SAYS.search(flat)
        self.assertIsNotNone(said, "premise: the bullet names what --force rewrites")
        named = re.findall(r"`([^`]+)`", said.group(1))
        self.assertGreater(len(named), 1, "premise: the bullet names what --force rewrites")
        kept = "\n# us1136 kept line\n"
        for name in named:
            hits = [f for f in root.rglob(name) if f.is_file()]
            self.assertEqual(1, len(hits), f"{name}: {hits}")
            hits[0].write_text(hits[0].read_text(encoding="utf-8") + kept, encoding="utf-8")
        self.assertEqual(0, _cli(scripts, root, "init.py", "run", "--force").returncode)
        for name in named:
            with self.subTest(claim=f"--force rewrites {name}"):
                self.assertNotIn(kept, next(root.rglob(name)).read_text(encoding="utf-8"))

    def test_the_62_upgrade_path_is_given(self) -> None:
        """AC3. MUTANTS: notes telling a 6.2 project a reinstall is all it needs (no `migrate`
        lines); the two `migrate` steps in the wrong order; the `init.py run` step cut; a step
        naming a flag the shipped CLI refuses (`--write` for `--apply`); the reinstall URL
        misspelt (`instal.sh`); `--apply` said to remove a config key; the dry run's version
        stamp misquoted; a `migrate.py` and `init.py` that write files of their own. The notes'
        own steps are then run, in their order, on a project v6.2.0's `init.py` made, and the
        upgraded project reads `release_strategy` as `trunk`."""
        old = section(self.text, r"^Upgrading from 6\.2$")
        steps = [ln for ln in old.splitlines() if "/migrate.py" in ln and ln.startswith("python3")]
        self.assertEqual(2, len(steps), steps)
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps) + "\n", "")),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps),
                                                      "\n".join(reversed(steps)))),
                         "`migrate` then `migrate --apply`")
        init = next(ln for ln in old.splitlines() if "/init.py" in ln)
        self.assertFlags(upgrade_problems(self.mutant(init + "\n", "")), "`init.py run`")
        self.assertFlags(upgrade_problems(self.mutant(
            "and changes nothing else:", "and removes `review.policy`:")), "removes something")
        self.assertFlags(upgrade_problems(self.mutant("main/install.sh |", "main/instal.sh |")),
                         "not one docs/INSTALL.md gives")
        self.assertFlags(upgrade_problems(self.mutant("never set it now reads\n`trunk`",
                                                      "never set it keeps its value")),
                         "reads `trunk`")
        self.assertEqual([], upgrade_problems(self.text))

        self.needs_cli()
        scripts = _FIX["scripts"]
        refused = self.mutant('migrate.py" --apply ', 'migrate.py" --write ')
        self.assertFlags(step_problems(refused, scripts, self.project()), "refused by the shipped CLI")
        misquoted = self.mutant("(skill 6.2.0 -> 6.3.0)`", "(skill 6.1.0 -> 6.3.0)`")
        self.assertFlags(step_problems(misquoted, scripts, self.project()), "do not quote")
        with tempfile.TemporaryDirectory() as d:
            for name in ("migrate.py", "init.py"):
                (Path(d) / name).write_text(_STRAY, encoding="utf-8")
            stray = step_problems(self.text, Path(d), self.project())
        self.assertFlags(stray, "the dry run `migrate.py` wrote")
        self.assertFlags(stray, "not `sdlc-studio/.version` alone")
        self.assertFlags(stray, "changed sdlc-studio/.config.yaml, a file that was there")
        self.assertFlags(stray, "did not add .claude/agents/sdlc-builder.md")
        project = self.project()
        self.assertEqual([], step_problems(self.text, scripts, project))
        shown = _cli(scripts, project, "config.py", "show", "--key", "release_strategy")
        self.assertEqual("trunk", json.loads(shown.stdout), shown.stderr)

    def test_a_fragment_written_after_the_cut_leaves_the_63_entries_read(self) -> None:
        """MUTANT: `entries_63` reading any pending fragment in preference to a cut
        `## [6.3.0]` section, so the first fragment of the next release (a Breaking BG9999 here)
        replaced 6.3's entries and AC2 refused the no-Breaking statement. Both the CHANGELOG and
        the fragment are fixtures; the real `changelog.d/` is never written."""
        cut = ("## [Unreleased]\n\n## [6.3.0] - 2026-11-09\n\n### Added\n\n- **New (US1136).**\n\n"
               "### Fixed\n\n- **Mended (BG1213).**\n\n## [6.2.0] - 2026-11-02\n\n### Breaking\n\n"
               "- **Old (US0978).**\n")
        late = "- **A break after the cut (BG9999).** Gone.\n"
        with tempfile.TemporaryDirectory() as d:
            frags = Path(d)
            (frags / "BG9999.md").write_text(f"<!-- section: Breaking -->\n{late}", encoding="utf-8")
            after = entries_63(cut, frags)
            self.assertEqual(["Added", "Fixed"], [s for s, _b in after])
            self.assertEqual(after, entries_63(cut, frags / "absent"))
            self.assertEqual([], breaking_problems(self.text, after))
            precut = "## [Unreleased]\n\n## [6.2.0] - 2026-11-02\n"
            self.assertEqual([("Breaking", late)], entries_63(precut, frags))


if __name__ == "__main__":
    unittest.main()
