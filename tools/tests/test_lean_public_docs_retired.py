"""US0954: the repository's front door (README, CONTRIBUTING, the install guide) describes v6.

A newcomer reads these three pages before any file under the skill, so a retired verb, flag, key or
phrase here is the first thing they learn wrongly. The retired surface is IMPORTED from US0924's
`retired_surface` module, which derives it from the code's registries, never restated here: a
second hand list is one somebody must remember to extend at the next retirement.

The release a page pins or calls current is read from `check_versions.py`'s homes, so the cut's
version bump reddens this module until the pins move with it.

Every document another unit adds to the front door adds its test here, through
`live_outside_removed`.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"))
import retired_surface  # noqa: E402

_spec = importlib.util.spec_from_file_location("check_versions",
                                               REPO / "tools" / "check_versions.py")
check_versions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_versions)

README = REPO / "README.md"
FRONT_DOOR = ("README.md", "CONTRIBUTING.md", "docs/INSTALL.md")

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def live_outside_removed(text: str) -> list[tuple[int, str, str]]:
    """`retired_surface.live_mentions` over `text` with every 'Removed in v6' passage blanked:
    a heading naming it, down to the next heading at the same or a higher level. Lines are
    blanked rather than dropped, so a reported line number is the line a reader opens."""
    out, level = [], 0
    for line in text.splitlines():
        m = _HEADING.match(line)
        if m and level and len(m.group(1)) <= level:
            level = 0
        if m and not level and re.search(r"(?i)\bremoved in v6\b", m.group(2)):
            level = len(m.group(1))
        out.append("" if level else line)
    return retired_surface.live_mentions("\n".join(out) + "\n")


def release() -> str:
    """The full version the version homes declare (`6.0.0-rc.1`, not its core): the tag a
    verified install must pin, since only a published tag carries a checksum."""
    version = check_versions.from_package_json(REPO)
    if not version:
        raise AssertionError("package.json declares no version, so no pin can be checked")
    return version


def _section(text: str, heading: str) -> str:
    """The body under the first `## ` heading starting with `heading`, to the next `## `."""
    m = re.search(rf"^## {re.escape(heading)}.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def _split_fences(text: str) -> tuple[str, list[str]]:
    """(`text` with fenced blocks blanked, the fenced blocks' bodies)."""
    prose, blocks, block = [], [], None
    for line in text.splitlines():
        if _FENCE.match(line):
            if block is None:
                block = []
            else:
                blocks.append("\n".join(block))
                block = None
            prose.append("")
            continue
        prose.append("" if block is not None else line)
        if block is not None:
            block.append(line)
    return "\n".join(prose), blocks


def _without_fences(text: str) -> str:
    """`text` with fenced blocks blanked: sample output shows what a tool prints elsewhere."""
    return _split_fences(text)[0]


def _verified_installs(text: str) -> list[str]:
    """Each fenced command that makes the checksum mandatory, continuation lines joined."""
    commands = []
    for block in _split_fences(text)[1]:
        for cmd in re.sub(r"\\\n\s*", " ", block).splitlines():
            if "SDLC_STUDIO_REQUIRE_CHECKSUM=1" in cmd:
                commands.append(cmd.strip())
    return commands


class PublicDocsTests(unittest.TestCase):

    def test_the_front_door_teaches_no_retired_surface(self) -> None:
        """AC1. MUTANTS: HEAD README 136 '**verification-depth tiers** (a bug cannot reach Fixed'
        restored; `VF -->|two-role review + sign-off| DN[Done]` restored; `two-role review` put
        back among the site's concept guides."""
        for rel in FRONT_DOOR:
            hits = live_outside_removed((REPO / rel).read_text(encoding="utf-8"))
            with self.subTest(doc=rel):
                self.assertEqual([], hits, f"{rel} teaches a retired surface outside a "
                                           f"'Removed in v6' passage: {hits}")

    def test_a_removed_in_v6_passage_excuses_only_itself(self) -> None:
        """The helper's own discrimination: blanking must stop at the passage's end."""
        text = ("## New\n\n### Removed in v6\n\nThe repair plan goes.\n\n"
                "### Loop\n\nWrite a repair plan.\n")
        hits = live_outside_removed(text)
        self.assertEqual([(9, "a repair plan", "Write a repair plan.")], hits)

    def test_the_readme_leads_with_v6(self) -> None:
        """AC2. MUTANTS: the `## New in 5.1` section restored first; the loop link dropped; the
        FAQ upgrade answer without `migrate --apply`; routes to docs/existing-users.md cut from
        four to two; a route's paragraph calling v6 a drop-in."""
        text = README.read_text(encoding="utf-8")
        version = release()
        self.assertTrue(version.startswith("6."), f"the version homes declare {version}")
        body = text.split("</div>", 1)[1]
        first = re.search(r"^## (.*)$", body, re.M)
        self.assertIsNotNone(first, "README has no section after the badges")
        self.assertTrue(first.group(1).startswith("New in 6"),
                        f"README's first section after the badges is '{first.group(1)}'")
        lead = _section(body, "New in 6")
        self.assertIn(f"(docs/release-notes-v{version}.md)", lead,
                      f"'New in 6' does not link the {version} release notes")
        self.assertRegex(lead, r"\(\.claude/skills/sdlc-studio/reference-sprint\.md#the-loop\)",
                         "'New in 6' does not link the loop")
        faq = re.search(r"<summary>How do I upgrade\?</summary>(.*?)</details>", text, re.S)
        self.assertIsNotNone(faq, "README's FAQ has no upgrade answer")
        self.assertIn("migrate --apply", faq.group(1))
        self.assertRegex(faq.group(1), r"\bv5\b[^.]*\bv6\b|\bv6\b[^.]*\bv5\b",
                         "the FAQ upgrade answer does not describe the v5-to-v6 path")
        routes = [ln for ln in text.splitlines() if "docs/existing-users.md" in ln]
        self.assertGreaterEqual(len(routes), 3, f"{len(routes)} routes to docs/existing-users.md")
        # The paragraph around each route, not only its line: the claim sits a line above it.
        for para in re.split(r"\n\s*\n", text):
            if "docs/existing-users.md" in para:
                self.assertNotRegex(para, r"(?i)(?<!not )\ba drop-in\b|\bdrop-in replacement\b",
                                    f"a route calls v6 a drop-in: {para[:160]}")

    def test_the_readme_pins_no_hand_count(self) -> None:
        """AC3. MUTANT: '4,000+ unit tests' restored under 'Under the hood'."""
        prose = _without_fences(README.read_text(encoding="utf-8"))
        counts = re.findall(r"(?i)\b\d[\d,]*\+?\s+(?:more\s+)?(?:unit\s+)?"
                            r"(?:tests?|test functions|scripts|helpers)\b", prose)
        self.assertEqual([], counts, "README states a test or script count typed by hand")

    def test_contributing_and_install_are_current(self) -> None:
        """AC4. MUTANTS: README pin `--version v5.1.0`; INSTALL pin `v5.0.1`; INSTALL's
        'Specific version' example at `v1.8.0`; v5.1.0 'the current stable release';
        CONTRIBUTING's `CHANGELOG.md [Unreleased]` paperwork rule."""
        tag = f"v{release()}"
        for rel in FRONT_DOOR:
            text = (REPO / rel).read_text(encoding="utf-8")
            for pinned in re.findall(r"-(?:-v|V)ersion (v\d[\w.-]*\w)", text):
                with self.subTest(doc=rel, pinned=pinned):
                    self.assertEqual(tag, pinned, f"{rel} names a version example other than {tag}")
        for rel in FRONT_DOOR:
            for cmd in _verified_installs((REPO / rel).read_text(encoding="utf-8")):
                with self.subTest(doc=rel, cmd=cmd[-60:]):
                    self.assertRegex(cmd, rf"--version {re.escape(tag)}(?![\w.-])",
                                     f"{rel} pins a verified install to another tag than {tag}")
        for rel in ("README.md", "docs/INSTALL.md"):
            self.assertTrue(_verified_installs((REPO / rel).read_text(encoding="utf-8")),
                            f"{rel} carries no verified-install example to check")
        text = README.read_text(encoding="utf-8")
        listed = re.findall(r"^- \[docs/release-notes-v([^\]]+)\.md\].*$", text, re.M)
        self.assertIn(release(), listed, "README's release-notes list omits the current release")
        for line in re.findall(r"^- \[docs/release-notes-v.*$", text, re.M):
            ver = re.search(r"release-notes-v([^\]]+)\.md", line).group(1)
            calls_current = re.search(r"(?i)\bthe current\b", line)
            with self.subTest(notes=ver):
                self.assertEqual(ver == release(), bool(calls_current),
                                 f"README's list calls the wrong release current: {line[:100]}")
        contributing = (REPO / "CONTRIBUTING.md").read_text(encoding="utf-8")
        rule = re.search(r"^- \*\*Paperwork in the same commit\.\*\*(.*?)(?=^- \*\*|\Z)",
                         contributing, re.M | re.S)
        self.assertIsNotNone(rule, "CONTRIBUTING has no paperwork rule")
        self.assertIn("`changelog.d/<UNIT-ID>.md`", rule.group(1))
        self.assertNotIn("[Unreleased]", rule.group(1))


if __name__ == "__main__":
    unittest.main()
