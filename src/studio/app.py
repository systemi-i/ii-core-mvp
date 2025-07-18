# studio/app.py

import streamlit as st
from views.explore import render_explore_view
from views.diagnose import render_diagnose_view
from views.compose import render_compose_view
from views.simulate import render_simulate_view  # ✅ Added missing import
from utils.memory_adapter import load_memory

# ─────────────────────────────────────────────────────────────
# App Config & Title
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Interence Studio", layout="wide")

st.title("🧠 Interence Studio")
st.markdown("A governance intelligence interface for exploring compositions and memory objects.")

# ─────────────────────────────────────────────────────────────
# Load Memory
# ─────────────────────────────────────────────────────────────
memory = load_memory()

if st.sidebar.checkbox("🛠 Show Debug Info"):
    st.code(f"📁 MEMORY PATH → {memory.memory_path}")
    st.write("🧠 Total loaded objects:", len(memory.objects))

# ─────────────────────────────────────────────────────────────
# Mode Routing
# ─────────────────────────────────────────────────────────────
mode = st.sidebar.radio("🧭 Select Mode", ["Explore", "Diagnose", "Compose", "Simulate"])

if mode == "Explore":
    render_explore_view(memory)
elif mode == "Diagnose":
    render_diagnose_view(memory)
elif mode == "Compose":
    render_compose_view(memory)
elif mode == "Simulate":
    render_simulate_view(memory)  # ✅ Now properly recognized
else:
    st.info("More modes coming soon.")
