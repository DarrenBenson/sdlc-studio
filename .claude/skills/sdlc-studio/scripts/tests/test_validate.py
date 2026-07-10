"""Unit tests for validate.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import pathlib
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "validate.py"
_spec = importlib.util.spec_from_file_location("validate", SCRIPT_PATH)
assert _spec and _spec.loader
validate = importlib.util.module_from_spec(_spec)
sys.modules["validate"] = validate
_spec.loader.exec_module(validate)

GOOD_STORY = "# Login\n\n> **Status:** Done\n\n### AC1: Happy\n- **Verify:** file a.py\n"


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class ValidateFileTests(unittest.TestCase):
    def test_good_story_has_no_violations(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            self.assertEqual(validate.validate_file(p, "story"), [])

    def test_bad_status_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0002-x.md",
                       "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("status-vocab", rules)

    def test_status_vocab_error_names_extension_mechanism(self) -> None:
        # The error carries the sanctioned remedy: declare an established project
        # status via config, not rewrite historical artifacts.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0002-x.md",
                       "# X\n\n> **Status:** Frozen\n\n### AC1: y\n- **Verify:** file b\n")
            msgs = [v["message"] for v in validate.validate_file(p, "story")
                    if v["rule"] == "status-vocab"]
            self.assertEqual(len(msgs), 1)
            self.assertIn("status_vocab.story", msgs[0])
            self.assertIn(".config.yaml", msgs[0])
            self.assertIn("reference-config.md", msgs[0])

    def test_missing_status_and_title(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0003-x.md", "no heading, no status\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-status", rules)
            self.assertIn("no-title", rules)

    def test_story_without_ac_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0004-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)

    def test_no_ac_grandfathered_below_adopt_after(self) -> None:
        # A pre-cutoff story is exempt from no-ac; a story at/after the cutoff is not.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: US0682\n")
            old = _write(root, "sdlc-studio/stories/US0100-x.md",
                         "# X\n\n> **Status:** Draft\n")
            new = _write(root, "sdlc-studio/stories/US0700-y.md",
                         "# Y\n\n> **Status:** Draft\n")
            old_rules = {v["rule"] for v in validate.validate_file(old, "story", root)}
            new_rules = {v["rule"] for v in validate.validate_file(new, "story", root)}
            self.assertNotIn("no-ac", old_rules)  # grandfathered
            self.assertIn("no-ac", new_rules)      # judged

    def test_no_ac_still_flagged_without_cutoff(self) -> None:
        # No .config.yaml cutoff -> the discipline applies to every story.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _write(root, "sdlc-studio/stories/US0100-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertIn("no-ac", rules)

    def test_no_ac_still_flagged_with_malformed_config(self) -> None:
        # Fail-safe: a broken .config.yaml must NOT silently exempt - no-ac fires.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml", ": : not yaml :")
            p = _write(root, "sdlc-studio/stories/US0001-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertIn("no-ac", rules)

    def test_no_ac_at_cutoff_is_exempt(self) -> None:
        # The cutoff is inclusive (<=): the cutoff story itself is grandfathered, matching
        # conformance/provenance ("this id and earlier are exempt").
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: US0100\n")
            p = _write(root, "sdlc-studio/stories/US0100-x.md",
                       "# X\n\n> **Status:** Draft\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story", root)}
            self.assertNotIn("no-ac", rules)  # boundary id exempt

    def test_no_ac_bare_int_cutoff_exempts_at_boundary(self) -> None:
        # BG0039: a bare-integer cutoff used to silently fail here (id_number("103") -> None),
        # so a pre-cutoff story was wrongly flagged. It must now exempt ids <= the cutoff.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/.config.yaml",
                   "conformance:\n  adopt_after: 103\n")  # bare int
            at = _write(root, "sdlc-studio/stories/US0103-x.md",
                        "# X\n\n> **Status:** Draft\n")     # 103 <= 103 -> exempt
            below = _write(root, "sdlc-studio/stories/US0050-y.md",
                           "# Y\n\n> **Status:** Draft\n")  # 50 <= 103 -> exempt
            above = _write(root, "sdlc-studio/stories/US0200-z.md",
                           "# Z\n\n> **Status:** Draft\n")  # 200 > 103 -> judged
            self.assertNotIn("no-ac", {v["rule"] for v in validate.validate_file(at, "story", root)})
            self.assertNotIn("no-ac", {v["rule"] for v in validate.validate_file(below, "story", root)})
            self.assertIn("no-ac", {v["rule"] for v in validate.validate_file(above, "story", root)})

    def test_bad_id_format(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/login.md", GOOD_STORY)
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("id-format", rules)

    def test_decorated_status_accepted(self) -> None:
        # `Done (v2.66.0)` canonicalises to `Done` — not a status-vocab error.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0005-x.md",
                       "# X\n\n> **Status:** Done (v2.66.0)\n\n### AC1: y\n- **Verify:** file b\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("status-vocab", rules)

    def test_bold_bullet_ac_accepted(self) -> None:
        # `- **AC1:**` compact bullet style satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0006-x.md",
                       "# X\n\n> **Status:** Draft\n\n- **AC1:** login works\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_plain_ac_section_accepted(self) -> None:
        # A populated `## Acceptance Criteria` section (plain bullets, no ACn
        # ids) satisfies the AC requirement.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0007-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n- user can log in\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertNotIn("no-ac", rules)

    def test_empty_ac_section_still_flagged(self) -> None:
        # An AC heading with no content before the next heading is still no-ac.
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/stories/US0008-x.md",
                       "# X\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n## Notes\n- something\n")
            rules = {v["rule"] for v in validate.validate_file(p, "story")}
            self.assertIn("no-ac", rules)


class InferTypeTests(unittest.TestCase):
    def test_infer_from_dir(self) -> None:
        self.assertEqual(validate.infer_type(Path("sdlc-studio/epics/EP0001-x.md")), "epic")

    def test_infer_from_id_prefix(self) -> None:
        self.assertEqual(validate.infer_type(Path("/tmp/CR-0001-x.md")), "cr")


class CheckCmdTests(unittest.TestCase):
    def test_check_exit_nonzero_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-bad.md", "# X\n\n> **Status:** Frozen\n")
            rc = validate.main(["check", "--type", "story", "--root", d])
            self.assertEqual(rc, 1)

    def test_check_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _write(Path(d), "sdlc-studio/stories/US0001-login.md", GOOD_STORY)
            rc = validate.main(["check", "--type", "story", "--root", d])
            self.assertEqual(rc, 0)


GOOD_AGENTS = (
    "# Proj\n\n"
    "Read `reference-doctrine.md`. Read `sdlc-studio/reviews/LATEST.md` first.\n"
    "IMPORTANT pre-release gate: `/sdlc-studio reconcile --verify` + the review legs.\n"
    "After `/compact` or a reset, re-read LATEST.md and run status.\n"
)


class InstructionsTests(unittest.TestCase):
    def test_missing_agents_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            v = validate.check_instructions(Path(d))
            self.assertIn("no-agents", {x["rule"] for x in v})
            self.assertTrue(any(x["severity"] == "error" for x in v))

    def test_good_agents_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
            self.assertEqual(validate.check_instructions(root), [])

    def test_claude_not_pointer_warns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            (root / "CLAUDE.md").write_text("# full instructions inline\n", encoding="utf-8")
            self.assertIn("claude-not-pointer", {x["rule"] for x in validate.check_instructions(root)})

    def test_missing_elements_warn(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "AGENTS.md").write_text("# Proj\n\nNothing useful here.\n", encoding="utf-8")
            rules = {x["rule"] for x in validate.check_instructions(root)}
            self.assertIn("no-doctrine-pointer", rules)
            self.assertIn("no-latest-pointer", rules)
            self.assertIn("no-release-gate", rules)
            self.assertIn("no-compaction-rule", rules)

    def test_cmd_exit_nonzero_when_no_agents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = validate.main(["instructions", "--root", d])
            self.assertEqual(rc, 1)

    def test_cmd_exit_zero_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text(GOOD_AGENTS, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = validate.main(["instructions", "--root", d])
            self.assertEqual(rc, 0)


class PlaceholderTests(unittest.TestCase):
    def _story(self, body):
        import tempfile
        d = tempfile.mkdtemp()
        f = pathlib.Path(d) / "US0001-x.md"
        f.write_text(body, encoding="utf-8")
        return f

    def test_placeholder_ac_flagged(self):
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "### AC1: {{define}}\n\n- **Given** {{context}}\n- **Verify:** {{check}}\n")
        rules = [v["rule"] for v in validate.validate_file(f, "story") if v["severity"] == "error"]
        self.assertIn("placeholder", rules)

    def test_placeholder_metadata_flagged(self):
        f = self._story("# US0001: x\n\n> **Status:** {{status}}\n\n## Acceptance Criteria\n\n"
                        "- some real criterion\n")
        self.assertIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_prose_placeholder_not_flagged(self):
        # meta-artifact discussing {{placeholder}} syntax in prose must NOT be flagged
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Description\n\n"
                        "Templates use {{placeholder}} syntax for fields.\n\n"
                        "## Acceptance Criteria\n\n- a real filled criterion\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_checkbox_placeholder_flagged(self):
        # CR/story AC checklist `- [ ] {{criterion}}` is a structural AC line (CR0056 critic gap).
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] {{criterion}}\n")
        self.assertIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_checkbox_real_text_not_flagged(self):
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] a genuine filled criterion\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])

    def test_embedded_token_in_real_ac_not_flagged(self):
        # A real, filled AC that references a {{...}} token in its text (this repo's own
        # meta-CRs) must NOT be flagged - only placeholder-ONLY values are (CR0056 critic).
        f = self._story("# US0001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                        "- [ ] validate flags unresolved {{...}} placeholders as an error\n"
                        "- [x] All three use `{{placeholder}}` syntax and pass lint\n")
        self.assertNotIn("placeholder", [v["rule"] for v in validate.validate_file(f, "story")])


class PersonaWellFormedTests(unittest.TestCase):
    def _persona(self, repo, name, role, *, sections):
        d = repo / "sdlc-studio" / "personas"; d.mkdir(parents=True, exist_ok=True)
        body = (f"# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                f"| **Cast role** | {role} |\n\n")
        body += "".join(f"## {s}\n\nx\n\n" for s in sections)
        (d / f"{name}.md").write_text(body, encoding="utf-8")

    STD = ["Who They Are", "End Goals", "Experience Goals", "Behaviours & Context",
           "Frustrations", "Scenario"]
    NEG = ["Who They Are", "End Goals (stated to exclude)", "Why We Are Not Designing For Them",
           "Behaviours & Context", "Frustrations", "Scenario"]

    def test_well_formed_primary_no_findings(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "maya", "Primary", sections=self.STD)
            self.assertEqual(validate.check_personas(repo), [])

    def test_primary_missing_scenario_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "maya", "Primary", sections=[s for s in self.STD if s != "Scenario"])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Scenario" in m for m in msgs))

    def test_negative_variant_well_formed_no_findings(self):
        # the Negative persona has no Experience Goals - the cast-role-aware check must accept it
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "trevor", "Negative", sections=self.NEG)
            self.assertEqual(validate.check_personas(repo), [])

    def test_negative_missing_whynot_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "trevor", "Negative",
                          sections=[s for s in self.NEG if "Why" not in s])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Why" in m for m in msgs))

    def test_customer_experience_and_scenario_optional(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "buyer", "Customer",
                          sections=["Who They Are", "End Goals", "Behaviours & Context", "Frustrations"])
            self.assertEqual(validate.check_personas(repo), [])

    def test_missing_cast_role_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            (dd / "x.md").write_text("# X\n\n## Who They Are\n\nx\n", encoding="utf-8")
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertIn("persona-cast-role", rules)


    def test_collision_headings_do_not_false_pass(self):
        # prefix matching: unrelated headings that merely contain the keywords must NOT satisfy
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "junk", "Primary",
                          sections=["Why End Goals Matter", "Some Context We Discuss",
                                    "Frustrations Of Other People", "Scenario Planning Theory"])
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertIn("persona-section", rules)  # flagged, not a clean pass

    def test_negative_loose_why_flagged(self):
        # "## Why This Matters" must NOT satisfy the Negative why-not rationale
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "t", "Negative",
                          sections=["Who They Are", "End Goals (stated to exclude)",
                                    "Why This Matters", "Behaviours & Context", "Frustrations", "Scenario"])
            msgs = [v["message"] for v in validate.check_personas(repo)]
            self.assertTrue(any("Why we are not" in m for m in msgs))

    def test_empty_bodies_still_well_formed(self):
        # well-formed is structural (headings present); bodies are not content-checked (RFC0017)
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); self._persona(repo, "maya", "Primary", sections=self.STD)
            self.assertEqual(validate.check_personas(repo), [])

    def test_unknown_role_held_to_standard(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            # no Cast role; has the common sections but not Experience Goals / Scenario
            (dd / "x.md").write_text(
                "# X\n\n## Who They Are\n\nx\n## End Goals\n\nx\n"
                "## Behaviours & Context\n\nx\n## Frustrations\n\nx\n", encoding="utf-8")
            out = validate.check_personas(repo)
            rules = [v["rule"] for v in out]; msgs = [v["message"] for v in out]
            self.assertIn("persona-cast-role", rules)               # role missing
            self.assertTrue(any("Experience Goals" in m for m in msgs))  # held to standard
            self.assertTrue(any("Scenario" in m for m in msgs))

    def test_shipped_personas_are_well_formed(self):
        # pin the two shipped personas (Maya Primary + Trevor Negative) - a future edit must not break them
        repo_root = pathlib.Path(__file__).resolve().parents[5]
        src = repo_root / "sdlc-studio" / "personas"
        if not (src / "maya-okafor-founder-engineer.md").exists():
            self.skipTest("shipped personas not present")
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d); dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            for f in src.glob("*.md"):
                (dd / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_no_personas_dir_is_noop(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(validate.check_personas(pathlib.Path(d)), [])

    def test_index_md_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            dd = repo / "sdlc-studio" / "personas"; dd.mkdir(parents=True)
            (dd / "index.md").write_text("# Index\n\nstuff\n", encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_consult_guide_and_readme_not_flagged(self):
        # BG0027: non-design-persona files in personas/ are not checked for the Cooper schema
        import tempfile, pathlib as _pl
        d = tempfile.mkdtemp(); pd = _pl.Path(d) / "sdlc-studio" / "personas"; pd.mkdir(parents=True)
        (pd / "consult-guide.md").write_text("# Consult guide\n\nrun consult team\n", encoding="utf-8")
        (pd / "README.md").write_text("# Personas\n\noverview\n", encoding="utf-8")
        self.assertEqual([f["file"] for f in validate.check_personas(_pl.Path(d))], [])

    def test_nested_only_personas_get_advisory_not_clean_pass(self):
        # BG0040: a project whose personas are nested (no flat design personas) must NOT read as a
        # clean pass - the flat glob finds nothing, so the check must say so, not pass vacuously.
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            nested = repo / "sdlc-studio" / "personas" / "team"
            nested.mkdir(parents=True)
            body = ("# Maya\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                    "| **Cast role** | Primary |\n\n## Who They Are\n\nx\n")
            (nested / "maya.md").write_text(body, encoding="utf-8")
            out = validate.check_personas(repo)
            rules = [v["rule"] for v in out]
            self.assertIn("persona-layout", rules)
            self.assertTrue(any("not validated" in v["message"] for v in out))

    def test_nested_count_reported_in_advisory(self):
        # the advisory names how many nested files were found (so the operator can act).
        # team/ is a genuinely-legacy nesting; seats/ and stakeholders/ are the generator's
        # canonical homes and are excluded from this advisory by design (CR0218).
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            pdir = repo / "sdlc-studio" / "personas" / "team"
            pdir.mkdir(parents=True)
            (pdir / "a.md").write_text("# A\n\n## Who They Are\n\nx\n", encoding="utf-8")
            (pdir / "b.md").write_text("# B\n\n## Who They Are\n\nx\n", encoding="utf-8")
            out = validate.check_personas(repo)
            self.assertEqual(len(out), 1)
            self.assertEqual(out[0]["rule"], "persona-layout")
            self.assertIn("2", out[0]["message"])

    def test_seats_and_stakeholders_are_canonical_not_nested(self):
        # CR0218: the generator's own output homes never trip the layout advisory
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            for sub in ("seats", "stakeholders"):
                pdir = repo / "sdlc-studio" / "personas" / sub
                pdir.mkdir(parents=True)
                (pdir / "x.md").write_text("# X\n", encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])

    def test_flat_personas_present_no_layout_advisory(self):
        # when flat design personas ARE found, nested files do not trigger the advisory
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            self._persona(repo, "maya", "Primary", sections=self.STD)
            nested = repo / "sdlc-studio" / "personas" / "team"
            nested.mkdir(parents=True)
            (nested / "x.md").write_text("# X\n\n## Who They Are\n\nx\n", encoding="utf-8")
            rules = [v["rule"] for v in validate.check_personas(repo)]
            self.assertNotIn("persona-layout", rules)

    def test_seats_only_is_not_a_layout_advisory(self):
        # seats/ holds review-seat charters (a different schema), not nested design personas;
        # a personas/ dir with only seats/ is genuinely empty of personas, not a nested layout
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)
            seats = repo / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "engineer.md").write_text("# Engineer seat\n\ncharter\n", encoding="utf-8")
            self.assertEqual(validate.check_personas(repo), [])


class NotAnArtifactSweepTests(unittest.TestCase):
    """An id-named file the census excludes (no artifact header) must be NAMED,
    never silently invisible - the operator either fixes the header or declares
    the suffix as a companion. Warning severity: a declared companion is fine."""

    def _run(self, root):
        import argparse
        ns = argparse.Namespace(root=str(root), type=None, file=None, format="json")
        import contextlib, io, json as _json
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            validate.cmd_check(ns)
        return _json.loads(buf.getvalue())

    def test_off_template_artifact_named_as_warning(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/stories/US0001-login.md",
                   "# US0001 - Login\n\nStatus: Draft\n")   # off-template: excluded
            out = self._run(root)
            rules = [v["rule"] for v in out["violations"]]
            self.assertIn("not-an-artifact", rules)
            v = next(x for x in out["violations"] if x["rule"] == "not-an-artifact")
            self.assertEqual(v["severity"], "warning")
            self.assertIn("companion", v["message"])        # both remedies named

    def test_declared_companion_suffix_not_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/epics/EP0001-x.md",
                   "# EP0001: x\n\n> **Status:** Draft\n")
            _write(root, "sdlc-studio/epics/EP0001-x-consultations.md", "notes\n")
            out = self._run(root)
            self.assertEqual([v for v in out["violations"]
                              if v["rule"] == "not-an-artifact"], [])


class StructuredAuthorshipTests(unittest.TestCase):
    """US0060/CR0169: schema-v3 artefacts carry a typed, resolvable raised_by; v2 is exempt."""

    def _v3(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")

    def _bug(self, root: Path, meta: str) -> Path:
        return _write(root, "sdlc-studio/bugs/BG0001-x.md",
                      f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{meta}\n")

    def test_v3_missing_authorship_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._bug(root, "")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("authorship-structured", rules)

    def test_v3_unresolvable_persona_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = self._bug(root, "> **Raised-by:** Nobody Here; persona; v1")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("authorship-unresolved", rules)

    def test_v3_resolvable_persona_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            pd = root / "sdlc-studio" / "personas"
            pd.mkdir(parents=True, exist_ok=True)
            (pd / "sam.md").write_text("# Sam Eriksson - QA amigo\n", encoding="utf-8")
            p = self._bug(root, "> **Raised-by:** Sam Eriksson; persona; v1")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertNotIn("authorship-structured", rules)
            self.assertNotIn("authorship-unresolved", rules)

    def test_v2_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # no .config.yaml -> v2
            p = self._bug(root, "")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertNotIn("authorship-structured", rules)


class SeparationOfDutiesTests(unittest.TestCase):
    """US0061/CR0170: a triager may not be the raiser (v3). Solo-human self-triage warns."""

    def _v3_persona(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        pd = root / "sdlc-studio" / "personas"; pd.mkdir(parents=True, exist_ok=True)
        (pd / "sam.md").write_text("# Sam Eriksson - QA amigo\n", encoding="utf-8")
        (pd / "dani.md").write_text("# Dani Okafor - Engineering amigo\n", encoding="utf-8")

    def _bug(self, root: Path, raised: str, triaged: str) -> Path:
        return _write(root, "sdlc-studio/bugs/BG0001-x.md",
                      f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                      f"> **Raised-by:** {raised}\n> **Triaged-by:** {triaged}\n")

    def test_same_persona_raiser_and_triager_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Sam Eriksson; persona; v1", "Sam Eriksson; persona; v1")
            errs = [v for v in validate.validate_file(p, "bug", root)
                    if v["rule"] == "duties-separated" and v["severity"] == "error"]
            self.assertTrue(errs)

    def test_distinct_personas_pass(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Sam Eriksson; persona; v1", "Dani Okafor; persona; v1")
            self.assertEqual([v for v in validate.validate_file(p, "bug", root)
                              if v["rule"] == "duties-separated"], [])

    def test_solo_human_self_triage_warns_not_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3_persona(root)
            p = self._bug(root, "Darren; human; v1", "Darren; human; v1")
            rows = [v for v in validate.validate_file(p, "bug", root) if v["rule"] == "duties-separated"]
            self.assertTrue(rows)
            self.assertTrue(all(v["severity"] == "warning" for v in rows))


class EvidenceSchemaTests(unittest.TestCase):
    """US0062/CR0171: v3 bugs need evidence; v3 CRs need impact + effort. v2 exempt."""

    def _v3(self, root: Path) -> None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
        pd = root / "sdlc-studio" / "personas"; pd.mkdir(parents=True, exist_ok=True)
        (pd / "sam.md").write_text("# Sam Eriksson - QA\n", encoding="utf-8")

    _AUTH = "> **Raised-by:** Sam Eriksson; persona; v1\n"

    def test_bug_without_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{self._AUTH}\n"
                       "## Summary\n\nsomething is wrong\n")
            rules = [v["rule"] for v in validate.validate_file(p, "bug", root)]
            self.assertIn("evidence-present", rules)

    def test_bug_with_file_line_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       f"# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n{self._AUTH}\n"
                       "## Evidence\n\n`scripts/foo.py:42` returns the wrong value\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "bug", root)])

    def test_cr_without_effort_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/change-requests/CR0001-x.md",
                       f"# CR-0001: x\n\n> **Status:** Proposed\n> **Priority:** Low\n> **Type:** X\n{self._AUTH}\n"
                       "## Impact\n\nusers are affected\n")
            self.assertIn("evidence-present",
                          [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_cr_with_impact_and_effort_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self._v3(root)
            p = _write(root, "sdlc-studio/change-requests/CR0001-x.md",
                       f"# CR-0001: x\n\n> **Status:** Proposed\n> **Priority:** Low\n> **Type:** X\n{self._AUTH}\n"
                       "## Impact\n\nusers are affected and blocked\n\n## Effort\n\n**M.** moderate\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "cr", root)])

    def test_v2_bug_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # v2
            p = _write(root, "sdlc-studio/bugs/BG0001-x.md",
                       "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n\n## Summary\n\nx\n")
            self.assertNotIn("evidence-present",
                             [v["rule"] for v in validate.validate_file(p, "bug", root)])


def _v3_cr(root: Path, tranche_line: str = "") -> Path:
    """A schema-v3 repo with one CR; `tranche_line` is an optional `> **Tranche:** ...` line."""
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    body = f"# CR-0001: c\n\n> **Status:** Proposed\n{tranche_line}\n## Summary\n\ns\n"
    return _write(root, "sdlc-studio/change-requests/CR0001-c.md", body)


class TrancheShapeTests(unittest.TestCase):
    """US0068 AC1: a record-only tranche reference - absent or valued is fine; present-but-empty
    is a malformed record. Era-gated to schema v3."""

    def _rules(self, p: Path, root: Path) -> set:
        return {v["rule"] for v in validate.validate_file(p, "cr", root)}

    def test_tranche_shape_empty_value_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:**\n")
            self.assertIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_whitespace_value_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:**    \n")
            self.assertIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_present_value_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "> **Tranche:** sprint-12\n")
            self.assertNotIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_absent_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = _v3_cr(root, "")
            self.assertNotIn("tranche-shape", self._rules(p, root))

    def test_tranche_shape_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)  # v2: no .config.yaml
            p = _write(root, "sdlc-studio/change-requests/CR0001-c.md",
                       "# CR-0001: c\n\n> **Status:** Proposed\n> **Tranche:**\n\n## Summary\n\ns\n")
            self.assertNotIn("tranche-shape",
                             {v["rule"] for v in validate.validate_file(p, "cr", root)})


class UlidIdFormatTests(unittest.TestCase):
    """US0112/CR0198: validate must accept a v3 ULID id (BG-01JQK3F8), not flag it id-format."""

    def test_v3_ulid_id_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/BG-01JQK3F8-x.md",
                       "# BG-01JQK3F8: x\n\n> **Status:** Open\n> **Severity:** Low\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertNotIn("id-format", rules)

    def test_v2_sequential_still_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/BG0001-x.md",
                       "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertNotIn("id-format", rules)

    def test_garbage_id_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = _write(Path(d), "sdlc-studio/bugs/notanid-x.md",
                       "# x\n\n> **Status:** Open\n")
            rules = {v["rule"] for v in validate.validate_file(p, "bug")}
            self.assertIn("id-format", rules)

class SeatCheckTests(unittest.TestCase):
    """The error-level generation floor: role declared+allowed, review render present,
    demographic denylist clean, one card per role, cast capped at 5."""

    GOOD = ("<!-- role: qa -->\n# Priya - QA seat\n\n## Lens\n\nx\n"
            "## Pushes Back When\n\nx\n## Shadow\n\nx\n")

    def _seat(self, root: Path, name: str, body: str) -> None:
        d = root / "sdlc-studio" / "personas" / "seats"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(body, encoding="utf-8")

    def _rules(self, root: Path) -> set:
        return {v["rule"] for v in validate.check_seats(root)}

    def test_good_seat_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            errs = [v for v in validate.check_seats(Path(d)) if v["severity"] == "error"]
            self.assertEqual(errs, [])

    def test_missing_role_and_render_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "bad.md", "# Someone\n\n## Who They Are\n\nx\n")
            rules = self._rules(Path(d))
            self.assertIn("seat-no-role", rules)
            self.assertIn("seat-no-review-render", rules)

    def test_duplicate_role_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "a.md", self.GOOD)
            self._seat(Path(d), "b.md", self.GOOD)
            self.assertIn("seat-duplicate-role", self._rules(Path(d)))

    def test_demographic_fluff_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "p.md", self.GOOD.replace(
                "# Priya - QA seat", "# Priya - QA seat\n\n34 years old, married"))
            self.assertIn("seat-demographic-fluff", self._rules(Path(d)))

    def test_cast_over_five_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            roles = ["engineering", "qa", "product", "security", "sre", "data"]
            for i, r in enumerate(roles):
                self._seat(Path(d), f"s{i}.md", self.GOOD.replace("role: qa", f"role: {r}"))
            self.assertIn("seat-cast-size", self._rules(Path(d)))

    def test_cli_exits_1_on_errors_0_clean(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "bad.md", "# no role\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate.main(["seats", "--root", d]), 1)
        with tempfile.TemporaryDirectory() as d:
            self._seat(Path(d), "priya.md", self.GOOD)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validate.main(["seats", "--root", d]), 0)


if __name__ == "__main__":
    unittest.main()
