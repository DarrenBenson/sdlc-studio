"""BG0675: the corpus tier shift the Points fix caused is recorded, and recorded in a frame.

Removing `Points` from `route.estimate`'s `spec` subscore moves units between the light and full
review tiers. The delivery measured how many, over every story and bug, before the fix and after
it, and wrote the figure into the bug. A figure recomputed against the live corpus un-verifies
itself as the corpus grows (BG0234), so this holds the FRAME instead: the named commit is an
ancestor of HEAD, its estimator is the pre-fix one, its population is the one counted, and the
split adds up. K itself is not recomputed - a corpus pass costs minutes - and a reviewer reads it
against the recorded counts.

A shallow clone cannot see the named commit, so only the sha-bound checks skip there, by name.
"""
# The subject is the recorded figure, not a module: no `tools/` script sits behind this file.
# test-census-subject: sdlc-studio/bugs/BG0675-an-author-declared-points-value-sets-a-unit.md
from __future__ import annotations

import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load(REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py", "_tsr_gitutil")
BUG_GLOB = "sdlc-studio/bugs/BG0675-*.md"
ROUTE = ".claude/skills/sdlc-studio/scripts/route.py"
#: The pre-fix size-to-spec expression. The fix removes it, so a post-fix commit lacks it.
PRE_FIX_EXPRESSION = "story_points / max_points"
#: The population: every story and bug directly under its directory (archive and `_index.md` out).
POPULATION = re.compile(r"^sdlc-studio/(?:stories/US[^/]*|bugs/BG[^/]*)\.md$")
_N = r"(\d[\d,]*)"
LINE = re.compile(
    rf"^- \*\*Tier shift:\*\* {_N} of {_N} units change tier \({_N} light to full, {_N} full to "
    rf"light\); before {_N} light / {_N} full, after {_N} light / {_N} full; measured at "
    r"`?([0-9a-f]{7,40})`?\s*$")


def _section(text: str) -> str | None:
    m = re.search(r"^## Tier Shift[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else None


def parse_record(text: str) -> tuple[dict | None, list[str]]:
    """(figures, problems) for a bug's `## Tier Shift` section. Figures are None when the
    section or its one line is absent; problems name every arithmetic rule the line breaks."""
    body = _section(text)
    if body is None:
        return None, ["no `## Tier Shift` section"]
    lines = [ln for ln in body.splitlines() if ln.startswith("- **Tier shift:**")]
    if len(lines) != 1:
        return None, [f"the section carries {len(lines)} `Tier shift` lines, not one"]
    m = LINE.match(lines[0].strip())
    if not m:
        return None, [f"the line does not match the recorded shape: {lines[0]!r}"]
    k, total, a, b, l0, f0, l1, f1 = (int(g.replace(",", "")) for g in m.groups()[:8])
    fig = {"K": k, "M": total, "A": a, "B": b, "L0": l0, "F0": f0, "L1": l1, "F1": f1,
           "sha": m.group(9)}
    problems = []
    if a + b != k:
        problems.append(f"A + B = {a + b}, not K = {k}")
    if k < 1:
        problems.append("K is 0 - two passes over one estimator record exactly that")
    if l0 + f0 != total:
        problems.append(f"before L0 + F0 = {l0 + f0}, not M = {total}")
    if l1 + f1 != total:
        problems.append(f"after L1 + F1 = {l1 + f1}, not M = {total}")
    if l1 != l0 - a + b:
        problems.append(f"L1 = {l1}, not L0 - A + B = {l0 - a + b}")
    return fig, problems


def _git(repo: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    """git in `repo`, confined to it by the shared fixture helper: a repository-locating
    variable a hook exports must not point the throwaway fixture's commits at this checkout."""
    return gitutil.git(list(args), cwd=repo, check=False, text=True, timeout=60)


def frame_problems(repo: pathlib.Path, sha: str, population: int) -> list[str]:
    """Every way the named commit fails to be the frame: not an ancestor of HEAD (or not in
    the history at all), an estimator that is not the pre-fix one, a different population."""
    problems = []
    if _git(repo, "merge-base", "--is-ancestor", sha, "HEAD").returncode != 0:
        problems.append(f"{sha} is not an ancestor of HEAD (or is unreachable)")
    blob = _git(repo, "show", f"{sha}:{ROUTE}")
    if blob.returncode != 0 or PRE_FIX_EXPRESSION not in blob.stdout:
        problems.append(f"{ROUTE} at {sha} does not carry `{PRE_FIX_EXPRESSION}` - "
                        f"not the pre-fix estimator")
    tree = _git(repo, "ls-tree", "-r", "--name-only", sha, "--",
                "sdlc-studio/stories", "sdlc-studio/bugs")
    counted = sum(1 for ln in tree.stdout.splitlines() if POPULATION.match(ln.strip()))
    if tree.returncode != 0 or counted != population:
        problems.append(f"M = {population}, but {sha} holds {counted} US/BG files")
    return problems


def _sample(k=3, m=10, a=2, b=1, l0=4, f0=6, l1=3, f1=7, sha="abc1234") -> str:
    return (f"# BG0000: x\n\n## Tier Shift\n\n- **Tier shift:** {k} of {m} units change tier "
            f"({a} light to full, {b} full to light); before {l0} light / {f0} full, after "
            f"{l1} light / {f1} full; measured at `{sha}`\n\n## Revision History\n")


class TierShiftRecordTests(unittest.TestCase):
    def test_the_bug_records_the_corpus_tier_shift_at_a_named_commit(self) -> None:
        """Mutants (each in the bug file): count only the stories, so M no longer reconciles
        with the split or the tree; name a post-fix revision, whose estimator no longer carries
        the size expression; record 0 moved units; change the after-fix light figure alone;
        delete the section. Each reddens a named check below, and the in-test controls show
        every check can refuse."""
        # -- controls: the checker refuses what it must, beside a sample it accepts
        _fig, ok = parse_record(_sample())
        self.assertEqual(ok, [], "the positive control is refused - the checker is wrong")
        self.assertTrue(any("L1 = " in p for p in parse_record(_sample(l1=4))[1]),
                        "a split that does not sum is accepted")
        self.assertTrue(any("K is 0" in p for p in
                            parse_record(_sample(k=0, a=0, b=0, l1=4, f1=6))[1]),
                        "a zero shift is accepted")
        self.assertTrue(parse_record("# BG0000: x\n\n## Revision History\n")[1],
                        "a bug with no section is accepted")
        line = _sample().split("## Tier Shift\n\n", 1)[1].split("\n", 1)[0]
        doubled = _sample().replace(line, line + "\n" + line)
        self.assertIn("2 `Tier shift` lines", parse_record(doubled)[1][0],
                      "a section carrying two Tier shift lines is accepted")
        self.assertIn("recorded shape", parse_record(_sample().replace(" units change tier",
                                                                       " units move"))[1][0],
                      "a line of another shape is accepted")
        self.assertTrue(any("A + B = " in p for p in parse_record(_sample(k=4))[1]),
                        "a direction split that does not sum to K is accepted")
        self.assertTrue(any("before L0 + F0" in p for p in parse_record(_sample(f0=7))[1]),
                        "a before-pass that does not sum to M is accepted")
        self._frame_controls()

        # -- the record itself: present, one line, a real shift, a split that sums
        bugs = sorted(REPO.glob(BUG_GLOB))
        self.assertEqual(len(bugs), 1, f"expected one {BUG_GLOB}, found {bugs}")
        fig, problems = parse_record(bugs[0].read_text(encoding="utf-8"))
        self.assertIsNotNone(fig, problems)
        self.assertEqual(problems, [], f"{bugs[0].name}: {problems}")

        # -- the frame: bound to the named commit, which a shallow clone cannot see
        shallow = _git(REPO, "rev-parse", "--is-shallow-repository").stdout.strip()
        if shallow == "true":
            self.skipTest("shallow clone: the ancestry, route.py blob and ls-tree population "
                          "checks need the named commit's history; the section, the K floor "
                          "and the split arithmetic ran above")
        self.assertEqual(frame_problems(REPO, fig["sha"], fig["M"]), [])

    def _frame_controls(self) -> None:
        """A throwaway repository: a pre-fix commit that is the frame, a post-fix commit whose
        estimator dropped the expression, and a side commit off HEAD's line."""
        with tempfile.TemporaryDirectory() as d:
            repo = pathlib.Path(d)

            def commit(route_text: str, units: list[str], msg: str) -> str:
                (repo / ROUTE).parent.mkdir(parents=True, exist_ok=True)
                (repo / ROUTE).write_text(route_text, encoding="utf-8")
                for u in units:
                    (repo / u).parent.mkdir(parents=True, exist_ok=True)
                    (repo / u).write_text("x\n", encoding="utf-8")
                _git(repo, "add", "-A")
                _git(repo, "commit", "-qm", msg)
                return _git(repo, "rev-parse", "HEAD").stdout.strip()

            _git(repo, "init", "-q", "-b", "main")
            pre = commit(f"x = {PRE_FIX_EXPRESSION}\n",
                         ["sdlc-studio/stories/US0001-a.md", "sdlc-studio/bugs/BG0001-b.md",
                          "sdlc-studio/stories/_index.md",
                          "sdlc-studio/stories/archive/US0000-old.md"], "pre")
            post = commit("x = ac_count / max_ac\n", [], "post")
            _git(repo, "checkout", "-q", "-b", "side", pre)
            side = commit(f"x = {PRE_FIX_EXPRESSION}  # side\n", [], "side")
            _git(repo, "checkout", "-q", "main")
            self.assertEqual(len({pre, post, side}), 3, "a fixture commit was not made")

            self.assertEqual(frame_problems(repo, pre, 2), [],
                             "the positive control (archive and _index.md excluded) is refused")
            self.assertTrue(any("not an ancestor" in p for p in frame_problems(repo, side, 2)),
                            "a commit off HEAD's line is accepted")
            self.assertTrue(any("not an ancestor" in p
                                for p in frame_problems(repo, "0" * 40, 2)),
                            "an unreachable commit is accepted")
            self.assertTrue(any("not the pre-fix" in p for p in frame_problems(repo, post, 2)),
                            "a post-fix estimator is accepted")
            self.assertTrue(any("holds 2" in p for p in frame_problems(repo, pre, 1)),
                            "a population that does not match the tree is accepted")


if __name__ == "__main__":
    unittest.main()
