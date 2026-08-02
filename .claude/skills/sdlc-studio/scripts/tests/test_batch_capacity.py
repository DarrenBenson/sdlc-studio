#!/usr/bin/env python3
"""`sprint batch swap`: trading units is ONE recorded decision.

Drop-then-add reaches the same batch, but the ledger then carries two unrelated changes and a
reader cannot tell a trade from a cut followed later by an unrelated addition. The swap is the
intent, and the record should say so.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"


def sdlc_md_norm(rec):
    from lib import sdlc_md
    return sdlc_md.norm_id(rec)


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod

class SwapTests(unittest.TestCase):
    """A swap is ONE recorded decision, not a drop that happens to be followed by an add."""

    def _run(self, root, *argv):
        sprint = _load()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = sprint.main(["batch", *argv, "--root", str(root)])
        return rc, buf_out.getvalue() + buf_err.getvalue()

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        for uid, pts in (("US0001", 5), ("US0002", 3), ("US0003", 5), ("US0004", 2)):
            (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
                f"# {uid}: a unit\n\n> **Status:** Ready\n> **Points:** {pts}\n"
                f"> **Affects:** src/a.py\n", encoding="utf-8")
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-T", "batch": ["US0001", "US0002"],
                        "outcome": "running"}), encoding="utf-8")
        return root

    def test_swap_records_one_pair_and_matches_the_drop_then_add_equivalent(self) -> None:
        """MUTANT: record no swap entry, leaving only the individual changes.

        The BATCH is asserted equal to what drop-then-add reaches, AND the swap record asserted
        to exist - the first alone passes with the intent unrecorded, which is the defect.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003",
                                "--reason", "traded for the blocking one")
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "run-state.json").read_text())
        self.assertEqual(0, rc, out)
        self.assertEqual(["US0002", "US0003"], sorted(state["batch"]),
                         "the batch is not what drop-then-add would have reached")
        swaps = state.get("batch_swaps") or []
        self.assertEqual(1, len(swaps), "the swap was not recorded as one decision")
        self.assertEqual(["US0001"], swaps[0]["out"])
        self.assertEqual(["US0003"], swaps[0]["in"])
        self.assertIn("traded for", swaps[0]["reason"])

    def test_an_unbalanced_swap_warns_with_the_delta_and_a_balanced_one_does_not(self) -> None:
        """MUTANT: warn always, or never.

        Both directions: a warning on every swap is noise the operator learns to skip, and no
        warning at all hides the thing the appetite has to absorb.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _rc, out = self._run(root, "swap", "--out", "US0002", "--in", "US0003",
                                 "--reason", "r")          # 3 -> 5
        self.assertIn("+2", out, f"an unbalanced swap did not report its delta:\n{out}")
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            _rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003",
                                 "--reason", "r")          # 5 -> 5
        self.assertNotIn("NOT balanced", out, "a balanced swap warned anyway")

    def test_an_absent_out_unit_refuses_atomically_and_changes_nothing(self) -> None:
        """MUTANT: check each outgoing unit as it is dropped.

        A half-applied swap leaves the batch in a state nobody chose, and the operator's next
        move is to guess which half landed. The state file is asserted byte-unchanged.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            before = (root / "sdlc-studio" / ".local" / "run-state.json").read_text()
            rc, out = self._run(root, "swap", "--out", "US0001,US0099", "--in", "US0003",
                                "--reason", "r")
            after = (root / "sdlc-studio" / ".local" / "run-state.json").read_text()
        self.assertEqual(2, rc, out)
        self.assertIn("US0099", out, "the refusal does not name the absent unit")
        self.assertEqual(before, after, "a refused swap still wrote to the run state")

    def test_a_swap_without_a_reason_is_refused(self) -> None:
        """MUTANT: default the reason to empty and carry on.

        A swap changes what the run is FOR. Unrecorded, the close cannot say why the delivered
        batch differs from the planned one.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, out = self._run(root, "swap", "--out", "US0001", "--in", "US0003")
        self.assertEqual(2, rc)
        self.assertIn("--reason", out)

    def test_one_sided_swaps_are_refused(self) -> None:
        """MUTANT: allow --out alone, silently turning a swap into a drop."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            rc, _out = self._run(root, "swap", "--out", "US0001", "--reason", "r")
        self.assertEqual(2, rc, "a one-sided swap was accepted")

    def test_the_out_list_accepts_every_house_form_identically(self) -> None:
        """MUTANT: split on commas only, or accept only a repeated flag.

        `--out A --out B` and `--out A,B` are the same request in this project's grammar, and a
        verb that honours one is a second grammar.
        """
        sprint = _load()
        from lib import sdlc_md
        self.assertEqual(sdlc_md.split_id_list(["US0001", "US0002"]),
                         sdlc_md.split_id_list(["US0001,US0002"]),
                         "the repeated and comma forms are not read identically")



class AddEpicTests(unittest.TestCase):
    """Adding an epic's stories one at a time reaches the same batch and a WORSE record.

    The ledger then reads as several unrelated decisions, and nobody sees the points the batch
    grew by in one step - which is the number that decides whether the appetite still holds.
    """

    def _run(self, root, *argv):
        sprint = _load()
        buf_out, buf_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            rc = sprint.main(["batch", *argv, "--root", str(root)])
        return rc, buf_out.getvalue() + buf_err.getvalue()

    def _story(self, root, uid, epic, status, pts):
        (root / "sdlc-studio" / "stories" / f"{uid}-x.md").write_text(
            f"# {uid}: a unit\n\n> **Status:** {status}\n> **Epic:** {epic}\n"
            f"> **Points:** {pts}\n> **Affects:** src/a.py\n", encoding="utf-8")

    def _root(self, d, batch=("US0001",)):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        self._story(root, "US0001", "EP0010", "Ready", 5)
        self._story(root, "US0002", "EP0010", "Ready", 3)
        self._story(root, "US0003", "EP0010", "Draft", 8)     # right epic, WRONG status
        self._story(root, "US0004", "EP0011", "Ready", 13)    # right status, WRONG epic
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-T", "batch": list(batch), "outcome": "running"}),
            encoding="utf-8")
        return root

    def _batch(self, root):
        return json.loads(
            (root / "sdlc-studio" / ".local" / "run-state.json").read_text(encoding="utf-8")
        ).get("batch") or []

    def test_the_link_form_of_the_epic_field_is_selected(self) -> None:
        """MUTANT: compare the Epic field with an exact string equality, as shipped.

        This corpus writes the field two ways - `EP0010`, and the link form
        `[EP0010: A Title](../epics/EP0010-a-title.md)`. The first version compared exactly and
        so could not see the second: 33 real stories were invisible to it, including all 13 on
        EP0005, and the command reported the epic as empty. My own front-door check missed it
        because the fixture I built used only the bare form - so the fixture, not the code, is
        what this test fixes.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=[])
            # the LINK form, which is what a third of this repo's stories carry
            (root / "sdlc-studio" / "stories" / "US0007-linked.md").write_text(
                "# US0007: a linked unit\n\n> **Status:** Ready\n"
                "> **Epic:** [EP0010: A Title](../epics/EP0010-a-title.md)\n"
                "> **Points:** 8\n> **Affects:** src/a.py\n", encoding="utf-8")
            rc, out = self._run(root, "add-epic", "--epic", "EP0010", "--status", "Ready",
                                "--format", "json")
            rec = json.loads(out)
        self.assertEqual(0, rc, out)
        self.assertIn("US0007", rec["added"],
                      "a story whose Epic field is written in the LINK form was not selected - "
                      "an exact-string compare cannot see it, and a third of this corpus uses it")

    def test_the_selection_agrees_with_select_batch(self) -> None:
        """MUTANT: hand-roll the walk again instead of delegating.

        The criterion names `select_batch` as law precisely because a second selector is a
        second answer to the same question. Asserted as EQUALITY with the shared selector over
        a mixed-form fixture, so any future divergence reddens rather than being reasoned about.
        """
        sprint = _load()
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=[])
            (root / "sdlc-studio" / "stories" / "US0007-linked.md").write_text(
                "# US0007: a linked unit\n\n> **Status:** Ready\n"
                "> **Epic:** [EP0010: A Title](../epics/EP0010-a-title.md)\n"
                "> **Points:** 8\n> **Affects:** src/a.py\n", encoding="utf-8")
            mine = sprint._epic_units(root, "EP0010", "Ready")
            canon = [sdlc_md_norm(u["id"]) for u in
                     sprint.select_batch(root, "story", "Ready", epics={"EP0010"})]
        self.assertEqual(sorted(canon), sorted(mine),
                         "the add-epic selection disagrees with `select_batch`, which the "
                         "criterion names as the selector")

    def test_the_epic_stories_at_the_named_status_are_added_as_a_priced_set(self) -> None:
        """MUTANT: add them without reporting the points, or report a constant.

        The POINTS are asserted as a number, not merely present: the count of units says
        nothing about whether the appetite still holds, and 8 is the only right answer here
        (US0002 alone is fresh - US0001 is already in the batch and must not be repriced).
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=[])
            rc, out = self._run(root, "add-epic", "--epic", "EP0010", "--status", "Ready",
                                "--format", "json")
            rec = json.loads(out)
            batch = self._batch(root)
        self.assertEqual(0, rc, out)
        self.assertEqual(["US0001", "US0002"], sorted(rec["added"]))
        self.assertEqual(8, rec["points"],
                         "the set was added without its price, so the appetite cannot be judged")
        self.assertEqual(["US0001", "US0002"], sorted(batch))

    def test_a_story_added_to_the_epic_between_calls_is_picked_up_and_a_wrong_status_one_is_not(
            self) -> None:
        """MUTANT: resolve the epic's stories from a snapshot rather than reading the tree.

        Proven against a MUTATED fixture, not a second identical call: repeating the same call
        passes under a cached list too, so it would not discriminate. A story appearing in the
        epic afterwards must be seen, and the Draft one must stay out both times.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=[])
            self._run(root, "add-epic", "--epic", "EP0010", "--status", "Ready")
            self._story(root, "US0009", "EP0010", "Ready", 2)   # appears AFTER the first call
            rc, out = self._run(root, "add-epic", "--epic", "EP0010", "--status", "Ready",
                                "--format", "json")
            rec = json.loads(out)
            batch = self._batch(root)
        self.assertEqual(0, rc, out)
        self.assertEqual(["US0009"], rec["added"],
                         "a story added to the epic between calls was not picked up, so the "
                         "selection is a snapshot rather than the tree")
        self.assertNotIn("US0003", batch, "a Draft story was added at status Ready")
        self.assertNotIn("US0004", batch, "a story from another epic was added")

    def test_already_present_units_are_named_and_not_double_counted(self) -> None:
        """MUTANT: silently skip the duplicates, or count their points again.

        Both halves are asserted. Naming them is what tells the operator the set was partly
        there already; not repricing them is what keeps the appetite number honest.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=["US0001"])
            rc, out = self._run(root, "add-epic", "--epic", "EP0010", "--status", "Ready",
                                "--format", "json")
            rec = json.loads(out)
            batch = self._batch(root)
        self.assertEqual(0, rc, out)
        self.assertEqual(["US0001"], rec["already"], "the duplicate was not named")
        self.assertEqual(["US0002"], rec["added"])
        self.assertEqual(3, rec["points"],
                         "a unit already in the batch was priced again, inflating the growth")
        self.assertEqual(["US0001", "US0002"], sorted(batch))

    def test_an_epic_with_nothing_at_that_status_fails_loud_and_changes_nothing(self) -> None:
        """MUTANT: return 0 on an empty selection.

        Adding nothing silently reads exactly like adding everything, and the operator would
        only discover the batch never grew at the close.
        """
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, batch=["US0001"])
            before = self._batch(root)
            rc, out = self._run(root, "add-epic", "--epic", "EP0011", "--status", "Done")
            after = self._batch(root)
        self.assertNotEqual(0, rc, "an empty selection was reported as a successful add")
        self.assertIn("nothing was added", out.lower())
        self.assertEqual(before, after, "a refused add still changed the batch")


if __name__ == "__main__":
    unittest.main()
