"""US0900: a change request can be filed before it is sized.

A CR is a request: `refine` decomposes it and sizes the epic it writes, never the CR. Only
`sprint plan` can demand a size from a CR itself, and only when the CR is planned directly
instead of being decomposed first. Both creators used to refuse a CR filed with no size, no
`Affects` or no criteria. A bug is a delivery unit and keeps its refusal. Driven through each
creator's `main`, the shipped entry point, in throwaway project trees.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

file_finding = loader.load_script("file_finding")
artifact = loader.load_script("artifact")
validate = loader.load_script("validate")
transition = loader.load_script("transition")

_HEADERS = {
    "cr": ("change-requests", "| ID | Title | Status | Priority | Type | Date | Linked Epics |"),
    "bug": ("bugs", "| ID | Title | Status | Severity | Created | Updated |"),
}


def _seed_index(root: Path, type_: str) -> Path:
    rel, header = _HEADERS[type_]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    sep = "|" + " --- |" * (header.count("|") - 1)
    idx = d / "_index.md"
    idx.write_text(f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
                   f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return idx


def _run(main, argv: list[str]) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = main(argv)
        except ValueError as exc:      # `artifact.py`'s `__main__` turns this into exit 1
            return 1, str(exc)
    return rc, out.getvalue() + err.getvalue()


def _written(root: Path, type_: str) -> list[Path]:
    d = root / "sdlc-studio" / _HEADERS[type_][0]
    return sorted(p for p in d.glob("*.md") if p.name != "_index.md")


_CR = ["--type", "cr", "--summary", "the planner cannot say which run owns a unit",
       "--priority", "High"]
_BUG = ["--type", "bug", "--severity", "High", "--summary", "the parser drops a dash",
        "--steps", "run it on a-b", "--fix", "keep the dash"]


class CrFilingTests(unittest.TestCase):

    def test_an_unsized_cr_is_filed_by_both_creators(self) -> None:
        """Mutant: put `cr` back in `GROOMED_TYPES`, or `acs` back in the CR's required
        fields - either one refuses this filing again."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            idx = _seed_index(root, "cr")
            rc, out = _run(file_finding.main,
                           ["file", *_CR, "--title", "filed by the filer", "--root", str(root)])
            self.assertEqual(0, rc, out)
            rc, out = _run(artifact.main,
                           ["new", *_CR, "--title", "created by new", "--root", str(root)])
            self.assertEqual(0, rc, out)
            written = _written(root, "cr")
            self.assertEqual(["CR0001", "CR0002"], [p.name[:6] for p in written])
            index = idx.read_text(encoding="utf-8")
            for p in written:
                text = p.read_text(encoding="utf-8")
                self.assertIn("the planner cannot say which run owns a unit", text)
                self.assertNotIn("**Size:**", text, "a size nobody chose was invented")
                self.assertNotIn("**Affects:**", text, "a footprint nobody chose was invented")
                self.assertNotIn("## Impact", text, "an impact nobody wrote was scaffolded")
                self.assertIn(f"]({p.name})", index, f"{p.name} was written but not indexed")

    def test_an_unsized_bug_is_still_refused(self) -> None:
        """Mutant: drop `bug` from `GROOMED_TYPES` too - the bug is then written unsized."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "parse.py").write_text("", encoding="utf-8")
            idx = _seed_index(root, "bug")
            before = idx.read_text(encoding="utf-8")
            gaps = {"no points": ["--affects", "src/parse.py"], "no affects": ["--points", "3"]}
            for label, extra in gaps.items():
                for name, main, verb in (("file_finding", file_finding.main, "file"),
                                         ("artifact", artifact.main, "new")):
                    with self.subTest(creator=name, gap=label):
                        rc, msg = _run(main, [verb, *_BUG, "--title", f"{name} {label}", *extra,
                                              "--root", str(root)])
                        self.assertNotEqual(0, rc, f"{name} wrote a bug with {label}")
                        self.assertIn("UNGROOMED", msg)
                        self.assertEqual([], _written(root, "bug"))
                        self.assertEqual(before, idx.read_text(encoding="utf-8"))
            # Nothing was allocated: the first bug filed groomed still takes the first id.
            rc, out = _run(file_finding.main,
                           ["file", *_BUG, "--title", "groomed", "--points", "3",
                            "--affects", "src/parse.py", "--root", str(root)])
            self.assertEqual(0, rc, out)
            self.assertEqual(["BG0001"], [p.name[:6] for p in _written(root, "bug")])


def _v3(root: Path) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")


class CrValidatesOnSchemaV3Tests(unittest.TestCase):
    """The refusal is retired, not moved: what the creators write, the validator accepts at
    every status the shipped tools move the CR to. Nothing writes a Size or an Impact onto a
    CR filed without one (`refine` sizes the epic it writes, never the CR), so no status may
    demand them."""

    def _check(self, root: Path) -> tuple[int, str]:
        return _run(validate.main, ["check", "--root", str(root)])

    def test_a_minimal_cr_validates_at_every_status_the_shipped_tools_move_it_to(self) -> None:
        """Mutants: restore the evidence rule from Approved on (the round-2 opening-status
        exemption), or let `artifact.py` scaffold a `{{criterion}}` slot again - either errors
        at Approved. Deleting the evidence rule for every type is caught by the bug control."""
        triager = "Sam Reviewer; human; v1"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v3(root)
            _seed_index(root, "cr")
            for main, verb, title in ((file_finding.main, "file", "filed by the filer"),
                                      (artifact.main, "new", "created by new")):
                rc, out = _run(main, [verb, *_CR, "--title", title, "--root", str(root)])
                self.assertEqual(0, rc, out)
            ids = [p.name.split("-")[0] + "-" + p.name.split("-")[1]
                   for p in _written(root, "cr")]
            self.assertEqual(2, len(ids))
            rc, out = self._check(root)
            self.assertEqual((0, True), (rc, "errors=0" in out), out)
            # Each creator's CR walks both lanes, so neither creator's shape escapes a status.
            for cid in ids:
                for status, extra in (("Approved", ["--triaged-by", triager]),
                                      ("In Progress", [])):
                    with self.subTest(cr=cid, status=status):
                        rc, out = _run(transition.main,
                                       ["set", cid, status, *extra, "--root", str(root)])
                        self.assertEqual(0, rc, out)
                        rc, out = self._check(root)
                        self.assertEqual(0, rc, out)
                        self.assertIn("errors=0", out)
            # A second pair, rejected straight from the inbox.
            before = set(ids)
            for main, verb, title in ((file_finding.main, "file", "filed then rejected"),
                                      (artifact.main, "new", "created then rejected")):
                rc, out = _run(main, [verb, *_CR, "--title", title, "--root", str(root)])
                self.assertEqual(0, rc, out)
            rejected = [p.name.split("-")[0] + "-" + p.name.split("-")[1]
                        for p in _written(root, "cr")]
            rejected = [c for c in rejected if c not in before]
            self.assertEqual(2, len(rejected))
            for cid in rejected:
                with self.subTest(cr=cid, status="Rejected"):
                    rc, out = _run(transition.main, ["set", cid, "Rejected", "--triaged-by",
                                                     triager, "--root", str(root)])
                    self.assertEqual(0, rc, out)
                    rc, out = self._check(root)
                    self.assertEqual(0, rc, out)
                    self.assertIn("errors=0", out)
            # The control: the evidence rule still stands for a bug.
            bug = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            bug.parent.mkdir(parents=True, exist_ok=True)
            bug.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                           "> **Raised-by:** sdlc-studio; agent; v1\n\n"
                           "## Summary\n\nsomething is wrong\n", encoding="utf-8")
            rules = [v["rule"] for v in validate.validate_file(bug, "bug", root)
                     if v["severity"] == "error"]
            self.assertIn("evidence-present", rules)


_SKILL = Path(__file__).resolve().parents[2]
_REPO = _SKILL.parents[2]
# The shipped texts that say who sizes a CR, read from this repository. Includes this module
# and test_two_backlogs.py (both carry the claim in prose comments/docstrings) and the US0128
# story whose revision history once repeated it.
_TRUTH_FILES = (_SKILL / "help" / "cr.md", _SKILL / "reference-scripts-create.md",
                _SKILL / "templates" / "agent-instructions.md",
                _SKILL / "scripts" / "file_finding.py", _REPO / "changelog.d" / "US0900.md",
                Path(__file__).resolve(),
                _SKILL / "scripts" / "tests" / "test_two_backlogs.py",
                _REPO / "sdlc-studio" / "stories" /
                "US0128-undecomposed-drift-cr-creation-size-demand-respect-the.md")


def _prose(path: Path) -> str:
    """The words a reader meets: a Python file's comments and strings, or a whole text file. A
    test module's own module docstring and comments count; its method bodies carry deliberate
    wrong-example fixtures for its own probes, not documentation, so those are excluded."""
    if path.suffix != ".py":
        return path.read_text(encoding="utf-8")
    import tokenize
    with path.open("rb") as fh:
        toks = list(tokenize.tokenize(fh.readline))
    if path.name.startswith("test_"):
        module_doc = next((t.string for t in toks if t.type == tokenize.STRING), "")
        return "\n".join([module_doc] + [t.string for t in toks if t.type == tokenize.COMMENT])
    return "\n".join(tok.string for tok in toks
                     if tok.type in (tokenize.COMMENT, tokenize.STRING))


# Naming the epic anywhere in the sentence normally earns the exemption - true text names it in
# different word orders ("the epic carries the size", "is sized", "sizes the epic"). A sentence
# that puts a size onto the request or its pronoun directly must still be caught even when the
# epic is named too: the object of the sizing verb decides truth here, not the epic's presence.
_SIZES_THE_REQUEST = re.compile(r"\b(?:siz(?:e|es|ed|ing)|gives?)\b\s+(?:it\b|the\s+cr\b)", re.I)


def _false_sizing_claims(text: str) -> list[str]:
    """Each sentence that names `refine` and sizes the CR (or "it") directly, or names a size
    without naming the epic `refine` actually sizes."""
    flat = re.sub(r"[\s#\"'>]+", " ", text)
    sentences = re.split(r"(?<=[.;:!?])\s+", flat)
    return [s for s in sentences
            if re.search(r"\brefine\b", s, re.I) and re.search(r"\bsiz(?:e|es|ed|ing)\b", s, re.I)
            and (_SIZES_THE_REQUEST.search(s) or not re.search(r"\bepic\b", s, re.I))]


class CrDocTruthTests(unittest.TestCase):
    """`refine` sizes the epic it writes, never the CR: no shipped text may say otherwise."""

    def test_no_shipped_text_says_refine_sizes_the_cr(self) -> None:
        """Mutant: restore the round-2 wording, "refine sizes it later" or "`refine` gives it a
        size" - the probe below proves the scan flags both. A third probe pins the tightened
        exemption: naming the epic elsewhere in the sentence must not excuse sizing the CR."""
        for wrong in ("--priority High   # enough to capture it; refine sizes it later",
                      "A CR is a request, and `refine` gives it a size, a footprint and criteria.",
                      "refine sizes the CR as it writes the epic."):
            self.assertTrue(_false_sizing_claims(wrong), f"the scan misses: {wrong}")
        self.assertEqual([], _false_sizing_claims(
            "`refine` decomposes it into an epic and stories, and sizes the epic."))
        for path in _TRUTH_FILES:
            with self.subTest(file=path.name):
                self.assertEqual([], _false_sizing_claims(_prose(path)))


if __name__ == "__main__":
    unittest.main()
