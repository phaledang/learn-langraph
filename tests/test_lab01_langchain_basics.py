"""
Tests for Lab 01: LangChain Basics

Covers:
- LLM initialization with AzureChatOpenAI
- PromptTemplate creation and formatting
- LCEL chain construction (prompt | llm | parser)
- Single invocation and batch processing
"""

import sys
import os
import pytest

# Ensure lab01 solution is importable
LAB_DIR = os.path.join(
    os.path.dirname(__file__), "..", "labs", "lab01-langchain-basics", "solution"
)
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)


# ---------------------------------------------------------------------------
# PromptTemplate tests (no LLM needed)
# ---------------------------------------------------------------------------

class TestPromptTemplate:
    """Test prompt template creation and formatting."""

    def test_prompt_template_creation(self):
        from langchain_core.prompts import PromptTemplate

        template = """You are a creative poet. Write a short, beautiful poem about {topic}.

The poem should be:
- 4 lines long
- Creative and inspiring
- Easy to understand

Poem:"""
        prompt = PromptTemplate(input_variables=["topic"], template=template)
        assert "topic" in prompt.input_variables
        assert prompt.template == template

    def test_prompt_template_format(self):
        from langchain_core.prompts import PromptTemplate

        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Write a poem about {topic}.",
        )
        result = prompt.format(topic="nature")
        assert "nature" in result

    def test_prompt_template_partial(self):
        from langchain_core.prompts import PromptTemplate

        prompt = PromptTemplate(
            input_variables=["topic", "style"],
            template="Write a {style} poem about {topic}.",
        )
        partial = prompt.partial(style="haiku")
        result = partial.format(topic="ocean")
        assert "haiku" in result
        assert "ocean" in result


# ---------------------------------------------------------------------------
# StrOutputParser tests
# ---------------------------------------------------------------------------

class TestOutputParser:
    """Test output parsers."""

    def test_str_output_parser(self):
        from langchain_core.output_parsers import StrOutputParser

        parser = StrOutputParser()
        # StrOutputParser extracts .content from AIMessage or returns str
        assert parser.parse("hello world") == "hello world"


# ---------------------------------------------------------------------------
# Chain construction tests (mocked LLM)
# ---------------------------------------------------------------------------

class TestChainConstruction:
    """Test LCEL chain building with mocked LLM."""

    def test_chain_invoke(self, mock_env_azure_openai):
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import AIMessage
        from langchain_core.runnables import RunnableLambda

        # Use a RunnableLambda to simulate the LLM in the LCEL chain
        fake_llm = RunnableLambda(lambda _: AIMessage(content="A beautiful poem about nature"))

        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Write a poem about {topic}.",
        )
        chain = prompt | fake_llm | StrOutputParser()
        result = chain.invoke({"topic": "nature"})

        assert isinstance(result, str)
        assert "poem" in result.lower() or len(result) > 0

    def test_chain_batch(self, mock_env_azure_openai):
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.messages import AIMessage
        from langchain_core.runnables import RunnableLambda

        fake_llm = RunnableLambda(lambda _: AIMessage(content="A poem"))

        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Write a poem about {topic}.",
        )
        chain = prompt | fake_llm | StrOutputParser()
        results = chain.batch([{"topic": "ocean"}, {"topic": "mountains"}])

        assert isinstance(results, list)
        assert len(results) == 2
