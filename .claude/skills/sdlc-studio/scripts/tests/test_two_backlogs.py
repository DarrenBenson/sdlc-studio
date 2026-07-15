"""Unit tests for the two-backlog gates (CR0271 / RFC0038 U6).

The shared fixture builds one request->product chain on disk:

    RFC0100  (request)
      -> CR0100  (request, Parent: RFC0100)
           -> EP0100  (epic, Parent: CR0100)
                -> US0100, US0101  (stories, Epic: EP0100)

so the link primitive (US0120), the derived-status gate (US0122), the two-backlog
status view (US0123) and the UNDECOMPOSED drift check (US0124) all test against the
same shape.

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


# lib/ is importable as `from lib import sdlc_md` from the scripts dir.
sys.path.insert(0, str(_SCRIPTS))
from lib import sdlc_md  # noqa: E402
reconcile = _load("reconcile", "reconcile.py")
transition = _load("transition", "transition.py")
status = _load("status", "status.py")
sprint = _load("sprint", "sprint.py")
artifact = _load("artifact", "artifact.py")
file_finding = _load("file_finding", "file_finding.py")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_chain(root: Path, *, cr_children: str = "EP0100",
                epic_parent: str = "CR0100") -> None:
    """The canonical RFC -> CR -> epic -> stories chain, links symmetric by default.
    `cr_children` / `epic_parent` let a test break one side to force asymmetry."""
    base = root / "sdlc-studio"
    _write(base / "rfcs" / "RFC0100-a-request.md",
           "# RFC-0100: A request\n\n> **Status:** Accepted\n"
           "> **Decomposed-into:** CR0100\n")
    _write(base / "change-requests" / "CR0100-a-change.md",
           "# CR-0100: A change\n\n> **Status:** Proposed\n> **Size:** M\n"
           "> **Parent:** RFC0100\n"
           f"> **Decomposed-into:** {cr_children}\n")
    _write(base / "epics" / "EP0100-an-epic.md",
           "# EP0100: An epic\n\n> **Status:** Draft\n> **Size:** M\n"
           f"> **Parent:** {epic_parent}\n")
    for sid, status in (("US0100", "Done"), ("US0101", "Draft")):
        _write(base / "stories" / f"{sid}-a-story.md",
               f"# {sid}: A story\n\n> **Status:** {status}\n> **Epic:** EP0100\n"
               "> **Points:** 2\n")


class TaxonomyTests(unittest.TestCase):
    def test_request_vs_product(self) -> None:
        self.assertTrue(sdlc_md.is_request("cr"))
        self.assertTrue(sdlc_md.is_request("rfc"))
        self.assertFalse(sdlc_md.is_request("story"))
        self.assertFalse(sdlc_md.is_request("epic"))
        self.assertFalse(sdlc_md.is_request("bug"))


class LinkPrimitiveTests(unittest.TestCase):
    def test_parent_ref_and_child_parent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root)
            epic = (root / "sdlc-studio" / "epics" / "EP0100-an-epic.md").read_text()
            story = (root / "sdlc-studio" / "stories" / "US0100-a-story.md").read_text()
            # an epic names its parent with the generic Parent: field
            self.assertEqual(sdlc_md.parent_ref(epic), "CR0100")
            self.assertEqual(sdlc_md.child_parent(epic), "CR0100")
            # a story has no Parent:, but child_parent falls back to its Epic:
            self.assertIsNone(sdlc_md.parent_ref(story))
            self.assertEqual(sdlc_md.child_parent(story), "EP0100")

    def test_decomposed_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root)
            cr = (root / "sdlc-studio" / "change-requests" / "CR0100-a-change.md").read_text()
            self.assertEqual(sdlc_md.decomposed_ids(cr), ["EP0100"])

    def test_decomposed_ids_ignores_parenthetical_grandchildren(self) -> None:
        # A parenthetical is an annotation (what the epic holds), NOT a list of the request's
        # direct children - the stories carry Epic:, not Parent: the CR. Grabbing them made
        # link_asymmetry_drift falsely flag a correctly-linked chain.
        cr = ("# CR-0100\n\n> **Status:** Proposed\n"
              "> **Decomposed-into:** EP0033 (US0120, US0121, US0122)\n")
        self.assertEqual(sdlc_md.decomposed_ids(cr), ["EP0033"])
        # Multiple direct children with a trailing annotation still read as the two epics only.
        cr2 = "> **Decomposed-into:** EP0033, EP0034 (both P1)\n"
        self.assertEqual(sdlc_md.decomposed_ids(cr2), ["EP0033", "EP0034"])

    def test_symmetric_chain_clean_with_annotated_decomposed_into(self) -> None:
        # The annotated form must be as clean as the bare form: the parenthetical grandchildren
        # must not be back-checked against the request.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root, cr_children="EP0100 (US0100, US0101)")
            self.assertEqual(reconcile.link_asymmetry_drift(root), [])

    def test_children_of_resolves_each_level(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root)
            self.assertEqual(sdlc_md.children_of(root, "RFC0100"), [("CR0100", "cr")])
            self.assertEqual(sdlc_md.children_of(root, "CR0100"), [("EP0100", "epic")])
            self.assertEqual(
                sdlc_md.children_of(root, "EP0100"),
                [("US0100", "story"), ("US0101", "story")])

    def test_childless_request_has_no_children(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root)
            # CR0100 exists but nothing names EP9999
            self.assertEqual(sdlc_md.children_of(root, "EP9999"), [])


class LinkAsymmetryDriftTests(unittest.TestCase):
    def test_symmetric_chain_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root)
            self.assertEqual(reconcile.link_asymmetry_drift(root), [])

    def test_parent_resolves_to_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root, epic_parent="CR9999")  # epic points at a missing CR
            kinds = {(x["kind"], x["id"]) for x in reconcile.link_asymmetry_drift(root)}
            self.assertIn(("link-asymmetry", "EP0100"), kinds)

    def test_parent_does_not_name_child_back(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # CR lists no children, but the epic still names the CR as Parent -> one-sided
            build_chain(root, cr_children="-")
            drift = reconcile.link_asymmetry_drift(root)
            ids = {x["id"] for x in drift}
            self.assertIn("EP0100", ids)

    def test_decomposed_entry_that_resolves_to_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_chain(root, cr_children="EP0100, EP7777")  # EP7777 does not exist
            drift = reconcile.link_asymmetry_drift(root)
            ids = {x["id"] for x in drift}
            self.assertIn("EP7777", ids)


class TwoBacklogStatusTests(unittest.TestCase):
    """G4 (US0123): status splits the request backlog from the product backlog."""

    def _make(self, root: Path) -> None:
        _write(root / "sdlc-studio" / "change-requests" / "CR0400-x.md",
               "# CR-0400: X\n\n> **Status:** Proposed\n> **Size:** M\n")
        _write(root / "sdlc-studio" / "rfcs" / "RFC0400-x.md",
               "# RFC0400: X\n\n> **Status:** Draft\n")
        _write(root / "sdlc-studio" / "stories" / "US0400-x.md",
               "# US0400: X\n\n> **Status:** Ready\n> **Epic:** EP0400\n> **Points:** 2\n")
        _write(root / "sdlc-studio" / "bugs" / "BG0400-x.md",
               "# BG0400: X\n\n> **Status:** Open\n> **Points:** 2\n")

    def test_summary_partitions_by_is_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            data = status.backlog(root)
            summary = status._two_backlog_summary(data)
            self.assertEqual(summary["discovery"]["count"], 2)   # cr + rfc
            self.assertEqual(set(summary["discovery"]["types"]), {"cr", "rfc"})
            self.assertEqual(summary["delivery"]["count"], 2)    # story + bug
            self.assertEqual(set(summary["delivery"]["types"]), {"bug", "story"})

    def test_text_output_labels_both_backlogs(self) -> None:
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                status.main(["backlog", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Discovery backlog", out)
            self.assertIn("Delivery backlog", out)
            # a request type appears under Discovery, a product type under Delivery
            disc_idx, del_idx = out.index("Discovery backlog"), out.index("Delivery backlog")
            self.assertLess(disc_idx, out.index("cr:"))
            self.assertLess(del_idx, out.index("bug:"))

    def test_json_keeps_per_type_keys_and_adds_backlogs(self) -> None:
        import io
        import json as _json
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                status.main(["backlog", "--root", str(root), "--format", "json"])
            j = _json.loads(buf.getvalue())
            self.assertIn("cr", j)                       # per-type keys unchanged (back-compat)
            self.assertEqual(j["backlogs"]["discovery"]["count"], 2)
            self.assertEqual(j["backlogs"]["delivery"]["count"], 2)


class DerivedStatusTests(unittest.TestCase):
    """G2 (US0122): a request's SUCCESSFUL terminal is derived from its children. Uses
    dry_run=True, which runs the pre-write gate then returns without writing - so the gate is
    tested without a full index fixture."""

    def _cr(self, root: Path, cid: str, status: str, decomposed: str = "") -> None:
        extra = f"> **Decomposed-into:** {decomposed}\n" if decomposed else ""
        _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
               f"# CR-{cid[2:]}: X\n\n> **Status:** {status}\n> **Size:** M\n{extra}")

    def _epic(self, root: Path, eid: str, status: str, parent: str) -> None:
        _write(root / "sdlc-studio" / "epics" / f"{eid}-x.md",
               f"# {eid}: X\n\n> **Status:** {status}\n> **Size:** M\n> **Parent:** {parent}\n")

    def test_cr_blocked_while_child_unfinished(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0300", "Approved", decomposed="EP0300")
            self._epic(root, "EP0300", "Draft", "CR0300")   # child not done
            with self.assertRaises(ValueError) as cm:
                transition.transition(root, "CR0300", "Complete", dry_run=True)
            self.assertIn("EP0300", str(cm.exception))

    def test_childless_cr_cannot_complete_but_can_reject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0301", "Approved")
            with self.assertRaises(ValueError):
                transition.transition(root, "CR0301", "Complete", dry_run=True)
            # Rejected asserts no delivery, so a childless request may still be closed that way
            res = transition.transition(root, "CR0301", "Rejected", dry_run=True)
            self.assertEqual(res["to"], "Rejected")

    def test_cr_completes_when_children_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0302", "Approved", decomposed="EP0302")
            self._epic(root, "EP0302", "Done", "CR0302")
            res = transition.transition(root, "CR0302", "Complete", dry_run=True)
            self.assertEqual(res["to"], "Complete")

    def test_cr_force_overrides_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0303", "Approved")   # childless
            res = transition.transition(root, "CR0303", "Complete", dry_run=True, force=True)
            self.assertEqual(res["to"], "Complete")

    def test_rfc_accepted_requires_child_crs_complete(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "rfcs" / "RFC0300-x.md",
                   "# RFC0300: X\n\n> **Status:** In Review\n> **Decomposed-into:** CR0310\n")
            # child CR still open -> RFC cannot be Accepted
            self._cr(root, "CR0310", "Approved", decomposed="")
            _write(root / "sdlc-studio" / "change-requests" / "CR0310-x.md",
                   "# CR-0310: X\n\n> **Status:** Approved\n> **Size:** M\n> **Parent:** RFC0300\n")
            with self.assertRaises(ValueError):
                transition.transition(root, "RFC0300", "Accepted", dry_run=True)
            # complete the child CR -> RFC may be Accepted
            _write(root / "sdlc-studio" / "change-requests" / "CR0310-x.md",
                   "# CR-0310: X\n\n> **Status:** Complete\n> **Size:** M\n> **Parent:** RFC0300\n")
            res = transition.transition(root, "RFC0300", "Accepted", dry_run=True)
            self.assertEqual(res["to"], "Accepted")


class CreatorAgreementTests(unittest.TestCase):
    """BG0148 + BG0149: artifact.py (the canonical creator) writes the RIGHT sizing field per
    type, from the same sdlc_md definition the finding filer uses - so the two creators cannot
    disagree on what a type is sized by (LL0016)."""

    def test_bg0149_story_points_are_written(self) -> None:
        # BG0149: `artifact new --type story --points 5` used to SILENTLY DROP the points.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            artifact.new(root, "epic", "e", {"size": "M"})
            eid = sdlc_md.extract_record_id(
                next((root / "sdlc-studio" / "epics").glob("EP*.md")).stem)
            r = artifact.new(root, "story", "s", {"epic": eid, "points": 5})
            text = Path(r["path"]).read_text()
            self.assertEqual(sdlc_md.read_points(text), 5)

    def test_bg0148_cr_carries_size_not_points(self) -> None:
        # BG0148: a CR is a REQUEST - artifact.py must write a T-shirt Size, never points.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            r = artifact.new(root, "cr", "c", {"affects": "src/x.py", "size": "M", "impact": "x"})
            text = Path(r["path"]).read_text()
            self.assertEqual(sdlc_md.read_size(text), "M")
            self.assertIsNone(sdlc_md.read_points(text))

    def test_both_creators_agree_on_a_cr_size_shape(self) -> None:
        # The heart of BG0148: artifact.new and the finding filer produce the SAME Size shape.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            a = artifact.new(root, "cr", "via new",
                             {"affects": "src/x.py", "size": "L", "impact": "x"})
            b = file_finding.file_finding(
                root, "cr", "via filer",
                {"affects": "src/y.py", "size": "L", "impact": "y", "priority": "Medium",
                 "ctype": "Improvement", "summary": "s", "acs": ["a"]})
            self.assertEqual(sdlc_md.read_size(Path(a["path"]).read_text()), "L")
            self.assertEqual(sdlc_md.read_size(Path(b["path"]).read_text()), "L")

    def test_wrong_sizing_flag_for_type_is_not_written(self) -> None:
        # a story's --size and a cr's --points are the wrong flag for the type: not written.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            artifact.new(root, "epic", "e", {"size": "M"})
            eid = sdlc_md.extract_record_id(
                next((root / "sdlc-studio" / "epics").glob("EP*.md")).stem)
            r = artifact.new(root, "story", "s", {"epic": eid, "size": "M", "points": 3})
            text = Path(r["path"]).read_text()
            self.assertEqual(sdlc_md.read_points(text), 3)   # the right flag won
            self.assertIsNone(sdlc_md.read_size(text))        # the wrong flag was not written


class PlanRefusesRequestTests(unittest.TestCase):
    """G1 (US0121): `sprint plan` refuses an RFC or CR - the Delivery backlog is stories and bugs."""

    def _cr(self, root: Path, num: int, status: str = "Proposed") -> None:
        _write(root / "sdlc-studio" / "change-requests" / f"CR{num:04d}-x.md",
               f"# CR-{num:04d}: c\n\n> **Status:** {status}\n> **Size:** M\n"
               f"> **Affects:** src/cr{num:04d}.py\n")

    def _bug(self, root: Path, num: int, status: str = "Open") -> None:
        _write(root / "sdlc-studio" / "bugs" / f"BG{num:04d}-x.md",
               f"# BG{num:04d}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n"
               f"> **Affects:** src/bg{num:04d}.py\n> **Points:** 2\n")

    def _plan(self, root: Path, *sel: str):
        import io
        import contextlib
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = sprint.main(["plan", *sel, "--root", str(root), "--no-fetch"])
        return rc, err.getvalue()

    def test_plan_refuses_a_cr_batch_and_names_the_decompose_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, 1)
            self._cr(root, 2)
            rc, err = self._plan(root, "--crs", "Proposed")
            self.assertEqual(rc, 2)
            self.assertIn("REQUESTS", err)
            self.assertIn("CR0001", err)
            self.assertIn("decompose", err.lower())      # names the fix
            self.assertIn("Decomposed-into", err)         # names the link to write

    def test_plan_refuses_a_mixed_batch_that_includes_a_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, 1)
            self._cr(root, 2)
            rc, err = self._plan(root, "--bugs", "Open", "--crs", "Proposed")
            self.assertEqual(rc, 2)
            self.assertIn("REQUESTS", err)
            self.assertIn("CR0002", err)

    def test_a_pure_product_batch_is_not_refused_for_being_a_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, 1)
            rc, err = self._plan(root, "--bugs", "Open")
            # it must NOT hit the request gate; a groomed bug plans (rc 0) - and certainly the
            # refusal message never appears for a delivery-only batch
            self.assertNotIn("are REQUESTS", err)


class UndecomposedDriftTests(unittest.TestCase):
    def _cr(self, root: Path, cid: str, status: str) -> None:
        _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
               f"# CR-{cid[2:]}: X\n\n> **Status:** {status}\n> **Size:** M\n")

    def _rfc(self, root: Path, rid: str, status: str) -> None:
        _write(root / "sdlc-studio" / "rfcs" / f"{rid}-x.md",
               f"# {rid}: X\n\n> **Status:** {status}\n")

    def test_accepted_childless_request_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0200", "Approved")     # accepted, no children -> flagged
            self._rfc(root, "RFC0200", "In Review")   # accepted, no children -> flagged
            ids = {(x["kind"], x["id"]) for x in reconcile.undecomposed_drift(root)}
            self.assertIn(("undecomposed", "CR0200"), ids)
            self.assertIn(("undecomposed", "RFC0200"), ids)

    def test_in_progress_cr_flags_and_decorated_status_reduces(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # an In Progress CR (accepted, working) with a decorated status line must still flag
            _write(root / "sdlc-studio" / "change-requests" / "CR0210-x.md",
                   "# CR-0210: X\n\n> **Status:** In Progress (v4) · **Size:** M\n")
            ids = {(x["kind"], x["id"]) for x in reconcile.undecomposed_drift(root)}
            self.assertIn(("undecomposed", "CR0210"), ids)

    def test_intake_request_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0201", "Proposed")   # pre-triage intake
            self._rfc(root, "RFC0201", "Draft")     # pre-triage intake
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_terminal_childless_request_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0202", "Rejected")
            self._cr(root, "CR0203", "Complete")
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_decomposed_request_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0204", "Approved")
            # give CR0204 a child epic
            _write(root / "sdlc-studio" / "epics" / "EP0204-child.md",
                   "# EP0204: Child\n\n> **Status:** Draft\n> **Size:** M\n"
                   "> **Parent:** CR0204\n")
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_parked_request_is_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0205", "Deferred")
            self._cr(root, "CR0206", "Blocked")
            self.assertEqual(reconcile.undecomposed_drift(root), [])


if __name__ == "__main__":
    unittest.main()
