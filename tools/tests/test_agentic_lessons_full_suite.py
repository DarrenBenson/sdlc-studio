"""BG1116: the shipped habit and AGENTS.md name the full suite where the gate runs it.

AC1 reads the habits list of the "Review BEFORE the commit, not after" lesson in
reference-agentic-lessons.md as structure: the bullet list in that lesson, the paragraph
leading into it, and the bold sentence leading each bullet, read as a set. AC2 reads the
paragraph of AGENTS.md that "The push gate is the full-suite check." leads, beside the
pre-push hook's ref loop it describes.

The boundary habit is read for its route too: it names the project's own full test command,
and names no `gate.py` while gate.py's full-suite lane reads only the suites its
`TEST_SUITE_DIRS` lists, which are this repository's own. On a consuming project that lane
reports N/A and the gate passes with no test run (BG1116 round 1).
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-agentic-lessons.md
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LESSONS = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-agentic-lessons.md"
AGENTS = REPO / "AGENTS.md"
PRE_PUSH = REPO / ".githooks" / "pre-push"
GATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"
#: Where this repository keeps its own suites: a `TEST_SUITE_DIRS` entry under one of these is
#: not a consuming project's.
OWN_SUITE_ROOTS = (".claude/skills/sdlc-studio/", "tools/")
#: The round-1 habit body, which sent a consuming project to `gate.py --boundary push`.
ROUND_1 = ("Let a commit run the test modules its change selects, and run the whole suite "
           "before each push (`gate.py --boundary push`, or the project's own pre-push hook).")

LESSON = "Review BEFORE the commit, not after"
COUNTS = {w: n for n, w in enumerate(
    "zero one two three four five six seven eight nine ten".split())}
RULE = "The push gate is the full-suite check."


def _squash(text: str) -> str:
    return " ".join(text.split())


def _lesson(text: str) -> str:
    """The body of the `### LESSON` section, up to the next heading of level 1 to 3 outside a
    fenced block."""
    lines, start, fenced = text.splitlines(), None, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else re.match(r"^(#{1,3})\s+(.*?)\s*$", line)
        if start is None:
            if m and len(m.group(1)) == 3 and m.group(2) == LESSON:
                start = i + 1
        elif m:
            return "\n".join(lines[start:i])
    if start is None:
        raise AssertionError(f"the lessons page has no section headed '### {LESSON}'")
    return "\n".join(lines[start:])


def _habits(text: str) -> tuple[str, list[str]]:
    """(the paragraph leading into the lesson's bullet list, the bold lead of each bullet, "" for
    a bullet with none). A lead wrapped over two lines reads as one sentence."""
    blocks = re.split(r"\n[ \t]*\n", _lesson(text).strip("\n"))
    for i, block in enumerate(blocks):
        if i and block.startswith("- "):
            items = re.split(r"\n(?=- )", block)
            leads = [m.group(1) if (m := re.match(r"- \*\*(.+?)\*\*", item, re.S)) else ""
                     for item in items]
            return _squash(blocks[i - 1]), [_squash(lead) for lead in leads]
    raise AssertionError(f"the lesson '{LESSON}' carries no bullet list after a paragraph")


def _stated_count(lead_in: str) -> int | None:
    """The first count the lead-in names, as a word or digits; None when it names none."""
    for word in re.findall(r"[A-Za-z]+|\d+", lead_in):
        if word.isdigit():
            return int(word)
        if word.lower() in COUNTS:
            return COUNTS[word.lower()]
    return None


def _habit_problems(text: str) -> list[str]:
    """Every way `text`, read as the lessons page, falls short of AC1; empty when it meets it."""
    lead_in, leads = _habits(text)
    out = [f"habit {n} has no bold lead" for n, lead in enumerate(leads, 1) if not lead]
    suite = [lead for lead in leads if re.search(r"\bfull suite\b", lead, re.I)]
    out += [f"{lead!r} runs the full suite per commit" for lead in suite
            if re.search(r"\b(every|each|a)\s+commit\b", lead, re.I)]
    at_push = [lead for lead in suite if re.search(r"\bpush\b", lead, re.I)]
    if len(at_push) != 1:
        out.append(f"{len(at_push)} leads name the full suite at the push boundary, not one")
    count = _stated_count(lead_in)
    if count != len(leads):
        out.append(f"the lead-in states {count} habits and the list holds {len(leads)}")
    return out


def _rule_paragraph(text: str) -> str:
    """The one paragraph of `text` that opens with the bold RULE, squashed."""
    paras = [p for p in re.split(r"\n[ \t]*\n", text)
             if _squash(p).startswith(f"**{RULE}**")]
    if len(paras) != 1:
        raise AssertionError(f"{len(paras)} paragraphs open with **{RULE}**, not one")
    return _squash(paras[0])


def _push_gate_problems(text: str) -> list[str]:
    """Every way `text`, read as AGENTS.md, falls short of AC2; empty when it meets it."""
    para, out = _rule_paragraph(text), []
    if "each pushed ref points at" not in para:
        out.append("the push-gate paragraph does not say the hook judges the commit each "
                   "pushed ref points at")
    if re.search(r"\b(each|every) pushed commit\b", para):
        out.append("the push-gate paragraph still says the hook judges each pushed commit")
    return out


def _boundary_habit(text: str) -> str:
    """The whole habit, squashed, whose bold lead names the full suite at the push boundary."""
    blocks = re.split(r"\n[ \t]*\n", _lesson(text).strip("\n"))
    for block in (b for b in blocks if b.startswith("- ")):
        for item in re.split(r"\n(?=- )", block):
            m = re.match(r"- \*\*(.+?)\*\*", item, re.S)
            if m and re.search(r"\bfull suite\b", m.group(1), re.I) \
                    and re.search(r"\bpush\b", m.group(1), re.I):
                return _squash(item)
    raise AssertionError("no habit's lead names the full suite at the push boundary")


def _swap_body(text: str, body: str, new: str) -> str:
    """`text` with the squashed `body` replaced by `new`, however the page wraps it."""
    return re.sub(r"\s+".join(map(re.escape, body.split())), lambda _m: new, text, count=1)


def _gate_suite_dirs() -> tuple[str, ...]:
    """gate.py's `TEST_SUITE_DIRS`, the suites its full-suite lane and its selection read."""
    for node in ast.parse(GATE.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "TEST_SUITE_DIRS" for t in node.targets):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError("gate.py no longer assigns TEST_SUITE_DIRS")


def _route_problems(text: str, suite_dirs: tuple[str, ...]) -> list[str]:
    """Every way the boundary habit in `text` routes a consuming project's push to a command
    that would not run its tests, given gate.py's `suite_dirs`; empty when it routes none."""
    habit, out = _boundary_habit(text), []
    if re.search(r"\bgate\.py\b", habit) and all(d.startswith(OWN_SUITE_ROOTS)
                                                 for d in suite_dirs):
        out.append(f"the boundary habit names gate.py, whose full-suite lane reads only "
                   f"{suite_dirs}, so a consuming project's push gate runs none of its tests")
    if not re.search(r"\bproject's own full test command\b", habit):
        out.append("the boundary habit does not name the project's own full test command")
    return out


class AgenticLessonsFullSuiteTests(unittest.TestCase):

    def test_the_habit_runs_the_full_suite_at_the_boundary(self) -> None:
        """AC1. MUTANTS: the retired per-commit lead restored; the boundary lead dropped; the
        lead-in's count left at two (see the mutant test below)."""
        text = LESSONS.read_text(encoding="utf-8")
        lead_in, leads = _habits(text)
        self.assertGreater(len(leads), 1, "the reader saw one habit or none")
        self.assertIsNotNone(_stated_count(lead_in), "the reader found no count in the lead-in")
        self.assertEqual([], _habit_problems(text))

    def test_the_boundary_habit_names_the_projects_own_test_command(self) -> None:
        """BG1116 round 1. The habit names the project's own full test command and no gate.py
        while gate.py reads only this repository's suites. MUTANTS: the round-1 body restored;
        gate.py named beside the project's command; the project's command dropped."""
        text = LESSONS.read_text(encoding="utf-8")
        dirs = _gate_suite_dirs()
        self.assertTrue(dirs and all(d.startswith(OWN_SUITE_ROOTS) for d in dirs),
                        f"gate.py now reads {dirs}: re-judge whether it can carry the habit")
        self.assertEqual([], _route_problems(text, dirs))
        body = _boundary_habit(text).split("** ", 1)[1].split(" Two commits", 1)[0]
        round_1 = _swap_body(text, body, ROUND_1)
        mutants = {
            "the round-1 body": round_1,
            "gate.py beside the project's command":
                _swap_body(text, body, body + " Or run `gate.py --boundary push`."),
            "the project's command dropped":
                _swap_body(text, body, "Run the whole suite before each push."),
        }
        for name, mutated in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(text, mutated, "the mutation did not apply")
                self.assertNotEqual([], _route_problems(mutated, dirs))
        # The refusal of gate.py rests on what gate.py reads: were its suites a project's own,
        # the round-1 route would no longer be refused for naming it.
        self.assertFalse([p for p in _route_problems(round_1, ("tests",)) if "gate.py" in p])
        self.assertTrue([p for p in _route_problems(round_1, dirs) if "gate.py" in p])

    def test_each_habit_mutant_is_refused(self) -> None:
        """Each AC1 mutant, applied to the real page, is refused, and each of the last four by
        one check alone, so no check rides on another."""
        text = LESSONS.read_text(encoding="utf-8")
        lead_in, leads = _habits(text)
        at_push = next(lead for lead in leads if re.search(r"\bpush\b", lead, re.I))
        other = next(lead for lead in leads if lead != at_push)
        para = next(p for p in re.split(r"\n[ \t]*\n", text) if _squash(p) == lead_in)
        retired = "Run the full suite before every commit, never a filtered subset."
        word = next(w for w in re.findall(r"[A-Za-z]+", lead_in) if w.lower() in COUNTS)
        fewer = next(w for w, n in COUNTS.items() if n == COUNTS[word.lower()] - 1)

        def lead(old: str, new: str) -> str:
            span = re.search(r"\*\*" + r"\s+".join(map(re.escape, old.split())) + r"\*\*", text)
            return text.replace(span.group(0), new, 1)

        mutants = {
            "the retired lead in place of the boundary lead": lead(at_push, f"**{retired}**"),
            "the retired lead beside the boundary lead":
                lead(at_push, f"**{at_push}** x\n- **{retired}**"),
            "the boundary lead also asks for every commit":
                lead(at_push, "**Run the full suite at the push boundary and before every "
                              "commit.**"),
            "the boundary lead without the push":
                lead(at_push, "**Run the full suite before the work leaves the machine.**"),
            "the lead-in states one habit fewer":
                text.replace(para, para.replace(word, fewer.capitalize(), 1)),
            "a habit with no bold lead": lead(other, other),
        }
        for name, mutated in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(text, mutated, "the mutation did not apply")
                problems = _habit_problems(mutated)
                self.assertNotEqual([], problems)
                if name not in list(mutants)[:2]:
                    self.assertEqual(1, len(problems), problems)

    def test_agents_md_names_the_commit_each_ref_points_at(self) -> None:
        """AC2. The hook collects one commit per stdin ref line and enumerates no commit below
        it, which is what the paragraph must say. MUTANT: restore 'on each pushed commit'."""
        hook = PRE_PUSH.read_text(encoding="utf-8")
        self.assertRegex(hook, r"while read -r \S+ local_sha remote_ref \S+; do",
                         "the hook no longer reads one commit per stdin ref line")
        self.assertNotIn("rev-list", hook,
                         "the hook now enumerates the commits below a ref, so 'the commit each "
                         "pushed ref points at' no longer describes it")
        text = AGENTS.read_text(encoding="utf-8")
        self.assertEqual([], _push_gate_problems(text))
        para = next(p for p in re.split(r"\n[ \t]*\n", text)
                    if _squash(p).startswith(f"**{RULE}**"))
        old = text.replace(para, re.sub(r"the commit each\s+pushed ref points at",
                                        "each pushed commit", para))
        self.assertNotEqual(text, old, "the mutation did not apply")
        self.assertNotEqual([], _push_gate_problems(old))


if __name__ == "__main__":
    unittest.main()
