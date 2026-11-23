"""Unit tests for review_prep.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/, for the confined git helper
import gitutil  # noqa: E402

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "review_prep.py"
_spec = importlib.util.spec_from_file_location("review_prep", SCRIPT_PATH)
assert _spec and _spec.loader
review_prep = importlib.util.module_from_spec(_spec)
sys.modules["review_prep"] = review_prep
_spec.loader.exec_module(review_prep)


def _base(root: Path) -> Path:
    b = root / "sdlc-studio"
    b.mkdir(parents=True, exist_ok=True)
    return b


class StalenessTests(unittest.TestCase):
    def test_no_review_state_means_needs_review(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            stale = review_prep.staleness(root)
            self.assertIn("prd", stale)
            self.assertTrue(stale["prd"]["needs_review"])

    def test_recent_review_clears_staleness(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            (b / ".local").mkdir()
            # A review far in the future is necessarily after the file mtime.
            (b / ".local" / "review-state.json").write_text(
                json.dumps({"artifacts": {"prd": {"last_reviewed": "2999-01-01T00:00:00Z"}}}),
                encoding="utf-8",
            )
            stale = review_prep.staleness(root)
            self.assertFalse(stale["prd"]["needs_review"])

    @staticmethod
    def _bug(root: Path, n: int, body: str = "", slug: str = "b") -> Path:
        path = root / "sdlc-studio" / "bugs" / f"BG{n:04d}-{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# BG{n:04d}: b\n\n> **Status:** Open\n{body}", encoding="utf-8")
        return path

    @staticmethod
    def _commit(root: Path, when: str, *paths: Path) -> None:
        gitutil.git(["add", "--", *map(str, paths)], root)
        gitutil.git(["commit", "-q", "-m", when], root,
                    env_extra={"GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when})

    def _git_processes(self, root: Path) -> tuple[dict, list]:
        """`staleness(root)` and the argv of each git process it started, caught at Popen,
        which `subprocess.run`, `check_output` and a bare Popen all reach."""
        real, started = subprocess.Popen, []

        def counting(args, *a, **kw):
            if isinstance(args, (list, tuple)) and args and Path(str(args[0])).name == "git":
                started.append(list(args))
            return real(args, *a, **kw)

        with mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                mock.patch.object(subprocess, "Popen", counting):
            got = review_prep.staleness(root)
        return got, started

    def test_the_git_calls_do_not_grow_with_the_artefacts(self) -> None:
        """A close ran half an hour on one `git log -1` per artefact: the count of git processes
        is the same for two tracked artefacts and for twelve."""
        counts = {}
        for many in (2, 12):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                gitutil.git(["init", "-q"], root)
                paths = [self._bug(root, n) for n in range(1, many + 1)]
                self._commit(root, "2026-01-01T00:00:00+00:00", *paths)
                got, started = self._git_processes(root)
                counts[many] = len(started)
                self.assertEqual(many, len(got))
                self.assertEqual({"git"}, {r["modified_method"] for r in got.values()})
        self.assertGreater(counts[2], 0, "the commit times were not read from git at all")
        self.assertEqual(counts[2], counts[12],
                         f"git processes grew with the artefacts: {counts}")

    def test_the_single_pass_reads_each_files_own_commit_time(self) -> None:
        """Each tracked record carries its OWN last commit (the newest touching it, never a
        later commit's time nor its first), and an untracked artefact its file time."""
        t1, t2, t3 = ("2026-01-01T10:00:00+00:00", "2026-02-01T10:00:00+00:00",
                      "2026-03-01T10:00:00+00:00")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], root)
            prd = _base(root) / "prd.md"
            prd.write_text("# PRD\n", encoding="utf-8")
            one, two = self._bug(root, 1), self._bug(root, 2)
            # a name git would quote unless told not to: it is still read from the history
            accented = self._bug(root, 4, slug="caf\u00e9")
            self._commit(root, t1, prd, one, two, accented)
            self._bug(root, 2, "changed\n")
            self._commit(root, t2, two)
            self._bug(root, 1, "changed again\n")
            self._commit(root, t3, one)
            loose = self._bug(root, 3)
            os.utime(loose, (1_700_000_000, 1_700_000_000))
            got, _ = self._git_processes(root)
        stamp = lambda key: review_prep._parse_dt(got[key]["last_modified"])  # noqa: E731
        self.assertEqual(review_prep._parse_dt(t3), stamp("BG0001"), got["BG0001"])
        self.assertEqual(review_prep._parse_dt(t2), stamp("BG0002"), got["BG0002"])
        self.assertEqual(review_prep._parse_dt(t1), stamp("prd"), got["prd"])
        self.assertEqual(review_prep._parse_dt(t1), stamp("BG0004"), got["BG0004"])
        for key in ("BG0001", "BG0002", "BG0004", "prd"):
            self.assertEqual("git", got[key]["modified_method"], got[key])
        self.assertEqual("mtime", got["BG0003"]["modified_method"], got["BG0003"])
        self.assertEqual(datetime.fromtimestamp(1_700_000_000, timezone.utc), stamp("BG0003"))

    #: Where a project sits in its repository: at the top, in a folder below it, and in a
    #: folder whose name git would quote unless told not to.
    LAYOUTS = ("", "proj/one", "caf\u00e9/one")

    def _a_conflict_resolved_in_a_merge(self, below: str) -> dict:
        """`staleness` over a project at `below` in its repository (its top when empty) whose
        bug was last changed by a merge resolving a conflict (t4), reviewed between main's
        earlier parent (t3) and the merge."""
        t1, t2, t3, t4 = ("2026-01-01T10:00:00+00:00", "2026-02-01T10:00:00+00:00",
                          "2026-03-01T10:00:00+00:00", "2026-04-01T10:00:00+00:00")
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            root = repo / below
            gitutil.git(["init", "-q", "-b", "main"], repo)
            one = self._bug(root, 1)
            self._commit(repo, t1, one)
            gitutil.git(["checkout", "-q", "-b", "side"], repo)
            self._bug(root, 1, "the side's change\n")
            self._commit(repo, t2, one)
            gitutil.git(["checkout", "-q", "main"], repo)
            self._bug(root, 1, "main's change\n")
            self._commit(repo, t3, one)
            merged = gitutil.git(["merge", "-q", "side"], repo, check=False)
            self.assertNotEqual(0, merged.returncode, "the fixture's merge did not conflict")
            self._bug(root, 1, "the resolution\n")
            self._commit(repo, t4, one)
            want = gitutil.git(["log", "-1", "--format=%cI", "--", str(one)], repo,
                               text=True).stdout.strip()
            self.assertEqual(review_prep._parse_dt(t4), review_prep._parse_dt(want))
            _base(root).joinpath(".local").mkdir(exist_ok=True)
            (_base(root) / ".local" / "review-state.json").write_text(json.dumps(
                {"artifacts": {"BG0001": {"last_reviewed": "2026-03-15T00:00:00+00:00"}}}),
                encoding="utf-8")
            got, _ = self._git_processes(root)
        self.assertEqual(review_prep._parse_dt(t4),
                         review_prep._parse_dt(got["BG0001"]["last_modified"]), got["BG0001"])
        self.assertEqual("git", got["BG0001"]["modified_method"], got["BG0001"])
        self.assertTrue(got["BG0001"]["needs_review"], got["BG0001"])
        return got

    def test_a_conflict_resolved_in_a_merge_reads_the_merge_time(self) -> None:
        """A merge that resolves a conflict is the file's last change, as `git log -1 -- <path>`
        reads it: a review between the earlier parent and the merge is not current."""
        self._a_conflict_resolved_in_a_merge("")

    def test_a_conflict_resolved_in_a_merge_below_the_repository_root_reads_the_merge_time(
            self) -> None:
        """In a project kept in a folder of its repository, git names a merge's paths from the
        repository top: the conflict's resolution is still the file's last change, so a review
        between the earlier parent and the merge is not current."""
        self._a_conflict_resolved_in_a_merge("proj/one")

    def test_a_clean_merge_is_read_as_git_log_reads_each_path(self) -> None:
        """A clean merge of two sides that each changed the file is its last change; a file only
        one side changed keeps that side's commit, as `git log -1 -- <path>` reads them, with the
        project at the repository top and in a folder below it."""
        t1, t2, t3, t4 = ("2026-01-01T10:00:00+00:00", "2026-02-01T10:00:00+00:00",
                          "2026-03-01T10:00:00+00:00", "2026-04-01T10:00:00+00:00")
        lines = "top\nmiddle 1\nmiddle 2\nmiddle 3\nbottom\n"
        for below in self.LAYOUTS:
            with self.subTest(below=below), tempfile.TemporaryDirectory() as d:
                repo = Path(d)
                root = repo / below
                gitutil.git(["init", "-q", "-b", "main"], repo)
                both, one = self._bug(root, 1, lines), self._bug(root, 2)
                self._commit(repo, t1, both, one)
                gitutil.git(["checkout", "-q", "-b", "side"], repo)
                self._bug(root, 1, lines.replace("top", "top, the side's"))
                self._bug(root, 2, "the side's change\n")
                self._commit(repo, t2, both, one)
                gitutil.git(["checkout", "-q", "main"], repo)
                self._bug(root, 1, lines.replace("bottom", "bottom, main's"))
                self._commit(repo, t3, both)
                gitutil.git(["merge", "-q", "--no-edit", "side"], repo,
                            env_extra={"GIT_COMMITTER_DATE": t4, "GIT_AUTHOR_DATE": t4})
                want = {key: gitutil.git(["log", "-1", "--format=%cI", "--", str(path)], repo,
                                         text=True).stdout.strip()
                        for key, path in (("BG0001", both), ("BG0002", one))}
                got, _ = self._git_processes(root)
                stamp = lambda key: review_prep._parse_dt(got[key]["last_modified"])  # noqa: E731
                self.assertEqual(review_prep._parse_dt(t4), review_prep._parse_dt(want["BG0001"]))
                self.assertEqual(review_prep._parse_dt(t2), review_prep._parse_dt(want["BG0002"]))
                self.assertEqual(review_prep._parse_dt(t4), stamp("BG0001"), got["BG0001"])
                self.assertEqual(review_prep._parse_dt(t2), stamp("BG0002"), got["BG0002"])

    def test_a_project_below_the_repository_root_reads_its_commit_times(self) -> None:
        """A project root that is a folder of the repository reads each artefact's commit
        time from git, not its file time."""
        t1 = "2026-01-01T10:00:00+00:00"
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            gitutil.git(["init", "-q"], repo)
            root = repo / "projects" / "one"
            paths = [self._bug(root, 1), self._bug(root, 2)]
            self._commit(repo, t1, *paths)
            for path in paths:
                os.utime(path, (1_700_000_000, 1_700_000_000))
            got, _ = self._git_processes(root)
        for key in ("BG0001", "BG0002"):
            with self.subTest(key=key):
                self.assertEqual("git", got[key]["modified_method"], got[key])
                self.assertEqual(review_prep._parse_dt(t1),
                                 review_prep._parse_dt(got[key]["last_modified"]), got[key])

    def test_a_project_in_no_repository_reads_each_file_time(self) -> None:
        """Outside any repository, where git names no folder and lists nothing, each artefact
        reads its file time and no history is walked."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = self._bug(root, 1)
            os.utime(path, (1_700_000_000, 1_700_000_000))
            got, started = self._git_processes(root)
        self.assertEqual("mtime", got["BG0001"]["modified_method"], got["BG0001"])
        self.assertEqual(datetime.fromtimestamp(1_700_000_000, timezone.utc),
                         review_prep._parse_dt(got["BG0001"]["last_modified"]))
        self.assertTrue(any("rev-parse" in a for a in started), started)
        self.assertEqual([], [a for a in started if "log" in a], started)

    def test_no_history_is_walked_when_nothing_is_tracked(self) -> None:
        """Every artefact untracked: each reads its file time, and no `git log` walks a history
        that can name none of them."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            gitutil.git(["init", "-q"], root)
            other = root / "src" / "x.py"
            other.parent.mkdir()
            other.write_text("x = 1\n", encoding="utf-8")
            self._commit(root, "2026-01-01T00:00:00+00:00", other)
            self._bug(root, 1)
            got, started = self._git_processes(root)
        self.assertEqual("mtime", got["BG0001"]["modified_method"], got["BG0001"])
        self.assertEqual([], [a for a in started if "log" in a], started)


class QuotedAndRelativePathTests(unittest.TestCase):
    """The history walk reads the paths git prints verbatim: a project in a folder whose name
    git quotes, and the user's `diff.relative` setting, still read each artefact's commit time
    through `review_prep.py prep`, at the repository top and in a folder below it."""

    _bug = staticmethod(StalenessTests._bug)
    _commit = staticmethod(StalenessTests._commit)
    _git_processes = StalenessTests._git_processes
    _a_conflict_resolved_in_a_merge = StalenessTests._a_conflict_resolved_in_a_merge

    #: Folders whose names git quotes even under `core.quotePath=false`: a double quote, a
    #: backslash, and tabs, one leading the name, which a strip of the folder's name would lose.
    QUOTED = ('q"uote/one', "back\\slash/one", "\ttab/o\tne")

    #: The user's git setting that makes `git log` print an ordinary commit's paths relative to
    #: where it runs, where a merge's are still printed from the repository top.
    RELATIVE = "[diff]\n\trelative = true\n"

    T1, T2 = "2026-01-01T10:00:00+00:00", "2026-02-01T10:00:00+00:00"

    def _prep(self, root: Path, gitconfig: str = "") -> dict:
        """The staleness `review_prep.py prep --format json` prints over the project at `root`,
        with `gitconfig` as the user's git configuration."""
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / "gitconfig"
            config.write_text(gitconfig, encoding="utf-8")
            out = io.StringIO()
            with mock.patch.dict(os.environ, gitutil.git_env(GIT_CONFIG_GLOBAL=str(config)),
                                 clear=True), contextlib.redirect_stdout(out):
                self.assertEqual(0, review_prep.main(
                    ["prep", "--root", str(root), "--format", "json"]))
        return json.loads(out.getvalue())["staleness"]

    def _two_commits(self, repo: Path, below: str) -> Path:
        """A project at `below` in `repo` whose two bugs were committed together at T1 (one
        first in that commit's names, one after it) and whose second bug alone changed at T2;
        the second's name holds a `"`, a `\\` and a tab, which git quotes, and each file's own
        time is set far from both."""
        root = repo / below
        gitutil.git(["init", "-q", "-b", "main"], repo)
        one, two = self._bug(root, 1), self._bug(root, 2, slug='q"uo\\b\te')
        self._commit(repo, self.T1, one, two)
        self._bug(root, 2, "changed\n", slug='q"uo\\b\te')
        self._commit(repo, self.T2, two)
        for path in (one, two):
            os.utime(path, (1_700_000_000, 1_700_000_000))
        return root

    def _assert_commit_times(self, got: dict) -> None:
        """BG0001 reads T1 and BG0002 reads T2, each from git."""
        for key, when in (("BG0001", self.T1), ("BG0002", self.T2)):
            with self.subTest(key=key):
                self.assertEqual("git", got[key]["modified_method"], got[key])
                self.assertEqual(review_prep._parse_dt(when),
                                 review_prep._parse_dt(got[key]["last_modified"]), got[key])

    def test_a_project_in_a_folder_git_quotes_reads_its_commit_times(self) -> None:
        """Each artefact of a project in a folder whose name git quotes reads its own commit
        time, not its file time."""
        for below in self.QUOTED:
            with self.subTest(below=below), tempfile.TemporaryDirectory() as d:
                self._assert_commit_times(self._prep(self._two_commits(Path(d), below)))

    def test_a_conflict_resolved_in_a_merge_in_a_folder_git_quotes_reads_the_merge_time(
            self) -> None:
        """In a folder whose name git quotes, a conflict's resolution in a merge is still the
        file's last change."""
        for below in self.QUOTED:
            with self.subTest(below=below):
                self._a_conflict_resolved_in_a_merge(below)

    def test_the_users_diff_relative_setting_reads_as_without_it(self) -> None:
        """With `diff.relative = true` set, each artefact reads the commit time it reads
        without the setting, with the project at the repository top, below it, and in a
        top-level folder named as the artefacts' own first folder."""
        for below in ("", "proj/one", "sdlc-studio"):
            with self.subTest(below=below), tempfile.TemporaryDirectory() as d:
                root = self._two_commits(Path(d), below)
                plain, relative = self._prep(root), self._prep(root, self.RELATIVE)
                self._assert_commit_times(plain)
                self._assert_commit_times(relative)
                self.assertEqual({k: v["last_modified"] for k, v in plain.items()},
                                 {k: v["last_modified"] for k, v in relative.items()})


class PersonaUsageTests(unittest.TestCase):
    def test_defined_referenced_and_unused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "personas.md").write_text(
                "# Personas\n\n## Sarah Chen\n\n## Tom Bradley\n", encoding="utf-8"
            )
            (b / "prd.md").write_text("# PRD\n\nSarah Chen is the PM.\n", encoding="utf-8")
            pu = review_prep.persona_usage(root)
            self.assertEqual(sorted(pu["defined"]), ["Sarah Chen", "Tom Bradley"])
            self.assertEqual(pu["referenced_in_prd"], ["Sarah Chen"])
            self.assertEqual(pu["unused"], ["Tom Bradley"])


class InputsTests(unittest.TestCase):
    def test_counts_and_ac_summary(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            sd = b / "stories"
            sd.mkdir()
            (sd / "US0001-x.md").write_text("# X\n\n> **Status:** Done\n", encoding="utf-8")
            (b / ".local").mkdir()
            (b / ".local" / "verify-report.json").write_text(
                json.dumps({"stories": {"US0001-x": {"verified": 2, "failed": 1}}}),
                encoding="utf-8",
            )
            ins = review_prep.inputs(root)
            self.assertEqual(ins["counts"]["story"], 1)
            self.assertEqual(ins["ac_verification"], {"stories": 1, "verified": 2, "failed": 1})


class RequiredLegsTests(unittest.TestCase):
    """Leg absence is machine-visible: for each of the four required document legs, whether
    the artefact is present and, if not, the waiver decision id (or null). An absent-and-unwaived
    leg is no longer invisible in the prep JSON - the enabler of the BG0110 prose downgrade."""

    def test_absent_leg_is_visible_and_unwaived(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "prd.md").write_text("# PRD\n", encoding="utf-8")
            legs = review_prep.required_legs(root)
            self.assertEqual(set(legs), {"prd", "trd", "tsd", "personas"})
            self.assertTrue(legs["prd"]["present"])
            self.assertFalse(legs["tsd"]["present"])
            self.assertIsNone(legs["tsd"]["waiver"])
            self.assertTrue(legs["prd"]["path"].endswith("prd.md"))

    def test_waived_leg_carries_decision_id(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _base(root)
            import decisions
            r = decisions.record_waiver(root, "leg:tsd", "single-repo project")
            legs = review_prep.required_legs(root)
            self.assertFalse(legs["tsd"]["present"])
            self.assertEqual(legs["tsd"]["waiver"], r["id"])

    def test_personas_directory_counts_as_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            pdir = b / "personas"
            pdir.mkdir()
            (pdir / "maya.md").write_text("# Maya\n", encoding="utf-8")
            self.assertTrue(review_prep.required_legs(root)["personas"]["present"])

    def test_personas_md_fallback_counts_as_present(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            b = _base(root)
            (b / "personas.md").write_text("## Maya\n", encoding="utf-8")
            self.assertTrue(review_prep.required_legs(root)["personas"]["present"])

    def test_prep_json_carries_required_legs(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _base(root)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                review_prep.main(["prep", "--root", str(root), "--format", "json"])
            payload = json.loads(out.getvalue())
            self.assertIn("required_legs", payload)
            self.assertFalse(payload["required_legs"]["tsd"]["present"])


class CmdTests(unittest.TestCase):
    def test_prep_runs_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _base(Path(d))
            self.assertEqual(review_prep.main(["prep", "--root", d, "--format", "json"]), 0)


class PersonaIndexNotCountedTests(unittest.TestCase):
    """BG0129: the persona dir uses `index.md`; the filter excluded only `_index.md`, so the
    index was parsed as a phantom persona ('Persona Index'). Both index spellings are now
    excluded, in both the usage and required-legs passes."""

    def _dir(self, d: Path) -> None:
        pdir = d / "sdlc-studio" / "personas"
        pdir.mkdir(parents=True)
        (pdir / "index.md").write_text("# Persona Index\n")
        (pdir / "maya.md").write_text("# Maya Okafor\n")
        (d / "sdlc-studio" / "prd.md").write_text("# PRD\nMaya Okafor is our user.\n")

    def test_index_md_is_not_a_persona(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._dir(Path(d))
            usage = review_prep.persona_usage(Path(d))
            self.assertNotIn("Persona Index", usage["defined"])
            self.assertEqual(usage["defined"], ["Maya Okafor"])

    def test_underscore_index_still_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            pdir = Path(d) / "sdlc-studio" / "personas"; pdir.mkdir(parents=True)
            (pdir / "_index.md").write_text("# Index\n")
            (pdir / "sam.md").write_text("# Sam Rivera\n")
            (Path(d) / "sdlc-studio" / "prd.md").write_text("# PRD\n")
            self.assertEqual(review_prep.persona_usage(Path(d))["defined"], ["Sam Rivera"])


import json  # noqa: E402


def _review_workspace(root: Path, *, with_rv: bool = True) -> None:
    sd = root / "sdlc-studio"
    for doc in ("prd.md", "trd.md", "tsd.md"):
        (sd / doc).parent.mkdir(parents=True, exist_ok=True)
        (sd / doc).write_text(f"# {doc}\n", encoding="utf-8")
    (sd / "personas").mkdir(exist_ok=True)
    (sd / "personas" / "maya.md").write_text("# Maya\n", encoding="utf-8")
    if with_rv:
        rv = sd / "reviews"
        rv.mkdir(exist_ok=True)
        (rv / "RV0042-unified-review.md").write_text(
            "# RV-0042: Unified Review\n\n> **Status:** N/A\n> **Date:** 2026-07-17\n",
            encoding="utf-8")


class CloseStampTests(unittest.TestCase):
    """US0186: `close` stamps review-state.json deterministically - the CRITICAL
    hand-step the workflow spelled out and nobody performed until 2026-07-16."""

    def test_close_stamps_state_for_every_leg(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            rc = review_prep.close(root, "RV0042")
            self.assertEqual(rc["stamped"], ["persona", "prd", "trd", "tsd"])
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "review-state.json").read_text())
            for leg in ("prd", "trd", "tsd", "persona"):
                self.assertEqual(state["artifacts"][leg]["review_findings_ref"], "RV0042")
                self.assertTrue(state["artifacts"][leg]["last_reviewed"])
            self.assertIn("RV0042", state["reviews"])
            self.assertIn("RV0042-unified-review.md",
                          state["reviews"]["RV0042"]["findings_file"])

    def test_close_preserves_foreign_state_keys(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            local = root / "sdlc-studio" / ".local"
            local.mkdir(parents=True)
            (local / "review-state.json").write_text(
                json.dumps({"version": 1, "artifacts": {"custom": {"x": 1}},
                            "reviews": {"RV0001": {"artifact": "old"}}}), encoding="utf-8")
            review_prep.close(root, "RV0042")
            state = json.loads((local / "review-state.json").read_text())
            self.assertEqual(state["artifacts"]["custom"], {"x": 1})
            self.assertIn("RV0001", state["reviews"])


class AnchorRefusalTests(unittest.TestCase):
    """US0186: the anchor is derived from a record or not at all."""

    def test_close_refuses_without_the_dated_rv(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root, with_rv=False)
            with self.assertRaises(ValueError) as ctx:
                review_prep.close(root, "RV0042")
            self.assertIn("RV0042", str(ctx.exception))
            self.assertFalse(
                (root / "sdlc-studio" / ".local" / "review-state.json").exists())

    def test_latest_write_requires_rv_reference_in_body(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            body = "# Unified Review anchor\n\nno reference to the record here\n"
            with self.assertRaises(ValueError) as ctx:
                review_prep.close(root, "RV0042", latest_body=body)
            self.assertIn("RV0042", str(ctx.exception))
            self.assertFalse((root / "sdlc-studio" / "reviews" / "LATEST.md").exists())

    def test_latest_written_when_body_references_the_record(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            body = "# RV0042 - Unified Review anchor\n\ncontent\n"
            review_prep.close(root, "RV0042", latest_body=body)
            latest = (root / "sdlc-studio" / "reviews" / "LATEST.md").read_text()
            self.assertEqual(latest, body)
class CloseIndexRowTests(unittest.TestCase):
    """US0214: the close writes the RV's own index row.

    Before this, `close` stamped review-state and derived LATEST but left the RV out of
    `reviews/_index.md`. The very next step of the close chain - reconcile - then caught
    the missing row as drift and stopped the ceremony for a mechanical fix that
    `reconcile apply` performed anyway (CR0335). The write belongs where the record is
    created.
    """

    def _rows(self, root):
        p = root / "sdlc-studio" / "reviews" / "_index.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def test_close_writes_the_index_row(self) -> None:
        """AC1: the row exists after the close."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            self.assertIn("RV0042", self._rows(root))

    def test_no_missing_row_drift_after_close(self) -> None:
        """AC2: the close chain's reconcile has nothing to stop for."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "reconcile", Path(review_prep.__file__).parent / "reconcile.py")
            rec = importlib.util.module_from_spec(spec)
            sys.modules["reconcile"] = rec
            spec.loader.exec_module(rec)
            missing = [x for x in rec.apply_meta(root, dry_run=True)["missing_unapplied"]
                       if "RV0042" in str(x)]
            self.assertEqual(missing, [])

    def test_existing_row_is_not_duplicated(self) -> None:
        """AC3: a re-run appends nothing - the close is idempotent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            review_prep.close(root, "RV0042")
            first = self._rows(root)
            r2 = review_prep.close(root, "RV0042")
            self.assertEqual(self._rows(root), first)
            self.assertFalse(r2["indexed"])          # nothing new appended
            self.assertEqual(first.count("RV0042"), 1)

    def test_indexing_failure_still_stamps(self) -> None:
        """AC4: the stamp is the close; indexing is a convenience on top of it."""
        import io
        from contextlib import redirect_stderr
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _review_workspace(root)
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "reconcile", Path(review_prep.__file__).parent / "reconcile.py")
            rec = importlib.util.module_from_spec(spec)
            sys.modules["reconcile"] = rec
            spec.loader.exec_module(rec)
            original = rec.apply_meta
            self.addCleanup(setattr, rec, "apply_meta", original)

            def _boom(*_a, **_k):
                raise OSError("index is read-only")
            rec.apply_meta = _boom
            with redirect_stderr(io.StringIO()) as err:
                r = review_prep.close(root, "RV0042")
            self.assertFalse(r["indexed"])
            self.assertIn("reconcile.py apply", err.getvalue())   # remedy named
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "review-state.json").read_text())
            self.assertIn("RV0042", state["reviews"])             # the close still happened


class ClaimPassOrderTests(unittest.TestCase):
    """US0322 (EP0109): the claim pass is ordered before the logic review, and the two kinds of
    finding are reported separately so a prose-only round is visibly a different kind of round."""

    def test_a_round_with_logic_findings_and_no_claim_pass_is_incomplete(self) -> None:
        order = review_prep.review_phase_order()
        self.assertLess(order.index("claim-pass"), order.index("logic-review"))
        # logic findings recorded with no claim pass run: incomplete, not accepted
        r = review_prep.assess_review_round(claim_pass_ran=False, logic_findings=["bug at x:1"])
        self.assertFalse(r["complete"])
        # the same round WITH the claim pass run first is complete
        r2 = review_prep.assess_review_round(claim_pass_ran=True, logic_findings=["bug at x:1"])
        self.assertTrue(r2["complete"])

    def test_prose_and_logic_findings_are_counted_separately(self) -> None:
        r = review_prep.assess_review_round(
            claim_pass_ran=True, prose_findings=["false claim a", "false claim b"],
            logic_findings=[])
        self.assertEqual(r["prose_findings"], 2)
        self.assertEqual(r["logic_findings"], 0)
        self.assertEqual(r["kind"], "prose-only")       # a different kind of round
        # a round carrying a logic defect is a different kind, counted apart
        r2 = review_prep.assess_review_round(
            claim_pass_ran=True, prose_findings=[], logic_findings=["real bug"])
        self.assertEqual((r2["prose_findings"], r2["logic_findings"]), (0, 1))
        self.assertNotEqual(r2["kind"], r["kind"])


if __name__ == "__main__":
    unittest.main()
