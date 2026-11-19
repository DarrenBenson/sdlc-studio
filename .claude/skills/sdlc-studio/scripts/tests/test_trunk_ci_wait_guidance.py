"""After a `trunk` push the agent waits on the CI run that push started with one blocking command
under a timeout, never a polling loop, and reads a red main before it pushes again.

A polling loop re-reads the run into the session on every pass, so a long-lived session grows
with each wait; one blocking watch costs one call. The rule is stated in the `trunk` section of
`reference-code.md`, and in the same words in the shipped agent-instructions template, which is
the one page a consuming project's agent loads on every call.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-code.md
# test-census-subject: .claude/skills/sdlc-studio/templates/agent-instructions.md
# test-census-subject: .claude/skills/sdlc-studio/reference-test-validation.md
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
CODE_REF = SKILL / "reference-code.md"
TEST_REF = SKILL / "reference-test-validation.md"
TEMPLATE = SKILL / "templates" / "agent-instructions.md"
sys.path.insert(0, str(SCRIPTS))

import init  # noqa: E402

#: The template's ceiling in characters, the figure `test_agent_instructions_budget.py` holds.
CAP = 5_000
#: The rule's three clauses, each of which the reference and the template state.
WAIT = "one blocking command under a timeout"
NO_LOOP = "never a polling loop"
RED_MAIN = "read a red main before pushing again"
#: The GitHub form of the one blocking command.
WATCH = "gh run watch <id> --exit-status"
#: A shell loop or a sleep in a fence: the shape of polling.
LOOP = re.compile(r"\b(while|until|for)\b[^#]*\bdo\b|^\s*done\b|\bsleep\b|\bwatch\s+-n\b", re.M)


def _fold(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _trunk_section() -> str:
    """The body of `### \\`trunk\\`` up to the next heading of level three or above, skipping `#`
    comments inside a code fence."""
    lines = CODE_REF.read_text(encoding="utf-8").splitlines()
    start = lines.index("### `trunk`")
    body, inside = [], False
    for ln in lines[start + 1:]:
        if ln.lstrip().startswith("```"):
            inside = not inside
        if not inside and re.match(r"#{1,3}\s", ln):
            break
        body.append(ln)
    return "\n".join(body)


def _fenced(text: str) -> list[str]:
    rows, inside = [], False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            inside = not inside
            continue
        if inside:
            rows.append(ln)
    return rows


def _rule(text: str) -> str:
    """The one sentence of `text` that states the blocking wait."""
    found = re.findall(rf"[^.]*{re.escape(WAIT)}[^.]*\.", _fold(text))
    if len(found) != 1:
        raise AssertionError(f"expected one sentence stating the wait, found {found}")
    return found[0].strip()


class TrunkCiWaitGuidanceTests(unittest.TestCase):

    def test_the_trunk_section_waits_with_one_blocking_watch_under_a_timeout(self) -> None:
        """AC1. MUTANTS: the fence ending at `git push origin main`; the watch line before the
        push, without `timeout`, or without `--exit-status`; a `while`/`until`/`for` loop or a
        `sleep` over `gh run list` in the fence; the prose dropping the blocking command, the
        GitHub watch or the never-poll clause."""
        section = _trunk_section()
        commands = [c.strip() for c in _fenced(section)]
        push = next((i for i, c in enumerate(commands) if c == "git push origin main"), None)
        self.assertIsNotNone(push, commands)
        watch = [i for i, c in enumerate(commands)
                 if re.fullmatch(r"timeout \S+ gh run watch <id> --exit-status(\s+#.*)?", c)]
        self.assertEqual(1, len(watch), f"one timed watch line, not {commands}")
        self.assertGreater(watch[0], push, "the wait comes after the push")
        self.assertIsNone(LOOP.search("\n".join(commands)), commands)
        self.assertEqual([], [c for c in commands if "gh run list" in c and "--limit 1" not in c])
        prose = _fold(section)
        for words in (WAIT, NO_LOOP, f"`{WATCH}`", "never loop over `gh run list`"):
            self.assertIn(words, prose)

    def test_a_red_main_is_read_before_the_next_push(self) -> None:
        """AC2. MUTANTS: the red-main sentence cut or turned into "push the next unit"; the
        pointer to the red-run policy dropped, or naming an anchor the test reference lacks, one
        outside its flakiness section or another subsection of it; the policy restated here (its
        rerun or flake terms)."""
        prose = _fold(_trunk_section())
        self.assertIn(RED_MAIN, prose)
        self.assertIn("A red main is read before anything is pushed again", prose)
        pointer = re.findall(r"`reference-test-validation\.md#([a-z0-9-]+)`", prose)
        self.assertEqual(1, len(pointer), prose)
        ref = TEST_REF.read_text(encoding="utf-8")
        flaky = ref[ref.index("\n## Flakiness Prevention {#flakiness-prevention}"):]
        flaky = flaky[:flaky.index("\n## ", 1)]
        self.assertIn(f"{{#{pointer[0]}}}", flaky, "the pointer must land in the flakiness section")
        policy = flaky[flaky.index(f"{{#{pointer[0]}}}"):]
        policy = policy.split("\n### ", 1)[0]
        self.assertIn("`gate.py --red-run`", policy, "the pointer must land on the red-run policy")
        lower = prose.lower()
        self.assertNotIn("rerun", lower, "point at the policy, do not restate it")
        self.assertNotIn("flak", lower, "point at the policy, do not restate it")

    def test_the_agent_instructions_template_carries_the_wait_rule(self) -> None:
        """AC3. MUTANTS: the template silent on the wait or the red-main read; the rule
        reworded so it differs from the reference's sentence; the template grown past 5,000
        characters; init dropping the line from a project's AGENTS.md."""
        rule = _rule(_trunk_section())
        for words in (WAIT, NO_LOOP, RED_MAIN):
            self.assertIn(words, rule)
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertLessEqual(len(text), CAP, f"the template is {len(text):,} chars")
        self.assertEqual(rule, _rule(text), "the template must use the reference's words")
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d) / "acme"
            repo.mkdir()
            init.init(repo)
            self.assertEqual(rule, _rule((repo / "AGENTS.md").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
