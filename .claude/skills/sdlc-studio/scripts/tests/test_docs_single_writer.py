"""Doc invariants for the single-writer rule in reference-sprint.md / reference-review.md.

Why this module exists rather than four `grep` Verify lines: a substring grep is a
presence check, and presence does not establish meaning. The four criteria this locks
were originally evidenced by `grep "green"`, `grep "symlink"`, `grep "window"` and one
distinctive phrase; a reviewer replaced the documentation with prose asserting the
OPPOSITE of every criterion and all four greps still passed, because each word survives
inside its own denial. `grep` is exempt from the vacuity gate, so nothing flagged it.

The shape used here is deliberately two-sided, and the positive half carries the weight:

  REQUIRED  a specific whole sentence, plus the facts that have to sit beside it (the
            ceremony commits, the incident, the mechanism, the command). Negated prose
            fails on this half alone, structurally - it cannot contain the asserted
            sentence and assert the opposite at the same time.
  FORBIDDEN a curated family of contradicting phrasings. This half is belt-and-braces.
            It is a blocklist, not a semantic proof, and it is honest about that: a new
            way of writing the same contradiction has to be added to it.

Both reference files are part of the shipped skill, so these checks run identically from
an installed copy. Prose is normalised (emphasis and code markers dropped, whitespace
collapsed) before matching, so a required sentence wrapped across two lines still matches
- which a line-oriented grep cannot do.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared loader
import loader  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[2]
SPRINT_DOC = SKILL_DIR / "reference-sprint.md"
REVIEW_DOC = SKILL_DIR / "reference-review.md"


# -----------------------------------------------------------------------------
# Text handling
# -----------------------------------------------------------------------------

def normalise(text: str) -> str:
    """Drop markdown emphasis / code markers and collapse whitespace."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).strip()


def paragraphs(raw: str) -> list[str]:
    """Blank-line separated blocks, each normalised."""
    return [normalise(p) for p in re.split(r"\n\s*\n", raw) if normalise(p)]


def sentences(raw: str) -> list[str]:
    """Every sentence in the document, normalised.

    Split on terminal punctuation followed by whitespace only, so `mutation.py window`
    and `retro.py` stay whole.
    """
    out: list[str] = []
    for para in paragraphs(raw):
        out.extend(s for s in re.split(r"(?<=[.!?])\s+", para) if s)
    return out


def _mentioning(raw: str, pattern: str) -> list[str]:
    """Sentences matching `pattern` (case-insensitive)."""
    rx = re.compile(pattern, re.I)
    return [s for s in sentences(raw) if rx.search(s)]


def _requires(raw: str, needle: str, where: str, ac: str) -> list[str]:
    """One failure string when `needle` (a regex) is absent from the normalised text."""
    if re.search(needle, normalise(raw), re.I):
        return []
    return [f"{ac}: {where} does not state: /{needle}/"]


def _forbids(raw: str, pattern: str, why: str, ac: str) -> list[str]:
    """One failure string per sentence matching a contradicting phrasing."""
    return [f"{ac}: contradicting sentence ({why}): {s!r}"
            for s in _mentioning(raw, pattern)]


# -----------------------------------------------------------------------------
# The CLI the prose points at (AC4's anti-drift half)
# -----------------------------------------------------------------------------

def window_cli() -> tuple[set[str], set[str]]:
    """The real `mutation.py window` verbs and flags, read from its argparse.

    Prose naming a command the tool does not have is drift, and drift is exactly what
    AC4 is written to prevent, so the prose is checked against the parser rather than
    against another copy of the prose.
    """
    mutation = loader.load_script("mutation")
    parser = mutation.build_parser()
    subs = [a for a in parser._actions if hasattr(a, "choices") and isinstance(a.choices, dict)]
    window = subs[0].choices["window"]
    verbs: set[str] = set()
    flags: set[str] = set()
    for action in window._actions:
        if action.option_strings:
            flags.update(action.option_strings)
        elif action.choices:
            verbs.update(action.choices)
    return verbs, flags


_CMD_RE = re.compile(r"mutation\.py window ([a-z|]+)((?:\s+--[a-z-]+(?:\s+<[^>]*>)?)*)")


def cited_commands(raw: str) -> list[tuple[str, list[str]]]:
    """Every `mutation.py window ...` invocation the prose cites: (verb, flags)."""
    out: list[tuple[str, list[str]]] = []
    for verbs, tail in _CMD_RE.findall(normalise(raw)):
        flags = re.findall(r"--[a-z-]+", tail)
        out.extend((verb, flags) for verb in verbs.split("|") if verb)
    return out


# -----------------------------------------------------------------------------
# The four criteria
# -----------------------------------------------------------------------------

#: The ceremony commits an author makes during a review, which AC1 requires named
#: beside the rule rather than left to the reader.
CEREMONY_TERMS = ("retro", "review anchor", "findings", "CHANGELOG")


def check_ac1(sprint: str) -> list[str]:
    """The single-writer rule covers review time, not only a build-time mutation run."""
    ac = "AC1"
    claim = (r"an independent review is a concurrent-writer window too, "
             r"and it is the more dangerous of the two")
    bad = _requires(sprint, claim, "reference-sprint.md", ac)
    if not bad:
        holder = next(p for p in paragraphs(sprint) if re.search(claim, p, re.I))
        missing = [t for t in CEREMONY_TERMS if t.lower() not in holder.lower()]
        if missing:
            bad.append(f"{ac}: the rule states the window but does not name the ceremony "
                       f"commits made during one: {', '.join(missing)}")
    bad += _forbids(sprint, r"concurrent-writer window[^.]*\b(den(y|ies|ied)|no such thing)",
                    "denies the window it is meant to state", ac)
    bad += _forbids(sprint, r"(is|are|was) (not|never) a concurrent-writer window",
                    "denies the window it is meant to state", ac)
    return bad


def check_ac2(sprint: str, review: str) -> list[str]:
    """The documented mechanism is the corrected one: a redirect through a symlink."""
    ac = "AC2"
    bad: list[str] = []
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        joint = [s for s in sentences(raw)
                 if re.search(r"redirect", s, re.I) and re.search(r"symlink", s, re.I)]
        if not joint:
            bad.append(f"{ac}: {name} has no sentence naming the redirect AND the symlink "
                       f"as one mechanism")
        bad += _forbids(raw, r"\bmutants?\b[^.]*\b(caused|was the cause)\b|"
                             r"\b(caused by|the cause was|because of|due to)\b[^.]*\bmutants?\b",
                        "attributes the incident to a mutant", ac)
        bad += _forbids(raw, r"\bno symlink\b|\bsymlink[^.]*\b(was|were) not involved",
                        "denies the symlink mechanism", ac)
    return bad


def check_ac3(sprint: str, review: str) -> list[str]:
    """A passing gate is not evidence that no concurrent write is staged."""
    ac = "AC3"
    bad = _requires(sprint, r"a passing gate does not establish that no concurrent write is "
                            r"staged", "reference-sprint.md", ac)
    bad += _requires(review, r"green suite is (not|never) evidence the tree is clean",
                     "reference-review.md", ac)
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        # Polarity, not presence: every claim about what a green run shows must be negated.
        for match in re.finditer(r"evidence the tree is clean", normalise(raw), re.I):
            lead = normalise(raw)[max(0, match.start() - 30):match.start()]
            if not re.search(r"\b(not|never|no)\b", lead, re.I):
                bad.append(f"{ac}: {name} claims a green run IS evidence the tree is clean: "
                           f"{lead.strip()!r}")
        bad += _forbids(raw, r"\bdoes establish\b",
                        "asserts a gate establishes what the rule says it cannot", ac)
    return bad


def check_ac4(sprint: str, review: str, cli: tuple[set[str], set[str]] | None = None) -> list[str]:
    """Both files point at the declared-window guard, and cite it as it really is."""
    ac = "AC4"
    verbs, flags = cli if cli is not None else window_cli()
    bad = _requires(sprint, r"mutation\.py window open --owner", "reference-sprint.md", ac)
    bad += _requires(sprint, r"mutation\.py window close --owner", "reference-sprint.md", ac)
    bad += _requires(sprint, r"the enforcement path is the declared window",
                     "reference-sprint.md", ac)
    bad += _requires(review, r"mutation\.py window open\|close", "reference-review.md", ac)
    for name, raw in (("reference-sprint.md", sprint), ("reference-review.md", review)):
        for verb, cited in cited_commands(raw):
            if verb not in verbs:
                bad.append(f"{ac}: {name} cites `mutation.py window {verb}`, which the tool "
                           f"does not have (has: {', '.join(sorted(verbs))})")
            for flag in cited:
                if flag not in flags:
                    bad.append(f"{ac}: {name} cites `{flag}` on `window {verb}`, which the "
                               f"tool does not accept")
        bad += _forbids(raw, r"no such thing as a[^.]*window|windows? (do|does) not exist",
                        "denies the guard the rule points at", ac)
    return bad


def check_all(sprint: str, review: str,
              cli: tuple[set[str], set[str]] | None = None) -> dict[str, list[str]]:
    """Every criterion, keyed by AC id."""
    return {"AC1": check_ac1(sprint),
            "AC2": check_ac2(sprint, review),
            "AC3": check_ac3(sprint, review),
            "AC4": check_ac4(sprint, review, cli)}


def read_docs(skill_dir: Path = SKILL_DIR) -> tuple[str, str]:
    """The two shipped reference files, as text."""
    return ((skill_dir / "reference-sprint.md").read_text(encoding="utf-8"),
            (skill_dir / "reference-review.md").read_text(encoding="utf-8"))


# -----------------------------------------------------------------------------
# The negated prose these checks exist to catch
# -----------------------------------------------------------------------------
# Verbatim from the review that rejected the original grep evidence. Held here as data,
# never written to disk in this tree: every check below must go RED on it, or the
# criterion it belongs to is once again evidenced by nothing.

NEGATED_SPRINT = """## The single-writer rule {#single-writer}

There is no such thing as a window here, and a review is a concurrent-writer window is a
phrase we deny. Stage whatever you like; git add -A is fine during a review.
"""

NEGATED_REVIEW = """**Single-writer during a review.** A green gate DOES establish that no
concurrent write is staged, and the RUN-01KY321Q incident was caused by a stale
hand-applied mutant; no symlink was involved, so a green suite is evidence the tree is
clean.
"""


class SingleWriterDocTests(unittest.TestCase):
    """GREEN against the shipped documentation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sprint, cls.review = read_docs()
        cls.cli = window_cli()

    def test_the_rule_covers_review_time_and_names_the_ceremony_commits(self) -> None:
        self.assertEqual([], check_ac1(self.sprint))

    def test_the_mechanism_documented_is_the_redirect_through_a_symlink(self) -> None:
        self.assertEqual([], check_ac2(self.sprint, self.review))

    def test_a_passing_gate_is_documented_as_no_evidence_of_a_clean_tree(self) -> None:
        self.assertEqual([], check_ac3(self.sprint, self.review))

    def test_both_files_cite_the_window_guard_as_the_tool_really_offers_it(self) -> None:
        self.assertEqual([], check_ac4(self.sprint, self.review, self.cli))


class NegatedProseTests(unittest.TestCase):
    """RED against prose asserting the opposite of each criterion.

    This is the class the original `grep` evidence lacked. Without it, a checker that
    passes on the shipped files proves only that the files exist.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.cli = window_cli()

    def test_ac1_rejects_a_denial_of_the_review_window(self) -> None:
        self.assertTrue(check_ac1(NEGATED_SPRINT))

    def test_ac2_rejects_blaming_a_staged_mutant(self) -> None:
        self.assertTrue(check_ac2(NEGATED_SPRINT, NEGATED_REVIEW))

    def test_ac3_rejects_a_green_gate_treated_as_proof_of_a_clean_tree(self) -> None:
        self.assertTrue(check_ac3(NEGATED_SPRINT, NEGATED_REVIEW))

    def test_ac4_rejects_prose_that_names_no_window_command(self) -> None:
        self.assertTrue(check_ac4(NEGATED_SPRINT, NEGATED_REVIEW, self.cli))

    def test_every_criterion_is_red_on_the_negated_pair(self) -> None:
        failures = check_all(NEGATED_SPRINT, NEGATED_REVIEW, self.cli)
        self.assertEqual([], [ac for ac, msgs in failures.items() if not msgs])

    def test_a_ceremony_list_stripped_from_the_rule_is_caught(self) -> None:
        # The statement survives, the facts beside it do not: presence alone is not enough.
        thin = ("**An independent review is a concurrent-writer window too, and it is the "
                "more dangerous of the two.** Be careful.\n")
        self.assertTrue(check_ac1(thin))

    def test_a_command_the_tool_does_not_have_is_caught(self) -> None:
        sprint, review = read_docs()
        invented = sprint.replace("window close --owner", "window unlock --owner")
        self.assertTrue(check_ac4(invented, review, self.cli))

    def test_a_flag_the_tool_does_not_accept_is_caught(self) -> None:
        sprint, review = read_docs()
        invented = sprint.replace("window open --owner", "window open --holder")
        self.assertTrue(check_ac4(invented, review, self.cli))


if __name__ == "__main__":
    unittest.main()
