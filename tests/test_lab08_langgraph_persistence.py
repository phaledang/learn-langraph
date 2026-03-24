"""
Tests for Lab 08: LangGraph State Persistence

Covers:
- StateDocument pydantic model
- detect_database_type factory logic
- create_state_persistence factory
- ConversationState schema
- Persistent graph construction
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from shared.state_persistence.base import BaseStatePersistence, StateDocument
from shared.state_persistence.factory import detect_database_type, create_state_persistence


# ---------------------------------------------------------------------------
# StateDocument tests
# ---------------------------------------------------------------------------

class TestStateDocument:
    def test_create_state_document(self):
        doc = StateDocument(
            thread_id="t1",
            checkpoint_id="cp1",
            state={"step": 0, "messages": []},
            metadata={"user": "tester"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert doc.thread_id == "t1"
        assert doc.checkpoint_id == "cp1"
        assert doc.state["step"] == 0

    def test_state_document_optional_metadata(self):
        doc = StateDocument(
            thread_id="t2",
            checkpoint_id="cp2",
            state={"x": 1},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        assert doc.metadata is None

    def test_state_document_serialization(self):
        now = datetime.utcnow()
        doc = StateDocument(
            thread_id="t3",
            checkpoint_id="cp3",
            state={"data": "value"},
            created_at=now,
            updated_at=now,
        )
        d = doc.model_dump()
        assert d["thread_id"] == "t3"
        assert "data" in d["state"]


# ---------------------------------------------------------------------------
# detect_database_type tests
# ---------------------------------------------------------------------------

class TestDetectDatabaseType:
    def test_cosmosdb(self):
        conn = "AccountEndpoint=https://myaccount.documents.azure.com:443/;AccountKey=abc123=="
        assert detect_database_type(conn) == "cosmosdb"

    def test_postgresql(self):
        conn = "postgresql://user:pass@localhost:5432/mydb"
        assert detect_database_type(conn) == "postgresql"

    def test_postgres_alias(self):
        conn = "postgres://user:pass@localhost:5432/mydb"
        assert detect_database_type(conn) == "postgresql"

    def test_sqlserver(self):
        conn = "mssql+pyodbc://user:pass@server:1433/db?driver=ODBC+Driver+17"
        assert detect_database_type(conn) == "sqlserver"

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unable to detect"):
            detect_database_type("redis://localhost:6379")


# ---------------------------------------------------------------------------
# create_state_persistence factory tests
# ---------------------------------------------------------------------------

class TestCreateStatePersistence:
    def test_missing_connection_string_raises(self, monkeypatch):
        monkeypatch.delenv("DATABASE_CONNECTION_STRING", raising=False)
        with pytest.raises(ValueError, match="No connection string"):
            create_state_persistence()

    @patch("shared.state_persistence.factory.PostgreSQLStatePersistence")
    def test_creates_postgresql(self, MockPG, monkeypatch):
        monkeypatch.setenv(
            "DATABASE_CONNECTION_STRING",
            "postgresql://user:pass@localhost/db"
        )
        result = create_state_persistence()
        MockPG.assert_called_once()

    @patch("shared.state_persistence.factory.CosmosDBStatePersistence")
    def test_creates_cosmosdb(self, MockCosmos, monkeypatch):
        monkeypatch.setenv(
            "DATABASE_CONNECTION_STRING",
            "AccountEndpoint=https://x.documents.azure.com:443/;AccountKey=key=="
        )
        result = create_state_persistence()
        MockCosmos.assert_called_once()

    @patch("shared.state_persistence.factory.SQLServerStatePersistence")
    def test_creates_sqlserver(self, MockSQL, monkeypatch):
        monkeypatch.setenv(
            "DATABASE_CONNECTION_STRING",
            "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17"
        )
        result = create_state_persistence()
        MockSQL.assert_called_once()

    @patch("shared.state_persistence.factory.PostgreSQLStatePersistence")
    def test_custom_table_name(self, MockPG, monkeypatch):
        conn = "postgresql://user:pass@localhost/db"
        create_state_persistence(connection_string=conn, table_name="my_table")
        MockPG.assert_called_once_with(conn, "my_table")


# ---------------------------------------------------------------------------
# Conversation graph tests (no LLM)
# ---------------------------------------------------------------------------

class TestConversationGraph:
    """Test building a persistent graph without LLM calls."""

    def test_graph_with_memory_saver(self):
        from typing import TypedDict, Annotated
        from langgraph.graph import StateGraph, END, add_messages
        from langgraph.checkpoint.memory import MemorySaver
        from langchain_core.messages import HumanMessage, BaseMessage

        class ConvState(TypedDict):
            messages: Annotated[list[BaseMessage], add_messages]
            step: int

        def process(state: ConvState) -> ConvState:
            state["step"] += 1
            return state

        wf = StateGraph(ConvState)
        wf.add_node("process", process)
        wf.set_entry_point("process")
        wf.add_edge("process", END)

        memory = MemorySaver()
        app = wf.compile(checkpointer=memory)

        config = {"configurable": {"thread_id": "conv_1"}}
        result = app.invoke(
            {"messages": [HumanMessage(content="Hi")], "step": 0},
            config,
        )
        assert result["step"] == 1

        saved = app.get_state(config)
        assert saved.values["step"] == 1
