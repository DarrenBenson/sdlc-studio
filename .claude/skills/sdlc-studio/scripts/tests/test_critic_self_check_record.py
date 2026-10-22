"""US1088: `critic.py self-check record` stores the author's own claim inventory and mutation run.

The record is refused unless every claim is ruled, none is FALSE and at least one was checked;
unless the commit message and every changelog fragment the unit's Affects declares carry a
claim; and unless each mutant names a test file the unit declares, a result, and, for a
survivor, an answer. A recorded row names the unit, the author, the date, the counts and a
digest of the content of the unit's Affects files, so a later edit is visible against it.

Every criterion drives `critic.py` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
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
sdlc_md = critic.sdlc_md

LOG = Path("sdlc-studio") / "reviews" / "author-self-checks.md"
CODE_AND_TEST = "src/widget.py, tests/test_widget.py, changelog.d/US0101.md"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, unit: str, affects: str) -> None:
    """A unit with the given Affects and a QA seat card, in a throwaway project."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "tests/test_widget.py", "def test_w():\n    assert True\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    kind = "bugs" if unit.startswith("BG") else "stories"
    _write(root, f"sdlc-studio/{kind}/{unit}-widget.md",
           f"# {unit}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _claim(surface: str, ruling: str | None = "TRUE", text: str = "") -> dict:
    entry = {"surface": surface, "claim": text or f"a claim the {surface} makes"}
    if ruling is not None:
        entry["ruling"] = ruling
    return entry


def _covered(fragment: str = "changelog.d/US0101.md") -> list[dict]:
    """A claims list covering both required surfaces, each ruled TRUE."""
    return [_claim("commit message"), _claim(fragment)]


KILLED = [{"mutant": "w returns 2", "test": "tests/test_widget.py::test_w", "result": "killed"}]


def _record(root: Path, unit: str, claims, mutants, *extra: str) -> subprocess.CompletedProcess:
    """Write the two files and run the shipped command over them."""
    cpath, mpath = root / "claims.json", root / "mutants.json"
    cpath.write_text(json.dumps(claims), encoding="utf-8")
    mpath.write_text(json.dumps(mutants), encoding="utf-8")
    return subprocess.run([sys.executable, "-B", str(CRITIC), "self-check", "record", "--unit",
                           unit, "--claims", str(cpath), "--mutants", str(mpath), *extra,
                           "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


class SelfCheckRecordTests(unittest.TestCase):

    def _refused(self, root: Path, r: subprocess.CompletedProcess, *names: str) -> None:
        self.assertEqual(2, r.returncode, f"not refused:\n{r.stdout}{r.stderr}")
        for name in names:
            self.assertIn(name, r.stderr, "the refusal does not name its cause")
        self.assertFalse((root / LOG).exists(), "a refused record still wrote the log")

    def test_an_unruled_false_or_unchecked_inventory_is_refused(self) -> None:
        """AC1. Mutants: `validate_claim_inventory` not called, so an unruled claim or one ruled
        MAYBE beside a TRUE one is recorded; the all-UNVERIFIABLE check dropped, so an inventory
        that checked nothing is recorded; a FALSE ruling recorded rather than refused."""
        cases = {
            "unruled": ([*_covered(), _claim("docstrings", None, "w is pure")], "w is pure"),
            "outside the vocabulary": ([*_covered(), _claim("comments", "MAYBE")], "MAYBE"),
            "ruled FALSE": ([*_covered(), _claim("comments", "FALSE", "w caches")], "w caches"),
            "all UNVERIFIABLE": ([_claim("commit message", "UNVERIFIABLE"),
                                  _claim("changelog.d/US0101.md", "UNVERIFIABLE")],
                                 "UNVERIFIABLE"),
        }
        for label, (claims, named) in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, "US0101", CODE_AND_TEST)
                self._refused(root, _record(root, "US0101", claims, KILLED), named)
        with tempfile.TemporaryDirectory() as d:  # the positive control beside them
            root = Path(d)
            _project(root, "US0101", CODE_AND_TEST)
            claims = [*_covered(), _claim("docstrings", "UNVERIFIABLE")]
            r = _record(root, "US0101", claims, KILLED)
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertTrue((root / LOG).is_file(), "a TRUE and UNVERIFIABLE inventory was not written")

    def test_a_claims_file_skipping_a_surface_is_refused(self) -> None:
        """AC2. Mutants: the fragment found as changelog.d/<id>.md rather than read from the
        unit's Affects, which misses a carried bug's fragment; the commit-message surface not
        required. A surface nobody named is refused rather than counted."""
        unit, fragment = "BG0201", "changelog.d/US0200.md"
        cases = {
            "no commit-message claim": ([_claim(fragment)], "commit message"),
            "no claim from the declared fragment": ([_claim("commit message")], fragment),
            "a surface nobody named": ([*_covered(fragment), _claim("release notes")],
                                       "release notes"),
        }
        for label, (claims, named) in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, unit, f"src/widget.py, tests/test_widget.py, {fragment}")
                r = _record(root, unit, claims, KILLED)
                self._refused(root, r, named)
                self.assertNotIn(f"changelog.d/{unit}.md", r.stderr, "a fragment was taken from the id")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, unit, f"src/widget.py, tests/test_widget.py, {fragment}")
            r = _record(root, unit, [*_covered(fragment), _claim("the commit message")], KILLED)
            self.assertEqual(0, r.returncode, r.stderr)

    def test_an_undeclared_test_or_unanswered_survivor_is_refused(self) -> None:
        """AC3. Mutants: a mutant against a test the unit does not declare recorded; a survivor
        recorded with no answer; a docs-only unit refused for having no mutant, which would leave
        it unbriefable under `block`."""
        survivor = {"mutant": "w returns None", "test": "tests/test_widget.py::test_w",
                    "result": "survived"}
        cases = {
            "no mutant": ([], "lists no mutant"),
            "an undeclared test": ([{**KILLED[0], "test": "tests/test_other.py::test_x"}],
                                   "tests/test_other.py"),
            "no result": ([{"mutant": "w raises", "test": "tests/test_widget.py"}], "w raises"),
            "a result outside killed and survived": ([{**KILLED[0], "result": "timeout"}],
                                                     "timeout"),
            "an unanswered survivor": ([survivor], "w returns None"),
        }
        for label, (mutants, named) in cases.items():
            with self.subTest(case=label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, "US0101", CODE_AND_TEST)
                self._refused(root, _record(root, "US0101", _covered(), mutants), named)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0101", CODE_AND_TEST)
            answered = {**survivor, "answer": "None and 1 are both truthy-checked; filed BG0001"}
            r = _record(root, "US0101", _covered(), [*KILLED, answered])
            self.assertEqual(0, r.returncode, r.stderr)
            row = critic.read_self_checks(root)[-1]
            self.assertEqual("killed 1, survived 1", row["mutants"])
        with tempfile.TemporaryDirectory() as d:  # a docs-only unit
            root = Path(d)
            _project(root, "US0102", "docs/guide.md, changelog.d/US0102.md")
            claims = _covered("changelog.d/US0102.md")
            self._refused(root, _record(root, "US0102", claims, KILLED), "tests/test_widget.py")
            r = _record(root, "US0102", claims, [])
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn("no test declared", critic.read_self_checks(root)[-1]["mutants"])

    def test_the_record_binds_the_affects_content(self) -> None:
        """AC4. Mutant: the digest computed over the Affects PATHS (or their sizes) rather than
        their content, so a same-length edit to a declared file leaves it unmoved. The log is
        committed, never under .local."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0101", f"{CODE_AND_TEST}, tools/")
            _write(root, "tools/check.sh", "echo ok\n")
            claims = [*_covered(), _claim("comments", "UNVERIFIABLE")]
            r = _record(root, "US0101", claims, KILLED, "--author", "builder-7")
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn(str(LOG), r.stdout)
            text = (root / LOG).read_text(encoding="utf-8")
            self.assertIn("| Unit | Author | Date | Claims | Mutants | Digest |", text)
            first = critic.read_self_checks(root)[-1]
            self.assertEqual("US0101", first["unit"])
            self.assertEqual("builder-7", first["author"])
            self.assertEqual(sdlc_md.now_date(), first["date"])
            self.assertEqual("TRUE 2, FALSE 0, UNVERIFIABLE 1", first["claims"])
            self.assertEqual("killed 1, survived 0", first["mutants"])
            self.assertEqual(critic.affects_digest(root, "US0101"), first["digest"])
            # A file, and one inside a declared directory; each edit keeps the file's length.
            for rel, was, now in (("src/widget.py", "1", "2"), ("tools/check.sh", "ok", "no")):
                with self.subTest(edited=rel):
                    before = critic.affects_digest(root, "US0101")
                    _write(root, rel, (root / rel).read_text(encoding="utf-8").replace(was, now))
                    self.assertNotEqual(before, critic.affects_digest(root, "US0101"))
            r = _record(root, "US0101", claims, KILLED, "--author", "builder-7")
            self.assertEqual(0, r.returncode, r.stderr)
            second = critic.read_self_checks(root)[-1]
            self.assertNotEqual(first["digest"], second["digest"],
                                "the command bound the same digest to a different diff")
            self.assertEqual([], [str(p) for p in (root / "sdlc-studio").rglob("*self-check*")
                                  if ".local" in p.parts], "a self-check was kept under .local")

    def test_the_brief_names_the_record_command(self) -> None:
        """AC5. Mutant: the brief's author self-check section printing no record command. The
        command it prints parses under the shipped parser, so the two cannot drift apart."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0101", CODE_AND_TEST)
            r = subprocess.run([sys.executable, "-B", str(CRITIC), "brief", "--unit", "US0101",
                                "--seat", "qa", "--tier", "full", "--root", str(root)],
                               capture_output=True, text=True, timeout=300,
                               env=gitutil.git_env(), check=False)
            self.assertEqual(0, r.returncode, r.stderr)
            start = r.stderr.find("AUTHOR SELF-CHECK")
            section = r.stderr[start:r.stderr.find("review tier:", start)]
            self.assertGreaterEqual(start, 0, r.stderr)
            line = next((ln for ln in section.splitlines()
                         if "critic.py self-check record --unit US0101" in ln), "")
            self.assertTrue(line, f"the section names no record command:\n{section}")
            words = shlex.split(line[line.index("critic.py"):].rstrip("."))[1:]
            args = critic.build_parser().parse_args(words)
            self.assertEqual(("self-check", "US0101"), (args.cmd, args.unit))
            self.assertNotIn("self-check record", r.stdout, "the record command reached the brief")


if __name__ == "__main__":
    unittest.main()
