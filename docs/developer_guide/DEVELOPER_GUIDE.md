# GRANITE Developer Guide

> **General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics**

| Field | Value |
|---|---|
| **Current Development Version** | 0.6.7 (main branch) |
| **Last Stable Version** | 0.6.5 — Stability & Benchmark Release |
| **Release Date (Stable)** | April 10, 2026 |
| **Maintainer** | LiranOG (Founder & Lead Developer) |
| **License** | GPL-3.0 (see `LICENSE`) |
| **Repository** | https://github.com/LiranOG/Granite |
| **Language** | C++17 + MPI + OpenMP (CUDA/HIP roadmap in progress) |
| **Test Suite** | 107 tests, 100% pass rate (GoogleTest) |
| **Status** | Active development — binary black hole production runs operational |

---

## Table of Contents

1. [Project Philosophy & Scientific Motivation](#1-project-philosophy--scientific-motivation)
2. [Repository Structure](#2-repository-structure)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Data Structures](#4-core-data-structures)
5. [Physics Formulations](#5-physics-formulations)
6. [Numerical Methods](#6-numerical-methods)
7. [Initial Data](#7-initial-data)
8. [AMR Engine](#8-amr-engine)
9. [Boundary Conditions](#9-boundary-conditions)
10. [Diagnostics & GW Extraction](#10-diagnostics--gw-extraction)
11. [I/O & Checkpointing](#11-io--checkpointing)
12. [MPI & OpenMP Parallelism](#12-mpi--openmp-parallelism)
13. [Development Environment Setup](#13-development-environment-setup)
14. [Build System](#14-build-system)
15. [Coding Standards & Style Guide](#15-coding-standards--style-guide)
16. [Testing Philosophy & Workflow](#16-testing-philosophy--workflow)
17. [Adding New Features / Physics Modules](#17-adding-new-features--physics-modules)
18. [Parameter System (YAML)](#18-parameter-system-yaml)
19. [HPC & Performance Guidelines](#19-hpc--performance-guidelines)
20. [Known Fixed Bugs (CHANGELOG Reference)](#20-known-fixed-bugs-changelog-reference)
21. [Simulation Health & Debugging](#21-simulation-health--debugging)
22. [Scientific Validation & Publication Policy](#22-scientific-validation--publication-policy)
23. [Collaboration & Community](#23-collaboration--community)
24. [Roadmap (v0.7 → v1.0)](#24-roadmap-v07--v10)
25. [Flagship Scenario: B5\_star](#25-flagship-scenario-b5_star)

---

## 1. Project Philosophy & Scientific Motivation

### 1.1 Why GRANITE Exists

GRANITE was created to fill a specific and critical gap in the numerical relativity ecosystem: **no existing open-source code simultaneously handles full CCZ4 spacetime evolution, GRMHD with high-resolution shock-capturing, M1 radiation transport, dynamic AMR up to 12 levels, and neutrino leakage, all within a single tightly-integrated framework.**

Codes like the Einstein Toolkit, SpECTRE, GRChombo, and AthenaK each excel in subsets of this capability space, but none address the full multi-physics problem at the fidelity required for next-generation multi-messenger astrophysics events such as:

- Simultaneous mergers of multiple supermassive black holes (SMBHs)
- BBH + neutron star environments in dense nuclear clusters
- Extreme mass-ratio inspirals with MHD jets and radiation

GRANITE is built to simulate precisely these scenarios, with the **B5\_star benchmark** (five 10⁸ M☉ SMBHs + two 4300 M☉ stars in a pentagon configuration) as the flagship scientific target.

### 1.2 Core Design Principles

These principles are **non-negotiable** and inform every architectural decision:

| Principle | Implementation |
|---|---|
| Scientific correctness before performance | Physics-exact implementations, not approximations |
| 100% unit test coverage from day one | GoogleTest suite, CI enforcement |
| Reproducibility | YAML-driven benchmarks, containerized environments |
| Maximum modularity, zero runtime overhead | Clean subsystem interfaces, no virtual dispatch in hot loops |
| Modern C++17 foundation | No C++20 until v1.0 (HPC cluster compatibility) |
| Exascale readiness | MPI + OpenMP now; CUDA/HIP roadmap explicit |

### 1.3 Intellectual Lineage

The code's theoretical and numerical lineage traces through several analytic predecessor frameworks:

```
NRCF → PRISM → SYNAPSE → AUE → GRANITE (v0.6.5) → GRAVITAS-X (future)
```

NRCF and PRISM provide analytic benchmark numbers (GW energy, peak frequency, shock temperatures, spin bounds) against which GRANITE simulation outputs are continuously validated.

---

## 2. Repository Structure

```text
GRANITE/
│
├── 📄 README.md                        # Project overview, benchmarks, quick-start, and documentation index.
├── 📄 CHANGELOG.md                     # Complete engineering audit trail — every fix, milestone, and architectural decision (2,331 lines).
├── 📄 CITATION.cff                     # Machine-readable citation metadata (CFF v1.2) — ORCID, Zenodo DOI, preferred reference.
├── 📄 CMakeLists.txt                   # Master CMake build system: MPI, OpenMP, HDF5, CUDA/HIP, Google Test.
├── 📄 LICENSE                          # GNU General Public License v3.0-or-later.
├── 📄 pyproject.toml                   # Python package metadata for `granite_analysis` (pip install -e .).
│
├── 📁 .github/                         # GitHub automation and community governance.
│   ├── 📁 workflows/
│   │   ├── ci.yml                      # CI matrix: GCC-12 × Clang-18 × Debug/Release — build, test, coverage.
│   │   ├── codeql.yml                  # Automated static security analysis via GitHub CodeQL.
│   │   └── .codecov.yml                # Coverage upload configuration for Codecov.io.
│   ├── CONTRIBUTING.md                 # Contribution guide: PR workflow, coding standards, test requirements.
│   ├── CODE_OF_CONDUCT.md              # Community standards and enforcement policy.
│   └── SECURITY.md                     # Vulnerability disclosure and responsible reporting policy.
│
├── 📁 benchmarks/                      # Self-contained simulation presets (YAML config + expected output).
│   ├── 📁 single_puncture/
│   │   └── params.yaml                 # Standard 3-D moving-puncture Schwarzschild stability benchmark (t=500 M).
│   ├── 📁 B2_eq/
│   │   └── params.yaml                 # Equal-mass (M=1.0) binary BH merger — inspiral + ringdown (t=500 M).
│   ├── 📁 B5_star/
│   │   └── params.yaml                 # Flagship: 5 SMBHs (10⁸ M☉) + 2 ultra-massive stars — v1.0 production target.
│   ├── 📁 gauge_wave/
│   │   └── params.yaml                 # 1-D sinusoidal gauge validation for CCZ4 advection stability.
│   ├── 📁 scaling_tests/
│   │   ├── slurm_submit.sh             # SLURM job template for Tier-1 HPC strong/weak scaling.
│   │   ├── pbs_submit.sh               # PBS/Torque equivalent for legacy cluster schedulers.
│   │   └── README.md                   # HPC deployment guide and expected throughput targets.
│   └── validation_tests.yaml           # Master validation suite: expected ‖H‖₂ bounds per benchmark config.
│
├── 📁 containers/                      # Container definitions for reproducible HPC deployments.
│   ├── Dockerfile                      # Docker multi-stage image (Ubuntu 22.04, HDF5 1.12, OpenMPI 4.1).
│   └── granite.def                     # Singularity/Apptainer definition for cluster environments.
│
├── 📁 docs/                            # Permanent technical reference documentation.
│   │
│   ├── 📄 DEVELOPER_GUIDE.md           # Complete developer reference: architecture, all 22 CCZ4 variables,
│   │                                   # physics formulations, data structures, coding standards, HPC guidelines.
│   ├── 📄 BENCHMARKS.md                # Full benchmark report: raw telemetry tables, constraint norm time
│   │                                   # series, resolution convergence, and hardware profiles.
│   ├── 📄 COMPARISON.md                # Source-cited, per-feature comparison vs. Einstein Toolkit, GRChombo,
│   │                                   # SpECTRE, and AthenaK.
│   ├── 📄 SCIENCE.md                   # Physics motivation, governing equations, B5_star scenario description,
│   │                                   # GRANITE's place in the NR landscape, and multi-messenger context.
│   ├── 📄 VISION.md                    # Long-term roadmap: YAML revolution, VORTEX live telemetry, v1.0 goals.
│   ├── 📄 PERSONAL_NOTE.md             # A direct address to the community on the philosophy behind GRANITE.
│   ├── 📄 COMMUNITY_SECTION.md         # Contributing guidelines and community engagement details.
│   ├── 📄 FAQ.md                       # Frequently asked questions — science, engineering, and HPC (15 answered).
│   ├── 📄 INSTALL.md                   # A-to-Z installation guide per OS and terminal environment.
│   ├── 📄 INSTALLATION.md              # Extended installation reference with dependency troubleshooting.
│   ├── 📄 WINDOWS_README.md            # Windows-specific setup guide (native PowerShell, Conda, WSL2).
│   ├── 📄 DEPLOYMENT_AND_PERFORMANCE.md# HPC deployment guide: NUMA binding, MPI ranks, Lustre I/O tuning.
│   ├── 📄 diagnostic_handbook.md       # Simulation health reference: lapse lifecycle, ‖H‖₂ interpretation,
│   │                                   # NaN forensics, and the pre-flight Health Check Checklist.
│   ├── 📄 v0.6.5_master_dictionary.md  # Exhaustive technical reference: every CLI flag, YAML parameter,
│   │                                   # C++ constant, CMake option, and Stability Patch forensic records.
│   ├── 📄 citation.bib                 # BibTeX entry for citing GRANITE in LaTeX documents.
│   ├── 📄 conf.py                      # Sphinx documentation configuration (Breathe + autodoc).
│   ├── 📄 index.rst                    # Sphinx master documentation index.
│   │
│   ├── 📁 paper/                       # Technical preprint — in preparation for Physical Review D.
│   │   ├── granite_preprint_v067.tex   # Full LaTeX source (1,709 lines): CCZ4/GRMHD/VORTEX formalism,
│   │   │                               # validated benchmarks, known limitations, B5_star scenario.
│   │   ├── granite_preprint_v067.pdf   # Compiled PDF — current draft, freely distributable.
│   │   └── 📁 figures/                 # All 13 publication-quality figures (300 dpi PDF, real devlog data).
│   │       ├── fig1_single_puncture.pdf      # SP ‖H‖₂ + lapse, 3 resolutions, ×84.8 reduction annotation.
│   │       ├── fig2_binary_bbh.pdf           # BBH ‖H‖₂ + lapse, real data points + monotonic decay.
│   │       ├── fig3_constraint_comparison.pdf# Normalised constraint reduction: SP vs BBH comparison.
│   │       ├── fig4_scaling.pdf              # OpenMP speedup + parallel efficiency (1–6 threads).
│   │       ├── fig5_amr_schematic.pdf        # Nested AMR hierarchy schematic with tracking spheres.
│   │       ├── fig6_amr_evolution.pdf        # Live AMR block count evolution (real devlog data).
│   │       ├── fig7_architecture.pdf         # Software architecture: RK3→modules→AMR→infrastructure.
│   │       ├── fig8_bbh_diagnostics.pdf      # BBH convergence summary bar chart.
│   │       ├── fig9_bbh_comprehensive.pdf    # BBH 4-panel: ‖H‖₂, lapse, AMR blocks, throughput.
│   │       ├── fig10_trumpet_closeup.pdf     # Single-puncture trumpet transition zoom (t ≤ 20 M).
│   │       ├── fig11_sp_comprehensive.pdf    # SP 4-panel: ‖H‖₂, lapse, AMR blocks, throughput.
│   │       ├── fig12_throughput.pdf          # M/s throughput evolution across all 5 benchmark runs.
│   │       ├── fig13_walltime.pdf            # Wall-time vs simulation time (all benchmarks).
│   │       └── generate_figures.py           # Reproducible figure generation script from raw devlog data.
│   │
│   ├── 📁 theory/
│   │   └── ccz4.rst                    # CCZ4 physics derivations and notation reference (Sphinx source).
│   └── 📁 user_guide/
│       └── installation.rst            # End-user installation tutorial (Sphinx source).
│
├── 📁 include/granite/                 # Public C++ interface headers — indexed by subsystem.
│   ├── 📁 core/
│   │   ├── grid.hpp                    # GridBlock: field-major 3-D data structure, ghost zones, MPI buffers.
│   │   └── types.hpp                   # Type aliases (Real, DIM), physical constants, variable enumerations.
│   ├── 📁 spacetime/
│   │   └── ccz4.hpp                    # CCZ4Evolution: RHS, constraint monitoring, KO dissipation, gauge driver.
│   ├── 📁 amr/
│   │   └── amr.hpp                     # AMRHierarchy: Berger-Oliger subcycling, tracking spheres, regridding.
│   ├── 📁 grmhd/
│   │   ├── grmhd.hpp                   # GRMHDEvolution: Valencia flux loop, HLLE/HLLD, PLM/MP5/PPM, con2prim.
│   │   └── tabulated_eos.hpp           # EquationOfState base + IdealGasEOS + TabulatedNuclearEOS interface.
│   ├── 📁 radiation/
│   │   └── m1.hpp                      # M1Transport: grey moment closure, Minerbo Eddington factor, IMEX source.
│   ├── 📁 neutrino/
│   │   └── neutrino.hpp                # NeutrinoLeakage: hybrid leakage + M1 for νe, ν̄e, νx transport.
│   ├── 📁 horizon/
│   │   └── horizon_finder.hpp          # ApparentHorizonFinder: flow-method expansion zero-finding (Gundlach 1998).
│   ├── 📁 initial_data/
│   │   └── initial_data.hpp            # Brill-Lindquist, Bowen-York, Two-Punctures, TOV polytrope, gauge wave.
│   ├── 📁 io/
│   │   └── hdf5_io.hpp                 # HDF5Writer/Reader: parallel MPI-IO, writeCheckpoint(), readCheckpoint().
│   └── 📁 postprocess/
│       └── postprocess.hpp             # Psi4Extractor: NP Ψ₄ on extraction spheres, GW strain, recoil kick.
│
├── 📁 src/                             # C++17 physics kernels and engine entry point (~8,918 lines total).
│   ├── main.cpp                        # Engine entry point: YAML load, AMR init, SSP-RK3 time loop (1,231 ln).
│   │                                   # NaN forensics, Sommerfeld BCs, puncture tracking, diagnostics output.
│   ├── 📁 core/
│   │   └── grid.cpp                    # GridBlock implementation: packBoundary/unpackBoundary MPI buffers (115 ln).
│   ├── 📁 spacetime/
│   │   └── ccz4.cpp                    # CCZ4 RHS: full conformal Ricci tensor, physical Laplacian of lapse,   (1,158 ln)
│   │                                   # χ-blended upwind advection, KO dissipation, constraint monitoring.
│   ├── 📁 amr/
│   │   └── amr.cpp                     # AMR hierarchy: dynamic Berger-Oliger subcycling, iterative union-merge,  (722 ln)
│   │                                   # gradient tagger, puncture tracking spheres, live per-step regridding.
│   ├── 📁 grmhd/
│   │   ├── grmhd.cpp                   # Valencia GRMHD: PLM/MP5/PPM reconstruction, HLLE Riemann solver,        (1,014 ln)
│   │   │                               # Palenzuela con2prim NR, geometric source terms, atmosphere floors.
│   │   ├── hlld.cpp                    # Full 7-wave HLLD Riemann solver + upwind constrained transport CT.       (476 ln)
│   │   └── tabulated_eos.cpp           # Nuclear EOS: trilinear interpolation, NR temperature inversion,          (707 ln)
│   │                                   # β-equilibrium Ye solver, ideal gas + polytropic fallbacks.
│   ├── 📁 radiation/
│   │   └── m1.cpp                      # Grey M1 radiation: Minerbo closure, IMEX source integration,             (416 ln)
│   │                                   # GR lapse/shift corrections, Eddington tensor. [RK3 coupling: v0.7]
│   ├── 📁 neutrino/
│   │   └── neutrino.cpp                # Hybrid leakage-M1: URCA, pair annihilation, optical depth integration,   (411 ln)
│   │                                   # dYe/dt β-process rates. [RK3 coupling: v0.7]
│   ├── 📁 horizon/
│   │   └── horizon_finder.cpp          # Apparent horizon finder: null expansion θ⁺, flow iteration,              (565 ln)
│   │                                   # multi-BH detection, common horizon, recoil estimation.
│   ├── 📁 initial_data/
│   │   └── initial_data.cpp            # BL conformal factor, BY NR solver, Two-Punctures spectral,               (957 ln)
│   │                                   # TOV ODE integrator, gauge wave, polytrope star builder.
│   ├── 📁 io/
│   │   └── hdf5_io.cpp                 # Parallel HDF5 I/O: grid snapshots, full checkpoint write/read,           (497 ln)
│   │                                   # time-series diagnostics, simulation metadata serialisation.
│   └── 📁 postprocess/
│       └── postprocess.cpp             # Ψ₄ GW extraction: NP tetrad, spin-weighted harmonics (ℓ≤4),              (649 ln)
│                                       # fixed-frequency strain integration, radiated energy/momentum.
│
├── 📁 tests/                           # 92-test GoogleTest suite — 100% pass rate on GCC-12 and Clang-18.
│   ├── CMakeLists.txt                  # CTest integration for all 10 test files.
│   ├── 📁 core/
│   │   ├── test_types.cpp              # TypesTest (7): symIdx, variable counts, physical constants, units.
│   │   └── test_grid.cpp               # GridBlockTest (13) + BufferTest (5) + FlatLayoutTest (4) — 22 total.
│   ├── 📁 spacetime/
│   │   ├── test_ccz4_flat.cpp          # CCZ4FlatTest (10): RHS=0 on flat, KO dissipation, upwind blending.
│   │   └── test_gauge_wave.cpp         # GaugeWaveTest (4): initialization, RHS bounds, matter-source neutrality.
│   ├── 📁 grmhd/
│   │   ├── test_ppm.cpp                # PPMTest (5): parabolic recovery, discontinuity sharpness, monotonicity.
│   │   ├── test_hlld_ct.cpp            # HLLDTest (4) + CTTest (3): MHD shock fluxes, ∇·B preservation.
│   │   ├── test_grmhd_gr.cpp           # GRMHDGRTest (5): HLLE in curved metric, MP5 reconstruction.
│   │   └── test_tabulated_eos.cpp      # IdealGasLimitTest (5) + ThermodynamicsTest (5) +
│   │                                   # InterpolationTest (5) + BetaEquilibriumTest (5) — 20 total.
│   └── 📁 initial_data/
│       ├── test_brill_lindquist.cpp    # BrillLindquistTest (5): single/binary/5-BH conformal factor.
│       └── test_polytrope.cpp          # PolytropeTest (7): Lane-Emden, TOV solver, density/pressure monotonicity.
│
├── 📁 python/                          # Installable Python analysis package (pip install -e .).
│   └── 📁 granite_analysis/
│       ├── __init__.py                 # Package exports and version.
│       ├── reader.py                   # HDF5 grid reader: load snapshots, reconstruct AMR hierarchy (104 ln).
│       ├── gw.py                       # GW strain extraction: Ψ₄ time integration, fixed-frequency filter (506 ln).
│       └── plotting.py                 # Matplotlib helpers: constraint plots, lapse evolution, GW waveforms (155 ln).
│
├── 📁 scripts/                         # Python build/run orchestration wrappers.
│   ├── run_granite.py                  # Unified CLI: build / run / clean / format / dev subcommands.
│   │                                   # 'dev' subcommand: build → run → stream to granite_analysis dashboard.
│   │                                   # 'dev --watch': auto-rebuild and restart on src/ changes.
│   ├── run_granite_hpc.py              # HPC launch wrapper: NUMA overrides, MPI ranks, AMR telemetry,
│   │                                   # --slurm flag generates and submits sbatch scripts piped to sim_tracker.
│   ├── health_check.py                 # Pre-flight verifier: Release flags, OMP core count, memory, HDF5.
│   └── setup_windows.ps1               # One-click Windows dependency installer (vcpkg + HDF5 + MPI).
│
│   ⚠ NOTE: sim_tracker.py, dev_benchmark.py, and dev_stability_test.py have been permanently removed.
│     Their logic is now in the `granite_analysis` package (python/granite_analysis/cli/).
│     Invoke via:
│       python3 -m granite_analysis.cli.sim_tracker [logfile]
│       python3 -m granite_analysis.cli.dev_benchmark [logfile] [--json out.json] [--csv out.csv]
│       python3 scripts/run_granite.py dev [--watch]
│
├── 📁 runs/                            # ⚠ gitignored — job scripts and parameter-scan configurations.
│
├── 📁 viz/                             # Visualization and post-processing.
│   ├── README.md                       # Documents planned plot_constraints.py, plot_gw.py, plot_amr.py.
│   └── 📁 vortex_eternity/             # VORTEX: standalone browser-native N-body physics engine.
│       ├── index.html                  # Complete self-contained VORTEX engine (~428 KB, zero dependencies).
│       │                               # 4th-order Hermite PC integrator · 2.5PN radiation reaction
│       │                               # Lense-Thirring frame-dragging · GLSL gravitational lens shader
│       │                               # GW audio sonification · Minimap 3.0 · Zen Mode · Cinematic Autopilot
│       │                               # Zero-allocation architecture — sustained 60 FPS in any modern browser.
│       └── README.md                   # VORTEX architecture, physics engine, and v1.0 coupling roadmap.
```

---

## 3. Architecture Overview

### 3.1 High-Level Data Flow

```
YAML Benchmark File
        │
        ▼
Parameter Parser (params.yaml)
        │
        ▼
Initial Data Generator ──────────────────────────────────────────────┐
  [Brill-Lindquist | Bowen-York | Two-Punctures | TOV]               │
        │                                                             │
        ▼                                                             │
AMR Grid Hierarchy (Berger-Oliger, up to 12 levels)                  │
        │                                                             │
        ▼                                                             │
┌────────────────────────────────────────────────────────────┐        │
│                  Time Evolution Loop (RK3)                 │        │
│                                                            │        │
│  ┌─────────────────────────────────────────────────────┐  │        │
│  │  Stage k (k = 1, 2, 3)                              │  │        │
│  │                                                     │  │        │
│  │  1. Compute CCZ4 RHS                                │  │        │
│  │     · 4th-order FD spatial derivatives              │  │        │
│  │     · CCZ4 constraint damping terms                 │  │        │
│  │     · 1+log slicing + Gamma-driver gauge            │  │        │
│  │     · KO dissipation (σ = 0.1)                      │  │        │
│  │                                                     │  │        │
│  │  2. Compute GRMHD RHS                               │  │        │
│  │     · MP5/PPM/PLM reconstruction                    │  │        │
│  │     · HLLE/HLLD Riemann fluxes                      │  │        │
│  │     · CT for ∇·B = 0                                │  │        │
│  │     · C2P via Newton-Raphson                        │  │        │
│  │                                                     │  │        │
│  │  3. Compute Radiation RHS (M1)                      │  │        │
│  │     · M1 moment closure                             │  │        │
│  │     · Neutrino leakage source terms                 │  │        │
│  │                                                     │  │        │
│  │  4. SSP-RK3 update                                  │  │        │
│  │                                                     │  │        │
│  └─────────────────────────────────────────────────────┘  │        │
│                          │                                 │        │
│                          ▼                                 │        │
│           AMR Refinement + Regridding                      │        │
│           Ghost Zone Exchange (MPI)                        │        │
│                          │                                 │        │
│                          ▼                                 │        │
│           Diagnostics + GW Extraction                      │        │
│           Checkpoint (every N steps, HDF5)                 │        │
│                                                            │        │
└────────────────────────────────────────────────────────────┘        │
                           │                                          │
                           └── Post-Processing (Python / granite_analysis)
```

### 3.2 Subsystem Coupling

| Interface | From | To | Via |
|---|---|---|---|
| Evolved metric | CCZ4 | GRMHD | `GRMetric3` |
| Stress-energy | GRMHD | CCZ4 | `StressEnergyTensor3` |
| Radiation sources | M1 | GRMHD | Source terms in Valencia |
| Grid metadata | AMR | All | `GridBlock` hierarchy |
| Constraint norms | CCZ4 | Diagnostics | `ConstraintMonitor` |

**Critical rule:** `GRMetric3` is the **only** public interface between the CCZ4 spacetime module and the GRMHD module. Direct access to CCZ4 internal variables from GRMHD code is forbidden.

---

## 4. Core Data Structures

### 4.1 `GridBlock`

The fundamental compute unit. Represents a single uniform Cartesian patch with its own ghost zone halo.

**Memory layout (field-major, flat allocation):**

```cpp
// data_[var * stride + flat(i,j,k)]
// where flat(i,j,k) = i*ny*nz + j*nz + k
// and stride = (nx+2*nghost)*(ny+2*nghost)*(nz+2*nghost)

class GridBlock {
    std::vector<Real> data_;   // SINGLE flat allocation (see H2)
    int nx_, ny_, nz_;
    int nghost_ = 4;           // 4 ghost zones for 4th-order FD
    int nvar_;
    Real dx_, dy_, dz_;
    Real x0_, y0_, z0_;        // Origin of this block (including ghosts)
};
```

**Access pattern:**

```cpp
// Preferred: via accessor inline
inline Real& GridBlock::at(int var, int i, int j, int k) {
    return data_[var * stride_ + (i + nghost_) * ny_stride_
                               + (j + nghost_) * nz_stride_
                               + (k + nghost_)];
}
// i, j, k are interior-relative (0 to nx-1, etc.)
// Ghost zone: i in [-nghost, -1] ∪ [nx, nx+nghost-1]
```

**Architecture decisions (immutable):**

- Field-major layout (`data_[var*stride + flat(i,j,k)]`) is chosen for RHS loop vectorization: all spatial points of one variable are contiguous.
- Single flat allocation (not `vector<vector<Real>>`) eliminates pointer-chasing and enables SIMD (fixed bug H2).
- `nghost = 4` throughout — never reduced, even for lower-order reconstructors.

### 4.2 `GRMetric3`

Public interface object populated by CCZ4 and consumed by GRMHD.

```cpp
struct GRMetric3 {
    // Conformal decomposition: g_ij = χ^{-1} * γ̃_ij
    Real chi;               // Conformal factor
    Real gamma_tilde[3][3]; // Conformal spatial metric
    Real K;                 // Trace of extrinsic curvature
    Real A_tilde[3][3];     // Traceless part of Ã_ij

    // Gauge
    Real alpha;             // Lapse
    Real beta[3];           // Shift vector
    Real Gamma_tilde[3];    // Contracted conformal Christoffel

    // Derived (computed on demand)
    Real gamma[3][3];       // Physical spatial metric (= γ̃/χ)
    Real gamma_inv[3][3];   // Inverse physical metric
    Real sqrt_gamma;        // sqrt(det(γ))
    Real K_ij[3][3];        // Full extrinsic curvature
};
```

### 4.3 CCZ4 Variable Layout (22 variables)

| Index | Symbol | Description |
|---|---|---|
| 0 | χ | Conformal factor |
| 1–6 | γ̃_{ij} | Conformal metric (symmetric, 6 components) |
| 7 | K | Trace of extrinsic curvature |
| 8–13 | Ã_{ij} | Traceless conformal extrinsic curvature |
| 14–16 | Γ̃^i | Conformal connection functions |
| 17 | α | Lapse |
| 18–20 | β^i | Shift vector |
| 21 | Θ | CCZ4 constraint variable |

### 4.4 GRMHD Conserved Variables (9 variables)

| Index | Symbol | Description |
|---|---|---|
| 0 | D | Conserved baryon density |
| 1–3 | S_i | Conserved momentum density |
| 4 | τ | Conserved energy density |
| 5–7 | B^i | Magnetic field (staggered, CT) |
| 8 | Y_e | Electron fraction |

---

## 5. Physics Formulations

### 5.1 Spacetime: CCZ4

GRANITE implements the **CCZ4 formulation** of the Einstein equations (Alic et al. 2012, Phys.Rev.D 85, 064040). CCZ4 extends BSSN by promoting the algebraic constraints to dynamical fields, enabling active constraint damping with exponential decay rates.

**Evolution equations (schematic):**

```
∂_t χ       = β^i ∂_i χ + (2/3) χ α K − (2/3) χ ∂_i β^i
∂_t γ̃_{ij} = β^k ∂_k γ̃_{ij} − 2α Ã_{ij} + ... (Lie derivative terms)
∂_t K       = β^i ∂_i K − D_i D^i α + α(Ã_{ij}Ã^{ij} + K²/3) − κ₁(1+κ₂)αΘ + 4πα(ρ+S)
∂_t Θ       = β^i ∂_i Θ + (1/2)α(R − Ã_{ij}Ã^{ij} + (2/3)K² − 2Λ) − αΓ̂ − κ₁(2+κ₂)αΘ
```

**Constraint damping parameters (production defaults):**

```yaml
ccz4:
  kappa1: 0.02   # Constraint damping coefficient
  kappa2: 0.0    # κ₂ = 0: standard CCZ4 (not Z4c variant)
  eta:    2.0    # Gamma-driver shift damping
```

### 5.2 Gauge Conditions

**Lapse:** 1+log slicing

```
∂_t α = β^i ∂_i α − 2 α K
```

This gauge is singularity-avoiding: the lapse collapses near punctures (α → 0), preventing the evolution from reaching the physical singularity.

**Shift:** Moving punctures Gamma-driver

```
∂_t β^i = (3/4) B^i
∂_t B^i = ∂_t Γ̃^i − η B^i
```

The η parameter controls the speed of shift adjustment. η = 2.0 is the standard production value.

**Trumpet gauge:** At sufficient resolution and with correct KO dissipation (σ = 0.1), the lapse profile forms a trumpet geometry near each puncture. This is the correct end state. If the trumpet is unresolved (e.g., dx = 0.75M at 128³), α will not drop to the expected floor — this is a resolution effect, not a bug.

### 5.3 GRMHD: Valencia Formulation

The matter sector evolves the conservative variables {D, S_i, τ, B^i, Y_e} via:

```
∂_t U + ∂_i F^i(U) = S(U, g_{μν})
```

where U is the conserved vector, F^i are fluxes, and S contains all geometric source terms including couplings to the spacetime curvature.

The **primitive variables** {ρ, v^i, ε, P, B^i} are recovered from conserved variables at each RK3 stage via Newton-Raphson root-finding (C2P step).

### 5.4 Magnetic Field: Constrained Transport

The ∇·B = 0 condition is enforced via **Constrained Transport** (Evans & Hawley 1988). The magnetic field is stored on cell faces (staggered grid), and the CT update ensures that ∇·B = 0 is preserved to machine precision at all times, not just approximately.

### 5.5 Equation of State

Two EOS modes are available:

| Mode | Usage | Implementation |
|---|---|---|
| Ideal gas | Development, validation | γ = 4/3 (for SMBH mergers); sound speed is exact (fixed bug C1) |
| Tabulated nuclear | Future neutron star runs | Tri-linear interpolation in (ρ, T, Y_e) space |

**Critical:** The EOS sound speed is always computed exactly from the EOS, never from a hardcoded γ (this was fixed bug C1).

### 5.6 Radiation Transport: M1 + Leakage

The radiation module uses the **M1 moment closure** scheme (grey, frequency-integrated). In M1, the radiation field is described by its energy density E and flux F^i, closed by an analytic Eddington tensor.

Neutrino leakage source terms couple the radiation to the fluid via:

```
Q_ν = −κ_a (E − E_eq)   [absorption / emission]
R_ν = (source term in electron fraction Y_e evolution)
```

**Status (v0.6.7):** The M1 module is implemented and tested but not yet wired into the main RK3 evolution loop. It will be activated in v0.7.

---

## 6. Numerical Methods

### 6.1 Spatial Derivatives: 4th-Order Finite Difference

All spatial derivatives are computed to 4th-order accuracy using standard centered stencils:

```
∂_x f|_i = (−f_{i+2} + 8f_{i+1} − 8f_{i−1} + f_{i−2}) / (12 Δx)   [4th-order centered]
```

This requires `nghost = 4` ghost zones per face to accommodate the full stencil (2 points on each side for the 4th-order operator, extended to 4 for safety with advection terms at higher resolution).

### 6.2 Reconstruction: MP5 / PPM / PLM

GRMHD interface values are reconstructed from cell centers using one of three schemes, configurable per run:

| Scheme | Order | Cost | Recommended for |
|---|---|---|---|
| PLM | 2nd | Low | Quick tests, low resolution |
| PPM | 3rd | Medium | Standard production runs |
| MP5 | 5th | High | High-resolution, convergence tests |

MP5 (Monotonicity-Preserving 5th-order, Suresh & Huynh 1997) is the default for production runs.

### 6.3 Riemann Solvers: HLLE / HLLD

| Solver | Physics | Notes |
|---|---|---|
| HLLE | MHD with actual GR metric | Fixed bug C3: uses real metric, not flat dummy |
| HLLD | MHD with intermediate states | Miyoshi & Kusano 2005; preferred for MHD accuracy |

**Critical (C3):** The HLLE solver uses the actual curved-space metric to compute wave speeds. Using a flat-space approximation was a known bug that has been permanently fixed.

### 6.4 Time Integration: SSP-RK3

The Shu-Osher 3rd-order Strong-Stability-Preserving Runge-Kutta scheme:

```
U^(1) = U^n + Δt L(U^n)
U^(2) = (3/4) U^n + (1/4) [U^(1) + Δt L(U^(1))]
U^(n+1) = (1/3) U^n + (2/3) [U^(2) + Δt L(U^(2))]
```

SSP-RK3 is total-variation-diminishing (TVD) under appropriate CFL conditions and is the industry standard for HRSC methods in numerical relativity.

**CFL condition:**

```yaml
time_integration:
  cfl: 0.25     # Global CFL safety factor
                # Note: CFL at finest AMR level ≤ 0.5 required for stability
                # with current lapse suppression compensation
```

### 6.5 Kreiss-Oliger Dissipation

Numerical high-frequency noise is controlled by Kreiss-Oliger (KO) dissipation added to all CCZ4 right-hand sides:

```
(∂_t u)_KO = −σ * (Δx)^{2p−1} * D^{2p}_+ u   [6th-order, p=3]
```

**Critical parameter:**

```yaml
dissipation:
  ko_sigma: 0.1   # SAFE DEFAULT — do not increase above this value
```

Values of `ko_sigma > 0.1` (e.g., 0.35) have been confirmed in testing to **over-dissipate the trumpet gauge profile**, causing secondary gauge collapse without NaN events. This is a documented failure mode in the CHANGELOG and must not be reintroduced.

---

## 7. Initial Data

### 7.1 Two-Punctures / Bowen-York (Binary Black Holes)

BBH initial data is generated using the **Two-Punctures** method (Brandt & Brügmann 1997), which provides a conformally flat, maximal slicing solution for two Schwarzschild-like black holes with specified momenta and spins.

**Key parameters for quasi-circular orbit:**

```yaml
initial_data:
  type: two_punctures
  bh1:
    mass: 0.5          # ADM mass in code units (M_total = 1)
    position: [5.0, 0.0, 0.0]
    momentum: [0.0, 0.0840, 0.0]   # Tangential momentum for d=10M separation
    spin: [0.0, 0.0, 0.0]
  bh2:
    mass: 0.5
    position: [-5.0, 0.0, 0.0]
    momentum: [0.0, -0.0840, 0.0]  # Equal and opposite
    spin: [0.0, 0.0, 0.0]
```

**Critical:** Zero tangential momentum (`momentum: [0.0, 0.0, 0.0]`) produces a head-on collision, not an inspiral. The quasi-circular tangential momenta must be computed from PN approximations. For a d = 10M equal-mass BBH: p_t ≈ ±0.0840 per black hole.

### 7.2 Brill-Lindquist Initial Data

Brill-Lindquist data uses a simple conformal factor sum for N black holes at rest:

```
ψ_BL = 1 + Σ_i (m_i / 2r_i)
```

**Important limitation:** Sommerfeld boundary conditions are **incompatible** with Brill-Lindquist data. Use copy (flat-space) boundary conditions with BL initial data — this has been confirmed experimentally (8× worse constraint violations with Sommerfeld + BL). See CHANGELOG.

### 7.3 TOV Solver (Neutron Stars)

The Tolman-Oppenheimer-Volkoff equations are integrated for isolated neutron star initial data:

```
dP/dr = −(ρ + P)(m + 4πr³P) / [r(r − 2m)]
dm/dr = 4π r² ρ
```

**Critical:** The TOV solver uses `1e5 cm/km` for unit conversion (not `RSUN_CGS`). Using the solar radius in place of the km→cm conversion factor was a known bug that has been fixed.

---

## 8. AMR Engine

### 8.1 Berger-Oliger with Subcycling

GRANITE's AMR follows the Berger-Oliger (1984) approach:

- The domain is a hierarchy of nested `GridBlock` patches at refinement levels ℓ = 0, 1, …, ℓ_max
- Each level has its own timestep: Δt_ℓ = Δt_0 / 2^ℓ
- Refinement/coarsening are applied recursively using subcycling

**Refinement criteria (configurable):**

```yaml
amr:
  levels: 6              # Max AMR levels in production
  refinement:
    criteria:
      - variable: chi
        threshold: 0.15  # Refine where conformal factor drops below
      - variable: rho
        threshold: 1e-4  # Refine in dense matter
      - variable: alpha
        threshold: 0.3   # Refine near punctures (collapsing lapse)
```

### 8.2 Prolongation (Coarse → Fine)

When a new fine patch is created, values are prolonged from the coarse parent using **trilinear interpolation**:

```
f(x, y, z) = Σ_{ijk} c_{ijk} * f_{i,j,k}   [trilinear in (ξ, η, ζ) ∈ [0,1]³]
```

This is second-order accurate in space, which is consistent with the requirement that AMR interpolation errors not exceed the global truncation error.

### 8.3 Restriction (Fine → Coarse)

Fine-level data is injected back to the coarse level using **volume-weighted restriction**:

```
f_coarse = (1/8) Σ_{children} f_fine   [in 3D, 8 fine cells per coarse cell]
```

Volume weighting ensures conservation of extensive quantities (mass, momentum) across level boundaries.

### 8.4 Ghost Zone Filling

Ghost zones at refinement boundaries are filled by:
1. **MPI exchange** for same-level neighbors on different ranks
2. **Prolongation** from the coarser parent level for inter-level ghosts

Ghost zone filling order within the RK3 loop:
1. Fill from same-level MPI neighbors (non-blocking `MPI_Isend`/`MPI_Irecv`)
2. Fill from coarser level via prolongation
3. Apply boundary conditions (outermost ghosts)

### 8.5 Dynamic Regridding (v0.6.7 Status)

Dynamic regridding is **fully implemented** in v0.6.7. Gradient-based and 
puncture-tracking triggers fire per step via `AMRHierarchy::subcycle()`, 
with iterative union-merge box aggregation and live regridding integrated 
into the main RK3 loop.

---

## 9. Boundary Conditions

### 9.1 Sommerfeld (Outgoing Wave) BCs

Sommerfeld radiation-absorbing boundary conditions are applied to all CCZ4 variables at the outer boundary when the domain is large enough:

```
∂_t u + (x/r) ∂_r u + (u − u_∞) / r = 0
```

This enforces outgoing wave behavior and suppresses gauge reflections from the outer boundary.

**Critical domain size requirement:** Gauge waves travel at speed √2 in the CCZ4 gauge. The boundary reflection travel time is:

```
t_reflection = domain_half / √2
```

If `t_reflection < t_simulation`, gauge reflections contaminate the interior. For stable production runs, the domain half-width must be at least `±48M` (tested and confirmed as safe for t ~ 500M simulations at dx = 0.75M).

**Sommerfeld BCs are incompatible with Brill-Lindquist data** — use copy BCs with BL ID.

### 9.2 Copy (Flat-Space) BCs

Simple copy of interior values to ghost cells. Required for BL initial data. Not suitable for long evolutions on small domains.

---

## 10. Diagnostics & GW Extraction

### 10.1 Gravitational Wave Extraction: Ψ₄

Gravitational waves are extracted via the **Newman-Penrose Weyl scalar Ψ₄**, decomposed into spin-weighted spherical harmonics:

```
Ψ₄(t, r) = Σ_{ℓ,m} Ψ₄^{ℓm}(t, r) _{-2}Y_{ℓm}(θ, φ)
```

Extraction is performed at multiple extraction radii r_ex ∈ {50, 100, 150, 200, 300, 500} r_g to enable extrapolation to null infinity (Nakano et al. 2015).

The GW strain h_{+,×} is recovered by double time-integration of Ψ₄:

```
h_{+} − i h_{×} = ∫∫ Ψ₄ dt dt   [fixed-frequency integration preferred]
```

### 10.2 Constraint Monitoring

The Hamiltonian and momentum constraint norms are monitored at every diagnostic output step:

```
‖H‖₂ = sqrt(∫ H² dV / V)      [L2 norm of Hamiltonian constraint]
‖M^i‖₂ = sqrt(∫ M_i M^i dV / V) [L2 norm of momentum constraints]
```

**Health thresholds (production):**

| Metric | Acceptable | Warning | Critical |
|---|---|---|---|
| ‖H‖₂ growth rate γ | < 0.005 /M | 0.005–0.02 /M | > 0.02 /M |
| ‖H‖₂ total change | < ×10 over 500M | ×10–×100 | > ×100 |
| NaN events | 0 | — | Any |

### 10.3 Apparent Horizon Finder

The apparent horizon is located by solving the expansion equation:

```
Θ = D_i n^i + K_{ij} n^i n^j − K = 0
```

on a trial surface, iterated until convergence. The AH finder runs every N_AH diagnostic steps (configurable, default N_AH = 10).

### 10.4 Phase Classification

Simulation phases are currently classified by time thresholds (a known limitation; separation-based classification is more physically accurate and is planned for v0.7):

| Phase | Time Range |
|---|---|
| Early Inspiral | t < 100M |
| Mid Inspiral | 100M ≤ t < 300M |
| Late Inspiral | t ≥ 300M |

---

## 11. I/O & Checkpointing

### 11.1 HDF5 Checkpoint Format

Checkpoints are written in parallel HDF5, one file per checkpoint:

```
checkpoint_XXXXXX.h5
├── /metadata
│   ├── time
│   ├── step
│   └── amr_level_count
├── /level_0
│   ├── ccz4_vars   [shape: (nblocks, 22, nx, ny, nz)]
│   └── grmhd_vars  [shape: (nblocks, 9, nx, ny, nz)]
└── /level_1
    ├── ccz4_vars   [shape: (nblocks, 22, nx, ny, nz)]
    └── grmhd_vars  [shape: (nblocks, 9, nx, ny, nz)]
```

**Checkpoint frequency (recommended):**

```yaml
io:
  checkpoint_every: 5000   # steps
  output_every: 100        # diagnostic output (constraints, GW) frequency
```

### 11.2 Restart (Status in v0.6.7)

`writeCheckpoint()` and `readCheckpoint()` are fully implemented in 
`src/io/hdf5_io.cpp`. The `--resume` CLI flag to invoke restart from 
`main.cpp` is pending implementation (v0.7 target).

---

## 12. MPI & OpenMP Parallelism

### 12.1 Domain Decomposition

The AMR block hierarchy is decomposed across MPI ranks using a **space-filling curve** (Hilbert curve) to maximize cache locality and minimize inter-rank communication volume.

Each MPI rank owns a contiguous set of `GridBlock` patches. Ghost zones shared between ranks are exchanged using non-blocking MPI:

```cpp
MPI_Isend(ghost_send_buffer, count, MPI_DOUBLE, dest_rank, tag, comm, &req);
MPI_Irecv(ghost_recv_buffer, count, MPI_DOUBLE, src_rank, tag, comm, &req);
MPI_Waitall(n_requests, requests, statuses);
```

### 12.2 OpenMP Threading

Within each MPI rank, `GridBlock` loops are parallelized with OpenMP:

```cpp
// KO dissipation: single OMP region (fixed bug H1)
#pragma omp parallel for collapse(3) schedule(static)
for (int var = 0; var < nvar; ++var)
    for (int i = 0; i < nx; ++i)
        for (int j = 0; j < ny; ++j)
            for (int k = 0; k < nz; ++k)
                rhs(var, i, j, k) += ko_term(var, i, j, k);
```

**Critical (H1):** KO dissipation must be applied in a **single OpenMP parallel region** over all 22 CCZ4 variables, not in 22 separate parallel regions. Spawning 22 separate thread teams was a confirmed bug causing race conditions.

### 12.3 RHS Loop Order (Performance-Critical)

The RHS computation must follow the canonical loop order:

```cpp
// CORRECT (spatial outer, variable inner — cache-friendly for field-major layout)
for (int i ...) for (int j ...) for (int k ...)
    for (int var ...) rhs(var, i, j, k) = ...;

// WRONG (variable outer, spatial inner — cache-thrashing)
for (int var ...) for (int i ...) for (int j ...) for (int k ...)
    rhs(var, i, j, k) = ...;
```

This loop order is fixed (bug H3) and must not be changed.

---

## 13. Development Environment Setup

### 13.1 Supported Platforms

| Platform | Status |
|---|---|
| Linux (native) | ✅ Fully supported |
| WSL2 on Windows | ✅ Supported (run from Linux filesystem, not `/mnt/c/`) |
| macOS | 🔶 Planned for v0.8+ |
| Windows native | 🔶 Planned for v0.8+ |

**WSL note:** Always run from a Linux-native filesystem path (e.g., `~/Granite/`), not from a Windows-mounted path (`/mnt/c/...`). Cross-filesystem performance is severely degraded and may cause intermittent MPI failures.

### 13.2 One-Command Bootstrap

```bash
git clone https://github.com/LiranOG/Granite-NR.git
cd Granite-NR
python3 scripts/run_granite.py setup --all
```

This script installs all dependencies, configures the build system, and runs the test suite to verify the installation.

### 13.3 Manual Dependencies

If the bootstrap script is not used, install manually:

| Dependency | Minimum Version | Notes |
|---|---|---|
| GCC or Clang | GCC ≥ 11 / Clang ≥ 14 | C++17 required |
| CMake | 3.22 | Modern target-based build |
| OpenMPI or MPICH | 4.0 | Tested with both |
| HDF5 | 1.12 (parallel) | Must be parallel-enabled |
| GoogleTest | 1.12 | Auto-downloaded by CMake |
| Python | 3.10+ | For analysis scripts |
| Python packages | — | `numpy`, `h5py`, `matplotlib`, `yt` |

---

## 14. Build System

### 14.1 Common Build Targets

```bash
# Standard builds
python3 scripts/run_granite.py build --release          # Optimized (-O3 -march=native)
python3 scripts/run_granite.py build --debug            # Full symbols + ASan + UBSan
python3 scripts/run_granite.py build --tests            # Build + run 92-test suite

# Code quality
python3 scripts/run_granite.py format                   # clang-format + cmake-format
python3 scripts/run_granite.py health_check             # Pre-simulation validator

# Direct CMake (alternative)
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGRANITE_ENABLE_MPI=ON
cmake --build build -j$(nproc)
ctest --test-dir build --output-on-failure
```

### 14.2 CMake Options

| Option | Default | Description |
|---|---|---|
| `GRANITE_ENABLE_MPI` | ON | MPI parallelism |
| `GRANITE_ENABLE_OMP` | ON | OpenMP threading |
| `GRANITE_ENABLE_HDF5` | ON | HDF5 I/O + checkpointing |
| `GRANITE_ENABLE_CUDA` | OFF | CUDA GPU kernels (not yet available) |
| `GRANITE_ENABLE_SANITIZERS` | OFF | ASan + UBSan (Debug builds only) |

### 14.3 Developer Benchmark

A full end-to-end correctness and performance benchmark runs in under 5 minutes on a typical development machine (Intel i5-8400 class):

```bash
# Integrated pipeline
python3 scripts/run_granite.py dev

# Or direct invocation on a log / stdin
python3 -m granite_analysis.cli.dev_benchmark
```

The benchmark runs a 128³ single-puncture stability test and a short equal-mass BBH evolution, reporting constraint norms and timing. This must pass before any PR.

---

## 15. Coding Standards & Style Guide

### 15.1 Language & Standard

- **C++17** exclusively. No C++20 features until v1.0 (ensures compatibility with HPC cluster compilers as of 2026).
- No exceptions in C++ code (performance + HPC portability). Use `GRANITE_ASSERT(cond, msg)` and return codes.
- No `std::cout` in library code — use the `Logger` class which is MPI-rank-aware.

### 15.2 Naming Conventions

| Category | Convention | Examples |
|---|---|---|
| Namespaces | `snake_case` | `granite::`, `granite::spacetime`, `granite::grmhd` |
| Classes | `PascalCase` | `GridBlock`, `GRMetric3`, `CCZ4Solver` |
| Functions | `camelCase` | `computeRHS()`, `fillGhostZones()` |
| Variables | `snake_case` | `conformal_factor`, `dt_local` |
| Constants | `UPPER_SNAKE` | `MAX_AMR_LEVELS`, `NGHOST` |
| Template parameters | Single uppercase | `T`, `Real`, `N` |

### 15.3 Header Guidelines

```cpp
// CORRECT
namespace granite::spacetime {
class CCZ4Solver {
  public:
    /// @brief Compute the full CCZ4 RHS into rhs_block.
    /// @param state Current state GridBlock
    /// @param rhs Output RHS GridBlock (must be pre-allocated)
    /// @param metric GRMetric3 computed from state
    void computeRHS(const GridBlock& state,
                    GridBlock& rhs,
                    const GRMetric3& metric) noexcept;
};
} // namespace granite::spacetime

// FORBIDDEN in public headers
using namespace granite;  // Never pollute the global namespace
```

### 15.4 Physical Quantities

- Always document physical units in comments: `// [code units: M_total = 1, G = c = 1]`
- Never mix unit systems silently. Conversions must be explicit and commented.
- Physical constants must be in `include/granite/constants.hpp`, never magic numbers.

### 15.5 Formatting

Enforced by `.clang-format` (LLVM style, 100-character line limit). Run before every commit:

```bash
python3 scripts/run_granite.py format
```

---

## 16. Testing Philosophy & Workflow

### 16.1 Zero-Tolerance Policy

**All PRs must maintain 100% test pass rate.** A failing test blocks merge, no exceptions.

### 16.2 Test Categories

| Category | Location | Run Command |
|---|---|---|
| Unit tests | `tests/` | `ctest --test-dir build` |
| Integration tests | `granite_analysis.cli.dev_benchmark` | `python3 -m granite_analysis.cli.dev_benchmark` |
| Dev pipeline | `scripts/run_granite.py dev` | `python3 scripts/run_granite.py dev [--watch]` |
| Validation | Comparison vs. analytic / SXS | `python3 python/granite_analysis/validate.py` |

### 16.3 Adding Tests

Every new feature **must** add tests. Follow this pattern:

```cpp
// tests/test_new_feature.cpp
#include <gtest/gtest.h>
#include <granite/new_module/feature.hpp>

namespace granite::test {

TEST(NewFeatureSuite, PhysicsCorrectness) {
    // Arrange
    GridBlock state = createTestBlock(32, 32, 32, /* dx= */ 0.1);
    initializeMinkowski(state);

    // Act
    double result = computeNewObservable(state);

    // Assert
    EXPECT_NEAR(result, expected_analytic_value, 1e-10)
        << "Observable should match analytic value to roundoff";
}

TEST(NewFeatureSuite, ConvergenceOrder) {
    // Test that errors converge at the expected rate
    double err_coarse = runAndMeasureError(/* dx= */ 0.2);
    double err_fine   = runAndMeasureError(/* dx= */ 0.1);
    double order = std::log2(err_coarse / err_fine);
    EXPECT_NEAR(order, 4.0, 0.1) << "Should converge at 4th order";
}

} // namespace granite::test
```

### 16.4 Pre-PR Checklist

Before opening any pull request:

```
[ ] Full test suite passes in Release mode: python3 scripts/run_granite.py build --tests
[ ] health_check.py passes: python3 scripts/health_check.py
[ ] Dev pipeline passes in <5 minutes: python3 scripts/run_granite.py dev
[ ] granite_analysis package imports cleanly: python3 -m granite_analysis.cli.dev_benchmark --help
[ ] CHANGELOG.md updated under ## [Unreleased]
[ ] New physics: reference paper cited in comment (author year, journal)
[ ] No regression in constraint norm growth rate vs. baseline
```

---

## 17. Adding New Features / Physics Modules

### 17.1 Step-by-Step Process

1. **RFC first:** Open a GitHub Discussion titled `[RFC] New Feature: <name>` with:
   - Physical motivation and governing equations
   - Reference to relevant papers
   - Estimate of implementation complexity
   - Impact on existing tests

2. **Branch:** `git checkout -b feature/<descriptive-name>`

3. **Implement** in `src/<subsystem>/` following existing patterns. New subsystems get their own directory.

4. **Public interface** in `include/granite/<subsystem>/`. Only expose what users of the module need.

5. **Tests** in `tests/test_<feature>.cpp`. Minimum: one unit test and one convergence test.

6. **YAML support:** If the feature has runtime parameters, add them to the YAML parser and document in `docs/`.

7. **Update CHANGELOG.md** under `## [Unreleased]`.

8. **PR** using the provided template. Must include benchmark results showing no regression.

### 17.2 Priority Areas (2026 Roadmap)

- GPU acceleration (CUDA kernels for CCZ4 and GRMHD hot loops)
- Tabulated nuclear EOS + nuclear reaction network
- Frequency-dependent M1 radiation (multi-group)
- Full dynamic AMR regridding
- Checkpoint-restart (`loadCheckpoint()` implementation)
- macOS native support

---

## 18. Parameter System (YAML)

### 18.1 Parameter File Structure

```yaml
# params.yaml — canonical parameter file
simulation:
  name:          "B2_eq_production"
  output_dir:    "./output/B2_eq"
  total_time:    1000.0     # [M]
  checkpoint_every: 5000   # steps

domain:
  size:   96.0        # half-width [M] (full domain: [-96, 96]³)
  nx: 128
  ny: 128
  nz: 128

amr:
  levels: 6
  refinement:
    criteria:
      - variable: chi
        threshold: 0.15
      - variable: alpha
        threshold: 0.3

initial_data:
  type: two_punctures
  bh1:
    mass: 0.5
    position: [5.0, 0.0, 0.0]
    momentum: [0.0, 0.0840, 0.0]
    spin: [0.0, 0.0, 0.0]
  bh2:
    mass: 0.5
    position: [-5.0, 0.0, 0.0]
    momentum: [0.0, -0.0840, 0.0]
    spin: [0.0, 0.0, 0.0]

ccz4:
  kappa1: 0.02
  kappa2: 0.0
  eta:    2.0

dissipation:
  ko_sigma: 0.1       # SAFE DEFAULT — do not increase

time_integration:
  cfl: 0.25

boundary:
  type: sommerfeld    # Use 'copy' for Brill-Lindquist ID only

diagnostics:
  gw_extraction:
    enabled: true
    radii: [50, 100, 150, 200, 300, 500]
  constraints:
    output_every: 100
  ah_finder:
    enabled: true
    every: 10

io:
  output_every: 100
  checkpoint_every: 5000
```

---

## 19. HPC & Performance Guidelines

### 19.1 Scaling Targets

| Configuration | Description | Target Efficiency |
|---|---|---|
| 128³ development run | i5-8400, 6 cores, 16 GB | Baseline (single node) |
| 256³ production run | Cluster, 64+ cores, 128 GB | ≥ 90% strong scaling |
| 512³ flagship | Cluster, 512+ cores, 1 TB | ≥ 85% strong scaling |
| Full B5\_star | 10,000+ cores, ~2 TB RAM | Exascale-class |

**Note on the GTX 1050 Ti:** The development desktop GPU is not viable for FP64 GPU compute (too little VRAM, no FP64 fast path). GPU production runs target **vast.ai H100 SXM instances** after GPU kernel porting is complete.

### 19.2 Memory Estimates

| Simulation | AMR Levels | RAM Estimate |
|---|---|---|
| 128³, 6 levels | 6 | ~2 GB |
| 256³, 8 levels | 8 | ~16–32 GB |
| 512³, 10 levels | 10 | ~128–256 GB |
| Full B5\_star, 12 levels | 12 | ~2 TB |

### 19.3 HPC Job Submission

```bash
# Generate SLURM job script
python3 scripts/run_granite_hpc.py --nodes 32 --cores-per-node 64 \
    --benchmark benchmarks/B2_eq/B2_eq.yaml \
    --output slurm_B2_eq.sh

# Submit
sbatch slurm_B2_eq.sh
```

### 19.4 I/O Tuning (Lustre / Parallel FS)

```yaml
io:
  hdf5_stripe_count: 16    # Match Lustre stripe count to node count
  hdf5_stripe_size: 4194304  # 4 MB stripes
  collective_io: true        # MPI-IO collective mode
```

### 19.5 Profiling

Recommended tools:
- **Intel VTune** / **AMD uProf** — CPU hotspot analysis
- **Score-P + Vampir** — MPI communication analysis
- **NVIDIA Nsight** — GPU kernels (post v0.7)
- **Valgrind Massif** — Memory profiling (debug builds only)

---

## 20. Known Fixed Bugs (CHANGELOG Reference)

The CHANGELOG is the **authoritative record** of previously identified and fixed bugs. Never re-introduce a fix listed here. If a proposed change would revert any of these, it must be flagged immediately and rejected.

| ID | Component | Bug Description | Fix |
|---|---|---|---|
| **C1** | GRMHD EOS | Sound speed hardcoded as γ = 1 (wrong for all non-trivial EOS) | Compute sound speed exactly from EOS every call |
| **C3** | GRMHD HLLE | GR-aware HLLE used a flat (Minkowski) dummy metric for wave speeds | Use actual curved-space metric from GRMetric3 |
| **H1** | CCZ4 KO | Kreiss-Oliger dissipation spawned 22 separate OpenMP parallel regions (race condition) | Single parallel region over all 22 variables |
| **H2** | GridBlock | Data allocated as `vector<vector<Real>>` (pointer-chasing, no SIMD) | Single flat `vector<Real>` with stride-based indexing |
| **H3** | CCZ4 RHS | RHS zero-out loop had variable as outer loop (cache-thrashing) | Spatial outer, variable inner (matches field-major layout) |
| **TOV** | Initial data | TOV ODE integration used RSUN\_CGS for km→cm conversion | Use `1e5 cm/km` |
| **KO-σ** | CCZ4 dissipation | `ko_sigma: 0.35` in params.yaml over-dissipates trumpet gauge profile | Default and enforce `ko_sigma: 0.1` |
| **Sommerfeld+BL** | BCs | Sommerfeld BCs applied with Brill-Lindquist ID (8× constraint blow-up) | Use copy BCs for BL; Sommerfeld only for puncture data |
| **Domain** | Geometry | Small domains (±24M) caused secular constraint drift from boundary gauge reflections | Minimum domain half-width ±48M for stable long runs |
| **alpha_center** | Diagnostics | `alpha_center` diagnostic read lapse from AMR level 0 at r ≈ 0.65M, not from the finest level near r → 0 | Sample from finest AMR level at the puncture location |

---

## 21. Simulation Health & Debugging

### 21.1 Primary Health Indicators

Monitor these quantities at every diagnostic output step:

| Indicator | Description | Healthy Range |
|---|---|---|
| `alpha_center` | Lapse at finest AMR level near puncture | Collapses toward 0 for moving punctures |
| `‖H‖₂` | Hamiltonian constraint L2 norm | Decaying or slowly growing (< ×100 over 500M) |
| `gamma_H` | Growth rate of ‖H‖₂ fit | < 0.005 /M (exponential growth coefficient) |
| `NaN_events` | Count of NaN values produced | Must be 0 at all times |
| `AMR_levels` | Actual AMR refinement count | Should grow toward max\_levels over inspiral |
| `CFL_finest` | CFL at finest AMR level | Must remain ≤ 0.5 with lapse suppression active |

### 21.2 Debugging Flowchart

```
Simulation crashed or produced unexpected results
        │
        ├── NaN events > 0?
        │       └── YES: Check CFL violation (finest level CFL > 0.5)
        │                Check reconstruction (MP5 → PPM → PLM fallback)
        │                Check C2P failure (reduce GRMHD timestep)
        │
        ├── ‖H‖₂ growing rapidly (γ > 0.05 /M)?
        │       └── YES: Check domain size (< ±48M → gauge reflection)
        │                Check ko_sigma (> 0.1 → over-dissipation)
        │                Check BCs (Sommerfeld + BL data → incompatible)
        │
        ├── No merger despite d = 10M BBH?
        │       └── YES: Check tangential momenta (p_t = 0 → head-on)
        │                Verify Bowen-York parameters in params.yaml
        │
        ├── Lapse not forming trumpet?
        │       └── Check resolution (dx > 0.5M → trumpet unresolved, not a bug)
        │                Check ko_sigma (0.35 → destroys trumpet profile)
        │
        └── Secondary gauge collapse without NaN?
                └── This is gauge pathology, NOT a numerical crash
                         Do NOT terminate — monitor and let the run continue
```

### 21.3 Common Failure Modes

**"Simulation crashes at t ≈ 6M"**
Usually a CFL violation at the finest AMR level when the lapse collapses. Fix: ensure CFL ≤ 0.5 at finest level, or verify the lapse floor is active.

**"Constraint norms growing exponentially from t = 0"**
Usually incompatible BCs + ID. Verify Sommerfeld BCs are only used with Two-Punctures/Bowen-York ID, never with Brill-Lindquist.

**"AMR blocks stuck at 4 throughout the run"**
Dynamic regridding is **fully implemented in v0.6.7** and active in production runs. This is not a limitation.

**"Phase labels show Early Inspiral through t=500M"**
Phase labels are currently time-based, not separation-based. This is a known accuracy issue. Do not mistake it for a physics bug.

---

## 22. Scientific Validation & Publication Policy

### 22.1 Validation Targets

| Benchmark | Reference | Status |
|---|---|---|
| Single BH puncture stability | Analytic: lapse → trumpet | ✅ Validated (DEV_LOG5) |
| Equal-mass BBH | SXS catalog (60+ configs) | 🔶 In progress (B2\_eq series) |
| TOV neutron star | Analytic TOV solution | ✅ Unit test passes |
| GW waveform | SXS:BBH:0305 (standard) | 🔶 Planned for v0.7 |
| Shock tube | GRMHD exact solutions | ✅ Unit tests pass |
| MHD rotor | Analytic | ✅ Validated |

### 22.2 Requirements for Publication

Any scientific result from GRANITE intended for publication **must**:

1. Cite the GRANITE paper (in preparation — see `docs/citation.bib`)
2. Include the exact YAML benchmark file used
3. Provide `health_check.py` output and full test coverage report
4. Include constraint norm time series and AMR level count evolution
5. Share checkpoint files on Zenodo or equivalent

Co-authorship is actively encouraged for significant scientific contributions.

---

## 23. Collaboration & Community

### 23.1 Communication Channels

- **GitHub Discussions** — primary channel for design decisions, RFCs, and Q&A
- **GitHub Issues** — bug reports and concrete feature requests
- **PRs** — code contributions following the workflow in Section 17

### 23.2 Contribution Recognition

| Contribution Type | Recognition |
|---|---|
| Code contributor | Listed in AUTHORS.md + release notes |
| Physics / validation contributor | Co-author on related papers |
| Major subsystem owner | Listed as "Core Developer" |

### 23.3 Partnerships Sought

GRANITE actively seeks partnerships with:
- Supercomputing centers (Tier-0/1) for B5\_star production runs
- Einstein Toolkit, GRChombo, SpECTRE teams for cross-validation
- LIGO/Virgo/KAGRA waveform groups for template bank applications
- Nuclear physics groups for EOS and neutrino interaction data

---

## 24. Roadmap (v0.7 → v1.0)

| Version | Quarter | Key Deliverables |
|---|---|---|
| **v0.7** | Q2 2026 | GPU prototype (CUDA CCZ4 + GRMHD kernels), checkpoint-restart, full dynamic AMR regridding, M1 wired into RK3 loop |
| **v0.8** | Q3 2026 | Tabulated nuclear EOS + nuclear network, SXS BBH waveform validation suite |
| **v0.9** | Q4 2026 | Full validation vs. Einstein Toolkit binaries, multi-group M1 radiation, Python API for real-time steering |
| **v1.0** | Q1 2027 | Production-ready B5\_star publication + full community open release, full support to all native OS(windows\macOS) |

**Scaling path to B5\_star:**
1. v0.6.5: Development-scale runs (128³) on personal desktop (i5-8400, GTX 1050 Ti not viable for FP64)
2. v0.7: GPU kernel porting complete → vast.ai H100 SXM instances (contingent on GPU porting)
3. v0.8–v0.9: 256³–512³ runs on cluster allocations
4. v1.0: Full B5\_star at 12 AMR levels (~2 TB RAM, ~5×10⁶ CPU-hours or ~5×10⁵ GPU-hours)

---

## 25. Flagship Scenario: B5\_star

### 25.1 Configuration

The B5\_star benchmark is the primary scientific motivation for GRANITE. It represents a scenario with no existing code capable of simulating it at full physics fidelity.

```yaml
# benchmarks/B5_star/B5_star.yaml (excerpt)
simulation:
  name: "B5_star_flagship"
  total_time: 1.0e5   # years (in code units scaled to 10^8 M_sun)

initial_data:
  type: multi_body
  bodies:
    # Five supermassive black holes
    - type: black_hole
      mass: 1.0e8   # M_sun
      position: [1.0, 0.0, 0.0]    # pc (pentagon vertex)
      # ... (5 BHs in regular pentagon at 1 pc radius)

    # Two ultra-massive stars at center
    - type: star
      mass: 4300.0  # M_sun
      position: [0.0, 0.0, 0.1]
      # ... (polytropic star + MHD fields)

amr:
  levels: 12
  # Estimated RAM at full 12 levels: ~2 TB
```

### 25.2 Expected Physics

The B5\_star simulation will capture:
- Sequential SMBH inspiral and merger driven by gravitational radiation + dynamical friction
- Jet formation from MHD processes during each merger
- Neutrino emission from stellar disruption events
- Multi-band gravitational wave signal (LISA / PTA frequency range)
- Electromagnetic counterpart (multi-messenger signal)

### 25.3 Analytic Pre-Validation (NRCF / PRISM Benchmarks)

Before the full simulation, key output observables are pre-validated against analytic estimates from the NRCF and PRISM predecessor frameworks:

| Observable | NRCF/PRISM Estimate | Tolerance |
|---|---|---|
| Peak GW frequency | Computed from chirp mass | ±10% |
| Total GW energy radiated | η M c² (η ~ 0.05) | ±15% |
| Merger shock temperature | T_shock ~ GM μ / (k_B r_merger) | ±20% |
| Final spin parameter | a/M ≲ 0.7 (NR bound) | ±5% |

---

## Appendix A: Physical Constants (Code Units)

GRANITE uses geometrized units throughout: **G = c = 1**, with mass scale set by the total system ADM mass M_total = 1.

| Quantity | Code Symbol | Conversion |
|---|---|---|
| Speed of light | c = 1 | 3×10¹⁰ cm/s |
| Gravitational constant | G = 1 | 6.674×10⁻⁸ cm³ g⁻¹ s⁻² |
| Gravitational wave unit | M | M_total × G/c³ (in seconds) |
| km to cm | — | 1.0 × 10⁵ cm/km (NOT RSUN_CGS) |

## Appendix B: Key References

| Reference | Used in |
|---|---|
| Alic et al. 2012, PRD 85, 064040 | CCZ4 formulation |
| Bona et al. 1995 | 1+log slicing gauge |
| Campanelli et al. 2006 (moving punctures) | Gamma-driver shift |
| Miyoshi & Kusano 2005, JCP 208, 315 | HLLD Riemann solver |
| Suresh & Huynh 1997 | MP5 reconstruction |
| Berger & Oliger 1984 | AMR + subcycling |
| Evans & Hawley 1988 | Constrained transport |
| Brandt & Brügmann 1997 | Two-punctures ID |
| Nakano et al. 2015 | Ψ₄ extrapolation to null infinity |
| Shu & Osher 1988 | SSP-RK3 time integration |

---

*This document is version-controlled. Always refer to the latest version in the repository.*
*GRANITE v0.6.7 — April 27, 2026 — LiranOG*
