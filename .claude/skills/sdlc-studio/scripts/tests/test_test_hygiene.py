# test-census-subject: .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py
"""A test that swaps a module in `sys.modules` puts it back.

A bare `sys.modules["x"] = mod` inside a test method leaks the swap into every later test in
the process: one that loaded a stand-in `x` poisoned the next module that imported it, and the
failure read red only when the whole suite ran in one process. The scanner here reads test
sources for such an assignment and reports it by file and line; the sweep holds the skill's own
tests to it.

An assignment is restored when it sits in a `with patch.dict(sys.modules, ...)` block or in a
function decorated with `patch.dict(sys.modules, ...)`; when its function registers an
`addCleanup` that puts the entry it set back (the `stop` of a `patch.dict(sys.modules, ...)`
the function binds and starts before it, or a `pop`, `__setitem__` or `__delitem__` of that key
on `sys.modules`, registered itself or called from a lambda); when it sits in a `try` whose `finally` puts that entry back
(by assigning, deleting, popping, `__setitem__` or `__delitem__` of the same key) or in that
`finally` itself; or when such a `try` follows it in the same block. A cleanup or `finally`
that puts back another entry, or none, leaves it reported.
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
#: The calls on `sys.modules` that put one entry back, the entry's key their first argument.
_RESTORERS = ("sys.modules.pop", "sys.modules.__setitem__", "sys.modules.__delitem__")


def _is_sys_modules(node: ast.AST) -> bool:
    return ast.unparse(node) == "sys.modules"


def _keys(node: ast.AST) -> list[str]:
    """The keys, as source text, of the `sys.modules` entries an assignment or `del` names."""
    return [ast.unparse(t.slice) for t in getattr(node, "targets", [])
            if isinstance(t, ast.Subscript) and _is_sys_modules(t.value)]


def _patches_modules(node: ast.AST) -> bool:
    """A `patch.dict(sys.modules, ...)` call anywhere under `node`."""
    return any(isinstance(c, ast.Call) and ast.unparse(c.func).endswith("patch.dict")
               and c.args and _is_sys_modules(c.args[0]) for c in ast.walk(node))


def _puts_back(nodes: list[ast.AST], key: str) -> bool:
    """Code under `nodes` that puts the entry `key` of `sys.modules` back: an assignment or
    `del` of that entry, or a `pop`, `__setitem__` or `__delitem__` call given that key."""
    for node in nodes:
        for c in ast.walk(node):
            if isinstance(c, (ast.Assign, ast.Delete)) and key in _keys(c):
                return True
            if (isinstance(c, ast.Call) and ast.unparse(c.func) in _RESTORERS and c.args
                    and ast.unparse(c.args[0]) == key):
                return True
    return False


def _at(node: ast.AST) -> tuple[int, int]:
    return node.lineno, node.col_offset


def _started_before(function: ast.AST, owner: str, swap: ast.AST) -> bool:
    """`owner` holds a `patch.dict(sys.modules, ...)` in `function`, started before `swap`
    (earlier in the source, so on the swap's own line only to the left of it)."""
    held = any(isinstance(a, ast.Assign) and _patches_modules(a.value)
               and owner in [ast.unparse(t) for t in a.targets] for a in ast.walk(function))
    return held and any(isinstance(c, ast.Call) and ast.unparse(c.func) == f"{owner}.start"
                        and _at(c) < _at(swap) for c in ast.walk(function))


def _cleanup_restores(function: ast.AST, key: str, swap: ast.AST) -> bool:
    """`function` registers an `addCleanup` that puts the entry `key` back for `swap`, an
    assignment to `sys.modules`. A cleanup runs `callback(*args)`, so it restores what that call would; a
    patch's `stop` restores the entry when the patch was started before the swap."""
    for call in ast.walk(function):
        if not (isinstance(call, ast.Call) and ast.unparse(call.func).endswith("addCleanup")
                and call.args):
            continue
        callback = call.args[0]
        if _puts_back([ast.Call(func=callback, args=call.args[1:], keywords=[])], key):
            return True
        if (isinstance(callback, ast.Attribute) and callback.attr == "stop"
                and _started_before(function, ast.unparse(callback.value), swap)):
            return True
    return False


def _restored(node: ast.AST, key: str, parents: dict) -> bool:
    child, parent = node, parents.get(node)
    while parent is not None:
        if isinstance(parent, ast.With) and child in parent.body and any(
                _patches_modules(item) for item in parent.items):
            return True
        if isinstance(parent, ast.Try):
            if child in parent.body and _puts_back(parent.finalbody, key):
                return True
            if child in parent.finalbody:
                return True
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(_patches_modules(d) for d in parent.decorator_list):
                return True
            if _cleanup_restores(parent, key, node):
                return True
        block = next((getattr(parent, f) for f in ("body", "orelse", "finalbody")
                      if child in getattr(parent, f, [])), [])
        later = block[block.index(child) + 1:] if child in block else []
        if any(isinstance(s, ast.Try) and _puts_back(s.finalbody, key) for s in later):
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
        # A node setting no entry has no key, so `all` passes it over as it does a restored one.
        if not isinstance(node, ast.Assign) or all(
                _restored(node, key, parents) for key in _keys(node)):
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


def _method(*lines: str) -> str:
    """A test method's source holding `lines`, the first of them at line 5."""
    return "import sys\n\nclass T:\n    def test_x(self):\n" + "".join(
        f"        {line}\n" for line in lines)


_SWAP = "sys.modules[\"widget\"] = mod"
_STARTED = ("swap = mock.patch.dict(sys.modules)", "swap.start()", "self.addCleanup(swap.stop)")


class SysModulesRestoreTests(unittest.TestCase):
    SWAP = _SWAP
    #: A cleanup that puts the swapped entry back: the swap is not reported.
    RESTORING_CLEANUPS = (
        ("stopped patch", _method(*_STARTED, _SWAP)),
        ("started on the swap's line", _method(_STARTED[0], f"{_STARTED[1]}; {_SWAP}",
                                                _STARTED[2])),
        ("stopped patch on self", _method(*(s.replace("swap", "self.swap") for s in _STARTED),
                                          _SWAP)),
        ("lambda", _method(_SWAP, "self.addCleanup(lambda: sys.modules.__setitem__('widget', "
                                  "prior) if prior else sys.modules.pop('widget', None))")),
        ("delitem", _method(_SWAP, "self.addCleanup(sys.modules.__delitem__, 'widget')")),
        ("setitem", _method(_SWAP, "self.addCleanup(sys.modules.__setitem__, 'widget', prior)")),
        ("both entries", _method("sys.modules['gadget'] = " + _SWAP,
                                 "self.addCleanup(sys.modules.pop, 'widget', None)",
                                 "self.addCleanup(sys.modules.pop, 'gadget', None)")),
    )
    #: A cleanup that leaves the swapped entry in place: the swap is still reported.
    IDLE_CLEANUPS = (
        ("pops another entry", _method(_SWAP, "self.addCleanup(sys.modules.pop, 'gadget', None)")),
        ("lambda pops another", _method(_SWAP,
                                        "self.addCleanup(lambda: sys.modules.pop('gadget'))")),
        ("prints", _method(_SWAP, "self.addCleanup(print, sys.modules)")),
        ("no callback", _method(_SWAP, "self.addCleanup()")),
        ("never registered", _method(_SWAP, "undo = partial(sys.modules.pop, 'widget', None)")),
        ("starts the patch again", _method(_STARTED[0], _STARTED[1],
                                           "self.addCleanup(swap.start)", _SWAP)),
        ("stops a patch of another mapping",
         _method(*(s.replace("sys.modules)", "os.environ)") for s in _STARTED), _SWAP)),
        ("patch started after the swap", _method(_SWAP, *_STARTED)),
        ("started after on the swap's line", _method(_STARTED[0], f"{_SWAP}; {_STARTED[1]}",
                                                     _STARTED[2])),
        ("patch never started", _method(_STARTED[0], "worker.start()", _STARTED[2], _SWAP)),
        ("stops another patcher", _method(_STARTED[0], _STARTED[1],
                                          "env = mock.patch.dict(os.environ)", "env.start()",
                                          "self.addCleanup(env.stop)", _SWAP)),
        ("one of two entries", _method("sys.modules['gadget'] = " + _SWAP,
                                       "self.addCleanup(sys.modules.pop, 'widget', None)")),
    )

    def test_an_unrestored_assignment_is_reported_by_file_and_line(self) -> None:
        """MUTANT: let the scan pass an assignment nothing restores."""
        src = ("import sys\n\nclass T:\n    def test_x(self):\n        mod = object()\n"
               f"        {self.SWAP}\n        self.assertTrue(mod)\n")
        self.assertEqual(unrestored_swaps(src, "test_demo.py"),
                         [{"file": "test_demo.py", "line": 6, "scope": "method"}])
        self.assertEqual(
            unrestored_swaps(f"import sys\nmod = 1\n{self.SWAP}\n", "test_load.py"),
            [{"file": "test_load.py", "line": 3, "scope": "module"}])
        # A cleanup is not a restore by being there: one that puts back an attribute, as a
        # test patching the swapped module's function does, leaves the module itself swapped.
        unrelated = src.replace("        self.assertTrue(mod)\n",
                                "        self.addCleanup(setattr, mod, 'run', None)\n")
        self.assertEqual([f["line"] for f in unrestored_swaps(unrelated)], [6])

    def test_the_pre_filter_reads_a_key_in_any_spelling(self) -> None:
        """MUTANT: let the cheap text filter admit only one spelling of the key, so a source
        whose only swap spells it another way is never parsed."""
        for key in ("'widget'", '"widget"', "spec.name", "name", " 'widget' "):
            with self.subTest(key):
                src = ("import sys\n\nclass T:\n    def test_x(self):\n"
                       f"        sys.modules[{key}] = object()\n")
                self.assertEqual([f["line"] for f in unrestored_swaps(src)], [5])

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
        reassigned = finally_.replace("sys.modules.pop('widget', None)",
                                      "sys.modules['widget'] = prior")
        for name, src in (("addCleanup", cleanup), ("patch.dict", patched),
                          ("decorator", decorated), ("finally", finally_),
                          ("try after", after), ("in finally", in_finally),
                          ("del in finally", deleted), ("reassigned in finally", reassigned),
                          ("a del is no swap", f"del sys.modules['gadget']\n{patched}"),
                          *self.RESTORING_CLEANUPS):
            with self.subTest(name):
                self.assertEqual(unrestored_swaps(src), [])
        # Positive control: a finally that restores nothing, and a patch of another mapping,
        # leave the swap reported, so the clean results above are not the scan looking at nothing.
        weak = finally_.replace("sys.modules.pop('widget', None)", "print('done')")
        other = patched.replace("sys.modules)", "os.environ)")
        self.assertEqual([f["line"] for f in unrestored_swaps(weak)], [7])
        self.assertEqual([f["line"] for f in unrestored_swaps(other)], [7])
        # A restore of another entry, or one that leaves an entry present in place, restores
        # nothing of this swap, and a cleanup restoring none leaves it reported at its line.
        for name, src in (
                ("finally pops another", finally_.replace("pop('widget'", "pop('gadget'")),
                ("later finally pops another", after.replace("pop('widget'", "pop('gadget'")),
                ("finally deletes another", deleted.replace("['widget']", "['gadget']")),
                ("finally setdefault", finally_.replace("pop(", "setdefault(")),
                ("finally update", finally_.replace("pop('widget', None)", "update(saved)")),
                ("finally pops no key", finally_.replace("pop('widget', None)", "pop()")),
                *self.IDLE_CLEANUPS):
            with self.subTest(name):
                line = next(n for n, text in enumerate(src.splitlines(), 1) if _SWAP in text)
                self.assertEqual([f["line"] for f in unrestored_swaps(src)], [line])

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
                         "back; start a mock.patch.dict(sys.modules) "
                         "before the swap and stop it on cleanup")


if __name__ == "__main__":
    unittest.main()
