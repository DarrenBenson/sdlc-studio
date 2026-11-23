"""`escape.py trace` proposes the unit and verdict that let an escaped bug through: the units a
release shipped that share a file with the fix, ranked by the files they share, each with its
recorded verdict and seat, and records one only on the operator's `--confirm`."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the gitutil helper
import gitutil  # noqa: E402
import critic  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


escape = _load("escape")


def _cli(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = escape.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _story(root: Path, sid: str, affects: str) -> None:
    (root / "sdlc-studio" / "stories" / f"{sid}-a-story.md").write_text(
        f"# {sid}: a story\n\n> **Status:** Done\n> **Affects:** {affects}\n", encoding="utf-8")


def _bug(root: Path, affects: str = "scripts/a.py", shipped: str | None = "v1.0.0") -> Path:
    path = root / "sdlc-studio" / "bugs" / "BG0001-the-total-is-wrong.md"
    ship = f"> **Shipped-in:** {shipped}\n" if shipped else ""
    path.write_text("# BG0001: the total is wrong\n\n> **Status:** Open\n> **Severity:** High\n"
                    f"> **Affects:** {affects}\n> **Escaped:** yes\n{ship}\n"
                    "## Summary\n\nthe total is wrong\n", encoding="utf-8")
    return path


def _commit(root: Path, message: str) -> None:
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "--allow-empty", "-m", message], root)


def _project(d: str) -> Path:
    """v0.9.0 tags a commit naming no unit; v1.0.0 ships US0001 (scripts/a.py, approved by the
    product seat), US0002 (docs/x.md) and US0003 (scripts/a.py and scripts/b.py); v1.1.0 tags
    one more commit naming no unit, so only the span since v1.0.0 is its own."""
    root = Path(d)
    for sub in ("stories", "bugs", "reviews"):
        (root / "sdlc-studio" / sub).mkdir(parents=True)
    gitutil.git(["init", "-q"], root)
    _commit(root, "chore: start")
    gitutil.git(["tag", "v0.9.0"], root)
    _story(root, "US0001", "scripts/a.py")
    _commit(root, "feat(US0001): total the basket")
    _story(root, "US0002", "docs/x.md")
    _commit(root, "docs(US0002): describe the basket")
    _story(root, "US0003", "scripts/a.py, scripts/b.py")
    _commit(root, "feat(US0003): round the total")
    gitutil.git(["tag", "v1.0.0"], root)
    _commit(root, "chore: polish")
    gitutil.git(["tag", "v1.1.0"], root)
    with contextlib.redirect_stderr(io.StringIO()):
        critic.record_verdict(root, "US0001", "APPROVE", reviewer="Lena Marsh (product)",
                              author="builder-1")
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(root).parts}


class EscapeTraceTests(unittest.TestCase):

    def test_the_unit_sharing_the_fixed_file_is_proposed_with_its_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            _bug(root)
            rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root),
                                 "--format", "json"])
            self.assertEqual(0, rc, err)
            got = json.loads(out)
            units = [p["unit"] for p in got["proposals"]]
            self.assertEqual("US0001", units[0])
            self.assertNotIn("US0002", units)
            first = got["proposals"][0]
            self.assertEqual(["scripts/a.py"], first["shared"])
            self.assertEqual("APPROVE", first["verdict"]["verdict"])
            self.assertEqual("Lena Marsh (product)", first["verdict"]["reviewer"])
            self.assertEqual("product", first["verdict"]["seat"])
            self.assertEqual(1, first["verdict"]["round"])
            # A unit nobody reviewed is proposed with no verdict, never one borrowed from another.
            self.assertIsNone(got["proposals"][1]["verdict"])
            # The text form says the same, on the first proposal line.
            rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root)])
            self.assertEqual(0, rc, err)
            line = next(ln for ln in out.splitlines() if "US0001" in ln)
            for want in ("scripts/a.py", "APPROVE", "Lena Marsh (product)", "seat product"):
                self.assertIn(want, line)
            self.assertNotIn("US0002", out)
            # Ranked by the files shared: a fix touching both files puts US0003 first.
            _bug(root, affects="scripts/a.py, scripts/b.py")
            rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root),
                                 "--format", "json"])
            self.assertEqual(0, rc, err)
            self.assertEqual(["US0003", "US0001"],
                             [p["unit"] for p in json.loads(out)["proposals"]])

    def test_a_confirmed_unit_is_recorded_and_an_unrelated_one_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            bug = _bug(root)
            before = _snapshot(root)
            rc, _out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root)])
            self.assertEqual(0, rc, err)
            self.assertEqual(before, _snapshot(root), "a proposal wrote without --confirm")
            rc, _out, err = _cli(["trace", "--bug", "BG0001", "--confirm", "US0002",
                                  "--root", str(root)])
            self.assertEqual(2, rc)
            self.assertIn("US0002", err)
            self.assertEqual(before, _snapshot(root), "a refused confirm wrote")
            rc, _out, err = _cli(["trace", "--bug", "BG0001", "--confirm", "US0001",
                                  "--root", str(root)])
            self.assertEqual(0, rc, err)
            after = _snapshot(root)
            changed = sorted(k for k in after if after[k] != before.get(k))
            self.assertEqual([str(bug.relative_to(root))], changed)
            lines = bug.read_text(encoding="utf-8").splitlines()
            self.assertIn("> **Escaped-via:** US0001", lines)
            stamp = next(ln for ln in lines if ln.startswith("> **Escaped-verdict:**"))
            for want in ("round 1", "APPROVE", "Lena Marsh (product)", "seat product"):
                self.assertIn(want, stamp)
            # Confirming again replaces the lines rather than stacking a second pair.
            rc, _out, err = _cli(["trace", "--bug", "BG0001", "--confirm", "US0003",
                                  "--root", str(root)])
            self.assertEqual(0, rc, err)
            text = bug.read_text(encoding="utf-8")
            self.assertEqual(1, text.count("> **Escaped-via:**"))
            self.assertIn("> **Escaped-via:** US0003", text)
            self.assertIn("> **Escaped-verdict:** none recorded", text)

    def test_a_bug_with_no_release_or_an_empty_release_proposes_nothing(self) -> None:
        cases = ((None, "records no Shipped-in"), ("v0.9.0", "v0.9.0 tags no unit"),
                 ("v1.1.0", "v1.1.0 tags no unit"), ("v7.0.0", "v7.0.0 is not a git tag"))
        for shipped, named in cases:
            with self.subTest(shipped=shipped), tempfile.TemporaryDirectory() as d:
                root = _project(d)
                _bug(root, shipped=shipped)
                before = _snapshot(root)
                for extra in ([], ["--confirm", "US0001"]):
                    rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root),
                                         "--format", "json", *extra])
                    self.assertEqual(2, rc, out + err)
                    self.assertIn(named, err)
                    self.assertNotIn("US0001", out)
                self.assertEqual(before, _snapshot(root))

    def test_a_bug_filed_by_the_changelog_spelling_of_a_tag_is_traced(self) -> None:
        """The tag is v6.4.0 and CHANGELOG.md calls the release [6.4.0]. Filing by the changelog's
        spelling stores the tag's, so the trace reads the release instead of refusing it as no
        tag; and a record that already holds the changelog spelling is read through the same
        resolver rather than refused. Either stored spelling keeps the bound of the tag before
        it: v6.3.0 shipped US0002 over the same file, and neither the trace nor `--confirm`
        reads it as a unit of v6.4.0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for sub in ("stories", "bugs", "reviews"):
                (root / "sdlc-studio" / sub).mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")
            gitutil.git(["init", "-q"], root)
            _commit(root, "chore: start")
            _story(root, "US0002", "scripts/a.py")
            _commit(root, "feat(US0002): an earlier total")
            gitutil.git(["tag", "v6.3.0"], root)
            _story(root, "US0001", "scripts/a.py")
            _commit(root, "feat(US0001): total the basket")
            gitutil.git(["tag", "v6.4.0"], root)
            (root / "CHANGELOG.md").write_text("# Changelog\n\n## [6.4.0] - 2026-11-16\n",
                                               encoding="utf-8")
            file_finding = _load("file_finding")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = file_finding.main([
                    "file", "--type", "bug", "--title", "the total is wrong",
                    "--severity", "High", "--affects", "scripts/a.py", "--points", "2",
                    "--summary", "the total is wrong", "--steps", "add two prices",
                    "--fix", "carry the one", "--escaped", "--shipped-in", "6.4.0",
                    "--format", "json", "--root", str(root)])
            self.assertEqual(0, rc, err.getvalue())
            filed = json.loads(out.getvalue())
            path = Path(filed["path"])
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertIn("> **Shipped-in:** v6.4.0", lines)
            # The filed spelling, then a record written before filing resolved the spelling: each
            # is traced to v6.4.0's own unit, US0001, and never to US0002, which v6.3.0 shipped.
            for stored in ("v6.4.0", "6.4.0"):
                with self.subTest(stored=stored):
                    kept = [ln for ln in path.read_text(encoding="utf-8").splitlines()
                            if not ln.startswith(("> **Escaped-via:**",
                                                  "> **Escaped-verdict:**"))]
                    path.write_text("\n".join(
                        f"> **Shipped-in:** {stored}" if ln.startswith("> **Shipped-in:**")
                        else ln for ln in kept) + "\n", encoding="utf-8")
                    rc, out, err = _cli(["trace", "--bug", filed["id"], "--root", str(root),
                                         "--format", "json"])
                    self.assertEqual(0, rc, err)
                    got = json.loads(out)
                    self.assertEqual(stored, got["release"])
                    self.assertEqual(["US0001"], got["units"])
                    self.assertEqual(["US0001"], [p["unit"] for p in got["proposals"]])
                    before = path.read_bytes()
                    rc, _out, err = _cli(["trace", "--bug", filed["id"], "--confirm", "US0002",
                                          "--root", str(root)])
                    self.assertEqual(2, rc, err)
                    self.assertIn(f"US0002 is not a unit release {stored} shipped", err)
                    self.assertEqual(before, path.read_bytes(), "a refused confirm wrote")
                    rc, _out, err = _cli(["trace", "--bug", filed["id"], "--confirm", "US0001",
                                          "--root", str(root)])
                    self.assertEqual(0, rc, err)
                    lines = path.read_text(encoding="utf-8").splitlines()
                    self.assertIn("> **Escaped-via:** US0001", lines)
                    self.assertIn(f"> **Shipped-in:** {stored}", lines)
            # The resolver itself: either spelling finds the tag, and nothing else does.
            self.assertEqual("v6.4.0", escape.release_tag(root, "6.4.0"))
            self.assertEqual("v6.4.0", escape.release_tag(root, "v6.4.0"))
            self.assertEqual("v6.4.0", escape.release_tag(root, " 6.4.0 "))
            self.assertIsNone(escape.release_tag(root, "V6.4.0"))
            gitutil.git(["tag", "7.0.0"], root)
            self.assertEqual("7.0.0", escape.release_tag(root, "v7.0.0"))
            self.assertEqual("7.0.0", escape.release_tag(root, "V7.0.0"))
            for nothing in ("", "   ", "v", "6.5.0"):
                self.assertIsNone(escape.release_tag(root, nothing), nothing)
            # Where both spellings are tags, the exact one is the release named.
            gitutil.git(["tag", "6.4.0"], root)
            self.assertEqual("6.4.0", escape.release_tag(root, "6.4.0"))
            self.assertEqual("v6.4.0", escape.release_tag(root, "v6.4.0"))



def _span(d: str, *messages: str) -> Path:
    """A project whose v1.0.0 holds one commit per message and v0.9.0 the stories before them:
    US0001, US0003, US0004, US0005 and US0006 each on scripts/a.py. Only the commits after
    v0.9.0 are v1.0.0's own, so a unit counts only where one of `messages` names it."""
    root = Path(d)
    for sub in ("stories", "bugs", "reviews"):
        (root / "sdlc-studio" / sub).mkdir(parents=True)
    gitutil.git(["init", "-q"], root)
    for sid in ("US0001", "US0003", "US0004", "US0005", "US0006"):
        _story(root, sid, "scripts/a.py")
    _commit(root, "chore: start")
    gitutil.git(["tag", "v0.9.0"], root)
    for message in messages:
        _commit(root, message)
    gitutil.git(["tag", "v1.0.0"], root)
    return root


def _trace(root: Path) -> tuple[int, dict, str]:
    rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root), "--format", "json"])
    return rc, (json.loads(out) if rc == 0 else {}), out + err


class EscapeTraceUnitsTests(unittest.TestCase):
    """The units a release shipped are those its commits own - the ids a subject names and a
    `Refs:` trailer names - never an id a `Mentions:` trailer names, which owns no file."""

    def test_a_unit_named_only_in_a_mentions_trailer_is_not_proposed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "docs(D0001): rule the release\n\nMentions: US0005")
            _bug(root)
            rc, _got, said = _trace(root)
            self.assertEqual(2, rc, said)
            self.assertIn("release v1.0.0 tags no unit", said)
            self.assertNotIn("US0005", said)
            self.assertEqual([], escape.release_units(root, "v1.0.0"))

    def test_a_subject_unit_a_mentions_trailer_names_is_not_proposed(self) -> None:
        """The commit-msg hook writes `Mentions:` for a subject id that owns none of the staged
        files, so the subject naming it does not make it shipped; the `Refs:` id beside it is."""
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "docs(US0001, US0005): rule the total\n\n"
                            "Refs: US0001\nmentions:  US0005")
            _bug(root)
            rc, got, said = _trace(root)
            self.assertEqual(0, rc, said)
            self.assertEqual(["US0001"], got["units"])
            self.assertEqual(["US0001"], [p["unit"] for p in got["proposals"]])

    def test_a_subject_or_refs_unit_is_still_proposed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "feat(US0001, US0003): share the total\n\nRefs: US0001\n"
                            "Refs: US0003", "feat(US0006): round the total")
            _bug(root)
            rc, got, said = _trace(root)
            self.assertEqual(0, rc, said)
            self.assertEqual(["US0001", "US0003", "US0006"],
                             sorted(p["unit"] for p in got["proposals"]))
        # A `Refs:` trailer owns its unit even where the subject names none, and a body line that
        # is not a trailer owns nothing.
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "chore: tidy the basket\n\nThe slip came from US0005.\n\n"
                            "Refs: US0004, US0006")
            _bug(root)
            rc, got, said = _trace(root)
            self.assertEqual(0, rc, said)
            self.assertEqual(["US0004", "US0006"], got["units"])


class EscapeTraceDocumentedRulesTests(unittest.TestCase):
    """The rules the module documents: the verdict proposed is the latest APPROVE, not the latest
    row; the escaped bug is never its own cause; a bug with no Affects is refused."""

    def test_the_latest_approve_is_proposed_not_a_later_reject(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "feat(US0001): total the basket")
            _bug(root)
            with contextlib.redirect_stderr(io.StringIO()):
                critic.record_verdict(root, "US0001", "APPROVE", reviewer="Lena Marsh (product)",
                                      author="builder-1")
                critic.record_verdict(root, "US0001", "REJECT", reviewer="Sam Eriksson (qa)",
                                      author="builder-1", issues="a late finding")
            rows = critic.unit_review_rounds(root, "US0001")
            self.assertEqual("REJECT", str(rows[-1]["verdict"]).upper()[:6])
            rc, got, said = _trace(root)
            self.assertEqual(0, rc, said)
            verdict = got["proposals"][0]["verdict"]
            self.assertEqual("APPROVE", verdict["verdict"])
            self.assertEqual("Lena Marsh (product)", verdict["reviewer"])

    def test_the_escaped_bug_is_never_proposed_as_its_own_cause(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "fix(BG0001): an earlier fix", "feat(US0001): total the basket")
            _bug(root)
            self.assertIn("BG0001", escape.release_units(root, "v1.0.0"))
            rc, got, said = _trace(root)
            self.assertEqual(0, rc, said)
            self.assertEqual(["US0001"], got["units"])
            self.assertEqual(["US0001"], [p["unit"] for p in got["proposals"]])
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "fix(BG0001): an earlier fix")
            _bug(root)
            rc, _got, said = _trace(root)
            self.assertEqual(2, rc, said)
            self.assertIn("release v1.0.0 tags no unit", said)

    def test_a_bug_with_no_affects_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _span(d, "feat(US0001): total the basket")
            bug = _bug(root)
            bug.write_text(bug.read_text(encoding="utf-8").replace(
                "> **Affects:** scripts/a.py\n", ""), encoding="utf-8")
            before = _snapshot(root)
            for extra in ([], ["--confirm", "US0001"]):
                rc, out, err = _cli(["trace", "--bug", "BG0001", "--root", str(root),
                                     "--format", "json", *extra])
                self.assertEqual(2, rc, out + err)
                self.assertIn("BG0001 names no Affects", err)
                self.assertNotIn("US0001", out)
            self.assertEqual(before, _snapshot(root))

if __name__ == "__main__":
    unittest.main()
