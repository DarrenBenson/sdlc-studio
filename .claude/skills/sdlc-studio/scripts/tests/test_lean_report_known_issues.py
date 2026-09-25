"""US0951: a clean run's report hands over no false known issues.

Driven through the shipped entry points on a fresh `init run` project, which is schema v3 and
so mints ULID ids: one story with a lean criterion, one independent APPROVE, a goal verdict of
achieved, then `sprint.py close`. Each fixture tree cleans itself up.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

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


def _delivered_project(root: Path) -> str:
    """A fresh project whose one story is green, independently APPROVEd and at Review, with
    the run open and nothing yet closed. Returns the story id."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], env=gitutil.git_env(),
                   check=True, capture_output=True)
    _ok(root, "init.py", "run")
    # The review is stood down, as the measured premise ran it: a fresh project seeds no seat
    # card, so a briefed verdict is a separate gap (G1), not this story's.
    cfg = root / "sdlc-studio" / ".config.yaml"
    cfg.write_text(cfg.read_text(encoding="utf-8")
                   + "\nreview:\n  require_brief_provenance: false\n", encoding="utf-8")
    _commit(root, "init")
    epic = _ID.search(_ok(root, "artifact.py", "new", "--type", "epic",
                          "--title", "Widgets")).group(1)
    story = _ID.search(_ok(root, "artifact.py", "new", "--type", "story", "--title", "A widget",
                           "--epic", epic, "--points", "1", "--affects", "src/widget.py",
                           "--ac", "the widget exists",
                           "--verify", "shell test -f src/widget.py")).group(1)
    _commit(root, "story")
    _ok(root, "transition.py", "set", story, "Ready")
    _commit(root, "ready")
    _ok(root, "sprint.py", "plan", "--stories", "Ready", "--sprint-goal", "A widget ships",
        "--write", "--no-fetch")
    _commit(root, "plan")
    (root / "src").mkdir()
    (root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
    _commit(root, "widget")
    _ok(root, "verify_ac.py", "run", "--id", story)
    _ok(root, "critic.py", "record", "--unit", story, "--verdict", "APPROVE",
        "--reviewer", "qa seat", "--author", "engineering seat")
    _ok(root, "transition.py", "set", story, "Review")
    _commit(root, "delivered")
    return story


def _close(root: Path) -> dict:
    """`sprint.py close` as an operator runs it: the first call scaffolds the retro and records
    the verdict, the second files the report. Returns the filed report's JSON."""
    _cli(root, "sprint.py", "close", "--goal-verdict", "achieved", "--note", "it shipped")
    retro = next((root / "sdlc-studio" / "retros").glob("RETRO0001-*.md"))
    text = retro.read_text(encoding="utf-8")
    for slot, words in (("keep", "small batches"), ("stop", "nothing"), ("try", "more")):
        text = text.replace("{{" + slot + "}}", words)
    retro.write_text(text, encoding="utf-8")
    _commit(root, "retro")
    _ok(root, "sprint.py", "close", "--retro", "RETRO0001")
    state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
    report = root / "sdlc-studio" / "reports" / f"{state['report']}.json"
    return json.loads(report.read_text(encoding="utf-8"))


def _section(report: dict, key: str) -> dict | None:
    return next((s for s in report["sections"] if s["key"] == key), None)


def _page(root: Path) -> str:
    return next((root / "sdlc-studio" / "reports").glob("RPT*-*.md")).read_text(encoding="utf-8")


class KnownIssuesTests(unittest.TestCase):
    """One delivered project, closed once for the clean run and once, on a copy, with a red
    gate lane - the close is the expensive step, so each tree closes exactly once."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name)
        cls.clean = base / "clean"
        cls.clean.mkdir()
        cls.story = _delivered_project(cls.clean)
        # The control: the same delivered tree with one real defect in it - a second artefact
        # claiming the story's id, which the gate's duplicate-id lane refuses.
        cls.red = base / "red"
        shutil.copytree(cls.clean, cls.red, symlinks=True)
        dup = next((cls.red / "sdlc-studio" / "stories").glob(f"{cls.story}-*.md"))
        shutil.copy(dup, dup.with_name(f"{cls.story}-a-second-widget.md"))
        _commit(cls.red, "a duplicate id")
        cls.clean_report = _close(cls.clean)
        cls.red_report = _close(cls.red)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_a_clean_run_hands_over_no_close_gap(self) -> None:
        """AC1. Mutants: read the retro's Batch with the v2-only id grammar; hold an unmetered
        cost row outstanding; report the not-applicable verb-surface row; ignore the per-unit
        APPROVE in the closing-review row; or blame the work for the review anchor a first
        close has yet to write. Each hands a clean run a close gap again."""
        issues = _section(self.clean_report, "known_issues")
        self.assertEqual([], [row["issue_detail"]["value"] for row in issues["rows"]],
                         "a clean run handed over known issues")
        scan = issues["figures"]["findings_scan"]["value"]
        self.assertIn("0 close gap(s)", scan)
        self.assertIn("0 carried unit(s)", scan)
        page = _page(self.clean)
        handed = page.split("## Known issues handed over", 1)[1].split("\n## ", 1)[0]
        self.assertIn("No open finding, close gap or carried unit is recorded.", handed)

    def test_unmeasurable_rows_go_to_the_appendix_and_a_red_lane_stays(self) -> None:
        """AC2. Mutants: relabel the unmeasured cost row `answered` (it leaves the appendix),
        keep it outstanding (it returns under known issues), or drop gate lanes from the known
        issues (the control goes quiet)."""
        sr = loader.load_script("sprint_report")
        self.assertNotIn("mutation-survivors", [item["id"] for item in sr.CHECKLIST])
        self.assertFalse(hasattr(sr, "_ck_mutation_survivors"), "the resolver survived")
        proc = subprocess.run(
            [sys.executable, "-B", str(_SCRIPTS / "sprint_report.py"), "--root", str(self.red),
             "checklist", "--id", "RETRO0001", "--format", "json"],
            env=gitutil.git_env(), capture_output=True, text=True, timeout=300)
        ck = json.loads(proc.stdout)
        rows = {item["id"]: item for item in ck["items"]}
        # Outside the skill's own repository the verb-surface row does not apply: omitted.
        self.assertNotIn("doc-surface", rows)
        # Nothing metered this run's cost, so the row cannot be measured - and says so.
        self.assertEqual(sr.UNMEASURABLE, rows["cost"]["state"])
        self.assertNotIn("cost", ck["outstanding"])
        # The control: the red lane is still handed over, and only the unmeasured row moved.
        issues = [row["issue_detail"]["value"]
                  for row in _section(self.red_report, "known_issues")["rows"]]
        self.assertTrue([i for i in issues if i.startswith("duplicate-id:")],
                        f"the red gate lane was not handed over: {issues}")
        self.assertFalse([i for i in issues if i.startswith("cost:")], issues)
        # ...and a lane the close failed only on its own paperwork (the review anchor it has
        # yet to write) is not handed over beside the real one.
        self.assertFalse([i for i in issues if i.startswith("review-current:")], issues)
        page = _page(self.red)
        handed = page.split("## Known issues handed over", 1)[1].split("\n## ", 1)[0]
        self.assertIn("duplicate-id", handed)
        self.assertNotIn("cost:", handed)
        appendix = page.split("## Appendix", 1)[1]
        unmeasured = appendix.split("### Not measured", 1)[1]
        self.assertRegex(unmeasured, r"\| cost: [^|]+\| not measured \|",
                         "the unmeasured row is not in the appendix as `not measured`")

    def test_goal_judged_reads_the_recorded_verdict(self) -> None:
        """AC3. Mutant: `_sprint_goal` reads only the live run state - the verdict is then
        lost the moment the next run opens and archives this one."""
        sr = loader.load_script("sprint_report")
        live = {item["id"]: item for item in sr.checklist(self.clean, "RETRO0001")["items"]}
        self.assertEqual((sr.RAN, "achieved"),
                         (live["goal-judged"]["state"], live["goal-judged"]["value"]))
        # The next run opens: this one is archived and the live record belongs to another.
        rs = loader.load_script("sprint").run_state
        rs.archive(self.clean)
        path = self.clean / "sdlc-studio" / ".local" / "run-state.json"
        nxt = {**json.loads(path.read_text(encoding="utf-8")), "run_id": "RUN-NEXT",
               "batch": ["US-01ZZZZZZ"], "sprint_goal": "the next thing",
               "sprint_goal_verdict": None}
        path.write_text(json.dumps(nxt), encoding="utf-8")
        later = {item["id"]: item for item in sr.checklist(self.clean, "RETRO0001")["items"]}
        self.assertEqual((sr.RAN, "achieved"),
                         (later["goal-judged"]["state"], later["goal-judged"]["value"]))


if __name__ == "__main__":
    unittest.main()
