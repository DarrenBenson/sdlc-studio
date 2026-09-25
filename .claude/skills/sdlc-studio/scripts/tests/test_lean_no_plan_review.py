"""US0909: a story reaches In Progress and Done without a plan review.

The spec plan-review gate (`plan_review.py`) is gone, with its config block, its telemetry writer
and summary, its re-review bucket in the upgrade rebaseline and its two CLI verbs. AC1 drives
`transition.py set` through the CLI on a schema-v3 workspace that would have been refused, AC3
briefs a unit through `critic.py main` with `plan_review` blocked from import, and AC4 asks
`telemetry.py show --summary` through the CLI. AC5 and AC6 read this repository, because their
criteria are about its derived surface page and its stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
from __future__ import annotations

import ast
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined git for the fixture repos
import workspace  # noqa: E402

REPO = workspace.REPO

#: Five declared files, one of them a spec document: the old gate fired on both signals.
AFFECTS = ["docs/prd.md", "src/a.py", "src/b.py", "src/c.py", "src/d.py"]

STORY = """# US0001: the thing

> **Status:** Ready
> **Epic:** [EP0001: e](../epics/EP0001-e.md)
> **Affects:** {affects}
> **Points:** 3

## Acceptance Criteria

### AC1: the spec is there

- **Given** a spec
- **When** it is read
- **Then** it exists
- **Verify:** file docs/prd.md
"""

EPIC = """# EP0001: e

> **Status:** In Progress

## Story Breakdown

- [ ] [US0001: the thing](../stories/US0001-x.md)
"""

INDEX = """# Stories

| ID | Title | Status |
| --- | --- | --- |
| [US0001](US0001-x.md) | the thing | Ready |
"""


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          env=gitutil.git_env(), timeout=300, check=False)


def _v3_workspace(tmp: str) -> Path:
    """A committed schema-v3 git workspace that has closed a sprint (a committed retro), with
    `plan_review.enabled` unset and one Ready story that cites a spec and declares five files."""
    root = Path(tmp)
    _write(root, "sdlc-studio/.config.yaml", "schema_version: 3\n")
    _write(root, "sdlc-studio/retros/RETRO0001-x.md", "# RETRO0001: x\n")
    _write(root, "sdlc-studio/stories/US0001-x.md", STORY.format(affects=", ".join(AFFECTS)))
    _write(root, "sdlc-studio/stories/_index.md", INDEX)
    _write(root, "sdlc-studio/epics/EP0001-e.md", EPIC)
    for rel in AFFECTS:
        _write(root, rel, "x = 1\n" if rel.endswith(".py") else "# PRD\n")
    gitutil.git(["init", "-q"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "fixture"], cwd=root)
    return root


def _banded(root: Path, uid: str, *, heavy: bool) -> None:
    """A unit `route.estimate` bands high (heavy) or at the bottom of the scale (light)."""
    if heavy:
        files = [f"src/mod{i}.py" for i in range(5)]
        for f in files:
            _write(root, f, "def f():\n" + "    if True:\n        pass\n" * 40)
        affects, points = ", ".join(files), 13
        acs = "".join(f"### AC{i}: does thing {i}\n\n- **Then** z\n- **Verify:** shell true\n\n"
                      for i in range(1, 10))
    else:
        _write(root, "docs/note.md", "a note\n")
        affects, points = "docs/note.md", 1
        acs = "### AC1: works\n\n- **Then** z\n- **Verify:** shell true\n"
    _write(root, f"sdlc-studio/stories/{uid}-x.md",
           f"# {uid}: the thing\n\n> **Status:** In Progress\n> **Affects:** {affects}\n"
           f"> **Points:** {points}\n\n## Acceptance Criteria\n\n{acs}")
    _write(root, "sdlc-studio/personas/seats/qa.md", "# Sam - QA seat\n\ncharter text\n")


#: The criteria whose selector named a test this story deletes, by unit - the story's list, plus
#: the five `-k` selectors on FirstRunPlanReviewSofteningTests (US0662 AC1-AC3, US0663 AC1-AC2)
#: and the five grep criteria reading the docs this story deletes (US0090 AC5, US0091 AC1, AC2,
#: AC4, AC5), which the measured list did not name.
RETIRED = {
    "BG0529": ("AC2",), "BG0565": ("AC1",),
    "BG0567": ("AC1", "AC2", "AC3", "AC4", "AC5"), "BG0637": ("AC10",),
    "US0090": ("AC1", "AC2", "AC3", "AC4", "AC5"), "US0091": ("AC1", "AC2", "AC3", "AC4", "AC5"),
    "US0094": ("AC1", "AC2", "AC3", "AC4"),
    "US0640": ("AC1", "AC2", "AC3", "AC4", "AC5"), "US0662": ("AC1", "AC2", "AC3", "AC4"),
    "US0663": ("AC1", "AC2", "AC3"), "US0684": ("AC3", "AC4"),
}
#: BG0510's two, on checklist lines that carry no AC id.
CHECKLIST_RETIRED = {"BG0510": 2}

#: The test modules this story deletes or cuts classes from, relative to the repository.
#: HAND-MAINTAINED ON PURPOSE: the list is the story's own record of what it cut, not a mirror
#: of a set the production tree owns.
TOUCHED_TESTS = tuple(f".claude/skills/sdlc-studio/scripts/tests/{name}" for name in (
    "test_plan_review.py", "test_lane_plan_review.py", "test_transition.py", "test_telemetry.py",
    "test_project_upgrade.py", "test_critic.py"))


def _artefact(uid: str) -> Path:
    kind = "bugs" if uid.startswith("BG") else "stories"
    return next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md"))


class PlanReviewGoneTests(unittest.TestCase):

    def test_an_unreviewed_spec_story_is_not_refused(self) -> None:
        """AC1. Mutant: delete only the Done-side check and keep the In Progress entry gate -
        the first move is refused naming plan review."""
        with tempfile.TemporaryDirectory() as t:
            root = _v3_workspace(t)
            ran = _run(str(SCRIPTS / "verify_ac.py"), "run", "--root", str(root))
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
            import critic  # noqa: PLC0415
            critic.record_verdict(root, "US0001", "APPROVE", reviewer="qa-seat",
                                  author="dev-seat", brief="a" * 12)
            self.assertTrue(critic.is_independent(critic.verdict_for(root, "US0001")))
            for status in ("In Progress", "Done"):
                with self.subTest(status=status):
                    r = _run(str(SCRIPTS / "transition.py"), "--root", str(root), "set",
                             "US0001", status)
                    out = r.stdout + r.stderr
                    self.assertEqual(r.returncode, 0, out)
                    self.assertIsNone(re.search(r"plan[- _]review", out, re.I), out)
            text = (root / "sdlc-studio" / "stories" / "US0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Done", text)

    def test_nothing_imports_plan_review(self) -> None:
        """AC2. Mutant: delete the module but leave `telemetry.record_plan_review`, which never
        imported it."""
        self.assertFalse((SCRIPTS / "plan_review.py").exists())
        importers = []
        for path in sorted(SCRIPTS.rglob("*.py")):
            if "tests" in path.relative_to(SCRIPTS).parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                         else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                if any(n.split(".")[0] == "plan_review" for n in names):
                    importers.append(f"{path.relative_to(SCRIPTS)}:{node.lineno}")
        self.assertEqual(importers, [], "a shipped script still imports plan_review")
        import telemetry  # noqa: PLC0415
        self.assertFalse(hasattr(telemetry, "record_plan_review"),
                         "telemetry still writes plan-review events")

    def test_the_brief_tier_still_follows_the_route_band(self) -> None:
        """AC3. Mutant: leave `tier_for` calling `plan_review._difficulty_band` - the blocked
        import raises and both units tier `full`."""
        import route  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as t, \
                mock.patch.dict(sys.modules, {"plan_review": None}):
            root = Path(t)
            _banded(root, "US0001", heavy=True)
            _banded(root, "US0002", heavy=False)
            stories = root / "sdlc-studio" / "stories"
            self.assertEqual(route.estimate(root, stories / "US0001-x.md")["difficulty_band"],
                             "high")
            # the bottom of the scale a one-criterion unit reaches; both bottom bands tier light
            self.assertIn(route.estimate(root, stories / "US0002-x.md")["difficulty_band"],
                          ("trivial", "low"))
            import critic  # noqa: PLC0415
            for uid, tier in (("US0001", "full"), ("US0002", "light")):
                with self.subTest(uid=uid):
                    out, err = io.StringIO(), io.StringIO()
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                        rc = critic.main(["brief", "--unit", uid, "--seat", "qa",
                                          "--root", str(root)])
                    self.assertEqual(rc, 0, err.getvalue())
                    self.assertIn(f"review tier: {tier} (derived", err.getvalue())

    def test_no_plan_review_config_rebaseline_or_telemetry(self) -> None:
        """AC4. Mutant: drop the writer but keep the summary block that still reads old events
        - the historical log summarises with a `plan_review` key."""
        defaults = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^plan_review:", defaults),
                          "config-defaults.yaml still carries a plan_review block")
        import project_upgrade  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as t:
            root = _v3_workspace(t)
            census = project_upgrade.rebaseline(root)
            entries = [e for bucket in census.values() for e in bucket]
            self.assertFalse([e for e in entries if e["capability"] == "plan-review"], census)
            self.assertNotIn("re-review", census)
            self.assertIn("US0001", [e["id"] for e in census["backfill"]],
                          "the census did not reach the story at all")

            def summary() -> dict:
                r = _run(str(SCRIPTS / "telemetry.py"), "--root", str(root), "show",
                         "--summary", "--format", "json")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                return json.loads(r.stdout)

            self.assertNotIn("plan_review", summary())
            _write(root, "sdlc-studio/.local/telemetry.jsonl", "\n".join(json.dumps(rec) for rec in (
                {"event": "plan-review", "phase": "plan-review", "id": "US0001",
                 "verdict": "APPROVE", "reviewer": "qa", "author": "dev", "independent": True},
                {"id": "US0001", "type": "story", "iterations": 1})) + "\n")
            got = summary()
            self.assertNotIn("plan_review", got)
            self.assertEqual(got["story"]["count"], 1, "the unit record was not read")
            self.assertNotIn("unknown", got, "the historical event was counted as a unit")

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC5, on this repository's derived surface page."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        page = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        for verb in ("plan_review.py check", "plan_review.py record"):
            self.assertNotIn(verb, page)
        r = _run(str(SCRIPTS / "docgen.py"), "surface", "--check", "--root", str(REPO))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("0 drift", r.stdout + r.stderr)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC6, on this repository's stamped criteria."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        import verify_ac  # noqa: PLC0415
        for uid, acs in RETIRED.items():
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(
                _artefact(uid).read_text(encoding="utf-8"))}
            for ac in acs:
                with self.subTest(unit=uid, ac=ac):
                    block = blocks.get(ac)
                    self.assertIsNotNone(block, f"{uid} has no {ac}")
                    self.assertTrue((block.verifier or "").startswith(
                        "manual - retired by US0909: "), block.verifier)
                    self.assertEqual(block.verified_state, "manual", block)
                    self.assertEqual(block.verified_reason, "retired, superseded by US0909",
                                     block)
        # BG0510 writes its criteria as a checklist, one line each, which criteria_blocks skips
        checklist = [line for line in _artefact("BG0510").read_text(encoding="utf-8").splitlines()
                     if line.startswith("- [x]") and "*Verify:* manual - retired by US0909: "
                     in line and "*Verified:* manual (" in line
                     and line.endswith(") - retired, superseded by US0909")]
        self.assertEqual(len(checklist), CHECKLIST_RETIRED["BG0510"], "BG0510 is not retired")
        # Every stamped selector naming a touched module still selects something in this tree,
        # judged by AST the way the stamps-staged commit lane judges the index.
        nodes = {rel: (verify_ac._ast_nodes((REPO / rel).read_text(encoding="utf-8"))  # noqa: SLF001
                       if (REPO / rel).exists() else None) for rel in TOUCHED_TESTS}
        dead = []
        for kind in ("stories", "bugs"):
            for path in sorted((REPO / "sdlc-studio" / kind).rglob("*.md")):
                text = path.read_text(encoding="utf-8", errors="replace")
                stamped = [(b.ac_id, b.verifier) for b in verify_ac.criteria_blocks(text)
                           if (b.verified_state or "").strip().lower() == "yes" and b.verifier]
                # the checklist shape criteria_blocks does not read: `- [x] ... *Verify:* ...`
                stamped += [("checklist", line.split("*Verify:* ", 1)[1].split(" *Verified:*")[0])
                            for line in text.splitlines()
                            if line.startswith("- [x]") and "*Verify:* " in line]
                for ac, verifier in stamped:
                    test_file, node, kpat = verify_ac._selector_parts(verifier, REPO)  # noqa: SLF001
                    if test_file not in nodes:
                        continue
                    if nodes[test_file] is None or not verify_ac._selector_live(  # noqa: SLF001
                            test_file, node, kpat, nodes[test_file]):
                        dead.append(f"{path.name[:6]} {ac}: {verifier}")
        self.assertEqual(dead, [], "a stamped criterion names a deleted test")
        # US0641's stamp survives: its node is rewritten against route.estimate, same name
        us0641 = _artefact("US0641").read_text(encoding="utf-8")
        self.assertRegex(us0641, r"BriefTierTests::test_an_unresolvable_band_tiers_full\n"
                                 r"- \*\*Verified:\*\* yes")
        source = (HERE / "test_critic.py").read_text(encoding="utf-8")
        node = next(n for c in ast.parse(source).body
                    if isinstance(c, ast.ClassDef) and c.name == "BriefTierTests"
                    for n in c.body if getattr(n, "name", "") == "test_an_unresolvable_band_tiers_full")
        body = ast.get_source_segment(source, node)
        self.assertIn("route", body)
        self.assertNotIn("plan_review", body)


if __name__ == "__main__":
    unittest.main()
