> ### 📝 A Note from the Developer: The Vision, The Reality, and The Road Ahead
>
> **Welcome to GRANITE.** This project was born from a simple but overwhelming ambition: *to simulate the unimaginable*. I wanted to build an engine capable of modeling scenarios that still feel like science fiction—multiple supermassive black holes merging, tearing through stars, and interacting with extreme matter, all happening simultaneously. Currently, existing engines struggle to couple all these physics (CCZ4 spacetime evolution, GRMHD, and Adaptive Mesh Refinement) without collapsing under the computational weight. My goal is to build the architecture that finally solves this.
>
> **Currently, GRANITE is driven by a single independent developer. To transition from a powerful solo-architected engine into a universally trusted scientific instrument, it is time to open the doors to the community.**
>
> ---
>
> #### ⚠️ Deployment Notice
> Making all these complex engines communicate perfectly, optimizing OpenMP threads, and managing AMR grids takes an immense amount of bandwidth. Because my focus must remain 100% on the physics and the engine's stability, I have to make a hard choice regarding deployment:
>
> **Currently, native Windows (CMD/PowerShell) and macOS are STRICTLY UNSUPPORTED.**
>
> Trying to troubleshoot package managers, compilers, and terminal quirks across every operating system is draining resources I simply do not have right now. To run GRANITE, **you must use Linux or Windows Subsystem for Linux (WSL2).** The engine is optimized for environments where dependencies are natively supported, allowing you to bypass installation headaches and focus on the science.
>
> **My promise to you:** In the future, once the core engine is flawless and perfectly optimized, I will dedicate the time to make GRANITE a true plug-and-play experience across every OS.
>
> ---
>
> #### 🤝 A Call for Collaboration
> **Until then, I am asking for your help.** To the scientific community, physicists, and HPC administrators: The foundational math and architecture are here, but transforming this into a universally trusted scientific instrument requires more than one pair of hands.
>
> I warmly invite you to review the code, test it on your clusters, point out the flaws, and submit PRs. Let's look past the current rough edges and build the ultimate open-source engine for extreme astrophysics together.

---

# GRANITE 🌌
**General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

[![Build Status](https://github.com/LiranOG/Granite/actions/workflows/ci.yml/badge.svg)](https://github.com/LiranOG/Granite/actions)
[![License: GPL v3](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![DOI](https://sandbox.zenodo.org/badge/DOI/10.5072/zenodo.486359.svg)](https://sandbox.zenodo.org/record/486359)
[![C++ Standard](https://img.shields.io/badge/c%2B%2B-17-purple.svg)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-92%20%2F%20100%25-brightgreen.svg)](tests/)
[![AMR Levels](https://img.shields.io/badge/max%20AMR%20levels-12-orange.svg)](docs/DEVELOPER_GUIDE.md)
[![Physics Modules](https://img.shields.io/badge/physics%20modules-6-blueviolet.svg)](src/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](.github/CONTRIBUTING.md)

> **Status: 🟢 The Stability Update (v0.6.5)** — CCZ4 spacetime evolution, full GRMHD, dynamic Berger-Oliger AMR subcycling, moving-puncture tracking, and diagnostic Python dashboards are fully integrated. 92 tests / 100% pass rate. `single_puncture` + `B2_eq` benchmarks validated stable through t = 500 M.

GRANITE is a high-performance, next-generation numerical relativity and General-Relativistic Magnetohydrodynamics (GRMHD) engine. Designed from the ground up to model extreme astrophysical events — such as the inspiral and merger of multiple Supermassive Black Holes (SMBHs) interacting with dense stellar environments and accretion discs — GRANITE brings state-of-the-art multi-scale physics into a cohesive, open-source framework.

---

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
- [⚠️ Known Limitations](#️-known-limitations-v065)
- [📋 Versioning Policy](#-versioning-policy-pre-100)
- [💙 To the Community](#-to-the-community--a-personal-word)
- [🏛️ Institutional Partnership & Supercomputing Readiness](#️-institutional-partnership--supercomputing-readiness)
- [🤝 Contributing](#-contributing)
- [📚 Documentation](#-documentation)
- [📎 Citing GRANITE](#-citing-granite)
- [📜 License](#-license)

---

## ✨ Key Features

- **Spacetime Evolution (CCZ4):** Robust conformal and covariant Z4 formulation for evolving the Einstein field equations with moving-puncture gauge conditions and active constraint damping (κ₁=0.02, η=2.0).
- **GRMHD & Matter:** High-resolution shock-capturing (HRSC) in the Valencia formulation — MP5/PPM/PLM reconstruction, HLLE/HLLD Riemann solvers, constrained transport (∇·B = 0 to machine precision).
- **Adaptive Mesh Refinement (AMR):** Block-structured Berger-Oliger subcycling with gradient-based dynamic refinement (up to 12 levels), trilinear prolongation, and volume-weighted restriction.
- **Multi-BH Initial Data:** Built-in solvers for Brill-Lindquist, Bowen-York, Two-Punctures, and Superposed Kerr-Schild configurations for arbitrarily complex N-body BH systems.
- **Radiation & Neutrino Transport:** Hybrid neutrino leakage + M1 moment closure for photon and neutrino emission/absorption in hot nuclear matter.
- **Diagnostics & GW Extraction:** Flow-method Apparent Horizon finder, Newman-Penrose Ψ₄ GW extraction at multiple radii (50–500 r_g), recoil velocity estimation, and real-time constraint monitoring.
- **HDF5 I/O:** Fully parallel MPI-IO for grid snapshots, checkpoints, and time-series diagnostics.

---

## ⚖️ How GRANITE Compares

No single existing open-source code simultaneously handles all of these capabilities in a unified framework. GRANITE is specifically architected to close this gap.

| Capability | Einstein Toolkit | GRChombo | SpECTRE | AthenaK | **GRANITE v0.6.5** |
|---|:---:|:---:|:---:|:---:|:---:|
| CCZ4 formulation | ✅ | ✅ | ✅ | ❌ | ✅ |
| Full GRMHD (Valencia) | ✅ | ✅ | 🔶 | ✅ | ✅ |
| M1 radiation transport | ✅ | ❌ | ❌ | ❌ | ✅ |
| Neutrino leakage | ✅ | ❌ | ❌ | ❌ | ✅ |
| Dynamic AMR (subcycling) | ✅ | ✅ | ✅ | ✅ | ✅ |
| N > 2 BH simultaneous merger | ❌ | ❌ | ❌ | ❌ | ✅ |
| Single unified codebase | ❌ | ✅ | ✅ | ✅ | ✅ |
| MP5 + HLLD + CT combined | ❌ | ❌ | ❌ | ✅ | ✅ |
| Python real-time telemetry | ❌ | ❌ | ❌ | ❌ | ✅ |
| Open license | LGPL | ✅ MIT | ✅ MIT | ✅ BSD | ✅ GPL-3.0 |

> 🔶 = partial / in development. Full source-cited analysis: [`docs/COMPARISON.md`](./docs/COMPARISON.md)

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

> **What ‖H‖₂ reduction means:** The Hamiltonian constraint measures how accurately the evolved spacetime satisfies Einstein's equations. A monotonically *decreasing* ‖H‖₂ over 500 M of simulated time — through a full BBH inspiral — is a quantitative proof of numerical stability, correct constraint damping, and physical consistency.
>
> 📄 Raw telemetry, step-by-step logs, and extended resolution tables: [`docs/BENCHMARKS.md`](./docs/BENCHMARKS.md)

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

#### 💎 Windows — WSL2 / Ubuntu (Recommended ⭐)
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

#### 🪟 Windows — Native PowerShell / CMD
```powershell
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="../vcpkg/scripts/buildsystems/vcpkg.cmake" -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

#### 🐍 Windows — Miniforge / Conda
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

Expected output: `[  PASSED  ] 92 tests.` (92 tests from 16 test suites)

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
├── benchmarks/              # Self-contained simulation presets (YAML + expected output).
│   ├── B2_eq/               # Equal-mass (M=1.0) binary BH merger — inspiral + ringdown.
│   ├── gauge_wave/          # 1-D sinusoidal gauge validation for CCZ4 advection stability.
│   ├── scaling_tests/       # SLURM/PBS strong & weak-scaling job templates for HPC.
│   └── single_puncture/     # Standard 3-D moving-puncture Schwarzschild stability benchmark.
├── CMakeLists.txt           # Master CMake build: MPI, OpenMP, HDF5, CUDA/HIP, Google Test.
├── containers/              # Container definitions for reproducible HPC deployments.
│   ├── Dockerfile           # Docker multi-stage image (Ubuntu 22.04, HDF5, OpenMPI).
│   └── granite.def          # Singularity/Apptainer definition file for cluster environments.
├── docs/                    # Permanent technical reference documentation.
│   ├── DEVELOPER_GUIDE.md           # Complete developer reference: architecture, physics, APIs.
│   ├── BENCHMARKS.md                # Full benchmark data, raw telemetry, convergence tables.
│   ├── COMPARISON.md                # Source-cited comparison vs. existing NR codes.
│   ├── SCIENCE.md                   # Physics motivation, equations, B5_star scenario.
│   ├── FAQ.md                       # Frequently asked questions — science, engineering, HPC.
│   ├── diagnostic_handbook.md       # Telemetry guide: lapse, ‖H‖₂, NaN forensics.
│   ├── v0.6.5_master_dictionary.md  # Exhaustive CLI, parameter, and stability-patch reference.
│   ├── INSTALL.md                   # A-to-Z installation guide per terminal.
│   ├── internal/                    # Internal architecture notes (not user-facing).
│   ├── theory/                      # Physics derivations and CCZ4 notation reference.
│   └── user_guide/                  # End-user tutorials and worked examples.
├── include/granite/         # Public C++ interface headers indexed by subsystem.
│   ├── amr/                 # AMR hierarchy, Berger-Oliger interfaces, tracking spheres.
│   ├── core/                # Low-level primitives: GridBlock, type aliases, dimension traits.
│   ├── grmhd/               # GRMHD Valencia-formulation routines and EOS lookup tables.
│   ├── initial_data/        # Analytic metric setters: Brill-Lindquist, Bowen-York, SKS.
│   ├── io/                  # MPI-aware HDF5 streamers and exact-state checkpoint managers.
│   ├── postprocess/         # Ψ₄ GW extraction, horizon finder, recoil estimator headers.
│   └── spacetime/           # CCZ4 evolution equations, constraint monitor, gauge drivers.
├── python/                  # Installable Python analysis package (pip install -e .).
│   └── granite_analysis/    # HDF5 reader, GW strain extraction, matplotlib plot helpers.
├── runs/                    # ⚠ gitignored. Job scripts and parameter-scan configs.
├── scripts/                 # Python build/run wrappers and live diagnostics dashboard.
│   ├── dev_benchmark.py     # Forensic diagnostic runner: NaN propagation + constraint tracking.
│   ├── dev_stability_test.py # Extended stability sweep across t-target values.
│   ├── health_check.py      # Pre-flight: verifies Release flags, OMP core count, memory.
│   ├── run_granite.py       # Unified CLI: build / run / clean / format subcommands.
│   ├── run_granite_hpc.py   # HPC launch wrapper: NUMA overrides, MPI ranks, AMR telemetry.
│   └── sim_tracker.py       # Context-aware live dashboard with rich telemetry log mirroring.
├── src/                     # High-performance C++ physics kernels and engine entry point.
│   ├── amr/                 # Restriction, 4th-order prolongation, regridding, ghost sync.
│   ├── initial_data/        # BL conformal factor solver and Bowen-York Newton-Raphson.
│   ├── spacetime/           # OpenMP-parallelised CCZ4 RHS loops (Ricci, KO dissipation).
│   └── main.cpp             # Engine entry point: YAML load, AMR init, RK3 time loop.
├── tests/                   # 92-test GoogleTest suite (physics accuracy + advection stability).
└── viz/                     # Post-processing and visualisation scripts.
    └── README.md            # Documents planned plot_constraints.py, plot_gw.py, etc.
```

---

## 🗺️ Roadmap

| Version | Target | Status | Key Deliverables |
|---|---|:---:|---|
| **v0.6.5** | Q1 2026 | ✅ **Released** | BBH stable to t=500M, 4-level AMR, 92 tests, Python dashboard |
| **v0.7.0** | Q2 2026 | 🔄 In Progress | GPU CUDA kernels, checkpoint-restart, full dynamic AMR regrid, M1 wired into RK3 |
| **v0.8.0** | Q3 2026 | 📋 Planned | Tabulated nuclear EOS + reaction network |
| **v0.9.0** | Q4 2026 | 📋 Planned | Full SXS catalog validation (~60 BBH configs), multi-group M1 |
| **v1.0.0** | Q1 2027 | 🎯 Target | B5\_star production run + publication, full community release + full support across all native OS systems |

**Scaling path to B5\_star:** Development (128³, desktop) → GPU porting (vast.ai H100) → cluster production (256³–512³) → flagship (12 AMR levels, ~2 TB RAM, ~5×10⁶ CPU-hours).

---

## ⚠️ Known Limitations (v0.6.5)

Scientific integrity demands transparency. These limitations are known, documented, and actively addressed.

| Limitation | Impact | Status | Planned Fix |
|---|---|:---:|---|
| Checkpoint-restart not implemented (`loadCheckpoint()` stub only) | Long runs cannot resume after interruption | 🔄 Active | v0.7 |
| M1 radiation built but not wired into RK3 loop | Radiation not active in production runs | 🔄 Active | v0.7 |
| Dynamic AMR regridding partially implemented | Block count fixed at initialization | 🔄 Active | v0.7 |
| Phase labels (Early/Mid/Late Inspiral) are time-based, not separation-based | Approximate classification | 📋 Known | v0.7 |
| `alpha_center` reads from AMR level 0, not finest level near puncture | Misleading lapse diagnostic | 📋 Known | v0.7 |
| GTX 1050 Ti not viable for FP64 GPU compute | GPU path requires H100-class hardware | 📋 Known | Post GPU porting |
| macOS / Windows native unsupported | Limits accessibility | 📋 Planned | v0.8+ |
| Tangential BY momenta required for inspiral (p_t ≈ ±0.084 per BH) | Zero momenta → head-on, not inspiral | 📝 Documented | User parameter |

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

## 💙 To the Community — A Personal Word

> *"The universe doesn't yield its secrets to a single observer.
> It never has. It never will."*

I want to speak to you directly — not as a project README, but as one person who built something they genuinely believe in, reaching out to the people who might care about it just as much.

GRANITE started as a private obsession: the conviction that the astrophysics community deserved an open-source engine capable of simulating the most extreme multi-body events the universe produces — not one day, not in theory, but *now*, with rigorous physics and reproducible science. Every line of this codebase was written with that conviction. The CCZ4 formulation, the GRMHD Valencia kernel, the AMR subcycling, the constraint monitors — none of it was scaffolded or approximated. It was derived, implemented, debugged, and validated with the same standard I would hold any published code to.

But a single developer, no matter how driven, is still just one person. And a scientific instrument — which is what GRANITE is meant to become — is not built by one person. It is built by a community of people who each bring something irreplaceable: a sharper eye for a subtle numerical instability, a deeper familiarity with a particular cluster's topology, a physical intuition that catches what the tests don't, a weekend spent stress-testing a benchmark nobody else thought to run.

**This is that invitation.**

---

### 🌍 How You Can Contribute — On Your Own Terms

There is no minimum. There is no gatekeeping. There is no "small enough to not matter."

| What you bring | How it helps GRANITE |
|---|---|
| **You run it on your cluster** | Real-world scaling data and hardware-specific failure modes a desktop cannot surface |
| **You read the physics and find something wrong** | A wrong formula caught early is worth a thousand correct ones discovered late |
| **You submit a PR — any size** | A one-line fix, a new unit test, a missing C2P edge case — all of it moves the needle |
| **You open an issue** | Describing what broke, what confused you, or what's missing is itself a contribution of enormous value |
| **You share it with a colleague** | The person most likely to find the deepest bug is the one we haven't met yet |
| **You validate a benchmark** | Running `B2_eq` and sharing constraint norms takes 20 minutes and generates ground truth we cannot produce alone |
| **You review the theory** | If you work in NR, GRMHD, or computational astrophysics — your professional eye is the most valuable thing you could offer |

No contribution requires understanding the whole codebase. The modules are deliberately decoupled: an expert in radiation transport can engage with `src/radiation/` without touching the CCZ4 RHS loop.

---

### 🏛️ To Research Groups & Institutions

The codebase is **fully open, GPL-3.0-licensed, and architecturally designed for extension**. We are not asking you to replace your existing tools. We are asking whether some of what we have built might be useful to you, and whether some of what you know might make GRANITE better for everyone.

We are actively interested in joint validation campaigns, Tier-0/1 allocation access for B5\_star, graduate student and postdoc involvement, and waveform template collaboration with LIGO/Virgo/LISA groups.

If any of this resonates, open an issue tagged `[partnership]` or contact the maintainer via the repository.

---

### 🙏 A Genuine Thank You

To those who will file a bug report at 11pm because something didn't converge and they couldn't let it go — thank you in advance.

To those who will spend a Saturday writing a test for a corner case nobody asked them to cover — thank you in advance.

To those who will send a message saying "I ran `B2_eq` on our cluster and here's what happened" — thank you in advance.

To those who will read a formula in `ccz4.cpp` and say "wait, shouldn't that sign be negative?" — *especially* thank you in advance.


This project exists because the science demands it. It will reach its potential because the community makes it.

**Welcome aboard. Let's simulate the universe — together.**

— **LiranOG**, Founder & Lead Developer | April 10, 2026

<div align="right">

[![GitHub Issues](https://img.shields.io/github/issues/LiranOG/Granite?label=open%20issues&color=blue)](https://github.com/LiranOG/Granite/issues)
[![GitHub Discussions](https://img.shields.io/github/discussions/LiranOG/Granite?label=discussions&color=purple)](https://github.com/LiranOG/Granite/discussions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/LiranOG/Granite/blob/main/.github/CONTRIBUTING.md)

</div>

---

## 🏛️ Institutional Partnership & Supercomputing Readiness

> **The mathematical foundation is rock solid. The engine is ready. Come run it at scale.**

GRANITE's 100% pass rate across 92 test suites is not a claim — it is a verifiable, reproducible, auditable fact any institution can confirm in under an hour on any Linux HPC node.

| Partner type | What GRANITE brings | What we seek |
|---|---|---|
| **National supercomputing centres** (NERSC, BSC, ARCHER2, Jülich) | Production-ready MPI+OpenMP engine, SLURM/PBS templates, AMR telemetry | Tier-1 allocation for strong/weak scaling benchmarks |
| **Numerical relativity groups** (AEI, RIT, Cardiff, Caltech) | Open CCZ4 codebase, community-extensible AMR, Python telemetry | Code review, physics validation, joint publications |
| **Gravitational wave observatories** (LIGO, Virgo, LISA prep) | Template bank generation at institutional scale | Waveform validation against detector strain data |
| **Computational science departments** | Pedagogically clean C++17 engine, 92-test teaching harness | Graduate students, postdocs, course integration |

### HPC Quick-Start

```bash
python3 scripts/run_granite_hpc.py build/bin/granite_main \
    benchmarks/B2_eq/params.yaml  \
    --omp-threads 32              \
    --mpi-ranks 128               \
    --disable-numa-bind           \
    --amr-telemetry-file /scratch/$USER/amr_scaling.jsonl
```

Job scheduler templates (SLURM + PBS/Torque): [`benchmarks/scaling_tests/`](./benchmarks/scaling_tests/)

**If your institution runs NR workloads, operates Tier-1/2 supercomputers, or trains the next generation of gravitational wave scientists — we would like to hear from you.** Open a GitHub Issue tagged `[partnership]`.

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

If something is unclear — in the code, in the physics, or in the parameters — the answer is almost certainly in one of these pages.

---

## 🤝 Contributing

We welcome contributions from the scientific and open-source communities. Please read [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) and adhere to [`.github/CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md).

```bash
python3 scripts/run_granite.py format   # Auto-format all C++ contributions
```

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

---

## 📎 Citing GRANITE

If you use GRANITE in academic research, teaching, or scientific software, please cite:

```bibtex
@software{granite2026,
  author    = {LiranOG},
  title     = {{GRANITE}: General-Relativistic Adaptive N-body Integrated
               Tool for Extreme Astrophysics},
  year      = {2026},
  version   = {v0.6.5},
  url       = {https://github.com/LiranOG/Granite},
  note      = {CCZ4 + GRMHD + AMR engine for multi-body black hole merger simulations}
}
```

A formal paper is in preparation (see `docs/citation.bib`). Please also cite the upstream physics papers that GRANITE implements — full reference list in [`docs/SCIENCE.md`](./docs/SCIENCE.md#references).

---

## 👥 Contributors

<a href="https://github.com/LiranOG/Granite/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=LiranOG/Granite" />
</a>

---

## 📜 License

GRANITE is released under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)**. See the [`LICENSE`](./LICENSE) file for full terms.
