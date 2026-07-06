"""US0063/CR0174: the consolidated audit-check runs the team-schema rules with stable ids."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


audit = _load("audit_check")


def _v3(root: Path) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    pd = root / "sdlc-studio" / "personas"; pd.mkdir(parents=True, exist_ok=True)
    (pd / "sam.md").write_text("# Sam Eriksson - QA\n", encoding="utf-8")


def _bug(root: Path, body: str) -> None:
    d = root / "sdlc-studio" / "bugs"; d.mkdir(parents=True, exist_ok=True)
    (d / "_index.md").write_text(
        "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 1 |\n\n"
        "## All\n\n| ID | Title | Status | Severity | Created | Updated |\n"
        "| --- | --- | --- | --- | --- | --- |\n| [BG0001](BG0001-x.md) | x | Open | Low | -- | -- |\n",
        encoding="utf-8")
    (d / "BG0001-x.md").write_text(body, encoding="utf-8")


class AuditCheckTests(unittest.TestCase):
    def test_clean_repo_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _v3(root)
            _bug(root, "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                       "> **Raised-by:** Sam Eriksson; persona; v1\n\n## Evidence\n\n`a/b.py:9` wrong\n")
            self.assertEqual(audit.run(root), [])
            self.assertEqual(audit.main(["check", "--root", str(root)]), 0)

    def test_missing_authorship_and_evidence_reported_with_stable_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _v3(root)
            _bug(root, "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n\n## Summary\n\nx\n")
            rules = {f["rule"] for f in audit.run(root)}
            self.assertIn("authorship-structured", rules)
            self.assertIn("evidence-present", rules)
            self.assertEqual(audit.main(["check", "--root", str(root)]), 1)

    def test_rule_ids_are_stable(self) -> None:
        self.assertEqual(audit.RULE_IDS[:3],
                         ("authorship-structured", "authorship-type", "authorship-unresolved"))


if __name__ == "__main__":
    unittest.main()
