"""BG1625: the kept mutant list `self-check record --mutants-from` writes, and the selectors the
author self-check names.

Four defects from both seats' reviews of the recorded runner report:

- a Verify line filtering with `-k 'a or b'` printed `'a`, `or` and `b'` as pytest selectors in
  the author self-check section `critic.py brief` prints. It now names the files and node ids
  the line selects, and the `-k` (or `-m`) expression by name as one that names no test;
- a kept list that could not be written still left its self-check row added, while the message
  said nothing was written. The list is written before the row, and a failure refuses the
  record with no row;
- a malformed kept list crashed the brief. It is refused with an error naming the file;
- the kept list stored the report's absolute local path in a committed file. It stores the
  path relative to the root, or the report's name alone when it lies outside it.

Each case drives `critic.py` through its entry point, or the function the brief calls, in a
throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")
mutation = loader.load_script("mutation")
AFFECTS = "src/widget.py, tests/test_widget.py, changelog.d/US0101.md"
TEST = "tests/test_widget.py::test_w"
CLAIMS = [{"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE"},
          {"surface": "changelog.d/US0101.md", "claim": "w is new", "ruling": "TRUE"}]


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _project(root: Path, verify: str = "shell true") -> None:
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "tests/test_widget.py", "def test_w():\n    assert True\n")
    _write(root, "sdlc-studio/personas/seats/qa.md",
           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
           "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           f"# US0101: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Affects:** {AFFECTS}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           f"- **Verify:** {verify}\n")


def _report(path: Path, **overrides) -> Path:
    """A runner report of the current shape: one mutant, killed."""
    data = {"kind": "mutation-edits", "version": mutation.EDITS_REPORT_VERSION, "unit": "US0101",
            "mutants": [{"mutant": "w returns 2", "file": "src/widget.py", "old": "return 1",
                         "new": "return 2", "test": TEST, "result": "killed", "answer": ""}],
            "counts": {"killed": 1, "survived": 0}, **overrides}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _record_from(root: Path, report: Path) -> subprocess.CompletedProcess:
    claims = _write(root, "sdlc-studio/.local/claims.json", json.dumps(CLAIMS))
    return _cli(root, "self-check", "record", "--unit", "US0101", "--claims", str(claims),
                "--mutants-from", str(report))


class CriticReplaySelectorTests(unittest.TestCase):

    def test_a_k_expression_is_named_never_split_into_selectors(self) -> None:
        """AC1. Mutants: the Verify line split on whitespace, so `'add`, `or` and `sign'` are
        printed as selectors; the `-k` value read as a selector; the expression dropped without
        being named. The file the line selects from is still named."""
        for verify, expr in (("pytest tests/test_widget.py -k 'add or sign'", "-k 'add or sign'"),
                             ('pytest -m "slow and not flaky" tests/test_widget.py',
                              "-m 'slow and not flaky'")):
            with self.subTest(verify=verify), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, verify)
                text = critic.author_self_check(root, "US0101")
                line = next(ln for ln in text.splitlines() if "Verify selectors" in ln)
                named = line.split("Verify selectors: ", 1)[1]
                self.assertEqual("tests/test_widget.py", named.split(" (", 1)[0], line)
                self.assertIn(f"tests/test_widget.py ({expr} filters by expression and names no "
                              f"test: give each mutant the node id of a test it selects)", line)

    def test_node_ids_and_options_with_values_are_read_as_pytest_reads_them(self) -> None:
        """Node ids and a bare directory are named as written; a plain option and the value of
        an option that takes the next word (`-p no:cacheprovider`, `--deselect <id>`, `-n 4`)
        are not selectors, and a line with no filter names no expression. Mutants: every word
        not an option read as a target, so an option's value is printed as a selector; only a
        word naming a path read as one, so a bare directory is dropped."""
        self.assertEqual((["tests/a.py::T::test_x", "tests/b.py"], []),
                         critic.pytest_targets(
                             "pytest -q -p no:cacheprovider tests/a.py::T::test_x tests/b.py"))
        self.assertEqual((["tests/a.py"], ["-k 'x or y'"]),
                         critic.pytest_targets("pytest tests/a.py -k'x or y'"))
        self.assertEqual((["tests/a.py"], []),
                         critic.pytest_targets("pytest tests/a.py -k"),
                         "a dangling -k with no value")
        self.assertEqual((["tests/a.py"], []), critic.pytest_targets("pytest 'tests/a.py"),
                         "an unbalanced quote is read word by word")
        self.assertEqual((["tests"], []), critic.pytest_targets("pytest -q tests"),
                         "a directory named bare is a target")
        self.assertEqual((["tests/a.py", "tests"], []), critic.pytest_targets(
            "pytest tests/a.py -n 4 --deselect tests/a.py::T::slow --tb=short tests"),
                         "an option's value given as the next word is not a target")
        self.assertEqual(([], []), critic.pytest_targets("python3 -m pytest tests/a.py"),
                         "a line not run as pytest names nothing")

    def test_a_cluster_of_short_flags_is_read_as_pytest_reads_it(self) -> None:
        """A short flag cluster (`-qk`, `-vm`) is each letter in turn, as pytest's argparse reads
        it, until one that takes a value, whose value is the rest of the word or else the next
        word; `-r` is pytest's own value option. One `=` directly after that letter is dropped,
        as argparse drops it (`-k=add` filters by `add`, `-k==add` by `=add`; Python 3.10's keeps
        it in a cluster such as `-qk=add`), and `-k=` is an empty value that leaves the next word
        a target. A long option written `--opt=value` carries its value, so the next word stays a
        target. Mutants: a cluster ending in `k` skipped as a plain option, so its expression's
        words print as selectors; `-r` left out of the value options, so its value prints as one;
        the letters read on past the one that took the rest of the word, so `-km` takes the next
        word as an `-m` expression; the `=` kept, so `-k=add` names `=add`; every leading `=`
        dropped; the `=` dropped only after a lone `-k`, never in a cluster; `-k=` taking the
        next word; a long `--opt=value` taking the next word as well."""
        for verify, want in (
                ("pytest tests/a.py -qk 'add or sign'", (["tests/a.py"], ["-k 'add or sign'"])),
                ("pytest -vm 'slow and not flaky' tests/a.py",
                 (["tests/a.py"], ["-m 'slow and not flaky'"])),
                ("pytest tests/a.py -qkadd", (["tests/a.py"], ["-k add"])),
                ("pytest tests/a.py -r a -k add", (["tests/a.py"], ["-k add"])),
                ("pytest -rA tests/a.py", (["tests/a.py"], [])),
                ("pytest -km tests/a.py", (["tests/a.py"], ["-k m"])),
                ("pytest -qx tests/a.py", (["tests/a.py"], [])),
                ("pytest -- tests/a.py", (["tests/a.py"], [])),
                ("pytest tests/a.py -rA -k=add", (["tests/a.py"], ["-k add"])),
                ("pytest -qk='add or sign' tests/a.py", (["tests/a.py"], ["-k 'add or sign'"])),
                ("pytest tests/a.py -k==add", (["tests/a.py"], ["-k =add"])),
                ("pytest -k= tests/a.py", (["tests/a.py"], [])),
                ("pytest -p=no:cacheprovider tests/a.py", (["tests/a.py"], [])),
                ("pytest --deselect=tests/a.py::T::slow tests/b.py", (["tests/b.py"], []))):
            with self.subTest(verify=verify):
                self.assertEqual(want, critic.pytest_targets(verify))

    def test_every_listed_value_option_takes_the_next_word(self) -> None:
        """Each option `_PYTEST_VALUE_OPTIONS` lists, given its value as the next word, leaves
        that word out of the targets, so no entry is listed for nothing. Mutant: any entry
        dropped, so its value prints as a selector."""
        for option in sorted(critic._PYTEST_VALUE_OPTIONS):
            with self.subTest(option=option):
                self.assertEqual((["tests/a.py"], []),
                                 critic.pytest_targets(f"pytest {option} v tests/a.py"))

    def test_every_option_pytest_reads_a_value_for_is_listed(self) -> None:
        """The installed pytest's own options (its plugins' autoload off) that read one value
        are each a listed value option or an expression option, so the brief reads a line as
        pytest does. A pytest whose parser cannot be read this way is named as the reason."""
        probe = ("import json, _pytest.config as c\n"
                 "p = c._prepareconfig([])._parser\n"
                 "p = getattr(p, 'optparser', None) or p._getparser()\n"
                 "print(json.dumps(sorted(o for a in p._actions if a.nargs in (None, 1)"
                 " for o in a.option_strings)))\n")
        env = {**gitutil.git_env(), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, "-B", "-c", probe], capture_output=True,
                               text=True, timeout=120, env=env, cwd=d, check=False)
        if r.returncode != 0:
            self.skipTest(f"pytest's option parser could not be read: {r.stderr.strip()[-300:]}")
        options = json.loads(r.stdout.strip().splitlines()[-1])
        self.assertIn("-k", options, "premise: the probe read pytest's options")
        known = critic._PYTEST_VALUE_OPTIONS | set(critic._PYTEST_EXPRESSION_OPTIONS)
        self.assertEqual([], [o for o in options if o not in known])

    def test_an_expression_named_twice_is_named_once(self) -> None:
        """Two criteria filtering one file by one expression name the file and the expression
        once each, in criterion order. Mutant: the expressions kept as each line gives them."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "pytest tests/test_widget.py -k 'add or sign'\n\n### AC2: again\n"
                           "- **Verify:** pytest tests/test_widget.py -k 'add or sign' -m slow")
            self.assertEqual((["tests/test_widget.py"], ["-k 'add or sign'", "-m slow"]),
                             critic._verify_selectors(root, "US0101"))

    def test_a_unit_no_artefact_holds_names_no_selector(self) -> None:
        """A unit id no artefact holds reads as no selectors and no expressions, never None.
        Mutant: the not-found branch returning nothing, which the caller unpacks."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, "pytest tests/test_widget.py -k 'add or sign'")
            self.assertEqual(([], []), critic._verify_selectors(root, "US0999"))
            self.assertEqual((["tests/test_widget.py"], ["-k 'add or sign'"]),
                             critic._verify_selectors(root, "US0101"))

    def test_the_brief_prints_no_bogus_selector(self) -> None:
        """AC1 through the shipped verb: the author self-check section on the brief's stderr,
        for a `-k` given on its own and in a cluster of short flags after `-r a`."""
        for verify in ("pytest tests/test_widget.py -k 'add or sign'",
                       "pytest tests/test_widget.py -r a -qk 'add or sign'"):
            with self.subTest(verify=verify), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, verify)
                r = _cli(root, "brief", "--unit", "US0101", "--seat", "qa")
                self.assertEqual(0, r.returncode, r.stderr)
                said = " ".join(r.stderr.split())
                self.assertIn("Verify selectors: tests/test_widget.py (-k 'add or sign' filters "
                              "by expression", said)
                self.assertNotIn("tests/test_widget.py; ", said, "a second selector was named")


class CriticKeptListWriteTests(unittest.TestCase):

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                     "root writes into a read-only directory")
    def test_a_kept_list_that_cannot_be_written_adds_no_row(self) -> None:
        """AC2, part one. Mutant: the row appended before the kept list is written, so a failed
        write leaves a row while the message says nothing was written. A record by hand whose
        stale list cannot be removed is refused the same way."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            kept = critic.author_mutants_path(root, "US0101").parent
            kept.mkdir(parents=True)
            kept.chmod(0o555)
            try:
                self._read_only(root, kept)
            finally:
                kept.chmod(0o755)

    def _read_only(self, root: Path, kept: Path) -> None:
        """The cases under a read-only kept-list folder, restored by the caller."""
        r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "report.json"))
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("the kept mutant list", r.stderr)
        self.assertIn("was not written", r.stderr)
        self.assertIn("Nothing was written", r.stderr)
        self.assertEqual([], critic.read_self_checks(root))
        kept.chmod(0o755)
        r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "report.json"))
        self.assertEqual(0, r.returncode, r.stderr)
        kept.chmod(0o555)
        mutants = _write(root, "sdlc-studio/.local/mutants.json", json.dumps(
            [{"mutant": "by hand", "test": TEST, "result": "killed"}]))
        claims = root / "sdlc-studio" / ".local" / "claims.json"
        r = _cli(root, "self-check", "record", "--unit", "US0101", "--claims", str(claims),
                 "--mutants", str(mutants))
        self.assertEqual(2, r.returncode, r.stdout)
        self.assertIn("was not removed", r.stderr)
        self.assertEqual(1, len(critic.read_self_checks(root)))

    def test_a_row_that_cannot_be_appended_leaves_no_new_kept_list(self) -> None:
        """The other order of failure: the list written and the row then refused by the disk.
        The list is put back as it was, so no list names a row that was never written."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            failing = OSError("disk full")
            with unittest.mock.patch.object(critic, "_append_row", side_effect=failing), \
                    self.assertRaises(OSError):
                critic.record_self_check(root, "US0101", CLAIMS,
                                         critic.mutants_from_report(_report(
                                             root / "r.json"), "US0101"),
                                         report=str(root / "r.json"))
            self.assertFalse(critic.author_mutants_path(root, "US0101").exists())
            critic.record_self_check(root, "US0101", CLAIMS, critic.mutants_from_report(
                _report(root / "r.json"), "US0101"), report=str(root / "r.json"))
            before = critic.author_mutants_path(root, "US0101").read_bytes()
            with unittest.mock.patch.object(critic, "_append_row", side_effect=failing), \
                    self.assertRaises(OSError):
                critic.record_self_check(root, "US0101", CLAIMS, critic.mutants_from_report(
                    _report(root / "r2.json"), "US0101"), report=str(root / "r2.json"))
            self.assertEqual(before, critic.author_mutants_path(root, "US0101").read_bytes())

    def test_a_malformed_kept_list_is_refused_by_name_not_a_crash(self) -> None:
        """AC2, part two. Mutants: a kept list whose mutants are not objects crashing the brief
        with AttributeError; one that is not JSON read as no list at all. Each is refused with
        the file named, and the brief writes no fingerprint."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "report.json"))
            self.assertEqual(0, r.returncode, r.stderr)
            path = critic.author_mutants_path(root, "US0101")
            good = json.loads(path.read_text(encoding="utf-8"))
            for label, body in (("mutants not objects", json.dumps({**good, "mutants": [1, "x"]})),
                                ("one mutant not an object", json.dumps(
                                    {**good, "mutants": [good["mutants"][0], 1]})),
                                ("a field not text", json.dumps(
                                    {**good, "mutants": [{**good["mutants"][0], "old": 3}]})),
                                ("mutants not a list", json.dumps({**good, "mutants": "x"})),
                                ("not an object", json.dumps([good])),
                                ("not JSON", "{not json")):
                with self.subTest(case=label):
                    path.write_text(body, encoding="utf-8")
                    with self.assertRaises(ValueError) as caught:
                        critic.recorded_mutants(root, "US0101")
                    self.assertIn(str(path), str(caught.exception))
                    self.assertIn("malformed", str(caught.exception))
                    r = _cli(root, "brief", "--unit", "US0101", "--seat", "qa")
                    self.assertEqual(2, r.returncode, r.stderr)
                    self.assertIn("brief refused:", r.stderr)
                    self.assertIn("malformed", r.stderr)
                    self.assertNotIn("Traceback", r.stderr)
                    self.assertEqual("", r.stdout)

    def test_a_kept_list_that_cannot_be_read_is_refused_by_name(self) -> None:
        """A kept list the disk will not read (here a directory where the file should be) is
        refused as malformed, naming the file, as an unparsable one is. Mutant: only a parse
        error caught, so the read error crashes the brief."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "report.json"))
            self.assertEqual(0, r.returncode, r.stderr)
            path = critic.author_mutants_path(root, "US0101")
            path.unlink()
            path.mkdir()
            with self.assertRaises(ValueError) as caught:
                critic.recorded_mutants(root, "US0101")
            self.assertIn(f"the kept mutant list {path} is malformed", str(caught.exception))
            r = _cli(root, "brief", "--unit", "US0101", "--seat", "qa")
            self.assertEqual(2, r.returncode, r.stderr)
            self.assertIn("brief refused:", r.stderr)
            self.assertNotIn("Traceback", r.stderr)

    def test_an_absent_or_stale_kept_list_still_reads_as_none(self) -> None:
        """The controls: no kept file, or one naming another row, is no list (the brief says
        nothing was recorded), never a refusal."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            self.assertIsNone(critic.recorded_mutants(root, "US0101"))
            r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "report.json"))
            self.assertEqual(0, r.returncode, r.stderr)
            path = critic.author_mutants_path(root, "US0101")
            data = json.loads(path.read_text(encoding="utf-8"))
            path.write_text(json.dumps({**data, "digest": "0123456789abcdef"}), encoding="utf-8")
            self.assertIsNone(critic.recorded_mutants(root, "US0101"))
            path.unlink()
            self.assertIsNone(critic.recorded_mutants(root, "US0101"))


class CriticKeptListPathTests(unittest.TestCase):

    def test_the_kept_list_names_the_report_relative_to_the_root(self) -> None:
        """AC3, part one. Mutant: the report's path kept as given, so a committed file carries
        an absolute local path. A report outside the root is kept by its name alone."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as away:
            root = Path(d)
            _project(root)
            inside = _report(root / "sdlc-studio" / ".local" / "lane" / "US0101-report.json")
            r = _record_from(root, inside)
            self.assertEqual(0, r.returncode, r.stderr)
            kept = json.loads(critic.author_mutants_path(root, "US0101").read_text("utf-8"))
            self.assertEqual("sdlc-studio/.local/lane/US0101-report.json", kept["report"])
            r = _record_from(root, _report(Path(away) / "elsewhere" / "report.json"))
            self.assertEqual(0, r.returncode, r.stderr)
            kept = json.loads(critic.author_mutants_path(root, "US0101").read_text("utf-8"))
            self.assertEqual("report.json", kept["report"])
            self.assertNotIn(str(away), critic.author_mutants_path(root, "US0101").read_text(
                "utf-8"))
            self.assertNotIn(str(root), critic.author_mutants_path(root, "US0101").read_text(
                "utf-8"))

    def test_a_root_given_as_dot_still_names_the_report_relative_to_it(self) -> None:
        """The default `--root .`, run from the project root, with the report named by its
        absolute path or relative to the working directory: the kept list names it relative to
        the root. The CLI hands the record a root it has already resolved, so the function that
        names the report is also given the root as `.` and as a path through a symlink. Mutant:
        the root left unresolved there, so no resolved report lies under `.` or under the link,
        and each is kept by its name alone."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve()
            _project(root)
            report = _report(root / "sdlc-studio" / ".local" / "lane" / "US0101-report.json")
            claims = _write(root, "sdlc-studio/.local/claims.json", json.dumps(CLAIMS))
            for given in (str(report), "sdlc-studio/.local/lane/US0101-report.json"):
                with self.subTest(report=given):
                    r = subprocess.run(
                        [sys.executable, "-B", str(CRITIC), "self-check", "record", "--unit",
                         "US0101", "--claims", str(claims), "--mutants-from", given, "--root",
                         "."], capture_output=True, text=True, timeout=300, cwd=root,
                        env=gitutil.git_env(), check=False)
                    self.assertEqual(0, r.returncode, r.stderr)
                    kept = json.loads(critic.author_mutants_path(root, "US0101").read_text(
                        "utf-8"))
                    self.assertEqual("sdlc-studio/.local/lane/US0101-report.json",
                                     kept["report"])
            link = Path(d).parent / f"{Path(d).name}-link"
            link.symlink_to(root, target_is_directory=True)
            self.addCleanup(link.unlink)
            here = os.getcwd()
            os.chdir(root)
            try:
                for given in (".", str(link)):
                    with self.subTest(root=given):
                        self.assertEqual("sdlc-studio/.local/lane/US0101-report.json",
                                         critic._kept_report_path(given, report))
            finally:
                os.chdir(here)

    def test_a_report_of_the_wrong_kind_or_version_is_refused(self) -> None:
        """AC3, part two. Mutants: the kind check dropped; the version check dropped. Each is
        refused naming the cause, with no row written."""
        for label, overrides, said in (
                ("another kind", {"kind": "mutation-run"}, "is not a report the mutation runner"),
                ("another version", {"version": mutation.EDITS_REPORT_VERSION + 1},
                 f"version {mutation.EDITS_REPORT_VERSION + 1!r} runner report")):
            with self.subTest(case=label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                r = _record_from(root, _report(root / "sdlc-studio" / ".local" / "r.json",
                                               **overrides))
                self.assertEqual(2, r.returncode, r.stdout)
                self.assertIn(said, r.stderr)
                self.assertEqual([], critic.read_self_checks(root))


if __name__ == "__main__":
    unittest.main()
