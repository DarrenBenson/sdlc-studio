"""Tests for the command-surface audit (command_audit.py) - CR0272 slice 1, US0149/US0150.

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
_REPO = _SCRIPTS.parents[3]   # the real repo (has SKILL.md)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
command_audit = _load("command_audit")


def _skill(root: Path, *, type_ref: list[str], help_cmds: list[str],
           scripts: dict[str, str]) -> None:
    """Build a minimal skill fixture: a SKILL.md Type Reference, a help catalogue, and scripts."""
    sd = root / ".claude" / "skills" / "sdlc-studio"
    (sd / "scripts").mkdir(parents=True)
    tr = "\n".join(f"| `{c}` | desc |" for c in type_ref)
    (sd / "SKILL.md").write_text(
        f"# SKILL\n\n## Type Reference\n\n| Command | Description |\n| --- | --- |\n{tr}\n\n"
        f"## Full Reference\n\nx\n", encoding="utf-8")
    (sd / "help").mkdir()
    cat = "\n".join(f"| `/sdlc-studio {c}` | desc |" for c in help_cmds)
    (sd / "help" / "help.md").write_text(f"# help\n\n{cat}\n", encoding="utf-8")
    for name, body in scripts.items():
        (sd / "scripts" / f"{name}.py").write_text(body, encoding="utf-8")
    # a reference-scripts page documenting every fixture script (so `undocumented` is 0 unless a
    # test deliberately omits one)
    entries = "\n".join(f"### `{name}.py`\n\ndesc\n" for name in scripts)
    (sd / "reference-scripts.md").write_text(f"# scripts\n\n{entries}\n", encoding="utf-8")


_GOOD = "import argparse\np=argparse.ArgumentParser()\np.parse_args()\n"
_BROKEN = "import sys\nprint('boom', file=sys.stderr)\nsys.exit(1)\n"


class RealRepoAuditTests(unittest.TestCase):
    """The audit on this actual repo - the surface it will be run against."""

    def setUp(self) -> None:
        self.result = command_audit.audit(_REPO)

    def test_applicable_and_every_command_dispositioned(self) -> None:
        self.assertTrue(self.result["applicable"])
        self.assertTrue(self.result["commands"])
        for r in self.result["commands"]:
            self.assertIn(r["spine"], command_audit.SPINE_ORDER)
            self.assertIn(r["disposition"], ("keep", "review"))

    def test_spine_map_is_complete_no_unmapped(self) -> None:
        # every command in the live surface is placed on the spine; a new one would land `unmapped`
        # and this test would fail - the nudge to place it.
        unmapped = [r["command"] for r in self.result["commands"] if r["spine"] == "unmapped"]
        self.assertEqual(unmapped, [], f"unmapped commands: {unmapped}")

    def test_the_five_help_only_commands_are_flagged_as_drift(self) -> None:
        drift = {r["command"] for r in self.result["commands"]
                 if r["drift"] == "in-help-not-in-type-ref"}
        # these live in the help catalogue but not the SKILL Type Reference - the real finding
        self.assertEqual(drift, {"lessons", "repo", "retro", "review", "upgrade"})


class FixtureAuditTests(unittest.TestCase):
    def test_drift_both_directions_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug", "onlytr"], help_cmds=["bug", "onlyhelp"], scripts={})
            res = command_audit.audit(root)
            by = {r["command"]: r for r in res["commands"]}
            self.assertIsNone(by["bug"]["drift"])                       # in both
            self.assertEqual(by["onlytr"]["drift"], "in-type-ref-not-in-help")
            self.assertEqual(by["onlyhelp"]["drift"], "in-help-not-in-type-ref")
            self.assertEqual(by["onlytr"]["disposition"], "review")    # drift -> review

    def test_unmapped_command_is_a_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["zzznovel"], help_cmds=["zzznovel"], scripts={})
            res = command_audit.audit(root)
            r = res["commands"][0]
            self.assertEqual(r["spine"], "unmapped")
            self.assertEqual(r["disposition"], "review")

    def test_broken_tool_detected_and_good_tool_alive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"],
                   scripts={"good": _GOOD, "broken": _BROKEN})
            res = command_audit.audit(root, check_tools=True)
            by = {r["script"]: r for r in res["scripts"]}
            self.assertTrue(by["good"]["alive"])
            self.assertFalse(by["broken"]["alive"])
            self.assertGreaterEqual(res["summary"]["broken_tools"], 1)

    def test_strict_exit_nonzero_on_broken_tool(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"broken": _BROKEN})
            rc = command_audit.main(["--root", str(root), "--check-tools", "--strict"])
            self.assertEqual(rc, 1)

    def test_write_produces_the_audit_document(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug", "cr"], help_cmds=["bug", "cr"], scripts={})
            rc = command_audit.main(["--root", str(root), "--write"])
            self.assertEqual(rc, 0)
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("# Command-surface audit", doc)
            self.assertIn("## raise", doc)
            self.assertIn("`bug`", doc)

    def test_write_without_check_tools_does_not_certify_tooling(self) -> None:
        # the persisted doc must not claim "every tool runs" when --check-tools was not passed -
        # it would be an unverified claim on disk (a broken tool would be silently certified fine).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"broken": _BROKEN})
            command_audit.main(["--root", str(root), "--write"])   # no --check-tools
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("tooling not checked", doc)
            self.assertNotIn("every tool runs", doc)

    def test_write_with_check_tools_certifies_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={"good": _GOOD})
            command_audit.main(["--root", str(root), "--write", "--check-tools"])
            doc = (root / "sdlc-studio" / "reviews" / "command-audit.md").read_text()
            self.assertIn("every tool runs", doc)

    def test_non_skill_repo_is_a_noop(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = command_audit.audit(Path(d))
            self.assertFalse(res["applicable"])
            self.assertEqual(command_audit.main(["--root", d]), 0)


if __name__ == "__main__":
    unittest.main()
