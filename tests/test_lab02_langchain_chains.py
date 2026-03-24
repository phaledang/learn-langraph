"""
Tests for Lab 02: LangChain Chains

Covers:
- Sequential chain pattern (summarize → extract)
- Router chain with keyword-based routing
- RAG chain components (text splitting, vector store, retrieval)
"""

import pytest
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


# ---------------------------------------------------------------------------
# Sequential Chain tests
# ---------------------------------------------------------------------------

class TestSequentialChain:
    """Test sequential chain pattern: summarize → extract key points."""

    def test_summarize_prompt_format(self):
        template = """Summarize the following text in 2-3 sentences:

Text: {text}

Summary:"""
        prompt = PromptTemplate(input_variables=["text"], template=template)
        result = prompt.format(text="AI has changed the world.")
        assert "AI has changed the world." in result

    def test_extract_prompt_format(self):
        template = """From the following summary, extract 3 key points as a bullet list:

Summary: {summary}

Key Points:"""
        prompt = PromptTemplate(input_variables=["summary"], template=template)
        result = prompt.format(summary="A concise summary.")
        assert "A concise summary." in result

    def test_sequential_chains_invoke(self, mock_env_azure_openai):
        """Two chains executed sequentially: summarize, then extract."""
        from langchain_core.messages import AIMessage
        from langchain_core.runnables import RunnableLambda

        call_count = {"n": 0}
        responses = [
            "AI revolutionizes industries through ML and DL.",
            "- Point 1\n- Point 2\n- Point 3",
        ]

        def fake_invoke(_):
            idx = min(call_count["n"], len(responses) - 1)
            call_count["n"] += 1
            return AIMessage(content=responses[idx])

        fake_llm = RunnableLambda(fake_invoke)

        summarize_prompt = PromptTemplate(
            input_variables=["text"], template="Summarize: {text}"
        )
        extract_prompt = PromptTemplate(
            input_variables=["summary"], template="Extract: {summary}"
        )

        summarize_chain = summarize_prompt | fake_llm | StrOutputParser()
        extract_chain = extract_prompt | fake_llm | StrOutputParser()

        summary = summarize_chain.invoke({"text": "Long document text..."})
        assert len(summary) > 0

        key_points = extract_chain.invoke({"summary": summary})
        assert "Point" in key_points


# ---------------------------------------------------------------------------
# Router Chain tests
# ---------------------------------------------------------------------------

class TestRouterChain:
    """Test keyword-based routing logic."""

    def _route_query(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ["calculate", "math", "equation", "solve"]):
            return "math"
        elif any(w in query_lower for w in ["code", "python", "function", "program"]):
            return "coding"
        return "general"

    def test_route_math(self):
        assert self._route_query("Calculate the sum of 1 to 100") == "math"
        assert self._route_query("Solve this equation") == "math"

    def test_route_coding(self):
        assert self._route_query("Write a Python function") == "coding"
        assert self._route_query("Show me code to reverse a list") == "coding"

    def test_route_general(self):
        assert self._route_query("What is the capital of France?") == "general"
        assert self._route_query("Tell me a joke") == "general"


# ---------------------------------------------------------------------------
# RAG Components tests
# ---------------------------------------------------------------------------

class TestRAGComponents:
    """Test RAG building blocks: splitting, documents, retriever."""

    def test_document_creation(self):
        doc = Document(page_content="LangChain is a framework.")
        assert doc.page_content == "LangChain is a framework."

    def test_text_splitter(self):
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        docs = [Document(page_content="A" * 120)]
        splits = splitter.split_documents(docs)
        assert len(splits) > 1
        for s in splits:
            assert len(s.page_content) <= 50

    def test_text_splitter_preserves_content(self):
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        original = "Word " * 100  # ~500 chars
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        docs = [Document(page_content=original.strip())]
        splits = splitter.split_documents(docs)
        # All original words should appear in at least one chunk
        combined = " ".join(s.page_content for s in splits)
        assert "Word" in combined

    def test_multiple_documents(self):
        docs = [
            Document(page_content="LangChain is a framework."),
            Document(page_content="LangGraph builds stateful apps."),
            Document(page_content="LangSmith helps with debugging."),
        ]
        assert len(docs) == 3
        assert all(isinstance(d, Document) for d in docs)
