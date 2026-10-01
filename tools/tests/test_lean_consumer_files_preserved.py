"""US0976: install and upgrade never damage a consumer's own files.

Three files a consuming project owns were damaged by the tools that maintain it: `init.py run
--force` rewrote `sdlc-studio/.version`, erasing the version the project was created at; the
migrate's `.gitignore` append wrote LF over a CRLF file and a regular file over a symlink; and an
explicit `install.sh --target copilot` replaced a folder holding only a user's notes. Each test
drives the shipped entry point in a throwaway tree.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/project_upgrade.py
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
INSTALL_SH = REPO / "install.sh"


def _py(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=300)


class ConsumerFilesPreservedTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name).resolve()

    def _project(self, name: str) -> Path:
        root = self.base / name
        root.mkdir()
        proc = _py("init.py", "run", "--root", str(root))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        return root

    def test_init_force_keeps_the_version_record(self) -> None:
        """AC1. MUTANT: HEAD, where `--force` rewrites `.version` with the running version."""
        root = self._project("p")
        version = root / "sdlc-studio" / ".version"
        text = version.read_text(encoding="utf-8")
        self.assertEqual(1, len(re.findall(r'skill_version: "[^"]*"', text)), text)
        version.write_text(re.sub(r'skill_version: "[^"]*"', 'skill_version: "5.0.0"', text),
                           encoding="utf-8")
        proc = _py("init.py", "run", "--force", "--root", str(root))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn('skill_version: "5.0.0"', version.read_text(encoding="utf-8"))

    def test_the_gitignore_append_keeps_endings_and_links(self) -> None:
        """AC2. MUTANT: read through universal newlines and write LF - the CRLF file becomes a
        whole-file diff. MUTANT: replace the path - the symlink becomes a regular file and its
        target never gets the rule."""
        crlf = self._project("crlf")
        gi = crlf / "sdlc-studio" / ".gitignore"
        gi.write_bytes(b"# mine\r\nbuild/\r\n")
        proc = _py("migrate.py", "--apply", "--root", str(crlf))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        data = gi.read_bytes()
        self.assertIn(b".local/", data)
        self.assertTrue(data.startswith(b"# mine\r\nbuild/\r\n"), data)
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"), f"an LF-only line: {data!r}")

        linked = self._project("linked")
        target = self.base / "shared.gitignore"
        target.write_text("build/\n", encoding="utf-8")
        gi = linked / "sdlc-studio" / ".gitignore"
        gi.unlink()
        gi.symlink_to(target)
        proc = _py("migrate.py", "--apply", "--root", str(linked))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue(gi.is_symlink(), "the symlinked .gitignore was replaced by a file")
        self.assertIn(".local/", target.read_text(encoding="utf-8"))
        self.assertTrue(target.read_text(encoding="utf-8").startswith("build/\n"))

    def test_a_crlf_file_with_no_final_newline_gets_a_crlf_separator(self) -> None:
        """The separator before the appended rule is the file's own line ending. MUTANT: join
        with a bare LF when the file does not end in a newline - one LF-only line appears."""
        root = self._project("crlf_open")
        gi = root / "sdlc-studio" / ".gitignore"
        gi.write_bytes(b"# mine\r\nbuild/")
        proc = _py("migrate.py", "--apply", "--root", str(root))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        data = gi.read_bytes()
        self.assertTrue(data.startswith(b"# mine\r\nbuild/\r\n#"), data)
        self.assertEqual(data.count(b"\n"), data.count(b"\r\n"), data)

    def test_the_append_keeps_the_file_mode(self) -> None:
        """MUTANT: write with the temp file's own 0600 mode - a group-readable ignore file is
        silently narrowed."""
        root = self._project("mode")
        gi = root / "sdlc-studio" / ".gitignore"
        gi.write_text("build/\n", encoding="utf-8")
        gi.chmod(0o664)
        proc = _py("migrate.py", "--apply", "--root", str(root))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn(".local/", gi.read_text(encoding="utf-8"))
        self.assertEqual(0o664, gi.stat().st_mode & 0o777)

    def _legacy_amigo(self, root: Path) -> Path:
        amigos = root / "sdlc-studio" / "personas" / "amigos"
        amigos.mkdir(parents=True)
        (amigos / "qa.md").write_text("<!-- role: qa -->\n# Sam - QA\n", encoding="utf-8")
        return root / "sdlc-studio" / "personas" / "seats" / "qa.md"

    def test_an_unwritable_gitignore_link_needs_a_human_and_the_step_goes_on(self) -> None:
        """Round-1 repro. A dangling link, and a link into a read-only directory: the write
        through it fails. MUTANT: let the failure escape - the whole conventions step aborts and
        the legacy amigo card is never moved. MUTANT: swallow it - nobody is told the ignore
        file still lacks the rule."""
        if os.geteuid() == 0:                       # pragma: no cover - root writes anywhere
            self.skipTest("root can write a read-only directory")
        locked = self.base / "locked"
        locked.mkdir()
        (locked / "shared.gitignore").write_text("build/\n", encoding="utf-8")
        locked.chmod(0o555)
        self.addCleanup(locked.chmod, 0o755)
        for name, target in (("dangling", self.base / "gone" / "shared.gitignore"),
                             ("readonly", locked / "shared.gitignore")):
            with self.subTest(case=name):
                root = self._project(name)
                gi = root / "sdlc-studio" / ".gitignore"
                gi.unlink()
                gi.symlink_to(target)
                seat = self._legacy_amigo(root)
                proc = _py("migrate.py", "--apply", "--root", str(root))
                out = proc.stdout + proc.stderr
                self.assertEqual(0, proc.returncode, out)
                self.assertTrue(seat.is_file(), f"the amigo card was not moved:\n{out}")
                self.assertTrue(gi.is_symlink(), out)
                human = out.split("## Needs a human", 1)[-1] if "## Needs a human" in out else ""
                self.assertIn(f"sdlc-studio/.gitignore is a link to {target}", human, out)

    def test_an_explicit_install_skips_a_foreign_folder(self) -> None:
        """AC3. MUTANT: HEAD, which swaps the folder out and removes notes.txt. MUTANT: skip any
        existing folder - an empty one, which holds nothing of the user's, must still install."""
        src = self.base / "src" / "sdlc-studio"
        (src / "templates").mkdir(parents=True)
        (src / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
        (src / "templates" / "version.yaml").write_text('skill_version: "6.0.0"\n',
                                                        encoding="utf-8")
        home = self.base / "home"
        foreign = home / ".agents" / "skills" / "sdlc-studio"
        foreign.mkdir(parents=True)
        (foreign / "notes.txt").write_text("mine\n", encoding="utf-8")

        def install() -> subprocess.CompletedProcess:
            return subprocess.run(
                ["bash", str(INSTALL_SH), "--target", "copilot", "--from", str(src)],
                cwd=str(self.base), env={"HOME": str(home), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=120)

        proc = install()
        out = proc.stdout + proc.stderr
        self.assertEqual("mine\n", (foreign / "notes.txt").read_text(encoding="utf-8"), out)
        self.assertFalse((foreign / "SKILL.md").exists(), out)
        self.assertEqual(1, out.count(f"{foreign} (no sdlc-studio SKILL.md - not touching it)"),
                         out)
        # the control: an empty folder holds nothing of anyone's, and is installed into
        (foreign / "notes.txt").unlink()
        proc = install()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertTrue((foreign / "SKILL.md").is_file(), proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
