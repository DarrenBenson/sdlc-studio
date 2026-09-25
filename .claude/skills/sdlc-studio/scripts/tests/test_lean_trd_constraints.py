"""US0932: a build lane's brief carries the TRD constraints of the components its unit touches.

The TRD's Component Overview table carries a Constraints column. `sprint.py lane brief` reads
the rows whose component names a file the unit's `Affects` declares - matched by whole path
segments, never by substring - and lists each row's component and constraint. When nothing
matches, the TRD has no Constraints column, or there is no TRD, the brief says so in one line and
the dispatch is otherwise unchanged.

Driven through `sprint.main`, the shipped entry point, in throwaway trees.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

SKILL = Path(__file__).resolve().parents[2]
NONE_LINE = "TRD constraints: the TRD records no constraints for these files."
HEADING = "TRD constraints on the components this unit touches:"
SCRIPTS_RULE = "Pure stdlib; every workspace write goes through atomic_write."
SKILL_RULE = "Stays a router; detail loads on demand."


def _trd(constraints: bool = True, rows: tuple[tuple[str, str], ...] | None = None) -> str:
    rows = rows if rows is not None else (("`scripts/` (60+ scripts)", SCRIPTS_RULE),
                                          ("`SKILL.md` router", SKILL_RULE))
    if constraints:
        head = ("| Component | Responsibility | Technology | Constraints |\n"
                "| --- | --- | --- | --- |\n")
        body = "".join(f"| {c} | does a thing | Python | {k} |\n" for c, k in rows)
    else:
        head = "| Component | Responsibility | Technology |\n| --- | --- | --- |\n"
        body = "".join(f"| {c} | does a thing | Python |\n" for c, _k in rows)
    return f"# TRD\n\n## 3. Architecture\n\n### Component Overview\n\n{head}{body}\n## 4. Next\n"


class TrdConstraintsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _unit(self, uid: str, affects: str) -> None:
        d = self.root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: a change\n\n> **Status:** Ready\n> **Affects:** {affects}\n"
            "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
            "- **Verify:** shell true\n", encoding="utf-8")

    def _write_trd(self, text: str | None) -> None:
        p = self.root / "sdlc-studio" / "trd.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        if text is None:
            p.unlink(missing_ok=True)
        else:
            p.write_text(text, encoding="utf-8")

    def _brief(self, uid: str) -> str:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "brief", "--units", uid, "--root", str(self.root)])
        self.assertEqual(0, rc, f"the dispatch was refused: {err.getvalue()}")
        self.assertNotIn("REFUSED", err.getvalue())
        return out.getvalue()

    def test_the_touched_components_constraints_reach_the_brief(self) -> None:
        self._write_trd(_trd())
        self._unit("US0001", ".claude/skills/x/scripts/a.py")
        brief = self._brief("US0001")
        self.assertIn(HEADING, brief)
        self.assertIn(f"`scripts/` (60+ scripts): {SCRIPTS_RULE}", brief)
        self.assertNotIn(SKILL_RULE, brief)
        self.assertNotIn("`SKILL.md`", brief)
        self.assertNotIn(NONE_LINE, brief)
        # A substring match would call `tools/scripts_helper.py` part of `scripts/`, and a file
        # named like the component but outside it (`x/NOTSKILL.md`) part of `SKILL.md`.
        self._unit("US0002", "tools/scripts_helper.py, docs/NOTSKILL.md")
        other = self._brief("US0002")
        self.assertNotIn(SCRIPTS_RULE, other)
        self.assertNotIn(SKILL_RULE, other)
        self.assertIn(NONE_LINE, other)
        # A file component matches its own path at any depth, a glob by its segment.
        self._write_trd(_trd(rows=(("`SKILL.md` router", SKILL_RULE),
                                   ("`help/*.md`", "One file per type."))))
        self._unit("US0003", ".claude/skills/x/SKILL.md, .claude/skills/x/help/story.md")
        both = self._brief("US0003")
        self.assertIn(f"`SKILL.md` router: {SKILL_RULE}", both)
        self.assertIn("`help/*.md`: One file per type.", both)

    def test_no_matching_component_is_stated_not_refused(self) -> None:
        self._unit("US0001", "src/app/main.py")
        # The same unit where a row DOES match: the only difference must be the TRD block.
        self._write_trd(_trd(rows=(("`src/`", "Owns the domain."),)))
        matched = [ln for ln in self._brief("US0001").splitlines()
                   if ln not in (HEADING, "  `src/`: Owns the domain.")]
        cases = {"no matching component": _trd(), "no Constraints column": _trd(False),
                 "no TRD": None,
                 "empty constraint cell": _trd(rows=(("`src/`", "-"),))}
        for label, text in cases.items():
            with self.subTest(label):
                self._write_trd(text)
                lines = self._brief("US0001").splitlines()
                self.assertEqual(1, lines.count(NONE_LINE), lines)
                self.assertNotIn(HEADING, lines)
                self.assertEqual(matched, [ln for ln in lines if ln != NONE_LINE])

    def test_the_template_carries_the_constraints_column(self) -> None:
        template = (SKILL / "templates" / "core" / "trd.md").read_text(encoding="utf-8")
        rows = sprint.trd_component_rows(template)
        self.assertTrue(rows, "the template's Component Overview table carries no Constraints "
                              "column the brief can read")
        self.assertTrue(all(r["constraint"].startswith("{{") for r in rows), rows)
        reference = (SKILL / "reference-trd.md").read_text(encoding="utf-8")
        section = reference.split("\n## Component Constraints {#component-constraints}\n", 1)
        self.assertEqual(2, len(section), "reference-trd.md has no component-constraints section")
        body = section[1].split("\n## ", 1)[0]
        self.assertIn("Constraints", body)
        self.assertIn("lane brief", body)


if __name__ == "__main__":
    unittest.main()
