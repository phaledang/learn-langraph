"""
Tests for Lab 09: LangSmith Tracing and Monitoring

Covers:
- LangSmith environment variable setup
- Tracing configuration
- Custom metadata / tags patterns
"""

import os
import pytest


# ---------------------------------------------------------------------------
# Environment setup tests
# ---------------------------------------------------------------------------

class TestLangSmithConfig:
    """Verify tracing env vars can be set correctly."""

    def test_tracing_env_vars(self, monkeypatch):
        monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")
        monkeypatch.setenv("LANGCHAIN_API_KEY", "ls-test-key")
        monkeypatch.setenv("LANGCHAIN_PROJECT", "test-project")

        assert os.getenv("LANGCHAIN_TRACING_V2") == "true"
        assert os.getenv("LANGCHAIN_API_KEY") == "ls-test-key"
        assert os.getenv("LANGCHAIN_PROJECT") == "test-project"

    def test_tracing_disabled_by_default(self, monkeypatch):
        monkeypatch.delenv("LANGCHAIN_TRACING_V2", raising=False)
        assert os.getenv("LANGCHAIN_TRACING_V2") is None


# ---------------------------------------------------------------------------
# Custom metadata / tags
# ---------------------------------------------------------------------------

class TestTracingMetadata:
    """Test patterns for attaching metadata to runs."""

    def test_metadata_dict_structure(self):
        metadata = {
            "user_id": "user_123",
            "session_id": "sess_456",
            "environment": "staging",
        }
        assert "user_id" in metadata
        assert metadata["environment"] == "staging"

    def test_tags_list(self):
        tags = ["production", "v2", "experiment-A"]
        assert "production" in tags
        assert len(tags) == 3

    def test_run_config_pattern(self):
        """LangSmith config pattern used in chain.invoke(..., config=...)."""
        config = {
            "metadata": {"user_id": "u1"},
            "tags": ["test"],
            "run_name": "my-run",
        }
        assert config["run_name"] == "my-run"
        assert "test" in config["tags"]
