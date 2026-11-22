"""BG1124: the brief's practice and claim-inventory refusals read the brief it composed, not the
unit diff it carries.

`critic.py brief` refuses a brief missing a standing practice or a claim-inventory surface. The
checks searched the whole assembled brief, which carries the UNIT DIFF, so a unit whose own
commit quoted (or removed) a practice's text had its deficient brief issued: the diff's lines
satisfied the check the brief failed. The checks now read the brief less its UNIT DIFF, and the
author's recorded mutants section appended after it is not read either.

Each case runs the shipped verb in-process against a throwaway git repository whose open run
names the unit, with the brief's practices block (or its claim inventory) patched to drop what
the committed diff quotes.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo
import loader  # noqa: E402

critic = loader.load_script("critic")
PRACTICE = "mutate the author's tests"
PRIOR = "VERDICT: REJECT\nISSUES: [new] a is wrong\nBLOCKING: [new] a is wrong\n"


def _paragraph(block: str, lead: str) -> str:
    """The paragraph of `block` that opens with `lead`."""
    return next(p for p in block.split("\n\n") if p.startswith(lead))


QUOTED = _paragraph(critic._REVIEW_PRACTICES_BLOCK, "Mutate the author's TESTS")
#: the practices block with the quoted practice's paragraph dropped
DROPPED = critic._REVIEW_PRACTICES_BLOCK.replace(f"\n\n{QUOTED}", "")
#: the claim inventory with one of its four surfaces dropped
NO_RESOLUTIONS = critic._CLAIM_INVENTORY_BLOCK.replace("surfaces - Resolutions, ", "surfaces - ")


def _project(root: Path, quote: str) -> None:
    """US0001 declaring src/a.py, an open run naming it at the base commit, and a commit after
    the base that writes `quote` into src/a.py on one line, so the brief's diff carries it."""
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    story = root / "sdlc-studio" / "stories" / "US0001-the-widget.md"
    story.parent.mkdir(parents=True)
    story.write_text("# US0001: the widget\n\n> **Status:** In Progress\n> **Affects:** src/a.py\n"
                     "> **Points:** 2\n\n## Acceptance Criteria\n\n- [ ] **AC1** it works\n"
                     "  - **Verify:** shell true\n", encoding="utf-8")
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    gitutil.git(["init", "-q"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-qm", "base"], root)
    base = gitutil.git(["rev-parse", "HEAD"], root, text=True).stdout.strip()
    one_line = " ".join(quote.split())
    (root / "src" / "a.py").write_text(f"a = 1\nQUOTE = {one_line!r}\n", encoding="utf-8")
    gitutil.git(["commit", "-qam", "feat(US0001): quote it"], root)
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                 "started_at": "2026-10-01T08:00:00Z", "batch": ["US0001"],
                                 "base_ref": base}), encoding="utf-8")


def _main(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(["brief", "--unit", "US0001", "--seat", "qa", "--tier", "full",
                          *argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class BriefChecksIgnoreTheDiffTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _refused(self, got: tuple[int, str, str], named: str, why: str) -> None:
        rc, out, err = got
        self.assertEqual(2, rc, f"{why}: issued\n{err}")
        self.assertEqual("", out, f"{why}: a refused brief reached stdout")
        self.assertIn(named, err, why)

    def test_a_practice_quoted_only_in_the_diff_does_not_satisfy_the_check(self) -> None:
        """AC1. Mutants: the check reading the whole brief, diff included; the re-review brief
        checked over its diff; the author's recorded mutants section read by the check. The
        positive control: the same diff under the shipped block is issued."""
        root = self.root
        _project(root, QUOTED)
        rc, out, err = _main(root)
        self.assertEqual(0, rc, f"premise: the shipped block is issued\n{err}")
        self.assertIn(f"+QUOTE = {' '.join(QUOTED.split())!r}", out,
                      "premise: the brief's diff carries the practice's text")
        with unittest.mock.patch.object(critic, "_REVIEW_PRACTICES_BLOCK", DROPPED):
            self._refused(_main(root), f"missing standing practice(s): {PRACTICE}",
                          "a practice quoted only in the diff satisfied the check")
            prior = root / "prior.txt"
            prior.write_text(PRIOR, encoding="utf-8")
            self._refused(_main(root, "--rejoinder", str(prior)),
                          f"missing standing practice(s): {PRACTICE}",
                          "the re-review brief's diff satisfied the check")
            with unittest.mock.patch.object(critic, "author_mutants_section",
                                            return_value=QUOTED):
                self._refused(_main(root), f"missing standing practice(s): {PRACTICE}",
                              "the author's mutants section satisfied the check")

    def test_a_surface_quoted_only_in_the_diff_does_not_satisfy_the_claim_pass(self) -> None:
        """The claim-inventory refusal is held to the same text. Mutant: it reads the whole
        brief, so the diff's 'Resolutions' satisfies it; the re-review brief's claim pass reads
        its diff. The positive control: the shipped inventory over the same diff is issued, on
        the first brief and the re-review alike."""
        root = self.root
        _project(root, critic._CLAIM_INVENTORY_BLOCK)
        rc, _out, err = _main(root)
        self.assertEqual(0, rc, f"premise: the shipped inventory is issued\n{err}")
        prior = root / "prior.txt"
        prior.write_text(PRIOR, encoding="utf-8")
        rc, out, err = _main(root, "--rejoinder", str(prior))
        self.assertEqual(0, rc, f"premise: the shipped inventory's re-review is issued\n{err}")
        self.assertIn("+QUOTE = ", out, "premise: the re-review's diff carries the inventory")
        self.assertIn("Resolutions", out[out.index("+QUOTE = "):].splitlines()[0],
                      "premise: the quoted inventory names the dropped surface")
        omits = "claim-inventory pass omits prose surface(s): Resolutions"
        with unittest.mock.patch.object(critic, "_CLAIM_INVENTORY_BLOCK", NO_RESOLUTIONS):
            self._refused(_main(root), omits,
                          "a surface quoted only in the diff satisfied the claim pass")
            self._refused(_main(root, "--rejoinder", str(prior)), omits,
                          "the re-review brief's diff satisfied the claim pass")


if __name__ == "__main__":
    unittest.main()
