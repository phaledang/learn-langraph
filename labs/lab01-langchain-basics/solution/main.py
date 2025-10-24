"""
Lab 01: LangChain Basics - Solution Code

A complete implementation of basic LangChain concepts.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Load environment variables
load_dotenv()


def main():
    """
    Main function demonstrating LangChain basics.
    """
    print("=== Lab 01: LangChain Basics ===\n")
    
    # Task 1: Initialize LLM Model
    print("Task 1: Initializing LLM Model...")
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    print("✓ LLM initialized\n")
    
    # Task 2: Create Prompt Template
    print("Task 2: Creating Prompt Template...")
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
    print("✓ Prompt template created\n")
    
    # Task 3: Build a Chain using LCEL (LangChain Expression Language)
    print("Task 3: Building Chain...")
    chain = prompt | llm | StrOutputParser()
    print("✓ Chain built\n")
    
    # Task 4: Test the Chain
    print("Task 4: Testing Chain...")
    topics = ["artificial intelligence", "nature", "friendship"]
    
    for topic in topics:
        print(f"\n--- Poem about '{topic}' ---")
        result = chain.invoke({"topic": topic})
        print(result)
        print("-" * 50)
    
    # Task 5: Demonstrate batch processing
    print("\nTask 5: Batch Processing Multiple Topics...")
    batch_topics = [
        {"topic": "ocean"},
        {"topic": "mountains"},
        {"topic": "dreams"}
    ]
    
    batch_results = chain.batch(batch_topics)
    
    for i, result in enumerate(batch_results):
        print(f"\nPoem {i+1} ({batch_topics[i]['topic']}):")
        print(result)
    
    print("\n=== Lab 01 Complete! ===")


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in your .env file.")
        exit(1)
    
    main()
