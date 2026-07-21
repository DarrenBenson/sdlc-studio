"""The suite lanes run in a git environment of their own, not the caller's (BG0222).

`git commit -a` hands the pre-commit hook GIT_INDEX_FILE (and, depending on how git was
invoked, GIT_DIR / GIT_WORK_TREE / GIT_PREFIX). The suite lanes inherit them, and every test
that builds a throwaway repo in a temp directory and shells out to git then acts on the OUTER
repo instead. The same commit passes when staged and fails under `-a`, so it reads as flaky
tests rather than an environment leak.

These tests pin the scrub itself, behaviourally: the script is run with a polluted environment
and asked what its child actually sees. A structural grep for `unset` would pass on an `unset`
that never executes.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "skill-tests.sh"

# The variables that can point git at a different repository, index, object store or path
# prefix. Keep in step with the scrub in tools/skill-tests.sh: this list is the assertion, so
# a variable dropped from the script fails here rather than going quiet.
REPO_LOCATING = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)

# Set by the fixtures for their own hermeticity, or harmless identity. Scrubbing these would
# weaken the fixtures rather than protect them, so the script must leave them ALONE - the
# scrub has an upper bound as well as a lower one.
MUST_SURVIVE = ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME",
                "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")


def _scrub_prelude() -> str:
    """The scrub as the script actually declares it, up to the first non-scrub statement.

    Extracted from the file rather than duplicated here: a copy would drift, and a drifted
    copy would test itself rather than the shipped script."""
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.index("unset -v GIT_DIR")
    tail = text[start:]
    end = tail.index("\n\n")
    return tail[:end]


class ScrubClearsTheCallersGitEnvironment(unittest.TestCase):
    def _child_env_after_scrub(self, polluted: dict) -> dict:
        """What a child of the scrub prelude sees, given a polluted parent environment."""
        env = {**os.environ, **polluted}
        # `/usr/bin/env` by absolute path, not a bare `env`: on some PATHs the bare name
        # resolves to a wrapper that reports a sanitised environment, which would make this
        # test pass by reading the wrong thing rather than by the scrub working.
        proc = subprocess.run(
            ["bash", "-c", f"{_scrub_prelude()}\nexec /usr/bin/env"],
            capture_output=True, text=True, env=env, cwd=REPO, check=True)
        out = {}
        for line in proc.stdout.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k] = v
        return out

    def test_every_repo_locating_variable_is_cleared_for_the_child(self) -> None:
        polluted = {name: "/definitely/not/this/repo" for name in REPO_LOCATING}
        seen = self._child_env_after_scrub(polluted)
        still_set = [n for n in REPO_LOCATING if n in seen]
        self.assertEqual(still_set, [],
                         f"the scrub left {still_set} pointing at the caller's repository")

    def test_the_scrub_leaves_the_fixtures_own_variables_alone(self) -> None:
        polluted = {name: "fixture-value" for name in MUST_SURVIVE}
        seen = self._child_env_after_scrub(polluted)
        lost = [n for n in MUST_SURVIVE if seen.get(n) != "fixture-value"]
        self.assertEqual(lost, [],
                         f"the scrub cleared {lost}, which the fixtures rely on")

    def test_a_polluted_index_no_longer_reaches_a_git_call_after_the_scrub(self) -> None:
        """The end-to-end property, in a throwaway repo the test owns.

        Without the scrub, `git add` under a polluted GIT_INDEX_FILE writes the OUTER index.
        This builds its own repo, points GIT_INDEX_FILE at a decoy, and asserts the decoy is
        untouched once the scrub has run - which is the actual harm, not a variable's absence.
        """
        with tempfile.TemporaryDirectory() as d:
            work, decoy = Path(d) / "work", Path(d) / "decoy-index"
            work.mkdir()
            clean = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            subprocess.run(["git", "init", "-q"], cwd=work, check=True, env=clean)
            (work / "a.txt").write_text("x", encoding="utf-8")
            decoy.write_bytes(b"")
            script = f"{_scrub_prelude()}\ncd {work}\ngit add a.txt\n"
            subprocess.run(["bash", "-c", script], check=True, capture_output=True,
                           env={**os.environ, "GIT_INDEX_FILE": str(decoy)})
            self.assertEqual(decoy.read_bytes(), b"",
                             "the scrub let git write the caller's index")
            listed = subprocess.run(["git", "ls-files"], cwd=work, capture_output=True,
                                    text=True, check=True,
                                    env=clean)
            self.assertIn("a.txt", listed.stdout,
                          "the add did not land in the fixture's own index either")


class ScrubListsAgreeTests(unittest.TestCase):
    """The scrub list now exists in THREE places and nothing kept them equal.

    `skill-tests.sh` has always had it; RUN-01KY1WCR added a copy to the hook's tool-tests lane
    (which git also hands a polluted environment, and which invokes `unittest` directly rather
    than through the script) and a third to the fixture module that builds git repos. The
    adversarial review pointed out that dropping three variables from the hook's copy alone left
    all 254 tool tests green - so the newest copy, guarding the lane that actually caused the
    finding, was pinned by nothing.

    This module's own docstring is the argument: a copy drifts, and a drifted copy tests itself
    rather than the shipped script. So assert the three agree, by parsing each one from source.
    """

    HOOK = REPO / ".githooks" / "pre-commit"
    MODULE = REPO / "tools" / "tests" / "test_precommit_budget_recording.py"

    def _hook_scrub_list(self) -> tuple[str, ...]:
        """The `-u VAR` flags on the hook's tool-tests lane."""
        import re
        text = self.HOOK.read_text(encoding="utf-8")
        m = re.search(r"/usr/bin/env((?:\s*\\?\s*-u\s+\w+)+)", text)
        self.assertIsNotNone(m, "no `/usr/bin/env -u ...` scrub found on a hook lane")
        return tuple(re.findall(r"-u\s+(\w+)", m.group(1)))

    def _module_scrub_list(self) -> tuple[str, ...]:
        import ast
        tree = ast.parse(self.MODULE.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and any(getattr(t, "id", None) == "_GIT_ENV_VARS" for t in node.targets)):
                return tuple(el.value for el in node.value.elts)
        self.fail("no _GIT_ENV_VARS in the fixture module")

    def test_the_hook_lane_scrubs_the_same_variables_as_the_script(self) -> None:
        self.assertEqual(sorted(self._hook_scrub_list()), sorted(REPO_LOCATING))

    def test_the_fixture_module_scrubs_the_same_variables(self) -> None:
        self.assertEqual(sorted(self._module_scrub_list()), sorted(REPO_LOCATING))

    def test_the_script_itself_still_scrubs_them(self) -> None:
        """Closes the loop: without this, all three copies could drift together away from the
        list this file asserts, and the two tests above would still agree with each other."""
        prelude = _scrub_prelude()
        for var in REPO_LOCATING:
            self.assertIn(var, prelude, f"{var} dropped from tools/skill-tests.sh")


if __name__ == "__main__":
    unittest.main()
