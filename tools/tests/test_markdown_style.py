"""The markdown emphasis style this repo's configs pin, and what `--fix` may rewrite (BG0566).

MD050 enforces a CONSISTENT strong-emphasis style per file and, left to itself, INFERS that
style from the first occurrence. A bare `__init__.py` anywhere in a document is an occurrence,
so one filename in a bug title decided how the whole file was rewritten: `npm run lint:fix`
converted every `> **Status:**` metadata line to `> __Status:__`, and the schema reader then
reported `[no-status]` on an artefact the tool itself had just rewritten. Restoring the
asterisks made markdownlint fail again - two guards with no shared fixed point.

The style is now PINNED to `asterisk`, so nothing is inferred and the metadata block cannot be
flipped. That is the half tested here. The other half - the token itself, which a pinned style
rewrites to `**init**.py` instead - is refused before `--fix` can reach it by the bare-dunder
lane in `tools/lint-style.sh` (see `tools/tests/test_lint_style.py`).

Every case runs under `tempfile`; nothing is written inside the repository.

Run from the repo root:
    python3 -m pytest tools/tests/test_markdown_style.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT_CONFIG = REPO / ".markdownlint.json"
PAYLOAD_CONFIG = REPO / ".claude" / "skills" / "sdlc-studio" / ".markdownlint.json"

sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"))
from lib import sdlc_md  # noqa: E402 - the shipped schema reader, not a second copy of it

#: An artefact as the writers mint one: an H1 carrying a bare dunder, then the metadata block
#: the schema reader matches. This is the exact shape that was destroyed.
ARTEFACT = """\
# BG0001: the loader skips __init__.py in a package directory

> **Status:** Open
> **Severity:** High
> **Points:** 3

## Summary

Something.
"""

#: The same artefact with the token backticked - the one spelling both guards leave alone.
ARTEFACT_BACKTICKED = ARTEFACT.replace("__init__.py", "`__init__.py`")

#: A document that uses underscore strong emphasis CONSISTENTLY. With the style inferred it is
#: clean, because the inference agrees with it; with the style pinned it is reported. That is
#: what separates "pinned to asterisk" from "MD050 switched off", and no fixture mixing the two
#: spellings can tell them apart - both are reported either way, only on different lines.
UNDERSCORE_PROSE = "# A title\n\nThis is __very__ important and __so__ is this.\n"


def _markdownlint() -> str:
    """The markdownlint binary the gate itself would use, or a skip naming what is missing."""
    local = REPO / "node_modules" / ".bin" / "markdownlint"
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    found = shutil.which("markdownlint")
    if found:
        return found
    raise unittest.SkipTest(
        "markdownlint is not installed (run `npm install`), so what `--fix` does to an "
        "artefact cannot be executed here. The config-shape case below still runs.")


def _lint(target: Path, *, config: Path | None = None,
          fix: bool = False) -> subprocess.CompletedProcess:
    """Lint one file exactly as a gate lane does: from the repo root, so an omitted `--config`
    is resolved by markdownlint's own discovery rather than by this test."""
    cmd = [_markdownlint()]
    if config is not None:
        cmd += ["--config", str(config)]
    if fix:
        cmd.append("--fix")
    cmd.append(str(target))
    return subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)


class MetadataSurvivesFixTests(unittest.TestCase):
    """The artefact is schema, not prose, so `--fix` must not be able to unmake it."""

    def test_a_bare_dunder_no_longer_flips_the_metadata_block_to_underscores(self) -> None:
        """MUTANT: drop `"MD050": { "style": "asterisk" }` from `.markdownlint.json`. The style
        is then inferred from the H1's dunder, `--fix` rewrites all three metadata lines, and
        `extract_field` returns None on a file the tool itself wrote.

        The BACKTICKED variant is asserted in the same case, because either half alone has a
        trivial wrong answer: a file nothing touches is not necessarily a file that passes, and
        a metadata block that survives says nothing about the fixed point the two guards need."""
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "BG0001-x.md"
            target.write_text(ARTEFACT, encoding="utf-8")
            _lint(target, fix=True)          # the root lane's invocation: no --config
            after = target.read_text(encoding="utf-8")
            self.assertEqual("Open", sdlc_md.extract_field(after, "Status"),
                             f"the schema reader lost the Status:\n{after}")
            self.assertEqual("High", sdlc_md.extract_field(after, "Severity"))
            self.assertEqual("3", sdlc_md.extract_field(after, "Points"))
            self.assertNotIn("__Status:__", after)

            fixed_point = Path(d) / "BG0003-x.md"
            fixed_point.write_text(ARTEFACT_BACKTICKED, encoding="utf-8")
            _lint(fixed_point, fix=True)
            self.assertEqual(ARTEFACT_BACKTICKED, fixed_point.read_text(encoding="utf-8"),
                             "--fix rewrote an artefact whose dunder was already backticked")
            self.assertEqual(0, _lint(fixed_point).returncode,
                             "the artefact survives --fix but does not satisfy the linter")

    def test_the_payload_config_inherits_the_pin_it_does_not_restate_it(self) -> None:
        """The shipped payload is linted under its own config, which `extends` the root one.
        A pin the payload lane does not inherit would leave every template and reference page
        on the inferred style, which is where most of the corpus lives.

        MUTANT: restate `"MD050": { "style": "consistent" }` in the payload config. `extends`
        merges rather than replaces, so the nearer value wins and the payload lane goes back to
        inferring - with the root config still pinned and this file's sibling case still green."""
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "BG0002-x.md"
            target.write_text(ARTEFACT, encoding="utf-8")
            _lint(target, config=PAYLOAD_CONFIG, fix=True)
            after = target.read_text(encoding="utf-8")
            self.assertEqual("Open", sdlc_md.extract_field(after, "Status"),
                             f"the payload lane's config did not inherit the pin:\n{after}")
            self.assertNotIn("__Status:__", after)


class StylePinnedNotDisabledTests(unittest.TestCase):
    """A rule switched off would satisfy every case above and check nothing."""

    def test_underscore_strong_emphasis_in_prose_is_still_reported(self) -> None:
        """MUTANT: set `"MD050": false` instead of pinning the style. The document below is
        consistently underscore-styled, so an INFERRED style also reports nothing on it - which
        is why this fixture, and not a mixed one, is the discriminator."""
        for name, config in (("root", None), ("payload", PAYLOAD_CONFIG)):
            with self.subTest(config=name), tempfile.TemporaryDirectory() as d:
                target = Path(d) / "prose.md"
                target.write_text(UNDERSCORE_PROSE, encoding="utf-8")
                proc = _lint(target, config=config)
                # markdownlint reports on stderr; both streams are read so the assertion
                # cannot pass on an empty stdout while the finding sat in the other pipe.
                report = proc.stdout + proc.stderr
                self.assertEqual(1, proc.returncode,
                                 f"underscore emphasis passed the {name} config:\n{report}")
                self.assertIn("MD050", report)

    def test_the_root_config_pins_the_strong_style_rather_than_inferring_it(self) -> None:
        """The half that runs with no Node on the machine. `consistent` is MD050's default and
        is exactly the inference this bug was: it is not a value this config may carry."""
        import json
        config = json.loads(ROOT_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual({"style": "asterisk"}, config.get("MD050"),
                         "the root markdownlint config does not pin the strong-emphasis style, "
                         "so it is inferred per file and one dunder decides how the whole "
                         "document is rewritten")


class FixIsGuardedByTheStyleLaneTests(unittest.TestCase):
    """`npm run lint:fix` is the command BG0566 is titled after, and it ran the fixer with no
    precondition.

    The bare-dunder refusal that stops `--fix` unmaking an artefact lives in
    `tools/lint-style.sh`, and the fix command reached markdownlint without ever calling it. A
    guard is only in force where the command people actually run consults it, so the script
    chains the style lane ahead of the fixer and stops on its non-zero exit.

    The chain is repo-wide, not scoped to the files about to be rewritten: `lint:style` reads
    the whole tree, so an unrelated style finding elsewhere now blocks the fixer too. That is
    the deliberate trade - the fixer is a whole-tree pass itself, and a scoped precondition
    would leave the file it is about to rewrite unguarded whenever the scope missed it.
    """

    def test_lint_fix_runs_the_style_lane_before_the_fixer(self) -> None:
        """MUTANT: drop the `lint:style &&` head from `lint:fix`.

        Read as an ORDERED chain, not as a mention: the fixer must not be reachable when the
        style lane exits non-zero, so a `lint:fix` that merely names the lane afterwards - or
        joins it with `;` - fails here.
        """
        import json
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        fix = scripts["lint:fix"]
        self.assertIn("--fix", fix, "lint:fix no longer runs the fixer at all")
        head, sep, tail = fix.partition("&&")
        self.assertTrue(sep, "lint:fix does not chain anything ahead of the fixer, so the "
                             "bare-dunder refusal that protects it never runs (BG0566)")
        self.assertIn("lint:style", head,
                      "the style lane does not run BEFORE the fixer, so `npm run lint:fix` can "
                      "still rewrite an artefact the style guard would have refused")
        self.assertIn("--fix", tail, "the fixer runs before the style lane rather than after it")
        self.assertNotIn("lint:style", tail)


if __name__ == "__main__":
    unittest.main()
