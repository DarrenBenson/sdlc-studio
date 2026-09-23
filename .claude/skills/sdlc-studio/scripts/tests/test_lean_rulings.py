"""US0874: a persona seat answers the run's questions and cites precedent (EP0260).

`decisions.py rule` records a seat's binding ruling with its seat and subject; `precedent`
ranks the prior accepted rulings for a subject, then keyword matches across the whole log;
`rule` refuses to re-decide a subject silently; an open run counts who ruled.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import run_state  # noqa: E402


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


decisions = _load("decisions")


def _run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = decisions.main(list(argv))
    return code, out.getvalue(), err.getvalue()


def _rule(root: Path, subject: str, question: str, *extra: str, seat: str = "engineering"):
    return _run("rule", "--root", str(root), "--seat", seat, "--subject", subject,
                "--question", question, "--ruling", "pin it to a commit sha",
                "--reason", "a floating tag can change under us", *extra)


class RuleTests(unittest.TestCase):
    def test_a_ruling_is_recorded_with_seat_and_subject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            code, out, err = _rule(root, "Deps:Action-Pins", "may a workflow use a tag?")
            self.assertEqual(code, 0, err)
            self.assertIn("D0001", out)                              # its id is printed
            rec = decisions.list_decisions(root)[0]
            self.assertEqual(rec["status"], "accepted")
            meta = decisions.ruling_of(rec)
            self.assertEqual(meta["seat"], "engineering")
            self.assertEqual(meta["subject"], "deps:action-pins")    # normalised key
            self.assertIn("may a workflow use a tag?", rec["decision"])
            self.assertIn("pin it to a commit sha", rec["decision"])
            self.assertIn("a floating tag can change under us", rec["rationale"])
            # an ordinary decision is not a ruling
            decisions.add(root, "Use SQLite", "one file")
            self.assertIsNone(decisions.ruling_of(decisions.list_decisions(root)[1]))
            # the JSON form carries the same id
            code, out, _ = _rule(root, "other:subject", "q?", "--format", "json")
            self.assertEqual(json.loads(out)["id"], "D0003")

    def test_a_precedent_must_be_cited_or_departed_from(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _rule(root, "deps:action-pins", "may a workflow use a tag?")     # D0001
            # neither flag: refused, the precedent is printed, nothing written
            code, out, err = _rule(root, "deps:action-pins", "can we float a tag?",
                                   seat="qa")
            self.assertEqual(code, 2)
            self.assertIn("D0001", out + err)
            self.assertEqual(len(decisions.list_decisions(root)), 1)
            # --cites: no new row, the cited ruling is printed
            code, out, err = _rule(root, "deps:action-pins", "can we float a tag?",
                                   "--cites", "D0001")
            self.assertEqual(code, 0, err)
            self.assertEqual(len(decisions.list_decisions(root)), 1)
            self.assertIn("D0001", out)
            self.assertIn("pin it to a commit sha", out)
            # citing a decision that does not exist is refused
            code, _, _ = _rule(root, "deps:action-pins", "q?", "--cites", "D0099")
            self.assertEqual(code, 2)
            # --differs: a new ruling naming the precedent it departs from
            code, out, err = _rule(root, "deps:action-pins", "a vendored action?",
                                   "--differs", "vendored code is pinned by the tree")
            self.assertEqual(code, 0, err)
            rows = decisions.list_decisions(root)
            self.assertEqual(len(rows), 2)
            self.assertIn("D0001", rows[1]["rationale"])
            self.assertIn("vendored code is pinned by the tree", rows[1]["rationale"])
            # a different subject with no precedent needs neither flag
            code, _, err = _rule(root, "deps:lockfile", "commit the lockfile?")
            self.assertEqual(code, 0, err)


class PrecedentTests(unittest.TestCase):
    def test_precedent_ranks_subject_then_keywords(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # rows written before subjects existed (plain decisions)
            decisions.add(root, "Mutation evidence is registered after the last edit",
                          "content-hash registration empties evidence on later edits")  # D0001
            decisions.add(root, "Release notes are composed from fragments",
                          "one fragment per unit")                                     # D0002
            decisions.add(root, "Mutation ledger rows are audited at close",
                          "stale rows win the join")                                   # D0003
            decisions.add(root, "Mutation ledger evidence is wiped on registration",
                          "an old ruling")                                             # D0004
            decisions.add(root, "Mutation ledger evidence registered twice",
                          "replaced", supersedes="D0004")                              # D0005
            # prior rulings on the subject
            _rule(root, "review:mutation", "who writes the mutants?")                  # D0006
            _rule(root, "review:other", "unrelated")                                   # D0007
            _rule(root, "review:mutation", "one more ruling here",
                  "--differs", "a new case")                                   # D0008
            got = decisions.precedent(root, "Review:Mutation",
                                      "when is mutation evidence registered in the ledger?")
            ids = [p["id"] for p in got]
            self.assertEqual(len(ids), 3)                                  # at most 3
            self.assertEqual(ids[:2], ["D0008", "D0006"])                  # subject first, newest first
            self.assertEqual([p["match"] for p in got[:2]], ["subject", "subject"])
            self.assertEqual(got[2]["match"], "keywords")
            # the best keyword match among pre-subject rows; the superseded row never appears
            self.assertEqual(ids[2], "D0005")
            self.assertNotIn("D0004", ids)
            # without subject hits, keyword matches fill the list, best overlap first
            got = decisions.precedent(root, "nothing:here",
                                      "when is mutation evidence registered in the ledger?")
            self.assertEqual([p["id"] for p in got], ["D0005", "D0001", "D0003"])
            self.assertNotIn("D0002", [p["id"] for p in got])
            # the CLI verb prints them
            code, out, err = _run("precedent", "--root", str(root), "--subject",
                                  "review:mutation", "--question", "mutation evidence?")
            self.assertEqual(code, 0, err)
            self.assertIn("D0008", out)


class RulingCountTests(unittest.TestCase):
    def test_the_run_counts_persona_and_operator_rulings(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # no run open: rulings are recorded, but no run state is minted
            _rule(root, "deps:action-pins", "may a workflow use a tag?")               # D0001
            self.assertEqual(run_state.read(root), {})
            run_state.update(root, run_id="RUN-TEST")
            self.assertTrue(run_state.is_open(root))
            _rule(root, "deps:lockfile", "commit the lockfile?", seat="qa")            # D0002
            _rule(root, "deps:action-pins", "float a tag?", "--cites", "D0001")
            code, _, err = _run("add", "--root", str(root), "--decision", "Ship Friday",
                                "--rationale", "operator call")                        # D0003
            self.assertEqual(code, 0, err)
            rulings = run_state.read(root)["rulings"]
            self.assertEqual(rulings, [
                {"id": "D0002", "by": "persona", "seat": "qa", "subject": "deps:lockfile",
                 "kind": "ruling"},
                {"id": "D0001", "by": "persona", "seat": "engineering",
                 "subject": "deps:action-pins", "kind": "cited"},
                {"id": "D0003", "by": "operator", "seat": None, "subject": None,
                 "kind": "ruling"},
            ])
            by = [r["by"] for r in rulings]
            self.assertEqual((by.count("persona"), by.count("operator")), (2, 1))
            # a refused ruling is not counted
            _rule(root, "deps:lockfile", "again?")
            self.assertEqual(len(run_state.read(root)["rulings"]), 3)


if __name__ == "__main__":
    unittest.main()
