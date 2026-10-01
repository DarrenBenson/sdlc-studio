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
sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

init = loader.load_script("init")
review_prep = loader.load_script("review_prep")

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

    def _epic(self) -> str:
        spec = self.root / "spec.json"
        spec.write_text(json.dumps([{"title": "An epic"}]), encoding="utf-8")
        out = _cli("artifact.py", "batch", "--type", "epic", "--spec", str(spec),
                   "--root", str(self.root), "--format", "json").stdout
        return next(e for e in sdlc_md.ID_SEARCH_RE.findall(out) if e.startswith("EP"))

    def _hint(self) -> dict:
        return json.loads(_cli("status.py", "hint", "--root", str(self.root),
                               "--format", "json").stdout)

    def test_a_filled_registry_moves_the_hint_past_persona(self) -> None:
        """Round-1 repro (BG0881). Guided onboarding through every stage, then the registry
        filled and an epic added: the hint moves to `story`. MUTANT: count `personas.md` alone
        as personas present (HEAD's status.py:375) - the hint sticks on `persona` for every
        guided project. The seeded registry, still empty, is not personas: before it is filled
        the hint stays on `persona`, which is the honest answer."""
        for _ in range(10):
            state = json.loads(_cli("init.py", "guided", "--root", str(self.root),
                                    "--format", "json").stdout)
            if state["current"] is None:
                break
            _cli("init.py", "guided", "--root", str(self.root), "--confirm")
        self.assertEqual("persona", self._hint()["next_command"])
        index = self.root / "sdlc-studio" / "personas" / "index.md"
        text = index.read_text(encoding="utf-8")
        index.write_text(text.replace("## Primary\n", "## Primary\n\n- **Maya Okafor** - the "
                                      "operator who runs the sprint\n", 1), encoding="utf-8")
        self.assertEqual(1, len(sdlc_md.persona_registry(self.root).entries))
        self._epic()
        hint = self._hint()
        self.assertEqual("story", hint["next_command"], hint)
        legs = review_prep.required_legs(self.root)
        self.assertTrue(legs["personas"]["present"], legs["personas"])

    def test_the_seeded_registry_reads_as_a_seed(self) -> None:
        """`_is_seed` maps the registry to its template, so the runner says the tool drafted it.
        MUTANT: map personas to the old core/personas.md - the seeded registry reads as the
        user's work, and the guided runner says `already present`."""
        self._guided_to_personas()
        self.assertTrue(init._is_seed(self.root, "sdlc-studio/personas/index.md"))
        self.assertFalse(init._is_seed(self.root, "sdlc-studio/personas.md"))
        text = _cli("init.py", "guided", "--root", str(self.root)).stdout
        self.assertIn("sdlc-studio/personas/index.md seeded from its template", text)

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
