"""BG0878: `config.py show` reports the value in force for keys whose default lived only in code.

`config-defaults.yaml` calls itself the single source of truth for skill defaults, yet a run of
dotted keys the scripts read carried their default only in the reading call, so `show --key`
refused them and `show --sources` listed nothing while a value was in force. Each such key is now
declared with the default its reader uses, and the review-round cap with the one `critic.py`
enforces. Driven through the shipped `config.py` CLI against a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/config-defaults.yaml
from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
DEFAULTS = SKILL / "templates" / "config-defaults.yaml"
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402

try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover - config is read through PyYAML
    HAVE_YAML = False


def _show(root: Path, *flags: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / "config.py"), "show", *flags,
                           "--root", str(root)], capture_output=True, text=True, check=False,
                          timeout=120)


def _constants(tree: ast.Module) -> dict:
    """Module-level `NAME = <literal>` assignments, so a default spelt as a named constant is
    judged by its value rather than skipped."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


_UNRESOLVED = object()


def _default_of(node: ast.expr, local: dict, md: dict):
    try:
        return ast.literal_eval(node)
    except ValueError:
        pass
    if isinstance(node, ast.Name):
        return local.get(node.id, _UNRESOLVED)
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
            and node.value.id == "sdlc_md":
        return md.get(node.attr, _UNRESOLVED)
    return _UNRESOLVED


def code_defaults() -> dict:
    """{dotted key: default} for every `config.get(root, "<a.b>", <default>)` in the shipped
    scripts whose default is a literal or a named literal constant."""
    md = _constants(ast.parse((SCRIPTS / "lib" / "sdlc_md.py").read_text(encoding="utf-8")))
    found: dict = {}
    for path in sorted(list(SCRIPTS.glob("*.py")) + list((SCRIPTS / "lib").glob("*.py"))):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        local = _constants(tree)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "config" and len(node.args) == 3):
                continue
            key = node.args[1]
            if not (isinstance(key, ast.Constant) and isinstance(key.value, str)
                    and "." in key.value):
                continue
            default = _default_of(node.args[2], local, md)
            if default is not _UNRESOLVED:
                found[key.value] = (default, f"{path.name}:{node.lineno}")
    return found


class ConfigCodeDefaultsTests(unittest.TestCase):
    """AC1-AC2."""

    def test_show_reports_the_value_in_force(self) -> None:
        """AC1. MUTANT: HEAD, where config-defaults.yaml leaves `review.max_rounds` out, so `show
        --key` exits 1 and `--sources` prints no line for it. The control: the project's own
        `coverage.unit` still reads `project`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text("coverage:\n  unit: 75\n",
                                                               encoding="utf-8")
            key = _show(root, "--key", "review.max_rounds")
            self.assertEqual(0, key.returncode, key.stderr)
            self.assertEqual("2", key.stdout.strip())
            self.assertEqual(str(critic.DEFAULT_REVIEW_CEILING), key.stdout.strip(),
                             "the declared default is not the cap critic.py enforces")
            src = _show(root, "--sources", "--key", "review.max_rounds")
            self.assertEqual(0, src.returncode, src.stderr)
            self.assertIn("default review.max_rounds = 2", src.stdout.splitlines())
            cov = _show(root, "--sources", "--key", "coverage.unit")
            self.assertEqual(["project coverage.unit = 75"], cov.stdout.splitlines())

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_every_key_read_is_declared_with_its_default(self) -> None:
        """AC2. MUTANTS: (1) delete `lessons.loop` from the defaults - undeclared; (2) declare
        `sprint.points_split_above: 5` - the value disagrees with the reader's 8."""
        defaults = yaml.safe_load(DEFAULTS.read_text(encoding="utf-8")) or {}
        found = code_defaults()
        # A floor against an empty scan, not a count to keep.
        self.assertGreaterEqual(len(found), 8, f"the scan found too few keys: {sorted(found)}")
        for key, (default, where) in sorted(found.items()):
            with self.subTest(key=key):
                cur = defaults
                for part in key.split("."):
                    self.assertTrue(isinstance(cur, dict) and part in cur,
                                    f"{key} ({where}) is not declared in config-defaults.yaml")
                    cur = cur[part]
                self.assertEqual((type(default), default), (type(cur), cur),
                                 f"{key}: config-defaults.yaml says {cur!r}, {where} uses {default!r}")


if __name__ == "__main__":
    unittest.main()
