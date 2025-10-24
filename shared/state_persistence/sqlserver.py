"""
SQL Server implementation for state persistence.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from .base import BaseStatePersistence, StateDocument


class SQLServerStatePersistence(BaseStatePersistence):
    """
    SQL Server implementation for storing LangGraph state.
    """
    
    def __init__(self, connection_string: str, table_name: str = "graph_states"):
        super().__init__(connection_string, table_name)
        self.engine = None
        self.async_session = None
    
    async def initialize(self) -> None:
        """Initialize SQL Server connection and create table if needed."""
        # Create async engine
        self.engine = create_async_engine(
            self.connection_string,
            echo=False,
            future=True
        )
        
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create table if it doesn't exist
        create_table_query = f"""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{self.table_name}')
        BEGIN
            CREATE TABLE {self.table_name} (
                id INT IDENTITY(1,1) PRIMARY KEY,
                thread_id NVARCHAR(255) NOT NULL,
                checkpoint_id NVARCHAR(255) NOT NULL,
                state NVARCHAR(MAX) NOT NULL,
                metadata NVARCHAR(MAX),
                created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
                updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
                CONSTRAINT UQ_{self.table_name}_thread_checkpoint UNIQUE (thread_id, checkpoint_id)
            );
            
            CREATE INDEX idx_{self.table_name}_thread_id 
            ON {self.table_name}(thread_id);
            
            CREATE INDEX idx_{self.table_name}_created_at 
            ON {self.table_name}(created_at DESC);
        END
        """
        
        async with self.engine.begin() as conn:
            await conn.execute(text(create_table_query))
    
    async def save_state(
        self,
        thread_id: str,
        checkpoint_id: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save state to SQL Server."""
        try:
            state_json = json.dumps(state)
            metadata_json = json.dumps(metadata) if metadata else None
            now = datetime.utcnow()
            
            # Use MERGE for upsert operation
            query = f"""
            MERGE {self.table_name} AS target
            USING (SELECT :thread_id AS thread_id, :checkpoint_id AS checkpoint_id) AS source
            ON (target.thread_id = source.thread_id AND target.checkpoint_id = source.checkpoint_id)
            WHEN MATCHED THEN
                UPDATE SET 
                    state = :state,
                    metadata = :metadata,
                    updated_at = :updated_at
            WHEN NOT MATCHED THEN
                INSERT (thread_id, checkpoint_id, state, metadata, created_at, updated_at)
                VALUES (:thread_id, :checkpoint_id, :state, :metadata, :created_at, :updated_at);
            """
            
            async with self.async_session() as session:
                await session.execute(
                    text(query),
                    {
                        'thread_id': thread_id,
                        'checkpoint_id': checkpoint_id,
                        'state': state_json,
                        'metadata': metadata_json,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                await session.commit()
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False
    
    async def load_state(
        self,
        thread_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional[StateDocument]:
        """Load state from SQL Server."""
        try:
            if checkpoint_id:
                # Load specific checkpoint
                query = f"""
                SELECT thread_id, checkpoint_id, state, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE thread_id = :thread_id AND checkpoint_id = :checkpoint_id
                """
                params = {'thread_id': thread_id, 'checkpoint_id': checkpoint_id}
            else:
                # Load most recent checkpoint
                query = f"""
                SELECT TOP 1 thread_id, checkpoint_id, state, metadata, created_at, updated_at
                FROM {self.table_name}
                WHERE thread_id = :thread_id
                ORDER BY created_at DESC
                """
                params = {'thread_id': thread_id}
            
            async with self.async_session() as session:
                result = await session.execute(text(query), params)
                row = result.fetchone()
            
            if not row:
                return None
            
            return StateDocument(
                thread_id=row.thread_id,
                checkpoint_id=row.checkpoint_id,
                state=json.loads(row.state),
                metadata=json.loads(row.metadata) if row.metadata else None,
                created_at=row.created_at,
                updated_at=row.updated_at
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
            SELECT TOP :limit thread_id, checkpoint_id, state, metadata, created_at, updated_at
            FROM {self.table_name}
            WHERE thread_id = :thread_id
            ORDER BY created_at DESC
            """
            
            async with self.async_session() as session:
                result = await session.execute(
                    text(query),
                    {'thread_id': thread_id, 'limit': limit}
                )
                rows = result.fetchall()
            
            return [
                StateDocument(
                    thread_id=row.thread_id,
                    checkpoint_id=row.checkpoint_id,
                    state=json.loads(row.state),
                    metadata=json.loads(row.metadata) if row.metadata else None,
                    created_at=row.created_at,
                    updated_at=row.updated_at
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
        """Delete state from SQL Server."""
        try:
            if checkpoint_id:
                # Delete specific checkpoint
                query = f"""
                DELETE FROM {self.table_name}
                WHERE thread_id = :thread_id AND checkpoint_id = :checkpoint_id
                """
                params = {'thread_id': thread_id, 'checkpoint_id': checkpoint_id}
            else:
                # Delete all checkpoints for thread
                query = f"""
                DELETE FROM {self.table_name}
                WHERE thread_id = :thread_id
                """
                params = {'thread_id': thread_id}
            
            async with self.async_session() as session:
                await session.execute(text(query), params)
                await session.commit()
            return True
        except Exception as e:
            print(f"Error deleting state: {e}")
            return False
    
    async def close(self) -> None:
        """Close SQL Server engine."""
        if self.engine:
            await self.engine.dispose()
