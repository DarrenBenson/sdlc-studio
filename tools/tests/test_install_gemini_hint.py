"""BG0774: install.sh must exit 0 after installing the gemini target when the gemini CLI is
absent. `native_hint` ended in `command -v gemini && echo ...`, so with no gemini on PATH the
function returned 1, `set -e` aborted the installer after the skill was already installed,
and the Next steps output stopped at the gemini line.

Each test drives the real installer end to end, hermetically: a scratch HOME, `--from` a
minimal skill copy and `--no-sweep`, so nothing outside the temp dir is read or written.
"""
# test-census-subject: install.sh
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
BASE_PATH = "/usr/bin:/bin"
GEMINI_HINT = "native: gemini skills install https://github.com/DarrenBenson/sdlc-studio"
NEXT_STEPS_TAIL = "Then: status / hint / help"


class InstallGeminiHintTests(unittest.TestCase):
    def _src(self, root: Path) -> Path:
        src = root / "src" / "sdlc-studio"
        (src / "templates").mkdir(parents=True)
        (src / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
        (src / "templates" / "version.yaml").write_text(
            'skill_version: "9.9.9"\n', encoding="utf-8")
        return src

    def _install_gemini(self, root: Path, path: str) -> subprocess.CompletedProcess:
        home = root / "home"
        home.mkdir()
        return subprocess.run(
            ["bash", str(INSTALL_SH), "--from", str(self._src(root)), "--no-sweep",
             "--target", "gemini"],
            env={"PATH": path, "HOME": str(home)}, cwd=str(root),
            capture_output=True, text=True, timeout=60)

    def test_the_gemini_target_installs_cleanly_without_the_gemini_cli(self) -> None:
        # The premise, asserted rather than assumed: a PATH that holds a gemini would
        # exercise the present-CLI branch and pass whatever native_hint does.
        self.assertIsNone(shutil.which("gemini", path=BASE_PATH),
                          f"precondition: {BASE_PATH} must not hold a gemini command")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = self._install_gemini(root, BASE_PATH)
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertTrue((root / "home" / ".gemini" / "skills" / "sdlc-studio"
                             / "SKILL.md").is_file(), out)
            self.assertIn("Next steps:", proc.stdout)
            self.assertIn("Gemini CLI: run /skills", proc.stdout)
            self.assertIn(NEXT_STEPS_TAIL, proc.stdout)   # the output ran to its end
            self.assertNotIn("native: gemini", proc.stdout)

    def test_the_gemini_hint_still_shows_when_the_cli_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stub_bin = root / "bin"
            stub_bin.mkdir()
            stub = stub_bin / "gemini"
            stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            stub.chmod(0o755)
            proc = self._install_gemini(root, f"{stub_bin}{os.pathsep}{BASE_PATH}")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn(GEMINI_HINT, proc.stdout)
            self.assertIn(NEXT_STEPS_TAIL, proc.stdout)


if __name__ == "__main__":
    unittest.main()
