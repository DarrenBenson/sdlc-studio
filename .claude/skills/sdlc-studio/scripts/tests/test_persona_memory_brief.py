"""A persona's brief carries its own live learnings, capped, ranked and bounded.

`critic.py brief --seat <seat>` and `persona_resolve.py resolve` / `resolve-consult` read the
seat's memory file (`sdlc-studio/personas/memory/<seat>.md`) through `persona_memory.digest`
and `render`. Every case drives the shipped entry points in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/persona_memory.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CARD = ("<!-- role: {role} -->\n# Sam - {role} seat\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n"
        "## Shadow\n\nx\n")
LONG = "Long learning sentence. " * 210  # about 5,000 characters


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _story(root: Path, sid: str, affects: str) -> None:
    _write(root, f"sdlc-studio/stories/{sid}-s.md",
           f"# {sid}: s\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _entry(id_: str, title: str, body: str = "Short learning.", state: str = "approved",
           added: str = "2026-10-01", review_by: str = "2099-01-01",
           evidence: str = "US0001") -> str:
    return (f"\n## {id_}: {title}\n\n- **Persona:** x\n- **Evidence:** {evidence}\n"
            f"- **Added:** {added}\n- **Review-by:** {review_by}\n- **State:** {state}\n\n"
            f"{body}\n")


def _memory(root: Path, key: str, entries: list[str]) -> None:
    _write(root, f"sdlc-studio/personas/memory/{key}.md",
           f"# Persona Memory: {key}\n" + "".join(entries))


def _run(script: str, *args: str) -> str:
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *args],
                       capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                       check=False)
    assert r.returncode == 0, r.stderr
    return r.stdout


class PersonaMemoryBriefTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for role in ("qa", "product"):
            _write(self.root, f"sdlc-studio/personas/seats/{role}.md", CARD.format(role=role))
        _write(self.root, "scripts/a.py", "x = 1\n")
        _story(self.root, "US0001", "scripts/a.py, src/w.py")

    def tearDown(self):
        self._tmp.cleanup()

    def brief(self, unit: str = "US0001", seat: str = "qa") -> str:
        return _run("critic.py", "brief", "--unit", unit, "--seat", seat, "--root",
                    str(self.root))

    def _seven_and_more(self) -> None:
        qa = [_entry(f"M-000{n}", f"Qa learning {n}", LONG if n == 3 else "Short learning.",
                     added=f"2026-10-0{n}") for n in range(1, 8)]
        qa.append(_entry("M-0008", "Qa proposed one", state="proposed", added="2026-10-09"))
        qa.append(_entry("M-0009", "Qa expired one", added="2026-10-09", review_by="2000-01-01"))
        _memory(self.root, "qa", qa)
        _memory(self.root, "product", [_entry("M-0010", "Product learning ten"),
                                       _entry("M-0011", "Product learning eleven")])

    def test_the_review_brief_carries_its_own_seats_capped_bounded_learnings(self):
        self._seven_and_more()
        out = self.brief()
        carried = sorted(set(re.findall(r"\bM-00(?:0[1-7])\b", out)))
        # The five newest live ones; the cap withholds the two oldest.
        self.assertEqual(carried, ["M-0003", "M-0004", "M-0005", "M-0006", "M-0007"])
        for absent in ("M-0008", "M-0009", "M-0010", "M-0011", "Product learning"):
            self.assertNotIn(absent, out)
        self.assertRegex(out, r"\+2 more live, withheld by the cap of 5")
        self.assertRegex(out, r"1 approved learning past its Review-by horizon")
        [line] = [ln for ln in out.splitlines() if "M-0003" in ln]
        self.assertIn("Qa learning 3", line)
        gist = line.split("Qa learning 3: ", 1)[1]
        self.assertLessEqual(len(gist), 200)
        self.assertTrue(gist.startswith("Long learning sentence."))
        self.assertNotIn(LONG.strip()[:400], out)

    def test_a_learning_whose_evidence_shares_the_units_files_outranks_a_newer_one(self):
        _story(self.root, "US0005", "scripts/a.py")
        _story(self.root, "US0006", "docs/x.md")
        _story(self.root, "US0002", "other/z.py")
        _memory(self.root, "qa", [
            _entry("M-0001", "Older relevant", added="2026-09-01", evidence="US0005"),
            _entry("M-0002", "Newer unrelated", added="2026-10-01", evidence="US0006")])
        _write(self.root, "sdlc-studio/.config.yaml", "personas:\n  memory:\n    inject_max: 1\n")
        out = self.brief("US0001")
        self.assertIn("M-0001 Older relevant", out)
        self.assertNotIn("M-0002", out)
        self.assertIn("+1 more live, withheld by the cap of 1", out)
        # Control: for a unit sharing no file with either, recency decides.
        out = self.brief("US0002")
        self.assertIn("M-0002 Newer unrelated", out)
        self.assertNotIn("M-0001", out)

    def test_every_persona_resolve_framing_carries_its_own_seats_learnings(self):
        self._seven_and_more()
        root = str(self.root)
        for render, out in (
                ("build", _run("persona_resolve.py", "resolve", "--seat", "qa", "--render",
                               "build", "--root", root)),
                ("review", _run("persona_resolve.py", "resolve-consult", "--role", "qa",
                                "--root", root))):
            with self.subTest(render=render):
                self.assertIn(f"--- LEARNINGS: qa ({render} render) ---", out)
                self.assertIn("M-0007 Qa learning 7", out)
                self.assertNotIn("M-0010", out)
                self.assertNotIn("Product learning", out)
        # The product seat's framing carries product's and not qa's.
        out = _run("persona_resolve.py", "resolve", "--seat", "product", "--render", "review",
                   "--root", root)
        self.assertIn("--- LEARNINGS: product (review render) ---", out)
        self.assertIn("M-0010", out)
        self.assertNotIn("Qa learning", out)
        # --skip-personas still frames nothing at all.
        self.assertEqual(_run("persona_resolve.py", "resolve", "--seat", "qa",
                              "--skip-personas", "--root", root).strip(), "")

    def test_unreadable_and_absent_memory_are_told_apart(self):
        _memory(self.root, "qa", ["\n## M-12: not an entry heading\n\nbody\n"])
        out = self.brief()
        self.assertIn("Learnings for qa could not be read", out)
        self.assertIn("sdlc-studio/personas/memory/qa.md", out)
        self.assertNotIn("none recorded", out)
        (self.root / "sdlc-studio" / "personas" / "memory" / "qa.md").unlink()
        out = self.brief()
        self.assertIn("Learnings for qa: none recorded", out)
        self.assertNotIn("could not be read", out)


if __name__ == "__main__":
    unittest.main()
