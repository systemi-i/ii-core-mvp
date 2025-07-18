import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from models.typed_edge import TypedEdge
from memory.models import MemoryObject
from memory.polaris_memory import PolarisMemory
from compose.composition_engine import CompositionEngine
from studio.components.dag_canvas import render_dag_pyvis


# Set up memory and dummy modules
from pathlib import Path
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
    ),
    "mod-C": MemoryObject(
        id="mod-C",
        object_type="PermittingModule",
        jurisdiction="TestJurisdiction",
        version="v1",
        data={
            "dependencies": [],
            "jurisdiction": "TestJurisdiction",
            "version": "v1",
            "object_type": "PermittingModule"
        }
    )
}

# Manually define typed edges
edges = [
    TypedEdge(from_node="mod-A", to_node="mod-B", type="dependency").model_dump(),
    TypedEdge(from_node="mod-B", to_node="mod-C", type="override", label="⚡").model_dump(),
    TypedEdge(from_node="mod-A", to_node="mod-C", type="conditional", condition="X == True").model_dump(),
]

modules = ["mod-A", "mod-B", "mod-C"]

# Render DAG
html_path = render_dag_pyvis(modules, edges, memory, composition_id="test_dag_viz")

print(f"✅ DAG rendered: {html_path}")
