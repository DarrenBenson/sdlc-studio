"""Tests for the lite profile (US0071).

Lite collapses the pipeline to PRD -> story -> implement: no TRD/TSD/persona/epic
ceremony and no nag about their absence, while AC verification and reconcile work
identically. It is promotable to the full profile, inserting an epic above the
existing stories.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

init = _load("init")
status = _load("status")
artifact = _load("artifact")
reconcile = _load("reconcile")
lite_profile = _load("lite_profile")


def _lite_repo(profile: str = "lite", with_prd: bool = True) -> Path:
    d = Path(tempfile.mkdtemp())
    init.init(d)
    (d / "sdlc-studio" / ".config.yaml").write_text(f"profile: {profile}\n", encoding="utf-8")
    if with_prd:
        (d / "sdlc-studio" / "prd.md").write_text("# PRD\n\n> **Status:** Approved\n",
                                                  encoding="utf-8")
    return d


class TestLiteProfile(unittest.TestCase):
    def test_profile_reader_defaults_to_full(self):
        d = Path(tempfile.mkdtemp())
        init.init(d)
        self.assertEqual(sdlc_md.profile(d), "full")

    def test_profile_reader_reads_lite(self):
        d = _lite_repo()
        self.assertEqual(sdlc_md.profile(d), "lite")

    def test_lite_hint_after_prd_is_story_not_trd_or_epic(self):
        d = _lite_repo()
        hint = status.compute_hint(status.gather(d), d)
        self.assertEqual(hint["next_command"], "story")
        self.assertNotIn("TRD", hint["reason"])
        self.assertNotIn("epic", hint["reason"].lower())

    def test_lite_no_epic_nag_when_stories_present(self):
        d = _lite_repo()
        artifact.new(d, "story", "First capability")
        hint = status.compute_hint(status.gather(d), d)
        self.assertNotIn("epic", hint["reason"].lower())
        self.assertNotEqual(hint["next_command"], "epic")

    def test_lite_story_created_without_epic(self):
        d = _lite_repo()
        r = artifact.new(d, "story", "First capability")
        self.assertTrue(Path(r["path"]).exists())
        self.assertIsNone(r["epic_linked"])
        self.assertEqual(len(list((d / "sdlc-studio" / "epics").glob("EP*.md"))), 0)

    def test_full_profile_still_requires_epic(self):
        d = _lite_repo(profile="full")
        with self.assertRaises(ValueError):
            artifact.new(d, "story", "Needs an epic")

    def test_lite_reconcile_clean_without_epics(self):
        d = _lite_repo()
        artifact.new(d, "story", "First capability")
        artifact.new(d, "story", "Second capability")
        res = reconcile.detect_type("story", d)
        self.assertEqual(res["drift"], [], f"lite project drifted: {res}")

    def test_promote_inserts_epic_above_stories(self):
        d = _lite_repo()
        artifact.new(d, "story", "First capability")
        artifact.new(d, "story", "Second capability")
        result = lite_profile.promote(d)
        epics = list((d / "sdlc-studio" / "epics").glob("EP*.md"))
        self.assertEqual(len(epics), 1, "promotion did not create exactly one epic")
        epic_text = epics[0].read_text(encoding="utf-8")
        self.assertIn("US0001", epic_text)
        self.assertIn("US0002", epic_text)
        self.assertEqual(sdlc_md.profile(d), "full", "config not flipped to full")
        # every story now names the epic
        for sp in (d / "sdlc-studio" / "stories").glob("US*.md"):
            self.assertIn(result["epic"], sp.read_text(encoding="utf-8"))
        # and the workspace reconciles clean
        self.assertEqual(reconcile.detect_type("story", d)["drift"], [])
        self.assertEqual(reconcile.detect_type("epic", d)["drift"], [])




class StoryTitleParseTests(unittest.TestCase):
    def test_story_title_reads_the_h1(self) -> None:
        # Kills the surviving invert-guard mutant on the H1 parser.
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "US0001-login.md"
            p.write_text("# US0001: Login flow\n\nbody\n", encoding="utf-8")
            self.assertEqual(lite_profile._story_title(p), "Login flow")


if __name__ == "__main__":
    unittest.main()
