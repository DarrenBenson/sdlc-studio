"""EP0146 / US0393: on the FLAG path a prose-taking writer reports a detected shell hazard on
stderr (non-blocking); on the --fields-file path it raises none, because that prose crossed no
shell. Verified against every converted writer, not one representative."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))

HAZARD = "run `git status` and $(whoami) - a swallowed command on the flag path"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _options(parser) -> set[str]:
    """Every option string a parser accepts, subparsers included. Asked of the PARSER, never of
    the source text: a grep is satisfied by a help string that merely mentions the flag."""
    import argparse  # noqa: PLC0415 - only this helper needs it
    out: set[str] = set()
    for action in parser._actions:
        out.update(action.option_strings)
        if isinstance(action, argparse._SubParsersAction):
            for sub in action.choices.values():
                out |= _options(sub)
    return out


def _critic_repo(d):
    (d / "sdlc-studio" / "reviews").mkdir(parents=True)


def _close_owed_repo(d):
    (d / "sdlc-studio").mkdir(parents=True)


def _sprint_repo(d):
    (d / "sdlc-studio" / ".local").mkdir(parents=True)
    (d / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
        {"schema": 1, "run_id": "RUN-X", "sprint_goal": "g", "outcome": "running", "batch": []}))


#: (module name, repo setup, argv builder given root and a note-value) for every converted writer.
WRITERS = [
    ("critic", _critic_repo, lambda d, note: ["signoff", "--unit", "US0001", "--principal",
     "operator", "--author", "builder", "--note", note, "--root", str(d)]),
    ("close_owed", _close_owed_repo, lambda d, note: ["--root", str(d), "baseline", "--note", note]),
    ("sprint", _sprint_repo, lambda d, note: ["goal-verdict", "--verdict", "achieved",
     "--note", note, "--root", str(d)]),
]


class FlagPathHazardTests(unittest.TestCase):

    def _run(self, name, setup, argv):
        mod = _load(name)
        d = Path(tempfile.mkdtemp(prefix=f"hazard_{name}_"))
        setup(d)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = mod.main(argv(d) if callable(argv) else argv)
        return rc, buf.getvalue(), d

    def test_each_writer_reports_a_hazard_on_stderr(self) -> None:
        for name, setup, build in WRITERS:
            rc, out, _ = self._run(name, setup, lambda d, b=build: b(d, HAZARD))
            self.assertIn("metacharacters", out, f"{name} did not report the flag-path hazard")

    def test_the_warning_is_emitted_yet_does_not_block_the_flag_path(self) -> None:
        for name, setup, build in WRITERS:
            rc, out, _ = self._run(name, setup, lambda d, b=build: b(d, HAZARD))
            self.assertEqual(rc, 0, f"{name} blocked the flag path over a hazard - it must warn only")
            self.assertIn("metacharacters", out)

    def test_fields_file_prose_raises_no_hazard_warning(self) -> None:
        for name, setup, _build in WRITERS:
            mod = _load(name)
            d = Path(tempfile.mkdtemp(prefix=f"hazard_ff_{name}_"))
            setup(d)
            fields = {"verdict": "achieved", "note": HAZARD} if name == "sprint" else {"note": HAZARD}
            (d / "f.json").write_text(json.dumps(fields))
            if name == "critic":
                argv = ["signoff", "--unit", "US0001", "--principal", "operator", "--author",
                        "builder", "--fields-file", str(d / "f.json"), "--root", str(d)]
            elif name == "close_owed":
                argv = ["--root", str(d), "baseline", "--fields-file", str(d / "f.json")]
            else:
                argv = ["goal-verdict", "--fields-file", str(d / "f.json"), "--root", str(d)]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                rc = mod.main(argv)
            self.assertEqual(rc, 0, f"{name} refused the fields-file path")
            self.assertNotIn("metacharacters", buf.getvalue(),
                             f"{name} warned on the fields-file path, which crossed no shell")


def _decisions_repo(d):
    (d / "sdlc-studio").mkdir(parents=True)


def _lessons_repo(d):
    (d / "sdlc-studio" / ".local").mkdir(parents=True)


def _handoff_repo(d):
    hd = d / "sdlc-studio" / "handoffs"
    hd.mkdir(parents=True)
    (hd / "_index.md").write_text("# Handoff Index\n\n**Last Updated:** 2026-07-24\n\n"
                                  "| ID | Title | Date |\n| --- | --- | --- |\n",
                                  encoding="utf-8")
    st = d / "sdlc-studio" / "stories"
    st.mkdir(parents=True)
    (st / "US0002-story-2.md").write_text(
        "# US0002: story 2\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
        "- **AC1:** it works\n  - **Verify:** pytest tests/test_x.py\n", encoding="utf-8")


#: The four writers US0361 converts: (module, repo setup, the flag carrying its free prose, the
#: argv that reaches that flag, the fields-file argv, the document's other required keys).
#: Enumerated rather than represented by one example - a shared loader adopted in three of four
#: writers is exactly the drift this sweep exists to refuse.
REMAINING_WRITERS = [
    ("decisions", _decisions_repo, "--rationale",
     lambda d, prose: ["add", "--decision", "a ruling", "--rationale", prose, "--root", str(d)],
     lambda d, src: ["add", "--decision", "a ruling", "--fields-file", src, "--root", str(d)],
     {}),
    ("lessons", _lessons_repo, "--body",
     lambda d, prose: ["add", "--title", "a lesson", "--body", prose, "--root", str(d)],
     lambda d, src: ["add", "--fields-file", src, "--root", str(d)],
     {"title": "a lesson"}),
    ("ledger", _decisions_repo, "--rationale",
     lambda d, prose: ["record", "--tranche", "CR0001", "--decision", "a ruling",
                       "--rationale", prose, "--root", str(d)],
     lambda d, src: ["record", "--tranche", "CR0001", "--decision", "a ruling",
                     "--fields-file", src, "--root", str(d)],
     {}),
    ("handoff", _handoff_repo, "--title",
     lambda d, prose: ["generate", "--title", prose, "--ids", "US0002", "--root", str(d)],
     lambda d, src: ["generate", "--fields-file", src, "--ids", "US0002", "--root", str(d)],
     {}),
]

#: A title is slugged into a filename and stripped of trailing punctuation for the H1, so the
#: handoff's prose is checked without either.
PROSE = "run `git status` and $(whoami) - a swallowed command"


def _stored(d: Path) -> str:
    """Everything the writer wrote under the fixture root, so the assertion is on the ARTEFACT
    rather than on what the writer printed about it."""
    return "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in sorted(d.rglob("*.md")))


class RemainingProseWriterTests(unittest.TestCase):
    """US0361 AC3: each of the four writers the widened sweep enumerates takes the shared
    fields-file path, and its flag path still works and still reports the damage."""

    def test_the_four_remaining_writers_take_a_fields_file(self) -> None:
        for name, setup, flag, flag_argv, file_argv, extra in REMAINING_WRITERS:
            with self.subTest(name):
                mod = _load(name)
                self.assertIn("--fields-file", _options(mod.build_parser()),
                              f"{name} exposes {flag} but no --fields-file")
                # the fields-file path: stored byte-for-byte, and no hazard warning, because
                # nothing in the document crossed a shell
                d = Path(tempfile.mkdtemp(prefix=f"ff_{name}_"))
                setup(d)
                doc = d.parent / f"{d.name}.json"
                doc.write_text(json.dumps({**extra, flag.lstrip("-"): PROSE}), encoding="utf-8")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    rc = mod.main(file_argv(d, str(doc)))
                self.assertEqual(rc, 0, f"{name} refused the fields-file path: {buf.getvalue()}")
                self.assertNotIn("metacharacters", buf.getvalue(),
                                 f"{name} warned on the fields-file path, which crossed no shell")
                self.assertIn(PROSE, _stored(d), f"{name} did not store the document's prose")
                # the flag path: still works, and still says the value arrived mangled
                d2 = Path(tempfile.mkdtemp(prefix=f"flag_{name}_"))
                setup(d2)
                buf2 = io.StringIO()
                with contextlib.redirect_stdout(buf2), contextlib.redirect_stderr(buf2):
                    rc2 = mod.main(flag_argv(d2, PROSE))
                self.assertEqual(rc2, 0, f"{name} blocked the flag path - it must warn only")
                self.assertIn("metacharacters", buf2.getvalue(),
                              f"{name} stored a mangled {flag} value without reporting it")
                self.assertIn(PROSE, _stored(d2), f"{name} dropped the flag value")


class StdinFieldsDocumentTests(unittest.TestCase):
    """US0361 AC1: `--fields-file -` reads the document from stdin, so a document produced by
    another process reaches the writer without being spilled to a temporary file first."""

    def test_a_fields_file_of_dash_reads_the_document_from_stdin(self) -> None:
        for name, setup, flag, _flag_argv, file_argv, extra in REMAINING_WRITERS:
            with self.subTest(name):
                mod = _load(name)
                d = Path(tempfile.mkdtemp(prefix=f"stdin_{name}_"))
                setup(d)
                doc = json.dumps({**extra, flag.lstrip("-"): PROSE})
                buf = io.StringIO()
                stdin = sys.stdin
                sys.stdin = io.StringIO(doc)
                try:
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                        rc = mod.main(file_argv(d, "-"))
                finally:
                    sys.stdin = stdin
                self.assertEqual(rc, 0, f"{name} refused the stdin document: {buf.getvalue()}")
                self.assertNotIn("metacharacters", buf.getvalue(),
                                 f"{name} warned on a document that crossed no shell")
                self.assertIn(PROSE, _stored(d),
                              f"{name} did not store the stdin document's prose byte-for-byte")

    def test_the_shared_loader_reads_stdin_once_for_every_caller(self) -> None:
        # ONE implementation: the dash is resolved inside the shared loader, so a writer cannot
        # grow its own stdin idiom that drifts from it.
        ff = _load("file_finding")
        stdin = sys.stdin
        sys.stdin = io.StringIO(json.dumps({"note": PROSE}))
        try:
            out = ff.load_fields_file("-", allowed=("note",))
        finally:
            sys.stdin = stdin
        self.assertEqual(out, {"note": PROSE})

    def test_an_unparseable_stdin_document_is_refused_by_name(self) -> None:
        ff = _load("file_finding")
        stdin = sys.stdin
        sys.stdin = io.StringIO("not json at all")
        try:
            with self.assertRaises(ValueError) as cm:
                ff.load_fields_file("-", allowed=("note",))
        finally:
            sys.stdin = stdin
        self.assertIn("stdin", str(cm.exception))


class MixedPathHazardTests(unittest.TestCase):
    """The closing review caught this: a --flag value crossed a shell even when a --fields-file was
    also present, but the hazard check only ran on the flag-only branch."""

    def test_a_flag_value_is_hazard_checked_even_alongside_a_fields_file(self):
        ff = _load("file_finding")
        d = Path(tempfile.mkdtemp(prefix="mixed_hazard_"))
        (d / "f.json").write_text(json.dumps({"note": "safe file note"}))
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            out = ff.resolve_prose_fields(str(d / "f.json"),
                                          {"note": "run $(danger)"}, allowed=("note",))
        self.assertEqual(out["note"], "run $(danger)")           # the flag wins over the file...
        self.assertIn("metacharacters", buf.getvalue())          # ...and is still flagged


if __name__ == "__main__":
    unittest.main()
