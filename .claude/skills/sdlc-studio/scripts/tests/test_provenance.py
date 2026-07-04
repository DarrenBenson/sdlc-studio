"""Unit tests for provenance.py - stamp check + remake backfill (CR0052)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "provenance.py"


def _load():
    spec = importlib.util.spec_from_file_location("provenance", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["provenance"] = mod
    spec.loader.exec_module(mod)
    return mod


prov = _load()

STAMPED = "# US0010: y\n\n> **Status:** Done\n> **Created-by:** sdlc-studio new\n\n## User Story\n\nbody\n"
UNSTAMPED = "# US0005: x\n\n> **Status:** Done\n> **Epic:** EP0001\n\n## User Story\n\nimportant body\n"


def _story(repo: Path, name: str, text: str) -> Path:
    d = repo / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    p = d / name
    p.write_text(text, encoding="utf-8")
    return p


class StampTests(unittest.TestCase):
    def test_has_stamp(self) -> None:
        self.assertTrue(prov.has_stamp(STAMPED))
        self.assertFalse(prov.has_stamp(UNSTAMPED))

    def test_add_stamp_is_idempotent_and_preserving(self) -> None:
        out, changed = prov._add_stamp(UNSTAMPED)
        self.assertTrue(changed)
        self.assertTrue(prov.has_stamp(out))
        for line in UNSTAMPED.splitlines():        # content preserved
            self.assertIn(line, out.splitlines())
        out2, changed2 = prov._add_stamp(out)      # idempotent
        self.assertFalse(changed2)
        self.assertEqual(out2, out)

    def test_stamp_lands_in_header_not_body_blockquote(self) -> None:
        # HIGH regression: a `>` quote in the BODY must not be treated as metadata.
        text = ("# US0001: x\n\n> **Status:** Done\n\n## Notes\n\n> a quoted line in prose\n"
                "> second quoted line\n\n## End\n")
        out, _ = prov._add_stamp(text)
        lines = out.splitlines()
        # stamp sits in the header block (right after Status), not in the Notes quote
        si = lines.index(prov._STAMP.strip()) if prov._STAMP.strip() in lines else \
            next(i for i, l in enumerate(lines) if "Created-by" in l)
        self.assertLess(si, lines.index("## Notes"))
        self.assertIn("> a quoted line in prose", lines)  # body quote intact
        self.assertIn("> second quoted line", lines)

    def test_stamp_no_metadata_html_comment_lead(self) -> None:
        # H1 + leading HTML comment, no metadata blockquote: comment must stay intact.
        text = "# US0002: y\n\n<!-- a template comment -->\n\n## Body\n\ncontent\n"
        out, changed = prov._add_stamp(text)
        self.assertTrue(changed and prov.has_stamp(out))
        self.assertIn("<!-- a template comment -->", out)
        self.assertIn("content", out)

    def test_no_trailing_newline_preserved(self) -> None:
        out, _ = prov._add_stamp("# US0003: z\n\n> **Status:** Done\n\nbody")  # no trailing \n
        self.assertFalse(out.endswith("\n"))

    def test_has_stamp_prose_mention_is_not_a_match(self) -> None:
        # a prose mention (no leading `>`) must NOT count as stamped (else check fails open)
        self.assertFalse(prov.has_stamp("This CR adds a **Created-by:** sdlc-studio stamp.\n"))


class CheckTests(unittest.TestCase):
    def test_unstamped_flagged_stamped_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _story(repo, "US0005-x.md", UNSTAMPED)
            _story(repo, "US0010-y.md", STAMPED)
            r = prov.check(repo, ["story"])
            ids = [f["id"] for f in r["findings"]]
            self.assertIn("US0005", ids)
            self.assertNotIn("US0010", ids)

    def test_advisory_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _story(repo, "US0005-x.md", UNSTAMPED)
            r = prov.check(repo, ["story"])
            self.assertTrue(r["ok"])  # advisory -> ok despite a finding
            self.assertFalse(r["findings"][0]["blocking"])

    def test_adopt_after_cutoff_exempts_legacy(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "provenance:\n  adopt_after: 7\n", encoding="utf-8")
            _story(repo, "US0005-x.md", UNSTAMPED)   # 5 <= 7 -> exempt
            _story(repo, "US0009-z.md", UNSTAMPED.replace("US0005", "US0009"))  # 9 > 7 -> checked
            ids = [f["id"] for f in prov.check(repo, ["story"])["findings"]]
            self.assertEqual(ids, ["US0009"])

    def test_adopt_after_prefixed_id_exempts_legacy(self) -> None:
        # BG0039: the shared parser now accepts a prefixed id on provenance too,
        # matching conformance - US0007 exempts ids <= 7.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "provenance:\n  adopt_after: US0007\n", encoding="utf-8")
            _story(repo, "US0005-x.md", UNSTAMPED)   # 5 <= 7 -> exempt
            _story(repo, "US0009-z.md", UNSTAMPED.replace("US0005", "US0009"))  # 9 > 7 -> checked
            ids = [f["id"] for f in prov.check(repo, ["story"])["findings"]]
            self.assertEqual(ids, ["US0009"])

    def test_boundary_id_is_exempt(self) -> None:
        # BG0039: <= boundary - the cutoff id itself is exempt.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "provenance:\n  adopt_after: 5\n", encoding="utf-8")
            _story(repo, "US0005-x.md", UNSTAMPED)   # 5 <= 5 -> exempt
            self.assertEqual(prov.check(repo, ["story"])["findings"], [])

    def test_unparseable_cutoff_raises_not_silent(self) -> None:
        # LL0008: a typo'd cutoff must fail loud, not coerce to 0 and judge everything.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "provenance:\n  adopt_after: oops\n", encoding="utf-8")
            _story(repo, "US0005-x.md", UNSTAMPED)
            with self.assertRaises(ValueError):
                prov.check(repo, ["story"])

    def test_enforce_makes_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                "provenance:\n  enforce: true\n", encoding="utf-8")
            _story(repo, "US0005-x.md", UNSTAMPED)
            r = prov.check(repo, ["story"])
            self.assertFalse(r["ok"])
            self.assertTrue(r["findings"][0]["blocking"])

    def test_enforce_quoted_false_is_not_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "sdlc-studio").mkdir(parents=True)
            (repo / "sdlc-studio" / ".config.yaml").write_text(
                'provenance:\n  enforce: "false"\n', encoding="utf-8")  # quoted -> still falsey
            _story(repo, "US0005-x.md", UNSTAMPED)
            self.assertTrue(prov.check(repo, ["story"])["ok"])


FIELD_STAMPED = ("# US0011: z\n\n> **Status:** Done\n"
                 "> **Created-by:** field report (a consuming project, 2026-07-04)\n\n"
                 "## User Story\n\nbody\n")


class NonToolProvenanceTests(unittest.TestCase):
    """A non-tool Created-by is provenance, not absence: check accepts it and
    remake never appends a second Created-by line beside it."""

    def test_check_accepts_field_created_by(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            _story(repo, "US0011-z.md", FIELD_STAMPED)
            r = prov.check(repo)
            self.assertEqual(r["findings"], [])

    def test_remake_never_double_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            p = _story(repo, "US0011-z.md", FIELD_STAMPED)
            r = prov.remake(repo)
            self.assertEqual(r["changed"], [])
            text = p.read_text(encoding="utf-8")
            self.assertEqual(
                len([l for l in text.splitlines()
                     if l.lstrip().startswith("> **Created-by:**")]), 1)


class RemakeCutoffTests(unittest.TestCase):
    """remake honours the same adopt_after exemption as check; --all overrides."""

    def _repo(self, d):
        repo = Path(d)
        _story(repo, "US0005-x.md", UNSTAMPED)          # pre-cutoff (legacy)
        _story(repo, "US0009-y.md",
               "# US0009: y\n\n> **Status:** Done\n\n## User Story\n\nbody\n")  # post-cutoff
        (repo / "sdlc-studio" / ".config.yaml").write_text(
            "provenance:\n  adopt_after: 7\n", encoding="utf-8")
        return repo

    def test_remake_skips_pre_cutoff_artifacts(self) -> None:
        try:
            import yaml  # noqa: F401 - config read degrades without PyYAML
        except ImportError:
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r = prov.remake(repo)
            self.assertEqual(r["changed"], ["US0009"])   # legacy US0005 untouched

    def test_remake_all_overrides_cutoff(self) -> None:
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML absent")
        with tempfile.TemporaryDirectory() as d:
            repo = self._repo(d)
            r = prov.remake(repo, include_exempt=True)
            self.assertEqual(sorted(r["changed"]), ["US0005", "US0009"])


class RemakeTests(unittest.TestCase):
    def test_remake_stamps_idempotent_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            p = _story(repo, "US0005-x.md", UNSTAMPED)
            # dry-run: reports but does not write
            r = prov.remake(repo, ["story"], dry_run=True)
            self.assertEqual(r["changed"], ["US0005"])
            self.assertFalse(prov.has_stamp(p.read_text()))
            # real run: stamps, content preserved
            prov.remake(repo, ["story"])
            self.assertTrue(prov.has_stamp(p.read_text()))
            self.assertIn("important body", p.read_text())
            # idempotent: second run changes nothing
            self.assertEqual(prov.remake(repo, ["story"])["count"], 0)


if __name__ == "__main__":
    unittest.main()
