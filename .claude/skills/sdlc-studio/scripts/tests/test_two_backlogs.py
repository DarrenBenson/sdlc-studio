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
refine = _load("refine", "refine.py")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _enforce(root: Path) -> None:
    """Opt the temp project into the two-backlog workflow (US0125), so the hard gates - which
    default OFF for upgrade-safety - are ON for a test that exercises the enforced behaviour."""
    _write(root / "sdlc-studio" / ".config.yaml", "two_backlog:\n  enforce: true\n")


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


class EnforcementGateTests(unittest.TestCase):
    """US0125: the two-backlog workflow is enforce-on-request. `two_backlog_enforced` defaults OFF
    (upgrade-safe for an existing project) and turns on with one line of config."""

    def test_default_off_and_opt_in_on(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            self.assertFalse(sdlc_md.two_backlog_enforced(root))   # no config -> off
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "two_backlog:\n  enforce: true\n", encoding="utf-8")
            self.assertTrue(sdlc_md.two_backlog_enforced(root))    # opted in -> on

    def test_explicit_false_stays_off(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "two_backlog:\n  enforce: false\n", encoding="utf-8")
            self.assertFalse(sdlc_md.two_backlog_enforced(root))

    def test_unenforced_cr_creation_keeps_the_legacy_points_flow(self) -> None:
        # US0128: an unenforced project creates a CR with legacy --points (grooms on points);
        # an enforced project holds the strict Size demand and refuses it.
        for enforce, expect_created in ((False, True), (True, False)):
            with self.subTest(enforce=enforce), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio").mkdir(parents=True)
                (root / "src").mkdir()
                (root / "src" / "x.py").write_text("", encoding="utf-8")
                if enforce:
                    _enforce(root)
                fields = {"affects": "src/x.py", "points": 5, "impact": "i"}
                if expect_created:
                    r = artifact.new(root, "cr", "legacy cr", fields)
                    self.assertEqual(sdlc_md.read_points(Path(r["path"]).read_text()), 5)
                else:
                    with self.assertRaises(ValueError):
                        artifact.new(root, "cr", "strict cr", fields)

    def test_batch_create_reads_the_target_enforcement_not_the_cwd(self) -> None:
        # US0128 (review finding): new_batch must thread the TARGET root into the renderer, so a
        # batch create against an unenforced target keeps the legacy points flow regardless of the
        # CWD's enforcement. The bug read enforcement from the CWD and refused a legacy CR.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)   # unenforced target
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text("", encoding="utf-8")
            r = artifact.new_batch(root, "cr", [{"title": "legacy batch cr",
                                                 "affects": "src/x.py", "points": 5, "impact": "i"}])
            text = Path(r["created"][0]["path"]).read_text()
            self.assertEqual(sdlc_md.read_points(text), 5)   # legacy points honoured
            self.assertIsNone(sdlc_md.read_size(text))

    def test_undecomposed_drift_only_surfaces_when_enforced(self) -> None:
        # US0128: an accepted childless CR is undecomposed drift ONLY in an enforced project;
        # an unenforced project is not told its childless CRs are drift.
        import io
        import contextlib
        for enforce, expect_flag in ((False, False), (True, True)):
            with self.subTest(enforce=enforce), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write(root / "sdlc-studio" / "change-requests" / "CR0500-x.md",
                       "# CR-0500: X\n\n> **Status:** Approved\n> **Size:** M\n")
                if enforce:
                    _enforce(root)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    reconcile.main(["detect", "--root", str(root)])
                self.assertEqual("undecomposed" in buf.getvalue(), expect_flag)


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

    def test_parent_ref_agrees_with_parent_refs_past_a_sentinel_first_line(self) -> None:
        # BG0186: a malformed record whose FIRST Parent line is a sentinel (`-`) followed by a
        # real id must not make the singular reader disagree with the plural. parent_ref returns
        # the first NON-sentinel parent, so parent_ref == parent_refs[0] and child_parent agrees.
        rec = ("# EP0200: shared batch\n\n> **Status:** Draft\n"
               "> **Parent:** -\n> **Parent:** CR0200\n")
        self.assertEqual(sdlc_md.parent_refs(rec), ["CR0200"])
        self.assertEqual(sdlc_md.parent_ref(rec), "CR0200")   # was None (stopped at the sentinel)
        self.assertEqual(sdlc_md.child_parent(rec), "CR0200")

    def test_parent_ref_still_none_when_every_parent_line_is_a_sentinel(self) -> None:
        rec = "# EP0201: x\n\n> **Status:** Draft\n> **Parent:** -\n> **Parent:** --\n"
        self.assertIsNone(sdlc_md.parent_ref(rec))
        self.assertEqual(sdlc_md.parent_refs(rec), [])

    def test_child_parent_reads_the_legacy_change_request_link(self) -> None:
        # BG0151: an old-flow epic links its CR the `cr action` way (`Change Request:`), not the
        # two-backlog `Parent:`. child_parent must resolve it, or children_of misses it.
        epic = ("# EP0002: X\n\n> **Status:** Draft\n"
                "> **Change Request:** [CR-0001](../change-requests/CR0001-x.md)\n")
        self.assertIsNone(sdlc_md.parent_ref(epic))            # no new-style link
        self.assertEqual(sdlc_md.change_request_ref(epic), "CR-0001")
        self.assertEqual(sdlc_md.child_parent(epic), "CR-0001")
        # a Parent: link still wins when both are present
        both = epic + "> **Parent:** CR0009\n"
        self.assertEqual(sdlc_md.child_parent(both), "CR0009")

    def test_children_of_and_awaiting_see_a_legacy_decomposed_cr(self) -> None:
        # the false-positive BG0151 fixes end to end: a CR decomposed the OLD way (its epics carry
        # Change Request:, not Parent:) is NOT reported as awaiting refinement.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Size:** M\n")
            _write(root / "sdlc-studio" / "epics" / "EP0002-e.md",
                   "# EP0002: E\n\n> **Status:** Draft\n> **Change Request:** CR-0001\n> **Size:** M\n")
            self.assertEqual(sdlc_md.children_of(root, "CR0001"), [("EP0002", "epic")])
            self.assertEqual(status.discovery_awaiting(root)["ids"], [])   # not awaiting - decomposed

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


class DiscoverySurfacingTests(unittest.TestCase):
    """CR0272 slice 1 (US0151/US0152): the two backlogs are surfaced at `hint` and the main
    `status` dashboard, not only in `status backlog`."""

    def _make(self, root: Path) -> None:
        # two undecomposed discovery items (a childless CR + Issue) and one already-decomposed CR
        _write(root / "sdlc-studio" / "change-requests" / "CR0500-x.md",
               "# CR-0500: X\n\n> **Status:** Proposed\n> **Size:** M\n")
        _write(root / "sdlc-studio" / "issues" / "IS0500-x.md",
               "# IS0500: X\n\n> **Status:** Open\n> **Severity:** Low\n> **Size:** S\n")
        _write(root / "sdlc-studio" / "change-requests" / "CR0501-y.md",
               "# CR-0501: Y\n\n> **Status:** In Progress\n> **Size:** M\n"
               "> **Decomposed-into:** EP0500\n")
        _write(root / "sdlc-studio" / "epics" / "EP0500-e.md",
               "# EP0500: E\n\n> **Status:** In Progress\n> **Parent:** CR0501\n> **Size:** M\n")

    def test_discovery_awaiting_excludes_decomposed_and_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            aw = status.discovery_awaiting(root)
            self.assertEqual(aw["count"], 2)                       # CR0500 + IS0500
            self.assertEqual(aw["ids"], ["CR0500", "IS0500"])      # CR0501 is decomposed, excluded

    def test_discovery_awaiting_excludes_parked_items(self) -> None:
        # a deliberately parked (Deferred/Blocked) childless request must NOT be nudged - it cannot
        # be refined now, so counting it is a false prompt.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0600-x.md",
                   "# CR-0600: X\n\n> **Status:** Deferred\n> **Size:** M\n")
            _write(root / "sdlc-studio" / "change-requests" / "CR0601-y.md",
                   "# CR-0601: Y\n\n> **Status:** Blocked\n> **Size:** M\n")
            _write(root / "sdlc-studio" / "change-requests" / "CR0602-z.md",
                   "# CR-0602: Z\n\n> **Status:** Proposed\n> **Size:** M\n")   # intake - counted
            aw = status.discovery_awaiting(root)
            self.assertEqual(aw["ids"], ["CR0602"])   # only the live intake item awaits refinement

    def test_discovery_awaiting_excludes_an_item_with_a_dropped_child(self) -> None:
        # a request whose only child was dropped (Won't Implement) has been decomposed; it is not
        # re-surfaced as awaiting (documenting the current behaviour - see the retro note).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0700-x.md",
                   "# CR-0700: X\n\n> **Status:** In Progress\n> **Size:** M\n"
                   "> **Decomposed-into:** US0700\n")
            _write(root / "sdlc-studio" / "stories" / "US0700-x.md",
                   "# US0700: X\n\n> **Status:** Won't Implement\n> **Parent:** CR0700\n"
                   "> **Points:** 2\n")
            self.assertEqual(status.discovery_awaiting(root)["ids"], [])

    def test_hint_carries_discovery_and_prints_it(self) -> None:
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            (root / "sdlc-studio" / "prd.md").write_text("# PRD\n", encoding="utf-8")
            hint = status.compute_hint(status.gather(root), root)
            self.assertEqual(hint["discovery"]["count"], 2)        # additive field on the hint
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                status.main(["hint", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("discovery: 2 item(s) await refinement/triage", out)

    def test_dashboard_shows_the_two_backlog_split(self) -> None:
        import io
        import contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._make(root)
            data = status.gather(root)
            self.assertEqual(data["backlogs"]["awaiting"]["count"], 2)
            self.assertIn("issue", data["backlogs"]["discovery"]["types"])
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                status.main(["pillars", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("Backlogs:", out)
            self.assertIn("Discovery=", out)
            self.assertIn("awaiting refine/triage", out)


class DerivedStatusTests(unittest.TestCase):
    """G2 (US0122): a request's SUCCESSFUL terminal is derived from its children. Uses
    dry_run=True, which runs the pre-write gate then returns without writing - so the gate is
    tested without a full index fixture."""

    def _cr(self, root: Path, cid: str, status: str, decomposed: str = "") -> None:
        _enforce(root)   # G2 is enforce-on-request (US0127); these tests exercise the enforced gate
        extra = f"> **Decomposed-into:** {decomposed}\n" if decomposed else ""
        _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
               f"# CR-{cid[2:]}: X\n\n> **Status:** {status}\n> **Size:** M\n{extra}")

    def _epic(self, root: Path, eid: str, status: str, parent: str) -> None:
        _write(root / "sdlc-studio" / "epics" / f"{eid}-x.md",
               f"# {eid}: X\n\n> **Status:** {status}\n> **Size:** M\n> **Parent:** {parent}\n")

    def test_unenforced_project_completes_a_childless_cr_by_assertion(self) -> None:
        # US0127: the G2 derived-status gate is gated - an unenforced project closes a CR the old
        # way, no children required.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0350-x.md",
                   "# CR-0350: X\n\n> **Status:** Approved\n> **Size:** M\n")   # no _enforce
            res = transition.transition(root, "CR0350", "Complete", dry_run=True)
            self.assertEqual(res["to"], "Complete")

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
            _write(root / "src" / "x.py", "")  # BG0144: the Affects path must resolve on disk
            r = artifact.new(root, "cr", "c", {"affects": "src/x.py", "size": "M", "impact": "x"})
            text = Path(r["path"]).read_text()
            self.assertEqual(sdlc_md.read_size(text), "M")
            self.assertIsNone(sdlc_md.read_points(text))

    def test_both_creators_agree_on_a_cr_size_shape(self) -> None:
        # The heart of BG0148: artifact.new and the finding filer produce the SAME Size shape.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            _write(root / "src" / "x.py", "")  # BG0144: the Affects path must resolve on disk
            _write(root / "src" / "y.py", "")
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


class RefineTests(unittest.TestCase):
    """US0129: `refine` decomposes a request into an epic + stories, wiring the bidirectional
    links the two-backlog gates verify."""

    def _cr(self, root: Path, cid: str = "CR0001", status: str = "Approved") -> None:
        _write(root / "sdlc-studio" / "change-requests" / f"{cid}-x.md",
               f"# CR-{cid[2:]}: X\n\n> **Status:** {status}\n> **Priority:** P1\n"
               f"> **Type:** Improvement\n> **Size:** L\n\n## Summary\n\ns\n\n## Impact\n\ni\n")

    def test_refine_creates_epic_and_stories_with_links(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            res = refine.refine(root, "CR0001", "The epic",
                                [("First", 3, None), ("Second", 5, "src/x.py")])
            self.assertEqual(res["points"], 8)
            self.assertEqual(res["epic_size"], "M")           # 8 pts -> M
            # children_of resolves the request -> epic -> stories chain
            self.assertEqual(sdlc_md.children_of(root, "CR0001"), [(res["epic"], "epic")])
            self.assertEqual(len(sdlc_md.children_of(root, res["epic"])), 2)
            # the links resolve BOTH ways - no asymmetry, and the CR is no longer undecomposed
            self.assertEqual(reconcile.link_asymmetry_drift(root), [])
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_refine_rolls_the_epic_point_total(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            res = refine.refine(root, "CR0001", "The epic", [("A", 2, None), ("B", 3, None)])
            epic_text = sdlc_md.find_by_id(root, res["epic"])[0].read_text()
            self.assertEqual(sdlc_md.extract_field(epic_text, "Derived Point Total"), "5")

    def test_refine_refuses_a_non_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "bugs" / "BG0001-x.md",
                   "# BG0001: b\n\n> **Status:** Open\n> **Points:** 2\n")
            with self.assertRaises(ValueError):
                refine.refine(root, "BG0001", "nope", [("x", 2, None)])

    def test_refine_into_adds_stories_to_an_existing_epic(self) -> None:
        # CR0322: --into decomposes a request's stories INTO a shared open epic instead of minting
        # a singleton container. Parent/Decomposed-into wired as usual, the point total rolls up.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            self._cr(root, "CR0002")
            lead = refine.refine(root, "CR0001", "Batch epic", [("A", 2, None)])
            epic = lead["epic"]
            res = refine.refine(root, "CR0002", None, [("B", 3, "src/y.py")], into_epic=epic)
            self.assertEqual(res["epic"], epic)                 # no NEW epic minted
            self.assertEqual(sdlc_md.children_of(root, "CR0002"), [(epic, "epic")])
            self.assertEqual(len(sdlc_md.children_of(root, epic)), 2)   # A (CR0001) + B (CR0002)
            epic_text = sdlc_md.find_by_id(root, epic)[0].read_text()
            self.assertEqual(sdlc_md.extract_field(epic_text, "Derived Point Total"), "5")  # 2+3
            self.assertEqual(reconcile.link_asymmetry_drift(root), [])
            self.assertEqual(reconcile.undecomposed_drift(root), [])

    def test_refine_into_refuses_a_terminal_epic_minting_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            self._cr(root, "CR0002")
            epic = refine.refine(root, "CR0001", "Batch epic", [("A", 2, None)])["epic"]
            ep_path = sdlc_md.find_by_id(root, epic)[0]
            ep_path.write_text(ep_path.read_text().replace("**Status:** Proposed",
                                                           "**Status:** Done")
                               .replace("**Status:** Draft", "**Status:** Done"),
                               encoding="utf-8")
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0002", None, [("B", 3, None)], into_epic=epic)
            # nothing minted for it: CR0002 stays undecomposed
            self.assertTrue(any(x["id"] == "CR0002"
                                for x in reconcile.undecomposed_drift(root)))

    def test_refine_into_refuses_a_non_epic_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            self._cr(root, "CR0002")
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0002", None, [("B", 3, None)], into_epic="CR0001")

    def test_refine_into_refuses_an_unknown_target(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0001", None, [("B", 3, None)], into_epic="EP9999")

    def test_roll_point_total_bumps_an_annotated_total_in_place(self) -> None:
        # CR0322 review finding 1: a non-bare Derived Point Total (annotated, or non-blockquote)
        # must be incremented IN PLACE - not duplicated (the annotated case), not silently no-op'd
        # (the non-blockquote case). And reconcile can fix a wrong blockquote total.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            self._cr(root, "CR0002")
            epic = refine.refine(root, "CR0001", "Batch epic", [("A", 2, None)])["epic"]
            ep_path = sdlc_md.find_by_id(root, epic)[0]
            ep_path.write_text(ep_path.read_text().replace(
                "**Derived Point Total:** 2", "**Derived Point Total:** 2 (derived)"),
                encoding="utf-8")
            refine.refine(root, "CR0002", None, [("B", 3, None)], into_epic=epic)
            text = ep_path.read_text()
            self.assertEqual(text.count("Derived Point Total:"), 1, "not duplicated")
            self.assertTrue(sdlc_md.extract_field(text, "Derived Point Total").startswith("5"),
                            "incremented in place to 2+3, annotation preserved")
            self.assertEqual(reconcile.epic_points_drift(root), [], "no residual points drift")

    def test_each_story_records_its_originating_request(self) -> None:
        # CR0322: in a SHARED batch epic, which story delivers which request must be
        # machine-resolvable, not only in the title. Every refined story carries `Delivers: <req>`.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, "CR0001")
            self._cr(root, "CR0002")
            lead = refine.refine(root, "CR0001", "Batch epic", [("A", 2, None)])
            epic = lead["epic"]
            refine.refine(root, "CR0002", None, [("B", 3, None)], into_epic=epic)
            a = sdlc_md.find_by_id(root, lead["stories"][0])[0].read_text()
            self.assertEqual(sdlc_md.extract_field(a, "Delivers"), "CR0001")
            # the joining request's story records ITS request, not the epic's original owner
            b_id = [s for s, _ in sdlc_md.children_of(root, epic) if s != lead["stories"][0]][0]
            b = sdlc_md.find_by_id(root, b_id)[0].read_text()
            self.assertEqual(sdlc_md.extract_field(b, "Delivers"), "CR0002")

    def test_refine_refuses_an_already_decomposed_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            refine.refine(root, "CR0001", "The epic", [("A", 2, None)])
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0001", "again", [("B", 2, None)])

    def test_refine_refuses_an_off_scale_point_and_mints_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            with self.assertRaises(ValueError):
                refine.parse_story_spec("bad|7")   # 7 is off the Fibonacci scale
            # nothing minted: the CR is still undecomposed
            self.assertEqual(sdlc_md.decomposed_ids(
                sdlc_md.find_by_id(root, "CR0001")[0].read_text()), [])

    def test_refine_refuses_an_empty_breakdown(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0001", "empty", [])

    def test_refine_add_appends_a_second_epic_without_losing_the_first(self) -> None:
        # US0132: refine add appends a further epic to an already-decomposed request; the
        # Decomposed-into is append-only (the first epic is preserved), and both resolve.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            first = refine.refine(root, "CR0001", "First slice", [("A", 3, None)])
            res = refine.refine_add(root, "CR0001", "Second slice", [("B", 5, None)])
            self.assertEqual(res["all_epics"], [first["epic"], res["epic"]])
            # both epics are children; the CR's Decomposed-into lists both; links resolve
            kids = {e for e, _ in sdlc_md.children_of(root, "CR0001")}
            self.assertEqual(kids, {first["epic"], res["epic"]})
            self.assertEqual(reconcile.link_asymmetry_drift(root), [])

    def test_refine_add_refuses_an_undecomposed_request(self) -> None:
        # US0133: add requires the request already be decomposed (apply is for the first epic).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            with self.assertRaises(ValueError):
                refine.refine_add(root, "CR0001", "nope", [("A", 2, None)])

    def test_refine_add_dedupes_and_is_atomic(self) -> None:
        # US0133: the append de-dupes by normalised id (no duplicate child), and a bad title on
        # the add path mints nothing (the first slice's epic/stories survive untouched).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            first = refine.refine(root, "CR0001", "First", [("A", 3, None)])
            before = {p.name for p in (root / "sdlc-studio" / "epics").glob("EP*.md")}
            with self.assertRaises(ValueError):
                refine.refine_add(root, "CR0001", "Second", [("Bad\ntitle", 5, None)])
            after = {p.name for p in (root / "sdlc-studio" / "epics").glob("EP*.md")}
            self.assertEqual(before, after)                       # no new epic minted
            self.assertEqual(sdlc_md.decomposed_ids(
                sdlc_md.find_by_id(root, "CR0001")[0].read_text()), [first["epic"]])
            # de-dupe: _write_decomposed collapses a repeated id
            rpath = sdlc_md.find_by_id(root, "CR0001")[0]
            refine._write_decomposed(rpath, [first["epic"], first["epic"], "EP9999"])
            self.assertEqual(sdlc_md.decomposed_ids(rpath.read_text()), [first["epic"], "EP9999"])

    def test_a_bad_title_mints_nothing_atomicity(self) -> None:
        # review finding: a story title with a newline used to raise INSIDE artifact.new mid-loop,
        # after the epic + first story were already on disk (orphaned). Titles are now validated
        # up front, so a bad breakdown leaves the backlog untouched.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            with self.assertRaises(ValueError):
                refine.refine(root, "CR0001", "E", [("Good", 3, None), ("Bad\ntitle", 5, None)])
            self.assertEqual(list((root / "sdlc-studio" / "epics").glob("EP*.md"))
                             if (root / "sdlc-studio" / "epics").exists() else [], [])
            self.assertEqual(list((root / "sdlc-studio" / "stories").glob("US*.md"))
                             if (root / "sdlc-studio" / "stories").exists() else [], [])
            self.assertEqual(sdlc_md.decomposed_ids(
                sdlc_md.find_by_id(root, "CR0001")[0].read_text()), [])

    def test_refine_moves_the_request_to_its_working_status(self) -> None:
        # US0131: a decomposed CR is now being delivered via its children, so it moves to In
        # Progress (it reaches terminal only by derivation, G2).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root, status="Approved")
            res = refine.refine(root, "CR0001", "E", [("A", 3, None)])
            self.assertEqual(res["status"], "In Progress")
            crtext = sdlc_md.find_by_id(root, "CR0001")[0].read_text()
            self.assertEqual(
                sdlc_md.canonical_status(sdlc_md.extract_field(crtext, "Status"),
                                         sdlc_md.status_vocab("cr", root)),
                "In Progress")

    def test_refine_surfaces_open_questions_for_the_amigos(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            res = refine.refine(root, "CR0001", "E", [("A", 2, None)],
                                questions=["schema or config?", ""])   # blank dropped
            self.assertEqual(res["open_questions"], ["schema or config?"])
            # the consult now names the resolved seats (engineering-led), not bare role strings
            self.assertEqual([p["role"] for p in res["consult"]["panel"]],
                             ["engineering", "product", "qa"])
            self.assertEqual(res["consult"]["panel"][0]["role"], "engineering")

    def test_show_surfaces_the_request_content(self) -> None:
        # US0130: refinable() gathers what the operator needs to propose, and refuses the same
        # cases apply does - so a request show accepts is one apply will.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr(root)
            info = refine.refinable(root, "CR0001")
            self.assertEqual(info["type"], "cr")
            self.assertEqual(info["summary"], "s")   # the Summary section body
            self.assertEqual(info["detail"], "i")    # the Impact section body
            # refuses a non-request and an already-decomposed request, like apply
            _write(root / "sdlc-studio" / "bugs" / "BG0001-x.md",
                   "# BG0001: b\n\n> **Status:** Open\n> **Points:** 2\n")
            with self.assertRaises(ValueError):
                refine.refinable(root, "BG0001")
            refine.refine(root, "CR0001", "e", [("A", 2, None)])
            with self.assertRaises(ValueError):
                refine.refinable(root, "CR0001")   # now decomposed


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
            _enforce(root)
            self._cr(root, 1)
            self._cr(root, 2)
            rc, err = self._plan(root, "--crs", "Proposed")
            self.assertEqual(rc, 2)
            self.assertIn("DISCOVERY items", err)
            self.assertIn("CR0001", err)
            self.assertIn("decompose", err.lower())      # names the fix
            self.assertIn("refine.py", err)               # names the ceremony a request needs

    def test_plan_refuses_a_mixed_batch_that_includes_a_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            self._bug(root, 1)
            self._cr(root, 2)
            rc, err = self._plan(root, "--bugs", "Open", "--crs", "Proposed")
            self.assertEqual(rc, 2)
            self.assertIn("DISCOVERY items", err)
            self.assertIn("CR0002", err)

    def test_an_unenforced_project_plans_a_cr_as_before(self) -> None:
        # US0126: the G1 refusal is gated - a project that has NOT opted in keeps its old flow.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir(parents=True)
            (root / "src" / "cr0001.py").write_text("", encoding="utf-8")   # Affects resolves
            self._cr(root, 1)
            rc, err = self._plan(root, "--crs", "Proposed")
            self.assertNotIn("DISCOVERY items", err)   # not refused for being a discovery item

    def test_a_pure_product_batch_is_not_refused_for_being_a_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, 1)
            rc, err = self._plan(root, "--bugs", "Open")
            # it must NOT hit the discovery gate; a groomed bug plans (rc 0) - and certainly the
            # refusal message never appears for a delivery-only batch
            self.assertNotIn("DISCOVERY items", err)


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


class SeedAcsTests(unittest.TestCase):
    """US0187: refine copies the request's acceptance criteria into the minted story
    as AC scaffolds - the exact checkable criteria the request states stop being
    re-typed by hand."""

    def _cr_with_acs(self, root: Path) -> None:
        _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
               "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
               "> **Type:** Improvement\n> **Size:** M\n\n## Summary\n\ns\n\n## Impact\n\ni\n\n"
               "## Acceptance Criteria\n\n"
               "- [ ] the first checkable criterion\n"
               "- [ ] the second criterion with detail\n")

    def _story_text(self, root: Path, res) -> str:
        sid = sdlc_md.children_of(root, res["epic"])[0][0]
        return sdlc_md.find_by_id(root, sid)[0].read_text(encoding="utf-8")

    def test_seed_acs_copies_request_criteria_into_the_story(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_with_acs(root)
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            text = self._story_text(root, res)
            self.assertIn("### AC1: the first checkable criterion", text)
            self.assertIn("### AC2: the second criterion with detail", text)
            self.assertIn("- **Then** the first checkable criterion", text)
            self.assertIn("{{executable check}}", text)    # Verify stays the author's job
            self.assertNotIn("### AC1: {{define}}", text)  # scaffold replaced

    def test_seed_acs_multi_story_seeds_first_with_note(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_with_acs(root)
            res = refine.refine(root, "CR0001", "The epic",
                                [("First", 2, None), ("Second", 2, None)])
            first = self._story_text(root, res)
            self.assertIn("### AC1: the first checkable criterion", first)
            self.assertIn("redistribute", first.lower())
            second_id = sdlc_md.children_of(root, res["epic"])[1][0]
            second = sdlc_md.find_by_id(root, second_id)[0].read_text(encoding="utf-8")
            self.assertIn("### AC1: {{define}}", second)   # untouched scaffold

    def test_seeded_ac_heading_from_a_long_criterion_has_no_trailing_punctuation(self) -> None:
        # BG0178: a long criterion truncated into the AC heading must not end in '...' (MD026),
        # so a project that markdownlints its workspace is not blocked by the generator's output.
        long_criterion = ("sprint close runs the chain in order and STOPS loudly at the first "
                          "failing gate, naming the remedy for the operator to act on next")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
                   "> **Type:** Improvement\n> **Size:** M\n\n## Summary\n\ns\n\n## Impact\n\ni\n\n"
                   "## Acceptance Criteria\n\n"
                   f"- [ ] {long_criterion}\n")
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            text = self._story_text(root, res)
            heading = next(ln for ln in text.splitlines() if ln.startswith("### AC1:"))
            self.assertFalse(heading.rstrip().endswith("..."))
            self.assertFalse(heading.rstrip()[-1] in ".,;:!?…",
                             f"AC heading ends in punctuation (MD026): {heading!r}")

    def test_seed_not_ready_placeholders_still_flagged(self) -> None:
        # seeding transcribes, it never greens: validate still errors on the
        # unresolved placeholders until the author fills them
        validate = _load("validate", "validate.py")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_with_acs(root)
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            sid = sdlc_md.children_of(root, res["epic"])[0][0]
            spath = sdlc_md.find_by_id(root, sid)[0]
            rules = [v["rule"] for v in validate.validate_file(spath, "story")]
            self.assertIn("placeholder", rules)

    def test_criterion_with_backslashes_lands_verbatim(self) -> None:
        # the critic's blocking catch: criterion text is data, not a regex template -
        # a \\1 must not crash the mint, C:\\temp must not become a TAB
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
                   "> **Type:** Improvement\n> **Size:** M\n\n## Summary\n\ns\n\n## Impact\n\ni\n\n"
                   "## Acceptance Criteria\n\n"
                   "- [ ] the path C:\\temp\\out and the group \\1 survive verbatim\n")
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            text = self._story_text(root, res)
            self.assertIn("C:\\temp\\out and the group \\1 survive verbatim", text)
            self.assertNotIn("\t", text.split("## Acceptance Criteria")[1])

    def test_checked_criteria_are_not_seeded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
                   "> **Type:** Improvement\n> **Size:** M\n\n## Summary\n\ns\n\n## Impact\n\ni\n\n"
                   "## Acceptance Criteria\n\n"
                   "- [x] already delivered elsewhere\n"
                   "- [ ] the live criterion\n")
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            text = self._story_text(root, res)
            self.assertIn("### AC1: the live criterion", text)
            self.assertNotIn("already delivered elsewhere", text)

    def test_single_story_has_no_redistribute_note(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_with_acs(root)
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            self.assertNotIn("redistribute", self._story_text(root, res).lower())

    def test_seed_opt_out_restores_bare_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._cr_with_acs(root)
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)],
                                seed_acs=False)
            text = self._story_text(root, res)
            self.assertIn("### AC1: {{define}}", text)
            self.assertNotIn("the first checkable criterion", text)

    def test_request_without_acs_leaves_scaffold_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "sdlc-studio" / "change-requests" / "CR0001-x.md",
                   "# CR-0001: X\n\n> **Status:** Approved\n> **Priority:** P1\n"
                   "> **Type:** Improvement\n> **Size:** M\n\n## Summary\n\ns\n\n## Impact\n\ni\n")
            res = refine.refine(root, "CR0001", "The epic", [("Only story", 3, None)])
            self.assertIn("### AC1: {{define}}", self._story_text(root, res))


if __name__ == "__main__":
    unittest.main()
