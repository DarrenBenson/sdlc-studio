"""US1011: a review brief names the file the reviewer writes its verdict block to.

After the unchanged return contract, `critic.py brief` prints an absolute path under the main
checkout's `sdlc-studio/reviews/verdicts/<UNIT>/`, unique per briefing, and the `UNIT:` and
`BRIEF:` lines the file opens with; the footer's record command reads that path with
`--from-verdict`. The path and its header lines stay out of the fingerprint, so two briefs of the
same scope share one, and a rejoinder names a fresh file rather than the earlier one.

Every case drives `critic.py` through its entry point in a throwaway project, from a working
directory that is not the project root.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

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


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path) -> None:
    """One story with a QA seat card, in a throwaway project."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    _write(root, f"sdlc-studio/stories/{UNIT}-widget.md",
           f"# {UNIT}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _critic(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _brief(cwd: Path, root: Path, *extra: str) -> subprocess.CompletedProcess:
    r = _critic(cwd, "brief", "--unit", UNIT, "--seat", "qa", *extra, "--root", str(root))
    assert r.returncode == 0, r.stderr
    return r


def _named(stdout: str) -> tuple[Path, str]:
    """The verdict path the brief names after its return contract, and the stem its BRIEF line
    gives. The two header lines must be the last two lines of the brief, in order."""
    tail = stdout[stdout.rindex(critic._RETURN_CONTRACT) + len(critic._RETURN_CONTRACT):]
    lines = [ln.strip() for ln in tail.splitlines() if ln.strip()]
    paths = [ln for ln in lines if ln.endswith(".txt") and "/verdicts/" in ln]
    assert len(paths) == 1, f"{len(paths)} verdict paths after the contract:\n{tail}"
    assert lines[-2:] == [f"UNIT: {UNIT}", f"BRIEF: {Path(paths[0]).stem}"], tail
    return Path(paths[0]), lines[-1].split(": ", 1)[1]


def _footer(stderr: str) -> list[str]:
    """The record command the footer prints, as argv after `critic.py`, without its `...`."""
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", stderr, re.M)
    assert m, f"no record command in the footer:\n{stderr}"
    return [a for a in shlex.split(m.group(1)) if a != "..."]


def _fingerprint(stderr: str) -> str:
    m = re.search(r"^brief fingerprint: (\S+)$", stderr, re.M)
    assert m, stderr
    return m.group(1)


def _record(cwd: Path, root: Path, argv: list[str]) -> subprocess.CompletedProcess:
    r = _critic(cwd, *argv, "--reviewer", "qa-seat", "--author", "builder", "--root", str(root))
    assert r.returncode == 0, r.stderr
    return r


class BriefVerdictPathTests(unittest.TestCase):

    def test_the_brief_names_an_absolute_verdict_path_and_records_from_it(self) -> None:
        """AC1. Mutants: the path printed relative to the working directory; the return contract
        parameterised with the path, which breaks the neutrality check's exact strip; the footer
        still printing `--verdict <APPROVE|REJECT>`."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root = Path(d)
            _project(root)
            r = _brief(Path(elsewhere), root)
            self.assertIn(critic._RETURN_CONTRACT, r.stdout, "the return contract changed")
            self.assertEqual([], critic.neutrality_violations(r.stdout))
            path, stem = _named(r.stdout)
            self.assertTrue(path.is_absolute(), f"{path} is not absolute")
            self.assertEqual(root.resolve() / "sdlc-studio" / "reviews" / "verdicts" / UNIT,
                             path.parent)
            self.assertTrue(path.parent.is_dir(), "the unit's verdict directory was not made")
            self.assertFalse(path.exists(), "the brief wrote the reviewer's file itself")
            fp = _fingerprint(r.stderr)
            self.assertTrue(stem.startswith(f"{fp}-"), stem)
            argv = _footer(r.stderr)
            self.assertNotIn("--verdict", argv)
            self.assertEqual(str(path), argv[argv.index("--from-verdict") + 1])
            self.assertEqual(fp, argv[argv.index("--brief") + 1])
            # the reviewer's file, as the brief told it to write it
            path.write_text(f"UNIT: {UNIT}\nBRIEF: {stem}\nVERDICT: APPROVE\nISSUES: none\n"
                            "BLOCKING: none\n", encoding="utf-8")
            _record(Path(elsewhere), root, argv)
            row = critic.read_verdicts(root)[-1]
            self.assertEqual((UNIT, "APPROVE", fp), (row["unit"], row["verdict"], row["brief"]))
            noted = critic._noted_row(root, UNIT, fp)
            self.assertEqual(str(path), noted.get("verdict_file"),
                             "the brief note does not record the issued path")

    def test_two_briefs_share_a_fingerprint_and_not_a_path(self) -> None:
        """AC2. Mutant: the path or its header lines left inside the fingerprinted text, so each
        brief's fingerprint differs and a record warns about a scope that has not changed."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            first, second = _brief(cwd, root), _brief(cwd, root)
            self.assertNotEqual(_named(first.stdout)[0], _named(second.stdout)[0])
            fp = _fingerprint(first.stderr)
            self.assertEqual(fp, _fingerprint(second.stderr))
            for n, r in enumerate((first, second)):
                saved = cwd / f"brief-{n}.txt"
                saved.write_text(r.stdout, encoding="utf-8")
                rec = _record(cwd, root, ["record", "--unit", UNIT, "--verdict", "APPROVE",
                                          "--brief-file", str(saved), "--tier",
                                          critic.tier_for(root, UNIT)])
                self.assertEqual(fp, critic.read_verdicts(root)[-1]["brief"], rec.stderr)
                self.assertNotIn("changed since", rec.stderr)

    def test_a_rejoinder_never_names_an_earlier_rounds_file(self) -> None:
        """AC3. Mutant: a path derived from the unit and seat alone, so the second reviewer
        overwrites the first one's file in place."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            first = _brief(cwd, root)
            path, stem = _named(first.stdout)
            path.write_text(f"UNIT: {UNIT}\nBRIEF: {stem}\nVERDICT: REJECT\n"
                            "ISSUES: [new] w returns 1 (src/widget.py:2)\n"
                            "BLOCKING: w returns 1\n", encoding="utf-8")
            _record(cwd, root, _footer(first.stderr))
            self.assertEqual("REJECT", critic.read_verdicts(root)[-1]["verdict"])
            again = _brief(cwd, root, "--rejoinder", str(path))
            self.assertIn("w returns 1", again.stdout, "control: the prior verdict is quoted")
            new_path, new_stem = _named(again.stdout)
            self.assertNotEqual(path, new_path)
            self.assertEqual(path.parent, new_path.parent)
            for stream in (again.stdout, again.stderr):
                self.assertNotIn(str(path), stream)
                self.assertNotIn(stem, stream)
            argv = _footer(again.stderr)
            self.assertEqual(str(new_path), argv[argv.index("--from-verdict") + 1])
            self.assertTrue(new_stem.startswith(f"{_fingerprint(again.stderr)}-"))

    def test_a_linked_worktree_brief_names_the_main_checkout(self) -> None:
        """A brief printed in a linked worktree names a file in the main checkout, where the
        recorder runs. Mutant: the path taken from `--root` unresolved."""
        with tempfile.TemporaryDirectory() as d:
            main, linked = Path(d) / "main", Path(d) / "linked"
            _project(main)
            gitutil.git(["init", "-q"], main)
            gitutil.git(["add", "-A"], main)
            gitutil.git(["commit", "-qm", "fixture"], main)
            gitutil.git(["worktree", "add", "-q", str(linked)], main)
            path, _ = _named(_brief(Path(d), linked).stdout)
            self.assertEqual(main.resolve() / "sdlc-studio" / "reviews" / "verdicts" / UNIT,
                             path.parent)


if __name__ == "__main__":
    unittest.main()
