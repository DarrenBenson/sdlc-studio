"""A bug records that it escaped to production: the release it shipped in and the unit that
let it through, written by both creation paths and held at the move to Fixed until its Root
Cause is written."""
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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the gitutil helper
import gitutil  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


artifact = _load("artifact")
file_finding = _load("file_finding")
transition = _load("transition")

ESCAPE = ["--escaped", "--shipped-in", "v1.0.0", "--escaped-via", "US0001"]


def _cli(main, argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def _project(d: str, tag: str = "v1.0.0") -> Path:
    """A git project tagged `tag`, with one story on disk and a source file a bug can affect."""
    root = Path(d)
    (root / "sdlc-studio" / "bugs").mkdir(parents=True)
    (root / "sdlc-studio" / "bugs" / "_index.md").write_text(
        "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    (root / "sdlc-studio" / "stories").mkdir(parents=True)
    (root / "sdlc-studio" / "stories" / "US0001-a-shipped-story.md").write_text(
        "# US0001: a shipped story\n\n> **Status:** Done\n> **Affects:** a.py\n",
        encoding="utf-8")
    (root / "a.py").write_text("x = 1\n", encoding="utf-8")
    gitutil.git(["init", "-q"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", "feat(US0001): ship it"], root)
    gitutil.git(["tag", tag], root)
    return root


def _new_bug(root: Path, *extra: str) -> tuple[int, str, str]:
    """`artifact.py new --type bug` through its CLI."""
    return _cli(artifact.main, ["new", "--type", "bug", "--title", "the total is wrong",
                                "--severity", "Medium", "--affects", "a.py", "--points", "2",
                                "--summary", "the total is wrong", "--ac", "the total is right",
                                "--format", "json", "--root", str(root), *extra])


def _file_bug(root: Path, *extra: str) -> tuple[int, str, str]:
    """`file_finding.py file --type bug` through its CLI."""
    return _cli(file_finding.main, ["file", "--type", "bug", "--title", "the sum is wrong",
                                    "--severity", "Medium", "--affects", "a.py",
                                    "--points", "2", "--summary", "the sum is wrong",
                                    "--steps", "add two numbers", "--fix", "carry the one",
                                    "--format", "json", "--root", str(root), *extra])


def _bug_files(root: Path) -> list[Path]:
    return sorted(p for p in (root / "sdlc-studio" / "bugs").glob("*.md")
                  if p.name != "_index.md")


class BugEscapeFieldTests(unittest.TestCase):

    def test_an_escaped_bug_carries_release_and_unit(self) -> None:
        for label, create in (("artifact new", _new_bug), ("file_finding file", _file_bug)):
            with self.subTest(path=label), tempfile.TemporaryDirectory() as d:
                root = _project(d)
                rc, out, err = create(root, *ESCAPE)
                self.assertEqual(0, rc, err)
                text = Path(json.loads(out)["path"]).read_text(encoding="utf-8")
                lines = text.splitlines()
                for want in ("> **Escaped:** yes", "> **Shipped-in:** v1.0.0",
                             "> **Escaped-via:** US0001"):
                    self.assertIn(want, lines, f"{label}: {want} missing")
                self.assertIn("## Root Cause", lines, f"{label}: no Root Cause section")
                section = text.split("## Root Cause", 1)[1].split("\n## ", 1)[0]
                self.assertIn(file_finding.ROOT_CAUSE_SCAFFOLD, section)
                # The fields sit in the header block, where every reader looks for a field.
                head = text.split("\n## ", 1)[0]
                self.assertIn("> **Shipped-in:** v1.0.0", head)

    def test_an_escape_without_a_resolvable_release_or_unit_is_refused(self) -> None:
        cases = (
            (["--escaped"], "needs --shipped-in"),
            (["--escaped", "--shipped-in", "v9.9.9"], "v9.9.9"),
            (["--escaped", "--shipped-in", "v1.0.0", "--escaped-via", "US0999"], "US0999"),
            (["--shipped-in", "v1.0.0"], "--escaped"),
        )
        for label, create in (("artifact new", _new_bug), ("file_finding file", _file_bug)):
            for argv, named in cases:
                with self.subTest(path=label, argv=argv), tempfile.TemporaryDirectory() as d:
                    root = _project(d)
                    rc, _out, err = create(root, *argv)
                    self.assertEqual(2, rc, f"{label} {argv}: {err}")
                    self.assertIn(named, err)
                    self.assertEqual([], _bug_files(root), f"{label} {argv} wrote a file")
            with self.subTest(path=label, case="a release the changelog names"), \
                    tempfile.TemporaryDirectory() as d:
                root = _project(d)
                (root / "CHANGELOG.md").write_text("# Changelog\n\n## [2.0.0] - 2026-01-01\n",
                                                   encoding="utf-8")
                rc, _out, err = create(root, "--escaped", "--shipped-in", "v2.0.0")
                self.assertEqual(0, rc, err)
            with self.subTest(path=label, case="a bug that did not escape"), \
                    tempfile.TemporaryDirectory() as d:
                root = _project(d)
                rc, out, err = create(root)
                self.assertEqual(0, rc, err)
                text = Path(json.loads(out)["path"]).read_text(encoding="utf-8")
                for absent in ("Escaped", "Shipped-in", "## Root Cause"):
                    self.assertNotIn(absent, text)

    def test_an_escaped_bug_is_not_fixed_with_an_empty_root_cause(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, out, err = _new_bug(root, *ESCAPE)
            self.assertEqual(0, rc, err)
            path = Path(json.loads(out)["path"])
            bug_id = path.name.split("-")[0]
            # Tick the criterion, so the only thing between this bug and Fixed is the cause.
            path.write_text(path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
                            encoding="utf-8")
            rc, out, err = _cli(transition.main, ["set", "--id", bug_id, "--status", "Fixed",
                                                  "--root", str(root)])
            self.assertNotEqual(0, rc)
            self.assertIn("Root Cause section is unwritten", out + err)
            self.assertIn("> **Status:** Open", path.read_text(encoding="utf-8"))
            # Written, the cause lets it through.
            text = path.read_text(encoding="utf-8").replace(
                file_finding.ROOT_CAUSE_SCAFFOLD,
                "The review read the diff, not the rounding path the total takes.")
            path.write_text(text, encoding="utf-8")
            rc, _o, err = _cli(transition.main, ["set", "--id", bug_id, "--status", "Fixed",
                                                 "--root", str(root)])
            self.assertEqual(0, rc, err)
            self.assertIn("> **Status:** Fixed", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
