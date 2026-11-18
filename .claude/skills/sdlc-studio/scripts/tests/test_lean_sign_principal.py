"""BG0776: `sprint sign --principal` refuses a principal that names nobody.

The guard used to strip the raw string, so `-` passed it while the id normaliser the
independence check compares with reads `-` as empty: the run was sealed with a signature that
named no principal. Driven through `sprint.main`, the shipped entry point, in a throwaway run
whose batch is empty, so nothing is stubbed and the seal is the real one.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")


def _closed_run(root: Path) -> None:
    """A run the close prepared: it names its report and a goal verdict, and is not sealed."""
    state = {
        "schema": 1, "run_id": "RUN-BG0776", "started_at": "2026-09-26T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": [],
        "handoff": None, "report": "RPT0001", "sprint_goal": "sign names its principal",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"},
    }
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")


def _read(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())


def _sign(root: Path, principal: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["sign", "--report", "RPT0001", "--principal", principal,
                          "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class SignPrincipalTests(unittest.TestCase):

    def test_a_principal_that_normalises_to_empty_is_refused(self) -> None:
        """Mutant: check the raw string for emptiness (`principal.strip()`) before the id
        normaliser runs, so `-` and `_` pass the guard and the run is sealed unnamed."""
        for principal in ("-", "  ", "_"):
            with self.subTest(principal=principal), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _closed_run(root)
                rc, out, err = _sign(root, principal)
                self.assertNotEqual(0, rc, out)
                self.assertIn(f"sign REFUSED: --principal {principal!r}", err)
                state = _read(root)
                self.assertEqual("running", state["outcome"])
                self.assertIsNone(state.get("signature"))

    def test_a_real_principal_still_seals(self) -> None:
        """Mutant: a guard that refuses every principal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _closed_run(root)
            rc, out, err = _sign(root, "Darren Benson")
            self.assertEqual(0, rc, err)
            self.assertIn("signed by Darren Benson", out)
            state = _read(root)
            self.assertEqual("goal-reached", state["outcome"])
            self.assertEqual("Darren Benson", state["signature"]["principal"])


def _decisions(root: Path) -> tuple[str, str]:
    """A decisions log written through `decisions.add`: one authority since superseded and the
    accepted one that replaced it. Returns (accepted, superseded)."""
    decisions = loader.load_script("decisions")
    old = decisions.add(root, "the agent may sign RUN-BG0776", "an early authority")["id"]
    new = decisions.add(root, "the agent may sign RUN-BG0776 for the operator", "replaces it",
                        supersedes=old)["id"]
    return new, old


def _sign_as(root: Path, *extra: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["sign", "--report", "RPT0001", "--principal", "Darren Benson", *extra,
                          "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class DelegatedSignatureTests(unittest.TestCase):
    """US1291: a signature entered under delegation names the accepted decision that authorises
    it, and the signature block records both; one the operator enters needs neither."""

    def test_a_delegated_signature_without_an_accepted_decision_is_refused(self) -> None:
        """AC1. MUTANTS: `--delegated` sealed with no decision; any id accepted, so one the log
        does not hold seals; any recorded id accepted, so the superseded one seals; the check
        placed after the seal writes."""
        for label, extra in (("no decision", ()), ("an id the log does not hold", ("D0099",)),
                             ("the superseded decision", None)):
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _closed_run(root)
                accepted, superseded = _decisions(root)
                named = ("--decision", superseded) if extra is None else (
                    ("--decision", *extra) if extra else ())
                rc, out, err = _sign_as(root, "--delegated", *named)
                self.assertNotEqual(0, rc, out + err)
                self.assertIn("sign REFUSED:", err)
                self.assertIn("accepted decision", err, "the refusal names no decision it needs")
                state = _read(root)
                self.assertEqual("running", state["outcome"])
                self.assertIsNone(state.get("signature"))
                self.assertNotIn("sealed", out)

    def test_a_delegated_signature_records_its_decision_in_the_signature_block(self) -> None:
        """AC2. MUTANTS: the block written without `delegated`, or without the decision id; the
        sealed line silent on the decision; the id recorded as typed rather than as the log
        spells it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _closed_run(root)
            accepted, _ = _decisions(root)
            rc, out, err = _sign_as(root, "--delegated", "--decision", accepted.lower())
            self.assertEqual(0, rc, out + err)
            state = _read(root)
            self.assertEqual("goal-reached", state["outcome"])
            signature = state["signature"]
            self.assertEqual("Darren Benson", signature["principal"])
            self.assertIs(True, signature.get("delegated"))
            self.assertEqual(accepted, signature.get("decision"))
            sealed = next(ln for ln in out.splitlines() if ln.startswith("sealed "))
            self.assertIn(accepted, sealed, "the sealed line does not name the decision")
            self.assertIn("delegated", sealed)

    def test_an_undelegated_signature_seals_without_a_decision(self) -> None:
        """AC3. MUTANTS: every signature asked for a decision; an undelegated signature written
        with `delegated` or a `decision` key; a decision named without `--delegated` recorded
        as a delegation instead of refused."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _closed_run(root)
            rc, out, err = _sign_as(root)
            self.assertEqual(0, rc, out + err)
            signature = _read(root)["signature"]
            self.assertEqual("Darren Benson", signature["principal"])
            self.assertNotIn("delegated", signature)
            self.assertNotIn("decision", signature)
            self.assertNotIn("delegated", out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _closed_run(root)
            accepted, _ = _decisions(root)
            rc, out, err = _sign_as(root, "--decision", accepted)
            self.assertNotEqual(0, rc, out + err)
            self.assertIn("sign REFUSED: --decision", err)
            self.assertIsNone(_read(root).get("signature"))


if __name__ == "__main__":
    unittest.main()
