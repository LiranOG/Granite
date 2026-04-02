# GRANITE v0.5.0 — Full Technical Audit & Upgrade Roadmap

**Date:** April 1, 2026  
**Engine:** GRANITE — General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics  
**Scope:** Complete codebase review + document synthesis (Grok Audit PDF + IDEAS FOR PROJECTS doc) + 10 new upgrade recommendations

---

## Part A — Summary of "IDEAS FOR PROJECTS" Document

The Google Doc outlines what Claude Opus/Sonnet can accomplish for GRANITE development. Key categories:

### A.1 Code Tasks (Creation, Debugging, Refactoring)
- **New module creation** (C++/Python): Expected 1 hour–5 days per module depending on complexity (e.g., a new Riemann solver is 2–5 days).
- **Debugging**: Minutes for syntax issues, 1–2 days for deep MPI race conditions or timing bugs.
- **Refactoring/optimization**: 2 hours for local changes, 3–7 days for architectural changes like full AMR.

### A.2 Testing
- **Unit tests** (GoogleTest): 15–30 min per function, 1–2 days for a full suite.
- **Validation** (vs SXS/BHAC): Scripting is 1–2 days; actual simulation runtime depends on HPC resources (days–weeks per binary BH run at 2 orbits).

### A.3 Documentation
- Doxygen comments, README, CHANGELOG, and academic papers — all feasible in hours to days.

### A.4 Data Analysis
- Python scripts for log/HDF5 processing, mismatch computation, convergence-order analysis — 1–4 hours per script.

### A.5 Architecture Planning
- Module/interface design, experiment matrices, cost estimation — hours to days.

### A.6 Key Caveats from the Document
- Claude cannot **run** heavy simulations (hardware-dependent).
- Claude cannot **replace** the physicist's deep understanding of results.
- Timing/race-condition bugs need real test runs, not just code review.
- Estimated timeline from v0.5.0 → v1.0 validated: **weeks** with AI assistance vs months without, contingent on compute resources.

---

## Part B — Synthesis of Grok Audit PDF Findings

### B.1 "Do Not Touch" — Production-Grade Components (7 systems)

| System | Score | File(s) |
|--------|-------|---------|
| GridBlock (flat contiguous, H2 fix) | 10/10 | grid.hpp + grid.cpp |
| HLLD Riemann solver (7 waves, CT) | 10/10 | hlld.cpp |
| GRMHD core (C1+C3 fixes, wavespeeds) | 9.9/10 | grmhd.cpp |
| NaN diagnostics (dev_benchmark.py) | 10/10 | dev_benchmark.py |
| CCZ4 evolution (KO dissipation, H1 fix) | 9.8/10 | ccz4.cpp |
| Tabulated EOS (tri-linear, NR+bisection) | 9.8/10 | tabulated_eos.cpp |
| Type system (symIdx, constexpr, enums) | 10/10 | types.hpp |

**Verdict:** The technical core (GridBlock, HLLD, CT, KO, EOS) is publication-grade. Do not refactor these.

### B.2 Stubs & Missing Infrastructure (6 critical gaps)

1. **AMR** — `amr.cpp` is single-level stub. `regrid()`, `prolongate()`, `restrict_data()` are empty. `fillGhostZones()` copies only interior (not multi-level).
2. **Initial Data** — `BowenYorkPuncture::solve()` doesn't call PETSc for the elliptic constraint. No real multigrid solver at scale.
3. **Radiation/Neutrino Coupling** — M1 and leakage exist in separate files but are **not wired** to the main evolution loop. `computeRHS` in grmhd does not include radiation sources.
4. **GW Extraction (Python)** — `gw.py` has modes (ℓ,m) for ℓ≤2 partially stubbed. No spherical-data HDF5 writer.
5. **Multi-block MPI** — `syncGhostZones` in main.cpp works for single-level but does **not** handle AMR inter-level communication. `redistributeBlocks` is a stub.
6. **Domain-size crash** — Single puncture crashes at t≈6.25M because the gauge wave hits the boundary. Domain is too small (±16M default), needs ±32M or a `--large-domain` flag.

### B.3 Architectural Strengths & Weaknesses

**Strengths:**
- Dependency injection (params + EOS pointer) — clean.
- Flat GridBlock (H2+H3) — significant performance gain.
- OpenMP collapse(3) + MPI non-blocking — HPC-ready for single level.

**Weaknesses:**
- Functions in `ccz4.cpp`, `grmhd.cpp`, and `main.cpp` are excessively long (1000+ lines each) — hard to maintain.
- Ghost-zone filling code is duplicated between AMR and main.
- NaN handling is still ad-hoc (floors only, no configurable flag).
- AMR is a stub — no prolongation/restriction operators exist.

### B.4 Performance Assessment

- **Single-node (flat layout + OMP):** Very good.
- **Multi-node:** Weak — AMR doesn't exist, so can't scale beyond single block.
- **Memory:** Excellent — single flat allocation per GridBlock.
- **Cache:** Excellent — H3 fix (spatial-outer, var-inner loop order).

---

## Part C — Codebase Deep Dive: Current State of Every Module

### C.1 main.cpp (1,135 lines)
- Complete SSP-RK3 integrator with `BlockBundle` pattern.
- Ghost-zone sync via MPI non-blocking `Isend/Irecv` — works for single level.
- Supports 5 initial data types: `brill_lindquist`, `bowen_york`, `tov_star`, `bns`, `magnetar`.
- **Gap:** No neutrino/radiation source terms in the RK3 substeps.
- **Gap:** NaN scan only for first 20 steps (hardcoded).
- **Gap:** No checkpoint restart — writes checkpoints but no load-from-checkpoint code path.

### C.2 ccz4.cpp (56K, ~1,400 lines)
- Full 22-variable CCZ4 system with 4th-order FD.
- `d1`, `d1up` (advection), `d2` stencils correctly implemented.
- KO dissipation in single OMP region (H1 fix confirmed).
- Constraint computation (`computeConstraints`) present and correct.
- **Concern:** The `computeRHS` function is monolithic — over 600 lines of physics in one scope.

### C.3 grmhd.cpp (45K, ~1,100 lines)
- Valencia formulation with HLLE (GR-aware, C3 fix).
- HLLD solver in separate `hlld.cpp` (20K) — complete with CT.
- PPM, PLM, MP5 reconstruction all present.
- Con2Prim with Newton-Raphson + Palenzuela fallback.
- EOS-exact sound speed (C1 fix confirmed).
- **Gap:** No WENO reconstruction option (useful for discontinuities).

### C.4 amr.cpp (269 lines)
- `AMRHierarchy::initialize()` creates a single level-0 block.
- `regrid()` is empty stub.
- `prolongate()` / `restrictData()` exist as method signatures but are stubs.
- `gradientChiTagger` — the tagging function exists and computes gradients, but `regrid()` never calls it.
- `fillGhostZones(level)` — only does same-level interior copy.
- **Critical:** This is the #1 blocker for production use.

### C.5 tabulated_eos.cpp (29K)
- Full StellarCollapse HDF5 format reader.
- Tri-linear interpolation in (log₁₀ρ, log₁₀T, Yₑ) space.
- Newton-Raphson T-inversion with bisection fallback.
- Beta-equilibrium solver for cold NS initial data.
- **Solid:** Publication-ready. No changes needed.

### C.6 initial_data.cpp (30K)
- `BrillLindquist` — analytic conformal factor, works.
- `BowenYorkPuncture::solve()` — sets up the linear system but defaults to the Brill-Lindquist fallback if PETSc is not enabled.
- `TOVSolver` — correct CGS→geometric unit conversion (1e5 cm/km, not RSUN).
- `BNSGenerator` — superposition of two TOV stars with boost.
- **Gap:** No Kerr-Schild initial data for spinning BH tests.

### C.7 neutrino.cpp (16K) + m1.cpp (17K)
- `NeutrinoTransport` — leakage rates (Bruenn 1985), optical depth, Yₑ evolution.
- `M1Transport` — Minerbo closure, free-streaming/diffusion interpolation.
- Both modules are **self-contained and tested individually** but are **never called from main.cpp**.
- **Critical:** Wiring these into the main evolution loop is the #2 physics priority.

### C.8 postprocess.cpp (25K) + horizon_finder.hpp
- `Psi4Extractor` — computes Ψ₄ on coordinate spheres, mode decomposition.
- `EMDiagnostics` — Blandford-Znajek jet power, accretion rate, Eddington luminosity.
- `RemnantAnalyzer` — recoil velocity, final mass/spin.
- `ApparentHorizonFinder` — flow method (Gundlach 1998), spin from isolated-horizon.
- **Gap:** No Wigner d-matrix for full mode rotation. `gw.py` has it but not the C++ side.

### C.9 Python Analysis (gw.py, plotting.py, reader.py, dev_benchmark.py)
- `gw.py` (507 lines) — Ψ₄ modes, FFI strain, energy/momentum spectra, recoil. Well-implemented for ℓ≤4.
- `plotting.py` — matplotlib wrappers.
- `reader.py` — HDF5 timeseries reader.
- `dev_benchmark.py` — NaN forensics, phase classification, growth-rate analysis, CFL advection checks. This is an excellent diagnostic tool.

---

## Part D — URGENT Action Items (from Audit PDF, verified against code)

### D.1 [BLOCKER] AMR → Multi-Level Implementation
- **File:** `amr.cpp`
- **Task:** Implement `regrid()` with Berger-Rigoutsos cell clustering, `prolongate()` with trilinear interpolation, `restrict()` with volume-average.
- **Why:** Without multi-level AMR there is no adaptive refinement. The engine runs a uniform grid and cannot resolve both the near-zone (puncture) and wave zone simultaneously.
- **Physics impact:** Cannot do production binary mergers.

### D.2 [BLOCKER] Domain-Size Crash Fix
- **File:** `main.cpp` + params.yaml
- **Task:** Increase default domain from ±16M to ±32M or add `--large-domain` CLI flag. Alternatively, implement sponge-layer / Sommerfeld outgoing-wave boundary conditions.
- **Why:** Gauge wave reaches boundary at t≈6.25M and reflects back, causing NaN.
- **Verified:** The NAN_DEBUG_BRIEF documents this exact failure mode.

### D.3 [HIGH] Wire Radiation + Neutrino into Main Loop
- **File:** `main.cpp` → `TimeIntegrator::sspRK3Step`
- **Task:** After `grmhd.computeRHS()`, call `neutrino.computeLeakageRates()` and add `Q_cool/Q_heat` as source terms to the GRMHD energy and Yₑ equations. Optionally evolve M1 moments as additional conserved variables.
- **Why:** This is the core science of the project — without neutrino coupling, neutron star mergers produce no neutrino signal and ejecta composition (r-process) is wrong.

---

## Part E — 10 Additional Upgrades (Beyond Documents)

These are upgrades that were **not mentioned** in either the audit PDF or the IDEAS document, but are essential for a competitive NR engine:

### E.1 GPU Acceleration Backend (CUDA/HIP Kernels)
**Status:** CMake has `GRANITE_ENABLE_GPU` and `GRANITE_GPU_BACKEND` options, but no actual GPU kernel code exists.

**What to implement:**
- Port the three hottest loops to GPU: (a) CCZ4 RHS evaluation, (b) GRMHD flux computation, (c) Con2Prim.
- Use a portable abstraction layer (Kokkos or custom `granite::parallel_for`) so the same source compiles for CPU (OpenMP), NVIDIA (CUDA), and AMD (HIP).
- The flat `data_[var * stride + flat(i,j,k)]` layout is already GPU-friendly — no SoA conversion needed.

**Why critical:** SpECTRE, KHARMA, H-AMR all run on GPUs. Without GPU support, GRANITE cannot compete at petascale. A single A100 delivers ~10× speedup over a full CPU node for structured-grid stencil codes.

**Estimated effort:** 2–4 weeks for initial port of CCZ4+GRMHD kernels.

### E.2 Checkpoint Restart (Fault Tolerance)
**Status:** `HDF5Writer::writeCheckpoint()` exists and writes data, but there is **no** `loadCheckpoint()` function anywhere.

**What to implement:**
- Add `HDF5Reader::loadCheckpoint()` that reads grid data, step counter, time, and all BlockBundle fields.
- Add CLI flag `--restart <checkpoint.h5>` to main.cpp.
- Store RNG state for any stochastic processes (turbulence seeding).

**Why critical:** Production BNS simulations take weeks. A crash at step 500,000 without restart means total loss. Every serious NR code has checkpoint/restart.

**Estimated effort:** 2–3 days.

### E.3 Sommerfeld / Absorbing Outer Boundary Conditions
**Status:** Current BCs are zeroth-order outflow (copy from interior) — a known source of reflections.

**What to implement:**
- Sommerfeld radiative BC: ∂_t u + (v/r)(u - u₀) + v ∂_r u = 0 for each variable.
- For lapse: u₀ = 1. For shift: u₀ = 0. For conformal metric perturbations: u₀ = 0.
- Apply at all 6 faces of the domain.

**Why critical:** This directly fixes the domain-size crash at t≈6.25M and allows smaller domains (less memory).

**Reference:** Ruiz et al. (2008); Alcubierre (2008) §11.3.

**Estimated effort:** 1–2 days.

### E.4 User-Facing Simulation Template System
**Status:** The IDEAS doc mentions the desire for users to create their own simulations, but no template infrastructure exists.

**What to implement:**
- A `templates/` directory in the repo with documented YAML parameter files for common scenarios: single BH, binary BH, single NS (TOV), binary NS, magnetar collapse, BH-NS.
- Each template includes: `params.yaml`, `README.md` explaining physics, expected runtime, and expected outputs.
- A Python CLI tool `granite-setup <template-name> [--mass1 1.4 --mass2 1.2 ...]` that generates a ready-to-run directory.
- Documentation showing how to write custom initial data classes that plug into the existing `InitialDataGenerator` interface.

**Why critical:** This is the single most impactful feature for community adoption. SpECTRE and Einstein Toolkit both provide example parameter files.

**Estimated effort:** 3–5 days for 6 templates + CLI tool.

### E.5 WENO-Z Reconstruction
**Status:** PPM, PLM, and MP5 are implemented. No WENO variant.

**What to implement:**
- WENO-Z 5th-order reconstruction (Borges et al. 2008).
- Drop-in replacement selectable via `params.yaml: reconstruction: WENO5Z`.
- Reduces spurious oscillations near shocks compared to MP5 while maintaining high order.

**Why critical:** WENO is the standard in modern GRMHD codes (KHARMA, H-AMR, AthenaK). It handles contact discontinuities and magnetically-dominated regions more robustly.

**Estimated effort:** 2–3 days (the reconstruction interface already exists in grmhd.cpp).

### E.6 In-Situ Visualization Pipeline (VTK/ADIOS2 Output)
**Status:** Output is HDF5 timeseries only. No 3D volume output for visualization tools.

**What to implement:**
- Add VTK-XML (`.vti`) output for 3D grid data at configurable intervals.
- Or integrate ADIOS2 for streaming output compatible with ParaView Catalyst.
- Include a Python script to generate ParaView `.pvd` time-series files.

**Why critical:** Researchers need to see their simulations. Every competitor (SpECTRE, GRChombo, Einstein Toolkit) has visualization output. Without it, GRANITE cannot be used for publications that require figures.

**Estimated effort:** 2–3 days for VTK output, 1 week for full ADIOS2.

### E.7 Adaptive Time-Stepping with Subcycling
**Status:** Fixed global dt from CFL on the base grid. No subcycling.

**What to implement:**
- Once AMR is active, each refinement level should evolve at dt/2^level (subcycling in time).
- Requires flux-matching at coarse-fine boundaries (refluxing).
- Store intermediate RK3 states at level boundaries for temporal interpolation of ghost zones.

**Why critical:** Without subcycling, the finest level forces the entire grid to use its small dt, making AMR almost useless. This is a fundamental requirement for efficient AMR.

**Reference:** Berger & Colella (1989); GRChombo implementation.

**Estimated effort:** 1–2 weeks (tightly coupled with AMR implementation).

### E.8 Mixed-Precision Support (FP32 for non-critical variables)
**Status:** Everything is `Real = double` (64-bit). No mixed-precision option.

**What to implement:**
- Keep metric (γ̃ᵢⱼ, χ, K) and gauge (α, βⁱ) in FP64.
- Allow atmosphere GRMHD cells and KO dissipation to use FP32.
- On GPUs, this doubles throughput for FP32 kernels (tensor cores: 8× for FP16→FP32).
- Add CMake option `GRANITE_MIXED_PRECISION` and a `RealLow` type alias.

**Why critical:** GPU performance is memory-bandwidth-limited. Mixed precision reduces data movement by 30-50% with negligible accuracy loss in non-critical regions.

**Estimated effort:** 1 week.

### E.9 CI/CD Integration Testing with Physics Validation
**Status:** CI runs unit tests (92 tests, 100% pass). No integration tests that validate physics.

**What to implement:**
- Add a CI job that runs a short gauge-wave test (10 crossing times) and checks:
  - Convergence order ≥ 3.5 (expect 4.0 for 4th-order FD).
  - L2 norm decay rate matches analytical prediction.
- Add a TOV star stability test: evolve for 5ms, check central density drift < 1%.
- Store reference data in `tests/reference_data/` for regression testing.

**Why critical:** Without physics validation in CI, a refactoring commit could silently break convergence order or introduce a sign error in a Christoffel symbol.

**Estimated effort:** 2–3 days.

### E.10 Multi-Physics Plugin Architecture
**Status:** Physics modules (CCZ4, GRMHD, neutrino, M1) are hardcoded in main.cpp. Adding a new physics module requires modifying main.cpp.

**What to implement:**
- A `PhysicsModule` abstract base class with:
  ```cpp
  class PhysicsModule {
  public:
      virtual void computeRHS(const GridBlock& state, GridBlock& rhs, Real t) = 0;
      virtual int numVars() const = 0;
      virtual std::string name() const = 0;
  };
  ```
- A `PhysicsDriver` that owns a `vector<unique_ptr<PhysicsModule>>` and orchestrates the RK3 step.
- Registration via YAML: `physics: [ccz4, grmhd, neutrino_leakage, m1]`.
- Users can write custom physics modules (e.g., resistive MHD, scalar-tensor gravity) without touching the core engine.

**Why critical:** This is what makes the engine "flexible for every user" — the stated vision. Without it, every new physics addition requires deep knowledge of main.cpp internals.

**Estimated effort:** 1–2 weeks for the full architecture refactor.

---

## Part F — Priority-Ordered Master Roadmap

### Tier 1: URGENT / BLOCKERS (must fix for any production run)

| # | Task | Files | Effort | Impact |
|---|------|-------|--------|--------|
| 1 | AMR multi-level (prolongate + restrict + regrid) | amr.cpp | 2–3 weeks | Enables adaptive resolution |
| 2 | Domain-size fix + Sommerfeld BC | main.cpp, ccz4.cpp | 2–3 days | Fixes t≈6.25M crash |
| 3 | Wire neutrino+radiation to main loop | main.cpp | 3–5 days | Core science capability |
| 4 | Checkpoint restart | main.cpp, hdf5_io | 2–3 days | Fault tolerance |

### Tier 2: MEDIUM / Feature Completeness

| # | Task | Files | Effort | Impact |
|---|------|-------|--------|--------|
| 5 | GPU backend (CUDA/HIP kernels) | new gpu/ directory | 2–4 weeks | 10× performance |
| 6 | User simulation templates + CLI | templates/, scripts/ | 3–5 days | Community adoption |
| 7 | PETSc elliptic solver for Bowen-York | initial_data.cpp | 1 week | Full initial data support |
| 8 | Full GW extraction (Wigner d + HDF5 writer) | postprocess.cpp, gw.py | 1 week | Publication-ready waveforms |
| 9 | VTK/ADIOS2 visualization output | new io/ module | 3 days | Enables 3D visualization |
| 10 | WENO-Z reconstruction | grmhd.cpp | 2–3 days | Better shock handling |

### Tier 3: LOW / Refactoring & Future

| # | Task | Files | Effort | Impact |
|---|------|-------|--------|--------|
| 11 | Plugin architecture (PhysicsModule) | main.cpp refactor | 1–2 weeks | Extensibility |
| 12 | Adaptive subcycling | amr.cpp, main.cpp | 1–2 weeks | AMR efficiency |
| 13 | Mixed-precision (FP32/FP64) | types.hpp, kernels | 1 week | GPU throughput |
| 14 | CI physics validation (convergence tests) | tests/, CI yaml | 2–3 days | Regression safety |
| 15 | Split long functions (ccz4/grmhd/main) | ccz4.cpp, grmhd.cpp | 1 week | Maintainability |
| 16 | C++23 `std::mdspan` for GridBlock | grid.hpp | 3 days | Modern API |
| 17 | Configurable NaN scan flag | main.cpp, params | 1 day | Debugging flexibility |

---

## Part G — Overall Assessment

### What GRANITE Does Exceptionally Well
The core physics engine — CCZ4 + GRMHD + HLLD + CT + EOS — is genuinely publication-grade. The flat GridBlock design, the cache-optimized loop ordering, and the clean EOS abstraction are comparable to what you'd find in established NR codes. The `dev_benchmark.py` diagnostic tool is outstanding.

### What Needs to Happen for v1.0
The engine has approximately 70% of the physics required for a first paper, but only about 40% of the infrastructure. The three critical gaps are: (1) AMR, (2) radiation coupling, and (3) GPU support. With these three, GRANITE becomes competitive with existing tools. Without them, it's a well-engineered single-block code that can run gauge-wave tests but not real mergers.

### Realistic Timeline to v1.0 (Validated)
With focused development and AI-assisted implementation:
- **Tier 1 (blockers):** 4–5 weeks
- **Tier 2 (features):** 6–8 weeks (partially overlapping with Tier 1)
- **Tier 3 (polish):** ongoing
- **Total to v1.0-rc1:** approximately 10–12 weeks

This aligns with the Grok audit's estimate that GRANITE is "very close" to being an engine-level peer of Einstein Toolkit / GRChombo, with roughly 30% of the feature set still missing.
