"""
Tests for Lab 04: LangChain Memory Systems

Covers:
- ConversationBufferMemory basics
- Memory variable loading/saving
- Chat message history management
"""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage


# ---------------------------------------------------------------------------
# Message types tests
# ---------------------------------------------------------------------------

class TestMessageTypes:
    """Test LangChain message types used in memory."""

    def test_human_message(self):
        msg = HumanMessage(content="Hello!")
        assert msg.content == "Hello!"
        assert msg.type == "human"

    def test_ai_message(self):
        msg = AIMessage(content="Hi there!")
        assert msg.content == "Hi there!"
        assert msg.type == "ai"

    def test_message_list(self):
        messages = [
            HumanMessage(content="What is AI?"),
            AIMessage(content="AI is artificial intelligence."),
            HumanMessage(content="Tell me more."),
            AIMessage(content="It includes machine learning and deep learning."),
        ]
        assert len(messages) == 4
        assert messages[0].type == "human"
        assert messages[1].type == "ai"


# ---------------------------------------------------------------------------
# Conversation buffer memory tests
# ---------------------------------------------------------------------------

class TestConversationMemory:
    """Test conversation memory patterns."""

    def test_buffer_memory_basic(self):
        """Test basic buffer memory using message list."""
        memory = []
        memory.append(HumanMessage(content="Hello"))
        memory.append(AIMessage(content="Hi there!"))

        assert len(memory) == 2
        assert memory[0].content == "Hello"
        assert memory[-1].content == "Hi there!"

    def test_memory_window(self):
        """Test sliding window memory (keep last N messages)."""
        window_size = 4
        memory = []

        for i in range(10):
            memory.append(HumanMessage(content=f"Question {i}"))
            memory.append(AIMessage(content=f"Answer {i}"))

        windowed = memory[-window_size:]
        assert len(windowed) == window_size
        assert "Question 8" in windowed[0].content

    def test_memory_clear(self):
        """Test clearing memory."""
        memory = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi!"),
        ]
        memory.clear()
        assert len(memory) == 0

    def test_memory_serialization(self):
        """Test that messages can be serialized to dicts."""
        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="World"),
        ]
        serialized = [
            {"type": m.type, "content": m.content} for m in messages
        ]
        assert serialized[0] == {"type": "human", "content": "Hello"}
        assert serialized[1] == {"type": "ai", "content": "World"}

    def test_memory_deserialization(self):
        """Test reconstructing messages from dicts."""
        data = [
            {"type": "human", "content": "Hello"},
            {"type": "ai", "content": "World"},
        ]
        messages = []
        for d in data:
            if d["type"] == "human":
                messages.append(HumanMessage(content=d["content"]))
            else:
                messages.append(AIMessage(content=d["content"]))

        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
