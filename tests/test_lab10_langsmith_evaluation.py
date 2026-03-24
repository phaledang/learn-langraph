"""
Tests for Lab 10: LangSmith Evaluation and Testing

Covers:
- Evaluator function patterns
- Test dataset structure
- Scoring logic
"""

import pytest


# ---------------------------------------------------------------------------
# Evaluator patterns
# ---------------------------------------------------------------------------

class TestEvaluators:
    """Test custom evaluator functions."""

    def test_exact_match_evaluator(self):
        def exact_match(prediction: str, reference: str) -> dict:
            return {
                "key": "exact_match",
                "score": 1.0 if prediction.strip() == reference.strip() else 0.0,
            }

        assert exact_match("Paris", "Paris")["score"] == 1.0
        assert exact_match("paris", "Paris")["score"] == 0.0
        assert exact_match("  Paris  ", "Paris")["score"] == 1.0

    def test_contains_evaluator(self):
        def contains(prediction: str, reference: str) -> dict:
            return {
                "key": "contains",
                "score": 1.0 if reference.lower() in prediction.lower() else 0.0,
            }

        assert contains("The capital is Paris.", "paris")["score"] == 1.0
        assert contains("Berlin is the capital.", "paris")["score"] == 0.0

    def test_length_evaluator(self):
        def length_check(prediction: str, max_length: int = 500) -> dict:
            return {
                "key": "length_check",
                "score": 1.0 if len(prediction) <= max_length else 0.0,
            }

        assert length_check("Short answer")["score"] == 1.0
        assert length_check("x" * 501)["score"] == 0.0

    def test_numeric_closeness_evaluator(self):
        def numeric_close(prediction: float, reference: float, tolerance: float = 0.1) -> dict:
            return {
                "key": "numeric_close",
                "score": 1.0 if abs(prediction - reference) <= tolerance else 0.0,
            }

        assert numeric_close(3.14, 3.14)["score"] == 1.0
        assert numeric_close(3.15, 3.14, tolerance=0.02)["score"] == 1.0
        assert numeric_close(5.0, 3.14)["score"] == 0.0


# ---------------------------------------------------------------------------
# Dataset structure tests
# ---------------------------------------------------------------------------

class TestDataset:
    """Test evaluation dataset structure."""

    def test_dataset_entry(self):
        entry = {
            "input": "What is the capital of France?",
            "expected": "Paris",
        }
        assert "input" in entry
        assert "expected" in entry

    def test_dataset_batch(self):
        dataset = [
            {"input": "Capital of France?", "expected": "Paris"},
            {"input": "Capital of Germany?", "expected": "Berlin"},
            {"input": "Capital of Japan?", "expected": "Tokyo"},
        ]
        assert len(dataset) == 3
        assert all("input" in d and "expected" in d for d in dataset)

    def test_evaluation_results_aggregation(self):
        scores = [1.0, 0.0, 1.0, 1.0, 0.0]
        avg = sum(scores) / len(scores)
        assert avg == pytest.approx(0.6)
