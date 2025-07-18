# rename_modules_to_ids.py

import os
import json
from pathlib import Path

TARGET_DIR = Path("library/domains/urban_permitting/denpasar_v1")

def rename_files_to_module_id():
    for file in TARGET_DIR.glob("mod-*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("object_type") != "PermittingModule":
                continue

            module_id = data.get("module_id")
            if not module_id:
                print(f"⚠️  Skipping {file.name}: no module_id")
                continue

            new_filename = f"{module_id}.json"
            new_path = file.with_name(new_filename)

            if file.name == new_filename:
                print(f"✅ Already named correctly: {file.name}")
                continue

            if new_path.exists():
                print(f"🚫 Target already exists: {new_filename}")
                continue

            file.rename(new_path)
            print(f"🔁 Renamed {file.name} → {new_filename}")

        except Exception as e:
            print(f"❌ Failed to process {file.name}: {e}")

if __name__ == "__main__":
    rename_files_to_module_id()
