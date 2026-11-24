# test-census-subject: .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py
"""A test that swaps a module in `sys.modules` puts it back.

A bare `sys.modules["x"] = mod` inside a test method leaks the swap into every later test in
the process: one that loaded a stand-in `x` poisoned the next module that imported it, and the
failure read red only when the whole suite ran in one process. The scanner here reads test
sources for such an assignment and reports it by file and line; the sweep holds the skill's own
tests to it.

An assignment is restored when it sits in a `with patch.dict(sys.modules, ...)` block, in a
function decorated with `patch.dict(sys.modules, ...)`, in a function that registers an
`addCleanup`, in a `try` whose `finally` puts `sys.modules` back (or in that `finally`
itself), or when such a `try` follows it in the same block.
"""
from __future__ import annotations

import ast
import re
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
# A cheap pre-filter: a source with no `sys.modules[...] =` text is not parsed at all.
_MAYBE_SWAP = re.compile(r"sys\.modules\s*\[[^\n]*\]\s*=(?!=)")


def _is_sys_modules(node: ast.AST) -> bool:
    return ast.unparse(node) == "sys.modules"


def _assigns_module(node: ast.AST) -> bool:
    targets = getattr(node, "targets", [])
    return isinstance(node, (ast.Assign, ast.Delete)) and any(
        isinstance(t, ast.Subscript) and _is_sys_modules(t.value) for t in targets)


def _patches_modules(node: ast.AST) -> bool:
    """A `patch.dict(sys.modules, ...)` call anywhere under `node`."""
    return any(isinstance(c, ast.Call) and ast.unparse(c.func).endswith("patch.dict")
               and c.args and _is_sys_modules(c.args[0]) for c in ast.walk(node))


def _registers_cleanup(node: ast.AST) -> bool:
    return any(isinstance(c, ast.Call) and ast.unparse(c.func).endswith("addCleanup")
               for c in ast.walk(node))


def _puts_back(stmts: list[ast.stmt]) -> bool:
    """Statements that restore `sys.modules`: an assignment or `del` of an entry, or a
    `pop`/`update`/`setdefault` on it."""
    for stmt in stmts:
        for c in ast.walk(stmt):
            if _assigns_module(c):
                return True
            if isinstance(c, ast.Call) and ast.unparse(c.func) in (
                    "sys.modules.pop", "sys.modules.update", "sys.modules.setdefault"):
                return True
    return False


def _restored(node: ast.AST, parents: dict) -> bool:
    child, parent = node, parents.get(node)
    while parent is not None:
        if isinstance(parent, ast.With) and child in parent.body and any(
                _patches_modules(item) for item in parent.items):
            return True
        if isinstance(parent, ast.Try):
            if child in parent.body and _puts_back(parent.finalbody):
                return True
            if child in parent.finalbody:
                return True
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(_patches_modules(d) for d in parent.decorator_list):
                return True
            if _registers_cleanup(parent):
                return True
        block = next((getattr(parent, f) for f in ("body", "orelse", "finalbody")
                      if child in getattr(parent, f, [])), [])
        later = block[block.index(child) + 1:] if child in block else []
        if any(isinstance(s, ast.Try) and _puts_back(s.finalbody) for s in later):
            return True
        child, parent = parent, parents.get(parent)
    return False


def unrestored_swaps(source: str, filename: str = "<source>") -> list[dict]:
    """Each `sys.modules[...] = ...` in `source` that nothing restores, as
    `{"file", "line", "scope"}`; the scope is "method" inside a class's function and "module"
    elsewhere (an import-time registration)."""
    if not _MAYBE_SWAP.search(source):
        return []
    tree = ast.parse(source, filename=filename)
    parents: dict = {}
    pending = [tree]
    while pending:
        parent = pending.pop()
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
            pending.append(child)
    found = []
    for node in parents:
        if not (isinstance(node, ast.Assign) and _assigns_module(node)):
            continue
        if _restored(node, parents):
            continue
        chain, up = [], parents.get(node)
        while up is not None:
            chain.append(up)
            up = parents.get(up)
        in_function = any(isinstance(a, (ast.FunctionDef, ast.AsyncFunctionDef)) for a in chain)
        in_class = any(isinstance(a, ast.ClassDef) for a in chain)
        found.append({"file": filename, "line": node.lineno,
                      "scope": "method" if in_function and in_class else "module"})
    return sorted(found, key=lambda f: f["line"])


def sweep(directory: Path) -> tuple[list[str], int]:
    """The unrestored swaps made inside a class's methods, as `file:line`, and the count of
    the import-time registrations among the modules of `directory`."""
    methods, imports = [], 0
    for path in sorted(directory.glob("*.py")):
        for found in unrestored_swaps(path.read_text(encoding="utf-8"), path.name):
            if found["scope"] == "method":
                methods.append(f"{found['file']}:{found['line']}")
            else:
                imports += 1
    return methods, imports


class SysModulesRestoreTests(unittest.TestCase):
    SWAP = "sys.modules[\"widget\"] = mod"

    def test_an_unrestored_assignment_is_reported_by_file_and_line(self) -> None:
        """MUTANT: let the scan pass an assignment nothing restores."""
        src = ("import sys\n\nclass T:\n    def test_x(self):\n        mod = object()\n"
               f"        {self.SWAP}\n        self.assertTrue(mod)\n")
        self.assertEqual(unrestored_swaps(src, "test_demo.py"),
                         [{"file": "test_demo.py", "line": 6, "scope": "method"}])
        self.assertEqual(
            unrestored_swaps(f"import sys\nmod = 1\n{self.SWAP}\n", "test_load.py"),
            [{"file": "test_load.py", "line": 3, "scope": "module"}])

    def test_a_restored_assignment_is_not_reported(self) -> None:
        """MUTANT: refuse every assignment, restored or not."""
        cleanup = ("import sys\n\nclass T:\n    def test_x(self):\n        mod = object()\n"
                   f"        {self.SWAP}\n        self.addCleanup(sys.modules.pop, 'widget', None)\n")
        patched = ("import sys\n\nclass T:\n    def test_x(self):\n        mod = object()\n"
                   f"        with mock.patch.dict(sys.modules):\n            {self.SWAP}\n")
        decorated = ("import sys\n\nclass T:\n    @mock.patch.dict(sys.modules)\n"
                     f"    def test_x(self):\n        {self.SWAP}\n")
        finally_ = ("import sys\n\nclass T:\n    def test_x(self):\n        mod = object()\n"
                    f"        try:\n            {self.SWAP}\n        finally:\n"
                    "            sys.modules.pop('widget', None)\n")
        after = ("import sys\n\nclass T:\n    def test_x(self):\n"
                 f"        {self.SWAP}\n        try:\n            pass\n"
                 "        finally:\n            sys.modules.pop('widget', None)\n")
        deleted = finally_.replace("sys.modules.pop('widget', None)", "del sys.modules['widget']")
        in_finally = ("import sys\n\nclass T:\n    def test_x(self):\n        try:\n"
                      f"            pass\n        finally:\n            {self.SWAP}\n")
        for name, src in (("addCleanup", cleanup), ("patch.dict", patched),
                          ("decorator", decorated), ("finally", finally_),
                          ("try after", after), ("in finally", in_finally),
                          ("del in finally", deleted)):
            with self.subTest(name):
                self.assertEqual(unrestored_swaps(src), [])
        # Positive control: a finally that restores nothing, and a patch of another mapping,
        # leave the swap reported, so the clean results above are not the scan looking at nothing.
        weak = finally_.replace("sys.modules.pop('widget', None)", "print('done')")
        other = patched.replace("sys.modules)", "os.environ)")
        self.assertEqual([f["line"] for f in unrestored_swaps(weak)], [7])
        self.assertEqual([f["line"] for f in unrestored_swaps(other)], [7])

    def test_the_scope_separates_a_method_from_an_import_time_registration(self) -> None:
        """MUTANT: call every unrestored assignment a method's, or a function's, or a class's."""
        loader = f"import sys\n\ndef load():\n    {self.SWAP}\n"
        body = f"import sys\n\nclass T:\n    {self.SWAP}\n"
        nested = ("import sys\n\nclass T:\n    def test_x(self):\n        def inner():\n"
                  f"            {self.SWAP}\n")
        self.assertEqual([f["scope"] for f in unrestored_swaps(loader)], ["module"])
        self.assertEqual([f["scope"] for f in unrestored_swaps(body)], ["module"])
        self.assertEqual([f["scope"] for f in unrestored_swaps(nested)], ["method"])

    def test_the_sweep_reads_every_module_of_a_directory(self) -> None:
        """MUTANT: read no module, or drop a method's swap from the sweep's report."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_a.py").write_text(
                f"import sys\n\nclass T:\n    def test_x(self):\n        {self.SWAP}\n",
                encoding="utf-8")
            (Path(d) / "test_b.py").write_text(f"import sys\n{self.SWAP}\n", encoding="utf-8")
            self.assertEqual(sweep(Path(d)), (["test_a.py:5"], 1))

    def test_the_skill_s_tests_restore_every_module_they_swap(self) -> None:
        """MUTANT: skip a module of the tree, or count a method's swap as an import."""
        methods, imports = sweep(TESTS_DIR)
        print(f"advisory: {imports} import-time module registrations are not restored",
              file=sys.stderr)
        self.assertEqual(methods, [], "a test swaps a module in sys.modules and never puts it "
                         "back; restore it with mock.patch.dict(sys.modules) or addCleanup")


if __name__ == "__main__":
    unittest.main()
