"""
LangGraph Multi-Agent Systems - Implementation

A multi-agent system with researcher, writer, and supervisor agents.
"""

import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# Define the shared state
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    next_agent: str
    research_data: str
    draft_content: str
    final_content: str

def create_researcher_agent():
    """Create a research agent that gathers information on topics."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    
    def research_node(state: AgentState):
        print("🔍 Researcher Agent: Starting research...")
        
        # Get the last message or topic
        messages = state.get("messages", [])
        topic = messages[-1] if messages else "artificial intelligence"
        
        # Create research prompt
        research_prompt = f"""You are a research agent. Research the topic: {topic}
        
        Provide key facts, statistics, and insights about this topic.
        Format your response as bullet points with key information.
        Keep it concise but informative.
        """
        
        response = llm.invoke([SystemMessage(content=research_prompt)])
        research_data = response.content
        
        print(f"📊 Research completed on: {topic}")
        print(f"Research findings: {research_data[:100]}...")
        
        return {
            "messages": [f"Research completed on: {topic}"],
            "research_data": research_data,
            "next_agent": "writer"
        }
    
    return research_node

def create_writer_agent():
    """Create a writer agent that creates content based on research."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    def writer_node(state: AgentState):
        print("✍️ Writer Agent: Creating content...")
        
        research_data = state.get("research_data", "")
        
        # Create writing prompt
        writing_prompt = f"""You are a content writer. Create an engaging article based on this research:

        Research Data:
        {research_data}
        
        Write a well-structured article with:
        - Compelling introduction
        - Main body with key points
        - Conclusion
        
        Keep it informative but readable. Aim for 200-300 words.
        """
        
        response = llm.invoke([SystemMessage(content=writing_prompt)])
        draft_content = response.content
        
        print("📝 Draft content created")
        print(f"Content preview: {draft_content[:100]}...")
        
        return {
            "messages": [f"Draft content created"],
            "draft_content": draft_content,
            "next_agent": "supervisor"
        }
    
    return writer_node

def create_supervisor_agent():
    """Create a supervisor agent that coordinates other agents."""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    
    def supervisor_node(state: AgentState):
        print("👔 Supervisor Agent: Reviewing work...")
        
        research_data = state.get("research_data", "")
        draft_content = state.get("draft_content", "")
        
        # Review and decide next action
        review_prompt = f"""You are a supervisor reviewing the work of a research and writing team.

        Research Data:
        {research_data}
        
        Draft Content:
        {draft_content}
        
        Review the quality and decide:
        1. If the work is complete and satisfactory, respond with "APPROVED: [brief feedback]"
        2. If it needs revision, respond with "REVISION_NEEDED: [specific feedback]"
        
        Be constructive and specific in your feedback.
        """
        
        response = llm.invoke([SystemMessage(content=review_prompt)])
        feedback = response.content
        
        print(f"📋 Supervisor feedback: {feedback[:100]}...")
        
        if "APPROVED" in feedback:
            print("✅ Work approved by supervisor!")
            return {
                "messages": [f"Supervisor approved the work: {feedback}"],
                "final_content": draft_content,
                "next_agent": "END"
            }
        else:
            print("🔄 Revision requested by supervisor")
            return {
                "messages": [f"Supervisor requests revision: {feedback}"],
                "next_agent": "writer"
            }
    
    return supervisor_node

def should_continue(state: AgentState):
    """Determine the next agent to run."""
    next_agent = state.get("next_agent", "END")
    
    if next_agent == "END":
        return END
    else:
        return next_agent

def main():
    """Main function demonstrating multi-agent coordination."""
    print("="*80)
    print("LangGraph Multi-Agent Systems - Demo")
    print("="*80)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set your OpenAI API key in the environment or .env file")
        return
    
    try:
        # Create the agent graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("researcher", create_researcher_agent())
        workflow.add_node("writer", create_writer_agent())
        workflow.add_node("supervisor", create_supervisor_agent())
        
        # Set entry point
        workflow.set_entry_point("researcher")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "researcher",
            should_continue,
            {"writer": "writer", "END": END}
        )
        
        workflow.add_conditional_edges(
            "writer", 
            should_continue,
            {"supervisor": "supervisor", "END": END}
        )
        
        workflow.add_conditional_edges(
            "supervisor",
            should_continue,
            {"writer": "writer", "END": END}
        )
        
        # Compile the workflow
        app = workflow.compile()
        
        print("\n🤖 Starting multi-agent workflow...")
        print("Topic: Machine Learning in Healthcare")
        
        # Initialize state
        initial_state = {
            "messages": ["Machine Learning in Healthcare"],
            "next_agent": "researcher",
            "research_data": "",
            "draft_content": "",
            "final_content": ""
        }
        
        # Run the workflow
        print("\n" + "="*50)
        print("WORKFLOW EXECUTION")
        print("="*50)
        
        result = app.invoke(initial_state)
        
        print("\n" + "="*50)
        print("FINAL RESULTS")
        print("="*50)
        
        if result.get("final_content"):
            print("\n📄 FINAL APPROVED CONTENT:")
            print("-" * 40)
            print(result["final_content"])
        
        print(f"\n📊 Workflow Messages:")
        for i, msg in enumerate(result.get("messages", []), 1):
            print(f"{i}. {msg}")
            
        print("\n✅ Multi-agent workflow completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running workflow: {e}")
        print("Make sure you have the required dependencies installed:")
        print("pip install langchain langchain-openai langgraph python-dotenv")


if __name__ == "__main__":
    main()
