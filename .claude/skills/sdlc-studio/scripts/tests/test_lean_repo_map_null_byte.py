"""BG0757: a source file the parser rejects with ValueError stays in the repo map.

Python 3.10's `ast.parse` raises ValueError, not SyntaxError, for source holding a null byte.
Both tests inject that ValueError so they fail the same way on every interpreter.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

repo_map = loader.load_script("repo_map")

_SCRIPT = Path(__file__).resolve().parent.parent / "repo_map.py"
_NULL_SOURCE = "import os\n\x00\ndef kept():\n    pass\n\nclass Kept:\n    pass\n"

# Runs the shipped script as __main__ with ast.parse raising ValueError on a null byte, the
# way 3.10 does, so the exit code is the one a consumer's CLI run would see.
_RUNNER = (
    "import ast, runpy, sys\n"
    "_real = ast.parse\n"
    "def _parse(source, *a, **k):\n"
    "    if '\\x00' in source:\n"
    "        raise ValueError('source code string cannot contain null bytes')\n"
    "    return _real(source, *a, **k)\n"
    "ast.parse = _parse\n"
    "script = sys.argv.pop(1)\n"
    "sys.argv[0] = script\n"
    "runpy.run_path(script, run_name='__main__')\n"
)


class NullByteTests(unittest.TestCase):
    def test_a_valueerror_from_the_parser_falls_back_to_the_regex_index(self) -> None:
        with unittest.mock.patch.object(
                repo_map.ast, "parse",
                side_effect=ValueError("source code string cannot contain null bytes")):
            symbols, imports = repo_map.parse_python(_NULL_SOURCE)
        self.assertEqual((symbols, imports), repo_map._parse_python_regex(_NULL_SOURCE))
        self.assertEqual([s["name"] for s in symbols], ["kept", "Kept"])
        self.assertEqual(imports, ["os"])

    def test_the_build_cli_exits_zero_over_a_null_byte_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="bg0757_") as tmp:
            root = Path(tmp)
            (root / "null.py").write_text(_NULL_SOURCE, encoding="utf-8")
            (root / "clean.py").write_text("def clean():\n    pass\n", encoding="utf-8")
            out = root / "map.json"
            proc = subprocess.run(
                [sys.executable, "-c", _RUNNER, str(_SCRIPT), "build",
                 "--root", str(root), "--out", str(out)],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("indexed 2 files", proc.stdout)
            files = json.loads(out.read_text(encoding="utf-8"))["files"]
            self.assertEqual(sorted(files), ["clean.py", "null.py"])
            self.assertEqual([s["name"] for s in files["null.py"]["symbols"]], ["kept", "Kept"])


if __name__ == "__main__":
    unittest.main()
