"""Capture the console diagnostics a tool writes during a test that is not about them.

`tools/skill-tests.sh` fails a GREEN run that printed anything, because a passing suite
whose output contains `warning:` trains every reader to skim past the word - and skimming
past `warning:` is the reflex that lets a real one through.

Two shipped warnings fire from deep inside library calls that most fixtures make in
passing. `file_finding.file_finding()` warns for every finding whose criteria carry no
verifier (BG0636), and `critic.repair_state()` warns for each legacy closure chunk with no
`->` separator (BG0631). Both are correct and both must keep reaching a real operator; they
are noise only in a fixture that is about indexing, escaping or attribution instead.

    import quiet

    with quiet.diagnostics() as err:
        res = ff.file_finding(root, "cr", "t", fields)
    self.assertIn("carry no verifier", err.getvalue())   # when the warning IS the point

The buffer is YIELDED rather than dropped, so a test that wants to assert on the diagnostic
can, and one that does not is at least explicit that it is swallowing something. Only stderr
is captured: stdout carries a command's actual output, and a test that redirects it is
usually reading it.
"""
from __future__ import annotations

import contextlib
import io
from collections.abc import Iterator


@contextlib.contextmanager
def diagnostics() -> Iterator[io.StringIO]:
    """Redirect stderr into a buffer for the duration of the block, and yield the buffer."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        yield err
