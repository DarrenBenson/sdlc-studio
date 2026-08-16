"""The release rehearsal: the two paths every adopter arrives on, driven end to end (CR0542).

Every other check in this repository runs against this repository. A project that has just been
created, and one being upgraded from v4, are the two situations the suite cannot occupy - and
walking them by hand once turned up three consumer-facing defects (BG0558, BG0559, BG0560) that a
6,000-test suite, twenty gate lanes and a 250-point backlog had all missed.

These tests drive `tools/rehearse-release.sh` as a subprocess, which is what the harness itself
does to the CLI. Reading the exit status directly, never through a pipe.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_rehearse_release.py
"""
from __future__ import annotations

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


def _git_status() -> str:
    """The working tree's porcelain status, through `gitutil.git` - the unconfined-raw-git
    ratchet is at zero and a fixture is not a reason to raise it."""
    # `--ignored=matching`: `.rehearsal-scratch/` is gitignored now, so a plain porcelain status
    # cannot see residue at exactly the path this criterion hardened - the ignore rule that
    # stopped the residue being COMMITTED also stopped it being VISIBLE. A round-3 seat caught it.
    return gitutil.git(["status", "--porcelain", "--ignored=matching"],
                       cwd=REPO, check=False, text=True).stdout


def _run(*args, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run the harness that lives under `cwd`, not the repository's own.

    The harness resolves its skill tree and its baseline from its OWN location, so pointing a
    clone's run at the repository's copy exercises the repository - which is exactly the mistake
    the break-it tests below exist to avoid, and it made both of them pass on an unbroken tree.
    """
    root = cwd or REPO
    return subprocess.run(["bash", str(root / "tools" / "rehearse-release.sh"), *args],
                          cwd=str(root), capture_output=True, text=True, timeout=900,
                          check=False)


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
        # COLD. This criterion passed for a whole review round only because two sibling tests
        # defined above it ran the harness first and warmed the bytecode cache, so the
        # `__pycache__` the harness itself wrote was already present in `before`. Purging here
        # makes the test hold when run alone, which is how a reviewer following this repo's own
        # mutation protocol runs it.
        for cache in (REPO / ".claude" / "skills" / "sdlc-studio" / "scripts").rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)
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


class UpgradeRehearsalTests(unittest.TestCase):
    """US0665."""

    def _baseline_lanes(self) -> set:
        return {ln.split("|", 1)[0].strip()
                for ln in BASELINE.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.startswith("#")}

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
            bl.write_text("".join(f"{n}|CR0497|x\n" for n in kept), encoding="utf-8")
            dropped = _run("upgrade", cwd=clone)
            self.assertNotEqual(0, dropped.returncode,
                                "a lane failing that the baseline does not record was tolerated")
            self.assertIn("does not record", dropped.stdout + dropped.stderr)

            bl.write_text("".join(f"{n}|CR0497|x\n" for n in sorted(lanes))
                          + "integrity|nothing|it already passes\n", encoding="utf-8")
            stale = _run("upgrade", cwd=clone)
            self.assertNotEqual(0, stale.returncode,
                                "a baselined lane that now PASSES was left in the file, so the "
                                "baseline can never empty")
            self.assertIn("now PASS", stale.stdout + stale.stderr)

    def test_every_baselined_lane_names_the_artefact_that_clears_it(self) -> None:
        # Driven through the HARNESS, not by reading the file: a round-2 seat found the first
        # version reading the baseline directly, so a harness that ignored the clearing-artefact
        # column could not fail it - the criterion was satisfiable without the CLI ever running.
        r = _run("upgrade")
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        reported = {ln.split("known gap:", 1)[1].split("->")[0].strip()
                    for ln in r.stdout.splitlines() if "known gap:" in ln}
        self.assertEqual(self._baseline_lanes(), reported,
                         "the harness does not report the baseline rows it read, so nothing "
                         "outside the file can see whether it read the artefact column")
        for ln in r.stdout.splitlines():
            if "known gap:" in ln:
                self.assertRegex(ln, r"->\s*(CR|BG|RFC|US|EP)\d{4}\s*$",
                                 f"the harness reported a gap with no clearing artefact: {ln}")
        for line in BASELINE.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            self.assertEqual(3, len(parts), f"malformed baseline row: {line!r}")
            lane, artefact, expected = parts
            self.assertTrue(lane, f"row names no lane: {line!r}")
            self.assertRegex(artefact, r"^(CR|BG|RFC|US|EP)\d{4}$",
                             f"{lane} names no artefact that will clear it - a known gap with no "
                             f"owner is indistinguishable from a gate nobody switched on")
            self.assertGreater(len(expected), 20,
                               f"{lane} does not say what the lane will report once cleared, so a "
                               f"reader cannot tell the gap is closed")


if __name__ == "__main__":
    unittest.main()
