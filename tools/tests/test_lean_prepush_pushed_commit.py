"""BG0837: the pre-push gate judges the commit being pushed, not the working tree.

The hook ran `gate.py --boundary push` in the pusher's working tree, so an uncommitted fix turned
a red push green (CI, checking out the commit, then went red) and an uncommitted red edit refused
a green push. It now runs the gate in a temporary worktree checked out at each pushed commit and
removes that worktree afterwards, red or green. A dirty tree is neither refused nor touched.

Every fixture is a throwaway clone from `test_pre_push_hook._Clone`: the tracked hook, a bare
remote, and a stub `gate.py` at the path the hook invokes. Here the stub's verdict is written INTO
the file, so the committed copy and the working-tree copy can disagree.
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import unittest

# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_pre_push_hook as _pp

#: A stub gate whose verdict is its own text, not the environment's: `{rc}` is the exit code and
#: the line it prints names which copy ran.
STUB = 'print("  [{word}] stub gate - the {which} copy ran")\nraise SystemExit({rc})\n'
RED_COMMITTED = STUB.format(word="FAIL", which="COMMITTED-RED", rc=1)
GREEN_COMMITTED = STUB.format(word="PASS", which="COMMITTED-GREEN", rc=0)
GREEN_EDIT = STUB.format(word="PASS", which="UNCOMMITTED-GREEN", rc=0)
RED_EDIT = STUB.format(word="FAIL", which="UNCOMMITTED-RED", rc=1)


def _gate_file(fx: "_pp._Clone"):
    return fx.clone / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"


def _commit_gate(fx: "_pp._Clone", text: str, message: str) -> None:
    _gate_file(fx).write_text(text, encoding="utf-8")
    _pp._git(fx.clone, "add", "-A")
    _pp._git(fx.clone, "commit", "-q", "-m", message)


class PrePushPushedCommitTests(unittest.TestCase):
    """AC1-AC2."""

    def _assert_no_worktree_left(self, fx: "_pp._Clone") -> None:
        listed = _pp._git(fx.clone, "worktree", "list", "--porcelain").stdout
        self.assertEqual(1, listed.count("worktree "),
                         "the temporary worktree outlived the push:\n" + listed)

    def test_the_gate_judges_the_pushed_commit(self) -> None:
        """AC1. MUTANTS: (1) run the gate in the working tree (HEAD before the fix) - the
        uncommitted green copy runs and the push goes through; (2) stash the edit and never
        restore it - the working-tree edit is gone afterwards; (3) check out the clone's HEAD
        rather than the pushed sha - the topic-branch push below runs the green HEAD; (4) drop the
        worktree cleanup - a second worktree is still listed after the refusal."""
        fx = _pp._Clone()
        try:
            _commit_gate(fx, RED_COMMITTED, "a red gate, committed")
            _gate_file(fx).write_text(GREEN_EDIT, encoding="utf-8")       # the uncommitted "fix"
            r = fx.push()
            self.assertNotEqual(0, r.returncode,
                                "an uncommitted green edit let a red commit through:\n" + r.stderr)
            self.assertIn("COMMITTED-RED copy ran", r.stderr,
                          "the refusal did not come from the committed gate:\n" + r.stderr)
            self.assertNotIn("UNCOMMITTED-GREEN", r.stderr, "the working-tree gate ran:\n" + r.stderr)
            self.assertEqual(0, fx.remote_count(), "the remote advanced despite the refusal")
            self.assertEqual(GREEN_EDIT, _gate_file(fx).read_text(encoding="utf-8"),
                             "the pusher's uncommitted edit did not survive the push")
            self.assertIn("gate.py", _pp._git(fx.clone, "status", "--porcelain").stdout,
                          "the edit is no longer uncommitted")
            self._assert_no_worktree_left(fx)

            # The PUSHED commit, not the checked-out one: main (red) is pushed from a topic
            # checkout whose HEAD carries a green gate.
            _pp._git(fx.clone, "checkout", "-q", "--", ".")
            _pp._git(fx.clone, "checkout", "-q", "-b", "topic")
            _commit_gate(fx, GREEN_COMMITTED, "a green gate on the topic branch")
            topic = fx.push("main")
            self.assertNotEqual(0, topic.returncode,
                                "main was judged by the checked-out topic commit:\n" + topic.stderr)
            self.assertIn("COMMITTED-RED copy ran", topic.stderr, topic.stderr)
            self.assertEqual(0, fx.remote_count())
            self._assert_no_worktree_left(fx)
        finally:
            fx.cleanup()

    def test_an_uncommitted_red_edit_does_not_refuse_a_green_commit(self) -> None:
        """AC2. MUTANTS: (1) run the gate in the working tree (HEAD before the fix) - the
        uncommitted red copy refuses; (2) refuse any dirty tree - the dirty push is refused with
        no gate run; (3) drop the worktree cleanup."""
        fx = _pp._Clone()
        try:
            _commit_gate(fx, GREEN_COMMITTED, "a green gate, committed")
            _gate_file(fx).write_text(RED_EDIT, encoding="utf-8")          # an unfinished red edit
            r = fx.push()
            self.assertEqual(0, r.returncode,
                             "an uncommitted red edit refused a green commit:\n" + r.stderr)
            self.assertIn("COMMITTED-GREEN copy ran", r.stderr,
                          "the committed gate did not run:\n" + r.stderr)
            self.assertNotIn("UNCOMMITTED-RED", r.stderr, "the working-tree gate ran:\n" + r.stderr)
            self.assertEqual(2, fx.remote_count(), "the push reported success but the remote did not advance")
            self.assertEqual(RED_EDIT, _gate_file(fx).read_text(encoding="utf-8"),
                             "the pusher's uncommitted edit did not survive the push")
            self._assert_no_worktree_left(fx)
        finally:
            fx.cleanup()


if __name__ == "__main__":
    unittest.main()
