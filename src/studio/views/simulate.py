# src/studio/views/simulate.py

import streamlit as st
import streamlit.components.v1 as components
from memory.polaris_memory import PolarisMemory
from simulate.simulation_engine import run_simulation
from memory.models import MemoryObject
from pathlib import Path
import json
import matplotlib.pyplot as plt


def format_edges_for_nx(edge_dicts):
    """
    Convert dict-style edges into NetworkX-compatible (from, to, attrs) tuples.
    """
    return [
        (e["from_node"], e["to_node"], {k: v for k, v in e.items() if k not in ("from_node", "to_node")})
        for e in edge_dicts if isinstance(e, dict)
    ]


def render_simulate_view(memory: PolarisMemory):
    st.title("🧠 Simulate Governance Flow")

    compositions = memory.get_by_type("Composition")
    if not compositions:
        st.error("No compositions found in memory.")
        return

    composition_labels = [
        f"{c.data.get('title', '[Untitled]')} ({c.id})" for c in compositions
    ]
    selected_index = st.selectbox(
        "Select a Composition",
        range(len(compositions)),
        format_func=lambda i: composition_labels[i]
    )
    selected_comp = compositions[selected_index]
    st.success(f"✅ Selected: {composition_labels[selected_index]}")

    # Governance Layers
    layers = selected_comp.data.get("data", {})
    symbolic = layers.get("symbolic_scaffolds", [])
    overrides = layers.get("override_protocols", [])
    feedbacks = layers.get("feedback_loops", [])
    failures = layers.get("failure_events", [])

    with st.expander("🧠 Attached Governance Layers"):
        st.markdown(f"🔮 **Symbolic Scaffolds:** {len(symbolic)} → `{symbolic}`")
        st.markdown(f"🚨 **Overrides:** {len(overrides)} → `{overrides}`")
        st.markdown(f"🔁 **Feedback Loops:** {len(feedbacks)} → `{feedbacks}`")
        st.markdown(f"⚠️ **Failure Events:** {len(failures)} → `{failures}`")

    # Parameters
    st.markdown("### ⚙️ Simulation Parameters")
    min_dur = st.number_input("Min Task Duration (days)", value=5, min_value=1)
    max_dur = st.number_input("Max Task Duration (days)", value=20, min_value=min_dur)
    failure_rate = st.slider("Failure Rate (%)", 0, 100, 10)
    max_loops = st.number_input("Max Feedback Loops", value=2, min_value=0)
    override_days = st.number_input("Override Threshold (days)", value=45, min_value=0)
    num_iterations = st.slider("Monte Carlo Iterations", 10, 2000, 1000, step=10)

    params = {
        "task_duration_range": (min_dur, max_dur),
        "failure_rate": failure_rate / 100,
        "max_feedback_loops": max_loops,
        "override_days": override_days
    }

    if st.button("▶️ Run Simulation"):
        try:
            modules = selected_comp.data.get("data", {}).get("modules", [])
            edges = selected_comp.data.get("data", {}).get("edges", [])
            if not modules or not edges:
                st.error("❌ This composition is missing modules or edges.")
                return
        except Exception as e:
            st.error(f"❌ Invalid composition format: {e}")
            return

        for mid in modules:
            obj = memory.get_by_id(mid)
            if obj is None:
                st.error(f"❌ Missing module in memory: {mid}")
            else:
                st.success(f"✅ Found: {mid} ({obj.object_type})")

        formatted_edges = format_edges_for_nx(edges)

        with st.spinner("⏳ Running Monte Carlo simulation..."):
            try:
                # ✅ Pass formatted_edges explicitly and inject into composition

                result = run_simulation(
                    composition=selected_comp,
                    memory=memory,
                    params=params,
                    runs=num_iterations,
                    formatted_edges=formatted_edges,
                )
            except Exception as e:
                st.error(f"❌ Simulation error: {e}")
                return

        st.success("✅ Simulation Complete")
        st.metric("Average Completion Time (days)", f"{result['avg_duration']:.2f}")
        st.markdown("### Module Failure Frequencies")
        st.json(result["failures"])

        st.markdown("### 📊 Failure Frequency Chart")
        if result["failures"]:
            modules = list(result["failures"].keys())
            counts = list(result["failures"].values())
            fig, ax = plt.subplots()
            ax.bar(modules, counts, color="#F08080")
            ax.set_ylabel("Failure Count")
            ax.set_xlabel("Module ID")
            ax.set_title("Failure Frequency by Module")
            plt.xticks(rotation=90)
            st.pyplot(fig)

        st.markdown("### 💾 Export Results")
        if st.checkbox("📤 Save results to JSON"):
            export_data = {
                "composition_id": selected_comp.id,
                "parameters": params,
                "iterations": num_iterations,
                "avg_duration": result["avg_duration"],
                "failures": result["failures"]
            }
            export_path = Path("export") / f"simulation_{selected_comp.id}.json"
            export_path.parent.mkdir(exist_ok=True)
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
            st.success(f"📁 Results exported to: `{export_path}`")