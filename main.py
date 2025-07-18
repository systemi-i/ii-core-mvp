# Add src/ to path so we can import memory.*, studio.*, etc.
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

# Now it's safe to import modules inside src/
import streamlit as st
from memory.polaris_memory import PolarisMemory

# ─────────────────────────────────────────────────────────────
# App Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Interence Studio", layout="wide")
st.title("🧠 Interence Studio")
st.markdown("A governance intelligence interface for exploring compositions and memory objects.")

# ─────────────────────────────────────────────────────────────
# Load Memory
# ─────────────────────────────────────────────────────────────
memory_path = Path("library/domains/urban_permitting/denpasar_v1")
memory = PolarisMemory(memory_path)

if st.sidebar.checkbox("🛠 Show Debug Info"):
    st.code(f"📁 MEMORY PATH → {memory.memory_path}")
    st.write("🧠 Total loaded objects:", len(memory.objects))

# ─────────────────────────────────────────────────────────────
# Mode Routing
# ─────────────────────────────────────────────────────────────
mode = st.sidebar.radio("🧭 Select Mode", ["Explore", "Compose", "Diagnose", "Simulate"])

if mode == "Explore":
    from studio.views.explore import render_explore_view
    render_explore_view(memory)

elif mode == "Compose":
    from studio.views.compose import render_compose_view
    render_compose_view(memory)

elif mode == "Diagnose":
    from studio.views.diagnose import render_diagnose_view
    render_diagnose_view(memory)

elif mode == "Simulate":
    from studio.views.simulate import render_simulate_view
    render_simulate_view(memory)
