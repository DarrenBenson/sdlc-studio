"""Unit tests for repo_map.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "repo_map.py"
)
_spec = importlib.util.spec_from_file_location("repo_map", SCRIPT_PATH)
assert _spec and _spec.loader
repo_map = importlib.util.module_from_spec(_spec)
sys.modules["repo_map"] = repo_map
_spec.loader.exec_module(repo_map)


class FixtureRepo:
    """Construct a small throwaway repo for indexing tests."""

    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_test_"))
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / "core.py").write_text(
            "class AuthClient:\n"
            "    def login(self, email, password):\n"
            "        return True\n"
            "\n"
            "def hash_password(value):\n"
            "    return value\n"
        )
        (self.tmp / "src" / "api.py").write_text(
            "from src.core import AuthClient, hash_password\n"
            "\n"
            "class ApiServer:\n"
            "    def __init__(self):\n"
            "        self.auth = AuthClient()\n"
        )
        (self.tmp / "src" / "widget.ts").write_text(
            "import { AuthClient } from './core';\n"
            "\n"
            "export class Widget {\n"
            "    render() { return null; }\n"
            "}\n"
            "\n"
            "export function renderWidget() { return null; }\n"
        )
        (self.tmp / "node_modules").mkdir()
        (self.tmp / "node_modules" / "ignored.js").write_text(
            "function shouldNotIndex() {}"
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class RepoMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self.index_path = self.fixture.tmp / ".local" / "repo-map.json"

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def build(self) -> dict:
        rc = repo_map.main(
            [
                "build",
                "--root",
                str(self.fixture.tmp),
                "--out",
                str(self.index_path),
            ]
        )
        self.assertEqual(rc, 0)
        return json.loads(self.index_path.read_text())

    def test_build_indexes_python_and_typescript(self) -> None:
        data = self.build()
        files = data["files"]
        self.assertIn("src/core.py", files)
        self.assertIn("src/api.py", files)
        self.assertIn("src/widget.ts", files)
        # node_modules is skipped by default
        self.assertNotIn("node_modules/ignored.js", files)

    def test_python_symbols_extracted_via_ast(self) -> None:
        data = self.build()
        core = data["files"]["src/core.py"]
        names = {s["name"] for s in core["symbols"]}
        self.assertIn("AuthClient", names)
        self.assertIn("login", names)
        self.assertIn("hash_password", names)

    def test_typescript_symbols_extracted_via_regex(self) -> None:
        data = self.build()
        widget = data["files"]["src/widget.ts"]
        names = {s["name"] for s in widget["symbols"]}
        self.assertIn("Widget", names)
        self.assertIn("renderWidget", names)

    def test_imports_captured(self) -> None:
        data = self.build()
        api_imports = set(data["files"]["src/api.py"]["imports"])
        self.assertTrue(any("src.core" in imp or "core" in imp for imp in api_imports))
        ts_imports = set(data["files"]["src/widget.ts"]["imports"])
        self.assertTrue(any("core" in imp for imp in ts_imports))

    def test_in_degree_counts_references(self) -> None:
        data = self.build()
        core = data["files"]["src/core.py"]
        # src/api.py imports src.core -> core.py should have in_degree >= 1
        self.assertGreaterEqual(core["in_degree"], 1)

    def test_query_ranks_relevant_files_first(self) -> None:
        self.build()
        result = repo_map.query_index(
            self.index_path,
            "Implement user authentication flow with email login via AuthClient",
            top_n=10,
        )
        self.assertTrue(result, "expected non-empty results")
        top_paths = [r["path"] for r in result[:2]]
        self.assertIn("src/core.py", top_paths)

    def test_query_with_no_matches_returns_empty(self) -> None:
        self.build()
        result = repo_map.query_index(
            self.index_path, "xylophone quasar refrigerator", top_n=10
        )
        self.assertEqual(result, [])

    def test_stats_runs_without_error(self) -> None:
        self.build()
        rc = repo_map.main(["stats", "--map", str(self.index_path)])
        self.assertEqual(rc, 0)

    def test_tokenise_splits_camel_and_snake_case(self) -> None:
        tokens = repo_map.tokenise("AuthClient handles email_login flow")
        self.assertIn("auth", tokens)
        self.assertIn("client", tokens)
        self.assertIn("email", tokens)
        self.assertIn("login", tokens)
        self.assertNotIn("the", tokens)  # stopword


class ParserTests(unittest.TestCase):
    def test_python_parser_handles_syntax_error(self) -> None:
        src = "def foo(:\n  pass\n"
        symbols, imports = repo_map.parse_python(src)
        # Should fall back to regex and still find foo
        names = {s["name"] for s in symbols}
        self.assertIn("foo", names)

    def test_go_parser_captures_struct_and_func(self) -> None:
        src = (
            'package main\n'
            'import "fmt"\n'
            'type Bridge struct { Name string }\n'
            'func connectBridge() error { return nil }\n'
        )
        parser = repo_map.LANGUAGE_PARSERS["go"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Bridge", names)
        self.assertIn("connectBridge", names)
        self.assertIn("fmt", imports)

    def test_rust_parser_captures_struct_and_fn(self) -> None:
        src = (
            'use std::collections::HashMap;\n'
            'pub struct Config { pub name: String }\n'
            'pub fn load_config() -> Config { Config { name: String::new() } }\n'
        )
        parser = repo_map.LANGUAGE_PARSERS["rust"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Config", names)
        self.assertIn("load_config", names)


if __name__ == "__main__":
    unittest.main()
