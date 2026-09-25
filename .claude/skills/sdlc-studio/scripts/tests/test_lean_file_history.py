"""US0930: a reviewer's brief carries the history of the files the unit touches.

`critic.py brief` lists the recent delivered units that changed the unit's files and the blocking
findings their reviews recorded, so a seat looks first for the repeats the record already holds.
The bounds are D0266's: at most five prior units, the three most recent per touched file, ranked by
shared files and then recency; test modules and `changelog.d/` fragments are not matched on; only
Done stories and Fixed or Verified bugs count; each unit carries at most three blocking findings of
200 characters, lesson class codes kept.

The corpus walk is reconcile's, shared with the already-delivered advisory, so AC5 pins that
advisory's output byte for byte through `reconcile.py detect`.

Every test builds a throwaway workspace and drives the shipped entry point.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/reconcile.py
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import reconcile  # noqa: E402

HEADING = "History of the files this unit touches"
LEDGER_HEAD = ("# Critic Verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- |\n")


def _unit(root: Path, uid: str, status: str, affects: list[str], date: str = "2026-01-01",
          title: str = "a change") -> None:
    type_ = "bug" if uid.startswith("BG") else "story"
    d = root / reconcile.sdlc_md.ARTIFACT_TYPES[type_][0]
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: {title}\n\n> **Status:** {status}\n> **Affects:** {', '.join(affects)}\n\n"
        "## Acceptance Criteria\n\n- **AC1:** Given x, then y\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        f"| {date} | sdlc-studio | {status} |\n", encoding="utf-8")


def _ledger(root: Path, *rows: tuple[str, str, str]) -> None:
    """Verdict rows as (unit, verdict, issues)."""
    p = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(LEDGER_HEAD + "".join(
        f"| {u} | {v} | qa-rev | {u}-build | 2026-01-02 | abcdef012345 | full | {i} |\n"
        for u, v, i in rows), encoding="utf-8")


def _workspace(d: str) -> Path:
    root = Path(d)
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True)
    (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
    return root


def _brief(root: Path, unit: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = critic.main(["brief", "--unit", unit, "--seat", "qa", "--tier", "full",
                          "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _section(brief: str) -> list[str]:
    """The history section's lines: the heading line and everything up to the next blank line."""
    lines = brief.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith(HEADING)]
    if len(starts) != 1:
        raise AssertionError(f"expected one history section, found {len(starts)}")
    out = []
    for ln in lines[starts[0]:]:
        if not ln.strip():
            break
        out.append(ln)
    return out


def _listed(section: list[str]) -> list[str]:
    return [m.group(1) for ln in section if (m := re.match(r"- ([A-Z]+\d+) ", ln))]


def _findings(section: list[str], uid: str) -> list[str]:
    """The indented lines under `uid`'s entry."""
    out, inside = [], False
    for ln in section:
        if ln.startswith("- "):
            inside = ln.startswith(f"- {uid} ")
        elif inside and ln.startswith("  - "):
            out.append(ln[4:])
    return out


class FileHistoryTests(unittest.TestCase):

    def test_the_three_most_recent_done_units_per_file_are_listed(self) -> None:
        """AC1. MUTANTS: order by id, oldest first, or list all five."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            # Dates deliberately out of id order: by date the newest three are 1, 3, 5.
            for uid, date in (("US0001", "2026-03-05"), ("US0002", "2026-03-01"),
                              ("US0003", "2026-03-04"), ("US0004", "2026-03-02"),
                              ("US0005", "2026-03-03")):
                _unit(root, uid, "Done", ["src/a.py"], date)
            _unit(root, "US0010", "In Progress", ["src/a.py"])
            _ledger(root)
            section = _section(_brief(root, "US0010"))
            self.assertEqual(["US0001", "US0003", "US0005"], _listed(section), section)
            self.assertIn("2026-03-05", section[1], "an entry does not show the date it ranks by")
            self.assertIn("src/a.py", section[1], "an entry does not name the file it changed")

    def test_each_entry_carries_at_most_three_blocking_findings(self) -> None:
        """AC2. MUTANTS: paste the whole Issues cell; keep non-blocking or pre-existing items;
        cut at 200 characters and lose the lesson class code; drop the no-findings line."""
        long = "the corpus walk " + "reads every artefact twice " * 12
        issues = "; ".join([
            f"[new] {long}[LC-002]",
            "[new] non-blocking: a nit about a docstring",
            "[pre-existing] test\\_old.py was already red",
            "[new] the second blocking defect",
            "[new] the third blocking defect [LC-006]",
            "[new] the fourth blocking defect",
        ])
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _unit(root, "US0001", "Done", ["src/a.py"], "2026-03-05")
            _unit(root, "US0002", "Done", ["src/a.py"], "2026-03-04")
            _unit(root, "US0010", "In Progress", ["src/a.py"])
            # An APPROVE's issues are not review findings of a defect; only REJECT rows count.
            _ledger(root, ("US0001", "APPROVE", "[new] an approving note that is no defect"),
                    ("US0001", "REJECT", issues),
                    ("US0002", "APPROVE", "[new] another approving note"))
            brief = _brief(root, "US0010")
            section = _section(brief)
            self.assertNotIn(issues, brief, "the whole Issues cell was pasted")
            found = _findings(section, "US0001")
            self.assertEqual(3, len(found), found)
            self.assertTrue(all(len(f) <= 200 for f in found), [len(f) for f in found])
            self.assertTrue(found[0].startswith("[new] the corpus walk reads every"), found[0])
            self.assertTrue(found[0].endswith("[LC-002]"), "the cut lost the lesson class code")
            self.assertEqual("[new] the second blocking defect", found[1])
            self.assertEqual("[new] the third blocking defect [LC-006]", found[2])
            joined = "\n".join(section)
            for skipped in ("non-blocking", "pre-existing", "fourth", "approving note",
                            "another approving"):
                self.assertNotIn(skipped, joined)
            self.assertEqual(["no review findings recorded"], _findings(section, "US0002"))

    def test_the_section_is_bounded_to_five_units(self) -> None:
        """AC3. MUTANTS: concatenate a list per file; rank by recency alone; match on test
        modules or changelog fragments."""
        files = [f"src/f{i:02}.py" for i in range(20)]
        own = [*files, "scripts/tests/test_f.py", "changelog.d/US0200.md"]
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            # Units changing several of this unit's files, each among the newest on its files.
            _unit(root, "US0301", "Done", files[0:5], "2026-02-01")
            _unit(root, "US0302", "Done", files[5:9], "2026-02-02")
            _unit(root, "US0303", "Done", files[9:12], "2026-02-03")
            _unit(root, "US0304", "Done", files[12:14], "2026-02-04")
            # Many older single-file units on every file: a per-file concatenation lists them all,
            # and the newest of them (US0440) takes the fifth place.
            n = 400
            for f in files:
                for day in (1, 2):
                    n += 1
                    _unit(root, f"US{n:04}", "Done", [f], f"2026-01-{day:02}")
            # The newest units of all share only the changelog fragment or only the test module;
            # matched on, either would take the fifth place.
            for i in range(6):
                _unit(root, f"US{501 + i:04}", "Done", [own[21 if i < 3 else 20]],
                      f"2026-03-{i + 1:02}")
            _unit(root, "US0200", "In Progress", own)
            _ledger(root)
            listed = _listed(_section(_brief(root, "US0200")))
            self.assertEqual(["US0301", "US0302", "US0303", "US0304", "US0440"], listed)

    def test_only_units_that_changed_code_are_listed(self) -> None:
        """AC4. MUTANTS: count every terminal status; list the unit itself; crash or drop the
        brief when nothing qualifies or no verdict ledger exists."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _unit(root, "US0010", "Done", ["src/a.py"], "2026-03-09")   # the unit itself
            for uid, status in (("US0001", "In Progress"), ("US0002", "Draft"),
                                ("US0003", "Superseded"), ("US0004", "Won't Implement"),
                                ("BG0001", "Won't Fix"), ("BG0002", "Closed"),
                                ("BG0003", "Open"), ("BG0004", "Superseded")):
                _unit(root, uid, status, ["src/a.py"], "2026-03-05")
            _ledger(root)
            brief = _brief(root, "US0010")
            self.assertEqual([f"{HEADING}: none recorded"], _section(brief))
            self.assertIn("Acceptance criteria", brief, "the brief was not produced")
            # Positive control: a Fixed and a Verified bug and a Done story DID change the code.
            _unit(root, "BG0005", "Fixed", ["src/a.py"], "2026-03-06")
            _unit(root, "BG0006", "Verified", ["src/a.py"], "2026-03-07")
            _unit(root, "US0005", "Done", ["src/a.py"], "2026-03-08")
            self.assertEqual(["US0005", "BG0006", "BG0005"],
                             _listed(_section(_brief(root, "US0010"))))
            # No verdict ledger at all: one line, and the brief still produced.
            (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").unlink()
            brief = _brief(root, "US0010")
            self.assertEqual([f"{HEADING}: none recorded"], _section(brief))
            self.assertIn("Acceptance criteria", brief)

    def test_the_fingerprint_does_not_digest_the_history(self) -> None:
        """The history moves when a sibling lands, so it stays out of the brief fingerprint.
        MUTANTS: digest the whole brief (the sibling marks the verdict unmatched); strip too
        much (a change to the unit's own criteria still matches); leave the heading in (a
        fingerprint recorded before the section existed stops matching)."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            for seat in ("engineering", "product"):
                (root / "sdlc-studio" / "personas" / "seats" / f"{seat}.md").write_text(
                    f"# {seat}\n", encoding="utf-8")
            _unit(root, "US0001", "Done", ["src/a.py"], "2026-03-01")
            _unit(root, "US0020", "In Progress", ["src/a.py"], "2026-03-02")
            _unit(root, "US0010", "In Progress", ["src/a.py"])
            _ledger(root)
            before = _brief(root, "US0010")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                critic.main(["brief", "--unit", "US0010", "--seat", "qa", "--tier", "full",
                             "--root", str(root)])
            fp = re.search(r"brief fingerprint: ([0-9a-f]{12})", err.getvalue()).group(1)

            def record() -> str:
                err = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                    rc = critic.main(["record", "--unit", "US0010", "--verdict", "REJECT",
                                      "--reviewer", "qa-rev", "--author", "dev", "--brief", fp,
                                      "--tier", "full", "--issues", "[new] x",
                                      "--root", str(root)])
                self.assertEqual(0, rc, err.getvalue())
                return critic.read_verdicts(root)[-1]["brief"]

            # A sibling sharing the file lands between briefing and recording.
            _unit(root, "US0020", "Done", ["src/a.py"], "2026-03-02")
            after = _brief(root, "US0010")
            self.assertNotEqual(_section(before), _section(after), "the history did not move")
            self.assertEqual(["US0020", "US0001"], _listed(_section(after)))
            self.assertEqual(fp, record(), "a sibling landing marked the verdict unmatched")
            # A fingerprint taken before the section existed: the same brief, no history.
            # By name, so the patch reaches whichever module `brief()` imports.
            with unittest.mock.patch("reconcile.file_history_section", lambda *a, **k: ""):
                legacy = critic.brief(root, "US0010", "qa")
            self.assertNotIn(HEADING, legacy)
            self.assertEqual(critic.brief_fingerprint(legacy),
                             critic.brief_fingerprint(critic.brief(root, "US0010", "qa")))
            # Positive control: the unit's own criteria changing still unmatches it.
            p = root / "sdlc-studio" / "stories" / "US0010-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace("then y", "then z"),
                         encoding="utf-8")
            self.assertEqual(f"{fp} {critic.UNMATCHED_MARK}", record())

    def test_the_already_delivered_advisory_is_unchanged(self) -> None:
        """AC5. MUTANTS: drop the advisory, or let the history's Done-only filter narrow the
        advisory's delivered set (a Won't Implement unit then stops being reported)."""
        skeleton = "prose reaches every creation script without a shell"
        done = skeleton + ": a shared fields-file helper adopted across the prose writers"
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            _unit(root, "US0125", "Draft", ["src/prose.py"], title=skeleton)
            _unit(root, "US0146", "Done", ["src/prose.py"], title=done)
            _unit(root, "BG0007", "Fixed", ["src/prose.py", "tests/test_prose.py"],
                  title=skeleton)
            _unit(root, "US0150", "Won't Implement", ["src/prose.py"], title=skeleton)
            _unit(root, "US0160", "Done", ["src/other.py"], title=skeleton)   # no shared file
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                reconcile.main(["detect", "--root", str(root), "--format", "json"])
            notes = json.loads(out.getvalue())["already_delivered_advisory"]
            self.assertEqual(
                [(n["id"], n["status"], n["delivered"], n["delivered_status"], n["shared"],
                  n["similarity"]) for n in notes],
                [("US0125", "Draft", "BG0007", "Fixed", ["src/prose.py"], 1.0),
                 ("US0125", "Draft", "US0146", "Done", ["src/prose.py"], 1.0),
                 ("US0125", "Draft", "US0150", "Won't Implement", ["src/prose.py"], 1.0)])
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                reconcile.main(["detect", "--root", str(root)])
            lines = [ln for ln in out.getvalue().splitlines() if "already-delivered" in ln]
            self.assertEqual(
                "advisory (already-delivered): US0125 (Draft) may already be delivered by "
                "US0146 (Done): 100% of the shorter title's words match and both declare "
                "src/prose.py - triage before it is built", lines[1])
            self.assertEqual(3, len(lines), lines)


if __name__ == "__main__":
    unittest.main()
