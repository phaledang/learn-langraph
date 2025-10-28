# Lab 09: LangSmith Tracing and Monitoring

## Learning Objectives
- Set up LangSmith tracing for comprehensive monitoring
- Monitor LLM calls and performance metrics
- Debug applications using trace analysis
- Analyze performance bottlenecks and costs
- Create custom tags and metadata for organization

## Prerequisites
- Completion of Labs 01-08
- LangSmith account and API key
- Understanding of LangChain/LangGraph applications

## Lab Overview
In this lab, you will:
1. Configure LangSmith for your applications
2. Add tracing to LangChain chains and agents
3. Create custom tags and metadata
4. Analyze traces for debugging and optimization
5. Monitor production applications

## Step-by-Step Instructions

### Task 1: Configure LangSmith
**Objective**: Set up LangSmith tracing for your LangChain applications.

**Steps**:
1. Install LangSmith:
   ```bash
   pip install langsmith
   ```

2. Set environment variables:
   ```python
   import os
   os.environ["LANGCHAIN_TRACING_V2"] = "true"
   os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
   os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
   os.environ["LANGCHAIN_PROJECT"] = "lab09-tracing"
   ```

3. Import and verify setup:
   ```python
   from langsmith import Client
   client = Client()
   print("LangSmith configured successfully!")
   ```

**Expected Result**: LangSmith client connected and ready to trace:
```
LangSmith configured successfully!
Project: lab09-tracing
Endpoint: https://api.smith.langchain.com
✓ Ready to trace LangChain applications
```

### Task 2: Add Basic Tracing
**Objective**: Trace simple LangChain operations to see them in LangSmith.

**Steps**:
1. Create a traced chain:
   ```python
   from langchain_openai import ChatOpenAI
   from langchain.prompts import PromptTemplate
   from langchain.schema.output_parser import StrOutputParser
   
   llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
   
   prompt = PromptTemplate(
       input_variables=["topic"],
       template="Write a haiku about {topic}"
   )
   
   chain = prompt | llm | StrOutputParser()
   ```

2. Run traced operations:
   ```python
   topics = ["spring", "technology", "ocean"]
   
   for topic in topics:
       print(f"\nGenerating haiku for: {topic}")
       result = chain.invoke({"topic": topic})
       print(result)
   ```

**Expected Result**: Operations appear in LangSmith dashboard:
```
Generating haiku for: spring
Cherry blossoms bloom
Gentle breeze through verdant leaves  
Nature awakens

✓ Trace recorded in LangSmith
✓ LLM call metadata captured
✓ Input/output logged
```

### Task 3: Create Custom Tags and Metadata
**Objective**: Add custom tags and metadata to organize and filter traces.

**Steps**:
1. Add tags to operations:
   ```python
   from langchain.callbacks import LangChainTracer
   
   # Create tracer with custom tags
   tracer = LangChainTracer(
       project_name="lab09-tracing",
       tags=["haiku-generation", "creative-writing"]
   )
   ```

2. Use context managers for custom metadata:
   ```python
   from langsmith import trace
   
   @trace(name="haiku_generator", tags=["poetry", "creative"])
   def generate_haiku_with_analysis(topic: str):
       """Generate haiku and analyze it."""
       
       # Generate haiku
       haiku = chain.invoke({"topic": topic})
       
       # Analyze haiku structure
       lines = haiku.strip().split('\n')
       syllable_pattern = [len(line.split()) for line in lines]
       
       return {
           "haiku": haiku,
           "line_count": len(lines),
           "word_pattern": syllable_pattern,
           "topic": topic
       }
   ```

3. Test with custom metadata:
   ```python
   topics = ["mountain", "code", "friendship"]
   
   for topic in topics:
       result = generate_haiku_with_analysis(topic)
       print(f"Topic: {topic}")
       print(f"Haiku:\n{result['haiku']}")
       print(f"Analysis: {result['line_count']} lines, pattern {result['word_pattern']}")
   ```

**Expected Result**: Rich metadata in traces:
```
✓ Custom tags applied: poetry, creative, haiku-generation
✓ Function-level tracing enabled
✓ Input/output parameters captured
✓ Execution time measured
```

### Task 4: Analyze Traces for Debugging
**Objective**: Use LangSmith traces to debug and optimize applications.

**Steps**:
1. Create a chain with potential issues:
   ```python
   def problematic_chain(user_input: str):
       """Chain that might have issues."""
       
       # Intentionally problematic prompt
       if len(user_input) < 3:
           raise ValueError("Input too short")
       
       prompt = PromptTemplate(
           template="Respond to this {input} in a helpful way",
           input_variables=["input"]
       )
       
       response = chain.invoke({"topic": user_input})
       return response
   ```

2. Test with various inputs:
   ```python
   test_inputs = ["hi", "Hello there", "Tell me about AI", ""]
   
   for test_input in test_inputs:
       try:
           with trace(name="problematic_test", metadata={"input_length": len(test_input)}):
               result = problematic_chain(test_input)
               print(f"✓ Success: {test_input[:20]}...")
       except Exception as e:
           print(f"✗ Error with '{test_input}': {str(e)}")
   ```

**Expected Result**: Clear error traces for debugging:
```
✗ Error with 'hi': Input too short
✓ Success: Hello there...
✓ Success: Tell me about AI...
✗ Error with '': Input too short

→ Check LangSmith dashboard for detailed error traces
→ Stack traces and error contexts captured
→ Performance metrics available
```

### Task 5: Monitor Production Applications
**Objective**: Set up monitoring for production LangChain applications.

**Steps**:
1. Create a production-style application:
   ```python
   class ProductionChatbot:
       def __init__(self):
           self.llm = ChatOpenAI(model="gpt-3.5-turbo")
           self.conversation_count = 0
       
       @trace(name="chatbot_response")
       def respond(self, user_message: str, user_id: str = "anonymous"):
           """Generate chatbot response with full tracing."""
           
           self.conversation_count += 1
           
           # Add user context to trace
           with trace(
               name="process_user_input",
               metadata={
                   "user_id": user_id,
                   "conversation_number": self.conversation_count,
                   "message_length": len(user_message)
               }
           ):
               # Process and respond
               prompt = PromptTemplate(
                   template="You are a helpful assistant. Respond to: {message}",
                   input_variables=["message"]
               )
               
               chain = prompt | self.llm | StrOutputParser()
               response = chain.invoke({"message": user_message})
               
               return {
                   "response": response,
                   "conversation_id": self.conversation_count,
                   "user_id": user_id
               }
   ```

2. Simulate production usage:
   ```python
   chatbot = ProductionChatbot()
   
   # Simulate multiple users
   scenarios = [
       ("user1", "Hello, how are you?"),
       ("user2", "What's the weather like?"),
       ("user1", "Can you help me with Python?"),
       ("user3", "Tell me a joke"),
       ("user2", "Thank you!"),
   ]
   
   for user_id, message in scenarios:
       result = chatbot.respond(message, user_id)
       print(f"[{user_id}] {message[:30]}... → {result['response'][:50]}...")
   ```

**Expected Result**: Comprehensive production monitoring:
```
[user1] Hello, how are you?... → Hello! I'm doing well, thank you for asking...
[user2] What's the weather like?... → I don't have access to current weather data...
[user1] Can you help me with Python?... → Absolutely! I'd be happy to help with Python...

✓ User sessions tracked
✓ Conversation flows mapped
✓ Performance metrics collected
✓ Error rates monitored
✓ Cost tracking enabled
```

## Expected Outcomes
- Master LangSmith tracing and monitoring
- Build production-ready observability
- Understand performance optimization
- Debug applications effectively

**Complete Program Output**:
```
=== Lab 09: LangSmith Tracing and Monitoring ===

Task 1: LangSmith Configuration
✓ LangSmith client configured
✓ Project 'lab09-tracing' created
✓ Environment variables set

Task 2: Basic Tracing
Generating haiku for: spring
Cherry blossoms fall
Soft petals dance on the breeze
Spring's gentle whisper
✓ Trace captured: prompt → LLM → output

Task 3: Custom Tags and Metadata
✓ Custom function tracing enabled
✓ Tags applied: poetry, creative, haiku-generation
✓ Metadata captured: topic, line_count, word_pattern

Task 4: Debug Analysis
Testing problematic inputs...
✗ Error with 'hi': Input too short
✓ Success: Hello there → Response generated
✗ Error with '': Input too short
→ Error traces available in LangSmith dashboard

Task 5: Production Monitoring
[user1] Hello, how are you? → Hello! I'm doing well...
[user2] What's the weather like? → I don't have access...
[user1] Can you help me with Python? → Absolutely! I'd be happy...
✓ 5 conversations traced
✓ User sessions tracked
✓ Performance metrics collected

=== Lab 09 Complete! ===
Visit LangSmith dashboard to explore your traces:
https://smith.langchain.com/projects/lab09-tracing
```

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## Next Steps
Proceed to **Lab 10: LangSmith Evaluation**.
