"""BG0816: the skill's docs name the Three Amigos the resolver loads, not the retired names.

`persona_resolve.py resolve --seat <s> --render review` seats the amigos from the shipped cards
(or a project seat card that overrides one). The retired names Sarah Chen, Marcus Johnson and
Priya Sharma survive only as sample personas, and each surviving mention sits inside a marked
region:

    <!-- sample-personas -->
    ...visible text saying these are sample personas, not the amigos...
    <!-- /sample-personas -->

These tests read THIS repository's shipped docs and AGENTS.md, as the criteria name them.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# parents: [0] tests [1] scripts [2] the shipped skill [3] skills [4] .claude [5] the repository.
SKILL = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
RESOLVER = SKILL / "scripts" / "persona_resolve.py"
SEATS = ("product", "engineering", "qa")

RETIRED = re.compile(r"\b(Sarah\s+Chen|Marcus\s+Johnson|Priya\s+Sharma)\b", re.I)
OPEN, CLOSE = "<!-- sample-personas -->", "<!-- /sample-personas -->"
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")
# A top-level numbered step ("4. ", "4b. ") or a rule starts a new passage, as a heading does.
STEP = re.compile(r"^\d+[a-z]?\. ")
RULE = re.compile(r"^---\s*$")
COMMENT = re.compile(r"<!--.*?-->", re.S)
# The visible disclaimer each region carries: sample personas, and not the amigos.
SAMPLE = re.compile(r"\bsample\b.{0,40}?\bpersonas?\b", re.I)
NOT_AMIGO = re.compile(r"\bnot\b.{0,40}?\bamigos?\b", re.I)
SENTENCE = re.compile(r"(?<=[.;:!?])\s+")


def _docs() -> list[Path]:
    return sorted(SKILL.rglob("*.md"))


def _walk(lines: list[str]) -> list[tuple[list[str], str | None]]:
    """Per line: the heading chain above it and the passage head (the nearest step or heading
    line), both read outside code fences."""
    chain: list[tuple[int, str]] = []
    head: str | None = None
    fenced = False
    out = []
    for line in lines:
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced:
            m = HEADING.match(line)
            if m:
                level = len(m.group(1))
                chain = [c for c in chain if c[0] < level] + [(level, m.group(2))]
                head = line
            elif STEP.match(line):
                head = line
            elif RULE.match(line):
                head = None
        out.append(([c[1] for c in chain], head))
    return out


def _regions(rel: str, lines: list[str]) -> list[tuple[int, int]]:
    """(open line, close line) pairs; an unbalanced marker is a failure, not a region."""
    spans, start = [], None
    for i, line in enumerate(lines):
        if line.strip() == OPEN:
            assert start is None, f"{rel}:{i + 1}: sample-personas region opened twice"
            start = i
        elif line.strip() == CLOSE:
            assert start is not None, f"{rel}:{i + 1}: sample-personas close with no open"
            spans.append((start, i))
            start = None
    assert start is None, f"{rel}:{start + 1}: sample-personas region never closed"
    return spans


def _resolved_dirs() -> set[Path]:
    """Every directory the shipped resolver loads a seat card from: this repository's own seats,
    and the shipped defaults it falls back to in a tree with no seat cards."""
    dirs = set()
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "sdlc-studio").mkdir()
        for root in (REPO, Path(tmp)):
            for seat in SEATS:
                r = subprocess.run([sys.executable, str(RESOLVER), "resolve", "--seat", seat,
                                    "--render", "review", "--path-only", "--root", str(root)],
                                   capture_output=True, text=True, check=True)
                dirs.add(Path(r.stdout.strip()).resolve().parent)
    return dirs


class AmigoNameTests(unittest.TestCase):

    def test_no_amigo_passage_names_a_retired_seat(self) -> None:
        """AC1. MUTANTS: the rc.1 docs (the bug fix step, consult team table and chat workshop
        name the retired amigos, no region); a region wrapped round an amigo passage (the bug
        fix step's persona bullets marked sample); a region whose disclaimer is gone or hidden
        in a comment; an unclosed region; a name in a code fence under a Three Amigos heading;
        a region wrapped round the --amigos chat workshop, whose headings never say amigo."""
        hits = 0
        for path in _docs():
            rel = str(path.relative_to(SKILL))
            lines = path.read_text(encoding="utf-8").splitlines()
            spans = _regions(rel, lines)
            where = _walk(lines)
            for i, line in enumerate(lines):
                for m in RETIRED.finditer(line):
                    hits += 1
                    self.assertTrue(any(a < i < b for a, b in spans),
                                    f"{rel}:{i + 1}: {m.group(0)} outside a sample-personas "
                                    "region; an amigo is named by its role label")
            for a, b in spans:
                # The headings and passage heads over the region's opening and every line in it.
                heads = where[a][0] + [h for _, h in where[a:b] if h]
                heads += [c[-1] for c, _ in where[a + 1:b] if c]
                for h in heads:
                    self.assertNotRegex(h, r"(?i)amigo", f"{rel}:{a + 1}: a sample-personas "
                                        f"region sits in an amigo passage ({h!r})")
                visible = " ".join(COMMENT.sub(" ", "\n".join(lines[a + 1:b])).split())
                self.assertRegex(visible, SAMPLE, f"{rel}:{a + 1}: region never says its "
                                 "names are sample personas")
                self.assertRegex(visible, NOT_AMIGO, f"{rel}:{a + 1}: region never says its "
                                 "names are not the amigos")
                # Past the disclaimer, a sample region says nothing of the amigos: an amigo
                # passage (a --amigos workshop, a Three Amigos step) cannot be marked sample.
                rest = " ".join(s for s in SENTENCE.split(visible) if not NOT_AMIGO.search(s))
                self.assertNotRegex(rest, r"(?i)amigo", f"{rel}:{a + 1}: a sample-personas "
                                    "region speaks of the amigos beyond its disclaimer")
        self.assertGreater(hits, 0, "the scan found no retired name: it read nothing")

    @unittest.skipUnless((REPO / "AGENTS.md").is_file(), "names this repository's AGENTS.md")
    def test_agents_md_names_the_real_seat_directory(self) -> None:
        """AC2. MUTANTS: the rc.1 row (.claude/skills/sdlc-studio/personas/seats/, which does not
        exist); a row naming a directory that exists but holds no card the resolver loads
        (templates/personas/); the row deleted."""
        text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        start = text.index("## Where things live")
        end = text.index("\n## ", start + 1)
        rows = [r for r in text[start:end].splitlines()
                if r.startswith("|") and re.search(r"(?i)amigo", r)]
        self.assertTrue(rows, "AGENTS.md 'Where things live' has no amigo seat row")
        loaded = _resolved_dirs()
        for row in rows:
            dirs = [d for d in re.findall(r"`([^`]+/)`", row)]
            self.assertTrue(dirs, f"the amigo row names no directory: {row}")
            for d in dirs:
                p = (REPO / d).resolve()
                self.assertTrue(p.is_dir(), f"AGENTS.md names {d}, which does not exist")
                self.assertIn(p, loaded, f"AGENTS.md names {d}, which persona_resolve.py "
                              f"never loads a seat from; it loads from {sorted(map(str, loaded))}")


if __name__ == "__main__":
    unittest.main()
