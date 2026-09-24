"""US0890: recording a waiver no longer re-reads every script (EP0262).

`waivable_subjects` finds the checkers that declare a waiver rule by parsing every script under
`scripts/`. It did that on every call - 72 parses, 0.34s - so a test module recording waivers
spent most of its time re-parsing an unchanged tree. The scan is now held per process and
re-done only when a script's name, size or modification time moves.
"""
from __future__ import annotations

import ast
import collections
import contextlib
import importlib
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
import decisions  # noqa: E402


@contextlib.contextmanager
def _parse_spy(tree: Path):
    """Count `ast.parse` calls per script of `tree`, keyed by the source text each one holds,
    so the count does not depend on how the scan names the file it parses."""
    names_by_source: dict[str, list[str]] = {}
    for p in tree.glob("*.py"):
        names_by_source.setdefault(p.read_text(encoding="utf-8"), []).append(p.name)
    counts: collections.Counter = collections.Counter()
    real = ast.parse

    def spy(source, *args, **kwargs):
        if source in names_by_source:
            counts[source] += 1
        return real(source, *args, **kwargs)

    with mock.patch.object(ast, "parse", spy):
        yield counts, names_by_source


class _ImportableTree:
    """A throwaway scripts tree on sys.path, its module names unique to this test run so
    `waivable_subjects` imports these declarations and no stale module of the same name."""

    def __init__(self, tree: Path) -> None:
        self.tree = tree
        self.prefix = f"us0890_{uuid.uuid4().hex[:8]}_"

    def __enter__(self) -> "_ImportableTree":
        sys.path.insert(0, str(self.tree))
        return self

    def __exit__(self, *exc) -> None:
        sys.path.remove(str(self.tree))
        for name in [m for m in sys.modules if m.startswith(self.prefix)]:
            del sys.modules[name]

    def path(self, stem: str) -> Path:
        return self.tree / f"{self.prefix}{stem}.py"

    def rule(self, stem: str) -> str:
        return f"rule:{self.prefix}{stem}"

    def declare(self, stem: str, extra: str = "") -> None:
        self.path(stem).write_text(f"WAIVER_RULE = {self.rule(stem)!r}\n{extra}", encoding="utf-8")

    def subjects(self) -> tuple[set[str], list[str]]:
        # The import system caches directory listings; a script added mid-test must be seen by
        # the import `waivable_subjects` makes, which is not the cache under test.
        importlib.invalidate_caches()
        return decisions.waivable_subjects(self.tree)


class DecisionsScanCacheTests(unittest.TestCase):
    def test_each_script_is_parsed_at_most_once_per_process(self) -> None:
        # Mutant: `_modules_declaring_rules` without the memo - every call parses every script,
        # so ten calls count ten parses a script.
        with tempfile.TemporaryDirectory() as d, _ImportableTree(Path(d)) as t:
            t.declare("alpha")
            t.path("beta").write_text("X = 1\n", encoding="utf-8")
            t.path("gamma").write_text("def f():\n    return 2\n", encoding="utf-8")
            with _parse_spy(t.tree) as (counts, names_by_source):
                answers = [t.subjects() for _ in range(10)]
            # Positive control: the spy is wired - a tree this process never scanned is parsed
            # once, every script of it, and then never again.
            self.assertEqual({names_by_source[s][0]: n for s, n in counts.items()},
                             {p.name: 1 for p in t.tree.glob("*.py")})
            self.assertIn(t.rule("alpha"), answers[0][0])
            self.assertTrue(all(a == answers[0] for a in answers), "the memo changed the answer")

        # The shipped tree, through `record_waiver`: ten recordings, each script parsed at most
        # once (not at all when an earlier test in this process already warmed the scan).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with _parse_spy(decisions.SCRIPTS) as (counts, names_by_source):
                for i in range(10):
                    decisions.record_waiver(root, "rule:engagement-floor", f"reason {i}")
            over = {names_by_source[s][0]: n for s, n in counts.items()
                    if n > len(names_by_source[s])}
            self.assertEqual(over, {}, "scripts parsed more than once across ten waivers")
            self.assertEqual(len(decisions.list_decisions(root)), 10)

    def test_a_changed_added_or_deleted_script_is_rescanned(self) -> None:
        # Mutants: a memo keyed on file names alone, on names and mtime without the size, or
        # held for the life of the process regardless of the tree - each misses the change.
        with tempfile.TemporaryDirectory() as d, _ImportableTree(Path(d)) as t:
            t.declare("alpha")
            beta = t.path("beta")
            beta.write_text("X = 1\n", encoding="utf-8")
            first, _ = t.subjects()
            self.assertIn(t.rule("alpha"), first)
            self.assertNotIn(t.rule("beta"), first)

            # Changed: a new WAIVER_RULE, so its size differs. The mtime is put back, so only
            # the size can tell the scan the file moved (a coarse clock can do the same).
            before = beta.stat()
            t.declare("beta")
            os.utime(beta, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertNotEqual(beta.stat().st_size, before.st_size)
            self.assertEqual(beta.stat().st_mtime_ns, before.st_mtime_ns)
            changed, _ = t.subjects()
            self.assertIn(t.rule("beta"), changed, "a changed script was not rescanned")

            # Added.
            t.declare("gamma")
            added, _ = t.subjects()
            self.assertIn(t.rule("gamma"), added, "an added script was not scanned")

            # Deleted: its module stays imported in this process, so only a rescan of the tree
            # drops its rule.
            t.path("alpha").unlink()
            deleted, _ = t.subjects()
            self.assertNotIn(t.rule("alpha"), deleted, "a deleted script's rule survived")
            self.assertIn(t.rule("beta"), deleted)
            self.assertIn(t.rule("gamma"), deleted)

    def test_the_waive_cli_answers_are_unchanged(self) -> None:
        cli = [sys.executable, str(SCR / "decisions.py"), "waive"]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            refused = subprocess.run(
                cli + ["--subject", "rule:no-such-rule", "--rationale", "r", "--root", d],
                capture_output=True, text=True, cwd=d, timeout=120)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertIn("unknown waiver subject 'rule:no-such-rule'", refused.stderr)
            self.assertIn("Known subjects:", refused.stderr)
            self.assertIn("rule:engagement-floor", refused.stderr)
            self.assertEqual(decisions.list_decisions(root), [])

            recorded = subprocess.run(
                cli + ["--subject", "rule:engagement-floor", "--rationale", "declared",
                       "--root", d],
                capture_output=True, text=True, cwd=d, timeout=120)
            self.assertEqual(recorded.returncode, 0, recorded.stderr)
            self.assertIn("waived rule:engagement-floor -> D0001", recorded.stdout)
            self.assertIsNotNone(decisions.waiver_for(root, "rule:engagement-floor"))

        # In process, a warm scan answers exactly as a cold one. Mutant: the memo hands back
        # its stored list, `waivable_subjects` appends an unimportable checker to it, and the
        # second answer names that checker twice.
        with tempfile.TemporaryDirectory() as d, _ImportableTree(Path(d)) as t:
            t.declare("broken", 'raise RuntimeError("unimportable")\n')
            t.declare("sound")
            cold = t.subjects()
            warm = t.subjects()
            self.assertEqual(cold[1], [f"{t.prefix}broken"])
            self.assertEqual(warm, cold)
            self.assertIn(t.rule("sound"), warm[0])


if __name__ == "__main__":
    unittest.main()
