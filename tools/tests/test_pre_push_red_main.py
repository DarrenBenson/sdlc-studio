"""The pre-push hook names a push-triggered Lint run on main that is still in progress.

The red-main read asks the forge for the latest COMPLETED run, so a run still in progress over
main's newest commit was skipped in silence, and a red there was first read pushes later. The
hook now reads the newest push-triggered run whatever its status and, when it has not completed,
names it and the commit it judges. Each fixture is a throwaway clone from `test_pre_push_hook`
with a `gh` stub that answers the completed read and the newest-run read separately.

Run from the repo root:
    python3 -m pytest -q tools/tests/test_pre_push_red_main.py
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pre_push_hook as _pp  # noqa: E402

GREEN_ID, RED_ID, NEWEST_ID = "35100000001", "35100000002", "35100000003"
HEAD_SHA = "0123456789abcdef0123456789abcdef01234567"

#: `gh` for the two push-triggered reads: a call carrying `--status completed` answers
#: STUB_COMPLETED (green or red), any other push read answers STUB_NEWEST, and the scheduled read
#: answers green. STUB_NEWEST names the newest run's shape, or `fail` / `garbage` for a read that
#: cannot be used.
STUB_GH = textwrap.dedent(f'''
    #!/usr/bin/env python3
    import json, os, sys
    from pathlib import Path
    Path(os.environ["STUB_GH_ARGV"]).open("a").write(" ".join(sys.argv[1:]) + "\\n")
    args = sys.argv[1:]
    green = {{"databaseId": {GREEN_ID}, "conclusion": "success", "status": "completed",
              "headSha": "1" * 40, "url": "https://example.test/runs/{GREEN_ID}"}}
    red = {{"databaseId": {RED_ID}, "conclusion": "failure", "status": "completed",
            "headSha": "2" * 40, "url": "https://example.test/runs/{RED_ID}"}}
    if "schedule" in args:
        print(json.dumps([dict(green, databaseId=34100000003)])); raise SystemExit(0)
    if "--status" in args:
        print(json.dumps([{{"green": green, "red": red}}[os.environ["STUB_COMPLETED"]]]))
        raise SystemExit(0)
    newest = os.environ["STUB_NEWEST"]
    if newest == "fail":
        sys.stderr.write("gh: connection reset\\n"); raise SystemExit(1)
    if newest == "garbage":
        print("<html>rate limited</html>"); raise SystemExit(0)
    run = {{"databaseId": {NEWEST_ID}, "conclusion": "", "status": "in_progress",
            "headSha": "{HEAD_SHA}", "url": "https://example.test/runs/{NEWEST_ID}"}}
    shapes = {{"in_progress": [run], "queued": [dict(run, status="queued")],
               "no_sha": [dict(run, headSha="")],
               "no_id": [{{k: v for k, v in run.items() if k != "databaseId"}}],
               "no_status": [{{k: v for k, v in run.items() if k != "status"}}],
               "dict": {{"runs": [run]}},
               "empty": [], "same_green": [green], "same_red": [red]}}
    print(json.dumps(shapes[newest]))
''').lstrip()

NOTICE = (f"pre-push: push-triggered Lint run {NEWEST_ID} on main is in progress over commit "
          f"{HEAD_SHA}; its result is not yet read, so this push is not judged against it\n")


class PrePushRedMainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fx = _pp._Clone()
        self.addCleanup(self.fx.cleanup)
        path = self.fx.stub_path()
        (path / "gh").write_text(STUB_GH, encoding="utf-8")
        (path / "gh").chmod(0o755)

    def _push(self, completed: str, newest: str, ack: str | None = None):
        self.fx.commit_more()
        env = {"STUB_COMPLETED": completed, "STUB_NEWEST": newest}
        return _pp._git(self.fx.clone, "push", "-q", "origin", "main", check=False,
                        env={**self._base_env(), **env, **({"SDLC_PUSH_ACK_RED": ack} if ack else {})})

    def _base_env(self) -> dict:
        return {"STUB_ARGV": str(self.fx.argv), "STUB_RC": "0", "PATH": str(self.fx.stub_path()),
                "STUB_GH_ARGV": str(self.fx.tmp / "gh-argv.txt")}

    def _newest_reads(self) -> list[str]:
        return [c for c in self.fx.gh_calls() if "--event push" in c and "--status" not in c]

    def test_an_in_progress_run_is_named_with_the_commit_it_judges(self) -> None:
        """AC1: the newest run is in progress and the latest concluded run is green."""
        r = self._push("green", "in_progress")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn(NOTICE, r.stderr)
        self.assertEqual(1, r.stderr.count("not yet read"), r.stderr)
        self.assertEqual(["run list --workflow Lint --branch main --event push --limit 1 "
                          "--json databaseId,status,headSha"], self._newest_reads())
        calls = self.fx.gh_calls()
        self.assertEqual(3, len(calls), calls)
        self.assertIn("--event push --status completed", calls[0], calls)
        self.assertEqual(self._newest_reads()[0], calls[1], "the newest run is not read second")
        self.assertIn("--event schedule", calls[2], calls)
        self.assertEqual(2, self.fx.remote_count(), "the push did not land")

    def test_a_red_concluded_run_behind_an_in_progress_one_refuses(self) -> None:
        """AC2, the control: a red concluded run is judged even with a newer run in progress."""
        r = self._push("red", "in_progress")
        self.assertNotEqual(0, r.returncode, r.stderr)
        self.assertIn(f"has not been read: run {RED_ID} (https://example.test/runs/{RED_ID})",
                      r.stderr)
        self.assertIn(f"SDLC_PUSH_ACK_RED={RED_ID} git push", r.stderr)
        self.assertEqual(0, self.fx.remote_count(), "a red main was pushed over")

    def test_a_green_main_with_nothing_in_progress_says_nothing(self) -> None:
        """AC3: the newest run is the concluded green one: the read is made and says nothing."""
        r = self._push("green", "same_green")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertEqual(1, len(self._newest_reads()), self.fx.gh_calls())
        self.assertNotIn("not yet read", r.stderr)
        self.assertNotIn(NEWEST_ID, r.stderr)

    def test_an_acknowledged_red_still_names_the_run_in_progress(self) -> None:
        r = self._push("red", "in_progress", ack=RED_ID)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn(f"red Lint run {RED_ID} acknowledged", r.stderr)
        self.assertIn(NOTICE, r.stderr)

    def test_a_queued_run_is_named_as_queued(self) -> None:
        r = self._push("green", "queued")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn(f"Lint run {NEWEST_ID} on main is queued over commit {HEAD_SHA}; its result "
                      "is not yet read", r.stderr)

    def test_a_run_whose_commit_is_not_named_says_so(self) -> None:
        r = self._push("green", "no_sha")
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn(f"Lint run {NEWEST_ID} on main is in progress over commit (not named by the "
                      "forge); its result is not yet read", r.stderr)

    def test_an_unusable_newest_read_adds_nothing_and_blocks_nothing(self) -> None:
        for newest in ("fail", "garbage", "empty", "dict", "no_id", "no_status", "same_red"):
            with self.subTest(newest=newest):
                log = self.fx.tmp / "gh-argv.txt"
                log.unlink(missing_ok=True)
                before = self.fx.remote_count()
                r = self._push("green", newest)
                self.assertEqual(0, r.returncode, r.stderr)
                self.assertEqual(1, len(self._newest_reads()), self.fx.gh_calls())
                self.assertNotIn("not yet read", r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                self.assertGreater(self.fx.remote_count(), before, r.stderr)


if __name__ == "__main__":
    unittest.main()
