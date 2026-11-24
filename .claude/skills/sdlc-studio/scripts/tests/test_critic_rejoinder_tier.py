"""BG0975: `critic.py brief --rejoinder` with no `--tier` derived the tier from the unit's risk
band alone, so a re-review of a REJECT recorded at the full tier on a light-band unit was briefed
light, without the claim inventory the REJECT was found with. The rejoinder now takes the tier
the seat's standing REJECT was recorded at when that is the deeper, names that REJECT as the
tier's source, and carries the tier into the record command; an explicit `--tier` is kept as
chosen, and a REJECT no deeper than the band changes nothing.

Each brief is driven through `critic.py`'s entry point in a throwaway project; the deeper-band
case calls the tier's reader in-process, because it needs a band no small fixture reaches.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")
UNIT = "US0101"
REVIEWER = "qa-seat"
DERIVED = "(derived from the unit's risk band)"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path) -> None:
    """A unit that bands LOW (one doc file, one criterion), so its tier derives light."""
    _write(root, "docs/note.md", "a note\n")
    _write(root, "sdlc-studio/personas/seats/qa.md",
           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
           "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
    _write(root, f"sdlc-studio/stories/{UNIT}-note.md",
           f"# {UNIT}: note\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
           f"> **Affects:** docs/note.md\n\n## Acceptance Criteria\n\n### AC1: noted\n"
           "- **Verify:** shell true\n")


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _reject(root: Path, *tier: str) -> None:
    r = _cli(root, "record", "--unit", UNIT, "--verdict", "reject", "--reviewer", REVIEWER,
             "--author", "eng-seat", "--issues", "[new] the note is wrong", *tier)
    assert r.returncode == 0, r.stderr


def _tier_line(stderr: str) -> str:
    found = re.findall(r"^review tier: .*$", stderr, re.M)
    assert len(found) == 1, stderr
    return found[0]


class RejoinderTierTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _project(self.root)
        self.assertEqual("light", critic.tier_for(self.root, UNIT), "premise: a light band")
        self.prior = self.root / "prior.txt"
        self.prior.write_text("VERDICT: REJECT\nISSUES: [new] the note is wrong\n"
                              "BLOCKING: the note is wrong\n", encoding="utf-8")

    def _rejoinder(self, *args: str) -> subprocess.CompletedProcess:
        r = _cli(self.root, "brief", "--unit", UNIT, "--seat", "qa", "--rejoinder", *args)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("RE-REVIEW (rejoinder)", r.stdout)
        return r

    def _inherits_full(self, r: subprocess.CompletedProcess) -> None:
        line = _tier_line(r.stderr)
        self.assertTrue(line.startswith("review tier: full ("), line)
        self.assertIn(f"{REVIEWER}'s REJECT of {UNIT}", line, "the source REJECT is not named")
        self.assertNotIn(DERIVED, line)
        record = next(ln for ln in r.stderr.splitlines() if "critic.py record" in ln)
        self.assertIn("--tier full", record)
        self.assertNotIn("--tier-explicit", record, "an inherited tier is not this brief's choice")
        self.assertIn("CLAIM INVENTORY", r.stdout, "the brief is not the full tier's")

    def test_a_rejoinder_from_a_verdict_file_inherits_the_full_tier(self) -> None:
        """AC1. Mutants: the rejoinder's tier read from the band alone; the footer naming the
        band as the source of an inherited tier."""
        _reject(self.root, "--tier", "full", "--tier-explicit")
        self._inherits_full(self._rejoinder(str(self.prior)))

    def test_a_rejoinder_from_the_ledger_inherits_the_full_tier(self) -> None:
        """AC2: the prior verdict quoted from the ledger takes the same tier."""
        _reject(self.root, "--tier", "full", "--tier-explicit")
        self._inherits_full(self._rejoinder())

    def test_an_explicit_tier_and_a_light_round_are_kept(self) -> None:
        """AC3, the controls. Mutants: the inherited tier overriding an explicit `--tier`; every
        rejoinder forced to full; a REJECT as deep as the band named as the tier's source."""
        _reject(self.root, "--tier", "full", "--tier-explicit")
        r = self._rejoinder(str(self.prior), "--tier", "light")
        self.assertEqual("review tier: light (chosen)", _tier_line(r.stderr))
        self.assertNotIn("CLAIM INVENTORY", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            self.root = Path(d)
            _project(self.root)
            _reject(self.root, "--tier", "light")
            r = self._rejoinder(str(self.prior))
            self.assertEqual(f"review tier: light {DERIVED}", _tier_line(r.stderr))

    def test_a_rejoinder_with_no_tiered_reject_to_read_derives_the_tier(self) -> None:
        """No REJECT in the ledger to read, and a REJECT recorded with no tier, each leave the
        band's tier. Mutants: no standing REJECT refusing the brief instead of falling back; a
        tier cell of `-` read as a tier."""
        r = self._rejoinder(str(self.prior))
        self.assertEqual(f"review tier: light {DERIVED}", _tier_line(r.stderr))
        _reject(self.root)
        self.assertEqual("-", critic.read_verdicts(self.root)[-1]["tier"], "premise: no tier")
        r = self._rejoinder(str(self.prior))
        self.assertEqual(f"review tier: light {DERIVED}", _tier_line(r.stderr))

    def test_the_tier_is_read_from_the_briefed_seats_own_reject(self) -> None:
        """The tier a rejoinder inherits is the briefed seat's own REJECT's, never another
        seat's: an engineering rejoinder on a unit where only the qa seat holds a full REJECT
        stays at the band's tier, and one answering the engineering seat's own full REJECT,
        with no qa REJECT standing, is briefed full naming it. Mutant: the REJECT read for a
        fixed seat (`qa`) whichever seat is briefed."""
        engineering = ("<!-- role: engineering -->\n# Dani - Engineering amigo\n\ncharter\n\n"
                       "## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
        _write(self.root, "sdlc-studio/personas/seats/engineering.md", engineering)
        _reject(self.root, "--tier", "full", "--tier-explicit")
        r = _cli(self.root, "brief", "--unit", UNIT, "--seat", "engineering", "--rejoinder",
                 str(self.prior))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(f"review tier: light {DERIVED}", _tier_line(r.stderr),
                         "the qa seat's REJECT set the engineering rejoinder's tier")
        with tempfile.TemporaryDirectory() as d:
            self.root = Path(d)
            _project(self.root)
            _write(self.root, "sdlc-studio/personas/seats/engineering.md", engineering)
            r = _cli(self.root, "record", "--unit", UNIT, "--verdict", "reject", "--reviewer",
                     "engineering-seat", "--author", "eng-builder", "--issues",
                     "[new] the note is wrong", "--tier", "full", "--tier-explicit")
            self.assertEqual(0, r.returncode, r.stderr)
            r = _cli(self.root, "brief", "--unit", UNIT, "--seat", "engineering", "--rejoinder")
            self.assertEqual(0, r.returncode, r.stderr)
            line = _tier_line(r.stderr)
            self.assertTrue(line.startswith("review tier: full ("), line)
            self.assertIn(f"engineering-seat's REJECT of {UNIT}", line,
                          "the engineering seat's own REJECT is not the tier's source")

    def test_a_shallower_reject_never_lowers_the_band(self) -> None:
        """A light REJECT on a unit whose band derives full is re-reviewed full, as before.
        Mutant: the REJECT's tier taken whatever the band."""
        _reject(self.root, "--tier", "light")
        with unittest.mock.patch.object(critic, "tier_for", return_value="full"):
            self.assertEqual(("full", None), critic.rejoinder_tier(self.root, UNIT, "qa"))
        _reject(self.root, "--tier", "full")
        tier, source = critic.rejoinder_tier(self.root, UNIT, "qa")
        self.assertEqual("full", tier)
        self.assertIn(f"{REVIEWER}'s REJECT of {UNIT}", source or "")


if __name__ == "__main__":
    unittest.main()
