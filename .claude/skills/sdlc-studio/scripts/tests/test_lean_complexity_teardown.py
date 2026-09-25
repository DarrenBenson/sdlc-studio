"""BG0711: the churn test's temporary git repository cannot fail it on teardown.

`CompositeRiskTests.test_assess_finds_churn_for_absolute_path` builds a real repository with 20
commits. Every `git commit` starts `git maintenance run --auto --detach`, and from git 2.55 (the
CI runner's version) that daemon outlives the commit: it still holds
`.git/objects/maintenance.lock` and reads the repository after the commit returns. On a loaded
runner it was still working in `.git` when the temporary directory was removed, and the run read
`errors=1` with every assertion passed. The fixture now turns automatic maintenance off, and its
teardown ignores a cleanup error, because the test's subject is churn resolution, not removal.

Both criteria run the real test through unittest: AC1 with the removal of `.git` failing as it
did on CI, AC2 with the churn lookup returning nothing, so a fix that silences the test is caught.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/complexity.py
from __future__ import annotations

import errno
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_complexity  # noqa: E402

TARGET = "CompositeRiskTests.test_assess_finds_churn_for_absolute_path"


def _run_target() -> unittest.TestResult:
    suite = unittest.defaultTestLoader.loadTestsFromName(TARGET, test_complexity)
    result = unittest.TestResult()
    suite.run(result)
    return result


class ComplexityTeardownTests(unittest.TestCase):
    def test_a_cleanup_race_does_not_fail_the_churn_test(self) -> None:
        real_rmdir, real_mkdtemp = os.rmdir, tempfile.mkdtemp
        fired: list[str] = []
        made: list[str] = []

        def racing_rmdir(path, *args, **kwargs):
            # the CI failure: removing `.git` finds an entry a git process wrote after the scan
            if os.path.basename(os.fspath(path)) == ".git":
                fired.append(os.fspath(path))
                raise OSError(errno.ENOTEMPTY, "Directory not empty", os.fspath(path))
            return real_rmdir(path, *args, **kwargs)

        def recording_mkdtemp(*args, **kwargs):
            made.append(real_mkdtemp(*args, **kwargs))
            return made[-1]

        try:
            with mock.patch("os.rmdir", racing_rmdir), \
                    mock.patch("tempfile.mkdtemp", recording_mkdtemp):
                result = _run_target()
        finally:
            for d in made:  # the injected failure leaves the tree behind; remove it for real
                shutil.rmtree(d, ignore_errors=True)
        self.assertTrue(fired, "the injected cleanup failure never fired - nothing was tested")
        self.assertEqual((result.testsRun, len(result.skipped)), (1, 0))
        self.assertEqual([tb.splitlines()[-1] for _, tb in result.errors + result.failures], [])

    def test_the_churn_assertion_still_fails_on_a_miss(self) -> None:
        with mock.patch.object(test_complexity.cx, "churn", return_value={"hot.py": 0}):
            result = _run_target()
        self.assertEqual((result.testsRun, len(result.skipped), len(result.errors)), (1, 0, 0))
        self.assertEqual(len(result.failures), 1, "a churn miss must fail the test, not pass it")


if __name__ == "__main__":
    unittest.main()
