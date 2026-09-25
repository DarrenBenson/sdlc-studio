"""US0904 AC1: every refusal either hook makes is logged, one JSON line per refusing lane.

The line lands in `sdlc-studio/.local/refusals.jsonl` and carries the lane, a timestamp and the
staged paths, so the close can join each refusal to the commit that followed it. The log is
written where each hook closes on its refusal exit, never inside `run`: the unit suites run
inside the repo-writes window, and a line written there would be reported by that lane as a
stray write into `.local/`.

RUNS THE REAL HOOK PAIR over `git commit` in a throwaway repo, on the fixture
`test_message_first_gate` builds, so what is asserted is what the hooks executed.
"""
from __future__ import annotations

import calendar
import json
import os
import re
import subprocess
import time
import unittest
from pathlib import Path

from test_message_first_gate import (  # noqa: F401 - tearDownModule removes the shared template
    _GateFixture, _clean_env, _failed_lanes, _git, _lanes, tearDownModule)

#: Which lane a stub fails is chosen per commit through the environment git hands its hooks,
#: so one fixture can be refused by the gate, then by a suite, then pass.
FAIL_VAR = "US0904_FAIL_LANE"

#: Fails the plain `gate.py --root .` call only: the suite decision and the verdict record call
#: the same script, and failing them would change which lanes run rather than which refuses.
GATE_STUB = (
    "import os, sys\n"
    f"sys.exit(1 if os.environ.get({FAIL_VAR!r}) == 'gate' and sys.argv[1:] == ['--root', '.']"
    " else 0)\n")


class RefusalLogTests(_GateFixture):

    def _build(self, tmp: Path) -> Path:
        root = super()._build(tmp)
        # The fixture links the shared scripts template in whole. Linked here file by file
        # instead, with a gate.py of this module's own, so the shared template is never edited.
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        template = Path(os.readlink(scripts))
        scripts.unlink()
        scripts.mkdir()
        for entry in template.iterdir():
            if entry.name != "gate.py":
                (scripts / entry.name).symlink_to(entry, target_is_directory=entry.is_dir())
        (scripts / "gate.py").write_text(GATE_STUB, encoding="utf-8")
        skill_tests = root / "tools" / "skill-tests.sh"
        skill_tests.write_text(
            "#!/usr/bin/env bash\n"
            f"[ \"${{{FAIL_VAR}:-}}\" = skill-tests ] && {{ echo 'Ran 12 tests in 1.000s'; echo 'FAILED (failures=1)'; exit 1; }}\n"
            "echo 'Ran 12 tests in 1.000s'\necho OK\nexit 0\n", encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture: per-lane stubs")
        return root

    def _commit_failing(self, lane: str | None) -> tuple[int, str]:
        env = _clean_env()
        env.pop(FAIL_VAR, None)
        if lane:
            env[FAIL_VAR] = lane
        out = subprocess.run(["git", "-C", str(self.root), "commit", "-m", "feat: a thing"],
                             capture_output=True, text=True, env=env)
        return out.returncode, out.stdout + out.stderr

    def _log(self) -> list[dict]:
        path = self.root / "sdlc-studio" / ".local" / "refusals.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_a_refused_commit_logs_its_lane_and_a_clean_one_logs_nothing(self) -> None:
        """MUTANT: append the line inside `run`'s failure path. The suite lanes fail inside
        the repo-writes window, so that lane then reports the log as a stray write and refuses
        a commit whose only fault was the suite. MUTANT: log from pre-commit only - the suite
        refusal in commit-msg goes unrecorded."""
        (self.root / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
        _git(self.root, "add", "tools/thing.py")
        before = time.time()

        # Refused in pre-commit, by the gate block.
        rc, out = self._commit_failing("gate")
        self.assertNotEqual(0, rc, out)
        self.assertEqual(["gate"], _failed_lanes(out), out)
        log = self._log()
        self.assertEqual(["gate"], [r["lane"] for r in log], out)
        self.assertEqual(["tools/thing.py"], log[0]["staged"])
        # The staged content itself, so the close can tell a retry that changed the code from
        # one that carried it unchanged.
        self.assertEqual({"tools/thing.py": _git(self.root, "rev-parse", ":tools/thing.py")
                          .stdout.strip()}, log[0]["blobs"])
        self.assertRegex(log[0]["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        stamped = calendar.timegm(time.strptime(log[0]["ts"], "%Y-%m-%dT%H:%M:%SZ"))
        self.assertLessEqual(abs(stamped - before), 120, "the timestamp is not the refusal's")

        # Refused in commit-msg, by a unit suite: inside the repo-writes window.
        rc, out = self._commit_failing("skill-tests")
        self.assertNotEqual(0, rc, out)
        self.assertEqual(["skill-tests"], _failed_lanes(out), out)
        self.assertIn("repo-writes", _lanes(out), "the repo-writes lane did not run")
        log = self._log()
        self.assertEqual(["gate", "skill-tests"], [r["lane"] for r in log])
        self.assertEqual(["tools/thing.py"], log[1]["staged"])

        # A commit that passes appends nothing.
        raw = (self.root / "sdlc-studio" / ".local" / "refusals.jsonl").read_bytes()
        rc, out = self._commit_failing(None)
        self.assertEqual(0, rc, out)
        self.assertEqual([], _failed_lanes(out), out)
        self.assertEqual(raw, (self.root / "sdlc-studio" / ".local" / "refusals.jsonl")
                         .read_bytes(), "a passing commit wrote to the refusal log")
        self.assertTrue(re.search(r"(?m)^feat: a thing$",
                                  _git(self.root, "log", "--format=%s").stdout))

    def test_a_refused_message_is_logged_and_leaves_no_snapshot_open(self) -> None:
        """The message rule refuses in commit-msg BEFORE the suites, while the repo-writes
        snapshot pre-commit took is still on disk. MUTANT: drop that exit's `log_refusals` - the
        refusal goes unrecorded. MUTANT: keep the snapshot there - it outlives the refusal, and
        a later commit-msg-only run would compare the tree against a run that never happened."""
        (self.root / "tools" / "thing.py").write_text("x = 1\n", encoding="utf-8")
        _git(self.root, "add", "tools/thing.py")
        env = _clean_env()
        env.pop(FAIL_VAR, None)
        out = subprocess.run(["git", "-C", str(self.root), "commit", "-m",
                              "feat(CR0257, CR0258): two ids and no Refs trailer"],
                             capture_output=True, text=True, env=env)
        text = out.stdout + out.stderr
        self.assertNotEqual(0, out.returncode, text)
        self.assertEqual(["message-refs"], _failed_lanes(text), text)
        # The positive control: the suites WERE selected, so the snapshot was taken.
        self.assertIn("unit suites selected", text)
        self.assertEqual(["message-refs"], [r["lane"] for r in self._log()])
        self.assertEqual(["tools/thing.py"], self._log()[0]["staged"])
        self.assertEqual({"tools/thing.py": _git(self.root, "rev-parse", ":tools/thing.py")
                          .stdout.strip()}, self._log()[0]["blobs"])
        snapshot = _git(self.root, "rev-parse", "--git-path", "sdlc-repo-writes").stdout.strip()
        self.assertFalse((self.root / snapshot).exists(),
                         "the repo-writes snapshot outlived the message refusal")


if __name__ == "__main__":
    unittest.main()
