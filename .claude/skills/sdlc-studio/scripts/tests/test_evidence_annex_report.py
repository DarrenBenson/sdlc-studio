"""The report of record holds to the evidence annex a consumer parses it by.

`reference-evidence-schema.md` publishes the report's envelope, the shape of a section and of a
figure, the section catalogue, every figure and row key and the source grammar, as Markdown
tables under fixed headings. A consumer's parser reads those tables, so these tests read them the
same way: the heading, the table beneath it, the code span in each row's first cell. Prose on the
page satisfies nothing here.

The schema-2 pages are ones `sprint close` files in a throwaway git run. The schema-1 pages are
the four this repository holds, copied into a fixture, because no writer produces schema 1.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-evidence-schema.md
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil

REPO = Path(__file__).resolve().parents[5]
ANNEX = Path(__file__).resolve().parents[2] / "reference-evidence-schema.md"
RUN = "RUN-01ANNEXRPT"
RETRO = "RETRO0001"
#: A model the shipped price table prices, so the cost sections carry their priced figures.
MODEL = "claude-opus-5-5"
#: The schema-1 pages this repository holds: no writer produces schema 1 any more.
SCHEMA_ONE = ("RPT0002", "RPT0003", "RPT0004", "RPT0005")


def _live(name: str):
    """The module as `sys.modules` holds it NOW, imported on first use (see test_lean_close)."""
    return sys.modules.get(name) or importlib.import_module(name)


# --- the annex, read as a consumer reads it ------------------------------------------------------

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_SPAN = re.compile(r"`([^`]+)`")


def _block(heading: str) -> list[str]:
    """The lines beneath the one heading titled `heading`, up to the next heading of its level
    or above. A missing or repeated heading fails: a parser keyed on it would break too."""
    lines = ANNEX.read_text(encoding="utf-8").splitlines()
    hits = [i for i, ln in enumerate(lines)
            if (m := _HEADING.match(ln)) and m.group(2) == heading]
    if len(hits) != 1:
        raise AssertionError(f"the annex carries {len(hits)} headings titled {heading!r}")
    level = len(_HEADING.match(lines[hits[0]]).group(1))
    out = []
    for ln in lines[hits[0] + 1:]:
        m = _HEADING.match(ln)
        if m and len(m.group(1)) <= level:
            break
        out.append(ln)
    return out


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def annex_table(heading: str) -> list[dict[str, str]]:
    """The first table beneath `heading`, one mapping of column title to cell per row."""
    lines = _block(heading)
    start = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("|")), None)
    if start is None:
        raise AssertionError(f"no table under the annex heading {heading!r}")
    rows = []
    for ln in lines[start:]:
        if not ln.lstrip().startswith("|"):
            break
        rows.append(ln)
    head = _cells(rows[0])
    return [dict(zip(head, _cells(ln))) for ln in rows[2:]]


def _key(cell: str) -> str:
    """The key a row documents: the code span opening its cell, never the prose."""
    m = _SPAN.match(cell)
    if not m:
        raise AssertionError(f"a catalogue row names no key in a code span: {cell!r}")
    return m.group(1)


def keyed(heading: str, column: str) -> dict[str, dict[str, str]]:
    """`annex_table(heading)` by the key in `column`, refusing a key documented twice."""
    out: dict[str, dict[str, str]] = {}
    for row in annex_table(heading):
        k = _key(row[column])
        if k in out:
            raise AssertionError(f"{heading!r} documents {k!r} twice")
        out[k] = row
    return out


def figure_keys() -> set[tuple[str, str, str]]:
    """`(section, where, key)` for every figure key and row key the annex catalogues: `where`
    is `figures` for a section's figures, else the row list the row key sits in."""
    out = {(_key(r["Section"]), "figures", _key(r["Figure"]))
           for r in annex_table("Report figure keys")}
    out |= {(_key(r["Section"]), _key(r["In"]), _key(r["Row key"]))
            for r in annex_table("Report row keys")}
    return out


def source_parts_resolve(source: str) -> bool:
    """Does every part of a figure's `source` read under the annex's source grammar? Parts are
    joined by a comma and a space; each is a declared non-path source, a workspace path or a
    `.jsonl` file outside the workspace."""
    non_path = tuple(keyed("Report non-path sources", "Source"))
    prefixes = tuple(keyed("Report workspace prefixes", "Prefix"))
    return all(p.startswith(non_path) or p.startswith(prefixes) or p.endswith(".jsonl")
               for p in (part.strip() for part in source.split(", ")) if p)


# --- the fixture run, closed through `sprint close` ---------------------------------------------

def _git(root: Path, *argv: str, when: str | None = None) -> None:
    env = gitutil.git_env()
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(["git", "-C", str(root), *argv], env=env, check=True, capture_output=True)


def _commit(root: Path, when: str, *paths: str) -> None:
    for rel in paths:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"{rel} at {when}\n", encoding="utf-8")
    _git(root, "add", "--", *paths)
    _git(root, "commit", "-q", "-m", f"change at {when}", when=when)


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _components(scale: int) -> dict:
    """A meter reading's priced components, so the run's cost can be priced in dollars."""
    return {"input": 100_000 * scale, "output": 50_000 * scale, "cache_write_5m": 0,
            "cache_write_1h": 20_000 * scale, "cache_read": 400_000 * scale}


def _run(root: Path, full: bool) -> None:
    """A run one delivered unit wide. Both runs carry metered and priced cost, the spend by
    role, delegated tokens, a plan, rulings and a waiver in force. `full` adds what fills each
    conditional section: a refusal log and a checklist row the close could not measure."""
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    _git(root, "init", "-q")
    _git(root, "add", ".gitignore")
    _git(root, "commit", "-q", "-m", "base", when="2026-09-01T00:00:00Z")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           "# US0101: widget\n\n> **Status:** Done\n> **Points:** 3\n> **Epic:** EP0001\n"
           "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")
    _write(root, "sdlc-studio/retros/RETRO0001-annex.md",
           "# RETRO-0001: annex\n\n> **Date:** 2026-09-20\n\n## Delivered\n\n"
           "- US0101 - shipped\n\n## Lessons\n\n- learned a thing\n")
    _write(root, "sdlc-studio/decisions.md",
           "# Decisions\n\n| ID | Decision | Rationale | Status | Supersedes | Date |\n"
           "| --- | --- | --- | --- | --- | --- |\n"
           "| D0001 | waiver: review.line_coverage | coverage cannot run here | accepted |  "
           "| 2026-09-20 |\n")
    _commit(root, "2026-09-02T00:00:00Z", "src/widget.py")
    _git(root, "add", "sdlc-studio")
    _git(root, "commit", "-q", "-m", "artefacts", when="2026-09-02T00:00:01Z")
    _commit(root, "2026-09-20T10:00:00Z", "src/widget.py")
    state = {
        "schema": 1, "run_id": RUN, "started_at": "2026-09-20T08:00:00Z", "ended_at": None,
        "outcome": "running", "sprint_goal": "a consumer can parse the page",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it parsed"},
        "batch": ["US0101"], "handoff": None,
        "plan_snapshot": {
            "units": {"US0101": {"planned_points": 3, "forecast_tokens": 300_000,
                                 "forecast_minutes": 30.0, "added": False}},
            "rates": {"tokens_per_point": {"value": 100_000, "source": "median of 5 runs"},
                      "minutes_per_point": {"value": 10.0, "source": "median of 5 runs"}}},
        "unit_actuals": {"US0101": {"started_at": "2026-09-20T08:10:00Z", "start_tokens": 0,
                                    "minutes": 40.0, "tokens": 400_000, "open": False}},
        "close_known_issues": [{"source": "installed-copy",
                                "detail": "the installed copy was not refreshed"}],
        "rulings": [
            {"id": "D0002", "by": "persona", "seat": "qa", "subject": "a", "kind": "ruling"},
            {"id": "D0003", "by": "operator", "seat": None, "subject": "b", "kind": "cited"}],
        "session_token_stamps": [
            {"tokens": 1_000_000, "source": "/t/s1.jsonl", "at": "2026-09-20T08:00:00Z",
             "kind": "open", "model": MODEL, "components": _components(1)},
            {"tokens": 2_700_000, "source": "/t/s1.jsonl", "at": "2026-09-20T18:00:00Z",
             "kind": "report", "model": MODEL, "components": _components(3),
             "cost_roles": {"source": "s1", "subagent_files": 1, "roles": [
                 {"role": "main", "agents": 1, "calls": 12, "priced": 900_000, "share": 0.6,
                  "split": {"cache_read": 0.5, "cache_write": 0.3, "output": 0.2},
                  "first_context": 20_000, "avg_context": 60_000,
                  "cache_writes": {"growth": 1_000, "rewrite_5m": 200, "rewrite_1h": 300}}],
                 "total": {"agents": 1, "calls": 12, "priced": 900_000}}}],
        # The second agent is tagged to the unit with its minutes and priced split, so the unit
        # row's figures carry the `label` that names where their reading came from.
        "delegated_tokens": [{"tokens": 123_456, "agent": "reviewer", "note": "",
                              "provenance": "supplied", "model": MODEL},
                             {"tokens": 200_000, "agent": "builder", "note": "",
                              "provenance": "supplied", "model": MODEL, "unit": "US0101",
                              "minutes": 25.0, "priced": 500_000,
                              "by_model": {MODEL: _components(1)}}],
    }
    if full:
        state["close_not_measured"] = [
            {"id": "C9", "title": "a row with nothing to measure",
             "detail": "the run changed no file this row reads"}]
        _write(root, "sdlc-studio/.local/refusals.jsonl",
               json.dumps({"lane": "gate", "ts": "2026-09-20T09:00:00Z",
                           "staged": ["src/widget.py"]}) + "\n")
    _write(root, "sdlc-studio/.local/run-state.json", json.dumps(state))


def _close(root: Path) -> dict:
    """Close the fixture run through `sprint close` and return the JSON page it filed. The chain
    steps are stubbed to pass, as in test_lean_lane_yield: what is under test is the page."""
    mod = _live("sprint")
    stack = contextlib.ExitStack()
    stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
    stack.enter_context(unittest.mock.patch.object(
        _live("sprint_report").sdlc_md, "now_iso8601", lambda *a, **k: "2026-09-24T12:00:00Z"))
    for name in mod._CLOSE_CHAIN:
        stack.enter_context(unittest.mock.patch.object(
            mod, "_close_" + name.replace("-", "_"),
            lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
    out, err = io.StringIO(), io.StringIO()
    with stack, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(["close", "--retro", RETRO, "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"sprint close refused the fixture run ({rc}):\n"
                             f"{out.getvalue()}\n{err.getvalue()}")
    state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                       .read_text(encoding="utf-8"))
    page = root / "sdlc-studio" / "reports" / f"{state['report']}.json"
    return json.loads(page.read_text(encoding="utf-8"))


def _figure_sets(page: dict):
    """`(section, where, key, figure)` for every figure on the page: a section's figures, its
    row lists and its not-measured marker (`where` is `not_measured`, `key` None)."""
    for sec in page["sections"]:
        if sec.get("not_measured"):
            yield sec["key"], "not_measured", None, sec["not_measured"]
        for k, f in (sec.get("figures") or {}).items():
            yield sec["key"], "figures", k, f
        for rows in ("rows", "unit_rows"):
            for row in sec.get(rows) or []:
                for k, f in row.items():
                    yield sec["key"], rows, k, f


class ReportAnnexTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        # The fixture's git calls must see the fixture, never an inherited GIT_DIR.
        patcher = unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _filed(self, full: bool) -> dict:
        root = self.tmp / ("full" if full else "bare")
        root.mkdir()
        _run(root, full)
        return _close(root)

    def test_a_filed_report_conforms_to_the_annex(self) -> None:
        """AC1. MUTANT: add a section, figure key, row key or envelope mark to `build_report`
        with no catalogue row (a mention in the annex's prose does not count). MUTANT: stop
        emitting a section the catalogue marks always emitted."""
        page = self._filed(full=True)
        envelope = keyed("Report envelope keys", "Key")
        sections = keyed("Report sections", "Section")
        section_shape = set(keyed("Report section shape", "Key"))
        figure_shape = set(keyed("Report figure shape", "Field"))
        catalogued = figure_keys()
        present = {s["key"]: s for s in page["sections"]}
        # The fixture carries every section, or the conformance below proves less than it says.
        self.assertEqual(set(sections), set(present), "the full fixture lost a section")

        self.assertEqual(set(), set(page) - set(envelope), "envelope keys the annex lacks")
        for k, row in envelope.items():
            if row["Presence"] in ("always", "rule mark"):
                self.assertIn(k, page, f"the envelope's {k} is documented as {row['Presence']}")
            fixed = _SPAN.fullmatch(row["Value"])
            if fixed and k in page:   # a rule mark's value is part of its contract
                self.assertEqual(fixed.group(1), str(page[k]), f"the envelope's {k}")
        always = {k for k, r in sections.items() if r["Emitted"] == "always"}
        self.assertEqual(set(), always - set(present), "always-emitted sections missing")
        sr = _live("sprint_report")
        self.assertEqual(set(sr.FRONT_PAGE),
                         {k for k, r in sections.items() if r["Placement"] == "front page"})
        for key, sec in present.items():
            self.assertEqual(sections[key]["Title"], sec["title"], f"section {key} title")
            self.assertEqual(set(), set(sec) - section_shape, f"section {key} keys")
        seen, fields = set(), set()
        for section, where, key, f in _figure_sets(page):
            self.assertEqual(set(), set(f) - figure_shape, f"{section}.{key} figure fields")
            fields |= set(f)
            self.assertTrue(source_parts_resolve(f["source"]),
                            f"{section}.{key} source {f['source']!r} is outside the grammar")
            if key is not None:
                self.assertIn((section, where, key), catalogued,
                              f"{section} {where} key {key!r} is not in the annex's tables")
                seen.add((section, where, key))
        # The full page carries every key the catalogue lists, so no row documents a dead key.
        self.assertEqual(set(), catalogued - seen, "catalogued keys no page carries")
        # Every documented figure field is on the page too, so the unit row's `label` stays
        # reached: a fixture with no agent tagged to its unit would test the shape by halves.
        self.assertEqual(set(), figure_shape - fields, "documented figure fields no page carries")
        self.assertEqual(set(sr.NON_PATH_SOURCES),
                         set(keyed("Report non-path sources", "Source")))
        self.assertEqual(set(sr.WORKSPACE_PREFIXES),
                         set(keyed("Report workspace prefixes", "Prefix")))

    def test_the_section_catalogue_matches_what_the_builder_emits(self) -> None:
        """AC2. MUTANT: keep a catalogue row for a section the builder no longer emits; mark a
        conditional section always emitted; add a conditional section with no row."""
        full, bare = self._filed(full=True), self._filed(full=False)
        catalogue = keyed("Report sections", "Section")
        on_full = [s["key"] for s in full["sections"]]
        on_bare = [s["key"] for s in bare["sections"]]
        self.assertEqual(set(catalogue), set(on_full) | set(on_bare))
        self.assertEqual({"always", "conditional"},
                         {r["Emitted"] for r in catalogue.values()})
        conditional = {k for k, r in catalogue.items() if r["Emitted"] == "conditional"}
        self.assertEqual(conditional, set(catalogue) - set(on_bare))
        self.assertTrue(conditional, "the bare run lacks no section, so it tests nothing")
        for k, r in catalogue.items():
            named = r["Absent when"] not in ("", "-")
            self.assertEqual(k in conditional, named,
                             f"{k}: a conditional section names when it is absent, and only one")
        order = list(catalogue)   # the page carries its sections in the catalogue's order
        for keys in (on_full, on_bare):
            self.assertEqual(keys, sorted(keys, key=order.index))

    def test_schema_one_is_documented_as_it_stands(self) -> None:
        """AC3. MUTANT: catalogue only the fifteen sections the first page carries, leaving
        `waivers` out; mark `waivers` required; document schema 1 as re-derivable."""
        root = self.tmp / "schema-one"
        reports = root / "sdlc-studio" / "reports"
        reports.mkdir(parents=True)
        for rid in SCHEMA_ONE:
            for src in (REPO / "sdlc-studio" / "reports").glob(f"{rid}*"):
                shutil.copy2(src, reports / src.name)
        pages = [json.loads((reports / f"{rid}.json").read_text(encoding="utf-8"))
                 for rid in SCHEMA_ONE]
        self.assertEqual({1}, {p["schema"] for p in pages})
        held = [{s["key"] for s in p["sections"]} for p in pages]
        envs = [set(p) for p in pages]

        sections = keyed("Report schema 1 sections", "Section")
        self.assertEqual(set(sections), set.union(*held))
        self.assertEqual({"optional", "always"}, {r["Emitted"] for r in sections.values()})
        optional = {k for k, r in sections.items() if r["Emitted"] == "optional"}
        self.assertEqual(optional, set.union(*held) - set.intersection(*held))
        self.assertEqual({"waivers"}, optional)
        envelope = keyed("Report schema 1 envelope keys", "Key")
        self.assertEqual(set(envelope), set.union(*envs))
        self.assertEqual({k for k, r in envelope.items() if r["Presence"] == "optional"},
                         set.union(*envs) - set.intersection(*envs))
        self.assertEqual({"window_end"}, set.union(*envs) - set.intersection(*envs))

        schemas = keyed("Report schemas", "Schema")
        self.assertEqual("no", schemas["1"]["Re-derivable"])
        self.assertEqual("yes", schemas["2"]["Re-derivable"])
        self.assertIn("the page stands as filed", schemas["1"]["Check answers"])
        for rid in SCHEMA_ONE:
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = _live("sprint_report").main(["--root", str(root), "check", "--report", rid])
            self.assertEqual(2, rc, err.getvalue())
            self.assertIn("cannot be re-derived - the page stands as filed", err.getvalue())


if __name__ == "__main__":
    unittest.main()
