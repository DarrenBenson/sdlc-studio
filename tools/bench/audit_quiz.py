#!/usr/bin/env python3
"""Auditability-metric grader for benchmark runs (repo-only, CR0193).

Scores "can a maintainer with only the finished workspace answer standard audit
questions?" - the fifth pre-registered metric. Questions live HELD BACK in
`tools/bench/fixtures/<name>/audit/quiz.json` + `answer_key.json` (never copied into a
workspace by `runner.py prepare`). Scoring is outcome-based, never artifact-presence:
no question may name or presuppose an sdlc-studio artifact, and arm B can score 100%
via README, commit messages, docstrings and tests.

Question classes:
  D  deterministic evidence: the auditor cites a runnable check for a requirement; it
     scores 1 only if the cited test EXISTS in the workspace, PASSES on it, and FAILS
     on the per-question seeded mutant (audit/mutants/) - proof the evidence is real.
  T  trace/decision: the auditor answers {answer, cited_path, cited_quote}; scores 1
     only if the path exists, the quote is verbatim in that file, and the answer (or
     quote) matches the answer key's fact regex. Unanswerable-from-workspace = 0 -
     that IS the measurement.
  I  informational (e.g. reviewer-independence): reported descriptively, weight 0 -
     a single-agent arm structurally cannot score it, so any weight would be a
     by-construction point for the pipeline arm.

Subcommands:
  questions  Print a fixture's quiz questions (no answer key) - the auditor's input.
  grade      Score an auditor's answers file against a workspace.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parent
FIXTURES_DIR = BENCH_ROOT / "fixtures"


def load_quiz(fixture: str, fixtures_dir: Path = FIXTURES_DIR) -> tuple[list, dict]:
    audit_dir = fixtures_dir / fixture / "audit"
    quiz = json.loads((audit_dir / "quiz.json").read_text(encoding="utf-8"))
    key = json.loads((audit_dir / "answer_key.json").read_text(encoding="utf-8"))
    return quiz, {k["id"]: k for k in key}


def _run_pytest(node: str, cwd: Path, timeout: int = 120) -> bool:
    env = dict(os.environ, PYTHONSAFEPATH="1")
    r = subprocess.run([sys.executable, "-m", "pytest", node, "-q"],
                       cwd=str(cwd), capture_output=True, text=True,
                       timeout=timeout, env=env)
    return r.returncode == 0


def grade_class_d(q: dict, key: dict, answer: dict, workspace: Path,
                  fixtures_dir: Path = FIXTURES_DIR, fixture: str = "") -> dict:
    """1 iff the cited check exists, passes on the workspace, and fails on the mutant."""
    cited = (answer or {}).get("cited_test", "").strip()
    if not cited:
        return {"score": 0, "reason": "no runnable check cited"}
    node_file = cited.split("::")[0]
    if not (workspace / node_file).exists():
        return {"score": 0, "reason": f"cited file {node_file} not in workspace"}
    if not _run_pytest(cited, workspace):
        return {"score": 0, "reason": "cited check does not pass on the workspace"}
    mutant_rel = key.get("mutant")
    target_rel = key.get("target_file")
    if not mutant_rel or not target_rel:
        return {"score": 0, "reason": "answer key missing mutant/target_file"}
    mutant = fixtures_dir / fixture / mutant_rel
    with tempfile.TemporaryDirectory() as tmp:
        mutated = Path(tmp) / "ws"
        shutil.copytree(workspace, mutated,
                        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git"))
        shutil.copy2(mutant, mutated / target_rel)
        if _run_pytest(cited, mutated):
            return {"score": 0,
                    "reason": "cited check still passes with the requirement broken - "
                              "not real evidence for this requirement"}
    return {"score": 1, "reason": "check passes on workspace, fails on mutant"}


def grade_class_t(q: dict, key: dict, answer: dict, workspace: Path) -> dict:
    """1 iff cited_path exists, cited_quote is verbatim in it, and the fact regex matches."""
    a = answer or {}
    cited_path = (a.get("cited_path") or "").strip()
    cited_quote = (a.get("cited_quote") or "").strip()
    fact = (a.get("answer") or "").strip()
    if not cited_path or not cited_quote:
        return {"score": 0, "reason": "no citation given"}
    target = workspace / cited_path
    if not target.is_file():
        return {"score": 0, "reason": f"cited path {cited_path} not in workspace"}
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"score": 0, "reason": f"cited path {cited_path} unreadable"}
    if cited_quote not in text:
        return {"score": 0, "reason": "cited quote is not verbatim in the cited file"}
    pattern = key.get("fact_regex", "")
    if pattern and not (re.search(pattern, fact, re.I) or re.search(pattern, cited_quote, re.I)):
        return {"score": 0, "reason": "answer does not match the expected fact"}
    return {"score": 1, "reason": "citation verified"}


def grade(fixture: str, workspace: Path, answers: dict,
          fixtures_dir: Path = FIXTURES_DIR) -> dict:
    """{audit_score, per_question, descriptive}. audit_score averages class D+T only;
    class I is reported descriptively at weight 0."""
    quiz, key = load_quiz(fixture, fixtures_dir)
    answers_by_id = {a.get("question_id"): a for a in answers.get("answers", [])}
    per_question, descriptive, scored = [], [], []
    for q in quiz:
        qid, qclass = q["id"], q.get("class", "T")
        a = answers_by_id.get(qid)
        if qclass == "I":
            descriptive.append({"id": qid, "question": q["question"],
                                 "answer": (a or {}).get("answer")})
            continue
        if qclass == "D":
            r = grade_class_d(q, key.get(qid, {}), a, workspace,
                              fixtures_dir=fixtures_dir, fixture=fixture)
        else:
            r = grade_class_t(q, key.get(qid, {}), a, workspace)
        per_question.append({"id": qid, "class": qclass, **r})
        scored.append(r["score"])
    return {"audit_score": round(sum(scored) / len(scored), 3) if scored else None,
            "per_question": per_question, "descriptive": descriptive}


def cmd_questions(args: argparse.Namespace) -> int:
    quiz, _key = load_quiz(args.fixture)
    print(json.dumps([{k: v for k, v in q.items()} for q in quiz], indent=2))
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    r = grade(args.fixture, Path(args.workspace), answers)
    print(json.dumps(r, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Auditability-metric grader (repo-only).")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("questions", help="Print a fixture's quiz (no answer key).")
    q.add_argument("--fixture", required=True)
    q.set_defaults(func=cmd_questions)
    g = sub.add_parser("grade", help="Score an auditor's answers against a workspace.")
    g.add_argument("--fixture", required=True)
    g.add_argument("--workspace", required=True)
    g.add_argument("--answers", required=True, help="auditor answers JSON")
    g.set_defaults(func=cmd_grade)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
