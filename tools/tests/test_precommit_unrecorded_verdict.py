"""BG1492: the pre-commit hook refuses a staged verdict file no recorded review row cites.

In run fourteen an orchestrator committed accepted units' records with `git add -A sdlc-studio/`
while a reviewer was still writing a verdict, and the half-written file went into the commit: a
verdict file being written has no marker a commit can see. The hook's gate lane now asks
`critic.py show --unrecorded-staged` whenever the commit stages a file under
`sdlc-studio/reviews/verdicts/`, and refuses one whose staged bytes no review row cites.

DRIVEN, not read: the real hooks run in the hermetic fixture `test_precommit_window_guard.py`
builds, every other hook-invoked script stubbed to pass, with the real `critic.py` linked in.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_precommit_window_guard as _wg  # noqa: E402 - imported as a module, not collected

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
sys.path.insert(0, str(SCRIPTS / "tests"))
import loader  # noqa: E402

critic = loader.load_script("critic")
REL = "sdlc-studio/reviews/verdicts/US0001/abc123def456-0a1b2c3d.txt"
BODY = "UNIT: US0001\nBRIEF: abc123def456-0a1b2c3d\nVERDICT: APPROVE\nISSUES: none\n"


def _repo(tmp: Path) -> Path:
    """The hermetic hook fixture, with the real `critic.py` in its skill scripts folder (it
    resolves its siblings from where it really lives)."""
    root = _wg.WindowGuardTests("run")._repo(tmp)
    link = root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "critic.py"
    if not link.exists():
        link.symlink_to(SCRIPTS / "critic.py")
    return root


def _commit(root: Path, message: str) -> tuple[int, str]:
    """`git add -A` of the records, as the incident did, then the commit through the hooks."""
    _wg._git(root, "add", "-A")
    out = subprocess.run(["git", "-C", str(root), "commit", "-m", message],
                         capture_output=True, text=True, env=_wg._clean_env(), timeout=600)
    return out.returncode, out.stdout + out.stderr


def _head(root: Path) -> str:
    return _wg._git(root, "rev-parse", "HEAD").stdout.strip()


def _listed_keys(root: Path) -> list[str]:
    listed = subprocess.run([str(root / ".githooks" / "pre-commit"), "--list"], cwd=root,
                            capture_output=True, text=True, check=True, timeout=60).stdout
    return [ln.split("\t", 1)[0] for ln in listed.splitlines() if "\t" in ln]


class UnrecordedVerdictLaneTests(unittest.TestCase):

    def test_a_commit_holding_an_unrecorded_verdict_is_refused(self) -> None:
        """AC3. Mutants: the check existing in critic.py with no hook lane calling it; the lane
        advisory (its failure not failing the lane); the refusal on a lane `--list` does not
        print. The positive control: the same file, once a review row cites its bytes,
        commits."""
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before = _head(root)
            path = root / REL
            path.parent.mkdir(parents=True)
            path.write_text(BODY, encoding="utf-8")
            rc, out = _commit(root, "docs: the accepted units' records")
            self.assertNotEqual(0, rc, f"an unrecorded verdict file was committed:\n{out}")
            self.assertEqual(before, _head(root), "something was committed")
            self.assertIn(f"{REL}: no recorded review row cites it", out)
            self.assertIn("critic.py record --unit US0001", out)
            failed = [ln.split("FAIL", 1)[1].strip() for ln in out.splitlines()
                      if ln.strip().startswith("FAIL")]
            self.assertTrue(failed, f"no lane reported the refusal:\n{out}")
            self.assertTrue(set(failed) <= set(_listed_keys(root)),
                            f"the refusing lane {failed} is not one `--list` prints")

            critic._write_verdict(root, "US0001", "APPROVE", "qa-seat", "eng-seat", "",
                                  "delivery", "abc123def456", None, False,
                                  source=critic.source_cell(REL, BODY.encode()))
            rc, out = _commit(root, "docs: the accepted units' records")
            self.assertEqual(0, rc, f"a verdict file its row cites was refused:\n{out}")
            self.assertNotEqual(before, _head(root))


if __name__ == "__main__":
    unittest.main()
