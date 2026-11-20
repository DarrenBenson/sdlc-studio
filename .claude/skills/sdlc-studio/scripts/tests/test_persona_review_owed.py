"""`sprint plan` names each persona card the standard refuses with its remedy, and
`persona_review.py owed`, the plan and the release cut name each card changed since its review,
never reviewed, or not reviewed since the newest release tag - reported, never refused.

Driven through `sprint.main`, `persona_review.main` and `release_cut.main`, the shipped entry
points, in throwaway trees: the goal-trace fixture for the plan (BG0001; Maya Okafor Primary,
Trevor Hale Negative) and git repositories built with the confined git env for the tag checks.
A review's date is set through `persona_review.record`'s `today`, the one writer of a ledger row.
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
import gitutil  # noqa: E402
import loader  # noqa: E402
import test_goal_review_testable_goals as tg  # noqa: E402 - the in-process sprint runner
import test_lean_goal_trace as s1  # noqa: E402 - the plannable project with persona cards

sprint = loader.load_script("sprint")
persona_review = loader.load_script("persona_review")
release_cut = loader.load_script("release_cut")

_QA = "sdlc-studio/personas/seats/qa.md"
_UNKNOWN = "The Primary persona is Zed Unknown."


def _seat(extra: str = "") -> str:
    """A qa seat card carrying the review render, `extra` closing its Who They Are section."""
    return ("<!-- role: qa -->\n# Quinn Lake - reviewing seat\n\n## Who They Are\n\n"
            f"Quinn Lake reviews the work.{extra}\n\n## Lens\n\n- x\n\n## Pushes Back When\n\n"
            "- x\n\n## Shadow\n\nx\n\n## Evidence\n\n- BG0001: the bug this seat reviews\n")


def _persona(name: str, body: str = "Somebody.") -> str:
    return (f"# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
            f"| **Cast role** | Secondary |\n\n## Who They Are\n\n{body}\n")


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _pass(root: Path, rel: str, day: str) -> None:
    persona_review.record(root, rel, "pass", "Rowan Hart (engineering)", run_by="Tess Moreau",
                          today=day)


def _owed(root: Path) -> tuple[int, list[str]]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = persona_review.main(["owed", "--root", str(root)])
    assert err.getvalue() == "", err.getvalue()
    return rc, [ln for ln in out.getvalue().splitlines()
                if ln.startswith("persona review owed:")]


def _commit(root: Path, message: str, when: str) -> None:
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", message], root,
                env_extra={"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})


def _plan(root: Path, *extra: str) -> tuple[int, str, str]:
    return tg._run(root, "plan", "--worklist", str(root / "worklist.txt"), "--no-fetch", *extra)


def _plan_both(root: Path) -> tuple[int, list[str], int, list[str]]:
    """The JSON plan's exit code and batch, and the text plan's exit code and lines."""
    rc, out, err = _plan(root, "--format", "json")
    assert rc == 0, err
    batch = [u["id"] for u in json.loads(out)["batch"]]
    text_rc, text, text_err = _plan(root)
    return rc, batch, text_rc, (text + text_err).splitlines()


def _cut_fixture(root: Path) -> None:
    _write(root, "CHANGELOG.md", "# Changelog\n\n## [Unreleased]\n\n## [1.0.0] - 2026-01-01\n\n"
                                 "### Added\n\n- the first release\n")
    _write(root, "changelog.d/US0001.md", "<!-- section: Added -->\n\nA change.\n")


def _cut(root: Path) -> tuple[int, list[str]]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = release_cut.main(["changelog-cut", "--version", "9.9.9", "--root", str(root)])
    return rc, (out.getvalue() + err.getvalue()).splitlines()


class PersonaReviewOwedTests(unittest.TestCase):

    def test_the_plan_names_each_blocked_card_with_its_remedy(self) -> None:
        """AC1. Mutants: the plan silent about a blocked seat card; the line without its rule,
        its line or its remedy; the plan refused or its batch changed for the card."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            s1._project(root)
            _write(root, _QA, _seat())
            rc0, batch0, text_rc0, lines0 = _plan_both(root)
            _write(root, _QA, _seat(f" {_UNKNOWN}"))
            rc, batch, text_rc, lines = _plan_both(root)
        self.assertEqual([], [ln for ln in lines0 if ln.startswith("persona card blocked:")])
        blocked = [ln for ln in lines if ln.startswith("persona card blocked:")]
        self.assertEqual(1, len(blocked), "\n".join(lines))
        line = blocked[0]
        self.assertIn(f"persona card blocked: {_QA} breaks the persona standard - ", line)
        expected = _seat(f" {_UNKNOWN}").splitlines().index(f"Quinn Lake reviews the work. "
                                                           f"{_UNKNOWN}") + 1
        self.assertIn(f"seat-persona-unknown (line {expected}): ", line)
        self.assertIn("Zed Unknown", line)
        self.assertRegex(line, rf"Run next: python3 \S+persona_review\.py brief --card {_QA} "
                               r"--seat (?!qa\b)\w+$")
        self.assertEqual((rc0, batch0, text_rc0), (rc, batch, text_rc))

    def test_changed_and_unreviewed_cards_are_owed(self) -> None:
        """AC2. Mutants: change read from the file's mtime or bytes or git history rather than
        the recorded body hash; a never-reviewed card left out; a repository with no tags
        erroring."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], root)
            kept = _write(root, "sdlc-studio/personas/ada-lane.md", _persona("Ada Lane"))
            edited = _write(root, "sdlc-studio/personas/ben-ode.md", _persona("Ben Ode"))
            _write(root, "sdlc-studio/personas/cy-park.md", _persona("Cy Park"))
            _commit(root, "cards", "2026-11-01T10:00:00+0000")
            _pass(root, "sdlc-studio/personas/ada-lane.md", "2026-11-02")
            _pass(root, "sdlc-studio/personas/ben-ode.md", "2026-11-03")
            edited.write_text(_persona("Ben Ode", "Somebody else."), encoding="utf-8")
            # The kept card is rewritten, touched and committed after its review, its bytes
            # unchanged.
            kept.write_text(kept.read_text(encoding="utf-8"), encoding="utf-8")
            os.utime(kept, (2_000_000_000, 2_000_000_000))
            _commit(root, "after the reviews", "2026-11-05T10:00:00+0000")
            rc, lines = _owed(root)
        self.assertEqual(0, rc)
        self.assertEqual(
            ["persona review owed: sdlc-studio/personas/ben-ode.md - changed since its review "
             "of 2026-11-03",
             "persona review owed: sdlc-studio/personas/cy-park.md - never reviewed"],
            lines)

    def test_a_card_not_reviewed_since_the_latest_tag_is_owed_by_day(self) -> None:
        """AC3. Mutants: the newest tag chosen by name order, or by the tag's own date rather
        than its commit's; a same-day review compared against the commit's timestamp."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], root)
            _write(root, "sdlc-studio/personas/eve-ruiz.md", _persona("Eve Ruiz"))
            _write(root, "sdlc-studio/personas/finn-ash.md", _persona("Finn Ash"))
            _commit(root, "first", "2026-11-01T10:00:00+0000")
            # The highest version name sits on the older commit.
            gitutil.git(["tag", "v9.0.0"], root)
            _write(root, "README.md", "x\n")
            _commit(root, "second", "2026-11-10T15:00:00+0000")
            # An annotated tag made two days after its commit: the commit's date is the one read.
            gitutil.git(["tag", "-a", "v1.0.0", "-m", "release"], root,
                        env_extra={"GIT_COMMITTER_DATE": "2026-11-12T09:00:00+0000"})
            _pass(root, "sdlc-studio/personas/eve-ruiz.md", "2026-11-09")
            _pass(root, "sdlc-studio/personas/finn-ash.md", "2026-11-10")
            rc, lines = _owed(root)
        self.assertEqual(0, rc)
        self.assertEqual(
            ["persona review owed: sdlc-studio/personas/eve-ruiz.md - not reviewed since v1.0.0: "
             "its PASS of 2026-11-09 is dated before the tag commit's date, 2026-11-10 "
             "(compared by day: the PASS date against the tag commit's date)"],
            lines)

    def test_the_plan_and_the_release_cut_name_owed_reviews(self) -> None:
        """AC4. Mutants: either command refusing on an owed review; one of them silent; the
        plan naming each card rather than the count; the owed list written into CHANGELOG.md."""
        with tempfile.TemporaryDirectory() as d_owed, tempfile.TemporaryDirectory() as d_clear:
            results = {}
            for name, root in (("owed", Path(d_owed)), ("clear", Path(d_clear))):
                s1._project(root)
                _cut_fixture(root)
                if name == "clear":
                    for card in ("maya-okafor", "trevor-hale"):
                        _pass(root, f"sdlc-studio/personas/{card}.md", "2026-11-02")
                plan = _plan_both(root)
                skipped = _plan(root, "--skip-personas")
                cut_rc, cut_lines = _cut(root)
                changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
                results[name] = (plan, cut_rc, cut_lines, changelog, skipped)
        (rc, batch, text_rc, lines), cut_rc, cut_lines, changelog, skipped = results["owed"]
        (rc0, batch0, text_rc0, lines0), cut_rc0, cut_lines0, changelog0, _ = results["clear"]
        # --skip-personas reads no card, so it names neither a blocked card nor an owed review.
        self.assertEqual(0, skipped[0], skipped[2])
        self.assertEqual([], [ln for ln in (skipped[1] + skipped[2]).splitlines()
                              if ln.startswith("persona ")])
        owed = [ln for ln in lines if ln.startswith("persona reviews owed:")]
        self.assertEqual(1, len(owed), "\n".join(lines))
        self.assertTrue(owed[0].startswith("persona reviews owed: 2 "), owed[0])
        self.assertIn("persona_review.py owed", owed[0])
        self.assertEqual([], [ln for ln in lines if "maya-okafor.md" in ln])
        self.assertEqual([], [ln for ln in lines0 if ln.startswith("persona review")])
        self.assertEqual((rc0, batch0, text_rc0), (rc, batch, text_rc))
        self.assertEqual(0, cut_rc0)
        self.assertEqual(cut_rc0, cut_rc)
        self.assertEqual(
            ["persona review owed: sdlc-studio/personas/maya-okafor.md - never reviewed",
             "persona review owed: sdlc-studio/personas/trevor-hale.md - never reviewed"],
            [ln for ln in cut_lines if ln.startswith("persona review owed:")])
        self.assertEqual([], [ln for ln in cut_lines0 if ln.startswith("persona review")])
        self.assertEqual(changelog0, changelog)
        self.assertNotIn("persona", changelog)


if __name__ == "__main__":
    unittest.main()
