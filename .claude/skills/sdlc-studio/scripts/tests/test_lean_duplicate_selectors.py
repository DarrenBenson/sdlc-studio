"""US0897: a shared Verify selector is an advisory note within one artefact, never a refusal.

The pre-commit `verify-ratchet` lane (`verify_ac.py lint --ratchet --bugs`) refused any
duplicate-verifier group across the whole corpus that `.verify-lint-baseline.json` did not
record. It refused a bug that shared its fixing story's selector, which is correct sharing: a
bug's fix is the story's criteria. The lane, the `--ratchet`/`--stamp` flags, the npm script and
the baseline are deleted. A duplicate is judged within ONE artefact only, reported by
`verify_ac.py lint` and noted in the review brief, and never fails anything.

AC1 reads this repository's hooks, package.json and tree, because its criterion is about this
repository. AC2 and AC3 run the shipped CLIs in throwaway workspaces. AC4 reads the live
artefacts.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import workspace  # noqa: E402
import verify_ac  # noqa: E402

REPO = workspace.REPO
VERIFY_AC = SCRIPTS / "verify_ac.py"
CRITIC = SCRIPTS / "critic.py"
BASELINE = "sdlc-studio/.verify-lint-baseline.json"
ARTEFACT_DIRS = ("stories", "bugs", "change-requests")
#: The phrase the brief's advisory line carries; the criteria text never contains it.
ADVISORY = "share one Verify selector"


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _unit(uid: str, status: str, verifiers: list[str]) -> str:
    acs = "".join(f"\n### AC{i}: behaviour {i}\n\n- **Given** a thing\n- **When** it runs\n"
                  f"- **Then** it works\n- **Verify:** {v}\n"
                  for i, v in enumerate(verifiers, 1))
    return (f"# {uid}: a unit\n\n> **Status:** {status}\n> **Points:** 2\n"
            f"> **Affects:** src/thing.py\n\n## Acceptance Criteria\n{acs}")


def _code(hook: str) -> str:
    """The hook's executable lines: a comment may say what a lane USED to do."""
    text = (REPO / ".githooks" / hook).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _npm_lint_commands() -> list[str]:
    """Every command `npm run lint` reaches, following its `npm run <name>` chain."""
    scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
    seen: list[str] = []
    todo = ["lint"]
    while todo:
        body = scripts[todo.pop()]
        seen.append(body)
        todo.extend(n for n in re.findall(r"npm run ([\w:-]+)", body) if n in scripts)
    return seen


def _lint(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(VERIFY_AC), "lint", "--root", str(root),
                           *extra], capture_output=True, text=True, timeout=300, check=False)


#: A bug and the story that fixed it, sharing the story's selector; and one story two of whose
#: criteria share a selector. Every status is still being authored, so the lint's authoring-time
#: refusals are live and would fire on anything they judged.
FIX = "pytest tests/test_fix.py::FixTests::test_the_fix"
PAIR = "pytest tests/test_pair.py::PairTests::test_both"
#: One selector two different STORIES share: still not a group (review of US0897, LC-002).
ACROSS = "pytest tests/test_across.py::AcrossTests::test_shared"


def _corpus(root: Path) -> None:
    _write(root, "src/thing.py", "VALUE = 1\n")
    _write(root, "sdlc-studio/stories/US0001-the-fix.md",
           _unit("US0001", "In Progress", [FIX, "pytest tests/test_fix.py::FixTests::test_b"]))
    _write(root, "sdlc-studio/bugs/BG0001-the-bug.md", _unit("BG0001", "Open", [FIX]))
    _write(root, "sdlc-studio/stories/US0002-a-pair.md",
           _unit("US0002", "Draft", [PAIR, PAIR, "pytest tests/test_pair.py::PairTests::test_c"]))
    # Two different stories sharing one selector: judged per artefact, so neither is a group.
    _write(root, "sdlc-studio/stories/US0003-one-side.md", _unit("US0003", "Draft", [ACROSS]))
    _write(root, "sdlc-studio/stories/US0004-other-side.md", _unit("US0004", "Draft", [ACROSS]))


class DuplicateSelectorTests(unittest.TestCase):

    def test_no_commit_or_lint_run_is_refused_on_a_shared_selector(self) -> None:
        """AC1. MUTANTS: put the `verify-ratchet` lane back into the pre-commit hook; put
        `lint:verify-ratchet` back into the npm lint chain; restore the `--ratchet` flag; restore
        the baseline, or list it in `test_baselines_only_shrink.BASELINES` again; make a shared
        selector count towards the lint's exit code."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        # 1. No hook runs the lint, under any lane key.
        for hook in ("pre-commit", "commit-msg"):
            with self.subTest(hook=hook):
                code = _code(hook)
                self.assertNotIn("verify-ratchet", code)
                self.assertNotRegex(code, r"verify_ac\.py\"?\s+lint\b")
        # 2. `npm run lint` reaches no command that runs it, and the script is gone.
        for command in _npm_lint_commands():
            self.assertNotIn("verify-ratchet", command)
            self.assertNotIn("--ratchet", command)
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("lint:verify-ratchet", scripts)
        # 3. The flag is gone from the shipped CLI: argparse refuses it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corpus(root)
            refused = _lint(root, "--ratchet", "--bugs")
            # 4. The positive control, by execution: the same corpus, the command a person types.
            kept = _lint(root, "--bugs")
        self.assertEqual(2, refused.returncode, refused.stdout + refused.stderr)
        self.assertIn("unrecognized arguments: --ratchet", refused.stderr)
        self.assertEqual(0, kept.returncode, kept.stdout + kept.stderr)
        self.assertIn("duplicate verifier", kept.stdout, "the fixture formed no pair to judge")
        # 5. The baseline is gone, and the shrink-only guard no longer lists it.
        self.assertFalse((REPO / BASELINE).exists(), f"{BASELINE} still exists")
        sys.path.insert(0, str(REPO / "tools" / "tests"))
        import test_baselines_only_shrink as shrink  # noqa: PLC0415 - repo-only module
        self.assertNotIn(BASELINE, shrink.BASELINES)
        self.assertTrue(shrink.BASELINES, "the guard lists no baseline at all")

    def test_duplicates_are_judged_within_one_artefact_only(self) -> None:
        """AC2. MUTANTS: group on the selector alone again, so the bug and its fixing story form
        a group; group on the artefact alone, so every criterion of one unit is a pair; key on
        the artefact's folder or id prefix, so two different stories sharing a selector form a
        group; make a reported pair count towards the exit code."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corpus(root)
            r = _lint(root, "--bugs")
            paths = sorted((root / "sdlc-studio").glob("*/*.md"))
            groups = verify_ac.duplicate_verifiers(paths)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        self.assertEqual([{"verifier": PAIR, "acs": ["US0002 AC1", "US0002 AC2"]}], groups)
        dupes = [ln for ln in out.splitlines() if ln.startswith("duplicate verifier")]
        self.assertEqual(1, len(dupes), out)
        self.assertIn(PAIR, dupes[0])
        self.assertIn("US0002 AC1, US0002 AC2", out)
        # The bug sharing its fixing story's selector is correct sharing, and is not reported.
        self.assertNotIn("test_the_fix", "\n".join(dupes))
        self.assertNotIn("BG0001 AC1", out)
        self.assertNotIn("REFUSED", out)

    def test_the_brief_notes_a_shared_selector(self) -> None:
        """AC3. MUTANTS: drop the advisory line from the delivery brief; emit it for every unit;
        judge the pair across the corpus, so the bug that shares its fixing story's selector is
        noted in the bug's brief."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _corpus(root)
            _write(root, "sdlc-studio/personas/seats/qa.md", "# Sam - QA amigo\n\ncharter\n")
            briefs = {}
            for unit in ("US0002", "US0001", "BG0001"):
                r = subprocess.run([sys.executable, "-B", str(CRITIC), "brief", "--unit", unit,
                                    "--seat", "qa", "--root", str(root)],
                                   capture_output=True, text=True, timeout=300, check=False)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                briefs[unit] = [ln for ln in r.stdout.splitlines() if ADVISORY in ln]
        self.assertEqual(1, len(briefs["US0002"]), briefs["US0002"])
        note = briefs["US0002"][0]
        for part in ("AC1", "AC2", PAIR):
            self.assertIn(part, note)
        self.assertNotIn("AC3", note)
        self.assertEqual([], briefs["US0001"], "a unit with distinct selectors carries a note")
        self.assertEqual([], briefs["BG0001"], "a bug sharing its fixing story's selector was noted")


#: The test nodes this story deletes, by the selector text a `Verify:` line names them with.
DELETED_NODES = (
    # Qualified by module: a bare `RatchetTests::` also matches `UnjudgedRatchetTests::` in
    # test_command_audit.py, whose ratchet this story does not touch.
    "test_verify_ac.py::RatchetTests::", "test_verify_ac.py::DuplicateBurndownTests::",
    "test_baselines_only_shrink.py::JsonBaselineReaderTests::",
    "test_the_ratchet_lane_carries_its_flags_at_both_invocation_sites",
    "test_duplicates_are_found_across_different_stories",
    "test_a_reasonless_unresolvable_or_oversized_entry_is_refused",
    "test_a_bad_entry_refuses_through_the_RATCHET_not_only_the_helper",
    "test_a_bad_entry_refuses_through_the_COMMAND_an_operator_types",
    "test_a_baselined_group_that_has_SPREAD_since_is_refused",
    "test_an_epic_or_cr_id_cannot_stand_in_for_the_group_s_acs",
    "test_a_baseline_key_a_human_hand_edited_is_normalised_on_the_way_in",
    "test_two_baseline_keys_that_collide_once_normalised_are_corrupt",
    "test_stamp_will_not_mint_an_entry_with_a_reason",
)

#: The stamped criteria that named a deleted node, by artefact, and how many each carried. The
#: count is the assertion: a retired line dropped or added is a changed record, not a rewording.
RETIRED = {"US0461": 5, "US0635": 3, "US0636": 3, "BG0433": 3}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0897: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0897\b")


class RetiredCriteriaTests(unittest.TestCase):

    def test_the_verify_ratchet_criteria_are_retired(self) -> None:
        """AC4. MUTANTS: leave a stamped criterion's `Verify:` naming a deleted node; retire one
        without its `Verified:` stamp; name another story as the retirer."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        live, retired = [], {}
        for path in [p for d in ARTEFACT_DIRS
                     for p in sorted((REPO / "sdlc-studio" / d).glob("*.md"))]:
            lines = path.read_text(encoding="utf-8").splitlines()
            unit = path.name.split("-")[0]
            for i, line in enumerate(lines):
                stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                if "**Verify:**" in line and stamp and any(n in line for n in DELETED_NODES):
                    live.append(f"{path.name}:{i + 1}")
                if RETIRED_VERIFY.search(line):
                    self.assertRegex(stamp, RETIRED_STAMP,
                                     f"{path.name}:{i + 1} is retired without its stamp")
                    retired[unit] = retired.get(unit, 0) + 1
        self.assertEqual([], live, "a stamped criterion still names a deleted test node")
        self.assertEqual(RETIRED, retired)


if __name__ == "__main__":
    unittest.main()
