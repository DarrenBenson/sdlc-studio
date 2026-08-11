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


_IN_FLIGHT_HEADING = "## In-flight controls {#in-flight-controls}"

#: The controls the reference's own in-flight section must carry, as invocations. `batch
#: add-epic` and `appetite resize` are here because they are in-flight controls too, and a list
#: that omitted them let the two newest ship undocumented in the reference.
_IN_FLIGHT_CONTROLS = ("batch swap", "batch drop", "batch add", "batch add-epic",
                       "appetite resize", "stop", "reopen", "goal-review")


#: The two SURFACES the page documents a sprint invocation on, each anchored at the start of the
#: line and matching only up to the end of its prefix - what follows is the argv a user passes.
#: Anchored so a fenced line invoking a DIFFERENT script (`sprint_report.py`, `artifact.py`) is
#: not read as a sprint invocation, and the `python3 <path>` head is optional on the script
#: surface because the page has spelled the same command both ways.
_INVOCATION_SURFACES = (
    ("slash", re.compile(r"^/sdlc-studio\s+sprint\b")),
    ("script", re.compile(r"^(?:python3\s+(?:\S*/)?)?sprint\.py\b")),
)


def _fenced_invocations(page: str) -> list[tuple[str, str]]:
    """Every documented sprint invocation in a FENCED block, as `(surface, argv)` pairs.

    BOTH surfaces, and the surface is carried out with the argv because the two are not the same
    parser: the slash surface owns flags the script's does not, so a check that forgets which one
    a line came from either refuses a real slash example or accepts a script line that no parser
    would run. Filtering to `/sdlc-studio sprint` left every script-form line unchecked (BG0497).

    Continuations are joined FIRST. A trailing `\\` line reaching `shlex.split` on its own raises
    `ValueError: No escaped character`, and its flags - seven of them on this page - are on the
    lines below, which arrive as invocations of nothing and are silently dropped.

    Fenced only. A verb named in a sentence is prose, not an invocation, and scraping prose
    pulls in flags and ordinary words - which would make this assert that the English around a
    command parses.
    """
    fenced = "\n".join(re.findall(r"```[a-z]*\n(.*?)```", page, re.S))
    joined: list[str] = []
    for line in fenced.splitlines():
        line = line.strip()
        if joined and joined[-1].endswith("\\"):
            joined[-1] = f"{joined[-1][:-1].rstrip()} {line}"
        else:
            joined.append(line)
    out = []
    for line in joined:
        for surface, prefix in _INVOCATION_SURFACES:
            match = prefix.match(line)
            if match:
                out.append((surface, line[match.end():].split("  #", 1)[0].strip()))
                break
    return out


def _skill_only_flags(arguments_page: str) -> set[str]:
    """The flags `help/arguments.md` DECLARES as belonging to the slash surface rather than to
    `sprint.py`'s parser.

    The slash surface is a superset of the script's, deliberately: `--autonomous` names a mode
    the skill runs, and the page says so in terms. Read from the declaration rather than
    hard-coded, so an undeclared flag on the page is still refused below - which is the whole
    difference between modelling two surfaces and excusing whatever fails.
    """
    out = set()
    for row in arguments_page.splitlines():
        if not row.startswith("|") or "parser flag" not in row:
            continue
        # The row's FIRST cell only - its subject. The description cell names other flags in
        # passing (the `--autonomous` row explains itself by pointing at `--goal`), and reading
        # the whole row exempted a flag the parser does own.
        subject = re.match(r"\|\s*`(--[a-z][a-z0-9-]*)`\s*\|", row)
        if subject:
            out.add(subject.group(1))
    return out


def _unparsable_invocations(invocations: list[tuple[str, str]]) -> list[str]:
    """The documented invocations `sprint.build_parser()` refuses, as `(surface, argv)` pairs.

    PARSED, never verb-matched. The check read the bare verb WORD and asked whether the parser
    knew it, so every flag on every documented line went unlooked-at and `--nonexistent-flag
    zzz` was documented as freely as a real one.

    The slash-only exemption is SCOPED to the slash surface. Applied to both, a script-form
    `--autonomous` - an invocation `sprint.py` genuinely refuses - reads as documented, which
    turns the repair into the rubber stamp it exists to refuse (BG0497).
    """
    import argparse                                 # noqa: PLC0415
    import contextlib                               # noqa: PLC0415
    import io                                       # noqa: PLC0415
    import shlex                                    # noqa: PLC0415
    sprint = _load("sprint")
    parser = sprint.build_parser()
    verbs = {name for a in parser._actions if isinstance(a, argparse._SubParsersAction)
             for name in a.choices}
    skill_only = _skill_only_flags(_ARGUMENTS.read_text(encoding="utf-8"))
    bad = []
    for surface, invocation in invocations:
        argv = shlex.split(invocation)
        # The flag-first front-door form is plan-shaped: `/sdlc-studio sprint --bugs Open` is
        # `plan --bugs Open`, which is how the page's own Flags table describes it.
        if not argv or argv[0] not in verbs:
            argv = ["plan"] + argv
        if surface == "slash":
            argv = [a for a in argv if a not in skill_only]
        buf = io.StringIO()
        try:
            with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(buf):
                parser.parse_args(argv)
        except SystemExit:
            bad.append(f"{surface}: {invocation}  ->  {buf.getvalue().strip().splitlines()[-1:]}")
    return bad


def _controls_missing_from_in_flight_section(ref: str) -> list[str] | None:
    """The in-flight controls the reference's OWN section body does not carry, or None when
    there is no such section.

    Scoped to the section. The check looked for `{#in-flight-controls}` anywhere in the file -
    which the generated reading-guide row at the top also contains, so deleting the heading left
    it green - and then looked for each invocation file-wide, so moving the block out of the
    section and emptying it passed as well.
    """
    if _IN_FLIGHT_HEADING not in ref:
        return None
    body = ref.split(_IN_FLIGHT_HEADING, 1)[1]
    body = re.split(r"\n## ", body, maxsplit=1)[0]
    # A WHOLE verb, not a substring: `sprint.py batch add` is a prefix of `batch add-epic`, so a
    # plain `in` reported the shorter one documented by the longer one's line alone.
    return [c for c in _IN_FLIGHT_CONTROLS
            if not re.search(rf"sprint\.py {re.escape(c)}(?![\w-])", body)]


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
        """MUTANT: document `--nonexistent-flag zzz`, or extract nothing.

        The EMPTINESS check is half the test, and it is emptiness PER SURFACE: a bare `found`
        was satisfied by the page's nineteen slash lines while the filter matched not one of the
        twenty-three script-form lines, which is exactly how that regression shipped green. An
        extractor that matches nothing reports every invocation valid, which is the vacuous-pass
        shape this project keeps meeting. The other half is that the line is PARSED, not scanned
        for its verb word: this matched the bare verb and never looked at a flag, so a documented
        flag no parser owns survived (BG0497).
        """
        page = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        found = _fenced_invocations(page)
        self.assertTrue(found, "the extraction matched no invocations at all")
        surfaces = {surface for surface, _ in found}
        self.assertIn("slash", surfaces,
                      "no `/sdlc-studio sprint` invocation was extracted, so the slash surface "
                      "is reported clean by matching nothing")
        self.assertIn("script", surfaces,
                      "no `sprint.py` invocation was extracted, so the script surface is "
                      "reported clean by matching nothing - the shape of BG0497 itself")
        rejected = _unparsable_invocations(found)
        self.assertEqual([], rejected,
                         f"the page shows invocations the parser does not accept: {rejected}")

    def test_reference_sprint_carries_a_named_in_flight_control_section_with_the_invocations(self) -> None:
        """MUTANT: move the in-flight fenced block out of its own section.

        A reader working through the reference should not have to leave it to learn how to
        change a run that is already open - and the lookup was file-wide, so emptying the
        section while leaving the commands anywhere else in the file passed (BG0497).
        """
        ref = (self.SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        missing = _controls_missing_from_in_flight_section(ref)
        self.assertIsNotNone(missing,
                             "the reference has no in-flight-control SECTION - only the reading "
                             "guide row that names one, which a deleted heading leaves standing")
        self.assertEqual(missing, [],
                         f"the in-flight-control section does not carry: {missing}")


class SprintInvocationBinderTests(unittest.TestCase):
    """The two binders the criteria above rest on, shown to DISCRIMINATE.

    Both were satisfied by anything: the invocation check read the bare verb word and never
    looked at a flag, and the reference check looked file-wide for a string the generated
    reading guide already carried. Each mutant below is applied to a COPY of the shipped file,
    so this is the criterion's own mutant executed rather than a shape asserted about it.
    """

    SKILL = Path(__file__).resolve().parents[1].parent

    def test_a_documented_flag_no_surface_owns_is_refused(self) -> None:
        """MUTANT: match the bare verb WORD instead of parsing the line.

        Five cases, because the check has to separate things a verb match cannot: a flag nothing
        owns (refused), a flag the parser owns (accepted), and a flag the slash surface declares
        as its own - accepted on the slash surface, because `--autonomous` names a mode the skill
        runs, and REFUSED on the script surface, because `sprint.py` does not run it. That last
        pair is the whole reason the exemption is scoped: applied to both surfaces it would
        document, as runnable, a script invocation that exits non-zero.
        """
        real = (self.SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        self.assertEqual([], _unparsable_invocations(_fenced_invocations(real)),
                         "the shipped page is already refused, so the controls below prove "
                         "nothing about the binder")
        skill_only = _skill_only_flags(_ARGUMENTS.read_text(encoding="utf-8"))
        self.assertIn("--autonomous", skill_only,
                      "help/arguments.md no longer declares the slash-only flag, so the binder "
                      "is exempting nothing and the page's own examples should now be refused")

        bad = ("slash", "--bugs Open --nonexistent-flag zzz")
        self.assertTrue(_unparsable_invocations([bad]),
                        "a documented flag owned by no parser and declared by no page was "
                        "accepted - the binder is reading the verb and stopping")
        self.assertTrue(_unparsable_invocations([("script", "review-batch --nope 1")]),
                        "a script-form flag no parser owns was accepted, so the script surface "
                        "is extracted but not parsed")
        self.assertEqual([], _unparsable_invocations([("slash", "--bugs Open")]),
                         "a real invocation was refused - the binder refuses everything")
        self.assertEqual([], _unparsable_invocations([("script", "batch drop US0001")]),
                         "a real script invocation was refused - the script surface is being "
                         "parsed as though it were the slash one")
        self.assertEqual([], _unparsable_invocations([("slash", "--bugs Open --autonomous")]),
                         "the declared slash-only flag was refused, so the binder models one "
                         "surface where there are two")
        self.assertTrue(_unparsable_invocations([("script", "plan --bugs Open --autonomous")]),
                        "the slash-only flag was excused on the SCRIPT surface, where the "
                        "parser owns no such flag - the exemption is unscoped, and the page "
                        "could document a script command that does not run")

    def test_moving_the_controls_out_of_their_section_is_refused(self) -> None:
        """MUTANT: look the invocations up file-wide, or match the anchor anywhere in the file.

        Two states are separated here that the file-wide lookup could not: the section GONE
        (only the generated reading-guide row still names it) and the section EMPTY with the
        commands moved elsewhere. Both used to pass.
        """
        real = (self.SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        self.assertEqual([], _controls_missing_from_in_flight_section(real),
                         "the shipped reference already fails, so the mutants below prove "
                         "nothing")
        self.assertIn("{#in-flight-controls}", real.split(_IN_FLIGHT_HEADING, 1)[0],
                      "the reading-guide row that made the old anchor check vacuous is gone, "
                      "so this mutant no longer reproduces the finding - restate it")

        gone = real.replace(_IN_FLIGHT_HEADING, "## In-flight controls")
        self.assertIsNone(_controls_missing_from_in_flight_section(gone),
                          "the named section was deleted and the check still found one - it is "
                          "matching the reading-guide row at the top of the file")

        head, body = real.split(_IN_FLIGHT_HEADING, 1)
        rest = re.split(r"\n## ", body, maxsplit=1)
        emptied = f"{head}{_IN_FLIGHT_HEADING}\n\nnothing here.\n\n## {rest[1]}\n{rest[0]}"
        self.assertEqual(
            sorted(_controls_missing_from_in_flight_section(emptied)),
            sorted(_IN_FLIGHT_CONTROLS),
            "the controls were moved out of the section and the check still found them, so it "
            "is looking file-wide rather than within the section body")


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


#: The heading whose body must name every recorded ledger key. Scoped rather than file-wide:
#: the criterion is about that SECTION, and a bare `\bat\b` matched the English around it.
_BATCH_LEDGER_HEADING = "### What a batch change puts on the record"


def _batch_change_keys() -> set[str]:
    """Every key the `batch_changes` writers actually put on the ledger, read by RUNNING them.

    EXECUTED, never scanned. This was `re.findall(r'"(action|id|reason|at|note)":', src)` over
    the whole `run_state` module - an alternation that names the answer in advance, so a key
    added to an entry was invisible to it and a key renamed away stayed in the set. Both mutants
    survived. A drop, an add with a reason, and a second add of the SAME unit are run against a
    throwaway run because between them they produce every branch of the two writers: the
    duplicate add is the only path that records `note`.
    """
    sys.path.insert(0, str(_SCRIPTS))
    from lib import run_state                       # noqa: PLC0415 - deferred sibling
    import json                                     # noqa: PLC0415
    import tempfile                                 # noqa: PLC0415
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({"run_id": "RUN-T", "batch": ["US0001"], "outcome": "running"}),
            encoding="utf-8")
        run_state.drop_from_batch(root, "US0001", reason="recorded, not silent")
        run_state.add_to_batch(root, "US0002", reason="joined late")
        state = run_state.add_to_batch(root, "US0002")
        entries = state.get("batch_changes") or []
    return {k for entry in entries for k in entry}


def _keys_unnamed_in_ledger_section(page: str, keys) -> list[str]:
    """The recorded keys the batch-mutation section never names, as a code span.

    A code span, not a bare word: `at` occurs in ordinary English all over the page, so a
    `\\bat\\b` match reported the key documented wherever the prose happened to use the word.
    """
    if _BATCH_LEDGER_HEADING not in page:
        return sorted(keys)          # no section at all names none of them
    body = page.split(_BATCH_LEDGER_HEADING, 1)[1]
    body = re.split(r"\n#{2,3} ", body, maxsplit=1)[0]
    return sorted(k for k in keys if f"`{k}`" not in body)


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

        The keys are read by EXECUTING the writers, so the page cannot drift from the ledger
        without this reddening. The previous version derived them from a hardcoded alternation
        over the module source, which named the answer in advance: adding `origin` to the drop
        entry survived, and renaming `note` to `remark` survived (BG0523).
        """
        keys = _batch_change_keys()
        self.assertTrue(keys, "no batch_changes keys were derived from run_state")
        page = self._page()
        self.assertEqual(_keys_unnamed_in_ledger_section(page, keys), [],
                         "the batch-mutation section never names these recorded ledger key(s)")
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

    def test_the_recorded_key_set_is_executed_and_an_unnamed_key_is_refused(self):
        """MUTANT: rename `note` to `remark` in `run_state.add_to_batch`, or add `origin` to the
        drop entry in `run_state.drop_from_batch`.

        Both survived the alternation this replaces, which is the whole of BG0523's first
        finding. Two halves, and each is needed: the derived set is asserted to be EXACTLY what
        the two writers put on a real ledger, so a renamed or added key moves it; and the
        section binder is asserted to refuse a key the section does not name, so the derivation
        being right is worth something.
        """
        self.assertEqual(_batch_change_keys(), {"action", "id", "reason", "at", "note"},
                         "the executed writers no longer record exactly these ledger keys - "
                         "update the page's batch-mutation section and this set together")
        self.assertEqual(
            _keys_unnamed_in_ledger_section(self._page(), _batch_change_keys() | {"origin"}),
            ["origin"],
            "a ledger key the batch-mutation section never names was not refused, so the "
            "binder passes whatever the writers record")

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
