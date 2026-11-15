"""US1067: the close lists on the retro every learning about to go live, whatever wrote it.

`sprint.py close` runs a `persona-memory` stage that lists every approved learning not yet live
in a delimited `## Persona learnings` block on the retro, with its seat, its approver and what it
addresses, stamps each Listed-in with the run and names the ids on the run record. It also names
each seat whose record holds adverse evidence and no learning, and how many verdict rows name no
seat. Driven through `sprint.main` in throwaway projects; every other chain step is stubbed green.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")

RUN = "RUN-LEARN0001"
QA = "Sam Eriksson (qa)"
PRODUCT = "Lena Marsh (product)"
BUILDER = "Dani Okafor (engineering)"
BEGIN = "<!-- persona-learnings:begin"
END = "<!-- persona-learnings:end -->"


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _project(root: Path, rows: list[tuple]) -> None:
    """Three seat cards, two stories, an open run over both, a retro naming them and a ledger of
    `rows`, each (unit, verdict, reviewer, author, issues). A git work tree, as the store
    refuses to write where nothing it writes could be committed."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True, timeout=60,
                   env=gitutil.git_env())
    for role, holder in (("engineering", "Dani Okafor"), ("qa", "Sam Eriksson"),
                         ("product", "Lena Marsh")):
        _write(root, f"sdlc-studio/personas/seats/{role}.md",
               f"<!-- role: {role} -->\n# {holder} - {role} seat\n\ncharter\n")
    for uid in ("US0101", "US0102"):
        _write(root, f"sdlc-studio/stories/{uid}-widget.md",
               f"# {uid}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")
    _write(root, "sdlc-studio/retros/RETRO0001-run.md",
           "# RETRO0001: run\n\n> **Date:** 2026-11-15\n> **Batch:** US0101, US0102\n\n"
           "## Delivered\n\n- US0101 and US0102 shipped\n\n## Lessons\n\n- learned a thing\n")
    _write(root, "sdlc-studio/reviews/critic-verdicts.md",
           "# Critic Verdicts\n\n"
           "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Source | Issues |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
           + "".join(f"| {u} | {v} | {r} | {a} | 2026-11-14 | - | full | - | {i} |\n"
                     for u, v, r, a, i in rows))
    _write(root, "sdlc-studio/.local/run-state.json", json.dumps({
        "schema": 1, "run_id": RUN, "started_at": "2026-11-14T00:00:00Z", "ended_at": None,
        "outcome": "running", "goal": "done", "batch": ["US0101", "US0102"], "handoff": None,
        "appetite": {"minutes": 240.0, "units": 8}, "sprint_goal": "learnings are listed",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "they were"}}))


def _learning(root: Path, key: str, title: str, *, state: str = "approved",
              approver: str = "", addresses: str = "") -> str:
    """One learning written through the store's own functions, as `add` and a later approval
    write it; returns its id."""
    pm = _live("persona_memory")
    entry = pm.add(root, key, title, f"{title}, in prose.", ["US0101"])
    if state != "proposed":
        pm.set_field(root, entry["id"], "State", state)
    if approver:
        pm.set_field(root, entry["id"], "Approved-by", approver)
    if addresses:
        pm.set_field(root, entry["id"], "Addresses", addresses)
    return entry["id"]


def _close(root: Path) -> tuple[int, str, str]:
    """`sprint close` with every chain step but `persona-memory` stubbed green."""
    mod = _live("sprint")
    stack = contextlib.ExitStack()
    stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
    for name in mod._CLOSE_CHAIN:
        if name != "persona-memory":
            stack.enter_context(unittest.mock.patch.object(
                mod, "_close_" + name.replace("-", "_"),
                lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
    out, err = io.StringIO(), io.StringIO()
    with stack, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _retro(root: Path) -> str:
    return (root / "sdlc-studio" / "retros" / "RETRO0001-run.md").read_text(encoding="utf-8")


def _block(text: str) -> str:
    return text.split(BEGIN, 1)[1].split(END, 1)[0]


def _fields(root: Path, entry_id: str) -> dict:
    pm = _live("persona_memory")
    for entries in pm.all_stores(root).values():
        for e in entries:
            if e["id"] == entry_id:
                return e["fields"]
    raise AssertionError(f"no store holds {entry_id}")


def _state(root: Path) -> dict:
    return json.loads((root / "sdlc-studio" / ".local" / "run-state.json")
                      .read_text(encoding="utf-8"))


_APPROVALS = [("US0101", "APPROVE", QA, BUILDER, "none blocking"),
              ("US0102", "APPROVE", PRODUCT, BUILDER, "none blocking")]


class RetroLearningsTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_the_close_lists_every_approved_learning_not_yet_live(self) -> None:
        """AC1. MUTANTS: only the run's own proposals listed, so a learning written with `add`
        and approved outside any retro goes live unlisted; no Listed-in stamp; the run record
        left without the ids; a proposed, rejected or already-live learning listed."""
        root = self.root
        _project(root, _APPROVALS)
        qa_id = _learning(root, "qa", "A retry loop hides a race", approver=PRODUCT,
                          addresses="round:US0101r2")
        product_id = _learning(root, "product", "Name the user in the criterion",
                               approver=QA, addresses="none: keeps a habit that held")
        proposed = _learning(root, "qa", "Still proposed", state="proposed")
        rejected = _learning(root, "qa", "Turned down", state="rejected", approver=PRODUCT)
        # Already live: listed by an earlier run whose tracked record is sealed and lists it.
        earlier = _learning(root, "product", "Already live", approver=QA, addresses="bug:BG0001")
        _live("persona_memory").set_field(root, earlier, "Listed-in", "RUN-EARLIER")
        _write(root, "sdlc-studio/reports/runs/RUN-EARLIER.json", json.dumps({
            "schema": 1, "run_id": "RUN-EARLIER", "outcome": "goal-reached",
            "signature": {"principal": "Darren"}, "persona_learnings_listed": [earlier]}))

        rc, out, err = _close(root)

        self.assertEqual(0, rc, out + err)
        self.assertRegex(out, r"close \[\d+/\d+\] persona-memory: ok")
        text = _retro(root)
        self.assertEqual(1, text.count("## Persona learnings"), text)
        block = _block(text)
        lines = {i: [ln for ln in block.splitlines() if i in ln]
                 for i in (qa_id, product_id, proposed, rejected, earlier)}
        self.assertEqual(1, len(lines[qa_id]), block)
        self.assertIn(PRODUCT, lines[qa_id][0])
        self.assertIn("round:US0101r2", lines[qa_id][0])
        self.assertIn("(qa)", lines[qa_id][0])
        self.assertEqual(1, len(lines[product_id]), block)
        self.assertIn(QA, lines[product_id][0])
        self.assertIn("none: keeps a habit that held", lines[product_id][0])
        for absent in (proposed, rejected, earlier):
            self.assertEqual([], lines[absent], f"{absent} was listed:\n{block}")
        self.assertEqual(RUN, _fields(root, qa_id).get("listed-in"))
        self.assertEqual(RUN, _fields(root, product_id).get("listed-in"))
        self.assertEqual("RUN-EARLIER", _fields(root, earlier).get("listed-in"))
        self.assertNotIn("listed-in", _fields(root, proposed))
        self.assertEqual([qa_id, product_id], _state(root).get("persona_learnings_listed"))
        record = root / "sdlc-studio" / "reports" / "runs" / f"{RUN}.json"
        self.assertTrue(record.is_file(), "the close filed no run record")
        self.assertEqual([qa_id, product_id],
                         json.loads(record.read_text(encoding="utf-8"))
                         .get("persona_learnings_listed"))

    def test_the_close_names_unlearned_adverse_evidence_and_unattributed_rows(self) -> None:
        """AC2. MUTANTS: every quiet seat named on every close; unattributed rows left out, so an
        empty block reads as a clean run; the finding made blocking; the close reading the
        ledger alone, so a later bug `retro.py seats` charges to a seat names no seat. The bug is
        a real artefact on disk, charged by the seats record's own narrow rule: created in the
        retro's window, citing US0101 and sharing its Affects file, after product approved it."""
        root = self.root
        _project(root, [
            ("US0101", "APPROVE", PRODUCT, BUILDER, "none blocking"),
            ("US0102", "REJECT", QA, BUILDER, "none blocking"),
            ("US0102", "APPROVE", QA, BUILDER, "none blocking"),
            ("US0102", "APPROVE", "a reviewer", BUILDER, "none blocking"),
            ("US0102", "APPROVE", "someone else", BUILDER, "none blocking")])
        _write(root, "sdlc-studio/bugs/BG0002-widget-drops-input.md",
               "# BG0002: widget drops input\n\n> **Status:** Open\n"
               "> **Affects:** src/widget.py\n> **Created:** 2026-11-15\n\n## Summary\n\n"
               "US0101 shipped a widget that drops its input.\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(0, _live("retro").main(
                ["--root", str(root), "seats", "--id", "RETRO0001", "--format", "json"]))
        seats = json.loads(out.getvalue())["seats"]
        self.assertEqual(["BG0002"], [m["bug"] for m in seats["product"]["missed"]],
                         "the seats record does not charge the fixture's bug to product")
        self.assertEqual([], seats["qa"]["missed"])

        rc, out, err = _close(root)

        self.assertEqual(0, rc, out + err)
        self.assertRegex(out, r"close \[\d+/\d+\] persona-memory: ok")
        self.assertNotIn("persona-memory", json.dumps(_state(root).get("close_known_issues")))
        block = _block(_retro(root))
        for where, text in (("close output", out), ("block", block)):
            with self.subTest(where=where):
                named = [ln for ln in text.splitlines() if "adverse evidence" in ln]
                self.assertEqual(1, len(named), text)
                self.assertIn("product", named[0])
                self.assertIn("bug:BG0002", named[0])
                self.assertNotIn("qa", named[0])
                self.assertIn("2 of 5 verdict rows name no seat", text)
        self.assertNotIn("qa", block, "a quiet seat is named on the retro")

    def test_a_reclose_refreshes_the_block_in_place(self) -> None:
        """AC3. MUTANTS: a second block appended; the author's prose rewritten; the block kept
        from the first close, so the new learning is missing."""
        root = self.root
        _project(root, _APPROVALS)
        first = _learning(root, "qa", "A retry loop hides a race", approver=PRODUCT,
                          addresses="round:US0101r2")
        second = _learning(root, "product", "Name the user", approver=QA, addresses="none: kept")
        rc, out, err = _close(root)
        self.assertEqual(0, rc, out + err)
        path = root / "sdlc-studio" / "retros" / "RETRO0001-run.md"
        text = path.read_text(encoding="utf-8")
        head, rest = text.split(BEGIN, 1)
        old, tail = rest.split(END, 1)
        head = head.replace("## Persona learnings", "Prose above.\n\n## Persona learnings\n\n"
                                                    "The author's reading of it.")
        tail = "\n\nProse below, by the author.\n" + tail
        path.write_text(head + BEGIN + old + END + tail, encoding="utf-8")
        third = _learning(root, "qa", "Probe the empty input", approver=PRODUCT,
                          addresses="round:US0102r1")

        rc, out, err = _close(root)

        self.assertEqual(0, rc, out + err)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(BEGIN), text)
        self.assertEqual(1, text.count(END), text)
        self.assertEqual(1, text.count("## Persona learnings"), text)
        new_head, new_rest = text.split(BEGIN, 1)
        new_block, new_tail = new_rest.split(END, 1)
        self.assertEqual(head, new_head, "the author's prose above the block changed")
        self.assertEqual(tail, new_tail, "the author's prose below the block changed")
        for entry_id in (first, second, third):
            self.assertIn(entry_id, new_block)
        self.assertEqual([first, second, third], _state(root).get("persona_learnings_listed"))


if __name__ == "__main__":
    unittest.main()
