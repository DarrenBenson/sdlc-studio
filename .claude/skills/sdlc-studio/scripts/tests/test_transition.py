"""Unit tests for transition.py - status transition + index/epic cascade (CR0042).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import contextlib
import re
import io
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tr = _load("transition", "transition.py")
rc = _load("reconcile", "reconcile.py")
transition = tr
sprint = _load("sprint", "sprint.py")
sys.path.insert(0, str(DIR / "lib"))
import sdlc_md  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402


def _repo(root: Path) -> Path:
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    (sd / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
        "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n", encoding="utf-8")
    (sd / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Ready | 1 |\n| In Progress | 0 |\n| Done | 0 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
    ed = root / "sdlc-studio" / "epics"
    ed.mkdir(parents=True)
    (ed / "EP0001-e.md").write_text(
        "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
        "- [ ] [US0001: s](../stories/US0001-x.md)\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
    return root


def _read(root, *parts):
    return (root.joinpath("sdlc-studio", *parts)).read_text(encoding="utf-8")


def _cli(root, *argv) -> tuple[int, str]:
    """Drive `transition.py` through its SHIPPED ENTRY POINT. `(exit_code, output)`.

    ONE driver for the whole module, because the wiring between entry point and function is
    exactly what a library test does not exercise - the scar BG0541 was filed for, where
    `repair_mutation_gate` returned STALE from the library while `transition.py set` exited 0.
    A criterion whose When names the command and whose Verify calls the function is testing a
    different claim from the one it states.

    stdout and stderr are merged, because a refusal reaches the reader on stderr and a success
    line on stdout, and a test that reads only one of them can assert nothing about the other.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            code = tr.main(["--root", str(root), *argv])
        except SystemExit as exc:                     # argparse's own exits
            code = int(exc.code or 0)
    return code, buf.getvalue()


def _git_repo(root: Path) -> None:
    """A real git repository with one commit, so a diff against a base ref exists.

    The exemption is re-derived from git's diff rather than from the author's own declaration,
    so a `tmpdir` with no repository takes the could-not-be-established arm and refuses for a
    reason the criteria are not about. A test asserting only a non-zero exit cannot tell that
    refusal from the one it wants, which is why every assertion below names the message.

    Through `gitutil.git`, never a raw `subprocess.run(["git", ...])`: the shared helper fences
    upward repository discovery at the temp root and neutralises host config, and the repo's
    own sweep freezes the count of unconfined callers at zero.
    """
    gitutil.git(["init", "-q", "-b", "main"], cwd=root)
    (root / ".gitignore").write_text("", encoding="utf-8")
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "base"], cwd=root)


def _git_commit(root: Path, message: str = "change") -> None:
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", message], cwd=root)


def _head(root: Path) -> str:
    return gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()


class VerdictErrorNamesAnnotateTests(unittest.TestCase):
    """`set --author X` without the verdict pair is an identity-only stamp gone to the
    wrong verb. The all-or-none refusal must name `transition annotate` - the verb
    that exists for exactly that - so the actor is not left to re-derive it."""

    def test_author_without_verdict_pair_names_annotate(self) -> None:
        import io
        from contextlib import redirect_stderr
        args = tr.build_parser().parse_args(
            ["set", "--id", "US0001", "--status", "Fixed", "--author", "dani"])
        buf = io.StringIO()
        with redirect_stderr(buf):
            rc_val = tr.cmd_set(args)
        self.assertEqual(rc_val, 2)
        self.assertIn("annotate", buf.getvalue())


class TransitionTests(unittest.TestCase):
    def test_sets_status_syncs_index_and_ticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            self.assertEqual((res["from"], res["to"]), ("Ready", "Done"))
            self.assertIn("> **Status:** Done", _read(root, "stories", "US0001-x.md"))
            idx = _read(root, "stories", "_index.md")
            self.assertIn("| [US0001](US0001-x.md) | s | Done |", idx)   # row synced
            self.assertIn("| Done | 1 |", idx)                          # counts recomputed
            self.assertIn("| Ready | 0 |", idx)
            self.assertIn("- [x] [US0001: s]", _read(root, "epics", "EP0001-e.md"))  # epic ticked
            self.assertEqual(res["epic"], "EP0001")
            self.assertEqual(rc.detect_type("story", root)["drift"], [])  # 0 drift after

    def test_reopen_unticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            tr.transition(root, "US0001", "In Progress")
            self.assertIn("- [ ] [US0001: s]", _read(root, "epics", "EP0001-e.md"))
            self.assertIn("> **Status:** In Progress", _read(root, "stories", "US0001-x.md"))
            self.assertEqual(rc.detect_type("story", root)["drift"], [])

    def test_invalid_status_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Frozen")

    def test_unknown_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US9099", "Done")

    def test_dry_run_writes_nothing(self) -> None:
        # `In Progress`, not `Done`. This story declares an executable AC that has never been
        # verified, so a Done dry-run now correctly REFUSES (BG0213) - it used to pass, which
        # is precisely the dishonesty that bug was about. The write-nothing property being
        # asserted here needs a transition that is actually allowed; the refused case is
        # covered by DryRunHonestyTests.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before_story = _read(root, "stories", "US0001-x.md")
            before_idx = _read(root, "stories", "_index.md")
            before_epic = _read(root, "epics", "EP0001-e.md")
            res = tr.transition(root, "US0001", "In Progress", dry_run=True)
            self.assertEqual(res["to"], "In Progress")
            self.assertEqual(_read(root, "stories", "US0001-x.md"), before_story)
            self.assertEqual(_read(root, "stories", "_index.md"), before_idx)
            self.assertEqual(_read(root, "epics", "EP0001-e.md"), before_epic)

    def test_inline_status_field_preserved(self) -> None:
        # House inline `· **Status:** X · **Epic:** Y` form: only the Status value changes.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text("# US0001: s\n\n> **Status:** Ready · **Epic:** EP0001 · **Points:** 3\n\n"
                          "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
                          encoding="utf-8")
            tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            line = next(ln for ln in sp.read_text(encoding="utf-8").splitlines() if "Status" in ln)
            self.assertIn("**Status:** Done", line)
            self.assertIn("**Epic:** EP0001", line)   # neighbours intact
            self.assertIn("**Points:** 3", line)


class SurvivorGateTests(unittest.TestCase):
    """US0565: the gate is the SURVIVOR count over the changed lines, not the run's exit status.

    A mutation run that completes is evidence a run happened and says nothing about what it
    found. And `survivors == 0` over an EMPTY mutant set is vacuous - the same shape as a clean
    pass over criteria nobody read, one instrument over.
    """

    def _repo(self, d, mutants):
        """Build the fixture UNDER `d`, and refuse to build it anywhere else.

        A placeholder call left in this class passed `"."` and wrote `src/thing.py`, a fake
        `sdlc-studio/bugs/BG0001-x.md` and - worst - `sdlc-studio/.local/mutation-runs.json`
        into the REAL repository on every run, destroying 23 recorded mutation registrations.
        A test fixture that can address the working tree will eventually write to it, so this
        refuses rather than trusting every caller to pass a temp path.
        """
        import json, hashlib
        root = Path(d).resolve()
        if not str(root).startswith(tempfile.gettempdir()):
            raise AssertionError(
                f"fixture root {root} is outside {tempfile.gettempdir()} - a test fixture must "
                f"never be able to write into the working tree")
        (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(parents=True, exist_ok=True)
        src = root / "src" / "thing.py"
        src.write_text("def g(a, b):\n    if a == b:\n        return 1\n", encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
            "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Affects:** src/thing.py\n> **Points:** 3\n", encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(json.dumps(
            {"entries": [{"target": "src/thing.py",
                          "hash": hashlib.sha256(src.read_bytes()).hexdigest(),
                          "mutants": mutants}]}), encoding="utf-8")
        return str(root), (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(
            encoding="utf-8")

    def test_a_completed_run_with_one_survivor_refuses(self) -> None:
        """Mutant: judge on the run's exit status instead of the survivor count - a run that
        completed cleanly while a mutant lived reads as evidence."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, [
                {"unit": "BG0001", "criterion": "AC1", "verdict": "killed"},
                {"unit": "BG0001", "criterion": "AC2", "verdict": "survived",
                 "line": 2, "mutant": "invert the guard"}])
            r = tr.repair_mutation_gate(root, "BG0001", text)
            self.assertIsNotNone(r, "a run carrying a survivor was accepted")
            self.assertIn("SURVIVED", r)

    def test_the_refusal_names_each_survivor_with_its_file_line_and_mutation(self) -> None:
        """The finding is about the TEST, so the message must point at what is missing rather
        than at the mutant alone. Mutant: report only a count - the author is told a number and
        has to go looking for which assertion is absent."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, [
                {"unit": "BG0001", "criterion": "AC1", "verdict": "survived",
                 "line": 2, "mutant": "invert the guard"}])
            r = tr.repair_mutation_gate(root, "BG0001", text)
            self.assertIn("src/thing.py", r, "the refusal names no file")
            self.assertIn(":2", r, "the refusal names no line")
            self.assertIn("invert the guard", r, "the refusal names no applied mutation")
            self.assertIn("about the TEST", r)

    def test_an_empty_mutant_set_is_refused_not_passed(self) -> None:
        """THE VACUOUS ZERO. Mutant: pass when survivors == 0 without checking that anything was
        applied - a record with no mutants at all opens the gate, which is `ac=0 pass=0` reading
        as a clean pass, one instrument over."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, [])
            empty = tr.repair_mutation_gate(root, "BG0001", text)
            self.assertIsNotNone(empty, "an empty mutant set passed on a zero survivor count")
            # AC4 asks for the DISTINCTION, so assert it: "nothing to mutate" and "nothing
            # survived" have different fixes, and a record whose mutants are all equivalent is
            # a third state again - a run that applied things and judged none of them.
            root2, text2 = self._repo(d + "/b", [
                {"unit": "BG0001", "criterion": "AC1", "verdict": "equivalent",
                 "reason": "unreachable"}])
            vacuous = tr.repair_mutation_gate(root2, "BG0001", text2)
            self.assertIsNotNone(vacuous)
            self.assertNotEqual(empty, vacuous,
                                "an absent record and a record that judged nothing read alike")
            self.assertIn("NO mutation evidence", empty)
            self.assertIn("vacuous", vacuous)

    def test_zero_survivors_over_a_non_empty_set_passes(self) -> None:
        """THE POSITIVE CONTROL: a gate refusing every repair satisfies all three criteria above
        while stopping repair work entirely. Mutant: refuse whatever the record says."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, [
                {"unit": "BG0001", "criterion": "AC1", "verdict": "killed"},
                {"unit": "BG0001", "criterion": "AC2", "verdict": "killed"}])
            self.assertIsNone(tr.repair_mutation_gate(root, "BG0001", text),
                              "two killed mutants over the current bytes were refused")

    def test_an_equivalent_mutant_is_excluded_not_counted_as_a_kill(self) -> None:
        """An equivalent mutant cannot be killed by any test, so counting it as one inflates the
        evidence. Mutant: count it toward `applied` - a record of nothing but equivalents opens
        the gate on a set where nothing was ever judged."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, [
                {"unit": "BG0001", "criterion": "AC1", "verdict": "equivalent",
                 "reason": "unreachable branch"}])
            r = tr.repair_mutation_gate(root, "BG0001", text)
            self.assertIsNotNone(r, "a record of only equivalent mutants opened the gate")
            self.assertIn("vacuous", r)


class RepairMutationGateTests(unittest.TestCase):
    """US0564: a repair carries mutation evidence over its OWN changed lines, re-read from the
    record, and a record about bytes the file no longer has is STALE rather than green."""

    def _repo(self, d, *, record=None, body="def g(a, b):\n    if a == b:\n        return 1\n"):
        import json, hashlib
        root = Path(d)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(parents=True, exist_ok=True)
        src = root / "src" / "thing.py"
        src.write_text(body, encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
            "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            "> **Affects:** src/thing.py\n> **Points:** 3\n", encoding="utf-8")
        if record is not None:
            digest = (hashlib.sha256(src.read_bytes()).hexdigest() if record == "current"
                      else "0" * 64)
            (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(json.dumps(
                {"entries": [{"target": "src/thing.py", "hash": digest,
                              "mutants": [{"unit": "BG0001", "criterion": "AC1",
                                           "verdict": "killed"}]}]}), encoding="utf-8")
        return root, (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")

    def test_a_repair_without_mutation_evidence_is_refused(self) -> None:
        """Mutant: return None when no record exists - the demand is a comment."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d)
            r = tr.repair_mutation_gate(str(root), "BG0001", text)
            self.assertIsNotNone(r, "a repair with no mutation evidence was let through")
            self.assertIn("NO mutation evidence", r)
            self.assertIn("register --unit BG0001", r, "the refusal names no command")

    def test_an_asserted_pass_without_a_record_is_refused(self) -> None:
        """The evidence is READ, never accepted. Mutant: trust a caller-supplied claim - the
        gate accepts the very thing it exists to check."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d)
            claimed = text + "\n> **Mutation-checked:** yes, all mutants killed\n"
            self.assertIsNotNone(tr.repair_mutation_gate(str(root), "BG0001", claimed),
                                 "a prose claim of mutation evidence opened the gate")

    def test_a_record_predating_the_current_surface_is_stale(self) -> None:
        """STALE is distinct from ABSENT - different fixes, and a passing run banked against an
        earlier surface must not be spendable on this one.

        Mutant: ignore the hash - a gate you satisfy once, then edit freely behind.
        """
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, record="stale")
            r = tr.repair_mutation_gate(str(root), "BG0001", text)
            self.assertIsNotNone(r, "a record about bytes the file no longer has read as green")
            self.assertIn("STALE", r)
            self.assertIn("not absent", r, "stale is reported as if no record existed")

    def test_a_current_record_opens_the_gate(self) -> None:
        """THE POSITIVE CONTROL: a gate that refuses every repair satisfies the three criteria
        above and stops all repair work. Mutant: refuse whatever the record says."""
        with tempfile.TemporaryDirectory() as d:
            root, text = self._repo(d, record="current")
            self.assertIsNone(tr.repair_mutation_gate(str(root), "BG0001", text),
                              "evidence covering the current bytes was refused")


class RepairScopeTests(unittest.TestCase):
    """US0566: the mutation demand is scoped to REPAIRS, and the class is read from metadata.

    Feature work is already held by a test written before anyone knew which way the
    implementation would go. Only a repair's test is authored with the answer in hand, which is
    what the evidence indicts. A blanket demand on all work is the one that gets switched off
    wholesale, and then it holds nothing.
    """

    def test_a_feature_story_is_not_held_to_the_repair_bar(self) -> None:
        """Mutant: drop the scope so every unit is classed a repair - new capability is held to
        a bar its evidence does not indict, and the demand is switched off wholesale."""
        repair, why = tr.is_repair_unit(
            "story", "# US3: fix the regression in the parser\n\n"
                     "> **Status:** Ready\n> **Delivers:** CR0500\n")
        self.assertFalse(repair, why)

    def test_the_repair_class_is_derived_from_metadata_not_prose(self) -> None:
        """The fourth case is the one that matters: its TITLE says "fix the regression" and its
        provenance says feature work. A classifier reading words types it wrongly in the
        direction that costs most.

        Mutant: classify on the title text - the feature story becomes a repair and this reddens
        on it alone.
        """
        cases = [
            ("bug", "# BG1: x\n\n> **Status:** Open\n", True),
            ("story", "# US1: x\n\n> **Status:** Ready\n> **Parent:** BG0123\n", True),
            ("story", "# US2: x\n\n> **Status:** Ready\n> **Delivers:** RV0007\n", True),
            ("story", "# US3: fix the regression in the parser\n\n"
                      "> **Status:** Ready\n> **Delivers:** CR0500\n", False),
        ]
        for type_, text, expected in cases:
            with self.subTest(text=text.splitlines()[0]):
                got, why = tr.is_repair_unit(type_, text)
                self.assertEqual(got, expected, why)
                self.assertTrue(why, "the classification states no field it read")


def _lane_repo(d, *, mode=None, record="none", exemption=None, affects="src/thing.py",
               cutoff=True, mutants=None, py_change=True) -> Path:
    """A real git repo carrying one repair bug, for the mutation-evidence lane's CLI tests.

    `record`: "none" | "current" (a hash matching the file as it stands) | "stale".
    `mode`: what `review.mutation_evidence` says, or None to leave it unset.
    `cutoff`: whether `review.test_plan_after` is set, which governs a DIFFERENT gate - the
    lane must not inherit it, which is AC5.
    `py_change`: whether the commit AFTER the base ref touches Python. False gives a
    markdown-only diff, which is the only shape a genuine no-surface exemption can hold in -
    the surface is derived from the diff alone, so a docs repair sharing a diff with Python
    work is refused, deliberately and in the safe direction.
    """
    import hashlib
    root = Path(d)
    (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "thing.py").write_text(
        "def g(a, b):\n    if a == b:\n        return 1\n    return 2\n", encoding="utf-8")
    (root / "src" / "other.py").write_text(
        "def h(x, y):\n    if x > y:\n        return x\n    return y\n", encoding="utf-8")
    (root / "README.md").write_text("# prose only\n", encoding="utf-8")
    cfg = []
    if mode is not None:
        cfg.append(f"review:\n  mutation_evidence: {mode}\n")
    if cutoff:
        cfg.append("  test_plan_after: '2020-01-01'\n" if mode is not None
                   else "review:\n  test_plan_after: '2020-01-01'\n")
    if cfg:
        (root / "sdlc-studio" / ".config.yaml").write_text("".join(cfg), encoding="utf-8")
    (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
        "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** {affects}\n> **Points:** 3\n"
        "> **Verification depth:** functional (unit: the repaired branch, both ways)\n\n"
        "## Summary\n\ns\n\n## Acceptance Criteria\n\n"
        "- [x] **AC1:** the repaired branch behaves\n"
        "      **Verify:** shell echo ok\n", encoding="utf-8")
    (root / "sdlc-studio" / "bugs" / "_index.md").write_text(
        "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [BG0001](BG0001-x.md) | b | Open |\n", encoding="utf-8")
    _git_repo(root)
    base = _head(root)
    # A change AFTER the base ref, so the diff is non-empty and the derived surface exists.
    if py_change:
        (root / "src" / "thing.py").write_text(
            "def g(a, b):\n    if a == b:\n        return 1\n    return 3\n", encoding="utf-8")
    else:
        (root / "README.md").write_text("# prose only, edited\n", encoding="utf-8")
    _git_commit(root, "the repair")
    (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
        {"run_id": "RUN-TEST01", "outcome": "running", "batch": ["BG0001"],
         "base_ref": base}), encoding="utf-8")
    if record != "none":
        src = root / "src" / "thing.py"
        digest = (hashlib.sha256(src.read_bytes()).hexdigest() if record == "current"
                  else "0" * 64)
        rows = mutants if mutants is not None else [
            {"unit": "BG0001", "criterion": "AC1", "verdict": "killed", "line": 4,
             "mutant": "return 3 -> return 2", "test": "shell echo ok"}]
        (root / "sdlc-studio" / ".local" / "mutation-runs.json").write_text(json.dumps(
            {"version": 1, "dropped": 0,
             "entries": [{"target": "src/thing.py", "hash": digest,
                          "provenance": "registered", "mutants": rows}]}), encoding="utf-8")
    if exemption is not None:
        (root / "sdlc-studio" / ".local" / "no-mutatable-surface.json").write_text(
            json.dumps({"BG0001": {"paths": exemption}}), encoding="utf-8")
    return root


class MutationEvidenceLaneCLITests(unittest.TestCase):
    """BG0541: the SHIPPED VERB reaches the mutation-evidence lane, in the mode the project set.

    Every test here drives `transition.py set`. The whole bug is that the library refused and
    the command did not, and a criterion whose When names the command cannot be answered by a
    test that calls the function.
    """

    def test_the_command_refuses_what_the_library_refuses(self) -> None:
        """AC1. Mutant: delete the lane call from `_pre_write_gates` - the state of the tree
        this bug was filed against, where the CLI exited 0 on a ledger the library called
        STALE."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="stale")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "the command let through what the library refuses")
            self.assertIn("STALE", out, "the refusal does not name the state it found")
            self.assertIn("Status:** Open", _read(root, "bugs", "BG0001-x.md"),
                          "the artefact was written despite the refusal")

    def test_the_default_mode_reports_and_the_transition_proceeds(self) -> None:
        """AC2. Mutant: map the report mode onto the blocking arm - which would ship the hard
        bar CR0537 overruled, under the name of the mode that was chosen instead."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode=None, record="stale")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"the default mode blocked the transition:\n{out}")
            self.assertIn("Status:** Fixed", _read(root, "bugs", "BG0001-x.md"))
            self.assertIn("mutation-evidence advisory", out,
                          "the stale evidence passed without being reported, so the default "
                          "mode is silent rather than reporting")
            self.assertIn("STALE", out, "the advisory does not say what it found")

    def test_the_lane_runs_with_no_test_plan_cutoff_set(self) -> None:
        """AC5. Mutant: nest the lane call inside `_plan_gate_active` - it would then be inert
        in every project that never set `review.test_plan_after`, while a fixture setting both
        went green. That is this bug's own defect, one level in."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="stale", cutoff=False)
            self.assertNotIn(
                "test_plan_after",
                (root / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8"),
                "the fixture sets the cutoff, so it cannot show the lane runs without it")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "the lane stood down with no test-plan cutoff set, so "
                                         "it inherited a condition governing a different gate")
            self.assertIn("STALE", out)

    def test_sound_evidence_passes_and_off_refuses_nothing(self) -> None:
        """AC6, THE CONTROL. Every other criterion here is a refusal, so without this pair a
        lane that refuses every repair - or one that never fires at all - satisfies the plan.

        Mutant: append the lane's block whatever the lane returned.
        Mutant: emit the advisory in the `off` arm as well.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="current")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"sound evidence was refused under block:\n{out}")
            self.assertIn("Status:** Fixed", _read(root, "bugs", "BG0001-x.md"))
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="off", record="stale")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"`off` refused a transition:\n{out}")
            self.assertNotIn("mutation-evidence advisory", out,
                             "`off` emitted an advisory, so it is `report` under another name")

    def test_an_unrecognised_mode_is_refused_by_name(self) -> None:
        """A typo must not silently switch a project's hard bar off. Mutant: fall back to the
        default on an unrecognised value - `blcok` would then get `report`, which is the one
        outcome no reading of the operator's decision asks for."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="blcok", record="current")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "an unrecognised evidence mode was defaulted")
            self.assertIn("blcok", out, "the refusal does not quote the offending value")


class RepairMutationGateCLITests(unittest.TestCase):
    """US0564, re-verified through the SHIPPED COMMAND.

    Every criterion in this wave names `transition.py set` as its When while its verifier
    called the library function, so none of them could see that `_pre_write_gates` never
    reached the gate. That is BG0541, and this is the wave closing on the tests that would have
    caught it.
    """

    def test_a_repair_without_mutation_evidence_is_refused_by_the_command(self) -> None:
        """AC1. Mutant: return None when no record exists - the demand is a comment.
        The mode is named in the fixture: CR0537 makes reporting the default, so `block` is
        what this criterion is about."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a repair with no mutation evidence was let through")
            self.assertIn("NO mutation evidence", out)
            self.assertIn("register --unit BG0001", out, "the refusal names no command")
            self.assertIn("Status:** Open", _read(root, "bugs", "BG0001-x.md"))

    def test_an_asserted_pass_without_a_record_is_refused_by_the_command(self) -> None:
        """AC3. The evidence is READ, never accepted from the caller. Mutant: trust a claim in
        the artefact's own prose - the gate then accepts the very thing it exists to check."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            art = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            art.write_text(art.read_text(encoding="utf-8").replace(
                "> **Points:** 3\n",
                "> **Points:** 3\n> **Mutation-checked:** yes, all mutants killed\n"),
                encoding="utf-8")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a prose claim of mutation evidence opened the gate")
            self.assertIn("NO mutation evidence", out)

    def test_a_record_predating_the_current_surface_is_stale_through_the_command(self) -> None:
        """AC4. STALE is distinct from ABSENT - different fixes, and a passing run banked
        against an earlier surface must not be spendable on this one.

        Mutant: ignore the hash - a gate you satisfy once, then edit freely behind.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="stale")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code)
            self.assertIn("STALE", out, "a banked run was spent on a later surface")
            self.assertNotIn("NO mutation evidence", out,
                             "STALE was reported as absent, which has a different fix")


class SurvivorGateCLITests(unittest.TestCase):
    """US0565, re-verified through the shipped command: the gate is the SURVIVOR count over the
    changed lines, not the fact that a run happened."""

    def _repo(self, d, mutants, mode="block"):
        return _lane_repo(d, mode=mode, record="current", mutants=mutants)

    def _killed(self, n, start=2):
        return [{"unit": "BG0001", "criterion": "AC1", "verdict": "killed", "line": start + i,
                 "mutant": f"mutant {i}", "test": "pytest x"} for i in range(n)]

    def test_a_completed_run_with_one_survivor_refuses_through_the_command(self) -> None:
        """AC1. Mutant: refuse on the run's own exit status rather than on the survivor count -
        a run that completes is evidence a run happened and says nothing about what it found."""
        with tempfile.TemporaryDirectory() as d:
            rows = self._killed(11) + [{"unit": "BG0001", "criterion": "AC2",
                                        "verdict": "survived", "line": 3,
                                        "mutant": "inverted the guard", "test": "pytest x"}]
            root = self._repo(d, rows)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a completed run carrying a survivor was let through")
            self.assertIn("SURVIVED", out)
            self.assertIn("1 of 12", out, f"the refusal does not state the count:\n{out}")

    def test_the_refusal_names_each_survivor_with_its_file_line_and_mutation(self) -> None:
        """AC2. The author is told WHICH assertion is missing, not that a number was too high.

        The ledger under test is written the way the shipped verb writes it, carrying the
        `line` that `register --line` now records - before US0661 no verb could produce one, so
        this assertion passed on a fixture the tool itself could never have made.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, [{"unit": "BG0001", "criterion": "AC1", "verdict": "survived",
                                   "line": 3, "mutant": "inverted the a == b guard",
                                   "test": "pytest x"}])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code)
            self.assertIn("src/thing.py:3", out, "the refusal names no file and line")
            self.assertIn("inverted the a == b guard", out,
                          "the refusal does not say what was mutated")

    def test_zero_survivors_over_a_non_empty_set_passes_through_the_command(self) -> None:
        """AC3, the control. Mutant: refuse whatever the count - the gate then holds nothing
        open and every other assertion here passes for the wrong reason."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, self._killed(12))
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"12 killed mutants did not open the gate:\n{out}")
            self.assertIn("Status:** Fixed", _read(root, "bugs", "BG0001-x.md"))

    def test_an_empty_mutant_set_is_refused_not_passed_through_the_command(self) -> None:
        """AC4. `survivors == 0` over an EMPTY set is the vacuous green this gate exists to
        refuse - the same shape as `ac=0 pass=0` reading as a clean pass, one instrument over.

        Mutant: treat an applied count of zero as a pass.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, [{"unit": "BG0001", "criterion": "AC1",
                                   "verdict": "equivalent", "line": 3,
                                   "mutant": "a no-op swap", "reason": "no behaviour changed"}])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a run that applied no mutant was read as a pass")
            self.assertIn("NO mutant", out, f"the refusal does not say why:\n{out}")


class RepairScopeCLITests(unittest.TestCase):
    """US0566 AC1/AC2, through the command: feature work keeps the cheaper bar."""

    def test_a_feature_story_is_not_held_to_the_repair_bar(self) -> None:
        """The scope of the demand is the repair class the evidence indicts. A blanket
        requirement on all work is the one that gets switched off for cost, and then it holds
        nothing.

        Mutant: drop the repair test and hold every unit - a feature story with no mutation
        record is then refused, which is the gate nobody keeps switched on.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-f.md").write_text(
                "# US0001: a feature\n\n> **Status:** In Progress\n"
                "> **Affects:** src/thing.py\n> **Points:** 3\n\n"
                "## Acceptance Criteria\n\n### AC1: it behaves\n\n"
                "- **Then** it behaves\n- **Verify:** shell echo ok\n- **Verified:** yes\n",
                encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-f.md) | a feature | In Progress |\n", encoding="utf-8")
            code, out = _cli(root, "set", "--id", "US0001", "--status", "Done", "--force")
            self.assertEqual(0, code, out)
            self.assertNotIn("mutation evidence", out,
                             "feature work was held to the repair bar")

    def test_the_repair_class_is_derived_from_metadata_not_prose(self) -> None:
        """AC2. Derived from the artefact's own type and provenance fields, never keyword-matched
        against its title - a title is prose, and prose is the thing an author writes to explain
        rather than to be parsed.

        Mutant: match `fix` or `regression` in the title - the feature story below is then typed
        as a repair on a word in its own summary.
        """
        cases = [
            ("bug", "> **Status:** Open\n", True),
            ("story", "> **Status:** Ready\n> **Parent:** BG0009\n", True),
            ("story", "> **Status:** Ready\n> **Delivers:** RV0003\n", True),
            ("story", "> **Status:** Ready\n> **Delivers:** CR0009\n", False),
        ]
        for type_, fields, expected in cases:
            with self.subTest(type_=type_, fields=fields):
                text = (f"# X: a regression fix for the broken bug\n\n{fields}"
                        f"> **Affects:** src/thing.py\n")
                repair, why = tr.is_repair_unit(type_, text)
                self.assertEqual(expected, repair,
                                 f"{type_} with {fields!r} classified {repair}, expected "
                                 f"{expected} - and the title says 'regression fix' either way")
                self.assertTrue(why.strip(), "the classification states no reason")


class MeasuredEvidenceCLITests(unittest.TestCase):
    """US0661: the gate is satisfiable by MEASUREMENT, not only by the author's typed claim.

    `append_ledger` reduced a measured run to a counter block and discarded its per-mutant
    records, while `register_mutant` wrote the list the gate selects on. So the strongest
    evidence in the system read as no evidence, and the weakest read as proof - the exact
    inverse of the doctrine's phrase about evidence an author could not have manufactured.
    """

    def _measured(self, root, *, unit="BG0001", verdicts=(("killed", 4),)):
        """Write a MEASURED ledger entry through `append_ledger`, the production writer."""
        import hashlib
        src = root / "src" / "thing.py"
        report = {"targets": [str(src)],
                  "target_hashes": {str(src): hashlib.sha256(src.read_bytes()).hexdigest()},
                  "git_rev": "abc", "generated_at": "2026-08-07T00:00:00Z",
                  "test_cmd": "pytest x"}
        records = [{"file": str(src), "line": line, "class": "stub-return-null",
                    "verdict": v, "test": "pytest x"} for v, line in verdicts]
        import importlib.util as iu
        spec = iu.spec_from_file_location("mutation", DIR / "mutation.py")
        mod = iu.module_from_spec(spec)
        sys.modules["mutation"] = mod
        spec.loader.exec_module(mod)
        mod.append_ledger(root, report, records, unit=unit)

    def test_a_measured_run_satisfies_the_gate(self) -> None:
        """AC1, A DISCRIMINATING PAIR. Asserting exit 0 alone is vacuous - the command exited 0
        for every ledger before the lane was wired, so a single-arm test is green in both
        states. The negative arm is the same ledger with its per-mutant rows removed, which is
        exactly what today's `append_ledger` wrote.

        Mutant: drop the per-mutant list from a measured entry.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            self._measured(root)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"a measured run did not satisfy the gate:\n{out}")
            self.assertIn("Status:** Fixed", _read(root, "bugs", "BG0001-x.md"))
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            self._measured(root)
            led = root / "sdlc-studio" / ".local" / "mutation-runs.json"
            state = json.loads(led.read_text(encoding="utf-8"))
            for e in state["entries"]:
                e.pop("mutants", None)
            led.write_text(json.dumps(state), encoding="utf-8")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a ledger with its per-mutant rows removed still "
                                         "satisfied the gate, so the rows decide nothing")

    def test_a_measured_record_is_attributed_to_its_unit(self) -> None:
        """AC2. Persisting the list is half the change and the attribution is the other half:
        a row nobody can attribute answers no question the gate asks.

        Mutant: write the measured records but omit the `unit` key.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            self._measured(root, unit="BG0001")
            self.assertEqual(0, _cli(root, "set", "--id", "BG0001", "--status", "Fixed")[0])
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="none")
            self._measured(root, unit=None)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "an unattributed measured row opened the gate, so the "
                                         "unit key decides nothing")

    def test_a_recorded_kill_shown_to_survive_refuses_even_when_off(self) -> None:
        """AC4. Not a quality bar - the instrument reporting two different things about one
        fact. `off` says evidence must not hold your transitions; it cannot say the ledger may
        lie, because every figure derived from a false verdict is wrong and nothing downstream
        can tell.

        Mutant: gate the contradiction check behind the mode being other than `off`.
        Mutant: refuse on ANY co-located registered and measured pair, whatever the verdicts -
        which the control below catches.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="off", record="current")   # registered killed at line 4
            self._measured(root, verdicts=(("survived", 4),))    # measured survived at line 4
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a self-contradicting ledger was accepted under `off`")
            self.assertIn("CONTRADICTS", out, f"the refusal does not say what it found:\n{out}")
        with tempfile.TemporaryDirectory() as d:
            # THE CONTROL: the same co-located pair, AGREEING. A check that refuses on any pair
            # passes the assertion above for the wrong reason.
            root = _lane_repo(d, mode="off", record="current")
            self._measured(root, verdicts=(("killed", 4),))
            self.assertEqual(0, _cli(root, "set", "--id", "BG0001", "--status", "Fixed")[0],
                             "two records AGREEING were read as a contradiction")

    def test_the_refusal_quotes_the_registered_line(self) -> None:
        """AC6. The survivor listing composes `target:line`, and before `register --line` no
        shipped verb could write one - so it printed a question mark, and every test asserting
        otherwise passed on a fixture the tool could not produce.

        Mutant: compose the refusal from the target alone, dropping the line.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", record="current", mutants=[
                {"unit": "BG0001", "criterion": "AC1", "verdict": "survived", "line": 2,
                 "mutant": "inverted the guard", "test": "pytest x"}])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a survivor did not refuse under `block`")
            self.assertIn("src/thing.py:2", out,
                          f"the refusal does not quote the line:\n{out}")
            self.assertNotIn("src/thing.py:?", out,
                             "the refusal printed a question mark where a line was recorded")


class SurvivorFilingCLITests(unittest.TestCase):
    """US0660: under the default mode a survivor becomes a severity-rated bug and the
    transition PROCEEDS.

    Reporting rather than blocking is only an honest trade if the thing traded away lands
    somewhere a person will see it. A survivor named in a terminal window that then closes has
    been dropped, which is the outcome blocking was rejected to avoid, not the one chosen.
    """

    def _survivor_repo(self, d, **kw):
        return _lane_repo(d, mode=None, record="current", mutants=[
            {"unit": "BG0001", "criterion": "AC1", "verdict": "survived", "line": 2,
             "mutant": "inverted the a == b guard", "test": "pytest x"}], **kw)

    def _bugs(self, root):
        return sorted(p.name for p in (root / "sdlc-studio" / "bugs").glob("BG*.md")
                      if p.name != "BG0001-x.md")

    def test_a_survivor_is_filed_and_the_close_proceeds(self) -> None:
        """AC1. Mutant: report the survivor in the warning and mint nothing - the finding then
        dies with the terminal window."""
        with tempfile.TemporaryDirectory() as d:
            root = self._survivor_repo(d)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"the default mode blocked on a survivor:\n{out}")
            self.assertIn("Status:** Fixed", _read(root, "bugs", "BG0001-x.md"))
            filed = self._bugs(root)
            self.assertEqual(1, len(filed), f"expected one filed survivor bug, got {filed}")
            body = (root / "sdlc-studio" / "bugs" / filed[0]).read_text(encoding="utf-8")
            for needle in ("BG0001", "src/thing.py", "inverted the a == b guard", "pytest x"):
                self.assertIn(needle, body,
                              f"the filed finding does not name {needle!r}, so a reader cannot "
                              f"act on it without going back to the ledger")

    def test_one_command_mints_exactly_one_bug_and_a_dry_run_mints_none(self) -> None:
        """AC2, on TWO PRISTINE FIXTURES. One fixture cannot see this: once AC4's idempotence
        exists, a dry run following a real one dedupes against it and mints nothing for the
        wrong reason.

        Mutant: file the survivor inside the gate lane, with no dry-run guard - `_pre_write_gates`
        runs up to three times per `set`, and the preflight pass writes during what is
        contractually a dry run.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._survivor_repo(d)
            # `--reviewer` alone is refused; the point of this arm is only that the ladder
            # runs more than once per `set`, which the preflight already forces.
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed",
                             "--depth", "functional (unit: the repaired branch, both ways)")
            self.assertEqual(0, code, out)
            self.assertEqual(1, len(self._bugs(root)),
                             f"one command minted {self._bugs(root)} - the gate ladder runs "
                             f"more than once per `set`")
        with tempfile.TemporaryDirectory() as d:
            root = self._survivor_repo(d)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed", "--dry-run")
            self.assertEqual(0, code, out)
            self.assertEqual([], self._bugs(root),
                             "a dry run minted an artefact, breaking the contract that it "
                             "introduces no write of its own")
            self.assertIn("Status:** Open", _read(root, "bugs", "BG0001-x.md"))

    def test_the_same_survivor_does_not_mint_a_second_bug_after_a_cache_loss(self) -> None:
        """AC4. The filer's own bookkeeping is cleared while the mutation ledger is left
        INTACT - `sdlc-studio/.local/` holds both, and deleting it wholesale would remove the
        survivor itself, so run two would find nothing and mint nothing for the wrong reason.

        Mutant: key idempotence on a `.local` cache rather than on the artefact field.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._survivor_repo(d)
            self.assertEqual(0, _cli(root, "set", "--id", "BG0001", "--status", "Fixed")[0])
            first = self._bugs(root)
            self.assertEqual(1, len(first))
            keep = {"mutation-runs.json", "mutation-report.json", "mutation-series.jsonl",
                    "run-state.json"}
            local = root / "sdlc-studio" / ".local"
            for f in local.iterdir():
                if f.is_file() and f.name not in keep:
                    f.unlink()
            # A reopen RETRACTS the depth, so restore it before closing again - otherwise the
            # second close is refused by the depth gate and mints nothing for a reason that has
            # nothing to do with idempotence.
            _cli(root, "set", "--id", "BG0001", "--status", "Open")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed",
                             "--depth", "functional (unit: the repaired branch, both ways)")
            self.assertEqual(0, code, out)
            self.assertEqual(first, self._bugs(root),
                             "the same survivor minted a second bug once the filer's own "
                             "bookkeeping was lost, so the key is not on the artefact")

    def test_a_survivor_bug_never_parents_another(self) -> None:
        """The generational hazard. A filed survivor bug is itself a repair; without this it
        files a survivor of its own, and so on for ever."""
        with tempfile.TemporaryDirectory() as d:
            root = self._survivor_repo(d)
            self.assertEqual(0, _cli(root, "set", "--id", "BG0001", "--status", "Fixed")[0])
            child = self._bugs(root)[0]
            body = (root / "sdlc-studio" / "bugs" / child).read_text(encoding="utf-8")
            self.assertIn(tr.SURVIVOR_FIELD, body,
                          "the filed bug carries no survivor field, so nothing stops it "
                          "parenting another")
            cid = sdlc_md.extract_record_id(Path(child).stem)
            _cli(root, "set", "--id", cid, "--status", "Fixed")
            self.assertEqual([child], self._bugs(root),
                             "a survivor bug filed a survivor of its own")


class SurvivorSeverityTests(unittest.TestCase):
    """US0660 AC3: severity is DERIVED from the enclosing structure, and names its signal.

    The three fixtures differ ONLY in that structure - the same file, the same function name -
    so a mapping keyed on either, which is what a hurried implementer writes, cannot pass.
    """

    BODIES = {
        "High": "def decide(a, b):\n    if a == b:\n        raise ValueError('no')\n    return 1\n",
        "Medium": "def decide(a, b):\n    if a == b:\n        print('x')\n    return 1\n",
        "Low": "DECIDE = 1\ndef other():\n    return 2\n",
    }

    def test_severity_is_derived_from_the_enclosing_structure_and_names_its_signal(self) -> None:
        """Mutant: map severity from the target file's suffix rather than the enclosing
        structure - all three fixtures share a suffix, so it cannot pass.
        Mutant: file the derived severity with no signal string - all three severities stay
        correct and triage gets a verdict it cannot disagree with.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir(parents=True)
            for expected, body in self.BODIES.items():
                (root / "src" / "thing.py").write_text(body, encoding="utf-8")
                sev, signal = tr._survivor_severity(
                    str(root), {"target": "src/thing.py", "line": 1 if expected == "Low" else 3})
                self.assertEqual(expected, sev,
                                 f"a body whose only difference is its structure derived "
                                 f"{sev}, not {expected}")
                self.assertTrue(signal.strip(),
                                "the severity names no signal, so nothing can be disagreed with")

    def test_an_unparseable_file_is_medium_and_says_so(self) -> None:
        """Never High, which inflates triage on a file nobody could read; never Low, which
        buries it. Mutant: return Low, or High, on a parse failure."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir(parents=True)
            (root / "src" / "thing.py").write_text("def broken(\n", encoding="utf-8")
            sev, signal = tr._survivor_severity(str(root),
                                                {"target": "src/thing.py", "line": 1})
            self.assertEqual("Medium", sev)
            self.assertIn("UNDERIVED", signal,
                          "a severity that could not be derived does not say so")


class NoSurfaceExemptionCLITests(unittest.TestCase):
    """BG0541 AC3/AC7 and US0566 AC3/AC4: the exemption is re-derived from the DIFF.

    Re-deriving over the record's own `paths` checks that the author was consistent with
    themselves, which is not a check: a record naming `README.md` exempted a repair whose
    `Affects` was a mutatable module, because the generator dutifully found nothing in the
    markdown file it was handed.
    """

    def test_the_refusal_names_the_path_the_diff_gives_not_the_one_affects_gives(self) -> None:
        """AC3. THE THREE SOURCES DISAGREE, which is the whole criterion: `Affects` names an
        unchanged module, the diff changes a different one, and the record claims a markdown
        file. Against a fixture where Affects and the diff name the same file, the old
        derivation and the new one produce identical output and the test pins nothing.

        Mutant: derive the exempted surface from `affects_files(text)` rather than from the
        diff against the run's base ref.
        """
        with tempfile.TemporaryDirectory() as d:
            # `Affects` names the module the diff did NOT touch. Give both the same file and
            # the two derivations produce identical output, so the test pins nothing - which is
            # the state the first draft of this test was in, proven by its mutant surviving.
            root = _lane_repo(d, mode="block", exemption=["README.md"],
                              affects="src/other.py")
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a false exemption over a mutatable surface was granted")
            self.assertIn("src/thing.py", out,
                          "the refusal does not name the file the DIFF gives - "
                          f"got:\n{out}")
            self.assertNotIn("src/other.py", out,
                             "the refusal names the file `Affects` declares and the diff never "
                             "touched, so the surface came from the declaration rather than "
                             "from the change")
            self.assertIn("README.md", out, "the refusal does not quote what was claimed")

    def test_a_false_exemption_is_refused_under_report_too(self) -> None:
        """`report` trades a hard bar for a filed finding. It does not trade away the truth of
        a statement its author made in writing, so a claim re-derived and found untrue blocks
        in every mode but `off`.

        Mutant: route the exemption refusal through the mode table with the other rows.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode=None, exemption=["README.md"])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a false exemption was reported rather than refused")
            self.assertIn("src/thing.py", out)
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="off", exemption=["README.md"])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"`off` refused a false exemption:\n{out}")

    def test_an_empty_base_ref_refuses_the_exemption(self) -> None:
        """AC7. The fallback fails the WORSE way here: a derivation that cannot run produces no
        mutant, and no mutant is indistinguishable from a claim that holds - so every exemption
        would be granted by the one condition under which nothing was checked.

        Mutant: swallow the empty base ref and grant the exemption.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", exemption=["README.md"])
            (root / "sdlc-studio" / ".local" / "run-state.json").unlink()
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "an exemption was granted with no base ref to check it")
            self.assertIn("no base ref", out,
                          f"the refusal does not name the missing base ref:\n{out}")

    def test_a_no_surface_repair_records_the_exemption_and_its_reason(self) -> None:
        """US0566 AC3. An exemption that states no scope cannot be re-derived, so it is a claim
        wearing an exemption's name.

        Mutant: accept a record naming no paths.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", exemption=[], affects="README.md",
                              py_change=False)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"a genuine markdown-only repair was refused:\n{out}")
            rec = json.loads((root / "sdlc-studio" / ".local"
                              / "no-mutatable-surface.json").read_text(encoding="utf-8"))
            self.assertIn("BG0001", rec,
                          "the exemption was granted without a durable record, so a reader "
                          "cannot tell an established absence from a skipped run")

    def test_a_claimed_exemption_over_a_mutatable_surface_is_refused(self) -> None:
        """US0566 AC4. An exemption an author can assert is the gate's own fail-open.

        Mutant: return None without re-deriving - a hand-written record claiming nothing could
        be mutated exempts a repair whose Python function the generator can demonstrably
        mutate, and the gate becomes a box somebody ticks.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", exemption=["README.md"])
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertNotEqual(0, code, "a false exemption over a mutatable surface was granted")
            self.assertIn("src/thing.py", out, "the refusal names no file that refutes it")
            self.assertIn("re-derived", out)

    def test_a_genuine_no_surface_repair_keeps_its_exemption(self) -> None:
        """The control. A repair whose changed surface really is markdown-only must pass, or
        the exemption is not an exemption and the criterion is satisfied by refusing
        everything."""
        with tempfile.TemporaryDirectory() as d:
            root = _lane_repo(d, mode="block", exemption=["README.md"], affects="README.md",
                              py_change=False)
            code, out = _cli(root, "set", "--id", "BG0001", "--status", "Fixed")
            self.assertEqual(0, code, f"a genuine markdown-only repair was refused:\n{out}")


class TestPlanGateTests(unittest.TestCase):
    """US0630: a unit reaching delivery without a REVIEWED test plan is refused by the command
    that starts the work, not reported at the close.

    The demand has to arrive before any code is written, or it is a tax on finished work rather
    than a gate on starting it - which is how a gate stops being satisfied and starts being
    forced.
    """

    PLAN = ("\n## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
            "| AC1 | in thing.py, delete the guard | it refuses |\n")

    def _repo(self, root: Path, *, plan: bool, created="2026-08-06", cutoff=True) -> None:
        (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "src" / "thing.py").write_text("x = 1\n", encoding="utf-8")
        if cutoff:
            (root / "sdlc-studio" / ".config.yaml").write_text(
                'review:\n  test_plan_after: "2026-01-01"\n', encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
            f"# BG0001: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Verification depth:** functional\n> **Created:** {created}\n"
            f"> **Affects:** src/thing.py\n> **Points:** 3\n\n"
            f"## Acceptance Criteria\n\n### AC1: it refuses\n\n- **Then** it refuses\n"
            f"- **Verify:** pytest x\n" + (self.PLAN if plan else ""), encoding="utf-8")

    def _start(self, root: Path):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tr.main(["set", "--id", "BG0001", "--status", "In Progress",
                            "--root", str(root)])
        return code, out.getvalue() + err.getvalue()

    def test_starting_work_without_a_plan_is_refused(self) -> None:
        """Mutant: gate only at Done - the plan is demanded of finished work, which is a tax
        rather than a gate and is exactly what gets forced. THE POSITIVE CONTROL is below: with
        a reviewed plan the same transition succeeds."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=False)
            code, text = self._start(root)
            self.assertNotEqual(code, 0, "work started with no test plan")
            self.assertIn("no `## Test Plan`", text)
            self.assertIn("testplan derive", text,
                          "the refusal does not print the command that produces one")

    def test_an_unreviewed_plan_is_refused_distinctly(self) -> None:
        """The two refusals have DIFFERENT fixes, so one message for both sends the reader to
        the wrong command - and being sent to the wrong one of "write a plan" and "get it
        reviewed" is not a small error when the whole claim is that reviewing the test is cheap.

        Mutant: return the missing-plan message for both - this reddens on the distinction.
        A spec-kind approval must not discharge it either: that reviewer never saw a test plan.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=True)
            code, text = self._start(root)
            self.assertNotEqual(code, 0, "work started on an unreviewed plan")
            self.assertIn("no independent seat has approved", text)
            self.assertNotIn("no `## Test Plan`", text,
                             "an unreviewed plan was reported as a missing one")

            # A SPEC approval does not clear the TEST-PLAN gate - BG0510's whole point.
            import critic
            critic.record_verdict(root, "BG0001", "approve", reviewer="qa", author="dev",
                                  phase="plan-review", kind="spec", brief="a" * 12)
            code, text = self._start(root)
            self.assertNotEqual(code, 0,
                                "a spec-review approval discharged the test-plan gate")

            # A SELF test-plan review does not clear it either.
            critic.record_verdict(root, "BG0001", "approve", reviewer="dev", author="dev",
                                  phase="plan-review", kind="test-plan", brief="b" * 12)
            code, text = self._start(root)
            self.assertNotEqual(code, 0, "a self-review cleared the test-plan gate")
            self.assertIn("self-review", text)

            # THE POSITIVE CONTROL: an independent test-plan APPROVE opens it.
            critic.record_verdict(root, "BG0001", "approve", reviewer="qa", author="dev",
                                  phase="plan-review", kind="test-plan", brief="c" * 12)
            code, text = self._start(root)
            self.assertEqual(code, 0, f"a reviewed plan was still refused: {text}")

    def test_requirements_states_the_test_plan_demand(self) -> None:
        """Asked BEFORE the work. Derived by running the real gate rather than restating it, so
        there is no second copy to go stale.

        Mutant: hand-maintain the requirement list - it drifts from the gate silently, which is
        the failure `requirements` exists to remove, reintroduced one layer up.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=False)
            unmet = tr.requirements(str(root), "BG0001", "In Progress")
            self.assertTrue(any("Test Plan" in u for u in unmet),
                            f"the demand is not stated before the work: {unmet}")

    def test_an_unreadable_ledger_refuses_rather_than_passes(self) -> None:
        """`return None` is PASS, so swallowing every exception made the one condition under
        which the gate was least able to judge the one under which it approved everything. A seat
        chmod-ed the verdict ledger and watched a refusal become exit 0 with nothing on either
        stream. Two sibling gates in this same file already fail loud; this one was written past
        both.

        Mutant: swallow and return None - an unreadable bar reads as a passed one.
        """
        import os
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=True)
            led = root / "sdlc-studio" / "reviews" / "plan-review-verdicts.md"
            led.parent.mkdir(parents=True, exist_ok=True)
            led.write_text("# Plan review verdicts\n\n| Unit | Verdict |\n| --- | --- |\n",
                           encoding="utf-8")
            os.chmod(led, 0o000)
            try:
                if os.access(led, os.R_OK):      # running as root - the probe cannot be made
                    self.skipTest("cannot make a file unreadable in this environment")
                code, text = self._start(root)
            finally:
                # Restored HERE, not via addCleanup: the temp directory is gone by then, so the
                # cleanup would raise FileNotFoundError and mask the result it is protecting.
                os.chmod(led, 0o644)
            self.assertNotEqual(code, 0, "an unreadable ledger was treated as a passed gate")
            self.assertIn("could not be established", text)
            self.assertIn("not a passed one", text)

    def test_an_unreadable_config_does_not_switch_the_gate_off(self) -> None:
        """An unreadable `.config.yaml` is not an ABSENT cutoff. `project_override` swallows every
        config fault and returns the default, so `not after` read a malformed, non-UTF-8,
        unreadable or directory-shaped config as "this project set no cutoff" and stood BOTH new
        gates down entirely. A seat reproduced it four ways.

        The sibling `_two_role_gate` already solved this with `_config_unparseable`, and its
        comment enumerates the same four shapes: "silence read as a pass, reproduced one layer up
        in the gate written to close it". This repair reached parity with that gate's LEDGER half
        and skipped its CONFIG half.

        Mutant: read an unparseable config as no cutoff - a project that DECLARES the rule and
        then cannot be read has silently waived it.
        """
        import os
        shapes = {
            "malformed yaml": lambda c: c.write_text("review:\n\ttest_plan_after: x\n",
                                                     encoding="utf-8"),
            "non-utf8": lambda c: c.write_bytes(b"review:\n  test_plan_after: \xff\xfe\n"),
            "a directory": lambda c: c.mkdir(),
        }
        for why, make in shapes.items():
            with self.subTest(why=why), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._repo(root, plan=False, cutoff=False)
                make(root / "sdlc-studio" / ".config.yaml")
                code, text = self._start(root)
                self.assertNotEqual(code, 0,
                                    f"an unreadable config ({why}) switched the gate off")

    def test_the_planned_mutant_gate_also_fails_loud(self) -> None:
        """The sibling half of the fail-loud repair, which a seat found pinned by NOTHING: the
        `return None` mutant survived 2,137 tests across eight suite files, and this unit's own
        Mutation-checked field claimed it had been killed. Both are corrected.

        Mutant: swallow and return None - a corrupt mutation ledger grants the terminal
        transition at exit 0.
        """
        import unittest.mock
        import mutation
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=True)
            # The FIRST version of this test wrote a corrupt ledger and passed for the wrong
            # reason: `_load_ledger` catches that one layer down, so the except branch never ran
            # and the swallow mutant survived it. The failure has to be forced at the boundary
            # the gate actually guards.
            with unittest.mock.patch.object(
                    mutation, "plan_execution",
                    side_effect=RuntimeError("ledger unreadable")):
                unmet = tr.requirements(str(root), "BG0001", "Fixed")
            self.assertTrue(any("could not be established" in u for u in unmet),
                            f"a failing planned-mutant gate granted the transition: {unmet}")
            self.assertTrue(any("not a passed one" in u for u in unmet), unmet)

    def test_a_unit_before_the_cutoff_is_not_held(self) -> None:
        """A gate that refuses every unit in an existing backlog is one that gets switched off
        wholesale rather than satisfied.

        Mutant: gate unconditionally, or ignore the unit's Created date - every historical unit
        in every consuming project is held by a plan nobody was ever asked for.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=False, created="2025-01-01")
            code, text = self._start(root)
            self.assertEqual(code, 0, f"a pre-cutoff unit was retro-refused: {text}")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, plan=False, cutoff=False)
            code, text = self._start(root)
            self.assertEqual(code, 0, f"the gate fired with no cutoff recorded: {text}")


class DoneGateTests(unittest.TestCase):
    """CR0084: a story may not reach Done with red / never-run executable ACs."""

    def _story(self, root: Path, body: str) -> None:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "US0001-x.md").write_text(body, encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")

    def _report(self, root: Path, payload: dict) -> None:
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(payload), encoding="utf-8")

    def test_blocks_when_executable_ac_never_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")        # no report -> blocked

    def test_blocks_when_report_red(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                          "failures": [{"ac": "AC1"}]}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_passes_when_report_green(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {"failed": 0, "stale": 0, "failures": []}}})
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_bare_manual_ac_blocks_done(self) -> None:  # BG0300
        # A manual AC with no `**Verified:**` marker means nothing looked at the deliverable.
        # The gate must refuse Done and name the bare AC.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** manual eyeball it\n")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "US0001", "Done")
            self.assertIn("AC1", str(cm.exception))

    def test_manual_ac_verified_no_or_stale_blocks_done(self) -> None:  # BG0300
        # Only a PASSING verdict is evidence. `no` (human saw it fail) and `stale` (evidence out
        # of date) must block, symmetric with a red/stale executable verifier - not be waved
        # through as "a marker is present".
        for state in ("no", "stale"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n"
                                  f"- **Verify:** manual eyeball it\n- **Verified:** {state} (2026-07-27)\n")
                with self.assertRaises(ValueError) as cm:
                    tr.transition(root, "US0001", "Done")
                self.assertIn("AC1", str(cm.exception))

    def test_manual_ac_with_evidence_passes(self) -> None:  # BG0300
        # The same manual AC, now carrying recorded human evidence, is allowed through.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n"
                              "- **Verify:** manual eyeball it\n- **Verified:** yes (2026-07-27)\n")
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_force_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            res = tr.transition(root, "US0001", "Done", force=True)
            self.assertEqual(res["to"], "Done")

    def test_pyyaml_absent_still_blocks_not_crashes(self) -> None:  # BG0062
        # On a machine without PyYAML the Done gate must still emit its block (ValueError),
        # not surface a config-loading RuntimeError. The gate reads policy via the
        # gracefully-degrading project_override, never config.get's hard PyYAML path.
        import config
        orig = config._yaml
        def _boom():
            raise RuntimeError("config loading needs PyYAML")
        config._yaml = _boom
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
                self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                             "failures": [{"ac": "AC1"}]}}})
                with self.assertRaises(ValueError):
                    tr.transition(root, "US0001", "Done")
        finally:
            config._yaml = orig

    def test_blocks_when_story_edited_after_verify(self) -> None:  # BG0065
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            # a green entry, but stamped in the past - the story file is newer (edited since).
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2020-01-01T00:00:00Z"}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_blocks_when_ac_added_after_verify(self) -> None:  # BG0065
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n"
                              "### AC1\n- **Verify:** shell true\n\n### AC2\n- **Verify:** shell true\n")
            # green + fresh stamp (mtime check passes), but the report only accounted for 1 AC.
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2099-01-01T00:00:00Z"}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_passes_when_fresh_and_ac_count_matches(self) -> None:  # BG0065 no false positive
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2099-01-01T00:00:00Z"}}})
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_config_toggle_downgrades_to_advisory(self) -> None:  # CR0095
        from lib import sdlc_md
        orig = sdlc_md.project_override
        sdlc_md.project_override = lambda root, dotted, default=None: (
            False if dotted == "quality.done_requires_verified" else orig(root, dotted, default))
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
                self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                             "failures": [{"ac": "AC1"}]}}})
                res = tr.transition(root, "US0001", "Done")   # toggle off -> warns, does not raise
                self.assertEqual(res["to"], "Done")
                self.assertIn("advisory", (res["warning"] or "").lower())
        finally:
            sdlc_md.project_override = orig


class ManualEvidenceGateFailsLoudTests(unittest.TestCase):
    """BG0335: `_acs_missing_evidence` returned an EMPTY pair on any exception, and an empty
    pair is exactly what "every AC carries a passing human verdict" looks like. A broken
    `verify_ac` import or a story the parser choked on therefore disarmed the manual-evidence
    Done gate completely - the all-manual story below is blocked when the parser works
    (`DoneGateTests.test_bare_manual_ac_blocks_done`) and sailed through when it did not.
    The failure must be VISIBLE: a block reason, not silence."""

    def _story(self, root: Path, body: str) -> None:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "US0001-x.md").write_text(body, encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")

    _BARE_MANUAL = ("# US0001: s\n\n> **Status:** Ready\n\n### AC1\n"
                    "- **Verify:** manual eyeball it\n")

    @contextlib.contextmanager
    def _parser_raising(self):
        import verify_ac
        orig = verify_ac.parse_story

        def _boom(_text):
            raise RuntimeError("parser exploded")

        verify_ac.parse_story = _boom
        try:
            yield
        finally:
            verify_ac.parse_story = orig

    @contextlib.contextmanager
    def _import_broken(self):
        orig = sys.modules.get("verify_ac")
        sys.modules["verify_ac"] = None      # `import verify_ac` now raises ImportError
        try:
            yield
        finally:
            if orig is None:
                sys.modules.pop("verify_ac", None)
            else:
                sys.modules["verify_ac"] = orig

    def test_parse_failure_blocks_done_instead_of_waving_it_through(self) -> None:
        with self._parser_raising():
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, self._BARE_MANUAL)
                with self.assertRaises(ValueError) as cm:
                    tr.transition(root, "US0001", "Done")
                msg = str(cm.exception)
                self.assertIn("could not run", msg)
                self.assertIn("parser exploded", msg)   # the reason is named, not swallowed

    def test_import_failure_blocks_done(self) -> None:
        with self._import_broken():
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, self._BARE_MANUAL)
                with self.assertRaises(ValueError) as cm:
                    tr.transition(root, "US0001", "Done")
                self.assertIn("could not run", str(cm.exception))

    def test_helper_reports_the_failure_rather_than_an_empty_all_clear(self) -> None:
        """At the helper's own boundary: the caller must be able to tell "nothing owed" from
        "nothing looked". An empty pair with no error signal cannot express the difference."""
        with self._parser_raising():
            result = tr._acs_missing_evidence(self._BARE_MANUAL)
        self.assertIsNotNone(result[-1], "the parse failure was reported as an all-clear")
        clean = tr._acs_missing_evidence(
            "### AC1\n- **Verify:** manual eyeball it\n- **Verified:** yes (2026-07-27)\n")
        self.assertIsNone(clean[-1], "a healthy parse must not report an error")

    def test_force_still_overrides_the_loud_failure(self) -> None:
        """Failing loud must not become unbypassable: `--force` is the deliberate,
        recorded escape and it still works."""
        with self._parser_raising():
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, self._BARE_MANUAL)
                res = tr.transition(root, "US0001", "Done", force=True)
                self.assertEqual(res["to"], "Done")


def _bug_repo(root: Path, depth: str | None, prod: bool = False) -> Path:
    bd = root / "sdlc-studio" / "bugs"
    bd.mkdir(parents=True)
    header = "# BG0001: b\n\n> **Status:** In Progress\n> **Severity:** medium\n"
    if prod:
        header += "> **Production-affecting:** yes\n"
    if depth is not None:
        header += f"> **Verification depth:** {depth}\n"
    # A criterion, because BG0378 made the criteria floor fire at the VERB: a bug reaching a
    # delivered-terminal status with nothing stating what fixed looks like is refused. These
    # fixtures are about the depth tiers, so they carry the minimum that lets the unit under
    # test be the one that decides the verdict.
    (bd / "BG0001-x.md").write_text(
        header + "\n## Summary\n\nx\n\n## Steps to Reproduce\n\n1. x\n\n## Proposed Fix\n\ny\n"
        "\n## Acceptance Criteria\n\n- [x] the defect no longer reproduces\n",
        encoding="utf-8")
    (bd / "_index.md").write_text(
        "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| In Progress | 1 |\n| Fixed | 0 |\n| Closed | 0 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [BG0001](BG0001-x.md) | b | In Progress |\n", encoding="utf-8")
    return root


class TheVerbEnforcesTheBarItWritesTests(unittest.TestCase):
    """BG0417. The Definition of Done states the two-role clause and `conformance.py` implements
    it - but conformance is a lane that runs LATER, over a status a different tool has already
    written. `transition.py`, the verb that writes `Status: Done`, never consulted it: no call,
    no config read, no reference to the evidence half anywhere in the module. So a unit could be
    moved to Done with no independent review at all, and the only trace was a report somebody had
    to run and read. That is the mechanism behind every Done story carrying no independent verdict (the count of 25 that circulated with this bug is NOT supported by the tree - a claims-lens census found 21, all pre-cutoff):
    they did not slip past a gate, the gate they are said to have passed was never asked."""

    def _repo(self, root: Path, *, cutoff: int | None = 0, sid: str = "US0001") -> None:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / f"{sid}-x.md").write_text(
            f"# {sid}: s\n\n> **Status:** Review\n\n## Acceptance Criteria\n\n"
            f"### AC1\n- **Verify:** manual a human looked\n- **Verified:** yes (2026-01-01)\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Review | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [{sid}]({sid}-x.md) | s | Review |\n", encoding="utf-8")
        if cutoff is not None:
            (root / "sdlc-studio" / ".config.yaml").write_text(
                f"review:\n  two_role_after: {cutoff}\n", encoding="utf-8")

    def test_a_past_cutoff_unit_with_NEITHER_half_is_refused_and_both_are_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "US0001", "Done")
            msg = str(cm.exception)
            # conformance's OWN vocabulary, which is the point of delegating: the verb and the
            # lane must name the same halves. The first version re-implemented them inline with
            # its own strings AND omitted the verdict half, so it was weaker than the lane.
            # conformance's OWN vocabulary, which is the point: the verb and the lane must
            # name the same halves, so a rename moves both. The VERDICT half is deliberately
            # NOT this gate's - it belongs to the `critiqued` stage, and demanding it here
            # refused work the lane accepts.
            import conformance
            for half in (conformance.HALF_EVIDENCE, conformance.HALF_SIGNOFF):
                self.assertIn(half, msg,
                              f"{half!r} is not named - each unmet half needs a different "
                              f"action from a different person, so all must be listed")
            self.assertNotIn(conformance.HALF_VERDICT, msg,
                             "the verdict half is the critiqued stage's, not this gate's")

    def test_a_unit_with_a_SIGN_OFF_and_no_evidence_is_still_refused(self) -> None:
        """The bug's own reproduction: US0479 had a genuine operator sign-off, no adversarial
        pass at all, and was one `transition set` away from Done."""
        import critic
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            critic.record_verdict(root, "US0001", "APPROVE", reviewer="reviewer-a",
                                  author="builder", issues="probed")
            critic.record_signoff(root, "US0001", principal="the operator", author="builder",
                                  note="looks right")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "US0001", "Done")
            import conformance
            self.assertIn(conformance.HALF_EVIDENCE, str(cm.exception))

    def test_a_unit_with_BOTH_halves_is_allowed_through(self) -> None:
        """The control. A gate nothing can satisfy is not a gate, it is a wall - and the whole
        sprint this landed in is about gates that report a verdict they never established."""
        import critic
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            # ALL THREE halves. The first version of this control recorded only evidence and a
            # sign-off, so it passed a story to Done with no independent APPROVE - which
            # conformance would then have marked non-conformant. A control asserting a weaker
            # bar than the lane is how the gate came to be weaker than the lane.
            critic.record_verdict(root, "US0001", "APPROVE", reviewer="reviewer-a",
                                  author="builder", issues="probed")
            critic.record_evidence(root, "US0001", reviewer="reviewer-a", author="builder",
                                   findings="probed the parser")
            critic.record_signoff(root, "US0001", principal="the operator", author="builder",
                                  note="approved")
            tr.transition(root, "US0001", "Done")          # does not raise
            self.assertIn("Done", (root / "sdlc-studio" / "stories" / "US0001-x.md")
                          .read_text(encoding="utf-8"))

    def test_a_project_that_declares_NO_cutoff_is_unaffected(self) -> None:
        """Forward-only by design: a project that never adopted the two-role rule is not
        retro-fitted with it by an upgrade."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, cutoff=None)
            tr.transition(root, "US0001", "Done")          # does not raise

    def test_a_unit_AT_OR_BELOW_the_cutoff_is_unaffected(self) -> None:
        """The other half of forward-only: the cutoff is sequential, so US0001 under a cutoff
        of 500 is pre-gate work and keeps today's behaviour byte-for-byte."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, cutoff=500)
            tr.transition(root, "US0001", "Done")          # does not raise

    def test_force_still_overrides_and_the_bypass_is_RECORDED(self) -> None:
        """`--force` stays available and stays visible: a two-role bypass must be at least as
        recorded as every other forceable close gate. The recording half is asserted, not just
        the override - an earlier version of this test named it and checked only that the status
        moved, so a mutant blanking the bypass list left it green."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            tr.transition(root, "US0001", "Done", force=True)
            body = (root / "sdlc-studio" / "stories" / "US0001-x.md").read_text(encoding="utf-8")
            self.assertIn("Done", body)
            self.assertIn("two_role_after", body,
                          "the artefact does not record WHICH gate was bypassed, so a forced "
                          "two-role override is indistinguishable from an ordinary close")

    def test_an_UNREADABLE_CONFIG_refuses_rather_than_disabling_the_gate(self) -> None:
        """The reviewer's blocking finding, and the sharpest one: `project_override` swallows
        every config fault by design and returns the default, so a broken `.config.yaml` made
        the cutoff None, `two_role_applies_to` False, and the gate returned before it ever
        touched a ledger. Reproduced five ways - malformed YAML, tab indentation, non-UTF-8
        bytes, `.config.yaml` as a directory, PyYAML absent - each writing `Status: Done`, exit
        0. That is this gate's own stated principle, silence read as a pass, reproduced one
        layer up inside the gate written to close it."""
        for label, blob in (("malformed", b"review:\n\t\ttwo_role_after: [[[\n"),
                            ("non-utf8", b"review:\n  two_role_after: \xff\xfe\n")):
            with self.subTest(config=label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._repo(root, cutoff=None)
                (root / "sdlc-studio" / ".config.yaml").write_bytes(blob)
                # The config reader warns loudly about the unparseable file, which is correct
                # behaviour and pure noise HERE - a green suite must say nothing, or a real
                # error hides in it. Captured rather than silenced, so the warning still exists
                # for the operator who meets it.
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(ValueError) as cm:
                        tr.transition(root, "US0001", "Done")
                self.assertIn("could not be parsed", str(cm.exception))

    def test_a_VALID_config_that_omits_the_rule_is_not_held_to_it(self) -> None:
        """The control that keeps the refusal above honest. A project whose config PARSES and
        simply does not declare the two-role rule has not adopted it, and refusing there would
        hold every project to a rule none of them opted into - the opposite failure, and just
        as wrong. The distinguishing fact is whether the file can be READ, not whether it
        happens to mention the key: an unparseable config means you cannot know what it
        declared, which is why that case refuses and this one does not."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root, cutoff=None)
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "quality:\n  done_requires_verified: true\n", encoding="utf-8")
            tr.transition(root, "US0001", "Done")          # does not raise

    def test_an_unreadable_bar_is_NOT_a_passed_one(self) -> None:
        """Fails CLOSED. This gate exists because silence was being read as a pass, so a gate
        that cannot establish the bar must refuse rather than wave the unit through."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            real = tr._two_role_gate
            try:
                import critic
                broken = critic.evidence_for

                def boom(*a, **k):
                    raise RuntimeError("the ledger is unreadable")

                critic.evidence_for = boom
                with self.assertRaises(ValueError) as cm:
                    tr.transition(root, "US0001", "Done")
                self.assertIn("could not be established", str(cm.exception))
            finally:
                critic.evidence_for = broken
                tr._two_role_gate = real


class PositionalSetFormTests(unittest.TestCase):
    """CR0423/US0446: `transition.py set <ID> <STATUS>` (the natural first attempt) is accepted,
    mapping onto --id/--status; mixing the positional and flag form for one value is refused."""

    def _repo_ready(self, root: Path) -> None:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
            "### AC1\n- **Verify:** manual eyeballed\n- **Verified:** yes (2026-07-27)\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Draft |\n", encoding="utf-8")

    def test_positional_set_form_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo_ready(root)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = tr.main(["set", "US0001", "Review", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("**Status:** Review", _read(root, "stories", "US0001-x.md"))

    def test_positional_and_flag_conflict_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo_ready(root)
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = tr.main(["set", "US0001", "Review", "--status", "Done", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("EITHER positionally", err.getvalue())


class DepthTierGateTests(unittest.TestCase):
    """Verification-depth tiers are enforced on bug transitions, not decorative."""

    def test_smoke_to_fixed_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "smoke")
            with self.assertRaises(ValueError) as cm:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            self.assertIn("smoke", str(cm.exception))
            self.assertIn("functional", str(cm.exception))  # names required tier

    def test_functional_to_fixed_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional (unit + regression)")
            res = _quiet(tr.transition, root, "BG0001", "Fixed")
            self.assertEqual(res["to"], "Fixed")

    def test_missing_depth_refused_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)
            with self.assertRaises(ValueError) as cm:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            self.assertIn("Verification depth", str(cm.exception))

    def test_functional_to_verified_refused(self) -> None:
        # Verified claims the higher-tier proof landed; functional alone is
        # exactly the false assurance the status exists to prevent
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional (unit + component)")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Verified")
            self.assertIn("functional", str(cm.exception))

    def test_soak_to_verified_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "soak (24h in staging)")
            res = tr.transition(root, "BG0001", "Verified")
            self.assertEqual(res["to"], "Verified")

    def test_missing_depth_to_verified_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Verified")
            self.assertIn("Verification depth", str(cm.exception))

    def test_prod_bug_smoke_to_closed_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional", prod=True)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Closed")
            self.assertIn("soak", str(cm.exception))

    def test_prod_bug_soak_to_closed_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "soak (7 days)", prod=True)
            res = tr.transition(root, "BG0001", "Closed")
            self.assertEqual(res["to"], "Closed")

    def test_non_prod_close_path_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)  # no depth, not production-affecting
            res = tr.transition(root, "BG0001", "Closed")
            self.assertEqual(res["to"], "Closed")

    def test_decorated_prod_flag_still_gates(self) -> None:
        # 'yes (checkout path)' must not silently switch the soak gate OFF.
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional")
            p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** medium\n",
                "> **Severity:** medium\n> **Production-affecting:** yes (checkout path)\n"),
                encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Closed")
            self.assertIn("soak", str(cm.exception))

    def test_force_overrides_depth_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "smoke")
            res = tr.transition(root, "BG0001", "Fixed", force=True)
            self.assertEqual(res["to"], "Fixed")


class StoryTargetParityTests(unittest.TestCase):
    """Story Done should not out-run a declared AC Verification target - advisory
    by default, gateable via quality.depth_parity_gate."""

    def _story_with_target(self, root: Path, target: str) -> Path:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            f"### AC1\n- **Verify:** manual check\n- **Verified:** yes (2026-07-27)\n"
            f"- **Verification target:** {target}\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return root

    def test_target_above_functional_warns_but_allows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._story_with_target(Path(d), "soak")
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")
            self.assertIn("soak", res["warning"] or "")

    def test_functional_target_no_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._story_with_target(Path(d), "functional")
            res = tr.transition(root, "US0001", "Done")
            self.assertIsNone(res["warning"])


class BatchIdsTests(unittest.TestCase):
    """CR0143: --ids batches same-target transitions; each id individually gated,
    one refusal never aborts the rest."""

    def _two_bugs(self, root: Path):
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n"
            "> **Verification depth:** functional\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "BG0002-y.md").write_text(
            "# BG0002: b\n\n> **Status:** In Progress\n"
            "> **Verification depth:** smoke\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n"
            "| [BG0002](BG0002-y.md) | b | In Progress |\n", encoding="utf-8")
        return root

    def test_ids_batch_gates_each_and_continues(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tr.main(["set", "--ids", "BG0001,BG0002", "--status", "Fixed",
                              "--root", str(root)])
            out = buf.getvalue()
            self.assertNotEqual(rc, 0)                       # one refusal -> non-zero
            self.assertIn("BG0001", out)                     # the pass reported
            self.assertIn("blocked", out.lower())            # the refusal reported
            text1 = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            text2 = (root / "sdlc-studio" / "bugs" / "BG0002-y.md").read_text(encoding="utf-8")
            self.assertIn("**Status:** Fixed", text1)        # gated pass applied
            self.assertIn("**Status:** In Progress", text2)  # gated refusal untouched

    def test_id_and_ids_merge_deduped(self) -> None:
        # CR0210 grammar: --id (repeatable) and --ids (comma list) are combinable and merged,
        # de-duplicated in first-seen order - not mutually exclusive. Here BG0001 appears in
        # both, so exactly BG0001 and BG0002 are attempted (each individually gated).
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--id", "BG0001", "--ids", "BG0001,BG0002",
                         "--status", "Fixed", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("BG0001", out)
            self.assertIn("BG0002", out)

    def test_repeatable_id_batches(self) -> None:
        # CR0210: repeat --id instead of the comma spelling
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--id", "BG0001", "--id", "BG0002",
                         "--status", "Fixed", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("BG0001", out)
            self.assertIn("BG0002", out)

    def test_no_ids_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            rc = tr.main(["set", "--status", "Fixed", "--root", str(root)])
            self.assertEqual(rc, 2)

    def test_meta_type_refused_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RETRO0001", "Done")
            self.assertIn("meta", str(cm.exception).lower())


class BatchJsonCleanTests(unittest.TestCase):
    def test_batch_json_stdout_is_parseable(self) -> None:
        # critic finding: the human batch summary must not pollute json stdout
        import io, json as _json
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text(
                "# BG0001: a\n\n> **Status:** Open\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
            (bd / "_index.md").write_text(
                "# B\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [BG0001](BG0001-x.md) | a | Open |\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--ids", "BG0001,BG9999", "--status", "In Progress",
                         "--root", str(root), "--format", "json"])
            _json.loads(buf.getvalue())   # must be pure JSON


class TelemetryOnCloseTests(unittest.TestCase):
    """BG0052: a terminal transition records the telemetry event - the loop's
    real close path must not bypass the calibration data (never a second call)."""

    def _bug(self, root: Path, status="In Progress"):
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True, exist_ok=True)
        (bd / "BG0001-x.md").write_text(
            f"# BG0001: a\n\n> **Status:** {status}\n"
            "> **Verification depth:** soak\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# B\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [BG0001](BG0001-x.md) | a | {status} |\n", encoding="utf-8")
        return root

    def _records(self, root: Path):
        # Through the public read, not a hard-coded path: where the evidence lives is
        # telemetry's business, and a test that pinned the path would have to be edited every
        # time it moved rather than checking the behaviour it cares about.
        import telemetry as tel
        return tel.read_all(root)

    def test_terminal_transition_records_exactly_one_event(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed")
            recs = self._records(root)
            self.assertEqual(len(recs), 1, recs)
            self.assertEqual(recs[0]["id"], "BG0001")
            self.assertEqual(recs[0]["type"], "bug")

    def test_non_terminal_transition_records_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), status="Open")
            tr.transition(root, "BG0001", "In Progress")
            self.assertEqual(self._records(root), [])

    def test_dry_run_records_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed", dry_run=True)
            self.assertEqual(self._records(root), [])

    def test_lifecycle_records_exactly_one_event(self) -> None:
        # Fixed -> Verified -> Closed is ONE unit closing once: one event, not three;
        # an idempotent re-close records nothing.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            _quiet(tr.transition, root, "BG0001", "Fixed")
            tr.transition(root, "BG0001", "Verified")
            tr.transition(root, "BG0001", "Closed")
            tr.transition(root, "BG0001", "Closed")
            self.assertEqual(len(self._records(root)), 1)

    def test_reopen_and_reclose_records_a_second_event(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed")
            tr.transition(root, "BG0001", "In Progress")   # reopened
            tr.transition(root, "BG0001", "Closed")
            recs = self._records(root)
            self.assertEqual(len(recs), 2)

    def test_fractional_wall_time_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.main(["set", "--id", "BG0001", "--status", "Closed",
                     "--root", str(root), "--wall-time-s", "12.5"])
            self.assertEqual(self._records(root)[0]["wall_time_s"], 12.5)

    def test_cli_metrics_pass_through(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root), "--iterations", "2",
                           "--verdict", "approve"])
            self.assertEqual(rc_, 0)
            recs = self._records(root)
            self.assertEqual(recs[0]["iterations"], 2)
            self.assertEqual(recs[0]["critic_verdict"], "approve")

    def test_close_threads_attempts_to_telemetry(self) -> None:
        # BG0152: a close that escalated must record every attempt through the SAME close
        # path, so unit_cost sums the true cost. Before the fix the metrics dict dropped
        # attempts/tokens/model entirely and every escalation landed as a flat record.
        import telemetry as tel
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root),
                           "--attempt", "haiku:1000", "--attempt", "opus:5000"])
            self.assertEqual(rc_, 0)
            rec = self._records(root)[0]
            self.assertEqual(rec["attempts"],
                             [{"model": "haiku", "tokens": 1000},
                              {"model": "opus", "tokens": 5000}])
            self.assertEqual(tel.unit_cost(root, rec)["tokens"], 6000)  # summed, not last-line

    def test_malformed_attempt_fails_fast_and_writes_nothing(self) -> None:
        # A bad --attempt is a usage error (rc 2), refused before any id is touched -
        # never caught and re-reported once per id, never a partial write.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root), "--attempt", "no-tokens-here"])
            self.assertEqual(rc_, 2)
            self.assertEqual(self._records(root), [])


class HonestSyncTests(unittest.TestCase):
    """index_synced reflects the real post-transition state (critic CR0042)."""

    def test_archived_row_reports_not_synced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
                "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n",
                encoding="utf-8")  # empty active table - the row lives in archive
            ad = sd / "archive" / "r1"
            ad.mkdir(parents=True)
            (ad / "story.md").write_text(
                "# story archive - r1\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](../../US0001-x.md) | s | Ready |\n", encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")
            self.assertFalse(res["index_synced"])      # archive row not synced - honest
            self.assertIsNotNone(res["warning"])

    def test_status_without_summary_row_now_syncs_by_insertion(self) -> None:
        # Formerly pinned index_synced=False: the writer could not ADD a
        # missing summary row, so the honest report was not-synced. The
        # summary-row insertion removed the limitation - the row is inserted
        # into the managed block and the sync report is truthfully True.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Status:** Ready\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")  # no Done summary row
            res = tr.transition(root, "US0001", "Done")
            self.assertTrue(res["index_synced"])
            text = (sd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("| Done | 1 |", text)
            self.assertIn("| Ready | 0 |", text)

    def test_no_status_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Epic:** EP0001\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_non_story_type_no_epic_cascade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text(
                "# CR-0001: c\n\n> **Status:** Proposed\n> **Decomposed-into:** EP0001\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n"
                "| Complete | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0001](CR0001-x.md) | c | Proposed |\n", encoding="utf-8")
            # G2 (US0122): a CR reaches Complete only when its children are resolved. Give it a
            # Done child epic so the completion is legitimate - this test is about the non-story
            # cascade/sync, not the derived-status gate.
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0001-c.md").write_text(
                "# EP0001: c\n\n> **Status:** Done\n> **Parent:** CR0001\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
            res = tr.transition(root, "CR0001", "Complete")
            self.assertTrue(res["index_synced"])
            self.assertIsNone(res["epic"])
            self.assertEqual(rc.detect_type("cr", root)["drift"], [])

    def test_epic_absent_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            # point the story at a non-existent epic
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "[EP0001: e](../epics/EP0001-e.md)", "[EP0099: gone](../epics/EP0099-gone.md)"),
                encoding="utf-8")
            res = tr.transition(root, "US0001", "Done", force=True)  # must not crash (cascade test)
            self.assertIsNone(res["epic"])
            self.assertTrue(res["index_synced"])


def _v3_bug_repo(root: Path, status: str = "inbox",
                 raised_by: str = "Scout; agent; 1") -> Path:
    """A schema-v3 repo with one bug in `status` carrying a structured Raised-by (US0065)."""
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True)
    (sd / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    bd = sd / "bugs"
    bd.mkdir(parents=True)
    (bd / "BG0001-x.md").write_text(
        f"# BG0001: b\n\n> **Status:** {status}\n> **Severity:** high\n"
        f"> **Raised-by:** {raised_by}\n\n## Summary\n\nx\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
    (bd / "_index.md").write_text(
        "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| inbox | 1 |\n| Open | 0 |\n\n## All\n\n| ID | Title | Status |\n"
        "| --- | --- | --- |\n| [BG0001](BG0001-x.md) | b | inbox |\n", encoding="utf-8")
    return root


class TriageGateTests(unittest.TestCase):
    """US0065: the v3 gated inbox->triaged transition recording triaged_by (AC1/AC2)."""

    def test_triage_gate_requires_triaged_by(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "BG0001", "Open")  # no triaged_by -> fail loud
            self.assertIn("triaging seat must be recorded", str(ctx.exception).lower())

    def test_triage_gate_enforces_separation_of_duties(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "BG0001", "Open", triaged_by="Scout; agent; 1")
            self.assertIn("separation of duties", str(ctx.exception).lower())

    def test_triage_gate_records_triaged_by_on_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            res = tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1")
            self.assertEqual(res["to"], "Open")
            text = _read(root, "bugs", "BG0001-x.md")
            self.assertIn("> **Status:** Open", text)
            self.assertIn("> **Triaged-by:** Knox; agent; 1", text)
            self.assertTrue(res["index_synced"])

    def test_triage_gate_dormant_under_v2(self) -> None:
        # No schema_version:3 -> the triage gate never fires; a normal bug transition
        # needs no triaged_by (era-gating keeps v2 projects untouched).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text(
                "# BG0001: b\n\n> **Status:** Open\n> **Severity:** high\n\n## Summary\n\nx\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            (bd / "_index.md").write_text(
                "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 1 |\n"
                "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [BG0001](BG0001-x.md) | b | Open |\n", encoding="utf-8")
            res = tr.transition(root, "BG0001", "In Progress")  # no triaged_by required
            self.assertEqual(res["to"], "In Progress")

    def test_triage_gate_allows_solo_human_self_triage_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Darren; human; 1")
            res = tr.transition(root, "BG0001", "Open", triaged_by="Darren; human; 1")
            self.assertEqual(res["to"], "Open")               # not deadlocked
            self.assertIn("solo-human self-triage", res["warning"])

    def test_triage_gate_covers_all_exits_from_inbox(self) -> None:
        # Leaving inbox by any exit is the triage act - not only the canonical accept
        # target - so an agent cannot sidestep triage by jumping to another state.
        for target in ("In Progress", "Superseded"):
            with tempfile.TemporaryDirectory() as d:
                root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
                with self.assertRaises(ValueError) as ctx:
                    tr.transition(root, "BG0001", target)  # no triaged_by
                self.assertIn("triaging seat must be recorded", str(ctx.exception).lower())

    def test_triage_gate_records_on_non_canonical_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            res = tr.transition(root, "BG0001", "In Progress", triaged_by="Knox; agent; 1")
            self.assertEqual(res["to"], "In Progress")
            self.assertIn("> **Triaged-by:** Knox; agent; 1",
                          _read(root, "bugs", "BG0001-x.md"))

    def test_triage_gate_dry_run_is_honest(self) -> None:
        # A dry-run preflight of a triage that would block must not report a false green.
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            with self.assertRaises(ValueError):
                tr.transition(root, "BG0001", "Open", dry_run=True)  # no triaged_by

    def test_triage_severity_recorded_alongside_raiser(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")  # raiser Severity: high
            tr.transition(root, "BG0001", "Open",
                          triaged_by="Knox; agent; 1", triage_severity="low")
            text = _read(root, "bugs", "BG0001-x.md")
            self.assertIn("> **Severity:** high", text)         # raiser's retained
            self.assertIn("> **Triage-severity:** low", text)   # triager's recorded


def _v3_story_repo(root: Path, affects: str = "docs/prd.md",
                   cfg_extra: str = "plan_review:\n  affects_files_threshold: 99\n"
                                    "  min_difficulty: extreme\n") -> Path:
    """A schema-v3 repo with one Ready story (spec-citing by default) + its index."""
    sd = root / "sdlc-studio"
    (sd / "stories").mkdir(parents=True)
    (sd / "reviews").mkdir(parents=True)
    (sd / ".config.yaml").write_text("schema_version: 3\n" + cfg_extra, encoding="utf-8")
    (sd / "stories" / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
        f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n"
        "### AC1: a\n- **Given** x\n- **When** y\n- **Then** z\n", encoding="utf-8")
    (sd / "stories" / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
        "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
    return root


class PlanReviewGateTests(unittest.TestCase):
    """US0090: a spec-derived story is blocked from entering In Progress until reviewed."""

    def test_triggered_story_blocked_entering_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))          # cites docs/prd.md -> trigger fires
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "US0001", "In Progress")
            self.assertIn("plan-review", str(ctx.exception).lower())

    def test_independent_plan_approve_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            cr = _load("critic", "critic.py")
            cr.record_verdict(root, "US0001", "APPROVE", reviewer="qa", author="dev",
                              phase="plan-review")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_override_field_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "> **Affects:** docs/prd.md",
                "> **Affects:** docs/prd.md\n> **Plan-Review-Override:** ops: hotfix"),
                encoding="utf-8")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_force_does_not_bypass(self) -> None:
        # The only sanctioned skip is the recorded override, never --force (AC3).
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "In Progress", force=True)

    def test_dry_run_is_honest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "In Progress", dry_run=True)

    def test_untriggered_story_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d), affects="a.py")   # no spec, low volume
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_direct_ready_to_done_is_blocked(self) -> None:
        # The gate's PURPOSE is defeated if a spec-derived story can be closed straight to
        # Done unreviewed - guard every entry to an implementation state, not just In Progress.
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "US0001", "Done")
            self.assertIn("plan-review", str(ctx.exception).lower())

    def test_forward_walk_after_review_reaches_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            cr = _load("critic", "critic.py")
            cr.record_verdict(root, "US0001", "APPROVE", reviewer="qa", author="dev",
                              phase="plan-review")
            self.assertEqual(tr.transition(root, "US0001", "In Progress")["to"], "In Progress")
            # In Progress -> Done is not re-gated (already past the pre-impl states)
            self.assertEqual(tr.transition(root, "US0001", "Done", force=True)["to"], "Done")

    def test_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            sd = root / "sdlc-studio"
            (sd / ".config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")       # gate no-op on v2




class AnnotateVerbTests(unittest.TestCase):
    """CR0209/US0116 AC1: a deterministic metadata-stamp verb."""

    def _bug(self, root: Path) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                     "> **Created-by:** sdlc-studio new\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        return p

    def test_annotate_inserts_a_new_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            rc = tr.main(["annotate", "--id", "BG0001",
                                  "--field", "Verification depth",
                                  "--value", "functional (tests red-first)", "--root", str(root)])
            self.assertEqual(rc, 0)
            body = p.read_text(encoding="utf-8")
            self.assertIn("> **Verification depth:** functional (tests red-first)", body)
            self.assertEqual(tr.sdlc_md.extract_field(body, "Verification depth"),
                             "functional (tests red-first)")

    def test_annotate_updates_in_place_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            for value in ("smoke", "functional (upgraded)"):
                rc = tr.main(["annotate", "--id", "BG0001",
                                      "--field", "Verification depth",
                                      "--value", value, "--root", str(root)])
                self.assertEqual(rc, 0)
            body = p.read_text(encoding="utf-8")
            self.assertEqual(body.count("**Verification depth:**"), 1)
            self.assertIn("functional (upgraded)", body)

    def test_annotate_unknown_id_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            rc = tr.main(["annotate", "--id", "BG9999", "--field", "F",
                                  "--value", "v", "--root", d])
            self.assertNotEqual(rc, 0)


class AllGatesInOneRefusalTests(unittest.TestCase):
    """CR0209/US0116 AC2: a blocked transition names EVERY unmet gate."""

    def test_v3_finding_refusal_names_depth_and_triage_together(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            msg = str(ctx.exception)
            self.assertIn("Verification depth", msg)
            self.assertIn("triage", msg.lower())




def _quiet(fn, *args, **kwargs):
    """Run `fn` with its diagnostics captured. A green suite must print nothing, or a real
    error hides in the noise - the repo's test-noise gate enforces that as a line budget."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args, **kwargs)


class DryRunHonestyTests(unittest.TestCase):
    """BG0213: a dry-run must give the same answer as the real run, and write nothing.

    A dry-run exists so an agent learns a transition's requirements BEFORE doing the work.
    One that reports success where the real run blocks is worse than none: the requirement
    is still met as a refusal afterwards, and the agent has been told the opposite in the
    meantime. The tier gate already fires on dry-run for exactly this reason, in a comment
    stating that an honest preflight surfaces the refusal a real run would hit; the bug-depth,
    depth-parity and AC-verify gates simply did not follow it.
    """

    def _bug_without_depth(self, root: Path) -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        (d / "BG0001-x.md").write_text(
            "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n> **Points:** 2\n\n"
            "## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")

    def test_a_dry_run_reports_the_refusal_the_real_run_gives(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            self.assertIn("Verification depth", str(ctx.exception))

    def test_the_dry_run_and_the_real_run_agree(self) -> None:
        # The two paths must differ only in whether the write happens.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            dry = real = None
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            except ValueError as exc:
                dry = str(exc)
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            except ValueError as exc:
                real = str(exc)
            self.assertEqual(dry, real, "dry-run and real run disagree about the same transition")
            self.assertIsNotNone(dry, "both must refuse; a passing pair proves nothing here")

    def test_a_refused_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            before = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            with self.assertRaises(ValueError):
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_a_satisfiable_transition_still_dry_runs_clean(self) -> None:
        # The negative branch: making the gates fire on dry-run must not make every dry-run
        # refuse, or the honesty fix would just be a different lie.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** Low",
                "> **Verification depth:** functional (reproduced)\n> **Severity:** Low"),
                encoding="utf-8")
            res = _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            self.assertEqual(res["to"], "Fixed")
            self.assertIn("> **Status:** Open", p.read_text(encoding="utf-8"))

    def test_a_story_done_dry_run_reports_the_ac_verify_refusal(self) -> None:
        """The STORY half of the same fix, which the bug cases cannot reach.

        Restoring `not dry_run` on the AC-verify gate alone left the whole suite green -
        every other test here exercises a BUG, so the story branch was unpinned while the
        commit claimed the fix applied to all of them.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))       # US0001 declares an executable AC, never verified
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertIn("never verified", str(ctx.exception))
            self.assertIn("> **Status:** Ready", _read(root, "stories", "US0001-x.md"))

    def test_a_story_dry_run_reports_the_depth_parity_refusal(self) -> None:
        """The THIRD gate the BG0213 fix changed, which had no test at all.

        Restoring `not dry_run` on this branch left the entire suite green, while the commit
        claimed the fix covered all three gates it touched. It is advisory by default, so the
        project must opt in via `quality.depth_parity_gate` for it to refuse - which is why
        the other story tests never reach it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "quality:\n  depth_parity_gate: true\n  done_requires_verified: false\n",
                encoding="utf-8")
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "- **Verify:** shell echo ok",
                "- **Verification target:** soak\n- **Verify:** shell echo ok"),
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertIn("Verification target", str(ctx.exception))
            self.assertIn("> **Status:** Ready", sp.read_text(encoding="utf-8"))

    def test_force_still_waives_the_gate_on_a_dry_run(self) -> None:
        # `--force` is a legitimate override, so a forced dry-run must report what a forced
        # real run would do - not refuse. Dropping `not dry_run` without keeping `not force`
        # would break this.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            res = _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True, force=True)
            self.assertEqual(res["to"], "Fixed")


class RequirementsPreflightTests(unittest.TestCase):
    """US0267: ask what a transition needs BEFORE doing the work."""

    def _bug(self, root: Path, depth: str = "") -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        line = f"> **Verification depth:** {depth}\n" if depth else ""
        p = d / "BG0001-x.md"
        p.write_text(f"# BG0001: x\n\n> **Status:** Open\n{line}"
                     "> **Severity:** Low\n> **Points:** 2\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                     encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")
        return p

    def test_requirements_listed_before_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertEqual(len(unmet), 1)
            self.assertIn("Verification depth", unmet[0])

    def test_a_satisfied_transition_reports_nothing_unmet(self) -> None:
        # The negative branch: a command that always found a requirement would be useless
        # and would still pass the assertion above.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, depth="functional (reproduced)")
            self.assertEqual(_quiet(tr.requirements, root, "BG0001", "Fixed"), [])

    def test_asking_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_requirements_are_not_duplicated(self) -> None:
        """AC3: the text comes from the gate, so it cannot drift from the gate.

        Proven by changing the GATE's wording and watching the reported requirement change
        with it. A hand-maintained copy in the reporter would keep the old words and pass
        every other test in this class.
        """
        sentinel = "SENTINEL-GATE-WORDING"
        original = tr._bug_depth_gate
        try:
            tr._bug_depth_gate = lambda text, target: sentinel
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._bug(root)
                unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertTrue(any(sentinel in u for u in unmet),
                            "the reporter restates requirements instead of deriving them")
        finally:
            tr._bug_depth_gate = original

    def test_an_unknown_id_raises_rather_than_reporting_a_bogus_requirement(self) -> None:
        """A lookup failure must never masquerade as a requirement.

        The first version parsed ANY ValueError into the unmet list, so asking about a
        nonexistent id answered "you must satisfy: <not-found message>" - a confidently wrong
        answer, which is the class of defect this command exists to end. Caught by the
        briefing's own unresolvable-unit test rather than by reading.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            with self.assertRaises((ValueError, FileNotFoundError)):
                _quiet(tr.requirements, root, "BG9999", "Fixed")

    def _two_suffix_free_gates(self, root: Path) -> None:
        """A story that trips the TIER gate and the PLAN-REVIEW gate.

        Both state their reason WITHOUT the `". Override with --force"` suffix, which is the
        case the old prose-splitting collapsed into one item. Every earlier attempt at this
        test used a fixture where one of the two blocks carried the suffix, so the wrong
        delimiter still yielded two and the test passed on the defect.
        """
        (root / "sdlc-studio").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir()
        # `Template: full` with none of the sections the full tier promises -> tier gate.
        # Ready -> In Progress on a schema-v3 story -> plan-review gate.
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Ready\n> **Template:** full\n"
            "> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        ed = root / "sdlc-studio" / "epics"
        ed.mkdir()
        (ed / "EP0001-e.md").write_text(
            "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
            "- [ ] [US0001: s](../stories/US0001-x.md)\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")

    def test_two_suffix_free_gates_are_two_requirements_not_one(self) -> None:
        """THE case the re-parsing collapsed - driven through the real ladder.

        The previous version of this test constructed a `GateRefusal` by hand and asserted
        `__init__` stored its argument. No gate ran, `requirements()` was never called, and
        the defective code it claimed to catch was never executed - so re-introducing the
        merge left the whole suite green. A test that names a defect it cannot reach is worse
        than no test: it reads as coverage.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._two_suffix_free_gates(root)
            unmet = _quiet(tr.requirements, root, "US0001", "In Progress")
        self.assertEqual(len(unmet), 2, f"two gates collapsed into {len(unmet)}: {unmet}")
        joined = " ".join(unmet)
        self.assertIn("full", joined)          # the tier gate's reason
        self.assertIn("plan-review", joined)   # the plan-review gate's reason
        for item in unmet:
            self.assertNotIn("; AND ", item)

    def test_the_refusal_carries_its_blocks_as_data(self) -> None:
        # The mechanism, exercised through the real ladder rather than a hand-built object:
        # `blocks` must match what the message claims, so the two can never disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._two_suffix_free_gates(root)
            try:
                _quiet(tr.transition, root, "US0001", "In Progress", dry_run=True)
                self.fail("expected the ladder to refuse")
            except tr.GateRefusal as exc:
                self.assertEqual(len(exc.blocks), 2)
                self.assertIsInstance(exc, ValueError)   # every existing caller still catches
                stated = int(re.search(r"blocked \((\d+) requirement", str(exc)).group(1))
                self.assertEqual(stated, len(exc.blocks))

    def test_no_requirement_carries_the_ladders_join_token(self) -> None:
        # The observable symptom of re-parsing: a leaked `; AND ` inside an item.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
        self.assertGreaterEqual(len(unmet), 2)
        for item in unmet:
            self.assertNotIn("; AND ", item, f"the join token leaked into an item: {item!r}")

    def test_the_reported_count_matches_the_gates_own_count(self) -> None:
        # The two numbers came from different places and could disagree; now they cannot.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed")
                self.fail("expected the gate to refuse")
            except ValueError as exc:
                stated = int(re.search(r"blocked \((\d+) requirement", str(exc)).group(1))
        self.assertEqual(len(unmet), stated)

    def test_every_unmet_gate_is_listed_not_just_the_first(self) -> None:
        # The ladder collects all refusals into one message; the reporter must split them
        # back out rather than returning the joined blob as a single item.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertGreaterEqual(len(unmet), 2, f"expected several requirements, got {unmet}")
            joined = " ".join(unmet)
            self.assertIn("Verification depth", joined)
            self.assertIn("triage", joined.lower())


class AnnotateCannotBypassGatesTests(unittest.TestCase):
    """Critic F1/F2/F5: annotate must never touch gated/index-backed fields, must fail loud
    without a Status anchor, and must reject metadata-injection values."""

    def _v3_inbox_bug(self, root: Path) -> Path:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(exist_ok=True)
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n"
                     "## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        return p

    def test_annotate_refuses_the_status_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            for spelling in ("Status", "status", "STATUS"):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", spelling,
                              "--value", "Fixed", "--root", str(root)])
                self.assertNotEqual(rc, 0, spelling)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_refuses_the_provenance_security_stamp(self) -> None:
        # Closing-critic F1: Provenance is a verify_ac shell-gate control - annotate clearing
        # it exit-0 re-enabled shell on untrusted content. It must be denylisted like Status.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** Low\n", "> **Severity:** Low\n> **Provenance:** external\n"),
                encoding="utf-8")
            before = p.read_text(encoding="utf-8")
            for spelling in ("Provenance", "provenance", " Provenance "):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", spelling,
                              "--value", "internal", "--root", str(root)])
                self.assertNotEqual(rc, 0, spelling)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_refuses_triage_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            rc = tr.main(["annotate", "--id", "BG0001", "--field", "Triaged-by",
                          "--value", "Me; human; 1", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_fails_loud_without_a_status_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text("# BG0001: x\n\nno metadata block\n",
                                            encoding="utf-8")
            rc = tr.main(["annotate", "--id", "BG0001", "--field", "Verification depth",
                          "--value", "functional", "--root", str(root)])
            self.assertNotEqual(rc, 0)

    def test_annotate_rejects_newlines_in_field_and_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            for sep in ("\n", "\r", "\u2028"):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", "Verification depth",
                              "--value", f"functional{sep}> **Status:** Fixed",
                              "--root", str(root)])
                self.assertNotEqual(rc, 0, repr(sep))
            self.assertEqual(p.read_text(encoding="utf-8"), before)


class OneCallCloseTests(unittest.TestCase):
    """CR0213: the three-verb bug close (annotate depth, record verdict, gated set) collapses
    to one call - and every predictable refusal happens BEFORE any write."""

    def _bug(self, root: Path) -> Path:
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n", encoding="utf-8")
        return root

    def test_one_call_stamps_records_and_transitions(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            with redirect_stdout(io.StringIO()):
                rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                              "--depth", "functional (one-call test)",
                              "--verdict", "approve", "--reviewer", "Blake", "--author", "Alex",
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Fixed", text)
            self.assertIn("Verification depth:** functional (one-call test)", text)
            log = (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").read_text(encoding="utf-8")
            self.assertIn("BG0001", log)
            self.assertIn("Blake", log)

    def test_self_review_refused_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                          "--depth", "functional", "--verdict", "approve",
                          "--reviewer", "Alex", "--author", "Alex", "--root", str(root)])
            self.assertEqual(rc, 2)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** In Progress", text)           # no transition
            self.assertNotIn("Verification depth", text)               # no depth stamp either
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_reviewer_without_author_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                          "--verdict", "approve", "--reviewer", "Blake", "--root", str(root)])
            self.assertEqual(rc, 2)

    def test_statically_undershooting_depth_refuses_before_any_write(self) -> None:
        # Critic repro: --depth smoke --status Verified is a pure function of the flags -
        # it must refuse with NO stamp and NO verdict row, not stamp-then-block.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            before = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            rc = tr.main(["set", "--id", "BG0001", "--status", "Verified",
                          "--depth", "smoke", "--verdict", "approve",
                          "--reviewer", "r1", "--author", "a1", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)  # byte-identical: no stamp landed
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_depth_alone_still_gates_normally(self) -> None:
        # --depth without reviewer/author: stamp + gated transition, no verdict recording
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            with redirect_stdout(io.StringIO()):
                rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                              "--depth", "functional (stamp only)", "--root", str(root)])
            self.assertEqual(rc, 0)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Fixed", text)


class MetadataLineInjectionTests(unittest.TestCase):
    """Every writer of a metadata line inherits ONE refusal (`sdlc_md.require_single_line` in
    `_upsert_field`), rather than each caller remembering to escape. `annotate` guarded its own
    value; the triage stamps went straight to the writer and did not, so a triage record could
    write arbitrary metadata lines into the artefact it was closing."""

    BREAK = "\n> **Evil:** injected"

    def test_triaged_by_cannot_inject_a_metadata_line(self) -> None:
        # the fixture reproduction: --triaged-by $'Dani Okafor; human; v1\n> **Evil:** injected'
        # stamped a `> **Evil:**` line that `extract_field` read back
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Open",
                              triaged_by="Dani Okafor; human; v1" + self.BREAK)
            self.assertIn("single line", str(cm.exception))
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIsNone(tr.sdlc_md.extract_field(text, "Evil"))
            self.assertNotIn("Evil", text)

    def test_triage_severity_cannot_inject_a_metadata_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1",
                              triage_severity="low" + self.BREAK)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertNotIn("Evil", text)

    def test_the_whole_line_breaking_class_is_refused_at_the_writer(self) -> None:
        for ch in ("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85",
                   "\u2028", "\u2029", "\x00"):
            with self.subTest(ch=repr(ch)):
                with self.assertRaises(ValueError):
                    tr._upsert_field("# x\n\n> **Status:** Open\n", "Triaged-by",
                                     f"Knox{ch}> **Evil:** injected")
                with self.assertRaises(ValueError):
                    tr._upsert_field("# x\n\n> **Status:** Open\n", f"Bad{ch}Field", "v")

    def test_annotate_still_refuses_and_a_clean_stamp_still_lands(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.annotate(root, "BG0001", "Verification depth", "functional" + self.BREAK)
            res = tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1",
                                triage_severity="low")
            self.assertEqual(res["to"], "Open")
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Triaged-by:** Knox; agent; 1", text)
            self.assertIn("> **Triage-severity:** low", text)


class AcFingerprintFreshnessTests(unittest.TestCase):
    """US0213: freshness must be judged on what the verifier ran against, not on mtime.

    A Status transition, a Revision History row, and verify_ac's own `**Verified:**` stamps
    all bump mtime while leaving every AC and verifier untouched - under the mtime rule a
    correct green was rejected as "edited after it was last verified", forcing a re-run that
    could only ever produce the same result."""

    STORY = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
             "### AC1: it works\n- **Verify:** shell true\n")

    def _root(self, d, body=None):
        root = Path(d)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "US0001-x.md").write_text(body or self.STORY, encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return root

    def _report(self, root, entry):
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps({"stories": {"US0001-x": entry}}), encoding="utf-8")

    def _fp(self, text):
        import verify_ac
        return verify_ac.ac_fingerprint(text)

    def _green(self, text, **over):
        return {"failed": 0, "stale": 0, "failures": [],
                "verified_at": "2000-01-01T00:00:00Z",      # long in the past: mtime WILL be newer
                "ac_fingerprint": self._fp(text), **over}

    def test_metadata_edit_stays_fresh(self) -> None:
        """AC1: an edit outside the AC section must not invalidate the green."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            self._report(root, self._green(self.STORY))
            # touch metadata only - a Revision History row, exactly what closing paperwork adds
            p = root / "sdlc-studio" / "stories" / "US0001-x.md"
            p.write_text(self.STORY + "\n## Revision History\n\n| 2026-07-18 | me | edited |\n",
                         encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_ac_edits_invalidate(self) -> None:
        """AC2: retitling an AC, re-pointing a verifier, or adding an AC each block."""
        mutations = {
            "retitled": "### AC1: it works differently\n- **Verify:** shell true\n",
            "re-pointed": "### AC1: it works\n- **Verify:** shell false\n",
            "added": "### AC1: it works\n- **Verify:** shell true\n\n"
                     "### AC2: more\n- **Verify:** shell true\n",
        }
        for label, acs in mutations.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = self._root(d)
                self._report(root, self._green(self.STORY))
                edited = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n" + acs)
                (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(edited, encoding="utf-8")
                with self.assertRaises(ValueError):
                    tr.transition(root, "US0001", "Done")

    def test_legacy_report_falls_back_to_mtime(self) -> None:
        """AC3: a pre-fingerprint report must not silently pass - mtime still governs."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            entry = self._green(self.STORY)
            entry.pop("ac_fingerprint")          # written before the field existed
            self._report(root, entry)
            with self.assertRaises(ValueError):  # story mtime is newer than verified_at
                tr.transition(root, "US0001", "Done")


class AcFingerprintTests(unittest.TestCase):
    """US0213 AC4: the fingerprint covers ACs and verifiers, and nothing else."""

    BASE = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            "### AC1: it works\n- **Verify:** shell true\n")

    def _fp(self, text):
        import verify_ac
        return verify_ac.ac_fingerprint(text)

    def test_metadata_does_not_change_the_fingerprint(self) -> None:
        noise = self.BASE.replace("**Status:** Ready", "**Status:** Done") + \
            "\n## Revision History\n\n| d | a | c |\n"
        self.assertEqual(self._fp(self.BASE), self._fp(noise))

    def test_verified_stamp_does_not_change_the_fingerprint(self) -> None:
        stamped = self.BASE + "- **Verified:** yes (2026-07-18)\n"
        self.assertEqual(self._fp(self.BASE), self._fp(stamped))

    def test_verifier_change_changes_the_fingerprint(self) -> None:
        self.assertNotEqual(self._fp(self.BASE),
                            self._fp(self.BASE.replace("shell true", "shell false")))

    def test_ac_count_change_changes_the_fingerprint(self) -> None:
        self.assertNotEqual(
            self._fp(self.BASE),
            self._fp(self.BASE + "\n### AC2: more\n- **Verify:** shell true\n"))


def _rfc_repo(root: Path, status: str = "In Review", rows: str | None = None,
              override: str | None = None) -> Path:
    """An RFC with an Open Decisions table, the shape reference-rfc.md's accept step reads."""
    d = root / "sdlc-studio" / "rfcs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# RFC0001: r\n\n> **Status:** {status}\n"
    if override:
        body += f"> **Decision-Override:** {override}\n"
    table = rows if rows is not None else "| D1 | Act on this finding or keep status quo | Open |\n"
    body += ("\n## Summary\n\nx\n\n## Open Decisions\n\n"
             "| # | Decision | Status |\n| --- | --- | --- |\n" + table)
    (d / "RFC0001-r.md").write_text(body, encoding="utf-8")
    (d / "_index.md").write_text(
        "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [RFC0001](RFC0001-r.md) | r | {status} |\n", encoding="utf-8")
    return root


class RfcOpenDecisionGateTests(unittest.TestCase):
    """US0244 AC1: an RFC cannot reach Accepted while a decision row is still Open.

    reference-rfc.md's accept step already forbade this in prose, and six RFCs were
    Accepted, decomposed and delivered carrying nothing but the boilerplate Open row.
    A gate that lives only in prose fires when somebody remembers.
    """

    def test_open_decision_refuses_the_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("D1", str(cm.exception))
            self.assertIn("Status:** In Review", _read(root, "rfcs", "RFC0001-r.md"))

    def test_every_open_row_is_named_not_just_the_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "| D1 | first | Open |\n| D2 | second | Closed |\n| D3 | third | Open |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            msg = str(cm.exception)
            self.assertIn("D1", msg)
            self.assertIn("D3", msg)
            self.assertNotIn("D2", msg)  # a Closed row is not a blocker

    def test_all_decisions_closed_lets_the_transition_through(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows="| D1 | settled | Closed |\n")
            tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_annotated_open_cell_still_counts_as_open(self) -> None:
        """A status cell carrying its reasoning is the shape real RFCs use.

        RFC0042 D2 reads `Open - the mechanism detail for the blocking lane`. A reader that
        demands the bare word misses it and reports the file clean - a false negative in the
        gate, which is worse than the prose rule it replaced.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "| D1 | Enforcement mechanism | Resolved: option D (soft nudge + blocking lane) |\n"
                "| D2 | How to detect the trigger | Open - the mechanism detail for the lane |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            msg = str(cm.exception)
            self.assertIn("D2", msg)
            self.assertNotIn("D1", msg)  # 'Resolved: ...' is settled, not open

    def test_the_reader_is_not_locked_to_one_table_shape(self) -> None:
        """Four false negatives found by the closing review, all the same root cause.

        The reader hardcoded three columns, split on every pipe, matched only `## `
        headings, and accepted only the bare leading word `Open`. Each is a way for a real
        Open decision to pass the gate silently - the outcome the docstring calls worse
        than the prose rule it replaced, because it also looks like proof.
        """
        shapes = {
            "four columns": ("| # | Decision | Options | Status |\n| --- | --- | --- | --- |\n"
                             "| D1 | which store | sqlite/postgres | Open |\n"),
            "pipe in a cell": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                               r"| D1 | keep a \| b | Open |" + "\n"),
            "unresolved": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                           "| D1 | which store | Unresolved |\n"),
            "pending": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                        "| D1 | which store | Pending operator |\n"),
        }
        for name, rows in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=rows)
                with self.assertRaises(ValueError, msg=f"{name}: Open decision passed"):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_comment_in_a_fenced_block_does_not_end_the_section(self) -> None:
        """Widening the heading match to any line starting with `#` created a NEW bypass.

        A shell comment inside a fenced code block begins with `#`, contains no "decision",
        and so switched the section OFF - every Open row after it invisible. The pre-repair
        code was correct here. Only a real ATX heading is a boundary, and nothing inside a
        fence is a heading at all.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "```bash\n# regenerate the table\n```\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | which store | Open |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("D1", str(cm.exception))

    def test_fence_handling_cannot_hide_the_decisions_section(self) -> None:
        """Fence tracking must never DISABLE the gate - the round 2 repair did exactly that.

        A naive `in_fence = not in_fence` toggle treats any fence-like line as a delimiter, so
        an unclosed fence, or a nested longer fence containing a shorter one, left the tracker
        inside a fence at EOF and made the whole decisions section invisible. That is a wider
        bypass than the `#`-in-a-fence case it was fixing, and the code it replaced caught all
        of these. Two guards now: proper CommonMark matching (a fence closes only on the same
        character at the same length or longer), and a fail-closed re-scan if the tracker still
        ends inside a fence, because unparseable markdown must not read as no open decisions.
        """
        table = ("\n| # | Decision | Status |\n| --- | --- | --- |\n"
                 "| D1 | which store | Open |\n")
        shapes = {
            "unclosed fence before the section": "```bash\necho hi\n\n## Open Decisions\n" + table,
            "nested four-backtick fence": (
                "````markdown\n```bash\n````\n\n## Open Decisions\n" + table),
            "tilde fence never closed": "~~~\nstuff\n\n## Open Decisions\n" + table,
            "fence opened inside the section": (
                "## Open Decisions\n\n```bash\n# regenerate\n```\n" + table),
            # The fail-closed re-scan dropped the FENCE rule but kept the SECTION rule, so a
            # `#` comment inside the unterminated fence ended the section and hid every row
            # after it. The fallback then returned "no open decisions" for the exact document
            # it exists to catch: the gate advertised fail-closed and failed OPEN. The two
            # structural signals fail together, so the fallback now drops both.
            "unclosed fence whose body holds a # comment": (
                "## Open Decisions\n\n```bash\n# regenerate the table\n" + table),
            "unclosed tilde fence whose body holds a # comment": (
                "## Open Decisions\n\n~~~bash\n# regenerate the table\n" + table),
        }
        for name, body in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                rd = root / "sdlc-studio" / "rfcs"
                rd.mkdir(parents=True)
                (rd / "RFC0001-r.md").write_text(
                    "# RFC0001: r\n\n> **Status:** In Review\n\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n" + body, encoding="utf-8")
                (rd / "_index.md").write_text(
                    "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                    "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
                with self.assertRaises(ValueError, msg=f"{name}: gate bypassed"):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_fence_hiding_only_some_rows_still_names_every_open_decision(self) -> None:
        """The fail-closed re-scan must fire on an unterminated fence, not only on an empty read.

        The guard was `fence is not None and not open_rows`, so the fallback ran only when the
        main scan found NOTHING. With one open row before a broken fence and another after it,
        the first is found, `not open_rows` is False, the re-scan never fires, and the caller
        gets an INCOMPLETE list. Both callers print that list, so the operator is told the RFC
        carries one open decision, D1, when it carries two.

        The gate still blocks and it converges - closing D1 and re-running surfaces D7 - so this
        costs a round trip rather than correctness. It is still a false completeness claim in
        operator-facing output (BG0207).
        """
        body = ("## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | which store | Open |\n\n"
                "```bash\necho 'never closed'\n\n"
                "| D7 | which format | Open |\n")
        self.assertEqual(tr._rfc_open_decisions(body), ["D1", "D7"])

    def test_commonmark_fence_matching_is_pinned_independently_of_the_fallback(self) -> None:
        """The CommonMark `(char, length)` rule needs a test the FALLBACK cannot satisfy.

        Every other fence test asserts the gate BLOCKS, and the fail-closed re-scan blocks on
        its own - so reverting the matcher to a naive `in_fence = not in_fence` toggle left
        them all green and the headline guard untested. Only a case where the correct answer
        is "no open decisions" separates the two: a well-formed nested fence, closed properly,
        holding an EXAMPLE row.

        Correct CommonMark: ```` opens, the inner ``` is content, the trailing ```` closes.
        The tracker ends outside any fence, the example row was skipped, the gate passes.
        Under the naive toggle the inner ``` counts as a delimiter, the file ends inside a
        fence, the fail-closed re-scan fires and reads the example row as real - so accepting
        this RFC raises. The mutant FAILS this test where it passes all the others.
        """
        body = ("## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | which store | Accepted |\n\n"
                "````markdown\n```text\n| D9 | an example row, not a decision | Open |\n"
                "```\n````\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n" + body, encoding="utf-8")
            (rd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            tr.transition(root, "RFC0001", "Accepted")   # must NOT raise

    def test_a_hash_that_is_not_a_heading_does_not_end_the_section(self) -> None:
        """`#42` and `#!/bin/sh` start with `#` but are not headings."""
        for line in ("#42 is the issue this row came from", "#!/usr/bin/env bash"):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=(
                    f"{line}\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                    "| D1 | q | Open |\n"))
                with self.assertRaises(ValueError):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_decisions_section_at_any_heading_level_is_read(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n### Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | q | Open |\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n",
                encoding="utf-8")
            (rd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tr.transition(root, "RFC0001", "Accepted")

    def test_a_settled_row_still_passes_in_every_shape(self) -> None:
        """Widening what counts as open must not start blocking settled work."""
        for cell in ("Closed", "Resolved: option D", "Superseded by RFC0050", "Done"):
            with self.subTest(cell=cell), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=f"| D1 | q | {cell} |\n")
                tr.transition(root, "RFC0001", "Accepted")
                self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_rfc_with_no_decision_table_is_unaffected(self) -> None:
        """The gate must not invent a blocker for an RFC that never had a table."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "rfcs"
            dd.mkdir(parents=True)
            (dd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n## Summary\n\nx\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))


class RfcDecisionOverrideTests(unittest.TestCase):
    """US0244 AC2: the only escape is a RECORDED override, never a bare --force.

    Mirrors the Plan-Review-Override convention: a skip that leaves a reason in the
    file is auditable, a --force is not.
    """

    def test_recorded_override_permits_the_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), override="D1 settled verbally at the 07-19 review")
            res = tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))
            self.assertIn("settled verbally", (res.get("warning") or ""))

    def test_bare_force_does_not_bypass_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted", force=True)
            self.assertIn("Decision-Override", str(cm.exception))
            self.assertIn("Status:** In Review", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_empty_override_is_not_an_override(self) -> None:
        """A field present but blank records no reason, so it cannot buy a skip."""
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), override="   ")
            with self.assertRaises(ValueError):
                tr.transition(root, "RFC0001", "Accepted")


class UnspecifiedAcDoneGateTests(unittest.TestCase):
    """BG0316: an AC carrying NO `Verify:` line at all must not be cheaper than one that
    honestly declares `Verify: manual`.

    The gate blocked a bare manual AC (BG0300) while waving through a criterion with no
    verifier at all, so omitting the line was the cheapest way to Done - and the release
    lane (`gate.py._verify_acs`) refuses the same story, so it failed only at tag time.
    """

    def _story(self, root: Path, acs: str) -> Path:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-x.md"
        p.write_text("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n" + acs,
                     encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return p

    def test_ac_with_no_verify_line_blocks_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root, "### AC1\n- Given x\n\n### AC2\n- Given y\n")
            with self.assertRaises(ValueError) as cm:
                _quiet(tr.transition, root, "US0001", "Done")
            msg = str(cm.exception)
            self.assertIn("AC1", msg)
            self.assertIn("AC2", msg)
            self.assertIn("Verify:", msg)
            self.assertIn("> **Status:** Ready", p.read_text(encoding="utf-8"))

    def test_omission_is_never_cheaper_than_declaration(self) -> None:
        # The parity the bug is about: the honest `Verify: manual` AC and the silent one
        # must both refuse. A pass on either side inverts the incentive.
        for acs in ("### AC1\n- **Verify:** manual eyeball it\n", "### AC1\n- Given x\n"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, acs)
                with self.assertRaises(ValueError) as cm:
                    _quiet(tr.transition, root, "US0001", "Done")
                self.assertIn("AC1", str(cm.exception))

    def test_recorded_human_evidence_lets_it_through(self) -> None:
        # Symmetric with the manual path: the gate cannot judge the outcome, but a recorded
        # PASSING human verdict is evidence somebody looked.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "### AC1\n- Given x\n- **Verify:** manual a human checks x\n"
                              "- **Verified:** yes (2026-07-27)\n")
            res = _quiet(tr.transition, root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_a_bare_ac_is_not_rescued_by_a_verified_marker(self) -> None:
        # The release lane counts an AC with no Verify line as unspecified whatever markers sit
        # under it. If this gate exempted it, the two would disagree and Done would not survive
        # to tag time.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "### AC1\n- Given x\n- **Verified:** yes (2026-07-27)\n")
            with self.assertRaises(tr.GateRefusal):
                _quiet(tr.transition, root, "US0001", "Done")

    def test_the_transition_gate_and_the_release_lane_agree(self) -> None:
        # The differential the review asked for: one file, both lanes, same verdict.
        import verify_ac
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "### AC1\n- Given x\n- **Verified:** yes (2026-07-27)\n")
            path = root / "sdlc-studio" / "stories" / "US0001-x.md"
            blocked = False
            try:
                _quiet(tr.transition, root, "US0001", "Done")
            except tr.GateRefusal:
                blocked = True
            report = verify_ac.verify_story(path, dry_run=True, timeout=10, repo_root=root)
            self.assertTrue(blocked, "the transition gate let a bare AC through")
            self.assertGreaterEqual(report.unspecified, 1,
                                    "the release lane did not see it unspecified")

    def test_force_still_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "### AC1\n- Given x\n")
            res = _quiet(tr.transition, root, "US0001", "Done", force=True)
            self.assertEqual(res["to"], "Done")


class ForcedOverrideRecordTests(unittest.TestCase):
    """BG0314: `--force` advertised the bypass as `recorded as an override` and recorded
    nothing - a forced close of a red-AC story was byte-identical to a verified one."""

    def _story(self, root: Path, body: str | None = None) -> Path:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-x.md"
        p.write_text(body or ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
                              "### AC1\n- **Verify:** shell true\n\n## Revision History\n\n"
                              "| Date | Author | Change |\n| --- | --- | --- |\n"
                              "| 2026-07-27 | a | Filed |\n"), encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return p

    def test_forced_bypass_is_recorded_on_the_artefact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root)
            res = _quiet(tr.transition, root, "US0001", "Done", force=True)
            text = p.read_text(encoding="utf-8")
            self.assertIn("Forced-override", text)          # the durable record
            self.assertIn("never verified", text)           # naming the gate it waived
            self.assertTrue(res.get("forced_override"))     # and reported to the caller

    def test_the_record_names_every_bypassed_gate_in_the_revision_log(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root)
            _quiet(tr.transition, root, "US0001", "Done", force=True)
            rows = [ln for ln in p.read_text(encoding="utf-8").splitlines()
                    if ln.startswith("|") and "force" in ln.lower()]
            self.assertTrue(rows, "no Revision History row records the forced bypass")

    def test_force_with_nothing_to_bypass_records_nothing(self) -> None:
        # A force that waived no gate is not an override, and claiming one would be the
        # same dishonesty in the opposite direction.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
                                  "### AC1\n- **Verify:** manual eyeball\n"
                                  "- **Verified:** yes (2026-07-27)\n")
            res = _quiet(tr.transition, root, "US0001", "Done", force=True)
            self.assertNotIn("Forced-override", p.read_text(encoding="utf-8"))
            self.assertIsNone(res.get("forced_override"))

    def test_a_forced_dry_run_writes_no_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root)
            before = p.read_text(encoding="utf-8")
            _quiet(tr.transition, root, "US0001", "Done", dry_run=True, force=True)
            self.assertEqual(before, p.read_text(encoding="utf-8"))


class OneCallPreflightTests(unittest.TestCase):
    """BG0315: `cmd_set`'s one-call close must pre-flight the WHOLE gate ladder before it
    writes anything, and its `--dry-run` must judge the same text the real run will."""

    def _story(self, root: Path) -> Path:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        p = sd / "US0001-x.md"
        p.write_text("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
                     "### AC1\n- **Verify:** shell true\n", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return p

    def _bug(self, root: Path) -> Path:
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True, exist_ok=True)
        p = bd / "BG0001-x.md"
        p.write_text("# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n", encoding="utf-8")
        return p

    def test_a_refused_close_leaves_no_stamp_and_no_verdict_row(self) -> None:
        # The AC-verify gate refuses this close, but the depth stamp and the critic verdict
        # were already on disk by the time it ran - a persistent record of a close that
        # never happened.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root)
            before = p.read_text(encoding="utf-8")
            rc_val = _quiet(tr.main, ["set", "US0001", "Done", "--depth", "functional",
                                      "--verdict", "approve", "--reviewer", "Blake",
                                      "--author", "Alex", "--root", str(root)])
            self.assertNotEqual(rc_val, 0)
            self.assertEqual(before, p.read_text(encoding="utf-8"))   # byte-identical
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_depth_dry_run_agrees_with_the_real_run(self) -> None:
        # `--depth functional --dry-run` judged the UN-stamped file and refused what the
        # identical real command accepts: the preview/run divergence `pending_fields` exists
        # to close, on the one path that never passed it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            dry = _quiet(tr.main, ["set", "BG0001", "Fixed", "--depth", "functional",
                                   "--dry-run", "--root", str(root)])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            real = _quiet(tr.main, ["set", "BG0001", "Fixed", "--depth", "functional",
                                    "--root", str(root)])
        self.assertEqual((dry, real), (0, 0), "dry-run and real run disagree")

    def test_the_dry_run_still_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            _quiet(tr.main, ["set", "BG0001", "Fixed", "--depth", "functional",
                             "--dry-run", "--root", str(root)])
            self.assertEqual(before, p.read_text(encoding="utf-8"))


class CriteriaFloorAtTheVerbTests(unittest.TestCase):
    """BG0378. BG0370 closed the criteria floor at the VALIDATE layer, which the pre-commit
    gate enforces - so a unit could not LAND at a terminal status with no criteria. The verb
    still performed the change, and the refusal arrived later, from a different tool, phrased
    as a validation error. Defence at the gate rather than at the verb is weaker than the rule
    reads, and it leaves the working tree in the state the rule forbids."""

    def _bug(self, root: Path, ident: str = "BG0001", criteria: str = "") -> Path:
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        p = bugs / f"{ident}-x.md"
        p.write_text(
            f"# {ident}: a defect\n\n> **Status:** Open\n> **Severity:** Low\n"
            f"> **Points:** 1\n> **Verification depth:** functional\n\n"
            f"## Summary\n\nx\n\n## Acceptance Criteria\n\n{criteria}\n",
            encoding="utf-8")
        return p

    def test_a_terminal_transition_with_no_criteria_is_refused_at_the_verb(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = self._bug(root)
            before = path.read_text()
            unmet = tr.requirements(root, "BG0001", "Fixed")
            self.assertTrue(any("acceptance criteria" in u for u in unmet), unmet)
            with self.assertRaises(Exception):
                tr.transition(root, "BG0001", "Fixed")
            self.assertEqual(path.read_text(), before,
                             "the artefact was mutated by a transition that is refused")

    def test_a_unit_with_criteria_still_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, criteria="- [x] the defect no longer reproduces")
            self.assertEqual(tr.requirements(root, "BG0001", "Fixed"), [])

    def test_a_decision_terminal_status_needs_no_criteria(self) -> None:
        """A unit ruled `Won't Fix` was never built, so it owes no contract. Without this the
        floor would demand a definition of done for work nobody did."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            self.assertEqual(
                [u for u in tr.requirements(root, "BG0001", "Won't Fix")
                 if "acceptance criteria" in u], [])

    def test_the_verb_and_the_validator_use_one_predicate(self) -> None:
        """Two copies of "what counts as a criterion" would diverge, and the looser one is the
        one that runs. Asserted as agreement rather than as two expected answers."""
        import validate
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for criteria in ("", "- [ ] it works", "### AC1: x\n\n- **Then** y"):
                path = self._bug(root, criteria=criteria)
                text = path.read_text()
                refused = any("acceptance criteria" in u
                              for u in tr.requirements(root, "BG0001", "Fixed"))
                self.assertEqual(refused, not validate._has_criteria(text),
                                 f"verb and validator disagree for {criteria!r}")


class AReopenRetractsTheGreenItOverturnsTests(unittest.TestCase):
    """BG0416. A reopen is a human overturning a machine verdict, and nothing in the machine
    heard it. BG0372 was reopened because its tests asserted a constant and a header the writer
    never emits - and those tests still passed, so the verify-report still recorded it green and
    the planner still priced it as BUILT-NOT-CLOSED at zero points. The reopen must reach the
    evidence, not only the status."""

    def _reopened(self, depth: str | None = "functional (tests red-first)"):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _bug_repo(root, depth)
        p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "> **Status:** In Progress", "> **Status:** Fixed"), encoding="utf-8")
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True, exist_ok=True)
        (local / "verify-report.json").write_text(json.dumps(
            {"stories": {"BG0001-x": {"verified": 3, "failed": 0, "stale": 0}}}), encoding="utf-8")
        return root, p, local / "verify-report.json"

    def test_reopening_retracts_the_verification_depth(self) -> None:
        root, p, _ = self._reopened()
        transition.transition(root, "BG0001", "Open")
        depth = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Verification depth") or ""
        self.assertTrue(depth.upper().startswith("RETRACTED"),
                        f"the withdrawn claim survived the reopen: {depth!r}")
        self.assertIn("functional", depth, "the retraction dropped what was being retracted")

    def test_the_invalidation_reaches_a_v3_id(self) -> None:
        """`split("-")[0]` on a v3 stem `US-01KYQ84R-v3-unit` yields `US`, so the entry never
        matched and the invalidation silently no-opped. `init` mints v3 ids by default, so EVERY
        new consuming project got the no-op while this repo's legacy-shaped fixture passed.
        Found by an independent reviewer; the sibling test picked the one stem shape that worked."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        report = local / "verify-report.json"
        report.write_text(json.dumps({"stories": {
            "US-01KYQ84R-v3-unit": {"verified": 3, "failed": 0, "stale": 0}}}), encoding="utf-8")
        transition._invalidate_verify_report(root, "US-01KYQ84R")
        entry = json.loads(report.read_text(encoding="utf-8"))["stories"]["US-01KYQ84R-v3-unit"]
        self.assertEqual(entry["verified"], 0, "a v3 unit's stale green survived the reopen")
        self.assertEqual(entry["stale"], 1)

    def test_reopening_invalidates_the_verify_report_entry(self) -> None:
        """The green a reviewer overturned must not stay readable as current."""
        root, _, report = self._reopened()
        transition.transition(root, "BG0001", "Open")
        entry = json.loads(report.read_text(encoding="utf-8"))["stories"].get("BG0001-x")
        self.assertFalse(entry and entry.get("verified", 0) > 0 and not entry.get("stale", 0),
                         "the verify-report still reports the reopened unit green")

    def test_the_planner_prices_a_reopened_unit_at_full_points(self) -> None:
        """The reader that was actually wrong. `_built_not_closed` must not call it built."""
        root, p, _ = self._reopened()
        transition.transition(root, "BG0001", "Open")
        self.assertFalse(
            sprint._built_not_closed(root, "BG0001", p.read_text(encoding="utf-8")),
            "a reopened unit is still excluded from the build forecast")

    def test_a_retracted_depth_alone_defeats_a_green_verify_report(self) -> None:
        """The two mechanisms must not be able to disagree: even with the report left green,
        a retracted depth is enough. Without this the fix rests on the invalidation alone."""
        root, p, report = self._reopened()
        transition.transition(root, "BG0001", "Open")
        report.write_text(json.dumps(
            {"stories": {"BG0001-x": {"verified": 3, "failed": 0, "stale": 0}}}), encoding="utf-8")
        self.assertFalse(
            sprint._built_not_closed(root, "BG0001", p.read_text(encoding="utf-8")),
            "a re-greened report outvoted the retraction")

    def test_a_unit_with_no_depth_claim_is_not_given_one(self) -> None:
        """A reopen retracts what was claimed; it never invents a claim that was never made."""
        root, p, _ = self._reopened(depth=None)
        transition.transition(root, "BG0001", "Open")
        self.assertIsNone(
            sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Verification depth"),
            "the reopen invented a verification-depth field")

    def test_moving_between_two_non_terminal_statuses_retracts_nothing(self) -> None:
        """The predicate is LEAVING a terminal status, not ARRIVING at a non-terminal one.
        Caught by mutation: the sibling negative control moved to Fixed, which is terminal, so
        a predicate reading only the target passed it. Reading only the target would wipe the
        evidence on every ordinary move through a working status."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _bug_repo(root, "functional (tests red-first)")   # starts at In Progress
        transition.transition(root, "BG0001", "Open")     # non-terminal -> non-terminal
        p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        depth = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Verification depth") or ""
        self.assertFalse(depth.upper().startswith("RETRACTED"),
                         "a move between two open statuses retracted a live claim")

    def test_an_ordinary_forward_transition_retracts_nothing(self) -> None:
        """In Progress -> Fixed is not a reopen. The guard must fire on leaving a terminal
        status, not on touching a unit that has a depth."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _bug_repo(root, "functional (tests red-first)")
        transition.transition(root, "BG0001", "Fixed")
        p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        depth = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Verification depth") or ""
        self.assertFalse(depth.upper().startswith("RETRACTED"),
                         "a forward transition retracted a live claim")


class OpenQuestionsGateTests(unittest.TestCase):
    """US0465, at the VERB. Defence at the validate layer alone is weaker than the rule reads:
    the transition performs the change and the refusal arrives later, from a different tool,
    phrased as a validation error - leaving the tree in the state the rule forbids."""

    def _repo(self, status, body):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            f"# US0001: x\n\n> **Status:** {status}\n\n"
            f"## Acceptance Criteria\n\n### AC1\n- **Verify:** manual - checked\n"
            f"  - **Verified:** yes (2026-07-29)\n\n{body}", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
            f"| {status} | 1 |\n| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n"
            f"| --- | --- | --- |\n| [US0001](US0001-x.md) | x | {status} |\n", encoding="utf-8")
        return root, sd / "US0001-x.md"

    def test_a_terminal_move_is_refused_while_a_question_is_unchecked(self) -> None:
        root, path = self._repo("Review", "## Open Questions\n\n- [ ] should we do X?\n")
        before = path.read_text(encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            transition.transition(root, "US0001", "Done")
        msg = str(ctx.exception)
        self.assertIn("Open Question", msg)
        # BOTH routes named, or the refusal costs a round-trip to discover what yes looks like.
        self.assertIn("Resolved Questions", msg, "the ruling route is not named")
        self.assertIn("follow-up", msg, "the follow-up-artefact route is not named")
        # ...and NOTHING was written.
        self.assertEqual(before, path.read_text(encoding="utf-8"),
                         "the artefact was modified by a refused transition")

    def test_a_ruling_or_a_resolvable_follow_up_id_is_accepted_and_a_dangling_id_is_not(self) -> None:
        # Route 1: a ruling recorded on the item.
        root, _ = self._repo("Review", "## Open Questions\n\n- [x] X, ruled by D0001\n")
        transition.transition(root, "US0001", "Done")

        # Route 2: a follow-up id that RESOLVES.
        root2, _ = self._repo("Review", "## Open Questions\n\n- [x] X, filed as BG0002\n")
        bugs = root2 / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / "BG0002-follow-up.md").write_text(
            "# BG0002: follow up\n\n> **Status:** Open\n", encoding="utf-8")
        transition.transition(root2, "US0001", "Done")

        # Refused: a tick citing an id nothing holds.
        root3, _ = self._repo("Review", "## Open Questions\n\n- [x] X, filed as BG9999\n")
        with self.assertRaises(ValueError) as ctx:
            transition.transition(root3, "US0001", "Done")
        self.assertIn("resolves to no artefact", str(ctx.exception))

    def test_a_ruling_VERB_does_not_buy_an_exemption_from_the_id_it_cites(self) -> None:
        """US0465 AC3, the fourth escape in the family. `_RULING_RE` matched before either
        destination check ran, so `resolved by BG9999` - a ruling naming an artefact nothing in
        the workspace holds - was ACCEPTED, while the identical citation without the verb was
        refused. Four words of prose bought an exemption from the one thing being checked.

        The unticked case matters as much as the ticked one: the verb branch sat above the
        `state == " "` check too, so an open box wearing a ruling verb was accepted as well.
        """
        for body in ("- [x] deferred, resolved by BG9999\n",
                     "- [ ] settled in BG9999\n",
                     "- [x] ruled: see CR9999\n"):
            with self.subTest(item=body.strip()):
                root, path = self._repo("Review", f"## Open Questions\n\n{body}")
                before = path.read_text(encoding="utf-8")
                with self.assertRaises(ValueError) as ctx:
                    transition.transition(root, "US0001", "Done")
                self.assertIn("resolves to no artefact", str(ctx.exception))
                self.assertEqual(before, path.read_text(encoding="utf-8"),
                                 "a refused transition still wrote to the artefact")

    def test_a_ruling_citing_a_decision_row_the_table_does_not_hold_is_refused(self) -> None:
        """The same hole on the decision route. `_decision_cited` already tested for a row that
        EXISTS, but `_RULING_RE` matched first for the natural phrasing, so its existence check
        was unreachable for `ruled by D9999` - dead code standing beside the defect it was
        written to prevent."""
        root, _ = self._repo("Review", "## Open Questions\n\n- [x] X, ruled by D9999\n")
        (root / "sdlc-studio" / "decisions.md").write_text(
            "# Decisions\n\n| ID | Decision | Status |\n| --- | --- | --- |\n"
            "| D0001 | something else | accepted |\n", encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            transition.transition(root, "US0001", "Done")
        self.assertIn("decisions table does not hold", str(ctx.exception))

    def test_a_project_keeping_NO_decisions_table_is_not_held_to_one(self) -> None:
        """An absent table is not a failed lookup. Refusing a cited decision row because the
        project never kept a decisions file is a guard manufacturing work, and it is a different
        fact from a table that exists and does not hold the id.

        The item deliberately carries NO ruling verb. Written as `ruled by D0001` this test
        passes whether the carve-out is present or not - `_RULING_RE` matches first and settles
        the item, masking the branch entirely - and a mutation run caught it doing exactly that.
        A bare citation is the only shape that reaches `_decision_cited`'s absent-table answer.
        """
        root, _ = self._repo("Review", "## Open Questions\n\n- [x] X, see D0001\n")
        self.assertFalse((root / "sdlc-studio" / "decisions.md").exists())
        transition.transition(root, "US0001", "Done")

    def test_a_valid_decision_row_settles_the_item_even_beside_its_own_id(self) -> None:
        """A ruling that names a real decision row has named its destination. An artefact citing
        its own id ALONGSIDE that row - "RULED MOOT: CR0019 is Superseded, see D0011" - is
        describing what was ruled, not offering itself as its own follow-up. Ordering the
        self-citation check first reported three such items across the live corpus."""
        root, _ = self._repo(
            "Review", "## Open Questions\n\n- [x] RULED MOOT: US0001 is Superseded; see D0011\n")
        (root / "sdlc-studio" / "decisions.md").write_text(
            "# Decisions\n\n| ID | Decision | Status |\n| --- | --- | --- |\n"
            "| D0011 | the ruling | accepted |\n", encoding="utf-8")
        transition.transition(root, "US0001", "Done")

    def test_a_non_terminal_move_is_unaffected(self) -> None:
        """The bar is the TERMINAL status. A question is legitimate while work is in flight,
        and refusing it there would make the gate unusable."""
        root, _ = self._repo("Ready", "## Open Questions\n\n- [ ] should we do X?\n")
        transition.transition(root, "US0001", "In Progress")

    def test_force_still_overrides_and_the_refusal_says_so(self) -> None:
        root, _ = self._repo("Review", "## Open Questions\n\n- [ ] should we do X?\n")
        with self.assertRaises(ValueError) as ctx:
            transition.transition(root, "US0001", "Done")
        self.assertIn("--force", str(ctx.exception))
        transition.transition(root, "US0001", "Done", force=True)


class TerminalOracleTests(unittest.TestCase):
    """A bug reaching `Fixed` is held to an oracle, the way a story is at `Done`.

    Having criteria is not the same as anything speaking for them. Eight terminal bugs carried
    31 unticked boxes and zero `Verify:` lines and passed every check - a status the artefact's
    own body contradicts.
    """

    def _bug(self, root, body):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0001-x.md").write_text(body, encoding="utf-8")
        return root

    HEAD = ("# BG0001: a defect\n\n> **Status:** Open\n> **Points:** 3\n"
            "> **Severity:** High\n> **Affects:** src/a.py\n"
            "> **Verification depth:** functional (checked)\n\n"
            "## Summary\n\ns\n\n## Acceptance Criteria\n\n")

    def test_an_unticked_unverified_bug_cannot_reach_fixed(self) -> None:
        """MUTANT: delete the ticked/executable check.

        This is the shape that shipped: criteria present, none ticked, no Verify line.
        """
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), self.HEAD + "- [ ] the defect is corrected\n")
            blocks = mod.requirements(root, "BG0001", "Fixed")
        self.assertTrue(any("nothing speaks for this fix" in b for b in blocks),
                        f"an unticked, unverified bug reached Fixed: {blocks}")

    def test_a_tick_outside_the_criteria_does_not_satisfy_it(self) -> None:
        """MUTANT: search the whole artefact, as shipped.

        The gate's own refusal says "every acceptance criterion is unticked", but it searched
        the WHOLE document - so `- [x] I reproduced it on my machine` in Steps to Reproduce
        answered a question about the criteria. Reproduced through the CLI before this was
        written: the bug reached Fixed.
        """
        mod = tr
        body = ("# BG0001: a defect\n\n> **Status:** Open\n> **Points:** 3\n"
                "> **Severity:** High\n> **Affects:** src/a.py\n"
                "> **Verification depth:** functional (checked)\n\n"
                "## Summary\n\ns\n\n"
                "## Steps to Reproduce\n\n- [x] I reproduced it on my machine\n\n"
                "## Acceptance Criteria\n\n- [ ] the defect is corrected\n")
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), body)
            blocks = mod.requirements(root, "BG0001", "Fixed")
        self.assertTrue(any("nothing speaks for this fix" in b for b in blocks),
                        f"a ticked box OUTSIDE the criteria satisfied the oracle: {blocks}")

    def test_a_verify_line_outside_the_criteria_does_not_satisfy_it(self) -> None:
        """MUTANT: search the whole artefact, as shipped.

        The second half of the same hole, and the worse one: the `Verify:` line named a test
        file that does not exist, so nothing could have run it. It still cleared the gate.
        """
        mod = tr
        body = ("# BG0001: a defect\n\n> **Status:** Open\n> **Points:** 3\n"
                "> **Severity:** High\n> **Affects:** src/a.py\n"
                "> **Verification depth:** functional (checked)\n\n"
                "## Summary\n\ns\n\n"
                "## Proposed Fix\n\n- **Verify:** pytest tests/test_nothing.py::nope\n\n"
                "## Acceptance Criteria\n\n- [ ] the defect is corrected\n")
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), body)
            blocks = mod.requirements(root, "BG0001", "Fixed")
        self.assertTrue(any("nothing speaks for this fix" in b for b in blocks),
                        f"a `Verify:` line OUTSIDE the criteria satisfied the oracle: {blocks}")

    def test_a_ticked_criterion_satisfies_it(self) -> None:
        """The human oracle. MUTANT: require a Verify line as well.

        Demanding both would refuse the ordinary judgement call a bug fix often is.
        """
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), self.HEAD + "- [x] the defect is corrected\n")
            blocks = mod.requirements(root, "BG0001", "Fixed")
        self.assertFalse(any("nothing speaks for this fix" in b for b in blocks),
                         f"a ticked criterion did not satisfy the gate: {blocks}")

    def test_an_executable_criterion_satisfies_it(self) -> None:
        """The machine oracle. MUTANT: accept only a tick."""
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), self.HEAD +
                             "### AC1: it behaves\n\n- **Then** it behaves\n"
                             "- **Verify:** pytest tests/test_a.py::T::test_x\n")
            blocks = mod.requirements(root, "BG0001", "Fixed")
        self.assertFalse(any("nothing speaks for this fix" in b for b in blocks),
                         f"an executable criterion did not satisfy the gate: {blocks}")


if __name__ == "__main__":
    unittest.main()
