
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import json
from memory.models import MemoryObject
from compose.composition_engine import load_composition_extended
from memory.polaris_memory import PolarisMemory
from compose.composition_engine import CompositionEngine

def test_load_typed_edge_composition():
    test_path = Path("tests/composition-test-typededges.json")

    with open(test_path, "r") as f:
        data = json.load(f)
        comp = MemoryObject(**data)

    # ✅ Mock PolarisMemory with dummy modules (no load_default)
    memory = PolarisMemory(memory_path=Path("tests/mock-memory"))
    memory.objects = {
        "mod-A": MemoryObject(id="mod-A", object_type="PermittingModule", data={}),
        "mod-B": MemoryObject(id="mod-B", object_type="PermittingModule", data={}),
        "mod-C": MemoryObject(id="mod-C", object_type="PermittingModule", data={}),
    }

    result = load_composition_extended(comp, memory)

    assert len(result["edges"]) == 3
    edge_types = {e.type for e in result["edges"]}
    assert "dependency" in edge_types
    assert "conditional" in edge_types
    assert "override" in edge_types

    override_edge = next(e for e in result["edges"] if e.type == "override")
    assert override_edge.override_action == "skip_step"

    assert result["graph"].has_edge("mod-A", "mod-C")
    edge_data = result["graph"]["mod-A"]["mod-C"]
    assert edge_data["edge_type"] == "override"

def test_export_composition_outputs_typed_edges():
    from memory.models import MemoryObject
    from memory.polaris_memory import PolarisMemory
    from compose.composition_engine import CompositionEngine

    # Step 1: Set up a mock memory and engine
    memory = PolarisMemory(memory_path=Path("tests/mock-memory"))
    memory.objects = {
    "mod-A": MemoryObject(
        id="mod-A",
        object_type="PermittingModule",
        jurisdiction="TestJurisdiction",
        version="v1",
        data={
            "dependencies": [],
            "jurisdiction": "TestJurisdiction",
            "version": "v1",
            "object_type": "PermittingModule"
        }
    ),
    "mod-B": MemoryObject(
        id="mod-B",
        object_type="PermittingModule",
        jurisdiction="TestJurisdiction",
        version="v1",
        data={
            "dependencies": ["mod-A"],
            "jurisdiction": "TestJurisdiction",
            "version": "v1",
            "object_type": "PermittingModule"
        }
    )
}

    engine = CompositionEngine(memory)
    engine.load_modules("TestJurisdiction")
    engine.build_graph()

    # Step 2: Export composition
    comp = engine.export_composition(title="EdgeTest", created_by="test-user", jurisdiction="TestJurisdiction")

    # Step 3: Validate typed edges in export
    assert comp.object_type == "Composition"
    edge_data = comp.data["edges"]
    assert isinstance(edge_data, list)
    assert all("from_node" in e and "to_node" in e and "type" in e for e in edge_data)
    assert any(e["type"] == "dependency" for e in edge_data)

def test_export_and_save_composition():
    memory_path = Path("tests/mock-memory")
    memory = PolarisMemory(memory_path=memory_path)

    memory.objects = {
        "mod-A": MemoryObject(
            id="mod-A",
            object_type="PermittingModule",
            jurisdiction="TestJurisdiction",
            version="v1",
            data={
                "dependencies": [],
                "jurisdiction": "TestJurisdiction",
                "version": "v1",
                "object_type": "PermittingModule"
            }
        ),
        "mod-B": MemoryObject(
            id="mod-B",
            object_type="PermittingModule",
            jurisdiction="TestJurisdiction",
            version="v1",
            data={
                "dependencies": ["mod-A"],
                "jurisdiction": "TestJurisdiction",
                "version": "v1",
                "object_type": "PermittingModule"
            }
        )
    }

    engine = CompositionEngine(memory)
    engine.load_modules("TestJurisdiction")
    engine.build_graph()
    comp = engine.export_composition(
        title="EdgeTestSaved",
        created_by="test-user",
        jurisdiction="TestJurisdiction"
    )

    # ✅ Save the composition
    memory.save_object(comp)

    # ✅ Confirm file was written
    saved_path = memory_path / f"{comp.id}.json"
    assert saved_path.exists()

    # ✅ Optionally reload and verify
    with open(saved_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
        assert saved_data["object_type"] == "Composition"
        assert len(saved_data["data"]["edges"]) >= 1