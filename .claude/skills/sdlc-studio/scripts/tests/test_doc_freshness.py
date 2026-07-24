"""Unit tests for doc_freshness.py - the advisory LATEST.md staleness check (CR0073)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import unittest.mock as mock
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
_spec = importlib.util.spec_from_file_location("doc_freshness", SCR / "doc_freshness.py")
assert _spec and _spec.loader
df = importlib.util.module_from_spec(_spec)
sys.modules["doc_freshness"] = df
_spec.loader.exec_module(df)


def _skill(root: Path, version: str, n_tests: int) -> Path:
    sd = root / ".claude" / "skills" / "sdlc-studio"
    (sd / "scripts" / "tests").mkdir(parents=True, exist_ok=True)
    (sd / "SKILL.md").write_text(f'---\nmetadata:\n  version: "{version}"\n---\n# Skill\n', encoding="utf-8")
    body = "\n".join(f"def test_{i}():\n    pass" for i in range(n_tests))
    (sd / "scripts" / "tests" / "test_x.py").write_text(body + "\n", encoding="utf-8")
    return sd


def _latest(root: Path, text: str) -> None:
    rd = root / "sdlc-studio" / "reviews"
    rd.mkdir(parents=True, exist_ok=True)
    (rd / "LATEST.md").write_text(text, encoding="utf-8")


def _runstate(root: Path, rounds: int, ended: bool = True) -> None:
    """A run-state.json with `rounds` recorded review rounds, closed when `ended`."""
    d = root / "sdlc-studio" / ".local"
    d.mkdir(parents=True, exist_ok=True)
    state = {
        "schema": 1, "run_id": "RUN-TESTBG0261", "started_at": "2026-07-22T10:00:00Z",
        "ended_at": "2026-07-22T11:41:23Z" if ended else None,
        "outcome": "goal-reached" if ended else "running",
        "review_rounds": [{"round": i + 1, "verdict": "REJECT"} for i in range(rounds)],
    }
    (d / "run-state.json").write_text(__import__("json").dumps(state), encoding="utf-8")


class DocFreshnessTests(unittest.TestCase):
    def test_not_applicable_without_latest(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)            # skill but no LATEST.md
            self.assertFalse(df.check(d)["applicable"])

    def test_not_applicable_off_skill_repo(self):
        with tempfile.TemporaryDirectory() as d:
            _latest(Path(d), "Project version: 2.4.4")   # LATEST but no SKILL.md
            self.assertFalse(df.check(d)["applicable"])

    def test_fresh_when_claims_match(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.4\n\n3 script tests pass; disclosure 0.\n")
            with mock.patch.object(df, "_true_disclosure_count", return_value=0):
                r = df.check(d)
            self.assertTrue(r["applicable"]); self.assertTrue(r["ok"]); self.assertEqual(r["findings"], [])

    def test_version_drift(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.0\n\n3 script tests\n")
            kinds = [f["kind"] for f in df.check(d)["findings"]]
            self.assertIn("version-drift", kinds)

    def test_test_count_drift(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.4\n\n99 script tests\n")
            kinds = [f["kind"] for f in df.check(d)["findings"]]
            self.assertIn("test-count-drift", kinds)

    def test_count_drift_message_names_the_counting_method(self):
        # CR0147 (reduced AC): the finding must say WHAT it counts - statically
        # counted test functions - so the operator writes the claim for the right
        # number instead of chasing the runner's skip/subclass accounting.
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.4\n\n99 script tests\n")
            f = next(x for x in df.check(d)["findings"]
                     if x["kind"] == "test-count-drift")
            self.assertIn("counted statically", f["detail"])
            self.assertIn("test functions", f["detail"])

    def test_disclosure_drift(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.4\n\n3 script tests; disclosure 0.\n")
            with mock.patch.object(df, "_true_disclosure_count", return_value=5):
                kinds = [f["kind"] for f in df.check(d)["findings"]]
            self.assertIn("disclosure-drift", kinds)

    def test_only_checks_stated_facts(self):
        # a LATEST.md that states no test count / no disclosure must not be flagged for them
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), "2.4.4", 3)
            _latest(Path(d), "**Project version:** 2.4.4\n\nNothing else stated.\n")
            r = df.check(d)
            self.assertEqual(r["findings"], [])


class AnchorWindowCeilingTests(unittest.TestCase):
    """The anchor is a window, not a ledger: LATEST.md over the configurable
    line ceiling draws an advisory naming the remedy (move sprint paragraphs
    to their retros); under-ceiling stays silent."""

    def test_over_ceiling_flagged_with_remedy(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "3.4.0", 5)
            _latest(root, "# LATEST\n" + ("line\n" * 120))
            r = df.check(root)
            kinds = [f["kind"] for f in r["findings"]]
            self.assertIn("anchor-ledger", kinds)
            f = next(x for x in r["findings"] if x["kind"] == "anchor-ledger")
            self.assertIn("80", f["detail"])          # ceiling named
            self.assertIn("retro", f["detail"].lower())  # remedy named

    def test_under_ceiling_silent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "3.4.0", 5)
            _latest(root, "# LATEST\n" + ("line\n" * 40))
            r = df.check(root)
            self.assertNotIn("anchor-ledger", [f["kind"] for f in r["findings"]])

    def test_config_ceiling_respected(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "3.4.0", 5)
            (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "docs:\n  latest_max_lines: 200\n", encoding="utf-8")
            _latest(root, "# LATEST\n" + ("line\n" * 120))
            r = df.check(root)
            self.assertNotIn("anchor-ledger", [f["kind"] for f in r["findings"]])

class AnchorClaimsCheckedAgainstRunStateTests(unittest.TestCase):
    """BG0261: the anchor's two load-bearing claims - has the owed sign-off landed, does the
    narrated round count match the ledger - are checked against the run state, and neither check
    can be satisfied by correcting the prose alone."""

    def test_a_landed_signoff_and_a_contradicted_round_count_are_both_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, rounds=6, ended=True)          # run closed; ledger holds 6 rounds
            _latest(root, "**Project version:** 2.4.4\n\n"
                          "The run is NOT closed: the sign-off is owed and round 3's repair is "
                          "unreviewed. Three independent adversarial rounds have run.\n")
            r = df.check(root)
            kinds = [f["kind"] for f in r["findings"]]
            self.assertIn("signoff-drift", kinds)
            self.assertIn("round-count-drift", kinds)
            # distinct findings, not folded into the line-count one
            self.assertNotEqual("signoff-drift", "round-count-drift")
            rc = next(f for f in r["findings"] if f["kind"] == "round-count-drift")
            self.assertIn("6", rc["detail"])               # names the ledger's real count

        # and NEITHER fires when the document agrees with the state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, rounds=6, ended=True)
            _latest(root, "**Project version:** 2.4.4\n\n"
                          "The run is closed and the sign-off landed. "
                          "Six adversarial rounds ran.\n")
            kinds = [f["kind"] for f in df.check(root)["findings"]]
            self.assertNotIn("signoff-drift", kinds)
            self.assertNotIn("round-count-drift", kinds)

    def test_signoff_owed_is_true_while_the_run_is_still_open(self):
        # the check must not fire when the sign-off is GENUINELY owed - an open run
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, rounds=2, ended=False)
            _latest(root, "**Project version:** 2.4.4\n\nThe sign-off is owed.\n")
            self.assertNotIn("signoff-drift", [f["kind"] for f in df.check(root)["findings"]])


class ClaimAnchoredTests(unittest.TestCase):
    """US0367 / CR0302: the census guard is anchored to the CLAIM, not to the first match in the
    file and not to a freshness stamp. It failed to catch "58 scripts" against 67 present because
    it read one match and compared it as a floor; and a document nobody checked must not read the
    same as one whose counts were measured and matched."""

    def _repo(self, root: Path, n_scripts: int, n_reference: int, n_help: int) -> Path:
        sd = root / ".claude" / "skills" / "sdlc-studio"
        (sd / "scripts").mkdir(parents=True, exist_ok=True)
        (sd / "help").mkdir(parents=True, exist_ok=True)
        (sd / "SKILL.md").write_text('---\nmetadata:\n  version: "1.0.0"\n---\n', encoding="utf-8")
        for i in range(n_scripts):
            (sd / "scripts" / f"s{i}.py").write_text("", encoding="utf-8")
        for i in range(n_reference):
            (sd / f"reference-{i}.md").write_text("", encoding="utf-8")
        for i in range(n_help):
            (sd / "help" / f"h{i}.md").write_text("", encoding="utf-8")
        return sd

    def _trd(self, root: Path, text: str) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "trd.md").write_text(text, encoding="utf-8")

    def test_a_stale_count_fails_and_is_named(self):
        """AC1. The exact CR0302 shape: an exact claim under the real count, restated later in the
        file, in a document freshly touched and carrying a 'verified' stamp."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=53, n_help=44)
            self._trd(root, (
                "# TRD\n\nLast verified: 2026-07-24 (freshness stamp).\n\n"
                "The markdown knowledge base and the 58 scripts that drive it.\n\n"
                "## ADR-001\n\nSDLC Studio is large (52 reference files, 41 help files).\n"))
            r = df.census_claims(root)
            self.assertTrue(r["applicable"])
            kinds = [f["kind"] for f in r["findings"]]
            self.assertEqual(kinds, ["census-drift"] * 3, f"expected 3 stale claims, got {kinds}")
            blob = " ".join(f["detail"] for f in r["findings"])
            # each finding NAMES the stale claim: the claimed number, the measured one, and the
            # document's own words - not just a count of problems
            for claimed, actual in (("58", "67"), ("52", "53"), ("41", "44")):
                self.assertIn(claimed, blob)
                self.assertIn(actual, blob)
            self.assertIn("58 scripts", blob)          # the claim quoted back
            # and check() surfaces them as advisory findings, never as a crash or a pass
            self.assertIn("census-drift", [f["kind"] for f in df.check(root)["findings"]])

    def test_a_correct_count_passes_on_the_value_not_the_stamp(self):
        """AC2. The pass is computed from the measured value: no stamp is needed to pass, and no
        stamp can buy a pass. A claim the document does not make is UNCHECKED, not a pass."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=53, n_help=44)
            # no freshness stamp anywhere, and the counts are right
            self._trd(root, "# TRD\n\n67 scripts, 53 reference files, 44 help files.\n")
            r = df.census_claims(root)
            self.assertEqual(r["findings"], [])
            self.assertEqual(r["unchecked"], [])
            self.assertEqual(len(r["checked"]), 3)
            # the verdict carries the MEASURED number, so the pass is attributable
            self.assertEqual({c["claim"]: c["actual"] for c in r["checked"]},
                             {"scripts": 67, "reference files": 53, "help files": 44})
            self.assertTrue(all(c["ok"] for c in r["checked"]))

        # the same document with a stamp but a WRONG number still fails - the stamp is not evidence
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=53, n_help=44)
            self._trd(root, "# TRD\n\nLast verified: 2026-07-24.\n\n"
                            "58 scripts, 53 reference files, 44 help files.\n")
            r = df.census_claims(root)
            self.assertEqual([f["kind"] for f in r["findings"]], ["census-drift"])
            self.assertIn("58", r["findings"][0]["detail"])

        # a document that states NO count is unchecked - distinct from verified-and-matching
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=53, n_help=44)
            self._trd(root, "# TRD\n\nNo census claim is made here.\n")
            r = df.census_claims(root)
            self.assertEqual(r["findings"], [])
            self.assertEqual(r["checked"], [])
            self.assertEqual(sorted(r["unchecked"]),
                             ["help files", "reference files", "scripts"])

    def test_every_occurrence_is_checked_not_the_first(self):
        # the first-match defect: a correct claim early in the file must not shelter a stale
        # restatement later
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=1, n_help=1)
            self._trd(root, "# TRD\n\n67 scripts here.\n\nLater on: 58 scripts.\n")
            r = df.census_claims(root)
            self.assertEqual(len(r["checked"]), 2)
            self.assertEqual([f["kind"] for f in r["findings"]], ["census-drift"])
            self.assertIn("58", r["findings"][0]["detail"])

    def test_the_comparison_form_is_read_off_the_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=1, n_help=1)
            # "60+" is a floor and holds at 67; the same number written exact does not
            self._trd(root, "# TRD\n\n60+ scripts.\n")
            self.assertEqual(df.census_claims(root)["findings"], [])
            self._trd(root, "# TRD\n\n60 scripts.\n")
            self.assertEqual(len(df.census_claims(root)["findings"]), 1)
            # a floor left far enough behind reality is stale too
            self._trd(root, "# TRD\n\n40+ scripts.\n")
            self.assertEqual(len(df.census_claims(root)["findings"]), 1)

    def test_the_revision_history_is_not_a_current_claim(self):
        # a history entry quoting the number it corrected must not re-report the fixed defect
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=67, n_reference=1, n_help=1)
            self._trd(root, "# TRD\n\n67 scripts.\n\n## Revision History\n\n"
                            "| 2026-07-24 | restated the stale 58 scripts as a band |\n")
            self.assertEqual(df.census_claims(root)["findings"], [])

    def test_not_applicable_without_the_document(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, n_scripts=3, n_reference=1, n_help=1)
            self.assertFalse(df.census_claims(root)["applicable"])


if __name__ == "__main__":
    unittest.main()
