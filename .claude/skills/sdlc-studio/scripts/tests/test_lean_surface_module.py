"""BG0758: the surface module judged is the judged tree's own, whatever the process has cached.

`command_audit._surface_module` resolved `import surface`, so once anything in the process had
imported the dev repo's `lib/surface.py` (test_docgen does, at import), a fixture tree was
judged with the dev module - and a tree with no surface module at all read as measured.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
command_audit = loader.load_script("command_audit")
sprint_report = loader.load_script("sprint_report")


def _dev_surface():
    """The dev repo's `surface`, cached under that name the way test_docgen leaves it."""
    lib = str(_SCRIPTS / "lib")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import surface  # noqa: PLC0415
    assert Path(surface.__file__).resolve() == (_SCRIPTS / "lib" / "surface.py").resolve()
    return surface


def _skill_tree(root: Path) -> Path:
    skill = root / ".claude" / "skills" / "sdlc-studio"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
    return skill


class SurfaceModuleTests(unittest.TestCase):
    def test_the_judged_trees_own_surface_module_is_loaded_whatever_is_cached(self) -> None:
        dev = _dev_surface()
        with tempfile.TemporaryDirectory(prefix="bg0758_") as tmp:
            skill = _skill_tree(Path(tmp))
            lib = skill / "scripts" / "lib"
            lib.mkdir(parents=True)
            (lib / "surface.py").write_text("MARK = 'fixture'\n", encoding="utf-8")
            mod = command_audit._surface_module(skill)
            self.assertEqual(getattr(mod, "MARK", None), "fixture",
                             "the dev repo's cached `surface` was returned for a fixture tree")
            self.assertEqual(Path(mod.__file__).resolve(), (lib / "surface.py").resolve())
        self.assertIs(sys.modules.get("surface"), dev,
                      "the fixture's module was left cached under `surface` for the next caller")

    def test_a_tree_with_no_surface_module_reads_unreadable_in_process(self) -> None:
        _dev_surface()
        with tempfile.TemporaryDirectory(prefix="bg0758_") as tmp:
            root = Path(tmp)
            _skill_tree(root)
            (root / "sdlc-studio").mkdir()
            with self.assertRaises(ModuleNotFoundError, msg="the dev repo's verbs were counted"):
                command_audit.verb_coverage(tmp)
            proc = subprocess.run(
                [sys.executable, "-B", str(_SCRIPTS / "sprint_report.py"), "--root", tmp,
                 "checklist", "--id", "RETRO0001", "--format", "json"],
                capture_output=True, text=True, timeout=120)
            cli = next(r for r in json.loads(proc.stdout)["items"] if r["id"] == "doc-surface")
            state, value, detail = sprint_report._ck_doc_surface({"root": root})
        self.assertEqual(value, "unreadable", detail)
        self.assertEqual((state, value, detail), (cli["state"], cli["value"], cli["detail"]),
                         "the in-process close row and the CLI's disagree")


if __name__ == "__main__":
    unittest.main()
