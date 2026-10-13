"""BG0945: BG0940's changelog entry says what `sprint sign` does after a late ruling.

The entry said a page with a ruling logged between the close and the sign "still checks VALID
when it is signed". Through the CLI the ruling's decisions.md row changes the tree, and sign
refuses the changed tree until a re-close. The test runs those Steps (close, `decisions.py add
--by operator`, sign) on BG0848's close-and-sign fixture and holds the sentence to the outcome.

MUTANT: the fragment's original wording restored (the page is signed after a late ruling), or
sign accepting the changed tree, either of which the test fails on.
"""
# test-census-subject: changelog.d/BG0940.md
from __future__ import annotations

import os
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

        # The way through the fragment names: re-close, then sign.
        run._commit("the late ruling")
        run.sign(run.close())
        self.assertTrue(signing.run_state.read(run.root).get("signature"),
                        "a re-close did not let the run be signed")

        text = " ".join(FRAGMENT.read_text(encoding="utf-8").split())
        self.assertNotIn("still checks VALID when it is signed", text,
                         "the fragment still says the page is signed after a late ruling")
        self.assertRegex(text, r"sign\S* refuses", "the fragment does not say sign refuses")
        self.assertIn("re-close", text, "the fragment does not name the way through")


if __name__ == "__main__":
    unittest.main()
