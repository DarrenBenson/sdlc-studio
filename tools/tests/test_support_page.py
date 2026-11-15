"""SUPPORT.md: what support exists, where to ask and what is not supported.

The page names only channels the repository can show: a GitHub link goes to the repository's
issues (backed by its issue templates) or its security policy (backed by SECURITY.md), every
issue template it names exists, and it gives no install command of its own but links the one
install guide. Each check runs on the live page and on a planted failure beside it.
"""
# test-census-subject: SUPPORT.md
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "SUPPORT.md"
REPO_URL = "https://github.com/DarrenBenson/sdlc-studio"

#: Each required section, found by its level-two heading.
SECTIONS = {
    "what support exists": re.compile(r"\bwhat support exists\b", re.I),
    "where to ask": re.compile(r"\bwhere to ask\b", re.I),
    "what is not supported": re.compile(r"\bnot supported\b", re.I),
}
#: Each GitHub route the page may name, and the path in the repository that backs it.
CHANNELS = (
    (re.compile(rf"^{re.escape(REPO_URL)}/issues(?:/new(?:/choose)?)?/?(?:\?[\w=&.%-]*)?$"),
     ".github/ISSUE_TEMPLATE"),
    (re.compile(rf"^{re.escape(REPO_URL)}/security(?:/policy)?/?$"), "SECURITY.md"),
)
#: Channels nothing in the repository backs: a forum, a chat room, an email address.
UNBACKED = re.compile(r"\b(?:discussions?|forums?|chat|discord|slack|gitter|e-?mail|"
                      r"mailing list)\b|mailto:|[\w.+-]+@[\w-]+\.[a-z]{2,}", re.I)
INSTALL_COMMAND = re.compile(r"\b(?:cp|curl|wget|git clone|npx|npm|pip|irm|iex)\b|"
                             r"install\.(?:sh|ps1)", re.I)

_H2 = re.compile(r"^##\s+(.*?)\s*$")
_URL = re.compile(r"https?://[^\s)>\]]+")
_LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")
_TEMPLATE = re.compile(r"ISSUE_TEMPLATE/([\w.-]+)|[?&]template=([\w.-]+)")
_FENCE = re.compile(r"^\s*(?:```|~~~)")
_SPAN = re.compile(r"`[^`\n]+`")


def split_code(text: str) -> tuple[str, list[str]]:
    """(prose, code): a fenced line or code span is code, the rest prose. An unclosed fence runs
    to the end of the page, so a command cannot hide in it."""
    prose, code, fenced = [], [], False
    for line in text.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
        elif fenced:
            code.append(line)
        else:
            code += _SPAN.findall(line)
            prose.append(_SPAN.sub("", line))
    return "\n".join(prose), code


def missing_sections(text: str) -> list[str]:
    """Each required section the page lacks or repeats."""
    headings = [m.group(1) for line in text.splitlines() if (m := _H2.match(line))]
    problems = []
    for key, pattern in SECTIONS.items():
        found = [h for h in headings if pattern.search(h)]
        if len(found) != 1:
            problems.append(f"{len(found)} sections for {key}")
    return problems


def channel_problems(text: str, repo: Path = REPO) -> list[str]:
    """Each channel the page names that the repository at `repo` does not back."""
    problems = []
    for url in _URL.findall(text):
        url = url.rstrip(".,;")
        backing = next((path for pattern, path in CHANNELS if pattern.match(url)), None)
        if backing is None:
            problems.append(f"{url} is not the repository's issues or security policy")
        elif not (repo / backing).exists():
            problems.append(f"{url} has no {backing} behind it")
    prose, code = split_code(text)
    for m in UNBACKED.finditer(_URL.sub("", prose)):
        problems.append(f"names {m.group(0)!r}, which nothing in the repository backs")
    for a, b in _TEMPLATE.findall(text):
        if not (repo / ".github" / "ISSUE_TEMPLATE" / (a or b)).is_file():
            problems.append(f"names the issue template {a or b}, which does not exist")
    for line in code:
        if INSTALL_COMMAND.search(line):
            problems.append(f"gives an install command of its own: {line.strip()[:60]}")
    if not any((PAGE.parent / t.partition("#")[0]).resolve() == (REPO / "docs" / "INSTALL.md")
               for t in _LINK_TARGET.findall(text)):
        problems.append("links no docs/INSTALL.md")
    return problems


ISSUES = f"{REPO_URL}/issues"
INSTALL = "See [installing](docs/INSTALL.md)."


class SupportPageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = PAGE.read_text(encoding="utf-8")

    def test_the_three_sections_are_present(self) -> None:
        self.assertEqual(missing_sections(self.text), [])
        # Planted failures: each section renamed away, and a section repeated.
        for key, pattern in SECTIONS.items():
            cut = "\n".join("## Elsewhere" if _H2.match(ln) and pattern.search(ln) else ln
                            for ln in self.text.splitlines())
            self.assertEqual(missing_sections(cut), [f"0 sections for {key}"])
        self.assertEqual(missing_sections(self.text + "\n## Where to ask, again\n"),
                         ["2 sections for where to ask"])

    def test_every_channel_named_exists(self) -> None:
        self.assertEqual(channel_problems(self.text), [])
        self.assertRegex(self.text, _TEMPLATE, "the page names no issue template")
        # A positive control, then each planted failure alone.
        self.assertEqual(channel_problems(f"Ask in [issues]({ISSUES}). {INSTALL}"), [])
        planted = {
            "```bash\ncp -r .claude/skills/sdlc-studio ~/.claude/skills/\n```":
                "gives an install command of its own: cp -r .claude/skills/sdlc-studio ~/.claude/skills/",
            "Run `bash install.sh` first.": "gives an install command of its own: `bash install.sh`",
            "Ask in GitHub Discussions.": "names 'Discussions', which nothing in the repository backs",
            "Find us on Discord.": "names 'Discord', which nothing in the repository backs",
            "Write to help@example.org.": "names 'help@example.org', which nothing in the "
                                          "repository backs",
            f"Ask [here]({REPO_URL}/discussions).":
                f"{REPO_URL}/discussions is not the repository's issues or security policy",
            "Use the [bug form](.github/ISSUE_TEMPLATE/question.md).":
                "names the issue template question.md, which does not exist",
            f"Use [the form]({ISSUES}/new?template=support.yml).":
                "names the issue template support.yml, which does not exist",
        }
        for text, problem in planted.items():
            self.assertEqual(channel_problems(f"{text}\n\n{INSTALL}"), [problem], text)
        self.assertEqual(channel_problems(f"{INSTALL}\n\n```\ncurl -fsSL x | bash\n"),
                         ["gives an install command of its own: curl -fsSL x | bash"])
        self.assertEqual(channel_problems(f"Ask in [issues]({ISSUES})."), ["links no docs/INSTALL.md"])
        with tempfile.TemporaryDirectory() as bare:
            self.assertEqual(channel_problems(f"Ask in [issues]({ISSUES}). {INSTALL}", Path(bare)),
                             [f"{ISSUES} has no .github/ISSUE_TEMPLATE behind it"])
            self.assertEqual(channel_problems(f"Read [it]({REPO_URL}/security/policy). {INSTALL}",
                                              Path(bare)),
                             [f"{REPO_URL}/security/policy has no SECURITY.md behind it"])


if __name__ == "__main__":
    unittest.main()
