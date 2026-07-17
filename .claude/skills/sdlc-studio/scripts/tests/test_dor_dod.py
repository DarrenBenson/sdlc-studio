"""DoR/DoD documents + check-id registry (RED first).

The two editable documents are the single source of the project's ready and done
bars; an enforceable criterion carries a [check: <id>] tag resolving through ONE
registered vocabulary. An unknown id is a loud validation error - a tag nothing
enforces would be human intent silently unenforced.
"""
from __future__ import annotations

import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import loader  # noqa: E402

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

TEMPLATES = SCRIPTS.parent / "templates" / "core"


class RegistryTests(unittest.TestCase):
    """One authority module holds the check-id vocabulary; the shipped templates
    tag only registered ids and cover every level."""

    def test_registry_lives_in_one_authority_module(self):
        reg = sdlc_md.DOR_DOD_CHECK_IDS
        self.assertIsInstance(reg, dict)
        self.assertGreaterEqual(len(reg), 8)
        for cid, desc in reg.items():
            self.assertRegex(cid, r"^[a-z0-9]+(\.[a-z0-9-]+)+$")
            self.assertTrue(desc.strip(), f"{cid} has no description")

    def test_registry_names_the_existing_gates(self):
        # The bar maps to checks that EXIST - grooming, verify-ac, critic, close, release.
        for expected in ("grooming.affects", "grooming.points", "story.verify-ac",
                         "review.critic-approve", "close.retro", "release.gate"):
            self.assertIn(expected, sdlc_md.DOR_DOD_CHECK_IDS)

    def test_check_tags_parse(self):
        text = ("- [ ] Affects declared [check: grooming.affects]\n"
                "- [ ] judged by a human, untagged\n"
                "- [ ] ACs pass [check: story.verify-ac]\n")
        self.assertEqual(sdlc_md.check_tags(text),
                         ["grooming.affects", "story.verify-ac"])

    def test_shipped_templates_exist_tag_registered_ids_and_cover_levels(self):
        for name in ("definition-of-ready.md", "definition-of-done.md"):
            path = TEMPLATES / name
            self.assertTrue(path.is_file(), f"{name} not shipped")
            text = path.read_text(encoding="utf-8")
            tags = sdlc_md.check_tags(text)
            self.assertGreaterEqual(len(tags), 3, f"{name} has too few enforceable criteria")
            self.assertEqual(sdlc_md.unknown_check_ids(text), [],
                             f"{name} tags an unregistered id")
            for level in ("Story", "Sprint", "Release"):
                self.assertIn(f"## {level}", text, f"{name} missing the {level} level")

    def test_templates_state_the_never_weaken_rule(self):
        for name in ("definition-of-ready.md", "definition-of-done.md"):
            text = (TEMPLATES / name).read_text(encoding="utf-8")
            self.assertIn("never weaken the bar", text)


class UnknownCheckIdTests(unittest.TestCase):
    """An unknown check id is a loud validation error, never silently unenforced."""

    def test_unknown_ids_are_listed(self):
        text = ("- [ ] real [check: grooming.affects]\n"
                "- [ ] typo [check: groomin.affects]\n"
                "- [ ] invented [check: vibes.good]\n")
        self.assertEqual(sdlc_md.unknown_check_ids(text),
                         ["groomin.affects", "vibes.good"])

    def test_validate_flags_unknown_id_in_project_document(self):
        validate = loader.load_script("validate")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / "definition-of-done.md").write_text(
                "# Definition of Done\n\n## Story\n\n"
                "- [ ] ACs pass [check: story.verify-ac]\n"
                "- [ ] good vibes [check: vibes.good]\n", encoding="utf-8")
            args = validate.build_parser().parse_args(["check", "--root", str(root)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = args.func(args)
            self.assertEqual(rc, 1)   # loud: the run FAILS
            self.assertIn("vibes.good", out.getvalue())
            self.assertIn("ERROR", out.getvalue())

    def test_validate_passes_registered_only_document(self):
        validate = loader.load_script("validate")
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / "definition-of-ready.md").write_text(
                "# Definition of Ready\n\n## Story\n\n"
                "- [ ] Affects declared [check: grooming.affects]\n"
                "- [ ] a human-judged criterion, untagged\n", encoding="utf-8")
            args = validate.build_parser().parse_args(["check", "--root", str(root)])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(args.func(args), 0)

    def test_untagged_criteria_are_not_errors(self):
        # Untagged = explicitly human-judged; only a BAD tag errors.
        self.assertEqual(sdlc_md.unknown_check_ids("- [ ] judged by the operator\n"), [])


if __name__ == "__main__":
    unittest.main()
