"""
Factory function to create the appropriate state persistence implementation
based on the connection string.
"""

import os
from typing import Optional

from .base import BaseStatePersistence
from .cosmosdb import CosmosDBStatePersistence
from .postgresql import PostgreSQLStatePersistence
from .sqlserver import SQLServerStatePersistence


def detect_database_type(connection_string: str) -> str:
    """
    Detect database type from connection string.
    
    Args:
        connection_string: Database connection string
        
    Returns:
        Database type: 'cosmosdb', 'postgresql', or 'sqlserver'
        
    Raises:
        ValueError: If database type cannot be determined
    """
    connection_string_lower = connection_string.lower()
    
    # Check for Cosmos DB
    if 'accountendpoint' in connection_string_lower and 'accountkey' in connection_string_lower:
        return 'cosmosdb'
    
    # Check for PostgreSQL
    if connection_string_lower.startswith('postgresql://') or connection_string_lower.startswith('postgres://'):
        return 'postgresql'
    
    # Check for SQL Server
    if 'mssql' in connection_string_lower or 'sqlserver' in connection_string_lower:
        return 'sqlserver'
    
    raise ValueError(
        f"Unable to detect database type from connection string. "
        f"Supported formats: "
        f"Cosmos DB (AccountEndpoint=...), "
        f"PostgreSQL (postgresql://...), "
        f"SQL Server (mssql+pyodbc://...)"
    )


def create_state_persistence(
    connection_string: Optional[str] = None,
    table_name: Optional[str] = None
) -> BaseStatePersistence:
    """
    Create a state persistence instance based on the connection string.
    
    Args:
        connection_string: Database connection string. If None, reads from
                         DATABASE_CONNECTION_STRING environment variable.
        table_name: Name of the table/collection. If None, reads from
                   DATABASE_TABLE_NAME environment variable or uses default.
        
    Returns:
        BaseStatePersistence instance for the detected database type
        
    Raises:
        ValueError: If connection string is not provided or database type
                   cannot be determined
        
    Example:
        >>> # Using environment variables
        >>> persistence = create_state_persistence()
        >>> 
        >>> # Or providing values directly
        >>> persistence = create_state_persistence(
        ...     connection_string="postgresql://user:pass@localhost/db",
        ...     table_name="my_states"
        ... )
    """
    # Get connection string from parameter or environment
    if connection_string is None:
        connection_string = os.getenv('DATABASE_CONNECTION_STRING')
    
    if not connection_string:
        raise ValueError(
            "No connection string provided. Either pass connection_string parameter "
            "or set DATABASE_CONNECTION_STRING environment variable."
        )
    
    # Get table name from parameter or environment or use default
    if table_name is None:
        table_name = os.getenv('DATABASE_TABLE_NAME', 'graph_states')
    
    # Detect database type
    db_type = detect_database_type(connection_string)
    
    # Create appropriate instance
    if db_type == 'cosmosdb':
        return CosmosDBStatePersistence(connection_string, table_name)
    elif db_type == 'postgresql':
        return PostgreSQLStatePersistence(connection_string, table_name)
    elif db_type == 'sqlserver':
        return SQLServerStatePersistence(connection_string, table_name)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# Example usage
if __name__ == "__main__":
    # This demonstrates how to use the factory
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def demo():
        # Create persistence instance (automatically detects database type)
        persistence = create_state_persistence()
        
        # Initialize the database
        await persistence.initialize()
        
        # Save a state
        await persistence.save_state(
            thread_id="conversation_123",
            checkpoint_id="checkpoint_001",
            state={"messages": ["Hello", "How are you?"], "step": 2},
            metadata={"user_id": "user_456"}
        )
        
        # Load the state
        state_doc = await persistence.load_state(
            thread_id="conversation_123"
        )
        print(f"Loaded state: {state_doc}")
        
        # List all checkpoints
        checkpoints = await persistence.list_checkpoints(
            thread_id="conversation_123"
        )
        print(f"Found {len(checkpoints)} checkpoints")
        
        # Cleanup
        await persistence.close()
    
    # Run demo
    asyncio.run(demo())
