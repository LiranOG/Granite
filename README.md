# GRANITE 🌌
**General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

![Build Status](https://github.com/granite-nr/granite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![C++ Standard](https://img.shields.io/badge/c%2B%2B-17%2F20-purple.svg)

> **Status: 🟢 Stable Release (v0.1.0)** - The core CCZ4 spacetime evolution, GRMHD coupling, and Adaptive Mesh Refinement (AMR) systems are fully implemented and functional.

GRANITE is a high-performance, next-generation numerical relativity and General-Relativistic Magnetohydrodynamics (GRMHD) engine. Designed from the ground up to model extreme astrophysical events—such as the inspiral and merger of multiple Supermassive Black Holes (SMBHs) interacting with dense stellar environments and accretion discs—GRANITE brings state-of-the-art multi-scale physics into a cohesive, open-source framework.

## ✨ Key Features

- **Spacetime Evolution (CCZ4):** Robust conformal and covariant Z4 (CCZ4) formulation for evolving the Einstein field equations with moving-puncture gauge conditions.
- **GRMHD & Matter:** High-resolution shock-capturing (HRSC) schemes in the Valencia formulation, incorporating magnetic fields and realistic equations of state.
- **Adaptive Mesh Refinement (AMR):** Block-structured Berger-Oliger subcycling with dynamic gradient-based refinement to resolve multiple dynamic scales.
- **Multi-BH Initial Data:** Built-in solvers for Brill-Lindquist, Bowen-York, and Superposed Kerr-Schild initial conditions for arbitrarily complex N-body BH configurations.
- **Radiation & Neutrino Transport:** Hybrid Leakage + M1 closure schemes for modeling photon and neutrino emission/absorption in hot nuclear matter.
- **Diagnostics & Apparent Horizons:** Built-in flow-method Apparent Horizon finder, Newman-Penrose (Ψ₄) gravitational wave extraction, and recoil velocity estimation.
- **HDF5 I/O:** Fully parallel MPI-IO utilizing HDF5 for grid snapshots, checkpoints, and time-series data.

## 🚀 Quick Start Guide

We provide a unified execution script, `run_granite.py`, to abstract the complexities of CMake and execution.

### Prerequisites
Ensure the following dependencies are installed on your system:
- **C++ Compiler:** GCC 12+ or Clang 15+ (C++17/20 support required)
- **CMake:** 3.20 or newer
- **HDF5:** Development libraries with parallel/MPI support
- **YAML-CPP:** For configuration parsing
- **MPI & OpenMP:** For parallel execution
- **Python:** 3.8+ (for analysis and the unified runner)

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/granite-nr/granite.git
   cd granite
   ```

2. **Build the framework:**
   Use the unified runner to configure and compile the project automatically.
   ```bash
   python run_granite.py build
   ```

3. **Run a benchmark simulation:**
   Launch the `single_puncture` benchmark (runs the compiled executable with the corresponding YAML configuration).
   ```bash
   python run_granite.py run --benchmark single_puncture
   ```

   To demonstrate the full multi-physics engine, run the flagship scenario (5 supermassive black holes + 2 stars):
   ```bash
   python run_granite.py run --benchmark B5_star
   ```

4. **Clean build artifacts:**
   ```bash
   python run_granite.py clean
   ```

## 📁 Repository Structure

```text
granite/
├── benchmarks/        # YAML configuration files for standard test cases
├── containers/        # Docker and Singularity recipes
├── docs/              # Sphinx documentation (Theory & User Guide)
├── include/granite/   # C++ Public Headers
│   ├── amr/           # Adaptive Mesh Refinement logic
│   ├── core/          # Types, grid data structures, and constants
│   ├── grmhd/         # Magnetohydrodynamics kernels
│   ├── horizon/       # Apparent horizon finder
│   ├── initial_data/  # Brill-Lindquist, Bowen-York, TOV setters
│   ├── io/            # HDF5 output writers and readers
│   ├── neutrino/      # Leakage + M1 neutrino schemes
│   ├── postprocess/   # GW extraction and recoil properties
│   ├── radiation/     # M1 photon transport
│   └── spacetime/     # CCZ4 RHS evolution equations
├── python/            # Post-processing Python package (granite_analysis)
├── src/               # C++ Source Files (implementation of headers)
├── tests/             # GoogleTest unit and integration tests
├── .clang-format      # Code formatting rules
├── CMakeLists.txt     # Build configuration
├── run_granite.py     # Unified execution wrapper
└── README.md          # This file
```

## 🤝 Contributing
We welcome contributions from the scientific and open-source communities! Please check our `CONTRIBUTING.md` and adhere to the `CODE_OF_CONDUCT.md`. 
To automatically format your C++ contributions to our guidelines, run:
```bash
python run_granite.py format
```

## 📜 License
GRANITE is released under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See the `LICENSE` file for details.
