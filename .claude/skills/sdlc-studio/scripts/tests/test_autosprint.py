"""Unit tests for `autosprint.py` - the alias the sprint command kept when it was renamed.

The alias is four lines of re-export, so the thing worth binding is not the shim's own body
but what an operator still reaches through it: the sprint lifecycle. These tests therefore
drive the whole primary path through `autosprint.main` - plan opens the run, the batch is
worked, close runs the ceremony chain and seals the run - and assert on the run state the
path leaves behind, never on the absence of an exception.

Two things the alias itself owes are pinned directly: it re-exports the SAME objects sprint
defines (a copy that drifted would be a second implementation), and running it names its
replacement.

The close chain's steps that delegate to another module (retro, lessons, gate, reconcile)
are stubbed, as `test_sprint_rolling.py` stubs them: those modules have their own suites, and
what is under test here is the chain's own control flow. `handoff` runs for real, because it
is the step that closes the run object - the state every assertion below reads.

`test_the_suite_kills_a_loop_control_mutant` is the anti-vacuity proof. It copies the scripts
tree, makes the chain loop swallow a failing step at the CALL SITE, and re-runs the loop test
against the copy in a child process, asserting it goes red - having first asserted that the
same test goes GREEN against an unmutated copy, so a mutant "killed" by a broken harness is
not mistaken for a mutant killed by the test.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ - shared helpers
sys.path.insert(0, str(SCRIPTS))                          # scripts/ - autosprint's `import sprint`

import gitutil  # noqa: E402 - the confined git environment every fixture subprocess runs under


def _load_alias():
    """Load `autosprint.py` under a private module name.

    Its own name is irrelevant to the chain-step lookup - `cmd_close` resolves each step
    through `sys.modules["sprint"]`, because that is the module the re-exported function was
    defined in - so the stubs below patch THAT module, whichever instance of it a sibling
    suite left registered. A private name here only keeps this suite from becoming the
    `autosprint` any other suite would import.
    """
    spec = importlib.util.spec_from_file_location("autosprint_sut", SCRIPTS / "autosprint.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["autosprint_sut"] = mod
    spec.loader.exec_module(mod)
    # The instance the alias bound its names FROM, captured here because a sibling suite that
    # loads sprint.py by path replaces `sys.modules["sprint"]` afterwards. Identity is asked of
    # this one; the chain-step stubs still go to whatever is registered at call time, which is
    # where the running `cmd_close` looks them up.
    return mod, sys.modules["sprint"]


autosprint, sprint_at_load = _load_alias()
run_state = sprint_at_load.run_state

#: The chain steps that delegate to another module, stubbed green - DERIVED from the chain
#: minus the two that deliberately run for real, so a step added to the ceremony is stubbed by
#: default instead of silently reddening this suite. `handoff` and `review-anchor` are the
#: stated exceptions; keeping them as an exclusion list rather than an inclusion list is what
#: makes the intent survive a new step.
_RUNS_FOR_REAL = ("handoff", "review_anchor")
_DELEGATING = tuple(s.replace("-", "_") for s in sprint_at_load._CLOSE_CHAIN
                    if s.replace("-", "_") not in _RUNS_FOR_REAL)

_INDEXES = (("bugs", "Bugs"), ("stories", "Stories"), ("epics", "Epics"),
            ("change-requests", "Change Requests"), ("retros", "Retros"),
            ("handoffs", "Handoffs"), ("reviews", "Reviews"), ("rfcs", "RFCs"))


# --- fixtures ---------------------------------------------------------------------

def _ws(root: Path) -> Path:
    """A minimal but complete workspace: every artefact directory with a real index table."""
    sd = root / "sdlc-studio"
    for sub, hdr in _INDEXES:
        (sd / sub).mkdir(parents=True, exist_ok=True)
        (sd / sub / "_index.md").write_text(
            f"# {hdr}\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    return sd


def _bug_path(root: Path, num: int) -> Path:
    return root / "sdlc-studio" / "bugs" / f"BG{num:04d}-x.md"


def _bug(root: Path, num: int, status: str = "Open", points: int = 2) -> None:
    """A groomed bug - `sprint plan` refuses an ungroomed batch, and a fixture that could not
    be planned would be testing the grooming gate rather than the path under test."""
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    f = root / f"src/bg{num:04d}.py"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("", encoding="utf-8")
    _bug_path(root, num).write_text(
        f"# BG{num:04d}: b{num}\n\n> **Status:** {status}\n> **Severity:** Medium\n"
        f"> **Affects:** src/bg{num:04d}.py\n> **Points:** {points}\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n- **Given** the recorded state\n- **Verify:** shell true\n\n", encoding="utf-8")
    idx = d / "_index.md"
    idx.write_text(idx.read_text(encoding="utf-8")
                   + f"| [BG{num:04d}](BG{num:04d}-x.md) | b{num} | {status} |\n",
                   encoding="utf-8")


def _work(root: Path, num: int, status: str = "Fixed") -> None:
    """Work the unit: the status the batch was planned on becomes the terminal one."""
    p = _bug_path(root, num)
    p.write_text(p.read_text(encoding="utf-8")
                 .replace("> **Status:** Open", f"> **Status:** {status}"), encoding="utf-8")
    idx = root / "sdlc-studio" / "bugs" / "_index.md"
    idx.write_text(idx.read_text(encoding="utf-8")
                   .replace(f"| b{num} | Open |", f"| b{num} | {status} |"), encoding="utf-8")


def _retro(root: Path, rid: str = "RETRO0001") -> str:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{rid}-x.md").write_text(
        f"# {rid}: r\n\n> **Status:** Complete\n\n## Lessons\n\n"
        "- A lesson worth keeping. It carries a second sentence so it cuts cleanly.\n",
        encoding="utf-8")
    idx = d / "_index.md"
    idx.write_text(idx.read_text(encoding="utf-8") + f"| [{rid}]({rid}-x.md) | r | Complete |\n",
                   encoding="utf-8")
    return rid


def _capture(argv: list[str]) -> tuple[int, str]:
    """Drive the alias's own entry point, with the console captured - a test that leaked the
    ceremony's output would be counted by the noise ratchet."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            rc = autosprint.main(argv)
        except SystemExit as exc:  # argparse refusals
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, buf.getvalue()


def _plan(root: Path, *extra: str) -> tuple[int, str]:
    return _capture(["plan", "--bugs", "Open", "--write", "--no-fetch", "--root", str(root),
                     "--sprint-goal", "ship the fixture batch", *extra])


def _close(root: Path, retro_id: str, *extra: str) -> tuple[int, str]:
    return _capture(["close", "--root", str(root), "--retro", retro_id,
                     "--goal-verdict", "achieved", "--note", "the batch shipped", *extra])


@contextlib.contextmanager
def _stubbed(failing: str | None = None):
    """Stub the delegating chain steps green, optionally failing one by name.

    Patched onto `sys.modules["sprint"]` because that is where `cmd_close` looks each step up
    at call time; patching the instance this module happens to hold would be silently ignored
    whenever another suite registered its own.
    """
    tgt = sys.modules[autosprint.cmd_close.__module__]
    saved = {n: getattr(tgt, f"_close_{n}") for n in _DELEGATING}
    # US0834's report holds go green alongside the chain steps, for the same reason: these
    # tests are about the PRIMARY PATH - the run opens over the approved batch and the worked
    # batch closes it - and their fixture was never built to be report-clean. A live hold would
    # make every one of them fail for a reason outside its own subject.
    # Patched into `cmd_close`'s OWN globals, not onto whatever `sys.modules["sprint"]` holds.
    # A sibling suite that loads sprint.py through `spec_from_file_location` REPLACES that
    # entry, so the module `tgt` resolves to is then a different object from the one this
    # function body reads its names out of - and the stub lands where nothing looks for it.
    # Module-alone this is invisible; it only appears once another module has run first.
    g = autosprint.cmd_close.__globals__
    saved_holds = g["_report_holds"]
    g["_report_holds"] = lambda *a, **k: []

    def make(n):
        def step(root, retro_id, state):
            if n == failing:
                return False, f"{n.replace('_', '-')} failed", "fix the fixture failure"
            return True, f"{n} ok", ""
        return step

    for n in _DELEGATING:
        setattr(tgt, f"_close_{n}", make(n))
    try:
        yield
    finally:
        g["_report_holds"] = saved_holds
        for n, fn in saved.items():
            setattr(tgt, f"_close_{n}", fn)


# --- the mutant ---------------------------------------------------------------------
#
# The call site of the close chain's failure handling, not the body of a step: a mutant applied
# inside a step would only prove the step's own tests bind. Reading every step as green makes the
# loop report a failed step as passed and record no known issue - exactly the failure mode the
# loop test exists to refuse.
_MUTATION_TARGET = "sprint.py"
_ORIGINAL = ("        ok, detail, remedy = step(root, args.retro, state)\n"
             "        if ok:\n")
_MUTANT = ("        ok, detail, remedy = step(root, args.retro, state)\n"
           "        if ok or True:  # MUTANT: a failed step is swallowed\n")
#: The single test node re-run against the mutant. Naming ONE node keeps the mutation test
#: from re-entering itself.
_MUTATION_PROBE = ("test_autosprint.PrimaryPathTests."
                   "test_a_failing_step_is_named_and_the_loop_runs_on")


def _copy_tree(dest: Path) -> Path:
    """A bytecode-free copy of the scripts tree. Stale `.pyc` files are the reason a
    same-length mutant can report SURVIVED without its code ever running."""
    out = dest / "scripts"
    shutil.copytree(SCRIPTS, out, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".local"))
    # the close now runs through to the report, which renders from the skill's templates
    shutil.copytree(SCRIPTS.parent / "templates", dest / "templates")
    return out


def _run_probe(tree: Path) -> subprocess.CompletedProcess:
    """Run the probe against a copied tree. `gitutil.git_env` confines the child - the
    plan it drives calls git, and an inherited repo-locating variable would point it at the
    real checkout - and `-B` plus the bytecode-free copy keep a cached `.pyc` from running
    the ORIGINAL code under a same-length mutant."""
    return subprocess.run([sys.executable, "-B", "-m", "unittest", _MUTATION_PROBE],
                          cwd=tree / "tests", env=gitutil.git_env(PYTHONDONTWRITEBYTECODE="1"),
                          capture_output=True, text=True, timeout=300, check=False)


# --- tests ---------------------------------------------------------------------

class AliasTests(unittest.TestCase):
    """The shim's own contract: same objects, and it says what replaced it."""

    def test_the_alias_re_exports_sprints_own_entry_points(self) -> None:
        for name in ("main", "select_batch", "build_plan", "build_parser", "cmd_close"):
            fn = getattr(autosprint, name)
            self.assertIs(fn, getattr(sprint_at_load, name),
                          f"{name} is a copy, not a re-export - the alias would drift")
            self.assertEqual(fn.__module__, "sprint",
                             f"{name} is defined on the alias, not re-exported from sprint")

    def test_running_the_alias_names_its_replacement(self) -> None:
        proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / "autosprint.py"), "--help"],
                              capture_output=True, text=True, timeout=120, check=False,
                              env=gitutil.git_env(PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("deprecated alias", proc.stderr)
        self.assertIn("use `sprint`", proc.stderr)
        self.assertIn("close", proc.stdout)  # the re-exported parser, not a stub


class PrimaryPathTests(unittest.TestCase):
    """US0351: the lifecycle an operator still reaches through the alias."""

    def test_the_primary_path_drives_a_batch_to_close(self) -> None:
        """AC1: plan opens the run over the approved batch, the worked batch closes it.

        Under US0832's split the close is PREPARE: it runs every step that can change a fact,
        files the report and leaves the run OPEN, because under D0213 ending a run belongs to
        the SEAL. So the primary path is driven to its end here rather than stopped half way -
        `close` then `sign` - and both halves of the contract are asserted, which is what this
        test was for before the verb it names stopped being the whole of it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            rid = _retro(root)

            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            opened = run_state.read(root)
            self.assertTrue(run_state.is_open(root), "plan --write did not open the run")
            self.assertEqual(opened["batch"], ["BG0001", "BG0002"])
            self.assertEqual(opened["outcome"], "running")
            self.assertEqual(opened.get("sprint_goal"), "ship the fixture batch")

            _work(root, 1); _work(root, 2)
            with _stubbed():
                rc, out = _close(root, rid)
            self.assertEqual(rc, 0, out)

            prepared = run_state.read(root)
            self.assertEqual(prepared["run_id"], opened["run_id"], "a second run was opened")
            self.assertEqual(prepared["outcome"], "running",
                             "PREPARE ended the run - under D0213 that belongs to the SEAL, "
                             "and a run ended here can no longer be signed over its report")
            self.assertTrue(run_state.is_open(root), "PREPARE closed the run it is preparing")
            self.assertTrue(prepared.get("report"), "PREPARE filed no report to be signed over")
            self.assertTrue(prepared.get("handoff"), "no handoff recorded against the run")
            self.assertEqual(prepared["sprint_goal_verdict"]["verdict"], "achieved")

            # ...and the SEAL refuses this fixture, which is the gate working rather than a
            # gap: one command, one principal, and a run whose units carry no independent
            # critic record cannot be signed at all. The successful seal is pinned where it
            # belongs, on `test_sprint.py::PrepareAndSealTests` and `SealTests`, over a fixture
            # built to be signable; asserting it here would mean teaching this one to record a
            # reviewer, and a lifecycle test that has to fake independence tests nothing.
            rc, out_sign = _capture(["sign", "--root", str(root),
                                     "--report", str(prepared["report"]),
                                     "--principal", "A Reviewer Of Record"])
            self.assertNotEqual(rc, 0, "an unsignable run was sealed")
            self.assertIn("critic", out_sign.lower(),
                          f"the refusal does not name what is missing: {out_sign}")
            self.assertEqual(run_state.read(root)["outcome"], "running",
                             "a refused seal moved the run's outcome anyway")
            closed = prepared
            # every step ran, in the ceremony's order, and the batch it sealed is the one
            # the plan approved
            # DERIVED: the ceremony's own order, so a step added to the chain is asserted
            # rather than silently dropped from this check.
            chain = sprint_at_load._CLOSE_CHAIN
            for i, name in enumerate(chain, start=1):
                self.assertIn(f"close [{i}/{len(chain)}] {name}: ok", out)
            self.assertEqual(closed["batch"], ["BG0001", "BG0002"])

    def test_a_failing_step_is_named_and_the_loop_runs_on(self) -> None:
        """AC2, as US0876 re-states it: the second step fails - the close names it as a known
        issue and runs every later step. A chain that swallowed the failure would report it
        green and record nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _ws(root); _bug(root, 1); _bug(root, 2)
            rid = _retro(root)
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            _work(root, 1); _work(root, 2)

            with _stubbed(failing="retro_extract"):
                rc, out = _close(root, rid)

            self.assertEqual(rc, 0, out)
            chain = sprint_at_load._CLOSE_CHAIN
            self.assertIn(f"close [{chain.index('retro-extract') + 1}/{len(chain)}] "
                          f"retro-extract: 1 known issue(s)", out)
            self.assertIn("fix the fixture failure", out)
            # the steps after the failure all run
            for name in ("lessons-summary", "gate", "handoff", "reconcile", "review-anchor"):
                self.assertIn(f"close [{chain.index(name) + 1}/{len(chain)}] {name}", out)
            state = run_state.read(root)
            self.assertIn({"source": "retro-extract", "detail": "retro-extract failed"},
                          state["close_known_issues"])
            self.assertTrue(state.get("handoff"))

    def test_the_suite_kills_a_loop_control_mutant(self) -> None:
        """AC3: the loop test is bound to the loop, not merely running over it.

        Control first, then the mutant: a probe that cannot go green on an untouched copy
        would "kill" every mutant for reasons that have nothing to do with the code.
        """
        with tempfile.TemporaryDirectory() as d:
            control = _copy_tree(Path(d) / "control")
            clean = _run_probe(control)
            self.assertEqual(clean.returncode, 0,
                             f"the probe is not green on an untouched copy:\n{clean.stderr}")

            mutant = _copy_tree(Path(d) / "mutant")
            target = mutant / _MUTATION_TARGET
            src = target.read_text(encoding="utf-8")
            self.assertEqual(src.count(_ORIGINAL), 1, "the mutation anchor is not unique")
            target.write_text(src.replace(_ORIGINAL, _MUTANT), encoding="utf-8")
            # the patch landed, and it landed on running code
            self.assertNotEqual(target.read_text(encoding="utf-8"), src, "the mutant is a no-op")
            self.assertIn("MUTANT", target.read_text(encoding="utf-8"))
            compile(target.read_text(encoding="utf-8"), str(target), "exec")

            killed = _run_probe(mutant)
            self.assertNotEqual(killed.returncode, 0,
                                f"the mutant SURVIVED - the loop test does not bind the loop "
                                f"control:\n{killed.stdout}\n{killed.stderr}")
            self.assertIn("FAILED", killed.stderr)


if __name__ == "__main__":
    unittest.main()
