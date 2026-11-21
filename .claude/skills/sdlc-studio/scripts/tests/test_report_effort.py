"""Each run's report of record states the effort its builders and reviewers were dispatched at.

`sprint plan --write` stamps `effort: {builder, reviewer}` on every unit's row of the plan it
writes, and the run record names that plan by its content digest (`plan_digest`). The report's
cost section reads the effort back from the plan the run record names, never from the project's
config at report time, and states one figure per role: each value with the count of units that
carried it. A run planned before the stamp existed, or whose record names no plan or another
plan, reads NOT MEASURED with its reason.

Every expected figure is typed here from the fixture's own plan rows; the digest is formed here
with hashlib, never by the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint_report.py
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_evidence_annex_report as annex  # noqa: E402 - the annex read as a consumer reads it
import test_lean_report as lean  # noqa: E402 - the sealed fixture run the report is built over

sr = lean.sr
from lib import lanes  # noqa: E402 - the lane records the effort figure reads
UNITS = ("US0001", "US0002", "US0004", "US0005")
PLAN_REL = "sdlc-studio/.local/sprint-plan.json"
KEYS = ("effort_builder", "effort_reviewer")


def _effort(builder: str, reviewer: str) -> dict:
    return {"builder": builder, "reviewer": reviewer}


class ReportEffortTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean.lean_run(self.root)

    # --- the fixture -------------------------------------------------------------------------

    def plan(self, efforts: dict, name_it: bool = True) -> None:
        """Write the plan the run was opened from, one batch row per unit carrying the effort
        in `efforts` (none where the unit maps to None), and, under `name_it`, name it on the
        run record by the digest of its bytes."""
        rows = [{"id": uid, "points": 3, **({"effort": e} if e is not None else {})}
                for uid, e in efforts.items()]
        path = self.root / PLAN_REL
        path.write_text(json.dumps({"batch": rows}, indent=2), encoding="utf-8")
        if name_it:
            self.name_plan("sha256:" + hashlib.sha256(path.read_bytes()).hexdigest())

    def name_plan(self, digest: str | None) -> None:
        rec = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(rec.read_text(encoding="utf-8"))
        if digest is None:
            state.pop("plan_digest", None)
        else:
            state["plan_digest"] = digest
        rec.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def configure(self, builder: str, reviewer: str) -> None:
        """The project's `routing.effort` AT REPORT TIME, set apart from the plan's stamp."""
        (self.root / "sdlc-studio" / ".config.yaml").write_text(
            f"routing:\n  effort:\n    builder: {builder}\n    reviewer: {reviewer}\n",
            encoding="utf-8")

    def cli(self, *argv: str) -> str:
        """The shipped `sprint_report.py` entry point; what it printed."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), *argv])
        self.assertEqual(0, rc, err.getvalue())
        return out.getvalue()

    def built(self) -> tuple[dict, str, str]:
        """`sprint_report.py build` as JSON, its Markdown twin, and the page rendered as HTML."""
        page = json.loads(self.cli("build", "--run", lean.RUN, "--format", "json"))
        return page, self.cli("build", "--run", lean.RUN), sr.render_html(page)

    @staticmethod
    def cost(page: dict) -> dict:
        return next(s for s in page["sections"] if s["key"] == "cost")["figures"]

    # --- the criteria ------------------------------------------------------------------------

    def test_the_report_states_each_roles_effort_from_the_run_record(self) -> None:
        """AC1. MUTANTS: the figure read from `routing.effort` at report time (reads high); the
        builder and reviewer values swapped; the figure citing the plan's `.local/`
        path rather than the run record alone; the Markdown twin or the HTML page leaving the effort out."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        self.configure("high", "high")
        page, md, html = self.built()
        figures = self.cost(page)
        self.assertEqual("low (4 units)", figures["effort_builder"]["value"])
        self.assertEqual("medium (4 units)", figures["effort_reviewer"]["value"])
        record = figures["tokens_delegated"]["source"]
        for key in KEYS:
            # Cited to the run record alone: the plan it names sits under `.local/`, which a
            # filed page never names.
            self.assertEqual(record, figures[key]["source"], key)
            self.assertNotIn(".local/", json.dumps(figures[key]), key)
        self.assertEqual(sr.EFFORT_STATED, page[sr.EFFORT_RULE])
        for rendered in (md, html):
            self.assertIn("builder low (4 units); reviewer medium (4 units)", rendered)
            self.assertNotIn("high (", rendered)

    def test_a_plan_the_run_record_does_not_name_is_not_read(self) -> None:
        """AC1, the record as the source. MUTANT: read whatever plan sits on disk without
        checking the digest the run record names it by - a later plan's high is reported."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        self.plan({uid: _effort("high", "high") for uid in UNITS}, name_it=False)
        page, md, _html = self.built()
        for key in KEYS:
            f = self.cost(page)[key]
            self.assertEqual(sr.NOT_MEASURED, f["value"], key)
            self.assertIn("is not the plan the run record names", f["reason"])
        self.assertNotIn("high (", md)

    def test_a_run_without_effort_reads_not_measured(self) -> None:
        """AC2. MUTANTS: an older run's missing stamp read as inherit (the shipped default); the
        figure left blank, `None` or `-`; a record that names no plan read as one that does."""
        cases = (("a plan planned before the stamp", "stamped no effort on its units",
                  lambda: self.plan({uid: None for uid in UNITS})),
                 ("a record naming no plan", "names no plan",
                  lambda: (self.plan({uid: _effort("low", "low") for uid in UNITS}),
                           self.name_plan(None))))
        for name, reason, arrange in cases:
            with self.subTest(case=name):
                arrange()
                page, md, html = self.built()
                for key in KEYS:
                    f = self.cost(page)[key]
                    self.assertEqual(sr.NOT_MEASURED, f["value"], key)
                    self.assertIn(reason, f["reason"], key)
                    self.assertNotIn("inherit", f["reason"])
                cell = f"{sr.NOT_MEASURED} - {self.cost(page)['effort_builder']['reason']}"
                for rendered in (md, html):
                    self.assertIn(f"builder {cell}; reviewer {cell}", rendered)
                    self.assertNotIn("inherit (", rendered)
                    self.assertNotIn("low (", rendered)

    def test_the_annex_documents_the_figure_and_mixed_effort_is_counted(self) -> None:
        """AC3. MUTANTS: a figure key or the rule mark missing from the annex's tables; a mixed
        run reported as one value (its first row's, or its most common); counts ordered by size
        rather than by effort; a single unit counted as `1 units`."""
        figures = {(annex._key(r["Section"]), annex._key(r["Figure"])): r["Meaning"]
                   for r in annex.annex_table("Report figure keys")}
        for key in KEYS:
            self.assertTrue(figures.get(("cost", key), "").strip(),
                            f"the annex's figure table does not document cost.{key}")
        mark = annex.keyed("Report envelope keys", "Key").get(sr.EFFORT_RULE)
        self.assertIsNotNone(mark, "the annex does not document the effort rule mark")
        self.assertEqual(("rule mark", f"`{sr.EFFORT_STATED}`"), (mark["Presence"], mark["Value"]))

        self.plan({"US0001": _effort("medium", "high"), "US0002": _effort("low", "medium"),
                   "US0004": _effort("medium", "medium"), "US0005": _effort("medium", "medium")})
        page, md, _html = self.built()
        self.assertEqual("low (1 unit), medium (3 units)",
                         self.cost(page)["effort_builder"]["value"])
        self.assertEqual("medium (3 units), high (1 unit)",
                         self.cost(page)["effort_reviewer"]["value"])
        self.assertIn("builder low (1 unit), medium (3 units); reviewer medium (3 units), "
                      "high (1 unit)", md)

    def test_the_effort_rule_round_trips_and_an_earlier_page_re_derives_as_filed(self) -> None:
        """MUTANTS: the mark dropped from the envelope; the rule hard-wired on in `revalidate`,
        so a page filed before it re-derives with effort figures it never carried; a signed
        page re-reading a plan that moved after the run instead of replaying its own figure."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        page = sr.build_report(self.root, lean.RETRO)
        self.assertTrue(sr.revalidate(self.root, sr.file_report(self.root, page))["valid"])
        before = sr.build_report(self.root, lean.RETRO, effort_rule=False)
        self.assertNotIn(sr.EFFORT_RULE, before)
        self.assertFalse(set(KEYS) & set(self.cost(before)), "a page filed before the rule")
        self.assertNotIn("**Effort.**", sr.render_markdown(before))
        check = sr.revalidate(self.root, sr.file_report(self.root, before))
        self.assertTrue(check["valid"], check["changes"])
        dropped = {k: v for k, v in page.items() if k not in (sr.EFFORT_RULE, "fingerprint")}
        check = sr.revalidate(self.root, sr.file_report(self.root, dropped))
        self.assertFalse(check["valid"], "the rule moves no figure on this fixture")
        # The page's own reading is replayed: a later plan on disk moves nothing on it.
        self.plan({uid: _effort("max", "max") for uid in UNITS})
        again = sr.build_report(self.root, lean.RETRO, filed=page)
        self.assertEqual("low (4 units)", self.cost(again)["effort_builder"]["value"])
        self.assertEqual(page["fingerprint"], again["fingerprint"])

    # --- BG1539: a headless lane's effort is reported as it ran -------------------------------

    def headless(self, unit: str, effort: str | None, harness: str = "claude",
                 run_id: str = lean.RUN) -> None:
        """A `sprint lane run` record of `unit` in the run, its command having carried
        `effort` (None: no effort flag), as `lanes._run` writes it."""
        path = self.root / "sdlc-studio" / ".local" / "lane-runs" / unit / f"s-{harness}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"unit": unit, "run_id": run_id, "harness": harness,
                                    "effort": effort, "effort_stamped": "low"}),
                        encoding="utf-8")

    def test_a_headless_unit_is_never_reported_dispatched_at_an_effort_not_passed(self) -> None:
        """BG1539 AC1. MUTANTS: the plan's stamp counted for every unit, as it was, so the two
        headless units read as dispatched at low; the not-applied units named with no reason; a
        lane record from another run, or one whose command carried the effort, counted as not
        applied."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        self.headless("US0001", None)
        self.headless("US0002", None, harness="codex")
        self.headless("US0004", None, run_id="RUN-01OTHERRUN")
        page, md, html = self.built()
        value = self.cost(page)["effort_builder"]["value"]
        self.assertTrue(value.startswith("low (2 units), "), value)
        self.assertIn("low configured and not applied (2 units)", value)
        self.assertIn("headless", value)
        self.assertIn("no effort flag", value)
        self.assertEqual("medium (4 units)", self.cost(page)["effort_reviewer"]["value"])
        for rendered in (md, html):
            self.assertIn(f"builder {value}; reviewer medium (4 units)", rendered)
            self.assertNotIn("builder low (4 units)", rendered)

    def test_a_run_built_wholly_headless_lists_each_stamp_lowest_first(self) -> None:
        """BG1539 AC1, every unit built headless, each under its own stamp. MUTANTS: the
        not-applied counts in the order of their names (high before low) or reversed; a stamp
        `sprint plan` never writes counted before the ones it does, or two such stamps in the
        order their rows came rather than by name; the harnesses left out; the in-session
        counts kept when no unit was built in session, opening the value with ", "; the
        harnesses named in the order their rows came rather than by name."""
        self.plan({"US0001": _effort("high", "medium"), "US0002": _effort("low", "medium"),
                   "US0004": _effort("max", "medium"), "US0005": _effort("medium", "medium"),
                   "US0006": _effort("xhigh", "medium"), "US0007": _effort("ultra", "medium"),
                   "US0003": _effort("turbo", "medium")})
        # the plan's first row ran under codex, so the harnesses read in row order would not be
        # in the order of their names
        self.headless("US0001", None, harness="codex")
        for uid in ("US0002", "US0003", "US0004", "US0005", "US0006", "US0007"):
            self.headless(uid, None)
        page, md, _html = self.built()
        value = self.cost(page)["effort_builder"]["value"]
        apart = ", ".join(f"{v} configured and not applied (1 unit)"
                          for v in ("low", "medium", "high", "xhigh", "max", "turbo", "ultra"))
        self.assertEqual(f"{apart}: built headless by `sprint lane run` (claude, codex), whose "
                         f"command carries no effort flag, so each ran at its harness's own "
                         f"default", value)
        self.assertIn(f"builder {value}; reviewer medium (7 units)", md)

    def test_a_headless_unit_asking_for_no_effort_is_counted_as_stamped(self) -> None:
        """BG1539 AC1's exemption: a headless unit stamped `inherit` asked its command to carry
        nothing, and one with no stamp asked for nothing, so each is counted as it was stamped,
        never as configured and not applied. MUTANTS: the `inherit` exemption dropped (reads
        "inherit configured and not applied"); a unit with no stamp counted apart (reads "None
        configured and not applied"), or its absent stamp read as a mapping."""
        self.plan({"US0001": _effort("inherit", "medium"), "US0002": None,
                   "US0004": _effort("low", "medium"), "US0005": _effort("low", "medium")})
        self.headless("US0001", None)
        self.headless("US0002", None, harness="codex")
        page, md, _html = self.built()
        value = self.cost(page)["effort_builder"]["value"]
        self.assertEqual("inherit (1 unit), low (2 units), not stamped (1 unit)", value)
        self.assertNotIn("not applied", md)

    def test_a_record_of_no_run_is_never_counted_as_not_applied(self) -> None:
        """MUTANT: `effort_not_applied`'s guard on a run with no id dropped, so a run record
        naming none counts every lane record that names none either, its own or not."""
        for run_id in (None, ""):
            self.headless(f"US000{1 if run_id is None else 2}", None, run_id=run_id)
        self.headless("US0004", None, harness="codex")
        for run_id in (None, ""):
            with self.subTest(run_id=run_id):
                self.assertEqual({}, lanes.effort_not_applied(self.root, run_id))
        self.assertEqual({"US0004": ["codex"]}, lanes.effort_not_applied(self.root, lean.RUN))

    def test_an_in_session_unit_still_reads_as_dispatched(self) -> None:
        """BG1539 AC3. MUTANTS: every unit read as not applied once any lane ran headless; a
        headless command that did carry the effort read as not applied."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        self.headless("US0001", "low")
        page, md, _html = self.built()
        self.assertEqual("low (4 units)", self.cost(page)["effort_builder"]["value"])
        self.assertIn("builder low (4 units); reviewer medium (4 units)", md)
        self.assertNotIn("not applied", md)

    def test_an_unsigned_page_checks_valid_where_its_plan_is_not_held(self) -> None:
        """MUTANT: `revalidate` re-reading the plan for an unsigned page instead of replaying the
        page's own effort - a clone that holds no `.local/` plan reads NOT MEASURED and the page
        it was handed reads INVALIDATED. The control: the plan's removal moves a fresh build."""
        self.plan({uid: _effort("low", "medium") for uid in UNITS})
        filed = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO))
        (self.root / PLAN_REL).unlink()
        fresh = sr.build_report(self.root, lean.RETRO)
        self.assertEqual(sr.NOT_MEASURED, self.cost(fresh)["effort_builder"]["value"])
        check = sr.revalidate(self.root, filed)
        self.assertTrue(check["valid"], check["changes"])


class ReportEffortDocsTests(unittest.TestCase):
    """BG1539 AC4: the three pages that account for `routing.effort` say what a headless lane
    does with it, and none presents the reported figure as the effort every agent ran at."""

    SKILL = Path(__file__).resolve().parents[2]
    PAGES = ("reference-evidence-schema.md", "reference-config.md", "reference-sprint.md")

    def test_the_three_pages_say_what_a_headless_lane_does_with_effort(self) -> None:
        """MUTANTS: a page left saying only that agents are dispatched or spawned at the
        stamped effort; a page naming headless lanes without saying the effort is not applied."""
        for name in self.PAGES:
            with self.subTest(page=name):
                text = (self.SKILL / name).read_text(encoding="utf-8")
                said = [para for para in re.split(r"\n\s*\n|\n\|", text)
                        if "headless" in para and "effort" in para]
                self.assertTrue(said, f"{name} says nothing of effort on a headless lane")
                self.assertTrue(any("not applied" in para or "no effort flag" in para
                                    for para in said),
                                f"{name} does not say a headless lane leaves the effort unapplied")
        schema = (self.SKILL / "reference-evidence-schema.md").read_text(encoding="utf-8")
        rows = [ln for ln in schema.splitlines() if ln.startswith("| `cost` | `effort_builder`")]
        self.assertEqual(1, len(rows))
        self.assertIn("not applied", rows[0])


if __name__ == "__main__":
    unittest.main()
