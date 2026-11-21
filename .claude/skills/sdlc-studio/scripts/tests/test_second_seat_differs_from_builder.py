"""BG1609: a high-class unit's second review seat is never the seat that built it.

`sprint plan` gave every high-class unit a second review seat of engineering, and `sprint lane
brief` builds every unit under the engineering seat unless told otherwise, so the builder and the
second seat were one seat holder: `critic.py brief --seat engineering` printed a record command
naming the author as reviewer, with a note calling it a self-review, and the plan named no other
seat to brief. Driven through the shipped entry points against a throwaway project: `sprint plan`
names the second seat, `sprint lane brief` (no --seat) records the building seat, and `critic.py
brief` at the planned second seat prints the record command. The record command's `--author` is
the lane's recorded seat, the 'Dani Okafor (engineering)' that `lane land --author` names.

MUTANTS, each of which a test here fails on: (1) the second seat skips only the first review
seat, so it is engineering again; (2) the second seat is the first review seat, qa; (3) a project
whose own seats are only qa and the building seat gets the building seat back; (4) the shipped
seats are searched before the project's own, so a project whose own seats are engineering, qa
and security gets product, a seat it does not hold.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import shlex
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
from lib import run_state  # noqa: E402

UID = "US0001"
BUILDER = "Dani Okafor (engineering)"
_MAP = "risk:\n  components:\n    src/pay: high\n"
CARD = ("<!-- role: {role} -->\n# {holder} - {role} seat\n\n## Lens\n\nx\n\n"
        "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")


def _live(name: str):
    """The module the command resolves at call time; another test module may re-register it."""
    return sys.modules.get(name) or importlib.import_module(name)


def _call(script: str, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live(script).main(list(argv))
    return rc, out.getvalue(), err.getvalue()


def _project(d: str) -> Path:
    """One groomed Ready story tagged Risk-class high, touching the high component, and the
    project's own three seat cards, each naming its holder."""
    root = Path(d) / "repo"
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (root / "src" / "pay").mkdir(parents=True)
    (root / "src" / "pay" / "charge.py").write_text("", encoding="utf-8")
    (stories / f"{UID}-take-a-payment.md").write_text(
        f"# {UID}: take a payment\n\n> **Status:** Ready\n> **Affects:** src/pay/charge.py\n"
        "> **Points:** 2\n> **Risk-class:** high\n\n## Acceptance Criteria\n\n"
        "### AC1: the charge is taken once\n\n- **Verify:** shell true\n", encoding="utf-8")
    (root / "wl.md").write_text(f"{UID}\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(_MAP, encoding="utf-8")
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    for role, holder in (("engineering", "Dani Okafor"), ("qa", "Sam Eriksson"),
                         ("product", "Lena Marsh")):
        (seats / f"{role}.md").write_text(CARD.format(role=role, holder=holder),
                                          encoding="utf-8")
    return root


def _record_line(err: str) -> list[str]:
    """The record command's words, from the footer the brief prints to stderr."""
    line = next((ln for ln in err.splitlines() if "critic.py record --unit" in ln), None)
    if line is None:
        raise AssertionError(f"the brief printed no record command:\n{err[-2000:]}")
    return shlex.split(line.split("record the verdict with:", 1)[1])


def _flag(words: list[str], flag: str) -> str:
    return words[words.index(flag) + 1]


class SecondSeatNotBuilderTests(unittest.TestCase):

    def test_the_planned_second_seat_is_not_the_building_seat(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, out, err = _call("sprint", "plan", "--worklist", str(root / "wl.md"),
                                 "--root", str(root), "--format", "json", "--no-fetch")
            self.assertEqual(0, rc, err)
            second = json.loads(out)["risk_classes"]["units"][UID]["second_seat"]
            self.assertIn(f"second review seat: {second}", err)
            self.assertNotIn(second, ("engineering", sprint.FIRST_REVIEW_SEAT),
                             "the second seat is the building seat or the first review seat")
            run_state.open_run(root, batch=[UID], goal="the charge is taken once")
            rc, _out, err = _call("sprint", "lane", "brief", "--units", UID, "--root", str(root))
            self.assertEqual(0, rc, err)
            self.assertEqual("engineering", run_state.lane_seat(root, UID),
                             "the lane brief recorded no building seat")
            rc, out, err = _call("critic", "--root", str(root), "brief", "--unit", UID,
                                 "--seat", second)
            self.assertEqual(0, rc, err)
            words = _record_line(err)
            self.assertEqual(BUILDER, _flag(words, "--author"))
            self.assertNotEqual(BUILDER, _flag(words, "--reviewer"),
                                "the second seat's record command names the author as reviewer")
            self.assertRegex(_flag(words, "--reviewer"), rf"\({re.escape(second)}\)$")
            self.assertNotIn("self-review", out + err)
            # THE CONTROL: briefing the building seat itself is still named a self-review, so
            # the absence above is the seat's doing, not a note that can no longer print.
            rc, out, err = _call("critic", "--root", str(root), "brief", "--unit", UID,
                                 "--seat", "engineering")
            self.assertEqual(0, rc, err)
            words = _record_line(err)
            self.assertEqual(BUILDER, _flag(words, "--reviewer"))
            self.assertIn("self-review; brief another seat", err)

    def test_a_project_with_only_qa_and_the_building_seat_gets_a_third(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            for role in ("qa", "engineering"):
                (seats / f"{role}.md").write_text(f"<!-- role: {role} -->\n# {role} seat\n",
                                                  encoding="utf-8")
            self.assertEqual(["engineering", "qa"], sprint.review_seats(root)[0])
            self.assertEqual("product", sprint.second_review_seat(root))

    def test_a_projects_own_seat_comes_before_the_shipped_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            for role in ("engineering", "qa", "security"):
                (seats / f"{role}.md").write_text(f"<!-- role: {role} -->\n# {role} seat\n",
                                                  encoding="utf-8")
            self.assertEqual((["engineering", "qa", "security"], False),
                             sprint.review_seats(root))
            self.assertEqual("security", sprint.second_review_seat(root),
                             "the second seat is a shipped seat the project does not hold")


if __name__ == "__main__":
    unittest.main()
