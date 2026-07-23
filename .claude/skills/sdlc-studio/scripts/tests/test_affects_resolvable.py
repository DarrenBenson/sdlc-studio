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
_NONE = "nowhere/ghost.py"
_PROSE = "everything"
_SHAPES = ((_EVERY, False), (_SOME, False), (_NONE, True), (_PROSE, False))


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
        unres = entry.get("unresolvable") or []
        return bool(declared) and len(unres) == len(declared)

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
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _proj(root)
            msg = self._refuse_msg(root, "typo/nowhere-at-all.py")
            self.assertIn("typo/nowhere-at-all.py", msg)      # still named
            self.assertIn("no file named nowhere-at-all.py", msg)

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


if __name__ == "__main__":
    unittest.main()
