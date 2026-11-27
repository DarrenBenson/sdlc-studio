"""`escape.py failure-rate` derives change failure rate from release records and linked incidents.

The rate is the releases with at least one linked incident divided by the releases counted. A
release is read from `sdlc-studio/reports/releases.jsonl`, the record `release_cut.py
changelog-cut` writes. An incident is an issue whose `## Root Cause` section is written, linked to
a release through each escaped bug it was triaged into (the issue's `Decomposed-into`, or a bug
naming it as `Parent`) and that bug's `Shipped-in`. A release younger than the settling period at
the window's end is pending, in neither the counted nor the failed releases. With no release
record in the window, or no incident recorded anywhere, the figure reads not measured, never 0%.

Driven through `escape.main`, the shipped entry point, in throwaway project roots of plain files;
one case runs the script itself. No fixture needs git.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/escape.py
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

escape = loader.load_script("escape")
file_finding = loader.load_script("file_finding")

SKILL = loader.SCRIPTS_DIR.parent
RECORDS = Path("sdlc-studio") / "reports" / "releases.jsonl"
CAUSE = ("The review approved a checkout total never tested at the empty basket, so the "
         "boundary shipped unpinned.")
#: The four releases AC1 counts, each settled by 2026-03-31.
AC1_RELEASES = (("1.0.0", "2026-01-05"), ("1.1.0", "2026-02-02"), ("1.2.0", "2026-03-02"),
                ("1.3.0", "2026-03-16"))
WINDOW = ("--since", "2026-01-01", "--until", "2026-03-31")


def _record(version: str, date) -> str:
    return json.dumps({"version": version, "date": date, "previous": None, "reports": []})


def _project(d: str) -> Path:
    root = Path(d)
    for sub in ("issues", "bugs", "reports"):
        (root / "sdlc-studio" / sub).mkdir(parents=True)
    return root


def _records(root: Path, *releases: tuple[str, str], lines: list[str] | None = None) -> None:
    body = [_record(v, dt) for v, dt in releases] if lines is None else lines
    (root / RECORDS).write_text("\n".join(body) + "\n", encoding="utf-8")


def _issue(root: Path, iid: str = "IS0001", *, cause: str | None = CAUSE,
           decomposed: str | None = "BG0001", extra: str = "") -> None:
    text = f"# {iid}: the checkout fell over\n\n> **Status:** Triaged\n"
    if decomposed:
        text += f"> **Decomposed-into:** {decomposed}\n"
    text += extra + "\n## Summary\n\nThe checkout fell over in production.\n"
    if cause is not None:
        text += f"\n## Root Cause\n\n{cause}\n"
    (root / "sdlc-studio" / "issues" / f"{iid}-the-checkout-fell-over.md").write_text(
        text, encoding="utf-8")


def _bug(root: Path, bid: str, shipped: str | None = "v1.1.0", parent: str | None = "IS0001",
         escaped: str | None = "yes") -> None:
    text = f"# {bid}: the total is wrong\n\n> **Status:** Open\n"
    if parent:
        text += f"> **Parent:** {parent}\n"
    if escaped:
        text += f"> **Escaped:** {escaped}\n"
    if shipped:
        text += f"> **Shipped-in:** {shipped}\n"
    text += "\n## Summary\n\nThe total is wrong.\n"
    (root / "sdlc-studio" / "bugs" / f"{bid}-the-total-is-wrong.md").write_text(
        text, encoding="utf-8")


def _ac1(root: Path, *more: tuple[str, str]) -> None:
    """AC1's records and links, plus BG0002: escaped into 1.2.0 with no incident naming it."""
    _records(root, *AC1_RELEASES, *more)
    _issue(root, "IS0001", decomposed="BG0001")
    _bug(root, "BG0001", "v1.1.0", "IS0001")
    _bug(root, "BG0002", "v1.2.0", None)


def _cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = escape.main(argv)
        except SystemExit as exc:          # argparse refuses a flag with exit 2
            rc = exc.code
    return rc, out.getvalue(), err.getvalue()


def _rate(root: Path, *flags: str, window=WINDOW, fmt: str = "text") -> tuple[int, str, str]:
    return _cli(["failure-rate", "--root", str(root), *window, *flags, "--format", fmt])


def _json(root: Path, *flags: str, window=WINDOW) -> dict:
    rc, out, err = _rate(root, *flags, window=window, fmt="json")
    assert rc == 0, (rc, out, err)
    return json.loads(out)


def _line(out: str, label: str) -> str:
    """The text after `label: ` on its own line of the output."""
    hits = [ln[len(label) + 2:] for ln in out.splitlines() if ln.startswith(f"{label}: ")]
    assert len(hits) == 1, (label, out)
    return hits[0]


def _today():
    return datetime.now(timezone.utc).date()


class ChangeFailureRateTests(unittest.TestCase):

    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory(prefix="cfr_")
        self.addCleanup(self._dir.cleanup)
        self.root = _project(self._dir.name)

    # ---- the criteria ------------------------------------------------------------------

    def test_the_rate_names_the_releases_counted_the_incident_and_the_window(self) -> None:
        _ac1(self.root)
        rc, out, err = _rate(self.root)
        self.assertEqual((0, ""), (rc, err))
        self.assertEqual("change failure rate 25% (1 of 4 releases)", out.splitlines()[0])
        self.assertEqual("2026-01-01 to 2026-03-31 (both days included), 14-day settling period",
                         _line(out, "window"))
        self.assertEqual("1.0.0, 1.1.0, 1.2.0, 1.3.0", _line(out, "counted"))
        self.assertEqual("1.1.0 (incident IS0001; bug BG0001)", _line(out, "failed"))
        self.assertEqual("none", _line(out, "pending"))
        self.assertNotIn("BG0002", out, "an escaped bug no incident names moved the figure")
        self.assertEqual({"rate_percent": 25, "counted": ["1.0.0", "1.1.0", "1.2.0", "1.3.0"],
                          "failed": [{"release": "1.1.0", "incidents": ["IS0001"],
                                      "bugs": ["BG0001"]}],
                          "pending": [], "unrecorded": [], "since": "2026-01-01",
                          "until": "2026-03-31", "settle_days": 14, "not_measured": None},
                         _json(self.root))
        # the script itself, as the operator runs it
        proc = subprocess.run([sys.executable, str(loader.SCRIPTS_DIR / "escape.py"),
                               "failure-rate", "--root", str(self.root), *WINDOW],
                              capture_output=True, text=True, timeout=60,
                              env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual((0, out), (proc.returncode, proc.stdout), proc.stderr)

    def test_a_release_younger_than_the_settling_period_is_pending(self) -> None:
        _ac1(self.root, ("1.4.0", "2026-03-25"))
        rc, out, _ = _rate(self.root)
        self.assertEqual(0, rc)
        self.assertEqual("change failure rate 25% (1 of 4 releases)", out.splitlines()[0])
        self.assertEqual("1.0.0, 1.1.0, 1.2.0, 1.3.0", _line(out, "counted"))
        self.assertEqual("1.4.0 (inside the 14-day settling period)", _line(out, "pending"))
        data = _json(self.root)
        self.assertEqual((["1.4.0"], 25), (data["pending"], data["rate_percent"]))
        self.assertNotIn("1.4.0", data["counted"] + [f["release"] for f in data["failed"]])
        rc, out, _ = _rate(self.root, "--settle-days", "3")
        self.assertEqual("change failure rate 20% (1 of 5 releases)", out.splitlines()[0])
        self.assertEqual("1.0.0, 1.1.0, 1.2.0, 1.3.0, 1.4.0", _line(out, "counted"))
        self.assertEqual("none", _line(out, "pending"))
        self.assertIn("3-day settling period", _line(out, "window"))
        self.assertEqual((3, 20), (_json(self.root, "--settle-days", "3")["settle_days"],
                                   _json(self.root, "--settle-days", "3")["rate_percent"]))

    def test_no_release_or_no_incident_record_reads_not_measured(self) -> None:
        cases = {
            # one: the record file holds no release dated in the window, while an incident is
            # recorded, so the release record is what is absent
            "no release": (lambda r: (_records(r, ("0.9.0", "2025-12-01")),
                                      _issue(r), _bug(r, "BG0001", "v0.9.0")),
                           "not measured: no release record in the window",
                           "release_cut.py changelog-cut"),
            # two: four settled releases, and the one issue's Root Cause is only the scaffold
            "no incident": (lambda r: (_records(r, *AC1_RELEASES),
                                       _issue(r, cause=file_finding.ROOT_CAUSE_SCAFFOLD),
                                       _bug(r, "BG0001", "v1.1.0")),
                            "not measured: no incident recorded", "## Root Cause"),
        }
        for label, (build, reason, hint) in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                build(root)
                rc, out, err = _rate(root)
                self.assertEqual((0, ""), (rc, err))
                self.assertTrue(out.splitlines()[0].startswith(f"change failure rate {reason}"),
                                out)
                self.assertIn(hint, out)
                self.assertNotIn("%", out, "an unmeasured project printed a percentage")
                self.assertEqual(2, len(out.splitlines()),
                                 "an unmeasured project printed counted and failed lines")
                data = _json(root)
                self.assertIsNone(data["rate_percent"])
                self.assertTrue(data["not_measured"].startswith(reason.split(": ", 1)[1]))
        # three: four settled releases, and the incident's escaped bug shipped in a release
        # recorded outside the window - measured, and nothing failed
        _records(self.root, ("0.9.0", "2025-12-01"), *AC1_RELEASES)
        _issue(self.root)
        _bug(self.root, "BG0001", "v0.9.0")
        rc, out, _ = _rate(self.root)
        self.assertEqual("change failure rate 0% (0 of 4 releases)", out.splitlines()[0])
        self.assertEqual("1.0.0, 1.1.0, 1.2.0, 1.3.0", _line(out, "counted"))
        self.assertEqual("none", _line(out, "failed"))
        self.assertNotIn("unrecorded", out)
        data = _json(self.root)
        self.assertEqual((0, None, []), (data["rate_percent"], data["not_measured"],
                                         data["unrecorded"]))

    def test_the_deploy_help_names_the_command_and_its_sources(self) -> None:
        page = (SKILL / "help" / "deploy.md").read_text(encoding="utf-8")
        commands = page.split("\n## Commands\n", 1)[1].split("\n## ", 1)[0]
        rows = [ln for ln in commands.splitlines() if ln.startswith("| `escape.py failure-rate")]
        self.assertEqual(1, len(rows), "the deploy help's Commands table has no failure-rate row")
        row = rows[0]
        for needle in ("--since", "--until", "--settle-days", "release_cut.py changelog-cut",
                       "incident", "## Root Cause", "escaped bug", "pending",
                       "`deploy.py metrics`", "`failed`", "`rolled-back`", "deploy ledger",
                       "not measured"):
            self.assertIn(needle, row)
        self.assertRegex(row, rf"--until[^|]*\b{escape.WINDOW_DAYS} days ending\b")
        self.assertRegex(row, rf"--settle-days[^|]*default {escape.SETTLE_DAYS}\b")
        ref = (SKILL / "reference-scripts-review.md").read_text(encoding="utf-8")
        section = ref.split("\n### `escape.py`\n", 1)[1].split("\n### ", 1)[0]
        self.assertIn("failure-rate", section)
        self.assertIn("failure_rate", section)

    # ---- links -------------------------------------------------------------------------

    def test_an_incident_linked_through_decomposed_into_alone_fails_each_release(self) -> None:
        _records(self.root, *AC1_RELEASES)
        _issue(self.root, decomposed="bg0001, BG0003")
        _bug(self.root, "BG0001", "v1.1.0", None)
        _bug(self.root, "BG0003", "1.3.0", None)
        data = _json(self.root)
        self.assertEqual(50, data["rate_percent"])
        self.assertEqual([{"release": "1.1.0", "incidents": ["IS0001"], "bugs": ["BG0001"]},
                          {"release": "1.3.0", "incidents": ["IS0001"], "bugs": ["BG0003"]}],
                         data["failed"])

    def test_an_incident_linked_through_parent_alone_fails_each_release(self) -> None:
        _records(self.root, *AC1_RELEASES)
        _issue(self.root, decomposed=None)
        _bug(self.root, "BG0001", "V1.1.0", "is0001", escaped="Yes")
        _bug(self.root, "BG0003", "v1.3.0", "IS0001 (the checkout incident)")
        data = _json(self.root)
        self.assertEqual(50, data["rate_percent"])
        self.assertEqual(["1.1.0", "1.3.0"], [f["release"] for f in data["failed"]])

    def test_two_bugs_and_two_incidents_in_one_release_fail_it_once(self) -> None:
        _records(self.root, *AC1_RELEASES)
        _issue(self.root, "IS0001", decomposed="BG0001, BG0003")
        _issue(self.root, "IS0002", decomposed="BG0004")
        for bid in ("BG0001", "BG0003", "BG0004"):
            _bug(self.root, bid, "v1.1.0", None)
        rc, out, _ = _rate(self.root)
        self.assertEqual("change failure rate 25% (1 of 4 releases)", out.splitlines()[0])
        self.assertEqual("1.1.0 (incidents IS0001, IS0002; bugs BG0001, BG0003, BG0004)",
                         _line(out, "failed"))

    def test_a_bug_naming_a_release_no_record_holds_is_named_and_moves_no_figure(self) -> None:
        _ac1(self.root)
        _bug(self.root, "BG0003", "v9.9.9", "IS0001")
        rc, out, _ = _rate(self.root)
        self.assertEqual("change failure rate 25% (1 of 4 releases)", out.splitlines()[0])
        self.assertEqual("BG0003 names v9.9.9 (incident IS0001); it moves no figure: record the "
                         "release or correct the bug's Shipped-in",
                         _line(out, "linked to an unrecorded release"))
        self.assertEqual([{"bug": "BG0003", "shipped_in": "v9.9.9", "incidents": ["IS0001"]}],
                         _json(self.root)["unrecorded"])

    def test_a_linked_bug_not_escaped_or_with_no_release_moves_nothing(self) -> None:
        _ac1(self.root)
        _bug(self.root, "BG0003", "v1.2.0", "IS0001", escaped="no")
        _bug(self.root, "BG0004", None, "IS0001")
        data = _json(self.root)
        self.assertEqual((25, ["1.1.0"], []), (data["rate_percent"],
                                               [f["release"] for f in data["failed"]],
                                               data["unrecorded"]))

    def test_a_root_cause_the_gate_reads_as_unwritten_makes_no_incident(self) -> None:
        unwritten = {"the scaffold": file_finding.ROOT_CAUSE_SCAFFOLD,
                     "an HTML comment": "<!-- why it got through -->",
                     "a slot": "{{root_cause}}",
                     "an italic prompt": "> *Say why the defect got through the unit.*",
                     "an empty section": ""}
        for label, cause in unwritten.items():
            with self.subTest(label), tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                _records(root, *AC1_RELEASES)
                _issue(root, cause=cause)
                _bug(root, "BG0001", "v1.1.0")
                self.assertTrue(_json(root)["not_measured"].startswith("no incident recorded"))
        _records(self.root, *AC1_RELEASES)
        _issue(self.root, cause=CAUSE)
        _bug(self.root, "BG0001", "v1.1.0")
        self.assertEqual(25, _json(self.root)["rate_percent"])

    def test_an_issue_carrying_its_own_escaped_field_is_judged_by_its_root_cause(self) -> None:
        for cause, expect in ((CAUSE, 25), (file_finding.ROOT_CAUSE_SCAFFOLD, None)):
            with self.subTest(written=cause == CAUSE), \
                    tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                _records(root, *AC1_RELEASES)
                _issue(root, cause=cause, extra="> **Escaped:** no\n")
                _bug(root, "BG0001", "v1.1.0")
                self.assertEqual(expect, _json(root)["rate_percent"])

    # ---- settling, the window and the order of the reasons -----------------------------

    def test_a_pending_release_with_an_incident_stays_pending(self) -> None:
        _ac1(self.root, ("1.4.0", "2026-03-25"))
        _bug(self.root, "BG0003", "v1.4.0", "IS0001")
        data = _json(self.root)
        self.assertEqual((25, ["1.4.0"], ["1.1.0"]),
                         (data["rate_percent"], data["pending"],
                          [f["release"] for f in data["failed"]]))

    def test_the_settling_boundary_is_exactly_the_period(self) -> None:
        _ac1(self.root, ("1.4.0", "2026-03-17"), ("1.5.0", "2026-03-18"))
        data = _json(self.root)
        self.assertIn("1.4.0", data["counted"], "a release exactly 14 days old is settled")
        self.assertEqual(["1.5.0"], data["pending"])

    def test_the_window_includes_both_end_dates(self) -> None:
        # recorded out of date order, so the counted releases are seen to be sorted by date
        _records(self.root, ("0.3.0", "2026-03-31"), ("0.1.0", "2025-12-31"),
                 ("0.2.0", "2026-01-01"), ("0.4.0", "2026-04-01"))
        _issue(self.root)
        _bug(self.root, "BG0001", "v0.2.0")
        # an issue and a bug that cannot be read as UTF-8 are skipped, not a crash
        (self.root / "sdlc-studio" / "issues" / "IS0009-unreadable.md").write_bytes(b"\xff\xfe")
        (self.root / "sdlc-studio" / "bugs" / "BG0009-unreadable.md").write_bytes(b"\xff\xfe")
        data = _json(self.root, "--settle-days", "0")
        self.assertEqual((["0.2.0", "0.3.0"], 50), (data["counted"], data["rate_percent"]))

    def test_the_default_window_is_the_ninety_days_ending_on_its_end_date(self) -> None:
        _ac1(self.root)
        today = _today()
        data = _json(self.root, window=())
        self.assertEqual(((today - timedelta(days=89)).isoformat(), today.isoformat(), 14),
                         (data["since"], data["until"], data["settle_days"]))
        data = _json(self.root, window=("--until", "2026-03-31"))
        self.assertEqual(("2026-01-01", "2026-03-31", 25),
                         (data["since"], data["until"], data["rate_percent"]))
        data = _json(self.root, window=("--since", "2026-01-01"))
        self.assertEqual(("2026-01-01", today.isoformat()), (data["since"], data["until"]))

    def test_a_future_end_date_settles_against_today(self) -> None:
        today = _today()
        _records(self.root, ("2.0.0", (today - timedelta(days=20)).isoformat()),
                 ("2.1.0", (today - timedelta(days=3)).isoformat()))
        _issue(self.root)
        _bug(self.root, "BG0001", "v2.0.0")
        data = _json(self.root, window=("--since", (today - timedelta(days=60)).isoformat(),
                                        "--until", (today + timedelta(days=30)).isoformat()))
        self.assertEqual((["2.0.0"], ["2.1.0"], 100),
                         (data["counted"], data["pending"], data["rate_percent"]))

    def test_every_release_pending_reads_not_measured_naming_them(self) -> None:
        for with_incident in (False, True):
            with self.subTest(with_incident=with_incident), \
                    tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                _records(root, ("1.5.0", "2026-03-20"), ("1.6.0", "2026-03-25"))
                if with_incident:
                    _issue(root)
                    _bug(root, "BG0001", "v1.5.0")
                rc, out, _ = _rate(root)
                self.assertEqual("change failure rate not measured: every release in the window "
                                 "is still inside the 14-day settling period: 1.5.0, 1.6.0",
                                 out.splitlines()[0])
                self.assertNotIn("%", out)
                self.assertEqual(["1.5.0", "1.6.0"], _json(root)["pending"])

    # ---- the percentage ----------------------------------------------------------------

    def test_the_percentage_is_whole_when_exact_and_one_decimal_otherwise(self) -> None:
        _records(self.root, *AC1_RELEASES[:3])
        _issue(self.root, decomposed="BG0001")
        _bug(self.root, "BG0001", "v1.1.0", None)
        rc, out, _ = _rate(self.root)
        self.assertEqual("change failure rate 33.3% (1 of 3 releases)", out.splitlines()[0])
        self.assertEqual(33.3, _json(self.root)["rate_percent"])
        _bug(self.root, "BG0003", "v1.2.0")
        rc, out, _ = _rate(self.root)
        self.assertEqual("change failure rate 66.7% (2 of 3 releases)", out.splitlines()[0])
        _records(self.root, *AC1_RELEASES)
        rate = _json(self.root)["rate_percent"]
        self.assertEqual((50, int), (rate, type(rate)))

    # ---- refusals ----------------------------------------------------------------------

    def test_a_flag_that_does_not_parse_is_refused_naming_it(self) -> None:
        _ac1(self.root)
        cases = (("--since", ("--since", "2026-13-01", "--until", "2026-03-31")),
                 ("--since", ("--since", "20260101", "--until", "2026-03-31")),
                 ("--until", ("--since", "2026-01-01", "--until", "yesterday")),
                 ("--settle-days", ("--settle-days", "-1", *WINDOW)),
                 ("--settle-days", ("--settle-days", "x", *WINDOW)),
                 ("--since", ("--since", "2026-04-01", "--until", "2026-03-31")))
        for flag, window in cases:
            with self.subTest(window=window):
                rc, out, err = _rate(self.root, window=window)
                self.assertEqual((2, ""), (rc, out))
                self.assertIn(flag, err)
        rc, out, err = _rate(self.root, window=("--since", "2026-04-01", "--until", "2026-03-31"))
        self.assertIn("--until", err)
        rc, out, _ = _rate(self.root, "--settle-days", "0",
                           window=("--since", "2026-02-02", "--until", "2026-02-02"))
        self.assertEqual((0, "change failure rate 100% (1 of 1 releases)"),
                         (rc, out.splitlines()[0]))

    def test_a_record_that_does_not_parse_is_refused_naming_its_line(self) -> None:
        good = _record("1.0.0", "2026-01-05")
        bad = {"not JSON": "{not json",
               "no version": json.dumps({"date": "2026-01-05", "reports": []}),
               "reports not a list": json.dumps({"version": "1.1.0", "date": "2026-02-02",
                                                 "reports": "RPT0001"}),
               "no date": json.dumps({"version": "1.1.0", "reports": []}),
               "a number for a date": _record("1.1.0", 20260202),
               "a short date": _record("1.1.0", "2026-2-2"),
               "no such day": _record("1.1.0", "2026-02-30")}
        for label, line in bad.items():
            with self.subTest(label), tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                _records(root, lines=[good, "", line])
                _issue(root)
                _bug(root, "BG0001", "v1.0.0")
                rc, out, err = _rate(root)
                self.assertEqual((2, ""), (rc, out))
                self.assertIn("line 3", err)

    def test_a_release_recorded_twice_is_refused_naming_both_lines(self) -> None:
        for again in ("1.1.0", "v1.1.0"):
            with self.subTest(again=again), tempfile.TemporaryDirectory(prefix="cfr_") as d:
                root = _project(d)
                _records(root, *AC1_RELEASES, (again, "2026-03-20"))
                _issue(root)
                _bug(root, "BG0001", "v1.1.0")
                rc, out, err = _rate(root)
                self.assertEqual((2, ""), (rc, out))
                self.assertIn("lines 2 and 5", err)

    # ---- the function the report calls, and the declaration ----------------------------

    def test_the_function_returns_what_the_json_prints_and_refuses_as_the_cli_does(self) -> None:
        _ac1(self.root, ("1.4.0", "2026-03-25"))
        self.assertEqual(_json(self.root),
                         escape.failure_rate(self.root, since="2026-01-01", until="2026-03-31"))
        for kwargs in ({"since": "2026-04-01", "until": "2026-03-31"},
                       {"since": "2026-01-01", "until": "2026-03-31", "settle_days": -1},
                       {"since": "2026-1-1", "until": "2026-03-31"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(escape.RateRefused):
                escape.failure_rate(self.root, **kwargs)

    def test_the_report_declares_failure_rate_as_a_non_ceremony_verb(self) -> None:
        sprint_report = loader.load_script("sprint_report")
        self.assertEqual(("failure-rate", "to-class", "trace"),
                         sprint_report.NON_CEREMONY_VERBS["escape"])


if __name__ == "__main__":
    unittest.main()
