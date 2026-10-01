"""BG0876: the dev lockfile resolves patched brace-expansion and markdown-it.

`npm audit` reported brace-expansion 4.0.0-5.0.11 (high: GHSA-q2hr-2g5m-vwhr,
GHSA-qhr7-859c-m2p7, GHSA-6j4f-fj2g-mc7p) and markdown-it below 14.3.1 (moderate:
GHSA-253c-mchw-3w2r), both reached through markdownlint-cli. package.json holds each at a patched
release with an npm `overrides` entry, as BG0866 holds js-yaml, and this test pins every lockfile
entry and both overrides. The compare is numeric on (major, minor, patch), never a string match.
"""
from __future__ import annotations

# test-census-subject: package-lock.json
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOCK = REPO / "package-lock.json"
PACKAGE = REPO / "package.json"
#: brace-expansion's vulnerable range, inclusive.
BRACE_VULNERABLE = ((4, 0, 0), (5, 0, 11))
#: markdown-it's first patched release.
MARKDOWN_IT_PATCHED = (14, 3, 1)


def semver(raw: str) -> tuple[int, int, int]:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", raw or "")
    if not m:
        raise ValueError(f"no semver in {raw!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _entries(name: str) -> dict[str, tuple[int, int, int]]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    return {path: semver(meta.get("version", ""))
            for path, meta in (lock.get("packages") or {}).items()
            if path == f"node_modules/{name}" or path.endswith(f"/node_modules/{name}")}


class DevAdvisoriesPatchedTests(unittest.TestCase):
    def test_the_lockfile_resolves_patched_brace_expansion_and_markdown_it(self) -> None:
        """AC1. MUTANT: the lockfile at 9f992b78 (brace-expansion 5.0.9, markdown-it 14.3.0).
        MUTANT: drop either override - the next install resolves the vulnerable range again.
        MUTANT: an override whose floor admits a vulnerable release (`^5.0.0`, `^14.3.0`)."""
        braces = _entries("brace-expansion")
        self.assertTrue(braces, "brace-expansion is not in package-lock.json")
        low, high = BRACE_VULNERABLE
        for path, version in braces.items():
            self.assertFalse(low <= version <= high,
                             f"{path} resolves brace-expansion {version}, inside 4.0.0-5.0.11")
        markdown_it = _entries("markdown-it")
        self.assertTrue(markdown_it, "markdown-it is not in package-lock.json")
        for path, version in markdown_it.items():
            self.assertGreaterEqual(version, MARKDOWN_IT_PATCHED,
                                    f"{path} resolves markdown-it {version}, below 14.3.1")

        overrides = json.loads(PACKAGE.read_text(encoding="utf-8")).get("overrides") or {}
        brace = overrides.get("brace-expansion")
        self.assertIsNotNone(brace, "package.json carries no brace-expansion override")
        self.assertGreater(semver(brace), high, f"the override {brace!r} admits a vulnerable release")
        md = overrides.get("markdown-it")
        self.assertIsNotNone(md, "package.json carries no markdown-it override")
        self.assertGreaterEqual(semver(md), MARKDOWN_IT_PATCHED,
                                f"the override {md!r} admits a vulnerable release")
        self.assertIn("js-yaml", overrides, "BG0866's js-yaml override was lost")


if __name__ == "__main__":
    unittest.main()
