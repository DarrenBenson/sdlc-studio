"""US0459: the falsified token-observation premise is replaced by the measured one.

Nine live files stated that "a script cannot observe token spend". `lib/run_state.py`'s
`session_tokens` falsifies it - it reads the harness-tracked total straight out of the
transcript. The surviving limit is different and narrower: the measured total is a LOWER BOUND,
because `delegated_total` is SUPPLIED rather than observed and sidechain spend is invisible.

The verdicts here are derived from the CODE, not from a hardcoded rule. If the measurement were
ever removed, the old claim would become permissible again rather than staying banned by a
sentence in a test - which is the difference between a guard and a second copy of the doctrine.

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
TRD = REPO / "sdlc-studio" / "trd.md"
DECISIONS = REPO / "sdlc-studio" / "decisions.md"

sys.path.insert(0, str(SCRIPTS))
_spec = importlib.util.spec_from_file_location("run_state_us0459", SCRIPTS / "lib" / "run_state.py")
assert _spec and _spec.loader

#: The falsified premise, in every phrasing the corpus used.
_PREMISE = re.compile(r"(?:a\s+)?(?:script|no script)\s+can(?:no|')?t?\s*(?:not)?\s*observe\s+token",
                      re.IGNORECASE)

#: Records of what was decided or shipped THEN. Rewriting them would falsify history to make a
#: guard green, which is the one thing a truth guard must never demand.
_HISTORY = (
    "CHANGELOG.md",
    "changelog.d/",                        # fragments that BECOME CHANGELOG.md - same class
    "sdlc-studio/change-requests/",
    "sdlc-studio/handoffs/",
    "sdlc-studio/retros/",
    "sdlc-studio/reviews/",
    "sdlc-studio/bugs/",
    "tools/tests/test_token_premise.py",   # this file quotes the premise to ban it
    "sdlc-studio/stories/",                # a story describing the defect must quote it
)

#: Wording that RETRACTS the premise, and it must sit IMMEDIATELY BEFORE it. An amendment has
#: to be able to say what it corrected, so a marked quotation is allowed - but the first version
#: allowed any LINE containing one of these words, which an independent reviewer demonstrated is
#: a working bypass: "A script cannot observe token spend, so the delegated figure is no longer
#: inferred." asserted the premise and passed. Four common words disarmed the whole sweep.
_RETRACTOR = re.compile(
    r"(amended|falsif\w*|the original (?:rationale|reason)|was wrong|corrected|"
    r"said|stated(?:\s+that)?|claimed|previously|used to (?:say|state)|incorrectly)\W*$",
    re.IGNORECASE)
#: How far back a retraction may sit. Wide enough for "AMENDED 2026-07-29: the original
#: rationale said <premise>", narrow enough that a word later in the sentence cannot license it.
_RETRACTION_WINDOW = 60


def _asserts_premise(text: str) -> list[str]:
    """Lines that ASSERT the premise, ignoring one RETRACTED immediately before the phrase.

    Adjacency, not line membership. A line-wide allowance means every line carrying the word
    "corrected" may also assert the thing freely - and three live files were shown to do exactly
    that with the suite green."""
    bad = []
    for line in text.splitlines():
        for m in _PREMISE.finditer(line):
            before = line[max(0, m.start() - _RETRACTION_WINDOW):m.start()]
            if _RETRACTOR.search(before):
                continue
            bad.append(line.strip()[:120])
            break
    return bad


def _load_run_state():
    import lib.run_state as rs  # noqa: PLC0415 - loaded through the package so relatives resolve
    return rs


def _tracked(root: Path) -> list[str]:
    import subprocess  # noqa: PLC0415
    res = subprocess.run(["git", "-C", str(root), "ls-files", "*.md", "*.py"],
                         capture_output=True, text=True, check=False)
    assert res.returncode == 0, f"git ls-files failed: {res.stderr}"
    return [line for line in res.stdout.splitlines() if line.strip()]


def _d0020_row() -> str:
    for line in DECISIONS.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| D0020 "):
            return line
    raise AssertionError(
        "no D0020 row in sdlc-studio/decisions.md - the decision this guard asserts against "
        "has been removed or renumbered, and a deleted decision must not read as a compliant one")


class TokenPremiseMatchesTheCode(unittest.TestCase):

    def test_a_measuring_session_tokens_refuses_the_cannot_observe_claim(self) -> None:
        """DERIVED from the call. The claim is banned because the measurement exists, so
        removing the measurement would permit the claim again rather than leaving this test
        asserting a rule of its own."""
        rs = _load_run_state()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            transcripts = root / "transcripts"
            transcripts.mkdir()
            (transcripts / "session.jsonl").write_text(
                '{"message": {"usage": {"input_tokens": 100, "output_tokens": 50, '
                '"cache_creation_input_tokens": 10}}}\n', encoding="utf-8")
            got = rs.session_tokens(root, transcripts_dir=transcripts)
        self.assertIsInstance(got, dict)
        self.assertEqual(got.get("tokens"), 160,
                         f"session_tokens did not measure the transcript: {got}. If the "
                         f"measurement has genuinely been removed, the premise this guard bans "
                         f"is true again and both it and the documents must change together")
        for path in (TRD, DECISIONS):
            self.assertEqual([], _asserts_premise(path.read_text(encoding="utf-8")),
                             f"{path.name} still ASSERTS a premise the code falsifies")

    def test_both_documents_state_the_delegated_lower_bound_reason(self) -> None:
        """The SURVIVING limit, stated rather than vaguely gestured at: delegated spend is
        supplied, not observed, so the measured total is a lower bound.

        SCOPE, plainly, because US0459 AC2 claims more than this asserts. The two `assertIn`
        calls below search the WHOLE lowercased file, and each document also carries a Revision
        History whose row describes this very change - which contains both words. So gutting
        the passages that actually STATE the premise leaves this green: an independent seat
        emptied `trd.md` at both stating passages, together and separately, and all three
        mutants survived. This pins that the words appear SOMEWHERE in the file, which is not
        the same as pinning the claim, and AC2's "rather than a vaguer restatement" is
        precisely the distinction it fails to make. Repairing it is BG0457."""
        rs = _load_run_state()
        state = {"delegated_tokens": [{"tokens": 5000, "agent": "a", "note": ""}]}
        self.assertEqual(5000, rs.delegated_total(state),
                         "delegated_total no longer reads a supplied figure")
        for path in (TRD, DECISIONS):
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("lower bound", text,
                          f"{path.name} does not state that the measured total is a lower bound")
            self.assertIn("supplied", text,
                          f"{path.name} does not say the delegated figure is SUPPLIED rather "
                          f"than observed - the reason the bound is a bound")


class ThePremiseIsGoneFromEveryLiveFile(unittest.TestCase):

    def test_no_live_file_outside_the_history_allowlist_asserts_the_premise(self) -> None:
        offenders = []
        scanned = 0
        for rel in _tracked(REPO):
            if any(rel.startswith(h) or rel == h for h in _HISTORY):
                continue
            try:
                text = (REPO / rel).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            scanned += 1
            if _asserts_premise(text):
                offenders.append(rel)
        # The positive control: a sweep over nothing reports a clean tree.
        self.assertGreater(scanned, 50, "the sweep read almost nothing - it proves nothing")
        self.assertEqual([], offenders,
                         f"live files still assert the falsified premise: {offenders}")

    def test_a_reintroduced_premise_is_caught(self) -> None:
        """The sweep must be able to FAIL, or the assertion above is a formality."""
        for phrasing in ("a script cannot observe token spend",
                         "No script can observe token spend",
                         "a script can't observe token spend"):
            self.assertTrue(_asserts_premise(phrasing), f"not caught: {phrasing!r}")

    def test_a_trailing_retractor_word_does_not_license_an_assertion(self) -> None:
        """The bypass an independent reviewer demonstrated live in three files. A line-wide
        allowance let any line containing "no longer", "corrected", "amended" or "falsif"
        assert the premise freely."""
        for bypass in (
                "A script cannot observe token spend, so the delegated figure is no longer inferred.",
                "No script can observe token spend; this was corrected elsewhere.",
                "A script cannot observe token spend - amended in a later release."):
            self.assertTrue(_asserts_premise(bypass),
                            f"a trailing retractor word licensed an assertion: {bypass!r}")

    def test_a_retracted_quotation_is_allowed(self) -> None:
        """The other direction, and it matters as much: an amendment must be able to say what
        it corrected. A rule that banned the phrase outright would force a decision record to
        hide its own superseded rationale to make a guard green."""
        self.assertEqual([], _asserts_premise(
            "AMENDED: the original rationale said no script can observe token spend, "
            "which session_tokens falsifies."))

    def test_the_d0020_citation_is_borne_out_by_the_file_it_names(self) -> None:
        """A citation that has rotted is worse than none: it sends a reader to evidence that
        has moved. Every file the row cites is READ for the claim it is cited as supporting."""
        row = _d0020_row()
        cited = re.findall(r"`([A-Za-z0-9_./-]+\.py)(?:::[A-Za-z0-9_]+)?`", row)
        self.assertTrue(cited, "the amended D0020 row cites no file at all")
        for ref in cited:
            name = ref.split("::")[0]
            candidates = [REPO / name, SCRIPTS / Path(name).name, SCRIPTS / name]
            path = next((c for c in candidates if c.is_file()), None)
            self.assertIsNotNone(path, f"D0020 cites {name!r}, which is not on disk")
            text = path.read_text(encoding="utf-8")
            self.assertEqual([], _asserts_premise(text),
                             f"D0020 cites {name} while that file still asserts the premise")
            self.assertIn("session_tokens", text,
                          f"D0020 cites {name} as the measurement's home and it does not "
                          f"define or mention session_tokens - the citation has rotted")

    def test_a_missing_d0020_row_fails_rather_than_passing_silently(self) -> None:
        """The empty-input clean verdict that hides the whole class."""
        real = globals()["DECISIONS"]
        with tempfile.TemporaryDirectory() as d:
            stripped = Path(d) / "decisions.md"
            stripped.write_text("# Decisions\n\n| ID | Decision |\n| --- | --- |\n"
                                "| D0019 | something else |\n", encoding="utf-8")
            globals()["DECISIONS"] = stripped
            try:
                with self.assertRaises(AssertionError) as ctx:
                    _d0020_row()
                self.assertIn("D0020", str(ctx.exception),
                              "the failure does not name the row it could not find")
            finally:
                globals()["DECISIONS"] = real


if __name__ == "__main__":
    unittest.main()
