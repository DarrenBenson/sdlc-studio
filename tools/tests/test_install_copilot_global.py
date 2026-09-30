"""BG0852: install.sh treated Copilot as repo-scoped only. Copilot CLI reads the personal skill
folders `~/.agents/skills` and `~/.copilot/skills`, yet `copilot:global` mapped to nothing,
`--target auto` skipped copilot on a global install, detection looked for `gh` or `.github`
rather than the `copilot` binary, and the default install said nothing. A Copilot CLI user
following the quick start got no skill and no hint why.

Each test drives the real installer hermetically: a scratch HOME and project, `--from` a
minimal skill copy, and a curated PATH holding only the utilities the installer needs plus
whichever stub a test adds. This host's /usr/bin carries `gh` and `cursor`, so a PATH of
/usr/bin:/bin would detect tools the fixture says are absent.
"""
# test-census-subject: install.sh
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
BASH = shutil.which("bash") or "/bin/bash"
# What install.sh calls, and nothing that names a coding agent.
UTILITIES = ("bash", "sh", "cp", "mv", "rm", "mkdir", "grep", "sed", "tr", "sort", "head",
             "awk", "find", "mktemp", "cat", "tar", "curl", "sha256sum", "dirname", "env")
AGENT_CLIS = ("gh", "copilot", "codex", "cursor", "claude", "gemini", "opencode")


def curated_path(root: Path, stubs: tuple[str, ...] = ()) -> str:
    """A PATH of one directory: symlinks to UTILITIES, plus an `exit 0` stub per name in stubs.

    Asserts the premise rather than assuming it: no agent CLI is on it except a stub asked for.
    """
    bin_dir = root / "bin"
    bin_dir.mkdir()
    for name in UTILITIES:
        real = shutil.which(name, path="/usr/bin:/bin")
        if real:
            (bin_dir / name).symlink_to(real)
    for name in stubs:
        stub = bin_dir / name
        stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        stub.chmod(0o755)
    path = str(bin_dir)
    for cli in AGENT_CLIS:
        if cli not in stubs:
            assert shutil.which(cli, path=path) is None, f"precondition: {cli} leaked onto {path}"
    return path


def skill_copy(path: Path, version: str) -> Path:
    """A minimal sdlc-studio tree: what `is_skill_copy` and `installed_version` read."""
    (path / "templates").mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
    (path / "templates" / "version.yaml").write_text(f'skill_version: "{version}"\n',
                                                     encoding="utf-8")
    return path


def run_install(root: Path, path: str, *argv: str) -> subprocess.CompletedProcess:
    """Run install.sh from root/project with HOME at root/home, installing root/src."""
    home, project = root / "home", root / "project"
    home.mkdir(exist_ok=True)
    project.mkdir(exist_ok=True)
    src = root / "src" / "sdlc-studio"
    if not src.exists():
        skill_copy(src, "2.0.0")
    return subprocess.run(
        [BASH, str(INSTALL_SH), "--from", str(src), *argv],
        env={"PATH": path, "HOME": str(home), "NO_COLOR": "1"}, cwd=str(project),
        capture_output=True, text=True, timeout=60)


def installer_dir(target: str, scope: str, home: str = "/HOME") -> str:
    """The directory install.sh's own target_dir names, read by sourcing it."""
    proc = subprocess.run(
        [BASH, "-c", f'source "{INSTALL_SH}"; target_dir {target} {scope}'],
        env={"PATH": "/usr/bin:/bin", "HOME": home}, capture_output=True, text=True, timeout=30)
    return proc.stdout.strip()


def doc_blocks(text: str) -> list[str]:
    """A document as the units a reader takes in one go: each table row, each list item, and
    each prose paragraph. A whole-file search would let one unrelated sentence satisfy a claim
    about another."""
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        starts_item = bool(re.match(r"^(- |\* |\d+\. )", stripped))
        if not stripped or stripped.startswith("|") or starts_item:
            if current:
                blocks.append(" ".join(current))
                current = []
            if stripped.startswith("|"):
                blocks.append(stripped)
                continue
        if stripped:
            current.append(stripped)
    if current:
        blocks.append(" ".join(current))
    return blocks


class CopilotGlobalTests(unittest.TestCase):

    def test_auto_selects_a_copilot_personal_folder(self) -> None:
        """AC1. MUTANTS: auto skips copilot on a global install (today's `continue`);
        copilot:global maps to nothing; neither copilot nor agents detection looks for the
        `copilot` binary. Each leaves a copilot-only host with no personal folder planned
        (today: "No installable targets resolved"). The control - the same host without the
        stub - catches the opposite mutant, an auto that plans ~/.agents/skills always."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("copilot",)),
                               "--target", "auto", "--dry-run")
            out = proc.stdout + proc.stderr
            self.assertFalse((root / "home" / ".agents").exists(), "precondition: no ~/.agents")
            self.assertEqual(proc.returncode, 0, out)
            home = root / "home"
            planned = [ln for ln in out.splitlines() if "[dry run] would install to:" in ln]
            personal = (f"{home}/.agents/skills/sdlc-studio", f"{home}/.copilot/skills/sdlc-studio")
            self.assertTrue(any(ln.rstrip().endswith(personal) for ln in planned),
                            f"auto planned no Copilot CLI personal folder:\n{out}")
            self.assertFalse((root / "project" / ".github").exists(), out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root), "--target", "auto", "--dry-run")
            out = proc.stdout + proc.stderr
            self.assertNotIn("/.agents/skills/sdlc-studio", out,
                             "auto planned ~/.agents/skills with no tool that reads it")

    def test_default_install_hints_an_undetected_copilot(self) -> None:
        """AC2. MUTANTS: silence (no hint); a hint that names Copilot but no `--target`; a hint
        naming a --target without copilot; a hint printed with no Copilot CLI present (the
        control); a hint whose absent-CLI branch returns non-zero, which `set -e` turns into an
        aborted install (the BG0774 shape - the control asserts exit 0 and the full output)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("copilot",)), "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            home = root / "home"
            self.assertTrue((home / ".claude/skills/sdlc-studio/SKILL.md").is_file(), out)
            self.assertFalse((home / ".agents").exists(),
                             f"the default install wrote beyond Claude Code:\n{out}")
            hints = [ln for ln in out.splitlines() if "Copilot CLI" in ln and "--target" in ln]
            self.assertEqual(len(hints), 1, f"expected one Copilot CLI hint line:\n{out}")
            self.assertRegex(hints[0], r"--target \S*\bcopilot\b",
                             f"the hint names no --target that installs for Copilot: {hints[0]}")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root), "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn("Then: status / hint / help", proc.stdout, "output stopped short")
            self.assertNotIn("Copilot CLI", out, "a Copilot hint with no Copilot CLI present")

    def test_docs_do_not_call_copilot_repo_scoped(self) -> None:
        """AC4. MUTANTS: the README or INSTALL.md `(repo-scoped)` row survives; the prose still
        says Copilot skills are repo-scoped; a row names a personal folder other than the one
        install.sh writes; a line tells the reader Copilot reads `.github/skills` and stops
        there. The folder is read from install.sh itself, so docs and installer cannot drift."""
        folder = installer_dir("copilot", "global").replace("/HOME", "~", 1)
        self.assertTrue(folder.startswith("~/"),
                        f"install.sh names no personal folder for copilot: {folder!r}")
        for name in ("README.md", "docs/INSTALL.md"):
            blocks = doc_blocks((REPO / name).read_text(encoding="utf-8"))
            copilot = [b for b in blocks if "Copilot" in b]
            rows = [b for b in copilot if re.match(r"^\|\s*Copilot\s*\|", b)]
            self.assertTrue(rows, f"{name}: no Copilot row in its tool table")
            for block in copilot:
                self.assertNotIn("repo-scoped", block, f"{name}: {block}")
            for row in rows:
                if ".github/skills" in row:
                    self.assertIn(folder, row, f"{name}: the Copilot row omits {folder}: {row}")
            for block in copilot:
                if ".github/skills" in block:
                    self.assertIn(folder, block,
                                  f"{name}: says Copilot reads .github/skills, not {folder}: "
                                  f"{block}")


if __name__ == "__main__":
    unittest.main()
