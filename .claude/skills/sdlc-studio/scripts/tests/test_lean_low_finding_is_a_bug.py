"""BG0731: a Low-severity finding mints its own bug; consolidation is opt-in (D0217).

D0217 ruled that a consolidation bucket is not a change request and retired CR0511 and CR0575.
With consolidation on (this repository sets it in its own config), the next Low finding rebuilt
the bucket the following day (CR0592): every Low finding on a schema-v3 project folded into a
themed CR. The shipped default is now off; a project that states `low_consolidation: true` keeps the old behaviour. Both filing
tests run the shipped `file_finding.py file` CLI in a fixture project.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent.parent
SCRIPT = SKILL / "scripts" / "file_finding.py"
REFERENCE = SKILL / "reference-config.md"
DEFAULTS = SKILL / "templates" / "config-defaults.yaml"

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

_INDEXES = (
    ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
     "| inbox | 0 |\n| Open | 0 |\n| Fixed | 0 |"),
    ("change-requests", "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
     "| inbox | 0 |\n| Proposed | 0 |\n| Complete | 0 |"),
)


def _project(root: Path, config: str) -> Path:
    """A fresh project holding the given `.config.yaml`, empty bug and CR indexes, and the one
    source file the filed finding declares as its Affects (the grooming gate resolves it)."""
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True)
    (sd / ".config.yaml").write_text(config, encoding="utf-8")
    for rel, header, summary in _INDEXES:
        d = sd / rel
        d.mkdir()
        sep = "|" + " --- |" * (header.count("|") - 1)
        (d / "_index.md").write_text(
            f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
            f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    return root


def _file_low(root: Path) -> dict:
    """File one Low bug through the shipped CLI; return its JSON result."""
    finding = {"title": "a low nit", "severity": "Low", "summary": "s", "steps": "r",
               "fix": "f", "affects": "src/thing.py", "points": 1}
    fields = root / "finding.json"
    fields.write_text(json.dumps(finding), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "file", "--type", "bug", "--fields-file", str(fields),
         "--root", str(root), "--format", "json"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "SDLC_TRIAGE_SESSION": "bg0731-test"})
    if proc.returncode != 0:
        raise AssertionError(f"file_finding exited {proc.returncode}:\n{proc.stdout}\n"
                             f"{proc.stderr}")
    return json.loads(proc.stdout)


def _artefacts(root: Path, rel: str, prefix: str) -> list[Path]:
    return sorted((root / "sdlc-studio" / rel).glob(f"{prefix}*.md"))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class LowFindingTests(unittest.TestCase):

    def test_a_low_finding_mints_its_own_bug_by_default(self) -> None:
        """AC1, for both shapes of "sets no triage keys": no `triage` block at all, and a block
        holding only commented-out keys. The second parses as YAML null, which replaces the
        defaults' whole `triage` mapping on merge, so `config.get` falls through to the
        caller's own fallback. MUTANTS: HEAD's shipped default `low_consolidation: true` (both
        cases fold into a `Low-severity bugs (consolidated)` CR); a `True` fallback in
        `triage_noise.low_consolidation` (the commented-out case folds)."""
        configs = {
            "no triage block": "schema_version: 3\n",
            "commented-out keys only": "schema_version: 3\ntriage:\n  # low_consolidation: true\n",
        }
        for label, config in configs.items():
            with self.subTest(config=label), tempfile.TemporaryDirectory() as d:
                root = _project(Path(d), config)
                res = _file_low(root)
                self.assertNotIn("consolidated_into", res,
                                 f"a Low finding was folded into a CR by default: {res}")
                bugs = _artefacts(root, "bugs", "BG")
                self.assertEqual(len(bugs), 1, f"expected one BG artefact, found {bugs}")
                self.assertIn("> **Severity:** Low", bugs[0].read_text(encoding="utf-8"))
                self.assertEqual(_artefacts(root, "change-requests", "CR"), [],
                                 "a Low finding created a change request by default")

    def test_an_opted_in_project_still_consolidates(self) -> None:
        """AC2. MUTANT: deleting consolidation outright (`should_consolidate` returning False)
        - the opted-in project gets a BG file and no themed CR."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d), "schema_version: 3\ntriage:\n  low_consolidation: true\n")
            res = _file_low(root)
            self.assertTrue(res.get("consolidated_into"),
                            f"an opted-in project did not consolidate: {res}")
            self.assertEqual(_artefacts(root, "bugs", "BG"), [],
                             "an opted-in Low finding minted its own bug")
            crs = _artefacts(root, "change-requests", "CR")
            self.assertEqual(len(crs), 1, f"expected one consolidation CR, found {crs}")
            body = crs[0].read_text(encoding="utf-8")
            self.assertIn("> **Consolidation:** low-severity-bugs", body)
            self.assertIn("a low nit", body)

    def test_the_reference_states_the_default(self) -> None:
        """AC3. MUTANT: flipping config-defaults.yaml while reference-config.md still documents
        `true` - the documented default no longer matches the shipped one."""
        rows = [line for line in REFERENCE.read_text(encoding="utf-8").splitlines()
                if line.startswith("| `triage.low_consolidation` |")]
        self.assertEqual(len(rows), 1, f"expected one triage.low_consolidation row: {rows}")
        cells = [c.strip() for c in rows[0].strip("|").split("|")]
        self.assertEqual(cells[1], "`false`", f"the documented default is {cells[1]}")
        self.assertRegex(cells[2], r"\bD0217\b", "the row does not cite D0217")
        shipped = yaml.safe_load(DEFAULTS.read_text(encoding="utf-8"))["triage"]
        self.assertIs(shipped["low_consolidation"], False,
                      "config-defaults.yaml does not ship low_consolidation off")
        self.assertEqual(re.sub(r"`", "", cells[1]), str(shipped["low_consolidation"]).lower(),
                         "reference-config.md and config-defaults.yaml disagree")


if __name__ == "__main__":
    unittest.main()
