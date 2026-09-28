"""BG0819: a report's `Verified on:` names the commit the close's gate ran against.

`sprint_report.py` filled the figure from `verified_sha or base_ref`, and nothing wrote
`verified_sha`, so every page named the commit the run was PLANNED from as the commit it was
verified on. The close now stamps the HEAD its gate ran against on the run state before the
page is derived, and a run with none recorded reads `not recorded`, never the base ref. A page
signed before the stamp existed named the base ref, and its record holds no `verified_sha` key;
re-deriving that page reads the record's base ref again, so the fix moves no signature it did
not make and the figure is still judged against the record.

AC1 drives `sprint.py close`, the shipped entry point, in a throwaway git repository; AC2 derives
the page from a run record carrying a base ref and no verified commit.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
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

sr = lean.sr


def _live(name: str):
    """The module the close resolves at call time, whatever `sys.modules` holds now."""
    return sys.modules.get(name) or importlib.import_module(name)


def _git(root: Path, *args: str) -> str:
    return gitutil.git(list(args), root, text=True, timeout=60).stdout.strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q",
         "--no-verify", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _state_path(root: Path) -> Path:
    return root / "sdlc-studio" / ".local" / "run-state.json"


def _edit_state(root: Path, **fields) -> None:
    state = json.loads(_state_path(root).read_text(encoding="utf-8"))
    for key, value in fields.items():
        if value is None:
            state.pop(key, None)
        else:
            state[key] = value
    _state_path(root).write_text(json.dumps(state, indent=2), encoding="utf-8")


def _verified_on(report: dict) -> str:
    goal = next(s for s in report["sections"] if s["key"] == "goal")
    return goal["figures"]["verified_sha"]["value"]


def _green_chain(mod) -> contextlib.ExitStack:
    """Every close chain step and report hold stubbed green: this unit judges the page the close
    files, not the steps before it."""
    stack = contextlib.ExitStack()
    stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
    for name in mod._CLOSE_CHAIN:
        stack.enter_context(unittest.mock.patch.object(
            mod, "_close_" + name.replace("-", "_"),
            lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
    return stack


class ReportVerifiedOnTests(unittest.TestCase):

    def test_the_close_commit_is_named(self) -> None:
        """AC1. MUTANTS: HEAD's `verified_sha or base_ref` with nothing writing `verified_sha`;
        a close that stamps the base ref, or stamps nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _git(root, "init", "-q")
            lean.lean_run(root)
            base = _commit(root, "fixture base")
            _edit_state(root, base_ref=base, ended_at=None, outcome="running")
            (root / "work.txt").write_text("the run's work\n", encoding="utf-8")
            head = _commit(root, "the run's work")
            self.assertNotEqual(base, head)
            sprint = _live("sprint")
            out, err = io.StringIO(), io.StringIO()
            with _green_chain(sprint), contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                rc = sprint.main(["close", "--retro", lean.RETRO, "--root", str(root)])
            self.assertEqual(0, rc, out.getvalue() + err.getvalue())
            state = json.loads(_state_path(root).read_text(encoding="utf-8"))
            self.assertEqual(head, state.get("verified_sha"))
            rid = state.get("report")
            self.assertTrue(rid, out.getvalue() + err.getvalue())
            page = sr.read_report(root, rid)
            self.assertEqual(head, _verified_on(page))
            md = next((root / "sdlc-studio" / "reports").glob(f"{rid}-*.md"))
            self.assertIn(f"> **Verified on:** {head}", md.read_text(encoding="utf-8"))

    def test_no_record_is_not_the_base_ref(self) -> None:
        """AC2. MUTANT: the base-ref fallback; `none recorded` in place of `not recorded`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean.lean_run(root)
            _edit_state(root, base_ref="0" * 40, verified_sha=None)
            self.assertEqual("not recorded", _verified_on(sr.build_report(root, lean.RETRO)))
            # THE CONTROL: a recorded commit is named.
            _edit_state(root, verified_sha="1" * 40)
            self.assertEqual("1" * 40, _verified_on(sr.build_report(root, lean.RETRO)))

    def test_a_page_signed_before_the_stamp_is_judged_against_its_record(self) -> None:
        """A page signed before the close stamped a commit named the base ref, and its record
        holds no `verified_sha` key. Re-derived with that page, the figure reads the record's
        base ref again, so `check` still judges it against the record. MUTANTS: no fallback, so
        every page signed under the old rule reads INVALIDATED; replaying the signed page's own
        reading, so a rewritten base ref, or a stamp deleted from a newer record, reads VALID."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean.lean_run(root)
            _edit_state(root, base_ref="0" * 40, verified_sha=None)
            page = sr.build_report(root, lean.RETRO)
            self.assertEqual("not recorded", _verified_on(page))      # a first derivation
            goal = next(s for s in page["sections"] if s["key"] == "goal")
            goal["figures"]["verified_sha"]["value"] = "0" * 40      # as signed, the old rule
            self.assertEqual("0" * 40, _verified_on(sr.build_report(root, lean.RETRO,
                                                                     filed=page)))
            # A rewritten base ref in the signed record moves the figure, so the page reads
            # INVALIDATED, as it did before the stamp existed.
            _edit_state(root, base_ref="2" * 40)
            self.assertEqual("2" * 40, _verified_on(sr.build_report(root, lean.RETRO,
                                                                     filed=page)))
            # A newer record's stamp is read; deleting it moves the figure off the stamp.
            _edit_state(root, verified_sha="1" * 40)
            goal["figures"]["verified_sha"]["value"] = "1" * 40
            self.assertEqual("1" * 40, _verified_on(sr.build_report(root, lean.RETRO,
                                                                     filed=page)))
            _edit_state(root, verified_sha=None)
            self.assertNotEqual("1" * 40, _verified_on(sr.build_report(root, lean.RETRO,
                                                                        filed=page)))
            # A close that could not read HEAD stamps the key as null: that record does not
            # predate the stamp, so it reads `not recorded`, never the base ref.
            state = json.loads(_state_path(root).read_text(encoding="utf-8"))
            state["verified_sha"] = None
            _state_path(root).write_text(json.dumps(state), encoding="utf-8")
            self.assertEqual("not recorded", _verified_on(sr.build_report(root, lean.RETRO,
                                                                           filed=page)))

if __name__ == "__main__":
    unittest.main()
