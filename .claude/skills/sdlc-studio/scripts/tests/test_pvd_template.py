"""Completeness tests for the PVD template + product manifest (CR0047)."""
from __future__ import annotations

import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
PVD = SKILL / "templates" / "core" / "pvd.md"
MANIFEST = SKILL / "templates" / "product-manifest.yaml"

LEAN = ["## 1. Vision & Scope", "## 2. Strategic Goals", "## 3. Master Feature Inventory",
        "## 4. Cross-Repo Dependencies", "## 5. API Contract Commitments",
        "## 6. Risk & Conflict Register", "## 7. Decisions Log"]
OPTIN = ["## 8. PVD Topology (opt-in)", "## 9. Governance Stage-Gates (opt-in)",
         "## 10. Release Coordination (opt-in)"]


class PvdTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.t = PVD.read_text(encoding="utf-8")

    def test_lean_sections_present(self) -> None:
        for s in LEAN:
            self.assertIn(s, self.t, f"missing lean section: {s}")

    def test_optin_sections_present_and_marked(self) -> None:
        for s in OPTIN:
            self.assertIn(s, self.t)
        self.assertIn("Opt-in: only for large", self.t)  # the tiering boundary marker

    def test_feature_map_traces_to_repo_and_prd_feature(self) -> None:
        # §3 must map a product feature to <repo>:<prd feature> (the traceability key).
        self.assertIn("{{repo}}:{{prd_feature_id}}", self.t)

    def test_coordinate_not_respecify_intent(self) -> None:
        self.assertIn("re-specifies", self.t)  # "coordinate and trace, never re-specify"

    def test_pm_owns_pvd(self) -> None:
        self.assertIn("Owner:** Product Manager", self.t)


class ManifestTemplateTests(unittest.TestCase):
    def test_manifest_has_repo_listing_keys(self) -> None:
        m = MANIFEST.read_text(encoding="utf-8")
        for key in ("product:", "master_pvd:", "repos:", "path:", "url:", "id:"):
            self.assertIn(key, m, f"manifest missing {key}")


if __name__ == "__main__":
    unittest.main()
