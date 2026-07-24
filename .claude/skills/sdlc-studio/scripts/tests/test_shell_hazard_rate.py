"""US0362: the detector's post-damage half, and the number that says how much it misses.

The three shipped hazard shapes all detect a metacharacter that SURVIVED. The corruptions
that prompted this work are the opposite case: the substitution COMPLETED, so the backticks
and everything between them are gone and the stored text carries no metacharacter at all.
This module holds the four real corruptions as a corpus, measures the extended detector
against them, and asserts the COUNT it catches - not a status word, and not a constant that
could stay green while the detector rotted.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import workspace  # noqa: E402 - the shared "am I in the dev repo?" check


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load("file_finding")

#: The four corruptions measured during RUN-01KXVYGR, kept here so the evidence lives in the
#: repository rather than in a run log. Each entry carries `stored` (what the artefact ended
#: up holding), `written` (what the author typed), `lost` (the backticked token(s) the shell
#: removed) and `artefact` (where the damage is recorded or was repaired).
#:
#: Provenance, stated plainly so a reader can check it rather than take it: entry 1's `stored`
#: text is quoted verbatim in CR0351. The other three were repaired before their artefact was
#: committed, so their `stored` text is reconstructed the only way it can be - by deleting the
#: backticked token from the repaired sentence, which is exactly the edit the shell performed.
#: `test_the_corpus_holds_the_four_real_corruptions_with_what_was_lost` re-derives every
#: `stored` string from its `written` string, so a corpus entry cannot drift into fiction.
CORRUPTION_CORPUS: tuple[dict, ...] = (
    {
        "id": "summary-truncated-before-a-full-stop",
        "artefact": "sdlc-studio/change-requests/CR0351-file-finding-silently-accepts-shell-"
                    "mangled-text-so.md",
        "written": "US0251 AC2 runs `python3 .claude/skills/sdlc-studio/scripts/"
                   "command_audit.py --write --check-tools`.",
        "lost": ("`python3 .claude/skills/sdlc-studio/scripts/command_audit.py --write "
                 "--check-tools`",),
        "stored": "US0251 AC2 runs .",
    },
    {
        "id": "two-reproduction-commands-deleted-mid-sentence",
        "artefact": "sdlc-studio/bugs/BG0240-lessons-py-summary-out-and-loop-guard-py.md",
        "written": "Run `python3 lessons.py summary --root <proj> --out summary-out.md` from a "
                   "foreign cwd, then `python3 loop_guard.py record` from a subdirectory.",
        "lost": ("`python3 lessons.py summary --root <proj> --out summary-out.md`",
                 "`python3 loop_guard.py record`"),
        "stored": "Run  from a foreign cwd, then  from a subdirectory.",
    },
    {
        "id": "the-command-the-bug-was-about-was-executed-not-stored",
        "artefact": "sdlc-studio/bugs/BG0242-35-bare-subprocess-git-calls-in-8-test.md",
        "written": "an unscrubbed fixture wrote its own tree into the real repo's pending index "
                   "under `git commit -a`, reproduced on three victim repos.",
        "lost": ("`git commit -a`",),
        "stored": "an unscrubbed fixture wrote its own tree into the real repo's pending index "
                  "under , reproduced on three victim repos.",
    },
    {
        # The one that cannot be caught: the token opened the sentence, so its removal left
        # grammatical text with no mark on it at all.
        "id": "the-lost-token-opened-the-sentence",
        "artefact": "sdlc-studio/bugs/BG0240-lessons-py-summary-out-and-loop-guard-py.md",
        "written": "`loop_guard.py` writes a stray workspace beside the cwd and exits 0.",
        "lost": ("`loop_guard.py`",),
        "stored": "writes a stray workspace beside the cwd and exits 0.",
    },
)

#: The corpus entry no fingerprint can reach, named here so the miss is a stated limit rather
#: than an unexplained gap in a count.
UNDETECTABLE_IN_PRINCIPLE = "the-lost-token-opened-the-sentence"

#: Artefacts whose own prose QUOTES corrupted text on purpose, so a finding there is a TRUE
#: positive and excluding them is not a convenience. The exclusion is a debt ratchet like
#: KNOWN_PROSE_WRITER_GAPS: `test_the_excluded_artefact_is_excluded_for_a_true_positive`
#: fails if the quoted damage is ever repaired, rather than leaving a stale entry behind.
QUOTES_CORRUPTED_TEXT = {
    "CR0409": "records the goal-review corruption verbatim, double space and all - the stored "
              "QA note that lost the word it was about",
}

#: The artefact sections whose bodies are author prose rather than structure.
_PROSE_SECTIONS = ("## summary", "## impact", "## proposed fix", "## steps to reproduce",
                   "## notes")
_FENCE = re.compile(r"^\s*```")
_ARTEFACT_DIRS = ("bugs", "change-requests", "stories", "rfcs", "epics", "retros", "handoffs",
                  "test-specs", "reviews", "decisions", "personas")


def legitimate_prose_sample(repo: Path) -> list[tuple[str, str]]:
    """(artefact path, prose) for every prose section of every artefact in the workspace.

    A POPULATION, not a hand-picked sample: every artefact of every type, so the false-positive
    rate cannot be bought by choosing agreeable fields. Fenced blocks are dropped because a
    fenced block is verbatim code the author bracketed deliberately, not prose.
    """
    out: list[tuple[str, str]] = []
    for d in _ARTEFACT_DIRS:
        dd = repo / "sdlc-studio" / d
        if not dd.is_dir():
            continue
        for p in sorted(dd.glob("*.md")):
            if p.name == "_index.md" or any(p.name.startswith(k) for k in QUOTES_CORRUPTED_TEXT):
                continue
            grab = fence = False
            buf: list[str] = []
            for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if ln.startswith("## "):
                    if buf:
                        out.append((str(p), "\n".join(buf).strip()))
                        buf = []
                    grab = ln.strip().lower() in _PROSE_SECTIONS
                    fence = False
                    continue
                if not grab:
                    continue
                if _FENCE.match(ln):
                    fence = not fence
                    continue
                if not fence:
                    buf.append(ln)
            if buf:
                out.append((str(p), "\n".join(buf).strip()))
    return [(p, t) for p, t in out if t]


class CorruptionCorpusTests(unittest.TestCase):
    """AC1: the four corruptions are recorded evidence, each with what the shell removed."""

    def test_the_corpus_holds_the_four_real_corruptions_with_what_was_lost(self) -> None:
        self.assertEqual(len(CORRUPTION_CORPUS), 4)
        self.assertEqual(len({e["id"] for e in CORRUPTION_CORPUS}), 4, "duplicate corpus id")
        for e in CORRUPTION_CORPUS:
            with self.subTest(e["id"]):
                for key in ("stored", "written", "artefact"):
                    self.assertTrue(e[key].strip(), f"{e['id']} has an empty {key}")
                self.assertTrue(e["lost"], f"{e['id']} names no lost token")
                # Every lost token is a BACKTICKED span - that is what a shell substitutes
                # away, and an entry naming a plain word would be a different defect.
                for token in e["lost"]:
                    self.assertTrue(token.startswith("`") and token.endswith("`"),
                                    f"{e['id']} lost token is not a backticked span: {token!r}")
                    self.assertIn(token, e["written"],
                                  f"{e['id']} lost a token its written text never held")
                # The corpus checks itself: deleting the lost token(s) from what was WRITTEN
                # must reproduce what was STORED, character for character. A hand-typed
                # `stored` string that drifts from its `written` string fails here.
                damaged = e["written"]
                for token in e["lost"]:
                    damaged = damaged.replace(token, "")
                self.assertEqual(damaged.strip(), e["stored"].strip(),
                                 f"{e['id']}: deleting the lost token(s) from the written text "
                                 f"does not reproduce the stored text")
                self.assertNotEqual(e["stored"], e["written"], e["id"])

    def test_every_corpus_entry_names_an_artefact_that_exists(self) -> None:
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for e in CORRUPTION_CORPUS:
            with self.subTest(e["id"]):
                self.assertTrue((workspace.REPO / e["artefact"]).is_file(),
                                f"{e['id']} cites {e['artefact']}, which is not in the repository")


class MeasuredCatchRateTests(unittest.TestCase):
    """AC2/AC3: what the extended detector catches over the corpus, as a number, and what it
    costs over the legitimate population."""

    @staticmethod
    def _findings(text: str) -> list[tuple[str, str]]:
        return ff.shell_hazards({"summary": text}, keys=("summary",))

    def test_the_catch_count_over_the_corpus_is_asserted_as_a_number(self) -> None:
        caught = [e["id"] for e in CORRUPTION_CORPUS if self._findings(e["stored"])]
        missed = [e["id"] for e in CORRUPTION_CORPUS if not self._findings(e["stored"])]
        self.assertEqual(
            len(caught), 3,
            f"the detector caught {len(caught)} of {len(CORRUPTION_CORPUS)} recorded "
            f"corruptions (caught: {caught}; missed: {missed}). The ONE miss this repository "
            f"accepts is {UNDETECTABLE_IN_PRINCIPLE!r}, which is undetectable in principle: a "
            f"token lost from the START of a sentence leaves grammatical text behind, carrying "
            f"no mark for any fingerprint to find. Any other number means the detector changed "
            f"- re-measure it, do not re-label it")
        self.assertEqual(missed, [UNDETECTABLE_IN_PRINCIPLE],
                         f"the miss moved: {missed}. The recorded limit is that ONE entry")
        # Each of the three post-damage fingerprints earns its place: the three caught entries
        # are caught by three DIFFERENT findings, so none of them is dead weight carried by a
        # sibling that would have caught the entry anyway.
        first_finding = {e["id"]: self._findings(e["stored"])[0][1]
                         for e in CORRUPTION_CORPUS if self._findings(e["stored"])}
        self.assertEqual(len(set(first_finding.values())), 3,
                         f"two entries were caught by the same fingerprint: {first_finding}")

    def test_the_stored_text_carries_no_metacharacter_for_the_shipped_shapes_to_find(self) -> None:
        # The reason this story exists: the substitution COMPLETED, so the three shipped shapes
        # (unbalanced backtick, surviving `$(`, trailing backslash) see nothing at all.
        for e in CORRUPTION_CORPUS:
            with self.subTest(e["id"]):
                self.assertNotIn("`", e["stored"])
                self.assertNotIn("$(", e["stored"])
                self.assertFalse(e["stored"].rstrip().endswith("\\"))

    def test_no_legitimate_artefact_field_is_flagged(self) -> None:
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        sample = legitimate_prose_sample(workspace.REPO)
        chars = sum(len(t) for _, t in sample)
        # Non-vacuity first: a sample that shrank to nothing would pass this test by having
        # nothing to flag, which is the failure mode the whole module exists to refuse.
        self.assertGreaterEqual(len(sample), 800, "the legitimate sample collapsed")
        self.assertGreaterEqual(chars, 400_000, "the legitimate sample collapsed")
        flagged = [(path, what) for path, text in sample for _, what in self._findings(text)]
        self.assertEqual(
            flagged[:5], [],
            f"{len(flagged)} legitimate artefact field(s) of {len(sample)} were flagged. A "
            f"false positive trains a reader to ignore the warning, so a new fingerprint must "
            f"buy its catch rate without one")

    def test_a_flag_argument_is_not_read_as_a_hole(self) -> None:
        """A discriminating pair: `--root .` is a spelling, and the same sentence without the
        flag is a hole. Without the flag guard the first reads as damage, which is the false
        positive that would train a reader to ignore the warning."""
        self.assertEqual(self._findings("the writers all default to --root ."), [])
        self.assertEqual(len(self._findings("the writers all default to the .")), 1)

    def test_the_excluded_artefact_is_excluded_for_a_true_positive(self) -> None:
        """The exclusion list is a debt ratchet, not a convenience: each entry must still hold
        text the detector genuinely flags, or the entry is stale and must go."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for prefix, why in QUOTES_CORRUPTED_TEXT.items():
            with self.subTest(prefix):
                self.assertTrue(why.strip(), f"{prefix} is excluded with no reason")
                files = [p for d in _ARTEFACT_DIRS
                         for p in (workspace.REPO / "sdlc-studio" / d).glob(f"{prefix}*.md")]
                self.assertTrue(files, f"{prefix} is excluded but no such artefact exists")
                hits = [w for p in files
                        for _, w in self._findings(p.read_text(encoding="utf-8"))]
                self.assertTrue(hits, f"{prefix} no longer carries text the detector flags - "
                                      f"the quoted damage was repaired; drop the exclusion")


if __name__ == "__main__":
    unittest.main()
