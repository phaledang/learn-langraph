"""
Lab 08: LangGraph State Persistence - Starter Code

Complete the TODOs to implement state persistence.
"""

import os
import asyncio
from pathlib import Path
from typing import TypedDict
from dotenv import load_dotenv

_script_dir = Path(__file__).parent
load_dotenv(_script_dir / ".env")          # primary
load_dotenv(_script_dir / ".env.sample")   # fallback for defaults


# TODO: Task 1 - Import State Persistence Module
# Import create_state_persistence from shared.state_persistence


# TODO: Task 2 - Define State Schema
# Create a TypedDict for your graph state


# TODO: Task 3 - Create Checkpointed Graph
# Build a graph that uses the state persistence


# TODO: Task 4 - Implement Save/Load Functions
# Create functions to save and load checkpoints


# TODO: Task 5 - Build Persistent Conversational Agent
# Create an agent that maintains conversation history across sessions


async def main():
    print("Lab 08: LangGraph State Persistence - Starter")
    
    # TODO: Initialize persistence
    
    # TODO: Create and run graph
    
    # TODO: Save checkpoint
    
    # TODO: Load and resume
    
    pass


if __name__ == "__main__":
    asyncio.run(main())
