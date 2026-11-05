"""The pre-commit `budgets` lane's docgen checks: generated-doc drift refused before the suites
(BG1226).

Run six, twice: a commit added a verb to sprint.py without regenerating
`reference-scripts-surface.md`, and the drift surfaced only as `test_lean_*` assertions after the
selected suites had run for 1,016 s and for over 1,500 s. The three `docgen.py ... --check` lanes
take seconds and EXIT 0 on drift by design, so the lane reads their counts. They are folded into
the `budgets` lane so the commit's lane count stays at its cap, and each runs only when the commit
stages what it derives from: `surface` for a skill script, the other two for a reference or help.

These tests RUN THE REAL HOOK against the REAL `docgen.py` and its `lib/` in a throwaway repo
holding a one-verb script, its generated page, one reference and the reference index. Every other
lane's script is a stub that passes, so the only lane that can refuse is the one under test. The
gate stub notes each `--suite-decision` call in a marker file: the suites are decided after the
cheap lanes, so a refusal that leaves no marker was made before any suite was decided or run.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"
SKILL_SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
SKILL = ".claude/skills/sdlc-studio"

PASS_SH = "#!/usr/bin/env bash\nexit 0\n"
PASS_PY = "import sys\nsys.exit(0)\n"
#: The gate stub: it passes, and it notes the suite decision being asked for.
GATE_STUB = ("import sys\nfrom pathlib import Path\n"
             "if '--suite-decision' in sys.argv:\n"
             "    Path('suite-decision.called').write_text('yes', encoding='utf-8')\n"
             "sys.exit(0)\n")


def _tiny(verbs: tuple[str, ...]) -> str:
    """A script whose CLI surface is exactly `verbs`, the way the surface page enumerates one."""
    adds = "".join(f"    sub.add_parser({v!r})\n" for v in verbs)
    return ("import argparse\n\n\ndef build_parser():\n"
            "    p = argparse.ArgumentParser(prog='tiny.py')\n"
            "    sub = p.add_subparsers(dest='cmd', required=True)\n"
            f"{adds}    return p\n")


def _load_gitutil():
    """The shipped git-fixture helper, whose `git_env` confines every git call here to the
    fixture. Loaded rather than re-implemented, so this module carries no second copy of the
    repo-locating list for `tools/tests/test_skill_tests_env.py` to pin."""
    import importlib.util
    import sys
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_pre_commit_docgen_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()


def _clean_env() -> dict:
    return gitutil.git_env()


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


def _docgen(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["python3", f"{SKILL}/scripts/docgen.py", *args], cwd=root,
                          capture_output=True, text=True, env=_clean_env())


class DocgenLaneTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._repo(Path(self._tmp.name))

    def _repo(self, tmp: Path) -> Path:
        root = tmp / "r"
        skill = root / SKILL
        (root / ".githooks").mkdir(parents=True)
        (root / "tools").mkdir()
        (root / "node_modules" / ".bin").mkdir(parents=True)
        (skill / "help").mkdir(parents=True)

        hook = root / ".githooks" / "pre-commit"
        hook.write_text(HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        hook.chmod(0o755)
        for rel in ("tools/lint-style.sh", "tools/check_action_pins.sh",
                    "node_modules/.bin/markdownlint"):
            (root / rel).write_text(PASS_SH, encoding="utf-8")
            (root / rel).chmod(0o755)
        # DERIVED from the hook - see tools/tests/hookutil.py - so a lane added to the gate
        # reaches this fixture without an edit here.
        from hookutil import hook_skill_scripts, hook_tool_scripts
        for name in hook_tool_scripts():
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")

        # The REAL docgen and the library it imports; every other lane script is a stub.
        shutil.copytree(SKILL_SCRIPTS / "lib", skill / "scripts" / "lib",
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
        shutil.copy2(SKILL_SCRIPTS / "docgen.py", skill / "scripts" / "docgen.py")
        for rel in hook_skill_scripts():
            if not (root / rel).exists():
                (root / rel).write_text(PASS_PY, encoding="utf-8")
        (skill / "scripts" / "gate.py").write_text(GATE_STUB, encoding="utf-8")
        (skill / "scripts" / "tiny.py").write_text(_tiny(("alpha",)), encoding="utf-8")

        markers = "<!-- BEGIN GENERATED -->\n<!-- END GENERATED -->\n"
        (skill / "reference-scripts-surface.md").write_text(
            f"# Scripts surface\n\n{markers}", encoding="utf-8")
        (skill / "reference-sample.md").write_text(
            "# Sample\n\n> A sample reference.\n\nBody.\n", encoding="utf-8")
        (skill / "help" / "references.md").write_text(
            f"# References\n\n{markers}", encoding="utf-8")
        (root / "notes.txt").write_text("notes\n", encoding="utf-8")
        for verb in ("surface", "references", "reading-guides"):
            gen = _docgen(root, verb)
            assert gen.returncode == 0, gen.stdout + gen.stderr

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        # The control every test leans on: the fixture as built carries no drift at all.
        for verb in ("surface", "references", "reading-guides"):
            check = _docgen(root, verb, "--check")
            assert ": 0 drift item(s)" in check.stdout, check.stdout + check.stderr
        return root

    def _commit(self, *paths: str) -> tuple[int, str]:
        _git(self.root, "add", "--", *paths)
        out = subprocess.run(["git", "-C", str(self.root), "commit", "-m", "change"],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr

    def _drift_the_script(self) -> str:
        """Give tiny.py a second verb the generated page does not list."""
        rel = f"{SKILL}/scripts/tiny.py"
        (self.root / rel).write_text(_tiny(("alpha", "beta")), encoding="utf-8")
        return rel

    def _decided(self) -> bool:
        return (self.root / "suite-decision.called").exists()

    def _loose_reference(self) -> None:
        """Leave an UNTRACKED reference in the tree, so the reference index drifts unstaged."""
        (self.root / SKILL / "reference-loose.md").write_text(
            "# Loose\n\n> A loose reference.\n", encoding="utf-8")

    def test_a_drifting_script_is_refused_before_any_suite_is_decided(self) -> None:
        """MUTANTS: no docgen check in the lane (the commit lands); the lane trusts docgen's
        exit status, which is 0 on drift (the commit lands); the check runs after the suite
        decision (the gate stub's marker is written)."""
        rc, out = self._commit(self._drift_the_script())
        self.assertNotEqual(0, rc, f"drift was not refused:\n{out}")
        self.assertIn("FAIL budgets", out)
        self.assertIn("docgen surface: 1 drift item(s)", out)
        self.assertIn(f"python3 {SKILL}/scripts/docgen.py surface", out,
                      "the refusal does not name the regenerate command")
        self.assertIn("unit suites - a cheaper lane already failed", out)
        self.assertFalse(self._decided(), f"the suites were decided before the refusal:\n{out}")

    def test_the_regenerated_page_staged_passes(self) -> None:
        """The positive control. MUTANTS: the lane refuses whenever it runs; it reads `drift
        item(s)` with any count as drift."""
        script = self._drift_the_script()
        self.assertEqual(0, _docgen(self.root, "surface").returncode)
        rc, out = self._commit(script, f"{SKILL}/reference-scripts-surface.md")
        self.assertEqual(0, rc, f"a regenerated page was refused:\n{out}")
        self.assertIn("ok   budgets", out)
        self.assertTrue(self._decided(), "the hook stopped before the suite decision")

    def test_a_staged_script_runs_only_the_surface_check(self) -> None:
        """MUTANT: a staged script runs all three checks (the unstaged index drift refuses)."""
        self._loose_reference()
        rel = f"{SKILL}/scripts/tiny.py"
        (self.root / rel).write_text(_tiny(("alpha",)) + "# a comment\n", encoding="utf-8")
        rc, out = self._commit(rel)
        self.assertEqual(0, rc, f"a script with no surface drift was refused:\n{out}")
        self.assertIn("ok   budgets", out)

    def test_a_new_reference_without_its_index_row_is_refused(self) -> None:
        """A staged reference-*.md runs the index check, which refuses. MUTANTS: the path match
        omits references; the lane runs only `docgen surface`."""
        (self.root / SKILL / "reference-added.md").write_text(
            "# Added\n\n> An added reference.\n", encoding="utf-8")
        rc, out = self._commit(f"{SKILL}/reference-added.md")
        self.assertNotEqual(0, rc, f"an unindexed reference was not refused:\n{out}")
        self.assertIn("docgen references: 1 drift item(s)", out)

    def test_a_staged_reference_runs_no_surface_check(self) -> None:
        """MUTANT: a staged reference runs the surface check too (the unstaged script drift
        refuses). The reference is staged with its regenerated index, so only surface drifts."""
        self._drift_the_script()
        (self.root / SKILL / "reference-added.md").write_text(
            "# Added\n\n> An added reference.\n", encoding="utf-8")
        for verb in ("references", "reading-guides"):
            self.assertEqual(0, _docgen(self.root, verb).returncode)
        rc, out = self._commit(f"{SKILL}/reference-added.md", f"{SKILL}/help/references.md")
        self.assertEqual(0, rc, f"a regenerated reference index was refused:\n{out}")
        self.assertIn("ok   budgets", out)

    def test_a_staged_help_file_runs_the_index_check(self) -> None:
        """MUTANT: the path match omits `help/`. The index drift is left unstaged in the tree:
        the lane reads the working tree, so a check that runs refuses and one that skips does
        not."""
        self._loose_reference()
        (self.root / SKILL / "help" / "extra.md").write_text("# Extra\n", encoding="utf-8")
        rc, out = self._commit(f"{SKILL}/help/extra.md")
        self.assertNotEqual(0, rc, f"a staged help file did not run the index check:\n{out}")
        self.assertIn("docgen references: 1 drift item(s)", out)

    def test_a_commit_staging_no_script_reference_or_help_file_skips_the_checks(self) -> None:
        """MUTANT: the docgen checks run on every commit (the unstaged drift below refuses)."""
        self._drift_the_script()
        self._loose_reference()
        (self.root / "notes.txt").write_text("more notes\n", encoding="utf-8")
        rc, out = self._commit("notes.txt")
        self.assertEqual(0, rc, f"a commit staging no docgen input was refused:\n{out}")
        self.assertIn("ok   budgets", out)
        self.assertIn("budgets - docgen checks skipped: no skill script, reference-*.md or "
                      "help/ file staged", out)

    def test_a_tree_with_no_docgen_notes_the_checks_skipped(self) -> None:
        """The hook-test fixtures elsewhere carry no `docgen.py`, and the first build refused
        every commit there that staged a script or a reference ("can't open file"). MUTANTS:
        the absent-docgen skip removed (the commit is refused); the skip keyed on anything but
        `docgen.py` being absent (the drift tests above are no longer refused)."""
        _git(self.root, "rm", "-q", f"{SKILL}/scripts/docgen.py")
        _git(self.root, "commit", "-q", "--no-verify", "-m", "no docgen")
        script = self._drift_the_script()
        (self.root / SKILL / "reference-added.md").write_text(
            "# Added\n\n> An added reference.\n", encoding="utf-8")
        rc, out = self._commit(script, f"{SKILL}/reference-added.md")
        self.assertEqual(0, rc, f"a tree with no docgen.py was refused:\n{out}")
        self.assertIn("ok   budgets", out)
        self.assertIn(f"budgets - docgen checks skipped: no {SKILL}/scripts/docgen.py in this "
                      "tree", out)
        self.assertNotIn("can't open file", out)
        self.assertTrue(self._decided(), "the hook stopped before the suite decision")

    def test_list_names_both_checks_under_budgets(self) -> None:
        """MUTANT: the budgets rule text is left naming only the line ceiling."""
        r = subprocess.run([str(HOOK), "--list"], capture_output=True, text=True,
                           cwd=self.root, env=_clean_env())
        rules = dict(line.split("\t", 1) for line in r.stdout.splitlines() if "\t" in line)
        self.assertNotIn("docgen", rules, "docgen is its own lane again, over the lane cap")
        self.assertIn("line ceiling", rules.get("budgets", ""), r.stdout)
        self.assertIn("docgen surface --check", rules["budgets"])
        self.assertIn("docgen references --check", rules["budgets"])


if __name__ == "__main__":
    unittest.main()
