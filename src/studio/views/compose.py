import streamlit as st
import streamlit.components.v1 as components
from memory.models import MemoryObject
from compose.composition_engine import CompositionEngine
import networkx as nx
from studio.components.dag_canvas import render_dag_pyvis

from interpret.flow_grammar import interpret_flow


def render_compose_view(memory):
    st.subheader("🧱 Compose New Governance Flow")
    from models.typed_edge import TypedEdge
    # ─────────────────────────────────────────────────────────────
    # Step 1: Jurisdiction Selection
    # ─────────────────────────────────────────────────────────────
    jurisdictions = sorted(set(
        obj.jurisdiction for obj in memory.get_by_type("PermittingModule") if obj.jurisdiction
    ))
    selected_jurisdiction = st.selectbox("🌍 Jurisdiction", jurisdictions)

    all_modules = [
        m for m in memory.get_by_type("PermittingModule")
        if m.jurisdiction == selected_jurisdiction
    ]
    module_ids = [m.id for m in all_modules]
    selected_modules = st.multiselect("📦 Select Modules", module_ids)

    if not selected_modules:
        st.info("Select modules to continue.")
        return

    title = st.text_input("Composition Title")
    created_by = st.text_input("Created By", value="user:compose")

    # ─────────────────────────────────────────────────────────────
    # Step 1.5: Semantic Layer Preview
    # ─────────────────────────────────────────────────────────────
    symbolic_map = {obj.data.get("module_id"): obj.id for obj in memory.get_by_type("SymbolicScaffold")}
    override_map = {obj.data.get("module_id"): obj.id for obj in memory.get_by_type("OverrideProtocol")}
    feedback_map = {obj.data.get("trigger_module_id"): obj.id for obj in memory.get_by_type("FeedbackLoop")}
    failure_map = {obj.data.get("module_id"): obj.id for obj in memory.get_by_type("FailureEvent")}

    matched_symbolic = [symbolic_map[mid] for mid in selected_modules if mid in symbolic_map]
    matched_override = [override_map[mid] for mid in selected_modules if mid in override_map]
    matched_feedback = [feedback_map[mid] for mid in selected_modules if mid in feedback_map]
    matched_failure = [failure_map[mid] for mid in selected_modules if mid in failure_map]

    st.markdown("### 🧠 Semantic & Control-Layer Annotations")
    col1, col2 = st.columns(2)
    col1.metric("🔮 Symbolic Scaffolds", len(matched_symbolic))
    col1.metric("⚠️ Failure Events", len(matched_failure))
    col2.metric("🔁 Feedback Loops", len(matched_feedback))
    col2.metric("🚨 Override Protocols", len(matched_override))

    with st.expander("📋 View Attached Object IDs"):
        st.markdown(f"**Symbolic Scaffolds:** {matched_symbolic}")
        st.markdown(f"**Overrides:** {matched_override}")
        st.markdown(f"**Feedback Loops:** {matched_feedback}")
        st.markdown(f"**Failures:** {matched_failure}")

    # ─────────────────────────────────────────────────────────────
    # Step 2: Edge Definition
    # ─────────────────────────────────────────────────────────────
    st.markdown("🔗 Define Edges (from → to)")
    typed_edge_inputs = []
    edge_type_options = [
        "dependency", "temporal", "conditional", "override",
        "semantic_link", "actor_constraint", "feedback_loop"
    ]

    for i in range(len(selected_modules)):
        col1, col2, col3 = st.columns([4, 4, 2])
        with col1:
            src = st.selectbox(f"Edge {i+1} – from", selected_modules, key=f"edge_src_{i}")
        with col2:
            dst = st.selectbox(f"Edge {i+1} – to", selected_modules, key=f"edge_dst_{i}")
        with col3:
            etype = st.selectbox("Type", edge_type_options, index=0, key=f"edge_type_{i}")
        if src != dst:
            typed_edge_inputs.append({
                "from_node": src,
                "to_node": dst,
                "type": etype,
                "label": ""
            })

     # Deduplicate
    unique_edges = {(e["from_node"], e["to_node"], e["type"]) for e in typed_edge_inputs}
    typed_edge_inputs = [
        {"from_node": src, "to_node": dst, "type": typ, "label": ""}
        for (src, dst, typ) in unique_edges
    ]

    preview_graph = nx.DiGraph()
    preview_graph.add_edges_from((e["from_node"], e["to_node"]) for e in typed_edge_inputs)

    if not nx.is_directed_acyclic_graph(preview_graph):
        st.error("⚠️ Warning: This graph contains a cycle.")
    elif not typed_edge_inputs:
        st.warning("⚠️ No edges defined. Flow will be disconnected.")

    # ─────────────────────────────────────────────────────────────
    # Step 3: DAG Preview
    # ─────────────────────────────────────────────────────────────
    if st.button("🔍 Preview DAG"):
        st.markdown("#### 🔎 Edge Preview")
        st.json(typed_edge_inputs)
        
        html_file = render_dag_pyvis(
            modules=selected_modules,
            edges=typed_edge_inputs,
            memory=memory,
            composition_id="preview",
            show_symbolic=False
        )
        with open(html_file, "r", encoding="utf-8") as f:
            components.html(f.read(), height=650, scrolling=True)

        # ─────────────────────────────────────────────────────────
        # Step 3.5: Interpretation Diagnostic
        # ─────────────────────────────────────────────────────────
        if title and selected_modules:
            with st.expander("🧠 Interpret Composition", expanded=False):
                composition_preview = MemoryObject(
                    id="preview-composition",
                    object_type="Composition",
                    jurisdiction=selected_jurisdiction,
                    version="v1",
                    created_by=created_by,
                    data={
                        "title": title,
                        "jurisdiction": selected_jurisdiction,
                        "modules": selected_modules,
                        "edges": typed_edge_inputs,
                        "created_by": created_by
                    }
                )
                interp = interpret_flow(composition_preview, memory)

                st.markdown("#### ✅ Validity")
                if interp["valid"]:
                    st.success("✅ Valid DAG")
                else:
                    st.error("❌ Invalid Composition")

                for err in interp["errors"]:
                    st.error(f"- {err}")
                for warn in interp["warnings"]:
                    st.warning(f"- {warn}")

                st.markdown("#### 📊 Summary")
                st.json(interp["summary"])

                st.markdown("#### 🏷️ Module Tags")
                def tag_to_emoji(tag):
                    return {
                        "fragile": "⚠️",
                        "loop-prone": "🔁",
                        "symbolic": "🧿",
                        "bottleneck": "🚧",
                        "political": "📢",
                    }.get(tag, "🏷️")

                for mod_id, taglist in interp["tags"].items():
                    tag_str = " ".join(f"{tag_to_emoji(t)} `{t}`" for t in taglist) or "—"
                    st.markdown(f"- **{mod_id}**: {tag_str}")

    # ─────────────────────────────────────────────────────────────
    # Step 4: Save Composition
    # ─────────────────────────────────────────────────────────────
    st.markdown("💾 **Save Composition**")
    if st.button("💾 Save to Polaris"):
        if not title:
            st.warning("⚠️ Please enter a title before saving.")
            return
        if not selected_modules:
            st.warning("⚠️ No modules selected.")
            return
        if not nx.is_directed_acyclic_graph(preview_graph):
            st.error("❌ Cannot save — graph contains a cycle.")
            return

        engine = CompositionEngine(memory)
        engine.graph.clear()
        engine.modules = {m.id: m for m in all_modules if m.id in selected_modules}
        engine.graph.add_nodes_from(selected_modules)

        for edge in typed_edge_inputs:
            engine.graph.add_edge(edge["from_node"], edge["to_node"], {
                k: v for k, v in edge.items() if k not in ("from_node", "to_node")
            })

        try:
            engine.validate_graph()
            new_sdm = engine.export_composition(title, created_by, selected_jurisdiction)

            # Save metadata + properly structured edge dicts
            new_sdm.data.update({
                "edges": [
                    {
                        "from_node": e["from_node"],
                        "to_node": e["to_node"],
                        "type": e.get("type", "dependency"),
                        "label": e.get("label", "")
                    } for e in typed_edge_inputs
                ],
                "modules": selected_modules,
                "symbolic_scaffolds": matched_symbolic,
                "override_protocols": matched_override,
                "feedback_loops": matched_feedback,
                "failure_events": matched_failure
            })

            memory.save_object(new_sdm)
            st.success(f"✅ Composition saved: `{new_sdm.id}`")
            st.balloons()

            st.markdown("### ✅ Flow saved successfully")
            st.json(new_sdm.data)

        except Exception as e:
            st.error(f"❌ Error during save: {e}")