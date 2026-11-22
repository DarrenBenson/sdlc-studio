"""BG1702: a re-review brief's practice and claim-inventory checks read the brief's own text,
not the prior verdict it quotes.

`critic.py brief` refuses a brief whose text carries none of a standing practice. The checks
read the brief less its UNIT DIFF, but a `--rejoinder` brief's checked text still held the
quoted prior verdict, so a REJECT whose findings quote a practice satisfied the check for a
re-review brief whose own sections carry none of it. The checked text now leaves the quote out,
the way it leaves out the diff; the issued brief still quotes the prior verdict in full.

Each case works in a throwaway git repository whose open run names the unit, its REJECT
recorded in the ledger. The two refusal cases run the shipped verb in-process with the brief's
practices block, or its claim inventory, patched to drop what the prior verdict quotes: the
stand-in for a seat's brief that names none of it. The issued-brief case runs the verb
in-process with the shipped blocks as they are, and the checked-text case calls
`critic.checked_rejoinder_brief` directly, with the shipped blocks too.
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


def _paragraph(block: str, lead: str) -> str:
    return next(p for p in block.split("\n\n") if p.startswith(lead))


QUOTED = " ".join(_paragraph(critic._REVIEW_PRACTICES_BLOCK, "Mutate the author's TESTS").split())
#: the practices block with the quoted practice's paragraph dropped
DROPPED = critic._REVIEW_PRACTICES_BLOCK.replace(
    "\n\n" + _paragraph(critic._REVIEW_PRACTICES_BLOCK, "Mutate the author's TESTS"), "")
INVENTORY = " ".join("\n".join(critic._CLAIM_INVENTORY_BLOCK.splitlines()[2:]).split())
#: the claim inventory with one of its four surfaces dropped
NO_RESOLUTIONS = critic._CLAIM_INVENTORY_BLOCK.replace("surfaces - Resolutions, ", "surfaces - ")


def _project(root: Path, finding: str) -> None:
    """US0001 declaring src/a.py, an open run naming it at the base commit, a commit after the
    base under its id, and a qa REJECT of it in the ledger whose one finding is `finding`."""
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
    (root / "src" / "a.py").write_text("a = 2\n", encoding="utf-8")
    gitutil.git(["commit", "-qam", "feat(US0001): a is two"], root)
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-A", "outcome": "running",
                                 "started_at": "2026-10-01T08:00:00Z", "batch": ["US0001"],
                                 "base_ref": base}), encoding="utf-8")
    with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            contextlib.redirect_stderr(io.StringIO()):
        critic.record_verdict(root, "US0001", "REJECT", "qa-seat", "eng-seat",
                              f"BLOCKING: [new] {finding}")


def _main(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(["brief", "--unit", "US0001", "--seat", "qa", "--tier", "full",
                          *argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


class RejoinderQuoteDoesNotSatisfyTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _refused(self, got: tuple[int, str, str], named: str, why: str) -> None:
        rc, out, err = got
        self.assertEqual(2, rc, f"{why}: issued\n{err}")
        self.assertEqual("", out, f"{why}: a refused brief reached stdout")
        self.assertIn(named, err, why)

    def test_a_practice_quoted_only_in_the_prior_verdict_does_not_satisfy_the_check(self) -> None:
        """AC1. Mutant: the rejoinder's checked text keeps the quoted prior verdict, so its
        words satisfy the practices check. Held for the prior verdict read from the ledger
        (`--rejoinder` bare) and from a file."""
        root = self.root
        _project(root, QUOTED)
        prior = root / "prior.txt"
        prior.write_text(f"VERDICT: REJECT\nISSUES: [new] {QUOTED}\nBLOCKING: [new] {QUOTED}\n",
                         encoding="utf-8")
        with unittest.mock.patch.object(critic, "_REVIEW_PRACTICES_BLOCK", DROPPED):
            self._refused(_main(root, "--rejoinder"), f"missing standing practice(s): {PRACTICE}",
                          "the ledger REJECT's quoted practice satisfied the check")
            self._refused(_main(root, "--rejoinder", str(prior)),
                          f"missing standing practice(s): {PRACTICE}",
                          "the prior verdict file's quoted practice satisfied the check")

    def test_a_surface_quoted_only_in_the_prior_verdict_does_not_satisfy_the_claim_pass(
            self) -> None:
        """The claim-inventory refusal reads the same text. Mutant: it reads the quote, so the
        prior verdict's 'Resolutions' satisfies it."""
        root = self.root
        _project(root, INVENTORY)
        with unittest.mock.patch.object(critic, "_CLAIM_INVENTORY_BLOCK", NO_RESOLUTIONS):
            self._refused(_main(root, "--rejoinder"),
                          "claim-inventory pass omits prose surface(s): Resolutions",
                          "the prior verdict's quoted surface satisfied the claim pass")


class RejoinderBriefStillQuotesTests(unittest.TestCase):

    def test_the_issued_rejoinder_still_quotes_the_prior_verdict_in_full(self) -> None:
        """AC2. Mutant: the quote dropped from the issued brief rather than from the checked
        text. The shipped block names the practice, so the brief is issued, and the prior
        verdict appears whole under the re-review heading."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, QUOTED)
            rc, out, err = _main(root, "--rejoinder")
            self.assertEqual(0, rc, err)
            quote = out[out.index("--- RE-REVIEW (rejoinder) ---"):]
            self.assertIn(f"VERDICT: REJECT\nISSUES: [new] {QUOTED}\nBLOCKING: [new] {QUOTED}\n",
                          quote)
            self.assertIn(critic.REBUILT_QUOTE, quote)

    def test_the_checked_text_is_the_rejoinder_less_its_quote_and_diff(self) -> None:
        """`checked_rejoinder_brief`'s second value carries the re-review's own instructions
        and return contract, and neither the prior verdict nor the UNIT DIFF."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "a sentinel finding no brief section says")
            prior = "VERDICT: REJECT\nISSUES: [new] a sentinel finding no brief section says\n"
            with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
                text, checked = critic.checked_rejoinder_brief(root, "US0001", "qa", prior)
            self.assertIn("a sentinel finding", text)
            self.assertNotIn("a sentinel finding", checked)
            self.assertIn("--- RE-REVIEW (rejoinder) ---", checked)
            self.assertIn("RE-EXECUTE the probes and mutants", checked)
            self.assertNotIn("--- UNIT DIFF", checked)


if __name__ == "__main__":
    unittest.main()
