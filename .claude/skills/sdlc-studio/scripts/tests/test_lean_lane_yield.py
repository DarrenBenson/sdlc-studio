"""US0904: each commit lane's refusals are counted against the defects they caught.

The hooks append one line per refusing lane to `sdlc-studio/.local/refusals.jsonl`. The close
joins each line to the NEXT commit after it: a code or test change there makes the refusal a
candidate catch, a change to artefacts, baselines, indexes, changelog fragments or docs alone
makes it paperwork, and a refusal no commit has followed yet is pending. The report appendix
carries the per-lane table, and a lane that refused across the last three runs without one
candidate catch is listed for deletion - listed, never enforced.

Every fixture is a throwaway git repo whose commits carry fixed committer dates, so which commit
follows which refusal is decided by the fixture, not by the clock.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

RUN = "RUN-01LANEYLD"
RETRO = "RETRO0001"


def _live(name: str):
    """The module as `sys.modules` holds it NOW, imported on first use (see test_lean_close)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _git(root: Path, *argv: str, when: str | None = None) -> None:
    env = gitutil.git_env()
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(["git", "-C", str(root), *argv], env=env, check=True, capture_output=True)


def _commit(root: Path, when: str, *paths: str) -> None:
    """One commit at `when` changing exactly `paths`."""
    for rel in paths:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"{rel} at {when}\n", encoding="utf-8")
    _git(root, "add", "--", *paths)
    _git(root, "commit", "-q", "-m", f"change at {when}", when=when)


def _refusals(root: Path, *rows: tuple) -> None:
    """`(lane, ts, staged)` or `(lane, ts, staged, blobs)` - blobs map a path to its staged id."""
    p = root / "sdlc-studio" / ".local" / "refusals.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        for lane, ts, staged, *blobs in rows:
            rec = {"lane": lane, "ts": ts, "staged": staged}
            if blobs:
                rec["blobs"] = blobs[0]
            fh.write(json.dumps(rec) + "\n")


def _blob(root: Path, text: str) -> str:
    """The id git gives `text` as a file's content - what a staged path's blob would be."""
    return subprocess.run(["git", "-C", str(root), "hash-object", "--stdin"], input=text,
                          env=gitutil.git_env(), check=True, capture_output=True,
                          text=True).stdout.strip()


def _repo(root: Path) -> None:
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", ".gitignore")
    _git(root, "commit", "-q", "-m", "base", when="2026-09-01T00:00:00Z")


def _run_state(root: Path, **over) -> None:
    state = {"schema": 1, "run_id": RUN, "started_at": "2026-09-20T08:00:00Z",
             "ended_at": "2026-09-20T18:00:00Z", "outcome": "goal-reached",
             "sprint_goal": "every lane shows what it caught", "batch": []}
    state.update(over)
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state), encoding="utf-8")


def _archive(root: Path, run_id: str, start: str, end: str) -> None:
    d = root / "sdlc-studio" / ".local" / "run-archive"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{run_id}.json").write_text(json.dumps(
        {"schema": 1, "run_id": run_id, "started_at": start, "ended_at": end,
         "outcome": "goal-reached", "sprint_goal": "an earlier run"}), encoding="utf-8")


def _section_of(report: dict) -> dict | None:
    return next((s for s in report["sections"] if s["key"] == "lane_yield"), None)


def _yield_rows(report: dict) -> dict:
    sec = _section_of(report) or {}
    return {r["yield_lane"]["value"]: {k: f["value"] for k, f in r.items()}
            for r in sec.get("rows") or []}


def _classed_run(root: Path) -> None:
    """Five refusals in one run window, each followed by a different kind of commit, and one
    before it.

    `gate`  09:00, staged a doc; the 09:30 commit changes code AND an artefact  -> catch
    `style` 10:00, staged code;  the 10:30 commit changes only paperwork        -> paperwork
    `links` 11:00;               the 11:30 commit changes a test to a new blob  -> catch
    `stamps-staged` 12:00, staged src/widget.py; the 12:30 commit carries that SAME blob and a
                                 fragment - the retry changed only paperwork  -> paperwork
    `tool-tests` 17:00;          no commit follows                              -> pending
    `budgets` the day before the run: outside every window, so not counted.
    The staged paths deliberately disagree with the next commit, so a classifier reading the
    refused commit's own paths gets `gate` and `style` the wrong way round.
    """
    _repo(root)
    _run_state(root)
    retried = _blob(root, "src/widget.py at 2026-09-20T12:30:00Z\n")
    _refusals(root,
              ("budgets", "2026-09-19T09:00:00Z", ["src/widget.py"]),
              ("gate", "2026-09-20T09:00:00Z", ["docs/notes.md"]),
              ("style", "2026-09-20T10:00:00Z", ["src/widget.py"]),
              ("links", "2026-09-20T11:00:00Z", ["tests/test_widget.py"],
               {"tests/test_widget.py": "0" * 40}),
              ("stamps-staged", "2026-09-20T12:00:00Z", ["src/widget.py"],
               {"src/widget.py": retried}),
              ("tool-tests", "2026-09-20T17:00:00Z", ["tools/thing.py"]))
    _commit(root, "2026-09-20T09:30:00Z", "src/widget.py", "sdlc-studio/stories/US0001-a.md")
    _commit(root, "2026-09-20T10:30:00Z", "sdlc-studio/stories/_index.md",
            "sdlc-studio/reports/x.html", "changelog.d/US0001.md",
            "tools/test-noise-baseline.json", "docs/notes.md", "README.md")
    _commit(root, "2026-09-20T11:30:00Z", "tests/test_widget.py")
    _commit(root, "2026-09-20T12:30:00Z", "src/widget.py", "changelog.d/US0002.md")


class LaneYieldTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        # The fixture's git calls must see the fixture, never an inherited GIT_DIR.
        patcher = unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_a_refusal_is_classed_by_the_commit_that_followed_it(self) -> None:
        """MUTANT: class a refusal by its own staged paths - `gate` reads paperwork and `style`
        a catch. MUTANT: class a commit paperwork when ANY path is paperwork - the 09:30 commit
        also touches an artefact, so `gate` reads paperwork. MUTANT: join to the commit BEFORE
        the refusal - `links` reads paperwork and `tool-tests` a catch. MUTANT: ignore the
        refused blobs - the retry that carried `stamps-staged`'s own code reads a catch.
        MUTANT: drop the `sdlc-studio/` prefix rule - the report's .html makes `style` a catch.
        MUTANT: count refusals outside the run windows - `budgets` appears."""
        _classed_run(self.root)
        rows = _yield_rows(_live("sprint_report").build_report(self.root, RETRO))
        got = {lane: (r["yield_refusals"], r["yield_catches"], r["yield_paperwork"])
               for lane, r in rows.items()}
        self.assertEqual({"gate": (1, 1, 0), "style": (1, 0, 1), "links": (1, 1, 0),
                          "stamps-staged": (1, 0, 1), "tool-tests": (1, 0, 0)}, got)

    def test_a_retry_in_the_refusals_own_second_is_classed_by_that_retry(self) -> None:
        """Git stamps a commit when it STARTS, before its hooks run, so a retry that lands in the
        same second as the refusal carries that second as its committer time. MUTANT: join on a
        commit strictly after the refusal (`when > at`) - both same-second retries read
        `pending`. MUTANT: widen the join backwards past the refusal's own second - the
        `budgets` refusal a second after the last commit reads that commit's class instead of
        `pending`. Known limit, recorded rather than checked: the stamps are whole seconds, so a
        commit that landed in the refusal's second but BEFORE it is read as its retry."""
        _repo(self.root)
        # Every refusal staged the blob the 11:00:07 commit carries, so a join that skips a
        # same-second retry lands there and reads `paperwork` (or `pending`), never `catch`.
        retried = _blob(self.root, "src/widget.py at 2026-09-20T11:00:07Z\n")
        refusals = [
            {"lane": "style", "ts": "2026-09-20T10:00:05Z", "staged": ["src/widget.py"],
             "blobs": {"src/widget.py": retried}},
            {"lane": "gate", "ts": "2026-09-20T11:00:07Z", "staged": ["src/widget.py"],
             "blobs": {"src/widget.py": retried}},
            {"lane": "budgets", "ts": "2026-09-20T11:00:08Z", "staged": ["src/widget.py"],
             "blobs": {"src/widget.py": retried}},
        ]
        _commit(self.root, "2026-09-20T10:00:05Z", "src/widget.py")
        _commit(self.root, "2026-09-20T11:00:07Z", "src/widget.py", "changelog.d/US0001.md")
        got = _live("sprint_report").classify_refusals(self.root, refusals)
        self.assertEqual(["catch", "paperwork", "pending"], got)

    def test_two_same_second_commits_are_classed_by_the_older_one(self) -> None:
        """`git log` is newest first, so two commits stamped in the same whole second arrive
        with the child (the later, truly-newer one) first. MUTANT: sort `_commits_after`'s raw
        `git log` order without reversing first - the stable sort then keeps that child ahead of
        its own same-second parent, so the refusal is classed by the LATER commit instead of the
        one that actually followed it first."""
        _repo(self.root)
        _refusals(self.root, ("gate", "2026-09-20T10:00:00Z", ["src/widget.py"]))
        # Parent: committed first, touches paperwork only. Child: committed second but stamped
        # the same second, touches code. The refusal must be classed by the parent (paperwork).
        _commit(self.root, "2026-09-20T10:00:00Z", "changelog.d/US0001.md")
        _commit(self.root, "2026-09-20T10:00:00Z", "src/widget.py")
        got = _live("sprint_report").classify_refusals(self.root, [
            {"lane": "gate", "ts": "2026-09-20T10:00:00Z", "staged": ["src/widget.py"]},
        ])
        self.assertEqual(["paperwork"], got)

    def test_the_appendix_shows_lane_yield(self) -> None:
        """MUTANT: leave the section out of either template - the table is derived and never
        shown. MUTANT: put it on the front page - it renders above the sign line."""
        _classed_run(self.root)
        sr = _live("sprint_report")
        report = sr.build_report(self.root, RETRO)
        keys = [s["key"] for s in report["sections"]]
        self.assertIn("lane_yield", sr.APPENDIX)
        self.assertGreater(keys.index("lane_yield"), keys.index("signoff"))
        md = sr.render_markdown(report)
        appendix = md.split("\n## Appendix\n", 1)[1]
        self.assertIn("### Lane yield", appendix)
        table = appendix.split("### Lane yield", 1)[1]
        self.assertRegex(table, r"(?m)^\| gate \| 1 \| 1 \| 0 \|")
        self.assertRegex(table, r"(?m)^\| style \| 1 \| 0 \| 1 \|")
        self.assertRegex(table, r"(?m)^\| tool-tests \| 1 \| 0 \| 0 \|")
        html = sr.render_html(report)
        self.assertLess(html.index("Sign-off"), html.index("Lane yield"))
        self.assertRegex(html, r"<th scope=\"row\"[^>]*>style</th><td class=\"num\">1</td>"
                               r"<td class=\"num\">0</td><td class=\"num\">1</td>")

    def test_a_lane_that_caught_nothing_in_three_runs_is_listed_not_enforced(self) -> None:
        """MUTANT: list a lane on this run's refusals alone - `gate`, which caught a defect two
        runs ago, is listed too. MUTANT: list a lane with no catch whatever its refusals were -
        `links`, whose one refusal no commit has followed yet, is listed too. MUTANT: turn the listing into a close refusal or a filed
        finding - the close's exit, its known issues, its files or its fingerprint then differ
        from the same close without the log."""
        closes = {}
        for logged in (True, False):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._closable(root, logged)
                before = self._files(root)
                rc, out, err = self._close(root)
                after = self._files(root)
                state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                                   .read_text(encoding="utf-8"))
                report = _live("sprint_report").read_report(root, state["report"])
                closes[logged] = {
                    "rc": rc, "new_files": sorted(after - before),
                    "known_issues": state.get("close_known_issues"),
                    "fingerprint": report["fingerprint"],
                    "out": re.sub(r"\S*" + re.escape(d) + r"\S*", "<root>", out),
                    "err": re.sub(r"\S*" + re.escape(d) + r"\S*", "<root>", err),
                    "rows": _yield_rows(report), "section": _section_of(report)}
        listed = {lane for lane, r in closes[True]["rows"].items()
                  if r["yield_verdict"].startswith("delete")}
        self.assertEqual({"markdown"}, listed, closes[True]["rows"])
        self.assertIn("links", closes[True]["rows"], "the pending-only lane is not shown")
        # No log at all - every consuming project - and the section is left out, not shown
        # NOT MEASURED for ever.
        self.assertIsNone(closes[False]["section"])
        for key in ("rc", "new_files", "known_issues", "fingerprint", "out", "err"):
            self.assertEqual(closes[False][key], closes[True][key], key)
        self.assertEqual(0, closes[True]["rc"], closes[True]["err"])

    def test_a_bad_or_unreadable_log_never_stops_the_close(self) -> None:
        """The measure must not be able to stop the close. MUTANT: accept a stamp with no zone
        - comparing it with the run window raises TypeError out of the close. MUTANT: read the
        log unguarded - an unreadable file raises PermissionError out of the close. MUTANT:
        drop bad lines silently - the note no longer counts them."""
        _closable_bad = self.root / "bad"
        _closable_bad.mkdir()
        self._closable(_closable_bad, True)
        log = _closable_bad / "sdlc-studio" / ".local" / "refusals.jsonl"
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"lane": "gate", "ts": "2026-09-20T11:30:00", "staged": []})
                     + "\nnot json at all\n")
        rc, _out, err = self._close(_closable_bad)
        self.assertEqual(0, rc, err)
        report = self._report(_closable_bad)
        note = _section_of(report)["figures"]["lane_yield_note"]["value"]
        self.assertIn("2 unparseable line(s)", note)
        self.assertIn("markdown", _yield_rows(report), "the good lines were lost with the bad")

        if os.geteuid() == 0:
            self.skipTest("root reads a mode-000 file, so the unreadable half cannot be staged")
        unreadable = self.root / "unreadable"
        unreadable.mkdir()
        self._closable(unreadable, True)
        log = unreadable / "sdlc-studio" / ".local" / "refusals.jsonl"
        log.chmod(0)
        self.addCleanup(log.chmod, 0o600)
        rc, _out, err = self._close(unreadable)
        self.assertEqual(0, rc, err)
        nm = _section_of(self._report(unreadable))["not_measured"]
        self.assertIn("could not be read", nm["reason"])

    def test_an_unreadable_history_reads_not_measured(self) -> None:
        """MUTANT: read a failed `git log` as no commits - every refusal reads pending and the
        page shows a clean measure that never happened. Here the tree is not a repository."""
        _run_state(self.root)
        _refusals(self.root, ("gate", "2026-09-20T09:00:00Z", ["src/widget.py"]))
        sec = _section_of(_live("sprint_report").build_report(self.root, RETRO))
        self.assertIsNotNone(sec["not_measured"], sec)
        self.assertIn("git log", sec["not_measured"]["reason"])

    # --- the close fixture -------------------------------------------------------------------

    @staticmethod
    def _report(root: Path) -> dict:
        state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                           .read_text(encoding="utf-8"))
        return _live("sprint_report").read_report(root, state["report"])

    @staticmethod
    def _files(root: Path) -> set[str]:
        rels = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        return {r for r in rels if not r.startswith(".git/")
                and r != "sdlc-studio/.local/refusals.jsonl"}

    def _closable(self, root: Path, logged: bool) -> None:
        """Three runs. `markdown` refuses once in each and every time the next commit is only
        paperwork; `gate` refuses in each, and two runs ago its next commit changed code."""
        _repo(root)
        _archive(root, "RUN-01EARLIER1", "2026-09-10T08:00:00Z", "2026-09-10T18:00:00Z")
        _archive(root, "RUN-01EARLIER2", "2026-09-15T08:00:00Z", "2026-09-15T18:00:00Z")
        _run_state(root, run_id=RUN, ended_at=None, outcome="running", goal="done",
                   batch=["US0101"], handoff=None,
                   sprint_goal_verdict={"verdict": "achieved", "note": "it did"})
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True, exist_ok=True)
        (stories / "US0101-widget.md").write_text(
            "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
            "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
            "- **Verify:** shell true\n", encoding="utf-8")
        retros = root / "sdlc-studio" / "retros"
        retros.mkdir(parents=True, exist_ok=True)
        (retros / "RETRO0001-lean.md").write_text(
            "# RETRO-0001: lean\n\n> **Date:** 2026-09-20\n\n## Delivered\n\n- US0101 - shipped\n"
            "\n## Lessons\n\n- learned a thing\n", encoding="utf-8")
        _commit(root, "2026-09-02T00:00:00Z", "src/widget.py")
        _git(root, "add", "sdlc-studio")
        _git(root, "commit", "-q", "-m", "artefacts", when="2026-09-02T00:00:01Z")
        for day, gate_next in (("10", "src/widget.py"), ("15", "docs/a.md"),
                               ("20", "docs/b.md")):
            if logged:
                _refusals(root, ("markdown", f"2026-09-{day}T09:00:00Z", ["docs/a.md"]),
                          ("gate", f"2026-09-{day}T11:00:00Z", ["src/widget.py"]))
            _commit(root, f"2026-09-{day}T10:00:00Z", f"sdlc-studio/notes-{day}.md")
            _commit(root, f"2026-09-{day}T12:00:00Z", gate_next)
        if logged:   # after the last commit: pending, and pending is not evidence of anything
            _refusals(root, ("links", "2026-09-20T13:00:00Z", ["README.md"]))

    @staticmethod
    def _close(root: Path) -> tuple[int, str, str]:
        mod = _live("sprint")
        stack = contextlib.ExitStack()
        stack.enter_context(unittest.mock.patch.object(mod, "_report_holds",
                                                       lambda *a, **k: []))
        # An open run's window ends at the page's generation time, which the fingerprint covers:
        # two closes either side of a second boundary would otherwise sign different pages.
        stack.enter_context(unittest.mock.patch.object(
            _live("sprint_report").sdlc_md, "now_iso8601", lambda *a, **k: "2026-09-24T12:00:00Z"))
        for name in mod._CLOSE_CHAIN:
            stack.enter_context(unittest.mock.patch.object(
                mod, "_close_" + name.replace("-", "_"),
                lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
        out, err = io.StringIO(), io.StringIO()
        with stack, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main(["close", "--retro", RETRO, "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()


if __name__ == "__main__":
    unittest.main()
