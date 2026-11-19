"""A project sets how long the agent waits on its push's CI run and how many reruns one red run
of filed flakes may have, under the `ci` keys; the defaults file holds both and the config
reference states the same defaults.

Read through the shipped loader's entry point, `config.py show`, in throwaway projects.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/config-defaults.yaml
# test-census-subject: .claude/skills/sdlc-studio/reference-config.md
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
DEFAULTS = SKILL / "templates" / "config-defaults.yaml"
CONFIG_REF = SKILL / "reference-config.md"
sys.path.insert(0, str(SCRIPTS))

TIMEOUT = "ci.wait_timeout_minutes"
LIMIT = "ci.rerun_limit"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _resolved(root: Path, key: str):
    """`key` as `config.py show` resolves it for the project at `root`."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = _live("config").main(["show", "--key", key, "--root", str(root)])
    if rc != 0:
        raise AssertionError(out.getvalue())
    return json.loads(out.getvalue())


def _project(d: str, config: str | None = None) -> Path:
    root = Path(d)
    if config is not None:
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
    return root


def _stated() -> dict[str, int]:
    """The `ci` block's keys and integer values as the defaults FILE states them, read as text
    rather than through the loader, so the loader and the file are checked against each other."""
    text = DEFAULTS.read_text(encoding="utf-8")
    block = re.search(r"(?m)^ci:\n((?:[ #].*\n)+)", text)
    if block is None:
        raise AssertionError("config-defaults.yaml has no top-level `ci:` block")
    return {f"ci.{k}": int(v) for k, v in
            re.findall(r"(?m)^  ([a-z_]+):\s*(\d+)\b", block.group(1))}


class CiWaitConfigTests(unittest.TestCase):

    def test_the_defaults_and_a_project_override_are_read(self) -> None:
        """AC1. MUTANTS: either key missing from the defaults (the loader gives None); the limit
        defaulting to 2 or 0; the timeout at 0; a project's override ignored (the default
        returned); a partial override that drops the sibling default."""
        stated = _stated()
        self.assertEqual({TIMEOUT, LIMIT}, set(stated), stated)
        self.assertEqual(1, stated[LIMIT])
        self.assertGreater(stated[TIMEOUT], 0)
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            self.assertEqual(stated[TIMEOUT], _resolved(root, TIMEOUT))
            self.assertEqual(1, _resolved(root, LIMIT))
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, "ci:\n  wait_timeout_minutes: 45\n  rerun_limit: 0\n")
            self.assertEqual(45, _resolved(root, TIMEOUT))
            self.assertEqual(0, _resolved(root, LIMIT))
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, "ci:\n  rerun_limit: 3\n")
            self.assertEqual(3, _resolved(root, LIMIT))
            self.assertEqual(stated[TIMEOUT], _resolved(root, TIMEOUT))

    def test_the_reference_states_the_defaults_the_file_holds(self) -> None:
        """AC2. MUTANTS: a reference default that differs from the file; a key spelled other
        than the defaults file spells it (`ci.rerun_max`); a key row cut; the timeout row not
        saying what it bounds, or the limit row not saying what it counts."""
        rows = {}
        for ln in CONFIG_REF.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*`(ci\.[a-z_]+)`\s*\|(.*)\|\s*`([^`]*)`\s*\|\s*$", ln)
            if m:
                rows[m.group(1)] = (m.group(2), m.group(3))
        self.assertEqual({TIMEOUT, LIMIT}, set(rows), rows)
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            for key, (_meaning, default) in rows.items():
                self.assertEqual(str(_resolved(root, key)), default, key)
        self.assertEqual(_stated(), {k: int(v[1]) for k, v in rows.items()})
        timeout, limit = rows[TIMEOUT][0].lower(), rows[LIMIT][0].lower()
        self.assertRegex(timeout, r"\bbounds\b.*\bblocking\b.*\bci run\b")
        self.assertIn("minutes", timeout)
        self.assertRegex(limit, r"\bcounts\b.*\breruns\b.*\bflak")


if __name__ == "__main__":
    unittest.main()
