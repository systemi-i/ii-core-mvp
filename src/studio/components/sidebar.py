import streamlit as st

def render_composition_selector(memory):
    compositions = memory.get_by_type("Composition")
    if not compositions:
        st.warning("No compositions found.")
        return None

    composition_ids = [c.id for c in compositions]
    selected_id = st.selectbox("📄 Select a composition", composition_ids)
    return memory.get_by_id(selected_id)
