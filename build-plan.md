
---

## 📄 `build-plan.md`

```markdown
# Build Plan – Interence OS v1.5 MVP

This file describes the implementation plan and file-by-file roadmap for the Interence OS MVP repository (`i-core/`).

---

## 🧱 Folder Structure

i-core/
  README.md
  build-plan.md
  requirements.txt
  Dockerfile
  main.py

  library/
    domains/
      urban_permitting/
        denpasar_v1/
          actors.json
          failures.json
          feedback_loops.json
          jurisdiction_profile.json
          mod-001.json
          override.json
          reform_variants.json
          symbolic_scaffolds.json

  src/
    __init__.py
    memory/
      __init__.py
      polaris_memory.py
    compose/
      __init__.py
      composition_engine.py
    simulate/
      __init__.py
      simulation_engine.py
    suggest/
      __init__.py
      suggestion_engine.py
    interpret/
      __init__.py
      interpreter.py
    interface/
      __init__.py
      cli.py
    tools/
      __init__.py
      report_generator.py

  tests/
    __init__.py
    test_memory.py
    test_composition.py
    test_simulation.py
    test_suggestion.py
    test_interpretation.py
    test_interface.py

---

## 🧩 Phase-by-Phase Subsystem Plan

### Phase 2: `memory/` – Polaris Memory Engine
- Load all JSON data as SDMOs (actors, modules, reforms, etc.)
- Provide `get_by_id()`, `query_by_tag()`, etc.
- Version and provenance fields in memory objects

### Phase 3: `compose/` – Composition Engine
- Assemble process graphs from modules
- Validate with composition rules (start/end nodes, dependencies)
- Integrate grammar rules from Samaris

### Phase 4: `simulate/` – Simulation Engine
- Traverse DAGs with parallel branches
- Simulate stochastic durations, overrides, failures
- Monte Carlo aggregation

### Phase 5: `suggest/` – Suggestion Engine
- Match bottlenecks or failures to known reform variants
- Suggest and apply transformations to process graphs

### Phase 6: `interpret/` – Samaris Interpreter
- Normalize terms (e.g. “AMDAL” → Environmental Assessment)
- Validate semantic integrity across modules
- Optional: integrate LLM or rule-based classification

### Phase 7: `interface/` – CLI/Workflow Loop
- Build CLI commands: `compose`, `simulate`, `suggest`, `save`
- Possibly preview results or timelines
- Minimal UI wrappers (optionally Streamlit later)

### Phase 8: `tools/` – Export Kit
- Report generator: markdown, PDF, CSV
- Export timelines, scenario stats, and reform histories

---

## 🔁 Integration Tasks

- Memory → Simulation → Suggestion → Adaptation
- Versioning every saved composition or scenario
- Later: compare versions and detect drift

---

## ✅ Output Format

- Every subsystem produces a working `.py` file
- Tests live in `/tests` for each module
- Simulation pipeline: `main.py` → memory → compose → simulate → suggest → export

---

