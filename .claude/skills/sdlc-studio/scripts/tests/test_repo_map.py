"""Unit tests for repo_map.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
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

    def test_python_function_symbols_carry_complexity(self) -> None:
        # RFC0009 WS1: per-function cognitive + cyclomatic emitted into the map.
        src = "def f(a, b):\n    if a and b:\n        return 1\n    return 0\n"
        symbols, _ = repo_map.parse_python(src)
        fn = next(s for s in symbols if s["name"] == "f")
        self.assertEqual(fn["cognitive"], 2)   # if(1) + boolop(1)
        self.assertEqual(fn["cyclomatic"], 3)  # 1 + if + boolop branch

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


class MoreLanguageParserTests(unittest.TestCase):
    """Cover the regex parsers that the original suite skipped."""

    def test_java_parser_captures_class_and_imports(self) -> None:
        src = (
            "package com.example;\n"
            "import java.util.List;\n"
            "import static org.junit.Assert.assertEquals;\n"
            "public class BridgeService {\n"
            "    void run() {}\n"
            "}\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["java"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("BridgeService", names)
        self.assertIn("java.util.List", imports)
        self.assertIn("org.junit.Assert.assertEquals", imports)

    def test_kotlin_uses_java_patterns(self) -> None:
        # Kotlin is wired to the Java regex pair; the Java class/interface/enum
        # pattern recognises Kotlin's `class` and `interface` declarations.
        src = (
            "class Greeter {\n"
            "    fun hello() {}\n"
            "}\n"
            "interface Speaker\n"
        )
        symbols, _ = repo_map.LANGUAGE_PARSERS["kotlin"](src)
        names = {s["name"] for s in symbols}
        self.assertIn("Greeter", names)
        self.assertIn("Speaker", names)

    def test_csharp_parser_captures_class_and_using(self) -> None:
        src = (
            "using System.Collections.Generic;\n"
            "namespace App {\n"
            "    public class Repository {\n"
            "        public void Save() {}\n"
            "    }\n"
            "}\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["csharp"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Repository", names)
        self.assertIn("System.Collections.Generic", imports)

    def test_ruby_parser_captures_class_module_def(self) -> None:
        src = (
            "require 'json'\n"
            "require_relative 'helper'\n"
            "module Billing\n"
            "  class Invoice\n"
            "    def total\n"
            "    end\n"
            "  end\n"
            "end\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["ruby"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Billing", names)
        self.assertIn("Invoice", names)
        self.assertIn("total", names)
        self.assertIn("json", imports)
        self.assertIn("helper", imports)

    def test_php_parser_captures_class_and_function(self) -> None:
        src = (
            "<?php\n"
            "use App\\Models\\User;\n"
            "class Controller {\n"
            "}\n"
            "function handle() {}\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["php"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Controller", names)
        self.assertIn("handle", names)
        self.assertTrue(any("User" in imp for imp in imports))

    def test_swift_parser_captures_struct_and_func(self) -> None:
        src = (
            "import Foundation\n"
            "public struct Point {\n"
            "    func distance() -> Double { return 0 }\n"
            "}\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["swift"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("Point", names)
        self.assertIn("distance", names)
        self.assertIn("Foundation", imports)

    def test_javascript_uses_typescript_patterns(self) -> None:
        src = (
            "const handler = () => {};\n"
            "function process() {}\n"
            "const dep = require('./helper');\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["javascript"]
        symbols, imports = parser(src)
        names = {s["name"] for s in symbols}
        self.assertIn("handler", names)
        self.assertIn("process", names)
        self.assertIn("./helper", imports)

    def test_typescript_interface_and_type_symbols(self) -> None:
        src = (
            "export interface Config { name: string }\n"
            "export type Id = string;\n"
        )
        parser = repo_map.LANGUAGE_PARSERS["typescript"]
        symbols, _ = parser(src)
        kinds = {s["name"]: s["kind"] for s in symbols}
        self.assertEqual(kinds.get("Config"), "iface")
        self.assertEqual(kinds.get("Id"), "ty")

    def test_parse_with_regex_picks_first_truthy_group(self) -> None:
        # The require capture is the second alternation group; ensure the
        # parser still records it when the import group is non-empty.
        symbols, imports = repo_map.parse_with_regex(
            "const x = require('lodash');\n",
            repo_map._TS_SYMBOL_RE,
            repo_map._TS_IMPORT_RE,
        )
        self.assertEqual(imports, ["lodash"])
        self.assertEqual({s["name"] for s in symbols}, {"x"})

    def test_symbol_line_numbers_are_one_based(self) -> None:
        # Two declarations on consecutive lines with no blank-line gap, so the
        # leading-whitespace match cannot drift into a prior line.
        src = "export function first() {}\nexport function second() {}\n"
        symbols, _ = repo_map.parse_with_regex(
            src, repo_map._TS_SYMBOL_RE, repo_map._TS_IMPORT_RE
        )
        lines = {s["name"]: s["line"] for s in symbols}
        self.assertEqual(lines["first"], 1)
        self.assertEqual(lines["second"], 2)


class PythonParserDetailTests(unittest.TestCase):
    def test_async_function_recorded(self) -> None:
        symbols, _ = repo_map.parse_python("async def fetch():\n    pass\n")
        kinds = {s["name"]: s["kind"] for s in symbols}
        self.assertEqual(kinds.get("fetch"), "function")

    def test_import_from_module_recorded(self) -> None:
        _, imports = repo_map.parse_python("from pkg.sub import thing\n")
        self.assertIn("pkg.sub", imports)

    def test_relative_import_from_yields_empty_module(self) -> None:
        # `from . import x` has node.module == None; the code stores "".
        _, imports = repo_map.parse_python("from . import sibling\n")
        self.assertIn("", imports)

    def test_class_method_lines_distinct(self) -> None:
        src = "class A:\n    def one(self):\n        pass\n    def two(self):\n        pass\n"
        symbols, _ = repo_map.parse_python(src)
        lines = {s["name"]: s["line"] for s in symbols}
        self.assertEqual(lines["A"], 1)
        self.assertEqual(lines["one"], 2)
        self.assertEqual(lines["two"], 4)

    def test_regex_fallback_captures_imports(self) -> None:
        # Broken syntax forces the regex fallback path, which also reads imports.
        src = "import os\nfrom sys import argv\ndef broken(:\n  pass\n"
        symbols, imports = repo_map.parse_python(src)
        self.assertIn("broken", {s["name"] for s in symbols})
        self.assertIn("os", imports)
        self.assertIn("sys", imports)

    def test_only_functions_carry_complexity_keys(self) -> None:
        symbols, _ = repo_map.parse_python("class C:\n    pass\ndef f():\n    pass\n")
        cls = next(s for s in symbols if s["name"] == "C")
        fn = next(s for s in symbols if s["name"] == "f")
        self.assertNotIn("cognitive", cls)
        self.assertIn("cognitive", fn)
        self.assertIn("cyclomatic", fn)


class TokeniseTests(unittest.TestCase):
    def test_two_letter_words_dropped(self) -> None:
        # The word regex requires 3+ chars overall, and parts must be >=3.
        tokens = repo_map.tokenise("go to db")
        self.assertNotIn("go", tokens)
        self.assertNotIn("to", tokens)
        self.assertNotIn("db", tokens)

    def test_jargon_stopwords_removed(self) -> None:
        tokens = repo_map.tokenise("the test class function method page")
        for noise in ("the", "test", "class", "function", "method", "page"):
            self.assertNotIn(noise, tokens)

    def test_camel_split_keeps_meaningful_parts(self) -> None:
        tokens = repo_map.tokenise("getUserProfileData")
        # "user" is a stopword and should be removed even after the split.
        self.assertIn("get", tokens)
        self.assertIn("profile", tokens)
        self.assertIn("data", tokens)
        self.assertNotIn("user", tokens)

    def test_digits_retained_within_token(self) -> None:
        tokens = repo_map.tokenise("oauth2 handler")
        self.assertIn("oauth2", tokens)

    def test_empty_text_yields_empty_set(self) -> None:
        self.assertEqual(repo_map.tokenise("  !!  "), set())


class ScoreFileTests(unittest.TestCase):
    def _entry(self, **kw) -> "repo_map.FileEntry":
        return repo_map.FileEntry(
            language=kw.get("language", "python"),
            symbols=kw.get("symbols", []),
            imports=kw.get("imports", []),
            in_degree=kw.get("in_degree", 0),
        )

    def test_zero_match_scores_zero_despite_hub(self) -> None:
        entry = self._entry(in_degree=100)
        score, matched = repo_map.score_file("zzz/unrelated.py", entry, {"payments"})
        self.assertEqual(score, 0.0)
        self.assertEqual(matched, [])

    def test_path_token_match_weighted_two(self) -> None:
        entry = self._entry()
        score, matched = repo_map.score_file("src/billing.py", entry, {"billing"})
        self.assertEqual(score, 2.0)
        self.assertEqual(matched, ["billing"])

    def test_symbol_match_weighted_three(self) -> None:
        entry = self._entry(symbols=[{"name": "ChargeCard", "kind": "class", "line": 1}])
        score, matched = repo_map.score_file("x/zz.py", entry, {"charge"})
        self.assertEqual(score, 3.0)
        self.assertIn("charge", matched)

    def test_hub_bonus_added_only_after_a_match(self) -> None:
        # 1 symbol match (3.0) + in_degree 4 * 0.5 = 5.0
        entry = self._entry(
            symbols=[{"name": "billing", "kind": "function", "line": 1}],
            in_degree=4,
        )
        score, _ = repo_map.score_file("x/zz.py", entry, {"billing"})
        self.assertEqual(score, 5.0)

    def test_matched_tokens_returned_sorted_and_unique(self) -> None:
        entry = self._entry(
            symbols=[
                {"name": "betaThing", "kind": "function", "line": 1},
                {"name": "alphaThing", "kind": "function", "line": 2},
            ]
        )
        _, matched = repo_map.score_file("x/zz.py", entry, {"alpha", "beta", "thing"})
        self.assertEqual(matched, ["alpha", "beta", "thing"])


class QueryIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_query_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_map(self, files: dict) -> Path:
        path = self.tmp / "map.json"
        path.write_text(json.dumps({"version": 1, "files": files}))
        return path

    def test_invalid_json_raises_value_error(self) -> None:
        path = self.tmp / "broken.json"
        path.write_text("{ not json")
        with self.assertRaises(ValueError):
            repo_map.query_index(path, "anything matching", top_n=5)

    def test_empty_query_returns_empty_without_reading_files(self) -> None:
        path = self._write_map(
            {"a.py": {"language": "python", "symbols": [], "imports": [], "in_degree": 0}}
        )
        # All-stopword text tokenises to nothing.
        self.assertEqual(repo_map.query_index(path, "the and for", top_n=5), [])

    def test_results_truncated_to_top_n(self) -> None:
        files = {
            f"mod/payment_{i}.py": {
                "language": "python",
                "symbols": [{"name": "payment", "kind": "function", "line": 1}],
                "imports": [],
                "in_degree": 0,
            }
            for i in range(5)
        }
        path = self._write_map(files)
        results = repo_map.query_index(path, "payment processing", top_n=2)
        self.assertEqual(len(results), 2)

    def test_tie_break_is_alphabetical_and_deterministic(self) -> None:
        # All three files score identically; order must be by path ascending.
        files = {
            name: {
                "language": "python",
                "symbols": [{"name": "payment", "kind": "function", "line": 1}],
                "imports": [],
                "in_degree": 0,
            }
            for name in ("c.py", "a.py", "b.py")
        }
        path = self._write_map(files)
        first = [r["path"] for r in repo_map.query_index(path, "payment", top_n=10)]
        second = [r["path"] for r in repo_map.query_index(path, "payment", top_n=10)]
        self.assertEqual(first, ["a.py", "b.py", "c.py"])
        self.assertEqual(first, second)

    def test_higher_score_sorts_before_lower(self) -> None:
        files = {
            "weak.py": {
                "language": "python",
                "symbols": [],
                "imports": [],
                "in_degree": 0,
            },  # matches only on path token (2.0)
            "strong.py": {
                "language": "python",
                "symbols": [{"name": "weak", "kind": "function", "line": 1}],
                "imports": [],
                "in_degree": 0,
            },  # matches on symbol (3.0) and not path
        }
        path = self._write_map(files)
        results = repo_map.query_index(path, "weak", top_n=10)
        self.assertEqual(results[0]["path"], "strong.py")
        self.assertGreater(results[0]["score"], results[1]["score"])

    def test_result_score_is_rounded_two_dp(self) -> None:
        files = {
            "billing.py": {
                "language": "python",
                "symbols": [{"name": "billing", "kind": "function", "line": 1}],
                "imports": [],
                "in_degree": 3,
            }
        }
        path = self._write_map(files)
        result = repo_map.query_index(path, "billing", top_n=1)[0]
        # path(2) + symbol(3) + 3*0.5 = 6.5
        self.assertEqual(result["score"], 6.5)
        self.assertEqual(result["in_degree"], 3)


class WalkAndIgnoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_walk_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_root_dotdir_indexed_but_nested_dotdir_pruned(self) -> None:
        (self.tmp / ".claude").mkdir()
        (self.tmp / ".claude" / "top.py").write_text("def top():\n    pass\n")
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / ".cache").mkdir()
        (self.tmp / "src" / ".cache" / "buried.py").write_text("def buried():\n    pass\n")
        found = {
            str(p.relative_to(self.tmp))
            for p in repo_map.walk_source_files(self.tmp, repo_map.DEFAULT_IGNORES)
        }
        self.assertIn(".claude/top.py", found)
        self.assertNotIn("src/.cache/buried.py", found)

    def test_custom_ignore_dir_excluded(self) -> None:
        (self.tmp / "keep").mkdir()
        (self.tmp / "keep" / "a.py").write_text("def a():\n    pass\n")
        (self.tmp / "skipme").mkdir()
        (self.tmp / "skipme" / "b.py").write_text("def b():\n    pass\n")
        ignores = set(repo_map.DEFAULT_IGNORES) | {"skipme"}
        found = {
            str(p.relative_to(self.tmp))
            for p in repo_map.walk_source_files(self.tmp, ignores)
        }
        self.assertIn("keep/a.py", found)
        self.assertNotIn("skipme/b.py", found)

    def test_unsupported_extension_skipped(self) -> None:
        (self.tmp / "notes.md").write_text("# notes\n")
        (self.tmp / "data.json").write_text("{}\n")
        (self.tmp / "code.py").write_text("def x():\n    pass\n")
        found = {
            p.name for p in repo_map.walk_source_files(self.tmp, repo_map.DEFAULT_IGNORES)
        }
        self.assertEqual(found, {"code.py"})

    def test_extension_match_is_case_insensitive(self) -> None:
        (self.tmp / "Upper.PY").write_text("def x():\n    pass\n")
        found = {
            p.name for p in repo_map.walk_source_files(self.tmp, repo_map.DEFAULT_IGNORES)
        }
        self.assertIn("Upper.PY", found)


class InDegreeTests(unittest.TestCase):
    def test_self_import_not_counted(self) -> None:
        entries = {
            "core.py": repo_map.FileEntry(language="python", imports=["core"]),
        }
        repo_map.compute_in_degree(entries)
        self.assertEqual(entries["core.py"].in_degree, 0)

    def test_basename_resolution_across_files(self) -> None:
        entries = {
            "src/core.py": repo_map.FileEntry(language="python", imports=[]),
            "src/a.py": repo_map.FileEntry(language="python", imports=["core"]),
            "src/b.py": repo_map.FileEntry(language="python", imports=["core"]),
        }
        repo_map.compute_in_degree(entries)
        self.assertEqual(entries["src/core.py"].in_degree, 2)

    def test_dotted_python_import_does_not_resolve_to_basename(self) -> None:
        # Known limit: `splitext` treats `src.core` as stem `src`, so the
        # dotted module name does not resolve to core.py. Documenting the
        # current crude behaviour, not endorsing it.
        entries = {
            "src/core.py": repo_map.FileEntry(language="python", imports=[]),
            "src/a.py": repo_map.FileEntry(language="python", imports=["src.core"]),
        }
        repo_map.compute_in_degree(entries)
        self.assertEqual(entries["src/core.py"].in_degree, 0)

    def test_relative_ts_import_resolved(self) -> None:
        entries = {
            "src/core.ts": repo_map.FileEntry(language="typescript", imports=[]),
            "src/widget.ts": repo_map.FileEntry(
                language="typescript", imports=["./core"]
            ),
        }
        repo_map.compute_in_degree(entries)
        self.assertEqual(entries["src/core.ts"].in_degree, 1)

    def test_unresolved_import_changes_nothing(self) -> None:
        entries = {
            "a.py": repo_map.FileEntry(language="python", imports=["requests"]),
        }
        repo_map.compute_in_degree(entries)
        self.assertEqual(entries["a.py"].in_degree, 0)

    def test_empty_entries_is_safe(self) -> None:
        entries: dict = {}
        repo_map.compute_in_degree(entries)  # must not raise
        self.assertEqual(entries, {})


class BuildRobustnessTests(unittest.TestCase):
    """build_index must survive malformed sources and odd inputs."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_build_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_malformed_python_does_not_crash_build(self) -> None:
        (self.tmp / "broken.py").write_text("def broken(:\n  this is not python @@@\n")
        (self.tmp / "ok.py").write_text("def fine():\n    pass\n")
        entries = repo_map.build_index(self.tmp, repo_map.DEFAULT_IGNORES)
        self.assertIn("broken.py", entries)
        self.assertIn("ok.py", entries)
        # The regex fallback should still surface the broken function name.
        names = {s["name"] for s in entries["broken.py"].symbols}
        self.assertIn("broken", names)

    def test_binary_garbage_in_source_does_not_crash(self) -> None:
        # errors="ignore" decoding means undecodable bytes are dropped.
        (self.tmp / "junk.py").write_bytes(b"\xff\xfe\x00def maybe():\n    pass\n")
        entries = repo_map.build_index(self.tmp, repo_map.DEFAULT_IGNORES)
        self.assertIn("junk.py", entries)

    def test_empty_repo_yields_empty_index(self) -> None:
        entries = repo_map.build_index(self.tmp, repo_map.DEFAULT_IGNORES)
        self.assertEqual(entries, {})

    def test_paths_are_relative_to_root(self) -> None:
        (self.tmp / "pkg").mkdir()
        (self.tmp / "pkg" / "mod.py").write_text("def m():\n    pass\n")
        entries = repo_map.build_index(self.tmp, repo_map.DEFAULT_IGNORES)
        self.assertIn("pkg/mod.py", entries)
        self.assertTrue(all(not k.startswith("/") for k in entries))


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_cli_"))
        (self.tmp / "a.py").write_text(
            "def billing_run():\n    pass\n"
        )
        self.map_path = self.tmp / "map.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _build(self) -> None:
        rc = repo_map.main(
            ["build", "--root", str(self.tmp), "--out", str(self.map_path)]
        )
        self.assertEqual(rc, 0)

    def test_build_missing_root_returns_2(self) -> None:
        rc = repo_map.main(
            ["build", "--root", str(self.tmp / "nope"), "--out", str(self.map_path)]
        )
        self.assertEqual(rc, 2)
        self.assertFalse(self.map_path.exists())

    def test_query_missing_map_returns_2(self) -> None:
        rc = repo_map.main(
            ["query", "--story", "billing", "--map", str(self.tmp / "absent.json")]
        )
        self.assertEqual(rc, 2)

    def test_query_invalid_json_returns_2(self) -> None:
        self.map_path.write_text("{not valid")
        rc = repo_map.main(
            ["query", "--story", "billing", "--map", str(self.map_path)]
        )
        self.assertEqual(rc, 2)

    def test_query_story_from_file_path(self) -> None:
        self._build()
        story = self.tmp / "story.md"
        story.write_text("As a user I need billing_run to execute the billing.")
        rc = repo_map.main(
            [
                "query",
                "--story",
                str(story),
                "--map",
                str(self.map_path),
                "--format",
                "json",
            ]
        )
        self.assertEqual(rc, 0)

    def test_query_inline_text_when_path_absent(self) -> None:
        self._build()
        rc = repo_map.main(
            ["query", "--story", "billing", "--map", str(self.map_path)]
        )
        self.assertEqual(rc, 0)

    def test_stats_missing_map_returns_2(self) -> None:
        rc = repo_map.main(["stats", "--map", str(self.tmp / "absent.json")])
        self.assertEqual(rc, 2)

    def test_stats_invalid_json_returns_2(self) -> None:
        self.map_path.write_text("nope")
        rc = repo_map.main(["stats", "--map", str(self.map_path)])
        self.assertEqual(rc, 2)

    def test_stats_empty_index_returns_0(self) -> None:
        self.map_path.write_text(json.dumps({"version": 1, "files": {}}))
        rc = repo_map.main(["stats", "--map", str(self.map_path)])
        self.assertEqual(rc, 0)

    def test_build_writes_expected_json_shape(self) -> None:
        self._build()
        data = json.loads(self.map_path.read_text())
        self.assertEqual(data["version"], 1)
        self.assertIn("generated_at", data)
        self.assertIn("root", data)
        self.assertIn("a.py", data["files"])

    def test_no_subcommand_exits_nonzero(self) -> None:
        # argparse with required subparser raises SystemExit on no args.
        with self.assertRaises(SystemExit):
            repo_map.main([])


class RootAnchoringTests(unittest.TestCase):
    """BG0228: the map is written and read under the PROJECT ROOT, never beside the cwd.

    `build --root /proj` from another directory resolved its relative `--out` against the
    cwd, so the map landed in a stray `sdlc-studio/.local` tree next to wherever the agent
    happened to be, and `query`/`stats` then looked for it somewhere else again. Every test
    below runs from a cwd that is NOT the root: a test that chdir'd to the root would pass
    on a script that ignores `--root` completely and would prove nothing.
    """

    DEFAULT_MAP = Path("sdlc-studio") / ".local" / "repo-map.json"

    def setUp(self) -> None:
        self._prev_cwd = Path.cwd()
        self.tmp = Path(tempfile.mkdtemp(prefix="repo_map_root_"))
        self.root = self.tmp / "proj"
        # `sdlc-studio/stories` is one of the project-root markers discovery looks for.
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        (self.root / "a.py").write_text("def billing_run():\n    pass\n")
        self.inner = self.root / "scripts"          # a subdirectory inside the project
        self.inner.mkdir()
        self.outside = self.tmp / "elsewhere"       # a cwd with no project above it
        self.outside.mkdir()

    def tearDown(self) -> None:
        os.chdir(self._prev_cwd)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = repo_map.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_build_writes_the_map_under_the_named_root_not_the_cwd(self) -> None:
        os.chdir(self.outside)
        rc, _out, err = self._run(["build", "--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / self.DEFAULT_MAP).is_file(),
                        "the map did not land under the root that was named")
        self.assertEqual(sorted(p.name for p in self.outside.iterdir()), [],
                         "the map was written beside the cwd")

    def test_build_without_a_root_discovers_the_project_from_a_subdirectory(self) -> None:
        """The default `--root .` means 'work it out from here', not 'assume the cwd is
        the project' - running from `scripts/` must still index and write the project."""
        os.chdir(self.inner)
        rc, _out, err = self._run(["build"])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / self.DEFAULT_MAP).is_file(),
                        "the map did not land under the discovered project root")
        self.assertEqual(sorted(p.name for p in self.inner.iterdir()), [],
                         "the map was written beside the cwd")

    def test_build_prints_the_absolute_path_it_wrote(self) -> None:
        """The relative path it used to print could not distinguish the root from the cwd,
        which is what hid the misplaced write."""
        os.chdir(self.outside)
        _rc, out, _err = self._run(["build", "--root", str(self.root)])
        self.assertIn(str(self.root / self.DEFAULT_MAP), out)

    def test_query_reads_the_map_build_wrote_under_the_same_root(self) -> None:
        """Build and read from DIFFERENT working directories. Sharing one cwd would let
        two equally cwd-relative paths agree with each other and still both be wrong."""
        os.chdir(self.outside)
        self.assertEqual(self._run(["build", "--root", str(self.root)])[0], 0)
        os.chdir(self.inner)
        rc, _out, err = self._run(["--root", str(self.root), "query", "--story", "billing"])
        self.assertEqual(rc, 0, err)
        self.assertNotIn("repo map not found", err)

    def test_stats_reads_the_map_build_wrote_under_the_same_root(self) -> None:
        os.chdir(self.outside)
        self.assertEqual(self._run(["build", "--root", str(self.root)])[0], 0)
        os.chdir(self.inner)
        rc, _out, err = self._run(["--root", str(self.root), "stats"])
        self.assertEqual(rc, 0, err)
        self.assertNotIn("repo map not found", err)

    def test_an_absolute_out_is_honoured_verbatim(self) -> None:
        """Anchoring must not capture a path the caller chose deliberately."""
        os.chdir(self.outside)
        out_path = self.tmp / "chosen.json"
        rc, _out, err = self._run(["build", "--root", str(self.root), "--out", str(out_path)])
        self.assertEqual(rc, 0, err)
        self.assertTrue(out_path.is_file(), "an absolute --out was re-anchored under the root")

    def test_a_named_root_is_not_re_pointed_by_discovery(self) -> None:
        """Discovery widens the default `.` only. A root the caller NAMED is where the map
        goes, even with a bigger project above it - silently retargeting it would be the
        same lie in the other direction."""
        os.chdir(self.outside)
        rc, _out, err = self._run(["build", "--root", str(self.inner)])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.inner / self.DEFAULT_MAP).is_file(),
                        "the named root was overridden by discovery")
        self.assertFalse((self.root / "sdlc-studio" / ".local").exists())

    def test_discovery_does_not_escape_a_cwd_with_no_project_above_it(self) -> None:
        """With no project root anywhere above, the cwd is the honest answer - discovery
        must not walk to `/` and index something unrelated."""
        os.chdir(self.outside)
        rc, _out, err = self._run(["build"])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.outside / self.DEFAULT_MAP).is_file())
        self.assertFalse((self.root / "sdlc-studio" / ".local").exists())


if __name__ == "__main__":
    unittest.main()
