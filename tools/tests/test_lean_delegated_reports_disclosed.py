"""RPT0028 to RPT0034, the 6.4.0 evidence pack and the evidence page say that the seven signatures
were entered under delegation, each naming the decision that authorised it (US1295, BG1778).

The orchestrator entered those signatures in the operator's name, each on an authorisation the
decisions log records (D0504; D0640 traced each one from its seal commit). `sprint_report.py
disclose` adds the statement to a report without re-signing it, and `release_cut.py
evidence-pack` and `sprint_report.py evidence` carry it into the pack and the page.

These tests read the committed records as files. They never rebuild the pack, so a later edit to
a unit the pack covers cannot turn them red; the page is held to its generator by `--check`.
"""
# test-census-subject: sdlc-studio/reports/evidence-pack-6.4.0.md

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sprint_report  # noqa: E402


def _load_gitutil():
    """The shipped git helper, so every git call here runs with the host's git config fenced."""
    path = SCRIPTS / "tests" / "gitutil.py"
    spec = importlib.util.spec_from_file_location("_delegated_reports_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

REPORTS_REL = "sdlc-studio/reports"
REPORTS = REPO / REPORTS_REL
PACK = REPORTS / "evidence-pack-6.4.0.md"
PAGE = REPO / "docs" / "evidence.md"
SPRINT_REPORT = SCRIPTS / "sprint_report.py"

#: Each delegated report: its run, the decision that authorised its signature, the seal commit
#: that wrote its signature and run record, and its Markdown twin.
DISCLOSED = {
    "RPT0028": ("RUN-01M7061X", "D0654", "45db061c3798e8d97488d80502effb2f22aa8e84",
                "RPT0028-sprint-report-run-01m7061x.md"),
    "RPT0029": ("RUN-01M77177", "D0467", "8a199868b4000618a53fd3887342e05148a566e4",
                "RPT0029-sprint-report-run-01m77177.md"),
    "RPT0030": ("RUN-01M78TKD", "D0472", "f1b77e38ef56e8636755d57c8aa16d8d4c9ee478",
                "RPT0030-sprint-report-run-01m78tkd.md"),
    "RPT0031": ("RUN-01M7E52T", "D0475", "1787393dd6cea90cce581a771926acc03f1931b9",
                "RPT0031-sprint-report-run-01m7e52t.md"),
    "RPT0032": ("RUN-01M7EYR3", "D0479", "45b97375bcff1dac8ac822837c13fc70bad21323",
                "RPT0032-sprint-report-run-01m7eyr3.md"),
    "RPT0033": ("RUN-01M7GEHM", "D0493", "8fb4e7ebf9b2d31ab328c9169441a027a4c10ae8",
                "RPT0033-sprint-report-run-01m7gehm.md"),
    "RPT0034": ("RUN-01M7HA6R", "D0493", "e356db805d0a7882da6da82794d2e41913bde995",
                "RPT0034-sprint-report-run-01m7ha6r.md"),
}
#: The reports the 6.4.0 pack is built over, in the order its header names them.
PACK_REPORTS = list(DISCLOSED)
#: The reports whose delegation the pack must state; RPT0028 joins once the pack is rebuilt.
PACK_DISCLOSED = {k: v for k, v in DISCLOSED.items() if k != "RPT0028"}
#: A `check` past this fails the node, never skips it. RPT0030's took up to 55 s at load 7, and
#: RPT0029's 158 s alone at load 35 on eight cores, so a loaded host is not read as a failure.
CHECK_TIMEOUT = 300


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True,
                          encoding="utf-8", env=gitutil.git_env(), timeout=60)


def _show(rev: str, rel: str) -> str:
    """`rel` as the commit `rev` holds it."""
    proc = _git("show", f"{rev}:{rel}")
    if proc.returncode != 0:
        raise AssertionError(f"git show {rev[:12]}:{rel} failed: {proc.stderr.strip()}")
    return proc.stdout


def _run_record_rel(run: str) -> str:
    return f"{REPORTS_REL}/runs/{run}.json"


def _held(run: str) -> dict:
    """The signature of record: the one the run's tracked record holds."""
    return json.loads((REPO / _run_record_rel(run)).read_text(encoding="utf-8"))["signature"]


def _cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _signed_by_cell(twin: str) -> str:
    """The Signed by cell of a twin's sign-off table: the first cell of the row under its header."""
    lines = twin.splitlines()
    at = lines.index("| Signed by | Date | Fingerprint signed |")
    return _cells(lines[at + 2])[0]


def _index_rows(index: str) -> list[tuple[str, str]]:
    """`(report id, row)` for each report row of the reports index, in page order."""
    return [(m[1], m[0]) for m in re.finditer(r"^\| \[(RPT\d+)\]\(.*$", index, re.M)]


def _pack_entries(pack: str) -> list[tuple[str, list[str], list[str]]]:
    """`(heading, Accountable lines, Report lines)` for each change the pack lists."""
    entries = []
    for block in re.split(r"^(?=### )", pack, flags=re.M)[1:]:
        lines = block.splitlines()
        entries.append((lines[0], [ln for ln in lines if ln.startswith("- Accountable:")],
                        [ln for ln in lines if ln.startswith("- Report:")]))
    return entries


def _page_rows(page: str) -> dict[str, dict[str, str]]:
    """The evidence table's rows by run, each a mapping of column header to cell."""
    lines = page.splitlines()
    at = next(n for n, ln in enumerate(lines) if ln.startswith("| Run |"))
    header = _cells(lines[at])
    rows = {}
    for ln in lines[at + 2:]:
        if not ln.startswith("|"):
            break
        cells = dict(zip(header, _cells(ln)))
        rows[cells["Run"]] = cells
    return rows


def _statement(principal: str, decision: str) -> str:
    return f"{principal} (entered under delegation, authorised by decision {decision})"


class DelegatedReportsDisclosedTests(unittest.TestCase):

    def test_each_delegated_report_names_its_decision_and_checks_valid(self) -> None:
        """AC1. Each report's signature is the one its seal commit wrote plus `delegated` and its
        decision, its twin's Signed by cell states the delegation, its fingerprint and run record
        are as the seal wrote them, its index row has not moved, and `check` prints VALID."""
        # Every check starts first, so the node's wall time is the slowest single check.
        checks = {rid: subprocess.Popen(
            [sys.executable, str(SPRINT_REPORT), "--root", str(REPO), "check", "--report", rid],
            cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding="utf-8", env=gitutil.git_env()) for rid in DISCLOSED}
        try:
            index = (REPORTS / "_index.md").read_text(encoding="utf-8")
            ids = [rid for rid, _row in _index_rows(index)]
            self.assertEqual(ids, sorted(set(ids)), "the reports index lists each report once, in "
                             "id order, so no disclosure re-appended a row")
            for rid, (run, decision, seal, twin) in DISCLOSED.items():
                report = json.loads((REPORTS / f"{rid}.json").read_text(encoding="utf-8"))
                sealed = json.loads(_show(seal, f"{REPORTS_REL}/{rid}.json"))
                self.assertEqual(report["signature"], {**sealed["signature"], "delegated": True,
                                                       "decision": decision},
                                 f"{rid}'s signature is the sealed one plus its delegation")
                self.assertEqual((REPO / _run_record_rel(run)).read_text(encoding="utf-8"),
                                 _show(seal, _run_record_rel(run)),
                                 f"{run}'s run record is as its seal commit wrote it")
                held = _held(run)
                self.assertEqual(held["report"], rid)
                self.assertEqual(report["fingerprint"], held["fingerprint"],
                                 f"{rid}'s fingerprint is the one {run} signed")
                self.assertEqual(_signed_by_cell((REPORTS / twin).read_text(encoding="utf-8")),
                                 _statement(held["principal"], decision),
                                 f"{twin}'s Signed by cell")
                self.assertEqual(sprint_report.authorising_decision(REPO, decision),
                                 (decision, ""), f"{decision} is accepted in the decisions log")
                self.assertEqual(dict(_index_rows(index))[rid],
                                 dict(_index_rows(_show(seal, f"{REPORTS_REL}/_index.md")))[rid],
                                 f"{rid}'s index row is the one its seal wrote")
            for rid, proc in checks.items():
                out, err = proc.communicate(timeout=CHECK_TIMEOUT)
                self.assertEqual(proc.returncode, 0, f"check {rid}:\n{out}{err}")
                self.assertEqual(out.splitlines()[0],
                                 f"VALID: {rid} re-derives to the fingerprint it records "
                                 f"({_held(DISCLOSED[rid][0])['fingerprint']})")
        finally:
            for proc in checks.values():
                if proc.poll() is None:
                    proc.kill()
                proc.communicate()

    def test_the_evidence_pack_and_page_name_the_delegated_signatures(self) -> None:
        """AC2. Every change of a delegated report states the delegation and its decision on its
        Accountable line, the header names the seven reports and a
        commit holding the disclosures, and the page's Signed by cells say the same and pass
        `--check`."""
        pack = PACK.read_text(encoding="utf-8")
        header = re.search(r"from the records committed at `([0-9a-f]+)`, over the signed "
                           r"reports ([^.]+)\.", pack)
        self.assertIsNotNone(header, "the pack's header names its commit and its reports")
        self.assertEqual(header[2].split(", "), PACK_REPORTS)
        by_report: dict[str, list[str]] = {}
        for heading, accountable, named in _pack_entries(pack):
            self.assertEqual((len(accountable), len(named)), (1, 1),
                             f"{heading} has one Accountable line and one Report line")
            by_report.setdefault(named[0].removeprefix("- Report: ").rstrip("."),
                                 []).append(accountable[0])
        self.assertEqual(sorted(by_report), PACK_REPORTS, "each report contributes a change")
        for rid, (run, decision, _seal, _twin) in PACK_DISCLOSED.items():
            held = _held(run)
            for line in by_report[rid]:
                self.assertRegex(line, rf"entered under delegation, authorised by decision "
                                       rf"{decision}\b", f"a change from {rid}")
                self.assertRegex(line, rf"\bon {held['signed_at'][:10]}\b")
                self.assertRegex(line, rf"\bfingerprint {held['fingerprint']}\b")
        built = header[1]
        self.assertEqual(_git("merge-base", "--is-ancestor", built, "HEAD").returncode, 0,
                         f"the pack's build commit {built} is in this branch's history")
        for rid, (_run, decision, _seal, _twin) in PACK_DISCLOSED.items():
            sig = json.loads(_show(built, f"{REPORTS_REL}/{rid}.json"))["signature"]
            self.assertEqual((sig.get("delegated"), sig.get("decision")), (True, decision),
                             f"the commit the pack was built at holds {rid}'s disclosure")

        rows = _page_rows(PAGE.read_text(encoding="utf-8"))
        for rid, (run, decision, _seal, _twin) in PACK_DISCLOSED.items():
            self.assertEqual(rows[run]["Report"], rid)
            self.assertEqual(rows[run]["Signed by"], _statement(_held(run)["principal"], decision),
                             f"the page's row for {run}")
        check = subprocess.run(
            [sys.executable, str(SPRINT_REPORT), "--root", str(REPO), "evidence", "--out",
             "docs/evidence.md", "--check"], cwd=str(REPO), capture_output=True, text=True,
            encoding="utf-8", env=gitutil.git_env(), timeout=CHECK_TIMEOUT)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()
