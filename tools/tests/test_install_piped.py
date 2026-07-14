"""Regression test for BG0122: install.sh must run `main` when piped to bash.

The bottom of install.sh guards `main` so the functions stay unit-testable when
sourced (see test_install_sweep.py). The guard was:

    if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then main; fi

Piped (`curl ... | bash`) bash reads the script from stdin, so there is no source
file: BASH_SOURCE[0] is unset/empty while $0 is "bash". The test failed, `main`
never ran, and the installer defined its functions, fell off the bottom, and
exited 0 - no output, no error, no install. That is the exact invocation the
README advertises. The fix is the `:-$0` fallback.

The existing suite could not catch this: it *sources* install.sh, which is the
one invocation mode that was never broken.

Two things this test must get right, both learned from the bug:

1. Assert on STDOUT, not the exit code. The broken script exited 0. An
   exit-code assertion passes against the bug and proves nothing.
2. Probe with a flag consumed INSIDE `main`. Argument parsing runs at top level
   (the `while` loop near the top of the script), so a bogus flag errors and
   exits 2 even when the guard is broken. `--list-targets` is handled inside
   `main`, needs no network and writes nothing, so it cleanly separates
   "reached main" from "fell off the bottom".
"""
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"

# Printed by main() via print_list; unreachable if the guard skips main.
MAIN_ONLY_MARKER = "SDLC Studio - targets"


def _run(script: str, *args: str) -> subprocess.CompletedProcess:
    """Pipe `script` to bash on stdin, mimicking `curl ... | bash -s -- ARGS`."""
    return subprocess.run(
        ["bash", "-s", "--", *args],
        input=script,
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )


class InstallPipedInvocation(unittest.TestCase):
    def setUp(self) -> None:
        self.script = INSTALL_SH.read_text()

    def test_piped_script_runs_main(self) -> None:
        """curl | bash must reach main - the README's advertised install."""
        proc = _run(self.script, "--list-targets")
        self.assertIn(
            MAIN_ONLY_MARKER,
            proc.stdout,
            "install.sh piped to bash produced no main() output - the "
            "source-vs-execute guard skipped main (BG0122). stdout was: "
            f"{proc.stdout!r}",
        )

    def test_piped_script_is_not_a_silent_noop(self) -> None:
        """The bug's signature: exit 0 with nothing done. Guard the signature."""
        proc = _run(self.script, "--list-targets")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(
            proc.stdout.strip(),
            "install.sh piped to bash exited 0 having printed nothing - a "
            "silent no-op, which is what made BG0122 so hard to spot.",
        )

    def test_probe_actually_detects_the_old_broken_guard(self) -> None:
        """Meta-test: prove the probe above fails against the pre-fix guard.

        Without this, a probe that is silently insensitive to the bug (as an
        exit-code assertion would be) could pass forever and give false comfort.
        """
        broken = self.script.replace('"${BASH_SOURCE[0]:-$0}"', '"${BASH_SOURCE[0]}"')
        self.assertNotEqual(
            broken, self.script, "could not synthesise the pre-fix guard - has it moved?"
        )
        proc = _run(broken, "--list-targets")
        self.assertNotIn(
            MAIN_ONLY_MARKER,
            proc.stdout,
            "the pre-fix guard produced main() output when piped, so this test "
            "is not actually exercising the regression it claims to.",
        )


if __name__ == "__main__":
    unittest.main()
