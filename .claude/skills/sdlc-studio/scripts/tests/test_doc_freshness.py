"""Unit tests for doc_freshness.py - the advisory LATEST.md staleness check (CR0073)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
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


def _runstate(root: Path, ended: bool = True) -> None:
    """A run-state.json, closed when `ended`."""
    d = root / "sdlc-studio" / ".local"
    d.mkdir(parents=True, exist_ok=True)
    state = {
        "schema": 1, "run_id": "RUN-TESTBG0261", "started_at": "2026-07-22T10:00:00Z",
        "ended_at": "2026-07-22T11:41:23Z" if ended else None,
        "outcome": "goal-reached" if ended else "running",
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

    def test_overage_stated_explicitly(self):
        """US0365 AC1: the refusal names how many lines OVER the ceiling, not only the two
        raw numbers - a reader should not have to subtract to know the size of the trim."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "3.4.0", 5)
            # 82 content lines under an 80 ceiling: exactly 2 over.
            _latest(root, "# LATEST\n" + ("line\n" * 81))
            r = df.check(root)
            f = next(x for x in r["findings"] if x["kind"] == "anchor-ledger")
            self.assertIn("2 over the 80-line ceiling", f["detail"],
                          "the overage must be stated, e.g. '2 over the 80-line ceiling'")

    def test_longest_sections_named_by_line_count(self):
        """US0365 AC2: the message names the longest sections and their line counts so the
        trim can be aimed rather than guessed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "3.4.0", 5)
            body = (
                "# LATEST\n"
                "## Short\n" + ("s\n" * 4)
                + "## Sprint history\n" + ("h\n" * 80)
                + "## Extra\n" + ("e\n" * 40)
                + "## Middle\n" + ("m\n" * 20)
            )
            _latest(root, body)
            r = df.check(root)
            f = next(x for x in r["findings"] if x["kind"] == "anchor-ledger")
            # The biggest section is named with its count, ahead of the smaller ones.
            self.assertIn("Sprint history", f["detail"])
            self.assertRegex(f["detail"], r"Sprint history' \(\d+ lines\)")
            self.assertLess(f["detail"].index("Sprint history"),
                            f["detail"].index("Middle"),
                            "sections must be named longest-first")
            self.assertNotIn("Short", f["detail"],
                             "only the longest few are named, not every heading")

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
    """BG0261: the anchor's load-bearing claim - has the owed sign-off landed - is checked against
    the run state. Its round-count half read a ledger nothing writes, and BG0783 deleted it."""

    def test_a_landed_signoff_is_reported_and_an_agreeing_anchor_is_not(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, ended=True)
            _latest(root, "**Project version:** 2.4.4\n\n"
                          "The run is NOT closed: the sign-off is owed and round 3's repair is "
                          "unreviewed.\n")
            self.assertIn("signoff-drift", [f["kind"] for f in df.check(root)["findings"]])

        # and it does not fire when the document agrees with the state
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, ended=True)
            _latest(root, "**Project version:** 2.4.4\n\n"
                          "The run is closed and the sign-off landed.\n")
            self.assertNotIn("signoff-drift", [f["kind"] for f in df.check(root)["findings"]])

    def test_signoff_owed_is_true_while_the_run_is_still_open(self):
        # the check must not fire when the sign-off is GENUINELY owed - an open run
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _skill(root, "2.4.4", 3)
            _runstate(root, ended=False)
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
            self.assertEqual(r["unchecked"], ["baseline"])
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
                             ["baseline", "help files", "reference files", "scripts"])

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


def _census_tree(root: Path, n_scripts: int, n_reference: int, n_help: int) -> Path:
    """A skill tree for the census to measure. A test reads its figures back through the
    census's own derivations rather than restating them."""
    sd = root / ".claude" / "skills" / "sdlc-studio"
    (sd / "scripts").mkdir(parents=True, exist_ok=True)
    (sd / "help").mkdir(parents=True, exist_ok=True)
    (sd / "SKILL.md").write_text('---\nmetadata:\n  version: "3.2.1"\n---\n', encoding="utf-8")
    for i in range(n_scripts):
        (sd / "scripts" / f"s{i}.py").write_text("", encoding="utf-8")
    for i in range(n_reference):
        (sd / f"reference-{i}.md").write_text("", encoding="utf-8")
    for i in range(n_help):
        (sd / "help" / f"h{i}.md").write_text("", encoding="utf-8")
    return sd


def _spec(root: Path, name: str, text: str) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / name).write_text(text, encoding="utf-8")


def _run(root: Path, *extra: str) -> str:
    """doc_freshness.py as the operator runs it, its stdout captured."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = df.main(["--root", str(root), *extra])
    assert rc == 0, "the check is advisory and must exit 0"
    return out.getvalue()


class PrdTsdFreshnessTests(unittest.TestCase):
    """The census reads the PRD and TSD as it reads the TRD: a count or baseline either one states
    is judged against the tree, and a band is judged as a band."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        sd = _census_tree(self.root, n_scripts=67, n_reference=53, n_help=44)
        self.measured = {name: measure(sd) for name, measure in df._CENSUS_MEASURES.items()}
        self.version = df._true_version(sd)
        # a TRD whose claims hold, so any finding below is the PRD's or the TSD's own
        _spec(self.root, "trd.md", (
            f"# TRD\n\nCoverage: v{self.version} as cut.\n\n{self.measured['scripts']} scripts.\n"))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _findings(self) -> list[dict]:
        return json.loads(_run(self.root, "--format", "json"))["findings"]

    def test_a_stale_prd_count_is_reported(self):
        """AC1. MUTANT: leave the PRD out of the census's document set - nothing then reads it and
        the stale count goes unreported."""
        stale = self.measured["scripts"] - 9
        _spec(self.root, "prd.md", (
            "# PRD\n\n### Tech Stack\n\n"
            f"- **Python 3.10+** - {stale} scripts under `scripts/`, sharing `lib/`.\n"))
        findings = self._findings()
        self.assertEqual([f["kind"] for f in findings], ["census-drift"], findings)
        detail = findings[0]["detail"]
        self.assertIn("sdlc-studio/prd.md", detail)
        self.assertIn(f"claims {stale} scripts", detail)                  # the stated figure
        self.assertIn(f"{self.measured['scripts']} counted", detail)       # the derived one
        self.assertIn(f"{stale} scripts under `scripts/`", detail)         # the line, quoted
        # the text report names the PRD's census beside the TRD's
        text = _run(self.root)
        self.assertIn("[census-drift] sdlc-studio/prd.md claims", text)
        self.assertIn("claim(s) in sdlc-studio/prd.md verified", text)

    def test_a_stale_tsd_figure_is_reported(self):
        """AC2. MUTANT: leave the TSD out of the census's document set, compare the baseline on its
        major figure alone (or its major and minor), or report only a baseline behind SKILL.md. A
        baseline one major, minor or patch figure behind SKILL.md's version, or one patch ahead,
        and a count the tree no longer holds, are each reported."""
        major, minor, patch = (int(n) for n in self.version.split("."))
        stale = self.measured["help files"] + 5
        # one figure off at a time, so an exact comparison and a partial one disagree
        for other in (f"{major - 1}.{minor}.{patch}", f"{major}.{minor - 1}.{patch}",
                      f"{major}.{minor}.{patch - 1}", f"{major}.{minor}.{patch + 1}"):
            with self.subTest(baseline=other):
                _spec(self.root, "tsd.md", (
                    "# Test Strategy Document\n\n"
                    f"> **Coverage:** v{other} as cut, plus the work on `main` since.\n\n"
                    f"The skill ships {stale} help files.\n"))
                findings = self._findings()
                self.assertEqual([f["kind"] for f in findings], ["census-drift"] * 2, findings)
                self.assertTrue(all("sdlc-studio/tsd.md" in f["detail"] for f in findings),
                                findings)
                baseline = next(f["detail"] for f in findings if "as its baseline" in f["detail"])
                self.assertIn(f"names v{other} as its baseline", baseline)
                self.assertIn(f"SKILL.md is {self.version}", baseline)
                self.assertIn(f"v{other} as cut", baseline)
                count = next(f["detail"] for f in findings
                             if f"claims {stale} help files" in f["detail"])
                self.assertIn(f"{self.measured['help files']} counted", count)

    def test_matching_prd_and_tsd_are_clean(self):
        """AC3, the positive control. MUTANT: read a band ("about 50", "40+") as a pinned count -
        each band below sits off the measured figure, so an exact reading reports it."""
        m = self.measured
        _spec(self.root, "prd.md", (
            f"# PRD\n\n> **Coverage:** v{self.version} as cut, plus the work on `main` since.\n\n"
            f"{m['scripts']} scripts, about {m['reference files'] - 4} reference files and "
            f"{m['help files'] - 3}+ help files.\n"))
        _spec(self.root, "tsd.md", (
            f"# TSD\n\n> **Coverage:** v{self.version} as cut.\n\n"
            f"Roughly {m['scripts'] + 6} scripts and ~{m['help files'] - 2} help files.\n"))
        r = json.loads(_run(self.root, "--format", "json"))
        self.assertEqual(r["findings"], [])
        census = {c["document"]: c for c in r["census"]}
        # read, not skipped: each claim the two documents make was checked, and held
        forms = {doc: sorted(c["form"] for c in census[doc]["checked"])
                 for doc in ("sdlc-studio/prd.md", "sdlc-studio/tsd.md")}
        self.assertEqual(forms["sdlc-studio/prd.md"], ["approximate", "exact", "exact", "floor"])
        self.assertEqual(forms["sdlc-studio/tsd.md"], ["approximate", "approximate", "exact"])
        for doc in forms:
            self.assertTrue(all(c["ok"] for c in census[doc]["checked"]), census[doc])
        text = _run(self.root)
        self.assertIn("doc-freshness: state documents are fresh", text)
        self.assertIn("4/4 claim(s) in sdlc-studio/prd.md verified", text)
        self.assertIn("3/3 claim(s) in sdlc-studio/tsd.md verified", text)

    def test_a_band_left_far_behind_is_still_reported(self):
        """MUTANT: never report an approximate claim, drop either end of its band, or drop one of
        its spellings. "about N" holds near N, not at any count."""
        actual = self.measured["scripts"]
        for word, far in [(w, n) for w in ("About ", "around ", "roughly ", "approximately ", "~")
                          for n in (actual // 2, actual * 2)]:
            with self.subTest(word=word, far=far):
                _spec(self.root, "prd.md", f"# PRD\n\n{word}{far} scripts.\n")
                findings = self._findings()
                self.assertEqual(len(findings), 1, findings)
                self.assertIn(f"claims {word}{far} scripts", findings[0]["detail"])
                self.assertIn("an approximate claim holds while the count sits in",
                              findings[0]["detail"])

    def test_the_approximate_band_is_pinned_at_both_edges(self):
        """MUTANT: widen or narrow the band (a ratio of 1.1 or 1.9 for 1.25), or swap either edge's
        comparison (`<=` at the top, `<` at the bottom). "about N" holds while the count sits in
        [N / 1.25, N x 1.25): the bottom edge is in the band and the top edge is not."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            actual = df._CENSUS_MEASURES["scripts"](_census_tree(root, 40, 1, 1))
            # 1.25 is written here, not read off the module, so a change to the module's ratio
            # fails; a count divisible by 20 puts both edges on whole numbers
            self.assertEqual(actual % 20, 0, actual)
            # at_top x 1.25 == actual == at_bottom / 1.25
            at_top, at_bottom = actual * 4 // 5, actual * 5 // 4
            for claimed, holds in ((at_top - 1, False), (at_top, False), (at_top + 1, True),
                                   (at_bottom - 1, True), (at_bottom, True),
                                   (at_bottom + 1, False)):
                with self.subTest(claimed=claimed, actual=actual):
                    _spec(root, "prd.md", f"# PRD\n\nabout {claimed} scripts.\n")
                    r = json.loads(_run(root, "--format", "json"))
                    prd = next(c for c in r["census"] if c["document"] == "sdlc-studio/prd.md")
                    self.assertEqual([c["ok"] for c in prd["checked"]], [holds], prd)
                    self.assertEqual(len(r["findings"]), 0 if holds else 1, r["findings"])

    def test_a_prd_or_tsd_alone_makes_the_check_applicable(self):
        """MUTANT: judge applicability on the TRD alone (`census[0]["applicable"]`), or on the TRD
        and the PRD. On SKILL.md and one stale PRD or TSD, with no LATEST.md and no TRD, the first
        prints N/A for either document and the second for the TSD."""
        spec_dir = self.root / "sdlc-studio"
        (spec_dir / "trd.md").unlink()
        self.assertFalse((spec_dir / "reviews" / "LATEST.md").exists())
        stale = self.measured["scripts"] - 9
        for doc in ("prd.md", "tsd.md"):
            with self.subTest(doc=doc):
                for each in ("prd.md", "tsd.md"):
                    (spec_dir / each).unlink(missing_ok=True)
                _spec(self.root, doc, f"# Spec\n\n{stale} scripts.\n")
                r = json.loads(_run(self.root, "--format", "json"))
                self.assertTrue(r["applicable"], r)
                self.assertEqual([f["detail"].split(" claims ")[0] for f in r["findings"]],
                                 [f"sdlc-studio/{doc}"], r["findings"])
                self.assertIn(f"[census-drift] sdlc-studio/{doc} claims {stale} scripts",
                              _run(self.root))

    def test_a_baseline_is_unchecked_when_skill_md_names_no_version(self):
        """MUTANT: judge a stated baseline against a missing version - it is then reported as
        stale, though nothing measured contradicts it."""
        skill = self.root / ".claude" / "skills" / "sdlc-studio" / "SKILL.md"
        skill.write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
        _spec(self.root, "prd.md", "# PRD\n\n> **Coverage:** v1.0.0 as cut.\n")
        r = json.loads(_run(self.root, "--format", "json"))
        self.assertEqual(r["findings"], [])
        prd = next(c for c in r["census"] if c["document"] == "sdlc-studio/prd.md")
        self.assertIn("baseline", prd["unchecked"])


if __name__ == "__main__":
    unittest.main()
