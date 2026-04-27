<div align="center">

# GRANITE 🌌
### **General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

[![Build Status](https://github.com/LiranOG/Granite/actions/workflows/ci.yml/badge.svg)](https://github.com/LiranOG/Granite/actions) 
[![Development Status](https://img.shields.io/badge/Status-Active%20Development-2d3436.svg)](https://github.com/LiranOG/Granite/pulse)

[![ORCID](https://img.shields.io/badge/ORCID-Profile-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0008-8035-1308)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19502265.svg)](https://doi.org/10.5281/zenodo.19502265)
[![License: GPL v3](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)

[![C++ Standard](https://img.shields.io/badge/c%2B%2B-17-007acc.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/python-3.8%2B-007acc.svg)](https://python.org)
[![OpenMP](https://img.shields.io/badge/OpenMP-4.5%2B-007acc.svg)](https://www.openmp.org/)
[![MPI](https://img.shields.io/badge/MPI-OpenMPI%20%7C%20MS--MPI-007acc.svg)](https://www.open-mpi.org/)

[![Wiki](https://img.shields.io/badge/docs-GRANITE%20Wiki-002b36.svg)](https://github.com/LiranOG/Granite/wiki)

---

</div>

> **Status: 🟢 v0.6.7 (active development)** — CCZ4 + full GRMHD + fully dynamic Berger-Oliger AMR, moving-puncture gauge, HDF5 checkpoint write, VORTEX Frontend. 107 unit tests across 20 test suites covering all physics modules: CCZ4, GRMHD, AMR, horizon finder, M1 radiation, HDF5 I/O, initial data, and grid kernels. `single_puncture` + `B2_eq` validated **stable** through t = 500 M (early inspiral phase; full merger run is a v0.8 target).

GRANITE is a high-performance, next-generation numerical relativity and General-Relativistic Magnetohydrodynamics (GRMHD) engine.
Designed from the ground up to model extreme astrophysical events — such as the inspiral and merger of multiple Supermassive Black Holes (SMBHs) interacting with dense stellar environments and accretion discs — GRANITE brings state-of-the-art multi-scale physics into a cohesive, open-source framework.

---

> [!IMPORTANT]
> **Current development status — please read before the feature list.**
>
> GRANITE is an **active research project** by a **solo independent researcher** (not affiliated with any NR collaboration or institution). Before reading the feature list, please be aware of the following current limitations:
>
> - **Merger runs are a v0.8 target.** The t=500M BBH benchmarks below reach *early inspiral only* — no merger has been observed. Full merger + SXS catalog validation is planned for v0.9.
> - **M1 radiation transport** is compiled and unit-tested, but is **not yet wired** into the main RK3 evolution loop.
> - **`--resume` checkpoint restart** is not yet exposed at the CLI (`writeCheckpoint()` works; the `--resume` flag is a v0.7 target).
> - **Recoil velocity** (`computeRecoilVelocity`) throws `std::runtime_error` — not yet implemented.
> - **AMR reflux correction** at coarse-fine interfaces: known accuracy limitation.
> - **Unit tests cover all major physics modules** (107 tests across 20 suites). Only `postprocess` lacks dedicated unit tests.
> - **Native Windows / macOS** unsupported; Linux and WSL2 only.
>
> See [Known Limitations](#️-known-limitations-v067) for the full table.

## 📖 Table of Contents

- [✨ Key Features](#-key-features)
- [⚖️ How GRANITE Compares](#️-how-granite-compares)
- [📊 Benchmark Results](#-benchmark-results)
- [🚀 Quick Start Guide](#-quick-start-guide)
  - [Step 1 — Clone the Repository](#step-1--clone-the-repository)
  - [Step 2 — Install Dependencies & Build](#step-2--install-dependencies--build)
  - [Step 3 — Run the Health Check](#step-3--run-the-health-check-pre-flight)
  - [Step 4 — Run the Unit Tests](#step-4--run-the-unit-tests)
  - [Step 5 — Run the Developer Benchmark](#step-5--run-the-developer-benchmark)
  - [Step 6 — Run a Full Simulation](#step-6--run-a-full-simulation)
- [📁 Repository Structure](#-repository-structure)
- [🗺️ Roadmap](#️-roadmap)
- [⚠️ Known Limitations](#️-known-limitations-v067)
- [📋 Versioning Policy](#-versioning-policy-pre-100)
- [🤝 Open for Collaboration](#-open-for-collaboration)
- [🤝 Contributing](#-contributing)
- [📚 Documentation](#-documentation)
- [🗂 The Genesis Archive: Background & Motivation](#-the-genesis-archive-background--motivation)
- [🌀 VORTEX: The Interactive WebGL Simulator](#-vortex-the-interactive-webgl-simulator)
- [📎 Citing GRANITE](#-citing-granite)
- [👥 Contributors](#-contributors)
- [📜 License](#-license)

---

## ✨ Key Features

- **Spacetime Evolution (CCZ4):** Robust conformal and covariant Z4 formulation for evolving the Einstein field equations with moving-puncture gauge conditions and active constraint damping (κ₁=0.02, η=2.0).
- **GRMHD & Matter:** High-resolution shock-capturing (HRSC) in the Valencia formulation — MP5/PPM/PLM reconstruction, HLLE/HLLD Riemann solvers, constrained transport (∇·B = 0 to machine precision).
- **Adaptive Mesh Refinement (AMR):** Fully dynamic block-structured 
Berger-Oliger subcycling — gradient-based and puncture-tracking refinement 
triggers with iterative union-merge box aggregation, trilinear prolongation, 
volume-weighted restriction, and live per-step regridding integrated into the 
RK3 loop. Supports up to 12 refinement levels; production benchmarks currently 
validated at 4 levels.
- **Multi-BH Initial Data:** Built-in solvers for Brill-Lindquist, Bowen-York, Two-Punctures, and Superposed Kerr-Schild configurations for arbitrarily complex N-body BH systems.
- **Radiation & Neutrino Transport:** Hybrid neutrino leakage + M1 moment closure for photon and neutrino emission/absorption in hot nuclear matter.
- **Diagnostics & GW Extraction:** Flow-method Apparent Horizon finder, Newman-Penrose Ψ₄ GW extraction at multiple radii (50–500 r_g), recoil velocity estimation, and real-time constraint monitoring.
- **HDF5 I/O & Checkpointing:** Fully parallel MPI-IO for grid snapshots and time-series diagnostics. `writeCheckpoint()` serialises the full AMR hierarchy — all grid blocks, spacetime variables, step count, and simulation time — into portable HDF5. `readCheckpoint()` is implemented; `--resume` CLI integration is in active development for v0.7.

---

## ⚖️ How GRANITE Compares

No single existing open-source code simultaneously handles all of these capabilities in a unified framework. GRANITE is specifically architected to close this gap.

### Summary Comparison

| Capability | Einstein Toolkit | GRChombo | SpECTRE | AthenaK | **GRANITE v0.6.7** |
|---|:---:|:---:|:---:|:---:|:---:|
| CCZ4 formulation | ✅ | ✅ | ✅ | ❌ | ✅ |
| Full GRMHD (Valencia) | ✅ | ✅ | 🔶 | ✅ | ✅ |
| M1 radiation transport | ✅ | ❌ | ❌ | ❌ | 🔵 |
| Dynamic AMR (subcycling) | ✅ | ✅ | ✅ | ✅ | ✅ |
| N > 2 BH simultaneous merger | ❌ | ❌ | ❌ | ❌ | 🔵 | 
| Open license | LGPL | ✅ MIT | ✅ MIT | ✅ BSD | ✅ GPL-3.0 |

> *N>2 BH: Brill-Lindquist multi-BH initial data and 5-BH `B5_star` benchmark configuration exist; production run at research resolution (256³+) requires GPU porting (v0.7 target).*

*(Table abridged. See the full feature matrix below.)*

**Legend:**
* ✅ = **Fully implemented** (Production-ready and integrated)
* 🔵 = **Core module built, pending integration** (Mathematical logic and tests pass, pending wiring into the main RK3 loop)
* 🔶 = **Partial / in development** (Currently being actively developed)
* ❌ = **Not available**


> [!NOTE]
> 💡 **Deep-Dive Architectural Analysis & Full Comparison**
> 
> The table above provides only a high-level overview. For an exhaustive, source-cited capability breakdown against *Einstein Toolkit, GRChombo, SpECTRE, and AthenaK*, please refer to the **[Detailed Comparison & Architecture Guide](docs/COMPARISON.md)**. 
---

## 📊 Benchmark Results

All results are from **production runs on a single desktop workstation** (Intel i5-8400, 6-core, 16 GB DDR4, Linux/WSL2). Every number below is from real simulation logs and is fully reproducible by cloning this repository.

### Single Moving Puncture — Schwarzschild Stability

| Resolution | AMR Levels | dx finest | ‖H‖₂ t=0 | ‖H‖₂ final | Reduction | t\_final | NaN events |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 64³ | 4 | 0.1875 M | 1.083 × 10⁻² | 1.277 × 10⁻⁴ | **×84.8** | 500 M ✅ | 0 |
| 128³ | 4 | 0.09375 M | 1.855 × 10⁻² | 1.039 × 10⁻³ | **×17.9** | 120 M ✅ | 0 |

### Binary Black Hole Inspiral — Equal-Mass, Two-Punctures / Bowen-York

| Resolution | AMR Levels | dx finest | ‖H‖₂ peak | ‖H‖₂ final (t=500M) | Reduction | Wall time | Throughput | NaN events |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 64³ | 4 | 0.781 M | 8.226 × 10⁻⁴ | **1.341 × 10⁻⁵** | **×61.3** | 98.9 min | 0.084 M/s | 0 |
| 96³ | 4 | 0.521 M | 2.385 × 10⁻³ | **3.538 × 10⁻⁵** | **×67.4** | 496 min | 0.017 M/s | 0 |

> **What ‖H‖₂ reduction means:** The Hamiltonian constraint measures how accurately the evolved spacetime satisfies Einstein's equations. A monotonically *decreasing* ‖H‖₂ over 500 M of simulated time is a necessary (but not sufficient) indicator of **numerical stability and correct constraint damping**.
>
> **What these benchmarks do NOT yet prove:** The t=500M runs above reach *early inspiral phase only* (no merger observed). Merger-waveform validation against the SXS catalog is a **v0.8–v0.9 target**. See [Known Limitations](#️-known-limitations-v067).
>
> 📄 Raw telemetry, step-by-step logs, and extended resolution tables: [`docs/user_guide/BENCHMARKS.md`](./docs/user_guide/BENCHMARKS.md)

---

## 🚀 Quick Start Guide

> [!NOTE]
> **OS Requirement:** GRANITE is currently optimized exclusively for **Linux** and **WSL2**. Native Windows and macOS are strictly unsupported.
> *Hitting a wall?* See [**INSTALL.md**](./docs/INSTALL.md) for step-by-step guides and exhaustive troubleshooting.

### Step 1 — Clone the Repository
```bash
git clone https://github.com/LiranOG/Granite.git
cd Granite
```

### Step 2 — Install Dependencies & Build

#### 💎 Windows — WSL2 / Ubuntu (the only supported Windows path)

> [!NOTE]
> Native Windows builds via PowerShell or Conda are **not supported**. Use WSL2.

```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
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

Verify Release optimization flags and OpenMP core allocation before any simulation.

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
.\build\bin\Release\granite_tests.exe
# or: cd build && ctest --output-on-failure && cd ..
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
build/bin/granite_tests
# or: cd build && ctest --output-on-failure && cd ..
```

Expected output: `[  PASSED  ] 107 tests.` (107 tests from 20 test suites — covers CCZ4, GRMHD, AMR, horizon finder, M1 radiation, HDF5 I/O, initial data, and grid kernels)

---

### Step 5 — Run the Developer Benchmark

#### 🪟 Windows (PowerShell / CMD / Conda)
```powershell
python scripts/dev_benchmark.py
python scripts/dev_benchmark.py --verbose
python scripts/dev_stability_test.py --t-target 50
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
python3 scripts/dev_benchmark.py
python3 scripts/dev_benchmark.py --verbose
python3 scripts/dev_stability_test.py --t-target 50
```

---

### Step 6 — Run a Full Simulation

#### 🪟 Windows (PowerShell / CMD / Conda)
```powershell
python scripts/run_granite.py run --benchmark gauge_wave
python scripts/run_granite.py run --benchmark single_puncture
python scripts/run_granite.py run --benchmark B2_eq
```

#### 🐧 Linux / 💎 WSL2 / 🍎 macOS
```bash
python3 scripts/run_granite.py run --benchmark gauge_wave
python3 scripts/run_granite.py run --benchmark single_puncture
python3 scripts/run_granite.py run --benchmark B2_eq
```

> [!IMPORTANT]
> Always run `health_check.py` before `B2_eq`. See [`docs/DEPLOYMENT_AND_PERFORMANCE.md`](./docs/DEPLOYMENT_AND_PERFORMANCE.md).

**What healthy output looks like:**
```
  step=80  t=5.0000M  α_center=0.029 [RECOVER]  ‖H‖₂=0.153 [OK]
  Phase: Lapse recovering — trumpet stable ✓
  Advection CFL: 0.938 ✓ stable
```
- `α_center` drops 1 → ~0.003 (lapse collapse), recovers to ~0.03 (trumpet formation) ✓
- `‖H‖₂ < 1.0` through `t = 6M` — constraints satisfied ✓
- NaN Forensics: "No NaN events detected" ✓

Logs saved to `dev_logs/dev_benchmark_<timestamp>.log`.

> [!IMPORTANT]
> Complete A-to-Z setup, dependencies, and full Q&A troubleshooting: [**INSTALL.md**](./docs/INSTALL.md)

---

## 📁 Repository Structure

```text
GRANITE/
├── benchmarks/          # Simulation presets (YAML + expected output).
├── containers/          # Dockerfile + Singularity/Apptainer for HPC.
├── docs/                # Technical documentation, preprint, and paper figures.
│   └── paper/                 # PRD preprint (LaTeX + PDF) + 13 publication figures.
├── include/granite/     # Public C++ headers indexed by subsystem.
├── python/              # granite_analysis installable package (pip install -e .).
├── runs/                # ⚠ gitignored — job scripts and parameter scans.
├── scripts/             # Build/run wrappers, health check, live diagnostics.
├── src/                 # C++17 physics kernels (~8,900 lines).
├── tests/               # 107-test GoogleTest suite across 20 suites (covers all physics modules: CCZ4, GRMHD, AMR, horizon, M1, HDF5 I/O, initial data).
└── viz/                 # Post-processing and visualisation scripts.
    └── vortex_eternity/       # The new WebGL frontend directory
```

> For a complete file-by-file inventory with line counts, module descriptions,
> and subsystem notes, see [`docs/DEVELOPER_GUIDE.md`](./docs/DEVELOPER_GUIDE.md).

---

## 🗺️ Roadmap

| Version | Target | Status | Key Deliverables |
|---|---|:---:|---|
| **v0.6.5** | Q1 2026 | ✅ **Released** | BBH stable to t=500M, 4-level AMR, 92 tests, Python dashboard |
| **v0.6.7** | Q1 2026 | ✅ **Released** | VORTEX Gold Master, dynamic AMR fully wired, HDF5 checkpoint write |
| **v0.7.0** | Q2 2026 | 🔄 In Progress | GPU CUDA kernels, `--resume` checkpoint restart CLI, M1 wired into RK3 loop |
| **v0.8.0** | Q3 2026 | 📋 Planned | Tabulated nuclear EOS + reaction network |
| **v0.9.0** | Q4 2026 | 📋 Planned | Full SXS catalog validation (~60 BBH configs), multi-group M1 |
| **v1.0.0** | Q1 2027 | 🎯 Target | B5\_star production run + publication, full community release + full support across all native OS systems |

**Scaling path to B5\_star:** Development (128³, desktop) → GPU porting (vast.ai H100) → cluster production (256³–512³) → flagship (12 AMR levels, ~2 TB RAM, ~5×10⁶ CPU-hours).

---

## ⚠️ Known Limitations (v0.6.7)

Scientific integrity demands transparency. These limitations are known, documented, and actively addressed.

| Limitation | Impact | Status | Planned Fix |
|---|---|:---:|---|
| `writeCheckpoint()` fully implemented; `--resume` CLI flag not yet wired | Long runs cannot be resumed without code modification | 🔄 Active | v0.7 |
| M1 radiation built but not wired into RK3 loop | Radiation not active in production runs | 🔄 Active | v0.7 |
| `alpha_center` reads from AMR level 0, not finest level near puncture | Misleading lapse diagnostic | 📋 Known | v0.7 |
| GTX 1050 Ti not viable for FP64 GPU compute | GPU path requires H100-class hardware | 📋 Known | Post GPU porting |
| macOS / Windows native unsupported | Limits accessibility | 📋 Planned | v0.8+ |
| Tangential BY momenta required for inspiral p_t ≈ ±0.0954 per BH (quasi-circular, d = 10 M) | Zero momenta → head-on, not inspiral | 📝 Documented | User parameter |

> Full debug context: [`docs/diagnostic_handbook.md`](./docs/diagnostic_handbook.md)

---

## 📋 Versioning Policy (Pre-1.0.0)

> [!IMPORTANT]
> **Until the official `v1.0.0` full release, all version history, phase documentation, and change logs are tracked exclusively inside [`CHANGELOG.md`](./CHANGELOG.md)** — not through GitHub Releases or GitHub's release notes UI.
>
> This is an intentional decision to keep the complete engineering audit trail (Phases 0–5 and beyond) in a single, richly-documented source of truth that lives alongside the code.
>
> **What this means for contributors and users:**
> - The `CHANGELOG.md` file is the canonical record of every bug fix, new feature, architectural decision, and test count milestone.
> - GitHub Tags (e.g. `v0.6.5`) mark stable integration points but carry minimal release notes — refer to `CHANGELOG.md` for the full picture.
> - GitHub Releases will be created officially at `v1.0.0` — the first production-ready, fully-coherent version of the engine.

---

## 🤝 Open for Collaboration

GRANITE is built by an independent researcher. If you work in numerical
relativity, GRMHD, gravitational-wave astronomy, or computational
astrophysics — and are interested in reviewing, extending, or testing
the engine — your input is very welcome.

**What would be most useful:**

| What you can offer | Why it helps |
|---|---|
| **Physics review** — familiarity with CCZ4, Valencia GRMHD, or apparent horizon finding | Catch formula errors, validate algorithmic choices against literature |
| **Benchmark validation** on HPC clusters | Current benchmarks are desktop-only; cluster scaling is entirely untested |
| **Comparison runs** against established codes (Einstein Toolkit, GRChombo) on standard scenarios | Gauge wave, single puncture, Balsara shock tubes |
| **Bug reports and PRs** at any scale | One-line fix, new unit test, missing C2P edge case — all of it helps |

I am a solo developer, not affiliated with any institutional NR group. The project is
released under GPL-3.0 in the hope that it will be useful and instructive.

If you're interested — open a GitHub Discussion or email `scliran9@gmail.com`.

---

## 🤝 Contributing

Contributions from the scientific and open-source communities are welcome. Please read [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) and adhere to [`.github/CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

```bash
python3 scripts/run_granite.py format   # Auto-format all C++ contributions
```

### 🌍 How You Can Contribute — On Your Own Terms

There is no minimum. There is no gatekeeping. There is no "small enough to not matter."

| What you bring | How it helps GRANITE |
|---|---|
| **You run it on your cluster** | Real-world scaling data and hardware-specific failure modes a desktop cannot surface |
| **You read the physics and find something wrong** | A wrong formula caught early is worth a thousand correct ones discovered late |
| **You submit a PR — any size** | A one-line fix, a new unit test, a missing C2P edge case — all of it moves the needle |
| **You open an issue** | Describing what broke, what confused you, or what's missing is itself a contribution of enormous value |
| **You share it with a colleague** | The person most likely to find the deepest bug is the one I haven't met yet |
| **You validate a benchmark** | Running `B2_eq` and sharing constraint norms takes 20 minutes and generates ground truth I cannot produce alone |
| **You review the theory** | If you work in NR, GRMHD, or computational astrophysics — your professional eye is the most valuable thing you could offer |

No contribution requires understanding the whole codebase. The modules are deliberately decoupled: an expert in radiation transport can engage with `src/radiation/` without touching the CCZ4 RHS loop.

---
## 📚 Documentation

| Document | Description |
|---|---|
| [`docs/DEVELOPER_GUIDE.md`](./docs/DEVELOPER_GUIDE.md) | **Complete Developer Reference** — architecture, all 22 CCZ4 variables, physics formulations, data structures, coding standards, testing workflow, and HPC guidelines. |
| [`docs/BENCHMARKS.md`](./docs/BENCHMARKS.md) | **Full Benchmark Report** — raw telemetry tables, constraint norm time series, resolution convergence, and hardware profiles for all production runs. |
| [`docs/SCIENCE.md`](./docs/SCIENCE.md) | **Science & Physics Reference** — governing equations, B5\_star scenario, GRANITE's place in the NR landscape, and multi-messenger astrophysics context. |
| [`docs/COMPARISON.md`](./docs/COMPARISON.md) | **Code Comparison** — source-cited, per-feature comparison against Einstein Toolkit, GRChombo, SpECTRE, and AthenaK. |
| [`docs/FAQ.md`](./docs/FAQ.md) | **Frequently Asked Questions** — science, engineering, HPC, and contribution questions answered in depth. |
| [`docs/v0.6.5_master_dictionary.md`](./docs/v0.6.5_master_dictionary.md) | **Exhaustive Technical Reference** — every CLI flag, YAML parameter, C++ constant, CMake option, and all Stability Patch forensic records. |
| [`docs/diagnostic_handbook.md`](./docs/diagnostic_handbook.md) | **Diagnostic Handbook** — lapse lifecycle, ‖H‖₂ interpretation, NaN forensics, and the Health Check Checklist. |
| [`docs/INSTALL.md`](./docs/INSTALL.md) | **Complete Installation Guide** — per-terminal dependency setup, troubleshooting Q&A, and build verification. |
| [`docs/paper/granite_preprint_v067.tex`](./docs/paper/granite_preprint_v067.tex) | **Technical Paper (Draft)** — Full formalism, CCZ4/GRMHD/VORTEX description, and validated benchmarks. In preparation for *Physical Review D*. ([compiled PDF](./docs/paper/granite_preprint_v067.pdf)) |

---

## 📖 Deep-Dive Documentation — GRANITE Wiki

The `docs/` directory covers the essentials, but GRANITE is a large and technically demanding engine. For researchers, contributors, and institutions who need to go beyond the surface level, every subsystem has its own dedicated Wiki page — written at the same level of technical depth as a peer-reviewed software paper.

> **[→ Visit the GRANITE Wiki](https://github.com/LiranOG/Granite/wiki)**

The Wiki covers, in full technical detail:

| Topic | Wiki Page |
| --- | --- |
| Engine architecture, data flow, and memory layout | [Architecture Overview](https://github.com/LiranOG/Granite/wiki/Architecture-Overview) |
| Every `params.yaml` parameter with ranges, units, and failure modes | [Parameter Reference](https://github.com/LiranOG/Granite/wiki/Parameter-Reference) |
| Simulation health, ‖H‖₂ interpretation, NaN forensics, debugging flowchart | [Simulation Health & Debugging](https://github.com/LiranOG/Granite/wiki/Simulation-Health-&-Debugging) |
| All confirmed fixed bugs with code diffs — never re-introduce these | [Known Fixed Bugs](https://github.com/LiranOG/Granite/wiki/Known-Fixed-Bugs) |
| Full CCZ4, GRMHD, M1, and CT governing equations with references | [Physics Formulations](https://github.com/LiranOG/Granite/wiki/Physics-Formulations) |
| Bowen-York momenta, TOV solver, initial data compatibility matrix | [Initial Data](https://github.com/LiranOG/Granite/wiki/Initial-Data) |
| Berger-Oliger subcycling, prolongation, restriction, ghost zones | [AMR Design](https://github.com/LiranOG/Granite/wiki/AMR-Design) |
| Ψ₄ extraction, spherical harmonics, strain recovery, recoil kick | [GW Extraction](https://github.com/LiranOG/Granite/wiki/Gravitational-Wave-Extraction) |
| Full benchmark tables, reproducibility commands, HPC projections | [Benchmarks & Validation](https://github.com/LiranOG/Granite/wiki/Benchmarks-&-Validation) |
| SLURM templates, Lustre I/O tuning, container deployment, GPU roadmap | [HPC Deployment](https://github.com/LiranOG/Granite/wiki/HPC-Deployment) |
| Coding standards, PR checklist, CI/CD, adding physics modules | [Developer Guide](https://github.com/LiranOG/Granite/wiki/Developer-Guide) |
| B5_star scenario, multi-messenger physics, LISA / PTA signals | [Scientific Context](https://github.com/LiranOG/Granite/wiki/Scientific-Context) |
| Version targets, GPU porting plan, Tier-1 blockers for v0.7 | [Roadmap](https://github.com/LiranOG/Granite/wiki/Roadmap) |
| 15 answered questions on science, engineering, and HPC | [FAQ](https://github.com/LiranOG/Granite/wiki/FAQ) |
| Complete inventory of every document in the repository | [Documentation Index](https://github.com/LiranOG/Granite/wiki/Documentation-Index-&-Master-Reference) |
| Explore the interactive WebGL N-body simulator | [VORTEX Engine](https://github.com/LiranOG/Granite/wiki/VORTEX-Simulator) |
| Learn about the Architecture History of GRANITE & VORTEX | [Theoretical & Architectural Overview](https://github.com/LiranOG/Granite/wiki/GRANITE%E2%80%90Astrophysics%E2%80%90Suite-%E2%80%94-Theoretical-&-Architectural-Overview#-granite-astrophysics-suite--the-definitive-theoretical--architectural-overview) |

***If something is unclear — in the code, in the physics, or in the parameters — the answer is almost certainly in one of these pages.***

---

## 🗂 The Genesis Archive: Background & Motivation

The C++ engine in this repository was preceded by a series of personal research notes
exploring the physics of multi-BH merger scenarios. These notes motivated the key
architectural choices:

Every major architectural decision in GRANITE traces to a specific physical requirement:

- **CCZ4 over BSSN** — for active constraint damping on long evolution timescales required by cascade scenarios
- **Valencia GRMHD** — for exact conservation on curved spacetime during stellar disruption events
- **M1 radiation transport** — for accurate photon and neutrino coupling in hot nuclear debris
- **Deep AMR (≥12 levels targeted)** — for the ~10⁸ dynamic range spanning BH horizons to circumbinary disk scales

These choices are grounded in established NR literature. The personal research notes that
preceded the code are archived separately for transparency at
**[GRANITE-Astrophysics-Suite](https://github.com/LiranOG/GRANITE-Astrophysics-Suite)**.

> **Note:** The archived notes are **personal theoretical exploration, not peer-reviewed results.**
> They provide context for architectural decisions, but should not be read as predictions the
> engine is validated against. Formal validation follows the standard NR protocol: benchmarks
> against known analytic solutions and comparison against the SXS catalog (v0.9 target).

> *For the derivation archive and interactive kinematic simulations:*
> **[→ GRANITE-Astrophysics-Suite](https://github.com/LiranOG/GRANITE-Astrophysics-Suite)**

---

## 🌀 VORTEX: The Interactive WebGL Simulator

**VORTEX** ([`viz/vortex_eternity/`](./viz/vortex_eternity/)) is a standalone, browser-native N-body physics renderer built on a strict **Zero-Allocation Architecture** — all hot-path computation operates on pre-allocated Float32Arrays with no per-frame garbage collection.

**Physics Engine:** 4th-Order Hermite Predictor-Corrector integrator with Kahan compensated summation and dynamic Aarseth timestepping. Implements 1.5PN Lense-Thirring frame-dragging, 2.5PN radiation-reaction (GW inspiral), mass-defect mergers, and Tidal Disruption Events — all running in real time in the browser.

**Research-Grade Diagnostics (Gold Master):**
- `🔭 NR Diagnostics` — live Chart.js panels for orbital eccentricity vs. semi-major axis, GW chirp frequency sweep (f_GW), and relativistic velocity parameter (β²)
- Minimap 3.0 with gravitational isobar contours (marching-squares), radiation flux thermal overlay, ISCO proximity warnings, and logarithmic projection
- CPU-side Relativistic Doppler/Beaming and Einstein Cross gravitational lens GLSL shader extension

**Cinematic Systems:** Zen Mode (full UI fade to black for recording), Cinematic Autopilot camera director, and ESC-abort placement system.

**v1.0 Coupling Vision:** GRANITE's HDF5 outputs will be distilled into kinematic streams and ingested by VORTEX as a high-fidelity 3D playback viewer, enabling real-time interactive exploration of full GR numerical relativity data.

> **[🚀 Explore VORTEX](./viz/vortex_eternity/)**

---

## 📎 Citing GRANITE

If you use GRANITE in academic research, teaching, or scientific software, please cite:

```bibtex
@software{granite2026,
  author    = {LiranOG},
  title     = {{GRANITE}: General-Relativistic Adaptive N-body Integrated
               Tool for Extreme Astrophysics},
  year      = {2026},
  version   = {v0.6.7},
  url       = {https://github.com/LiranOG/Granite},
  note      = {CCZ4 + GRMHD + AMR engine for multi-body black hole merger simulations}
}
```

A technical draft describing GRANITE's formalism and benchmarks is being developed.
See `docs/paper/granite_preprint_v067.tex` and `docs/citation.bib`.

---

### 🙏 A Genuine Thank You

To those who will file a bug report at 11pm because something didn't converge and they couldn't let it go — thank you in advance.

To those who will spend a Saturday writing a test for a corner case nobody asked them to cover — thank you in advance.

To those who will send a message saying "I ran `B2_eq` on our cluster and here's what happened" — thank you in advance.

To those who will read a formula in `ccz4.cpp` and say "wait, shouldn't that sign be negative?" — *especially* thank you in advance.


This project exists because the science demands it. It will reach its potential because the community makes it.

I have written a **[Personal Note to the Community](docs/PERSONAL_NOTE.md)** explaining exactly why GRANITE was built and the philosophy behind it. If you share this obsession with the cosmos, I invite you to read it.


**Welcome aboard. Let's simulate the universe — together.**

<div align="right">

[![GitHub Issues](https://img.shields.io/github/issues/LiranOG/Granite?label=open%20issues&color=blue)](https://github.com/LiranOG/Granite/issues)
[![GitHub Discussions](https://img.shields.io/github/discussions/LiranOG/Granite?label=discussions&color=purple)](https://github.com/LiranOG/Granite/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/LiranOG/Granite/blob/main/.github/CONTRIBUTING.md)

</div>

---

## 👥 Contributors

GRANITE is currently a **solo project** by [Liran M. Schwartz](https://orcid.org/0009-0008-8035-1308).

If you use, test, review, or contribute to GRANITE in any way — you are part of the story.
See [Open for Collaboration](#-open-for-collaboration) or open a [GitHub Discussion](https://github.com/LiranOG/Granite/discussions) to get involved.

---

## 📜 License

GRANITE is released under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**. See the [`LICENSE`](./LICENSE) file for full terms.

<div align="center">

[⬆️BACK TO THE TOP⬆️](#granite-)

</div>
