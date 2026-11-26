"""US1339: the person owns the PRD and the PVD; a seat checks the work under delegated authority.

The skill said the Product Owner seat owns the PRD and the Product Manager seat owns the PVD,
while the explainer and the website said the person in each role owns each document. Every
shipped page now names the person as owner and the seat as the delegate that checks the work
against the document and signs its review leg. Each page is normalised before it is matched
(blockquote marks and bold stripped, lines joined), because a line-by-line grep passes the PVD
page's old sentence, which was split across a line break and bold.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/reference-workflow-personas.md
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
sys.path.insert(0, str(REPO / "tools"))

import check_links  # noqa: E402

PRD_PAGE = SKILL / "reference-prd.md"
PVD_PAGE = SKILL / "reference-pvd.md"
PVD_HELP = SKILL / "help" / "pvd.md"
REVIEW_PAGE = SKILL / "reference-review.md"
PERSONAS_PAGE = SKILL / "reference-workflow-personas.md"

#: A seat, named by role, by its abbreviation or generically, as the subject or agent of ownership.
_SEAT = r"(?:Product (?:Owner|Manager)|PO|PM|seat|persona)"
#: A seat or a persona named as a document's owner.
OWNER_PATTERNS = {
    "a seat owns": re.compile(rf"\b{_SEAT}(?: (?:seat|persona))?\s+owns\b", re.I),
    "owned by a seat": re.compile(rf"\bowned by (?:the |a )?{_SEAT}\b", re.I),
}
#: A seat called a document owner.
DOC_OWNER_PATTERNS = {
    "document owner": re.compile(r"\bdocument[- ]owners?\b", re.I),
    "PO/PM owners": re.compile(r"\bPO/PM owners?\b"),
}
ALL_PATTERNS = {**OWNER_PATTERNS, **DOC_OWNER_PATTERNS}
#: A table column headed by ownership, in any wording ("Owns", "Owns (the document)", "Owner").
OWNS_HEADER = re.compile(r"\bown(?:s|ed|ers?)?\b", re.I)

#: The old wording, in the shapes HEAD carried it: split across a line and bold, and plain.
PLANTED = (
    "> The PRD is owned by\n> the **Product Owner** seat. The **Product Manager** seat owns\n"
    "> this, the product manager owns it, each seat owns one, a page owned by a Persona, a\n"
    "> Document-owner seat, a document owner, the PM owns it, a page owned by the PO, and PO/PM\n"
    "> owners review it."
)
#: Every match the planted paragraph holds, pattern by pattern.
PLANTED_HITS = 10
#: A leg that names its seat signing and, in another sentence, delegation.
NEAR_MISS_LEG = "The Product Owner seat signs it. The person delegates the review."
COMPLIANT = "The person owns the PRD; the Product Owner seat signs its review leg"


def normalise(text: str) -> str:
    """Strip blockquote marks and bold, and join the lines into one."""
    lines = [re.sub(r"^\s*(?:>\s?)+", "", line) for line in text.splitlines()]
    return re.sub(r"\s+", " ", " ".join(lines).replace("**", ""))


def sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+", normalise(text))


def signed(leg: str, seat: str) -> list[str]:
    """The sentences that say `seat` signs the verdict under delegated authority."""
    return [s for s in sentences(leg)
            if re.search(rf"\b{seat} seat signs\b", s) and "delegat" in s]


#: What the seats section's delegate sentence says, every part in the one sentence.
DELEGATE_WORDS = ("accountable", "delegat", "check", "signs", "review leg", "asks the person",
                  "unsure")


def delegate_rule(text: str) -> list[str]:
    """The sentences that make a seat the person's delegate for checking its document."""
    return [s for s in sentences(text) if all(w in s for w in DELEGATE_WORDS)]


def corpus() -> list[Path]:
    return sorted(SKILL.rglob("*.md"))


def hits(text: str, patterns: dict[str, re.Pattern[str]]) -> list[str]:
    flat = normalise(text)
    return [f"{name}: {m.group(0)!r}" for name, rx in patterns.items() for m in rx.finditer(flat)]


def section(text: str, start: str, ends: tuple[str, ...]) -> str:
    i = text.index(start)
    stops = [j for j in (text.find(e, i + len(start)) for e in ends) if j != -1]
    return text[i:min(stops) if stops else len(text)]


def seats_section(text: str) -> tuple[str, str]:
    """The heading and body of the `###` section that holds the Product Owner seat's row."""
    row = text.index("| **Product Owner** |")
    start = text.rindex("\n### ", 0, row) + 1
    end = min(j for j in (text.find("\n### ", row), text.find("\n## ", row), len(text)) if j != -1)
    heading, _, body = text[start:end].partition("\n")
    return heading, body


def anchors(path: Path) -> set[str]:
    """The explicit `{#id}` anchors and the implicit heading slugs `path` defines."""
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        out.update(re.findall(r"\{#([\w-]+)\}", line))
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            out.add(check_links.slug(m.group(1)))
    return out


class OwnershipWordingTests(unittest.TestCase):
    def test_no_page_says_a_seat_owns_the_prd_or_the_pvd(self) -> None:
        """AC1. MUTANT: HEAD's 'The PRD is owned by the Product Owner seat', its PVD sentence
        split across a line and bold, and help's '(Product Manager owns it)'."""
        for page in (PRD_PAGE, PVD_PAGE, PVD_HELP):
            found = hits(page.read_text(encoding="utf-8"), OWNER_PATTERNS)
            self.assertEqual(found, [], f"{page.name} says a seat owns its document")
        for page, doc in ((PRD_PAGE, "PRD"), (PVD_PAGE, "PVD")):
            flat = normalise(page.read_text(encoding="utf-8"))
            self.assertRegex(flat, rf"\b[Tt]he person owns the {doc}\b",
                             f"{page.name} does not say the person owns the {doc}")

    def test_the_review_legs_say_the_seat_signs_under_delegated_authority(self) -> None:
        """AC2. MUTANT: HEAD's 'The Product Manager seat owns this' and 'The Product Owner seat
        owns this', with no 'delegat' in either leg."""
        text = REVIEW_PAGE.read_text(encoding="utf-8")
        legs = (
            ("#### PVD Review", "Product Manager"),
            ("#### PRD Review", "Product Owner"),
        )
        # The PRD leg keeps its completion condition, the one the PRD page states.
        prd_leg = section(text, "#### PRD Review", ("\n#### ", "\n### "))
        for name, body in (("the PRD leg", prd_leg), (PRD_PAGE.name, PRD_PAGE.read_text("utf-8"))):
            done = [s for s in sentences(body) if "not complete until" in s]
            self.assertTrue(done, f"{name} states no completion condition")
            self.assertRegex(done[0], r"\bconfirmed met\b", name)
            self.assertRegex(done[0], r"\bgaps are named and tracked\b", name)
        for heading, seat in legs:
            leg = section(text, heading, ("\n#### ", "\n### "))
            self.assertEqual(hits(leg, OWNER_PATTERNS), [], f"{heading} says a seat owns it")
            self.assertTrue(signed(leg, seat), f"{heading}: no sentence says the {seat} seat signs the "
                                    "verdict under authority the person delegates")

    def test_the_seats_section_names_the_person_as_owner_and_the_seat_as_delegate(self) -> None:
        """AC3. MUTANT: HEAD's '### Document-owner seats' heading, its 'Owns' column, and a
        section with no 'delegat', no 'unsure' and no sentence naming the person as owner."""
        heading, body = seats_section(PERSONAS_PAGE.read_text(encoding="utf-8"))
        self.assertNotRegex(heading, re.compile(r"owner|owns", re.I))
        header = next(line for line in body.splitlines() if line.startswith("|"))
        cells = [c.strip() for c in header.strip("|").split("|")]
        self.assertEqual([c for c in cells if OWNS_HEADER.search(c)], [], "a column is headed Owns")
        said = sentences(body)
        owner = [s for s in said if re.search(r"\bperson owns every document\b", s)]
        self.assertTrue(owner, "no sentence says the person owns every document")
        for doc in ("PRD", "PVD", "TRD", "TSD", "personas"):
            self.assertRegex(owner[0], rf"\b{doc}\b", f"the owner sentence leaves out {doc}")
        self.assertTrue(delegate_rule(body), "no sentence says each seat checks the work, signs "
                        "its review leg under authority the person delegates and asks when unsure")

    def test_no_shipped_page_calls_a_seat_a_document_owner(self) -> None:
        """AC4. MUTANT: HEAD's 'document-owner' and 'document owner' in the personas page, the
        PRD, PVD and persona pages and both seat templates, 'PO/PM owners' in the persona page,
        and the links into '#document-owner-seats' once the heading is renamed."""
        found = []
        for page in corpus():
            for hit in hits(page.read_text(encoding="utf-8"), ALL_PATTERNS):
                found.append(f"{page.relative_to(SKILL)}: {hit}")
        self.assertEqual(found, [])
        defined = anchors(PERSONAS_PAGE)
        links = [(page, a) for page in corpus() for a in re.findall(
            r"reference-workflow-personas\.md#([\w-]+)", page.read_text(encoding="utf-8"))]
        self.assertTrue(links, "no page links into the seats section")
        dangling = [f"{p.relative_to(SKILL)}#{a}" for p, a in links if a not in defined]
        self.assertEqual(dangling, [])

    def test_the_patterns_fail_on_a_planted_owner_sentence(self) -> None:
        """AC5. MUTANT: a pattern that has stopped matching, a normaliser that no longer joins
        the split sentence, and an empty corpus would all pass the four tests above."""
        for name, rx in ALL_PATTERNS.items():
            self.assertRegex(normalise(PLANTED), rx, f"{name} misses the planted sentence")
            self.assertNotRegex(normalise(COMPLIANT), rx, f"{name} matches the compliant one")
        # The split sentence is caught only once the page is normalised.
        raw = [m.group(0) for m in OWNER_PATTERNS["owned by a seat"].finditer(PLANTED)]
        self.assertEqual(raw, ["owned by a Persona", "owned by the PO"])
        self.assertEqual(len(hits(PLANTED, ALL_PATTERNS)), PLANTED_HITS)
        # A column headed by ownership is caught in any wording; the section's own are not.
        for heading in ("Owns", "Owns (the document)", "Owner", "owned by"):
            self.assertRegex(heading, OWNS_HEADER)
        for heading in ("Seat", "Checks the work against", "Accountable for", "Applies"):
            self.assertNotRegex(heading, OWNS_HEADER)
        # A seat signing in one sentence and delegation in another is not the rule.
        self.assertEqual(signed(NEAR_MISS_LEG, "Product Owner"), [])
        self.assertTrue(signed(NEAR_MISS_LEG.replace(". The person", ", as the person"),
                               "Product Owner"))
        self.assertEqual(signed("The Product Owner seat owns it, as the person delegates.",
                                "Product Owner"), [])
        rule = ("Each seat is accountable, with authority the person delegates, for checking "
                "it: it signs its review leg and asks the person when unsure.")
        self.assertTrue(delegate_rule(rule))
        self.assertEqual(delegate_rule(rule.replace(": it signs", ". It signs")), [])
        # Each part, taken out, fails the rule: a word dropped from DELEGATE_WORDS is caught.
        for part in ("accountable", "delegates", "checking", "signs", "review leg",
                     "asks the person", "unsure"):
            self.assertEqual(delegate_rule(rule.replace(part, "")), [], part)
        self.assertGreater(len(corpus()), 100)
        for page in (PRD_PAGE, PVD_PAGE, PVD_HELP, REVIEW_PAGE, PERSONAS_PAGE):
            self.assertIn(page, corpus())


if __name__ == "__main__":
    unittest.main()
