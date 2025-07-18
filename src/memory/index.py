# src/memory/index.py

from typing import Dict, List
from .models import MemoryObject


class MemoryIndex:
    """
    Lightweight indexing utility for tag-based lookups.
    """

    def __init__(self):
        self.tag_index: Dict[str, List[str]] = {}

    def index(self, obj: MemoryObject) -> None:
        for tag in obj.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if obj.id not in self.tag_index[tag]:
                self.tag_index[tag].append(obj.id)

    def get_by_tag(self, tag: str) -> List[str]:
        return self.tag_index.get(tag, [])
