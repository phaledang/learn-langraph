"""
Shared pytest fixtures and configuration for all lab tests.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


# ---------------------------------------------------------------------------
# Ensure key project directories are importable
# ---------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_paths_to_add = [
    PROJECT_ROOT,
    os.path.join(PROJECT_ROOT, "shared"),
    os.path.join(PROJECT_ROOT, "labs", "lab13-pdf-and_image_to_csv"),
    os.path.join(PROJECT_ROOT, "labs", "lab14-mcp-server"),
    os.path.join(PROJECT_ROOT, "labs", "lab14-mcp-sharepoint"),
]
for p in _paths_to_add:
    if p not in sys.path:
        sys.path.insert(0, p)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_env_openai(monkeypatch):
    """Set minimal OpenAI environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-fake")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")


@pytest.fixture
def mock_env_azure_openai(monkeypatch):
    """Set minimal Azure OpenAI environment variables for testing."""
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-azure-key-fake")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")


@pytest.fixture
def mock_llm_response():
    """Return a factory that creates a mock LLM with a preset response."""
    def _make(content="Mock LLM response"):
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = content
        mock_llm.invoke.return_value = mock_response
        mock_llm.batch.return_value = [mock_response]
        return mock_llm
    return _make


@pytest.fixture
def mock_db_connection_string(monkeypatch):
    """Set a fake database connection string for testing."""
    monkeypatch.setenv(
        "DATABASE_CONNECTION_STRING",
        "postgresql://testuser:testpass@localhost:5432/testdb"
    )
