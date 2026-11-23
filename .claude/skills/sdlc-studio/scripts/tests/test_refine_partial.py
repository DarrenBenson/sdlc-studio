"""BG1452: a request refined in part is not derived terminal when its children resolve.

CR0692 was refined in part (AC1 and AC2 into one epic) and reconcile derived it Complete once
that epic's stories resolved, leaving AC3 and AC4 undelivered. `refine apply --unrefined` now
records the criteria a refine leaves on the request's `Unrefined:` field, and reconcile names
them instead of deriving the request. Each test drives the shipped `refine.py` and
`reconcile.py` entry points over a throwaway two-backlog workspace.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import loader  # noqa: E402 - the canonical way to import a script under test
from lib import sdlc_md  # noqa: E402

refine = loader.load_script("refine")
reconcile = loader.load_script("reconcile")

_CRITERIA = ["the first criterion holds", "the second criterion holds",
             "the third criterion holds", "the fourth criterion holds"]


def _run(main, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RefinePartialTests(unittest.TestCase):

    def setUp(self) -> None:
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root = Path(d.name)
        ws = self.root / "sdlc-studio"
        ws.mkdir()
        (ws / ".config.yaml").write_text("two_backlog:\n  enforce: true\n", encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("", encoding="utf-8")
        body = "".join(f"- [ ] **AC{n}** {c}\n" for n, c in enumerate(_CRITERIA, 1))
        self.cr = ws / "change-requests" / "CR0001-x.md"
        self.cr.parent.mkdir()
        self.cr.write_text("# CR-0001: a request\n\n> **Status:** Approved\n> **Priority:** P1\n"
                           "> **Type:** Improvement\n> **Size:** L\n> **Affects:** src/a.py\n\n"
                           f"## Summary\n\ns\n\n## Acceptance Criteria\n\n{body}\n"
                           "## Impact\n\ni\n", encoding="utf-8")

    # -- helpers -------------------------------------------------------------------------------

    def _refine(self, *extra: str, stories=("First|2", "Second|3")) -> tuple[int, str, str]:
        argv = ["apply", "--request", "CR0001", "--epic-title", "The epic", "--skip-personas"]
        for s in stories:
            argv += ["--story", s]
        return _run(refine.main, *argv, *extra, "--root", str(self.root))

    def _resolve_children(self) -> None:
        """Every epic and story the refines minted, at Done: the request's children resolve."""
        for type_ in ("story", "epic"):
            for p in sdlc_md.artifact_files(type_, self.root):
                text = p.read_text(encoding="utf-8")
                p.write_text(re.sub(r"^> \*\*Status:\*\* .*$", "> **Status:** Done", text,
                                    count=1, flags=re.M), encoding="utf-8")

    def _cr_text(self) -> str:
        return self.cr.read_text(encoding="utf-8")

    def _cr_status(self) -> str:
        return sdlc_md.extract_field(self._cr_text(), "Status")

    def _derivable(self) -> list[dict]:
        return [d for d in reconcile.derivable_request_drift(self.root) if d["id"] == "CR0001"]

    # -- the criterion ---------------------------------------------------------------------------

    def test_a_request_refined_in_part_is_not_derived_and_names_what_is_left(self) -> None:
        code, out, err = self._refine("--unrefined", "AC3, AC4")
        self.assertEqual(code, 0, err)
        self.assertIn("left unrefined: AC3, AC4 - reconcile does not derive it", out)
        self.assertEqual(sdlc_md.extract_field(self._cr_text(), "Unrefined"), "AC3, AC4")
        self.assertEqual(self._derivable(), [])   # children still open: nothing to name yet
        self._resolve_children()
        items = self._derivable()
        self.assertEqual(len(items), 1, items)
        self.assertEqual(items[0]["unrefined"], ["AC3", "AC4"])
        self.assertIn("AC3, AC4", items[0]["blocked_by"])
        self.assertIn("AC3, AC4", items[0]["fix"])
        self.assertIn("refine.py add --request CR0001", items[0]["fix"])
        # detect names the criteria and exits non-zero; apply does not derive the request.
        code, out, _ = _run(reconcile.main, "--root", str(self.root), "detect")
        self.assertEqual(code, 1)
        self.assertRegex(out, r"request-derivable CR0001: .*AC3, AC4")
        before = self._cr_status()
        _run(reconcile.main, "--root", str(self.root), "apply")
        self.assertEqual(self._cr_status(), before)
        self.assertNotEqual(before, "Complete")
        # Nothing to transition on the quiet path a close and apply both walk.
        self.assertEqual([d for d in reconcile.derivable_request_drift(self.root, explain=False)
                          if d["id"] == "CR0001"], [])

    def test_the_same_request_refined_whole_is_derived_complete(self) -> None:
        # The positive control: no --unrefined, the request derives Complete as before.
        code, _out, err = self._refine()
        self.assertEqual(code, 0, err)
        self.assertIsNone(sdlc_md.extract_field(self._cr_text(), "Unrefined"))
        self._resolve_children()
        items = self._derivable()
        self.assertEqual(len(items), 1, items)
        self.assertNotIn("unrefined", items[0])
        self.assertIsNone(items[0]["blocked_by"])
        _run(reconcile.main, "--root", str(self.root), "apply")
        self.assertEqual(self._cr_status(), "Complete")

    def test_refine_add_replaces_the_record_and_none_clears_it(self) -> None:
        self.assertEqual(self._refine("--unrefined", "AC3,AC4")[0], 0)
        add = ["add", "--request", "CR0001", "--epic-title", "More", "--story", "Third|2"]
        code, out, err = _run(refine.main, *add, "--unrefined", "AC4", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertIn("left unrefined: AC4", out)
        self.assertEqual(sdlc_md.extract_field(self._cr_text(), "Unrefined"), "AC4")
        self.assertEqual(1, self._cr_text().count("> **Unrefined:**"))   # replaced in place
        # An add that does not say leaves the record as it is.
        code, _out, err = _run(refine.main, "add", "--request", "CR0001", "--epic-title",
                               "Again", "--story", "Fourth|1", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertEqual(sdlc_md.extract_field(self._cr_text(), "Unrefined"), "AC4")
        self._resolve_children()
        self.assertEqual(self._derivable()[0]["unrefined"], ["AC4"])
        code, out, err = _run(refine.main, "add", "--request", "CR0001", "--epic-title", "Last",
                              "--story", "Fifth|1", "--unrefined", "none", "--root", str(self.root))
        self.assertEqual(code, 0, err)
        self.assertIn("left unrefined: none", out)
        self.assertNotIn("does not derive", out)
        self.assertEqual(sdlc_md.extract_field(self._cr_text(), "Unrefined"), "none")
        self._resolve_children()
        self.assertIsNone(self._derivable()[0]["blocked_by"])

    def test_a_bad_label_is_refused_before_anything_is_minted(self) -> None:
        for spec, why in (("AC5", "has 4 criteria"), ("AC0", "has 4 criteria"),
                          ("3", "criterion labels"), ("AC3,later", "criterion labels"),
                          (",", "names no criterion"), ("none", "criterion labels")):
            with self.subTest(spec=spec):
                code, _out, err = self._refine("--unrefined", spec)
                self.assertEqual(code, 2)
                self.assertIn(why, err)
                self.assertEqual(sdlc_md.artifact_files("epic", self.root), [])
                self.assertIsNone(sdlc_md.extract_field(self._cr_text(), "Unrefined"))

    def test_add_refuses_a_bad_label_and_mints_nothing(self) -> None:
        self.assertEqual(self._refine("--unrefined", "AC4")[0], 0)
        epics = len(sdlc_md.artifact_files("epic", self.root))
        code, _out, err = _run(refine.main, "add", "--request", "CR0001", "--epic-title", "More",
                               "--story", "Third|2", "--unrefined", "AC9", "--root", str(self.root))
        self.assertEqual(code, 2)
        self.assertIn("has 4 criteria", err)
        self.assertEqual(len(sdlc_md.artifact_files("epic", self.root)), epics)
        self.assertEqual(sdlc_md.extract_field(self._cr_text(), "Unrefined"), "AC4")

    def test_a_dry_run_records_nothing(self) -> None:
        code, out, err = self._refine("--unrefined", "AC2,ac2", "--dry-run")
        self.assertEqual(code, 0, err)
        self.assertIn("left unrefined: AC2 - ", out)   # once, whatever case it was given in
        self.assertIsNone(sdlc_md.extract_field(self._cr_text(), "Unrefined"))

    def test_a_single_story_seeds_only_the_criteria_it_refines(self) -> None:
        code, _out, err = self._refine("--unrefined", "AC2,AC4", stories=("Only|3",))
        self.assertEqual(code, 0, err)
        story = sdlc_md.artifact_files("story", self.root)[0].read_text(encoding="utf-8")
        headings = [ln for ln in story.splitlines() if ln.startswith("### AC")]
        self.assertEqual(headings, ["### AC1: the first criterion holds",
                                    "### AC2: the third criterion holds"])

    def test_a_multi_story_epic_carries_only_the_criteria_it_refines(self) -> None:
        self.assertEqual(self._refine("--unrefined", "AC1")[0], 0)
        epic = sdlc_md.artifact_files("epic", self.root)[0].read_text(encoding="utf-8")
        self.assertNotIn(_CRITERIA[0], epic)
        for c in _CRITERIA[1:]:
            self.assertIn(c, epic)

    def test_leaving_every_criterion_seeds_none(self) -> None:
        code, _out, err = self._refine("--unrefined", "AC1,AC2,AC3,AC4", stories=("Only|3",))
        self.assertEqual(code, 0, err)
        story = sdlc_md.artifact_files("story", self.root)[0].read_text(encoding="utf-8")
        self.assertIn(sdlc_md.UNGROOMED_AC_TOKEN, story)
        for c in _CRITERIA:
            self.assertNotIn(c, story)

    def test_a_record_reconcile_cannot_read_still_blocks_derivation(self) -> None:
        # A hand-written value naming no label is not read as "nothing left".
        self.assertEqual(self._refine()[0], 0)
        self.cr.write_text(self._cr_text().replace(
            "> **Status:**", "> **Unrefined:** the last two\n> **Status:**", 1), encoding="utf-8")
        self._resolve_children()
        item = self._derivable()[0]
        self.assertEqual(item["unrefined"], ["the last two"])
        self.assertIn("the last two", item["fix"])

    def test_the_reader_reads_labels_none_and_absence(self) -> None:
        for value, want in (("AC3, AC4", ["AC3", "AC4"]), ("ac2 and AC 5", ["AC2", "AC5"]),
                            ("AC03", ["AC3"]), ("none", []), ("NONE", []), ("", [])):
            with self.subTest(value=value):
                text = f"# CR-0001: x\n\n> **Status:** Approved\n> **Unrefined:** {value}\n"
                self.assertEqual(refine.unrefined_criteria(text), want)
        self.assertEqual(refine.unrefined_criteria("# CR-0001: x\n\n> **Status:** Draft\n"), [])


if __name__ == "__main__":
    unittest.main()
