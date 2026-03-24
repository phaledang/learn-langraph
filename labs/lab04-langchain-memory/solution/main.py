"""
LangChain Memory Systems - Solution Code

Complete implementation demonstrating langchain memory systems.
Implements all 5 tasks from the README:
  1. Implement Buffer Memory
  2. Create Summary Memory
  3. Build Entity Memory
  4. Handle Memory Limits
  5. Create Persistent Memory
"""

import os
import json
import pickle
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Load environment variables from .env file relative to this script
load_dotenv(Path(__file__).parent / ".env")


# ---------------------------------------------------------------------------
# Helper: create an Azure OpenAI LLM instance
# ---------------------------------------------------------------------------

def _create_llm(temperature: float = 0.7) -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# Memory helpers (message-list based approach — works with latest LangChain)
# ---------------------------------------------------------------------------

class ConversationBufferMemory:
    """Simple buffer memory that stores all messages."""

    def __init__(self):
        self.messages: list = []

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

    def get_messages(self) -> list:
        return list(self.messages)

    def clear(self):
        self.messages.clear()

    @property
    def buffer(self):
        return self.messages


class ConversationBufferWindowMemory:
    """Sliding-window memory that keeps only the last *k* exchanges."""

    def __init__(self, k: int = 5):
        self.k = k
        self.messages: list = []

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

    def get_messages(self) -> list:
        # Each exchange = 2 messages (human + ai), keep last k exchanges
        return self.messages[-(self.k * 2):]

    def clear(self):
        self.messages.clear()


class ConversationSummaryMemory:
    """Memory that periodically summarizes older messages to save tokens."""

    def __init__(self, llm, max_messages: int = 6):
        self.llm = llm
        self.max_messages = max_messages
        self.messages: list = []
        self.summary: str = ""

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))
        # Auto-summarize when messages exceed the limit
        if len(self.messages) > self.max_messages:
            self._summarize()

    def _summarize(self):
        """Summarize older messages and keep only recent ones."""
        older = self.messages[:-4]  # summarize all but last 4
        recent = self.messages[-4:]  # keep last 4 messages

        conversation_text = "\n".join(
            f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in older
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize the following conversation concisely, "
                       "preserving key facts and context:\n\n{conversation}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        new_summary = chain.invoke({"conversation": conversation_text})

        if self.summary:
            self.summary = f"{self.summary}\n{new_summary}"
        else:
            self.summary = new_summary

        self.messages = recent
        print(f"  [Summary updated]: {self.summary[:120]}...")

    def get_messages(self) -> list:
        result = []
        if self.summary:
            result.append(AIMessage(content=f"[Previous conversation summary]: {self.summary}"))
        result.extend(self.messages)
        return result

    def clear(self):
        self.messages.clear()
        self.summary = ""


class ConversationEntityMemory:
    """Memory that tracks entities (people, places, facts) mentioned in conversation."""

    def __init__(self, llm):
        self.llm = llm
        self.messages: list = []
        self.entities: dict = {}  # entity_name -> description

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))

    def extract_entities(self, text: str):
        """Use the LLM to extract entities from text."""
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Extract named entities (people, places, organizations, key facts) "
             "from the following text. Return as JSON with entity names as keys "
             "and brief descriptions as values. Return only valid JSON, no markdown.\n\n"
             "Text: {text}"),
        ])
        chain = prompt | self.llm | StrOutputParser()
        raw = chain.invoke({"text": text})
        try:
            new_entities = json.loads(raw)
            self.entities.update(new_entities)
            print(f"  [Entities extracted]: {list(new_entities.keys())}")
        except json.JSONDecodeError:
            print(f"  [Entity extraction]: could not parse response")

    def get_entity_context(self) -> str:
        if not self.entities:
            return ""
        lines = [f"- {name}: {desc}" for name, desc in self.entities.items()]
        return "Known entities:\n" + "\n".join(lines)

    def get_messages(self) -> list:
        result = []
        ctx = self.get_entity_context()
        if ctx:
            result.append(AIMessage(content=f"[Entity memory]: {ctx}"))
        result.extend(self.messages)
        return result

    def clear(self):
        self.messages.clear()
        self.entities.clear()


class ConversationSummaryBufferMemory:
    """Combines buffer + summary: keeps recent messages and summarizes old ones
    when total estimated tokens exceed *max_token_limit*."""

    def __init__(self, llm, max_token_limit: int = 300):
        self.llm = llm
        self.max_token_limit = max_token_limit
        self.messages: list = []
        self.summary: str = ""

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(text) // 4  # rough estimate: 1 token ≈ 4 chars

    def _total_tokens(self) -> int:
        total = self._estimate_tokens(self.summary)
        for m in self.messages:
            total += self._estimate_tokens(m.content)
        return total

    def add_user_message(self, content: str):
        self.messages.append(HumanMessage(content=content))

    def add_ai_message(self, content: str):
        self.messages.append(AIMessage(content=content))
        if self._total_tokens() > self.max_token_limit:
            self._prune()

    def _prune(self):
        """Move older messages into the running summary."""
        while self._total_tokens() > self.max_token_limit and len(self.messages) > 2:
            old_pair = self.messages[:2]
            self.messages = self.messages[2:]

            text = "\n".join(
                f"{'Human' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
                for m in old_pair
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "Progressively summarize the conversation, incorporating new lines "
                 "into the existing summary.\n\n"
                 "Current summary: {summary}\n\n"
                 "New lines:\n{new_lines}\n\n"
                 "Updated summary:"),
            ])
            chain = prompt | self.llm | StrOutputParser()
            self.summary = chain.invoke({"summary": self.summary, "new_lines": text})
            print(f"  [Token limit pruning]: ~{self._total_tokens()} tokens remaining")

    def get_messages(self) -> list:
        result = []
        if self.summary:
            result.append(AIMessage(content=f"[Conversation summary]: {self.summary}"))
        result.extend(self.messages)
        return result

    def clear(self):
        self.messages.clear()
        self.summary = ""


# ---------------------------------------------------------------------------
# Conversation runner helper
# ---------------------------------------------------------------------------

def chat(llm, memory, user_input: str, system_prompt: str = "You are a helpful assistant.") -> str:
    """Send a message through the LLM, updating memory before and after."""
    memory.add_user_message(user_input)

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "history": memory.get_messages()[:-1],  # exclude the just-added human msg
        "input": user_input,
    })

    memory.add_ai_message(response)
    return response


# ---------------------------------------------------------------------------
# Task 1: Implement Buffer Memory
# ---------------------------------------------------------------------------

def task1_buffer_memory():
    """Demonstrate buffer memory for short-term context retention."""
    print("\n=== Task 1: Buffer Memory ===")

    llm = _create_llm()

    # --- Basic buffer memory ---
    print("\n--- Basic Buffer Memory ---")
    basic_memory = ConversationBufferMemory()

    response1 = chat(llm, basic_memory, "Hi, I'm learning about AI")
    print(f"Human: Hi, I'm learning about AI")
    print(f"AI: {response1}")

    response2 = chat(llm, basic_memory, "What did I just say I was learning about?")
    print(f"\nHuman: What did I just say I was learning about?")
    print(f"AI: {response2}")

    print(f"\nMessages in memory: {len(basic_memory.get_messages())}")

    # --- Window buffer memory ---
    print("\n--- Window Buffer Memory (k=2) ---")
    window_memory = ConversationBufferWindowMemory(k=2)

    conversations = [
        "My name is Alice.",
        "I work at OpenAI.",
        "I love hiking on weekends.",
        "What do you remember about me?",
    ]
    for msg in conversations:
        response = chat(llm, window_memory, msg)
        print(f"Human: {msg}")
        print(f"AI: {response}\n")

    print(f"Total messages stored: {len(window_memory.messages)}")
    print(f"Window returns: {len(window_memory.get_messages())} messages")
    print("✓ Buffer memory demonstrated")


# ---------------------------------------------------------------------------
# Task 2: Create Summary Memory
# ---------------------------------------------------------------------------

def task2_summary_memory():
    """Demonstrate summary memory for long conversations."""
    print("\n\n=== Task 2: Summary Memory ===")

    llm = _create_llm()
    summary_memory = ConversationSummaryMemory(llm=llm, max_messages=6)

    topics = [
        "Tell me about machine learning.",
        "How does deep learning differ from traditional ML?",
        "What are neural networks?",
        "Explain backpropagation briefly.",
        "What are transformers in AI?",
        "How does attention mechanism work?",
    ]

    for msg in topics:
        print(f"\nHuman: {msg}")
        response = chat(llm, summary_memory, msg)
        print(f"AI: {response[:150]}...")

    print(f"\nCurrent summary: {summary_memory.summary[:200] if summary_memory.summary else '(none yet)'}")
    print(f"Active messages: {len(summary_memory.messages)}")
    print("✓ Summary memory demonstrated")


# ---------------------------------------------------------------------------
# Task 3: Build Entity Memory
# ---------------------------------------------------------------------------

def task3_entity_memory():
    """Demonstrate entity memory for tracking people/places/facts."""
    print("\n\n=== Task 3: Entity Memory ===")

    llm = _create_llm()
    entity_memory = ConversationEntityMemory(llm=llm)

    statements = [
        "My name is Bob and I work at Microsoft in Seattle.",
        "My colleague Sarah is a data scientist who specializes in NLP.",
        "We are working on Project Atlas, which is an AI-powered search engine.",
    ]

    for msg in statements:
        print(f"\nHuman: {msg}")
        response = chat(llm, entity_memory, msg)
        print(f"AI: {response[:150]}...")
        # Extract entities from the user's statement
        entity_memory.extract_entities(msg)

    print(f"\n--- Tracked Entities ---")
    for name, desc in entity_memory.entities.items():
        print(f"  {name}: {desc}")

    # Ask a question that requires entity recall
    question = "What do you know about Sarah and Project Atlas?"
    print(f"\nHuman: {question}")
    response = chat(llm, entity_memory, question)
    print(f"AI: {response}")
    print("✓ Entity memory demonstrated")


# ---------------------------------------------------------------------------
# Task 4: Handle Memory Limits
# ---------------------------------------------------------------------------

def task4_memory_limits():
    """Demonstrate memory size management with token-limited memory."""
    print("\n\n=== Task 4: Memory Limits ===")

    llm = _create_llm()
    limited_memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)

    print("--- Token-Limited Summary Buffer Memory (limit=100 tokens) ---")

    messages = [
        "I'm studying computer science at MIT.",
        "My favorite programming language is Python.",
        "I'm interested in reinforcement learning.",
        "I also enjoy playing chess competitively.",
        "What topics have we discussed so far?",
    ]

    for msg in messages:
        print(f"\nHuman: {msg}")
        response = chat(llm, limited_memory, msg)
        print(f"AI: {response[:150]}...")
        print(f"  [estimated tokens: ~{limited_memory._total_tokens()}]")

    if limited_memory.summary:
        print(f"\nRunning summary: {limited_memory.summary[:200]}...")
    print(f"Active messages: {len(limited_memory.messages)}")
    print("✓ Memory limits demonstrated")


# ---------------------------------------------------------------------------
# Task 5: Create Persistent Memory
# ---------------------------------------------------------------------------

MEMORY_DIR = Path(__file__).parent / "memory_store"


def save_memory(memory, filename: str):
    """Save conversation memory to disk as JSON."""
    MEMORY_DIR.mkdir(exist_ok=True)
    filepath = MEMORY_DIR / filename

    data = {
        "messages": [
            {"type": m.type, "content": m.content}
            for m in memory.get_messages()
        ],
    }
    # Save summary if present
    if hasattr(memory, "summary"):
        data["summary"] = memory.summary
    # Save entities if present
    if hasattr(memory, "entities"):
        data["entities"] = memory.entities

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  [Memory saved to {filepath}]")


def load_memory(filename: str) -> dict:
    """Load conversation memory from disk."""
    filepath = MEMORY_DIR / filename
    if not filepath.exists():
        print(f"  [No saved memory found at {filepath}]")
        return {"messages": []}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"  [Memory loaded from {filepath}]")
    return data


def restore_buffer_memory(data: dict) -> ConversationBufferMemory:
    """Reconstruct a ConversationBufferMemory from saved data."""
    memory = ConversationBufferMemory()
    for m in data.get("messages", []):
        if m["type"] == "human":
            memory.add_user_message(m["content"])
        else:
            memory.add_ai_message(m["content"])
    return memory


def task5_persistent_memory():
    """Demonstrate saving and restoring conversation memory across sessions."""
    print("\n\n=== Task 5: Persistent Memory ===")

    llm = _create_llm()

    # --- Session 1: have a conversation and save ---
    print("\n--- Session 1: Initial Conversation ---")
    memory = ConversationBufferMemory()

    response = chat(llm, memory, "Hi, my name is Charlie and I live in Tokyo.")
    print(f"Human: Hi, my name is Charlie and I live in Tokyo.")
    print(f"AI: {response}")

    response = chat(llm, memory, "I'm a software engineer working on AI projects.")
    print(f"Human: I'm a software engineer working on AI projects.")
    print(f"AI: {response}")

    save_memory(memory, "session_memory.json")

    # --- Session 2: restore and continue ---
    print("\n--- Session 2: Restored Conversation ---")
    saved_data = load_memory("session_memory.json")
    restored_memory = restore_buffer_memory(saved_data)

    print(f"Restored {len(restored_memory.get_messages())} messages from previous session")

    response = chat(llm, restored_memory, "What's my name and where do I live?")
    print(f"Human: What's my name and where do I live?")
    print(f"AI: {response}")

    # Also demonstrate pickle-based persistence
    print("\n--- Pickle-based Persistence ---")
    pickle_path = MEMORY_DIR / "session_memory.pkl"
    MEMORY_DIR.mkdir(exist_ok=True)

    with open(pickle_path, "wb") as f:
        pickle.dump(memory.buffer, f)
    print(f"  [Pickle saved to {pickle_path}]")

    with open(pickle_path, "rb") as f:
        restored_buffer = pickle.load(f)
    print(f"  [Pickle loaded: {len(restored_buffer)} messages]")

    # Clean up
    if MEMORY_DIR.exists():
        for fp in MEMORY_DIR.iterdir():
            fp.unlink()
        MEMORY_DIR.rmdir()
        print("  [Memory store cleaned up]")

    print("✓ Persistent memory demonstrated")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run all tasks."""
    print("=" * 80)
    print("Lab 04: LangChain Memory Systems — Solution")
    print("=" * 80)

    # Check API key
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: AZURE_OPENAI_API_KEY not set")
        return

    task1_buffer_memory()
    task2_summary_memory()
    task3_entity_memory()
    task4_memory_limits()
    task5_persistent_memory()

    print("\n" + "=" * 80)
    print("Lab 04 Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
