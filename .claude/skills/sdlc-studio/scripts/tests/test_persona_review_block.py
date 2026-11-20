"""A project persona or seat card that breaks a blocking rule of the persona standard, or whose
latest review in the ledger failed, frames nothing: `persona_resolve.py resolve` and
`resolve-consult`, `critic.py brief` and the refine and triage panels each refuse it, naming the
card, the rule and one command to run next, and no other card stands in for it. A card with no
review, or changed since its PASS, still frames and is named as owed its review; the shipped
default and `--skip-personas` never read the ledger."""
from __future__ import annotations

import io
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import artifact  # noqa: E402
import gitutil  # noqa: E402
import persona_resolve  # noqa: E402
import persona_review  # noqa: E402
from lib import run_state  # noqa: E402

QA = "sdlc-studio/personas/seats/qa.md"
PRODUCT = "sdlc-studio/personas/seats/product.md"
ENGINEERING = "sdlc-studio/personas/seats/engineering.md"
LEDGER = "sdlc-studio/reviews/persona-reviews.md"
EVIDENCE = "## Evidence\n\n- US0001: the story this card was drawn from\n"
STORY = "# US0001: A story on disk\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n- **AC1:** x\n"
SHIPPED_QA = SCRIPTS.parent / "templates" / "personas" / "amigos" / "qa.md"
#: The remedy every refusal prints: one command, briefing another seat to review the card.
REMEDY_RE = re.compile(r"persona_review\.py brief --card (\S+) --seat (\S+)")


def _seat(role: str, name: str, *, extra: str = "", evidence: bool = True) -> str:
    return (f"<!-- role: {role} -->\n# {name} - {role} seat\n\n## Who They Are\n\n"
            f"{name} reviews the work.{extra}\n\n## Lens\n\n- x\n\n## Pushes Back When\n\n- x\n\n"
            f"## Shadow\n\nx\n\n" + (EVIDENCE if evidence else ""))


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _fixture(root: Path, qa: str | None) -> None:
    """A git project with a story, a request, an issue and the engineering and product seat
    cards, both clean; `qa` is the qa seat card's text, or None for no project qa card."""
    _write(root, "sdlc-studio/.config.yaml", "two_backlog:\n  enforce: true\n")
    _write(root, "src/a.py", "")
    _write(root, "sdlc-studio/stories/US0001-a-story-on-disk.md", STORY)
    _write(root, ENGINEERING, _seat("engineering", "Cal Dorn"))
    _write(root, PRODUCT, _seat("product", "Lena Marsh"))
    if qa is not None:
        _write(root, QA, qa)
    artifact.new(root, "cr", "A change", {"size": "M", "priority": "P2", "affects": "src/a.py",
                                          "ctype": "Feature", "summary": "s", "impact": "i",
                                          "acs": ["a"]})
    artifact.new(root, "issue", "Checkout 500s", {"size": "M", "severity": "High",
                                                  "summary": "s"})
    gitutil.git(["init", "-q"], root)


def _env(root: Path) -> dict:
    """The confined environment: git config neutralised, every home the run could write under
    pointed inside the fixture."""
    home = root.parent / (root.name + "-home")
    home.mkdir(exist_ok=True)
    return gitutil.git_env(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
                           XDG_DATA_HOME=str(home / ".local" / "share"),
                           CLAUDE_CONFIG_DIR=str(home / ".claude"))


def _cli(root: Path, script: str, *argv: str) -> tuple[int, str, str]:
    """Run a shipped script as the operator does, from the project root."""
    done = subprocess.run([sys.executable, str(SCRIPTS / script), *argv], cwd=str(root),
                          env=_env(root), capture_output=True, text=True, timeout=240,
                          check=False)
    return done.returncode, done.stdout, done.stderr


def _record(root: Path, outcome: str, reviewer: str, date: str, rules=(), card: str = QA) -> None:
    with mock.patch.dict(os.environ, gitutil.git_env(), clear=True):
        persona_review.record(root, card, outcome, reviewer, run_by="Dana Fox", rules=rules,
                              today=date)


def _resolve(root: Path, *extra: str) -> tuple[int, str, str]:
    return _cli(root, "persona_resolve.py", "resolve", "--seat", "qa", "--root", str(root),
                *extra)


class PersonaReviewBlockTests(unittest.TestCase):

    def test_a_card_breaking_a_blocking_rule_is_refused_at_every_entry_point(self) -> None:
        """AC1. Mutants: the refusal raised as a type refine and triage do not catch (a
        traceback); the check in one entry point only; a refused card falling back to the
        shipped default; the remedy naming the card's own seat or no command."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole", extra=" She is 42 years old."))
            runs = {
                "resolve --render review": (1, _resolve(root, "--render", "review")),
                "resolve --render build": (1, _resolve(root, "--render", "build")),
                "resolve-consult": (1, _cli(root, "persona_resolve.py", "resolve-consult",
                                            "--role", "qa", "--root", str(root))),
                "critic brief": (2, _cli(root, "critic.py", "brief", "--unit", "US0001",
                                         "--seat", "qa", "--root", str(root))),
                "refine apply": (2, _cli(root, "refine.py", "apply", "--request", "CR0001",
                                         "--epic-title", "Search", "--story",
                                         "index it|3|src/a.py", "--question", "q",
                                         "--dry-run", "--root", str(root))),
                "triage apply": (2, _cli(root, "triage.py", "apply", "--issue", "IS0001",
                                         "--bug", "null total|3|High|src/a.py", "--question",
                                         "q", "--dry-run", "--root", str(root))),
            }
            for name, (want, (rc, out, err)) in runs.items():
                with self.subTest(entry=name):
                    self.assertEqual(want, rc, err)
                    self.assertNotIn("Traceback", err)
                    self.assertEqual("", out.strip(), "a refused card frames nothing")
                    self.assertIn(QA, err)
                    self.assertIn("seat-demographic-fluff", err)
                    self.assertNotIn(str(SHIPPED_QA), out + err)
                    self.assertNotIn("templates/personas/amigos/qa.md", out + err)
                    # One command for the refused card; a panel's other seats may each be
                    # named as owed their own review.
                    remedies = [(c, s) for c, s in REMEDY_RE.findall(err) if c == QA]
                    self.assertEqual(1, len(remedies), err)
                    self.assertIn(remedies[0][1], ("engineering", "product"))
            # The remedy is a command that runs: it briefs the other seat on the refused card.
            line = next(ln for ln in err.splitlines()
                        if (m := REMEDY_RE.search(ln)) and m.group(1) == QA)
            argv = shlex.split(line[line.index("python3"):]) if "python3" in line else []
            self.assertEqual("python3", argv[0] if argv else None, line)
            rc, out, err = _cli(root, argv[1].split("/")[-1], *argv[2:], "--root", str(root))
            self.assertEqual(0, rc, err)
            self.assertIn(f"reviews {QA} against the persona standard", out)
            self.assertIn("seat-demographic-fluff", out)

    def test_the_sprint_briefs_refuse_a_blocked_card_without_a_traceback(self) -> None:
        """AC1, the sprint's two briefs that resolve a seat card. Mutants: `sprint lane brief`
        or `goal-review brief --seat` letting the refusal out as a traceback; either one
        framing the shipped card in place of the refused one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole", extra=" She is 42 years old."))
            _write(root, ENGINEERING, _seat("engineering", "Cal Dorn", extra=" He is married."))
            _write(root, "sdlc-studio/stories/US0002-a-ready-story.md",
                   "# US0002: A ready story\n\n> **Status:** Ready\n> **Affects:** src/a.py\n"
                   "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
                   "- **Verify:** file src/a.py\n")
            run_state.open_run(root, batch=["US0002"], goal="g")
            runs = {
                ("lane brief", ENGINEERING, "engineering"): _cli(
                    root, "sprint.py", "lane", "brief", "--units", "US0002", "--root", str(root)),
                ("goal-review brief", QA, "qa"): _cli(
                    root, "sprint.py", "goal-review", "brief", "--seat", "qa", "--root",
                    str(root)),
            }
            for (name, card, role), (rc, out, err) in runs.items():
                with self.subTest(entry=name):
                    self.assertEqual(2, rc, err)
                    self.assertNotIn("Traceback", err)
                    self.assertEqual("", out.strip(), "a refused card frames nothing")
                    self.assertIn(card, err)
                    self.assertIn("seat-demographic-fluff", err)
                    self.assertEqual(1, len([c for c, _ in REMEDY_RE.findall(err) if c == card]),
                                     err)
                    shipped = SCRIPTS.parent / "templates" / "personas" / "amigos" / f"{role}.md"
                    self.assertNotIn(str(shipped), out + err)

    def test_the_remedy_names_a_clear_seat_and_a_held_seat_is_refused_cleanly(self) -> None:
        """AC1, the remedy itself. Mutants: the remedy naming the first other seat whatever
        holds its own card; a seat's clearance read from every card's findings, not its own;
        `persona_review.py brief` letting a held reviewing seat out as a traceback."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole", extra=" She is 42 years old."))
            _write(root, ENGINEERING, _seat("engineering", "Cal Dorn", extra=" He is married."))
            rc, out, err = _resolve(root)
            self.assertEqual((1, ""), (rc, out.strip()), err)
            # engineering is first in the roster and held; product is the seat that is clear.
            self.assertEqual([(QA, "product")], REMEDY_RE.findall(err), err)
            self.assertRegex(err.splitlines()[-1], r"^Run next: python3 \S+persona_review\.py "
                             rf"brief --card {re.escape(QA)} --seat product$")
            rc, out, err = _cli(root, "persona_review.py", "brief", "--card", QA, "--seat",
                                "product", "--root", str(root))
            self.assertEqual(0, rc, err)
            self.assertIn(f"reviews {QA} against the persona standard", out)
            # Briefing the held seat is refused with its own card's refusal, never a traceback.
            rc, out, err = _cli(root, "persona_review.py", "brief", "--card", QA, "--seat",
                                "engineering", "--root", str(root))
            self.assertEqual(2, rc, err)
            self.assertNotIn("Traceback", err)
            self.assertEqual("", out.strip(), "a held reviewing seat frames no brief")
            self.assertTrue(err.startswith("persona_review brief refused: "), err)
            self.assertIn(f"{ENGINEERING} breaks the persona standard", err)
            self.assertIn("seat-demographic-fluff", err)

    def test_with_every_other_seat_held_the_remedy_names_no_brief(self) -> None:
        """AC1, no seat clear. Mutants: the remedy falling back to a brief for a held seat,
        which `persona_review.py brief` refuses; the owed line doing the same."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole", extra=" She is 42 years old."))
            _write(root, ENGINEERING, _seat("engineering", "Cal Dorn", extra=" He is married."))
            _write(root, PRODUCT, _seat("product", "Lena Marsh", extra=" She is 35 years old."))
            for name, want, (rc, out, err) in (
                    ("resolve", 1, _resolve(root)),
                    ("critic brief", 2, _cli(root, "critic.py", "brief", "--unit", "US0001",
                                             "--seat", "qa", "--root", str(root)))):
                with self.subTest(entry=name):
                    self.assertEqual(want, rc, err)
                    self.assertNotIn("Traceback", err)
                    self.assertEqual("", out.strip())
                    self.assertIn(f"{QA} breaks the persona standard", err)
                    self.assertEqual([], REMEDY_RE.findall(err), "no brief can run: " + err)
                    self.assertIn("No other seat is clear to review it: the engineering and "
                                  "product seat cards are each held too", err)
                    self.assertIn("persona_review.py record", err)
            # A clean qa card owed its review frames, and its one owed line names no brief.
            _write(root, QA, _seat("qa", "Ivy Cole", evidence=False))
            rc, out, err = _resolve(root)
            self.assertEqual(0, rc, err)
            self.assertIn("Ivy Cole reviews the work.", out)
            lines = [ln for ln in err.splitlines() if ln.strip()]
            self.assertEqual(1, len(lines), err)
            self.assertIn("persona review owed", lines[0])
            self.assertIn("No other seat is clear to review it", lines[0])
            self.assertEqual([], REMEDY_RE.findall(err), err)

    def test_a_failed_review_holds_only_its_own_card(self) -> None:
        """AC2, the FAIL's scope. Mutant: the latest review read as the ledger's last row for
        any card, so a FAIL on one seat card holds every other."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole"))
            _record(root, "fail", "Lena Marsh (product)", "2026-11-18", ["persona-evidence"],
                    card=ENGINEERING)
            rc, out, err = _cli(root, "persona_resolve.py", "resolve", "--seat", "engineering",
                                "--root", str(root))
            self.assertEqual(1, rc, "control: the FAIL holds its own card: " + err)
            self.assertIn("Lena Marsh (product)", err)
            rc, out, err = _resolve(root)
            self.assertEqual(0, rc, err)
            self.assertIn("Ivy Cole reviews the work.", out)
            self.assertNotIn("Lena Marsh (product)", err)
            lines = [ln for ln in err.splitlines() if ln.strip()]
            self.assertEqual(1, len(lines), err)
            self.assertIn(f"persona review owed: {QA} has no review recorded", lines[0])
            self.assertRegex(lines[0], r"meanwhile\. Run next: python3 \S+persona_review\.py "
                             rf"brief --card {re.escape(QA)} --seat product$")

    def test_a_failed_review_holds_until_a_later_review_passes(self) -> None:
        """AC2. Mutants: the FAIL honoured only while its hash equals the card's bytes; the
        refusal not naming the reviewer, the date or the rule; a PASS never lifting it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole"))
            self.assertEqual([], [f for f in persona_review.check(root, root / QA)
                                  if f["severity"] == persona_review.BLOCKS],
                             "premise: the card breaks no blocking rule")
            _record(root, "fail", "Cal Dorn (engineering)", "2026-11-18", ["persona-evidence"])
            _write(root, QA, _seat("qa", "Ivy Cole", extra=" She owns the release checks."))
            rc, out, err = _resolve(root)
            self.assertEqual(1, rc, err)
            self.assertEqual("", out.strip())
            for named in (QA, "Cal Dorn (engineering)", "2026-11-18", "persona-evidence"):
                with self.subTest(named=named):
                    self.assertIn(named, err)
            self.assertEqual(1, len(REMEDY_RE.findall(err)), err)
            _record(root, "pass", "Lena Marsh (product)", "2026-11-19")
            rc, out, err = _resolve(root)
            self.assertEqual(0, rc, err)
            self.assertIn("She owns the release checks.", out)
            self.assertEqual("", err.strip(), "a card PASSed as it stands is owed nothing")

    def test_an_unreviewed_card_resolves_and_is_named_owed(self) -> None:
        """AC3. Mutants: an unreviewed card refused; a reported rule treated as blocking; the
        owed line printed for a card PASSed as it stands, or more than once."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            never = base / "never"
            edited = base / "edited"
            for root in (never, edited):
                root.mkdir()
                _fixture(root, _seat("qa", "Ivy Cole", evidence=False))
                self.assertEqual(["persona-evidence"],
                                 [f["rule"] for f in persona_review.check(root, root / QA)],
                                 "premise: only a reported rule fails on the card")
            _record(edited, "pass", "Cal Dorn (engineering)", "2026-11-18")
            rc, out, err = _resolve(edited)
            self.assertEqual((0, ""), (rc, err.strip()), "control: PASSed as it stands")
            _write(edited, QA, _seat("qa", "Ivy Cole", extra=" She owns the release checks.",
                                     evidence=False))
            for root in (never, edited):
                with self.subTest(card=root.name):
                    rc, out, err = _resolve(root)
                    self.assertEqual(0, rc, err)
                    self.assertIn("Ivy Cole reviews the work.", out)
                    lines = [ln for ln in err.splitlines() if ln.strip()]
                    self.assertEqual(1, len(lines), err)
                    self.assertRegex(lines[0], r"(?i)persona review owed")
                    self.assertIn(QA, lines[0])

    def test_the_default_card_and_skip_personas_are_untouched(self) -> None:
        """AC4. Mutants: the shipped default judged against the project's ledger (a FAIL for a
        since-deleted qa card holding it); `--skip-personas` reading the ledger at all."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _fixture(root, _seat("qa", "Ivy Cole"))
            _record(root, "fail", "Cal Dorn (engineering)", "2026-11-18", ["persona-evidence"])
            ledger = (root / LEDGER).read_text(encoding="utf-8")
            skipped = _resolve(root, "--skip-personas")
            (root / LEDGER).unlink()
            self.assertEqual(_resolve(root, "--skip-personas"), skipped)
            self.assertEqual((0, "", ""), (skipped[0], skipped[1].strip(), skipped[2]))
            # In process, the ledger and the standard are not read at all under the flag.
            boom = mock.Mock(side_effect=AssertionError("read under --skip-personas"))
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(persona_review, "check", boom), \
                    mock.patch.object(persona_review, "ledger_rows", boom), \
                    redirect_stdout(out), redirect_stderr(err):
                rc = persona_resolve.main(["resolve", "--seat", "qa", "--root", str(root),
                                           "--skip-personas"])
            self.assertEqual((0, ""), (rc, err.getvalue()))
            boom.assert_not_called()
            # The qa card is deleted with its FAIL still in the ledger: the shipped default
            # resolves exactly as it does with no ledger present.
            (root / QA).unlink()
            _write(root, LEDGER, ledger)
            held = _resolve(root)
            (root / LEDGER).unlink()
            self.assertEqual(_resolve(root), held)
            rc, out, err = held
            self.assertEqual((0, ""), (rc, err))
            self.assertIn(SHIPPED_QA.read_text(encoding="utf-8").strip().splitlines()[0], out)


if __name__ == "__main__":
    unittest.main()
