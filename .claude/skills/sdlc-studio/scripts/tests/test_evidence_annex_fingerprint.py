"""A consumer recomputes a report's fingerprint from the evidence annex alone.

`reference-evidence-schema.md` states the schema-2 fingerprint under `### Report fingerprint`:
the steps, a reference implementation in a fenced Python block, and the figures and sections the
digest leaves out as tables. These tests take the block off the page and run it with
`python3 -I` from an empty working directory, so nothing the skill ships can stand in for it,
over a page `sprint close` files in a fixture and over every schema-2 page this repository holds.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-evidence-schema.md
from __future__ import annotations

import ast
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil
import sprint_report
import test_evidence_annex_report as annex

REPO = Path(__file__).resolve().parents[5]
REFERENCE_SPRINT = Path(__file__).resolve().parents[2] / "reference-sprint.md"
#: The schema-2 pages this repository held when the procedure was published: every later page
#: joins by the glob, and fewer than this means the glob found the wrong place.
COMMITTED_FLOOR = 25

_FENCE = re.compile(r"^```python\s*$")


def reference_implementation() -> str:
    """The one fenced Python block under `### Report fingerprint`."""
    lines = annex._block("Report fingerprint")
    starts = [i for i, ln in enumerate(lines) if _FENCE.match(ln)]
    if len(starts) != 1:
        raise AssertionError(f"the fingerprint section holds {len(starts)} Python blocks")
    body = []
    for ln in lines[starts[0] + 1:]:
        if ln.startswith("```"):
            return "\n".join(body) + "\n"
        body.append(ln)
    raise AssertionError("the fingerprint section's Python block is never closed")


def committed_pages() -> list[Path]:
    """Every schema-2 page the repository holds, found by glob."""
    out = []
    for p in sorted((REPO / "sdlc-studio" / "reports").glob("RPT*.json")):
        if json.loads(p.read_text(encoding="utf-8")).get("schema") == 2:
            out.append(p)
    return out


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.:;])\s+", " ".join(text.split())) if s]


def states_unsigned(text: str) -> bool:
    """Does one sentence say the signature block, the generation time and each figure's source
    are not signed?"""
    return any(all(w in s for w in ("signature block", "generation time", "source",
                                    "not signed"))
               for s in _sentences(text))


class FingerprintAnnexTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        patcher = unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        # An empty working directory holding only the extracted block: `-I` keeps the
        # environment and the user's site out, and nothing beside the script can be imported.
        self.work = self.tmp / "consumer"
        self.work.mkdir()
        self.script = self.work / "fingerprint.py"
        self.script.write_text(reference_implementation(), encoding="utf-8")

    def recompute(self, *pages: Path) -> list[str]:
        proc = subprocess.run([sys.executable, "-I", str(self.script), *map(str, pages)],
                              cwd=self.work, capture_output=True, text=True,
                              env={"PATH": os.environ.get("PATH", "")})
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout.split()

    def _filed(self) -> Path:
        root = self.tmp / "run"
        root.mkdir()
        annex._run(root, True)
        page = annex._close(root)
        return root / "sdlc-studio" / "reports" / f"{page['report_id']}.json"

    def test_the_annex_procedure_recomputes_filed_fingerprints_in_isolation(self) -> None:
        """AC1. MUTANT: drop a step of the procedure (the row index, the `unit_rows` pass, the
        price table entry, an exclusion) or change the digest's serialisation - a page's
        recorded fingerprint no longer comes back."""
        fixture = self._filed()
        page = json.loads(fixture.read_text(encoding="utf-8"))
        # The fixture exercises the envelope entry and the rows; the committed pages add the
        # older shapes the glob finds.
        self.assertEqual(sprint_report.TABLE_REPLAYED, page.get(sprint_report.TABLE_RULE))
        self.assertTrue(any(s.get("rows") for s in page["sections"]))
        committed = committed_pages()
        self.assertGreaterEqual(len(committed), COMMITTED_FLOOR, "the glob found too few pages")
        pages = [fixture, *committed]
        recorded = [json.loads(p.read_text(encoding="utf-8"))["fingerprint"] for p in pages]
        self.assertEqual(recorded, self.recompute(*pages))

        # Controls on the fixture: what is outside the digest moves nothing, a value moves it.
        def digest_of(edit) -> str:
            changed = copy.deepcopy(page)
            edit(changed)
            p = self.tmp / "edited.json"
            p.write_text(json.dumps(changed, indent=2), encoding="utf-8")
            # The procedure agrees with the shipped digest on every edited page too.
            got = self.recompute(p)[0]
            self.assertEqual(sprint_report.fingerprint(changed), got)
            return got

        figure = next(f for s in page["sections"] if s["key"] not in
                      sprint_report.SECTIONS_OUTSIDE_THE_DIGEST
                      for f in (s.get("figures") or {}).values())
        key = figure["key"]

        def set_on(field, value):
            def edit(changed):
                for s in changed["sections"]:
                    for f in (s.get("figures") or {}).values():
                        if f is not None and f.get("key") == key:
                            f[field] = value
            return edit

        for unsigned in (set_on("source", "elsewhere"),
                         lambda c: c.update(generated_at="2030-01-01T00:00:00Z"),
                         lambda c: c.update(signature={"principal": "someone"})):
            self.assertEqual(page["fingerprint"], digest_of(unsigned))
        self.assertNotEqual(page["fingerprint"], digest_of(set_on("value", "moved")))
        self.assertNotEqual(page["fingerprint"],
                            digest_of(lambda c: c.update(price_table={"moved": True})))

        # No filed page here holds a section-level marker, so one is set: it enters the digest.
        def unmeasured(changed):
            sec = changed["sections"][0]
            sec["not_measured"] = {"key": sec["key"], "value": "NOT MEASURED",
                                   "source": "the harness meter", "reason": "a control"}
        self.assertNotEqual(page["fingerprint"], digest_of(unmeasured))

    def test_the_annex_exclusions_match_the_code(self) -> None:
        """AC2. MUTANT: add or drop a row in either exclusion table, or a name in the code's
        tuples, or drop the not-signed sentence from either page - the comparison fails."""
        figures = {(annex._key(r["Section"]), annex._key(r["Figure"]))
                   for r in annex.annex_table("Report figures outside the digest")}
        sections = set(annex.keyed("Report sections outside the digest", "Section"))
        self.assertEqual(set(sprint_report.OUTSIDE_THE_DIGEST), figures)
        self.assertEqual(set(sprint_report.SECTIONS_OUTSIDE_THE_DIGEST), sections)
        # The reference implementation carries the same two lists, so the tables, the code and
        # the procedure a consumer runs are one set.
        held = {}
        for node in ast.parse(reference_implementation()).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                held[node.targets[0].id] = ast.literal_eval(node.value)
        self.assertEqual(figures, set(held["OUTSIDE_THE_DIGEST"]))
        self.assertEqual(sections, set(held["SECTIONS_OUTSIDE_THE_DIGEST"]))
        self.assertTrue(states_unsigned("\n".join(annex._block("Report fingerprint"))),
                        "the annex does not say what is not signed")
        self.assertTrue(states_unsigned(REFERENCE_SPRINT.read_text(encoding="utf-8")),
                        "reference-sprint.md does not say what is not signed")


if __name__ == "__main__":
    unittest.main()
