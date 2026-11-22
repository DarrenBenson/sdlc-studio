"""BG1701: a reviewer's verdict files leave the author's self-check digest unmoved.

The self-check digest leaves out what the review tooling itself writes while a unit is reviewed
(the self-check log, the verdict ledger, the kept mutant lists and the runtime notes). The verdict
files a reviewer writes under `sdlc-studio/reviews/verdicts/<unit>/`, each one named by a brief,
were not left out, so for a unit whose Affects declares `sdlc-studio/reviews/` every verdict file
moved the digest and the next round's brief refused the author's self-check as stale over an
unchanged diff. The verdicts folder is now one of the review tooling's writes; any other file
under `sdlc-studio/reviews/` still counts.

Each case drives the shipped `critic.py` in a throwaway project under
`review.author_self_check: block`, where a stale self-check refuses the brief.
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

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
UNIT = "US0101"
STALE = "is stale"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _project(root: Path, affects: str) -> None:
    """`UNIT` declaring `affects`, a QA seat card, the self-check gate at `block`, a page of
    review notes under `sdlc-studio/reviews/`, one commit holding it all, and the unit's
    self-check recorded through the shipped command."""
    _write(root, "sdlc-studio/personas/seats/qa.md",
           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
           "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
    _write(root, "sdlc-studio/.config.yaml", "review:\n  author_self_check: block\n")
    _write(root, "sdlc-studio/reviews/notes.md", "# Review notes\n\nfirst\n")
    _write(root, f"sdlc-studio/stories/{UNIT}-review-notes.md",
           f"# {UNIT}: review notes\n\n> **Status:** Review\n> **Points:** 1\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    gitutil.git(["init", "-q"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "--no-verify", "-m", f"feat({UNIT}): review notes"], root)
    with tempfile.TemporaryDirectory() as d:
        claims = Path(d) / "claims.json"
        claims.write_text(json.dumps([{"surface": "commit message", "claim": "notes are new",
                                       "ruling": "TRUE"}]), encoding="utf-8")
        mutants = Path(d) / "mutants.json"
        mutants.write_text("[]", encoding="utf-8")
        r = _cli(root, "self-check", "record", "--unit", UNIT, "--author", "eng",
                 "--claims", str(claims), "--mutants", str(mutants))
    assert r.returncode == 0, r.stderr


def _brief(root: Path) -> subprocess.CompletedProcess:
    return _cli(root, "brief", "--unit", UNIT, "--seat", "qa")


class VerdictFilesLeaveDigestTests(unittest.TestCase):

    def test_a_verdict_file_leaves_the_self_check_current(self) -> None:
        """AC1. Mutant: the verdicts folder left in the digest, so the reviewer's file moves it
        and the brief refuses the self-check as stale. Held for Affects declaring the reviews
        folder and for one declaring the workspace above it; the positive control is the brief
        issued before the verdict file exists."""
        for affects in ("sdlc-studio/reviews/", "sdlc-studio/"):
            with self.subTest(affects=affects), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, affects)
                r = _brief(root)
                self.assertEqual(0, r.returncode, f"premise: the brief is issued\n{r.stderr}")
                _write(root, f"sdlc-studio/reviews/verdicts/{UNIT}/abc123-0001.txt",
                       f"UNIT: {UNIT}\nBRIEF: abc123-0001\nVERDICT: APPROVE\nISSUES: none\n")
                r = _brief(root)
                self.assertEqual(0, r.returncode, r.stderr)
                self.assertNotIn(STALE, r.stderr)
                self.assertIn(f"Unit under review: {UNIT}", r.stdout)

    def test_a_verdict_file_of_another_unit_leaves_it_current_too(self) -> None:
        """The whole verdicts folder is the tooling's, whichever unit's folder the file is in."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "sdlc-studio/reviews/")
            _write(root, "sdlc-studio/reviews/verdicts/US0999/ffff00-0002.txt", "VERDICT: x\n")
            r = _brief(root)
            self.assertEqual(0, r.returncode, r.stderr)


class OtherReviewFilesStillStaleTests(unittest.TestCase):

    def test_another_file_under_reviews_still_stales_the_self_check(self) -> None:
        """AC2. Mutants: the exclusion widened to the whole reviews folder, or to any path that
        merely starts with `verdicts` (a sibling `verdicts-notes.md` beside the folder). Each
        such edit leaves the brief refused as stale."""
        for rel in ("sdlc-studio/reviews/notes.md", "sdlc-studio/reviews/verdicts-notes.md",
                    "sdlc-studio/reviews/archive/verdicts/US0101/x.txt"):
            with self.subTest(changed=rel), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, "sdlc-studio/reviews/")
                _write(root, rel, "# Review notes\n\nsecond\n")
                r = _brief(root)
                self.assertEqual(2, r.returncode, f"{rel} left the self-check current")
                self.assertIn(STALE, r.stderr)


if __name__ == "__main__":
    unittest.main()
