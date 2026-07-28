"""Unit tests for constitution.py - the project-constitution gate (RFC0005).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "constitution.py"


def _load():
    spec = importlib.util.spec_from_file_location("constitution", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["constitution"] = mod
    spec.loader.exec_module(mod)
    return mod


con = _load()

try:
    import yaml as _yaml  # noqa: F401
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def _story(root: Path, num: int, *, epic: bool = True, ac: bool = True,
           verify: bool = True, status: str = "Ready") -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# US{num:04d}: s", "", f"> **Status:** {status}"]
    if epic:
        lines.append("> **Epic:** [EP0001: x](../epics/EP0001-x.md)")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing"]
        if verify:
            lines.append("- **Verify:** shell echo ok")
    (d / f"US{num:04d}-s.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _epic(root: Path, num: int = 1) -> None:
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"EP{num:04d}-x.md").write_text(f"# EP{num:04d}: x\n\n> **Status:** Ready\n", encoding="utf-8")


def _const(root: Path, body: str) -> None:
    d = root / "sdlc-studio"
    d.mkdir(parents=True, exist_ok=True)
    (d / "constitution.md").write_text(body, encoding="utf-8")


class ParseTests(unittest.TestCase):
    def test_extracts_text_and_rule(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _const(root, "## Principles\n\n"
                   "- **Stories trace to an epic.** `rule: story-requires-epic`\n"
                   "- **No PII in logs.**\n")
            ps = con.parse_constitution(root)
            self.assertEqual(ps[0], {"text": "Stories trace to an epic.", "rule": "story-requires-epic"})
            self.assertEqual(ps[1], {"text": "No PII in logs.", "rule": None})


class CheckTests(unittest.TestCase):
    def test_no_constitution_is_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = con.check_constitution(Path(d))
            self.assertFalse(res["exists"])
            self.assertTrue(res["ok"])

    def test_passing_principle(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=True)
            _const(root, "- **Stories trace to an epic.** `rule: story-requires-epic`\n")
            res = con.check_constitution(root)
            self.assertIn("story-requires-epic", res["gated"])
            self.assertEqual(res["violations"], [])
            self.assertTrue(res["ok"])

    def test_violated_principle_reported(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)  # missing Epic -> violates the principle
            _const(root, "- **Stories trace to an epic.** `rule: story-requires-epic`\n")
            res = con.check_constitution(root)
            self.assertFalse(res["ok"])
            self.assertEqual(res["violations"][0]["rule"], "story-requires-epic")
            self.assertTrue(any("US0001" in it for it in res["violations"][0]["items"]))

    def test_advisory_default_exits_zero_despite_violation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)
            _const(root, "- **Stories trace to an epic.** `rule: story-requires-epic`\n")
            args = con.build_parser().parse_args(["check", "--root", str(root)])
            self.assertEqual(args.func(args), 0)  # advisory -> never fails the run

    @unittest.skipUnless(_HAS_YAML, "enforce reads .config.yaml (needs PyYAML)")
    def test_enforced_violation_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)
            _const(root, "- **Stories trace to an epic.** `rule: story-requires-epic`\n")
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "constitution:\n  enforce: true\n", encoding="utf-8")
            args = con.build_parser().parse_args(["check", "--root", str(root)])
            self.assertEqual(args.func(args), 1)  # opted-in -> blocking

    def test_advisory_principle_listed_not_gated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _const(root, "- **No PII in logs.**\n")
            res = con.check_constitution(root)
            self.assertIn("No PII in logs.", res["advisory"])
            self.assertEqual(res["gated"], [])

    def test_unknown_rule_flagged_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _const(root, "- **Weird one.** `rule: made-up-rule`\n")
            res = con.check_constitution(root)
            self.assertIn("made-up-rule", res["unknown_rules"])
            self.assertTrue(res["ok"])  # unknown rule is a config issue, not a violation


class RuleCoverageTests(unittest.TestCase):
    """Each checkable rule fires on a violation and is silent when satisfied (a rule
    that silently no-ops gives false assurance)."""

    def _check(self, root: Path, rule: str):
        _const(root, f"- **P.** `rule: {rule}`\n")
        return con.check_constitution(root)

    def test_links_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as d:  # story refs EP0001 that doesn't exist
            root = Path(d)
            _story(root, 1, epic=True)
            self.assertFalse(self._check(root, "links-resolve")["ok"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=True)
            _epic(root, 1)
            self.assertTrue(self._check(root, "links-resolve")["ok"])

    def test_ac_requires_verify(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, verify=False)
            self.assertFalse(self._check(root, "ac-requires-verify")["ok"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, verify=True)
            self.assertTrue(self._check(root, "ac-requires-verify")["ok"])

    def test_story_has_ac(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, ac=False)
            self.assertFalse(self._check(root, "story-has-ac")["ok"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, ac=True)
            self.assertTrue(self._check(root, "story-has-ac")["ok"])

    def test_status_in_vocab(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Bogus")
            self.assertFalse(self._check(root, "status-in-vocab")["ok"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Ready")
            self.assertTrue(self._check(root, "status-in-vocab")["ok"])

    def test_no_index_drift(self) -> None:
        def _seed(root, index_status):
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True, exist_ok=True)
            (d / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Done\n"
                "> **Epic:** [EP0001](../epics/EP0001-x.md)\n", encoding="utf-8")
            (d / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
                f"| {index_status} | 1 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                f"| [US0001](US0001-x.md) | s | {index_status} |\n", encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:  # file Done, index Draft -> drift
            root = Path(d)
            _seed(root, "Draft")
            self.assertFalse(self._check(root, "no-index-drift")["ok"])
        with tempfile.TemporaryDirectory() as d:  # index matches file
            root = Path(d)
            _seed(root, "Done")
            self.assertTrue(self._check(root, "no-index-drift")["ok"])

    def test_bare_rule_in_prose_is_advisory_not_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _const(root, "- **Follow the golden rule: be kind.**\n")
            res = con.check_constitution(root)
            self.assertIn("Follow the golden rule: be kind.", res["advisory"])
            self.assertEqual(res["unknown_rules"], [])


class LaneCostTests(unittest.TestCase):
    """The constitution lane is the per-commit gate's dominant cost, and none of it buys
    an answer the declared rules read.

    Measured on this repo in fresh processes: the whole artefact gate 32.9s, the
    constitution lane 26.6s of it. Profiled, the 26.6s is 107 `pytest --collect-only`
    subprocesses inside `verify_ac.unresolvable_stamps`, reached because the
    conformance-backed rules asked for the WHOLE-workspace sweep - which computes the
    Done-only stages (verified, critiqued, ...) for every Done story. The two rules that
    ask for it read `specified` and `verifiable`, the Definition-of-Ready signals, which
    are computed for every unit whatever the scope. So the lane paid for the Done-only
    half and threw it away.

    These are CALLER tests: they drive `check_constitution`, which is what gate.py's
    constitution lane calls, not the individual rule functions.
    """

    def _done_story_with_a_stamped_verifier(self, root: Path) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / "US0001-s.md").write_text(
            "# US0001: s\n\n> **Status:** Done\n"
            "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n\n- **Given** a thing\n"
            "- **Verify:** pytest tests/test_thing.py::Klass::test_it\n"
            "- **Verified:** yes\n", encoding="utf-8")

    def test_the_lane_does_not_pay_the_done_only_verification_sweep(self) -> None:
        """RED before the fix: `unresolvable_stamps` is reached once per stamped Done
        criterion, each a `pytest --collect-only` subprocess."""
        import conformance as conf
        calls: list = []
        real = conf.verify_ac.unresolvable_stamps

        def spy(path, cwd=None):
            calls.append(str(path))
            return real(path, cwd)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._done_story_with_a_stamped_verifier(root)
            _epic(root, 1)
            _const(root, "- **P.** `rule: story-has-ac`\n")
            conf.verify_ac.unresolvable_stamps = spy
            try:
                res = con.check_constitution(root)
            finally:
                conf.verify_ac.unresolvable_stamps = real
        self.assertTrue(res["ok"])
        self.assertEqual(calls, [], "the constitution lane reads only the "
                                    "Definition-of-Ready stages, so it must not run the "
                                    "per-criterion selector-resolution sweep")

    def test_a_detector_two_rules_share_runs_once(self) -> None:
        """`story-requires-epic` and `links-resolve` both read the integrity census. Two
        declared principles must not mean two full censuses."""
        runs: list = []
        real = con.integrity.detect_integrity

        def spy(root):
            runs.append(str(root))
            return real(root)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=True)
            _epic(root, 1)
            _const(root, "- **A.** `rule: story-requires-epic`\n"
                         "- **B.** `rule: links-resolve`\n")
            con.integrity.detect_integrity = spy
            try:
                res = con.check_constitution(root)
            finally:
                con.integrity.detect_integrity = real
        self.assertTrue(res["ok"])
        self.assertEqual(len(runs), 1,
                         f"the integrity census must run once per check, ran {len(runs)}")

    def test_the_cache_does_not_outlive_the_run(self) -> None:
        """A memo that survived the call would answer the SECOND check from the FIRST
        tree - the gate would then pass a repo it had never looked at."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=True)
            _epic(root, 1)
            _const(root, "- **P.** `rule: story-requires-epic`\n")
            self.assertTrue(con.check_constitution(root)["ok"])
            _story(root, 1, epic=False)   # same path, now violating
            self.assertFalse(con.check_constitution(root)["ok"],
                             "a re-check must read the tree again, not a stale memo")


if __name__ == "__main__":
    unittest.main()
