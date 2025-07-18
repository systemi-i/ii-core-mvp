# src/simulate/simulation_engine.py

import random
import networkx as nx
from typing import Dict, Tuple, List
from compose.composition_engine import CompositionEngine
from memory.polaris_memory import PolarisMemory
from memory.models import MemoryObject


def simulate_run(
    graph: nx.DiGraph,
    modules: Dict[str, MemoryObject],
    params: dict
) -> Tuple[int, Dict[str, int]]:
    durations = {}
    rework_count = {}

    for node in nx.topological_sort(graph):
        base_duration = random.randint(*params["task_duration_range"])
        failure = random.random() < params["failure_rate"]
        loops = 0

        while failure and loops < params["max_feedback_loops"]:
            loops += 1
            base_duration += random.randint(*params["task_duration_range"])
            failure = random.random() < params["failure_rate"]

        durations[node] = base_duration
        rework_count[node] = loops

    total_duration = sum(durations.values())
    return total_duration, rework_count


def format_edges_for_nx(edge_dicts: List[dict]) -> List[Tuple[str, str, dict]]:
    """
    Convert edge dictionaries to NetworkX-compatible 3-tuples.
    """
    return [
        (e["from_node"], e["to_node"], {k: v for k, v in e.items() if k not in ("from_node", "to_node")})
        for e in edge_dicts
    ]


def run_simulation(
    composition: MemoryObject,
    memory: PolarisMemory,
    params: dict,
    runs: int = 1000,
    debug: bool = False,
    formatted_edges: List[Tuple[str, str, dict]] = None
):
    # 🧠 Extract modules + edges from SDMO schema
    module_ids = composition.data.get("data", {}).get("modules", [])
    raw_edges = composition.data.get("data", {}).get("edges", [])

    # If not pre-formatted, format now
    if formatted_edges is None:
        formatted_edges = format_edges_for_nx(raw_edges)

    # Validate and filter valid PermittingModules
    valid_modules = {}
    for mid in module_ids:
        obj = memory.get_by_id(mid)
        if obj and obj.object_type == "PermittingModule":
            valid_modules[mid] = obj

    if debug:
        print("🧪 DEBUG: Checking modules...")
        print("Modules in composition:")
        for i, mid in enumerate(module_ids):
            print(f"{i}: {mid}")
        for mid in module_ids:
            obj = memory.get_by_id(mid)
            print(f"→ {mid}: {obj.object_type if obj else 'NOT FOUND'}")
        print(f"✅ Valid modules found: {list(valid_modules.keys())}")

    if not valid_modules:
        raise ValueError("No valid modules found in memory for this composition.")

    results = []
    all_reworks = []

    for _ in range(runs):
        G = nx.DiGraph()
        G.add_nodes_from(valid_modules.keys())
        G.add_edges_from(formatted_edges)

        duration, reworks = simulate_run(G, valid_modules, params)
        results.append(duration)
        all_reworks.append(reworks)

    avg_duration = sum(results) / len(results)
    module_fail_freq = {mod: 0 for mod in valid_modules}
    for rework in all_reworks:
        for mod, count in rework.items():
            if count > 0:
                module_fail_freq[mod] += 1

    return {
        "avg_duration": avg_duration,
        "runs": runs,
        "failures": module_fail_freq,
    }
