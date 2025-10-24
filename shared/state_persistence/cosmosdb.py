"""
Azure Cosmos DB implementation for state persistence.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from azure.cosmos.aio import CosmosClient
from azure.cosmos import exceptions, PartitionKey

from .base import BaseStatePersistence, StateDocument


class CosmosDBStatePersistence(BaseStatePersistence):
    """
    Azure Cosmos DB implementation for storing LangGraph state.
    """
    
    def __init__(self, connection_string: str, table_name: str = "graph_states"):
        super().__init__(connection_string, table_name)
        self.client = None
        self.database = None
        self.container = None
        
        # Parse connection string to extract endpoint and key
        self._parse_connection_string()
    
    def _parse_connection_string(self):
        """Parse Cosmos DB connection string."""
        parts = self.connection_string.split(';')
        self.endpoint = None
        self.key = None
        
        for part in parts:
            if part.startswith('AccountEndpoint='):
                self.endpoint = part.split('=', 1)[1]
            elif part.startswith('AccountKey='):
                self.key = part.split('=', 1)[1]
        
        if not self.endpoint or not self.key:
            raise ValueError("Invalid Cosmos DB connection string")
    
    async def initialize(self) -> None:
        """Initialize Cosmos DB client and create database/container if needed."""
        self.client = CosmosClient(self.endpoint, credential=self.key)
        
        # Create database if it doesn't exist
        database_name = "langgraph_db"
        try:
            self.database = await self.client.create_database_if_not_exists(id=database_name)
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating database: {e}")
            raise
        
        # Create container if it doesn't exist
        try:
            self.container = await self.database.create_container_if_not_exists(
                id=self.table_name,
                partition_key=PartitionKey(path="/thread_id"),
                offer_throughput=400
            )
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating container: {e}")
            raise
    
    async def save_state(
        self,
        thread_id: str,
        checkpoint_id: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save state to Cosmos DB."""
        try:
            now = datetime.utcnow()
            document = {
                'id': f"{thread_id}_{checkpoint_id}",
                'thread_id': thread_id,
                'checkpoint_id': checkpoint_id,
                'state': state,
                'metadata': metadata or {},
                'created_at': now.isoformat(),
                'updated_at': now.isoformat()
            }
            
            await self.container.upsert_item(document)
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error saving state: {e}")
            return False
    
    async def load_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[StateDocument]:
        """Load state from Cosmos DB."""
        try:
            if checkpoint_id:
                # Load specific checkpoint
                doc_id = f"{thread_id}_{checkpoint_id}"
                document = await self.container.read_item(
                    item=doc_id,
                    partition_key=thread_id
                )
            else:
                # Load most recent checkpoint
                query = f"SELECT * FROM c WHERE c.thread_id = '{thread_id}' ORDER BY c.created_at DESC"
                items = [item async for item in self.container.query_items(
                    query=query,
                    partition_key=thread_id,
                    max_item_count=1
                )]
                if not items:
                    return None
                document = items[0]
            
            return StateDocument(
                thread_id=document['thread_id'],
                checkpoint_id=document['checkpoint_id'],
                state=document['state'],
                metadata=document.get('metadata'),
                created_at=datetime.fromisoformat(document['created_at']),
                updated_at=datetime.fromisoformat(document['updated_at'])
            )
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error loading state: {e}")
            return None
    
    async def list_checkpoints(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[StateDocument]:
        """List all checkpoints for a thread."""
        try:
            query = f"SELECT * FROM c WHERE c.thread_id = '{thread_id}' ORDER BY c.created_at DESC"
            items = [item async for item in self.container.query_items(
                query=query,
                partition_key=thread_id,
                max_item_count=limit
            )]
            
            return [
                StateDocument(
                    thread_id=item['thread_id'],
                    checkpoint_id=item['checkpoint_id'],
                    state=item['state'],
                    metadata=item.get('metadata'),
                    created_at=datetime.fromisoformat(item['created_at']),
                    updated_at=datetime.fromisoformat(item['updated_at'])
                )
                for item in items
            ]
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error listing checkpoints: {e}")
            return []
    
    async def delete_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """Delete state from Cosmos DB."""
        try:
            if checkpoint_id:
                # Delete specific checkpoint
                doc_id = f"{thread_id}_{checkpoint_id}"
                await self.container.delete_item(
                    item=doc_id,
                    partition_key=thread_id
                )
            else:
                # Delete all checkpoints for thread
                query = f"SELECT c.id FROM c WHERE c.thread_id = '{thread_id}'"
                items = [item async for item in self.container.query_items(
                    query=query,
                    partition_key=thread_id
                )]
                for item in items:
                    await self.container.delete_item(
                        item=item['id'],
                        partition_key=thread_id
                    )
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error deleting state: {e}")
            return False
    
    async def close(self) -> None:
        """Close Cosmos DB client."""
        if self.client:
            await self.client.close()
