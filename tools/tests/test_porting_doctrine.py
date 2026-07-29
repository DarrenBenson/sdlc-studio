"""US0460: the porting doctrine is stated in ONE direction, and the stale facts beside it go.

The TRD and personas.md both said the installed copy at `~/.claude/skills/sdlc-studio/` was
the source of production fixes and that the repo back-ported from it. `tools/forward-port.sh`
says the opposite and always has: `SRC` is the repo tree and the target defaults to the
installed copy. The operator confirmed the script: **the repo is the source, and the installed
copy is a derived mirror.** The mirror is a deployment step, not an upstream.

These tests derive the direction FROM THE SCRIPT, so swapping its `SRC` and target reddens the
guard rather than leaving two documents unchallenged.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PERSONAS = REPO / "sdlc-studio" / "personas.md"
TRD = REPO / "sdlc-studio" / "trd.md"
FORWARD_PORT = REPO / "tools" / "forward-port.sh"

#: Wording that makes the installed copy the SOURCE of a fix. An absence rule, not a
#: majority rule: a repair must not be able to go green by adding one correct sentence above
#: four inverted ones, which is why each is applied to the whole extracted block.
_INVERTED = (
    r"back-?port",
    r"installed copy is the (?:back-?port )?source",
    r"fixes land (?:first )?in the installed",
    r"production fix source",
)


def _script_direction() -> tuple[str, str]:
    """`(src, target)` as `tools/forward-port.sh` declares them.

    Read from the script so the doctrine the docs are held to is the doctrine the tooling
    actually implements - not a third copy of it living in this test.
    """
    text = FORWARD_PORT.read_text(encoding="utf-8")
    src = re.search(r'^SRC="([^"]+)"', text, re.M)
    target = re.search(r'TARGET="\$\{HOME\}/([^"]+)"', text)
    assert src, "forward-port.sh declares no SRC - the direction cannot be derived"
    assert target, "forward-port.sh declares no HOME-rooted TARGET"
    return src.group(1), target.group(1)


def _block(path: Path, start: str, end_pattern: str) -> str:
    """The document block from the line containing `start` to the next `end_pattern` heading."""
    text = path.read_text(encoding="utf-8")
    i = text.find(start)
    assert i != -1, f"{path.name}: could not locate {start!r} - the passage was renamed"
    rest = text[i + len(start):]
    m = re.search(end_pattern, rest, re.M)
    return rest[:m.start()] if m else rest


class PortingDoctrineAgrees(unittest.TestCase):

    def test_the_docs_name_the_repo_as_source_derived_from_the_script(self) -> None:
        src, target = _script_direction()
        self.assertTrue(src.startswith(".claude/skills"),
                        f"forward-port.sh SRC is {src!r} - if the direction has genuinely "
                        f"changed, this guard and both documents must change together")
        self.assertTrue(target.startswith(".claude/skills"), f"unexpected target {target!r}")
        for path in (TRD, PERSONAS):
            text = path.read_text(encoding="utf-8")
            self.assertIn("forward-port.sh", text,
                          f"{path.name} does not name the tool that performs the mirror")
        self.assertIn("--check", TRD.read_text(encoding="utf-8"),
                      "the TRD does not name the drift gate")

    def test_a_reintroduced_backport_sentence_in_any_subsection_reddens(self) -> None:
        """An ABSENCE rule over the whole block, in both files. Applied per sentence it would
        pass as soon as one correct sentence existed, however many inverted ones sat below it."""
        blocks = {
            "personas.md Skill Maintainer card": _block(
                PERSONAS, "**Role:** Developer of SDLC Studio itself", r"^---\s*$"),
            "trd.md deployment + environment": _block(
                TRD, "### Deployment Topology", r"^## "),
        }
        for where, block in blocks.items():
            for pattern in _INVERTED:
                self.assertIsNone(
                    re.search(pattern, block, re.I),
                    f"{where}: {pattern!r} still makes the installed copy the fix source")

    def test_a_missing_card_section_or_script_fails_rather_than_passing_silently(self) -> None:
        """The failure mode that would let this whole guard pass on a document it never opened.

        `_block` returning "" for a renamed heading would satisfy every absence assertion in
        this class, and `_script_direction` returning a default for a missing script would make
        the derivation a restatement. Both must RAISE, naming what could not be read.
        """
        import tempfile
        with self.assertRaises(AssertionError) as ctx:
            _block(PERSONAS, "**Role:** A Heading Nobody Wrote", r"^---\s*$")
        self.assertIn("could not locate", str(ctx.exception),
                      "the failure does not name the passage it could not find")

        with self.assertRaises(AssertionError):
            _block(TRD, "### A Section That Was Removed", r"^## ")

        # A missing script: the direction cannot be derived, so nothing may be asserted from it.
        real = globals()["FORWARD_PORT"]
        with tempfile.TemporaryDirectory() as d:
            globals()["FORWARD_PORT"] = Path(d) / "absent.sh"
            try:
                with self.assertRaises((AssertionError, OSError)):
                    _script_direction()
            finally:
                globals()["FORWARD_PORT"] = real

    def test_the_absence_rule_can_actually_fail(self) -> None:
        """The positive control. Without it, a block-extractor that returned "" would pass
        every absence assertion above and prove nothing at all."""
        card = _block(PERSONAS, "**Role:** Developer of SDLC Studio itself", r"^---\s*$")
        self.assertTrue(card.strip(), "the extracted card is empty - the rule checks nothing")
        poisoned = card + "\nProduction fix source; back-ported here.\n"
        hits = [p for p in _INVERTED if re.search(p, poisoned, re.I)]
        self.assertTrue(hits, "a restored back-port sentence did not trip any pattern")


class StaleFactsAreRefreshed(unittest.TestCase):

    def test_no_bare_router_line_count_is_quoted_in_personas_or_the_trd(self) -> None:
        """A quoted count rots on every router edit, and both files quoted a different wrong
        one (~195 and ~260 against a real 270). The CEILING is the claim, and
        `tools/check_budgets.py` owns it - one number with one owner."""
        bare = re.compile(r"~\s*\d{2,4}\s+lines")
        for path in (PERSONAS, TRD):
            found = bare.findall(path.read_text(encoding="utf-8"))
            self.assertEqual([], found,
                             f"{path.name} quotes a bare line count {found} that rots on every "
                             f"router edit - cite the budgeted ceiling and its checker instead")

    def test_the_ceiling_and_its_owner_are_named_instead(self) -> None:
        """The positive control for the rule above: removing the count is only correct if the
        claim it replaced is still made, by its owner."""
        for path in (PERSONAS, TRD):
            text = path.read_text(encoding="utf-8")
            self.assertIn("check_budgets.py", text,
                          f"{path.name} dropped the count without naming what enforces the bound")

    def test_the_scripts_only_testing_claim_is_refused_while_the_tools_suite_exists(self) -> None:
        """Gated on the SUITE'S EXISTENCE rather than on someone noticing the claim went stale."""
        tool_suites = list((REPO / "tools" / "tests").glob("test_*.py"))
        self.assertTrue(tool_suites, "no tools suite - this guard would pass vacuously")
        text = PERSONAS.read_text(encoding="utf-8")
        self.assertNotRegex(
            text, r"only the scripts have unit tests",
            f"personas.md claims only the scripts are unit-tested while "
            f"{len(tool_suites)} tools test modules exist")


if __name__ == "__main__":
    unittest.main()
