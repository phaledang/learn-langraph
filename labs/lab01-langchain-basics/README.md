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

## Tasks

### Task 1: Initialize LLM Model
Create a ChatOpenAI instance and test it with a simple prompt.

### Task 2: Create Prompt Templates
Build a prompt template that accepts user input variables.

### Task 3: Build a Chain
Combine the LLM and prompt template into a chain.

### Task 4: Add Output Parsing
Parse the LLM output into a structured format.

### Task 5: Create a Complete Application
Build a simple application that generates creative content based on user input.

## Expected Outcomes
By the end of this lab, you should be able to:
- Initialize and use LangChain LLM models
- Create reusable prompt templates
- Build basic chains
- Parse LLM outputs
- Understand the LangChain component architecture

## Resources
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Next Steps
After completing this lab, proceed to **Lab 02: LangChain Chains** to learn about more complex chain patterns.
