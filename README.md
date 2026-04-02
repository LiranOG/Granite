# GRANITE 🌌
**General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

![Build Status](https://github.com/LiranOG/Granite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![C++ Standard](https://img.shields.io/badge/c%2B%2B-17%2F20-purple.svg)

> **Status: 🟢 Stable Core (v0.5.0)** — CCZ4 spacetime evolution, full GR-MHD with HLLE/HLLD solvers, MP5/PPM reconstruction, Constrained Transport, Tabulated Nuclear EOS, and GW analysis tools are fully implemented and tested (90 tests / 100% pass rate).

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

Choose your environment below and run the commands in order to get GRANITE running.

### Step 1 — Clone the Repository
```bash
git clone https://github.com/LiranOG/Granite.git
cd Granite
```

### Step 2 — Install Dependencies & Build

#### 🪟 Windows — WSL2 (Ubuntu) ⭐ Recommended
*Use for: WSL2 terminal inside Windows*
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

#### 🐍 Windows — Miniforge / Conda
*Use for: Miniforge Prompt, Anaconda Prompt*
> Requires Visual Studio Build Tools 2022 ("Desktop development with C++" workload) installed separately.
```bash
conda install -c conda-forge cmake hdf5 openmpi yaml-cpp
python scripts/run_granite.py build
```

#### 🪟 Windows — PowerShell / CMD / VS Code / Node.js
*Use for: Any native Windows terminal — requires CMake + VS Build Tools installed manually (see INSTALL.md)*
```powershell
python scripts/run_granite.py build
```

#### 🐧 Linux — Ubuntu / Debian
*Use for: Ubuntu, Debian, any apt-based distro*
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

#### 🐧 Linux — Fedora / RHEL / Rocky
*Use for: dnf-based distros*
```bash
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y cmake hdf5-devel openmpi-devel yaml-cpp-devel
module load mpi/openmpi-x86_64
python3 scripts/run_granite.py build
```

#### 🍎 macOS — Homebrew
*Use for: macOS Terminal, iTerm2*
```bash
brew install cmake hdf5 open-mpi yaml-cpp
python3 scripts/run_granite.py build
```

### Step 3 — Run the Unit Tests
```bash
# Option A — run directly from the project root (recommended)
build/bin/granite_tests

# Option B — run via CTest
# ⚠️  WARNING: This changes your working directory into build/!
cd build && ctest --output-on-failure
cd ..   # ← IMPORTANT: return to project root before Step 5!
```
Expected output: `[  PASSED  ] 90 tests.` (90 tests from 16 test suites)

### Step 4 — Run the Developer Benchmark (Recommended)

The `scripts/dev_benchmark.py` script runs the `single_puncture` benchmark with **real-time physics diagnostics** — lapse monitoring, Hamiltonian constraint tracking, NaN forensics, and advection CFL monitoring. It is the primary tool for verifying that the engine is working correctly after a fresh build.

> **Make sure you are in the project root directory** before running.

```bash
# Standard run (10-step summary every 0.625M)
python3 scripts/dev_benchmark.py

# Verbose mode — step-by-step NaN detection + propagation tracking
python3 scripts/dev_benchmark.py --verbose
```

```bash
# Stability run
python3 dev_stability_test.py --t-target 50
```

### Step 5 — Run a Simulation
```bash
# Basic benchmark run
python3 scripts/run_granite.py run --benchmark single_puncture

# Flagship: 5 SMBHs + 2 stars [Not Released]
python3 scripts/run_granite.py run --benchmark B5_star
```
> **Windows (PowerShell/CMD/Conda):** use `python` instead of `python3`.


**What healthy output looks like:**
```
  step=80  t=5.0000M  α_center=0.029 [RECOVER]  ‖H‖₂=0.153 [OK]
  Phase: Lapse recovering — trumpet stable ✓
  Advection CFL: 0.938 ✓ stable
```
- `α_center` should drop from 1 → ~0.003 (lapse collapse) then recover to ~0.03 (trumpet formation) ✓  
- `‖H‖₂ < 1.0` through `t = 6M` means the constraints are satisfied ✓  
- NaN Forensics section should show "No NaN events detected" for a healthy build ✓

Logs are automatically saved to `dev_logs/dev_benchmark_<timestamp>.log`.

---

> [!IMPORTANT]
> **Need more details?** For complete A-to-Z setup guides per terminal, all dependencies explained, and a full **Q&A / Troubleshooting** section covering every possible error, see [**INSTALL.md**](./docs/INSTALL.md).

## 📁 Repository Structure

```text
Granite/
├── benchmarks/          # YAML parameter files for standard test cases
│   └── single_puncture/ # Single moving-puncture BH benchmark
├── containers/          # Docker & Singularity recipes for HPC clusters
├── dev_logs/            # Auto-generated benchmark logs (git-ignored)
├── docs/                # Sphinx documentation, user guides, internal notes
├── include/granite/     # C++ Public Headers
│   ├── core/            # Types, GridBlock data structures, constants
│   ├── grmhd/           # GRMHD kernels (HLLE/HLLD, EOS, CT)
│   ├── horizon/         # Apparent horizon finder
│   ├── initial_data/    # Brill-Lindquist, Bowen-York, TOV setters
│   ├── io/              # HDF5 output writers and readers
│   ├── neutrino/        # Leakage + M1 neutrino schemes
│   ├── postprocess/     # GW extraction (Ψ₄) and recoil estimation
│   ├── radiation/       # M1 photon transport
│   └── spacetime/       # CCZ4 RHS evolution equations
├── python/              # granite_analysis Python post-processing package
├── scripts/             # Python wrapper scripts
│   ├── run_granite.py   # Unified build/run/format wrapper
│   └── dev_benchmark.py # ⭐ Developer diagnostic benchmark (see above)
├── src/                 # C++ source implementations
└── tests/               # 90 GoogleTest unit & integration tests
```

## 📋 Versioning Policy (Pre-1.0.0)

> [!IMPORTANT]
> **Until the official `v1.0.0` full release, all version history, phase documentation, and change logs are tracked exclusively inside [`CHANGELOG.md`](./CHANGELOG.md)** — not through GitHub Releases or GitHub's release notes UI.
>
> This is an intentional decision to keep the complete engineering audit trail (Phases 0–5 and beyond) in a single, richly-documented source of truth that lives alongside the code.
>
> **What this means for contributors and users:**
> - The `CHANGELOG.md` file is the canonical record of every bug fix, new feature, architectural decision, and test count milestone.
> - GitHub Tags (e.g. `v0.5.0`) mark stable integration points but carry minimal release notes — refer to `CHANGELOG.md` for the full picture.
> - GitHub Releases will be created officially at `v1.0.0` — the first production-ready, fully-coherent version of the engine.

---

## 🤝 Contributing
We welcome contributions from the scientific and open-source communities! Please check our `.github/CONTRIBUTING.md` and adhere to the `.github/CODE_OF_CONDUCT.md`. 
To automatically format your C++ contributions to our guidelines, run:
```bash
python scripts/run_granite.py format
```

## 📜 License
GRANITE is released under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See the `LICENSE` file for details.
