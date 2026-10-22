"""US1093: `sprint.py lane brief` hands a fresh builder agent everything it needs for one unit.

The brief carries the unit's Affects, one path per line, and a commit step that stages exactly
those paths; the author self-check `critic.author_self_check` prints, verbatim; the self-check
record command and the command that runs the unit's criteria; and the engineering seat card's
work render to adopt. The toolchain runbook's delivery table builds each unit that way: a fresh
agent per unit (a fresh session where the harness has no subagents), waited on by its completion
notification and accepted back through `sprint.py lane return`.

The brief tests drive `sprint.py lane brief` in-process against a throwaway project with an
open run; the runbook test reads THIS repository's shipped runbook, as the criterion names it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import os
import re
import shlex
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
persona_resolve = loader.load_script("persona_resolve")
sprint = loader.load_script("sprint")
from lib import run_state, sdlc_md  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]
BATCH = ("US0101", "US0102")
# A parenthetical note and a test file and a fragment among the paths: the note is stripped only
# by `affects_files`, and the test file and fragment give the self-check something to name.
AFFECTS = {"US0101": "src/other.py, tests/test_other.py",
           "US0102": "src/app.py (new), tests/test_app.py, changelog.d/US0102.md"}
#: A project engineering seat with the work render and none of the review render's sections, so
#: resolving it for `render="review"` raises rather than returning the same path.
PROJECT_SEAT = ("<!-- role: engineering -->\n# Ola - the project's engineer\n\n"
                "## How They Work *(work render)*\n\nSmall diffs, test first.\n")


def _live(name: str):
    """The module the command resolves at call time. Another test module may re-register a
    sibling in `sys.modules`, so a patch on the object loaded here would miss the command."""
    return sys.modules.get(name) or importlib.import_module(name)


def _story(root: Path, uid: str, affects: str | None) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    field = f"> **Affects:** {affects}\n" if affects is not None else ""
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: x\n\n> **Status:** Ready\n{field}> **Points:** 2\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/app.py\n",
        encoding="utf-8")


def _project(d: str, affects: dict[str, str | None] | None = None) -> Path:
    """Two groomed Ready stories and an open run whose batch holds both."""
    root = Path(d) / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for uid in BATCH:
        _story(root, uid, (affects or AFFECTS).get(uid))
    run_state.open_run(root, batch=list(BATCH), goal="g")
    return root


def _brief(root: Path, uid: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["lane", "brief", "--units", uid, "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _unit_text(root: Path, uid: str) -> str:
    return (root / "sdlc-studio" / "stories" / f"{uid}-x.md").read_text(encoding="utf-8")


def _listed_affects(out: str) -> list[str]:
    """The paths under the brief's one Affects heading, one per indented line."""
    lines = out.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith("Affects (")]
    if len(heads) != 1:
        raise AssertionError(f"expected one Affects heading, found {len(heads)}:\n{out}")
    listed = []
    for ln in lines[heads[0] + 1:]:
        if not ln.startswith("  "):
            break
        listed.append(ln.strip())
    return listed


class _Isolated(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        transcripts = Path(self._tmp.name) / "transcripts"
        transcripts.mkdir()
        env = unittest.mock.patch.dict(os.environ,
                                       {run_state.TRANSCRIPTS_ENV: str(transcripts)})
        env.start()
        self.addCleanup(env.stop)


class BuilderBriefTests(_Isolated):

    def test_the_brief_names_the_affects_and_stages_only_them(self) -> None:
        """AC1. MUTANTS: the Affects popped from the brief before rendering, as `lane_dispatch`
        did, so no Affects list is printed; the raw field split on commas, which keeps the
        `(new)` note on a path; `git add -A` or `git commit -a` in the commit step, which sweeps
        a concurrent lane's files into this unit's commit; the batch's first unit named for the
        commit subject rather than the one briefed."""
        root = _project(self._tmp.name)
        out = _brief(root, "US0102")
        declared = sdlc_md.affects_files(_unit_text(root, "US0102"))
        self.assertEqual(["src/app.py", "tests/test_app.py", "changelog.d/US0102.md"],
                         declared, "premise: the note is stripped by the shared parser")
        self.assertEqual(declared, _listed_affects(out))
        lines = out.splitlines()
        adds = [i for i, ln in enumerate(lines) if ln.strip().startswith("git add")]
        self.assertEqual(1, len(adds), f"expected one staging command:\n{out}")
        self.assertEqual(["git", "add", "--", *declared], shlex.split(lines[adds[0]]))
        self.assertIn("US0102", lines[adds[0] - 1], "the commit step names the unit")
        self.assertIn("commit subject", lines[adds[0] - 1])
        self.assertNotIn("US0101", lines[adds[0] - 1])
        for sweep in ("git add -A", "git add .", "git commit -a", "git add --all"):
            self.assertNotIn(sweep, out)

    def test_a_unit_with_no_affects_is_told_so_and_stages_nothing(self) -> None:
        """MUTANT: an empty Affects rendered as an empty list and a bare `git add --`, which
        stages nothing and reads as a step done."""
        root = _project(self._tmp.name, {"US0101": "src/other.py", "US0102": None})
        out = _brief(root, "US0102")
        self.assertEqual([], sdlc_md.affects_files(_unit_text(root, "US0102")), "premise")
        self.assertIn("Affects: NONE DECLARED", out)
        self.assertNotIn("git add", out)
        self.assertIn("declares no Affects, so there is no path to stage", out)

    def test_the_brief_carries_the_self_check_and_the_commands_for_this_unit(self) -> None:
        """AC2. MUTANTS: the self-check steps retyped in sprint.py, so the brief keeps them when
        `author_self_check` changes; the self-check left out; either command carrying another
        unit's id (the batch's first, US0101); a command printed before the self-check."""
        root = _project(self._tmp.name)
        real = critic.author_self_check(root, "US0102")
        out = _brief(root, "US0102")
        self.assertIn(real, out, "the self-check, verbatim")
        after = out.index(real) + len(real)
        record = "critic.py self-check record --unit US0102 "
        verify = "verify_ac.py run --id US0102"
        self.assertGreater(out.find(record, after), -1, "the record command after the self-check")
        self.assertGreater(out.find(verify, after), -1, "the verify command after the self-check")
        named = [ln for ln in out[after:].splitlines()
                 if "self-check record" in ln or "verify_ac.py" in ln]
        self.assertTrue(named and all("US0101" not in ln for ln in named), named)

        stub = "STUB SELF-CHECK for {unit}\nsecond line of the stub"
        with unittest.mock.patch.object(
                _live("critic"), "author_self_check", lambda _root, unit: stub.format(unit=unit)):
            changed = _brief(root, "US0102")
        self.assertIn(stub.format(unit="US0102"), changed, "the brief follows the replacement")
        self.assertNotIn(real, changed)
        after = changed.index("second line of the stub")
        self.assertGreater(changed.find(record, after), -1)
        self.assertGreater(changed.find(verify, after), -1)

    def test_the_brief_names_the_engineering_seats_work_render(self) -> None:
        """AC3. MUTANTS: the shipped default's path hard-coded, which shadows the project's own
        seat; the review render named, or the card resolved with `render="review"`, which
        raises on a project card that carries only its work render."""
        root = _project(self._tmp.name)
        shipped = persona_resolve.resolve_card(root, "engineering", render="build")
        self.assertEqual(SKILL / "templates" / "personas" / "amigos" / "engineering.md",
                         shipped, "premise: with no project card the shipped default resolves")
        self.assertEqual([str(shipped)], self._seat_paths(_brief(root, "US0101")))

        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "ola.md").write_text(PROJECT_SEAT, encoding="utf-8")
        own = persona_resolve.resolve_card(root, "engineering", render="build")
        self.assertEqual(seats / "ola.md", own, "premise: the project card resolves")
        out = _brief(root, "US0101")
        self.assertEqual([str(own)], self._seat_paths(out))
        self.assertNotIn(str(shipped), out)

    def test_a_project_with_no_engineering_card_is_told_so(self) -> None:
        """MUTANT: no seat line when nothing resolves, which reads the same as a brief that
        never looked."""
        root = _project(self._tmp.name)
        with unittest.mock.patch.object(_live("persona_resolve"), "resolve_card",
                                        lambda *a, **k: None):
            out = _brief(root, "US0101")
        self.assertIn("Seat: no engineering seat card resolves", out)

    def _seat_paths(self, out: str) -> list[str]:
        """The card each Seat line names as the work render to adopt."""
        seat = [ln for ln in out.splitlines() if ln.startswith("Seat: ")]
        self.assertEqual(1, len(seat), out)
        self.assertNotIn("review render", seat[0])
        m = re.fullmatch(r"Seat: adopt the work render of the engineering seat card (\S+) - .+",
                         seat[0])
        self.assertIsNotNone(m, seat[0])
        return [m.group(1)]


#: The rows the deliver table must hold, as (Do, Command, Instead of) cells.
DELIVER_ROWS = (
    ("Build a unit",
     "`sprint.py lane brief --units <id>`, handed to a fresh agent; a harness without "
     "subagents starts a fresh session per unit from the same brief",
     "building it in the orchestrating context"),
    ("Wait for the builder", "its completion notification", "polling its output or sleeping"),
    ("Accept its return", "`sprint.py lane return --units <id>`",
     "reading the builder's diff or transcript into the orchestrating context"),
)


class BuilderRunbookTests(unittest.TestCase):

    def test_the_deliver_table_builds_each_unit_in_a_fresh_agent(self) -> None:
        """AC4. MUTANTS: a row missing; a Command cell naming another command; the rule stated as
        prose under the table, which is no row; the build row with no fallback for a harness
        without subagents."""
        text = (SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        m = re.search(r"(?ms)^## 3\. Deliver a unit\n(.*?)(?=^## |\Z)", text)
        self.assertIsNotNone(m, "the runbook has no `## 3. Deliver a unit` section")
        tables = list(sdlc_md.iter_tables(m.group(1)))
        self.assertEqual(1, len(tables))
        self.assertEqual(["Do", "Command", "Instead of"], tables[0]["header"])
        rows = [tuple(cells) for _n, cells in tables[0]["rows"]]
        for row in DELIVER_ROWS:
            self.assertIn(row, rows)


if __name__ == "__main__":
    unittest.main()
