# tests/test_composition_extended.py

from pathlib import Path
from compose.composition_engine import CompositionEngine, load_composition_extended
from memory.polaris_memory import PolarisMemory

def test_extended_composition_load():
    memory = PolarisMemory(Path("library/domains/urban_permitting/denpasar_v1"))
    engine = CompositionEngine(memory)

    # Step 1: Load and compose
    engine.load_modules("Denpasar")
    engine.graph.add_nodes_from([
        "mod-denpasar-environmental-assessment",
        "mod-denpasar-grid-coordination",
        "mod-denpasar-electrical-agreement",
        "mod-denpasar-public-consultation",
    ])
    engine.graph.add_edges_from([
        ("mod-denpasar-environmental-assessment", "mod-denpasar-grid-coordination"),
        ("mod-denpasar-grid-coordination", "mod-denpasar-electrical-agreement"),
        ("mod-denpasar-electrical-agreement", "mod-denpasar-public-consultation"),
    ])

    sdm = engine.export_composition("test_extended", "test:user", "Denpasar")

    # Step 2: Load composition from SDMO
    loaded = load_composition_extended(sdm, memory)

    assert "mod-denpasar-grid-coordination" in loaded["modules"]
    assert list(loaded["graph"].edges) == [
        ("mod-denpasar-environmental-assessment", "mod-denpasar-grid-coordination"),
        ("mod-denpasar-grid-coordination", "mod-denpasar-electrical-agreement"),
        ("mod-denpasar-electrical-agreement", "mod-denpasar-public-consultation"),
    ]
    assert isinstance(loaded["symbolic_scaffolds"], list)
    assert isinstance(loaded["override_protocols"], list)

    # Sanity check — are any tags actually found?
    assert len(loaded["symbolic_scaffolds"]) >= 1, "Expected at least one symbolic scaffold"
    assert len(loaded["override_protocols"]) >= 1, "Expected at least one override protocol"

    print("✅ Extended composition loaded with:")
    print("  - Modules:", list(loaded["modules"].keys()))
    print("  - Overrides:", [o.id for o in loaded["override_protocols"]])
    print("🧠 Symbolic matches:", [
    obj.id for obj in memory.get_by_type("SymbolicScaffold")
    if obj.data.get("module_id") in engine.graph.nodes
])
    print("  - Symbolic:", [s.id for s in loaded["symbolic_scaffolds"]])
    print("Symbolic scaffolds attached:", [s.id for s in loaded["symbolic_scaffolds"]])