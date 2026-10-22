"""US1094: `critic.py brief` carries the unit's own capped diff and the command that runs its
Verify lines, and each review tier states the sections it carries and its tool-call budget.

The brief named the diff scope but carried no diff and no command for the unit's Verify lines,
so a reviewer spent its turns finding the change before judging it, and the light tier carried
nearly everything the full one did. Each test drives the shipped `critic.py brief` against a
throwaway git repository whose open run names the unit, with git confined to the fixture.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo
import loader  # noqa: E402

critic = loader.load_script("critic")
SCRIPTS = loader.SCRIPTS_DIR
SKILL = SCRIPTS.parent
VERIFY_AC = SCRIPTS / "verify_ac.py"

try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover - the project config is read through PyYAML
    HAVE_YAML = False

_STORY = ("# US0001: the widget\n\n> **Status:** In Progress\n{affects}> **Points:** 2\n\n"
          "## Acceptance Criteria\n\n- [ ] **AC1** Given a widget, when it runs, then it "
          "returns one. Fails on: a widget returning two\n  - **Verify:** shell true\n")
#: Every `--- NAME ---` heading line a brief prints, by NAME. A diff line never matches: git
#: prefixes each with a space, `+` or `-`, and its own `--- a/<path>` header is lower case.
_HEADING = re.compile(r"(?m)^--- ([A-Z][A-Z' -]*?)(?: \([^\n]*\))? ---$")
_REMAINDER = re.compile(r"(\S+), (\d+) of its lines \(git diff (\S+) HEAD -- (\S+)\)")


def _repo(root: Path, affects: str | None = "src/a.py, src/b.py, src/d.py") -> str:
    """A committed project: four source files and US0001 declaring `affects` (None declares
    none). Returns the base commit."""
    (root / "src").mkdir()
    for name in "abcd":
        (root / "src" / f"{name}.py").write_text(f"{name} = 1\n", encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    line = f"> **Affects:** {affects}\n" if affects else ""
    (stories / "US0001-the-widget.md").write_text(_STORY.format(affects=line), encoding="utf-8")
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    gitutil.git(["init", "-q"], root)
    return _commit(root, "base")


def _commit(root: Path, message: str) -> str:
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-qm", message], root)
    return gitutil.git(["rev-parse", "HEAD"], root, text=True).stdout.strip()


def _grow(root: Path, name: str, lines: int) -> None:
    """Append `lines` lines to src/<name>.py."""
    path = root / "src" / f"{name}.py"
    path.write_text(path.read_text(encoding="utf-8")
                    + "".join(f"{name}{i} = {i}\n" for i in range(lines)), encoding="utf-8")


def _open_run(root: Path, batch: list[str], base: str) -> None:
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                 "started_at": "2026-10-01T08:00:00Z", "batch": batch,
                                 "base_ref": base}), encoding="utf-8")


def _config(root: Path, text: str) -> None:
    (root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")


def _brief(root: Path, *argv: str) -> subprocess.CompletedProcess:
    """The shipped verb, as a reviewer's dispatcher runs it."""
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", "US0001",
         "--seat", "qa", *argv, "--root", str(root)],
        capture_output=True, text=True, check=False, timeout=120, env=gitutil.git_env())


def _main(root: Path, *argv: str) -> str:
    """The verb in-process, so a table patched in the module reaches it; returns stdout."""
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(["brief", "--unit", "US0001", "--seat", "qa", *argv,
                          "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _diff_lines(brief: str) -> list[str] | None:
    """The UNIT DIFF section's lines after its heading, or None when the brief carries none."""
    m = re.search(r"(?m)^--- UNIT DIFF \([^\n]*\) ---\n", brief)
    if m is None:
        return None
    return brief[m.end():brief.index("\n\n", m.end())].split("\n")


def _git_diff(root: Path, base: str, *files: str) -> str:
    return gitutil.git(["diff", base, "HEAD", "--", *files], root, text=True).stdout


class ReviewBriefDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_the_brief_carries_the_units_own_diff_bounded_to_affects(self) -> None:
        """AC1. MUTANTS: the diff taken with no pathspec, which carries src/c.py's hunk; the
        working tree diffed against the base, which carries a line an isolated reviewer's
        checkout cannot see; the diff printed on stderr, outside the brief the reviewer reads
        and the fingerprint covers."""
        root = self.root
        base = _repo(root, "src/a.py, src/b.py")
        for name in "abc":
            (root / "src" / f"{name}.py").write_text(f"{name} = 2\n", encoding="utf-8")
        _commit(root, "change a, b and the undeclared c")
        _open_run(root, ["US0001"], base)
        (root / "src" / "a.py").write_text("a = 2\nUNCOMMITTED = 1\n", encoding="utf-8")
        proc = _brief(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        expected = _git_diff(root, base, "src/a.py", "src/b.py")
        self.assertIn("+a = 2", expected, "control: the fixture changed a declared file")
        self.assertIn("+b = 2", expected, "control: the fixture changed both declared files")
        self.assertEqual(expected, "\n".join(_diff_lines(proc.stdout)) + "\n")
        self.assertIn(f"--- UNIT DIFF (git diff {base} HEAD -- src/a.py src/b.py) ---",
                      proc.stdout.splitlines())
        self.assertNotIn("+c = 2", proc.stdout, "the undeclared file's hunk is in the brief")
        self.assertNotIn("UNCOMMITTED", proc.stdout, "uncommitted work is in the brief")
        self.assertNotIn("+a = 2", proc.stderr, "the diff is printed on stderr")
        # The fingerprint the verb prints is the one the in-process brief gives, diff and all.
        tier = re.search(r"review tier: (\w+)", proc.stderr).group(1)
        fp = re.search(r"brief fingerprint: ([0-9a-f]{12})", proc.stderr).group(1)
        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
            text = critic.brief(root, "US0001", "qa", tier)
        self.assertEqual(expected, "\n".join(_diff_lines(text)) + "\n")
        self.assertEqual(fp, critic.brief_fingerprint(text))

    def test_a_diff_over_the_cap_names_what_it_left_out(self) -> None:
        """AC2. MUTANTS: the diff silently truncated at the cap; a remainder giving a count but
        no command; the cap typed in the renderer rather than read from `BRIEF_DIFF_LINES` and
        `review.brief_diff_lines`. A diff within the cap carries no remainder line."""
        root = self.root
        base = _repo(root)
        _grow(root, "a", 300)
        _grow(root, "b", 200)
        _grow(root, "d", 50)
        _commit(root, "grow a, b and d")
        _open_run(root, ["US0001"], base)
        own = {f: _git_diff(root, base, f).splitlines() for f in ("src/a.py", "src/b.py",
                                                                   "src/d.py")}
        whole = _git_diff(root, base, "src/a.py", "src/b.py", "src/d.py").splitlines()
        self.assertEqual(sum(len(v) for v in own.values()), len(whole))
        for tier in critic.TIERS:
            cap = critic.BRIEF_DIFF_LINES[tier]
            self.assertLess(cap, len(whole), f"control: the diff exceeds the {tier} cap")
            proc = _brief(root, "--tier", tier)
            self.assertEqual(0, proc.returncode, proc.stderr)
            lines = _diff_lines(proc.stdout)
            self.assertEqual(whole[:cap], lines[:cap], tier)
            self.assertEqual(cap + 1, len(lines), f"{tier}: not one remainder line after the cap")
            remainder = lines[cap]
            self.assertIn(f"Diff cut at the {cap}-line cap for the {tier} tier "
                          f"(review.brief_diff_lines). Not shown: ", remainder)
            named = _REMAINDER.findall(remainder)
            # Each file cut or left out, in order, with the count of its lines not shown.
            shown, expected = 0, []
            for f, diff in own.items():
                if shown + len(diff) > cap:
                    expected.append((f, str(len(diff) - max(cap - shown, 0)), base, f))
                shown += len(diff)
            self.assertEqual(expected, named, tier)
            # The same, as literals, so the walk above cannot agree with the code by construction:
            # a.py's diff is 306 lines, b.py's 206 and d.py's 56.
            literal = {"full": [("src/b.py", "112"), ("src/d.py", "56")],
                       "light": [("src/a.py", "156"), ("src/b.py", "206"), ("src/d.py", "56")]}
            self.assertEqual(literal[tier], [(n[0], n[1]) for n in named], tier)
            self.assertEqual(len(whole) - cap, sum(int(n[1]) for n in named))
            # Each named command prints that file's diff, whose tail is what was not shown.
            for f, count, _b, _f in named:
                printed = _git_diff(root, base, f).splitlines()
                self.assertEqual(own[f][-int(count):], printed[-int(count):])
        # The declared default, not a number in the renderer: a patched table moves the cap.
        with unittest.mock.patch.dict(critic.BRIEF_DIFF_LINES, {"full": 7}):
            self.assertEqual(8, len(_diff_lines(_main(root, "--tier", "full"))))
        if not HAVE_YAML:
            self.skipTest("PyYAML not installed: the project config is not read")
        # The project's key sets the cap per tier; a value that is not a positive whole number
        # falls back to the default.
        _config(root, "review:\n  brief_diff_lines:\n    full: 9\n")
        self.assertEqual(10, len(_diff_lines(_brief(root, "--tier", "full").stdout)))
        light = critic.BRIEF_DIFF_LINES["light"]
        self.assertEqual(light + 1, len(_diff_lines(_brief(root, "--tier", "light").stdout)))
        for bad in ("0", "-3", "ten", "true", "9.5"):
            with self.subTest(value=bad):
                _config(root, f"review:\n  brief_diff_lines:\n    full: {bad}\n")
                self.assertEqual(critic.BRIEF_DIFF_LINES["full"],
                                 critic.brief_diff_cap(root, "full"))
        # Within the cap: the whole diff and no remainder line.
        _config(root, "review:\n  brief_diff_lines:\n    full: 5000\n")
        lines = _diff_lines(_brief(root, "--tier", "full").stdout)
        self.assertEqual(whole, lines)
        self.assertFalse(any(ln.startswith("Diff cut at") for ln in lines))

    def test_the_brief_names_the_command_that_runs_the_units_verify_lines(self) -> None:
        """AC3. MUTANTS: the command omitted, or naming another unit; the command without
        `--dry-run`, which writes its verdicts into the author's story file; a diff taken from a
        run about other work. With no run naming the unit the brief says no base is recorded,
        carries no diff section, and still carries the command."""
        root = self.root
        base = _repo(root)
        (root / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
        _commit(root, "change a")
        command = f"python3 {shlex.quote(str(VERIFY_AC))} run --id US0001 --dry-run"
        no_base = ("No run names this unit, so no base commit is recorded and this brief "
                   "carries no diff of it.")
        _open_run(root, ["US0001"], base)
        for tier in critic.TIERS:
            proc = _brief(root, "--tier", tier)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn(command, proc.stdout.splitlines(), tier)
            self.assertIsNotNone(_diff_lines(proc.stdout), tier)
            self.assertNotIn(no_base, proc.stdout, tier)
        # A run about other work, then no run at all: no base, no diff, the command still there.
        for label in ("other work", "no run"):
            if label == "other work":
                _open_run(root, ["US0002"], base)
            else:
                (root / "sdlc-studio" / ".local" / "run-state.json").unlink()
            for tier in critic.TIERS:
                proc = _brief(root, "--tier", tier)
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertIn(no_base, proc.stdout, (label, tier))
                self.assertIsNone(_diff_lines(proc.stdout), (label, tier))
                self.assertNotIn("UNIT DIFF", proc.stdout, (label, tier))
                self.assertNotIn(base, proc.stdout, (label, tier))
                self.assertIn(command, proc.stdout.splitlines(), (label, tier))
        # Run from the repo root, the command runs the unit's Verify lines and leaves its file
        # as it was; the same command without --dry-run writes the verdict into it.
        story = root / "sdlc-studio" / "stories" / "US0001-the-widget.md"
        before = story.read_bytes()
        run = subprocess.run(shlex.split(command), cwd=root, capture_output=True, text=True,
                             check=False, timeout=120, env=gitutil.git_env())
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        self.assertIn("US0001", run.stdout)
        self.assertEqual(before, story.read_bytes(), "the dry run wrote the unit's file")
        live = subprocess.run(shlex.split(command)[:-1], cwd=root, capture_output=True,
                              text=True, check=False, timeout=120, env=gitutil.git_env())
        self.assertEqual(0, live.returncode, live.stdout + live.stderr)
        self.assertIn("  - **Verified:** yes", story.read_text(encoding="utf-8"),
                      "control: the live run did not write its verdict into the file")

    def test_an_empty_or_untakeable_diff_is_said_and_no_affects_carries_none(self) -> None:
        """MUTANTS: an unchanged Affects rendered as an empty section; a git failure that
        refuses the brief or prints nothing; a unit with no Affects diffed with no pathspec."""
        root = self.root
        base = _repo(root)
        (root / "src" / "c.py").write_text("c = 2\n", encoding="utf-8")
        head = _commit(root, "change only the undeclared c")
        _open_run(root, ["US0001"], base)
        self.assertEqual(["(no committed change to these files since the base)"],
                         _diff_lines(_brief(root, "--tier", "light").stdout))
        _open_run(root, ["US0001"], "0" * 40)
        proc = _brief(root, "--tier", "light")
        self.assertEqual(0, proc.returncode, proc.stderr)
        said = _diff_lines(proc.stdout)
        self.assertEqual(1, len(said), said)
        self.assertTrue(said[0].startswith("(git could not take this diff: "), said)
        self.assertGreater(len(said[0]), len("(git could not take this diff: )"), said)
        # git that cannot run, or that fails saying nothing, is named rather than read as empty.
        quiet = subprocess.CompletedProcess([], 1, b"", b"")
        for answer, why in ((None, "git could not be run"), (quiet, "git exited 1")):
            with unittest.mock.patch.object(critic, "_git", return_value=answer):
                self.assertEqual([f"(git could not take this diff: {why})"],
                                 _diff_lines(critic.brief(root, "US0001", "qa", "light")))
        # No Affects declared: there is no bound, so no diff, though the run names a base.
        story = root / "sdlc-studio" / "stories" / "US0001-the-widget.md"
        story.write_text(_STORY.format(affects=""), encoding="utf-8")
        _open_run(root, ["US0001"], base)
        self.assertNotEqual(base, head)
        proc = _brief(root, "--tier", "full")
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIsNone(_diff_lines(proc.stdout))
        self.assertNotIn("+c = 2", proc.stdout)


class ReviewTierTests(unittest.TestCase):
    def test_each_tier_carries_its_declared_sections_practices_and_budget(self) -> None:
        """AC4. MUTANTS: the light tier rendering full's sections; the budget typed in the
        depth line rather than read from `TIER_TOOL_BUDGET`; `assert_brief_practices` still
        demanding all five practices at light, which refuses every light brief."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = _repo(root)
            _grow(root, "a", 200)
            _commit(root, "grow a")
            _open_run(root, ["US0001"], base)
            size = len(_git_diff(root, base, "src/a.py").splitlines())
            light_cap, full_cap = critic.BRIEF_DIFF_LINES["light"], critic.BRIEF_DIFF_LINES["full"]
            self.assertLess(light_cap, full_cap)
            self.assertTrue(light_cap < size <= full_cap, "control: the diff sits between caps")
            names = [name for name, _i, _r in critic._BRIEF_PRACTICES]
            self.assertEqual(5, len(names))
            self.assertEqual(("per-item repair verdict", "regression cover for a repair",
                              "isolated checkout for mutation"), critic.TIER_PRACTICES["light"])
            self.assertEqual(tuple(names), critic.TIER_PRACTICES["full"])
            self.assertEqual({"FILE HISTORY", "CLAIM INVENTORY"},
                             set(critic.TIER_SECTIONS["full"]) - set(critic.TIER_SECTIONS["light"]))
            briefs = {}
            for tier in critic.TIERS:
                proc = _brief(root, "--tier", tier)
                self.assertEqual(0, proc.returncode, f"{tier} refused: {proc.stderr}")
                briefs[tier] = text = proc.stdout
                headings = _HEADING.findall(text)
                self.assertEqual(len(headings), len(set(headings)), headings)
                self.assertEqual(set(critic.TIER_SECTIONS[tier]), set(headings), tier)
                present = [n for n in names if n not in critic.missing_practices(text)]
                self.assertEqual(list(critic.TIER_PRACTICES[tier]), present, tier)
                self.assertIn(f"Tool-call budget: {critic.TIER_TOOL_BUDGET[tier]} tool calls at "
                              f"the {tier} tier;", text)
                self.assertEqual(size if tier == "full" else light_cap + 1,
                                 len(_diff_lines(text)), tier)
            self.assertIn("History of the files this unit touches", briefs["full"])
            self.assertNotIn("History of the files this unit touches", briefs["light"])
            # Light never walks the corpus for the history it does not carry.
            with unittest.mock.patch("reconcile.file_history_section",
                                     side_effect=AssertionError("light walked the corpus")):
                _main(root, "--tier", "light")
            # Full carries the practices block unchanged; light, the same block less two paragraphs.
            self.assertEqual(critic._REVIEW_PRACTICES_BLOCK, critic._practices_block("full"))
            full_paras = critic._REVIEW_PRACTICES_BLOCK.split("\n\n")
            light_paras = critic._practices_block("light").split("\n\n")
            self.assertEqual(len(full_paras) - 2, len(light_paras))
            self.assertTrue(set(light_paras) < set(full_paras))
            # Light is held to its own practices only; full's demand would refuse it.
            critic.assert_brief_practices(briefs["light"], "light")
            with self.assertRaises(ValueError):
                critic.assert_brief_practices(briefs["light"], "full")
            # The tables decide: a budget or a section list patched there reaches the brief.
            with unittest.mock.patch.dict(critic.TIER_TOOL_BUDGET, {"full": 41, "light": 16}):
                for tier, n in (("full", 41), ("light", 16)):
                    self.assertIn(f"Tool-call budget: {n} tool calls at the {tier} tier;",
                                  _main(root, "--tier", tier))
            with unittest.mock.patch.dict(critic.TIER_SECTIONS,
                                          {"light": critic.TIER_SECTIONS["full"]}):
                self.assertEqual(set(critic.TIER_SECTIONS["full"]),
                                 set(_HEADING.findall(_main(root, "--tier", "light"))))

    def test_an_unknown_tier_is_refused(self) -> None:
        """MUTANT: an unknown tier read as light, as the brief did before the tables."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _repo(root)
            with self.assertRaisesRegex(ValueError, "unknown review tier 'medium'"):
                critic.brief(root, "US0001", "qa", "medium")

    def test_the_docs_and_defaults_state_the_tables(self) -> None:
        """MUTANTS: a tier's sections, practices, diff cap or budget changed in critic.py and
        not in reference-review.md's table; the cap declared in config-defaults.yaml or
        reference-config.md apart from `BRIEF_DIFF_LINES`."""
        doc = (SKILL / "reference-review.md").read_text(encoding="utf-8")
        for tier in critic.TIERS:
            row = re.search(rf"(?m)^\| {tier} \| (.*) \|$", doc)
            self.assertIsNotNone(row, f"reference-review.md has no {tier} row")
            sections, practices, cap, budget = [c.strip() for c in row.group(1).split(" | ")]
            self.assertEqual(", ".join(critic.TIER_SECTIONS[tier]), sections, tier)
            self.assertEqual(", ".join(critic.TIER_PRACTICES[tier]), practices, tier)
            self.assertEqual(str(critic.BRIEF_DIFF_LINES[tier]), cap, tier)
            self.assertEqual(str(critic.TIER_TOOL_BUDGET[tier]), budget, tier)
        caps, budget = critic.BRIEF_DIFF_LINES, critic.TIER_TOOL_BUDGET
        helped = " ".join((SKILL / "help" / "review.md").read_text(encoding="utf-8").split())
        self.assertIn(f"`review.brief_diff_lines` ({caps['full']} lines at full, "
                      f"{caps['light']} at light)", helped)
        self.assertIn(f"A tool-call budget, {budget['full']} at full and {budget['light']} at "
                      f"light,", helped)
        cfg = (SKILL / "reference-config.md").read_text(encoding="utf-8")
        declared = ", ".join(f"{t}: {critic.BRIEF_DIFF_LINES[t]}" for t in critic.TIERS)
        self.assertIn(f"| `review.brief_diff_lines` | `{declared}` |", cfg)
        if not HAVE_YAML:
            self.skipTest("PyYAML not installed")
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertEqual(critic.BRIEF_DIFF_LINES, defaults["review"]["brief_diff_lines"])


if __name__ == "__main__":
    unittest.main()
