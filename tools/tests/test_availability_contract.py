"""US0455: one availability contract, stated the same way everywhere and derived from the code.

Four passages answered one question, and three of them were wrong. `github_sync.gh()` raises
when `gh` is off PATH and `main()` returns 127 - it FAILS LOUD. The PRD, ADR-004 and the
personas capability list all said sync "degrades gracefully when `gh` is absent". Only the TSD's
NFR row had it right.

The verdict is COMPUTED from the observed exit code, so removing the abort would permit the
graceful wording again rather than leaving it banned by a sentence in a test.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PRD = REPO / "sdlc-studio" / "prd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"
TRD = REPO / "sdlc-studio" / "trd.md"
PERSONAS = REPO / "sdlc-studio" / "personas.md"
DECISIONS = REPO / "sdlc-studio" / "decisions.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))

#: The claim the shipped behaviour contradicts, in every phrasing that means it. The first
#: version matched ONE - `degrades gracefully when gh` - so `gracefully degrades`,
#: `degrades gracefully IF gh is absent`, `in the absence of gh` and `silently no-ops` all
#: walked past it. A denylist of one spelling is a denylist of nothing.
_GRACEFUL = re.compile(
    r"(degrades?\s+gracefully|gracefully\s+degrades?|silently\s+no-?ops?|"
    r"soft\s+no-?ops?|no-?ops?\s+silently)", re.IGNORECASE)

#: The contract each passage must POSITIVELY state, as a phrase that means it - not as the
#: letters `fail` occurring anywhere. The first version used `assertRegex(passage, "(fail|
#: abort|non-zero)")` over the whole of personas.md, so deleting the contract sentence left the
#: test green on an unrelated "fix failures before tagging". A substring is not a claim.
_STATES_FAIL_LOUD = re.compile(
    r"(fails?\s+loud|aborts?\s+(?:non-zero|with|cleanly)|exits?\s+non-zero|"
    r"aborts?\s+non-zero|non-zero\s+exit|does\s+not\s+degrade)", re.IGNORECASE)


def states_fail_loud(passage: str) -> bool:
    """True when the passage states the contract, and it must name `gh` in the same passage.

    Both halves matter: a passage may say something aborts without saying WHAT, and a passage
    naming `gh` proves nothing about the abort. Requiring both in the same located block is what
    stops an unrelated sentence elsewhere in the file satisfying it.
    """
    return bool(_STATES_FAIL_LOUD.search(passage)) and "gh" in passage.lower()


#: A negation IMMEDIATELY before the claim, within a short window. Scoped by adjacency rather
#: than allowed line-wide: a line-wide allowance is a bypass, because any line containing the
#: word also gets to assert the thing freely - which is exactly the hole an independent
#: reviewer opened in this sprint's sibling guard.
_NEGATED = re.compile(r"(does\s+not|doesn'?t|never|no\s+longer|rather\s+than|not)\s*$",
                      re.IGNORECASE)
_NEGATION_WINDOW = 24


def graceful_findings(where: str, passage: str) -> list[str]:
    """A pure rule over passage TEXT, so it can be proven to fail on the exact defect.

    Exposed as a function rather than folded into an assertion over the live files: a defence
    that has only ever been run against a repaired tree has never been shown to work.

    A NEGATED claim is not a claim: "does not degrade gracefully" is the contract being stated,
    not contradicted. The negation must sit immediately before the phrase, so a negating word
    elsewhere in the sentence cannot license an assertion.
    """
    out = []
    for m in _GRACEFUL.finditer(passage):
        before = passage[max(0, m.start() - _NEGATION_WINDOW):m.start()]
        if _NEGATED.search(before.rstrip()):
            continue
        out.append(f"{where}: {m.group(0)!r} contradicts the shipped fail-loud abort")
    return out


def _observed_gh_absent_exit() -> int:
    """What `github_sync` actually does with `gh` off PATH - monkeypatched in-process."""
    import shutil
    spec = importlib.util.spec_from_file_location("gs_us0455", SCRIPTS / "github_sync.py")
    assert spec and spec.loader
    gs = importlib.util.module_from_spec(spec)
    sys.modules["gs_us0455"] = gs
    spec.loader.exec_module(gs)
    real = shutil.which
    shutil.which = lambda name, *a, **k: None if name == "gh" else real(name, *a, **k)
    try:
        try:
            gs.gh("issue", "list")
        except RuntimeError:
            return 127
        return 0
    finally:
        shutil.which = real


def _section(path: Path, heading: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    i = text.find(heading)
    assert i != -1, (f"{path.name}: could not locate {heading!r} - the passage was renamed, and "
                     f"a guard must never report a clean result for text it did not read")
    rest = text[i + len(heading):]
    m = re.search(end, rest, re.M)
    return rest[:m.start()] if m else rest


def _personas_availability_bullet() -> str:
    """The ONE capability bullet that states the contract, located rather than searched for.

    Reading the whole file made the positive assertion satisfiable by any line containing the
    letters `fail` - which `fix failures before tagging` supplies - so the contract sentence
    could be deleted with the suite green."""
    for line in PERSONAS.read_text(encoding="utf-8").splitlines():
        low = line.lower()
        if line.lstrip().startswith("-") and "offline-capable" in low and "sync" in low:
            return line
    raise AssertionError("no offline-capable/sync capability bullet in personas.md - the "
                         "passage was renamed or removed, and a guard must not report a clean "
                         "result for text it did not read")


def _tsd_availability_row() -> str:
    for line in TSD.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "**Availability**" in line:
            return line
    raise AssertionError("no Availability row in the TSD's NFR mapping table")


def _cr0427_decision() -> str:
    for line in DECISIONS.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "CR0427" in line and "resolved by" in line:
            return line
    raise AssertionError("no decisions.md row records which CR0427 branch was taken - the "
                         "rewording must be traceable to a ruling, not to an editorial choice")


class AvailabilityContractAgrees(unittest.TestCase):

    def test_the_prd_clause_and_tsd_row_match_the_measured_abort(self) -> None:
        observed = _observed_gh_absent_exit()
        self.assertEqual(127, observed,
                         "github_sync no longer aborts with gh absent - if the behaviour has "
                         "genuinely changed, this guard and all four passages change together")
        for where, passage in (
                ("prd.md Availability", _section(PRD, "### Availability", r"^## ")),
                ("tsd.md NFR row", _tsd_availability_row()),
                # The LOCATED capability bullet, not the whole file: reading the whole of
                # personas.md let an unrelated "fix failures before tagging" satisfy the
                # positive assertion while the contract sentence was deleted outright.
                ("personas.md capability bullet", _personas_availability_bullet())):
            self.assertEqual([], graceful_findings(where, passage))
            self.assertTrue(states_fail_loud(passage),
                            f"{where} does not state the fail-loud contract - it must say the "
                            f"sync aborts/fails-loud AND name `gh`, in this passage: {passage!r}")

    def test_adr_004_block_states_the_same_contract(self) -> None:
        """The THIRD copy, extracted by its own heading - never the whole TRD, or a correct
        sentence anywhere in the document would satisfy it."""
        block = _section(TRD, "### ADR-004", r"^### ADR-")
        self.assertEqual([], graceful_findings("trd.md ADR-004", block))
        self.assertTrue(states_fail_loud(block),
                        "ADR-004 does not state the fail-loud contract")

    def test_the_positive_assertion_cannot_be_satisfied_by_an_unrelated_sentence(self) -> None:
        """The hole an independent reviewer found: the contract sentence deleted, the test green
        on `fix failures before tagging`. Both halves are required in the SAME passage now."""
        self.assertFalse(states_fail_loud("Runs the suite; fix failures before tagging."),
                         "an unrelated sentence containing 'fail' satisfied the contract")
        self.assertFalse(states_fail_loud("the nightly backup must not fail"),
                         "a sentence with no mention of gh satisfied the contract")
        self.assertFalse(states_fail_loud("with `gh` absent the behaviour is unspecified"),
                         "naming gh without stating the abort satisfied the contract")
        self.assertTrue(states_fail_loud("with `gh` absent it aborts non-zero"))

    def test_a_reintroduced_graceful_claim_returns_a_finding(self) -> None:
        """The defence proven on the exact defect it was built for, not only on a repaired tree,
        and in every phrasing that MEANS it - a denylist of one spelling is a denylist of
        nothing. All four of these walked past the first version."""
        for wording in ("sync degrades gracefully when `gh` is absent",
                        "checks degrade gracefully when gh is absent",
                        "sync gracefully degrades if `gh` is missing",
                        "with `gh` absent the sync silently no-ops",
                        "github_sync does a soft no-op in the absence of gh"):
            found = graceful_findings("fixture", wording)
            self.assertTrue(found, f"not caught: {wording!r}")
            self.assertIn("fixture", found[0], "the finding does not name the passage")

    def test_the_branch_is_recorded_as_a_decision_row(self) -> None:
        row = _cr0427_decision()
        self.assertRegex(row.lower(), r"reword",
                         "the row does not name which branch of CR0427 was taken")
        self.assertRegex(row.lower(), r"not implemented|fail.loud|aborts",
                         "the row does not state the contract the rewording implies")

    def test_a_missing_passage_or_row_fails_rather_than_reporting_clean(self) -> None:
        """The empty-set pass that let the original drift survive four revisions."""
        with self.assertRaises(AssertionError) as ctx:
            _section(PRD, "### A Heading Nobody Wrote", r"^## ")
        self.assertIn("could not locate", str(ctx.exception))

        real = globals()["DECISIONS"]
        with tempfile.TemporaryDirectory() as d:
            stripped = Path(d) / "decisions.md"
            stripped.write_text("# Decisions\n\n| ID | Decision |\n| --- | --- |\n", encoding="utf-8")
            globals()["DECISIONS"] = stripped
            try:
                with self.assertRaises(AssertionError) as ctx2:
                    _cr0427_decision()
                self.assertIn("CR0427", str(ctx2.exception))
            finally:
                globals()["DECISIONS"] = real


if __name__ == "__main__":
    unittest.main()
