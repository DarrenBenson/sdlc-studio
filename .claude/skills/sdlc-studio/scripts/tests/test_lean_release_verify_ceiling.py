"""BG0792: the release verify lane's per-verifier ceiling defaults to CI's 300 s.

The lane read 120 s unless `SDLC_VERIFY_TIMEOUT` said otherwise, while CI's corpus-verify job sets
300. A criterion whose verifier takes 177 s (US0940 AC1's) read green on CI and red in a local
`gate.py --release` on the v6.0.0-rc.1 commit, so the cut runbook carried the override by hand.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

gate = loader.load_script("gate")
verify_ac = loader.load_script("verify_ac")

STORY = ("# US9301: s\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
         "### AC1: it behaves\n\n- **Then** it behaves\n- **Verify:** shell true\n")


class ReleaseVerifyCeilingTests(unittest.TestCase):

    def _ceilings(self, env: dict) -> list:
        """The timeout the verify lane hands each verifier it runs, under `env`."""
        seen = []
        # the module the lane's own `import verify_ac` resolves now: a sibling test may have
        # replaced the entry since this module loaded, and patching a stale one records nothing
        current = sys.modules.get("verify_ac", verify_ac)
        real = current.verify_story

        def recording(*args, **kwargs):
            seen.append(kwargs.get("timeout"))
            return real(*args, **kwargs)

        with tempfile.TemporaryDirectory() as t:
            stories = Path(t) / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US9301-x.md").write_text(STORY, encoding="utf-8")
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch.object(current, "verify_story", recording):
                gate._verify_acs(t)
        return seen

    def test_the_verify_ceiling_defaults_to_ci_s_figure(self) -> None:
        """AC1. MUTANTS: HEAD's 120 s default; a default that ignores the override."""
        base = {k: v for k, v in os.environ.items() if k != gate.VERIFY_TIMEOUT_ENV}
        self.assertEqual([300], self._ceilings(base))
        self.assertEqual([45], self._ceilings({**base, gate.VERIFY_TIMEOUT_ENV: "45"}))


if __name__ == "__main__":
    unittest.main()
