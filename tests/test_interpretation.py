# tests/test_interpretation.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import json
from memory.polaris_memory import PolarisMemory
from memory.models import MemoryObject
from interpret.flow_grammar import interpret_flow


def load_test_composition(path: Path) -> MemoryObject:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return MemoryObject(**raw)


def test_interpret_flow_denpasar():
    # Set up memory from the domain folder
    memory_path = Path("library/domains/urban_permitting/denpasar_v1/")
    memory = PolarisMemory(memory_path)

    # Load Denpasar test composition
    composition_path = memory_path / "composition-denpasar-denpasar_bess_permitting_flow.json"
    composition = load_test_composition(composition_path)

    # Run interpretation
    result = interpret_flow(composition, memory)

    # Print summary
    print("\n🧠 Interpretation Summary:")
    print(json.dumps(result["summary"], indent=2))
    print("\n🏷️ Tags:")
    for mod, tags in result["tags"].items():
        print(f"{mod}: {tags}")
    if result["errors"]:
        print("\n❌ Errors:")
        print(result["errors"])
    if result["warnings"]:
        print("\n⚠️ Warnings:")
        print(result["warnings"])

    # Basic test conditions
    assert isinstance(result, dict)
    assert "valid" in result
    assert "summary" in result
    assert "tags" in result
    assert result["summary"]["module_count"] > 0
