"""BG0579: the boundary marker must defer tests, never quietly delete them.

`boundary_only` moves a slow test out of the per-commit gate and into the boundary suite. That is
only honest while something actually RUNS the boundary suite, and while the marked set stays a
handful of measured, named exceptions. A marker nobody honours is an exclusion with better
manners - and this repository has twice found a lane that shipped believing it was enforced and
was not, which is the failure these assertions exist to make impossible for this one.

Every suppression is also a blindfold, so the blindfold is what gets checked here.
"""
from __future__ import annotations

import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
TESTS = REPO / ".claude/skills/sdlc-studio/scripts/tests"
MARKER = "SDLC_STUDIO_BOUNDARY_SUITE"


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
        """`tools/run-suite.sh` IS the boundary runner - push, release, close and the manual
        full run all go through it. If it does not set the marker, every marked test runs
        nowhere at all and the gate is green on tests that never execute."""
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


if __name__ == "__main__":
    unittest.main()
