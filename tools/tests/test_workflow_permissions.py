"""Regression guard for BG0058: every GitHub Actions workflow must declare an explicit
top-level `permissions:` block, so the workflow token never silently inherits the
repository/org default (which may be the legacy permissive token).

Parsed without PyYAML (stdlib only) - a top-level `permissions:` key is a line with no
leading whitespace. This is a lint-style structural check, not a full YAML parse.
"""
import unittest
from pathlib import Path

WORKFLOWS = Path(__file__).resolve().parents[2] / ".github" / "workflows"


def _has_top_level_permissions(text: str) -> bool:
    return any(line.rstrip().startswith("permissions:") and line[:1] not in (" ", "\t")
              for line in text.splitlines())


class WorkflowPermissions(unittest.TestCase):
    def test_every_workflow_declares_permissions(self) -> None:
        workflows = sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))
        self.assertTrue(workflows, "no workflow files found - wrong path?")
        missing = [w.name for w in workflows
                   if not _has_top_level_permissions(w.read_text(encoding="utf-8"))]
        self.assertEqual(missing, [], f"workflows without a top-level permissions block: {missing}")


if __name__ == "__main__":
    unittest.main()
