"""US1077: one command says whether a gate host can judge a push.

Built on test_remote_gate_push.py's fixture and stubbed transport. What the fixture host holds is
decided by the test, never by this machine, with US1004's dist-info technique: the host's
`python3` runs this interpreter with `-S`, so none of its own site-packages are visible, and a
PYTHONPATH of `*.dist-info` records the test writes first. The clone carries the REAL
tools/gate_prereqs.py and the real requirements-dev.txt, plus one requirement only this fixture
names, so a doctor reading a list of its own instead of the one list gives a different answer.
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_remote_gate_push import HOST, REPO, _git, _HostClone  # noqa: E402

sys.path.insert(0, str(REPO / "tools"))
import gate_prereqs  # noqa: E402

FIXTURE_ONLY = "sdlc-fixture-only-dist"


class _DoctorClone(_HostClone):
    """A clone carrying the real checker and the one list, and a host whose distributions are
    exactly the ones a test writes."""

    def __init__(self) -> None:
        super().__init__()
        shutil.copy(REPO / "tools" / "gate_prereqs.py", self.clone / "tools" / "gate_prereqs.py")
        shutil.copy(REPO / "tools" / "enable-hooks.sh", self.clone / "tools" / "enable-hooks.sh")
        listing = (REPO / "requirements-dev.txt").read_text(encoding="utf-8")
        (self.clone / "requirements-dev.txt").write_text(
            listing.rstrip("\n") + f"\n{FIXTURE_ONLY}>=1.0\n", encoding="utf-8")
        self.commit("the real checker and the one list")
        self.rows, unread = gate_prereqs.requirements(self.clone)
        assert not unread, unread
        assert any(gate_prereqs.normalise(d) == "pytest-xdist" for d, _ in self.rows)

    def host(self, *, without: tuple[str, ...] = (), lacking: tuple[str, ...] = ()) -> str:
        """A host PATH whose python3 sees exactly the list's distributions, less `without`, and
        which carries node and npm. With `lacking`, the PATH is ONLY that directory, holding the
        few commands the transport and the doctor use, less the executables `lacking` names."""
        bin_dir = Path(tempfile.mkdtemp(prefix="doctor-host-", dir=self.tmp))
        dists = bin_dir / "dists"
        dists.mkdir()
        for dist, floor in self.rows:
            if gate_prereqs.normalise(dist) in {gate_prereqs.normalise(w) for w in without}:
                continue
            version = ".".join(map(str, floor)) if floor else "99.0"
            info = dists / f"{dist.replace('-', '_')}-{version}.dist-info"
            info.mkdir()
            (info / "METADATA").write_text(f"Metadata-Version: 2.1\nName: {dist}\nVersion: {version}\n",
                                           encoding="utf-8")
        (bin_dir / "python3").write_text(
            f"#!/bin/sh\nPYTHONPATH={shlex.quote(str(dists))} exec {shlex.quote(sys.executable)} -S \"$@\"\n",
            encoding="utf-8")
        for tool in ("node", "npm"):
            if tool not in lacking:
                (bin_dir / tool).write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        for f in bin_dir.iterdir():
            if f.is_file():
                f.chmod(0o755)
        if not lacking:
            return os.pathsep.join([str(bin_dir), os.environ.get("PATH", "/usr/bin:/bin")])
        for tool in ("bash", "sh", "tar", "mktemp", "rm", "uname", "git"):
            if tool not in lacking:
                (bin_dir / tool).symlink_to(shutil.which(tool))
        return str(bin_dir)

    def env(self, host_path: str) -> dict:
        base = {k: v for k, v in os.environ.items()
                if not k.startswith("GIT_") and k not in ("SDLC_GATE_LOCAL", "PYTHONPATH")}
        path = self.path()
        for tool in ("sed", "basename"):
            if not (path / tool).exists():
                (path / tool).symlink_to(shutil.which(tool))
        base.update({"PATH": str(path), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                     "STUB_SSH_LOG": str(self.tmp / "ssh.log"), "STUB_GATE_LOG": str(self.tmp / "gate.log"),
                     "STUB_PREREQ_LOG": str(self.tmp / "prereq.log"),
                     "STUB_HOST_HOME": str(self.host_home), "STUB_HOST_PATH": host_path})
        return base

    def doctor(self, host_path: str, **extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", "tools/remote-gate.sh", "doctor"], cwd=self.clone,
                              env={**self.env(host_path), **extra}, capture_output=True, text=True,
                              timeout=120)


class GateHostDoctorTests(unittest.TestCase):

    def setUp(self) -> None:
        self.fx = _DoctorClone()
        self.addCleanup(self.fx.cleanup)

    def test_a_complete_host_is_reported_ready(self) -> None:
        """AC1. Mutants: the doctor checks a hard-coded list of its own instead of the one list
        (it then misses the requirement only this fixture names); it does not name the host."""
        fx = self.fx
        r = fx.doctor(fx.host())
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn(f"{HOST} is ready to judge a push", out)
        r = fx.doctor(fx.host(without=(FIXTURE_ONLY,)))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0,
                            "a host lacking a distribution only this clone's list names was called ready:\n" + out)
        self.assertIn(FIXTURE_ONLY, out, "the doctor did not read the clone's own list")

    def test_a_missing_prerequisite_is_named(self) -> None:
        """AC2. Mutant: the doctor reports ready without checking each entry, or names the gap
        without its install route."""
        fx = self.fx
        r = fx.doctor(fx.host(without=("pytest-xdist",)))
        out = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, "a host without pytest-xdist was called ready:\n" + out)
        line = next((ln for ln in out.splitlines() if "pytest-xdist" in ln), "")
        self.assertTrue(line, "the missing pytest-xdist is not named:\n" + out)
        self.assertIn("Install:", line, "the missing prerequisite is named without its install route")
        self.assertIn(f"{HOST} is NOT ready to judge a push", out)

    def test_what_else_a_host_needs_is_named(self) -> None:
        """The doctor's other claims, each able to fail: git on the host's ssh PATH, Node and npm,
        and an unreachable host told apart from an unready one. Mutants: any of the three checks
        dropped; a transport failure reported as a host that is not ready."""
        fx = self.fx
        r = fx.doctor(fx.host(lacking=("_",)))
        self.assertEqual(r.returncode, 0, "the minimal host PATH is itself incomplete:\n" + r.stderr)
        for tool, named in (("git", "git is not on"), ("node", "node is not on"), ("npm", "npm is not on")):
            with self.subTest(lacking=tool):
                r = fx.doctor(fx.host(lacking=(tool,)))
                self.assertEqual(r.returncode, 1, f"a host without {tool} was not refused:\n" + r.stderr)
                self.assertIn(named, r.stderr)
                self.assertIn(f"{HOST} is NOT ready", r.stderr)
        r = fx.doctor(fx.host(), STUB_SSH_FAIL="before")
        self.assertEqual(r.returncode, 3, "an unreachable host is not exit 3:\n" + r.stderr)
        self.assertIn(f"{HOST} could not be reached", r.stderr)
        self.assertNotIn("NOT ready", r.stderr, "an unreachable host was reported as one that is not ready")

    def test_enable_hooks_names_the_host_and_its_verdict(self) -> None:
        """AC3. Mutant: enable-hooks.sh does not mention the gate host, or does not ask it."""
        fx = self.fx
        r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=fx.clone, env=fx.env(fx.host()),
                           capture_output=True, text=True, timeout=180)
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        self.assertIn(f"Gate host: {HOST}", out, "enable-hooks.sh does not name the configured gate host")
        self.assertIn(f"{HOST} is ready to judge a push", out, "enable-hooks.sh does not give the host's verdict")
        _git(fx.clone, "config", "--unset", "sdlc.gateHost")
        r = subprocess.run(["bash", "tools/enable-hooks.sh"], cwd=fx.clone, env=fx.env(fx.host()),
                           capture_output=True, text=True, timeout=180)
        self.assertNotIn("Gate host:", r.stdout + r.stderr, "a gate host was named though none is configured")


if __name__ == "__main__":
    unittest.main()
