"""
ZeroDB Memory Module

Handles memory operations for context retention and retrieval.
"""

from typing import TYPE_CHECKING, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from ..client import AINativeClient


class MemoryPriority(Enum):
    """Memory priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MemoryClient:
    """Client for ZeroDB memory operations."""
    
    def __init__(self, client: "AINativeClient"):
        """
        Initialize memory client.

        Args:
            client: Parent AINative client instance
        """
        self.client = client
        self.base_path = "/projects"
    
    def create(
        self,
        project_id: str,
        content: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Create a new memory entry.

        Args:
            project_id: Project ID (required)
            content: Memory content
            title: Memory title
            tags: List of tags
            priority: Memory priority level
            metadata: Additional metadata
            user_id: Associated user ID
            expires_at: Expiration timestamp

        Returns:
            Created memory details

        Example:
            >>> memory = client.zerodb.memory.create(
            ...     PROJECT_ID,
            ...     content="User prefers dark mode",
            ...     tags=["preferences", "ui"]
            ... )
        """
        data = {
            "content": content,
            "title": title or "Memory Entry",
            "tags": tags or [],
            "priority": priority.value,
            "metadata": metadata or {},
        }

        if user_id:
            data["user_id"] = user_id
        if expires_at:
            data["expires_at"] = expires_at.isoformat()

        return self.client.post(f"{self.base_path}/{project_id}/database/memory", data=data)
    
    def list(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[MemoryPriority] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List memory entries.

        Args:
            project_id: Project ID (required)
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            user_id: Filter by user ID
            tags: Filter by tags
            priority: Filter by priority
            search: Search query

        Returns:
            Dictionary containing memories list and pagination info

        Example:
            >>> memories = client.zerodb.memory.list(PROJECT_ID, limit=50)
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if user_id:
            params["user_id"] = user_id
        if tags:
            params["tags"] = ",".join(tags)
        if priority:
            params["priority"] = priority.value
        if search:
            params["search"] = search

        return self.client.get(f"{self.base_path}/{project_id}/database/memory", params=params)
    
    def get(self, project_id: str, memory_id: str) -> Dict[str, Any]:
        """
        Get a specific memory entry.

        Args:
            project_id: Project ID (required)
            memory_id: Memory ID

        Returns:
            Memory details
        """
        return self.client.get(f"{self.base_path}/{project_id}/database/memory/{memory_id}")
    
    def update(
        self,
        project_id: str,
        memory_id: str,
        content: Optional[str] = None,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        priority: Optional[MemoryPriority] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a memory entry.

        Args:
            project_id: Project ID (required)
            memory_id: Memory ID
            content: New content
            title: New title
            tags: New tags
            priority: New priority
            metadata: New metadata

        Returns:
            Updated memory details
        """
        data = {}
        if content is not None:
            data["content"] = content
        if title is not None:
            data["title"] = title
        if tags is not None:
            data["tags"] = tags
        if priority is not None:
            data["priority"] = priority.value
        if metadata is not None:
            data["metadata"] = metadata

        return self.client.patch(f"{self.base_path}/{project_id}/database/memory/{memory_id}", data=data)
    
    def delete(self, project_id: str, memory_id: str) -> Dict[str, Any]:
        """
        Delete a memory entry.

        Args:
            project_id: Project ID (required)
            memory_id: Memory ID

        Returns:
            Deletion confirmation
        """
        return self.client.delete(f"{self.base_path}/{project_id}/database/memory/{memory_id}")
    
    def search(
        self,
        project_id: str,
        query: str,
        limit: int = 10,
        user_id: Optional[str] = None,
        semantic: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Search memories using text or semantic search.

        Args:
            project_id: Project ID (required)
            query: Search query
            limit: Maximum number of results
            user_id: Filter by user ID
            semantic: Use semantic search (if False, uses text search)

        Returns:
            List of matching memories

        Example:
            >>> results = client.zerodb.memory.search(
            ...     PROJECT_ID,
            ...     query="What does user prefer?",
            ...     top_k=5
            ... )
        """
        data = {
            "query": query,
            "limit": limit,
            "semantic": semantic,
        }

        if user_id:
            data["user_id"] = user_id

        response = self.client.post(f"{self.base_path}/{project_id}/database/memory/search", data=data)
        return response.get("results", [])
    
    def bulk_create(
        self,
        project_id: str,
        memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create multiple memory entries at once.

        Args:
            project_id: Project ID (required)
            memories: List of memory data dictionaries

        Returns:
            Bulk creation result
        """
        data = {
            "memories": memories,
        }

        return self.client.post(f"{self.base_path}/{project_id}/database/memory/bulk", data=data)
    
    def get_related(
        self,
        project_id: str,
        memory_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get memories related to a specific memory.

        Args:
            project_id: Project ID (required)
            memory_id: Memory ID
            limit: Maximum number of related memories

        Returns:
            List of related memories
        """
        params = {"limit": limit}
        response = self.client.get(f"{self.base_path}/{project_id}/database/memory/{memory_id}/related", params=params)
        return response.get("memories", [])