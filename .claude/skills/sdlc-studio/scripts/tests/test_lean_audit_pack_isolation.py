"""BG0763: the audit-attribution tests that plant a stub or duplicate lens pack must never
write into the shipped `templates/audit-profiles/` folder. Under pytest-xdist a sibling
worker's write there made `LIVE_LENS` ambiguous for every other worker, so
`test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing` failed one run in several
and passed alone every time.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))  # tests/ dir, for its siblings


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _TESTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Loaded under its own name, distinct from pytest's own collected copy of test_file_finding.py,
# so this probe's re-exec (which reloads file_finding.py into sys.modules) never collides with
# it - this module only needs to DRIVE the two tests and inspect the filesystem, not share
# identity with whatever else already imported them.
tff = _load("test_file_finding_isolation_probe", "test_file_finding.py")

PACKS_DIR = Path(tff.ff.__file__).resolve().parent.parent / "templates" / "audit-profiles"


def _snapshot() -> dict[str, bytes]:
    """Every shipped pack's name mapped to its bytes, so a write, a rewrite or a delete
    among them all show up as an inequality with a later snapshot."""
    return {p.name: p.read_bytes() for p in PACKS_DIR.glob("*.md")}


class AuditPackIsolationTests(unittest.TestCase):
    """BG0763 AC1/AC2: the stub/duplicate pack tests write to a per-test override, never the
    shipped `templates/audit-profiles/` folder, and the override is genuinely read rather than
    silently ignored."""

    def test_no_test_writes_into_the_shipped_packs_folder(self) -> None:
        """AC1. Runs the two tests that plant a stub/duplicate pack and diffs the shipped
        folder before and after.

        MUTANT: a fix that only reorders or serialises the two tests, leaving their writes
        aimed at the shipped folder, still fails this - the snapshot comparison does not care
        what order the writes happened in, only where they landed.
        """
        before = _snapshot()
        suite = unittest.TestSuite([
            tff.AuditAttributionUnheldInvariantsTests(
                "test_a_stub_pack_elsewhere_does_not_break_an_unrelated_filing"),
            tff.AuditAttributionUnheldInvariantsTests(
                "test_an_AMBIGUOUS_lens_is_refused_rather_than_resolved_alphabetically"),
        ])
        result = unittest.TestResult()
        suite.run(result)
        after = _snapshot()
        self.assertEqual(
            before, after,
            "a stub or duplicate pack test wrote into the shipped templates/audit-profiles/ "
            "folder instead of a per-test temporary copy")
        self.assertTrue(
            result.wasSuccessful(),
            f"the isolated tests themselves failed: {result.errors + result.failures}")

    def test_the_pack_lookup_reads_the_override_not_the_shipped_folder(self) -> None:
        """AC2. Points `check_audit_attribution`'s lookup at an override folder holding ONLY a
        pack that declares no lens, then files with a lens every SHIPPED pack declares.

        A lookup that reads the override sees no pack owning the lens and refuses, naming the
        override's own (lensless) pack. A lookup that ignores the override and reads the
        shipped folder instead resolves the lens there and either succeeds or names the
        shipped `LIVE_PROFILE` pack - either way this test catches it.
        """
        skill_dir = Path(tempfile.mkdtemp(prefix="packs_override_"))
        self.addCleanup(shutil.rmtree, skill_dir, ignore_errors=True)
        (skill_dir / "templates" / "audit-profiles").mkdir(parents=True)
        stub = skill_dir / "templates" / "audit-profiles" / "zz-override-only.md"
        stub.write_text("# A pack declaring no lens\n\nTBD.\n", encoding="utf-8")

        root = Path(tempfile.mkdtemp(prefix="attr_override_"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        tff._seed_index(root, "bug")
        for rel in tff.GROOM["affects"].split(", "):
            tff._affect(root, rel.strip())
        rid = tff._register(root)

        with unittest.mock.patch.dict(
                os.environ, {tff.ff.AUDIT_PACKS_SKILL_DIR_ENV: str(skill_dir)}):
            with self.assertRaises(ValueError) as ctx:
                tff.ff.file_finding(root, "bug", "x",
                                     {**tff.BUG, "lens": tff.LIVE_LENS, "audit_run": rid})
        msg = str(ctx.exception)
        self.assertIn(
            "zz-override-only", msg,
            "the refusal does not name the override folder's own pack, so the lookup ignored "
            "the override and read the shipped folder instead")
        self.assertNotIn(
            tff.LIVE_PROFILE, msg,
            f"{tff.LIVE_PROFILE!r} is a SHIPPED pack name; seeing it in the refusal means the "
            "lookup read the shipped folder, not the override")


if __name__ == "__main__":
    unittest.main()
