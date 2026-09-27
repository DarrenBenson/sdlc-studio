"""US0961: a verdict recorded against a brief the unit has since outgrown says so.

`critic.py brief` notes each brief it prints under `sdlc-studio/.local/` - the fingerprint, the
seat, the tier and the unit's Affects and criteria as briefed. `critic.py record --brief F` reads
that note back: when the unit's Affects or criteria have changed since F was printed, it records
the row as before and says on stderr that the brief is now G, naming the field and the command
that re-briefs the seat. Advisory only: nothing is refused. Every case drives the shipped entry
point in a throwaway workspace.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import critic  # noqa: E402

AC = "the widget spins clockwise"
WARN = "changed since"


def _story(root: Path, affects: str = "src/widget.py", then: str = AC) -> None:
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True, exist_ok=True)
    (stories / "US0001-x.md").write_text(
        "# US0001: the widget\n\n> **Status:** In Progress\n> **Points:** 2\n"
        f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n"
        f"### AC1: it spins\n\n- **Then** {then}\n- **Verify:** shell true\n",
        encoding="utf-8")


def _project(root: Path) -> None:
    _story(root)
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    (seats / "qa.md").write_text("<!-- role: qa -->\n# Sam - QA seat\n\ncharter\n",
                                 encoding="utf-8")


def _main(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main([*argv, "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _heavy(root: Path, *files: str) -> None:
    """Files `route.estimate` scores as real scope, so declaring them moves the unit's band."""
    for f in files:
        p = root / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("def f():\n" + "    if True:\n        pass\n" * 40, encoding="utf-8")


class RebriefTests(unittest.TestCase):
    def _brief(self, root: Path, *extra: str, tier: str | None = "full") -> str:
        flags = ("--tier", tier) if tier else ()
        rc, _out, err = _main(root, "brief", "--unit", "US0001", "--seat", "qa", *flags, *extra)
        self.assertEqual(0, rc, err)
        m = re.search(r"brief fingerprint: ([0-9a-f]{12})", err)
        self.assertIsNotNone(m, err)
        return m.group(1)

    def _record(self, root: Path, fp: str, verdict: str = "APPROVE",
                issues: str = "") -> str:
        rc, out, err = _main(root, "record", "--unit", "US0001", "--verdict", verdict,
                             "--reviewer", "qa seat", "--author", "dev", "--issues", issues,
                             "--brief", fp, "--tier", "full")
        self.assertEqual(0, rc, out + err)
        row = critic.read_verdicts(root)[-1]
        self.assertEqual((verdict, fp), (row["verdict"], row["brief"]), "the row was not recorded")
        return err

    def _warning(self, err: str) -> str:
        lines = [ln for ln in err.splitlines() if WARN in ln]
        self.assertEqual(1, len(lines), err)
        return lines[0]

    def test_a_widened_unit_is_named_at_record(self) -> None:
        """AC1. MUTANTS: HEAD's silent record; refuse the record (rc 2, no row); name Affects
        whatever changed; print the old fingerprint as the new one; drop the command."""
        for field, edit in (("Affects", {"affects": "src/widget.py, src/extra.py"}),
                            ("criteria", {"then": "the widget spins both ways"})):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                briefed = self._brief(root)
                _story(root, **edit)
                line = self._warning(self._record(root, briefed))
                now = self._brief(root)         # what a re-brief prints today
                self.assertNotEqual(briefed, now)
                self.assertIn(briefed, line)
                self.assertIn(f"now {now}", line)
                self.assertIn(field, line)
                other = "criteria" if field == "Affects" else "Affects"
                self.assertNotIn(other, line)
                self.assertIn("critic.py brief --unit US0001 --seat qa --tier full", line)

    def test_a_derived_tier_is_derived_again(self) -> None:
        """A brief taken with no --tier is re-derived at record: the widening below moves the
        unit's band from light to full, so the brief a re-brief prints is a full one, and the
        command it names pins no tier. MUTANTS: re-render at the noted tier (names the light
        brief's fingerprint); keep `--tier light` in the command (a re-brief that follows it
        records an explicit light tier the full band refuses)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            _heavy(root, "docs/note.md")
            _story(root, affects="docs/note.md")
            self.assertEqual("light", critic.tier_for(root, "US0001"))
            briefed = self._brief(root, tier=None)
            _heavy(root, "src/mod0.py", "src/mod1.py")
            _story(root, affects="docs/note.md, src/mod0.py, src/mod1.py")
            self.assertEqual("full", critic.tier_for(root, "US0001"), "the band did not move")
            line = self._warning(self._record(root, briefed))
            now = self._brief(root, tier=None)
            self.assertEqual(self._brief(root, tier="full"), now)
            self.assertIn(f"now {now}", line)
            self.assertIn("Re-brief the seat: critic.py brief --unit US0001 --seat qa", line)
            self.assertNotIn("--tier", line)

    def test_an_unreadable_note_never_breaks_a_record(self) -> None:
        """A note file with a byte that is not UTF-8 still records, exit 0, and the lines that
        do read still speak. MUTANT: read the notes strictly (UnicodeDecodeError after the row
        is written: a traceback and exit 1)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            briefed = self._brief(root)
            with (root / critic.BRIEF_NOTES_REL).open("ab") as fh:
                fh.write(b"\xff{not json\n")
            _story(root, affects="src/widget.py, src/extra.py")
            self.assertIn(briefed, self._warning(self._record(root, briefed)))

    def test_a_brief_is_never_refused_for_its_note(self) -> None:
        """MUTANT: raise when the note cannot be written (the brief is refused, exit 2)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            (root / critic.BRIEF_NOTES_REL).mkdir(parents=True)   # unwritable as a file
            prior = "VERDICT: REJECT\nISSUES: [new] x\nBLOCKING: x\n"
            for extra, verdict, issues in (((), "REJECT", "[new] x"),
                                           (("--rejoinder", "-"), "APPROVE", "")):
                with self.subTest(extra=extra):
                    with unittest.mock.patch("sys.stdin", io.StringIO(prior)):
                        briefed = self._brief(root, *extra)
                    self.assertNotIn(WARN, self._record(root, briefed, verdict, issues))

    def test_an_unchanged_unit_records_quietly(self) -> None:
        """AC2. MUTANTS: warn on every record; note the rejoinder under its whole-text hash,
        so the control after it is silent; recompute a rejoinder's brief as a base brief, so the
        control names the wrong fingerprint; compare a rejoinder against the base brief."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            self.assertNotIn(WARN, self._record(root, self._brief(root)))
        # A round 2, briefed by rejoinder, records quietly against the footer it printed; the
        # control widens the unit after the rejoinder and must be told the rejoinder's new value.
        for widen in (False, True):
            with self.subTest(widen=widen), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                self._record(root, self._brief(root), "REJECT", "[new] it spins backwards")
                prior = root / "prior.txt"
                prior.write_text("VERDICT: REJECT\nISSUES: [new] it spins backwards\n"
                                 "BLOCKING: it spins backwards\n", encoding="utf-8")
                rejoinder = self._brief(root, "--rejoinder", str(prior))
                if widen:
                    _story(root, affects="src/widget.py, src/extra.py")
                err = self._record(root, rejoinder)
                if not widen:
                    self.assertNotIn(WARN, err)
                    continue
                line = self._warning(err)
                now = self._brief(root, "--rejoinder", str(prior))
                self.assertNotEqual(rejoinder, now)
                self.assertIn(f"now {now}", line)
                self.assertIn("--rejoinder", line)


if __name__ == "__main__":
    unittest.main()
