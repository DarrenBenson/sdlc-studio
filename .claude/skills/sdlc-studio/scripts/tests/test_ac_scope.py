"""Unit tests for ac_scope.py - the cross-epic AC scope lint (CR0086)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ac_scope = _load("ac_scope")


def _epic(root: Path, disp: str, title: str, status: str = "Draft") -> None:
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(
        f"# {disp}: {title}\n\n> **Status:** {status}\n", encoding="utf-8")


def _story(root: Path, disp: str, epic: str, ac_body: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(
        f"# {disp}: s\n\n> **Status:** Draft\n> **Epic:** {epic}\n\n"
        f"## Acceptance Criteria\n\n{ac_body}\n", encoding="utf-8")


class AcScopeTests(unittest.TestCase):
    def test_flags_cross_epic_capability(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0001", "Platform & API Foundation")
            _epic(root, "EP0006", "Accounts & Cross-Device Sync")
            # an EP0001 story whose AC reaches into EP0006's "accounts" capability
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            findings = ac_scope.check(root)
            # the AC says "account" (singular); the title keyword is "accounts" - matched via root
            self.assertTrue(any(f["keyword"] == "accounts" and f["owner_epic"] == "EP0006"
                                for f in findings))

    def test_in_scope_story_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0001", "Platform & API Foundation")
            _epic(root, "EP0006", "Accounts & Cross-Device Sync")
            # an EP0006 story legitimately mentioning accounts - its own epic
            _story(root, "US0030", "EP0006",
                   "### AC1\n- **Then** the account is created\n")
            self.assertEqual(ac_scope.check(root), [])

    def test_shared_keyword_not_distinctive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # "sync" appears in two epic titles -> not distinctive -> never flagged
            _epic(root, "EP0006", "Accounts & Sync")
            _epic(root, "EP0007", "Offline Sync Polish")
            _story(root, "US0001", "EP0001",
                   "### AC1\n- **Then** data will sync across devices\n")
            self.assertEqual([f for f in ac_scope.check(root) if f["keyword"] == "sync"], [])

    def test_shared_domain_vocabulary_suppressed(self) -> None:
        # "list" is distinctive to EP0002's title, but it is shared domain vocabulary:
        # stories across many epics legitimately display lists. High document frequency
        # across distinct epics -> suppress, do not cry wolf. CR0113.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0002", "List Management")
            _epic(root, "EP0005", "Web Client")
            # the keyword turns up in stories owned by three distinct other epics
            _story(root, "US0002", "EP0005",
                   "### AC1\n- **Then** the web client renders the list\n")
            _story(root, "US0003", "EP0001",
                   "### AC1\n- **Then** the API returns the list\n")
            _story(root, "US0004", "EP0003",
                   "### AC1\n- **Then** a saved list appears\n")
            self.assertEqual([f for f in ac_scope.check(root) if f["keyword"] == "list"], [])

    def test_concentrated_cross_epic_keyword_still_flags(self) -> None:
        # the same threshold must not blunt a genuine, concentrated reference: "accounts"
        # appears in just one other epic's stories -> still a real cross-epic leak. CR0113.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0002", "List Management")
            _epic(root, "EP0005", "Web Client")
            _epic(root, "EP0006", "Accounts & Cross-Device Sync")
            # "list" is shared across three distinct epics -> suppressed
            _story(root, "US0002", "EP0005",
                   "### AC1\n- **Then** the web client renders the list\n")
            _story(root, "US0003", "EP0001",
                   "### AC1\n- **Then** the API returns the list\n")
            _story(root, "US0004", "EP0003",
                   "### AC1\n- **Then** a saved list appears\n")
            # "accounts" reaches in from exactly one EP0005 story -> still flags
            _story(root, "US0005", "EP0005",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            findings = ac_scope.check(root)
            self.assertEqual([f for f in findings if f["keyword"] == "list"], [])
            self.assertTrue(any(f["keyword"] == "accounts" and f["owner_epic"] == "EP0006"
                                for f in findings))

    def test_terminal_owner_epic_exempted(self) -> None:
        # BG0184: a closed epic owns no live scope. A keyword whose SOLE owning epic is
        # terminal (Done) must not block a new extension story that reuses it - the
        # cross-epic-ac heuristic is about live scope leakage, and a closed epic has none.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0006", "Accounts & Cross-Device Sync", status="Done")
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            self.assertEqual(
                [f for f in ac_scope.check(root) if f["keyword"] == "accounts"], [])

    def test_live_owner_epic_still_flags(self) -> None:
        # The exemption is scoped to TERMINAL owners only: a live (non-terminal) owner
        # still owns scope, so the cross-epic reference is still a real leak and flags.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0006", "Accounts & Cross-Device Sync", status="In Progress")
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            self.assertTrue(any(f["keyword"] == "accounts" and f["owner_epic"] == "EP0006"
                                for f in ac_scope.check(root)))

    def test_two_distinct_epics_below_threshold_still_flags(self) -> None:
        # Boundary, pinned to the canonical AC ("across stories of MANY epics"): a keyword
        # reaching in from exactly TWO distinct non-owner epics is still concentrated leakage,
        # not shared domain vocabulary, so it must still flag. The threshold is 3 by design;
        # this fails if the constant drifts down to 2 or the comparison loosens to <=. CR0113.
        # Intentionally NOT parameterised on ac_scope._SHARED_EPIC_THRESHOLD - that would track
        # the very value under test and never catch its drift (a tautology).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0002", "List Management")
            # "list" (owned by EP0002) named by stories in exactly two distinct other epics
            _story(root, "US0003", "EP0001",
                   "### AC1\n- **Then** the API returns the list\n")
            _story(root, "US0004", "EP0003",
                   "### AC1\n- **Then** a saved list appears\n")
            findings = ac_scope.check(root)
            flagged = [f for f in findings if f["keyword"] == "list"]
            # two distinct epics < threshold (3) -> not suppressed -> both stories flag "list"
            self.assertEqual(len(flagged), 2)
            self.assertTrue(all(f["owner_epic"] == "EP0002" for f in flagged))


class SingleKeywordIsAdvisoryTests(unittest.TestCase):
    """BG0192: one shared English word is a coincidence, not evidence of scope leakage."""

    def test_a_single_keyword_hit_is_advisory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0076", "Rolling multi-sprint policy")
            _epic(root, "EP0072", "Close and gate ergonomics")
            _story(root, "US0219", "EP0072",
                   "### AC1\n- **Then** the gate keeps a rolling local history of run times\n")
            findings = ac_scope.check(root)
            hit = next(f for f in findings if f["keyword"] == "rolling")
            self.assertEqual(hit["strength"], 1)
            self.assertTrue(hit["advisory"])

    def test_two_keywords_from_the_same_epic_are_blocking(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0006", "Accounts Sync")
            _epic(root, "EP0001", "Platform Foundation")
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves and sync completes\n")
            findings = [f for f in ac_scope.check(root) if f["owner_epic"] == "EP0006"]
            self.assertEqual(len(findings), 2)
            for f in findings:
                self.assertEqual(f["strength"], 2)
                self.assertFalse(f["advisory"])

    def test_strength_is_counted_per_owner_epic_not_across_all_hits(self):
        # One keyword from each of two epics is still two coincidences, not one pattern.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0076", "Rolling policy")
            _epic(root, "EP0078", "Weakness hunting")
            _epic(root, "EP0072", "Close ergonomics")
            _story(root, "US0219", "EP0072",
                   "### AC1\n- **Then** a rolling history informs the weakness report\n")
            findings = ac_scope.check(root)
            self.assertTrue(findings)
            for f in findings:
                self.assertEqual(f["strength"], 1)
                self.assertTrue(f["advisory"])

    def test_an_owner_epics_own_stories_never_suppress_its_keywords(self):
        # A story-count suppression was tried and removed: it counted the OWNER's stories,
        # and an epic's backlog is exactly where its own title vocabulary appears, so a few
        # sibling stories deleted a genuine leak before its strength was computed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0006", "Payment Gateway")
            _epic(root, "EP0001", "Reporting Dashboard")
            for n in range(1, 6):   # the owner's OWN stories, using its own vocabulary
                _story(root, f"US001{n}", "EP0006",
                       "### AC1\n- **Then** the payment gateway settles\n")
            _story(root, "US0002", "EP0001",   # the actual cross-epic leak
                   "### AC1\n- **Then** a payment via the gateway is refunded\n")
            hits = [f for f in ac_scope.check(root)
                    if f["story"] == "US0002" and f["owner_epic"] == "EP0006"]
            self.assertEqual(len(hits), 2, "the leak must survive the owner's own usage")
            self.assertTrue(all(not f["advisory"] for f in hits))

    def test_the_owning_epics_own_stories_do_not_count_towards_the_spread(self):
        # One owner story plus one unrelated epic used to reach _SHARED_EPIC_THRESHOLD and
        # erase a real cross-epic leak. The threshold asks how widely a word is used OUTSIDE
        # the epic that owns it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0006", "Payment Gateway")
            _epic(root, "EP0001", "Reporting Dashboard")
            _epic(root, "EP0009", "Other Area")
            _story(root, "US0002", "EP0001",           # the leak
                   "### AC1\n- **Then** a payment via the gateway is refunded\n")
            _story(root, "US0050", "EP0009",
                   "### AC1\n- **Then** the payment gateway is mentioned here too\n")
            _story(root, "US0010", "EP0006",           # the OWNER's own usage
                   "### AC1\n- **Then** the payment gateway settles\n")
            hits = [f for f in ac_scope.check(root) if f["story"] == "US0002"]
            self.assertEqual(len(hits), 2, "the owner's own usage erased the leak")
            self.assertTrue(all(not f["advisory"] for f in hits))

    def test_a_keyword_spread_across_many_distinct_epics_is_still_suppressed(self):
        # Genuinely shared vocabulary - three NON-owning epics use it - is still dropped.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0082", "Residual audit fixes")
            for n in range(1, 5):
                _epic(root, f"EP001{n}", f"Unrelated area {n}")
                _story(root, f"US001{n}", f"EP001{n}",
                       "### AC1\n- **Then** the residual case is handled\n")
            findings = ac_scope.check(root)
            self.assertFalse([f for f in findings if f["keyword"] == "residual"],
                             "shared across many epics is vocabulary, not leakage")

    def test_the_motivating_cross_epic_case_still_reports(self):
        # It becomes advisory rather than silent - the signal is kept, the block is not.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _epic(root, "EP0001", "Platform Foundation")
            _epic(root, "EP0006", "Accounts")
            _story(root, "US0002", "EP0001",
                   "### AC1\n- **Then** a valid account token resolves a userId\n")
            findings = ac_scope.check(root)
            self.assertTrue(any(f["keyword"] == "accounts" and f["owner_epic"] == "EP0006"
                                for f in findings))


if __name__ == "__main__":
    unittest.main()
