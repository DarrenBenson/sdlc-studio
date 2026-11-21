"""`vitest <file> -t "name"` and `jest <file> -t "name"` select the test they name.

The two verbs folded the whole tail into the `-t` pattern, so the file argument became part of
the name and nothing matched, and they called a bare binary that a Node project rarely has on
PATH. The tail is now split: positional arguments stay positional, `-t` (or
`--testNamePattern`) carries only the name, matched literally, and the runner is reached through
the project's `node_modules/.bin` or `npx` when the bare binary is absent. The older form, a
bare pattern with no `-t`, is unchanged.

Every launcher case runs a fake runner through `run_verifier` and reads back the argv the
runner received, so a command that is built right and launched wrong still fails here.
"""
from __future__ import annotations

import os
import re
import tempfile
import unittest
import unittest.mock
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

NAME = "adds two numbers"
FILE = "src/a.test.ts"

# A fake runner: records each argument on its own line beside itself, then reports a pass.
# Shell builtins only, because the fixture's PATH holds nothing else.
FAKE = ("#!/bin/sh\n"
        "for a in \"$@\"; do printf '%s\\n' \"$a\"; done > \"${0%/*}/argv.${0##*/}\"\n"
        "echo 'Tests  1 passed (1)'\n")


def _fake(bin_dir: Path, name: str) -> Path:
    bin_dir.mkdir(parents=True, exist_ok=True)
    p = bin_dir / name
    p.write_text(FAKE, encoding="utf-8")
    p.chmod(0o755)
    return p


def _argv_seen(bin_dir: Path, name: str) -> list[str]:
    seen = bin_dir / f"argv.{name}"
    return seen.read_text(encoding="utf-8").splitlines() if seen.exists() else []


class VitestFileAndNameTests(unittest.TestCase):

    def _run(self, project: Path, path_dir: Path, expr: str):
        """`run_verifier` with PATH holding only `path_dir`, so which runner is "on PATH" is
        decided by this fixture and never by the machine running the suite."""
        path_dir.mkdir(parents=True, exist_ok=True)
        with unittest.mock.patch.dict(os.environ, {"PATH": str(path_dir)}):
            return verify_ac.run_verifier(expr, timeout=30, cwd=project)

    def test_file_and_name_are_separate_arguments(self) -> None:
        # The command each verb builds: the file positional, only the name after -t.
        for flag in (f'-t "{NAME}"', f'--testNamePattern "{NAME}"',
                     f'"--testNamePattern={NAME}"'):
            with self.subTest(flag=flag):
                self.assertEqual(verify_ac._build_command(f"vitest {FILE} {flag}"),
                                 ("vitest", ["vitest", "run", FILE, "-t", NAME]))
                self.assertEqual(verify_ac._build_command(f"jest {FILE} {flag}"),
                                 ("jest", ["jest", FILE, "-t", NAME]))
        # Positive control: the older bare-pattern form keeps its meaning.
        self.assertEqual(verify_ac._build_command('jest "login happy path"'),
                         ("jest", ["jest", "-t", "login happy path"]))
        self.assertEqual(verify_ac._build_command('vitest "submits form"'),
                         ("vitest", ["vitest", "run", "-t", "submits form"]))
        # A -t with no name, an empty one or two of them is an invalid verifier, never a run
        # with a pattern the author did not write.
        for bad in (f"vitest {FILE} -t", f'vitest {FILE} -t ""', f"jest {FILE} -t a -t b"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                verify_ac._build_command(bad)
        # A bare tail shlex cannot split is still the bare form, read as it always was.
        self.assertEqual(verify_ac._build_command("jest it's fine"),
                         ("jest", ["jest", "-t", "it's fine"]))

        # How each verb is launched, read back from the argv the runner received.
        for verb, expected in (("vitest", ["run", FILE, "-t", NAME]),
                               ("jest", [FILE, "-t", NAME])):
            expr = f'{verb} {FILE} -t "{NAME}"'
            with self.subTest(verb=verb, launcher="node_modules/.bin"), \
                    tempfile.TemporaryDirectory() as d:
                project, local = Path(d) / "proj", Path(d) / "proj" / "node_modules" / ".bin"
                _fake(local, verb)
                r = self._run(project, Path(d) / "empty-path", expr)
                self.assertTrue(r.ok, r.stderr)
                self.assertEqual(_argv_seen(local, verb), expected)
            with self.subTest(verb=verb, launcher="npx"), tempfile.TemporaryDirectory() as d:
                project, path_dir = Path(d) / "proj", Path(d) / "path"
                project.mkdir()
                _fake(path_dir, "npx")
                r = self._run(project, path_dir, expr)
                self.assertTrue(r.ok, r.stderr)
                self.assertEqual(_argv_seen(path_dir, "npx"), ["--no-install", verb, *expected])
            with self.subTest(verb=verb, launcher="PATH first"), \
                    tempfile.TemporaryDirectory() as d:
                project, path_dir = Path(d) / "proj", Path(d) / "path"
                local = project / "node_modules" / ".bin"
                _fake(local, verb)
                _fake(path_dir, verb)
                r = self._run(project, path_dir, expr)
                self.assertTrue(r.ok, r.stderr)
                self.assertEqual(_argv_seen(path_dir, verb), expected)
                self.assertEqual(_argv_seen(local, verb), [], "the bare binary on PATH "
                                 "was passed over for the project-local one")

    def test_a_metacharacter_in_the_name_is_literal_or_warned(self) -> None:
        title = r"renders (empty) [list] a.b+c? ^x$ {1} | \ *"
        near_miss = r"renders empty list aXb+c x 1 \ "
        for verb in ("vitest", "jest"):
            with self.subTest(verb=verb):
                _kind, argv = verify_ac._build_command(f"{verb} {FILE} -t '{title}'")
                pattern = argv[argv.index("-t") + 1]
                # The pattern a regex engine compiles matches the title as written, and only
                # it: JavaScript's RegExp and Python's re agree on a backslash-escaped
                # metacharacter, which is all the escape emits.
                self.assertIsNotNone(re.search(pattern, title), pattern)
                self.assertIsNone(re.search(pattern, near_miss), pattern)
                self.assertNotEqual(pattern, title, "a metacharacter reached -t unescaped")
                # Positive control: a plain name reaches -t untouched.
                _kind, plain = verify_ac._build_command(f'{verb} {FILE} -t "{NAME}"')
                self.assertEqual(plain[plain.index("-t") + 1], NAME)
        # The older bare-pattern form is still a regex, as it always was.
        self.assertEqual(verify_ac._build_command("jest ^login$")[1], ["jest", "-t", "^login$"])
        # The jest batch cache never answers the file-and-name form with its bare-pattern
        # matcher; it hands the line to the per-criterion run.
        asserts = [{"name": f"{FILE} -t {NAME}", "ok": True}, {"name": NAME, "ok": True}]
        self.assertIsNone(verify_ac.resolve_jest_from_cache(f"jest {FILE} -t {NAME}", asserts))
        self.assertIsNotNone(verify_ac.resolve_jest_from_cache(f'jest "{NAME}"', asserts))


if __name__ == "__main__":
    unittest.main()
