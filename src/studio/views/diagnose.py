import streamlit as st
from studio.components.sidebar import render_composition_selector
from studio.utils.diagnostics import run_diagnostics
from studio.components.diagnostics_panel import render_diagnostics_panel


def format_edges_for_nx(edge_dicts):
    """
    Convert list of edge dicts to NetworkX-compatible (from, to, attrs) tuples.
    """
    return [
        (e["from_node"], e["to_node"], {k: v for k, v in e.items() if k not in ("from_node", "to_node")})
        for e in edge_dicts
    ]


def render_diagnose_view(memory):
    selected_obj = render_composition_selector(memory)
    if not selected_obj:
        return

    st.subheader(f"🧪 Diagnosing: {selected_obj.id}")

    data = selected_obj.data.get("data", {})
    modules = data.get("modules", [])
    edge_dicts = data.get("edges", [])

    symbolic = data.get("symbolic_scaffolds", [])
    overrides = data.get("override_protocols", [])
    feedbacks = data.get("feedback_loops", [])
    failures = data.get("failure_events", [])

    with st.expander("🧠 Attached Governance Layers"):
        st.markdown(f"🔮 **Symbolic Scaffolds:** {len(symbolic)} → {symbolic}")
        st.markdown(f"🚨 **Overrides:** {len(overrides)} → {overrides}")
        st.markdown(f"🔁 **Feedback Loops:** {len(feedbacks)} → {feedbacks}")
        st.markdown(f"⚠️ **Failures:** {len(failures)} → {failures}")

    if st.button("Run Diagnostics"):
        formatted_edges = format_edges_for_nx(edge_dicts)
        try:
            results = run_diagnostics(modules, formatted_edges, memory)
            render_diagnostics_panel(results)
        except Exception as e:
            st.error(f"❌ Diagnostic error: {e}")