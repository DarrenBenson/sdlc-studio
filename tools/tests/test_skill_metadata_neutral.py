"""US1319: the skill's metadata requires no single harness, and `--agentic` states its fallback.

Harnesses show the SKILL.md `description` when they list skills, `compatibility` says what the
skill needs, and llms.txt is what an agent evaluating the repository reads first. None of them
may say one harness is required: the skill runs in six. `epic implement --agentic` runs its waves
in parallel where the harness has sub-agents with worktree isolation; elsewhere the same stories
run one at a time in dependency order, which is the fallback docs/harnesses.md states, so the
compatibility line and the epic help say so too.

BG1599: docs/harnesses.md marks in-session sub-agents untested outside Claude Code, so a parallel
claim must name worktree isolation, and reference-epic.md's Agentic mode, the procedure an agent
follows, must carry the one-at-a-time step in the words the other two surfaces use.

Every test also runs its check on a broken copy, so a check that cannot fail is caught by the
test that relies on it.
"""
# test-census-subject: .claude/skills/sdlc-studio/SKILL.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL_MD = REPO / ".claude" / "skills" / "sdlc-studio" / "SKILL.md"
EPIC_HELP = REPO / ".claude" / "skills" / "sdlc-studio" / "help" / "epic.md"
LLMS = REPO / "llms.txt"
REFERENCE_EPIC = REPO / ".claude" / "skills" / "sdlc-studio" / "reference-epic.md"

#: The six harnesses, alphabetical without regard to case: the order llms.txt names them in.
HARNESSES = ("Claude Code", "Codex", "Cursor", "Gemini CLI", "GitHub Copilot", "opencode")
#: A harness or vendor named in a sentence that states a requirement makes it a requirement.
_HARNESS = re.compile(r"Claude|Anthropic|Codex|Cursor|Gemini|Copilot|opencode")
_REQUIRES = re.compile(r"(?i)\b(requires?|required|needs?|needed|only)\b|-only\b")
_SENTENCE = re.compile(r"(?<=[.;])\s+")
#: What the compatibility line must say `--agentic` does, with sub-agents and without.
AGENTIC_FALLBACK = {"--agentic": r"--agentic", "parallel": r"(?i)\bparallel\b",
                    "sub-agents": r"(?i)\bsub-?agents\b", "one at a time": r"(?i)\bone at a time\b"}
#: What the epic help's `--agentic` row must say: when it runs waves, and what runs without them.
AGENTIC_ROW = {"sub-agents": r"(?i)\bsub-?agents\b", "one at a time": r"(?i)\bone at a time\b",
               "dependency order": r"(?i)\bdependency order\b"}
#: The facts the compatibility line already carried, which a neutral rewrite keeps.
KEPT_FACTS = ("Python 3.10+", "gh CLI")
#: The agentskills.io limit on `compatibility`.
COMPATIBILITY_LIMIT = 500
NEW_PAGES = ("docs/harnesses.md", "docs/enterprise.md")
#: BG1599: the capability parallel waves need, and the words the fallback is stated in, the same
#: on all three surfaces.
WORKTREE_SUBAGENTS = r"(?i)\bsub-?agents with worktree isolation\b"
_BARE_SUBAGENTS = re.compile(r"(?i)\bsub-?agents\b(?! with worktree isolation)")
FALLBACK_WORDS = r"(?i)\bone at a time in dependency order\b"
#: The no-sub-agent step, found by its condition, and what it must say once found.
_NO_SUBAGENTS = re.compile(r"(?i)\b(no|without)\s+sub-?agents with worktree isolation\b")
FALLBACK_STEP = {"one at a time in dependency order": FALLBACK_WORDS,
                 "as plain `epic implement` does": r"as plain `epic implement` does",
                 "that the prior `epic plan --agentic` does not apply":
                     r"`epic plan --agentic`[^.]*\bnot apply\b"}
#: A fallback denied rather than given: "never run the stories one at a time".
_DENIED = re.compile(r"(?i)\b(never|not|rather than|instead of)\b[^.;]*\bone at a time\b")


def front_matter_field(text: str, key: str) -> str:
    """The value of a flat `key:` in the page's front matter, unquoted; "" when absent."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    match = re.search(rf'(?m)^{re.escape(key)}:\s*(.*?)\s*$', parts[1])
    if not match:
        return ""
    value = match.group(1)
    return value[1:-1] if len(value) >= 2 and value[0] == value[-1] == '"' else value


def required_harnesses(field: str) -> list[str]:
    """Each sentence of `field` that names a harness and states a requirement."""
    return [s for s in _SENTENCE.split(field) if _HARNESS.search(s) and _REQUIRES.search(s)]


def skill_faults(text: str) -> list[str]:
    """What keeps SKILL.md's description and compatibility line from being harness-neutral."""
    faults = []
    for key in ("description", "compatibility"):
        value = front_matter_field(text, key)
        if not value:
            faults.append(f"SKILL.md has no {key}")
        faults += [f"{key} names a harness as required: {s!r}" for s in required_harnesses(value)]
    compatibility = front_matter_field(text, "compatibility")
    faults += [f"compatibility does not say {label}" for label, p in AGENTIC_FALLBACK.items()
               if not re.search(p, compatibility)]
    faults += [f"compatibility drops {fact!r}" for fact in KEPT_FACTS if fact not in compatibility]
    if len(compatibility) > COMPATIBILITY_LIMIT:
        faults.append(f"compatibility is {len(compatibility)} chars, over {COMPATIBILITY_LIMIT}")
    return faults


def llms_faults(text: str, root: Path = REPO) -> list[str]:
    """What keeps llms.txt from naming the six harnesses in order and linking the new pages."""
    summary = " ".join(ln.lstrip("> ").strip() for ln in text.splitlines() if ln.startswith(">"))
    faults = [f"the summary does not name {name}" for name in HARNESSES if name not in summary]
    named = [name for name in HARNESSES if name in summary]
    if sorted(named, key=summary.index) != named:
        faults.append("the summary does not name the harnesses alphabetically")
    docs = text.split("## Docs", 1)[1].split("\n## ", 1)[0] if "## Docs" in text else ""
    for page in NEW_PAGES:
        if f"]({page})" not in docs:
            faults.append(f"the Docs list does not link {page}")
        elif not (root / page).is_file():
            faults.append(f"the Docs list links {page}, which does not exist")
    return faults


def agentic_row(text: str) -> str:
    """The `--agentic` row of the `### implement` flag table; "" when there is none."""
    implement = text.split("### implement", 1)[1].split("\n### ", 1)[0] if "### implement" in text else ""
    return next((ln for ln in implement.splitlines() if ln.startswith("| `--agentic` |")), "")


def epic_faults(text: str) -> list[str]:
    """What keeps the epic help's `--agentic` row from stating the fallback without sub-agents."""
    row = agentic_row(text)
    if not row:
        return ["help/epic.md's implement table has no --agentic row"]
    return [f"the --agentic row does not say {label}" for label, p in AGENTIC_ROW.items()
            if not re.search(p, row)]


def parallel_claim_faults(label: str, claim: str) -> list[str]:
    """BG1599. What keeps `claim` from naming worktree isolation wherever it names sub-agents."""
    faults = [] if re.search(WORKTREE_SUBAGENTS, claim) else [
        f"{label} does not say sub-agents with worktree isolation"]
    if _BARE_SUBAGENTS.search(claim):
        faults.append(f"{label} names sub-agents without worktree isolation")
    return faults


def agentic_mode(text: str) -> str:
    """Step 4's Agentic mode in reference-epic.md, up to step 5; "" when there is none."""
    head = "**Agentic mode (`--agentic`):**"
    return text.split(head, 1)[1].split("\n5. **", 1)[0] if head in text else ""


def reference_fallback_faults(text: str) -> list[str]:
    """BG1599. What keeps the Agentic mode from giving the step for a harness without sub-agents."""
    mode = agentic_mode(text)
    if not mode:
        return ["reference-epic.md has no Agentic mode"]
    step = next((p for p in mode.split("\n\n") if _NO_SUBAGENTS.search(p)), "")
    if not step:
        return ["the Agentic mode has no step for a harness without sub-agents with worktree "
                "isolation"]
    faults = [f"the no-sub-agent step does not say {label}" for label, p in FALLBACK_STEP.items()
              if not re.search(p, step)]
    if _DENIED.search(step):
        faults.append("the no-sub-agent step denies the one-at-a-time run")
    return faults


def shared_words_faults(surfaces: dict[str, str]) -> list[str]:
    """BG1599. Each surface that does not state the fallback in the shared words."""
    return [f"{label} does not say {words}" for label, text in surfaces.items()
            for words, p in (("sub-agents with worktree isolation", WORKTREE_SUBAGENTS),
                             ("one at a time in dependency order", FALLBACK_WORDS))
            if not re.search(p, text)]


class SkillMetadataNeutralTests(unittest.TestCase):
    def test_skill_md_requires_no_single_harness(self) -> None:
        """AC1. Mutants: the old "Claude-Code-only" line, a harness named as required in the
        description, the fallback dropped, the Python fact dropped."""
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertEqual(skill_faults(text), [])

        compatibility = front_matter_field(text, "compatibility")
        old = text.replace(compatibility, "Requires Python 3.10+ for bundled scripts; gh CLI "
                           "(authenticated) for GitHub sync commands. Agentic wave execution "
                           "(--agentic) is Claude-Code-only.", 1)
        faults = skill_faults(old)
        self.assertIn("compatibility names a harness as required: 'Agentic wave execution "
                      "(--agentic) is Claude-Code-only.'", faults)
        self.assertIn("compatibility does not say one at a time", faults)
        description = front_matter_field(text, "description")
        needy = text.replace(description, description + " Requires Claude Code.", 1)
        self.assertEqual(skill_faults(needy),
                         ["description names a harness as required: 'Requires Claude Code.'"])
        self.assertEqual(skill_faults(text.replace("Python 3.10+", "Python 3", 1)),
                         ["compatibility drops 'Python 3.10+'"])
        self.assertEqual(skill_faults(text.replace("one at a time", "in turn", 1)),
                         ["compatibility does not say one at a time"])

    def test_llms_txt_names_six_harnesses_and_links_the_new_pages(self) -> None:
        """AC2. Mutants: Codex dropped, Cursor named before Codex, either new page unlinked."""
        text = LLMS.read_text(encoding="utf-8")
        self.assertEqual(llms_faults(text), [])

        self.assertIn("the summary does not name Codex", llms_faults(text.replace("Codex", "")))
        swapped = text.replace("Codex, Cursor", "Cursor, Codex", 1)
        self.assertEqual(llms_faults(swapped),
                         ["the summary does not name the harnesses alphabetically"])
        for page in NEW_PAGES:
            self.assertEqual(llms_faults(text.replace(f"]({page})", "](README.md)")),
                             [f"the Docs list does not link {page}"])
        self.assertEqual(llms_faults(text.replace("## Docs", "## Pages", 1)),
                         [f"the Docs list does not link {page}" for page in NEW_PAGES])
        self.assertEqual(llms_faults(text, root=REPO / "docs"),
                         [f"the Docs list links {page}, which does not exist"
                          for page in NEW_PAGES])

    def test_epic_help_states_the_agentic_fallback(self) -> None:
        """AC3. Mutants: the old row with no fallback, and no row at all."""
        text = EPIC_HELP.read_text(encoding="utf-8")
        self.assertEqual(epic_faults(text), [])

        row = agentic_row(text)
        old = text.replace(row, "| `--agentic` | Autonomous concurrent execution with wave "
                                "analysis (cross-layer only) |", 1)
        self.assertEqual(epic_faults(old), ["the --agentic row does not say sub-agents",
                                            "the --agentic row does not say one at a time",
                                            "the --agentic row does not say dependency order"])
        decoy = old.replace("\n### plan\n", f"\n### plan\n\n{row}\n", 1)
        self.assertEqual(len(epic_faults(decoy)), 3, "a row outside implement was read")
        self.assertEqual(epic_faults(text.replace(row, "", 1)),
                         ["help/epic.md's implement table has no --agentic row"])

    def test_the_parallel_claim_names_worktree_isolation(self) -> None:
        """BG1599 AC1. Mutants: each surface back to the bare "where the harness has sub-agents",
        and a second, bare mention beside the qualified one."""
        compatibility = front_matter_field(SKILL_MD.read_text(encoding="utf-8"), "compatibility")
        row = agentic_row(EPIC_HELP.read_text(encoding="utf-8"))
        for label, claim in (("compatibility", compatibility), ("the --agentic row", row)):
            with self.subTest(label):
                self.assertEqual(parallel_claim_faults(label, claim), [])
                bare = re.sub(WORKTREE_SUBAGENTS, "sub-agents", claim)
                self.assertEqual(parallel_claim_faults(label, bare),
                                 [f"{label} does not say sub-agents with worktree isolation",
                                  f"{label} names sub-agents without worktree isolation"])
                self.assertEqual(parallel_claim_faults(label, claim + " Uses sub-agents."),
                                 [f"{label} names sub-agents without worktree isolation"])

    def test_reference_epic_states_the_no_subagent_fallback(self) -> None:
        """BG1599 AC2. Mutants: the step removed, moved into Sequential mode, its condition
        flipped, denied, keeping the prerequisite, or missing dependency order (also with the
        words moved to another paragraph), the plain-`epic implement` link or the prerequisite it
        waives; and either other surface losing the shared words."""
        text = REFERENCE_EPIC.read_text(encoding="utf-8")
        self.assertEqual(reference_fallback_faults(text), [])
        step = next(p for p in agentic_mode(text).split("\n\n") if _NO_SUBAGENTS.search(p))
        none = ["the Agentic mode has no step for a harness without sub-agents with worktree "
                "isolation"]
        self.assertEqual(reference_fallback_faults(text.replace(step, "", 1)), none)
        moved = text.replace(step, "", 1).replace(
            "**Sequential mode (default):**", f"**Sequential mode (default):**\n\n{step}", 1)
        self.assertEqual(reference_fallback_faults(moved), none)
        flipped = text.replace(step, step.replace("has no sub-agents", "has sub-agents", 1), 1)
        self.assertEqual(reference_fallback_faults(flipped), none)
        denied = text.replace(step, step.replace("run the stories", "never run the stories", 1), 1)
        self.assertEqual(reference_fallback_faults(denied),
                         ["the no-sub-agent step denies the one-at-a-time run"])
        kept = text.replace(step, step.replace("then do not apply", "still apply", 1), 1)
        self.assertEqual(reference_fallback_faults(kept), [
            "the no-sub-agent step does not say that the prior `epic plan --agentic` does not apply"])
        scattered = text.replace(step, step.replace(" in dependency order", "", 1), 1).replace(
            "   d. **Wait for All Stories", "   Run them one at a time in dependency order.\n\n"
            "   d. **Wait for All Stories", 1)
        self.assertEqual(reference_fallback_faults(scattered), [
            "the no-sub-agent step does not say one at a time in dependency order"])
        for label, cut in (("one at a time in dependency order", " in dependency order"),
                           ("as plain `epic implement` does", "as plain `epic implement` does"),
                           ("that the prior `epic plan --agentic` does not apply",
                            "`epic plan --agentic`")):
            with self.subTest(label):
                self.assertIn(cut, step)
                self.assertEqual(reference_fallback_faults(
                    text.replace(step, step.replace(cut, "", 1), 1)),
                    [f"the no-sub-agent step does not say {label}"])
        self.assertEqual(reference_fallback_faults(text.replace("**Agentic mode", "**Wave mode")),
                         ["reference-epic.md has no Agentic mode"])

        compatibility = front_matter_field(SKILL_MD.read_text(encoding="utf-8"), "compatibility")
        row = agentic_row(EPIC_HELP.read_text(encoding="utf-8"))
        surfaces = {"compatibility": compatibility, "the --agentic row": row,
                    "the no-sub-agent step": step}
        self.assertEqual(shared_words_faults(surfaces), [])
        for label in ("compatibility", "the --agentic row"):
            for words, drop in (("one at a time in dependency order", " in dependency order"),
                                ("sub-agents with worktree isolation", " with worktree isolation")):
                with self.subTest(label, words=words):
                    cut = dict(surfaces, **{label: surfaces[label].replace(drop, "")})
                    self.assertEqual(shared_words_faults(cut), [f"{label} does not say {words}"])


if __name__ == "__main__":
    unittest.main()
