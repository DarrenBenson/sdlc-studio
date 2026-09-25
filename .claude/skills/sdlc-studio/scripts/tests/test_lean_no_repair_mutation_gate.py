"""US0935: a repair reaches Fixed on green criteria and its review, with no mutation evidence.

The repair lane is gone: no registered mutant is demanded at the terminal transition, no survivor
bug is filed, and `review.mutation_evidence` is no longer a setting. The criteria gate stays, so a
red criterion still refuses. `mutation.py run` remains an on-demand tool.

The first test drives the shipped entry points as subprocesses against throwaway git workspaces.
The last reads this repository's own artefacts, because its criterion names them.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import critic  # noqa: E402
import mutation  # noqa: E402
import transition  # noqa: E402
import validate  # noqa: E402
from gitutil import git  # noqa: E402
from lib import sdlc_md  # noqa: E402
# The stamp derivation US0916 built, reused rather than copied: the same deleted-node reading
# and the same `-k` matching, so the two retirement checks cannot disagree about a selector.
from test_lean_no_two_role import (REPO, _git, _live_stamps, _string_reads,  # noqa: E402
                                   _test_nodes)

#: The repair lane's functions, which AC3 names.
DELETED = ("is_repair_unit", "mutation_evidence_lane", "_ledger_contradiction",
           "repair_mutation_gate", "_file_surviving_mutants")
#: The test classes AC4 names. The full deleted set is DERIVED (`_deleted_nodes`); these only prove
#: the derivation is looking at the right base, since each must appear in it.
AC4_NAMED = {"test_transition.py": ("SurvivorGateTests", "RepairMutationGateTests",
                                    "RepairScopeTests", "MutationEvidenceLaneCLITests",
                                    "NoSurfaceExemptionCLITests", "MeasuredEvidenceCLITests",
                                    "SurvivorFilingCLITests"),
             "test_check_spec_claims.py": ("DoctrineTests",),
             "test_mutation.py": ("CrossProvenanceContradictionTests",)}
#: Both test trees: the rule 21 guard lived under tools/.
TEST_DIRS = (TESTS.relative_to(REPO).as_posix(), "tools/tests")

_BUG = ("# {id}: a repair\n\n> **Status:** In Progress\n> **Severity:** Medium\n"
        "> **Affects:** src/thing.py\n> **Verification depth:** functional\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c\n"
        "  - **Verify:** shell {verdict}\n")


def _run(script: str, *argv: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=300)


def _repair_workspace(d: str, mode: str, bugs: dict[str, str]) -> Path:
    """A git workspace whose open run's diff changes Python, holding one repair bug per entry of
    `bugs` (id -> `true` or `false` for its one Verify line), with no registered mutant. The
    project sets `review.mutation_evidence: <mode>`, the one setting the deleted lane read."""
    root = Path(d)
    sd = root / "sdlc-studio"
    (sd / "bugs").mkdir(parents=True)
    (sd / ".local").mkdir()
    (root / "src").mkdir()
    (sd / ".config.yaml").write_text(f"review:\n  mutation_evidence: {mode}\n", encoding="utf-8")
    for uid, verdict in bugs.items():
        (sd / "bugs" / f"{uid}-a-repair.md").write_text(_BUG.format(id=uid, verdict=verdict),
                                                        encoding="utf-8")
    src = root / "src" / "thing.py"
    src.write_text("def g(a, b):\n    if a == b:\n        return 1\n    return 2\n",
                   encoding="utf-8")
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    git(["init", "-q", "-b", "main"], cwd=root)
    git(["add", "-A"], cwd=root)
    git(["commit", "-qm", "base"], cwd=root)
    base = git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()
    src.write_text("def g(a, b):\n    if a == b:\n        return 1\n    return 3\n",
                   encoding="utf-8")
    git(["commit", "-qam", "the repair"], cwd=root)
    (sd / ".local" / "run-state.json").write_text(json.dumps(
        {"run_id": "RUN-TEST01", "outcome": "running", "batch": list(bugs),
         "base_ref": base}), encoding="utf-8")
    for uid in bugs:
        critic.record_verdict(root, uid, "APPROVE", "rev", "dev")
        _run("verify_ac.py", "run", "--id", uid, root=root)
    return root


def _status(path: Path) -> str:
    m = re.search(r"^> \*\*Status:\*\* (.+)$", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else ""


def _base_ref() -> str | None:
    """The parent of the commit that added this module, or HEAD while it is uncommitted."""
    try:
        rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    added = _git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


def _deleted_nodes(base: str) -> dict[str, dict[str, set]]:
    """Per test module changed since `base` in either test tree: the nodes it defined there and
    no longer defines (`gone`), and the nodes it defines now (`now`)."""
    out: dict[str, dict[str, set]] = {}
    for name in (_git("diff", "--name-only", base, "--", *TEST_DIRS) or "").split():
        if not (Path(name).name.startswith("test_") and name.endswith(".py")):
            continue
        old = _git("show", f"{base}:{name}")
        if old is None:
            continue
        path = REPO / name
        now = _test_nodes(path.read_text(encoding="utf-8")) if path.exists() else set()
        gone = _test_nodes(old) - now
        if gone:
            out[Path(name).name] = {"gone": gone, "now": now}
    return out


def _rule_21(text: str) -> str:
    """Rule 21's own text, from its numbered heading to the next rule or top-level heading."""
    m = re.search(r"^21\. \*\*.+$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    end = re.search(r"^(?:## |\d+\. \*\*)", rest, re.M)
    return text[m.start():m.end() + (end.start() if end else len(rest))]


class RepairMutationGateGoneTests(unittest.TestCase):
    def test_a_repair_needs_no_mutation_evidence(self) -> None:
        """AC1. MUTANTS: HEAD's `repair_mutation_gate` under `block` (the green repair is refused
        for carrying no mutation evidence); HEAD's survivor filing under `report` (a second bug is
        minted for the survived row); and a deletion that takes the Verify gate with it (the red
        repair reaches Fixed)."""
        with tempfile.TemporaryDirectory() as d:
            root = _repair_workspace(d, "block", {"BG0001": "true", "BG0002": "false"})
            bugs = root / "sdlc-studio" / "bugs"
            r = _run("transition.py", "set", "BG0001", "Fixed", root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            self.assertEqual(_status(bugs / "BG0001-a-repair.md"), "Fixed")
            self.assertNotIn("mutation", out.lower())

            r = _run("transition.py", "set", "BG0002", "Fixed", root=root)
            out = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("red (AC1)", out)
            self.assertEqual(_status(bugs / "BG0002-a-repair.md"), "In Progress")

        with tempfile.TemporaryDirectory() as d:
            root = _repair_workspace(d, "report", {"BG0001": "true"})
            src = root / "src" / "thing.py"
            import hashlib
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(json.dumps(
                {"version": 1, "dropped": 0, "entries": [{
                    "target": "src/thing.py", "provenance": "registered",
                    "hash": hashlib.sha256(src.read_bytes()).hexdigest(),
                    "mutants": [{"unit": "BG0001", "criterion": "AC1", "verdict": "survived",
                                 "line": 4, "mutant": "return 3 -> return 2",
                                 "test": "shell true"}]}]}), encoding="utf-8")
            r = _run("transition.py", "set", "BG0001", "Fixed", root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            bugs = sorted(p.name for p in (root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(bugs, ["BG0001-a-repair.md"], f"a survivor bug was filed: {bugs}")
            self.assertNotIn("survivor", out.lower())

    def test_the_mutation_evidence_key_and_tag_are_retired(self) -> None:
        """AC2. MUTANTS: delete `repair.mutation-evidence` from `DOR_DOD_CHECK_IDS` without adding
        it to `RETIRED_CHECK_IDS` (validate then refuses the tag as unknown); keep the key in
        config-defaults; keep `mutation.evidence_mode`."""
        import yaml
        defaults = SCRIPTS.parent / "templates" / "config-defaults.yaml"
        text = defaults.read_text(encoding="utf-8")
        review = (yaml.safe_load(text) or {}).get("review") or {}
        self.assertNotIn("mutation_evidence", review)
        self.assertIsNone(re.search(r"^\s*mutation_evidence\s*:", text, re.M))
        shipped = sorted([*SCRIPTS.glob("*.py"), *(SCRIPTS / "lib").glob("*.py")])
        self.assertGreater(len(shipped), 20, "the scan is looking in the wrong place")
        readers = [p.name for p in shipped
                   if any("mutation_evidence" in s for s in _string_reads(p))]
        self.assertEqual(readers, [], "a shipped script still reads review.mutation_evidence")
        for name in ("evidence_mode", "EVIDENCE_MODES", "EVIDENCE_MODE_DEFAULT"):
            self.assertFalse(hasattr(mutation, name), f"mutation.{name} survives")

        cid = "repair.mutation-evidence"
        self.assertIn(cid, sdlc_md.RETIRED_CHECK_IDS)
        self.assertNotIn(cid, sdlc_md.DOR_DOD_CHECK_IDS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- [ ] ACs pass [check: story.verify-ac]\n"
                f"- [ ] a repair carries a killed mutant [check: {cid}]\n", encoding="utf-8")
            r = _run("validate.py", "check", root=root)
            out = r.stdout + r.stderr
            findings = validate.check_dor_dod(root)
            self.assertEqual(r.returncode, 0, out)
            self.assertNotIn("unknown-check-id", out)
            hit = [f for f in findings if f"[check: {cid}]" in f["message"]]
            self.assertEqual(len(hit), 1, findings)
            self.assertEqual(hit[0]["rule"], "retired-check-id")
            self.assertNotEqual(hit[0]["severity"], validate.SEVERITY_ERROR)
            self.assertIn("migrate", hit[0]["message"])

    def test_the_repair_lane_is_deleted(self) -> None:
        """AC3. MUTANTS: unwire the lane at `_pre_write_gates` but leave the functions defined;
        leave rule 21 naming `transition.py` or the setting as its enforcing mechanism."""
        source = (SCRIPTS / "transition.py").read_text(encoding="utf-8")
        defined = {n.name for n in ast.walk(ast.parse(source))
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertIn("_pre_write_gates", defined, "the scan is reading the wrong module")
        for name in DELETED:
            with self.subTest(name=name):
                self.assertNotIn(name, defined)
                self.assertFalse(hasattr(transition, name), f"transition.{name} survives")
        doctrine = (SCRIPTS.parent / "reference-doctrine.md").read_text(encoding="utf-8")
        rule = _rule_21(doctrine)
        self.assertIn("{#repair-evidence}", rule, "rule 21 was not found where it was")
        self.assertIn("mutant", rule.lower(), "the slice holds some other rule")
        for gate in ("transition.py", "review.mutation_evidence", "verify_no_surface_claim",
                     *DELETED):
            with self.subTest(gate=gate):
                self.assertNotIn(gate, rule, "rule 21 still names an enforcing gate")

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC4. MUTANTS: leave a retired criterion's `Verified: yes` stamp in place, as a node id or
        as a `-k` selector naming a deleted method; keep a deleted class in its module.

        The deleted nodes are DERIVED: every class and `test_` function a changed test module (in
        the skill's tests or `tools/tests`) defined at the base and no longer defines, the base
        being the parent of the commit that added this module (HEAD while it is uncommitted)."""
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = _deleted_nodes(base)
        for module, classes in AC4_NAMED.items():
            gone = deleted.get(module, {}).get("gone", set())
            for cls in classes:
                self.assertIn((cls, ""), gone, f"{module}::{cls} was to be deleted ({base})")
        tr = ".claude/skills/sdlc-studio/scripts/tests/test_transition.py"
        controls = {
            "node-id": ([f"- **Verify:** pytest {tr}::SurvivorFilerTests",
                         "- **Verified:** yes (2026-08-20)"], ["node-id:1"]),
            "k": ([f"- **Verify:** pytest {tr} -k an_explicit_return_none_is_a_none_path",
                   "- **Verified:** yes (2026-08-20)"], ["k:1"]),
            "retired": ([f"- **Verify:** pytest {tr}::SurvivorFilerTests",
                         "- **Verified:** manual (2026-09-25) - retired, superseded by US0935"],
                        []),
        }
        for label, (lines, want) in controls.items():
            self.assertEqual(_live_stamps([(label, lines)], deleted), want, label)
        artefacts = REPO / "sdlc-studio"
        if not artefacts.is_dir():
            self.skipTest("no sdlc-studio/ artefacts in this checkout")
        live = _live_stamps(((path.relative_to(REPO), path.read_text(
            encoding="utf-8", errors="replace").splitlines())
            for path in sorted(artefacts.rglob("*.md"))), deleted)
        self.assertEqual(live, [], "a live stamp selects only deleted test nodes")


if __name__ == "__main__":
    unittest.main()
