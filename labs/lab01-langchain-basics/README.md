# Lab 01: LangChain Basics

## Learning Objectives
- Understand the fundamentals of LangChain
- Learn how to work with LLM models
- Create and use prompt templates
- Build simple chains
- Parse LLM outputs

## Prerequisites
- Python 3.9+
- OpenAI API key
- Basic Python knowledge

## Lab Overview
In this lab, you will:
1. Initialize an LLM model
2. Create prompt templates
3. Build a basic chain
4. Use output parsers
5. Combine components into a working application

## Setup
1. Ensure you have installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set your `OPENAI_API_KEY`

## Step-by-Step Instructions

### Task 1: Initialize LLM Model
**Objective**: Create a ChatOpenAI instance and test it with a simple prompt.

**Steps**:
1. Import the necessary modules:
   ```python
   from langchain_openai import ChatOpenAI
   import os
   from dotenv import load_dotenv
   ```

2. Load environment variables:
   ```python
   load_dotenv()
   ```

3. Initialize the LLM:
   ```python
   llm = ChatOpenAI(
       model="gpt-3.5-turbo",
       temperature=0.7,
       api_key=os.getenv("OPENAI_API_KEY")
   )
   ```

**Expected Result**: A working ChatOpenAI instance that can generate responses. You should see output like:
```
Task 1: Initializing LLM Model...
✓ LLM initialized
```

### Task 2: Create Prompt Templates
**Objective**: Build a prompt template that accepts user input variables.

**Steps**:
1. Import PromptTemplate:
   ```python
   from langchain.prompts import PromptTemplate
   ```

2. Create a template with input variables:
   ```python
   template = """You are a creative poet. Write a short, beautiful poem about {topic}.
   
   The poem should be:
   - 4 lines long
   - Creative and inspiring
   - Easy to understand

   Poem:"""
   
   prompt = PromptTemplate(
       input_variables=["topic"],
       template=template
   )
   ```

**Expected Result**: A reusable prompt template that can accept different topics. You should see:
```
Task 2: Creating Prompt Template...
✓ Prompt template created
```

### Task 3: Build a Chain
**Objective**: Combine the LLM and prompt template into a chain using LCEL (LangChain Expression Language).

**Steps**:
1. Import the output parser:
   ```python
   from langchain.schema.output_parser import StrOutputParser
   ```

2. Create the chain using the pipe operator:
   ```python
   chain = prompt | llm | StrOutputParser()
   ```

**Expected Result**: A functional chain that processes input through prompt → LLM → parser. Output:
```
Task 3: Building Chain...
✓ Chain built
```

### Task 4: Test the Chain
**Objective**: Use the chain to generate poems for different topics.

**Steps**:
1. Define test topics:
   ```python
   topics = ["artificial intelligence", "nature", "friendship"]
   ```

2. Invoke the chain for each topic:
   ```python
   for topic in topics:
       result = chain.invoke({"topic": topic})
       print(f"Poem about '{topic}':")
       print(result)
   ```

**Expected Result**: Three different poems generated for each topic. Example output:
```
--- Poem about 'artificial intelligence' ---
In circuits bright and data streams so vast,
A mind awakens, learning unsurpassed.
Through algorithms deep, it seeks to find,
The bridge between the heart and thinking mind.
```

### Task 5: Demonstrate Batch Processing
**Objective**: Process multiple inputs simultaneously using batch operations.

**Steps**:
1. Prepare batch inputs:
   ```python
   batch_topics = [
       {"topic": "ocean"},
       {"topic": "mountains"}, 
       {"topic": "dreams"}
   ]
   ```

2. Use batch processing:
   ```python
   batch_results = chain.batch(batch_topics)
   ```

**Expected Result**: Multiple poems generated simultaneously, demonstrating efficient batch processing:
```
Task 5: Batch Processing Multiple Topics...

Poem 1 (ocean):
Beneath the waves where mysteries sleep,
The ocean holds its secrets deep...

Poem 2 (mountains):
Majestic peaks that touch the sky,
Where eagles soar and spirits fly...
```

## Expected Outcomes
By the end of this lab, you should be able to:
- Initialize and use LangChain LLM models
- Create reusable prompt templates
- Build basic chains using LCEL
- Parse LLM outputs
- Understand the LangChain component architecture

**Complete Program Output**:
When you run the complete solution, you should see output similar to:
```
=== Lab 01: LangChain Basics ===

Task 1: Initializing LLM Model...
✓ LLM initialized

Task 2: Creating Prompt Template...
✓ Prompt template created

Task 3: Building Chain...
✓ Chain built

Task 4: Testing Chain...

--- Poem about 'artificial intelligence' ---
In circuits bright and data streams so vast,
A mind awakens, learning unsurpassed.
Through algorithms deep, it seeks to find,
The bridge between the heart and thinking mind.
--------------------------------------------------

--- Poem about 'nature' ---
The forest whispers ancient tales,
Of seasons past and mountain trails.
Where flowers bloom and rivers flow,
Life's endless beauty starts to show.
--------------------------------------------------

--- Poem about 'friendship' ---
A bond that time cannot erase,
Two hearts that find their sacred space.
Through laughter, tears, and dreams we share,
A friendship built with loving care.
--------------------------------------------------

Task 5: Batch Processing Multiple Topics...

Poem 1 (ocean):
Beneath the waves where mysteries sleep,
The ocean holds its secrets deep.
With rhythmic tides and endless blue,
A world of wonder waits for you.

Poem 2 (mountains):
Majestic peaks that touch the sky,
Where eagles soar and spirits fly.
In silence grand, they stand so tall,
Nature's cathedrals over all.

Poem 3 (dreams):
In slumber's realm where visions dance,
Our minds take flight in mystic trance.
Where hopes and fears together weave,
The tapestry of what we believe.

=== Lab 01 Complete! ===
```

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Next Steps
After completing this lab, proceed to **Lab 02: LangChain Chains** to learn about more complex chain patterns.
