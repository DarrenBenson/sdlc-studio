"""Tests for the shape of the help catalogue: it is grouped by the process spine.

The catalogue in `help/help.md` and the curated `command_audit.SPINE` map are two views of
the same fact - which stage of the process a command serves. These tests bind them together
so the two cannot disagree: a command placed under the wrong heading, or listed twice, fails
here rather than being discovered by an operator reading the page.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
_REPO = _SCRIPTS.parents[3]   # the real repo (has SKILL.md)
_HELP = _REPO / ".claude" / "skills" / "sdlc-studio" / "help" / "help.md"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
command_audit = _load("command_audit")

# The catalogue heading each spine category is published under. The keys are the `### `
# headings a reader sees; the values are `command_audit.SPINE`'s internal category names.
STAGE_HEADINGS: dict[str, str] = {
    "Raise": "raise",
    "Break Down": "break-down",
    "Sprint and Review": "sprint+review",
    "Levers": "lever",
    "Support": "support",
    "Utility": "utility",
}

_CMD_RE = re.compile(r"/sdlc-studio ([a-z][a-z-]*)")


def _all_command_sections(text: str) -> dict[str, str]:
    """The `### ` subsections of the "All Commands" catalogue, heading -> body.

    Scoped to that one section deliberately: commands are also named in the Getting Started
    examples and the Typical Workflows diagrams, and those are narrative, not the catalogue.
    """
    body = text.split("\n## All Commands\n", 1)[1]
    body = re.split(r"\n## ", body, maxsplit=1)[0]
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("### "):
            current = line[4:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _commands_in(body: str) -> set[str]:
    """The command tokens a catalogue section lists, ignoring redirect signposts (a folded
    command's redirect names it, but does not catalogue it)."""
    lines = [ln for ln in body.splitlines() if not command_audit._REDIRECT_RE.match(ln)]
    return {t for m in _CMD_RE.finditer("\n".join(lines)) if (t := m.group(1).rstrip("-"))}


class HelpSpineGroupingTests(unittest.TestCase):
    """Every catalogued command sits under the heading its spine category maps to."""

    def setUp(self) -> None:
        self.sections = _all_command_sections(_HELP.read_text(encoding="utf-8"))

    def test_every_spine_stage_has_a_section(self) -> None:
        for heading in STAGE_HEADINGS:
            self.assertIn(heading, self.sections, f"no `### {heading}` section in All Commands")

    def test_each_command_sits_under_its_spine_section(self) -> None:
        for heading, category in STAGE_HEADINGS.items():
            for cmd in _commands_in(self.sections.get(heading, "")):
                with self.subTest(heading=heading, command=cmd):
                    self.assertEqual(
                        command_audit.SPINE.get(cmd, "unmapped"), category,
                        f"`{cmd}` is listed under `### {heading}` but SPINE maps it to "
                        f"`{command_audit.SPINE.get(cmd, 'unmapped')}`")

    def test_no_command_is_listed_under_two_sections(self) -> None:
        seen: dict[str, str] = {}
        dupes: list[str] = []
        for heading in STAGE_HEADINGS:
            for cmd in _commands_in(self.sections.get(heading, "")):
                if cmd in seen:
                    dupes.append(f"`{cmd}` in both `{seen[cmd]}` and `{heading}`")
                else:
                    seen[cmd] = heading
        self.assertEqual(dupes, [], "; ".join(dupes))

    def test_every_spine_mapped_command_is_catalogued_somewhere(self) -> None:
        # the complement of the grouping check: a stage section must not be missing a command
        # the spine map knows about, or the rewrite silently dropped it from the page.
        catalogued: set[str] = set()
        for heading in STAGE_HEADINGS:
            catalogued |= _commands_in(self.sections.get(heading, ""))
        folded = set(command_audit._redirects(_HELP.parent.parent))
        missing = sorted(set(command_audit.SPINE) - catalogued - folded)
        self.assertEqual(missing, [], f"spine-mapped but absent from the catalogue: {missing}")


class HelpLeverPrecedenceTests(unittest.TestCase):
    """The document levers are the operator's top-level controls, so they are reached before
    the support and utility tooling."""

    LEVERS = ("prd", "trd", "tsd", "persona")

    def setUp(self) -> None:
        self.text = _HELP.read_text(encoding="utf-8")
        self.sections = _all_command_sections(self.text)

    def _pos(self, heading: str) -> int:
        i = self.text.find(f"\n### {heading}\n")
        self.assertNotEqual(i, -1, f"no `### {heading}` heading")
        return i

    def test_levers_section_precedes_support_and_utility(self) -> None:
        levers = self._pos("Levers")
        self.assertLess(levers, self._pos("Support"), "Levers must precede Support")
        self.assertLess(levers, self._pos("Utility"), "Levers must precede Utility")

    def test_levers_section_names_the_four_document_levers(self) -> None:
        listed = _commands_in(self.sections.get("Levers", ""))
        for lever in self.LEVERS:
            with self.subTest(lever=lever):
                self.assertIn(lever, listed, f"`{lever}` is not listed under `### Levers`")


class SprintInFlightControlDocsTests(unittest.TestCase):
    """Every sprint verb is documented as an INVOCATION somebody can run.

    A verb whose name merely appears in prose is not documented: the reader still cannot run
    it, and a page that mentions every word while showing no command passes a word-search while
    teaching nothing.
    """

    SKILL = Path(__file__).resolve().parents[1].parent

    def _parser_verbs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sprint", self.SKILL / "scripts" / "sprint.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["sprint"] = mod
        spec.loader.exec_module(mod)
        parser = mod.build_parser()
        for action in parser._actions:
            if hasattr(action, "choices") and action.choices and action.dest == "cmd":
                return sorted(action.choices), mod
        self.fail("the sprint parser exposes no subcommand choices")

    def test_every_parser_verb_appears_as_an_invocation_and_a_prose_only_page_fails(self) -> None:
        """MUTANT: document a verb by naming it in a sentence.

        Derived from the PARSER, so a verb added tomorrow is covered without editing this - and
        matched as `sprint.py <verb>`, which prose mentioning the word does not satisfy.
        """
        verbs, _mod = self._parser_verbs()
        page = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        # EITHER invocation form counts: the script path a script-level reader runs, and the
        # `/sdlc-studio sprint <verb>` slash form a skill user types. Both are real commands, so
        # requiring one spelling would fail a page that documents the other perfectly well.
        missing = [v for v in verbs
                   if f"sprint.py {v}" not in page and f"/sdlc-studio sprint {v}" not in page]
        self.assertEqual([], missing,
                         f"these verbs are not shown as a runnable invocation: {missing}")

    def test_every_extracted_invocation_parses_and_the_extraction_is_not_empty(self) -> None:
        """MUTANT: extract nothing, or document a command the parser rejects.

        The EMPTINESS check is half the test: an extractor that matches nothing reports every
        invocation valid, which is the vacuous-pass shape this project keeps meeting.
        """
        import re as _re
        verbs, mod = self._parser_verbs()
        page = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        # FENCED blocks only. A verb named in a sentence is prose, not an invocation, and
        # scraping prose pulls in flags and ordinary words - which would make this assert that
        # the English around a command parses.
        fenced = "\n".join(_re.findall(r"```[a-z]*\n(.*?)```", page, _re.S))
        self.assertTrue(fenced.strip(), "the page shows no fenced commands at all")
        found = _re.findall(r"(?:sprint\.py|/sdlc-studio sprint)\s+([a-z][a-z-]*)", fenced)
        self.assertTrue(found, "the extraction matched no invocations at all")
        unknown = sorted({v for v in found if v not in verbs})
        self.assertEqual([], unknown,
                         f"the page shows invocations the parser does not accept: {unknown}")

    def test_reference_sprint_carries_a_named_in_flight_control_section_with_the_invocations(self) -> None:
        """MUTANT: document the controls in help only.

        A reader working through the reference should not have to leave it to learn how to
        change a run that is already open.
        """
        ref = (self.SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        self.assertIn("{#in-flight-controls}", ref,
                      "the reference has no named in-flight-control section to link to")
        for verb in ("batch swap", "batch drop", "stop", "reopen", "goal-review"):
            with self.subTest(verb=verb):
                self.assertIn(f"sprint.py {verb}", ref,
                              f"the reference section does not carry `{verb}`")


_SPRINT_HELP = _REPO / ".claude" / "skills" / "sdlc-studio" / "help" / "sprint.md"
_ARGUMENTS = _REPO / ".claude" / "skills" / "sdlc-studio" / "help" / "arguments.md"
_PRE_REWRITE = _SCRIPTS / "tests" / "fixtures" / "sprint-help-pre-rewrite.md"


def _sprint_verbs() -> list[str]:
    """Every subcommand the SHIPPED parser owns, read from the parser itself.

    Derived, never listed here. The story that asked for this named twelve verbs; the parser
    carries eighteen, because `call`, `next`, `queue`, `lane`, `appetite` and `review-batch`
    landed after it was written. An enumeration of a rule is a lower bound, not a boundary - a
    hard-coded list would have silently exempted the six newest verbs, which are exactly the
    ones a page is most likely not to document yet.
    """
    import argparse
    sprint = _load("sprint")
    for action in sprint.build_parser()._actions:
        if isinstance(action, argparse._SubParsersAction):
            return sorted(action.choices)
    raise AssertionError("sprint.build_parser() exposes no subparser tree to derive verbs from")


def _invocation_re(verb: str) -> re.Pattern:
    """A verb in INVOCATION form, never as a bare substring.

    This distinction is the whole check. On the pre-rewrite page `stop`, `batch`, `breakdown`,
    `call`, `goal-verdict`, `lane`, `next` and `preflight` all appear as ordinary words while
    none of them is documented as a command, so a substring match reported full coverage of a
    page that documented none of them.
    """
    v = re.escape(verb)
    return re.compile(rf"(?:/sdlc-studio\s+sprint\s+{v}\b)|(?:sprint\.py\s+{v}\b)")


def _undocumented(text: str) -> list[str]:
    return [v for v in _sprint_verbs() if not _invocation_re(v).search(text)]


def _documents_flag(text: str, flag: str) -> bool:
    """True when `text` documents `flag` as a WHOLE flag.

    Not a substring test. `assertIn("--force", page)` is satisfied by `--forcible`, which is
    how the first version of this check reported a documented flag that had been renamed away -
    the very confusion between a bare substring and a real match that this page's verb check
    exists to prevent. Caught by mutation: the renamed-flag mutant survived.
    """
    return re.search(rf"{re.escape(flag)}(?![a-z0-9-])", text) is not None


class SprintSurfaceTests(unittest.TestCase):
    """US0468: the sprint help page is bound to the shipped surface, not written beside it.

    Every fact these tests demand is read from `build_parser` or from `lib/run_state`, so a verb
    added, a flag renamed or a ledger key changed fails HERE rather than leaving the page quietly
    describing a tool that no longer exists.
    """

    def _page(self) -> str:
        self.assertTrue(_SPRINT_HELP.is_file(), f"the sprint help page is missing: {_SPRINT_HELP}")
        return _SPRINT_HELP.read_text(encoding="utf-8")

    def test_every_shipped_verb_appears_in_invocation_form_and_the_pre_rewrite_page_fails(self):
        """MUTANT: match verbs as bare substrings instead of in invocation form.

        The fixture is the REAL page from before the rewrite (72265e63^), not a contrived one,
        and the same check must fail over it. Without that half, a check that passes on today's
        page proves only that today's page exists.
        """
        verbs = _sprint_verbs()
        self.assertTrue(verbs, "no verbs were derived - the check would pass over nothing")
        self.assertEqual(_undocumented(self._page()), [],
                         "shipped verbs are undocumented in invocation form")

        self.assertTrue(_PRE_REWRITE.is_file(), f"the discriminating fixture is missing: {_PRE_REWRITE}")
        pre = _PRE_REWRITE.read_text(encoding="utf-8")
        missing_pre = _undocumented(pre)
        self.assertTrue(missing_pre,
                        "the pre-rewrite fixture passes the check, so the check discriminates "
                        "nothing - it would pass on a page documenting no verb at all")
        for verb in ("batch", "stop", "reopen", "preflight", "breakdown",
                     "goal-verdict", "goal-review"):
            with self.subTest(verb=verb):
                self.assertIn(verb, missing_pre,
                              f"{verb} is not caught on the pre-rewrite page")
        substring_only = [v for v in missing_pre if re.search(rf"\b{re.escape(v)}\b", pre)]
        self.assertTrue(substring_only,
                        "no fixture verb appears as a bare word, so this fixture cannot show "
                        "that invocation form is stricter than a substring match")

    def test_batch_and_stop_sections_name_every_recorded_key_and_the_drop_versus_deferred_rule(self):
        """MUTANT: add a key to `batch_changes` and leave the page alone.

        The keys are read from the module that writes them, so the page cannot drift from the
        ledger without this reddening.
        """
        import inspect
        run_state = _load("run_state") if (_SCRIPTS / "run_state.py").exists() else None
        if run_state is None:                       # it lives under lib/
            sys.path.insert(0, str(_SCRIPTS))
            from lib import run_state               # noqa: PLC0415
        src = inspect.getsource(run_state)
        keys = set(re.findall(r'"(action|id|reason|at|note)":', src))
        self.assertTrue(keys, "no batch_changes keys were derived from run_state")
        page = self._page()
        for key in sorted(keys):
            with self.subTest(key=key):
                self.assertRegex(page, rf"`{key}`|\b{key}\b",
                                 f"the batch-mutation section never names the recorded key {key!r}")
        self.assertIn("Deferred", page,
                      "the page does not state the drop-versus-Deferred distinction")
        self.assertRegex(page, r"drop.{0,400}?Deferred|Deferred.{0,400}?drop",
                         "drop and Deferred are both mentioned but never contrasted")
        self.assertTrue(_documents_flag(page, "--force"),
                        "stop's --force is undocumented")

    def test_every_documented_invocation_resolves_across_verb_first_and_flag_first_classes(self):
        """MUTANT: drop the flag-first class, or stop consulting help/arguments.md.

        Both classes must be non-empty, so an over-tight filter cannot report coverage it never
        achieved by matching nothing.
        """
        import argparse
        sprint = _load("sprint")
        verbs = set(_sprint_verbs())
        page = self._page()
        args_ref = _ARGUMENTS.read_text(encoding="utf-8")

        verb_first, flag_first = [], []
        for line in re.findall(r"/sdlc-studio\s+sprint\s+[^\n`]+", page):
            rest = line.split("sprint", 1)[1].strip()
            (verb_first if rest.split()[:1] and rest.split()[0] in verbs else flag_first).append(rest)
        self.assertTrue(verb_first, "no verb-first example was found to check")
        self.assertTrue(flag_first, "no flag-first example was found to check")

        owned = set()
        for action in sprint.build_parser()._actions:
            if isinstance(action, argparse._SubParsersAction):
                for sub in action.choices.values():
                    owned |= {o for a in sub._actions for o in a.option_strings}
            owned |= set(action.option_strings)
        for example in verb_first + flag_first:
            for flag in re.findall(r"--[a-z][a-z0-9-]+", example):
                with self.subTest(flag=flag):
                    self.assertTrue(flag in owned or flag in args_ref,
                                    f"{flag} is documented on the sprint page but owned by no "
                                    f"parser and absent from help/arguments.md")

    def test_appetite_and_rolling_sections_name_every_recorded_field_and_flag(self):
        """MUTANT: rename a field in `appetite_record` and leave the page alone."""
        import inspect
        sys.path.insert(0, str(_SCRIPTS))
        from lib import run_state                   # noqa: PLC0415
        src = inspect.getsource(run_state.appetite_record)
        fields = set(re.findall(r'"([a-z_]+)":', src))
        self.assertTrue(fields, "no appetite fields were derived")
        page = self._page()
        for field in sorted(fields):
            with self.subTest(field=field):
                self.assertIn(field, page,
                              f"the appetite section never names the recorded field {field!r}")
        for flag in ("--appetite-minutes", "--appetite-units", "--cycles", "--stop-on"):
            with self.subTest(flag=flag):
                self.assertTrue(_documents_flag(page, flag), f"{flag} is undocumented")
        self.assertRegex(page, r"regenerates the plan at each boundary|regenerate.{0,60}boundary",
                         "the rolling section does not say a rolling run re-plans at each "
                         "boundary rather than queueing plans")

    def test_binder_fails_loud_when_the_page_or_section_is_missing(self):
        """MUTANT: return an empty list from `_undocumented` when the page cannot be read.

        An absent page and a page with nothing wrong in it must never read the same. Every check
        above asserts a non-zero derived count for the same reason.
        """
        self.assertTrue(_undocumented(""),
                        "an EMPTY page reports full verb coverage - the binder passes vacuously")
        self.assertTrue(_undocumented("# sprint\n\nnothing here documents a command.\n"),
                        "a page with no commands reports full coverage")
        self.assertTrue(_sprint_verbs(), "the derived verb set is empty, so nothing is checked")



if __name__ == "__main__":
    unittest.main()
