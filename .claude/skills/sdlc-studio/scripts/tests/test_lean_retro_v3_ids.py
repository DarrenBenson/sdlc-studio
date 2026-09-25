"""BG0778: the retro reads a v3 project's ULID ids in its dispositions and carried rows.

A fresh project is schema v3 and mints ids such as `BG-01M3CVPV`; a run record and a Batch line
carry them normalised (`BG01M3CVPV`). The retro's id readers matched only `(CR|BG|...)-?NNNN`,
so a disposition naming a ULID read as undecided and a carried row as naming no artefact. Both
readers now take their grammar from `lib/sdlc_md.py`. Each fixture tree cleans itself up.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import critic  # noqa: E402
import gitutil  # noqa: E402
import lessons  # noqa: E402
import retro  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

_SCRIPTS = HERE.parent
_CREATED = re.compile(r"created (\S+)")


def _ok(root: Path, script: str, *args: str) -> str:
    proc = subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} exited {proc.returncode}:\n"
                             f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def _retro_text(actions: list[tuple[str, str]], carried: list[str]) -> str:
    rows = "".join(f"| {finding} | {disp} |\n" for finding, disp in actions)
    known = "".join(f"| {issue} | accepted-risk | Maya | 2026-09-25 |\n" for issue in carried)
    return ("# RETRO0001: Sprint 1\n\n"
            "## Actions raised\n\n| Finding | Disposition |\n| --- | --- |\n" + rows + "\n"
            "## Known issues carried\n\n| Issue | Ruling | By | Date |\n"
            "| --- | --- | --- | --- |\n" + known)


class RetroV3IdTests(unittest.TestCase):

    def test_dispositions_and_carried_rows_read_v3_ids(self) -> None:
        """AC1. Ids minted by a real schema-v3 project, named bare and normalised, are read by
        both readers exactly as a four-digit id is - and the carried row joins the artefact's
        live status, which it can only do when the id was read whole."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)],
                           env=gitutil.git_env(), check=True, capture_output=True)
            _ok(root, "init.py", "run")
            self.assertGreaterEqual(sdlc_md.schema_version(root), 3)
            bug = _CREATED.search(_ok(root, "artifact.py", "new", "--type", "bug",
                                      "--title", "A widget leaks", "--affects", "src/widget.py",
                                      "--points", "1")).group(1)
            cr = _CREATED.search(_ok(root, "artifact.py", "new", "--type", "cr",
                                     "--title", "Widgets should not leak", "--affects",
                                     "src/widget.py", "--points", "1")).group(1)
            self.assertTrue(sdlc_md.is_v3_id(bug) and sdlc_md.is_v3_id(cr), (bug, cr))
            bare, normalised = bug, sdlc_md.norm_id(cr)
            self.assertNotIn("-", normalised)
            text = _retro_text(
                [("widget leak", bare), ("leak policy", normalised),
                 ("legacy finding", "BG0042")],
                [bare, normalised, "BG0042"])

            rows = retro.dispositions_in(text)
            self.assertEqual([(r["state"], r["detail"]) for r in rows],
                             [("filed", bare), ("filed", normalised), ("filed", "BG0042")])

            carried = retro.carried_issues(text, root=root)
            self.assertEqual([c["id"] for c in carried],
                             [sdlc_md.norm_id(bare), normalised, "BG0042"])
            self.assertEqual([c["ok"] for c in carried], [True, True, True])
            # The ULID rows resolve to the artefacts the project minted; the v2 control names
            # nothing in this project, so it is unreadable - read, but not found.
            minted = [(sdlc_md.extract_field(sdlc_md.find_by_id(root, uid)[0].read_text(
                encoding="utf-8"), "Status") or "").strip() for uid in (bare, cr)]
            self.assertTrue(all(minted), minted)
            self.assertEqual([c["status"] for c in carried[:2]], minted)
            self.assertEqual([c["unreadable"] for c in carried], [False, False, True])

    def test_prose_is_not_read_as_an_id(self) -> None:
        """AC2. A word shaped like an id prefix with no id after it is prose, not a filing."""
        # `SC2086` and `TS2345` are ShellCheck and TypeScript codes, not a charter or a test spec:
        # a retro names a finding filed as a CR, bug, story, RFC, epic or lesson.
        prose = ["USB stick", "EPIC saga", "CRXYZ12345", "BUGFIX", "ISSUES", "EP2000s", "SC2086",
                 "TS2345 suppressed"]
        text = _retro_text([(f"finding {n}", p) for n, p in enumerate(prose)], prose)
        self.assertEqual({r["state"] for r in retro.dispositions_in(text)}, {"undecided"})
        carried = retro.carried_issues(text)
        self.assertEqual([c["id"] for c in carried], [""] * len(prose))
        self.assertTrue(all(not c["ok"] for c in carried))
        self.assertEqual(retro.batch_ids("> **Batch:** " + ", ".join(prose) + "\n"), [])

    def test_the_retro_reads_ids_through_the_shared_grammar(self) -> None:
        """AC3. Both readers are the grammar `lib/sdlc_md.py` owns, and retro.py compiles no id
        grammar of its own. The shared grammar decides the edge cases: an uppercase non-id is
        not a unit id, and a five-digit v2 id is read whole, never truncated or dropped."""
        # One reader for dispositions, carried rows and the Batch line, narrowed from the shared
        # grammar to the families a finding is filed as; the Try unit narrows it further.
        self.assertIs(retro.ARTEFACT_ID_RE, retro.BATCH_ID_RE)
        self.assertIs(retro.ARTEFACT_ID_RE,
                      sdlc_md.cited_id_re(("CR", "BG", "US", "RFC", "EP", "LL")))
        self.assertIs(retro.TRY_UNIT_RE, sdlc_md.cited_id_re(("US", "BG", "CR")))

        # Narrowing changes the prefix alternation and nothing else of the shared grammar.
        def body(pattern: str) -> str:
            return re.sub(r"\(\?:[A-Z|]+\)", "", pattern, count=1)
        for reader in (retro.ARTEFACT_ID_RE, retro.TRY_UNIT_RE):
            self.assertEqual(body(reader.pattern), body(sdlc_md.CITED_ID_RE.pattern))

        prefixes = {p for _, p in sdlc_md.ARTIFACT_TYPES.values()}

        def alternated(value: str) -> set[str]:
            return {p for p in prefixes
                    if re.search(rf"(?<![A-Za-z]){p}\||\|{p}(?![A-Za-z])", value)}

        tree = ast.parse((_SCRIPTS / "retro.py").read_text(encoding="utf-8"))
        own = [node.value for node in ast.walk(tree)
               if isinstance(node, ast.Constant) and isinstance(node.value, str)
               and len(alternated(node.value)) >= 2]
        self.assertEqual(own, [], "retro.py spells an id-prefix alternation of its own")

        for reader in (retro.ARTEFACT_ID_RE, retro.BATCH_ID_RE):
            self.assertIsNone(reader.search("CRXYZ12345"))
            self.assertEqual(reader.search("see US01010 here").group(1), "US01010")
        self.assertEqual(retro.batch_ids("> **Batch:** CRXYZ12345, US01010, US-01M3CVPV\n"),
                         ["US01010", "US01M3CVPV"])
        # The Try item's unit, the third id reader here, follows the same grammar.
        # Normalised, as the critic's hit on the same unit is, whatever form the item wrote.
        self.assertEqual(retro.try_class("[LC-001] EP0001 drifted in US-01M3CVPV")["unit"],
                         "US01M3CVPV")
        for written in ("US-01M3CVPV", "US01M3CVPV", "us-0101", "US0101"):
            self.assertEqual(retro.try_class(f"[LC-001] it drifted in {written}")["unit"],
                             sdlc_md.norm_id(written), written)

    def test_a_try_item_and_a_review_on_one_dashed_unit_are_one_repeat(self) -> None:
        """A retro Try item and a REJECT that cite one class on one unit are one repeat, not
        two, when the unit is written dashed. Two would graduate the class (GRADUATE_AT 2) and
        file a CR on a single real repeat. Only the verdict ledger read is stood in for: the
        critic's own normalising read and the class store's counting run as shipped."""
        unit = "US-01M3CVPV"
        state = {"batch": [unit], run_state.REVIEW_BASE: {sdlc_md.norm_id(unit): 0}}
        rows = [{"verdict": "REJECT", "issues": "[new] the mutant was never applied [LC-001]"}]
        with mock.patch.object(critic, "delivery_rounds", lambda *_a, **_k: rows):
            review = critic.cited_lessons(".", state)
        self.assertEqual(len(review), 1)
        tag = retro.try_class(f"[LC-001] the mutant was never applied on {unit}")
        row = {"id": "LC-001", "recorded_run": "RUN-A", "hits": []}
        self.assertTrue(lessons.add_hit(row, "RUN-B", tag["unit"], "retro:RETRO0002"))
        _code, review_unit, finding = review[0]
        self.assertTrue(lessons.add_hit(row, "RUN-B", review_unit, "critic:RUN-B", finding))
        self.assertEqual(lessons.repeats_after_recording(row), 1)


if __name__ == "__main__":
    unittest.main()
