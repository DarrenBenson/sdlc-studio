"""BG0818: `init guided` must not read a stage's own drafted scaffold, or an AGENTS.md that
carries no lifecycle doctrine, as that stage done.

`stage_output_exists` answered on existence alone. The PRD stage seeds `sdlc-studio/prd.md`, so the
very run that drafted it printed `resume point: trd`, and the next bare `init guided` ticked `prd`
from the unfilled template and drafted the TRD: the PRD was never confirmed. A brownfield
AGENTS.md of framework boilerplate ticked `agents` the same way, so the project's agents never
received the process. Every test here drives the shipped CLI in a throwaway project.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
INIT = SCR / "init.py"
STATUS = SCR / "status.py"
STARTER = SCR.parent / "templates" / "agent-instructions.md"
BOILERPLATE = "# AGENTS.md\n\nThis is an Astro site. Run `npm run dev` to start it.\n"


def _cli(root: Path, *args: str, script: Path = INIT) -> str:
    r = subprocess.run([sys.executable, str(script), *args, "--root", str(root)],
                       capture_output=True, text=True, cwd=root, timeout=60)
    if r.returncode:
        raise AssertionError(f"{script.name} {' '.join(args)} exited {r.returncode}: {r.stderr}")
    return r.stdout


def _status(root: Path, stage: str) -> str:
    state = json.loads((root / "sdlc-studio" / ".local" / "onboarding.json").read_text())
    return next(s["status"] for s in state["stages"] if s["name"] == stage)


def _resume_point(out: str) -> str:
    m = re.search(r"resume point: (\S+)", out)
    if not m:
        raise AssertionError(f"no resume point in:\n{out}")
    return m.group(1)


def _doctrine_block() -> str:
    """The starter's `## Operating doctrine` section, as an operator would append it."""
    text = STARTER.read_text(encoding="utf-8")
    start = text.index("## Operating doctrine")
    return text[start:text.index("\n## ", start + 1)] + "\n"


class GuidedStageConfirmTests(unittest.TestCase):

    def test_the_drafted_stage_stays_current(self) -> None:
        """MUTANT: in `init.py`, drop the unfilled-scaffold test from `stage_output_exists`, so a
        seeded singleton satisfies its stage on existence alone (HEAD's behaviour)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cli(root, "run")
            _cli(root, "guided", "--confirm")          # accept the seeded agent instructions
            first = _cli(root, "guided")
            self.assertIn("drafted sdlc-studio/prd.md", first, first)
            self.assertEqual("prd", _resume_point(first),
                             "the run that drafted the PRD must name it as the resume point")
            self.assertRegex(first, r"\[ \] prd  <- next")
            second = _cli(root, "guided")
            self.assertEqual("prd", _resume_point(second),
                             "a second bare run read the unfilled template as the PRD")
            self.assertEqual("pending", _status(root, "prd"), second)
            self.assertFalse((root / "sdlc-studio" / "trd.md").exists(),
                             "the TRD was drafted before the PRD was confirmed")
            # Control: the stage is open, not stuck - an explicit confirm still advances it.
            confirmed = _cli(root, "guided", "--confirm")
            self.assertEqual("done", _status(root, "prd"))
            self.assertEqual("trd", _resume_point(confirmed))

    def test_boilerplate_agents_md_leaves_the_stage_open(self) -> None:
        """MUTANT: in `init.py`, drop the doctrine test from the agents branch of
        `stage_output_exists`, so AGENTS.md plus CLAUDE.md satisfy it on existence alone."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(BOILERPLATE, encoding="utf-8")
            (root / "package.json").write_text('{"name": "site"}\n', encoding="utf-8")
            _cli(root, "run")                          # writes CLAUDE.md, leaves AGENTS.md
            self.assertEqual(BOILERPLATE, (root / "AGENTS.md").read_text(encoding="utf-8"))
            out = _cli(root, "guided")
            self.assertEqual("agents", _resume_point(out), out)
            self.assertRegex(out, r"\[ \] agents  <- next")
            self.assertEqual("pending", _status(root, "agents"))
            self.assertIn("AGENTS.md already present - review it", out,
                          "the project's own AGENTS.md is not a seeded draft")
            self.assertRegex(out, r"append the `## Operating doctrine` block from \S*"
                                  r"templates/agent-instructions\.md", out)
            self.assertEqual(BOILERPLATE, (root / "AGENTS.md").read_text(encoding="utf-8"),
                             "the offer must not rewrite the project's own AGENTS.md")
            # Control: taking the offer satisfies the stage - the check reads the doctrine, it
            # does not refuse every pre-existing AGENTS.md.
            with (root / "AGENTS.md").open("a", encoding="utf-8") as fh:
                fh.write("\n" + _doctrine_block())
            after = _cli(root, "guided")
            self.assertEqual("done", _status(root, "agents"), after)
            self.assertEqual("prd", _resume_point(after))

    def test_a_fresh_projects_seeded_agent_instructions_await_review(self) -> None:
        """MUTANT: in `init.py`, drop the unfilled-scaffold test for the agent files, so the
        starter `init run` seeds satisfies the agents stage before anyone has read it.

        The same defect one stage earlier: `init run` seeds AGENTS.md from the starter the agents
        stage drafts, placeholders and all, and the first `init guided` ticked the stage."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cli(root, "run")
            out = _cli(root, "guided")
            self.assertEqual("agents", _resume_point(out), out)
            self.assertIn("AGENTS.md seeded from its template - review it", out,
                          "a fresh project's AGENTS.md was written by init, not by the user")
            self.assertIn("CLAUDE.md seeded from its template - review it", out)
            self.assertIn("fill in the {{placeholders}} in AGENTS.md", out)
            self.assertFalse((root / "sdlc-studio" / "prd.md").exists(),
                             "the PRD was drafted over an agents stage nobody had reviewed")
            # Control: once the placeholders are filled the tree satisfies the stage unaided. The
            # starter's guidance comment (stripped when seeding) names `{{placeholder}}`; a
            # project documenting that syntax is not an unfilled scaffold.
            agents = root / "AGENTS.md"
            agents.write_text(re.sub(r"\{\{[^{}]*\}\}", "filled",
                                     agents.read_text(encoding="utf-8"))
                              + "\nTemplates use `{{placeholder}}` syntax.\n", encoding="utf-8")
            self.assertEqual("prd", _resume_point(_cli(root, "guided")))
            self.assertEqual("done", _status(root, "agents"))

    def test_an_authored_document_still_supersedes_its_stage(self) -> None:
        """MUTANT: in `init.py`, make `stage_output_exists` return False for every singleton.

        The paired control for BG0615: the tree must still be able to contradict the marker. A
        PRD that carries none of its template's placeholders is authored work, and a stale
        `pending` beside it is reconciled rather than held for ever."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cli(root, "run")
            _cli(root, "guided", "--confirm")          # agents
            # It QUOTES template tokens: a code span, and a fenced example. `{{version}}` and
            # `{{date}}` are tokens of the PRD template itself. The bare `{{date}}` is one seeding
            # always fills, so it can never mark a draft.
            (root / "sdlc-studio" / "prd.md").write_text(
                "# PRD\n\nA written PRD. Release notes render `{{version}}` from the tag.\n\n"
                "```text\nBuilt at {{version}}\n```\n\nFooters print {{date}}.\n",
                encoding="utf-8")
            out = _cli(root, "guided")
            self.assertEqual("done", _status(root, "prd"), out)
            self.assertEqual("trd", _resume_point(out))

    def test_a_non_utf8_file_does_not_crash_onboarding(self) -> None:
        """MUTANT: in `init.py`, read stage outputs with strict UTF-8, or let `carries_doctrine`
        raise, so a cp1252 project file crashes `init guided` and `status hint`.

        The draft and doctrine tests look for ASCII tokens; a project file saved in another
        encoding must leave the stage open and say why, never take down the orientation path."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_bytes("# AGENTS.md\n\nBudget: \u00a3500.\n".encode("cp1252"))
            (root / "package.json").write_text('{"name": "site"}\n', encoding="utf-8")
            _cli(root, "run")
            out = _cli(root, "guided")
            self.assertEqual("agents", _resume_point(out), out)
            self.assertIn("AGENTS.md cannot be read (not valid UTF-8) - re-save it as UTF-8", out)
            _cli(root, "hint", script=STATUS)
            # A cp1252 PRD, written and quoting no template token, is authored work.
            _cli(root, "guided", "--confirm")
            (root / "sdlc-studio" / "prd.md").write_bytes(
                "# PRD\n\nPrice: \u00a39 a month.\n".encode("cp1252"))
            out = _cli(root, "guided")
            self.assertEqual("done", _status(root, "prd"), out)
            self.assertEqual("trd", _resume_point(out))
            _cli(root, "hint", script=STATUS)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores chmod")
    def test_an_unreadable_file_does_not_crash_onboarding(self) -> None:
        """MUTANT: in `init.py`, let `_read` raise OSError, so a stage output the process may not
        read crashes `init guided` and `status hint` with `Permission denied` (BG0840).

        An unreadable output is not authored: the stage stays open and the output names the file
        and the reason, never a UTF-8 remedy for a file that is not a decoding problem."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            agents = root / "AGENTS.md"
            agents.write_text(BOILERPLATE, encoding="utf-8")
            (root / "package.json").write_text('{"name": "site"}\n', encoding="utf-8")
            agents.chmod(0)
            try:
                _cli(root, "run")
                out = _cli(root, "guided")
                self.assertEqual("agents", _resume_point(out), out)
                self.assertIn("AGENTS.md cannot be read (Permission denied)", out)
                self.assertNotIn("UTF-8", out)
                _cli(root, "hint", script=STATUS)
            finally:
                agents.chmod(0o644)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cli(root, "run")
            _cli(root, "guided", "--confirm")          # agents
            prd = root / "sdlc-studio" / "prd.md"
            prd.write_text("# PRD\n\nA written PRD.\n", encoding="utf-8")
            prd.chmod(0)
            try:
                out = _cli(root, "guided")
                self.assertEqual("prd", _resume_point(out), out)
                self.assertEqual("pending", _status(root, "prd"))
                self.assertIn("sdlc-studio/prd.md cannot be read (Permission denied)", out)
                _cli(root, "hint", script=STATUS)
            finally:
                prd.chmod(0o644)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").mkdir()                 # a directory where the file belongs
            _cli(root, "run")
            out = _cli(root, "guided")
            self.assertEqual("agents", _resume_point(out), out)
            self.assertIn("AGENTS.md cannot be read (Is a directory)", out)
            _cli(root, "hint", script=STATUS)


if __name__ == "__main__":
    unittest.main()
