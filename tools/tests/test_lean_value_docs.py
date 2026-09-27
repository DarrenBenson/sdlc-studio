"""US0957: the white paper and the value argument describe the v6 operating model.

A team lead takes these two documents to their team before anyone installs the skill, so a
retired gate described here as current is the first thing that team learns wrongly. The retired
surface is IMPORTED from US0924's `retired_surface` module, never restated. Three phrasings these
long-form pages used for gates v6 deleted are added below, because no shipped help page used them:
depth tiers as a gate, an attestation ledger of sign-offs, and the plan's independent review.

A passage under a heading saying what was removed in v6 is where the retired gates are named as
history, so it is blanked before the scan. The ratchet section's figures are read from their
sources where a source can be counted, so the paper cannot drift from them.
"""
# test-census-subject: docs/whitepaper.md
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"))
import retired_surface  # noqa: E402

PAPER = REPO / "docs" / "whitepaper.md"
WHY = REPO / "docs" / "why-sdlc-studio.md"
PLAN_REVIEWS = REPO / "sdlc-studio" / "reviews" / "plan-review-verdicts.md"
BACK_TO_BASICS = REPO / "sdlc-studio" / "reviews" / "back-to-basics-review.md"

#: The long-form phrasings of gates v6 deleted, beside the shared list.
LONG_FORM = {
    "depth tiers as a gate":
        r"(?i)\bverification[- ]depth\b|\bdepth[- ](?:tiers?|gated)\b|\brecorded depth\b",
    "an attestation ledger of sign-offs":
        r"(?i)\battestation (?:ledger|log|record)\b|\bsign-?off (?:ledger|record|rows?)\b",
    "the plan's independent review":
        r"(?i)\bindependent (?:review|check) of the plan\b|\bplan (?:itself )?gets an "
        r"independent review\b|\bplan's independent review\b",
}

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def patterns() -> dict[str, re.Pattern]:
    return {**retired_surface.surfaces(),
            **{label: re.compile(rx) for label, rx in LONG_FORM.items()}}


def outside_removed(text: str) -> str:
    """`text` with each passage under a heading naming what was 'removed in v6' blanked, down to
    the next heading at the same or a higher level. Lines are blanked, not dropped, so a reported
    line number is the line a reader opens."""
    out, level = [], 0
    for line in text.splitlines():
        m = _HEADING.match(line)
        if m and level and len(m.group(1)) <= level:
            level = 0
        if m and not level and re.search(r"(?i)\bremoved in v6\b", m.group(2)):
            level = len(m.group(1))
        out.append("" if level else line)
    return "\n".join(out) + "\n"


def live(text: str) -> list[tuple[int, str, str]]:
    return retired_surface.live_mentions(outside_removed(text), patterns())


def section(text: str, heading_rx: str) -> str:
    m = re.search(rf"^## [^\n]*{heading_rx}[^\n]*\n(.*?)(?=^## |\Z)", text,
                  re.M | re.S | re.I)
    if not m:
        raise AssertionError(f"no '## ...{heading_rx}...' section")
    return m.group(1)


def plan_review_counts() -> tuple[int, int]:
    """(REJECT rows, all rows) of the frozen plan-review ledger."""
    rows = [ln.split("|")[2].strip() for ln in PLAN_REVIEWS.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| ") and not ln.startswith(("| Unit", "| ---"))]
    return rows.count("REJECT"), len(rows)


def inventory_size() -> int:
    """The entry count the CHANGELOG's 6.0.0 Breaking inventory states."""
    m = re.search(r"(\d+) entries: \d+ verbs", (REPO / "CHANGELOG.md").read_text(encoding="utf-8"))
    if not m:
        raise AssertionError("CHANGELOG.md states no Breaking inventory count")
    return int(m.group(1))


def paragraph_with(text: str, *needles: str) -> str | None:
    for para in re.split(r"\n\s*\n", text):
        flat = " ".join(para.split())
        if all(n in flat for n in needles):
            return flat
    return None


class ValueDocsTests(unittest.TestCase):

    def test_the_value_docs_teach_no_retired_surface(self) -> None:
        """AC1. MUTANTS: HEAD's whitepaper (depth tiers recording how a fix was verified, the
        plan's independent review gate) and why page (verification-depth tiers, an attestation
        record, a depth tier per unit); the long-form list dropped; the removed-in-v6 passage
        un-blanked."""
        pats = patterns()
        # Controls: each long-form phrasing HEAD used is caught, and a removal clause excuses it.
        for leak in ("depth tiers record how a fix was verified",
                     "verification-depth tiers apply to any writer",
                     "the critic-verdict record is an attestation log",
                     "which is why the plan itself gets an independent review gate",
                     "an independent check of the plan against the spec"):
            self.assertTrue(retired_surface.live_mentions(leak, pats), leak)
        self.assertFalse(retired_surface.live_mentions(
            "The verification-depth field was removed in v6.", pats))
        self.assertTrue(live("## Evidence\n\nDepth tiers record how a fix was verified.\n"))
        self.assertFalse(live("## 11. What was removed in v6\n\nDepth tiers recorded it.\n"
                              "\n## 12. Next\n\nNothing.\n"))
        found = [f"{path.name}:{n}: [{label}] {line.strip()[:120]}"
                 for path in (PAPER, WHY)
                 for n, label, line in live(path.read_text(encoding="utf-8"))]
        self.assertEqual(found, [], "a value doc teaches a surface v6 retired:\n"
                         + "\n".join(found))

    def test_the_whitepaper_is_v6_and_carries_the_ratchet(self) -> None:
        """AC2. MUTANTS: HEAD's 'v4.0 · July 2026' line; a v6 line with the register still
        citing depth-gated closes; a ratchet figure with no source, or one its source does not
        hold."""
        text = PAPER.read_text(encoding="utf-8")
        version = re.search(r"^\*\*An SDLC Studio white paper · (v[\d.]+) · ([^*]+)\*\*$",
                            text, re.M)
        self.assertIsNotNone(version, "the white paper has no version line")
        self.assertRegex(version.group(1), r"^v6(?:\.|$)")
        self.assertNotRegex(text, r"(?i)v6(?:\.0){0,2} (?:is|was) released",
                            "the paper must not claim v6.0.0 is released")

        ratchet = section(text, "ratchet")
        # 82% of the last 116 units: the back-to-basics review's figure, still stated there.
        self.assertIn("82% of the last 116", BACK_TO_BASICS.read_text(encoding="utf-8"))
        self.assertIsNotNone(paragraph_with(ratchet, "82%", "116", "back-to-basics-review.md"),
                             "the 82% of 116 figure does not name its source")
        # Plan review: counted from the frozen ledger, never typed from memory.
        rejects, total = plan_review_counts()
        self.assertIsNotNone(paragraph_with(ratchet, f"{rejects} of {total}",
                                            f"{round(100 * rejects / total)}%",
                                            "plan-review-verdicts.md"),
                             "the plan-review figure does not match or name its ledger")
        # What was deleted: the inventory's own count, beside the CHANGELOG.
        self.assertIsNotNone(paragraph_with(ratchet, f"{inventory_size()} ", "CHANGELOG.md"),
                             "the deleted surface is not counted from the CHANGELOG inventory")

        register = section(text, "claims register")
        rows = [ln for ln in register.splitlines() if ln.startswith("| ")]
        self.assertTrue(rows, "the claims register has no rows")
        stale = [f"{label}: {line[:100]}"
                 for n, label, line in retired_surface.live_mentions("\n".join(rows), patterns())]
        self.assertEqual(stale, [], "the claims register has a row for a deleted gate")
        self.assertFalse([r for r in rows if re.search(r"(?i)depth-gated|attestation", r)])


if __name__ == "__main__":
    unittest.main()
