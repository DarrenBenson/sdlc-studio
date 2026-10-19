"""US1078: tools/run-suite.sh runs on the gate host this clone configures, against the tree it hashes.

Built on test_remote_gate_push.py's fixture and stubbed transport: a clone, its origin, a fake
host's home, and an ssh that runs the command there. The clone carries the real run-suite.sh and
remote-gate.sh. Its suite is one test, `checks/test_value.py`, which passes while `value.txt`
reads `green`; the host's `~/sdlc-gate/gate-env.sh` names that suite as the command, so the host
side runs the commit's own run-suite.sh exactly as it would run the real one.

Which tree reached the host is read from the outcome, never from the script's word for it: a red
edit that is staged, or not staged at all, turns the host's run red only if that edit was sent.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_remote_gate_push import HOST, REPO, _git, _HostClone  # noqa: E402

CHECK = """from pathlib import Path


def test_value():
    assert Path("value.txt").read_text(encoding="utf-8").strip() == "green"
"""

#: The host's suite command, named in its gate-env.sh as a real host names its Python and Node.
HOST_SUITE = "python3 -B -m pytest -q -p no:cacheprovider checks"


class _SuiteClone(_HostClone):
    """A clone whose suite is one test, run on a fixture host through run-suite.sh."""

    def __init__(self) -> None:
        super().__init__()
        shutil.copy(REPO / "tools" / "run-suite.sh", self.clone / "tools" / "run-suite.sh")
        (self.clone / "checks").mkdir()
        (self.clone / "checks" / "test_value.py").write_text(CHECK, encoding="utf-8")
        self.commit("a suite of one test", **{"value.txt": "green\n"})
        gate_dir = self.host_home / "sdlc-gate"
        gate_dir.mkdir(parents=True, exist_ok=True)
        (gate_dir / "gate-env.sh").write_text(f"export SUITE_CMD_OVERRIDE='{HOST_SUITE}'\n",
                                              encoding="utf-8")

    def write(self, name: str, body: str) -> None:
        (self.clone / name).write_text(body, encoding="utf-8")

    def run_suite(self, *args: str, **extra: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("GIT_") and k not in ("SDLC_GATE_LOCAL", "SUITE_CMD_OVERRIDE",
                                                         "SDLC_STUDIO_BOUNDARY_SUITE", "PYTHONPATH")}
        env.update({"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                    "STUB_SSH_LOG": str(self.tmp / "ssh.log"), "STUB_GATE_LOG": str(self.tmp / "gate.log"),
                    "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"),
                    "STUB_HOST_HOME": str(self.host_home), "STUB_HOST_PATH": self.host_path()})
        env.update(extra)
        return subprocess.run(["bash", "tools/run-suite.sh", *args], cwd=self.clone, env=env,
                              capture_output=True, text=True, timeout=300)

    def verdict(self) -> dict:
        return json.loads((self.clone / "sdlc-studio" / ".local" / "suite-verdict.json")
                          .read_text(encoding="utf-8"))

    def suite_calls(self) -> list[str]:
        return [c for c in self.ssh_calls() if " remote --clone " in c]


class RunSuiteRemoteTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fx = _SuiteClone()
        self.addCleanup(self.fx.cleanup)

    def test_the_hashed_tree_is_what_runs(self) -> None:
        """AC1. Mutant: the wrapper sends HEAD instead of the hashed tree (HEAD is green, so the
        host's run passes over a staged red change)."""
        fx = self.fx
        head = _git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        fx.write("value.txt", "red\n")
        _git(fx.clone, "add", "value.txt")
        r = fx.run_suite("all")
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, "the host's run passed over a red change:\n" + out)
        self.assertEqual(len(fx.suite_calls()), 1, "the suite was not run on the host:\n" + out)
        self.assertTrue(any(line.startswith("FAILED checks/test_value.py::test_value")
                            for line in out.splitlines()), "the failing test is not named:\n" + out)
        named = r.stderr.split("failing test(s):", 1)[-1].split("full output:", 1)[0].split()
        self.assertEqual(named.count("FAILED"), 1, "the wrapper names the failing test more than once:\n" + r.stderr)
        self.assertEqual(_git(fx.clone, "rev-parse", "HEAD").stdout.strip(), head,
                         "running the suite on the host moved HEAD")
        self.assertEqual(_git(fx.clone, "diff", "--cached", "--name-only").stdout.split(), ["value.txt"],
                         "running the suite on the host changed what is staged")

    def test_an_unstaged_red_edit_is_judged(self) -> None:
        """AC2. Mutant: the wrapper sends only the index, recording a green over an unstaged red
        edit."""
        fx = self.fx
        fx.write("notes.txt", "a staged change the suite does not read\n")
        _git(fx.clone, "add", "notes.txt")
        fx.write("value.txt", "red\n")
        r = fx.run_suite("all")
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, "a green was recorded over an unstaged red edit:\n" + out)
        self.assertEqual(len(fx.suite_calls()), 1, "the suite was not run on the host:\n" + out)
        self.assertNotEqual(fx.verdict()["exit_code"], 0, "the verdict records the red run as green")

    def test_check_reads_the_host_verdict(self) -> None:
        """AC3. Mutants: the host's verdict is not written to the local suite verdict; it is
        bound to HEAD's tree rather than the tree that was sent."""
        fx = self.fx
        fx.write("notes.txt", "an untracked file, so the tree sent is not HEAD's\n")
        r = fx.run_suite("all")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(fx.suite_calls()), 1, "the suite was not run on the host")
        check = fx.run_suite("--check")
        self.assertEqual(check.returncode, 0, "a green host run did not satisfy --check:\n" + check.stderr)
        self.assertIn("GREEN (all)", check.stdout)
        fx.write("notes.txt", "one further edit\n")
        check = fx.run_suite("--check")
        self.assertEqual(check.returncode, 1, "--check accepted a tree edited after the host's run")
        self.assertIn("TREE has changed", check.stderr)

    def test_the_suite_runs_where_the_configuration_says(self) -> None:
        """AC4. Mutants: the wrapper ignores `sdlc.gateHost`, or SDLC_GATE_LOCAL. With a host, the
        run there takes the host's suite command, never this machine's; with no host, or with the
        documented local escape, the suite runs here and nothing is sent."""
        fx = self.fx
        marker = "touch ran-here"
        r = fx.run_suite("all", SUITE_CMD_OVERRIDE=marker)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(fx.suite_calls()), 1, "a configured host was not used:\n" + r.stdout + r.stderr)
        self.assertIn(f"on {HOST} (sdlc.gateHost)", r.stdout)
        self.assertFalse((fx.clone / "ran-here").exists(),
                         "this machine's suite command ran, or reached the host, in a run sent there")
        for case, extra in (("SDLC_GATE_LOCAL", {"SDLC_GATE_LOCAL": "1", "SUITE_CMD_OVERRIDE": marker}),
                            ("no host", {"SUITE_CMD_OVERRIDE": marker})):
            with self.subTest(case=case):
                if case == "no host":
                    _git(fx.clone, "config", "--unset", "sdlc.gateHost")
                (fx.clone / "ran-here").unlink(missing_ok=True)
                before = len(fx.suite_calls())
                r = fx.run_suite("all", **extra)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertTrue((fx.clone / "ran-here").exists(), "the suite did not run here")
                self.assertEqual(len(fx.suite_calls()), before, "the suite was sent to a host")

    def test_the_host_runs_the_suite_itself(self) -> None:
        """A host whose own git config names a gate host still runs the suite it was sent, rather
        than sending it on. Mutant: the host side launches run-suite.sh without SDLC_GATE_LOCAL."""
        fx = self.fx
        (fx.host_home / ".gitconfig").write_text(
            "[sdlc]\n\tgateHost = onward.invalid\n\tgateSsh = false\n", encoding="utf-8")
        r = fx.run_suite("all")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, "the host did not run the suite itself:\n" + out)
        self.assertNotIn("onward.invalid", out)

    def test_an_unreachable_host_names_the_local_escape(self) -> None:
        """A host that cannot be reached is a red verdict naming the way to run the suite here,
        not the push's escape. Mutant: the transport failure names `git push`."""
        fx = self.fx
        r = fx.run_suite("all", STUB_SSH_FAIL="before")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("SDLC_GATE_LOCAL=1 tools/run-suite.sh all", r.stderr)
        self.assertNotIn("git push", r.stderr)
        self.assertEqual(fx.verdict()["exit_code"], 3, "an unreachable host left no red verdict")


if __name__ == "__main__":
    unittest.main()
