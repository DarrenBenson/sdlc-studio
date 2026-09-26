"""US0940: every criterion on a Done story passes when the release gate runs it, or is retired.

`gate.py --release` read 27 criteria red on stories already at Done at 013a46d0: 19 carried in the
v5.1 baseline under D0186 and 8 new since. Each is repaired where its behaviour still ships and
retired in the D0259 pattern where the behaviour was removed on purpose, so v6 ships with no
ruling that tolerates red evidence. One of them also wrote into the tree the gate was judging.

This module runs ONLY the named criteria, through the same `verify_ac.verify_story` call and the
same per-verifier ceiling the release gate's verify lane uses. It never runs the corpus lane: a
criterion that runs every criterion would recurse, and would take the 25 minutes the lane does.

Run from the repo root:
    python3 -m unittest discover -s tools/tests -p test_lean_release_verify.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
STORIES = REPO / "sdlc-studio" / "stories"
BASELINE = REPO / "tools" / "verify-corpus-baseline.txt"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
import gate  # noqa: E402
import gitutil  # noqa: E402
import verify_ac  # noqa: E402
from lib import sdlc_md  # noqa: E402

try:
    import pytest
    #: Executing the named criteria costs minutes (215 s measured under a loaded machine), so a
    #: commit's selected run defers it and the push's full suite runs it, the same trade `test_gate.py` makes for its real-gate tests.
    boundary = pytest.mark.boundary_only
except ImportError:     # the unittest runner deselects nothing, so there is no marker to set
    def boundary(test):
        return test

#: The criteria `gate.py --release` read red on stories claiming completion: 27 at 013a46d0,
#: and four more once the review-ledger and sign-off deletions landed.
MEASURED_RED = (
    "US0021::AC1", "US0040::AC3", "US0042::AC2", "US0047::AC1", "US0052::AC4", "US0063::AC1",
    "US0063::AC2", "US0070::AC1", "US0070::AC2", "US0080::AC2", "US0165::AC2", "US0202::AC3",
    "US0207::AC3", "US0268::AC1", "US0284::AC4", "US0289::AC2", "US0347::AC1", "US0512::AC4",
    "US0666::AC1", "US0162::AC1", "US0178::AC3", "US0211::AC3", "US0224::AC1", "US0224::AC2",
    "US0251::AC2", "US0268::AC3", "US0854::AC1",
    # Red on main after US0918 and US0919 landed, measured by the same lane on 5f4b7cad.
    "US0194::AC1", "US0248::AC1", "US0248::AC2", "US0941::AC5",
)

#: The D0259 retirement: the criterion says who retired it and why, and its stamp says what
#: superseded it. A bare `manual` would be a declared judgement nobody can audit.
RETIRED_VERIFY = re.compile(r"^manual - retired by (?:US|BG|CR)\d{4}: \S")
#: The one other declared shape: a criterion whose executable check waits on an OPEN bug that
#: restores it. It carries no stamp, because nothing has verified it; the bug is its owner.
DEFERRED_VERIFY = re.compile(r"^manual - deferred to (BG\d{4}): \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by \S")

#: A Verify line that hands a shipped script a writing flag. `.py` then any arguments up to the
#: end of that command, so `a.py --check | b.py` is not read as `b`'s flag belonging to `a`.
WRITES = re.compile(r"\.py\b[^|;&]*?\s--(?:write|apply)\b")

#: US0251 AC2: the committed command audit matches a fresh run. The one writer found at 013a46d0.
AUDIT_CRITERION = ("US0251", "AC2")
AUDIT_REPORT = Path("sdlc-studio") / "reviews" / "command-audit.md"


def _story(root: Path, sid: str) -> Path:
    return _unit(root, sid)


def _unit(root: Path, uid: str) -> Path:
    folder = "bugs" if uid.startswith("BG") else "stories"
    [path] = sorted((root / "sdlc-studio" / folder).glob(f"{uid}-*.md"))
    return path


def _scoped_copy(path: Path, keep: set[str], into: Path) -> Path:
    """A copy of the story whose OTHER criteria carry no Verify line, so `verify_story` executes
    only `keep` and reads the rest as unspecified. The file is the one the gate reads; nothing
    about the kept criteria changes, including the `Verified:` line the gate also judges."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    starts = sorted((b.heading_line, b.ac_id) for b in verify_ac.criteria_blocks(text))
    drop = set()
    for i, line in enumerate(lines):
        owner = next((ac for start, ac in reversed(starts) if start <= i), None)
        if owner is not None and owner not in keep and verify_ac.VERIFY_RE.match(line):
            drop.add(i)
    out = into / path.name
    out.write_text("\n".join(ln for i, ln in enumerate(lines) if i not in drop), encoding="utf-8")
    return out


def _run(path: Path, acs: set[str], root: Path, scratch: Path) -> verify_ac.StoryReport:
    """The release gate's own call on the named criteria: dry-run, its per-verifier ceiling."""
    return verify_ac.verify_story(_scoped_copy(path, acs, scratch), dry_run=True,
                                  timeout=gate._verify_timeout(), repo_root=root)


def _baseline_ids(metric: str) -> set[str]:
    for line in BASELINE.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{metric}|"):
            return set(line.split("|")[3].split())
    raise AssertionError(f"{BASELINE.name} carries no {metric} row")


class ReleaseVerifyTests(unittest.TestCase):
    @boundary
    def test_the_measured_red_criteria_pass_or_are_retired(self) -> None:
        by_story: dict[str, set[str]] = {}
        for ident in MEASURED_RED:
            sid, ac = ident.split("::")
            by_story.setdefault(sid, set()).add(ac)
        executable: dict[str, set[str]] = {}
        for sid, acs in sorted(by_story.items()):
            path = _story(REPO, sid)
            self.assertTrue(gate._claims_completion(gate._story_status(path)),
                            f"{sid} no longer claims completion, so it left the measured set")
            text = path.read_text(encoding="utf-8")
            lines = text.split("\n")
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(text)}
            for ac in sorted(acs):
                block = blocks.get(ac)
                self.assertIsNotNone(block, f"{sid}::{ac} no longer parses as a criterion")
                deferred = DEFERRED_VERIFY.match(block.verifier or "")
                if deferred:
                    with self.subTest(criterion=f"{sid}::{ac}", kind="deferred"):
                        self.assertIsNone(block.verified_line,
                                          "a deferred criterion is stamped though nothing ran it")
                        bug = _unit(REPO, deferred.group(1))
                        self.assertFalse(sdlc_md.is_terminal_status(
                            "bug", sdlc_md.extract_field(bug.read_text("utf-8"), "Status") or ""),
                            f"{deferred.group(1)} is closed, so the check it owed is back")
                elif block.verifier and verify_ac._is_manual(block.verifier):
                    with self.subTest(criterion=f"{sid}::{ac}", kind="retired"):
                        self.assertRegex(block.verifier, RETIRED_VERIFY,
                                         "a manual line that does not say who retired it and why")
                        self.assertEqual(block.extra_verifiers, [])
                        self.assertIsNotNone(block.verified_line, "a retirement with no stamp")
                        self.assertRegex(lines[block.verified_line], RETIRED_STAMP,
                                         "the stamp does not name what superseded it")
                else:
                    executable.setdefault(sid, set()).add(ac)
        with tempfile.TemporaryDirectory() as scratch:
            for sid, acs in sorted(executable.items()):
                report = _run(_story(REPO, sid), acs, REPO, Path(scratch))
                for ac in sorted(acs):
                    with self.subTest(criterion=f"{sid}::{ac}", kind="executed"):
                        failure = next((f for f in report.failures if f["ac"] == ac), None)
                        self.assertIsNone(failure, f"red when the release gate runs it: {failure}")
                        self.assertIn(ac, report.passed, "not executed, so not evidence")
        still_tolerated = sorted(set(MEASURED_RED) & _baseline_ids("red-criteria"))
        self.assertEqual(still_tolerated, [],
                         f"{BASELINE.name} still tolerates criteria this unit answered")

    def test_no_verify_line_writes_a_tracked_file(self) -> None:
        writers = []
        for path in sorted(STORIES.glob("US*.md")):
            if not gate._claims_completion(gate._story_status(path)):
                continue
            for block in verify_ac.criteria_blocks(path.read_text(encoding="utf-8")):
                writers += [f"{path.stem[:6]}::{block.ac_id}: {v}" for v in block.verifiers
                            if WRITES.search(v)]
        self.assertEqual(writers, [], "a Verify line on a Done story hands a shipped script a "
                                      "writing flag, so the release gate changes the tree it "
                                      "judges and record-green stamps a tree that differs from "
                                      "the commit")
        with tempfile.TemporaryDirectory() as d:
            clone, scratch = Path(d) / "clone", Path(d) / "scratch"
            scratch.mkdir()
            env = self._clean_clone(clone)
            sid, ac = AUDIT_CRITERION
            with mock.patch.dict(os.environ, env, clear=True):
                green = _run(_story(clone, sid), {ac}, clone, scratch)
                self.assertIn(ac, green.passed, f"the committed audit is stale: {green.failures}")
                self.assertEqual(self._porcelain(clone, env), "")
                # The control: a stale report must read RED and still leave the tree alone. A
                # line that rewrites the report before comparing reads green here, or dirties it.
                report = clone / AUDIT_REPORT
                report.write_text(report.read_text(encoding="utf-8") + "\nstale\n",
                                  encoding="utf-8")
                self._git(clone, env, "commit", "-qam", "stale the audit")
                red = _run(_story(clone, sid), {ac}, clone, scratch)
                self.assertIn(ac, [f["ac"] for f in red.failures],
                              "a stale committed audit read green")
                self.assertEqual(self._porcelain(clone, env), "",
                                 "the criterion wrote into the tree it was judging")

    @staticmethod
    def _git(root: Path, env: dict, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, text=True,
                              check=True, timeout=120).stdout

    def _clean_clone(self, clone: Path) -> dict:
        """This tree's tracked files as a fresh one-commit repository: a clean clone of the
        commit under test, including a change that is staged but not yet committed."""
        listing = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True,
                                 text=True, check=True, timeout=60).stdout
        for rel in filter(None, listing.split("\0")):
            src = REPO / rel
            if src.is_file():
                (clone / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, clone / rel)
        env = gitutil.git_env(PYTHONDONTWRITEBYTECODE="1")
        self._git(clone, env, "init", "-q")
        self._git(clone, env, "add", "-A")
        self._git(clone, env, "commit", "-qm", "clean clone")
        return env

    def _porcelain(self, root: Path, env: dict) -> str:
        return self._git(root, env, "status", "--porcelain")


if __name__ == "__main__":
    unittest.main()
