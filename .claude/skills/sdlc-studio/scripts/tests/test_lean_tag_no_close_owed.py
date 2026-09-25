"""US0942: the release tag is refused only for what a release needs, not for close-owed debt.

`release_cut.py tag-check` asks two questions - was the gate recorded green on this commit, and
did CI pass on the forge - and `gate.py --require-close` is retired by name. The close-owed
detector stays behind the `status`/`hint` advisory.

AC1-AC4 drive the shipped entry points as subprocesses against throwaway workspaces, with a
scripted `gh` on PATH so no network is touched. AC5 reads this repository's own artefacts, as
the criterion names them, and skips from an installed copy.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import close_owed  # noqa: E402
import gitutil  # noqa: E402
import workspace  # noqa: E402

UNITS = ("US0001", "US0002", "US0003")
#: What a green forge answers `gh run list --commit <sha> --json ...` with.
GREEN_RUNS = '[{"workflowName": "Lint", "status": "completed", "conclusion": "success"}]'


def _run(script: str, *argv: str, root: Path, env: dict | None = None
         ) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), "--root", str(root),
                           *argv], capture_output=True, text=True, check=False, timeout=300,
                          env=env or gitutil.git_env())


def _git(root: Path, *argv: str) -> str:
    return gitutil.git(list(argv), cwd=root, text=True).stdout.strip()


def _story(root: Path, uid: str, status: str) -> None:
    (root / "sdlc-studio" / "stories" / f"{uid}-a-story.md").write_text(
        f"# {uid}: a story\n\n> **Status:** {status}\n> **Points:** 2\n", encoding="utf-8")


def _owed_workspace(root: Path) -> None:
    """Three delivery units that went terminal after the close-owed baseline, with no retro
    naming them: exactly what `close_owed.py detect` refuses on."""
    for sub in ("stories", "retros"):
        (root / "sdlc-studio" / sub).mkdir(parents=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    for uid in UNITS:
        _story(root, uid, "In Progress")
    # Stamped while the units are open, so the baseline cannot grandfather them.
    close_owed.stamp_baseline(root, date="2026-01-01")
    for uid in UNITS:
        _story(root, uid, "Done")


class TagNoCloseOwedTests(unittest.TestCase):

    def _tagged_repo(self) -> tuple[Path, str, dict]:
        """A committed owed workspace with a GitHub remote and a `gh` that reports CI green."""
        d = tempfile.TemporaryDirectory(prefix="us0942_")
        self.addCleanup(d.cleanup)
        root = Path(d.name) / "repo"
        root.mkdir()
        _owed_workspace(root)
        _git(root, "init", "-q")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "c")
        _git(root, "remote", "add", "origin", "https://github.com/example/project.git")
        sha = _git(root, "rev-parse", "HEAD")
        fake = Path(d.name) / "bin"
        fake.mkdir()
        gh = fake / "gh"
        gh.write_text(f"#!/bin/sh\ncat <<'EOF'\n{GREEN_RUNS}\nEOF\n", encoding="utf-8")
        gh.chmod(0o755)
        # Confined like the fixture's own calls, so the `git remote` inside `tag-check` reads
        # this fixture and never a repository an inherited GIT_DIR names.
        env = gitutil.git_env(PATH=f"{fake}{os.pathsep}{os.environ.get('PATH', '')}")
        # The fixture is what it claims: the detector refuses on these three units.
        detect = _run("close_owed.py", "detect", root=root)
        self.assertEqual(1, detect.returncode, detect.stdout + detect.stderr)
        for uid in UNITS:
            self.assertIn(uid, detect.stdout + detect.stderr)
        return root, sha, env

    def test_uncovered_units_do_not_refuse_the_tag(self) -> None:
        """AC1. MUTANT: restore the close-owed half of `tag_check` - it refuses on US0001-3."""
        root, sha, env = self._tagged_repo()
        r = _run("release_cut.py", "record-green", "--commit", sha, root=root, env=env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        r = _run("release_cut.py", "tag-check", "--commit", sha, root=root, env=env)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertIn("CI green on the forge", out)
        for uid in UNITS:
            self.assertNotIn(uid, out)

    def test_a_green_on_another_commit_still_refuses(self) -> None:
        """AC2. MUTANT: delete the whole guard rather than its close-owed half - it allows."""
        root, sha, env = self._tagged_repo()
        other = "0" * 40
        r = _run("release_cut.py", "record-green", "--commit", other, root=root, env=env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        r = _run("release_cut.py", "tag-check", "--commit", sha, root=root, env=env)
        out = r.stdout + r.stderr
        self.assertEqual(2, r.returncode, out)
        self.assertIn(other, out)
        self.assertIn(sha, out)

    def test_require_close_is_retired(self) -> None:
        """AC3. MUTANT: drop the flag from the parser - argparse exits 2 on an unrecognised
        argument that names neither the retirement nor `sprint sign`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            r = _run("gate.py", "--require-close", root=root)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("--require-close is retired", r.stderr)
        self.assertIn("`sprint sign`", r.stderr)
        self.assertNotIn("unrecognized arguments", r.stderr)

    def test_the_status_advisory_stays(self) -> None:
        """AC4. MUTANT: delete `close_owed.py` with the bindings - the advisory goes silent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _owed_workspace(root)
            r = _run("status.py", "hint", root=root)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        line = next((ln for ln in r.stdout.splitlines()
                     if ln.startswith("advisory: a sprint close is owed")), None)
        self.assertIsNotNone(line, r.stdout)
        for uid in UNITS:
            self.assertIn(uid, line)

    def test_no_stamp_names_the_retired_flag(self) -> None:
        """AC5, over this repository. MUTANT: remove the doc lines and leave US0166 AC3 as a
        `Verified: yes` shell grep for `require-close` - a live stamp then names the flag."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        repo = workspace.REPO
        retired = re.compile(r"require-close|TagRefusesAnOwedCloseTests|"
                             r"TagCheckReadsTheBlockingPredicateTests|CloseOwedGateLaneTests|"
                             r"CloseOwedLaneIsOptInTests|-k CloseOwed\b")
        live = []
        for kind in ("stories", "bugs"):
            for path in sorted((repo / "sdlc-studio" / kind).glob("*.md")):
                for line in path.read_text(encoding="utf-8").splitlines():
                    m = re.search(r"\*\*Verify:\*\*\s*(.*)", line)
                    if m and not m.group(1).startswith("manual") and retired.search(m.group(1)):
                        live.append(f"{path.name}: {m.group(1)}")
        self.assertEqual([], live, "a live stamp still names the retired close-owed surface")

        # General, not by name: any stamped-green criterion whose selector names a test module
        # this unit edits must still select something, so a deleted node cannot leave a stamp.
        # The edited modules are read from this story's own `Affects`, never copied here.
        import verify_ac  # noqa: PLC0415
        from lib import sdlc_md  # noqa: PLC0415
        own = next((repo / "sdlc-studio" / "stories").glob("US0942-*.md"))
        edited = [Path(p).name for p in sdlc_md.affects_files(own.read_text(encoding="utf-8"))
                  if "/tests/test_" in p]
        self.assertIn("test_release_cut.py", edited)
        dead = [f"{row['record']} {row['ac']}: {row['verifier']}"
                for kind in ("stories", "bugs")
                for path in sorted((repo / "sdlc-studio" / kind).glob("*.md"))
                for row in verify_ac.unresolvable_stamps(path, repo)
                if any(name in row["verifier"] for name in edited)]
        self.assertEqual([], dead, "a stamp rests on a test node this unit deleted")

        # Criteria whose claim is about the retired surface, though their selectors still run:
        # a stamp that stays green by asserting the opposite of its words is not caught above.
        retired = {"US0166": ("AC3",), "US0226": ("AC2", "AC3"), "US0165": ("AC1", "AC2"),
                   "BG0311": ("AC1", "AC2", "AC3"), "BG0668": ("AC1", "AC2", "AC3")}
        for uid, acs in retired.items():
            kind = "bugs" if uid.startswith("BG") else "stories"
            text = next((repo / "sdlc-studio" / kind).glob(f"{uid}-*.md")).read_text(
                encoding="utf-8")
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(text)}
            for ac in acs:
                with self.subTest(unit=uid, ac=ac):
                    self.assertTrue(blocks[ac].verifier.startswith("manual - retired by US0942"),
                                    blocks[ac].verifier)
                    self.assertTrue((blocks[ac].verified_state or "").startswith("manual"),
                                    blocks[ac].verified_state)

        pins = subprocess.run([sys.executable, "-B", "-m", "unittest",
                               "tests.test_verify_ac.US0166Ac3Tests"],
                              cwd=SCRIPTS, capture_output=True, text=True, timeout=300)
        self.assertEqual(0, pins.returncode, pins.stderr[-2000:])

        drift = subprocess.run([sys.executable, "-B", str(SCRIPTS / "docgen.py"), "surface",
                                "--check"], cwd=repo, capture_output=True, text=True,
                               timeout=300)
        # `--check` reports and always exits 0, so the count is the verdict.
        self.assertIn("docgen surface: 0 drift item(s)", drift.stdout, drift.stderr)


if __name__ == "__main__":
    unittest.main()
