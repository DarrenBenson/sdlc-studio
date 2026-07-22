"""The pre-commit gate's concurrent-write window guard (US0308, CR0388 as CORRECTED).

The incident this guards against was NOT a hand-applied mutant. An independent reviewer
built a helper directory with `ln -sf <repo>/scripts/*.py .` and ran
`git show <sha>:...retro.py > retro.py` inside it; the redirect followed the symlink and
overwrote the live working tree with a pre-sprint revision, reverting two units' work.
A `git add -A` in the author's session then staged it.

Two things follow, and both shape these tests. The guard cannot try to recognise a
mutant, because there was none. And it cannot rest on the suite going red, because that
commit was refused only by luck - the reverted source happened to fail the suite, and a
rewrite leaving the suite green would have committed silently under a commit message
about paperwork.

So the rule is: while a window is open, a staged path the window claims is refused,
however green everything else is (D0053 - refuse, not warn; a warning inside a passing
run reads as noise, which is exactly the failure mode observed).

These tests RUN THE REAL HOOK in a throwaway repo whose every other guard is stubbed to
PASS, so the hook reaches `fail=0` and the refusal can only come from the window guard.
The pairing of AC1 with AC4 is what makes the claim checkable: the SAME staged content
commits cleanly with no window on disk, and is refused with one.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"

PASS_SH = "#!/usr/bin/env bash\nexit 0\n"
PASS_PY = "import sys\nsys.exit(0)\n"

#: The fixture's stand-in for `gate.py`, running the REAL `window` lane and nothing else.
#:
#: It used to be PASS_PY, and that stub is what let the two halves of this feature contradict
#: each other in the same commit: `gate.py --root .` carries a `window` lane of its own, the
#: lane was BLOCKING on the record's EXISTENCE, and the hook runs it a few lines below this
#: guard. One real run printed "No staged path is claimed by it, so this commit proceeds" AND
#: "[FAIL] window: a rewrite window is OPEN" AND "Commit blocked." The AC2 test below could not
#: see it, because the stub exited 0 before reaching the lane that decided the verdict its own
#: name claims (L-0174: a test written to close a class, stubbed past the code that holds it).
#:
#: Only the window lane, because everything else the real gate reads (artefact indexes, a
#: conformance surface, a docs tree) is absent from a fixture built to isolate this guard - and
#: a lane failing for a missing index would refuse every commit here for the wrong reason.
#: It also LOGS its verdict to a file, because the hook prints a passing gate's output nowhere -
#: so stdout alone cannot tell "the lane ran and passed" from "the lane never ran", which is the
#: exact confusion the stub created.
GATE_WINDOW_LANE = """\
import sys
sys.path.insert(0, {scripts!r})
import gate
lane = gate.DEFAULT_CHECKS["window"](".")
with open("sdlc-studio/.local/gate-window-lane.log", "a", encoding="utf-8") as fh:
    fh.write(("FAIL " if lane["count"] else "ok ") + lane["detail"] + "\\n")
if lane["count"]:
    print("[FAIL] window: " + lane["detail"])
    sys.exit(1)
sys.exit(0)
"""

#: Where the stub above records that it ran.
GATE_LANE_LOG = "sdlc-studio/.local/gate-window-lane.log"

#: The hook's own branch marker for a commit that ran no unit suite. Asserting on it is
#: how AC4's "lane selection unchanged" claim stays checkable rather than assumed.
DOCS_ONLY = "no test-relevant file staged"

#: Git hands a pre-commit hook GIT_INDEX_FILE pointing at the OUTER repo's index. Every
#: git call here must run with those gone, or this fixture writes its tree into the real
#: repo's pending commit.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _clean_env() -> dict:
    env = dict(os.environ)
    for var in _GIT_ENV_VARS:
        env.pop(var, None)
    return env


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


class WindowGuardTests(unittest.TestCase):
    """A staged path an open window claims is refused; anything else is untouched."""

    #: The file the window claims. Deliberately test-relevant (`tools/`), so the commit
    #: that stages it is one whose unit suites RUN - the "green is not enough" case.
    CLAIMED = "tools/thing.py"
    UNCLAIMED = "README.md"

    def _repo(self, tmp: Path) -> Path:
        """A throwaway repo whose every guard PASSES, so only the window guard can refuse."""
        root = tmp / "r"
        (root / "tools" / "tests").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / ".githooks").mkdir(parents=True)
        (root / ".claude" / "skills" / "sdlc-studio" / "scripts").mkdir(parents=True)
        (root / "node_modules" / ".bin").mkdir(parents=True)

        hook = root / ".githooks" / "pre-commit"
        hook.write_text(HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        hook.chmod(0o755)

        for name in ("lint-style.sh", "check_action_pins.sh", "skill-tests.sh"):
            p = root / "tools" / name
            p.write_text(PASS_SH, encoding="utf-8")
            p.chmod(0o755)
        for name in ("check_links.py", "validate_skill.py", "check_versions.py",
                     "check_budgets.py", "check_neutrality.py", "gate_timing.py"):
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")
        scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        for name in ("engagement_floor.py", "reconcile.py"):
            (scripts / name).write_text(PASS_PY, encoding="utf-8")
        # NOT stubbed to pass: the real window lane, which is the other half of this feature
        # and the half that contradicted the guard above.
        (scripts / "gate.py").write_text(
            GATE_WINDOW_LANE.format(scripts=str(REPO / ".claude" / "skills" / "sdlc-studio"
                                                / "scripts")), encoding="utf-8")
        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(PASS_SH, encoding="utf-8")
        md.chmod(0o755)
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        # `unittest discover` over an EMPTY dir exits 1, which would fail the tool-tests
        # lane and make every case reach the hook's blocked branch instead of its own.
        (root / "tools" / "tests" / "test_stub.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n", encoding="utf-8")
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        (root / self.CLAIMED).write_text("VALUE = 1\n", encoding="utf-8")
        (root / self.UNCLAIMED).write_text("notes\n", encoding="utf-8")

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _open_window(self, root: Path, *, paths: list[str] | None = None,
                     name: str = "review-window.json", raw: str | None = None) -> Path:
        rec = root / "sdlc-studio" / ".local" / name
        rec.parent.mkdir(parents=True, exist_ok=True)
        rec.write_text(raw if raw is not None else json.dumps({
            "owner": "independent-review (RUN-01KY321Q)",
            "opened": "2026-07-22T10:00:00Z",
            "paths": paths if paths is not None else [self.CLAIMED],
        }), encoding="utf-8")
        return rec

    def _commit(self, root: Path, rel: str, body: str) -> tuple[int, str]:
        """Write `rel`, stage everything (the `git add -A` of the incident) and commit."""
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        _git(root, "add", "-A")
        out = subprocess.run(["git", "-C", str(root), "commit", "-m", "docs: paperwork"],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr

    # -- AC1 ---------------------------------------------------------------------
    def test_a_green_staged_path_claimed_by_an_open_window_is_refused(self) -> None:
        """The case today's gate cannot catch. Every lane is green - the staged content
        is valid Python and every guard is stubbed to pass - and the commit is still
        refused, because a window claims the path. The rewrite is a plain value change,
        not a recognisable mutant, exactly as the corrected mechanism describes."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root)
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertNotEqual(rc, 0, f"the commit was NOT refused:\n{out}")
            self.assertIn("window", out.lower(), "the refusal must name the open window")
            self.assertIn("independent-review (RUN-01KY321Q)", out, "it must name the owner")
            self.assertIn(self.CLAIMED, out, "it must name the offending staged path")
            # ...and the refusal actually stopped the commit, rather than merely printing.
            self.assertEqual(_git(root, "log", "--format=%s").stdout.strip(), "fixture")

    # -- AC2 ---------------------------------------------------------------------
    def test_staging_only_unclaimed_paths_proceeds_while_a_window_is_open(self) -> None:
        """The guard scopes staging; it does not freeze the tree for a review's duration.
        Every ceremony commit during a review is this shape."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root)
            rc, out = self._commit(root, self.UNCLAIMED, "notes and more notes\n")
            self.assertEqual(rc, 0, f"a scoped commit was refused:\n{out}")
            self.assertIn("docs: paperwork", _git(root, "log", "--format=%s").stdout)

    # -- AC3 ---------------------------------------------------------------------
    def test_the_refusal_names_the_scoped_staging_remedy(self) -> None:
        """Self-diagnosing, per this hook's convention: the way forward and the way to
        clear a window a killed process left behind."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            rec = self._open_window(root)
            _, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertIn("git add -A", out, "it must name the staging habit to stop")
            self.assertIn("git add <path>", out, "it must name the scoped-staging remedy")
            self.assertIn(rec.relative_to(root).as_posix(), out,
                          "it must name the record to delete when its owner is gone")
            self.assertIn("rm ", out, "clearing a stale window must be spelled out")

    # -- AC4 ---------------------------------------------------------------------
    def test_a_record_that_names_its_own_clearing_command_has_it_printed(self) -> None:
        """A window opened by a tool knows how it is closed, and says so in the record.
        Printing the record's own `clear_with` beats any command this hook could guess at,
        and the `rm` line stays as the answer that is true whoever wrote the record."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            rec = root / "sdlc-studio" / ".local" / "mutation-window.json"
            rec.parent.mkdir(parents=True, exist_ok=True)
            rec.write_text(json.dumps({
                "owner": "mutation.py run", "opened_at": "2026-07-22T10:00:00Z",
                "paths": [self.CLAIMED],
                "clear_with": "mutation.py window close --owner 'mutation.py run'",
            }), encoding="utf-8")
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("mutation.py window close", out)
            self.assertIn("opened 2026-07-22T10:00:00Z", out,
                          "the record's own opened_at spelling must be read")
            self.assertIn("rm sdlc-studio/.local/mutation-window.json", out)

    def test_no_window_open_leaves_the_hook_behaviour_unchanged(self) -> None:
        """The normal path pays nothing: same staged content as AC1, no record on disk,
        commit succeeds, and the guard says nothing at all. This is also what makes AC1
        a real finding rather than a hook that refuses everything."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertEqual(rc, 0, f"a commit with no window open was refused:\n{out}")
            self.assertNotIn("window", out.lower(),
                             "with no window on disk the guard must be silent")
            self.assertNotIn(DOCS_ONLY, out,
                             "lane selection changed: a tools/ change must still run the suites")
            self.assertIn("gate green.", out)

    # -- beyond the ACs: the ways a reader of the record can lie ------------------
    def test_an_unreadable_record_is_read_as_open_not_as_closed(self) -> None:
        """A truncated or half-written record must never read as 'no window'. It claims
        the whole tree until someone says otherwise - the safe direction for a guard whose
        whole purpose is to stop a write nobody announced."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, raw='{"owner": "reviewer", "pat')
            rc, out = self._commit(root, self.UNCLAIMED, "notes, truncated-record case\n")
            self.assertNotEqual(rc, 0, f"a truncated record was read as closed:\n{out}")
            self.assertIn("unreadable", out.lower())

    def test_a_record_naming_no_paths_claims_the_whole_tree(self) -> None:
        """Same direction: a window that does not say what it may rewrite has not said it
        may rewrite nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, paths=[])
            rc, out = self._commit(root, self.UNCLAIMED, "notes, path-less-record case\n")
            self.assertNotEqual(rc, 0, f"a path-less window was read as claiming nothing:\n{out}")

    def test_a_directory_claim_covers_the_files_under_it(self) -> None:
        """The realistic shape of a review window: a whole scripts directory, not a list
        of every file in it. Nested, because a claim on `tools/` that covered only its
        immediate children would miss most of what a review touches."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, paths=["tools/"])
            rc, out = self._commit(root, "tools/nested/deep.py", "VALUE = 999\n")
            self.assertNotEqual(rc, 0, f"a directory claim did not cover its files:\n{out}")
            self.assertIn("tools/nested/deep.py", out)

    def test_a_claim_on_the_repo_root_claims_everything(self) -> None:
        """`/` and `.` are how a reviewer says "I may rewrite anything in here". Read as a
        literal path they would match nothing, which is the fail-OPEN direction: the record
        says the whole tree is in play and the guard would wave the commit through."""
        for root_claim in ("/", "."):
            with self.subTest(claim=root_claim), tempfile.TemporaryDirectory() as d:
                root = self._repo(Path(d))
                self._open_window(root, paths=[root_claim])
                rc, out = self._commit(root, self.UNCLAIMED, "notes, root-claim case\n")
                self.assertNotEqual(rc, 0, f"a claim on {root_claim!r} claimed nothing:\n{out}")

    def test_one_matching_claim_among_several_is_enough(self) -> None:
        """A window claims a LIST of paths. Refusal needs one of them to match, not all
        of them: a review claiming three files and a commit staging the second must be
        refused, and every case above uses a single claim, so nothing else pins this."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, paths=["some/other.py", self.CLAIMED, "third/one.py"])
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertNotEqual(rc, 0, f"a matching claim among several did not refuse:\n{out}")
            self.assertIn(self.CLAIMED, out)

    def test_a_glob_claim_matches_by_pattern(self) -> None:
        """The third clause of the matcher, which neither of the other two can satisfy:
        a window claiming `tools/*.py` rather than a file or a directory."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, paths=["tools/*.py"])
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertNotEqual(rc, 0, f"a glob claim matched nothing:\n{out}")
            self.assertIn(self.CLAIMED, out)

    def test_the_gate_lane_does_not_contradict_the_guard_in_the_same_run(self) -> None:
        """The finding, stated as the property. AC2 above proves the commit LANDS; this proves
        the run contains no refusal at all - the shape observed was one run printing both
        "No staged path is claimed by it, so this commit proceeds" and "[FAIL] window", with
        the blocking half winning. Whatever refuses, the hook and the gate must agree."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root)
            rc, out = self._commit(root, self.UNCLAIMED, "notes, no-contradiction case\n")
            self.assertEqual(rc, 0, f"a scoped commit was refused:\n{out}")
            self.assertNotIn("[FAIL]", out, f"the gate lane refused what the guard allowed:\n{out}")
            self.assertNotIn("Commit blocked", out, out)
            self.assertIn("this commit proceeds", out)

    def test_the_gate_lane_is_actually_reached_by_this_fixture(self) -> None:
        """The control on the fixture itself. A gate stubbed past its window lane made the test
        above unfalsifiable, so something has to prove the lane RUNS here - and the hook prints
        a passing gate's output nowhere, which is why the lane logs its own verdict."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root)
            _, out = self._commit(root, self.UNCLAIMED, "notes, lane-reached case\n")
            log = root / GATE_LANE_LOG
            self.assertTrue(log.exists(),
                            f"the real gate window lane never ran in this fixture:\n{out}")
            verdict = log.read_text(encoding="utf-8")
            self.assertTrue(verdict.startswith("ok "), verdict)
            self.assertIn("OPEN", verdict, "the lane did not even see the window")

    # -- the ways a record can defeat the matcher --------------------------------
    def test_a_record_that_is_not_a_json_object_claims_the_whole_tree(self) -> None:
        """The third fail-safe reading the record contract names, and the one that had no test:
        a JSON array, string or number is a window record nobody can read. Mutating the hook's
        non-object branch from [EVERYTHING] to [] survived the whole suite."""
        for raw in ('["tools/thing.py"]', '"just a string"', "42", "null"):
            with self.subTest(record=raw), tempfile.TemporaryDirectory() as d:
                root = self._repo(Path(d))
                self._open_window(root, raw=raw)
                rc, out = self._commit(root, self.UNCLAIMED, "notes, non-object case\n")
                self.assertNotEqual(rc, 0, f"a non-object record claimed nothing:\n{out}")
                self.assertIn("unreadable", out.lower(), out)

    def test_a_claim_the_matcher_cannot_interpret_claims_the_whole_tree(self) -> None:
        """FAIL SAFE, not fail open. Every shape below was reproduced end to end against the
        real hook and COMMITTED: `paths` holding objects, nested lists or numbers was str()-ed
        into a pattern that matched nothing at all."""
        for claim in ([{"path": "tools/thing.py"}], [["tools/thing.py"]], [0], [None]):
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as d:
                root = self._repo(Path(d))
                self._open_window(root, paths=claim)
                rc, out = self._commit(root, self.UNCLAIMED, "notes, bad-claim case\n")
                self.assertNotEqual(rc, 0,
                                    f"an uninterpretable claim waved the commit through:\n{out}")

    def test_an_absolute_claim_claims_the_whole_tree(self) -> None:
        """`git diff --cached --name-only` is repo-relative, so an absolute claim can never
        equal a staged path. `window open --paths /abs/tools/thing.py` printed "Commits in this
        tree will be refused until it is closed" and the commit rewriting that exact file
        landed. Windows are normalised at open time now; a record already on disk is read here
        as claiming everything."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._open_window(root, paths=[str(root / self.CLAIMED)])
            rc, out = self._commit(root, self.UNCLAIMED, "notes, absolute-claim case\n")
            self.assertNotEqual(rc, 0, f"an absolute claim matched nothing:\n{out}")

    def test_a_record_in_the_windows_directory_is_found_too(self) -> None:
        """Both spellings of the record contract are read: a single `*window*.json` file,
        and one file per window under `windows/`. A reader that found only one of them
        would report 'no window' while a window was open."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            wdir = root / "sdlc-studio" / ".local" / "windows"
            wdir.mkdir(parents=True)
            (wdir / "reviewer.json").write_text(json.dumps(
                {"owner": "reviewer", "opened": "2026-07-22T10:00:00Z",
                 "paths": [self.CLAIMED]}), encoding="utf-8")
            rc, out = self._commit(root, self.CLAIMED, "VALUE = 999\n")
            self.assertNotEqual(rc, 0, f"a windows/ record was not read:\n{out}")
            self.assertIn(self.CLAIMED, out)


def _guard_module():
    """The guard's reader, lifted out of the hook and executed as a module.

    The class above drives the guard through real commits, which is the truth of it, but a
    real commit cannot make `git diff --cached` fail on demand, and that branch decides
    whether a guard that cannot see the index refuses or waves the commit through. This
    reads the SAME source the hook runs - the heredoc, cut at its `try:` launcher so
    importing it does not call `sys.exit` - so the two layers can never test different
    code.
    """
    text = HOOK.read_text(encoding="utf-8")
    start = text.index("window_out=\"$(python3 - <<'PY'\n") + len("window_out=\"$(python3 - <<'PY'\n")
    end = text.index("\nPY\n", start)
    body = text[start:end].split("\ntry:\n")[0]
    ns: dict = {"__name__": "window_guard"}
    exec(compile(body, str(HOOK) + " (window guard heredoc)", "exec"), ns)
    return ns


class _FakeProc:
    def __init__(self, returncode: int, stdout: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout


class WindowRecordReaderTests(unittest.TestCase):
    """The reader's branches a real commit cannot reach."""

    def test_a_git_failure_is_not_read_as_nothing_staged(self) -> None:
        """If the staged list cannot be read while a window is open, the honest answer is
        "I cannot tell", and the safe one is to refuse. Reading it as an empty list would
        wave through exactly the commit the guard exists to stop."""
        ns = _guard_module()
        ns["subprocess"] = type("S", (), {"run": staticmethod(
            lambda *a, **k: _FakeProc(128, ""))})()
        self.assertIsNone(ns["staged_paths"](),
                          "a failed git call must not be reported as an empty index")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "review-window.json").write_text(
                json.dumps({"owner": "reviewer", "paths": ["tools/thing.py"]}),
                encoding="utf-8")
            cwd = os.getcwd()
            os.chdir(root)
            try:
                import contextlib
                import io
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = ns["main"]()
            finally:
                os.chdir(cwd)
        self.assertEqual(rc, 1, "an unreadable index with a window open must refuse")
        self.assertIn("could not be read", buf.getvalue())

    def test_a_dot_slash_prefixed_claim_is_normalised(self) -> None:
        """`./tools/thing.py` and `tools/thing.py` are the same file. Git reports the
        second; a record may well carry the first."""
        claims = _guard_module()["claims"]
        self.assertTrue(claims("./tools/thing.py", "tools/thing.py"))
        self.assertTrue(claims("./tools", "tools/thing.py"))

    def test_an_unrelated_path_is_not_claimed(self) -> None:
        """The negative control: without it every assertion above is satisfied by a
        matcher that returns True."""
        claims = _guard_module()["claims"]
        self.assertFalse(claims("tools/thing.py", "README.md"))
        self.assertFalse(claims("tools/", "toolsmith.py"))

    def _parse(self, raw: str):
        """`parse` over a record written to disk, in ISOLATION from the rest of the hook.

        The end-to-end cases in the class above cannot pin this reader on their own: the hook
        also runs the gate's window lane, which refuses on the same records for its own reasons,
        so a commit stays blocked even with this branch broken. Mutating the two readings below
        SURVIVED every end-to-end test in this file and was killed only here."""
        with tempfile.TemporaryDirectory() as d:
            rec = Path(d) / "review-window.json"
            rec.write_text(raw, encoding="utf-8")
            return _guard_module()["parse"](rec)

    def test_a_record_that_is_not_a_json_object_claims_everything(self) -> None:
        """The record contract names three fail-safe readings "each with its own test"; this
        was the one with none. A JSON array, string or number parses fine and is not a window
        record, and reading it as claiming nothing is the fail-OPEN direction."""
        for raw in ('["tools/thing.py"]', '"a string"', "42", "null"):
            with self.subTest(record=raw):
                owner, _, claimed, _ = self._parse(raw)
                self.assertEqual(claimed, ["*"], raw)
                self.assertIn("unreadable", owner, raw)

    def test_a_claim_that_is_not_a_string_claims_everything(self) -> None:
        """`paths` holding objects, nested lists, numbers or nulls. Each was str()-ed into a
        pattern that could match nothing, and each COMMITTED against the real hook."""
        for claim in ([{"path": "tools/thing.py"}], [["tools/thing.py"]], [0], [None],
                      ["tools/thing.py", 0]):
            with self.subTest(claim=claim):
                _, _, claimed, _ = self._parse(json.dumps({"owner": "o", "paths": claim}))
                self.assertEqual(claimed, ["*"], claim)

    def test_a_record_of_plain_string_claims_is_left_alone(self) -> None:
        """The negative control on both readings above: a well-formed record must keep its own
        claims, or the guard refuses every commit in every tree and gets switched off."""
        _, _, claimed, _ = self._parse(json.dumps(
            {"owner": "o", "paths": ["tools/thing.py", "scripts/"]}))
        self.assertEqual(claimed, ["tools/thing.py", "scripts/"])


def _skill_module(name: str):
    """A shipped skill script, imported by path."""
    import importlib.util
    scripts = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(f"{name}_for_window_contract",
                                                  scripts / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class OneRecordContractTests(unittest.TestCase):
    """The record contract has one meaning, and three pieces of code implement it: this hook's
    inline reader, `mutation`'s reader, and the gate's `window` lane.

    The hook's reader cannot import the skill (it must work in a clone where the scripts are
    absent or broken - a guard that cannot run is a guard that is not there), so the duplication
    is deliberate. What is NOT acceptable is the duplication drifting: `mutation.read_window`
    read one fixed filename while the hook read two spellings, so a record at
    `.local/windows/reviewer.json` blocked commits, was reported "no rewrite window is open" by
    `window status`, and let `window open` declare a SECOND writer over the same tree. These
    tests are the mechanical agreement the one-contract claim rests on.
    """

    def _tree(self, root: Path, *rels: str) -> None:
        for rel in rels:
            p = root / "sdlc-studio" / ".local" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"owner": "o", "paths": ["tools/thing.py"]}),
                         encoding="utf-8")

    def test_both_readers_discover_the_same_records(self) -> None:
        mutation = _skill_module("mutation")
        hook_records = _guard_module()["records"]
        cases = (
            (),
            ("mutation-window.json",),
            ("review-window.json",),
            ("windows/reviewer.json",),
            ("mutation-window.json", "windows/reviewer.json", "review-window.json"),
        )
        for rels in cases:
            with self.subTest(records=rels), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio" / ".local").mkdir(parents=True)
                self._tree(root, *rels)
                # the hook reads records relative to the repo root it cd'd into
                cwd = os.getcwd()
                os.chdir(root)
                try:
                    from_hook = sorted(p.as_posix() for p in hook_records())
                finally:
                    os.chdir(cwd)
                from_tool = sorted(
                    Path(p).relative_to(root).as_posix() for p in mutation.window_records(root))
                self.assertEqual(from_hook, from_tool)
                self.assertEqual(len(from_tool), len(rels))

    def test_both_matchers_agree_on_every_claim_shape(self) -> None:
        """The hook's `claims` and the gate lane's `_window_claims` decide the same commits.
        Every row below is a shape that was reproduced against the real hook."""
        gate = _skill_module("gate")
        claims = _guard_module()["claims"]
        rows = (
            ("tools/thing.py", "tools/thing.py"),
            ("tools/thing.py", "README.md"),
            ("./tools/thing.py", "tools/thing.py"),
            ("tools/", "tools/nested/deep.py"),
            ("tools", "toolsmith.py"),
            ("tools/*.py", "tools/thing.py"),
            ("/", "README.md"),
            (".", "README.md"),
            ("", "README.md"),
            ("/abs/tools/thing.py", "tools/thing.py"),
            ({"path": "tools/thing.py"}, "README.md"),
            (["tools/thing.py"], "README.md"),
            (0, "README.md"),
            (None, "README.md"),
        )
        for claim, staged in rows:
            with self.subTest(claim=claim, staged=staged):
                self.assertEqual(bool(claims(claim, staged)),
                                 bool(gate._window_claims(claim, staged)))

    def test_the_matchers_are_not_agreeing_by_both_saying_yes(self) -> None:
        """The control on the test above: two matchers that returned True for everything would
        agree perfectly and guard nothing."""
        gate = _skill_module("gate")
        claims = _guard_module()["claims"]
        for matcher in (claims, gate._window_claims):
            self.assertFalse(matcher("tools/thing.py", "README.md"))
            self.assertTrue(matcher("tools/thing.py", "tools/thing.py"))


if __name__ == "__main__":
    unittest.main()
