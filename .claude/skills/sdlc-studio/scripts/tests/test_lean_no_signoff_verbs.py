"""US0919: the operator's one signature is `sprint sign`, and the per-unit sign-off verbs are gone.

`critic.py signoff` and `critic.py signoff-brief` are refused by name, the sign-off panel
(`persona_resolve.py panel --ceremony signoff`, the plan-time assignment and the
`review.signoff` key) is gone, and the frozen `signoff-record.md` is read by nothing. The
principal-independence check `sprint sign` asks of every batch unit survives, moved into
`sprint._principal_refusals`.

AC1 to AC4 drive the shipped entry points in throwaway workspaces. AC5 and AC6 read this
repository, because their criteria name its surface page and its stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import workspace  # noqa: E402
import critic  # noqa: E402
import persona_resolve  # noqa: E402
import sprint  # noqa: E402
import verify_ac  # noqa: E402
import test_lean_no_two_role as stamps  # noqa: E402 - the derived deleted-node check (US0916)
import test_lean_sign_seals_once as seal  # noqa: E402 - the sign fixture (US0917)

REPO = workspace.REPO

#: The criteria whose selector named a test this story deletes, by unit, each retired in the
#: D0259 pattern. The story's list, less US0602 AC2 (already retired by US0917) and BG0393 (its
#: `UnansweredPanelTests` judge `critic.goal_panel`, which the close still calls, so they stay),
#: plus what the measured list did not name: US0428 AC1/AC2 (the delegated sign-off disclosure
#: AC4 removes), and three `-k` selectors
#: reaching only deleted classes - US0194 AC2/AC3 (`-k Delegate`, `-k SignoffBrief`) and US0198
#: AC2 (`-k CloseBrief`, the sign-off brief the close once printed).
RETIRED = {
    "BG0406": ("AC8",), "BG0496": ("AC1", "AC2"), "US0194": ("AC2", "AC3"),
    "US0198": ("AC2",),
    "US0427": ("AC1", "AC2", "AC3"), "US0428": ("AC1", "AC2"),
    "US0598": ("AC1", "AC2", "AC3", "AC4"), "US0599": ("AC1", "AC2", "AC3"),
    "US0601": ("AC1", "AC2"), "US0602": ("AC1",),
    "US0643": ("AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "AC7"),
    "US0644": ("AC1", "AC2", "AC3", "AC4", "AC5"),
}

#: Deleted nodes, as (class, test) - a whole class as (class, ""). The full deleted set is
#: DERIVED; these prove the derivation reads the right base, since each must appear in it.
AC6_DELETED = {
    "test_critic.py": (("PanelSignoffCliTests", ""), ("SignoffCapacityTests", ""),
                       ("SignoffDelegateTests", ""), ("SignoffPolicyTests", ""),
                       ("SignoffProvenanceTests", ""), ("PanelInterlockTests", ""),
                       ("SkippedCountTests", "")),
    "test_persona_resolve.py": (("PanelAssignmentTests", ""),),
    "test_sprint.py": (("SignoffPanelAssignmentTests", ""),),
    "test_lane_critic.py": (("US0644TheCapacityReachesTheWrittenRecord", ""),),
}

#: The sign-off ledger as HEAD wrote it: one direct row and one delegated-agent row.
LEDGER = (
    "# Reviewer-of-Record Sign-offs\n\n"
    "| Unit | Principal | Chain | Author | Date | Note | Capacity |\n"
    "| --- | --- | --- | --- | --- | --- | --- |\n"
    "| US0001 | operator | - | builder | 2026-08-01 | - | human |\n"
    "| US0002 | qa-seat | operator -> qa-seat (boundary: agent) [DELEGATED AGENT] | builder "
    "| 2026-08-01 | - | human |\n")


def _run(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=300)


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _config_reads(path: Path, key: str) -> list[str]:
    """`file:line` for each call handed `key` as an argument - a config READ - in a module.
    A registry naming the key retired (a dict key, a docstring) is not a read."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [f"{path.name}:{node.lineno}" for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and any(isinstance(a, ast.Constant) and a.value == key
                    for a in [*node.args, *(k.value for k in node.keywords)])]


class SignoffVerbsGoneTests(unittest.TestCase):

    def test_the_signoff_verbs_are_retired(self) -> None:
        """AC1. MUTANTS: keep either verb in the parser; drop it from the parser with no by-name
        refusal (argparse's bare `invalid choice`); delete `critic.signoff_refusal` with the
        verbs and nothing in its place, so `sprint sign` seals under the author's own seat."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/reviews/.keep", "")
            for argv in (["signoff", "--unit", "US0001", "--principal", "operator",
                          "--author", "builder", "--root", str(root)],
                         ["--root", str(root), "signoff-brief", "--units", "US0001"]):
                with self.subTest(verb=argv):
                    r = _run("critic.py", *argv)
                    self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                    self.assertIn("retired", r.stderr)
                    self.assertIn("sprint.py sign", r.stderr)
            self.assertFalse((root / "sdlc-studio" / "reviews" / "signoff-record.md").exists(),
                             "a retired verb wrote a sign-off row")
        r = _run("critic.py", "--help")
        self.assertEqual(0, r.returncode, r.stderr)
        verbs = r.stdout.split("{", 1)[1].split("}", 1)[0].split(",")
        self.assertIn("record", verbs, "the help lost a live verb")
        self.assertNotIn("signoff", verbs)
        self.assertNotIn("signoff-brief", verbs)
        self.assertFalse(hasattr(critic, "signoff_refusal"), "the check was not moved off critic")
        # THE SURVIVING CHECK. `sprint sign` by the unit's author, or by the seat that reviewed
        # it, is refused with nothing written; an outside principal seals.
        # Recased spellings too: the check compares identities, not raw strings, so a principal
        # cannot walk round it by capitalising the author's or the reviewer's name.
        for principal, why in (("builder", "is the author"),
                               ("qa-seat", "authoring-session"),
                               ("Builder", "is the author"),
                               ("QA-Seat", "authoring-session")):
            with self.subTest(principal=principal), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                seal._unit(root, "US0101")
                seal._run_state(root, ["US0101"])
                rc, out, err = seal._cli(root, "sign", "--report", "RPT0001",
                                         "--principal", principal)
                self.assertEqual(2, rc, out + err)
                self.assertIn("sign REFUSED: US0101", err)
                self.assertIn(why, err)
                self.assertEqual("Review", seal._status(root, "US0101"))
                self.assertIsNone(sprint.run_state.read(root).get("signature"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seal._unit(root, "US0101")
            seal._run_state(root, ["US0101"])
            rc, out, err = seal._sign(root)
            self.assertEqual(0, rc, out + err)
            self.assertEqual("Done", seal._status(root, "US0101"))

    def test_the_signoff_ceremony_is_retired_and_the_review_panel_works(self) -> None:
        """AC2. MUTANTS: HEAD, which assigns and records the sign-off panel; a deletion that
        takes the `panel` verb with it, so refine and triage stop resolving."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            for argv in (["panel", "--ceremony", "signoff", "--root", str(root)],
                         ["--root", str(root), "panel", "--ceremony=signoff"]):
                with self.subTest(argv=argv):
                    r = _run("persona_resolve.py", *argv)
                    self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                    self.assertIn("--ceremony signoff", r.stderr)
                    self.assertIn("retired", r.stderr)
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists(),
                             "the retired ceremony recorded an assignment on the run")
            self.assertFalse(hasattr(persona_resolve, "signoff_panel"))
            for ceremony, lead in (("refine", "engineering"), ("triage", "qa")):
                with self.subTest(ceremony=ceremony):
                    r = _run("persona_resolve.py", "panel", "--ceremony", ceremony,
                             "--root", str(root))
                    self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                    self.assertIn(f"{ceremony} amigo panel", r.stdout)
                    self.assertIn(f"({lead})", r.stdout.split(":", 1)[1].split(",")[0])

    def test_review_signoff_has_no_reader(self) -> None:
        """AC3. MUTANTS: HEAD's plan-time panel assignment, which records `signoff_panel` on the
        run or refuses the plan when the seats cannot supply it; keep `review.signoff` in the
        shipped defaults; keep `critic.signoff_policy` reading it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml", "review:\n  signoff: panel\n")
            _write(root, "src/bg0001.py", "")
            _write(root, "sdlc-studio/bugs/BG0001-x.md",
                   "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                   "> **Affects:** src/bg0001.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                   "### AC1: it behaves as recorded\n\n- **Given** the recorded state\n"
                   "- **Verify:** shell true\n")
            # The seats cannot be rendered, the case HEAD refused the plan over.
            real = persona_resolve.amigo_panel

            def unresolvable(*_a, **_k):
                raise persona_resolve.RenderError("no seat card could be rendered")
            persona_resolve.amigo_panel = unresolvable
            self.addCleanup(setattr, persona_resolve, "amigo_panel", real)
            rc, out, err = seal._cli(root, "plan", "--bugs", "Open", "--write", "--no-fetch")
            self.assertEqual(0, rc, out + err)
            self.assertNotIn("sign-off panel", out + err)
            state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                               .read_text(encoding="utf-8"))
            self.assertEqual(["BG0001"], state["batch"])
            self.assertNotIn("signoff_panel", state)
        defaults = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        review = defaults.split("\nreview:\n", 1)[1]
        review = review[:re.search(r"(?m)^\S", review).start()]
        self.assertIsNone(re.search(r"(?m)^  signoff\s*:", review),
                          "config-defaults.yaml still carries review.signoff")
        reads = [hit for path in sorted(SCRIPTS.rglob("*.py"))
                 if "tests" not in path.relative_to(SCRIPTS).parts
                 for hit in _config_reads(path, "review.signoff")]
        self.assertEqual([], reads, "a shipped script still reads review.signoff")

    def test_the_signoff_ledger_is_frozen_and_unread(self) -> None:
        """AC4. MUTANT: HEAD's `sprint_report` delegated-row read, which prints a 'Delegated
        sign-offs' block naming US0002 from the frozen ledger."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/retros/RETRO9100-t.md",
                   "# RETRO9100: a sprint\n\n> **Batch:** US0001, US0002\n\n## Delivered\n"
                   "- shipped\n\n## Lessons\n- a lesson worth keeping for next time\n")
            for uid in ("US0001", "US0002"):
                _write(root, f"sdlc-studio/stories/{uid}-s.md",
                       f"# {uid}: s\n\n> **Status:** Done\n> **Points:** 2\n")
            ledger = _write(root, "sdlc-studio/reviews/signoff-record.md", LEDGER)
            before = ledger.read_bytes()
            r = _run("sprint_report.py", "--root", str(root), "show", "--id", "RETRO9100")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("RETRO9100", r.stdout, "the report did not render")
            self.assertNotIn("Delegated sign-offs", r.stdout + r.stderr)
            self.assertNotIn("DELEGATED AGENT", r.stdout + r.stderr)
            self.assertEqual(before, ledger.read_bytes(), "the frozen ledger was rewritten")
        self.assertFalse(hasattr(critic, "delegated_agent_signoffs"))
        self.assertFalse(hasattr(sprint, "_disclose_delegated_signoffs"),
                         "the close still discloses rows read from the frozen ledger")

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC5. MUTANT: retire the verbs without rerunning `docgen.py surface`, so the table
        still lists them and `--check` reports drift."""
        text = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertIn("`critic.py record`", text, "the surface lost a live verb")
        self.assertIn("`persona_resolve.py panel`", text, "the surface lost the panel verb")
        for verb in ("critic.py signoff", "critic.py signoff-brief"):
            self.assertNotIn(f"`{verb}`", text, f"the surface lists {verb}")
        r = _run("docgen.py", "surface", "--check", "--root", str(REPO))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("docgen surface: 0 drift item(s)", r.stdout)

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC6. MUTANTS: leave a retired criterion's `Verified: yes` stamp in place; retire one
        with a hand-written reason that is not the D0259 shape; keep a deleted class.

        The deleted nodes are DERIVED, as US0916's check derives them: every class and `test_`
        function a changed test module defined at the base and no longer defines, the base
        being the parent of the commit that added this module (HEAD while it is uncommitted)."""
        for uid, acs in RETIRED.items():
            kind = "bugs" if uid.startswith("BG") else "stories"
            path = next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md"))
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(
                path.read_text(encoding="utf-8"))}
            for ac in acs:
                with self.subTest(unit=uid, ac=ac):
                    block = blocks.get(ac)
                    self.assertIsNotNone(block, f"{uid} has no {ac}")
                    self.assertTrue((block.verifier or "").startswith(
                        "manual - retired by US0919: "), block.verifier)
                    self.assertEqual("manual", block.verified_state, block)
                    self.assertEqual("retired, superseded by US0919", block.verified_reason,
                                     block)
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = stamps._deleted_nodes(base)
        for module, nodes in AC6_DELETED.items():
            gone = deleted.get(module, {}).get("gone", set())
            for node in nodes:
                self.assertIn(node, gone, f"{module}::{node} was to be deleted ({base})")
        # BG0393's goal-panel tests are not sign-off tests, and stay.
        self.assertNotIn(("UnansweredPanelTests", ""),
                         deleted.get("test_critic.py", {}).get("gone", set()))
        tests = ".claude/skills/sdlc-studio/scripts/tests/test_critic.py"
        controls = {
            "live": ([f"- **Verify:** pytest {tests}::SignoffPolicyTests::test_the_default_is_"
                      "operator", "- **Verified:** yes (2026-08-01)"], ["live:1"]),
            "retired": ([f"- **Verify:** pytest {tests}::SignoffPolicyTests",
                         "- **Verified:** manual (2026-09-25) - retired, superseded by US0919"],
                        []),
        }
        for label, (lines, want) in controls.items():
            self.assertEqual(stamps._live_stamps([(label, lines)], deleted), want, label)
        live = stamps._live_stamps(((path.relative_to(REPO), path.read_text(
            encoding="utf-8", errors="replace").splitlines())
            for path in sorted((REPO / "sdlc-studio").rglob("*.md"))), deleted)
        self.assertEqual(live, [], "a live stamp selects only deleted test nodes")


def _base_ref() -> str | None:
    """The parent of the commit that added this module, or HEAD while it is uncommitted."""
    rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    added = stamps._git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if stamps._git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


if __name__ == "__main__":
    unittest.main()
