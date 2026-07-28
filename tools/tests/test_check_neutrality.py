"""Unit tests for tools/check_neutrality.py (domain-neutrality name guard).

Uses a SENTINEL token (never a real project name) to exercise the mechanism, so the test
itself stays neutral.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "check_neutrality.py"
_spec = importlib.util.spec_from_file_location("check_neutrality", TOOLS)
assert _spec and _spec.loader
cn = importlib.util.module_from_spec(_spec)
sys.modules["check_neutrality"] = cn
_spec.loader.exec_module(cn)

SENTINEL = "zzqsentinelname"          # not a real name; just to drive the matcher
SENTINEL_HASH = hashlib.sha256(SENTINEL.encode()).hexdigest()
BLOCK = {SENTINEL_HASH}


class CheckNeutralityTests(unittest.TestCase):
    def _file(self, body: str) -> Path:
        d = Path(tempfile.mkdtemp())
        p = d / "doc.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_flags_a_blocklisted_token(self):
        p = self._file(f"intro\nthis mentions {SENTINEL} in prose\n")
        found = cn.check(p.parent, blocked=BLOCK, files=[p])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["line"], 2)

    def test_output_redacts_the_term(self):
        # the finding must NOT contain the plaintext token - only a hash prefix
        p = self._file(f"{SENTINEL}\n")
        found = cn.check(p.parent, blocked=BLOCK, files=[p])
        self.assertNotIn(SENTINEL, repr(found))
        self.assertEqual(found[0]["hashes"], [SENTINEL_HASH[:12]])

    def test_sub_token_join_matches_a_variant(self):
        # a base name's hash also catches longer hyphenated variants (base-extra)
        p = self._file(f"see {SENTINEL}-extra here\n")
        self.assertEqual(len(cn.check(p.parent, blocked=BLOCK, files=[p])), 1)

    def test_clean_file_passes(self):
        p = self._file("a perfectly neutral consuming-project reference\n")
        self.assertEqual(cn.check(p.parent, blocked=BLOCK, files=[p]), [])

    def test_unrelated_hyphenated_terms_not_flagged(self):
        p = self._file("agent-instructions review-seat-charter deploy-readiness\n")
        self.assertEqual(cn.check(p.parent, blocked=BLOCK, files=[p]), [])

    def test_real_blocklist_is_populated(self):
        self.assertGreaterEqual(len(cn._BLOCKED), 3)


class ScanCoverageTests(unittest.TestCase):
    """BG0327: the contract is every tracked file, so the selector must be a small binary
    DENYLIST, not a suffix allowlist that silently exempts whatever nobody enumerated."""

    def test_shipped_template_payload_and_extensionless_text_are_selected(self):
        # .template ships into every consuming project (the highest-risk leak site); the
        # evidence log, the hook scripts, CODEOWNERS and .version are all tracked text too.
        rels = [
            ".claude/skills/sdlc-studio/templates/automation/pytest.py.template",
            ".claude/skills/sdlc-studio/templates/docker-compose.test.template",
            "sdlc-studio/retros/evidence/actuals-2026-07-27.jsonl",
            ".githooks/pre-commit",
            ".github/CODEOWNERS",
            "sdlc-studio/.version",
            "LICENSE",
        ]
        self.assertEqual(cn._scannable(rels), rels)

    def test_binary_and_self_and_lockfiles_are_skipped(self):
        rels = ["docs/whitepaper.pdf", "a/logo.png", "package-lock.json",
                "tools/check_neutrality.py", "notes.md"]
        self.assertEqual(cn._scannable(rels), ["notes.md"])

    def test_the_real_tracked_listing_includes_the_previously_exempt_suffixes(self):
        repo = Path(__file__).resolve().parents[2]
        if not (repo / ".git").exists():
            self.skipTest("not a git checkout")
        rels = {p.relative_to(repo).as_posix() for p in cn._tracked_text_files(repo)}
        for want in (".claude/skills/sdlc-studio/templates/automation/pytest.py.template",
                     ".githooks/pre-commit"):
            self.assertIn(want, rels, f"{want} is tracked text but the guard does not scan it")
        self.assertNotIn("docs/whitepaper.pdf", rels)

    def test_a_null_byte_payload_is_skipped_and_the_same_bytes_as_text_are_scanned(self):
        """A discriminating pair, so the sniff is the thing under test rather than the
        emptiness of the fixture: identical bytes, one carrying a NUL, one not."""
        d = Path(tempfile.mkdtemp())
        binary, text = d / "blob.bin", d / "blob.txt"
        binary.write_bytes(b"\x00\x01" + SENTINEL.encode() + b"\x00")
        text.write_bytes(SENTINEL.encode() + b"\n")
        self.assertEqual(cn.check(d, blocked=BLOCK, files=[binary]), [],
                         "binary payload was decoded and scanned as text")
        self.assertEqual(len(cn.check(d, blocked=BLOCK, files=[text])), 1)


class UnreadableFileTests(unittest.TestCase):
    """BG0339: a tracked file the guard could not read is the silent clean-pass LL0008
    forbids - the same failure `_tracked_text_files` already refuses by name."""

    def test_an_unreadable_file_fails_loud_instead_of_scanning_as_empty(self):
        d = Path(tempfile.mkdtemp())
        missing = d / "gone.md"
        with self.assertRaises(SystemExit) as ctx:
            cn.check(d, blocked=BLOCK, files=[missing])
        self.assertIn("gone.md", str(ctx.exception))
        self.assertIn("refusing", str(ctx.exception))

    def test_main_does_not_print_a_clean_scan_when_a_file_was_unreadable(self):
        d = Path(tempfile.mkdtemp())
        (d / "clean.md").write_text("nothing to see\n", encoding="utf-8")
        original = cn._tracked_text_files
        cn._tracked_text_files = lambda root: [d / "clean.md", d / "gone.md"]
        try:
            with self.assertRaises(SystemExit) as ctx:
                cn.main([])
        finally:
            cn._tracked_text_files = original
        self.assertIn("gone.md", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
