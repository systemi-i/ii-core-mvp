# src/compose/graphviz_export.py

import networkx as nx
import pydot
from pathlib import Path
from typing import List
from memory.polaris_memory import PolarisMemory

def export_graph(edges: List[tuple], module_ids: List[str], output_path: Path = Path("dag_output.png"), memory: PolarisMemory = None):
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Create node labels using module names from memory
    labels = {}
    if memory:
        for mod_id in module_ids:
            obj = memory.get_by_id(mod_id)
            label = obj.data.get("module_name", mod_id) if obj else mod_id
            labels[mod_id] = label
    else:
        labels = {node: node for node in module_ids}

    # Convert to Pydot and customize
    dot = nx.nx_pydot.to_pydot(G)

    for node in dot.get_nodes():
        node_id = node.get_name().strip('"')
        node.set_label(labels.get(node_id, node_id))
        node.set_shape("box")
        node.set_style("filled")
        node.set_fillcolor("lightgray")

    dot.write_png(str(output_path))
    print(f"✅ DAG exported to: {output_path.resolve()}")
