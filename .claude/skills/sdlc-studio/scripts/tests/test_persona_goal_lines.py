"""A persona End goal can carry its own Verify and Applies-to lines, nested under its number.

`validate.py personas` lints each End goal's own lines by card and number (and no other Verify
line on the card), warns on a scope nothing checks or one written in a dialect the matcher does
not read, the template's commented End goal example is a shape the reader parses and never one of
a card's End goals, and every `persona-goal-*` rule the lint prints has a row in
reference-persona.md's rule table.

Driven through `validate.main` and `sprint.main`, the shipped entry points, in throwaway trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project the brief needs

validate = loader.load_script("validate")
sprint = loader.load_script("sprint")
from lib import persona_goals, sdlc_md  # noqa: E402

SKILL = loader.SCRIPTS_DIR.parent
TEMPLATE = SKILL / "templates" / "personas" / "persona-template.md"
REFERENCE = SKILL / "reference-persona.md"

_CARD = """# {name}

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | {role} |

## Who They Are

Somebody particular.

## End Goals

*Most important first.*

{goals}

## Experience Goals

- calm

## Behaviours & Context

- **Environment:** a laptop

## Frustrations

- lost work

## Scenario

{scenario}
"""

_VERIFY_GOALS = """1. Ship features through the lifecycle
   - **Verify:** {{the check that proves it}}
2. Never lose the thread after a reset
   - **Verify:** npm test
3. Drive a batch to done
   - **Verify:** pytest tests/test_batch.py::BatchTests::test_done"""

_SCOPE_GOALS = """1. Every room stays warm
   - **Applies-to:** `ha/rooms/`
2. A room's schedule survives a restart
   - **Verify:** pytest tests/test_rooms.py::RoomTests::test_schedule_survives
   - **Applies-to:** `ha/rooms/**`
3. The lights follow whoever is in the room
   - **Verify:** pytest tests/test_rooms.py::RoomTests::test_lights_follow
   - **Applies-to:** `ha/rooms/`"""


def _card(root: Path, slug: str, name: str, goals: str, *, role: str = "Primary",
          scenario: str = "They ship a feature and it stays shipped.") -> Path:
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    path = pdir / f"{slug}.md"
    path.write_text(_CARD.format(name=name, role=role, goals=goals, scenario=scenario),
                    encoding="utf-8")
    return path


def _personas(root: Path) -> list[dict]:
    """`validate.py personas --format json`'s findings for the tree."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        validate.main(["personas", "--root", str(root), "--format", "json"])
    return json.loads(out.getvalue())["violations"]


def _goal_findings(root: Path, rule: str) -> list[dict]:
    return [v for v in _personas(root) if v["rule"] == rule]


def _brief(root: Path, goal: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main(["goal-review", "brief", "--goal", goal, "--brief-worklist",
                          str(root / "worklist.txt"), "--root", str(root)])
    assert rc == 0, err.getvalue()
    return out.getvalue()


def _template_example() -> tuple[str, str]:
    """The `<!-- end-goal-example ... -->` comment under the template's End Goals, whole, and
    the End goal lines it carries (from its first numbered line on)."""
    text = TEMPLATE.read_text(encoding="utf-8")
    section = re.search(r"^## End Goals\s*$(.*?)^## ", text, re.M | re.S)
    assert section, "the template has no `## End Goals` section"
    m = re.search(r"<!-- end-goal-example\b.*?-->", section.group(1), re.S)
    assert m, "no `<!-- end-goal-example ... -->` comment under the template's End Goals"
    body = m.group(0)[len("<!--"):-len("-->")]
    lines = body.splitlines()
    first = next(i for i, ln in enumerate(lines) if re.match(r"^\d+[.)]\s", ln))
    return m.group(0), "\n".join(lines[first:]).rstrip()


def _brief_goals(brief: str, name: str) -> list[str]:
    """The End goal lines the brief lists under one persona's heading."""
    lines = brief.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"  {name} ("))
    out = []
    for ln in lines[start + 1:]:
        if not ln.startswith("    "):
            break
        out.append(ln.strip())
    return out


class GoalVerifyLintTests(unittest.TestCase):

    def test_validate_personas_lints_each_end_goal_verify(self) -> None:
        """Mutants: never run the lint; lint every Verify line in the file (the Scenario's too);
        attach a Verify to the wrong goal number, or one not nested under it; skip the
        placeholder check."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            card = _card(root, "maya-okafor", "Maya Okafor", _VERIFY_GOALS,
                         scenario="Maya ships a feature.\n\n- She checks it shipped:\n"
                                  "  - **Verify:** npx jest rooms")
            found = _goal_findings(root, "persona-goal-verify")
            self.assertEqual(sorted((Path(f["file"]).name, f["goal"]) for f in found),
                             [(card.name, "1"), (card.name, "2")], found)
            by_goal = {f["goal"]: f["message"] for f in found}
            self.assertTrue(by_goal["1"].startswith("End goal 1"), by_goal)
            self.assertIn("{{", by_goal["1"])
            self.assertTrue(by_goal["2"].startswith("End goal 2"), by_goal)
            self.assertIn("npm test", by_goal["2"])
            self.assertTrue(all(f["severity"] == "warning" for f in found), found)
            self.assertFalse([f for f in _personas(root) if "npx jest" in f["message"]],
                             "the Scenario's Verify line was linted as an End goal's")
            # A Verify line that is not nested under a goal's number is not that goal's.
            card.write_text(card.read_text(encoding="utf-8").replace(
                "test_done\n", "test_done\n\n- **Verify:** npm run flat\n"), encoding="utf-8")
            self.assertEqual(sorted(f["goal"] for f in _goal_findings(root, "persona-goal-verify")),
                             ["1", "2"])


class GoalScopeLintTests(unittest.TestCase):

    def test_validate_personas_warns_on_an_unchecked_or_misdialected_scope(self) -> None:
        """Mutants: pass a scoped goal that carries no Verify; pass `**` silently; name `**`
        without the trailing-`/` form that replaces it; warn on the well-formed third goal."""
        # The dialect is the TRD component matcher's, which reads `**` as one literal segment:
        # the lint exists because this probe misses, so it is pinned beside the lint.
        self.assertFalse(sprint._component_names("ha/rooms/**", "ha/rooms/up/bed.yaml"))
        self.assertTrue(sprint._component_names("ha/rooms/", "ha/rooms/up/bed.yaml"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            card = _card(root, "maya-okafor", "Maya Okafor", _SCOPE_GOALS)
            found = _goal_findings(root, "persona-goal-scope")
            self.assertEqual(sorted((Path(f["file"]).name, f["goal"]) for f in found),
                             [(card.name, "1"), (card.name, "2")], found)
            by_goal = {f["goal"]: f["message"] for f in found}
            self.assertIn("no Verify", by_goal["1"])
            self.assertIn("`**`", by_goal["2"])
            self.assertIn("`ha/rooms/`", by_goal["2"])
            self.assertNotIn("no Verify", by_goal["2"])
            self.assertEqual(_goal_findings(root, "persona-goal-verify"), [])


class TemplateExampleTests(unittest.TestCase):

    def test_template_example_is_read_and_its_comment_is_not(self) -> None:
        """Mutants: a template example whose Verify is not nested under its number; a reader
        that takes the commented example as one of the card's End goals."""
        comment, example = _template_example()
        self.assertRegex(example, r"\n\s+- \*\*Verify:\*\* \S")
        self.assertRegex(example, r"\n\s+- \*\*Applies-to:\*\* \S")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root, personas=())
            filled = _card(root, "maya-okafor", "Maya Okafor", example)
            _card(root, "jonah-reyes", "Jonah Reyes",
                  f"{comment}\n\n1. Adopt the lifecycle incrementally", role="Secondary")
            self.assertEqual([f for f in _personas(root)
                              if f["rule"].startswith("persona-goal-")], [])
            brief = _brief(root, "Ship the rooms feature")
            goal_text = re.match(r"^\d+[.)]\s+(.+)$", example.splitlines()[0]).group(1)
            self.assertIn(f"1. {goal_text}", _brief_goals(brief, "Maya Okafor"))
            self.assertEqual(_brief_goals(brief, "Jonah Reyes"),
                             ["1. Adopt the lifecycle incrementally"])
            # Positive control: the example's shape IS read - its Verify swapped for one the
            # verify_ac lint flags draws the warning on the filled card.
            filled.write_text(re.sub(r"(\*\*Verify:\*\*) .+", r"\1 npm test",
                                     filled.read_text(encoding="utf-8")), encoding="utf-8")
            self.assertEqual([(Path(f["file"]).name, f["goal"])
                              for f in _goal_findings(root, "persona-goal-verify")],
                             [(filled.name, "1")])


class RuleTableTests(unittest.TestCase):

    def test_every_printed_persona_goal_rule_has_a_row(self) -> None:
        """Mutants: a rule renamed or added in code with no row; the scope row dropping the
        dialect."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _card(root, "maya-okafor", "Maya Okafor", _VERIFY_GOALS)
            _card(root, "jonah-reyes", "Jonah Reyes", _SCOPE_GOALS, role="Secondary")
            printed = {f["rule"] for f in _personas(root) if f["rule"].startswith("persona-goal-")}
        self.assertEqual(printed, {"persona-goal-verify", "persona-goal-scope"})
        rows: dict[str, str] = {}
        for table in sdlc_md.iter_tables(REFERENCE.read_text(encoding="utf-8")):
            if (table["header"] or [""])[0].strip().lower() == "rule":
                for _n, cells in table["rows"]:
                    for rule in re.findall(r"`([a-z]+(?:-[a-z]+)+)`", cells[0]):
                        rows[rule] = " ".join(cells[1:])
        for rule in sorted(printed):
            self.assertIn(rule, rows, f"reference-persona.md's rule table has no row for {rule}")
        scope = rows["persona-goal-scope"]
        for stated in ("ending `/`", "`**`", "segment"):
            self.assertIn(stated, scope, "the Applies-to dialect is not stated beside its rule")


class CommentInsideCodeTests(unittest.TestCase):

    def _goals(self, above: str) -> list:
        return persona_goals.end_goals(
            f"# Card\n\n{above}\n\n## End Goals\n\n1. first\n2. second\n")

    def test_an_unclosed_comment_opener_in_code_hides_no_goal(self) -> None:
        """Mutants: scan comments before fences; ignore inline code spans; a fence that does not
        end at its closer."""
        for above in ("```html\n<!-- an example\n```", "~~~\n<!--\n~~~", "Use `<!--` to open one.",
                      "Use ``<!-- a ` b`` to open one."):
            with self.subTest(above=above):
                self.assertEqual([g.number for g in self._goals(above)], ["1", "2"])

    def test_a_real_comment_and_a_fence_inside_a_comment_still_hide(self) -> None:
        text = ("## End Goals\n\n1. kept\n<!--\n```\n2. hidden\n-->\n3. after\n"
                "<!-- 4. one line --> 5. same line\n6. `<!--` span then text\n")
        self.assertEqual([g.number for g in persona_goals.end_goals(text)], ["1", "3", "5", "6"])
        # an opener after a closed span on the same line is a comment
        text = "## End Goals\n\n1. kept `x` <!-- 2. hidden\n-->\n3. after\n"
        self.assertEqual([g.number for g in persona_goals.end_goals(text)], ["1", "3"])
        # a fenced block between a goal and its nested line is invisible to the reader
        text = "## End Goals\n\n1. one\n\n```\ncode\n```\n   - **Verify:** pytest a.py\n"
        self.assertEqual([(g.number, g.verify) for g in persona_goals.end_goals(text)],
                         [("1", "pytest a.py")])
        # a fence opened above an End Goals heading and left open drops what follows, as before
        text = "## End Goals\n\n1. a\n```\n2. in code\n```\n3. b\n"
        self.assertEqual([g.number for g in persona_goals.end_goals(text)], ["1", "3"])


class NestedLineAttachmentTests(unittest.TestCase):

    def test_a_nested_line_under_a_note_attaches_to_no_goal(self) -> None:
        """Mutants: no reset on a paragraph; reset on a blank line alone; reset on an indented
        line; reset on a line with no blank line above it."""
        text = ("## End Goals\n\n1. one\n   - **Verify:** pytest a.py\n\n2. two\n\n"
                "Notes:\n  - **Verify:** npm test\n  - **Applies-to:** `x/`\n")
        goals = persona_goals.end_goals(text)
        self.assertEqual([(g.number, g.verify, g.applies_to) for g in goals],
                         [("1", "pytest a.py", ()), ("2", None, ())])
        # controls: a nested line after a blank line, a wrapped continuation (no blank line,
        # unindented) and an indented second paragraph all stay with their goal
        text = ("## End Goals\n\n1. one\n\n   - **Verify:** pytest a.py\n"
                "2. two wraps\ncontinued here\n   - **Verify:** pytest b.py\n"
                "3. three\n\n   more words\n   - **Verify:** pytest c.py\n")
        self.assertEqual([(g.number, g.verify) for g in persona_goals.end_goals(text)],
                         [("1", "pytest a.py"), ("2", "pytest b.py"), ("3", "pytest c.py")])

    def test_a_second_verify_on_one_goal_is_a_finding(self) -> None:
        """Mutants: the second replaces the first; the first is dropped; no finding; a finding
        naming the wrong goal or no check."""
        text = ("## End Goals\n\n1. one\n   - **Verify:** pytest a.py\n"
                "2. two\n   - **Verify:** pytest b.py\n   - **Verify:** pytest c.py\n"
                "   - **Verify:** pytest d.py\n")
        goals = persona_goals.end_goals(text)
        self.assertEqual([(g.verify, g.extra_verifies) for g in goals],
                         [("pytest a.py", ()), ("pytest b.py", ("pytest c.py", "pytest d.py"))])
        found = persona_goals.findings(goals, lambda expr: None)
        self.assertEqual([(rule, n) for rule, n, _m in found],
                         [("persona-goal-verify", "2")] * 2)
        self.assertIn("pytest c.py", found[0][2])
        self.assertIn("pytest b.py", found[0][2])
        self.assertIn("pytest d.py", found[1][2])
        row = next(line for line in REFERENCE.read_text(encoding="utf-8").splitlines()
                   if line.startswith("| `persona-goal-verify`"))
        self.assertIn("second nested Verify on one goal is also warned of", row)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            card = _card(root, "maya-okafor", "Maya Okafor",
                         "1. one\n   - **Verify:** pytest a.py\n   - **Verify:** pytest b.py")
            self.assertEqual([(Path(f["file"]).name, f["goal"], f["severity"])
                              for f in _goal_findings(root, "persona-goal-verify")],
                             [(card.name, "1", "warning")])


if __name__ == "__main__":
    unittest.main()
