"""US0952 AC2: `project upgrade` prints the breaking changes first, every one of them.

The digest printed its kinds in Keep-a-Changelog order with Breaking absent from that order, so
the Breaking group came after up to 18 capped Added, Changed and Fixed entries, and a long
Breaking group was cut at the same cap as the rest. A 5.1 project upgrading to 6.0.0 must read
the retirements that will refuse its scripts before anything else.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

pu = loader.load_script("project_upgrade")


def _section(version: str, **kinds: int) -> str:
    out = [f"## [{version}] - 2026-09-26", ""]
    for kind, n in kinds.items():
        out += [f"### {kind}", ""] + [f"- {version} {kind.lower()} {i}" for i in range(1, n + 1)]
        out.append("")
    return "\n".join(out)


def _changelog(d: str, rc_breaking: int = 4) -> Path:
    path = Path(d) / "CHANGELOG.md"
    path.write_text("# Changelog\n\n## [Unreleased]\n\n"
                    + _section("6.0.0", Breaking=1, Added=7, Changed=7, Fixed=7)
                    + _section("6.0.0-rc.1", Breaking=rc_breaking)
                    + _section("5.1.0", Added=2), encoding="utf-8")
    return path


class UpgradeDigestTests(unittest.TestCase):

    def test_breaking_leads_the_digest_uncapped(self) -> None:
        """MUTANTS: `Breaking` dropped from `_KIND_ORDER` (it prints last, after the capped
        groups); Breaking held to `_GROUP_CAP` like every other kind; `_gt` read as `>=` for
        the recorded bound, so a project on rc.1 is shown rc.1's entries again."""
        with tempfile.TemporaryDirectory() as d:
            dig = pu.changelog_digest("5.1.0", "6.0.0", _changelog(d))
            self.assertTrue(dig["available"], dig)
            lines = pu._render_digest(dig)
            self.assertEqual("  Breaking:", lines[0], f"the digest opens with {lines[0]!r}")
            breaking = lines[1:6]
            self.assertEqual(
                ["    - 6.0.0 breaking 1"] + [f"    - 6.0.0-rc.1 breaking {i}" for i in range(1, 5)],
                breaking)
            self.assertFalse(lines[6].startswith("    "), f"a sixth Breaking line: {lines[6]!r}")

            on_rc = pu.changelog_digest("6.0.0-rc.1", "6.0.0", _changelog(d))
            self.assertEqual(["6.0.0"], on_rc["versions"])
            self.assertEqual(["6.0.0 breaking 1"], on_rc["groups"]["Breaking"])
            self.assertNotIn("6.0.0-rc.1", "\n".join(pu._render_digest(on_rc)),
                             "a project already on rc.1 is shown rc.1's entries again")

        # Uncapped: more Breaking entries than any other group may print, all shown.
        with tempfile.TemporaryDirectory() as d:
            many = pu._GROUP_CAP + 3
            dig = pu.changelog_digest("5.1.0", "6.0.0", _changelog(d, rc_breaking=many))
            self.assertEqual(many + 1, len(dig["groups"]["Breaking"]))
            self.assertNotIn("Breaking", dig["extra"])
            rendered = "\n".join(pu._render_digest(dig))
            self.assertIn(f"6.0.0-rc.1 breaking {many}", rendered)
            self.assertIn("(+1 more - see CHANGELOG.md)", rendered, "the other groups stay capped")


if __name__ == "__main__":
    unittest.main()
