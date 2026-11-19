"""`sprint sign` writes the velocity row for the run's own retro, and for no other.

After the seal, the signature re-runs `retro.py accuracy --write` so the velocity row counts the
units the seal has just made terminal. It took the retro from the run state's
`scaffolded_retro` and fell back to a fixed first id, so a run whose retro was made with
`artifact.py new --type retro` and named to the close with `--retro` rewrote the first retro of
an unrelated run, its accuracy block and its velocity row, whatever `sign --retro` said.

Pinned here through `sprint.main`, the shipped entry point, in throwaway trees whose meter reads
nothing (HOME and the transcript store point inside the fixture):

* `sign --retro` names the retro written, and every other retro is left byte for byte (AC1);
* without `--retro`, the retro the close was given is written, and a run that records no retro
  writes none and says so, naming `--retro` (AC2).

Run from the repo root:
    pytest .claude/skills/sdlc-studio/scripts/tests/test_sign_retro.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_close_cost_regression as ccr  # noqa: E402 - a tree the shipped close can close
import test_meter_reads_true as meter  # noqa: E402

PRINCIPAL = "Pat Operator"


def _out(fn, *args) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = fn(*args)
    return rc, out.getvalue(), err.getvalue()


def _row(root: Path, retro: str) -> str | None:
    """The VELOCITY.md row keyed by `retro`, or None."""
    text = (root / "sdlc-studio" / "retros" / "VELOCITY.md").read_text(encoding="utf-8")
    return next((ln for ln in text.splitlines() if ln.startswith(f"| {retro} |")), None)


class SignRetroTests(ccr._Case):
    def setUp(self) -> None:
        super().setUp()
        env = unittest.mock.patch.dict(os.environ, {
            "HOME": str(self.tmp / "home"),
            self.rs.TRANSCRIPTS_ENV: str(self.tmp / "no-store")})
        env.start()
        self.addCleanup(env.stop)
        for name in meter._live("lib.token_meters").selection_variables():
            os.environ.pop(name, None)
        self.accuracy_ids: list[str] = []

    def _bare(self, name: str, state: dict) -> Path:
        """A tree holding RETRO0001 and RETRO0002, RETRO0001's accuracy block and velocity row
        written with a recorded elapsed (which a rewrite from the run state would lose), and a
        run the close prepared whose state is `state` over an empty batch."""
        root = self.tmp / name
        stories, retros = root / "sdlc-studio" / "stories", root / "sdlc-studio" / "retros"
        stories.mkdir(parents=True)
        retros.mkdir(parents=True)
        for n in (1, 2):
            (stories / f"US010{n}-x.md").write_text(
                f"# US010{n}: x\n\n> **Status:** Done\n> **Points:** 2\n\n## Acceptance Criteria"
                "\n\n### AC1: a\n\n- **Verify:** shell true\n", encoding="utf-8")
            (retros / f"RETRO000{n}-r{n}.md").write_text(
                f"# RETRO-000{n}: r{n}\n\n> **Date:** 2026-09-2{n}\n> **Batch:** US010{n}\n\n"
                "## Delivered\n\n- it shipped\n", encoding="utf-8")
        rc, said = self.sprint._run_cli(self.retro.main, [
            "--root", str(root), "accuracy", "--id", "RETRO0001", "--write",
            "--elapsed-hours", "172.9"])
        self.assertEqual(rc, 0, said)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True, exist_ok=True)
        (local / "run-state.json").write_text(json.dumps({
            "schema": 1, "run_id": f"RUN-{name.upper()}", "started_at": "2026-11-18T21:04:57Z",
            "ended_at": None, "outcome": "running", "goal": "done", "batch": [],
            "handoff": None, "report": "RPT0001", "sprint_goal": "the sign writes its own retro",
            "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}, **state}),
            encoding="utf-8")
        return root

    def _sign(self, root: Path, report: str = "RPT0001", *extra: str) -> tuple[int, str, str]:
        real = self.sprint._run_cli

        def spy(module_main, argv):
            if "accuracy" in argv:
                self.accuracy_ids.append(argv[argv.index("--id") + 1])
            return real(module_main, argv)

        with unittest.mock.patch.object(self.sprint, "_run_cli", spy):
            return _out(self.sprint.main, ["sign", "--report", report, "--principal", PRINCIPAL,
                                           *extra, "--root", str(root)])

    def test_sign_writes_the_named_retro_and_leaves_retro0001(self) -> None:
        """AC1. MUTANTS: the fixed first-id fallback kept (RETRO0001 rewritten, its elapsed
        lost); `--retro` read but after `scaffolded_retro`; `--retro` parsed and never passed to
        the cascade (the run names no retro, so nothing is written)."""
        root = self._bare("named", {})
        retros = root / "sdlc-studio" / "retros"
        first = (retros / "RETRO0001-r1.md").read_bytes()
        first_row = _row(root, "RETRO0001")
        self.assertIn("172.9", first.decode(), "the fixture records RETRO0001's elapsed")
        self.assertIsNone(_row(root, "RETRO0002"))
        rc, out, err = self._sign(root, "RPT0001", "--retro", "RETRO0002")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.accuracy_ids, ["RETRO0002"], out + err)
        self.assertIn("<!-- accuracy:end -->",
                      (retros / "RETRO0002-r2.md").read_text(encoding="utf-8"),
                      "RETRO0002's accuracy block was not written")
        self.assertIsNotNone(_row(root, "RETRO0002"), "RETRO0002's velocity row was not written")
        self.assertIn("sign: velocity row recorded", out)
        self.assertEqual((retros / "RETRO0001-r1.md").read_bytes(), first,
                         "the sign rewrote RETRO0001")
        self.assertEqual(_row(root, "RETRO0001"), first_row, "the sign rewrote RETRO0001's row")
        # `--retro` is read first, ahead of any retro the run state names.
        self.assertEqual("RETRO0002", self.sprint._sign_retro(
            {self.sprint.CLOSE_RETRO: "RETRO0003", "scaffolded_retro": "RETRO0004"}, "RETRO0002"))

    def test_sign_uses_the_close_retro_and_writes_none_when_unknown(self) -> None:
        """AC2. MUTANTS: the close not recording the retro it was given (the sign writes none);
        the sign not reading it; the fixed first-id fallback kept for a run that records no
        retro; a run with no retro silently writing nothing, or refusing the seal."""
        # A run the shipped close prepared with `--retro RETRO0007`, beside an unrelated RETRO0001.
        root = self.tree({"RETRO0001": "800,000"})
        old = root / "sdlc-studio" / "retros" / "RETRO0001-old.md"
        old.write_text("# RETRO-0001: old\n\n> **Date:** 2026-09-29\n> **Batch:** US0001\n\n"
                       "## Delivered\n\n- an unrelated run\n", encoding="utf-8")
        before = old.read_bytes()
        rc, out = self.close(root, real=())
        self.assertEqual(rc, 0, out)
        report = self.rs.read(root).get("report")
        self.assertTrue(report, out)
        rc, out, err = self._sign(root, report)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.accuracy_ids, [ccr.RETRO], "the sign wrote the close's retro")
        self.assertIn("sign: velocity row recorded", out)
        self.assertIn("<!-- accuracy:end -->",
                      (root / "sdlc-studio" / "retros" / f"{ccr.RETRO}-cost.md").read_text(
                          encoding="utf-8"))
        self.assertEqual(old.read_bytes(), before, "the sign rewrote RETRO0001")
        # Without `--retro`, the close's retro is read ahead of the one it scaffolded.
        self.assertEqual("RETRO0003", self.sprint._sign_retro(
            {self.sprint.CLOSE_RETRO: "RETRO0003", "scaffolded_retro": "RETRO0004"}, None))

        # A run that records no retro at all: sealed, no retro written, and the sign says so.
        self.accuracy_ids.clear()
        bare = self._bare("unknown", {})
        retros = bare / "sdlc-studio" / "retros"
        snapshot = {p.name: p.read_bytes() for p in retros.iterdir()}
        rc, out, err = self._sign(bare)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.rs.read(bare).get("outcome"), "goal-reached", "the seal held")
        self.assertEqual(self.accuracy_ids, [], "a run naming no retro wrote one")
        self.assertEqual({p.name: p.read_bytes() for p in retros.iterdir()}, snapshot,
                         "a retro or VELOCITY.md changed")
        said = " ".join(err.split())
        self.assertIn("velocity row NOT recorded", said)
        self.assertIn("--retro", said, "the sign names the remedy")


if __name__ == "__main__":
    unittest.main()
