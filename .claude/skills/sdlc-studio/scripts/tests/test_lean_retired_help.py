"""US0949: no shipped command's help offers a retired behaviour.

`sprint close --apply-signoff` signs nothing and exits 2, yet `close --help` described it as the
sign-off fan-out and `sprint call` forwarded it to the close. `artifact new --target` wrote a
`Verification target` line on every supplied AC that no gate reads. Each is driven through the
shipped entry point in a throwaway tree.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")


def _cli(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=120)


def _main(argv: list[str]) -> tuple[int, str]:
    """`sprint.main` in-process; an argparse refusal is an exit code, not an exception."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = sprint.main(argv)
        except SystemExit as exc:
            rc = exc.code
    return rc, out.getvalue()


def _run_with_two_bugs(root: Path) -> Path:
    """An open run whose batch holds one delivered bug and one never started."""
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    for bid, status in (("BG0001", "Fixed"), ("BG0002", "Open")):
        (bugs / f"{bid}-x.md").write_text(
            f"# {bid}: b\n\n> **Status:** {status}\n> **Severity:** Medium\n> **Points:** 2\n\n"
            "## Acceptance Criteria\n\n### AC1: it behaves\n\n- **Verify:** shell true\n",
            encoding="utf-8")
    state = root / "sdlc-studio" / ".local" / "run-state.json"
    state.parent.mkdir(parents=True)
    state.write_text(json.dumps({"schema": 1, "run_id": "RUN-US0949", "outcome": "running",
                                 "batch": ["BG0001", "BG0002"], "sprint_goal": "a goal",
                                 "started_at": "2026-09-25T09:00:00Z"}), encoding="utf-8")
    return state


class RetiredHelpTests(unittest.TestCase):
    def test_close_and_call_do_not_offer_apply_signoff(self) -> None:
        """AC1. MUTANTS: HEAD, whose close help describes the fan-out and whose `call` appends
        the flag to the close argv; and a fix that rewords only the close help, so `call` still
        forwards it."""
        for verb in ("close", "call"):
            res = _cli("sprint.py", verb, "--help")
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertNotIn("apply-signoff", res.stdout,
                             f"`sprint.py {verb} --help` still offers the retired sign-off "
                             f"fan-out:\n{res.stdout}")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = _run_with_two_bugs(root)
            before = state.read_text(encoding="utf-8")
            reached = []
            with unittest.mock.patch.object(sprint, "cmd_close",
                                            lambda a: reached.append(a) or 0):
                rc, printed = _main(["call", "--reason", "out of appetite", "--apply-signoff",
                                     "--root", str(root)])
            self.assertFalse([a for a in reached if getattr(a, "apply_signoff", False)],
                             "`call` still forwards --apply-signoff to the close")
            self.assertEqual(rc, 2, printed)
            self.assertEqual(state.read_text(encoding="utf-8"), before,
                             "a call carrying the retired flag still descoped the batch")
            # The close itself still refuses the flag by name and points at the one signature.
            rc, printed = _main(["close", "--apply-signoff", "--principal", "Darren",
                                 "--root", str(root)])
            self.assertEqual(rc, 2, printed)
            self.assertIn("sprint.py sign", printed)

    def test_verification_target_tier_is_retired(self) -> None:
        """AC2. MUTANTS: HEAD, where `--target soak` writes the line on every supplied AC; and
        a fix that removes only the template line while the flag still writes it."""
        help_text = _cli("artifact.py", "new", "--help")
        self.assertEqual(help_text.returncode, 0, help_text.stderr)
        self.assertNotIn("--target", help_text.stdout)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            epic = _cli("artifact.py", "new", "--type", "epic", "--title", "the group",
                        "--summary", "the group", "--format", "json", "--root", str(root))
            self.assertEqual(epic.returncode, 0, epic.stderr)
            epic_id = json.loads(epic.stdout)["id"]
            stories = root / "sdlc-studio" / "stories"
            for template in ("minimal", "planning"):
                story = ["--type", "story", "--title", f"a {template} story", "--epic", epic_id,
                         "--ac", "the CLI exits 0", "--verify", "shell true",
                         "--template", template, "--root", str(root)]
                before = sorted(p.name for p in stories.glob("*")) if stories.is_dir() else []
                for value in ("soak", ""):      # an empty value is the flag, still retired
                    refused = _cli("artifact.py", "new", *story, "--target", value)
                    self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
                    self.assertIn("verification-target tier is retired", refused.stderr)
                after = sorted(p.name for p in stories.glob("*")) if stories.is_dir() else []
                self.assertEqual(after, before, "a refused --target still wrote a story")
                made = _cli("artifact.py", "new", *story, "--format", "json")
                self.assertEqual(made.returncode, 0, made.stderr)
                body = Path(json.loads(made.stdout)["path"]).read_text(encoding="utf-8")
                self.assertIn("- **Verify:** shell true", body)
                self.assertNotIn("Verification target", body, template)


if __name__ == "__main__":
    unittest.main()
