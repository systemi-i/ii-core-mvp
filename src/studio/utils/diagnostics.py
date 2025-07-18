import networkx as nx
from typing import List, Dict

def run_diagnostics(modules: List[str], edges: List[List[str]], memory) -> Dict:
    g = nx.DiGraph()
    g.add_nodes_from(modules)
    g.add_edges_from(edges)

    has_cycle = not nx.is_directed_acyclic_graph(g)
    disconnected = list(nx.isolates(g))

    orphan_non_optional = []
    for node in disconnected:
        obj = memory.get_by_id(node)
        if obj and not obj.data.get("optional", False):
            orphan_non_optional.append(node)

    # ✅ Match on trigger_module_id (not related_modules)
    # ✅ Use loop_id if available, fallback to id
    feedback_loops = []
    for obj in memory.get_by_type("FeedbackLoop"):
        trigger = obj.data.get("trigger_module_id")
        if trigger in modules:
            loop_label = obj.data.get("loop_id", obj.id)
            feedback_loops.append(loop_label)

    return {
        "has_cycle": has_cycle,
        "disconnected": disconnected,
        "orphan_non_optional": orphan_non_optional,
        "feedback_loops": feedback_loops,
    }
