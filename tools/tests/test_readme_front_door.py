"""README.md is a front door: short, and opening with three routes in, each to a page that exists.

The reader is a head of engineering deciding whether to evaluate SDLC Studio, try it or upgrade
a project already on it. The page is counted as `wc -w` counts it, over the whole file, and its
first section after the badges must offer the three routes in that order, each linking the
page that carries it: evaluate to the engineering-leaders page and the evidence page, try to
the install guide, upgrade to the existing-users page. Each check returns its problems and runs
on the live README and on planted failures beside it: a route missing, out of order, or linking
a file that does not exist.

The opening paragraph claims no more than the process does: each step is reviewed independently
of its author and a named person signs each run, and no sentence has a person approving each
step. One line points an agent at llms.txt and AGENTS.md, both files that exist.
"""
# test-census-subject: README.md
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
MAX_WORDS = 1800

#: Each route, in the order the section must offer it -> the bold lead that opens its bullet,
#: and the pages it must link, relative to the repository root.
ROUTES = (
    ("evaluate", re.compile(r"^evaluate\b", re.I),
     ("docs/engineering-leaders.md", "docs/evidence.md")),
    ("try", re.compile(r"^try\b", re.I), ("docs/INSTALL.md",)),
    ("upgrade", re.compile(r"^upgrade\b", re.I), ("docs/existing-users.md",)),
)
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_BULLET = re.compile(r"^- \*\*(.+?)\*\*(.*?)(?=^- |^\S|\Z)", re.M | re.S)


def words(text: str) -> int:
    """What `wc -w` counts: runs of non-whitespace bytes."""
    return len(text.encode("utf-8").split())


def first_section(text: str) -> tuple[str, str]:
    """(heading, body) of the first level-two section after the badges' closing `</div>`."""
    body = text.split("</div>", 1)[1] if "</div>" in text else text
    m = re.search(r"^## (.*?)\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    return (m.group(1), m.group(2)) if m else ("", "")


def route_problems(text: str, root: Path = REPO) -> list[str]:
    """The three routes, in order, each linking the pages it must and only pages that exist."""
    heading, body = first_section(text)
    if not heading:
        return ["the README has no section after the badges"]
    bullets = [(lead.strip(), lead + rest) for lead, rest in _BULLET.findall(body)]
    problems, positions = [], []
    for name, opens, pages in ROUTES:
        hits = [i for i, (lead, _) in enumerate(bullets) if opens.search(lead)]
        if len(hits) != 1:
            problems.append(f"the first section ('{heading}') offers the {name} route "
                            f"{len(hits)} times, not once")
            continue
        positions.append(hits[0])
        links = [t.split("#", 1)[0] for t in _LINK.findall(bullets[hits[0]][1])
                 if not re.match(r"[a-z]+:", t)]
        for page in pages:
            if page not in links:
                problems.append(f"the {name} route does not link {page}")
        for link in links:
            if link and not (root / link).is_file():
                problems.append(f"the {name} route links {link}, which does not exist")
    if positions != sorted(positions):
        problems.append("the routes are not in the order evaluate, try, upgrade")
    return problems


#: The opening's sentence before it was corrected, kept as a planted failure.
OLD_OPENING = ("You describe what you want in plain language; the agent does the work, and a "
               "person you can name reviews and approves each step.")


def opening(text: str) -> str:
    """The first paragraph after the badges' closing `</div>`, its whitespace collapsed."""
    body = text.split("</div>", 1)[1] if "</div>" in text else text
    paragraph = next((p for p in re.split(r"\n\s*\n", body) if p.strip()), "")
    return " ".join(paragraph.split())


def opening_problems(text: str) -> list[str]:
    """What the opening claims against what the process does, judged sentence by sentence."""
    sentences = re.split(r"(?<=[.;])\s+", opening(text))
    problems = []
    if any(re.search(r"\bapprov\w*\b.*\beach step\b", s, re.I) for s in sentences):
        problems.append("the opening says a person approves each step")
    if not any(re.search(r"\bindependent", s, re.I) and re.search(r"\beach step\b", s, re.I)
               for s in sentences):
        problems.append("the opening does not say each step is reviewed independently")
    if not any(re.search(r"\bsigns?\b", s, re.I) and re.search(r"\beach run\b", s, re.I)
               and re.search(r"\b(?:person|principal)\b", s, re.I) for s in sentences):
        problems.append("the opening does not say a named person signs each run")
    return problems


def agent_pointer_problems(text: str, root: Path = REPO) -> list[str]:
    """One line links both llms.txt and AGENTS.md, and both files exist."""
    wanted = ("llms.txt", "AGENTS.md")
    lines = [ln for ln in text.splitlines()
             if all(page in [t.split("#", 1)[0].removeprefix("./") for t in _LINK.findall(ln)]
                    for page in wanted)]
    if not lines:
        return ["no line links both llms.txt and AGENTS.md"]
    return [f"the agent line links {page}, which does not exist"
            for page in wanted if not (root / page).is_file()]


class ReadmeFrontDoorTests(unittest.TestCase):
    def test_the_readme_is_at_most_1800_words(self) -> None:
        """AC1: `wc -w README.md` is at most 1,800; a page one word over is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertLessEqual(words(text), MAX_WORDS,
                             f"README.md is {words(text)} words, over {MAX_WORDS}")
        self.assertEqual(words("one  two\tthree\nfour - `five`"), 6)
        self.assertGreater(words(text + " extra" * (MAX_WORDS - words(text) + 1)), MAX_WORDS)

    def test_the_first_section_offers_three_routes_each_to_a_page_that_exists(self) -> None:
        """AC2: evaluate, try, upgrade, in that order, each to the pages that carry it. A route
        cut, two routes swapped, a route's page unlinked or a link to a missing file is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(route_problems(text), [])
        heading, body = first_section(text)
        bullets = {name: next(m.group(0) for m in _BULLET.finditer(body)
                              if opens.search(m.group(1).strip()))
                   for name, opens, _ in ROUTES}
        cut = text.replace(bullets["try"], "", 1)
        self.assertIn("the first section ('%s') offers the try route 0 times, not once" % heading,
                      route_problems(cut))
        swapped = text.replace(bullets["evaluate"], "\0", 1).replace(
            bullets["upgrade"], bullets["evaluate"], 1).replace("\0", bullets["upgrade"], 1)
        self.assertIn("the routes are not in the order evaluate, try, upgrade",
                      route_problems(swapped))
        unlinked = text.replace("(docs/evidence.md)", "(docs/evidence-missing.md)", 1)
        self.assertIn("the evaluate route does not link docs/evidence.md",
                      route_problems(unlinked))
        self.assertIn("the evaluate route links docs/evidence-missing.md, which does not exist",
                      route_problems(unlinked))
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("the try route links docs/INSTALL.md, which does not exist",
                          route_problems(text, Path(d)))
        twice = text.replace(bullets["try"], bullets["try"] + bullets["try"], 1)
        self.assertIn("the first section ('%s') offers the try route 2 times, not once" % heading,
                      route_problems(twice))
        moved = text.replace(f"## {heading}", "## Later", 1).replace(
            "</div>\n", "</div>\n\n## Something else first\n\nText.\n", 1)
        self.assertTrue(any("offers the evaluate route 0 times" in p
                            for p in route_problems(moved)))
        inside = text.replace("</div>\n", f"## {heading}\n{body}\n</div>\n\n## Other\n\nText.\n", 1)
        self.assertTrue(any("offers the evaluate route 0 times" in p
                            for p in route_problems(inside)),
                        "routes inside the badges block counted as the first section after it")

    def test_the_opening_claims_independent_review_and_one_signature_per_run(self) -> None:
        """BG1487 AC1: the opening says each step is reviewed independently and a named person
        signs each run, and never that a person approves each step. The old sentence, the
        signature clause cut, and the review clause cut are each refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(opening_problems(text), [], opening(text))
        para = opening(text)
        old = text.replace("</div>\n", f"</div>\n\n{OLD_OPENING}\n", 1)
        self.assertEqual(opening(old), OLD_OPENING)
        self.assertEqual(opening_problems(old),
                         ["the opening says a person approves each step",
                          "the opening does not say each step is reviewed independently",
                          "the opening does not say a named person signs each run"])
        unsigned = text.replace("</div>\n", "</div>\n\n" + re.sub(
            r"\bsigns\b", "reads", para) + "\n", 1)
        self.assertEqual(opening_problems(unsigned),
                         ["the opening does not say a named person signs each run"])
        for wrong in (para.replace("signs each run", "signs each step", 1),
                      para.replace("a person you name signs", "the tool signs", 1)):
            self.assertNotEqual(wrong, para)
            planted = text.replace("</div>\n", f"</div>\n\n{wrong}\n", 1)
            self.assertEqual(opening_problems(planted),
                             ["the opening does not say a named person signs each run"], wrong)
        unreviewed = text.replace("</div>\n", "</div>\n\n" + re.sub(
            r"\bindependent\w*", "", para) + "\n", 1)
        self.assertEqual(opening_problems(unreviewed),
                         ["the opening does not say each step is reviewed independently"])
        approved = text.replace("</div>\n", "</div>\n\n" + para.replace(
            "each run", "each run and approves each step", 1) + "\n", 1)
        self.assertIn("the opening says a person approves each step", opening_problems(approved))

    def test_one_line_points_agents_at_llms_txt_and_agents_md(self) -> None:
        """BG1487 AC2: one line links llms.txt and AGENTS.md, both of which exist. The line cut
        (AGENTS.md still linked elsewhere), one of its links changed, the two split across lines,
        or a missing file is refused."""
        text = README.read_text(encoding="utf-8")
        self.assertEqual(agent_pointer_problems(text), [])
        line = next(ln for ln in text.splitlines() if "](llms.txt)" in ln and "](AGENTS.md)" in ln)
        cut = text.replace(line, "", 1)
        self.assertIn("](AGENTS.md)", cut)
        self.assertEqual(agent_pointer_problems(cut),
                         ["no line links both llms.txt and AGENTS.md"])
        only_one = text.replace(line, line.replace("](llms.txt)", "](docs/INSTALL.md)"), 1)
        self.assertEqual(agent_pointer_problems(only_one),
                         ["no line links both llms.txt and AGENTS.md"])
        split = text.replace(line, line.replace("[AGENTS.md]", "\n[AGENTS.md]", 1), 1)
        self.assertEqual(agent_pointer_problems(split),
                         ["no line links both llms.txt and AGENTS.md"])
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text("x", encoding="utf-8")
            self.assertEqual(agent_pointer_problems(text, Path(d)),
                             ["the agent line links llms.txt, which does not exist"])


if __name__ == "__main__":
    unittest.main()
