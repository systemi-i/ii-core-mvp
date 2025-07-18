import sys
from pathlib import Path

# ✅ Add src/ to Python path BEFORE any local imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# Now safe to import
from pyvis.network import Network
from memory.polaris_memory import PolarisMemory
from compose.graphviz_export import export_graph

# Add src/ to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# -- Export interactive HTML visualization --
def export_interactive_dag(edges, module_ids, memory, output_path="dag_interactive.html"):
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

    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "multi": "md"
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": false
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -10000,
          "centralGravity": 0.2,
          "springLength": 100,
          "springConstant": 0.04,
          "damping": 0.09,
          "avoidOverlap": 0.5
        }
      }
    }
    """)
    net.show(str(output_path), notebook=False)
    print(f"✅ Interactive HTML DAG exported to: {output_path}")

# -- Load memory --
memory = PolarisMemory(Path("library/domains/urban_permitting/denpasar_v1"))

# -- List compositions --
print("\n📦 Available compositions:")
compositions = memory.get_by_type("Composition")
for obj in compositions:
    print(" -", obj.id)

# -- Load composition --
composition_id = "composition-denpasar-denpasar_bess_permitting_flow"
composition = memory.get_by_id(composition_id)

if composition is None:
    raise ValueError(f"❌ Composition {composition_id} not found in memory.")

# -- Access nested data --
print(f"✅ DEBUG: Composition keys: {composition.data.keys()}")
inner = composition.data.get("data", {})

if "modules" not in inner or "edges" not in inner:
    raise ValueError(
        f"❌ Composition {composition.id} missing 'modules' or 'edges'. Available inner keys: {inner.keys()}"
    )

modules = inner["modules"]
edges = inner["edges"]

# -- Print summary --
print(f"📌 Title: {inner.get('title')}")
print(f"🏛️ Jurisdiction: {composition.jurisdiction}")
print(f"🧱 Modules: {modules}")
print(f"🔗 Edges: {edges[:5]}")

# -- Export static PNG DAG --
export_graph(
    edges=edges,
    module_ids=modules,
    memory=memory,
    output_path=Path("dag_output.png")
)
print("✅ Static PNG DAG exported to: dag_output.png")

# -- Export interactive DAG --
output_dir = Path("visuals")
output_dir.mkdir(exist_ok=True)

export_interactive_dag(
    edges=edges,
    module_ids=modules,
    memory=memory,
    output_path=output_dir / "dag_interactive.html"
)
