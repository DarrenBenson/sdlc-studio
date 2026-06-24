"""Unit tests for disclosure.py - progressive-disclosure + best-practice check (CR0063, advisory)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "disclosure.py"


def _load():
    spec = importlib.util.spec_from_file_location("disclosure", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["disclosure"] = mod
    spec.loader.exec_module(mod)
    return mod


dc = _load()

MARKER = "<!-- Load when: x -->\n"


def _skill(repo, *, refs=None, helps=None, scripts=None, templates=None, indexed=()):
    """Build a minimal skill dir. `indexed` names appear in SKILL.md (reachable)."""
    sd = repo / ".claude" / "skills" / "sdlc-studio"
    (sd / "help").mkdir(parents=True, exist_ok=True)
    (sd / "scripts").mkdir(parents=True, exist_ok=True)
    (sd / "templates").mkdir(parents=True, exist_ok=True)
    (sd / "SKILL.md").write_text(
        "# SKILL\n\n## When to Use\n\nx\n\n## Index\n\n" + "\n".join(indexed) + "\n", encoding="utf-8")
    (sd / "help" / "references.md").write_text("# refs\n", encoding="utf-8")
    (sd / "help" / "help.md").write_text("# help\n", encoding="utf-8")
    for name, body in (refs or {}).items():
        (sd / name).write_text(body, encoding="utf-8")
    for name, body in (helps or {}).items():
        (sd / "help" / name).write_text(body, encoding="utf-8")
    for name, (body, ex) in (scripts or {}).items():
        p = sd / "scripts" / name
        p.write_text(body, encoding="utf-8")
        p.chmod(0o755 if ex else 0o644)
    for relpath, body in (templates or {}).items():
        f = sd / "templates" / relpath
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body, encoding="utf-8")
    return sd


def _kinds(repo, kind):
    return [f["name"] for f in dc.check(repo)["findings"] if f["kind"] == kind]


class DisclosureTests(unittest.TestCase):
    def test_missing_load_marker_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": "# foo\n\nno marker\n"}, indexed=["reference-foo.md"])
            self.assertIn("reference-foo.md", _kinds(Path(d), "missing-load-marker"))

    def test_marked_indexed_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": MARKER + "# foo\n"}, indexed=["reference-foo.md"])
            names = [f["name"] for f in dc.check(Path(d))["findings"]
                     if f["name"] == "reference-foo.md"]
            self.assertEqual(names, [])  # neither missing-marker nor orphan

    def test_orphan_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": MARKER + "# foo\n"}, indexed=[])  # not in index
            self.assertIn("reference-foo.md", _kinds(Path(d), "orphan"))

    def test_help_file_checked_too(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), helps={"bug.md": "# bug help\n"}, indexed=[])
            self.assertIn("bug.md", _kinds(Path(d), "missing-load-marker"))

    def test_help_missing_nl_block_flagged(self):  # CR0108
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), helps={"bug.md": "# bug help\n"}, indexed=[])
            self.assertIn("bug.md", _kinds(Path(d), "help-missing-nl-block"))

    def test_help_with_nl_block_passes(self):  # CR0108
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), helps={"bug.md": "# bug\n\n## You can just ask\n\n| x | y |\n"}, indexed=[])
            self.assertNotIn("bug.md", _kinds(Path(d), "help-missing-nl-block"))

    def test_meta_help_files_exempt_from_nl_block(self):  # CR0108: arguments/references exempt
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), indexed=[])
            self.assertNotIn("references.md", _kinds(Path(d), "help-missing-nl-block"))

    def test_script_not_executable_and_no_help_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), scripts={"foo.py": ("x = 1\n", False)})  # not executable, no argparse
            self.assertIn("foo.py", _kinds(Path(d), "script-not-executable"))
            self.assertIn("foo.py", _kinds(Path(d), "script-no-help"))

    def test_executable_argparse_script_passes(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), scripts={"foo.py": ("import argparse\n", True)})
            names = [f["name"] for f in dc.check(Path(d))["findings"] if f["name"] == "foo.py"]
            self.assertEqual(names, [])

    def test_template_without_placeholder_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), templates={"core/core.md": "# hardcoded, no placeholder\n"})
            self.assertIn("core.md", _kinds(Path(d), "template-no-placeholder"))

    def test_consuming_repo_is_noop(self):
        with tempfile.TemporaryDirectory() as d:
            r = dc.check(Path(d))  # no .claude/skills/sdlc-studio/SKILL.md
            self.assertFalse(r["applicable"])
            self.assertEqual(r["findings"], [])

    def test_all_findings_advisory_and_ok(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": "no marker\n"}, indexed=[])
            r = dc.check(Path(d))
            self.assertTrue(r["ok"])  # advisory: never not-ok
            self.assertTrue(all(f["blocking"] is False for f in r["findings"]))

    def test_non_utf8_file_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), refs={"reference-foo.md": MARKER})
            (sd / "templates" / "bin.md").write_bytes(b"\xff\xfe not utf8 \x00")
            r = dc.check(Path(d))           # must not raise
            self.assertTrue(r["applicable"])

    def test_download_does_not_false_match_marker(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": "# foo\n\nDownload: a file\nPayload: x\n"},
                   indexed=["reference-foo.md"])
            self.assertIn("reference-foo.md", _kinds(Path(d), "missing-load-marker"))

    def test_orphan_not_masked_by_substring(self):
        with tempfile.TemporaryDirectory() as d:
            # index references qrcode.md; the real orphan code.md must still be flagged
            sd = _skill(Path(d), helps={"code.md": MARKER}, indexed=["qrcode.md"])
            self.assertIn("code.md", _kinds(Path(d), "orphan"))

    def test_help_file_reachable_via_type_pattern_not_orphan(self):
        # help/<type>.md is reached via the templated help/{type}.md reference (not a literal name)
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), helps={"bug.md": MARKER}, indexed=[])
            # inject the pattern into SKILL.md (as the Progressive Loading Guide does)
            sk = sd / "SKILL.md"; sk.write_text(sk.read_text() + "\n| x | help/{type}.md | - |\n", encoding="utf-8")
            self.assertNotIn("bug.md", _kinds(Path(d), "orphan"))

    def test_module_template_not_flagged(self):
        # template check is scoped to templates/core/ - guidance modules are not fill scaffolds
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), templates={"modules/tsd/contract-tests.md": "# fixed examples, no placeholder\n"})
            self.assertEqual(_kinds(Path(d), "template-no-placeholder"), [])

    def test_core_template_without_placeholder_still_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), templates={"core/prd.md": "# no placeholder here\n"})
            self.assertIn("prd.md", _kinds(Path(d), "template-no-placeholder"))

    def test_real_reference_orphan_still_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), refs={"reference-foo.md": MARKER}, indexed=[])  # not in any index, not help/
            self.assertIn("reference-foo.md", _kinds(Path(d), "orphan"))

    def test_help_orphan_flagged_when_pattern_absent(self):
        # the safety net: with no help/{type}.md pattern in any index, a help file IS an orphan
        with tempfile.TemporaryDirectory() as d:
            _skill(Path(d), helps={"bug.md": MARKER}, indexed=[])  # SKILL.md has no pattern
            self.assertIn("bug.md", _kinds(Path(d), "orphan"))

    def test_dead_help_file_vouched_by_pattern_is_deliberate_tradeoff(self):
        # documented trade-off: once the help/{type}.md pattern exists, even an unreferenced help
        # file is treated as reachable (the pattern vouches for all help files). Advisory; accepted.
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), helps={"zombie.md": MARKER}, indexed=[])
            sk = sd / "SKILL.md"; sk.write_text(sk.read_text() + "\n| x | help/{type}.md | - |\n", encoding="utf-8")
            self.assertNotIn("zombie.md", _kinds(Path(d), "orphan"))


if __name__ == "__main__":
    unittest.main()
