import streamlit as st

def render_diagnostics_panel(results: dict):
    st.subheader("🧪 Diagnostics Result")

    if results["has_cycle"]:
        st.error("❌ Composition graph contains cycles.")
    else:
        st.success("✅ No cycles found.")

    if results["disconnected"]:
        st.warning(f"⚠️ Disconnected nodes: {len(results['disconnected'])}")
        st.code("\n".join(results["disconnected"]))
    else:
        st.success("✅ All modules connected.")

    if results["orphan_non_optional"]:
        st.error("❌ Disconnected non-optional modules:")
        st.code("\n".join(results["orphan_non_optional"]))
    else:
        st.success("✅ All disconnected modules are optional or none exist.")

    if results["feedback_loops"]:
        st.warning(f"⚠️ Feedback loops present: {len(results['feedback_loops'])}")
        st.code("\n".join(results["feedback_loops"]))
    else:
        st.info("ℹ️ No feedback loops detected (or none defined).")
