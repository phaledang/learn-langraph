# Lab 02: LangChain Chains and Prompts

## Learning Objectives
- Master sequential and parallel chains
- Create complex prompt templates
- Use chain routing and conditional logic
- Implement retrieval augmented generation (RAG)
- Work with different chain types

## Prerequisites
- Completion of Lab 01
- Understanding of basic LangChain concepts

## Lab Overview
In this lab, you will:
1. Build sequential chains
2. Create router chains
3. Implement RAG with document retrieval
4. Use different chain patterns
5. Build a complete Q&A system

## Step-by-Step Instructions

### Task 1: Sequential Chains
**Objective**: Create a chain that processes data through multiple steps.

**Steps**:
1. Import required modules:
   ```python
   from langchain.chains import SequentialChain, LLMChain
   from langchain.prompts import PromptTemplate
   from langchain_openai import ChatOpenAI
   ```

2. Create the first chain for content generation:
   ```python
   synopsis_template = """Write a synopsis for a {genre} story about {topic}."""
   synopsis_prompt = PromptTemplate(input_variables=["genre", "topic"], template=synopsis_template)
   synopsis_chain = LLMChain(llm=llm, prompt=synopsis_prompt, output_key="synopsis")
   ```

3. Create the second chain for review:
   ```python
   review_template = """Review this synopsis: {synopsis}. Provide constructive feedback."""
   review_prompt = PromptTemplate(input_variables=["synopsis"], template=review_template)
   review_chain = LLMChain(llm=llm, prompt=review_prompt, output_key="review")
   ```

4. Combine into sequential chain:
   ```python
   overall_chain = SequentialChain(
       chains=[synopsis_chain, review_chain],
       input_variables=["genre", "topic"],
       output_variables=["synopsis", "review"]
   )
   ```

**Expected Result**: A chain that first generates a synopsis, then reviews it:
```
Synopsis: A thrilling sci-fi tale about space exploration...
Review: This synopsis effectively captures the essence of science fiction...
```

### Task 2: Router Chains
**Objective**: Build a chain that routes to different sub-chains based on input.

**Steps**:
1. Import router components:
   ```python
   from langchain.chains.router import MultiPromptChain
   from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
   ```

2. Define destination chains:
   ```python
   science_template = """You are a science expert. Answer this question: {input}"""
   history_template = """You are a history expert. Answer this question: {input}"""
   ```

3. Create router template:
   ```python
   router_template = """Given a question, determine if it's about science or history.
   Question: {input}
   Return either "science" or "history"."""
   ```

4. Build the router chain:
   ```python
   router_chain = MultiPromptChain(
       router_chain=router_llm_chain,
       destination_chains=destination_chains,
       default_chain=default_chain
   )
   ```

**Expected Result**: Questions automatically routed to appropriate expert chains:
```
Question: "What is photosynthesis?" → Routes to science chain
Question: "When did WWII end?" → Routes to history chain
```

### Task 3: RAG Implementation
**Objective**: Implement a simple retrieval-augmented generation system.

**Steps**:
1. Install and import vector store components:
   ```python
   from langchain.vectorstores import FAISS
   from langchain.embeddings import OpenAIEmbeddings
   from langchain.text_splitter import CharacterTextSplitter
   ```

2. Prepare documents:
   ```python
   documents = ["Document 1 content...", "Document 2 content..."]
   text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
   texts = text_splitter.split_text("\n".join(documents))
   ```

3. Create vector store:
   ```python
   embeddings = OpenAIEmbeddings()
   vectorstore = FAISS.from_texts(texts, embeddings)
   retriever = vectorstore.as_retriever()
   ```

4. Build RAG chain:
   ```python
   from langchain.chains import RetrievalQA
   qa_chain = RetrievalQA.from_chain_type(
       llm=llm,
       chain_type="stuff",
       retriever=retriever
   )
   ```

**Expected Result**: A system that retrieves relevant documents and generates answers:
```
Question: "What is mentioned about AI?"
Retrieved: "Documents mentioning artificial intelligence..."
Answer: "Based on the retrieved documents, AI is described as..."
```

### Task 4: Conversation Chains
**Objective**: Create a chain that maintains context across multiple exchanges.

**Steps**:
1. Import conversation components:
   ```python
   from langchain.chains import ConversationChain
   from langchain.memory import ConversationBufferMemory
   ```

2. Set up memory:
   ```python
   memory = ConversationBufferMemory()
   conversation = ConversationChain(
       llm=llm,
       memory=memory,
       verbose=True
   )
   ```

3. Test conversation flow:
   ```python
   response1 = conversation.predict(input="Hi, my name is John")
   response2 = conversation.predict(input="What's my name?")
   ```

**Expected Result**: The chain remembers previous conversation:
```
User: "Hi, my name is John"
AI: "Hello John! Nice to meet you."
User: "What's my name?"
AI: "Your name is John, as you mentioned earlier."
```

### Task 5: Complete Application
**Objective**: Build a document Q&A system using all learned concepts.

**Steps**:
1. Combine all components:
   ```python
   # Document processing + RAG + Conversation memory
   complete_system = create_qa_system_with_memory()
   ```

2. Test with multiple questions:
   ```python
   questions = [
       "What are the main topics in the documents?",
       "Can you elaborate on the first topic?",
       "How does this relate to what we discussed earlier?"
   ]
   ```

**Expected Result**: A complete Q&A system that:
- Retrieves relevant documents
- Maintains conversation context
- Provides coherent, contextual answers

## Expected Outcomes
- Understand advanced chain patterns
- Implement complex workflows
- Work with document retrieval
- Build production-ready applications

**Complete Program Output**:
When you run the complete lab, you should see output demonstrating each concept:

```
=== Lab 02: LangChain Chains ===

Task 1: Sequential Chains
→ Generating synopsis...
→ Reviewing synopsis...
Synopsis: A thrilling space exploration story where humanity discovers...
Review: This synopsis effectively captures the essence of science fiction...

Task 2: Router Chains
Question: "What is photosynthesis?"
→ Routing to: science
Expert Answer: Photosynthesis is the process by which plants convert...

Question: "When did World War II end?"
→ Routing to: history  
Expert Answer: World War II ended on September 2, 1945...

Task 3: RAG Implementation
→ Creating vector store from documents...
→ Building retrieval chain...
Question: "What technologies are mentioned?"
Retrieved Documents: [Document chunks about AI, machine learning...]
Answer: Based on the retrieved documents, several key technologies are mentioned...

Task 4: Conversation Chains
User: Hi, my name is Alice
AI: Hello Alice! Nice to meet you. How can I help you today?

User: What's my name?
AI: Your name is Alice, as you mentioned when we started our conversation.

Task 5: Complete Q&A System
→ Initializing document Q&A system with memory...
User: What are the main topics covered?
AI: Based on the documents, the main topics include...

User: Tell me more about the first topic
AI: Regarding the first topic we discussed...

=== Lab 02 Complete! ===
```

## Resources
- [LangChain Chains](https://python.langchain.com/docs/modules/chains/)
- [RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

## Next Steps
Proceed to **Lab 03: LangChain Agents** to learn about autonomous agents.
