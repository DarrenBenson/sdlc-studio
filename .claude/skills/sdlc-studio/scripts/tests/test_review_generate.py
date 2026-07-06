"""Tests for the `review generate` on-ramp (US0070).

`review generate` is model-driven, but its deterministic spine is testable: the
zero-setup workspace bootstrap, the verbatim remediation-only security policy, and
the secret-absence guard over produced artefacts.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


rg = _load("review_generate")
next_id = _load("next_id")


class TestBootstrap(unittest.TestCase):
    """AC1: zero-setup - a folderless repo gets the folders the review needs."""

    def test_bootstrap_creates_workspace_on_folderless_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertFalse((root / "sdlc-studio").exists())
            result = rg.bootstrap(root)
            for rel in ("sdlc-studio/reviews", "sdlc-studio/bugs",
                        "sdlc-studio/change-requests"):
                self.assertTrue((root / rel).is_dir(), f"{rel} not created")
            self.assertTrue((root / "sdlc-studio/bugs/_index.md").exists())
            self.assertTrue((root / "sdlc-studio/change-requests/_index.md").exists())
            self.assertTrue(result["created"], "bootstrap reported nothing created")

    def test_bootstrap_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rg.bootstrap(root)
            second = rg.bootstrap(root)
            self.assertEqual(second["created"], [], "second bootstrap re-created files")

    def test_bootstrap_lets_a_review_id_be_allocated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rg.bootstrap(root)
            self.assertEqual(next_id.allocate_number("review", root, remote=False), 1)


class TestSecretHandling(unittest.TestCase):
    """AC2: remediation-only policy verbatim; secret values never in artefacts."""

    def test_secret_handling_policy_is_verbatim_in_template(self):
        tmpl = (SCRIPTS.parent / "templates" / "workflows" / "repo-review.md")
        self.assertTrue(tmpl.exists(), "repo-review prompt template missing")
        self.assertIn(rg.SECURITY_POLICY.strip(), tmpl.read_text(encoding="utf-8"),
                      "security policy not embedded verbatim in the prompt template")

    def test_secret_handling_scan_flags_a_planted_secret(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rg.bootstrap(root)
            secret = "AKIAIOSFODNN7EXAMPLE"
            (root / "sdlc-studio/bugs/BG9001-leak.md").write_text(
                f"# BG9001\n\nHard-coded key `{secret}` at config.py:12\n",
                encoding="utf-8")
            hits = rg.scan_secret(root, secret)
            self.assertTrue(hits, "planted secret not detected by scan_secret")
            self.assertIn("BG9001-leak.md", hits[0][0])

    def test_secret_handling_scan_clean_when_only_location_and_rotation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rg.bootstrap(root)
            secret = "AKIAIOSFODNN7EXAMPLE"
            (root / "sdlc-studio/bugs/BG9002-leak.md").write_text(
                "# BG9002\n\nHard-coded AWS key at config.py:12. "
                "Rotate the key in IAM and load it from the environment.\n",
                encoding="utf-8")
            self.assertEqual(rg.scan_secret(root, secret), [],
                             "clean remediation-only finding wrongly flagged")


if __name__ == "__main__":
    unittest.main()
