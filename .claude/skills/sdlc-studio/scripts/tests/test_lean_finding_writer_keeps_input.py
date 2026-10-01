"""US0970: the finding writers keep every criterion and verifier they are handed.

`file_finding.py file` and `artifact.py new` wrote a CR's criteria with no Verify line at exit 0,
paired a surplus or blank verifier with the wrong criterion, wrote an `acs` object as its Python
repr, and refused a new test whose name extends an existing method as a typo. Every case runs the
shipped CLI in a temporary `init run` project holding one small test module.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
FILER = _SCRIPTS / "file_finding.py"
ARTIFACT = _SCRIPTS / "artifact.py"

#: The existing method a new test's name extends, after the premise's own shape.
METHOD = "test_no_amigo_passage_names_a_retired_seat"
TEST_MODULE = ("import unittest\n\n\nclass AmigoNameTests(unittest.TestCase):\n"
               f"    def {METHOD}(self):\n        pass\n\n    def test_b(self):\n        pass\n")
SEL = "pytest tests/test_amigo.py::AmigoNameTests"
#: A bug complete enough to file, less its criteria.
BUG = {"title": "a nit", "severity": "Low", "summary": "s", "steps": "r", "fix": "f",
       "affects": "tests/test_amigo.py", "points": 1}
CR = {"title": "a request", "summary": "s", "priority": "Low"}


def _project(root: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True,
                   capture_output=True)
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True)
    (root / "tests").mkdir()
    (root / "tests" / "test_amigo.py").write_text(TEST_MODULE, encoding="utf-8")
    return root


def _file(root: Path, type_: str, doc: dict) -> subprocess.CompletedProcess:
    path = root / "doc.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return subprocess.run([sys.executable, str(FILER), "file", "--type", type_, "--fields-file",
                           str(path), "--root", str(root), "--format", "json"],
                          cwd=root, capture_output=True, text=True, timeout=300)


def _new(root: Path, type_: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ARTIFACT), "new", "--type", type_, *argv,
                           "--root", str(root)], cwd=root, capture_output=True, text=True,
                          timeout=300)


def _written(root: Path, rel: str) -> list[Path]:
    return sorted((root / "sdlc-studio" / rel).glob("*-*.md"))


class FindingWriterKeepsInputTests(unittest.TestCase):

    def _pairs(self, path: Path, criteria: list[str]) -> list[str]:
        """The line under each criterion, found by its text."""
        lines = path.read_text(encoding="utf-8").splitlines()
        out = []
        for c in criteria:
            at = next(i for i, ln in enumerate(lines) if ln.startswith("- [ ]") and c in ln)
            out.append(lines[at + 1] if at + 1 < len(lines) else "")
        return out

    def test_a_cr_keeps_its_verify_lines(self) -> None:
        """AC1. MUTANTS: (1) HEAD's plain CR checklist - no Verify line from either writer;
        (2) the verifiers written but swapped or all under the first criterion."""
        expect = ["  - **Verify:** shell true", "  - **Verify:** shell echo two"]
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _file(root, "cr", {**CR, "acs": ["given a then b", "given c then d"],
                                   "verify": ["shell true", "shell echo two"]})
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual(expect, self._pairs(Path(json.loads(r.stdout)["path"]),
                                                 ["given a then b", "given c then d"]))
            r = _new(root, "cr", "--title", "another request", "--ac", "given e then f",
                     "--verify", "shell true", "--ac", "given g then h",
                     "--verify", "shell echo two")
            self.assertEqual(0, r.returncode, r.stderr)
            made = next(p for p in _written(root, "change-requests") if "another-request" in p.name)
            self.assertEqual(expect, self._pairs(made, ["given e then f", "given g then h"]))

    def test_an_unpaired_verifier_is_named_not_mis_paired(self) -> None:
        """AC2. MUTANTS: (1) no pairing check - exit 0 with the verifier under the wrong
        criterion; (2) the surplus refused but a blank entry still skipped, shifting the rest;
        (3) the check run after the write - the artefact is left behind."""
        cases = {"surplus": (["given a then b"], ["shell true", "shell echo spare"],
                             "shell echo spare"),
                 "blank": (["given a then b", "given c then d"], ["", "shell echo two"],
                           "verify[1]")}
        for name, (acs, verify, named) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as d:
                root = _project(Path(d))
                r = _file(root, "bug", {**BUG, "acs": acs, "verify": verify})
                self.assertNotEqual(0, r.returncode, r.stdout)
                self.assertIn(named, r.stderr)
                argv = [a for ac, v in zip(acs, verify) for a in ("--ac", ac, "--verify", v)]
                argv += [a for v in verify[len(acs):] for a in ("--verify", v)]
                r = _new(root, "cr", "--title", "another request", *argv)
                self.assertNotEqual(0, r.returncode, r.stdout)
                self.assertIn(named, r.stderr)
                self.assertEqual([], _written(root, "bugs") + _written(root, "change-requests"))

    def test_criterion_objects_are_read_as_text_and_verify(self) -> None:
        """AC3. MUTANTS: (1) HEAD's `str(obj)` - the repr is the criterion; (2) the text read but
        the object's verify dropped."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _file(root, "bug", {**BUG, "acs": [
                {"id": "AC1", "text": "Given x then y", "verify": f"{SEL}::test_b"}]})
            self.assertEqual(0, r.returncode, r.stderr)
            text = Path(json.loads(r.stdout)["path"]).read_text(encoding="utf-8")
        self.assertIn(f"- [ ] **AC1** Given x then y\n  - **Verify:** {SEL}::test_b\n", text)
        self.assertNotIn("{'id'", text)

    def test_an_extended_test_name_files_as_new(self) -> None:
        """AC4. MUTANTS: (1) HEAD's near-miss refusal of the extended name; (2) every node of a
        collected class filed as new - the one-letter typo is no longer refused."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(Path(d))
            r = _file(root, "bug", {**BUG, "acs": ["given a then b"],
                                    "verify": [f"{SEL}::{METHOD}_in_slug_form"]})
            self.assertEqual(0, r.returncode, r.stderr)
            typo = _file(root, "bug", {**BUG, "title": "another nit", "acs": ["given a then b"],
                                       "verify": [f"{SEL}::{METHOD[:-1]}"]})
            self.assertNotEqual(0, typo.returncode, typo.stdout)
            self.assertIn("did you mean", typo.stderr)


    def test_artifact_keeps_a_criterion_objects_blank_verifier_in_place(self) -> None:
        """Round 1's repro. MUTANTS: (1) artifact's `_verifiers_of` skipping blanks - B's
        verifier is written under A, at exit 0, for a CR and a bug alike; (2) a story writing an
        empty `Verify:` line for the blank slot."""
        doc = {"acs": [{"text": "crit A"}, {"text": "crit B", "verify": "shell echo B"}]}
        for type_, extra in (("cr", {}), ("bug", {"severity": "Low", "points": 1,
                                                   "affects": "tests/test_amigo.py",
                                                   "steps": "r", "fix": "f"}),
                            ("story", {})):
            with self.subTest(type_), tempfile.TemporaryDirectory() as d:
                root = _project(Path(d))
                if type_ == "story":
                    r = _new(root, "epic", "--title", "an epic", "--format", "json")
                    extra = {"epic": json.loads(r.stdout)["id"]}
                path = root / "doc.json"
                path.write_text(json.dumps({**doc, **extra, "title": f"a {type_}",
                                            "summary": "s"}), encoding="utf-8")
                r = _new(root, type_, "--fields-file", str(path))
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                made = _written(root, {"cr": "change-requests", "bug": "bugs",
                                       "story": "stories"}[type_])[0]
                text = made.read_text(encoding="utf-8")
                lines = text.splitlines()
                a = next(i for i, ln in enumerate(lines) if "crit A" in ln)
                b = next(i for i, ln in enumerate(lines) if "crit B" in ln)
                self.assertNotIn("Verify", lines[a + 1], text)
                self.assertEqual("  - **Verify:** shell echo B", lines[b + 1], text)

    def test_a_near_miss_of_a_longer_sibling_is_refused_whatever_it_extends(self) -> None:
        """Round 1's regression. MUTANTS: (1) `_extends_a_sibling` judging only the prefix - a
        typo of `test_names_a_retired_seat` that extends `test_names` files as a new test;
        (2) the exemption granted with no sibling extended - a node hung below a collected
        test (`::test_b::extra`) files as new."""
        module = ("import unittest\n\n\nclass NameTests(unittest.TestCase):\n"
                  "    def test_names(self):\n        pass\n\n"
                  "    def test_names_a_retired_seat(self):\n        pass\n")
        for typo in ("test_names_a_retried_seat", "test_names_a_retired_seats",
                     "test_names::extra"):
            with self.subTest(typo), tempfile.TemporaryDirectory() as d:
                root = _project(Path(d))
                (root / "tests" / "test_names.py").write_text(module, encoding="utf-8")
                r = _file(root, "bug", {**BUG, "acs": ["given a then b"], "verify": [
                    f"pytest tests/test_names.py::NameTests::{typo}"]})
                self.assertNotEqual(0, r.returncode, r.stdout)
                self.assertIn("did you mean", r.stderr)


if __name__ == "__main__":
    unittest.main()
