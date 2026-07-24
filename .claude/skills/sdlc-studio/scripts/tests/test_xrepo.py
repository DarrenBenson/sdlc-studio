"""Unit tests for scripts/lib/xrepo.py - the cross-repo artefact resolver.

Every checker that follows a `Depends on:` / `Blocked By:` edge in a multi-repo product
delegates its lookup here, so this module decides whether a unit in one repo is cleared by
work delivered in another. The tests are built on two real trees on disk: the primary path
resolves a referent in each of them, and the verdict is shown to track what those trees
actually contain rather than a manifest's say-so.

The degradation contract gets equal weight, because a resolver that guesses is worse than one
that refuses: three states (resolved, unsearchable, genuinely missing) must stay distinct, an
absent sibling checkout is named and never resolves, and no verdict may depend on the order
the manifest happens to list the repos in.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))  # `lib` is a package - a relative import needs it here

from lib import xrepo  # noqa: E402


# --- fixtures ---------------------------------------------------------------------

def _artefact(root: Path, kind: str, rec_id: str, status: str | None = "Draft") -> Path:
    """One artefact file in `<root>/sdlc-studio/<kind>/`, optionally with no Status line."""
    d = root / "sdlc-studio" / kind
    d.mkdir(parents=True, exist_ok=True)
    head = f"# {rec_id}: t\n\n"
    body = f"> **Status:** {status}\n" if status is not None else "> **Owner:** nobody\n"
    p = d / f"{rec_id}-t.md"
    p.write_text(head + body, encoding="utf-8")
    return p


def _manifest(root: Path, *entries: tuple[str, str], master: str = "docs/pvd.md") -> Path:
    """A product manifest naming each (id, path) sibling repo."""
    lines = [f"master_pvd: {master}", "repos:"]
    for rid, rel in entries:
        lines += [f"  - id: {rid}", f"    path: {rel}"]
    p = root / xrepo.MANIFEST_NAME
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _set_status(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8")
                    .replace(f"> **Status:** {old}", f"> **Status:** {new}"), encoding="utf-8")


# --- tests ---------------------------------------------------------------------

class PrimaryPathTests(unittest.TestCase):
    """US0352 AC1: the resolver driven across two trees."""

    def test_the_primary_path_completes_across_two_trees(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"          # the repo the lookup runs from
            away = Path(t) / "svc-b"          # the sibling the manifest names
            mine = _artefact(home, "stories", "US0010", "In Progress")
            theirs = _artefact(away, "epics", "EP0099", "Done")
            _artefact(away, "stories", "US0020", "Draft")
            _manifest(home, ("svc-b", "../svc-b"))

            repos = xrepo.manifest_repos(home)
            self.assertEqual([label for label, _ in repos], ["svc-b"])
            self.assertEqual(repos[0][1], away.resolve())

            # in-repo first, and reported as this repo
            here = xrepo.resolve("US0010", home, repos)
            self.assertEqual((here["repo"], here["status"]), (".", "In Progress"))
            self.assertFalse(here["cleared"])
            self.assertIsNone(here["error"])

            # ...and the referent that lives in the OTHER tree resolves, named and cleared
            there = xrepo.resolve("EP0099", home, repos)
            self.assertEqual((there["repo"], there["status"]), ("svc-b", "Done"))
            self.assertTrue(there["cleared"])
            self.assertIsNone(there["error"])
            self.assertEqual(xrepo.resolve("US0020", home, repos)["status"], "Draft")

            # the verdict is a function of what is on disk in both trees, so editing either
            # one changes it - a resolver reading a manifest claim instead would not move
            _set_status(theirs, "Done", "In Progress")
            self.assertFalse(xrepo.resolve("EP0099", home, repos)["cleared"])
            _set_status(mine, "In Progress", "Done")
            self.assertTrue(xrepo.resolve("US0010", home, repos)["cleared"])


class DegradationTests(unittest.TestCase):
    """The three states a caller must never collapse: resolved, unsearchable, missing."""

    def test_an_absent_checkout_is_named_and_never_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            _artefact(home, "stories", "US0010", "Draft")
            _manifest(home, ("gone", "../no-such-repo"))
            r = xrepo.resolve("EP0099", home, xrepo.manifest_repos(home))
            self.assertFalse(r["cleared"])
            self.assertIsNone(r["status"])
            self.assertIn("gone", r["error"])
            self.assertIn("no-such-repo", r["error"])
            self.assertNotEqual(r["error"], xrepo.MISSING)  # unsearchable is not missing

    def test_a_referent_in_no_repo_at_all_is_reported_missing(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            away = Path(t) / "svc-b"
            _artefact(home, "stories", "US0010", "Draft")
            _artefact(away, "epics", "EP0099", "Done")
            _manifest(home, ("svc-b", "../svc-b"))
            r = xrepo.resolve("EP0088", home, xrepo.manifest_repos(home))
            self.assertEqual(r["error"], xrepo.MISSING)
            self.assertIsNone(r["repo"])
            self.assertFalse(r["cleared"])

    def test_an_absent_repo_never_stops_the_search_of_a_later_one(self) -> None:
        """The verdict must not depend on manifest ordering: the referent is delivered in a
        repo that IS on disk, listed after one that is not."""
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            away = Path(t) / "svc-b"
            _artefact(home, "stories", "US0010", "Draft")
            _artefact(away, "epics", "EP0099", "Done")
            _manifest(home, ("gone", "../no-such-repo"), ("svc-b", "../svc-b"))
            r = xrepo.resolve("EP0099", home, xrepo.manifest_repos(home))
            self.assertEqual(r["repo"], "svc-b")
            self.assertTrue(r["cleared"])
            self.assertIsNone(r["error"])  # a searched-and-found id owes no absence report

    def test_a_referent_with_no_readable_status_is_not_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            _artefact(home, "epics", "EP0099", status=None)
            r = xrepo.resolve("EP0099", home, [])
            self.assertEqual(r["status"], "Unknown")
            self.assertFalse(r["cleared"])
            self.assertEqual(r["error"], "unknown status")


class ManifestTests(unittest.TestCase):
    """The line-wise manifest parse - no PyYAML, so its edges are ours to hold."""

    def test_no_manifest_is_an_in_repo_only_run(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            _artefact(home, "stories", "US0010", "Draft")
            self.assertEqual(xrepo.manifest_repos(home), [])
            r = xrepo.resolve("US0010", home, xrepo.manifest_repos(home))
            self.assertEqual(r["repo"], ".")

    def test_repo_paths_resolve_against_the_manifest_not_the_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "product" / "svc-a"
            away = Path(t) / "product" / "svc-b"
            away.mkdir(parents=True)
            mpath = _manifest(home.parent, ("svc-b", "./svc-b"))
            # the manifest sits a level ABOVE the repo, and is passed explicitly
            self.assertEqual(xrepo.manifest_repos(home, mpath), [("svc-b", away.resolve())])

    def test_inline_comments_are_stripped_from_the_fields(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            home.mkdir(parents=True)
            (home / xrepo.MANIFEST_NAME).write_text(
                "# the product\nmaster_pvd: docs/pvd.md\nrepos:\n"
                "  - id: svc-b   # the API service\n"
                "    path: ../svc-b   # a sibling checkout\n", encoding="utf-8")
            data = xrepo.read_manifest(home / xrepo.MANIFEST_NAME)
            self.assertEqual(data["master_pvd"], "docs/pvd.md")
            self.assertEqual(data["repos"], [{"id": "svc-b", "path": "../svc-b"}])
            self.assertEqual(xrepo.manifest_repos(home),
                             [("svc-b", (Path(t) / "svc-b").resolve())])

    def test_a_repo_entry_without_a_path_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            home = Path(t) / "svc-a"
            home.mkdir(parents=True)
            (home / xrepo.MANIFEST_NAME).write_text(
                "master_pvd: docs/pvd.md\nrepos:\n  - id: nameless\n  - id: svc-b\n"
                "    path: ../svc-b\n", encoding="utf-8")
            self.assertEqual([label for label, _ in xrepo.manifest_repos(home)], ["svc-b"])


if __name__ == "__main__":
    unittest.main()
