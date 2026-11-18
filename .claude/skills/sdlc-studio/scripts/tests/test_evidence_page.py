"""`sprint_report.py evidence`: the signed reports of record as one evidence table.

A change board reads the table, so each cell is read from the named report rather than worked
out again, the page's hand-written text is never touched, and `--check` tells a hand-edited
cell (a failure) apart from a report signed after the page was built (a note, never a failure,
so a sprint close cannot turn the tree red).
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
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import command_audit  # noqa: E402
import sprint_report as sr  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parents[1]
_SKILL = _SCRIPTS.parent
BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
HAND_HEAD = "# Evidence\n\nHand text  with  two spaces, a tab\there and a trailing space \n\n"
HAND_TAIL = "\n## After the table\n\nMore hand text, kept byte for byte.\n"


def _figure(key: str, value) -> dict:
    return {"key": key, "value": value, "source": "sdlc-studio/reports/runs/x.json"}


def _report(rid: str, run: str, generated: str, signed: str | None, verdict: str, note: str,
            dollars: str | None) -> dict:
    rows = [{"est_measure": _figure("est_measure", "Points"), "est_actual": _figure("est_actual", 9)}]
    if dollars is not None:
        rows.append({"est_measure": _figure("est_measure", "Dollars per point"),
                     "est_actual": _figure("est_actual", dollars)})
    signature = {"principal": "An Operator", "signed_at": signed, "report": rid} if signed else {}
    return {"schema": 2, "report_id": rid, "run_id": run, "generated_at": generated,
            "signature": signature,
            "sections": [
                {"key": "goal", "title": "Goal", "rows": [], "not_measured": None,
                 "figures": {"goal_verdict": _figure("goal_verdict", verdict),
                             "goal_verdict_note": _figure("goal_verdict_note", note)}},
                {"key": "estimates", "title": "Estimates", "figures": {}, "rows": rows,
                 "not_measured": None},
                # The signoff section is built before the sign, so it never holds the signature.
                {"key": "signoff", "title": "Sign-off", "rows": [], "not_measured": None,
                 "figures": {"signed_at": _figure("signed_at", "not yet signed")}}]}


def _models(rep: dict, priced: tuple[str, ...] = (), tokens: tuple[str, ...] = (),
            figure: str | None = None) -> dict:
    """`rep` with a `cost` section of tokens-by-model rows named `tokens` and, when `priced`
    names any, a `cost_prices` section with one row per priced model, as a report files them.
    `figure` is the `model` figure the older Cost section carried instead of those rows, as
    RPT0002, RPT0003 and RPT0005 hold it."""
    figures = {"model": _figure("model", figure)} if figure is not None else {}
    rep["sections"].append({"key": "cost", "title": "Tokens by model", "figures": figures,
                            "not_measured": None,
                            "rows": [{"model_name": _figure("model_name", m),
                                      "model_tokens": _figure("model_tokens", 1000)}
                                     for m in tokens]})
    if priced:
        rep["sections"].append({"key": "cost_prices", "title": "Prices", "figures": {},
                                "not_measured": None,
                                "rows": [{"price_model": _figure("price_model", m),
                                          "price_usd": _figure("price_usd", "$1.00")}
                                         for m in priced]})
    return rep


FIXTURE = (
    _report("RPT0101", "RUN-AAA", "2026-01-01T00:00:00Z", "2026-01-01T02:30:00Z",
            "Judged achieved", "everything planned shipped", "$2.50"),
    _report("RPT0102", "RUN-BBB", "2026-01-02T00:00:00Z", "2026-01-05T18:00:00Z",
            "Judged partial", "the gate held | one criterion short", None),
    _report("RPT0103", "RUN-CCC", "2026-01-06T00:00:00Z", "2026-01-06T01:00:00Z",
            "Judged achieved", "first signature", "$3.00"),
    _report("RPT0104", "RUN-CCC", "2026-01-06T05:00:00Z", "2026-01-06T06:00:00Z",
            "Judged partial", "re-judged on a second look", "$3.10"),
    _report("RPT0105", "RUN-DDD", "2026-01-07T00:00:00Z", None,
            "Judged achieved", "never signed", "$9.99"),
)


def _cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def _table(region: str) -> list[dict]:
    lines = [ln for ln in region.splitlines() if ln.startswith("|")]
    head = _cells(lines[0])
    return [dict(zip(head, _cells(ln))) for ln in lines[2:]]


def _hours(report: dict) -> str:
    def ts(s: str) -> datetime:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
    gap = ts(report["signature"]["signed_at"]) - ts(report["generated_at"])
    return f"{gap.total_seconds() / 3600:.1f}"


class EvidencePageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="evidence_page_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.reports = self.root / "sdlc-studio" / "reports"
        self.reports.mkdir(parents=True)
        for rep in FIXTURE:
            self._file(rep)
        self.page = self.root / "docs" / "evidence.md"
        self.page.parent.mkdir()
        self.page.write_bytes(f"{HAND_HEAD}{BEGIN}\nstale\n{END}{HAND_TAIL}".encode("utf-8"))

    def _file(self, rep: dict) -> None:
        (self.reports / f"{rep['report_id']}.json").write_text(json.dumps(rep), encoding="utf-8")

    def _run(self, *extra: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = sr.main(["--root", str(self.root), "evidence", "--out", "docs/evidence.md",
                            *extra])
        return code, out.getvalue()

    def _region(self) -> str:
        text = self.page.read_text(encoding="utf-8")
        return text[text.index(BEGIN) + len(BEGIN):text.index(END)]

    def test_one_row_per_signed_run_from_its_latest_report(self) -> None:
        code, out = self._run()
        self.assertEqual(0, code, out)
        rows = {r["Run"]: r for r in _table(self._region())}
        self.assertEqual(3, len(_table(self._region())), "one row per signed run, none twice")
        self.assertEqual({"RUN-AAA", "RUN-BBB", "RUN-CCC"}, set(rows), "the unsigned run is out")
        self.assertEqual("RPT0104", rows["RUN-CCC"]["Report"], "the run's latest signed report")
        self.assertEqual(["Judged achieved", "-", "$2.50", "2.5"],
                         [rows["RUN-AAA"][k] for k in ("Goal verdict", "Verdict note",
                                                       "Dollars per point", "Hours to signature")])
        self.assertEqual(["Judged partial", r"the gate held \| one criterion short",
                          "not recorded", "90.0"],
                         [rows["RUN-BBB"][k] for k in ("Goal verdict", "Verdict note",
                                                       "Dollars per point", "Hours to signature")])
        self.assertEqual(["Judged partial", "re-judged on a second look", "$3.10", "1.0"],
                         [rows["RUN-CCC"][k] for k in ("Goal verdict", "Verdict note",
                                                       "Dollars per point", "Hours to signature")])
        self.assertNotIn("RPT0105", self._region())
        self.assertNotIn("$9.99", self._region())
        # The latest signature wins, not the highest report id.
        self._file(_report("RPT0100", "RUN-CCC", "2026-01-06T06:30:00Z", "2026-01-06T07:00:00Z",
                           "Judged achieved", "signed last under a lower id", "$3.20"))
        self.assertEqual(0, self._run()[0])
        rows = {r["Run"]: r for r in _table(self._region())}
        self.assertEqual("RPT0100", rows["RUN-CCC"]["Report"], "latest signature, not highest id")

    def test_a_goal_not_measured_reads_its_not_measured_figure(self) -> None:
        rep = _report("RPT0106", "RUN-EEE", "2026-02-01T00:00:00Z", "2026-02-01T01:00:00Z",
                      "unused", "", None)
        rep["sections"][0].update(figures={}, not_measured={
            **_figure("goal", "NOT MEASURED"), "reason": "the run set no goal"})
        self._file(rep)
        self.assertEqual(0, self._run()[0])
        rows = {r["Run"]: r for r in _table(self._region())}
        self.assertEqual("NOT MEASURED", rows["RUN-EEE"]["Goal verdict"])

    def test_no_cell_is_empty_and_a_missing_note_reads_not_recorded(self) -> None:
        """An empty cell fails markdownlint's compact table style, and a reader cannot tell a
        note left out by rule from one the report never held. An achieved verdict's note reads
        `-`; a partial verdict with no note reads not recorded."""
        self._file(_report("RPT0106", "RUN-EEE", "2026-02-01T00:00:00Z", "2026-02-01T01:00:00Z",
                           "Judged partial", "", "$2.00"))
        self.assertEqual(0, self._run()[0])
        region = self._region()
        rows = {r["Run"]: r for r in _table(region)}
        self.assertEqual("-", rows["RUN-AAA"]["Verdict note"])
        self.assertEqual("not recorded", rows["RUN-EEE"]["Verdict note"])
        for line in (ln for ln in region.splitlines() if ln.startswith("|")):
            self.assertNotIn("|  |", line)
            self.assertNotIn("", _cells(line), line)
        self.assertRegex(region, r"(?m)^- Verdict note: .*`-`")

    def test_each_row_names_the_model_its_report_priced(self) -> None:
        """The Model cell reads the models the row's own report priced: each `price_model` of
        its `cost_prices` rows, or, where it priced none, each `model_name` of its tokens-by-model
        rows that names a model, or, where it has neither, the `model` figure of its Cost section
        that names one. A report recording none reads not recorded, never a blank, never mixed,
        and never a model from the catalogue of prices it carries or from another report."""
        catalogue = {"models": {m: {"input": 1.0} for m in
                                ("claude-fable-5", "gpt-6-luna", "claude-opus-5-5",
                                 "claude-sonnet-5-5", "claude-haiku-5-5")}}
        # Priced out of alphabetical order, so the cell keeps the order the report holds them.
        priced = _models(_report("RPT0106", "RUN-EEE", "2026-02-01T00:00:00Z",
                                 "2026-02-01T01:00:00Z", "Judged achieved", "", "$2.00"),
                         priced=("claude-sonnet-5-5", "claude-opus-5-5"), tokens=("mixed",))
        priced["price_table"] = catalogue
        # A token row beside the older figure: the token row is the record, the figure the last
        # fallback.
        tokens_only = _models(_report("RPT0107", "RUN-FFF", "2026-02-02T00:00:00Z",
                                      "2026-02-02T01:00:00Z", "Judged achieved", "", None),
                              tokens=("claude-haiku-5-5",), figure="claude-opus-5")
        mixed_only = _models(_report("RPT0108", "RUN-GGG", "2026-02-03T00:00:00Z",
                                     "2026-02-03T01:00:00Z", "Judged achieved", "", None),
                             tokens=("mixed",), figure="mixed")
        mixed_only["price_table"] = catalogue
        # The older figure read UNMEASURED where the stamps recorded no model.
        unrecorded = _models(_report("RPT0109", "RUN-HHH", "2026-02-04T00:00:00Z",
                                     "2026-02-04T01:00:00Z", "Judged achieved", "", None),
                             tokens=("unrecorded",), figure="UNMEASURED")
        # Tokens counted for a model the report did not price: the priced one is the record.
        partly = _models(_report("RPT0110", "RUN-III", "2026-02-05T00:00:00Z",
                                 "2026-02-05T01:00:00Z", "Judged achieved", "", "$1.50"),
                         priced=("claude-opus-5-5",),
                         tokens=("claude-haiku-5-5", "claude-opus-5-5"))
        # The shape of RPT0002, RPT0003 and RPT0005: a Cost section with no rows, whose `model`
        # figure is the only record of the model.
        figure_only = _models(_report("RPT0111", "RUN-JJJ", "2026-02-06T00:00:00Z",
                                      "2026-02-06T01:00:00Z", "Judged achieved", "", None),
                              figure="claude-opus-5")
        for rep in (priced, tokens_only, mixed_only, unrecorded, partly, figure_only):
            self._file(rep)
        code, out = self._run()
        self.assertEqual(0, code, out)
        region = self._region()
        # Every cell exactly, so a model from another row's report, the catalogue, a token row
        # beside a priced one, the figure beside a token row, mixed, unrecorded, UNMEASURED, a
        # reordered list or a blank each fails here.
        self.assertEqual({"RUN-EEE": "claude-sonnet-5-5, claude-opus-5-5",
                          "RUN-FFF": "claude-haiku-5-5", "RUN-III": "claude-opus-5-5",
                          "RUN-JJJ": "claude-opus-5",
                          "RUN-GGG": "not recorded", "RUN-HHH": "not recorded",
                          "RUN-AAA": "not recorded", "RUN-BBB": "not recorded",
                          "RUN-CCC": "not recorded"},
                         {r["Run"]: r.get("Model") for r in _table(region)})
        self.assertRegex(region, r"(?m)^- Model: .*`price_model`.*`cost_prices`.*`model_name`"
                                 r".*`model` figure")
        self.assertEqual(0, self._run("--check")[0], "the page the verb wrote checks clean")

    def test_hand_text_is_kept_and_every_figure_is_a_report_field(self) -> None:
        self.assertEqual(0, self._run()[0])
        raw = self.page.read_bytes()
        self.assertTrue(raw.startswith(f"{HAND_HEAD}{BEGIN}".encode("utf-8")))
        self.assertTrue(raw.endswith(f"{END}{HAND_TAIL}".encode("utf-8")))
        region = self._region()
        by_id = {r["report_id"]: r for r in FIXTURE}
        rows = _table(region)
        # Every column names the report field it reads, inside the markers.
        for column in rows[0]:
            self.assertRegex(region, rf"(?m)^- {re.escape(column)}: .*`[a-z_.]+`",
                             f"the column {column!r} names no report field")
        for row in rows:
            rep = by_id[row["Report"]]
            goal = next(s for s in rep["sections"] if s["key"] == "goal")["figures"]
            est = next(s for s in rep["sections"] if s["key"] == "estimates")["rows"]
            verdict = goal["goal_verdict"]["value"]
            dollars = [r["est_actual"]["value"] for r in est
                       if r["est_measure"]["value"] == "Dollars per point"]
            self.assertEqual(rep["run_id"], row["Run"])
            self.assertEqual(verdict, row["Goal verdict"])
            self.assertEqual("-" if verdict == "Judged achieved"
                             else goal["goal_verdict_note"]["value"].replace("|", r"\|"),
                             row["Verdict note"])
            self.assertEqual(dollars[0] if dollars else "not recorded", row["Dollars per point"])
            self.assertEqual(_hours(rep), row["Hours to signature"])
        # Outside the table, the only figures are the newest report's id and signing time.
        newest = by_id["RPT0104"]
        prose = "\n".join(ln for ln in region.splitlines() if not ln.startswith("|"))
        self.assertIn("RPT0104", prose)
        self.assertIn(newest["signature"]["signed_at"], prose)
        bare = prose.replace("RPT0104", "").replace(newest["signature"]["signed_at"], "")
        self.assertNotRegex(bare, r"\d", "a figure with no report field behind it")
        # A second run changes nothing.
        before = self.page.read_bytes()
        self.assertEqual(0, self._run()[0])
        self.assertEqual(before, self.page.read_bytes())

    def test_check_names_a_drifted_run_and_only_notes_a_newer_report(self) -> None:
        self.assertEqual(0, self._run()[0])
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertNotIn("not yet on the page", out, "a fresh page prints no note")
        self.assertNotIn("differs", out)
        fresh = self.page.read_text(encoding="utf-8")
        # A hand-edited cell is drift, named by its run: RUN-BBB's Dollars per point, the one
        # not recorded beside a Model cell that is not recorded too.
        self.assertEqual(1, fresh.count("| not recorded | not recorded |"), fresh)
        self.page.write_text(fresh.replace("| not recorded | not recorded |",
                                           "| $1.00 | not recorded |"), encoding="utf-8")
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn("RUN-BBB", out)
        self.assertNotIn("RUN-AAA", out)
        self.assertNotIn("RUN-CCC", out)
        # A report signed after the newest the page names is noted, and is not drift.
        self.page.write_text(fresh, encoding="utf-8")
        self._file(_report("RPT0106", "RUN-EEE", "2026-02-01T00:00:00Z", "2026-02-01T01:00:00Z",
                           "Judged achieved", "later", "$2.00"))
        self._file(_report("RPT0107", "RUN-AAA", "2026-02-02T00:00:00Z", "2026-02-02T01:00:00Z",
                           "Judged partial", "re-signed after the page", "$2.60"))
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertRegex(out, r"RUN-EEE.*not yet on the page")
        self.assertRegex(out, r"RUN-AAA.*not yet on the page")
        self.assertEqual(fresh, self.page.read_text(encoding="utf-8"), "--check writes nothing")
        # The note never masks drift beside it, and the newer reports are not called drift.
        self.page.write_text(fresh.replace("| not recorded | not recorded |",
                                           "| $1.00 | not recorded |"), encoding="utf-8")
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        differs = [line for line in out.splitlines() if "differs" in line]
        self.assertEqual(1, len(differs), out)
        self.assertIn("RUN-BBB", differs[0])

    def test_a_page_naming_no_report_only_notes_the_first_signed_report(self) -> None:
        """A page built before any report was signed names none, so every signed report is
        newer than it: noted, never drift. Its empty-state line is still checked."""
        for rep in FIXTURE:
            if rep["signature"]:
                (self.reports / f"{rep['report_id']}.json").unlink()
        self.assertEqual(0, self._run()[0])
        self.assertIn("No report of record has been signed yet.", self._region())
        empty = self.page.read_text(encoding="utf-8")
        self._file(FIXTURE[0])
        code, out = self._run("--check")
        self.assertEqual(0, code, out)
        self.assertRegex(out, r"RUN-AAA \(RPT0101, signed .*\) is not yet on the page")
        self.assertNotIn("differs", out)
        self.assertEqual(empty, self.page.read_text(encoding="utf-8"), "--check writes nothing")
        # The empty-state line is generated text: an edit to it is drift.
        self.page.write_text(empty.replace("No report of record has been signed yet.",
                                           "No report has been signed."), encoding="utf-8")
        code, out = self._run("--check")
        self.assertEqual(1, code, out)
        self.assertIn("differs from the reports outside the table rows", out)
        self.assertRegex(out, r"RUN-AAA.*not yet on the page")

    def test_check_names_reordered_or_repeated_rows_as_row_drift(self) -> None:
        self.assertEqual(0, self._run()[0])
        fresh = self.page.read_text(encoding="utf-8")
        rows = [ln for ln in fresh.splitlines() if ln.startswith("| RUN-")]
        rows_msg, legend_msg = "in the order or number of its table rows", "outside the table rows"
        swapped = fresh.replace(f"{rows[0]}\n{rows[1]}", f"{rows[1]}\n{rows[0]}")
        for page, said, unsaid in (
                (swapped, rows_msg, legend_msg),
                (fresh.replace(rows[0], f"{rows[0]}\n{rows[0]}"), rows_msg, legend_msg),
                (fresh.replace("Each column reads", "Each column shows"), legend_msg, rows_msg)):
            self.page.write_text(page, encoding="utf-8")
            code, out = self._run("--check")
            self.assertEqual(1, code, out)
            self.assertIn(said, out)
            self.assertNotIn(unsaid, out)

    def test_the_verb_is_in_every_registry_a_new_verb_implies(self) -> None:
        import argparse  # noqa: PLC0415
        sub = next(a for a in sr.build_parser()._actions
                   if isinstance(a, argparse._SubParsersAction))
        self.assertIn("evidence", sub.choices)
        flags = {o for a in sub.choices["evidence"]._actions for o in a.option_strings}
        self.assertLessEqual({"--out", "--check"}, flags)
        self.assertIn("evidence", sr.NON_CEREMONY_VERBS.get("sprint_report", ()))
        self.assertEqual([], sr.cycle_drift()["stale"])
        surface = subprocess.run(
            [sys.executable, str(_SCRIPTS / "docgen.py"), "--root", str(_SKILL.parents[2]),
             "surface", "--check"], capture_output=True, text=True, timeout=120, check=False)
        self.assertIn("docgen surface: 0 drift item(s)", surface.stdout, surface.stderr)
        self.assertIn("| `sprint_report.py evidence` |",
                      (_SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8"))
        source = (_SCRIPTS / "sprint_report.py").read_text(encoding="utf-8")
        judged = command_audit.dead_flags(source)
        self.assertLessEqual({"out", "check"}, set(judged["dests"]))
        for dest in ("out", "check"):
            self.assertNotIn(dest, [d["dest"] for d in judged["dead"]], "judged dead")
            self.assertNotIn(dest, [u["dest"] for u in judged["unjudged"]], "left unjudged")
        domain = (_SKILL / "reference-scripts-domain.md").read_text(encoding="utf-8")
        section = domain.split("### `sprint_report.py`", 1)[1].split("\n### ", 1)[0]
        self.assertIn("evidence --out", section)


if __name__ == "__main__":
    unittest.main()
