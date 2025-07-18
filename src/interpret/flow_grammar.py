# src/interpret/flow_grammar.py

import networkx as nx
from typing import Dict, List, Tuple
from memory.models import MemoryObject
from memory.polaris_memory import PolarisMemory

def interpret_flow(composition: MemoryObject, memory: PolarisMemory) -> Dict:
    """
    Run semantic and structural validation on a Composition SDMO.
    Returns a canonical interpretation output.
    """
    modules = composition.data.get("modules", [])
    edge_dicts = composition.data.get("edges", [])

    # Extract edge tuples safely
    edges = [
        (e["from_node"], e["to_node"])
        for e in edge_dicts
        if isinstance(e, dict) and "from_node" in e and "to_node" in e
    ]

    graph = nx.DiGraph()
    graph.add_nodes_from(modules)
    graph.add_edges_from(edges)

    errors = []
    warnings = []

    # Structural validation
    is_valid_dag, dag_errors = validate_dag(graph)
    if not is_valid_dag:
        errors.extend(dag_errors)

    # Orphan / disconnected module check
    disconnected = list(nx.isolates(graph))
    for module_id in disconnected:
        module_obj = memory.get_by_id(module_id)
        optional = module_obj and module_obj.data.get("optional", False)
        if not optional:
            warnings.append(f"Disconnected module (not marked optional): {module_id}")

    # Semantic tagging
    tags = tag_modules(modules, memory)

    # Fragility analysis
    fragile_paths = detect_fragile_paths(graph, tags)
    symbolic_modules = [m for m, t in tags.items() if "symbolic" in t]

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "module_count": len(modules),
            "edge_count": len(edges),
            "symbolic_modules": symbolic_modules,
            "fragile_paths": fragile_paths,
            "disconnected_modules": disconnected
        },
        "tags": tags
    }


def validate_dag(graph: nx.DiGraph) -> Tuple[bool, List[str]]:
    """
    Ensure the graph is a valid DAG.
    Returns (valid, errors).
    """
    errors = []
    if not nx.is_directed_acyclic_graph(graph):
        errors.append("Graph contains cycles.")
        return False, errors

    start_nodes = [n for n in graph.nodes if graph.in_degree(n) == 0]
    end_nodes = [n for n in graph.nodes if graph.out_degree(n) == 0]

    if not start_nodes:
        errors.append("No start node found (no node with in-degree 0).")
    if not end_nodes:
        errors.append("No terminal node found (no node with out-degree 0).")

    return len(errors) == 0, errors


def tag_modules(modules: List[str], memory: PolarisMemory) -> Dict[str, List[str]]:
    """
    Tags each module with semantic properties (symbolic, override, feedback).
    """
    tags = {}

    symbolic_ids = {obj.data.get("module_id") for obj in memory.get_by_type("SymbolicScaffold")}
    override_ids = {obj.data.get("module_id") for obj in memory.get_by_type("OverrideProtocol")}
    feedback_ids = {
        obj.data.get("trigger_module_id") for obj in memory.get_by_type("FeedbackLoop")
    }

    for module_id in modules:
        module_tags = []
        if module_id in symbolic_ids:
            module_tags.append("symbolic")
        if module_id in override_ids:
            module_tags.append("override_risk")
        if module_id in feedback_ids:
            module_tags.append("feedback_trigger")
        tags[module_id] = module_tags

    return tags


def detect_fragile_paths(graph: nx.DiGraph, tags: Dict[str, List[str]]) -> List[List[str]]:
    """
    Identify edges where fragility might occur (e.g. symbolic to override).
    """
    fragile = []
    for src, tgt in graph.edges():
        src_tags = tags.get(src, [])
        tgt_tags = tags.get(tgt, [])
        if "symbolic" in src_tags or "override_risk" in tgt_tags:
            fragile.append([src, tgt])
    return fragile
