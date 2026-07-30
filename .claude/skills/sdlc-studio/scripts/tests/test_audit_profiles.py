"""Tests for the audit lens-pack surface: the packs on disk and `--profile` resolution.

A profile is a declarative lens pack. These tests hold three things the packs
cannot hold for themselves: that each shipped pack declares real lenses, that
resolution refuses a name no pack declares (rather than running an empty lens
set), and that the security posture the repo pack inherited survives verbatim.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

audit = loader.load_script("readiness")

SKILL = Path(__file__).resolve().parent.parent.parent
PACKS = SKILL / "templates" / "audit-profiles"

# The remediation-only security posture, verbatim. It is the contract a finder agent
# is handed: it moved into the repo pack when the on-ramp script was retired, and this
# literal is what stops a later edit paraphrasing it away.
SECURITY_POSTURE = (
    "Security findings are remediation-only by design: report location, weakness "
    "class, realistic impact, and a concrete fix. Do not include proof-of-concept "
    "exploits or payloads. Never copy a secret value into any artefact; report a "
    "committed secret by its location plus rotation instructions, and leave the "
    "value where it is."
)


# The file-or-decline discipline, verbatim. The test pack's whole value is in its lenses
# being run and answered, so silence on a candidate is the failure mode to design against;
# this literal is what stops a later edit softening it into a suggestion.
FILE_OR_DECLINE = (
    "Every candidate that survives the refute panel is either filed through "
    "`file_finding.py` or declined with a stated reason. Silence on a candidate is "
    "not an outcome of this run."
)

#: Ids of the shipped lessons registry, i.e. the ids a pack citation may resolve to.
_LESSON_ROW_RE = re.compile(r"^\|\s*\[(LL\d{4})\]\(([^)]+)\)")
_LESSON_ID_RE = re.compile(r"LL\d{4}")


def _registry_lessons() -> dict[str, str]:
    """`{LL id: filename}` for every lesson the shipped registry lists."""
    index = SKILL / "lessons" / "_index.md"
    out: dict[str, str] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        m = _LESSON_ROW_RE.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def _run_cli(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SKILL / "scripts" / "readiness.py"), *argv],
                          capture_output=True, text=True)


class RepoProfileLensTests(unittest.TestCase):
    """The repo pack: three legs, declarative, with the security posture intact."""

    def setUp(self) -> None:
        self.pack = PACKS / "repo.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/repo.md is missing")
        self.parsed = audit.parse_pack(self.pack)

    def test_repo_pack_declares_the_three_legs(self) -> None:
        names = sorted(lens["name"] for lens in self.parsed["lenses"])
        self.assertEqual(names, ["architecture", "code-quality", "defensive-security"])

    def test_every_repo_lens_carries_a_question_and_what_it_hunts(self) -> None:
        for lens in self.parsed["lenses"]:
            self.assertTrue(lens["question"].strip(),
                            f"{lens['name']}: no adversarial question")
            self.assertTrue(lens["hunts"].strip(),
                            f"{lens['name']}: nothing declared as hunted")
            self.assertIn("?", lens["question"],
                          f"{lens['name']}: the adversarial question is not a question")

    def test_repo_pack_uses_the_same_declarative_shape_as_the_skill_pack(self) -> None:
        skill_pack = audit.parse_pack(PACKS / "skill.md")
        self.assertEqual(self.parsed["columns"], skill_pack["columns"])

    def test_repo_pack_carries_the_remediation_only_posture_verbatim(self) -> None:
        # Whitespace is re-wrapped in markdown, so compare on collapsed whitespace.
        body = " ".join(self.pack.read_text(encoding="utf-8").split())
        self.assertIn(" ".join(SECURITY_POSTURE.split()), body)

    def test_repo_pack_declares_the_shared_refute_panel(self) -> None:
        self.assertEqual(self.parsed["threshold"], {"survive": 2, "votes": 3})


class ProfileResolveTests(unittest.TestCase):
    """`--profile <name>` resolves to a pack, or refuses loudly."""

    def test_repo_resolves_to_its_pack(self) -> None:
        got = audit.resolve_profile("repo")
        self.assertEqual(got["source"], "templates/audit-profiles/repo.md")
        self.assertEqual(len(got["lenses"]), 3)
        self.assertEqual(got["threshold"], {"survive": 2, "votes": 3})

    def test_an_unknown_name_raises_rather_than_yielding_an_empty_lens_set(self) -> None:
        with self.assertRaises(audit.UnknownProfile) as ctx:
            audit.resolve_profile("no-such-pack")
        self.assertIn("repo", str(ctx.exception))
        self.assertIn("skill", str(ctx.exception))

    def test_an_unknown_name_exits_non_zero_naming_the_packs_that_exist(self) -> None:
        proc = _run_cli("profile", "--name", "no-such-pack")
        self.assertNotEqual(proc.returncode, 0, "an unknown profile exited 0")
        message = proc.stderr + proc.stdout
        for name in audit.profile_names():
            self.assertIn(name, message, f"the refusal never named the {name} pack")

    def test_the_cli_reports_the_lenses_and_the_refute_threshold(self) -> None:
        proc = _run_cli("profile", "--name", "repo")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for lens in ("architecture", "code-quality", "defensive-security"):
            self.assertIn(lens, proc.stdout)
        self.assertIn("2 of 3", proc.stdout)

    def test_every_shipped_pack_resolves(self) -> None:
        names = audit.profile_names()
        self.assertIn("repo", names)
        for name in names:
            got = audit.resolve_profile(name)
            self.assertTrue(got["lenses"], f"{name} resolved to an empty lens set")


class CodeProfileLensTests(unittest.TestCase):
    """The code pack: code-level lenses for auditing an implementation."""

    #: The lenses the code profile was promised: correctness, security smells,
    #: pattern violations, and drift between an AC and what was built.
    EXPECTED = ["ac-drift", "correctness", "pattern-violations", "security-smells"]

    def setUp(self) -> None:
        self.pack = PACKS / "code.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/code.md is missing")
        self.parsed = audit.parse_pack(self.pack)

    def test_code_pack_declares_its_code_level_lenses(self) -> None:
        self.assertEqual(sorted(lens["name"] for lens in self.parsed["lenses"]), self.EXPECTED)

    def test_every_code_lens_carries_a_question_and_what_it_hunts(self) -> None:
        for lens in self.parsed["lenses"]:
            self.assertIn("?", lens["question"],
                          f"{lens['name']}: the adversarial question is not a question")
            self.assertTrue(lens["hunts"].strip(),
                            f"{lens['name']}: nothing declared as hunted")

    def test_code_pack_uses_the_same_declarative_shape_as_the_skill_pack(self) -> None:
        self.assertEqual(self.parsed["columns"], audit.parse_pack(PACKS / "skill.md")["columns"])

    def test_code_profile_resolves(self) -> None:
        got = audit.resolve_profile("code")
        self.assertEqual(got["source"], "templates/audit-profiles/code.md")
        self.assertEqual(len(got["lenses"]), len(self.EXPECTED))


class TestProfileTests(unittest.TestCase):
    """The `test` pack as a surface: it resolves, it is panel-wired, it refuses to run
    empty, and it hands the finder the file-or-decline discipline.

    A mutant cannot detect a docstring that lies, so this profile's value is entirely in
    its lenses being run at all. The failure to design against is therefore a `test` run
    reporting a clean audit having examined nothing.
    """

    def setUp(self) -> None:
        self.pack = PACKS / "test.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/test.md is missing")

    def test_test_profile_is_listed_and_resolves_to_its_pack(self) -> None:
        listed = _run_cli("profile", "--list", "--format", "json")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("test", json.loads(listed.stdout)["profiles"])
        proc = _run_cli("profile", "--name", "test")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("profile test -> templates/audit-profiles/test.md", proc.stdout)
        count = re.search(r"lenses: (\d+)", proc.stdout)
        self.assertIsNotNone(count, "the resolve output reported no lens count")
        self.assertGreater(int(count.group(1)), 0, "the pack resolved to zero lenses")

    def test_test_pack_declares_the_shared_refute_threshold(self) -> None:
        got = audit.resolve_profile("test")
        self.assertEqual(got["threshold"], {"survive": 2, "votes": 3})
        self.assertIn("does not opt out", got["refute"],
                      "the pack never states that it is panel-wired")

    def test_a_lensless_test_pack_is_refused_rather_than_run(self) -> None:
        """A pack whose lens table is emptied by a later edit is refused, not run clean."""
        with tempfile.TemporaryDirectory() as td:
            fixture = Path(td)
            packs = fixture / "templates" / "audit-profiles"
            packs.mkdir(parents=True)
            gutted = "\n".join(line for line in self.pack.read_text(encoding="utf-8").splitlines()
                               if not line.startswith("|"))
            (packs / "test.md").write_text(gutted, encoding="utf-8")
            with self.assertRaises(audit.UnknownProfile) as ctx:
                audit.resolve_profile("test", fixture)
            self.assertIn("test", str(ctx.exception))
            self.assertIn("templates/audit-profiles/test.md", str(ctx.exception))

            err = io.StringIO()
            with mock.patch.object(audit, "SKILL_DIR", fixture), \
                    mock.patch.object(audit, "PROFILE_DIR", packs), \
                    contextlib.redirect_stderr(err):
                rc = audit.main(["profile", "--name", "test"])
        self.assertNotEqual(rc, 0, "a lens-less pack exited 0, i.e. reported a clean audit")
        self.assertIn("declares no lens", err.getvalue())

    def test_the_pack_states_file_or_decline(self) -> None:
        # Whitespace is re-wrapped in markdown, so compare on collapsed whitespace.
        body = " ".join(self.pack.read_text(encoding="utf-8").split())
        self.assertIn(" ".join(FILE_OR_DECLINE.split()), body)


class TestProfileLensTests(unittest.TestCase):
    """The `test` pack's content: four lenses, each anchored to a recorded failure mode.

    A lens appended without a citation is a lens invented from first principles, and a
    citation that no longer resolves is a dangling reference; the pack is where either
    would go unnoticed.
    """

    #: The four failure classes the profile was adopted for.
    EXPECTED = ["can-it-fail", "docstring-vs-assertion", "incidentally-green",
                "reaches-the-code"]

    def setUp(self) -> None:
        self.pack = PACKS / "test.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/test.md is missing")
        self.parsed = audit.parse_pack(self.pack)

    def test_the_four_lenses_are_declared_with_question_and_hunts(self) -> None:
        self.assertEqual(sorted(lens["name"] for lens in self.parsed["lenses"]), self.EXPECTED)
        for lens in self.parsed["lenses"]:
            self.assertIn("?", lens["question"],
                          f"{lens['name']}: the adversarial question is not a question")
            self.assertTrue(lens["hunts"].strip(),
                            f"{lens['name']}: nothing declared as hunted")

    def test_every_lens_cites_a_lesson_id_that_resolves(self) -> None:
        registry = _registry_lessons()
        self.assertTrue(registry, "the shipped lessons registry parsed as empty")
        for lens in self.parsed["lenses"]:
            cited = _LESSON_ID_RE.findall(lens.get("drawn_from", ""))
            self.assertTrue(cited, f"{lens['name']}: no recorded failure mode cited")
            for lesson in cited:
                self.assertIn(lesson, registry,
                              f"{lens['name']} cites {lesson}, which the registry does not list")
                self.assertTrue((SKILL / "lessons" / registry[lesson]).is_file(),
                                f"{lesson} is listed but its file is missing")


def _catalogued(path: Path, heading: str) -> set[str]:
    """Profile names a catalogue table lists, read from the first column of the first
    table under `heading`. Names are backticked so a prose mention cannot pass as a row."""
    text = path.read_text(encoding="utf-8")
    if heading not in text:
        return set()
    body = text.split(heading, 1)[1]
    names: set[str] = set()
    seen_table = False
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if seen_table and names:
                break
            continue
        seen_table = True
        first = audit._split_row(stripped)[0]
        m = re.match(r"`([a-z-]+)`", first)
        if m:
            names.add(m.group(1))
    return names


class ProfileCommandOutputTests(unittest.TestCase):
    """`audit profile`'s own output branches (BG0212).

    A full mutation enumeration over `readiness.py` left six survivors inside `cmd_profile`:
    the list-versus-resolve split, the text-versus-JSON split, and the threshold line. The
    resolution logic beneath was well covered; nothing asserted what the COMMAND prints, so
    every print branch could be rewritten without a test noticing.
    """

    def test_list_text_names_every_profile(self) -> None:
        proc = _run_cli("profile", "--list")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("audit profiles:", proc.stdout)
        for name in audit.profile_names():
            self.assertIn(name, proc.stdout)

    def test_list_json_is_parseable_and_complete(self) -> None:
        # The JSON branch is a separate `print`; a mutant swapping it for the text form
        # survived because nothing parsed the output.
        proc = _run_cli("profile", "--list", "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(sorted(payload["profiles"]), sorted(audit.profile_names()))

    def test_resolve_json_carries_the_lenses_and_threshold(self) -> None:
        proc = _run_cli("profile", "--name", "repo", "--format", "json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["name"], "repo")
        self.assertTrue(payload["lenses"])
        self.assertEqual(payload["threshold"], {"survive": 2, "votes": 3})

    def test_resolve_text_reports_the_source_and_lens_count(self) -> None:
        proc = _run_cli("profile", "--name", "repo")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("profile repo -> ", proc.stdout)
        self.assertIn(f"lenses: {len(audit.resolve_profile('repo')['lenses'])}", proc.stdout)

    def test_a_pack_without_a_threshold_says_so_rather_than_printing_a_count(self) -> None:
        # The threshold line has two branches and only the declared one was exercised.
        self.assertIsNone(audit._parse_threshold("# Pack\n\nno panel here\n"))

    def test_no_name_and_no_list_still_lists(self) -> None:
        # `args.list or not args.name` - the second half was unpinned, so a bare
        # `audit profile` could have started erroring without a test noticing.
        proc = _run_cli("profile")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("audit profiles:", proc.stdout)


class ProfileParserEdgeTests(unittest.TestCase):
    """The not-found paths of the profile parsers.

    Every shipped pack declares a refute panel and every reference profile resolves, so
    the happy path is covered many times over and the absent paths are covered nowhere -
    a mutation run over this surface finds them by stubbing each `return ""` and watching
    nothing fail. These are the tests that make the empty answers mean something.
    """

    def test_a_pack_with_no_refute_declaration_reads_as_empty(self) -> None:
        # The empty string is the signal `resolve_profile` checks to report a pack as not
        # panel-wired. Stubbed to return None, nothing here failed.
        self.assertEqual(audit._refute_declaration("# Pack\n\nNo panel here.\n"), "")

    def test_a_refute_declaration_wrapped_across_lines_is_read_whole(self) -> None:
        # The block join is the reason this is not a one-line regex; without a case that
        # actually wraps, the continuation loop is decoration.
        text = ("# Pack\n\n> **Refute panel:** three votes, two must survive, and this\n"
                "> pack does not opt out of it.\n")
        got = audit._refute_declaration(text)
        self.assertIn("does not opt out", got)
        self.assertNotIn("\n", got)

    def test_a_missing_anchor_yields_an_empty_section(self) -> None:
        self.assertEqual(
            audit._reference_section(SKILL, "reference-audit.md", "no-such-anchor-here"), "")

    def test_a_section_keeps_deeper_headings_and_stops_at_a_sibling(self) -> None:
        """The `<= level` rule, which every real caller happens not to exercise.

        A profile's lens table sits under `###` subheadings inside its `##` section, so
        stopping at ANY heading would truncate the table, and stopping at none would run
        the next profile's lenses into this one. Both mutants survived against the shipped
        references because their sections happen to have no deeper headings before the end.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "ref.md").write_text(
                "# Title\n\n"
                "## Wanted {#wanted}\n"
                "alpha\n"
                "### Deeper\n"
                "beta\n"
                "## Sibling {#sibling}\n"
                "gamma\n", encoding="utf-8")
            body = audit._reference_section(root, "ref.md", "wanted")
        self.assertIn("alpha", body)
        self.assertIn("### Deeper", body, "a DEEPER heading is part of the section")
        self.assertIn("beta", body)
        self.assertNotIn("gamma", body, "a SIBLING heading ends the section")

    def test_the_anchor_guard_selects_the_named_section_not_the_first(self) -> None:
        # `line.startswith("#") AND the anchor is present` - inverting or dropping either
        # half survived, because every other caller passes an anchor that happens to sit
        # in the first matching heading anyway.
        body = audit._reference_section(SKILL, "reference-audit.md", "audit-profiles")
        self.assertTrue(body.strip(), "the known-good anchor must still resolve")
        self.assertNotIn("{#audit-profiles}", body, "the heading itself is not part of the body")


class ProfileCatalogueTests(unittest.TestCase):
    """Every profile that exists is catalogued in both places, and none opts out
    of the shared refute panel."""

    REFERENCE = SKILL / "reference-audit.md"
    HELP = SKILL / "help" / "audit.md"

    def test_the_reference_catalogue_matches_the_profiles_that_exist(self) -> None:
        self.assertEqual(_catalogued(self.REFERENCE, "## Lens Profiles {#audit-profiles}"),
                         set(audit.profile_names()))

    def test_the_help_catalogue_matches_the_profiles_that_exist(self) -> None:
        self.assertEqual(_catalogued(self.HELP, "## Profiles"), set(audit.profile_names()))

    def test_every_promised_profile_is_present(self) -> None:
        self.assertEqual(set(audit.profile_names()),
                         {"project", "skill", "repo", "code", "test", "process"})

    def test_no_profile_opts_out_of_the_shared_refute_panel(self) -> None:
        for name in audit.profile_names():
            got = audit.resolve_profile(name)
            self.assertEqual(got["threshold"], {"survive": 2, "votes": 3},
                             f"{name} does not declare the shared refute threshold")
            self.assertIn("does not opt out", got["refute"] + " " + got["source"],
                          f"{name} never states that it is panel-wired")


REPO_ROOT = SKILL.parent.parent.parent  # the repo the skill tree sits inside

#: Any artefact id (a bug, CR, RFC, story, epic, run, ...) or a project-local `L-` lesson.
#: These open nothing in a consuming project, so a shipped pack must not cite them.
_ANY_CITED_RE = re.compile(
    r"LL\d{4}|L-\d+|(?:BG|CR|RFC|US|EP|RV|RETRO|HO)\d{3,}|RUN-[0-9A-Z]{6,}|D\d{4}")


def _provenance_violations(lenses: list[dict], registry: dict[str, str]) -> list[str]:
    """`"<lens>: <id>"` for every provenance token a consuming project could not resolve.

    A pack ships, so a citation is valid only when it is a shipped `LL` id the registry
    lists. A project-local `L-<n>` lesson, or any artefact id, is a dangling reference
    outside this repo and is reported, named against its lens.
    """
    out: list[str] = []
    for lens in lenses:
        for tok in _ANY_CITED_RE.findall(lens.get("drawn_from", "")):
            if not (re.fullmatch(r"LL\d{4}", tok) and tok in registry):
                out.append(f"{lens['name']}: {tok}")
    return out


class ProcessProfileTests(unittest.TestCase):
    """The `process` pack as a surface (US0340): it resolves, it is catalogued everywhere,
    it is panel-wired and hands the finder the file-or-decline discipline, and an emptied
    pack is refused rather than reported clean."""

    def setUp(self) -> None:
        self.pack = PACKS / "process.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/process.md is missing")

    def test_the_process_profile_resolves_and_is_catalogued_wherever_profiles_are_listed(self) -> None:
        got = audit.resolve_profile("process")
        self.assertEqual(got["source"], "templates/audit-profiles/process.md")
        self.assertTrue(got["lenses"], "the process pack resolved to an empty lens set")
        self.assertIn("process", audit.profile_names())
        reference = _catalogued(SKILL / "reference-audit.md", "## Lens Profiles {#audit-profiles}")
        help_ = _catalogued(SKILL / "help" / "audit.md", "## Profiles")
        self.assertIn("process", reference, "the reference catalogue never lists the process pack")
        self.assertIn("process", help_, "the help catalogue never lists the process pack")

    def test_the_process_pack_is_panel_wired_and_states_file_or_decline(self) -> None:
        got = audit.resolve_profile("process")
        self.assertEqual(got["threshold"], {"survive": 2, "votes": 3})
        self.assertIn("does not opt out", got["refute"],
                      "the pack never states that it is panel-wired")
        body = " ".join(self.pack.read_text(encoding="utf-8").split())
        self.assertIn(" ".join(FILE_OR_DECLINE.split()), body,
                      "the pack never carries the file-or-decline discipline verbatim")

    def test_a_lensless_process_pack_is_refused_rather_than_run(self) -> None:
        """A pack whose lens table is emptied by a later edit is refused, not run clean."""
        with tempfile.TemporaryDirectory() as td:
            fixture = Path(td)
            packs = fixture / "templates" / "audit-profiles"
            packs.mkdir(parents=True)
            gutted = "\n".join(line for line in self.pack.read_text(encoding="utf-8").splitlines()
                               if not line.startswith("|"))
            (packs / "process.md").write_text(gutted, encoding="utf-8")
            with self.assertRaises(audit.UnknownProfile) as ctx:
                audit.resolve_profile("process", fixture)
            self.assertIn("process", str(ctx.exception))
            self.assertIn("templates/audit-profiles/process.md", str(ctx.exception))

            err = io.StringIO()
            with mock.patch.object(audit, "SKILL_DIR", fixture), \
                    mock.patch.object(audit, "PROFILE_DIR", packs), \
                    contextlib.redirect_stderr(err):
                rc = audit.main(["profile", "--name", "process"])
        self.assertNotEqual(rc, 0, "a lens-less pack exited 0, i.e. reported a clean audit")
        self.assertIn("declares no lens", err.getvalue())


class ProcessProfileLensTests(unittest.TestCase):
    """The process pack's lenses (US0340 AC2): declarative, in the same shape as its
    siblings, every one carrying a question and what it hunts."""

    #: The five failure classes the process pack was adopted for.
    EXPECTED = ["accepted-without-running", "count-by-hand", "path-from-memory",
                "repair-without-plan", "skipped-preflight"]

    def setUp(self) -> None:
        self.pack = PACKS / "process.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/process.md is missing")
        self.parsed = audit.parse_pack(self.pack)

    def test_every_process_lens_declares_a_question_and_what_it_hunts(self) -> None:
        self.assertEqual(sorted(lens["name"] for lens in self.parsed["lenses"]), self.EXPECTED)
        for lens in self.parsed["lenses"]:
            self.assertIn("?", lens["question"],
                          f"{lens['name']}: the adversarial question is not a question")
            self.assertTrue(lens["hunts"].strip(),
                            f"{lens['name']}: nothing declared as hunted")
        # A finder handed this pack gets the same fields as any other. Asserted against THIS
        # pack's own headers, not by subtracting a sibling pack's column count: deriving the
        # expected shape from `test.md` coupled the two files, so `test.md` gaining a Signature
        # column of its own reddened this assertion for a reason it is not about. Every pack now
        # carries Signature, and each is held to its own header list.
        self.assertEqual(["Lens", "Adversarial question", "Hunts for", "Drawn from", "Signature"],
                         self.parsed["columns"])


class ProcessLensSignatureTests(unittest.TestCase):
    """Each lens names its signature (US0341): the parser carries it as its own field, a
    lens with no mechanical signature declares the absence with its reason, and a
    mechanical one names a documented detector and paths that are actually on disk."""

    def setUp(self) -> None:
        self.pack = PACKS / "process.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/process.md is missing")
        self.parsed = audit.parse_pack(self.pack)

    def test_every_process_lens_declares_a_signature_the_parser_carries(self) -> None:
        for lens in self.parsed["lenses"]:
            self.assertTrue(lens["signature"].strip(),
                            f"{lens['name']}: no signature - the column is blank or dropped")
            # Distinct from the two cells beside it, so a signature is not just a copy of
            # what it hunts or where it was drawn from.
            self.assertNotEqual(lens["signature"], lens["hunts"], lens["name"])
            self.assertNotEqual(lens["signature"], lens["drawn_from"], lens["name"])

    def test_a_lens_with_no_mechanical_signature_declares_it_and_gives_a_reason(self) -> None:
        absent = [lens for lens in self.parsed["lenses"] if not lens["mechanical"]]
        self.assertTrue(absent, "no lens declares an absent signature, so this bar is untested")
        for lens in absent:
            sig = lens["signature"].strip()
            self.assertTrue(sig.startswith(f"{audit.SIGNATURE_ABSENT} - "),
                            f"{lens['name']}: an absent signature must use the fixed "
                            f"'{audit.SIGNATURE_ABSENT} - <reason>' form, not {sig!r}")
            reason = sig[len(f"{audit.SIGNATURE_ABSENT} - "):].strip()
            self.assertGreater(len(reason), 20,
                               f"{lens['name']}: a dash or empty reason is not a declared absence")
            self.assertFalse(lens["mechanical"],
                             f"{lens['name']}: an absent signature parsed as mechanical")

    def test_every_mechanical_signature_names_a_detector_and_paths_that_exist(self) -> None:
        mechanical = [lens for lens in self.parsed["lenses"] if lens["mechanical"]]
        self.assertTrue(mechanical, "no lens ships a mechanical signature")
        for lens in mechanical:
            tokens = lens["signature"].split()
            self.assertIn(tokens[0], audit.SIGNATURE_DETECTORS,
                          f"{lens['name']}: {tokens[0]!r} is not a documented detector")
            paths = [t for t in tokens if "/" in t]
            self.assertTrue(paths, f"{lens['name']}: a mechanical signature names no path to run")
            for p in paths:
                self.assertTrue((REPO_ROOT / p).exists(),
                                f"{lens['name']}: signature names {p}, which is not on disk")


class ProcessLensProvenanceTests(unittest.TestCase):
    """Every lens cites the incident it derives from (US0342): a shipped lesson id that
    resolves, and never a project-local or artefact id a consuming project cannot open."""

    def setUp(self) -> None:
        self.pack = PACKS / "process.md"
        self.assertTrue(self.pack.is_file(), "templates/audit-profiles/process.md is missing")
        self.parsed = audit.parse_pack(self.pack)
        self.registry = _registry_lessons()
        self.assertTrue(self.registry, "the shipped lessons registry parsed as empty")

    def test_every_process_lens_cites_a_lesson_that_resolves(self) -> None:
        for lens in self.parsed["lenses"]:
            cited = _LESSON_ID_RE.findall(lens.get("drawn_from", ""))
            self.assertTrue(cited, f"{lens['name']}: no recorded incident cited")
            for lesson in cited:
                self.assertIn(lesson, self.registry,
                              f"{lens['name']} cites {lesson}, which the registry does not list")
                self.assertTrue((SKILL / "lessons" / self.registry[lesson]).is_file(),
                                f"{lesson} is listed but its file is missing")

    def test_a_project_local_or_artefact_id_is_refused_as_provenance(self) -> None:
        # The shipped pack cites only ids a consuming project can open.
        self.assertEqual(_provenance_violations(self.parsed["lenses"], self.registry), [],
                         "the shipped process pack cites an id no consuming project could resolve")
        # And the check has teeth: a project-local lesson and an artefact id are both caught,
        # each named against its lens. Without this, an appended `L-` or `BG` citation would
        # ship as a dangling reference.
        polluted = [
            {"name": "borrowed-local", "drawn_from": "L-0003"},
            {"name": "borrowed-bug", "drawn_from": "LL0046, BG0256"},
        ]
        violations = _provenance_violations(polluted, self.registry)
        self.assertIn("borrowed-local: L-0003", violations)
        self.assertIn("borrowed-bug: BG0256", violations)
        self.assertNotIn("borrowed-bug: LL0046", violations,
                         "a resolving LL id beside a bad one must still pass")




# ---------------------------------------------------------------------------
# US0464: every lens names its detector, read by header name, across every runner shipped
# ---------------------------------------------------------------------------

def _pack(signature_col: str, rows: list[str], drawn_from: bool = False) -> str:
    """A pack file whose lens table has Signature LAST, with or without a Drawn from column."""
    head = "| Lens | Adversarial question | Hunts for |"
    if drawn_from:
        head += " Drawn from |"
    head += f" {signature_col} |"
    divider = "| " + " | ".join(["---"] * (len(head.split("|")) - 2)) + " |"
    body = "\n".join(rows)
    return f"# Pack\n\n## Lenses\n\n{head}\n{divider}\n{body}\n"


def _skill_fixture(packs: dict[str, str]):
    """A temp skill dir holding `{name: pack text}`, as (dir, cleanup)."""
    d = Path(tempfile.mkdtemp(prefix="packs_"))
    (d / "templates" / "audit-profiles").mkdir(parents=True)
    for name, text in packs.items():
        (d / "templates" / "audit-profiles" / f"{name}.md").write_text(text, encoding="utf-8")
    return d


class SignatureColumnTests(unittest.TestCase):
    """AC1: the signature column is resolved by header name, not position."""

    def test_the_signature_column_is_resolved_by_header_name(self) -> None:
        """MUTANTS. (1) Revert to `signature = cells[4] if len(cells) > 4 else ""`. Dies ONLY on a
        FOUR-column pack whose Signature is fourth with no `Drawn from` - on a five-column pack the
        positional and by-name reads agree, so a corpus-only assertion survives it. (2) Build the
        header map from the DIVIDER row instead of the header row: every by-name read then returns
        "", which is indistinguishable from the positional read unless `drawn_from` is asserted to
        be empty as well as `signature` being asserted non-empty.
        """
        four_col = _pack("Signature",
                         ["| alpha | q | h | python3 tools/check_links.py |"])
        _, lenses = audit._parse_lens_table(four_col.splitlines())
        self.assertEqual("python3 tools/check_links.py", lenses[0]["signature"],
                         "a four-column pack's Signature was not read by header name - this is "
                         "exactly what cells[4] drops")
        self.assertEqual("", lenses[0]["drawn_from"],
                         "the Signature leaked into drawn_from, so the map is built from the "
                         "wrong row")
        self.assertTrue(lenses[0]["mechanical"])

        five_col = _pack("Signature",
                         ["| beta | q | h | LL0001 | python3 tools/check_links.py |"],
                         drawn_from=True)
        _, five = audit._parse_lens_table(five_col.splitlines())
        self.assertEqual("python3 tools/check_links.py", five[0]["signature"])
        self.assertEqual("LL0001", five[0]["drawn_from"],
                         "the five-column shape lost its provenance column")

    def test_the_shipped_packs_span_three_shapes_and_all_parse(self) -> None:
        """The real corpus, because a fixture-only test cannot see a pack that ships mis-parsed.
        `code`/`repo`/`skill` are four-column (Signature fourth, no Drawn from) and would every
        one read as non-mechanical under the positional read."""
        widths = {}
        for name in sorted(set(audit.profile_names()) - set(audit.REFERENCE_PROFILES)):
            p = audit.resolve_profile(name)
            widths[name] = len(p["columns"])
            for lens in p["lenses"]:
                self.assertTrue(lens["signature"],
                                f"{name}/{lens['name']} parsed with an empty signature")
        self.assertIn(4, widths.values(), "no four-column pack ships, so AC1's real case is "
                                          "exercised only by a fixture")
        self.assertIn(5, widths.values(), "no five-column pack ships")


class SignatureDetectorSetTests(unittest.TestCase):
    """AC2: the detector set covers the runners this repo actually ships."""

    def test_every_shipped_runner_shape_classifies_as_mechanical_and_yields_its_path(self) -> None:
        """MUTANTS. (1) Delete ANY single runner from `SIGNATURE_DETECTORS` - caught only by one
        assertion per runner, never by `all(mechanical)` over the corpus. (2) Return the first
        token after the runner unconditionally: `npm run lint:links` then yields `run` and
        `rg pat path` yields `pat`, so the extracted VALUE is asserted, not merely that a
        resolution check passed. (3) Drop the `npm run` two-token rule so a bare `npm` passes.
        """
        cases = [
            ("python3 tools/check_links.py", "path", "tools/check_links.py"),
            ("bash tools/lint-style.sh", "path", "tools/lint-style.sh"),
            ("rg -ni \"two words\" tools", "path", "tools"),
            ("npm run lint:links", "npm-script", "lint:links"),
        ]
        for signature, kind, value in cases:
            with self.subTest(signature=signature):
                self.assertTrue(audit._signature_is_mechanical(signature),
                                f"{signature!r} is a runner this repo ships and read as "
                                f"non-mechanical")
                self.assertEqual((kind, value), audit.signature_target(signature),
                                 "the extracted target is wrong, which a mere 'it resolved' "
                                 "assertion would not catch")

    def test_a_bare_npm_and_a_manual_reason_naming_a_runner_are_both_non_mechanical(self) -> None:
        """MUTANT: `tokens[0] in SIGNATURE_DETECTORS` widened to `any(t in ... for t in tokens)`.
        Dies ONLY on a `manual` reason that MENTIONS a detector token mid-sentence, so the
        fixture deliberately contains one. `npm` alone dies to the two-token rule.
        """
        mentions = ("manual - no python3 script over the tree can tell a deliberate bound from "
                    "a mistaken one")
        self.assertFalse(audit._signature_is_mechanical(mentions),
                         "a manual reason mentioning `python3` read as mechanical, so the "
                         "leading-token rule was widened to any-token")
        self.assertIsNone(audit.signature_target(mentions))
        self.assertFalse(audit._signature_is_mechanical("npm"),
                         "a bare `npm` runs nothing and read as mechanical")
        self.assertFalse(audit._signature_is_mechanical("npm ci"))

    def test_a_quoted_pattern_is_one_token_so_a_pattern_is_never_mistaken_for_a_path(self) -> None:
        """MUTANT: `shlex.split` reverted to `str.split`.

        The FIRST fixture here does not discriminate and is kept only as a regression: with the
        path last, `rest[-1]` yields `tools` whether or not quoting is honoured, so a mutation run
        reported this SURVIVED. The case that discriminates is a quoted pattern with NO path -
        `shlex` correctly reports no target, while `str.split` invents `words"` as one and the
        refusal then blames a missing file instead of a missing path.
        """
        self.assertEqual(("path", "tools"),
                         audit.signature_target('rg -n "two words" tools'))

        self.assertEqual(("path", ""), audit.signature_target('rg -n "two words"'),
                         "a quoted pattern was split, so a fragment of it was taken as the path")
        lens = {"name": "x", "signature": 'rg -n "two words"', "mechanical": True}
        errors = audit.signature_errors(lens, SKILL.parents[2])
        self.assertIn("must end with the path", errors[0],
                      "the refusal blames a missing file rather than a missing path, so the "
                      "pattern was mistaken for one")

    def test_an_rg_signature_naming_no_path_is_refused_rather_than_reported(self) -> None:
        """The third-state decision, pinned. `rg <pattern>` with no path cannot be resolved, so
        it must FAIL the contract rather than pass as mechanical-but-unresolvable: a state that
        is reported and not enforced is the class this repo keeps finding.
        """
        lens = {"name": "x", "signature": "rg -n pattern", "mechanical": True}
        errors = audit.signature_errors(lens, SKILL.parents[2])
        self.assertTrue(errors, "an rg signature naming no path was accepted")
        self.assertIn("must end with the path", errors[0])


class SignatureCoverageTests(unittest.TestCase):
    """AC3/AC4/AC5: every lens carries a signature; mechanical resolves; absent is declared."""

    ROOT = SKILL.parents[2]

    def test_every_lens_of_every_pack_file_carries_a_signature(self) -> None:
        """AC3, over the resolver's OWN list (`profile_names()` minus `REFERENCE_PROFILES`) so a
        pack added later is held without anyone editing this test."""
        names = sorted(set(audit.profile_names()) - set(audit.REFERENCE_PROFILES))
        self.assertTrue(names)
        for name in names:
            for lens in audit.resolve_profile(name)["lenses"]:
                with self.subTest(pack=name, lens=lens["name"]):
                    self.assertTrue(lens["signature"].strip(),
                                    "ships with an empty Signature cell")

    def test_a_pack_added_later_is_held_without_this_test_being_edited(self) -> None:
        """MUTANT: replace the derived list with the five literal pack names. AC3's claim that a
        later pack is held is otherwise UNTESTED - the assertion above passes either way, because
        the five names and the derived list are the same set today. Caught only by dropping a NEW
        pack into a fixture skill dir.
        """
        fixture = _skill_fixture({"latecomer": _pack("Signature", ["| newlens | q | h |  |"])})
        self.addCleanup(shutil.rmtree, fixture, ignore_errors=True)
        with mock.patch.object(audit, "SKILL_DIR", fixture), \
             mock.patch.object(audit, "PROFILE_DIR", fixture / "templates" / "audit-profiles"):
            self.assertIn("latecomer", audit.profile_names(),
                          "a pack on disk was not discovered by the resolver")
            args = argparse.Namespace(name=None, list=False, validate=True, format="text",
                                      root=str(self.ROOT))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                rc = audit.cmd_validate_profiles(args)
        self.assertEqual(1, rc, "a newly added pack with a blank signature was not refused")
        self.assertIn("newlens", err.getvalue())

    def test_every_mechanical_signature_names_a_path_on_disk(self) -> None:
        """AC4, against the live tree: a detector written from memory is caught here."""
        for name in sorted(set(audit.profile_names()) - set(audit.REFERENCE_PROFILES)):
            for lens in audit.resolve_profile(name)["lenses"]:
                if not lens["mechanical"]:
                    continue
                kind, value = audit.signature_target(lens["signature"])
                with self.subTest(pack=name, lens=lens["name"], kind=kind):
                    self.assertTrue(value, "a mechanical signature names no target")
                    if kind == "npm-script":
                        self.assertIn(value, audit._npm_scripts(self.ROOT),
                                      "names no key in package.json's `scripts`")
                    else:
                        self.assertTrue((self.ROOT / value).exists(),
                                        f"{value!r} is not on disk")

    def test_the_npm_script_is_looked_up_in_scripts_not_the_whole_document(self) -> None:
        """MUTANT: look the key up across the whole `package.json` rather than in its `scripts`
        object. Dies only on a colliding TOP-LEVEL key, so the fixture uses `name` - which every
        package.json has and no `npm run` can invoke.
        """
        d = Path(tempfile.mkdtemp(prefix="npmpack_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "package.json").write_text(
            json.dumps({"name": "sdlc-studio", "scripts": {"lint:real": "echo ok"}}),
            encoding="utf-8")
        self.assertEqual({"lint:real": "echo ok"}, audit._npm_scripts(d))
        lens = {"name": "x", "signature": "npm run name", "mechanical": True}
        errors = audit.signature_errors(lens, d)
        self.assertTrue(errors, "`npm run name` resolved against a top-level key, which "
                                "`npm run` cannot invoke")
        self.assertIn("scripts", errors[0])

    def test_a_non_mechanical_signature_uses_the_manual_form_with_a_reason(self) -> None:
        """AC5, plus the two negative cases it names. MUTANTS: (1) drop the reason requirement so
        a bare `manual` passes; (2) `"manual" in cell` instead of the LEADING token, which a
        `- manual` or `see the manual` cell then satisfies.
        """
        root = self.ROOT
        for name in sorted(set(audit.profile_names()) - set(audit.REFERENCE_PROFILES)):
            for lens in audit.resolve_profile(name)["lenses"]:
                if lens["mechanical"]:
                    continue
                with self.subTest(pack=name, lens=lens["name"]):
                    self.assertEqual([], audit.signature_errors(lens, root))
                    self.assertTrue(lens["signature"].strip().startswith(audit.SIGNATURE_ABSENT))
                    self.assertGreaterEqual(len(audit._absent_reason(lens["signature"])),
                                            audit.MIN_ABSENT_REASON)

        for bad in ("-", "manual", "manual -", "see the manual for why", "- manual"):
            with self.subTest(bad=bad):
                lens = {"name": "x", "signature": bad,
                        "mechanical": audit._signature_is_mechanical(bad)}
                self.assertTrue(audit.signature_errors(lens, root),
                                f"{bad!r} was accepted as a considered declaration")


class SignatureContractIsShippedNotOnlyTestedTests(unittest.TestCase):
    """The guard must live in shipped code: a consuming project never runs these tests."""

    def test_the_contract_is_reachable_from_the_cli_a_consuming_project_runs(self) -> None:
        """MUTANT: keep the rule only in this test module. `reference-audit.md#audit-extend` and
        `process.md`'s Notes both invite a consuming project to append a pack row "stating its own
        signature in the same way", and such a project runs `readiness.py`, never `unittest`.
        Driven through the real CLI, not `signature_errors` directly.
        """
        done = _run_cli("profile", "--validate")
        self.assertEqual(0, done.returncode,
                         f"the shipped packs fail their own contract:\n{done.stderr}")
        self.assertIn("declares `manual` with a reason", done.stdout)

    def test_the_cli_exits_non_zero_on_a_breach(self) -> None:
        """The positive control's partner: a validator that always returned 0 would pass the
        test above while enforcing nothing."""
        fixture = _skill_fixture({"broken": _pack("Signature", ["| l | q | h | manual |"])})
        self.addCleanup(shutil.rmtree, fixture, ignore_errors=True)
        with mock.patch.object(audit, "SKILL_DIR", fixture), \
             mock.patch.object(audit, "PROFILE_DIR", fixture / "templates" / "audit-profiles"):
            args = argparse.Namespace(name=None, list=False, validate=True, format="text",
                                      root=str(SKILL.parents[2]))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                rc = audit.cmd_validate_profiles(args)
        self.assertEqual(1, rc)
        self.assertIn("without stating why", err.getvalue())

    def test_the_documented_token_prose_lists_exactly_the_constant(self) -> None:
        """MUTANT: widen `SIGNATURE_DETECTORS` and leave `process.md` saying the token is
        `python3`. The pack's own `count-by-hand` lens is this defect pointed at this change, so
        the prose is held to the constant rather than kept beside it by hand.
        """
        text = (PACKS / "process.md").read_text(encoding="utf-8")
        i = text.find("## Signatures")
        pack_section = text[i:text.find("\n|", i)]

        # The SECOND copy of the same claim. `reference-audit.md` stated the token set too, and
        # widening the code while fixing only the pack would leave this one lying - the
        # count-by-hand defect moved one file sideways rather than removed.
        ref = (SKILL / "reference-audit.md").read_text(encoding="utf-8")
        j = ref.find("Each lens names its **signature**")
        ref_section = ref[j:j + 900]

        for where, section in (("process.md", pack_section), ("reference-audit.md", ref_section)):
            for token in audit.SIGNATURE_DETECTORS:
                self.assertIn(f"`{token}`", section,
                              f"{where} does not document the runner {token!r} that the code "
                              f"accepts")
            for absent in ("perl", "ruby", "make"):
                self.assertNotIn(f"`{absent}`", section,
                                 f"{where} documents {absent!r}, which the code does not accept")


class SignatureRefusalsThatWereUnheldTests(unittest.TestCase):
    """Every mutant an independent review found SURVIVING the first cut of this story.

    Each docstring names the mutant, because eight rules here were enforced in shipped code and
    asserted nowhere - including the one AC4 exists to pin.
    """

    ROOT = SKILL.parents[2]

    def _errs(self, signature: str, root=None):
        """Through the PUBLIC helper, with `mechanical` deliberately not supplied: the helper
        re-derives it, which is also the MINOR-10 regression (a hand-built lens dict used to
        raise TypeError out of the helper a consuming project is told to call)."""
        return audit.signature_errors({"name": "x", "signature": signature}, root or self.ROOT)

    def test_a_mechanical_signature_naming_a_MISSING_path_is_refused(self) -> None:
        """MUTANT: `if not resolved.exists():` -> `if False:`. This is AC4's entire shipped rule
        and it survived the first cut: every other test either retyped the check itself or passed
        a signature that failed earlier, so no test ever drove a missing path through the helper.
        """
        errors = self._errs("python3 does/not/exist.py")
        self.assertTrue(errors, "a detector naming a path that is not on disk was accepted")
        self.assertIn("not on disk", errors[0])

    def test_a_long_reason_that_does_not_open_with_manual_is_refused_for_THAT(self) -> None:
        """MUTANT: drop the `tokens[0] != SIGNATURE_ABSENT` opener rule.

        Every original negative fixture failed on LENGTH, so the opener rule was never
        discriminated from the floor. This reason is 39 characters and six words - it clears both
        floors and must still be refused for not being the documented form.
        """
        errors = self._errs("hopefully someone eyeballs this one day")
        self.assertTrue(errors, "a non-`manual` prose cell was accepted as a declaration")
        self.assertIn("opens with neither", errors[0],
                      f"refused, but not for the opener: {errors[0]}")

    def test_a_reason_that_is_long_but_says_nothing_is_refused(self) -> None:
        """MUTANT: `MIN_ABSENT_REASON` 20 -> 1, and `_absent_reason` -> `signature.strip()`.

        A LENGTH floor alone accepted `manual - xxxxxxxxxxxxxxxxxxxx`: twenty characters of
        padding. A reason states something, so distinct words are required as well as length.
        """
        for padded in ("manual - xxxxxxxxxxxxxxxxxxxxxxxx",
                       "manual - aaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                       "manual - TODO fill this in later ok please"):
            with self.subTest(padded=padded):
                errors = self._errs(padded)
                self.assertTrue(errors, f"{padded!r} was accepted as a considered declaration")

    def test_a_short_reason_is_still_refused_so_the_length_floor_survives(self) -> None:
        """The floor's own positive control: the word check must not REPLACE it."""
        self.assertTrue(self._errs("manual - too short ok"))
        self.assertEqual(20, audit.MIN_ABSENT_REASON, "the floor's value changed")
        self.assertEqual(5, audit.MIN_ABSENT_REASON_WORDS)

    def test_an_honest_manual_declaration_is_accepted(self) -> None:
        """The positive control. A checker that refused every `manual` cell would pass every
        test above while making the documented form unusable."""
        self.assertEqual([], self._errs(
            "manual - whether a helper duplicates one the shared library provides is a judgement "
            "no search over the tree can settle"))

    def test_a_target_no_finder_could_run_is_refused_by_shape(self) -> None:
        """MINOR-9: an existence check alone accepted all of these.

        An ABSOLUTE path is the sharpest: `Path(root) / "/etc/passwd"` discards the root, so it
        validates on the machine that wrote it and nowhere else - the written-from-memory class
        this check exists to catch, passing the check.
        """
        cases = {
            "bash /etc/passwd": "absolute",
            "python3 /usr/bin/python3": "absolute",
            "python3 ../../../etc/hostname": "escapes the root",
            "python3 .claude/skills/sdlc-studio/scripts": "DIRECTORY",
            "python3 tools/check_links.py | head -1": "chains on",
        }
        for signature, expect in cases.items():
            with self.subTest(signature=signature):
                errors = self._errs(signature)
                self.assertTrue(errors, f"{signature!r} was accepted")
                self.assertIn(expect, errors[0], f"refused for the wrong reason: {errors[0]}")

    def test_rg_may_target_a_DIRECTORY_because_a_search_takes_a_tree(self) -> None:
        """The directory refusal's scope. Applying it to every runner would ban the one shape
        that legitimately needs a tree, and `rg <pattern> .` is a shipped signature."""
        self.assertEqual([], self._errs('rg -ni "pattern" .claude/skills/sdlc-studio/scripts'))

    def test_a_skill_relative_detector_resolves_from_a_FOREIGN_root(self) -> None:
        """The portability rule a reviewer demonstrated broken: eight of eight mechanical
        signatures were refused in a consuming project, because they were resolved against the
        audited root while the skill they name may be installed anywhere.

        MUTANT: drop the `SKILL_PATH_PREFIX` branch from `_resolve_signature_path`.
        """
        foreign = Path(tempfile.mkdtemp(prefix="foreign_"))
        self.addCleanup(shutil.rmtree, foreign, ignore_errors=True)
        self.assertEqual([], self._errs(
            "python3 .claude/skills/sdlc-studio/scripts/reconcile.py detect", root=foreign),
            "a shipped detector did not resolve from a root that is not this repo")

    def test_every_shipped_pack_validates_from_a_foreign_root(self) -> None:
        """The whole point of AC4, end to end and through the CLI: a consuming project must get a
        clean verdict on the packs IT DID NOT AUTHOR."""
        foreign = Path(tempfile.mkdtemp(prefix="foreignpacks_"))
        self.addCleanup(shutil.rmtree, foreign, ignore_errors=True)
        (foreign / "package.json").write_text('{"name":"other","scripts":{"build":"tsc"}}',
                                              encoding="utf-8")
        done = _run_cli("--root", str(foreign), "profile", "--validate")
        self.assertEqual(0, done.returncode,
                         f"the shipped packs fail their own contract in a consuming project:\n"
                         f"{done.stderr}")

    def test_a_literal_pipe_in_a_cell_survives_the_table_parse(self) -> None:
        """MUTANT: `_split_row` splits on every `|` again.

        An `rg` alternation needs a literal pipe, and markdown escapes it `\\|`. Splitting on
        every pipe tore the cell in half and the fragment was then refused for "naming no
        target" - the pattern was fine and the parser was eating it.
        """
        row = r"| alpha | q | h | rg -ni \"(a\|b)\" tools |"
        cells = audit._split_row(row)
        self.assertEqual(4, len(cells), f"the escaped pipe split the row: {cells}")
        self.assertIn("(a|b)", cells[3], "the escape was not unescaped after the split")

    def test_the_shipped_secret_scan_matches_the_forms_it_claims(self) -> None:
        """MODERATE-7: the first cut's pattern matched only identifiers BEGINNING `secret`, so it
        found nothing in the tree and would have missed `api_key`, `password` and `token`. A
        detector that cannot fire on its lens's class is decoration, and AC4 only ever checked
        that the path resolved."""
        lens = next(l for l in audit.resolve_profile("code")["lenses"]
                    if l["name"] == "security-smells")
        m = re.search(r'"(.+)"', lens["signature"])
        self.assertTrue(m, f"no quoted pattern in {lens['signature']!r}")
        rx = re.compile(m.group(1), re.I)
        for hit in ('api_key = "h"', 'API_KEY = "h"', 'password = "x"', 'SECRET_KEY = "y"',
                    'access_token = "z"', 'my_token="q"'):
            self.assertTrue(rx.search(hit), f"the shipped scan misses {hit!r}")
        for miss in ('harmless = 1', 'count = 2', 'tokenise(x)'):
            self.assertFalse(rx.search(miss), f"the shipped scan false-positives on {miss!r}")

    def test_the_prose_documents_EXACTLY_the_constant_in_both_directions(self) -> None:
        """MUTANT: rewrite the sentence to document `go` and `perl6` alongside the real runners.

        The first cut asserted only that each real token APPEARS, plus that a hand-picked triple
        (`perl`, `ruby`, `make`) does not - so the prose could advertise any runner not on that
        list. Compared as SETS now, which is what "exactly" means.
        """
        for rel, marker in (("templates/audit-profiles/process.md", "detector tokens are"),
                            ("reference-audit.md", "detector token (")):
            text = (SKILL / rel).read_text(encoding="utf-8")
            i = text.find(marker)
            self.assertNotEqual(-1, i, f"{rel}: the documented-token sentence was renamed")
            sentence = text[i:i + 220]
            tokens = {tok for tok in re.findall(r"`([^`]+)`", sentence) if " " not in tok}
            self.assertEqual(set(audit.SIGNATURE_DETECTORS), tokens,
                             f"{rel} documents {sorted(tokens)} but the code accepts "
                             f"{sorted(audit.SIGNATURE_DETECTORS)}")


class AbsentReasonIsMeasuredWithoutItsOwnTokenTests(unittest.TestCase):
    """Three mutants that survived because they change a MEASUREMENT or a MESSAGE, not a verdict.

    Each needed a fixture chosen so the mutant flips the outcome, which none of the existing
    fixtures did - the exact "the test cannot fail" shape this story keeps being rejected for.
    """

    ROOT = SKILL.parents[2]

    def _errs(self, signature: str):
        return audit.signature_errors({"name": "x", "signature": signature}, self.ROOT)

    def test_the_manual_token_does_not_count_towards_its_own_reason(self) -> None:
        """MUTANT: `_absent_reason` -> `signature.strip()`, measuring the WHOLE cell.

        Discriminating fixture: the reason alone is 18 characters and four distinct words, so it
        is refused; the whole cell is 27 characters and five words, so the mutant accepts it. The
        documented token must not pay for the substance it exists to introduce.
        """
        self.assertEqual("one two three four", audit._absent_reason("manual - one two three four"))
        self.assertTrue(self._errs("manual - one two three four"),
                        "the `manual` token was counted as part of the reason it introduces")

    def test_the_separator_is_stripped_from_the_reason(self) -> None:
        """MUTANT: `rest.lstrip("-:– ")` -> `rest`, leaving the separator in the measured reason.

        Asserted on the helper's RETURN VALUE, because the two characters only occasionally cross
        the length floor - a verdict-level fixture would be luck, and this is the property.
        """
        for sig, expect in (("manual - a stated reason", "a stated reason"),
                            ("manual: a stated reason", "a stated reason"),
                            ("manual   a stated reason", "a stated reason")):
            with self.subTest(sig=sig):
                self.assertEqual(expect, audit._absent_reason(sig))

    def test_a_BLANK_cell_is_refused_with_its_own_diagnostic(self) -> None:
        """MUTANT: delete the blank-signature branch. The cell is still refused by the
        "opens with neither" branch, so the VERDICT is unchanged and only the better message is
        lost - which no verdict-level assertion can see. The message is the point: a blank cell
        and a prose cell want different fixes.
        """
        blank = self._errs("")
        self.assertTrue(blank)
        self.assertIn("carries no signature", blank[0],
                      f"a blank cell was reported as a malformed one: {blank[0]}")
        prose = self._errs("hopefully someone eyeballs this one day")
        self.assertIn("opens with neither", prose[0])
        self.assertNotEqual(blank[0], prose[0],
                            "a blank cell and a prose cell give the same message, so one of the "
                            "two diagnostics is dead")


if __name__ == "__main__":
    unittest.main()
