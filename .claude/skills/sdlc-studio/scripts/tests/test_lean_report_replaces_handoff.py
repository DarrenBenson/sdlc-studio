"""US0967: the close writes no handoff; the next plan reads the last signed report's carried work.

The signed report's "Known issues handed over" section already lists every open finding raised in
the run and every carried unit. The handoff restated it and could disagree with it: after
RUN-01M3T8N1 the plan read the handoff and said `nothing carried over` while RPT0013 handed over
three findings. So the close and `sign` write no handoff, the plan's last-run notice and
`--worklist RPT<n>` read the last signed report, and a run ended by `stop --force` - which files
no report - has its waived units named from the run record.

Every test drives the shipped entry points in a throwaway project and reads nothing of this
repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
_ID = re.compile(r"created (\S+)")


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)


def _ok(root: Path, script: str, *args: str) -> str:
    proc = _cli(root, script, *args)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} exited {proc.returncode}:\n"
                             f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def _commit(root: Path, message: str) -> None:
    for argv in (["add", "-A"], ["commit", "-q", "--allow-empty", "-m", message]):
        subprocess.run(["git", "-C", str(root), *argv], env=gitutil.git_env(), check=True,
                       capture_output=True)


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _story(root: Path, sid: str, status: str = "Ready") -> None:
    _w(root, f"src/{sid.lower()}.py", "x = 1\n")
    _w(root, f"sdlc-studio/stories/{sid}-x.md",
       f"# {sid}: x\n\n> **Status:** {status}\n> **Epic:** EP0001\n> **Points:** 2\n"
       f"> **Affects:** src/{sid.lower()}.py\n\n## Acceptance Criteria\n\n### AC1: it works\n\n"
       f"- **Verify:** shell true\n")


def _bug(root: Path, bid: str) -> None:
    _w(root, f"src/{bid.lower()}.py", "x = 1\n")
    _w(root, f"sdlc-studio/bugs/{bid}-x.md",
       f"# {bid}: x\n\n> **Status:** Open\n> **Severity:** Medium\n> **Points:** 2\n"
       f"> **Affects:** src/{bid.lower()}.py\n\n## Acceptance Criteria\n\n### AC1: it works\n\n"
       f"- **Verify:** shell true\n")


def _report(root: Path, rid: str, run_id: str, issue_ids: list[str], signed: bool) -> None:
    """A filed report's JSON of record, holding only what the plan reads: its run, whether it is
    signed, and the issue ids of its `Known issues handed over` rows."""
    rows = [{"issue_id": {"key": "issue_id", "value": i, "source": "fixture"},
             "issue_priority": {"key": "issue_priority", "value": "Medium", "source": "fixture"},
             "issue_detail": {"key": "issue_detail", "value": "d", "source": "fixture"}}
            for i in issue_ids]
    signature = ({"principal": "the operator", "signed_at": "2026-10-01T00:00:00Z",
                  "report": rid, "fingerprint": "f"} if signed else {})
    _w(root, f"sdlc-studio/reports/{rid}.json", json.dumps(
        {"schema": 1, "report_id": rid, "run_id": run_id, "signature": signature,
         "sections": [{"key": "known_issues", "title": "Known issues handed over",
                       "figures": {}, "rows": rows}]}))


def _plan(root: Path, *args: str) -> subprocess.CompletedProcess:
    return _cli(root, "sprint.py", "plan", *args, "--no-fetch", "--skip-personas")


class ReportReplacesHandoffTests(unittest.TestCase):
    """AC1-AC3."""

    def test_the_close_and_sign_write_no_handoff(self) -> None:
        """AC1. MUTANTS: (1) keep the close's `handoff` chain step - it generates HO0001, its
        worklist and `state["handoff"]`; (2) keep sign's refresh of a recorded handoff; (3) keep
        the checklist's `handoff` row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)], env=gitutil.git_env(),
                           check=True, capture_output=True)
            _ok(root, "init.py", "run")
            _commit(root, "init")
            epic = _ID.search(_ok(root, "artifact.py", "new", "--type", "epic",
                                  "--title", "Widgets")).group(1)
            units = [_ID.search(_ok(root, "artifact.py", "new", "--type", "story", "--title",
                                    title, "--epic", epic, "--points", "1", "--affects", path,
                                    "--ac", "it exists", "--verify", f"shell test -f {path}"))
                     .group(1) for title, path in (("A widget", "src/widget.py"),
                                                   ("A gadget", "src/gadget.py"))]
            for uid in units:
                _ok(root, "transition.py", "set", uid, "Ready")
            _commit(root, "stories")
            _ok(root, "sprint.py", "plan", "--stories", "Ready", "--sprint-goal",
                "A widget ships", "--write", "--no-fetch")
            _commit(root, "plan")
            delivered, carried = units
            (root / "src").mkdir()
            (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
            _commit(root, "widget")
            _ok(root, "verify_ac.py", "run", "--id", delivered)
            _ok(root, "critic.py", "record", "--unit", delivered, "--verdict", "APPROVE",
                "--reviewer", "qa seat", "--author", "engineering seat")
            _ok(root, "transition.py", "set", delivered, "Review")
            # The carried unit: rejected at the round cap, which files its findings as an open
            # bug raised inside the run and carries the unit out of the batch.
            for _round in (1, 2):
                _ok(root, "critic.py", "record", "--unit", carried, "--verdict", "REJECT",
                    "--reviewer", "qa seat", "--author", "engineering seat",
                    "--issues", "[new] the gadget is missing")
            # The carry stamps its bug to the second, and the report places a finding in the
            # half-open window [start, end): a close in the same second as the carry would leave
            # the finding off the page. A real close comes later than the carry, so the clock is
            # let past the carry's second rather than slept a fixed time.
            carried_at = int(time.time())
            while int(time.time()) <= carried_at:
                time.sleep(0.02)
            _commit(root, "delivered")
            handoffs = root / "sdlc-studio" / "handoffs"
            before = sorted(p.name for p in handoffs.rglob("*")) if handoffs.exists() else []
            _cli(root, "sprint.py", "close", "--goal-verdict", "partial", "--note", "one carried")
            retro = next((root / "sdlc-studio" / "retros").glob("RETRO*-*.md"))
            text = retro.read_text(encoding="utf-8")
            for slot, words in (("keep", "small batches"), ("stop", "nothing"), ("try", "more")):
                text = text.replace("{{" + slot + "}}", words)
            retro.write_text(text, encoding="utf-8")
            _commit(root, "retro")
            retro_id = retro.name.split("-", 1)[0]
            _ok(root, "sprint.py", "close", "--retro", retro_id)
            _commit(root, "closed")
            signed = _ok(root, "sprint.py", "sign", "--principal", "the operator")
            self.assertIn("sealed", signed, "premise: the run was not signed:\n" + signed)
            stored = json.loads((root / "sdlc-studio" / "reports" / "RPT0001.json")
                                .read_text(encoding="utf-8"))
            rows = next(s["rows"] for s in stored["sections"] if s["key"] == "known_issues")
            self.assertTrue(any(r["issue_id"]["value"].startswith("BG") for r in rows),
                            "premise: the report hands over no open finding raised in the run")

            after = sorted(p.name for p in handoffs.rglob("*")) if handoffs.exists() else []
            self.assertEqual(before, after, "the close or sign wrote under sdlc-studio/handoffs/")
            self.assertFalse((root / "sdlc-studio" / ".local" / "handoff-worklist.txt").exists(),
                             "a handoff worklist was written")
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertIsNone(state.get("handoff"), "run state records a handoff")
            r = subprocess.run([sys.executable, "-B", str(_SCRIPTS / "sprint_report.py"), "--root",
                                str(root), "checklist", "--id", retro_id, "--format", "json"],
                               cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                               timeout=300)   # `--root` is the script's own, before the verb
            items = [i["id"] for i in json.loads(r.stdout)["items"]]
            self.assertIn("known-issues", items, "premise: the checklist was read")
            self.assertNotIn("handoff", items, "the checklist still lists a handoff step")

    def test_the_plan_reads_the_signed_reports_handed_over_ids(self) -> None:
        """AC2. MUTANTS: (1) the notice reads `state["handoff"]` only - it names nothing; (2) read
        the newest report whether signed or not - it names RPT0002; (3) take every row id,
        `checklist` close gap included - `--worklist` refuses an id with no artefact; (4) drop the
        report branch from `--worklist` - it reads `RPT0001` as a missing file."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bug(root, "BG0002")
            _story(root, "US0003")
            _report(root, "RPT0001", "RUN-A", ["BG0002", "checklist", "US0003"], signed=True)
            _report(root, "RPT0002", "RUN-B", ["BG0009"], signed=False)   # filed, not signed

            r = _plan(root, "--stories", "Ready")
            notice = next((ln for ln in r.stderr.splitlines() if "RPT0001" in ln), "")
            self.assertTrue(notice, "the plan's notice does not name the last signed report:\n"
                            + r.stderr)
            for uid in ("BG0002", "US0003"):
                self.assertIn(uid, notice, f"the notice does not name {uid}:\n{notice}")
            self.assertNotIn("RPT0002", r.stderr, "the notice read an unsigned report")
            self.assertNotIn("checklist", notice, "a close gap was named as plannable work")
            self.assertNotIn("since closed", notice,
                             "a close gap's row was counted as a handed-over item since closed")

            w = _plan(root, "--worklist", "RPT0001")
            self.assertEqual(0, w.returncode, w.stdout + w.stderr)
            self.assertIn("batch: 2 unit(s)", w.stdout, w.stdout)
            for uid in ("BG0002", "US0003"):
                self.assertIn(uid, w.stdout, f"--worklist RPT0001 did not plan {uid}")

    def test_a_forced_stops_waived_units_reach_the_next_plan(self) -> None:
        """AC3. MUTANTS: (1) read only the signed report - a forced stop files none, so nothing is
        named; (2) drop the `unanswered` read - US0004 is not named as waived."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, "US0004")
            opened = _plan(root, "--stories", "Ready", "--write")
            self.assertEqual(0, opened.returncode, opened.stdout + opened.stderr)
            stop = _cli(root, "sprint.py", "stop", "--force", "--reason", "x")
            self.assertEqual(0, stop.returncode, stop.stdout + stop.stderr)
            self.assertIn("US0004", stop.stderr, "premise: the stop waived nothing:\n" + stop.stderr)
            r = _plan(root, "--stories", "Ready")
            notice = next((ln for ln in r.stderr.splitlines() if "US0004" in ln), "")
            self.assertTrue(notice, "the next plan does not name the waived unit:\n" + r.stderr)
            self.assertIn("waived by the forced stop", notice, notice)


if __name__ == "__main__":
    unittest.main()
