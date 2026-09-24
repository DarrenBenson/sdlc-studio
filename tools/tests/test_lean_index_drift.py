"""Mechanical index and epic drift is fixed at commit, not refused (US0899).

The gate's `index-derived` lane and reconcile's `epic-status-stale` kind used to refuse a commit,
and the remedy they named was always a command with no judgement in it: regenerate the index with
`reconcile apply`, or close an epic whose every child is terminal. The commit hook now applies
that remedy itself (`reconcile.py settle`), restages exactly the files it wrote, and the gate
reports the two kinds without failing. An epic whose children were all abandoned derives the new
epic terminal `Superseded`, so the auto-close can never mark a retired epic `Done`.

The mutants each test is written against are named in its docstring.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_index_drift.py
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

sys.path.insert(0, str(SKILL_SCRIPTS))
sys.path.insert(0, str(REPO / "tools"))
import reconcile  # noqa: E402 - the module under test, from the real skill tree
from lib import sdlc_md  # noqa: E402
from repo_writes import _clean_env  # noqa: E402 - the one scrub of repo-locating git variables

PASS_PY = "import sys\nsys.exit(0)\n"

#: US0001's row in the story index, reading Done.
US0001_DONE_ROW = r"(?m)^\| \[US0001\]\(US0001-x\.md\) \|.*\| Done \|"
PASS_SH = "#!/usr/bin/env bash\nexit 0\n"

#: The real skill scripts, copied ONCE for the module and symlinked into each hook fixture.
_SCRIPTS_TEMPLATE: Path | None = None


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


def _scripts_template() -> Path:
    """The real skill scripts minus their tests, with `gate.py` stubbed.

    `reconcile.py` and everything it reaches are the shipped files: the settle step is what
    is under test. `gate.py` is stubbed because this fixture is not a whole project, and a
    gate lane failing on it would refuse the commit for a reason nothing here caused; the
    gate's own half of the story is judged by the last test, over the real gate.
    """
    global _SCRIPTS_TEMPLATE
    if _SCRIPTS_TEMPLATE is None:
        holder = tempfile.mkdtemp(prefix="us0899-scripts-")
        dest = Path(holder) / "scripts"
        shutil.copytree(SKILL_SCRIPTS, dest,
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
        (dest / "gate.py").write_text(PASS_PY, encoding="utf-8")
        _SCRIPTS_TEMPLATE = dest
    return _SCRIPTS_TEMPLATE


def tearDownModule() -> None:
    if _SCRIPTS_TEMPLATE is not None:
        shutil.rmtree(_SCRIPTS_TEMPLATE.parent, ignore_errors=True)


_DIRS = {"US": "stories", "BG": "bugs"}


def _unit_text(uid: str, status: str) -> str:
    if uid.startswith("BG"):
        return f"# {uid}: a bug\n\n> **Status:** {status}\n> **Severity:** Low\n"
    return (f"# {uid}: a story\n\n> **Status:** {status}\n> **Epic:** EP0001\n\n"
            f"## Acceptance Criteria\n\n- **AC1:** a thing happens\n")


def _unit_path(root: Path, uid: str) -> Path:
    return root / "sdlc-studio" / _DIRS[uid[:2]] / f"{uid}-x.md"


def _epic_path(root: Path) -> Path:
    return root / "sdlc-studio" / "epics" / "EP0001-alpha.md"


def _write_epic(root: Path, children: dict) -> None:
    """EP0001, Draft, whose breakdown declares `children`; a box is ticked exactly when its
    child is terminal, as the live cascade would leave it."""
    lines = []
    for uid, status in children.items():
        utype = "bug" if uid.startswith("BG") else "story"
        tick = "x" if sdlc_md.is_terminal_status(utype, status) else " "
        lines.append(f"- [{tick}] [{uid}](../{_DIRS[uid[:2]]}/{uid}-x.md)")
    _epic_path(root).write_text(
        "# EP0001: Alpha\n\n> **Status:** Draft\n> **Created:** 2026-09-01\n\n"
        "## Story Breakdown\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def _workspace(root: Path, children: dict) -> Path:
    """An SDLC workspace: EP0001 over `children` ({id: status}), indexes derived by the real
    `reconcile apply`, and conformance grandfathered so the real gate judges only drift."""
    for sub in ("epics", "stories", "bugs", ".local"):
        (root / "sdlc-studio" / sub).mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "conformance:\n  adopt_after: 9999\n", encoding="utf-8")
    for uid, status in children.items():
        _unit_path(root, uid).write_text(_unit_text(uid, status), encoding="utf-8")
    _write_epic(root, children)
    with open(os.devnull, "w") as sink:
        subprocess.run([sys.executable, str(SKILL_SCRIPTS / "reconcile.py"), "apply",
                        "--root", str(root)], stdout=sink, stderr=sink, check=False)
    assert not reconcile.index_derived_issues(root), "the fixture's indexes must start derived"
    return root


def _finish_story(root: Path, uid: str = "US0001", status: str = "Done") -> None:
    """A status change written by hand, box ticked, index left behind - the drift under test."""
    path = _unit_path(root, uid)
    path.write_text(path.read_text(encoding="utf-8").replace(
        "> **Status:** Draft", f"> **Status:** {status}"), encoding="utf-8")
    epic = _epic_path(root)
    epic.write_text(epic.read_text(encoding="utf-8").replace(f"- [ ] [{uid}]", f"- [x] [{uid}]"),
                    encoding="utf-8")


class IndexDriftTests(unittest.TestCase):

    # --- the hook fixture ---------------------------------------------------------------

    def _hook_repo(self, tmp: Path) -> Path:
        """A throwaway repo carrying BOTH real hooks, the real skill scripts (gate stubbed) and
        the real repo-writes guard; every tools/ lane is stubbed to pass, so a refusal or a
        write can only have come from the settle step or the repo-writes lane."""
        root = tmp / "r"
        for rel in ("tools/tests", ".githooks", "node_modules/.bin"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        for name in ("pre-commit", "commit-msg"):
            dest = root / ".githooks" / name
            dest.write_text((REPO / ".githooks" / name).read_text(encoding="utf-8"),
                            encoding="utf-8")
            dest.chmod(0o755)
        from hookutil import hook_tool_scripts
        for name in hook_tool_scripts():
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")
        for name in ("lint-style.sh", "check_action_pins.sh", "skill-tests.sh"):
            p = root / "tools" / name
            p.write_text(PASS_SH, encoding="utf-8")
            p.chmod(0o755)
        (root / "tools" / "gate_timing.py").write_text(PASS_PY, encoding="utf-8")
        # REAL, written after the derivation above stubbed it: the lane AC1 must see green.
        (root / "tools" / "repo_writes.py").write_text(
            (REPO / "tools" / "repo_writes.py").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tools" / "tests" / "test_stub.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n", encoding="utf-8")
        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(PASS_SH, encoding="utf-8")
        md.chmod(0o755)
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        scripts.parent.mkdir(parents=True, exist_ok=True)
        scripts.symlink_to(_scripts_template(), target_is_directory=True)
        (root / ".gitignore").write_text("sdlc-studio/.local/\nnode_modules/\n__pycache__/\n",
                                         encoding="utf-8")
        (root / "tools" / "thing.py").write_text("VALUE = 1\n", encoding="utf-8")
        _workspace(root, {"US0001": "Draft"})
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _commit(self, root: Path) -> tuple[int, str]:
        out = subprocess.run(["git", "-C", str(root), "commit", "-m", "chore: finish a story"],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr

    @staticmethod
    def _head(root: Path, rel: str) -> str:
        return _git(root, "show", f"HEAD:{rel}").stdout

    def test_the_hook_applies_and_restages_mechanical_drift(self) -> None:
        """MUTANTS: delete the settle block from `.githooks/pre-commit` (the commit carries a
        stale index and a live epic); drop the `git add` from `reconcile.settle` (the fixes stay
        unstaged in the working tree); or run the settle AFTER the repo-writes snapshot (the lane
        reports the restaged paths as the suites' writes)."""
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _finish_story(root)
            (root / "tools" / "thing.py").write_text("VALUE = 2\n", encoding="utf-8")
            _git(root, "add", "-A")
            rc, out = self._commit(root)
            self.assertEqual(0, rc, f"the commit was refused:\n{out}")
            self.assertEqual("chore: finish a story",
                             _git(root, "log", "-1", "--format=%s").stdout.strip())
            landed = set(_git(root, "show", "--name-only", "--format=", "HEAD").stdout.split())
            for rel in ("sdlc-studio/stories/_index.md", "sdlc-studio/epics/_index.md",
                        "sdlc-studio/epics/EP0001-alpha.md"):
                self.assertIn(rel, landed, f"{rel} was not restaged into the commit:\n{out}")
            self.assertIn("> **Status:** Done", self._head(root, "sdlc-studio/epics/EP0001-alpha.md"))
            self.assertRegex(self._head(root, "sdlc-studio/stories/_index.md"), US0001_DONE_ROW)
            self.assertEqual([], reconcile.index_derived_issues(root),
                             "the committed tree still carries index drift")
            self.assertEqual("", _git(root, "status", "--porcelain").stdout,
                             "the fix was written but not everything it wrote was staged")
            self.assertRegex(out, r"(?m)^ {2}ok\s+repo-writes",
                             f"the repo-writes lane did not run green:\n{out}")
            self.assertIn("EP0001", out, "the hook did not name the epic it closed")

    def test_a_file_with_unstaged_edits_is_never_restaged(self) -> None:
        """MUTANTS: restage with `git add -u`, or add every written path without asking whether
        it was dirty before - the author's unstaged note enters the commit; drop the directory
        rule - an index derived from a sibling's unstaged status is committed; drop the epic
        input check - an epic is closed on a child status the commit does not carry."""
        note = "<!-- the author's own unstaged note -->"
        stories = "sdlc-studio/stories/_index.md"
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _finish_story(root)
            _git(root, "add", "-A")
            index = root / stories
            index.write_text(index.read_text(encoding="utf-8") + f"\n{note}\n", encoding="utf-8")
            rc, out = self._commit(root)
            self.assertEqual(0, rc, f"the commit was refused, and this story adds no refusal:\n{out}")
            self.assertNotIn(note, self._head(root, stories),
                             "the author's unstaged edit entered the commit")
            self.assertIn(note, index.read_text(encoding="utf-8"),
                          "the author's unstaged edit was lost from the working tree")
            self.assertIn(f"left {stories}", out,
                          f"the hook did not name the drift it left unstaged:\n{out}")
            self.assertIn("unstaged", out)
            # The file with no edits of its own was still restaged.
            self.assertIn("> **Status:** Done", self._head(root, "sdlc-studio/epics/EP0001-alpha.md"))

        # Unstaged work reaches a commit DERIVED, too: an index regenerated from a sibling's
        # unstaged status, or an epic closed on a child status the commit does not carry.
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _unit_path(root, "US0002").write_text(_unit_text("US0002", "Draft"), encoding="utf-8")
            with open(os.devnull, "w") as sink:
                subprocess.run([sys.executable, str(SKILL_SCRIPTS / "reconcile.py"), "apply",
                                "--root", str(root)], stdout=sink, stderr=sink, check=False)
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "--no-verify", "-m", "a second story")
            _finish_story(root)                      # US0001 Done and ticked - NOT staged
            sibling = _unit_path(root, "US0002")
            sibling.write_text(sibling.read_text(encoding="utf-8").replace(
                "# US0002: a story", "# US0002: a story, retitled"), encoding="utf-8")
            _git(root, "add", str(sibling))          # the only artefact change staged
            rc, out = self._commit(root)
            self.assertEqual(0, rc, out)
            self.assertIn("> **Status:** Draft", self._head(root, "sdlc-studio/epics/EP0001-alpha.md"),
                          "the epic was closed on a child status the commit does not carry")
            self.assertIn("left EP0001", out, f"the unclosed epic was not named:\n{out}")
            self.assertNotRegex(self._head(root, stories), US0001_DONE_ROW,
                             "an index row derived from unstaged work entered the commit")
            self.assertIn(f"left {stories}", out, out)

    def test_a_pathspec_commit_settles_nothing_and_the_next_commit_reverts_nothing(self) -> None:
        """`git commit -- <paths>` runs the hook against a TEMPORARY index. Staging into it lands
        in that commit, but the repository's own index keeps the old bytes, so the next plain
        commit silently reverted the settled epic, both indexes and the actuals ledger.

        MUTANT: make `_temporary_index` answer None - the pathspec commit settles, and the plain
        commit after it reverts every file it settled."""
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _finish_story(root)
            out = subprocess.run(
                ["git", "-C", str(root), "commit", "-m", "chore: finish a story", "--",
                 "sdlc-studio/stories/US0001-x.md", "sdlc-studio/epics/EP0001-alpha.md"],
                capture_output=True, text=True, env=_clean_env())
            self.assertEqual(0, out.returncode, out.stdout + out.stderr)
            self.assertIn("temporary index", out.stdout + out.stderr,
                          "the hook did not say why it settled nothing")
            (root / "tools" / "thing.py").write_text("VALUE = 3\n", encoding="utf-8")
            _git(root, "add", "tools/thing.py")
            rc, said = self._commit(root)
            self.assertEqual(0, rc, said)
            self.assertEqual("", _git(root, "diff", "--stat", "HEAD~1", "HEAD", "--",
                                      "sdlc-studio").stdout,
                             "the plain commit after a pathspec commit reverted artefacts")
            self.assertEqual("", _git(root, "diff", "--cached", "--stat").stdout)

    def test_an_untracked_sibling_keeps_its_index_unstaged(self) -> None:
        """MUTANT: read only modified paths in `_unstaged` (drop `--untracked-files=all`) - the
        index regenerated with a row for a file the commit does not carry is committed."""
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _finish_story(root)
            _git(root, "add", "-A")
            _unit_path(root, "US0002").write_text(_unit_text("US0002", "Draft"),
                                                  encoding="utf-8")   # never staged
            rc, out = self._commit(root)
            self.assertEqual(0, rc, out)
            self.assertNotIn("[US0002]", self._head(root, "sdlc-studio/stories/_index.md"),
                             "an index row for an untracked file entered the commit")
            self.assertIn("left sdlc-studio/stories/_index.md", out, out)

    def test_a_staged_rename_is_read_as_one_path(self) -> None:
        """MUTANT: drop the rename/copy source skip in `_unstaged` - the source path is parsed
        as an entry of its own and a phantom path appears."""
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _git(root, "mv", "tools/thing.py", "tools/renamed.py")
            (root / "tools" / "renamed.py").write_text("VALUE = 9\n", encoding="utf-8")
            self.assertEqual(["tools/renamed.py"], sorted(reconcile._unstaged(root)))

    def test_one_epic_fault_leaves_the_rest_of_the_settle_running(self) -> None:
        """MUTANT: catch only ValueError/FileNotFoundError around the epic close - a KeyError
        from one epic aborts the settle and no index is regenerated."""
        import transition
        with tempfile.TemporaryDirectory() as d:
            root = self._hook_repo(Path(d))
            _finish_story(root)
            _git(root, "add", "-A")

            def boom(*_a, **_k):
                raise KeyError("status")
            with unittest.mock.patch.object(transition, "transition", boom):
                res = reconcile.settle(root)
            self.assertEqual("EP0001", res["refused"][0][0])
            self.assertIn("sdlc-studio/stories/_index.md", res["restaged"],
                          "one epic's fault stopped the index regeneration")

    # --- the derivation -----------------------------------------------------------------

    def test_an_epic_of_abandoned_children_derives_superseded(self) -> None:
        """MUTANTS: derive `default_terminal_status("epic")` or the first sorted terminal (the
        old `terminal[0]`) for every stale epic - an abandoned epic derives Done; or leave
        `Superseded` out of the epic vocabulary - the settle's transition is refused."""
        self.assertIn("Superseded", sdlc_md.STATUS_VOCAB["epic"])
        self.assertTrue(sdlc_md.is_terminal_status("epic", "Superseded"))
        self.assertEqual("Done", sdlc_md.default_terminal_status("epic"),
                         "a bare close must still derive the successful terminal")
        abandoned = {"US0001": "Superseded", "US0002": "Won't Implement", "BG0001": "Won't Fix"}
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), abandoned)
            drift = reconcile.epic_status_stale_drift(root)
            self.assertEqual([("EP0001", "Superseded")], [(x["id"], x["target"]) for x in drift])
            self.assertIn("--status Superseded", drift[0]["fix"])
            # Through the shipped entry point: the auto-apply must never mark it Done.
            _git(root, "init", "-q")
            _git(root, "add", "-A")
            _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                 "--no-verify", "-m", "fixture")
            with contextlib.redirect_stdout(io.StringIO()) as said:
                rc = reconcile.main(["settle", "--root", str(root)])
            self.assertEqual(0, rc)
            self.assertIn("EP0001: Draft -> Superseded", said.getvalue())
            self.assertIn("> **Status:** Superseded", _epic_path(root).read_text(encoding="utf-8"))
            self.assertEqual([], reconcile.epic_status_stale_drift(root))
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0001": "Done", "US0002": "Superseded",
                                        "BG0001": "Won't Fix"})
            self.assertEqual(["Done"], [x["target"] for x in reconcile.epic_status_stale_drift(root)])
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0002": "Superseded", "BG0001": "Fixed"})
            self.assertEqual(["Done"], [x["target"] for x in reconcile.epic_status_stale_drift(root)],
                             "a fixed bug is delivered work, so the epic derives Done")

    # --- the gate -----------------------------------------------------------------------

    def _gate(self, root: Path) -> tuple[int, dict]:
        proc = subprocess.run([sys.executable, str(SKILL_SCRIPTS / "gate.py"), "--root", str(root),
                               "--format", "json"], capture_output=True, text=True)
        return proc.returncode, {c["check"]: c for c in json.loads(proc.stdout)["checks"]}

    def test_the_gate_reports_mechanical_drift_without_failing(self) -> None:
        """MUTANTS: leave `index-derived` blocking, or count `epic-status-stale` in the reconcile
        lane - the first gate run fails; or exempt every reconcile kind - the second passes."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0001": "Draft"})
            _finish_story(root)
            kinds = {x["kind"] for x in reconcile.detect_all(root)[1]}
            self.assertEqual({"status-mismatch", "epic-status-stale"}, kinds,
                             "the fixture must carry exactly the mechanical drift")
            rc, lanes = self._gate(root)
            self.assertEqual(0, rc, f"mechanical drift failed the gate: {lanes}")
            self.assertFalse(lanes["index-derived"]["blocking"])
            self.assertEqual("fail", lanes["index-derived"]["status"],
                             "the lane must still REPORT the drift, not go quiet")
            self.assertIn("story", lanes["index-derived"]["detail"])
            self.assertIn("epic-status-stale", lanes["reconcile"]["detail"])

            # Any other reconcile kind still fails: untick the finished story's box.
            epic = _epic_path(root)
            epic.write_text(epic.read_text(encoding="utf-8").replace("- [x] [US0001]",
                                                                     "- [ ] [US0001]"),
                            encoding="utf-8")
            self.assertIn("breakdown-unticked", {x["kind"] for x in reconcile.detect_all(root)[1]})
            rc, lanes = self._gate(root)
            self.assertEqual(1, rc, "a non-mechanical drift kind no longer fails the gate")
            self.assertEqual(("fail", True), (lanes["reconcile"]["status"],
                                              lanes["reconcile"]["blocking"]))

    def test_only_what_settle_applies_is_exempt(self) -> None:
        """MUTANTS: exempt by kind alone (drop the DEFAULT_TYPES scope in `settled_items`) - a
        review with no index row passes the gate, though settle never writes the meta indexes;
        or ignore `missing_unapplied` - a row `apply` cannot write is claimed as settled."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0001": "Draft"})
            reviews = root / "sdlc-studio" / "reviews"
            reviews.mkdir()
            (reviews / "_index.md").write_text("# Reviews\n\n| ID | Title |\n| --- | --- |\n"
                                               "| [RV0001](RV0001-a.md) | a |\n", encoding="utf-8")
            (reviews / "RV0001-a.md").write_text("# RV0001: a\n", encoding="utf-8")
            (reviews / "RV0002-b.md").write_text("# RV0002: b\n", encoding="utf-8")
            drift = reconcile.detect_all(root)[1]
            self.assertEqual([("review", "missing-row")], [(x["type"], x["kind"]) for x in drift])
            self.assertEqual([], reconcile.settled_items(root, drift))
            rc, lanes = self._gate(root)
            self.assertEqual(1, rc, "a meta missing-row passed the gate")
            self.assertEqual(1, lanes["reconcile"]["count"])
            self.assertNotIn("mechanical", lanes["reconcile"]["detail"])
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0001": "Draft"})
            index = root / "sdlc-studio" / "stories" / "_index.md"
            index.write_text(index.read_text(encoding="utf-8").replace(
                "| ID | Title | Epic | Status |", "| Key | Title | Epic | Status |").replace(
                "| ID | Title | Status | Points | Owner |", "| Key | Title | Status | Points | Owner |"),
                encoding="utf-8")
            _unit_path(root, "US0002").write_text(_unit_text("US0002", "Draft"), encoding="utf-8")
            drift = reconcile.detect_all(root)[1]
            self.assertIn(("story", "missing-row"), [(x["type"], x["kind"]) for x in drift])
            self.assertEqual(["US0002"],
                             reconcile.apply_type("story", root, dry_run=True)["missing_unapplied"])
            self.assertEqual([], reconcile.settled_items(root, drift),
                             "a row apply cannot write was claimed as settled")
            rc, lanes = self._gate(root)
            self.assertEqual(1, rc)
            self.assertNotIn("mechanical", lanes["reconcile"]["detail"])

    def test_the_sprint_close_derives_the_same_status(self) -> None:
        """The sprint close derives parent epics too. MUTANT: restore its hard-coded `Done` - an
        epic of abandoned units closes Done at sign-off."""
        import sprint
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(Path(d), {"US0001": "Superseded", "BG0001": "Won't Fix"})
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(["EP0001"], sprint._derive_parent_epics(root, ["US0001"]))
            self.assertIn("> **Status:** Superseded", _epic_path(root).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
