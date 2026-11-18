"""A high-class unit gets a second independent review seat, and the retro reports its yield.

The seat is briefed by the shipped `critic.py brief`, which names the unit's risk class and that
the seat is the second independent one. A second seat 'catches' something when it rejects, or
records issues, on a unit whose first seat's latest verdict approved; the retro reports those per
second seat, says in one line when a high-class unit has no second-seat verdict or when the
second seats caught nothing, and refuses nothing.
"""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import retro  # noqa: E402
from lib import run_state  # noqa: E402

_MAP = "risk:\n  components:\n    src/pay: high\n"
_AC = ("## Acceptance Criteria\n\n### AC1: the charge is taken once\n\n- **Given** x\n"
       "- **When** y\n- **Then** z\n- **Verify:** shell true\n")


def _root(d: str) -> Path:
    root = Path(d)
    (root / "sdlc-studio" / "reviews").mkdir(parents=True)
    (root / "sdlc-studio" / ".config.yaml").write_text(_MAP, encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    for role in ("qa", "engineering"):
        (seats / f"{role}.md").write_text(f"<!-- role: {role} -->\n# {role} seat\n\ncharter\n",
                                          encoding="utf-8")
    return root


def _story(root: Path, num: int, cls: str | None, affects: str = "src/pay/charge.py") -> str:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    tag = f"> **Risk-class:** {cls}\n" if cls else ""
    (d / f"US{num:04d}-s.md").write_text(
        f"# US{num:04d}: take a payment\n\n> **Status:** Review\n> **Affects:** {affects}\n"
        f"> **Points:** 2\n{tag}\n{_AC}", encoding="utf-8")
    return f"US{num:04d}"


def _bug(root: Path, num: int, affects: str) -> str:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-b.md").write_text(
        f"# BG{num:04d}: a payment bug\n\n> **Status:** Fixed\n> **Severity:** Medium\n"
        f"> **Affects:** {affects}\n> **Points:** 1\n\n{_AC}", encoding="utf-8")
    return f"BG{num:04d}"


def _ledger(root: Path, *rows: tuple[str, str, str, str]) -> None:
    """Delivery verdict rows (unit, verdict, reviewer, issues), oldest first. A row with no
    issues carries `none`, the cell `critic.py record --from-verdict` writes for `ISSUES: none`;
    the rows the recorder's round rules would refuse are written as cells, as a forced or older
    ledger holds them."""
    body = "".join(f"| {u} | {v} | {who} | builder | 2026-11-15 | {'a' * 12} | full | - "
                   f"| {issues or 'none'} |\n" for u, v, who, issues in rows)
    (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").write_text(
        critic.HEADER + body, encoding="utf-8")


def _record(root: Path, unit: str, seat: str, block: str) -> None:
    """Record one delivery verdict through the shipped `critic.py record --from-verdict`, so the
    ledger holds exactly the cells the recorder writes for the reviewer's returned block."""
    path = root / f"{unit}-{seat}.txt"
    path.write_text(f"UNIT: {unit}\nBRIEF: {path.stem}\n{block}", encoding="utf-8")
    err = io.StringIO()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
        rc = critic.main(["record", "--unit", unit, "--reviewer", seat, "--author", "builder",
                          "--from-verdict", str(path), "--root", str(root)])
    if rc != 0:
        raise AssertionError(err.getvalue())


def _retro(root: Path, units: list[str]) -> None:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    (d / "RETRO9000-t.md").write_text(
        f"# RETRO-9000: a run\n\n> **Date:** 2026-11-15\n> **Batch:** {', '.join(units)}\n"
        f"> **Goal:** take payments\n\n## Delivered\n- done\n## Lessons\n- none\n",
        encoding="utf-8")


def _composed(root: Path) -> tuple[dict, list[str]]:
    """The retro's accuracy bundle and its rendered lines, as `retro.py accuracy` composes them."""
    res = retro.accuracy(str(root), "RETRO9000")
    return res, retro._points_lines(res)  # noqa: SLF001


class SecondSeatBriefTests(unittest.TestCase):
    def test_brief_names_class_and_second_seat_role(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)
            high = _story(root, 1, "high")
            bug = _bug(root, 2, "src/pay/refund.py")
            standard = _story(root, 3, "standard", "src/core/a.py")
            text = critic.brief(root, high, "engineering", tier="full")
            # The shipped seat brief: the charter, the Affects scope and the criteria.
            self.assertIn("You are the engineering review seat", text)
            self.assertIn("personas/seats/engineering.md", text)
            self.assertIn("src/pay/charge.py", text)
            self.assertIn("AC1: the charge is taken once", text)
            self.assertIn("risk class is high", text)
            self.assertIn("second independent seat", text)
            # The first seat's brief names the class and that a second seat follows it.
            first = critic.brief(root, high, "qa", tier="full")
            self.assertIn("risk class is high", first)
            self.assertNotIn("You are the second independent seat", first)
            self.assertIn("first of two independent seats", first)
            # A bug carries no tag: its class is read from its Affects through the map.
            self.assertIn("risk class is high", critic.brief(root, bug, "engineering"))
            # Positive control: a standard unit's brief carries no second-seat line.
            plain = critic.brief(root, standard, "engineering", tier="full")
            self.assertNotIn("second independent seat", plain)
            self.assertNotIn("risk class is", plain)

    def test_first_recorded_seat_decides_which_seat_is_second(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)
            high = _story(root, 1, "high")
            # engineering reviewed first, so the qa seat is the second one on this unit.
            _ledger(root, (high, "APPROVE", "engineering", ""))
            self.assertIn("You are the second independent seat",
                          critic.brief(root, high, "qa", tier="full"))


class RetroSecondSeatYieldTests(unittest.TestCase):
    def test_retro_reports_second_seat_catches(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)
            units = [_story(root, 1, "high"), _story(root, 2, "high"),
                     _story(root, 3, "standard", "src/core/a.py"), _story(root, 4, "high"),
                     _story(root, 5, "high"), _story(root, 6, "high")]
            _ledger(root,
                    # caught: the second seat rejected after the first approved
                    ("US0001", "APPROVE", "qa", ""), ("US0001", "REJECT", "engineering",
                                                      "[new] the charge runs twice"),
                    # caught: the second seat approved but raised an issue
                    ("US0002", "APPROVE", "qa", ""), ("US0002", "APPROVE", "engineering",
                                                      "[pre-existing] a stale comment"),
                    # not counted: a standard unit has no second seat
                    ("US0003", "APPROVE", "qa", ""), ("US0003", "REJECT", "engineering", "[new] x"),
                    # not a catch: the issues are the first seat's, and it never approved
                    ("US0004", "REJECT", "qa", "[new] the refund is lost"),
                    ("US0004", "APPROVE", "engineering", ""),
                    # not a catch: the first seat's latest verdict approved, the second agreed
                    ("US0005", "REJECT", "qa", "[new] y"), ("US0005", "APPROVE", "qa", ""),
                    ("US0005", "APPROVE", "engineering", ""),
                    # not a catch: both seats rejected, so the first seat never approved
                    ("US0006", "REJECT", "qa", "[new] the ledger drifts"),
                    ("US0006", "REJECT", "engineering", "[new] the ledger drifts"))
            _retro(root, units)
            res, lines = _composed(root)
            got = res["batch"]["second_seat"]
            self.assertEqual({"engineering": ["US0001", "US0002"]},
                             {s: v["caught"] for s, v in got["seats"].items()})
            self.assertEqual(["US0001", "US0002", "US0004", "US0005", "US0006"],
                             got["seats"]["engineering"]["reviewed"])
            said = [ln for ln in lines if "second seat engineering" in ln]
            self.assertEqual(1, len(said), lines)
            self.assertIn("caught 2 of 5", said[0])
            self.assertIn("US0001, US0002", said[0])
            for absent in ("US0003", "US0004", "US0005", "US0006"):
                self.assertNotIn(absent, said[0])


class RetroSecondSeatNothingTests(unittest.TestCase):
    def test_missing_and_empty_yield_are_stated_not_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)
            units = [_story(root, 1, "high"), _story(root, 2, "high"), _story(root, 3, "high")]
            clean = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
            # A clean run as the shipped recorder writes it: `ISSUES: none` is the cell `none`,
            # and a clean approval's rulings are the one `RULINGS:` item, neither a finding.
            _record(root, "US0001", "qa", clean)
            _record(root, "US0002", "qa", clean)
            _record(root, "US0002", "engineering", clean)
            _record(root, "US0003", "qa", clean)
            _record(root, "US0003", "engineering", clean + "RULINGS: AC1 holds by execution\n")
            cells = [r["issues"] for r in critic.read_verdicts(root)]
            self.assertEqual(4, cells.count("none"), cells)
            self.assertTrue(cells[-1].startswith("RULINGS:"), cells)
            _retro(root, units)
            _res, lines = _composed(root)
            missing = [ln for ln in lines if "no second-seat verdict" in ln]
            self.assertEqual(1, len(missing), lines)
            self.assertIn("US0001", missing[0])
            self.assertNotIn("US0002", missing[0])
            nothing = [ln for ln in lines if "caught nothing" in ln]
            self.assertEqual(1, len(nothing), lines)
            self.assertIn("engineering", nothing[0])
            self.assertIn("over 2 unit(s)", nothing[0])
            self.assertEqual([], [ln for ln in lines if "caught 1" in ln or "caught 2" in ln])
            self.assertNotRegex(" ".join(missing + nothing), r"\b0\b")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = retro.main(["--root", str(root), "accuracy", "--id", "RETRO9000"])
            self.assertEqual(0, rc, err.getvalue())

    def test_a_run_with_no_high_class_unit_adds_no_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _root(d)
            units = [_story(root, 1, "standard", "src/core/a.py")]
            _ledger(root, ("US0001", "APPROVE", "qa", ""))
            _retro(root, units)
            _res, lines = _composed(root)
            self.assertEqual([], [ln for ln in lines if "second seat" in ln.lower()])


_REFERENCE = SCRIPTS.parent / "reference-sprint.md"


def _capped_root(d: str, max_rounds: int | None = None) -> Path:
    """A `_root` workspace recording without brief provenance, at the default cap unless
    `max_rounds` is given."""
    root = _root(d)
    cfg = _MAP + "review:\n  require_brief_provenance: false\n"
    if max_rounds is not None:
        cfg += f"  max_rounds: {max_rounds}\n"
    (root / "sdlc-studio" / ".config.yaml").write_text(cfg, encoding="utf-8")
    return root


def _verdict(root: Path, unit: str, seat: str, verdict: str,
             issues: str = "") -> tuple[int, str, str]:
    """One delivery verdict through the shipped `critic.py record`, refusals returned, not
    raised."""
    argv = ["record", "--unit", unit, "--verdict", verdict, "--reviewer", seat,
            "--author", "builder", "--root", str(root)]
    if issues:
        argv += ["--issues", issues]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _rows(root: Path, unit: str) -> list[dict]:
    """Every delivery verdict row the ledger holds for `unit`, oldest first."""
    return [r for r in critic.read_verdicts(root) if r.get("unit") == unit]


class SecondSeatLedgerLimitTests(unittest.TestCase):
    """The second seat runs on the single-sequence round ledger until per-seat rounds land: the
    reference states the limit, and `critic.py record` behaves as it states."""

    def setUp(self) -> None:
        # Opening a run reads the token meter; point it at nothing, never the operator's own.
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def test_the_reference_states_the_single_sequence_limit(self) -> None:
        """AC2. MUTANTS: drop the limit sentence; move it out of the second-seat text; state a cap
        the code does not default to. Each leaves the second-seat line without the claim."""
        lines = [ln for ln in _REFERENCE.read_text(encoding="utf-8").splitlines()
                 if "second independent seat" in ln]
        self.assertEqual(len(lines), 1, "premise: one second-seat line in reference-sprint.md")
        text = " ".join(lines[0].split())
        self.assertIn("rounds are one sequence per unit, whichever seat records them", text)
        self.assertIn(f"at the default cap of {critic.DEFAULT_REVIEW_CEILING} a second seat's "
                      f"REJECT after the first seat's APPROVE is round 2", text)
        self.assertIn("so the unit is carried and not repaired", text)
        self.assertIn("until per-seat rounds (US1032, US1033) land", text)

    def test_a_second_seat_reject_after_an_approve_is_carried(self) -> None:
        """AC3. MUTANTS: number rounds per seat; default the cap to 3; skip the carry. Each
        leaves the REJECT at round 1 or the unit uncarried in the batch."""
        with tempfile.TemporaryDirectory() as d:
            root = _capped_root(d)
            unit = _story(root, 1, "high")
            run_state.open_run(root, batch=[unit, "US0002"], goal="g")
            self.assertEqual(_verdict(root, unit, "qa", "APPROVE")[0], 0)
            rc, out, err = _verdict(root, unit, "engineering", "REJECT",
                                    "[new] the charge is taken twice")
            self.assertEqual(rc, 0, err)
            # Numbered against the run's own record: the carry drops the unit from the batch.
            rounds = critic.delivery_rounds(root, unit, run_state.read(root))
            self.assertEqual([(r["round"], r["verdict"], r["reviewer"]) for r in rounds],
                             [(1, "APPROVE", "qa"), (2, "REJECT", "engineering")])
            self.assertEqual(critic.first_review_seat(root, unit), "qa",
                             "premise: the REJECT is the second seat's")
            bug = critic.carried_by(root, unit)
            self.assertTrue(bug, f"the second seat's round-2 REJECT did not carry {unit}: {err}")
            self.assertIn(bug, out)
            self.assertEqual(run_state.read(root)["batch"], ["US0002"])
        # Positive control: the same two verdicts below a cap of 3 are not carried, so the carry
        # above is the cap counting both seats as one sequence.
        with tempfile.TemporaryDirectory() as d:
            root = _capped_root(d, max_rounds=3)
            unit = _story(root, 1, "high")
            run_state.open_run(root, batch=[unit, "US0002"], goal="g")
            _verdict(root, unit, "qa", "APPROVE")
            self.assertEqual(_verdict(root, unit, "engineering", "REJECT", "[new] twice")[0], 0)
            self.assertIsNone(critic.carried_by(root, unit))
            self.assertEqual(run_state.read(root)["batch"], [unit, "US0002"])

    def test_a_second_seat_verdict_past_the_cap_is_refused_in_plain_words(self) -> None:
        """AC4. MUTANTS: give every reviewer past the cap the second-seat message; give it to
        none; compare the reviewer's name rather than its seat. Each fails one of the three
        cases below."""
        with tempfile.TemporaryDirectory() as d:
            root = _capped_root(d)
            unit = _story(root, 1, "high")
            _verdict(root, unit, "qa", "REJECT", "[new] the charge is taken twice")
            self.assertEqual(_verdict(root, unit, "qa", "APPROVE")[0], 0)
            rc, _out, err = _verdict(root, unit, "engineering", "APPROVE")
            self.assertEqual(rc, 2, err)
            said = " ".join(err.split())
            self.assertIn("at the cap of 2 (`review.max_rounds`)", said)
            self.assertIn("The round ledger numbers every seat's verdicts on a unit as one "
                          "sequence", said)
            self.assertIn("the engineering seat, second after the qa seat", said)
            self.assertNotIn("still rejected at the cap", said)
            self.assertEqual(len(_rows(root, unit)), 2, "the refused verdict wrote a row")
            # Control: another reviewer in the first seat keeps the plain cap refusal.
            rc, _out, err = _verdict(root, unit, "qa-2", "APPROVE")
            self.assertEqual(rc, 2, err)
            self.assertIn("still rejected at the cap", err)
            self.assertNotIn("one sequence", err)
        # Positive control: a second-seat verdict that fits within the cap is recorded.
        with tempfile.TemporaryDirectory() as d:
            root = _capped_root(d)
            unit = _story(root, 1, "high")
            _verdict(root, unit, "qa", "APPROVE")
            rc, _out, err = _verdict(root, unit, "engineering", "APPROVE")
            self.assertEqual(rc, 0, err)
            self.assertEqual([r["reviewer"] for r in _rows(root, unit)], ["qa", "engineering"])


if __name__ == "__main__":
    unittest.main()
