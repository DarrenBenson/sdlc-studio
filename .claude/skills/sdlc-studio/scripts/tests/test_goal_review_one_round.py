"""US1096: one goal-review round by default.

An amendment carried only the requesting seat's verdict forward, so every other seat was
reported as owing a verdict on the reworded goal. It now carries every seat's verdict unless
that seat asked to re-review, and an operator's amendment of an OPEN run's goal moves the goal
the close judges. Every case runs the shipped CLI in a
temporary project; the fixtures are built once and copied per case.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")

G = "ship the parser to users"
G2 = "ship the renderer to users"
SEATS = ("engineering", "product", "qa")
_TEMPLATES: dict[str, Path] = {}


def _cli(root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(_SCRIPTS / script), *argv, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300)


def _ok(r: subprocess.CompletedProcess) -> str:
    if r.returncode != 0:
        raise AssertionError(f"exited {r.returncode}:\n{r.stdout}\n{r.stderr}")
    return r.stdout + r.stderr


def _record(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return _cli(root, "sprint.py", "goal-review", "record", *argv)


def _plan(root: Path, goal: str, *argv: str) -> str:
    return _ok(_cli(root, "sprint.py", "plan", "--stories", "Ready", "--no-fetch",
                    "--sprint-goal", goal, *argv))


def _owing(out: str) -> list[str]:
    return [ln for ln in out.splitlines() if "owing a verdict" in ln]


def _local(root: Path, name: str) -> Path:
    return root / "sdlc-studio" / ".local" / name


def _bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def setUpModule() -> None:
    """Two projects, built once: `base` (initialised, one Ready story, the shipped seats) and
    `run` (its own four seats, one of them `operator`, a goal review of G and a run opened on G
    by `plan --write`)."""
    home = Path(tempfile.mkdtemp(prefix="us1096_"))
    base = home / "base"
    subprocess.run(["git", "init", "-q", str(base)], env=gitutil.git_env(), check=True,
                   capture_output=True)
    _ok(_cli(base, "init.py", "run"))
    stories = base / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    (stories / "US0001-s.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n> **Points:** 2\n"
        "> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: works\n\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    run = home / "run"
    shutil.copytree(base, run)
    cards = run / "sdlc-studio" / "personas" / "seats"
    cards.mkdir(parents=True, exist_ok=True)
    for role in (*SEATS, "operator"):
        (cards / f"{role}.md").write_text(f"<!-- role: {role} -->\n# {role}\n", encoding="utf-8")
    _ok(_record(run, "--goal", G, *[a for r in SEATS for a in ("--seat", f"{r}|yes|done|yes")],
                "--seat", "operator|no|done|yes|too large for one sprint"))
    _plan(run, G, "--write")
    _TEMPLATES.update(home=home, base=base, run=run)


def tearDownModule() -> None:
    shutil.rmtree(_TEMPLATES["home"], ignore_errors=True)


class _Copies(unittest.TestCase):

    def _copy(self, name: str) -> Path:
        d = Path(tempfile.mkdtemp(prefix=f"us1096_{name}_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        dest = d / name
        shutil.copytree(_TEMPLATES[name], dest)
        return dest


class OneRoundTests(_Copies):

    def _seed(self, root: Path, *seats: str) -> None:
        _ok(_record(root, "--goal", G, *[a for s in seats for a in ("--seat", s)]))

    def test_an_amendment_carries_every_verdict_forward(self) -> None:
        """AC1. MUTANT: today's carry - only the requesting seat's verdict carries forward, so
        engineering and product owe a second round (`needs_reconsult` non-empty)."""
        root = self._copy("base")
        self._seed(root, *(f"{r}|yes|done|yes" for r in SEATS))
        _ok(_record(root, "--goal", G2, "--amend-from", G, "--requesting-seat", "qa"))
        latest = sprint.goal_review_rounds(sprint.goal_review(root))[-1]
        self.assertEqual(sorted(SEATS), sorted(s["seat"] for s in latest["seats"]))
        self.assertTrue(all(s.get("carried_from") == G for s in latest["seats"]))
        status = sprint.goal_review_status(root, G2)
        self.assertTrue(status["reviewed"])
        self.assertEqual([], status["needs_reconsult"])
        out = _plan(root, G2)
        self.assertIn(f"3 seat(s) examined \"{G2}\"", out)
        self.assertEqual([], _owing(out))

    def test_only_a_seat_that_asked_is_re_consulted(self) -> None:
        """AC2. MUTANTS: (1) `rereview` parsed and then ignored - qa carries and nobody owes;
        (2) the sixth `--seat` field read as part of the note - the same; (3) a material change
        carrying verdicts - its round holds seats and the plan names fewer than three."""
        for form in ("fields-file", "seat"):
            with self.subTest(form):
                root = self._copy("base")
                if form == "seat":
                    self._seed(root, "engineering|yes|done|yes|fine|no", "product|yes|done|yes",
                               "qa|yes|done|yes|show me the test plan|yes")
                else:
                    fields = root / "fields.json"
                    fields.write_text(json.dumps({"goal": G, "seats": [
                        {"seat": r, "achievable": "yes", "done_means": "done",
                         "one_increment": "yes", **({"rereview": "yes"} if r == "qa" else {})}
                        for r in SEATS]}), encoding="utf-8")
                    _ok(_record(root, "--fields-file", str(fields)))
                first = sprint.goal_review_rounds(sprint.goal_review(root))[-1]["seats"]
                self.assertEqual("yes", next(s for s in first if s["seat"] == "qa")["rereview"])
                _ok(_record(root, "--goal", G2, "--amend-from", G,
                            "--requesting-seat", "engineering"))
                latest = sprint.goal_review_rounds(sprint.goal_review(root))[-1]
                self.assertEqual(["engineering", "product"],
                                 sorted(s["seat"] for s in latest["seats"]))
                self.assertEqual(["qa"], sprint.goal_review_status(root, G2)["needs_reconsult"])
                owing = _owing(_plan(root, G2))
                self.assertEqual(1, len(owing), owing)
                self.assertIn("qa", owing[0])
                self.assertNotIn("engineering", owing[0])
                self.assertNotIn("product", owing[0])
        # A material change carries none, and every seat owes a verdict on the new wording.
        material = "ship the whole product to users"
        _ok(_record(root, "--goal", material, "--amend-from", G, "--material"))
        latest = sprint.goal_review_rounds(sprint.goal_review(root))[-1]
        self.assertEqual([], latest["seats"])
        self.assertEqual("material", latest["change_type"])
        status = sprint.goal_review_status(root, material)
        self.assertFalse(status["reviewed"])
        self.assertEqual(sorted(SEATS), status["needs_reconsult"])
        owing = _owing(_plan(root, material))
        self.assertEqual(1, len(owing), owing)
        for seat in SEATS:
            self.assertIn(seat, owing[0])

    def test_a_rereview_answer_outside_yes_and_no_is_refused(self) -> None:
        """MUTANT: an unreadable `rereview` stored, or dropped, rather than refused - a seat that
        asked to re-review would then have its verdict carried as though it had not."""
        root = self._copy("base")
        fields = root / "fields.json"
        fields.write_text(json.dumps({"goal": G, "seats": [
            {"seat": "qa", "achievable": "yes", "done_means": "done", "one_increment": "yes",
             "rereview": "maybe"}]}), encoding="utf-8")
        for argv in (("--fields-file", str(fields)),
                     ("--goal", G, "--seat", "qa|yes|done|yes|a note|maybe")):
            with self.subTest(argv[0]):
                r = _record(root, *argv)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn("rereview", r.stderr)
                self.assertIsNone(_bytes(_local(root, "goal-review.json")))
        # the positive control: a five-field --seat keeps its note and asks for nothing
        _ok(_record(root, "--goal", G, "--seat", "qa|yes|done|yes|a note"))
        seat = sprint.goal_review_rounds(sprint.goal_review(root))[-1]["seats"][0]
        self.assertEqual("a note", seat["note"])
        self.assertNotIn("rereview", seat)


class OpenRunGoalAmendTests(_Copies):

    def _amend(self, root: Path, goal: str, frm: str = G) -> subprocess.CompletedProcess:
        return _record(root, "--goal", goal, "--amend-from", frm, "--requested-by", "operator")

    def test_an_operator_amendment_moves_the_goal_the_close_judges(self) -> None:
        """AC3. MUTANTS: (1) the run state left untouched; (2) the operator passed as a seat
        role, so the `operator` seat's objection is discharged; (3) the run goal moved to
        whatever `--amend-from` names; (4) an amendment accepted after the goal verdict."""
        root = self._copy("run")
        before = sprint.run_state.read(root)
        self.assertEqual(G, before["sprint_goal"])
        _ok(self._amend(root, G2))
        latest = sprint.goal_review_rounds(sprint.goal_review(root))[-1]
        self.assertEqual("operator", latest["requested_by"])
        self.assertNotIn("requesting_seat", latest)
        self.assertEqual(sorted((*SEATS, "operator")), sorted(s["seat"] for s in latest["seats"]))
        status = sprint.goal_review_status(root, G2)
        self.assertEqual([], status["needs_reconsult"])
        self.assertEqual([], status["discharged"])
        self.assertEqual(["operator"], [o["seat"] for o in status["objections"]])
        state = sprint.run_state.read(root)
        self.assertEqual(G2, state["sprint_goal"])
        amended = state["sprint_goal_amendments"][-1]
        self.assertEqual((G, G2, "operator"),
                         (amended["from"], amended["to"], amended["requested_by"]))
        # the plan's record keeps the goal as planned
        self.assertEqual(G, json.loads(_bytes(_local(root, "sprint-plan.json")))["sprint_goal"])
        self.assertEqual(G, state["sprint_goal_review"]["goal"])
        self.assertEqual(before["plan_snapshot"], state["plan_snapshot"])
        # the close judges the amended wording
        judged = "\n".join(sprint.close_goal_judgement(root, {**state, "author": "builder"}))
        self.assertIn(G2, judged)
        self.assertNotIn(G, judged)

        # An --amend-from that is not the open run's goal leaves the run state unchanged.
        root = self._copy("run")
        other = "ship the linter to users"
        _ok(_record(root, "--goal", other, "--seat", "qa|yes|done|yes"))
        run_before = _bytes(_local(root, "run-state.json"))
        _ok(self._amend(root, "ship the formatter to users", frm=other))
        self.assertEqual(run_before, _bytes(_local(root, "run-state.json")))

        # With no run open, an operator amendment is recorded and no run state is written.
        root = self._copy("base")
        _ok(_record(root, "--goal", G, "--seat", "qa|yes|done|yes"))
        _ok(self._amend(root, G2))
        self.assertIsNone(_bytes(_local(root, "run-state.json")))
        self.assertEqual(G2, sprint.goal_review_rounds(sprint.goal_review(root))[-1]["goal"])

        # After the run's goal verdict, the amendment is refused naming that verdict.
        root = self._copy("run")
        _ok(_cli(root, "sprint.py", "goal-verdict", "--verdict", "partial",
                 "--note", "the parser shipped, its docs did not"))
        review_before = _bytes(_local(root, "goal-review.json"))
        run_before = _bytes(_local(root, "run-state.json"))
        r = self._amend(root, G2)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("partial", r.stderr)
        self.assertEqual(review_before, _bytes(_local(root, "goal-review.json")))
        self.assertEqual(run_before, _bytes(_local(root, "run-state.json")))

    def test_an_amended_goal_over_twenty_words_is_refused_and_nothing_is_written(self) -> None:
        """AC4. MUTANTS: (1) the length check skipped on the amendment path; (2) the round
        appended before the refusal; (3) the limit read as exclusive - 20 words refused."""
        root = self._copy("run")
        review_before = _bytes(_local(root, "goal-review.json"))
        run_before = _bytes(_local(root, "run-state.json"))
        long_goal = " ".join(["word"] * sprint.GOAL_WORD_LIMIT + ["more"])
        self.assertEqual(21, len(long_goal.split()))
        for argv in (("--requested-by", "operator"), ("--requesting-seat", "qa")):
            with self.subTest(argv[0]):
                r = _record(root, "--goal", long_goal, "--amend-from", G, *argv)
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn("21 words", r.stderr)
                self.assertIn(f"limit is {sprint.GOAL_WORD_LIMIT}", r.stderr)
                self.assertEqual(review_before, _bytes(_local(root, "goal-review.json")))
                self.assertEqual(run_before, _bytes(_local(root, "run-state.json")))
        # the positive control: twenty words is within the limit and moves the run's goal
        twenty = " ".join(["word"] * sprint.GOAL_WORD_LIMIT)
        _ok(self._amend(root, twenty))
        self.assertEqual(twenty, sprint.run_state.read(root)["sprint_goal"])


if __name__ == "__main__":
    unittest.main()
