# src/compose/composition_engine.py

import networkx as nx
import json
from typing import Dict, List, Optional
from memory.polaris_memory import PolarisMemory
from memory.models import MemoryObject
from models.typed_edge import TypedEdge


class CompositionEngine:
    def __init__(self, memory: PolarisMemory):
        self.memory = memory
        self.graph = nx.DiGraph()
        self.modules: Dict[str, MemoryObject] = {}
        self.temporal_constraints = []

    def load_modules(self, jurisdiction: str, version: str = "v1") -> None:
        """Load PermittingModules matching the jurisdiction and version."""
        self.modules = {}
        for m in self.memory.objects.values():
            print(f"🧪 {m.id}: {m.jurisdiction} v{m.version} → {m.data.get('object_type')}")
            if (
                m.data.get("object_type") == "PermittingModule"
                and m.jurisdiction.lower() == jurisdiction.lower()
                and m.version.lower() == version.lower()
            ):
                self.modules[m.id] = m

    def load_temporal_constraints(self, path: str) -> None:
        """Load temporal constraints from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            self.temporal_constraints = json.load(f)

    def build_graph(self) -> None:
        """Construct a DAG using dependencies and temporal constraints."""
        print("\n📥 Modules loaded:")
        for module_id in self.modules:
            print(" -", module_id)
            self.graph.add_node(module_id)

        print("\n🔗 Adding dependency edges:")
        for module in self.modules.values():
            for dep in module.data.get("dependencies", []):
                if dep in self.modules:
                    print(f"   ✅ {dep} --> {module.id}")
                    self.graph.add_edge(dep, module.id)
                else:
                    print(f"   ⚠️ Dependency {dep} not found for {module.id}")

        print("\n⏱️ Adding temporal constraint edges:")
        for constraint in self.temporal_constraints:
            if constraint["type"] == "must_finish_before":
                src, tgt = constraint["module_ids"]
                if src in self.modules and tgt in self.modules:
                    print(f"   ✅ {src} --> {tgt}")
                    self.graph.add_edge(src, tgt)
                else:
                    print(f"   ⚠️ Constraint skipped: {src} -> {tgt} (missing)")

    def validate_graph(self) -> None:
        """Check graph for acyclic structure, required connectivity, start/end nodes."""
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Composition graph contains cycles.")

        # Disconnected nodes check
        disconnected = list(nx.isolates(self.graph))
        for node in disconnected:
            if not self.modules[node].data.get("optional", False):
                raise ValueError(f"Disconnected non-optional module: {node}")

        # Entry and exit nodes
        start_nodes = [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]
        end_nodes = [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]
        if not start_nodes:
            raise ValueError("Graph must have at least one start node.")
        if not end_nodes:
            raise ValueError("Graph must have at least one terminal node.")

    def export_composition(self, title: str, created_by: str, jurisdiction: str) -> MemoryObject:
        """Package the DAG into a Composition SDMO, including semantic/control-layer links."""
        
        modules = list(self.graph.nodes())
        module_ids = set(modules)

        # ✅ Construct typed edges from graph metadata
        edges: List[TypedEdge] = []
        for u, v in self.graph.edges():
            edge_data = self.graph.get_edge_data(u, v)
            edge_type = edge_data.get("edge_type", "dependency")
            label = edge_data.get("label")

            typed_edge = TypedEdge(
                from_node=u,
                to_node=v,
                type=edge_type,
                label=label
            )
            edges.append(typed_edge)

        # ✅ Collect semantic/control-layer links
        symbolic_ids = {
            obj.id for obj in self.memory.get_by_type("SymbolicScaffold")
            if obj.data.get("module_id") in module_ids
        }
        override_ids = {
            obj.data.get("override_id") or obj.id
            for obj in self.memory.get_by_type("OverrideProtocol")
            if obj.data.get("module_id") in module_ids
        }
        feedback_ids = {
            obj.data.get("loop_id") or obj.id
            for obj in self.memory.get_by_type("FeedbackLoop")
            if obj.data.get("trigger_module_id") in module_ids
        }
        failure_ids = {
            obj.data.get("failure_id") or obj.id
            for obj in self.memory.get_by_type("FailureEvent")
            if obj.data.get("module_id") in module_ids
        }

        # Collect typed edges from current graph
        edges = []
        for src, dst in self.graph.edges:
            edge_data = self.graph.get_edge_data(src, dst)
            edges.append({
                "from_node": src,
                "to_node": dst,
                "type": edge_data.get("type", "dependency"),
                "label": edge_data.get("label", ""),
            })

        # ✅ Build structured composition data dict
        composition_data = {
            "title": title,
            "jurisdiction": jurisdiction,
            "modules": modules,
            "edges":edges,
            "symbolic_scaffolds": list(symbolic_ids),
            "override_protocols": list(override_ids),
            "feedback_loops": list(feedback_ids),
            "failure_events": list(failure_ids),
            "created_by": created_by
        }

        # 🧠 DEBUG LOGGING
        print("🧠 MODULES IN GRAPH:", module_ids)

        print("🧠 SYMBOLIC SCAFFOLDS AVAILABLE:", [
            (obj.id, obj.data.get("module_id")) for obj in self.memory.get_by_type("SymbolicScaffold")
        ])

        print("✅ MATCHED SCAFFOLDS:", [
            obj.id for obj in self.memory.get_by_type("SymbolicScaffold")
            if obj.data.get("module_id") in module_ids
        ])

        print("🧠 DEBUG: All memory object types:")
        for obj in self.memory.objects.values():
            print(f"- {obj.id} | type={obj.data.get('object_type')} | module_id={obj.data.get('module_id')}")

        return MemoryObject(
            id=f"composition-{jurisdiction.lower()}-{title.lower().replace(' ', '_')}",
            object_type="Composition",
            jurisdiction=jurisdiction,
            version="v1",
            created_by=created_by,
            data=composition_data
        )

    def compose(self, jurisdiction: str, temporal_path: str, title: str, created_by: str) -> MemoryObject:
        """Run the full composition pipeline and return the SDMO."""
        self.load_modules(jurisdiction)
        self.load_temporal_constraints(temporal_path)
        self.build_graph()
        self.validate_graph()
        return self.export_composition(title, created_by, jurisdiction)


# ─────────────────────────────────────────────────────────────
# Extended Loader (for Interpreter, Simulate, Samaris)
# ─────────────────────────────────────────────────────────────

def load_composition_extended(composition: MemoryObject, memory: PolarisMemory):
    """
    Load a saved composition SDMO and reconstruct the full composition context.
    Returns a dict with graph, modules, edges, and any attached semantic/control-layer objects.
    """
    graph = nx.DiGraph()
    modules = {}
    edge_raw = composition.data.get("edges", [])
    
    typed_edges: List[TypedEdge] = []

    # Backward compatibility: tuple or dict
    for edge in edge_raw:
        if isinstance(edge, list) and len(edge) == 2:
            # Legacy (from, to) edge
            typed_edges.append(TypedEdge(from_node=edge[0], to_node=edge[1], type="dependency"))
        elif isinstance(edge, dict):
            # Already typed
            typed_edges.append(TypedEdge(**edge))
        else:
            print(f"⚠️ Invalid edge format: {edge}")

    # Build the graph using validated typed edges
    for edge in typed_edges:
        graph.add_edge(edge.from_node, edge.to_node, edge_type=edge.type, label=edge.label)

    module_ids = composition.data.get("modules", [])
    graph.add_nodes_from(module_ids)

    for mid in module_ids:
        obj = memory.objects.get(mid)
        if obj:
            modules[mid] = obj

    def resolve_ids(ids: List[str]) -> List[MemoryObject]:
        return [memory.objects.get(i) for i in ids if memory.objects.get(i)]

    return {
        "graph": graph,
        "modules": modules,
        "edges": typed_edges,
        "symbolic_scaffolds": resolve_ids(composition.data.get("symbolic_scaffolds", [])),
        "override_protocols": resolve_ids(composition.data.get("override_protocols", [])),
        "feedback_loops": resolve_ids(composition.data.get("feedback_loops", [])),
        "failure_events": resolve_ids(composition.data.get("failure_events", [])),
        "title": composition.data.get("title"),
        "created_by": composition.data.get("created_by"),
        "jurisdiction": composition.data.get("jurisdiction")
    }