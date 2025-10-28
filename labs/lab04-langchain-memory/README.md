# Lab 04: LangChain Memory Systems

## Learning Objectives
- Implement conversation memory for context retention
- Use buffer and summary memory strategies
- Create entity memory for tracking information
- Handle long conversations with memory limits
- Build persistent memory systems

## Prerequisites
- Completion of Labs 01-03
- Understanding of LangChain chains and agents
- Basic knowledge of conversation flows

## Lab Overview
In this lab, you will:
1. Implement buffer memory for short-term context
2. Create summary memory for long conversations
3. Build entity memory for tracking people/places
4. Handle memory size limitations
5. Create persistent memory storage

## Step-by-Step Instructions

### Task 1: Implement Buffer Memory
**Objective**: Store recent conversation history in memory buffers.

**Steps**:
1. Import memory components:
   ```python
   from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
   from langchain.chains import ConversationChain
   from langchain_openai import ChatOpenAI
   ```

2. Create basic buffer memory:
   ```python
   basic_memory = ConversationBufferMemory()
   llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
   conversation = ConversationChain(llm=llm, memory=basic_memory, verbose=True)
   ```

3. Test conversation flow:
   ```python
   conversation.predict(input="Hi, I'm learning about AI")
   conversation.predict(input="What did I just say I was learning about?")
   ```

**Expected Result**: AI remembers previous context in conversation.

### Task 2: Create Summary Memory
**Objective**: Summarize old conversations to save space while retaining key information.

**Steps**:
1. Import summary memory:
   ```python
   from langchain.memory import ConversationSummaryMemory
   ```

2. Create summary-based conversation:
   ```python
   summary_memory = ConversationSummaryMemory(llm=llm)
   summary_conversation = ConversationChain(llm=llm, memory=summary_memory, verbose=True)
   ```

**Expected Result**: Long conversations get summarized automatically.

### Task 3: Build Entity Memory
**Objective**: Track specific entities (people, places, facts) mentioned in conversation.

**Steps**:
1. Import entity memory:
   ```python
   from langchain.memory import ConversationEntityMemory
   ```

2. Create entity tracking:
   ```python
   entity_memory = ConversationEntityMemory(llm=llm)
   entity_conversation = ConversationChain(llm=llm, memory=entity_memory, verbose=True)
   ```

**Expected Result**: System tracks and remembers specific entities.

### Task 4: Handle Memory Limits
**Objective**: Manage memory size and implement rotation strategies.

**Steps**:
1. Create token-limited memory:
   ```python
   from langchain.memory import ConversationSummaryBufferMemory
   limited_memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)
   ```

**Expected Result**: Memory automatically manages size limits.

### Task 5: Create Persistent Memory
**Objective**: Save and restore conversation memory across sessions.

**Steps**:
1. Implement memory persistence:
   ```python
   def save_memory(memory, filename):
       import pickle
       with open(filename, 'wb') as f:
           pickle.dump(memory.buffer, f)
   
   def load_memory(filename):
       import pickle
       with open(filename, 'rb') as f:
           return pickle.load(f)
   ```

**Expected Result**: Conversations persist across application restarts.

## Expected Outcomes
- Master LangChain memory systems
- Build production-ready applications with context
- Understand memory management best practices

**Complete Program Output**:
```
=== Lab 04: LangChain Memory Systems ===

Task 1: Buffer Memory
Human: Hi, I'm learning about AI
AI: That's great! AI is a fascinating field...

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## Next Steps
Proceed to **Lab 05: LangGraph Basics**.
