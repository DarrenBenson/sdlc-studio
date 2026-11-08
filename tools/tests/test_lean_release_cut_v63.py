"""US1139: v6.3.0 is cut through the shipped release path.

AC2 judges the disclosure at the commit that cut 6.3.0, never at the live corpus, because
`gate.py --release` runs every story's Verify at each later cut and a finding filed after this
one must not turn it red (BG1054). That commit is the v6.3.0 tag once it exists, else the commit
that last wrote `docs/known-issues.md`. While the cut is being committed, the page in the working
tree differs from HEAD's, and the working tree is then the commit about to be made, so it is the
one judged. AC3's notes link is read against the anchor of the CHANGELOG's own `## [6.3.0]`
heading. AC5 holds three sentences of the release text to the code they describe: each is read
where the cut leaves it (BG1290's entry from its fragment before the cut and from the CHANGELOG's
`## [6.3.0]` section after it), and the behaviour it states is exercised beside it. Each check
returns its problems and is run on a mutated copy, and on the wording before the cut, which it
must refuse.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_release_cut_v63.py
"""
# test-census-subject: docs/known-issues.md
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import conformance  # noqa: E402 - the light-APPROVE check the notes describe
import critic  # noqa: E402 - `tier_for` and `self_check_gap`
import init as init_mod  # noqa: E402 - what `init.py run --force` rewrites and what it leaves
KNOWN_ISSUES = REPO / "tools" / "known_issues.py"
CHANGELOG = REPO / "CHANGELOG.md"
PAGE = "docs/known-issues.md"
NOTES = "docs/release-notes-v6.3.0.md"
TAG = "v6.3.0"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


known_issues = _load("known_issues")  # the page's own reader: its export of a committed corpus
check_links = _load("check_links")    # the slug a CHANGELOG heading's anchor is spelt by

#: The one sentence of the notes `known_issues.py write` fills, with its three figures.
COUNT_LINE = re.compile(
    r"^\*\*v6\.3\.0 discloses (\d+) open defects: (\d+) Medium, (\d+) Low\.\*\*$", re.M)
#: The page's own count line, as `known_issues.render` writes it below the table.
PAGE_COUNT = re.compile(r"^(\d+) findings: (\d+) Medium, (\d+) Low\.$", re.M)
#: The heading a page names its release series in, which `known_issues.py check` reads it by.
BAR_HEADING = re.compile(r"^## The bar v(\d+\.\d+) is held to$", re.M)
CHANGELOG_LINK = re.compile(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)")

#: AC5's three sentences as worded before the cut (D0432), each of which claims more than the
#: code does: the notes' light-APPROVE bullet, their `--force` sentence and BG1290's entry.
LIGHT_BEFORE = (
    "- **A light APPROVE stops counting once the unit's own Affects grow.** Conformance owes the\n"
    "  full-tier review when the unit's Affects gained a file since its light APPROVE, or when the\n"
    "  tier was forced with `--tier light`, and `critic.py record` warns on stderr when a unit's "
    "latest\n  APPROVE is shallower than the tier its risk band now derives.\n")
FORCE_BEFORE = ("Do not pass `--force` for this: it rewrites every file `init`\n  writes, "
                "`.config.yaml`, `AGENTS.md`, `CLAUDE.md` and `decisions.md` among them.")
BG1290_BEFORE = (
    "`lane accept` now applies the check `critic.py brief` applies, `critic.self_check_gap`: "
    "under `block` it refuses and names the stale self-check, under `report` it records the "
    "verdict with that finding as a warning, and under `off` it does not ask.")
#: What each corrected sentence must say, whitespace folded: (pattern, what it says).
LIGHT_SAYS = (
    (r"only once `critic\.tier_for` derives `full` for the unit's risk band",
     "that a light APPROVE stops counting only once `critic.tier_for` derives `full`"),
    (r"`full`[^.]*?, and then when the tier was forced with `--tier light` or the unit's own "
     r"Affects gained a file",
     "that it then stops when forced with `--tier light` or when the Affects grew"),
)
FORCE_SAYS = (
    (r"leaves `sdlc-studio/\.version` alone", "that `--force` leaves `sdlc-studio/.version` alone"),
    (r"skips an `_index\.md` that exists", "that `--force` skips an `_index.md` that exists"),
)
BG1290_SAYS = (
    (r"`critic\.self_check_gap` sets aside a commit whose subject names only another unit",
     "that `critic.self_check_gap` sets aside a commit whose subject names only another unit"),
    (r"a change to the unit's Affects committed under another unit's id is not read as stale",
     "that a change committed under another unit's id is not read as stale"),
)
#: A claim the code refutes, whitespace folded: (pattern, why).
OVERCLAIMS = (
    (r"stops counting once the unit's own Affects grow\b",
     "it says a light APPROVE stops counting once the Affects grow, whatever the band"),
    (r"rewrites every file `init` writes", "it says `--force` rewrites every file `init` writes"),
)


def _env() -> dict:
    """This environment without the GIT_ variables a hook exports, so git reads this clone."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          env=_env(), timeout=120, check=False)


def _known_issues(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(KNOWN_ISSUES), *args], capture_output=True,
                          text=True, env=_env(), timeout=300, check=False)


def checkout() -> bool:
    """Whether this tree is the top of its own git work tree. A copy of its files with no history,
    as `test_lean_release_notes` makes to file a finding in, is not, and names no commit."""
    top = _git("rev-parse", "--show-toplevel")
    return top.returncode == 0 and Path(top.stdout.strip()).resolve() == REPO.resolve()


def cut_revision() -> tuple[str | None, str]:
    """`(revision, how)`: the commit that cut 6.3.0 and how it was found. The revision is None
    when the working tree is the cut, its page differing from HEAD's because the cut is being
    committed now. A comparison git cannot make raises rather than reading as a difference."""
    tag = _git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}^{{commit}}")
    if tag.returncode == 0:
        return tag.stdout.strip(), f"the {TAG} tag"
    diff = _git("diff", "--quiet", "HEAD", "--", PAGE)
    if diff.returncode not in (0, 1):
        raise AssertionError(f"git cannot compare {PAGE} with HEAD: {diff.stderr.strip()}")
    if diff.returncode == 1:
        return None, "the working tree, whose page is not yet committed"
    last = _git("log", "-1", "--format=%H", "--", PAGE).stdout.strip()
    return (last or None), f"{last[:8]}, the commit that last wrote {PAGE}"


def disclosure_problems(page: str, notes: str) -> list[str]:
    """Why `page` and `notes` are not what the 6.3.0 cut writes: the page names a bar series other
    than 6.3, the notes carry other than one filled count line, or that line's figures differ from
    the page's own count line. Empty when all three hold."""
    problems = []
    series = BAR_HEADING.findall(page)
    if series != ["6.3"]:
        problems.append(f"the page states the bar for {', '.join(series) or 'no release'}, "
                        "not v6.3")
    filled = COUNT_LINE.findall(notes)
    if len(filled) != 1:
        problems.append(f"the notes carry {len(filled)} filled count lines, not one")
    counted = PAGE_COUNT.findall(page)
    if len(counted) != 1:
        problems.append(f"the page carries {len(counted)} count lines, not one")
    elif len(filled) == 1 and filled[0] != counted[0]:
        problems.append(f"the notes disclose {'/'.join(filled[0])} (total/Medium/Low); the page "
                        f"lists {'/'.join(counted[0])}")
    return problems


def notes_link_problems(notes: str, changelog: str) -> list[str]:
    """Why the 6.3.0 notes do not link the CHANGELOG's `## [6.3.0]` section, or still link
    `[Unreleased]`."""
    heading = re.search(r"^## \[6\.3\.0\] - \d{4}-\d{2}-\d{2}$", changelog, re.M)
    if not heading:
        return ["the CHANGELOG has no `## [6.3.0] - <date>` heading"]
    anchor = check_links.slug(heading.group(0)[3:])
    links = CHANGELOG_LINK.findall(notes)
    problems = [] if anchor in links else [f"the notes do not link #{anchor}"]
    if "unreleased" in links:
        problems.append("the notes still link #unreleased")
    return problems


def flat(text: str) -> str:
    return " ".join(text.split())


def bullet(text: str, lead: str) -> str:
    """The one list item of `text` whose first line holds `lead`, its wrapped lines included;
    empty when none or more than one does."""
    hits = [i for i in re.split(r"(?m)^(?=- )", text)
            if i.startswith("- ") and lead in i.splitlines()[0]]
    return hits[0] if len(hits) == 1 else ""


def says_problems(text: str, says: tuple, where: str) -> list[str]:
    """Why `text` does not say each of `says`, or makes a claim OVERCLAIMS lists."""
    folded = flat(text)
    if not folded:
        return [f"no {where} was found"]
    problems = [f"the {where} does not say {what}" for pattern, what in says
                if not re.search(pattern, folded)]
    return problems + [f"the {where} claims more than the code: {why}"
                       for pattern, why in OVERCLAIMS if re.search(pattern, folded)]


def bg1290_entry(changelog: str, fragments: Path) -> str:
    """BG1290's entry where the cut leaves it: its fragment while one is pending, else the one
    list item naming it in the CHANGELOG's `## [6.3.0]` section; empty when neither holds it."""
    fragment = fragments / "BG1290.md"
    if fragment.is_file():
        return fragment.read_text(encoding="utf-8")
    cut = re.search(r"^## \[6\.3\.0\] - .*?(?=^## \[)", changelog, re.M | re.S)
    if not cut:
        return ""
    items = [i for i in re.split(r"(?m)^(?=- )", cut.group(0)) if "(BG1290)" in i]
    return items[0] if len(items) == 1 else ""


class ReleaseCutTests(unittest.TestCase):

    def test_the_release_text_claims_no_more_than_the_code(self) -> None:
        """AC5 (D0432). Each sentence is held to what it must say, then the behaviour it states
        is run: `conformance.tier_covers` keeps an explicit light APPROVE while `tier_for` derives
        `light` and drops it once it derives `full`; `init.init(force=True)` rewrites a seeded
        file but leaves `sdlc-studio/.version` and an existing `_index.md`;
        `critic._names_another_unit` reads a subject naming only another unit as that unit's.
        Mutants: each sentence as worded before the cut; the light bullet's `tier_for`
        precondition cut; the `--force` sentence's `_index.md` clause cut; no BG1290 entry."""
        notes = (REPO / NOTES).read_text(encoding="utf-8")
        light = bullet(notes, "light APPROVE stops counting")
        force = bullet(notes, "agent definitions")
        entry = bg1290_entry(CHANGELOG.read_text(encoding="utf-8"), REPO / "changelog.d")
        self.assertEqual([], says_problems(light, LIGHT_SAYS, "light-APPROVE bullet"))
        self.assertEqual([], says_problems(force, FORCE_SAYS, "`--force` bullet"))
        self.assertEqual([], says_problems(entry, BG1290_SAYS, "BG1290 entry"))

        with self.subTest(mutant="each sentence as worded before the cut"):
            self.assertEqual(
                ["the light-APPROVE bullet does not say " + what for _p, what in LIGHT_SAYS]
                + ["the light-APPROVE bullet claims more than the code: " + OVERCLAIMS[0][1]],
                says_problems(LIGHT_BEFORE, LIGHT_SAYS, "light-APPROVE bullet"))
            self.assertEqual(
                ["the `--force` bullet does not say " + what for _p, what in FORCE_SAYS]
                + ["the `--force` bullet claims more than the code: " + OVERCLAIMS[1][1]],
                says_problems(FORCE_BEFORE, FORCE_SAYS, "`--force` bullet"))
            self.assertEqual(
                ["the BG1290 entry does not say " + what for _p, what in BG1290_SAYS],
                says_problems(BG1290_BEFORE, BG1290_SAYS, "BG1290 entry"))
        with self.subTest(mutant="a clause of each corrected sentence cut"):
            cut = flat(light).replace("only once `critic.tier_for` derives `full`", "once", 1)
            self.assertIn("the light-APPROVE bullet does not say " + LIGHT_SAYS[0][1],
                          says_problems(cut, LIGHT_SAYS, "light-APPROVE bullet"))
            cut = flat(force).replace("skips an `_index.md` that exists", "skips nothing")
            self.assertEqual(["the `--force` bullet does not say " + FORCE_SAYS[1][1]],
                             says_problems(cut, FORCE_SAYS, "`--force` bullet"))
            self.assertEqual(["no BG1290 entry was found"],
                             says_problems("", BG1290_SAYS, "BG1290 entry"))

        with self.subTest(claim="a light APPROVE counts until `tier_for` derives `full`"):
            explicit = {"tier": "light" + critic.EXPLICIT_SUFFIX}
            with mock.patch.object(critic, "tier_for", return_value="light"):
                self.assertTrue(conformance.tier_covers(REPO, "US1139", explicit))
            with mock.patch.object(critic, "tier_for", return_value="full"):
                self.assertFalse(conformance.tier_covers(REPO, "US1139", explicit))
                self.assertTrue(conformance.tier_covers(REPO, "US1139", {"tier": "full"}))

        with self.subTest(claim="`--force` leaves .version and an existing _index.md"):
            with tempfile.TemporaryDirectory(prefix="us1139_force_") as tmp:
                root = Path(tmp)
                init_mod.init(root)
                kept = "\n<!-- us1139 kept -->\n"
                version = root / "sdlc-studio" / ".version"
                index = next((root / "sdlc-studio").rglob("_index.md"))
                config = root / "sdlc-studio" / ".config.yaml"
                for path in (version, index, config):
                    path.write_text(path.read_text(encoding="utf-8") + kept, encoding="utf-8")
                init_mod.init(root, force=True)
                self.assertIn(kept, version.read_text(encoding="utf-8"))
                self.assertIn(kept, index.read_text(encoding="utf-8"))
                self.assertNotIn(kept, config.read_text(encoding="utf-8"))

        with self.subTest(claim="a subject naming only another unit is that unit's commit"):
            self.assertTrue(critic._names_another_unit("fix(BG1288): x", "BG1290"))
            self.assertTrue(critic._names_another_unit("docs(US1136, BG1288): x", "BG1290"))
            self.assertFalse(critic._names_another_unit("fix(BG1288, BG1290): x", "BG1290"))
            self.assertFalse(critic._names_another_unit("chore: tidy", "BG1290"))

    def test_the_known_issues_page_is_cut_for_630(self) -> None:
        """AC2. Mutants: the 6.2.0 page left in place (its heading names v6.2); a count line whose
        figures disagree with the page's; the count line doubled, or left unfilled."""
        if not checkout():
            self.skipTest(f"{REPO} is not a git checkout of its own, so no commit is the cut")
        rev, how = cut_revision()
        shallow = _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
        if rev is not None and shallow and how != f"the {TAG} tag":
            self.skipTest("a shallow clone cannot name the commit that last wrote the page")
        self.assertTrue(rev is not None or how.startswith("the working tree"),
                        f"no commit has written {PAGE}")
        with tempfile.TemporaryDirectory(prefix="us1139_cut_") as tmp:
            if rev is None:
                root = REPO
                check = _known_issues("check", "--root", str(REPO))
                notes = (REPO / NOTES).read_text(encoding="utf-8")
            else:
                root = Path(tmp)
                self.assertTrue(known_issues._export(REPO, rev, root), f"cannot read {how}")
                check = _known_issues("check", "--root", str(REPO), "--at", rev)
                shown = _git("show", f"{rev}:{NOTES}")
                self.assertEqual(0, shown.returncode, f"{NOTES} is not in {how}")
                notes = shown.stdout
            self.assertEqual(0, check.returncode, f"`known_issues.py check` refuses the page at "
                             f"{how}:\n{check.stdout}{check.stderr}")
            bar = _known_issues("bar", "--root", str(root))
            self.assertEqual(0, bar.returncode, f"`known_issues.py bar` refuses {how}:\n"
                             f"{bar.stdout}{bar.stderr}")
            page = (root / PAGE).read_text(encoding="utf-8")
        self.assertEqual([], disclosure_problems(page, notes), how)

        line = COUNT_LINE.search(notes).group(0)
        total, mediums, lows = COUNT_LINE.search(notes).groups()
        off = line.replace(f"{mediums} Medium", f"{int(mediums) + 1} Medium")
        self.assertEqual(
            ["the page states the bar for 6.2, not v6.3"],
            disclosure_problems(page.replace("## The bar v6.3 is held to",
                                             "## The bar v6.2 is held to"), notes))
        self.assertEqual(
            [f"the notes disclose {total}/{int(mediums) + 1}/{lows} (total/Medium/Low); the page "
             f"lists {total}/{mediums}/{lows}"],
            disclosure_problems(page, notes.replace(line, off)))
        self.assertEqual(["the notes carry 2 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, f"{line}\n\n{line}")))
        unfilled = "**v6.3.0 discloses N open defects: N Medium, N Low.**"
        self.assertEqual(["the notes carry 0 filled count lines, not one"],
                         disclosure_problems(page, notes.replace(line, unfilled)))

    def test_the_notes_link_the_630_section(self) -> None:
        """AC3. Mutants: the notes' CHANGELOG link left at `#unreleased`; the CHANGELOG with no
        6.3.0 heading."""
        notes = (REPO / NOTES).read_text(encoding="utf-8")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        self.assertEqual([], notes_link_problems(notes, changelog))
        anchor = next(a for a in CHANGELOG_LINK.findall(notes) if a.startswith("630-"))
        stale = notes.replace(f"#{anchor})", "#unreleased)")
        self.assertNotEqual(notes, stale)
        self.assertEqual([f"the notes do not link #{anchor}", "the notes still link #unreleased"],
                         notes_link_problems(stale, changelog))
        uncut = re.sub(r"^## \[6\.3\.0\] - ", "## [6.3.0-draft] - ", changelog, flags=re.M)
        self.assertEqual(["the CHANGELOG has no `## [6.3.0] - <date>` heading"],
                         notes_link_problems(notes, uncut))


if __name__ == "__main__":
    unittest.main()
