"""US1013: a verdict that differs from its issued file, or was recorded before, is named.

`critic.py record` compares a transcribed block with the files a brief issued for the unit under
the same fingerprint, refuses a file whose bytes an earlier row already carries or whose header
names another unit or another file, and `critic.py show` says when a recorded file has changed or
gone since its row was written.

Every case drives `critic.py` through its entry point in a throwaway project, from a working
directory that is not the project root.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")

UNIT = "US0001"
DRIFT = "differs from"
#: Three findings, wrapped across lines, a BLOCKING none and a RULINGS line the row keeps apart.
ISSUED = ("VERDICT: APPROVE\n"
          "ISSUES: [pre-existing] the docstring names a\n"
          "    removed flag\n"
          "  [pre-existing] the help page lists two verbs\n"
          "  [pre-existing] the changelog fragment is undated\n"
          "BLOCKING: none\n"
          "RULINGS: AC1 met through the entry point\n")
A = "[pre-existing] the docstring names a removed flag"
B = "[pre-existing] the help page lists two verbs"
C = "[pre-existing] the changelog fragment is undated"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, *units: str) -> None:
    """Stories with a QA seat card, in a throwaway project."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    for unit in units or (UNIT,):
        _write(root, f"sdlc-studio/stories/{unit}-widget.md",
               f"# {unit}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")


def _critic(cwd: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args], cwd=cwd, input=stdin,
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _brief(cwd: Path, root: Path, unit: str = UNIT) -> tuple[Path, list[str]]:
    """Brief the unit: the issued path, and the footer's record command as argv."""
    r = _critic(cwd, "brief", "--unit", unit, "--seat", "qa", "--root", str(root))
    assert r.returncode == 0, r.stderr
    tail = r.stdout[r.stdout.rindex(critic._RETURN_CONTRACT):]
    path = next(Path(ln.strip()) for ln in tail.splitlines() if ln.strip().endswith(".txt"))
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", r.stderr, re.M)
    assert m, r.stderr
    return path, [a for a in shlex.split(m.group(1)) if a != "..."]


def _header(path: Path, unit: str = UNIT, stem: str | None = None) -> str:
    return f"UNIT: {unit}\nBRIEF: {stem or path.stem}\n"


def _record(cwd: Path, root: Path, argv: list[str],
            stdin: str | None = None) -> subprocess.CompletedProcess:
    return _critic(cwd, *argv, "--reviewer", "qa-seat", "--author", "builder",
                   "--root", str(root), stdin=stdin)


def _transcribe(argv: list[str], *how: str) -> list[str]:
    """The footer's command with its `--from-verdict <path>` swapped for `how`, `--brief` kept."""
    at = argv.index("--from-verdict")
    return argv[:at] + list(how) + argv[at + 2:]


def _warning(stderr: str) -> str:
    lines = [ln for ln in stderr.splitlines() if DRIFT in ln]
    assert len(lines) <= 1, stderr
    return lines[0] if lines else ""


class VerdictDriftTests(unittest.TestCase):

    def test_a_transcription_that_differs_from_the_issued_file_warns_and_a_reflow_does_not(
            self) -> None:
        """AC1. Mutants: comparing the verdict word only; comparing raw text; naming the last
        difference, or the file's first finding, rather than the first that differs."""
        reflowed = (f"VERDICT: APPROVE\nISSUES: {A}\n{B}\n  {C}\nBLOCKING: none\n")
        cases = (
            # (why, how the block reaches record, stdin, the text the warning names, or None)
            ("a dropped finding, from stdin", ("--from-verdict", "-"),
             f"VERDICT: APPROVE\nISSUES: {A}\n  {C}\nBLOCKING: none\n", B),
            ("a changed finding, by flags",
             ("--verdict", "approve", "--issues", f"{A}; [new] the help page lists two verbs; {C}"),
             None, B),
            ("a changed verdict, by flags",
             ("--verdict", "reject", "--issues", f"{A}; {B}; {C}"), None, "REJECT"),
            ("reflowed only, from stdin", ("--from-verdict", "-"), reflowed, None),
            ("the same findings, by flags",
             ("--verdict", "approve", "--issues", f"{A}; {B}; {C}"), None, None),
        )
        for why, how, stdin, named in cases:
            with self.subTest(why), tempfile.TemporaryDirectory() as d, \
                    tempfile.TemporaryDirectory() as elsewhere:
                root, cwd = Path(d), Path(elsewhere)
                _project(root)
                path, argv = _brief(cwd, root)
                path.write_text(_header(path) + ISSUED, encoding="utf-8")
                r = _record(cwd, root, _transcribe(argv, *how), stdin=stdin)
                self.assertEqual(0, r.returncode, r.stderr)
                self.assertEqual("-", critic.read_verdicts(root)[-1]["source"], "written as transcribed")
                warning = _warning(r.stderr)
                if named is None:
                    self.assertEqual("", warning, r.stderr)
                    continue
                self.assertIn(str(path), warning)
                self.assertIn(named, warning)
                if named == B:
                    self.assertNotIn(C, warning, "named a later finding than the first to differ")
                    self.assertNotIn(A, warning, "named a finding that matches")

    def test_re_briefs_compare_every_issued_unrecorded_file_and_name_the_newest(self) -> None:
        """AC1, the notes' re-brief rule. Mutants: comparing the newest file only; naming the
        oldest; counting a file a row already records, or a file never written."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            older, argv = _brief(cwd, root)
            newer, again = _brief(cwd, root)
            _brief(cwd, root)  # issued, never written
            self.assertEqual(argv[argv.index("--brief") + 1], again[again.index("--brief") + 1])
            older.write_text(_header(older) + f"VERDICT: APPROVE\nISSUES: {A}\nBLOCKING: none\n",
                             encoding="utf-8")
            newer.write_text(_header(newer) + f"VERDICT: APPROVE\nISSUES: {B}\nBLOCKING: none\n",
                             encoding="utf-8")
            r = _record(cwd, root, _transcribe(argv, "--verdict", "approve", "--issues", A))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("", _warning(r.stderr), "the older file matches")
            r = _record(cwd, root, _transcribe(argv, "--verdict", "approve", "--issues", C))
            self.assertEqual(0, r.returncode, r.stderr)
            warning = _warning(r.stderr)
            self.assertIn(str(newer), warning)
            self.assertNotIn(older.name, warning)
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            first, argv = _brief(cwd, root)
            second, _ = _brief(cwd, root)
            first.write_text(_header(first) + f"VERDICT: APPROVE\nISSUES: {A}\nBLOCKING: none\n",
                             encoding="utf-8")
            second.write_text(_header(second) + f"VERDICT: APPROVE\nISSUES: {B}\nBLOCKING: none\n",
                              encoding="utf-8")
            self.assertEqual(0, _record(cwd, root, argv).returncode)  # binds `first`
            r = _record(cwd, root, _transcribe(argv, "--verdict", "approve", "--issues", A))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn(str(second), _warning(r.stderr), "a recorded file is not compared")
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            before, argv = _brief(cwd, root)
            before.write_text(_header(before) + f"VERDICT: APPROVE\nISSUES: {A}\nBLOCKING: none\n",
                              encoding="utf-8")
            story = root / "sdlc-studio" / "stories" / f"{UNIT}-widget.md"
            story.write_text(story.read_text(encoding="utf-8")
                             + "\n### AC2: also\n- **Verify:** shell true\n", encoding="utf-8")
            after, moved = _brief(cwd, root)  # the scope moved, so the fingerprint did
            self.assertNotEqual(argv[argv.index("--brief") + 1], moved[moved.index("--brief") + 1])
            after.write_text(_header(after) + f"VERDICT: APPROVE\nISSUES: {B}\nBLOCKING: none\n",
                             encoding="utf-8")
            r = _record(cwd, root, _transcribe(moved, "--verdict", "approve", "--issues", A))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn(str(after), _warning(r.stderr), "a file under another fingerprint")

    def test_a_replayed_or_misheaded_file_is_refused_and_bare_approves_are_not(self) -> None:
        """AC2. Mutants: no header check; the replay test made on the path, or on the parsed
        block, rather than the file's bytes."""
        bare = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root, UNIT, "US0002")
            one, argv_one = _brief(cwd, root)
            two, argv_two = _brief(cwd, root, "US0002")
            one.write_text(_header(one) + bare, encoding="utf-8")
            two.write_text(_header(two, "US0002") + bare, encoding="utf-8")
            for argv in (argv_one, argv_two):
                r = _record(cwd, root, argv)
                self.assertEqual(0, r.returncode, r.stderr)
            rows = critic.read_verdicts(root)
            self.assertEqual([UNIT, "US0002"], [row["unit"] for row in rows])
            earlier = rows[0]["source"]
            self.assertTrue(earlier.startswith("sha256:"), earlier)
            ledger = critic.verdicts_path(root).read_bytes()

            copy, argv_copy = _brief(cwd, root)
            copy.write_bytes(one.read_bytes())
            mixed, argv_mixed = _brief(cwd, root)
            mixed.write_text(_header(mixed, "US0002") + bare, encoding="utf-8")
            borrowed, argv_borrowed = _brief(cwd, root)
            borrowed.write_text(_header(borrowed, UNIT, two.stem) + bare, encoding="utf-8")
            cases = (
                ("the same file again", argv_one, (earlier,)),
                ("its bytes at another issued path", argv_copy, (earlier,)),
                ("a UNIT line naming another unit", argv_mixed, ("UNIT: US0002", UNIT)),
                ("a BRIEF line naming another file", argv_borrowed,
                 (f"BRIEF: {two.stem}", borrowed.stem)),
            )
            for why, argv, named in cases:
                with self.subTest(why):
                    r = _record(cwd, root, argv)
                    self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                    for text in named:
                        self.assertIn(text, r.stderr)
                    if named == (earlier,):
                        self.assertIn(f"{UNIT} APPROVE", r.stderr, "names the earlier row")
                    self.assertEqual(ledger, critic.verdicts_path(root).read_bytes(),
                                     "a refusal wrote to the ledger")
            # Saved anywhere a brief did not issue: the UNIT line still refuses another unit's
            # block, and the BRIEF line, naming the file it was written to, does not refuse.
            foreign, saved = cwd / "foreign.txt", cwd / "saved.txt"
            foreign.write_text(_header(two, "US0002") + "VERDICT: APPROVE\nISSUES: none\n"
                               "BLOCKING: none\nRULINGS: saved by hand\n", encoding="utf-8")
            r = _record(cwd, root, ["record", "--unit", UNIT, "--from-verdict", str(foreign)])
            self.assertEqual(2, r.returncode, r.stdout + r.stderr)
            self.assertIn("UNIT: US0002", r.stderr)
            saved.write_text(_header(copy) + "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
                             "RULINGS: saved by hand\n", encoding="utf-8")
            r = _record(cwd, root, ["record", "--unit", UNIT, "--from-verdict", str(saved)])
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("-", critic.read_verdicts(root)[-1]["source"])

    def test_show_names_a_verdict_file_changed_or_missing_since_it_was_recorded(self) -> None:
        """AC3. Mutants: `show` hashing the file and comparing it with itself; testing only that
        the path exists; the note on a line of its own rather than its row's."""
        units = (UNIT, "US0002", "US0003")
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root, *units)
            issued = {}
            for unit in units:
                path, argv = _brief(cwd, root, unit)
                path.write_text(_header(path, unit) + "VERDICT: APPROVE\nISSUES: none\n"
                                "BLOCKING: none\n", encoding="utf-8")
                self.assertEqual(0, _record(cwd, root, argv).returncode)
                issued[unit] = path
            with issued[UNIT].open("a", encoding="utf-8") as fh:
                fh.write("A line added after the row was written.\n")
            issued["US0002"].unlink()
            r = _critic(cwd, "show", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stderr)
            lines = {unit: [ln for ln in r.stdout.splitlines() if unit in ln] for unit in units}
            for unit in units:
                self.assertEqual(1, len(lines[unit]), r.stdout)
            self.assertIn("(changed since it was recorded)", lines[UNIT][0])
            self.assertNotIn("missing", lines[UNIT][0])
            self.assertIn("(missing)", lines["US0002"][0])
            self.assertNotIn("changed", lines["US0002"][0])
            self.assertNotIn("changed", lines["US0003"][0], "an untouched file is not flagged")
            self.assertNotIn("missing", lines["US0003"][0])
            r = _critic(cwd, "show", "--format", "json", "--root", str(root))
            states = {row["unit"]: row["verdict_file_state"] for row in json.loads(r.stdout)}
            self.assertEqual({UNIT: "changed", "US0002": "missing", "US0003": "unchanged"}, states)


if __name__ == "__main__":
    unittest.main()
