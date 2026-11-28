"""US1330: v6.5.0 is cut through the shipped release path.

Every check returns its problems and is run on mutated copies, which it must refuse. Each stays
true after later releases, because `gate.py --release` runs every story's Verify at each cut:
the versions are read as at or above 6.5.0, the CHANGELOG range is bounded by the `## [6.4.0]`
heading, the install pins are held to the release package.json declares, and the specs are
judged at the v6.5.0 tag once it exists, else in the working tree. A clone without the tag whose
package.json has moved past 6.5.0 skips that check, naming why.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_release_cut_v65.py
"""
# test-census-subject: CHANGELOG.md
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
CHANGELOG = REPO / "CHANGELOG.md"
NOTES = "docs/release-notes-v6.5.0.md"
RELEASES = "sdlc-studio/reports/releases.jsonl"
STAMP = "sdlc-studio/.version"
TAG = "v6.5.0"
FLOOR = (6, 5, 0)
PIN_PAGES = ("README.md", "docs/INSTALL.md", "docs/enterprise.md")
SPECS = ("sdlc-studio/prd.md", "sdlc-studio/trd.md", "sdlc-studio/tsd.md")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check_links = _load("_cut_v65_check_links", REPO / "tools" / "check_links.py")
#: The shipped git-fixture helper, so every git child runs with the skill tests' confinement.
gitutil = _load("_cut_v65_gitutil", SCRIPTS / "tests" / "gitutil.py")

#: The sentence US1054's fragment carried until the cut corrected it: BG1655 made a lone first
#: name after a comma no claim, so the copy it describes draws no finding.
SAM_CLAIM = "in every project whose cast holds no Sam"
SAM_SENTENCE = ('A copy that still names "the Primary persona, Sam the new shopper" is reported as '
                f"`seat-persona-unknown`, which blocks, {SAM_CLAIM}.")
#: An id one of the folded fragments' own text carries, rechecked at the cut.
CARRIED_ID = "US1321"
CHANGELOG_LINK = re.compile(r"\]\(\.\./CHANGELOG\.md#([\w-]+)\)")
HEADING_650 = re.compile(r"^## \[6\.5\.0\] - \d{4}-\d{2}-\d{2}$", re.M)
HEADING_640 = re.compile(r"^## \[6\.4\.0\] - ", re.M)
PIN = re.compile(r"(?<![\w-])(--version|-Version) v(\d+\.\d+\.\d+[\w.-]*)")
SKILL_VERSION = re.compile(r'^skill_version:\s*"?([^"\s#]+)"?', re.M)
NOTES_ITEM = re.compile(r"^- \[docs/release-notes-v([^\]]+)\.md\]\(docs/release-notes-v[^)]+\)"
                        r".*$", re.M)
COVERAGE = re.compile(r"(?:\*\*)?Coverage:(?:\*\*)? v(\S+) as cut, plus the (\S+) work on `main`")
BASELINE_LINE = re.compile(r"^Baseline: v(\S+) as cut, plus the (\S+) work on `main`", re.M)


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True,
                          env=gitutil.git_env(), timeout=120, check=False)


def _core(version: str) -> tuple[int, ...]:
    """The numeric core of `version` (`6.5.0-rc.1` gives `(6, 5, 0)`), or `()` unread."""
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", str(version or ""))
    return tuple(int(p) for p in m.groups()) if m else ()


def _read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def release() -> str:
    """The release package.json declares."""
    return json.loads(_read("package.json"))["version"]


def version_problems(package: dict, lock: dict, stamp: str) -> list[str]:
    """Why package.json, package-lock.json and the project stamp do not carry the release: the
    package below 6.5.0, the lock's top or root-package version not the package's, or the
    stamp's skill_version below 6.5.0."""
    problems = []
    version = package.get("version", "")
    if _core(version) < FLOOR:
        problems.append(f"package.json names {version or 'no version'}, below 6.5.0")
    top = lock.get("version")
    if top != version:
        problems.append(f"package-lock.json's top version is {top}, not package.json's {version}")
    root = (lock.get("packages") or {}).get("", {}).get("version")
    if root != version:
        problems.append(f"package-lock.json's root package is {root}, not package.json's "
                        f"{version}")
    m = SKILL_VERSION.search(stamp)
    stamped = m.group(1) if m else ""
    if _core(stamped) < FLOOR:
        problems.append(f"{STAMP} names skill_version {stamped or 'none'}, below 6.5.0")
    return problems


def section_problems(changelog: str, releases: str) -> list[str]:
    """Why the CHANGELOG's 6.5.0 section is not the cut's: no `## [6.5.0] - <date>` heading, no
    `## [6.4.0]` heading below it to bound it, the range not carrying `CARRIED_ID` or still
    carrying US1054's corrected claim, or the release record the cut appends not written
    exactly once (a section merged by hand writes none)."""
    heading = HEADING_650.search(changelog)
    if not heading:
        return ["the CHANGELOG has no `## [6.5.0] - <date>` heading"]
    bound = HEADING_640.search(changelog, heading.end())
    if not bound:
        return ["the CHANGELOG has no `## [6.4.0]` heading below the 6.5.0 one"]
    body = " ".join(changelog[heading.end():bound.start()].split())
    problems = []
    if CARRIED_ID not in body:
        problems.append(f"the 6.5.0 section does not carry {CARRIED_ID}")
    if SAM_CLAIM in body:
        problems.append(f"the 6.5.0 section still says a copy naming Sam is refused {SAM_CLAIM}")
    records = [json.loads(line) for line in releases.splitlines() if line.strip()]
    cut = [r for r in records if r.get("version") == "6.5.0"]
    if len(cut) != 1:
        problems.append(f"{RELEASES} holds {len(cut)} 6.5.0 records, not one")
    return problems


def notes_link_problems(notes: str, changelog: str) -> list[str]:
    """Why the 6.5.0 notes do not link the CHANGELOG's `## [6.5.0]` section, or still link
    `[Unreleased]`."""
    heading = HEADING_650.search(changelog)
    if not heading:
        return ["the CHANGELOG has no `## [6.5.0] - <date>` heading"]
    anchor = check_links.slug(heading.group(0)[3:])
    links = CHANGELOG_LINK.findall(notes)
    problems = [] if anchor in links else [f"the notes do not link #{anchor}"]
    if "unreleased" in links:
        problems.append("the notes still link #unreleased")
    return problems


def pin_problems(pages: dict[str, str], version: str) -> list[str]:
    """Why the install pages do not pin `version`: a page with no pin, a `--version` or
    `-Version` example naming another release, enterprise.md's "Pin a release" line missing
    either form, README's current-release line not linking `version`'s notes, or README's
    release-notes list calling other than exactly that release current."""
    problems = []
    for rel, text in pages.items():
        pins = PIN.findall(text)
        if not pins:
            problems.append(f"{rel} pins no release")
        problems += [f"{rel} pins {flag} v{named}, not v{version}"
                     for flag, named in pins if named != version]
    enterprise = pages.get("docs/enterprise.md", "")
    line = next((ln for ln in enterprise.splitlines() if "**Pin a release.**" in ln), "")
    for flag in ("--version", "-Version"):
        if not re.search(rf"(?<![\w-]){flag} v{re.escape(version)}(?![\w.-])", line):
            problems.append(f"enterprise.md's Pin a release line has no {flag} v{version}")
    readme = pages.get("README.md", "")
    lead = next((ln for ln in readme.splitlines()
                 if ln.startswith("What changed in the current release:")), "")
    if f"](docs/release-notes-v{version}.md)" not in lead:
        problems.append(f"README's current-release line does not link the {version} notes")
    current = [m.group(1) for m in NOTES_ITEM.finditer(readme)
               if " - the current release" in m.group(0)]
    if current != [version]:
        problems.append(f"README's release-notes list calls {current or 'nothing'} current, "
                        f"not only {version}")
    return problems


def spec_problems(pages: dict[str, str]) -> list[str]:
    """Why the PRD, TRD and TSD do not cover v6.5.0 as cut, plus the 6.6 work on `main`: a page
    whose Coverage line is missing, doubled or names another baseline, or a PRD whose inventory
    `Baseline:` line does."""
    problems = []
    for rel, text in pages.items():
        found = COVERAGE.findall(text)
        if found != [("6.5.0", "6.6")]:
            problems.append(f"{rel}'s Coverage reads {found or 'nothing'}, not v6.5.0 as cut, "
                            "plus the 6.6 work on `main`")
        if rel.endswith("prd.md"):
            base = BASELINE_LINE.findall(text)
            if base != [("6.5.0", "6.6")]:
                problems.append(f"{rel}'s inventory Baseline reads {base or 'nothing'}, not "
                                "v6.5.0 as cut, plus the 6.6 work on `main`")
    return problems


def spec_pages() -> tuple[dict[str, str] | None, str]:
    """`(pages, how)`: the specs as the v6.5.0 tag holds them once it exists, else the working
    tree's (the cut uncommitted, or committed with no tag yet). None when the tag is not in this
    clone and package.json has moved past 6.5.0, so no tree read here is the cut."""
    tag = _git("rev-parse", "-q", "--verify", f"refs/tags/{TAG}^{{commit}}")
    if tag.returncode == 0:
        pages = {}
        for rel in SPECS:
            shown = _git("show", f"{TAG}:{rel}")
            if shown.returncode != 0:
                raise AssertionError(f"{rel} is not in the {TAG} tag: {shown.stderr.strip()}")
            pages[rel] = shown.stdout
        return pages, f"the {TAG} tag"
    if _core(release())[:2] > FLOOR[:2]:
        return None, f"the {TAG} tag is not in this clone and package.json is {release()}"
    return {rel: _read(rel) for rel in SPECS}, "the working tree"


class ReleaseCutTests(unittest.TestCase):

    def test_every_version_home_and_the_section_name_650(self) -> None:
        """AC1. Mutants: package.json at 6.4.0; the lock's root package at 6.4.0; the stamp at
        6.4.0; no 6.5.0 heading; US1054's last sentence put back; the carried id gone; the
        release record gone or doubled; no 6.4.0 bound. Near miss that must pass: the sentence
        below the 6.4.0 heading."""
        package = json.loads(_read("package.json"))
        lock = json.loads(_read("package-lock.json"))
        stamp = _read(STAMP)
        changelog = CHANGELOG.read_text(encoding="utf-8")
        releases = _read(RELEASES)
        self.assertEqual([], version_problems(package, lock, stamp))
        self.assertEqual([], section_problems(changelog, releases))

        version = package["version"]
        old = dict(package, version="6.4.0")
        self.assertEqual(["package.json names 6.4.0, below 6.5.0",
                          f"package-lock.json's top version is {version}, not package.json's "
                          "6.4.0",
                          f"package-lock.json's root package is {version}, not package.json's "
                          "6.4.0"],
                         version_problems(old, lock, stamp))
        split = json.loads(json.dumps(lock))
        split["packages"][""]["version"] = "6.4.0"
        self.assertEqual([f"package-lock.json's root package is 6.4.0, not package.json's "
                          f"{version}"], version_problems(package, split, stamp))
        unstamped = SKILL_VERSION.sub('skill_version: "6.4.0"', stamp)
        self.assertNotEqual(stamp, unstamped)
        self.assertEqual([f"{STAMP} names skill_version 6.4.0, below 6.5.0"],
                         version_problems(package, lock, unstamped))

        heading = HEADING_650.search(changelog).group(0)
        uncut = changelog.replace(heading, heading.replace("[6.5.0]", "[6.5.0-draft]"))
        self.assertEqual(["the CHANGELOG has no `## [6.5.0] - <date>` heading"],
                         section_problems(uncut, releases))
        bound = HEADING_640.search(changelog).group(0)
        unbounded = changelog.replace(bound, "## [6.4.0-draft] - ")
        self.assertEqual(["the CHANGELOG has no `## [6.4.0]` heading below the 6.5.0 one"],
                         section_problems(unbounded, releases))
        with_sam = changelog.replace(heading, f"{heading}\n\n{SAM_SENTENCE}", 1)
        self.assertEqual([f"the 6.5.0 section still says a copy naming Sam is refused {SAM_CLAIM}"],
                         section_problems(with_sam, releases))
        wrapped_sentence = SAM_SENTENCE.replace(" every ", "\nevery ")
        wrapped = changelog.replace(heading, f"{heading}\n\n{wrapped_sentence}", 1)
        self.assertEqual(1, len(section_problems(wrapped, releases)), "a wrapped claim is read")
        line_end = changelog.index("\n", HEADING_640.search(changelog).end())
        below = changelog[:line_end] + f"\n\n{SAM_SENTENCE}\n" + changelog[line_end:]
        self.assertEqual([], section_problems(below, releases))
        start, end = HEADING_650.search(changelog).end(), HEADING_640.search(changelog).start()
        dropped = changelog[:start] + changelog[start:end].replace(CARRIED_ID, "US9999") + \
            changelog[end:]
        self.assertEqual([f"the 6.5.0 section does not carry {CARRIED_ID}"],
                         section_problems(dropped, releases))
        lines = releases.splitlines()
        unrecorded = "\n".join(ln for ln in lines if '"version": "6.5.0"' not in ln)
        self.assertNotEqual(releases.strip(), unrecorded.strip())
        self.assertEqual([f"{RELEASES} holds 0 6.5.0 records, not one"],
                         section_problems(changelog, unrecorded))
        twice = releases + next(ln for ln in lines if '"version": "6.5.0"' in ln) + "\n"
        self.assertEqual([f"{RELEASES} holds 2 6.5.0 records, not one"],
                         section_problems(changelog, twice))

    def test_the_notes_link_the_650_section(self) -> None:
        """AC2. Mutants: the notes' CHANGELOG link left at `#unreleased`; an anchor of another
        date; the CHANGELOG with no 6.5.0 heading."""
        notes = _read(NOTES)
        changelog = CHANGELOG.read_text(encoding="utf-8")
        self.assertEqual([], notes_link_problems(notes, changelog))
        anchor = next(a for a in CHANGELOG_LINK.findall(notes) if a.startswith("650-"))
        stale = notes.replace(f"#{anchor})", "#unreleased)")
        self.assertNotEqual(notes, stale)
        self.assertEqual([f"the notes do not link #{anchor}", "the notes still link #unreleased"],
                         notes_link_problems(stale, changelog))
        other = notes.replace(f"#{anchor})", "#650---1999-01-01)")
        self.assertNotEqual(notes, other)
        self.assertEqual([f"the notes do not link #{anchor}"], notes_link_problems(other, changelog))
        uncut = re.sub(r"^## \[6\.5\.0\] - ", "## [6.5.0-draft] - ", changelog, flags=re.M)
        self.assertEqual(["the CHANGELOG has no `## [6.5.0] - <date>` heading"],
                         notes_link_problems(notes, uncut))

    def test_every_install_pin_names_the_release(self) -> None:
        """AC2. Mutants: enterprise.md's `--version` and then its `-Version` at v6.4.0; INSTALL's
        checksum pin at v6.4.0; a page with no pin; README's current-release line at the 6.4.0
        notes; README's list calling 6.4.0 current as well, or 6.5.0 not current."""
        version = release()
        self.assertGreaterEqual(_core(version), FLOOR)
        pages = {rel: _read(rel) for rel in PIN_PAGES}
        self.assertEqual([], pin_problems(pages, version))

        def mutated(rel: str, old: str, new: str) -> dict[str, str]:
            self.assertIn(old, pages[rel], f"{old!r} is not in {rel}")
            return dict(pages, **{rel: pages[rel].replace(old, new, 1)})

        ent = "docs/enterprise.md"
        self.assertEqual([f"{ent} pins --version v6.4.0, not v{version}",
                          f"enterprise.md's Pin a release line has no --version v{version}"],
                         pin_problems(mutated(ent, f"--version v{version}", "--version v6.4.0"),
                                      version))
        self.assertEqual([f"{ent} pins -Version v6.4.0, not v{version}",
                          f"enterprise.md's Pin a release line has no -Version v{version}"],
                         pin_problems(mutated(ent, f"-Version v{version}", "-Version v6.4.0"),
                                      version))
        checksum = f"SDLC_STUDIO_REQUIRE_CHECKSUM=1 bash -s -- --version v{version}"
        self.assertEqual([f"docs/INSTALL.md pins --version v6.4.0, not v{version}"],
                         pin_problems(mutated("docs/INSTALL.md", checksum,
                                              checksum.replace(version, "6.4.0")), version))
        bare = dict(pages, **{"docs/INSTALL.md": PIN.sub("", pages["docs/INSTALL.md"])})
        self.assertEqual(["docs/INSTALL.md pins no release"], pin_problems(bare, version))
        lead = (f"[the {version} release notes](docs/release-notes-v{version}.md)")
        self.assertEqual([f"README's current-release line does not link the {version} notes"],
                         pin_problems(mutated("README.md", lead,
                                              "[the 6.4.0 release notes]"
                                              "(docs/release-notes-v6.4.0.md)"), version))
        item = (f"- [docs/release-notes-v{version}.md](docs/release-notes-v{version}.md)"
                " - the current release")
        older = ("- [docs/release-notes-v6.4.0.md](docs/release-notes-v6.4.0.md) - the current "
                 "release: the 6.3 upgrade path\n")
        self.assertEqual([f"README's release-notes list calls ['6.4.0', '{version}'] current, "
                          f"not only {version}"],
                         pin_problems(mutated("README.md", item, f"{older}{item}"), version))
        self.assertEqual([f"README's release-notes list calls nothing current, not only "
                          f"{version}"],
                         pin_problems(mutated("README.md", item, item.replace(
                             " - the current release", " - the release")), version))

    def test_the_specs_name_650_as_cut(self) -> None:
        """AC3. Mutants: each spec's Coverage line back at v6.4.0 as cut, plus the 6.5 work; the
        PRD's inventory Baseline at 6.4.0; the 6.6 put back as 6.5; a Coverage line doubled or
        removed."""
        pages, how = spec_pages()
        if pages is None:
            self.skipTest(how)
        self.assertEqual([], spec_problems(pages), how)
        stale = "v6.4.0 as cut, plus the 6.5 work on `main`"
        for rel in SPECS:
            with self.subTest(page=rel):
                line = COVERAGE.search(pages[rel]).group(0)
                back = line.replace("v6.5.0 as cut, plus the 6.6 work on `main`", stale)
                self.assertNotEqual(line, back)
                self.assertEqual([f"{rel}'s Coverage reads [('6.4.0', '6.5')], not v6.5.0 as "
                                  "cut, plus the 6.6 work on `main`"],
                                 spec_problems({rel: pages[rel].replace(line, back, 1)}))
                self.assertEqual(1, len(spec_problems({rel: pages[rel].replace(line, "", 1)})))
                self.assertEqual(1, len(spec_problems(
                    {rel: pages[rel].replace(line, f"{line}; {line}", 1)})))
        prd = "sdlc-studio/prd.md"
        base = BASELINE_LINE.search(pages[prd]).group(0)
        self.assertEqual([f"{prd}'s inventory Baseline reads [('6.4.0', '6.5')], not v6.5.0 as "
                          "cut, plus the 6.6 work on `main`"],
                         spec_problems({prd: pages[prd].replace(base, f"Baseline: {stale}", 1)}))
        line = COVERAGE.search(pages[prd]).group(0)
        self.assertEqual([f"{prd}'s Coverage reads [('6.5.0', '6.5')], not v6.5.0 as cut, plus "
                          "the 6.6 work on `main`"],
                         spec_problems({prd: pages[prd].replace(
                             line, line.replace("plus the 6.6 work", "plus the 6.5 work"), 1)}))


if __name__ == "__main__":
    unittest.main()
