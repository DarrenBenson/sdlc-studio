"""One resolvable-Affects predicate, reached by every writer (EP0110 / CR0400).

`file_finding.file` already refused a declared `Affects` that resolves to nothing; `artifact new`
and `refine apply` did not, so five of 23 stories minted through one decomposition run carried a
wrong path. These tests pin the shared predicate and its reach:

- US0323: the three writers and the grooming gate return ONE verdict on a declared `Affects`,
  reached at a single seam, so a writer added without the check is caught.
- US0325: the refusal names the closest unique basename match where one exists, lists an ambiguous
  set without choosing, and offers nothing when the basename matches no file.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k affects_resolvable
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sibling helpers (loader)

import loader  # noqa: E402 - the canonical way to import a script under test

# Load file_finding FIRST so `sys.modules['file_finding']` is this object before artifact/refine/
# sprint import it - the patch in AC2 must be seen through every writer (loader L-0057).
ff = loader.load_script("file_finding")
artifact = loader.load_script("artifact")
refine = loader.load_script("refine")
sprint = loader.load_script("sprint")

#: The refusal signature the resolvable-Affects predicate raises with - distinct from the grooming
#: gate's "Affects missing" refusal, so a probe can attribute a refusal to THIS check specifically.
_AFFECTS_REFUSAL = "Affects resolves to nothing"


def _proj(root: Path) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)


def _real(root: Path, rel: str = "src/real.py") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("", encoding="utf-8")


def _cr(root: Path, cid: str = "CR0001") -> str:
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{cid}-x.md").write_text(
        f"# CR-{cid[2:]}: t\n\n> **Status:** Approved\n> **Priority:** P1\n"
        f"> **Type:** Improvement\n> **Size:** L\n\n## Summary\n\ns\n\n## Impact\n\ni\n",
        encoding="utf-8")
    return cid


def _bug_fields(affects: str) -> dict:
    """A bug otherwise fully groomed, so the ONLY thing under test is its declared `Affects`."""
    return {"severity": "High", "summary": "s", "steps": "x", "fix": "y",
            "points": 3, "affects": affects}


def _refuses_for_affects(fn) -> bool:
    """True iff `fn` refuses SPECIFICALLY because the declared `Affects` resolves to nothing.

    A refusal for another reason (a bug missing its `Affects` altogether) is NOT this check, so it
    reads as an accept from the predicate's view - which is what lets a bug-writer and a
    story-writer agree on the prose shape that declares no path at all."""
    try:
        fn()
        return False
    except ValueError as exc:
        return _AFFECTS_REFUSAL in str(exc)


# The four shapes AC1 names: every path resolves, some resolve, none resolves, and prose the
# parser cannot read as a path at all. Only the third is the resolvable-Affects refusal.
_EVERY = "src/real.py"
_SOME = "src/real.py, src/not-yet.py"
# BG0558: the rule catches a TYPO, not an unresolvable path. `_TYPO` names a wrong directory
# for a file that really exists - the measured hazard BG0144 records - and must refuse.
# `_CREATES` names a basename that exists nowhere, which is every path a greenfield story
# declares, and must NOT: refusing it refused the first sprint plan of every new project.
# The old `_NONE = "nowhere/ghost.py"` sat under the refusing expectation and was the creation
# case wearing a typo's label, so it moves rather than being deleted.
_TYPO = "elsewhere/real.py"
_CREATES = "nowhere/ghost.py"
_PROSE = "everything"
_SHAPES = ((_EVERY, False), (_SOME, False), (_TYPO, True), (_CREATES, False), (_PROSE, False))


class SharedPredicateTests(unittest.TestCase):
    """US0323: one predicate, reached by every writer, agreeing with the grooming gate."""

    def _probe(self, writer: str, affects: str) -> bool:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            _real(root)
            if writer == "file_finding":
                return _refuses_for_affects(
                    lambda: ff.file_finding(root, "bug", "t", _bug_fields(affects)))
            if writer == "artifact":
                return _refuses_for_affects(
                    lambda: artifact.new(root, "bug", "t", _bug_fields(affects)))
            if writer == "refine":
                cid = _cr(root)
                return _refuses_for_affects(
                    lambda: refine.refine(root, cid, "E", [("S", 3, affects)],
                                          skip_personas=True))
            raise AssertionError(writer)

    def test_all_three_writers_agree_on_every_affects_shape(self) -> None:
        for affects, expect_refuse in _SHAPES:
            verdicts = {w: self._probe(w, affects)
                        for w in ("file_finding", "artifact", "refine")}
            self.assertEqual(set(verdicts.values()), {expect_refuse},
                             f"writers disagree on {affects!r}: {verdicts}")

    def test_every_writer_routes_through_the_one_predicate(self) -> None:
        # Replace the shared seam with one that calls EVERY declared path unresolvable. A resolvable
        # `Affects` ('src/real.py') must then be refused by each entry point - one that resolved
        # paths by its own means, or did not check, would slip through and fail here.
        #
        # The suite's other modules load `file_finding` through their own importlib incantations, so
        # a writer may hold a different `file_finding` object than `ff`. Patch the seam on EVERY
        # object a writer references, so the single-seam guarantee is tested regardless of which
        # copy each writer imported (in production there is exactly one module).
        import contextlib
        patched = lambda root, declared: list(declared)  # noqa: E731 - refuse everything
        targets = {id(m): m for m in (
            ff, getattr(artifact, "file_finding", None), getattr(refine, "file_finding", None),
            sys.modules.get("file_finding")) if m is not None}
        with contextlib.ExitStack() as stack:
            for m in targets.values():
                stack.enter_context(mock.patch.object(m, "unresolvable_affects", patched))
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                _real(root)
                with self.assertRaises(ValueError):
                    ff.file_finding(root, "bug", "t", _bug_fields(_EVERY))
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                _real(root)
                with self.assertRaises(ValueError):
                    artifact.new(root, "bug", "t", _bug_fields(_EVERY))
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                _real(root)
                with self.assertRaises(ValueError):
                    artifact.new_batch(root, "bug",
                                       [{"title": "t", **_bug_fields(_EVERY)}])
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                _real(root)
                cid = _cr(root)
                with self.assertRaises(ValueError):
                    refine.refine(root, cid, "E", [("S", 3, _EVERY)], skip_personas=True)

    def _unit(self, root: Path, affects: str) -> dict:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0001-x.md").write_text(
            f"# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Affects:** {affects}\n> **Points:** 2\n", encoding="utf-8")
        return {"id": "BG0001", "type": "bug", "path": str(d / "BG0001-x.md")}

    def _gate_refuses_for_resolvable(self, root: Path, affects: str) -> bool:
        declared = ff.declared_affects(affects)
        bd = sprint.breakdown(root, [self._unit(root, affects)], skip_personas=True)
        entry = next((u for u in bd["ungroomed"] if u["id"] == "BG0001"), None)
        if entry is None:
            return False
        # Read the gate's OWN verdict, never re-derive it. The previous form inferred "refused
        # for resolvability" from "is ungroomed AND every path is unresolvable", so a unit
        # ungroomed for a DIFFERENT reason - these fixtures carry no acceptance criteria - was
        # counted as a resolvability refusal, and the invariant reported a disagreement that was
        # the helper's own (BG0558). `typos` is what the gate decided on.
        return bool(declared) and bool(entry.get("typos"))

    def _predicate_refuses(self, root: Path, affects: str) -> bool:
        try:
            ff.check_affects_resolvable(root, affects)
            return False
        except ValueError:
            return True

    def test_the_predicate_and_the_grooming_gate_never_disagree(self) -> None:
        # Including the partly-resolvable case the gate deliberately allows: a unit accepted at
        # mint is never refused at plan time for the field it was just checked on.
        for affects, _ in _SHAPES:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                _real(root)
                self.assertEqual(self._predicate_refuses(root, affects),
                                 self._gate_refuses_for_resolvable(root, affects),
                                 f"predicate and grooming gate disagree on {affects!r}")


class ClosestMatchTests(unittest.TestCase):
    """US0325: the refusal names the closest unique basename match where one exists."""

    def _refuse_msg(self, root: Path, affects: str) -> str:
        with self.assertRaises(ValueError) as cm:
            artifact.new(root, "bug", "t", _bug_fields(affects))
        return str(cm.exception)

    def test_the_refusal_names_a_unique_basename_match(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            (root / "real").mkdir()
            (root / "real" / "widget.py").write_text("", encoding="utf-8")
            msg = self._refuse_msg(root, "wrongdir/widget.py")
            self.assertIn("wrongdir/widget.py", msg)          # the value rejected
            self.assertIn("real/widget.py", msg)              # the one real path, named

    def test_an_ambiguous_basename_lists_candidates_without_choosing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            for sub in ("a", "b"):
                (root / sub).mkdir()
                (root / sub / "dup.py").write_text("", encoding="utf-8")
            msg = self._refuse_msg(root, "typo/dup.py")
            self.assertIn("a/dup.py", msg)
            self.assertIn("b/dup.py", msg)
            self.assertIn("cannot choose", msg)               # names none as THE answer

    def test_no_basename_match_offers_no_suggestion(self) -> None:
        # BG0558: a lone no-match path is a file the unit CREATES and no longer refuses at all,
        # so the refusal is raised by a typo BESIDE it. The no-match path is still named and
        # still says so plainly - the author is never sent to a file the tool invented.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            _real(root)
            msg = self._refuse_msg(root, "elsewhere/real.py, typo/nowhere-at-all.py")
            self.assertIn("typo/nowhere-at-all.py", msg)      # still named
            self.assertIn("no file named nowhere-at-all.py", msg)

    def test_a_path_matching_nothing_is_a_creation_and_never_refuses(self) -> None:
        # The positive control for the test above: on its own, that same path is accepted.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            _real(root)
            ff.check_affects_resolvable(root, "typo/nowhere-at-all.py")

    def test_all_three_refusals_carry_the_same_suggestion(self) -> None:
        # The suggestion is built where the predicate lives, so every writer's refusal carries it.
        def _msgs(affects: str) -> list[str]:
            out = []
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                (root / "real").mkdir()
                (root / "real" / "gate.py").write_text("", encoding="utf-8")
                with self.assertRaises(ValueError) as c1:
                    ff.file_finding(root, "bug", "t", _bug_fields(affects))
                out.append(str(c1.exception))
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                (root / "real").mkdir()
                (root / "real" / "gate.py").write_text("", encoding="utf-8")
                with self.assertRaises(ValueError) as c2:
                    artifact.new(root, "bug", "t", _bug_fields(affects))
                out.append(str(c2.exception))
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _proj(root)
                (root / "real").mkdir()
                (root / "real" / "gate.py").write_text("", encoding="utf-8")
                cid = _cr(root)
                with self.assertRaises(ValueError) as c3:
                    refine.refine(root, cid, "E", [("S", 3, affects)], skip_personas=True)
                out.append(str(c3.exception))
            return out

        for msg in _msgs("wrongdir/gate.py"):
            self.assertIn("real/gate.py", msg)




class GreenfieldPlansTests(unittest.TestCase):
    """BG0558: a project that has just been created can plan its first sprint.

    Every criterion here drives the SHIPPED COMMAND as a subprocess. The defect lives in which
    tree the predicate is pointed at and in what the CLI does with its verdict, and an in-process
    call to `breakdown` or `check_affects_resolvable` sees neither - the plan review rejected the
    first version of this plan for exactly that (LL0040, and BG0556's shape).
    """

    def _run(self, root: Path, *args: str):
        import subprocess  # noqa: PLC0415 - local: only these tests spawn the CLI
        return subprocess.run(
            [sys.executable, str(_SCRIPTS / args[0]), "--root", str(root), *args[1:]],
            capture_output=True, text=True, timeout=300, check=False)

    def _project(self, root: Path) -> None:
        # No `git init`: the initialiser does not need one, and the unconfined-raw-git ratchet is
        # at zero. A fixture is not a reason to raise it.
        r = self._run(root, "init.py", "run")
        self.assertEqual(0, r.returncode, r.stderr)

    def _story(self, root: Path, sid: str, affects: str) -> Path:
        p = root / "sdlc-studio" / "stories" / f"{sid}-x.md"
        p.write_text(
            f"# {sid}: a visitor can sign up\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
            f"> **Priority:** High\n> **Affects:** {affects}\n> **Points:** 3\n\n"
            f"## Acceptance Criteria\n\n### AC1: an account is created\n\n"
            f"- **Given** a valid email\n- **When** the form is submitted\n"
            f"- **Then** an account exists\n- **Verify:** shell true\n", encoding="utf-8")
        return p

    def _worklist(self, root: Path, *ids: str) -> Path:
        p = root / "wl.txt"
        p.write_text("\n".join(ids) + "\n", encoding="utf-8")
        return p

    def test_greenfield_creation_plans(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root)
            # The lane must be ENFORCING, or the mutant survives on a fixture that opted out.
            # Asserted before anything else, from the shipped config the initialiser wrote.
            self.assertEqual("enforce", sprint.breakdown_mode(root))
            self.assertFalse((root / "sdlc-studio" / "definition-of-ready.md").read_text()
                             .strip() == "", "a blank DoR would downgrade grooming.affects")
            self._story(root, "US0001", "src/auth/signup.py, tests/test_signup.py")
            r = self._run(root, "sprint.py", "plan", "--worklist",
                          str(self._worklist(root, "US0001")), "--write",
                          "--sprint-goal", "a visitor can sign up")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertTrue((root / "sdlc-studio" / ".local" / "run-state.json").exists(),
                            "no run was written: " + r.stdout + r.stderr)
            self.assertIn("US0001", (root / "sdlc-studio" / ".local"
                                     / "run-state.json").read_text())

    def test_typo_and_creation_differ_in_one_tree(self) -> None:
        # ONE tree, two units, opposite verdicts - so no repair keyed on "is this project empty"
        # can satisfy this. The plan review named that as a blocking gap in the first version.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root)
            _real(root, "src/auth/signup.py")
            self._story(root, "US0001", "src/authh/signup.py")          # typo: basename exists
            self._story(root, "US0002", "src/billing/invoice.py")       # creation: nowhere
            typo = self._run(root, "sprint.py", "plan", "--worklist",
                             str(self._worklist(root, "US0001")), "--write",
                             "--sprint-goal", "g")
            self.assertNotEqual(0, typo.returncode, "a typo must still refuse")
            self.assertFalse((root / "sdlc-studio" / ".local" / "run-state.json").exists(),
                             "a refused plan must write no run")
            made = self._run(root, "sprint.py", "plan", "--worklist",
                             str(self._worklist(root, "US0002")), "--write",
                             "--sprint-goal", "g")
            self.assertEqual(0, made.returncode, made.stdout + made.stderr)

    def test_refusal_names_the_typo_not_a_missing_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._project(root)
            _real(root, "src/auth/signup.py")
            self._story(root, "US0001", "src/authh/signup.py")
            r = self._run(root, "sprint.py", "breakdown", "--worklist",
                          str(self._worklist(root, "US0001")))
            out = r.stdout + r.stderr
            self.assertIn("src/authh/signup.py", out)          # names the path
            # Names the MATCH that makes it a typo, not merely that the path is absent. Mutation
            # found the first version of this assertion vacuous: shortening the message to the
            # bare word `Affects` left the path in the output and every assertion green.
            self.assertIn("src/auth/signup.py", out)
            self.assertIn("found at", out)
            self.assertNotIn("lacks: Affects", out,
                             "a unit that DECLARES an Affects was told it lacks one")

    def test_one_predicate_decides_for_every_writer(self) -> None:
        # Replacing the shared predicate must move the writer check AND the grooming gate. A
        # faithful copy would be an invalid mutant, so the mutant this pins is a DIVERGENT one.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            _real(root)
            # Resolve the module the way PRODUCTION does. `sprint` does a function-local
            # `import file_finding`, which reads `sys.modules` at call time; patching the
            # test's own reference passed in isolation and failed in the full suite, where
            # another module had bound a different object under that name. An order-dependent
            # green is worse than a red, and it would have made this criterion untrustworthy
            # in exactly the run that matters.
            shared = sys.modules["file_finding"]
            # Positive control FIRST: un-mocked, both the writer and the gate refuse. Without it
            # a repair that never refuses anything satisfies the mocked half for the wrong reason.
            with self.assertRaises(ValueError):
                shared.check_affects_resolvable(root, _TYPO)
            armed = sprint.breakdown(root, [self._unit_for(root, _TYPO)], skip_personas=True)
            self.assertTrue([u for u in armed["ungroomed"] if u.get("typos")])
            with mock.patch.object(shared, "fictional_affects", return_value=[]):
                shared.check_affects_resolvable(root, _TYPO)   # writer: no longer refuses
                bd = sprint.breakdown(root, [self._unit_for(root, _TYPO)], skip_personas=True)
                self.assertEqual([], [u for u in bd["ungroomed"] if u.get("typos")],
                                 "the grooming gate did not follow the shared predicate")

    def _unit_for(self, root: Path, affects: str) -> dict:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "BG0001-x.md").write_text(
            f"# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
            f"> **Affects:** {affects}\n> **Points:** 2\n\n"
            f"## Acceptance Criteria\n\n### AC1: it behaves\n\n"
            f"- **Given** x\n- **Verify:** shell true\n", encoding="utf-8")
        return {"id": "BG0001", "type": "bug", "path": str(d / "BG0001-x.md")}

    def test_refine_apply_mints_a_creating_story(self) -> None:
        # The second call site. This is the one that refused CR0542's own rehearsal stories, so
        # AC1 alone does not satisfy it: `refine apply` bottoms out on the writer check, not on
        # the grooming gate.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            _real(root)
            cid = _cr(root)
            refine.refine(root, cid, "E", [("S", 3, "tools/not-yet-written.sh")],
                          skip_personas=True)


if __name__ == "__main__":
    unittest.main()
