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


#: Every place in the repo that writes out a git repo-locating scrub list, and what stops that
#: copy drifting. The sweep below fails on a code file naming several of these variables that
#: is NOT registered here, which is the structural answer to L-0177: a protection built for one
#: suite does not cover the suite beside it, and the copy nobody pinned is the one that drifts.
#: An entry beginning `PARTIAL` is declared debt, not a clean bill of health.
SCRUB_SITES: dict[str, str] = {
    "tools/skill-tests.sh":
        "pinned by test_the_script_itself_still_scrubs_them",
    ".githooks/pre-commit":
        "pinned by test_the_hook_lane_scrubs_the_same_variables_as_the_script",
    "tools/tests/test_precommit_budget_recording.py":
        "pinned by test_the_hook_fixture_module_scrubs_the_same_variables",
    "tools/tests/test_precommit_window_guard.py":
        "pinned by test_every_hook_fixture_module_scrubs_the_same_variables",
    "tools/tests/test_precommit_floor_pending.py":
        "pinned by test_every_hook_fixture_module_scrubs_the_same_variables",
    "tools/tests/test_skill_tests_env.py":
        "this file: REPO_LOCATING is the list every other copy is held to",
    ".claude/skills/sdlc-studio/scripts/tests/test_gitutil.py":
        "asserts the shipped helper's confinement behaviourally, against throwaway repos",
    ".claude/skills/sdlc-studio/scripts/tests/gitutil.py":
        "pinned by test_the_shipped_fixture_helper_scrubs_the_same_variables",
    ".claude/skills/sdlc-studio/scripts/gate.py":
        "PARTIAL: clears only GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE before a read-only "
        "`rev-parse`. It reads rather than writes, so an escape misreports rather than "
        "damages, and it is out of BG0230's scope. Widen it to REPO_LOCATING when touched.",
    ".claude/skills/sdlc-studio/scripts/lessons.py":
        "PARTIAL: same three variables, same read-only `git -C` shape, same debt as gate.py.",
}


class ScrubListsAgreeTests(unittest.TestCase):
    """The scrub list exists in several places and nothing kept them equal.

    `skill-tests.sh` has always had it; RUN-01KY1WCR added a copy to the hook's tool-tests lane
    (which git also hands a polluted environment, and which invokes `unittest` directly rather
    than through the script) and a third to the fixture module that builds git repos. BG0230
    added a fourth, in the shipped fixture helper the skill suites build their git repos with.
    The adversarial review pointed out that dropping three variables from the hook's copy alone
    left all 254 tool tests green - so the newest copy, guarding the lane that actually caused
    the finding, was pinned by nothing.

    This module's own docstring is the argument: a copy drifts, and a drifted copy tests itself
    rather than the shipped script. So assert they all agree, by parsing each one from source.
    """

    HOOK = REPO / ".githooks" / "pre-commit"
    MODULE = REPO / "tools" / "tests" / "test_precommit_budget_recording.py"
    GITUTIL = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests" / "gitutil.py"

    def _hook_scrub_list(self) -> tuple[str, ...]:
        """The `-u VAR` flags on the hook's tool-tests lane."""
        import re
        text = self.HOOK.read_text(encoding="utf-8")
        m = re.search(r"/usr/bin/env((?:\s*\\?\s*-u\s+\w+)+)", text)
        self.assertIsNotNone(m, "no `/usr/bin/env -u ...` scrub found on a hook lane")
        return tuple(re.findall(r"-u\s+(\w+)", m.group(1)))

    def _named_tuple_in(self, path: Path, name: str) -> tuple[str, ...]:
        """The string tuple assigned to `name` in `path`, read from source rather than imported.

        Parsed, not imported: the shipped helper reads `os.environ` and the repo module builds
        git fixtures, and neither should run merely to have its declaration inspected.
        """
        import ast
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and any(getattr(t, "id", None) == name for t in node.targets)):
                return tuple(el.value for el in node.value.elts)
        self.fail(f"no {name} in {path.relative_to(REPO)}")

    def test_the_hook_lane_scrubs_the_same_variables_as_the_script(self) -> None:
        self.assertEqual(sorted(self._hook_scrub_list()), sorted(REPO_LOCATING))

    def test_the_hook_fixture_module_scrubs_the_same_variables(self) -> None:
        self.assertEqual(
            sorted(self._named_tuple_in(self.MODULE, "_GIT_ENV_VARS")), sorted(REPO_LOCATING))

    def test_every_hook_fixture_module_scrubs_the_same_variables(self) -> None:
        """Every module that builds a throwaway repo and RUNS THE HOOK in it carries this
        list, so each is a place the scrub can drift. Found by globbing rather than by
        naming them: a fixture module added next week is caught by the sweep below only if
        something here actually holds its copy to the list."""
        modules = sorted((REPO / "tools" / "tests").glob("test_precommit_*.py"))
        self.assertGreaterEqual(len(modules), 2, "the hook fixture modules moved or vanished")
        for path in modules:
            if "_GIT_ENV_VARS" not in path.read_text(encoding="utf-8"):
                continue     # a module that never shells out to git needs no scrub list
            with self.subTest(module=path.name):
                self.assertEqual(sorted(self._named_tuple_in(path, "_GIT_ENV_VARS")),
                                 sorted(REPO_LOCATING))

    def test_the_shipped_fixture_helper_scrubs_the_same_variables(self) -> None:
        """The skill suites' own git fixtures (BG0230). This copy is the one that matters most:
        it is the layer where a fixture git call is actually made, and it ships to consuming
        projects, where neither the hook nor `skill-tests.sh` exists to protect them."""
        self.assertEqual(
            sorted(self._named_tuple_in(self.GITUTIL, "REPO_LOCATING_GIT_VARS")),
            sorted(REPO_LOCATING))

    def test_the_script_itself_still_scrubs_them(self) -> None:
        """Closes the loop: without this, every copy could drift together away from the list
        this file asserts, and the tests above would still agree with each other."""
        prelude = _scrub_prelude()
        for var in REPO_LOCATING:
            self.assertIn(var, prelude, f"{var} dropped from tools/skill-tests.sh")


class ScrubSiteSweepTests(unittest.TestCase):
    """A new scrub list cannot arrive unpinned.

    The tests above hold the copies that exist today equal. They say nothing about the fifth
    copy someone adds next week, which is exactly how the hook's lane came to be unpinned. This
    sweep reads the repo instead of a fixed list: any code file naming several repo-locating
    variables must be registered in `SCRUB_SITES`, with what keeps it honest.
    """

    #: Two names, not one: a partial scrub is still a scrub list, and the two shipped scripts
    #: that clear only `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` are exactly what the sweep
    #: must not skip past. A single mention is usually prose about one variable.
    THRESHOLD = 2
    SKIP_DIRS = frozenset({".git", "node_modules", "__pycache__", ".local"})

    def _sites(self) -> dict[str, int]:
        """`{repo-relative path: how many repo-locating names it mentions}` for code files."""
        found: dict[str, int] = {}
        for path in sorted(REPO.rglob("*")):
            if not path.is_file() or self.SKIP_DIRS & set(path.parts):
                continue
            if path.suffix not in (".py", ".sh") and path.name != "pre-commit":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            hits = sum(1 for name in REPO_LOCATING if name in text)
            if hits >= self.THRESHOLD:
                found[str(path.relative_to(REPO))] = hits
        return found

    def test_the_sweep_still_finds_the_sites_it_exists_to_guard(self) -> None:
        """A sweep that stopped finding anything would pass over every copy in the tree."""
        sites = self._sites()
        for known in ("tools/skill-tests.sh", ".githooks/pre-commit"):
            self.assertIn(known, sites, f"the sweep no longer sees {known}")

    def test_every_scrub_site_is_registered(self) -> None:
        unregistered = sorted(set(self._sites()) - set(SCRUB_SITES))
        self.assertEqual(
            unregistered, [],
            "these files write out a git repo-locating scrub list that nothing pins: "
            f"{unregistered}. Add a test holding it to REPO_LOCATING, then register it in "
            "SCRUB_SITES saying what pins it.")

    def test_the_registry_has_no_rotted_entries(self) -> None:
        """An entry for a file that no longer carries a scrub list is dead weight the sweep
        would otherwise hide behind."""
        stale = sorted(set(SCRUB_SITES) - set(self._sites()))
        self.assertEqual(stale, [], f"registered files with no scrub list left: {stale}")

    def test_every_registry_entry_states_what_pins_it(self) -> None:
        blank = sorted(k for k, v in SCRUB_SITES.items() if not v.strip())
        self.assertEqual(blank, [], f"registry entries with no reason: {blank}")


if __name__ == "__main__":
    unittest.main()
