"""The reference pages say a config-reading command refuses when PyYAML will not import.

A present `.config.yaml` that PyYAML cannot read is refused: exit 1, one stderr line naming the
file and the install command. It is never read as the shipped defaults. Three reference pages
still described the behaviour this replaced (`config.get` degrading to the built-in default, the
config migration reporting its keys on a machine without PyYAML, and `config.py` degrading
without it), so a consuming agent reading them expected a run to carry on and misread the refusal.

The check judges each PARAGRAPH that names PyYAML, not a list of the old sentences: the paragraph
must state the refusal with its exit status, no sentence in it may describe PyYAML's absence
without the refusal, and none may say the scripts degrade, fall back or carry on with the
defaults. A negation directly before such a phrase states the contract rather than breaking it.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/reference-config.md
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
PAGES = ("reference-config.md", "reference-upgrade.md", "reference-scripts-domain.md")

#: PyYAML as a word, so `pip install pyyaml` counts and a longer identifier does not.
_NAMES_PYYAML = re.compile(r"(?<![\w-])pyyaml(?![\w-])", re.I)
#: A sentence about PyYAML being unavailable, in the phrasings that mean it.
_ABSENT = re.compile(
    r"(without\s+pyyaml|no\s+pyyaml|"
    r"pyyaml\s+(?:is\s+)?(?:absent|missing|not\s+installed|isn'?t\s+installed|unavailable)|"
    r"pyyaml\s+(?:will\s+not|won'?t|does\s+not|cannot|can'?t)\s+(?:be\s+)?import|"
    r"(?:cannot|can'?t|will\s+not|does\s+not)\s+import\s+pyyaml)", re.I)
_REFUSES = re.compile(r"\brefus(?:e|es|ed|ing|al)\b", re.I)
_EXIT_1 = re.compile(r"\bexits?\s*(?:status\s+|code\s+)?1\b", re.I)
_NAMES_CONFIG = re.compile(r"config", re.I)
#: The claim the shipped refusal contradicts: the run degrades, falls back or carries on.
_CARRIES_ON = re.compile(
    r"(degrad\w*|fall(?:s|ing)?\s+back|fallback|graceful\w*|carr(?:y|ies|ying)\s+on|"
    r"do(?:es)?\s+not\s+crash|"
    r"(?:runs?|running|continues?|proceeds?|uses?|using)\s+(?:on\s+|with\s+)?(?:the\s+)?"
    r"(?:built-in\s+|shipped\s+)?defaults?\b)", re.I)
#: A negation directly before the phrase, scoped by adjacency so a negating word elsewhere in
#: the sentence cannot license the claim.
_NEGATED = re.compile(r"\b(does\s+not|doesn'?t|do\s+not|never|no\s+longer|rather\s+than|not)\s*$",
                      re.I)
_NEGATION_WINDOW = 24
_BREAK = re.compile(r"^\s*(?:\d+\.|[-*+])\s|^\s*#")


def paragraphs(text: str) -> list[str]:
    """The page's paragraphs, each on one line: blocks split at blank lines, list items and
    headings, so one numbered item is judged on its own and not with its neighbours."""
    out: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if not line.strip() or _BREAK.match(line):
            if current:
                out.append(current)
            current = [line] if line.strip() else []
            continue
        current.append(line)
    if current:
        out.append(current)
    return [" ".join(" ".join(block).split()) for block in out]


def _sentences(paragraph: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", paragraph)


def pyyaml_findings(where: str, paras: list[str]) -> list[str]:
    """What each paragraph naming PyYAML gets wrong about a machine that cannot import it."""
    out = []
    for para in paras:
        if not _NAMES_PYYAML.search(para):
            continue
        head = f"{where}: {para[:60]!r}"
        sentences = _sentences(para)
        if not any(_ABSENT.search(s) and _REFUSES.search(s) and _EXIT_1.search(s)
                   and _NAMES_CONFIG.search(s) for s in sentences):
            out.append(f"{head} names PyYAML but does not say a config-reading command refuses "
                       "(exit 1) when PyYAML will not import")
        for s in sentences:
            if _ABSENT.search(s) and not _REFUSES.search(s):
                out.append(f"{head} describes PyYAML's absence without the refusal: {s[:80]!r}")
        for m in _CARRIES_ON.finditer(para):
            before = para[max(0, m.start() - _NEGATION_WINDOW):m.start()]
            if not _NEGATED.search(before.rstrip()):
                out.append(f"{head} says the run carries on without PyYAML: {m.group(0)!r}")
    return out


#: The three removed passages, each as the paragraph it stood in (reference-upgrade.md's list
#: item cut to the sentences around its PyYAML one) and, verbatim, as the sentence that carried
#: the claim.
RESTORED = {
    "reference-config.md": (
        "**PyYAML dependency (graceful):** parsing `.config.yaml` needs PyYAML (`pip install "
        "pyyaml`). Without it, the scripts do not crash: `config.get` degrades to the built-in "
        "default with a one-line stderr warning, so a stdlib-only machine runs on the defaults. "
        "A project that ships a `.config.yaml` should install PyYAML so its declared conventions "
        "are actually applied.",
        "Without it, the scripts do not crash: `config.get` degrades to the built-in default "
        "with a one-line stderr warning, so a stdlib-only machine runs on the defaults."),
    "reference-upgrade.md": (
        "4. **retired review surfaces** - a retired `[check: <id>]` tag in the Definition of "
        "Ready or Done is removed and its criterion kept as a human-judged item. A comment "
        "directly above a removed key is kept and named. Every rewrite is re-parsed with PyYAML "
        "and must equal the original minus those keys; a layout that cannot be edited line by "
        "line (a flow mapping), or a machine without PyYAML, gets nothing written and the keys "
        "reported. The ids and keys come from `sdlc_md.RETIRED_CHECK_IDS` and "
        "`sdlc_md.RETIRED_CONFIG_KEYS`.",
        "Every rewrite is re-parsed with PyYAML and must equal the original minus those keys; a "
        "layout that cannot be edited line by line (a flow mapping), or a machine without "
        "PyYAML, gets nothing written and the keys reported."),
    "reference-scripts-domain.md": (
        "Merged per-project configuration reader. Layers `templates/config-defaults.yaml` under "
        "the project's `sdlc-studio/.config.yaml` (degrading without PyYAML); the source of "
        "`status_vocab`, adoption cutoffs, `complexity`, `constitution`, `version_check`, "
        "`provenance`, etc.",
        "Layers `templates/config-defaults.yaml` under the project's `sdlc-studio/.config.yaml` "
        "(degrading without PyYAML); the source of `status_vocab`, adoption cutoffs, "
        "`complexity`, `constitution`, `version_check`, `provenance`, etc."),
}


#: A paragraph naming PyYAML that leaves out one part of the refusal: each is a finding.
SILENT = {
    "no absence": "A command that reads a malformed `.config.yaml` refuses (exit 1); parsing "
                  "it needs PyYAML.",
    "no exit status": "When PyYAML will not import, a command that reads `.config.yaml` refuses.",
    "no config read": "When PyYAML will not import, the command refuses (exit 1).",
    "no refusal at all": "Parsing `.config.yaml` needs PyYAML.",
}


def _refusing(paras: list[str]) -> int:
    """The index of the paragraph that states the refusal, or -1."""
    for i, para in enumerate(paras):
        if _NAMES_PYYAML.search(para) and not pyyaml_findings("", [para]):
            return i
    return -1


class ReferencePagesPyYamlTests(unittest.TestCase):
    def test_every_pyyaml_paragraph_says_the_command_refuses(self) -> None:
        """AC1. MUTANT: any of the three pages back on its old passage. MUTANT: a page whose
        PyYAML paragraph is deleted, which a check over no paragraphs would pass."""
        for name in PAGES:
            with self.subTest(page=name):
                paras = paragraphs((SKILL / name).read_text(encoding="utf-8"))
                self.assertEqual([], pyyaml_findings(name, paras))
                self.assertNotEqual(-1, _refusing(paras),
                                    f"{name} carries no paragraph saying a config-reading "
                                    "command refuses (exit 1) when PyYAML will not import")
        for gap, para in SILENT.items():
            with self.subTest(silent=gap):
                self.assertNotEqual([], pyyaml_findings("silent", [para]))

    def test_a_restored_fallback_passage_fails_the_check(self) -> None:
        """AC2. Each removed passage, put back in place of the live paragraph or beside its
        refusal, is a finding; a negated fallback beside the refusal is not."""
        for name, (paragraph, sentence) in RESTORED.items():
            paras = paragraphs((SKILL / name).read_text(encoding="utf-8"))
            i = _refusing(paras)
            self.assertNotEqual(-1, i, f"{name} has no refusing paragraph to restore over")
            with self.subTest(page=name, restored="in place of the live paragraph"):
                self.assertNotEqual([], pyyaml_findings(name, paras[:i] + [paragraph]
                                                        + paras[i + 1:]))
            with self.subTest(page=name, restored="beside the refusal"):
                beside = paras[:i] + [f"{paras[i]} {sentence}"] + paras[i + 1:]
                self.assertNotEqual([], pyyaml_findings(name, beside))
            with self.subTest(page=name, control="a negated fallback beside the refusal"):
                negated = paras[:i] + [f"{paras[i]} It never falls back to the built-in "
                                       "defaults."] + paras[i + 1:]
                self.assertEqual([], pyyaml_findings(name, negated))


if __name__ == "__main__":
    unittest.main()
