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
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
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


# --- The runner's report ------------------------------------------------------------------
MUTATION = SCRIPTS / "mutation.py"
WIDGET = ("def add(a, b):\n    return a + b\n\n\ndef sign(x):\n    if x < 0:\n"
          "        return -1\n    return 1\n")
WIDGET_TESTS = ("from src.widget import add, sign\n\n\ndef test_add():\n"
                "    assert add(2, 3) == 5\n\n\ndef test_sign():\n    assert sign(-4) == -1\n"
                "    assert sign(4) == 1\n")
ADD, SIGN = "tests/test_widget.py::test_add", "tests/test_widget.py::test_sign"
#: Three mutants the widget's tests kill.
THREE_KILLED = [
    {"mutant": "add subtracts", "file": "src/widget.py", "old": "return a + b",
     "new": "return a - b", "test": ADD},
    {"mutant": "negative reads positive", "file": "src/widget.py", "old": "return -1",
     "new": "return 1", "test": SIGN},
    {"mutant": "positive reads zero", "file": "src/widget.py", "old": "    return 1\n",
     "new": "    return 0\n", "test": SIGN},
]
#: One the tests cannot see: no test asks for the sign of zero.
ZERO_SURVIVES = {"mutant": "zero reads negative", "file": "src/widget.py", "old": "if x < 0:",
                 "new": "if x <= 0:", "test": SIGN}


def _runner_project(root: Path, unit: str = "US0101", verify: tuple = (ADD, SIGN)) -> None:
    """A git work tree whose unit declares the widget, its tests and a fragment, with a pytest
    Verify selector per criterion: the tree the mutation runner copies and mutates."""
    _project(root, unit, "src/widget.py, tests/test_widget.py, changelog.d/US0101.md")
    acs = "".join(f"### AC{n}: holds\n- **Verify:** pytest {sel}\n\n"
                  for n, sel in enumerate(verify, 1))
    _write(root, f"sdlc-studio/stories/{unit}-widget.md",
           f"# {unit}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** src/widget.py, tests/test_widget.py, changelog.d/US0101.md\n\n"
           f"## Acceptance Criteria\n\n{acs}")
    _write(root, "src/widget.py", WIDGET)
    _write(root, "tests/test_widget.py", WIDGET_TESTS)
    gitutil.git(["init", "-q"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", "fixture"], root)


def _run_runner(root: Path, edits: list, unit: str = "US0101", name: str = "report") -> Path:
    """The shipped runner over `edits`, through its entry point; the report it wrote."""
    epath, report = root.parent / f"{name}-edits.json", root.parent / f"{name}.json"
    epath.write_text(json.dumps(edits), encoding="utf-8")
    r = subprocess.run([sys.executable, "-B", str(MUTATION), "run", "--edits", str(epath),
                        "--scope", unit, "--report", str(report), "--root", str(root)],
                       cwd=str(root), capture_output=True, text=True, timeout=300,
                       env=gitutil.git_env(), check=False)
    assert report.is_file(), f"the runner wrote no report:\n{r.stdout}{r.stderr}"
    return report


def _record_from(root: Path, unit: str, report: Path, *extra: str) -> subprocess.CompletedProcess:
    """`self-check record --mutants-from <report>` through the shipped command."""
    cpath = root.parent / "claims.json"
    cpath.write_text(json.dumps(_covered()), encoding="utf-8")
    return subprocess.run([sys.executable, "-B", str(CRITIC), "self-check", "record", "--unit",
                           unit, "--claims", str(cpath), "--mutants-from", str(report), *extra,
                           "--author", "builder-7", "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _rewrite_report(report: Path, change) -> Path:
    """The report with `change(data)` applied, as an author editing it by hand would."""
    data = json.loads(report.read_text(encoding="utf-8"))
    change(data)
    report.write_text(json.dumps(data), encoding="utf-8")
    return report


class SelfCheckRecordTests(unittest.TestCase):

    def _refused(self, root: Path, r: subprocess.CompletedProcess, *names: str) -> None:
        self.assertEqual(2, r.returncode, f"not refused:\n{r.stdout}{r.stderr}")
        for name in names:
            self.assertIn(name, r.stderr, "the refusal does not name its cause")
        self.assertFalse((root / LOG).exists(), "a refused record still wrote the log")

    def test_an_unruled_false_or_unchecked_inventory_is_refused(self) -> None:
        """AC1. Mutants: `validate_claim_inventory` not called, so an unruled claim or one ruled
        MAYBE beside a TRUE one is recorded; the all-UNVERIFIABLE check dropped, so an inventory
        that checked nothing is recorded; a FALSE ruling recorded rather than refused; an empty
        claims list refused under the all-UNVERIFIABLE cause rather than for making no claim."""
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
        with self.subTest(case="no claim at all"), tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0101", CODE_AND_TEST)
            r = _record(root, "US0101", [], KILLED)
            self._refused(root, r, "lists no claim")
            self.assertNotIn("UNVERIFIABLE", r.stderr, "an empty list was refused for a ruling it has not got")
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
        required; only the first declared fragment required, or any one fragment taken as
        enough, which a unit declaring two tells apart; the surface label compared with its case.
        A surface nobody named is refused rather than counted."""
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
        second = "changelog.d/US0199.md"
        with self.subTest(case="the second of two declared fragments uncovered"), \
                tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, unit, f"src/widget.py, tests/test_widget.py, {fragment}, {second}")
            self._refused(root, _record(root, unit, _covered(fragment), KILLED), second)
            r = _record(root, unit, [*_covered(fragment), _claim(second)], KILLED)
            self.assertEqual(0, r.returncode, r.stderr)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, unit, f"src/widget.py, tests/test_widget.py, {fragment}")
            claims = [_claim("The Commit Message"), _claim("Changelog.d/US0200.md")]
            r = _record(root, unit, claims, KILLED)
            self.assertEqual(0, r.returncode, r.stderr)

    def test_the_commit_message_is_required_without_a_fragment(self) -> None:
        """Beyond AC2's letter, which speaks of units declaring fragments. Mutant: the
        required-surface check gated on the unit declaring a fragment, so a unit declaring none
        is recorded with no claim on its commit message."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0103", "src/widget.py, tests/test_widget.py")
            self._refused(root, _record(root, "US0103", [_claim("docstrings")], KILLED),
                          "commit message")
            r = _record(root, "US0103", [_claim("commit message")], KILLED)
            self.assertEqual(0, r.returncode, r.stderr)

    def test_an_undeclared_test_or_unanswered_survivor_is_refused(self) -> None:
        """AC3. Mutants: a mutant against a test the unit does not declare recorded; a survivor
        recorded with no answer, or with an answer of whitespace alone; a docs-only unit refused
        for having no mutant, which would leave it unbriefable under `block`."""
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
            "a survivor answered with whitespace": ([{**survivor, "answer": "   "}],
                                                    "w returns None"),
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
        """AC4. Mutants: the digest computed over the Affects PATHS (or their sizes) rather than
        their content, so a same-length edit to a declared file leaves it unmoved; the paths
        taken in declared order, so a regroom that only reorders Affects stales the record. The
        log is committed, never under .local."""
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
            _project(root, "US0101", f"tools/, changelog.d/US0101.md, tests/test_widget.py, "
                                     f"src/widget.py")
            r = _record(root, "US0101", claims, KILLED, "--author", "builder-7")
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual(first["digest"], critic.read_self_checks(root)[-1]["digest"],
                             "reordering Affects moved the digest")
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

    def test_the_runners_report_is_recorded_with_its_full_mutant_list(self) -> None:
        """The runner's own report, three mutants all killed, is recorded with its counts and
        its whole list, which the brief reads back. Mutants: only the counts kept; a key of
        each mutant dropped from what is kept; a report for another unit, or a mutant the
        runner did not apply, recorded; a later record by hand left reading the stale list."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            _runner_project(root)
            report = _run_runner(root, THREE_KILLED)
            r = _record_from(root, "US0101", report)
            self.assertEqual(0, r.returncode, r.stderr)
            row = critic.read_self_checks(root)[-1]
            self.assertEqual(("US0101", "killed 3, survived 0"), (row["unit"], row["mutants"]))
            kept = critic.recorded_mutants(root, "US0101")
            self.assertIsNotNone(kept, "the record kept no mutant list for the brief to read")
            ran = json.loads(report.read_text(encoding="utf-8"))["mutants"]
            keys = ("mutant", "file", "old", "new", "test", "result")
            self.assertEqual([{k: m[k] for k in keys} for m in ran],
                             [{k: m[k] for k in keys} for m in kept])
            self.assertEqual(["killed"] * 3, [m["result"] for m in kept])
            self.assertEqual(sorted(e["old"] for e in THREE_KILLED),
                             sorted(m["old"] for m in kept))
            # The same list read back is the brief's: kept in a committed file, not under .local.
            self.assertFalse(any(".local" in p.parts for p in (root / "sdlc-studio").rglob("*")
                                 if p.is_file() and "US0101" in p.name and "mutant" in p.name))
            # A kept list naming another row is not this row's.
            sidecar = critic.author_mutants_path(root, "US0101")
            good = sidecar.read_text(encoding="utf-8")
            sidecar.write_text(good.replace(row["digest"], "0123456789abcdef"), encoding="utf-8")
            self.assertIsNone(critic.recorded_mutants(root, "US0101"),
                              "a list kept for another row was read as this row's")
            sidecar.write_text(good, encoding="utf-8")
            for label, change, named in (
                    ("another unit's report", lambda data: data.update(unit="US0999"), "US0999"),
                    ("a mutant not applied", lambda data: data["mutants"][1].update(
                        result="not-applied", reason="the old text is not in src/widget.py"),
                     "negative reads positive"),
                    ("counts its rows deny", lambda data: data["counts"].update(killed=2),
                     "counts")):
                with self.subTest(refused=label):
                    bad = Path(d) / f"{label}.json"
                    bad.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
                    before = (root / LOG).read_text(encoding="utf-8")
                    r = _record_from(root, "US0101", _rewrite_report(bad, change))
                    self.assertEqual(2, r.returncode, f"recorded:\n{r.stdout}{r.stderr}")
                    self.assertIn(named, r.stderr)
                    self.assertEqual(before, (root / LOG).read_text(encoding="utf-8"))
            r = _record(root, "US0101", _covered(), [{"mutant": "by hand", "result": "killed",
                                                      "test": ADD}])
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("killed 1, survived 0", critic.read_self_checks(root)[-1]["mutants"])
            self.assertIsNone(critic.recorded_mutants(root, "US0101"),
                              "a record by hand left the brief reading the report's list")

    def test_a_report_with_an_unanswered_survivor_is_refused(self) -> None:
        """A runner report with one survivor is refused, naming it and writing nothing, until
        the survivor carries an answer; then the answer is kept beside it. A report whose
        mutant names a test outside the unit's Affects is refused as `--mutants` refuses it.
        A `--mutants` list beside the report is judged with it, and a record given neither is
        refused. Mutants: the survivor check skipped for a report; the answer dropped from the
        kept list; the Affects check skipped for a report; the list beside the report left
        unjudged, or kept with the report's; the record given neither list let through."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            _runner_project(root)
            report = _run_runner(root, [THREE_KILLED[0], ZERO_SURVIVES])
            ran = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(["killed", "survived"], [m["result"] for m in ran["mutants"]])
            r = _record_from(root, "US0101", report)
            self._refused(root, r, "zero reads negative", "answer")
            self.assertIsNone(critic.recorded_mutants(root, "US0101"))
            answer = "no criterion asks for the sign of zero; BG0001 files it"
            answered = _run_runner(root, [THREE_KILLED[0], {**ZERO_SURVIVES, "answer": answer}])
            r = _record_from(root, "US0101", answered)
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("killed 1, survived 1", critic.read_self_checks(root)[-1]["mutants"])
            kept = {m["mutant"]: m for m in critic.recorded_mutants(root, "US0101")}
            self.assertEqual(("survived", answer), (kept["zero reads negative"]["result"],
                                                     kept["zero reads negative"]["answer"]))
            # A mutant the runner cannot run, listed by hand beside the report, is judged with
            # its rows: unanswered it refuses the record, writing nothing; answered it is
            # counted, and the kept list stays the report's, the one the brief can replay.
            hand, by_hand = Path(d) / "by-hand.json", {
                "mutant": "sign of zero by hand", "test": SIGN, "result": "survived"}
            hand.write_text(json.dumps([by_hand]), encoding="utf-8")
            before = (root / LOG).read_text(encoding="utf-8")
            r = _record_from(root, "US0101", answered, "--mutants", str(hand))
            self.assertEqual(2, r.returncode, f"recorded:\n{r.stdout}{r.stderr}")
            self.assertIn("sign of zero by hand", r.stderr)
            self.assertEqual(before, (root / LOG).read_text(encoding="utf-8"))
            hand.write_text(json.dumps([{**by_hand, "answer": answer}]), encoding="utf-8")
            r = _record_from(root, "US0101", answered, "--mutants", str(hand))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("killed 1, survived 2", critic.read_self_checks(root)[-1]["mutants"])
            self.assertEqual(["add subtracts", "zero reads negative"],
                             [m["mutant"] for m in critic.recorded_mutants(root, "US0101")])
            before = (root / LOG).read_text(encoding="utf-8")
            r = subprocess.run([sys.executable, "-B", str(CRITIC), "self-check", "record",
                                "--unit", "US0101", "--claims", str(root.parent / "claims.json"),
                                "--root", str(root)], capture_output=True, text=True,
                               timeout=300, env=gitutil.git_env(), check=False)
            self.assertEqual(2, r.returncode, f"recorded with no mutants:\n{r.stdout}{r.stderr}")
            self.assertIn("--mutants-from REPORT.json", r.stderr)
            self.assertEqual(before, (root / LOG).read_text(encoding="utf-8"))
            outside = _rewrite_report(answered, lambda data: data["mutants"][0].update(
                test="tests/test_other.py::test_add"))
            before = (root / LOG).read_text(encoding="utf-8")
            r = _record_from(root, "US0101", outside)
            self.assertEqual(2, r.returncode, f"recorded:\n{r.stdout}{r.stderr}")
            self.assertIn("tests/test_other.py::test_add", r.stderr)
            self.assertIn("Affects", r.stderr)
            self.assertEqual(before, (root / LOG).read_text(encoding="utf-8"))

    def test_the_author_brief_names_the_runner_command_for_the_units_selectors(self) -> None:
        """The author section `sprint.py lane brief` prints names the runner command with the
        unit's id and both Verify selectors, and the record's `--mutants-from`; critic's own
        section prints that record command whole. The runbook's mutation row and the prompt
        template name the same runner command, and the runner's parser accepts it. Mutants:
        the selectors left out; the runner command missing the unit's id; the record command
        still `--mutants` only; a page naming a command the parser refuses."""
        import loader as _loader  # noqa: PLC0415
        mutation = _loader.load_script("mutation")
        sprint = _loader.load_script("sprint")
        from lib import run_state  # noqa: PLC0415 - on the path once sprint is loaded
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            _runner_project(root)
            run_state.open_run(root, batch=["US0101"], goal="g")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(0, sprint.main(
                    ["lane", "brief", "--units", "US0101", "--root", str(root)]))
            text = out.getvalue()
            section = text[text.index("AUTHOR SELF-CHECK"):text.index("Then, for US0101")]
            runner = next((ln.strip() for ln in section.splitlines()
                           if "mutation.py run --edits" in ln), "")
            self.assertTrue(runner, f"the lane brief names no runner command:\n{section}")
            args = mutation.build_parser().parse_args(shlex.split(runner)[1:])
            self.assertEqual(("US0101", "sdlc-studio/.local/lane/US0101-mutation-edits.json"),
                             (args.scope, args.report))
            for selector in (ADD, SIGN):
                self.assertIn(selector, section, "a Verify selector is missing from the section")
            self.assertIn("--mutants-from", section)
            # critic's own section, the one `critic.py brief` prints, carries the record command
            own = critic.author_self_check(root, "US0101")
            line = next(ln for ln in own.splitlines() if "self-check record --unit US0101" in ln)
            words = shlex.split(line[line.index("critic.py"):].rstrip("."))[1:]
            parsed = critic.build_parser().parse_args(words)
            ran = next(ln.strip() for ln in own.splitlines() if "mutation.py run --edits" in ln)
            self.assertEqual(shlex.split(ran)[-1], parsed.mutants_from,
                             "the record does not read the report the runner writes")
            self.assertIsNone(parsed.mutants)
            # the list by hand goes beside the report, as the lane brief and lane land have it
            self.assertIn("--mutants MUTANTS.json beside --mutants-from", " ".join(own.split()))
        skill = SCRIPTS.parent
        command = "mutation.py run --edits EDITS.json --scope <id> --report REPORT.json"
        for page in ("reference-sprint-toolchain.md", "reference-agent-prompt-template.md"):
            with self.subTest(page=page):
                body = " ".join((skill / page).read_text(encoding="utf-8").split())
                self.assertTrue(command in body, f"{page} does not name the runner command")
                args = mutation.build_parser().parse_args(
                    shlex.split(command.replace("<id>", "US0101"))[1:])
                self.assertEqual(("US0101", "EDITS.json"), (args.scope, args.edits))
                self.assertTrue("--mutants-from REPORT.json" in body, f"{page} names no record")

    def test_lane_land_records_through_the_runners_report(self) -> None:
        """Lane land records a hand-in holding the runner's report through `--mutants-from`,
        keeping the list and refusing an unanswered survivor; a hand-in holding only the
        mutants file records as before; a mutants file handed in beside the report is recorded
        and judged with it, so its unanswered survivor is refused; and the lane brief names
        the report under the name the landing reads. Mutants: the report passed to
        `--mutants`; the report ignored, so the land refuses for want of a mutants file; the
        mutants file dropped when the report is there; the brief naming another file name."""
        import loader as _loader  # noqa: PLC0415
        sprint = _loader.load_script("sprint")
        from lib import lanes  # noqa: PLC0415 - on the path once sprint is loaded
        self.assertEqual("US0101-mutation-edits.json", lanes.report_hand_in_name("us0101"))
        commands = "\n".join(sprint._lane_builder_commands("US0101", ["src/widget.py"], 2))
        self.assertIn(f"{sprint.LANE_HAND_IN}/US0101-mutation-edits.json", commands)
        self.assertRegex(commands, r"US0101-mutants\.json - [^\n]*recorded beside the report",
                         "the brief does not say the mutants file is recorded with the report")
        by_hand ={"mutant": "sign of zero by hand", "test": SIGN, "result": "survived"}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            _runner_project(root)
            claims, mutants = lanes.hand_in_names("US0101")
            report = _run_runner(root, THREE_KILLED)
            survivor = _run_runner(root, [THREE_KILLED[0], ZERO_SURVIVES], name="survivor")
            for label, files, refused, kept, counts in (
                    ("the runner's report", {"report": report}, None, 3, "killed 3, survived 0"),
                    ("an unanswered survivor", {"report": survivor}, "zero reads negative",
                     None, None),
                    ("a mutants file alone", {"mutants": KILLED}, None, None,
                     "killed 1, survived 0"),
                    ("an unanswered survivor by hand beside the report",
                     {"report": report, "mutants": [by_hand]}, "sign of zero by hand", None,
                     None),
                    ("an answered survivor by hand beside the report",
                     {"report": report, "mutants": [{**by_hand, "answer": "BG0001 files it"}]},
                     None, 3, "killed 3, survived 1")):
                with self.subTest(hand_in=label):
                    keep = Path(d) / label.replace(" ", "-")
                    keep.mkdir()
                    (keep / claims).write_text(json.dumps(_covered()), encoding="utf-8")
                    if "report" in files:
                        (keep / lanes.report_hand_in_name("US0101")).write_text(
                            files["report"].read_text(encoding="utf-8"), encoding="utf-8")
                    if "mutants" in files:
                        (keep / mutants).write_text(json.dumps(files["mutants"]),
                                                    encoding="utf-8")
                    rows = len(critic.read_self_checks(root))
                    good, line = lanes._record_and_brief(root, keep, "US0101", "builder-7")
                    self.assertEqual(refused is None, good, line)
                    if refused:
                        self.assertIn("REFUSED", line)
                        self.assertIn(refused, line)
                        self.assertEqual(rows, len(critic.read_self_checks(root)))
                        continue
                    self.assertEqual(counts, critic.read_self_checks(root)[-1]["mutants"])
                    listed = critic.recorded_mutants(root, "US0101")
                    self.assertEqual(kept, None if listed is None else len(listed))


if __name__ == "__main__":
    unittest.main()
