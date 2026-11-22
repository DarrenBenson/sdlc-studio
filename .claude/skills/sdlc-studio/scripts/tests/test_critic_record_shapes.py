"""BG1229: critic.py's self-check and verdict records accept the shapes authors and reviewers
write, and `record` validates a verdict without writing it.

Three frictions from run six, each costing a hand-fix or an agent resume:

- `self-check record` refused a ruling written `TRUE: <evidence>`. It now reads the ruling word
  before the colon and keeps the evidence after it as the claim's `evidence` field; a ruling
  with prose after the word and no colon (`TRUE in substance`) is still refused.
- `record` had no dry run, so a reviewer could not check a verdict before handing it back.
  `record --dry-run` runs every check `record` makes and writes nothing.
- the verdict ledger escaped underscores and not asterisks, so a verdict naming `test_lean_`*
  tripped markdownlint (MD037). A bare asterisk outside a code span is now escaped too.

Each case drives `critic.py` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import shutil
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
REPO = Path(__file__).resolve().parents[5]
critic = loader.load_script("critic")
AFFECTS = "src/widget.py, tests/test_widget.py, changelog.d/US0101.md"
KILLED = [{"mutant": "w returns 2", "test": "tests/test_widget.py::test_w", "result": "killed"}]


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path) -> None:
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "tests/test_widget.py", "def test_w():\n    assert True\n")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           f"# US0101: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {AFFECTS}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _cli(root: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          input=stdin, check=False)


def _self_check(root: Path, claims: list[dict]) -> subprocess.CompletedProcess:
    cpath, mpath = root / "claims.json", root / "mutants.json"
    cpath.write_text(json.dumps(claims), encoding="utf-8")
    mpath.write_text(json.dumps(KILLED), encoding="utf-8")
    return _cli(root, "self-check", "record", "--unit", "US0101", "--claims", str(cpath),
                "--mutants", str(mpath))


def _snapshot(root: Path) -> dict[str, bytes]:
    """Every file under `root` with its bytes, so a write anywhere shows."""
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def _markdownlint() -> str | None:
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [REPO]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SCRIPTS,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


class RulingWithEvidenceTests(unittest.TestCase):

    def test_a_ruling_with_its_evidence_records_as_the_ruling(self) -> None:
        """AC1, part one. Mutants: the colon form refused as outside the vocabulary; the word
        read with its colon kept (`TRUE:`), so the claim counts as unruled; every ruling read
        as TRUE, so `UNVERIFIABLE: no command settles it` counts as checked."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            claims = [{"surface": "commit message", "claim": "w returns 1",
                       "ruling": "TRUE: grep finds return 1 at src/widget.py:2"},
                      {"surface": "changelog.d/US0101.md", "claim": "w is new",
                       "ruling": "true:it was absent at the base"},
                      {"surface": "docstrings", "claim": "w is pure",
                       "ruling": "UNVERIFIABLE: no command settles purity"}]
            r = _self_check(root, claims)
            self.assertEqual(0, r.returncode, r.stderr)
            row = critic.read_self_checks(root)[-1]
            self.assertEqual("TRUE 2, FALSE 0, UNVERIFIABLE 1", row["claims"])

    def test_the_evidence_is_kept_as_a_field(self) -> None:
        """AC1, part one: the evidence after the colon is kept, not dropped with the word, and
        the claim's other fields are kept as given. A bare ruling carries no evidence."""
        claims = [{"surface": "commit message", "claim": "w returns 1",
                   "ruling": "TRUE:  grep finds it ", "extra": 1},
                  {"surface": "docstrings", "claim": "w is pure", "ruling": "FALSE"}]
        got = critic.ruled_claims(claims)
        self.assertEqual({"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE",
                          "evidence": "grep finds it", "extra": 1}, got[0])
        self.assertEqual(("FALSE", ""), (got[1]["ruling"], got[1]["evidence"]))
        self.assertEqual("TRUE:  grep finds it ", claims[0]["ruling"], "the input was changed")
        self.assertEqual(("Unverifiable", "x: y"), critic.split_ruling("Unverifiable : x: y"))
        self.assertEqual(("TRUE", ""), critic.split_ruling(" TRUE "))
        self.assertEqual(("TRUE in substance", ""), critic.split_ruling("TRUE in substance"))

    def test_a_false_ruling_with_evidence_is_still_refused_naming_it(self) -> None:
        """A FALSE claim is corrected before review whatever follows it, and the refusal names
        the evidence the author gave."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            claims = [{"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE"},
                      {"surface": "changelog.d/US0101.md", "claim": "w caches",
                       "ruling": "FALSE: nothing is cached"}]
            r = _self_check(root, claims)
            self.assertEqual(2, r.returncode)
            self.assertIn("is ruled FALSE", r.stderr)
            self.assertIn("nothing is cached", r.stderr)
            self.assertEqual([], critic.read_self_checks(root))

    def test_prose_after_the_word_without_a_colon_is_still_refused(self) -> None:
        """The colon is the separator: `TRUE in substance` hedges the ruling and stays refused,
        as does a word outside the vocabulary before a colon."""
        for ruling in ("TRUE in substance", "MAYBE: it looked fine", "TRUE - grep finds it"):
            with self.subTest(ruling=ruling), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                claims = [{"surface": "commit message", "claim": "w", "ruling": ruling},
                          {"surface": "changelog.d/US0101.md", "claim": "w", "ruling": "TRUE"}]
                r = _self_check(root, claims)
                self.assertEqual(2, r.returncode)
                self.assertIn(f"has the ruling {ruling!r}", r.stderr)
                self.assertEqual([], critic.read_self_checks(root))


class RecordDryRunTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _project(self.root)

    def _record(self, *args: str) -> subprocess.CompletedProcess:
        return _cli(self.root, "record", "--unit", "US0101", "--reviewer", "qa-seat",
                    "--author", "eng-seat", *args)

    def test_a_valid_verdict_is_checked_and_nothing_is_written(self) -> None:
        """AC1, part two. Mutants: the dry run writing the row (or the review base, or the
        ledger's header); the dry run skipping the checks it stands in for."""
        before = _snapshot(self.root)
        r = self._record("--verdict", "approve", "--dry-run")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("US0101 APPROVE would be recorded", r.stdout)
        self.assertIn("nothing was written", r.stdout)
        self.assertEqual(before, _snapshot(self.root))
        r = self._record("--verdict", "approve")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertNotEqual(before, _snapshot(self.root), "premise: a real record writes")

    def test_a_verdict_file_is_checked_and_nothing_is_written(self) -> None:
        """The reviewer's own file, read as `record --from-verdict` reads it."""
        verdict = self.root / "verdict.txt"
        verdict.write_text("VERDICT: REJECT\nISSUES: [new] w is wrong\nBLOCKING: [new] w is "
                           "wrong\n", encoding="utf-8")
        before = _snapshot(self.root)
        r = self._record("--from-verdict", str(verdict), "--dry-run")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("US0101 REJECT would be recorded", r.stdout)
        self.assertEqual(before, _snapshot(self.root))

    def test_a_verdict_record_would_refuse_is_refused_by_the_dry_run(self) -> None:
        """Each refusal a record makes before or at its write, under the dry run: an untagged
        finding, a cell markdownlint would refuse (an odd backtick), an unknown unit, and a
        round past the review cap. Nothing is written for any."""
        cases = {
            "an untagged finding": (("--verdict", "reject", "--issues", "w is wrong"),
                                    "carry no origin"),
            "an odd backtick": (("--verdict", "reject", "--issues", "[new] `w is wrong"),
                                "odd number of backticks"),
        }
        for label, (args, said) in cases.items():
            with self.subTest(case=label):
                before = _snapshot(self.root)
                r = self._record(*args, "--dry-run")
                self.assertEqual(2, r.returncode, f"{label} passed the dry run")
                self.assertIn(said, r.stderr)
                self.assertEqual(before, _snapshot(self.root))
        before = _snapshot(self.root)
        r = _cli(self.root, "record", "--unit", "US9999", "--verdict", "approve", "--reviewer",
                 "qa-seat", "--author", "eng-seat", "--dry-run")
        self.assertEqual(2, r.returncode)
        self.assertIn("resolve to no artefact", r.stderr)
        self.assertEqual(before, _snapshot(self.root))

    def test_a_round_past_the_cap_is_refused_by_the_dry_run(self) -> None:
        """The review cap is judged as the record judges it: two REJECT rounds recorded, a
        third is refused by the dry run with nothing written."""
        for _ in range(2):
            r = self._record("--verdict", "reject", "--issues", "[new] w is wrong")
            self.assertEqual(0, r.returncode, r.stderr)
        before = _snapshot(self.root)
        r = self._record("--verdict", "approve", "--dry-run")
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("refused for US0101", r.stderr)
        self.assertEqual(before, _snapshot(self.root))


class LedgerAsteriskTests(unittest.TestCase):

    def test_a_verdict_naming_a_glob_between_spans_writes_a_row_markdownlint_passes(self) -> None:
        """AC1, part three: `a_`*`_b` puts a bare asterisk between two code spans; two of them
        in one row pair into emphasis unless each is escaped. Mutant: the asterisk left bare."""
        mdl = _markdownlint()
        if mdl is None:
            self.skipTest("markdownlint is not installed (run `npm install`)")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            issues = "[new] `a_`*`_b` and `test_lean_`*`_x` both match"
            r = _cli(root, "record", "--unit", "US0101", "--verdict", "reject", "--reviewer",
                     "qa-seat", "--author", "eng-seat", "--issues", issues)
            self.assertEqual(0, r.returncode, r.stderr)
            ledger = critic.verdicts_path(root)
            self.assertIn("`a_`\\*`_b`", ledger.read_text(encoding="utf-8"))
            lint = subprocess.run([mdl, "--config", str(REPO / ".markdownlint.json"),
                                   str(ledger)], capture_output=True, text=True, check=False,
                                  timeout=300)
            self.assertEqual(0, lint.returncode, lint.stdout + lint.stderr)
            got = critic.parse_findings(critic.read_verdicts(root)[-1]["issues"])
            self.assertEqual(["`a_`*`_b` and `test_lean_`*`_x` both match"],
                             [f["text"] for f in got])


if __name__ == "__main__":
    unittest.main()
