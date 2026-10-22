"""BG1117: an author's self-check record is bound to the unit's own change, not to whole files.

A record keeps the digest of the unit's Affects content and the commit it was taken at. The brief
gate admits a row whose digest matches that content as it stands, or as it would stand had no
other unit committed to those files since: a commit whose subject names a unit id that is not
this unit's is set aside, and nothing else is, so the author's own further edit, committed or
not, still reads as a record of an earlier diff. The review tooling's own writes (the self-check
log, the verdict logs, the runtime notes under `sdlc-studio/.local`) are outside the digest, so
recording a self-check or a verdict, or taking a brief, never stales a record.

Every case drives `critic.py` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
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

A, B = "US0101", "US0102"
SHARED = "src/shared.py"
A_AFFECTS = f"{SHARED}, tests/test_shared.py, changelog.d/{A}.md"
LOG = Path("sdlc-studio") / "reviews" / "author-self-checks.md"
STALE = "is stale"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _story(root: Path, unit: str, affects: str) -> None:
    _write(root, f"sdlc-studio/stories/{unit}-shared.md",
           f"# {unit}: shared\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _project(root: Path, a_affects: str = A_AFFECTS, repo: bool = True) -> None:
    """A and B both declaring `src/shared.py`, a QA seat card, `review.author_self_check:
    block`, and (with `repo`) one commit holding it all."""
    _write(root, SHARED, "def s():\n    return 1\n")
    _write(root, "src/other.py", "def o():\n    return 1\n")
    _write(root, "tests/test_shared.py", "def test_s():\n    assert True\n")
    _write(root, "sdlc-studio/personas/seats/qa.md",
           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    _write(root, "sdlc-studio/.config.yaml", "review:\n  author_self_check: block\n")
    _story(root, A, a_affects)
    _story(root, B, f"{SHARED}, changelog.d/{B}.md")
    if repo:
        gitutil.git(["init", "-q"], root)
        _commit(root, f"feat({A}): the shared module")


def _commit(root: Path, subject: str, rel: str | None = None, body: str | None = None) -> None:
    """Write `body` to `rel` (when given), then commit every change under `subject`."""
    if rel is not None:
        _write(root, rel, body or "")
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "--no-verify", "-m", subject], root)


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _record(root: Path, scratch: Path, unit: str = A) -> None:
    """A self-check of `unit` through the shipped command; the two files live outside the
    project, so no commit carries them."""
    claims = [{"surface": "commit message", "claim": "s returns 1", "ruling": "TRUE"},
              {"surface": f"changelog.d/{unit}.md", "claim": "s is new", "ruling": "TRUE"}]
    mutants = [{"mutant": "s returns 2", "test": "tests/test_shared.py::test_s",
                "result": "killed"}]
    (scratch / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
    (scratch / "mutants.json").write_text(json.dumps(mutants), encoding="utf-8")
    r = _cli(root, "self-check", "record", "--unit", unit, "--claims",
             str(scratch / "claims.json"), "--mutants", str(scratch / "mutants.json"),
             "--author", "builder")
    assert r.returncode == 0, r.stderr


def _brief(root: Path, unit: str = A) -> subprocess.CompletedProcess:
    return _cli(root, "brief", "--unit", unit, "--seat", "qa", "--tier", "full")


class LaterUnitTests(unittest.TestCase):

    def setUp(self) -> None:
        self._dirs = [tempfile.TemporaryDirectory() for _ in range(2)]
        self.root, self.scratch = (Path(d.name) for d in self._dirs)

    def tearDown(self) -> None:
        for d in self._dirs:
            d.cleanup()

    def _admitted(self, r: subprocess.CompletedProcess, why: str) -> None:
        self.assertEqual(0, r.returncode, f"{why}:\n{r.stderr}")
        self.assertTrue(r.stdout.strip(), f"{why}: no brief on stdout")
        self.assertNotIn(STALE, r.stderr, why)

    def _refused(self, r: subprocess.CompletedProcess, why: str) -> None:
        self.assertEqual(2, r.returncode, f"{why}:\n{r.stderr}")
        self.assertEqual("", r.stdout, f"{why}: a refused brief reached stdout")
        self.assertIn(STALE, r.stderr, why)

    def _row(self) -> dict:
        return critic.read_self_checks(self.root)[-1]

    def _moved(self) -> None:
        """The guard against a vacuous fixture: B's commit moved A's Affects content, so the
        content as it stands no longer matches the record and only the own-change view can."""
        self.assertNotEqual(self._row()["digest"], critic.affects_digest(self.root, A),
                            "B's commit did not move the content, so the case proves nothing")

    def test_a_later_units_commit_does_not_stale_the_record(self) -> None:
        """AC1. Mutants: the gate comparing whole-file content only, so B's commit stales A's
        record; a commit naming this unit read as another's, so A's own committed edit is set
        aside; an uncommitted edit on top of B's commit read through to the content before it.
        The row keeps the commit it was taken at, in its Digest cell."""
        _project(self.root)
        head = gitutil.git(["rev-parse", "--short=12", "HEAD"], self.root,
                           text=True).stdout.strip()
        _record(self.root, self.scratch)
        row = self._row()
        self.assertEqual(head, row["commit"], "the record did not keep the commit it was taken at")
        self.assertIn(f"| {row['digest']} at {head} |",
                      (self.root / LOG).read_text(encoding="utf-8"))
        self._admitted(_brief(self.root), "a fresh record was refused")
        _commit(self.root, f"feat({B}): shared grows", SHARED,
                "def s():\n    return 1\n\n\ndef t():\n    return 2\n")
        self._moved()
        self._admitted(_brief(self.root), "B's commit to a shared file staled A's record")
        _write(self.root, SHARED, "def s():\n    return 3\n\n\ndef t():\n    return 2\n")
        self._refused(_brief(self.root), "A's uncommitted edit after B's commit was admitted")
        _commit(self.root, f"fix({A}): s returns 3")
        self._refused(_brief(self.root), "A's committed edit was admitted")

    def test_the_review_tools_own_writes_do_not_stale_the_record(self) -> None:
        """AC2. Mutants: either log left in the digest, so the record's own append (or a verdict
        recorded for another unit) stales it; the exclusion applied to a declared file but not
        to a declared directory's members; `brief`'s fingerprint note under `.local` left in, so
        a unit declaring `sdlc-studio/` is refused at its second brief. The positive control:
        an edit to another file the declared directory holds still stales the record."""
        logs = "sdlc-studio/reviews/author-self-checks.md, sdlc-studio/reviews/critic-verdicts.md"
        latest = "sdlc-studio/reviews/LATEST.md"
        for declared, other in ((logs, SHARED), ("sdlc-studio/reviews", latest),
                                ("sdlc-studio/", latest)):
            with self.subTest(declared=declared), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, f"{A_AFFECTS}, {declared}", repo=False)
                _write(root, "sdlc-studio/reviews/LATEST.md", "# Latest\n")
                _record(root, self.scratch)
                self._admitted(_brief(root), "the record's own append staled it")
                r = _cli(root, "record", "--unit", B, "--verdict", "APPROVE", "--reviewer",
                         "qa seat", "--author", "builder", "--issues", "none")
                self.assertEqual(0, r.returncode, r.stderr)
                self._admitted(_brief(root), "another unit's verdict staled the record")
                _record(root, self.scratch)
                self._admitted(_brief(root), "a second record or brief staled the record")
                _write(root, other, "# Latest\n\nedited by the author\n")
                self._refused(_brief(root), f"an edit to {other} was admitted")

    def test_a_commit_not_named_for_another_unit_stales_the_record(self) -> None:
        """Mutants: a subject naming no unit id read as another unit's, so an unattributed edit
        is set aside; a subject naming this unit beside another read as the other's alone."""
        for subject in ("tidy the shared module", f"fix({B}): shared, with {A}'s fix"):
            with self.subTest(subject=subject), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                _record(root, self.scratch)
                _commit(root, subject, SHARED, "def s():\n    return 4\n")
                self._refused(_brief(root), f"a commit {subject!r} was set aside")

    def test_a_record_of_uncommitted_work_survives_its_own_commit(self) -> None:
        """A record taken before the author commits: the author's commit of the recorded content,
        then B's commit on top. Mutant: the walk stopping at the record's commit rather than
        at the author's own later commit, so the recorded edit reads as missing."""
        _project(self.root)
        _write(self.root, SHARED, "def s():\n    return 5\n")
        _record(self.root, self.scratch)
        _commit(self.root, f"feat({A}): s returns 5")
        _commit(self.root, f"feat({B}): shared grows", SHARED,
                "def s():\n    return 5\n\n\ndef t():\n    return 2\n")
        self._moved()
        self._admitted(_brief(self.root), "A's own commit of the recorded edit staled it")

    def test_another_units_files_in_a_declared_directory_do_not_stale_the_record(self) -> None:
        """A declares the directory `src/`; B adds one file under it and deletes another.
        Mutants: the paths only another unit touched left out of the view, so B's deletion reads
        as A's; a path absent at the record read as empty rather than absent. The control: a
        file the author adds afterwards, never committed, stales the record."""
        _project(self.root, f"src/, tests/test_shared.py, changelog.d/{A}.md")
        _record(self.root, self.scratch)
        _write(self.root, "src/added.py", "x = 1\n")
        (self.root / "src/other.py").unlink()
        _commit(self.root, f"feat({B}): add one module, drop another")
        self._moved()
        self._admitted(_brief(self.root), "B's files under A's directory staled A's record")
        _write(self.root, "src/mine.py", "y = 2\n")
        self._refused(_brief(self.root), "a file the author added was admitted")

    def test_a_record_off_the_line_of_history_reads_the_content_as_it_stands(self) -> None:
        """A record taken on a branch HEAD does not contain is judged on the content as it
        stands, as is a row written before the commit was kept. Mutant: the ancestor check
        dropped, so B's commit on main is set aside against a side branch's content that main
        never received."""
        _project(self.root)
        gitutil.git(["checkout", "-q", "-b", "side"], self.root)
        _commit(self.root, f"feat({A}): s returns 6", SHARED, "def s():\n    return 6\n")
        _record(self.root, self.scratch)
        gitutil.git(["checkout", "-q", "-"], self.root)
        _commit(self.root, f"feat({B}): shared grows", SHARED,
                "def s():\n    return 1\n\n\ndef t():\n    return 2\n")
        self._refused(_brief(self.root), "a record from a branch HEAD lacks was admitted")
        digest = critic.affects_digest(self.root, A)
        with (self.root / LOG).open("a", encoding="utf-8") as fh:
            fh.write(f"| {A} | builder | 2026-10-22 | TRUE 2, FALSE 0, UNVERIFIABLE 0 | "
                     f"killed 1, survived 0 | {digest} |\n")
        self.assertEqual(("", digest), (self._row()["commit"], self._row()["digest"]))
        self._admitted(_brief(self.root), "a row without a commit matching the content")
        _commit(self.root, f"feat({B}): shared grows again", SHARED, "def s():\n    return 7\n")
        self._refused(_brief(self.root), "a row without a commit survived B's commit")


if __name__ == "__main__":
    unittest.main()
