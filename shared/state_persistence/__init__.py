"""
State Persistence Module

Provides database-agnostic state persistence for LangGraph applications.
Automatically detects and uses the appropriate database based on connection string.
"""

from .base import BaseStatePersistence, StateDocument
from .factory import create_state_persistence

__all__ = [
    'BaseStatePersistence',
    'StateDocument',
    'create_state_persistence'
]
