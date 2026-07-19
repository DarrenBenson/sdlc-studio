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
doc_coverage = command_audit.doc_coverage   # the enumerators both tools share


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

    def test_no_command_is_left_in_one_surface_only(self) -> None:
        # the five help-only commands (lessons, repo, retro, review, upgrade) were the standing
        # finding here; four are now promoted into the Type Reference and `upgrade` is folded
        # behind `migrate`, so the surface must carry no drift in either direction.
        drift = {r["command"]: r["drift"] for r in self.result["commands"] if r["drift"]}
        self.assertEqual(drift, {}, f"catalogue drift: {drift}")
        self.assertEqual(self.result["summary"]["drift"], 0)


class HelpOnlyPromotionTests(unittest.TestCase):
    """The spine-serving help-only commands are promoted into the SKILL Type Reference.

    `lessons` and `retro` are bound into the sprint close gate, `review` is one of the three
    support features, and `repo` map ranks files for a story - all four are working commands
    whose absence from the Type Reference was the drift, so they are promoted rather than cut.
    """

    PROMOTED = ("lessons", "repo", "retro", "review")

    def setUp(self) -> None:
        self.skill_dir = _REPO / ".claude" / "skills" / "sdlc-studio"
        self.result = command_audit.audit(_REPO)
        self.by = {r["command"]: r for r in self.result["commands"]}

    def test_each_promoted_command_is_present_in_both_surfaces(self) -> None:
        for cmd in self.PROMOTED:
            with self.subTest(command=cmd):
                self.assertIn(cmd, self.by, f"`{cmd}` is not in the command surface at all")
                row = self.by[cmd]
                self.assertTrue(row["in_type_ref"], f"`{cmd}` is missing from the Type Reference")
                self.assertTrue(row["in_help"], f"`{cmd}` is missing from the help catalogue")
                self.assertIsNone(row["drift"], f"`{cmd}` still drifts: {row['drift']}")

    def test_each_promoted_command_has_a_one_line_description(self) -> None:
        # a bare row satisfies "present" while telling a reader nothing; the AC asks for a
        # description, so an empty or stub cell fails here.
        import re
        text = (self.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        section = text.split("## Type Reference", 1)[1].split("## Full Reference")[0]
        rows = {m.group(1): m.group(2).strip()
                for m in re.finditer(r"^\| `([^`]+)` \| (.+?) \|\s*$", section, re.M)}
        for cmd in self.PROMOTED:
            with self.subTest(command=cmd):
                self.assertIn(cmd, rows, f"no Type Reference row for `{cmd}`")
                self.assertGreaterEqual(
                    len(rows[cmd]), 20,
                    f"`{cmd}` has no real description in the Type Reference: {rows[cmd]!r}")

    def test_promotion_closes_the_documented_coverage_gate(self) -> None:
        # a Type Reference row with no help catalogue entry fails doc_coverage repo-wide, for
        # every unit - so promotion is only complete when that gate is green.
        r = doc_coverage.check(_REPO)
        uncatalogued = [f["name"] for f in r["findings"] if f["kind"] == "command-uncatalogued"]
        self.assertEqual(uncatalogued, [], f"promoted but uncatalogued: {uncatalogued}")


class RetiredCommandAbsenceTests(unittest.TestCase):
    """A command taken out of the catalogue leaves a redirect, not a dead route.

    `upgrade` is FOLDED behind `migrate`: `reference-upgrade.md` names migrate the front door
    that orchestrates upgrade, so it is a working component of a catalogued command, not a dead
    one. The observable contract the AC asks for holds either way - the command is absent from
    both catalogue surfaces, and one redirect line names what replaces it.
    """

    FOLDED = "upgrade"
    TARGET = "migrate"

    def setUp(self) -> None:
        self.skill_dir = _REPO / ".claude" / "skills" / "sdlc-studio"
        self.result = command_audit.audit(_REPO)

    def test_folded_command_is_absent_from_both_surfaces(self) -> None:
        self.assertNotIn(self.FOLDED, doc_coverage._type_ref_commands(self.skill_dir),
                         f"`{self.FOLDED}` is still in the SKILL Type Reference")
        self.assertNotIn(self.FOLDED, command_audit._help_commands(self.skill_dir),
                         f"`{self.FOLDED}` is still catalogued in help/help.md")
        self.assertNotIn(self.FOLDED, {r["command"] for r in self.result["commands"]},
                         f"`{self.FOLDED}` still holds a command-surface row")

    def test_exactly_one_redirect_names_the_replacement(self) -> None:
        redirects = command_audit._redirects(self.skill_dir)
        self.assertEqual(redirects.get(self.FOLDED), self.TARGET,
                         f"no redirect from `{self.FOLDED}` to `{self.TARGET}`")
        text = (self.skill_dir / "help" / "help.md").read_text(encoding="utf-8")
        n = sum(1 for ln in text.splitlines() if command_audit._REDIRECT_RE.match(ln))
        self.assertEqual(n, 1, f"expected exactly one redirect line, found {n}")

    def test_the_folded_help_page_survives_and_names_the_front_door(self) -> None:
        # folding is not deletion: reference-upgrade.md links this page, and an operator
        # following an old habit must land on a page that redirects rather than a 404.
        p = self.skill_dir / "help" / self.FOLDED
        p = p.with_suffix(".md")
        self.assertTrue(p.is_file(), f"help/{self.FOLDED}.md was deleted")
        self.assertIn(f"/sdlc-studio {self.TARGET}", p.read_text(encoding="utf-8"),
                      f"help/{self.FOLDED}.md does not point at `{self.TARGET}`")

    def test_a_redirect_line_does_not_count_as_a_catalogue_entry(self) -> None:
        # the discriminating half: if the audit read a redirect as a catalogue entry, folding
        # would be indistinguishable from leaving the command in place, and drift would persist.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug"], scripts={})
            hp = root / ".claude" / "skills" / "sdlc-studio" / "help" / "help.md"
            hp.write_text(hp.read_text(encoding="utf-8") +
                          "\n- Folded: `/sdlc-studio upgrade` -> `/sdlc-studio migrate` - "
                          "migrate is the front door\n", encoding="utf-8")
            res = command_audit.audit(root)
            self.assertNotIn("upgrade", {r["command"] for r in res["commands"]})
            self.assertEqual(res["summary"]["drift"], 0)
            self.assertEqual(res["summary"]["redirects"], 1)
            self.assertEqual(res["redirects"], {"upgrade": "migrate"})

    def test_a_plain_catalogue_line_is_still_counted(self) -> None:
        # the guard on the guard: stripping redirects must not swallow ordinary entries.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, type_ref=["bug"], help_cmds=["bug", "upgrade"], scripts={})
            res = command_audit.audit(root)
            by = {r["command"]: r for r in res["commands"]}
            self.assertIn("upgrade", by)
            self.assertEqual(by["upgrade"]["drift"], "in-help-not-in-type-ref")
            self.assertEqual(res["summary"]["redirects"], 0)


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
