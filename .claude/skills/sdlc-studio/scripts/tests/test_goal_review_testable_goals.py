"""The goal review lists each traced persona's End goals with what checks each, and the brief and
the plan name a Sprint Goal that traces to personas none of whose End goals carries an executable
Verify - advice, never a refusal.

Driven through `sprint.main`, the shipped entry point, in throwaway trees built on the goal-trace
fixture (BG0001; Maya Okafor Primary, Trevor Hale Negative; outcomes O1 and O2).
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
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")

_PYTEST = "pytest tests/test_fixed.py::FixedTests::test_closed"
_HANA_VERIFY = "pytest tests/test_notice.py::NoticeTests::test_heard"
_MANUAL = "manual walk each room"


def _card(name: str, role: str, goals: list[tuple[str, str | None]],
          numbers: list[str] | None = None) -> str:
    """A persona card whose `## End Goals` are `goals`, each `(text, verify or None)`, numbered
    `1.` `2.` ... unless `numbers` gives the number each goal is written under."""
    numbers = numbers or [str(n) for n in range(1, len(goals) + 1)]
    body = "".join(f"{n}. {text}\n" + (f"   - **Verify:** {verify}\n" if verify else "")
                   for n, (text, verify) in zip(numbers, goals, strict=True))
    return (f"# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
            f"| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n\n"
            f"## End Goals\n\n{body}")


def _write_card(root: Path, name: str, role: str, goals: list[tuple[str, str | None]],
                numbers: list[str] | None = None) -> None:
    slug = name.lower().replace(" ", "-")
    (root / "sdlc-studio" / "personas" / f"{slug}.md").write_text(
        _card(name, role, goals, numbers), encoding="utf-8")


def _run(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        rc = sprint.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _brief(root: Path, goal: str) -> list[str]:
    rc, out, err = _run(root, "goal-review", "brief", "--goal", goal, "--brief-worklist",
                        str(root / "worklist.txt"))
    assert rc == 0, err
    return out.splitlines()


def _plan(root: Path, goal: str, *extra: str) -> tuple[int, str]:
    rc, out, _err = _run(root, "plan", "--worklist", str(root / "worklist.txt"), "--sprint-goal",
                         goal, "--no-fetch", *extra)
    return rc, out


def _plan_json(root: Path, goal: str) -> tuple[int, dict]:
    rc, out = _plan(root, goal, "--format", "json")
    return rc, json.loads(out)


def _starting(lines: list[str], prefix: str) -> list[str]:
    return [ln.strip() for ln in lines if ln.strip().lower().startswith(prefix.lower())]


def _trace_lines(lines: list[str]) -> list[str]:
    """The goal-trace lines a surface prints: `goal serves` and `goal check`, either case."""
    return _starting(lines, "goal serves") + _starting(lines, "goal check")


def _traced_block(lines: list[str]) -> list[str]:
    """The lines under the brief's `Traced End goals` heading, up to the next unindented line."""
    start = next((i for i, ln in enumerate(lines) if ln.startswith("Traced End goals")), None)
    if start is None:
        return []
    block = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  "):
            break
        block.append(ln)
    return block


class TestableListingTests(unittest.TestCase):

    def test_brief_lists_each_end_goal_with_its_check(self) -> None:
        """Mutants: keep today's text-only listing; attach a Verify to the following goal; count
        a manual Verify as testable."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", None),
                         ("Every open bug is fixed", _PYTEST),
                         ("Every room is lit", _MANUAL)])
            lines = _brief(root, "Maya Okafor sees every open bug fixed")
            self.assertEqual(
                ["  Maya Okafor (Primary):",
                 "    1. Walk in to a warm house - not testable: no Verify line",
                 f"    2. Every open bug is fixed - Verify: {_PYTEST}",
                 f"    3. Every room is lit - checked by hand: {_MANUAL}"],
                _traced_block(lines))
            # goal 2 is executable, so the goal can be checked and no goal-check line prints
            self.assertEqual([], _starting(lines, "Goal check"))

    def test_a_verify_naming_no_check_is_not_testable(self) -> None:
        """Mutant: count an empty Verify, or an unfilled placeholder, as executable."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            card = _card("Maya Okafor", "Primary", [("Walk in to a warm house", None),
                                                     ("Every room is lit", None)])
            card = card.replace("house\n", "house\n   - **Verify:**\n").replace(
                "lit\n", "lit\n   - **Verify:** `{{verify command}}`\n")
            (root / "sdlc-studio" / "personas" / "maya-okafor.md").write_text(
                card, encoding="utf-8")
            lines = _brief(root, "Maya Okafor sees every open bug fixed")
            self.assertEqual(
                ["  Maya Okafor (Primary):",
                 "    1. Walk in to a warm house - not testable: its Verify names no check",
                 "    2. Every room is lit - not testable: its Verify names no check"],
                _traced_block(lines))
            self.assertEqual(1, len(_starting(lines, "Goal check")))


class GoalCheckTests(unittest.TestCase):

    def test_goal_with_no_executable_end_goal_is_named_on_brief_and_plan(self) -> None:
        """Mutants: drop the line from the brief or the plan; return non-zero on it; name only
        the first traced persona."""
        goal = "Maya Okafor and Hana Ito see every open bug fixed"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", None), ("Every room is lit", _MANUAL)])
            _write_card(root, "Hana Ito", "Secondary", [("Hear about a change", None)])
            rc_flagged_text, flagged_text = _plan(root, goal)
            for surface, lines in (("brief", _brief(root, goal)),
                                   ("plan", flagged_text.splitlines())):
                checks = _starting(lines, "goal check")
                self.assertEqual(1, len(checks), (surface, checks))
                for name in ("Maya Okafor", "Hana Ito"):
                    self.assertIn(name, checks[0], surface)
                self.assertIn("nothing can check", checks[0], surface)
            rc_flagged, flagged = _plan_json(root, goal)
            self.assertFalse(flagged["goal_trace"]["checkable"])
            # the same plan with one executable End goal: no line, same exit code, same batch
            _write_card(root, "Hana Ito", "Secondary", [("Hear about a change", _HANA_VERIFY)])
            self.assertEqual([], _starting(_brief(root, goal), "goal check"))
            rc_text, text = _plan(root, goal)
            self.assertEqual([], _starting(text.splitlines(), "goal check"))
            rc_clear, clear = _plan_json(root, goal)
            self.assertTrue(clear["goal_trace"]["checkable"])
            self.assertEqual((0, 0), (rc_flagged_text, rc_flagged))
            self.assertEqual((rc_text, rc_clear), (rc_flagged_text, rc_flagged))
            self.assertEqual(clear["batch"], flagged["batch"])
            self.assertEqual(["BG0001"], [u["id"] for u in flagged["batch"]])

    def test_checkable_reads_only_the_traced_personas(self) -> None:
        """Mutant: compute checkability over every persona card, so Hana's testable End goal
        makes Maya's uncheckable goal read checkable."""
        goal = "Maya Okafor sees every open bug fixed"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", None), ("Every room is lit", None)])
            _write_card(root, "Hana Ito", "Secondary", [("Hear about a change", _HANA_VERIFY)])
            rc, data = _plan_json(root, goal)
            self.assertEqual(0, rc)
            trace = data["goal_trace"]
            self.assertFalse(trace["checkable"])
            self.assertEqual([], trace["checked_by"])
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", _PYTEST), ("Every room is lit", None)])
            rc, data = _plan_json(root, goal)
            self.assertEqual(0, rc)
            trace = data["goal_trace"]
            self.assertTrue(trace["checkable"])
            self.assertEqual([{"persona": "Maya Okafor", "number": "1",
                               "text": "Walk in to a warm house", "verify": _PYTEST}],
                             trace["checked_by"])


class GoalCheckBoundaryTests(unittest.TestCase):

    def test_outcome_only_and_untraced_goals_print_no_goal_check(self) -> None:
        """Mutant: fire the goal-check line on a goal that traces to no persona, so a project
        with no End goal Verify lines yet sees it every sprint."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", None), ("Every room is lit", None)])
            outcome_goal = "every open bug is fixed, advancing O1"
            rc, data = _plan_json(root, outcome_goal)
            self.assertEqual(0, rc)
            self.assertNotIn("checkable", data["goal_trace"])
            brief = _brief(root, outcome_goal)
            self.assertEqual([], _starting(brief, "goal check"))
            self.assertEqual([], _traced_block(brief))
            rc, text = _plan(root, outcome_goal)
            self.assertEqual(0, rc)
            self.assertEqual([], _starting(text.splitlines(), "goal check"))

            untraced = "every open bug is fixed"
            brief = _brief(root, untraced)
            goal_lines = _trace_lines(brief)
            self.assertEqual(1, len(goal_lines), goal_lines)
            self.assertTrue(goal_lines[0].startswith("Goal serves: NONE"), goal_lines)
            self.assertEqual([], _traced_block(brief))
            rc, text = _plan(root, untraced)
            self.assertEqual(0, rc)
            goal_lines = _trace_lines(text.splitlines())
            self.assertEqual(1, len(goal_lines), goal_lines)
            self.assertTrue(goal_lines[0].startswith("goal serves: NONE"), goal_lines)

            # a goal naming only the Negative persona serves none: its End goals are stated to
            # exclude, so the trace reads none of them
            rc, data = _plan_json(root, "Trevor Hale sees every open bug fixed")
            self.assertTrue(data["goal_trace"]["flagged"])
            self.assertNotIn("checkable", data["goal_trace"])

            # positive control: in the same project a goal naming Maya prints the line on both
            persona_goal = "Maya Okafor sees every open bug fixed"
            self.assertEqual(1, len(_starting(_brief(root, persona_goal), "goal check")))
            self.assertEqual(1, len(_starting(_plan(root, persona_goal)[1].splitlines(),
                                              "goal check")))


class RepeatedNumberTests(unittest.TestCase):
    """Each End goal keeps its own check however the card numbers it, an empty code-span Verify
    names no check, and the traced listing names each persona's own Cast role."""

    _GOALS = (("Walk in to a warm house", None), ("Every open bug is fixed", _PYTEST),
              ("Every room is lit", _MANUAL))

    def _read(self, root: Path, numbers: list[str] | None) -> tuple[list[str], dict]:
        """The traced block with each line's number dropped, and the plan's goal trace."""
        _write_card(root, "Maya Okafor", "Primary", list(self._GOALS), numbers)
        goal = "Maya Okafor sees every open bug fixed"
        block = [ln.split(". ", 1)[-1] for ln in _traced_block(_brief(root, goal))]
        rc, data = _plan_json(root, goal)
        self.assertEqual(0, rc)
        return block, data["goal_trace"]

    def test_goals_numbered_alike_keep_their_own_checks(self) -> None:
        """Mutant: join each End goal to its Verify by the number written on the card, so a card
        numbering every goal `1.` hands each of them the last goal's Verify."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            alike_block, alike = self._read(root, ["1", "1", "1"])
            counted_block, counted = self._read(root, None)
        self.assertEqual(
            ["  Maya Okafor (Primary):",
             "Walk in to a warm house - not testable: no Verify line",
             f"Every open bug is fixed - Verify: {_PYTEST}",
             f"Every room is lit - checked by hand: {_MANUAL}"],
            counted_block)
        self.assertEqual(counted_block, alike_block)

        def _checks(trace: dict) -> list[tuple]:
            return [(g["text"], g["verify"], g["check"]) for g in trace["end_goals"]["Maya Okafor"]]

        self.assertEqual(_checks(counted), _checks(alike))
        self.assertEqual(["1", "1", "1"], [g["number"] for g in alike["end_goals"]["Maya Okafor"]])
        self.assertTrue(alike["checkable"])
        self.assertEqual([{"persona": "Maya Okafor", "number": "1",
                           "text": "Every open bug is fixed", "verify": _PYTEST}],
                         alike["checked_by"])

    def test_an_empty_code_span_verify_is_no_check(self) -> None:
        """Mutant: read the Verify without stripping its backticks, so two backticks and nothing
        between read as an executable check."""
        goal = "Maya Okafor sees every open bug fixed"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary",
                        [("Walk in to a warm house", "``"), ("Every room is lit", None)])
            lines = _brief(root, goal)
            rc, data = _plan_json(root, goal)
        self.assertEqual(
            ["  Maya Okafor (Primary):",
             "    1. Walk in to a warm house - not testable: its Verify names no check",
             "    2. Every room is lit - not testable: no Verify line"],
            _traced_block(lines))
        self.assertEqual(1, len(_starting(lines, "Goal check")))
        self.assertEqual(0, rc)
        trace = data["goal_trace"]
        self.assertEqual(["none", "none"],
                         [g["check"] for g in trace["end_goals"]["Maya Okafor"]])
        self.assertEqual("``", trace["end_goals"]["Maya Okafor"][0]["verify"])
        self.assertFalse(trace["checkable"])

    def test_the_traced_listing_names_each_personas_role(self) -> None:
        """Mutant: label every traced persona Primary in the listing."""
        goal = "Maya Okafor and Hana Ito see every open bug fixed"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write_card(root, "Maya Okafor", "Primary", [("Walk in to a warm house", None)])
            _write_card(root, "Hana Ito", "Secondary", [("Hear about a change", _HANA_VERIFY)])
            block = _traced_block(_brief(root, goal))
        self.assertEqual(["  Hana Ito (Secondary):", "  Maya Okafor (Primary):"],
                         sorted(ln for ln in block if not ln.startswith("    ")))

    def test_persona_cards_returns_no_number_keyed_goal_map(self) -> None:
        """Mutant: keep building a map keyed by the number written on the card beside the goals
        list, the shape that kept only the last of two goals numbered alike."""
        text = _card("Maya Okafor", "Primary",
                     [("Walk in to a warm house", _MANUAL), ("Every open bug is fixed", _PYTEST)],
                     ["1", "1"])
        text += "   - **Applies-to:** `app/bugs/`\n"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "personas").mkdir(parents=True)
            (root / "sdlc-studio" / "personas" / "maya-okafor.md").write_text(text,
                                                                             encoding="utf-8")
            cards = sprint.persona_cards(root)
        self.assertEqual(1, len(cards))
        self.assertEqual({"name", "role", "end_goals", "goals"}, set(cards[0]))
        goals = cards[0]["goals"]
        self.assertEqual([("1", "Walk in to a warm house", _MANUAL, ()),
                          ("1", "Every open bug is fixed", _PYTEST, ("app/bugs/",))],
                         [(g.number, g.text, g.verify, tuple(g.applies_to)) for g in goals])
        self.assertEqual([("1", "Walk in to a warm house"), ("1", "Every open bug is fixed")],
                         cards[0]["end_goals"])
        doc = sprint.persona_cards.__doc__
        named = re.search(r"\[\{([^}]*)\}\]", doc)
        self.assertIsNotNone(named, doc)
        self.assertEqual(["name", "role", "end_goals", "goals"],
                         [k.strip() for k in named.group(1).split(",")])
        self.assertNotIn("goal_verify", doc)
        self.assertNotIn("goal_applies_to", doc)


if __name__ == "__main__":
    unittest.main()
