"""US1110: the v6.2.0 release notes lead with what changed for the person using it.

The reader is a founder-engineer on 6.1.0 deciding whether to take 6.2. Each check is a function
returning its problems, run on the notes and on a control it must refuse: the 6.1.0 notes with
the version changed, a draft composed from the changelog fragments, a theme with its units cut, a
theme or a change the checks do not list, a figure with its source cut or its value changed. The
figures `figure_sources` pins are read from their sources when the test runs, never typed here.
The self-check, goal-review and summary-refusal bullets are then run through the 6.2.0 skill's
own CLI, and the upgrade path by running the notes' own steps on a project `init.py` created at
v6.1.0.

The 6.2.0 skill is the v6.2.0 tag's tree once the tag exists, and before then this tree with its
version read as 6.2.0, so the checks judge 6.2.0's own CLI before the cut and after it. The
CHANGELOG link is judged against the layout the CHANGELOG has at the time: `[Unreleased]` before
the cut, `[6.2.0]` after it.
"""
# test-census-subject: docs/release-notes-v6.2.0.md
from __future__ import annotations

import hashlib
import json
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
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

NOTES = REPO / "docs" / "release-notes-v6.2.0.md"
NOTES_61 = REPO / "docs" / "release-notes-v6.1.0.md"
CHANGELOG = REPO / "CHANGELOG.md"
FRAGMENTS = REPO / "changelog.d"

#: Each theme of the first section -> the units its bullet names, and no others.
THEMES = {
    "a reviewer judges only work its author has self-checked":
        {"US1087", "US1088", "US1089", "US1094"},
    "one command gives a builder its whole brief": {"US1093"},
    "a run states what it cost, priced, over the main thread and every subagent":
        {"US1091", "US1092", "US1095", "US1097"},
    "the gates cost less": {"BG1065", "BG1109"},
}
#: What a figure's sentence or row may name as its source.
SOURCE = re.compile(r"RPT\d{4}|gate_timing\.py|GATE_BUDGET_MEASURED|cost line|(?i:changelog)|"
                    r"known-issues")
#: The release numbers themselves, and an exit status, are not figures.
RELEASE = re.compile(r"\b6\.[12]\b(?!\.\d)|\b(?:at )?exits? \d\b")
COUNT_LINE = re.compile(r"^\*\*v6\.2\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$")
NO_BREAKING = re.compile(r"No 6\.2 fragment is filed under Breaking or Removed\.")
#: Each change a 6.1 habit meets, label -> (what names its bullet, what the bullet must also
#: say, what its `Instead:` clause must carry).
CHANGES = {
    "review.author_self_check": (r"`review\.author_self_check`",
                                 (r"ships as `report`", r"`block`[^.]*exits 2",
                                  r"`critic\.py self-check record"),
                                 r"record the self-check"),
    "the single goal-review round": (r"--amend-from`", (r"every seat's verdict",),
                                     r"`rereview: yes`"),
    "the cost known issue": (r"`cost\.baseline_per_point`", (r"`retro\.py validate`",),
                             r"`## Cost`"),
    "the light review tier": (r"--tier light`", (r"`review\.brief_diff_lines`",),
                              r"`--tier full`"),
    "the committed lessons log": (r"It lives at `sdlc-studio/retros/LESSONS\.md`",
                                  (r"refuses", r"`retro\.py extract`"), r"commit the moved log"),
    "the summary refusal": (r"`lessons\.py summary`",
                            (r"`LESSONS-SUMMARY\.md` lists a lesson the log lacks",
                             r"exits 1 and writes nothing, where 6\.1 rewrote the digest "
                             r"without it",
                             r"`sprint\.py close` runs it, carries the refusal to the report"),
                            r"commit the log it moves"),
    "revalidate --reason": (r"`lessons\.py revalidate --extend`", (r"refused",), r"`--reason`"),
    "the tracked run record": (r"`sdlc-studio/reports/runs/", (r"`sprint\.py plan --write`",),
                               r"`sprint\.py sign --report"),
    "sign re-deriving the page": (r"`decisions\.py add`", (r"re-closed",),
                                  r"`sprint\.py close` again"),
    "the ruled carried unit": (r"`## Known issues carried`", (), r"`sprint\.py reopen`"),
    "a supplied token total": (r"`sprint\.py lane return --tokens N`", (), r"rely on the meter"),
    "the token basis": (r"each assistant message once", (), r"`Priced/pt`"),
    "the persona mint": (r"no `--persona`", (r"Primar",), r"pass `--persona`"),
    "the doc_freshness census": (r"`doc_freshness\.py --format json`", (), r"each document's entry"),
}
#: Each pinned figure -> what reads it from the notes, whitespace folded: the first section's,
#: then the changed-behaviour section's. `figure_sources` reads the value each must equal from
#: its source at test time.
LEAD_FIGURES = {
    "the self-check key's shipped default": r"`([^`]+)`, the shipped default,",
    "RPT0023's priced cost, points and token sum":
        r"RPT0023, [^.]*?prices it at ([\d,]+) input-equivalent tokens over ([\d,]+) delivered "
        r"points, where its input \+ output \+ cache-write sum is ([\d,]+)\.",
    "BG1109's reads of the decisions log and the ledger":
        r"opened the decisions log ([\d,]+) times and the ledger ([\d,]+) times",
}
CHANGED_FIGURES = {
    "the self-check key's shipped default": r"`review\.author_self_check` key ships as `([^`]+)`",
    "cost.baseline_per_point": r"`cost\.baseline_per_point`, shipped as `([^`]+)`",
    "review.brief_diff_lines": r"`review\.brief_diff_lines` \(`full: ([^`]+)`, `light: ([^`]+)`\)",
    "the cost median's window and floor":
        r"the median of the (\w+) most recent priced runs once (\w+) exist",
    "the cost ratio": r"more than ([a-z ]+?|[\d.]+) times its baseline",
    "the amended goal's word limit": r"an amended goal over (\w+) words",
}
#: A figure the notes spell in words, read as its digits.
WORDS = {"one and a half": "1.5", "three": "3", "five": "5", "twenty": "20"}
REPORTS = REPO / "sdlc-studio" / "reports"
LESSON_LOG = ("# Lessons\n\n## L-0001: keep the gate cheap\n\n- **Lesson:** keep the gate cheap.\n"
              "- **Status:** open\n- **Review-by:** 2027-01-01\n")
_FIX: dict[str, Path | str] = {}
#: A `migrate.py` that reports what the notes quote but writes a file of its own on each run, the
#: control `step_problems` must refuse on both steps.
_STRAY_MIGRATE = """import json, sys
from pathlib import Path
root = Path(sys.argv[sys.argv.index("--root") + 1])
(root / "stray.txt").write_text(" ".join(sys.argv[1:]), encoding="utf-8")
if "--apply" in sys.argv:
    (root / "sdlc-studio" / ".version").write_text('skill_version: "6.2.0"\\n', encoding="utf-8")
print(json.dumps({"deterministic": [{"detail": "sdlc-studio/.version stale (skill 6.1.0 -> 6.2.0)"}]}))
"""


def entries_62(changelog: str, fragments: Path = FRAGMENTS) -> list[tuple[str, str]]:
    """(section, body) of each 6.2 entry wherever the layout holds it at the time: the
    `## [6.2.0]` section's subsections once the cut has written it, the pending `changelog.d/`
    fragments only before then (a fragment present after the cut belongs to the next release)."""
    cut = re.search(r"^## \[6\.2\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    if cut:
        return [(m.group(1), m.group(2)) for m in
                re.finditer(r"^### (\w+)\n(.*?)(?=^### |\Z)", cut.group(1), re.M | re.S)]
    out = []
    for p in sorted(fragments.glob("*.md")) if fragments.is_dir() else []:
        head, _, body = p.read_text(encoding="utf-8").partition("\n")
        m = re.match(r"<!-- section: (\w+) -->", head)
        out.append((m.group(1) if m else "", body))
    return out


def _blocks(body: str) -> tuple[list[str], list[str]]:
    """(bullets, paragraphs) of a section body: a bullet runs to the next bullet or blank line."""
    parts = [p for block in re.split(r"\n[ \t]*\n", body)
             for p in re.split(r"\n(?=- )", block.strip("\n")) if p.strip()]
    return [p for p in parts if p.startswith("- ")], [p for p in parts if not p.startswith("- ")]


def _bullets(body: str) -> list[str]:
    return _blocks(body)[0]


def shipped(rel: str) -> str:
    """`rel` as 6.2.0 ships it: at the v6.2.0 tag once this clone holds it, else in this tree."""
    if _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify",
            "refs/tags/v6.2.0").returncode != 0:
        return (REPO / rel).read_text(encoding="utf-8")
    proc = _run("git", "-C", str(REPO), "show", f"v6.2.0:{rel}")
    if proc.returncode != 0:
        raise AssertionError(f"git show v6.2.0:{rel} failed: {proc.stderr}")
    return proc.stdout


def _figure(value: object) -> str:
    text = " ".join(str(value).lower().replace(",", "").split())
    return WORDS.get(text, text)


def _const(src: str, name: str) -> str | None:
    """What a module-level `NAME = value` line gives, following one alias to another constant."""
    m = re.search(rf"^{name} = (\S+)", src, re.M)
    if m and re.fullmatch(r"[A-Z_]+", m.group(1)):
        m = re.search(rf"^{m.group(1)} = (\S+)", src, re.M)
    return m.group(1) if m else None


def figure_sources(entries: list[tuple[str, str]], report: str | None = None) -> dict:
    """Each figure `LEAD_FIGURES` and `CHANGED_FIGURES` read from the notes, label -> its value
    as read now from what decides it at 6.2.0, or None where that source no longer reads: the
    shipped `config-defaults.yaml`, which `config.py show` reads; the constants in `retro.py` and
    `sprint.py` that decide the cost comparison and the goal limit; RPT0023's Estimates, or
    `report` in their place when given; and the 6.2 entry for BG1109."""
    import yaml  # noqa: PLC0415 - config.py, whose defaults this reads, needs it too
    defaults = yaml.safe_load(shipped(f"{SKILL_REL}/templates/config-defaults.yaml")) or {}
    review, cost = defaults.get("review") or {}, defaults.get("cost") or {}
    lines = review.get("brief_diff_lines") or {}
    retro, sprint = (shipped(f"{SKILL_REL}/scripts/{name}.py") for name in ("retro", "sprint"))
    if report is None:
        found = sorted(REPORTS.glob("RPT0023-*.md"))
        report = found[0].read_text(encoding="utf-8") if found else ""
    points = re.search(r"^\| Points \| [^|]* \| ([\d,]+) \|", report, re.M)
    priced = re.search(r"^\| Priced cost \| [^|]* \| ([\d,]+) \|[^\n]*?input \+ output \+ cache "
                       r"write ([\d,]+)", report, re.M)
    opened = re.search(r"opened the decisions log ([\d,]+) times and the verdict ledger "
                       r"([\d,]+) times", " ".join(" ".join(b.split()) for _s, b in entries))

    def held(*values: object) -> tuple[str, ...] | None:
        return None if any(v is None for v in values) else tuple(_figure(v) for v in values)
    return {
        "the self-check key's shipped default": held(review.get("author_self_check")),
        "cost.baseline_per_point": held(cost.get("baseline_per_point")),
        "review.brief_diff_lines": held(lines.get("full"), lines.get("light")),
        "the cost median's window and floor": held(_const(retro, "COST_WINDOW"),
                                                   _const(retro, "COST_MIN_RUNS")),
        "the cost ratio": held(_const(retro, "COST_REGRESSION_RATIO")),
        "the amended goal's word limit": held(_const(sprint, "GOAL_WORD_LIMIT")),
        "RPT0023's priced cost, points and token sum":
            held(priced.group(1), points.group(1), priced.group(2)) if priced and points else None,
        "BG1109's reads of the decisions log and the ledger": held(*opened.groups()) if opened
        else None,
    }


def pin_problems(text: str, patterns: dict[str, str], figures: dict) -> list[str]:
    """Each figure `patterns` reads from `text`, every time it is stated, equals its source's."""
    flat = " ".join(text.split())
    problems = []
    for label, rx in patterns.items():
        want = figures.get(label)
        if want is None:
            problems.append(f"the source of {label} no longer reads")
            continue
        said = [tuple(_figure(g) for g in ((m,) if isinstance(m, str) else m))
                for m in re.findall(rx, flat)]
        if not said:
            problems.append(f"the notes never state {label}")
        problems += [f"the notes state {label} as {', '.join(s)}, where its source reads "
                     f"{', '.join(want)}" for s in said if s != want]
    return problems


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
    """AC1: a one-sentence headline naming 6.2.0 as current, a first section holding the four
    themes and nothing else, each naming exactly its units, no unit id outside a theme bullet but
    in the known-issues and sources passages, the CHANGELOG section holding 6.2's entries linked,
    no figure without its source, and each first-section figure equal to its source's value
    (`figures`, read by `figure_sources` when not given)."""
    if figures is None:
        figures = figure_sources(entries_62(changelog))
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.2\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.2.0 the current release: "
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
        hit = hits[0]
        rest = rest.replace(hit, "", 1)
        named = set(UNIT_ID.findall(hit))
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
    want = "6.2.0" if "6.2.0" in labels.values() else "Unreleased"
    if want not in linked:
        problems.append(f"no link to the CHANGELOG's {want} section")
    return problems + figure_problems(text) + pin_problems(first, LEAD_FIGURES, figures)


def breaking_problems(text: str, entries: list[tuple[str, str]]) -> list[str]:
    """AC2: the notes say no 6.2 fragment is filed under Breaking or Removed exactly when none
    is, and claim no breaking change when none is filed."""
    filed = [s for s, _b in entries if s in ("Breaking", "Removed")]
    said = bool(NO_BREAKING.search(" ".join(_blank(text).split())))
    if filed:
        return [f"the notes say no fragment is Breaking or Removed, but {len(filed)} are"] if said \
            else []
    problems = [] if said else ["the notes do not state that no 6.2 fragment is filed under "
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
    """AC2: each listed change a 6.1 habit meets in exactly one bullet, beside what to do
    instead, no bullet but a listed change, no text but the no-Breaking paragraph outside them,
    and each figure the section states equal to its source's value (`figures`, read by
    `figure_sources` when not given)."""
    body = section(text, r"^Changed defaults and new refusals$")
    if body is None:
        return ["no 'Changed defaults and new refusals' section"]
    if figures is None:
        figures = figure_sources(entries)
    found, paras = _blocks(body)
    bullets = [" ".join(b.split()) for b in found]
    problems = [f"the section holds text outside its change bullets: {' '.join(p.split())[:80]!r}"
                for p in paras if not NO_BREAKING.search(" ".join(p.split()))]
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
        problems += [f"{label} does not say {rx!r}" for rx in says if not re.search(rx, hit)]
        if not re.search(instead, hit.partition("Instead:")[2]):
            problems.append(f"{label} is named with no replacement beside it")
    return (problems + pin_problems(body, CHANGED_FIGURES, figures)
            + breaking_problems(text, entries))


def _steps(text: str) -> list[list[str]]:
    """The arguments of each `migrate.py` step in the upgrade section's code, in order."""
    old = section(text, r"^Upgrading from 6\.1$") or ""
    fence = re.search(r"^```bash\n(.*?)^```", old, re.M | re.S)
    out = []
    for line in (fence.group(1) if fence else "").splitlines():
        argv = shlex.split(line, comments=True)
        if argv[:1] == ["python3"] and argv[1:2] and argv[1].endswith("/migrate.py"):
            out.append(argv[2:])
    return out


def upgrade_problems(text: str) -> list[str]:
    """AC3: reinstall, `migrate` then `migrate --apply`, and what each reports for a 6.1
    project, as the notes say it."""
    old = section(text, r"^Upgrading from 6\.1$")
    if old is None:
        return ["no 'Upgrading from 6.1' section"]
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
    dry = [i for i, s in enumerate(steps) if "--apply" not in s]
    wet = [i for i, s in enumerate(steps) if "--apply" in s]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the steps are not `migrate` then `migrate --apply`")
    flat = " ".join(old.split())
    dry_para = re.search(r"\*\*`migrate`\*\* (.*?)(?= \*\*`|$)", flat)
    dry_para = dry_para.group(1) if dry_para else ""
    if not re.search(r"\bwrites nothing\b", dry_para):
        problems.append("the path does not say the dry run writes nothing")
    if not re.search(r"`sdlc-studio/\.version stale \(skill 6\.1\.0 -> 6\.2\.0\)`", dry_para):
        problems.append("the path does not quote the version stamp the dry run reports")
    apply = re.search(r"\*\*`migrate --apply`\*\* (.*?)(?= \*\*|$)", flat)
    apply = apply.group(1) if apply else ""
    if not re.search(r"writes that stamp to `sdlc-studio/\.version` and changes nothing else",
                     apply):
        problems.append("the path does not say `migrate --apply` writes the stamp and nothing else")
    if re.search(r"(?i)\bremoves\b", apply):
        problems.append("the path says `migrate --apply` removes something")
    if not re.search(r"`sdlc-studio/\.local/lessons\.md`[^.]*`lessons` command[^.,]*, or "
                     r"`retro\.py extract`, moves it to `sdlc-studio/retros/LESSONS\.md`"
                     r"[^.]*commit", flat):
        problems.append("the path does not say the first `lessons` command or `retro.py extract` "
                        "moves the legacy log and says to commit it")
    return problems


def _tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def _cli(scripts: Path, root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(scripts / script), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=600, cwd=str(root),
                          env=gitutil.git_env(PYTHONDONTWRITEBYTECODE="1"))


def step_problems(text: str, scripts: Path, project: Path) -> list[str]:
    """AC3: the notes' `migrate.py` steps, run in their order on `project` (a 6.1 project),
    report what the notes say: the dry run writes nothing and reports exactly the version stamp
    the notes quote, and `--apply` writes `sdlc-studio/.version` alone, stamped 6.2.0."""
    problems = []
    flat = " ".join(text.split())
    for argv in _steps(text):
        before = _tree(project)
        proc = _cli(scripts, project, "migrate.py", *argv, "--format", "json")
        shown = " ".join(["migrate.py", *argv])
        if proc.returncode != 0:
            problems.append(f"the step `{shown}` is refused by the shipped CLI "
                            f"(exit {proc.returncode}): {proc.stderr.strip()[:120]}")
            continue
        after = _tree(project)
        moved = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        details = [d["detail"] for d in json.loads(proc.stdout)["deterministic"]]
        if "--apply" not in argv:
            if moved:
                problems.append(f"the dry run `{shown}` wrote {moved}")
            problems += [f"the dry run reports {d!r}, which the notes do not quote"
                         for d in details if f"`{d}`" not in flat]
            if not details:
                problems.append("the dry run reports no version stamp for a 6.1 project")
        else:
            if moved != ["sdlc-studio/.version"]:
                problems.append(f"`{shown}` changed {moved}, not `sdlc-studio/.version` alone")
            stamp = (project / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            if 'skill_version: "6.2.0"' not in stamp:
                problems.append(f"`{shown}` did not stamp 6.2.0: {stamp!r}")
    return problems


def _extract(tag: str, dest: Path) -> Path | None:
    """The skill tree at `tag`, without its tests, extracted under `dest`; None when this clone
    has no such tag."""
    if _run("git", "-C", str(REPO), "rev-parse", "-q", "--verify",
            f"refs/tags/{tag}").returncode != 0:
        return None
    archive = dest / f"{tag}.tar"
    proc = _run("git", "-C", str(REPO), "archive", "-o", str(archive), tag, "--", SKILL_REL,
                f":(exclude){SKILL_REL}/scripts/tests")
    if proc.returncode != 0:
        raise AssertionError(f"git archive {tag} failed: {proc.stderr}")
    with tarfile.open(archive) as tar:
        tar.extractall(dest / tag, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    return dest / tag / SKILL_REL


def setUpModule() -> None:
    """A 6.1 project made by v6.1.0's own `init.py`, and the 6.2.0 skill: the v6.2.0 tag's tree,
    or before the tag this tree with a 6.1.0 version read as 6.2.0, the cut's one change to it.
    A tree that is not a git clone, such as a copy of the tracked files, holds neither tag: the
    checks that run the CLI are skipped there, naming why, and the checks of the text still run.
    A clone lacking the v6.1.0 tag fails rather than skips."""
    top = _run("git", "-C", str(REPO), "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != REPO.resolve():
        _FIX["skip"] = ("this tree is not a git clone, so it holds no v6.1.0 tree to make a "
                       "6.1 project from")
        return
    home = Path(tempfile.mkdtemp(prefix="us1110_"))
    _FIX["home"] = home
    skill61 = _extract("v6.1.0", home)
    if skill61 is None:
        raise AssertionError("this clone has no v6.1.0 tag to make a 6.1 project from: fetch tags")
    project = home / "p61"
    project.mkdir()
    proc = _cli(skill61 / "scripts", project, "init.py", "run")
    if proc.returncode != 0:
        raise AssertionError(f"v6.1.0's init.py failed: {proc.stdout}{proc.stderr}")
    skill62 = _extract("v6.2.0", home)
    if skill62 is None:
        skill62 = home / "v6.2.0-pending" / "sdlc-studio"
        shutil.copytree(REPO / SKILL_REL, skill62,
                        ignore=shutil.ignore_patterns("tests", "__pycache__", ".local"))
        md = skill62 / "SKILL.md"
        md.write_text(re.sub(r'(?m)^(  version: )"6\.1\.0"$', r'\1"6.2.0"',
                             md.read_text(encoding="utf-8")), encoding="utf-8")
    _FIX.update(project=project, scripts=skill62 / "scripts", scripts61=skill61 / "scripts")


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

    def project(self) -> Path:
        """A fresh copy of the 6.1 project."""
        d = Path(tempfile.mkdtemp(prefix="us1110_p_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        shutil.copytree(_FIX["project"], d / "p")
        return d / "p"

    def test_the_notes_lead_with_what_changed_for_you(self) -> None:
        """AC1. MUTANTS: the 6.1.0 notes as they stand (headline '6.1.0 is the current release')
        and with the version changed (no 6.2 theme); a draft composed from the 6.2 fragments,
        whose ids sit outside any theme; a theme with its units cut ('Delivered by US1093.'
        gone) or one short (BG1065 dropped); a fifth theme naming no unit, as a bullet or a
        paragraph; a theme listed twice; '111,425,278' with its RPT0023 source cut; RPT0023's 69
        points read as 96, BG1109's 2,256 as 2,265, and the self-check key's shipped `report` as
        `block`; the notes as they stand against an RPT0023 whose points moved; the
        `#unreleased` link left in place after the cut moved 6.2's entries under [6.2.0]."""
        figs = figure_sources(entries_62(self.changelog))
        self.assertTrue(all(figs.values()), f"premise: every figure's source reads: {figs}")
        lead = lambda text: lead_problems(text, self.changelog, figs)  # noqa: E731
        copied = NOTES_61.read_text(encoding="utf-8")
        self.assertFlags(lead(copied), "the opening")
        self.assertFlags(lead(copied.replace("6.1.0", "6.2.0")), "no theme")
        fragments = "\n".join(body for _section, body in entries_62(self.changelog))
        self.assertTrue(UNIT_ID.search(fragments), "premise: the 6.2 entries name their units")
        composed = self.mutant("\n## Changed defaults", f"\n{fragments}\n\n## Changed defaults")
        self.assertFlags(lead(composed), "outside a theme")
        self.assertFlags(lead(self.mutant(" Delivered by US1093.", "")), "names no unit")
        self.assertFlags(lead(self.mutant("Delivered by US1093.", "Delivered by US1093 and BG1111.")),
                         "names BG1111, not one of its units")
        self.assertFlags(lead(self.mutant("Delivered by BG1065 and BG1109.", "Delivered by BG1109.")),
                         "does not name BG1065")
        self.assertFlags(lead(self.mutant("RPT0023, the report of the last run before this release,",
                                          "the last run before this release")),
                         "a figure with no source")
        fifth = "- **Installs are faster.** Install is quicker.\n"
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"{fifth}\n## Changed defaults")), "not one of the four")
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          f"\n{fifth[2:]}\n## Changed defaults")),
                         "outside its theme bullets")
        self.assertFlags(lead(self.mutant("\n## Changed defaults",
                                          "- **The gates cost less.**\n\n## Changed defaults")),
                         "2 times")
        for old, new in (("over 69\n", "over 96\n"), ("log 2,256 times", "log 2,265 times"),
                         ("`report`, the shipped default,", "`block`, the shipped default,")):
            with self.subTest(figure=new):
                self.assertFlags(lead(self.mutant(old, new)), "where its source reads")
        report = sorted(REPORTS.glob("RPT0023-*.md"))[0].read_text(encoding="utf-8")
        moved = re.sub(r"^(\| Points \| [^|]* \| )(\d+)",
                       lambda m: f"{m.group(1)}{int(m.group(2)) + 1}", report, count=1, flags=re.M)
        self.assertNotEqual(report, moved)
        self.assertFlags(lead_problems(self.text, self.changelog,
                                       figure_sources(entries_62(self.changelog), moved)),
                         "where its source reads")
        self.assertEqual([], lead(self.text))

        before = re.sub(r"#620---\d{4}-\d{2}-\d{2}\)", "#unreleased)", self.text)
        self.assertIn("](../CHANGELOG.md#unreleased)", before)
        cut = "## [Unreleased]\n\n## [6.2.0] - 2026-11-02\n\n## [6.1.0] - 2026-10-03\n"
        precut = "## [Unreleased]\n\n## [6.1.0] - 2026-10-03\n"
        self.assertEqual([], lead_problems(before, precut, figs))
        self.assertFlags(lead_problems(before, cut, figs), "6.2.0 section")
        self.assertEqual([], lead_problems(before.replace("#unreleased)", "#620---2026-11-02)"),
                                           cut, figs))

    def test_every_changed_behaviour_names_what_to_do(self) -> None:
        """AC2. MUTANTS: a section copied from the entries filed under Changed alone, which never
        names `review.author_self_check` (filed under Added); the self-check bullet with its
        'Instead:' sentence cut; the summary refusal's bullet cut, as round 1 shipped the notes;
        an added bullet whose 'Instead:' says nothing, one with a whole 'Instead:' that
        no listed change names, and a change given as a paragraph; `2500000` read as `250000`,
        `full: 400` as `full: 40`, and 'twenty words' as 'thirty'; a 'Breaking changes' section
        no fragment records; the no-Breaking statement cut, and kept beside a Breaking entry. The
        self-check, goal-review and summary bullets are then run on the 6.2.0 skill, the
        summary's beside v6.1.0's own, and `config.py show` is held to the defaults the figures
        were read from."""
        entries = entries_62(self.changelog)
        self.assertGreater(len(entries), 1, "premise: the 6.2 entries are read")
        self.assertEqual([], [s for s, _b in entries if s in ("Breaking", "Removed")])
        figs = figure_sources(entries)
        self.assertTrue(all(figs.values()), f"premise: every figure's source reads: {figs}")
        changed = ("## Changed defaults and new refusals\n\n"
                   + "\n".join(b for s, b in entries if s == "Changed") + "\n")
        self.assertFlags(changed_problems(changed, entries, figs),
                         "never names review.author_self_check")
        start = self.text.index("- **`lessons.py summary` refuses")
        stop = self.text.index("- **`lessons.py revalidate", start)
        round1 = self.text[:start] + self.text[stop:]
        self.assertFlags(changed_problems(round1, entries, figs), "never names the summary refusal")
        tail = "\n## Upgrading from 6.1"
        for bullet, expected in (
                ("- **`foo` now refuses bar.** Instead: .\n", "`Instead:` says nothing"),
                ("- **`foo` now refuses bar.** Instead: pass `--bar` to keep it.\n",
                 "a bullet no listed change names"),
                ("\n`foo` now refuses bar. Instead: pass `--bar` to keep it.\n",
                 "outside its change bullets")):
            with self.subTest(added=bullet):
                self.assertFlags(changed_problems(self.mutant(tail, f"{bullet}{tail}"), entries,
                                                  figs), expected)
        for old, new in (("shipped as `2500000`", "shipped as `250000`"),
                         ("(`full: 400`", "(`full: 40`"),
                         ("over twenty words", "over thirty words")):
            with self.subTest(figure=new):
                self.assertFlags(changed_problems(self.mutant(old, new), entries, figs),
                                 "where its source reads")
        self.assertFlags(changed_problems(self.mutant(
            "\n  Instead: record the self-check before you brief, or keep `report` until your "
            "builders do.", ""), entries), "a change named with no replacement")
        self.assertFlags(changed_problems(self.mutant(
            "  ships as `report`, which", "  ships as `off`, which"), entries),
            "review.author_self_check does not say")
        self.assertFlags(changed_problems(self.mutant(
            "  Instead: record the self-check before you brief,",
            "  You may record the self-check before you brief. Instead: carry on,"), entries),
            "review.author_self_check is named with no replacement")
        self.assertFlags(changed_problems(self.mutant(
            "\n## Upgrading from 6.1", "\n## Breaking changes\n\n- **`migrate` is gone.** "
            "Instead: reinstall.\n\n## Upgrading from 6.1"), entries), "a heading claims")
        self.assertFlags(changed_problems(self.mutant(
            "No 6.2 fragment is filed under Breaking or Removed. ", ""), entries), "do not state")
        self.assertFlags(changed_problems(self.text, entries + [("Breaking", "- **x.** y\n")]),
                         "but 1 are")
        self.assertEqual([], changed_problems(self.text, entries, figs))

        self.needs_cli()
        scripts = _FIX["scripts"]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for key, label in (("review.author_self_check", "the self-check key's shipped default"),
                               ("cost.baseline_per_point", "cost.baseline_per_point"),
                               ("review.brief_diff_lines", "review.brief_diff_lines")):
                with self.subTest(claim=f"config.py show gives {key} as the figures read it"):
                    shown = _cli(scripts, root, "config.py", "show", "--key", key)
                    value = json.loads(shown.stdout)
                    value = (value["full"], value["light"]) if isinstance(value, dict) else (value,)
                    self.assertEqual(figs[label], tuple(_figure(v) for v in value), shown.stderr)
            for rel, body in (
                    ("src/widget.py", "def w():\n    return 1\n"),
                    ("tests/test_widget.py", "def test_w():\n    assert True\n"),
                    ("changelog.d/US0101.md", "<!-- section: Added -->\n\n- w (US0101).\n"),
                    ("sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam\n\ncharter\n"),
                    ("sdlc-studio/stories/US0101-widget.md",
                     "# US0101: widget\n\n> **Status:** Review\n> **Points:** 2\n"
                     "> **Epic:** EP0001\n> **Affects:** src/widget.py, tests/test_widget.py, "
                     "changelog.d/US0101.md\n\n## Acceptance Criteria\n\n### AC1: works\n"
                     "- **Verify:** shell true\n")):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(body, encoding="utf-8")
            config = root / "sdlc-studio" / ".config.yaml"
            brief = lambda: _cli(scripts, root, "critic.py", "brief", "--unit", "US0101",  # noqa: E731
                                 "--seat", "qa")
            with self.subTest(claim="report briefs and names the missing record"):
                r = brief()
                self.assertEqual(0, r.returncode, r.stderr)
                self.assertTrue(r.stdout.strip())
                self.assertIn("no author self-check recorded", r.stderr)
            with self.subTest(claim="block exits 2 and prints nothing until the record"):
                config.write_text("review:\n  author_self_check: block\n", encoding="utf-8")
                r = brief()
                self.assertEqual((2, ""), (r.returncode, r.stdout), r.stderr)
                self.assertIn("critic.py self-check record", r.stderr)
            with self.subTest(claim="another value refuses the brief, naming it"):
                config.write_text("review:\n  author_self_check: blocking\n", encoding="utf-8")
                r = brief()
                self.assertEqual(2, r.returncode)
                self.assertIn("`blocking`", r.stderr)
            with self.subTest(claim="the recorded self-check admits the brief under block"):
                config.write_text("review:\n  author_self_check: block\n", encoding="utf-8")
                (root / "c.json").write_text(json.dumps([
                    {"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE"},
                    {"surface": "changelog.d/US0101.md", "claim": "w is new", "ruling": "TRUE"}]),
                    encoding="utf-8")
                (root / "m.json").write_text(json.dumps([
                    {"mutant": "w returns 2", "test": "tests/test_widget.py::test_w",
                     "result": "killed"}]), encoding="utf-8")
                rec = _cli(scripts, root, "critic.py", "self-check", "record", "--unit", "US0101",
                           "--claims", str(root / "c.json"), "--mutants", str(root / "m.json"),
                           "--author", "builder")
                self.assertEqual(0, rec.returncode, rec.stderr)
                self.assertEqual(0, brief().returncode)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            gitutil.git(["init", "-q"], cwd=root)
            self.assertEqual(0, _cli(scripts, root, "init.py", "run").returncode)
            (root / "sdlc-studio" / "stories" / "US0001-s.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Points:** 2\n"
                "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: works\n\n"
                "- **Verify:** shell true\n", encoding="utf-8")
            goal, amended = "ship the parser to users", "ship the renderer to users"
            record = lambda *a: _cli(scripts, root, "sprint.py", "goal-review", "record", *a)  # noqa: E731
            with self.subTest(claim="a seat answering rereview: yes owes a verdict, the rest carry"):
                self.assertEqual(0, record("--goal", goal, "--seat", "engineering|yes|done|yes",
                                           "--seat", "product|yes|done|yes",
                                           "--seat", "qa|yes|done|yes|show me|yes").returncode)
                amend = record("--goal", amended, "--amend-from", goal, "--requesting-seat",
                               "engineering")
                self.assertEqual(0, amend.returncode, amend.stderr)
                self.assertIn("carried engineering, product forward", amend.stdout)
                plan = _cli(scripts, root, "sprint.py", "plan", "--stories", "Ready", "--no-fetch",
                            "--sprint-goal", amended)
                owing = [ln for ln in (plan.stdout + plan.stderr).splitlines()
                         if "owing a verdict" in ln]
                self.assertEqual(1, len(owing), plan.stdout + plan.stderr)
                self.assertIn("qa", owing[0])
            with self.subTest(claim="a --fields-file rereview other than yes or no is refused"):
                fields = root / "f.json"
                fields.write_text(json.dumps({"goal": goal, "seats": [
                    {"seat": "qa", "achievable": "yes", "done_means": "done",
                     "one_increment": "yes", "rereview": "maybe"}]}), encoding="utf-8")
                r = record("--fields-file", str(fields))
                self.assertEqual(2, r.returncode)
                self.assertIn("rereview", r.stderr)
            with self.subTest(claim="an amended goal over the limit the notes state is refused"):
                limit = int(figs["the amended goal's word limit"][0])
                r = record("--goal", " ".join(["word"] * (limit + 1)), "--amend-from", amended,
                           "--requesting-seat", "qa")
                self.assertEqual(2, r.returncode)
                self.assertIn(f"the limit is {limit}", r.stderr)

        with tempfile.TemporaryDirectory() as d:
            # Machine A holds 6.1's gitignored log and the digest v6.1.0 built from it; machine B,
            # a second clone, holds the committed digest and not the log.
            a, b, b61 = Path(d) / "a", Path(d) / "b", Path(d) / "b61"
            shutil.copytree(_FIX["project"], a)
            legacy = a / "sdlc-studio" / ".local" / "lessons.md"
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_text(LESSON_LOG, encoding="utf-8")
            built = _cli(_FIX["scripts61"], a, "lessons.py", "summary")
            self.assertEqual(0, built.returncode, built.stderr)
            for clone in (b, b61):
                shutil.copytree(a, clone, ignore=shutil.ignore_patterns(".local"))
            digest = Path("sdlc-studio") / "retros" / "LESSONS-SUMMARY.md"
            self.assertIn("L-0001", (b / digest).read_text(encoding="utf-8"), "premise")
            with self.subTest(claim="summary exits 1 and writes nothing where the log lacks one"):
                before = _tree(b)
                r = _cli(scripts, b, "lessons.py", "summary")
                self.assertEqual(1, r.returncode, r.stdout + r.stderr)
                self.assertIn("L-0001", r.stderr)
                self.assertEqual(before, _tree(b))
            with self.subTest(claim="where 6.1 rewrote the digest without it"):
                rewrote = _cli(_FIX["scripts61"], b61, "lessons.py", "summary")
                self.assertEqual(0, rewrote.returncode, rewrote.stderr)
                self.assertNotIn("L-0001", (b61 / digest).read_text(encoding="utf-8"))
            with self.subTest(claim="the log a lessons command moves, committed, lets it run"):
                moved = _cli(scripts, a, "lessons.py", "list")
                self.assertEqual(0, moved.returncode, moved.stderr)
                self.assertIn("commit it", moved.stderr)
                log = Path("sdlc-studio") / "retros" / "LESSONS.md"
                shutil.copy2(a / log, b / log)
                r = _cli(scripts, b, "lessons.py", "summary")
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                self.assertIn("L-0001", (b / digest).read_text(encoding="utf-8"))

    def test_the_61_upgrade_path_is_given(self) -> None:
        """AC3. MUTANTS: notes telling a 6.1 project a reinstall is all it needs (no `migrate`
        lines); the two steps in the wrong order; a step naming a flag the shipped CLI refuses
        (`--write` for `--apply`); the reinstall URL misspelt (`instal.sh`), against the line
        6.2.0's docs/INSTALL.md gives; `--apply` said to remove a config key; the dry run's version
        stamp misquoted; a `migrate.py` that writes a file of its own on each step. The notes'
        own steps are then run, in their order, on a project v6.1.0's `init.py` made, and the
        legacy lessons log is moved as the notes say."""
        old = section(self.text, r"^Upgrading from 6\.1$")
        steps = [ln for ln in old.splitlines() if ln.startswith("python3")]
        self.assertEqual(2, len(steps), steps)
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps) + "\n", "")),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps),
                                                      "\n".join(reversed(steps)))),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant(
            "and changes nothing else:", "and removes `review.policy`:")), "removes something")
        self.assertFlags(upgrade_problems(self.mutant("main/install.sh |", "main/instal.sh |")),
                         "not one docs/INSTALL.md gives")
        self.assertFlags(upgrade_problems(self.mutant(" and says to commit it. Commit",
                                                      " it. Commit")),
                         "says to commit it")
        self.assertEqual([], upgrade_problems(self.text))

        self.needs_cli()
        scripts = _FIX["scripts"]
        refused = self.mutant('migrate.py" --apply ', 'migrate.py" --write ')
        self.assertFlags(step_problems(refused, scripts, self.project()), "refused by the shipped CLI")
        misquoted = self.mutant("(skill 6.1.0 -> 6.2.0)`", "(skill 6.0.0 -> 6.2.0)`")
        self.assertFlags(step_problems(misquoted, scripts, self.project()), "do not quote")
        self.assertEqual([], step_problems(self.text, scripts, self.project()))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "migrate.py").write_text(_STRAY_MIGRATE, encoding="utf-8")
            stray = step_problems(self.text, Path(d), self.project())
        self.assertFlags(stray, "the dry run `migrate.py` wrote")
        self.assertFlags(stray, "not `sdlc-studio/.version` alone")

        project = self.project()
        legacy = project / "sdlc-studio" / ".local" / "lessons.md"
        legacy.parent.mkdir(parents=True, exist_ok=True)
        legacy.write_text(LESSON_LOG, encoding="utf-8")
        with self.subTest(claim="migrate leaves the legacy lessons log where it is"):
            proc = _cli(scripts, project, "migrate.py", "--format", "json")
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertNotIn("lessons", proc.stdout)
            self.assertTrue(legacy.is_file())
        with self.subTest(claim="the first lessons command moves it and says to commit it"):
            proc = _cli(scripts, project, "lessons.py", "list")
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertFalse(legacy.exists())
            self.assertTrue((project / "sdlc-studio" / "retros" / "LESSONS.md").is_file())
            self.assertIn("commit it", proc.stderr)

    def test_a_fragment_written_after_the_cut_leaves_the_62_entries_read(self) -> None:
        """MUTANT: `entries_62` reading any pending fragment in preference to a cut
        `## [6.2.0]` section, so the first fragment of the next release (a Breaking BG9999 here)
        replaced 6.2's entries and AC2 refused the no-Breaking statement. Both the CHANGELOG and
        the fragment are fixtures; the real `changelog.d/` is never written."""
        cut = ("## [Unreleased]\n\n## [6.2.0] - 2026-11-02\n\n### Added\n\n- **New (US1110).**\n\n"
               "### Fixed\n\n- **Mended (BG1166).**\n\n## [6.1.0] - 2026-10-03\n\n### Breaking\n\n"
               "- **Old (US0978).**\n")
        late = "- **A break after the cut (BG9999).** Gone.\n"
        with tempfile.TemporaryDirectory() as d:
            frags = Path(d)
            (frags / "BG9999.md").write_text(f"<!-- section: Breaking -->\n{late}", encoding="utf-8")
            after = entries_62(cut, frags)
            self.assertEqual(["Added", "Fixed"], [s for s, _b in after])
            self.assertEqual(after, entries_62(cut, frags / "absent"))
            self.assertEqual([], breaking_problems(self.text, after))
            # The control: before the cut there is no section, and the fragments are the entries.
            precut = "## [Unreleased]\n\n## [6.1.0] - 2026-10-03\n"
            self.assertEqual([("Breaking", late)], entries_62(precut, frags))


if __name__ == "__main__":
    unittest.main()
