"""US0916: a story reaches Done on green criteria and one independent APPROVE.

The per-unit two-role bar - an adversarial-pass evidence row and a reviewer-of-record sign-off
row per unit past `review.two_role_after` - is gone. The review bar that survives is the
independent delivery APPROVE, still judged by `conformance.py check` (the `critiqued` stage)
and at `sprint sign`. The verb that writes Done never refused a missing verdict, so nothing new
refuses here.

Every fixture that must fail at the pre-deletion code sets `review.two_role_after: 1`, which is
the one configuration where the deleted gate acted. Each workspace is a temporary directory; the
last test reads this repository's own artefacts, because its criterion names them.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/conformance.py
from __future__ import annotations

import ast
import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(SCRIPTS))
import conformance  # noqa: E402
import critic  # noqa: E402
import sprint  # noqa: E402
import transition  # noqa: E402
import validate  # noqa: E402
from lib import sdlc_md  # noqa: E402

SID = "US0002"
#: The two per-unit halves the deletion retires, spelled as the old lane printed them.
RETIRED_HALVES = ("adversarial-pass evidence", "reviewer-of-record sign-off")

#: The deleted classes AC5 names. The full deleted set is DERIVED (`_deleted_nodes`); these only
#: prove the derivation is looking at the right base, since each must appear in it.
AC5_NAMED = {"test_conformance.py": ("TwoRoleCutoffOnUlidIdsTests", "CritiquedHalvesTests",
                                     "TwoRoleCritiquedTests"),
             "test_transition.py": ("TheVerbEnforcesTheBarItWritesTests",)}

#: The selector US0298 AC1 was stamped on until this story retired it: a `-k` selector naming a
#: method this story deleted, which a hand-listed class check let through.
US0298_AC1 = ("pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k "
              "test_plan_names_the_reachable_end_state_under_the_two_role_gate")

_K_OPERATORS = {"and", "or", "not"}


def _project(root: Path, status: str = "Review") -> Path:
    """A project that sets the old cutoff, holding one story past it with green criteria."""
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("review:\n  two_role_after: 1\n",
                                                        encoding="utf-8")
    path = sd / f"{SID}-x.md"
    path.write_text(
        f"# {SID}: x\n\n> **Status:** {status}\n> **Epic:** EP0001\n\n"
        "## Acceptance Criteria\n\n### AC1: it behaves\n- **Given** the unit\n"
        "- **Verify:** manual a human looked\n- **Verified:** yes (2026-09-25)\n",
        encoding="utf-8")
    (sd / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        f"| {status} | 1 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [{SID}]({SID}-x.md) | x | {status} |\n", encoding="utf-8")
    return path


def _approve(root: Path) -> None:
    critic.record_verdict(root, SID, "APPROVE", reviewer="reviewer-a", author="builder",
                          issues="probed the edges")


def _run(fn, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = fn(argv)
    return rc, buf.getvalue()


def _check(root: Path) -> tuple[dict, str]:
    """The unit as `conformance.py check` judges it, and the lane's printed report."""
    _rc, out = _run(conformance.main, ["check", "--root", str(root)])
    unit = {u["id"]: u for u in conformance.detect_conformance(root)["units"]}[SID]
    return unit, out


def _string_reads(path: Path) -> list[str]:
    """Every string constant in a module that is not a docstring - the values code can read."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and n.body and isinstance(n.body[0], ast.Expr)
            and isinstance(n.body[0].value, ast.Constant)}
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]


def _git(*args: str) -> str | None:
    """`git <args>` in this repository: its stdout, or None when git cannot answer."""
    try:
        proc = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                              check=False, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _base_ref() -> str | None:
    """The tree this story's deletions are judged against: the parent of the commit that added
    this module, or HEAD while the module is uncommitted. None when history cannot say (no git,
    or a shallow clone without that parent)."""
    try:
        rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    added = _git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


def _test_nodes(source: str) -> set[tuple[str, str]]:
    """Every class, as (class, ""), and every `test_` function, as (class or "", name)."""
    out: set[tuple[str, str]] = set()
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef):
            out.add((node.name, ""))
            out.update((node.name, f.name) for f in node.body
                       if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and f.name.startswith("test_"))
        elif (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
              and node.name.startswith("test_")):
            out.add(("", node.name))
    return out


def _deleted_nodes(base: str) -> dict[str, dict[str, set]]:
    """Per test module the working tree changed since `base`: the nodes it defined there and no
    longer defines (`gone`), and the nodes it defines now (`now`). Derived, never listed."""
    rel = (SCRIPTS / "tests").relative_to(REPO).as_posix()
    out: dict[str, dict[str, set]] = {}
    for name in (_git("diff", "--name-only", base, "--", rel) or "").split():
        if not (Path(name).name.startswith("test_") and name.endswith(".py")):
            continue
        old = _git("show", f"{base}:{name}")
        if old is None:
            continue                    # added since the base: nothing of it was deleted
        path = REPO / name
        now = _test_nodes(path.read_text(encoding="utf-8")) if path.exists() else set()
        gone = _test_nodes(old) - now
        if gone:
            out[Path(name).name] = {"gone": gone, "now": now}
    return out


def _k_keywords(expr: str) -> list[str]:
    """The keywords a `-k` expression selects on, less its operators and any negated word."""
    words, out = re.findall(r"\w+", expr), []
    for i, word in enumerate(words):
        if word.lower() in _K_OPERATORS or (i and words[i - 1].lower() == "not"):
            continue
        out.append(word.lower())
    return out


def _selects_only_deleted(verify: str, deleted: dict[str, dict[str, set]]) -> bool:
    """Does a `Verify:` value select a deleted node of a changed module, and nothing there that
    survives? A node id (`module.py::Class[::test]`) selects that node. `-k EXPR` selects each
    node whose `Class::test` name holds one of its keywords, case-insensitively, as pytest
    matches; reading `and` as `or` over-selects, so a compound `-k` can only be under-reported."""
    hits = list(re.finditer(r"(test_\w+\.py)((?:::\w+)*)", verify))
    for i, m in enumerate(hits):
        mod = deleted.get(m.group(1))
        if not mod:
            continue
        parts = [p for p in m.group(2).split("::") if p]
        if parts:
            keys = ({(parts[0], parts[1])} if len(parts) > 1
                    else {(parts[0], ""), ("", parts[0])})
            if keys & mod["gone"] and not keys & mod["now"]:
                return True
            continue
        tail = verify[m.end():hits[i + 1].start() if i + 1 < len(hits) else len(verify)]
        km = re.search(r"\s-k\s+(?:\"([^\"]*)\"|'([^']*)'|(\S+))", tail)
        if not km:
            continue
        kws = _k_keywords(next(g for g in km.groups() if g is not None))

        def picked(nodes: set) -> bool:
            return any(k in f"{c}::{f}".lower() for c, f in nodes for k in kws)
        if kws and picked(mod["gone"]) and not picked(mod["now"]):
            return True
    return False


def _live_stamps(sources, deleted: dict[str, dict[str, set]]) -> list[str]:
    """`label:line` for each `Verified: yes` criterion whose selector reaches only deleted nodes.
    `sources` yields (label, lines)."""
    live: list[str] = []
    for label, lines in sources:
        for i, line in enumerate(lines):
            vm = sdlc_md.VERIFY_RE.match(line)
            if not vm or not _selects_only_deleted(vm.group(2), deleted):
                continue
            for nxt in lines[i + 1:i + 4]:
                if sdlc_md.VERIFY_RE.match(nxt):
                    break
                m = sdlc_md.VERIFIED_RE.match(nxt)
                if m and m.group(2).lower() == "yes":
                    live.append(f"{label}:{i + 1}")
    return live


class TwoRoleGoneTests(unittest.TestCase):
    def test_done_needs_no_signoff(self) -> None:
        """AC1. MUTANT: restore `transition._two_role_gate` and its call at the Done write, so
        the story is refused for the missing evidence and sign-off rows."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _project(root)
            _approve(root)
            rc, out = _run(transition.main, ["set", SID, "Done", "--root", str(root)])
            self.assertEqual(rc, 0, out)
            self.assertIn("> **Status:** Done", path.read_text(encoding="utf-8"))
            self.assertFalse(critic.signoff_path(root).exists(), "a sign-off row was written")
            for half in RETIRED_HALVES:
                self.assertNotIn(half, out)

    def test_conformance_names_no_two_role_half(self) -> None:
        """AC2. MUTANTS: keep the two-role halves in `conformance._done_stages` (the Done story
        reads critiqued unmet, naming both), and delete the APPROVE bar with them (the control
        story with no verdict reads critiqued met)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, status="Done")
            _approve(root)
            unit, out = _check(root)
            self.assertTrue(unit["stages"]["critiqued"], out)
            self.assertNotIn("critiqued", unit["missing"])
            for half in RETIRED_HALVES:
                self.assertNotIn(half, out)
                self.assertNotIn(half, unit["critiqued_missing"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, status="Done")        # the control: no delivery verdict at all
            unit, out = _check(root)
            self.assertFalse(unit["stages"]["critiqued"])
            self.assertIn("critiqued", unit["missing"])
            self.assertEqual(unit["critiqued_missing"], [conformance.HALF_VERDICT])
            line = next(ln for ln in out.splitlines() if SID in ln)
            self.assertIn("independent APPROVE", line)

    def test_the_plan_reaches_done(self) -> None:
        """AC3. MUTANT: restore the cutoff cap in `sprint.reachable_end_state`, so a batch of
        stories past `two_role_after: 1` is reported as reaching Review."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, status="Ready")
            (root / "sdlc-studio" / "stories" / f"{SID}-x.md").write_text(
                (root / "sdlc-studio" / "stories" / f"{SID}-x.md").read_text(encoding="utf-8")
                .replace("> **Epic:** EP0001\n",
                         "> **Epic:** EP0001\n> **Priority:** High\n> **Points:** 2\n"
                         "> **Affects:** src/x.py\n"), encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "x.py").write_text("x = 1\n", encoding="utf-8")
            data = sprint.build_plan(root, "story", "Ready", skip_personas=True)
            self.assertEqual([it["id"] for it in data["batch"]], [SID])
            end = data["reachable_end_state"]
            self.assertEqual(end["state"], "Done", end)
            self.assertIsNone(end.get("reason"), end)
            rc, out = _run(sprint.main, ["plan", "--stories", "Ready", "--root", str(root),
                                         "--no-fetch", "--skip-personas"])
            self.assertEqual(rc, 0, out)
            self.assertNotIn("reachable end state: Review", out)

    def test_the_two_role_key_and_tag_are_retired(self) -> None:
        """AC4. MUTANTS: delete `review.two-role` from `DOR_DOD_CHECK_IDS` alone (validate then
        refuses the tag as unknown), and name the retired id in `validate.py` rather than read
        it from the `sdlc_md` registry (a newly retired id is then refused)."""
        import yaml
        defaults = SCRIPTS.parent / "templates" / "config-defaults.yaml"
        review = (yaml.safe_load(defaults.read_text(encoding="utf-8")) or {}).get("review") or {}
        self.assertNotIn("two_role_after", review)
        self.assertIsNone(re.search(r"^\s*two_role_after\s*:", defaults.read_text(
            encoding="utf-8"), re.M))
        shipped = sorted([*SCRIPTS.glob("*.py"), *(SCRIPTS / "lib").glob("*.py")])
        self.assertGreater(len(shipped), 20, "the scan is looking in the wrong place")
        readers = [p.name for p in shipped
                   if any("two_role_after" in s for s in _string_reads(p))]
        self.assertEqual(readers, [], "a shipped script still reads review.two_role_after")

        self.assertIn("review.two-role", sdlc_md.RETIRED_CHECK_IDS)
        self.assertNotIn("review.two-role", sdlc_md.DOR_DOD_CHECK_IDS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- [ ] ACs pass [check: story.verify-ac]\n"
                "- [ ] signed off [check: review.two-role]\n"
                "- [ ] retired later [check: lean.retired-probe]\n", encoding="utf-8")
            with mock.patch.dict(sdlc_md.RETIRED_CHECK_IDS,
                                 {"lean.retired-probe": "retired by a later story"}):
                rc, out = _run(validate.main, ["check", "--root", str(root)])
                findings = validate.check_dor_dod(root)
            self.assertEqual(rc, 0, out)
            self.assertNotIn("unknown-check-id", out)
            for cid in ("review.two-role", "lean.retired-probe"):
                hit = [f for f in findings if f"[check: {cid}]" in f["message"]]
                self.assertEqual(len(hit), 1, findings)
                self.assertEqual(hit[0]["rule"], "retired-check-id")
                self.assertNotEqual(hit[0]["severity"], validate.SEVERITY_ERROR)
                self.assertIn("migrate", hit[0]["message"])
            self.assertIn("[retired-check-id]", out)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: leave a retired criterion's `Verified: yes` stamp in place - a node id,
        or a `-k` selector naming a deleted method, the shape US0298 AC1-AC3 carried past the
        hand-listed version of this check; keep a deleted class in its module.

        The deleted nodes are DERIVED: every class and `test_` function a changed test module
        defined at the base and no longer defines, the base being the parent of the commit
        that added this module (HEAD while it is uncommitted)."""
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = _deleted_nodes(base)
        for module, classes in AC5_NAMED.items():
            gone = deleted.get(module, {}).get("gone", set())
            for cls in classes:
                self.assertIn((cls, ""), gone, f"{module}::{cls} was to be deleted ({base})")
        # The shape the hand-listed check let through is caught, and a live selector is not.
        sprint_tests = ".claude/skills/sdlc-studio/scripts/tests/test_sprint.py"
        controls = {
            "us0298-k": ([f"- **Verify:** {US0298_AC1}", "- **Verified:** yes (2026-07-22)"],
                         ["us0298-k:1"]),
            "node-id": ([f"- **Verify:** pytest {sprint_tests}::ReachableEndStateTests",
                         "- **Verified:** yes (2026-07-22)"], ["node-id:1"]),
            "retired": ([f"- **Verify:** {US0298_AC1}",
                         "- **Verified:** manual (2026-09-25) - retired, superseded by US0916"],
                        []),
            "survives": ([f"- **Verify:** pytest {sprint_tests} -k "
                          "test_done_fixed_and_rung_end_units_do_not_hold_the_close",
                          "- **Verified:** yes (2026-09-25)"], []),
            "partly": ([f"- **Verify:** pytest {sprint_tests} -k rung_end_units_do_not_hold",
                        "- **Verified:** yes (2026-09-25)"], []),
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
