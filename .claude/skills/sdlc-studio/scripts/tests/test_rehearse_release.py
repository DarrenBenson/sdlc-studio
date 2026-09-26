"""The release rehearsal: the paths every adopter arrives on, driven end to end (CR0542).

Every other check in this repository runs against this repository. A project that has just been
created, and one being upgraded from v4 or v5.1, are the situations the suite cannot occupy - and
walking the first two by hand once turned up three consumer-facing defects (BG0558, BG0559,
BG0560) that a 6,000-test suite, twenty gate lanes and a 250-point backlog had all missed.

These tests drive `tools/rehearse-release.sh` as a subprocess, which is what the harness itself
does to the CLI. Reading the exit status directly, never through a pipe.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py
"""
from __future__ import annotations

import ast
import os
import re
import sys
import shutil
import subprocess
import tempfile
import pytest
import unittest
from pathlib import Path

# parents[5], not [4]: [4] is `.claude`. The same off-by-one shipped in the doc-surface
# lane tests, where it made every assertion pass against an error message for a year.
REPO = Path(__file__).resolve().parents[5]

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers
import gitutil  # noqa: E402 - the tests' shared confined-git environment
HARNESS = REPO / "tools" / "rehearse-release.sh"
BASELINE = REPO / "tools" / "release-rehearsal-baseline.txt"
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
#: A `__pycache__` directory as a path component: `a/__pycache__/`, `a/__pycache__/b.pyc`.
_PYCACHE_DIR = re.compile(r"(^|/)__pycache__(/|$)")


def _git_status(root: Path = REPO) -> str:
    """The working tree's porcelain status, through `gitutil.git` - the unconfined-raw-git
    ratchet is at zero and a fixture is not a reason to raise it."""
    # `--ignored=matching`: `.rehearsal-scratch/` is gitignored now, so a plain porcelain status
    # cannot see residue at exactly the path this criterion hardened - the ignore rule that
    # stopped the residue being COMMITTED also stopped it being VISIBLE. A round-3 seat caught it.
    # A path with a `__pycache__` DIRECTORY component is left out: under `pytest -n 4` the other
    # workers write bytecode into the scripts tree while the harness runs, so it cannot be told
    # apart from the harness's own. Judged on the path component, never the substring, so a file
    # merely named like it (`tools/__pycache__notes.md`) is still seen. What the harness writes
    # into a `__pycache__` is checked where nothing else writes: on a clone, below.
    out = gitutil.git(["status", "--porcelain", "--ignored=matching"],
                      cwd=root, check=False, text=True).stdout
    return "".join(ln for ln in out.splitlines(keepends=True)
                   if not _PYCACHE_DIR.search(ln[3:].rstrip("\n")))


def _clone(d: str) -> Path:
    """The harness, its baseline and the skill tree, copied without bytecode or local state."""
    clone = Path(d) / "repo"
    (clone / "tools").mkdir(parents=True)
    shutil.copy2(HARNESS, clone / "tools" / "rehearse-release.sh")
    shutil.copy2(BASELINE, clone / "tools" / "release-rehearsal-baseline.txt")
    shutil.copytree(SKILL, clone / ".claude" / "skills" / "sdlc-studio",
                    ignore=shutil.ignore_patterns("__pycache__", ".local"))
    return clone


def _mutate(path: Path, old: str, new: str) -> str:
    """Replace `old`, which must occur exactly once, and return the original text."""
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, (f"{path.name}: the mutated line moved, so the test would pass "
                                  f"for the wrong reason: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    return text


def _terminal_statuses() -> dict:
    """`sdlc_md.TERMINAL_STATUS`, read from the source with `ast` so this subprocess-only module
    imports no production code: the one authority on which statuses are closed."""
    src = (SKILL / "scripts" / "lib" / "sdlc_md.py").read_text(encoding="utf-8")
    for node in ast.parse(src).body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "TERMINAL_STATUS":
            return ast.literal_eval(node.value)
    raise AssertionError("sdlc_md.TERMINAL_STATUS is gone, so no status can be judged open")


def _run(*args, cwd: Path | None = None, env: dict | None = None
         ) -> subprocess.CompletedProcess:
    """Run the harness that lives under `cwd`, not the repository's own.

    The harness resolves its skill tree and its baseline from its OWN location, so pointing a
    clone's run at the repository's copy exercises the repository - which is exactly the mistake
    the break-it tests below exist to avoid, and it made both of them pass on an unbroken tree.
    """
    root = cwd or REPO
    return subprocess.run(["bash", str(root / "tools" / "rehearse-release.sh"), *args],
                          cwd=str(root), capture_output=True, text=True, timeout=900,
                          check=False, env=env)


class GreenfieldRehearsalTests(unittest.TestCase):
    """US0664."""

    def test_greenfield_reaches_a_written_plan(self) -> None:
        r = _run("greenfield")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("greenfield: OK", r.stdout)

    def test_greenfield_reddens_when_the_path_is_broken(self) -> None:
        """The load-bearing test. A rehearsal that is green on a tree known to be broken proves
        nothing, and this repository has shipped that shape twice - a set comparison that could
        not fail, and an assertion whose two sides moved together.

        The break is applied to a COPY of the skill tree and the harness is pointed at it, so the
        working tree is never modified: BG0536 records a fixture that took a caller-supplied root,
        was passed `.`, and destroyed 23 mutation registrations here.
        """
        with tempfile.TemporaryDirectory() as d:
            clone = Path(d) / "repo"
            (clone / "tools").mkdir(parents=True)
            shutil.copy2(HARNESS, clone / "tools" / "rehearse-release.sh")
            shutil.copy2(BASELINE, clone / "tools" / "release-rehearsal-baseline.txt")
            shutil.copytree(REPO / ".claude" / "skills" / "sdlc-studio",
                            clone / ".claude" / "skills" / "sdlc-studio",
                            ignore=shutil.ignore_patterns("__pycache__", ".local"))
            ff = clone / ".claude" / "skills" / "sdlc-studio" / "scripts" / "file_finding.py"
            text = ff.read_text(encoding="utf-8")
            marker = ("    if not fictional_affects(repo_root, declared):\n"
                      "        return  # nothing carries these basenames anywhere: "
                      "the unit CREATES them all")
            self.assertEqual(1, text.count(marker),
                             "the greenfield repair moved - this test breaks a line that no "
                             "longer exists, so it would pass for the wrong reason")
            ff.write_text(text.replace(marker, "    if False:\n        return"), encoding="utf-8")
            sp = clone / ".claude" / "skills" / "sdlc-studio" / "scripts" / "sprint.py"
            stext = sp.read_text(encoding="utf-8")
            smark = "        if declared and len(unresolvable) == len(declared) and typos:"
            self.assertEqual(1, stext.count(smark))
            sp.write_text(stext.replace(
                smark, "        if declared and len(unresolvable) == len(declared):"),
                encoding="utf-8")

            r = _run("greenfield", cwd=clone)
            self.assertNotEqual(0, r.returncode,
                                "the rehearsal is GREEN on a tree carrying the very defect it "
                                "exists to catch, so its green means nothing")
            self.assertIn("refused a first sprint", r.stdout + r.stderr)

    @pytest.mark.serial_only
    def test_the_rehearsal_writes_nothing_into_the_working_tree(self) -> None:
        # A `__pycache__` directory is not compared here (see `_git_status`): what the harness
        # writes into one is checked on a clone by
        # `test_a_rehearsal_that_writes_into_the_repository_is_seen`.
        before = _git_status()
        r = _run("all")
        # The exit status is checked. Without it this test passes on a rehearsal that failed
        # outright and therefore wrote nothing - a green that means "it did not run".
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        after = _git_status()
        self.assertEqual(before, after,
                         "the rehearsal changed the working tree - every fixture must be built "
                         "under a temporary root")
        # The git-status check alone is satisfied by a harness that writes inside the repository
        # and then removes it on exit - the cleanup trap hides the write, and mutation found that
        # exact hole. So the work root is asserted to be a real temporary directory, never
        # derived from the repository, which is the property BG0536 is about.
        text = (REPO / "tools" / "rehearse-release.sh").read_text(encoding="utf-8")
        self.assertIn('WORK="$(mktemp -d)"', text,
                      "the work root is not an mktemp directory, so a fixture can be built "
                      "inside the repository and swept away before anyone sees it")
        self.assertNotIn('WORK="$REPO', text, "the work root is derived from the repository")
        # And nothing shaped like rehearsal residue is TRACKED. The mutant for this criterion
        # points the work root inside the repository; running it once and committing swept 41
        # fixture files onto main, in the very commit whose criterion asserts this cannot happen.
        # A git-status check cannot see that, because by then the files are committed and clean.
        tracked = gitutil.git(["ls-files", ".rehearsal-scratch"], cwd=REPO,
                              check=False, text=True).stdout
        self.assertEqual("", (tracked or "").strip(),
                         "rehearsal fixture output is tracked in the repository")

    def test_a_rehearsal_that_writes_into_the_repository_is_seen(self) -> None:
        """The comparison above leaves `__pycache__` directories out, so what it drops is checked
        here, on a clone that is its own committed git repository and that nothing else writes
        into. `all` - every path - as shipped leaves the status unchanged and creates no
        `__pycache__`. Two writes made by the LAST path (so a run of fewer paths misses them) are
        each seen: a file in a directory the repository already tracks, through the status, and a
        file in a `__pycache__` directory, through the directory check."""
        with tempfile.TemporaryDirectory() as d:
            clone = _clone(d)
            shutil.copy2(REPO / ".gitignore", clone / ".gitignore")
            for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "fixture"]):
                gitutil.git(argv, cwd=clone, check=True)
            before = _git_status(clone)
            # Without the caller's own bytecode switch, so only the harness's export can hold it.
            env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
            r = _run("all", cwd=clone, env=env)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(before, _git_status(clone))
            self.assertEqual([], sorted(clone.rglob("__pycache__")),
                             "the harness wrote a __pycache__ inside the repository")

            harness = clone / "tools" / "rehearse-release.sh"
            last = '  gate_against_baseline upgrade-v5 "$root"\n'
            kept = _mutate(harness, last, '  : > "$REPO/tools/leak.md"\n' + last)
            r = _run("all", cwd=clone, env=env)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("?? tools/leak.md", _git_status(clone),
                          "a file written into a tracked directory of the repository was not seen")
            (clone / "tools" / "leak.md").unlink()
            harness.write_text(kept, encoding="utf-8")

            _mutate(harness, last, '  mkdir -p "$SCRIPTS/__pycache__" && '
                                   ': > "$SCRIPTS/__pycache__/leak.pyc"\n' + last)
            r = _run("all", cwd=clone, env=env)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertNotEqual([], sorted(clone.rglob("__pycache__")),
                                "a file written into a __pycache__ in the repository was not seen")

    def test_the_status_filter_drops_only_a_pycache_directory(self) -> None:
        """The filter judges the path component: bytecode directories go, a file merely named
        like one stays."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tools").mkdir()
            (root / "tools" / "keep.txt").write_text("x", encoding="utf-8")
            (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
            for argv in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "fixture"]):
                gitutil.git(argv, cwd=root, check=True)
            (root / "tools" / "__pycache__").mkdir()
            (root / "tools" / "__pycache__" / "a.pyc").write_bytes(b"")
            (root / "tools" / "__pycache__notes.md").write_text("x", encoding="utf-8")
            status = _git_status(root)
            self.assertIn("tools/__pycache__notes.md", status)
            self.assertNotIn("tools/__pycache__/", status)


class UpgradeRehearsalTests(unittest.TestCase):
    """US0665."""

    @staticmethod
    def _baseline_rows() -> list:
        """`[path, lane, clearing artefact, what the lane says once cleared]` per row."""
        return [[p.strip() for p in ln.split("|")]
                for ln in BASELINE.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.startswith("#")]

    def _baseline_lanes(self, path: str = "upgrade") -> set:
        return {row[1] for row in self._baseline_rows() if row[0] == path}

    def test_upgrade_migrates_then_gates(self) -> None:
        r = _run("upgrade")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("upgrade: OK", r.stdout)
        # ORDER, not merely presence. A round-2 seat swapped the two steps and this test stayed
        # green: the baselined lane set is identical either way, so the criterion's central claim
        # - migrate THEN gate - was unmeasured. The harness now reports each step as it takes it.
        order = [ln.split("order:", 1)[1].strip()
                 for ln in r.stdout.splitlines() if "order:" in ln]
        self.assertEqual(["migrate", "gate"], order,
                         f"the upgrade did not run migrate before gate: {order}")
        # And the migrate's OUTCOME. The previous form asserted a string in the HARNESS SOURCE and
        # claimed the fixture "comes back at 3" - migrate does not bump schema_version at all. A
        # seat proved the whole path unmeasured by deleting `--apply`: every test stayed green,
        # because the failing lane set is identical on a migrated and an unmigrated fixture. The
        # harness now checks what migrate really writes, and reports it.
        self.assertIn("migrated: .version written", r.stdout,
                      "the harness does not assert the migration happened, so the rehearsal "
                      "passes on a fixture that was never migrated")
        self.assertIn("known gap:", r.stdout)

    def test_the_upgrade_baseline_reddens_in_both_directions(self) -> None:
        """A baseline that only ever tolerates is one that never empties.

        Both directions on a COPY: a lane removed from the baseline must be reported as a new
        failure, and a lane added that is already passing must be reported as removable.
        """
        lanes = self._baseline_lanes()
        self.assertTrue(lanes, "the baseline records no lanes, so neither direction is testable")
        with tempfile.TemporaryDirectory() as d:
            clone = Path(d) / "repo"
            (clone / "tools").mkdir(parents=True)
            shutil.copy2(HARNESS, clone / "tools" / "rehearse-release.sh")
            shutil.copytree(REPO / ".claude" / "skills" / "sdlc-studio",
                            clone / ".claude" / "skills" / "sdlc-studio",
                            ignore=shutil.ignore_patterns("__pycache__", ".local"))
            bl = clone / "tools" / "release-rehearsal-baseline.txt"

            kept = sorted(lanes)[1:]
            bl.write_text("".join(f"upgrade|{n}|BG0001|x\n" for n in kept), encoding="utf-8")
            dropped = _run("upgrade", cwd=clone)
            self.assertNotEqual(0, dropped.returncode,
                                "a lane failing that the baseline does not record was tolerated")
            self.assertIn("does not record", dropped.stdout + dropped.stderr)

            bl.write_text("".join(f"upgrade|{n}|BG0001|x\n" for n in sorted(lanes))
                          + "upgrade|integrity|nothing|it already passes\n", encoding="utf-8")
            stale = _run("upgrade", cwd=clone)
            self.assertNotEqual(0, stale.returncode,
                                "a baselined lane that now PASSES was left in the file, so the "
                                "baseline can never empty")
            self.assertIn("now PASS", stale.stdout + stale.stderr)

    def test_every_baselined_lane_names_the_artefact_that_clears_it(self) -> None:
        # Driven through the HARNESS, not by reading the file: a round-2 seat found the first
        # version reading the baseline directly, so a harness that ignored the clearing-artefact
        # column could not fail it - the criterion was satisfiable without the CLI ever running.
        # Every path the baseline names is run, and each reported owner must be OPEN (US0938): a
        # gap whose owner is closed is tolerated on behalf of work nobody will do.
        terminal = _terminal_statuses()
        kinds = {"CR": "cr", "BG": "bug", "RFC": "rfc", "US": "story", "EP": "epic"}
        for path in sorted({row[0] for row in self._baseline_rows()}):
            r = _run(path)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            gaps = [ln.split("known gap:", 1)[1] for ln in r.stdout.splitlines()
                    if "known gap:" in ln]
            self.assertEqual({(row[1], row[2]) for row in self._baseline_rows()
                              if row[0] == path},
                             {tuple(p.strip() for p in g.split("->", 1)) for g in gaps},
                             "the harness does not report the baseline rows it read, lane and "
                             "owner, so nothing outside the file can see whether it read the "
                             "artefact column")
            for gap in gaps:
                m = re.search(r"->\s*(CR|BG|RFC|US|EP)(\d{4})\s*$", gap)
                self.assertIsNotNone(m, f"the harness reported a gap with no clearing artefact: "
                                        f"{gap}")
                owner = m.group(1) + m.group(2)
                files = sorted((REPO / "sdlc-studio").glob(f"*/{owner}-*.md"))
                self.assertEqual(1, len(files), f"{path}: {owner} names no single artefact")
                status = re.search(r"^> \*\*Status:\*\* *(.+?) *$",
                                   files[0].read_text(encoding="utf-8"), re.M)
                self.assertIsNotNone(status, f"{owner} carries no Status")
                self.assertNotIn(status.group(1), terminal[kinds[m.group(1)]],
                                 f"{path}: the gap's owner {owner} is {status.group(1)}, so the "
                                 f"tolerated gap has no open owner")
        for line in BASELINE.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            self.assertEqual(4, len(parts), f"malformed baseline row: {line!r}")
            path, lane, artefact, expected = parts
            self.assertIn(path, ("upgrade", "upgrade-v5"), f"row names no upgrade path: {line!r}")
            self.assertTrue(lane, f"row names no lane: {line!r}")
            self.assertRegex(artefact, r"^(CR|BG|RFC|US|EP)\d{4}$",
                             f"{lane} names no artefact that will clear it - a known gap with no "
                             f"owner is indistinguishable from a gate nobody switched on")
            self.assertGreater(len(expected), 20,
                               f"{lane} does not say what the lane will report once cleared, so a "
                               f"reader cannot tell the gap is closed")

    def test_every_baselined_gap_names_an_open_owner(self) -> None:
        """US0938 AC3. The open-owner check extends US0665's test above rather than adding another
        run of the harness; this name is the criterion's selector for it."""
        self.test_every_baselined_lane_names_the_artefact_that_clears_it()

    def test_the_v5_upgrade_strips_retired_tags(self) -> None:
        """US0938 AC1: a v5.1 workspace migrates to no retired DoD tag, migrate reports the
        AGENTS.md line, and the gate matches the baseline. Red on a harness that drops `--apply`
        and on a migrate that leaves the tags or does not name the AGENTS.md line, each applied
        to a clone."""
        r = _run("upgrade-v5")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("upgrade-v5: OK", r.stdout)
        self.assertRegex(r.stdout, r"migrated: the DoD carries no retired tag, AGENTS\.md:\d+ "
                                   r"reported")
        order = [ln.split("order:", 1)[1].strip() for ln in r.stdout.splitlines()
                 if "order:" in ln]
        self.assertEqual(["migrate", "gate"], order)
        with tempfile.TemporaryDirectory() as d:
            clone = _clone(d)
            harness = clone / "tools" / "rehearse-release.sh"
            kept = _mutate(harness, 'report="$($PY "$SCRIPTS/migrate.py" --root "$root" --apply '
                                    '2>&1)"',
                           'report="$($PY "$SCRIPTS/migrate.py" --root "$root" 2>&1)"')
            r = _run("upgrade-v5", cwd=clone)
            self.assertNotEqual(0, r.returncode, "the rehearsal passed without migrating")
            self.assertIn("still carries a retired [check:] tag", r.stdout + r.stderr)
            harness.write_text(kept, encoding="utf-8")

            migrate = clone / ".claude" / "skills" / "sdlc-studio" / "scripts" / "migrate.py"
            original = _mutate(migrate, "    retired = sdlc_md.RETIRED_CHECK_IDS\n",
                               "    retired = {}\n")
            r = _run("upgrade-v5", cwd=clone)
            self.assertNotEqual(0, r.returncode, "the rehearsal passed on a migrate that leaves "
                                                 "the retired tags")
            self.assertIn("still carries a retired [check:] tag", r.stdout + r.stderr)
            migrate.write_text(original, encoding="utf-8")

            _mutate(migrate, '    for name in ("AGENTS.md", "CLAUDE.md", ',
                    '    for name in ("CLAUDE.md", ')
            r = _run("upgrade-v5", cwd=clone)
            self.assertNotEqual(0, r.returncode, "the rehearsal passed on a migrate whose report "
                                                 "does not name the AGENTS.md line")
            self.assertIn("does not name AGENTS.md", r.stdout + r.stderr)

    def test_all_runs_the_v5_path(self) -> None:
        """US0938 AC2: `all` is what the release-rehearsal lane runs."""
        r = _run("all")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        done = [m.group(1) for m in re.finditer(r"^(greenfield|upgrade|upgrade-v5): OK", r.stdout,
                                                re.M)]
        self.assertEqual(["greenfield", "upgrade", "upgrade-v5"], done)


if __name__ == "__main__":
    unittest.main()
