"""Unit tests for tools/check_script_tests.py (US0456).

The TSD said "Every script has a matching `test_<script>.py`" and, separately, that every script
and shared-library module has a dedicated test module. Neither was true - three modules have
none - and the document itself admitted, two hundred lines away, that "no sweep enumerates the
scripts and fails a build on a module that arrives without a test". This is that sweep.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "check_script_tests.py"
_spec = importlib.util.spec_from_file_location("check_script_tests", TOOL)
assert _spec and _spec.loader
cst = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cst)

_MAP = """#### Unit coverage map

Some prose about the map.

```text
{listed}
```

More prose.
"""

_PASSAGES = """**Script tier - test-driven, executable.** Nearly every script has a partner.

---

The 80% floor is the **hard gate**; the aspiration is a dedicated module bar the exceptions.

```bash
echo done
```
"""


def _tree(root: Path, top: list[str], lib: list[str], tests: list[str], listed: list[str]):
    scripts = root / cst.SCRIPTS_REL
    (scripts / "lib").mkdir(parents=True)
    (scripts / "tests").mkdir(parents=True)
    (scripts / "lib" / "__init__.py").write_text("", encoding="utf-8")
    for name in top:
        (scripts / f"{name}.py").write_text("x = 1\n", encoding="utf-8")
    for name in lib:
        (scripts / "lib" / f"{name}.py").write_text("x = 1\n", encoding="utf-8")
    for name in tests:
        (scripts / "tests" / f"test_{name}.py").write_text("x = 1\n", encoding="utf-8")
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / cst.TSD_REL).write_text(
        _MAP.format(listed="\n".join(listed)) + _PASSAGES, encoding="utf-8")
    return root


class SweepDerivesTheModuleSet(unittest.TestCase):

    def _root(self, **kw) -> Path:
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return _tree(d, **kw)

    def test_new_untested_top_level_and_lib_modules_are_both_reported(self) -> None:
        """Both, because a `scripts/*.py`-shaped glob silently drops the shared library - the
        exemption-by-omission that would lose `lib/tiers` without anyone deciding to."""
        root = self._root(top=["alpha", "fresh"], lib=["shared", "newlib"],
                          tests=["alpha", "shared"], listed=[])
        swept = cst.untested_modules(root)
        self.assertIn("fresh", swept, "a new top-level module with no test was not reported")
        self.assertIn("lib/newlib", swept, "a new lib module with no test was not reported")

    def test_tests_and_lib_dunder_init_are_excluded_by_a_rule_the_test_exercises(self) -> None:
        root = self._root(top=["alpha"], lib=["shared"], tests=["alpha", "shared"], listed=[])
        swept = cst.untested_modules(root)
        self.assertEqual([], swept, f"the sweep reported something it should exclude: {swept}")

    def test_an_absent_scripts_dir_refuses_and_names_IT(self) -> None:
        """A sweep over nothing reports zero exceptions, which reads exactly like a clean tree.

        The MESSAGE is asserted, not merely the exception type: both guards raise `Unreadable`,
        so a type-only assertion is satisfied by whichever one happens to fire and the first
        guard could be deleted unnoticed. Caught by mutation."""
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        with self.assertRaises(cst.Unreadable) as ctx:
            cst.untested_modules(d)
        msg = str(ctx.exception)
        self.assertIn(cst.SCRIPTS_REL, msg)
        self.assertNotIn("/tests", msg,
                         "the scripts-absent case was reported as the tests-absent one, so the "
                         "first guard is not what refused")

    def test_an_absent_tests_dir_refuses_and_names_THAT(self) -> None:
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / cst.SCRIPTS_REL).mkdir(parents=True)
        with self.assertRaises(cst.Unreadable) as ctx:
            cst.untested_modules(d)
        self.assertIn("/tests", str(ctx.exception))


class TsdExceptionListAgreesWithTheSweep(unittest.TestCase):

    def _root(self, **kw) -> Path:
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        return _tree(d, **kw)

    def test_the_list_and_the_sweep_disagree_in_either_direction_and_exit_non_zero(self) -> None:
        # Direction 1: a swept module the list omits - an undeclared gap.
        root = self._root(top=["alpha", "untested"], lib=[], tests=["alpha"], listed=[])
        errors = cst.check(root)
        self.assertTrue(errors)
        self.assertIn("untested", errors[0])
        self.assertIn("does not name it", errors[0])

        # Direction 2: a listed module that now HAS a test - a stale exemption.
        root2 = self._root(top=["alpha"], lib=[], tests=["alpha"], listed=["alpha"])
        errors2 = cst.check(root2)
        self.assertTrue(errors2)
        self.assertIn("alpha", errors2[0])
        self.assertIn("stale exemption", errors2[0])

        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, cst.main(["--root", str(root)]))
            self.assertEqual(1, cst.main(["--root", str(root2)]))

    def test_an_agreeing_list_passes(self) -> None:
        """The positive control: a checker that failed both directions always would pass the
        test above while being useless."""
        root = self._root(top=["alpha", "indirect"], lib=[], tests=["alpha"],
                          listed=["indirect"])
        self.assertEqual([], cst.check(root))

    def test_a_missing_fenced_list_refuses(self) -> None:
        root = self._root(top=["alpha"], lib=[], tests=["alpha"], listed=[])
        (root / cst.TSD_REL).write_text("#### Unit coverage map\n\nprose only\n", encoding="utf-8")
        with self.assertRaises(cst.Unreadable):
            cst.declared_exceptions(root)


class TheShippedDocumentAgrees(unittest.TestCase):

    def test_the_real_tsd_map_matches_the_real_scripts_tree(self) -> None:
        """Against the live repository, because that is the whole point of the lane."""
        self.assertEqual([], cst.check(REPO),
                         "this repository's own TSD disagrees with its scripts tree")
        self.assertEqual(["carry_forward", "triage", "lib/tiers"],
                         sorted(cst.untested_modules(REPO),
                                key=["carry_forward", "triage", "lib/tiers"].index),
                         "the shipped indirect-only set changed - update the TSD's map")


class AbsoluteClaimsAreRefused(unittest.TestCase):

    def test_a_denied_phrase_fails_and_a_renamed_heading_fails_loud(self) -> None:
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        root = _tree(d, top=["alpha"], lib=[], tests=["alpha"], listed=[])
        # A denied phrase inside its own located passage.
        text = (root / cst.TSD_REL).read_text(encoding="utf-8").replace(
            "Nearly every script has a partner.", "Every script has a matching partner.")
        (root / cst.TSD_REL).write_text(text, encoding="utf-8")
        found = cst.denied_claims(root)
        self.assertTrue(found, "a denied absolute claim was not reported")
        self.assertIn("Script tier", found[0], "the finding does not name the passage")

        # A renamed heading fails loud rather than matching nothing and reporting clean.
        (root / cst.TSD_REL).write_text("#### Unit coverage map\n\n```text\n```\n", encoding="utf-8")
        with self.assertRaises(cst.Unreadable) as ctx:
            cst.denied_claims(root)
        self.assertIn("could not locate", str(ctx.exception))

    def test_the_real_tsd_carries_no_denied_claim(self) -> None:
        self.assertEqual([], cst.denied_claims(REPO))

    def test_a_denied_claim_reaches_the_checker_not_only_the_helper(self) -> None:
        """Through `check()`, because the sibling tests call `denied_claims` directly and so
        survived a mutant that dropped the call from the checker entirely. A helper nothing
        invokes is a helper that reports nothing."""
        d = Path(tempfile.mkdtemp(prefix="scripttests_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        root = _tree(d, top=["alpha"], lib=[], tests=["alpha"], listed=[])
        text = (root / cst.TSD_REL).read_text(encoding="utf-8").replace(
            "Nearly every script has a partner.", "Every script has a matching partner.")
        (root / cst.TSD_REL).write_text(text, encoding="utf-8")
        errors = cst.check(root)
        self.assertTrue(any("Script tier" in e for e in errors),
                        f"the checker did not surface the denied claim: {errors}")


class TheCheckerIsAGateLane(unittest.TestCase):

    def test_the_checker_is_wired_into_npm_lint_and_the_pre_commit_hook(self) -> None:
        """A binary only its own fixtures invoke is not a lane."""
        pkg = json.loads((REPO / "package.json").read_text(encoding="utf-8"))
        lint = pkg["scripts"]["lint"]
        self.assertIn("lint:script-tests", lint, "the checker is not in the npm lint chain")
        self.assertIn("check_script_tests.py", pkg["scripts"]["lint:script-tests"])
        hook = (REPO / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn("check_script_tests.py", hook,
                      "the checker is not a lane in the gate people actually run")


if __name__ == "__main__":
    unittest.main()
