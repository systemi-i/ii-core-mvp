# Interence OS v1.5 – Governance Process Simulator (MVP)

**Interence OS** is a modular, five-layer institutional intelligence system designed to simulate, adapt, and reform governance processes. It enables users to model complex regulatory workflows, identify bottlenecks via simulation, and test reform interventions. The MVP (v1.5) focuses on a real-world permitting process in Denpasar, Indonesia for battery energy storage systems (BESS).

---

## 🧱 Architecture Overview

The system is structured into five core layers:

1. **Interface Layer**  
   A command-line or minimal GUI to let users load, simulate, and visualize governance process flows.

2. **Composition Layer**  
   Users build governance processes from modular components (Permitting Modules). Validates structural logic and composition grammar.

3. **Simulation Layer**  
   A Monte Carlo engine runs the process DAG under uncertainty. Supports parallel tasks, overrides, and feedback loops.

4. **Grammar / Interpretation Layer (Samaris)**  
   Interprets user and system input, enforces semantic consistency, and helps guide composition or suggest improvements.

5. **Memory Layer (Polaris)**  
   A persistent, structured store of all Self-Describing Memory Objects (SDMOs), such as actors, modules, reform variants, and simulation results.

---

## ⚡ Denpasar Use Case (Pilot)

The MVP simulates the Denpasar permitting workflow for BESS installations, with:
- Multi-agency sequencing (spatial zoning, AMDAL, grid connection)
- Feedback loops (e.g. iterative reviews)
- Symbolic friction (e.g. informal village veto)
- Reform options (e.g. default approval after 120 days, parallelizing steps)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 (must not use 3.13+)
- pip

### Setup

```bash
cd i-core/
python -m venv .venv
.\.venv\Scripts\activate      # Windows
# or source .venv/bin/activate (Mac/Linux)

pip install -r requirements.txt