"""Unit tests for ledger.py (RED first - the script does not exist yet)."""
from __future__ import annotations

import ast
import contextlib
import importlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "ledger.py"


def _load():
    spec = importlib.util.spec_from_file_location("ledger", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ledger"] = mod
    spec.loader.exec_module(mod)
    return mod


class AppendTests(unittest.TestCase):
    def test_creates_and_appends(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _load().append_decision(root, "CR0020", "drop PL files", "evidence 0.27%")
            f = root / "sdlc-studio" / "decisions" / "CR0020.md"
            self.assertTrue(f.exists())
            text = f.read_text(encoding="utf-8")
            self.assertIn("drop PL files", text)
            self.assertIn("evidence 0.27%", text)
            self.assertIn("Decision", text)  # table header present

    def test_append_only_preserves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "first", "r1")
            mod.append_decision(root, "CR0020", "second", "r2")
            mod.append_decision(root, "CR0020", "third", "r3")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual([r["decision"] for r in rows], ["first", "second", "third"])

    def test_pipe_and_newline_do_not_drop_the_row(self) -> None:
        # A decision containing a table-breaking pipe or newline must still
        # round-trip as exactly one ruling (no silent data loss). Guards _clean.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "use A | B | C", "line1\nline2")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual(len(rows), 1)
            self.assertNotIn("|", rows[0]["decision"])
            self.assertNotIn("\n", rows[0]["rationale"])


class ReadTests(unittest.TestCase):
    def test_reads_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            mod.append_decision(root, "CR0020", "dec", "rat")
            rows = mod.read_ledger(root, "CR0020")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["decision"], "dec")
            self.assertEqual(rows[0]["rationale"], "rat")
            self.assertIn("at", rows[0])

    def test_missing_ledger_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(_load().read_ledger(Path(d), "CRXXXX"), [])


class CliTests(unittest.TestCase):
    def test_record_then_show(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            mod = _load()
            rc = mod.main(["record", "--tranche", "CR0020", "--decision", "d",
                           "--rationale", "r", "--root", str(root)])
            self.assertEqual(rc, 0)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc2 = mod.main(["show", "--tranche", "CR0020", "--root", str(root)])
            self.assertEqual(rc2, 0)
            self.assertIn("d", buf.getvalue())


SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _ff():
    """The shared fields-file loader, imported the way every consumer imports it."""
    import file_finding  # noqa: PLC0415 - deferred, as the consumers themselves defer it
    return file_finding


#: The `.get(...) or ""` guards on a fields-file value that this repository still carries, and
#: the reason each is tolerated. The sweep below refuses anything NOT on this list, so the list
#: is a debt register rather than an exemption: adding a row is a deliberate act with a sentence
#: attached, which is what turns the enumeration into a boundary.
#:
#: Both survivors sit outside the declared surface of the unit that built this check, and both
#: read a key the shared prose rule does not reach: `lessons.py` re-tests presence on a dict the
#: loader has already type-checked (redundant, not wrong), and `sprint.py` reads `goal` straight
#: off `load_fields_file`, which by design still accepts typed values.
KNOWN_OR_EMPTY_GUARDS: frozenset = frozenset({
    ("lessons.py", "fields", "k"),
    ("sprint.py", "from_file", "goal"),
})

#: The two names a fields-file document arrives under. A guard is in scope only when its
#: receiver is one of these loaders' results.
_FIELDS_FILE_LOADERS = ("load_fields_file", "resolve_prose_fields")


def _is_loader_call(node) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
    return name in _FIELDS_FILE_LOADERS


def _fields_file_names(tree: ast.AST) -> set:
    """Every local name a fields-file document is bound to in this module.

    MODULE-scoped on purpose, and this is the fields-file SCOPING the sweep turns on. The dict
    travels out of the function that loaded it under the same name - the filer's own
    `file_finding(root, type_, title, fields)` takes it as `fields` - so a function-scoped read
    would exempt exactly the call sites this check exists for. A `{**doc, **flags}` merge
    carries the taint forward, because the merged dict still holds the document's values.
    """
    names: set = set()
    changed = True
    while changed:                              # a merge can name a dict named by a later merge
        changed = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            value = node.value
            tainted = _is_loader_call(value)
            if not tainted and isinstance(value, ast.Dict):
                tainted = any(k is None and isinstance(v, ast.Name) and v.id in names
                              for k, v in zip(value.keys, value.values))
            if tainted:
                for t in targets:
                    if t not in names:
                        names.add(t)
                        changed = True
    return names


def or_empty_guards(source: str, module: str) -> list:
    """`[(module, receiver, key)]` - every `.get(...) or ""` applied to a fields-file value.

    The shape refused: `or ""` tests TRUTH, so a `false`, a `0` and an empty string all read as
    a key the document never carried, and the writer then reports a field missing while naming
    one the file plainly contains. `file_finding.prose_value` is the presence-tested
    replacement.

    SCOPED to fields-file receivers, and the scoping is the half that makes the check usable: a
    sweep that refused every `or ""` in the tree would refuse this repository, which carries
    hundreds of them on ledger rows, run state and argparse values that never came from a
    document.
    """
    found = []
    tree = ast.parse(source)
    names = _fields_file_names(tree)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or)
                and len(node.values) == 2):
            continue
        left, right = node.values
        if not (isinstance(right, ast.Constant) and right.value == ""):
            continue
        if not (isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute)
                and left.func.attr == "get" and left.args):
            continue
        receiver = left.func.value
        if isinstance(receiver, ast.Name) and receiver.id in names:
            who = receiver.id
        elif _is_loader_call(receiver):
            who = "<loader call>"
        else:
            continue                            # not a fields-file value: out of scope
        arg = left.args[0]
        key = arg.value if isinstance(arg, ast.Constant) else ast.unparse(arg)
        found.append((module, who, key))
    return found


class FieldsFileTypeTests(unittest.TestCase):
    """The fields-file type rule and the boundary that keeps it from being a fixed list.

    MUTANTS, one per criterion and stated before the tests were written: delete the type check
    from `resolve_prose_fields`; hoist that same check into `load_fields_file`, where it sees
    typed keys; bypass the shared loader at each of the five commands' call sites; narrow the
    sweep's predicate so a fields-file guard is not matched; drop the fields-file scoping from
    the sweep so every `or ""` in the tree is refused.
    """

    def test_a_non_string_prose_field_is_refused_naming_it(self) -> None:
        """AC1. A prose key carrying a non-string is REFUSED, and the refusal names the field.

        MUTANT: delete the type check from `resolve_prose_fields`. Without it a `false` reaches
        `_clean` and raises `AttributeError: 'bool' object has no attribute 'replace'` with a
        traceback - measured on `ledger.py record` before the fix - which is neither a refusal
        nor a name.
        """
        ff = _ff()
        for value in (False, 0, 5, ["a", "b"]):
            with tempfile.TemporaryDirectory() as d:
                doc = Path(d) / "fields.json"
                doc.write_text(json.dumps({"decision": "a ruling", "rationale": value}),
                               encoding="utf-8")
                with self.assertRaises(ValueError) as caught:
                    ff.resolve_prose_fields(str(doc), {}, allowed=("decision", "rationale"))
                message = str(caught.exception)
                self.assertIn("rationale", message)
                self.assertIn(type(value).__name__, message)
                # The field it does NOT name: a refusal that lists every key teaches nobody
                # which one to fix.
                self.assertNotIn("`decision`", message)

    def test_a_well_formed_fields_file_is_still_accepted(self) -> None:
        """AC2. Prose strings beside TYPED non-strings: accepted, and the values survive.

        MUTANT: hoist the refusal out of `resolve_prose_fields` into `load_fields_file`. The
        loader is the one three other writers pass a numeric `line` through, so a rule applied
        there refuses `points`, `acs`, `verify` and `line` while satisfying nothing AC1 asks
        for.
        """
        ff = _ff()
        typed = {"title": "a title", "summary": "a summary", "points": 3,
                 "acs": ["one", "two"], "verify": ["pytest a.py::T::t", "manual"]}
        with tempfile.TemporaryDirectory() as d:
            doc = Path(d) / "fields.json"
            doc.write_text(json.dumps(typed), encoding="utf-8")
            out = ff.load_fields_file(str(doc))
            self.assertEqual(3, out["points"])
            self.assertEqual(["one", "two"], out["acs"])
            self.assertEqual(["pytest a.py::T::t", "manual"], out["verify"])
            # ...and through the shared resolver, with the typed keys declared as metadata.
            resolved = ff.resolve_prose_fields(
                str(doc), {}, allowed=tuple(typed), metadata_keys=ff.FIELDS_FILE_TYPED_KEYS)
            self.assertEqual(3, resolved["points"])
            self.assertEqual(["one", "two"], resolved["acs"])
            # The numeric `line` the three writers outside this surface pass through the loader.
            other = Path(d) / "line.json"
            other.write_text(json.dumps({"file": "a.py", "line": 0, "reason": "why"}),
                             encoding="utf-8")
            self.assertEqual(
                0, ff.load_fields_file(str(other),
                                       allowed=("file", "line", "reason", "author"))["line"])

    def test_the_five_shipped_commands_refuse_by_name_and_never_traceback(self) -> None:
        """AC3. Each of the five modules' COMMANDS, driven as a subprocess.

        MUTANT (one per module): bypass the shared loader and read the JSON directly at that
        command's call site. The refusal asserted here is the LOADER'S, so a command that stops
        consulting it fails this test whatever else it prints - `decisions.py` and `handoff.py`
        both refuse a boolean today for the wrong reason ("no rationale", "no title"), which is
        a refusal that names a key the document carries.
        """
        import subprocess  # noqa: PLC0415 - the shipped entry point, not the library behind it
        scripts = Path(__file__).resolve().parent.parent
        cases = [
            ("ledger.py", "rationale", {"decision": "a ruling", "rationale": False},
             ["record", "--tranche", "CR0020"]),
            ("decisions.py", "rationale", {"decision": "a ruling", "rationale": False},
             ["add"]),
            ("handoff.py", "title", {"title": 0}, ["generate", "--dry-run"]),
            ("validate.py", "reason", {"reason": []}, ["warning-ratchet", "--stamp"]),
            ("file_finding.py", "impact",
             {"title": "t", "summary": "s", "severity": "Medium", "steps": "1. a", "fix": "f",
              "impact": False, "affects": "scripts/a.py", "points": 3},
             ["file", "--type", "bug", "--dry-run"]),
        ]
        for module, field, doc, argv in cases:
            with self.subTest(module=module), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio").mkdir()
                spec = root / "fields.json"
                spec.write_text(json.dumps(doc), encoding="utf-8")
                r = subprocess.run(
                    [sys.executable, str(scripts / module), *argv,
                     "--fields-file", str(spec), "--root", str(root)],
                    capture_output=True, text=True, timeout=300, check=False)
                output = r.stdout + r.stderr
                self.assertNotEqual(0, r.returncode, output)
                self.assertNotIn("Traceback", output)
                self.assertIn(f"`{field}`", output)
                self.assertIn("not text", output)
        # THE POSITIVE CONTROL, one per command and in-process so the refusal is not the only
        # thing these paths are known to do. A rule that refuses every document satisfies the
        # rows above and takes the recommended input path out of service.
        well_formed = [
            ("ledger", 0, {"decision": "a ruling", "rationale": "why it was taken"},
             ["record", "--tranche", "CR0020"]),
            ("decisions", 0, {"decision": "a ruling", "rationale": "why it was taken"}, ["add"]),
            ("handoff", 2, {"title": "a handoff"}, ["generate", "--dry-run"]),
            ("validate", 0, {"reason": "predates the ratchet"},
             ["warning-ratchet", "--stamp"]),
            ("file_finding", 0,
             {"title": "t", "summary": "a summary", "severity": "Medium",
              "steps": "1. run it", "fix": "repair it", "impact": "an impact",
              "affects": "src/a.py", "points": 3, "acs": ["it behaves"],
              "verify": ["manual"], "parent": "", "lens": "", "audit_run": "",
              # The two attribution fields that are read only once a run RESOLVES, so the
              # fixture below seeds the series the filer checks them against.
              "mutation_run": "RUN-TEST01"},
             ["file", "--type", "bug", "--dry-run"]),
        ]
        for module, expected, doc, argv in well_formed:
            with self.subTest(control=module), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio").mkdir()
                (root / "sdlc-studio" / ".local").mkdir()
                (root / "sdlc-studio" / ".local" / "mutation-series.jsonl").write_text(
                    json.dumps({"run_id": "RUN-TEST01", "targets": ["src/a.py"]}) + "\n",
                    encoding="utf-8")
                (root / "src").mkdir()
                (root / "src" / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
                spec = root / "fields.json"
                spec.write_text(json.dumps(doc), encoding="utf-8")
                mod = importlib.import_module(module)
                out, err = io.StringIO(), io.StringIO()
                with redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = mod.main([*argv, "--fields-file", str(spec), "--root", str(root)])
                output = out.getvalue() + err.getvalue()
                self.assertNotIn("not text", output)
                self.assertEqual(expected, rc, output)
                if module == "handoff":     # the one refusal that is about something else
                    self.assertIn("no batch to hand over", output)

    def test_a_new_or_empty_guard_is_refused_by_the_repository_check(self) -> None:
        """AC4. A new `.get(...) or ""` on a fields-file consumer is REFUSED by the sweep.

        MUTANT: narrow the sweep's predicate so a guard on a fields-file path is not matched -
        drop the merged-dict propagation, or require the receiver to be the loader call itself.
        Either way the injected guard below goes unseen and the live tree reads clean.
        """
        injected = (
            "import file_finding\n"
            "def cmd_new(args):\n"
            "    doc = file_finding.load_fields_file(args.fields_file)\n"
            "    fields = {**doc, **{}}\n"
            "    note = str(fields.get('note') or '').strip()\n"
            "    return note\n")
        self.assertEqual([("new_writer.py", "fields", "note")],
                         or_empty_guards(injected, "new_writer.py"))
        # ...and the same shape written directly against the loader's result.
        direct = ("import file_finding\n"
                  "def cmd(args):\n"
                  "    return (file_finding.resolve_prose_fields(\n"
                  "        args.fields_file, {}, allowed=('note',)).get('note') or '').strip()\n")
        self.assertEqual([("direct.py", "<loader call>", "note")],
                         or_empty_guards(direct, "direct.py"))
        # THE BOUNDARY, over the live tree: nothing but the registered debt above.
        scripts = Path(__file__).resolve().parent.parent
        live = []
        for path in sorted(scripts.rglob("*.py")):
            live += or_empty_guards(path.read_text(encoding="utf-8"),
                                    path.relative_to(scripts).as_posix())
        self.assertEqual(KNOWN_OR_EMPTY_GUARDS, set(live),
                         "a fields-file consumer gained (or lost) an `or \"\"` guard - use "
                         "`file_finding.prose_value(fields, key)`, which tests presence, or "
                         "register the instance in KNOWN_OR_EMPTY_GUARDS with its reason")

    def test_an_unrelated_or_empty_guard_is_left_alone(self) -> None:
        """AC5. An `or ""` that never touched a fields-file document PASSES.

        MUTANT: drop the fields-file scoping from the sweep's predicate. That satisfies AC4 and
        refuses the repository: measured on this tree, 187 `.get(...) or ""` guards stand
        outside `tests/` (201 counting them) and the sweep matches 2 - `sprint.py` alone carries
        35, and `decisions.py` reads its own ledger rows that way.
        """
        unrelated = (
            "def render(rec, args):\n"
            "    kind = str(rec.get('rationale') or '').strip()\n"
            "    goal = (args.goal or '').strip()\n"
            "    return kind + goal\n")
        self.assertEqual([], or_empty_guards(unrelated, "unrelated.py"))
        # The live controls, read from the modules the criterion names.
        scripts = Path(__file__).resolve().parent.parent
        decisions = (scripts / "decisions.py").read_text(encoding="utf-8")
        self.assertNotIn("decisions.py", {m for m, _, _ in or_empty_guards(decisions,
                                                                          "decisions.py")})
        self.assertIn('_KIND_RE.search(rec.get("rationale") or "")', decisions)


if __name__ == "__main__":
    unittest.main()
