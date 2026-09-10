"""The corpus verification lane compares against its baseline in BOTH directions (BG0535/D0137).

`tools/verify-corpus.sh` asks the two questions the per-commit gate cannot afford - a criterion
stamped `Verified: yes` whose selector now selects nothing, and a criterion that FAILS when
executed - and compares each count against `tools/verify-corpus-baseline.txt`.

The lane's own logic is exercised here with a STUBBED runner, so the ~28-minute release gate is
not the price of testing the comparison that wraps it. A lane whose logic can only be exercised by
paying its full cost is one whose logic never gets exercised - and the first version of this
script counted rows containing `::` and reported 3 for a corpus of 5, because two dead selectors
were a `-k` pattern and a bare file target.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LANE = REPO / "tools" / "verify-corpus.sh"

#: Five dead stamps, of which only THREE carry `::`. This is the real corpus shape as of
#: 2026-08-11 - a `-k` pattern and a bare file target have no node address - and it is what makes
#: "read the tool's own total" distinguishable from "count the rows that look like nodes".
_STAMPS_OUT = textwrap.dedent("""\
    verify-stamps: 5 stamped AC(s) resting on a selector that resolves to nothing - the stamp is STALE, not green
    US0063 AC2: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_audit_check.py
    US0273 AC2: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_preflight_writes_nothing
    US0473 AC4: stamped verified, but its verifier selects nothing
        pytest tools/tests/test_check_budgets.py::ReferenceSprintCeilingTests::test_x
    BG0357 AC4: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_y
    BG0357 AC5: stamped verified, but its verifier selects nothing
        pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::KilledMutantsCarryTheirKillerTests::test_z
""")


#: The five dead stamps of `_STAMPS_OUT`, as the `<record>::<AC>` addresses the baseline stores.
_STAMP_IDS = ("US0063::AC2", "US0273::AC2", "US0473::AC4", "BG0357::AC4", "BG0357::AC5")


def _ids(*ids: str) -> str:
    return " ".join(ids)


def _red_ids(n: int) -> tuple[str, ...]:
    """`n` synthetic red identities. The lane's fixtures claim counts of 58 and 67 while naming a
    handful, because the human clause elides after ten - so the identity payload has to be
    generated rather than typed, which is the whole reason the count alone was never enough."""
    return tuple(f"US{i:04d}::AC1" for i in range(1, n + 1))


_RED_58 = _red_ids(58)
_RED_67 = _red_ids(67)

#: The machine-readable payload `gate.py` appends to its red clause: every identity, unelided.
_RED_58_PAYLOAD = f"[ids: {_ids(*_RED_58)}]"


def _row(metric: str, count: int, ids: str, prose: str = "s") -> str:
    """One baseline row in the shipped shape: `metric|count|prose|identities`."""
    return f"{metric}|{count}|{prose}|{ids}\n"


def _make_corpus(tmp: Path, ids) -> Path:
    """A minimal corpus in which each given `<record>::<AC>` identity RESOLVES.

    The lane asks whether a baseline identity still exists before it calls its absence a repair,
    and that question is asked of a corpus. Pointing it at a fixture rather than at this
    repository is what keeps these tests from turning red the day somebody renumbers a criterion
    in an unrelated story.
    """
    root = tmp / "corpus"
    for sub in ("stories", "bugs"):
        (root / "sdlc-studio" / sub).mkdir(parents=True, exist_ok=True)
    by_record: dict[str, list[str]] = {}
    for i in ids:
        record, ac = i.split("::")
        by_record.setdefault(record, []).append(ac)
    for record, acs in by_record.items():
        sub = "bugs" if record.startswith("BG") else "stories"
        body = f"# {record}: x\n\n" + "".join(f"### {ac}: a\n\n" for ac in sorted(acs))
        (root / "sdlc-studio" / sub / f"{record}-x.md").write_text(body, encoding="utf-8")
    return root


class CorpusVerifyBaselineTests(unittest.TestCase):

    def _corpus(self, tmp: Path, ids) -> Path:
        return _make_corpus(tmp, ids)

    def _run(self, stamps_out: str, baseline: str, arg: str = "stamps", exists=_STAMP_IDS):
        """Drive the lane with a stub standing in for the Python runner it shells."""
        tmp = Path(tempfile.mkdtemp(prefix="verify_corpus_"))
        stub = tmp / "stub.py"
        # The stub ignores its arguments and prints the supplied output. It stands in for
        # `python3 <script> stamps ...`, which is how the lane invokes the real runner.
        stub.write_text("import sys\nsys.stdout.write(%r)\n" % stamps_out)
        runner = tmp / "runner.sh"
        runner.write_text(f'#!/usr/bin/env bash\nexec {sys.executable} "{stub}"\n')
        runner.chmod(0o755)
        bfile = tmp / "baseline.txt"
        bfile.write_text(baseline)
        env = {**os.environ, "PYTHON": str(runner), "VERIFY_CORPUS_BASELINE": str(bfile),
               "VERIFY_CORPUS_ROOT": str(self._corpus(tmp, exists))}
        return subprocess.run(["bash", str(LANE), arg], capture_output=True, text=True,
                              env=env, cwd=str(REPO), check=False, timeout=300)

    def test_the_count_is_the_tools_own_total_not_a_count_of_node_shaped_rows(self) -> None:
        """The bug this lane shipped with. Five dead stamps, three of which carry `::` - a reader
        that counts rows reports 3 against a baseline of 5 and blocks on a defect nobody has."""
        r = self._run(_STAMPS_OUT, _row("dead-stamps", 5, _ids(*_STAMP_IDS), "the stamps"))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("dead-stamps: 5 (baseline 5)", r.stdout)

    def test_a_count_above_the_baseline_blocks(self) -> None:
        r = self._run(_STAMPS_OUT, _row("dead-stamps", 4, _ids(*_STAMP_IDS[:4]), "the stamps"))
        self.assertNotEqual(0, r.returncode)
        self.assertIn("NEW one(s)", r.stdout + r.stderr)

    def test_a_count_below_the_baseline_also_blocks(self) -> None:
        """A baseline that only ever tolerates is one that never empties, so good news must be
        BANKED in the same commit rather than left as credit that could admit a later defect."""
        extra = "US0900::AC1"
        r = self._run(_STAMPS_OUT,
                      _row("dead-stamps", 6, _ids(*_STAMP_IDS, extra), "the stamps"),
                      exists=(*_STAMP_IDS, extra))
        self.assertNotEqual(0, r.returncode)
        self.assertIn("BANKED", r.stdout + r.stderr)

    def test_a_missing_total_is_refused_rather_than_read_as_zero(self) -> None:
        """A sweep that died before reporting and a sweep that found nothing are different facts.
        Collapsing them into 0 would turn every crash into a passing lane."""
        r = self._run("Traceback (most recent call last):\n  ImportError: no module\n",
                      _row("dead-stamps", 5, _ids(*_STAMP_IDS), "the stamps"))
        self.assertNotEqual(0, r.returncode)
        self.assertIn("did not complete", r.stdout + r.stderr)

    def test_a_baseline_row_that_is_missing_is_refused(self) -> None:
        """A metric with no row must not silently pass - that is how a lane ends up tolerating
        everything it forgot to record."""
        r = self._run(_STAMPS_OUT, "# only a comment\n")
        self.assertNotEqual(0, r.returncode)
        self.assertIn("no baseline row", r.stdout + r.stderr)

    # --- the red-criteria half, which no test reached until an independent pass ran the lane ---

    def _run_full(self, gate_out: str, baseline: str, exists=None):
        """Drive `verify-corpus.sh full`, discriminating the two runners the lane shells.

        `full` calls `verify_ac.py stamps` and then `gate.py --release` through the same `$PYTHON`,
        so a stub that ignores its arguments answers both with one string and the red half is
        never really exercised. That is exactly how the red half shipped with two defects and a
        green suite: every test here passed `stamps` and none passed `full`.
        """
        tmp = Path(tempfile.mkdtemp(prefix="verify_corpus_full_"))
        stub = tmp / "stub.py"
        stub.write_text(
            "import sys\n"
            "argv = ' '.join(sys.argv)\n"
            "sys.stdout.write(%r if 'verify_ac' in argv else %r)\n" % (_STAMPS_OUT, gate_out))
        runner = tmp / "runner.sh"
        runner.write_text(f'#!/usr/bin/env bash\nexec {sys.executable} "{stub}" "$@"\n')
        runner.chmod(0o755)
        bfile = tmp / "baseline.txt"
        bfile.write_text(baseline)
        if exists is None:
            exists = (*_STAMP_IDS, *_RED_67)
        env = {**os.environ, "PYTHON": str(runner), "VERIFY_CORPUS_BASELINE": str(bfile),
               "VERIFY_CORPUS_ROOT": str(self._corpus(tmp, exists))}
        return subprocess.run(["bash", str(LANE), "full"], capture_output=True, text=True,
                              env=env, cwd=str(REPO), check=False, timeout=300)

    #: The stamps row every `full` fixture below carries, so each one is judged on its red half.
    _STAMPS_ROW = _row("dead-stamps", 5, _ids(*_STAMP_IDS))

    #: The shape `gate.py` actually renders when the corpus is clean. The lane read `[ OK ] verify`,
    #: a string that occurs nowhere in the tree, so its green path was unreachable.
    _GATE_PASS = "  [PASS] verify [2145.0s]: 0 red AC(s) [669 stories, 1899 executable AC(s)]\n"

    #: A red run whose detail carries the unspecified clause FIRST. That clause contains colons of
    #: its own (`no Verify: line`, `Verify: manual`), which is what defeated the anchored parse.
    _GATE_RED_WITH_UNSPECIFIED = (
        "  [FAIL] verify [2145.0s]: 3 story/stories with an unspecified AC (no Verify: line - an "
        "omitted verifier is not a passed one; author one or mark it `Verify: manual`): US0001, "
        "US0002, US0003; 58 red AC(s): US0063 AC2, US0273 AC2 " + _RED_58_PAYLOAD +
        " [669 stories, 1899 executable AC(s) in 2145s (batched)]\n")

    _GATE_RED_PLAIN = ("  [FAIL] verify [2145.0s]: 58 red AC(s): US0063 AC2 " +
                       _RED_58_PAYLOAD + " [669 stories]\n")

    #: The shape BG0592 introduced: an exclusion clause carrying its own "red count"-adjacent
    #: wording and a comma-separated ledger, printed AFTER the red clause. This suite exists
    #: because this parse broke once already on a clause it had not been shown, so a new clause
    #: arrives with a fixture rather than with a hope. The identity payload sits INSIDE the red
    #: clause, so the same clause boundary the count parse needed is the one the id parse needs.
    _GATE_RED_WITH_EXCLUSIONS = (
        "  [FAIL] verify [2145.0s]: 58 red AC(s): US0063 AC2, US0273 AC2 " + _RED_58_PAYLOAD +
        "; 67 failing AC(s) on "
        "stories claiming NO completion - unbuilt or abandoned, not a regression, so outside the "
        "corpus red count: US0625::AC1 (pytest x) [Ready], US0482::AC2 (pytest y) [Superseded] "
        "[670 stories, 1943 executable AC(s) in 2145s (batched)]\n")

    def test_a_clean_verify_lane_is_read_as_zero_rather_than_as_a_crash(self) -> None:
        """The end state the baseline exists to force. Reading a marker the gate never prints made
        the green path unreachable: at `red-criteria|0` the lane could only ever have refused."""
        r = self._run_full(self._GATE_PASS, self._STAMPS_ROW + _row("red-criteria", 0, ""))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 0 (baseline 0)", r.stdout)

    def test_the_red_count_is_read_when_an_unspecified_clause_precedes_it(self) -> None:
        """The live shape. An anchored walk from the lane name cannot cross the first clause's own
        colons, so it returned empty and the lane refused as 'did not complete' with the real
        count sitting in the output it had just printed."""
        r = self._run_full(self._GATE_RED_WITH_UNSPECIFIED,
                           self._STAMPS_ROW + _row("red-criteria", 58, _ids(*_RED_58)))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_red_count_is_read_from_a_plain_detail_too(self) -> None:
        """The positive control. Without it, a parser that matched nothing at all would pass the
        test above for the wrong reason."""
        r = self._run_full(self._GATE_RED_PLAIN,
                           self._STAMPS_ROW + _row("red-criteria", 58, _ids(*_RED_58)))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_red_count_is_read_past_an_exclusion_clause(self) -> None:
        """MUTANT: let the red-count walk run to the end of the detail instead of stopping at the
        first `N red AC` match.

        The exclusion clause BG0592 added sits AFTER the red clause and contains the words
        "corpus red count" plus a second per-AC list. A greedy or last-match read picks up the
        wrong number, and the failure mode is the worst available: the lane reports a plausible
        count and nobody re-derives it.
        """
        r = self._run_full(self._GATE_RED_WITH_EXCLUSIONS,
                           self._STAMPS_ROW + _row("red-criteria", 58, _ids(*_RED_58)))
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("red-criteria: 58 (baseline 58)", r.stdout)

    def test_the_exclusion_count_is_never_mistaken_for_the_red_count(self) -> None:
        """THE DISCRIMINATOR. The exclusion clause's own number (67) must not be readable as the
        metric. Baselined at 67, this run must BLOCK rather than report a tidy match."""
        r = self._run_full(self._GATE_RED_WITH_EXCLUSIONS,
                           self._STAMPS_ROW + _row("red-criteria", 67, _ids(*_RED_67)))
        self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)

    def test_a_rise_in_red_criteria_blocks(self) -> None:
        r = self._run_full(self._GATE_RED_PLAIN,
                           self._STAMPS_ROW + _row("red-criteria", 57, _ids(*_RED_58[:57])))
        self.assertNotEqual(0, r.returncode)
        self.assertIn("NEW one(s)", r.stdout + r.stderr)

    def test_a_gate_that_died_before_reporting_is_refused_not_read_as_zero(self) -> None:
        """A crash and a clean corpus must not collapse into the same number."""
        r = self._run_full("Traceback (most recent call last):\n  RuntimeError\n",
                           self._STAMPS_ROW + _row("red-criteria", 58, _ids(*_RED_58)))
        self.assertNotEqual(0, r.returncode)
        self.assertIn("did not complete", r.stdout + r.stderr)

    def test_the_committed_baseline_names_both_metrics(self) -> None:
        """The shipped baseline must carry a row per metric the lane reads, or the scheduled run
        fails on its first invocation for a reason that looks like a defect in the corpus."""
        text = (REPO / "tools" / "verify-corpus-baseline.txt").read_text(encoding="utf-8")
        rows = {ln.split("|")[0] for ln in text.splitlines()
                if ln.strip() and not ln.startswith("#")}
        self.assertEqual({"red-criteria", "dead-stamps"}, rows)


#: The gate and the skill scripts the lane actually shells, by their real paths.
GATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"

#: `--release` BINDS four lanes, and deselecting a bound lane is refused, so the narrowest
#: honest selection that still runs the AC-verify lane names all four.
_RELEASE_LANES = "verify,review-legs,versions,changelog-fragments"


def _red_corpus(root: Path, reds: int, *, dead_stamp: bool = False) -> Path:
    """A corpus with `reds` executable criteria that FAIL, on stories claiming completion.

    `shell false` rather than a missing test file: the lane's metric is criteria that fail when
    EXECUTED, and a criterion nobody can run is a different fact with a different remedy.
    """
    (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
    for i in range(1, reds + 1):
        rec = f"US{i:04d}"
        (root / "sdlc-studio" / "stories" / f"{rec}-x.md").write_text(
            f"# {rec}: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
            f"- **Given** x\n- **When** y\n- **Then** z\n- **Verify:** shell false\n",
            encoding="utf-8")
    if dead_stamp:
        # A stamped-green criterion whose selector selects nothing: the file exists, the node
        # does not. Without one the stamp sweep prints its clean-path wording, which carries no
        # total, and the lane refuses before the red half is ever reached.
        (root / "tests").mkdir(parents=True, exist_ok=True)
        (root / "tests" / "test_x.py").write_text(
            "class T:\n    def test_a(self):\n        pass\n", encoding="utf-8")
        (root / "sdlc-studio" / "stories" / "US0090-x.md").write_text(
            "# US0090: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
            "- **Given** x\n- **When** y\n- **Then** z\n"
            "- **Verify:** pytest tests/test_x.py::T::test_missing\n- **Verified:** yes\n",
            encoding="utf-8")
    return root


class BaselineIdentityTests(unittest.TestCase):
    """BG0657: the baseline records WHICH criteria are red, not only how many.

    `red-criteria: 23, baseline 20 - 3 NEW one(s)` tells a reader to find and fix three criteria
    and gives them nothing to find them with: the baseline holds a bare number, so naming the
    three means re-running a 28-minute lane against the baseline commit and diffing two lists by
    hand. The identities are recorded beside the count, and the count stays the gate.
    """

    def _lane(self, baseline: str, corpus: Path, *, real: bool = False, gate_out: str = "",
              stamps_out: str = _STAMPS_OUT, arg: str = "full"):
        """Drive `verify-corpus.sh`. `real=True` hands it the REAL interpreter, so the strings its
        parser reads are the ones `verify_ac.py` and `gate.py` actually print."""
        tmp = Path(tempfile.mkdtemp(prefix="baseline_identity_"))
        bfile = tmp / "baseline.txt"
        bfile.write_text(baseline)
        env = {**os.environ, "VERIFY_CORPUS_BASELINE": str(bfile),
               "VERIFY_CORPUS_ROOT": str(corpus)}
        if not real:
            stub = tmp / "stub.py"
            stub.write_text(
                "import sys\n"
                "argv = ' '.join(sys.argv)\n"
                "sys.stdout.write(%r if 'verify_ac' in argv else %r)\n"
                % (stamps_out, gate_out))
            runner = tmp / "runner.sh"
            runner.write_text(f'#!/usr/bin/env bash\nexec {sys.executable} "{stub}" "$@"\n')
            runner.chmod(0o755)
            env["PYTHON"] = str(runner)
        return subprocess.run(["bash", str(LANE), arg], capture_output=True, text=True,
                              env=env, cwd=str(REPO), check=False, timeout=900)

    @staticmethod
    def _gate_line(reds, *, count=None) -> str:
        """A `[FAIL] verify` detail carrying an identity payload, in the shape gate.py renders."""
        named = ", ".join(f"{i} (shell false)" for i in reds[:10])
        return (f"  [FAIL] verify [12.0s]: {count if count is not None else len(reds)} red AC(s): "
                f"{named} [ids: {' '.join(reds)}] [9 story/stories, 9 executable AC(s)]\n")

    def test_the_full_red_identity_list_survives_the_elision(self) -> None:
        """AC1. MUTANT: wrap the machine-readable identity payload in a call to `_elide`.

        Driven through `gate.py` ITSELF over a real corpus, not through the lane against a stub
        printing a hand-written gate string: every other node in this module does the latter, so
        a mutant inside `gate.py` reddens nothing there and would be reported as survived.

        The human clause elides after ten and appends a count of the rest, which is why this
        bug's own Summary could list exactly ten of its twenty-three. A lane parsing that clause
        can never see the eleventh, so the identities have to be obtainable before they can be
        recorded.
        """
        with tempfile.TemporaryDirectory() as d:
            corpus = _red_corpus(Path(d), 12)
            r = subprocess.run([sys.executable, str(GATE), "--root", str(corpus), "--release",
                                "--only", _RELEASE_LANES],
                               capture_output=True, text=True, cwd=str(REPO), check=False,
                               timeout=600)
        line = next((ln for ln in r.stdout.splitlines() if "] verify " in ln), "")
        self.assertTrue(line, f"the verify lane printed no verdict:\n{r.stdout}{r.stderr}")
        self.assertIn("(+2 more)", line,
                      "the human list did NOT elide, so this fixture cannot show that the "
                      "payload survives an elision")
        payload = line.split("[ids: ", 1)[1].split("]", 1)[0] if "[ids: " in line else ""
        self.assertTrue(payload, f"no machine-readable identity payload in:\n{line}")
        for i in range(1, 13):
            self.assertIn(f"US{i:04d}::AC1", payload.split(),
                          f"US{i:04d}::AC1 is red and the payload does not name it:\n{payload}")
        self.assertNotIn("more)", payload, "the payload is elided too, so nothing recovers the "
                                           "identities past the tenth")

    def test_each_metric_records_identities_that_agree_with_its_count(self) -> None:
        """AC2. MUTANT: remove the length comparison between a metric's count field and its
        identity field. MUTANT: drop the discriminator that stops the capture at the clause
        boundary.

        The second is the same discriminator the count parse already needed: the exclusion ledger
        prints AFTER the red clause with a per-AC list of its own, so a capture that runs past the
        clause boundary reads 67 deliberately-excluded criteria as red.
        """
        with tempfile.TemporaryDirectory() as d:
            corpus = _make_corpus(Path(d), (*_STAMP_IDS, *_RED_58))
            # Each metric in turn: a row whose count its own identity list does not support.
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS[:3])), corpus, arg="stamps")
            self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("names 3 identity/identities", r.stdout + r.stderr)
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 58, _ids(*_RED_58[:57])), corpus,
                           gate_out=self._gate_line(_RED_58))
            self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("names 57 identity/identities", r.stdout + r.stderr)
            # ...and the clause boundary: the exclusion ledger's own ids are not red criteria.
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 58, _ids(*_RED_58)), corpus,
                           gate_out=self._GATE_WITH_EXCLUSIONS)
            self.assertEqual(0, r.returncode,
                             "the capture ran past the red clause and read the exclusion "
                             f"ledger's identities as red:\n{r.stdout}{r.stderr}")
            # ...and the rule applies to the OBSERVED side too: a run that reports a total its
            # own identity payload does not carry has told the reader two different things.
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 58, _ids(*_RED_58)), corpus,
                           gate_out=self._gate_line(_RED_58, count=99))
            self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("does not support", r.stdout + r.stderr)
        # The COMMITTED baseline holds to the same rule it enforces.
        for metric, count, ids in self._committed_rows():
            self.assertEqual(count, len(ids),
                             f"the committed '{metric}' row records {count} and names "
                             f"{len(ids)} identity/identities")

    #: The red clause followed by the exclusion ledger, which carries a second per-AC list and
    #: bracketed statuses of its own. Assembled here so both the payload and the ledger are in
    #: one string the lane's parser has to walk.
    _GATE_WITH_EXCLUSIONS = (
        "  [FAIL] verify [12.0s]: 58 red AC(s): " +
        ", ".join(f"{i} (shell false)" for i in _RED_58[:10]) +
        f" [ids: {' '.join(_RED_58)}]" +
        "; 67 failing AC(s) on stories claiming NO completion - unbuilt or abandoned, not a "
        "regression, so outside the corpus red count: US0625::AC1 (pytest x) [Ready], "
        "US0482::AC2 (pytest y) [Superseded] [670 stories, 1943 executable AC(s)]\n")

    @staticmethod
    def _committed_rows():
        text = (REPO / "tools" / "verify-corpus-baseline.txt").read_text(encoding="utf-8")
        for ln in text.splitlines():
            if not ln.strip() or ln.startswith("#"):
                continue
            parts = ln.split("|")
            yield parts[0], int(parts[1]), (parts[3].split() if len(parts) > 3 else [])

    def test_the_lane_names_what_rose_and_what_went_green(self) -> None:
        """AC3. MUTANT: delete the two set-difference computations, leaving the numeric
        comparison - the lane then says the number moved and still cannot say which three."""
        baseline_ids = ("US0001::AC1", "US0002::AC1", "US0003::AC1")
        observed = ("US0001::AC1", "US0002::AC1", "US0004::AC1", "US0005::AC1")
        with tempfile.TemporaryDirectory() as d:
            corpus = _make_corpus(Path(d), (*_STAMP_IDS, *baseline_ids, *observed))
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 3, _ids(*baseline_ids)), corpus,
                           gate_out=self._gate_line(observed))
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertIn("NEW: ", out, f"the refusal names no new identities at all:\n{out}")
        self.assertIn("went green: ", out, f"the refusal names nothing that went green:\n{out}")
        new = out.split("NEW: ", 1)[1].split("\n", 1)[0]
        green = out.split("went green: ", 1)[1].split("\n", 1)[0]
        self.assertEqual({"US0004::AC1", "US0005::AC1"}, set(new.split()), out)
        self.assertEqual({"US0003::AC1"}, set(green.split()), out)

    def test_an_equal_sized_swap_is_not_silent(self) -> None:
        """AC4. MUTANT: insert an early `exit 0` as soon as the two counts are equal.

        One criterion repaired and another introduced in the same window: the counts match, and
        a bare number reports a clean lane over a corpus that changed. This is the case the count
        alone cannot carry, and the reason the identities are worth recording at all.
        """
        baseline_ids = ("US0001::AC1", "US0002::AC1", "US0003::AC1")
        observed = ("US0001::AC1", "US0002::AC1", "US0004::AC1")
        with tempfile.TemporaryDirectory() as d:
            corpus = _make_corpus(Path(d), (*_STAMP_IDS, *baseline_ids, *observed))
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 3, _ids(*baseline_ids)), corpus,
                           gate_out=self._gate_line(observed))
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode,
                            f"an equal-sized swap exited 0 and said nothing:\n{out}")
        self.assertIn("COUNTS MATCH", out, out)
        self.assertIn("NEW: ", out, f"the refusal names no new identities at all:\n{out}")
        self.assertIn("went green: ", out, f"the refusal names nothing that went green:\n{out}")
        self.assertIn("US0004::AC1", out.split("NEW: ", 1)[1].split("\n", 1)[0], out)
        self.assertIn("US0003::AC1", out.split("went green: ", 1)[1].split("\n", 1)[0], out)

    def test_a_vanished_identity_is_named_rather_than_counted_as_repaired(self) -> None:
        """AC5. MUTANT: delete the existence test on each baseline identity, so an absent one
        falls into the repaired set - the number then falls for a reason nobody chose."""
        gone = "US0999::AC1"
        baseline_ids = ("US0001::AC1", "US0002::AC1", gone)
        observed = ("US0001::AC1", "US0002::AC1")
        with tempfile.TemporaryDirectory() as d:
            # The corpus holds the two survivors and NOT the third: a unit deleted, or its
            # criteria renumbered.
            corpus = _make_corpus(Path(d), (*_STAMP_IDS, *observed))
            r = self._lane(_row("dead-stamps", 5, _ids(*_STAMP_IDS))
                           + _row("red-criteria", 3, _ids(*baseline_ids)), corpus,
                           gate_out=self._gate_line(observed))
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, out)
        self.assertIn("VANISHED from the corpus", out,
                      f"the refusal has no vanished clause at all:\n{out}")
        self.assertIn("went green: ", out, f"the refusal names nothing that went green:\n{out}")
        vanished = out.split("VANISHED from the corpus", 1)[1].split("\n", 1)[0]
        green = out.split("went green: ", 1)[1].split("\n", 1)[0]
        self.assertIn(gone, vanished, f"an absent identity was not named as vanished:\n{out}")
        self.assertNotIn(gone, green, f"an absent identity was counted as a repair:\n{out}")

    def test_an_unchanged_tree_still_passes_and_the_format_still_parses(self) -> None:
        """AC6. MUTANT: rename the two metric keys in tools/verify-corpus-baseline.txt so the
        committed parse no longer matches them.

        The anchor the stubbed nodes cannot supply. Every other node here hands the lane a
        hand-written gate string, and a parser written against a hand-written fixture agrees with
        a string nobody produces. This one runs the REAL `verify_ac.py stamps` and the REAL
        `gate.py --release` over a corpus, and feeds their actual output to the lane's own parser.
        """
        with tempfile.TemporaryDirectory() as d:
            corpus = _red_corpus(Path(d), 12, dead_stamp=True)
            # 13 red, not 12: the stamped criterion's selector selects nothing, so it FAILS when
            # executed as well as resting on a dead stamp. Both metrics see it, for two reasons.
            reds = _ids(*(f"US{i:04d}::AC1" for i in range(1, 13)), "US0090::AC1")
            r = self._lane(_row("dead-stamps", 1, "US0090::AC1")
                           + _row("red-criteria", 13, reds), corpus, real=True)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode,
                         f"the lane cannot parse what the real emitters print:\n{out}")
        self.assertIn("dead-stamps: 1 (baseline 1) OK", r.stdout, out)
        self.assertIn("red-criteria: 13 (baseline 13) OK", r.stdout, out)
        # ...and the committed baseline still names both metrics in the shape the existing
        # pinning test reads, with identities behind each count.
        rows = list(self._committed_rows())
        self.assertEqual({"red-criteria", "dead-stamps"}, {m for m, _c, _i in rows})
        for metric, count, ids in rows:
            self.assertEqual(count, len(ids),
                             f"the committed '{metric}' row records {count} and names "
                             f"{len(ids)} identity/identities")


if __name__ == "__main__":
    unittest.main()
