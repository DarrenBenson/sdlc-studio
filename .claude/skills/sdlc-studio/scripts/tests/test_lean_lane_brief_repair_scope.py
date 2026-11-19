"""The lane brief bounds a repair, and `lane brief --repair` hands a repair agent what it answers.

A repair answering a REJECT kept breaking what the first build got right (LC-005), because
nothing the builder reads said a repair is bounded: the brief states it in one line among the
lane's obligations. A repair the orchestrator ran in its own context then cost that context the
refusal and the findings, read and re-read; `lane brief --repair` prints the unit's brief with
the landing's refusal and the REJECT's findings quoted byte for byte, for a fresh agent, and
refuses a unit with nothing to repair.

Driven through `sprint.py lane brief`, `lane land` and `lane accept`, the shipped entry points,
in throwaway projects; a landing's commit hook is a stub that refuses one path.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

UNIT, OTHER = "US0101", "US0102"
#: The stub hook's refusal, several lines with a trailing space and a tab, so a summary, a
#: truncation or a re-wrap of it cannot pass for the output itself.
REFUSAL = ("stub pre-commit: REFUSED src/refuse.py \n"
           "  lint-style: line 3:\tan em dash in prose\n"
           "commit-msg: subject names no unit")
HOOK = """#!/bin/sh
if git diff --cached --name-only | grep -q '^src/refuse'; then
  printf '%s\\n' "{refusal}" >&2
  exit 1
fi
exit 0
"""
#: Two BLOCKING findings and one that is not, each worded so a paraphrase is visible.
REJECT = ("VERDICT: REJECT\n"
          "ISSUES: [new] the gate lets a red unit through (lanes.py:41); [regression] the brief "
          "drops the unit's Affects when it is empty; [pre-existing] BG0900 the lane is slow\n"
          "BLOCKING: [new] the gate lets a red unit through (lanes.py:41); [regression] the brief "
          "drops the unit's Affects when it is empty\n")
APPROVE = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _story(root: Path, uid: str) -> None:
    _write(root, f"sdlc-studio/stories/{uid}-x.md",
           f"# {uid}: x\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
           f"> **Affects:** src/a.py, changelog.d/{uid}.md\n\n## Acceptance Criteria\n\n"
           "### AC1: it holds\n\n- **Verify:** shell true\n")


def _project(root: Path) -> None:
    """A git repository holding two Review stories and a QA seat card."""
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    _write(root, "src/a.py", "A = 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam\n\ncharter\n")
    for uid in (UNIT, OTHER):
        _story(root, uid)
    gitutil.git(["init", "-q", "-b", "main"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", "chore: the fixture"], root)


def _sprint(root: Path, *argv: str) -> tuple[int, str, str]:
    """`sprint.py` in-process, its git confined to the fixture."""
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _obligations(text: str) -> list[str]:
    """The lines of the brief's "Obligations on this lane" list."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Obligations on this lane"))
    rows = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  - "):
            break
        rows.append(ln[4:])
    return rows


class LaneBriefRepairScopeTests(unittest.TestCase):
    def test_the_brief_names_the_repair_scope(self) -> None:
        """AC1. MUTANT: HEAD, whose obligations name no repair scope; or a line that bounds the
        repair but drops the filing of the non-blocking findings. The control: the existing
        obligations stay, and the brief still exits 0 with no new flag."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0101-x.md").write_text(
                "# US0101: x\n\n> **Status:** Ready\n> **Points:** 1\n> **Affects:** src/a.py\n\n"
                "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n",
                encoding="utf-8")
            _live("lib.run_state").open_run(root, batch=["US0101"], goal="g")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = _live("sprint").main(["lane", "brief", "--units", "US0101",
                                           "--root", str(root)])
            self.assertEqual(0, rc, out.getvalue())
            rows = _obligations(out.getvalue())
            scope = [r for r in rows if "repair answering a REJECT" in r]
            self.assertEqual(1, len(scope), rows)
            self.assertIn("only the blocking findings", scope[0])
            self.assertIn("pins that kill them", scope[0])
            self.assertIn("files the rest", scope[0])
            self.assertTrue(any(r.startswith("Refuse a unit that carries no authored") for r in rows),
                            rows)
            self.assertEqual(5, len(rows), rows)

    # -- the repair brief ----------------------------------------------------------------------

    def _tmp(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name).resolve()

    def _refused_landing(self) -> Path:
        """A project whose landing of UNIT's lane the commit hook refused: `sprint.py lane land`
        exited 1 and kept the hook's output in the landing's commit.log."""
        base = self._tmp()
        root, wt = base / "repo", base / "lane-us0101"
        _project(root)
        _write(base, "hooks/pre-commit", HOOK.format(refusal=REFUSAL)).chmod(0o755)
        gitutil.git(["config", "core.hooksPath", str(base / "hooks")], root)
        gitutil.git(["worktree", "add", "-q", "-b", "lane-us0101", str(wt), "main"], root)
        _write(wt, "src/refuse.py", "X = 1\n")
        gitutil.git(["add", "--", "src/refuse.py"], wt)
        lane = "sdlc-studio/.local/lane"
        _write(wt, f"{lane}/commit-msg.txt", f"feat({UNIT}): a refusal\n")
        _write(wt, f"{lane}/{UNIT}-claims.json", json.dumps(
            [{"surface": "commit message", "claim": "a", "ruling": "TRUE"}]))
        _write(wt, f"{lane}/{UNIT}-mutants.json", "[]")
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "sprint.py"), "lane", "land",
                            "--worktree", str(wt), "--units", UNIT, "--root", str(root)],
                           capture_output=True, text=True, timeout=600, cwd=str(root),
                           env=gitutil.git_env(), check=False)
        self.assertEqual(1, r.returncode, r.stdout + r.stderr)
        return root

    def _accept(self, root: Path, uid: str, block: str, n: int) -> tuple[int, str, str]:
        """Record `block` for `uid` through `sprint.py lane accept`, from a verdict file a brief
        note issued for it, so the ledger row is bound to that file."""
        text = f"QA brief for {uid}\n"
        _write(root, f"sdlc-studio/.local/briefs/{uid}-qa.txt", text)
        critic = _live("critic")
        path = _write(root, f"sdlc-studio/reviews/verdicts/{uid}/{uid}-r{n}.txt", block)
        with (root / "sdlc-studio" / ".local" / "briefs.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"fp": critic.brief_fingerprint(text), "unit": uid, "seat": "qa",
                                 "tier": "full", "verdict_file": str(path)}) + "\n")
        return _sprint(root, "lane", "accept", "--unit", uid, "--verdict", str(path),
                       "--reviewer", "qa-seat", "--author", "builder-agent")

    def test_a_refused_landing_yields_a_repair_brief_with_the_refusal_verbatim(self) -> None:
        """AC1. MUTANTS: the refusal summarised or cut to its tail (the trailing space, the tab
        and the third line go); no refusal carried; the obligation bounding a repair dropped;
        a landing whose commit.log records a commit read as refused (the control)."""
        root = self._refused_landing()
        log = root / "sdlc-studio/.local/lane/landed/lane-us0101/commit.log"
        output = log.read_text(encoding="utf-8")
        self.assertIn(REFUSAL, output, "the fixture's hook output was not kept")
        rc, out, err = _sprint(root, "lane", "brief", "--units", UNIT, "--repair")
        self.assertEqual(0, rc, out + err)
        heading = next((ln for ln in out.splitlines() if ln.startswith("The landing's refusal")),
                       "")
        self.assertIn("sdlc-studio/.local/lane/landed/lane-us0101/commit.log", heading, out)
        self.assertIn(heading + "\n----- begin commit.log -----\n" + output
                      + "----- end commit.log -----", out, "the refusal is not byte for byte")
        self.assertTrue(any("repair answering a REJECT carries only the blocking findings" in r
                            for r in _obligations(out)), out)
        # The control: a later landing that committed answers the refusal.
        log.write_text("[lane-us0101 1a2b3c4] feat(US0101): a refusal\n 1 file changed\n",
                       encoding="utf-8")
        rc, out, err = _sprint(root, "lane", "brief", "--units", UNIT, "--repair")
        self.assertEqual(2, rc, out + err)

    def test_a_reject_yields_a_repair_brief_with_the_findings_verbatim(self) -> None:
        """AC2. MUTANTS: a finding paraphrased or re-joined from the ledger's folded cell; one
        of the two blocking findings dropped; the non-blocking issue listed as blocking; the
        verdict file left unnamed."""
        root = self._tmp()
        _project(root)
        rc, out, err = self._accept(root, UNIT, REJECT, 1)
        self.assertEqual(1, rc, out + err)
        self.assertIn(f"{UNIT}: REJECT recorded", out)
        rc, out, err = _sprint(root, "lane", "brief", "--units", UNIT, "--repair")
        self.assertEqual(0, rc, out + err)
        issues = REJECT.split("ISSUES: ", 1)[1].split("\nBLOCKING: ", 1)[0]
        blocking = REJECT.split("BLOCKING: ", 1)[1].rstrip("\n")
        rel = f"sdlc-studio/reviews/verdicts/{UNIT}/{UNIT}-r1.txt"
        head = next((ln for ln in out.splitlines() if ln.startswith("The REJECT this repair")), "")
        self.assertIn(f"verbatim from {rel}", head, out)
        self.assertIn(f"{head}\nISSUES:\n{issues}\nBLOCKING", out, "ISSUES not byte for byte")
        section = out.split("\nBLOCKING (every finding here blocks the unit", 1)[1]
        section = section.split("\n", 1)[1].split("\n\n", 1)[0]
        self.assertEqual(blocking, section, "the BLOCKING findings are not byte for byte")
        for finding in ("[new] the gate lets a red unit through (lanes.py:41)",
                        "[regression] the brief drops the unit's Affects when it is empty"):
            self.assertIn(finding, section, "a blocking finding is not marked blocking")
        self.assertNotIn("BG0900", section, "the non-blocking issue is presented as blocking")

    def test_a_unit_with_nothing_to_repair_is_refused_a_repair_brief(self) -> None:
        """AC3. MUTANTS: an empty repair brief at exit 0; a brief quoting a REJECT a later
        APPROVE answered; the ordinary brief changed, or given the repair section."""
        root = self._tmp()
        _project(root)
        rc, out, err = self._accept(root, OTHER, REJECT, 1)
        self.assertEqual(1, rc, out + err)
        rc, out, err = self._accept(root, OTHER, APPROVE, 2)
        self.assertEqual(0, rc, out + err)
        for uid in (UNIT, OTHER):
            with self.subTest(uid):
                rc, out, err = _sprint(root, "lane", "brief", "--units", uid, "--repair")
                self.assertEqual(2, rc, out + err)
                self.assertEqual("", out, "a refused repair brief printed a brief")
                self.assertIn(f"nothing to repair for {uid}", err)
        rc, out, err = _sprint(root, "lane", "brief", "--units", UNIT)
        self.assertEqual(0, rc, out + err)
        self.assertEqual(5, len(_obligations(out)), out)
        self.assertNotIn("--- REPAIR", out)

    def test_the_runbook_routes_a_repair_to_a_fresh_agent(self) -> None:
        """AC4. MUTANTS: no row for a refused landing or a REJECT; a row leaving the repair to
        the orchestrator; a row naming a command `sprint.py lane` refuses."""
        runbook = (SCRIPTS.parent / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        rows = [ln for ln in runbook.splitlines()
                if ln.startswith("| ") and "refused landing" in ln and "REJECT" in ln]
        self.assertEqual(1, len(rows), rows)
        row = rows[0]
        command = re.search(r"`(sprint\.py lane brief [^`]*--repair[^`]*)`", row)
        self.assertIsNotNone(command, row)
        self.assertIn("fresh repair agent", row)
        self.assertIn("does not edit the code or run its tests in its own context", row)
        argv = shlex.split(command.group(1).replace("<id>", UNIT))[1:]
        args = _live("sprint").build_parser().parse_args(argv)
        self.assertEqual(("brief", [UNIT], True), (args.action, args.units, args.repair))
        helped = subprocess.run([sys.executable, "-B", str(SCRIPTS / "sprint.py"), "lane",
                                 "--help"], capture_output=True, text=True, timeout=120,
                                check=False)
        # The flag itself, not a longer one argparse would accept `--repair` as an abbreviation of.
        self.assertRegex(helped.stdout, r"(?<![\w-])--repair(?![\w-])")


if __name__ == "__main__":
    unittest.main()
