"""Unit tests for conformance.py (RED first - the script does not exist yet).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import gitutil  # noqa: E402 - confined git for the fixture repos below

SCRIPT = Path(__file__).resolve().parent.parent / "conformance.py"


def _load():
    spec = importlib.util.spec_from_file_location("conformance", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conformance"] = mod
    spec.loader.exec_module(mod)
    return mod


def _story(root, num, *, epic=True, ac=True, verify=True, status="Ready", verified="yes"):
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# US{num:04d}: sample", "", f"> **Status:** {status}"]
    if epic:
        lines.append("> **Epic:** [EP0001: x](../epics/EP0001-x.md)")
    lines.append("")
    if ac:
        lines += ["## Acceptance Criteria", "", "### AC1: works", "- **Given** a thing"]
        if verify:
            lines.append("- **Verify:** shell echo ok")
        if status == "Done":
            lines.append(f"- **Verified:** {verified} (2026-01-01)")
    (d / f"US{num:04d}-sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _units(root):
    return {u["id"]: u for u in _load().detect_conformance(root)["units"]}


class StageTests(unittest.TestCase):
    def test_full_story_all_stages_true(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            u = _units(root)["US0001"]
            self.assertTrue(u["conformant"])
            self.assertEqual(u["missing"], [])
            self.assertTrue(all(u["stages"][s] for s in ("decomposed", "specified", "verifiable")))

    def test_missing_stage_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("decomposed", u["missing"])

    def test_draft_story_is_conformant_on_decomposed_alone(self) -> None:
        # CR0342: an ungroomed Draft story (a fresh refine output with placeholder ACs) needs only
        # `decomposed` - specified/verifiable are the Definition-of-Ready bar, required once it is
        # Ready+. So a large refined backlog does not read as non-conformant before it is groomed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Draft", ac=False, verify=False)
            u = _units(root)["US0001"]
            self.assertTrue(u["conformant"], u["missing"])
            self.assertEqual(u["missing"], [])

    def test_ready_story_still_requires_specified_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Ready", verify=False)
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("verifiable", u["missing"])

    def test_done_must_be_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="no")
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("verified", u["missing"])


def _record_verdict(root, unit, verdict="approve", reviewer="independent-critic", author="builder"):
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = m
    spec.loader.exec_module(m)
    # Independence floor (CR0117): the critic stage needs author != reviewer, so the helper
    # records distinct ids by default; self-review/missing-author cases are covered in test_critic.
    m.record_verdict(root, unit, verdict, reviewer=reviewer, author=author)


class SpecifiedStageTests(unittest.TestCase):
    def test_prose_bullet_ac_section_is_specified(self) -> None:
        # An AC section of prose bullets (no ACn id) still counts as specified.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n- New byModel strategy in group.ts\n- Unit-tested: counts match\n\n"
                "## Notes\n\nx\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertTrue(u["stages"]["specified"])

    def test_empty_ac_section_not_specified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n## Notes\n\nx\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])

    def test_placeholder_only_ac_not_specified_or_verifiable(self) -> None:
        # CR0056: a fresh scaffold whose AC/Verify slots are still {{...}} is NOT specified
        # and NOT verifiable - it cannot reach Done.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Draft\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: {{define}}\n\n- **Given** {{context}}\n"
                "- **When** {{action}}\n- **Then** {{outcome}}\n- **Verify:** {{check}}\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])
            self.assertFalse(u["stages"]["verifiable"])

    def test_one_real_ac_among_placeholders_is_specified(self) -> None:
        # A real Verify/AC line still counts even if a sibling slot is a placeholder.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: login works\n\n- **Given** a real precondition\n"
                "- **Verify:** pytest tests/test_login.py\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertTrue(u["stages"]["specified"])
            self.assertTrue(u["stages"]["verifiable"])


    def test_placeholder_with_trailing_punct_not_specified(self) -> None:
        # CR0056 (critic): `{{x}}.` is not real content - conformance must agree with validate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"; sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Draft\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: {{define}}.\n\n- **Verify:** {{check}}.\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertFalse(u["stages"]["specified"])
            self.assertFalse(u["stages"]["verifiable"])


class CritiqueStageTests(unittest.TestCase):
    def test_done_without_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")  # no critic verdict
            u = _units(root)["US0001"]
            self.assertFalse(u["conformant"])
            self.assertIn("critiqued", u["missing"])

    def test_done_with_approve_verdict_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            u = _units(root)["US0001"]
            self.assertNotIn("critiqued", u["missing"])
            self.assertTrue(u["stages"]["critiqued"])

    def test_done_with_reject_verdict_not_conformant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "reject")
            u = _units(root)["US0001"]
            self.assertIn("critiqued", u["missing"])  # unresolved REJECT

    def test_new_self_review_not_conformant(self) -> None:
        # CR0117: a NEW self-review (reviewer == author, no grandfather) never clears.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve", reviewer="dani", author="dani")
            u = _units(root)["US0001"]
            self.assertIn("critiqued", u["missing"])  # self-review blocked

    def test_pre_gate_unit_is_grandfathered(self) -> None:
        # A unit closed before the gate (PRE_GATE marker, prior risk-scaled policy)
        # is grandfathered conformant even though it is not real independence.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "critic", Path(__file__).resolve().parent.parent / "critic.py")
        critic = importlib.util.module_from_spec(spec); spec.loader.exec_module(critic)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve",
                            reviewer="self-review (light, docs)", author=critic.PRE_GATE)
            u = _units(root)["US0001"]
            self.assertNotIn("critiqued", u["missing"])  # grandfathered
            self.assertTrue(u["stages"]["critiqued"])


class ReconciledStageTests(unittest.TestCase):
    def test_done_with_index_drift_not_reconciled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")  # isolate the reconciled stage
            # index says Ready while the file says Done -> status-mismatch
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n"
                "| [US0001](US0001-sample.md) | sample | Ready |\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])
            self.assertFalse(u["stages"]["reconciled"])

    def test_done_absent_from_index_not_reconciled(self) -> None:
        # A Done story missing from the index (missing-row) is not reconciled.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verified="yes")
            _record_verdict(root, "US0001", "approve")
            (root / "sdlc-studio" / "stories" / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n", encoding="utf-8")
            u = _units(root)["US0001"]
            self.assertIn("reconciled", u["missing"])


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed_for_missing_stage(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False)  # missing decomposed
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["check", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("decomposed ->", out)


class CliTests(unittest.TestCase):
    def test_exit_and_shape(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1)
            _story(root, 2, epic=False)
            mod = _load()
            rc = mod.main(["check", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 1)  # US0002 is non-conformant
            data = mod.detect_conformance(root)
            self.assertIn("units", data)
            # `global_failures` (US0217) counts repo-wide failures attributed once rather
            # than charged to every unit; the gate adds it to `nonconformant` so that
            # reporting a failure differently never enforces less.
            self.assertEqual(set(data["summary"]),
                             {"total", "conformant", "nonconformant", "exempt", "ungroomed",
                              "global_failures", "judged", "advisory", "waived",
                              # A waiver no judged unit carries is still in force. This lane
                              # judges STORIES, so one scoped to a bug or a change request
                              # produced no line at all and sat silent.
                              "waived_unattributed"})


class WaiverInForceIsAlwaysReportedTests(unittest.TestCase):
    """BG0369. US0525 has the lane read recorded waivers and report a waived unit as waived,
    naming the decision. The report is built from this lane's UNITS, which are stories - so a
    waiver scoped to a bug or a change request emitted nothing at all and sat silently in
    force, which is the outcome the story exists to prevent."""

    def _repo(self, scope: str, status: str = "Draft") -> Path:
        d = Path(tempfile.mkdtemp(prefix="waiver_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        ws = d / "sdlc-studio"
        (ws / "stories").mkdir(parents=True)
        (ws / "stories" / "US0001-a-story.md").write_text(
            f"# US0001: a story\n\n> **Status:** {status}\n> **Epic:** EP0001\n",
            encoding="utf-8")
        (ws / "stories" / "_index.md").write_text(
            "# Story Index\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [US0001](US0001-a-story.md) | a story | {status} |\n", encoding="utf-8")
        # Six columns: `list_decisions` reads id, decision, rationale, status, supersedes, date.
        (ws / "decisions.md").write_text(
            "# Decisions\n\n| ID | Decision | Rationale | Status | Supersedes | Date |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            f"| D0001 | waiver: rule:conformance:verified{scope} | grandfathered | accepted "
            "| - | 2026-07-29 |\n", encoding="utf-8")
        return d

    def test_a_waiver_no_judged_unit_carries_is_reported(self) -> None:
        mod = _load()
        result = mod.detect_conformance(self._repo(":BG0042"))
        rows = result["waivers_unattributed"]
        self.assertTrue(rows, "a waiver scoped to a bug produced no report line at all")
        self.assertEqual("D0001", rows[0]["decision"])
        self.assertEqual(1, result["summary"]["waived_unattributed"])

    def test_the_report_names_it(self) -> None:
        import contextlib
        import io
        mod = _load()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            mod.main(["--root", str(self._repo(":BG0042")), "check"])
        printed = out.getvalue()
        self.assertIn("WAIVED verified", printed)
        self.assertIn("D0001", printed)
        self.assertIn("NOT carried by any unit this lane judges", printed)

    def test_a_waiver_a_judged_unit_does_carry_is_not_double_reported(self) -> None:
        """The discriminating half: a waiver already attributed per unit must not appear twice,
        or the new line becomes noise on every run and gets read past."""
        mod = _load()
        # DONE, not Draft. The lane judges delivered units, so a Draft fixture carried no
        # waiver at all - which is why the assertion below could sit behind a condition that
        # was never true and nobody noticed for a whole sprint.
        result = mod.detect_conformance(self._repo(":US0001", status="Done"))
        carried = [w for u in result["units"] for w in (u["waived"] or [])]
        # The POSITIVE CONTROL first. The only assertion used to sit behind `if carried:`,
        # which is False for this fixture - so the test iterated to nothing and passed however
        # the code behaved. An assertion guarded by a condition the fixture cannot meet is not
        # a guard; it is a comment that runs.
        self.assertTrue(carried,
                        "the fixture carries no per-unit waiver, so the discriminating "
                        "assertion below would never run")
        self.assertEqual([], result["waivers_unattributed"],
                         "a waiver reported per unit was reported unattributed as well")


try:
    import yaml as _yaml  # noqa: F401
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@unittest.skipUnless(HAS_YAML, "adopt_after reads .config.yaml (needs PyYAML)")
class AdoptCutoffTests(unittest.TestCase):
    """conformance.adopt_after exempts pre-adoption stories (CR0027)."""

    def _config(self, root: Path, body: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(body, encoding="utf-8")

    def test_pre_cutoff_story_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)   # would be non-conformant
            _story(root, 10, epic=False, ac=False)  # non-conformant, judged
            self._config(root, "conformance:\n  adopt_after: US0005\n")
            units = _units(root)
            self.assertTrue(units["US0001"]["exempt"])
            self.assertTrue(units["US0001"]["conformant"])   # exempt -> not failing
            self.assertEqual(units["US0001"]["missing"], [])
            self.assertFalse(units["US0010"]["exempt"])
            self.assertFalse(units["US0010"]["conformant"])  # still judged + failing
            summ = _load().detect_conformance(root)["summary"]
            self.assertEqual(summ["exempt"], 1)
            self.assertEqual(summ["nonconformant"], 1)

    def test_post_cutoff_story_is_still_judged(self) -> None:
        """The other half of the cutoff, asserted on its own selector (US0635).

        AC1's test carried both claims, so the exemption and the judgement shared one verifier
        and a regression in either failed both without saying which. This one asserts only that
        a story AT OR AFTER the cutoff is still judged, still non-conformant, and still counted
        as such - the direction that matters, because a cutoff that exempts everything is the
        failure a pre-cutoff assertion alone cannot see.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 10, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: US0005\n")
            units = _units(root)
            self.assertFalse(units["US0010"]["exempt"])
            self.assertFalse(units["US0010"]["conformant"])
            self.assertTrue(units["US0010"]["missing"],
                            "a judged non-conformant story named nothing missing")
            self.assertEqual(_load().detect_conformance(root)["summary"]["nonconformant"], 1)

    def test_no_cutoff_judges_all(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            self.assertFalse(_units(root)["US0001"]["exempt"])
            self.assertFalse(_units(root)["US0001"]["conformant"])

    def test_cmd_check_exits_zero_when_all_nonconformant_are_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)   # would fail, but exempt
            self._config(root, "conformance:\n  adopt_after: US0005\n")
            mod = _load()
            args = mod.build_parser().parse_args(["check", "--root", str(root)])
            self.assertEqual(args.func(args), 0)  # nothing judged-and-failing

    def test_bare_int_cutoff_now_exempts(self) -> None:
        # BG0039: a bare integer cutoff was silently dropped (id_number("5") -> None);
        # it must now exempt pre-cutoff stories exactly as the prefixed form does.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            _story(root, 10, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: 5\n")  # bare int
            units = _units(root)
            self.assertTrue(units["US0001"]["exempt"])
            self.assertFalse(units["US0010"]["exempt"])

    def test_boundary_id_itself_is_exempt(self) -> None:
        # BG0039: <= alignment - the cutoff id itself is grandfathered, not judged.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 5, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: 5\n")
            self.assertTrue(_units(root)["US0005"]["exempt"])

    def test_unparseable_cutoff_raises_not_silent(self) -> None:
        # LL0008: a typo'd cutoff must fail loud, NOT silently judge everything.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, epic=False, ac=False)
            self._config(root, "conformance:\n  adopt_after: oops\n")
            with self.assertRaises(ValueError):
                _load().detect_conformance(root)


def _critic_mod():
    spec = importlib.util.spec_from_file_location("critic", SCRIPT.parent / "critic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["critic"] = m
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
class TwoRoleCritiquedTests(unittest.TestCase):
    """CR0323 / RFC0044: with review.two_role_after set, a Done unit past the cutoff
    clears `critiqued` only with adversarial EVIDENCE plus an independent SIGN-OFF -
    forward-only, so existing projects and pre-cutoff units keep today's behaviour."""

    def _config(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: US0100\n", encoding="utf-8")

    def test_verdict_alone_no_longer_clears_critiqued(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")           # independent APPROVE, old-style
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])
            self.assertIn("critiqued", u["missing"])

    def test_evidence_plus_signoff_clears_critiqued(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)",
                             author="builder")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_hand_edited_self_signoff_is_backstopped(self) -> None:
        # record_signoff refuses a self-sign-off; a hand-appended row walks round the
        # tool, so conformance re-checks independence from the recorded rows.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            path = c.signoff_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            text = path.read_text(encoding="utf-8").replace("| operator |", "| builder |")
            path.write_text(text, encoding="utf-8")   # hand-edit: principal == author
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_signoff_by_session_subagent_is_backstopped(self) -> None:
        # A sign-off whose principal is a recorded authoring-session reviewer id
        # (the seat subagent) must not clear the gate even if hand-recorded.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101", reviewer="qa-seat")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            path = c.signoff_path(root)
            text = path.read_text(encoding="utf-8").replace("| operator |", "| qa-seat |")
            path.write_text(text, encoding="utf-8")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_signoff_without_evidence_not_critiqued(self) -> None:
        # "critiqued requires BOTH": an independent sign-off with no adversarial
        # evidence row must not clear the stage (kills the drop-evidence mutant).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)",
                             author="builder")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])
            self.assertIn("critiqued", u["missing"])

    def test_cutoff_boundary_unit_keeps_old_rule(self) -> None:
        # The cutoff id itself is grandfathered (<= exempt, > judged) - a `>` -> `>=`
        # regression would retroactively gate the boundary unit.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 100, status="Done")          # == US0100 cutoff
            _record_verdict(root, "US0100")           # verdict alone suffices
            u = _units(root)["US0100"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_pre_cutoff_done_unit_keeps_old_rule(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 99, status="Done")           # <= US0100 cutoff
            _record_verdict(root, "US0099")           # verdict alone suffices
            u = _units(root)["US0099"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_no_config_keeps_old_rule_everywhere(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])


@unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
class SprintReviewCritiquedTests(unittest.TestCase):
    """US0247 / RFC0046 option B: a recorded sprint-level adversarial full-diff review satisfies
    the per-unit `critiqued` gate for the units in its range - both the verdict half (a covered
    unit needs no individual APPROVE) and the two-role evidence half - while a per-unit REJECT is
    still repaired per unit and the per-unit sign-off stays required."""

    def _config(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: US0100\n", encoding="utf-8")

    def test_sprint_review_clears_critiqued_for_covered_unit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")           # NO per-unit verdict
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="full-diff pass; none blocking")
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)", author="builder")
            u = _units(root)["US0101"]
            self.assertTrue(u["stages"]["critiqued"])

    def test_SprintReview_does_not_override_a_per_unit_reject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101", "reject")  # latest per-unit verdict is REJECT
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="range looks fine overall")
            c.record_signoff(root, "US0101", principal="operator", author="builder")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])   # REJECT repairs per unit
            self.assertIn("critiqued", u["missing"])

    def test_SprintReview_still_needs_the_per_unit_signoff(self) -> None:
        # The sprint pass is EVIDENCE, not the reviewer-of-record sign-off: a covered unit with no
        # sign-off does not clear the two-role gate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            c = _critic_mod()
            c.record_sprint_review(root, ["US0101"], reviewer="qa-seat", author="builder",
                                   verdict="APPROVE", findings="full-diff pass; none blocking")
            u = _units(root)["US0101"]
            self.assertFalse(u["stages"]["critiqued"])

    def test_SprintReview_refuses_self_review_and_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            c = _critic_mod()
            with self.assertRaises(ValueError):        # reviewer == author
                c.record_sprint_review(root, ["US0101"], reviewer="bob", author="bob",
                                       verdict="APPROVE", findings="x")
            with self.assertRaises(ValueError):        # empty findings
                c.record_sprint_review(root, ["US0101"], reviewer="qa", author="bob",
                                       verdict="APPROVE", findings="")
            with self.assertRaises(ValueError):        # no covered units
                c.record_sprint_review(root, [], reviewer="qa", author="bob",
                                       verdict="APPROVE", findings="x")


class GlobalAttributionTests(unittest.TestCase):
    """US0217: a repo-GLOBAL failure is one fact about the repo, not a defect in each unit.

    The `documented` stage is a repo-wide floor: one uncatalogued command failed it for
    every Done unit, so a single doc gap rendered as 118 non-conformant units - a true
    count of a misleading thing, which buried every genuine per-unit finding (L-0084).

    The report must attribute it once WITHOUT enforcing less: the gate still blocks, and
    the CLI still exits non-zero. Reporting better must never mean gating weaker."""

    def _conformant_done_repo(self, root, n=3, doc_ok=False):
        """n Done stories that are conformant except for the repo-wide doc floor.

        `doc_coverage` is a shared module object in sys.modules, so stubbing its `check`
        leaks into every later test in the process unless it is restored - patch and
        register the undo together so the two can never drift apart.
        """
        mod = _load()
        original = mod.doc_coverage.check
        self.addCleanup(setattr, mod.doc_coverage, "check", original)
        rows = []
        for i in range(1, n + 1):
            _story(root, i, status="Done", verified="yes")
            _record_verdict(root, f"US{i:04d}", "approve")
            rows.append(f"| [US{i:04d}](US{i:04d}-sample.md) | sample | Done |")
        (root / "sdlc-studio" / "stories" / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n" + "\n".join(rows) + "\n",
            encoding="utf-8")
        # The stub returns the module's REAL contract, findings included - a stub narrower
        # than the thing it stands in for tests a shape the caller never receives.
        findings = [] if doc_ok else [{"kind": "command-uncatalogued", "name": "widget",
                                       "blocking": True, "detail": "widget is uncatalogued"}]
        mod.doc_coverage.check = lambda _r: {"ok": doc_ok, "findings": findings,
                                             "applicable": True}
        return mod

    def test_global_failure_reported_once(self) -> None:
        """AC1: one entry in `globals`, and no unit charged with it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=3, doc_ok=False)
            result = mod.detect_conformance(root)
            docs = [g for g in result["globals"] if g["stage"] == "documented"]
            self.assertEqual(len(docs), 1)
            self.assertTrue(docs[0]["remedy"])
            for u in result["units"]:
                self.assertNotIn("documented", u["missing"])
            self.assertEqual(result["summary"]["nonconformant"], 0)

    def test_unit_records_global_separately(self) -> None:
        """AC2: nothing is hidden - it moves to `missing_global`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=2, doc_ok=False)
            for u in mod.detect_conformance(root)["units"]:
                self.assertIn("documented", u["missing_global"])
                self.assertFalse(u["stages"]["documented"])

    def test_global_failure_still_blocks(self) -> None:
        """AC3: the gate lane counts it and the CLI exits non-zero."""
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=3, doc_ok=False)
            result = mod.detect_conformance(root)
            self.assertEqual(result["summary"]["global_failures"], 1)
            # the gate's own arithmetic: per-unit + global, so it still fails
            self.assertGreater(
                result["summary"]["nonconformant"] + result["summary"]["global_failures"], 0)
            with redirect_stdout(io.StringIO()) as buf:
                rc = mod.main(["check", "--root", str(root)])
            self.assertEqual(rc, 1)
            self.assertIn("REPO-WIDE documented", buf.getvalue())

    def test_per_unit_gaps_unaffected(self) -> None:
        """AC4: with no repo-wide failure, per-unit reporting is exactly as before."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = self._conformant_done_repo(root, n=1, doc_ok=True)
            _story(root, 9, status="Done", verified="no")   # a genuine per-unit gap
            result = mod.detect_conformance(root)
            self.assertEqual(result["globals"], [])
            self.assertEqual(result["summary"]["global_failures"], 0)
            u9 = next(u for u in result["units"] if u["id"] == "US0009")
            self.assertIn("verified", u9["missing"])
            self.assertEqual(u9["missing_global"], [])


class StampResolutionTests(unittest.TestCase):
    """BG0256: conformance must not count a Done story verified on a dead pointer."""

    def test_a_done_story_stamped_against_a_selector_that_resolves_to_nothing_is_not_verified(self) -> None:
        """The two calls differ in ONE argument. Everything else - the stamps, the index, the
        drift set - is held identical, so the assertion cannot pass on some other stage's
        behaviour. Without that, a fixture with unrelated conformance gaps would report
        `verified: False` either way and the test would prove nothing."""
        conformance = _load()
        dead = conformance._done_stages(".", "US9001", ["yes", "yes"], False, set(), True,
                                        dead_stamps=1)
        live = conformance._done_stages(".", "US9001", ["yes", "yes"], False, set(), True,
                                        dead_stamps=0)
        self.assertFalse(dead[0], "a green resting on a selector that selects nothing counted as verified")
        self.assertTrue(live[0], "a live stamp stopped counting as verified - the sign is flipped")


class ReviewPolicyTests(unittest.TestCase):
    """US0332 AC2: under carry-forward a REJECT does not block the close."""

    def _mods(self):
        import importlib.util, sys
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        for name in ("carry_forward", "critic", "conformance"):
            spec = importlib.util.spec_from_file_location(name, base / f"{name}.py")
            m = importlib.util.module_from_spec(spec); sys.modules[name] = m
            spec.loader.exec_module(m)
        return sys.modules["conformance"], sys.modules["critic"]

    def _root(self, policy):
        d = Path(tempfile.mkdtemp(prefix="cf_conf_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text(f"review:\n  policy: {policy}\n")
        b = d / "sdlc-studio" / "bugs"; b.mkdir()
        (b / "BG9001-x.md").write_text("# BG9001: c\n\n> **Status:** Open\n> **Found-against:** US0001\n")
        return d

    def test_a_reject_under_carry_forward_does_not_block_the_close(self) -> None:
        conf, critic = self._mods()
        review = {"verdict": "REJECT", "reviewer": "qa", "author": "dev"}
        findings = [{"ref": "BG9001", "units": ["US0001"]}]
        d_cf = self._root("carry-forward")
        d_block = self._root("block")
        try:
            self.assertTrue(conf.carry_forward_covers(d_cf, review, findings))
            # under block, the same REJECT does NOT carry - the close still blocks
            self.assertFalse(conf.carry_forward_covers(d_block, review, findings))
            # an APPROVE is not a carry-forward case at all
            self.assertFalse(conf.carry_forward_covers(
                d_cf, {"verdict": "APPROVE", "reviewer": "qa", "author": "dev"}, findings))
        finally:
            shutil.rmtree(d_cf, ignore_errors=True); shutil.rmtree(d_block, ignore_errors=True)


class CarriedFindingLinkTests(unittest.TestCase):
    """US0335: a carried finding names the units it was found against, and the link survives
    the close of the sprint that produced it."""

    def _cf(self):
        import importlib.util, sys
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "carry_forward", Path(__file__).resolve().parent.parent / "carry_forward.py")
        m = importlib.util.module_from_spec(spec); sys.modules["carry_forward"] = m
        spec.loader.exec_module(m); return m

    def _root(self):
        d = Path(tempfile.mkdtemp(prefix="cf_link_"))
        (d / "sdlc-studio").mkdir(parents=True)
        (d / "sdlc-studio" / ".config.yaml").write_text("review:\n  policy: carry-forward\n")
        return d

    def test_a_carried_finding_naming_no_unit_is_refused(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            b = d / "sdlc-studio" / "bugs"; b.mkdir(parents=True)
            (b / "BG9002-x.md").write_text("# BG9002: c\n\n> **Status:** Open\n")  # no Found-against
            with self.assertRaises(cf.PolicyError):
                cf.validate_carried(d, [{"ref": "BG9002", "units": []}])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_a_carried_finding_still_resolves_after_its_sprint_closes(self) -> None:
        cf = self._cf(); d = self._root()
        try:
            b = d / "sdlc-studio" / "bugs"; b.mkdir(parents=True)
            # the finding names its units on its OWN file, so closing the run cannot strand it
            (b / "BG9003-x.md").write_text(
                "# BG9003: c\n\n> **Status:** Fixed\n> **Found-against:** US0007, US0008\n")
            self.assertEqual(cf.carried_finding_units(d, "BG9003"), ["US0007", "US0008"])
        finally:
            shutil.rmtree(d, ignore_errors=True)


def _ungroomed_story(root, num) -> None:
    """A refine-minted ungroomed story: its Acceptance Criteria are the placeholder marker
    (`sdlc_md.UNGROOMED_AC_MARKER`) rather than authored criteria."""
    marker = _load().sdlc_md.UNGROOMED_AC_MARKER
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-sample.md").write_text(
        f"# US{num:04d}: sample\n\n> **Status:** Draft\n"
        "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
        f"## Acceptance Criteria\n\n{marker}\n", encoding="utf-8")


def _legacy_skeleton_story(root, num) -> None:
    """A story minted BEFORE the ungroomed marker existed: its Acceptance Criteria are the bare
    `{{...}}` template scaffold. Every pre-existing refined story in a real workspace has this
    shape, and it is the one the marker-only count could not see."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-sample.md").write_text(
        f"# US{num:04d}: sample\n\n> **Status:** Draft\n"
        "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
        "## Acceptance Criteria\n\n### AC1: {{define}}\n\n"
        "- **Given** {{context}}\n- **When** {{action}}\n- **Then** {{outcome}}\n"
        "- **Verify:** {{executable check}}\n", encoding="utf-8")


class UngroomedMarkerTests(unittest.TestCase):
    """US0411: the count of ungroomed stories is machine-visible - conformance counts them by the
    marker, so an operator sees a refined backlog's grooming debt rather than meeting it at plan."""

    def test_ungroomed_stories_are_counted_by_their_marker(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Deliberately UNEQUAL groomed (3) and ungroomed (2), so a count that measured the
            # wrong set (the groomed ones) would read 3, not 2.
            _story(root, 1)                 # groomed (real ACs)
            _story(root, 2)                 # groomed
            _story(root, 5)                 # groomed
            _ungroomed_story(root, 3)       # ungroomed marker
            _ungroomed_story(root, 4)       # ungroomed marker
            result = _load().detect_conformance(root)
            self.assertEqual(result["summary"]["ungroomed"], 2)
            flagged = {u["id"] for u in result["units"] if u["ungroomed"]}
            self.assertEqual(flagged, {"US0003", "US0004"})
            # a groomed story is not miscounted, and the marker does not read as a specified AC
            self.assertFalse(_units(root)["US0003"]["stages"]["specified"])

    def test_the_legacy_placeholder_scaffold_is_counted_as_ungroomed_too(self) -> None:
        """BG0276: the count knew only the marker, so it reported ZERO ungroomed while a real
        workspace held 31 legacy-scaffold stories. Both shapes are the same debt."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Three shapes, deliberately unequal, so a counter that sees only ONE reads a
            # different number: 2 groomed, 3 marker, 1 legacy scaffold -> 4 ungroomed.
            _story(root, 1)
            _story(root, 2)
            _ungroomed_story(root, 3)
            _ungroomed_story(root, 4)
            _ungroomed_story(root, 5)
            _legacy_skeleton_story(root, 6)
            result = _load().detect_conformance(root)
            self.assertEqual(result["summary"]["ungroomed"], 4)
            flagged = {u["id"] for u in result["units"] if u["ungroomed"]}
            self.assertEqual(flagged, {"US0003", "US0004", "US0005", "US0006"})

    def test_a_groomed_story_quoting_a_placeholder_is_not_counted(self) -> None:
        """The precision half: a REAL criterion beside a quoted `{{...}}` is groomed. Without
        this the fix would trade a false zero for a false alarm."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "stories"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "US0007-sample.md").write_text(
                "# US0007: sample\n\n> **Status:** Draft\n"
                "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: the template renders {{placeholder}} verbatim\n\n"
                "- **Given** a template\n- **Then** it renders\n"
                "- **Verify:** pytest tests/test_t.py::T::t\n", encoding="utf-8")
            result = _load().detect_conformance(root)
            self.assertEqual(result["summary"]["ungroomed"], 0)


class DiffScopedConformanceTests(unittest.TestCase):
    """US0354 AC2: `detect_conformance(..., changed=True)` judges only the units this working
    tree touched. The narrowing is a REPORTING scope over the per-unit ledger only - a repo-global
    stage (a missing story index, an uncatalogued command) must still be counted and still fail,
    or the scoped mode becomes a way to hide one.

    Every fixture below is a REAL git repo, because the behaviour under test is "what changed".
    """

    def _repo(self, t) -> Path:
        """Two stories committed, no `stories/_index.md` - so the repo-global `reconciled`
        stage fails for the Done unit while the per-unit ledger has its own separate fault."""
        root = Path(t)
        _story(root, 1, status="Ready")                   # will be touched: judged
        _story(root, 2, status="Done", verify=False)      # untouched: advisory
        gitutil.git(["init", "-q"], cwd=root)
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-qm", "baseline"], cwd=root)
        return root

    def _touch(self, root: Path, num: int) -> None:
        p = root / "sdlc-studio" / "stories" / f"US{num:04d}-sample.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n<!-- edited -->\n", encoding="utf-8")

    def test_untouched_unit_is_advisory_but_a_global_stage_still_fails(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._touch(root, 1)
            res = mod.detect_conformance(root, changed=True)
            units = {u["id"]: u for u in res["units"]}

            # The untouched unit is REPORTED - with its real per-unit fault named ...
            self.assertTrue(units["US0002"]["scoped_out"])
            self.assertIn("verifiable", units["US0002"]["missing"])
            # ... and it is NOT charged to the count that decides the exit code.
            self.assertEqual(res["summary"]["nonconformant"], 0)
            self.assertEqual(res["summary"]["advisory"], 1)
            self.assertEqual(res["summary"]["judged"], 1)

            # The repo-global stage is STILL counted and STILL fails the command.
            self.assertEqual(res["summary"]["global_failures"], 1)
            self.assertEqual([g["stage"] for g in res["globals"]], ["reconciled"])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod.main(["check", "--root", str(root), "--changed"])
            self.assertEqual(rc, 1)                      # the global blocks a scoped run
            out = buf.getvalue()
            self.assertIn("US0002", out)                 # what it scoped, named
            self.assertIn("REPO-WIDE reconciled", out)   # what still blocks, named

            # The scoped run and the full run AGREE on the unit both judged.
            full = mod.detect_conformance(root)
            full_units = {u["id"]: u for u in full["units"]}
            self.assertEqual(units["US0001"]["missing"], full_units["US0001"]["missing"])
            self.assertEqual(units["US0001"]["stages"], full_units["US0001"]["stages"])
            self.assertEqual(full["summary"]["global_failures"], 1)
            # ... and the full run charges the untouched fault, so the scope is what moved it.
            self.assertEqual(full["summary"]["nonconformant"], 1)

            # Scoping never turns a REAL failure green: bring the same unit into the diff and
            # the same fault is counted again, from the same code path.
            self._touch(root, 2)
            again = mod.detect_conformance(root, changed=True)
            self.assertEqual(again["summary"]["nonconformant"], 1)
            self.assertFalse({u["id"]: u for u in again["units"]}["US0002"]["scoped_out"])

    def test_a_degraded_probe_falls_back_to_the_whole_workspace(self) -> None:
        """The central risk, refused: with no git there is no diff, and a scope derived from an
        unanswered probe is an EMPTY scope wearing a green tick. Unknown must mean judge
        everything, and the report must say the probe degraded."""
        mod = _load()
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)                              # deliberately NOT a git repo
            _story(root, 1, status="Ready")
            _story(root, 2, status="Done", verify=False)
            res = mod.detect_conformance(root, changed=True)
            self.assertTrue(res["scope"]["degraded"])
            self.assertEqual(res["summary"]["advisory"], 0)
            self.assertEqual(res["summary"]["judged"], 2)
            self.assertEqual(res["summary"]["nonconformant"], 1)
            self.assertFalse(any(u["scoped_out"] for u in res["units"]))

    def test_a_scoped_out_unit_never_claims_a_stage_it_did_not_judge(self) -> None:
        """The expensive per-unit probes (stamp resolution, the critic ledger) are SKIPPED for a
        unit outside the diff - so those stages must read `not judged`, never a pass."""
        mod = _load()
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            self._touch(root, 1)
            res = mod.detect_conformance(root, changed=True)
            u2 = {u["id"]: u for u in res["units"]}["US0002"]
            for stage in mod.UNJUDGED_WHEN_SCOPED:
                self.assertIsNone(u2["stages"][stage], stage)
                self.assertNotIn(stage, u2["missing"])
            self.assertEqual(sorted(res["scope"]["unjudged_stages"]),
                             sorted(mod.UNJUDGED_WHEN_SCOPED))

            # The other half: a stage that costs NOTHING to judge is still judged, on its real
            # value. Skipping those would report `documented` as missing for every untouched
            # Done unit - claiming a failure in a stage nobody examined - and would drop the
            # repo-global finding that has to survive the narrowing.
            self.assertIs(u2["stages"]["documented"], True)
            self.assertNotIn("documented", u2["missing"])
            self.assertIs(u2["stages"]["reconciled"], False)   # the missing story index
            self.assertIn("reconciled", u2["missing_global"])


@unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
class CritiquedHalvesTests(unittest.TestCase):
    """`critiqued` is one boolean over up to three independent halves. Reporting only the
    composite name costs a source dive per occurrence, so every UNMET half is named."""

    def _config(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  two_role_after: US0100\n", encoding="utf-8")

    def _report(self, root: Path) -> str:
        mod = _load()
        args = mod.build_parser().parse_args(["check", "--root", str(root)])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            args.func(args)
        return buf.getvalue()

    def test_only_the_signoff_missing_names_the_signoff_not_the_composite(self) -> None:
        """AC1. Verdict recorded, adversarial evidence recorded, sign-off absent: the ONE
        unmet half is the one named. Asserting the sign-off phrase alone would pass on a
        line naming all three, so the other two are asserted absent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            _critic_mod().record_evidence(root, "US0101", reviewer="qa-seat",
                                          author="builder", findings="adversarial pass done")
            mod = _load()
            u = {x["id"]: x for x in mod.detect_conformance(root)["units"]}["US0101"]
            self.assertEqual(u["critiqued_missing"], [mod.HALF_SIGNOFF])
            out = self._report(root)
            self.assertIn(mod.HALF_SIGNOFF, out)
            self.assertNotIn(mod.HALF_VERDICT, out)
            self.assertNotIn(mod.HALF_EVIDENCE, out)

    def test_several_unmet_halves_are_all_named_in_one_line(self) -> None:
        """AC2. Nothing recorded at all: all three halves are unmet and all three are named
        on the unit's single line - not just the first the composition happened to reach."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            mod = _load()
            u = {x["id"]: x for x in mod.detect_conformance(root)["units"]}["US0101"]
            self.assertEqual(u["critiqued_missing"],
                             [mod.HALF_VERDICT, mod.HALF_EVIDENCE, mod.HALF_SIGNOFF])
            line = next(ln for ln in self._report(root).splitlines() if "US0101" in ln)
            for half in (mod.HALF_VERDICT, mod.HALF_EVIDENCE, mod.HALF_SIGNOFF):
                self.assertIn(half, line)

    def test_a_satisfied_critiqued_stage_stays_conformant_and_names_nothing(self) -> None:
        """AC3. The change is diagnostic detail, never a new refusal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done")
            _record_verdict(root, "US0101")
            c = _critic_mod()
            c.record_evidence(root, "US0101", reviewer="qa-seat", author="builder",
                              findings="adversarial pass done")
            c.record_signoff(root, "US0101", principal="Darren Benson (operator)",
                             author="builder")
            mod = _load()
            u = {x["id"]: x for x in mod.detect_conformance(root)["units"]}["US0101"]
            self.assertTrue(u["stages"]["critiqued"])
            self.assertNotIn("critiqued", u["missing"])
            self.assertEqual(u["critiqued_missing"], [])

    def test_a_pre_cutoff_unit_names_only_the_verdict_half(self) -> None:
        """The two-role halves do not APPLY below the cutoff, so they are not reported unmet -
        an inapplicable half named as owed is the same misdirection in the other direction."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 99, status="Done")
            mod = _load()
            u = {x["id"]: x for x in mod.detect_conformance(root)["units"]}["US0099"]
            self.assertEqual(u["critiqued_missing"], [mod.HALF_VERDICT])

    def test_backfill_remedy_is_withheld_when_no_unit_misses_verified(self) -> None:
        """CR0368's second half: `run verify_ac and back-annotate` is the remedy for the
        VERIFIED stage. Printed under a missing-critiqued failure it sends the operator at
        the wrong gate, which is what cost a source dive."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done", verified="yes")
            mod = _load()
            res = mod.detect_conformance(root)
            u = {x["id"]: x for x in res["units"]}["US0101"]
            self.assertNotIn("verified", u["missing"])
            self.assertIn("critiqued", u["missing"])
            self.assertNotIn(mod.REMEDY_BACKFILL, self._report(root))
            self.assertNotIn(mod.REMEDY_BACKFILL, mod.remedy_detail(res))

    def test_backfill_remedy_still_offered_when_a_unit_does_miss_verified(self) -> None:
        """The other side of the same gate: withholding it always would delete a correct
        remedy rather than aim it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._config(root)
            _story(root, 101, status="Done", verified="no")
            mod = _load()
            res = mod.detect_conformance(root)
            self.assertIn("verified", {x["id"]: x for x in res["units"]}["US0101"]["missing"])
            self.assertIn(mod.REMEDY_BACKFILL, self._report(root))
            self.assertIn(mod.REMEDY_BACKFILL, mod.remedy_detail(res))


class DocCoverageGapNamedTests(unittest.TestCase):
    """CR0338 residual: the repo-wide doc-coverage finding told the operator to run
    `doc_coverage.py` to learn what was undocumented - information this run already had in
    hand. The finding names the items."""

    def _skill(self, root: Path, commands: tuple[str, ...]) -> None:
        sd = root / ".claude" / "skills" / "sdlc-studio"
        (sd / "help").mkdir(parents=True, exist_ok=True)
        (sd / "scripts").mkdir(parents=True, exist_ok=True)
        rows = "\n".join(f"| `{c}` | a type |" for c in commands)
        (sd / "SKILL.md").write_text(
            f"# S\n\n## Type Reference\n\n| Type | What |\n| --- | --- |\n{rows}\n\n"
            "## Full Reference\n", encoding="utf-8")
        (sd / "help" / "help.md").write_text("# help\n", encoding="utf-8")
        (sd / "reference-scripts.md").write_text("# scripts\n", encoding="utf-8")

    def test_the_undocumented_items_are_named_not_merely_counted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._skill(root, ("widget", "sprocket"))
            _story(root, 1, status="Done")   # `documented` is a Done-only stage
            g = next(x for x in _load().detect_conformance(root)["globals"]
                     if x["stage"] == "documented")
            for name in ("widget", "sprocket"):
                self.assertIn(name, g["reason"])
            self.assertIn("2 undocumented", g["reason"])
            # The remedy must not send the operator off to rediscover what is already named.
            self.assertNotIn("to name the gap", g["remedy"])


class DocDriftResidualTests(unittest.TestCase):
    """US0369 AC2: every residual CR0365's evidence sweep recorded carries a written
    disposition. Silence is what let twelve requests derive Complete over unmet criteria,
    so the check reads the SOURCE table rather than a hand-kept list - a residual added to
    CR0365 later and left undispositioned fails here."""

    REPO = Path(__file__).resolve().parents[5]
    CR = REPO / "sdlc-studio" / "change-requests"
    STORY = REPO / "sdlc-studio" / "stories"
    VOCAB = ("corrected", "refiled", "declined")

    def _rows(self, text: str, heading: str) -> list[list[str]]:
        rows, inside = [], False
        for line in text.splitlines():
            if line.startswith("#"):
                inside = line.strip().lstrip("# ").strip().lower() == heading.lower()
                continue
            if not (inside and line.startswith("|")):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or set("".join(cells)) <= set("- :"):
                continue          # the separator row
            rows.append(cells)
        return rows[1:]           # drop the header

    def _one(self, base: Path, prefix: str) -> Path:
        hits = sorted(base.glob(f"{prefix}*.md"))
        self.assertEqual(len(hits), 1, f"expected exactly one {prefix} file, got {hits}")
        return hits[0]

    def test_every_residual_is_corrected_or_declined_with_a_reason(self) -> None:
        # This suite ships to consuming projects, which have no CR0365 of their own. Absent
        # the source table there is nothing to check, and skipping says so rather than
        # passing quietly; in THIS repo both files exist, so the check runs for real.
        if not sorted(self.CR.glob("CR0365*.md")):
            self.skipTest("no CR0365 in this workspace - the residual sweep is repo-specific")
        source = self._rows(self._one(self.CR, "CR0365").read_text(encoding="utf-8"),
                            "The residuals")
        expected = {r[0] for r in source}
        self.assertGreater(len(expected), 1, "CR0365's residual table did not parse")

        text = self._one(self.STORY, "US0369").read_text(encoding="utf-8")
        recorded = self._rows(text, "Residual disposition")
        seen = {r[0] for r in recorded}
        self.assertEqual(seen, expected,
                         "a residual in CR0365 has no disposition row (or vice versa)")
        for from_, disposition, reason in ((r[0], r[1], r[2]) for r in recorded):
            self.assertIn(disposition.lower(), self.VOCAB,
                          f"{from_}: '{disposition}' is not one of {self.VOCAB}")
            # A disposition with no reason is silence wearing a label.
            self.assertGreaterEqual(len(reason), 30, f"{from_}: reason too thin to be one")


class TwoRoleCutoffOnUlidIdsTests(unittest.TestCase):
    """BG0318: `review.two_role_after` is a NUMERIC cutoff compared against `id_number`, which
    returns None for a v3 ULID id. `two_role_applies` was therefore False for every ULID unit,
    so both halves defaulted True unchecked - a forward-only gate standing down on exactly the
    newest units it exists to cover, silently. A ULID id is by construction newer than any
    sequential cutoff, so the gate must fail CLOSED on an unnumbered id."""

    ULID = "US-01JQK3F8"
    V2 = "US0101"

    def _stages(self, root, rid):
        """Only `critic_required` is switched off, so `critiqued` here is decided by the
        two-role halves ALONE - the assertion cannot pass on the verdict half's behaviour."""
        return _load()._done_stages(root, rid, ["yes"], False, set(), True,
                                    two_role_cutoff=100, critic_required=False)

    def test_a_ulid_unit_past_the_cutoff_is_held_to_both_two_role_halves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            mod = _load()
            verified, _rec, critiqued, _doc, unmet = self._stages(d, self.ULID)
            self.assertTrue(verified)   # the fixture is otherwise clean
            self.assertFalse(critiqued,
                             "a ULID unit with no evidence and no sign-off cleared `critiqued`")
            self.assertEqual(unmet, [mod.HALF_EVIDENCE, mod.HALF_SIGNOFF])

    def test_the_ulid_verdict_matches_the_v2_verdict_for_the_same_evidence(self) -> None:
        """The two calls differ only in the id's ERA. A gate whose strictness depends on
        which id scheme a project mints is the defect, so the verdicts must be identical."""
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._stages(d, self.ULID)[4], self._stages(d, self.V2)[4])

    def test_no_cutoff_configured_still_leaves_a_ulid_unit_alone(self) -> None:
        """Fail-closed must not become always-on: without `review.two_role_after` the
        two-role halves apply to nobody, ULID ids included."""
        with tempfile.TemporaryDirectory() as d:
            unmet = _load()._done_stages(d, self.ULID, ["yes"], False, set(), True,
                                         two_role_cutoff=None, critic_required=False)[4]
            self.assertEqual(unmet, [])

    @unittest.skipUnless(HAS_YAML, "review.two_role_after reads .config.yaml (needs PyYAML)")
    def test_end_to_end_a_done_ulid_story_is_not_reported_conformant(self) -> None:
        """The stage list `detect_conformance` builds drops `critiqued` from `required`
        on the SAME None comparison, so the `_done_stages` fix alone would still report the
        story conformant. This pins the report, which is what an operator reads.

        The DoD downgrades the critic half only, leaving the two-role half armed - so
        `critiqued` survives in `required` for one reason and one reason only."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sdir = root / "sdlc-studio"
            sdir.mkdir(parents=True, exist_ok=True)
            (sdir / ".config.yaml").write_text(
                "review:\n  two_role_after: US0100\n", encoding="utf-8")
            (sdir / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- adversarial review recorded [check: review.two-role]\n",
                encoding="utf-8")
            sd = sdir / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / f"{self.ULID}-sample.md").write_text(
                f"# {self.ULID}: sample\n\n> **Status:** Done\n"
                "> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n### AC1: works\n- **Given** a thing\n"
                "- **Verify:** shell echo ok\n- **Verified:** yes (2026-01-01)\n",
                encoding="utf-8")
            u = _units(root)[self.ULID]
            self.assertIn("critiqued", u["missing"],
                          "the two-role gate stood down for a v3 ULID unit")


def _decisions_mod():
    spec = importlib.util.spec_from_file_location("decisions", SCRIPT.parent / "decisions.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["decisions"] = m
    spec.loader.exec_module(m)
    return m


def _waive(root, subject, rationale="recorded, reasoned, inherited debt") -> str:
    return _decisions_mod().record_waiver(root, subject, rationale)["id"]


def _index(root, statuses: dict) -> None:
    """A story index matching the fixture, so the repo-global `reconciled` stage is clean and
    the waiver under test is the only thing moving the verdict."""
    rows = "".join(f"| [US{n:04d}](US{n:04d}-sample.md) | sample | {s} |\n"
                   for n, s in sorted(statuses.items()))
    (root / "sdlc-studio" / "stories" / "_index.md").write_text(
        "# Stories\n\n| ID | Title | Status |\n|---|---|---|\n" + rows, encoding="utf-8")


class WaiverTests(unittest.TestCase):
    """US0525 / CR0460: the lane reads the recorded waivers. D0074 waived the pre-two-role
    critic debt through the sanctioned `decisions waive` path and the lane never read it, so
    the waived units were reported non-conformant on every clean-tree run - which is the state
    a close runs in, so the escape hatch the gate's own remedy text recommends was invisible
    precisely when it was needed."""

    def test_a_waived_unit_reports_as_waived_naming_the_decision(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done")          # Done, no critic verdict -> missing critiqued
            _index(root, {1: "Done"})
            did = _waive(root, "rule:conformance:critiqued:US0001")
            mod = _load()
            res = mod.detect_conformance(root)
            u = {x["id"]: x for x in res["units"]}["US0001"]
            self.assertEqual([w["stage"] for w in u["waived"]], ["critiqued"])
            self.assertEqual(u["waived"][0]["decision"], did)   # the decision is NAMED
            self.assertNotIn("critiqued", u["missing"])
            self.assertTrue(u["conformant"], u["missing"])
            self.assertEqual(res["summary"]["nonconformant"], 0)
            self.assertEqual(res["summary"]["waived"], 1)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = mod.main(["check", "--root", str(root)])
            out = buf.getvalue()
            self.assertEqual(rc, 0, out)            # a waived unit does not block the lane
            self.assertIn(did, out)                 # ... and the report says which decision
            self.assertIn("waived", out.lower())

    def test_an_unwaived_unit_is_still_reported(self) -> None:
        """A waiver NARROWS the finding rather than silencing the lane: it clears the stage it
        names, for the units it covers, and nothing else."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, status="Done", verify=False)   # missing verifiable AND critiqued
            _story(root, 2, status="Done")                 # missing critiqued, covered
            _story(root, 3, status="Done")                 # missing critiqued, OUTSIDE the scope
            _index(root, {1: "Done", 2: "Done", 3: "Done"})
            _waive(root, "rule:conformance:critiqued:US0001-US0002")   # an id range, as recorded
            res = _load().detect_conformance(root)
            units = {x["id"]: x for x in res["units"]}
            # covered on the stage named, still reported on the stage it was not
            self.assertEqual([w["stage"] for w in units["US0001"]["waived"]], ["critiqued"])
            self.assertIn("verifiable", units["US0001"]["missing"])
            self.assertFalse(units["US0001"]["conformant"])
            self.assertTrue(units["US0002"]["conformant"])
            # outside the waiver's scope: judged exactly as before
            self.assertEqual(units["US0003"]["waived"], [])
            self.assertIn("critiqued", units["US0003"]["missing"])
            self.assertEqual(res["summary"]["nonconformant"], 2)

    def test_a_ulid_scoped_waiver_covers_its_unit(self) -> None:
        """A v3 ULID id carries the same dash a range does. Read as a range it resolves to
        nothing and the waiver covers nobody - silently, and on the newest ids, which is the
        shape BG0318 already cost this gate once."""
        mod = _load()
        ulid = "US-01JQK3F8"
        waivers = [{"stage": "critiqued", "scope": ulid.lower(), "decision": "D0009"}]
        self.assertEqual(mod.waived_stages(waivers, ulid, ["critiqued"]),
                         [{"stage": "critiqued", "decision": "D0009"}])
        # ... and it covers that unit ONLY
        self.assertEqual(mod.waived_stages(waivers, "US-01JQK3F9", ["critiqued"]), [])
        self.assertEqual(mod.waived_stages(waivers, "US0288", ["critiqued"]), [])

    def test_a_scope_that_resolves_to_nothing_covers_nothing(self) -> None:
        """A scope tail naming neither a unit nor a range must narrow to nobody, never widen to
        everybody: a misspelled waiver is a waiver of nothing, not a waiver of the whole rule."""
        mod = _load()
        waivers = [{"stage": "critiqued", "scope": "pre-two-role", "decision": "D0074"}]
        for rid in ("US0288", "US0103", "US-01JQK3F8"):
            self.assertEqual(mod.waived_stages(waivers, rid, ["critiqued"]), [], rid)
        # the bare rule, with no tail at all, is the deliberate way to waive it everywhere
        every = [{"stage": "critiqued", "scope": "", "decision": "D0074"}]
        self.assertEqual([w["decision"] for w in mod.waived_stages(every, "US0288", ["critiqued"])],
                         ["D0074"])

    def test_the_waiver_holds_on_a_clean_tree(self) -> None:
        """The defect's actual shape: it only appeared to pass when there was a diff to scope
        to. A close runs on a CLEAN tree, where the lane judges the whole workspace - so the
        waiver must hold identically in both."""
        mod = _load()
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _story(root, 1, status="Done")
            _index(root, {1: "Done"})
            did = _waive(root, "rule:conformance:critiqued:US0001")
            gitutil.git(["init", "-q"], cwd=root)
            gitutil.git(["add", "-A"], cwd=root)
            gitutil.git(["commit", "-qm", "baseline"], cwd=root)

            clean = mod.detect_conformance(root, changed=True)   # nothing changed: a close
            self.assertTrue(clean["scope"]["degraded"])          # no diff -> judged everything
            self.assertEqual(clean["summary"]["judged"], 1)      # ... so it WAS judged
            u = {x["id"]: x for x in clean["units"]}["US0001"]
            self.assertEqual([w["decision"] for w in u["waived"]], [did])
            self.assertEqual(clean["summary"]["nonconformant"], 0)
            self.assertEqual(clean["summary"]["global_failures"], 0)

            p = root / "sdlc-studio" / "stories" / "US0001-sample.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n<!-- edited -->\n", encoding="utf-8")
            dirty = mod.detect_conformance(root, changed=True)
            self.assertFalse(dirty["scope"]["degraded"])
            d_unit = {x["id"]: x for x in dirty["units"]}["US0001"]
            self.assertEqual(u["waived"], d_unit["waived"])      # identical in both
            self.assertEqual(dirty["summary"]["nonconformant"], 0)


class ThreeStateCoverageTests(unittest.TestCase):
    """US0621 / CR0506: conformance names the REPAIRED state instead of "missing critiqued".

    It used those words for all eighteen repaired units of RUN-01KYZKY5 AND for units nobody had
    opened - the same phrase for two different facts - which is what sent that close to a waiver
    sweep over work whose findings were already fixed and mutation-verified.
    """

    def _mods(self):
        import importlib.util as u
        here = Path(__file__).resolve().parent.parent
        out = []
        for name in ("critic", "conformance"):
            spec = u.spec_from_file_location(name, here / f"{name}.py")
            mod = u.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            out.append(mod)
        return out

    def test_conformance_names_the_repaired_state_not_missing_critiqued(self) -> None:
        """MUTANT: leave `critiqued_unmet` reading only the APPROVE verdict.

        Both directions are asserted: an unrepaired REJECT still wants the verdict half, and a
        completely repaired one no longer does.
        """
        critic, conf = self._mods()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            critic.record_verdict(root, "US9101", "REJECT", "qa-seat", "builder",
                                  "[new] alpha broke", "delivery", "abcdef123456")
            unrepaired = conf.critiqued_unmet(root, "US9101", 0, True, False)
            self.assertIn(conf.HALF_VERDICT, unrepaired,
                          "an unrepaired REJECT was treated as covered")
            critic.record_repair(root, "US9101", "builder", "alpha broke -> mutant killed")
            repaired = conf.critiqued_unmet(root, "US9101", 0, True, False)
        self.assertNotIn(conf.HALF_VERDICT, repaired,
                         "a repaired unit still reports `missing critiqued "
                         "(independent APPROVE verdict)` - the same words used for a unit "
                         "nobody opened")

class TierCoverageTests(unittest.TestCase):
    """US0641: the third step, and the only one that makes the other two worth anything.

    Deriving a tier and recording it buys nothing until something REFUSES on it. `critic brief
    --tier` was never recorded, never read and never checked, so a reviewer could take the
    bounded pass on the riskiest unit in a batch and no gate downstream could tell.
    """

    def _unit(self, root: Path, uid: str, *, heavy: bool) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        if heavy:
            for i in range(5):
                fp = root / f"src/mod{i}.py"
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text("def f():\n" + "    if True:\n        pass\n" * 40,
                              encoding="utf-8")
            affects = ", ".join(f"src/mod{i}.py" for i in range(5))
            points = 13
        else:
            fp = root / "docs" / "note.md"
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text("a note\n", encoding="utf-8")
            affects, points = "docs/note.md", 1
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: sample\n\n> **Status:** Done\n> **Affects:** {affects}\n"
            f"> **Points:** {points}\n\n## Acceptance Criteria\n\n### AC1: works\n"
            f"- **Given** a thing\n- **Verify:** shell echo ok\n"
            f"- **Verified:** yes (2026-01-01)\n", encoding="utf-8")

    def test_a_light_verdict_does_not_cover_a_full_tier_unit(self) -> None:
        """Mutant: ignore the tier in coverage - the light verdict reads as coverage, and the
        whole of the deriving and recording buys exactly nothing."""
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0002", heavy=True)
            self.assertEqual(mod.critic.tier_for(root, "US0002"), "full",
                             "the fixture does not band high - it proves nothing")
            mod.critic.record_verdict(root, "US0002", "approve", reviewer="qa", author="dev",
                                      tier="light")
            v = mod.critic.verdict_for(root, "US0002")
            self.assertFalse(mod.tier_covers(root, "US0002", v))
            self.assertFalse(mod.verdict_half_ok(root, "US0002", sprint_covers=False))
            # ...and the operator is told WHICH thing is missing, not sent to look for an
            # approval that is sitting in the log
            unmet = mod.critiqued_unmet(root, "US0002", two_role_cutoff=None)
            self.assertIn(mod.HALF_TIER, unmet)
            self.assertNotIn(mod.HALF_VERDICT, unmet)

    def test_an_explicitly_chosen_light_tier_still_does_not_cover(self) -> None:
        """An operator's `--tier light` records a CHOICE, and the choice is visible - but it does
        not stand the gate down. A gate an operator can disarm with an undeclared flag is not a
        gate; standing it down is what a recorded decision is for.

        Mutant: compare the cell without splitting the `(explicit)` suffix off - `light
        (explicit)` stops matching `light`, and an explicit choice silently clears the gate that
        the identical derived choice does not. Found by mutation; no test reached this cell
        shape before.
        """
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0002", heavy=True)
            mod.critic.record_verdict(root, "US0002", "approve", reviewer="qa", author="dev",
                                      tier="light", tier_explicit=True)
            self.assertIn("explicit", mod.critic.verdict_for(root, "US0002")["tier"])
            self.assertFalse(mod.verdict_half_ok(root, "US0002", sprint_covers=False))

    def test_a_full_verdict_covers_a_full_tier_unit(self) -> None:
        """The positive control. Without it a predicate that refuses every tiered verdict
        passes the criterion above for the wrong reason."""
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0002", heavy=True)
            mod.critic.record_verdict(root, "US0002", "approve", reviewer="qa", author="dev",
                                      tier="full")
            self.assertTrue(mod.verdict_half_ok(root, "US0002", sprint_covers=False))

    def test_a_light_verdict_covers_a_low_band_unit(self) -> None:
        """The point of the whole slice: a small unit stops paying a large unit's review.
        Mutant: demand `full` everywhere - the tiering is a no-op wearing a config key."""
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0003", heavy=False)
            self.assertEqual(mod.critic.tier_for(root, "US0003"), "light")
            mod.critic.record_verdict(root, "US0003", "approve", reviewer="qa", author="dev",
                                      tier="light")
            self.assertTrue(mod.verdict_half_ok(root, "US0003", sprint_covers=False))

    def test_a_verdict_recorded_without_a_tier_still_covers(self) -> None:
        """Mutant: treat absent as light - the rule applies backwards, every historical verdict
        on a medium-or-worse unit stops covering, and the gate re-opens the closed corpus for a
        fact nobody could have recorded.

        BOTH spellings of absent, because they are written by different eras and only testing
        one leaves the other reachable: the current writer puts this file's `-` ABSENT marker in
        the cell, and a row from before the column existed carries no cell at all. The first
        version of this test covered only the `-` case, and the mutation pass found it.
        """
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0002", heavy=True)
            mod.critic.record_verdict(root, "US0002", "approve", reviewer="qa", author="dev")
            self.assertEqual(mod.critic.verdict_for(root, "US0002")["tier"], "-")
            self.assertTrue(mod.verdict_half_ok(root, "US0002", sprint_covers=False))
        with tempfile.TemporaryDirectory() as d:
            root, mod = Path(d), _load()
            self._unit(root, "US0002", heavy=True)
            path = mod.critic.verdicts_path(root, "delivery")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Critic Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Brief | Issues |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| US0002 | APPROVE | qa | dev | 2026-07-01 | abc123abc123 | - |\n",
                encoding="utf-8")
            self.assertEqual(mod.critic.verdict_for(root, "US0002")["tier"], "")
            self.assertTrue(mod.verdict_half_ok(root, "US0002", sprint_covers=False),
                            "a verdict from before the column existed stopped covering")

if __name__ == "__main__":
    unittest.main()
