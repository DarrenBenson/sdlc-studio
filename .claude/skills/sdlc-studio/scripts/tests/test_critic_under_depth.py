"""BG1167 (absorbing BG1052): `critic.py record` names an under-depth APPROVE.

A unit approved at the light tier whose own Affects then widened, so its band derives full,
is one conformance no longer counts. Before this, nothing said so when the repair landed or
when the next verdict was recorded: the gap first appeared at the close, after the review cap
was spent. `record` now prints the warning on stderr for whatever verdict it writes on the unit.

Each test builds a git fixture (three small declared modules and four criteria band low; a
fourth module of cognitive 40 added to the Affects, or grown in place, bands medium) and drives
the shipped CLI.

MUTANTS: the notice never printed, or printed only when the verdict being recorded is an
APPROVE; the notice printed for every light APPROVE on a full-band unit, unwidened or not; the
latest live APPROVE read as the first.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repos below
import loader  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"
SMALL = "def f():\n    return 1\n"
HEAVY = "def f():\n" + "    if True:\n        pass\n" * 40
FINDING = "[new] it does not work (src/a.py:1)"


def _write_unit(root: Path, affects: list[str]) -> None:
    criteria = "".join(f"### AC{i}: works\n- **Given** a thing\n- **Verify:** shell echo ok\n"
                       for i in range(1, 5))
    (root / "sdlc-studio" / "stories" / "US0004-sample.md").write_text(
        f"# US0004: sample\n\n> **Status:** Done\n> **Affects:** {', '.join(affects)}\n\n"
        f"## Acceptance Criteria\n\n{criteria}", encoding="utf-8")


def _commit(root: Path, message: str) -> None:
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", message], cwd=root)


class UnderDepthTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = root = Path(tmp.name)
        for name in ("a", "b", "c", "d"):
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / f"{name}.py").write_text(SMALL, encoding="utf-8")
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        _write_unit(root, ["src/a.py", "src/b.py", "src/c.py"])
        gitutil.git(["init", "-q"], cwd=root)
        _commit(root, "US0004 delivered")
        self.critic = loader.load_script("critic")
        self.assertEqual(self.critic.tier_for(root, "US0004"), "light")
        self.critic.record_verdict(root, "US0004", "approve", reviewer="qa", author="dev",
                                   brief="0123456789ab", tier="light")
        _commit(root, "US0004 approved light")

    def _widen(self) -> None:
        (self.root / "src" / "d.py").write_text(HEAVY, encoding="utf-8")
        _write_unit(self.root, ["src/a.py", "src/b.py", "src/c.py", "src/d.py"])
        _commit(self.root, "US0004 repair widens its Affects")
        self.assertEqual(self.critic.tier_for(self.root, "US0004"), "full",
                         "the widening does not raise the band - it proves nothing")

    def _record(self, verdict: str, reviewer: str, *extra: str) -> subprocess.CompletedProcess:
        argv = [sys.executable, str(SCRIPT), "record", "--unit", "US0004", "--verdict", verdict,
                "--reviewer", reviewer, "--author", "dev", "--root", str(self.root), *extra]
        return subprocess.run(argv, capture_output=True, text=True, timeout=120, check=False)

    def test_record_names_an_under_depth_approve(self) -> None:
        """AC4: whatever verdict `record` writes, a REJECT here, its stderr names the light
        APPROVE on file (reviewer, date, brief, tier) and the full tier the band demands."""
        self._widen()
        cp = self._record("reject", "product", "--issues", FINDING)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("US0004's APPROVE by qa on ", cp.stderr)
        self.assertIn("(brief 0123456789ab) was taken at tier light", cp.stderr)
        self.assertIn("now demands the full tier", cp.stderr)

    def test_a_new_light_approve_is_named_as_the_latest(self) -> None:
        """An APPROVE recorded now at light is the one named, not the first on file."""
        self._widen()
        cp = self._record("approve", "qa", "--issues", "none", "--tier", "light",
                          "--brief", "fedcba987654")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("(brief fedcba987654) was taken at tier light", cp.stderr)

    def test_no_notice_without_a_widening_or_after_a_full_approve(self) -> None:
        """The controls: another unit's edit raising the band leaves the light APPROVE counted,
        so `record` stays quiet; and a full APPROVE recorded after a widening answers it."""
        (self.root / "src" / "a.py").write_text(HEAVY, encoding="utf-8")
        _commit(self.root, "US0005 grows src/a.py")
        self.assertEqual(self.critic.tier_for(self.root, "US0004"), "full")
        cp = self._record("reject", "product", "--issues", FINDING)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("APPROVE by", cp.stderr)
        self._widen()
        cp = self._record("approve", "product", "--issues", "none", "--tier", "full")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertNotIn("APPROVE by", cp.stderr)


if __name__ == "__main__":
    unittest.main()
