"""
Polaris Memory Engine – Interence OS v1.5

Loads and manages Self-Describing Memory Objects (SDMOs) used across the OS.
Provides querying, indexing, versioning, and tagging capabilities.

Author: Interence Core Team
"""

import os
import json
from uuid import uuid4
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .models import MemoryObject
from .index import MemoryIndex


class PolarisMemory:
    def __init__(self, memory_path: Path):
        """
        Initialize and load all SDMOs from a specified memory directory.
        """
        self.memory_path = memory_path
        self.objects: Dict[str, MemoryObject] = {}
        self.index = MemoryIndex()
        self.load_all()

    def load_all(self) -> None:
        """
        Load all JSON files in the memory directory and index them.
        """
        for file in self.memory_path.glob("*.json"):
            print(f"📄 Scanning: {file.name}")
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        for item in content:
                            self._add_object(item)
                    else:
                        self._add_object(content)
            except Exception as e:
                print(f"❌ Error loading {file.name}: {e}")

    def _add_object(self, raw: dict) -> None:
        """
        Wraps a raw governance domain object into a MemoryObject.
        """
        try:
            object_id = (
                raw.get("id") or
                raw.get("module_id") or
                raw.get("failure_id") or
                raw.get("loop_id") or
                raw.get("reform_id") or
                raw.get("override_id") or
                raw.get("jurisdiction_id") or
                raw.get("actor_map_id") or
                raw.get("scaffold_id") or
                raw.get("term") or
                f"auto-{uuid4().hex[:8]}"
            )

            obj = MemoryObject(
                id=object_id,
                object_type=raw.get("object_type", "Unknown"),
                jurisdiction=raw.get("jurisdiction", "Denpasar"),
                version=raw.get("jurisdiction_version", "v1"),
                created_on=datetime.utcnow(),
                created_by="system:bootstrap",
                tags=[],
                data=raw
            )

            print(f"📦 {obj.id} → jurisdiction_version: {obj.version}")
            print(f"🧠 Adding object: {obj.id} | type: {obj.object_type}")

            if obj.id not in self.objects or obj.object_type == "PermittingModule":
                self.objects[obj.id] = obj
                self.index.index(obj)

        except Exception as e:
            print(f"⚠️ Failed to wrap object: {e}")

    def get_by_id(self, object_id: str) -> Optional[MemoryObject]:
        return self.objects.get(object_id)

    def get_by_type(self, object_type: str) -> List[MemoryObject]:
        return [obj for obj in self.objects.values() if obj.object_type == object_type]

    def query_by_tag(self, tag: str) -> List[MemoryObject]:
        ids = self.index.get_by_tag(tag)
        return [self.objects[obj_id] for obj_id in ids if obj_id in self.objects]

    def query(self, filter_fn: Callable[[MemoryObject], bool]) -> List[MemoryObject]:
        return [obj for obj in self.objects.values() if filter_fn(obj)]

    def save_object(self, obj: MemoryObject) -> None:
        """
        Save a single MemoryObject to disk and update memory/index.
        """
        try:
            filepath = self.memory_path / f"{obj.id}.json"

            # Validate path
            if not os.access(self.memory_path, os.W_OK):
                print(f"❌ Cannot write to path: {self.memory_path}")
                return

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(obj.dict(), f, indent=2, default=str)

            self.objects[obj.id] = obj
            self.index.index(obj)
            print(f"✅ Saved object: {obj.id} → {filepath.name}")

        except Exception as e:
            print(f"❌ Failed to save object {obj.id}: {e}")

    def create_version(self, base_id: str, new_data: dict, created_by: Optional[str] = None) -> Optional[MemoryObject]:
        """
        Create a new version of an existing object.
        """
        base = self.get_by_id(base_id)
        if not base:
            print(f"⚠️ Base object {base_id} not found.")
            return None
        new_obj = base.clone_with_new_id(new_data, created_by)
        self.save_object(new_obj)
        return new_obj

    def add_tag(self, object_id: str, tag: str):
        obj = self.get_by_id(object_id)
        if obj:
            obj.add_tag(tag)
            self.index.index(obj)

    def remove_tag(self, object_id: str, tag: str):
        obj = self.get_by_id(object_id)
        if obj:
            obj.remove_tag(tag)
            self.index.index(obj)

    def save_all(
        self,
        export_dir: Optional[Path] = None,
        only_type: Optional[str] = None,
        only_tag: Optional[str] = None,
        verbose: bool = True
    ) -> Path:
        """
        Export memory objects to JSON files in a target directory.
        Can optionally filter by object type or tag.
        """
        if export_dir is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            export_dir = Path("export") / timestamp

        export_dir.mkdir(parents=True, exist_ok=True)

        filtered_objects = list(self.objects.values())
        if only_type:
            filtered_objects = [obj for obj in filtered_objects if obj.object_type == only_type]
        if only_tag:
            filtered_objects = [obj for obj in filtered_objects if only_tag in obj.tags]

        grouped: Dict[str, List[MemoryObject]] = {}
        for obj in filtered_objects:
            grouped.setdefault(obj.object_type, []).append(obj)

        for obj_type in sorted(grouped.keys()):
            type_dir = export_dir / obj_type
            type_dir.mkdir(parents=True, exist_ok=True)
            for obj in grouped[obj_type]:
                safe_id = "".join(c for c in obj.id if c.isalnum() or c in ("-_")).rstrip()
                file_name = f"{safe_id}.json"
                with open(type_dir / file_name, "w", encoding="utf-8") as f:
                    json.dump(obj.model_dump(), f, indent=2, default=str)

        if verbose:
            print(f"✅ Polaris memory exported to: {export_dir.resolve()}")
            print("📊 Export Summary:")
            for obj_type in sorted(grouped.keys()):
                print(f" - {obj_type}: {len(grouped[obj_type])} objects")
            print(f"🧠 Total exported SDMOs: {sum(len(v) for v in grouped.values())}")

            if "PermittingModule" in grouped:
                all_module_ids = {obj.id for obj in grouped["PermittingModule"]}
                linked_ids = {
                    obj.data.get("module_id")
                    for obj in filtered_objects
                    if obj.object_type in {"FailureEvent", "FeedbackLoop", "ReformVariant", "OverrideProtocol"}
                }
                orphans = sorted(all_module_ids - linked_ids)
                if orphans:
                    print("🚨 Unlinked Permitting Modules (potential orphans):")
                    for oid in orphans:
                        print(f"   - {oid}")
                else:
                    print("✅ All permitting modules are linked to reforms, failures, or feedback.")

        return export_dir
