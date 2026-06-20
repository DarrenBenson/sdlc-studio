"""Workspace write-confinement test (CR0015).

The TSD asserts read-only scripts confine writes (contract rule 5), but nothing
exercised it. This snapshots a fixture workspace (paths + content hashes), runs a
read-only script against it, and asserts the tree outside `.local/` is byte
identical afterwards - the script wrote nothing it should not have.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _snapshot(root: Path) -> dict:
    snap = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".local" not in p.parts and "__pycache__" not in p.parts:
            snap[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return snap


def _fixture(root: Path) -> None:
    sd = root / "sdlc-studio"
    for sub in ("stories", "epics", "change-requests", "bugs"):
        (sd / sub).mkdir(parents=True)
    (sd / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (sd / "epics" / "EP0001-x.md").write_text("# EP0001: e\n\n> **Status:** Ready\n", encoding="utf-8")
    (sd / "stories" / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
        "## Acceptance Criteria\n\n### AC1: x\n- **Verify:** file scripts/x\n", encoding="utf-8")
    (sd / "stories" / "_index.md").write_text(
        "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")


class ConfinementTests(unittest.TestCase):
    def _assert_read_only(self, argv: list[str]) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            before = _snapshot(root)
            subprocess.run([sys.executable, str(SCRIPTS / argv[0]), *argv[1:]],
                           capture_output=True, cwd=str(root))  # exit code irrelevant
            self.assertEqual(before, _snapshot(root), f"{argv[0]} mutated the workspace outside .local/")

    def test_status_is_read_only(self) -> None:
        self._assert_read_only(["status.py", "pillars"])

    def test_conformance_is_read_only(self) -> None:
        self._assert_read_only(["conformance.py", "check"])

    def test_integrity_is_read_only(self) -> None:
        self._assert_read_only(["integrity.py", "check"])

    def test_reconcile_detect_is_read_only(self) -> None:
        self._assert_read_only(["reconcile.py", "detect", "--scope", "stories"])

    def test_audit_is_read_only(self) -> None:
        self._assert_read_only(["audit.py", "check", "--stories", "Ready"])


class SideEffectConfinementTests(unittest.TestCase):
    def test_ledger_writes_only_its_named_target(self) -> None:
        # A side-effecting script must touch only its named target (here the
        # tranche decisions file), nothing else in the workspace.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            before = _snapshot(root)
            subprocess.run([sys.executable, str(SCRIPTS / "ledger.py"), "record",
                            "--tranche", "T1", "--decision", "x", "--rationale", "y"],
                           capture_output=True, cwd=str(root))
            after = _snapshot(root)
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertEqual(changed, {"sdlc-studio/decisions/T1.md"})


if __name__ == "__main__":
    unittest.main()
