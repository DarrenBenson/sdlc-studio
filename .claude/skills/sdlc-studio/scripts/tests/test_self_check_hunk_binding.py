"""BG1121: an author's self-check record is bound to the unit's own change hunk by hunk, so it
survives the landing orders the per-file view could not see through.

The per-file view (BG1117) reads each declared file at its newest commit that is not another
unit's, which sets aside a later unit's commit but not one that lands beneath the author's own: a
record of uncommitted work, then another unit's commit of its own hunk to the shared file, then
the author's commit of the recorded edit, read as stale. A record taken at a commit later
cherry-picked onto main read as stale too, its commit being no ancestor of HEAD. The record is
now also judged with each change another unit committed since the record (since the commit HEAD
shares with it, after a cherry-pick) taken back out of the content as it stands, hunk by hunk. A
further edit of the unit's own, uncommitted or committed under its id, and a record whose commit
never reached HEAD, still read as stale, and the pages that describe the binding say so.

Every case drives `critic.py` through its entry point in a throwaway project, the fixture shared
with `test_self_check_survives_a_later_unit`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import test_self_check_survives_a_later_unit as later  # noqa: E402 - the shared fixture

critic = later.critic
A, B, SHARED = later.A, later.B, later.SHARED
SKILL = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
LINES = [f"V{n} = {n}\n" for n in range(1, 13)]


def _text(**changes: str) -> str:
    """The twelve-line shared file with the named lines changed (`V2="'a'"`)."""
    return "".join(f"V{n} = {changes[f'V{n}']}\n" if f"V{n}" in changes else line
                   for n, line in enumerate(LINES, 1))


def _git(root: Path, *args: str) -> str:
    return gitutil.git(list(args), root, text=True).stdout.strip()


class HunkBindingTests(unittest.TestCase):

    def setUp(self) -> None:
        self._dirs = [tempfile.TemporaryDirectory() for _ in range(2)]
        self.root, self.scratch = (Path(d.name) for d in self._dirs)
        later._project(self.root)
        later._commit(self.root, f"feat({A}): twelve lines", SHARED, _text())
        self.main = _git(self.root, "rev-parse", "--abbrev-ref", "HEAD")

    def tearDown(self) -> None:
        for d in self._dirs:
            d.cleanup()

    def _row(self) -> dict:
        return critic.read_self_checks(self.root)[-1]

    def _premise(self) -> None:
        """The case proves something only if the content as it stands and the per-file view
        both miss the record, so only the hunk view can admit it."""
        row = self._row()
        self.assertNotEqual(row["digest"], critic.affects_digest(self.root, A),
                            "the content as it stands still matches the record")
        self.assertNotEqual(row["digest"], critic._own_change_digest(self.root, A, row["commit"]),
                            "the per-file view already admits the record")

    def _admitted(self, why: str) -> None:
        r = later._brief(self.root)
        self.assertEqual(0, r.returncode, f"{why}:\n{r.stderr}")
        self.assertNotIn(later.STALE, r.stderr, why)

    def _refused(self, why: str) -> None:
        r = later._brief(self.root)
        self.assertEqual(2, r.returncode, f"{why}:\n{r.stderr}")
        self.assertEqual("", r.stdout, why)
        self.assertIn(later.STALE, r.stderr, why)

    def _sibling_first(self) -> None:
        """A records its uncommitted V2 edit; B commits only its own V11 hunk beneath it; A
        commits the recorded edit on top."""
        later._write(self.root, SHARED, _text(V2="'a'"))
        later._record(self.root, self.scratch)
        later._commit(self.root, f"feat({B}): V11", SHARED, _text(V11="'b'"))
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'", V11="'b'"))

    def _cherry_picked(self) -> None:
        """A commits its V2 edit on a side branch and records there; main takes a commit of B's
        (V6), cherry-picks A's commit, then B adds its V11 hunk."""
        _git(self.root, "checkout", "-q", "-b", "side")
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'"))
        picked = _git(self.root, "rev-parse", "HEAD")
        later._record(self.root, self.scratch)
        _git(self.root, "checkout", "-q", self.main)
        later._commit(self.root, f"feat({B}): V6", SHARED, _text(V6="'b'"))
        gitutil.git(["cherry-pick", picked], self.root)
        later._commit(self.root, f"feat({B}): V11", SHARED, _text(V2="'a'", V6="'b'", V11="'b'"))
        self.assertEqual(_text(V2="'a'", V6="'b'", V11="'b'"),
                         (self.root / SHARED).read_text(encoding="utf-8"))
        ancestor = gitutil.git(["merge-base", "--is-ancestor", self._row()["commit"], "HEAD"],
                               self.root, check=False)
        self.assertNotEqual(0, ancestor.returncode, "premise: the record's commit is on HEAD")

    def test_a_record_before_the_units_commit_survives_a_sibling_landing_first(self) -> None:
        """AC1. Mutants: the hunk view never consulted; B's commit not taken back out; the
        author's own commit taken out as though it were another unit's."""
        self._sibling_first()
        self._premise()
        self._admitted("B's commit beneath A's own staled A's record")

    def test_a_cherry_picked_commit_keeps_its_record(self) -> None:
        """AC2. Mutants: the view refused when the record's commit is no ancestor of HEAD, as
        the per-file view is; the walk over HEAD's whole history rather than the commits HEAD
        holds that the record's commit does not."""
        self._cherry_picked()
        self._premise()
        self._admitted("a cherry-picked commit lost its record")

    def test_another_units_commit_before_the_record_stays_in_the_view(self) -> None:
        """The walk reads only the commits since the record's: another unit's commit beneath
        the record is part of the content the record was taken over, never taken out. Mutant:
        the walk over HEAD's whole history, so B's earlier V11 is taken out too and the record
        reads as stale."""
        later._commit(self.root, f"feat({B}): V11 first", SHARED, _text(V11="'b'"))
        later._write(self.root, SHARED, _text(V2="'a'", V11="'b'"))
        later._record(self.root, self.scratch)
        later._commit(self.root, "feat(US0103): V6", SHARED, _text(V6="'c'", V11="'b'"))
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'", V6="'c'", V11="'b'"))
        self._premise()
        self._admitted("another unit's commit before the record was taken out of it")

    def test_another_units_commits_are_taken_out_newest_first(self) -> None:
        """B commits V11 twice beneath A's own commit of its recorded V2 edit. Only the newest
        of B's changes can come out of the content as it stands, the content then holds the
        older one to take out next, so the walk runs newest first. Mutant: the walk run oldest
        first, so B's first change cannot be taken out of content that holds its second and
        the record reads as stale."""
        later._write(self.root, SHARED, _text(V2="'a'"))
        later._record(self.root, self.scratch)
        later._commit(self.root, f"feat({B}): V11", SHARED, _text(V11="'b1'"))
        later._commit(self.root, f"feat({B}): V11 again", SHARED, _text(V11="'b2'"))
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'", V11="'b2'"))
        self._premise()
        self._admitted("B's two commits to one hunk staled A's record")

    def test_another_units_change_next_to_the_units_own_stales_the_record(self) -> None:
        """git's three-way merge reads two changes on neighbouring lines as a conflict, so B's
        commit of V3 beneath A's own commit of its recorded V2 edit cannot be taken back out
        hunk by hunk and the record reads as stale, as the review help and reference say; with
        one unchanged line between the two (B edits V4) it is taken out and the record
        admitted. B's V3 commit on top of the commit A recorded at, or on top of that commit
        cherry-picked onto main, is set aside whole, so it needs no second record."""
        original = self.root
        for line, order, admitted in (("V3", "beneath", False), ("V4", "beneath", True),
                                      ("V3", "on top", True), ("V3", "picked, on top", True)):
            with self.subTest(line=line, order=order), tempfile.TemporaryDirectory() as d:
                self.root = Path(d)
                later._project(self.root)
                later._commit(self.root, f"feat({A}): twelve lines", SHARED, _text())
                if order == "beneath":
                    later._write(self.root, SHARED, _text(V2="'a'"))
                    later._record(self.root, self.scratch)
                    later._commit(self.root, f"feat({B}): {line}", SHARED,
                                  _text(**{line: "'b'"}))
                    later._commit(self.root, f"feat({A}): V2", SHARED,
                                  _text(V2="'a'", **{line: "'b'"}))
                    self._premise()
                elif order == "on top":
                    later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'"))
                    later._record(self.root, self.scratch)
                    later._commit(self.root, f"feat({B}): {line}", SHARED,
                                  _text(V2="'a'", **{line: "'b'"}))
                else:
                    main = _git(self.root, "rev-parse", "--abbrev-ref", "HEAD")
                    _git(self.root, "checkout", "-q", "-b", "side")
                    later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'"))
                    picked = _git(self.root, "rev-parse", "HEAD")
                    later._record(self.root, self.scratch)
                    _git(self.root, "checkout", "-q", main)
                    gitutil.git(["cherry-pick", picked], self.root)
                    later._commit(self.root, f"feat({B}): {line}", SHARED,
                                  _text(V2="'a'", **{line: "'b'"}))
                if admitted:
                    self._admitted(f"B's change of {line}, {order}, staled A's record")
                else:
                    self._refused(f"B's change of {line}, next to A's, was taken out")
        self.root = original

    def test_an_unrecorded_hunk_of_the_units_own_still_stales_the_record(self) -> None:
        """AC3, the guards. Mutants: a binding that only checks the recorded hunks are present,
        so a further edit of A's own is admitted, uncommitted or committed under A's id; a
        side-branch record whose commit never reached main admitted against B's commits."""
        original = self.root
        for order in (self._sibling_first, self._cherry_picked):
            for committed in (False, True):
                with self.subTest(order=order.__name__, committed=committed), \
                        tempfile.TemporaryDirectory() as d:
                    self.root = Path(d)
                    later._project(self.root)
                    later._commit(self.root, f"feat({A}): twelve lines", SHARED, _text())
                    order()
                    self._admitted("premise: the order alone is admitted")
                    now = (self.root / SHARED).read_text(encoding="utf-8")
                    later._write(self.root, SHARED, now.replace("V4 = 4", "V4 = 'mine'"))
                    if committed:
                        later._commit(self.root, f"fix({A}): V4")
                    self._refused("a further edit of A's own was admitted")
        self.root = original
        _git(self.root, "checkout", "-q", "-b", "never")
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'"))
        later._record(self.root, self.scratch)
        _git(self.root, "checkout", "-q", self.main)
        later._commit(self.root, f"feat({B}): V11", SHARED, _text(V11="'b'"))
        self._refused("a record whose commit never reached main was admitted")

    def test_a_change_that_cannot_be_taken_back_out_leaves_the_record_stale(self) -> None:
        """B's later commit rewrites the line A's own uncommitted edit changed, so its change
        cannot be taken back out of the content as it stands; and a git that cannot set it
        aside at all. Each answers no judgement, never a crash or an admission. Mutants: a
        conflicted take-out read as clean; git unable to run read as no change."""
        self._sibling_first()
        later._write(self.root, SHARED, _text(V2="'a'", V11="'mine'"))
        later._commit(self.root, f"feat({B}): V11 again", SHARED, _text(V2="'a'", V11="'b2'"))
        later._write(self.root, SHARED, _text(V2="'a'", V11="'mine'"))
        self._refused("a take-out that conflicts was admitted")
        base = self._row()["commit"]
        self.assertIsNone(critic._hunk_view_digest(self.root, A, base))
        later._write(self.root, SHARED, _text(V2="'a'", V11="'b2'"))
        self.assertIsNotNone(critic._hunk_view_digest(self.root, A, base),
                             "premise: the clean tree is judged")
        real = critic._git

        def no_merge_file(at, *args, **kw):
            return None if "merge-file" in args else real(at, *args, **kw)

        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                unittest.mock.patch.object(critic, "_git", no_merge_file):
            self.assertIsNone(critic._hunk_view_digest(self.root, A, base))

    def test_a_file_another_unit_added_or_removed_is_set_aside(self) -> None:
        """A declares `src/`; its record of an uncommitted edit precedes B's commit of its own
        hunk to the shared file, adding one module and deleting another, beneath A's commit of
        the edit. Mutants: a file B added read as present, or one it deleted read as absent, in
        the view."""
        later._story(self.root, A, f"src/, tests/test_shared.py, changelog.d/{A}.md")
        later._commit(self.root, f"chore({A}): declare the directory")
        later._write(self.root, SHARED, _text(V2="'a'"))
        later._record(self.root, self.scratch)
        later._write(self.root, SHARED, _text(V11="'b'"))
        later._write(self.root, "src/added.py", "x = 1\n")
        (self.root / "src/other.py").unlink()
        later._commit(self.root, f"feat({B}): V11, add one module, drop another")
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'", V11="'b'"))
        self._premise()
        self._admitted("B's added and removed files staled A's record")

    def test_a_merge_with_content_of_its_own_is_not_taken_apart(self) -> None:
        """A conflict git settled under `-X theirs`, under git's own subject, leaves the shared
        file differing from both parents: content of the merge's own, which stales the record
        (BG1120), so the hunk view gives up on it. Mutant: the merge left unread, so taking
        both other units' changes back out returns the recorded content and admits it."""
        later._record(self.root, self.scratch)
        _git(self.root, "checkout", "-q", "-b", "side")
        later._commit(self.root, f"feat({B}): side", SHARED, _text(V2="'side'", V6="'side'"))
        _git(self.root, "checkout", "-q", self.main)
        later._commit(self.root, "feat(US0103): main", SHARED, _text(V2="'main'", V11="'main'"))
        gitutil.git(["merge", "-q", "--no-edit", "-X", "theirs", "side"], self.root)
        self.assertEqual(_text(V2="'side'", V6="'side'", V11="'main'"),
                         (self.root / SHARED).read_text(encoding="utf-8"),
                         "premise: git settled the conflict by itself")
        self.assertIsNone(critic._hunk_view_digest(self.root, A, self._row()["commit"]))
        self._refused("a merge with content of its own was taken apart and admitted")

    def test_a_side_the_change_cannot_be_taken_out_of_leaves_the_record_stale(self) -> None:
        """B commits a new module under A's declared directory beneath A's own commit, and A
        then edits that module, uncommitted: B's addition cannot be taken back out of content
        that has moved since. And a row naming a commit the repository does not hold. Each
        reads stale, never a crash. Mutants: the absent-side guard dropped, so writing the
        absent side fails with a TypeError; the unreadable walk read as no commit."""
        later._story(self.root, A, f"src/, tests/test_shared.py, changelog.d/{A}.md")
        later._commit(self.root, f"chore({A}): declare the directory")
        later._write(self.root, SHARED, _text(V2="'a'"))
        later._record(self.root, self.scratch)
        later._write(self.root, SHARED, _text(V11="'b'"))
        later._write(self.root, "src/added.py", "x = 1\n")
        later._commit(self.root, f"feat({B}): V11 and a module")
        later._commit(self.root, f"feat({A}): V2", SHARED, _text(V2="'a'", V11="'b'"))
        self._admitted("premise: the order alone is admitted")
        later._write(self.root, "src/added.py", "x = 2\n")
        self._refused("A's edit to a module B added was admitted")
        row = self._row()
        with (self.root / later.LOG).open("a", encoding="utf-8") as fh:
            fh.write(f"| {A} | builder | 2026-11-24 | TRUE 2, FALSE 0, UNVERIFIABLE 0 | "
                     f"killed 1, survived 0 | {row['digest']} at deadbeef1234 |\n")
        self.assertEqual("deadbeef1234", self._row()["commit"])
        self.assertIsNone(critic._hunk_view_digest(self.root, A, "deadbeef1234"))
        self._refused("a row naming a commit git does not hold was admitted")

    def test_the_pages_and_the_log_header_describe_the_hunk_binding(self) -> None:
        """AC4. Mutants: any of the five texts left on the per-file view alone, or still saying
        uncommitted recorded work is staled by another unit's commit landing first."""
        log = (REPO / "sdlc-studio" / "reviews" / "author-self-checks.md").read_text(
            encoding="utf-8")
        self.assertTrue(log.startswith(critic._SELF_CHECK_HEADER),
                        "the committed log's header is not the one the tool writes")
        review = (SKILL / "reference-review.md").read_text(encoding="utf-8")
        start = review.index("`review.author_self_check` decides")
        config = next(line for line in (SKILL / "reference-config.md").read_text(
            encoding="utf-8").splitlines() if line.startswith("| `review.author_self_check` |"))
        help_page = (SKILL / "help" / "review.md").read_text(encoding="utf-8")
        texts = {"help/review.md": help_page[help_page.index("The row it writes to"):
                                             help_page.index("## Retiring a verdict row")],
                 "reference-review.md": review[start:review.index("### A REJECT", start)],
                 "reference-config.md": config,
                 "_SELF_CHECK_HEADER": critic._SELF_CHECK_HEADER}
        for name, text in texts.items():
            flat = " ".join(text.replace(">", " ").split())
            with self.subTest(text=name):
                self.assertIn("hunk by hunk", flat, "the hunk binding is not described")
                self.assertIn("cherry-pick", flat, "the cherry-picked record is not described")
                for stale in ("landing first", "can still read as stale",
                              "read at its newest commit since"):
                    self.assertNotIn(stale, flat)

    def test_the_pages_say_a_change_next_to_the_units_own_stales_the_record(self) -> None:
        """The review help and the review reference say that another unit's change beneath the
        author's own, committed, uncommitted or cherry-picked, is taken out hunk by hunk and
        cannot be when it is on or next to a line the author's own change touches, so the
        record reads as stale, and neither says such a commit needs no second record. Mutants:
        either page left saying another unit's commit never needs a second record."""
        review = (SKILL / "reference-review.md").read_text(encoding="utf-8")
        start = review.index("`review.author_self_check` decides")
        help_page = (SKILL / "help" / "review.md").read_text(encoding="utf-8")
        texts = {"help/review.md": help_page[help_page.index("The row it writes to"):
                                             help_page.index("## Retiring a verdict row")],
                 "reference-review.md": review[start:review.index("### A REJECT", start)]}
        for name, text in texts.items():
            flat = " ".join(text.split())
            with self.subTest(text=name):
                self.assertIn("on or next to a line the author's own change touches", flat)
                self.assertIn("beneath the author's own change, committed, uncommitted or "
                              "cherry-picked", flat)
                self.assertIn("`git merge-file`", flat)
                for false in ("stays current until the unit's own change moves",
                              "after the author's own needs no second record;"):
                    self.assertNotIn(false, flat)


if __name__ == "__main__":
    unittest.main()
