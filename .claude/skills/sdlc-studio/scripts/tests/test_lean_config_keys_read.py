"""BG0831: the configuration reference documents only keys the code honours.

Three drifts. `reference-config.md` documented `sprint.split_above`, but the split threshold is
read from `sprint.points_split_above`, so the documented key changed nothing. `review.policy:
carry-forward` was documented as filing a REJECT's findings and shipping, but nothing outside
tests called the carry-forward module since the lean loop began carrying every unit at the round
cap; the key is retired (migrate strips it) and the module deleted. And the defaults' comment on
`review.max_rounds` said two consumers read it, when only critic.py's round cap does.

Driven through the shipped CLIs (`sprint.py plan`, `migrate.py --apply`) in throwaway trees.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-config.md
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover - config is read through PyYAML
    HAVE_YAML = False


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True,
                          text=True, timeout=300, check=False, env=_env())


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _pointed_bug(root: Path, points: int) -> None:
    _w(root, "src/widget.py", "x = 1\n")
    _w(root, "sdlc-studio/bugs/BG0001-x.md",
       "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n> **Affects:** src/widget.py\n"
       f"> **Points:** {points}\n\n## Acceptance Criteria\n\n### AC1: it behaves\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")


def _rows(text: str) -> list[str]:
    """The setting names a reference table documents: the first cell of each table row."""
    return re.findall(r"^\|\s*`([a-z_]+(?:\.[a-z_]+)+)`\s*\|", text, re.M)


class ConfigKeysReadTests(unittest.TestCase):
    """AC1-AC3."""

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_documented_split_key_is_the_one_read(self) -> None:
        """AC1. MUTANTS: (1) document `sprint.split_above` again - the row is found; (2) drop the
        `sprint.points_split_above` row - the documented key is missing; (3) read a key other than
        the one documented in `points_split_above()` - the unit over 5 plans.

        The unit is an 8, not the criterion's 6: `6` is off the modified Fibonacci scale, so it is
        refused as unsized ("lacks Points") whatever the threshold, and a 6 cannot tell a ceiling
        of 5 from the default 8 (mutant 3 survived it). An 8 is on the scale, legal by default
        and over a ceiling of 5, so only the configured threshold refuses it; a 5 is the control."""
        def plan(points: int) -> subprocess.CompletedProcess:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _w(root, "sdlc-studio/.config.yaml", "sprint:\n  points_split_above: 5\n")
                _pointed_bug(root, points)
                return _cli("sprint.py", "plan", "--bugs", "Open", "--root", str(root),
                            "--no-fetch", "--skip-personas")
        r = plan(8)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, "an 8-point unit planned under a ceiling of 5:\n" + out)
        self.assertIn("BG0001", r.stderr, out)
        self.assertNotIn("lacks Points", r.stderr, "refused as unsized, not as over the threshold")
        self.assertIn("5", r.stderr, "the refusal does not name the configured ceiling")
        self.assertNotIn("batch:", r.stdout, "a plan was printed for a refused batch")
        control = plan(5)
        self.assertEqual(0, control.returncode, "a unit at the ceiling was refused:\n"
                         + control.stdout + control.stderr)
        rows = _rows((SKILL / "reference-config.md").read_text(encoding="utf-8"))
        self.assertIn("sprint.points_split_above", rows,
                      "reference-config.md does not document the key the code reads")
        self.assertNotIn("sprint.split_above", rows,
                         "reference-config.md documents `sprint.split_above`, which nothing reads")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_review_policy_is_retired_not_documented(self) -> None:
        """AC2. MUTANTS: (1) leave `review.policy` out of `RETIRED_CONFIG_KEYS` - migrate keeps
        the line; (2) keep shipping `carry_forward.py`; (3) keep the `review.policy` row in
        reference-config.md, the `carry_forward.py` entry naming it in reference-scripts-review.md,
        or `policy:` under `review:` in config-defaults.yaml."""
        self.assertIn("review.policy", sdlc_md.RETIRED_CONFIG_KEYS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = _w(root, "sdlc-studio/.config.yaml",
                     "review:\n  policy: carry-forward\n  blocking_priority: high\n")
            r = _cli("migrate.py", "--apply", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            after = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            self.assertNotIn("policy", after.get("review") or {},
                             "migrate kept the retired review.policy key")
            self.assertEqual("high", after["review"]["blocking_priority"],
                             "migrate removed a key that is not retired")
            self.assertIn("review.policy", r.stdout, "the removal is not reported")
        self.assertFalse((SCRIPTS / "carry_forward.py").exists(), "carry_forward.py still ships")
        docs = [*SKILL.glob("reference-*.md"), *(SKILL / "help").rglob("*.md")]
        self.assertGreater(len(docs), 40, "premise: the reference and help pages were found")
        for path in docs:
            with self.subTest(doc=str(path.relative_to(SKILL))):
                self.assertNotIn("review.policy", path.read_text(encoding="utf-8"))
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertNotIn("policy", defaults.get("review") or {},
                         "config-defaults.yaml still declares review.policy")

    def test_max_rounds_comment_names_one_reader(self) -> None:
        """AC3. MUTANTS: (1) keep the two-consumer comment; (2) a comment that names no reader."""
        text = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        lines = text.splitlines()
        at = next((i for i, ln in enumerate(lines) if "review.max_rounds" in ln), None)
        self.assertIsNotNone(at, "config-defaults.yaml says nothing about review.max_rounds")
        start = at
        while start > 0 and lines[start - 1].lstrip().startswith("#"):
            start -= 1
        end = at
        while end + 1 < len(lines) and lines[end + 1].lstrip().startswith("#"):
            end += 1
        comment = " ".join(ln.strip().lstrip("#").strip() for ln in lines[start:end + 1])
        self.assertIn("critic.py", comment, "the comment does not name critic.py as the reader")
        self.assertRegex(comment, r"\bonly reader\b",
                         "the comment does not say critic.py is the only reader")
        for stale in ("two consumers", "close-attempt"):
            self.assertNotIn(stale, comment, f"the comment still says {stale!r}:\n{comment}")


if __name__ == "__main__":
    unittest.main()
