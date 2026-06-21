"""Unit tests for product_reconcile.py - cross-repo feature-map traceability (CR0049)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "product_reconcile.py"


def _load():
    spec = importlib.util.spec_from_file_location("product_reconcile", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["product_reconcile"] = mod
    spec.loader.exec_module(mod)
    return mod


pr = _load()


def _fixture(d: Path, rows: str, child_feature: str | None = "F0007",
             manifest_repos: str | None = None, prd_body: str | None = None) -> tuple[Path, Path]:
    """Build tmp/product/{pvd.md,manifest.yaml} + tmp/repo-a/sdlc-studio/prd.md.
    The child PRD DECLARES the feature in a table (not prose) unless prd_body overrides."""
    prod = d / "product"
    prod.mkdir(parents=True, exist_ok=True)
    pvd_md = prod / "pvd.md"
    pvd_md.write_text(
        "# PVD\n\n## 3. Master Feature Inventory\n\n"
        "| PF ID | Feature | Owning repo | Child PRD feature | Priority | Status | Target |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n" + rows, encoding="utf-8")
    manifest = prod / "manifest.yaml"
    manifest.write_text(
        "master_pvd: product/pvd.md\nrepos:\n" + (manifest_repos or
        "  - id: repo-a\n    path: ../repo-a\n    url: https://x/repo-a\n"), encoding="utf-8")
    if child_feature is not None or prd_body is not None:
        prd = d / "repo-a" / "sdlc-studio" / "prd.md"
        prd.parent.mkdir(parents=True, exist_ok=True)
        body = prd_body if prd_body is not None else (
            f"# PRD\n\n## Features\n\n| ID | Feature | Status |\n| --- | --- | --- |\n"
            f"| {child_feature} | x | Done |\n")
        prd.write_text(body, encoding="utf-8")
    return pvd_md, manifest


class ProductReconcileTests(unittest.TestCase):
    def test_in_sync(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0001 | x | repo-a | repo-a:F0007 | H | Done | r1 |\n")
            r = pr.product_reconcile(p, m)
            self.assertTrue(r["ok"])
            self.assertEqual(r["findings"], [])
            self.assertEqual(r["features"], 1)

    def test_orphan_feature_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0002 | y | repo-a | repo-a:F9999 | H | Done | r1 |\n")
            r = pr.product_reconcile(p, m)
            self.assertFalse(r["ok"])
            self.assertEqual(r["findings"][0]["kind"], "orphan-feature")

    def test_unknown_repo_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0003 | z | repo-z | repo-z:F1 | H | Done | r1 |\n")
            r = pr.product_reconcile(p, m)
            self.assertFalse(r["ok"])
            self.assertEqual(r["findings"][0]["kind"], "unknown-repo")

    def test_repo_absent_degrades_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # child PRD not created -> repo-a PRD unreachable
            p, m = _fixture(Path(d), "| PF0004 | w | repo-a | repo-a:F0007 | H | Done | r1 |\n",
                            child_feature=None)
            r = pr.product_reconcile(p, m)
            self.assertTrue(r["ok"])  # advisory, not blocking
            self.assertEqual(r["findings"][0]["kind"], "repo-absent")
            self.assertEqual(r["unverified"], 1)

    def test_prose_mention_does_not_count(self) -> None:
        # HIGH regression: a feature id only in prose/changelog must be DRIFT, not a pass.
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0005 | v | repo-a | repo-a:F0007 | H | Done | r1 |\n",
                            prd_body="# PRD\n\nF0007 was removed in v2; see changelog.\n")
            r = pr.product_reconcile(p, m)
            self.assertFalse(r["ok"])
            self.assertEqual(r["findings"][0]["kind"], "orphan-feature")

    def test_substring_id_boundary(self) -> None:
        # PVD maps F7; PRD declares F70 - F70 must NOT satisfy F7.
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0006 | u | repo-a | repo-a:F7 | H | Done | r1 |\n",
                            child_feature="F70")
            self.assertFalse(pr.product_reconcile(p, m)["ok"])

    def test_missing_path_blocks_not_false_pass(self) -> None:
        # HIGH regression: a manifest repo with no path must not silently read base/.../prd.md.
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0007 | t | repo-a | repo-a:F0007 | H | Done | r1 |\n",
                            manifest_repos="  - id: repo-a\n    url: https://x/repo-a\n")
            r = pr.product_reconcile(p, m)
            self.assertFalse(r["ok"])
            self.assertEqual(r["findings"][0]["kind"], "missing-path")

    def test_empty_feature_map_signals(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "")  # no PF rows
            r = pr.product_reconcile(p, m)
            self.assertTrue(r["ok"])  # advisory
            self.assertEqual(r["findings"][0]["kind"], "empty-feature-map")

    def test_template_placeholder_skipped(self) -> None:
        text = ("## 3\n| PF0001 | x | {{repo}} | {{repo}}:{{prd_feature_id}} | H | Done | r |\n")
        self.assertEqual(pr.parse_feature_map(text), [])  # placeholder has no digit -> skipped

    def test_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p, m = _fixture(Path(d), "| PF0008 | s | repo-a | repo-a:F9999 | H | Done | r |\n")
            self.assertEqual(pr.main(["--pvd", str(p), "--manifest", str(m), "--format", "json"]), 1)
            p2, m2 = _fixture(Path(d), "| PF0009 | s | repo-a | repo-a:F0007 | H | Done | r |\n")
            self.assertEqual(pr.main(["--pvd", str(p2), "--manifest", str(m2)]), 0)

    def test_parse_feature_map(self) -> None:
        text = ("## 3. Master Feature Inventory\n"
                "| PF0001 | x | repo-a | repo-a:F0007 | H | Done | r1 |\n"
                "| not-a-pf | skip | - | - | - | - | - |\n")
        fm = pr.parse_feature_map(text)
        self.assertEqual(fm, [{"pf_id": "PF0001", "repo": "repo-a", "feature": "F0007"}])


if __name__ == "__main__":
    unittest.main()
