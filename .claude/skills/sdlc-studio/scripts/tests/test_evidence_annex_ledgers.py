"""The lesson class store, the evidence logs and the four ledgers hold to the evidence annex.

`reference-evidence-schema.md` documents the fields of a lesson class row and its hits, of an
actuals, forecast and audit-cost line, and the columns of the critic, velocity, decisions and
deploy ledgers, as Markdown tables under fixed headings. These tests read those tables the way a
consumer's parser does (the annex reader is the report test's, shared) and hold them to what the
shipped writers produce in a throwaway project, each driven through its own command line rather
than read from its constants alone.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-evidence-schema.md
from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_evidence_annex_report as annex  # noqa: E402 - the annex reader, shared
import test_lean_report as lean_report  # noqa: E402 - a run `retro.py accuracy` can measure

SCRIPTS = Path(__file__).resolve().parents[1]
EVIDENCE = Path("sdlc-studio") / "retros" / "evidence"


def _live(name: str):
    """The module as `sys.modules` holds it NOW, imported on first use (see test_lean_close)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _cli(root: Path, script: str, *argv: str) -> str:
    """Run a shipped script's command line in `root`, failing on a refusal; its stdout."""
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / f"{script}.py"), *argv],
                       cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                       timeout=120, check=False)
    if r.returncode != 0:
        raise AssertionError(f"{script} {' '.join(argv)} exited {r.returncode}:\n"
                             f"{r.stdout}\n{r.stderr}")
    return r.stdout


def _lines(root: Path, prefix: str) -> list[dict]:
    """Every JSON line in the evidence logs whose file name starts with `prefix`."""
    out = []
    for path in sorted((root / EVIDENCE).glob(f"{prefix}-*.jsonl")):
        out += [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln]
    return out


def _header(path: Path, first: str) -> list[str]:
    """The cells of the ledger's header row: the first table row whose first cell is `first`."""
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.lstrip().startswith("|") and cells[0] == first:
            return cells
    raise AssertionError(f"{path} holds no table headed {first!r}")


def documented(heading: str) -> tuple[set[str], set[str]]:
    """`(every field, the required ones)` the annex documents under `heading`."""
    rows = annex.keyed(heading, "Field")
    bad = {k: r["Required"] for k, r in rows.items() if r["Required"] not in ("yes", "no")}
    if bad:
        raise AssertionError(f"{heading!r} marks fields neither yes nor no: {bad}")
    return set(rows), {k for k, r in rows.items() if r["Required"] == "yes"}


def columns(heading: str) -> list[str]:
    """The column names the annex lays out under `heading`, in order."""
    return [annex._key(r["Column"]) for r in annex.annex_table(heading)]


def line_problems(heading: str, line: dict) -> list[str]:
    """Each way a written line breaks the annex's table under `heading`: a field it does not
    document, or a field it marks required that the line lacks."""
    fields, required = documented(heading)
    return ([f"{heading}: {f!r} is not documented" for f in sorted(set(line) - fields)]
            + [f"{heading}: required {f!r} is missing" for f in sorted(required - set(line))])


def header_problems(heading: str, header: list[str]) -> list[str]:
    """How a ledger's header row differs from the annex's column list: equal, in order."""
    want = columns(heading)
    return [] if header == want else [f"{heading}: the annex lays out {want}, the ledger {header}"]


def _column(path: Path, first: str, column: str) -> list[str]:
    """Each data row's cell under `column` in the ledger table headed by `first`."""
    header, out = _header(path, first), []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if (line.lstrip().startswith("|") and len(cells) == len(header) and cells != header
                and not set(cells[0]) <= set("-: ")):
            out.append(cells[header.index(column)])
    return out


def tier_problems(written: set[str]) -> list[str]:
    """How the annex's critic `Tier` cell and the Tier cells `critic.py record` wrote disagree:
    a written value the cell's code spans do not spell, alone or as a value then a suffix, or a
    span (a flag name aside) that is no part of any written value."""
    meaning = next(r["Meaning"] for r in annex.annex_table("Critic ledger columns")
                   if annex._key(r["Column"]) == "Tier")
    spans = [s for s in re.findall(r"`([^`]+)`", meaning) if not s.startswith("--")]
    parts = {p for v in written for p in v.split(" ")}
    return ([f"Tier {v!r} is written but the annex does not spell it" for v in sorted(written)
             if v not in spans and not any(v == f"{b} {s}" for b in spans for s in spans)]
            + [f"Tier {s!r} is documented but never written" for s in spans if s not in parts])


class LedgerAnnexTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def _root(self, name: str) -> Path:
        root = self.tmp / name
        (root / "sdlc-studio").mkdir(parents=True)
        return root

    def _conforms(self, heading: str, line: dict) -> None:
        self.assertEqual([], line_problems(heading, line))

    def test_written_lines_conform_to_the_annex(self) -> None:
        """AC1. MUTANT: a field added to the actuals, forecast or audit-cost writer, or a key
        added to a lesson row or its hit, with no annex line. MUTANT: the annex marks required a
        field the writer does not always write."""
        root = self._root("logs")
        _cli(root, "telemetry", "record", "--root", ".", "--id", "US0001", "--type", "story",
             "--iterations", "2", "--wall-time-s", "60", "--stages", "build,review",
             "--verdict", "APPROVE", "--complexity", "3", "--churn", "40", "--reopened", "no",
             "--tokens", "1000", "--tier-recommended", "standard", "--tier-delivered",
             "standard", "--model", "claude-opus-5-5", "--escalated", "no",
             "--attempt", "claude-opus-5-5:1000")
        _cli(root, "telemetry", "forecast", "--root", ".", "--id", "US0001", "--tokens", "900",
             "--points", "3", "--estimator", "engineering seat", "--size-gate", "voluntary",
             "--constant", "per_point=300", "--planned-at", "2026-09-20T08:00:00Z")
        _cli(root, "audit_cost", "record", "--root", ".", "--lenses", "7", "--rounds", "3",
             "--votes", "3", "--est-agents", "217", "--est-tokens", "7800000",
             "--actual-agents", "265", "--actual-tokens", "12400000", "--actual-minutes", "95",
             "--notes", "a measured audit")
        written = {"Actuals line fields": _lines(root, "actuals"),
                   "Forecast line fields": _lines(root, "forecasts"),
                   "Audit cost line fields": _lines(root, "audit-cost")}
        for heading, lines in written.items():
            with self.subTest(log=heading):
                self.assertEqual(1, len(lines), f"{heading}: the writer wrote {len(lines)} lines")
                self._conforms(heading, lines[0])
        # Every supplied field reached the actuals line, so each one was held to the annex.
        tele = _live("telemetry")
        actuals = written["Actuals line fields"][0]
        self.assertEqual(set(tele.FIELDS), set(actuals) - {"project"})
        # The same check refuses a line in each direction it can break.
        self.assertEqual(["Actuals line fields: 'retries' is not documented"],
                         line_problems("Actuals line fields", {**actuals, "retries": 2}))
        self.assertEqual(["Actuals line fields: required 'project' is missing"],
                         line_problems("Actuals line fields",
                                       {k: v for k, v in actuals.items() if k != "project"}))
        # A field the writers declare but these commands cannot supply is documented too.
        for heading, declared in (("Actuals line fields", tele.FIELDS),
                                  ("Forecast line fields", tele.FORECAST_FIELDS),
                                  ("Audit cost line fields", _live("audit_cost").LEDGER_FIELDS)):
            with self.subTest(declared=heading):
                self.assertEqual(set(), set(declared) - documented(heading)[0])

        # The lesson store: a classed Try item recorded as a new class, then repeated.
        for n, item in ((1, "[new: scope drift | build, review] Review only the unit's diff. "
                            "Read the Affects before the diff."),
                        (2, "[LC-001] The review read the whole tree again.")):
            lean_retro = (root / "sdlc-studio" / "retros" / f"RETRO{n:04d}-a-sprint.md")
            lean_retro.parent.mkdir(parents=True, exist_ok=True)
            lean_retro.write_text(
                f"# RETRO-{n:04d}: a sprint\n\n> **Date:** 2026-09-24\n> **Batch:** US0001\n\n"
                f"## Keep\n\n- small units\n\n## Stop\n\n- plan review\n\n## Try\n\n- {item}\n",
                encoding="utf-8")
            _cli(root, "retro", "--root", ".", "extract", "--id", f"RETRO{n:04d}",
                 "--run", f"RUN-ANNEX000{n}")
        # The store starts from the skill's bundled seed, so the first extract writes the seed's
        # classes beside the new one; every line it holds is the writer's.
        rows = [json.loads(ln) for ln in (root / "sdlc-studio" / "lessons.jsonl")
                .read_text(encoding="utf-8").splitlines() if ln]
        new = [r for r in rows if r.get("recorded_run") == "RUN-ANNEX0001"]
        self.assertEqual(1, len(new), "extract wrote no line for the new class")
        hits = [h for r in rows for h in r.get("hits") or ()]
        self.assertEqual([("RUN-ANNEX0002", "retro:RETRO0002")],
                         [(h.get("run"), h.get("source")) for h in hits])
        for row in rows:
            with self.subTest(lesson=row.get("id")):
                self._conforms("Lesson class row fields", row)
        self._conforms("Lesson hit fields", hits[0])

    def test_ledger_headers_match_the_annex(self) -> None:
        """AC2. MUTANT: a column added to, removed from or moved in the critic delivery table,
        the velocity header, the decisions template or the deploy log, with no annex change."""
        critic_root = self._root("critic")
        _cli(critic_root, "critic", "record", "--root", ".", "--unit", "US0001",
             "--verdict", "APPROVE", "--reviewer", "qa seat", "--author", "builder",
             "--issues", "none")
        for unit, tier in (("US0002", ["--tier", "light"]),
                           ("US0003", ["--tier", "full", "--tier-explicit"])):
            _cli(critic_root, "critic", "record", "--root", ".", "--unit", unit,
                 "--verdict", "APPROVE", "--reviewer", "qa seat", "--author", "builder",
                 "--issues", "none", *tier)
        velocity_root = self.tmp / "velocity"
        velocity_root.mkdir()
        lean_report.lean_run(velocity_root)
        _cli(velocity_root, "retro", "--root", ".", "accuracy", "--id", lean_report.RETRO,
             "--tokens", "1823456", "--write")
        ledger_root = self._root("ledgers")
        _cli(ledger_root, "decisions", "add", "--root", ".", "--decision", "keep units small",
             "--rationale", "small units review well")
        _cli(ledger_root, "deploy", "record", "--root", ".", "--status", "rolled-out",
             "--detail", "the first release")
        ledgers = {
            "Critic ledger columns": _header(
                critic_root / "sdlc-studio" / "reviews" / "critic-verdicts.md", "Unit"),
            "Velocity history columns": _header(
                velocity_root / "sdlc-studio" / "retros" / "VELOCITY.md", "Retro"),
            "Decisions ledger columns": _header(
                ledger_root / "sdlc-studio" / "decisions.md", "ID"),
            "Deploy log columns": _header(ledger_root / "sdlc-studio" / "deploy-log.md", "When"),
        }
        for heading, header in ledgers.items():
            with self.subTest(ledger=heading):
                self.assertEqual([], header_problems(heading, header))
        self.assertEqual(9, len(columns("Critic ledger columns")))
        # Order counts: the same columns moved are refused.
        critic = ledgers["Critic ledger columns"]
        self.assertTrue(header_problems("Critic ledger columns", [*critic[1:], critic[0]]))
        # The Tier cell's values are the writer's: `-` with no tier, the tier, or the tier then
        # `(explicit)`, each spelt by the annex's cell and nothing else documented.
        written = set(_column(critic_root / "sdlc-studio" / "reviews" / "critic-verdicts.md",
                              "Unit", "Tier"))
        self.assertEqual({"-", "light", "full (explicit)"}, written)
        self.assertEqual([], tier_problems(written))
        # Both directions refuse: a value written but undocumented, a value documented but unwritten.
        self.assertTrue(tier_problems(written | {"full [explicit]"}))
        self.assertTrue(tier_problems(written - {"light"}))


if __name__ == "__main__":
    unittest.main()
