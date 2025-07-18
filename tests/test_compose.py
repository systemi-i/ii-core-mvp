import sys
from pathlib import Path
import json

# Add src/ to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from memory.polaris_memory import PolarisMemory
from compose.composition_engine import CompositionEngine

def main():
    # Load memory from Denpasar domain
    memory_path = Path("library/domains/urban_permitting/denpasar_v1")
    memory = PolarisMemory(memory_path)
    engine = CompositionEngine(memory)

    # Compose a new DAG
    composition_sdm = engine.compose(
        jurisdiction="Denpasar",
        temporal_path=str(memory_path / "temporal_constraints.json"),
        title="Denpasar BESS Permitting Flow",
        created_by="Federico"
    )

    # ✅ Debug: Ensure data is fully populated
    print("\n✅ DEBUG: Composition keys:", composition_sdm.data.keys())
    print("📌 Title:", composition_sdm.data.get("title"))
    print("🧱 Modules:", composition_sdm.data.get("modules"))
    print("🔗 Edges:", composition_sdm.data.get("edges")[:5])

    # Save to memory
    memory.save_object(composition_sdm)

    # ✅ Write composition as standalone file
    composition_file = memory_path / "composition-denpasar-denpasar_bess_permitting_flow.json"
    try:
        data = composition_sdm.model_dump() if hasattr(composition_sdm, "model_dump") else composition_sdm.dict()
        data["id"] = composition_sdm.id
        with open(composition_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"💾 Composition written to: {composition_file}")
    except Exception as e:
        print(f"❌ Failed to write composition file: {e}")

    # Confirm save
    print("\n📦 Compositions now in memory:")
    for obj in memory.get_by_type("Composition"):
        print(" -", obj.id)

    memory.save_all()

if __name__ == "__main__":
    main()
