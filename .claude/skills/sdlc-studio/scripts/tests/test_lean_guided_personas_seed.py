"""BG0824: guided onboarding seeds the persona registry v6 reads, not the legacy flat file.

`init guided`'s personas stage seeded `sdlc-studio/personas.md`, the legacy fallback, while
`sdlc_md.persona_registry`, `sprint plan --serves` and the goal trace read
`sdlc-studio/personas/index.md`. A user who filled the seeded file got no personas where they are
read. The story index template pointed at the same flat file and still said stories are numbered
`US0001, US0002` on a project that mints ULIDs. Each test drives the shipped CLIs in a throwaway
project.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import sdlc_md  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent


def _cli(script: str, *argv: str) -> subprocess.CompletedProcess:
    proc = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=120)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(argv)} exited {proc.returncode}:\n"
                             f"{proc.stdout}{proc.stderr}")
    return proc


class GuidedPersonasSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        _cli("init.py", "run", "--root", str(self.root))

    def _guided_to_personas(self) -> dict:
        """Walk `init guided` stage by stage, confirming each, until it drafts personas."""
        for _ in range(10):
            out = json.loads(_cli("init.py", "guided", "--root", str(self.root),
                                  "--format", "json").stdout)
            if out["current"] == "personas":
                return out
            _cli("init.py", "guided", "--root", str(self.root), "--confirm")
        self.fail("guided onboarding never reached the personas stage")

    def test_the_registry_is_seeded(self) -> None:
        """AC1. MUTANT: HEAD, which seeds `sdlc-studio/personas.md` and leaves `personas/`
        absent. MUTANT: seed the index from a template with no Primary/Secondary/Negative heading
        - the registry then reads `declares no Primary/Secondary/Negative heading`."""
        out = self._guided_to_personas()
        self.assertEqual(["sdlc-studio/personas/index.md"], out["drafted"]["created"])
        index = self.root / "sdlc-studio" / "personas" / "index.md"
        text = index.read_text(encoding="utf-8")
        for heading in ("## Primary", "## Secondary", "## Negative"):
            self.assertIn(heading, text)
        registry = sdlc_md.persona_registry(self.root)
        self.assertTrue(registry.available, registry.reason)
        self.assertEqual((), tuple(registry.entries))
        self.assertFalse((self.root / "sdlc-studio" / "personas.md").exists())
        # The seeded registry is read as the stage's draft, not as authored work, so the stage
        # stays open for review rather than being marked done underneath the operator.
        again = json.loads(_cli("init.py", "guided", "--root", str(self.root),
                                "--format", "json").stdout)
        self.assertEqual("personas", again["current"])

    def test_the_story_index_links_the_registry(self) -> None:
        """AC2. MUTANT: HEAD's `[User Personas](../personas.md)` link and the sequential
        numbering note."""
        spec = self.root / "spec.json"
        spec.write_text(json.dumps([{"title": "An epic"}]), encoding="utf-8")
        epic = json.loads(_cli("artifact.py", "batch", "--type", "epic", "--spec", str(spec),
                               "--root", str(self.root), "--format", "json").stdout)
        epic_id = json.dumps(epic)
        epic_id = next(e for e in sdlc_md.ID_SEARCH_RE.findall(epic_id) if e.startswith("EP"))
        spec.write_text(json.dumps([{"title": "A story", "epic": epic_id}]), encoding="utf-8")
        _cli("artifact.py", "batch", "--type", "story", "--spec", str(spec),
             "--root", str(self.root))
        text = (self.root / "sdlc-studio" / "stories" / "_index.md").read_text(encoding="utf-8")
        self.assertIn("](../personas/index.md)", text)
        self.assertNotIn("../personas.md", text)
        self.assertNotIn("US0001, US0002", text)


if __name__ == "__main__":
    unittest.main()
