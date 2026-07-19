"""Tests for the audit lens-pack surface: the packs on disk and `--profile` resolution.

A profile is a declarative lens pack. These tests hold three things the packs
cannot hold for themselves: that each shipped pack declares real lenses, that
resolution refuses a name no pack declares (rather than running an empty lens
set), and that the security posture the repo pack inherited survives verbatim.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

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

    def test_the_four_promised_profiles_are_all_present(self) -> None:
        self.assertEqual(set(audit.profile_names()), {"project", "skill", "repo", "code"})

    def test_no_profile_opts_out_of_the_shared_refute_panel(self) -> None:
        for name in audit.profile_names():
            got = audit.resolve_profile(name)
            self.assertEqual(got["threshold"], {"survive": 2, "votes": 3},
                             f"{name} does not declare the shared refute threshold")
            self.assertIn("does not opt out", got["refute"] + " " + got["source"],
                          f"{name} never states that it is panel-wired")


if __name__ == "__main__":
    unittest.main()
