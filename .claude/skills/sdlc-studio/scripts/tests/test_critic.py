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


if __name__ == "__main__":
    unittest.main()

