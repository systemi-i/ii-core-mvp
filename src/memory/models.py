# src/memory/models.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4


class MemoryObject(BaseModel):
    """
    Core schema for Self-Describing Memory Objects (SDMOs).
    This wraps a governance object with metadata for versioning, tagging, and provenance.
    """

    id: str
    object_type: str
    jurisdiction: Optional[str] = None
    version: Optional[str] = None
    created_on: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    previous_version: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    data: dict  # Contains object-specific fields (e.g. permitting module content)

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        if tag in self.tags:
            self.tags.remove(tag)

    def clone_with_new_id(self, new_data: dict, created_by: Optional[str] = None) -> "MemoryObject":
        """
        Creates a new version of this object with a new ID and updated data.
        """
        return MemoryObject(
            id=f"{self.object_type}:{uuid4().hex[:8]}",
            object_type=self.object_type,
            jurisdiction=self.jurisdiction,
            version=self.version,
            created_on=datetime.utcnow(),
            created_by=created_by,
            previous_version=self.id,
            tags=self.tags.copy(),
            data=new_data
        )
