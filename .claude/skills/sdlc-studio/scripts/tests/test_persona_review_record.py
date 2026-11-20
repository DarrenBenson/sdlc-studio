"""A persona or seat card is reviewed by a seat other than its own: `persona_review.py brief`
frames that seat with the standard and the card's mechanical findings, and `persona_review.py
record` appends the verdict to the review ledger against the card's body hash, refusing a review
it cannot stand behind and clearing a generated card's provisional stamp on a PASS."""
from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402
import persona_gen  # noqa: E402
import persona_review  # noqa: E402
import sprint  # noqa: E402
import validate  # noqa: E402
from lib import sdlc_md  # noqa: E402

TODAY = "2026-11-20"
QA = "sdlc-studio/personas/seats/qa.md"
PRODUCT = "sdlc-studio/personas/seats/product.md"
ENGINEERING = "sdlc-studio/personas/seats/engineering.md"
LEDGER = "sdlc-studio/reviews/persona-reviews.md"
EVIDENCE = "## Evidence\n\n- US0001: the story this card was drawn from\n"
STORY = "# US0001: A story on disk\n\n> **Status:** Draft\n"


def _seat(role: str, name: str, *, extra: str = "", evidence: bool = True) -> str:
    return (f"<!-- role: {role} -->\n# {name} - {role} seat\n\n## Who They Are\n\n"
            f"{name} reviews the work.{extra}\n\n## Lens\n\n- x\n\n## Pushes Back When\n\n- x\n\n"
            f"## Shadow\n\nx\n\n" + (EVIDENCE if evidence else ""))


MAYA = ("# Maya Okafor\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
        "| **Cast role** | Primary |\n\n## Who They Are\n\nMaya runs the team's releases.\n\n"
        "## End Goals\n\n1. Ship a change she can trust\n\n## Experience Goals\n\n- calm\n\n"
        "## Behaviours & Context\n\n- at a desk\n\n## Frustrations\n\n- slow reviews\n\n"
        "## Scenario\n\nShe opens the tool and finishes the job.\n\n" + EVIDENCE)


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _fixture(root: Path, user_name: str | None = None) -> None:
    """A git project with three seat cards: the qa card breaks a blocking rule (a demographic
    token) and a reported one (no Evidence section); the other two are clean."""
    _write(root, "sdlc-studio/stories/US0001-a-story-on-disk.md", STORY)
    _write(root, QA, _seat("qa", "Ivy Cole", extra=" She is married.", evidence=False))
    _write(root, PRODUCT, _seat("product", "Lena Marsh"))
    _write(root, ENGINEERING, _seat("engineering", "Cal Dorn"))
    gitutil.git(["init", "-q"], root)
    if user_name:
        gitutil.git(["config", "user.name", user_name], root)


def _run(mod, argv: list[str]) -> tuple[int, str, str]:
    """Run a script's main in-process under the confined git environment, so the run-by
    default reads only the fixture repository's own config."""
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
            mock.patch.object(sdlc_md, "now_date", return_value=TODAY), \
            redirect_stdout(out), redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _record(root: Path, *argv: str) -> tuple[int, str, str]:
    return _run(persona_review, ["record", "--root", str(root), *argv])


def _rows(root: Path) -> list[list[str]]:
    """The ledger's data rows, header and separator left out."""
    text = (root / LEDGER).read_text(encoding="utf-8")
    rows = [sdlc_md.table_cells(ln) for ln in text.splitlines()]
    return [r for r in rows if r and r[0] != "Card"]


def _independent_hash(text: str) -> str:
    """The card's body hash, computed here rather than through the code under test: every
    line but a generation stamp or reviewed marker, trailing whitespace dropped."""
    keep = [ln.rstrip() for ln in text.splitlines() if "<!-- provenance:" not in ln]
    return hashlib.sha256("\n".join(keep).encode("utf-8")).hexdigest()[:16]


class PersonaReviewRecordTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_the_brief_frames_another_seat_with_the_cards_findings(self) -> None:
        _fixture(self.root)
        rc, out, err = _run(persona_review, ["brief", "--root", str(self.root),
                                             "--card", QA, "--seat", "product"])
        self.assertEqual(rc, 0, err)
        self.assertIn(PRODUCT, out)              # the card the reviewing seat adopts
        self.assertIn("best-practices/persona.md", out)  # the standard
        self.assertIn(f"Card under review: {QA}", out)
        # The card's mechanical floor, each finding with its severity: one rule that blocks and
        # one that is reported, as the fixture's qa card breaks them.
        self.assertRegex(out, r"(?m)^\s*blocks\s+seat-demographic-fluff\b")
        self.assertRegex(out, r"(?m)^\s*reported\s+persona-evidence\b")
        found = persona_review.check(self.root, self.root / QA)
        self.assertEqual(len(found), 2, found)
        for f in found:
            self.assertRegex(out, rf"(?m)^\s*{f['severity']}\s+{re.escape(f['rule'])}\b")
        self.assertIn(f"persona_review.py record --card {QA} --outcome", out)
        self.assertIn('--reviewer "Lena Marsh (product)"', out)
        # The card's own seat is refused, and no brief is printed.
        rc, out, err = _run(persona_review, ["brief", "--root", str(self.root),
                                             "--card", QA, "--seat", "qa"])
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("a seat never reviews its own card", err)

    def test_a_review_is_recorded_against_the_cards_body_hash(self) -> None:
        _fixture(self.root, user_name="Rae Holt")
        card = self.root / QA
        rc, out, err = _record(self.root, "--card", QA, "--outcome", "fail",
                               "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox",
                               "--rule", "persona-evidence")
        self.assertEqual(rc, 0, err)
        want = _independent_hash(card.read_text(encoding="utf-8"))
        self.assertEqual(_rows(self.root), [[QA, want, "FAIL", "Lena Marsh (product)", "product",
                                             "Dana Fox", TODAY, "persona-evidence"]])
        # No --run-by: the row names the repository's own git user.name.
        rc, _out, err = _record(self.root, "--card", QA, "--outcome", "fail",
                                "--reviewer", "Lena Marsh (product)",
                                "--rule", "persona-evidence")
        self.assertEqual(rc, 0, err)
        self.assertEqual(_rows(self.root)[-1][5], "Rae Holt")
        # A generation stamp changes the file but not the card: the hash is the same.
        raw = card.read_bytes()
        persona_gen.stamp(card)
        self.assertNotEqual(card.read_bytes(), raw)
        rc, _out, err = _record(self.root, "--card", QA, "--outcome", "fail",
                                "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox",
                                "--rule", "persona-evidence")
        self.assertEqual(rc, 0, err)
        self.assertEqual([r[1] for r in _rows(self.root)], [want, want, want])

    def test_an_unsound_review_is_refused_and_nothing_is_written(self) -> None:
        _fixture(self.root)  # a repository with no user.name, global and system config off
        ok = ("--card", QA, "--outcome", "fail", "--reviewer", "Lena Marsh (product)",
              "--run-by", "Dana Fox", "--rule", "persona-evidence")
        rc, _out, err = _record(self.root, *ok)   # positive control: a sound review lands
        self.assertEqual(rc, 0, err)
        before = (self.root / LEDGER).read_bytes()
        cases = {
            "a FAIL names the rule it failed": (
                "--card", QA, "--outcome", "fail", "--reviewer", "Lena Marsh (product)",
                "--run-by", "Dana Fox"),
            "persona-wobble is no rule the standard holds": (
                *ok, "--rule", "persona-wobble"),
            "names no (role) group": (
                "--card", QA, "--outcome", "fail", "--reviewer", "Lena Marsh",
                "--run-by", "Dana Fox", "--rule", "persona-evidence"),
            "no --run-by and no git user.name": (
                "--card", QA, "--outcome", "fail", "--reviewer", "Lena Marsh (product)",
                "--rule", "persona-evidence"),
            "--run-by names a seat, not a person": (
                "--card", QA, "--outcome", "fail", "--reviewer", "Lena Marsh (product)",
                "--run-by", "(product)", "--rule", "persona-evidence"),
            "a seat never reviews its own card": (
                "--card", QA, "--outcome", "fail", "--reviewer", "Ivy Cole (qa)",
                "--run-by", "Dana Fox", "--rule", "persona-evidence"),
            "seat-demographic-fluff blocks": (
                "--card", QA, "--outcome", "pass", "--reviewer", "Lena Marsh (product)",
                "--run-by", "Dana Fox"),
        }
        for reason, argv in cases.items():
            with self.subTest(reason=reason):
                rc, out, err = _record(self.root, *argv)
                self.assertEqual(rc, 2, out)
                self.assertIn(reason, err)
                self.assertEqual((self.root / LEDGER).read_bytes(), before)

    def test_a_pass_clears_a_generated_cards_provisional_stamp(self) -> None:
        _fixture(self.root)
        card = self.root / ENGINEERING
        persona_gen.stamp(card)
        self.assertEqual(persona_gen.classify(card), "generated-pristine")
        stamped = card.read_text(encoding="utf-8")
        stamp_line = persona_gen.STAMP_RE.search(stamped).group(0)
        # A FAIL is no acceptance: the card stays provisional.
        rc, _out, err = _record(self.root, "--card", ENGINEERING, "--outcome", "fail",
                                "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox",
                                "--rule", "persona-evidence")
        self.assertEqual(rc, 0, err)
        self.assertEqual(persona_gen.classify(card), "generated-pristine")
        rc, _out, err = _record(self.root, "--card", ENGINEERING, "--outcome", "pass",
                                "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox")
        self.assertEqual(rc, 0, err)
        text = card.read_text(encoding="utf-8")
        self.assertIsNone(persona_gen.STAMP_RE.search(text))
        self.assertIn(f"<!-- provenance: reviewed {TODAY} -->", text.splitlines())
        # The PASS rewrites the provenance line and nothing else on the card.
        self.assertEqual(text, stamped.replace(stamp_line, f"<!-- provenance: reviewed {TODAY} -->"))
        rc, out, err = _run(persona_gen, ["classify", "--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        line = next(ln for ln in out.splitlines() if ln.endswith("engineering.md"))
        self.assertTrue(line.startswith("authored"), out)
        self.assertNotIn("seats/engineering.md", persona_gen.provisional_seats(self.root))
        self.assertEqual(_rows(self.root)[-1][2], "PASS")

    def test_the_review_ledger_is_never_read_as_a_persona_card(self) -> None:
        _fixture(self.root)
        _write(self.root, "sdlc-studio/personas/maya-okafor.md", MAYA)
        rc, _out, err = _record(self.root, "--card", QA, "--outcome", "fail",
                                "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox",
                                "--rule", "persona-evidence")
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.root / LEDGER).is_file())
        self.assertEqual(list((self.root / "sdlc-studio" / "personas").glob("*review*")), [])
        rc, out, err = _run(validate, ["personas", "--root", str(self.root)])
        self.assertNotIn("persona-reviews", out + err)
        self.assertNotIn("Persona Reviews", out + err)
        worklist = _write(self.root, "worklist.txt", "US0001\n")
        rc, out, err = _run(sprint, ["goal-review", "brief", "--goal",
                                     "Persona Reviews land for Maya", "--brief-worklist",
                                     str(worklist), "--root", str(self.root)])
        self.assertEqual(rc, 0, err)
        serves = [ln for ln in out.splitlines() if ln.startswith("Goal serves")]
        self.assertEqual(serves, ["Goal serves (the plan's own trace): Maya Okafor (Primary)"],
                         out)


if __name__ == "__main__":
    unittest.main()
