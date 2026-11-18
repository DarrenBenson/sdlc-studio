"""`docs/evidence.md` is this repository's signed reports of record, generated and explained.

The table between the markers is written by `sprint_report.py evidence`, so a hand-edited cell
is caught by its `--check`. The text around it is hand-written, and has to say what a partial
verdict means, how the wait for a signature is measured, and how to regenerate the page, with
every link landing on a file and heading that exist (`check_links.py` does not scan the file
links of `docs/` pages, so this test does it for this page).
"""
# test-census-subject: docs/evidence.md

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
import check_links  # noqa: E402

PAGE = REPO / "docs" / "evidence.md"
SPRINT_REPORT = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "sprint_report.py"
BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
REGENERATE = "sprint_report.py evidence --out docs/evidence.md"
#: The newest report the page must cover at least: run sixteen's, the newest signed when the
#: page gained its Model column. A later regeneration moves the page past it and keeps this
#: test green.
COVERS_AT_LEAST = "RPT0035"
#: The change request that adds the harness to the report, which the page names as the gap.
HARNESS_CR = "CR0743"


def _parts() -> tuple[str, str]:
    """`(hand-written text, generated region)` of the committed page."""
    text = PAGE.read_text(encoding="utf-8")
    start, end = text.index(BEGIN), text.index(END)
    return text[:start] + text[end + len(END):], text[start + len(BEGIN):end]


def _sections(hand: str) -> dict[str, str]:
    """`{level-two heading: its body}` of the hand-written text."""
    out, heading = {}, None
    for line in hand.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            out[heading] = ""
        elif heading is not None:
            out[heading] += line + "\n"
    return out


def _anchors(path: Path) -> set[str]:
    """The heading anchors of `path`, outside fenced code."""
    out, fenced = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m and not fenced:
            out.add(check_links.slug(m.group(1)))
            out.update(re.findall(r"\{#([\w-]+)\}", m.group(1)))
    return out


class CommittedEvidencePageTests(unittest.TestCase):
    def test_the_committed_page_matches_the_reports(self) -> None:
        run = subprocess.run(
            [sys.executable, str(SPRINT_REPORT), "--root", str(REPO), "evidence", "--out",
             "docs/evidence.md", "--check"], capture_output=True, text=True, timeout=120,
            check=False)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        _, region = _parts()
        rows = [ln for ln in region.splitlines() if re.match(r"\| RUN-", ln)]
        self.assertGreater(len(rows), 0, "the page carries no generated table")
        named = {ln.split("|")[2].strip() for ln in rows}
        signed = {}
        for rid in named:
            rep = json.loads((REPO / "sdlc-studio" / "reports" / f"{rid}.json")
                             .read_text(encoding="utf-8"))
            signed[rid] = rep["signature"]["signed_at"]
        newest = max(named, key=lambda rid: (signed[rid], rid))
        self.assertIn(f"The newest report this page covers is {newest}, signed at "
                      f"{signed[newest]}.", region)
        self.assertGreaterEqual(int(newest[3:]), int(COVERS_AT_LEAST[3:]),
                                f"the page stops at {newest}; regenerate it with {REGENERATE}")

    def test_the_page_states_the_reports_record_no_harness(self) -> None:
        """The table shows the model each run's report priced but not the harness it ran in,
        because no report records one yet; the hand-written text says so and names the change
        request that adds it."""
        hand, region = _parts()
        self.assertIn("| Model |", region, "the generated table carries no Model column")
        sentences = re.split(r"(?<=[.!?])\s+", " ".join(hand.split()))
        gap = [s for s in sentences if "harness" in s.lower()]
        self.assertTrue(any(HARNESS_CR in s and re.search(r"\bnot\b", s) for s in gap),
                        f"no sentence outside the markers says the reports do not record the "
                        f"harness and names {HARNESS_CR}: {gap}")

    def test_the_page_explains_partial_verdicts_waiting_and_regeneration(self) -> None:
        hand, _ = _parts()
        sections = _sections(hand)

        def section(word: str) -> str:
            found = [body for head, body in sections.items() if word in head.lower()]
            self.assertEqual(1, len(found), f"one section whose heading names {word!r}")
            return found[0]

        partial, wait, regen = section("partial"), section("wait"), section("regenerat")
        self.assertIn("Judged partial", partial)
        self.assertIn("goal_verdict_note", partial, "where a partial verdict's reason comes from")
        self.assertIn("generated_at", wait)
        self.assertIn("signature.signed_at", wait)
        self.assertIn(REGENERATE, regen)
        links = re.findall(r"\]\(([^)\s]+)\)", partial + wait + regen)
        self.assertGreaterEqual(len(links), 3, "the explanation links to where each rule lives")
        for link in links:
            with self.subTest(link=link):
                self.assertFalse(link.startswith(("http:", "https:")), "a link this test cannot check")
                target, _, anchor = link.partition("#")
                path = (PAGE.parent / target).resolve() if target else PAGE
                self.assertTrue(path.is_file(), f"{link} names no file")
                if anchor:
                    self.assertIn(anchor, _anchors(path), f"{link} names no heading")


if __name__ == "__main__":
    unittest.main()
