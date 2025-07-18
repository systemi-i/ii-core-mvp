from pyvis.network import Network
import tempfile
import os
import streamlit as st


def render_dag_pyvis(modules, edges, memory, composition_id, show_symbolic=False):
    net = Network(height="600px", width="100%", directed=True)
    net.barnes_hut(gravity=-30000)

    # Base colors by object type
    type_colors = {
        "PermittingModule": "#3DAEE9",
        "SymbolicScaffold": "#D08AE6",
        "FailureEvent": "#FF6F61",
        "OverrideProtocol": "#F4A259",
        "FeedbackLoop": "#66BB6A",
        "Composition": "#B0BEC5",
        "Unknown": "#CCCCCC"
    }

    # Edge styles by edge type
    edge_styles = {
        "dependency": {"color": "#B0BEC5", "label": "", "dashes": False},
        "temporal": {"color": "#FFA726", "label": "⏱", "dashes": True},
        "conditional": {"color": "#42A5F5", "label": "❓", "dashes": True},
        "override": {"color": "#EF5350", "label": "⚡", "dashes": False},
        "semantic_link": {"color": "#AB47BC", "label": "∿", "dashes": [2, 2]},
        "actor_constraint": {"color": "#26A69A", "label": "🔒", "dashes": [5, 3]},
        "feedback_loop": {"color": "#66BB6A", "label": "🌀", "dashes": True},
    }

    # Preload overlays
    symbolic_scaffolds = {obj.data.get("module_id") for obj in memory.get_by_type("SymbolicScaffold")}
    failure_events = {obj.data.get("module_id") for obj in memory.get_by_type("FailureEvent")}
    override_protocols = {obj.data.get("module_id") for obj in memory.get_by_type("OverrideProtocol")}
    feedback_loops = memory.get_by_type("FeedbackLoop")
    feedback_triggers = {loop.data.get("trigger_module_id"): loop for loop in feedback_loops}

    # Tag and color for each node
    def get_tag_info(mid):
        tags = []
        color = "#3DAEE9"  # default

        if mid in symbolic_scaffolds:
            tags.append("🧿")
            color = "#D08AE6"
        if mid in failure_events:
            tags.append("⚠️")
            color = "#FF6F61"
        if mid in override_protocols:
            tags.append("🚨")
            color = "#F4A259"
        if mid in feedback_triggers:
            tags.append("🌀")
            color = "#FFD700"

        return " ".join(tags), color

    # Render nodes
    for mod_id in modules:
        obj = memory.get_by_id(mod_id)
        base_label = f"{mod_id}\n({obj.object_type})" if obj else mod_id
        tag_badges, tag_color = get_tag_info(mod_id)
        label = f"{tag_badges} {base_label}" if tag_badges else base_label
        net.add_node(mod_id, label=label, color=tag_color)

    # Render edges with type-aware styles
    for edge in edges:
        if isinstance(edge, (list, tuple)) and len(edge) == 2:
            src, dst = edge
            net.add_edge(src, dst, color="#B0BEC5")
        elif isinstance(edge, dict):
            src = edge.get("from_node")
            dst = edge.get("to_node")
            edge_type = edge.get("type", "dependency")
            style = edge_styles.get(edge_type, edge_styles["dependency"])
            net.add_edge(src, dst, label=style["label"], color=style["color"], dashes=style["dashes"])

    # Write to temp HTML and return path
    tmp_dir = tempfile.gettempdir()
    out_file = os.path.join(tmp_dir, f"{composition_id}.html")
    net.write_html(out_file)
    return out_file
