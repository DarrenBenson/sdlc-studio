"""US0895: a commit runs only the gate lanes that can refuse it.

`gate.py --root .`, as the pre-commit hook calls it, spent about 70s of every commit on eight
advisory lanes that can never refuse one: doc-freshness, constitution, doc-surface, disclosure,
provenance, mutation, hook-enabled and batch-size. They leave the per-commit gate. doc-freshness
runs at the sprint close, where it reports and never blocks; the other seven run when named with
`--only`.

AC1 and AC2 drive the gate over throwaway git workspaces, with each of the eight lanes patched to
raise wherever the gate module holds it, so a lane that runs cannot pass unnoticed. AC3 reads the
live artefacts, because its criterion is about this repository's stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined git for the fixture repos
import workspace  # noqa: E402
import gate  # noqa: E402

REPO = workspace.REPO

#: The eight advisory lanes, by the gate function each runs.
ADVISORY_LANES = {
    "doc-freshness": "_doc_freshness", "constitution": "_constitution",
    "doc-surface": "_doc_surface", "disclosure": "_disclosure", "provenance": "_provenance",
    "mutation": "_mutation", "hook-enabled": "_hook_enabled", "batch-size": "_batch_size",
}

#: The lanes that refuse a commit, each of which the defect fixture below trips.
REFUSING_LANES = ("conformance", "reconcile", "validate", "integrity", "duplicate-id")

STORY = ("# {uid}: {title}\n\n> **Status:** {status}\n{epic}\n## Acceptance Criteria\n\n"
         "### AC1: works\n- **Given** a thing\n{verify}")


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _workspace(tmp: str) -> Path:
    """A git repository with an empty workspace and one committed file."""
    root = Path(tmp)
    _write(root, "sdlc-studio/.keep", "")
    _write(root, "README.md", "x\n")
    gitutil.git(["init", "-q"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "baseline"], cwd=root)
    return root


def _stage_defects(root: Path) -> None:
    """Staged stories carrying a defect for each refusing lane: two files claiming US0001
    (duplicate-id), no epic on an open story (integrity), a status outside the vocabulary
    (validate, conformance) and no stories index (reconcile, conformance)."""
    good = STORY.format(uid="US0001", title="first", status="Ready", epic="",
                        verify="- **Verify:** shell true\n")
    _write(root, "sdlc-studio/stories/US0001-first.md", good)
    _write(root, "sdlc-studio/stories/US0001-twin.md", good)
    _write(root, "sdlc-studio/stories/US0002-bad.md", STORY.format(
        uid="US0002", title="bad", status="Bananas", verify="",
        epic="> **Epic:** [EP0001: x](../epics/EP0001-x.md)\n"))
    gitutil.git(["add", "-A"], cwd=root)


def _stale_latest(root: Path) -> None:
    """A skill tree whose LATEST.md runs past its 80-line ceiling: one real doc-freshness
    finding, committed so the tree is clean as it is at a close."""
    _write(root, ".claude/skills/sdlc-studio/SKILL.md", "---\nname: sdlc-studio\n---\n# x\n")
    _write(root, ".claude/skills/sdlc-studio/help/help.md", "# help\n")  # conformance reads it
    _write(root, "sdlc-studio/reviews/LATEST.md",
           "# Latest\n\n" + "".join(f"- line {i}\n" for i in range(100)))
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "anchor"], cwd=root)


class _Lanes:
    """Replaces each named advisory lane wherever the gate module holds it - the module
    attribute and every table that carries the function - with a recorder. `raising` makes the
    recorder raise as well, so a lane that runs is both logged and visible as an error row."""

    def __init__(self, names, raising: bool = True) -> None:
        self.names, self.raising, self.reached = list(names), raising, []

    def _stub(self, name: str):
        def lane(root):
            self.reached.append(name)
            if self.raising:
                raise AssertionError(f"the advisory lane {name} ran")
            return {"count": 0, "blocking": False, "detail": f"{name} ran"}
        return lane

    @contextlib.contextmanager
    def patched(self):
        with contextlib.ExitStack() as stack:
            tables = [v for v in vars(gate).values() if isinstance(v, dict)]
            for name in self.names:
                attr = ADVISORY_LANES[name]
                real, stub = getattr(gate, attr), self._stub(name)
                stack.enter_context(mock.patch.object(gate, attr, stub))
                for table in tables:
                    for key, fn in list(table.items()):
                        if fn is real:
                            stack.enter_context(mock.patch.dict(table, {key: stub}))
            yield self


def _main(*argv: str) -> tuple[int, dict]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        rc = gate.main([*argv, "--format", "json"])
    return rc, json.loads(out.getvalue())


def _rows(report: dict) -> dict:
    return {r["check"]: r for r in report["checks"]}


def _passing(root):
    return {"count": 0, "blocking": True, "detail": "stubbed pass"}


class PerCommitLaneTests(unittest.TestCase):

    def test_the_advisory_lanes_leave_the_commit_gate(self) -> None:
        """AC1. MUTANTS: leave any one of the eight in DEFAULT_CHECKS; drop a refusing lane
        from it; make the plain gate select nothing it did not select before."""
        with tempfile.TemporaryDirectory() as t:
            root = _workspace(t)
            _stage_defects(root)
            with _Lanes(ADVISORY_LANES).patched() as lanes:
                rc, report = _main("--root", str(root))
        rows = _rows(report)
        self.assertEqual([], lanes.reached, "an advisory lane ran on the commit gate")
        self.assertEqual(set(), set(ADVISORY_LANES) & set(rows))
        for name in REFUSING_LANES:
            with self.subTest(lane=name):
                self.assertIn(name, rows, f"{name} no longer runs on the commit gate")
                self.assertEqual("fail", rows[name]["status"], rows[name]["detail"])
                self.assertTrue(rows[name]["blocking"], rows[name]["detail"])
        self.assertEqual(1, rc)
        self.assertFalse(report["ok"])

    def test_a_lane_the_project_set_to_block_stays_in_the_commit_gate(self) -> None:
        """D0263: a refusal a project opted into is kept; only a lane that can merely advise
        leaves. MUTANT: drop the enforced lanes from the plain run as well ("enforced lane
        still dropped"); keep them in whether or not the project enforces them."""
        principle = ("# Constitution\n\n## Principles\n\n"
                     "- **Every story traces to a parent epic.** `rule: story-requires-epic`\n")
        story = STORY.format(uid="US0001", title="orphan", status="Ready", epic="",
                             verify="- **Verify:** shell true\n")
        others = [n for n in ADVISORY_LANES if n not in ("constitution", "provenance")]
        for enforce in (True, False):
            with self.subTest(enforce=enforce), tempfile.TemporaryDirectory() as t:
                root = _workspace(t)
                _write(root, "sdlc-studio/constitution.md", principle)
                _write(root, "sdlc-studio/stories/US0001-orphan.md", story)
                if enforce:
                    _write(root, "sdlc-studio/.config.yaml",
                           "constitution:\n  enforce: true\nprovenance:\n  enforce: true\n")
                with _Lanes(others).patched() as lanes:
                    rc, report = _main("--root", str(root))
                rows = _rows(report)
                self.assertEqual([], lanes.reached, "an advisory-only lane ran on the commit gate")
                if not enforce:
                    self.assertNotIn("constitution", rows)
                    self.assertNotIn("provenance", rows)
                    continue
                self.assertIn("constitution", rows, "the enforced constitution lane was dropped")
                self.assertEqual("fail", rows["constitution"]["status"], rows["constitution"])
                self.assertTrue(rows["constitution"]["blocking"], rows["constitution"])
                self.assertIn("provenance", rows, "the enforced provenance lane was dropped")
                self.assertTrue(rows["provenance"]["blocking"], rows["provenance"])
                self.assertEqual(1, rc)
                self.assertFalse(report["ok"])

    def test_doc_freshness_runs_at_the_close_and_never_blocks(self) -> None:
        """AC2. The gate exactly as `sprint close` calls it, with the close's own lanes (retro,
        lessons, review currency) and the standard lanes stubbed green, so the verdict turns on
        doc-freshness alone. MUTANTS: leave doc-freshness out of the close; make it blocking;
        run any of the other seven at the close; refuse `--only <lane>` for one of them."""
        others = [n for n in ADVISORY_LANES if n != "doc-freshness"]
        green = {n: _passing for n in gate.DEFAULT_CHECKS if n not in ADVISORY_LANES}
        green.update({n: _passing for n in gate.LESSONS_CLOSE_CHECKS})
        with tempfile.TemporaryDirectory() as t:
            root = _workspace(t)
            _stale_latest(root)
            with _Lanes(others).patched() as lanes, \
                    mock.patch.dict(gate.DEFAULT_CHECKS, green), \
                    mock.patch.dict(gate.LESSONS_CLOSE_CHECKS, green), \
                    mock.patch.object(gate, "_retro_present", lambda r, rid: _passing(r)), \
                    mock.patch.object(gate, "_review_current", _passing), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                close = gate.run_gate(str(root), require_retro="RETRO0001",
                                      require_review=True, conformance_scope=set())
            self.assertEqual([], lanes.reached, "an on-demand lane ran at the close")
            row = _rows(close).get("doc-freshness")
            self.assertIsNotNone(row, "doc-freshness did not run at the close")
            self.assertEqual("fail", row["status"], row["detail"])
            self.assertGreaterEqual(row["count"], 1, row["detail"])
            self.assertIn("stale LATEST.md claim", row["detail"])
            self.assertFalse(row["blocking"])
            failing = [r for r in close["checks"] if r["blocking"] and r["status"] != "pass"]
            self.assertTrue(close["ok"], f"the close failed on {failing}")

            # The other seven: on demand, each when named with --only.
            for name in others:
                with self.subTest(lane=name), _Lanes([name], raising=False).patched() as one:
                    rc, report = _main("--root", str(root), "--only", name)
                    self.assertEqual([name], one.reached)
                    self.assertEqual([name], [r["check"] for r in report["checks"]])


#: The test nodes this story deletes, by the selector text a `Verify:` line names them with.
DELETED_NODES = ("test_gate.py::GateRealWrapperTests::test_default_checks_present",)

#: The stamped criteria that named a deleted node, by artefact, and how many each carried.
RETIRED = {"US0039": 1}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0895: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0895\b")
ARTEFACT_DIRS = ("stories", "bugs", "change-requests")


class RetiredCriteriaTests(unittest.TestCase):

    def test_criteria_naming_deleted_gate_lane_tests_are_retired(self) -> None:
        """AC3. MUTANTS: leave a stamped criterion naming a deleted node; retire one without
        its `Verified:` stamp; name another story as the retirer; keep the deleted node."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for node in DELETED_NODES:
            module, *names = node.split("::")
            source = (HERE / module).read_text(encoding="utf-8")
            self.assertFalse(f"def {names[-1]}(" in source, f"{node} still exists")
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
