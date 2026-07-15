"""The pseudo-`Verify:` refusal (BG0132).

Only a STORY carries an executable check - its canonical `- **Verify:**` line is the one thing
verify_ac runs. A CR/bug acceptance criterion is prose, so a command-shaped `Verify: <cmd>`
written into it is executed by nothing: a wrong command is a permanent false red, and a loose one
(a grep that matches unrelated prose) is a false green on a feature nobody built.

These tests exercise BEHAVIOUR through the public paths: the two creators must REFUSE such a
criterion (and write nothing), must ACCEPT the same criterion restated as an outcome, and the
validator must SURFACE the instances already on disk as warnings. They never assert that a string
is present in a source file - which is the exact false-green this bug is about.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load("file_finding")
artifact = _load("artifact")
validate = _load("validate")

# The two real instances from the field (BG0132), and their honest rewrites.
FALSE_GREEN = ("sprint.py reads the Effort field. "
               "Verify: rg -qi 'effort' .claude/skills/sdlc-studio/scripts/sprint.py")
FALSE_RED = "The env var is documented. Verify: `rg -q 'REQUIRE_CHECKSUM' README.md`"
HONEST = ("sprint.py reads the CR Effort field and sizes the unit by it, rather than falling "
          "back to the flat default")

# Sized for BOTH creators: a T-shirt `size` (the CR filer's field - a CR is a request) and a
# legacy `points` (the low-level `artifact new` path still writes points onto a CR, tolerated).
# Each creator reads the field it owns; these tests assert AC/validator behaviour, not the size.
CR_FIELDS = {"priority": "P3", "ctype": "Improvement", "summary": "s",
             "impact": "every sprint plan", "size": "M", "points": 5,
             "affects": "scripts/sprint.py", "date": "2026-07-14"}


def _seed_cr_index(root: Path) -> Path:
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    header = "| ID | Title | Status | Priority | Type | Date | Linked Epics |"
    sep = "|" + " --- |" * (header.count("|") - 1)
    (d / "_index.md").write_text(
        "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 0 |\n"
        f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return d / "_index.md"


class DetectorTests(unittest.TestCase):
    """What the detector matches, and what it deliberately lets through."""

    def test_matches_command_shaped_verify(self) -> None:
        for text in (
            "x. Verify: rg -qi 'effort' sprint.py",              # the false green
            "x. Verify: `rg -q 'REQUIRE_CHECKSUM' README.md`",   # the false red
            "x. Verify: `test -f .claude/skills/sdlc-studio/help/audit.md`",
            "x. Verify: python3 -m unittest discover -s scripts/tests -k gate",
            "x. Verify: ./install.sh --local",
            "x  - **Verify:** rg -q retro scripts/gate.py",      # a faked canonical line
            "x. verify: test -f a.md && rg -q b c.md",
            "x. Verify: python3 scripts/lessons.py recall | jq -e '.matches'",
            "x. Verify: ! rg -q 'review generate' README.md",    # a negated command still runs
        ):
            with self.subTest(text=text):
                self.assertIsNotNone(ff.pseudo_verify(text), "should be refused")

    def test_lets_honest_prose_through(self) -> None:
        for text in (
            HONEST,
            "Verify the operator sees the banner",               # the word, used honestly
            "Verify: the operator sees a red banner naming the file",
            "The verifier reports the AC as manual rather than failed",
            "Verify: manual - a reviewer reads the rendered page",
            "Verify: test that a stale LATEST.md fails the close",   # 'test' as English
            "Verify: make the over-budget case visible at plan time",
            "The AC carries no Verify line at all, and conformance says so",
        ):
            with self.subTest(text=text):
                self.assertIsNone(ff.pseudo_verify(text), "honest prose must be allowed")


class FilerRefusalTests(unittest.TestCase):
    """`file_finding.py` - the primary agent path."""

    def test_refuses_a_cr_whose_ac_carries_a_command_shaped_verify(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_cr_index(root)
            with self.assertRaises(ValueError) as ctx:
                ff.file_finding(root, "cr", "sizing", {**CR_FIELDS, "acs": [FALSE_GREEN]})
            msg = str(ctx.exception)
            self.assertIn("rg -qi", msg)          # names the offending command
            self.assertIn("story", msg.lower())   # says where executable proof belongs
            # nothing written, no id burned, no index row
            self.assertEqual(
                sorted(p.name for p in (root / "sdlc-studio" / "change-requests").iterdir()),
                ["_index.md"])
            self.assertIn("| **Total** | **0** |", idx.read_text(encoding="utf-8"))

    def test_accepts_the_same_cr_with_an_honest_prose_criterion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_cr_index(root)
            res = ff.file_finding(root, "cr", "sizing", {**CR_FIELDS, "acs": [HONEST]})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("- [ ] sprint.py reads the CR Effort field", body)

    def test_refusal_is_per_criterion_not_per_word(self) -> None:
        # A criterion that uses the word 'verify' as an outcome ("the operator sees ...") is
        # accepted; only the command shape is refused.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_cr_index(root)
            res = ff.file_finding(root, "cr", "banner",
                                  {**CR_FIELDS,
                                   "acs": ["Verify the operator sees the banner",
                                           "Verify: the run refuses and names the file"]})
            self.assertTrue(Path(res["path"]).exists())

    def test_refuses_a_bug_criterion_too(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            with self.assertRaises(ValueError):
                ff.file_finding(root, "bug", "a defect",
                                {"severity": "High", "summary": "s", "steps": "r", "fix": "f",
                                 "acs": [FALSE_RED]})


class CreatorRefusalTests(unittest.TestCase):
    """`artifact.py` - the second creation path. LL0016: both paths must agree on what a CR/bug
    acceptance criterion MEANS, or the refusal is only an inconvenience to whoever picked the
    guarded door."""

    def test_new_refuses_the_pseudo_verify_criterion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_cr_index(root)
            with self.assertRaises(ValueError):
                artifact.new(root, "cr", "sizing", {**CR_FIELDS, "acs": [FALSE_GREEN]})
            self.assertEqual(
                sorted(p.name for p in (root / "sdlc-studio" / "change-requests").iterdir()),
                ["_index.md"])

    def test_new_accepts_the_honest_criterion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_cr_index(root)
            res = artifact.new(root, "cr", "sizing", {**CR_FIELDS, "acs": [HONEST]})
            self.assertIn("sizes the unit by it",
                          Path(res["path"]).read_text(encoding="utf-8"))

    def test_batch_aborts_before_writing_anything(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_cr_index(root)
            items = [{"title": "clean", **CR_FIELDS, "acs": [HONEST]},
                     {"title": "dirty", **CR_FIELDS, "acs": [FALSE_GREEN]}]
            with self.assertRaises(ValueError) as ctx:
                artifact.new_batch(root, "cr", items)
            self.assertIn("batch item 2", str(ctx.exception))
            self.assertEqual(  # all-or-nothing: item 1 is not on disk either
                sorted(p.name for p in (root / "sdlc-studio" / "change-requests").iterdir()),
                ["_index.md"])

    def test_a_story_verify_line_is_untouched(self) -> None:
        # The guard is CR/bug-only. A story's --verify is the REAL check: it must still be
        # written, verbatim, and must still be runnable by verify_ac.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "epics").mkdir(parents=True)
            (root / "sdlc-studio" / "epics" / "EP0001-e.md").write_text(
                "# EP-0001: e\n\n> **Status:** Planned\n", encoding="utf-8")
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            res = artifact.new(root, "story", "sizing", {
                "epic": "EP0001", "acs": ["the Effort field is read"],
                "verify": ["rg -q 'Effort' scripts/sprint.py"]})
            body = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("- **Verify:** rg -q 'Effort' scripts/sprint.py", body)


class ValidatorWarningTests(unittest.TestCase):
    """The instances already on disk are surfaced, not silently tolerated."""

    def _cr(self, root: Path, ac: str) -> Path:
        p = root / "sdlc-studio" / "change-requests" / "CR0001-x.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            "# CR-0001: x\n\n> **Status:** Proposed\n> **Priority:** P3\n\n## Summary\n\n"
            "The old AC said `Verify: rg -qi effort sprint.py`, which passes on prose.\n\n"
            "## Impact\n\nevery sprint plan.\n\n> **Points:** 3\n\n"
            f"## Acceptance Criteria\n\n- [ ] {ac}\n\n## Revision History\n\n"
            "| Date | Author | Change |\n| --- | --- | --- |\n| 2026-07-14 | a | Raised |\n",
            encoding="utf-8")
        return p

    def test_pseudo_verify_ac_is_reported_as_a_warning_naming_the_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._cr(Path(d), FALSE_GREEN)
            hits = [v for v in validate.validate_file(p, "cr", Path(d))
                    if v["rule"] == "pseudo-verify"]
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["severity"], "warning")  # never an error: pre-existing
            self.assertEqual(hits[0]["file"], str(p))
            self.assertIn("line 18", hits[0]["message"])      # names the line
            self.assertIn("rg -qi", hits[0]["message"])

    def test_honest_prose_ac_is_not_warned_and_summary_prose_is_ignored(self) -> None:
        # The Summary of this fixture DISCUSSES a pseudo-Verify (as BG0132 itself does). Only
        # the acceptance criteria are judged - a bug report that quotes the pattern is not a
        # bug report that commits it.
        with tempfile.TemporaryDirectory() as d:
            p = self._cr(Path(d), HONEST)
            self.assertEqual(
                [v for v in validate.validate_file(p, "cr", Path(d))
                 if v["rule"] == "pseudo-verify"], [])

    def test_a_story_verify_line_is_never_warned(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sdlc-studio" / "stories" / "US0001-x.md"
            p.parent.mkdir(parents=True)
            p.write_text("# US-0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                         "- **AC1:** it works\n  - **Verify:** rg -q x scripts/sprint.py\n",
                         encoding="utf-8")
            self.assertEqual(
                [v for v in validate.validate_file(p, "story", Path(d))
                 if v["rule"] == "pseudo-verify"], [])


if __name__ == "__main__":
    unittest.main()
