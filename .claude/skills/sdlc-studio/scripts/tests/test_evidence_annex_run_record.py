"""The committed run record holds to the evidence annex a consumer reads it by.

`reference-evidence-schema.md` contracts the keys of the tracked run record in each of its three
states (awaiting its signature, sealed, stopped), the fields of its signature, and the rule that
makes a record await its signature, as Markdown tables under fixed headings. These tests read
those tables the way a consumer's parser does (the annex reader is the report test's, shared)
and hold them to records the shipped `sprint` entry points file in a throwaway git run: opened
by `sprint plan --write`, closed by `sprint close`, then signed by `sprint sign` in one clone and
ended by `sprint stop` in the closing checkout. The awaiting rule is evaluated from the annex's
own rows and compared with what `sprint plan --write` does in a fresh clone of each.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-evidence-schema.md
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_evidence_annex_report as annex  # noqa: E402 - the annex reader, shared
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

RUN = "RUN-LEAN0001"
REPORT = "RPT0001"
RECORD = f"sdlc-studio/reports/runs/{RUN}.json"
LIVE = "sdlc-studio/.local/run-state.json"
#: Commits are dated after the run's window, so none of them moves a figure.
LATER = "2099-01-01T00:00:00Z"
#: The states the annex's key table has a column for, in its column order.
STATES = ("Awaiting", "Sealed", "Stopped")
#: The JSON type words a type cell may use, as the decoded value's exact Python type: a bool is
#: never read as an integer.
TYPES = {"string": str, "integer": int, "object": dict, "list": list, "null": type(None),
         "boolean": bool}


# --- the annex, read as a consumer reads it ------------------------------------------------------

def documented_types(cell: str) -> tuple[type, ...] | None:
    """The types a state's cell allows, or None for a dash (not contracted in that state). A
    word the parser does not know fails: a consumer could not read it either."""
    cell = cell.strip()
    if cell == "-":
        return None
    words = [w.strip() for w in cell.split(" or ")]
    unknown = [w for w in words if w not in TYPES]
    if unknown:
        raise AssertionError(f"the annex names a type no parser reads: {cell!r}")
    return tuple(TYPES[w] for w in words)


def conformance_problems(record: dict, state: str) -> list[str]:
    """Each way `record` breaks the annex's contract for `state`: a contracted key missing, or
    holding a type its cell does not allow. A key the annex does not name is never a problem."""
    problems = []
    for key, row in annex.keyed("Run record keys", "Key").items():
        types = documented_types(row[state])
        if types is None:
            continue
        if key not in record:
            problems.append(f"{state}: the record carries no {key!r}")
        elif type(record[key]) not in types:
            problems.append(f"{state}: {key!r} holds a {type(record[key]).__name__}, "
                            f"the annex documents {row[state]!r}")
    return problems


def annex_awaits(record: dict) -> bool:
    """The annex's awaiting-signature rule, evaluated from its own rows: every row must hold. A
    cell that is one code span holds when the key equals it; `any non-empty value` and
    `no value` are the only other conditions, and any other wording fails."""
    rows = annex.keyed("Run record awaiting rule", "Key")
    if not rows:
        raise AssertionError("the annex's awaiting rule has no rows")
    for key, row in rows.items():
        holds, value = row["Holds"].strip(), record.get(key)
        if m := re.fullmatch(r"`([^`]+)`", holds):
            ok = value == m.group(1)
        elif holds == "any non-empty value":
            ok = bool(value)
        elif holds == "no value":
            ok = not value
        else:
            raise AssertionError(f"the annex's awaiting rule reads {holds!r} for {key!r}, "
                                 f"which no parser reads")
        if not ok:
            return False
    return True


# --- the fixture runs, through the shipped entry points ------------------------------------------

def _git(root: Path, *argv: str):
    return gitutil.git(list(argv), root, text=True,
                       env_extra={"GIT_COMMITTER_DATE": LATER, "GIT_AUTHOR_DATE": LATER})


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)


def _clone(base: Path, source: Path, name: str) -> Path:
    dest = base / name
    _git(base, "clone", "-q", f"file://{source}", str(dest))
    return dest


def _record(root: Path) -> dict:
    return json.loads((root / RECORD).read_text(encoding="utf-8"))


def _plan(root: Path) -> tuple[int, str, str]:
    return signing._run(root, "plan", "--stories", "Ready", "--write", "--no-fetch")


def _open_by_plan(root: Path) -> None:
    """Open the fixture's run through `sprint plan --write`, so the keys the plan writes come
    from their writer, then lay the close fixture's run over it: its id, window and figures."""
    live = root / LIVE
    fixture = json.loads(live.read_text(encoding="utf-8"))
    live.unlink()
    rc, _out, err = _plan(root)
    if rc != 0:
        raise AssertionError(f"sprint plan --write refused the fixture ({rc}):\n{err}")
    state = json.loads(live.read_text(encoding="utf-8"))
    state.update(fixture)
    live.write_text(json.dumps(state), encoding="utf-8")


class RunRecordAnnexTests(unittest.TestCase):
    """One run, filed three ways. Built once: each step is a shipped command over real git."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        base = Path(cls._tmp.name)
        stub = base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(base / "transcripts"))
        cls._env = unittest.mock.patch.dict(os.environ, env, clear=True)
        cls._env.start()
        try:
            cls._build(base)
        except BaseException:
            cls.tearDownClass()
            raise

    @classmethod
    def _build(cls, base: Path) -> None:
        closer = base / "closer"
        closer.mkdir()
        lean._fixture(closer)
        signing._git_repo(closer)
        _open_by_plan(closer)
        rc, _out, err = lean._close(closer)
        if rc != 0:
            raise AssertionError(f"sprint close refused the fixture run ({rc}):\n{err}")
        _commit(closer, "close paperwork")
        cls.records = {"Awaiting": _record(closer)}
        cls.planned = {"Awaiting": _plan(_clone(base, closer, "after-close"))}

        signer = _clone(base, closer, "signer")
        rc, _out, err = signing._sign(signer, REPORT)
        if rc != 0:
            raise AssertionError(f"sprint sign refused the fixture run ({rc}):\n{err}")
        _commit(signer, "seal")
        cls.records["Sealed"] = _record(signer)
        cls.planned["Sealed"] = _plan(_clone(base, signer, "after-sign"))

        rc, _out, err = signing._run(closer, "stop", "--reason", "abandoned", "--force")
        if rc != 0:
            raise AssertionError(f"sprint stop refused the fixture run ({rc}):\n{err}")
        _commit(closer, "stop")
        cls.records["Stopped"] = _record(closer)
        cls.planned["Stopped"] = _plan(_clone(base, closer, "after-stop"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls._env.stop()
        cls._tmp.cleanup()

    def test_the_annex_names_the_states_its_key_table_has_columns_for(self) -> None:
        """The states table and the key table's columns name the same states, in order."""
        self.assertEqual(list(STATES), list(annex.keyed("Run record states", "State")))
        head = annex.annex_table("Run record keys")[0]
        self.assertEqual(["Key", *STATES, "Meaning"], list(head))

    def test_the_tracked_record_holds_its_contracted_keys(self) -> None:
        """AC1. MUTANT: the close or the sign stops writing, or renames, a contracted key such as
        `report_fingerprint`, with no annex change. MUTANT: the annex contracts `signature` on
        an awaiting record. MUTANT: the parser fails on a key the annex does not name."""
        contracted = set(annex.keyed("Run record keys", "Key"))
        for state in STATES:
            record = self.records[state]
            with self.subTest(state=state):
                self.assertEqual([], conformance_problems(record, state))
                # Additions are tolerated: the record holds keys the annex leaves out, and one
                # no release wrote is no problem either.
                self.assertTrue(set(record) - contracted,
                                "the fixture record holds only contracted keys, so tolerance "
                                "of an addition is never exercised")
                self.assertEqual([], conformance_problems(
                    {**record, "a_key_no_release_wrote": [1]}, state))
        # A removal is never tolerated: the same check names the key a writer dropped.
        dropped = {k: v for k, v in self.records["Sealed"].items() if k != "report_fingerprint"}
        self.assertEqual(["Sealed: the record carries no 'report_fingerprint'"],
                         conformance_problems(dropped, "Sealed"))
        # Nor is a key holding a type its state's cell does not allow.
        self.assertEqual(["Awaiting: 'ended_at' holds a str, the annex documents 'null'"],
                         conformance_problems({**self.records["Awaiting"],
                                               "ended_at": "2026-09-24T12:00:00Z"}, "Awaiting"))
        signature = self.records["Sealed"]["signature"]
        for field, row in annex.keyed("Run record signature fields", "Field").items():
            with self.subTest(signature_field=field):
                self.assertIn(field, signature)
                self.assertIn(type(signature[field]), documented_types(row["Type"]))

    def test_the_annex_awaiting_rule_matches_the_plan_guard(self) -> None:
        """AC2. MUTANT: the annex reads awaiting as carrying no signature, which reads the
        stopped run as still open. MUTANT: the plan's guard changes with no annex change."""
        verdicts = {}
        for state in STATES:
            rc, _out, err = self.planned[state]
            refused = rc != 0
            with self.subTest(state=state):
                if refused:
                    self.assertIn(f"{RUN} awaits a signature on {REPORT}", err,
                                  "the plan was refused, but not by the awaiting guard")
                else:
                    self.assertEqual(0, rc, err)
                self.assertEqual(refused, annex_awaits(self.records[state]),
                                 f"the annex's awaiting rule and `sprint plan --write` disagree "
                                 f"on the {state.lower()} record")
            verdicts[state] = refused
        self.assertEqual({"Awaiting": True, "Sealed": False, "Stopped": False}, verdicts)


if __name__ == "__main__":
    unittest.main()
