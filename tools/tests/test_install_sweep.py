"""Regression test for BG0054: install.sh must not abort under `set -e` after a
successful stale-copy sweep.

`sweep_stale` ends by reporting whether any other copy was found. When it *did*
refresh a copy (`found=true`), a trailing `[[ ... ]] && info` compound returns 1,
and `set -e` then kills the installer before the success banner prints. This test
sources install.sh (which only runs `main` when executed, not when sourced),
stubs the environment probes, and asserts `sweep_stale` exits 0 in the
found-a-copy case.
"""
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"

# Source the installer, stub the filesystem/version probes so the sweep believes
# it found one stale copy to refresh, run in dry-run (no rm/cp), and surface the
# function's exit code. `set -e` is enabled to mirror the real script.
DRIVER = r"""
set -e
source "__INSTALL_SH__"

DRY_RUN=true
ALL_TARGETS="gemini"          # a single location to probe
VERSION="9.9.9"

# Stub the environment probes: pretend a stale sdlc-studio copy exists at $STALE.
target_dir() { [[ "$2" == global ]] && echo "$STALE_PARENT" || echo ""; }
is_skill_copy() { return 0; }
installed_version() { echo "0.0.1"; }

sweep_stale "/nonexistent/src" ""
echo "SWEEP_RC=$?"
"""


class InstallSweepExitCode(unittest.TestCase):
    def test_sweep_returns_zero_when_a_copy_is_refreshed(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            (parent / "sdlc-studio").mkdir()  # the "stale copy" the sweep finds
            script = DRIVER.replace("__INSTALL_SH__", str(INSTALL_SH))
            proc = subprocess.run(
                ["bash", "-c", script],
                env={"STALE_PARENT": str(parent), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=30,
            )
            # The whole point: `set -e` must not have aborted the sweep.
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertIn("SWEEP_RC=0", proc.stdout)


def _skill(path: Path, version: str) -> Path:
    """A minimal sdlc-studio skill tree: what `is_skill_copy` and `installed_version` read."""
    (path / "templates").mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
    (path / "templates" / "version.yaml").write_text(f'skill_version: "{version}"\n',
                                                     encoding="utf-8")
    return path


def _tree(path: Path) -> dict:
    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*"))
            if p.is_file()}


class LocalSweepTests(unittest.TestCase):
    """BG0809. `--local` pins a version in ONE project, so its sweep must not rewrite the
    personal copies every other project loads; and Claude Code loads a personal skill ahead of
    a project one of the same name, so a local install under a personal copy must say so.
    MUTANTS: the sweep walks both scopes under --local; the sweep is dropped altogether (the
    project's other local copies stop refreshing); the shadow note is never printed; it is
    printed without a personal copy; it names neither version."""

    def setUp(self) -> None:
        import tempfile
        base = Path(tempfile.mkdtemp(prefix="bg0809_"))
        self.addCleanup(__import__("shutil").rmtree, base, True)
        self.home, self.project = base / "home", base / "project"
        self.project.mkdir(parents=True)
        self.src = _skill(base / "src" / "sdlc-studio", "2.0.0")

    def _install(self, *argv: str) -> subprocess.CompletedProcess:
        self.home.mkdir(exist_ok=True)
        return subprocess.run(
            ["bash", str(INSTALL_SH), "--local", "--from", str(self.src), *argv],
            cwd=self.project, capture_output=True, text=True, timeout=60,
            env={"HOME": str(self.home), "PATH": "/usr/bin:/bin", "NO_COLOR": "1"})

    def test_a_local_install_leaves_personal_copies(self) -> None:
        personal = {
            "claude, same version": _skill(self.home / ".claude/skills/sdlc-studio", "2.0.0"),
            "opencode, older": _skill(self.home / ".config/opencode/skills/sdlc-studio", "1.0.0"),
        }
        for path in personal.values():      # a rewrite from the source would drop this file
            (path / "personal-only.txt").write_text("mine\n", encoding="utf-8")
        before = {k: _tree(p) for k, p in personal.items()}
        # the positive control: a stale copy in ANOTHER of this project's tool dirs is still
        # the sweep's business, so the sweep itself must not simply have gone
        project_other = _skill(self.project / ".opencode/skills/sdlc-studio", "1.0.0")
        cp = self._install("--target", "claude")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        for label, path in personal.items():
            self.assertEqual(_tree(path), before[label],
                             f"--local rewrote the personal copy ({label}) at {path}:\n{cp.stdout}")
        installed = self.project / ".claude/skills/sdlc-studio/templates/version.yaml"
        self.assertIn('"2.0.0"', installed.read_text(encoding="utf-8"), cp.stdout)
        self.assertIn('"2.0.0"', (project_other / "templates/version.yaml").read_text(
            encoding="utf-8"), f"the project's own stale copy was not refreshed:\n{cp.stdout}")

    def test_a_shadowed_local_install_is_named(self) -> None:
        cp = self._install("--target", "claude")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("ahead of", cp.stdout + cp.stderr,
                         "the shadow note printed with no personal copy")
        personal = _skill(self.home / ".claude/skills/sdlc-studio", "1.5.0")
        cp = self._install("--target", "claude")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        project = (self.project / ".claude/skills/sdlc-studio").resolve()
        notes = [ln for ln in (cp.stdout + cp.stderr).splitlines() if "ahead of" in ln]
        self.assertEqual(len(notes), 1, cp.stdout + cp.stderr)
        for part in ("Claude Code", str(personal.resolve()), "1.5.0", str(project), "2.0.0"):
            self.assertIn(part, notes[0], notes[0])
        self.assertLess(notes[0].index(str(personal.resolve())), notes[0].index("ahead of"),
                        f"the note does not say the PERSONAL copy is the one loaded: {notes[0]}")


if __name__ == "__main__":
    unittest.main()
