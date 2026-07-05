"""Unit tests for critic.py - committed critic-verdict record (CR0023). RED first."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"


def _load():
    spec = importlib.util.spec_from_file_location("critic", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = mod
    spec.loader.exec_module(mod)
    return mod


class RecordTests(unittest.TestCase):
    def test_record_and_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "approve", reviewer="critic", author="builder")
            v = mod.verdict_for(root, "US0017")
            self.assertIsNotNone(v)
            self.assertEqual(v["verdict"], "APPROVE")
            self.assertEqual(v["reviewer"], "critic")
            self.assertEqual(v["author"], "builder")  # both identities recorded on the verdict
            self.assertEqual(mod.verdict_for(root, "US9999"), None)

    def test_latest_wins_and_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "reject", author="builder", issues="bug")
            mod.record_verdict(root, "US0017", "approve", author="builder")
            self.assertEqual(len(mod.read_verdicts(root)), 2)        # append-only
            self.assertEqual(mod.verdict_for(root, "US0017")["verdict"], "APPROVE")  # latest

    def test_pipe_in_issues_does_not_break_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0017", "approve", author="builder", issues="a | b")
            self.assertEqual(len(mod.read_verdicts(root)), 1)


class CliTests(unittest.TestCase):
    def test_cli_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["record", "--unit", "US0017", "--verdict", "approve",
                           "--author", "builder", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.verdict_for(root, "US0017")["verdict"], "APPROVE")

    def test_cli_record_requires_author(self) -> None:
        # The authoring seat is mandatory: independence you cannot verify is none at all.
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            with self.assertRaises(SystemExit):
                mod.main(["record", "--unit", "US0017", "--verdict", "approve", "--root", d])

    def test_underscores_escaped_to_avoid_md037(self):
        # BG0023: underscored identifiers in the issues text must be escaped so they cannot
        # pair into markdown emphasis (markdownlint MD037).
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve", author="builder",
                               issues="fixed _read and _index_row and gate.run_gate")
            text = mod.verdicts_path(d).read_text(encoding="utf-8")
            self.assertNotIn(" _read", text)        # no bare underscore-led token
            self.assertIn(r"\_read", text)          # escaped instead
            self.assertTrue(any(v["unit"] == "US0001" for v in mod.read_verdicts(d)))


class IndependenceTests(unittest.TestCase):
    """CR0117: author != reviewer is a mechanical floor, proven, not an honour-system note."""

    def test_self_review_is_not_independent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve", reviewer="dani", author="dani")
            v = mod.verdict_for(d, "US0001")
            self.assertFalse(mod.is_independent(v))   # reviewer == author blocks

    def test_distinct_reviewer_is_independent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve", reviewer="qa-amir", author="dani")
            v = mod.verdict_for(d, "US0001")
            self.assertTrue(mod.is_independent(v))     # reviewer != author passes

    def test_missing_author_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve", reviewer="qa-amir")  # no author
            v = mod.verdict_for(d, "US0001")
            self.assertEqual(v["author"], "-")
            self.assertFalse(mod.is_independent(v))     # no recorded author -> not independent

    def test_pre_gate_is_grandfathered_not_independent(self) -> None:
        # A unit closed before the gate carries the visible PRE_GATE marker: it is
        # NOT real independence (is_independent stays truthful), but is_pre_gate flags
        # it so the conformance gate can grandfather it.
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve",
                               reviewer="self-review (light, docs)", author=mod.PRE_GATE)
            v = mod.verdict_for(d, "US0001")
            self.assertFalse(mod.is_independent(v))      # pre-gate is not real independence
            self.assertTrue(mod.is_pre_gate(v))          # but it is grandfathered
            self.assertFalse(mod.is_pre_gate(             # a real id is never pre-gate
                {"author": "dani", "reviewer": "qa-amir"}))

    def test_self_review_blocks_done_gate_distinct_passes(self) -> None:
        # The gate uses critic, so prove the wiring end to end via conformance.
        import importlib.util as _ilu
        cpath = SCRIPT.parent / "conformance.py"
        spec = _ilu.spec_from_file_location("conformance", cpath)
        conf = _ilu.module_from_spec(spec)
        sys.modules["conformance"] = conf
        spec.loader.exec_module(conf)
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            mod.record_verdict(d, "US0001", "approve", reviewer="dani", author="dani")
            self.assertFalse(conf.critic.is_independent(mod.verdict_for(d, "US0001")))
            mod.record_verdict(d, "US0001", "approve", reviewer="qa-amir", author="dani")
            self.assertTrue(conf.critic.is_independent(mod.verdict_for(d, "US0001")))

    def test_self_review_keeps_critiqued_in_missing_at_done_gate(self) -> None:
        # End-to-end: a Done story whose only APPROVE is a self-review (reviewer==author)
        # must leave `critiqued` unmet in the conformance gate's `missing` list - the
        # helper-level check is not enough; prove the gate itself blocks it. Swapping the
        # reviewer to a distinct id then clears `critiqued`.
        import importlib.util as _ilu
        cpath = SCRIPT.parent / "conformance.py"
        spec = _ilu.spec_from_file_location("conformance", cpath)
        conf = _ilu.module_from_spec(spec)
        sys.modules["conformance"] = conf
        spec.loader.exec_module(conf)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True, exist_ok=True)
            (stories / "US0001-sample.md").write_text("\n".join([
                "# US0001: sample", "", "> **Status:** Done",
                "> **Epic:** [EP0001: x](../epics/EP0001-x.md)", "",
                "## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing",
                "- **Verify:** shell echo ok", "- **Verified:** yes (2026-01-01)",
            ]) + "\n", encoding="utf-8")

            def critiqued_state():
                units = {u["id"]: u for u in conf.detect_conformance(root)["units"]}
                return units["US0001"]

            # Self-review APPROVE (reviewer == author): the gate must keep `critiqued` unmet.
            mod.record_verdict(root, "US0001", "approve", reviewer="dani", author="dani")
            u = critiqued_state()
            self.assertIn("critiqued", u["missing"])
            self.assertFalse(u["stages"]["critiqued"])
            # A later verdict from a distinct reviewer clears it (latest row wins).
            mod.record_verdict(root, "US0001", "approve", reviewer="qa-amir", author="dani")
            u = critiqued_state()
            self.assertNotIn("critiqued", u["missing"])
            self.assertTrue(u["stages"]["critiqued"])

    def test_legacy_five_column_row_reads_with_empty_author(self) -> None:
        # Rows that pre-date the gate (5 columns, no Author) still parse; their author is
        # empty, so they are correctly treated as not-yet-independent.
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            path = mod.verdicts_path(d)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Critic Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Date | Issues |\n| --- | --- | --- | --- | --- |\n"
                "| US0001 | APPROVE | critic | 2026-01-01 | - |\n",
                encoding="utf-8")
            v = mod.verdict_for(d, "US0001")
            self.assertEqual(v["verdict"], "APPROVE")
            self.assertEqual(v["author"], "")
            self.assertFalse(mod.is_independent(v))


if __name__ == "__main__":
    unittest.main()


class SeatDriftWarningTests(unittest.TestCase):
    """The persona lens must not drift out silently: recording a verdict under
    a reviewer that matches no declared seat/amigo draws a warning naming the
    declared options - advisory only, and silent where no personas exist."""

    def _repo(self, d, with_amigo=True):
        root = Path(d)
        (root / "sdlc-studio").mkdir(parents=True)
        if with_amigo:
            ad = root / "sdlc-studio" / "personas" / "amigos"
            ad.mkdir(parents=True)
            (ad / "qa.md").write_text(
                "<!-- role: qa -->\n# Sam Eriksson - QA amigo\n", encoding="utf-8")
        return root

    def _record(self, root, reviewer):
        import contextlib, io
        critic = _load()
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = critic.main(["record", "--unit", "CR0001", "--verdict", "approve",
                              "--reviewer", reviewer, "--author", "builder",
                              "--root", str(root)])
        return rc, err.getvalue()

    def test_unknown_reviewer_warns_and_names_seats(self):
        with tempfile.TemporaryDirectory() as d:
            rc, err = self._record(self._repo(d), "adversarial-critic (instance)")
            self.assertEqual(rc, 0)                       # advisory: never refuses
            self.assertIn("no declared seat", err)
            self.assertIn("qa", err)                       # declared role named

    def test_role_match_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            rc, err = self._record(self._repo(d), "Sam Eriksson (QA seat, review render)")
            self.assertEqual(rc, 0)
            self.assertNotIn("no declared seat", err)

    def test_no_personas_dir_is_silent(self):
        with tempfile.TemporaryDirectory() as d:
            rc, err = self._record(self._repo(d, with_amigo=False), "anyone")
            self.assertEqual(rc, 0)
            self.assertNotIn("no declared seat", err)
