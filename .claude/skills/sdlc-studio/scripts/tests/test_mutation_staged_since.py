"""BG1768: under `--since`, `mutation.py run` judges a fully staged target in a private copy of
the index, and still refuses a target carrying unstaged or untracked work.

The CLI runs as a subprocess from the fixture's root, with no `--root`, as a builder runs it;
`main` resolves the root, so the repository's paths are absolute, as an in-place run's are. Every git call goes through the confined
environment of `gitutil`, and every subprocess gets its own `TMPDIR`, so a scratch copy left
behind is seen rather than mixed with another run's.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402

SCRIPT = HERE.parent / "mutation.py"
REVIEW = HERE.parent.parent / "reference-review.md"
TEST_CMD = f"{sys.executable} -m pytest -q -p no:cacheprovider tests"

BASE = "def clamp(x, lo, hi):\n    if x < lo:\n        return lo\n    return x\n"
STAGED = ("def clamp(x, lo, hi):\n    if x < lo:\n        return lo\n    if x > hi:\n"
          "        return hi\n    return x\n")
# Tests the lower bound and the middle, never the upper bound: line 5's mutant survives.
TESTS = ("import sys\nfrom pathlib import Path\n\n"
         "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
         "from pkg.calc import clamp  # noqa: E402\n\n\n"
         "def test_low():\n    assert clamp(-1, 0, 10) == 0\n\n\n"
         "def test_mid():\n    assert clamp(5, 0, 10) == 5\n")
OTHER = "def other(a):\n    if a:\n        return 1\n    return 2\n"


def _load():
    spec = importlib.util.spec_from_file_location("mutation", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mutation"] = mod
    spec.loader.exec_module(mod)
    return mod


def _fixture(top: Path, sub: str = "", ceiling: int | None = 2) -> Path:
    """A repository on `main` whose `pkg/calc.py` has lines 4 and 5 staged over the commit,
    with a staged test that leaves the upper bound untested. Returns the project root."""
    root = top / sub if sub else top
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "calc.py").write_text(BASE, encoding="utf-8")
    (root / "pkg" / "other.py").write_text(OTHER, encoding="utf-8")
    (top / ".gitignore").write_text("sdlc-studio/.local/\npkg/gen.py\n", encoding="utf-8")
    if ceiling is not None:
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / ".config.yaml").write_text(
            f"quality:\n  mutation_max: {ceiling}\n", encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "base"]):
        gitutil.git(args, top)
    (root / "pkg" / "calc.py").write_text(STAGED, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_calc.py").write_text(TESTS, encoding="utf-8")
    gitutil.git(["add", "-A"], top)
    return root


def _state(top: Path) -> tuple:
    """(index bytes, {path: digest} of every file outside .git and the ignored report folder,
    porcelain). The index is read first, and status is asked not to refresh it."""
    index = (top / ".git" / "index").read_bytes()
    files = {}
    for p in sorted(top.rglob("*")):
        rel = p.relative_to(top).as_posix()
        if rel == ".git" or rel.startswith(".git/") or "sdlc-studio/.local" in rel:
            continue
        if p.is_file():
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    status = gitutil.git(["--no-optional-locks", "status", "--porcelain", "--untracked-files=all"],
                         top, text=True).stdout
    return index, files, status


def _cli(cwd: Path, tmp: Path, *argv: str, **env: str) -> tuple[int, str, str]:
    """`mutation.py run <argv>` from `cwd`, with its own TMPDIR and any `env` added."""
    tmp.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([sys.executable, str(SCRIPT), "run", *argv], cwd=str(cwd),
                          env=gitutil.git_env(TMPDIR=str(tmp), **env), capture_output=True,
                          text=True, timeout=600)
    return proc.returncode, proc.stdout, proc.stderr


def _json(out: str) -> dict:
    return json.loads(out[out.index("{"):])


def _section(path: Path, anchor: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(n for n, ln in enumerate(lines) if ln.startswith("###") and anchor in ln)
    end = next(n for n in range(start + 1, len(lines)) if lines[n].startswith("##"))
    return lines[start:end]


class StagedSinceTests(unittest.TestCase):

    def test_a_staged_target_is_mutated_in_a_private_copy_of_the_index(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            before = _state(top)
            code, out, err = _cli(top, Path(d) / "tmp", "--files", "pkg/calc.py",
                                  "--since", "main", "--test", TEST_CMD)
            self.assertEqual(1, code, out + err)                 # one survivor, no refusal
            self.assertNotIn("TREE UNESTABLISHED", out + err)
            self.assertNotIn("SHARED TREE", out + err)
            calc = str(top / "pkg" / "calc.py")
            self.assertIn(f"SURVIVED  {calc}:5 ", out)
            self.assertEqual(before, _state(top), "the index, the tree or the status changed")
            report = json.loads((top / "sdlc-studio" / ".local" / "mutation-report.json")
                                .read_text(encoding="utf-8"))
            self.assertEqual([calc], report["targets"])
            self.assertEqual([4, 5], sorted(r["line"] for r in report["mutations"]))
            self.assertEqual({calc}, {r["file"] for r in report["mutations"]})
            self.assertEqual([5], [r["line"] for r in report["mutations"]
                                   if r["verdict"] == "survived"])
            self.assertNotIn("mutation_staged_", json.dumps(report))
        # At the default ceiling every mutant fits, and the diff counts still name the two
        # changed-line mutants: a line map left keyed to the copy's paths would count none.
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top, ceiling=None)
            code, out, err = _cli(top, Path(d) / "tmp", "--files", "pkg/calc.py", "--since",
                                  "main", "--test", TEST_CMD, "--format", "json", "--dry-run")
            s = _json(out)["summary"]
            self.assertEqual((2, 2, True), (s["diff_mutations"], s["diff_applied"],
                                            s["diff_covered"]), out + err)
            self.assertGreater(s["applied"], 2, "the remainder of the ceiling went unspent")

    def test_unstaged_and_untracked_work_is_still_refused_naming_the_staged_route(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            (top / "pkg" / "calc.py").write_text(STAGED + "# unstaged\n", encoding="utf-8")
            (top / "pkg" / "extra.py").write_text("def f(x):\n    return x\n", encoding="utf-8")
            for target in ("pkg/calc.py", "pkg/extra.py"):
                with self.subTest(target=target):
                    held = (top / target).read_bytes()
                    code, out, err = _cli(top, Path(d) / "tmp", "--files", target, "--since",
                                          "main", "--test", TEST_CMD, "--format", "json")
                    self.assertEqual(2, code, out + err)
                    report = _json(out)
                    self.assertEqual("uncommitted-surface", report["refusal_kind"])
                    self.assertEqual([], report["mutations"])
                    self.assertEqual(held, (top / target).read_bytes())
                    remedy = report["remedy"]
                    for words in ("git add", "re-run with `--since", "git worktree add",
                                  "commit or stash"):
                        self.assertIn(words, remedy)

    def test_the_report_states_isolation_and_names_repository_paths(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top, tmp = Path(d) / "repo", Path(d) / "tmp"
            _fixture(top)
            code, out, err = _cli(top, tmp, "--files", "pkg/calc.py", "--since", "main",
                                  "--test", TEST_CMD, "--format", "json")
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertIs(True, report["summary"]["tree"]["isolated"])
            self.assertIn("private copy of the index", report["summary"]["tree"]["why"])
            calc = str(top / "pkg" / "calc.py")
            self.assertEqual([calc], report["targets"])
            self.assertTrue(report["mutations"])
            self.assertEqual({calc}, {r["file"] for r in report["mutations"]})
            self.assertNotIn("mutation_staged_", out)
            self.assertEqual([], sorted(p.name for p in tmp.glob("mutation_staged_*")))

    def test_the_review_reference_states_the_staged_route(self) -> None:
        section = _section(REVIEW, "{#mutation-isolation}")
        body = " ".join(section)
        self.assertEqual(32, len(section), "the section's rewrite was not net zero")
        for pattern in (r"(?i)unstaged or untracked", r"--since", r"(?i)fully staged",
                        r"(?i)private copy of the index",
                        r"(?i)index version of every file[^.]*unstaged edit[^.]*not run",
                        r"(?i)isolated checkout", r"(?i)mutation\.py[^.]*refus",
                        r"(?i)uncommitted changes"):
            self.assertRegex(body, pattern)

    def test_without_since_a_staged_target_is_still_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            code, out, err = _cli(top, Path(d) / "tmp", "--files", "pkg/calc.py",
                                  "--test", TEST_CMD, "--format", "json")
            self.assertEqual(2, code, out + err)
            self.assertEqual("uncommitted-surface", _json(out)["refusal_kind"])

    def test_mixed_targets_take_the_copy_only_when_every_one_is_staged_or_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            tmp = Path(d) / "tmp"
            run = ("--since", "main", "--test", TEST_CMD, "--format", "json", "--dry-run")
            # staged plus clean committed: the copy route
            _code, out, err = _cli(top, tmp, "--files", "pkg/calc.py", "pkg/other.py", *run)
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertIn("private copy of the index", report["summary"]["tree"]["why"])
            # clean committed alone: run in place as before, not in a copy
            _code, out, err = _cli(top, tmp, "--files", "pkg/other.py", *run)
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertNotIn("private copy", report["summary"]["tree"]["why"])
            self.assertEqual(0, report["summary"]["diff_mutations"])  # still aimed at the diff
            # staged plus unstaged: refused
            (top / "pkg" / "other.py").write_text(OTHER + "# unstaged\n", encoding="utf-8")
            code, out, err = _cli(top, tmp, "--files", "pkg/calc.py", "pkg/other.py", *run)
            self.assertEqual(2, code, out + err)
            self.assertEqual("uncommitted-surface", _json(out)["refusal_kind"])

    def test_a_temp_directory_inside_a_repository_still_runs_the_copy(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            outer = Path(d) / "outer"
            outer.mkdir()
            gitutil.git(["init", "-q", "-b", "main"], outer)
            top = Path(d) / "repo"
            _fixture(top)
            head = gitutil.git(["rev-parse", "HEAD"], top, text=True).stdout.strip()
            _code, out, err = _cli(top, outer / "tmp", "--files", "pkg/calc.py", "--since",
                                   "main", "--test", TEST_CMD, "--format", "json", "--dry-run")
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertEqual(head, report["git_rev"])

    def test_an_inherited_index_variable_does_not_redirect_the_copy(self) -> None:
        """A git hook exports GIT_INDEX_FILE; the copy is still this repository's index."""
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            _code, out, err = _cli(top, Path(d) / "tmp", "--files", "pkg/calc.py", "--since",
                                   "main", "--test", TEST_CMD, "--format", "json", "--dry-run",
                                   GIT_INDEX_FILE=str(Path(d) / "elsewhere-index"))
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertEqual(2, report["summary"]["diff_mutations"])
            self.assertEqual([4, 5], sorted(r["line"] for r in report["mutations"]))

    def test_a_project_root_below_the_repository_top(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top, sub="proj")
            _code, out, err = _cli(top, Path(d) / "tmp", "--root", "proj", "--files",
                                   "pkg/calc.py", "--since", "main", "--test", TEST_CMD,
                                   "--format", "json", "--dry-run")
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            self.assertEqual([str(top / "proj" / "pkg" / "calc.py")], report["targets"])
            self.assertEqual(2, report["summary"]["diff_mutations"])
            self.assertEqual([4, 5], sorted(r["line"] for r in report["mutations"]))

    def test_an_ignored_target_is_unchecked_under_its_repository_path(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            (top / "pkg" / "gen.py").write_text("def g(a):\n    return a\n", encoding="utf-8")
            # An unstaged edit to a test, not a target: the copy runs the staged test instead,
            # so this red test never reaches the baseline.
            (top / "tests" / "test_calc.py").write_text(
                TESTS + "\n\ndef test_unstaged():\n    assert False\n", encoding="utf-8")
            _code, out, err = _cli(top, Path(d) / "tmp", "--files", "pkg/calc.py",
                                   "pkg/gen.py", "--since", "main", "--test", TEST_CMD,
                                   "--format", "json", "--dry-run")
            report = _json(out)
            self.assertFalse(report["refused"], out + err)
            gen = str(top / "pkg" / "gen.py")
            unread = [u for u in report["unchecked"] if u["file"] == gen]
            self.assertTrue(unread, report["unchecked"])
            self.assertIn(gen, unread[0]["reason"])
            self.assertNotIn("mutation_staged_", out)
            self.assertFalse((top / "sdlc-studio" / ".local" / "mutation-report.json").exists())

    def test_changed_lines_reads_the_index_when_cached(self) -> None:
        m = _load()
        with tempfile.TemporaryDirectory() as d:
            top = Path(d) / "repo"
            _fixture(top)
            (top / "pkg" / "calc.py").write_text(STAGED + "X = 1\n", encoding="utf-8")
            (top / "pkg" / "new.py").write_text("Y = 2\n", encoding="utf-8")
            with unittest.mock.patch.dict("os.environ", gitutil.git_env(), clear=True):
                cached = m.changed_lines(top, "main", cached=True)
                worktree = m.changed_lines(top, "main")
            calc, new = str(top / "pkg" / "calc.py"), str(top / "pkg" / "new.py")
            self.assertEqual({4, 5}, cached[calc])
            self.assertNotIn(new, cached)
            self.assertEqual({4, 5, 7}, worktree[calc])           # the control
            self.assertIn(new, worktree)

    def test_staged_only_is_false_when_git_cannot_run(self) -> None:
        m = _load()
        with unittest.mock.patch.object(m.subprocess, "run", side_effect=OSError("no git")):
            self.assertIs(False, m.staged_only(Path("."), ["pkg/calc.py"]))


if __name__ == "__main__":
    unittest.main()
