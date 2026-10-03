"""US0952 AC1, AC3: a 5.1 upgrader opening the 6.0.0 section reads every v6 breaking change.

The v6 inventory sits under the release candidate's heading. The cut renames that heading
`[6.0.0-rc.1]` and composes Sprint 6's fragments under a new `[6.0.0]`, which alone would leave
the 6.0.0 section with no breaking change at all. The 6.0.0 Breaking text is the
`changelog.d/US0952.md` fragment before the cut and the `### Breaking` block under `## [6.0.0]`
after it; the candidate's is the `### Breaking` block under `## [6.0.0-rc.1]`, or under today's
`## [6.0.0]` before the rename. Which retirements must be disclosed is read from the registries
(`migrate._retired_verbs()`, `sdlc_md.RETIRED_CONFIG_KEYS`, `sdlc_md.RETIRED_CHECK_IDS`), never
from a hand list, so a retirement registered later needs a Breaking line or this fails. A
retirement registered after 6.0.0 shipped is disclosed where the next release's Breaking text
is written: a `changelog.d` fragment filed under `Breaking`, or `### Breaking` under
`## [Unreleased]` once composed (`pending_breaking`), never by editing a shipped section.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "tests"))
import retired_surface  # noqa: E402

_spec = importlib.util.spec_from_file_location("check_links_for_inventory",
                                               REPO / "tools" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)

_cspec = importlib.util.spec_from_file_location(
    "changelog_for_inventory", REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "changelog.py")
_changelog = importlib.util.module_from_spec(_cspec)
_cspec.loader.exec_module(_changelog)

FRAGMENT = Path("changelog.d") / "US0952.md"
_RELEASE = re.compile(r"^## \[([^\]]+)\](.*)$", re.M)

#: The machinery the candidate both built and removed, as its rc.1 entries name it.
MACHINERY = {
    "plan review": r"(?i)\bplan[- ]review",
    "the test plan": r"(?i)\btest[- ]plan",
    "repair plans": r"(?i)\brepair[- ]plan",
    "per-unit sign-off": r"(?i)\bsign-?off\b",
    "depth tiers": r"(?i)\bdepth\b",
    "mutation evidence": r"(?i)\bmutation[- ](?:evidence|ledger|gate)",
}


def _releases(text: str) -> dict[str, tuple[str, str]]:
    """version -> (the heading's text after the version, the section body)."""
    heads = list(_RELEASE.finditer(text))
    out: dict[str, tuple[str, str]] = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.setdefault(m.group(1), (m.group(2), text[m.end():end]))
    return out


def _block(body: str, kind: str) -> str:
    """The `### <kind>` block of a release body, to the next `### ` heading."""
    m = re.search(rf"^### {kind}\s*$(.*?)(?=^### |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def breaking_texts(root: Path) -> tuple[str, str, str, str]:
    """(6.0.0 Breaking text, rc.1 Breaking text, rc.1 section outside Breaking, rc.1 anchor)."""
    rel = _releases((root / "CHANGELOG.md").read_text(encoding="utf-8"))
    renamed = "6.0.0-rc.1" in rel
    rest, rc_body = rel.get("6.0.0-rc.1" if renamed else "6.0.0", ("", ""))
    fragment = root / FRAGMENT
    if fragment.is_file():
        six = fragment.read_text(encoding="utf-8").split("\n", 1)[-1]
    else:
        six = _block(rel.get("6.0.0", ("", ""))[1], "Breaking") if renamed else ""
    rc_rest = re.sub(r"^### Breaking\s*$.*?(?=^### |\Z)", "", rc_body, flags=re.M | re.S)
    return six, _block(rc_body, "Breaking"), rc_rest, check_links.slug(f"[6.0.0-rc.1]{rest}")


def pending_breaking(root: Path) -> str:
    """The Breaking text written after 6.0.0, where a retirement registered after 6.0.0 is
    disclosed - a shipped release's notes stay as shipped. Before the next cut it is
    `changelog.d` fragments filed under `Breaking` and the `### Breaking` block under
    `## [Unreleased]`; after it, the `### Breaking` block of every released section above
    `## [6.0.0]`. Reading only the pending text made a retirement disclosed today read as
    undisclosed the moment the release that discloses it was cut."""
    rel = _releases((root / "CHANGELOG.md").read_text(encoding="utf-8"))
    parts = []
    for version, (_head, body) in rel.items():     # file order: newest first
        if version == "6.0.0":
            break
        parts.append(_block(body, "Breaking"))
    for path in sorted((root / "changelog.d").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if re.match(r"\s*<!--\s*section:\s*Breaking\s*-->", text):
            parts.append(text)
    return "\n".join(parts)


def disclosure_problems(root: Path) -> list[str]:
    """What a 5.1 upgrader reading the 6.0.0 Breaking text would not be told."""
    six, rc, _rest, anchor = breaking_texts(root)
    lead = re.split(r"\n(?=- )|\n\s*\n", six.strip(), maxsplit=1)[0]
    problems = []
    if not re.search(r"(?i)\b5\.1\b", lead) or not re.search(r"(?i)every breaking change", lead):
        problems.append("the 6.0.0 Breaking text does not open by telling a 5.1 upgrader that "
                        "every breaking change listed under 6.0.0-rc.1 ships in 6.0.0")
    if not re.search(rf"\]\((?:CHANGELOG\.md)?#{re.escape(anchor)}\)", lead):
        problems.append(f"the lead does not link the 6.0.0-rc.1 section (#{anchor})")
    plain, apply = re.search(r"`migrate`", lead), re.search(r"`migrate --apply`", lead)
    if not (plain and apply and plain.start() < apply.start()):
        problems.append("the lead does not say to run `migrate`, then `migrate --apply`")
    both = f"{six}\n{rc}\n{pending_breaking(root)}"
    sdlc_md = retired_surface.sdlc_md
    for label in retired_surface.migrate._retired_verbs():
        script, verb = label.split(" ")
        if not re.search(rf"{re.escape(script)}`?\s+`?{re.escape(verb)}(?![\w-])", both):
            problems.append(f"retired verb `{label}` has no Breaking line")
    for name in (*sdlc_md.RETIRED_CONFIG_KEYS, *sdlc_md.RETIRED_CHECK_IDS):
        if not re.search(rf"(?<![\w.]){re.escape(name)}(?![\w.-])", both):
            problems.append(f"retired `{name}` has no Breaking line")
    return problems


class BreakingInventoryTests(unittest.TestCase):

    def _tree(self, changelog: str, fragment: str | None) -> Path:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
        if fragment is not None:
            (root / FRAGMENT).parent.mkdir()
            (root / FRAGMENT).write_text(fragment, encoding="utf-8")
        return root

    def test_every_registered_retirement_is_disclosed(self) -> None:
        """AC1. MUTANTS: the fragment's lead without its rc.1 link or its `migrate` steps; the
        `mutation.py audit` row deleted from the candidate's table; the cut's rename alone."""
        self.assertEqual([], disclosure_problems(REPO))

        # The cut, rehearsed on a copy while it is still ahead: rename the candidate, compose the
        # fragment under 6.0.0. After the cut the fragment is consumed and the candidate renamed,
        # and the assertion above carries AC1 alone.
        changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
        if not (REPO / FRAGMENT).is_file() or "6.0.0-rc.1" in _releases(changelog):
            return
        fragment = (REPO / FRAGMENT).read_text(encoding="utf-8")
        renamed = changelog.replace("## [6.0.0] -", "## [6.0.0-rc.1] -", 1)
        top = "## [Unreleased]\n"
        self.assertEqual(1, renamed.count(top))
        entry = fragment.split("\n", 1)[1]
        cut = renamed.replace(top, f"{top}\n## [6.0.0] - 2026-10-01\n\n### Breaking\n\n{entry}\n"
                                   f"### Fixed\n\n- a Sprint 6 fix\n\n", 1)
        self.assertEqual([], disclosure_problems(self._tree(cut, None)),
                         "the 6.0.0 section after the cut does not disclose v6's breaking changes")
        rename_only = renamed.replace(top, f"{top}\n## [6.0.0] - 2026-10-01\n\n### Fixed\n\n"
                                           f"- a Sprint 6 fix\n\n", 1)
        self.assertTrue(disclosure_problems(self._tree(rename_only, None)),
                        "the cut's rename alone read as a disclosed 6.0.0 section")

    def test_a_retirement_disclosed_after_6_0_0_stays_disclosed_after_the_next_cut(self) -> None:
        """BG0831 round-1 REJECT. MUTANT: `pending_breaking` reads only `## [Unreleased]` and the
        Breaking fragments - the cut moves them into a released section and consumes the
        fragment, so `review.policy`, disclosed today, reads as undisclosed at the tag push.

        The cut is the real one on a copy: `changelog.compose --apply` folds every pending
        fragment into `[Unreleased]` and deletes it, then `[Unreleased]` is released."""
        names = [n for n in retired_surface.sdlc_md.RETIRED_CONFIG_KEYS if n == "review.policy"]
        self.assertTrue(names, "premise: review.policy is a registered retirement")
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copy(REPO / "CHANGELOG.md", root / "CHANGELOG.md")
        # A release cut consumes every fragment, and git keeps no empty directory: on a cut tree
        # there is nothing to copy, and the disclosure already sits in a released section.
        if (REPO / "changelog.d").is_dir():
            shutil.copytree(REPO / "changelog.d", root / "changelog.d")
        self.assertNotIn("retired `review.policy` has no Breaking line",
                         disclosure_problems(root), "premise: disclosed before the cut")
        _changelog.compose(root, apply=True)
        self.assertFalse(list((root / "changelog.d").glob("*.md")), "the cut consumed nothing")
        text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        top = "## [Unreleased]\n"
        self.assertEqual(1, text.count(top))
        (root / "CHANGELOG.md").write_text(
            text.replace(top, f"{top}\n## [6.0.1] - 2026-10-02\n", 1), encoding="utf-8")
        self.assertEqual("", _block(_releases((root / "CHANGELOG.md").read_text(
            encoding="utf-8"))["Unreleased"][1], "Breaking"), "premise: Unreleased is empty")
        self.assertEqual([], [p for p in disclosure_problems(root) if "review.policy" in p],
                         "a retirement disclosed before the cut reads as undisclosed after it")

    def test_superseded_entries_are_flagged(self) -> None:
        """AC3. MUTANTS: the flag sentence dropped from the fragment; the rc.1 history deleted
        rather than flagged."""
        six, _rc, rc_rest, _anchor = breaking_texts(REPO)
        for label, rx in MACHINERY.items():
            with self.subTest(machinery=label):
                self.assertRegex(six, rx, f"the 6.0.0 Breaking text does not name {label}")
                self.assertTrue(re.search(rx, rc_rest),
                                f"the rc.1 section no longer holds its {label} history")
        flag = [" ".join(b.split()) for b in re.split(r"\n(?=- )", six)
                if "describe machinery the same release then" in " ".join(b.split())]
        self.assertEqual(1, len(flag), "no Breaking entry says the rc.1 entries describe "
                                       "machinery the same release then removed")
        for words in ("6.0.0-rc.1", "Added, Changed and Fixed entries",
                      "the same release then removed", "Breaking tables are the current word"):
            self.assertIn(words, flag[0])


if __name__ == "__main__":
    unittest.main()
