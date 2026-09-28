"""BG0822: the close, the signature and the signed page speak the v6 sign-off vocabulary.

The close's tail prefixed its lines `apply-signoff:`, naming a flag v6 retired, so an operator
read `apply-signoff: velocity row recorded` as sign output. Its last line told them to sign as
`"<the reviewer of record>"`, sign's refusals demanded a reviewer of record, and the page's
Sign-off table headed the operator's signature `Reviewer of record`. The handoff step said
`sign` writes `the stopped outcome from the partial verdict` while `sign` writes `partial` or
`missed`, and read `from the None verdict` with no verdict recorded.

Driven through `sprint.py close` and `sprint.py sign`, the shipped entry points, in throwaway git
repositories; the handoff step is asked directly with each verdict.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402 - git confined to the fixture
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

RETIRED = re.compile(r"(?i)apply-signoff|reviewer of record")


def _live(name: str):
    """The module the close resolves at call time, whatever `sys.modules` holds now."""
    return sys.modules.get(name) or importlib.import_module(name)


def _git(root: Path, *args: str) -> str:
    return gitutil.git(list(args), root, text=True, timeout=60).stdout.strip()


def _state_path(root: Path) -> Path:
    return root / "sdlc-studio" / ".local" / "run-state.json"


def _edit_state(root: Path, **fields) -> dict:
    state = json.loads(_state_path(root).read_text(encoding="utf-8"))
    state.update(fields)
    _state_path(root).write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def _fixture(root: Path) -> None:
    """The one-page report's run, open, in a git repository, with an epic whose breakdown the
    batch completes - so the close's tail derives it and says so."""
    _git(root, "init", "-q")
    lean.lean_run(root)
    ed = root / "sdlc-studio" / "epics"
    ed.mkdir(parents=True, exist_ok=True)
    (ed / "EP0001-a-epic.md").write_text(
        "# EP0001: a epic\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
        "- [x] [US0001: a unit](../stories/US0001-a-unit.md)\n"
        "- [x] [US0002: a unit](../stories/US0002-a-unit.md)\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q",
         "--no-verify", "-m", "fixture base")
    _edit_state(root, base_ref=_git(root, "rev-parse", "HEAD"), ended_at=None,
                outcome="running")


def _green_chain(mod) -> contextlib.ExitStack:
    """Every chain step and report hold stubbed green: this unit judges the words the close
    prints around them, its tail and its last line."""
    stack = contextlib.ExitStack()
    stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
    for name in mod._CLOSE_CHAIN:
        stack.enter_context(unittest.mock.patch.object(
            mod, "_close_" + name.replace("-", "_"),
            lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
    return stack


def _cli(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class CloseOutputVocabularyTests(unittest.TestCase):

    def test_no_retired_sign_off_words_in_close_output(self) -> None:
        """AC1. MUTANTS: HEAD's `apply-signoff:` tail prefix; the `<the reviewer of record>`
        principal hint; the template's `Reviewer of record` header; the derivation printing
        its own `apply-signoff:` refusal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            sprint = _live("sprint")
            with _green_chain(sprint):
                rc, out, err = _cli(root, "close", "--retro", lean.RETRO)
            self.assertEqual(0, rc, out + err)
            said = [ln for ln in (out + err).splitlines() if RETIRED.search(ln)]
            self.assertEqual([], said, out + err)
            # the tail ran and speaks as the close: it derived the epic and says who did
            self.assertIn("close: derived EP0001 terminal (all children terminal)",
                          out.splitlines())
            self.assertIn('--principal "<the operator who signs>"', out.splitlines()[-1])
            rid = json.loads(_state_path(root).read_text(encoding="utf-8"))["report"]
            md = next((root / "sdlc-studio" / "reports").glob(f"{rid}-*.md"))
            text = md.read_text(encoding="utf-8")
            self.assertNotIn("Reviewer of record", text)
            self.assertIn("| Signed by | Date | Fingerprint signed |", text)
            # and the page rendered on demand
            html = lean.sr.render_html(lean.sr.read_report(root, rid))
            self.assertNotIn("Reviewer of record", html)
            self.assertIn('<span class="k">Signed by</span>', html)
        # The derivation's own refusal line names its caller, never the retired flag.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            (root / "sdlc-studio" / "stories" / "US0002-a-unit.md").unlink()
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                sprint._derive_parent_epics(root, ["US0001", "US0002"], "close")
            self.assertIn("close: EP0001 not derived", err.getvalue())
            self.assertNotRegex(err.getvalue(), RETIRED)

    def test_the_handoff_step_names_the_signed_outcome(self) -> None:
        """AC2. MUTANT: HEAD's `GOAL_REACHED if achieved else STOPPED`, which names `stopped`
        for a partial verdict and prints `from the None verdict` with none recorded."""
        sprint = _live("sprint")
        for verdict, outcome in (("partial", "partial"), ("missed", "missed"),
                                 ("achieved", "goal-reached"), (None, "stopped")):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _fixture(root)
                state = _edit_state(root, sprint_goal_verdict=(
                    {"verdict": verdict, "note": "judged"} if verdict else None))
                self.assertEqual(outcome, sprint.SIGNED_OUTCOMES.get(verdict, "stopped"))
                with contextlib.redirect_stdout(io.StringIO()):
                    ok, detail, _remedy = sprint._close_handoff(root, lean.RETRO, state)
                self.assertTrue(ok, detail)
                self.assertIn(f"which writes the {outcome} outcome", detail)
                self.assertNotIn("None", detail)
                if verdict:
                    self.assertIn(f"from the {verdict} verdict", detail)

    def test_sign_refusals_name_the_operator(self) -> None:
        """The signature's refusals ask for the operator who signs. MUTANT: HEAD's `the reviewer
        of record must sit outside the author's control`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            _live("critic").record_verdict(root, "US0004", "APPROVE", reviewer="qa-seat",
                                           author="builder", issues="fine")
            _edit_state(root, report="RPT0001")
            for principal in ("-", "qa-seat"):
                with unittest.mock.patch.object(_live("sprint"), "tree_moved_since_close",
                                                lambda *a, **k: []):
                    rc, out, err = _cli(root, "sign", "--report", "RPT0001",
                                        "--principal", principal)
                self.assertEqual(2, rc, out + err)
                self.assertIn("sign REFUSED", err)
                self.assertNotRegex(out + err, RETIRED)
                self.assertIn("the operator", err)


if __name__ == "__main__":
    unittest.main()
