"""
Lab 02: LangChain Chains - Solution Code

Advanced chain patterns including sequential, router, and RAG chains.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough

# Load environment variables from .env file relative to this script
load_dotenv(Path(__file__).parent / ".env")


def task1_sequential_chain():
    """Demonstrate sequential chain processing."""
    print("\n=== Task 1: Sequential Chain ===")
    
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.3,
    )
    
    # Step 1: Summarization
    summarize_template = """Summarize the following text in 2-3 sentences:

Text: {text}

Summary:"""
    
    summarize_prompt = PromptTemplate(
        input_variables=["text"],
        template=summarize_template
    )
    
    # Step 2: Extract key points
    extract_template = """From the following summary, extract 3 key points as a bullet list:

Summary: {summary}

Key Points:"""
    
    extract_prompt = PromptTemplate(
        input_variables=["summary"],
        template=extract_template
    )
    
    # Build chains
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    extract_chain = extract_prompt | llm | StrOutputParser()
    
    # Test document
    document = """
    Artificial Intelligence has revolutionized how we approach problem-solving 
    in the modern world. Machine learning algorithms can now process vast amounts 
    of data to identify patterns and make predictions. Deep learning, a subset of 
    machine learning, uses neural networks to tackle complex tasks like image 
    recognition and natural language processing. These technologies are being 
    applied across industries, from healthcare to finance, improving efficiency 
    and enabling new capabilities.
    """
    
    # Execute sequential processing
    summary = summarize_chain.invoke({"text": document})
    print(f"Summary:\n{summary}\n")
    
    key_points = extract_chain.invoke({"summary": summary})
    print(f"Key Points:\n{key_points}")


def task2_router_chain():
    """Demonstrate router chain with conditional routing."""
    print("\n\n=== Task 2: Router Chain ===")
    
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.7,
    )
    
    # Different prompts for different query types
    math_template = """You are a math tutor. Solve this math problem step by step:

Problem: {query}

Solution:"""
    
    coding_template = """You are a coding expert. Provide a code solution with explanation:

Question: {query}

Solution:"""
    
    general_template = """Provide a helpful answer to this question:

Question: {query}

Answer:"""
    
    # Create prompt templates
    math_prompt = PromptTemplate(template=math_template, input_variables=["query"])
    coding_prompt = PromptTemplate(template=coding_template, input_variables=["query"])
    general_prompt = PromptTemplate(template=general_template, input_variables=["query"])
    
    # Create chains
    math_chain = math_prompt | llm | StrOutputParser()
    coding_chain = coding_prompt | llm | StrOutputParser()
    general_chain = general_prompt | llm | StrOutputParser()
    
    def route_query(query: str):
        """Simple routing logic based on keywords."""
        query_lower = query.lower()
        if any(word in query_lower for word in ["calculate", "math", "equation", "solve"]):
            return "math"
        elif any(word in query_lower for word in ["code", "python", "function", "program"]):
            return "coding"
        else:
            return "general"
    
    # Test queries
    queries = [
        "Calculate the sum of numbers from 1 to 100",
        "Write a Python function to reverse a string",
        "What is the capital of France?"
    ]
    
    for query in queries:
        route = route_query(query)
        print(f"\nQuery: {query}")
        print(f"Route: {route}")
        
        if route == "math":
            result = math_chain.invoke({"query": query})
        elif route == "coding":
            result = coding_chain.invoke({"query": query})
        else:
            result = general_chain.invoke({"query": query})
        
        print(f"Response:\n{result}\n")
        print("-" * 80)


def task3_rag_implementation():
    """Implement retrieval augmented generation."""
    print("\n\n=== Task 3: RAG Implementation ===")
    
    # Sample documents
    documents = [
        Document(page_content="LangChain is a framework for developing applications powered by language models."),
        Document(page_content="LangGraph allows you to build stateful, multi-actor applications with LLMs."),
        Document(page_content="LangSmith helps with debugging, testing, and monitoring LLM applications."),
        Document(page_content="Vector stores enable efficient similarity search for document retrieval."),
        Document(page_content="Embeddings are vector representations of text that capture semantic meaning."),
    ]
    
    # Split documents (in real scenarios, you'd have larger documents)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    splits = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name="langchain_docs"
    )
    
    # Create retrieval chain using LCEL
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    qa_template = """Use the following context to answer the question. If you don't know the answer, say you don't know.

Context: {context}

Question: {question}

Answer:"""
    qa_prompt = PromptTemplate(template=qa_template, input_variables=["context", "question"])
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    qa_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    # Test queries
    questions = [
        "What is LangChain?",
        "How does LangSmith help developers?",
        "What are embeddings?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = qa_chain.invoke(question)
        print(f"Answer: {answer}\n")
        print("-" * 80)


def main():
    """Run all tasks."""
    print("=== Lab 02: LangChain Chains - Solution ===")
    
    # Check API key
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        print("Error: AZURE_OPENAI_API_KEY not set")
        return
    
    task1_sequential_chain()
    task2_router_chain()
    task3_rag_implementation()
    
    print("\n=== Lab 02 Complete! ===")


if __name__ == "__main__":
    main()
