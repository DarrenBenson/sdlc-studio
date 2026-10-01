"""US0805: a `--fields-file` key spelled as the verb's own flag is accepted as its field.

A document is the shell-free form of an invocation, so a key spelled as the flag it replaces
(`ac` for `--ac`, `type` for `--type`, `status` for `--status`, `seat` for `--seat`) is read as
that field rather than refused as unknown. Every case runs the shipped CLI in a temporary
`init run` project.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
FILER = _SCRIPTS / "file_finding.py"
DECISIONS = _SCRIPTS / "decisions.py"

#: A bug finding complete enough to file, less its criteria.
FINDING = {"title": "a nit", "severity": "Low", "summary": "s", "steps": "r", "fix": "f",
           "affects": "src/thing.py", "points": 1}
ACS = ["given a then b", "given c then d"]
VERIFY = ["shell true", "shell true"]


def _project(root: Path) -> Path:
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True)
    (root / "src").mkdir()
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    return root


def _run(script: Path, root: Path, *argv: str, doc: dict | None = None):
    args = list(argv)
    if doc is not None:
        path = root / "doc.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        args += ["--fields-file", str(path)]
    return subprocess.run([sys.executable, str(script), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=120)


class FieldsFileFlagKeysTests(unittest.TestCase):

    def _filed_body(self, doc: dict) -> str:
        """The bug a document files, its minted id and filing time blanked so two filings
        compare."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            proc = _run(FILER, root, "file", "--type", "bug", "--format", "json", doc=doc)
            self.assertEqual(0, proc.returncode, proc.stderr)
            text = Path(json.loads(proc.stdout)["path"]).read_text(encoding="utf-8")
        text = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", "T", text)
        return re.sub(r"BG-[0-9A-Z]{8}", "BG-X", text)

    def test_ac_and_option_map_to_acs_and_options(self) -> None:
        """AC1. MUTANTS: (1) no alias - `ac` refused as unknown, exit 1; (2) the alias maps `ac`
        but drops `option`; (3) the alias wins over a canonical key present beside it, so a
        document carrying both spellings is no longer refused."""
        flag_spelt = {**FINDING, "ac": ACS, "verify": VERIFY, "option": ["opt one"]}
        canonical = {**FINDING, "acs": ACS, "verify": VERIFY, "options": ["opt one"]}
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            proc = _run(FILER, root, "file", "--type", "bug", "--dry-run", doc=flag_spelt)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn("would file", proc.stdout)
            both = _run(FILER, root, "file", "--type", "bug", "--dry-run",
                        doc={**canonical, "ac": ACS})
            self.assertEqual(1, both.returncode, "both spellings of one field stay refused")
            self.assertIn("unknown field(s): ac", both.stderr)
        body = self._filed_body(flag_spelt)
        self.assertEqual(self._filed_body(canonical), body)
        self.assertIn("given c then d", body)

    def test_decisions_add_reads_status_from_the_document(self) -> None:
        """AC2. MUTANTS: (1) `status` refused as unknown, exit 2; (2) read but the flag's default
        `accepted` overrides it; (3) an explicit `--status` no longer overrides the document."""
        doc = {"decision": "do x", "rationale": "because y", "status": "revisited"}
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            proc = _run(DECISIONS, root, "add", doc=doc)
            self.assertEqual(0, proc.returncode, proc.stderr)
            flag = _run(DECISIONS, root, "add", "--status", "accepted", doc=doc)
            self.assertEqual(0, flag.returncode, flag.stderr)
            rows = json.loads(_run(DECISIONS, root, "list", "--format", "json").stdout)
        self.assertEqual(["revisited", "accepted"], [r["status"] for r in rows[-2:]])

    def test_a_type_key_stands_in_for_the_type_flag(self) -> None:
        """AC3. MUTANTS: (1) `--type` still required by argparse, exit 2; (2) `type` read but
        refused as unknown by the loader, exit 1; (3) with neither, a default type is taken and
        the filing exits 0."""
        canonical = {**FINDING, "acs": ACS, "verify": VERIFY}
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            proc = _run(FILER, root, "file", "--dry-run", "--format", "json",
                        doc={**canonical, "type": "bug"})
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["id"].startswith("BG"), proc.stdout)
            neither = _run(FILER, root, "file", "--dry-run", doc=canonical)
            self.assertEqual(2, neither.returncode, neither.stdout)
            self.assertIn("--type", neither.stderr)

    def test_decisions_rule_reads_seat_and_subject_from_the_document(self) -> None:
        """AC4. MUTANTS: (1) `--seat`/`--subject` still required by argparse, exit 2; (2) read but
        refused as unknown fields; (3) the ruling recorded under a seat or subject other than the
        document's."""
        doc = {"seat": "engineering", "subject": "deps:action-pins", "question": "pin?",
               "ruling": "pin by sha", "reason": "tags move"}
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            proc = _run(DECISIONS, root, "rule", "--format", "json", doc=doc)
            self.assertEqual(0, proc.returncode, proc.stderr)
            rec = json.loads(proc.stdout)
            precedent = json.loads(_run(DECISIONS, root, "precedent", "--subject",
                                        "deps:action-pins", "--format", "json").stdout)
        self.assertEqual(("engineering", "deps:action-pins"), (rec["seat"], rec["subject"]))
        self.assertEqual([rec["id"]], [p["id"] for p in precedent])


if __name__ == "__main__":
    unittest.main()
