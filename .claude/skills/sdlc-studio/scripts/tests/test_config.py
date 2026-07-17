"""Tests for config.py - config-defaults.yaml as single source (CR0008). RED first."""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "config.py"
DEFAULTS = Path(__file__).resolve().parent.parent.parent / "templates" / "config-defaults.yaml"
REF_DOC = Path(__file__).resolve().parent.parent.parent / "reference-config.md"

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def _load():
    spec = importlib.util.spec_from_file_location("config", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["config"] = mod
    spec.loader.exec_module(mod)
    return mod


def _flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class LoadTests(unittest.TestCase):
    def test_default_resolves_from_yaml(self) -> None:
        mod = _load()
        self.assertEqual(mod.get(".", "coverage.unit"), 90)
        self.assertEqual(mod.get(".", "story_quality.sizing.max_ac"), 10)
        self.assertIsNone(mod.get(".", "no.such.key"))

    def test_project_override(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "coverage:\n  unit: 99\n", encoding="utf-8")
            self.assertEqual(mod.get(root, "coverage.unit"), 99)      # overridden
            self.assertEqual(mod.get(root, "coverage.integration"), 85)  # default kept


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class IntegrationTests(unittest.TestCase):
    def test_status_reads_config(self) -> None:
        # AC1: a core script (status.py) actually consumes config-defaults.yaml.
        spec = importlib.util.spec_from_file_location(
            "status", SCRIPT.parent / "status.py")
        status = importlib.util.module_from_spec(spec)
        sys.modules["status"] = status
        spec.loader.exec_module(status)
        data = status.gather(Path("."))
        self.assertIsNotNone(data["config"])
        self.assertEqual(data["config"]["schema_version"], 2)


class DocTests(unittest.TestCase):
    def test_no_duplicate_yaml_fences(self) -> None:
        # The duplicate machine-readable blocks must be gone; the YAML lives once.
        self.assertNotIn("```yaml", REF_DOC.read_text(encoding="utf-8"))

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_doc_defaults_match_yaml(self) -> None:
        # Every numeric Default documented in reference-config.md must equal the
        # value in config-defaults.yaml (drift-proof single source).
        flat = _flatten(yaml.safe_load(DEFAULTS.read_text(encoding="utf-8")))
        rows = re.findall(r"^\|\s*`([\w.]+)`\s*\|\s*(\d+)\s*\|", REF_DOC.read_text(encoding="utf-8"), re.M)
        self.assertTrue(rows, "no documented defaults found to guard")
        for key, val in rows:
            matches = [v for path, v in flat.items() if path == key or path.endswith("." + key)]
            self.assertTrue(matches, f"doc key {key} not found in config-defaults.yaml")
            self.assertIn(int(val), [int(m) for m in matches], f"{key}={val} drifted from YAML {matches}")


class GracefulDegradeTests(unittest.TestCase):
    """BG0093: config.get must warn-and-default when config cannot be loaded (no PyYAML /
    unreadable), never crash - unifying the three failure regimes into one."""

    def test_get_returns_default_when_yaml_unavailable(self) -> None:
        from unittest import mock
        config = _load()
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(config, "_yaml",
                                   side_effect=RuntimeError("config loading needs PyYAML")):
                # must NOT raise - degrade to the supplied default
                self.assertEqual(config.get(d, "quality.mutation_max", 25), 25)
                self.assertIsNone(config.get(d, "routing", None))

    def test_get_degrades_on_malformed_yaml(self) -> None:
        # BG0160: a syntactically broken override raises yaml.YAMLError (Parser/Scanner),
        # a subclass of Exception - NOT ValueError - so it was uncaught and tracebacked
        # through every consumer. The BG0093 contract is warn-and-default; hold it here
        # against the real malformed condition CR0180's AC demanded and never got.
        config = _load()
        with tempfile.TemporaryDirectory() as d:
            override = Path(d) / "sdlc-studio" / ".config.yaml"
            override.parent.mkdir(parents=True, exist_ok=True)
            override.write_text("pricing:\n  opus: [unclosed\n", encoding="utf-8")
            # must NOT raise - degrade to the supplied default
            self.assertEqual(config.get(d, "pricing.opus", "DEFAULT"), "DEFAULT")


if __name__ == "__main__":
    unittest.main()
