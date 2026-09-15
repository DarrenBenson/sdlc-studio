"""BG0579: the boundary marker must defer tests, never quietly delete them.

`boundary_only` moves a slow test out of the per-commit gate and into the boundary suite. That is
only honest while something actually RUNS the boundary suite, and while the marked set stays a
handful of measured, named exceptions. A marker nobody honours is an exclusion with better
manners - and this repository has twice found a lane that shipped believing it was enforced and
was not, which is the failure these assertions exist to make impossible for this one.

Every suppression is also a blindfold, so the blindfold is what gets checked here.
"""
# test-census-subject: tools/run-suite.sh
from __future__ import annotations

import ast
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import tempfile
import textwrap
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
TESTS = REPO / ".claude/skills/sdlc-studio/scripts/tests"
MARKER = "SDLC_STUDIO_BOUNDARY_SUITE"
BOUNDARY_PY = TESTS / "boundary.py"
PRE_PUSH = REPO / ".githooks" / "pre-push"
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
#: The commands a commit runs. None may name the marker, or the per-commit path stops deferring.
PER_COMMIT_INVOKERS = (REPO / ".githooks" / "pre-commit", REPO / ".githooks" / "commit-msg",
                       REPO / "tools" / "skill-tests.sh")


def _marked() -> list[tuple[str, str]]:
    """(module, reason) for every `boundary_only(...)` in the shipped test tree."""
    out = []
    for path in sorted(TESTS.glob("test_*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"@boundary_only\(\s*(.*?)\)\s*\n", text, re.S):
            out.append((path.name, m.group(1)))
    return out


class TheMarkerIsHonoured(unittest.TestCase):
    def test_the_boundary_runner_sets_the_marker(self) -> None:
        """`tools/run-suite.sh` is the manual full run. No hook, close or CI step invokes it -
        the push boundary sets the marker on its own gate invocations, which MarkerPromiseTests
        reads - but a full run that skipped the marked tests would be a full run in name only."""
        # An UNCOMMENTED line. `assertIn` on the raw text passed against
        # `# export SDLC_STUDIO_BOUNDARY_SUITE=1`, so commenting the export out - the one edit
        # that would silently disable every deferred test - left this green. Found by executing
        # the mutant, which is the only reason it is not still true. Third time in this run that
        # a check matched prose instead of a command.
        lines = (REPO / "tools/run-suite.sh").read_text(encoding="utf-8").splitlines()
        live = [ln for ln in lines
                if not ln.lstrip().startswith("#") and f"export {MARKER}=1" in ln]
        self.assertTrue(live,
                        "the boundary runner does not set the marker on any live line, so every "
                        "deferred test runs nowhere")

    def test_ci_sets_the_marker_on_both_suites(self) -> None:
        """CI is the independent boundary - the one run no developer machine can flatter.
        Both discovery commands must carry the marker, or the half without it silently drops
        whatever is marked in its tree."""
        lines = (REPO / ".github/workflows/lint.yml").read_text(encoding="utf-8").splitlines()
        # COMMANDS ONLY, and it took two goes to get that right - which is the point of writing
        # it down. The first cut scanned every line naming a runner and tripped on a COMMENT that
        # mentioned `coverage run`; the second tripped on a YAML step NAME that mentioned
        # `skill-tests.sh`. A guard that refuses on prose reports a defect that is not there,
        # and a guard with a history of crying wolf is one whose real refusal gets waved through.
        # A command is a line inside a `run:` block: not a comment, not a `- key:` list item.
        def _is_command(ln: str) -> bool:
            s = ln.strip()
            return bool(s) and not s.startswith("#") and not s.startswith("- ") \
                and not re.match(r"^[a-z-]+:( |$)", s)

        runs = [ln for ln in lines
                if _is_command(ln)
                and ("unittest discover" in ln or "coverage run" in ln
                     or "skill-tests.sh" in ln)]
        self.assertTrue(runs, "no test-running command found in the workflow at all")
        for line_no, line in enumerate(lines):
            if line not in runs:
                continue
            window = "\n".join(lines[max(0, line_no - 2):line_no + 1])
            self.assertIn(MARKER, window,
                          f"a CI command runs the suites without the marker, so whatever is "
                          f"deferred there runs nowhere: {line.strip()}")

    def test_a_deferral_with_no_stated_reason_is_refused(self) -> None:
        """The reason is the whole audit trail: it is what a reader of a per-commit run sees in
        place of the test, and what a reviewer judges the trade against. Enforced where it
        cannot be worked around - in the decorator itself, at import time, so a thin reason is a
        broken module rather than a lint anybody can ignore.

        The source scan below is the belt to that brace. It was the ONLY check here, and its
        mutant survived: measuring the captured argument's length says nothing, because a
        concatenated string keeps its length however the first line is worded."""
        import sys as _sys
        _sys.path.insert(0, str(TESTS))
        import boundary
        for thin in ("", "typo", "too short to audit"):
            with self.subTest(reason=thin):
                with self.assertRaises(ValueError):
                    boundary.boundary_only(thin)
        self.assertTrue(boundary.boundary_only("a reason long enough to tell a reader what "
                                               "coverage moved and why"))
        for module, arg in _marked():
            with self.subTest(module=module):
                self.assertGreater(len(arg.strip()), 40,
                                   f"{module}: a boundary deferral with no stated reason")

    def test_the_marked_set_stays_small_and_named(self) -> None:
        """A ratchet, in the direction that matters. The marker exists for a measured handful of
        expensive integration tests; a growing set means the per-commit gate is quietly becoming
        a subset nobody chose. Raise this only with the profile that justifies it."""
        marked = _marked()
        self.assertTrue(marked, "nothing is marked - if the marker is unused, delete it rather "
                                "than leaving a mechanism that looks like coverage")
        self.assertLessEqual(len(marked), 6,
                             f"{len(marked)} boundary-only tests: the per-commit gate is drifting "
                             f"into a subset nobody chose - profile first, then argue for it")


def _commands(text: str) -> list[str]:
    """Live commands: comment lines dropped, backslash continuations joined into one line."""
    out: list[str] = []
    buf = ""
    for raw in text.splitlines():
        s = raw.strip()
        if not buf and (not s or s.startswith("#")):
            continue
        if s.endswith("\\"):
            buf += s[:-1] + " "
            continue
        out.append(buf + s)
        buf = ""
    if buf:
        out.append(buf)
    return out


def _sets_marker(command: str, before: str, marker: str) -> bool:
    """Whether `command` assigns `<marker>=1` to the process it runs, ahead of the token
    matching `before` - an env assignment, never a `-u` removal or a later argument."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    head = next((i for i, t in enumerate(tokens) if re.search(before, t)), None)
    if head is None:
        return False
    return any(t == f"{marker}=1" and (i == 0 or tokens[i - 1] != "-u")
               for i, t in enumerate(tokens[:head]))


def _backed_runs(marker: str) -> set[str]:
    """The runs a live command sets the marker for, read from the hook and the workflow."""
    backed: set[str] = set()
    hook = _commands(PRE_PUSH.read_text(encoding="utf-8"))
    for boundary in ("push", "release"):
        calls = [c for c in hook if re.search(rf"gate\.py\"?\s+--boundary\s+{boundary}\b", c)]
        if calls and all(_sets_marker(c, r"gate\.py$", marker) for c in calls):
            backed.add(boundary)
    # A command is a line of a `run:` block, or the value of a one-line `run:`; a step's `name:`
    # and every other YAML key are prose, however they mention a runner.
    suite = re.compile(r"unittest discover|coverage run|skill-tests\.sh")
    ci = []
    for c in _commands(WORKFLOW.read_text(encoding="utf-8")):
        inline = re.match(r"^(?:- )?run:\s+([^|>\s].*)$", c)
        if inline:
            c = inline.group(1)
        elif c.startswith("- ") or re.match(r"^[a-z-]+:( |$)", c):
            continue
        if suite.search(c):
            ci.append(c)
    if ci and all(_sets_marker(c, r"^(bash|python3?|coverage)$", marker) for c in ci):
        backed.add("ci")
    return backed


def _claimed_runs(listing: str) -> set[str]:
    """`push, release and in CI` -> {"push", "release", "ci"}. An unknown word stays itself,
    so a claim naming a run nothing backs is reported under its own name."""
    items = re.split(r",|\band\b", listing)
    out = set()
    for item in items:
        word = re.sub(r"^(?:in|at|the)\s+", "", item.strip()).strip()
        if word:
            out.add(word.lower())
    return out


def _boundary_claims() -> tuple[str, set[str], set[str]]:
    """(BOUNDARY_ENV's value, the docstring's claimed runs, the skip reason's claimed runs),
    read from boundary.py's source, never imported - an imported module is whatever the
    interpreter cached, and the claim is about the file."""
    tree = ast.parse(BOUNDARY_PY.read_text(encoding="utf-8"))
    env = next(n.value.value for n in tree.body
               if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "BOUNDARY_ENV" for t in n.targets))
    doc = " ".join((ast.get_docstring(tree) or "").split())
    doc_lists = re.findall(r"runs in FULL at (.+?) - ", doc)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "boundary_only")
    strings = " ".join(n.value for n in ast.walk(fn) if isinstance(n, ast.Constant) and isinstance(n.value, str))
    reason_lists = re.findall(r"\(runs at (.+?);", strings)
    doc_runs = set().union(*(_claimed_runs(x) for x in doc_lists)) if doc_lists else set()
    reason_runs = set().union(*(_claimed_runs(x) for x in reason_lists)) if reason_lists else set()
    return env, doc_runs, reason_runs


MARKED_RED = textwrap.dedent('''
    import unittest
    from boundary import boundary_only


    class MarkedTests(unittest.TestCase):
        @boundary_only("a fixture deferral whose only job is to prove the per-commit run skips it")
        def test_marked(self):
            self.fail({sentinel!r})
''').lstrip()

SENTINEL = "MARKED-TEST-EXECUTED-c41d02"


class MarkerPromiseTests(unittest.TestCase):
    """BG0664: what boundary.py promises about where a marked test runs, held to the commands."""

    def test_the_docstring_claim_matches_the_paths_that_set_the_marker(self) -> None:
        """AC2. The claimed runs - the docstring's `runs in FULL at ...` list and the skip
        reason's `(runs at ...)` list - equal the runs a live command sets the marker for.

        MUTANTS: (1) delete `and CI` from the docstring's list - a backed run the claim omits;
        (2) drop the marker from the hook's release invocation - a claimed run nothing backs;
        (3) fix the docstring and leave the skip reason's `close` - a claim nothing backs."""
        env, doc_runs, reason_runs = _boundary_claims()
        self.assertEqual(MARKER, env, "boundary.py reads a different marker than the one checked here")
        backed = _backed_runs(env)
        self.assertEqual({"push", "release", "ci"}, backed,
                         "the hook's two gate invocations and CI's suite commands are the runs that "
                         f"set the marker; read from the commands: {sorted(backed)}")
        self.assertTrue(doc_runs, "no `runs in FULL at ... -` claim found in boundary.py's docstring")
        self.assertTrue(reason_runs, "no `(runs at ...;` claim found in boundary_only's skip reason")
        for where, claimed in (("docstring", doc_runs), ("skip reason", reason_runs)):
            with self.subTest(claim=where):
                self.assertFalse(claimed - backed,
                                 f"boundary.py's {where} names runs no live command sets the marker "
                                 f"for: {sorted(claimed - backed)}")
                self.assertFalse(backed - claimed,
                                 f"boundary.py's {where} omits runs that do execute a marked test: "
                                 f"{sorted(backed - claimed)}")

    def test_a_marked_test_is_still_deferred_in_the_per_commit_run(self) -> None:
        """AC3. The per-commit runner, driven over a fixture holding the tracked boundary.py and
        one red marked test, skips it with the marker unset and executes it with the marker set;
        and no live line of a per-commit invoker names the marker.

        MUTANTS: (1) `at_boundary()` tests `!= "0"` - the unset run executes the red test;
        (2) skill-tests.sh exports the marker - the same; (3) commit-msg prefixes its suite lane
        with the marker - only the scan sees it, because the driven run does not go through it."""
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="boundary_marker_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        skill = tmp / "scripts"
        (skill / "tests").mkdir(parents=True)
        shutil.copy(BOUNDARY_PY, skill / "tests" / "boundary.py")
        (skill / "tests" / "test_marked_fixture.py").write_text(
            MARKED_RED.format(sentinel=SENTINEL), encoding="utf-8")
        # No bytecode: a cached boundary.py from an earlier run would stand in for the file
        base = {k: v for k, v in os.environ.items() if k != MARKER}
        base["PYTHONDONTWRITEBYTECODE"] = "1"

        def run(env: dict) -> subprocess.CompletedProcess:
            return subprocess.run(["bash", "tools/skill-tests.sh", str(skill)], cwd=REPO, env=env,
                                  capture_output=True, text=True, timeout=300)

        unset = run(base)
        out = unset.stdout + unset.stderr
        self.assertEqual(0, unset.returncode, f"the per-commit runner executed the marked test:\n{out}")
        self.assertIn("OK (skipped=1)", out, f"the marked test was not reported skipped:\n{out}")
        self.assertNotIn(SENTINEL, out, f"the marked test executed with the marker unset:\n{out}")
        marked = run({**base, MARKER: "1"})
        out = marked.stdout + marked.stderr
        self.assertNotEqual(0, marked.returncode, f"with the marker set the red marked test did not fail:\n{out}")
        self.assertIn(SENTINEL, out, f"with the marker set the marked test did not execute:\n{out}")
        for path in PER_COMMIT_INVOKERS:
            with self.subTest(invoker=path.name):
                live = [ln for ln in path.read_text(encoding="utf-8").splitlines()
                        if MARKER in ln and not ln.lstrip().startswith("#")]
                self.assertFalse(live, f"{path.relative_to(REPO)} sets the marker on a per-commit path, "
                                       f"so the deferral is gone: {live}")


if __name__ == "__main__":
    unittest.main()
