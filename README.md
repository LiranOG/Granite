# GRANITE 🌌
**General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

![Build Status](https://github.com/LiranOG/Granite/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![C++ Standard](https://img.shields.io/badge/c%2B%2B-17%2F20-purple.svg)

> **Status: 🟢 Universal Deployment & Tracking (v0.6.0)** — CCZ4 spacetime evolution, full GR-MHD, dynamic Berger-Oliger AMR subcycling, moving-puncture tracking, and diagnostic Python dashboards are fully integrated. 92 tests / 100% pass rate.

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

#### 💎 Windows — WSL2 / Ubuntu (Recommended ⭐)
*Use for: WSL2 terminal inside Windows*
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

#### 🪟 Windows — Native PowerShell / CMD
*Use for: Native terminal without WSL2. Requires CMake + VS Build Tools + vcpkg (see [INSTALLATION.md](./INSTALLATION.md))*
```powershell
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="../vcpkg/scripts/buildsystems/vcpkg.cmake" -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

#### 🐍 Windows — Miniforge / Conda
*Use for: Miniforge Prompt, Anaconda Prompt. Requires VS Build Tools 2022 installed separately.*
```bash
conda install -c conda-forge cmake hdf5 openmpi yaml-cpp
python scripts/run_granite.py build
```

#### 🐧 Linux — Ubuntu / Debian
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

#### 🐧 Linux — Fedora / RHEL / Rocky
```bash
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y cmake hdf5-devel openmpi-devel yaml-cpp-devel
module load mpi/openmpi-x86_64
python3 scripts/run_granite.py build
```

#### 🍎 macOS — Homebrew
```bash
brew install cmake hdf5 open-mpi yaml-cpp
python3 scripts/run_granite.py build
```

---

### Step 3 — Run the Health Check (Pre-Flight)

Verify that your binary used the correct Release optimization flags and that all CPU cores are properly allocated to OpenMP before running any simulation.

#### 🪟 Windows (PowerShell / CMD / Conda)
```powershell
python scripts/health_check.py
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
python3 scripts/health_check.py
```

---

### Step 4 — Run the Unit Tests

#### 🪟 Windows — PowerShell / CMD
```powershell
# Option A — run directly (recommended)
.\build\bin\Release\granite_tests.exe

# Option B — via CTest
cd build
ctest --output-on-failure
cd ..
```

#### 🪟 Windows — Conda / 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
# Option A — run directly from the project root (recommended)
build/bin/granite_tests

# Option B — via CTest
# ⚠️ WARNING: This changes your working directory into build/!
cd build && ctest --output-on-failure
cd ..   # ← IMPORTANT: return to project root before Step 5!
```

Expected output: `[  PASSED  ] 92 tests.` (92 tests from 16 test suites)

---

### Step 5 — Run the Developer Benchmark

The `scripts/dev_benchmark.py` script provides **real-time physics diagnostics** — lapse monitoring, Hamiltonian constraint tracking, NaN forensics, and advection CFL monitoring.

> Run this from the **project root directory** at all times.

#### 🪟 Windows (PowerShell / CMD / Conda)
```powershell
# Standard run (10-step summary every 0.625M)
python scripts/dev_benchmark.py

# Verbose mode — step-by-step NaN detection + propagation tracking
python scripts/dev_benchmark.py --verbose

# Extended stability run
python scripts/dev_stability_test.py --t-target 50
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
# Standard run (10-step summary every 0.625M)
python3 scripts/dev_benchmark.py

# Verbose mode — step-by-step NaN detection + propagation tracking
python3 scripts/dev_benchmark.py --verbose

# Extended stability run
python3 scripts/dev_stability_test.py --t-target 50
```

---

### Step 6 — Run a Full Simulation

GRANITE is driven by YAML parameter files (`params.yaml`) in the `benchmarks/` directory. Use the wrapper script to select and launch physics scenarios.

#### 🪟 Windows (PowerShell / CMD / Conda)
```powershell
# 1. Gauge Wave Validation (fast advection test)
python scripts/run_granite.py run --benchmark gauge_wave

# 2. Single Moving Puncture (standard 3D setup)
python scripts/run_granite.py run --benchmark single_puncture

# 3. Equal-Mass BBH Merger (flagship — production-grade, run health_check.py first!)
python scripts/run_granite.py run --benchmark B2_eq

# 4. Custom scenario (create benchmarks/my_sim/params.yaml first)
python scripts/run_granite.py run --benchmark my_sim
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
# 1. Gauge Wave Validation (fast advection test)
python3 scripts/run_granite.py run --benchmark gauge_wave

# 2. Single Moving Puncture (standard 3D setup)
python3 scripts/run_granite.py run --benchmark single_puncture

# 3. Equal-Mass BBH Merger (flagship — production-grade, run health_check.py first!)
python3 scripts/run_granite.py run --benchmark B2_eq

# 4. Custom scenario (create benchmarks/my_sim/params.yaml first)
python3 scripts/run_granite.py run --benchmark my_sim
```

> [!IMPORTANT]
> Before launching `B2_eq` or any long-running simulation, always run `health_check.py` first (Step 3) and review [`DEPLOYMENT_AND_PERFORMANCE.md`](./DEPLOYMENT_AND_PERFORMANCE.md) to maximize native hardware utilization.

---

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

The architectural layout of the GRANITE engine is cleanly decoupled into modular subsystems. Below is the structural overview of the physics modules, diagnostics, and deployment ecosystem.

```text
Granite/
├── benchmarks/          # Central hub for YAML physics scenarios and simulation presets.
│   ├── B2_eq/           # Equal-mass (M=1.0) Binary Black Hole merger geometry configuration.
│   ├── gauge_wave/      # 1D sinusoidal gauge validation for CCZ4 advection consistency.
│   └── single_puncture/ # Standard 3D moving-puncture BH stability benchmark.
├── CMakeLists.txt       # Master build configuration. Orchestrates MSVC/GCC, vcpkg, and MPI linkage.
├── docs/                # Core documentation, engineering installation guides, and internal notes.
├── include/granite/     # Public C++ interface headers defining the numerical abstractions.
│   ├── amr/             # Adaptive mesh structures, tracking spheres, and Berger-Oliger interfaces.
│   ├── core/            # Low-level primitives, dimension traits, and `GridBlock` memory boundaries.
│   ├── grmhd/           # General Relativistic Magnetohydrodynamics routines and EOS lookup tables.
│   ├── initial_data/    # Analytic metric setters for Brill-Lindquist and Bowen-York geometries.
│   ├── io/              # MPI-aware HDF5 parallel data streamers and exact-state checkpoint managers.
│   ├── postprocess/     # Gravitational wave (Ψ₄) spherical harmonic extraction and EM estimates.
│   └── spacetime/       # Conformal and Covariant Z4 (CCZ4) evolution equations and constraints.
├── scripts/             # Python-based diagnostic suite, health telemetry, and CI/CD wrappers.
│   ├── dev_benchmark.py # Real-time forensic stability monitor for Hamiltonian constraints and NaNs.
│   ├── health_check.py  # Pre-flight hardware validation ensuring maximum OpenMP core saturation.
│   └── run_granite.py   # Unified cross-platform CLI tool for building, testing, and running sims.
├── setup_windows.ps1    # Automated Bootstrap tool deploying vcpkg, MS-MPI, and CMake on Windows.
├── src/                 # High-performance C++ implementation algorithms and physics kernels.
│   ├── amr/             # Implements spatial restriction, 4th-order prolongation, and regridding.
│   ├── spacetime/       # Highly parallelized CCZ4 right-hand-side loops computing Ricci sensors.
│   └── main.cpp         # Main execution loop managing AMR hierarchies, I/O burst intervals, and RK3.
└── tests/               # 92 integrated GoogleTest suite verifying physics accuracy and advection stability.
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

## 📝 A Personal Note from the Creator

> As the sole creator and developer of this project, I have built every single component of this repository from the ground up. Being a solo developer—regardless of professional expertise—makes it incredibly challenging to track and document every minor change. I do my absolute best to maintain the highest possible standard of documentation, but writing documentation is a full-time job in itself. When you are single-handedly programming, building, engineering, and documenting a physics engine of this magnitude, it's natural that occasional minor updates might slip through the cracks.
> 
> I warmly welcome and encourage constructive criticism from anyone and everyone—that is a core part of this project's purpose. However, I ask that you don't solely look for flaws. If you search for flaws in *any* codebase, you will always find them, but they pale in comparison to everything that works beautifully here. If your only goal is to find shortcomings, doubt the capabilities of a solo developer, or spread negativity—then this repository is simply not the place for you. 
> 
> But to everyone who takes the time to look through the project, test it,
> and offer genuine feedback (whether positive or critical):
> 
> **Thank you.** Your input is deeply appreciated and warmly welcomed.

---
## 🤝 Contributing
We welcome contributions from the scientific and open-source communities! Please check our `.github/CONTRIBUTING.md` and adhere to the `.github/CODE_OF_CONDUCT.md`. 
To automatically format your C++ contributions to our guidelines, run:
```bash
python scripts/run_granite.py format
```

## 📜 License
GRANITE is released under the GNU General Public License v3.0 or later (GPL-3.0-or-later). See the `LICENSE` file for details.
