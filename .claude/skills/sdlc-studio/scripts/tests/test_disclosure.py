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



class DepthReachesTheReportTests(unittest.TestCase):
    """US0659 AC4 through `disclosure.py` itself. A measurement with no caller reports to
    nobody - `nesting_depth` had zero non-test callers, which is the exact shape this project
    filed as BG0541 and spent a whole sprint repairing."""

    def _mod(self):
        import importlib.util, sys as _s, pathlib as _p
        d = _p.Path(__file__).resolve().parent.parent
        _s.path.insert(0, str(d)); _s.path.insert(0, str(d / "lib"))
        spec = importlib.util.spec_from_file_location("disclosure_cli", d / "disclosure.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m, d

    def test_the_command_prints_the_depth_and_still_exits_zero(self) -> None:
        """Mutant: leave `nesting_depth` uncalled, so the library is right and nothing runs it.
        Mutant: print a constant rather than the measurement.
        Mutant: make a non-zero depth fail the lane, which runs inside the blocking `lint`."""
        import io, contextlib, re
        m, d = self._mod()
        root = str(d.parents[3])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = m.main(["--root", root])
        out = buf.getvalue()
        self.assertEqual(0, code, "the disclosure lane exited non-zero - it sits inside the "
                                  "blocking `lint` chain, so a report there becomes a gate")
        found = re.search(r"nesting depth (\d+) hop\(s\) from SKILL\.md to ([^,\s]+)", out)
        self.assertIsNotNone(found, f"the command reported no depth at all: {out[-300:]}")
        measured = m.nesting_depth(root)
        self.assertEqual(measured["depth"], int(found.group(1)),
                         "the printed depth is not the measured one")
        self.assertEqual(measured["furthest"], found.group(2))

    def test_the_json_form_carries_it_too(self) -> None:
        """A reader parsing `--format json` must not have to scrape the text form."""
        import io, contextlib, json as _json
        m, d = self._mod()
        root = str(d.parents[3])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(0, m.main(["--root", root, "--format", "json"]))
        payload = _json.loads(buf.getvalue())
        self.assertIn("nesting", payload, "the json form drops the measurement")
        self.assertEqual(m.nesting_depth(root)["depth"], payload["nesting"]["depth"])


class NestingDepthTests(unittest.TestCase):
    """US0659 AC4: the depth is MEASURED, on a fixture whose true depth is known."""

    def _mod(self):
        import importlib.util, sys as _s, pathlib as _p
        d = _p.Path(__file__).resolve().parent.parent
        _s.path.insert(0, str(d)); _s.path.insert(0, str(d / "lib"))
        spec = importlib.util.spec_from_file_location("disclosure_ndt", d / "disclosure.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m

    def test_the_depth_is_measured_not_assumed(self) -> None:
        """The fixture's depth is deliberately FOUR, not the three this story states about the
        real tree: the mutant a hurried implementer writes is returning that constant, and a
        test asserting 'reports the measured depth' against a tree that really is 3 deep passes
        on a hardcoded 3.

        Mutant: return the constant 3 that this story's prose states.
        Mutant: walk depth-first for the longest path rather than breadth-first for the
        shortest - that measures how far a reader could WANDER, not how deep the disclosure is.
        """
        import tempfile as _t, pathlib as _p
        m = self._mod()
        with _t.TemporaryDirectory() as d:
            skill = _p.Path(d)
            (skill / "help").mkdir()
            (skill / "SKILL.md").write_text("# S\n\nSee reference-one.md\n", encoding="utf-8")
            (skill / "reference-one.md").write_text("# 1\n\nSee reference-two.md\n", encoding="utf-8")
            (skill / "reference-two.md").write_text("# 2\n\nSee help/three.md\n", encoding="utf-8")
            (skill / "help" / "three.md").write_text("# 3\n\nSee reference-four.md\n", encoding="utf-8")
            (skill / "reference-four.md").write_text("# 4\n\nNo further links.\n", encoding="utf-8")
            r = m.nesting_depth(skill)
            self.assertTrue(r["applicable"])
            self.assertEqual(4, r["depth"],
                             f"the fixture is four hops deep and the measurement said "
                             f"{r['depth']} - a hardcoded constant, or a longest-path walk")
            self.assertEqual("reference-four.md", r["furthest"])

    def test_the_measurement_is_advisory(self) -> None:
        """`disclosure.py` runs inside the blocking `lint` chain, so a non-zero exit here would
        turn a reported measurement into a gate nobody agreed to.

        Mutant: refuse when the depth exceeds some threshold.
        """
        import pathlib as _p
        m = self._mod()
        root = _p.Path(__file__).resolve().parents[4]
        # The measurement RETURNS a number and raises nothing, whatever the depth: it is a
        # reading, not a verdict, and the caller decides. Nothing in `check()` consults it.
        self.assertNotIn("nesting", str(m.check(root)),
                         "the depth reached the findings list, so it can fail a lane")
        # Measured over the SKILL tree directly rather than a repo root, so the assertion does
        # not depend on how deep this test file happens to sit.
        skill = _p.Path(__file__).resolve().parent.parent.parent
        self.assertGreater(m.nesting_depth(skill)["depth"], 0,
                           "the skill tree measured a depth of zero, which no document that "
                           "names fifty files can honestly have")



if __name__ == "__main__":
    unittest.main()
