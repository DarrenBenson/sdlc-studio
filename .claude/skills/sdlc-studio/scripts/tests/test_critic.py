"""Unit tests for critic.py - committed critic-verdict record (CR0023). RED first."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import shutil
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
             "ISSUES: minor thing at a.py:3; another note\n"
             "BLOCKING: none\n")

    def _record(self, root: Path, block: str) -> tuple[int, str]:
        mod = _load()
        f = root / "verdict.txt"
        f.write_text(block, encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = mod.main(["record", "--unit", "US0001", "--reviewer", "Sam seat",
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
                "BLOCKING: none", "BLOCKING: the big one at b.py:9"))
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            self.assertIn("BLOCKING: the big one", v["issues"])

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
            rc, _ = self._record(root, "verdict: reject\nissues: a real finding at a.py:3\n")
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            self.assertEqual(v["verdict"], "REJECT")
            self.assertIn("a real finding", v["issues"])

    def test_wrapped_issues_with_allcaps_word_not_truncated(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = self._record(root, "VERDICT: APPROVE\nISSUES: first line;\n"
                                       "NOTE: this continuation belongs to issues\n"
                                       "BLOCKING: none\n")
            self.assertEqual(rc, 0)
            v = _load().verdict_for(root, "US0001")
            self.assertIn("NOTE: this continuation", v["issues"])

    def test_echoed_contract_above_real_block_cannot_leak_placeholders(self) -> None:
        block = ("The contract I was given said:\n"
                 "VERDICT: APPROVE or REJECT\n"
                 "ISSUES: <semicolon-separated findings>\n"
                 "BLOCKING: <the subset>\n\n"
                 "VERDICT: REJECT\nISSUES: the actual finding\nBLOCKING: none\n")
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
                rc = mod.main(["record", "--unit", "US0001", "--reviewer", "Sam seat",
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
                rc = mod.main(["record", "--unit", "US0001", "--reviewer", "r",
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
            f.write_text("VERDICT: REJECT\nISSUES: off-by-one at flow.py:10\nBLOCKING: the off-by-one\n",
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

    def test_authoring_session_subagent_refused_as_delegate(self) -> None:
        # The seat subagent that reviewed for this unit is the author's own spawn -
        # naming it the delegate would hollow out the self-approval guard.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_evidence(root, "US0001", reviewer="qa-seat", author="builder",
                                findings="pass done")
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="operator", author="builder",
                                   delegate="qa-seat", boundary="another session")

    def test_verdict_reviewer_refused_as_delegate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="Sam seat", author="builder")
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="operator", author="builder",
                                   delegate="Sam seat", boundary="another session")

    def test_plan_review_phase_reviewer_refused_as_delegate(self) -> None:
        # The authoring-session set spans BOTH verdict phases: a subagent that only
        # reviewed the unit's plan (plan-review phase) is still the author's spawn.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.record_verdict(root, "US0001", "approve", reviewer="plan-seat",
                               author="builder", phase="plan-review")
            with self.assertRaises(ValueError):
                mod.record_signoff(root, "US0001", principal="operator", author="builder",
                                   delegate="plan-seat", boundary="another session")

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
             "ISSUES: vacuous killing test at test_x.py:10; docstring overclaims\n"
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
scripts/audit.py:88; the killing test did not fail.
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
            self.assertIn("scripts/audit.py:88", text)
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


class ReviewerBriefTests(unittest.TestCase):
    """US0318 (EP0108): the shipped reviewer brief carries the three standing practices, each
    with its reason, and a brief missing any is refused; reference-review.md documents them."""

    def _brief(self, mod, root: Path) -> str:
        _workspace(root)
        return mod.brief(root, "US0001", "qa")

    def test_a_brief_missing_any_of_the_three_practices_is_refused(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = self._brief(mod, root)
            # the shipped brief carries all three practices, each with its reason
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
                          "conclusion from it.")
            self.assertEqual(len(mod.missing_practices(reasonless)), 3,
                             "instructions with no reasons must all count as missing")
            # reference-review.md documents all three, so the shipped doc and the code agree
            doc = _norm(REFERENCE_REVIEW.read_text(encoding="utf-8"))
            for token in ("CLOSED", "OVER-CLAIMED", "MOVED", "author's TESTS", "isolation"):
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
        findings = ["audit.py:88 grep verb takes no flag",
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


if __name__ == "__main__":
    unittest.main()
