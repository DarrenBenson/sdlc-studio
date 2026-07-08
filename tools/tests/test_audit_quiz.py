"""Unit tests for tools/bench/audit_quiz.py (US0088/CR0193) - synthetic fixture."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bench" / "audit_quiz.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_quiz", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["audit_quiz"] = mod
    spec.loader.exec_module(mod)
    return mod


aq = _load()


def _make_fixture(root: Path) -> Path:
    """A synthetic fixture: one module + one real test + a mutant that breaks it."""
    f = root / "fixtures" / "synth"
    (f / "audit" / "mutants").mkdir(parents=True)
    (f / "visible").mkdir()
    (f / "hidden").mkdir()
    quiz = [
        {"id": "Q1", "class": "D",
         "question": "Name a runnable check verifying that add() sums its inputs."},
        {"id": "Q2", "class": "T",
         "question": "Which document states the rounding rule, and what is it?"},
        {"id": "Q3", "class": "I",
         "question": "Was the change reviewed by someone other than its author?"},
    ]
    key = [
        {"id": "Q1", "mutant": "audit/mutants/calc_broken.py", "target_file": "calc.py"},
        {"id": "Q2", "fact_regex": "half.?even"},
        {"id": "Q3"},
    ]
    (f / "audit" / "quiz.json").write_text(json.dumps(quiz), encoding="utf-8")
    (f / "audit" / "answer_key.json").write_text(json.dumps(key), encoding="utf-8")
    (f / "audit" / "mutants" / "calc_broken.py").write_text(
        "def add(a, b):\n    return a - b\n", encoding="utf-8")
    return f


def _make_workspace(root: Path) -> Path:
    ws = root / "ws"
    ws.mkdir()
    (ws / "calc.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (ws / "test_calc.py").write_text(
        "from calc import add\n\ndef test_add_sums():\n    assert add(2, 3) == 5\n",
        encoding="utf-8")
    (ws / "README.md").write_text(
        "# calc\n\nAmounts round half-even to 2 decimal places.\n", encoding="utf-8")
    return ws


class ClassDTests(unittest.TestCase):
    def test_class_d_real_evidence_scores_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            answers = {"answers": [{"question_id": "Q1", "cited_test": "test_calc.py::test_add_sums"}]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            q1 = [p for p in r["per_question"] if p["id"] == "Q1"][0]
            self.assertEqual(q1["score"], 1, q1["reason"])

    def test_class_d_vacuous_test_scores_zero(self) -> None:
        # a test that passes regardless (does not really check add) fails the mutant leg
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            (ws / "test_vacuous.py").write_text(
                "def test_always_green():\n    assert True\n", encoding="utf-8")
            answers = {"answers": [{"question_id": "Q1", "cited_test": "test_vacuous.py::test_always_green"}]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            q1 = [p for p in r["per_question"] if p["id"] == "Q1"][0]
            self.assertEqual(q1["score"], 0)
            self.assertIn("still passes", q1["reason"])

    def test_class_d_missing_citation_scores_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            r = aq.grade("synth", ws, {"answers": []}, fixtures_dir=root / "fixtures")
            q1 = [p for p in r["per_question"] if p["id"] == "Q1"][0]
            self.assertEqual(q1["score"], 0)


class ClassTTests(unittest.TestCase):
    def test_class_t_verbatim_citation_scores_one(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            answers = {"answers": [{"question_id": "Q2", "answer": "round half-even to 2dp",
                                     "cited_path": "README.md",
                                     "cited_quote": "Amounts round half-even to 2 decimal places."}]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            q2 = [p for p in r["per_question"] if p["id"] == "Q2"][0]
            self.assertEqual(q2["score"], 1, q2["reason"])

    def test_class_t_fabricated_quote_scores_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            answers = {"answers": [{"question_id": "Q2", "answer": "half-even",
                                     "cited_path": "README.md",
                                     "cited_quote": "This sentence is not in the file."}]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            q2 = [p for p in r["per_question"] if p["id"] == "Q2"][0]
            self.assertEqual(q2["score"], 0)
            self.assertIn("verbatim", q2["reason"])

    def test_class_t_nonexistent_path_scores_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            answers = {"answers": [{"question_id": "Q2", "answer": "half-even",
                                     "cited_path": "docs/nope.md", "cited_quote": "x"}]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            q2 = [p for p in r["per_question"] if p["id"] == "Q2"][0]
            self.assertEqual(q2["score"], 0)


class IndependenceWeightTests(unittest.TestCase):
    def test_class_i_reported_descriptively_with_zero_weight(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _make_fixture(root)
            ws = _make_workspace(root)
            answers = {"answers": [
                {"question_id": "Q1", "cited_test": "test_calc.py::test_add_sums"},
                {"question_id": "Q2", "answer": "half-even", "cited_path": "README.md",
                 "cited_quote": "Amounts round half-even to 2 decimal places."},
                {"question_id": "Q3", "answer": "no - single agent"},
            ]}
            r = aq.grade("synth", ws, answers, fixtures_dir=root / "fixtures")
            # Q3 appears descriptively, contributes nothing to the score
            self.assertEqual(len(r["descriptive"]), 1)
            self.assertEqual(r["descriptive"][0]["id"], "Q3")
            self.assertEqual(len(r["per_question"]), 2)
            self.assertEqual(r["audit_score"], 1.0)  # 2/2 scored questions, Q3 excluded


if __name__ == "__main__":
    unittest.main()
