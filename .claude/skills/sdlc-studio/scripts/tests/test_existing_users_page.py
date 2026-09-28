"""The upgrade page is checked by EXECUTING what it says, not by grepping it (BG0560).

README routes every existing user to `docs/existing-users.md`, which was the v4 page while v5
changed what an upgraded project is held to. The plan review's sharpest finding was that "run the
page's own upgrade steps" is mechanised nowhere, so a test hardcoding the sequence still passes
after the page is reverted: it measures the fixture, not the document. The steps are therefore
PARSED OUT of the page and run - a page that stops saying something stops having it checked.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_existing_users_page.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# parents[5], not [4]: [4] is `.claude`. That off-by-one made the doc-surface lane's own tests
# assert against an error message rather than the lane (BG0559).
REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402 - the module under test here: the page's table is checked against
               # the values config.py resolves, so this file belongs to config.py
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PAGE = REPO / "docs" / "existing-users.md"
README = REPO / "README.md"
UPGRADE_REF = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-upgrade.md"

#: The one step in the page's block a reader does by hand, marked there by a comment naming the key:
#: add the `conformance.adopt_after` line `migrate` named. The test does what the comment says, so
#: a page that drops the step leaves the gate step red.
_HAND_STEP = "conformance.adopt_after"
_NAMED_CUTOFF = re.compile(r"`conformance\.adopt_after: ([A-Za-z]+-?[0-9]+)`")

#: The defaults that decide what an EXISTING project is held to on upgrade, and what the page must
#: say about each. Derived here in one place so the page's table and the resolved values cannot
#: drift into disagreeing without a test noticing.
GATE_TABLE = {
    "sprint.breakdown": "enforce",
    "conformance.adopt_after": None,
}


def _steps_from_page() -> list[str]:
    """The lines of the page's upgrade-steps block, parsed from the page itself: each command,
    and each comment, which names a step the reader does by hand."""
    text = PAGE.read_text(encoding="utf-8")
    section = text.split("## Upgrade steps", 1)
    if len(section) < 2:
        return []
    block = re.search(r"```bash\n(.*?)```", section[1], re.S)
    if not block:
        return []
    return [ln.strip() for ln in block.group(1).splitlines() if ln.strip()]


class PageStepsAreExecutedTests(unittest.TestCase):
    """BG0560 AC1."""

    def _v4_fixture(self, d) -> Path:
        root = Path(d)
        r = subprocess.run([sys.executable, str(SCRIPTS / "init.py"), "--root", str(root), "run"],
                           capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(0, r.returncode, r.stderr)
        cfg = root / "sdlc-studio" / ".config.yaml"
        cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3",
                                                               "schema_version: 2"),
                       encoding="utf-8")
        (root / "sdlc-studio" / ".version").write_text(
            'schema_version: 2\nupgraded_from: null\nupgraded_at: 2025-01-01\n'
            'skill_version: "4.1.0"\n', encoding="utf-8")
        (root / "sdlc-studio" / "stories" / "US0001-legacy.md").write_text(
            "# US0001: legacy login\n\n> **Status:** Done\n> **Epic:** EP0001\n"
            "> **Priority:** High\n\n## Acceptance Criteria\n\n- [x] **AC1** it logs in\n",
            encoding="utf-8")
        (root / "sdlc-studio" / "change-requests" / "CR0001-legacy.md").write_text(
            "# CR-0001: legacy\n\n> **Status:** Approved\n> **Priority:** Medium\n"
            "> **Effort:** M\n\n## Summary\n\nAdd SSO.\n", encoding="utf-8")
        return root

    def test_the_pages_own_steps_are_parsed_and_executed(self) -> None:
        steps = _steps_from_page()
        self.assertTrue(steps, "the page's upgrade-steps block yields no commands, so nothing "
                               "about the upgrade path is being checked at all")
        # Every step must be FOUND IN THE PAGE. Without this a parser replaced by a hardcoded
        # list passes on a page that no longer says anything - which is the whole finding the
        # plan review raised, and mutation confirmed the weaker form could not see it.
        page_text = PAGE.read_text(encoding="utf-8")
        for step in steps:
            self.assertIn(step, page_text,
                          f"the executed step `{step}` does not appear in the page, so the "
                          f"sequence is hardcoded rather than read from the document")
        self.assertTrue(any(s.startswith("#") and _HAND_STEP in s for s in steps),
                        "the block does not tell the reader to add the cutoff migrate names")
        with tempfile.TemporaryDirectory() as d:
            root = self._v4_fixture(d)
            named = ""
            for step in steps:
                if step.startswith("#"):
                    if _HAND_STEP in step:
                        # The reader's hand step: the line the last `migrate` report named.
                        cutoff = _NAMED_CUTOFF.search(named)
                        self.assertTrue(cutoff, f"migrate named no cutoff line:\n{named}")
                        with (root / "sdlc-studio" / ".config.yaml").open(
                                "a", encoding="utf-8") as cfg:
                            cfg.write(f"\nconformance:\n  adopt_after: {cutoff.group(1)}\n")
                    continue
                script, *args = step.split()
                path = SCRIPTS / script
                self.assertTrue(path.exists(),
                                f"the page tells a reader to run `{step}`, and {script} does not "
                                f"exist - the page names a command nobody can type")
                r = subprocess.run([sys.executable, str(path), "--root", str(root), *args],
                                   capture_output=True, text=True, timeout=900, check=False)
                self.assertNotIn("Traceback", r.stderr,
                                 f"the page's step `{step}` crashed:\n{r.stderr[-800:]}")
                # Every step, the gate included, passes once the page's steps are followed.
                self.assertEqual(0, r.returncode,
                                 f"the page's step `{step}` failed:\n{r.stdout}{r.stderr}")
                if script == "migrate.py":
                    named = r.stdout


class PageClaimsTests(unittest.TestCase):
    """BG0560 AC2, AC3, AC4."""

    def test_every_readme_route_points_at_the_v5_page_and_claims_no_drop_in(self) -> None:
        # The name stays because a stamped Verify line (BG0560 AC2) selects it; the page it
        # checks is now the v6 one.
        # All THREE routes. The previous plan covered one, and a test checking only the
        # best-known route cannot notice the drop-in wording returning on another.
        text = README.read_text(encoding="utf-8")
        routes = [ln for ln in text.splitlines() if "docs/existing-users.md" in ln]
        self.assertGreaterEqual(len(routes), 3,
                                f"expected at least 3 routes to the upgrade page, found "
                                f"{len(routes)} - the test would silently stop covering one")
        for ln in routes:
            self.assertNotRegex(
                ln, r"(?i)\bit is a drop-in\b|\bdrop-in:\s*no project migration",
                f"a README route still calls v5 a drop-in requiring no migration: {ln[:120]}")
        self.assertTrue(PAGE.read_text(encoding="utf-8").startswith(
            "# SDLC Studio v6 for existing projects"),
            "the page every route points at does not say v6 in its own title")

    def test_the_pages_gate_table_agrees_with_the_resolved_defaults(self) -> None:
        text = PAGE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            for key, expected in GATE_TABLE.items():
                with self.subTest(key=key):
                    self.assertIn(f"`{key}`", text,
                                  f"the page's table does not mention {key}, so a reader is not "
                                  f"told about a default that decides what they are held to")
                    actual = config.get(root, key, None)
                    self.assertEqual(expected, actual,
                                     f"{key} resolves to {actual!r}, not the {expected!r} this "
                                     f"page's table describes - the page would reassure a reader "
                                     f"who is about to be refused")
                    # The page's STATED default, read out of its own row and compared with the
                    # resolved one. Asserting only that the key is mentioned let the row claim
                    # the opposite value and still pass; mutation found it.
                    row = next((ln for ln in text.splitlines()
                                if ln.startswith(f"| `{key}`")), "")
                    stated = re.search(r"\(default `?([A-Za-z_]+)`?\)", row)
                    if stated:
                        self.assertEqual(str(expected).lower() if expected is not None else "unset",
                                         stated.group(1).lower(),
                                         f"the page's row for {key} states a default of "
                                         f"{stated.group(1)!r}, but it resolves to {actual!r}")
        # The gate that FIRES must be described as firing.
        self.assertRegex(text, r"`sprint\.breakdown`[^|]*\|[^|]*refuses",
                         "the page does not say sprint.breakdown REFUSES on an upgraded project")

    def test_the_upgrade_reference_hands_off_the_v5_gate_delta(self) -> None:
        text = UPGRADE_REF.read_text(encoding="utf-8")
        self.assertIn("existing-users.md", text,
                      "reference-upgrade.md is the document a migration reads first and it does "
                      "not hand the reader to the page describing what v5 will refuse them")
        self.assertIn("sprint.breakdown", text)
        self.assertIn("conformance.adopt_after", text)


if __name__ == "__main__":
    unittest.main()
