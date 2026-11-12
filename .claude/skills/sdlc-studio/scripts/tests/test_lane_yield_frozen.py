"""US1001: the lane-yield appendix is read from the committed run record, as the close froze it.

The close reads this clone's refusal log and run archive, both under `.local/`, which no other
clone holds. It records the tally it read on the run record, and every derivation of the page,
in any clone, reads the tally from there. The run is closed through `sprint close` (its chain
steps stubbed green) and sealed through `sprint sign` (its principal check and terminal
transitions stubbed), committed, and re-built in a fresh clone holding no `.local/`. `gh` is a
stub that fails every call, so the forge is never read.

Every commit carries a fixed date, so which commit follows which refusal is the fixture's.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_sign as signing  # noqa: E402 - the stubbed seal, shared

RUN = "RUN-LEAN0001"
REPORT = "RPT0001"
RETRO = "RETRO0001"
TRACKED = f"sdlc-studio/reports/runs/{RUN}.json"
LATER = "2099-01-01T00:00:00Z"
#: The rows the close reads: `gate` caught a defect in this run and in the earlier one,
#: `markdown` drew only paperwork, and `links` refused after the last commit in the run, so it
#: is pending. Two runs on record (this one and the archived one), so no verdict is reached.
FROZEN = {"gate": (1, 1, 0), "markdown": (1, 0, 1), "links": (1, 0, 0)}
VERDICT = "too few runs: 2 of 3 recorded"


def _sr():
    import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
    return sprint_report


def _git(root: Path, *argv: str, at: str | None = None) -> None:
    extra = {"GIT_COMMITTER_DATE": at, "GIT_AUTHOR_DATE": at} if at else {}
    gitutil.git(list(argv), root, env_extra=extra, text=True)


def _commit(root: Path, message: str, at: str, *paths: str) -> None:
    """One commit at `at`: `paths` rewritten and committed, or every change when none."""
    for rel in paths:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"{rel} at {at}\n", encoding="utf-8")
    _git(root, "add", "-A", "--", *paths)
    _git(root, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m", message,
         at=at)


def _yield(section: dict | None) -> dict:
    return {r["yield_lane"]["value"]: (r["yield_refusals"]["value"], r["yield_catches"]["value"],
                                       r["yield_paperwork"]["value"], r["yield_verdict"]["value"])
            for r in (section or {}).get("rows") or []}


def _lane_yield(page: dict) -> dict | None:
    return next((s for s in page["sections"] if s["key"] == "lane_yield"), None)


class FrozenLaneYieldTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        stub = self.base / "bin"
        stub.mkdir()
        (stub / "gh").write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (self.base / "transcripts").mkdir()
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(self.base / "transcripts"),
                              HOME=str(self.base), XDG_DATA_HOME=str(self.base / "data"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)

    # --- the fixture ------------------------------------------------------------------------

    def _close(self) -> Path:
        """A run closed through `sprint close`: an earlier run in the archive, four refusals in
        the log (one in the earlier run, three in this one), its close committed."""
        root = self.base / "closer"
        root.mkdir()
        lean._fixture(root)          # the run opens 2026-09-23T00:00:00Z
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        _git(root, "init", "-q")
        _commit(root, "base", "2026-09-01T00:00:00Z")
        archive = root / "sdlc-studio" / ".local" / "run-archive"
        archive.mkdir(parents=True)
        (archive / "RUN-LEAN0000.json").write_text(json.dumps(
            {"schema": 1, "run_id": "RUN-LEAN0000", "started_at": "2026-09-20T08:00:00Z",
             "ended_at": "2026-09-20T18:00:00Z", "outcome": "goal-reached",
             "sprint_goal": "an earlier run"}), encoding="utf-8")
        log = root / "sdlc-studio" / ".local" / "refusals.jsonl"
        log.write_text("".join(json.dumps({"lane": lane, "ts": ts, "staged": [staged]}) + "\n"
                               for lane, ts, staged in (
                                   ("gate", "2026-09-20T09:00:00Z", "src/widget.py"),
                                   ("gate", "2026-09-23T00:20:00Z", "src/widget.py"),
                                   ("markdown", "2026-09-23T00:40:00Z", "docs/a.md"),
                                   ("links", "2026-09-23T00:55:00Z", "README.md"))),
                       encoding="utf-8")
        _commit(root, "a fix in the earlier run", "2026-09-20T10:00:00Z", "src/widget.py")
        _commit(root, "a fix", "2026-09-23T00:30:00Z", "src/widget.py")
        _commit(root, "a doc", "2026-09-23T00:50:00Z", "docs/a.md")
        rc, _out, err = lean._close(root)
        self.assertEqual(0, rc, err)
        _commit(root, "close paperwork", LATER)
        return root

    @staticmethod
    def _page(root: Path) -> dict:
        return json.loads((root / "sdlc-studio" / "reports" / f"{REPORT}.json")
                          .read_text(encoding="utf-8"))

    # --- the criteria -----------------------------------------------------------------------

    def test_close_freezes_the_tally_on_the_run_record(self) -> None:
        """AC1. Mutant: `_lane_yield_section` re-reading the refusal log at every derivation
        and citing it - the record carries no tally and every figure names `.local/`. Mutant:
        the freezer reading no run archive - every verdict reads 1 of 3 runs."""
        root = self._close()
        expected = {lane: (*counts, VERDICT) for lane, counts in FROZEN.items()}
        for where, record in (("live", root / "sdlc-studio" / ".local" / "run-state.json"),
                              ("tracked", root / TRACKED)):
            frozen = json.loads(record.read_text(encoding="utf-8")).get("lane_yield")
            self.assertIsInstance(frozen, dict, f"the {where} run record carries no tally")
            self.assertEqual(expected, {r["lane"]: (r["refusals"], r["catches"], r["paperwork"],
                                                    r["verdict"]) for r in frozen["rows"]}, where)
        page = self._page(root)
        section = _lane_yield(page)
        self.assertEqual(expected, _yield(section))
        figures = [*section["figures"].values(), *(f for r in section["rows"] for f in r.values())]
        self.assertEqual(16, len(figures))
        for f in figures:
            self.assertEqual([TRACKED, "git log"], f["source"].split(", "), f)
        self.assertIn("this clone's refusal log as the close read it",
                      section["figures"]["lane_yield_note"]["value"])
        named = [(s, k, f) for s, k, f in _sr().leaf_figures(page)
                 if ".local/" in json.dumps(f)]
        self.assertEqual([], named, "a figure on the page names a path under .local/")
        unmeasured = [s["not_measured"] for s in page["sections"] if s.get("not_measured")]
        self.assertNotIn(".local/", json.dumps(unmeasured))

    def test_a_fresh_clone_reads_the_frozen_tally(self) -> None:
        """AC2. Mutant: return no section when the clone holds no refusal log, as before the
        freeze - the section is shown only on the closing machine. Mutant: re-read the log
        whenever it exists and the record only when it does not - unchanged here, but the
        `links` refusal the close read as pending is paperwork against the commits since."""
        root = self._close()
        rc, _out, err = signing._sign(root, REPORT)
        self.assertEqual(0, rc, err)
        _commit(root, "seal", LATER)
        clone = self.base / "clone"
        _git(self.base, "clone", "-q", f"file://{root}", str(clone))
        self.assertFalse((clone / "sdlc-studio" / ".local").exists())
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _sr().main(["--root", str(clone), "build", "--run", RUN, "--id", RETRO,
                             "--format", "json"])
        self.assertEqual(0, rc, err.getvalue())
        built = _lane_yield(json.loads(out.getvalue()))
        filed = _lane_yield(self._page(clone))
        self.assertIsNotNone(built, "the fresh clone's page has no lane-yield section")
        self.assertEqual({lane: (*counts, VERDICT) for lane, counts in FROZEN.items()},
                         _yield(filed))
        self.assertEqual(filed["rows"], built["rows"])
        self.assertEqual(filed["figures"], built["figures"])
        # In the closing clone, whose log the history has moved past, the record still decides.
        with contextlib.redirect_stdout(io.StringIO()) as again:
            self.assertEqual(0, _sr().main(["--root", str(root), "build", "--run", RUN, "--id",
                                            RETRO, "--format", "json"]))
        self.assertEqual(filed["rows"], _lane_yield(json.loads(again.getvalue()))["rows"])


if __name__ == "__main__":
    unittest.main()
