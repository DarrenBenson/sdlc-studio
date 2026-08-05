"""Unit tests for the v3 triage noise controls (US0067): Low-severity consolidation and the
per-session creation cap. Enforced at creation time and dormant under schema_version 2.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import datetime
import importlib.util
import inspect
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _affect(root: Path, rel: str) -> None:
    """Make a fixture's declared Affects path real on disk so the BG0144 grooming gate resolves it."""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tn = _load("triage_noise", "triage_noise.py")
ff = _load("file_finding", "file_finding.py")


def _repo(root: Path, cap: int = 20, v3: bool = True, low_consolidation: bool = True) -> Path:
    """A repo with bug + change-request indexes; opt into v3 + a triage config when asked."""
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text(
            f"schema_version: 3\ntriage:\n  session_cap: {cap}\n"
            f"  low_consolidation: {'true' if low_consolidation else 'false'}\n",
            encoding="utf-8")
    for rel, header, summary in (
        ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
         "| inbox | 0 |\n| Open | 0 |\n| Fixed | 0 |"),
        ("change-requests",
         "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
         "| inbox | 0 |\n| Proposed | 0 |\n| Complete | 0 |")):
        d = sd / rel
        d.mkdir(parents=True, exist_ok=True)
        sep = "|" + " --- |" * (header.count("|") - 1)
        (d / "_index.md").write_text(
            f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
            f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    # Every fixture below files a finding whose declared Affects is `src/thing.py` (see `_bug`).
    # BG0144's grooming gate refuses a unit whose Affects paths all fail to resolve, so make it real.
    _affect(root, "src/thing.py")
    return root


def _bug(severity: str) -> dict:
    # Groomed: both creators refuse a finding `sprint plan` could not plan (BG0136), so even a
    # Low nit names the files it touches and its size before it can fold into a themed CR.
    return {"severity": severity, "summary": "s", "steps": "r", "fix": "f",
            "affects": "src/thing.py", "points": 3}


class ConsolidationTests(unittest.TestCase):
    """AC1: a Low-severity finding folds into a themed consolidation CR; Medium+ stays individual."""

    def test_consolidate_low_finding_into_cr(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertTrue(res.get("consolidated_into"))            # folded, not standalone
            self.assertFalse(list((root / "sdlc-studio" / "bugs").glob("BG*.md")))  # no bug file
            cr = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("## Consolidated Findings", cr)
            self.assertIn("a nit", cr)
            self.assertIn("> **Consolidation:** low-severity-bugs", cr)  # separator-safe slug marker

    def test_consolidate_theme_with_field_separator_stays_one_cr(self) -> None:
        # A theme containing `·` (the inline metadata separator) must still match on read-back -
        # the marker is a slug, so extract_field cannot truncate it into a fresh CR per finding.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            a = ff.file_finding(root, "bug", "one", {**_bug("low"), "theme": "auth · session"})
            b = ff.file_finding(root, "bug", "two", {**_bug("low"), "theme": "auth · session"})
            self.assertEqual(a["consolidated_into"], b["consolidated_into"])
            self.assertEqual(len(list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))), 1)

    def test_consolidate_theme_case_and_whitespace_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            a = ff.file_finding(root, "bug", "one", {**_bug("low"), "theme": "Perf Path"})
            b = ff.file_finding(root, "bug", "two", {**_bug("low"), "theme": "perf   path"})
            self.assertEqual(a["consolidated_into"], b["consolidated_into"])

    def test_consolidate_second_low_appends_to_same_cr(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            first = ff.file_finding(root, "bug", "nit one", _bug("low"))
            second = ff.file_finding(root, "bug", "nit two", _bug("low"))
            self.assertEqual(first["consolidated_into"], second["consolidated_into"])  # one CR
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 1)
            body = crs[0].read_text(encoding="utf-8")
            self.assertIn("nit one", body)
            self.assertIn("nit two", body)

    def test_consolidate_low_with_tranche_flags_the_drop(self) -> None:
        # A record-only tranche cannot ride onto a shared consolidation CR; the drop must be
        # visible (fail loud, not silent) - the EP0014 principle applied to a cross-unit edge.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a nit", {**_bug("low"), "tranche": "sprint-14"})
            self.assertTrue(res.get("consolidated_into"))
            self.assertEqual(res.get("tranche_dropped"), "sprint-14")
            cr = Path(res["path"]).read_text(encoding="utf-8")
            self.assertNotIn("Tranche", cr)   # not silently written onto the shared CR

    def test_consolidate_medium_stays_individual(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a real defect", _bug("medium"))
            self.assertIsNone(res.get("consolidated_into"))
            self.assertIn("> **Status:** inbox", Path(res["path"]).read_text(encoding="utf-8"))

    def test_consolidate_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), v3=False)
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertIsNone(res.get("consolidated_into"))          # filed individually on v2
            self.assertIn("> **Status:** Open", Path(res["path"]).read_text(encoding="utf-8"))

    def test_consolidate_off_when_low_consolidation_false(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), low_consolidation=False)
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            self.assertIsNone(res.get("consolidated_into"))          # individual, into inbox


class TriageEnabledKnobTests(unittest.TestCase):
    """CR0510. The controls were reachable only through a schema v3 bump that also switches on
    plan-review, spec-guard and the inbox status - so adopting a session cap meant adopting four
    unrelated things, and they had never once run on the project that built them: 801 findings
    filed in a month against an unused cap of 20, with the low-severity fold hand-rolled."""

    def test_a_v2_project_that_ASKS_gets_the_controls(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / ".config.yaml").write_text(
                "schema_version: 2\ntriage:\n  enabled: true\n  low_consolidation: true\n",
                encoding="utf-8")
            self.assertTrue(tn.active(root),
                            "a v2 project stating triage.enabled still gets no controls, so the "
                            "knob is decorative and the schema bump is still the only route")
            self.assertTrue(tn.should_consolidate(root, "low"))

    def test_an_UNSET_knob_keeps_the_previous_behaviour_exactly(self) -> None:
        """The compatibility half. Every consuming project has no `triage` block, and the change
        must be invisible to all of them - a knob that silently switches controls on for someone
        who never asked is a worse defect than the one being fixed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / ".config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
            self.assertFalse(tn.active(root), "an unset knob turned the controls ON under v2")
            (sd / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
            self.assertTrue(tn.active(root), "an unset knob turned the controls OFF under v3")

    def test_the_knob_can_turn_them_OFF_under_v3(self) -> None:
        """Both directions, or it is a switch with one position."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio"
            sd.mkdir(parents=True, exist_ok=True)
            (sd / ".config.yaml").write_text(
                "schema_version: 3\ntriage:\n  enabled: false\n", encoding="utf-8")
            self.assertFalse(tn.active(root))
            self.assertFalse(tn.should_consolidate(root, "low"))

    def test_the_SHIPPED_repo_config_has_them_on(self) -> None:
        """This project's own config, not a fixture. The whole point is that it stops being
        the project that ships a noise control it has never run."""
        # parents[5], not [4]: tests -> scripts -> sdlc-studio -> skills -> .claude -> root.
        # The first version was off by one and SKIPPED, which reads as a pass - so it reported
        # green whether or not this repo had the controls on, which is the only thing it checks.
        repo = Path(__file__).resolve().parents[5]
        cfg = repo / "sdlc-studio" / ".config.yaml"
        self.assertTrue(cfg.is_file(),
                        f"{cfg} not found - this test skips into a false pass if it cannot "
                        f"locate the repo, so it fails instead")
        self.assertTrue(tn.active(repo),
                        "this repo files ~26 findings a day with the controls switched off")


class ConsolidationBulletTests(unittest.TestCase):
    """A consolidation bullet must render a multi-line summary faithfully, not squeeze it onto one
    line. A raw newline embedded in the bullet breaks the summary's later lines OUT of the list
    item, so they land as bare top-level lines (and a line shaped like `> **Status:** x` forges a
    metadata line). Each continuation line is indented to stay part of the item instead."""

    def test_multi_line_summary_is_rendered_faithfully_not_flattened(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            summary = "first line of detail\nsecond line of detail\nthird line"
            ff.file_finding(root, "bug", "a low nit", {**_bug("low"), "summary": summary})
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 1)
            lines = crs[0].read_text(encoding="utf-8").splitlines()
            for ln in summary.splitlines():                    # nothing is dropped
                self.assertTrue(any(ln in b for b in lines), f"summary line lost: {ln!r}")
            i = next(k for k, ln in enumerate(lines) if ln.startswith("- **a low nit**"))
            # every continuation line is indented under the bullet, never a bare top-level line
            self.assertTrue(lines[i + 1].startswith("  "),
                            f"continuation not indented (flattened): {lines[i + 1]!r}")
            self.assertTrue(lines[i + 2].startswith("  "),
                            f"continuation not indented (flattened): {lines[i + 2]!r}")


class SessionCapTests(unittest.TestCase):
    """AC2: the N+1th finding in a session is refused loudly."""

    def test_session_cap_refuses_the_n_plus_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            ff.file_finding(root, "bug", "one", _bug("medium"))      # 1
            ff.file_finding(root, "bug", "two", _bug("medium"))      # 2
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "three", _bug("medium"))  # 3 -> refused
            self.assertIn("session cap reached", str(ctx.exception).lower())

    def test_session_cap_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2, v3=False)
            for t in ("one", "two", "three"):                        # cap not enforced on v2
                ff.file_finding(root, "bug", t, _bug("medium"))
            self.assertEqual(len(list((root / "sdlc-studio" / "bugs").glob("BG*.md"))), 3)

    def test_consolidated_appends_do_not_consume_budget(self) -> None:
        # Opening a consolidation CR mints one artefact (counts once); appending Low findings to
        # it mints nothing, so a Low flood cannot exhaust the session cap.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            for t in ("nit a", "nit b", "nit c", "nit d"):
                ff.file_finding(root, "bug", t, _bug("low"))
            self.assertEqual(tn.session_count(root), 1)              # only the CR open counted


class SessionKeyTests(unittest.TestCase):
    """BG0520: the session cap was a LIFETIME cap.

    `_session_key()` returned `os.environ.get("SDLC_TRIAGE_SESSION", "default")`, and nothing in
    the skill ever set that variable. So every session in a project's whole life shared the key
    `default`, the counter climbed monotonically and stayed at the cap, and filing was then
    refused permanently on a project that had done nothing wrong. Hit live at exactly 20,
    mid-run, while filing the residue of a unit whose own criteria required it to be filed.
    """

    def _run(self, root: Path, run_id: str | None) -> None:
        p = root / "sdlc-studio" / ".local" / "run-state.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        if run_id is None:
            p.unlink(missing_ok=True)
            return
        p.write_text(json.dumps({
            "schema": 1, "run_id": run_id, "started_at": "2026-08-05T00:00:00Z",
            "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0001"]}),
            encoding="utf-8")

    def setUp(self) -> None:
        # The documented explicit exit must not be in force, or every case below reads its value
        # instead of the key under test - a fixture that supplies the thing under test.
        self._prior = os.environ.pop("SDLC_TRIAGE_SESSION", None)
        if self._prior is not None:
            self.addCleanup(os.environ.__setitem__, "SDLC_TRIAGE_SESSION", self._prior)

    def test_the_count_resets_across_a_run_boundary(self) -> None:
        """AC1, and the defect itself. Mutant: restore the `default` fallback - the count
        survives the boundary and filing is refused for good."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            self._run(root, "RUN-AAAA")
            ff.file_finding(root, "bug", "one", _bug("medium"))
            ff.file_finding(root, "bug", "two", _bug("medium"))
            self.assertEqual(tn.session_count(root), 2)
            self._run(root, "RUN-BBBB")                    # the next run opens
            self.assertEqual(tn.session_count(root), 0,
                             "the counter survived a real session boundary")
            ff.file_finding(root, "bug", "three", _bug("medium"))   # and filing works again

    def test_the_cap_still_fires_within_one_run(self) -> None:
        """AC2, the positive control. Mutant: key on something unique per call - the cap never
        fires and the noise control this exists for is gone, while AC1 still passes."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            self._run(root, "RUN-AAAA")
            ff.file_finding(root, "bug", "one", _bug("medium"))
            ff.file_finding(root, "bug", "two", _bug("medium"))
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "three", _bug("medium"))
            self.assertIn("session cap reached", str(ctx.exception).lower())

    def test_no_open_run_keys_on_the_date(self) -> None:
        """AC3. Mutant: fall back to a constant when no run is open - the lifetime cap returns
        by the back door for exactly the sessions that file most, which is how this began."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            self._run(root, None)
            key = tn._session_key(root)
            self.assertTrue(key.startswith("date:"), key)
            self.assertIn(datetime.date.today().isoformat(), key)
            self.assertNotEqual(key, "default")

    def test_an_explicit_session_variable_still_wins(self) -> None:
        """AC4: the documented exit keeps working, over an open run, because consuming projects
        may rely on it. Mutant: consult the run first - an operator who named a session is
        silently given the run's instead."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=2)
            self._run(root, "RUN-AAAA")
            os.environ["SDLC_TRIAGE_SESSION"] = "mine"
            self.addCleanup(os.environ.pop, "SDLC_TRIAGE_SESSION", None)
            self.assertEqual(tn._session_key(root), "mine")

    def test_the_refusal_names_only_exits_that_work(self) -> None:
        """AC5. The message offered three exits and only one worked: triaging decrements
        nothing, so the first suggestion was false at the moment it was read - and the message
        is the only thing an operator has at that point. Mutant: leave the wording alone - the
        tool tells them to do something that cannot help.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=1)
            self._run(root, "RUN-AAAA")
            ff.file_finding(root, "bug", "one", _bug("medium"))
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "bug", "two", _bug("medium"))
            msg = str(ctx.exception)
            self.assertNotIn("triage the backlog", msg)
            self.assertIn("RUN-AAAA", msg, "the key in force is what tells them how to move it")
            self.assertIn("SDLC_TRIAGE_SESSION", msg)

    def test_the_writer_and_the_reader_resolve_the_same_key(self) -> None:
        """A counter stamped under one key and read under another never matches, so the cap
        never fires - the opposite failure, and just as silent. Mutant: drop `root` from the
        writer's call - it stamps the date key while the reader resolves the run id, and the
        count reads 0 forever."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d), cap=5)
            self._run(root, "RUN-AAAA")
            ff.file_finding(root, "bug", "one", _bug("medium"))
            stored = json.loads(
                (root / "sdlc-studio" / ".local" / "triage-session.json").read_text())
            self.assertEqual(stored["session"], tn._session_key(root))
            self.assertEqual(tn.session_count(root), 1)


class ConsolidationSlugTests(unittest.TestCase):
    """The default theme is already `low-severity <type>s`, and both the title and the filename
    prepend `Low-severity` - so neither may double it into `low-severity-low-severity-...`."""

    def test_default_theme_cr_slug_and_title_not_doubled(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = ff.file_finding(root, "bug", "a nit", _bug("low"))
            path = Path(res["path"])
            self.assertNotIn("low-severity-low-severity", path.name)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("Low-severity low-severity", text)
            # the stored marker key is unchanged, so read-back matching still folds the next find
            self.assertIn("> **Consolidation:** low-severity-bugs", text)


def _consolidation_rev_row(body: str) -> str:
    """The first Revision History data row of a consolidation CR body."""
    lines = body.splitlines()
    head = next(i for i, ln in enumerate(lines) if ln.strip().startswith("## Revision History"))
    rows = [ln for ln in lines[head:] if ln.strip().startswith("|")]
    return rows[2]  # header, separator, then the opened row


class ConsolidationSharedWriterTests(unittest.TestCase):
    """The consolidation CR is the third creator. Two distinct properties, two distinct guards:

    * AC1 (singular choke point) is a purely STRUCTURAL benefit - the routed form
      `rev_row(today, {"_raised_by": x}, "Consolidation opened")` is byte-identical to the
      open-coded `join_row([today, authorship_name(x), "Consolidation opened"])`, so a regression
      to open-coding is unobservable at output level. It is guarded at SOURCE level below (mirroring
      the BG0114 source-scan pattern), which reddens against the open-coded form.
    * AC2 (index author) and the escaping property are behavioural and guarded by the two tests
      that follow the source-scan.
    """

    def test_revision_row_is_built_through_rev_row_not_open_coded(self) -> None:
        # AC1's benefit is structural (one choke point), unobservable in output because the routed
        # and open-coded forms render identical bytes. So pin it at source: `_new_consolidation_cr`
        # must call `file_finding.rev_row(` and must NOT rebuild the row inline with a `join_row([`
        # carrying the "Consolidation opened" literal. Reddens against a revert to open-coding.
        src = inspect.getsource(tn._new_consolidation_cr)
        self.assertIn("file_finding.rev_row(", src,
                      "the revision row is not routed through the shared rev_row writer")
        self.assertIsNone(
            re.search(r"join_row\(\[[^\]]*Consolidation opened", src),
            "the revision row is open-coded inline via join_row rather than routed through rev_row")

    def test_revision_row_author_pipe_is_escaped(self) -> None:
        # A second, behavioural guard on the ESCAPING property only (not routing - the source-scan
        # above owns that): a pipe in the author must be escaped so the revision row stays a single
        # 3-column row rather than splitting and dropping the Change cell. It does not depend on
        # which `file_finding` module object is loaded, so it cannot go flaky under full discovery.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            ff.file_finding(root, "bug", "a low nit", {**_bug("low"), "author": "Sam | Bob"})
            crs = list((root / "sdlc-studio" / "change-requests").glob("CR*.md"))
            self.assertEqual(len(crs), 1)
            row = _consolidation_rev_row(crs[0].read_text(encoding="utf-8"))
            self.assertEqual(len(ff.sdlc_md.table_cells(row)), 3, row)  # not split into 4
            self.assertIn(r"Sam \| Bob", row)                           # escaped, not raw
            self.assertIn("Consolidation opened", row)                  # Change cell intact

    def test_index_row_carries_the_author(self) -> None:
        # A consuming project whose CR index defines an Author column: the header-driven row
        # builder must fill it with the authorship of record, never '--'.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            idx = root / "sdlc-studio" / "change-requests" / "_index.md"
            idx.write_text(
                "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| inbox | 0 |\n"
                "| **Total** | **0** |\n\n## All\n\n"
                "| ID | Title | Status | Priority | Type | Author | Date |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
            ff.file_finding(root, "bug", "a low nit",
                            {**_bug("low"), "author": "Dani Okafor; agent; v2"})
            row = next(ln for ln in idx.read_text(encoding="utf-8").splitlines()
                       if ln.startswith("| ["))
            cells = ff.sdlc_md.table_cells(row)
            self.assertEqual(cells[5], "Dani Okafor")  # the Author column, not '--'


if __name__ == "__main__":
    unittest.main()
