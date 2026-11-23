"""docs/engineering-leaders.md: the page a head of engineering reads before a change board.

It has four sections (change approval, separation of duties, the signed report, cost in dollars
a point), stays short, links every claim in those sections to the script, reference heading or
committed record behind it, and cites the committed report for every dollar figure it states.
Each check runs on the live page and on a planted failure beside it, so a check that has stopped
looking cannot pass.
"""
# test-census-subject: docs/engineering-leaders.md
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "engineering-leaders.md"
REFERENCE = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-scripts-domain.md"
REPORTS = REPO / "sdlc-studio" / "reports"
WORD_LIMIT = 1200

#: Each required section, found by its level-two heading.
SECTIONS = {
    "change approval": re.compile(r"\bchange approval\b", re.I),
    "separation of duties": re.compile(r"\bseparation of duties\b", re.I),
    "the signed report": re.compile(r"\bsigned report\b", re.I),
    "cost in dollars a point": re.compile(r"\bdollars a point\b", re.I),
}
#: The three duties the separation-of-duties section must name.
DUTIES = ("author", "reviewer", "signer")

_H2 = re.compile(r"^##\s+(.*?)\s*$")
_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
_EXPLICIT_ID = re.compile(r"\{#([\w-]+)\}")
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_DOLLARS = re.compile(r"\$\d[\d,]*(?:\.\d+)?")


def sections(text: str) -> list[tuple[str, str]]:
    """Each level-two section as (heading, body), in page order."""
    out: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        m = _H2.match(line)
        if m:
            out.append((m.group(1), []))
        elif line.startswith("# "):
            out.append(("", []))
        elif out:
            out[-1][1].append(line)
    return [(h, "\n".join(body)) for h, body in out if h]


def section_body(text: str, key: str) -> str:
    """The body of the one section whose heading matches `key`, or empty."""
    return "\n".join(b for h, b in sections(text) if SECTIONS[key].search(h))


def missing_sections(text: str) -> list[str]:
    """Each required section the page lacks or repeats, and each duty the duties section omits."""
    problems = []
    headings = [h for h, _ in sections(text)]
    for key, pattern in SECTIONS.items():
        found = [h for h in headings if pattern.search(h)]
        if not found:
            problems.append(f"no section for {key}")
        elif len(found) > 1:
            problems.append(f"{len(found)} sections for {key}")
    duties = section_body(text, "separation of duties").lower()
    if duties:
        problems += [f"separation of duties names no {d}" for d in DUTIES
                     if not re.search(rf"\b{d}s?\b", duties)]
    return problems


def word_count(text: str) -> int:
    """The page's words as `wc -w` counts them."""
    out = subprocess.run(["wc", "-w"], input=text, capture_output=True, text=True, check=True)
    return int(out.stdout.split()[0])


def claims(body: str) -> list[str]:
    """Each paragraph and each list item of a section body; headings are not claims."""
    out: list[str] = []
    for block in re.split(r"\n\s*\n", body):
        lines = [ln for ln in block.splitlines() if ln.strip() and not _HEADING.match(ln)]
        current: list[str] = []
        for line in lines:
            if _ITEM.match(line) and current:
                out.append(" ".join(current))
                current = []
            current.append(line.strip())
        if current:
            out.append(" ".join(current))
    return out


def anchors(path: Path) -> set[str]:
    """The anchors a markdown file's headings render: explicit ids and GitHub slugs."""
    seen: dict[str, int] = {}
    out: set[str] = set()
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else _HEADING.match(line)
        if not m:
            continue
        out.update(_EXPLICIT_ID.findall(m.group(1)))
        base = re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "",
                                          _EXPLICIT_ID.sub("", m.group(1)).strip().lower()))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    return out


def resolve(target: str, page: Path = PAGE) -> tuple[Path | None, str, str]:
    """(resolved file, anchor, problem) for a link `target` written on `page`."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        return None, "", f"{target} is not a file in this repository"
    path_part, _, anchor = target.partition("#")
    resolved = (page.parent / path_part).resolve() if path_part else page.resolve()
    if REPO.resolve() not in resolved.parents:
        return None, anchor, f"{target} resolves outside the repository"
    if not resolved.is_file():
        return None, anchor, f"{target} names no file"
    if anchor and anchor not in anchors(resolved):
        return None, anchor, f"{target} names no heading in {resolved.name}"
    return resolved, anchor, ""


def is_mechanism(resolved: Path, anchor: str) -> bool:
    """A script, a reference page heading, or a committed record under sdlc-studio/."""
    return (resolved.suffix == ".py"
            or (resolved.suffix == ".md" and bool(anchor))
            or (REPO / "sdlc-studio").resolve() in resolved.parents)


def claim_problems(body: str, page: Path = PAGE) -> list[str]:
    """Each claim with no mechanism link, and each link that resolves nowhere."""
    problems = []
    for claim in claims(body):
        mechanisms = 0
        for target in _LINK.findall(claim):
            resolved, anchor, problem = resolve(target, page)
            if problem:
                problems.append(problem)
            elif is_mechanism(resolved, anchor):
                mechanisms += 1
        if not mechanisms:
            problems.append(f"no mechanism linked: {claim[:70]}")
    return problems


def dollar_problems(body: str, page: Path = PAGE) -> list[str]:
    """Each dollar figure whose paragraph links no committed report that holds it."""
    problems = []
    for claim in claims(body):
        figures = _DOLLARS.findall(claim)
        if not figures:
            continue
        reports = []
        for target in _LINK.findall(claim):
            resolved, _, problem = resolve(target, page)
            if not problem and REPORTS.resolve() in resolved.parents:
                reports.append(resolved.read_text(encoding="utf-8"))
        for figure in figures:
            if not reports:
                problems.append(f"{figure} links no report under sdlc-studio/reports/")
            elif not any(figure in text for text in reports):
                problems.append(f"{figure} is in none of the reports its paragraph links")
    return problems


#: A clause that prices each model at its own rate: true of the dollar actual only.
_PER_MODEL = re.compile(r"\bown rate\b|\bper model\b|\bnever priced at one model", re.I)
#: A clause that says the forecast is priced at one model's rate.
_FORECAST_ONE_RATE = re.compile(r"\bforecast\b[^.;]*\bone model's\b[^.;]*\brate\b", re.I)
#: The over-claim that every verdict stamps the author, which older ledger rows do not.
_EVERY_STAMPS = re.compile(r"\bevery\s+(?:\w+\s+)?verdicts?\s+stamps?\b", re.I)
_CLAUSE = re.compile(r"(?<=[.;])\s+")


def clauses(body: str) -> list[str]:
    """Each sentence or semicolon clause of each claim in a section body."""
    return [c for claim in claims(body) for c in _CLAUSE.split(claim) if c.strip()]


def pricing_problems(body: str) -> list[str]:
    """Per-model pricing said of anything but the dollar actual, or a forecast left unpriced."""
    problems = [f"per-model pricing not limited to the dollar actual: {c[:70]}"
                for c in clauses(body) if _PER_MODEL.search(c)
                and (not re.search(r"\bactual\b", c, re.I) or re.search(r"\bforecast", c, re.I))]
    if not any(_FORECAST_ONE_RATE.search(c) for c in clauses(body)):
        problems.append("the forecast is not said to be priced at one model's rate")
    return problems


def refusal_link_problems(body: str) -> list[str]:
    """The evidence pack's refusals linked anywhere but the script that enforces them."""
    problems = []
    named = [c for c in claims(body) if re.search(r"\bpack\b", c, re.I)
             and re.search(r"\brefuses?\b", c, re.I)]
    for claim in named:
        scripts = {Path(t.partition("#")[0]).name for t in _LINK.findall(claim)}
        if "release_cut.py" in scripts:
            problems.append(f"links release_cut.py for the pack's refusals: {claim[:60]}")
        if "evidence_pack.py" not in scripts:
            problems.append(f"does not link evidence_pack.py for the pack's refusals: {claim[:60]}")
    return problems if named else ["names no refusal of the evidence pack"]


#: The three refusals of the pack's signer check (`evidence_pack.principal_refusal`), as the
#: page and the reference word them.
SIGNER_REFUSALS = {
    "a blank principal": re.compile(r"\ba blank principal\b", re.I),
    "one that reads as an agent by name": re.compile(r"\breads as an agent by name\b", re.I),
    "one recorded as an author of the report's own units":
        re.compile(r"\brecord(?:ed|s)? as an author of the report's own units\b", re.I),
}
#: What the check cannot see, and whose the remainder is, in one sentence.
_SIGNER_LIMIT = re.compile(r"\bcannot tell a person from an agent session\b[^.]*"
                           r"\bunder another name\b[^.]*\bthe operator's responsibility\b", re.I)
#: The author refusal's exception: `unit_authors` drops an author typed `human`.
_HUMAN_AUTHOR = re.compile(r"\bunless the ledger records that author as a person\b", re.I)


def reference_entry(text: str, heading: str = "### `evidence_pack.py`") -> str:
    """The body under a reference page's script heading, up to the next heading, or empty."""
    rest = text.partition(f"\n{heading}\n")[2]
    end = re.search(r"^#{1,6} ", rest, re.M)
    return rest[:end.start()] if end else rest


def signer_refusals(body: str) -> set[str]:
    """Each signer refusal stated in a claim that names a refusal."""
    named = [c for c in claims(body) if re.search(r"\brefus", c, re.I)]
    return {name for name, pattern in SIGNER_REFUSALS.items()
            if any(pattern.search(c) for c in named)}


def signer_limit_stated(body: str) -> bool:
    """Whether one sentence says the check cannot tell a person from an agent session signing
    under another name and leaves the named person to the operator."""
    return any(_SIGNER_LIMIT.search(c) for c in claims(body))


def signer_check_problems(body: str) -> list[str]:
    """The signer check stated as more or less than it enforces: a refusal of agents stated
    without saying it reads the name, a refusal or its exception left out, or the limit unsaid."""
    problems = [f"states the agent refusal as absolute: {c[:60]}" for c in clauses(body)
                if re.search(r"\brefus", c, re.I) and re.search(r"\bagents?\b", c, re.I)
                and not re.search(r"\bby name\b", c, re.I)]
    stated = signer_refusals(body)
    problems += [f"does not state the refusal of {name}" for name in SIGNER_REFUSALS
                 if name not in stated]
    if not any(_HUMAN_AUTHOR.search(c) for c in claims(body)):
        problems.append("does not say an author the ledger records as a person is not refused")
    if not signer_limit_stated(body):
        problems.append("does not say the pack cannot tell a person from an agent session "
                        "signing under another name")
    return problems


def author_stamp_problems(body: str) -> list[str]:
    """An author-stamping claim stronger than the verdict writer enforces."""
    problems = []
    for c in clauses(body):
        if _EVERY_STAMPS.search(c):
            problems.append(f"claims every verdict stamps the author: {c[:60]}")
        if re.search(r"\bby name and role\b", c, re.I) and not re.search(r"\bbrief\b", c, re.I):
            problems.append(f"credits name and role to the verdict, not the brief: {c[:60]}")
    if not any(re.search(r"\bauthor\b[^.;]*\breviewer\b", c, re.I) for c in clauses(body)):
        problems.append("no verdict is said to record the author beside the reviewer")
    return problems


SCRIPT = "../.claude/skills/sdlc-studio/scripts/transition.py"
REPORT = "../sdlc-studio/reports/RPT0031-sprint-report-run-01m7e52t.md"


class EngineeringLeadersPageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(PAGE.is_file(), f"{PAGE.relative_to(REPO)} does not exist")
        self.text = PAGE.read_text(encoding="utf-8")

    def test_the_four_sections_are_present_and_the_page_is_short(self) -> None:
        self.assertEqual(missing_sections(self.text), [])
        self.assertLessEqual(word_count(self.text), WORD_LIMIT)
        # Planted failures: each section dropped, a duty unnamed, a section repeated, a long page.
        for key, pattern in SECTIONS.items():
            heading = next(h for h, _ in sections(self.text) if pattern.search(h))
            cut = self.text.replace(f"## {heading}\n", "## Elsewhere\n")
            self.assertIn(f"no section for {key}", missing_sections(cut))
        duties = "## Separation of duties\n\nThe author writes and the reviewer reads.\n"
        self.assertEqual(missing_sections(duties)[-1], "separation of duties names no signer")
        self.assertIn("2 sections for change approval",
                      missing_sections(self.text + "\n## Change approval again\n"))
        self.assertLessEqual(word_count("word " * 1200), WORD_LIMIT)
        self.assertGreater(word_count("word " * 1201), WORD_LIMIT)

    def test_every_claim_links_a_mechanism_that_exists(self) -> None:
        for key in SECTIONS:
            body = section_body(self.text, key)
            self.assertTrue(claims(body), f"the {key} section makes no claim")
            self.assertEqual(claim_problems(body), [], f"in the {key} section")
        # Planted failures beside a positive control.
        self.assertEqual(claim_problems(f"A gate refuses it ([gate]({SCRIPT}))."), [])
        self.assertEqual(claim_problems(f"- One.\n- Two, [linked]({SCRIPT})."),
                         ["no mechanism linked: - One."])
        self.assertIn("no mechanism linked: A gate refuses it.",
                      claim_problems("A gate refuses it."))
        self.assertTrue(claim_problems("See [gone](../scripts/gone.py)."))
        self.assertTrue(claim_problems(
            "See [s](../.claude/skills/sdlc-studio/reference-sprint.md#no-such-heading)."))
        self.assertIn("https://example.com/x.py is not a file in this repository",
                      claim_problems("See [web](https://example.com/x.py)."))
        self.assertTrue(claim_problems("See [readme](../README.md)."))

    def test_every_dollar_figure_cites_its_report(self) -> None:
        body = section_body(self.text, "cost in dollars a point")
        self.assertTrue(_DOLLARS.search(body), "the cost section states no dollar figure")
        self.assertEqual(dollar_problems(body), [])
        # Planted failures beside a positive control.
        self.assertEqual(dollar_problems(f"It cost $2.27 a point ([report]({REPORT}))."), [])
        self.assertEqual(dollar_problems("It cost $2.27 a point."),
                         ["$2.27 links no report under sdlc-studio/reports/"])
        self.assertEqual(dollar_problems(f"It cost $2.27 a point ([script]({SCRIPT}))."),
                         ["$2.27 links no report under sdlc-studio/reports/"])
        self.assertEqual(dollar_problems(f"It cost $9.99 a point ([report]({REPORT}))."),
                         ["$9.99 is in none of the reports its paragraph links"])


class FactualWordingTests(unittest.TestCase):
    """Claims held to what the code does: pricing, where the pack's refusals link, what its
    signer check refuses and cannot see, and author stamping."""

    def setUp(self) -> None:
        self.text = PAGE.read_text(encoding="utf-8")

    def test_per_model_pricing_is_limited_to_the_dollar_actual(self) -> None:
        self.assertEqual(pricing_problems(section_body(self.text, "cost in dollars a point")), [])
        # Planted failures beside a positive control.
        good = ("The dollar actual prices each model at its own rate. The forecast is priced at "
                "one model's input rate.")
        self.assertEqual(pricing_problems(good), [])
        both = ("Each model is priced at its own rate, so a run that mixes models is never priced "
                "at one model's rate. The forecast is priced at one model's input rate.")
        self.assertEqual(len(pricing_problems(both)), 1)
        self.assertIn("the forecast is not said to be priced at one model's rate",
                      pricing_problems("The dollar actual prices each model at its own rate."))
        self.assertTrue(pricing_problems("The forecast and the actual are each priced per model; "
                                         "the forecast is priced at one model's rate."))

    def test_the_packs_refusals_link_evidence_pack_py(self) -> None:
        self.assertEqual(refusal_link_problems(section_body(self.text, "change approval")), [])
        # Planted failures beside a positive control.
        script = "../.claude/skills/sdlc-studio/scripts/{}"
        good = f"The pack refuses a report nobody signed ([e]({script.format('evidence_pack.py')}))."
        self.assertEqual(refusal_link_problems(good), [])
        cut = good.replace("evidence_pack.py", "release_cut.py")
        self.assertEqual(len(refusal_link_problems(cut)), 2)
        self.assertEqual(refusal_link_problems("The pack lists each change."),
                         ["names no refusal of the evidence pack"])

    GOOD_SIGNER = ("The pack refuses a blank principal, one that reads as an agent by name, and one "
                   "the review ledgers record as an author of the report's own units, unless the "
                   "ledger records that author as a person. It cannot tell a person from an agent "
                   "session signing under another name, so the person it names is the operator's "
                   "responsibility.")
    LIMIT_MISSING = ("does not say the pack cannot tell a person from an agent session signing "
                     "under another name")

    def test_the_agent_refusal_is_not_stated_as_absolute(self) -> None:
        self.assertEqual(signer_check_problems(section_body(self.text, "change approval")), [])
        # Planted failures beside a positive control.
        good = self.GOOD_SIGNER
        self.assertEqual(signer_check_problems(good), [])
        old = ("The pack refuses a report nobody has signed, and it refuses to name an agent as the "
               "accountable\nperson.")
        found = signer_check_problems(old)
        self.assertTrue(found[0].startswith("states the agent refusal as absolute"), found)
        self.assertEqual(len(found), 6, found)
        self.assertEqual(signer_check_problems(good + " It refuses agents."),
                         ["states the agent refusal as absolute: It refuses agents."])
        # Not a refusal of agents: one that says it reads the name, one of something else, and
        # an agent named in a sentence that refuses nothing.
        for said in (" It refuses as accountable any signer that reads as an agent by name.",
                     " It refuses an unsigned report.", " No agent is the accountable person."):
            with self.subTest(said=said):
                self.assertEqual(signer_check_problems(good + said), [])
        self.assertEqual(signer_check_problems(good.replace("unless the ledger", "if the ledger")),
                         ["does not say an author the ledger records as a person is not refused"])
        for name, (said, cut) in {
                "a blank principal": ("a blank principal", "a principal"),
                "one that reads as an agent by name": ("reads as an agent by name", "is odd"),
                "one recorded as an author of the report's own units":
                    ("record as an author", "record as a reviewer")}.items():
            with self.subTest(dropped=name):
                self.assertEqual(signer_check_problems(good.replace(said, cut)),
                                 [f"does not state the refusal of {name}"])
        for said in ("cannot tell", "another name", "the operator's responsibility"):
            with self.subTest(limit=said):
                self.assertEqual(signer_check_problems(good.replace(said, "x")),
                                 [self.LIMIT_MISSING])
        # The limit across two sentences is not stated: the remainder must be the operator's.
        self.assertEqual(signer_check_problems(good.replace("name, so", "name. So")),
                         [self.LIMIT_MISSING])
        # A refusal stated in a claim that says the pack refuses nothing does not count.
        self.assertEqual(signer_refusals("The pack names a blank principal.\n\n" + good.replace(
            "a blank principal, ", "")), set(SIGNER_REFUSALS) - {"a blank principal"})

    def test_the_reference_states_the_same_refusals_and_limit(self) -> None:
        entry = reference_entry(REFERENCE.read_text(encoding="utf-8"))
        self.assertIn("evidence pack", entry, "the reference has no evidence_pack.py entry")
        self.assertEqual(signer_check_problems(entry), [])
        page = section_body(self.text, "change approval")
        self.assertEqual(signer_refusals(entry), signer_refusals(page))
        self.assertEqual(signer_limit_stated(entry), signer_limit_stated(page))
        # Planted failures beside a positive control.
        old = ("It reads the committed copies, so an uncommitted edit never changes the pack, and "
               "it refuses an unsigned report or an agent named as accountable.")
        self.assertTrue(signer_check_problems(old)[0].startswith(
            "states the agent refusal as absolute"))
        two = self.GOOD_SIGNER.replace("a blank principal, ", "")
        self.assertNotEqual(signer_refusals(two), signer_refusals(self.GOOD_SIGNER))
        self.assertNotEqual(signer_limit_stated(two.replace("cannot tell", "x")),
                            signer_limit_stated(self.GOOD_SIGNER))
        heading = "### `evidence_pack.py`"
        self.assertEqual(reference_entry(f"# P\n\n{heading}\n\nA.\n\n### `flow.py`\n\nB.\n"),
                         "\nA.\n\n")
        self.assertEqual(reference_entry(f"# P\n\n{heading}\n\nA.\n"), "\nA.\n")
        self.assertEqual(reference_entry("Intro.\n\n### `flow.py`\n\nB.\n"), "")

    def test_author_stamping_claims_no_more_than_the_writer_enforces(self) -> None:
        self.assertEqual(author_stamp_problems(section_body(self.text, "separation of duties")), [])
        # Planted failures beside a positive control.
        good = ("A review verdict records the author beside the reviewer, and the review brief "
                "asks for both by name and role.")
        self.assertEqual(author_stamp_problems(good), [])
        self.assertTrue(author_stamp_problems(
            "Every review verdict stamps the author beside the reviewer, by name and role."))
        self.assertTrue(author_stamp_problems("Every verdict stamps the author beside the reviewer."))
        self.assertTrue(author_stamp_problems(
            "A verdict records the author beside the reviewer, by name and role."))
        self.assertEqual(author_stamp_problems("The review brief asks for both by name and role."),
                         ["no verdict is said to record the author beside the reviewer"])


if __name__ == "__main__":
    unittest.main()
