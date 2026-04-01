# GRANITE × Claude Opus/Sonnet — Complete Task Catalog

## What Can Be Done, What the Developer Must Provide, and How Long Everything Takes

**Prepared for:** GRANITE Development Team  
**Date:** April 2026  
**Engine version:** v0.5.0 (90 tests, 100% pass)  
**Context:** Claude Opus/Sonnet via Antigravity / Claude.ai / Claude Code

---

## How to Read This Document

Every task entry follows the same structure:

- **What Claude does** — the concrete deliverable.
- **What you must give Claude** — the exact inputs, files, context required. This is the most important part. Claude's output quality is directly proportional to input quality.
- **Time estimate** — broken into (a) Claude's work time and (b) real-world elapsed time (which may include simulation runs, HPC queue waits, or human review).
- **Quality gate** — how you know the result is correct.
- **GRANITE-specific notes** — exactly which files and functions are involved.

---

# Category 1 — Code Generation (New Modules)

## 1.1 Writing a Complete C++ Physics Module from Scratch

**What Claude does:**
Takes a mathematical specification (equations, boundary conditions, coupling terms) and produces a complete `.hpp` + `.cpp` pair that follows GRANITE's coding conventions: `granite::` namespace hierarchy, PascalCase classes, camelCase functions, snake_case variables, 100-char lines, LLVM clang-format. Includes Doxygen comments with `@brief`, `@param`, `@return`, and references to the relevant physics paper (e.g., "Alic et al., PRD 85, 064040 (2012)").

**What you must give Claude:**

1. **The equations** — written explicitly in index notation or coordinate-free form. Not "implement WENO" — instead: "Implement WENO-Z 5th-order reconstruction (Borges et al. 2008, eq. 2.3–2.7) with the smoothness indicators β_k defined in eq. 2.4 and the global smoothness indicator τ₅ = |β₀ - β₂|."
2. **The interface contract** — function signatures, input/output types. Example: "Input: `const GridBlock& grid, int var, int dim, int i, int j, int k`. Output: `std::pair<Real, Real>` for left/right reconstructed values."
3. **2–3 existing files** from the same part of the codebase for style reference. For GRMHD work, attach `grmhd.hpp` and `grmhd.cpp`. For spacetime work, attach `ccz4.hpp` and `ccz4.cpp`.
4. **Known constraints** — "Must not use dynamic memory allocation inside the spatial loop", "Must be compatible with OpenMP collapse(3)", "Must use the existing `GridBlock::data(var, i, j, k)` accessor".
5. **Test cases with known answers** — "For the Sod shock tube with γ=1.4, ρ_L=1, p_L=1, ρ_R=0.125, p_R=0.1, the contact discontinuity should be at x=0.6854 at t=0.25."

**Time estimates:**

| Module complexity | Claude work | Human review + integration | Total |
|---|---|---|---|
| Small function (50–150 lines, e.g., WENO reconstruction) | 30–60 min | 2–4 hours | 1 day |
| Medium module (300–600 lines, e.g., new Riemann solver) | 2–4 hours | 1–2 days | 2–3 days |
| Large module (800–1500 lines, e.g., resistive MHD extension) | 4–8 hours (multiple iterations) | 3–5 days | 1 week |
| Architectural module (e.g., full AMR with prolongation/restriction) | 2–3 days of iterative sessions | 1–2 weeks testing | 2–3 weeks |

**Quality gate:** Compiles with `-Wall -Wextra -Werror`. All new functions have unit tests. Convergence order matches expected value (±0.3).

**GRANITE-specific notes:**
- All new physics modules must respect the `GridBlock` field-major layout: `data_[var * stride + flat(i,j,k)]`.
- Loop order must be spatial-outermost, var-innermost (H3 fix — never reverse this).
- Ghost zone count is always `nghost=4` (for 4th-order FD stencils).
- The `GRMetric3` struct is the coupling bridge between CCZ4 and GRMHD — any new module that needs metric data must go through this interface.

---

## 1.2 Writing GPU Kernels (CUDA/HIP)

**What Claude does:**
Translates existing CPU functions into GPU kernels using CUDA or HIP. Can also write a portable abstraction layer using Kokkos-style `parallel_for` patterns.

**What you must give Claude:**

1. **The CPU function** to port (the exact `.cpp` file).
2. **The GPU strategy** — "One CUDA thread per grid cell", or "Use shared memory for the stencil halo", or "Use Kokkos with `RangePolicy`".
3. **Target architecture** — "NVIDIA A100 (sm_80)" or "AMD MI250 (gfx90a)".
4. **Memory layout confirmation** — GRANITE's flat layout is already GPU-friendly. Confirm that `data_[var * stride + flat(i,j,k)]` will be used on device.

**Time estimates:**

| Kernel complexity | Claude work | Human testing on GPU | Total |
|---|---|---|---|
| Simple kernel (element-wise, no stencil) | 1–2 hours | 1 day (GPU access, profiling) | 1–2 days |
| Stencil kernel (CCZ4 RHS, needs halo) | 4–8 hours | 2–3 days (shared memory tuning) | 3–5 days |
| Full module port (CCZ4 + GRMHD + Con2Prim) | 2–3 days | 1–2 weeks (performance tuning) | 2–4 weeks |

**Quality gate:** Bitwise identical results to CPU version for FP64. Achieved >5× speedup over 32-core CPU node.

---

## 1.3 Writing Python Analysis Scripts

**What Claude does:**
Produces complete Python scripts for post-processing GRANITE output: HDF5 data extraction, convergence analysis, waveform comparison, matplotlib/plotly visualizations, statistical analysis.

**What you must give Claude:**

1. **Sample output file** — either the actual HDF5 file (preferred) or its structure: dataset names, shapes, dtypes. Example: "The file `checkpoint_0100.h5` contains datasets `/spacetime/chi` (shape 72×72×72, float64), `/constraints/hamiltonian` (shape 64×64×64, float64), `/time` (scalar float64)."
2. **What to compute** — be specific. Not "analyze convergence" but "Compute the L2 norm of the Hamiltonian constraint at 3 resolutions (N=32, 48, 64), fit log(||H||₂) vs log(h) to extract convergence order Q, and plot with errorbars."
3. **Plot style** — "Publication-quality, LaTeX labels, log-log axes, 300 dpi PNG and PDF."
4. **Reference data** (if comparing) — SXS waveform file, analytical solution formula.

**Time estimates:**

| Script type | Claude work | Human verification | Total |
|---|---|---|---|
| Simple extraction + plot (1 quantity vs time) | 15–30 min | 30 min | 1 hour |
| Convergence analysis (3 resolutions, 1 test) | 30–60 min | 1–2 hours | 2–3 hours |
| Full benchmark suite (like `dev_benchmark.py`) | 4–8 hours | 1 day | 1–2 days |
| Waveform mismatch against SXS catalog | 2–4 hours | 1 day (+ simulation time) | 1–2 days + sim time |

**GRANITE-specific notes:**
- The existing `reader.py` provides HDF5 timeseries reading — tell Claude to use it.
- `gw.py` already has spin-weighted spherical harmonics (Wigner d-matrix) up to ℓ=8 — don't re-implement.
- `dev_benchmark.py` has NaN forensics, phase classification, CFL diagnostics — extend it, don't replace it.

---

# Category 2 — Debugging & Bug Fixing

## 2.1 Analyzing NaN/Inf Crashes

**What Claude does:**
Traces the origin of numerical instabilities by analyzing the code flow, identifying unprotected divisions (1/χ, 1/α, 1/ρ), checking floor consistency, verifying stencil correctness, and proposing fixes.

**What you must give Claude:**

1. **The exact error output** — copy-paste the full terminal output including the NaN diagnostic lines (e.g., `[NaN@step=12] ST var=0 (36,36,36) = nan`).
2. **The parameter file** (`params.yaml`) — domain size, resolution, CFL, initial data type, gauge parameters.
3. **The relevant source files** — for CCZ4 crashes: `ccz4.cpp`, `ccz4.hpp`, the RK3 step function. For GRMHD crashes: `grmhd.cpp`, the Con2Prim code.
4. **What changed recently** — "I modified the KO dissipation coefficient from 0.1 to 0.5" or "I added a new initial data type."
5. **The NAN_DEBUG_BRIEF.md** — it already contains the crash timeline, hypotheses, and recent mitigation attempts.

**Time estimates:**

| Bug type | Claude analysis | Fix verification | Total |
|---|---|---|---|
| Missing floor/guard (e.g., division by χ without floor) | 30–60 min | 1–2 hours (rerun sim) | 2–3 hours |
| Sign error in Christoffel symbol or RHS term | 1–2 hours (cross-reference with paper) | 4–8 hours (convergence test) | 1 day |
| Stencil addressing error (wrong index in FD) | 1–2 hours | 2–4 hours | 1 day |
| Race condition in OpenMP/MPI | 2–4 hours (code analysis) | 1–2 days (need multiple runs) | 2–3 days |
| Ghost zone sync order bug (RK3 substep missing sync) | 1–2 hours | 4–8 hours (need to run multiple steps) | 1 day |

**Critical rule:** Always tell Claude which bugs were already fixed (C1, C3, H1, H2, H3, TOV). Otherwise it may suggest reverting a fix.

---

## 2.2 Performance Profiling & Optimization

**What Claude does:**
Analyzes profiler output (perf, vtune, nsight), identifies bottlenecks, suggests loop transformations, SIMD hints, memory layout changes, and OpenMP tuning.

**What you must give Claude:**

1. **Profiler output** — `perf report` text, VTune hotspot summary, or NVIDIA Nsight Compute kernel statistics.
2. **The hot function** — the exact source code of the function that takes the most time.
3. **Hardware** — CPU model (e.g., "AMD EPYC 7763, 64 cores, 256 MB L3"), or GPU model.
4. **Current performance** — "CCZ4 RHS takes 2.3 seconds per step on 64³ grid with 32 threads."

**Time estimates:**

| Optimization type | Claude work | Testing | Total |
|---|---|---|---|
| Loop reordering / vectorization hints | 30–60 min | 2–4 hours (benchmark) | half day |
| OpenMP schedule tuning (static vs dynamic vs guided) | 30 min | 1–2 hours | 2–3 hours |
| Memory access pattern optimization | 1–2 hours | 1 day (profiling before/after) | 1–2 days |
| Major restructuring (e.g., SoA to AoS conversion) | 4–8 hours | 2–3 days | 3–5 days |

**GRANITE-specific notes:**
- Do NOT change the field-major layout (`data_[var * stride + flat(i,j,k)]`) — this is H2 fix, proven optimal.
- Do NOT split OMP regions in KO dissipation — this is H1 fix.
- Do NOT change RHS loop order — this is H3 fix.

---

# Category 3 — Testing & Validation

## 3.1 Unit Test Creation (GoogleTest)

**What Claude does:**
Writes complete GoogleTest test suites with fixtures, edge cases, tolerance checks, and ASSERT/EXPECT macros appropriate for numerical code.

**What you must give Claude:**

1. **The function to test** — full source code + header.
2. **Known analytical results** — "For a Minkowski spacetime (flat), all Christoffel symbols must be zero", or "For ideal gas with γ=5/3 and ρ=1, ε=1, the pressure should be p = (γ-1)ρε = 2/3."
3. **Tolerance** — "Relative tolerance 1e-12 for exact operations, 1e-6 for iterative solvers, 1e-2 for convergence order."
4. **Edge cases** — "Test with ρ = ρ_floor = 1e-12", "Test with B² >> ρ (magnetically dominated)", "Test at the puncture center where χ → 0."
5. **Existing test files** for style — attach `test_ccz4_flat.cpp` or `test_hlld_ct.cpp`.

**Time estimates:**

| Test scope | Claude work | Compilation + run | Total |
|---|---|---|---|
| Single function, 3–5 test cases | 15–30 min | 15 min | 30–45 min |
| Full module, 15–25 test cases | 2–4 hours | 30–60 min | 3–5 hours |
| Integration test (multi-module) | 4–6 hours | 1–2 hours | 1 day |

**Quality gate:** All tests pass. Edge cases do not segfault. Numerical tolerances are tight enough to catch regressions but loose enough to pass on different compilers.

**GRANITE current state:** 81 tests across 14 suites. Target for v1.0: 150+ tests.

---

## 3.2 Convergence Testing (requires simulation runs)

**What Claude does:**
- Writes the convergence test script (Python) that runs GRANITE at multiple resolutions and computes the convergence order.
- Writes the parameter files for each resolution.
- Writes the analysis script that fits Q = log(||e_h||/||e_{h/2}||) / log(2).
- Interprets the results and identifies if convergence is clean or polluted.

**What you must provide:**

1. **Which test** — gauge wave, single puncture, TOV star, Balsara shock tube.
2. **Resolutions** — typically 3–4: e.g., N = 32, 48, 64, 96 (or N, 1.5N, 2N for Richardson extrapolation).
3. **Error norm** — L2 of Hamiltonian constraint, L∞ of density, phase error of (2,2) mode.
4. **Reference solution** — analytical (for gauge wave) or fine-grid self-convergence.
5. **HPC allocation** — where to run, how many cores per run.

**What you must run yourself:**
The actual simulations. Claude cannot execute HPC jobs.

**Time estimates:**

| Phase | Who does it | Time |
|---|---|---|
| Script preparation (params + analysis) | Claude | 2–4 hours |
| Run 3 resolutions of gauge wave (64³, 96³, 128³) | You (HPC) | 1–8 hours per resolution |
| Run 3 resolutions of single puncture (64³, 96³, 128³) | You (HPC) | 4–48 hours per resolution |
| Run 3 resolutions of binary BH (need AMR) | You (HPC) | days–weeks per resolution |
| Result analysis | Claude | 1–2 hours |
| **Total for one convergence study** | Combined | **2–7 days** (dominated by sim time) |

**GRANITE-specific notes:**
- `validation_tests.yaml` already defines pass criteria for gauge wave (Q ≥ 3.7), single puncture (horizon mass drift < 1e-4), and binary BH (phase error < 0.01 rad).
- Expected convergence order: 4.0 for CCZ4 (4th-order FD), 2.0 for GRMHD with PLM, 3.0–5.0 with MP5/PPM.

---

## 3.3 Validation Against Reference Catalogs (long-term campaigns)

**What Claude does:**
- Designs the full validation matrix (which SXS waveforms, which resolutions, which physical parameters).
- Writes the mismatch computation: inner product ⟨h₁|h₂⟩ with noise-weighted integration.
- Writes batch submission scripts (SLURM, PBS) for parametric sweeps.
- Analyzes results: mismatch tables, convergence plots, phase/amplitude error decomposition.

**What you must provide:**

1. **SXS catalog access** — download specific waveforms (e.g., SXS:BBH:0001 through SXS:BBH:0020).
2. **Physical parameters per case** — mass ratio q, spins χ₁/χ₂, eccentricity.
3. **HPC allocation** — total core-hours budget.
4. **Acceptable mismatch threshold** — typically 1e-3 for data analysis, 1e-2 for initial validation.

**Time estimates:**

This is the category where timescales are measured in **weeks to months**, dominated entirely by simulation runtime:

| Campaign | # simulations | Time per sim | Claude work | Total campaign |
|---|---|---|---|---|
| Basic validation (5 SXS cases, 1 resolution) | 5 | 3–7 days each | 2–3 days (scripts) | 2–5 weeks |
| Convergence validation (5 cases × 3 resolutions) | 15 | 3–7 days each | 3–5 days (scripts) | 1–3 months |
| Full catalog comparison (20 cases × 3 resolutions) | 60 | 3–7 days each | 1 week (scripts) | 3–6 months |
| Parameter sweep (vary κ₁, η, CFL over 100 configs) | 100–500 | hours–days each | 2–3 days (scripts) | 1–4 months |
| Numerical parameter calibration (κ₁, κ₂, η, σ_KO) | 200–1000 | minutes–hours each | 1–2 days (scripts) | 2–8 weeks |

**Critical note:** Claude's role here is **preparation and analysis**, not execution. Claude prepares all scripts, parameter files, and analysis pipelines up front. The developer runs the simulations. When results are available, Claude analyzes them.

---

# Category 4 — Refactoring & Code Quality

## 4.1 Breaking Up Long Functions

**What Claude does:**
Splits monolithic functions (500+ lines) into well-named helper functions without changing behavior. Maintains the same memory access pattern and loop structure.

**What you must give Claude:**

1. **The function to split** — full source code.
2. **Logical groupings** — "Lines 100–250 compute Christoffel symbols, lines 250–400 compute Ricci tensor, lines 400–600 assemble the RHS." Or let Claude propose the split.
3. **Constraint:** "Must preserve the same OpenMP parallel region — don't add new `#pragma omp parallel` inside helper functions."

**Time estimates:**

| Function size | Claude work | Review + test | Total |
|---|---|---|---|
| 300–500 lines → 3–4 functions | 1–2 hours | 2–4 hours | half day |
| 800–1200 lines → 6–8 functions | 2–4 hours | 1 day | 1–2 days |
| `main.cpp` restructure (1135 lines) | 4–8 hours | 2–3 days | 3–5 days |

**GRANITE targets:**
- `ccz4.cpp` `computeRHS()` — split into `computeChristoffels()`, `computeRicci()`, `assembleRHS()`.
- `grmhd.cpp` — split flux computation from source terms.
- `main.cpp` — extract `TimeIntegrator` to its own file, extract `InitialDataDispatcher`, extract `DiagnosticsManager`.

---

## 4.2 Adding const-correctness, noexcept, [[nodiscard]]

**What Claude does:**
Scans a file and adds `const` to all methods that don't modify state, `noexcept` to functions that cannot throw, and `[[nodiscard]]` to functions whose return value should not be ignored.

**What you must give Claude:**
The `.hpp` + `.cpp` pair. That's it — this is a mechanical task.

**Time estimates:** 30–60 min per file pair. 1–2 days for the entire codebase.

---

# Category 5 — Documentation

## 5.1 Doxygen Comment Generation

**What Claude does:**
Adds complete Doxygen documentation to every public class, function, enum, and struct. Includes mathematical descriptions using LaTeX notation, parameter descriptions, return value specifications, and cross-references.

**What you must give Claude:**
The header file (`.hpp`). Optionally, the corresponding `.cpp` for implementation details.

**Time estimates:**

| File size | Claude work | Human review | Total |
|---|---|---|---|
| Small header (50–100 lines) | 30 min | 15 min | 45 min |
| Medium header (100–300 lines, like `ccz4.hpp`) | 1–2 hours | 30 min | 2 hours |
| Large header (300+ lines, like `grmhd.hpp`) | 2–3 hours | 1 hour | 3–4 hours |
| All headers in project | 1–2 days | 1 day | 2–3 days |

---

## 5.2 User-Facing Tutorials & Guides

**What Claude does:**
Writes step-by-step tutorials for specific use cases: "How to set up a binary BH simulation", "How to add a custom equation of state", "How to extract gravitational waveforms from output data."

**What you must give Claude:**

1. **Target audience** — "Graduate student in numerical relativity with C++ experience" or "Physicist who can run code but not write it."
2. **The workflow** — step by step, what commands are run, what files are created.
3. **Screenshots/outputs** — sample terminal output at each stage.

**Time estimates:** 2–4 hours per tutorial. A set of 5 tutorials covering the main use cases: 2–3 days.

---

## 5.3 Academic Paper Drafting

**What Claude does:**
Writes LaTeX-ready text for methods papers: introduction with literature review, mathematical formulation, numerical methods description, test results presentation, convergence analysis, and conclusion. Generates BibTeX references.

**What you must give Claude:**

1. **Paper structure** — "Introduction (cite Baiotti & Rezzolla 2017 review), Methods (CCZ4 formulation, GRMHD Valencia, HLLD solver), Tests (gauge wave, single puncture, Balsara), Results (convergence plots — I'll provide the data), Conclusion."
2. **Figures** — descriptions of what each figure shows, with the actual data/numbers.
3. **Target journal** — PRD, CQG, ApJ (affects style, length, reference format).
4. **Key references** — list of papers that must be cited.

**Time estimates:**

| Deliverable | Claude work | Human editing | Total |
|---|---|---|---|
| Methods section (5–8 pages) | 4–6 hours | 1–2 days | 2–3 days |
| Full first draft (15–20 pages) | 1–2 days | 3–5 days | 1 week |
| Revision after referee report | 2–4 hours per major point | 1–2 days | 2–3 days |

---

# Category 6 — Architecture & Design

## 6.1 Module Interface Design

**What Claude does:**
Proposes class hierarchies, inheritance structures, abstract interfaces, and dependency injection patterns for new GRANITE subsystems.

**What you must give Claude:**

1. **Requirements** — "I need a plugin system where users can register custom physics modules at runtime via YAML configuration."
2. **Constraints** — "No virtual function calls inside the spatial loop (performance critical)", "Must work with MPI — each rank loads the same plugins."
3. **Existing architecture** — attach the current `main.cpp`, `grmhd.hpp`, `ccz4.hpp` so Claude understands the patterns already in use.

**Time estimates:** 2–4 hours for initial design proposal. 1–2 iterations of refinement. Total: 1–2 days.

---

## 6.2 Experiment Design (Simulation Campaigns)

**What Claude does:**
Designs the parameter space, resolution hierarchy, and expected resource consumption for large-scale simulation campaigns.

**What you must give Claude:**

1. **Scientific question** — "What is the minimum mass ratio for prompt BH formation in BNS mergers with the SFHo EOS?"
2. **Parameter ranges** — mass ratio q ∈ [1.0, 2.0], total mass M ∈ [2.5, 3.2] M☉, spin χ ∈ [0, 0.3].
3. **Resource constraints** — "We have 500,000 core-hours on a 1000-node cluster with AMD EPYC 7763 CPUs."
4. **Resolution requirements** — "dx = 0.25M at the finest level, extraction radius at 500M."

**What Claude produces:**

- Parameter matrix (which simulations to run, in what order).
- Resource estimates per simulation (core-hours, memory, storage).
- Priority ordering (which runs give the most scientific value first).
- SLURM/PBS submission scripts.
- Post-processing pipeline specification.

**Time estimates:**

| Campaign size | Claude design work | Simulation runtime | Analysis | Total |
|---|---|---|---|---|
| Small (10 simulations) | 1 day | 2–4 weeks | 2–3 days | 3–5 weeks |
| Medium (50 simulations) | 2–3 days | 1–3 months | 1–2 weeks | 2–4 months |
| Large (200+ simulations) | 3–5 days | 3–12 months | 2–4 weeks | 6–12 months |

---

# Category 7 — Specific GRANITE Tasks (Ranked by Priority)

These are the concrete tasks from the audit, with Claude's exact role specified:

## 7.1 [BLOCKER] Implement Multi-Level AMR

**Claude's role:**
- Write the `prolongate()` function (trilinear interpolation from coarse to fine).
- Write the `restrict()` function (volume-average from fine to coarse).
- Write the `regrid()` function with Berger-Rigoutsos cell clustering.
- Write the inter-level ghost zone filling logic.
- Write 10–15 unit tests for each operator.

**What you provide:**
- The current `amr.cpp` and `amr.hpp` (Claude already has them).
- The decision on max refinement levels (suggest: 6–8 for binary BH).
- The refinement criterion (gradient of χ is already implemented as `gradientChiTagger`).

**Time:** Claude: 3–5 days. Integration + testing: 1–2 weeks. Total: 2–3 weeks.

---

## 7.2 [BLOCKER] Sommerfeld Boundary Conditions

**Claude's role:**
- Implement `applySommerfeldBC()` with per-variable asymptotic values.
- For lapse: u₀ = 1, falloff ∝ 1/r. For shift: u₀ = 0, falloff ∝ 1/r². For metric perturbations: u₀ = δᵢⱼ.
- Replace the current zeroth-order outflow in `main.cpp`.

**What you provide:**
- Current BC code in `main.cpp` (lines with `applyOuterBC`).
- The wave speed for each variable class (gauge: v=1, constraint: v=1, physical: v<1).

**Time:** Claude: 4–8 hours. Testing: 1 day. Total: 2 days.

---

## 7.3 [HIGH] Wire Neutrino Transport to Main Loop

**Claude's role:**
- Modify `TimeIntegrator::sspRK3Step()` to call `NeutrinoTransport::computeLeakageRates()` after GRMHD RHS.
- Add radiation source terms (Q_cool, Q_heat) to the energy equation and Yₑ equation.
- Optionally add M1 moments as additional evolved variables.

**What you provide:**
- The `neutrino.hpp`, `neutrino.cpp`, `m1.hpp`, `m1.cpp` files.
- The coupling equations: dE/dt += Q_heat - Q_cool, dYₑ/dt = (rate from `updateElectronFraction`).
- A test case: TOV star with neutrino cooling, expected luminosity ~10⁵³ erg/s.

**Time:** Claude: 1–2 days. Testing: 2–3 days. Total: 3–5 days.

---

## 7.4 [HIGH] GPU Kernel Port

**Claude's role:**
- Write CUDA/HIP kernels for: (a) `CCZ4Evolution::computeRHS()`, (b) `GRMHDEvolution::computeHLLEFlux()`, (c) `GRMHDEvolution::conservedToPrimitive()`.
- Write host-side memory management (device allocation, H↔D transfers).
- Write a `granite::gpu::parallel_for()` wrapper that dispatches to CUDA, HIP, or OpenMP.

**What you provide:**
- The CPU implementations (Claude has them).
- Target GPU architecture.
- Decision on memory management: managed memory (simple, slower) vs explicit transfers (complex, faster).

**Time:** Claude: 1–2 weeks. GPU testing + optimization: 1–2 weeks. Total: 2–4 weeks.

---

## 7.5 Checkpoint Restart

**Claude's role:**
- Write `HDF5Reader::loadCheckpoint()`.
- Write `--restart <file>` CLI parsing in main.cpp.
- Write a test that saves a checkpoint at step 50, restarts, and verifies bitwise identical results at step 100.

**What you provide:** The current `HDF5Writer::writeCheckpoint()` implementation (so Claude matches the format).

**Time:** Claude: 4–8 hours. Testing: 4 hours. Total: 1–2 days.

---

# Category 8 — Tasks That Take Hundreds/Thousands of Runs

These tasks require massive computational campaigns. Claude's role is strictly **preparation + analysis** — not execution.

## 8.1 Numerical Parameter Calibration

**Goal:** Find optimal values for κ₁, κ₂, η, σ_KO, CFL that minimize constraint violations while maintaining stability.

| Parameter | Range | Grid resolution | # Runs | Sim time each | Total wall time |
|---|---|---|---|---|---|
| κ₁ (constraint damping) | [0.001, 0.1] in 10 steps | 64³ | 10 | ~1 hour | 10 hours |
| κ₂ | [-1, 1] in 5 steps | 64³ | 5 | ~1 hour | 5 hours |
| η (Γ-driver) | [0.5, 4.0] in 8 steps | 64³ | 8 | ~1 hour | 8 hours |
| σ_KO | [0.01, 0.5] in 10 steps | 64³ | 10 | ~1 hour | 10 hours |
| CFL | [0.1, 0.4] in 7 steps | 64³ | 7 | ~1 hour | 7 hours |
| **2D sweep** (κ₁ × η) | 10 × 8 | 64³ | 80 | ~1 hour | 80 hours |
| **Full 4D sweep** | 5³ × 3 CFL | 64³ | 375 | ~1 hour | 375 hours (~2 weeks) |

**Claude's role:** Write parameter generation scripts, SLURM batch arrays, post-processing analysis (heatmaps of ||H||₂ vs parameters, stability boundary detection). ~2 days of Claude work.

---

## 8.2 Convergence Order Verification (Full Suite)

| Test case | # Resolutions | Sim time each | # Runs | Total wall time |
|---|---|---|---|---|
| Gauge wave (1D) | 4 (32,48,64,96) | minutes | 4 | < 1 hour |
| Robust stability | 3 (32,48,64) | hours | 3 | 3–6 hours |
| Single puncture | 4 (32,48,64,96) | hours–day | 4 | 1–4 days |
| TOV star | 4 (32,48,64,96) | hours | 4 | 4–16 hours |
| Balsara shock tubes (5 tests) | 3 (128,256,512) × 5 | minutes | 15 | 1–2 hours |
| Binary BH (needs AMR) | 3 (h, h/1.5, h/2) | days–weeks | 3 | 1–6 weeks |
| BNS merger (needs AMR + neutrino) | 3 | weeks | 3 | 1–3 months |
| **Total convergence campaign** | — | — | ~36 | **1–4 months** |

**Claude's role:** Write all parameter files, submission scripts, convergence analysis pipeline, publication-quality convergence plots. ~3–5 days of Claude work.

---

## 8.3 Waveform Validation Against SXS

| Validation tier | # SXS cases | Resolutions per case | Total sims | Sim time each | Campaign time |
|---|---|---|---|---|---|
| Tier 1: Proof of concept | 3 (q=1, q=2, q=4) | 1 | 3 | 1–2 weeks | 2–6 weeks |
| Tier 2: Basic catalog | 10 (varied q, χ) | 2 | 20 | 1–2 weeks | 1–3 months |
| Tier 3: Full validation | 20+ cases | 3 | 60+ | 1–2 weeks | 3–6 months |
| Tier 4: Paper-quality | 20 cases | 3 + extrapolation | 60+ analysis | 1–2 weeks | 6–12 months |

**Claude's role:** Design the case selection (which SXS waveforms give the most discriminating tests), write the mismatch pipeline, generate comparison plots, draft the results section of the paper. ~1 week of Claude work.

---

## 8.4 EOS Sensitivity Study

**Goal:** Test how different nuclear EOS tables affect merger outcomes.

| EOS | Source | # Simulations | Parameters varied |
|---|---|---|---|
| SFHo | StellarCollapse.org | 5 (varied mass ratio) | q = 1.0, 1.2, 1.4, 1.6, 1.8 |
| SFHx | StellarCollapse.org | 5 | same |
| DD2 | CompOSE | 5 | same |
| LS220 | StellarCollapse.org | 5 | same |
| BHBΛφ | CompOSE | 5 | same |
| **Total** | 5 EOS × 5 configs | **25 simulations** | Each takes 1–3 weeks |

**Claude's role:** Write the EOS loading scripts, parameter files for each configuration, comparison analysis (threshold mass for prompt collapse, ejecta mass vs EOS stiffness, kilonova light curves). ~3–5 days of Claude work. Campaign: 2–6 months.

---

# Category 9 — Things Claude Cannot Do (Or Does Poorly)

Being honest about limitations is critical for efficient workflow:

| Task | Why Claude can't do it | What to do instead |
|---|---|---|
| Run simulations | No HPC access | Use SLURM/PBS scripts Claude prepared |
| Fix timing-dependent MPI bugs | Needs real parallel execution | Run with `-fsanitize=thread`, give Claude the report |
| Tune GPU shared memory tile sizes | Needs profiler feedback loops | Run NVIDIA Nsight, give Claude the metrics |
| Judge physical plausibility of results | Needs domain expertise | Claude can flag anomalies, human decides if they're physical |
| Guarantee code is correct | Can introduce subtle sign errors | Always run convergence tests after any physics change |
| Replace the physicist | Understanding what the results mean | Claude assists; the scientist interprets |
| Write production-ready MPI code blindly | Deadlocks require runtime testing | Claude writes first draft; test with 2, 4, 8 ranks |

---

# Category 10 — Optimal Workflow: The "Golden Loop"

The most efficient way to use Claude for GRANITE development:

```
┌─────────────────────────────────────────────────────┐
│  1. SPECIFY                                          │
│     Developer writes precise task specification      │
│     (equations, interface contract, test cases)      │
│     Time: 30 min – 2 hours                          │
├─────────────────────────────────────────────────────┤
│  2. GENERATE                                         │
│     Claude writes code + tests + documentation       │
│     Time: 1 hour – 1 day                            │
├─────────────────────────────────────────────────────┤
│  3. REVIEW                                           │
│     Developer reads code, checks physics, runs       │
│     unit tests, verifies compilation                 │
│     Time: 1 – 4 hours                               │
├─────────────────────────────────────────────────────┤
│  4. ITERATE                                          │
│     If issues found → give Claude the error/output   │
│     → Claude fixes → back to step 3                  │
│     Iterations: typically 1–3                        │
├─────────────────────────────────────────────────────┤
│  5. VALIDATE                                         │
│     Run convergence test / benchmark                 │
│     Developer executes on HPC                        │
│     Time: hours – weeks (simulation dependent)       │
├─────────────────────────────────────────────────────┤
│  6. ANALYZE                                          │
│     Give results to Claude                           │
│     Claude produces plots, tables, interpretation    │
│     Time: 1 – 4 hours                               │
└─────────────────────────────────────────────────────┘
```

**Key principle:** The developer's time is spent on steps 1 and 5. Claude handles 2, 4, and 6. Step 3 is shared. This maximizes the value of both human expertise and AI capability.

---

# Summary Table — Everything at a Glance

| Task | Claude time | Human time | Sim/HPC time | Total |
|---|---|---|---|---|
| New C++ module (small) | 1h | 4h | — | 1 day |
| New C++ module (large) | 8h | 3d | — | 1 week |
| GPU kernel port (full) | 2w | 2w | — | 2–4 weeks |
| Unit test suite (20 tests) | 4h | 2h | — | 1 day |
| Bug fix (NaN crash) | 2h | 4h | 2h rerun | 1 day |
| Convergence test (1 case) | 2h | 1h | 1h–7d | 1–7 days |
| Convergence test (full suite) | 5d | 2d | 1–4 months | 1–4 months |
| SXS validation (20 cases) | 1w | 2w | 3–6 months | 3–6 months |
| Parameter calibration (4D sweep) | 2d | 1d | 2 weeks | 2–3 weeks |
| EOS sensitivity study | 5d | 1w | 2–6 months | 2–6 months |
| Doxygen (full project) | 2d | 1d | — | 3 days |
| Paper draft (methods paper) | 2d | 5d | — | 1 week |
| AMR implementation | 5d | 2w | 1w testing | 2–3 weeks |
| Sommerfeld BC | 8h | 1d | 4h testing | 2 days |
| Plugin architecture | 2w | 2w | 1w testing | 3–4 weeks |
| User templates + CLI | 5d | 3d | 1d testing | 1–2 weeks |
| Checkpoint restart | 8h | 4h | 2h testing | 1–2 days |
