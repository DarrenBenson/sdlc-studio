"""US0953: the v6.0.0 release notes lead with what changed for the person using it.

The reader is a founder-engineer deciding whether to upgrade. The notes lead with a headline
and themes, give an upgrade path from the candidate as well as from v5.1, name a source for
every figure, and report the soak the candidate's notes promised in public. Each check is a
function returning its problems, run on the notes and on a control it must refuse: the
candidate's own notes, which are the plausible wrong answer (copied with the version changed).

The notes are written before the release cut renames the CHANGELOG's `[6.0.0]` heading to
`[6.0.0-rc.1]`, so the section links are judged against the layout the CHANGELOG has now: before
the rename the candidate's entries sit under `[6.0.0]` and this release's under `[Unreleased]`.
"""
# test-census-subject: docs/release-notes-v6.0.0.md
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import check_links  # noqa: E402

NOTES = REPO / "docs" / "release-notes-v6.0.0.md"
CANDIDATE = REPO / "docs" / "release-notes-v6.0.0-rc.1.md"
CHANGELOG = REPO / "CHANGELOG.md"
SCENARIOS = REPO / "evals" / "scenarios"
REHEARSAL_NAME = "upgrade-rehearsal-v6.md"

THEMES = ("one plan, one review, one signature", "one-page report",
          "ceremony that caught nothing is gone", "faster feedback", "learns from its own runs")
#: A unit id (sequential or ULID). Report (RPT) and decision (D) ids are not units.
UNIT_ID = re.compile(r"\b(?:US|BG|CR|EP|RFC)\d{4}\b|\b(?:US|BG|CR|EP)-[0-9A-Z]{8}\b")
#: What a figure's sentence or row may name as its source.
SOURCE = re.compile(r"RPT\d{4}|gate_timing\.py|back-to-basics|rehearsal record|"
                    r"upgrade-rehearsal-v6\.md|eval run|v6-rc1|v6-main|CHANGELOG|known-issues|"
                    r"run record|verdict ledger")
#: Digits that are not a figure: versions, dates, ids and eval scenario names.
NOT_A_FIGURE = re.compile(r"v?\d+\.\d+\.\d+(?:-rc\.\d+)?|\bv\d+(?:\.\d+)?|(?<=\bfrom )\d+\.\d+|"
                          r"\b\d{4}-\d{2}-\d{2}\b|\b[A-Z]{1,4}-?\d{3,4}\b|"
                          r"\b[A-Z]{2,4}-[0-9A-Z]{8}\b|\b\d{2}-[a-z][a-z0-9-]*")
SMALLER = re.compile(r"(?i)\bsmaller\b|two-thirds|\bshr[au]nk\b|fewer lines|less code|"
                     r"lines of (?:production )?code (?:were |was )?(?:removed|deleted|cut)")
COUNT_LINE = re.compile(r"^\*\*v6\.0\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$",
                        re.M)
SLOT = re.compile(r"<!--\s*(?:TO FILL|06 re-run result)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _blank(text: str) -> str:
    """`text` without HTML comments and fenced blocks, line count kept."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"^```.*?^```", lambda m: "\n" * m.group(0).count("\n"), text,
                  flags=re.S | re.M)


def sections(text: str, level: int = 2) -> list[tuple[str, str]]:
    """(heading, body) for each heading at `level`, the body running to the next heading at
    that level or higher."""
    out: list[tuple[str, str]] = []
    marks = list(re.finditer(rf"^(#{{1,{level}}}) (.*)$", text, re.M))
    for i, m in enumerate(marks):
        if len(m.group(1)) != level:
            continue
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(2).strip(), text[m.end():end]))
    return out


def section(text: str, heading_rx: str, level: int = 2) -> str | None:
    for heading, body in sections(text, level):
        if re.search(heading_rx, heading, re.I):
            return body
    return None


def changelog_sections(changelog: str) -> dict[str, str]:
    """anchor -> version label for each `## [label]` heading of the CHANGELOG."""
    out = {}
    for line in changelog.splitlines():
        m = re.match(r"^## \[([^\]]+)\]", line)
        if m:
            out[check_links.slug(line[3:])] = m.group(1)
    return out


def lead_problems(text: str, changelog: str) -> list[str]:
    """AC1: a one-sentence headline naming 6.0.0 as current, the themes, the section links, no
    candidate framing, and no unit id outside the known-issues and sources passages."""
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.0\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.0.0 the current release: "
                        f"{headline[:120]!r}")
    firsts = sections(text)
    first = firsts[0][1].lower() if firsts else ""
    problems += [f"the first section lists no theme {t!r}" for t in THEMES if t not in first]
    labels = changelog_sections(changelog)
    linked = {labels.get(a) for a in re.findall(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)", text)}
    # After the cut's rename the candidate has its own heading; before it, 6.0.0's entries sit
    # under [Unreleased] and the candidate's under [6.0.0].
    want = ({"6.0.0", "6.0.0-rc.1"} if "6.0.0-rc.1" in labels.values()
            else {"Unreleased", "6.0.0"})
    problems += [f"no link to the CHANGELOG's {v} section" for v in sorted(want - linked)]
    if "](existing-users.md)" not in text:
        problems.append("no link to docs/existing-users.md")
    for rx in (r"this is a release candidate", r"remains the current (?:stable )?release",
               r"\bwhen (?:it|6\.0\.0) is cut\b", r"before the final tag",
               r"to try the candidate now"):
        if re.search(rx, text, re.I):
            problems.append(f"candidate framing: /{rx}/")
    for heading, sbody in sections(_blank(text)):
        if re.search(r"known issues|sources", heading, re.I):
            continue
        problems += [f"unit id {m} under '{heading}'" for m in UNIT_ID.findall(sbody)]
    return problems


def upgrade_problems(text: str) -> list[str]:
    """AC2: an rc.1 path (reinstall at v6.0.0, what changed since, the prompt) and a 5.1 path
    (`migrate` then `migrate --apply`, with what each leaves to the reader)."""
    problems = []
    rc = section(text, r"^Upgrading from 6\.0\.0-rc\.1$")
    if rc is None:
        problems.append("no 'Upgrading from 6.0.0-rc.1' section")
    else:
        if "--version v6.0.0" not in rc:
            problems.append("the rc.1 path does not reinstall with --version v6.0.0")
        if not re.search(r"(?i)\bprompted\b", rc):
            problems.append("the rc.1 path does not say an installed candidate is prompted")
        since = section(rc, r"since the candidate", level=3)
        if since is None or len(re.findall(r"^- ", since, re.M)) < 3:
            problems.append("the rc.1 path does not list what changed since the candidate")
    old = section(text, r"^Upgrading from 5\.1$")
    if old is None:
        problems.append("no 'Upgrading from 5.1' section")
        return problems
    lines = [ln for ln in old.splitlines() if "migrate.py" in ln and ln.startswith("python3")]
    dry = [i for i, ln in enumerate(lines) if "--apply" not in ln]
    wet = [i for i, ln in enumerate(lines) if "--apply" in ln]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the 5.1 steps are not `migrate` then `migrate --apply`")
    if not re.search(r"(?i)\*\*`migrate`\*\*[^\n]*\bwrites nothing\b", old):
        problems.append("the 5.1 path does not say what the dry run leaves (it writes nothing)")
    if not re.search(r"(?i)\bit leaves to you\b", old):
        problems.append("the 5.1 path does not say what `migrate --apply` leaves to the reader")
    return problems


def units(text: str) -> list[str]:
    """Each table row, and each sentence of every other line group, with code, link targets,
    comments and headings removed."""
    text = re.sub(r"`[^`\n]*`", "", _blank(text))
    text = re.sub(r"\]\([^)]*\)", "]", text)
    out: list[str] = []
    para: list[str] = []

    def flush() -> None:
        joined = " ".join(" ".join(para).split())
        out.extend(s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(*\"])", joined) if s)
        para.clear()

    for line in text.splitlines():
        if line.startswith("|") or line.startswith("#") or not line.strip():
            flush()
            if line.startswith("|"):
                out.append(line)
            continue
        if line.startswith("- "):
            flush()
        para.append(line)
    flush()
    return out


def figure_problems(text: str) -> list[str]:
    """AC3: every sentence or table row holding a figure names its source, and none says the
    code got smaller."""
    problems = []
    for unit in units(text):
        if COUNT_LINE.match(unit.strip()):
            continue       # written by `known_issues.py write`; its paragraph names the page
        if re.search(r"\d", NOT_A_FIGURE.sub("", unit)) and not SOURCE.search(unit):
            problems.append(f"a figure with no source: {unit.strip()[:140]!r}")
    problems += [f"claims the code got smaller: {m.group(0)!r}" for m in SMALLER.finditer(text)]
    return problems


def rehearsal_findings(record: str) -> set[str]:
    """The ids in a rehearsal record's Findings table."""
    body = section(record, r"findings") or section(record, r"findings", level=3) or ""
    rows = [ln for ln in body.splitlines() if ln.startswith("|")]
    return set(re.findall(r"\b(?:BG|CR|D)\d{4}\b", "\n".join(rows)))


def soak_problems(text: str, scenarios: list[str], record: str | None) -> list[str]:
    """AC4: the migration rehearsal (linked), the eval re-run (every scenario's result, a
    scenario not run named so) and the website's sprint, each with the findings it filed."""
    soak = section(text, r"\bsoak\b")
    if soak is None:
        return ["no soak section"]
    problems = []
    strands = {"rehearsal": section(soak, r"rehears", 3), "eval": section(soak, r"\beval", 3),
               "website": section(soak, r"website", 3)}
    problems += [f"no {k} strand under the soak" for k, v in strands.items() if v is None]
    rehearsal = strands["rehearsal"] or ""
    if f"]({REHEARSAL_NAME})" not in rehearsal:
        problems.append(f"the rehearsal strand does not link {REHEARSAL_NAME}")
    if not re.search(r"(?i)\btwo\b[^.]*consuming projects", rehearsal):
        problems.append("the rehearsal strand does not say two consuming projects")
    rows = [ln for ln in (strands["eval"] or "").splitlines() if ln.startswith("| `")]
    for name in scenarios:
        row = next((r for r in rows if f"`{name}`" in r), None)
        if row is None:
            problems.append(f"the eval strand has no row for {name}")
            continue
        cells = [c.strip() for c in row.strip("|").split("|")][1:]
        blank = [c for c in cells
                 if not re.search(r"(?i)\bpass|\bfail|\bnot (?:re-)?run\b", c)]
        if len(cells) < 2 or blank:
            problems.append(f"{name}: a run column states no result")
    if SLOT.search(text):
        problems.append("a slot left for the landing is still unfilled")
    if not re.search(r"sdlc-studio\.com", strands["website"] or ""):
        problems.append("the website strand does not name the website")
    sources = section(text, r"^sources$") or ""
    for key, rx in (("rehearsal", r"rehears"), ("eval", r"\beval"), ("website", r"website")):
        row = next((ln for ln in sources.splitlines()
                    if ln.startswith("|") and re.search(rx, ln.split("|")[1], re.I)), "")
        if not re.search(r"\b(?:BG|CR)-?[0-9A-Z]{4,8}\b|\bno finding\b", row):
            problems.append(f"the Sources row for the {key} strand names no finding")
    if record is not None:
        missing = sorted(rehearsal_findings(record) - set(re.findall(r"\b\w+\b", sources)))
        problems += [f"the rehearsal record's finding {i} is not named" for i in missing]
    return problems


class ReleaseNotesTests(unittest.TestCase):

    def setUp(self) -> None:
        self.text = _read(NOTES)
        self.candidate = _read(CANDIDATE)
        self.changelog = _read(CHANGELOG)

    def mutant(self, old: str, new: str) -> str:
        """The notes with `old`, which must occur exactly once, replaced: a mutant whose anchor
        is missing or ambiguous would pass for the wrong reason."""
        self.assertEqual(1, self.text.count(old), f"mutant anchor not unique: {old[:60]!r}")
        return self.text.replace(old, new)

    def assertFlags(self, problems: list[str], expected: str) -> None:
        self.assertTrue([p for p in problems if expected in p],
                        f"no problem naming {expected!r}: {problems}")

    def test_the_notes_lead_with_themes_not_ids(self) -> None:
        """AC1. MUTANTS: the candidate's notes with the version changed ('v5.1.0 remains the
        current stable release', 'This is a release candidate'); a two-sentence opening; a theme
        dropped; the existing-users link dropped; a unit id in a themed passage; the pre-cut
        section links left in place once the cut has renamed the candidate's heading."""
        lead = lambda text: lead_problems(text, self.changelog)  # noqa: E731
        copied = self.candidate.replace("6.0.0-rc.1", "6.0.0")
        self.assertFlags(lead(copied), "framing")
        self.assertFlags(lead(self.mutant("6.0.0 is the current release: a sprint",
                                          "6.0.0 is the current release. A sprint")),
                         "the opening")
        self.assertFlags(lead(self.mutant("**One plan, one review, one signature.**",
                                          "**One plan.**")), "no theme")
        self.assertFlags(lead(self.mutant("](existing-users.md)", "]")), "existing-users")
        self.assertFlags(lead(self.mutant("## What v6 is\n", "## What v6 is\n\nSee BG0790.\n")),
                         "unit id BG0790")
        self.assertEqual([], lead(self.text))
        # The layout after the cut's rename: the links must follow it.
        cut = "## [Unreleased]\n\n## [6.0.0] - 2026-10-01\n\n## [6.0.0-rc.1] - 2026-09-26\n"
        self.assertFlags(lead_problems(self.text, cut), "6.0.0-rc.1 section")
        moved = (self.text.replace("#600---2026-09-26", "#600-rc1---2026-09-26")
                 .replace("#unreleased", "#600---2026-10-01"))
        self.assertEqual([], lead_problems(moved, cut))

    def test_both_upgrade_paths_are_given(self) -> None:
        """AC2. MUTANTS: notes addressing only a 5.1 reader (the candidate's); the rc.1 path
        without the reinstall, the prompt or what changed since; the 5.1 steps in the wrong
        order; the dry run's or the apply's leftovers unsaid."""
        self.assertFlags(upgrade_problems(self.candidate), "Upgrading from 6.0.0-rc.1")
        self.assertFlags(upgrade_problems(self.text.replace("--version v6.0.0", "--version v6")),
                         "--version v6.0.0")
        self.assertFlags(upgrade_problems(self.text.replace("prompted", "told")), "prompted")
        self.assertFlags(upgrade_problems(self.mutant("### What changed since the candidate",
                                                      "### Also")), "since the candidate")
        old = section(self.text, r"^Upgrading from 5\.1$")
        steps = [ln for ln in old.splitlines() if ln.startswith("python3")]
        swapped = self.mutant("\n".join(steps), "\n".join(reversed(steps)))
        self.assertFlags(upgrade_problems(swapped), "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("**`migrate`** writes nothing.",
                                                      "**`migrate`** runs first.")),
                         "writes nothing")
        self.assertFlags(upgrade_problems(self.mutant("Three things it leaves to you, and names:",
                                                      "Three things, named:")), "leaves to")
        self.assertEqual([], upgrade_problems(self.text))

    def test_every_figure_names_its_source(self) -> None:
        """AC3. MUTANTS: the candidate's unsourced '82% of this repository's sprint units served
        its own machinery'; a 'two-thirds smaller' claim; a sourced sentence with its source
        cut; a table row with a figure and no source. The count line `known_issues.py` writes is
        the one figure exempt."""
        self.assertTrue(figure_problems(
            "By September 2026, 82% of this repository's sprint units served its own machinery "
            "rather than the product.\n"))
        self.assertTrue(figure_problems("v6 is two-thirds smaller than v5.\n"))
        self.assertTrue(figure_problems("| a | 12 runs |\n"))
        self.assertFalse(figure_problems("| a | 12 runs (RPT0010) |\n"))
        self.assertFalse(figure_problems("82% of the last 116 units (the back-to-basics "
                                         "review). Upgrading from 5.1 to 6.0.0-rc.1.\n"))
        self.assertFalse(figure_problems("**v6.0.0 discloses 3 open defects: 3 Medium, 0 Low.**\n"))
        self.assertTrue(figure_problems("**v6.0.0 has 3 open defects.**\n"))
        cited = "and 2.51x (RPT0007-RPT0010)"
        self.assertTrue(figure_problems(self.mutant(cited, "and 2.51x")))
        self.assertEqual([], figure_problems(self.text))

    def test_the_soak_promises_are_reported(self) -> None:
        """AC4. MUTANTS: the candidate's notes (the promises made, none reported); a strand
        dropped; the rehearsal link dropped; 'two consuming projects' unsaid; a scenario's row
        dropped; a row with no result; a landing slot left unfilled; the website unnamed; a
        strand's Sources row with no finding; a rehearsal finding the notes omit."""
        names = sorted(p.stem for p in SCENARIOS.glob("*.json"))
        self.assertGreaterEqual(len(names), 9, names)
        record_path = NOTES.parent / REHEARSAL_NAME
        self.assertTrue(record_path.is_file(),
                        f"the notes link docs/{REHEARSAL_NAME}, which does not exist")
        record = _read(record_path)
        soak = lambda text, rec=record: soak_problems(text, names, rec)  # noqa: E731
        self.assertFlags(soak(self.candidate, None), "no soak section")
        self.assertFlags(soak(self.mutant("### The website's lean sprint", "### Elsewhere")),
                         "no website strand")
        self.assertFlags(soak(self.text.replace(f"]({REHEARSAL_NAME})", "]")), REHEARSAL_NAME)
        self.assertFlags(soak(self.mutant("ran on copies of two real consuming projects",
                                          "ran on copies of real projects")),
                         "two consuming projects")
        row = next(ln for ln in self.text.splitlines() if ln.startswith("| `04-"))
        self.assertFlags(soak(self.mutant(row + "\n", "")), "no row for 04-drift-reconcile")
        self.assertFlags(soak(self.mutant(row, "| `04-drift-reconcile` | Pass | Later |")),
                         "states no result")
        self.assertFlags(soak(self.text + "\n<!-- 06 re-run result -->\n"), "unfilled")
        self.assertFlags(soak(self.text.replace("sdlc-studio.com", "the site")),
                         "does not name the website")
        sources = section(self.text, r"^sources$")
        website = next(ln for ln in sources.splitlines() if ln.startswith("| The website"))
        self.assertFlags(soak(self.mutant(website, "| The website's sprint | none |")),
                         "website strand names no finding")
        self.assertEqual({"BG9999", "D9999"}, rehearsal_findings(
            "# R\n\n## Findings\n\n| Id | What |\n| --- | --- |\n| BG9999 | x |\n| D9999 | y |\n"))
        self.assertFlags(soak(self.text, "## Findings\n\n| BG9999 | x |\n"), "BG9999")
        self.assertTrue(rehearsal_findings(record), "the record's Findings table read as empty")
        self.assertEqual([], soak(self.text))


if __name__ == "__main__":
    unittest.main()
