"""Each seat writes its learning in its own words from a brief carrying its record.

`persona_memory.py learn-brief` frames one seat's card with its own record from `retro.py seats`,
each adverse item with its key, and its live learnings; `propose` records the file the seat
wrote, verbatim, as a proposed learning whose evidence is the ids that record lists, never the
ids the seat's own text names. Every case drives `persona_memory.main` over a throwaway project.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402
import persona_memory as pm  # noqa: E402
from lib import run_state  # noqa: E402

QA = "Sam Eriksson (qa)"
PRODUCT = "Lena Marsh (product)"
HOLDERS = {"engineering": "Dani Okafor", "qa": "Sam Eriksson", "product": "Lena Marsh"}
CARD = ("<!-- role: {role} -->\n# {holder} - {role} seat\n\n## Lens\n\n{role} lens.\n\n"
        "## Non-Negotiables\n\n- {role} never waves through an unpinned criterion.\n\n"
        "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n\n## Authority / Scope\n\n"
        "- {role} may block a unit on its own seat.\n\n## Scenario\n\n{role} scenario.\n")
#: The ledger: qa approved US0001 in round 1 and product's round 2 blocked it on a defect no
#: earlier round cites, so qa carries round:US0001r2; every other batch verdict is product's.
#: Engineering approved US0003, outside the batch, in an earlier run.
ROWS = (("US0003", "APPROVE", "Dani Okafor (engineering)", "2026-09-01", "none"),
        ("US0001", "APPROVE", QA, "2026-10-01", "none"),
        ("US0001", "REJECT", PRODUCT, "2026-10-02",
         "[new] the widget drops a row (scripts/a.py:12)"),
        ("US0001", "APPROVE", PRODUCT, "2026-10-03", "none"),
        ("US0002", "APPROVE", PRODUCT, "2026-10-03", "none"))
FILE_REL = "sdlc-studio/.local/persona-learning/RETRO0002-qa.md"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _bug(root: Path, bid: str, unit: str, created: str) -> None:
    """A later bug `retro.py seats` charges by its narrow rule: it cites `unit`, shares its
    Affects file and falls in RETRO0002's window."""
    _write(root, f"sdlc-studio/bugs/{bid}-a-later-bug.md",
           f"# {bid}: a later bug\n\n> **Status:** Open\n> **Affects:** scripts/a.py\n"
           f"> **Created:** {created}\n\n## Summary\n\n{unit} drops the last row.\n")


def _entry(id_: str, persona: str, title: str, state: str = "approved") -> str:
    """A memory entry; an approved one names the close that listed it, so it stays live where
    a brief carries only a listed learning."""
    listed = "- **Listed-in:** RUN-01SIGNED\n" if state == "approved" else ""
    return (f"\n## {id_}: {title}\n\n- **Persona:** {persona}\n- **Evidence:** US0001\n"
            f"- **Added:** 2026-10-01\n- **Review-by:** 2099-01-01\n- **State:** {state}\n"
            f"{listed}\n{title}, in prose.\n")


class _Fixture(unittest.TestCase):
    """Three seat cards, three stories, RETRO0002 over two, the ledger above, BG0002 charged to
    the US0001 approvals, and one live learning for each of qa and product."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for role, holder in HOLDERS.items():
            _write(self.root, f"sdlc-studio/personas/seats/{role}.md",
                   CARD.format(role=role, holder=holder))
        for uid in ("US0001", "US0002", "US0003"):
            _write(self.root, f"sdlc-studio/stories/{uid}-widget.md",
                   f"# {uid}: widget\n\n> **Status:** Done\n> **Points:** 2\n> **Epic:** EP0001\n"
                   "> **Affects:** scripts/a.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
                   "- **Verify:** shell true\n")
        _bug(self.root, "BG0002", "US0001", "2026-10-05")
        _write(self.root, "sdlc-studio/retros/RETRO0002-run.md",
               "# RETRO0002: run\n\n> **Date:** 2026-10-10\n> **Batch:** US0001, US0002\n")
        _write(self.root, "sdlc-studio/reviews/critic-verdicts.md",
               "# Critic Verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Source | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
               + "".join(f"| {u} | {v} | {r} | - | {d} | - | full | - | {i} |\n"
                         for u, v, r, d, i in ROWS))
        _write(self.root, "sdlc-studio/personas/memory/qa.md",
               "# Persona Memory: qa\n" + _entry("M-0001", "qa", "Qa learned before"))
        _write(self.root, "sdlc-studio/personas/memory/product.md",
               "# Persona Memory: product\n" + _entry("M-0009", "product", "Product learned"))
        # The signed close that listed both approved learnings, so each is live in a brief.
        _write(self.root, "sdlc-studio/reports/runs/RUN-01SIGNED.json",
               '{"schema": 1, "run_id": "RUN-01SIGNED", "outcome": "goal-reached", '
               '"signature": {"principal": "Darren"}, '
               '"persona_learnings_listed": ["M-0001", "M-0009"]}')
        gitutil.git(["init", "-q"], self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = pm.main(["--root", str(self.root), *argv])
        return rc, out.getvalue(), err.getvalue()

    def memory(self, key: str) -> Path:
        return self.root / "sdlc-studio" / "personas" / "memory" / f"{key}.md"

    def entries(self, key: str) -> list[dict]:
        return pm.read_store(self.memory(key))

    def learning_file(self, text: str, rel: str = FILE_REL) -> str:
        _write(self.root, rel, text)
        return str(self.root / rel)

    def propose(self, key: str = "qa", text: str = "Run the round trip myself.\n"):
        path = self.learning_file(text, f"sdlc-studio/.local/persona-learning/{key}.md")
        return self.run_cli("propose", "--persona", key, "--retro", "RETRO0002",
                            "--from-file", path)



class ProposeLearningTests(_Fixture):

    def test_the_learning_brief_carries_only_its_own_seats_record(self) -> None:
        """AC1. Mutants: the whole seats report embedded, so qa reads product's record; the
        adverse items left out; the card or the live learnings not carried."""
        rc, out, err = self.run_cli("learn-brief", "--persona", "qa", "--retro", "RETRO0002")
        self.assertEqual(0, rc, err)
        self.assertIn("qa lens.", out)  # framed by qa's own card
        self.assertIn("You are the qa amigo", out)
        self.assertIn('"key": "round:US0001r1"', out)  # qa's verdict, from the record
        [adverse] = [ln for ln in out.splitlines() if ln.lstrip().startswith("[round:US0001r2]")]
        self.assertIn("the widget drops a row (scripts/a.py:12)", adverse)
        self.assertIn("M-0001 Qa learned before", out)  # qa's live learning
        self.assertRegex(out, r"cannot change[^\n]*Non-Negotiables[^\n]*Authority")
        self.assertIn(f"Write the learning to {FILE_REL}", out)
        self.assertIn(f"persona_memory.py propose --persona qa --retro RETRO0002 --from-file "
                      f"{FILE_REL}", out)
        for foreign in ("round:US0001r3", "round:US0002r1", "US0002", "Product learned",
                        "product lens."):
            self.assertNotIn(foreign, out)

    def test_a_proposal_keeps_the_seats_words_and_the_ledgers_evidence(self) -> None:
        """AC2. Mutants: evidence read from the seat's own text (US0002 r1, US0003); the text
        folded or paraphrased; the run not the one the retro's close names."""
        run_state.write(self.root, {"run_id": "RUN-01TEST01", "outcome": run_state.RUNNING})
        text = ("When I approve a parser change, I run its round trip myself.\n\n"
                "My record is clean: US0002 r1 and US0003 prove it.\n"
                "Keep `$(rm -rf /)` and \"quotes\" as written;  two spaces too.\n")
        before = self.entries("qa")
        rc, out, err = self.run_cli("propose", "--persona", "qa", "--retro", "RETRO0002",
                                    "--from-file", self.learning_file(text))
        self.assertEqual(0, rc, err)
        after = self.entries("qa")
        self.assertEqual(len(before) + 1, len(after))
        new = after[-1]
        self.assertIn(new["id"], out)
        fields = new["fields"]
        self.assertEqual(("qa", "proposed", "RUN-01TEST01", "RETRO0002"),
                         (fields["persona"], fields["state"], fields["run"], fields["retro"]))
        self.assertEqual("US0001 r1, US0001 r2, BG0002", fields["evidence"])
        self.assertEqual(text.strip(), pm.prose_of(new))
        self.assertEqual("When I approve a parser change, I run its round trip myself",
                         new["title"])

    def test_one_open_proposal_per_seat_and_run(self) -> None:
        """AC3. Mutants: one open proposal per seat and run not enforced; a seat with nothing
        on record proposing; a seat whose only item is a later bug refused."""
        qa_before = self.memory("qa").read_bytes()
        rc, _, err = self.propose("engineering")  # no verdict, no unit built, no adverse item
        self.assertEqual(2, rc)
        self.assertIn("engineering has no record in RETRO0002", err)
        self.assertFalse(self.memory("engineering").exists())
        self.assertEqual(qa_before, self.memory("qa").read_bytes())

        rc, out, err = self.propose("qa")
        self.assertEqual(0, rc, err)
        first = self.entries("qa")[-1]["id"]
        held = self.memory("qa").read_bytes()
        rc, _, err = self.propose("qa", "A second thought.\n")
        self.assertEqual(2, rc)
        self.assertIn(f"{first} is still proposed", err)
        self.assertEqual(held, self.memory("qa").read_bytes())

        pm.set_field(self.root, first, "State", "rejected")
        rc, _, err = self.propose("qa", "A better thought.\n")
        self.assertEqual(0, rc, err)
        self.assertEqual("A better thought.", pm.prose_of(self.entries("qa")[-1]))

        _bug(self.root, "BG0003", "US0003", "2026-10-06")  # charged to its earlier approval
        rc, _, err = self.propose("engineering")  # only a later-bug item: it may propose
        self.assertEqual(0, rc, err)
        self.assertEqual("BG0003", self.entries("engineering")[-1]["fields"]["evidence"])

    def test_a_learning_that_would_rewrite_its_own_entry_is_refused(self) -> None:
        """A `## ` line would read back as a new entry, and a field line as the entry's own
        field, so a seat could approve itself or name its own evidence; each is refused before
        anything is written, and a plain list item is kept."""
        held = self.memory("qa").read_bytes()
        for text, said in (("Intro.\n\n## M-0005: smuggled\n\nbody\n", "level-two heading"),
                           ("Intro.\n- **State:** approved\n", "has a field's shape"),
                           ("Intro.\n- **Evidence:** BG0002\n", "has a field's shape")):
            rc, _, err = self.propose("qa", text)
            self.assertEqual(2, rc, text)
            self.assertIn(said, err)
            self.assertEqual(held, self.memory("qa").read_bytes())
        rc, _, err = self.propose("qa", "Intro.\n\n- a plain list item stays\n")
        self.assertEqual(0, rc, err)


if __name__ == "__main__":
    unittest.main()
