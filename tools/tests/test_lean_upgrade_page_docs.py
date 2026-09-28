"""US0955: docs/existing-users.md takes an upgrading project from v5 (or older) to v6 on one page.

The retired surface is US0924's one list, `retired_surface` in the skill's tests directory, read
here rather than copied: a verb, flag, key or check id retired later is read without an edit.
The older-project path is checked against what `migrate` itself reports on a v4-era fixture, so
a report item the page does not explain reddens this module rather than surprising a reader.
"""
# test-census-subject: docs/existing-users.md
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_TESTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"
SCRIPTS = SKILL_TESTS.parent
PAGE = REPO / "docs" / "existing-users.md"
#: The real-project rehearsal record (US0962), which AC3's older-project path links.
REHEARSAL = REPO / "docs" / "upgrade-rehearsal-v6.md"

sys.path.insert(0, str(SKILL_TESTS))
import retired_surface  # noqa: E402

#: What the page's older-project path must say for each item `migrate` reports on a v4-era
#: project, keyed by the item's `kind` (or `source` where it carries no kind).
MIGRATE_ITEM_WORDS = {
    "stale-version": "`sdlc-studio/.version`",
    "sizing": "`Size`",
    "team-offer": "`persona generate --team`",
    "index-drift": "reconcile",
    "needs-refine": "refine",
    "conformance-cutoff": "`conformance.adopt_after`",
}


def _sections(text: str) -> list[tuple[str, str]]:
    """(heading, body) for each `## ` section, in order."""
    parts = re.split(r"(?m)^(## .*)$", text)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def _named(pats: dict[str, re.Pattern], text: str) -> list[str]:
    return [label for label, rx in pats.items() if rx.search(text)]


def _commands() -> dict[str, re.Pattern]:
    """The retired verbs, flags, config keys and check ids: the union US0924's test derives,
    without the prose phrases (concepts, which have no command to map)."""
    phrases = set(retired_surface.PHRASES)
    return {k: v for k, v in retired_surface.surfaces().items() if k not in phrases}


_SEPARATOR = re.compile(r"^\|[\s:|-]+\|$")


def _rows(section: str) -> list[list[str]]:
    """The body rows of every table in a section, as cells: a header (the row above a
    separator) and the separator itself are skipped."""
    lines = section.splitlines()
    out = []
    for i, line in enumerate(lines):
        header = i + 1 < len(lines) and _SEPARATOR.match(lines[i + 1].strip())
        if not line.startswith("|") or _SEPARATOR.match(line.strip()) or header:
            continue
        out.append([c.strip() for c in re.split(r"(?<!\\)\|", line.strip()[1:-1])])
    return out


def _env() -> dict:
    """The caller's environment minus every git locating variable, so a hook's GIT_DIR cannot
    steer a fixture at the outer repository."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


class UpgradePageTests(unittest.TestCase):

    def test_the_upgrade_page_maps_every_retired_surface(self) -> None:
        """AC1. MUTANTS: HEAD 63dfbbe8 (a v5 title; `testplan withdraw` and `mutation.py
        register --anchor` taught at 40-50; `review.test_plan_after` as a dormant gate at 68;
        verification-depth tiers as a quality floor at 80); a row whose replacement is empty;
        one surface dropped from the table; a retired key named below the section."""
        text = PAGE.read_text(encoding="utf-8")
        title = text.splitlines()[0]
        self.assertRegex(title, r"^# .*\bv6\b", "the page's title does not say v6")
        self.assertNotRegex(title, r"\bv5\b")

        sections = _sections(text)
        heading, section = sections[0]
        self.assertRegex(heading, r"^## Upgrading to v6\b",
                         "the page does not open with its 'Upgrading to v6' section")
        steps = re.search(r"```bash\n(.*?)```", section, re.S)
        self.assertTrue(steps, "the section holds no upgrade-steps block")
        lines = [ln.strip() for ln in steps.group(1).splitlines()]
        self.assertIn("migrate.py", lines, "no dry run of `migrate` in the steps")
        self.assertIn("migrate.py --apply", lines)
        self.assertLess(lines.index("migrate.py"), lines.index("migrate.py --apply"),
                        "the steps apply before the dry run")

        pats = _commands()
        for label in retired_surface.migrate._retired_verbs():
            self.assertIn(label, pats, "a registry verb is missing from the imported union")
        removed = set(retired_surface.sdlc_md.RETIRED_CONFIG_KEYS) | set(
            retired_surface.sdlc_md.RETIRED_CHECK_IDS)
        rows = _rows(section)
        for label, rx in pats.items():
            with self.subTest(surface=label):
                mapped = [row for row in rows if rx.search(row[0])]
                self.assertTrue(mapped, f"the section maps no replacement for {label}")
                for row in mapped:
                    self.assertTrue(row[-1] and row[-1] not in ("-", "None"),
                                    f"the row naming {label} gives no replacement: {row}")
                # A key or tag is what `migrate --apply` removes; one row naming it must say so
                # (`plan_review.py` also matches the `plan_review` key, in a row about the verb).
                if label in removed:
                    self.assertTrue(any("`migrate --apply`" in row[-1] for row in mapped),
                                    f"no row naming {label} says `migrate --apply` removes it")

        outside = "\n".join(f"{h}\n{b}" for h, b in sections[1:])
        self.assertEqual([], _named(pats, outside),
                         "a retired surface is named outside the 'Upgrading to v6' section")
        phrases = {k: v for k, v in retired_surface.surfaces().items()
                   if k in retired_surface.PHRASES}
        self.assertEqual([], retired_surface.live_mentions(outside, phrases),
                         "a retired concept is taught outside the 'Upgrading to v6' section")
        self.assertNotRegex(outside, r"(?i)verification[- ]depth",
                            "the tier vocabulary is advice no gate reads; this page teaches "
                            "upgraders and has no floor to describe with it")

    def test_the_upgrade_page_covers_an_older_project(self) -> None:
        """AC3. MUTANTS: a page with no older-project section (every reader assumed on 5.1); a
        section that drops what `migrate` reports for one item; one that never says schema 2 is
        kept; one that does not link the rehearsal record."""
        sections = dict(_sections(PAGE.read_text(encoding="utf-8")))
        older = next((b for h, b in sections.items()
                      if re.search(r"(?i)\bv4 or (?:earlier|older)\b", h)), None)
        self.assertIsNotNone(older, "the page gives no path for a project on v4 or earlier")
        self.assertIn("`schema_version: 2`", older,
                      "the older-project path does not say what happens to schema 2")
        self.assertRegex(older, r"`migrate(?:\.py)? --apply`")
        self.assertTrue(REHEARSAL.is_file(), "the rehearsal record the page links is missing")
        self.assertIn("](upgrade-rehearsal-v6.md)", older,
                      "the older-project path does not link the rehearsal record")

        with tempfile.TemporaryDirectory() as d:
            report = _migrate_v4_fixture(Path(d))
        items = report["deterministic"] + report["needs_human"]
        kinds = {item.get("kind") or item["source"] for item in items}
        self.assertIn("conformance-cutoff", kinds, "the fixture exercised no v4-era history")
        for kind in sorted(kinds):
            with self.subTest(kind=kind):
                self.assertIn(kind, MIGRATE_ITEM_WORDS,
                              f"migrate reports `{kind}` on a v4-era project and this test does "
                              f"not know what the page must say about it")
                self.assertIn(MIGRATE_ITEM_WORDS[kind], older,
                              f"migrate reports `{kind}` on a v4-era project and the page's "
                              f"older-project path does not mention it")


def _migrate_v4_fixture(root: Path) -> dict:
    """A workspace aged back to v4.1 (schema 2, `.version` 4.1.0, a Done story with no evidence,
    a request sized in Effort), and `migrate`'s dry-run report on it."""
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "init.py"), "--root", str(root), "run"],
                       capture_output=True, text=True, timeout=300, check=False, env=_env())
    assert r.returncode == 0, r.stderr
    ws = root / "sdlc-studio"
    cfg = ws / ".config.yaml"
    cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2"),
                   encoding="utf-8")
    (ws / ".version").write_text("schema_version: 2\nupgraded_from: null\n"
                                 "upgraded_at: 2025-01-01\nskill_version: \"4.1.0\"\n",
                                 encoding="utf-8")
    (ws / "stories" / "US0001-legacy.md").write_text(
        "# US0001: legacy login\n\n> **Status:** Done\n> **Epic:** EP0001\n> **Priority:** High\n\n"
        "## Acceptance Criteria\n\n- [x] **AC1** it logs in\n", encoding="utf-8")
    (ws / "change-requests" / "CR0001-legacy.md").write_text(
        "# CR-0001: legacy\n\n> **Status:** Approved\n> **Priority:** Medium\n> **Effort:** M\n\n"
        "## Summary\n\nAdd SSO.\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "migrate.py"), "--root", str(root),
                        "--format", "json"],
                       capture_output=True, text=True, timeout=300, check=False, env=_env())
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


if __name__ == "__main__":
    unittest.main()
