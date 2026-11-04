"""BG1116: the shipped habit and AGENTS.md name the full suite where the gate runs it.

AC1 reads the habits list of the "Review BEFORE the commit, not after" lesson in
reference-agentic-lessons.md as structure: the bullet list in that lesson, the paragraph
leading into it, and the bold sentence leading each bullet, read as a set. AC2 reads the
paragraph of AGENTS.md that "The push gate is the full-suite check." leads, beside the
pre-push hook's ref loop it describes.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-agentic-lessons.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LESSONS = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-agentic-lessons.md"
AGENTS = REPO / "AGENTS.md"
PRE_PUSH = REPO / ".githooks" / "pre-push"

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


class AgenticLessonsFullSuiteTests(unittest.TestCase):

    def test_the_habit_runs_the_full_suite_at_the_boundary(self) -> None:
        """AC1. MUTANTS: the retired per-commit lead restored; the boundary lead dropped; the
        lead-in's count left at two (see the mutant test below)."""
        text = LESSONS.read_text(encoding="utf-8")
        lead_in, leads = _habits(text)
        self.assertGreater(len(leads), 1, "the reader saw one habit or none")
        self.assertIsNotNone(_stated_count(lead_in), "the reader found no count in the lead-in")
        self.assertEqual([], _habit_problems(text))

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
