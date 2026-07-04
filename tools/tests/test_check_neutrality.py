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


if __name__ == "__main__":
    unittest.main()
