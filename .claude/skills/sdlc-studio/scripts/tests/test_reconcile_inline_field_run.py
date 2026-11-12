"""A metadata line joining several fields with `·` projects each field to its own value.

`reconcile`'s field projection reads an artefact's header the way `sdlc_md.extract_field` reads
it, so a field never swallows the ones after it on its line, and `reconcile apply` rewrites an
index cell that holds such a swallowed run to the single field value.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/reconcile.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
RECONCILE = SCRIPTS / "reconcile.py"
reconcile = loader.load_script("reconcile")
sdlc_md = reconcile.sdlc_md

#: Header lines, each with the fields on it and the value each must read as. Literal values,
#: so the projection and `extract_field` cannot agree on a wrong one.
HEADERS = {
    "joined run": ("> **Priority:** P2 · **Type:** Feature · **Points:** 3",
                   {"Priority": "P2", "Type": "Feature", "Points": "3"}),
    "persona first": ("> **Persona:** Priya · **Epic:** EP0001",
                      {"Persona": "Priya", "Epic": "EP0001"}),
    "hyphenated name": ("> **Severity:** High · **Raised-by:** Sam · **Owner:** Lee",
                        {"Severity": "High", "Raised-by": "Sam", "Owner": "Lee"}),
    "bold inside a value": ("> **Summary:** a **bold** word · **Owner:** Lee",
                            {"Summary": "a **bold** word", "Owner": "Lee"}),
    "escaped second name": ("> **Priority:** P2 · \\*\\*Type:\\*\\* group-chat (additive).",
                            {"Priority": "P2", "Type": None}),
}


#: The swallowed Priority run the bug quotes, its second field name escaped.
ESCAPED = "P2 · \\*\\*Type:\\*\\* group-chat / SSE contract (additive)."


def _artefact(line: str) -> str:
    return f"# CR0001: Inline run\n\n> **Status:** Proposed\n{line}\n\n## Summary\n\nBody.\n"


class InlineFieldRunTests(unittest.TestCase):

    def test_each_field_projected_as_extract_field_reads_it(self) -> None:
        """AC1. Mutants: the old end-of-line value (the first field swallows the rest); a name
        scan anchored to the line start only (the later fields are never read); a name grammar
        without the hyphen; a value cut at the first `**`."""
        for case, (line, want) in HEADERS.items():
            with self.subTest(case):
                text = _artefact(line)
                values = reconcile._file_field_values(text)
                for name, value in want.items():
                    self.assertEqual(value, sdlc_md.extract_field(text, name),
                                     f"premise: extract_field reads {name}")
                    self.assertEqual(value, values.get(name.lower()), name)
                self.assertEqual("Proposed", values.get("status"))

    def test_apply_repairs_swallowed_cells(self) -> None:
        """AC2. Mutants: projecting with the old reader (the swallowed run reads as unchanged);
        a repair written to the first cell only."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            crs = root / "sdlc-studio" / "change-requests"
            crs.mkdir(parents=True)
            (crs / "CR0001-inline-run.md").write_text(
                _artefact("> **Priority:** P2 · **Type:** Feature · **Points:** 3"),
                encoding="utf-8")
            (crs / "_index.md").write_text(
                "# Change Requests\n\n## All\n\n"
                "| ID | Title | Type | Priority | Status |\n|---|---|---|---|---|\n"
                "| [CR0001](CR0001-inline-run.md) | Inline run | Feature · **Points:** 3 "
                "| P2 · **Type:** Feature · **Points:** 3 | Proposed |\n"
                "| [CR0002](CR0002-escaped-run.md) | Escaped run | Bug "
                f"| {ESCAPED} | Proposed |\n", encoding="utf-8")
            (crs / "CR0002-escaped-run.md").write_text(
                _artefact(f"> **Priority:** {ESCAPED}").replace("CR0001: Inline",
                                                                "CR0002: Escaped"),
                encoding="utf-8")
            r = subprocess.run([sys.executable, "-B", str(RECONCILE), "apply", "--root", str(root)],
                               capture_output=True, text=True, timeout=300,
                               env=gitutil.git_env(), check=False)
            self.assertEqual(0, r.returncode, r.stderr + r.stdout)
            index = (crs / "_index.md").read_text(encoding="utf-8")
            rows = {ln.split("]")[0].strip("| ["):
                    [c.strip() for c in ln.strip().strip("|").split("|")]
                    for ln in index.splitlines() if ln.startswith("| [CR")}
            self.assertEqual(["Inline run", "Feature", "P2", "Proposed"], rows["CR0001"][1:])
            # The run as the bug that found it quoted it: an escaped second name is no field, so
            # Type keeps its cell and Priority is cut at the `·`.
            self.assertEqual(["Escaped run", "Bug", "P2", "Proposed"], rows["CR0002"][1:])
            self.assertNotIn("**Points:**", index)
            self.assertNotIn("group-chat", index)
            self.assertEqual([], reconcile.project_fields(root, "cr", dry_run=True)["drift"],
                             "the repaired index reads clean")


if __name__ == "__main__":
    unittest.main()
