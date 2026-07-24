"""Attribution for the corpus lint lane (US0358).

The corpus carries hundreds of findings that predate any given change. A lane that
reports the total and stops is a lane nobody can act on: it blocks whoever next touches
a file rather than whoever introduced the defect, which is the exact failure the lane was
built to end. So every finding is classified against a baseline revision - the same
enumeration and the same rule set, run at that revision - and the summary names the count
of each class.

Two things are load-bearing and both are asserted against real markdownlint runs over
real git revisions rather than canned finding sets:

* a finding is fingerprinted by file, rule and offending text, NOT by line, so unrelated
  content inserted above a pre-existing finding does not relabel it as introduced; and
* a baseline that cannot be read yields `unattributed`, never `pre-existing`. Failing the
  other way would quietly forgive every finding on a shallow clone.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lint_corpus = _load(REPO / "tools" / "lint_corpus.py", "lint_corpus_attr")
gitutil = _load(REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py", "_lca_gitutil")

LINTER = lint_corpus.find_linter(REPO)
ROOT_CONFIG = (REPO / ".markdownlint.json").read_text(encoding="utf-8")

#: One MD056 finding: the cell's unescaped pipes read as extra columns.
PIPE_TABLE = (
    "| Outcome | Meaning |\n"
    "| --- | --- |\n"
    "| achieved|partial|missed | the three sprint verdicts |\n"
)


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-q", "-m", message], cwd=root)
    return gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()


def _seed(root: Path) -> None:
    gitutil.git(["init", "-q", "-b", "main"], cwd=root)
    _write(root, ".markdownlint.json", ROOT_CONFIG)


def _by_status(result: dict) -> dict[str, list]:
    out: dict[str, list] = {"introduced": [], "pre-existing": [], "unattributed": []}
    for f in result["findings"]:
        out[f["status"]].append(f)
    return out


class AttributionTests(unittest.TestCase):
    def test_a_finding_absent_from_the_baseline_is_reported_as_introduced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root)
            # The baseline already carries a defect, in a file this change never touches.
            _write(root, "old.md", "# Old\n\n" + PIPE_TABLE)
            base = _commit(root, "baseline")
            # The change introduces a second one, in a new file.
            _write(root, "new.md", "# New\n\n" + PIPE_TABLE)
            _commit(root, "change")

            result = lint_corpus.analyse(root, baseline=base, linter=LINTER)

            self.assertTrue(result["baseline"]["readable"], result["baseline"])
            md056 = {f["path"]: f["status"] for f in result["findings"] if f["rule"] == "MD056"}
            self.assertEqual(md056, {"old.md": "pre-existing", "new.md": "introduced"})
            # The counts are over every finding, not only MD056: the same row also trips
            # MD060 twice per file, so the totals are real numbers and not a stand-in.
            by = _by_status(result)
            self.assertEqual(result["counts"]["introduced"], len(by["introduced"]))
            self.assertEqual(result["counts"]["pre_existing"], len(by["pre-existing"]))
            self.assertEqual(result["counts"]["unattributed"], 0)
            self.assertEqual(result["counts"]["introduced"],
                             result["counts"]["pre_existing"],
                             "the two files carry the identical defect, so the two classes "
                             "must come out equal")
            self.assertGreater(result["counts"]["introduced"], 0)

            summary = lint_corpus.render(result).splitlines()[0]
            self.assertIn(f"{result['counts']['introduced']} introduced", summary)
            self.assertIn(f"{result['counts']['pre_existing']} pre-existing", summary)
            self.assertEqual(lint_corpus.exit_code(result), 1,
                             "an introduced finding must fail the lane")

    def test_line_drift_alone_does_not_reclassify_a_pre_existing_finding(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root)
            _write(root, "doc.md", "# Doc\n\n" + PIPE_TABLE)
            base = _commit(root, "baseline")
            baseline_line = lint_corpus.lint_corpus(root, linter=LINTER)
            offending = [f for f in baseline_line if f.rule == "MD056"][0].line
            self.assertEqual(offending, 5)

            # Unrelated prose inserted ABOVE the defect. The defect itself is byte-identical.
            _write(root, "doc.md",
                   "# Doc\n\nOne.\n\nTwo.\n\nThree.\n\nFour.\n\n" + PIPE_TABLE)
            _commit(root, "insert prose above")

            result = lint_corpus.analyse(root, baseline=base, linter=LINTER)

            moved = [f for f in result["findings"] if f["rule"] == "MD056"]
            self.assertEqual(len(moved), 1)
            self.assertEqual(moved[0]["line"], offending + 8,
                             "the finding did move - if it did not, this test proves nothing")
            self.assertEqual(moved[0]["status"], "pre-existing")
            self.assertEqual(result["counts"]["introduced"], 0,
                             f"line drift alone was reported as introduced: "
                             f"{_by_status(result)['introduced']}")
            self.assertEqual(lint_corpus.exit_code(result), 0,
                             "a run that introduced nothing must not fail the lane")


    def test_a_second_copy_of_an_existing_finding_is_introduced(self) -> None:
        # Set membership would call all three pre-existing, because an identical finding
        # was already there. Attribution is COUNTED: two at the baseline and three now
        # means one was introduced, and it is the third row that has to be fixed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root)
            bad_row = "| achieved|partial|missed | verdicts |\n"
            header = "# Doc\n\n| Outcome | Meaning |\n| --- | --- |\n"
            _write(root, "doc.md", header + bad_row * 2)
            base = _commit(root, "baseline")
            _write(root, "doc.md", header + bad_row * 3)
            _commit(root, "one more bad row")

            result = lint_corpus.analyse(root, baseline=base, linter=LINTER)

            md056 = [f for f in result["findings"] if f["rule"] == "MD056"]
            self.assertEqual(len(md056), 3)
            self.assertEqual([f["status"] for f in md056].count("introduced"), 1)
            self.assertEqual([f["status"] for f in md056].count("pre-existing"), 2)


class BaselineDegradationTests(unittest.TestCase):
    def test_an_unreadable_baseline_reports_unattributed_rather_than_pre_existing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root)
            _write(root, "doc.md", "# Doc\n\n" + PIPE_TABLE)
            _commit(root, "baseline")
            total = len(lint_corpus.lint_corpus(root, linter=LINTER))
            self.assertGreater(total, 0, "the fixture must carry findings to classify")

            missing = "0123456789abcdef0123456789abcdef01234567"
            result = lint_corpus.analyse(root, baseline=missing, linter=LINTER)

            self.assertFalse(result["baseline"]["readable"])
            self.assertEqual(result["counts"]["unattributed"], total)
            self.assertEqual(result["counts"]["pre_existing"], 0,
                             "an unreadable baseline must forgive nothing")
            self.assertEqual(result["counts"]["introduced"], 0)
            self.assertEqual({f["status"] for f in result["findings"]}, {"unattributed"})

            text = lint_corpus.render(result)
            self.assertIn("baseline could not be read", text)
            self.assertIn(missing, text, "the report must name the ref it could not read")
            self.assertEqual(lint_corpus.exit_code(result), 1,
                             "findings nobody can attribute must not pass silently")

    def test_no_baseline_at_all_is_the_same_unreadable_verdict(self) -> None:
        # A repo with no tags and no origin: nothing to derive a baseline from. The lane
        # must say so rather than call every finding pre-existing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root)
            _write(root, "doc.md", "# Doc\n\n" + PIPE_TABLE)
            _commit(root, "only commit")

            result = lint_corpus.analyse(root, baseline=None, linter=LINTER)

            self.assertFalse(result["baseline"]["readable"])
            self.assertEqual(result["counts"]["pre_existing"], 0)
            self.assertEqual({f["status"] for f in result["findings"]}, {"unattributed"})
            self.assertIn("baseline could not be read", lint_corpus.render(result))


if __name__ == "__main__":
    unittest.main()
