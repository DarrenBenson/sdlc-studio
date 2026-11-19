"""Regression test for CR0205: install.sh must not destroy a working install when the
copy fails. The old `rm -rf $dest; cp -r ...` left the user with nothing (or a half-copy)
if cp failed between the two. The fix stages into a temp sibling and swaps, so a failed
copy leaves the previous install byte-for-byte intact.

BG1546 (NothingInstalledOutcome): a run that wrote no target says so and exits non-zero, and a
run that wrote some names only those in its banner, its next steps and the list the sweep trusts.

BG1632 (InstallPs1ExistingFolderTests): install.ps1 removed an existing folder named sdlc-studio
that is not the skill and installed in its place, where install.sh skips it.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
INSTALL_PS1 = REPO / "install.ps1"
PWSH = shutil.which("pwsh")

# Source the installer, point install_to at a source, but make `cp` fail. The previous
# install at $dest must survive unchanged, and install_to must report failure (non-zero).
DRIVER = r"""
source "__INSTALL_SH__"
set +e                                  # install.sh sets -e; relax it so we can inspect
DRY_RUN=false
SKILL_NAME="sdlc-studio"

ship_changelog() { :; }                 # no-op the changelog copy
cp() { command false; }                 # every cp fails

install_to "$PARENT" "$SRC"
echo "INSTALL_RC=$?"
cat "$PARENT/sdlc-studio/marker.txt" 2>/dev/null || echo "MARKER_GONE"
"""


class InstallAtomicSwap(unittest.TestCase):
    def test_swap_install_dest_tracks_the_arg_not_caller_scope(self) -> None:
        # Critic finding: dest="$parent/..." on the same `local` line as parent="$1" resolved
        # via caller dynamic scope (rm -rf on the install path riding on coincidence).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src" / "sdlc-studio"; src.mkdir(parents=True)
            (src / "x.txt").write_text("x\n")
            target = root / "target"; target.mkdir()
            driver = (
                'source "%s"\n' % INSTALL_SH
                + 'set +e\nDRY_RUN=false\nSKILL_NAME="sdlc-studio"\n'
                + 'ship_changelog() { :; }\n'
                + 'parent="/SHOULD_NOT_BE_USED"\n'   # a caller-scope decoy
                + 'swap_install "%s" "%s"\n' % (target, src)
                + 'echo "RC=$?"\n'
                + '[ -d "%s/sdlc-studio" ] && echo DEST_OK || echo DEST_WRONG\n' % target
            )
            proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                                  env={"PATH": "/usr/bin:/bin"}, timeout=30)
            self.assertIn("DEST_OK", proc.stdout, msg=proc.stdout + proc.stderr)

    def test_failed_copy_leaves_previous_install_intact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src" / "sdlc-studio"
            src.mkdir(parents=True)
            (src / "new.txt").write_text("new\n")
            parent = root / "target"
            (parent / "sdlc-studio").mkdir(parents=True)
            (parent / "sdlc-studio" / "marker.txt").write_text("PREVIOUS-INSTALL\n")
            # A previous INSTALL, so the copy is attempted: a folder holding no sdlc-studio
            # SKILL.md is the user's and is skipped before any copy (US0976).
            (parent / "sdlc-studio" / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n")
            script = DRIVER.replace("__INSTALL_SH__", str(INSTALL_SH))
            proc = subprocess.run(
                ["bash", "-c", script],
                env={"SRC": str(src), "PARENT": str(parent), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=30,
            )
            self.assertNotIn("not touching it", proc.stdout + proc.stderr,
                             "the fixture never reached the copy, so this proves nothing")
            self.assertIn("PREVIOUS-INSTALL", proc.stdout,
                          msg="the previous install was destroyed by a failed copy:\n"
                          + proc.stdout + proc.stderr)
            self.assertNotIn("INSTALL_RC=0", proc.stdout,
                             msg="install_to reported success despite a failed copy")


class ResolveTargetsAuto(unittest.TestCase):
    """CR0208: a GLOBAL `--target auto` must never write `.github/skills` into the current
    directory, an unrelated side effect of a per-user install. CR0208 kept that by excluding
    copilot from a global auto; BG0852 gives copilot a personal folder (the one Copilot CLI
    reads) and lets auto select it, so the intent is now pinned on the filesystem instead."""

    def _auto(self, mode: str) -> str:
        # source install.sh, pretend gh (copilot) and claude are both detected, then resolve
        driver = (
            'source "%s"\n' % INSTALL_SH
            + 'set +e\n'
            + 'is_detected() { case "$1" in copilot|claude) return 0;; *) return 1;; esac; }\n'
            + 'INSTALL_MODE="%s"\n' % mode
            + 'resolve_targets auto\n'
        )
        proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}, timeout=30)
        return proc.stdout.strip()

    def test_global_auto_never_writes_github_skills_in_cwd(self) -> None:
        """AC5 (BG0852). MUTANTS: copilot:global points at `.github/skills` in the current
        directory, or the old repo-scoped redirect comes back, so a global auto that selects
        copilot writes there (the side effect CR0208 removed); copilot's global target is not
        the personal folder. Both `gh` and `copilot` are on PATH and the cwd holds `.github`,
        so every old and new copilot detection fires."""
        from test_install_copilot_global import curated_path, installer_dir, run_install
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "project" / ".github").mkdir(parents=True)
            proc = run_install(root, curated_path(root, ("gh", "copilot")), "--target", "auto")
            out = proc.stdout + proc.stderr
            self.assertEqual(proc.returncode, 0, out)
            self.assertIn("copilot", next(ln for ln in out.splitlines() if "Targets:" in ln),
                          f"precondition: auto did not select copilot:\n{out}")
            self.assertFalse((root / "project" / ".github" / "skills").exists(),
                             f"a global install wrote .github/skills into the cwd:\n{out}")
            self.assertTrue((root / "home" / ".agents/skills/sdlc-studio/SKILL.md").is_file(),
                            f"copilot's personal folder was not written:\n{out}")
        self.assertEqual(installer_dir("copilot", "global"), "/HOME/.agents/skills")

    def test_local_auto_keeps_copilot(self) -> None:
        out = self._auto("local")
        self.assertIn("copilot", out)


class DowngradeGuard(unittest.TestCase):
    """BG0100: install/sweep must refuse to overwrite a copy that is NEWER than the version being
    installed, so an install from an older published release cannot silently revert newer local
    work (a dev checkout ahead of the frozen remote)."""

    def _dest(self, root: Path, version: str) -> Path:
        d = root / "sdlc-studio"
        (d / "templates").mkdir(parents=True)
        (d / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
        (d / "templates" / "version.yaml").write_text(
            'skill_version: "%s"\n' % version, encoding="utf-8")
        return d

    def _would_downgrade(self, dest: Path, incoming: str, allow: str = "false") -> int:
        driver = (
            'source "%s"\n' % INSTALL_SH
            + 'set +e\nwarn() { echo "WARN: $*" >&2; }\n'
            + 'ALLOW_DOWNGRADE=%s\n' % allow
            + 'would_downgrade "%s" "%s"; echo "RC=$?"\n' % (dest, incoming)
        )
        proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}, timeout=30)
        return proc.stdout + proc.stderr

    def test_refuses_downgrade_of_newer_copy(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            out = self._would_downgrade(dest, "3.6.0")
            self.assertIn("RC=0", out)          # 0 = would downgrade -> caller skips
            self.assertIn("refusing to downgrade", out)

    def test_allows_downgrade_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            self.assertIn("RC=1", self._would_downgrade(dest, "3.6.0", allow="true"))

    def test_allows_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "3.6.0")
            self.assertIn("RC=1", self._would_downgrade(dest, "4.0.0-rc.1"))

    def test_rc_to_ga_is_an_upgrade_not_a_downgrade(self) -> None:
        # BG0106: semver pre-release precedence - 4.0.0-rc.1 is OLDER than 4.0.0,
        # so the GA install over an rc copy must proceed (RC=1, no refusal).
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            out = self._would_downgrade(dest, "4.0.0")
            self.assertIn("RC=1", out)
            self.assertNotIn("refusing", out)

    def test_ga_to_rc_is_a_downgrade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0")
            self.assertIn("RC=0", self._would_downgrade(dest, "4.0.0-rc.1"))

    def test_rc_ordering_within_prereleases(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            self.assertIn("RC=1", self._would_downgrade(dest, "4.0.0-rc.2"))  # upgrade
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.2")
            self.assertIn("RC=0", self._would_downgrade(dest, "4.0.0-rc.1"))  # downgrade

    def test_branch_name_is_not_a_false_downgrade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0")
            self.assertIn("RC=1", self._would_downgrade(dest, "main"))  # non-semver -> not older


class LocalSourceInstall(unittest.TestCase):
    """CR0214: --from DIR installs the LOCAL tree (the dev-testing path) instead of
    downloading the published release; a non-skill dir refuses before any write."""

    def _run(self, home: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(INSTALL_SH), *args],
                              env={"PATH": "/usr/bin:/bin", "HOME": str(home)},
                              capture_output=True, text=True, timeout=60)

    def _src(self, root: Path, version: str = "9.9.9") -> Path:
        src = root / "src" / "sdlc-studio"
        (src / "templates").mkdir(parents=True)
        (src / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
        (src / "templates" / "version.yaml").write_text(
            'skill_version: "%s"\n' % version, encoding="utf-8")
        (src / "marker.txt").write_text("LOCAL-TREE\n", encoding="utf-8")
        return src

    def test_from_installs_the_local_tree_without_downloading(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            src = self._src(Path(d))
            proc = self._run(home, "--from", str(src), "--no-sweep")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            dest = home / ".claude" / "skills" / "sdlc-studio"
            self.assertEqual((dest / "marker.txt").read_text(encoding="utf-8"), "LOCAL-TREE\n")
            self.assertNotIn("Downloading", proc.stdout)  # no network path taken

    def test_default_sweep_never_touches_the_from_source(self) -> None:
        # Critic repro: the DOCUMENTED invocation - --from <source> with the sweep ON,
        # where a sweep target resolves to the source itself - must skip the source,
        # never rm-and-replace the git-tracked tree it is installing from.
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            # the source sits exactly where the local-scope claude target resolves
            proj = Path(d) / "proj" / ".claude" / "skills"
            src = proj / "sdlc-studio"
            (src / "templates").mkdir(parents=True)
            (src / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
            (src / "templates" / "version.yaml").write_text(
                'skill_version: "9.9.9"\n', encoding="utf-8")
            (src / "marker.txt").write_text("SOURCE-TREE\n", encoding="utf-8")
            proc = subprocess.run(
                ["bash", str(INSTALL_SH), "--from", str(src)],  # sweep ON (default)
                env={"PATH": "/usr/bin:/bin", "HOME": str(home)},
                cwd=str(Path(d) / "proj"),   # cwd makes .claude/skills resolve to the source
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            # the source tree is byte-identical: marker intact, no injected CHANGELOG
            self.assertEqual((src / "marker.txt").read_text(encoding="utf-8"), "SOURCE-TREE\n")
            self.assertFalse((src / "CHANGELOG.md").exists())
            self.assertIn("it IS the install source", proc.stdout)

    def test_dry_run_still_validates_from(self) -> None:
        # Critic minor: --dry-run --from /nonexistent must refuse, not report success.
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            proc = subprocess.run(
                ["bash", str(INSTALL_SH), "--dry-run", "--from", str(Path(d) / "junk")],
                env={"PATH": "/usr/bin:/bin", "HOME": str(home)},
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)

    def test_from_refuses_a_non_skill_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            junk = Path(d) / "junk"; junk.mkdir()
            proc = self._run(home, "--from", str(junk), "--no-sweep")
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertFalse((home / ".claude" / "skills" / "sdlc-studio").exists())

    def test_from_still_respects_the_downgrade_guard(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"
            dest = home / ".claude" / "skills" / "sdlc-studio"
            (dest / "templates").mkdir(parents=True)
            (dest / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
            (dest / "templates" / "version.yaml").write_text(
                'skill_version: "9.9.9"\n', encoding="utf-8")
            src = self._src(Path(d), version="1.0.0")   # older local tree
            proc = self._run(home, "--from", str(src), "--no-sweep")
            self.assertIn("refusing to downgrade", proc.stdout + proc.stderr)
            self.assertEqual((dest / "templates" / "version.yaml").read_text(encoding="utf-8"),
                             'skill_version: "9.9.9"\n')  # newer install untouched


class NothingInstalledOutcome(unittest.TestCase):
    """BG1546: install_to skipped a foreign folder and refused a downgrade with `return 0`, and
    main appended every requested target to the installed list, so a run that wrote nothing
    printed 'SDLC Studio installed for: claude' and exited 0. Each run installs this
    repository's own skill folder with `--from`, into a scratch HOME, stderr merged into stdout
    so the closing line is the one a reader sees last."""

    SKILL = REPO / ".claude" / "skills" / "sdlc-studio"

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = {**os.environ, "HOME": str(self.home)}

    def _dest(self, tool: str) -> Path:
        return self.home / f".{tool}" / "skills" / "sdlc-studio"

    def _foreign(self, tool: str) -> Path:
        dest = self._dest(tool)
        dest.mkdir(parents=True)
        (dest / "notes.txt").write_text("mine\n", encoding="utf-8")
        return dest

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(INSTALL_SH), "--from", str(self.SKILL), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              env=self.env, cwd=str(self.root), timeout=120)

    @staticmethod
    def _closing(out: str) -> str:
        lines = [ln for ln in out.splitlines() if ln.strip()]
        return lines[-1] if lines else ""

    def test_a_skipped_foreign_folder_ends_with_no_banner_and_a_failing_exit(self) -> None:
        """AC1. MUTANT: HEAD, whose banner names claude over the skipped folder and exits 0.
        MUTANT: a closing line that says nothing was installed without saying why."""
        dest = self._foreign("claude")
        proc = self._run("--no-sweep", "--target", "claude")
        self.assertIn("not touching it", proc.stdout, "the fixture never reached the skip")
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertNotIn("SDLC Studio installed for", proc.stdout, proc.stdout)
        self.assertNotIn("Next steps", proc.stdout, proc.stdout)
        closing = self._closing(proc.stdout)
        self.assertIn("Nothing was installed", closing, proc.stdout)
        self.assertIn("no sdlc-studio SKILL.md", closing, proc.stdout)
        self.assertEqual(["notes.txt"], sorted(p.name for p in dest.iterdir()))
        self.assertEqual("mine\n", (dest / "notes.txt").read_text(encoding="utf-8"))

    def test_a_refused_downgrade_ends_with_no_banner_and_a_failing_exit(self) -> None:
        """AC2. MUTANT: HEAD's `return 0   # refused`, read by main as a write."""
        dest = self._dest("claude")
        (dest / "templates").mkdir(parents=True)
        (dest / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
        stamp = dest / "templates" / "version.yaml"
        stamp.write_text('skill_version: "99.0.0"\n', encoding="utf-8")
        proc = self._run("--no-sweep", "--target", "claude")
        self.assertIn("refusing to downgrade", proc.stdout, proc.stdout)
        self.assertNotEqual(0, proc.returncode, proc.stdout)
        self.assertNotIn("SDLC Studio installed for", proc.stdout, proc.stdout)
        closing = self._closing(proc.stdout)
        self.assertIn("Nothing was installed", closing, proc.stdout)
        self.assertIn("downgrade refused", closing, proc.stdout)
        self.assertEqual('skill_version: "99.0.0"\n', stamp.read_text(encoding="utf-8"))

    def test_a_partly_skipped_run_names_only_what_it_wrote(self) -> None:
        """AC3. MUTANT: HEAD's unconditional `installed_dests` append, which hands the skipped
        gemini folder to the sweep as written. MUTANT: a banner or next steps built from every
        requested target. MUTANT: a skipped target left unnamed after the banner."""
        foreign = self._foreign("gemini")
        proc = self._run("--no-sweep", "--target", "claude,gemini")
        out = proc.stdout
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("SDLC Studio installed for: claude\n", out, out)
        self.assertNotIn("Gemini CLI: run /skills", out, "the skipped gemini got next steps")
        self.assertIn("Claude Code: run /sdlc-studio", out, out)
        tail = out[out.index("SDLC Studio installed for"):]
        self.assertTrue(any("gemini" in ln and "no sdlc-studio SKILL.md" in ln
                            for ln in tail.splitlines()),
                        f"the skipped gemini target is not named with its reason:\n{out}")
        self.assertTrue((self._dest("claude") / "SKILL.md").is_file(), out)
        self.assertEqual(["notes.txt"], sorted(p.name for p in foreign.iterdir()))

        # The list handed to the sweep, read off sweep_stale's own argument.
        driver = (f'source "{INSTALL_SH}" --from "{self.SKILL}" --target claude,gemini\n'
                  'sweep_stale() { echo "SWEEP_LIST=[$2]"; }\nmain\n')
        proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                              env=self.env, cwd=str(self.root), timeout=120)
        listed = [ln for ln in proc.stdout.splitlines() if ln.startswith("SWEEP_LIST=")]
        self.assertEqual(1, len(listed), proc.stdout + proc.stderr)
        claude = os.path.realpath(self._dest("claude").parent) + "/sdlc-studio"
        gemini = os.path.realpath(foreign.parent) + "/sdlc-studio"
        self.assertIn(claude, listed[0], listed[0])
        self.assertNotIn(gemini, listed[0], f"the sweep trusts the skipped gemini: {listed[0]}")

    def test_a_clean_install_still_prints_the_banner_and_exits_zero(self) -> None:
        """AC4, the control. MUTANT: a check that reports every install as nothing installed."""
        proc = self._run("--no-sweep", "--target", "claude")
        self.assertEqual(0, proc.returncode, proc.stdout)
        self.assertIn("SDLC Studio installed for: claude", proc.stdout, proc.stdout)
        self.assertNotIn("Nothing was installed", proc.stdout, proc.stdout)
        self.assertTrue((self._dest("claude") / "SKILL.md").is_file(), proc.stdout)


class InstallPs1ExistingFolderTests(unittest.TestCase):
    """BG1632. The install loop is read in every case; where pwsh is installed (the CI runners)
    a dry run over a foreign folder also runs, which needs no download."""

    def test_ps1_install_skips_an_existing_folder_that_is_not_the_skill(self) -> None:
        """AC1. MUTANT: HEAD's `if (Test-Path $dest) { ... Remove-Item ... }`, which replaces any
        folder of that name. MUTANT: the guard after the removal, or after the dry-run branch, so
        a dry run says it would install over the folder. MUTANT: a guard that warns and still
        removes. MUTANT: a skipped target still named in the banner, or a run that wrote
        nothing not refused (the BG1546 shape install.sh no longer has)."""
        src = INSTALL_PS1.read_text(encoding="utf-8")
        start = src.index("$installedDests = @()")
        loop = re.search(r"\n        foreach \(\$t in \$resolved\.Keys\) \{\n(.*?)\n        \}\n",
                         src[start:], re.S)
        self.assertIsNotNone(loop, "install.ps1's install loop moved")
        body = loop.group(1)
        removals = [m.start() for m in re.finditer(r"Remove-Item -Path \$dest\b", body)]
        self.assertEqual(1, len(removals), "the install loop should remove $dest in one place")
        guard = re.search(r"if \(\(Test-Path \$dest\) -and -not \(Test-SkillCopy \$dest\)[^\n]*\) "
                          r"\{(.*?)\n\s*\}", body, re.S)
        self.assertIsNotNone(guard, "the replacement is not guarded by the SKILL.md check")
        self.assertLess(guard.start(), removals[0], "the guard comes after the removal")
        self.assertLess(guard.start(), body.index("if ($DryRun)"),
                        "a dry run reaches the would-install line before the guard")
        self.assertIn("continue", guard.group(1), "a foreign folder is not skipped")
        self.assertIn("not touching it", guard.group(1), "the skip is not reported")
        self.assertNotIn("Remove-Item", guard.group(1))
        after = src[start + loop.end():]
        self.assertIn('throw "Nothing was installed', after, "a run that wrote nothing exits 0")
        self.assertIn('Write-Ok "SDLC Studio installed for: $($installedTargets -join', after,
                      "the banner does not name only the written targets")
        if PWSH:
            self._executed()

    def _executed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            project, home = Path(d) / "project", Path(d) / "home"
            home.mkdir()
            dest = project / ".claude" / "skills" / "sdlc-studio"
            dest.mkdir(parents=True)
            (dest / "notes.txt").write_text("mine\n", encoding="utf-8")
            env = {**os.environ, "HOME": str(home), "NO_COLOR": "1",
                   "POWERSHELL_TELEMETRY_OPTOUT": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                   "DOTNET_NOLOGO": "1"}
            proc = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File",
                                   str(INSTALL_PS1), "-Target", "claude", "-Local", "-NoSweep",
                                   "-DryRun", "-Version", "v9.9.9"],
                                  capture_output=True, text=True, env=env, cwd=str(project),
                                  timeout=180)
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            self.assertIn("not touching it", out, out)
            self.assertNotIn("would install to", out, out)
            self.assertEqual(["notes.txt"], sorted(p.name for p in dest.iterdir()), out)


if __name__ == "__main__":
    unittest.main()
