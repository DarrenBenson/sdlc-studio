"""US1015: a verdict written by the context that edited the unit is a self-review, whatever seat
it names.

Every verdict writer shares `critic._write_verdict`, which reads the session's Claude Code
transcripts for the context that wrote the verdict (the issued file's writer) or ran the command
recording it (a flagged verdict). When that context edited one of the unit's Affects files before
it first received the brief, the row's `Source` cell carries `self-review:<path>`, the writer
warns naming the file, and `critic.is_independent` reads the row as no independent review, so the
close's review-coverage step and the signature's review bar both name the unit. Nothing new is
refused at Done.

Every case drives the shipped entry points in a throwaway project. The transcripts are fixtures
under a temporary folder named by `SDLC_STUDIO_TRANSCRIPTS`, in Claude Code's layout, so no case
reads or writes a real harness store.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
from test_critic_verdict_provenance import (  # noqa: E402
    SESSION, _block, _brief, _critic, _env, _show_line, _Transcripts)

SCRIPTS = Path(__file__).resolve().parent.parent
critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

REVIEWER, AUTHOR = "Tomas Reinholt (qa)", "engineering"
TOKEN = "self-review:src/unit.py"


def _project(root: Path, *units: str) -> None:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "unit.py").write_text("def u():\n    return 1\n", encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True, exist_ok=True)
    (seats / "qa.md").write_text("<!-- role: qa -->\n# Tomas Reinholt - QA amigo\n\ncharter\n",
                                 encoding="utf-8")
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    for unit in units:
        (stories / f"{unit}-unit.md").write_text(
            f"# {unit}: unit\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
            "> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
            "- **Verify:** shell true\n", encoding="utf-8")


def _worktree(folder: Path, agent: str, path: Path) -> None:
    """Give subagent `agent` the `worktreePath` Claude Code writes in its `.meta.json`."""
    meta = folder / SESSION / "subagents" / f"agent-{agent}.meta.json"
    meta.write_text(json.dumps({**json.loads(meta.read_text(encoding="utf-8")),
                                "worktreePath": str(path), "spawnedWithWorktree": True}),
                    encoding="utf-8")


def _rows(root: Path, unit: str) -> list[dict]:
    return [r for r in critic.read_verdicts(root) if r["unit"] == unit]


class SelfReviewByContextTests(unittest.TestCase):

    def _dirs(self, d: str) -> tuple[Path, Path, Path, Path]:
        base = Path(d)
        root, cwd, home = base / "proj", base / "elsewhere", base / "home"
        for p in (root, cwd, home):
            p.mkdir()
        return base, root, cwd, home

    def _record(self, cwd: Path, root: Path, argv: list[str], env: dict
                ) -> subprocess.CompletedProcess:
        r = _critic(cwd, *argv, "--reviewer", REVIEWER, "--author", AUTHOR,
                    "--root", str(root), env=env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return r

    def assertSelfReview(self, root: Path, unit: str, row: dict) -> None:
        self.assertIn(TOKEN, row["source"].split())
        self.assertFalse(critic.is_independent(row))
        self.assertIn(unit, sprint.uncovered_units(root, [unit]))
        self.assertTrue(sprint.seal_bar_unmet(root, unit))

    def assertIndependent(self, root: Path, unit: str, row: dict) -> None:
        self.assertNotIn("self-review:", row["source"])
        self.assertTrue(critic.is_independent(row))
        self.assertNotIn(unit, sprint.uncovered_units(root, [unit]))

    def test_the_editing_context_is_a_self_review_whatever_the_seat_name(self) -> None:
        """AC1. Mutants: independence judged on the reviewer and author strings alone (the row
        passes as independent); the token written but `is_independent` not reading the Source
        cell; `show` silent on the token. Control: the same strings with no edit by the writer
        (US0002, written by briefed agent r1) stay independent, so the check is not
        unconditional."""
        with tempfile.TemporaryDirectory() as d:
            base, root, cwd, home = self._dirs(d)
            _project(root, "US0001", "US0002")
            self.assertTrue(critic.independence(REVIEWER, AUTHOR)[0],
                            "premise: the strings alone read as independent")
            path, stem, argv = _brief(cwd, root, "US0001")
            written = _block("US0001", stem, "Looks right.\n")
            path.write_text(written, encoding="utf-8")
            t = _Transcripts(base / "t1", root)
            t.said(None, "00:00", "build and review the unit")
            t.tool(None, "00:01", "Edit", file_path=str(root / "src" / "unit.py"),
                   old_string="return 1", new_string="return 2")
            t.tool(None, "00:02", "Bash", command="python3 critic.py brief --unit US0001")
            t.said(None, "00:03", f"[tool_result] write your verdict to:\n{path}")
            t.tool(None, "00:04", "Write", file_path=str(path), content=written)
            rec = self._record(cwd, root, argv, _env(t.flush(), home))
            self.assertRegex(rec.stderr, r"WARNING: .*the main thread.*src/unit\.py")
            self.assertSelfReview(root, "US0001", _rows(root, "US0001")[-1])
            self.assertIn("self-review", _show_line(cwd, root, "US0001"))
            self.assertIn("src/unit.py", _show_line(cwd, root, "US0001"))

            path2, stem2, argv2 = _brief(cwd, root, "US0002")
            written2 = _block("US0002", stem2, "Looks right.\n")
            path2.write_text(written2, encoding="utf-8")
            t = _Transcripts(base / "t2", root)
            t.tool(None, "00:01", "Edit", file_path=str(root / "src" / "unit.py"),
                   old_string="return 1", new_string="return 2")
            t.tool(None, "00:02", "Agent", prompt=f"Review it. Verdict file: {path2}")
            t.said("r1", "00:03", f"Review it. Verdict file: {path2}")
            t.tool("r1", "00:04", "Write", file_path=str(path2), content=written2)
            rec = self._record(cwd, root, argv2, _env(t.flush(), home))
            self.assertNotIn("self-review", rec.stderr)
            self.assertIndependent(root, "US0002", _rows(root, "US0002")[-1])
            self.assertNotIn("self-review", _show_line(cwd, root, "US0002"))

    def test_the_one_call_close_from_the_editing_thread_records_a_self_review(self) -> None:
        """AC2. Mutants: the context check placed in `cmd_record` rather than `_write_verdict`,
        so `transition.py set --verdict` writes a bare `-`; the warning dropped; the transition
        refused for it. Control: the same command from a thread that edited nothing records an
        independent row."""
        with tempfile.TemporaryDirectory() as d:
            base, root, cwd, home = self._dirs(d)
            _project(root, "US0001", "US0002")
            for unit, edits in (("US0001", True), ("US0002", False)):
                argv = [str(SCRIPTS / "transition.py"), "set", unit, "--status", "Done",
                        "--verdict", "APPROVE", "--reviewer", REVIEWER, "--author", AUTHOR,
                        "--root", str(root)]
                t = _Transcripts(base / f"t-{unit}", root)
                if edits:
                    t.tool(None, "00:01", "Edit", file_path=str(root / "src" / "unit.py"),
                           old_string="return 1", new_string="return 2")
                t.tool(None, "00:02", "Bash", command=f"python3 {shlex.join(argv)}")
                # the unit's criteria pass, so the Done gate has nothing to refuse
                v = subprocess.run([sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "run",
                                    "--id", unit, "--root", str(root)], cwd=cwd,
                                   capture_output=True, text=True, timeout=300,
                                   env=_env(base, home), check=False)
                self.assertEqual(0, v.returncode, v.stdout + v.stderr)
                r = subprocess.run([sys.executable, "-B", *argv], cwd=cwd, capture_output=True,
                                   text=True, timeout=300, env=_env(t.flush(), home),
                                   check=False)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                story = next((root / "sdlc-studio" / "stories").glob(f"{unit}-*.md"))
                self.assertIn("> **Status:** Done", story.read_text(encoding="utf-8"))
                row = _rows(root, unit)[-1]
                if edits:
                    self.assertRegex(r.stderr, r"WARNING: .*src/unit\.py")
                    self.assertSelfReview(root, unit, row)
                else:
                    self.assertNotIn("self-review", r.stderr)
                    self.assertIndependent(root, unit, row)

    def test_a_reviewer_mutating_its_own_worktree_after_the_brief_stays_independent(
            self) -> None:
        """AC3. Mutant: every edit to an Affects path counted whatever its time, which brands
        r1 for the mutant it applied and reverted after it was briefed. Control: an author
        agent b1 whose edit came first is never the judged writer here."""
        with tempfile.TemporaryDirectory() as d:
            base, root, cwd, home = self._dirs(d)
            _project(root, "US0001")
            path, stem, argv = _brief(cwd, root, "US0001")
            written = _block("US0001", stem, "The mutant was killed.\n")
            path.write_text(written, encoding="utf-8")
            tree = root / ".claude" / "worktrees" / "agent-r1"
            t = _Transcripts(base / "t", root)
            t.said("b1", "00:00", "Build the unit")
            t.tool("b1", "00:01", "Edit", file_path=str(root / "src" / "unit.py"),
                   old_string="return 1", new_string="return 2")
            t.tool(None, "00:02", "Bash", command="python3 critic.py brief --unit US0001")
            t.said(None, "00:03", f"[tool_result] write your verdict to:\n{path}")
            t.said("r1", "00:04", f"Review it. Verdict file: {path}")
            t.tool("r1", "00:05", "Edit", file_path=str(tree / "src" / "unit.py"),
                   old_string="return 1", new_string="return 0")
            t.tool("r1", "00:06", "Edit", file_path=str(tree / "src" / "unit.py"),
                   old_string="return 0", new_string="return 1")
            t.tool("r1", "00:07", "Write", file_path=str(path), content=written)
            folder = t.flush()
            _worktree(folder, "r1", tree)
            rec = self._record(cwd, root, argv, _env(folder, home))
            self.assertNotIn("self-review", rec.stderr)
            row = _rows(root, "US0001")[-1]
            self.assertIn("agent:r1", row["source"].split())
            self.assertIndependent(root, "US0001", row)

    def test_an_edit_before_the_units_delivery_began_is_not_counted(self) -> None:
        """The floor: an edit made before `since` (the unit's In Progress span) belongs to an
        earlier delivery, so the same thread running the same command is no self-review; with no
        floor the edit counts. Mutant: `since` ignored."""
        with tempfile.TemporaryDirectory() as d:
            base, root, _cwd, home = self._dirs(d)
            _project(root, "US0001")
            vp = loader.load_script("critic").verdict_provenance
            argv = ["transition.py", "set", "US0001", "--verdict", "APPROVE"]
            t = _Transcripts(base / "t", root)
            t.tool(None, "00:01", "Edit", file_path=str(root / "src" / "unit.py"),
                   old_string="return 1", new_string="return 2")
            t.tool(None, "00:40", "Bash", command=f"python3 {shlex.join(argv)}")
            env = _env(t.flush(), home)
            self.assertEqual({"path": "src/unit.py", "context": "main"},
                             vp.self_review(root, ["src/unit.py"], [], argv=argv, env=env))
            self.assertIsNone(vp.self_review(root, ["src/unit.py"], [], argv=argv, env=env,
                                             since="2026-11-12T10:00:30Z"))

    def test_a_worktree_author_is_matched_to_the_units_files(self) -> None:
        """AC4. Mutant: the edit's absolute path compared with the repository-relative Affects,
        so a1's edit inside its worktree is never matched and its verdict passes as
        independent. Control: r1, which edited nothing, writing the next round's file records
        as independent."""
        with tempfile.TemporaryDirectory() as d:
            base, root, cwd, home = self._dirs(d)
            _project(root, "US0001")
            tree = root / ".claude" / "worktrees" / "agent-a1"
            path, stem, argv = _brief(cwd, root, "US0001")
            written = _block("US0001", stem, "My own work holds.\n")
            path.write_text(written, encoding="utf-8")
            t = _Transcripts(base / "t", root)
            t.said("a1", "00:00", "Build the unit in your worktree")
            t.tool("a1", "00:01", "Edit", file_path=str(tree / "src" / "unit.py"),
                   old_string="return 1", new_string="return 2")
            t.tool(None, "00:02", "Bash", command="python3 critic.py brief --unit US0001")
            t.said(None, "00:03", f"[tool_result] write your verdict to:\n{path}")
            t.tool("a1", "00:04", "Write", file_path=str(path), content=written)
            folder = t.flush()
            _worktree(folder, "a1", tree)
            rec = self._record(cwd, root, argv, _env(folder, home))
            self.assertRegex(rec.stderr, r"WARNING: .*agent a1.*src/unit\.py")
            self.assertSelfReview(root, "US0001", _rows(root, "US0001")[-1])

            path2, stem2, argv2 = _brief(cwd, root, "US0001")
            self.assertNotEqual(path, path2, "premise: the next round issues a new file")
            written2 = _block("US0001", stem2, "Independently checked.\n")
            path2.write_text(written2, encoding="utf-8")
            t.tool(None, "00:05", "Agent", prompt=f"Review it. Verdict file: {path2}")
            t.said("r1", "00:06", f"Review it. Verdict file: {path2}")
            t.tool("r1", "00:07", "Write", file_path=str(path2), content=written2)
            folder = t.flush()
            _worktree(folder, "a1", tree)
            rec = self._record(cwd, root, argv2, _env(folder, home))
            self.assertNotIn("self-review", rec.stderr)
            row = _rows(root, "US0001")[-1]
            self.assertIn("agent:r1", row["source"].split())
            self.assertIndependent(root, "US0001", row)


if __name__ == "__main__":
    unittest.main()
