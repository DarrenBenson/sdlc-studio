"""US1068: a learning reaches a brief only once a signed close has listed it.

The close lists each approved learning not yet live and stamps it Listed-in with the run;
`sprint.py sign --strike M-NNNN --strike-reason ...` strikes any the close listed as it seals
the run. A brief carries a learning only while the run that listed it is signed, by the record
every clone holds, and has not struck it, so a reopened run holds its learnings until it is
signed again. Driven through `sprint.main`, `critic.py brief` and `persona_memory.py list` in
throwaway projects.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")

RUN = "RUN-STRIKE0001"
QA = "Sam Eriksson (qa)"
PRODUCT = "Lena Marsh (product)"
BUILDER = "Dani Okafor (engineering)"
CARD = ("<!-- role: {role} -->\n# {holder} - {role} seat\n\n## Lens\n\nx\n\n"
        "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path) -> dict:
    """A git work tree holding two reviewed units ready to seal, three seat cards, a retro over
    the batch and an open run whose close filed RPT0001."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True, timeout=60,
                   env=gitutil.git_env())
    for role, holder in (("engineering", "Dani Okafor"), ("qa", "Sam Eriksson"),
                         ("product", "Lena Marsh")):
        _write(root, f"sdlc-studio/personas/seats/{role}.md", CARD.format(role=role,
                                                                           holder=holder))
    report = {"stories": {}}
    for uid in ("US0101", "US0102"):
        _write(root, f"sdlc-studio/stories/{uid}-x.md",
               f"# {uid}: unit\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")
        report["stories"][f"{uid}-x"] = {"failed": 0, "stale": 0, "failures": [],
                                         "ac_count": 1, "verified_at": "2099-01-01T00:00:00Z"}
        _live("critic").record_verdict(root, uid, "APPROVE", reviewer=QA, author=BUILDER,
                                       issues="probed the edges; none blocking")
    _write(root, "sdlc-studio/.local/verify-report.json", json.dumps(report))
    _write(root, "sdlc-studio/retros/RETRO0001-run.md",
           "# RETRO0001: run\n\n> **Date:** 2026-11-15\n> **Batch:** US0101, US0102\n\n"
           "## Lessons\n\n- learned a thing\n")
    state = {"schema": 1, "run_id": RUN, "started_at": "2026-11-14T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done",
             "batch": ["US0101", "US0102"], "handoff": None, "report": "RPT0001",
             "sprint_goal": "struck learnings stay out",
             "sprint_goal_verdict": {"verdict": "achieved", "note": "they did"}}
    _write(root, "sdlc-studio/.local/run-state.json", json.dumps(state))
    return state


def _learning(root: Path, key: str, title: str, approver: str) -> str:
    pm = _live("persona_memory")
    entry = pm.add(root, key, title, f"{title}, in prose.", ["US0101"])
    pm.set_field(root, entry["id"], "State", "approved")
    pm.set_field(root, entry["id"], "Approved-by", approver)
    return entry["id"]


def _cli(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _close_lists(root: Path) -> None:
    """The close's persona-memory stage, as `sprint close` runs it."""
    mod = _live("sprint")
    with contextlib.redirect_stdout(io.StringIO()):
        ok, detail, _ = mod._close_persona_memory(root, "RETRO0001", mod.run_state.read(root))
    assert ok, detail


def _close(root: Path) -> None:
    """`sprint close` through `sprint.main`, every chain step but `persona-memory` stubbed
    green: the close lists the learnings and files the run's tracked record, still running."""
    mod = _live("sprint")
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
        for name in mod._CLOSE_CHAIN:
            if name != "persona-memory":
                stack.enter_context(unittest.mock.patch.object(
                    mod, "_close_" + name.replace("-", "_"),
                    lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
        rc, out, err = _cli(root, "close", "--retro", "RETRO0001")
    assert rc == 0, out + err


def _sign(root: Path, *extra: str) -> tuple[int, str, str]:
    """`sprint sign` over the page the run's last close filed (a re-close files a new one)."""
    report = _live("sprint").run_state.read(root).get("report") or "RPT0001"
    return _cli(root, "sign", "--report", report, "--principal", "Darren", *extra)


def _script(root: Path, script: str, *argv: str) -> str:
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root", str(root)],
                       capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                       check=False)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _brief(root: Path, seat: str) -> str:
    return _script(root, "critic.py", "brief", "--unit", "US0101", "--seat", seat)


def _fields(root: Path, entry_id: str) -> dict:
    for entries in _live("persona_memory").all_stores(root).values():
        for e in entries:
            if e["id"] == entry_id:
                return e["fields"]
    raise AssertionError(f"no store holds {entry_id}")


def _memory_bytes(root: Path) -> dict:
    return {p.name: p.read_bytes()
            for p in sorted((root / "sdlc-studio" / "personas" / "memory").glob("*.md"))}


def _record(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / "reports" / "runs" / f"{RUN}.json")
                      .read_text(encoding="utf-8"))


class StrikeLearningTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _project(self.root)
        self.qa = _learning(self.root, "qa", "A retry loop hides a race", PRODUCT)
        self.product = _learning(self.root, "product", "Name the user", QA)

    def test_a_struck_learning_never_reaches_the_brief(self) -> None:
        """AC1. MUTANTS: the strike written only to the run record, or only to memory, where
        the renderer does not read; the strike recorded without its principal, date or
        reason; every listed learning struck."""
        root = self.root
        _close_lists(root)
        rc, out, err = _sign(root, "--strike", self.qa, "--strike-reason", "it loosens the bar")
        self.assertEqual(0, rc, out + err)
        today = _live("lib.sdlc_md").now_date()
        state = _live("sprint").run_state.read(root)
        self.assertEqual("goal-reached", state["outcome"])
        self.assertEqual("Darren", state["signature"]["principal"])
        struck = [{"id": self.qa, "principal": "Darren", "date": today,
                   "reason": "it loosens the bar"}]
        self.assertEqual(struck, state.get("persona_learnings_struck"))
        self.assertEqual(struck, _record(root).get("persona_learnings_struck"))
        self.assertEqual("goal-reached", _record(root)["outcome"])
        field = _fields(root, self.qa).get("struck", "")
        for part in ("Darren", today, "it loosens the bar"):
            self.assertIn(part, field)
        self.assertNotIn("struck", _fields(root, self.product))
        self.assertNotIn(self.qa, _brief(root, "qa"))
        self.assertIn(f"{self.product} Name the user", _brief(root, "product"))
        # The sealed record alone keeps it out: a Struck field emptied by hand does not revive it.
        _live("persona_memory").set_field(root, self.qa, "Struck", "")
        self.assertNotIn(self.qa, _brief(root, "qa"))
        _live("persona_memory").strike(root, self.qa, "Darren", today, "it loosens the bar")
        [line] = [ln for ln in _script(root, "persona_memory.py", "list", "--persona", "qa")
                  .splitlines() if self.qa in ln]
        self.assertIn("struck", line)

    def test_a_learning_of_an_unsigned_run_is_held(self) -> None:
        """AC2. MUTANTS: approved learnings carried before the signature; the held learning
        dropped silently, so the brief cannot be told from one with none; any filed record read
        as signed, so the record the close files carries what nobody has signed."""
        root = self.root
        _close(root)
        record = _record(root)
        self.assertEqual("running", record.get("outcome"), "the close filed no running record")
        self.assertIsNone(record.get("signature"))
        self.assertEqual([self.qa, self.product], record.get("persona_learnings_listed"))
        brief = _brief(root, "qa")
        self.assertNotIn(self.qa, brief)
        self.assertIn("1 approved learning awaits its run's signature", brief)

    def test_a_reopened_run_holds_its_learnings_until_resigned(self) -> None:
        """AC3. MUTANTS: signed stamped into memory at the seal, so a reopened run's learnings
        stay live while the signature they relied on is broken; the re-sign's strike dropped
        because the first signature listed the learning; the outcome left unread, so the record
        the re-close files, running but still bearing the first signature, reads as signed."""
        root = self.root
        _close(root)
        rc, out, err = _sign(root)
        self.assertEqual(0, rc, out + err)
        self.assertIn(self.product, _brief(root, "product"), "a signed learning is not carried")
        rc, out, err = _cli(root, "reopen", "--reason", "a late review belongs to this run")
        self.assertEqual(0, rc, out + err)
        held = _brief(root, "product")
        self.assertNotIn(self.product, held)
        self.assertIn("1 approved learning awaits its run's signature", held)
        _close(root)
        record = _record(root)
        self.assertEqual("running", record.get("outcome"), "the re-close filed no running record")
        self.assertEqual("Darren", (record.get("signature") or {}).get("principal"),
                         "the re-close dropped the first signature, so this pins nothing")
        held = _brief(root, "product")
        self.assertNotIn(self.product, held, "a re-closed run's learning is carried unsigned")
        self.assertIn("1 approved learning awaits its run's signature", held)
        rc, out, err = _sign(root, "--strike", self.product, "--strike-reason", "it overreaches")
        self.assertEqual(0, rc, out + err)
        self.assertNotIn(self.product, _brief(root, "product"))
        self.assertIn("Darren", _fields(root, self.product).get("struck", ""))
        self.assertEqual([self.product],
                         [s["id"] for s in _record(root).get("persona_learnings_struck") or []])
        self.assertIn(self.qa, _brief(root, "qa"), "the re-sign lost the unstruck learning")

    def test_a_resign_keeps_the_earlier_signatures_strikes(self) -> None:
        """A re-sign adds its own strike to the run's struck list and keeps the first
        signature's. MUTANT: the struck list rewritten with the re-sign's strikes alone."""
        root = self.root
        _close(root)
        rc, out, err = _sign(root, "--strike", self.qa, "--strike-reason", "first")
        self.assertEqual(0, rc, out + err)
        rc, out, err = _cli(root, "reopen", "--reason", "a late review belongs to this run")
        self.assertEqual(0, rc, out + err)
        _close(root)
        rc, out, err = _sign(root, "--strike", self.product, "--strike-reason", "second")
        self.assertEqual(0, rc, out + err)
        self.assertEqual([(self.qa, "first"), (self.product, "second")],
                         [(s["id"], s["reason"])
                          for s in _record(root).get("persona_learnings_struck") or []])
        self.assertNotIn(self.qa, _brief(root, "qa"))
        self.assertNotIn(self.product, _brief(root, "product"))

    def test_a_bad_strike_refuses_the_seal_and_writes_nothing(self) -> None:
        """AC4. MUTANTS: the strike checked after the seal is written; a partial strike applied
        for the one good id; only the first bad id named."""
        root = self.root
        # Listed by another run, already signed, so this close does not list it.
        other = _learning(root, "qa", "Listed elsewhere", PRODUCT)
        _live("persona_memory").set_field(root, other, "Listed-in", "RUN-OTHER")
        _write(root, "sdlc-studio/reports/runs/RUN-OTHER.json", json.dumps({
            "schema": 1, "run_id": "RUN-OTHER", "outcome": "goal-reached",
            "signature": {"principal": "Darren"}, "persona_learnings_listed": [other]}))
        _close_lists(root)
        self.assertEqual([self.qa, self.product],
                         _live("sprint").run_state.read(root).get("persona_learnings_listed"))
        before = _memory_bytes(root)
        for case, argv, named in (
                ("bad ids", ("--strike", self.qa, "--strike", other, "--strike", "M-0099",
                             "--strike-reason", "x"), (other, "M-0099", "RUN-OTHER")),
                ("no reason", ("--strike", self.qa), ("--strike-reason",))):
            with self.subTest(case=case):
                rc, out, err = _sign(root, *argv)
                self.assertEqual(2, rc, out + err)
                for name in named:
                    self.assertIn(name, err)
                state = _live("sprint").run_state.read(root)
                self.assertEqual("running", state["outcome"], "the run was sealed")
                self.assertIsNone(state.get("signature"))
                self.assertIsNone(state.get("persona_learnings_struck"))
                self.assertEqual(before, _memory_bytes(root), "a memory file changed")
                text = (root / "sdlc-studio" / "stories" / "US0101-x.md").read_text()
                self.assertIn("> **Status:** Review", text, "a unit was sealed")


if __name__ == "__main__":
    unittest.main()
