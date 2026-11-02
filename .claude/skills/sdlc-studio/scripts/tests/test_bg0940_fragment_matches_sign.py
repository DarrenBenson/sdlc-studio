"""BG0945: BG0940's changelog entry says what `sprint sign` does after a late ruling.

The entry said a page with a ruling logged between the close and the sign "still checks VALID
when it is signed". Through the CLI the ruling's decisions.md row changes the tree, and sign
refuses the changed tree until a re-close. The test runs those Steps (close, `decisions.py add
--by operator`, sign) on BG0848's close-and-sign fixture and holds the sentence to the outcome.

The entry is read from `changelog.d/BG0940.md` while that fragment exists, and once a release cut
has folded it, from the released CHANGELOG section holding it (US1111). It carries no unit id, so
it is found by its own opening words; an entry in neither place fails the test.

MUTANT: the entry's original wording restored (the page is signed after a late ruling), sign
accepting the changed tree, or the entry missing from both the fragment and the CHANGELOG, any of
which the test fails on.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_sign as signing  # noqa: E402 - BG0848's close-and-sign fixture, shared

SCRIPTS = Path(__file__).resolve().parent.parent
FRAGMENT = SCRIPTS.parents[3] / "changelog.d" / "BG0940.md"
CHANGELOG = SCRIPTS.parents[3] / "CHANGELOG.md"
#: The entry's own opening words, by which it is found: it names no unit id.
OPENING = "- A ruling logged with `decisions.py add --by operator`"
#: A released section: its `## [x.y.z]` heading to the next `## [` heading. `[Unreleased]` is not
#: one, since a cut empties it.
_RELEASED = re.compile(r"^## \[(\d+\.\d+\.\d+[^\]]*)\][^\n]*\n(.*?)(?=^## \[|\Z)", re.M | re.S)


def _entry_in(text: str) -> str:
    """The bullet of `text` that opens with `OPENING`, whitespace folded; "" when none does."""
    for bullet in re.split(r"\n(?=- )", text):
        if bullet.lstrip().startswith(OPENING):
            return " ".join(bullet.split())
    return ""


def bg0940_entry(fragment: Path = FRAGMENT, changelog: Path = CHANGELOG) -> tuple[str, str]:
    """`(entry, where)`: BG0940's entry from `fragment` while it exists, else from the first
    released CHANGELOG section holding it. The entry is "" when neither holds it."""
    if fragment.is_file():
        return _entry_in(fragment.read_text(encoding="utf-8")), str(fragment)
    text = changelog.read_text(encoding="utf-8") if changelog.is_file() else ""
    for section in _RELEASED.finditer(text):
        found = _entry_in(section.group(2))
        if found:
            return found, f"{changelog.name} [{section.group(1)}]"
    return "", f"neither {fragment.name} nor a released section of {changelog.name}"


class FragmentMatchesSignTests(unittest.TestCase):
    def _rule(self, run, decision: str) -> None:
        r = subprocess.run([sys.executable, str(SCRIPTS / "decisions.py"), "add", "--decision",
                            decision, "--rationale", "the BG0945 steps", "--by", "operator",
                            "--root", str(run.root)],
                           capture_output=True, text=True, timeout=60, check=False, env=run.env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_the_fragment_says_what_sign_does(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = signing._SignMovesRun(tmp.name)
        env = unittest.mock.patch.dict(os.environ, run.env, clear=True)
        env.start()
        self.addCleanup(env.stop)
        run.build()
        # The decisions log is tracked, as it is in a real project: one ruling before the close,
        # committed, so the late one is a change to a tracked file, not a new untracked one.
        self._rule(run, "a ruling before the close")
        run._commit("the decisions log")
        report = run.close()
        self._rule(run, "a late ruling")
        with unittest.mock.patch.object(signing.run_state, "_unit_clock",
                                        lambda: "2026-09-30T10:00:00Z"), \
                unittest.mock.patch.object(signing.sprint, "_principal_refusals",
                                           lambda *a, **k: []):
            rc, out, err = signing._run(run.root, "sign", "--report", report, "--principal",
                                        "Darren")
        self.assertNotEqual(0, rc, "sign sealed a page over a tree changed since the close")
        self.assertIn("sdlc-studio/decisions.md", out + err)
        self.assertFalse(signing.run_state.read(run.root).get("signature"))

        # The way through the entry names: re-close, then sign.
        run._commit("the late ruling")
        run.sign(run.close())
        self.assertTrue(signing.run_state.read(run.root).get("signature"),
                        "a re-close did not let the run be signed")

        text, where = bg0940_entry()
        self.assertTrue(text, f"BG0940's entry is in {where}")
        self.assertNotIn("still checks VALID when it is signed", text,
                         f"the entry in {where} still says the page is signed after a late ruling")
        self.assertRegex(text, r"sign\S* refuses",
                         f"the entry in {where} does not say sign refuses")
        self.assertIn("re-close", text, f"the entry in {where} does not name the way through")

    def test_the_entry_is_read_from_the_fragment_or_its_release(self) -> None:
        """US1111. Mutants: the fragment read with the CHANGELOG ignored after the cut; an
        `[Unreleased]` copy read in place of the released one; a section read past its next
        heading; an entry in neither place read as found."""
        entry = (f"{OPENING} (or persona) between `sprint close` and\n  `sprint sign`, so"
                 " `sprint sign` refuses until the run is re-closed.")
        folded = " ".join(entry.split())
        with tempfile.TemporaryDirectory() as tmp:
            fragment, changelog = Path(tmp) / "BG0940.md", Path(tmp) / "CHANGELOG.md"
            changelog.write_text(
                f"# Changelog\n\n## [Unreleased]\n\n{OPENING}, an unreleased copy.\n\n"
                f"## [6.2.0] - 2026-11-02\n\n### Fixed\n\n- Another entry.\n{entry}\n\n"
                "## [6.1.0] - 2026-10-03\n\n### Fixed\n\n- An older entry naming a re-close.\n",
                encoding="utf-8")
            self.assertEqual((folded, "CHANGELOG.md [6.2.0]"), bg0940_entry(fragment, changelog))
            fragment.write_text(f"<!-- section: Fixed -->\n\n{entry}\n- A second entry.\n",
                                encoding="utf-8")
            self.assertEqual((folded, str(fragment)), bg0940_entry(fragment, changelog))
            fragment.unlink()
            changelog.write_text(changelog.read_text(encoding="utf-8").replace(entry, "- Gone."),
                                 encoding="utf-8")
            self.assertEqual("", bg0940_entry(fragment, changelog)[0])


if __name__ == "__main__":
    unittest.main()
