"""US0912: a unit's criteria and their Verify selectors are its whole test plan.

`verify_ac.py testplan` (derive, probe, rule, withdraw), the plan-row readers behind it,
`mutation.plan_execution` and `tools/batch_plan_shape.py` are deleted. AC1 and AC2 drive the
shipped entry points against throwaway workspaces; AC3 to AC5 read this repository, because
that is what each of those criteria names.
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
sys.path.insert(0, str(SCRIPTS / "tests"))
import gitutil  # noqa: E402 - confined, hermetic git for the revert-check fixture
import mutation  # noqa: E402
import verify_ac  # noqa: E402

#: The verify_ac names the deleted test-plan block defined. None may survive, and no caller may
#: reach one through the module.
HELPERS = (
    "testplan_derive", "testplan_probe", "testplan_row_faults", "testplan_rows_by_criterion",
    "testplan_unnameable", "testplan_unauthored", "testplan_unauthored_note", "_testplan_rows",
    "TESTPLAN_UNAUTHORED_NOTE", "TESTPLAN_OVERLAP_CEILING", "UNNAMEABLE", "cmd_testplan",
    "record_ruling", "withdraw_ruling", "read_rulings", "live_ruling", "ruling_digest",
    "ruling_path", "_replace_testplan", "_split_cells",
)

#: The nodes this story deletes, by module path. AC5 asserts each is gone and that no stamped
#: selector still names one.
DELETED = {
    "scripts/tests/test_verify_ac.py": (
        "TestPlanDeriveTests", "EditVerbVocabularyTests", "MultiRowTestPlanTests",
        "UnnameableRowTests", "TestPlanCellEscapingTests", "TestPlanProbeTests",
        "PlanRulingTests", "PlaceholderRowsAreReportedTests",
        "test_an_unnameable_row_beside_a_nameable_one_does_not_exempt",
        "test_a_plan_row_naming_a_bare_production_filename_does_not_exempt",
        "test_a_plan_row_naming_a_non_source_production_file_does_not_exempt",
        "test_a_plan_row_naming_only_test_code_still_exempts"),
    "scripts/tests/test_mutation.py": (
        "RowKeyedJoinTests", "FromPlanTests",
        "test_the_join_the_terminal_gate_reads_judges_a_row_by_its_own_site",
        "test_a_withdrawn_verdict_stops_holding_the_plan"),
    "tools/tests/test_batch_plan_shape.py": ("BatchPlanShapeTests",),
}

_PLAN = ("## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
         "| AC1 | unnameable: the criterion pins an ordering no single edit can reverse without "
         "also deleting the field it orders | it holds |\n"
         "| AC2 | in `notes.txt`, drop the marker so `rg x \\| wc` counts none | it reports |\n")


def _path(rel: str) -> Path:
    return (SKILL / rel) if rel.startswith("scripts/") else (REPO / rel)


def _nodes(module: Path) -> set:
    """Every class and function name the test module defines; nothing when it is gone."""
    if not module.is_file():
        return set()
    tree = ast.parse(module.read_text(encoding="utf-8"))
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef))}


def _names_deleted(verifier: str, rel: str, names: set) -> bool:
    """Does a pytest selector name a node this story deletes? A `mod::` node id does when one of
    its parts is a deleted name; a `-k` expression does when, evaluated as pytest evaluates it
    (a word matches any name containing it), it selects nothing the module still defines. A
    selector on a module that no longer exists names deleted nodes whatever else it says."""
    if not _path(rel).is_file():
        return True
    mod = rel.rsplit("/", 1)[1]
    if " -k " in f" {verifier} ":
        expr = verifier.split("-k", 1)[1].strip().strip("'\"")
        py = re.sub(r"[A-Za-z_][A-Za-z0-9_]*",
                    lambda m: m.group(0) if m.group(0) in ("and", "or", "not")
                    else str(any(m.group(0) in n for n in names)), expr)
        return not eval(py, {"__builtins__": {}})  # noqa: S307 - True/False/and/or/not only
    parts = {p for t in verifier.split() if f"tests/{mod}" in t for p in t.split("::")[1:]}
    return bool(parts & set(DELETED[rel]))


def _cli(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), *argv],
                          capture_output=True, text=True, check=False, timeout=300)


def _tree(root: Path) -> dict:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(root).parts}


class TestPlanToolingGoneTests(unittest.TestCase):
    def test_the_testplan_verb_is_retired(self) -> None:
        """AC1. MUTANTS: delete the parser without naming the verb retired (each action then
        exits 2 on a usage error that says nothing of the plan); a deletion that makes `run`
        read a legacy `## Test Plan` section (the control then stops verifying green)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (root / "notes.txt").write_text("marker\n", encoding="utf-8")
            story = stories / "US0001-a-story.md"
            story.write_text(
                "# US0001: a story\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
                "### AC1: it holds\n\n- **Verify:** grep marker notes.txt\n\n"
                "### AC2: it reports\n\n- **Verify:** grep marker notes.txt\n\n"
                + _PLAN + "\n## Revision History\n", encoding="utf-8")
            before = _tree(root)
            for action in ("derive", "probe", "rule", "withdraw"):
                with self.subTest(action=action):
                    r = _cli("testplan", action, "--unit", "US0001", "--criterion", "AC1",
                             "--reason", "a reason long enough to be recorded", "--author", "a",
                             "--root", str(root))
                    self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                    self.assertIn("retired", r.stderr)
                    self.assertIn("criteria and their Verify selectors", r.stderr)
                    self.assertNotIn("usage:", r.stderr)
                    self.assertEqual(before, _tree(root), f"`testplan {action}` wrote something")
            h = _cli("--help")
            self.assertEqual(h.returncode, 0, h.stderr)
            self.assertNotIn("testplan", h.stdout)

            # THE CONTROL: the legacy section is plain text to `run`, which verifies green.
            r = _cli("run", "--story", "US0001", "--root", str(root))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            text = story.read_text(encoding="utf-8")
            self.assertEqual(text.count("**Verified:** yes"), 2, text)
            self.assertIn(_PLAN, text, "the legacy Test Plan section was rewritten")

    def test_no_caller_reaches_a_testplan_helper(self) -> None:
        """AC2. MUTANTS: keep `mutation.plan_execution`; delete the helpers while
        `revert_exemptions` still reads plan rows (it then raises); keep the `unnameable`
        plan-row exemption (the legacy row then exempts AC2)."""
        for name in HELPERS:
            self.assertFalse(hasattr(verify_ac, name), f"verify_ac.{name} survives")
        for name in ("plan_execution", "cmd_from_plan"):
            self.assertFalse(hasattr(mutation, name), f"mutation.{name} survives")
        for script in ("mutation", "sprint", "critic"):     # the three AC2 names
            tree = ast.parse((SCRIPTS / f"{script}.py").read_text(encoding="utf-8"))
            aliases = {"verify_ac"} | {a.asname for n in ast.walk(tree)
                                      if isinstance(n, ast.Import) for a in n.names
                                      if a.name == "verify_ac" and a.asname}
            hits = [n.lineno for n in ast.walk(tree)
                    if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                        and n.value.id in aliases and n.attr in HELPERS)
                    or (isinstance(n, ast.Name) and n.id in ("plan_execution", "cmd_from_plan"))
                    or (isinstance(n, ast.Constant) and n.value == "testplan")]
            self.assertEqual(hits, [], f"{script} still reaches a testplan helper")

        exempt = "> **Revert-check-exempt:** AC1 - the paired control asserts the behaviour " \
                 "that stood before the change, so it stays green without it\n"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scripts").mkdir()
            prod = root / "scripts" / "prod.py"
            prod.write_text("BASE_ONLY = 1\n", encoding="utf-8")
            for args in (("init", "-q"), ("config", "user.email", "t@example.com"),
                         ("config", "user.name", "t"), ("add", "-A"), ("commit", "-qm", "base")):
                gitutil.git(list(args), root)
            base = gitutil.git(["rev-parse", "HEAD"], root).stdout.decode().strip()
            prod.write_text('BASE_ONLY = 1\nSHIPPED = "SHIPPED"\n', encoding="utf-8")
            gitutil.git(["commit", "-qam", "ship"], root)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US9001-x.md").write_text(
                "# US9001: x\n\n> **Status:** Review\n" + exempt
                + "> **Affects:** scripts/prod.py\n\n## Acceptance Criteria\n\n"
                "- [ ] **AC1** the control holds\n  - **Verify:** grep BASE_ONLY scripts/prod.py\n"
                "- [ ] **AC2** the legacy row\n  - **Verify:** grep BASE_ONLY scripts/prod.py\n\n"
                + _PLAN.replace("| AC2 | in", "| AC3 | in").replace("| AC1 | unnameable",
                                                                    "| AC2 | unnameable"),
                encoding="utf-8")
            # AC2 is the only criterion left to measure, so it staying green is the refusal; an
            # exempted AC2 would leave nothing measurable and exit 3 instead.
            r = _cli("revert-check", "--unit", "US9001", "--root", str(root), "--base", base)
            out = r.stdout + r.stderr
            self.assertRegex(out, r"AC1\s+exempt", out)
            self.assertNotRegex(out, r"AC2\s+exempt", "a legacy `unnameable` row exempted")
            self.assertIn("stayed GREEN", out)
            self.assertEqual(r.returncode, 1, out)

    def test_the_shape_tool_is_gone_and_rulings_are_frozen(self) -> None:
        """AC3. MUTANTS: keep `tools/batch_plan_shape.py`; keep a shipped script that writes
        `plan-rulings.md`. The file is frozen because nothing writes it any more; this story's
        diff leaves its bytes untouched, which is the byte-identical half of the criterion, and
        no hash is pinned here, so a later deliberate edit is not refused."""
        for rel in ("tools/batch_plan_shape.py", "tools/tests/test_batch_plan_shape.py"):
            self.assertFalse((REPO / rel).exists(), f"{rel} survives")
        self.assertTrue((REPO / "sdlc-studio" / "reviews" / "plan-rulings.md").is_file(),
                        "the ruling history was deleted rather than kept")
        writers = [p.name for p in SCRIPTS.glob("*.py") if "plan-rulings" in p.read_text(
            encoding="utf-8")]
        self.assertEqual(writers, [], "a shipped script still names the ruling file")

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC4. MUTANTS: leave the surface page un-regenerated; leave `test_surface.py`
        asserting `testplan derive`."""
        page = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertNotIn("verify_ac.py testplan", page)
        self.assertIn("`verify_ac.py coverage rule`", page)
        pinned = (SCRIPTS / "tests" / "test_surface.py").read_text(encoding="utf-8")
        self.assertIn('assertIn("coverage rule", surface.verbs().get("verify_ac.py", []))', pinned)
        self.assertNotIn('"testplan derive", surface.verbs()', pinned)
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "docgen.py"), "surface",
                            "--check"], capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("0 drift", r.stdout)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: keep one deleted class (its node is then still defined); retire one
        criterion fewer (its stamped selector then names a node that is gone)."""
        names = {rel: _nodes(_path(rel)) for rel in DELETED}
        for rel, deleted in DELETED.items():
            self.assertEqual(sorted(set(deleted) & names[rel]), [], rel)
        dead, read = [], 0
        mods = {rel: rel.rsplit("/", 1)[1] for rel in DELETED}
        for path in sorted((REPO / "sdlc-studio").rglob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if not any(m in text for m in mods.values()):
                continue
            for block in verify_ac.criteria_blocks(text):
                verifier = block.verifier or ""
                if (block.verified_state or "").strip().lower() != "yes":
                    continue
                rel = (next((r for r, m in mods.items() if f"tests/{m}" in verifier), None)
                       if verifier.startswith("pytest ") else None)
                read += bool(rel)
                if rel and _names_deleted(verifier, rel, names[rel]):
                    dead.append(f"{path.name[:6]} {block.ac_id}: {verifier}")
        self.assertGreater(read, 50, "the scan read no stamped selector, so it proves nothing")
        self.assertEqual(dead, [], "\n".join(dead))


if __name__ == "__main__":
    unittest.main()
