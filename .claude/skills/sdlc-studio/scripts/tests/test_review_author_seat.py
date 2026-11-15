"""US1061: a unit's review record names the seat that built it, and the seat reviewing it.

`sprint lane brief --seat <role>` (default engineering) names the building seat and records it
on the lane start; the review brief's record command then carries `--author "<holder> (<role>)"`
for that seat and `--reviewer "<holder> (<role>)"` for the seat being briefed, so every row it
records names both seats in the form `critic.recorded_seat` reads. `critic.py record` warns,
and never refuses, when a project declares seats and the author names none.

Every case drives `sprint.py` and `critic.py` through their entry points in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
SPRINT = SCRIPTS / "sprint.py"
critic = loader.load_script("critic")

sys.path.insert(0, str(SCRIPTS))
from lib import run_state  # noqa: E402

SEATS = {"engineering": "Dani Okafor", "qa": "Sam Eriksson", "product": "Lena Marsh"}


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, run: bool = True) -> None:
    """Two stories and three seat cards, with a run open over both."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    for role, holder in SEATS.items():
        _write(root, f"sdlc-studio/personas/seats/{role}.md",
               f"<!-- role: {role} -->\n# {holder} - {role} seat\n\ncharter\n")
    for uid in ("US0001", "US0002"):
        _write(root, f"sdlc-studio/stories/{uid}-widget.md",
               f"# {uid}: widget\n\n> **Status:** Ready\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")
    if run:
        run_state.open_run(root, batch=["US0001", "US0002"])


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), *args], capture_output=True,
                          text=True, timeout=300, env=gitutil.git_env(), check=False)


def _lane(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = _run(SPRINT, "lane", "brief", *args, "--root", str(root))
    assert r.returncode == 0, r.stderr
    return r


def _footer(root: Path, unit: str, seat: str) -> tuple[dict, str]:
    """The record command the review brief's footer prints, as {flag: value}, and its stderr."""
    r = _run(CRITIC, "brief", "--unit", unit, "--seat", seat, "--root", str(root))
    assert r.returncode == 0, r.stderr
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", r.stderr, re.M)
    assert m, r.stderr
    argv = shlex.split(m.group(1))
    return {a: argv[i + 1] for i, a in enumerate(argv[:-1]) if a.startswith("--")}, r.stderr


class ReviewAuthorSeatTests(unittest.TestCase):

    def test_the_record_command_names_the_seat_that_built_the_unit(self) -> None:
        """AC1. Mutants: the footer prints a fixed author or none; the lane's seat is never
        recorded, so a QA-built unit's footer still names the engineering holder."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            out = _lane(root, "--units", "US0001").stdout
            self.assertRegex(out, r"(?m)^Building seat: Dani Okafor \(engineering\)")
            flags, _ = _footer(root, "US0001", "product")
            self.assertEqual("Dani Okafor (engineering)", flags.get("--author"))
            out = _lane(root, "--units", "US0002", "--seat", "qa").stdout
            self.assertRegex(out, r"(?m)^Building seat: Sam Eriksson \(qa\)")
            self.assertRegex(out, r"(?m)^Seat: adopt the work render of the qa seat card \S+qa\.md")
            flags, err = _footer(root, "US0002", "product")
            self.assertEqual("Sam Eriksson (qa)", flags.get("--author"))
            self.assertNotIn("no lane recorded", err)
            # a later lane on another unit leaves this one's builder where it was: the fallback
            # is engineering, so only the qa-built unit can tell a kept record from a lost one
            _lane(root, "--units", "US0001")
            self.assertEqual("Sam Eriksson (qa)", _footer(root, "US0002", "product")[0]
                             .get("--author"))

    def test_an_unbriefed_unit_names_the_engineering_holder_and_says_so(self) -> None:
        """No lane record for the unit: the footer falls back to the engineering holder and one
        line says no lane recorded the builder, rather than guessing silently."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, run=False)
            flags, err = _footer(root, "US0001", "qa")
            self.assertEqual("Dani Okafor (engineering)", flags.get("--author"))
            self.assertEqual(1, err.count("no lane recorded the seat that built US0001"), err)

    def test_a_seatless_author_is_named_and_recorded(self) -> None:
        """AC2. Mutant: the author's seat read by `seat_for`'s name heuristic, which matches the
        word `engineering` in `engineering-seat build worker` and passes it silently."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            seatless = "engineering-seat build worker"
            r = _run(CRITIC, "record", "--unit", "US0001", "--verdict", "APPROVE",
                     "--reviewer", "Lena Marsh (product)", "--author", seatless,
                     "--root", str(root))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual(seatless, critic.read_verdicts(root)[-1]["author"])
            warned = [ln for ln in r.stderr.splitlines() if seatless in ln]
            self.assertEqual(1, len(warned), r.stderr)
            self.assertIn("<holder> (<role>)", warned[0])
            self.assertIn("Dani Okafor (engineering)", warned[0])
            r = _run(CRITIC, "record", "--unit", "US0001", "--verdict", "APPROVE",
                     "--reviewer", "Lena Marsh (product)", "--author",
                     "Dani Okafor (engineering)", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("Dani Okafor (engineering)", critic.read_verdicts(root)[-1]["author"])
            self.assertNotIn("<holder> (<role>)", r.stderr)
            self.assertNotIn("author '", r.stderr)

    def test_a_project_without_seats_hears_nothing_about_the_author(self) -> None:
        """A headless project declares no seat, so there is no seat for an author to name."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            for card in (root / "sdlc-studio" / "personas" / "seats").glob("*.md"):
                card.unlink()
            r = _run(CRITIC, "record", "--unit", "US0001", "--verdict", "APPROVE",
                     "--reviewer", "reviewer-1", "--author", "builder-1", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertNotIn("<holder> (<role>)", r.stderr)

    def test_the_footer_names_the_seat_as_reviewer(self) -> None:
        """AC3. Mutants: the footer omits --reviewer, or writes the role in free text, so a
        recorded Reviewer cell names no seat `recorded_seat` can read."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            flags, _ = _footer(root, "US0001", "qa")
            self.assertEqual("Sam Eriksson (qa)", flags.get("--reviewer"))
            self.assertEqual("qa", critic.recorded_seat(flags["--reviewer"]))
            flags, err = _footer(root, "US0001", "engineering")
            self.assertEqual("Dani Okafor (engineering)", flags.get("--reviewer"))
            self.assertEqual("engineering", critic.recorded_seat(flags["--reviewer"]))
            # the seat that built the unit reviewing it is a self-review, and is said to be one
            self.assertIn("self-review", err)

    def test_recorded_seat_reads_the_first_role_group(self) -> None:
        """The public reader: the first `(<role>)` or `(<role> seat)` group, nothing else."""
        cases = {
            "Sam Eriksson (qa) re-checking the product finding": "qa",
            "Claude Opus 5.5 (engineering seat)": "engineering",
            "Lena Marsh (Product)": "product",
            "engineering-seat build worker": None,
            "independent-critic": None,
            "Claude Opus 5.5 (run thirteen grooming, D0479)": None,
            "": None,
        }
        for cell, role in cases.items():
            self.assertEqual(role, critic.recorded_seat(cell), cell)


if __name__ == "__main__":
    unittest.main()
