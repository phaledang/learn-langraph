"""
Lab 01: LangChain Basics - Starter Code

Complete the TODOs to implement a basic LangChain application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """
    Main function to run the LangChain basics lab.
    """
    # TODO: Task 1 - Initialize LLM Model
    # Import ChatOpenAI from langchain_openai
    # Create an instance of ChatOpenAI with model="gpt-3.5-turbo"
    
    
    # TODO: Task 2 - Create Prompt Template
    # Import PromptTemplate from langchain.prompts
    # Create a template that asks the LLM to write a poem about a given topic
    # The template should have an input variable called "topic"
    
    
    # TODO: Task 3 - Build a Chain
    # Import LLMChain from langchain.chains (or use LCEL with |)
    # Combine the prompt and LLM into a chain
    
    
    # TODO: Task 4 - Test the Chain
    # Run the chain with topic="artificial intelligence"
    # Print the result
    
    
    # TODO: Task 5 - Add Output Parsing (Bonus)
    # Create a parser that extracts the poem into a structured format
    # Hint: Look at StrOutputParser or create a custom parser
    
    
    print("Lab 01 Complete!")


if __name__ == "__main__":
    main()
