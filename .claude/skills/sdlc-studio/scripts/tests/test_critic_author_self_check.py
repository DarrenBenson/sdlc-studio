"""US1087: `critic.py brief` tells the author, before the brief, the self-check to run.

The section goes to stderr, so the brief on stdout, the one a reviewer reads from a file, and its
fingerprint are unchanged. It names the claim-inventory surfaces (the commit message, each prose
surface the brief's claim inventory names, each changelog fragment the unit's Affects declares)
and the unit's declared test files as mutation-pass targets, and its instructions are the brief's
own claim-inventory text and its practice to mutate the author's tests, never a restatement.

AC1 and AC2 drive `critic.py brief` through its entry point in a throwaway project; AC3 calls the
section's builder in-process, because it changes the module's texts to see the section follow.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")

HEADING = "AUTHOR SELF-CHECK"


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


def _brief(root: Path, unit: str, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), "brief", "--unit", unit, "--seat",
                           "qa", "--tier", "full", *extra, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _section(stderr: str) -> str:
    """The author self-check section of a brief's stderr, from its heading to the next blank
    line that precedes the tier footer."""
    start = stderr.find(HEADING)
    assert start >= 0, f"no {HEADING} section on stderr:\n{stderr}"
    end = stderr.find("review tier:", start)
    return stderr[start:end if end > 0 else None]


class AuthorStepsTests(unittest.TestCase):

    def test_the_steps_go_to_stderr_and_the_brief_is_unchanged(self) -> None:
        """AC1. Mutants: the section printed to stdout, inside the brief a reviewer reads from a
        file, which also moves the brief's fingerprint; the `--rejoinder` path, the brief for a
        repair, left without the section."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0101", "src/widget.py, tests/test_widget.py, changelog.d/US0101.md")
            r = _brief(root, "US0101")
            self.assertEqual(0, r.returncode, r.stderr)
            section = _section(r.stderr)
            self.assertNotIn(HEADING, r.stdout)
            for line in filter(None, (ln.strip() for ln in section.splitlines())):
                with self.subTest(line=line[:60]):
                    self.assertNotIn(line, r.stdout, "a line of the section reached stdout")
            expected = critic.brief_fingerprint(critic.brief(root, "US0101", "qa", "full"))
            self.assertIn(f"brief fingerprint: {expected}", r.stderr,
                          "the printed brief no longer fingerprints as critic.brief() does")
            prior = root / "verdict.txt"
            prior.write_text("VERDICT: REJECT\nISSUES: [new] blocking: w returns 1 (src/widget.py:2)\n",
                             encoding="utf-8")
            again = _brief(root, "US0101", "--rejoinder", str(prior))
            self.assertEqual(0, again.returncode, again.stderr)
            self.assertNotIn(HEADING, again.stdout)
            self.assertIn(HEADING, again.stderr, "the rejoinder brief carries no self-check")

    def test_the_steps_name_the_units_surfaces_and_tests(self) -> None:
        """AC2. Mutants: the fragment taken as changelog.d/<id>.md, which misses a carried bug's
        fragment; the surfaces typed rather than read from CLAIM_SURFACES; the mutation targets
        taken from anything but the unit's declared test files."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "BG0900", "src/widget.py, tests/test_widget.py, changelog.d/US0800.md")
            section = _section(_brief(root, "BG0900").stderr)
            self.assertIn("changelog.d/US0800.md", section, "the declared fragment is not named")
            self.assertNotIn("changelog.d/BG0900.md", section, "a fragment was invented from the id")
            self.assertIn("commit message", section)
            for surface in critic.CLAIM_SURFACES:
                with self.subTest(surface=surface):
                    self.assertIn(surface, section)
            self.assertIn("tests/test_widget.py", section)
            self.assertNotIn("src/widget.py", section.split("mutation", 1)[-1],
                             "a source file was named as a mutation-pass target")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0102", "src/widget.py")
            section = _section(_brief(root, "US0102").stderr)
            self.assertIn("declares no test file", section)
            self.assertIn("declares no changelog fragment", section)
        with unittest.mock.patch.object(critic, "CLAIM_SURFACES",
                                        (*critic.CLAIM_SURFACES, "release notes")):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, "US0103", "src/widget.py")
                self.assertIn("release notes", critic.author_self_check(root, "US0103"),
                              "the surfaces are typed beside CLAIM_SURFACES, not read from it")

    def test_the_steps_derive_from_the_briefs_practices(self) -> None:
        """AC3. Mutant: the section's instruction typed beside the claim-inventory block and
        the practice to mutate the author's tests, rather than read from them (LL0042)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "US0104", "src/widget.py, tests/test_widget.py")
            marker_claims = "Rule each assertion against a probe you ran (marker C7)."
            claims = critic._CLAIM_INVENTORY_BLOCK + "\n" + marker_claims
            with unittest.mock.patch.object(critic, "_CLAIM_INVENTORY_BLOCK", claims):
                self.assertIn("marker C7", critic.author_self_check(root, "US0104"))
            practice = "Mutate the author's TESTS, not only the code:"
            self.assertIn(practice, critic._REVIEW_PRACTICES_BLOCK, "the practice moved")
            marked = critic._REVIEW_PRACTICES_BLOCK.replace(
                practice, practice + " swap a clause and negate one (marker M9);", 1)
            with unittest.mock.patch.object(critic, "_REVIEW_PRACTICES_BLOCK", marked):
                self.assertIn("marker M9", critic.author_self_check(root, "US0104"))


if __name__ == "__main__":
    unittest.main()
