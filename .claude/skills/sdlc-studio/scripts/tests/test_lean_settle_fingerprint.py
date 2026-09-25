"""BG0762: the settle fingerprint is not a weak security hash, and still tracks the bytes.

`reconcile._unstaged` hashes each unstaged path's working-tree bytes so `settle` can tell an
edit the author made from one the fix wrote. US0899 spelt it `hashlib.sha1(data)`, which CI's
bandit scan (`-ll`) reports as B324 High, turning the Lint run on main red. The hash only
detects a change, so it is declared `usedforsecurity=False`.

AC1 parses `_unstaged` and applies B324's own rule to every hashlib call in it. AC2 drives
`_unstaged` against a throwaway git repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/reconcile.py
from __future__ import annotations

import ast
import inspect
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import reconcile  # noqa: E402

# The algorithms bandit's B324 flags when `usedforsecurity` is not False.
WEAK = {"md4", "md5", "sha", "sha1"}


def _weak_calls(func) -> list[str]:
    """Every hashlib call in `func` that B324 would flag, as source text."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "hashlib"):
            continue
        name = node.func.attr.lower()
        if name == "new":
            first = node.args[0] if node.args else next(
                (k.value for k in node.keywords if k.arg == "name"), None)
            name = first.value.lower() if isinstance(first, ast.Constant) \
                and isinstance(first.value, str) else "?"
        if name not in WEAK:
            continue
        exempt = any(k.arg == "usedforsecurity" and isinstance(k.value, ast.Constant)
                     and k.value.value is False for k in node.keywords)
        if not exempt:
            found.append(ast.unparse(node))
    return found


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


class SettleFingerprintTests(unittest.TestCase):

    def test_the_unstaged_fingerprint_is_not_a_weak_security_hash(self):
        """MUTANT: HEAD's bare `hashlib.sha1(data)`, or `hashlib.new("sha1", data)`."""
        self.assertIn("hashlib.", inspect.getsource(reconcile._unstaged),
                      "the fingerprint no longer calls hashlib; this test reads nothing")
        self.assertEqual(_weak_calls(reconcile._unstaged), [],
                         "B324 flags these; pass usedforsecurity=False")

    def test_the_rule_flags_both_weak_spellings(self):
        """Positive control: the parser sees the two shapes AC1 names as failures."""
        def bare(data):
            return hashlib.sha1(data)  # noqa: F821

        def via_new(data):
            return hashlib.new("sha1", data)  # noqa: F821

        def declared(data):
            return hashlib.sha1(data, usedforsecurity=False)  # noqa: F821

        self.assertEqual(len(_weak_calls(bare)), 1)
        self.assertEqual(len(_weak_calls(via_new)), 1)
        self.assertEqual(_weak_calls(declared), [])

    def test_the_fingerprint_still_changes_with_the_bytes(self):
        """MUTANT: `hashlib.sha1(usedforsecurity=False)` (hashes nothing), or hashing the path."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git(root, "init", "-q")
            (root / "a.md").write_text("one\n")
            _git(root, "add", "a.md")
            (root / "a.md").write_text("two\n")          # edited after staging
            before = reconcile._unstaged(root)
            self.assertIn("a.md", before)
            self.assertEqual(reconcile._unstaged(root)["a.md"], before["a.md"],
                             "unchanged bytes must give the same fingerprint")
            (root / "a.md").write_text("three\n")
            self.assertNotEqual(reconcile._unstaged(root)["a.md"], before["a.md"],
                                "edited bytes must give a different fingerprint")


if __name__ == "__main__":
    unittest.main()
