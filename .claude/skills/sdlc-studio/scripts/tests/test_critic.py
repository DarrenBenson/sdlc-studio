"""Unit tests for critic.py - committed critic-verdict record (CR0023). RED first."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(SCRIPT.parent))
from lib.sdlc_md import norm_id as sdlc_md_norm  # noqa: E402


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

    def test_torn_row_surfaces_a_warning_not_silent_drop(self) -> None:
        # A crash mid-append can leave a truncated row in the append-only log. Such a
        # row must be REPORTED, not silently swallowed - a dropped verdict a gate then
        # reads as "no verdict" is a false signal. The well-formed rows still parse.
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            path = mod.verdicts_path(d)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Critic Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Issues |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| US0001 | APPROVE | critic | builder | 2026-01-01 | - |\n"
                "| US0002 | APPROVE | critic |\n"  # torn: interrupted mid-write, 3 cells
                "| US0003 | APPROVE | critic | builder | 2026-01-02 | - |\n",
                encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rows = mod.read_verdicts(d)
            self.assertIn("US0002", err.getvalue())  # the torn row is named, not silent
            self.assertRegex(err.getvalue(), r"(?i)malformed")
            units = [r["unit"] for r in rows]
            self.assertIn("US0001", units)  # well-formed rows still parse
            self.assertIn("US0003", units)


class CliTests(unittest.TestCase):
    def test_cli_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["record", "--brief", "abcdef123456",
                           "--unit", "US0017", "--verdict", "approve",
                           "--author", "builder", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.verdict_for(root, "US0017")["verdict"], "APPROVE")

    def test_cli_record_requires_author(self) -> None:
        # The authoring seat is mandatory: independence you cannot verify is none at all.
        # Asserted as the PROPERTY - refused, named, nothing written - rather than as the
        # SystemExit argparse used to raise. US0557 moved the check off argparse so one
        # refusal can name every missing argument at once; a test pinned to the mechanism
        # would have called that regression.
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                    contextlib.suppress(SystemExit):
                rc = mod.main(["record", "--brief", "abcdef123456",
                               "--unit", "US0017", "--verdict", "approve", "--root", d])
                self.assertNotEqual(rc, 0)
            self.assertIn("--author", out.getvalue() + err.getvalue())
            self.assertIsNone(mod.verdict_for(Path(d), "US0017"),
                              "a refused record must write nothing")

    def test_cli_SprintReview_records_and_covers(self) -> None:
        # US0247: the sprint-review CLI records a batch verdict readable as coverage per unit.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["sprint-review", "--units", "US0017,US0018", "--reviewer", "qa-seat",
                           "--author", "builder", "--verdict", "APPROVE",
                           "--findings", "full-diff pass", "--root", str(root)])
            self.assertEqual(rc, 0)
            rev = mod.sprint_review_for(root, "US0018")
            self.assertIsNotNone(rev)
            self.assertTrue(mod.sprint_covers_independently(root, "US0018", rev))

    def test_cli_SprintReview_refuses_self_review(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            rc = mod.main(["sprint-review", "--units", "US0017", "--reviewer", "bob",
                           "--author", "bob", "--verdict", "APPROVE", "--findings", "x",
                           "--root", d])
            self.assertNotEqual(rc, 0)

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
            rc = critic.main(["record", "--brief", "abcdef123456",
                              "--unit", "CR0001", "--verdict", "approve",
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

    def test_substring_inside_a_word_does_not_count(self):
        # Sam's attack: 'production' contains 'product'; a role match must be
        # a whole word, or free-text drift slips back past the warning
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            ad = root / "sdlc-studio" / "personas" / "amigos"
            (ad / "product.md").write_text(
                "<!-- role: product -->\n# Lena Fischer - Product amigo\n",
                encoding="utf-8")
            rc, err = self._record(root, "final production check")
            self.assertEqual(rc, 0)
            self.assertIn("no declared seat", err)

    def test_first_name_token_claims_the_seat(self):
        # 'sam checked it' names the seat holder - that is a seat claim, not
        # drift; token-level name matching keeps it silent
        with tempfile.TemporaryDirectory() as d:
            rc, err = self._record(self._repo(d), "sam checked it")
            self.assertEqual(rc, 0)
            self.assertNotIn("no declared seat", err)


import contextlib  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402


def _workspace(root: Path) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / "US0001-x.md").write_text(
        "# US0001: the thing\n\n> **Status:** In Progress\n"
        "> **Affects:** src/a.py, src/b.py\n> **Points:** 3\n\n"
        "## Acceptance Criteria\n\n### AC1: works\n\n- **Given** x\n- **When** y\n"
        "- **Then** z\n- **Verify:** shell true\n", encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True, exist_ok=True)
    (seats / "qa.md").write_text("# Sam - QA seat\n\ncharter text\n", encoding="utf-8")


class BriefTests(unittest.TestCase):
    """US0189: critic brief assembles the seat-review prompt deterministically."""

    def test_brief_carries_charter_acs_scope_and_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root)
            mod = _load()
            text = mod.brief(root, "US0001", "qa")
            self.assertIn("personas/seats/qa.md", text)       # charter reference
            self.assertIn("### AC1: works", text)             # ACs verbatim
            self.assertIn("src/a.py", text)                   # Affects-derived scope
            self.assertIn("VERDICT: APPROVE or REJECT", text) # the return contract
            self.assertIn("did NOT author", text)

    def test_unknown_unit_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root)
            mod = _load()
            with self.assertRaises(ValueError):
                mod.brief(root, "US0999", "qa")

    def test_unknown_seat_refused_naming_available(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root)
            mod = _load()
            with self.assertRaises(ValueError) as ctx:
                mod.brief(root, "US0001", "wizard")
            self.assertIn("qa", str(ctx.exception))


class FromVerdictTests(unittest.TestCase):
    """US0189: record --from-verdict parses the returned block, refusing malformed input."""

    BLOCK = ("Some preamble prose from the seat.\n"
             "VERDICT: APPROVE\n"
             "ISSUES: [new] minor thing at a.py:3; [pre-existing] another note\n"
             "BLOCKING: none\n")

    def _record(self, root: Path, block: str) -> tuple[int, str]:
        mod = _load()
        f = root / "verdict.txt"
        f.write_text(block, encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = mod.main(["record", "--brief", "abcdef123456",
                           "--unit", "US0001", "--reviewer", "Sam seat",
                           "--author", "builder", "--from-verdict", str(f),
                           "--root", str(root)])
        return rc, err.getvalue()

    def test_block_parsed_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, self.BLOCK)
            self.assertEqual(rc, 0)
            mod = _load()
            v = mod.verdict_for(root, "US0001")
            self.assertEqual(v["verdict"], "APPROVE")
            self.assertIn("minor thing", v["issues"])

    def test_blocking_content_folded_into_issues(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, self.BLOCK.replace(
                "BLOCKING: none", "BLOCKING: [regression] the big one at b.py:9"))
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            # The fold now carries the finding's origin through with it, so the label and the
            # text are no longer adjacent - assert both survive rather than their old spelling.
            self.assertIn("BLOCKING:", v["issues"])
            self.assertIn("the big one", v["issues"])
            self.assertIn("[regression]", v["issues"],
                          "the folded BLOCKING finding lost its origin")

    def test_verdictless_block_refused_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, err = self._record(root, "just prose, no verdict token\n")
            self.assertNotEqual(rc, 0)
            self.assertIn("VERDICT", err)
            self.assertIsNone(_load().verdict_for(root, "US0001"))

    def test_unknown_verdict_value_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, err = self._record(root, "VERDICT: SMASHED-IT\nISSUES: none\n")
            self.assertNotEqual(rc, 0)
            self.assertIn("SMASHED-IT", err)

    def test_duplicate_verdict_lines_refused_never_first_wins(self) -> None:
        # "VERDICT: APPROVE ... VERDICT: REJECT" must refuse - an ambiguous block
        # resolved in the author's favour is a forged approval
        with tempfile.TemporaryDirectory() as d:
            rc, err = self._record(Path(d),
                                   "VERDICT: APPROVE\nISSUES: none\nVERDICT: REJECT\n")
            self.assertNotEqual(rc, 0)
            self.assertIn("2 VERDICT", err)

    def test_lowercase_block_parsed_not_silently_dropped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, "verdict: reject\nissues: [new] a real finding at a.py:3\n")
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            self.assertEqual(v["verdict"], "REJECT")
            self.assertIn("a real finding", v["issues"])

    def test_wrapped_issues_with_allcaps_word_not_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, "VERDICT: APPROVE\nISSUES: [new] first line;\n"
                                       "[new] NOTE: this continuation belongs to issues\n"
                                       "BLOCKING: none\n")
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            self.assertIn("NOTE: this continuation", v["issues"])

    def test_echoed_contract_above_real_block_cannot_leak_placeholders(self) -> None:
        block = ("The contract I was given said:\n"
                 "VERDICT: APPROVE or REJECT\n"
                 "ISSUES: <semicolon-separated findings>\n"
                 "BLOCKING: <the subset>\n\n"
                 "VERDICT: REJECT\nISSUES: [new] the actual finding\nBLOCKING: none\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, block)
            self.assertEqual(rc, 0)  # the echo's "APPROVE or REJECT" is not a verdict line
            v = _load().verdict_for(root, "US0001")
            self.assertEqual(v["verdict"], "REJECT")
            self.assertIn("the actual finding", v["issues"])
            self.assertNotIn("<semicolon", v["issues"])

    def test_stdin_dash_path(self) -> None:
        import unittest.mock
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            with contextlib.redirect_stdout(io.StringIO()), \
                    unittest.mock.patch.object(sys, "stdin", io.StringIO(self.BLOCK)):
                rc = mod.main(["record", "--brief", "abcdef123456",
                               "--unit", "US0001", "--reviewer", "Sam seat",
                               "--author", "builder", "--from-verdict", "-",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.verdict_for(root, "US0001")["verdict"], "APPROVE")

    def test_explicit_verdict_and_from_verdict_refused_together(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            f = root / "v.txt"
            f.write_text(self.BLOCK, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["record", "--brief", "abcdef123456",
                               "--unit", "US0001", "--reviewer", "r",
                               "--author", "a", "--verdict", "approve",
                               "--from-verdict", str(f), "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("mutually exclusive", err.getvalue())


class EvidenceTests(unittest.TestCase):
    """CR0323 / RFC0044 D1: the seat subagent's adversarial pass is recorded as
    EVIDENCE (findings, reviewer seat, author) in its own log, distinct from the
    verdict record - the finder's output is input to the sign-off, never the sign-off."""

    def test_record_and_lookup_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="two probes executed; none blocking")
            ev = mod.evidence_for(root, "US0001")
            self.assertIsNotNone(ev)
            self.assertEqual(ev["reviewer"], "qa-seat")
            self.assertEqual(ev["author"], "builder")
            self.assertIn("probes", ev["findings"])
            self.assertIsNone(mod.evidence_for(root, "US9999"))
            # distinct from the verdict log: recording evidence never mints a verdict
            self.assertIsNone(mod.verdict_for(root, "US0001"))
            self.assertNotEqual(mod.evidence_path(root), mod.verdicts_path(root))

    def test_evidence_refuses_empty_findings(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            with self.assertRaises(ValueError):
                mod.record_evidence(d, "US0001", reviewer="qa", author="b", findings="  ")

    def test_evidence_cli_from_verdict_block(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            f = root / "v.txt"
            f.write_text("VERDICT: REJECT\nISSUES: [regression] off-by-one at flow.py:10\nBLOCKING: the off-by-one\n",
                         encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["evidence", "--unit", "US0001", "--reviewer", "qa-seat",
                               "--author", "builder", "--from-verdict", str(f),
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            ev = mod.evidence_for(root, "US0001")
            self.assertIn("REJECT", ev["findings"])
            self.assertIn("off-by-one", ev["findings"])

    def test_evidence_cli_refuses_malformed_block(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            f = root / "v.txt"
            f.write_text("no contract here\n", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["evidence", "--unit", "US0001", "--reviewer", "qa",
                               "--author", "b", "--from-verdict", str(f), "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIsNone(mod.evidence_for(root, "US0001"))


class SignoffDelegateTests(unittest.TestCase):
    """CR0323 / RFC0044 D3: the reviewer-of-record sign-off. The principal must be
    one the author does not control: not the author, and not an authoring-session
    subagent (any reviewer id recorded on the unit's evidence/verdict rows)."""

    def test_direct_signoff_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_signoff(root, "US0001", principal="Darren Benson (operator)",
                               author="builder")
            so = mod.signoff_for(root, "US0001")
            self.assertIsNotNone(so)
            self.assertIn("operator", so["principal"])
            self.assertEqual(so["chain"], "-")

    def test_self_signoff_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            with self.assertRaises(ValueError):
                mod.record_signoff(d, "US0001", principal="builder", author="builder")

    def test_delegate_chain_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_signoff(root, "US0001", principal="Darren Benson (operator)",
                               author="builder", delegate="ci-reviewer",
                               boundary="CI job on main")
            so = mod.signoff_for(root, "US0001")
            self.assertEqual(so["principal"], "ci-reviewer")   # the delegate signs
            self.assertIn("->", so["chain"])                   # chain recorded
            self.assertIn("CI job", so["chain"])               # trust boundary named

    def test_delegate_requires_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            with self.assertRaises(ValueError):
                mod.record_signoff(d, "US0001", principal="operator", author="builder",
                                   delegate="ci-reviewer")

    def test_authoring_session_subagent_is_accepted_as_a_DISCLOSED_delegate(self) -> None:
        # AMENDED under D0059, deliberately. This asserted a REFUSAL - the seat subagent is the
        # author's own spawn, so naming it the delegate hollowed out the self-approval guard.
        # The operator ruled that such a delegate is fully authorised and the honest answer to
        # the residual risk is DISCLOSURE rather than prohibition: unattended delivery could
        # otherwise never reach Done. The sign-off is now accepted AND MARKED, and the marker
        # is what this test pins - an unmarked row is the one outcome the ruling cannot
        # tolerate. Independence is not restored by any of this and the docs say so.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="pass done")
            mod.record_signoff(root, "US0001", principal="operator", author="builder",
                               delegate="qa-seat", boundary="another session")
            row = mod.signoff_for(root, "US0001")
        self.assertIn(mod.DELEGATED_AGENT, row["chain"])

    def test_verdict_reviewer_is_accepted_as_a_DISCLOSED_delegate(self) -> None:
        # AMENDED under D0059 - see the sibling test above for the reasoning and the cost.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="Sam seat", author="builder")
            mod.record_signoff(root, "US0001", principal="operator", author="builder",
                               delegate="Sam seat", boundary="another session")
            row = mod.signoff_for(root, "US0001")
        self.assertIn(mod.DELEGATED_AGENT, row["chain"])

    def test_plan_review_reviewer_is_accepted_as_a_DISCLOSED_delegate(self) -> None:
        # AMENDED under D0059. The authoring-session set still spans BOTH verdict phases - a
        # subagent that only reviewed the unit's PLAN is still the author's spawn - so what
        # this now pins is that the marker is applied to that case too. If the phase were
        # dropped from the session set, this delegate would be recorded as an ordinary
        # independent sign-off, which is exactly the silent outcome the ruling forbids.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="plan-seat",
                               author="builder", phase="plan-review")
            mod.record_signoff(root, "US0001", principal="operator", author="builder",
                               delegate="plan-seat", boundary="another session")
            row = mod.signoff_for(root, "US0001")
        self.assertIn(mod.DELEGATED_AGENT, row["chain"])

    def test_direct_principal_in_session_refused(self) -> None:
        # The write-time refusal covers the DIRECT path too, not only delegates:
        # a principal who is a recorded session reviewer is the author's own spawn.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="pass done")
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")

    def test_SprintReview_reviewer_refused_as_principal(self) -> None:
        # The reviewer-of-record must differ from the adversarial reviewer at sprint scope too:
        # a principal equal to a covering sprint-level review's reviewer is refused.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_sprint_review(root, ["US0001"], reviewer="qa-seat", author="builder",
                                     verdict="APPROVE", findings="full-diff pass")
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")

    def test_author_refused_as_delegate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            with self.assertRaises(ValueError):
                mod.record_signoff(d, "US0001", principal="operator", author="builder",
                                   delegate="builder", boundary="another session")

    def test_cli_signoff_and_refusal_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["signoff", "--unit", "US0001",
                               "--principal", "Darren Benson (operator)",
                               "--author", "builder", "--root", str(root)])
            self.assertEqual(rc, 0)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["signoff", "--unit", "US0002", "--principal", "b",
                               "--author", "b", "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIsNone(mod.signoff_for(root, "US0002"))


class RejoinderTests(unittest.TestCase):
    """CR0329: the re-verdict loop's scaffolding emitted deterministically - the
    prior verdict quoted verbatim, the refreshed scope, the same return contract."""

    PRIOR = ("VERDICT: REJECT\n"
             "ISSUES: [new] vacuous killing test at test_x.py:10; [new] docstring overclaims\n"
             "BLOCKING: the vacuous killing test\n")

    def _workspace(self, root: Path) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True)
        (d / "US0101-widget.md").write_text(
            "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
            "> **Affects:** widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
            "- **Verify:** shell echo ok\n", encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "qa.md").write_text("# Sam Eriksson - QA seat\n<!-- role: qa -->\n",
                                     encoding="utf-8")

    def test_rejoinder_quotes_prior_verdict_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            text = mod.rejoinder_brief(root, "US0101", "qa", self.PRIOR)
            self.assertIn("VERDICT: REJECT", text)                        # quoted
            self.assertIn("vacuous killing test at test_x.py:10", text)   # verbatim issues
            self.assertIn("BLOCKING: the vacuous killing test", text)
            self.assertIn("widget.py", text)                              # refreshed scope
            self.assertIn("VERDICT: APPROVE or REJECT", text)             # same contract

    def test_malformed_prior_verdict_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            with self.assertRaises(ValueError):
                mod.rejoinder_brief(root, "US0101", "qa", "no contract here")

    def test_cli_rejoinder_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            f = root / "prior.txt"
            f.write_text(self.PRIOR, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["brief", "--unit", "US0101", "--seat", "qa",
                               "--rejoinder", str(f), "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("VERDICT: REJECT", out.getvalue())
            bad = root / "bad.txt"
            bad.write_text("nothing here", encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["brief", "--unit", "US0101", "--seat", "qa",
                               "--rejoinder", str(bad), "--root", str(root)])
            self.assertEqual(rc, 2)


class RejoinderProbeTests(unittest.TestCase):
    """CR0329: the re-run-your-mutants demand is structural - the lesson from the
    two vacuous killing tests, in the ceremony, not just the lore."""

    def test_rejoinder_demands_reexecuting_the_named_probes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            RejoinderTests._workspace(RejoinderTests(), root)
            mod = _load()
            text = mod.rejoinder_brief(root, "US0101", "qa", RejoinderTests.PRIOR)
            low = text.lower()
            self.assertIn("re-execute", low)
            self.assertIn("mutant", low)
            # the demand binds BEFORE approval and forbids trusting the summary -
            # asserted on the rejoinder's own phrasing, not the base brief's contract
            self.assertIn("before you may approve", low)
            self.assertIn("a claim,\nnot evidence", low.replace("\r", ""))
            # the contract appears TWICE: the base brief's copy AND the rejoinder tail
            # (dropping the tail restatement must fail here)
            self.assertEqual(text.count("VERDICT: APPROVE or REJECT"), 2)


class SignoffBriefTests(unittest.TestCase):
    """CR0323 AC3 / CR0318: the sign-off request embeds the decision brief -
    deliveries, per-unit verdict + REJECT history, gate/cost evidence, and the
    approve/hold/delegate paths. Absent evidence is named absent, never invented."""

    def _workspace(self, root: Path) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True)
        (d / "US0101-widget.md").write_text(
            "# US0101: widget frobnicates\n\n> **Status:** Review\n> **Points:** 5\n"
            "> **Epic:** EP0001\n\n## Acceptance Criteria\n\n### AC1: works\n"
            "- **Verify:** shell echo ok\n", encoding="utf-8")

    def test_brief_carries_deliveries_history_and_paths(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            mod.record_verdict(root, "US0101", "reject", reviewer="qa-seat",
                               author="builder", issues="vacuous killing test")
            mod.record_verdict(root, "US0101", "approve", reviewer="qa-seat", author="builder")
            mod.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                                findings="mutants re-run; kill confirmed")
            text = mod.signoff_brief(root, ["US0101"], gate_note="gate: PASS",
                                     cost_note="forecast 125k / measured 110k")
            self.assertIn("US0101", text)
            self.assertIn("widget frobnicates", text)      # delivery title
            self.assertIn("5", text)                       # points
            self.assertIn("REJECT", text)                  # reject history quoted
            self.assertIn("vacuous killing test", text)
            self.assertIn("gate: PASS", text)              # gate evidence inline
            self.assertIn("125k", text)                    # cost evidence inline
            for path in ("approve", "hold", "delegate"):
                self.assertIn(path, text.lower())

    def test_brief_names_absent_evidence_never_invents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            text = mod.signoff_brief(root, ["US0101"])
            self.assertIn("no critic verdict recorded", text.lower())
            self.assertIn("no adversarial evidence recorded", text.lower())
            self.assertIn("not provided", text.lower())    # gate/cost notes absent, named

    def test_brief_refuses_unknown_unit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            with self.assertRaises(ValueError):
                mod.signoff_brief(root, ["US9999"])

    def test_SprintReviewBrief_reads_coverage_not_unreviewed(self) -> None:
        # US0248: a unit with no per-unit verdict but covered by a sprint-level review reads as
        # reviewed by that pass, never as "(no critic verdict recorded)".
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._workspace(root)
            mod = _load()
            mod.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                     verdict="APPROVE", findings="full-diff pass; none blocking")
            text = mod.signoff_brief(root, ["US0101"])
            self.assertIn("sprint-level review", text.lower())
            self.assertIn("qa-seat", text)
            self.assertNotIn("no critic verdict recorded", text.lower())
            self.assertNotIn("no adversarial evidence recorded", text.lower())


def _run_state():
    """The run_state module, loaded the same way critic.py reaches it."""
    import importlib
    sys.path.insert(0, str(SCRIPT.parent))
    try:
        return importlib.import_module("lib.run_state")
    finally:
        sys.path.pop(0)


class ReviewRoundCountTests(unittest.TestCase):
    """US0261 - the close review counts its rounds and stops at a ceiling."""

    def _open(self, root):
        rs = _run_state()
        rs.open_run(root, batch=["US0001"], goal="done")
        return rs

    def test_recording_a_verdict_increments_the_run_review_round(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = _load(), self._open(root)
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="reject", findings="something")
            self.assertEqual(rs.review_round_count(root), 1)
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="approve", findings="repaired")
            self.assertEqual(rs.review_round_count(root), 2)

    def test_round_past_the_ceiling_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = _load(), self._open(root)
            for _ in range(3):
                mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                         verdict="reject", findings="f")
            with self.assertRaises(ValueError) as ctx:
                mod.review_round_guard(root, ceiling=3)
            msg = str(ctx.exception)
            self.assertIn("3", msg)            # the count and the ceiling are both named
            self.assertIn("override", msg.lower())

    def test_ceiling_resolves_from_config_with_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            self.assertEqual(mod.review_ceiling(root), mod.DEFAULT_REVIEW_CEILING)
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.parent.mkdir(parents=True, exist_ok=True)
            cfg.write_text("review:\n  max_rounds: 7\n", encoding="utf-8")
            try:
                import yaml  # noqa: F401
            except ImportError:
                self.skipTest("PyYAML absent - the override path cannot be exercised")
            self.assertEqual(mod.review_ceiling(root), 7)

    def test_the_shipped_ceiling_default_is_three(self) -> None:
        """The literal 3, pinned by value rather than through its own symbol.

        Comparing `review_ceiling` to `DEFAULT_REVIEW_CEILING` is true for any value the
        constant takes, so it pins the wiring and not the number US0261 shipped.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            self.assertEqual(mod.DEFAULT_REVIEW_CEILING, 3)
            self.assertEqual(mod.review_ceiling(root), 3)   # no config present

    def test_the_default_ceiling_refuses_the_fourth_round_not_the_third(self) -> None:
        """The numeric boundary, driven through the guard with no explicit ceiling.

        Two-sided: with two rounds recorded the guard returns rather than raises, and with
        three it raises. A larger default would permit a fourth round; a smaller one would
        refuse the third.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = _load(), self._open(root)
            for _ in range(2):
                mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                         verdict="reject", findings="f")
            self.assertEqual(mod.review_round_guard(root), 2)   # still under the ceiling
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="reject", findings="f")
            with self.assertRaises(ValueError):
                mod.review_round_guard(root)
            self.assertEqual(rs.review_round_count(root), 3)

    def test_ceiling_override_is_explicit_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = _load(), self._open(root)
            for _ in range(3):
                mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                         verdict="reject", findings="f")
            mod.review_round_guard(root, ceiling=3, override=True)
            state = rs.read(root)
            self.assertEqual(state["review_ceiling_overrides"], [{"at_round": 3, "ceiling": 3}])

    def test_verdict_without_an_open_run_reports_rather_than_counts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = _load(), _run_state()
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="approve", findings="f")
            # the review itself is still recorded - the evidence is never dropped
            self.assertEqual(len(mod.sprint_reviews(root)), 1)
            # but nothing is counted against a run that does not exist
            self.assertIsNone(rs.read(root).get("run_id"))
            self.assertEqual(rs.review_round_count(root), 0)

    def test_rounds_without_a_run_id_are_not_counted(self) -> None:
        """The guard's own mechanism, reached directly.

        `record_review_round` already refuses with no run open, so through the public path
        this state never arises and a test driving it proves nothing. A hand-edited or
        partially-written run-state file DOES produce it, and rounds that belong to no run
        must not be counted as the current run's - they cannot be attributed to it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rs = _run_state()
            rs.write(root, {"schema": 1, "run_id": None, "outcome": "running",
                            "review_rounds": [{"round": 1, "verdict": "REJECT"},
                                              {"round": 2, "verdict": "APPROVE"}]})
            self.assertEqual(len(rs.review_rounds(root)), 2)   # they are readable
            self.assertEqual(rs.review_round_count(root), 0)   # but attributed to no run


class ReadRowsHeaderTests(unittest.TestCase):
    """BG0227 - the header skip is derived from the declared column names, not one table's
    first-column literal, so a table led by any other column does not return its own header."""

    def test_sprint_review_table_does_not_return_its_header_as_data(self) -> None:
        """One recorded sprint review reads back as exactly one row.

        The sprint-review table is led by `Base`, not `Unit`. A first-column literal skip
        knows only `Unit`, so it returned the `| Base | Reviewer | ... |` header as a data
        row with every cell set to its own column name.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="approve", findings="f")
            rows = mod.sprint_reviews(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["base"], "-")
            self.assertEqual(rows[0]["reviewer"], "seat")
            # the shape the defect produced: every cell equal to its own column name
            self.assertNotIn({"base": "Base", "reviewer": "Reviewer", "author": "Author",
                              "verdict": "Verdict", "date": "Date", "units": "Units",
                              "findings": "Findings"}, rows)

    def test_header_skip_generalises_to_a_table_with_unrelated_columns(self) -> None:
        """A table whose columns share no name with any shipped table still loses its header.

        This is the claim the docstring on `_read_rows` makes - that the skip cannot lapse
        when the next table is added - reached directly rather than through a caller, because
        no shipped caller uses these column names.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            path = root / "novel-table.md"
            path.write_text("# Novel\n\n"
                            "| Alpha | Beta |\n"
                            "| --- | --- |\n"
                            "| a1 | b1 |\n"
                            "| a2 | b2 |\n", encoding="utf-8")
            rows = mod._read_rows(path, ("alpha", "beta"))
            self.assertEqual(rows, [{"alpha": "a1", "beta": "b1"},
                                    {"alpha": "a2", "beta": "b2"}])

    def test_a_data_row_that_looks_like_a_header_only_in_its_first_cell_is_kept(self) -> None:
        """`Unit` as a first cell is data unless the WHOLE row is the column names.

        The old literal skip dropped any row whose first cell read `Unit`; the column-name
        match drops only the header itself.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            path = root / "look-alike.md"
            path.write_text("| Unit | Reviewer |\n"
                            "| --- | --- |\n"
                            "| Unit | someone |\n", encoding="utf-8")
            self.assertEqual(mod._read_rows(path, ("unit", "reviewer")),
                             [{"unit": "Unit", "reviewer": "someone"}])


class RepairRegressionTests(unittest.TestCase):
    """US0262 - a finding in code the previous round's repair touched is named as such."""

    def _run_with_round(self, root, repaired):
        rs = _run_state()
        rs.open_run(root, batch=["US0001"], goal="done")
        mod = _load()
        mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                 verdict="reject", findings="r1", repaired=repaired)
        return mod

    def test_round_records_its_repaired_file_set(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._run_with_round(root, [{"file": "critic.py", "lines": [[10, 20]]}])
            rounds = _run_state().review_rounds(root)
            self.assertEqual(rounds[0]["repaired"], [{"file": "critic.py", "lines": [[10, 20]]}])

    def test_finding_in_prior_repair_surface_is_a_repair_regression(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._run_with_round(root, [{"file": "critic.py", "lines": [[10, 20]]}])
            got = mod.classify_finding(root, file="critic.py", line=15)
            self.assertEqual(got["class"], mod.REPAIR_REGRESSION)
            self.assertEqual(got["round"], 1)

    def test_finding_outside_prior_repair_surface_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._run_with_round(root, [{"file": "critic.py", "lines": [[10, 20]]}])
            self.assertEqual(mod.classify_finding(root, file="sprint.py", line=15)["class"],
                             mod.FRESH)

    def test_same_file_outside_repaired_lines_is_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._run_with_round(root, [{"file": "critic.py", "lines": [[10, 20]]}])
            # same file, well outside the repaired span - a file-level match would call this a
            # regression and, on files of this size, would call almost everything one
            self.assertEqual(mod.classify_finding(root, file="critic.py", line=800)["class"],
                             mod.FRESH)

    def test_first_round_findings_are_always_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rs = _run_state()
            rs.open_run(root, batch=["US0001"], goal="done")
            mod = _load()
            # no round recorded yet: there is no prior repair surface to regress against
            self.assertEqual(mod.classify_finding(root, file="critic.py", line=15)["class"],
                             mod.FRESH)

    def test_unlocatable_finding_is_unclassified_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._run_with_round(root, [{"file": "critic.py", "lines": [[10, 20]]}])
            for bad in ({"file": None, "line": 15}, {"file": "critic.py", "line": None}):
                got = mod.classify_finding(root, **bad)
                self.assertEqual(got["class"], mod.UNCLASSIFIED, bad)
                self.assertTrue(got["reason"].strip(), "an unclassified finding must say why")

    def test_only_the_latest_round_is_the_comparison_surface(self) -> None:
        """Round 3 regresses against round 2's repair, not round 1's.

        Round 1's surface has already been re-reviewed by round 2; a finding there now is a
        fresh miss by round 2, not a regression round 2's repair created."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._run_with_round(root, [{"file": "old.py", "lines": [[1, 5]]}])
            mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                     verdict="reject", findings="r2",
                                     repaired=[{"file": "new.py", "lines": [[1, 5]]}])
            self.assertEqual(mod.classify_finding(root, file="new.py", line=3)["class"],
                             mod.REPAIR_REGRESSION)
            self.assertEqual(mod.classify_finding(root, file="old.py", line=3)["class"],
                             mod.FRESH)


class EscalationTests(unittest.TestCase):
    """US0263 - a repair regression escalates instead of buying another patch round."""

    def _regressed(self, root):
        rs = _run_state()
        rs.open_run(root, batch=["US0001"], goal="done")
        mod = _load()
        mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                 verdict="reject", findings="r1",
                                 repaired=[{"file": "critic.py", "lines": [[10, 20]]}])
        return mod, mod.classify_finding(root, file="critic.py", line=15)

    def test_repair_regression_presents_the_three_options(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, finding = self._regressed(root)
            esc = mod.escalation_for(root, finding)
            labels = [o["label"] for o in esc["options"]]
            self.assertEqual(sorted(labels), ["accept-and-file", "redesign", "revert"])
            for o in esc["options"]:
                self.assertTrue(o["consequence"].strip(), f"{o['label']} has no consequence")
            # another patch round is NOT among the offered options
            self.assertNotIn("patch", " ".join(labels).lower())

    def test_revert_option_names_its_scope(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, finding = self._regressed(root)
            revert = next(o for o in mod.escalation_for(root, finding)["options"]
                          if o["label"] == "revert")
            self.assertIn("critic.py", revert["consequence"])
            self.assertIn("1", revert["consequence"])   # the round it would revert

    def test_escalation_choice_is_recorded_against_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, finding = self._regressed(root)
            mod.record_escalation(root, "redesign", finding)
            rec = _run_state().read(root)["escalations"]
            self.assertEqual(len(rec), 1)
            self.assertEqual(rec[0]["choice"], "redesign")
            self.assertEqual(rec[0]["round"], 1)          # the regression that triggered it
            self.assertIn("critic.py", rec[0]["finding"]["file"])

    def test_accept_and_file_mints_a_linked_artefact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            # the filer refuses an `Affects` that does not resolve, and it is right to:
            # a path the parser cannot find counts as no Affects at all
            affected = root / "scripts" / "critic.py"
            affected.parent.mkdir(parents=True, exist_ok=True)
            affected.write_text("# fixture\n", encoding="utf-8")
            mod, finding = self._regressed(root)
            out = mod.record_escalation(root, "accept-and-file", finding,
                                        title="the regressed guard is unpinned",
                                        summary="round 1's repair left the branch unpinned",
                                        severity="Medium", steps="see the round-1 finding",
                                        fix="pin the branch",
                                        affects="scripts/critic.py",
                                        points=2)
            self.assertTrue(out["filed"], "accept-and-file must report the id it filed")
            self.assertRegex(out["filed"], r"^BG\d{4}$")
            self.assertTrue((root / "sdlc-studio" / "bugs").glob(f"{out['filed']}*"))

    def test_an_unknown_choice_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, finding = self._regressed(root)
            with self.assertRaises(ValueError):
                mod.record_escalation(root, "just-patch-it-again", finding)

    def test_autonomous_regression_blocks_rather_than_chooses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, finding = self._regressed(root)
            mod.defer_escalation(root, unit="US0001", finding=finding)
            pending = _run_state().read(root)["pending_decisions"]
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0]["unit"], "US0001")
            self.assertIsNone(pending[0]["resolution"], "nothing may be chosen for the operator")
            labels = [o["label"] for o in pending[0]["options"]]
            self.assertEqual(sorted(labels), ["accept-and-file", "redesign", "revert"])

    def test_a_fresh_finding_does_not_escalate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, _ = self._regressed(root)
            fresh = mod.classify_finding(root, file="sprint.py", line=15)
            with self.assertRaises(ValueError):
                mod.escalation_for(root, fresh)


class RoundCostTests(unittest.TestCase):
    """US0264 - what the rounds have cost, shown when the next one is offered."""

    def _run(self, root):
        rs = _run_state()
        rs.open_run(root, batch=["US0001"], goal="done")
        return _load(), rs

    def _review(self, mod, root, **kw):
        mod.record_sprint_review(root, ["US0001"], reviewer="seat", author="builder",
                                 verdict="reject", findings="f", **kw)

    def test_round_records_its_token_cost(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = self._run(root)
            self._review(mod, root, tokens=80_000)
            self.assertEqual(rs.review_rounds(root)[0]["tokens"], 80_000)

    def test_next_round_offer_shows_cumulative_cost(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, _ = self._run(root)
            self._review(mod, root, tokens=80_000)
            self._review(mod, root, tokens=60_000)
            text = mod.round_cost_report(root)
            self.assertIn("80,000", text)
            self.assertIn("60,000", text)
            self.assertIn("140,000", text)   # the cumulative total, not just the parts

    def test_unmeasured_round_is_named_not_zeroed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, _ = self._run(root)
            self._review(mod, root, tokens=80_000)
            self._review(mod, root)                       # unmeasured
            text = mod.round_cost_report(root)
            self.assertRegex(text, r"(?i)unmeasured")
            self.assertRegex(text, r"(?i)partial")        # the total is marked incomplete
            self.assertIn("80,000", text)
            # the unmeasured round must not be summed as zero and the total then presented as
            # whole: the TOTAL LINE itself has to carry the partial marker, not just the body
            total_line = next(l for l in text.splitlines() if "total" in l.lower())
            self.assertIn("PARTIAL", total_line)
            self.assertIn("1 of 2", total_line, "the total must say how many rounds it covers")

    def test_a_measured_zero_is_not_unmeasured(self) -> None:
        """0 and 'not measured' are different facts and must read differently.

        This is the BG0224 shape one level up: a falsy test cannot tell them apart, and
        showing a measured zero as 'unmeasured' would understate confidence rather than cost.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, rs = self._run(root)
            self._review(mod, root, tokens=0)
            self.assertEqual(rs.review_rounds(root)[0]["tokens"], 0)
            text = mod.round_cost_report(root)
            self.assertNotRegex(text, r"(?i)unmeasured")
            self.assertNotRegex(text, r"(?i)partial")

    def test_the_offer_carries_the_cost_and_the_count(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod, _ = self._run(root)
            self._review(mod, root, tokens=80_000)
            offer = mod.next_round_offer(root)
            self.assertIn("80,000", offer)
            self.assertIn("1", offer)                     # rounds so far
            self.assertIn(str(mod.DEFAULT_REVIEW_CEILING), offer)

    def test_no_rounds_reports_no_cost_rather_than_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._run(root)
            mod = _load()
            self.assertRegex(mod.round_cost_report(root), r"(?i)no .*round")


_PRIOR = """VERDICT: REJECT
ISSUES: MAJOR - the sibling sweep is blind to its own directory. I ran
`pytest tests/test_repo_hygiene.py -k sibling` and mutated the guard at
scripts/readiness.py:88; the killing test did not fail.
Also MINOR - the docstring overstates what the second clause pins.
BLOCKING: yes
"""


class NeutralBriefTests(unittest.TestCase):
    """US0265 - the brief carries the work, not the framing that predicts a conclusion."""

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: x\n\n> **Status:** Ready\n> **Affects:** a.py\n", encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True, exist_ok=True)
        (seats / "qa-seat.md").write_text(
            "<!-- role: qa -->\n# QA seat\n\n## Lens\n\nAssertion integrity.\n",
            encoding="utf-8")
        return root

    def test_neutral_brief_carries_diff_and_risk_surface(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod = _load()
            text = mod.neutral_brief(root, "US0001", "qa-seat")
            self.assertIn("US0001", text)
            self.assertTrue(len(text.strip()) > 100, "a brief must carry the work to be done")

    def test_brief_omits_verdict_round_and_expected_conclusion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod = _load()
            text = mod.neutral_brief(root, "US0001", "qa-seat", prior=_PRIOR, round_number=4)
            # the return contract necessarily names both verdict words and BLOCKING - that is
            # the reply format, not priming - so the property is checked with it excluded
            self.assertEqual(mod.neutrality_violations(text), [])
            body = text.replace(mod._RETURN_CONTRACT, "")
            for banned in ("REJECT", "MAJOR", "MINOR", "BLOCKING"):
                self.assertNotIn(banned, body, f"{banned} leaked outside the return contract")
            self.assertNotRegex(body, r"(?i)round\s*4")
            self.assertNotRegex(body, r"(?i)the pattern will continue|you will find|expect to find")

    def test_probe_list_travels_without_its_framing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod = _load()
            text = mod.neutral_brief(root, "US0001", "qa-seat", prior=_PRIOR)
            # the factual re-execution demand survives...
            self.assertIn("tests/test_repo_hygiene.py", text)
            self.assertIn("scripts/readiness.py:88", text)
            # ...as a DEMAND, not a bare list of paths: probes with no instruction to re-run
            # them are decoration, and the re-execution is the half worth keeping
            self.assertRegex(text, r"(?i)re-execute")
            self.assertRegex(text, r"(?i)killing test fails")
            # ...stripped of the verdict prose that surrounded it
            self.assertNotIn("blind to its own directory", text)

    def test_unparseable_probe_list_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod = _load()
            with self.assertRaises(ValueError) as ctx:
                mod.neutral_brief(root, "US0001", "qa-seat",
                                  prior="VERDICT: REJECT\nISSUES: it felt wrong\nBLOCKING: yes\n")
            self.assertRegex(str(ctx.exception), r"(?i)probe")

    def test_neutral_text_reports_no_violations(self) -> None:
        mod = _load()
        clean = "Review the diff for US0001. Return the contract below."
        self.assertEqual(mod.neutrality_violations(clean), [])

    # BG0235 - one case per priming class, each carrying ONLY that class, asserting the exact
    # violation list. A single test tripping all four at once and asserting truthiness stays
    # green when any one class regexp is neutered; these fail one test per broken class.

    def test_a_verdict_word_alone_is_flagged(self) -> None:
        mod = _load()
        self.assertEqual(mod.neutrality_violations("The prior outcome was REJECT."),
                         ["a prior verdict word"])
        self.assertEqual(mod.neutrality_violations("The prior outcome was APPROVE."),
                         ["a prior verdict word"])

    def test_a_severity_label_alone_is_flagged(self) -> None:
        mod = _load()
        for label in ("MAJOR", "MINOR", "BLOCKING"):
            self.assertEqual(mod.neutrality_violations(f"The finding was a {label} one."),
                             ["a severity label that pre-grades the finding"], label)

    def test_a_round_number_alone_is_flagged(self) -> None:
        mod = _load()
        self.assertEqual(mod.neutrality_violations("This is round 3 of the pass."),
                         ["a round number"])

    def test_an_asserted_conclusion_alone_is_flagged(self) -> None:
        mod = _load()
        for phrase in ("the pattern will continue", "you will find the same shape",
                       "expect to find the same shape", "as in the previous round"):
            self.assertEqual(mod.neutrality_violations(f"Note that {phrase}."),
                             ["an asserted conclusion"], phrase)

    def test_a_brief_with_no_prior_is_still_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            mod = _load()
            self.assertEqual(mod.neutrality_violations(
                mod.neutral_brief(root, "US0001", "qa-seat")), [])





class RepairProvenanceTests(unittest.TestCase):
    """US0314: a repair records which plan it executed."""

    def _critic(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "critic", Path(__file__).resolve().parent.parent / "critic.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["critic"] = m
        spec.loader.exec_module(m)
        return m

    def test_a_recorded_repair_carries_the_plan_it_executed(self) -> None:
        c = self._critic()
        issues = c.repair_provenance("RP0007")
        self.assertEqual(c.repair_plan_of(issues), "RP0007")
        self.assertTrue(c.is_planned_repair(issues))

    def test_an_unplanned_repair_is_recorded_as_unplanned_not_blank(self) -> None:
        c = self._critic()
        token = c.repair_provenance(None)
        # explicit, never the empty string - an absent field reads as missing data and
        # cannot be told from a planned repair whose id was dropped.
        self.assertNotEqual(token, "")
        self.assertEqual(token, c.REPAIR_UNPLANNED)
        self.assertIsNone(c.repair_plan_of(token))
        self.assertFalse(c.is_planned_repair(token))
        # and a verdict with NO provenance token at all is also not a planned repair
        self.assertFalse(c.is_planned_repair("ac-hash=deadbeef"))


class ReviewPolicyTests(unittest.TestCase):
    """US0332: a project declares a review policy: block-on-REJECT or carry-forward."""

    def _cf(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "carry_forward", Path(__file__).resolve().parent.parent / "carry_forward.py")
        m = importlib.util.module_from_spec(spec); sys.modules["carry_forward"] = m
        spec.loader.exec_module(m); return m

    def _root(self, policy=None):
        d = Path(tempfile.mkdtemp(prefix="cf_policy_"))
        (d / "sdlc-studio").mkdir(parents=True)
        if policy is not None:
            (d / "sdlc-studio" / ".config.yaml").write_text(f"review:\n  policy: {policy}\n")
        return d

    def test_an_undeclared_policy_blocks_exactly_as_today(self) -> None:
        cf = self._cf()
        d = self._root(None)
        try:
            self.assertEqual(cf.review_policy(d), "block")
            self.assertFalse(cf.reject_carries_forward(d, []))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_an_unrecognised_policy_is_refused_not_defaulted(self) -> None:
        cf = self._cf()
        d = self._root("carryforward")  # a plausible typo
        try:
            with self.assertRaises(cf.PolicyError):
                cf.review_policy(d)
        finally:
            shutil.rmtree(d, ignore_errors=True)


class CarryForwardTests(unittest.TestCase):
    """US0333: under carry-forward every finding is FILED or explicitly WAIVED."""

    def _cf(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "carry_forward", Path(__file__).resolve().parent.parent / "carry_forward.py")
        m = importlib.util.module_from_spec(spec); sys.modules["carry_forward"] = m
        spec.loader.exec_module(m); return m

    def _root(self):
        d = Path(tempfile.mkdtemp(prefix="cf_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text("review:\n  policy: carry-forward\n")
        return d

    def _file_bug(self, d, bid="BG9001"):
        bugs = d / "sdlc-studio" / "bugs"; bugs.mkdir(parents=True, exist_ok=True)
        (bugs / f"{bid}-carried.md").write_text(
            f"# {bid}: a carried finding\n\n> **Status:** Open\n> **Found-against:** US0001\n")
        return bid

    def test_an_unfiled_finding_blocks_the_close_under_carry_forward(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            bid = self._file_bug(d)
            # two filed, one neither filed nor waived
            findings = [{"ref": bid, "units": ["US0001"]}, {"ref": "", "waiver": ""}]
            with self.assertRaises(cf.PolicyError):
                cf.reject_carries_forward(d, findings)
            # all handled -> carries forward
            self.assertTrue(cf.reject_carries_forward(
                d, [{"ref": bid, "units": ["US0001"]}]))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_ref_that_resolves_to_no_artefact_is_refused(self) -> None:
        # US0333 AC1: a carried finding must be a real filed artefact, not a sentence. A ref
        # that resolves to nothing on disk is refused - without this a claimed-but-absent
        # finding would pass as handled.
        cf = self._cf(); d = self._root()
        try:
            with self.assertRaises(cf.PolicyError):
                cf.validate_carried(d, [{"ref": "BG9999", "units": ["US0001"]}])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_waiver_without_a_reason_is_refused(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            with self.assertRaises(cf.PolicyError):
                cf.validate_carried(d, [{"ref": "", "waiver": "   "}])
            cf.validate_carried(d, [{"ref": "", "waiver": "out of scope, tracked in Q3"}])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_finding_cannot_be_resolved_by_narrative_downgrade(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            for bad in ("downgrade to optional", "just an observation really", "soften to a note"):
                with self.subTest(bad=bad):
                    with self.assertRaises(cf.PolicyError):
                        cf.validate_carried(d, [{"ref": "", "waiver": bad}])
        finally:
            shutil.rmtree(d, ignore_errors=True)


REFERENCE_REVIEW = Path(__file__).resolve().parents[2] / "reference-review.md"


def _norm(text: str) -> str:
    """Collapse whitespace so a phrase wrapped across doc/brief lines still matches."""
    return " ".join(text.split())


class BriefStatesTheIsolatedCheckoutRuleTests(unittest.TestCase):
    """BG0440. The isolated-checkout rule was enforced author-side only: `mutation.run` refuses
    a target with uncommitted changes, protecting the AUTHOR, and nothing protected the tree
    from the REVIEWER. The brief is the one artefact guaranteed to reach a delegated reviewer,
    so a practice absent from it is held only by the dispatcher's memory - and four reviewers
    dispatched over one shared tree left a live mutant behind in it."""

    def _brief(self, mod, root: Path) -> str:
        _workspace(root)
        return mod.brief(root, "US0001", "qa")

    def test_the_brief_demands_an_isolated_checkout_and_says_why(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            text = self._brief(mod, Path(d))
            self.assertIn("ISOLATED CHECKOUT", text)
            self.assertIn("never the author", text)
            self.assertNotIn("isolated checkout for mutation", mod.missing_practices(text))

    def test_the_brief_names_the_MECHANISM_not_only_the_requirement(self) -> None:
        """A reviewer told an abstract requirement improvises; one told `isolation: 'worktree'`
        does the thing. The rule already existed in reference-review.md and was still bypassed."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("worktree", self._brief(mod, Path(d)))

    def test_the_brief_FORBIDS_the_tree_wide_cleanups_by_name(self) -> None:
        """`git stash` is what a reviewer told only to 'revert afterwards' reaches for, and it
        is tree-wide: it reverts a concurrent reviewer's mutant, so a SURVIVED verdict may
        describe a mutant that was never on disk when its test ran."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            text = self._brief(mod, Path(d))
            self.assertIn("git stash", text)
            self.assertIn("tree-wide", text)

    def test_the_practice_is_refused_when_its_reason_is_stripped(self) -> None:
        """The discriminating half. An instruction with no reason is the part a fresh reviewer
        drops first, so presence of the words alone must not satisfy the guard."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            text = self._brief(mod, Path(d))
            reasonless = re.sub(r"tree-wide[^.]*silently reverts a concurrent reviewer'?s mutant",
                                "REDACTED", _norm(text), flags=re.I)
            self.assertIn("isolated checkout for mutation", mod.missing_practices(reasonless))
            with self.assertRaises(ValueError):
                mod.assert_brief_practices(reasonless)


class OneIndependenceAuthorityTests(unittest.TestCase):
    """BG0443 + BG0444. There were FOUR independence predicates - `is_independent`,
    `sprint_covers_independently`, `is_independent_signoff` and a fourth hand-rolled inline in
    sprint.py reaching into critic's private `_id`. Correctness depended on each caller
    remembering which combination to AND, nothing checked the four agreed, and twice they did
    not: one required a non-empty reviewer and one did not, and one refused PRE_GATE while the
    module that actually gates Done accepted it."""

    def test_an_empty_reviewer_is_NOT_independent(self) -> None:
        """BG0443. `bool(author) and reviewer != author` is True for an empty reviewer, because
        '' != 'alice'. A guard that fails OPEN is the direction this project says it must never
        fail, and four gate consumers used that predicate alone."""
        mod = _load()
        self.assertFalse(mod.is_independent(
            {"verdict": "APPROVE", "reviewer": "", "author": "alice"}))
        ok, why = mod.independence("", "alice")
        self.assertFalse(ok)
        self.assertIn("no reviewer", why)

    def test_an_empty_reviewer_is_refused_by_EVERY_predicate(self) -> None:
        """BG0443's own discriminating case, distinct from the caller sweep: the hole was in
        `is_independent`, and the question is whether its SIBLINGS ever shared it. They must all
        refuse the same row, or the fix has closed one door in a corridor of four."""
        mod = _load()
        row = {"verdict": "APPROVE", "reviewer": "", "author": "alice"}
        self.assertFalse(mod.is_independent(row))
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(mod.sprint_covers_independently(Path(d), "US0001", row))
            self.assertFalse(mod.is_independent_signoff(
                Path(d), "US0001", {"principal": "", "author": "alice"}))

    def test_the_PRE_GATE_sentinel_is_refused_by_EVERY_predicate(self) -> None:
        """BG0444. `sprint_covers_independently` tested only non-empty-and-distinct, so it
        accepted the migration sentinel. sprint.py compensated by AND-ing a second predicate on;
        conformance.py did not, so the same row cleared Done in one module and not the other."""
        mod = _load()
        row = {"verdict": "APPROVE", "reviewer": "bob", "author": mod.PRE_GATE}
        self.assertFalse(mod.is_independent(row))
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(mod.sprint_covers_independently(Path(d), "US0001", row))
            self.assertFalse(mod.is_independent_signoff(
                Path(d), "US0001", {"principal": "bob", "author": mod.PRE_GATE}))

    def test_the_predicates_AGREE_across_every_pair(self) -> None:
        """The property the four never had. Whatever the authority says, each predicate says -
        so a caller can no longer be wrong by picking one."""
        mod = _load()
        cases = [("", ""), ("", "alice"), ("alice", ""), ("alice", "alice"),
                 ("alice", "bob"), ("bob", mod.PRE_GATE), (mod.PRE_GATE, "bob"),
                 ("Dani\\_Okafor", "dani_okafor"), ("-", "alice"), ("alice", "-")]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for reviewer, author in cases:
                want = mod.independence(reviewer, author)[0]
                with self.subTest(reviewer=reviewer, author=author):
                    self.assertIs(mod.is_independent(
                        {"verdict": "APPROVE", "reviewer": reviewer, "author": author}), want)
                    self.assertIs(mod.sprint_covers_independently(
                        root, "US0001", {"verdict": "APPROVE", "reviewer": reviewer,
                                         "author": author}), want)

    def test_the_writer_FLOORS_an_empty_reviewer_so_it_cannot_reach_the_ledger(self) -> None:
        """The predicate alone is not enough: the writer is what made the bad row reachable.
        `record_verdict` floored the author to `-` and gave the reviewer no such floor."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod.record_verdict(root, "US0001", "APPROVE", reviewer="", author="alice")
            # The PARSED REVIEWER CELL, not a substring of the row. `assertIn("| - |", ...)` was
            # satisfied by the trailing ISSUES cell whatever the reviewer held, so dropping the
            # floor left the test green and the mutant survived the entire skill suite - the one
            # writer-side behaviour this bug shipped was pinned by nothing.
            rows = mod.read_verdicts(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["reviewer"], "-",
                             "the empty reviewer cell was not floored - it reached the ledger "
                             f"as {rows[0]['reviewer']!r}")
            self.assertFalse(mod.is_independent(mod.verdict_for(root, "US0001")))

    def test_NO_module_hand_rolls_the_independence_comparison(self) -> None:
        """The shape that produced both bugs, pinned. A module comparing reviewer to author
        itself is a fifth predicate nobody is checking against the other four."""
        import ast
        scripts = Path(__file__).resolve().parents[1]
        offenders = []
        # `scripts/lib/` TOO. The first version globbed `scripts/*.py` only, so the same
        # hand-rolled predicate placed one directory down was invisible - a sweep that names its
        # scope narrower than its claim reports the narrow answer as the broad one, which is the
        # class this repo's own carried lessons name twice.
        for path in sorted([*scripts.glob("*.py"), *(scripts / "lib").glob("*.py")]):
            if path.name == "critic.py":
                continue                      # the authority itself
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                continue
            # An ALIASED import evades an Attribute-only match: `from critic import _id as _n`
            # binds a plain Name, so `_n(a) == _n(b)` is the same hand-rolled predicate wearing a
            # different shape. Collect the local names any such import binds, then flag calls to
            # them as well as `critic._id(...)`.
            aliases = {a.asname or a.name
                       for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                       and (node.module or "").split(".")[-1] == "critic"
                       for a in node.names if a.name.startswith("_")}
            for node in ast.walk(tree):
                # `critic._id(...)` - reaching into the authority's private normaliser is how a
                # caller builds its own comparison out of the authority's parts.
                if (isinstance(node, ast.Attribute) and node.attr == "_id"
                        and isinstance(node.value, ast.Name) and node.value.id == "critic"):
                    offenders.append(f"{path.name}:{node.lineno}")
                elif isinstance(node, ast.Name) and node.id in aliases:
                    offenders.append(f"{path.name}:{node.lineno} (aliased {node.id})")
        offenders = sorted(set(offenders))
        self.assertEqual(
            offenders, [],
            "these lines rebuild the independence test from critic's private parts instead of "
            f"calling `critic.independence`: {offenders}")


class ReviewerBriefTests(unittest.TestCase):
    """US0318 (EP0108): the shipped reviewer brief carries every standing practice, each
    with its reason, and a brief missing any is refused; reference-review.md documents them.

    The set has since grown (US0505 added regression cover for a repair), so nothing here
    hardcodes how many there are - the count comes from `_BRIEF_PRACTICES` itself. The method
    name is kept because a shipped Verify line resolves to it."""

    def _brief(self, mod, root: Path) -> str:
        _workspace(root)
        return mod.brief(root, "US0001", "qa")

    def test_a_brief_missing_any_of_the_three_practices_is_refused(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = self._brief(mod, root)
            # the shipped brief carries every practice, each with its reason
            self.assertEqual(mod.missing_practices(text), [])
            mod.assert_brief_practices(text)  # does not raise
            # strip each practice's instruction in turn: the guard names it missing and refuses
            for name, instruction, _reason in mod._BRIEF_PRACTICES:
                gutted = re.sub(instruction, "REDACTED", _norm(text), flags=re.I)
                self.assertIn(name, mod.missing_practices(gutted))
                with self.assertRaises(ValueError):
                    mod.assert_brief_practices(gutted)
            # a practice named WITHOUT its reason still counts as missing - the reason is the
            # half a fresh reviewer drops first, so presence of the instruction alone is not enough
            reasonless = ("On a REPAIR review, rule each previous finding CLOSED, OVER-CLAIMED "
                          "or MOVED. Mutate the author's TESTS, not only the code. When a mutant "
                          "SURVIVES, re-test its branch in ISOLATION before drawing any "
                          "conclusion from it. A repair that changes behaviour carries a test "
                          "asserting that behaviour; where it does not, report the missing "
                          "regression cover as a finding.")
            self.assertEqual(len(mod.missing_practices(reasonless)), len(mod._BRIEF_PRACTICES),
                             "instructions with no reasons must all count as missing")
            # reference-review.md documents every one, so the shipped doc and the code agree
            doc = _norm(REFERENCE_REVIEW.read_text(encoding="utf-8"))
            for token in ("CLOSED", "OVER-CLAIMED", "MOVED", "author's TESTS", "isolation",
                          "regression cover"):
                self.assertIn(token, doc)

    def test_the_survivor_instruction_requires_isolation_before_a_conclusion(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = self._brief(mod, root)
            self.assertNotIn("isolation re-test of a survivor", mod.missing_practices(text))
            body = _norm(text)
            # reorder so the conclusion is drawn BEFORE the isolation re-test: no longer carried
            reordered = body.replace(
                "re-test its branch in ISOLATION before drawing any conclusion from it",
                "draw your conclusion first and then re-test its branch in ISOLATION")
            self.assertIn("isolation re-test of a survivor", mod.missing_practices(reordered))
            # the reason (a sibling guard masking the branch) is required, not just the word
            self.assertIn("sibling guard", body)


class RepairVerdictTests(unittest.TestCase):
    """US0319 (EP0108): a repair review is briefed with each previous finding enumerated and
    returns a CLOSED / OVER-CLAIMED / MOVED verdict per item; MOVED is not counted closed."""

    def test_a_repair_brief_enumerates_every_previous_finding(self) -> None:
        mod = _load()
        findings = ["readiness.py:88 grep verb takes no flag",
                    "mutation.py reuses the cached pyc",
                    "the brief leaks the round number",
                    "the resolution claims mutation-proven"]
        out = mod.enumerate_repair_findings(findings)
        for f in findings:
            self.assertIn(f, out)                       # every finding shown item by item
        for i in range(1, len(findings) + 1):
            self.assertIn(f"{i}.", out)                 # each enumerated as its own item
        with self.assertRaises(ValueError):            # an empty prior set is refused
            mod.enumerate_repair_findings([])

    def test_a_verdict_leaving_a_finding_unruled_is_refused(self) -> None:
        mod = _load()
        findings = ["f1", "f2", "f3", "f4"]
        rulings = {"f1": "CLOSED", "f2": "OVER-CLAIMED", "f3": "MOVED"}  # f4 unruled
        with self.assertRaises(ValueError) as ctx:
            mod.validate_repair_verdict(findings, rulings)
        self.assertIn("f4", str(ctx.exception))         # the unruled finding is named
        with self.assertRaises(ValueError):            # a ruling off the vocabulary is refused
            mod.validate_repair_verdict(["f1"], {"f1": "fixed"})
        self.assertTrue(mod.validate_repair_verdict(findings, {**rulings, "f4": "CLOSED"}))

    def test_a_moved_finding_is_not_counted_as_closed(self) -> None:
        mod = _load()
        rulings = {"f1": "MOVED", "f2": "CLOSED", "f3": "OVER-CLAIMED"}
        open_findings = mod.repair_open_findings(rulings)
        self.assertIn("f1", open_findings)              # MOVED survived
        self.assertIn("f3", open_findings)              # OVER-CLAIMED survived
        self.assertNotIn("f2", open_findings)           # only CLOSED is closed


class ClaimInventoryTests(unittest.TestCase):
    """US0320/US0321 (EP0109): the brief directs a first pass over all four prose surfaces, and
    each claim is ruled TRUE / FALSE / UNVERIFIABLE - unverifiable counted apart from true."""

    def test_the_brief_names_all_four_prose_surfaces(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root)
            text = mod.brief(root, "US0001", "qa")
            self.assertEqual(mod.missing_claim_surfaces(text), [])
            mod.assert_brief_claim_pass(text)          # does not raise
            # dropping any one surface exempts it - the guard names it and refuses
            for surface in mod.CLAIM_SURFACES:
                gutted = _norm(text).replace(surface, "SOMETHING")
                self.assertIn(surface, mod.missing_claim_surfaces(gutted))
                with self.assertRaises(ValueError):
                    mod.assert_brief_claim_pass(gutted)
            # reference-review.md names all four surfaces too
            doc = _norm(REFERENCE_REVIEW.read_text(encoding="utf-8"))
            for surface in mod.CLAIM_SURFACES:
                self.assertIn(surface, doc)

    def test_a_claim_left_unruled_is_refused(self) -> None:
        mod = _load()
        claims = ["c1", "c2", "c3", "c4", "c5", "c6"]
        rulings = {"c1": "TRUE", "c2": "FALSE", "c3": "UNVERIFIABLE",
                   "c4": "TRUE", "c5": "FALSE"}         # six claims, five rulings - c6 unruled
        with self.assertRaises(ValueError) as ctx:
            mod.validate_claim_inventory(claims, rulings)
        self.assertIn("c6", str(ctx.exception))
        with self.assertRaises(ValueError):            # a ruling off the vocabulary is refused
            mod.validate_claim_inventory(["c1"], {"c1": "probably"})
        self.assertTrue(mod.validate_claim_inventory(claims, {**rulings, "c6": "UNVERIFIABLE"}))

    def test_an_unverifiable_claim_is_counted_separately_from_true(self) -> None:
        mod = _load()
        s = mod.summarise_claim_pass({"c1": "UNVERIFIABLE"})
        self.assertEqual(s["unverifiable"], 1)
        self.assertEqual(s["true"], 0)                  # not folded into TRUE
        self.assertEqual(s["on_trust"], 1)              # reported as resting on trust
        self.assertEqual(s["checked"], 0)
        s2 = mod.summarise_claim_pass(["TRUE", "UNVERIFIABLE", "UNVERIFIABLE"])
        self.assertEqual((s2["true"], s2["unverifiable"], s2["on_trust"]), (1, 2, 2))

    def test_an_all_unverifiable_pass_does_not_render_as_verified(self) -> None:
        mod = _load()
        all_unv = {"c1": "UNVERIFIABLE", "c2": "UNVERIFIABLE"}
        s = mod.summarise_claim_pass(all_unv)
        self.assertFalse(s["verified"])                 # nothing settled
        self.assertIn("NOT VERIFIED", mod.render_claim_pass(all_unv))
        # a pass with even one settled claim reads differently - no NOT VERIFIED
        self.assertNotIn("NOT VERIFIED", mod.render_claim_pass({"c1": "FALSE", "c2": "UNVERIFIABLE"}))
        self.assertTrue(mod.summarise_claim_pass({"c1": "FALSE"})["verified"])


class CriticFieldsFileTests(unittest.TestCase):
    """US0391: the sign-off note reaches the ledger through the shared fields-file loader, so
    prose carrying shell metacharacters is stored verbatim (Python never runs it) rather than
    swallowed by a shell."""

    def _repo(self):
        d = Path(tempfile.mkdtemp(prefix="critic_ff_"))
        (d / "sdlc-studio" / "reviews").mkdir(parents=True)
        return d

    def _run(self, mod, argv):
        import contextlib, io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = mod.main(argv)
        return rc, buf.getvalue()

    def test_fields_file_note_is_stored_verbatim_with_shell_metacharacters(self) -> None:
        import json
        mod = _load()
        d = self._repo()
        hazard = "run `git status` and $(whoami) - dangerous on the flag path"
        (d / "fields.json").write_text(json.dumps({"note": hazard}))
        rc, _ = self._run(mod, ["signoff", "--unit", "US0001", "--principal", "operator",
                                "--author", "builder", "--fields-file", str(d / "fields.json"),
                                "--root", str(d)])
        self.assertEqual(rc, 0)
        recorded = mod.signoff_path(d).read_text(encoding="utf-8")
        self.assertIn("`git status`", recorded)     # backtick survived - not executed
        self.assertIn("$(whoami)", recorded)          # command substitution stored verbatim

    def test_unknown_field_is_refused_by_the_shared_loader(self) -> None:
        import json
        mod = _load()
        d = self._repo()
        (d / "bad.json").write_text(json.dumps({"nte": "typo key nobody reads"}))
        rc, _ = self._run(mod, ["signoff", "--unit", "US0001", "--principal", "operator",
                                "--author", "builder", "--fields-file", str(d / "bad.json"),
                                "--root", str(d)])
        self.assertEqual(rc, 2)                        # refused, not silently ignored


class SupersedeTests(unittest.TestCase):
    """US0374: a verdict row that records an event which did not happen is retired through
    the tool - an appended supersession record naming the row, the reason and an authoriser
    who is not the row's own author. The row itself is never deleted."""

    def _row(self, mod, root: Path, unit: str) -> str:
        prefix = f"| {unit} "
        return next(ln for ln in mod.verdicts_path(root).read_text(encoding="utf-8").splitlines()
                    if ln.startswith(prefix))

    def test_supersession_records_reason_and_authoriser_and_leaves_the_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0276", "approve",
                               reviewer="Darren Benson (operator)",
                               author="sdlc-studio; agent; v1")
            row = self._row(mod, root, "US0276")
            date = mod.read_verdicts(root)[0]["date"]
            reason = ("the operator was the reviewer of record, not the adversarial critic, "
                      "so the pass this row states never ran")
            mod.record_supersession(root, "US0276", date=date, reason=reason,
                                    authorised_by="Darren Benson (operator)",
                                    boundary="operator console")
            after = mod.verdicts_path(root).read_text(encoding="utf-8")
            self.assertIn(row + "\n", after)     # byte-for-byte: corrected by addition
            recs = mod.read_supersessions(root)
            self.assertEqual(len(recs), 1)
            rec = recs[0]
            self.assertEqual(rec["unit"], "US0276")
            self.assertEqual(rec["row_date"], date)
            self.assertEqual(rec["row_verdict"], "APPROVE")
            self.assertEqual(rec["row_reviewer"], "Darren Benson (operator)")
            self.assertEqual(rec["row_author"], "sdlc-studio; agent; v1")
            self.assertEqual(rec["reason"], reason)
            self.assertEqual(rec["authorised_by"], "Darren Benson (operator)")
            # a later verdict still lands inside the table, so the log stays one block
            mod.record_verdict(root, "US0277", "approve", reviewer="critic-a", author="builder")
            lines = mod.verdicts_path(root).read_text(encoding="utf-8").splitlines()
            self.assertLess(lines.index(self._row(mod, root, "US0277")),
                            lines.index(mod.SUPERSEDE_HEADING))
            self.assertEqual(mod.verdict_for(root, "US0277")["verdict"], "APPROVE")

    def test_row_author_alone_is_refused_as_the_authoriser(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0276", "approve",
                               reviewer="Darren Benson (operator)",
                               author="sdlc-studio; agent; v1")
            date = mod.read_verdicts(root)[0]["date"]
            before = mod.verdicts_path(root).read_text(encoding="utf-8")
            for authoriser in ("sdlc-studio; agent; v1",     # the row's own author
                               "SDLC-Studio; Agent; V1",     # ...however it is cased
                               "",                           # nobody named at all
                               "   "):
                with self.assertRaises(ValueError):
                    mod.record_supersession(root, "US0276", date=date, reason="wrong row",
                                            authorised_by=authoriser, boundary="operator console")
            self.assertEqual(mod.read_supersessions(root), [])
            self.assertEqual(mod.verdicts_path(root).read_text(encoding="utf-8"), before)
            self.assertFalse(mod.read_verdicts(root)[0]["superseded"])

    def test_unmatched_row_refused_and_nothing_written(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0276", "approve", reviewer="critic-a",
                               author="sdlc-studio; agent; v1")
            date = mod.read_verdicts(root)[0]["date"]
            before = mod.verdicts_path(root).read_text(encoding="utf-8")
            with self.assertRaises(ValueError):     # no row for the unit at all
                mod.record_supersession(root, "US9999", date=date, reason="no such row",
                                        authorised_by="Darren Benson (operator)",
                                        boundary="operator console")
            with self.assertRaises(ValueError):     # right unit, a date it never carried
                mod.record_supersession(root, "US0276", date="2020-01-01",
                                        reason="wrong date", authorised_by="Darren Benson",
                                        boundary="operator console")
            self.assertEqual(mod.read_supersessions(root), [])
            self.assertEqual(mod.verdicts_path(root).read_text(encoding="utf-8"), before)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = mod.main(["supersede", "--unit", "US9999", "--date", date,
                               "--reason", "no such row", "--authorised-by", "operator",
                               "--boundary", "operator console", "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("US9999", err.getvalue())
            self.assertEqual(mod.read_supersessions(root), [])

    def test_ambiguous_row_refused_until_narrowed(self) -> None:
        # Two rows for one unit on one date: retiring "the row" is undefined, so it is
        # refused rather than resolved by guessing which one was meant.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0300", "reject", reviewer="critic-a", author="builder")
            mod.record_verdict(root, "US0300", "approve", reviewer="critic-b", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            with self.assertRaises(ValueError):
                mod.record_supersession(root, "US0300", date=date, reason="dup",
                                        authorised_by="operator", boundary="operator console")
            self.assertEqual(mod.read_supersessions(root), [])
            mod.record_supersession(root, "US0300", date=date, reviewer="critic-b",
                                    reason="the approve was filed against the wrong unit",
                                    authorised_by="operator", boundary="operator console")
            self.assertEqual(mod.read_supersessions(root)[0]["row_reviewer"], "critic-b")
            self.assertEqual(mod.verdict_for(root, "US0300")["reviewer"], "critic-a")

    def test_cli_correct_is_the_same_verb(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0276", "approve", reviewer="critic-a", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            with contextlib.redirect_stdout(io.StringIO()):
                rc = mod.main(["correct", "--unit", "US0276", "--date", date,
                               "--reason", "the pass it records never ran",
                               "--authorised-by", "Darren Benson (operator)",
                               "--boundary", "operator console",
                               "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertEqual(mod.read_supersessions(root)[0]["authorised_by"],
                             "Darren Benson (operator)")
            self.assertIsNone(mod.verdict_for(root, "US0276"))


class SupersededGateTests(unittest.TestCase):
    """US0375: a superseded row is retired for every gate that reads it, while staying
    in the file and printing as superseded - the audit trail keeps the record that it
    happened, and the gate stops acting on it."""

    def test_an_author_superseding_its_own_seats_verdict_is_refused(self) -> None:
        """A supersession retires a VERDICT; whether it retires the ATTRIBUTION turns on the
        authoriser (see PrincipalAuthorisedSupersessionTests). The bypass this closes: an author
        blocked by a REJECT superseded it - the only guard being that the authoriser was not the
        row's own author, met by any other string - the reviewer dropped out of the session set,
        and the author's own subagent was accepted as reviewer of record. Refused end to end now:
        the seat that filed the blocking verdict also filed evidence, so it is not an independent
        authoriser and the correction is refused before it can move the gate."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="the defect the reject records")
            mod.record_verdict(root, "US0001", "reject",
                               reviewer="qa-seat", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")
            with self.assertRaises(ValueError):
                mod.record_supersession(root, "US0001", date=date, reason="mis-filed",
                                        authorised_by="qa-seat", boundary="same session")
            # nothing retired: the verdict still stands and independence is unchanged
            self.assertIsNotNone(mod.verdict_for(root, "US0001"))
            self.assertIn("qa-seat", mod._session_reviewer_ids(root, "US0001"))
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")

    def test_a_HAND_APPENDED_author_supersession_cannot_retire_a_blocking_REJECT(self) -> None:
        """The fail-open in the honesty gate itself. `record_supersession` refuses to WRITE an
        author-authorised, boundary-less correction, but the log is a text file and a hand
        append walks round the tool - which is precisely why `_is_principal_superseded` exists
        as the read-time backstop. Only the sign-off gate consulted it. `verdict_for` tested the
        flag for plain truthiness, so one appended line naming the row's own author as
        authoriser and `-` as boundary deleted the REJECT from every reader downstream, and the
        close then reported the unit "covered by an independent pass".

        The grade required now scales with the direction the mistake fails: retiring an APPROVE
        weakly costs an approval and the gate refuses, but retiring a REJECT weakly removes the
        only record that blocks the unit.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "reject", reviewer="independent-qa",
                               author="the-author", issues="a real defect")
            row = mod.read_verdicts(root)[-1]
            path = mod.verdicts_path(root)
            path.write_text(
                path.read_text(encoding="utf-8") + "\n" + mod._SUPERSEDE_PREFIX
                + f"unit=US0001 row-date={row['date']} row-verdict=REJECT "
                  "row-reviewer=independent-qa row-author=the-author "
                  "authorised-by=the-author boundary=- reason=inconvenient "
                  "recorded=2026-07-31\n", encoding="utf-8")
            marked = mod.read_verdicts(root)[-1]
            self.assertTrue(marked["superseded"], "the hand append did parse - if this fails "
                                                  "the test proves nothing about the gate")
            self.assertFalse(mod._is_principal_superseded(root, "US0001", marked),
                             "the backstop must judge this correction non-principal")
            live = mod.verdict_for(root, "US0001")
            self.assertIsNotNone(live, "an author retired the REJECT blocking their own work")
            self.assertEqual("REJECT", live["verdict"])

    def test_a_PRINCIPAL_supersession_still_retires_a_reject(self) -> None:
        """The other half, or the repair is just a refusal to correct anything. A genuine
        principal - not the author, and having done no review work on the unit - retires the
        row exactly as before."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0002", "reject", reviewer="independent-qa",
                               author="the-author", issues="filed against the wrong unit")
            date = mod.read_verdicts(root)[-1]["date"]
            mod.record_supersession(root, "US0002", date=date, reviewer="independent-qa",
                                    reason="filed against the wrong unit",
                                    authorised_by="Darren Benson (operator)",
                                    boundary="operator console")
            self.assertIsNone(mod.verdict_for(root, "US0002"))

    def test_verdict_for_skips_the_superseded_row_and_falls_back(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0300", "approve", reviewer="critic-a", author="builder")
            mod.record_verdict(root, "US0300", "reject", reviewer="critic-b", author="builder",
                               issues="found a hole")
            date = mod.read_verdicts(root)[-1]["date"]
            mod.record_supersession(root, "US0300", date=date, reviewer="critic-b",
                                    reason="the reject was filed against the wrong unit",
                                    authorised_by="Darren Benson (operator)",
                                    boundary="operator console")
            live = mod.verdict_for(root, "US0300")
            self.assertEqual(live["verdict"], "APPROVE")     # the earlier LIVE row
            self.assertEqual(live["reviewer"], "critic-a")
            # a unit whose only row is superseded has NO verdict - never a silent approval
            mod.record_verdict(root, "US0301", "approve", reviewer="critic-a", author="builder")
            mod.record_supersession(root, "US0301", date=date, reason="never ran",
                                    authorised_by="Darren Benson (operator)",
                                    boundary="operator console")
            self.assertIsNone(mod.verdict_for(root, "US0301"))

    def test_superseded_row_stays_visible_and_flagged_in_show(self) -> None:
        import json as _json
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0276", "approve", reviewer="critic-a", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            reason = "the adversarial pass it records never ran"
            mod.record_supersession(root, "US0276", date=date, reason=reason,
                                    authorised_by="Darren Benson (operator)",
                                    boundary="operator console")
            mod.record_verdict(root, "US0277", "approve", reviewer="critic-a", author="builder")
            rows = mod.read_verdicts(root)
            self.assertEqual([r["unit"] for r in rows], ["US0276", "US0277"])  # nothing dropped
            self.assertTrue(rows[0]["superseded"])
            self.assertEqual(rows[0]["superseded_reason"], reason)
            self.assertEqual(rows[0]["superseded_by"], "Darren Benson (operator)")
            self.assertFalse(rows[1]["superseded"])          # the live row is not flagged
            self.assertEqual(rows[1]["superseded_reason"], "")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["show", "--root", str(root)])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("US0276", text)
            self.assertIn(reason, text)
            self.assertIn("Darren Benson (operator)", text)
            self.assertEqual(len([ln for ln in text.splitlines() if "US0277" in ln]), 1)
            self.assertNotIn(reason, [ln for ln in text.splitlines() if "US0277" in ln][0])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["show", "--format", "json", "--root", str(root)])
            self.assertEqual(rc, 0)
            payload = _json.loads(out.getvalue())
            self.assertEqual(len(payload), 2)
            self.assertEqual(payload[0]["superseded_reason"], reason)
            self.assertEqual(payload[0]["superseded_by"], "Darren Benson (operator)")
            self.assertFalse(payload[1]["superseded"])


class PrincipalAuthorisedSupersessionTests(unittest.TestCase):
    """BG0284. Superseding retires a verdict; whether it also retires the ATTRIBUTION (so the
    named reviewer stops counting toward independence) turns on WHO authorised it. The bypass
    and the mis-attribution incident are mechanically identical in the verdict rows alone -
    the recordable distinction is that a working session reviewer left an EVIDENCE row, while a
    principal wrongly named on a verdict row did not, and authorised the correction from a
    separate trust boundary. That distinction is what the guard tests."""

    def test_an_authoring_session_authoriser_is_refused(self) -> None:
        """AC1. A supersession authorised by a party who did in-session review work on the unit -
        or by the row's own author - is refused, on the sign-off's own independence rule."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            # qa-seat runs the adversarial pass (evidence) and files a blocking REJECT.
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="a hole in the batch fan-out")
            mod.record_verdict(root, "US0001", "reject", reviewer="qa-seat", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            before = mod.verdicts_path(root).read_text(encoding="utf-8")
            for authoriser in ("qa-seat",        # the author's own seat - it left evidence
                               "QA-Seat",         # ...however cased
                               "builder"):        # the row's own author
                with self.assertRaises(ValueError) as cm:
                    mod.record_supersession(root, "US0001", date=date, reason="inconvenient",
                                            authorised_by=authoriser, boundary="same session")
                self.assertTrue(
                    "independen" in str(cm.exception).lower()
                    or "author" in str(cm.exception).lower())
            # nothing written: the verdict still stands and still blocks
            self.assertEqual(mod.read_supersessions(root), [])
            self.assertEqual(mod.verdicts_path(root).read_text(encoding="utf-8"), before)
            self.assertIn("qa-seat", mod._session_reviewer_ids(root, "US0001"))

    def test_a_principal_authorised_supersession_clears_the_strand(self) -> None:
        """AC2. A verdict row wrongly names the operator as REVIEWER; the operator never reviewed
        (no evidence row). That strands the unit - the operator reads as a session reviewer and so
        cannot be its reviewer of record. A supersession the operator authorises from a separate,
        recorded boundary retires the attribution, and the strand clears."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="operator", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            # stranded: the operator reads as an authoring-session reviewer, cannot sign off
            self.assertIn("operator", mod._session_reviewer_ids(root, "US0001"))
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="operator", author="builder")
            mod.record_supersession(
                root, "US0001", date=date,
                reason="the operator was reviewer of record, not the adversarial critic; "
                       "the pass this row states never ran",
                authorised_by="operator", boundary="operator console")
            # the attribution is retired for the gate: the strand is cleared...
            self.assertNotIn("operator", mod._session_reviewer_ids(root, "US0001"))
            # ...so the legitimate reviewer of record can now sign off
            mod.record_signoff(root, "US0001", principal="operator", author="builder")
            self.assertIsNotNone(mod.signoff_for(root, "US0001"))
            # the boundary is recorded on the correction
            self.assertEqual(mod.read_supersessions(root)[0]["boundary"], "operator console")

    def test_no_author_only_sequence_clears_the_gate(self) -> None:
        """AC3. On a unit the author built, with a genuine two-role review (evidence + verdict),
        no supersession the author can author ALONE - itself or its own seat, any boundary string
        it can assert - retires the reviewer from the gate. A blocking review leaves evidence, and
        an evidence-row reviewer is refused as an authoriser however the boundary is dressed up."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="a real defect")
            mod.record_verdict(root, "US0001", "reject", reviewer="qa-seat", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            for authoriser, boundary in (("builder", "console"),      # the author
                                         ("qa-seat", "another session"),  # its seat (has evidence)
                                         ("qa-seat", "CI")):           # relabel the boundary
                with self.assertRaises(ValueError):
                    mod.record_supersession(root, "US0001", date=date, reason="retire it",
                                            authorised_by=authoriser, boundary=boundary)
            self.assertEqual(mod.read_supersessions(root), [])
            # the gate is unmoved and a self-sign-off stays refused
            self.assertIn("qa-seat", mod._session_reviewer_ids(root, "US0001"))
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")

    def test_a_boundaryless_correction_is_refused(self) -> None:
        """The boundary is mandatory - superseding is held to the sign-off's rule, and a
        correction with no recorded trust boundary is a hand edit with extra steps."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="operator", author="builder")
            date = mod.read_verdicts(root)[0]["date"]
            for boundary in ("", "   "):
                with self.assertRaises(ValueError) as cm:
                    mod.record_supersession(root, "US0001", date=date, reason="mis-filed",
                                            authorised_by="operator", boundary=boundary)
                self.assertIn("boundary", str(cm.exception).lower())
            self.assertEqual(mod.read_supersessions(root), [])

    def _forge(self, mod, root: Path, row: dict, authorised_by: str, boundary: str) -> None:
        """Hand-append a supersession record straight to the log, bypassing record_supersession -
        the walk-round-the-tool a read-time backstop exists to catch."""
        fields = (f"unit={row['unit']} row-date={row['date']} "
                  f"row-verdict={row['verdict'].upper()} row-reviewer={row['reviewer']} "
                  f"row-author={row['author']} authorised-by={authorised_by} "
                  f"boundary={boundary} reason=inconvenient recorded=2026-07-25")
        path = mod.verdicts_path(root)
        path.write_text(path.read_text(encoding="utf-8")
                        + "\n" + mod.SUPERSEDE_HEADING + "\n\n" + mod._SUPERSEDE_PREFIX
                        + fields + "\n", encoding="utf-8")

    def test_a_hand_forged_worker_correction_does_not_clear_the_gate(self) -> None:
        """Read-time backstop, worker leg: a hand-appended record authorised by an in-session
        seat - even with a boundary claim - retires the VERDICT but not the attribution, so the
        reviewer keeps counting and no self-sign-off clears the gate."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="a real defect")
            mod.record_verdict(root, "US0001", "reject", reviewer="qa-seat", author="builder")
            self._forge(mod, root, mod.read_verdicts(root)[0],
                        authorised_by="qa-seat", boundary="another session")
            self.assertTrue(mod.read_verdicts(root)[0]["superseded"])   # the forge parsed
            self.assertIn("qa-seat", mod._session_reviewer_ids(root, "US0001"))
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="qa-seat", author="builder")

    def test_a_hand_forged_boundaryless_correction_does_not_clear_the_gate(self) -> None:
        """Read-time backstop, boundary leg: the authoriser here is independent (not the author,
        not a worker), so ONLY the missing boundary stops it - a correction with no recorded trust
        boundary retires the verdict but not the attribution, and the reviewer keeps counting. This
        isolates the boundary check: an otherwise-clearing correction fails purely for want of a
        recorded boundary (AC2 shows the same shape WITH a boundary does clear)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            # a verdict row wrongly names the operator; the operator did no other reviewing work
            mod.record_verdict(root, "US0001", "approve", reviewer="operator", author="builder")
            row = mod.read_verdicts(root)[0]
            self._forge(mod, root, row, authorised_by="operator", boundary="")   # no boundary
            self.assertTrue(mod.read_verdicts(root)[0]["superseded"])            # the forge parsed
            # boundaryless: the attribution is NOT retired, so the operator keeps counting
            self.assertIn("operator", mod._session_reviewer_ids(root, "US0001"))
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="operator", author="builder")


class PlanCriticTests(unittest.TestCase):
    """D0061 / RFC0050 option B. Every adversarial surface in this project ran AFTER code
    existed, so the cheapest finding available - "this unit does not need to be built" - could
    only be reached by building it."""

    def test_three_lenses_run_before_the_plan_is_written(self) -> None:
        """AC1. A critique delivered after `--write` is a critique of a decision already
        taken."""
        mod = _load()
        rep = mod.plan_critique(["US0001"], {"scope": [], "risk": [], "efficiency": []})
        self.assertEqual(sorted(rep["lenses"]), sorted(mod.PLAN_LENSES))
        for lens in mod.PLAN_LENSES:
            self.assertTrue(rep["lenses"][lens]["ran"])

    def test_a_lens_with_no_finding_is_distinct_from_a_lens_that_did_not_run(self) -> None:
        """AC2, and the distinction the whole report rests on. A lens silent because it found
        nothing and one that never ran are otherwise indistinguishable - which is how a partial
        pass gets read as a clean one."""
        mod = _load()
        rep = mod.plan_critique(["US0001"], {"scope": []})   # risk/efficiency absent
        self.assertTrue(rep["lenses"]["scope"]["ran"])
        self.assertFalse(rep["lenses"]["risk"]["ran"])
        text = "\n".join(mod.render_plan_critique(rep))
        self.assertIn("found nothing", text)
        self.assertIn("NOT RUN", text)

    def test_a_failed_pass_leaves_no_run_and_no_plan_file(self) -> None:
        """AC3. Both the ordering defect this project shipped and its mirror image came from a
        write that outlived its refusal, so the refusal must be computable before anything is
        written."""
        mod = _load()
        rep = mod.plan_critique(["US0001"], {"scope": [{"title": "unneeded", "disposition": ""}]})
        self.assertTrue(mod.undispositioned_plan_findings(rep),
                        "an undispositioned finding must be detectable without writing anything")


class PlanCriticIntensityTests(unittest.TestCase):
    """The pass spends tokens BEFORE any value is delivered, on a sprint length already under
    complaint, so a two-unit batch must not pay for a forty-unit review."""

    def test_a_larger_batch_receives_more_scrutiny(self) -> None:
        """AC1. The rule is stated rather than emergent, so a reader can predict it."""
        mod = _load()
        self.assertEqual(mod.plan_intensity(3), "lite")
        self.assertEqual(mod.plan_intensity(12), "full")
        self.assertEqual(mod.plan_intensity(45), "ultra")
        small = mod.plan_critique([f"US{i:04d}" for i in range(1, 4)], {})
        large = mod.plan_critique([f"US{i:04d}" for i in range(1, 46)], {})
        self.assertGreater(len(large["examined"]), len(small["examined"]))

    def test_the_pass_names_what_the_intensity_cap_skipped(self) -> None:
        """AC2. A bounded pass that reports only what it found reads as complete coverage, and
        a silent cap is how a partial sweep is mistaken for a full one."""
        mod = _load()
        rep = mod.plan_critique([f"US{i:04d}" for i in range(1, 61)], {})
        self.assertTrue(rep["skipped"], "an over-cap batch must record what it skipped")
        text = "\n".join(mod.render_plan_critique(rep))
        self.assertIn("NOT examined individually", text)

    def test_a_batch_inside_the_cap_reports_nothing_skipped(self) -> None:
        """The control: a skipped-list that appears when nothing was skipped is noise."""
        mod = _load()
        rep = mod.plan_critique(["US0001", "US0002"], {})
        self.assertEqual(rep["skipped"], [])
        self.assertNotIn("NOT examined", "\n".join(mod.render_plan_critique(rep)))


class AcDefectTests(unittest.TestCase):
    """US0370 / CR0365: an acceptance criterion CORRECTED during delivery is recorded as an AC
    DEFECT, distinct from an ordinary revision. Counting it as a normal edit hides the most
    expensive class of defect this project has found (US0375's AC specified the independence-gate
    bypass, and a passing test defended it)."""

    def _story(self, root: Path, rows: str) -> Path:
        p = root / "US0375.md"
        p.write_text(
            "# US0375: the sign-off gate ignores a superseded row\n\n"
            "## Acceptance Criteria\n\n### AC1\n\n- **Then** ...\n\n"
            "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            + rows, encoding="utf-8")
        return p

    def test_an_amended_criterion_is_recorded_as_an_ac_defect(self):
        mod = _load()
        # the amendment US0375 actually carried: the criterion was found wrong and corrected
        self.assertEqual(
            mod.classify_revision("AC1 corrected: it specified the wrong behaviour "
                                  "(ignoring a superseded row is the gate bypass)"),
            mod.AC_DEFECT)
        # an explicit tag is honoured directly
        self.assertEqual(mod.classify_revision("AC-DEFECT: amended criterion AC2"), mod.AC_DEFECT)
        # an ordinary revision touching a criterion is NOT an AC defect
        self.assertEqual(mod.classify_revision("Reworded AC1 for clarity"),
                         mod.ORDINARY_REVISION)
        self.assertEqual(mod.classify_revision("Added AC3 for the empty case"),
                         mod.ORDINARY_REVISION)
        self.assertEqual(mod.classify_revision("Created via `new` (deterministic)"),
                         mod.ORDINARY_REVISION)
        # a trivial correction is not the expensive class
        self.assertEqual(mod.classify_revision("Corrected a typo in AC1"),
                         mod.ORDINARY_REVISION)
        # the two classes are distinct labels, so a caller cannot conflate them
        self.assertNotEqual(mod.AC_DEFECT, mod.ORDINARY_REVISION)

        # and the story-level reader separates the AC defect from the ordinary rows beside it
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = self._story(root, (
                "| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |\n"
                "| 2026-07-23 | builder | Reworded AC1 for clarity |\n"
                "| 2026-07-24 | builder | AC1 corrected: it specified the wrong behaviour, "
                "amended the criterion |\n"))
            defects = mod.ac_defects(story)
            self.assertEqual(len(defects), 1)
            self.assertEqual(defects[0]["class"], mod.AC_DEFECT)
            self.assertEqual(defects[0]["author"], "builder")
            self.assertIn("wrong behaviour", defects[0]["change"])
            # the same via text is equivalent to the path
            self.assertEqual(mod.ac_defects(story.read_text()), defects)

    def test_a_story_with_no_amendment_has_no_ac_defect(self):
        # an absence is a different fact from a negative result: no amendment != a defect found
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = self._story(root, "| 2026-07-23 | sdlc-studio | Created via `new` |\n")
            self.assertEqual(mod.ac_defects(story), [])

    def test_rows_outside_the_revision_history_are_ignored(self):
        # a correction phrase in the body (not the history table) must not be counted
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "US0001.md"
            p.write_text(
                "# US0001\n\n## Acceptance Criteria\n\n"
                "| Date | Author | Change |\n| --- | --- | --- |\n"
                "| 2026-07-24 | x | AC1 corrected: specified the wrong behaviour |\n\n"
                "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                "| 2026-07-23 | sdlc | Created via `new` |\n", encoding="utf-8")
            self.assertEqual(mod.ac_defects(p), [])


class CallerNamedTests(unittest.TestCase):
    """A criterion for a mechanism names the CALLER that consumes it.

    Four mechanisms shipped in one sprint reaching nothing - a hash whose digest could never
    match, a selection computed by one hook and ignored by the one that runs the tests, a
    consumer whose producer did not exist. Each had passing tests and a green gate, because
    every criterion described the function's own behaviour and nothing asked what would call
    it. The check reads the criteria at authoring time, when the answer is a sentence.
    """

    def _unit(self, root: Path, num: int, affects: str, acs: str) -> Path:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"US{num:04d}-x.md"
        p.write_text(f"# US{num:04d}: a unit\n\n> **Status:** Ready\n"
                     f"> **Affects:** {affects}\n> **Points:** 3\n\n"
                     f"## Acceptance Criteria\n\n{acs}", encoding="utf-8")
        return p

    def _file(self, root: Path, rel: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# marker\n", encoding="utf-8")

    def test_a_mechanism_with_no_named_caller_is_reported(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._file(root, "src/thing.py")
            self._file(root, "tests/test_thing.py")
            self._unit(root, 1, "src/thing.py, tests/test_thing.py",
                       "### AC1: the helper returns the digest\n\n"
                       "- **Given** a payload\n- **When** the helper runs\n"
                       "- **Then** it returns the digest\n"
                       "- **Verify:** pytest tests/test_thing.py::T::t\n")
            findings = mod.caller_findings(root, ["US0001"])
            self.assertEqual([f["unit"] for f in findings], ["US0001"])
            self.assertEqual(findings[0]["kind"], mod.CALLER_UNNAMED)
            self.assertIn("AC1", findings[0]["criteria"],
                          "the finding must NAME the criterion that describes a function with "
                          "no consumer, not just the unit")
            self.assertIn("AC1", findings[0]["detail"])
            # the negative control: a check that fires on everything is not a check. A unit
            # whose declared surface is documentation adds no mechanism, so it is not asked
            # for a consumer.
            self._file(root, "reference-x.md")
            self._unit(root, 2, "reference-x.md",
                       "### AC1: the reference states it\n\n- **Then** it is stated\n"
                       "- **Verify:** file reference-x.md\n")
            self.assertEqual(mod.caller_findings(root, ["US0002"]), [])

    def test_the_named_caller_must_resolve(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._file(root, "src/thing.py")
            self._file(root, "tests/test_thing.py")
            self._file(root, "tools/hooks/pre-commit")
            resolving = ("### AC1: the pre-commit hook consumes the digest\n\n"
                         "- **Then** the hook refuses a stale digest\n"
                         "- **Verify:** pytest tests/test_thing.py::T::t\n"
                         "- **Caller:** the commit gate (tools/hooks/pre-commit)\n")
            self._unit(root, 3, "src/thing.py, tests/test_thing.py", resolving)
            self.assertEqual(mod.caller_findings(root, ["US0003"]), [],
                             "a criterion naming a caller that exists satisfies the check")
            # naming a caller that is nowhere in the tree is not a way past it: the whole
            # failure being caught is a mechanism whose consumer does not exist
            self._unit(root, 4, "src/thing.py, tests/test_thing.py",
                       resolving.replace("tools/hooks/pre-commit", "tools/hooks/nightly-sweep"))
            findings = mod.caller_findings(root, ["US0004"])
            self.assertEqual([f["kind"] for f in findings], [mod.CALLER_UNRESOLVED])
            self.assertIn("nightly-sweep", findings[0]["detail"])
            self.assertIn("AC1", findings[0]["criteria"])
            # an unreadable tree is not a tree in which nothing resolves: a scan that answered
            # nothing must say so rather than fail every caller it was asked about
            empty = root / "nothing-here"
            empty.mkdir()
            with self.assertRaises(ValueError):
                mod.tree_index(empty)


class CallerResolverAtScaleTests(unittest.TestCase):
    """A negative control on a four-file tree cannot judge a resolver whose failure mode is a
    LARGE tree. Against this repository the original accepted `unknown`, `nothing at all` and
    `the main loop` - the rule was satisfiable by a word naming no consumer at all."""

    @classmethod
    def setUpClass(cls):
        cls.critic = _load()
        cls.index = cls.critic.tree_index(REPO_ROOT)

    def test_nonsense_declarations_do_not_resolve_against_this_repo(self):
        for junk in ("unknown", "n/a", "nothing at all", "the main loop", "the gate",
                     "the review", "the index", "the story", "none", "tbd"):
            self.assertFalse(self.critic.caller_resolves(self.index, junk),
                             f"{junk!r} names no consumer and must not satisfy the rule")

    def test_real_callers_still_resolve_against_this_repo(self):
        for real in (".githooks/pre-commit", "scripts/sprint.py", "gate.py",
                     ".claude/skills/sdlc-studio/scripts/verify_ac.py"):
            self.assertTrue(self.critic.caller_resolves(self.index, real),
                            f"{real!r} is a real caller and must resolve")

    def test_the_index_holds_only_tracked_files(self):
        self.assertFalse([p for p in self.index["paths"] if p.startswith("node_modules/")],
                         "a vendored tree turns the index into an English vocabulary")

    def test_an_index_that_found_nothing_refuses_rather_than_failing_everything(self):
        with tempfile.TemporaryDirectory() as d:
            c = _load()
            with self.assertRaises(ValueError):
                c.tree_index(d)

    def test_a_caller_named_as_a_symbol_resolves(self):
        """The repair that killed the nonsense-word hole required a path-shaped token, which
        made a caller named as a FUNCTION unverifiable. Every declaration in the lane stories
        names its consumer that way - `cmd_lane -> lane_dispatch` - and each passed only
        because an unrelated documentation filename sat on the same line. A rule satisfied by
        a token nobody meant as the caller is the theatre this class exists to refuse."""
        for sym in ("cmd_lane", "lane_dispatch", "lane_contract", "lane_verify", "build_plan"):
            self.assertTrue(self.critic.caller_resolves(self.index, sym),
                            f"{sym!r} is a real function in a tracked file and must resolve")

    def test_a_symbol_declaration_resolves_without_an_incidental_path_token(self):
        decl = "`sprint lane brief` (cmd_lane -> lane_dispatch -> lane_contract)"
        self.assertTrue(self.critic.caller_resolves(self.index, decl),
                        "the declaration names a real call chain and must resolve on it")

    def test_prose_words_are_not_rescued_by_the_symbol_index(self):
        """Widening to symbols must not reopen the hole it sits beside."""
        for junk in ("unknown", "nothing at all", "the main loop", "none", "tbd",
                     "future work", "to be decided", "see above"):
            self.assertFalse(self.critic.caller_resolves(self.index, junk),
                             f"{junk!r} names no consumer and must not satisfy the rule")


class CallerIndeterminateTests(unittest.TestCase):
    """BG0379. `mechanism_files` subtracts every Affects path a unit's own verifiers name, so a
    unit whose criterion points at a shell verifier INVOKING its only code file has an empty
    surface - and `caller_findings` then skipped it entirely. The check exited 0 whether the
    Caller declaration said something, said nothing, or was deleted: vacuous, which is the
    exact defect the check was built to remove, reintroduced by a repair to it."""

    def _unit(self, root: Path, ident: str, affects: str, verify: str, caller: str = "") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        line = f"- **Caller:** {caller}\n" if caller else ""
        (d / f"{ident}-x.md").write_text(
            f"# {ident}: x\n\n> **Status:** Review\n> **Affects:** {affects}\n\n"
            f"## Acceptance Criteria\n\n### AC1: it works\n\n{line}"
            f"- **Verify:** {verify}\n", encoding="utf-8")

    def test_a_surface_emptied_by_its_own_verifier_is_reported_not_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001", "src/thing.py", "shell python3 src/thing.py --check")
            kinds = [f["kind"] for f in _load().caller_findings(root, ["US0001"])]
            self.assertIn(_load().CALLER_INDETERMINATE, kinds)

    def test_a_documentation_only_unit_is_still_not_asked_for_a_caller(self) -> None:
        """The carve-out must not widen: a unit whose declared surface is markdown adds no
        mechanism and a check that fires on everything is not a check."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0002", "docs/guide.md", "grep -n x docs/guide.md")
            self.assertEqual(_load().caller_findings(root, ["US0002"]), [])

    def test_a_unit_with_a_real_surface_is_judged_as_before(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0003", "src/thing.py, tests/test_thing.py",
                       "pytest tests/test_thing.py::T::t")
            kinds = [f["kind"] for f in _load().caller_findings(root, ["US0003"])]
            self.assertIn(_load().CALLER_UNNAMED, kinds)
            self.assertNotIn(_load().CALLER_INDETERMINATE, kinds)

    def test_the_verdict_changes_when_the_declaration_does(self) -> None:
        """The property that was missing. Before the fix, deleting the Caller declaration left
        the check at exit 0 - so its greenness said nothing about the unit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0004", "src/thing.py, tests/test_thing.py",
                       "pytest tests/test_thing.py::T::t", caller="src/consumer.py")
            with_decl = _load().caller_findings(root, ["US0004"])
            self._unit(root, "US0004", "src/thing.py, tests/test_thing.py",
                       "pytest tests/test_thing.py::T::t")
            without = _load().caller_findings(root, ["US0004"])
            self.assertNotEqual([f["kind"] for f in with_decl], [f["kind"] for f in without])


class ReviewDurationTests(unittest.TestCase):
    """US0534. No round recorded a duration, so `_component_review` could only measure the span
    BETWEEN round stamps - nothing before the first round, and zero for rounds stamped together
    at close. A review that took hours read as unmeasured while the ratio treated it as free."""

    def test_a_recorded_round_carries_its_duration(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            _load().run_state.open_run(root, batch=["US0001"], goal="x")
            entry = _load().run_state.record_review_round(
                root, verdict="REJECT", units=["US0001"], reviewer="qa",
                started_at="2026-07-28T10:00:00Z", ended_at="2026-07-28T10:22:30Z")
            self.assertEqual(_load().run_state.round_duration(entry), 1350)

    def test_an_untimed_round_reads_unmeasured_not_zero(self) -> None:
        """The distinction the whole field exists for: a round nobody timed must not be folded
        to zero, because the ratio computes delivery by subtraction and a silent zero reports
        the review as having cost nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            _load().run_state.open_run(root, batch=["US0001"], goal="x")
            entry = _load().run_state.record_review_round(root, verdict="APPROVE", units=["US0001"],
                                                  reviewer="qa")
            self.assertIsNone(_load().run_state.round_duration(entry))
            self.assertIsNot(entry["seconds"], 0)

    def test_an_unparseable_stamp_is_unmeasured_rather_than_invented(self) -> None:
        self.assertIsNone(_load().run_state._elapsed_seconds("nonsense", "2026-07-28T10:00:00Z"))
        self.assertIsNone(_load().run_state._elapsed_seconds("2026-07-28T10:00:00Z", None))

    def test_a_measured_zero_is_kept_as_a_measurement(self) -> None:
        """Zero seconds is a legitimate reading; only UNMEASURED means nobody looked."""
        self.assertEqual(_load().run_state.round_duration({"seconds": 0}), 0)


class GoalPanelTests(unittest.TestCase):
    """US0542. The Sprint Goal verdict was recorded by whoever ran the close - which, on an
    author-run sprint, is the author. The two-role rule protects every unit's sign-off and
    left the goal judgement itself unprotected."""

    CLAUSES = ["seams have owners", "the goal is judged clause by clause"]

    def test_a_panel_including_the_author_is_refused(self) -> None:
        with self.assertRaises(ValueError) as caught:
            _load().goal_panel(".", self.CLAUSES, ["qa", "builder"], "builder")
        self.assertIn("author", str(caught.exception))

    def test_a_panel_excluding_the_author_returns_a_verdict_per_clause(self) -> None:
        r = _load().goal_panel(".", self.CLAUSES, ["qa", "product"], "builder",
                              {"seams have owners": {"qa": {"verdict": "achieved",
                                                            "evidence": "US0538 passes"},
                                                     "product": "achieved"},
                               "the goal is judged clause by clause":
                                   {"qa": "missed", "product": "missed"}})
        self.assertEqual([c["verdict"] for c in r["clauses"]], ["achieved", "missed"])
        self.assertEqual(r["verdict"], "partial")

    def test_a_clause_carries_the_evidence_the_panel_relied_on(self) -> None:
        r = _load().goal_panel(".", ["one clause"], ["qa"], "builder",
                              {"one clause": {"qa": {"verdict": "achieved",
                                                     "evidence": "the fixture reproduces"}}})
        self.assertEqual(r["clauses"][0]["evidence"], ["the fixture reproduces"])

    def test_disagreement_is_partial_rather_than_the_majority_word(self) -> None:
        """A clause one seat says was missed is not achieved because two others disagree -
        reporting the majority would let a dissent vanish into a number."""
        r = _load().goal_panel(".", ["one clause"], ["a", "b", "c"], "builder",
                              {"one clause": {"a": "achieved", "b": "achieved", "c": "missed"}})
        self.assertEqual(r["clauses"][0]["verdict"], "partial")

    def test_an_unknown_verdict_word_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            _load().goal_panel(".", ["one clause"], ["qa"], "builder",
                              {"one clause": {"qa": "mostly"}})

    def test_an_empty_panel_or_no_clauses_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            _load().goal_panel(".", ["one clause"], [], "builder")
        with self.assertRaises(ValueError):
            _load().goal_panel(".", [], ["qa"], "builder")


class _BatchBase(unittest.TestCase):
    """A workspace with an open run, so `--from-run` has a batch to read."""

    UNITS = ("US0001", "US0002", "US0003")

    def setUp(self) -> None:
        self.mod = _load()
        self.root = Path(tempfile.mkdtemp(prefix="critic_batch_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        (self.root / "sdlc-studio" / "reviews").mkdir(parents=True)
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-BATCH", "batch": list(self.UNITS), "outcome": "running"}),
            encoding="utf-8")

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.mod.main([*argv, "--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()


class BatchFormTests(_BatchBase):
    """US0556. Recording the evidence, the verdict and the sign-off for nineteen units took
    fifty-seven invocations of this script - each paying interpreter start, imports and a
    read-modify-write to record one line. Thirty-eight of them were spent discovering a
    required argument, one unit at a time."""

    def test_each_verb_records_every_named_unit_in_one_invocation(self) -> None:
        rc, out, err = self._run(["evidence", "--units", "US0001,US0002,US0003",
                                  "--reviewer", "qa", "--author", "builder",
                                  "--findings", "probed the boundary"])
        self.assertEqual(0, rc, err)
        for unit in self.UNITS:
            self.assertIsNotNone(self.mod.evidence_for(self.root, unit), f"{unit} unrecorded")
        rc, _, err = self._run(["record", "--brief", "abcdef123456",
                                "--units", "US0001,US0002,US0003",
                                "--verdict", "approve", "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)
        for unit in self.UNITS:
            self.assertEqual("APPROVE", self.mod.verdict_for(self.root, unit)["verdict"])
        rc, _, err = self._run(["signoff", "--units", "US0001,US0002,US0003",
                                "--principal", "operator", "--author", "builder"])
        self.assertEqual(0, rc, err)
        for unit in self.UNITS:
            self.assertIsNotNone(self.mod.signoff_for(self.root, unit), f"{unit} unsigned")

    def test_the_open_run_is_the_default_scope_and_an_absent_batch_is_refused(self) -> None:
        rc, _, err = self._run(["record", "--brief", "abcdef123456",
                                "--from-run", "--verdict", "approve",
                                "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)
        for unit in self.UNITS:
            self.assertEqual("APPROVE", self.mod.verdict_for(self.root, unit)["verdict"])
        (self.root / "sdlc-studio" / ".local" / "run-state.json").unlink()
        rc, _, err = self._run(["record", "--brief", "abcdef123456",
                                "--from-run", "--verdict", "approve",
                                "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(2, rc, "no open batch must refuse, never default to acting on nothing")
        self.assertIn("no open run", err.lower())

    def test_every_supplied_id_is_acted_on_and_the_count_is_reported(self) -> None:
        """BG0386's class: a repeated flag that silently keeps the last value reports a clean
        batch having looked at one unit. Both spellings must accumulate, and the count the
        command reports is the count it acted on."""
        rc, out, err = self._run(["record", "--brief", "abcdef123456",
                                  "--unit", "US0001", "--unit", "US0002",
                                  "--units", "US0003", "--verdict", "approve",
                                  "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)
        for unit in self.UNITS:
            self.assertIsNotNone(self.mod.verdict_for(self.root, unit),
                                 f"{unit} was supplied and silently dropped")
        self.assertIn("3", out, "the count acted on is reported, not assumed")

    def test_a_partial_failure_names_the_units_written_and_exits_non_zero(self) -> None:
        """A batch that half-succeeded and reported success is worse than one that never ran:
        the caller reruns nothing and the gap is invisible."""
        real = self.mod.record_verdict

        def explode(root, unit, *a, **kw):
            if sdlc_md_norm(unit) == "US0002":
                raise ValueError("US0002 is unwritable")
            return real(root, unit, *a, **kw)

        self.mod.record_verdict = explode
        self.addCleanup(setattr, self.mod, "record_verdict", real)
        rc, out, err = self._run(["record", "--brief", "abcdef123456",
                                  "--units", "US0001,US0002,US0003",
                                  "--verdict", "approve", "--reviewer", "qa",
                                  "--author", "builder"])
        self.assertNotEqual(0, rc, "a partial batch must never exit zero")
        combined = out + err
        self.assertIn("US0002", combined, "the failing unit is named")
        self.assertIn("US0001", combined, "so is what WAS written")

    def test_the_single_unit_form_is_unchanged(self) -> None:
        rc, out, err = self._run(["record", "--brief", "abcdef123456",
                                  "--unit", "US0001", "--verdict", "approve",
                                  "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)
        self.assertEqual("APPROVE", self.mod.verdict_for(self.root, "US0001")["verdict"])
        self.assertIsNone(self.mod.verdict_for(self.root, "US0002"),
                          "one named unit means one unit")


class UnansweredPanelTests(unittest.TestCase):
    """BG0393. `goal_panel` raises on an empty seat list precisely because "an empty panel
    returns a verdict nobody gave" - and then returned `partial` for a panel where no seat
    answered a single clause, which is the same verdict nobody gave by a different route.
    Worse, verdicts were keyed by the stripped clause text, so a key differing by case or a
    trailing space dropped a seat's `missed` without a word and it became `partial`."""

    def test_a_panel_nobody_answered_returns_no_verdict(self) -> None:
        mod = _load()
        panel = mod.goal_panel(".", ["c1", "c2"], ["qa", "arch"], "author")
        self.assertIsNone(panel["verdict"], "a verdict nobody gave was reported as partial")
        self.assertTrue(all(c["verdict"] is None for c in panel["clauses"]))
        self.assertEqual(["qa", "arch"], panel["clauses"][0]["unanswered"])

    def test_a_partly_answered_panel_still_reports(self) -> None:
        """The discriminating half: silence on one clause must not blank a real verdict."""
        mod = _load()
        panel = mod.goal_panel(".", ["c1", "c2"], ["qa"], "author",
                               verdicts={"c1": {"qa": "achieved"}})
        self.assertEqual("partial", panel["verdict"])
        self.assertEqual("achieved", panel["clauses"][0]["verdict"])
        self.assertIsNone(panel["clauses"][1]["verdict"])

    def test_a_verdict_key_matching_no_clause_is_refused(self) -> None:
        mod = _load()
        with self.assertRaises(ValueError) as caught:
            mod.goal_panel(".", ["c1"], ["qa"], "author", verdicts={"C1 ": {"qa": "missed"}})
        self.assertIn("match no clause", str(caught.exception))

    def test_a_unanimous_panel_still_reports_its_verdict(self) -> None:
        mod = _load()
        panel = mod.goal_panel(".", ["c1"], ["qa", "arch"], "author",
                               verdicts={"c1": {"qa": "missed", "arch": "missed"}})
        self.assertEqual("missed", panel["verdict"])


class BlockingPriorityFloorTests(unittest.TestCase):
    """BG0387. The floor was the literal tuple `p0/p1/critical/blocker`. This corpus files 104
    `Severity: High` bugs and 168 `Priority: High` CRs against 2 Critical and 13 P1, and an
    adversarial reviewer writes `major` - so the floor that exists to block a close on a defect
    a release cannot carry never fired once on the words this project uses."""

    def test_a_high_severity_defect_blocks_against_this_repos_own_vocabulary(self) -> None:
        mod = _load()
        ruling = mod.judge_defects_against_goal(
            [{"id": "BG0370", "severity": "High"}], ["every seam has an owner"])
        self.assertEqual(["BG0370"], [d["id"] for d in ruling["blocking"]])

    def test_major_is_the_same_tier_as_high(self) -> None:
        """The reviewer's word and the filer's word are one severity. An ordering that ranks
        them makes the cut depend on which one somebody happened to type."""
        mod = _load()
        ruling = mod.judge_defects_against_goal([{"id": "X", "priority": "Major"}], ["a clause"])
        self.assertEqual(["X"], [d["id"] for d in ruling["blocking"]])

    def test_a_decorated_value_is_normalised_before_comparing(self) -> None:
        """`**High**` compared raw is a value that never matches - half of why it never fired."""
        mod = _load()
        for raw in ("**High**", " High (severity) ", "P1", "Sev-1", "high"):
            with self.subTest(raw=raw):
                ruling = mod.judge_defects_against_goal([{"id": "X", "severity": raw}], ["c"])
                self.assertEqual(["X"], [d["id"] for d in ruling["blocking"]], raw)

    def test_below_the_cut_is_still_leavable_and_recorded(self) -> None:
        """The discriminating half - a floor that blocks everything is not a floor, and a
        leavable defect must still be recorded rather than dropped."""
        mod = _load()
        ruling = mod.judge_defects_against_goal(
            [{"id": "Y", "severity": "Low"}, {"id": "Z", "severity": "Medium"}], ["c"])
        self.assertEqual([], ruling["blocking"])
        self.assertEqual(["Y", "Z"], [d["id"] for d in ruling["leavable"]])
        self.assertTrue(all(d["why"] for d in ruling["leavable"]), "each records its reasoning")

    def test_the_floor_is_derived_from_one_cut_not_an_enumerated_list(self) -> None:
        """AC2. Every blocking word comes from the tiers at or above the cut, so a project
        changes ONE value rather than keeping a list in step with its own vocabulary."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  blocking_priority: critical\n", encoding="utf-8")
            strict = mod.blocking_priorities(root)
        self.assertIn("critical", strict)
        self.assertNotIn("high", strict, "raising the cut must narrow the floor")
        default = mod.blocking_priorities(None)
        self.assertIn("high", default)
        self.assertTrue(set(strict) < set(default), "the cut orders the tiers")

    def test_an_unrecognised_cut_falls_back_rather_than_emptying_the_floor(self) -> None:
        """A floor nobody configured must not silently become no floor at all."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  blocking_priority: urgent-ish\n", encoding="utf-8")
            self.assertEqual(mod.blocking_priorities(None), mod.blocking_priorities(root))

    def test_every_tier_word_is_reachable_by_some_cut(self) -> None:
        """The tiers ARE the vocabulary, so a word nobody can select is a word that silently
        means nothing - the enumeration failure this replaced, in a new shape."""
        mod = _load()
        for tier in mod.PRIORITY_TIERS:
            for word in tier:
                with self.subTest(word=word):
                    self.assertIn(word, mod.PRIORITY_ORDER)


class CallerCheckBatchTests(_BatchBase):
    """BG0386. `caller-check` declared `--unit` with a bare `nargs="+"`, so a REPEATED
    `--unit A --unit B` kept only B and argparse said nothing: the command answered about one
    unit while the caller believed it had answered about the batch. That is not hypothetical -
    it produced a `caller-unnamed 5 -> 0` that reached a retro and two commit messages before
    the library call was checked and showed 17 of 23."""

    def _units_with_findings(self) -> None:
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        for uid in self.UNITS:
            (self.root / "sdlc-studio" / "stories" / f"{uid}-mechanism.md").write_text(
                f"# {uid}: adds a mechanism\n\n> **Status:** Review\n"
                f"> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py\n\n"
                "## Acceptance Criteria\n\n### AC1: the function behaves\n\n"
                "- **Then** the function returns the right value\n", encoding="utf-8")

    def test_a_repeated_unit_flag_checks_every_named_unit(self) -> None:
        self._units_with_findings()
        rc, out, err = self._run(["caller-check", "--unit", "US0001", "--unit", "US0002"])
        self.assertEqual(1, rc, "findings mean a non-zero exit")
        for uid in ("US0001", "US0002"):
            self.assertIn(uid, out + err,
                          f"{uid} was named on the command line and silently dropped")

    def test_the_command_states_how_many_units_it_checked(self) -> None:
        """A clean result must name the scope it is clean over. The count is the one thing that
        would have shown, at the moment it was read, that the answer covered a single unit."""
        self._units_with_findings()
        _rc, out, _err = self._run(["caller-check", "--unit", "US0001", "--unit", "US0002"])
        self.assertIn("over 2 unit(s)", out)

    def test_the_open_run_is_available_as_a_batch_form(self) -> None:
        self._units_with_findings()
        rc, out, err = self._run(["caller-check", "--from-run"])
        self.assertIn(f"over {len(self.UNITS)} unit(s)", out,
                      f"the open run's batch was not read: {err}")
        self.assertNotEqual(2, rc)

    def test_several_ids_after_one_flag_still_work(self) -> None:
        """The spelling the bare `nargs="+"` supported. Fixing the repeat must not break it."""
        self._units_with_findings()
        _rc, out, _err = self._run(["caller-check", "--unit", "US0001", "US0002", "US0003"])
        self.assertIn("over 3 unit(s)", out)


class GhostIdsAreRefusedTests(_BatchBase):
    """A verdict may not be written against an id nothing resolves.

    `caller-check` and `refine seams` both refuse an unresolvable id, for the stated reason
    that a silent skip ships a smaller tranche than approved. The verb that writes the
    COMMITTED REVIEW LEDGER did not: `critic record --units US9998,US9999` wrote two verdicts
    for artefacts that do not exist and exited 0."""

    def _with_tree(self) -> None:
        d = self.root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / "US0001-real.md").write_text("# US0001: real\n\n> **Status:** Review\n",
                                          encoding="utf-8")

    def test_a_verdict_for_a_nonexistent_id_is_refused(self) -> None:
        self._with_tree()
        rc, out, err = self._run(["record", "--brief", "abcdef123456",
                                  "--units", "US9998,US9999", "--verdict", "approve",
                                  "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(2, rc, "two verdicts were written for artefacts that do not exist")
        self.assertIn("US9998", err)
        self.assertIsNone(self.mod.verdict_for(self.root, "US9998"))

    def test_one_bad_id_refuses_the_whole_batch_before_any_write(self) -> None:
        """A partial batch is the state the exit codes exist to distinguish; here nothing
        should be written at all, because the caller's list is wrong."""
        self._with_tree()
        rc, _out, err = self._run(["record", "--brief", "abcdef123456",
                                   "--units", "US0001,US9999", "--verdict", "approve",
                                   "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(2, rc)
        self.assertIn("US9999", err)
        self.assertIsNone(self.mod.verdict_for(self.root, "US0001"),
                          "a good id in a bad batch was written anyway")

    def test_a_resolvable_id_is_still_recorded(self) -> None:
        self._with_tree()
        rc, _out, err = self._run(["record", "--brief", "abcdef123456",
                                   "--unit", "US0001", "--verdict", "approve",
                                   "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)
        self.assertEqual("APPROVE", self.mod.verdict_for(self.root, "US0001")["verdict"])

    def test_a_workspace_that_cannot_resolve_is_not_refused(self) -> None:
        """Fail-open only on an UNANSWERABLE question. A root with no artefact tree resolves
        nothing, so refusing there would fail on the absence of a workspace rather than on a
        wrong id - the distinction `close_owed` draws between an absent and a corrupt
        baseline."""
        rc, _out, err = self._run(["record", "--brief", "abcdef123456",
                                   "--unit", "US0001", "--verdict", "approve",
                                   "--reviewer", "qa", "--author", "builder"])
        self.assertEqual(0, rc, err)


class ArgumentCompletenessTests(_BatchBase):
    """US0557. `critic signoff` needs `--author` and `close --apply-signoff` needs
    `--principal`; both were learned from a refusal, and the first cost nineteen spawns before
    the message was read. A refusal has to arrive once, before anything is written, naming
    everything the command needs."""

    def test_a_missing_argument_refuses_before_any_unit_is_written(self) -> None:
        rc, _, err = self._run(["signoff", "--units", "US0001,US0002,US0003",
                                "--principal", "operator"])
        self.assertEqual(2, rc, err)
        for unit in self.UNITS:
            self.assertIsNone(self.mod.signoff_for(self.root, unit),
                              f"{unit} was written despite the refusal")

    def test_the_refusal_names_every_missing_argument(self) -> None:
        rc, _, err = self._run(["signoff", "--units", "US0001,US0002"])
        self.assertEqual(2, rc)
        self.assertIn("--principal", err)
        self.assertIn("--author", err,
                      "naming only the first missing argument costs a second round-trip")

    def test_every_named_argument_is_one_the_parser_accepts(self) -> None:
        """A message that sends a caller to a flag the command does not have is a round-trip
        that ends in a second refusal. Checked against the parser, not against a list."""
        import argparse
        import re as _re
        parser = self.mod.build_parser() if hasattr(self.mod, "build_parser") else None
        self.assertIsNotNone(parser, "the parser must be reachable to be held to its messages")
        accepted: dict[str, set[str]] = {}
        for action in parser._subparsers._group_actions:      # noqa: SLF001 - the only route in
            for verb, sub in action.choices.items():
                accepted[verb] = {opt for a in sub._actions for opt in a.option_strings}  # noqa: SLF001
        for verb in ("record", "evidence", "signoff"):
            for missing in ([], ["--units", "US0001"]):
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                        contextlib.suppress(SystemExit):
                    self.mod.main([verb, *missing, "--root", str(self.root)])
                for flag in set(_re.findall(r"--[a-z][a-z-]*", out.getvalue() + err.getvalue())):
                    with self.subTest(verb=verb, flag=flag):
                        self.assertIn(flag, accepted[verb],
                                      f"{verb} names {flag}, which its parser does not accept")


class ASignoffSkipsAUnitThatDeliveredNothingTests(unittest.TestCase):
    """BG0406's tooling half. `critic signoff --from-run` takes the run's APPROVED BATCH as its
    scope and wrote a row for every id in it without consulting status. Closing RUN-01KYNKDP
    wrote three such rows: two bugs reopened precisely because they delivered nothing, and a
    story reverted to Blocked. The note was batch-scoped so it stated no falsehood about those
    units - but the ROW reads as approval of work that does not exist, which is the same defect
    as a status asserting a repair that did not happen."""

    def _repo(self, status: str):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0001-a-bug.md").write_text(
            f"# BG0001: a bug\n\n> **Status:** {status}\n> **Severity:** Medium\n",
            encoding="utf-8")
        return root

    def _story_repo(self, status: str):
        """A STORY, because that is the type whose vocabulary holds `Review`. The first version
        of this test used a bug - which has no Review status - so `_unit_status` returned
        "cannot say" and the test passed however the rule behaved. It survived the mutant that
        restored the deadlock."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            f"# US0001: x\n\n> **Status:** {status}\n\n"
            f"## Acceptance Criteria\n\n- [ ] something\n", encoding="utf-8")
        return root

    def test_a_unit_AWAITING_signoff_is_eligible(self) -> None:
        """The deadlock an independent reviewer found. The first version skipped every
        NON-TERMINAL unit - and `Review` is exactly where this repo's two-role rule HOLDS a unit
        until the sign-off lands. Skipping it there meant only an already-terminal unit could be
        signed off, inverting the gate into retrospective paperwork."""
        mod = _load()
        root = self._story_repo("Review")
        state = mod._unit_status(root, "US0001")
        self.assertEqual("Review", state["status"], "the fixture's status was not read at all")
        self.assertFalse(state["terminal"], "Review must be non-terminal for this to bite")
        self.assertIsNone(mod._signoff_withheld(root, "US0001"),
                          "a story at Review was refused the sign-off that moves it to Done")

    def test_an_undelivered_STORY_is_still_withheld(self) -> None:
        """The other side, on the same type - so eligibility is about the STATUS and not about
        the type happening to lack a review state."""
        mod = _load()
        root = self._story_repo("Ready")
        why = mod._signoff_withheld(root, "US0001")
        self.assertIsNotNone(why, "a story at Ready took a sign-off row")
        self.assertIn("not been delivered", why)

    def test_a_skip_is_reflected_in_the_exit_code(self) -> None:
        """The false clean an independent reviewer found: the skip was named on stderr while the
        summary printed "N unit(s) written" with rc 0 over a record holding fewer. The batch
        contract's own docstring says acting on nothing and reporting success is a false clean."""
        import argparse
        import contextlib
        import io
        mod = _load()
        root = self._story_repo("Ready")
        args = argparse.Namespace(root=root, unit=["US0001"], units=None, from_run=False,
                                  principal="Operator", author="agent", delegate=None,
                                  boundary=None, note="n", fields_file=None, format="text")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = mod.cmd_signoff(args)
        self.assertNotEqual(0, rc,
                            "every unit was skipped and the command still reported success")
        self.assertIn("SKIPPED", err.getvalue())

    def test_an_undelivered_unit_is_withheld_and_named(self) -> None:
        mod = _load()
        # Statuses the BUG vocabulary actually holds. `Ready` is a story status, so a bug
        # carrying it reads as "cannot say" - which is correct, and not what this asserts.
        for status in ("Open", "In Progress"):
            root = self._repo(status)
            why = mod._signoff_withheld(root, "BG0001")
            self.assertIsNotNone(why, f"{status!r} took a sign-off row")
            self.assertIn("not been delivered", why)

    def test_a_retracted_delivery_is_withheld_whatever_its_status(self) -> None:
        """The original defect, and the real signal for it: a reopen RETRACTS the evidence, so
        the unit delivered nothing however its status now reads."""
        mod = _load()
        root = self._repo("Fixed")
        p = root / "sdlc-studio" / "bugs" / "BG0001-a-bug.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "> **Severity:** Medium",
            "> **Severity:** Medium\n> **Verification depth:** RETRACTED on reopen (was: "
            "functional) - re-verify"), encoding="utf-8")
        why = mod._signoff_withheld(root, "BG0001")
        self.assertIsNotNone(why, "a retracted delivery took a sign-off row")
        self.assertIn("RETRACTED", why)

    def test_a_non_terminal_unit_is_skipped_and_named(self) -> None:
        root = self._repo("Open")
        state = _load()._unit_status(root, "BG0001")
        self.assertEqual(state["status"], "Open")
        self.assertFalse(state["terminal"])

    def test_a_terminal_unit_is_not_skipped(self) -> None:
        """The positive control: skipping the non-terminal must not skip everything, or the
        sign-off verb stops working and the guard reads as a clean run."""
        root = self._repo("Fixed")
        state = _load()._unit_status(root, "BG0001")
        self.assertTrue(state["terminal"])

    def test_an_unreadable_unit_says_it_cannot_say(self) -> None:
        """None means "cannot say", and the caller proceeds. Refusing a sign-off because a file
        could not be read would make the status check more important than the sign-off."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.assertIsNone(_load()._unit_status(Path(td.name), "BG9999"))


class BriefProvenanceTests(unittest.TestCase):
    """US0577: a verdict carries the provenance of the brief the seat was given.

    RUN-01KYX375 measured both ends of this. Four review prompts were hand-written while
    `critic.py brief` ships the bounded diff scope, the criteria as law and the claim-inventory
    pass; they returned eight sprawling repo-wide findings. The same units re-reviewed from the
    shipped brief returned one precise finding each with zero pre-existing noise. Nothing in the
    record distinguished the two, so the sprint could not tell a properly briefed review from an
    invented one.

    Each test names the mutant it must fail on, per LL0050.
    """

    def _unit(self, root: Path, uid: str = "US0001") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
            f"### AC1: it behaves\n\n- **Then** it behaves\n", encoding="utf-8")
        # `brief` resolves a seat CARD, so a fixture without one cannot exercise it at all.
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True, exist_ok=True)
        for role in ("engineering", "qa", "product"):
            (seats / f"{role}.md").write_text(
                f"<!-- role: {role} -->\n# A {role} seat\n\n## Lens\n\nJudge as {role}.\n",
                encoding="utf-8")

    def test_a_verdict_records_the_brief_it_was_given(self) -> None:
        """MUTANT: drop the fingerprint from the recorded row. This must go red - without it a
        hand-written prompt and a tool-issued brief are indistinguishable in the record."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            fp = critic.brief_fingerprint(critic.brief(root, "US0001", "engineering"))
            critic.record_verdict(root, "US0001", "APPROVE", reviewer="a seat",
                                  author="the author", brief=fp)
            row = critic.verdict_for(root, "US0001")
        self.assertTrue(row, "no verdict was recorded")
        self.assertEqual(fp, row.get("brief"), "the verdict does not carry its brief")

    def test_the_fingerprint_identifies_the_brief(self) -> None:
        """MUTANT: return a constant fingerprint. This must go red, or the field records that
        SOME brief existed rather than WHICH, and a stale or wrong brief passes as the right one."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            eng = critic.brief_fingerprint(critic.brief(root, "US0001", "engineering"))
            qa = critic.brief_fingerprint(critic.brief(root, "US0001", "qa"))
        self.assertNotEqual(eng, qa, "two different briefs share one fingerprint")
        self.assertTrue(eng and qa, "a brief fingerprints to nothing")

    def test_a_hand_written_prompt_records_no_provenance(self) -> None:
        """MUTANT: default the field to a plausible-looking value. This must go red.

        An absent brief must be visibly absent. A field filled in for a caller that never asked
        the tool is worse than an empty one, because it asserts a discipline nobody followed."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            critic.record_verdict(root, "US0001", "APPROVE", reviewer="a seat",
                                  author="the author")
            row = critic.verdict_for(root, "US0001")
        self.assertFalse(row.get("brief") and row["brief"] != "-",
                         "an unbriefed verdict records a fingerprint it never had")

    def test_the_fingerprint_is_stable_across_calls(self) -> None:
        """MUTANT: seed the fingerprint with the clock or a random value. This must go red - a
        fingerprint that changes between two identical briefs can never be compared, so the
        field would be decorative."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            a = critic.brief_fingerprint(critic.brief(root, "US0001", "engineering"))
            b = critic.brief_fingerprint(critic.brief(root, "US0001", "engineering"))
        self.assertEqual(a, b)

    def test_a_pre_brief_log_is_widened_rather_than_broken(self) -> None:
        """MUTANT: drop the `_ensure_brief_column` call from record_verdict.

        The header is written once, at creation, so an existing log keeps six columns while new
        rows carry seven - not a valid markdown table, and markdownlint MD056 then refuses the
        commit. This is the defect that actually blocked a commit, so it is pinned on the SHAPE
        of the file rather than on the exception: every row must have the same cell count as the
        header, and the pre-existing verdict must still read back with its recorded values.
        """
        critic = _load()
        from lib.sdlc_md import table_cells
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001")
            path = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Critic verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Issues |\n"
                "| --- | --- | --- | --- | --- | --- |\n"
                "| US0001 | APPROVE | ada | grace | 2026-01-01 | none |\n",
                encoding="utf-8")
            critic.record_verdict(root, "US0002", "REJECT", "ada", "grace",
                                  issues="one", brief="abc123def456")
            lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                     if l.startswith("| ") and not set(l.strip()) <= set("|-: ")]
        header = table_cells(lines[0])
        self.assertIn("Brief", header, "the header was not widened for the new column")
        for row in lines[1:]:
            self.assertEqual(
                len(header), len(table_cells(row)),
                f"row has a different cell count from the header, which is an invalid table:\n{row}")
        old_row = next(r for r in lines if r.startswith("| US0001 "))
        cells = table_cells(old_row)
        self.assertEqual(["US0001", "APPROVE", "ada", "grace", "2026-01-01"], cells[:5],
                         "the pre-existing verdict's recorded values did not survive widening")
        self.assertEqual("-", cells[5],
                         "a verdict predating the column should record an ABSENT brief")

    def _record(self, root, extra=()):
        critic = _load()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = critic.main(["record", "--unit", "US0001", "--verdict", "approve",
                              "--reviewer", "ada", "--author", "grace",
                              "--root", str(root), *extra])
        return rc, buf_out.getvalue() + buf_err.getvalue()

    def test_a_verdict_without_provenance_is_refused(self) -> None:
        """MUTANT: delete the `if required: return 2` branch in cmd_record.

        The seat-brief rule is doctrine everywhere else in this repo, and doctrine is what got
        skipped - a review round was run from four hand-written prompts while the shipped brief
        existed. A rule that matters is refused by the command people actually run (LL0027).
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001")
            rc, out = self._record(root)
        self.assertEqual(2, rc, "a verdict with no brief provenance was recorded")
        self.assertIn("critic.py brief", out,
                      "the refusal does not name the command that produces a brief")
        self.assertIn("--seat", out,
                      "the refusal does not show the seat the brief needs")

    def test_a_briefed_verdict_records_cleanly(self) -> None:
        """The positive control. MUTANT: make the refusal unconditional.

        A gate that refuses everything discriminates no better than one that refuses nothing,
        so the passing case is half the contract."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001")
            rc, out = self._record(root, ("--brief", "abc123def456"))
            recorded = (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").read_text(
                encoding="utf-8")
        self.assertEqual(0, rc, f"a briefed verdict was refused:\n{out}")
        self.assertIn("abc123def456", recorded,
                      "the fingerprint the reviewer supplied was not recorded")

    def test_the_stand_down_is_stated_not_silent(self) -> None:
        """MUTANT: drop the NOTE, or honour the config without saying so.

        Switching the rule off and forgetting it are different events, and a record that cannot
        tell them apart is the one that lets the second masquerade as the first."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "US0001")
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  require_brief_provenance: false\n", encoding="utf-8")
            rc, out = self._record(root)
        self.assertEqual(0, rc, f"a recorded stand-down did not take effect:\n{out}")
        self.assertIn("require_brief_provenance", out,
                      "the stand-down was honoured silently - nothing on the output says the "
                      "requirement was switched off rather than met")


class FindingClassTests(unittest.TestCase):
    """The ORIGIN axis: did THIS unit's diff cause the finding?

    Held apart from the existing `class` axis (FRESH / REPAIR_REGRESSION), which asks a
    different question - whether a round-N finding is a regression in round N-1's REPAIR. The
    word "regression" appears on both and means different things, so a test here that could
    pass by reading `class` would be pinning the wrong axis.
    """

    def _unit(self, root: Path, uid: str = "US0001") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
            f"### AC1: it behaves\n\n- **Then** it behaves\n", encoding="utf-8")

    def _record(self, root, issues):
        critic = _load()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = critic.main(["record", "--unit", "US0001", "--verdict", "reject",
                              "--brief", "abcdef123456", "--reviewer", "ada",
                              "--author", "grace", "--issues", issues, "--root", str(root)])
        return rc, buf_out.getvalue() + buf_err.getvalue()

    def test_a_classification_survives_the_round_trip(self) -> None:
        """MUTANT: drop the origin tag when parsing, or fold it into the text.

        Also asserts the `class` axis is untouched, because merging the two is the specific
        mistake an engineering seat flagged at goal review."""
        critic = _load()
        issues = ("[regression] verify_ac crashes on an empty Affects; "
                  "[pre-existing] BG0123 the gate is slow")
        parsed = critic.parse_findings(issues)
        self.assertEqual([critic.ORIGIN_REGRESSION, critic.ORIGIN_PRE_EXISTING],
                         [f["origin"] for f in parsed],
                         "the declared origins did not survive parsing")
        self.assertEqual("verify_ac crashes on an empty Affects", parsed[0]["text"],
                         "the tag was left in the finding text")
        self.assertNotIn("class", parsed[0],
                         "the origin axis wrote onto the `class` axis - they answer different "
                         "questions and merging them was the flagged mistake")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            rc, out = self._record(root, issues)
            recorded = (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").read_text(
                encoding="utf-8")
        self.assertEqual(0, rc, f"a fully classified verdict was refused:\n{out}")
        self.assertIn("[regression]", recorded, "the origin was not recorded")
        self.assertIn("[pre-existing]", recorded, "the origin was not recorded")

    def test_an_unclassified_finding_is_refused(self) -> None:
        """MUTANT: delete the `unclassified_findings` refusal from cmd_record."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            rc, out = self._record(root, "[regression] a real one; the gate feels slow")
        self.assertEqual(2, rc, "a verdict carrying an unsorted finding was recorded")
        self.assertIn("the gate feels slow", out,
                      "the refusal does not name WHICH finding is unclassified")

    def test_a_clean_pass_needs_no_classification(self) -> None:
        """The control. MUTANT: refuse whenever there are no classified findings.

        A rule satisfiable by refusing every clean APPROVE discriminates nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            rc, out = self._record(root, "none blocking")
        self.assertEqual(0, rc, f"a clean pass was refused for carrying no findings:\n{out}")


class ReviewRepairTests(unittest.TestCase):
    """The five findings an independent seat raised against EP0194's own delivery.

    Four of them were prose or provenance defects rather than broken logic, which is the shape
    this whole epic exists to catch - and one of them, F1, was a false claim shipped inside it.
    """

    def _unit(self, root: Path, uid: str = "US0001") -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n"
            f"### AC1: it behaves\n\n- **Then** it behaves\n", encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True, exist_ok=True)
        for role in ("engineering", "qa", "product"):
            (seats / f"{role}.md").write_text(
                f"<!-- role: {role} -->\n# A {role} seat\n\n## Lens\n\nJudge as {role}.\n",
                encoding="utf-8")

    def test_the_brief_command_emits_the_fingerprint(self) -> None:
        """F1. MUTANT: stop printing the fingerprint from cmd_brief.

        `brief_fingerprint` was called from ONE site - the `--brief-file` branch of record -
        and never from the command that ISSUES a brief. So the fingerprint was reachable only
        from the library, while the changelog and the commit message both said `critic.py
        brief` emitted it. AC1's own test computed it in-process, which is a library test and
        cannot see that the LANE is missing. This runs the CLI.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = critic.main(["brief", "--unit", "US0001", "--seat", "engineering",
                                  "--root", str(root)])
            err, out = buf_err.getvalue(), buf_out.getvalue()
        self.assertEqual(0, rc, f"brief refused:\n{err}")
        expected = critic.brief_fingerprint(out.rstrip("\n"))
        self.assertIn(expected, err,
                      "the command that issues a brief does not emit its fingerprint, so "
                      "nothing a reviewer can run produces the value `record` demands")
        self.assertIn("--brief", err,
                      "the fingerprint is printed without saying what to do with it")

    def test_a_made_up_brief_value_is_refused(self) -> None:
        """F2. MUTANT: delete the _FINGERPRINT_RE check in cmd_record.

        `--brief x` was accepted, so the provenance gate was satisfied by inventing a value -
        recording provenance for a prompt that was never issued, which is precisely what the
        field exists to make detectable."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = critic.main(["record", "--unit", "US0001", "--verdict", "approve",
                                  "--reviewer", "ada", "--author", "grace",
                                  "--brief", "x", "--root", str(root)])
            err = buf_err.getvalue() + buf_out.getvalue()
        self.assertEqual(2, rc, "a value that is not a fingerprint was accepted as provenance")
        self.assertIn("hex", err, "the refusal does not say what a fingerprint looks like")

    def test_a_well_formed_fingerprint_is_accepted(self) -> None:
        """The control for the check above: a gate refusing every value discriminates nothing."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            buf_out, buf_err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                rc = critic.main(["record", "--unit", "US0001", "--verdict", "approve",
                                  "--reviewer", "ada", "--author", "grace",
                                  "--brief", "0123456789ab", "--root", str(root)])
            err = buf_err.getvalue() + buf_out.getvalue()
        self.assertEqual(0, rc, f"a well-formed fingerprint was refused:\n{err}")

    def test_an_untagged_finding_does_not_cover_a_unit(self) -> None:
        """F4. MUTANT: delete the `any(f["origin"] != ORIGIN_PRE_EXISTING)` guard.

        Deleting that one line left the ENTIRE suite green, and every historical REJECT row in
        the shipped log carries untagged findings (they predate US0579). So the mutant would
        have started covering real units at the Done gate with nothing going red. The
        behaviour was correct and the cover was absent, which is the same risk as a defect
        one edit away.
        """
        critic = _load()
        untagged = {"verdict": "REJECT", "reviewer": "ada", "author": "grace",
                    "issues": "FAIL-OPEN IN THE COVERAGE GATE ITSELF; a second untagged note"}
        mixed = {"verdict": "REJECT", "reviewer": "ada", "author": "grace",
                 "issues": "[pre-existing] BG0123 slow gate; an untagged one"}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertFalse(
                critic.sprint_covers_independently(root, "US0001", untagged),
                "a REJECT whose findings are all UNTAGGED covered the unit - untagged is not "
                "the same as pre-existing, and treating it so is a fail-open")
            self.assertFalse(
                critic.sprint_covers_independently(root, "US0001", mixed),
                "one untagged finding beside a pre-existing one still covered the unit")
            self.assertTrue(
                critic.sprint_covers_independently(
                    root, "US0001", {**mixed, "issues": "[pre-existing] BG0123 slow gate"}),
                "the control failed: an all-pre-existing REJECT must still cover")

    def test_the_coverage_docstring_states_both_shapes(self) -> None:
        """F5. MUTANT: revert the docstring to "an APPROVE whose reviewer and author...".

        The docstring was TRUE at the base ref and this diff falsified it, inside the unit's
        own declared Affects. The claim-drift lane shipped in the sibling epic fired on
        neither this nor the parallel comment in sprint.py, so a guard is warranted rather
        than a promise to remember.
        """
        critic = _load()
        doc = critic.sprint_covers_independently.__doc__ or ""
        self.assertIn("pre-existing", doc,
                      "the docstring does not mention the REJECT shape that now also covers")
        self.assertIn("UNTAGGED", doc.upper(),
                      "the docstring does not say an untagged finding never qualifies")
        # All THREE sites, not just the one this test started with. The rule is restated in
        # two other modules, and pinning only the canonical copy leaves the same drift free to
        # recur in the places it actually recurred - which is the whole reason a second copy
        # of a rule is a liability. Flagged by the confirmation pass; cheap, so closed here.
        scripts = Path(__file__).resolve().parent.parent
        for rel, needle in (("sprint.py", "sprint_covers_independently` is THE predicate"),
                            ("carry_forward.py", "sprint_covers_independently`")):
            text = (scripts / rel).read_text(encoding="utf-8")
            i = text.find(needle)
            self.assertGreater(i, 0, f"{rel} no longer restates the coverage rule - if the "
                                     f"restatement was removed, remove it from this list too")
            passage = text[i:i + 600]
            self.assertIn("pre-existing", passage,
                          f"{rel} still describes coverage as APPROVE-only, which this diff "
                          f"falsified - the same drift the canonical docstring carried")


class SignoffPolicyTests(unittest.TestCase):
    """`review.signoff` decides who may satisfy the reviewer-of-record half.

    Default OPERATOR, always. A project that upgrades must not silently lose its human
    reviewer: the independence bar is the product's central claim, and a bar that moves
    without somebody deciding to move it is worth nothing.
    """

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            "> **Affects:** src/a.py\n", encoding="utf-8")
        # A BRIEFED adversarial verdict: the panel interlock refuses to ratify a review with
        # no provenance, so a fixture without one would be testing the interlock instead.
        _load().record_verdict(root, "US0001", "APPROVE", "qa seat", "author",
                               issues="none blocking", brief="abcdef123456")
        return root

    def test_the_default_is_operator(self) -> None:
        """MUTANT: default the policy to `panel`.

        Asserted on the POLICY READER and on the refusal, because a default that is only
        correct in the reader is not a default the gate honours.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            self.assertEqual("operator", critic.signoff_policy(root),
                             "a project with no setting did not default to operator")
            with self.assertRaises(ValueError) as caught:
                critic.record_signoff(root, "US0001", "Lena Marsh", "author",
                                      panel=["qa", "engineering"])
        self.assertIn("review.signoff", str(caught.exception),
                      "the refusal does not name the setting that would allow it")

    def test_panel_is_reached_only_by_explicit_config(self) -> None:
        """The control. MUTANT: refuse a panel sign-off regardless of config.

        A policy that can never be reached is not opt-in, it is absent.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  signoff: panel\n", encoding="utf-8")
            self.assertEqual("panel", critic.signoff_policy(root))
            path = critic.record_signoff(root, "US0001", "Lena Marsh", "author",
                                         panel=["qa", "engineering"])
            # Asserted INSIDE the block: the temp directory is gone by the time it exits, so
            # an exists() check outside is always False and would fail a working implementation.
            self.assertTrue(path.exists(), "a configured panel sign-off was not recorded")
            self.assertTrue(critic.is_panel_signoff(critic.signoff_for(root, "US0001")),
                            "the recorded row does not identify itself as a panel sign-off")


class SignoffProvenanceTests(unittest.TestCase):
    """Who accepted this must never become ambiguous.

    The product's claim is that its records mean something. A panel-signed unit and an
    operator-signed one are different facts about who took responsibility, and a reader months
    later cannot re-derive which it was.
    """

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            "> **Affects:** src/a.py\n", encoding="utf-8")
        (root / "sdlc-studio" / "stories" / "US0002-y.md").write_text(
            "# US0002: another\n\n> **Status:** Review\n> **Points:** 3\n"
            "> **Affects:** src/b.py\n", encoding="utf-8")
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  signoff: panel\n", encoding="utf-8")
        for uid in ("US0001", "US0002"):
            _load().record_verdict(root, uid, "APPROVE", "qa seat", "author",
                                   issues="none blocking", brief="abcdef123456")
        return root

    def test_panel_and_operator_rows_are_distinguishable(self) -> None:
        """MUTANT: record a panel sign-off with the same chain an operator's carries.

        Asserted in BOTH directions - the panel row must say panel, and the operator row must
        NOT - because a marker written onto every row distinguishes nothing.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            critic.record_signoff(root, "US0001", "Lena Marsh", "author",
                                  panel=["qa", "engineering"])
            critic.record_signoff(root, "US0002", "Darren Benson", "author")
            panel_row = critic.signoff_for(root, "US0001")
            operator_row = critic.signoff_for(root, "US0002")
        self.assertTrue(critic.is_panel_signoff(panel_row),
                        "a panel sign-off does not identify itself as one")
        self.assertFalse(critic.is_panel_signoff(operator_row),
                         "an operator sign-off is being read as a panel one")
        self.assertIn("qa", panel_row["chain"],
                      "the panel row does not name the seats that reviewed it")


class PanelInterlockTests(unittest.TestCase):
    """A panel may not ratify a review nobody can prove was properly briefed.

    Without this the panel LAUNDERS missing provenance instead of catching it: the sign-off
    half would be satisfied by seats whose adversarial half rested on a hand-written prompt
    carrying neither the charter, the bounded scope, nor the criteria as law.
    """

    def _root(self, d, brief="abcdef123456"):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            "> **Affects:** src/a.py\n", encoding="utf-8")
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  signoff: panel\n", encoding="utf-8")
        critic = _load()
        critic.record_verdict(root, "US0001", "APPROVE", "qa seat", "author",
                              issues="none blocking", brief=brief)
        return root

    def test_an_unbriefed_verdict_blocks_the_panel(self) -> None:
        """MUTANT: drop the provenance check from the panel path."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, brief="")
            with self.assertRaises(ValueError) as caught:
                critic.record_signoff(root, "US0001", "Lena Marsh", "author",
                                      panel=["qa", "engineering"])
            msg = str(caught.exception)
        self.assertIn("provenance", msg.lower(),
                      "the refusal does not say what is missing")
        self.assertIn("US0001", msg, "the refusal does not name the unit")

    def test_a_briefed_unit_signs_cleanly(self) -> None:
        """The control. MUTANT: refuse every panel sign-off regardless of provenance."""
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            path = critic.record_signoff(root, "US0001", "Lena Marsh", "author",
                                         panel=["qa", "engineering"])
            self.assertTrue(path.exists(), "a fully briefed unit was refused")

    def test_an_operator_signoff_is_not_subject_to_the_interlock(self) -> None:
        """A human principal reads the evidence themselves and can see it is unbriefed.

        MUTANT: apply the interlock to every sign-off. That would block the operator from
        signing off exactly the units they most need to look at, which is the opposite of
        human-in-the-lead.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, brief="")
            path = critic.record_signoff(root, "US0001", "Darren Benson", "author")
            self.assertTrue(path.exists(),
                            "an operator sign-off was blocked by the panel interlock")



class SkippedCountTests(unittest.TestCase):
    """BG0496: the printed count must equal what the RECORD holds.

    `signoff` over units in a non-signable status printed `14 unit(s) SKIPPED and NOT written`
    on stderr and `14 unit(s) written` on stdout, over a record holding zero rows. The skip path
    returns rather than raising, so the batch runner counted it as written. Exit code and stderr
    were already right, which is worse than both being wrong - the reader who trusts the
    headline is told the opposite of what happened (LL0008).
    """

    def _root(self, d, status="Ready"):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "reviews").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
            f"# US0001: a unit\n\n> **Status:** {status}\n> **Points:** 3\n"
            f"> **Affects:** src/a.py\n", encoding="utf-8")
        return root

    def test_the_printed_count_matches_the_record(self) -> None:
        """MUTANT: count a skipped unit as written (the shipped behaviour).

        Asserted against the RECORD, not against another number this test computes: the defect
        was precisely that two numbers in one output disagreed, so the file is the arbiter.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)                       # Ready: neither terminal nor awaiting
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = critic.main(["signoff", "--units", "US0001",
                                  "--principal", "Darren Benson", "--author", "an-author",
                                  "--note", "n", "--root", str(root)])
            out = buf.getvalue()
            record = root / "sdlc-studio" / "reviews" / "signoff-record.md"
            rows = record.read_text(encoding="utf-8").count("| US0001 |") if record.exists() else 0
        self.assertNotEqual(0, rc, "a wholly skipped batch reported success")
        self.assertEqual(0, rows, "control: the row should not have been written")
        self.assertIn("0 unit(s) written", out,
                      f"the printed count disagrees with the record, which holds {rows} row(s):"
                      f"\n{out}")

    def test_a_signable_unit_is_still_counted(self) -> None:
        """The control. MUTANT: subtract every unit, or report zero unconditionally.

        A count that always says zero agrees with an empty record and with nothing else.
        """
        critic = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, status="Review")      # awaiting the reviewer of record
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = critic.main(["signoff", "--units", "US0001",
                                  "--principal", "Darren Benson", "--author", "an-author",
                                  "--note", "n", "--root", str(root)])
            out = buf.getvalue()
            record = root / "sdlc-studio" / "reviews" / "signoff-record.md"
            rows = record.read_text(encoding="utf-8").count("| US0001 |")
        self.assertEqual(0, rc, f"a signable unit was refused:\n{out}")
        self.assertEqual(1, rows, "the sign-off row was not written")
        self.assertIn("1 unit(s) written", out, f"the count does not match the record:\n{out}")


def _rejected(mod, root, unit="US0017", issues="[new] alpha broke; [new] beta broke"):
    """A unit carrying a live REJECT with two itemised findings."""
    mod.record_verdict(root, unit, "REJECT", "qa-seat", "builder", issues, "delivery",
                       "abcdef123456")


def _bug_on_disk(root, bid="BG0123"):
    """A real artefact for a FILED closure to point at - the id has to RESOLVE."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{bid}-residue.md").write_text(
        f"# {bid}: the residue\n\n> **Status:** Open\n> **Points:** 1\n", encoding="utf-8")


class RepairRecordTests(unittest.TestCase):
    """US0620 / CR0506: a REJECT can be ANSWERED, beside the verdict rather than over it.

    `sprint_covers_independently` is satisfied only by an APPROVE, and no verb recorded what was
    done about a rejection - so a batch reviewed, rejected, repaired and mutation-verified read
    exactly like one nobody opened. This is the record the rest of the epic reads.
    """

    def test_a_repair_names_each_finding_it_closes_with_its_evidence(self) -> None:
        """MUTANT: accept a repair naming a finding the verdict never raised.

        A disposition that matches nothing is not a disposition, and without the check the route
        back to covered is opened by writing any text at all.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root)
            mod.record_repair(root, "US0017", "builder",
                              "alpha broke -> mutant re-applied and killed; "
                              "beta broke -> test now reddens")
            st = mod.repair_state(root, "US0017")
            self.assertEqual(st["state"], "complete")
            self.assertEqual(len(st["closed"]), 2)
            with self.assertRaises(ValueError) as caught:
                mod.record_repair(root, "US0017", "builder",
                                  "a finding nobody raised -> handwaving")
            self.assertIn("names no finding this verdict raised", str(caught.exception))

    def test_the_reject_survives_the_repair_byte_identically(self) -> None:
        """MUTANT: write the repair over the verdict row, or amend it.

        What the reviewer found stays true. A repair that replaced the verdict would destroy the
        only evidence the review happened - the failure this epic exists to END, arriving from
        the other side.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root)
            before = mod.verdicts_path(root).read_text(encoding="utf-8")
            mod.record_repair(root, "US0017", "builder",
                              "alpha broke -> killed; beta broke -> killed")
            after = mod.verdicts_path(root).read_text(encoding="utf-8")
        self.assertEqual(before, after, "the repair rewrote the verdict ledger")

    def test_an_unattributed_repair_is_refused(self) -> None:
        """MUTANT: default the author to the reviewer, or to empty.

        A repair is a claim about work somebody did, and an unattributed claim cannot be
        questioned - the same rule the verdict already holds.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root)
            with self.assertRaises(ValueError) as caught:
                mod.record_repair(root, "US0017", "", "alpha broke -> killed")
        self.assertIn("author", str(caught.exception))

    def test_a_repair_needs_a_live_reject_to_answer(self) -> None:
        """MUTANT: record a repair against any unit.

        A repair records what was done about a rejection, so there has to be one - otherwise the
        ledger fills with dispositions for findings nobody made.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod.record_verdict(root, "US0017", "APPROVE", "qa-seat", "builder", "none",
                               "delivery", "abcdef123456")
            with self.assertRaises(ValueError) as caught:
                mod.record_repair(root, "US0017", "builder", "alpha -> killed")
        self.assertIn("no live REJECT", str(caught.exception))

    def test_show_prints_the_repair_beside_the_verdict(self) -> None:
        """MUTANT: store the repair in a ledger the verdict's reader never consults.

        The whole value is that a reader of the verdict sees the disposition without knowing a
        second command exists. Driven through the shipped CLI - a library check cannot see a
        record the shipped reader never prints (LL0040).
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root)
            mod.record_repair(root, "US0017", "builder",
                              "alpha broke -> killed; beta broke -> killed")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["show", "--unit", "US0017", "--root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("repair", out.getvalue().lower(),
                      f"`show` does not mention the repair:\n{out.getvalue()}")


class ClosureResolutionTests(unittest.TestCase):
    """The rule that decides whether a rejected unit can reach the Done gate.

    THE REVIEW BYPASS. The first version matched bidirectional substring, so a closure of one
    character closed every finding: `repair --closed "e -> fixed"` through the shipped CLI marked
    a REJECT COMPLETE, flipped coverage to `repaired` and cleared the verdict half of the
    conformance gate - the exact thing `repair_state`'s own docstring says PARTIAL exists to
    prevent. And no test pinned the matching rule at all: swapping both substring tests for exact
    equality left the whole suite green, so the latitude was unchosen rather than designed.
    """

    def test_a_short_closure_cannot_close_every_finding(self) -> None:
        """MUTANT: match a closure against a finding by bidirectional substring.

        Driven through the shipped CLI, which is where the bypass was reachable.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0900")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = mod.main(["repair", "--unit", "US0900", "--author", "attacker",
                               "--closed", "e -> fixed", "--root", str(root)])
            self.assertNotEqual(rc, 0, "a one-character closure was accepted")
            self.assertEqual(mod.repair_state(root, "US0900")["state"], "none")
            self.assertEqual(mod.coverage_state(root, "US0900"), mod.COVERAGE_UNREVIEWED)

    def test_closing_a_short_finding_does_not_close_a_longer_one_containing_it(self) -> None:
        """MUTANT: the same substring rule, in reverse.

        Closing `the gate is slow` silently closed `the gate is slow and drops the last unit`,
        so the residue this record exists to name went unnamed.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0901",
                      "[new] the gate is slow; "
                      "[new] the gate is slow and drops the last unit silently")
            mod.record_repair(root, "US0901", "b", "#1 -> timed it, acceptable")
            st = mod.repair_state(root, "US0901")
        self.assertEqual(st["state"], "partial")
        self.assertEqual(len(st["outstanding"]), 1)
        self.assertIn("drops the last unit", st["outstanding"][0])

    def test_an_ambiguous_closure_is_refused_rather_than_guessed(self) -> None:
        """MUTANT: resolve a multi-match in the author's favour (take the first).

        Which finding a closure answers is not a coin toss, and resolving it silently is how the
        bypass reads as a feature.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0902",
                      "[new] the resolver is wrong about paths; "
                      "[new] the resolver is wrong about ids")
            with self.assertRaises(ValueError) as caught:
                mod.record_repair(root, "US0902", "b",
                                  "the resolver is wrong about -> looked at it")
        self.assertIn("prefix of 2", str(caught.exception))

    def test_an_ordinal_names_a_finding_exactly(self) -> None:
        """The positive control. MUTANT: refuse every closure.

        A rule that accepts nothing closes the route back to covered rather than gating it, so
        the refusal above must sit beside a form that works - and the ordinal is what the
        refusal message itself offers.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0903")
            mod.record_repair(root, "US0903", "b", "#1 -> killed; #2 -> killed")
            self.assertEqual(mod.repair_state(root, "US0903")["state"], "complete")

    def test_a_repair_does_not_answer_a_LATER_rejection(self) -> None:
        """MUTANT: read the latest repair regardless of which verdict it answers.

        `verdict_date` was recorded and read nowhere, so a round-one repair kept satisfying a
        later REJECT raising different findings - the unit reading `repaired` against findings
        nobody had answered.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0904", "[new] alpha broke")
            mod.record_repair(root, "US0904", "b", "#1 -> killed")
            self.assertEqual(mod.coverage_state(root, "US0904"), mod.COVERAGE_REPAIRED)
            # A FRESH rejection on a LATER day. The clock is patched rather than the ledger
            # rewritten, so the two rows differ the way two real rounds would.
            with unittest.mock.patch.object(mod.sdlc_md, "now_date", return_value="2099-12-31"):
                mod.record_verdict(root, "US0904", "REJECT", "qa-seat", "builder",
                                   "[new] a completely different defect", "delivery",
                                   "abcdef123456")
                state = mod.repair_state(root, "US0904")
        self.assertEqual(state["state"], "none",
                         "a repair answering an earlier rejection satisfied a later one")


class ThreeStateCoverageTests(unittest.TestCase):
    """US0621 / CR0506: approved, repaired and unreviewed are three states, not two."""

    def test_approved_repaired_and_unreviewed_are_three_distinct_states(self) -> None:
        """MUTANT: collapse `repaired` into either outer state.

        Reading it as unreviewed manufactures work; reading it as approved clears the gate on an
        unrepaired rejection. The defect this is filed from is the first.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod.record_verdict(root, "US0001", "APPROVE", "qa-seat", "builder", "none",
                               "delivery", "abcdef123456")
            _rejected(mod, root, "US0002")
            mod.record_repair(root, "US0002", "builder",
                              "alpha broke -> killed; beta broke -> killed")
            counts = mod.coverage_counts(root, ["US0001", "US0002", "US0003"])
        self.assertEqual(counts[mod.COVERAGE_APPROVED], ["US0001"])
        self.assertEqual(counts[mod.COVERAGE_REPAIRED], ["US0002"])
        self.assertEqual(counts[mod.COVERAGE_UNREVIEWED], ["US0003"])

    def test_an_unrepaired_or_partly_repaired_reject_stays_uncovered(self) -> None:
        """MUTANT: let any recorded repair reach `repaired`.

        That would convert every REJECT into an APPROVE for the cost of one command - a worse
        gate than the one being replaced.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0002")
            self.assertEqual(mod.coverage_state(root, "US0002"), mod.COVERAGE_UNREVIEWED)
            mod.record_repair(root, "US0002", "builder", "alpha broke -> killed")
            self.assertEqual(mod.coverage_state(root, "US0002"), mod.COVERAGE_UNREVIEWED,
                             "a PARTIAL repair reached the covered state")

    def test_the_gates_treatment_of_a_repaired_unit_is_declared_and_tested_both_ways(self) -> None:
        """MUTANT: let the gate answer this by accident of the APPROVE check.

        Whether a repaired unit satisfies the Done bar is a DECLARED rule with a test either
        way, so a future reader learns the answer from the code rather than from whichever
        branch happened to run. The declared answer: a COMPLETE repair satisfies the verdict
        half, a PARTIAL one does not.
        """
        mod = _load()
        import importlib.util as _u
        spec = _u.spec_from_file_location(
            "conformance", Path(__file__).resolve().parent.parent / "conformance.py")
        conf = _u.module_from_spec(spec)
        sys.modules["conformance"] = conf
        spec.loader.exec_module(conf)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US9002", "[new] alpha broke; [new] beta broke")
            partial_unmet = conf.critiqued_unmet(root, "US9002", 0, True, False)
            self.assertIn(conf.HALF_VERDICT, partial_unmet,
                          "an unrepaired REJECT satisfied the verdict half")
            mod.record_repair(root, "US9002", "builder",
                              "alpha broke -> killed; beta broke -> killed")
            complete_unmet = conf.critiqued_unmet(root, "US9002", 0, True, False)
        self.assertNotIn(conf.HALF_VERDICT, complete_unmet,
                         "a COMPLETE repair did not satisfy the verdict half, so the repaired "
                         "state reaches the gate as 'missing critiqued' after all")

    def test_the_three_counts_partition_the_batch(self) -> None:
        """MUTANT: let a unit fall through the classification into no count.

        Every unit falls in exactly one state and the total equals the batch size.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod.record_verdict(root, "US0001", "APPROVE", "qa", "b", "none", "delivery",
                               "abcdef123456")
            _rejected(mod, root, "US0002")
            units = ["US0001", "US0002", "US0003", "US0004"]
            counts = mod.coverage_counts(root, units)
        total = sum(len(v) for v in counts.values())
        self.assertEqual(total, len(units))
        self.assertEqual(sorted(sum(counts.values(), [])), sorted(units))


class PartialRepairTests(unittest.TestCase):
    """US0622 / CR0506: a repair that half-answers a rejection is PARTIAL and says which half."""

    def test_a_repair_covering_some_findings_is_partial_and_names_the_residue(self) -> None:
        """MUTANT: report a count instead of the outstanding findings."""
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0002",
                      "[new] alpha broke; [new] beta broke; [new] gamma broke")
            mod.record_repair(root, "US0002", "builder", "alpha broke -> killed")
            st = mod.repair_state(root, "US0002")
        self.assertEqual(st["state"], "partial")
        self.assertEqual(len(st["outstanding"]), 2)
        self.assertTrue(any("beta" in o for o in st["outstanding"]))
        self.assertTrue(any("gamma" in o for o in st["outstanding"]))

    def test_completeness_is_derived_per_finding_not_read_from_prose(self) -> None:
        """MUTANT: trust a repair that claims completeness in its own text.

        LL0015 - a guard that only catches the total case is not a guard.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0002", "[new] alpha broke; [new] beta broke")
            mod.record_repair(root, "US0002", "builder",
                              "alpha broke -> killed, and every finding is now closed")
            st = mod.repair_state(root, "US0002")
        self.assertEqual(st["state"], "partial",
                         "a repair claiming completeness in prose was believed")

    def test_a_repair_closing_every_finding_is_complete_and_counts_as_repaired(self) -> None:
        """The positive control. MUTANT: always report PARTIAL.

        PARTIAL must not be the only reachable answer, or the route back to covered is closed
        rather than gated.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0002", "[new] alpha broke; [new] beta broke")
            mod.record_repair(root, "US0002", "builder",
                              "alpha broke -> killed; beta broke -> killed")
            self.assertEqual(mod.repair_state(root, "US0002")["state"], "complete")
            self.assertEqual(mod.coverage_state(root, "US0002"), mod.COVERAGE_REPAIRED)


class FiledDispositionTests(unittest.TestCase):
    """US0623 / CR0506: closed by FILING is not the same as closed by fixing."""

    def test_a_filed_closure_records_the_disposition_and_the_id(self) -> None:
        """MUTANT: record every closure as a fix.

        Both dispositions are legitimate under the operator's rule; being unable to tell them
        apart afterwards is not.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug_on_disk(root)
            _rejected(mod, root, "US0002", "[new] alpha broke; [new] beta broke")
            mod.record_repair(root, "US0002", "builder",
                              "alpha broke -> killed by the re-applied mutant; "
                              "beta broke -> filed as BG0123")
            st = mod.repair_state(root, "US0002")
        self.assertEqual((st["fixed"], st["filed"]), (1, 1))
        filed = [c for c in st["closed"] if c["disposition"] == "filed"]
        self.assertEqual(filed[0]["artefact"], "BG0123")

    def test_a_filed_closure_with_an_unresolvable_id_is_refused(self) -> None:
        """MUTANT: accept any id in a FILED closure.

        A reference nobody can follow records the appearance of a disposition rather than one -
        the same failure shape as a `Verify:` line naming a test that does not exist, and found
        on the day it matters rather than the day it is written.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rejected(mod, root, "US0002", "[new] alpha broke; [new] beta broke")
            with self.assertRaises(ValueError) as caught:
                mod.record_repair(root, "US0002", "builder",
                                  "alpha broke -> killed; beta broke -> filed as BG9999")
        self.assertIn("BG9999", str(caught.exception))
        self.assertIn("resolves to no artefact", str(caught.exception))

    def test_fixed_and_filed_are_counted_separately(self) -> None:
        """MUTANT: report one combined `closed` total.

        A single total is the shape that makes deferral invisible, and EP0206's rule is only
        safe to enforce while the two can be told apart.
        """
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug_on_disk(root)
            _rejected(mod, root, "US0002", "[new] alpha broke; [new] beta broke")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                mod.main(["repair", "--unit", "US0002", "--author", "builder",
                          "--closed", "alpha broke -> killed; beta broke -> filed as BG0123",
                          "--root", str(root)])
        self.assertIn("1 fixed", out.getvalue())
        self.assertIn("1 filed", out.getvalue())



if __name__ == "__main__":
    unittest.main()

