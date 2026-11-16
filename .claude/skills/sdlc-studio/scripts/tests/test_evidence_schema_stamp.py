"""Each committed report and run record states the evidence-schema version it was written under.

The filed page carries `evidence_schema`, the version `reference-evidence-schema.md`'s masthead
states, and the tracked run record copies it from the page it names, so a record sealed after an
upgrade keeps the version its page was stamped with. A page filed before the stamp still checks.
The runs are closed through `sprint close` and signed through `sprint sign` in a throwaway git
repository, as `test_evidence_annex_report` closes its own; the seal's unit moves are stubbed
green, as `test_lean_sign` stubs them, because what is under test is what lands on disk.
"""
from __future__ import annotations

import contextlib
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
import gitutil
import sprint_report
import test_evidence_annex_report as annex
from lib import run_state

KEY = "evidence_schema"
_MASTHEAD = re.compile(r"^> \*\*Annex version (\S+?)\.\*\*", re.M)


def masthead_version() -> str:
    found = _MASTHEAD.findall(annex.ANNEX.read_text(encoding="utf-8"))
    if len(found) != 1:
        raise AssertionError(f"the annex states {len(found)} masthead versions")
    return found[0]


def _commit_all(root: Path, message: str) -> None:
    annex._git(root, "add", "-A")
    annex._git(root, "commit", "-q", "--allow-empty", "-m", message)


def _sign(root: Path, report_id: str) -> None:
    mod = annex._live("sprint")
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.object(mod, "_principal_refusals", lambda *a, **k: []), \
            unittest.mock.patch.object(mod, "_seal_units", lambda *a, **k: 0), \
            unittest.mock.patch.object(mod, "_cascade_after_signature", lambda *a, **k: None), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(["sign", "--report", report_id, "--principal", "Maya", "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"sprint sign refused ({rc}):\n{out.getvalue()}\n{err.getvalue()}")


def _check(root: Path, report_id: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        annex._live("sprint_report").main(["--root", str(root), "check", "--report", report_id])
    return out.getvalue() + err.getvalue()


class EvidenceSchemaStampTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        patcher = unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _signed(self, name: str, *, at_close: dict | None = None,
                at_sign: dict | None = None, unstamped: bool = False) -> tuple[Path, str]:
        """Close, commit, sign and commit a fixture run. `at_close` and `at_sign` patch
        `sprint_report` attributes for that step; `unstamped` files the page as a writer from
        before the stamp did, with no `evidence_schema` on it."""
        root = self.tmp / name
        root.mkdir()
        annex._run(root, False)
        # Patch the module `sprint` will import at call time, never the one this file imported at
        # load: another test may have put a fresh module in sys.modules since (BG1506).
        live = annex._live("sprint_report")
        with contextlib.ExitStack() as stack:
            for attr, value in (at_close or {}).items():
                stack.enter_context(unittest.mock.patch.object(live, attr, value))
            if unstamped:
                real = live.build_report

                def earlier(*a, **k):
                    page = real(*a, **k)
                    page.pop(KEY, None)
                    return page
                stack.enter_context(unittest.mock.patch.object(live, "build_report", earlier))
            page = annex._close(root)
        if unstamped:
            # A live record carrying a stamp of its own, as one taken up from another clone
            # could: the record still copies the page, which has none.
            run_state.update(root, **{KEY: "9.9"})
        _commit_all(root, "close paperwork")
        with contextlib.ExitStack() as stack:
            for attr, value in (at_sign or {}).items():
                stack.enter_context(unittest.mock.patch.object(annex._live("sprint_report"), attr,
                                                               value))
            _sign(root, page["report_id"])
        _commit_all(root, "signed")
        return root, page["report_id"]

    def _cloned(self, root: Path, report_id: str) -> tuple[dict, dict]:
        """The filed page and the tracked run record, as a fresh clone reads them."""
        clone = self.tmp / f"{root.name}-clone"
        subprocess.run(["git", "clone", "-q", str(root), str(clone)], env=gitutil.git_env(),
                       check=True, capture_output=True)
        page = json.loads((clone / "sdlc-studio" / "reports" / f"{report_id}.json")
                          .read_text(encoding="utf-8"))
        record = json.loads(run_state.tracked_path(clone, page["run_id"])
                            .read_text(encoding="utf-8"))
        return page, record

    def test_report_and_run_record_carry_the_annex_version(self) -> None:
        """AC1. MUTANT: drop the stamp from `build_report`, or from `file_tracked`, or move the
        constant off the masthead - the clone reads a missing or different version."""
        root, report_id = self._signed("run")
        page, record = self._cloned(root, report_id)
        self.assertTrue(record.get("signature"), "the record was not sealed")
        self.assertEqual(masthead_version(), page.get(KEY))
        self.assertEqual(masthead_version(), record.get(KEY))

    def test_the_record_keeps_its_pages_version_across_an_upgrade(self) -> None:
        """AC2. MUTANT: stamp the record with the version current at the sign rather than the
        page's - the sealed record reads 1.1."""
        root, report_id = self._signed("upgrade", at_close={"EVIDENCE_SCHEMA_VERSION": "1.0"},
                                       at_sign={"EVIDENCE_SCHEMA_VERSION": "1.1"})
        page, record = self._cloned(root, report_id)
        self.assertTrue(record.get("signature"), "the record was not sealed")
        self.assertEqual("1.0", page.get(KEY))
        self.assertEqual("1.0", record.get(KEY))
        self.assertIn(f"VALID: {report_id}", _check(root, report_id))

    def test_an_unstamped_page_still_checks_valid(self) -> None:
        """AC3. MUTANT: re-derive every page with the stamp as a figure, or refuse a page that
        lacks it - the earlier page reads INVALID or does not check."""
        before, before_id = self._signed("before", unstamped=True)
        after, after_id = self._signed("after")
        for root, report_id in ((before, before_id), (after, after_id)):
            out = _check(root, report_id)
            self.assertRegex(out, rf"(?m)^VALID: {report_id}\b", out)
        before_page, before_record = self._cloned(before, before_id)
        after_page, _record = self._cloned(after, after_id)
        self.assertNotIn(KEY, before_page)
        self.assertNotIn(KEY, before_record, "the record states a version its page never had")
        self.assertIn(KEY, after_page)

    def test_the_annex_states_its_compatibility_policy(self) -> None:
        """AC4. MUTANT: drop a clause of the policy, or write the masthead as `1` - the reading
        fails."""
        self.assertRegex(masthead_version(), r"^\d+\.\d+$")
        self.assertEqual(sprint_report.EVIDENCE_SCHEMA_VERSION, masthead_version())
        policy = [s for s in re.split(r"(?<=\.)\s+",
                                      " ".join(" ".join(annex._block("Versioning")).split()))]

        def stated(*words: str) -> bool:
            return any(all(w in s for w in words) for s in policy)
        self.assertTrue(stated("added field", "minor"), "an added field is a minor bump")
        self.assertTrue(stated("removed or renamed field", "major", "migration note"),
                        "a removed or renamed field is a major bump with a migration note")
        self.assertTrue(stated("consumer", "must tolerate", "unknown keys"),
                        "a consumer must tolerate unknown keys")
        self.assertTrue(stated(KEY, "run record"), "the stamp is stated for the run record")


if __name__ == "__main__":
    unittest.main()
