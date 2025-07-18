# [top unchanged imports...]
import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
from textwrap import shorten
from copy import deepcopy

# ...
from memory.polaris_memory import PolarisMemory
from compose.composition_engine import CompositionEngine
from compose.graphviz_export import export_graph
from compose.interactive_export import export_interactive_dag
import networkx as nx

print("✅ Running main.py from:", __file__)

MEMORY_PATH = (Path.cwd().parent / "library" / "domains" / "urban_permitting" / "denpasar_v1").resolve()

# ----- Utility Helpers -----

def normalize(text: str) -> str:
    return re.sub(r"[-_]", "", text.lower())

def resolve_composition_id(memory: PolarisMemory, partial_id: str) -> str:
    def score(candidate: str, query: str) -> int:
        return sum(1 for c in query if c in candidate)

    norm_partial = normalize(partial_id)
    candidates = memory.get_by_type("Composition")

    scored = [
        (obj.id, score(normalize(obj.id), norm_partial))
        for obj in candidates
    ]
    scored = [s for s in scored if s[1] > 0]
    scored.sort(key=lambda x: -x[1])

    if not scored:
        print(f"❌ No match found for '{partial_id}'")
        return None
    elif len(scored) > 1 and scored[0][1] == scored[1][1]:
        print(f"⚠️ Multiple high-similarity matches for '{partial_id}':")
        for sid, _ in scored[:5]:
            print(f" - {sid}")
        return None

    return scored[0][0]

# ----- Core Commands -----

def preview_composition(composition_id: str):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, composition_id)
    if not resolved_id: return
    obj = memory.get_by_id(resolved_id)
    data = obj.data.get("data", obj.data)
    print(f"\n📄 Composition ID: {obj.id}")
    print(f"🗺️ Jurisdiction: {obj.jurisdiction}")
    print(f"🏗️ Title: {data.get('title', '(untitled)')}")
    print(f"👤 Created by: {obj.created_by or '(unknown)'}")
    print(f"📆 Created on: {obj.created_on.strftime('%Y-%m-%d %H:%M')}")
    print(f"🧱 Modules: {len(data.get('modules', []))}")
    print(f"🔗 Edges: {len(data.get('edges', []))}")

def list_compositions(memory: PolarisMemory):
    compositions = memory.get_by_type("Composition")
    if not compositions:
        print("⚠️ No compositions found.")
        return
    print("\n📦 Available Compositions:\n")
    for comp in compositions:
        title = comp.data.get("title") or comp.data.get("data", {}).get("title") or "(untitled)"
        created = comp.created_on.strftime("%Y-%m-%d")
        display_id = shorten(comp.id, width=50, placeholder="…")
        print(f"🧾 {display_id}")
        print(f"    ├─ Title: {title}")
        print(f"    ├─ Created by: {comp.created_by or '(unknown)'} on {created}")
        print(f"    └─ Jurisdiction: {comp.jurisdiction}\n")

def compose_jurisdiction(jurisdiction: str, title: str = None, created_by: str = "CLI"):
    memory = PolarisMemory(MEMORY_PATH)
    engine = CompositionEngine(memory)

    if not title:
        title = f"{jurisdiction} Permitting Flow"

    temporal_path = MEMORY_PATH / "temporal_constraints.json"
    print("🧭 DEBUG path exists:", temporal_path.exists())
    print("🧭 DEBUG full path:", temporal_path)

    if not temporal_path.exists():
        print(f"⚠️ Warning: No temporal_constraints.json found at {temporal_path}.")
        return

    composition = engine.compose(
        jurisdiction=jurisdiction,
        temporal_path=str(temporal_path),
        title=title,
        created_by=created_by
    )

    memory.save_object(composition)
    memory.save_all()
    print(f"\n✅ Composition '{composition.id}' created and saved.")

def visualize(composition_id: str, html: bool = False):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, composition_id)
    if not resolved_id: return
    composition = memory.get_by_id(resolved_id)
    inner = composition.data.get("data", composition.data)
    modules = inner.get("modules", [])
    edges = inner.get("edges", [])
    if not modules or not edges:
        print("❌ Composition missing modules or edges.")
        return
    export_graph(edges, modules, Path("dag_output.png"), memory)
    if html:
        export_interactive_dag(edges, modules, memory, Path("visuals") / f"{resolved_id}.html")

def export_composition(composition_id: str, export_dir: str = None):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, composition_id)
    if not resolved_id: return
    path = Path(export_dir) if export_dir else None
    export_path = memory.save_all(export_dir=path, only_type="Composition")
    print(f"\n✅ Exported to: {export_path}")

def diagnose_composition(composition_id: str):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, composition_id)
    if not resolved_id: return
    obj = memory.get_by_id(resolved_id)
    data = obj.data.get("data", obj.data)
    modules = data.get("modules", [])
    edges = data.get("edges", [])
    G = nx.DiGraph()
    G.add_nodes_from(modules)
    G.add_edges_from(edges)
    print(f"\n🧠 Running diagnostics for: {resolved_id}")
    if not nx.is_directed_acyclic_graph(G):
        print("❌ Graph contains a cycle.")
    else:
        print("✅ Graph is acyclic.")
    disconnected = list(nx.isolates(G))
    if disconnected:
        print(f"⚠️ Disconnected nodes: {disconnected}")
    else:
        print("✅ All nodes are connected.")
    print(f"🧱 Nodes: {len(modules)} | 🔗 Edges: {len(edges)}")

def tag_object(object_id: str, tag: str):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, object_id)
    if not resolved_id: return
    obj = memory.get_by_id(resolved_id)
    obj.add_tag(tag)
    memory.save_object(obj)
    print(f"🏷️ Tag '{tag}' added to '{obj.id}'")

def delete_object(object_id: str):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, object_id)
    if not resolved_id: return
    if resolved_id in memory.objects:
        del memory.objects[resolved_id]
        print(f"🗑️ Deleted '{resolved_id}' from memory.")
    else:
        print(f"❌ Object '{resolved_id}' not found.")

def clone_object(object_id: str):
    memory = PolarisMemory(MEMORY_PATH)
    resolved_id = resolve_composition_id(memory, object_id)
    if not resolved_id: return
    obj = memory.get_by_id(resolved_id)
    clone = obj.clone_with_new_id(deepcopy(obj.data), created_by="CLI:clone")
    memory.save_object(clone)
    print(f"📦 Cloned '{resolved_id}' → '{clone.id}'")

def launch_ui():
    print("🌐 Launching Interence Studio (coming soon...)")
    print("📦 Try: streamlit run studio/app.py")

# ----- CLI Entry -----

def main():
    parser = argparse.ArgumentParser(description="Interence OS CLI Interface")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list-compositions", help="List all stored compositions")
    compose_parser = subparsers.add_parser("compose")
    compose_parser.add_argument("jurisdiction")
    compose_parser.add_argument("--title")
    compose_parser.add_argument("--created_by", default="CLI")

    vis_parser = subparsers.add_parser("visualize")
    vis_parser.add_argument("composition_id")
    vis_parser.add_argument("--html", action="store_true")

    exp_parser = subparsers.add_parser("export")
    exp_parser.add_argument("composition_id")
    exp_parser.add_argument("--dir")

    prev_parser = subparsers.add_parser("preview")
    prev_parser.add_argument("composition_id")

    diag_parser = subparsers.add_parser("diagnose")
    diag_parser.add_argument("composition_id")

    tag_parser = subparsers.add_parser("tag")
    tag_parser.add_argument("object_id")
    tag_parser.add_argument("tag")

    del_parser = subparsers.add_parser("delete")
    del_parser.add_argument("object_id")

    clone_parser = subparsers.add_parser("clone")
    clone_parser.add_argument("object_id")

    subparsers.add_parser("launch-ui")

    args = parser.parse_args()

    if args.command == "list-compositions":
        memory = PolarisMemory(MEMORY_PATH)
        list_compositions(memory)
    elif args.command == "compose":
        compose_jurisdiction(args.jurisdiction, args.title, args.created_by)
    elif args.command == "visualize":
        visualize(args.composition_id, html=args.html)
    elif args.command == "export":
        export_composition(args.composition_id, args.dir)
    elif args.command == "preview":
        preview_composition(args.composition_id)
    elif args.command == "diagnose":
        diagnose_composition(args.composition_id)
    elif args.command == "tag":
        tag_object(args.object_id, args.tag)
    elif args.command == "delete":
        delete_object(args.object_id)
    elif args.command == "clone":
        clone_object(args.object_id)
    elif args.command == "launch-ui":
        launch_ui()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
