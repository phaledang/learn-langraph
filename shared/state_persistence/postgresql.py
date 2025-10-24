"""
PostgreSQL implementation for state persistence.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncpg

from .base import BaseStatePersistence, StateDocument


class PostgreSQLStatePersistence(BaseStatePersistence):
    """
    PostgreSQL implementation for storing LangGraph state.
    """
    
    def __init__(self, connection_string: str, table_name: str = "graph_states"):
        super().__init__(connection_string, table_name)
        self.pool = None
    
    async def initialize(self) -> None:
        """Initialize PostgreSQL connection pool and create table if needed."""
        # Create connection pool
        self.pool = await asyncpg.create_pool(self.connection_string)
        
        # Create table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            thread_id VARCHAR(255) NOT NULL,
            checkpoint_id VARCHAR(255) NOT NULL,
            state JSONB NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(thread_id, checkpoint_id)
        );
        
        CREATE INDEX IF NOT EXISTS idx_{self.table_name}_thread_id 
        ON {self.table_name}(thread_id);
        
        CREATE INDEX IF NOT EXISTS idx_{self.table_name}_created_at 
        ON {self.table_name}(created_at DESC);
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(create_table_query)
    
    async def save_state(
        self,
        thread_id: str,
        checkpoint_id: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save state to PostgreSQL."""
        try:
            query = f"""
            INSERT INTO {self.table_name} 
            (thread_id, checkpoint_id, state, metadata, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (thread_id, checkpoint_id) 
            DO UPDATE SET 
                state = EXCLUDED.state,
                metadata = EXCLUDED.metadata,
                updated_at = EXCLUDED.updated_at
            """
            
            now = datetime.utcnow()
            async with self.pool.acquire() as conn:
                await conn.execute(
                    query,
                    thread_id,
                    checkpoint_id,
                    json.dumps(state),
                    json.dumps(metadata) if metadata else None,
                    now,
                    now
                )
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    async def load_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[StateDocument]:
        """Load state from PostgreSQL."""
        try:
            if checkpoint_id:
                # Load specific checkpoint
                query = f"""
                SELECT thread_id, checkpoint_id, state, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE thread_id = $1 AND checkpoint_id = $2
                """
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(query, thread_id, checkpoint_id)
            else:
                # Load most recent checkpoint
                query = f"""
                SELECT thread_id, checkpoint_id, state, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE thread_id = $1
                ORDER BY created_at DESC
                LIMIT 1
                """
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(query, thread_id)
            
            if not row:
                return None
            
            return StateDocument(
                thread_id=row['thread_id'],
                checkpoint_id=row['checkpoint_id'],
                state=json.loads(row['state']) if isinstance(row['state'], str) else row['state'],
                metadata=json.loads(row['metadata']) if row['metadata'] and isinstance(row['metadata'], str) else row['metadata'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
        except Exception as e:
            print(f"Error loading state: {e}")
            return None
    
    async def list_checkpoints(
        self,
        thread_id: str,
        limit: int = 10
    ) -> List[StateDocument]:
        """List all checkpoints for a thread."""
        try:
            query = f"""
            SELECT thread_id, checkpoint_id, state, metadata, created_at, updated_at
            FROM {self.table_name}
            WHERE thread_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, thread_id, limit)
            
            return [
                StateDocument(
                    thread_id=row['thread_id'],
                    checkpoint_id=row['checkpoint_id'],
                    state=json.loads(row['state']) if isinstance(row['state'], str) else row['state'],
                    metadata=json.loads(row['metadata']) if row['metadata'] and isinstance(row['metadata'], str) else row['metadata'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]
        except Exception as e:
            print(f"Error listing checkpoints: {e}")
            return []
    
    async def delete_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> bool:
        """Delete state from PostgreSQL."""
        try:
            if checkpoint_id:
                # Delete specific checkpoint
                query = f"""
                DELETE FROM {self.table_name}
                WHERE thread_id = $1 AND checkpoint_id = $2
                """
                async with self.pool.acquire() as conn:
                    await conn.execute(query, thread_id, checkpoint_id)
            else:
                # Delete all checkpoints for thread
                query = f"""
                DELETE FROM {self.table_name}
                WHERE thread_id = $1
                """
                async with self.pool.acquire() as conn:
                    await conn.execute(query, thread_id)
            return True
        except Exception as e:
            print(f"Error deleting state: {e}")
            return False
    
    async def close(self) -> None:
        """Close PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
