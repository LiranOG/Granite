# Changelog

All notable changes to **GRANITE** (General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics) are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Full development journal:** The granular, commit-level engineering log (2,300+ lines) is
> archived at [`docs/DEVELOPMENT_JOURNAL.md`](docs/DEVELOPMENT_JOURNAL.md).

---

## [Unreleased]

### In Progress
- Checkpoint-restart (`--resume` CLI flag, v0.7 target)
- M1 radiation coupling into RK3 main loop (v0.7 target)
- GPU porting via CUDA kernels (v0.7 target)

---

## [v0.6.7] — 2026-04-27

### Summary

The **Gold Master & Repository Seal** release. This major milestone brings the GRANITE engine to a Tier-1 professional standard by finalizing the VORTEX cinematic experience and successfully completing a comprehensive 4-phase architectural audit. The release guarantees a 100% clean CI/CD build (107 tests across 20 suites), enforces strict documentation coherence, and formally establishes the project's individual-architect identity.

### Added
- **VORTEX Gold Master (Cinematic & Audio):** Transformed the WebGL engine into a professional presentation environment. Features include a zero-allocation Gravitational Wave Audio Sonification Synthesizer (pitch/strain mapped to physics), a global Zen Mode (`Z`) for clean capture, a Cinematic Autopilot Camera Mode, and a Master Volume Control Panel.
- **C++ Smoke Tests (API-Synchronized):** Integrated 4 new physics smoke test suites (`test_amr_basic.cpp`, `test_schwarzschild_horizon.cpp`, `test_m1_diffusion.cpp`, `test_hdf5_roundtrip.cpp`). The test matrix now comprises **107 tests across 20 test suites**, achieving broad coverage of all major physics modules.
- **Repository Metadata:** Created `include/README.md` to map the C++ header architecture. Added a `.gitattributes` Linguist override to enforce `C++` dominance in GitHub repository statistics by properly identifying UI and scripting components as vendored/undetectable.

### Changed
- **Identity Purge & Voice Realignment:** Executed a repository-wide purge of the legacy "GRANITE Collaboration" entity, permanently replacing it with the authentic "Liran M. Schwartz" single-author attribution across 37 files (headers, `LICENSE`, LaTeX manuscripts). Realigned all documentation prose from group-centric ("We/Our") to individual-architect ("I/The").
- **Documentation Coherence:** Stripped non-professional artifacts (emojis) from technical theory documents to enforce an academic tone. Conducted an anti-truncation sweep to ensure all directory trees in `README.md` files precisely match the physical filesystem. Synchronized all scattered version claims to `v0.6.7`.

### Fixed
- **C++ API Hallucinations & Compilation:** Surgically repaired hallucinated APIs and signatures in the new smoke tests. Fixed signedness warnings, undeclared macros (`NUM_RADIATION_VARS`), and HDF5 nested group (`H5Gcreate2`) logic to achieve a flawless GCC-12 / Clang-18 build with zero errors and zero warnings.
- **CI/CD Pipeline Stabilization:** Resolved Sphinx build failures by forcing `docs/Makefile` tracking. Eliminated cross-platform `clang-format` (v18 vs v19) disagreements by disabling `AlignOperands` and refactoring multi-line `std::ostringstream` chains.
- **UX Polish (VORTEX):** Implemented an ESC-abort system for atomic cancellation of body placement and drag-to-spawn operations. Resolved multiple UI overlapping z-index issues.

---

## [v0.6.6] — 2026-04-12

### Summary

Integration of VORTEX WebGL N-body engine into `viz/vortex_eternity/`. Foundational architectural step toward decoupling the C++ HPC backend from interactive 3D rendering.

### Added
- **VORTEX engine:** 4th-order Hermite integrator, 2.5PN radiation reaction, Kahan summation, GLSL Schwarzschild lens shader, real-time GW strain telemetry.
- **Post-Newtonian physics:** 1PN (EIH), 1.5PN (Lense-Thirring/Rodrigues rotation), 2PN (spin-spin + QM), 2.5PN (radiation reaction).
- `viz/vortex_eternity/VORTEX-engine.html` — single-file browser engine, no install required.

---

## [v0.6.5] — 2026-04-07

### Summary

Tactical Reset: forensic rescue restoring verified production-stable baseline. Both `single_puncture` and `B2_eq` reach t=500M with `‖H‖₂` decaying monotonically.

### Added
- `benchmarks/gauge_wave/params.yaml` — Alcubierre et al. (2004) gauge wave benchmark.
- `benchmarks/B2_eq/params.yaml` — production-grade equal-mass BBH parameter file.
- `benchmarks/validation_tests.yaml` — machine-readable validation test suite (3 physics sectors, 9 tests).
- 2 new selective advection unit tests (test count: 90 → 92).
- `scripts/sim_tracker.py` — procedural live dashboard with 8-layer stability guard.
- PPM reconstruction (Colella & Woodward 1984) — 5 new unit tests.

### Fixed
- **Architecture:** Master reset of `ccz4.cpp`, `amr.cpp`, `main.cpp` to verified v0.6.0 baseline.
- **Memory safety:** `levels_.reserve()` in `AMRHierarchy::initialize()` — prevents reallocation-triggered UB during subcycling.
- **Singularity avoidance:** `MICRO_OFFSET = 1.3621415e-6` re-injected universally.
- **H2:** `GridBlock` flat contiguous allocation — 22 heap allocs → 1 per block.
- **H3:** RHS zero-out loop order — spatial outermost, var innermost.
- **EOS bug (C1):** `soundSpeed()` used instead of hardcoded Γ=1.
- **TOV unit bug:** `1.0e5 cm/km` instead of `RSUN_CGS`.

---

## [v0.6.0] — 2026-04-04

### Summary

Berger-Oliger AMR + BBH initial data + diagnostic overhaul. Engine transitioned from single-grid to full AMR hierarchy.

### Added
- Full Berger-Oliger recursive subcycling (`subcycle()`).
- `TwoPuncturesBBH` spectral initial data — Newton-Raphson Hamiltonian constraint solve.
- Tracking spheres for puncture-following AMR refinement.
- `scripts/dev_benchmark.py` — per-step NaN forensics and lapse monitoring.
- Block-merging algorithm preventing MPI deadlocks for close binaries.

### Fixed
- **C3 (HLLE flat metric bug):** `GRMetric3` promoted to public interface — GR fluxes now correct.
- **H1 (KO dissipation OMP):** 22 separate OpenMP regions → 1 region (var loop innermost).
- Prolongation origin off-by-N bug causing fine ghost cell corruption.
- `setLevelDt()` cascade fixing "Zombie Physics" frozen fine grids.
- Chi-blended selective upwinding: `χ < 0.05` → centered FD; `χ ≥ 0.05` → 4th-order upwinded.
- Sommerfeld radiative BCs implemented and wired.

### Changed
- Test count: 90 (from 88 in v0.5.0).
- `VERSION 0.5.0` → `VERSION 0.6.0` in `CMakeLists.txt`.

---

## [v0.5.0] — 2026-04-01

### Summary

Repository reorganization to professional production standards. Security and CodeQL scanning configured. Phase 5 GRMHD completions.

### Added
- `scripts/` directory; relocated `run_granite.py`, `dev_benchmark.py`, `dev_stability_test.py`.
- `.github/` directory; relocated `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- `docs/` restructured — `INSTALL.md`, `internal/` developer notes.
- `SECURITY.md` — GitHub private vulnerability reporting, 30-day patch SLA.
- `.github/workflows/codeql.yml` — CodeQL C++ + Python scanning.
- `python/granite_analysis/gw.py`: `spin_weighted_spherical_harmonic()` — full Wigner d-matrix implementation (Goldberg 1967).
- `python/granite_analysis/gw.py`: `compute_radiated_momentum()` — full Ruiz-Campanelli-Zlochower (2008) recoil kick.

### Changed
- Root directory reduced to 8 essential files.
- All documentation path references updated to new `docs/` structure.

---

*GRANITE — [GPL-3.0](LICENSE) — Liran M. Schwartz — 2026*
