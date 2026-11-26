"""The release cut writes a committed record of each release to sdlc-studio/reports/releases.jsonl:
the version, the date of the cut, the release before it and the signed reports it shipped.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/release_cut.py
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "release_cut.py"
RECORD = "sdlc-studio/reports/releases.jsonl"
CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [0.9.0] - 2026-01-01\n\n- old\n"
FRAGMENT = "<!-- section: Added -->\n- **A shipped thing (US0001).**\n"


def _load():
    spec = importlib.util.spec_from_file_location("release_cut", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["release_cut"] = mod
    spec.loader.exec_module(mod)
    return mod


def _git(root: Path, *argv: str) -> str:
    return gitutil.git(list(argv), root, text=True).stdout.strip()


def _commit(root: Path, message: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)


def _cli(root: Path, *argv: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """The shipped entry point as a subprocess, confined to the fixture."""
    return subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(root), *argv],
                          capture_output=True, text=True, env=env or gitutil.git_env(),
                          timeout=300, check=False)


def _project(case: unittest.TestCase, git: bool = True) -> Path:
    """A project holding CHANGELOG.md with `[Unreleased]` and one pending fragment."""
    d = tempfile.TemporaryDirectory(prefix="release_record_")
    case.addCleanup(d.cleanup)
    root = Path(d.name)
    (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    (root / "changelog.d").mkdir()
    (root / "changelog.d" / "US0001.md").write_text(FRAGMENT, encoding="utf-8")
    if git:
        _git(root, "init", "-q")
    return root


def _sign(root: Path, rid: str, at: str) -> None:
    """A signed report of record: only its id and its signature matter to the release record."""
    d = root / "sdlc-studio" / "reports"
    d.mkdir(parents=True, exist_ok=True)
    rep = {"report_id": rid, "signature": {"principal": "operator", "signed_at": at}}
    (d / f"{rid}.json").write_text(json.dumps(rep), encoding="utf-8")


def _lines(root: Path) -> list[dict]:
    return [json.loads(x) for x in (root / RECORD).read_text(encoding="utf-8").splitlines()]


def _header_date(root: Path, version: str) -> str:
    text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"(?m)^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})$", text)
    assert m, text
    return m.group(1)


def _confine(case: unittest.TestCase) -> None:
    patch = mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
    patch.start()
    case.addCleanup(patch.stop)


class ReleaseRecordTests(unittest.TestCase):
    def test_the_cut_records_the_version_date_and_reports_since_the_last_release(self) -> None:
        """AC1. RPT0001 is signed in the tagged commit; RPT0002 and RPT0003 are signed after it,
        so the 1.1.0 record names them and the tag, and the section is cut as before."""
        root = _project(self)
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        _sign(root, "RPT0001", "2026-01-02T10:00:00Z")
        _commit(root, "one")
        _git(root, "tag", "v1.0.0")
        _sign(root, "RPT0003", "2026-01-04T10:00:00Z")
        _sign(root, "RPT0002", "2026-01-03T10:00:00Z")
        _commit(root, "two")
        before = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        r = _cli(root, "changelog-cut", "--version", "1.1.0")
        after = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.assertEqual(r.returncode, 0, r.stderr)
        date = _header_date(root, "1.1.0")
        self.assertIn(date, {before, after})
        self.assertEqual(_lines(root), [{"version": "1.1.0", "date": date, "previous": "v1.0.0",
                                         "reports": ["RPT0002", "RPT0003"]}])
        self.assertIn(f"recorded in {RECORD}: ", r.stdout)
        self.assertIn('"previous": "v1.0.0"', r.stdout)
        ignored = subprocess.run(["git", "check-ignore", "-q", RECORD], cwd=root,
                                 env=gitutil.git_env(), capture_output=True, check=False)
        self.assertEqual(ignored.returncode, 1, "the record must not be git-ignored")
        self.assertIn(f"?? {RECORD}", _git(root, "status", "--porcelain", "-uall"))
        clog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn(f"## [Unreleased]\n\n## [1.1.0] - {date}", clog)
        self.assertIn("A shipped thing (US0001)", clog.split("## [1.1.0]")[1].split("## [0.9")[0])
        self.assertFalse((root / "changelog.d" / "US0001.md").exists())

    def test_a_second_cut_of_one_version_leaves_one_unchanged_record(self) -> None:
        """AC2. A re-run after an interrupted cut keeps the first record byte for byte, even a
        day later with a new report signed; a refused cut leaves the record file as it was."""
        mod = _load()
        _confine(self)
        root = _project(self)
        _sign(root, "RPT0001", "2026-01-02T10:00:00Z")
        argv = ["--root", str(root), "changelog-cut", "--version", "1.1.0"]
        with mock.patch.object(mod.sdlc_md, "now_date", return_value="2026-03-01"):
            self.assertEqual(mod.main(argv), 0)
        first = (root / RECORD).read_bytes()
        self.assertEqual(_lines(root), [{"version": "1.1.0", "date": "2026-03-01",
                                         "previous": None, "reports": ["RPT0001"]}])
        # the cut stopped before its section landed: the section is taken back out
        (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
        (root / "changelog.d" / "US0001.md").write_text(FRAGMENT, encoding="utf-8")
        _sign(root, "RPT0002", "2026-03-01T12:00:00Z")
        with mock.patch.object(mod.sdlc_md, "now_date", return_value="2026-03-02"):
            self.assertEqual(mod.main(argv), 0)
        self.assertEqual((root / RECORD).read_bytes(), first)
        self.assertEqual(_header_date(root, "1.1.0"), "2026-03-02")   # the cut completed
        # refused for an existing [1.1.0] section: the record file is untouched
        r = _cli(root, "changelog-cut", "--version", "1.1.0")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("already carries", r.stderr)
        self.assertEqual((root / RECORD).read_bytes(), first)
        # and a refused cut of a version with no record writes none either
        clog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        (root / "CHANGELOG.md").write_text(clog.replace("## [1.1.0]", "## [1.2.0]"),
                                           encoding="utf-8")
        r = _cli(root, "changelog-cut", "--version", "1.2.0")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertEqual((root / RECORD).read_bytes(), first)
        (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        r = _cli(root, "changelog-cut", "--version", "1.3.0")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("no '## [Unreleased]'", r.stderr)
        self.assertEqual((root / RECORD).read_bytes(), first)

    def test_a_release_with_no_signed_report_is_still_recorded(self) -> None:
        """AC3. No repository, no reports directory, no tag: the first release is recorded with
        no previous release and an empty report list, with git on PATH and without it."""
        empty = tempfile.TemporaryDirectory(prefix="release_record_nogit_")
        self.addCleanup(empty.cleanup)
        for env in (gitutil.git_env(), gitutil.git_env(PATH=empty.name)):
            root = _project(self, git=False)
            r = _cli(root, "changelog-cut", "--version", "1.0.0", env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse((root / "sdlc-studio" / "reports" / "RPT0001.json").exists())
            self.assertEqual(_lines(root), [{"version": "1.0.0",
                                             "date": _header_date(root, "1.0.0"),
                                             "previous": None, "reports": []}])

    def test_a_later_cut_appends_and_ships_only_the_reports_no_record_names(self) -> None:
        """Earlier records stay byte-identical (a missing final newline is supplied, not
        rewritten), and an empty or whitespace-only line is skipped; with no tag the previous
        release is the newest record; a report signed after one cut and before its tag ships
        with the next release, not with none."""
        mod = _load()
        _confine(self)
        root = _project(self)
        older = ('{"version": "0.8.0", "reports": []}\n\n   \n'
                 '{"version": "0.9.0", "reports": ["RPT0001"]}')
        (root / RECORD).parent.mkdir(parents=True)
        (root / RECORD).write_text(older, encoding="utf-8")
        _sign(root, "RPT0001", "2026-01-02T10:00:00Z")
        _sign(root, "RPT0002", "2026-01-03T10:00:00Z")
        with mock.patch.object(mod.sdlc_md, "now_date", return_value="2026-03-01"):
            self.assertEqual(mod.main(["--root", str(root), "changelog-cut", "--version",
                                       "1.0.0"]), 0)
        text = (root / RECORD).read_text(encoding="utf-8")
        self.assertTrue(text.startswith(older + "\n{"), text)
        self.assertEqual(json.loads(text.splitlines()[-1]),
                         {"version": "1.0.0", "date": "2026-03-01", "previous": "0.9.0",
                          "reports": ["RPT0002"]})
        # RPT0003 is signed and committed before the v1.0.0 tag, after the 1.0.0 cut
        (root / "CHANGELOG.md").write_text(
            (root / "CHANGELOG.md").read_text(encoding="utf-8").replace(
                "## [Unreleased]\n", "## [Unreleased]\n\n### Fixed\n\n- a fix\n"),
            encoding="utf-8")
        _sign(root, "RPT0003", "2026-03-02T10:00:00Z")
        _commit(root, "tagged")
        _git(root, "tag", "-a", "v1.0.0", "-m", "1.0.0")
        _sign(root, "RPT0004", "2026-03-03T10:00:00Z")
        with mock.patch.object(mod.sdlc_md, "now_date", return_value="2026-03-04"):
            self.assertEqual(mod.main(["--root", str(root), "changelog-cut", "--version",
                                       "1.1.0"]), 0)
        self.assertEqual(json.loads((root / RECORD).read_text(encoding="utf-8")
                                    .splitlines()[-1]),
                         {"version": "1.1.0", "date": "2026-03-04", "previous": "v1.0.0",
                          "reports": ["RPT0003", "RPT0004"]})

    def test_the_first_record_after_an_annotated_tag_reads_the_tagged_commit(self) -> None:
        """With no earlier record, the reports already signed in the tag's commit (annotated
        here) are not shipped again; an unsigned report there that is signed now is."""
        root = _project(self)
        _sign(root, "RPT0001", "2026-01-02T10:00:00Z")
        (root / "sdlc-studio" / "reports" / "RPT0002.json").write_text(
            json.dumps({"report_id": "RPT0002", "signature": {}}), encoding="utf-8")
        _commit(root, "one")
        _git(root, "tag", "-a", "v2.0.0", "-m", "2.0.0")
        _commit(root, "beyond the tag")
        _sign(root, "RPT0002", "2026-01-05T10:00:00Z")
        r = _cli(root, "changelog-cut", "--version", "2.1.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = _lines(root)[0]
        self.assertEqual((rec["previous"], rec["reports"]), ("v2.0.0", ["RPT0002"]))

    def test_a_malformed_record_file_refuses_the_cut_before_anything_is_written(self) -> None:
        """A line that is not a release record refuses the cut by its line number, leaving
        CHANGELOG.md, the fragment and the record file as they were."""
        bad = ["not json", "[1]", '{"reports": []}', '{"version": 1, "reports": []}',
               '{"version": "1.0.0"}', '{"version": "1.0.0", "reports": "RPT0001"}',
               '{"version": "1.0.0", "reports": [7]}']
        for line in bad:
            with self.subTest(line=line):
                root = _project(self, git=False)
                body = '{"version": "0.9.0", "reports": []}\n' + line + "\n"
                (root / RECORD).parent.mkdir(parents=True)
                (root / RECORD).write_text(body, encoding="utf-8")
                r = _cli(root, "changelog-cut", "--version", "1.0.0")
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn(f"{RECORD} line 2 is not a release record", r.stderr)
                self.assertEqual((root / RECORD).read_text(encoding="utf-8"), body)
                self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), CHANGELOG)
                self.assertTrue((root / "changelog.d" / "US0001.md").exists())

    def test_an_unreadable_signed_report_refuses_the_cut(self) -> None:
        """A report the reader cannot parse refuses the cut by name, writing nothing."""
        root = _project(self, git=False)
        (root / "sdlc-studio" / "reports").mkdir(parents=True)
        (root / "sdlc-studio" / "reports" / "RPT0009.json").write_text("{", encoding="utf-8")
        r = _cli(root, "changelog-cut", "--version", "1.0.0")
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("RPT0009.json could not be read", r.stderr)
        self.assertFalse((root / RECORD).exists())
        self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), CHANGELOG)

    def test_a_report_unreadable_at_the_previous_tag_refuses_the_cut(self) -> None:
        """The first record reads the reports as committed at the previous tag: one broken
        there, though repaired since, refuses the cut by name, writing nothing."""
        root = _project(self)
        reports = root / "sdlc-studio" / "reports"
        reports.mkdir(parents=True)
        (reports / "RPT0009.json").write_text("{", encoding="utf-8")
        _commit(root, "broken")
        _git(root, "tag", "v1.0.0")
        _sign(root, "RPT0009", "2026-01-02T10:00:00Z")
        _commit(root, "repaired")
        r = _cli(root, "changelog-cut", "--version", "1.1.0")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("changelog-cut refused: ", r.stderr)
        self.assertIn("RPT0009.json could not be read", r.stderr)
        self.assertFalse((root / RECORD).exists())
        self.assertEqual((root / "CHANGELOG.md").read_text(encoding="utf-8"), CHANGELOG)

    def test_the_shipped_reports_are_listed_oldest_signature_first(self) -> None:
        """The record lists the reports in signing order, not id order."""
        root = _project(self, git=False)
        _sign(root, "RPT0004", "2026-01-09T10:00:00Z")
        _sign(root, "RPT0005", "2026-01-02T10:00:00Z")
        r = _cli(root, "changelog-cut", "--version", "1.0.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(_lines(root)[0]["reports"], ["RPT0005", "RPT0004"])

    def test_a_cut_stopped_after_its_first_write_leaves_the_release_recorded(self) -> None:
        """The record is written before CHANGELOG.md: a cut stopped after its first final
        write has recorded the release, and the re-run cuts the section and keeps the record."""
        mod = _load()
        _confine(self)
        root = _project(self)
        real = mod.sdlc_md.atomic_write

        def stop_after_first_final_write(path, text, *args, **kwargs):
            real(path, text, *args, **kwargs)
            if Path(path).name == "releases.jsonl" or "## [1.1.0] - " in text:
                raise OSError("the cut was stopped")

        argv = ["--root", str(root), "changelog-cut", "--version", "1.1.0"]
        with mock.patch.object(mod.sdlc_md, "atomic_write", stop_after_first_final_write):
            self.assertEqual(mod.main(argv), 2)
        self.assertNotIn("## [1.1.0]", (root / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertTrue((root / RECORD).is_file(), "the stopped cut left the release unrecorded")
        first = (root / RECORD).read_bytes()
        self.assertEqual([rec["version"] for rec in _lines(root)], ["1.1.0"])
        r = _cli(root, "changelog-cut", "--version", "1.1.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((root / RECORD).read_bytes(), first)
        self.assertIn("A shipped thing (US0001)",
                      (root / "CHANGELOG.md").read_text(encoding="utf-8").split("## [1.1.0]")[1])


if __name__ == "__main__":
    unittest.main()
