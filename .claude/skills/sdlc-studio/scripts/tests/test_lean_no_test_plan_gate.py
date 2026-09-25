"""US0911: a unit plans and closes on its criteria and Verify selectors, with no test-plan gate,
planned-mutant join or plan-time falsifiability probe.

AC1 to AC3 drive the shipped entry points (`transition.py`, `sprint.py`, `mutation.py`) as
subprocesses against a throwaway workspace. AC4 reads the shipped defaults and scripts, and AC5
reads this repository's own artefacts, because that is what each criterion names.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
REPO = SKILL.parents[2]
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import verify_ac  # noqa: E402

#: Each criterion is created after the cutoff the fixture sets, so HEAD's gates are armed.
_CFG = 'schema_version: 3\nreview:\n  test_plan_after: "2026-01-01"\n  mutation_evidence: off\n'
_HEAD = "> **Status:** In Progress\n> **Created:** 2026-08-10\n"
_STORY = ("# US0001: a story\n\n" + _HEAD + "\n## Acceptance Criteria\n\n"
          "### AC1: it works\n\n- **Verify:** shell true\n")
_BUG = ("# BG0001: a bug\n\n" + _HEAD + "> **Severity:** medium\n"
        "> **Verification depth:** functional\n\n## Acceptance Criteria\n\n"
        "- [ ] **AC1** Given a, when b, then c\n  - **Verify:** shell true\n")

#: The nodes this story deletes, by module. AC5 asserts each is gone and that no stamped
#: selector still names one.
DELETED = {
    "test_transition.py": ("TestPlanGateTests", "TestPlanGateEntryTests",
                           "PlannedMutantGateNamesTheRowTests", "PlanReviewRepairGateTests",
                           "test_only_the_epic_is_released_from_the_test_plan_gate"),
    "test_sprint.py": ("UnnameableMutantTests", "PlanFalsifiabilityGateTests"),
    "test_config.py": ("test_the_two_cutoffs_document_the_kind_of_value_each_takes",),
}


def _run(script: str, *argv: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=300)


def _status(path: Path) -> str:
    m = re.search(r"^> \*\*Status:\*\* (.+)$", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else ""


def _plan_bug(root: Path, uid: str, points: str = "> **Points:** 3\n") -> None:
    """A groomed batch bug whose Test Plan holds a bare and a reasoned `unnameable` row. Its
    criteria run a real passing pytest node, which HEAD's probe classes `green`."""
    (root / "sdlc-studio" / "bugs" / f"{uid}-x.md").write_text(
        f"# {uid}: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** src/thing.py\n{points}\n## Acceptance Criteria\n\n"
        "### AC1: it holds\n\n- **Verify:** pytest tests/test_thing.py::test_holds\n\n"
        "### AC2: it reports\n\n- **Verify:** pytest tests/test_thing.py::test_holds\n\n"
        "## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
        "| AC1 | unnameable | it holds |\n"
        "| AC2 | unnameable: the criterion is about operator judgement and no code edit "
        "can falsify it | it reports |\n", encoding="utf-8")


def _nodes(module: Path) -> set:
    """Every class and function name the test module defines."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef))}


def _selects(verifier: str, mod: str, names: set) -> bool:
    """Does a pytest selector still name something `mod` defines? Each `mod::` node id needs every
    part; a `-k` expression needs each of its words inside some name, as pytest matches it."""
    if " -k " in f" {verifier} ":
        expr = verifier.split("-k", 1)[1]
        words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr)
                 if w not in ("and", "or", "not")]
        return all(any(w in n for n in names) for w in words)
    nodes = [t for t in verifier.split() if f"tests/{mod}::" in t]
    return all(part in names for node in nodes for part in node.split("::")[1:])


class TestPlanGateGoneTests(unittest.TestCase):
    def test_a_unit_without_a_test_plan_closes(self) -> None:
        """AC1. MUTANT: delete the Done-side test-plan gate and leave the Fixed-side planned-mutant
        gate - the bug is then refused for having no plan."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for sub in ("bugs", "stories"):
                (root / "sdlc-studio" / sub).mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(_CFG, encoding="utf-8")
            story = root / "sdlc-studio" / "stories" / "US0001-a-story.md"
            bug = root / "sdlc-studio" / "bugs" / "BG0001-a-bug.md"
            story.write_text(_STORY, encoding="utf-8")
            bug.write_text(_BUG, encoding="utf-8")
            for uid, path, target in (("US0001", story, "Done"), ("BG0001", bug, "Fixed")):
                with self.subTest(unit=uid):
                    self.assertNotIn("## Test Plan", path.read_text(encoding="utf-8"))
                    critic.record_verdict(root, uid, "APPROVE", "rev", "dev")
                    _run("verify_ac.py", "run", "--id", uid, root=root)
                    r = _run("transition.py", "set", uid, target, root=root)
                    out = (r.stdout + r.stderr).lower()
                    self.assertEqual(r.returncode, 0, out)
                    self.assertEqual(_status(path), target)
                    self.assertNotIn("test plan", out)
                    self.assertNotIn("planned mutant", out)

    def test_plan_neither_probes_nor_refuses_unnameable_rows(self) -> None:
        """AC2. MUTANTS: delete only the malformed-row branch (the reasoned row is still refused);
        delete the grooming read and keep the probe (under `block` it refuses the green
        criteria); a deletion that takes the Points refusal with it (the control plans)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "schema_version: 3\nreview:\n  plan_falsifiability: block\n", encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_thing.py").write_text("def test_holds():\n    assert True\n",
                                                          encoding="utf-8")
            _plan_bug(root, "BG0001")
            argv = ("plan", "--bugs", "Open", "--no-fetch", "--skip-personas")
            r = _run("sprint.py", *argv, root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            self.assertIn("BG0001", out)
            self.assertNotIn("unnameable", out)
            self.assertNotIn("falsifiab", out.lower())
            self.assertNotIn("cannot fail", out)

            _plan_bug(root, "BG0002", points="")
            r = _run("sprint.py", *argv, root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 2, out)
            self.assertIn("BG0002", out)
            self.assertIn("Points", out)

    def test_from_plan_is_retired(self) -> None:
        """AC3. MUTANT: keep `--from-plan` on the parser - it runs the join and exits on its
        verdict, and `--help` still offers it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            r = _run("mutation.py", "run", "--story", "BG0001", "--from-plan", root=root)
            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn("--from-plan", r.stderr)
            self.assertIn("retired", r.stderr)
            self.assertIn("mutation.py run", r.stderr)
            self.assertEqual(sorted(p.name for p in (root / "sdlc-studio").rglob("*")), ["bugs"],
                             "a retired flag wrote something")
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "mutation.py"), "run", "--help"],
                           capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("--from-plan", r.stdout)

    def test_no_test_plan_keys_are_read(self) -> None:
        """AC4. MUTANT: delete the keys from the defaults while `transition.py` still reads
        `review.test_plan_after` with a fallback."""
        defaults = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        for key in ("test_plan_after", "plan_falsifiability"):
            self.assertNotIn(key, defaults)
        gone = ("test_plan_after", "plan_falsifiability", "_plan_gate_active",
                "_planned_mutant_gate", "_test_plan_gate")
        readers = []
        for path in sorted(SCRIPTS.rglob("*.py")):
            if "tests" in path.relative_to(SCRIPTS).parts:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                # A line that names a key as retired (a migration's strip list) reads nothing.
                if "retired" not in line and any(g in line for g in gone):
                    readers.append(f"{path.relative_to(SCRIPTS)}:{n}")
        self.assertEqual(readers, [])

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: keep one deleted class (its node is then still defined); retire one
        criterion fewer (its stamped selector then names a node that is gone)."""
        tests = SCRIPTS / "tests"
        names = {mod: _nodes(tests / mod) for mod in DELETED}
        for mod, deleted in DELETED.items():
            self.assertEqual(sorted(set(deleted) & names[mod]), [], mod)
        dead, read = [], 0
        for path in sorted((REPO / "sdlc-studio").rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if not any(mod in text for mod in DELETED):
                continue
            for block in verify_ac.criteria_blocks(text):
                verifier = block.verifier or ""
                if (block.verified_state or "").strip().lower() != "yes":
                    continue
                mod = (next((m for m in DELETED if f"tests/{m}" in verifier), None)
                       if verifier.startswith("pytest ") else None)
                read += bool(mod)
                if mod and not _selects(verifier, mod, names[mod]):
                    dead.append(f"{path.name[:6]} {block.ac_id}: {verifier}")
        self.assertGreater(read, 100, "the scan read no stamped selector, so it proves nothing")
        self.assertEqual(dead, [], "\n".join(dead))


if __name__ == "__main__":
    unittest.main()
