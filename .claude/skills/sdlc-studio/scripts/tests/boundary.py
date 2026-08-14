"""Which tests run on every commit, and which only at a boundary.

BG0579. The per-commit gate reached 590s against a 380s budget and crossed the ceiling of the
tool timeouts that run it, so a commit was KILLED mid-run rather than refused - and a kill is
indistinguishable from a hang, whose documented escape is `--no-verify`. The failure mode trains
the bypass on the guard this repository leans on hardest.

Profiled rather than guessed. Four tests were 452s of a 934s full run, and the single largest was
`ReleaseRehearsalLaneTests`, at 228s - 24% of the suite - whose own docstring reads "the rehearsal
binds at the push and release boundaries and nowhere else". **The lane was boundary-only and its
test was not.** That is the shape this repository keeps finding: a rule stated in one place and
not applied to the thing that exercises it.

So this is not a speed-up. It is the same boundary rule, applied to the tests that measure it.

WHAT THIS IS NOT. Not a skip, and not an exclusion. A marked test runs in FULL at every boundary -
`tools/run-suite.sh` sets the marker, so every push, release, close and CI run executes it - and
is deferred only in the per-commit selected run. Nothing here reduces what is ever executed; it
moves when. A guard that quietly stopped running would be the very defect this repository files
bugs about, so `test_boundary_marker.py` asserts that the marked set is non-empty, that the
runner sets the marker, and that CI does - a marker nobody honours disables tests silently, which
is worse than the cost it was meant to save.

Mark a test only when BOTH hold:

* it costs seconds, not milliseconds - the whole point is wall-clock; and
* what it measures cannot regress between a commit and the next boundary WITHOUT some cheaper
  test also going red. A defect that only this test can see is a defect that must be caught on
  the commit that introduces it, whatever it costs.
"""
from __future__ import annotations

import os
import unittest

#: Set by `tools/run-suite.sh` and by CI. Absent in the per-commit gate's selected run.
BOUNDARY_ENV = "SDLC_STUDIO_BOUNDARY_SUITE"


def at_boundary() -> bool:
    """Whether this process is the boundary run that executes the marked tests."""
    return os.environ.get(BOUNDARY_ENV, "") == "1"


def boundary_only(reason: str):
    """Defer a test to the boundary suite, naming WHY it is affordable to defer.

    The reason is compulsory and is printed in the skip line, so a reader of a per-commit run
    sees which coverage moved and can judge the trade rather than discover it later.
    """
    if not reason or len(reason.strip()) < 20:
        raise ValueError(
            "boundary_only needs a reason saying why deferring this test to the boundary loses "
            "nothing on a commit - an unexplained deferral is an exclusion with better manners")
    return unittest.skipUnless(
        at_boundary(),
        f"boundary-only: {reason} (runs at push, release, close and in CI; "
        f"set {BOUNDARY_ENV}=1 to run it here)")
