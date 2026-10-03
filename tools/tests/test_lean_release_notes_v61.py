"""US0983: the v6.1.0 release notes lead with what changed for the person using it.

The reader is a founder-engineer on 6.0.0 deciding whether to take 6.1. Each check is a function
returning its problems, run on the notes and on a control it must refuse: the 6.0.0 notes with
the version changed, a draft composed from the changelog fragments, a figure with its source
cut. The breaking changes are judged by running each named replacement, and the CHANGELOG link
against the layout the CHANGELOG has at the time: `[Unreleased]` before the cut, `[6.1.0]`
after it.
"""
# test-census-subject: docs/release-notes-v6.1.0.md
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_lean_release_notes_v6 import (  # noqa: E402
    NOT_A_FIGURE, UNIT_ID, _blank, changelog_sections, section, sections, units)

NOTES = REPO / "docs" / "release-notes-v6.1.0.md"
NOTES_60 = REPO / "docs" / "release-notes-v6.0.0.md"
CHANGELOG = REPO / "CHANGELOG.md"
FRAGMENTS = REPO / "changelog.d"
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

THEMES = ("a run ends with its signed report", "the report states what it measured",
          "a plain install is the latest verified release",
          "migrate tells you more of what it leaves you", "fewer hand moves at the close")
#: What a figure's sentence or row may name as its source.
SOURCE = re.compile(r"RPT\d{4}|gate_timing\.py|CHANGELOG|known-issues")
#: The release numbers themselves, and an exit status, are not figures.
RELEASE = re.compile(r"\b6\.[01]\b(?!\.\d)|\b(?:at )?exits? \d\b")
COUNT_LINE = re.compile(r"^\*\*v6\.1\.0 discloses \d+ open defects: \d+ Medium, \d+ Low\.\*\*$")
#: Each breaking change, label -> (what names it, the replacement its bullet must carry).
BREAKING = {
    "the handoff writers": (r"`handoff\.py generate`.*`artifact\.py new --type handoff`",
                            r"`sprint\.py plan --worklist RPTxxxx`"),
    "--require-handoff": (r"`gate\.py --require-handoff`", r"`sprint\.py sign`"),
    "review.policy": (r"`review\.policy`", r"`migrate --apply`.*review cap"),
    "the install default": (r"(?i)plain install[^.]*`main`", r"`--version main`"),
    "the Copilot target": (r"Copilot CLI", r"`~/\.agents/skills`"),
    "the revert-check lane": (r"`revert-check` lane", r"`verify_ac\.py revert-check"),
    "validate.py check": (r"`validate\.py check` exits 1", r"`sdlc-studio/`"),
}


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _run(*argv: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(list(argv), capture_output=True, text=True, check=False, timeout=600,
                          env=_env(), cwd=str(cwd) if cwd else None)


def _py(script: str, *argv: str) -> subprocess.CompletedProcess:
    return _run(sys.executable, "-B", str(SCRIPTS / script), *argv)


def _norm(text: str) -> str:
    return " ".join(text.replace("`", "").replace("**", "").lower().split())


def figure_problems(text: str) -> list[str]:
    """Every sentence or table row holding a figure names its source."""
    problems = []
    # A code span becomes a word, so a sentence opening with one still starts a new unit
    # rather than running on into the sentence before it, whose source would excuse it.
    for unit in units(re.sub(r"`[^`\n]*`", "Code", _blank(text))):
        if COUNT_LINE.match(unit.strip()):
            continue       # written by `known_issues.py write`; its paragraph names the page
        if re.search(r"\d", RELEASE.sub("", NOT_A_FIGURE.sub("", unit))) and not SOURCE.search(unit):
            problems.append(f"a figure with no source: {unit.strip()[:140]!r}")
    return problems


def lead_problems(text: str, changelog: str) -> list[str]:
    """AC1: a one-sentence headline naming 6.1.0 as current, the five themes, the CHANGELOG
    section holding 6.1's entries and the upgrade page linked, no unit id outside the
    known-issues and sources passages, and no figure without its source."""
    problems = []
    body = text.split("\n", 1)[1] if text.startswith("# ") else text
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    headline = " ".join(paras[0].replace("**", "").split()) if paras else ""
    if len(re.findall(r"[.!?](?:\s|$)", headline)) != 1 or not re.search(
            r"\b6\.1\.0 is the current release\b", headline):
        problems.append(f"the opening is not one sentence naming 6.1.0 the current release: "
                        f"{headline[:120]!r}")
    firsts = sections(text)
    first = _norm(firsts[0][1]) if firsts else ""
    problems += [f"the first section lists no theme {t!r}" for t in THEMES if t not in first]
    labels = changelog_sections(changelog)
    linked = {labels.get(a) for a in re.findall(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)", text)}
    want = "6.1.0" if "6.1.0" in labels.values() else "Unreleased"
    if want not in linked:
        problems.append(f"no link to the CHANGELOG's {want} section")
    if "](existing-users.md)" not in text:
        problems.append("no link to docs/existing-users.md")
    for heading, sbody in sections(_blank(text)):
        if re.search(r"known issues|sources", heading, re.I):
            continue
        problems += [f"unit id {m} under '{heading}'" for m in UNIT_ID.findall(sbody)]
    return problems + figure_problems(text)


def breaking_problems(text: str) -> list[str]:
    """AC2: each change a 6.0 user meets, beside its replacement, in one bullet."""
    body = section(text, r"^Breaking changes$")
    if body is None:
        return ["no 'Breaking changes' section"]
    bullets = [" ".join(b.split()) for b in re.split(r"\n(?=- )", body) if b.startswith("- ")]
    problems = []
    for label, (names, instead) in BREAKING.items():
        hits = [b for b in bullets if re.search(names, b)]
        if not hits:
            problems.append(f"the breaking changes never name {label}")
        elif not any(re.search(instead, b) for b in hits):
            problems.append(f"{label} is named with no replacement beside it")
    return problems


def upgrade_problems(text: str) -> list[str]:
    """AC3: reinstall, `migrate` then `migrate --apply`, what each leaves, the CI limit, the HO
    files readable, and the upgrade page linked."""
    old = section(text, r"^Upgrading from 6\.0$")
    if old is None:
        return ["no 'Upgrading from 6.0' section"]
    problems = []
    if not re.search(r"(?i)\breinstall\b", old) or "latest verified release" not in old:
        problems.append("the path does not say to reinstall for the latest verified release")
    lines = [ln for ln in old.splitlines() if ln.startswith("python3") and "migrate.py" in ln]
    dry = [i for i, ln in enumerate(lines) if "--apply" not in ln]
    wet = [i for i, ln in enumerate(lines) if "--apply" in ln]
    if not (dry and wet and dry[0] < wet[0]):
        problems.append("the steps are not `migrate` then `migrate --apply`")
    if not re.search(r"\*\*`migrate`\*\*[^\n]*\bwrites nothing\b", old):
        problems.append("the path does not say the dry run writes nothing")
    apply = re.search(r"\*\*`migrate --apply`\*\*(.*?)\n\n", old, re.S)
    apply = " ".join(apply.group(1).split()) if apply else ""
    if not re.search(r"removes `review\.policy`", apply):
        problems.append("the path does not say `migrate --apply` removes `review.policy`")
    if not (re.search(r"markdown docs", apply) and all(
            n in apply for n in ("`handoff.py generate`", "`gate.py --require-handoff`"))):
        problems.append("the path does not say migrate names the retired handoff commands "
                        "in markdown docs")
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(old.split()))
    ci = [s for s in sentences if re.search(r"\bCI\b", s)]
    if not any(re.search(r"(?i)\b(?:neither|not|never)\b", s) and "scripts" in s for s in ci):
        problems.append("the path does not say migrate leaves CI files and scripts unread")
    problems += [f"a sentence implies migrate reads CI: {s[:100]!r}" for s in ci
                 if re.search(r"(?i)\b(?:reads?|scans?|searches|finds|names)\b", s)
                 and not re.search(r"(?i)\b(?:neither|nor|not|never)\b", s)]
    if not re.search(r"(?s)\bHO files\b.*?\bstay readable\b", old):
        problems.append("the path does not say the HO files stay readable")
    if "](existing-users.md)" not in old:
        problems.append("the path does not link docs/existing-users.md")
    return problems


#: A runbook holding a retired command in code, the same command in plain prose, and prose that
#: only talks about handoffs.
_RUNBOOK = ("# Ops\n"
            "\n"
            "At the close run `handoff.py generate --title \"S3\"`.\n"
            "\n"
            "We used to call handoff.py generate at the close.\n"
            "\n"
            "We read the last handoff before planning.\n")
_IN_CODE, _IN_PROSE, _ABOUT = 3, 5, 7


def migrate_sentence_problems(text: str, named: set[int]) -> list[str]:
    """BG0935: the theme bullet's account of what `migrate` names in a project's docs agrees
    with what it named in the `_RUNBOOK` fixture (`named` holds the fixture lines it named)."""
    bullet = re.search(r"(?s)^- \*\*`migrate` tells you more[^\n]*\n(?:  [^\n]*\n)*", text, re.M)
    if bullet is None:
        return ["no theme bullet on what `migrate` tells you"]
    said = " ".join(bullet.group(0).split()).split(" Its report ", 1)[0]
    problems = []
    if _IN_CODE in named and _IN_PROSE in named:
        if not re.search(r"\bin code or in plain prose\b", said):
            problems.append("the sentence does not say a retired command is named in code or "
                            "in plain prose")
        if re.search(r"(?i)leaves your prose alone", said):
            problems.append("the sentence says migrate leaves prose alone")
    if _ABOUT not in named and not re.search(r"(?i)only talks about handoffs[^.]*\bnot named",
                                             said):
        problems.append("the sentence does not say a line only talking about handoffs is "
                        "not named")
    return problems


def entries_61(changelog: str, fragments: Path = FRAGMENTS) -> list[tuple[str, str]]:
    """(section, body) of each 6.1 entry wherever the layout holds it at the time: the
    `## [6.1.0]` section's subsections once the cut has written it, the pending `changelog.d/`
    fragments only before then, so the controls built from the entries hold on both sides of the
    release commit. Once the section exists a fragment belongs to the next release: reading it
    first emptied the 6.1 Breaking entries at the first fragment written after the cut."""
    cut = re.search(r"^## \[6\.1\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.M | re.S)
    if cut:
        return [(m.group(1), m.group(2)) for m in
                re.finditer(r"^### (\w+)\n(.*?)(?=^### |\Z)", cut.group(1), re.M | re.S)]
    out = []
    for p in sorted(fragments.glob("*.md")) if fragments.is_dir() else []:
        head, _, body = p.read_text(encoding="utf-8").partition("\n")
        m = re.match(r"<!-- section: (\w+) -->", head)
        out.append((m.group(1) if m else "", body))
    return out


def install_bullet_problems(text: str) -> list[str]:
    """BG0935: the breaking bullet on the install default gives both installers' way to `main`."""
    body = section(text, r"^Breaking changes$") or ""
    bullet = next((" ".join(b.split()) for b in re.split(r"\n(?=- )", body)
                   if "A plain install no longer tracks `main`" in b), "")
    if not bullet:
        return ["no breaking bullet on the install default"]
    return [f"the install bullet does not name {flag}" for flag in ("`--version main`",
                                                                    "`-Version main`")
            if flag not in bullet]


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

    def test_the_notes_lead_with_what_changed_for_you(self) -> None:
        """AC1. MUTANTS: the 6.0.0 notes with the version changed (headline '6.0.0 is the
        current release', themes 'one plan, one review, one signature'); a draft composed from
        the fragments, which are id-laden; '29 of 34 units read NOT MEASURED' with no source;
        the `#unreleased` link left in place after the cut moved 6.1's entries under [6.1.0]."""
        lead = lambda text: lead_problems(text, self.changelog)  # noqa: E731
        copied = NOTES_60.read_text(encoding="utf-8")
        self.assertFlags(lead(copied), "the opening")
        self.assertFlags(lead(copied.replace("6.0.0", "6.1.0")), "no theme")
        fragments = "\n".join(body for _section, body in entries_61(self.changelog))
        composed = self.text.replace("## Upgrading from 6.0", fragments + "\n\n## Upgrading from 6.0")
        self.assertFlags(lead(composed), "unit id")
        self.assertFlags(lead(self.text + "\n29 of 34 units read NOT MEASURED.\n"),
                         "a figure with no source")
        self.assertFlags(lead(self.mutant("in RPT0014, 29 of 34", "in one run, 29 of 34")),
                         "a figure with no source")
        self.assertFlags(lead(self.text.replace("](existing-users.md)", "]")), "existing-users")
        self.assertEqual([], lead(self.text))

        before = re.sub(r"#610---\d{4}-\d{2}-\d{2}\)", "#unreleased)", self.text)
        self.assertIn("](../CHANGELOG.md#unreleased)", before)
        cut = "## [Unreleased]\n\n## [6.1.0] - 2026-10-04\n\n## [6.0.0] - 2026-09-29\n"
        precut = "## [Unreleased]\n\n## [6.0.0] - 2026-09-29\n"
        self.assertEqual([], lead_problems(before, precut))
        self.assertFlags(lead_problems(before, cut), "6.1.0 section")
        self.assertEqual([], lead_problems(before.replace("#unreleased)", "#610---2026-10-04)"), cut))

    def test_every_breaking_change_names_its_replacement(self) -> None:
        """AC2. MUTANTS: a section copied from the two entries filed under Breaking alone,
        which name the handoff writers and `review.policy` but not the install default or the
        Copilot target; a retired surface listed with no replacement. Each replacement the
        section names is then run."""
        breaking = [body for section_name, body in entries_61(self.changelog)
                    if section_name == "Breaking"]
        self.assertGreaterEqual(sum(len(re.findall(r"^- ", b, re.M)) for b in breaking), 2,
                                breaking)
        copied = "## Breaking changes\n\n" + "\n".join(breaking) + "\n"
        problems = breaking_problems(copied)
        self.assertFlags(problems, "the install default")
        self.assertFlags(problems, "the Copilot target")
        self.assertFlags(breaking_problems(self.mutant(
            "pass `--version main` to keep the moving branch", "it is gone")),
            "the install default is named with no replacement")
        self.assertEqual([], breaking_problems(self.text))

        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            self.assertEqual(0, _py("init.py", "run", "--root", str(root)).returncode)
            config = root / "sdlc-studio" / ".config.yaml"
            config.write_text(config.read_text(encoding="utf-8")
                              + "\nreview:\n  policy: carry-forward\n", encoding="utf-8")
            with self.subTest(replacement="sprint.py plan --worklist RPTxxxx"):
                proc = _py("sprint.py", "plan", "--root", str(root), "--worklist", "RPT0001")
                self.assertIn("signed report", proc.stdout + proc.stderr)
            with self.subTest(replacement="sprint.py sign"):
                proc = _py("sprint.py", "sign", "--help")
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertIn("--report", proc.stdout)
            with self.subTest(retired="handoff.py generate"):
                self.assertEqual(2, _py("handoff.py", "generate").returncode)
            with self.subTest(retired="gate.py --require-handoff"):
                proc = _py("gate.py", "--root", str(root), "--require-handoff", "HO0001")
                self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
            with self.subTest(replacement="migrate --apply removes review.policy"):
                proc = _py("migrate.py", "--root", str(root), "--apply")
                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                self.assertNotIn("policy", config.read_text(encoding="utf-8"))
            with self.subTest(retired="the revert-check lane"):
                proc = _py("gate.py", "--root", str(root), "--release", "--boundary", "release",
                           "--only", "revert-check", "--format", "json")
                self.assertIn("unknown check name(s): revert-check", proc.stdout)
            with self.subTest(replacement="verify_ac.py revert-check --unit"):
                proc = _py("verify_ac.py", "revert-check", "--help")
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertIn("--unit", proc.stdout)
            with self.subTest(change="validate.py check exits 1"):
                bare = Path(d) / "bare"
                bare.mkdir()
                self.assertEqual(1, _py("validate.py", "check", "--root", str(bare)).returncode)
        install = _run("bash", str(REPO / "install.sh"), "--help")
        with self.subTest(replacement="install.sh --version main"):
            self.assertEqual(0, install.returncode, install.stderr)
            self.assertRegex(install.stdout, r"--version VER[^\n]*\n?[^\n]*`main`")
        with self.subTest(change="Copilot CLI's global target"):
            self.assertRegex(install.stdout, r"(?m)^\s*copilot\s+~/\.agents/skills\b")

    def test_the_60_upgrade_path_is_given(self) -> None:
        """AC3. MUTANTS: notes telling a 6.0 project a reinstall is all it needs (no `migrate`
        lines); the two steps in the wrong order; a path implying `migrate` finds
        `gate.py --require-handoff` in a project's CI."""
        old = section(self.text, r"^Upgrading from 6\.0$")
        steps = [ln for ln in old.splitlines() if ln.startswith("python3")]
        self.assertEqual(2, len(steps), steps)
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps) + "\n", "")),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant("\n".join(steps), "\n".join(reversed(steps)))),
                         "`migrate` then `migrate --apply`")
        self.assertFlags(upgrade_problems(self.mutant(
            "Neither reads your CI files or scripts:",
            "Both also read your CI files and scripts, and name a CI job that runs it:")),
            "CI")
        self.assertFlags(upgrade_problems(self.mutant("removes `review.policy`", "keeps your config")),
                         "review.policy")
        self.assertEqual([], upgrade_problems(self.text))

    def test_the_migrate_and_install_sentences_are_true(self) -> None:
        """BG0935 AC1. MUTANTS: the theme bullet saying `migrate` names a retired command 'in
        code' and 'leaves your prose alone', when a fixture shows it names the same command in
        plain prose; the install bullet with `--version main` alone, which gives a Windows
        user no way back to `main`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            self.assertEqual(0, _py("init.py", "run", "--root", str(root)).returncode)
            (root / "docs").mkdir()
            (root / "docs" / "ops.md").write_text(_RUNBOOK, encoding="utf-8")
            proc = _py("migrate.py", "--root", str(root), "--format", "json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        named = {item["line"] for item in json.loads(proc.stdout)["needs_human"]
                 if item.get("kind") == "retired-surface" and item.get("file") == "docs/ops.md"}
        self.assertEqual({_IN_CODE, _IN_PROSE}, named, "the fixture no longer shows the split")
        self.assertFlags(migrate_sentence_problems(
            "- **`migrate` tells you more of what it leaves you.** It names each line of your "
            "markdown docs\n  that still runs a retired command in code, with what replaced it, "
            "and leaves your prose alone.\n", named), "leaves prose alone")
        self.assertEqual([], migrate_sentence_problems(self.text, named))

        self.assertFlags(install_bullet_problems(self.mutant(
            " (`-Version main`\n  for `install.ps1`)", "")), "`-Version main`")
        self.assertEqual([], install_bullet_problems(self.text))
        ps1 = (REPO / "install.ps1").read_text(encoding="utf-8")
        self.assertRegex(ps1, r"(?m)^\s*-Version VER\b[^\n]*\bmain\b",
                         "install.ps1 does not take -Version main")

    def test_a_fragment_written_after_the_cut_leaves_the_61_entries_read(self) -> None:
        """US0985 round-1 REJECT. MUTANT: `entries_61` reading any pending fragment in
        preference to the cut `## [6.1.0]` section, so the first fragment of the next release
        (a Fixed BG9999 here) replaced 6.1's entries and AC2 read 0 Breaking bullets. The
        fragment lives in a temp directory; the real `changelog.d/` is never written."""
        cut = re.search(r"(?m)^## \[6\.1\.0\][^\n]*\n(.*?)(?=^## \[|\Z)", self.changelog, re.S)
        self.assertIsNotNone(cut, "premise: the CHANGELOG holds the cut [6.1.0] section")
        late = "- **A fix after the cut (BG9999).** Mended.\n"
        with tempfile.TemporaryDirectory() as d:
            frags = Path(d)
            (frags / "BG9999.md").write_text(f"<!-- section: Fixed -->\n{late}", encoding="utf-8")
            after = entries_61(self.changelog, frags)
            self.assertEqual(entries_61(self.changelog, frags / "absent"), after,
                             "a post-cut fragment changed the 6.1 entries")
            self.assertNotIn(late, [body for _s, body in after])
            breaking = [body for s, body in after if s == "Breaking"]
            self.assertGreaterEqual(sum(len(re.findall(r"^- ", b, re.M)) for b in breaking), 2)
            # The control: before the cut there is no section, and the fragments are the entries.
            precut = self.changelog.replace(cut.group(0), "", 1)
            self.assertEqual([("Fixed", late)], entries_61(precut, frags))


if __name__ == "__main__":
    unittest.main()
