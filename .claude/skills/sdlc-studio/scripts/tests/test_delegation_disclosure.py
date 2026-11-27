"""`sprint_report.py disclose`: a delegation statement added to a report already signed.

A signature entered on the principal's behalf before `sprint sign --delegated` existed carries
no statement. The command writes `delegated` and the decision onto the report's signature and
re-renders its twin, never the tracked run record, so the sealed signature, its fingerprint and
`check` stand; the evidence pack accepts that report-side delegation when the decisions log
committed at the revision built holds its decision as accepted, and the evidence page names
each run's signer as the report's Signed by cell gives it.

Every fixture is a throwaway project whose reports are derived from a run and signed through
`sprint.py`'s own signature writer; the commands run through their shipped entry points.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402 - confined, hermetic git for fixtures
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

import command_audit  # noqa: E402
import decisions  # noqa: E402
from lib import run_state  # noqa: E402

sr = lean.sr
SKILL = SCRIPTS.parent
REPO = SKILL.parents[2]
SPRINT_REPORT = SCRIPTS / "sprint_report.py"
RELEASE_CUT = SCRIPTS / "release_cut.py"
PRINCIPAL = "Maya Okafor"
RUN_A, RUN_B, RUN_C = lean.RUN, "RUN-02SECOND", "RUN-03THIRD"
BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
PACK_REL = "sdlc-studio/reports/evidence-pack-1.0.0.md"


def delegated(decision: str) -> str:
    return f"{PRINCIPAL} (entered under delegation, authorised by decision {decision})"


def _git(root: Path, *args: str) -> None:
    gitutil.git(list(args), root)


def _commit(root: Path, message: str, *paths: str) -> None:
    _git(root, "add", "-A", *(["--", *paths] if paths else []))
    _git(root, "-c", "commit.gpgsign=false", "commit", "-qm", message)


def _file_run(root: Path, run_id: str, *, sign: bool = True, decision: str | None = None,
              tracked: bool = True) -> str:
    """File the report of run `run_id` and sign it through the seal's own signature writer,
    filing the tracked run record as the seal does. Returns the report id."""
    import sprint  # noqa: PLC0415 - the seal's signature writer, not a hand-made one
    path = root / "sdlc-studio" / ".local" / "run-state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    state["run_id"] = run_id
    state.pop("signature", None)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    rid = sr.file_report(root, sr.build_report(root, lean.RETRO))
    if sign:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            sprint._write_the_signature(root, rid, PRINCIPAL, decision)
        if tracked:
            run_state.file_tracked(root, run_state.read(root))
    return rid


def _project(root: Path, *runs: tuple[str, dict], rulings: tuple = ()) -> list[str]:
    """A committed project: the lean run's work, then one signed report per run in `runs`, and
    the decisions `rulings` names as `(text, supersedes)`, added through the log's own writer."""
    lean.lean_run(root)
    _git(root, "init", "-q", ".")
    _commit(root, "the delivered batch")
    rids = [_file_run(root, run, **opts) for run, opts in runs]
    for text, supersedes in rulings:
        decisions.add(root, text, "a fixture ruling", supersedes=supersedes)
    _commit(root, "sign the reports")
    return rids


ACCEPTED = (("the operator delegates the signature", ""),)
TWO_ACCEPTED = ACCEPTED + (("the operator delegates a second signature", ""),)
SUPERSEDED = ACCEPTED + (("a later ruling replaces it", "D0001"),)


def _cli(root: Path, *argv: str, script: Path = SPRINT_REPORT) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), "--root", str(root), *argv],
                          cwd=str(root), capture_output=True, text=True, timeout=120,
                          env=gitutil.git_env())


def _disclose(root: Path, rid: str, decision: str) -> subprocess.CompletedProcess:
    return _cli(root, "disclose", "--report", rid, "--decision", decision)


def _files(root: Path, rid: str) -> dict[str, Path]:
    d = root / "sdlc-studio" / "reports"
    return {"json": d / f"{rid}.json", "twin": sr._twin_path(root, sr.read_report(root, rid)),
            "index": d / "_index.md"}


def _bytes(root: Path, rid: str) -> dict[str, bytes]:
    return {k: p.read_bytes() for k, p in _files(root, rid).items()}


def _cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


class DelegationDisclosureTests(unittest.TestCase):
    def _root(self) -> Path:
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        return Path(d.name)

    def _check(self, root: Path, rid: str) -> subprocess.CompletedProcess:
        return _cli(root, "check", "--report", rid)

    def _assert_valid(self, root: Path, rid: str) -> None:
        proc = self._check(root, rid)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn(f"VALID: {rid}", proc.stdout)

    def _assert_refused(self, proc: subprocess.CompletedProcess, *named: str) -> None:
        self.assertEqual(2, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("error:", proc.stderr)
        self.assertNotIn("error:", proc.stdout)
        for word in named:
            self.assertIn(word, proc.stderr)

    # --- AC1 ---------------------------------------------------------------------------------

    def test_a_disclosure_leaves_the_signed_report_valid(self) -> None:
        root = self._root()
        [rid] = _project(root, (RUN_A, {}), rulings=ACCEPTED)
        record = run_state.tracked_path(root, RUN_A)
        held = record.read_bytes()
        before = sr.read_report(root, rid)
        self._assert_valid(root, rid)
        proc = _disclose(root, rid, "D0001")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        after = sr.read_report(root, rid)
        sig = after["signature"]
        self.assertIs(True, sig.get("delegated"))
        self.assertEqual("D0001", sig.get("decision"))
        self.assertEqual(before["signature"],
                         {k: v for k, v in sig.items() if k not in ("delegated", "decision")})
        self.assertEqual(before["fingerprint"], after["fingerprint"])
        self.assertEqual({k: v for k, v in before.items() if k != "signature"},
                         {k: v for k, v in after.items() if k != "signature"})
        self.assertEqual(held, record.read_bytes(), "the tracked run record was rewritten")
        twin = _files(root, rid)["twin"].read_text(encoding="utf-8")
        self.assertIn(f"| {delegated('D0001')} | ", twin)
        self._assert_valid(root, rid)
        _commit(root, "disclose the delegation")
        self._assert_valid(root, rid)

    # --- AC2 ---------------------------------------------------------------------------------

    def test_a_disclosure_is_refused_for_an_unsigned_report_or_an_unaccepted_decision(
            self) -> None:
        def no_decision(root: Path, rid: str) -> None:
            rep = sr.read_report(root, rid)
            rep["signature"]["delegated"] = True
            sr.write_report(root, rep)
        for label, opts, rulings, edit, named, says in (
                ("unsigned", {"sign": False}, ACCEPTED, None, "D0001", "not signed"),
                ("decision absent", {}, ACCEPTED, None, "D0002", "holds no such decision"),
                ("decision superseded", {}, SUPERSEDED, None, "D0001", "superseded"),
                ("already delegated", {"decision": "D0002"}, TWO_ACCEPTED, None, "D0001",
                 "D0002"),
                ("delegated with no decision", {}, ACCEPTED, no_decision, "D0001",
                 "no recorded decision")):
            with self.subTest(label):
                root = self._root()
                [rid] = _project(root, (RUN_A, opts), rulings=rulings)
                if edit:
                    edit(root, rid)
                before = _bytes(root, rid)
                self._assert_refused(_disclose(root, rid, named), rid, says)
                self.assertEqual(before, _bytes(root, rid), "a refusal wrote to the report")

    # --- AC3 ---------------------------------------------------------------------------------

    def test_repeating_a_disclosure_writes_it_once(self) -> None:
        root = self._root()
        [rid] = _project(root, (RUN_A, {}), rulings=ACCEPTED)
        self.assertEqual(0, _disclose(root, rid, "D0001").returncode)
        files = _files(root, rid)
        before = _bytes(root, rid)
        stats = {k: (files[k].stat().st_ino, files[k].stat().st_mtime_ns) for k in files}
        proc = _disclose(root, rid, "D0001")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("nothing changed", proc.stdout)
        self.assertEqual(before, _bytes(root, rid))
        self.assertEqual(stats, {k: (files[k].stat().st_ino, files[k].stat().st_mtime_ns)
                                 for k in files}, "a re-run rewrote the page")
        twin = files["twin"].read_text(encoding="utf-8")
        self.assertEqual(1, twin.count("entered under delegation"))
        self._assert_valid(root, rid)

    # --- AC4 ---------------------------------------------------------------------------------

    def _pack(self, root: Path) -> subprocess.CompletedProcess:
        return _cli(root, "evidence-pack", "--version", "1.0.0", "--reports", "RPT0001,RPT0002",
                    script=RELEASE_CUT)

    @staticmethod
    def _accountable(pack: str) -> dict[str, list[str]]:
        """`{report: [each of its changes' Accountable lines]}`."""
        out: dict[str, list[str]] = {}
        for entry in pack.split("\n### ")[1:]:
            lines = entry.splitlines()
            rid = next(ln for ln in lines if ln.startswith("- Report: "))[10:].rstrip(".")
            out.setdefault(rid, []).append(
                next(ln for ln in lines if ln.startswith("- Accountable: ")))
        return out

    def _refused_pack(self, root: Path, *named: str) -> None:
        proc = self._pack(root)
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        for word in ("RPT0001", *named):
            self.assertIn(word, proc.stderr)
        self.assertFalse((root / PACK_REL).exists(), "a refusal wrote a pack")

    def test_the_evidence_pack_states_a_disclosed_delegation(self) -> None:
        base = self._root() / "base"
        base.mkdir()
        _project(base, (RUN_A, {}), (RUN_B, {}), rulings=ACCEPTED)

        def copy(name: str) -> Path:
            dest = base.parent / name
            shutil.copytree(base, dest, symlinks=True)
            return dest

        root = copy("disclosed")
        self.assertEqual(0, _disclose(root, "RPT0001", "D0001").returncode)
        _commit(root, "disclose RPT0001")
        proc = self._pack(root)
        self.assertEqual(0, proc.returncode, proc.stderr)
        lines = self._accountable((root / PACK_REL).read_text(encoding="utf-8"))
        sig = {rid: sr.read_report(root, rid)["signature"] for rid in ("RPT0001", "RPT0002")}
        on = {rid: f"on {s['signed_at'][:10]} over fingerprint {s['fingerprint']}."
              for rid, s in sig.items()}
        self.assertTrue(lines.get("RPT0001") and lines.get("RPT0002"), lines)
        self.assertEqual({f"- Accountable: {PRINCIPAL}, whose signature on its report was entered "
                          f"under delegation, authorised by decision D0001, {on['RPT0001']}"},
                         set(lines["RPT0001"]))
        self.assertEqual({f"- Accountable: {PRINCIPAL}, who signed its report {on['RPT0002']}"},
                         set(lines["RPT0002"]))

        # The decision is read from the log committed at the revision built: superseded there,
        # or absent there while the working copy accepts it, refuses.
        root = copy("superseded")
        self.assertEqual(0, _disclose(root, "RPT0001", "D0001").returncode)
        decisions.add(root, "a later ruling replaces it", "a fixture ruling", supersedes="D0001")
        _commit(root, "disclose, then supersede the decision")
        self._refused_pack(root, "D0001", "superseded", "committed at the revision built")
        root = self._root() / "uncommitted"
        root.mkdir()
        _project(root, (RUN_A, {}), (RUN_B, {}))
        decisions.add(root, "the operator delegates the signature", "a fixture ruling")
        self.assertEqual(0, _disclose(root, "RPT0001", "D0001").returncode)
        _commit(root, "disclose without committing the log", "sdlc-studio/reports")
        self._refused_pack(root, "D0001", "holds no such decision")

        # A report-only decision is read as the report spells it, never normalised past it.
        for spelling in ("d0001", "1"):
            with self.subTest(spelling=spelling):
                root = copy(f"spelt-{spelling}")
                rep = sr.read_report(root, "RPT0001")
                rep["signature"].update(delegated=True, decision=spelling)
                sr.write_report(root, rep)
                _commit(root, "a hand-spelt decision")
                self._refused_pack(root, repr(spelling), "D0001")

        # A delegation the run record holds is still the run record's (US1292's refusals).
        sealed = self._root() / "sealed"
        sealed.mkdir()
        _project(sealed, (RUN_A, {"decision": "D0002"}), (RUN_B, {}), rulings=TWO_ACCEPTED)
        for label, change in (("dropped", lambda s: [s.pop(k) for k in ("delegated", "decision")]),
                              ("changed", lambda s: s.update(decision="D0001"))):
            with self.subTest(label):
                root = base.parent / f"sealed-{label}"
                shutil.copytree(sealed, root, symlinks=True)
                rep = sr.read_report(root, "RPT0001")
                change(rep["signature"])
                sr.write_report(root, rep)
                _commit(root, f"the report's delegation {label}")
                self._refused_pack(root, "disagree on delegation")

    # --- AC5 ---------------------------------------------------------------------------------

    def test_the_evidence_page_names_each_delegated_signature(self) -> None:
        root = self._root()
        rids = _project(root, (RUN_A, {"decision": "D0001"}), (RUN_B, {}), (RUN_C, {}),
                        rulings=TWO_ACCEPTED)
        self.assertEqual(["RPT0001", "RPT0002", "RPT0003"], rids)
        self.assertEqual(0, _disclose(root, "RPT0002", "D0002").returncode)
        page = root / "docs" / "evidence.md"
        page.parent.mkdir()
        page.write_text(f"# Evidence\n\n{BEGIN}\nstale\n{END}\n", encoding="utf-8")
        proc = _cli(root, "evidence", "--out", "docs/evidence.md")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        text = page.read_text(encoding="utf-8")
        region = text[text.index(BEGIN):text.index(END)]
        table = [ln for ln in region.splitlines() if ln.startswith("|")]
        head = _cells(table[0])
        self.assertEqual([c for c, _ in sr.EVIDENCE_COLUMNS], head)
        self.assertEqual(["Run", "Report", "Goal verdict", "Verdict note", "Dollars per point",
                          "Model", "Hours to signature", "Signed by"], head)
        rows = {r["Report"]: r for r in (dict(zip(head, _cells(ln))) for ln in table[2:])}
        self.assertEqual({"RPT0001": delegated("D0001"), "RPT0002": delegated("D0002"),
                          "RPT0003": PRINCIPAL}, {k: r["Signed by"] for k, r in rows.items()})
        legend = re.search(r"(?m)^- Signed by: (.*)$", region)
        self.assertIsNotNone(legend, region)
        for field in ("`signature.principal`", "`signature.delegated`", "`signature.decision`"):
            self.assertIn(field, legend.group(1))

        # This repository's page is regenerated with the column, and still checks.
        check = _cli(REPO, "evidence", "--out", "docs/evidence.md", "--check")
        self.assertEqual(0, check.returncode, check.stdout + check.stderr)
        committed = (REPO / "docs" / "evidence.md").read_text(encoding="utf-8")
        sig = json.loads((REPO / "sdlc-studio" / "reports" / "RPT0045.json")
                         .read_text(encoding="utf-8"))["signature"]
        row = next(ln for ln in committed.splitlines() if ln.startswith("| ") and
                   "| RPT0045 |" in ln)
        self.assertEqual(sr.signed_by(sig), _cells(row)[-1])
        self.assertIn("entered under delegation, authorised by decision D0545", _cells(row)[-1])

    # --- the guards beside the criteria -----------------------------------------------------

    def test_a_disclosure_keeps_the_report_index_row_where_it_stands(self) -> None:
        root = self._root()
        _project(root, (RUN_A, {}), (RUN_B, {}), rulings=ACCEPTED)
        index = _files(root, "RPT0001")["index"]
        before = index.read_bytes()
        self.assertEqual(0, _disclose(root, "RPT0001", "D0001").returncode)
        self.assertEqual(before, index.read_bytes(), "the disclosed report's row moved")

    def test_a_decision_in_another_spelling_is_normalised_and_a_non_id_refused(self) -> None:
        for spelling in ("d0001", "1"):
            with self.subTest(spelling=spelling):
                root = self._root()
                [rid] = _project(root, (RUN_A, {}), rulings=ACCEPTED)
                proc = _disclose(root, rid, spelling)
                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                self.assertEqual("D0001", sr.read_report(root, rid)["signature"]["decision"])
        root = self._root()
        [rid] = _project(root, (RUN_A, {}), rulings=ACCEPTED)
        before = _bytes(root, rid)
        self._assert_refused(_disclose(root, rid, "D00121"), "holds no such decision")
        self._assert_refused(_disclose(root, "RPT0099", "D0001"), "no report of record")
        self.assertEqual(before, _bytes(root, rid))

    def test_a_disclosure_changes_no_verdict_check_gives(self) -> None:
        """No tracked run record, a page of an older schema, and a page already INVALID: each is
        disclosed, and `check` says after what it said before."""
        def older_schema(root: Path, rid: str) -> None:
            path = _files(root, rid)["json"]
            path.write_text(path.read_text(encoding="utf-8").replace('"schema": 2,',
                                                                     '"schema": 1,', 1),
                            encoding="utf-8")

        def edited(root: Path, rid: str) -> None:
            rep = sr.read_report(root, rid)
            figures = next(s["figures"] for s in rep["sections"] if s.get("figures"))
            first = next(iter(figures.values()))
            first["value"] = f"{first['value']} edited"
            sr.write_report(root, rep)
        for label, opts, edit, verdict in (
                ("no tracked run record", {"tracked": False}, None, "VALID: RPT0001"),
                ("an older schema", {}, older_schema, "report schema 1"),
                ("already invalid", {}, edited, "INVALID")):
            with self.subTest(label):
                root = self._root()
                [rid] = _project(root, (RUN_A, opts), rulings=ACCEPTED)
                if edit:
                    edit(root, rid)
                    _commit(root, "the page as it stood")
                before = self._check(root, rid)
                self.assertIn(verdict, before.stdout + before.stderr)
                proc = _disclose(root, rid, "D0001")
                self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
                self.assertEqual("D0001", sr.read_report(root, rid)["signature"]["decision"])
                after = self._check(root, rid)
                self.assertEqual((before.returncode, before.stdout, before.stderr),
                                 (after.returncode, after.stdout, after.stderr))

    def test_the_verb_is_in_every_registry_a_new_verb_implies(self) -> None:
        import argparse  # noqa: PLC0415
        sub = next(a for a in sr.build_parser()._actions
                   if isinstance(a, argparse._SubParsersAction))
        self.assertIn("disclose", sub.choices)
        flags = {o for a in sub.choices["disclose"]._actions for o in a.option_strings}
        self.assertLessEqual({"--report", "--decision"}, flags)
        self.assertIn("disclose", sr.NON_CEREMONY_VERBS.get("sprint_report", ()))
        drift = sr.cycle_drift()
        self.assertEqual([], drift["stale"])
        self.assertNotIn("disclose", json.dumps(drift.get("uncovered")))
        surface = subprocess.run(
            [sys.executable, str(SCRIPTS / "docgen.py"), "--root", str(REPO), "surface",
             "--check"], capture_output=True, text=True, timeout=120, check=False)
        self.assertIn("docgen surface: 0 drift item(s)", surface.stdout, surface.stderr)
        self.assertIn("| `sprint_report.py disclose` |",
                      (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8"))
        judged = command_audit.dead_flags(SPRINT_REPORT.read_text(encoding="utf-8"))
        for dest in ("report", "decision"):
            self.assertIn(dest, judged["dests"])
            self.assertNotIn(dest, [d["dest"] for d in judged["dead"]], "judged dead")
            self.assertNotIn(dest, [u["dest"] for u in judged["unjudged"]], "left unjudged")
        domain = (SKILL / "reference-scripts-domain.md").read_text(encoding="utf-8")
        section = domain.split("### `sprint_report.py`", 1)[1].split("\n### ", 1)[0]
        self.assertIn("disclose --report", section)
        self.assertIn("sprint_report.py disclose --report",
                      (SKILL / "help" / "sprint.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
