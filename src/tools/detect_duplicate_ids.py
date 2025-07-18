# detect_duplicate_ids.py

from pathlib import Path
import json
from collections import defaultdict

DATA_DIR = Path("library/domains/urban_permitting/denpasar_v1")

# Map: ID → list of (filename, object_type, jurisdiction_version)
id_map = defaultdict(list)

for file in DATA_DIR.glob("*.json"):
    try:
        with open(file, "r", encoding="utf-8") as f:
            content = json.load(f)
            records = content if isinstance(content, list) else [content]

            for obj in records:
                object_id = (
                    obj.get("module_id") or
                    obj.get("failure_id") or
                    obj.get("loop_id") or
                    obj.get("reform_id") or
                    obj.get("override_id") or
                    obj.get("actor_map_id") or
                    obj.get("scaffold_id") or
                    obj.get("term") or
                    f"auto-{file.stem}"
                )
                object_type = obj.get("object_type", "Unknown")
                version = obj.get("jurisdiction_version", "N/A")

                id_map[object_id].append((file.name, object_type, version))
    except Exception as e:
        print(f"❌ Failed to read {file.name}: {e}")

# Print duplicates with conflicting versions
print("\n🔍 Checking for conflicting object IDs with multiple definitions:\n")
for object_id, entries in id_map.items():
    if len(entries) > 1:
        versions = set(v for _, _, v in entries)
        if len(versions) > 1:
            print(f"⚠️ {object_id} defined with multiple versions:")
            for filename, objtype, ver in entries:
                print(f"   → {filename} ({objtype}) → version={ver}")
