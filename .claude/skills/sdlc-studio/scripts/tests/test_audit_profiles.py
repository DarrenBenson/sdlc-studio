"""Tests for the audit lens-pack surface: the packs on disk and `--profile` resolution.

A profile is a declarative lens pack. These tests hold three things the packs
cannot hold for themselves: that each shipped pack declares real lenses, that
resolution refuses a name no pack declares (rather than running an empty lens
set), and that the security posture the repo pack inherited survives verbatim.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

audit = loader.load_script("audit")

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
    return subprocess.run([sys.executable, "-B", str(SKILL / "scripts" / "audit.py"), *argv],
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

    A full mutation enumeration over `audit.py` left six survivors inside `cmd_profile`:
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
                         {"project", "skill", "repo", "code", "test"})

    def test_no_profile_opts_out_of_the_shared_refute_panel(self) -> None:
        for name in audit.profile_names():
            got = audit.resolve_profile(name)
            self.assertEqual(got["threshold"], {"survive": 2, "votes": 3},
                             f"{name} does not declare the shared refute threshold")
            self.assertIn("does not opt out", got["refute"] + " " + got["source"],
                          f"{name} never states that it is panel-wired")


if __name__ == "__main__":
    unittest.main()
