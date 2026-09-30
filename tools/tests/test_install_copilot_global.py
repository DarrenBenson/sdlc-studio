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
        """AC1. MUTANTS: auto skips copilot on a global install (today's `continue`) - the
        Targets line loses copilot; copilot:global maps to nothing - copilot is skipped, and the
        explicit `--target copilot` run plans no folder; neither copilot nor agents detection
        looks for the `copilot` binary - "No installable targets resolved". The agents target
        alone would still plan ~/.agents/skills, so the folder check by itself kills only the
        last; the Targets and explicit-target checks kill the first two. The control - the same
        host without the stub - catches an auto that plans ~/.agents/skills always."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = curated_path(root, ("copilot",))
            proc = run_install(root, path, "--target", "auto", "--dry-run")
            out = proc.stdout + proc.stderr
            self.assertFalse((root / "home" / ".agents").exists(), "precondition: no ~/.agents")
            self.assertEqual(proc.returncode, 0, out)
            home = root / "home"
            planned = [ln for ln in out.splitlines() if "[dry run] would install to:" in ln]
            personal = (f"{home}/.agents/skills/sdlc-studio", f"{home}/.copilot/skills/sdlc-studio")
            self.assertTrue(any(ln.rstrip().endswith(personal) for ln in planned),
                            f"auto planned no Copilot CLI personal folder:\n{out}")
            self.assertFalse((root / "project" / ".github").exists(), out)
            targets = next(ln for ln in out.splitlines() if "Targets:" in ln)
            self.assertIn("copilot", targets.split(), f"auto did not select copilot:\n{out}")
            self.assertNotIn("skipping", out, out)
            proc = run_install(root, path, "--target", "copilot", "--dry-run")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn(f"[dry run] would install to: {home}/.agents/skills/sdlc-studio", out,
                          f"--target copilot planned no personal folder:\n{out}")
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


    def test_no_hint_when_a_folder_the_tool_reads_holds_a_copy(self) -> None:
        """BG0856 AC1. MUTANT: c00784d1's hint, which looks for a copy only in the tool's
        install target (~/.agents/skills for copilot), so a copy in ~/.copilot/skills - the other
        folder Copilot CLI reads - is refreshed by the sweep and then called not installed for,
        and following the hint makes Copilot load the skill twice. Run with the sweep on (the
        repro) and off (the copy serves whatever its version)."""
        for argv in ((), ("--no-sweep",)):
            with self.subTest(argv=argv), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                skill_copy(root / "home/.copilot/skills/sdlc-studio", "1.0.0")
                proc = run_install(root, curated_path(root, ("copilot",)), *argv)
                out = proc.stdout + proc.stderr
                self.assertEqual(proc.returncode, 0, out)
                self.assertEqual([ln for ln in hint_lines(out) if "Copilot CLI" in ln], [], out)
                self.assertFalse((root / "home/.agents").exists(), out)

    def test_no_hint_for_a_tool_served_by_a_shared_folder(self) -> None:
        """BG0856 AC2. MUTANT: a fix that special-cases ~/.copilot/skills instead of reading one
        per-tool folder table: opencode reads ~/.claude/skills, which the default install just
        wrote, and Gemini CLI reads ~/.agents/skills. The gemini control - the same stub with
        no copy - proves the fixture can reach the hint, so silence cannot pass."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("opencode",)))
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill_copy(root / "home/.agents/skills/sdlc-studio", "1.0.0")
            proc = run_install(root, curated_path(root, ("gemini",)))
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("gemini",)))
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(len(hint_lines(out)), 1, f"control: no Gemini CLI hint:\n{out}")
            self.assertIn("Gemini CLI", hint_lines(out)[0])

    def test_hint_still_names_a_tool_with_no_copy_in_any_folder_it_reads(self) -> None:
        """BG0856 AC3, the positive control. MUTANT: a fix that silences the hint whenever a
        copy exists anywhere. Copies sit in folders Copilot CLI does not read (~/.gemini/skills,
        ~/.config/opencode/skills, and the ~/.claude/skills the install writes)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill_copy(root / "home/.gemini/skills/sdlc-studio", "1.0.0")
            skill_copy(root / "home/.config/opencode/skills/sdlc-studio", "1.0.0")
            proc = run_install(root, curated_path(root, ("copilot",)))
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            hints = hint_lines(out)
            self.assertEqual(len(hints), 1, out)
            self.assertIn("Copilot CLI", hints[0])
            self.assertRegex(hints[0], r"--target claude,copilot \(", hints[0])


def hint_lines(out: str) -> list[str]:
    return [ln for ln in out.splitlines() if "Detected but not installed for" in ln]


class UndetectedHintTests(unittest.TestCase):
    """BG0852 round 2. The default install's hint names a tool only on evidence the tool is on
    this host, and never one whose skills folder already holds a copy."""

    def test_no_hint_for_a_folder_that_already_holds_a_copy(self) -> None:
        """MUTANTS: the hint ignores a copy already in the tool's folder (installed earlier, or
        refreshed by this run's sweep); a shared ~/.agents folder counts as Codex being present.
        Repro 1: after `--target copilot`, the default run named Codex, which the host lacks.
        Repro 2: a copy in ~/.gemini/skills was refreshed and then called not installed for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = curated_path(root, ("copilot",))
            first = run_install(root, path, "--target", "copilot")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            proc = run_install(root, path)
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = curated_path(root)
            skill_copy(root / "home/.gemini/skills/sdlc-studio", "1.0.0")
            proc = run_install(root, path)
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn("refreshed:", out, "precondition: the sweep refreshed the gemini copy")
            self.assertEqual(hint_lines(out), [], out)
        with tempfile.TemporaryDirectory() as d:   # ~/.agents alone is no tool
            root = Path(d)
            (root / "home/.agents").mkdir(parents=True)
            proc = run_install(root, curated_path(root), "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)

    def test_local_hint_ignores_repo_signals(self) -> None:
        """MUTANT: the hint reads is_detected, which --target auto uses, so on a --local default
        install repo and shared-folder signals - `gh`, a `.github` folder, a bare ~/.agents -
        name tools the host lacks. Since BG0856 Copilot CLI is served here either way (it reads
        the project's .claude/skills, which the install writes), so the ~/.agents signal naming
        Codex is what this fixture reaches. The control: a present tool that reads no folder the
        local install writes still earns the hint (Gemini CLI)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "project/.github").mkdir(parents=True)
            (root / "home/.agents").mkdir(parents=True)
            proc = run_install(root, curated_path(root, ("gh",)), "--local", "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("gemini",)), "--local", "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(len(hint_lines(out)), 1, out)
            self.assertIn("Gemini CLI", hint_lines(out)[0])

    def test_no_hint_for_an_explicit_target(self) -> None:
        """MUTANT: the hint prints for any target list, not only the default. A user who named
        `--target claude` chose; the control is AC2's default run on the same host."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("copilot",)), "--target", "claude",
                               "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertEqual(hint_lines(out), [], out)

    def test_one_target_per_shared_folder(self) -> None:
        """MUTANT: the hint stops de-duplicating by install folder, so Codex and Copilot CLI,
        whose targets both write ~/.agents/skills, add `codex,copilot` - two targets for one
        copy. Both tools are still named. (Cursor served here before BG0856; it reads the
        ~/.claude/skills the default install writes, so it is no longer hinted.)"""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_install(root, curated_path(root, ("codex", "copilot")), "--no-sweep")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            hints = hint_lines(out)
            self.assertEqual(len(hints), 1, out)
            self.assertIn("Codex", hints[0])
            self.assertIn("Copilot CLI", hints[0])
            self.assertRegex(hints[0], r"--target claude,codex \(", hints[0])


class CopilotDetectionTests(unittest.TestCase):

    def test_gh_and_github_detect_copilot_only_locally(self) -> None:
        """MUTANT: `gh` or a `.github` folder counts toward copilot on a global install, so a
        global auto is steered by the directory it runs from. The control: --local keeps them."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "project/.github").mkdir(parents=True)
            path = curated_path(root, ("gh",))
            rows = {}
            for mode in ("--global", "--local"):
                proc = run_install(root, path, mode, "--list-targets")
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                row = next(ln for ln in proc.stdout.splitlines()
                           if ln.split()[:1] == ["copilot"])
                rows[mode] = row.split()[-1]
            self.assertEqual(rows, {"--global": "no", "--local": "yes"})


if __name__ == "__main__":
    unittest.main()
