import streamlit as st
import streamlit.components.v1 as components
from studio.components.sidebar import render_composition_selector
from studio.components.dag_canvas import render_dag_pyvis

def render_explore_view(memory):
    selected_obj = render_composition_selector(memory)

    if not selected_obj:
        st.warning("No composition selected.")
        return

    st.subheader(f"📄 {selected_obj.id}")
    st.markdown(f"**Jurisdiction**: {selected_obj.jurisdiction}")
    st.markdown(f"**Created by**: {selected_obj.created_by}")
    st.markdown(f"**Modules**: {len(selected_obj.data.get('data', {}).get('modules', []))}")
    st.markdown(f"**Edges**: {len(selected_obj.data.get('data', {}).get('edges', []))}")

    # ─────────────────────────────────────────────────────────────
    # Symbolic Overlay Toggle + Legend
    # ─────────────────────────────────────────────────────────────
    show_symbolic = st.checkbox("🌀 Show Symbolic Overlay", value=False)

    with st.expander("🧭 Symbolic Overlay Legend"):
        st.markdown("""
        - 🟦 **Standard Module**: PermittingModule  
        - 🧿 **Symbolic Scaffold**: Module with cultural or narrative meaning (purple)  
        - ⚠️ **Fragile Path**: Module prone to failure events (red)  
        - 🌀 **Loop Trigger**: Feedback loop originates here (yellow)  
        - 🚨 **Override Protocol**: Special rule or override attached (orange)
        """)

    # ─────────────────────────────────────────────────────────────
    # Prepare DAG Data
    # ─────────────────────────────────────────────────────────────
    modules = selected_obj.data.get("data", {}).get("modules", [])
    edges = selected_obj.data.get("data", {}).get("edges", [])

    if not modules or not edges:
        st.error("This composition has no modules or edges. DAG cannot be rendered.")
        return

    # ─────────────────────────────────────────────────────────────
    # Render DAG on button press
    # ─────────────────────────────────────────────────────────────
    if st.button("🔍 Visualize DAG"):
        st.session_state["render_dag"] = True

    if st.session_state.get("render_dag", False):
        html_file = render_dag_pyvis(
            modules=modules,
            edges=edges,
            memory=memory,
            composition_id=selected_obj.id,
            show_symbolic=show_symbolic
        )
        with open(html_file, "r", encoding="utf-8") as f:
            components.html(f.read(), height=650, scrolling=True)

    # ─────────────────────────────────────────────────────────────
    # Governance Layers Summary
    # ─────────────────────────────────────────────────────────────
    symbolic = selected_obj.data.get("data", {}).get("symbolic_scaffolds", [])
    overrides = selected_obj.data.get("data", {}).get("override_protocols", [])
    feedbacks = selected_obj.data.get("data", {}).get("feedback_loops", [])
    failures = selected_obj.data.get("data", {}).get("failure_events", [])

    with st.expander("🧠 Attached Governance Layers"):
        st.markdown(f"🔮 **Symbolic Scaffolds:** {len(symbolic)} → {symbolic}")
        st.markdown(f"🚨 **Overrides:** {len(overrides)} → {overrides}")
        st.markdown(f"🔁 **Feedback Loops:** {len(feedbacks)} → {feedbacks}")
        st.markdown(f"⚠️ **Failure Events:** {len(failures)} → {failures}")