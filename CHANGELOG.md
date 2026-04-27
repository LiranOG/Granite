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

Audit remediation (P0–P3 findings resolved), VORTEX Gold Master polish, Phase 3 GitHub infrastructure hardening, and full API synchronization of smoke tests. All 107 tests across 20 suites compile and pass with zero errors and zero warnings under GCC-12 and Clang-18. This release marks the completion of the comprehensive 4-phase GRANITE audit, bringing the engine to a professional, Tier-1 Numerical Relativity standard.

### Added
- **Physics Smoke Tests (100% Clean Build):** API-accurate smoke tests for AMR (`test_amr_basic.cpp`, 5 tests), Horizon Finder (`test_schwarzschild_horizon.cpp`, 3 tests), M1 Radiation (`test_m1_diffusion.cpp`, 4 tests), and HDF5 I/O (`test_hdf5_roundtrip.cpp`, 3 tests). All compile against the core API with zero warnings. Total test count: 92 → **107 tests** across **20 test suites**.
- **Repository Standards:** Established complete GitHub community standards including `CODEOWNERS`, Issue/PR templates, and detailed Theory documentation stubs in `docs/theory/`.
- **VORTEX Gold Master:** Zen Mode (`Z`), GW Audio Chirp Synthesizer, Cinematic Autopilot, NR Diagnostics (Chart.js), Minimap 3.0 (isobar/flux sensor modes), FWM 5-pass hardening, Master Menu categorization.

### Changed
- **Infrastructure:** Full metadata sync (CMake, PyPI, Zenodo) to v0.6.7, including unified authorship (Liran M. Schwartz).
- **Documentation:** `README.md` and `BENCHMARKS.md` reframed for complete accuracy and transparency. `CHANGELOG.md` condensed to a standards-compliant summary with the full journal archived at `docs/DEVELOPMENT_JOURNAL.md`.
- **Configuration:** Translated localized Hebrew comments to English within configuration files (`benchmarks/B2_eq/params.yaml`).

### Fixed
- **Core C++ Logic:** Resolved critical issues in the CCZ4 Ricci tensor, AMR grid headers, and Bowen-York solver labels.
- **Physics Output:** `postprocess::computeRecoilVelocity` changed from a silent zero-return stub to `std::runtime_error` to prevent invalid physical outputs.
- **Formatting & Metadata:** Expanded `.gitignore` to a comprehensive 70-line configuration, corrected `docs/conf.py` Doxygen paths, and removed desk-reject trigger tags in LaTeX manuscripts.

### Security
- **CI/CD Overhaul:** Removed silent warning flags, enforced strict compilation gates (cppcheck and clang-format now block builds on failure), and updated `SECURITY.md` to clearly define the supported version matrix.

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
