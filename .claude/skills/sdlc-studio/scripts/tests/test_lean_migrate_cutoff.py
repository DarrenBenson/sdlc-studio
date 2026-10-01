"""BG0845: migrate's conformance cutoff on a v4.1 project.

The project already set `conformance.adopt_after: US0682`; migrate told it to "add" a cutoff at its
highest story, calling the 98 units above its own adoption point "pre-adoption history", and put the
49 of them holding an APPROVE row in the v4.1 five-column ledger (no Author column) in one list with
the units nobody reviewed. The item now names the existing cutoff and the line as a raise from it,
and counts the author-less APPROVE units apart. Read through `migrate.py --format json`, the command
an upgrader runs; every fixture is a temporary directory.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


migrate = _load("migrate")

#: The v4.1 ledger header: five columns, no Author.
V41_LEDGER = ("# Critic verdicts\n\n| Unit | Verdict | Reviewer | Date | Issues |\n"
              "| --- | --- | --- | --- | --- |\n")


def _w(root: Path, rel: str, text: str) -> None:
    p = root / "sdlc-studio" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _story(n: int, verified: bool = True) -> str:
    stamp = f"  - **Verified:** yes (2026-01-0{n})\n" if verified else ""
    return (f"# US000{n}: s{n}\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
            f"## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
            f"  - **Verify:** shell true\n{stamp}")


def _v41(root: Path, cutoff: str = "US0002", rows: str = "", extra: dict | None = None) -> None:
    """An `init`ed workspace aged to schema 2 with `conformance.adopt_after` set, four Done
    stories with a verified criterion, and the five-column ledger holding `rows`."""
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True)
    cfg = root / "sdlc-studio" / ".config.yaml"
    tail = f"\nconformance:\n  adopt_after: {cutoff}\n" if cutoff else ""
    cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2")
                   + tail, encoding="utf-8")
    for n in (1, 2, 3, 4):
        _w(root, f"stories/US000{n}-s.md", _story(n))
    for rel, text in (extra or {}).items():
        _w(root, rel, text)
    _w(root, "reviews/critic-verdicts.md", V41_LEDGER + rows)
    import reconcile  # noqa: PLC0415 - rows for the stories, so `reconciled` is met
    reconcile.apply_type("story", root)


#: A schema v3 Done story whose criterion is verified: conformant once an independent APPROVE
#: is recorded and its index row exists.
V3_STORY = "US-01M3VEK2"


def _v3(root: Path, approved: bool) -> None:
    """A fresh `init run` project (schema v3) holding one Done ULID story, its index reconciled,
    and an independent APPROVE when `approved`."""
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True)
    _w(root, f"stories/{V3_STORY}-s.md",
       f"# {V3_STORY}: s\n\n> **Status:** Done\n> **Epic:** EP-01M3VEK0\n\n"
       "## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
       "  - **Verify:** shell true\n  - **Verified:** yes (2026-01-01)\n")
    if approved:
        _load("critic").record_verdict(root, V3_STORY, "APPROVE", reviewer="qa seat",
                                       author="builder", issues="none")
    import reconcile  # noqa: PLC0415
    reconcile.apply_type("story", root)


class MigrateCutoffTests(unittest.TestCase):
    KIND = "conformance-cutoff"

    def test_a_ulid_only_conformance_failure_is_still_named(self) -> None:
        """BG0858 AC1. MUTANTS: (1) HEAD's `id_number` filter - a ULID-only failure names
        nothing; (2) propose the highest SEQUENTIAL id only - no line; (3) a line the lane does
        not accept - the gate still fails after it is written."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v3(root, approved=False)
            lane = self._lane(root)
            self.assertEqual("fail", lane["status"], "premise: the lane fails on the ULID story")
            item = self._item(root)
            self.assertEqual(f"conformance.adopt_after: {V3_STORY}", item["line"])
            self.assertEqual(lane["count"], item["count"])
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text(cfg.read_text(encoding="utf-8") + "\nconformance:\n  adopt_after: "
                           + V3_STORY + "\n", encoding="utf-8")
            self.assertEqual("pass", self._lane(root)["status"],
                             "the proposed cutoff did not clear the lane it was proposed for")

    def test_a_repo_wide_only_failure_is_still_named(self) -> None:
        """BG0858 AC2. MUTANT: HEAD's `if not failing: return []` - the lane fails on a missing
        story index and migrate names nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v3(root, approved=True)
            (root / "sdlc-studio" / "stories" / "_index.md").unlink()
            lane = self._lane(root)
            self.assertEqual("fail", lane["status"],
                             "premise: the repo-wide failure fails the lane")
            item = self._item(root)
            self.assertEqual(lane["count"], item["count"])
            self.assertIsNone(item.get("line"), item)
            self.assertNotIn("adopt_after:", item["detail"], item["detail"])

    def _item(self, root: Path) -> dict:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            rc = migrate.main(["--root", str(root), "--format", "json"])
        self.assertEqual(0, rc, buf.getvalue())
        items = [h for h in json.loads(buf.getvalue())["needs_human"] if h["kind"] == self.KIND]
        self.assertEqual(1, len(items), items)
        return items[0]

    def _lane(self, root: Path) -> dict:
        import gate  # noqa: PLC0415
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            gate.main(["--root", str(root), "--only", "conformance", "--format", "json"])
        return next(c for c in json.loads(buf.getvalue())["checks"] if c["check"] == "conformance")

    def test_an_existing_cutoff_is_named_as_raised_not_added(self) -> None:
        # Mutants: today's "add" wording, a raise that does not name the value already set, and
        # calling units above the project's own cutoff pre-adoption history.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v41(root)
            self.assertEqual("fail", self._lane(root)["status"])
            item = self._item(root)
        detail = item["detail"]
        self.assertIn("raise `conformance.adopt_after` from US0002 to US0004", detail)
        self.assertIn("`conformance.adopt_after: US0004`", detail)
        self.assertNotIn("add `", detail)
        self.assertNotIn("pre-adoption history", detail)
        self.assertEqual("conformance.adopt_after: US0004", item["line"])
        self.assertEqual("conformance", item["lane"])

    def test_approve_rows_with_no_author_are_counted_apart(self) -> None:
        # US0003: an APPROVE row in the five-column ledger and nothing else unmet. US0004: no
        # verdict row. US0005: an author-less APPROVE row but an unverified criterion too, so it
        # is not answered by recording an author. Mutants: one undifferentiated list, a split on
        # "has any APPROVE row" that ignores the other unmet stages, and counts that disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v41(root,
                 rows=("| US0003 | APPROVE | qa-seat | 2026-01-03 | - |\n"
                       "| US0005 | APPROVE | qa-seat | 2026-01-05 | - |\n"),
                 extra={"stories/US0005-s.md": _story(5, verified=False)})
            item = self._item(root)
        detail = item["detail"]
        self.assertIn("1 of them (US0003) with an APPROVE row that records no author", detail)
        self.assertIn("the other 2 (US0004", detail)
        self.assertIn("US0005 (verified", detail)
        self.assertEqual(["US0003"], item["approve_no_author"])
        self.assertEqual(["US0004", "US0005"], item["other"])
        self.assertEqual(["US0003", "US0004", "US0005"], item["ids"])

    def test_only_an_approve_with_no_author_is_counted_apart(self) -> None:
        # A self-reviewed APPROVE (author recorded, same as the reviewer) and an author-less
        # REJECT both fail `critiqued` alone, and neither is answered by recording an author.
        # Mutants: a split that ignores the author, and one that ignores the verdict. The REJECT
        # is dated on the day the repair licence ended, so it is current work, not licensed.
        import critic  # noqa: PLC0415
        on = critic.REPAIR_VERB_RETIRED
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v41(root,
                 rows=("| US0003 | APPROVE | qa-seat | 2026-01-03 | - |\n"
                       "| US0005 | APPROVE | dev-seat | dev-seat | 2026-01-05 | - |\n"
                       f"| US0006 | REJECT | qa-seat | {on} | - |\n"),
                 extra={"stories/US0005-s.md": _story(5), "stories/US0006-s.md": _story(6)})
            item = self._item(root)
        self.assertEqual(["US0003"], item["approve_no_author"])
        self.assertEqual(["US0004", "US0005", "US0006"], item["other"])

    def test_with_no_cutoff_set_the_line_is_still_an_add(self) -> None:
        # The neighbour: a project with no key is told to add it, as before (BG0785).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v41(root, cutoff="")
            item = self._item(root)
        self.assertIn("add `conformance.adopt_after: US0004` to", item["detail"])
        self.assertNotIn("raise", item["detail"])
        self.assertEqual([], item["approve_no_author"])


if __name__ == "__main__":
    unittest.main()
