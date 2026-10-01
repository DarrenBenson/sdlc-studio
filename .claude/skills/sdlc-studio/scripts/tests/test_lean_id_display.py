"""BG0825: an id is printed in its file's spelling, never as its comparison key.

`sdlc_md.norm_id` is a comparison key: it drops the dash a schema v3 id is spelled with
(`US-01ABCDEF` -> `US01ABCDEF`). Printed as the id - in `critic.py brief`'s record footer, the
plan's delivery-mode line, the carried-at-cap bug's title and the signed report's issue table -
it names an id no file carries, so a reader searching for it finds nothing. The close drifted the
other way for a sequential meta id: it printed `RETRO-0001` for the file `RETRO0001-x.md`.

Every test drives the shipped entry points in a throwaway tree and reads nothing of this
repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

UNIT, OTHER = "US-01ABCDEF", "US-01ABCDEG"


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300, check=False)


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _v3_project(root: Path) -> None:
    """A schema v3 project holding two Ready stories, each with its own source file."""
    _w(root, "sdlc-studio/.config.yaml", "schema_version: 3\n")
    for uid in (UNIT, OTHER):
        src = f"src/{uid.lower()}.py"
        _w(root, src, "x = 1\n")
        _w(root, f"sdlc-studio/stories/{uid}-a-story.md",
           f"# {uid}: a story\n\n> **Status:** Ready\n> **Epic:** EP-01ABCDEA\n> **Points:** 2\n"
           f"> **Affects:** {src}\n\n## Acceptance Criteria\n\n### AC1: it works\n\n"
           f"- **Verify:** shell test -f {src}\n")


def _open_run(root: Path, batch: list[str]) -> None:
    """A run record holding `batch` as run state stores it: normalised comparison keys."""
    _w(root, "sdlc-studio/.local/run-state.json", json.dumps(
        {"schema": 1, "run_id": "RUN-ID0825", "started_at": "2026-10-01T00:00:00Z",
         "ended_at": None, "outcome": "running", "goal": "done", "handoff": None,
         "sprint_goal": "ids read as their files do", "batch": batch, "batch_changes": []}))


class IdDisplayTests(unittest.TestCase):
    """AC1-AC2."""

    def test_ulid_ids_print_in_file_spelling(self) -> None:
        """AC1. MUTANTS: (1) the brief footer prints `norm_id(args.unit)`; (2) the delivery-mode
        offer groups `norm_id` keys; (3) `carry_at_cap` titles the bug with `norm_id(unit)`; (4)
        the report's carried-unit row writes the ledger's comparison key. Each prints
        `US01ABCDEF`, an id no file carries."""
        key = "US01ABCDEF"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v3_project(root)
            brief = _cli(root, "critic.py", "brief", "--unit", UNIT, "--seat", "qa")
            self.assertEqual(0, brief.returncode, brief.stdout + brief.stderr)
            footer = next((ln for ln in brief.stderr.splitlines() if "critic.py record" in ln),
                          "")
            self.assertIn(f"--unit {UNIT} ", footer, f"the brief's footer:\n{brief.stderr}")

            worklist = _w(root, "worklist.txt", f"{UNIT}\n{OTHER}\n")
            plan = _cli(root, "sprint.py", "plan", "--worklist", str(worklist), "--no-fetch",
                        "--skip-personas")
            mode = "\n".join(ln for ln in plan.stdout.splitlines()
                             if "delivery mode" in ln or "worktree group" in ln)
            self.assertIn(f"[{UNIT}]", mode, f"the delivery-mode lines:\n{plan.stdout}")
            self.assertNotIn(key, mode, mode)

            _open_run(root, [key])
            critic = importlib.import_module("critic")
            bug = critic.carry_at_cap(root, UNIT, {"round": 2, "reviewer": "qa seat",
                                                   "issues": "[new] it does not work"})
            self.assertTrue(bug, "premise: the open run held the unit, so it was carried")
            found = next((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            title = found.read_text(encoding="utf-8").splitlines()[0]
            self.assertIn(f"{UNIT} did not converge", title, title)
            self.assertNotIn(key, found.read_text(encoding="utf-8"))

            _open_run(root, [key])                     # the unit, carried undelivered
            # An open finding raised inside the run, stamped well before the page's window ends.
            _w(root, "sdlc-studio/bugs/BG-01ABCDEH-a-finding.md",
               "# BG-01ABCDEH: a finding\n\n> **Status:** Open\n> **Severity:** Medium\n"
               "> **Created:** 2026-10-01\n> **Raised-in-batch:** none open - raised outside a "
               "delivery batch, 2026-10-01T06:00:00Z\n")
            _w(root, "sdlc-studio/retros/RETRO0001-ids.md",
               "# RETRO-0001: ids\n\n> **Date:** 2026-10-01\n> **Run:** RUN-ID0825\n"
               f"> **Batch:** {UNIT}\n\n## Delivered\n\n- nothing\n")
            report = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "sprint_report.py"), "--root", str(root),
                 "build", "--id", "RETRO0001", "--format", "json"],
                cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)
            self.assertEqual(0, report.returncode, report.stdout + report.stderr)
            rows = next(s["rows"] for s in json.loads(report.stdout)["sections"]
                        if s["key"] == "known_issues")
            ids = [r["issue_id"]["value"] for r in rows]
            self.assertIn(UNIT, ids, f"the issue table:\n{ids}")
            self.assertIn("BG-01ABCDEH", ids, f"premise: the open finding is on the page: {ids}")
            keys = [i for i in ids if re.fullmatch(r"[A-Z]{2,5}[0-9A-HJKMNP-TV-Z]{8,}", i)]
            self.assertEqual([], keys, f"the issue table prints comparison keys: {ids}")

    def test_a_page_printing_file_spellings_still_replays(self) -> None:
        """A signed page's open-finding rows are replayed by comparison key, so a page that
        prints `BG-01ABCDEF` and one signed before, printing `BG01ABCDEF`, both replay.
        MUTANT: key the replay by the printed id - the new page's rows are never found."""
        sprint_report = importlib.import_module("sprint_report")
        for printed in ("BG-01ABCDEF", "BG01ABCDEF"):
            page = {"sections": [{"key": "known_issues", "rows": [
                {"issue_id": {"value": printed}, "issue_priority": {"value": "Medium"}}]}]}
            with self.subTest(printed=printed):
                self.assertIn("BG01ABCDEF", sprint_report._page_readings(page)["findings"])

    def test_the_scaffolded_retro_id_matches_its_file(self) -> None:
        """AC2. MUTANT: print and record `meta_new`'s display id (`RETRO-0001`) rather than the
        id the scaffolded file carries."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v3_project(root)
            _open_run(root, ["US01ABCDEF"])
            r = _cli(root, "sprint.py", "close")
            out = r.stdout + r.stderr
            [retro] = list((root / "sdlc-studio" / "retros").glob("RETRO*.md"))
            self.assertTrue(retro.name.startswith("RETRO0001-"), retro.name)
            self.assertIn("close: retro RETRO0001 ", out, out)
            self.assertIn("sprint.py close --retro RETRO0001", out, out)
            self.assertNotIn("RETRO-0001", out, out)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual("RETRO0001", state.get("scaffolded_retro"))


if __name__ == "__main__":
    unittest.main()
