"""
Base class for state persistence implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel


class StateDocument(BaseModel):
    """Represents a saved state document."""
    thread_id: str
    checkpoint_id: str
    state: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class BaseStatePersistence(ABC):
    """
    Abstract base class for state persistence implementations.
    
    Each database implementation must inherit from this class and
    implement all abstract methods.
    """
    
    def __init__(self, connection_string: str, table_name: str = "graph_states"):
        """
        Initialize the state persistence handler.
        
        Args:
            connection_string: Database connection string
            table_name: Name of the table/collection to store states
        """
        self.connection_string = connection_string
        self.table_name = table_name
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the database connection and create necessary tables/collections.
        Should be idempotent.
        """
        pass
    
    @abstractmethod
    async def save_state(
        self,
        thread_id: str,
        checkpoint_id: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a state checkpoint to the database.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            checkpoint_id: Unique identifier for this checkpoint
            state: The state data to save
            metadata: Optional metadata about the state
            
        Returns:
            True if save was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def load_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[StateDocument]:
        """
        Load a state checkpoint from the database.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            checkpoint_id: Optional specific checkpoint ID to load.
                         If None, loads the most recent checkpoint.
            
        Returns:
            StateDocument if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_checkpoints(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[StateDocument]:
        """
        List all checkpoints for a thread.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            limit: Maximum number of checkpoints to return
            
        Returns:
            List of StateDocument objects, ordered by created_at descending
        """
        pass
    
    @abstractmethod
    async def delete_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """
        Delete state checkpoint(s) from the database.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            checkpoint_id: Optional specific checkpoint ID to delete.
                         If None, deletes all checkpoints for the thread.
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close database connections and cleanup resources.
        """
        pass
