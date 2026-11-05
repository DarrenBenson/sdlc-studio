"""BG1224: sdlc-studio integrates continuously to `main` by default.

The shipped default was `release_strategy: pr-required`, so `code implement` taught `gh pr create`,
and nothing an agent loads stated the integration model: a harness that followed the shipped
guidance opened a PR per change. These pins hold the shipped default, the one-line rule in the
router and in the AGENTS.md starter, the lane obligation, and the default's ship guidance.

Driven through the shipped entry points where one exists - `config.py show` for the resolved
default and `sprint.py lane brief` for the obligation - each in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/config-defaults.yaml
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

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

#: The rule's own words, which each always-loaded surface states exactly once.
RULE_COMMIT = "Commit each unit to `main` when its gate passes"
RULE_NO_PR = "open no PR and push no branch"
RULE_OPT_IN = "unless `release_strategy` is `pr-required`"

#: A branch or PR step in a shipped command: what the default's ship guidance must not carry.
BRANCH_OR_PR_STEP = re.compile(
    r"\bgh\s+pr\b|\bgit\s+(checkout|switch|branch|merge|rebase)\b"
    r"|\bgit\s+push\s+(-u|--set-upstream)\b|\bgit\s+push\s+origin\s+(?!main\b)\S")


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _run(module: str, argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = _live(module).main(argv)
    return rc, out.getvalue()


def _resolved_strategy(root: Path) -> str:
    """`release_strategy` as the shipped config loader resolves it for `root`."""
    rc, out = _run("config", ["show", "--key", "release_strategy", "--root", str(root)])
    if rc != 0:
        raise AssertionError(out)
    return json.loads(out)


def _section(text: str, heading: str) -> str:
    """The body under the first heading line starting with `heading`, up to the next heading of
    the same or a higher level; "" when there is no such heading. A `#` comment inside a code
    fence is not a heading."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    for i, ln in enumerate(lines):
        if ln.startswith(heading):
            body, inside = [], False
            for nxt in lines[i + 1:]:
                if nxt.lstrip().startswith("```"):
                    inside = not inside
                m = None if inside else re.match(r"(#+)\s", nxt)
                if m and len(m.group(1)) <= level:
                    break
                body.append(nxt)
            return "\n".join(body)
    return ""


def _fenced(text: str) -> list[str]:
    """The lines inside the text's code fences."""
    rows, inside = [], False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            inside = not inside
            continue
        if inside:
            rows.append(ln)
    return rows


def _table_rows(text: str) -> dict[str, str]:
    """`{value: row}` for each table row whose first cell is a backticked value."""
    rows = {}
    for ln in text.splitlines():
        m = re.match(r"\|\s*`([^`]+)`\s*\|", ln)
        if m:
            rows[m.group(1)] = ln
    return rows


def _obligations(text: str) -> list[str]:
    """The lines of the brief's "Obligations on this lane" list."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Obligations on this lane"))
    rows = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  - "):
            break
        rows.append(ln[4:])
    return rows


class TrunkIntegrationTests(unittest.TestCase):
    def test_the_default_strategy_commits_to_main(self) -> None:
        """AC1. MUTANT: `config-defaults.yaml` back to `release_strategy: pr-required` (the
        loader resolves it for a project that sets nothing); `**Default.**` left on the
        `pr-required` row or missing from the `trunk` row; a `trunk` row that drops "no branch"
        or "no PR"; a `solo-dev` row not read as `trunk`; a `pr-required` row not labelled
        opt-in. Control: a project that sets `pr-required` still resolves to it."""
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual("trunk", _resolved_strategy(Path(d)))
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text(
                "release_strategy: pr-required\n", encoding="utf-8")
            self.assertEqual("pr-required", _resolved_strategy(Path(d)),
                             "the opt-in must still be honoured")
        section = _section((SKILL / "reference-config.md").read_text(encoding="utf-8"),
                           "## Release Strategy")
        self.assertTrue(section, "reference-config.md lost its Release Strategy section")
        self.assertRegex(section, r"(?m)^release_strategy: trunk\b")
        rows = _table_rows(section)
        self.assertEqual(["trunk"], [v for v, r in rows.items() if "**Default.**" in r], rows)
        trunk = rows["trunk"].lower()
        for words in (RULE_COMMIT.lower(), "push `main`", "no branch", "no pr"):
            self.assertIn(words, trunk)
        self.assertIn("read as `trunk`", rows["solo-dev"].lower())
        self.assertIn("opt-in", rows["pr-required"].lower())

    def test_the_router_and_agent_instructions_state_trunk_integration(self) -> None:
        """AC2. MUTANT: the rule line deleted from either file (no line holds it), pasted twice
        (two lines), or stated without its `pr-required` exception or its commit clause."""
        for rel in ("SKILL.md", "templates/agent-instructions.md"):
            text = (SKILL / rel).read_text(encoding="utf-8")
            held = [ln for ln in text.splitlines() if RULE_NO_PR.lower() in ln.lower()]
            self.assertEqual(1, len(held), f"{rel} must state the rule once: {held}")
            self.assertIn(RULE_COMMIT, held[0], rel)
            self.assertIn(RULE_OPT_IN, held[0], rel)
            self.assertIn("push `main`", held[0], rel)

    def test_the_lane_brief_forbids_a_pr_or_pushed_branch(self) -> None:
        """AC3. MUTANT: `LANE_OBLIGATIONS` without the trunk entry (no row forbids a PR), or an
        entry that drops the worktree fast-forward. Control: the obligations already shipped
        still ride the brief, and it exits 0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0101-x.md").write_text(
                "# US0101: x\n\n> **Status:** Ready\n> **Points:** 1\n> **Affects:** src/a.py\n\n"
                "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n",
                encoding="utf-8")
            _live("lib.run_state").open_run(root, batch=["US0101"], goal="g")
            rc, out = _run("sprint", ["lane", "brief", "--units", "US0101", "--root", str(root)])
        self.assertEqual(0, rc, out)
        rows = _obligations(out)
        trunk = [r for r in rows if RULE_NO_PR.lower() in r.lower()]
        self.assertEqual(1, len(trunk), rows)
        for words in ("Land the unit on `main`", "fast-forwarding", "worktree onto `main`",
                      "within the lane"):
            self.assertIn(words, trunk[0])
        self.assertTrue(any(r.startswith("Refuse a unit that carries no authored") for r in rows),
                        rows)
        self.assertTrue(any(r.startswith("A repair answering a REJECT") for r in rows), rows)

    def test_the_default_ship_guidance_has_no_branch_or_pr(self) -> None:
        """AC4. MUTANT: the default's section in reference-code.md carrying `gh pr create`, a
        `git checkout`/`git merge` branch step or the old "branch first" advice; the section
        deleted (empty); or the default flipped back to `pr-required`, whose section holds
        `gh pr create`. Control: the section still ships a `git push`, and the opt-in
        `pr-required` section still documents `gh pr create`."""
        with tempfile.TemporaryDirectory() as d:
            default = _resolved_strategy(Path(d))
        code = (SKILL / "reference-code.md").read_text(encoding="utf-8")
        branch = _section(code, "## Release-Strategy Branch")
        guidance = _section(branch, f"### `{default}`")
        self.assertTrue(guidance.strip(), f"reference-code.md has no ship guidance for {default}")
        self.assertNotIn("gh pr create", guidance)
        self.assertNotIn("branch first", guidance.lower())
        commands = _fenced(guidance)
        self.assertTrue(any("git push" in c for c in commands), commands)
        self.assertEqual([], [c for c in commands if BRANCH_OR_PR_STEP.search(c)])
        self.assertIn("gh pr create", _section(branch, "### `pr-required`"))


if __name__ == "__main__":
    unittest.main()
