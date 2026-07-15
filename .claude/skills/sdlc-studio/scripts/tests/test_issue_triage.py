"""Unit tests for the discovery track: the Issue type and the triage ceremony (RFC0039, EP0038).

The Issue is the defect-side DISCOVERY item: a raw report triaged into the bugs that deliver its
fix, the mirror of a request refined into stories. These tests pin:

- the vocabulary (`is_discovery` includes the Issue; `is_request` does not) - US0137;
- the artefact type (create + validate + prefix + sizing) - US0138;
- the triage command (apply/show, atomicity, the refusals) - US0139;
- the gates (G1 plan-refuse, the undecomposed check, G2 terminal-derivation) - US0140;
- refine show accepting an already-decomposed request (CR0275) - US0142.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
from lib import sdlc_md  # noqa: E402
artifact = _load("artifact", "artifact.py")
reconcile = _load("reconcile", "reconcile.py")
transition = _load("transition", "transition.py")
status = _load("status", "status.py")
sprint = _load("sprint", "sprint.py")
refine = _load("refine", "refine.py")
triage = _load("triage", "triage.py")
validate = _load("validate", "validate.py")


def _enforce(root: Path, *, v3: bool = False) -> None:
    p = root / "sdlc-studio" / ".config.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    head = "schema_version: 3\n" if v3 else ""
    p.write_text(head + "two_backlog:\n  enforce: true\n", encoding="utf-8")


def _new_issue(root: Path, title: str = "Checkout 500s", severity: str = "High",
               size: str = "M") -> str:
    """Create an Issue via the deterministic creator; return its id."""
    res = artifact.new(root, "issue", title,
                       {"size": size, "severity": severity, "summary": "A raw report."})
    return res["id"]


def _touch_affects(root: Path, *rel: str) -> None:
    """Create the files a triaged bug's Affects must resolve to (the grooming gate checks they
    exist on disk)."""
    for r in rel:
        p = root / r
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")


# --- US0137: the discovery vocabulary --------------------------------------------------------

class DiscoveryVocabTests(unittest.TestCase):
    def test_is_discovery_includes_issue_is_request_does_not(self) -> None:
        # An Issue is a Discovery item but NOT a request: refined vs triaged must not conflate.
        self.assertTrue(sdlc_md.is_discovery("issue"))
        self.assertTrue(sdlc_md.is_discovery("cr"))
        self.assertTrue(sdlc_md.is_discovery("rfc"))
        self.assertFalse(sdlc_md.is_request("issue"))
        self.assertTrue(sdlc_md.is_request("cr"))

    def test_delivery_types_are_not_discovery(self) -> None:
        for t in ("story", "bug", "epic"):
            self.assertFalse(sdlc_md.is_discovery(t), t)

    def test_issue_status_vocab_and_terminals(self) -> None:
        self.assertEqual(sdlc_md.create_status("issue"), "Open")
        # Resolved is the DERIVED successful terminal (first absorbing in vocab order).
        self.assertEqual(sdlc_md.default_terminal_status("issue"), "Resolved")
        self.assertIn("Resolved", sdlc_md.terminal_statuses("issue"))
        self.assertIn("Won't Fix", sdlc_md.terminal_statuses("issue"))
        self.assertFalse(sdlc_md.is_terminal_status("issue", "Triaging"))
        self.assertFalse(sdlc_md.is_terminal_status("issue", "Triaged"))


# --- US0138: the Issue artefact type ---------------------------------------------------------

class IssueArtefactTests(unittest.TestCase):
    def test_create_writes_size_severity_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            iid = _new_issue(root, size="M", severity="High")
            self.assertEqual(iid, "IS0001")
            text = (root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md").read_text()
            self.assertEqual(sdlc_md.extract_field(text, "Status"), "Open")
            self.assertEqual(sdlc_md.read_size(text), "M")
            self.assertEqual(sdlc_md.extract_field(text, "Severity"), "High")
            # An Issue is NOT a delivery unit: no Points.
            self.assertIsNone(sdlc_md.read_points(text))
            self.assertIn("## Report", text)

    def test_id_prefix_parses(self) -> None:
        self.assertEqual(sdlc_md.extract_record_id("IS0007-a-thing"), "IS0007")
        self.assertEqual(sdlc_md.ARTIFACT_TYPES["issue"], ("sdlc-studio/issues", "IS"))

    def test_created_issue_validates_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _new_issue(root)
            path = root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md"
            errs = [f for f in validate.validate_file(path, "issue", root)
                    if f.get("level") == "error"]
            self.assertEqual(errs, [], errs)

    def test_created_issue_leaves_reconcile_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _new_issue(root)
            # per-type census (index rows vs files vs summary) is clean for the new issue index
            self.assertEqual(reconcile.detect_type("issue", root)["drift"], [])


# --- US0139: the triage command --------------------------------------------------------------

class TriageTests(unittest.TestCase):
    def test_triage_mints_bugs_and_wires_both_sides(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py", "src/b.py")
            iid = _new_issue(root)
            res = triage.triage(root, iid,
                                [("Null total throws", 3, "High", "src/a.py"),
                                 ("Retry storm", 5, "Medium", "src/b.py")])
            self.assertEqual(res["bugs"], ["BG0001", "BG0002"])
            self.assertEqual(res["points"], 8)
            self.assertEqual(res["status"], "Triaged")
            issue = (root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md").read_text()
            self.assertEqual(sdlc_md.decomposed_ids(issue), ["BG0001", "BG0002"])
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Triaged")
            for bid in ("BG0001", "BG0002"):
                bpath, _ = sdlc_md.find_by_id(root, bid)
                self.assertEqual(sdlc_md.child_parent(bpath.read_text()), iid)
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_triage_refuses_a_non_issue(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")
            # a CR is refined, not triaged
            artifact.new(root, "cr", "A change", {"size": "M", "priority": "P2", "affects": "src/a.py",
                         "ctype": "Feature", "summary": "s", "impact": "i", "acs": ["a"]})
            with self.assertRaises(ValueError):
                triage.triage(root, "CR0001", [("x", 2, "Low", "src/a.py")])

    def test_triage_refuses_an_already_triaged_issue(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")
            iid = _new_issue(root)
            triage.triage(root, iid, [("b1", 2, "Low", "src/a.py")])
            with self.assertRaises(ValueError):
                triage.triage(root, iid, [("b2", 2, "Low", "src/a.py")])

    def test_triage_refuses_empty_breakdown(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            iid = _new_issue(root)
            with self.assertRaises(ValueError):
                triage.triage(root, iid, [])

    def test_triage_is_atomic_a_bad_bug_mints_nothing(self) -> None:
        # The 2nd bug's Affects does not resolve: grooming fails at pre-flight, so NEITHER bug is
        # minted and the Issue is untouched (no orphan file, no orphan index row, still Open).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")   # only the first exists
            iid = _new_issue(root)
            with self.assertRaises(ValueError):
                triage.triage(root, iid,
                              [("good", 2, "Low", "src/a.py"),
                               ("bad", 3, "Low", "src/does-not-exist.py")])
            issue = (root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md").read_text()
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Open")
            self.assertEqual(sdlc_md.decomposed_ids(issue), [])
            self.assertEqual(list((root / "sdlc-studio" / "bugs").glob("BG*.md")), [])

    def test_triage_off_scale_points_mints_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")
            _new_issue(root)
            with self.assertRaises(ValueError):
                triage.parse_bug_spec("a title|4|Low|src/a.py")   # 4 is off the Fibonacci scale

    def test_triage_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")
            iid = _new_issue(root)
            res = triage.triage(root, iid, [("b", 2, "Low", "src/a.py")], dry_run=True)
            self.assertTrue(res["dry_run"])
            issue = (root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md").read_text()
            self.assertEqual(sdlc_md.decomposed_ids(issue), [])
            self.assertEqual(list((root / "sdlc-studio" / "bugs").glob("BG*.md")), [])

    def test_parse_bug_spec_defaults_severity(self) -> None:
        self.assertEqual(triage.parse_bug_spec("a title|3"), ("a title", 3, "Medium", None))
        self.assertEqual(triage.parse_bug_spec("t|5|High|src/x.py"), ("t", 5, "High", "src/x.py"))

    def test_same_title_bugs_coexist(self) -> None:
        # two bugs with the SAME title get distinct ids (part of the filename), so no slug
        # collision - both mint, no rollback, no orphan.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py")
            iid = _new_issue(root)
            res = triage.triage(root, iid,
                                [("Same title", 2, "Low", "src/a.py"),
                                 ("Same title", 3, "Low", "src/a.py")])
            self.assertEqual(len(res["bugs"]), 2)
            self.assertEqual(len(set(res["bugs"])), 2)          # distinct ids
            self.assertEqual(reconcile.detect_type("bug", root)["drift"], [])

    def test_v3_low_severity_triage_mints_individual_bugs_not_a_cr(self) -> None:
        # Regression guard: on a schema-v3 project a Low-severity bug is normally folded into a
        # consolidation CR by the finding-noise controls. A TRIAGED bug is a deliberate
        # decomposition unit and must bypass that (consolidate=False), or the Issue would be wired
        # to a CR instead of a bug and the preflight (which cannot see the divergence) would pass.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root, v3=True)
            _touch_affects(root, "src/a.py", "src/b.py")
            iid = _new_issue(root)
            res = triage.triage(root, iid,
                                [("A low bug", 2, "Low", "src/a.py"),
                                 ("A high bug", 3, "High", "src/b.py")])
            self.assertEqual(len(res["bugs"]), 2)
            # every child is a BUG, never a consolidation CR
            for bid in res["bugs"]:
                self.assertTrue(sdlc_md.norm_id(bid).startswith("BG"), bid)
            self.assertEqual(list((root / "sdlc-studio" / "change-requests").glob("CR*.md")), [])
            issue_path, _ = sdlc_md.find_by_id(root, iid)
            children = sdlc_md.children_of(root, iid)
            self.assertTrue(all(t == "bug" for _, t in children), children)
            self.assertEqual(reconcile.detect_type("bug", root)["drift"], [])


# --- US0140: the gates -----------------------------------------------------------------------

class IssueGateTests(unittest.TestCase):
    def test_plan_refuses_an_issue_when_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _new_issue(root)
            wl = root / "wl.txt"
            wl.write_text("IS0001\n", encoding="utf-8")
            rc = sprint.main(["plan", "--worklist", str(wl), "--root", str(root), "--no-fetch"])
            self.assertEqual(rc, 2)

    def test_open_issue_not_flagged_triaging_childless_is(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            iid = _new_issue(root)
            # Open is intake - not flagged.
            self.assertEqual(reconcile.undecomposed_drift(root), [])
            # Accepted (Triaging) but childless - flagged as needs-triage.
            transition.transition(root, iid, "Triaging")
            drift = reconcile.undecomposed_drift(root)
            self.assertEqual([x["id"] for x in drift], [iid])
            self.assertIn("triage it into the bugs", drift[0]["fix"])

    def test_issue_resolved_is_derived_from_children(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch_affects(root, "src/a.py", "src/b.py")
            iid = _new_issue(root)
            triage.triage(root, iid, [("b1", 2, "Low", "src/a.py"), ("b2", 3, "Low", "src/b.py")])
            # bugs still Open -> Resolved is blocked (G2)
            with self.assertRaises(ValueError):
                transition.transition(root, iid, "Resolved")
            # resolve both bugs (force past the unrelated verification-depth gate), then it passes
            transition.transition(root, "BG0001", "Fixed", force=True)
            transition.transition(root, "BG0002", "Won't Fix", force=True)
            transition.transition(root, iid, "Resolved")
            issue = (root / "sdlc-studio" / "issues" / "IS0001-checkout-500s.md").read_text()
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Resolved")

    def test_childless_issue_cannot_be_resolved_by_assertion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            iid = _new_issue(root)
            with self.assertRaises(ValueError):
                transition.transition(root, iid, "Resolved")
            # but it CAN be closed as Won't Fix without children (asserts no delivery)
            transition.transition(root, iid, "Won't Fix")

    def test_status_backlog_buckets_issue_under_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _new_issue(root)
            data = status.backlog(root, ("issue", "bug", "cr", "rfc", "story", "epic"))
            summary = status._two_backlog_summary(data)
            self.assertIn("issue", summary["discovery"]["types"])
            self.assertNotIn("issue", summary["delivery"]["types"])


# --- US0142 (CR0275): refine show on an already-decomposed request ----------------------------

class RefineShowDecomposedTests(unittest.TestCase):
    def _decomposed_cr(self, root: Path) -> str:
        _enforce(root)
        _touch_affects(root, "src/a.py")
        artifact.new(root, "cr", "A change", {"size": "M", "priority": "P2", "affects": "src/a.py",
                     "ctype": "Feature", "summary": "s", "impact": "i", "acs": ["a"]})
        refine.refine(root, "CR0001", "The epic", [("A story", 2, "src/a.py")])
        return "CR0001"

    def test_show_accepts_a_decomposed_request_and_lists_epics(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cid = self._decomposed_cr(root)
            info = refine.refinable(root, cid, allow_decomposed=True)
            self.assertTrue(info["decomposed_into"])       # lists its existing epic(s)
            self.assertTrue(info["decomposed_into"][0].startswith("EP"))

    def test_apply_still_refuses_a_decomposed_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cid = self._decomposed_cr(root)
            with self.assertRaises(ValueError):
                refine.refinable(root, cid)   # default allow_decomposed=False
            with self.assertRaises(ValueError):
                refine.refine(root, cid, "x", [("y", 2, None)])

    def test_show_still_refuses_a_non_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _new_issue(root)
            with self.assertRaises(ValueError):
                refine.refinable(root, "IS0001", allow_decomposed=True)


if __name__ == "__main__":
    unittest.main()
