"""Unit tests for transition.py - status transition + index/epic cascade (CR0042).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import contextlib
import re
import io
import tempfile
import unittest
import unittest.mock  # a SUBMODULE: bare `import unittest` does not bind it, and only
# pytest imports it for you - the module-alone lane runs this file under the unittest runner
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


SCRIPT = DIR / "transition.py"


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

# The repository this test file itself lives in. `parents[5]` walks
# tests/ -> scripts/ -> sdlc-studio/ -> skills/ -> .claude/ -> the checkout root, and it is
# taken from `__file__` rather than from `cwd`, so it names the same tree whichever directory
# the suite is discovered from.
REPO_ROOT = Path(__file__).resolve().parents[5]


def _refuse_working_tree(root) -> Path:
    """Refuse a fixture root that is somebody's checkout. Returns the resolved root.

    BG0573. The guard this replaces asked `str(root).startswith(tempfile.gettempdir())`, which
    answers "is this path under /tmp" - a question about WHERE the tree lives, not about WHAT
    it is. Every reviewer in this repository's process works in a copy under /tmp, so for the
    whole population most likely to hit it the refusal could not fire, and a fixture handed the
    repository root built its workspace there instead: an emptied `.gitignore`, a fake
    `BG0001-x.md`, `src/thing.py`, a clobbered `sdlc-studio/.local/`, and `git add -A` over the
    lot.

    The discriminating facts do not mention location. A directory holding `.git` is a checkout.
    This file's own repository root is known without asking the filesystem. Either one refuses
    whether the tree sits under /tmp, under $HOME, or anywhere else.
    """
    root = Path(root).resolve()
    # FOUR relations, not two. The first repair asked only whether the root IS the repository or
    # CONTAINS it, and an independent pass measured what that leaves open: a directory INSIDE the
    # checkout is none of those, so `_repo(".")` from the scripts directory - the exact relative
    # placeholder BG0536 was filed for - built 444 paths there, including a nested `.git` and a
    # `.gitignore` truncated to nothing. The shipped guard it replaced refused every path outside
    # the temp directory, which covered that case for the wrong reason; narrowing to the right
    # question without the containment arm made the guard SHARPER and the tree less safe.
    inside = REPO_ROOT == root or REPO_ROOT in root.parents
    if (root / ".git").exists() or root == REPO_ROOT or root in REPO_ROOT.parents or inside:
        raise AssertionError(
            f"fixture root {root} is a working tree - a test fixture must never be able to "
            f"write into the working tree")
    return root


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


def _bug_repo(root: Path, status: str = "In Progress") -> Path:
    bd = root / "sdlc-studio" / "bugs"
    bd.mkdir(parents=True)
    header = f"# BG0001: b\n\n> **Status:** {status}\n> **Severity:** medium\n"
    # A criterion, because BG0378 made the criteria floor fire at the VERB: a bug reaching a
    # delivered-terminal status with nothing stating what fixed looks like is refused.
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


class BatchIdsTests(unittest.TestCase):
    """CR0143: --ids batches same-target transitions; each id individually gated,
    one refusal never aborts the rest."""

    def _two_bugs(self, root: Path):
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n"
            "- [x] the unit behaves\n", encoding="utf-8")
        # nothing speaks for BG0002's fix (an unticked criterion, no `Verify:`), so it is refused
        (bd / "BG0002-y.md").write_text(
            "# BG0002: b\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n"
            "- [ ] the unit behaves\n", encoding="utf-8")
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

    def test_v3_finding_refusal_names_the_criteria_floor_and_triage_together(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [ ] the unit behaves\n",
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            msg = str(ctx.exception)
            self.assertIn("unticked", msg)
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
    stating that an honest preflight surfaces the refusal a real run would hit; the other bug
    and story close gates simply did not follow it.
    """

    def _bug_nothing_speaks_for(self, root: Path) -> None:
        """A bug whose one criterion is unticked and carries no `Verify:`, so the criteria
        floor refuses Fixed."""
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        (d / "BG0001-x.md").write_text(
            "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n> **Points:** 2\n\n"
            "## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [ ] the unit behaves\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")

    def test_a_dry_run_reports_the_refusal_the_real_run_gives(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_nothing_speaks_for(root)
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            self.assertIn("unticked", str(ctx.exception))

    def test_the_dry_run_and_the_real_run_agree(self) -> None:
        # The two paths must differ only in whether the write happens.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_nothing_speaks_for(root)
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
            self._bug_nothing_speaks_for(root)
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
            self._bug_nothing_speaks_for(root)
            p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "- [ ] the unit behaves", "- [x] the unit behaves"), encoding="utf-8")
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

    def test_force_still_waives_the_gate_on_a_dry_run(self) -> None:
        # `--force` is a legitimate override, so a forced dry-run must report what a forced
        # real run would do - not refuse. Dropping `not dry_run` without keeping `not force`
        # would break this.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_nothing_speaks_for(root)
            res = _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True, force=True)
            self.assertEqual(res["to"], "Fixed")


class RequirementsPreflightTests(unittest.TestCase):
    """US0267: ask what a transition needs BEFORE doing the work."""

    def _bug(self, root: Path, ticked: bool = False) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        box = "x" if ticked else " "
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** Open\n"
                     "> **Severity:** Low\n> **Points:** 2\n\n## Summary\n\ns\n\n\n"
                     f"## Acceptance Criteria\n\n- [{box}] the unit behaves\n",
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
            self.assertIn("unticked", unmet[0])

    def test_a_satisfied_transition_reports_nothing_unmet(self) -> None:
        # The negative branch: a command that always found a requirement would be useless
        # and would still pass the assertion above.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, ticked=True)
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
        original = tr._bug_verify_gate
        try:
            tr._bug_verify_gate = lambda root, path, target: sentinel
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._bug(root, ticked=True)
                unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertTrue(any(sentinel in u for u in unmet),
                            "the reporter restates requirements instead of deriving them")
        finally:
            tr._bug_verify_gate = original

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

    def _tier_and_breakdown_gates(self, root: Path) -> None:
        """An epic whose `Done` trips the TIER gate and the BREAKDOWN gate.

        Only the FIRST is suffix-free: `_tier_gate` never appends `". Override with --force"`
        (not forceable - the sanctioned route adds the sections), while `_epic_breakdown_gate`'s
        own returned string ends with it. That is deliberate, not a compromise: the plan-review
        and test-plan gates, both suffix-free on a story, are deleted, and every other gate in
        the ladder either shares the tier gate's type (story/epic, and none of its
        siblings there is suffix-free) or shares the suffix-free gates' OWN type (rfc; bug/cr/rfc
        for triage) with no overlap onto story/epic, so no two genuinely suffix-free gates can
        ever co-fire on one artifact - checked against the whole ladder in `_pre_write_gates`,
        not assumed. An ALTERNATING pair (one bare, one suffixed) is thus the fixture this
        class can build, and it is exactly the shape the old prose-splitting bug mishandled:
        splitting on the suffix alone leaves the bare gate's text merged into its neighbour's,
        collapsing two reasons into one. Every earlier attempt at this test used a fixture that
        did not force that split point, so it stayed green on the defect.
        """
        (root / "sdlc-studio").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir()
        # `Template: full` on the epic with none of the sections the full tier promises -> tier
        # gate. Its breakdown names a story still Ready -> breakdown gate.
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Ready\n"
            "> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        ed = root / "sdlc-studio" / "epics"
        ed.mkdir()
        (ed / "EP0001-e.md").write_text(
            "# EP0001: e\n\n> **Status:** In Progress\n> **Template:** full\n\n"
            "## Story Breakdown\n\n- [ ] [US0001: s](../stories/US0001-x.md)\n\n\n"
            "## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")

    def test_tier_and_breakdown_gates_are_two_requirements_not_one(self) -> None:
        """THE case the re-parsing collapsed - driven through the real ladder.

        The previous version of this test constructed a `GateRefusal` by hand and asserted
        `__init__` stored its argument. No gate ran, `requirements()` was never called, and
        the defective code it claimed to catch was never executed - so re-introducing the
        merge left the whole suite green. A test that names a defect it cannot reach is worse
        than no test: it reads as coverage.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tier_and_breakdown_gates(root)
            unmet = _quiet(tr.requirements, root, "EP0001", "Done")
        self.assertEqual(len(unmet), 2, f"two gates collapsed into {len(unmet)}: {unmet}")
        joined = " ".join(unmet)
        self.assertIn("full", joined)          # the tier gate's reason
        self.assertIn("breakdown", joined)     # the breakdown gate's reason
        for item in unmet:
            self.assertNotIn("; AND ", item)

    def test_the_refusal_carries_its_blocks_as_data(self) -> None:
        # The mechanism, exercised through the real ladder rather than a hand-built object:
        # `blocks` must match what the message claims, so the two can never disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tier_and_breakdown_gates(root)
            try:
                _quiet(tr.transition, root, "EP0001", "Done", dry_run=True)
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
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [ ] the unit behaves\n",
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
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n\n\n## Acceptance Criteria\n\n- [ ] the unit behaves\n",
                encoding="utf-8")
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertGreaterEqual(len(unmet), 2, f"expected several requirements, got {unmet}")
            joined = " ".join(unmet)
            self.assertIn("unticked", joined)
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
    """CR0213: the bug close (record verdict, gated set) is one call - and every predictable
    refusal happens BEFORE any write."""

    def _bug(self, root: Path) -> Path:
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n- [x] the unit behaves\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n", encoding="utf-8")
        return root

    def test_one_call_records_and_transitions(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            with redirect_stdout(io.StringIO()):
                rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                              "--verdict", "approve", "--reviewer", "Blake", "--author", "Alex",
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Fixed", text)
            log = (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").read_text(encoding="utf-8")
            self.assertIn("BG0001", log)
            self.assertIn("Blake", log)

    def test_self_review_refused_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed", "--verdict", "approve",
                          "--reviewer", "Alex", "--author", "Alex", "--root", str(root)])
            self.assertEqual(rc, 2)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** In Progress", text)           # no transition
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_reviewer_without_author_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                          "--verdict", "approve", "--reviewer", "Blake", "--root", str(root)])
            self.assertEqual(rc, 2)


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
    """BG0315: `cmd_set`'s one-call close leaves nothing written when the gate ladder refuses,
    and its `--dry-run` writes nothing."""

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
        # The AC-verify gate refuses this close, but the critic verdict was already on disk by
        # the time it ran - a persistent record of a close that never happened.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._story(root)
            before = p.read_text(encoding="utf-8")
            rc_val = _quiet(tr.main, ["set", "US0001", "Done",
                                      "--verdict", "approve", "--reviewer", "Blake",
                                      "--author", "Alex", "--root", str(root)])
            self.assertNotEqual(rc_val, 0)
            self.assertEqual(before, p.read_text(encoding="utf-8"))   # byte-identical
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_the_dry_run_still_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            _quiet(tr.main, ["set", "BG0001", "Fixed", "--dry-run", "--root", str(root)])
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

    def _reopened(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _bug_repo(root)
        p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        p.write_text(p.read_text(encoding="utf-8").replace(
            "> **Status:** In Progress", "> **Status:** Fixed"), encoding="utf-8")
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True, exist_ok=True)
        (local / "verify-report.json").write_text(json.dumps(
            {"stories": {"BG0001-x": {"verified": 3, "failed": 0, "stale": 0}}}), encoding="utf-8")
        return root, p, local / "verify-report.json"

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

    def _green_at(self, status: str) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        _bug_repo(root, status)
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        (local / "verify-report.json").write_text(json.dumps(
            {"stories": {"BG0001-x": {"verified": 3, "failed": 0, "stale": 0}}}), encoding="utf-8")
        return root

    def _still_green(self, root: Path) -> bool:
        report = root / "sdlc-studio" / ".local" / "verify-report.json"
        entry = json.loads(report.read_text(encoding="utf-8"))["stories"]["BG0001-x"]
        return entry["verified"] == 3 and not entry.get("stale")

    def test_moving_between_two_non_terminal_statuses_retracts_nothing(self) -> None:
        """The predicate is LEAVING a terminal status, not ARRIVING at a non-terminal one.
        Caught by mutation: the sibling negative control moved to Fixed, which is terminal, so
        a predicate reading only the target passed it. Reading only the target would wipe the
        evidence on every ordinary move through a working status."""
        root = self._green_at("In Progress")
        transition.transition(root, "BG0001", "Open")     # non-terminal -> non-terminal
        self.assertTrue(self._still_green(root),
                        "a move between two open statuses invalidated a live green")

    def test_an_ordinary_forward_transition_retracts_nothing(self) -> None:
        """In Progress -> Fixed is not a reopen. The guard must fire on leaving a terminal
        status, not on touching a unit that has evidence."""
        root = self._green_at("In Progress")
        transition.transition(root, "BG0001", "Fixed")
        self.assertTrue(self._still_green(root), "a forward transition invalidated a live green")


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


class EpicBreakdownGateTests(unittest.TestCase):
    """BG0568: an epic's completion is derived from its breakdown, and something must CHECK it.

    The test-plan gate (since deleted) was accidentally standing in for this and could not be
    forced, so every epic `refine` minted was permanently un-closable. These drive `transition.py set` through the
    shipped CLI - the defect lives in which gate fires on which entry, and no in-process call to
    a single gate can see that.
    """

    _CFG = "schema_version: 3\n"

    def _proj(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "epics").mkdir(parents=True)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(self._CFG, encoding="utf-8")
        return root

    def _story(self, root, sid, status, *, created="2026-08-10"):
        (root / "sdlc-studio" / "stories" / f"{sid}-x.md").write_text(
            f"# {sid}: s\n\n> **Status:** {status}\n> **Epic:** EP0001\n"
            f"> **Created:** {created}\n\n## Acceptance Criteria\n\n### AC1: a\n\n"
            f"- **Given** x\n- **When** y\n- **Then** z\n- **Verify:** shell true\n",
            encoding="utf-8")

    def _epic(self, root, rows, *, status="Draft", created="2026-08-10", plan=""):
        body = "\n".join(f"- [ ] [{r}: t](../stories/{r}-x.md)" for r in rows)
        (root / "sdlc-studio" / "epics" / "EP0001-e.md").write_text(
            f"# EP0001: e\n\n> **Status:** {status}\n> **Created:** {created}\n\n"
            f"## Story Breakdown\n\n{body}\n{plan}\n## Acceptance Criteria\n\n"
            f"- [x] the unit behaves\n\n## Revision History\n\n"
            f"| Date | Author | Change |\n| --- | --- | --- |\n"
            f"| 2026-08-10 | fixture | Created |\n", encoding="utf-8")

    def _run(self, root, *args):
        import subprocess  # noqa: PLC0415
        scripts = Path(__file__).resolve().parents[1]
        return subprocess.run(
            [sys.executable, str(scripts / "transition.py"), "--root", str(root), *args],
            capture_output=True, text=True, timeout=300, check=False)

    def test_an_epic_with_a_terminal_breakdown_closes(self) -> None:
        # AC1. The epic carries no `## Test Plan`, and nothing may ask it for one.
        with tempfile.TemporaryDirectory() as d:
            root = self._proj(d)
            self._story(root, "US0001", "Done")
            self._epic(root, ["US0001"])
            self.assertNotIn("## Test Plan",
                             (root / "sdlc-studio" / "epics" / "EP0001-e.md").read_text())
            r = self._run(root, "set", "--id", "EP0001", "--status", "Done")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_an_epic_over_unfinished_work_is_refused_from_every_entry(self) -> None:
        # AC2. BOTH entries. The gate this replaces is entry-triggered, and `In Progress` is in an
        # epic's own vocabulary - a seat measured `In Progress -> Done` closing at exit 0 over a
        # Draft child under the first implementation, so the Draft-only half would have passed
        # while the ordinary route stayed open.
        for from_status in ("Draft", "In Progress"):
            with self.subTest(from_status=from_status), tempfile.TemporaryDirectory() as d:
                root = self._proj(d)
                self._story(root, "US0001", "Draft")
                self._epic(root, ["US0001"], status=from_status)
                r = self._run(root, "set", "--id", "EP0001", "--status", "Done")
                out = r.stdout + r.stderr
                self.assertNotEqual(0, r.returncode, out)
                self.assertIn("US0001", out, "the refusal does not name the unfinished unit")

    def test_the_epic_gate_mirrors_the_drift_detectors_silences(self) -> None:
        # AC3. Two silences mirrored, one deliberately inverted.
        with tempfile.TemporaryDirectory() as d:          # empty breakdown -> closes
            root = self._proj(d)
            self._epic(root, [])
            self.assertEqual(0, self._run(root, "set", "--id", "EP0001",
                                          "--status", "Done").returncode)
        with tempfile.TemporaryDirectory() as d:          # Deferred child -> closes
            root = self._proj(d)
            self._story(root, "US0001", "Deferred")
            self._epic(root, ["US0001"])
            r = self._run(root, "set", "--id", "EP0001", "--status", "Done")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        with tempfile.TemporaryDirectory() as d:          # unresolvable id -> REFUSES
            root = self._proj(d)
            self._epic(root, ["US0009"])                  # no backing file
            r = self._run(root, "set", "--id", "EP0001", "--status", "Done")
            self.assertNotEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("US0009", r.stdout + r.stderr)

    def test_the_gate_and_the_drift_detector_read_one_breakdown(self) -> None:
        # AC5, as a CLI OUTCOME rather than a claim about which function is called. The declared
        # table is wholly terminal; an extra child exists by BACK-LINK only. `children_of` would
        # see it and refuse; `declared_breakdown_ids` - what the drift detector reads - does not.
        with tempfile.TemporaryDirectory() as d:
            root = self._proj(d)
            self._story(root, "US0001", "Done")
            self._story(root, "US0002", "Draft")          # back-links to EP0001, not in the table
            self._epic(root, ["US0001"])
            r = self._run(root, "set", "--id", "EP0001", "--status", "Done")
            self.assertEqual(0, r.returncode,
                             "the gate followed the back-links rather than the declared table, "
                             "so it and the drift detector disagree about the same epic:\n"
                             + r.stdout + r.stderr)

    def test_a_forced_epic_close_succeeds_and_is_recorded(self) -> None:
        # AC6. Without this the defect returns in a brand-new gate: the one gate with no override.
        with tempfile.TemporaryDirectory() as d:
            root = self._proj(d)
            self._story(root, "US0001", "Draft")
            self._epic(root, ["US0001"])
            r = self._run(root, "set", "--id", "EP0001", "--status", "Done", "--force")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            body = (root / "sdlc-studio" / "epics" / "EP0001-e.md").read_text(encoding="utf-8")
            # On the Forced-override LINE, not anywhere in the body. The fixture's Story Breakdown
            # already contains `US0001` before the transition, so a whole-body `assertIn` cannot
            # fail - a seat proved it vacuous by replacing the summary with a constant and
            # watching this test stay green.
            forced = [ln for ln in body.splitlines() if "Forced-override" in ln]
            self.assertTrue(forced,
                            "the bypass was not recorded, so a forced close is invisible")
            self.assertIn("US0001", forced[0],
                          "the Forced-override line does not name what was waived")
            # ...and the Revision History row, the criterion's third conjunct, asserted rather
            # than assumed. It was unassertable before: the fixture carried no such section, and
            # `append_revision_row` is a no-op without one.
            rows = [ln for ln in body.splitlines()
                    if ln.startswith("| 2026-") and "Created" not in ln]
            self.assertTrue(rows, "no Revision History row records the forced transition")
            self.assertRegex(rows[-1], r"(?i)forc",
                             f"the Revision History row does not say the gate was forced: "
                             f"{rows[-1]}")


def _guarded_fixture(d) -> Path:
    """Build a small workspace UNDER `d`, and refuse to build it anywhere else.

    A placeholder call once passed `"."` to a fixture like this one and wrote `src/thing.py`, a
    fake `sdlc-studio/bugs/BG0001-x.md` and a mutation ledger into the REAL repository on every
    run. A fixture that can address the working tree will eventually write to it, so this refuses
    rather than trusting every caller to pass a temp path (BG0536, BG0573).
    """
    root = _refuse_working_tree(d)
    (root / "sdlc-studio" / "bugs").mkdir(parents=True, exist_ok=True)
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "thing.py").write_text("def g(a, b):\n    return a == b\n",
                                           encoding="utf-8")
    (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
        "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        "> **Affects:** src/thing.py\n> **Points:** 3\n", encoding="utf-8")
    return root


class FixtureRootGuardTests(unittest.TestCase):
    """BG0536: a fixture helper that takes its root as a parameter will eventually be given the
    wrong one, and writing to a real path looks exactly like writing to a temp path until you
    check what changed.

    A placeholder call passed `"."` and wrote `src/thing.py`, a fake bug and - worst -
    `sdlc-studio/.local/mutation-runs.json` into the REAL repository on every run, destroying 23
    mutation registrations that `.local/` being gitignored made unrecoverable. The guard that
    stops it has been in the tree since; nothing failed if it was removed, which is the
    difference between a guard and a comment.

    BG0573: and then the test written to pin that guard became the instance. It handed the REAL
    repository root to the fixture and relied on the guard to refuse it, so the moment the guard
    stopped refusing - which it does for any checkout under /tmp, where every reviewer works -
    the test itself built the greenfield workspace over the checkout. A test must not need the
    thing under test to be correct in order to be safe to run, so the destructive root is now a
    fake checkout under `tempfile` and the real repository is pinned through the predicate,
    which writes nothing.
    """

    def _fake_checkout(self, d: str) -> Path:
        """A directory that IS a checkout by the only fact that matters: it holds `.git`.

        Under `tempfile`, resolved absolutely, and named from `d` rather than from `cwd` - so
        if the guard ever stops refusing, the blast radius is a temp directory rather than
        somebody's work.
        """
        fake = Path(d).resolve() / "checkout"
        (fake / ".git").mkdir(parents=True)
        return fake

    def test_the_destructive_root_is_disposable_and_independent_of_cwd(self) -> None:
        """The criterion the shipped test could not state about itself: whatever the guard
        does, the root this class hands it must be disposable. The shipped version passed
        `Path(__file__).resolve().parents[5]` - the checkout - and was safe only for as long as
        the guard it was testing stayed correct, which is a test that cannot be run to find out
        whether the guard is correct.

        Mutant: in `_fake_checkout`, return `REPO_ROOT` - the root the shipped test used.
        """
        cwd = os.getcwd()
        seen = []
        try:
            with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
                for where in (Path(d), Path(elsewhere)):
                    os.chdir(where)
                    fake = self._fake_checkout(d)
                    self.assertTrue(fake.is_absolute(), f"{fake} is not an absolute path")
                    self.assertEqual(Path(d).resolve(), fake.parent,
                                     "the root is not under the temporary directory it was given")
                    self.assertNotEqual(REPO_ROOT, fake, "the root IS the repository")
                    self.assertNotIn(REPO_ROOT, [fake, *fake.parents],
                                     "the root is inside the repository")
                    seen.append(fake)
                    shutil.rmtree(fake)
                self.assertEqual(seen[0], seen[1],
                                 "the root moved when the working directory did")
        finally:
            os.chdir(cwd)

    def test_the_fixture_refuses_a_root_that_is_a_checkout(self) -> None:
        """The refusal, exercised where it can do no harm.

        Mutant: restore `if not str(root).startswith(tempfile.gettempdir())`. The fake checkout
        is under /tmp, so the location test passes it and the fixture builds - which is BG0573
        exactly, with a temp directory standing in for the repository.
        """
        with tempfile.TemporaryDirectory() as d:
            fake = self._fake_checkout(d)
            # The WHOLE workspace, not `fake.glob("*")`. The paths this fixture writes are
            # NESTED - `sdlc-studio/bugs/BG0001-x.md`, `sdlc-studio/.local/mutation-runs.json`,
            # `src/thing.py` - so a top-level listing cannot see any of them. The first version
            # of this assertion made exactly that mistake, and a stray `BG0001-x.md` from
            # another fixture was sitting in the tree at the time, invisible to it.
            before = sorted(str(p.relative_to(fake)) for p in fake.rglob("*"))
            with self.assertRaises(AssertionError) as ctx:
                _guarded_fixture(str(fake))
            self.assertIn("working tree", str(ctx.exception).lower(),
                          "the refusal does not say why the root was rejected")
            self.assertEqual(before, sorted(str(p.relative_to(fake)) for p in fake.rglob("*")),
                             "the fixture wrote into the checkout before refusing")

    def test_a_checkout_under_the_temp_directory_is_still_refused(self) -> None:
        """THE CASE THE SHIPPED GUARD COULD NOT SEE. `startswith(tempfile.gettempdir())` is
        satisfied by every rsync copy this repository's own review process makes, so its
        negative case could not be constructed by the population most likely to hit it.

        Mutant: restore the location test. The precondition below asserts the fixture root IS
        under the temp directory, so the restored guard accepts it and no refusal is raised.
        """
        with tempfile.TemporaryDirectory() as d:
            fake = self._fake_checkout(d)
            self.assertTrue(
                str(fake).startswith(tempfile.gettempdir()),
                "this checkout is not under the temp directory, so it is not the case the "
                "location-based guard was blind to")
            with self.assertRaises(AssertionError) as ctx:
                _refuse_working_tree(fake)
            self.assertIn("working tree", str(ctx.exception).lower())

    def test_this_repository_root_is_refused_without_being_written_to(self) -> None:
        """The original claim, kept, but asked of the predicate rather than of the fixture -
        a question costs nothing, whereas building the workspace to find out is the defect.

        Mutant: drop the `root == REPO_ROOT` arm AND the `.git` arm together; either alone
        still refuses a checkout that has both properties.
        """
        repo = Path(__file__).resolve().parents[5]
        with self.assertRaises(AssertionError) as ctx:
            _refuse_working_tree(repo)
        self.assertIn(str(repo), str(ctx.exception),
                      "the refusal does not name the root it rejected")

    def test_a_directory_INSIDE_the_checkout_is_refused(self) -> None:
        """The hole the first repair left, found by an independent pass measuring rather than
        reading.

        `_refuse_working_tree` asked whether the root IS the repository or CONTAINS it, and never
        whether it sits INSIDE it. A subdirectory is neither, so `_repo(".")` called from
        `<repo>/.claude/skills/sdlc-studio/scripts` - the exact relative placeholder BG0536 was
        filed for - built 444 paths there, including a nested `.git` and a `.gitignore` truncated
        to nothing. The guard this replaced refused every path outside the temp directory, which
        covered that case for the wrong reason, so narrowing to the right question without the
        containment arm made the guard sharper and the tree less safe.

        Mutant: drop `REPO_ROOT in root.parents` from the containment test.
        """
        for rel in ("sdlc-studio", ".claude/skills/sdlc-studio/scripts", "tools"):
            with self.subTest(inside=rel):
                with self.assertRaises(AssertionError, msg=f"{rel} was accepted"):
                    _refuse_working_tree(REPO_ROOT / rel)

    def test_a_checkout_with_no_git_directory_is_still_refused(self) -> None:
        """An exported or rsync-ed copy has no `.git`, and `REPO_ROOT` is how it is still
        recognised. Mutant: drop the `root == REPO_ROOT` arm.
        """
        import unittest.mock as mock
        with tempfile.TemporaryDirectory() as d:
            bare = Path(d).resolve() / "export"
            bare.mkdir()
            self.assertFalse((bare / ".git").exists(), "the fixture has a .git after all")
            with mock.patch.object(sys.modules[__name__], "REPO_ROOT", bare):
                with self.assertRaises(AssertionError):
                    _refuse_working_tree(bare)

    def test_the_fixture_still_builds_under_a_temp_directory(self) -> None:
        # The positive control: "refuses the wrong root" is otherwise satisfied by a helper that
        # refuses every root, leaving a fixture nobody can build.
        with tempfile.TemporaryDirectory() as d:
            root = _guarded_fixture(d)
            self.assertTrue((root / "sdlc-studio" / "bugs" / "BG0001-x.md").is_file())


class TheAppetiteBreakerIsPulledOnTheShippedPath(unittest.TestCase):
    """BG0526. `loop_guard budget` was fully wired to its data and had NO caller: every reference
    anywhere was a reference doc telling an agent to run it between units. So the ceiling an
    operator set at plan time held only while the driving agent remembered to pull it - which
    makes a recorded decision a suggestion, and is LL0027 exactly: a gate belongs in the command
    people actually run, not in the step they are told to run.

    A unit reaching a terminal status IS the boundary the breaker was designed for.
    """

    def _ws(self, units: int = 0, minutes: float = 0.0, appetite: bool = True) -> Path:
        d = Path(tempfile.mkdtemp(prefix="appetite_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "sdlc-studio" / "bugs").mkdir(parents=True)
        (d / "sdlc-studio" / ".local").mkdir(parents=True)
        for uid in ("BG9101", "BG9102"):
            (d / "sdlc-studio" / "bugs" / f"{uid}-x.md").write_text(
                f"# {uid}: a fixture bug\n\n> **Status:** Open\n> **Severity:** Medium\n"
                f"> **Points:** 2\n> **Verification depth:** functional\n> **Affects:** f.py\n\n"
                f"## Acceptance Criteria\n\n"
                f"- [x] **AC1** Given a thing, when it happens, then it works.\n"
                f"  - **Verify:** manual a human checks it\n", encoding="utf-8")
        state = {"schema": 1, "run_id": "RUN-TEST", "started_at": "2026-08-14T00:00:00Z",
                 "ended_at": None, "outcome": None, "goal": "x",
                 "batch": ["BG9101", "BG9102"], "plan": {},
                 "appetite": ({"units": units, "minutes": minutes, "standing_units": 64,
                               "standing_minutes": 960.0, "over_appetite": False}
                              if appetite else {})}
        (d / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        return d

    def _set(self, root: Path, uid: str) -> str:
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "set", "--root", str(root),
             "--id", uid, "--status", "Fixed"],
            capture_output=True, text=True, timeout=120)
        return (proc.stdout or "") + (proc.stderr or "")

    def test_a_spent_appetite_is_reported_at_the_unit_boundary(self) -> None:
        """The whole bug: nothing pulled the breaker. MUTANT: delete the `_report_appetite`
        call from `cmd_set` - the ceiling goes back to depending on recall."""
        root = self._ws(units=1)
        self._set(root, "BG9101")
        out = self._set(root, "BG9102")
        self.assertIn("APPETITE SPENT", out, "the breaker was never pulled")
        self.assertIn("units", out)
        self.assertIn("NEXT one", out, "the report does not say what the ceiling actually stops")

    def test_it_reports_and_does_not_refuse(self) -> None:
        """The unit just finished. Blocking its own transition would punish the wrong action and
        leave the record wrong as well - what a boundary check stops is the next unit.
        MUTANT: return non-zero when the appetite is spent."""
        root = self._ws(units=1)
        self._set(root, "BG9101")
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "set", "--root", str(root),
             "--id", "BG9102", "--status", "Fixed"], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode,
                         "a spent appetite refused the transition of a unit already delivered")
        text = (root / "sdlc-studio" / "bugs" / "BG9102-x.md").read_text(encoding="utf-8")
        self.assertIn("**Status:** Fixed", text, "the record was not written")

    def test_it_is_silent_when_there_is_nothing_to_say(self) -> None:
        """THE CONTROL, and the reason this is safe to put on a path run hundreds of times: a
        line printed after every transition is one nobody reads on the day it matters.
        MUTANT: report unconditionally instead of only when exhausted."""
        for label, kw in (("budget remaining", {"units": 8}),
                          ("no appetite declared", {"appetite": False})):
            with self.subTest(label):
                out = self._set(self._ws(**kw), "BG9101")
                self.assertNotIn("APPETITE", out, f"{label}: the breaker spoke with nothing to say")

    def test_an_unreadable_run_never_breaks_a_completed_transition(self) -> None:
        """This is a REPORT beside a transition that already succeeded, so a breaker that cannot
        be evaluated must not turn a good transition into a traceback. Deliberately the opposite
        of the fail-closed rule elsewhere: nothing here gates anything.
        MUTANT: let the exception escape."""
        root = self._ws(units=1)
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text("{ not json",
                                                                       encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "set", "--root", str(root),
             "--id", "BG9101", "--status", "Fixed"], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stderr[-400:])
        self.assertNotIn("Traceback", proc.stderr)


class AnnotateFieldsFileTests(unittest.TestCase):
    """BG0609 - `annotate` had only `--value`, so a backticked value was executed by the shell."""

    def _unit(self, root: Path) -> None:
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / "BG9100-fixture.md").write_text(
            "# BG9100: fixture\n\n> **Status:** Open\n> **Points:** 1\n"
            "> **Affects:** scripts/x.py\n\n## Acceptance Criteria\n\n- [ ] **AC1** a claim\n",
            encoding="utf-8")

    def test_a_value_carrying_backticks_is_stored_verbatim(self) -> None:
        """MUTANT: in `transition._annotate_fields`, ignore `--fields-file` and read the flags.

        Backticks are command substitution inside a shell argument, so on the flag path a value
        quoting a command is RUN and its output is stored in place of the text. A re-triage
        rationale quoting a command was written with the command gone and the two spaces that
        flanked it closed up, and the annotation reported success (BG0609)."""
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            doc = root / "fields.json"
            value = "the brief that `critic.py brief` generates carries the guard"
            doc.write_text(json.dumps({"field": "Note", "value": value}), encoding="utf-8")
            rc = mod.main(["annotate", "--id", "BG9100", "--fields-file", str(doc),
                           "--root", str(root)])
            self.assertEqual(0, rc)
            body = (root / "sdlc-studio" / "bugs" / "BG9100-fixture.md").read_text()
            self.assertIn(value, body,
                          "the stored value is not the text the document carried")

    def test_the_flag_path_still_works(self) -> None:
        """The paired control. The file is the recommended path, not the only one - a change
        that broke `--value` would break every caller in the toolchain."""
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            rc = mod.main(["annotate", "--id", "BG9100", "--field", "Note",
                           "--value", "plain text", "--root", str(root)])
            self.assertEqual(0, rc)
            body = (root / "sdlc-studio" / "bugs" / "BG9100-fixture.md").read_text()
            self.assertIn("plain text", body)

    def test_an_unknown_key_in_the_document_is_refused(self) -> None:
        """MUTANT: in `transition._annotate_fields`, ignore keys the reader does not know.

        A key nobody reads is a field that silently went missing, which is the rule
        `file_finding.py` already states for the same contract."""
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            doc = root / "fields.json"
            doc.write_text(json.dumps({"field": "Note", "value": "x", "reason": "y"}),
                           encoding="utf-8")
            self.assertEqual(2, mod.main(["annotate", "--id", "BG9100", "--fields-file",
                                          str(doc), "--root", str(root)]))

    def test_a_non_string_value_is_refused(self) -> None:
        """MUTANT: in `transition._annotate_fields`, accept any JSON type for `value`.

        BG0610's shape one contract over: a scalar supplied where a string is expected is
        iterated rather than stored, and the artefact is written with the damage invisible."""
        mod = tr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root)
            doc = root / "fields.json"
            doc.write_text(json.dumps({"field": "Note", "value": ["a", "b"]}), encoding="utf-8")
            self.assertEqual(2, mod.main(["annotate", "--id", "BG9100", "--fields-file",
                                          str(doc), "--root", str(root)]))




class MisplacedCriterionGateTests(unittest.TestCase):
    """BG0648: the Done gate refuses a criterion outside `## Acceptance Criteria` by name. The
    runner stopped executing such a block, so without this a story whose stray criterion has a
    RED verifier went Done clean where it used to block on the red. MUTANT: drop the misplaced
    refusal from `_acs_missing_evidence`, so the stray block is simply ignored."""

    def test_a_story_with_a_misplaced_red_criterion_is_refused_by_name(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text("# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
                          "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n\n"
                          "## Notes\n\n### AC2\n- **Verify:** shell false\n\n### AC3\n- **Then** a bare one\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertIn("outside `## Acceptance Criteria`", str(ctx.exception))
            self.assertIn("AC2 under `## Notes`", str(ctx.exception))
            self.assertIn("AC3 under `## Notes`", str(ctx.exception), "a misplaced criterion with no Verify line went unnamed")
            self.assertNotIn("could not run", str(ctx.exception), "a placement defect was told as broken tooling")
            # the control: the same criterion INSIDE the section is refused for its red verifier,
            # never for its placement
            sp.write_text("# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
                          "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n\n"
                          "### AC2\n- **Verify:** shell false\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx2:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertNotIn("outside", str(ctx2.exception))


class CoverageGateTests(unittest.TestCase):
    """US0816: the Fixed and Done gates refuse a unit whose own verifiers never executed a line
    it added, under `review.line_coverage: block`; report and off are the other modes; a ruled
    line is subtracted from uncovered and live at the bytes the gate reads; a ruling on stale
    bytes counts for nothing; the base ref belongs to the run whose batch names the unit, open
    or closed."""

    UNIT = "BG0001"
    PROD = "src/thing.py"
    TEST = "tests/test_thing.py"
    BASE_PROD = "def used():\n    return 1\n"
    BASE_TEST = ("import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))\n"
                 "from src import thing\n\n\nclass TestT:\n    def test_a(self):\n        assert thing.used() == 1\n")

    def _config(self, root: Path, mode, after: str | None = None) -> None:
        lines = ["review:\n"]
        if mode is not None:
            lines.append(f"  line_coverage: {mode}\n")
        if after:
            lines.append(f"  line_coverage_after: \"{after}\"\n")
        (root / "sdlc-studio" / ".config.yaml").write_text("".join(lines), encoding="utf-8")

    def _bug(self, root: Path, created: str | None = "2026-09-08", verifiers=None, affects=None) -> Path:
        p = root / "sdlc-studio" / "bugs" / f"{self.UNIT}-cov.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        vs = verifiers or [f"pytest {self.TEST}::TestT::test_a"]
        acs = "".join(f"- [x] **AC{i}** Given it, when it, then it.\n  - **Verify:** {v}\n" for i, v in enumerate(vs, 1))
        head = f"# {self.UNIT}: coverage gate fixture\n\n> **Status:** Open\n> **Severity:** Medium\n> **Points:** 1\n> **Affects:** {affects or self.PROD}\n"
        if created:
            head += f"> **Created:** {created}\n"
        p.write_text(head + f"> **Verification depth:** functional\n\n## Acceptance Criteria\n\n{acs}\n## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n| 2026-09-08 | t | Filed |\n", encoding="utf-8")
        return p

    def _repo(self, d: Path, *, mode="block", uncovered=True, created="2026-09-08", after=None, batch=None) -> Path:
        root = _refuse_working_tree(d)
        for rel in ("src", "tests", "sdlc-studio/.local"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        (root / "src" / "__init__.py").write_text("", encoding="utf-8")
        (root / self.PROD).write_text(self.BASE_PROD, encoding="utf-8")
        (root / self.TEST).write_text(self.BASE_TEST, encoding="utf-8")
        self._bug(root, created=created)
        self._config(root, mode, after)
        _git_repo(root)
        base = _head(root)
        (root / self.PROD).write_text(self.BASE_PROD + ("\n\ndef added_dead():\n    return 2\n" if uncovered else "\n\ndef added_used():\n    return 3\n"), encoding="utf-8")
        if not uncovered:
            (root / self.TEST).write_text(self.BASE_TEST + "\n    def test_b(self):\n        assert thing.added_used() == 3\n", encoding="utf-8")
            self._bug(root, created=created, verifiers=[f"pytest {self.TEST}::TestT::test_a", f"pytest {self.TEST}::TestT::test_b"])
        _git_commit(root, f"fix({self.UNIT}): the change")
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
            {"run_id": "RUN-TEST01", "outcome": "goal-reached", "ended_at": "2026-09-08T00:00:00Z",
             "batch": batch if batch is not None else [self.UNIT], "base_ref": base}), encoding="utf-8")
        return root

    def _set(self, root: Path, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = transition.main(["set", self.UNIT, "Fixed", "--root", str(root), *extra])
        return rc, out.getvalue(), err.getvalue()

    def _status(self, root: Path) -> str:
        return (root / "sdlc-studio" / "bugs" / f"{self.UNIT}-cov.md").read_text(encoding="utf-8")

    # -- AC1 -------------------------------------------------------------------------
    def test_an_uncovered_added_line_refuses_the_terminal_transition_and_a_covered_unit_passes(self) -> None:
        """MUTANTS: replace the fresh collection with a read of the last report on disk (the
        seeded `uncovered: 0` report passes the uncovered unit); drop the hash comparison on a
        reused report (the stale report is accepted)."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            # a PRIOR report claiming clean coverage, so a build that reads reports passes wrongly
            (root / "sdlc-studio" / ".local" / "verify-report.json").write_text(json.dumps(
                {"stories": {}, "coverage": {f"{self.UNIT}-cov": {"uncovered_total": 0, "affects_hash": "0" * 64, "files": {}}}}), encoding="utf-8")
            rc, out, err = self._set(root); text = out + err
            self.assertNotEqual(rc, 0, text)
            self.assertIn("uncovered added line", text); self.assertIn("src/thing.py: 6", text)
            self.assertIn("verify_ac.py coverage rule", text)
            self.assertIn("> **Status:** Open", self._status(root))
            # a reused report whose Affects hash does not match is refused as STALE
            rc, out, err = self._set(root, "--coverage-report", "sdlc-studio/.local/verify-report.json")
            self.assertNotEqual(rc, 0, out + err); self.assertIn("STALE", out + err)
            # ...and one whose hash matches is REUSED: written by the shipped `run --coverage`
            cp = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "run", "--id", self.UNIT, "--dir", "sdlc-studio/bugs", "--coverage", "--dry-run", "--report", "sdlc-studio/.local/cov.json", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(cp.returncode, 1, cp.stdout + cp.stderr)
            rc, out, err = self._set(root, "--coverage-report", "sdlc-studio/.local/cov.dry-run.json")
            self.assertNotEqual(rc, 0, out + err); self.assertIn("src/thing.py: 6", out + err); self.assertNotIn("STALE", out + err)
            # under report, a stale report is a warning and the transition proceeds
            self._config(root, "report")
            rc, out, err = self._set(root, "--coverage-report", "sdlc-studio/.local/verify-report.json")
            self.assertEqual(rc, 0, out + err); self.assertIn("STALE", out + err)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), uncovered=False)
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("> **Status:** Fixed", self._status(root))

    # -- AC2 -------------------------------------------------------------------------
    def test_a_ruled_line_passes_and_the_ruling_is_in_the_depth_field(self) -> None:
        """MUTANTS: remove the read of the Coverage Rulings table at the gate; drop the
        reason-floor check in `coverage rule`; omit the ruled-line count from the derived half."""
        import verify_ac  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            short = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "too short", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(short.returncode, 2, short.stdout + short.stderr); self.assertIn("floor", short.stderr)
            self.assertNotIn("## Coverage Rulings", self._status(root))
            ok = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "a dormant arm no fixture can reach without faking the OS", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            self.assertIn("## Coverage Rulings", self._status(root))
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("> **Status:** Fixed", self._status(root))
            # the ruling is live at the bytes the gate reads: the reader the gate subtracts with
            live, stale = verify_ac.live_rulings(root, self._status(root))
            self.assertEqual((1, 0), (len(live), len(stale)), (live, stale))
            # The recommended path: the reason read off disk, so a backtick in it is stored,
            # not executed - and a second ruling appends to the table the first one made.
            (root / "ruling.json").write_text(json.dumps({"file": self.PROD, "line": 1, "reason": "a `$(second)` reason long enough to pass the floor"}), encoding="utf-8")
            ff = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--fields-file", str(root / "ruling.json"), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(ff.returncode, 0, ff.stdout + ff.stderr)
            self.assertIn("`$(second)`", self._status(root)); self.assertEqual(self._status(root).count("## Coverage Rulings"), 1)
            missing = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2); self.assertIn("missing line, reason", missing.stderr)
            nobody = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", "BG0999", "--file", self.PROD, "--line", "6", "--reason", "a dormant arm no fixture can reach without faking the OS", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(nobody.returncode, 2); self.assertIn("no artefact with id BG0999", nobody.stderr)
            nofile = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", "src/absent.py", "--line", "6", "--reason", "a dormant arm no fixture can reach without faking the OS", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(nofile.returncode, 2); self.assertIn("not a readable file", nofile.stderr)
            (root / "bad.json").write_text("{not json", encoding="utf-8")
            bad = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--fields-file", str(root / "bad.json"), "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2, bad.stdout + bad.stderr); self.assertIn("coverage rule refused", bad.stderr)

    # -- AC3 -------------------------------------------------------------------------
    def test_a_ruling_on_stale_bytes_does_not_satisfy_the_gate(self) -> None:
        """MUTANT: drop the content-hash comparison so a ruling matches on path and line alone."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            ok = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "a dormant arm no fixture can reach without faking the OS", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            # the file's bytes change after the ruling
            (root / self.PROD).write_text((root / self.PROD).read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            _git_commit(root, f"fix({self.UNIT}): drift")
            rc, out, err = self._set(root)
            # the line it excused is uncovered again, so the unit is refused on that count, and
            # the stale row is named beside it as satisfying nothing
            self.assertNotEqual(rc, 0, out + err); self.assertIn("stale coverage ruling", out + err)
            self.assertIn("1 uncovered added line(s)", out + err)
            self.assertIn("> **Status:** Open", self._status(root))
            # A stale ruling on a line the unit's verifiers NOW execute blocks nothing: the
            # staleness itself is not a defect, and refusing on it told the author to re-assert
            # a waiver the measurement contradicts.
            (root / self.PROD).write_text(self.BASE_PROD + "\n\ndef added_used():\n    return 3\n", encoding="utf-8")
            (root / self.TEST).write_text((root / self.TEST).read_text(encoding="utf-8")
                                          + "\n    def test_b(self):\n        assert thing.added_used() == 3\n", encoding="utf-8")
            self._bug(root, created="2026-09-08", verifiers=[f"pytest {self.TEST}::TestT::test_a", f"pytest {self.TEST}::TestT::test_b"])
            ok2 = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "a dormant arm no fixture can reach without faking the OS", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(ok2.returncode, 0, ok2.stderr)
            (root / self.PROD).write_text(self.BASE_PROD + "\n\ndef added_used():\n    return 3\n\n\n# drift\n", encoding="utf-8")
            _git_commit(root, f"fix({self.UNIT}): every added line reached, the ruling now stale")
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err)
            self.assertIn("stale coverage ruling", out + err)
            self.assertNotIn("uncovered added line(s)", out + err)
            # and the withdrawal takes the row out of every count, on the record
            wd = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "withdraw", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "the arm is reached by a test now, so the waiver asserts nothing", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(wd.returncode, 0, wd.stderr)
            body = self._status(root)
            self.assertIn("withdrawn ", body); self.assertIn("(was: a dormant arm", body)
            # both refusals of the withdrawal: a reason below the floor, and one that names no row
            thin = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "withdraw", "--id", self.UNIT, "--file", self.PROD, "--line", "6", "--reason", "changed", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(thin.returncode, 2, thin.stdout + thin.stderr)
            self.assertIn("below the floor", thin.stderr)
            gone = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "withdraw", "--id", self.UNIT, "--file", self.PROD, "--line", "99", "--reason", "there is no ruling on this line to withdraw at all", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(gone.returncode, 2, gone.stdout + gone.stderr)
            self.assertIn("matches nothing has done nothing", gone.stderr)
            # two rulings sharing one reason, and one carrying a pipe: the withdrawal must take
            # the row NAMED, found by its own file, line and hash, and must read the escaped
            # cell back - a reason-text match took whichever row came first, at exit 0
            import verify_ac  # noqa: PLC0415
            for ln, why in ((4, "one reason, written for every line in a single pass"),
                            (5, "one reason, written for every line in a single pass"),
                            (6, "the arm | the OS decides, and no fixture reaches it")):
                r = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", str(ln), "--reason", why, "--root", str(root)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for ln in (5, 6):
                w = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "withdraw", "--id", self.UNIT, "--file", self.PROD, "--line", str(ln), "--reason", "withdrawn by the probe that proves the row named is the row taken", "--root", str(root)], capture_output=True, text=True)
                self.assertEqual(w.returncode, 0, w.stdout + w.stderr)
            live = {r["line"] for r in verify_ac.coverage_rulings(self._status(root))}
            self.assertNotIn(5, live, "the row NAMED is withdrawn, not whichever shares its reason")
            self.assertNotIn(6, live, "a reason carrying a pipe is withdrawn, never silently left live")
            self.assertIn(4, live, "the row that shares the reason but was not named stays live")
            # a reason OPENING with the withdrawal's own sentinel is refused: written, it would
            # be reported ruled and read by nothing
            sent = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "7", "--reason", "withdrawn from the earlier reading, which no fixture reaches", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(sent.returncode, 2, sent.stdout + sent.stderr)
            self.assertIn("may not begin with `withdrawn`", sent.stderr)
            import verify_ac  # noqa: PLC0415
            self.assertEqual(verify_ac.coverage_rulings(body), [], "a withdrawn row counts for nothing")

    # -- AC4 -------------------------------------------------------------------------
    def test_the_mode_decides_refusal_report_or_silence(self) -> None:
        """MUTANTS: change the report branch to refuse like block; change the else branch to
        treat an unknown value as off; call the collector under off and print nothing."""
        import verify_ac  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode="report")
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("coverage: 1 uncovered added line(s)", out + err)
            self.assertEqual((out + err).count("uncovered added line(s)"), 1, "the report line states the count ONCE: " + out + err)
            # a second ruling on the same live line is refused rather than counted twice
            again = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "4", "--reason", "the first ruling covers this line on these bytes", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(again.returncode, 0, again.stderr)
            dup = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "4", "--reason", "a second row for the same line on the same bytes", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(dup.returncode, 2, dup.stdout + dup.stderr)
            self.assertIn("already carries a live ruling on these bytes", dup.stderr)
            # a reason carrying a `|` or a newline must not write a row the parser cannot read:
            # reported as ruled, counted by nothing, inside a tracked artefact
            import verify_ac  # noqa: PLC0415
            hostile = subprocess.run([sys.executable, str(DIR / "verify_ac.py"), "coverage", "rule", "--id", self.UNIT, "--file", self.PROD, "--line", "5", "--reason", "the arm | the OS decides,\nand no fixture can reach it", "--root", str(root)], capture_output=True, text=True)
            self.assertEqual(hostile.returncode, 0, hostile.stdout + hostile.stderr)
            body = self._status(root)
            ruled = [r for r in verify_ac.coverage_rulings(body) if r["line"] == 5]
            self.assertEqual(len(ruled), 1, "the row a successful ruling writes must be one the parser reads back: " + body)
            self.assertIn("the OS decides, and no fixture", ruled[0]["reason"])
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode="off")     # the bare YAML word, which parses to False
            calls = []
            real = verify_ac.coverage_report
            with unittest.mock.patch.object(verify_ac, "coverage_report", lambda *a, **k: (calls.append(1), real(*a, **k))[1]):
                rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertEqual(calls, [], "off must call no collector")
            self.assertNotIn("coverage:", out + err)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode="blcok")
            rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("not one of report, block, off", out + err)

    # -- AC5 -------------------------------------------------------------------------
    def test_units_created_before_the_cutoff_are_exempt(self) -> None:
        """MUTANTS: remove the cutoff comparison; exempt a unit with no Created field; compare
        with `>` so the on-the-date unit is exempt; compare as a string prefix."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), created="2026-09-01", after="2026-09-07")
            rc, out, err = self._set(root); self.assertEqual(rc, 0, out + err)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), created="2026-09-07", after="2026-09-07")
            rc, out, err = self._set(root); self.assertNotEqual(rc, 0, "a unit created ON the date is judged")
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), created="2026-09-10", after="2026-09-1")
            rc, out, err = self._set(root); self.assertNotEqual(rc, 0, "a prefix is not a date comparison")
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), created=None, after="2026-09-07")
            rc, out, err = self._set(root); self.assertNotEqual(rc, 0, "no Created date is judged, never exempted")
        with tempfile.TemporaryDirectory() as d:
            # an UNPARSEABLE date is judged too: dropping the length check would read `1999` as
            # earlier than the cutoff and exempt it, which is a waiver granted by a typo
            root = self._repo(Path(d), created="1999", after="2026-09-07")
            rc, out, err = self._set(root); self.assertNotEqual(rc, 0, "an unparseable Created date is judged, never exempted: " + out + err)

    # -- AC6 -------------------------------------------------------------------------
    def test_a_missing_coverage_module_never_reads_as_covered(self) -> None:
        """MUTANT: an absent module yields an empty uncovered set."""
        with tempfile.TemporaryDirectory() as d:
            hidden = Path(d) / "python-without-coverage"
            hidden.write_text(f"#!/bin/sh\nexec {sys.executable} -S \"$@\"\n", encoding="utf-8"); hidden.chmod(0o755)
            root = self._repo(Path(d))
            with unittest.mock.patch.dict(os.environ, {"SDLC_COVERAGE_PYTHON": str(hidden)}):
                rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("the coverage module is absent", out + err)
            root2 = self._repo(Path(d) / "two", mode="report")
            with unittest.mock.patch.dict(os.environ, {"SDLC_COVERAGE_PYTHON": str(hidden)}):
                rc, out, err = self._set(root2)
            self.assertEqual(rc, 0, out + err)
            self.assertIn("coverage: not measured - the coverage module is absent (pip install coverage, or review.line_coverage: off)", out + err)
        with tempfile.TemporaryDirectory() as d:
            # the instrument itself unimportable: block refuses naming it, report warns and proceeds
            root = self._repo(Path(d))
            with unittest.mock.patch.dict(sys.modules, {"verify_ac": None}):
                rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("verify_ac could not be imported", out + err)
            root2 = self._repo(Path(d) / "two", mode="report")
            with unittest.mock.patch.dict(sys.modules, {"verify_ac": None}):
                rc, out, err = self._set(root2)
            self.assertEqual(rc, 0, out + err); self.assertIn("verify_ac could not be imported", out + err)

    # -- AC7 -------------------------------------------------------------------------
    def test_the_shipped_default_is_report(self) -> None:
        """MUTANTS: flip the fallback literal for the mode to `block`; flip the template's
        `line_coverage` value to the refusing mode."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode=None)     # never set
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("coverage: 1 uncovered added line(s)", out + err)
        template = (DIR.parent / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        self.assertIn("line_coverage: report", template)
        self.assertIn("OPTIONAL dependency", template); self.assertIn("line_coverage_after", template)

    # -- AC8 -------------------------------------------------------------------------
    def test_no_base_ref_refuses_under_block_and_is_reported_under_report(self) -> None:
        """MUTANTS: read the base ref only while the run is open (every story at the close is
        refused); drop the batch-membership check so a run whose batch does not name the unit is
        read. Driven through `artifact.close`, the seam `sprint close --apply-signoff` reaches."""
        import artifact  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), uncovered=False)      # the run is CLOSED (ended_at set)
            r = artifact.close(root, self.UNIT, "Fixed")
            self.assertEqual(r["to"], "Fixed", r)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), uncovered=False, batch=["BG0099"])   # a run naming another unit
            rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("--base", out + err)
            rc, out, err = self._set(root, "--base", "HEAD~1")
            self.assertEqual(rc, 0, out + err)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode="report", uncovered=False, batch=["BG0099"])
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("coverage: not measured - no base ref", out + err)
        with tempfile.TemporaryDirectory() as d:
            # `--base` given with no run state at all: the silence for a project that never
            # opened a run must not swallow a base the caller HAS given - it is measured.
            root = self._repo(Path(d), mode="report", batch=["BG0099"])
            (root / "sdlc-studio" / ".local" / "run-state.json").unlink()
            rc, out, err = self._set(root, "--base", "HEAD~1")
            self.assertEqual(rc, 0, out + err)
            self.assertIn("uncovered added line(s)", out + err, "an explicit --base is measured even with no run state: " + out + err)
        with tempfile.TemporaryDirectory() as d:
            # the one-call close (a verdict recorded with it) carries the coverage options into
            # its ladder: dropping them refused for want of a base ref the caller gave
            root = self._repo(Path(d), uncovered=False, batch=["BG0099"])
            rc, out, err = self._set(root, "--base", "HEAD~1", "--verdict", "approve",
                                     "--reviewer", "rev", "--author", "dev")
            self.assertEqual(rc, 0, out + err)
            self.assertNotIn("--base <ref>", out + err, "the one-call close was given the same options as the transition: " + out + err)
        with tempfile.TemporaryDirectory() as d:
            # an UNREADABLE run state names no unit: block refuses naming --base rather than
            # crashing or inventing a ref, and --base still answers
            root = self._repo(Path(d), uncovered=False)
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text("{ not json", encoding="utf-8")
            rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("--base", out + err)
        with tempfile.TemporaryDirectory() as d:
            # no run state AT ALL: `report` stays silent - a project that never opened a run is
            # not in a delivery, and a line printed on its every terminal transition is noise
            root = self._repo(Path(d), mode="report", uncovered=False)
            (root / "sdlc-studio" / ".local" / "run-state.json").unlink()
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertNotIn("coverage:", out + err)

    # -- AC9 -------------------------------------------------------------------------
    def test_a_not_measured_python_file_is_refused_under_block(self) -> None:
        """MUTANT: change the not-measured branch to count the file as covered."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._bug(root, verifiers=["shell echo ok"])
            _git_commit(root, f"fix({self.UNIT}): shell verifier only")
            rc, out, err = self._set(root)
            self.assertNotEqual(rc, 0, out + err); self.assertIn("not measured - no traced verifier", out + err)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d), mode="report")
            self._bug(root, verifiers=["shell echo ok"])
            _git_commit(root, f"fix({self.UNIT}): shell verifier only")
            rc, out, err = self._set(root)
            self.assertEqual(rc, 0, out + err); self.assertIn("not measured - no traced verifier", out + err)


class AnnotateSeverityTests(unittest.TestCase):
    """BG0633: `annotate` was a third writer of a Severity line and the only one that never
    checked the vocabulary, so an off-vocabulary value was written verbatim and then read by
    neither the release bar nor the disclosure page - the finding disappearing from both at
    once, which reads exactly like a clean corpus."""

    def _bug(self, root: Path) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Medium\n"
                     "> **Created-by:** sdlc-studio new\n\n## Summary\n\ns\n", encoding="utf-8")
        return p

    def test_an_off_vocabulary_severity_is_refused_through_the_shipped_command(self) -> None:
        """MUTANT: delete the vocabulary call from `annotate` so any value reaches the writer.

        Driven as the shipped command rather than as a call, because without `--id` argparse
        exits 2 and the file is unchanged for a reason that has nothing to do with the
        vocabulary - which is a green test for the wrong reason."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            rc, out = _cli(root, "annotate", "--id", "BG0001",
                           "--field", "Severity", "--value", "major")
            self.assertNotEqual(0, rc, out)
            self.assertIn("Critical, High, Medium, Low", out,
                          "the refusal must name the accepted set, or the author guesses")
            self.assertEqual(before, p.read_text(encoding="utf-8"),
                             "a refused annotate must leave the artefact untouched")

    def test_a_differently_cased_severity_is_normalised(self) -> None:
        """MUTANT: replace the normalisation with an exact-match membership test, so `high`
        is refused rather than written `High`.

        The positive control for the row above: a guard refusing EVERY severity satisfies the
        refusal test on its own. Both readers fold case, and a writer stricter than its own
        readers refuses findings they classify perfectly well."""
        for spelling in ("high", "High"):
            with self.subTest(spelling=spelling), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                p = self._bug(root)
                rc, out = _cli(root, "annotate", "--id", "BG0001",
                               "--field", "Severity", "--value", spelling)
                self.assertEqual(0, rc, out)
                body = p.read_text(encoding="utf-8")
                self.assertIn("> **Severity:** High", body)
                self.assertEqual(1, body.count("Severity:"),
                                 "the canonical line is updated in place, never duplicated")

    def test_the_success_line_reports_what_was_written(self) -> None:
        """MUTANT: print the argv pair again instead of the record `annotate` returns.

        The command canonicalises a vocabulary field's name and value before writing, so the
        text line and the same command's `--format json` were saying different things about
        one write. Nothing in the corpus asserted that line, which is why it went unnoticed."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            rc, out = _cli(root, "annotate", "--id", "BG0001",
                           "--field", "SEVERITY", "--value", "hIgH")
            self.assertEqual(0, rc, out)
            self.assertIn("> **Severity:** High", p.read_text(encoding="utf-8"))
            self.assertIn("Severity = High", out,
                          f"the success line reports the request rather than the write:\n{out}")
            self.assertNotIn("hIgH", out)

    def test_the_guard_is_keyed_on_the_normalised_field_name(self) -> None:
        """MUTANT: delete the `_ANNOTATE_VOCABULARY` lookup that rewrites the argument.

        Keying the guard on the raw `field` was the plan's first proposal and it does NOT kill
        this node: `severity` IS the dictionary key, so the lowercase spelling still matches
        while `Severity` no longer does - it kills AC1 and AC2 instead. Measured, not reasoned.

        Measured before the fix: `--field severity --value banana` exited 0 and INSERTED a
        second metadata line beside the untouched canonical one, because the denylist folds
        the name and the writer matches it case-sensitively. A guard keyed on the literal
        spelling passes both rows above with the defect live on every other one."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            rc, out = _cli(root, "annotate", "--id", "BG0001",
                           "--field", "severity", "--value", "banana")
            self.assertNotEqual(0, rc, out)
            self.assertEqual(before, p.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            rc, out = _cli(root, "annotate", "--id", "BG0001",
                           "--field", "severity", "--value", "low")
            self.assertEqual(0, rc, out)
            body = p.read_text(encoding="utf-8")
            self.assertIn("> **Severity:** Low", body)
            self.assertEqual(1, body.count("everity:"),
                             "an accepted value under a lowercase field name must update the "
                             "canonical line, not insert a second one beside it")


_FINDINGS_FILED_RE = re.compile(r"^>\s*\*\*Findings-filed-to:\*\*.*$", re.M)


def _findings_filed_line(path) -> str | None:
    """THE detector for a closed unit's discharge: the `> **Findings-filed-to:** ...` metadata
    line in the file at `path`, matched as a line whatever its value, or None.

    An empty value is still a line, so a build that stamps the field on every close is seen
    here rather than read as absent. Every fixture below names its filed ids in its own prose
    too, so a whole-file id search passes with no line written; only this line counts."""
    m = _FINDINGS_FILED_RE.search(Path(path).read_text(encoding="utf-8"))
    return m.group(0) if m else None


def _ids_on(line: str) -> set[str]:
    """The artefact ids a detector line names, read from its value alone."""
    value = line.split(":**", 1)[1]
    return {m.group(0).upper() for m in sdlc_md.ID_SEARCH_RE.finditer(value)}


class ClosedOverRejectNamesTheBugTests(unittest.TestCase):
    """US0628. A story or bug closed over a delivery REJECT names, in its OWN record, the
    artefact its findings were filed to - so the discharge is visible on the artefact rather than
    only in a verdict ledger nobody opens.

    Every close goes through `transition.py set`, the command that writes the status. Every
    discharge is a `filed:` closure recorded through `critic.record_repair` against the REJECT and
    naming an artefact that exists, and is read back through `critic.repair_state`."""

    #: Prose naming every id the fixtures file, fix or cite, so no assertion can be answered by
    #: a whole-file search: only the detector's line is evidence of the write.
    PROSE = ("## Summary\n\nThe delivery review's findings went to BG0002 and BG0003; the "
             "regression test BG0004 asked for pinned a fix, and CR0001 took the residue.\n\n")
    BRIEF = "f" * 12
    #: Origin-tagged, because `critic.py record` refuses an untagged finding: a fixture the
    #: shipped recorder could not have written is not evidence about the ledger it writes.
    TWO_FINDINGS = "[new] the parser drops a trailing row; [new] the refusal names no remedy"

    def _workspace(self) -> Path:
        """A fresh root holding the artefacts the closures file to or cite: BG0002, BG0003 and
        BG0004 (bugs) and CR0001 (a change request), so `record_repair` accepts every id."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        rows = ""
        for bid in ("BG0002", "BG0003", "BG0004"):
            (bd / f"{bid}-x.md").write_text(
                f"# {bid}: filed\n\n> **Status:** Open\n> **Severity:** medium\n",
                encoding="utf-8")
            rows += f"| [{bid}]({bid}-x.md) | filed | Open |\n"
        (bd / "_index.md").write_text(
            "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 3 |\n\n"
            "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n" + rows, encoding="utf-8")
        cd = root / "sdlc-studio" / "change-requests"
        cd.mkdir(parents=True)
        (cd / "CR0001-x.md").write_text("# CR0001: residue\n\n> **Status:** Proposed\n",
                                        encoding="utf-8")
        return root

    def _story(self, extra: str = "") -> tuple[Path, Path]:
        """US0001 at Review, its one criterion verified by hand, clearing every other close
        gate - so a refusal or a missing line is this unit's doing, not a neighbour's."""
        root = self._workspace()
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        path = sd / "US0001-x.md"
        path.write_text(
            "# US0001: s\n\n> **Status:** Review\n\n" + self.PROSE + extra +
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** manual a human looked\n"
            "- **Verified:** yes (2026-01-01)\n", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Review | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Review |\n", encoding="utf-8")
        return root, path

    def _bug(self) -> tuple[Path, Path]:
        """BG0001 In Progress at `conversational` depth (so Verified passes the depth gate) and
        not production-affecting (so Closed needs no soak), its one finding filed to CR0001."""
        root = self._workspace()
        bd = root / "sdlc-studio" / "bugs"
        path = bd / "BG0001-x.md"
        path.write_text(
            "# BG0001: b\n\n> **Status:** In Progress\n> **Severity:** medium\n"
            "> **Verification depth:** conversational (walked through by hand)\n\n"
            + self.PROSE + "## Acceptance Criteria\n\n- [x] the defect no longer reproduces\n",
            encoding="utf-8")
        idx = bd / "_index.md"
        idx.write_text(idx.read_text(encoding="utf-8").replace("| Open | 3 |", "| Open | 3 |\n"
                       "| In Progress | 1 |") + "| [BG0001](BG0001-x.md) | b | In Progress |\n",
                       encoding="utf-8")
        import critic
        critic.record_verdict(root, "BG0001", "REJECT", reviewer="qa", author="dev",
                              brief=self.BRIEF, issues="[new] the fix leaves the residue unowned")
        critic.record_repair(root, "BG0001", "dev", "#1 -> filed: CR0001")
        return root, path

    def _reject_and_repair(self, root: Path, closed: str, issues: str | None = None) -> None:
        import critic
        critic.record_verdict(root, "US0001", "REJECT", reviewer="qa", author="dev",
                              brief=self.BRIEF, issues=issues or self.TWO_FINDINGS)
        critic.record_repair(root, "US0001", "dev", closed)

    def _status(self, path: Path) -> str:
        return sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or ""

    def test_the_story_names_every_filed_artefact(self) -> None:
        """AC1. MUTANTS: drop the write, so the filed ids stay in the repair ledger alone; take
        only the first closure's artefact (`closed[0]`); write into each filed artefact's file
        instead of the closing unit's. Each leaves the detector's line on the STORY missing or
        short of BG0003."""
        import critic
        root, path = self._story()
        self._reject_and_repair(root, "#1 -> filed: BG0002; #2 -> filed: BG0003")
        state = critic.repair_state(root, "US0001", "delivery")
        self.assertEqual((state["state"], state["filed"]), ("complete", 2),
                         "the fixture's premise: two findings, each closed filed:")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        line = _findings_filed_line(path)
        self.assertIsNotNone(line, "the story closed over a REJECT carries no Findings-filed-to "
                                   "line - the discharge is visible only in the repair ledger")
        self.assertEqual(_ids_on(line), {"BG0002", "BG0003"},
                         f"the line does not name exactly the two filed bugs: {line!r}")

    def test_the_one_call_close_names_the_filed_artefacts(self) -> None:
        """AC2. MUTANT: key the write on the unit's latest ledger row being a REJECT. The one-call
        close appends its APPROVE BEFORE the transition runs, so that reading sees an APPROVE and
        writes nothing. And read the filings through `repair_state`, which stops reading a repair
        once the REJECT is answered. The APPROVE is the rejecting reviewer's own round 2, the only
        reviewer the one-call close accepts there."""
        import critic
        root, path = self._story()
        self._reject_and_repair(root, "#1 -> filed: BG0002; #2 -> filed: BG0003")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done",
                         "--verdict", "APPROVE", "--reviewer", "qa", "--author", "dev")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        rows = [r for r in critic.read_verdicts(root, "delivery")
                if sdlc_md.norm_id(r["unit"]) == "US0001"]
        self.assertEqual(rows[-1]["verdict"].upper(), "APPROVE",
                         "the premise: the ledger's LAST row is the one-call close's APPROVE")
        self.assertEqual(critic.repair_state(root, "US0001", "delivery")["state"], "none",
                         "the premise: the round-2 APPROVE answered the REJECT, so repair_state "
                         "no longer reads the repair")
        line = _findings_filed_line(path)
        self.assertIsNotNone(line, "the one-call close wrote no Findings-filed-to line")
        self.assertEqual(_ids_on(line), {"BG0002", "BG0003"}, line)

    def test_a_bug_names_the_filed_artefact_at_every_delivered_terminal(self) -> None:
        """AC3. MUTANTS: write the line for stories only; key it on `_TERMINAL_FOR_PLAN` (Done,
        Fixed), so a bug set straight to Verified - a route that never passes Fixed - gets
        nothing."""
        for target in ("Fixed", "Verified"):
            with self.subTest(target=target):
                root, path = self._bug()
                code, out = _cli(root, "set", "--id", "BG0001", "--status", target)
                self.assertEqual(code, 0, out)
                self.assertEqual(self._status(path), target)
                line = _findings_filed_line(path)
                self.assertIsNotNone(line, f"a bug set to {target} carries no line")
                self.assertEqual(_ids_on(line), {"CR0001"}, line)

    def test_a_terminal_walk_writes_the_line_once(self) -> None:
        """AC4. MUTANT: insert a new line on every terminal step (`_insert_after_status` in place
        of the upsert), so Fixed -> Verified -> Closed leaves three. A second copy is set straight
        to Closed, so a condition naming only Done, Fixed and Verified - which the walk alone
        cannot see, having written its line at Fixed - fails here too."""
        root, path = self._bug()
        for step in ("Fixed", "Verified", "Closed"):
            code, out = _cli(root, "set", "--id", "BG0001", "--status", step)
            self.assertEqual(code, 0, f"{step}: {out}")
            self.assertEqual(self._status(path), step)
        body = path.read_text(encoding="utf-8")
        count = sum(1 for ln in body.splitlines() if "Findings-filed-to" in ln)
        self.assertEqual(count, 1, f"the walk left {count} Findings-filed-to lines:\n{body}")
        self.assertEqual(_ids_on(_findings_filed_line(path)), {"CR0001"})

        direct_root, direct = self._bug()
        code, out = _cli(direct_root, "set", "--id", "BG0001", "--status", "Closed")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(direct), "Closed")
        line = _findings_filed_line(direct)
        self.assertIsNotNone(line, "a bug set straight to Closed carries no line")
        self.assertEqual(_ids_on(line), {"CR0001"}, line)

    def test_a_refused_close_writes_no_line(self) -> None:
        """AC5. MUTANT: stamp the field in `cmd_set` before `transition()` runs, mirroring the
        `--depth` stamp, so a close the ladder refuses keeps the line. The control lands, and its
        `--dry-run` first writes nothing - a close that did not happen names no discharge."""
        question = "should the parser keep the trailing row?"
        root, path = self._story(f"## Open Questions\n\n- [ ] {question}\n\n")
        self._reject_and_repair(root, "#1 -> filed: BG0002; #2 -> filed: BG0003")
        before = path.read_text(encoding="utf-8")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertIn("Open Question", out)
        self.assertNotIn("unanswered delivery REJECT", out,
                         "the refusal is the REJECT gate's, not the Open Question's")
        self.assertEqual(self._status(path), "Review")
        self.assertIsNone(_findings_filed_line(path), "a refused close left a discharge line")
        self.assertEqual(path.read_text(encoding="utf-8"), before)

        ctl_root, ctl = self._story(f"## Resolved Questions\n\n- [x] {question} Ruled: keep it.\n\n")
        self._reject_and_repair(ctl_root, "#1 -> filed: BG0002; #2 -> filed: BG0003")
        ctl_before = ctl.read_text(encoding="utf-8")
        code, out = _cli(ctl_root, "set", "--id", "US0001", "--status", "Done", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertIn("would set US0001", out)
        self.assertIsNone(_findings_filed_line(ctl), "a dry run wrote a discharge line")
        self.assertEqual(ctl.read_text(encoding="utf-8"), ctl_before)
        code, out = _cli(ctl_root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(ctl), "Done")
        line = _findings_filed_line(ctl)
        self.assertIsNotNone(line, "the landed control carries no line")
        self.assertEqual(_ids_on(line), {"BG0002", "BG0003"}, line)

    def test_an_ordinary_close_writes_no_discharge_line(self) -> None:
        """AC6. MUTANTS: stamp the field (empty) on every delivered-terminal close; take each
        closure's `ids` for its `artefact`, so a fix naming an id - or a filing's evidence naming
        a second id - is written as a filing. (d) files BG0002 with evidence naming US0001 too,
        and fixes a finding under BG0004, so its line must name BG0002 and nothing else."""
        import critic
        fixed = "fixed: pinned by the regression test BG0004 asked for"
        copies = {
            "a": "#1 -> filed: BG0002",
            "b": None,
            "c": f"#1 -> {fixed}; #2 -> fixed: the remedy BG0003 proposed, now in the refusal",
            "d": f"#1 -> filed: BG0002, raised against US0001; #2 -> {fixed}",
        }
        lines = {}
        for name, closed in copies.items():
            root, path = self._story()
            if closed is not None:
                self._reject_and_repair(root, closed,
                                        issues="[new] the parser drops a trailing row"
                                        if name == "a" else None)
                self.assertEqual(critic.repair_state(root, "US0001", "delivery")["state"],
                                 "complete", f"({name}) the premise: a complete repair")
            code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
            self.assertEqual(code, 0, f"({name}) {out}")
            self.assertEqual(self._status(path), "Done", f"({name}) did not land at Done")
            lines[name] = _findings_filed_line(path)
        self.assertIsNotNone(lines["a"], "(a) a filed REJECT closed with no line")
        self.assertEqual(_ids_on(lines["a"]), {"BG0002"}, lines["a"])
        self.assertIsNone(lines["b"], "(b) a close with no REJECT at all carries a line")
        self.assertIsNone(lines["c"], "(c) a fix naming an id was written as a filing")
        self.assertIsNotNone(lines["d"], "(d) a mixed repair's filing wrote no line")
        self.assertNotIn("BG0004", _ids_on(lines["d"]),
                         f"(d) the fixed closure's id was written as a filing: {lines['d']!r}")
        self.assertNotIn("US0001", _ids_on(lines["d"]),
                         f"(d) a filing's second id was written as a destination: {lines['d']!r}")
        self.assertEqual(_ids_on(lines["d"]), {"BG0002"}, lines["d"])


class RejectNeedsAnAnswerTests(unittest.TestCase):
    """US0627. A story or bug reaching a delivered terminal over an unanswered delivery REJECT is
    refused until the REJECT is answered, as `critic.coverage_state` reads it: `approved` (a
    later independent APPROVE on the same brief) or `repaired` (a complete repair whose `filed:`
    closures name artefacts that still resolve).

    Every fixture records its REJECT through `critic.record_verdict` in the DELIVERY phase -
    reviewer `qa`, author `dev`, a brief fingerprint, two findings - BACK-DATED to a fixed day,
    so a guard printing today's date cannot pass for one naming the verdict's. Each otherwise
    clears every other gate: no config, so `review.two_role_after` does not apply, and each
    criterion is verified. A refusal is asserted on
    `unanswered delivery REJECT`, text no other gate emits, and every case runs WITHOUT
    `--force` except AC13, which pins what `--force` does."""

    BRIEF = "a1b2c3d4e5f6"
    OTHER_BRIEF = "0f9e8d7c6b5a"
    REJECTED_ON = "2026-01-05"
    FIRST = "the parser drops a trailing row"
    SECOND = "the refusal names no remedy"
    FINDINGS = f"[new] {FIRST}; [new] {SECOND}"
    UNANSWERED = "unanswered delivery REJECT"
    STORY_STATUSES = ("Review", "Done", "Won't Implement", "Superseded")
    BUG_STATUSES = ("Open", "In Progress", "Fixed", "Verified", "Closed", "Won't Fix")

    @staticmethod
    def _index(d: Path, title: str, rows: list, statuses: tuple) -> None:
        counts = "".join(f"| {s} | {sum(1 for _, st in rows if st == s)} |\n" for s in statuses)
        table = "".join(f"| [{i}]({i}-x.md) | t | {st} |\n" for i, st in rows)
        (d / "_index.md").write_text(
            f"# {title}\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{counts}\n## All\n\n"
            f"| ID | Title | Status |\n| --- | --- | --- |\n{table}", encoding="utf-8")

    def _root(self, bug_status: str | None = None) -> Path:
        """A fresh root holding BG0002-BG0004, the bugs a closure files to - and BG0001, the
        unit under test, when `bug_status` names its starting status."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        rows = []
        for bid in ("BG0002", "BG0003", "BG0004"):
            (bd / f"{bid}-x.md").write_text(
                f"# {bid}: filed\n\n> **Status:** Open\n> **Severity:** medium\n",
                encoding="utf-8")
            rows.append((bid, "Open"))
        if bug_status:
            (bd / "BG0001-x.md").write_text(
                f"# BG0001: b\n\n> **Status:** {bug_status}\n> **Severity:** medium\n"
                "> **Verification depth:** conversational (walked through by hand)\n\n"
                "## Acceptance Criteria\n\n- [x] the defect no longer reproduces\n",
                encoding="utf-8")
            rows.append(("BG0001", bug_status))
        self._index(bd, "Bugs", rows, self.BUG_STATUSES)
        return root

    def _story(self, root: Path, status: str = "Review") -> Path:
        """US0001 at `status`, its one criterion verified by hand, with a Revision History for
        a forced override's row to land in."""
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        path = sd / "US0001-x.md"
        path.write_text(
            f"# US0001: s\n\n> **Status:** {status}\n\n"
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** manual a human looked\n"
            "- **Verified:** yes (2026-01-01)\n\n"
            "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            "| 2026-01-01 | dev | Created |\n", encoding="utf-8")
        self._index(sd, "Stories", [("US0001", status)], self.STORY_STATUSES)
        return path

    def _bug_path(self, root: Path) -> Path:
        return root / "sdlc-studio" / "bugs" / "BG0001-x.md"

    def _reject(self, root: Path, uid: str, phase: str = "delivery") -> None:
        """The delivery REJECT every criterion starts from, back-dated to REJECTED_ON."""
        import critic
        with unittest.mock.patch.object(critic.sdlc_md, "now_date",
                                        return_value=self.REJECTED_ON):
            critic.record_verdict(root, uid, "REJECT", reviewer="qa", author="dev",
                                  brief=self.BRIEF, issues=self.FINDINGS, phase=phase)

    def _repair(self, root: Path, uid: str, closed: str) -> None:
        """A repair written through the SHIPPED `critic.py repair`, whose write-time check
        refuses an id that resolves to nothing."""
        import critic
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = critic.main(["repair", "--root", str(root), "--unit", uid,
                                "--author", "dev", "--closed", closed])
        self.assertEqual(code, 0, f"the fixture's repair was refused: {buf.getvalue()}")

    def _status(self, path: Path) -> str:
        return sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or ""

    def _refusal(self, out: str) -> str:
        """The output lines carrying the guard's phrase - what the guard itself said."""
        return "\n".join(ln for ln in out.splitlines() if self.UNANSWERED in ln)

    def _assert_names_the_reject(self, out: str) -> None:
        said = self._refusal(out)
        self.assertTrue(said, f"nothing names the {self.UNANSWERED}:\n{out}")
        self.assertRegex(said, r"\bqa\b", f"the REJECT's reviewer is not named: {said}")
        self.assertIn(self.REJECTED_ON, said, f"the REJECT's verdict date is not named: {said}")

    def test_a_recorded_reject_blocks_done(self) -> None:
        """AC1. MUTANTS: stop reading the unit's delivery verdict (the guard never refuses);
        drop the reviewer and date so the refusal names only the unit. The REJECT is back-dated,
        so a refusal printing today's date does not pass for one naming the verdict's. The
        control is the same story with no REJECT, which lands - so the refusal is this gate's."""
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self._status(path), "Review", "a refused close moved the status")
        self._assert_names_the_reject(out)

        ctl_root = self._root()
        ctl = self._story(ctl_root)
        code, out = _cli(ctl_root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, f"the control, carrying no REJECT, did not land: {out}")
        self.assertEqual(self._status(ctl), "Done")
        self.assertNotIn(self.UNANSWERED, out)

    def test_a_recorded_reject_blocks_every_delivered_terminal_for_a_bug(self) -> None:
        """AC2. MUTANTS: gate the story route only; gate Done and Fixed by name; skip a bug
        already at Fixed. Five routes, each from a fresh root; each from-Fixed route has a
        control carrying no REJECT that lands, so the depth and soak gates pass it."""
        routes = (("In Progress", "Fixed"), ("In Progress", "Verified"),
                  ("In Progress", "Closed"), ("Fixed", "Verified"), ("Fixed", "Closed"))
        for start, target in routes:
            with self.subTest(start=start, target=target):
                root = self._root(bug_status=start)
                self._reject(root, "BG0001")
                code, out = _cli(root, "set", "--id", "BG0001", "--status", target)
                self.assertNotEqual(code, 0, f"{start} -> {target} landed: {out}")
                self.assertEqual(self._status(self._bug_path(root)), start)
                self._assert_names_the_reject(out)
                ctl_root = self._root(bug_status=start)
                code, out = _cli(ctl_root, "set", "--id", "BG0001", "--status", target)
                self.assertEqual(code, 0, f"control {start} -> {target} did not land: {out}")
                self.assertEqual(self._status(self._bug_path(ctl_root)), target)

    def test_a_filed_artefact_id_discharges_the_reject(self) -> None:
        """AC3. MUTANT (in critic.repair_state): count every `filed:` closure as outstanding even
        when its id resolves. Both findings are filed through `critic.py repair` to bugs that
        exist, so the unit reads `repaired` and lands."""
        import critic
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        self._repair(root, "US0001", "#1 -> filed: BG0002; #2 -> filed: BG0003")
        self.assertEqual(critic.coverage_state(root, "US0001", "delivery"),
                         critic.COVERAGE_REPAIRED, "the premise: a complete filed repair")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        self.assertNotIn(self.UNANSWERED, out)

    def test_an_id_naming_no_artefact_is_refused(self) -> None:
        """AC4. MUTANT: accept any filed id `record_repair` accepted at write time. The repair is
        written through `critic.py repair` while both bugs exist; BG0003 is then deleted, so the
        finding it closed - the second - is outstanding again and named, and the first is not."""
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        self._repair(root, "US0001", "#1 -> filed: BG0002; #2 -> filed: BG0003")
        (root / "sdlc-studio" / "bugs" / "BG0003-x.md").unlink()
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self._status(path), "Review")
        said = self._refusal(out)
        self.assertTrue(said, f"nothing names the {self.UNANSWERED}:\n{out}")
        self.assertIn(self.SECOND, said,
                      "the finding the deleted id had closed is not named as outstanding")
        self.assertNotIn(self.FIRST, said,
                         "the finding a still-resolving filing closed is named as outstanding")

    def test_a_complete_repair_answers_the_reject_as_review_coverage_does(self) -> None:
        """AC7. MUTANTS: demand a re-review APPROVE beside the complete repair; count only
        `filed:` closures as answers. One finding is fixed, one filed, and nobody re-reviewed:
        review-coverage reads it `repaired`, so the transition must too."""
        import critic
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        self._repair(root, "US0001",
                     "#1 -> fixed: the trailing row is kept and a test pins it; "
                     "#2 -> filed: BG0002")
        state = critic.repair_state(root, "US0001", "delivery")
        self.assertEqual((state["state"], state["fixed"], state["filed"]), ("complete", 1, 1))
        self.assertEqual(critic.coverage_counts(root, ["US0001"])[critic.COVERAGE_REPAIRED],
                         ["US0001"], "the premise: review-coverage counts it repaired")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        self.assertNotIn(self.UNANSWERED, out)

    def test_a_partly_filed_reject_is_refused(self) -> None:
        """AC8. MUTANT: count any filed closure as an answer. One of two findings is filed, so
        repair_state reads `partial` with one filed closure, and the other finding is named."""
        import critic
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        self._repair(root, "US0001", "#1 -> filed: BG0002")
        state = critic.repair_state(root, "US0001", "delivery")
        self.assertEqual((state["state"], state["filed"]), ("partial", 1))
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self._status(path), "Review")
        said = self._refusal(out)
        self.assertIn(self.SECOND, said, f"the outstanding finding is not named: {said}")
        self.assertNotIn(self.FIRST, said, f"the filed finding is named as outstanding: {said}")

    def test_a_same_brief_approve_answers_the_reject(self) -> None:
        """AC9. MUTANTS: read the REJECT rows directly and refuse any without a complete repair;
        accept any later APPROVE whatever its brief; key the guard on `critic.verdict_for`
        returning a REJECT. Three copies: an independent APPROVE on the REJECT's own brief
        (lands); one on a different brief (refused - another seat's approval does not retire
        this seat's rejection); and one on the same brief recorded by the REJECT's author, `dev`
        as both reviewer and author (refused - `verdict_for` returns that APPROVE, while
        `coverage_state` reads it `unreviewed`, so the refusal must name `qa`'s REJECT)."""
        import critic
        approvals = {"same": ("qa", "dev", self.BRIEF),
                     "different": ("product", "dev", self.OTHER_BRIEF),
                     "self": ("dev", "dev", self.BRIEF)}
        results = {}
        for name, (reviewer, author, brief) in approvals.items():
            root = self._root()
            path = self._story(root)
            self._reject(root, "US0001")
            # a ledger from before the round rules, which refuse `product`'s round 2 now
            with unittest.mock.patch.object(critic, "round_refusal", lambda *a, **k: None):
                critic.record_verdict(root, "US0001", "APPROVE", reviewer=reviewer,
                                      author=author, brief=brief)
            results[name] = (root, path, critic.coverage_state(root, "US0001", "delivery"))
        self.assertEqual(results["same"][2], critic.COVERAGE_APPROVED)
        self.assertEqual(results["different"][2], critic.COVERAGE_UNREVIEWED)
        self.assertEqual(results["self"][2], critic.COVERAGE_UNREVIEWED)
        self.assertEqual(critic.verdict_for(results["self"][0], "US0001")["verdict"], "APPROVE",
                         "the premise: verdict_for reads the self-approval as the standing row")

        root, path, _ = results["same"]
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        self.assertNotIn(self.UNANSWERED, out)
        for name in ("different", "self"):
            with self.subTest(copy=name):
                root, path, _ = results[name]
                code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
                self.assertNotEqual(code, 0, out)
                self.assertEqual(self._status(path), "Review")
                self._assert_names_the_reject(out)

    def test_a_plan_review_reject_alone_does_not_block(self) -> None:
        """AC10. MUTANT: read the plan-review phase as well. The plan-review copy's delivery
        coverage reads `unreviewed` too (it has no delivery verdict), so it is also the control
        that stops a guard refusing on `unreviewed` alone."""
        import critic
        plan_root = self._root()
        plan = self._story(plan_root)
        self._reject(plan_root, "US0001", phase="plan-review")
        self.assertEqual(critic.coverage_state(plan_root, "US0001", "plan-review"),
                         critic.COVERAGE_UNREVIEWED, "the premise: an unrepaired plan REJECT")
        self.assertEqual(critic.read_verdicts(plan_root, "delivery"), [])
        code, out = _cli(plan_root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(plan), "Done")
        self.assertNotIn(self.UNANSWERED, out)

        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self._status(path), "Review")
        self._assert_names_the_reject(out)

    def test_a_stop_ship_ruling_does_not_discharge_the_reject(self) -> None:
        """AC11. MUTANTS: let a carried-table ruling - `stop-ship`, or any of the other three -
        discharge the REJECT. The ruling sits where `retro.find_retro` and every reader of the
        carried table look, `sdlc-studio/retros/RETRO0001-run.md`, so a guard that globbed that
        directory and read `retro.carried_issues` would find it. Each row reads back `ok`, so a
        refusal is never a malformed row's doing."""
        import retro
        for ruling in ("stop-ship", "not-stop-ship", "accepted-risk", "deferred"):
            with self.subTest(ruling=ruling):
                root = self._root()
                path = self._story(root)
                self._reject(root, "US0001")
                rd = root / retro.RETRO_DIR
                rd.mkdir(parents=True)
                body = (f"# RETRO0001: run\n\n## {retro.KNOWN_ISSUES_SECTION}\n\n"
                        "| Issue | Ruling | Ruled by | Date |\n| --- | --- | --- | --- |\n"
                        f"| US0001 | {ruling} | Darren Benson (operator) | 2026-01-06 |\n")
                (rd / "RETRO0001-run.md").write_text(body, encoding="utf-8")
                self.assertEqual(retro.find_retro(root, "RETRO0001"), rd / "RETRO0001-run.md")
                rows = retro.carried_issues(body)
                self.assertEqual([(r["id"], r["ruling"], r["ok"]) for r in rows],
                                 [("US0001", ruling, True)], rows)
                code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
                self.assertNotEqual(code, 0, out)
                self.assertEqual(self._status(path), "Review")
                self._assert_names_the_reject(out)
                self.assertIn("does not discharge", self._refusal(out),
                              "the refusal does not say a carried ruling is no answer")

    def test_an_abandonment_terminal_names_the_reject(self) -> None:
        """AC12. MUTANTS: refuse abandonment too; say nothing. Won't Implement and Superseded for
        the story, Won't Fix for the bug, each landing with the REJECT named."""
        cases = (("story", "Won't Implement"), ("story", "Superseded"), ("bug", "Won't Fix"))
        for kind, target in cases:
            with self.subTest(kind=kind, target=target):
                if kind == "story":
                    root = self._root()
                    path, uid = self._story(root), "US0001"
                else:
                    root = self._root(bug_status="In Progress")
                    path, uid = self._bug_path(root), "BG0001"
                self._reject(root, uid)
                code, out = _cli(root, "set", "--id", uid, "--status", target)
                self.assertEqual(code, 0, out)
                self.assertEqual(self._status(path), target)
                self._assert_names_the_reject(out)

    def test_force_waives_the_guard_and_the_record_names_it(self) -> None:
        """AC13. MUTANTS: make the guard unforceable; check it outside `_pre_write_gates`, where
        `_force_bypassed` cannot re-derive it, so the forced close records no override."""
        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done", "--force")
        self.assertEqual(code, 0, out)
        self.assertEqual(self._status(path), "Done")
        text = path.read_text(encoding="utf-8")
        forced = sdlc_md.extract_field(text, "Forced-override") or ""
        self.assertIn(self.UNANSWERED, forced,
                      f"the Forced-override field does not name the waived guard: {forced!r}")
        history = text.split("## Revision History", 1)[1]
        row = next((ln for ln in history.splitlines() if "--force" in ln), "")
        self.assertIn(self.UNANSWERED, row,
                      f"the Revision History row does not name the waived guard:\n{history}")

    def _verdict(self, root: Path, verdict: str, reviewer: str, author: str, brief: str,
                 on: str, issues: str = "") -> None:
        """One delivery verdict, back-dated to `on`: history, so written as it was before the
        round rules, which refuse a second seat's round on one unit."""
        import critic
        with unittest.mock.patch.object(critic.sdlc_md, "now_date", return_value=on), \
                unittest.mock.patch.object(critic, "round_refusal", lambda *a, **k: None):
            critic.record_verdict(root, "US0001", verdict, reviewer=reviewer, author=author,
                                  brief=brief, issues=issues)

    def test_only_a_principal_supersession_retires_the_reject(self) -> None:
        """US0627 repair. MUTANT (in critic._live_verdict_rows, the one supersession rule
        `verdict_for` and `standing_rejects` share): skip every superseded row, dropping the
        principal-grade test - or give `standing_rejects` its own plain `is_superseded` filter.
        Either way the WEAK copy, a REJECT retired by a hand-appended record its own author
        authorised, reads as carrying no REJECT and lands at Done while `coverage_state` reads
        it `unreviewed`. The PRINCIPAL copy, retired through the shipped `critic.py supersede`
        by an operator in a separate boundary, has no REJECT left and lands."""
        import critic
        weak_root = self._root()
        weak = self._story(weak_root)
        self._reject(weak_root, "US0001")
        with critic.verdicts_path(weak_root, "delivery").open("a", encoding="utf-8") as fh:
            fh.write(f"\n{critic.SUPERSEDE_HEADING}\n\nSUPERSEDED unit=US0001 "
                     f"row-date={self.REJECTED_ON} row-verdict=REJECT row-reviewer=qa "
                     "row-author=dev authorised-by=dev boundary=the authoring session "
                     "reason=the review never ran recorded=2026-01-06\n")
        rows = critic.read_verdicts(weak_root, "delivery")
        self.assertEqual([(r["verdict"], r["superseded"], r["superseded_by"]) for r in rows],
                         [("REJECT", True, "dev")], "the premise: a weakly superseded REJECT")
        self.assertEqual(critic.coverage_state(weak_root, "US0001", "delivery"),
                         critic.COVERAGE_UNREVIEWED)
        code, out = _cli(weak_root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, f"an author-superseded REJECT reached Done: {out}")
        self.assertEqual(self._status(weak), "Review")
        self._assert_names_the_reject(out)

        root = self._root()
        path = self._story(root)
        self._reject(root, "US0001")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = critic.main(["supersede", "--root", str(root), "--unit", "US0001",
                              "--date", self.REJECTED_ON, "--reason", "filed on the wrong unit",
                              "--authorised-by", "Darren Benson (operator)",
                              "--boundary", "operator console"])
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIsNone(critic.verdict_for(root, "US0001"),
                          "the premise: a principal supersession retires the REJECT")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertEqual(code, 0, f"a principal-superseded REJECT still refused: {out}")
        self.assertEqual(self._status(path), "Done")
        self.assertNotIn(self.UNANSWERED, out)

    def test_the_refusal_names_each_unanswered_reject_and_no_answered_one(self) -> None:
        """US0627 repair. MUTANTS (in critic.standing_rejects): return only the OLDEST
        rejection (`[:1]`), only the latest (`[-1:]` on the unanswered list), or every REJECT
        row whatever answered it. (a) two rejections on two briefs, neither answered: both are
        named, each with its reviewer and date. (b) the first answered by an independent
        APPROVE on its own brief: only the second is named. (c) both retired by approvals their
        author recorded, so none is unanswered and `coverage_state` reads `unreviewed`: the
        latest rejection is still named."""
        import critic
        first = ("qa", "2026-01-05")
        second = ("product", "2026-01-07")

        def refused(root: Path, path: Path) -> str:
            code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
            self.assertNotEqual(code, 0, out)
            self.assertEqual(self._status(path), "Review")
            said = self._refusal(out)
            self.assertTrue(said, f"nothing names the {self.UNANSWERED}:\n{out}")
            return said

        def two_rejects(root: Path) -> None:
            self._verdict(root, "REJECT", first[0], "dev", self.BRIEF, first[1], self.FINDINGS)
            self._verdict(root, "REJECT", second[0], "dev", self.OTHER_BRIEF, second[1],
                          self.FINDINGS)

        root = self._root()
        path = self._story(root)
        two_rejects(root)
        said = refused(root, path)
        for who, when in (first, second):
            self.assertIn(f"{who}'s REJECT of {when}", said, f"(a) {who}'s REJECT unnamed: {said}")

        root = self._root()
        path = self._story(root)
        two_rejects(root)
        self._verdict(root, "APPROVE", first[0], "dev", self.BRIEF, "2026-01-08")
        said = refused(root, path)
        self.assertIn(f"{second[0]}'s REJECT of {second[1]}", said, f"(b) {said}")
        self.assertNotIn(first[1], said, f"(b) the answered REJECT is named: {said}")

        root = self._root()
        path = self._story(root)
        two_rejects(root)
        self._verdict(root, "APPROVE", "dev", "dev", self.BRIEF, "2026-01-08")
        self._verdict(root, "APPROVE", "dev", "dev", self.OTHER_BRIEF, "2026-01-09")
        self.assertEqual(critic.coverage_state(root, "US0001", "delivery"),
                         critic.COVERAGE_UNREVIEWED, "the premise: self-approvals answer nothing")
        said = refused(root, path)
        self.assertIn(f"{second[0]}'s REJECT of {second[1]}", said, f"(c) {said}")

    def test_a_reject_itemising_no_findings_claims_no_closure(self) -> None:
        """US0627 repair. MUTANT: the refusal's fallback says "every finding carries a closure"
        for a REJECT that itemises no findings and has no repair, stating a repair nobody
        recorded. AC4 and AC8 are the controls: an itemised REJECT names its findings."""
        import critic
        root = self._root()
        path = self._story(root)
        self._verdict(root, "REJECT", "qa", "dev", self.BRIEF, self.REJECTED_ON, "none")
        self.assertEqual(critic.repair_state(root, "US0001", "delivery")["state"], "none")
        code, out = _cli(root, "set", "--id", "US0001", "--status", "Done")
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self._status(path), "Review")
        self._assert_names_the_reject(out)
        said = self._refusal(out)
        self.assertNotIn("carries a closure", said, f"a repair nobody recorded is claimed: {said}")
        self.assertIn("itemises no findings", said, said)


class SealedRunRefusesWritesTests(unittest.TestCase):
    """US0833 AC3. A run whose report has been signed is SEALED, and a status write to a unit
    inside its batch is refused at `transition.transition` - the single chokepoint `artifact.close`
    also routes through, so one refusal covers both routes.

    MUTANT this test must fail on: print the drift as a warning and let the write through. The
    seal is then ordering advice rather than a transaction, which is the consult's own finding,
    and every assertion about the MESSAGE still passes - so the byte-comparison and the exit code
    below are the load-bearing half, not the wording.

    The paired control is the second half of the criterion: a unit OUTSIDE the batch transitions
    exactly as today. Without it this test passes on an implementation that refuses the whole
    repository while a run happens to be sealed, which is a different and much worse rule.
    """

    RUN_ID = "RUN-01TESTSEAL"
    REPORT = "RPT0001"

    def _sealed_repo(self, root: Path) -> Path:
        """THE SEALED RUN: a bug at `Fixed` inside the signed batch, and a story at `Ready`
        outside it. Both are at statuses the ordinary ladder lets move, measured at the base ref -
        so a refusal here is this seal's and not some neighbouring gate's."""
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: b\n\n> **Status:** Fixed\n> **Severity:** medium\n"
            "> **Verification depth:** functional\n\n## Summary\n\nx\n\n"
            "## Steps to Reproduce\n\n1. x\n\n## Proposed Fix\n\ny\n\n"
            "## Acceptance Criteria\n\n- [x] the defect no longer reproduces\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Fixed | 1 |\n"
            "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | b | Fixed |\n", encoding="utf-8")
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0009-outside.md").write_text(
            "# US0009: outside the batch\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            "### AC1\n- **Verify:** shell echo ok\n", encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0009](US0009-outside.md) | outside the batch | Ready |\n", encoding="utf-8")
        local = root / "sdlc-studio" / ".local"
        local.mkdir(parents=True)
        (local / "run-state.json").write_text(json.dumps({
            "schema": 3, "run_id": self.RUN_ID, "started_at": "2026-09-18T09:00:00Z",
            "ended_at": "2026-09-18T12:00:00Z", "outcome": "goal-reached",
            "goal": "seal the report", "batch": ["BG0001"], "reopened": [],
            "signature": {"principal": "Darren Benson", "signed_at": "2026-09-18",
                          "report": self.REPORT, "fingerprint": "f00dcafe"}}, indent=2),
            encoding="utf-8")
        return root

    @staticmethod
    def _run(root: Path, aid: str) -> tuple[int, str, str]:
        """`transition.main` through the SHIPPED entry point, stdout and stderr kept APART.

        `_cli` merges the two, and the criterion asks specifically where the refusal lands: a
        driver that reads only stdout, as the close's own chain does, must not be told the seal
        held when it did not."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = tr.main(["--root", str(root), "set", aid, "In Progress"])
            except SystemExit as exc:                   # argparse's own exits
                code = int(exc.code or 0)
        return code, out.getvalue(), err.getvalue()

    def test_requirements_still_answers_for_a_sealed_runs_unit(self) -> None:
        """The seal must not break the READ-ONLY question. MUTANT: let `SealedRunRefusal`
        escape `requirements()` as it did when this landed - `transition.py requirements` then
        raises an uncaught exception for every unit of a sealed run's batch, where at the base
        ref it returned a list. A refusal that reports is one thing; a reporting command that
        crashes is a regression, and it was invisible because `requirements` has no gate test
        that puts a sealed run in front of it.

        The requirement it names is the ONE thing that would let the write through, so the
        answer stays useful rather than merely non-fatal.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._sealed_repo(Path(d))
            reqs = transition.requirements(root, "BG0001", "In Progress")
            self.assertTrue(reqs, "a sealed run's unit reports no requirement at all")
            joined = " ".join(reqs)
            self.assertIn(self.RUN_ID, joined, "the requirement does not name the sealed run")
            self.assertIn(self.REPORT, joined, "the requirement does not name the signed report")
            self.assertIn("reopen", joined, "the requirement does not name the way back")
            # ...and the paired control: a unit OUTSIDE the batch answers as it always did.
            self.assertEqual([], transition.requirements(root, "US0009", "In Progress"),
                             "the seal leaked onto a unit outside its batch")

    def test_a_sealed_runs_batch_unit_cannot_be_transitioned(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _refuse_working_tree(Path(d))
            self._sealed_repo(root)
            sealed = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            control = root / "sdlc-studio" / "stories" / "US0009-outside.md"
            before = sealed.read_bytes()

            code, out, err = self._run(root, "BG0001")

            self.assertNotEqual(code, 0, f"the sealed run let the write through: {out}{err}")
            # BYTES, not the Status line. A warning-and-write mutant leaves a file whose status
            # reads `In Progress` while every assertion about the refusal's wording still holds,
            # and only the bytes tell the two implementations apart.
            self.assertEqual(sealed.read_bytes(), before,
                             "the unit file moved under a signed report")
            said = err
            self.assertIn(self.REPORT, said, f"the signed report is unnamed: {said!r}")
            self.assertIn(self.RUN_ID, said, f"the sealed run is unnamed: {said!r}")
            self.assertIn("sprint.py reopen", said, f"no way back is named: {said!r}")
            # The index must not have been synced either - a refusal that wrote the derived row
            # would leave the tree claiming a status the artefact does not carry.
            self.assertIn("| [BG0001](BG0001-x.md) | b | Fixed |",
                          _read(root, "bugs", "_index.md"))

            # THE PAIRED CONTROL: outside the batch, nothing is sealed.
            ccode, cout, cerr = self._run(root, "US0009")
            self.assertEqual(ccode, 0, f"the seal escaped its batch: {cout}{cerr}")
            self.assertIn("> **Status:** In Progress", control.read_text(encoding="utf-8"))
            self.assertNotIn(self.RUN_ID, cerr, f"a unit outside the batch was told about the "
                                                f"seal: {cerr!r}")


if __name__ == "__main__":
    unittest.main()

