"""Unit tests for readiness.py - sprint tranche readiness (RED first)."""
from __future__ import annotations

import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "readiness.py"


def _load():
    spec = importlib.util.spec_from_file_location("readiness", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["readiness"] = mod
    spec.loader.exec_module(mod)
    return mod


def _cr(root, num, status="Proposed", ac="- [ ] integrity.py exits 1 when an active story lacks its Epic link", depends=None):
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# CR-{num:04d}: c\n\n> **Status:** {status}\n"
    if depends:
        body += f"> **Depends on:** {depends}\n"
    body += f"\n## Acceptance Criteria\n\n{ac}\n"
    (d / f"CR{num:04d}-x.md").write_text(body, encoding="utf-8")


def _epic(root, num, status="Done"):
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"EP{num:04d}-x.md").write_text(
        f"# EP{num:04d}: e\n\n> **Status:** {status}\n", encoding="utf-8")


def _manifest(root, *repos):
    """Write a PVD manifest naming `repos` as (id, path) pairs, in that order."""
    lines = ["master_pvd: x", "repos:"]
    for repo_id, path in repos:
        lines += [f"  - id: {repo_id}", f"    path: {path}"]
    (root / "product-manifest.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


TAUTOLOGY = "- [ ] Change implemented and verified; lint and tests green."


def _bug(root, num, status="Open", repro=True, fix=True):
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n\n## Summary\n\nx\n"
    if repro:
        body += "\n## Steps to Reproduce\n\n1. do it\n"
    if fix:
        body += "\n## Proposed Fix\n\ndo this\n"
    (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")


class WeakAcTests(unittest.TestCase):
    def test_tautology_is_weak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)
            u = _load().audit_unit(root, "CR0001")
            self.assertFalse(u["ready"])
            self.assertIn("weak-AC", u["issues"])

    def test_concrete_ac_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2)  # concrete AC, Proposed, no deps
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])

    def test_empty_ac_is_weak(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 3, ac="(none yet)")
            u = _load().audit_unit(root, "CR0003")
            self.assertIn("weak-AC", u["issues"])

    def test_unexpanded_template_placeholder_is_weak(self) -> None:
        # BG0201: a story scaffolded by `artifact.py new` and never groomed carries
        # `{{...}}` spans in every AC field. It has AC-shaped markup, so the item
        # count is non-zero, and it does not contain the TAUTOLOGY phrase - it was
        # certified ready and entered implementation with `{{executable check}}` as
        # its own oracle.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 10, ac=(
                "### AC1: {{define}}\n\n"
                "- **Given** {{context}}\n"
                "- **When** {{action}}\n"
                "- **Then** {{outcome}}\n"
                "- **Verify:** {{executable check}}\n"))
            u = _load().audit_unit(root, "CR0010")
            self.assertFalse(u["ready"], u["issues"])
            self.assertIn("weak-AC", u["issues"])

    def test_placeholder_in_one_of_several_acs_is_weak(self) -> None:
        # A partly-groomed unit is not ready either: one ungroomed AC is an
        # ungroomed unit, and reporting ready would hide it behind its filled siblings.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 11, ac=(
                "### AC1: rejects a negative count\n\n"
                "- **Verify:** shell python3 -m unittest tests.test_x.NegativeTests\n\n"
                "### AC2: {{define}}\n\n"
                "- **Verify:** {{executable check}}\n"))
            u = _load().audit_unit(root, "CR0011")
            self.assertFalse(u["ready"], u["issues"])
            self.assertIn("weak-AC", u["issues"])

    def test_prose_only_ac_with_markup_elsewhere_is_weak(self) -> None:
        # AC-style markup OUTSIDE the AC section must not count; a prose-only AC
        # section is weak even if `- **AC1:**` appears in the Summary.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cdir = root / "sdlc-studio" / "change-requests"
            cdir.mkdir(parents=True, exist_ok=True)
            (cdir / "CR0009-x.md").write_text(
                "# CR-0009: c\n\n> **Status:** Proposed\n\n"
                "## Summary\n\n- **AC1:** this looks like an AC but is in Summary\n\n"
                "## Acceptance Criteria\n\nThe change should work well.\n",
                encoding="utf-8")
            u = _load().audit_unit(root, "CR0009")
            self.assertIn("weak-AC", u["issues"])


class DepsTerminalTests(unittest.TestCase):
    def test_unmet_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed")          # dependency, not yet done
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("CR0001" in i for i in u["issues"]))

    def test_met_dependency_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Complete")
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])

    def test_already_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 4, status="Complete")
            u = _load().audit_unit(root, "CR0004")
            self.assertFalse(u["ready"])
            self.assertIn("already-terminal", u["issues"])

    def test_missing_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="CR9099")  # referent absent
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("CR9099:missing" in i for i in u["issues"]))

    def test_dead_dependency_surfaced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Rejected")
            _cr(root, 2, status="Proposed", depends="CR0001")
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            self.assertTrue(any("dead" in i for i in u["issues"]))


class CrossRepoDepsTests(unittest.TestCase):
    """A `Depends on:` referent is resolved in-repo first, then across the repos the PVD
    manifest names: a multi-repo product's cross-repo dependency is a real edge, not
    `unmet-deps`. An absent sibling checkout is named, never silently passed."""

    def test_dep_resolved_in_repo_wins(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Complete")
            _cr(root, 2, status="Proposed", depends="CR0001")
            _manifest(root, ("sib", "./sibling"))       # manifest present, sibling irrelevant
            _epic(root / "sibling", 99, "Done")
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])

    def test_dep_delivered_cross_repo_is_met(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="EP0099")   # referent lives in the sibling
            _epic(root / "sibling", 99, "Done")
            _manifest(root, ("sib", "./sibling"))
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])
            self.assertNotIn("unmet-deps", "; ".join(u["issues"]))

    def test_dep_undelivered_cross_repo_is_unmet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="EP0099")
            _epic(root / "sibling", 99, "In Progress")           # not delivered yet
            _manifest(root, ("sib", "./sibling"))
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])
            # its real cross-repo status is named, not a vacuous ":missing"
            self.assertTrue(any("EP0099:In Progress" in i for i in u["issues"]), u["issues"])

    def test_absent_sibling_checkout_is_named_not_silently_passed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="EP0088")
            _manifest(root, ("gone", "./no-such-repo"))          # checkout absent
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])                          # never a silent pass
            joined = "; ".join(u["issues"])
            self.assertIn("gone", joined)                         # the repo is named
            self.assertIn("no-such-repo", joined)                 # and its path
            # unresolvable is not the same claim as undelivered - never a false "unmet"
            self.assertNotIn("unmet-deps", joined)
            self.assertIn("unresolved-deps", joined)


class MultiRepoManifestTests(unittest.TestCase):
    """A manifest naming several repos, with only some cloned - the case an operator is
    actually in. An absent repo must not stop the search: resolution has to keep looking in
    the repos that ARE on disk, and the verdict must not depend on the manifest's order."""

    def _fixture(self, root: Path) -> None:
        _cr(root, 2, status="Proposed", depends="EP0099")
        _epic(root / "sibling", 99, "Done")          # delivered, and checked out

    def test_absent_repo_does_not_mask_a_later_present_repo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._fixture(root)
            # the absent repo is listed FIRST; the delivered referent sits in the second
            _manifest(root, ("gone", "./no-such-repo"), ("sib", "./sibling"))
            u = _load().audit_unit(root, "CR0002")
            self.assertTrue(u["ready"], u["issues"])   # never a false block

    def test_verdict_is_independent_of_manifest_order(self) -> None:
        orders = (
            (("gone", "./no-such-repo"), ("sib", "./sibling")),
            (("sib", "./sibling"), ("gone", "./no-such-repo")),
        )
        verdicts = []
        for repos in orders:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._fixture(root)
                _manifest(root, *repos)
                u = _load().audit_unit(root, "CR0002")
                verdicts.append((u["ready"], u["issues"]))
        self.assertEqual(verdicts[0], verdicts[1], "same disk state, reordered manifest, "
                                                   "different verdict")

    def test_unresolvable_only_when_no_repo_resolves_it(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 2, status="Proposed", depends="EP0077")   # in neither repo
            _epic(root / "sibling", 99, "Done")
            _manifest(root, ("gone", "./no-such-repo"), ("sib", "./sibling"))
            u = _load().audit_unit(root, "CR0002")
            self.assertFalse(u["ready"])                         # never a silent pass
            joined = "; ".join(u["issues"])
            self.assertIn("unresolved-deps", joined)             # a repo went unsearched
            self.assertIn("gone", joined)                        # and it is named
            self.assertIn("no-such-repo", joined)


class LinkIntegrityTests(unittest.TestCase):
    def test_link_integrity_plumbing(self) -> None:
        # An active story with a `--` Epic is an integrity error; audit_batch must
        # surface it as a link-integrity issue (proves the integrity_errors wiring).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n> **Epic:** --\n\n"
                "## Acceptance Criteria\n\n### AC1: real thing\n", encoding="utf-8")
            res = _load().audit_batch(root, ["US0001"])
            self.assertIn("link-integrity", res["units"][0]["issues"])


class BugReadinessTests(unittest.TestCase):
    def test_well_formed_bug_is_ready_not_weak_ac(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 1, repro=True, fix=True)   # has Steps + Proposed Fix
            u = _load().audit_unit(root, "BG0001")
            self.assertTrue(u["ready"], u["issues"])
            self.assertNotIn("weak-AC", u["issues"])

    def test_underspecified_bug_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, 2, repro=False, fix=False)
            u = _load().audit_unit(root, "BG0002")
            self.assertFalse(u["ready"])
            self.assertIn("underspecified", u["issues"])
            self.assertNotIn("weak-AC", u["issues"])

    def test_template_vocabulary_bug_ready(self) -> None:
        # The shipped template's heading names are the second accepted vocabulary.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0004-x.md").write_text(
                "# BG0004: b\n\n> **Status:** Open\n\n## Reproduction Steps\n\n"
                "1. x\n\n## Fix Description\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0004")
            self.assertTrue(u["ready"], u["issues"])

    def test_mixed_vocabulary_bug_ready(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0005-x.md").write_text(
                "# BG0005: b\n\n> **Status:** Open\n\n## Reproduction Steps\n\n"
                "1. x\n\n## Proposed Fix\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0005")
            self.assertTrue(u["ready"], u["issues"])

    def test_shipped_template_renders_ready(self) -> None:
        # The gate validated against its own template's output: a bug authored from
        # templates/core/bug.md with every placeholder filled must not flag underspecified.
        template = Path(__file__).resolve().parents[2] / "templates" / "core" / "bug.md"
        rendered = template.read_text(encoding="utf-8")
        import re
        rendered = re.sub(r"\{\{[^}]*\}\}", "filled", rendered)
        self.assertFalse(_load()._bug_underspecified(rendered),
                         "shipped bug template flags underspecified when fully filled")

    def test_bug_missing_both_sections_still_flags(self) -> None:
        # True positive preserved: neither vocabulary present -> underspecified.
        self.assertTrue(_load()._bug_underspecified(
            "# BG0006: b\n\n> **Status:** Open\n\n## Summary\n\nx\n"))

    def test_house_template_symptom_rootcause_fix_proposed_ready(self) -> None:
        # A richer house shape (Symptom + Root cause + Fix (proposed)) is
        # stronger evidence than bare repro steps - it must read as ready
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0008-x.md").write_text(
                "# BG0008: b\n\n> **Status:** Open\n\n## Symptom\n\nwrong\n\n"
                "## Root cause\n\nbad map\n\n## Fix (proposed)\n\nremap\n\n"
                "## Verify\n\ntest\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0008")
            self.assertTrue(u["ready"], u["issues"])

    def test_fix_proposed_word_order_equivalent(self) -> None:
        # 'Fix (proposed)' and 'Proposed Fix' are the same two words
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0009-x.md").write_text(
                "# BG0009: b\n\n> **Status:** Open\n\n## Steps to Reproduce\n\n"
                "1. x\n\n## Fix (proposed)\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0009")
            self.assertTrue(u["ready"], u["issues"])

    def test_symptom_without_cause_still_underspecified(self) -> None:
        # the combo requires both halves - half a diagnosis is not repro evidence
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0010-x.md").write_text(
                "# BG0010: b\n\n> **Status:** Open\n\n## Symptom\n\nwrong\n\n"
                "## Proposed Fix\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0010")
            self.assertFalse(u["ready"])
            self.assertIn("underspecified", u["issues"])

    def test_symptom_alone_no_fix_still_underspecified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0012-x.md").write_text(
                "# BG0012: b\n\n> **Status:** Open\n\n## Symptom\n\nwrong\n",
                encoding="utf-8")
            u = _load().audit_unit(root, "BG0012")
            self.assertFalse(u["ready"])
            self.assertIn("underspecified", u["issues"])

    def test_config_declared_sections_respected(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent - conventions degrade to defaults")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "conventions:\n  bug_ready_sections:\n"
                "    repro: [Observed Behaviour]\n    fix: [Remedy]\n",
                encoding="utf-8")
            (dd / "BG0011-x.md").write_text(
                "# BG0011: b\n\n> **Status:** Open\n\n## Observed Behaviour\n\n"
                "x\n\n## Remedy\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0011")
            self.assertTrue(u["ready"], u["issues"])

    def test_bug_with_suffixed_headings_ready(self) -> None:
        # Heading match is substring-tolerant: "## Steps to Reproduce the crash" counts.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "bugs"
            dd.mkdir(parents=True, exist_ok=True)
            (dd / "BG0003-x.md").write_text(
                "# BG0003: b\n\n> **Status:** Open\n\n## Steps to Reproduce the crash\n\n"
                "1. x\n\n## Proposed Fix and rationale\n\ny\n", encoding="utf-8")
            u = _load().audit_unit(root, "BG0003")
            self.assertTrue(u["ready"], u["issues"])


class SequencedInBatchTests(unittest.TestCase):
    """A dependency satisfied by the SAME tranche is the planner doing its job -
    informational `sequenced-in-batch`, not `unmet-deps`."""

    def test_in_batch_dep_is_informational_not_unmet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2, depends="CR0001")
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertTrue(u2["ready"], u2["issues"])
            self.assertNotIn("unmet-deps", "; ".join(u2["issues"]))
            self.assertIn("sequenced-in-batch: CR0001", "; ".join(u2.get("info", [])))

    def test_dead_in_batch_dep_stays_unmet(self) -> None:
        # A Rejected dep cannot be delivered by sequencing - keep it unmet-deps.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Rejected")
            _cr(root, 2, depends="CR0001")
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertFalse(u2["ready"])
            self.assertIn("unmet-deps", "; ".join(u2["issues"]))

    def test_out_of_batch_dep_still_unmet(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1)
            _cr(root, 2, depends="CR0009")   # not in batch, not on disk
            res = _load().audit_batch(root, ["CR0001", "CR0002"])
            u2 = next(u for u in res["units"] if u["id"] == "CR0002")
            self.assertFalse(u2["ready"])
            self.assertIn("unmet-deps", "; ".join(u2["issues"]))


class GuidanceTests(unittest.TestCase):
    def test_guidance_printed(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)  # weak-AC -> not ready
            buf = io.StringIO()
            with redirect_stdout(buf):
                _load().main(["check", "--ids", "CR0001", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Guidance:", out)
            self.assertIn("weak-AC ->", out)


class CliTests(unittest.TestCase):
    def test_batch_json_and_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, ac=TAUTOLOGY)   # not ready
            _cr(root, 2)                  # ready
            mod = _load()
            res = mod.audit_batch(root, ["CR0001", "CR0002"])
            self.assertEqual(res["summary"]["total"], 2)
            self.assertEqual(res["summary"]["not_ready"], 1)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = mod.main(["check", "--ids", "CR0001,CR0002", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 1)  # a not-ready unit -> non-zero
            self.assertIn("summary", buf.getvalue())


class CrossCheckUnavailableTests(unittest.TestCase):
    """BG0325: a readiness check that CRASHED must never read as a check that passed.

    `ac_scope.check` is repo-wide, so one exception erased the cross-epic finding for
    every unit in the batch - including a blocking one that would have flipped a unit to
    not-ready and the exit code to 1. The gate then printed a verdict it never computed.
    """

    def _batch(self, root):
        _cr(root, 1)  # otherwise ready: nothing but the cross-epic check can fail it

    def test_crashing_cross_check_is_reported_not_swallowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._batch(root)
            mod = _load()
            err = io.StringIO()
            with mock.patch.object(mod.ac_scope, "check",
                                   side_effect=RuntimeError("ac_scope exploded")):
                with redirect_stderr(err):
                    res = mod.audit_batch(root, ["CR0001"])
            self.assertTrue(res["uncomputed"], "the crashed check must be named in the report")
            self.assertIn("cross-epic-ac", " ".join(res["uncomputed"]))
            self.assertIn("ac_scope exploded", " ".join(res["uncomputed"]))
            self.assertEqual(res["summary"]["uncomputed"], 1)
            self.assertIn("ac_scope exploded", err.getvalue())

    def test_healthy_batch_reports_nothing_uncomputed(self) -> None:
        # The negative control: the honest field must not be permanently populated.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._batch(root)
            res = _load().audit_batch(root, ["CR0001"])
            self.assertEqual(res["uncomputed"], [])
            self.assertEqual(res["summary"]["uncomputed"], 0)

    def test_cli_exits_non_zero_and_does_not_print_a_clean_total(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._batch(root)
            mod = _load()
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(mod.ac_scope, "check",
                                   side_effect=RuntimeError("ac_scope exploded")):
                with redirect_stdout(out), redirect_stderr(err):
                    rc = mod.main(["check", "--ids", "CR0001", "--root", str(root)])
            self.assertEqual(rc, 1)  # a verdict that was not computed is not a pass
            self.assertIn("PARTIAL", out.getvalue())

    def test_cli_exit_is_zero_when_every_check_ran(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._batch(root)
            out = io.StringIO()
            with redirect_stdout(out):
                rc = _load().main(["check", "--ids", "CR0001", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertNotIn("PARTIAL", out.getvalue())


class AlreadySatisfiedTests(unittest.TestCase):
    """CR0098: a Ready unit whose verifiers all pass is flagged already-satisfied."""

    def _story(self, root, num=1, status="Ready"):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n\n## Acceptance Criteria\n\n"
            "### AC1\n- **Verify:** shell true\n", encoding="utf-8")

    def _report(self, root, stem, payload):
        import json
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps({"stories": {stem: payload}}), encoding="utf-8")

    def test_all_green_ready_unit_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1)
            self._report(root, "US0001-x", {"ac_count": 1, "verified": 1, "failed": 0, "stale": 0})
            r = _load().audit_unit(root, "US0001")
            self.assertIn("already-satisfied", r["issues"])

    def test_failing_unit_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 2)
            self._report(root, "US0002-x", {"ac_count": 2, "verified": 1, "failed": 1, "stale": 0})
            r = _load().audit_unit(root, "US0002")
            self.assertNotIn("already-satisfied", r["issues"])


class CR0109AuditChecks(unittest.TestCase):
    """The tranche audit flags non-executable Verify lines + cross-epic AC leakage."""

    def _story(self, root, num, verify=None, ac_text="given a thing, when acted, then result",
               epic="EP0001", status="Draft"):
        d = root / "sdlc-studio" / "stories"; d.mkdir(parents=True, exist_ok=True)
        v = f"- **Verify:** {verify}\n" if verify else ""
        (d / f"US{num:04d}-x.md").write_text(
            f"# US{num:04d}: s\n\n> **Status:** {status}\n> **Epic:** [{epic}](../epics/{epic}-x.md)\n\n"
            f"## Acceptance Criteria\n\n### AC1\n- {ac_text}\n{v}", encoding="utf-8")

    def test_weak_verify_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 1, verify="curl $API/x prints < 0.300")
            self.assertIn("weak-verify", _load().audit_unit(root, "US0001")["issues"])

    def test_executable_verify_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, 2, verify='jest "US0002 works"')
            self.assertNotIn("weak-verify", _load().audit_unit(root, "US0002")["issues"])

    def test_cross_epic_ac_single_keyword_is_advisory_not_blocking(self):
        # BG0192: one shared word is a coincidence. `ac_scope` documents itself as an advisory
        # keyword heuristic, and every finding it produced against this repo was ordinary
        # English ("fixes", "residual", "around"). It is reported, and it no longer blocks.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            (ed / "EP0001-x.md").write_text("# EP0001: authentication\n", encoding="utf-8")
            (ed / "EP0002-x.md").write_text("# EP0002: billing\n", encoding="utf-8")
            self._story(root, 1, ac_text="the billing total updates correctly", epic="EP0001")
            r = _load().audit_batch(root, ["US0001"])
            self.assertNotIn("cross-epic-ac", r["units"][0]["issues"])
            self.assertTrue(any("cross-epic-ac" in n for n in r["units"][0]["info"]))

    def test_a_blocking_hit_is_not_hidden_behind_an_earlier_advisory_one(self):
        # Findings sort by keyword, so a story with a 1-keyword coincidence that sorts FIRST
        # and a real 2-keyword leak must still block: the strongest hit per story wins, not
        # whichever happened to come out of the sort first.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            (ed / "EP0001-x.md").write_text("# EP0001: authentication\n", encoding="utf-8")
            (ed / "EP0002-x.md").write_text("# EP0002: billing invoices\n", encoding="utf-8")
            (ed / "EP0003-x.md").write_text("# EP0003: alpha handling\n", encoding="utf-8")
            self._story(root, 1, epic="EP0001",
                        ac_text="the alpha path reconciles billing against invoices")
            r = _load().audit_batch(root, ["US0001"])
            self.assertIn("cross-epic-ac", r["units"][0]["issues"])

    def test_cross_epic_ac_multi_keyword_still_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ed = root / "sdlc-studio" / "epics"; ed.mkdir(parents=True)
            (ed / "EP0001-x.md").write_text("# EP0001: authentication\n", encoding="utf-8")
            (ed / "EP0002-x.md").write_text("# EP0002: billing invoices\n", encoding="utf-8")
            self._story(root, 1, ac_text="the billing total and the invoices reconcile",
                        epic="EP0001")
            r = _load().audit_batch(root, ["US0001"])
            self.assertIn("cross-epic-ac", r["units"][0]["issues"])


class RegressionTestHeuristicTests(unittest.TestCase):
    """CR0128 heuristic 2: a Fixed/Done bug whose recorded tests have no integration/regression
    case is flagged. The check is a name-signal heuristic; proving the test hits the seams is a
    review judgement (the advisory boundary)."""

    def _bug_with(self, root, num, status, body_extra):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        body = (f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n\n"
                f"## Summary\n\nx\n\n## Steps to Reproduce\n\n1. do it\n\n"
                f"## Proposed Fix\n\ndo this\n{body_extra}\n")
        (d / f"BG{num:04d}-x.md").write_text(body, encoding="utf-8")
        return _load().audit_unit(root, f"BG{num:04d}")

    def test_fixed_bug_unit_test_only_is_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 1, "Fixed",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_widget.py::test_parse\n")
            self.assertIn("missing-regression-test", r["issues"])

    def test_fixed_bug_with_regression_test_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 2, "Fixed",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_regression.py::test_dispatch_loop\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_fixed_bug_with_integration_test_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 3, "Fixed",
                               "\n## Regression Test\n\nIntegration test at the router -> dispatcher seam.\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_open_bug_not_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 4, "Open",
                               "\n## Tests\n\n- **Verify:** pytest tests/test_widget.py::test_parse\n")
            self.assertNotIn("missing-regression-test", r["issues"])

    def test_fixed_bug_no_test_info_not_double_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            r = self._bug_with(root, 5, "Fixed", "")
            self.assertNotIn("missing-regression-test", r["issues"])

class FindingKindVocabularyTests(unittest.TestCase):
    """FINDING_KINDS must be the true emission vocabulary, not a restated answer key.

    The remediation guard (test_sdlc_md) derives its expected audit key set from
    audit.FINDING_KINDS; if that tuple could silently drift from audit_unit, the guard
    would inherit the same blind spot the bug exists to kill. This ties the tuple to
    what the module actually appends to a unit's `issues` by scanning the source, so an
    issue kind added without a FINDING_KINDS entry reddens here. Informational `info`
    notes use `info.extend`, not `issues.append`, so they are correctly excluded.
    """

    def test_finding_kinds_matches_issue_literals_in_source(self) -> None:
        src = SCRIPT.read_text(encoding="utf-8")
        emitted = set(re.findall(r'issues\.append\(\s*"([a-zA-Z-]+)', src))
        emitted |= set(re.findall(r'"issues":\s*\["([a-zA-Z-]+)"', src))
        self.assertEqual(
            emitted, set(_load().FINDING_KINDS),
            "FINDING_KINDS drifted from the issue literals audit_unit appends")


class PredicateFallThroughTests(unittest.TestCase):
    """The `return False` branches the mutation gate found unpinned (BG0212).

    Each of these predicates was tested for its TRUE case only, so the fall-through - the
    common case in practice, since most units are fine - could be inverted without a test
    noticing. A predicate whose negative answer is unpinned is half a predicate.
    """

    def test_weak_verify_is_false_when_every_verifier_is_sound(self) -> None:
        audit = _load()
        text = ("## Acceptance Criteria\n\n### AC1: x\n"
                "- **Verify:** pytest tests/test_thing.py -k specific_case\n")
        # assertIs, not assertFalse: these are annotated `-> bool`, and a stub returning
        # None is falsy, so assertFalse passes on a mutant that broke the contract.
        self.assertIs(audit._weak_verify(text), False)

    def test_missing_regression_test_is_false_when_nothing_mentions_a_test(self) -> None:
        # The early return: a unit that never mentions testing is not accused of MISSING a
        # regression test. Inverting this would flag every doc-only unit.
        audit = _load()
        self.assertIs(audit._missing_regression_test("# BG0001: x\n\nJust prose.\n"), False)

    def test_already_satisfied_is_false_when_the_report_has_no_such_story(self) -> None:
        # The loop's fall-through, reached whenever the verify-report does not mention the
        # unit - which is most of the time.
        audit = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "verify-report.json").write_text(
                '{"stories": {"US9999-other": {"verified": 3, "failed": 0, "stale": 0}}}',
                encoding="utf-8")
            self.assertIs(audit._already_satisfied(root, "US0001"), False)

    def test_already_satisfied_is_true_only_on_a_clean_matching_entry(self) -> None:
        # The positive branch beside it, so the test above cannot pass by the predicate
        # simply always returning False.
        audit = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "verify-report.json").write_text(
                '{"stories": {"US0001-x": {"verified": 3, "failed": 0, "stale": 0}}}',
                encoding="utf-8")
            self.assertIs(audit._already_satisfied(root, "US0001"), True)


class CheckSelectionModeTests(unittest.TestCase):
    """`audit check` takes ids OR a status query, never both and never neither (BG0212)."""

    def _run(self, *argv):
        import subprocess
        skill = Path(__file__).resolve().parent.parent
        return subprocess.run([sys.executable, "-B", str(skill / "readiness.py"), *argv],
                              capture_output=True, text=True)

    def test_neither_ids_nor_a_query_is_refused(self) -> None:
        proc = self._run("check")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("exactly one selection mode", proc.stderr)

    def test_both_ids_and_a_query_is_refused(self) -> None:
        proc = self._run("check", "--id", "US0001", "--stories", "Ready")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("exactly one selection mode", proc.stderr)

    def test_a_status_query_actually_selects_the_batch(self) -> None:
        """The query path resolves ids, rather than auditing an empty set.

        Every other test here passes ids explicitly, so the `ids = [...select_batch...]`
        line was unpinned: neutralising it left the batch EMPTY, and an empty batch audits
        clean and exits 0 - a false green over work never examined.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed", ac=TAUTOLOGY)   # weak AC -> not ready
            proc = self._run("check", "--crs", "Proposed", "--root", str(root))
            self.assertEqual(proc.returncode, 1, f"out={proc.stdout} err={proc.stderr}")
            self.assertIn("CR0001", proc.stdout)
            # The count is the anti-vacuity half: an emptied batch prints "0/0 ready, 0 not"
            # and would satisfy an assertion that only looked for the id.
            self.assertIn("tranche audit: 0/1 ready, 1 not", proc.stdout)


SCRIPTS_DIR = SCRIPT.parent
TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS_DIR.parent

# The old module identifiers this rename retired. A shipped file matching any of these
# has a caller the rename left behind. Bare `"audit"` is deliberately NOT here: it is a
# valid remediation-registry key (`sdlc_md.REMEDIATION["audit"]`) and a lens-profile name,
# neither of which the rename touches - only module-name references move.
_OLD_MODULE_PATTERNS = (
    re.compile(r"\baudit\.py\b"),
    re.compile(r"\baudit_check\b"),
    re.compile(r"^\s*import audit\b", re.M),
    re.compile(r"""_load\(\s*["']audit["']"""),
    re.compile(r"""load_script\(\s*["']audit["']\s*\)"""),
    re.compile(r"""sys\.modules\[\s*["']audit["']\s*\]"""),
)


# This detector file is the one shipped file that MUST name the retired modules: it defines
# the patterns below and asserts the old files are gone. A linter does not lint its own rule
# definitions, so it is excluded from the reference sweeps (its own imports are pinned by the
# rest of this suite loading `readiness`/`schema_check`, never `audit`/`audit_check`).
_DETECTOR = Path(__file__).name


def _shipped_py_files():
    for p in sorted(SCRIPTS_DIR.rglob("*.py")):
        if "__pycache__" not in p.parts and p.name != _DETECTOR:
            yield p


def _load_schema_check():
    spec = importlib.util.spec_from_file_location("schema_check", SCRIPTS_DIR / "schema_check.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["schema_check"] = mod
    spec.loader.exec_module(mod)
    return mod


class RenameTests(unittest.TestCase):
    """RFC0033 D1 / US0345: the deterministic scripts moved off the `audit` stem.

    The `audit` verb belongs to the user-facing adversarial weakness-hunt; the two
    deterministic scripts are renamed - `audit.py` -> `readiness.py`, `audit_check.py`
    -> `schema_check.py` - and every caller moves with them.
    """

    def test_no_shipped_file_references_the_old_module_names(self):
        self.assertTrue((SCRIPTS_DIR / "readiness.py").is_file(), "readiness.py must exist")
        self.assertTrue((SCRIPTS_DIR / "schema_check.py").is_file(), "schema_check.py must exist")
        self.assertFalse((SCRIPTS_DIR / "audit.py").exists(), "old audit.py must be gone")
        self.assertFalse((SCRIPTS_DIR / "audit_check.py").exists(), "old audit_check.py must be gone")
        offenders = []
        for p in _shipped_py_files():
            text = p.read_text(encoding="utf-8")
            for pat in _OLD_MODULE_PATTERNS:
                if pat.search(text):
                    offenders.append(f"{p.relative_to(SKILL_DIR)}: /{pat.pattern}/")
        self.assertEqual(offenders, [], "a rename that leaves a caller behind is a rename that "
                         "has not happened:\n" + "\n".join(offenders))

    def test_gate_and_sprint_call_sites_resolve_and_behave_identically(self):
        # The tranche pre-flight (documented in the sprint flow) and the schema linter
        # (the CI/gate step) both resolve under their new names and expose the API their
        # importers use. NOTE: the in-repo Python importers are handoff.py and artifact.py;
        # gate.py and sprint.py invoke the deterministic scripts as documented/CI steps, not
        # as code imports (verified in the same sweep as the AC1 test above).
        readiness = _load()
        for attr in ("audit_unit", "find_artifact", "build_parser", "cmd_check"):
            self.assertTrue(hasattr(readiness, attr), f"readiness.{attr} missing after rename")
        schema_check = _load_schema_check()
        for attr in ("run", "main", "RULE_IDS"):
            self.assertTrue(hasattr(schema_check, attr), f"schema_check.{attr} missing after rename")
        # the real importers reach for the new name, not the old one
        for name in ("handoff.py", "artifact.py"):
            src = (SCRIPTS_DIR / name).read_text(encoding="utf-8")
            self.assertIn("readiness", src, f"{name} must reference the renamed module")
            self.assertNotRegex(src, r"\bimport audit\b", f"{name} still imports the old module")
        # A rename must change no verdict: the same input yields the same readiness result.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cr(root, 1, status="Proposed", ac=TAUTOLOGY)   # a vacuous AC -> not ready
            verdict = readiness.audit_unit(root, "CR0001")
            self.assertFalse(verdict["ready"], "a tautology AC must still audit as not-ready")
            self.assertIn("weak-AC", verdict["issues"])
            _cr(root, 2, status="Proposed",
                ac="- [ ] integrity.py exits 1 when an active story lacks its Epic link")
            self.assertTrue(readiness.audit_unit(root, "CR0002")["ready"],
                            "a checkable AC must still audit as ready")

    def test_the_public_audit_command_is_unchanged(self):
        # `audit --profile repo` runs the user-facing weakness-hunt; its engine (profile
        # resolution) still lives in the renamed module and the public surface must not move.
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "profile", "--name", "repo", "--format", "json"],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"out={proc.stdout} err={proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data["name"], "repo")
        self.assertTrue(data["lenses"], "the repo audit profile must still resolve its lenses")
        # the command itself is still catalogued under the `audit` verb
        help_help = (SKILL_DIR / "help" / "help.md").read_text(encoding="utf-8")
        self.assertIn("/sdlc-studio audit", help_help)


class RenameDocsTests(unittest.TestCase):
    """US0346: the test suites and the scripts catalogue move with their subjects."""

    def test_the_suites_are_renamed_and_green(self):
        self.assertTrue((TESTS_DIR / "test_readiness.py").is_file())
        self.assertTrue((TESTS_DIR / "test_schema_check.py").is_file())
        self.assertFalse((TESTS_DIR / "test_audit.py").exists())
        self.assertFalse((TESTS_DIR / "test_audit_check.py").exists())
        # no test file references the old module names (this file included)
        offenders = []
        for p in sorted(TESTS_DIR.glob("test_*.py")):
            if p.name == _DETECTOR:   # the detector names the old modules by design (see above)
                continue
            text = p.read_text(encoding="utf-8")
            for pat in _OLD_MODULE_PATTERNS:
                if pat.search(text):
                    offenders.append(f"{p.name}: /{pat.pattern}/")
        self.assertEqual(offenders, [], "\n".join(offenders))
        # both suites import cleanly (their passing is enforced by the discovery run this
        # test is part of); the catalogue lists the new names
        self.assertTrue(_load_schema_check())
        catalogue = (SKILL_DIR / "reference-scripts.md").read_text(encoding="utf-8")
        self.assertIn("readiness.py", catalogue)
        self.assertIn("schema_check.py", catalogue)


class SignatureDetectorCoverageTests(unittest.TestCase):
    """Every detector shape is exercised through the SHIPPED parser, not a synthetic fixture.

    Measured over `templates/audit-profiles/*.md`, the packs use `python3` (8 rows) and `rg`
    (1). `bash` and `npm` appear in none - so two of the four shapes were reaching the parser
    only through a fixture built for them, and deleting either runner from the tuple was caught
    by nothing a real pack could notice.

    The vocabulary is deliberately WIDER than this repo's packs use, because a consuming
    project writes its own signatures. So the fix is to exercise each shape against the real
    function, not to narrow the tuple to what one repo happens to need.
    """

    def _mod(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "readiness", Path(__file__).resolve().parent.parent / "readiness.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["readiness"] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_each_detector_is_recognised_by_the_shipped_parser(self) -> None:
        """MUTANT: delete ANY single runner from SIGNATURE_DETECTORS.

        One assertion per runner, because `all(mechanical)` over the packs passes with the two
        unused runners removed - the packs never exercise them.
        """
        mod = self._mod()
        for signature in ("bash tools/x.sh", "npm run lint",
                          "python3 tools/x.py", "rg -n 'x' src/"):
            with self.subTest(signature=signature):
                self.assertTrue(mod._signature_is_mechanical(signature),
                                f"{signature!r} is not recognised, so its runner is unreachable")

    def test_a_bare_npm_is_still_refused(self) -> None:
        """MUTANT: drop the `npm run` rule so a bare `npm` passes.

        `npm` alone runs an install, not a check, so accepting it would call an unrunnable
        signature mechanical.
        """
        mod = self._mod()
        self.assertFalse(mod._signature_is_mechanical("npm lint"),
                         "a bare `npm` was accepted as a mechanical signature")

    def test_a_detector_named_mid_sentence_is_not_mechanical(self) -> None:
        """MUTANT: widen the head test to `any(t in SIGNATURE_DETECTORS for t in tokens)`.

        Only a prose reason that MENTIONS a detector catches this, so the fixture must contain
        one.
        """
        mod = self._mod()
        self.assertFalse(
            mod._signature_is_mechanical("manual - a reviewer runs python3 by hand"),
            "a prose reason mentioning a detector was read as a mechanical signature")


if __name__ == "__main__":
    unittest.main()
