"""BG0943: `config.py show --key` reads every leaf key config-defaults.yaml declares.

Filed as "show drops a section's keys after a nested list", the defect was found on this
repository, whose `.config.yaml` keeps a `review:` section holding only comments since its last
key was retired. YAML reads that section as null, and the merge let the null replace the whole
`review` mapping the defaults declare, so `review.max_rounds`, `review.line_coverage`,
`review.blocking_priority` and their siblings read as declared nowhere. `config.get` reads
through the same merge, so it read them as absent too; a section that sets nothing now keeps
the defaults' keys for both.

Every leaf of the shipped config-defaults.yaml is put through the shipped entry point,
`config.main(["show", "--key", ...])`, in a project carrying that comment-only section, in a
project with no `.config.yaml`, and in this repository as it stands.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/config.py
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover - config.py needs PyYAML; so does this test
    yaml = None

config = loader.load_script("config")
REPO = Path(__file__).resolve().parents[5]
#: The shape this repository's own `.config.yaml` carries: a section whose body is comments.
COMMENT_ONLY = ("schema_version: 2\n"
                "review:\n"
                "  # The review policy setting was retired: nothing read it.\n"
                "  # The round cap is left at the shipped default.\n"
                "engagement_floor:\n"
                "  adopt_after: 1\n")
UNDECLARED = "review.no_such_key"
_ABSENT = object()


def _leaves(node, prefix: str = ""):
    """(dotted key, value) for every leaf, as `config._leaf_sources` reads one: a non-empty
    mapping is a section, anything else (a list, a scalar, an empty mapping) a leaf."""
    for key, val in node.items():
        dotted = f"{prefix}{key}"
        if isinstance(val, dict) and val:
            yield from _leaves(val, dotted + ".")
        else:
            yield dotted, val


def _show(root: Path, key: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = config.main(["show", "--key", key, "--root", str(root)])
    return rc, out.getvalue().strip(), err.getvalue()


def _dumps(value) -> str:
    return json.dumps(value, default=config._json_default)


@unittest.skipIf(yaml is None, "config.py needs PyYAML")
class ConfigKeysAfterListTests(unittest.TestCase):

    def test_keys_after_a_list_are_read(self) -> None:
        """AC1. MUTANT: HEAD's `_deep_merge`, which lets a section the project leaves null
        replace the mapping the defaults declare - `show --key review.max_rounds` then exits 1
        saying no file declares it, and `config.get` returns its fallback. The positive control
        is the undeclared key, still refused, and the project with no `.config.yaml`."""
        defaults = yaml.safe_load(config.DEFAULTS_PATH.read_text(encoding="utf-8"))
        leaves = dict(_leaves(defaults))
        for named in ("review.max_rounds", "review.line_coverage", "review.blocking_priority"):
            self.assertIn(named, leaves, f"premise: config-defaults.yaml declares {named}")
        self.assertNotIn(UNDECLARED, leaves, "premise: the undeclared key is declared nowhere")

        with tempfile.TemporaryDirectory() as d:
            commented, bare = Path(d) / "commented", Path(d) / "bare"
            (commented / "sdlc-studio").mkdir(parents=True)
            (bare / "sdlc-studio").mkdir(parents=True)
            (commented / "sdlc-studio" / ".config.yaml").write_text(COMMENT_ONLY,
                                                                     encoding="utf-8")
            self.assertIsNone(yaml.safe_load(COMMENT_ONLY)["review"],
                              "premise: a comment-only section reads as null")
            for label, root in (("comment-only section", commented), ("no .config.yaml", bare),
                                ("this repository", REPO)):
                project = config._project_override(root)
                for key, shipped in leaves.items():
                    with self.subTest(project=label, key=key):
                        rc, out, err = _show(root, key)
                        self.assertEqual(0, rc, f"show reads {key} as undeclared: {err}")
                        got = config.get(root, key, _ABSENT)
                        self.assertIsNot(got, _ABSENT, f"config.get does not read {key}")
                        self.assertEqual(_dumps(got), out)
                        if root is not REPO:
                            set_here = _leaves(project) if isinstance(project, dict) else ()
                            want = dict(set_here).get(key, shipped)
                            self.assertEqual(_dumps(want), out)
                with self.subTest(project=label, key=UNDECLARED):
                    rc, out, err = _show(root, UNDECLARED)
                    self.assertEqual(1, rc, out)
                    self.assertIn(f"no key `{UNDECLARED}`", err)


if __name__ == "__main__":
    unittest.main()
