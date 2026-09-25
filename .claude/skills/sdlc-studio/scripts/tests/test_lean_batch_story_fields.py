"""BG0755: both story creators write the user story they are given, and a batch is lean by default.

Sprint 3's 37 stories were minted with `artifact.py batch` carrying `role`, `capability` and
`benefit`; the batch dropped all three in silence and wrote the full template's page of
placeholder sections, and the single-item `new --fields-file` refused the three keys outright.
Every test drives the shipped CLI against a fresh `init` project, the shape a user meets.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
import artifact  # noqa: E402

CORE_STORY = SCR.parent / "templates" / "core" / "story.md"

USER_STORY = {"role": "founder-engineer running the loop",
              "capability": "stories minted with their user story written",
              "benefit": "nobody trims a page of placeholders by hand"}


def _run(root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCR / script), "--root", str(root), *argv],
                          capture_output=True, text=True, cwd=root, timeout=120)


class BatchStoryFieldsTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        init = _run(self.root, "init.py", "run")
        self.assertEqual(init.returncode, 0, init.stderr)
        epic = _run(self.root, "artifact.py", "new", "--type", "epic", "--title", "Parent epic",
                    "--size", "M", "--format", "json")
        self.assertEqual(epic.returncode, 0, epic.stderr)
        self.epic = json.loads(epic.stdout)["id"]
        (self.root / "src").mkdir()
        (self.root / "src" / "thing.py").write_text("", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_thing.py").write_text("def test_it():\n    pass\n",
                                                           encoding="utf-8")

    def _item(self, title: str, **extra) -> dict:
        return {"title": title, "epic": self.epic, "points": 2, "affects": "src/thing.py",
                "acs": ["the thing works"], "verify": ["pytest tests/test_thing.py::test_it"],
                **USER_STORY, **extra}

    def _batch(self, items: list[dict], *argv: str) -> subprocess.CompletedProcess:
        spec = self.root / "spec.json"
        spec.write_text(json.dumps(items), encoding="utf-8")
        return _run(self.root, "artifact.py", "batch", "--type", "story", "--spec", str(spec),
                    "--format", "json", *argv)

    def _story(self, title_slug: str) -> str:
        found = list((self.root / "sdlc-studio" / "stories").glob(f"*-{title_slug}.md"))
        self.assertEqual(len(found), 1, f"expected one story file for {title_slug}: {found}")
        return found[0].read_text(encoding="utf-8")

    def _assert_user_story(self, text: str, where: str) -> None:
        for label, key in (("As a", "role"), ("I want", "capability"), ("So that", "benefit")):
            self.assertIn(f"**{label}** {USER_STORY[key]}\n", text, f"{where}: {label}")
            self.assertNotIn("{{" + key + "}}", text, where)
        # The full template's Context section names a persona slot of its own; the User Story
        # block is what these three fields fill.
        block = text.split("## User Story", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("{{", block, where)

    def test_batch_fills_the_user_story_block(self) -> None:
        # Every template, not only the default: Sprint 5's units were minted under `planning`,
        # whose User Story block carries `{{persona_name}}` rather than `{{role}}`.
        for template in (None, "minimal", "planning", "full"):
            with self.subTest(template=template):
                title = f"filled {template or 'default'}"
                argv = ("--template", template) if template else ()
                proc = self._batch([self._item(title)], *argv)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self._assert_user_story(self._story(f"filled-{template or 'default'}"),
                                        str(template))

    def test_each_field_is_written_on_its_own_line_and_only_there(self) -> None:
        # A break inside a value would split the line it belongs to.
        item = self._item("one line", role="founder-engineer\n  running the loop")
        proc = self._batch([item], "--template", "planning")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("**As a** founder-engineer running the loop\n", self._story("one-line"))
        # Only the first `**As a**` line - the User Story block's - is filled: a template's own
        # prose further down that repeats the label (a house template's worked example) is kept.
        body = ("## User Story\n\n**As a** {{role}}\n\n## Example\n\n"
                "**As a** support agent (example)\n")
        filled = artifact._fill_user_story(body, "story", {"role": "tester"})
        self.assertIn("**As a** tester\n", filled)
        self.assertIn("**As a** support agent (example)\n", filled)

    def test_a_user_story_field_that_is_not_text_is_refused(self) -> None:
        proc = self._batch([self._item("listed", role=["a", "b"])])
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("'role' must be text", proc.stderr)
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"title": "listed too", "epic": self.epic, "benefit": 3}),
                       encoding="utf-8")
        proc = _run(self.root, "artifact.py", "new", "--type", "story", "--fields-file", str(doc))
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("'benefit' must be text", proc.stderr)
        self.assertEqual([p for p in (self.root / "sdlc-studio" / "stories").glob("*.md")
                          if p.name != "_index.md"], [])
        # The positive control: the same item with text creates.
        proc = self._batch([self._item("listed")])
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_a_user_story_field_on_another_type_is_refused(self) -> None:
        # Accepted by the fields-file key set, stored only by a story: never dropped at exit 0.
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"title": "an epic with a role", "role": "someone",
                                   "size": "M"}), encoding="utf-8")
        proc = _run(self.root, "artifact.py", "new", "--type", "epic", "--fields-file", str(doc))
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("'role'", proc.stderr)

    def test_new_fills_the_user_story_block(self) -> None:
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"title": "one at a time", "epic": self.epic,
                                   **USER_STORY}), encoding="utf-8")
        proc = _run(self.root, "artifact.py", "new", "--type", "story", "--fields-file", str(doc))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self._assert_user_story(self._story("one-at-a-time"), "new")

    def test_the_batch_default_is_the_lean_shape(self) -> None:
        proc = self._batch([self._item("lean by default")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lean = self._story("lean-by-default")
        self.assertNotIn("{{", lean, "the default batch story carries a placeholder")

        proc = self._batch([self._item("full on request")], "--template", "full")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        full = self._story("full-on-request")
        # The full template's own sections, read from the template rather than listed here.
        sections = re.findall(r"^## .+$", CORE_STORY.read_text(encoding="utf-8"), re.M)
        self.assertGreater(len(sections), 5, "the full story template lost its sections")
        for heading in sections:
            self.assertIn(heading, full, f"--template full dropped {heading}")
        for heading in sections:
            if heading not in ("## User Story", "## Acceptance Criteria", "## Revision History"):
                self.assertNotIn(heading, lean, f"the lean default carries {heading}")

    def test_an_unknown_batch_key_is_refused(self) -> None:
        item = self._item("misspelt")
        item["rol"] = item.pop("role")
        proc = self._batch([self._item("clean first"), item])
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("rol", proc.stderr)
        self.assertIn("unknown", proc.stderr)
        # All-or-nothing: the clean item before it was not written either.
        stories = [p.name for p in (self.root / "sdlc-studio" / "stories").glob("*.md")
                   if p.name != "_index.md"]
        self.assertEqual(stories, [])

        # The positive control: the correctly spelt key creates.
        proc = self._batch([self._item("spelt right")])
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
