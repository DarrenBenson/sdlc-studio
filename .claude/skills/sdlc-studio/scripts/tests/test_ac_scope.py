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


def _epic(root: Path, disp: str, title: str) -> None:
    d = root / "sdlc-studio" / "epics"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{disp}-x.md").write_text(f"# {disp}: {title}\n\n> **Status:** Draft\n", encoding="utf-8")


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


if __name__ == "__main__":
    unittest.main()
