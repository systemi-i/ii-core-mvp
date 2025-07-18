from pyvis.network import Network
from pathlib import Path
from typing import List
from memory.polaris_memory import PolarisMemory

def export_interactive_dag(edges: List[tuple], module_ids: List[str], memory: PolarisMemory, output_path="dag_interactive.html"):
    net = Network(height="800px", width="100%", directed=True)
    net.barnes_hut(gravity=-40000, central_gravity=0.3)

    type_colors = {
        "PermittingModule": "#3DAEE9",
        "SymbolicScaffold": "#D08AE6",
        "FailureEvent": "#FF6F61",
        "OverrideProtocol": "#F4A259",
        "FeedbackLoop": "#66BB6A",
        "Composition": "#B0BEC5",
        "Unknown": "#CCCCCC"
    }

    for mod_id in module_ids:
        obj = memory.get_by_id(mod_id)
        label = f"{mod_id}\n({obj.object_type})" if obj else mod_id
        color = type_colors.get(obj.object_type if obj else "Unknown", "#CCCCCC")
        net.add_node(mod_id, label=label, color=color, title=f"Type: {obj.object_type if obj else 'Unknown'}")

    for src, dst in edges:
        net.add_edge(src, dst)

    net.set_options("""var options = {
      "nodes": {"font": {"multi": "md"}},
      "edges": {"color": {"inherit": true}, "smooth": false},
      "physics": {"enabled": true,"barnesHut": {"gravitationalConstant": -10000,"centralGravity": 0.2,
      "springLength": 100,"springConstant": 0.04,"damping": 0.09,"avoidOverlap": 0.5}}}""")

    net.show(str(output_path), notebook=False)
    print(f"✅ Interactive HTML DAG exported to: {output_path}")
