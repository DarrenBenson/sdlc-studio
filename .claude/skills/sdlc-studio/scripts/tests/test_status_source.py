"""Single-source guard: the per-type status vocabulary is declared ONCE, in `lib.sdlc_md`.

`artifact.SPEC` and `file_finding.TYPES` both carry a per-type status cell. Both must DERIVE
it from the shared vocab, never restate it - three hand-kept copies of one table agree until
the day they do not, and the drift is silent (a finding filed at a status the validator does
not know, a `close` that moves an artefact to a state outside the vocab).

These tests fail if any of the three sources is edited alone: the pinned table below is the
behaviour of record (a deliberate vocab change updates it), and the cross-source assertions
fail the moment a divergent literal is re-hardcoded in either creator.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load("artifact")
file_finding = _load("file_finding")

# The behaviour of record: (create status, default close status) per type, in the order the
# creator declares them (the order the CLI's `--type` choices are printed in). Pinned here so
# a refactor of WHERE these values come from cannot quietly change WHAT they are.
EXPECTED: dict[str, tuple[str, str]] = {
    "epic": ("Draft", "Done"),
    "story": ("Draft", "Done"),
    "plan": ("Draft", "Complete"),
    "test-spec": ("Draft", "Complete"),
    "workflow": ("Created", "Done"),
    "bug": ("Open", "Fixed"),
    "cr": ("Proposed", "Complete"),
    "rfc": ("Draft", "Accepted"),
}


class StatusVocabSingleSource(unittest.TestCase):
    """CR0249: one declaration of the per-type statuses; the creators derive from it."""

    def test_shared_source_declares_the_pinned_statuses(self) -> None:
        for t, (create, terminal) in EXPECTED.items():
            self.assertEqual(sdlc_md.create_status(t), create, f"{t} create status")
            self.assertEqual(sdlc_md.default_terminal_status(t), terminal, f"{t} close status")

    def test_artifact_spec_derives_every_status_from_the_shared_source(self) -> None:
        # Fails if a divergent status literal is re-hardcoded in artifact.SPEC.
        for t in artifact.SPEC:
            self.assertEqual(artifact.SPEC[t]["status"], sdlc_md.create_status(t),
                             f"artifact.SPEC[{t!r}]['status'] has drifted from sdlc_md")
            self.assertEqual(artifact.SPEC[t]["terminal"], sdlc_md.default_terminal_status(t),
                             f"artifact.SPEC[{t!r}]['terminal'] has drifted from sdlc_md")

    def test_file_finding_types_derives_every_status_from_the_shared_source(self) -> None:
        # Fails if a divergent status literal is re-hardcoded in file_finding.TYPES.
        for t in file_finding.TYPES:
            self.assertEqual(file_finding.TYPES[t]["status"], sdlc_md.create_status(t),
                             f"file_finding.TYPES[{t!r}]['status'] has drifted from sdlc_md")

    def test_both_creators_agree_on_a_finding_status(self) -> None:
        # The filer and the general creator mint the same type: one born state, not two.
        for t in file_finding.TYPES:
            self.assertEqual(file_finding.TYPES[t]["status"], artifact.SPEC[t]["status"], t)

    def test_creator_shape_and_coverage_are_unchanged(self) -> None:
        # SPEC keeps its shape (other code reads status/terminal/dash) and its order (the CLI
        # `--type` choices), and covers exactly the types the vocab knows.
        self.assertEqual(list(artifact.SPEC), list(EXPECTED))
        self.assertEqual(set(artifact.SPEC), set(sdlc_md.STATUS_VOCAB))
        for t, entry in artifact.SPEC.items():
            self.assertEqual(set(entry), {"status", "terminal", "dash"}, t)
            self.assertIsInstance(entry["dash"], bool)
        self.assertEqual(set(file_finding.TYPES), set(sdlc_md.FINDING_TYPES))

    def test_every_derived_status_is_a_member_of_its_type_vocab(self) -> None:
        # The derivation can never name a status the validator would reject.
        for t in artifact.SPEC:
            self.assertIn(artifact.SPEC[t]["status"], sdlc_md.status_vocab(t), t)
            self.assertIn(artifact.SPEC[t]["terminal"], sdlc_md.terminal_statuses(t), t)

    def test_close_defaults_its_target_from_the_shared_source(self) -> None:
        # `close` with no --status must land on the vocab's close state, not a private table.
        with tempfile.TemporaryDirectory() as d:
            for t, (_create, terminal) in EXPECTED.items():
                prefix = sdlc_md.ARTIFACT_TYPES[t][1]
                r = artifact.close(Path(d), f"{prefix}0001", dry_run=True)
                self.assertEqual(r["type"], t)
                self.assertEqual(r["to"], terminal, f"close default for {t}")

    def test_unknown_type_yields_no_status(self) -> None:
        self.assertEqual(sdlc_md.create_status("persona"), "")
        self.assertEqual(sdlc_md.default_terminal_status("persona"), "")


if __name__ == "__main__":
    unittest.main()
