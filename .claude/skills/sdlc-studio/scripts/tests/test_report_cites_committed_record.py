"""US0997: a report the close files cites the committed run record, never `.local/run-state.json`.

The run is closed through `sprint close` (its chain steps stubbed green) and sealed through
`sprint sign` (its principal check and terminal transitions stubbed), committed, and read in a
fresh clone that holds no `.local/`. `gh` is a stub: `gh run ...` prints a file when the test
names one, and every call fails otherwise, so the CI runs the close freezes are the test's own.
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
TRACKED = f"sdlc-studio/reports/runs/{RUN}.json"
LOCAL = "sdlc-studio/.local/run-state.json"
LATER = "2099-01-01T00:00:00Z"
#: Inside the fixture's window (it opens 2026-09-23T00:00:00Z), so the history holds the two
#: commits the lead time is counted from whether or not the base commit falls inside it.
IN_WINDOW = ("2026-09-23T00:30:00Z", "2026-09-23T00:50:00Z")
#: Two push-triggered runs inside the window: one red, one green after it. Deployment
#: frequency, change failure rate and time to restore are all read from them.
RUNS = [{"databaseId": 11, "event": "push", "conclusion": "failure", "headBranch": "main",
         "headSha": "a" * 40, "workflowName": "ci", "createdAt": "2026-09-23T00:20:00Z",
         "updatedAt": "2026-09-23T00:25:00Z"},
        {"databaseId": 12, "event": "push", "conclusion": "success", "headBranch": "main",
         "headSha": "b" * 40, "workflowName": "ci", "createdAt": "2026-09-23T00:40:00Z",
         "updatedAt": "2026-09-23T00:45:00Z"}]
FROM_RUNS = ("Deployment frequency", "Change failure rate", "Time to restore")


def _sr():
    import sprint_report  # noqa: PLC0415 - bound at call time, as the suite loads it
    return sprint_report


class CommittedRecordCitationTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        stub = self.base / "bin"
        stub.mkdir()
        (stub / "gh").write_text(
            '#!/bin/sh\nif [ "$1" = run ] && [ -f "$GH_RUNS" ]; then cat "$GH_RUNS"; exit 0; fi\n'
            "exit 1\n", encoding="utf-8")
        (stub / "gh").chmod(0o755)
        (self.base / "transcripts").mkdir()
        (self.base / "runs.json").write_text(json.dumps(RUNS), encoding="utf-8")
        env = gitutil.git_env(PATH=f"{stub}{os.pathsep}{os.environ.get('PATH', '')}",
                              SDLC_STUDIO_TRANSCRIPTS=str(self.base / "transcripts"))
        patch = unittest.mock.patch.dict(os.environ, env, clear=True)
        patch.start()
        self.addCleanup(patch.stop)

    # --- the fixture ------------------------------------------------------------------------

    @staticmethod
    def _git(root: Path, *argv: str, at: str | None = None):
        extra = {"GIT_COMMITTER_DATE": at, "GIT_AUTHOR_DATE": at} if at else {}
        return gitutil.git(list(argv), root, env_extra=extra, text=True)

    def _commit(self, root: Path, message: str, at: str = LATER) -> None:
        self._git(root, "add", "-A")
        self._git(root, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty", "-m",
                  message, at=at)

    def _close(self, name: str, forge: bool = True) -> Path:
        """A run closed through `sprint close` in a fresh repository, its close committed. With
        `forge`, `gh run list` answers `RUNS` and the close freezes them on the record; without,
        it fails and the close freezes the failure."""
        root = self.base / name
        root.mkdir()
        lean._fixture(root)
        signing._git_repo(root)
        for at in IN_WINDOW:
            self._commit(root, f"a change inside the run window at {at}", at=at)
        os.environ.pop("GH_RUNS", None)
        if forge:
            os.environ["GH_RUNS"] = str(self.base / "runs.json")
        rc, _out, err = lean._close(root)
        self.assertEqual(0, rc, err)
        self._commit(root, "close paperwork")
        return root

    def _sign(self, root: Path) -> None:
        rc, _out, err = signing._sign(root, REPORT)
        self.assertEqual(0, rc, err)
        self._commit(root, "seal")

    def _clone(self, root: Path) -> Path:
        dest = self.base / f"{root.name}-clone"
        self._git(self.base, "clone", "-q", f"file://{root}", str(dest))
        self.assertFalse((dest / "sdlc-studio" / ".local").exists())
        return dest

    @staticmethod
    def _page(root: Path) -> dict:
        return json.loads((root / "sdlc-studio" / "reports" / f"{REPORT}.json")
                          .read_text(encoding="utf-8"))

    @staticmethod
    def _check(root: Path) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = _sr().main(["--root", str(root), "check", "--report", REPORT])
        return rc, out.getvalue() + err.getvalue()

    @staticmethod
    def _sources(page: dict) -> dict[str, str]:
        return {f"{s}.{k}": str(f.get("source"))
                for s, k, f in _sr().leaf_figures(page) if isinstance(f, dict)}

    @staticmethod
    def _dora(page: dict) -> dict[str, dict]:
        rows = {s["key"]: s for s in page["sections"]}["dora"]["rows"]
        return {r["dora_key"]["value"]: r for r in rows}

    # --- the criteria -----------------------------------------------------------------------

    def test_close_cites_the_tracked_run_record(self) -> None:
        """AC1. Mutant: `build_report` citing the path `_run_state_for` read the record from,
        which at a close is the live `.local/run-state.json`."""
        root = self._close("closer")
        page = self._page(root)
        sources = self._sources(page)
        local = {k: v for k, v in sources.items() if ".local/run-state.json" in v
                 or ".local/run-archive" in v}
        self.assertEqual({}, local, "a figure the close filed cites the closer's .local")
        for key in ("goal.sprint_goal", "goal.run_id", "goal.goal_verdict",
                    "delivered.planned_units", "delivered.unit_outcome[0]"):
            self.assertEqual(TRACKED, sources[key], key)
        cited = [k for k, v in sources.items() if TRACKED in v.split(", ")]
        self.assertGreater(len(cited), 20, "the run record is cited by too few figures")
        # The not-measured reasons: each names the source it consulted, and the twin prints it.
        unmeasured = {s["key"]: s["not_measured"]["source"] for s in page["sections"]
                      if s.get("not_measured")}
        self.assertTrue(any(v == TRACKED for v in unmeasured.values()), unmeasured)
        self.assertNotIn(LOCAL, json.dumps(unmeasured))
        twin = next((root / "sdlc-studio" / "reports").glob(f"{REPORT}-*.md"))
        text = twin.read_text(encoding="utf-8")
        self.assertIn(f"(consulted {TRACKED})", text)
        self.assertNotIn(LOCAL, text, "the Markdown twin names the closer's .local record")

    def test_frozen_ci_figures_cite_the_tracked_record(self) -> None:
        """AC2. Mutant: `_ci_runs` returning the frozen reading's own source alone, so every
        DORA figure read from the frozen runs cites a command and no committed file."""
        for forge, reading in ((True, "gh run list"), (False, "gh run list - exit 1")):
            with self.subTest(forge=forge):
                root = self._close("forge" if forge else "no-forge", forge=forge)
                frozen = json.loads((root / LOCAL).read_text(encoding="utf-8"))["ci_runs"]
                self.assertEqual(reading, frozen["source"])        # the forge reading itself
                self.assertEqual(2 if forge else 0, len(frozen["runs"]))
                dora = self._dora(self._page(root))
                from_runs = [k for k in FROM_RUNS if k in dora]
                self.assertEqual(list(FROM_RUNS), from_runs)
                checked = 0
                for key in from_runs:
                    if not forge and key == "Deployment frequency":
                        continue          # with no run it is counted from git history
                    for name, f in dora[key].items():
                        self.assertEqual(f"{TRACKED}, {reading}", f["source"], f"{key} {name}")
                        checked += 1
                self.assertGreaterEqual(checked, 10 if forge else 5, "too few DORA figures read")
                lead = dora["Lead time for changes"]
                self.assertEqual({"git log"}, {f["source"] for f in lead.values()},
                                 "a figure counted from git history stopped citing it")
                if not forge:
                    self.assertEqual({"git log"}, {f["source"] for f in
                                                   dora["Deployment frequency"].values()})

    def test_the_cited_record_opens_in_a_fresh_clone(self) -> None:
        """AC3. Mutants: cite the `.local` run archive, or a record name built other than by
        `run_state.tracked_path`; either names a file the fresh clone does not hold."""
        root = self._close("signer")
        self._sign(root)
        clone = self._clone(root)
        page = self._page(clone)
        cited = {part for v in self._sources(page).values() for part in v.split(", ")
                 if "run-state" in part or part.startswith("sdlc-studio/reports/runs/")
                 or ".local/" in part}
        self.assertEqual({TRACKED}, cited, "the page cites a run record other than the tracked one")
        record = clone / TRACKED
        self.assertTrue(record.is_file(), f"{TRACKED} is not in the fresh clone")
        signature = json.loads(record.read_text(encoding="utf-8")).get("signature")
        self.assertTrue(signature and signature.get("principal"), signature)
        self.assertEqual(page["signature"], signature)
        rc, out = self._check(clone)
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {REPORT}", out)

    def test_a_page_citing_local_still_checks_valid(self) -> None:
        """AC4. Mutants: compare each figure's source on re-derivation, or refuse a `.local`
        source at check; either turns every page signed before this change INVALID."""
        sr = _sr()
        # Filed under the rule every earlier page was: cite the path the record was read from.
        with unittest.mock.patch.object(sr, "_cited_record",
                                        lambda _root, _state, read_rel: read_rel):
            before = self._close("before")
        self._sign(before)
        after = self._close("after")
        self._sign(after)
        for root, cites_local in ((before, True), (after, False)):
            with self.subTest(page=root.name):
                clone = self._clone(root)
                sources = self._sources(self._page(clone))
                self.assertEqual(cites_local, any(v == LOCAL for v in sources.values()))
                self.assertEqual(not cites_local, any(v == TRACKED for v in sources.values()))
                rc, out = self._check(clone)
                self.assertEqual(0, rc, out)
                self.assertIn(f"VALID: {REPORT}", out)


if __name__ == "__main__":
    unittest.main()
