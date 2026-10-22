"""US1090: AGENTS.md names the push gate as the full-suite check (D0382).

The rule is read as structure, never as a phrase list over its prose (RETRO0135): the bold
sentence leading each paragraph of the Non-negotiable rules section, read as a set, and the
code spans of the paragraph the new lead heads. An `sdlc.` key those spans name is judged live
against the scripts that read it, and a path against the tree.
"""
# test-census-subject: AGENTS.md
from __future__ import annotations

import re
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / "AGENTS.md"
#: The scripts whose `git config --get <key>` reads make a named `sdlc.` key live.
KEY_READERS = (REPO / ".githooks" / "pre-push", REPO / "tools" / "run-suite.sh")

SECTION = "Non-negotiable rules"
RETIRED = "Run the full suite before a commit that touches shared surface."
RULE = "The push gate is the full-suite check."
#: What AC1 says the paragraph the rule leads names, each as a code span.
NAMED = ("sdlc.gateHost", "tools/run-suite.sh all")


def _squash(text: str) -> str:
    return " ".join(text.split())


def _section(text: str, heading: str) -> str:
    """The body of the level-2 section headed exactly `heading`, up to the next level-1 or
    level-2 heading outside a fenced block."""
    lines, start, fenced = text.splitlines(), None, False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else re.match(r"^(#{1,2})\s+(.*?)\s*$", line)
        if start is None:
            if m and len(m.group(1)) == 2 and m.group(2) == heading:
                start = i + 1
        elif m:
            return "\n".join(lines[start:i])
    if start is None:
        raise AssertionError(f"AGENTS.md has no section headed '## {heading}'")
    return "\n".join(lines[start:])


def _leads(section: str) -> dict[str, list[str]]:
    """{lead sentence: [paragraphs it leads]} for each paragraph that opens with a bold span.
    A lead wrapped over two lines reads as one sentence."""
    out: dict[str, list[str]] = {}
    for para in re.split(r"\n[ \t]*\n", section):
        m = re.match(r"\*\*(.+?)\*\*", para.strip(), re.S)
        if m:
            out.setdefault(_squash(m.group(1)), []).append(para.strip("\n"))
    return out


def _spans(paragraph: str) -> set[str]:
    return {_squash(s) for s in re.findall(r"`([^`]+)`", paragraph)}


def _read_keys() -> set[str]:
    return {k for path in KEY_READERS
            for k in re.findall(r"git config --get (sdlc\.[A-Za-z]+)",
                                path.read_text(encoding="utf-8"))}


def _problems(text: str) -> list[str]:
    """Every way `text`, read as AGENTS.md, falls short of AC1; empty when it meets it."""
    leads = _leads(_section(text, SECTION))
    out = []
    if RETIRED in leads:
        out.append(f"the retired lead {RETIRED!r} still leads a paragraph")
    paras = leads.get(RULE, [])
    if len(paras) != 1:
        return out + [f"{RULE!r} leads {len(paras)} paragraphs of the section, not one"]
    spans = _spans(paras[0])
    out += [f"the rule's paragraph does not name `{n}`" for n in NAMED if n not in spans]
    keys = _read_keys()
    for word in (s.split()[0] for s in spans):
        if re.fullmatch(r"sdlc\.[A-Za-z]+", word) and word not in keys:
            out.append(f"the rule names `{word}`, which no script it describes reads")
        if "/" in word and not (REPO / word).exists():
            out.append(f"the rule names `{word}`, which does not exist")
    return out


class FullSuiteRuleTests(unittest.TestCase):

    def test_the_rule_names_the_push_gate(self) -> None:
        """AC1. MUTANTS: keep the retired lead as a paragraph beside the new one; restore it in
        place of the new one; drop the bold from the new lead, or move it mid-paragraph; move
        the paragraph out of the Non-negotiable rules section; drop the gate host key or the
        suite runner's all invocation from the paragraph; lead two paragraphs with the rule;
        name a key no script reads, or a path that does not exist."""
        text = AGENTS.read_text(encoding="utf-8")
        leads = _leads(_section(text, SECTION))
        self.assertGreater(len(leads), 1, "the reader saw one lead or none in the section")
        self.assertTrue(_read_keys(), "the key readers read no sdlc. key, so liveness reads nothing")
        self.assertEqual([], _problems(text))

    def test_each_named_mutant_is_refused(self) -> None:
        """Each mutant the story and the test above name, applied to the real file through the
        paragraph the reader found, is refused: the check is not one that passes on any text."""
        text = AGENTS.read_text(encoding="utf-8")
        para = _leads(_section(text, SECTION))[RULE][0]
        self.assertEqual(1, text.count(para), "the rule's paragraph is not unique in the file")
        lead = f"**{RULE}**"
        retired = f"**{RETIRED}** The gate runs a selected subset."

        def swap(new_para: str) -> str:
            return text.replace(para, new_para)

        mutants = {
            "the retired lead kept beside the new one": swap(para + "\n\n" + retired),
            "the retired lead in place of the new one": swap(para.replace(lead, f"**{RETIRED}**")),
            "the new lead not bold": swap(para.replace(lead, RULE)),
            "the new lead moved mid-paragraph": swap("Read this. " + para),
            "the rule led twice": swap(para + "\n\n" + para),
            "the paragraph moved out of the section": swap("") + "\n" + para + "\n",
            "the paragraph without the gate host key":
                swap(re.sub(r"`sdlc\.gateHost`", "the gate host", para)),
            "the paragraph without the suite runner's all":
                swap(re.sub(r"`tools/run-suite\.sh\s+all`", "the suite runner", para)),
            "a key no script reads": swap(para + " See `sdlc.gateHostName`."),
            "a path that does not exist": swap(para + " See `tools/no-such-runner.sh`."),
        }
        for name, mutated in mutants.items():
            with self.subTest(mutant=name):
                self.assertNotEqual(text, mutated, "the mutation did not apply")
                self.assertNotEqual([], _problems(mutated))

    def test_a_rewrapped_rule_still_reads(self) -> None:
        """The equivalent mutant: the same paragraph flowed to one line, and with one word per
        line, which splits its lead and every code span with a space in it, still meets AC1.
        MUTANT: read the lead or the spans without collapsing their line breaks."""
        text = AGENTS.read_text(encoding="utf-8")
        para = _leads(_section(text, SECTION))[RULE][0]
        flat = _squash(para)
        for width in (len(flat), 1):
            wrapped = textwrap.fill(flat, width=width, break_on_hyphens=False,
                                    break_long_words=False)
            with self.subTest(width=width):
                self.assertEqual([], _problems(text.replace(para, wrapped)))


if __name__ == "__main__":
    unittest.main()
