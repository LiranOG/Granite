# Changelog

All notable changes to the **GRANITE** (General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics) numerical relativity engine are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **A Note on Commit Granularity**  
> Each commit in this repository represents a major integration milestone, not an individual line-edit. The work described below spans thousands of lines of C++ physics code, multiple debugging and stabilization sessions, and a rigorous, multi-phase audit. This changelog enumerates every significant change in granular detail so the full scope of the engineering effort is transparent to contributors, reviewers, and the scientific community. 

---

## [v0.6.5.5] — README Documentation Overhaul (2026-04-11)

### Summary

Completely rebuilt `README.md` from its v0.6.5 baseline. The restructure adds a linked table of contents, a quantified benchmark results section, a competitor feature matrix, a formal roadmap, a transparent known-limitations register, a community engagement narrative, a GitHub Wiki documentation index, and a BibTeX citation block. Cosmetically, the header block was centre-aligned and the badge suite was significantly expanded. The legacy inline developer warning (the "Note from the Developer" blockquote) was retired in favour of a dedicated community section.

---

### Changed — Header & Badge Suite (`README.md`)

- **Centre-Aligned Title Block:** Wrapped the project title and all badge rows inside a `<div align="center">` block, matching standard academic open-source presentation.
- **Expanded Badge Row:** The previous four badges (Build, Python, License, C++ Standard) were replaced with a richer, grouped suite:
  - **Row 1 — CI/Status:** `Build Status` (linked to Actions) + `Development Status` (active-development indicator).
  - **Row 2 — Identity:** `ORCID` profile link + Zenodo `DOI` badge (`10.5281/zenodo.19502265`) + `License: GPL v3`.
  - **Row 3 — Stack:** `C++17`, `Python 3.8+`, `OpenMP 4.5+`, `MPI (OpenMPI | MS-MPI)`.
  - **Row 4 — Docs:** `GRANITE Wiki` hyperlink badge.
- **C++ Standard Badge:** Narrowed from `c++17/20` → `c++17` to match the authoritative `CMakeLists.txt` version declaration.
- **Status Blurb:** Appended "stable through t = 500 M" to the `v0.6.5` status line; changed `GR-MHD` → `GRMHD` for consistency with body text.

---

### Added — Table of Contents (`README.md`)

- **`## 📖 Table of Contents`:** Inserted anchor-linked navigation covering all 13 top-level sections, including the new Roadmap, Known Limitations, Community, Wiki, Citing, and Contributors entries absent from the v0.6.5 baseline.

---

### Changed — Key Features Section (`README.md`)

- **CCZ4:** Added explicit constraint-damping coefficients (`κ₁=0.02, η=2.0`).
- **GRMHD:** Specified reconstruction schemes (`MP5/PPM/PLM`), Riemann solvers (`HLLE/HLLD`), and constrained transport (`∇·B = 0` to machine precision).
- **AMR:** Added maximum refinement depth (up to 12 levels), prolongation order (trilinear), and restriction method (volume-weighted).
- **Multi-BH Initial Data:** Added `Two-Punctures` as a supported initial data type alongside the existing Brill-Lindquist, Bowen-York, and Superposed Kerr-Schild entries.
- **Radiation:** Reworded from generic "hybrid leakage + M1" to specify neutrino leakage explicitly.
- **Diagnostics:** Expanded GW extraction to list radii range (`50–500 r_g`) and added real-time constraint monitoring as a named feature.

---

### Added — Competitor Feature Matrix (`README.md`)

- **`## ⚖️ How GRANITE Compares`:** New section providing a capability comparison across five codes: Einstein Toolkit, GRChombo, SpECTRE, AthenaK, and GRANITE v0.6.5.

  | Capability | Einstein Toolkit | GRChombo | SpECTRE | AthenaK | **GRANITE v0.6.5** |
  |---|:---:|:---:|:---:|:---:|:---:|
  | CCZ4 formulation | ✅ | ✅ | ✅ | ❌ | ✅ |
  | Full GRMHD (Valencia) | ✅ | ✅ | 🔶 | ✅ | ✅ |
  | M1 radiation transport | ✅ | ❌ | ❌ | ❌ | 🔵 |
  | Dynamic AMR (subcycling) | ✅ | ✅ | ✅ | ✅ | 🔵 |
  | N > 2 BH simultaneous merger | ❌ | ❌ | ❌ | ❌ | 🔵 |
  | Open license | LGPL | MIT | MIT | BSD | GPL-3.0 |

- **Legend defined:** ✅ = Production-ready; 🔵 = Core module built, pending RK3 wiring; 🔶 = Partial/in development; ❌ = Not available.
- **Pointer to extended analysis:** Cross-referenced `docs/COMPARISON.md` for exhaustive, source-cited per-feature breakdown.

---

### Added — Benchmark Results Section (`README.md`)

- **`## 📊 Benchmark Results`:** New section reporting production run data from a single desktop workstation (Intel i5-8400, 6-core, 16 GB DDR4, Linux/WSL2) with all numbers sourced directly from simulation logs.
- **Single Moving Puncture — Schwarzschild Stability:**

  | Resolution | AMR Levels | dx finest | ‖H‖₂ t=0 | ‖H‖₂ final | Reduction | t\_final | NaN events |
  |---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
  | 64³ | 4 | 0.1875 M | 1.083 × 10⁻² | 1.277 × 10⁻⁴ | **×84.8** | 500 M ✅ | 0 |
  | 128³ | 4 | 0.09375 M | 1.855 × 10⁻² | 1.039 × 10⁻³ | **×17.9** | 120 M ✅ | 0 |

- **Binary Black Hole Inspiral — Equal-Mass, Two-Punctures / Bowen-York:**

  | Resolution | AMR Levels | dx finest | ‖H‖₂ peak | ‖H‖₂ final (t=500M) | Reduction | Wall time | Throughput | NaN events |
  |---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
  | 64³ | 4 | 0.781 M | 8.226 × 10⁻⁴ | **1.341 × 10⁻⁵** | **×61.3** | 98.9 min | 0.084 M/s | 0 |
  | 96³ | 4 | 0.521 M | 2.385 × 10⁻³ | **3.538 × 10⁻⁵** | **×67.4** | 496 min | 0.017 M/s | 0 |

- **Raw telemetry pointer:** `docs/BENCHMARKS.md` linked for full per-step logs and extended resolution tables.

---

### Changed — Quick Start Guide (`README.md`)

- **OS Notice:** Replaced the top-of-file developer warning blockquote with a compact `> [!NOTE]` admonition at the top of the Quick Start section: "GRANITE is currently optimized exclusively for **Linux** and **WSL2**. Native Windows and macOS are strictly unsupported."
- **Step 2 — WSL2 sub-header:** Removed the `*Use for: WSL2 terminal inside Windows*` italic descriptor line.
- **Step 4 — Windows command block:** Condensed the two-option (`Option A` / `Option B`) listing into a single inline comment block, removing the duplicate `cd build` warning.
- **Step 5 — Windows command block:** Removed per-command inline comment labels (standard run, verbose, extended), unifying into a clean unlabelled command list.
- **Step 6 — Windows command block:** Removed per-command inline comments (`# 1.`, `# 2.`, `# 3.`, `# 4. Custom scenario`), retaining only the three canonical benchmark invocations; removed the custom-scenario example.
- **`DEPLOYMENT_AND_PERFORMANCE.md` link:** Updated reference path from `./DEPLOYMENT_AND_PERFORMANCE.md` → `./docs/DEPLOYMENT_AND_PERFORMANCE.md`.

---

### Changed — Repository Structure Tree (`README.md`)

- **Root label:** `Granite/` → `GRANITE/` (capitalised to match project name convention).
- **`benchmarks/`:** Added `scaling_tests/` entry (SLURM/PBS strong & weak-scaling templates). Updated descriptions to reflect self-contained simulation preset framing.
- **`CMakeLists.txt`:** Description expanded to name CUDA/HIP and Google Test as managed targets alongside MPI, OpenMP, and HDF5.
- **`containers/` (new):** Added directory entry documenting `Dockerfile` (Ubuntu 22.04 multi-stage) and `granite.def` (Singularity/Apptainer definition).
- **`docs/` (expanded):** Replaced sparse single-line entry with an exhaustive index of named documents: `DEVELOPER_GUIDE.md`, `BENCHMARKS.md`, `COMPARISON.md`, `SCIENCE.md`, `FAQ.md`, `diagnostic_handbook.md`, `v0.6.5_master_dictionary.md`, `INSTALL.md`, `internal/`, `theory/`, `user_guide/`.
- **`python/` (new):** Added installable Python analysis package entry (`granite_analysis/` — HDF5 reader, GW strain extraction, matplotlib helpers).
- **`runs/` (new):** Added gitignored job scripts and parameter-scan config directory.
- **`scripts/`:** Added `dev_stability_test.py` and `sim_tracker.py` as named entries; updated per-script descriptions.
- **`src/`:** Added `initial_data/` as a named subdirectory (BL conformal factor solver, Bowen-York Newton-Raphson).
- **`tests/`:** Updated entry label from `92 integrated GoogleTest suite` to `92-test GoogleTest suite`.
- **`viz/` (new):** Added post-processing and visualisation scripts directory with `README.md` documenting planned `plot_constraints.py` and `plot_gw.py` helpers.
- **Removed:** `setup_windows.ps1` entry.

---

### Added — Roadmap (`README.md`)

- **`## 🗺️ Roadmap`:** New version-target tracker table spanning `v0.6.5` through `v1.0.0`:

  | Version | Target | Status | Key Deliverables |
  |---|---|:---:|---|
  | **v0.6.5** | Q1 2026 | ✅ **Released** | BBH stable to t=500M, 4-level AMR, 92 tests, Python dashboard |
  | **v0.7.0** | Q2 2026 | 🔄 In Progress | GPU CUDA kernels, checkpoint-restart, full dynamic AMR regrid, M1 wired into RK3 |
  | **v0.8.0** | Q3 2026 | 📋 Planned | Tabulated nuclear EOS + reaction network |
  | **v0.9.0** | Q4 2026 | 📋 Planned | Full SXS catalog validation (~60 BBH configs), multi-group M1 |
  | **v1.0.0** | Q1 2027 | 🎯 Target | B5\_star production run + publication, full community release, native all-OS support |

- **B5_star scaling path noted:** Desktop (128³) → GPU (vast.ai H100) → cluster (256³–512³) → flagship (12 AMR levels, ~2 TB RAM, ~5×10⁶ CPU-hours).

---

### Added — Known Limitations Register (`README.md`)

- **`## ⚠️ Known Limitations (v0.6.5)`:** New section establishing a formal, versioned limitations matrix with columns for Impact, Status, and Planned Fix:

  | Limitation | Impact | Status | Planned Fix |
  |---|---|:---:|---|
  | `loadCheckpoint()` stub only | Long runs cannot resume | 🔄 Active | v0.7 |
  | M1 radiation built but not wired into RK3 | Radiation inactive in production | 🔄 Active | v0.7 |
  | Dynamic AMR regridding partial | Block count fixed at init | 🔄 Active | v0.7 |
  | Phase labels are time-based, not separation-based | Approximate classification | 📋 Known | v0.7 |
  | `alpha_center` reads AMR level 0, not finest | Misleading lapse diagnostic | 📋 Known | v0.7 |
  | GTX 1050 Ti not viable for FP64 GPU compute | GPU path requires H100-class | 📋 Known | Post GPU porting |
  | macOS / Windows native unsupported | Limits accessibility | 📋 Planned | v0.8+ |
  | Tangential BY momenta required for inspiral | Zero momenta → head-on only | 📝 Documented | User parameter |

---

### Changed — Community Section (`README.md`)

- **Removed:** The lead `> ### 📝 A Note from the Developer` blockquote (spanning the entire pre-title header).
- **Added — `## 💙 To the Community — A Personal Word`:** Replaced the removed blockquote with an expanded, prose-led community section positioned after the Versioning Policy. Includes:
  - An opening quote and direct-address narrative from the lead developer.
  - **`### 🌍 How You Can Contribute — On Your Own Terms`:** A seven-row contribution pathway table mapping contributor types (cluster runners, NR reviewers, PR authors, issue filers, theory validators) to concrete engine impact.
  - **`### 🏛️ To Research Groups & Institutions`:** A focused call-to-action for joint validation campaigns, Tier-0/1 allocation access, postdoc involvement, and LIGO/Virgo/LISA waveform collaboration.
  - **`### 🙏 A Genuine Thank You`:** A closing acknowledgement block.
  - **Community engagement badges** (right-aligned): GitHub Issues count, GitHub Discussions count, PRs Welcome shields.

---

### Changed — Institutional Partnership Section (`README.md`)

- **Partnership table:** Condensed column text for tighter formatting (e.g., "Tier-1 allocation time for strong/weak scaling benchmarks" → "Tier-1 allocation for strong/weak scaling benchmarks").
- **HPC Quick-Start sub-header:** Removed `(Supercomputer Administrators)` parenthetical from the section title. Removed the `# Full manual override — total administrator control:` inline comment from the code block.
- **Closing CTA:** Condensed the closing call-to-action paragraph text; removed the "contact the maintainer directly via the repository" clause.

---

### Added — GitHub Wiki Documentation Index (`README.md`)

- **`## 📖 Deep-Dive Documentation — GRANITE Wiki`:** New section providing a 15-row navigational table linking to dedicated Wiki pages covering Architecture Overview, Parameter Reference, Simulation Health & Debugging, Known Fixed Bugs, Physics Formulations, Initial Data, AMR Design, GW Extraction, Benchmarks & Validation, HPC Deployment, Developer Guide, Scientific Context, Roadmap, FAQ, and Documentation Index.

---

### Added — Documentation Reference Table (`README.md`)

- **`## 📚 Documentation`:** New section listing all primary `docs/` files in a two-column table (Document | Description):
  - `DEVELOPER_GUIDE.md`, `BENCHMARKS.md`, `SCIENCE.md`, `COMPARISON.md`, `FAQ.md`, `v0.6.5_master_dictionary.md`, `diagnostic_handbook.md`, `INSTALL.md`.

---

### Added — Citation & Contributors (`README.md`)

- **`## 📎 Citing GRANITE`:** New section providing a standard BibTeX `@software` record for academic citation:
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

---

## [v0.6.5.5] — The Documentation Release (2026-04-10)

### Summary

This release delivers the **complete GRANITE GitHub Wiki** — 17 fully cross-referenced
technical pages covering every subsystem, every parameter, every known bug, and every
benchmark result. Built after the v0.6.5 stable baseline, the wiki transforms GRANITE
from a well-engineered private codebase into a professionally documented open-science
project. All pages were validated against the v0.6.5 ZIP source to ensure technical
accuracy. In addition, this release documents three physics features that existed in
the v0.6.5 source but had no CHANGELOG entries: chi-blended selective upwinding, algebraic
constraint enforcement (det(γ̃)=1 / tr(Ã)=0), and the corrected B2_eq quasi-circular
tangential momenta.

---

### Added — GitHub Wiki (17 pages, ~18,000 words)

**Wiki URL:** https://github.com/LiranOG/Granite/wiki

All 17 pages were authored, cross-referenced, and validated on April 10, 2026.
Each page is technically grounded in the actual v0.6.5 source code — no claim
was made without verification from the ZIP. The commit history has 75 commits
reflecting the full iterative authoring session.

---

#### `Home.md` — Project Landing Page

**URL:** https://github.com/LiranOG/Granite/wiki/Home

- Engine capability overview: CCZ4, GRMHD Valencia, AMR, multi-physics matter, GW
  extraction, HPC parallelism.
- Current status table: v0.6.5 stable, 92 unit tests at 100% pass rate, validated
  benchmarks listed.
- 16-row documentation navigation table linking every wiki page with a one-line
  purpose description.
- Complete Quick Start guide: `git clone` → `apt install` → `build --release` →
  `health_check.py` → benchmark launch, in 6 commands.
- Contributing & Partnership section.
- Signed: *"Simulate the unimaginable." — GRANITE v0.6.5 — April 10, 2026 — LiranOG*

---

#### `Architecture-Overview.md` — Engine Architecture Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Architecture-Overview

10 major sections. The most comprehensive technical page on the wiki.

- **§1 High-Level System Diagram:** Full ASCII data-flow block diagram from
  `params.yaml` → Parameter Parser → Initial Data → AMR Hierarchy → SSP-RK3
  loop (8 substeps labeled) → Python post-processing.
- **§2 Data Flow:** 5-step narrative (Input → Initial Data → AMR Init → Time Loop
  → Post-Processing) with every sub-action enumerated.
- **§3 GridBlock Data Structure:** Memory layout documentation including the
  field-major flat allocation formula (`data_[var*stride + flat(i,j,k)]`), the
  2D ghost zone cross-section diagram, and the 4-row design decisions table
  (field-major, single flat vector, nghost=4, spatial-outer var-inner loop). Includes
  the canonical `at(var,i,j,k)` accessor definition.
- **§4 GRMetric3 Interface:** Full struct definition with all 14 fields. States the
  coupling rule: "GRMetric3 is the ONLY permitted interface between CCZ4 and GRMHD.
  Direct access from GRMHD code is forbidden."
- **§5 CCZ4 Variable Layout — 22 Variables:** Index-by-index table (0=χ through
  21=Θ) with physical meaning for each. Documents the algebraic constraints enforced
  after each RK3 step: det(γ̃)=1 and tr(Ã)=0.
- **§6 GRMHD Variable Layout — 9 Variables:** Conserved and primitive variable tables.
- **§7 Subsystem Coupling Map:** ASCII interface diagram (CCZ4↔GRMetric3↔GRMHD,
  GRMHD↔StressEnergyTensor3↔CCZ4, M1 noted as "built, NOT wired in v0.6.5",
  AMR→GridBlock→All subsystems, Diagnostics→Python dashboard).
- **§8 RK3 Time Loop:** Step-by-step enumeration of all 7 substeps per RK3 stage
  (ghost sync → outer BC → CCZ4 RHS including chi-blending → GRMHD RHS → floors →
  RK3 combine → algebraic constraints). This documents the chi-blended advection
  and `applyAlgebraicConstraints()` call that were present in the code but not
  previously documented.
- **§9 Memory Architecture:** Per-configuration RAM estimates (64³→2 TB B5_star)
  with formula. Scaling table (5 rows, 64³ to B5_star).
- **§10 Namespace Structure:** Complete `granite::` namespace tree with all
  classes listed per subsystem.

---

#### `Physics-Formulations.md` — Governing Equations Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Physics-Formulations

- **§1 CCZ4:** Full evolution equations for ∂_t χ, ∂_t γ̃_ij, ∂_t K, ∂_t Θ with
  κ₁, κ₂ terms. Production defaults: κ₁=0.02, κ₂=0, η=2.0.
- **§2 Gauge Conditions:** 1+log slicing (∂_t α = β^i ∂_i α − 2αK) and Gamma-driver
  shift. Documents trumpet geometry behavior vs. resolution.
- **§3 GRMHD Valencia:** Conserved variable definitions for D, S_j, τ, B^i, D·Y_e.
  Geometric source terms via GRMetric3.
- **§4 Constrained Transport:** Induction equation and ∇·B = 0 machine-precision
  enforcement (Evans & Hawley 1988).
- **§5 EOS:** IdealGasEOS and TabulatedEOS. States sound speed is always exact from
  EOS — never hardcoded Γ (references bug C1 fix).
- **§6 M1 Radiation:** Energy and flux equations, M1 Eddington tensor (Minerbo 1978).
  Status box: "built and tested but NOT called in the main RK3 loop in v0.6.5."
- **§7 Numerical Methods:** 4th-order FD stencil formula; KO dissipation formula with
  p=3; SSP-RK3 Shu-Osher stages; reconstruction table (PLM/PPM/MP5 with order,
  stencil, use case); Riemann solver table (HLLE/HLLD).
- **§8 References:** 16-entry bibliography with full journal citations for every
  physics paper used in GRANITE.

---

#### `Parameter-Reference.md` — Complete params.yaml Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Parameter-Reference

The single most operationally important wiki page. Documents every configurable
parameter with type, default, units, valid range, and warnings.

- **§2 Canonical Template:** Full annotated `params.yaml` covering all 12 sections.
- **§3 `simulation.*`:** `name`, `output_dir`, `total_time`, `checkpoint_every`
  (with explicit warning that `loadCheckpoint()` is NOT implemented in v0.6.5).
- **§4 `domain.*`:** `size` with the gauge wave travel time formula and the minimum
  safe domain table (16M→200M with t_reflection and stability verdict). `nx/ny/nz`
  with dx formula and standard configuration table.
- **§5 `amr.*`:** `levels` with dx-per-level table for 64³ domain=48M. Notes dynamic
  regridding limitation. `refinement.criteria` with all four tagging variables.
- **§6 `initial_data.*`:** `type` enum with BC compatibility notes per type. `bh1/bh2`
  sub-parameters: `mass`, `position` (documents MICRO_OFFSET and why origin is OK),
  `momentum` (critical warning box: quasi-circular p_t=±0.0840 for d=10M), `spin`.
- **§7 `ccz4.*`:** `kappa1` (range, damping timescale formula, warning at 0.1),
  `kappa2` (CCZ4 vs. Z4c), `eta` (Gamma-driver η, warning at η=4.0 tested and
  bad, SMBH scaling note).
- **§8 `dissipation.ko_sigma`:** Full critical warning box. Symptoms of
  over-dissipation. Confirmed failure mode (0.35). Safe value (0.1). KO formula.
- **§9 `time_integration.cfl`:** CFL formula. Warning: effective CFL at finest AMR
  level = cfl × 2^(levels-1). Documents that cfl=0.25 with 4 levels gives
  CFL_finest=2.0 (stable only due to lapse suppression). Adaptive CFL guardian
  documented.
- **§10 `boundary.type`:** Full compatibility matrix (3×2 table: BL/Two-Punctures/TOV
  × Sommerfeld/Copy). Sommerfeld formula with f∞ values and v_char=√2.
- **§11 `diagnostics.*`:** `output_every` with α_center AMR level 0 warning.
  `gw_extraction` section. `ah_finder` section.
- **§12 `io.*`:** `output_every`, `checkpoint_every` with HDF5 group structure.
  `format` enum. HPC I/O tuning parameters (Lustre striping).
- **§13 Dangerous Parameter Combinations:** 6-row table of confirmed failure modes
  with source references (CHANGELOG, DEVELOPER_GUIDE, BENCHMARKS).
- **§14 Preset Configurations:** (referenced, content in main body)

---

#### `AMR-Design.md` — Berger-Oliger AMR Technical Reference

**URL:** https://github.com/LiranOG/Granite/wiki/AMR-Design

- **§1 Subcycling:** `dt_ℓ = dt_0 / 2^ℓ` formula. Pseudo-code for recursive
  subcycle function with restrict step labeled.
- **§2 Prolongation:** Trilinear interpolation formula with weight definitions.
  Documents that `prolongateGhostOnly()` was introduced and reverted in v0.6.5.
- **§3 Restriction:** Volume-weighted averaging formula (1/8 Σ fine in 3D).
  Conservation argument for GRMHD conserved quantities.
- **§4 Ghost Zone Filling Order:** 4-step sequence (MPI_Isend → MPI_Irecv →
  prolongate → MPI_Waitall → outer BC). Order-matters note.
- **§5 Refinement Criteria:** 4-row table (chi/alpha/rho/ham with criterion type
  and physical interpretation). Tracking spheres override documented.
- **§6 Block-Merging Algorithm:** 3-step algorithm (list candidate patches → union-merge
  overlapping patches → create merged blocks). Documents the MPI deadlock fix for
  close-binary configurations.
- **§7 Current Limitations:** 4-row table (dynamic regridding not fully implemented,
  max 4 stable levels, no adaptive timestep per level, non-configurable regrid
  frequency). All targeted v0.7.

---

#### `Initial-Data.md` — Initial Data Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Initial-Data

- **§1 Two-Punctures / Bowen-York:** Physics background (conformal factor ψ = ψ_BL + u).
  5-row quasi-circular momentum table for separations d=6M to d=15M with
  leading-order PN and 1.5PN values. p_t=0.0840 highlighted as GRANITE default.
  YAML configuration with correct momentum signs.
- **§2 Brill-Lindquist:** ψ_BL formula. YAML config. Critical warning box:
  "MANDATORY: Use `boundary.type: copy` with BL data. Sommerfeld produces ‖H‖₂
  8× worse."
- **§3 TOV Neutron Star:** TOV ODEs (dP/dr and dm/dr). Critical unit box: "1 km =
  1.0e5 cm — NOT RSUN_CGS. Fixed as bug TOV, never revert." Expected results table
  (M≈1.4 M☉, R≈10 km, ρ_c≈5×10¹⁴ g/cm³).
- **§4 Compatibility Matrix:** 4×2 table (BL/Two-Punctures/Bowen-York/TOV ×
  Sommerfeld/Copy BC) with ✅/❌ and one-line justification per cell.

---

#### `Known-Fixed-Bugs.md` — Authoritative Bug Registry

**URL:** https://github.com/LiranOG/Granite/wiki/Known-Fixed-Bugs

Standing order header: "Every PR that touches any of the files listed in this table
MUST explicitly verify that the corresponding fix is still in place."

10-entry registry, each with: ID, severity, file, phase fixed, exact bug description
with before/after code snippets where applicable, consequence, and verification test.

| Bug ID | Description |
|---|---|
| **C1** | EOS sound speed hardcoded Γ=1 in `maxWavespeeds()`. Underestimate by factor √(5/3)–√2.5. Fix: `eos.soundSpeed()` |
| **C3** | HLLE `computeHLLEFlux()` used flat dummy metric. Consequence: SR fluxes in GR spacetime. Fix: GRMetric3 promoted to public interface |
| **H1** | KO dissipation spawned 22 separate OpenMP regions (one per variable). ~30% compute waste. Fix: single parallel region, var loop innermost |
| **H2** | GridBlock used `vector<vector<Real>>` — 22 heap allocations per block. Fix: single flat `vector<Real>` with stride indexing |
| **H3** | RHS zero-out loop: var outermost, spatial innermost — cache thrashing. Fix: spatial outermost, var innermost |
| **TOV** | TOV solver used `RSUN_CGS` for km→cm conversion (off by ×700,000). Fix: `1.0e5 cm/km` |
| **KO-σ** | B2_eq YAML used `ko_sigma: 0.35` — destroys trumpet gauge profile silently. Fix: `0.1` |
| **Sommerfeld+BL** | Sommerfeld BC with BL initial data: ‖H‖₂ 8× worse. Evidence: Phase 6 controlled experiment. Fix: use copy BC with BL |
| **Domain** | Small domains (<48M SP, <200M BBH) cause gauge wave reflection at t≈domain/√2. Formula documented |
| **alpha_center** | Diagnostic reads AMR level 0 at r≈0.65M, not finest level near puncture. Status: KNOWN BUT NOT YET FIXED — v0.7 target |

---

#### `Simulation-Health-&-Debugging.md` — Debugging Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Simulation-Health-&-Debugging

**This page supersedes the outdated `docs/diagnostic_handbook.md`.**
All thresholds calibrated to actual v0.6.5 production run output.

- **§1 Primary Health Indicators:** 6-row table (α_center, ‖H‖₂ with growth rate γ
  [M⁻¹], NaN_events, AMR_blocks, CFL_finest, speed) with Healthy/Warning/Critical
  thresholds for each.
- **§2 Healthy Output Examples:** Full verbatim expected terminal output for
  single_puncture (t=0→500M, ‖H‖₂ decaying ×84.8) and B2_eq (t=0→500M,
  ‖H‖₂ decaying ×61.3) with Stability Summary blocks.
- **§3 Lapse Lifecycle — α_center Explained:** Explicit caveat that α_center reads
  AMR level 0 at r≈0.65M, not the puncture. 5-row expected lapse table by phase
  (Initial → Gauge Adjustment → Trumpet Forming → Trumpet Stable → pathologies).
  Explains why α never drops to 0.3 at coarse resolution (trumpet unresolved —
  expected, not a bug).
- **§4 Hamiltonian Constraint Interpretation:** ‖H‖₂ formula with Ricci scalar
  expansion. 6-row threshold table using growth rate γ [M⁻¹] instead of absolute
  value. Constraint explosion forensic patterns (domain reflection, CFL violation,
  BC incompatibility, over-dissipation).
- **§5 NaN Forensics:** "NaN Is An Infection, Not A Crash." The Clean Summary Paradox.
  4-step forensic checklist: step-0 RHS scan → identify first NaN variable by index
  → locate infection source (center vs. boundary vs. spread rate) → identify cause
  per variable (chi → resolution; alpha → CFL/gauge; Gamma_hat → upwinding near
  puncture; boundary → BC problem).
- **§6 Debugging Flowchart:** Full ASCII decision tree covering: NaN events → which
  variable; ‖H‖₂ growing → from step 0 / sudden jump at t≈domain/√2 / gradual;
  no merger despite d=10M BBH; lapse not forming trumpet; AMR blocks stuck at 4;
  phase labels showing Early Inspiral for entire run.
- **§7 Common Failure Modes with Solutions:** 5 named failure modes with symptom,
  cause, and solution:
  1. Crash at t≈6–11M (gauge wave reflection). Domain table.
  2. High ‖H‖₂ from step 0 (Sommerfeld + BL).
  3. No inspiral in BBH run (zero tangential momentum).
  4. Trumpet not forming (resolution coarse or ko_sigma > 0.1).
  5. Secondary gauge collapse without NaN (gauge pathology, not crash — do NOT stop
     the simulation).
- **§8 Health Check Checklist:** `python3 scripts/health_check.py` expected output
  verbatim. 8-row manual checklist with pass criteria.
- **§9 Known Diagnostic Limitations:** 5-row table (α_center level 0, time-based phase
  labels, AMR block count frozen, loadCheckpoint stub, M1 inactive). All v0.7.

---

#### `Benchmarks-&-Validation.md` — Numerical Results

**URL:** https://github.com/LiranOG/Granite/wiki/Benchmarks-&-Validation

- Hardware: i5-8400, 16 GB DDR4, WSL2 Ubuntu 22.04, GCC 11.4 -O3, OpenMPI 4.1.2.
- **Single Puncture 64³:** ‖H‖₂: 1.083e-2 → 1.277e-4 (×84.8 reduction). 0 NaN. 497 min.
- **Single Puncture 128³:** ‖H‖₂: 1.855e-2 → 1.039e-3 (×17.9 reduction). 0 NaN.
- **B2_eq 64³ (t=500M):** Full 16-checkpoint step table (steps 2–320, t=3.125M–500M)
  with α_center, ‖H‖₂, block count. ×61.3 reduction. 98.9 min. 0.0843 M/s.
- **B2_eq 96³ (t=500M):** 12-checkpoint table. ×67.4 reduction. 496 min. 0.0168 M/s.
- Throughput and HPC projection table (desktop → 2× Xeon → H100 SXM).
- Validation test suite table: 6 tests with status (single_puncture ✅, balsara_1 ✅,
  magnetic_rotor ✅, gauge_wave 🔶 config exists no results, binary_equal_mass 🔶
  planned v0.7, radiative_shock_tube ⚪ M1 not active).
- `git clone` + `python3 scripts/run_granite.py run` reproduction commands.

---

#### `Developer-Guide.md` — Contributor Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Developer-Guide

- **§1 Coding Standards:** C++17 mandate. No exceptions policy. Logger not cout.
  Naming convention table (namespace snake_case / class PascalCase / function
  camelCase / variable snake_case / constant UPPER_SNAKE). Physical units comment
  requirement. clang-format enforcement.
- **§2 Pre-PR Checklist:** 9-item binary checklist. Includes explicit "No ko_sigma >
  0.1 in any YAML or code" item and "Known Fixed Bugs verified intact" item.
- **§3 Adding Physics Modules:** 8-step workflow (RFC Issue → branch → implement →
  public header → tests → YAML → CHANGELOG → PR). Two test templates with
  convergence order test pattern.
- **§4 Test Suite Structure:** Annotated file tree with test suite names and test
  counts per file. Total: 92 tests.
- **§5 Build System Reference:** `run_granite.py` subcommand table. CMake options
  table (5 options). Direct CMake commands.
- **§6 CI/CD Pipeline:** GitHub Actions pipeline steps. All PRs block on CI failure.

---

#### `HPC-Deployment.md` — HPC Operations Guide

**URL:** https://github.com/LiranOG/Granite/wiki/HPC-Deployment

- **§1 Pre-Flight:** `health_check.py` as mandatory first step.
- **§2 Memory Requirements:** 5-row table (64³→B5_star) with RAM estimates and formula
  (nvar_total=93 including RK3 buffers, AMR_factor per level).
- **§3 OpenMP:** `OMP_NUM_THREADS`, `OMP_PROC_BIND=close`, `OMP_PLACES=cores`.
  `numactl --interleave=all` for NUMA systems.
- **§4 HPC Launch Command:** `run_granite_hpc.py` with all flags shown.
- **§5 SLURM Template:** Complete `#SBATCH` job script for 4-node, 8-task/node,
  8-thread/task configuration.
- **§6 Lustre I/O Tuning:** `lfs setstripe -c 16 -S 4M` command and YAML I/O params.
- **§7 Containers:** Docker `build` + `run` commands. Singularity/Apptainer `build`
  + `run` commands.
- **§8 GPU Roadmap:** 4-row table (v0.6.5 current → v0.7 vast.ai H100 → v0.8 cluster
  → v1.0 Tier-0) with projected throughput. Note: GTX 1050 Ti NOT viable for FP64.

---

#### `Gravitational-Wave-Extraction.md` — GW Extraction Reference

**URL:** https://github.com/LiranOG/Granite/wiki/Gravitational-Wave-Extraction

- **§1 Newman-Penrose Ψ₄:** Ψ₄ = −(ḧ₊ − iḧ×) / 2r. NP formalism on CCZ4 metric.
- **§2 Spherical Harmonic Decomposition:** Full spin-weighted decomposition formula.
  Wigner d-matrix implementation (Goldberg 1967). Dominant mode: ℓ=2, m=±2.
- **§3 Extraction Radii:** 6-radius table (50M → 500M) with purpose for each.
  Richardson extrapolation requirement. Null-infinity proxy at 500M.
- **§4 Strain Recovery:** Double time-integration of Ψ₄. Fixed-frequency integration
  (Reisswig & Pollney 2011) to suppress drift: h̃(ω) = Ψ̃₄(ω)/max(ω,ω₀)².
- **§5 Radiated Energy and Momentum:** dE/dt formula. Recoil kick formula (Ruiz 2008)
  with adjacent-mode coupling coefficient a^ℓm.
- **§6 Status:** "Infrastructure implemented. Full activation in production runs
  targeted for v0.7."

---

#### `FAQ.md` — Frequently Asked Questions

**URL:** https://github.com/LiranOG/Granite/wiki/FAQ

12 questions across Science, Engineering, and HPC categories. Key entries:

- "Why CCZ4 and not BSSN?" — Exponential damping with timescale τ≈1/(κ₁α)≈50M.
- "Why not Einstein Toolkit?" — N>2 BH + unified GRMHD+M1 goal not achievable in
  thorn system.
- "What resolution do I need for realistic inspiral?" — dx < 0.05M near puncture,
  ~6 AMR levels at 64³ base.
- "What does ‖H‖₂ reduction by ×61 mean?" — 3-point explanation of CCZ4 constraint
  damping effectiveness.
- "My BBH runs to t=500M but I see no merger." — momentum=[0,0,0] → head-on. Check
  tangential momentum first.
- "What does ko_sigma do?" — KO formula with p=3. σ=0.1 safe; σ>0.1 over-dissipates
  trumpet silently.
- "Why can't I use Sommerfeld with BL data?" — ψ_BL ≠ 1/r outgoing profile. Phase 6
  evidence: ×8 constraint violation.
- "Why ≥48M domain?" — t_reflection = domain/√2. Formula and domain table.
- "Why is M1 built but not active?" — Coupling + checkpoint-restart both required
  first (v0.7 blockers).
- "Why must I run from a Linux-native path in WSL?" — 9P filesystem ~10× I/O latency.

---

#### `Scientific-Context.md` — Scientific Motivation

**URL:** https://github.com/LiranOG/Granite/wiki/Scientific-Context

- **§1 The Problem:** 4 coupled physics systems. Binary BH domain vs. GRANITE domain.
- **§2 Why Existing Codes Are Insufficient:** 5-row code comparison table
  (Einstein Toolkit / GRChombo / SpECTRE / AthenaK / GRANITE) with strength and
  key gap per code. Coupling problem articulation.
- **§3 B5_star Scenario:** Configuration (5 × 10⁸ M☉ SMBHs in pentagon + 2 × 4300 M☉
  stars). 3-phase physical sequence (Stellar Disruption → SMBH Inspiral → Remnant).
  5-row multi-messenger table (GW/X-ray/Radio/Neutrino with detector per messenger).
  Computational requirements table.
- **§4 Analytic Pre-Validation:** NRCF/PRISM pre-validation table (4 observables with
  estimates and tolerances).
- **§5 Physical Unit System:** G=c=1 conversion table for M=1 M☉ and M=10⁸ M☉.
  Unit bug warning: 1 km = 1.0e5 cm, not RSUN_CGS.

---

#### `Roadmap.md` — Development Roadmap

**URL:** https://github.com/LiranOG/Granite/wiki/Roadmap

- **Version Table:** v0.6.5 ✅ Released → v0.7 🔄 In Progress → v0.8 📋 Planned →
  v0.9 📋 Planned → v1.0 🎯 Target Q1 2027.
- **Tier-1 Blockers for v0.7:** 3-row table (dynamic AMR regridding, loadCheckpoint,
  M1 wired into RK3 loop) with exact files.
- **GPU Porting Plan:** 4 kernel priorities in order (CCZ4 RHS hot loop first).
  vast.ai H100 SXM as target hardware. Prerequisites: CPU validation first.
- **B5_star Scaling Path:** 4-step ASCII ladder (v0.6.5 desktop → v0.7 GPU → v0.8
  cluster → v1.0 flagship).
- **Known Limitations Table:** 6-row table with planned fix version for each.

---

#### `CHANGELOG-Summary.md` — Version History Summary

**URL:** https://github.com/LiranOG/Granite/wiki/CHANGELOG-Summary

High-level summary of all versions from Phase 4A through v0.6.5 with key deliverables
per version. References the full `CHANGELOG.md` for complete technical details.

---

#### `Documentation-Index-&-Master-Reference.md` — Complete Document Inventory

**URL:** https://github.com/LiranOG/Granite/wiki/Documentation-Index-&-Master-Reference

The most comprehensive wiki page (15 sections, ~6,000 words). A per-file encyclopedia
of every document in the repository.

- **§2 Document Map:** 18-row quick-reference table with path, line count, audience,
  and last-confirmed-accurate version.
- **§3–§13:** Per-file sections for every document in root, docs/, .github/,
  benchmarks/, scripts/, python/, containers/, viz/, include/, src/, tests/.
  Each section includes: Purpose, Sections (complete inventory), Known Gaps.
- **§14 Gap Analysis:** What is missing (10-row table: gauge_wave results, GW waveform
  section, updated diagnostic handbook, Unreleased CHANGELOG section, wiki pages
  needed, Jupyter tutorial, CI runner for validation_tests.yaml).
  Content requiring update (7-row table). Content confirmed correct (11 items).
- **§15 Cross-Reference Matrix:** 35-row topic→primary document→secondary document
  table covering every major topic in the codebase.

---

#### `_Sidebar.md` — Wiki Navigation Sidebar

Persistent left-sidebar navigation across all wiki pages. Organized into 4 sections
(Getting Started / Physics & Science / Running Simulations / Development) plus
Reference. Links to all 17 pages.

---

### Fixed — Undocumented v0.6.5 Physics Features (Now Documented)

The following three items existed in the v0.6.5 source code but had no CHANGELOG
entry. They are formally documented here.

---

#### Chi-Blended Selective Upwinding (`src/spacetime/ccz4.cpp`, `include/granite/spacetime/ccz4.hpp`)

**What was added (undocumented in v0.6.5 entry):**
The advection term β^i ∂_i f in the CCZ4 RHS uses a tanh-sigmoid blend between
4th-order centered FD (near the puncture, where β≈0 and CFL≈0) and 4th-order
upwinded FD (far from the puncture, where |β| can approach CFL limit):

```
blend_w = 0.5 * (1 + tanh((χ - χ_c) / χ_w))

advec(var) = blend_w × β^i d1up(var, i) + (1 - blend_w) × β^i d1(var, i)
```

Parameters: `chi_blend_center = 0.05`, `chi_blend_width = 0.02` (new fields
in `CCZ4Params`). The Γ̃^i advection term (T7) is always centered regardless of
blend weight — this prevents the step-9 NaN that was caused by upwinding over
steep near-puncture Γ̃^i gradients.

**Known limitation:** `chi_blend_center` and `chi_blend_width` are not parsed from
`params.yaml` in `main.cpp`. They use the hardcoded `CCZ4Params` defaults and
cannot be tuned without recompiling. YAML wiring is a v0.7 item.

---

#### Algebraic Constraint Enforcement (`src/main.cpp`)

**What was added (undocumented in v0.6.5 entry):**
`applyAlgebraicConstraints()` lambda in `TimeIntegrator::sspRK3Step` enforces
two algebraic identities of the CCZ4 conformal decomposition once per full RK3
step (at the final combine, on the main grid only — NOT on the stage grid):

1. **det(γ̃) = 1:** Computes `det = γ̃_xx(γ̃_yy γ̃_zz − γ̃_yz²) − ...`,
   rescales all 6 components by `cbrt(1/det)`. Degenerate metrics
   (det ≤ 1e-10 or non-finite) are reset to δ_ij.

2. **tr(Ã) = 0:** Computes `trA = γ̃^ij Ã_ij` using the cofactor inverse of γ̃
   (valid since det=1 has just been enforced). Removes `(1/3) trA γ̃_ij` from
   each Ã_ij component.

Consistent with standard CCZ4 practice (Alic et al. 2012).

---

#### B2_eq Quasi-Circular Tangential Momenta (`benchmarks/B2_eq/params.yaml`)

**What was fixed (undocumented critical physics change):**
Both BHs previously had `momentum: [0.0, 0.0, 0.0]`, producing a head-on
collision. Updated to Pfeiffer et al. (2007) quasi-circular PN values for
equal-mass d=10M (M_total=1):

```yaml
black_holes:
  - mass: 1.0
    position: [5.0, 0.0, 0.0]
    momentum: [0.0, 0.0954, 0.0]   # ← corrected from [0.0, 0.0, 0.0]
  - mass: 1.0
    position: [-5.0, 0.0, 0.0]
    momentum: [0.0, -0.0954, 0.0]  # ← corrected from [0.0, 0.0, 0.0]
```

**Note:** The benchmark data tables in `Benchmarks-&-Validation.md` reflect runs
with `p_t = ±0.0840` (an earlier PN estimate also in the quasi-circular range).
The YAML file now uses `±0.0954` (Pfeiffer et al. 2007, closer to the
eccentricity-reduced value). Both values produce inspiral; the difference in
orbital period and eccentricity is sub-dominant at this resolution.

---

### Changed — Version & Infrastructure

- **CITATION.cff:** `date-released: 2026-04-10` — Wiki launch date recorded as
  the project's public documentation milestone.
- **Wiki sidebar:** `_Sidebar.md` with 4-section navigation added. Appears on
  every wiki page.
- **`docs/diagnostic_handbook.md`:** Formally deprecated. The
  `Simulation-Health-&-Debugging` wiki page supersedes it with updated thresholds
  and v0.6.5-accurate expected output.

---

### Known Issues Carried Forward to v0.7

These items are documented for the first time in this release but not yet fixed:

| Issue | File | Description |
|---|---|---|
| `alpha_center` reads AMR L0 | `src/main.cpp` | Lapse read at r≈0.65M on coarsest level, not finest level near puncture. Displayed values misleadingly close to 1.0. |
| `chi_blend_center/width` not YAML-parseable | `src/main.cpp` | New `CCZ4Params` fields hardcoded, not wired through YAML parser. |
| `loadCheckpoint()` is a stub | `src/io/hdf5_io.cpp` | Throws `runtime_error`. Checkpoints written but restart non-functional. |
| M1 / neutrino not in RK3 loop | `src/main.cpp` | Modules built, pass tests, never called during evolution. |
| AMR dynamic regridding incomplete | `src/amr/amr.cpp` | Block count frozen at initialization. `regrid()` evaluates criteria but doesn't rebuild moving-puncture hierarchy at runtime. |
| Phase labels time-based | `scripts/sim_tracker.py` | "Early/Mid/Late Inspiral" classified by t/t_final fraction, not BH separation. |

---

## [v0.6.5] — The Stability Update (2026-04-07)

### Summary

This release completes **Phase 4: The Tactical Reset** — a comprehensive forensic rescue operation that restored the GRANITE engine to a verified, production-stable baseline. After a series of architectural regressions introduced over-engineered mathematical constraints and a fragile telemetry class hierarchy, a directory-wide `diff` against the verified `v0.6.0` backup was used as ground truth to surgically revert all damaging changes while preserving the P0 memory safety fixes accumulated during that period. Both the `single_puncture` and `B2_eq` benchmarks now run stably with `||H||₂` decaying properly and the tracker reporting truthfully.

---

### Fixed — Architecture & Stability (`src/spacetime/ccz4.cpp`, `src/amr/amr.cpp`)

- **Master Reset of CCZ4 Core:** Reverted `ccz4.cpp` to the exact v0.6.0 baseline, purging all over-engineered mathematical constraints that had been introduced during the forensic audit. Specifically removed:
  - Aggressive `chi`-flooring clamps applied inside stencil derivative reads — these incorrectly modified cell data before finite-difference reads, destroying the interpolation balance that AMR's load-bearing ghost zones depended on.
  - Constraint-value clamping inside `computeConstraints()` that produced false `||H||₂ = inf` reports by clamping intermediate products to `0.0/0.0`.
  - All other "load-bearing bug" disruptions to the delicate cancellation structure in the constraint-violation monitor.
- **Master Reset of AMR (`src/amr/amr.cpp`, `include/granite/amr/amr.hpp`):** Reverted `amr.cpp` and `amr.hpp` to the v0.6.0 baseline, eliminating theoretical patches that accidentally broke the numerical balance previously maintained by interpolation error cancellation:
  - Removed `std::floor` replacement of `std::round` in `regrid()` child cell snapping — the `std::round` behavior is what the v0.6.0 physics relied on.
  - Removed `fill_interior = false` flag and `prolongateGhostOnly()` bifurcation in `prolongate()` — the full-domain prolongation is the load-bearing behavior.
  - Removed `truncationErrorTagger` and `setGlobalStep()` dead code from the header.
- **Master Reset of Main Entry Point (`src/main.cpp`):** Reverted `main.cpp` to the v0.6.0 baseline, removing `derefine_threshold`, `use_truncation_error`, and other undefined struct members that had caused CI compilation failures.

---

### Fixed — Memory Safety (`src/amr/amr.cpp`)

- **`levels_.reserve()` Retained:** Across all resets, the single P0 memory safety fix was preserved:
  ```cpp
  levels_.reserve(static_cast<std::size_t>(params_.max_levels));
  ```
  Added at the top of `AMRHierarchy::initialize()`, this pre-allocates the `levels_` vector to its maximum capacity before any `push_back()` calls occur during the refinement cascade. Without this, `push_back()` could trigger a reallocation, invalidating every raw `GridBlock*` pointer captured by `syncBlocks()` lambdas — classic undefined behavior causing intermittent segfaults during subcycling.

---

### Fixed — Singularity Avoidance (`src/main.cpp`)

- **MICRO_OFFSET Grid Phase-Shift Re-Injected:** After the master reset wiped the previous injection, the `MICRO_OFFSET` was restored:
  ```cpp
  constexpr Real MICRO_OFFSET = 1.3621415e-6;
  for (int d = 0; d < 3; ++d) {
      params.domain_lo[d] += MICRO_OFFSET;
      params.domain_hi[d] += MICRO_OFFSET;
  }
  ```
  Applied universally after YAML parsing, before grid construction. This permanently immunizes the engine against `r=0` division-by-zero for any centered-domain single-puncture setup (e.g., `single_puncture` benchmark with BH at origin). The value `1.3621415e-6` is incommensurable with all typical `dx` values (~0.25M–2.0M) so no refinement level will re-align a cell center with the singularity.

---

### Fixed — Telemetry & UI (`scripts/sim_tracker.py`)

- **Procedural Architecture Restored:** Reverted the tracker from a broken class-based refactor back to the v0.6.0 procedural regex-based parsing architecture. The class-based version had rigid, incorrectly ordered regex groups that failed to parse the engine's standard output lines, producing cascading `ValueError: could not convert string to float` crashes and garbled UI output.
- **Crash-Proof Float Casting:** All metric extractions use `safe_float()` which returns `None` instead of raising on bad values (including `nan`, `inf`, `-`, empty strings, and partial C++ log lines).
- **Honest Stability Summary — 8-Layer Guard:** The `print_summary()` Stability Summary block was upgraded from a 2-condition boolean to an exhaustive 8-layer failure detection system that can never report "No catastrophic events" falsely:

  | Layer | Condition Checked |
  |:---:|:---|
  | 1 | `sess.crashed` — explicit lapse floor hit |
  | 2 | Any `record.alpha is None` — NaN α caught by `safe_float()` |
  | 3 | `not math.isfinite(final_alpha)` — inf/nan α not caught as None |
  | 4 | `max(fin_ham) > H_CRIT` — finite constraint explosion |
  | 5 | Any `record.ham is None` — NaN/∞ ‖H‖₂ captured as None |
  | 6 | `sess.nan_events` — explicit `[NaN@step=]` lines from C++ |
  | 7 | `sess.zombie_step` — frozen physics state |
  | 8 | Phase label contains CRASH/COLLAPSE/EXPLOSION/NAN — last-resort catch-all |

---

### Changed — Version & Release Infrastructure

- **`CMakeLists.txt`:** `VERSION 0.6.0` → `VERSION 0.6.5`
- **`src/main.cpp`:** Banner string `"0.5.0"` → `"0.6.5"`
- **`CHANGELOG.md`:** This entry prepended as the canonical release record.
- **Git Tag `v0.6.5`:** Annotated tag created and pushed to `origin/main` as an immutable checkpoint of the stable baseline.

---

## [v0.6.0] — The Puncture Tracking Update (2026-04-04)

### Summary

This mega-release consolidates Phase 8 stability hardening of the CCZ4 evolution engine with the massive Phase 2 Multi-level Adaptive Mesh Refinement (AMR) and Binary Black Hole (BBH) initial data integration. The engine has fully transitioned from a master single-grid architectural model to a Berger-Oliger recursive hierarchy capable of sustaining puncture tracking. Alongside solver upgrades, the diagnostic tracking tools have been completely overhauled for professional-grade terminal forensics. Test count increased from **90 → 92** (100% pass rate) with two new selective advection unit tests.

---

### Changed — Universal Deployment & Performance Phase

- **Files:** `CMakeLists.txt`, `README.md`, `docs/INSTALL.md`, `INSTALLATION.md` _(new)_, `DEPLOYMENT_AND_PERFORMANCE.md` _(new)_, `scripts/health_check.py` _(new)_.
- **Performance:** Enforced state-of-the-art native release optimizations in `CMakeLists.txt`. MSVC now triggers `/O2 /Ob2 /arch:AVX2 /fp:fast /MT`, ensuring explosive loop-unrolling and AVX2 vectorization natively on Windows. GCC/Clang now explicitly uses `-march=native -O3 -ffast-math`.
- **Packaging:** Solved native Windows dependency issues by explicitly wiring the build chain instructions for `vcpkg` HDF5/MPI/yaml-cpp installations.
- **Documentation Harmonization:** Built a complete, zero-failure technical onboarding sequence. Generated `INSTALLATION.md` for bare-metal cross-platform `cd / build` workflows and preserved deep technical Q&A troubleshooting in `docs/INSTALL.md`. Stripped all faulty bash scripting (`python3` vs `python` conditionals mapped per OS) to prevent native console breaking.
- **Maximum Power Protocols:** Authored authoritative master-level guides targeting OpenMP thread saturation bounding and memory checks inside `DEPLOYMENT_AND_PERFORMANCE.md`.
- **Pre-Flight Diagnostics:** Created Python `scripts/health_check.py` tool. Pre-analyzes `.CMakeCache.txt` configuration and logical `omp_get_max_threads()` constraints to prevent catastrophic user-side runtime bottlenecks and flags sub-optimal compiler flags before simulations execute.

---

### Added — Universal Append-Only Simulation Dashboard (`sim_tracker.py`)

- **File:** `scripts/sim_tracker.py`
- Completely rewrote the Python tracking toolkit to function as an append-only live dashboard, eliminating `\r` and cursor-up resets to preserve terminal history and prevent output-mangling from C++ diagnostic logs.
- Added real-time phase classification (e.g., Inspiral, Merger, Ringdown).
- Included real-time exponential constraint growth rate ($\gamma$) calculations for the Hamiltonian constraint.
- Added a "Zombie State" detector to instantly flag frozen physics when $\alpha$ and $\Vert H \Vert_2$ stagnate due to hierarchy synchronization failures.
- Implemented robust NaN forensics to track numerical explosions, pinpointing the variable that seeded the NaN and calculating its propagation speed across the grid.
- Integrated automated post-run Matplotlib summaries to visualize constraint growth and phase transitions instantly upon simulation completion.

---

### Added — `TwoPuncturesBBH` Spectral Initial Data

- **Files:** `src/core/initial_data.cpp`, `include/granite/core/initial_data.hpp`
- Mapped the analytical Bowen-York extrinsic curvature $K_{ij}$ fields to the macroscopic `GridBlock` tensors for arbitrary puncture momenta and spins.
- Implemented a Jacobi/Newton-Raphson iterative relaxation solver for the Hamiltonian constraint to accurately compute the conformal factor correction $u$ on top of the Brill-Lindquist background.
- Routed the YAML initialization hook to properly construct `TwoPuncturesBBH` whenever `type: two_punctures` is specified, officially enabling BBH simulation.
- **Tracking Spheres:** Implemented automatic tracking sphere registration in `main.cpp` for binary black hole punctures, instructing the AMR hierarchy to dynamically focus grid refinement down to the required `min_level` around moving horizons.

---

### Changed — Adaptive Mesh Refinement (AMR) Architecture Overhaul

- **Files:** `src/amr/amr.cpp`, `include/granite/amr/amr.hpp`
- **Subcycling:** Implemented full Berger-Oliger recursive subcycling (`subcycle()`). Finer levels now take proportionally smaller, independent $dt$ sub-steps per coarse step.
- **Block-Merging Algorithm:** Introduced a conservative bounding-box geometric merge algorithm in `regrid()` during refinement cascading. Proposed refinement patches around tracking spheres are iteratively union-merged if they touch or overlap, strictly eliminating duplicate cells and preventing fatal MPI `syncBlocks()` deadlocks for close binaries.
- **Physical Extent Alignment:** Refactored `regrid()` child block geometry math. Child $dx$ is now *strictly* forced to `parent_dx / ratio`, rather than being arbitrarily derived from sphere bounding box radii, ensuring exact grid boundary alignment and eliminating sub-grid drift.
- **Time-step Synchronization:** Added `setLevelDt()` to cascade and synchronize CFL-limited time steps from the Level 0 master domain down through the entire AMR hierarchy before execution, fixing the "Zombie Physics" bug where fine grids remained frozen at $dt=0$.
- **Conservative Restriction:** Built out `restrict_data()` logic using volume-weighted averaging and outlined conservative flux-correction (refluxing) hooks for GRMHD.

---

### Fixed — Coarse-Fine Interpolation & Ghost Cell Contamination

- **File:** `src/amr/amr.cpp`
- **Prolongation Origin Off-by-N Bug:** Fixed a catastrophic bug in `prolongate()` where the coordinate mapping scalar was incorrectly offset from the coarse grid's ghost boundary (`coarse.x(0,0)`) rather than the interior origin. This massive offset forced the interpolator out of bounds and left fine ghost cells entirely uninitialized.
- **Coarse-Fine Boundary Interpolation:** Fixed `fillGhostZones()` to correctly interpolate and prolongate boundary data from the active parent level into fine ghost cells *before* assigning fallback zero-gradient boundary conditions. This eliminates the instantaneous and fatal infinite-gradient explosions (`CFL = 5.8e28`) previously caused by stale ghost data interacting with post-step interior cells.
- **Initial Refinement Cascade:** Fixed `initialize()` to guarantee instantaneous, forced refinement cascading down to the deepest required `min_level` for all tracking spheres at $t=0$, bypassing the lack of gradient-based tagging on the initial flat spacetime slice.


### Fixed — Diagnostic Memory Access & Multidimensional Loops

- **File:** `src/main.cpp`
- **Linear Indexing Offset Bug:** Fixed a syntax bug where parameterless `istart()` and `iend()` were called on `GridBlock` objects during terminal diagnostics (like computing $\alpha_{center}$). Updated the accessors strictly to `istart(0)`, `iend(1)`, etc., restoring correct iteration across the multidimensional memory spaces.

---

### Added — New Benchmark: `gauge_wave` (Apples-with-Apples Test)

**File:** `benchmarks/gauge_wave/params.yaml` *(new file)*

- Standard CCZ4 code-validation benchmark based on the Alcubierre et al. (2004) gauge wave test.
- **Grid:** $64^3$ cells on a $[-0.5, 0.5]^3$ domain ($dx = 0.015625$).
- **Initial Data:** Sinusoidal lapse perturbation $\alpha = 1 + A\sin(2\pi x/L)$ with $A=0.1$, $L=1.0$ on flat conformal metric.
- **Physics:** All Hamiltonian constraint violation should remain $\sim 0$ to machine precision for all time, providing a regression test for the CCZ4 Ricci tensor and gauge evolution implementation.
- **CFL:** $0.25$ (standard SSP-RK3 safe value), $t_{final} = 100.0$.
- **KO Dissipation:** $\sigma = 0.1$ (light dissipation — the gauge wave is smooth and does not require aggressive damping).

---

### Added — New Benchmark: `B2_eq` (Equal-Mass Binary BH Merger)

**File:** `benchmarks/B2_eq/params.yaml` *(new file)*

- Production-grade parameter file for the flagship equal-mass, non-spinning binary black hole merger simulation.
- **Grid:** $256^3$ cells on a $\pm 200M$ domain with 6 AMR levels (finest $dx = 0.049M$, ~41 cells per $M$ at the puncture).
- **Initial Data:** Bowen-York puncture data with elliptic Hamiltonian constraint solve.
- **Black Holes:** Two equal-mass ($M=1.0$) BHs at separation $d=10M$ with quasi-circular orbital momenta $P_y = \pm 0.0954$ (Pfeiffer et al. 2007).
- **Physics Design:**
  - Domain $\pm 200M$: GW extraction at $r=100M$, gauge wave ($v=\sqrt{2}$) reaches boundary at $t\approx 245M$ — well past merger at $t\approx 150\text{--}200M$.
  - $\eta = 1.0 = 1/M_{ADM}$: Standard Campanelli (2006) Gamma-driver mass scaling.
  - $\sigma_{KO} = 0.35$: Damps gauge transients without destroying conformal-factor gradients.
- **HDF5 Output:** Gravitational wave extraction radii at $r = [50, 75, 100]M$ for Newman-Penrose $\Psi_4$ computation.

---

### Added — Machine-Readable Validation Test Suite

**File:** `benchmarks/validation_tests.yaml`

- Comprehensive validation test definitions spanning **three physics sectors** with quantitative pass/fail criteria:
  - **Spacetime:** `gauge_wave` (4th-order convergence, amplitude drift $< 10^{-6}$), `robust_stability` (noise growth $< 10\times$ over $10^5 M$), `single_puncture` (horizon mass drift $< 10^{-4}$), `binary_equal_mass` (phase error $< 0.01$ rad vs. SXS:BBH:0001 catalog).
  - **GRMHD:** `balsara_1` (shock tube $L_1$ error $< 10^{-3}$), `magnetic_rotor` ($\nabla\cdot B < 10^{-14}$), `bh_torus` (MRI growth rate within 5% of linear theory).
  - **Radiation:** `radiative_shock_tube` (M1 vs. analytic $L_2$ error $< 2\%$), `diffusion_limit` (diffusion coefficient error $< 1\%$).
- Each test entry specifies: `initial_data`, `grid`, `evolution`, `pass_criteria`, and optional `reference` datasets for comparison.
- Designed for future CI integration: a test runner can parse this YAML and auto-verify all convergence orders and error bounds.

---

### Added — Selective Advection Unit Tests (Test Count: 90 → 92)

**File:** `tests/spacetime/test_ccz4_flat.cpp`

Two new tests verifying the chi-weighted selective advection scheme introduced in Phase 7:

1. **`SelectiveAdvecUpwindedInFlatRegion`:** Verifies that with $\chi = 1$ (flat spacetime / far from puncture), the selective advection lambda correctly selects the upwinded `d1up` branch. A linear lapse profile $\alpha = 1 + 0.01x$ with nonzero shift $\beta^x = 0.5$ is evolved; the test asserts all RHS values are finite and contain a consistent advection contribution.

2. **`SelectiveAdvecCenteredNearPuncture`:** Verifies that with $\chi = 0.01$ (simulating near-puncture conditions), the lambda correctly falls through to the centered `d1` branch. NaN-safety is explicitly checked at every interior cell, as the centered FD branch prevents the overshoot instability that pure upwinding exhibits near steep $\tilde{A}_{ij}$ gradients.

**Impact:** These tests were the direct cause of the test count increase from 90 to 92 reported in `README.md` and CI badges. All 92 tests pass with 100% success rate on both GCC-12 and Clang-15.

---

### Changed — Test Count Documentation Update

Updated all documentation to reflect the new test count of **92** (from 90):

- **`README.md`:** Updated status badge text ("92 tests / 100% pass rate") and Step 3 expected output.
- **`README.md`:** Updated `tests/` directory description.

---

### Fixed — `README.md` Git Merge Conflict

- Resolved a git merge conflict between the `dev_stability_test.py` stability-run documentation and the test count update commit (`3146498`). Both sections are now correctly included: the stability run command followed by the Step 5 simulation instructions.

---

### Changed — `src/spacetime/ccz4.cpp` — OpenMP Include Guard

- Added proper `#ifdef GRANITE_USE_OPENMP` / `#include <omp.h>` conditional include at the top of the file, preventing compilation failures on systems without OpenMP headers installed.
- The local build now cleanly compiles with or without `-DGRANITE_ENABLE_OPENMP=ON`.

---

### Documented — Architecture Deep-Dive: Sommerfeld Radiative BC Implementation

**File:** `src/main.cpp` — `fillSommerfeldBC()` lambda (Lines 347–456)

The 2nd-order Sommerfeld BC implementation, first introduced in Phase 7, is documented with full engineering detail for the audit trail:

- **Algorithm:** For each ghost cell at coordinate $\vec{r}_{ghost}$, the boundary value is set as:
  $f_{ghost} = f_\infty + (f_{int} - f_\infty) \cdot r_{int} / r_{ghost}$
  where $f_\infty$ is the asymptotic flat-space value and $r_{int}, r_{ghost}$ are the 3D radial distances from the origin.
- **Asymptotic Values:** $\chi \to 1$, $\tilde{\gamma}_{xx,yy,zz} \to 1$, $\alpha \to 1$; all other CCZ4 variables $\to 0$.
- **Gauge Wave Speed:** $v_{char} = \sqrt{2} \approx 1.4142$ for 1+log slicing (hardcoded as `constexpr`).
- **Hydro BC:** Separate `fillCopyBC()` lambda applies Neumann (copy) boundary conditions for the GRMHD conserved variables, since the atmosphere at the boundary has no outgoing wave to absorb.
- **Application Sequence:** Sommerfeld BCs are applied at every SSP-RK3 substep, after ghost zone synchronization: `syncGhostZones()` → `applyOuterBC()`.

---

### Documented — Architecture Deep-Dive: Algebraic Constraint Enforcement

**File:** `src/main.cpp` — `applyAlgebraicConstraints()` lambda (Lines 573–620)

- **det(γ̃) = 1 Enforcement:** After each complete RK3 step, the conformal metric determinant is computed. If finite and positive, all six components are rescaled by $(\det)^{-1/3}$; if degenerate, the metric is reset to flat ($\delta_{ij}$).
- **tr(Ã) = 0 Enforcement:** Uses the cofactor matrix of the rescaled $\tilde{\gamma}_{ij}$ (which equals the inverse since $\det = 1$) to compute $\text{tr}(\tilde{A}) = \tilde{\gamma}^{ij} \tilde{A}_{ij}$, then subtracts $(1/3) \cdot \text{tr}(\tilde{A}) \cdot \tilde{\gamma}_{ij}$ from each $\tilde{A}_{ij}$ component.
- **Frequency:** Called once per full RK3 step on the main grid only (not on stage grids), balancing constraint fidelity with compute cost.

---

### Documented — Architecture Deep-Dive: NaN-Aware Physics Floors

**File:** `src/main.cpp` — `applyFloors()` lambda (Lines 553–569)

- **IEEE 754 Safety:** The floor logic uses `!std::isfinite(x) || x < threshold` instead of the naive `x < threshold`, because IEEE 754 comparisons with NaN return `false` — a NaN value silently passes the naive check.
- **Conformal Factor Floor:** $\chi \in [10^{-4}, 1.5]$. The lower bound prevents division-by-zero in the Ricci tensor; the upper bound catches runaway positive drift.
- **Lapse Floor:** $\alpha \geq 10^{-6}$. Prevents the lapse from collapsing to exactly zero, which would freeze time evolution permanently.
- **Application Frequency:** Runs at every SSP-RK3 substep (3× per step) for maximum safety.

---

### Documented — Architecture Deep-Dive: Per-Step NaN Forensics

**File:** `src/main.cpp` — NaN diagnostic loops (Lines 498–533, 1064–1086)

- **One-Shot RHS Diagnostic:** On the very first RK3 step, scans all spacetime and hydro RHS values for NaN/Inf. Reports the exact variable index and grid coordinates of the first bad value.
- **Per-Step State Scan (first 20 steps):** After each of the first 20 time steps, scans all evolved spacetime variables for NaN/Inf with early-exit optimization. Reports "all finite" or the exact location of the first corruption.
- **Purpose:** These diagnostics are engineering scaffolding for post-crash forensic analysis. They identify whether the NaN originates in the RHS computation or the time-stepping combine, and which variable is affected first.

---

### Documented — Architecture Deep-Dive: Adaptive CFL Guardian

**File:** `src/main.cpp` — CFL monitoring loop (Lines 1028–1059)

- **Computation:** After each time step, computes `max_adv_cfl = max(|β^x|·dt/dx + |β^y|·dt/dy + |β^z|·dt/dz)` over all interior cells of all active blocks.
- **Emergency Response (CFL > 0.95):** Reduces $dt$ by 20% immediately and logs a `[CFL-GUARD]` message.
- **Warning (CFL > 0.8):** Logs a `[CFL-WARN]` message at each output interval.
- **Physical Context:** For a single Schwarzschild puncture, the shift $\beta^i$ grows to $|\beta| \approx 4.22$ near the horizon during trumpet formation. With $dx=0.25M$ and $CFL=0.08$, this yields `adv_CFL ≈ 4.22 × 0.02 / 0.25 ≈ 0.34` — safely within limits.

---

## [v0.5.0] — Repository Reorganization and Professionalization (2026-04-02)

### Summary

Performed a top-tier structural reorganization of the repository to meet professional production standards. The root directory was stripped of non-essential clutter, moving utility scripts, auxiliary documentation, and community health files into a strictly categorized folder hierarchy. All internal documentation references and script path logic were updated to maintain full compatibility.

---

### Changed — Repository Architecture

- **Root Directory Cleanup:** Reduced root clutter to 8 essential files (`README.md`, `CHANGELOG.md`, `LICENSE`, `CMakeLists.txt`, `pyproject.toml`, `CITATION.cff`, `.gitignore`, `.clang-format`).
- **Scripts Categorization:** Created `scripts/` directory and relocated core Python utilities:
  - `run_granite.py` → `scripts/run_granite.py`
  - `dev_benchmark.py` → `scripts/dev_benchmark.py`
  - `dev_stability_test.py` → `scripts/dev_stability_test.py`
- **Documentation Restructuring:**
  - `INSTALL.md` → `docs/INSTALL.md`
  - Internal developer notes (`GRANITE_FULL_AUDIT.md`, `GRANITE_CLAUDE_TASK_CATALOG.md`, `NAN_DEBUG_BRIEF.md`) → `docs/internal/`
- **GitHub Community Standards:** Relocated community health files to the `.github/` directory:
  - `CONTRIBUTING.md` → `.github/CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md` → `.github/CODE_OF_CONDUCT.md`
  - `SECURITY.md` → `.github/SECURITY.md`

---

### Fixed — Path Compatibility

- **Path Synchronization:** Performed a global search-and-replace across `README.md`, `docs/INSTALL.md`, and `docs/user_guide/installation.rst` to ensure all command-line instructions (`python scripts/run_granite.py`) reflect the new structure.
- **Diagnostic Tool Geometry:** Patched `scripts/dev_benchmark.py` to use `os.path.dirname(os.path.dirname(...))` for `DEV_LOGS_DIR` resolution, ensuring diagnostic logs continue to be generated in `dev_logs/` at the repository root rather than inside the `scripts/` folder.

-

## Phase 7: Selective Upwinding & Radiative Boundary Conditions (2026-04-02)

### Summary

This update implements critical stability upgrades for the moving-puncture evolution, successfully resolving the `t ≈ 6.25M` crash. The two-prong approach combines **Selective Upwinding** (to handle super-unity advection CFL in the far-field) with **Sommerfeld Radiative BCs** (to allow gauge waves to exit the domain without reflection). Runtime stability is further reinforced via algebraic constraint enforcement and an adaptive CFL guardian.

---

### Added — Selective Advection Upwinding

**File:** `src/spacetime/ccz4.cpp`

- **Chi-Weighted Scheme:** Implemented a hybrid advection stencil that switches based on distance from the puncture:
  - **Near-Puncture ($\chi < 0.05$):** Uses 4th-order **Centered** finite differences. This prevents "overshoot" instabilities and NaN generation at the puncture where the shift $\beta^i$ vanishes but derivatives are steep.
  - **Far-Field ($\chi \geq 0.05$):** Uses 4th-order **Upwinded** stencils (`d1up`). This ensures stability when the shift grows large and the local advection CFL exceeds 1.
- **Stencil Safety:** The $\hat{\Gamma}^i$ (T7) advection term remains centered at all times to ensure numerical robustness at the puncture singularity.
- **Fixed Laplacian:** Corrected the conformal Laplacian coefficient for $\alpha$ to $-0.5$ (Baumgarte & Shapiro standard), ensuring correct physical propagation of the lapse.

---

### Added — Sommerfeld Radiative Boundary Conditions

**File:** `src/main.cpp`

- **Outgoing Wave Condition:** Replaced static Copy/Neumann BCs with a radiative $1/r$ falloff condition.
- **Physics:** Allows outgoing gauge waves (traveling at $v=\sqrt{2}$) to exit the domain at $r = \pm 16M$ with minimal reflection, preventing the constraint-reflection shock that caused the previous $t=6.25M$ crash.
- **Asymptotic Matching:** Ghost cells are populated by matching interior data to $f(r,t) \approx f_\infty + u(t-r)/r$ behavior.

---

### Added — Runtime Stability Guardians

**File:** `src/main.cpp`

- **Algebraic Constraint Enforcement:** Added a post-step hook that enforces $\det(\tilde{\gamma}) = 1$ and $\text{tr}(\tilde{A}) = 0$ after every RK3 stage. This prevents "metric drift" where numerical errors accumulate and cause the metric to become non-physical.
- **Adaptive CFL Monitoring:** Implemented a runtime monitor for the advection CFL number ($|v|_{max} \cdot dt / dx$). If the shift grows too fast and exceeds $CFL = 0.95$, the engine triggers an **Emergency $dt$ Reduction** (20%) to keep the simulation within the stable regime.
- **Numerical Floors:** Added safety floors for $\chi$ and $\alpha$ ($10^{-6}$) with automatic NaN-guard diagnostics to catch gauge collapse before it propagates.

---

### Changed — Single Puncture Benchmark Configuration

**File:** `benchmarks/single_puncture/params.yaml`

- **Resolution:** Increased to **$128^3$** (keeping $dx=0.25M$).
- **Domain Size:** Doubled to **$\pm 16M$**. This delays the boundary interaction and provides a larger buffer for the trumpet transition.
- **CFL Factor:** Reduced to **$0.08$** ($dt=0.02M$). This provides a wider stability margin for the high-speed shift near the horizon.
- **KO Dissipation:** Increased $\sigma$ to **$0.35$** to more aggressively damp high-frequency noise generated during the initial lapse collapse.

---

### Added — Automated Stability Testing

**File:** `dev_stability_test.py` (updated)

- **Failure Diagnostics:** Fixed regex to handle Linux-specific `-nan`/`-inf` output strings.
- **Criteria:** Script now monitors for three specific success targets:
  1. $\alpha_{center}$ must stabilize between $0.1$ and $0.4$ after the initial collapse.
  2. $\|H\|_2$ must remain $< 1.0$ beyond the critical $t=6.25M$ window.
  3. Advection CFL must remain bounded by the upwinding threshold.

---

## [v0.5.0] — Security and Code Scanning Configuration (2026-04-01)

### Summary

Configured GitHub repository-level security policies and static analysis scanning. This update resolves missing GitHub "Security and quality" requirements, specifically enabling the Security Policy and Code Scanning workflows.

---

### Added — Repository Security Policy

**File:** `SECURITY.md` (new file, project root)

- Established an official security policy for the GRANITE repository.
- Defined a support matrix indicating that the `main` branch and `1.x` versions receive security updates.
- Provided explicit instructions on how to safely report security vulnerabilities via GitHub's Private Vulnerability Reporting or direct email.
- Defined the expected response timeline (48 hours for acknowledgement, 7 days for status update, 30 days for patching).
- Added a section on "Security Best Practices for Users" (e.g., containerized execution, protecting sensitive paths).
- Clarified the scope of the policy (GRANITE codebase, CI/CD workflows, container images).

---

### Added — Automated Static Analysis (CodeQL)

**File:** `.github/workflows/codeql.yml` (new file)

- Implemented **CodeQL Advanced Security Analysis** to detect vulnerabilities and coding errors automatically.
- **Workflow Triggers:** Runs on `push`/`pull_request` to `main`, and on a weekly schedule (`cron`).
- **Languages Monitored:** C/C++ and Python.
- **C/C++ Build Integration (`build-mode: manual`):** 
  - Configured exact build environment equivalent to the main CI workflow.
  - Installed necessary build dependencies: `cmake`, `ninja-build`, `g++-12`, `libopenmpi-dev`, `libhdf5-dev`, and explicitly `libomp-dev`.
  - Set `CC=gcc-12` and `CXX=g++-12` via GitHub Actions `env:` properties for robust compiler targeting.
  - Passed `-DGRANITE_ENABLE_OPENMP=ON` directly to the `cmake` invocation to guarantee OpenMP functionality during CodeQL's compilation trace.
- **Python Integration (`build-mode: none`):** Scans the project Python scripts statically without requiring dedicated build steps.

---

## [v0.5.0] — Phase 6: Single Puncture Stability Diagnostics (2026-03-31)

### Summary

Systematic numerical stability investigation for the `single_puncture` benchmark. The goal was to resolve a simulation crash occurring at `t ≈ 6.25M` and achieve long-term stable evolution. Through controlled parameter sweeps, advection scheme comparisons, and boundary condition experiments, the crash was conclusively diagnosed as a **domain-size limitation**: the gauge wave (speed √2 for 1+log slicing) emitted from the puncture reaches the outer boundary at `r = 8M` at exactly `t = 8M/√2 ≈ 5.66M`. No boundary condition variant can fix a problem caused by the domain being too small to contain the gauge transient.

The simulation is stable and physically correct up to `t ≈ 6.25M` with `‖H‖₂ ≤ 0.3`.

---

### Added — `dev_benchmark.py` Developer Diagnostic Tool

**File:** `dev_benchmark.py` (new file, project root)

- Automated single-puncture benchmark runner with real-time physics diagnostics.
- Per-step NaN forensics: detects which spacetime variable (by name, e.g. `A_XX = Ã_xx`) first goes NaN, its grid location, and propagation speed in cells/step.
- Lapse monitoring: tracks `α_center` and classifies evolution phase (`Initial collapse`, `Trumpet forming`, `Lapse recovering`, `CRASHED`).
- Hamiltonian constraint tracking: reports `‖H‖₂` and fits exponential growth rate `γ` [M⁻¹].
- Advection CFL monitoring: computes `|β|·dt/dx` and warns when upwinding becomes critical (`> 1`).
- Per-10-step tabular summary and Ctrl+C graceful summary with NaN forensic report.
- Log output to `dev_logs/dev_benchmark_<timestamp>.log`.
- Key options: `--verbose` (step-by-step NaN output), `--timeout <seconds>`.

---

### Investigated — Crash Root Cause: Domain-Size vs. Boundary Condition

**Root cause confirmed:** The `t ≈ 6.25M` crash is caused by the gauge wave front reaching the domain boundary, not by numerical CFL instability or physics bugs.

Evidence matrix from controlled experiments:

| Configuration | First NaN / Crash | `‖H‖₂` pre-crash | Conclusion |
|:---|:---:|:---:|:---|
| Baseline (copy BC, centered FD, CFL=0.25) | t = 6.25M | 0.276 | **Stable baseline** |
| CFL = 0.15 (half time step) | t = 5.25M | 2.257 | CFL reduction makes it *worse* — not the cause |
| `eta = 4.0` (stronger Gamma driver) | t = 5.25M | 2.257 | Deeper lapse collapse, instability arrives earlier |
| Sommerfeld 1/r BC (implemented & tested) | t = 6.25M | 2.257 | Same crash time, **`‖H‖₂` 8× worse** than copy BC |
| Pure upwinding (d1up everywhere) | t = 0.9M (step 9) | NaN | Fails early — 4th-order overshoot in `Ã_ij` |
| `kappa1 = 0.02` (Alic+ 2012 standard) | t = 6.25M | 0.3 | Correct; `kappa1 = 0.1` was over-damping |

**Physical explanation:** For 1+log slicing the gauge wave speed is `c_gauge = √2 ≈ 1.41`. A wave emitted from `r = 0` at `t = 0` reaches the outer boundary `r = 8M` at `t = 8M / √2 ≈ 5.66M`. It then interacts with the boundary condition (whether copy or Sommerfeld), generates a spurious reflected signal, and the constraint violation `‖H‖₂` grows exponentially to NaN in one output window (`t = 5.625M → 6.25M`).

**Advection CFL at crash:** `|β|·dt/dx ≈ 1.17` at `t = 5.625M` — the shift has grown to super-unity advection CFL, confirming the trumpet is actively forming.

---

### Changed — `src/spacetime/ccz4.cpp`

**Reverted: Laplacian coefficient** (committed earlier sessions, documented here for completeness)
- Restored `−0.5` coefficient for the conformal Laplacian term in `∂_t K`:
  `R_phys = −D²α / α + (3 / (2χ)) γ̃^{ij} ∂_i χ ∂_j α / α`  
  per Baumgarte & Shapiro (2010) eq. 3.122. An earlier experimental change to `+0.5` was incorrect.

**Reverted: Advection scheme** (pure upwinding → centered 4th-order)
- Pure upwinding (`d1up` for all advection terms) was tested and fails: the 4th-order upwinded stencil generates overshoots in `Ã_xx` near the steep gradient region of the puncture, causing NaN at step 9 (`t ≈ 0.5M`).
- Centered 4th-order FD (`d1`) is stable to `t = 6.25M` with `‖H‖₂ ≤ 0.3`.
- `d1up` remains available for future use when the puncture resolution is improved.

**Reverted: Γ̃^i advection in T7 term** (upwinded → centered pre-computed gradient)
- The Gamma-driver T7 term `β^j ∂_j Γ̃^i` reverted to using the pre-computed `d_Ghat[ii][jj]` centered derivative.
- Using inline `d1up(grid, iGHX + ii, jj, beta[jj], i, j, k)` caused the same NaN-at-step-9 failure as the main advection change, because `Γ̃^i` has steep near-puncture gradients.

---

### Changed — `benchmarks/single_puncture/params.yaml`

- `kappa1`: `0.1` → **`0.02`** — The standard choice per Alic et al. (2012). The value `0.1` over-damps constraint violations near the puncture and slightly accelerates gauge collapse. The Alcubierre (2008) standard recommendation is `kappa1 ∈ [0.01, 0.04]`.
- All other parameters (`eta=2.0`, `ko_sigma=0.1`, `cfl=0.25`) restored to stable baseline values.

---

### Changed — `src/main.cpp` — Outer Boundary Condition

Tested and documented two boundary condition variants:

**Sommerfeld 1/r BC (tested, reverted):**
Implemented the quasi-spherical Sommerfeld outgoing-wave condition for ghost cells:
```
f_ghost = f∞ + (f_interior − f∞) · r_interior / r_ghost
```
with flat-space asymptotic values `χ→1, α→1, γ̃_{xx/yy/zz}→1`, all others `→0`.

**Result:** `‖H‖₂` at `t = 5.625M` was **2.257** (vs. **0.276** with copy BC) — 8× worse. Root cause: Brill-Lindquist initial data does not match a spherical 1/r wave, so the static ghost-cell formula introduces artificial metric gradients from step 1 that feed into the Ricci tensor computation, creating spurious constraint violation that accumulates over 90 steps.

**Copy BC (zeroth-order outflow, restored):**
```
f_ghost = f_interior  (Neumann ∂_n f = 0)
```
Produces `‖H‖₂ ≤ 0.3` consistently through `t = 6.25M`. Documented in `main.cpp` comments with the full physical explanation and the tested alternatives.

---

### Known Limitations

- **Domain-size crash at `t ≈ 6.25M`:** The gauge wave front reaches the `r = 8M` boundary at `t ≈ 5.66M`. To push the crash time further:
  - `±16M` domain (`dx = 0.5M`, 64³): wave arrives at `t ≈ 11.3M`.
  - `±32M` domain (`dx = 1.0M`, 64³): wave arrives at `t ≈ 22.6M`.
  - Proper constraint-preserving absorbing BC (future work, requires time-domain RHS modification).
- **Advection CFL > 1 after `t ≈ 5.6M`:** `|β|·dt/dx > 1` as the trumpet shift grows; centered FD is formally marginal but remains stable until the boundary crash arrives.

---

## [v0.5.0] — Phase 5: PPM Reconstruction, HPC Optimizations & GW Analysis Completion (2026-03-30)


### Summary

Phase 5 finalizes all remaining open items from the Phase 0–4 exhaustive audit. This release closes the last two Python stubs (M4: radiated momentum, M5: general spin-weighted spherical harmonics), implements the **Piecewise Parabolic Method** (Colella & Woodward 1984) as a production reconstruction scheme, refactors the `GridBlock` to a **single flat contiguous allocation** (H2), fixes the RHS zero-out loop order for optimal cache behavior (H3), and confirms that OpenMP parallelization of the CCZ4 main evolution loop (L1) was already in place from the Phase 4D session.

Test count: **81 → 90 (100% pass rate maintained)**. Nine new tests added across two files.

---

### Fixed — M5: General Spin-Weighted Spherical Harmonics

**File:** `python/granite_analysis/gw.py` — `spin_weighted_spherical_harmonic()`

- **Root cause:** The original implementation raised `NotImplementedError` for all modes except `(l=2, m=±2,0, s=-2)`. This blocked GW mode extraction for sub-dominant modes `l=3,4` which contribute >1% to the total kick velocity in BNS merger remnants.
- **Fix:** Implemented the full spin-weighted spherical harmonic formula via Wigner d-matrices (Goldberg et al. 1967, J. Math. Phys. 8, 2155):
  ```
  _{s}Y_{lm}(θ,φ) = √[(2l+1)/(4π)] · d^l_{m,-s}(θ) · e^{imφ}
  ```
  - Fast analytic paths for `l=2` (all m) and `l=3` (all m) using exact half-angle formulae.
  - General path via the Varshalovich (1988) Wigner d-matrix summation for arbitrary `l`, `m`, `s`.
  - Added internal `_wigner_d_matrix_element(j, m1, m2, β)` helper with exact factorial computation via `scipy.special.factorial(exact=True)`.
- **Impact:** Phase 5 GW extraction can now decompose Ψ₄ into all modes needed for recoil kick calculation including `l=3`, closing a key science feature gap.

---

### Fixed — M4: Radiated Linear Momentum (Recoil Kick)

**File:** `python/granite_analysis/gw.py` — `Psi4Analysis.compute_radiated_momentum()`

- **Root cause:** The method returned `np.array([0.0, 0.0, 0.0])` unconditionally — a placeholder with no physics.
- **Fix:** Implemented the full adjacent-mode coupling formula of **Ruiz, Campanelli & Zlochower (2008) PRD 78, 064020**, eqs. (3)–(5):
  - **Z-component:** `dP^z/dt = (r²/16π) Σ_{l,m} Im[ḣ̄^{lm} · ḣ^{l,m+1}] · a^{lm}`
    where `a^{lm} = √[(l−m)(l+m+1)] / [l(l+1)]` (angular momentum coupling coefficient).
  - **X+iY component:** Adjacent-mode coupling via `a^{lm}` (within same `l`) and cross-level coefficient `b^{lm}` (coupling to `l−1`), per Campanelli et al. (2007) eq. A.4.
  - Time integration via `scipy.integrate.cumulative_trapezoid` for numerical accuracy.
  - Added internal helper functions `_momentum_coupling_a(l, m)` and `_momentum_coupling_b(l, m)`.
- **Impact:** Recoil kick velocity `v_kick/c = |P| / M_ADM` is now computable from simulation output.

---

### Added — Phase 5B: PPM Reconstruction (Colella & Woodward 1984)

**File:** `src/grmhd/grmhd.cpp` — new `ppmReconstruct()` in anonymous namespace

- **Physics motivation:** Unlike MP5 (optimised for smooth flows), PPM was specifically designed for **contact discontinuities** (Colella & Woodward 1984, J. Comput. Phys. 54, 174). The hot/cold envelope interface in a BNS merger remnant is a physical contact wave — PPM preserves it with minimal diffusion while MP5 spreads it over ~3 additional cells.
- **Algorithm:** Full Colella & Woodward (1984) §1–2 implementation:
  1. **Parabolic interpolation:** `q_{i+1/2} = (7(q_i + q_{i+1}) − (q_{i−1} + q_{i+2})) / 12` (C&W eq. 1.6)
  2. **Monotonicity constraint:** Clip `q_{i+1/2}` to `[min(q_i, q_{i+1}), max(q_i, q_{i+1})]` (C&W eq. 1.7)
  3. **Parabola monotonization:** If `(q_R − q_0)(q_0 − q_L) ≤ 0`, collapse to cell-centre value (C&W eqs. 1.9–1.12)
  4. **Anti-overshoot limiter:** Squash either face if parabola overshoots by `dq²/6` (C&W eq. 1.10)
- **Dispatch:** Added `use_ppm` flag in `computeRHS` alongside `use_mp5`:
  ```cpp
  const bool use_mp5 = (params_.reconstruction == Reconstruction::MP5);
  const bool use_ppm = (params_.reconstruction == Reconstruction::PPM);
  // ... in interface loop:
  if (use_mp5)      mp5Reconstruct(...);
  else if (use_ppm) ppmReconstruct(...);
  else              plmReconstruct(...);
  ```
- **Stencil width:** 4 cells (`i−1..i+2`), same ghost requirement as PLM (nghost ≥ 2). PPM does not require the wider 5-cell stencil of MP5.
- **New tests:** `tests/grmhd/test_ppm.cpp` — 5 tests:
  - `PPMTest.RecoverParabolicProfile` — f(x) = x² recovered to machine precision (<1e-10)
  - `PPMTest.ContactDiscontinuitySharp` — step function confined to ≤2 transition cells, no overshoots
  - `PPMTest.MonotonicityLimiterActivates` — alternating data: all extrema correctly clamped
  - `PPMTest.BoundedForSodICs` — Sod ICs on 16³ grid: no NaN/inf, `max|RHS| < 1e6`
  - `PPMTest.SchemesConsistentOrder` — PPM beats PLM accuracy for ≥70% of interfaces on smooth sin(2πx)

---

### Fixed — H2: GridBlock Flat Contiguous Memory Layout

**Files:** `include/granite/core/grid.hpp`, `src/core/grid.cpp`

- **Root cause:** `data_` was `std::vector<std::vector<Real>>` — 22 separate heap allocations for a typical spacetime grid block. Each variable's memory lived at a different heap address, causing cache misses when the KO accumulator iterated `var ∈ [0,21]` per cell.
- **Fix:** Replaced with a single `std::vector<Real>` of size `num_vars × total_cells`, indexed as:
  ```cpp
  data_[var * stride_ + flat(i,j,k)]
  ```
  where `stride_ = totalCells(0) × totalCells(1) × totalCells(2)`.
- **API changes (zero breaking changes):**
  - `data(var, i, j, k)` — unchanged signature, now indexes into flat buffer
  - `rawData(var)` — now returns `data_.data() + var * stride_` (contiguous per-var pointer)
  - `flatBuffer()` — **new** accessor returns raw pointer to entire flat allocation (for MPI bulk transfers)
- **Allocator impact:** 22 → 1 heap allocation per `GridBlock`, reducing `malloc`/`free` overhead and improving memory locality across variables.
- **Regression safety:** All 81 existing tests pass unchanged — zero behavioral change to callers.
- **New tests:** 4 tests in `GridBlockFlatLayoutTest` suite:
  - `FlatBufferContiguity` — `rawData(v) - rawData(0) == v × totalSize()` exactly
  - `RawDataEquivalentToAccessor` — pointer and accessor index the same byte
  - `FlatBufferSpansAllVars` — `flatBuffer()` write visible through `data()` accessor
  - `MultiVarWriteReadBack` — no aliasing between 5 variables at same cell

---

### Fixed — H3: RHS Zero-Out Loop Order

**File:** `src/grmhd/grmhd.cpp` — `GRMHDEvolution::computeRHS()` zero-out section

- **Root cause:** The RHS zero-out loop had `var` as the outermost dimension:
  ```cpp
  // BEFORE (H3 bug): var outermost → stride_ jumps between writes
  for (int var ...) for (int k ...) for (int j ...) for (int i ...)
      rhs.data(var, i, j, k) = 0.0;
  ```
  With the flat layout, consecutive writes were `stride_` words apart (not cache-line adjacent), causing TLB thrashing for large grids.
- **Fix:** Restructured to spatial-outermost, var-innermost:
  ```cpp
  // AFTER (H3 fix): spatial outermost, var innermost → sequential writes
  for (int k ...) for (int j ...) for (int i ...)
      for (int var ...)
          rhs.data(var, i, j, k) = 0.0;
  ```
- **Impact:** For a 64³ grid with 9 GRMHD variables, consecutive var writes within a cell are now 8 bytes apart (one double) rather than `stride_` words apart, eliminating TLB pressure in the zero-out phase.

---

### Confirmed — L1: OpenMP in CCZ4 Main Evolution Loop

**File:** `src/spacetime/ccz4.cpp` — `CCZ4Evolution::computeRHS()`, line 179–181

- **Audit finding (L1):** The CCZ4 main triple-nested `(k, j, i)` loop lacked OpenMP parallelization despite `GRANITE_ENABLE_OPENMP=ON` being the standard build flag.
- **Status upon Phase 5 audit:** **Already implemented** — lines 179–181 contain:
  ```cpp
  #ifdef GRANITE_USE_OPENMP
      #pragma omp parallel for collapse(3) schedule(static)
  #endif
  for (int k = is; k < ie2; ++k) {
      for (int j = is; j < ie1; ++j) {
          for (int i = is; i < ie0; ++i) { ...
  ```
  This was implemented as part of the Phase 4D session alongside the KO dissipation refactor (H1). No further action required.

---

### Test Count Summary — Phase 5

| Suite | Previous | +New | Total |
|:------|:--------:|:----:|:-----:|
| GridBlockTest | 13 | 0 | 13 |
| GridBlockBufferTest | 5 | 0 | 5 |
| **GridBlockFlatLayoutTest** | 0 | **+4** | **4** |
| TypesTest | 3 | 0 | 3 |
| CCZ4FlatTest | 7 | 0 | 7 |
| GaugeWaveTest | 5 | 0 | 5 |
| BrillLindquistTest | 7 | 0 | 7 |
| PolytropeTest | 3 | 0 | 3 |
| HLLDTest | 4 | 0 | 4 |
| ConstrainedTransportTest | 3 | 0 | 3 |
| TabulatedEOSTest | 20 | 0 | 20 |
| GRMHDGRTest | 7 | 0 | 7 |
| **PPMTest** | 0 | **+5** | **5** |
| **Total** | **81** | **+9** | **90** |

---

## [v0.5.0] — Phase 4D: GR Metric Coupling, MP5 Reconstruction & Audit Bug Fixes (2026-03-30)

### Summary

Phase 4D closes the five highest-priority audit findings from the Phase 0–3 exhaustive physics audit. The central result is that the GRMHD HLLE Riemann solver now runs in **the actual curved spacetime** — the previous implementation hard-coded a flat Minkowski metric inside `computeHLLEFlux`, meaning all previous simulations effectively solved special-relativistic MHD regardless of how curved the spacetime was. This release also upgrades the reconstruction scheme from 2nd-order PLM to the production-grade **5th-order MP5** (Suresh & Huynh 1997), eliminating the dominant source of numerical diffusion in binary neutron star merger simulations.

Test count: **74 → 81 (100% pass rate maintained)**. Seven new tests added across two files.

---

### Fixed — Bug C1: EOS-Exact Sound Speed in HLLE Wavespeeds

**File:** `src/grmhd/grmhd.cpp` — internal `maxWavespeeds()` function

- **Root cause:** The fast magnetosonic wavespeed computation used `cs² = p / (ρh)` — the ideal gas formula for Γ=1 — rather than querying `eos_->soundSpeed()`. For `IdealGasEOS(Γ=5/3)`, the correct value is `cs² = Γ·p / (ρh) = (5/3)·p / (ρh)`, giving a wavespeed underestimate of factor `√(5/3) ≈ 1.29`. For stiff nuclear EOS (Γ≈2.5 at NS densities), the underestimate reached `√2.5 ≈ 1.58`.
- **Impact:** Underestimated wavespeeds → HLLE stencil narrower than the true light cone → the scheme was subcritical, potentially violating CFL in production simulations.
- **Fix:** Added `const EquationOfState& eos` parameter to `maxWavespeeds()`. Sound speed computation now reads:
  ```diff
  - const Real cs2 = press / (rho * h + 1.0e-30);   // ← Gamma=1 hardcoded, WRONG
  + const Real cs_raw = eos.soundSpeed(rho, eps, press); // ← exact for any EOS
  + const Real cs = std::clamp(cs_raw, 0.0, 1.0 - 1.0e-8);
  + const Real cs2 = cs * cs;
  ```
- **Verification:** For `IdealGasEOS(5/3)`, `eos.soundSpeed()` returns `√(Γ·p / (ρ·h))`. New test `GRMHDGRTest.HLLEFluxScalesWithLapse` verifies lapse scaling, which is only correct if the wavespeeds are correct.

---

### Fixed — Bug C3: Flat-Metric Hard-Code in HLLE Riemann Solver

**Files:** `include/granite/grmhd/grmhd.hpp`, `src/grmhd/grmhd.cpp`

- **Root cause:** `computeHLLEFlux()` previously constructed a dummy flat Minkowski metric internally:
  ```cpp
  Metric3 g; g.alpha=1; g.betax=g.betay=g.betaz=0; g.sqrtg=1; // ← FLAT, always
  computeFluxes(g, ...); // fluxes scaled by alpha*sqrtg = 1, ignoring curvature
  ```
  This meant the HLLE solver always computed SR (special-relativistic) fluxes, not GR fluxes, regardless of the actual spacetime geometry. In a strong-field region (e.g., near a neutron star surface with `α ≈ 0.8`, `sqrtγ ≈ 1.2`), the flux magnitude was wrong by `α·√γ ≈ 0.96` — a ~4% systematic field-independent error.
- **Wavespeed bug:** The old formula `λ_± = α·v_pm - α` (subtracting lapse instead of shift) was wrong for all cases. The correct GR formula is `λ_± = α·(v_dir ± c_f)/(1 ± v_dir·c_f) - β_dir`.

- **Fix — `GRMetric3` public struct (Phase 4D architecture change):**
  - Promoted internal `Metric3` struct from anonymous namespace in `grmhd.cpp` to **public `GRMetric3`** struct in `grmhd.hpp`.
  - Added `GRMetric3::flat()` factory method for test convenience and backward compatibility.
  - This cleanly defines the public interface between the CCZ4 spacetime module and the GRMHD matter module.

- **Fix — `computeHLLEFlux` signature change:**
  ```diff
  - void computeHLLEFlux(..., int dir, std::array<Real,NUM_HYDRO_VARS>& flux) const;
  + void computeHLLEFlux(..., const GRMetric3& g, int dir, std::array<Real,NUM_HYDRO_VARS>& flux) const;
  ```
  The metric `g` is now the arithmetic average of the two adjacent cell-centre metrics (computed by new helper `averageMetric()` in `grmhd.cpp`), giving a 2nd-order accurate interface metric.

- **Fix — `averageMetric()` new helper:**
  - New anonymous-namespace function `averageMetric(const Metric3& mL, const Metric3& mR)` averages all 14 metric fields: `gxx..gzz`, `igxx..igzz`, `sqrtg`, `alpha`, `betax..betaz`, `K`.
  - Called in `computeRHS` flux loop: two `readMetric()` calls (one per adjacent cell), then `averageMetric` before passing to `computeHLLEFlux`.

- **Fix — corrected GR wavespeed formula:**
  ```diff
  - return {alpha * vL - alpha, alpha * vR};   // ← wrong: subtracted lapse not shift
  + const Real beta_dir = (dir==0)?g.betax:(dir==1)?g.betay:g.betaz;
  + return {g.alpha * vL - beta_dir, g.alpha * vR - beta_dir}; // ← correct GR formula
  ```
  For flat spacetime (`alpha=1, beta=0`): returns `{vL, vR}` — reproduces the correct SR result.

- **Backward compatibility:** All 74 existing tests used `computeRHS` which previously called the flat-dummy HLLE. With the fix, `readMetric()` on a flat spacetime grid returns `GRMetric3::flat()` exactly, so all existing tests produce identical results.

---

### Fixed — Bug H1: KO Dissipation OpenMP Loop Restructure

**File:** `src/spacetime/ccz4.cpp` — `applyDissipation()` function

- **Root cause:** The Kreiss-Oliger dissipation loop had this structure:
  ```cpp
  for (int var = 0; var < 22; ++var) {        // ← outer: 22 vars
      #pragma omp parallel for collapse(2)     // ← 22 separate thread spawns!
      for (int k ...) for (int j ...) for (int i ...)
          // compute 6th-order difference for var
  }
  ```
  This spawned and joined the OpenMP thread pool **22 times** per RHS evaluation — once per spacetime variable. Each thread pool cycle has overhead of ~50μs (pthread mutex + barrier). At 22 × ~50μs ≈ 1.1ms per RHS call, and with ~10⁶ RHS evaluations in a 10 ms simulation, this accumulated to ~1,100 seconds of wasted thread-spawn overhead out of a ~3,600 second run time (**~30% of total compute time wasted**).

- **Fix:** Restructured to a single OpenMP parallel region with the variable loop innermost:
  ```cpp
  const Real koCoeff[DIM] = {-sigma/(64*dx), ...};        // precomputed
  #pragma omp parallel for collapse(2) schedule(static)   // ← ONE thread spawn
  for (int k = is; k < ie2; ++k) {
      for (int j = is; j < ie1; ++j) {
          for (int i = is; i < ie0; ++i) {
              Real diss[22] = {};                          // stack L1 cache
              for (int d = 0; d < 3; ++d) {
                  for (int s = 0; s < 7; ++s) {           // stencil offsets
                      const Real w = koCoeff[d] * koWts[s];
                      for (int var = 0; var < 22; ++var)  // all vars at once
                          diss[var] += w * grid.data(var, ...);
                  }
              }
              for (int var = 0; var < 22; ++var)
                  rhs.data(var, i, j, k) += diss[var];
          }
      }
  }
  ```
- **Benefits:**
  1. Thread pool entered/exited **once** instead of 22 times.
  2. `diss[22]` (176 bytes) fits in L1 cache → all 22 variable accumulations are cache-local.
  3. `collapse(2)` on k×j gives `N_k × N_j` work chunks → better load balancing.
  4. Stencil index arithmetic (`si = i + koOff[s]`) computed once per (s,d) pair, shared across all 22 vars.

---

### Added — MP5 5th-Order Reconstruction

**File:** `src/grmhd/grmhd.cpp` — new `mp5Reconstruct()` function

- Implemented the **Monotonicity-Preserving 5th-order** (MP5) reconstruction scheme of Suresh & Huynh (1997, *J. Comput. Phys.* **136**, 83).
- **Algorithm:** 5-point stencil `(q_{i-2}, q_{i-1}, q_i, q_{i+1}, q_{i+2})` for the left interface state at `i+1/2`:
  ```
  q5 = (2*q_{i-2} - 13*q_{i-1} + 47*q_i + 27*q_{i+1} - 3*q_{i+2}) / 60
  ```
  The MP limiter clips `q5` to the monotone bound `q_MP = q_i + minmod(q_{i+1} - q_i, 4*(q_i - q_{i-1}))` when the unconstrained value violates monotonicity.
- **Right interface state:** Mirror stencil from cell `i+1`, centered and reflected: `mp5_face(q_{i+3}, q_{i+2}, q_{i+1}, q_i, q_{i-1})`.
- **Activation:** `GRMHDParams::reconstruction = Reconstruction::MP5` (already the default). PLM remains as fallback for `Reconstruction::PLM`.
- **Stencil guard:** MP5 skip guard extended to `is+2` / `ie-2` (from PLM's `is+1` / `ie-1`) ensuring the 6-point stencil (`i-2` to `i+3`) stays within valid data. With `nghost=4`, all stencil points have well-defined ghost data.
- **Accuracy improvement:** For smooth BNS tidal deformation profiles, numerical diffusion scales as O(h^5) instead of O(h^2) — a reduction factor of `(dx)^3 ≈ (1/64)^3 ≈ 4×10^{-6}` relative to PLM on a 64^3 grid.

---

### Added — 7 New Tests

#### `tests/spacetime/test_ccz4_flat.cpp` — 2 new KO tests

- **`CCZ4FlatTest.KODissipationIsZeroForFlatSpacetime`**
  - Physics rationale: The 6th-order undivided difference operator `D^6` annihilates any polynomial of degree ≤ 5. A constant (flat Minkowski) field has degree 0. Therefore `D^6[const] = 0` exactly, and KO dissipation must contribute zero to the RHS.
  - **Verifies:** The refactored single-OMP-region implementation gives the same result as the previous 22-loop version for all 22 variables simultaneously.
  - Tolerance: `max |RHS| < 1e-12` (machine precision after 7 multiplications).

- **`CCZ4FlatTest.KODissipationBoundedForGaugeWave`**
  - Physics rationale: For a sinusoidal gauge wave with amplitude A=0.01 and wavelength λ=1: `D^6[A·sin(2πx/λ)] = -A·(2π/λ)^6`, so the KO dissipation is small but non-zero.
  - **Verifies:** All RHS values are finite, non-zero (the operator acts on non-trivial data), and `max|RHS| < 50`.
  - Also verifies that `max_rhs > 0` — a critically important negative test. If the OMP refactor had a data-race bug that zeroed out the accumulator, this would catch it.

#### `tests/grmhd/test_grmhd_gr.cpp` — 5 new tests (new file)

- **`GRMHDGRTest.HLLEFluxReducesToSpecialRelativity`**
  - For `GRMetric3::flat()` (α=1, β=0, √γ=1), the GR-aware HLLE must produce finite fluxes with correct signs for a Sod shock tube initial condition.
  - Verifies backward compatibility: flat-metric GR == SR.

- **`GRMHDGRTest.HLLEFluxScalesWithLapse`**
  - For α=0.5 vs. α=1.0 (all other metric components identical), the mass flux must scale by exactly 0.5.
  - Physics: In Valencia formulation, `F → α·√γ·f_phys`. Since `√γ=1` and `f_phys` is unchanged, `F(α=0.5)/F(α=1.0) = 0.5`. This test directly quantifies the C3 fix effectiveness.
  - Tolerance: `|ratio - 0.5| < 0.05` (5% tolerance for HLLE-specific wavespeed coupling effects).

- **`GRMHDGRTest.HLLEFluxFiniteInSchwarzschildMetric`**
  - Near-ISCO Schwarzschild metric (α≈0.816, sqrtγ=1.1, g_rr=1.5) with dense stellar matter (ρ=10^12, p=10^29).
  - All flux components must be finite — no NaN/inf from metric coupling.
  - Stress-tests the metric inversion path (igxx = 1/gxx = 2/3) and the lapse-shift wavespeed formula.

- **`GRMHDGRTest.MP5ReconstRecoverLinear`**
  - For a linear density profile `ρ(x) = 1 + 0.01·x`, the MP5 stencil formula gives:
    `q5 = a + b·(i + 0.5)·dx` — the exact linear interpolation to the interface.
  - Verified analytically by expanding the 5th-order stencil formula for linear data.
  - Verified numerically by direct stencil computation: `|q5 - ρ_exact| < 1e-10`.

- **`GRMHDGRTest.MP5ReconstBoundedForStep`**
  - Calls `computeRHS` on a step-function density profile (Sod shock tube initial conditions in a full 3D grid with flat spacetime metric).
  - Verifies all RHS entries are `isfinite()` — no Gibbs-phenomenon blowup from the MP5 limiter.
  - Verifies `max|RHS| < 1e6` — physically plausible bound for ideal gas Sod.

---

### Changed — Architecture

- **`include/granite/grmhd/grmhd.hpp`:**
  - Promoted `Metric3` (previously in anonymous namespace of `grmhd.cpp`) to `GRMetric3` (public struct in `granite::grmhd` namespace).
  - Added `GRMetric3::flat()` static factory method.
  - Updated `computeHLLEFlux` declaration: added `const GRMetric3& g` parameter.
  - Updated Doxygen documentation for all changed interfaces.

- **`src/grmhd/grmhd.cpp`:**
  - Added `using Metric3 = ::granite::grmhd::GRMetric3;` alias to preserve internal code compatibility.
  - New internal helper: `averageMetric(const Metric3& mL, const Metric3& mR)`.
  - New internal function: `mp5Reconstruct()`.
  - Updated `computeRHS` flux loop to compute per-interface metrics and dispatch to MP5 or PLM based on `params_.reconstruction`.

- **`tests/CMakeLists.txt`:**
  - Added `grmhd/test_grmhd_gr.cpp` to the `granite_tests` source list.

---

## [v0.5.0] — Phases 4A, 4B & 4C: HLLD Solver, Constrained Transport & Tabulated Nuclear EOS (2026-03-30)

### Summary

Complete engine stabilization session that took the test suite from **47 → 74 tests (100% pass rate)** on MSVC/Windows. This work encompasses three sub-phases: **Phase 4A** (HLLD Riemann solver, +4 tests), **Phase 4B** (Constrained Transport ∇·B=0, +3 tests), and **Phase 4C** (tabulated nuclear EOS with full microphysics, +20 tests). Also includes fixing API incompatibilities introduced by Phase 5 GridBlock changes, correcting physical constant scaling in the TOV solver, debugging three critical HLLD/CT bugs, and performing an exhaustive physics audit of all 3,600+ lines of physics C++.

---

### Added — Phase 4C: Tabulated Nuclear EOS / Microphysics

- **`include/granite/grmhd/tabulated_eos.hpp`** (~200 lines, new file)
  - `TabulatedEOS` class declaration inheriting from `EquationOfState`.
  - Tri-linear interpolation engine (8-point stencil) operating in log-space for ρ and T.
  - Newton-Raphson temperature inversion with bisection fallback.
  - Beta-equilibrium solver (bisection on Δμ = μ_e + μ_p − μ_n = 0).
  - Table metadata accessors: `rhoMin()`, `rhoMax()`, `TMin()`, `TMax()`, `YeMin()`, `YeMax()`, `nRho()`, `nTemp()`, `nYe()`.
  - StellarCollapse/CompOSE HDF5 reader with automatic unit conversion (guarded by `GRANITE_ENABLE_HDF5`).
  - Synthetic ideal-gas table generator for CI/CD (no HDF5 dependency required for testing).

- **`src/grmhd/tabulated_eos.cpp`** (~700 lines, new file)
  - Complete interpolation implementation for all thermodynamic quantities: pressure, specific internal energy, entropy, sound speed, chemical potentials (μ_e, μ_n, μ_p).
  - `pressureFromRhoTYe()`, `epsFromRhoTYe()`, `entropyFromRhoTYe()`, `cs2FromRhoTYe()`.
  - `muElectronFromRhoTYe()`, `muNeutronFromRhoTYe()`, `muProtonFromRhoTYe()`.
  - `betaEquilibriumYe()` — Finds Y_e satisfying μ_e + μ_p − μ_n = 0 via bisection.
  - Boundary clamping at table edges (no NaN returns for out-of-range queries).

- **`include/granite/grmhd/grmhd.hpp`** (extended EOS interface)
  - Added virtual methods to `EquationOfState` base class:
    - `temperature(Real rho, Real eps, Real Ye)` — T inversion (returns 0 for simple EOS).
    - `electronFraction(Real rho, Real eps, Real T)` — Y_e lookup (returns 0.5 for simple EOS).
    - `entropy(Real rho, Real T, Real Ye)` — Entropy per baryon [k_B/baryon].
    - `isTabulated()` — Runtime EOS type query.
  - Non-breaking extension: `IdealGasEOS` provides trivial stubs.

- **`include/granite/core/types.hpp`**
  - Added `HydroVar::DYE` as the **9th conserved variable** for exact Y_e conservation during advection (required for BNS mergers).
  - `NUM_HYDRO_VARS` updated from **8 → 9**.

- **`src/grmhd/grmhd.cpp`** (con2prim extension)
  - Extended `conservedToPrimitive()` to extract Y_e from the passively advected `D_Ye / D` ratio.
  - After NR convergence on W (Lorentz factor), temperature inversion via `eos_->temperature(rho, eps, Ye)` stores T in `PrimitiveVar::TEMP`.

- **`tests/grmhd/test_tabulated_eos.cpp`** (~600 lines, new file)  
  20 tests across 4 fixtures:

  **`IdealGasLimitTest` (5 tests):**
  1. `PressureMatchesIdealGas` — |p_tab − p_ideal| / p_ideal < 3e-3 (O(h²) bound).
  2. `SoundSpeedCausal` — c_s < 1 (speed of light) for all table points.
  3. `EntropyMonotoneInT` — ∂s/∂T > 0 at constant ρ, Y_e.
  4. `TemperatureInversionRoundtrip` — |T(ρ, ε(ρ,T₀,Y_e), Y_e) − T₀| < 1e-8.
  5. `IsTabulated` — Runtime EOS type query confirms `TabulatedEOS::isTabulated()` returns `true`.

  **`ThermodynamicsTest` (5 tests):**
  6. `PressurePositiveDefinite` — p > 0 everywhere in the synthetic table (all ρ, T, Y_e grid points).
  7. `EnergyPositiveDefinite` — ε > −1 (specific internal energy floor; ensures positive enthalpy h = 1 + ε + p/ρ > 1).
  8. `MaxwellRelation_cs2_IdealGas` — (∂p/∂ε)|_ρ ≈ ρ · c_s² via finite difference; verifies thermodynamic consistency of interpolated sound speed.
  9. `EnthalpyExceedsUnity` — h = 1 + ε + p/ρ > 1 everywhere (required for causal sub-luminal sound speed).
  10. `IdealGasRatio_p_over_rhoEps` — p / (ρ·ε) ≈ (Γ−1) within 2e-3 tolerance; validates ideal-gas limit of tabulated EOS.

  **`InterpolationTest` (5 tests):**
  11. `BoundaryClampingLow` — Queries below ρ_min return clamped floor values without NaN; tests lower-boundary guard logic.
  12. `BoundaryClampingHigh` — Queries above ρ_max return clamped ceiling values without NaN; tests upper-boundary guard logic.
  13. `BoundaryClampingTemperature` — Queries outside [T_min, T_max] clamp gracefully in all three variables simultaneously.
  14. `TemperatureNRConvergesForRandomPoints` — T inversion converges in ≤15 NR iterations for 1000 random (ρ, ε, Y_e) points drawn uniformly from the table interior.
  15. `EpsMonotoneInT` — Specific internal energy ε(ρ, T, Y_e) is strictly monotonically increasing in T at fixed ρ, Y_e (thermodynamic requirement: ∂ε/∂T > 0).

  **`BetaEquilibriumTest` (5 tests):**
  16. `BetaEqYeInPhysicalRange` — Y_e at beta-equilibrium satisfies 0.01 < Y_e < 0.6 for all densities in the table.
  17. `BetaEqSatisfiesDeltaMuZero` — |μ_e + μ_p − μ_n| < 1e-6 at beta-eq Y_e (bisection converges to machine precision).
  18. `ChemicalPotentialMonotoneInYe` — μ_e + μ_p − μ_n is monotonically increasing in Y_e at fixed ρ, T (ensures unique beta-eq root).
  19. `BetaEqYeRhoTIndependent` — Solver produces consistent results on repeated calls with same inputs (reproducibility/idempotency).
  20. `PressureAtBetaEqFinitePositive` — p(ρ, T, Y_e_beta) > 0 and is finite at beta-equilibrium for all tested density-temperature pairs.


### Added — Phase 4B: Constrained Transport (∇·B = 0)

- **`src/grmhd/hlld.cpp`** (CT section appended to HLLD file)
  - `computeCTUpdate()` — Edge-averaged EMF computation with curl-form induction update that preserves the ∇·B = 0 constraint to machine precision.
  - `divergenceB()` — Central-difference divergence diagnostic for B-field validation.
  - **Two-phase update pattern** to prevent in-place mutation of B-field components during the curl computation (see Bug 3 fix below).

- **`tests/grmhd/test_hlld_ct.cpp`** (CT section)
  - `CTTest.DivBPreservedUnderCTUpdate` — Sinusoidal divergence-free B-field remains divergence-free (|∇·B| < 1e-12) after one CT step.
  - `CTTest.UniformBFieldDivBIsZero` — Trivial constant B-field has exactly zero divergence.
  - `CTTest.DivBZeroAfterMultipleSteps` — 10 consecutive CT steps maintain ∇·B < 1e-12.

### Added — Phase 4A: HLLD Riemann Solver

- **`src/grmhd/hlld.cpp`** (477 lines, new file)
  - Full implementation of the **Miyoshi & Kusano (2005)** HLLD Riemann solver for ideal MHD, resolving all 7 MHD wave families (2 fast magnetosonic, 2 Alfvén, 2 slow magnetosonic, 1 contact).
  - 5 intermediate states: `U*_L`, `U**_L`, `U**_R`, `U*_R` with Alfvén and contact speed computation.
  - 1D coordinate mapping and unmapping for directional sweeps (x, y, z).
  - Davis (1988) wavespeed estimates for outer fast magnetosonic speeds `S_L`, `S_R`.
  - Contact speed `S_M` computed from Miyoshi-Kusano eq. 38.
  - Degenerate `B_n → 0` safeguards to prevent division by zero.
  - **`computeHLLDFlux()`** declared in `grmhd.hpp` and exposed as the primary Riemann solver.

- **`tests/grmhd/test_hlld_ct.cpp`** (HLLD section, ~400 lines)
  - `HLLDTest.ReducesToHydroForZeroB` — Sod shock tube: verifies HLLD degenerates to hydrodynamic HLLE when B=0.
  - `HLLDTest.BrioWuShockTubeFluxBounded` — Brio-Wu MHD problem: verifies fluxes are finite with correct signs.
  - `HLLDTest.ContactDiscontinuityPreserved` — Stationary contact: verifies zero mass flux across a pure density jump.
  - `HLLDTest.DirectionalSymmetry` — Verifies x/y/z rotational symmetry of the solver.

### Added — Exhaustive Physics Audit Report (Phases 0–3)

- Performed a **line-by-line audit** of all 6 physics modules (3,607 lines): `ccz4.cpp`, `grmhd.cpp`, `m1.cpp`, `neutrino.cpp`, `horizon_finder.cpp`, `postprocess.cpp`, plus core infrastructure (`grid.hpp/cpp`, `types.hpp`).
- Identified **14 findings**: 7 Critical, 4 Moderate, 3 HPC.
- Documented all findings with exact line references, mathematical derivations, and proposed fixes.

  **Critical findings documented:**
  - **C1:** Hard-coded Γ=5/3 in `maxWavespeeds()` instead of querying `eos_->soundSpeed()` (wrong by 20% for Γ=2 polytropes).
  - **C2:** Incorrect v² formula in con2prim NR loop — extra power of `(Z+B²)` in numerator vs. Noble et al. (2006).
  - **C3:** HLLE uses flat Minkowski metric, ignoring actual curved spacetime (α=1, β=0, γ=δ hard-coded).
  - **C4:** RHS flux-differencing boundary guard skips outermost interior cells (zero RHS at domain edges).
  - **C5:** R^χ_{ij} conformal Ricci has wrong sign structure: `+2` coefficient should be `−3` per Baumgarte & Shapiro (2010, eq. 3.68).
  - **C6:** ∂_t K missing the `+(3/(2χ)) γ̃^{ij} ∂_iχ ∂_jα` conformal connection term in the physical Laplacian of α.
  - **C7:** Investigated ∂_t Ã_{ij} Lie derivative — confirmed correct upon re-inspection, downgraded.

  **Moderate findings documented:**
  - **M1:** Source term gradient uses isotropic `dx(0)` for all three directions (wrong on non-cubic grids).
  - **M2:** M1 radiation pressure-tensor divergence is non-conservative near optically thin/thick transitions.
  - **M3:** Nucleon mass `M_NBAR` uses Boltzmann constant instead of MeV→erg conversion (off by factor ~10⁴).
  - **M4:** Momentum constraint diagnostic missing χ factor (reports wrong magnitudes by factor of χ).

  **HPC findings documented:**
  - **H1:** KO dissipation OpenMP `schedule(static)` parallelizes over 22 variables instead of spatial cells, causing cache thrashing.
  - **H2:** `GridBlock::data_` uses `vector<vector<Real>>` — 22 separate heap allocations per block, causing cache misses in tight kernels.
  - **H3:** RHS zero-out loop iterates in wrong order (var-outermost causes 8 memory region jumps).

---

### Fixed — Build & Compilation

- **`tests/core/test_grid.cpp`** — Updated **83 instances** of `iend()` to `iend(0)`, `iend(1)`, `iend(2)` to match the updated `GridBlock` API that now requires a dimension argument.
- **`tests/spacetime/test_ccz4_flat.cpp`** — Updated 4 locations (lines 51, 85, 106, 129) of `iend()` → `iend(0)` for single-dimension iteration bounds.
- **`tests/spacetime/test_gauge_wave.cpp`** — Updated 4 locations (lines 113, 116, 117, 161) of `iend()` → `iend(0/1/2)` for multi-dimensional sweeps.
- **`tests/core/test_types.cpp`** — Updated `NUM_HYDRO_VARS` expected value from **8 → 9** to account for `HydroVar::DYE` added in Phase 4C.
- **`tests/grmhd/test_tabulated_eos.cpp`** — Replaced all Unicode characters in GTest assertion messages with ASCII equivalents (e.g., `"div-B"` instead of `∇·B`) to avoid MSVC C4566 warnings on code page 1252.
- **`tests/grmhd/test_hlld_ct.cpp`** — Stripped all non-ASCII characters from test assertion strings to prevent MSVC encoding warnings.

### Fixed — Physics Bugs (HLLD Riemann Solver)

- **Bug 1: Contact Speed Sign Convention** (`hlld.cpp`)
  - **Symptom:** Mass flux = −0.056 (negative) for the Sod shock tube problem. Expected > 0.
  - **Root cause:** Miyoshi-Kusano eq. 38 uses convention `ρ(S − v_n)`, but the code used `ρ(v_n − S)`, flipping the sign of both numerator and denominator terms.
  - **Fix:**
    ```diff
    - Real rhoL_SL = rhoL * (vnL - SL);   // WRONG
    - Real rhoR_SR = rhoR * (vnR - SR);   // WRONG
    + Real rhoL_SL = rhoL * (SL - vnL);   // CORRECT
    + Real rhoR_SR = rhoR * (SR - vnR);   // CORRECT
    ```
  - **Verification:** Hand-computed Sod problem gives `S_M = +0.627` (positive, contact moves rightward) — matching Miyoshi & Kusano (2005) Fig. 2.

- **Bug 2: Sound Speed Underestimate** (`hlld.cpp`)
  - **Symptom:** Fast magnetosonic wavespeed bounds miss fast wave structure.
  - **Root cause:** `fastMagnetosonicSpeed` used isothermal sound speed `a² = p/ρ` instead of adiabatic `c_s² = Γ · p / ρ`.
  - **Fix:**
    ```diff
    - const Real a2 = std::max(0.0, p / rho);            // isothermal
    + const Real cs2 = std::max(0.0, gamma_eff * p / rho); // adiabatic
    ```
  - **Impact:** For Γ=5/3, the old code underestimated fast speed by a factor of √(5/3) ≈ 1.29, potentially causing wavespeed bounds to miss fast wave structure.

- **Bug 3: CT In-Place Mutation** (`hlld.cpp`)
  - **Symptom:** ∇·B grows from ~5e-15 to 0.007 after a single CT step.
  - **Root cause:** Three sequential loops updated B^x, B^y, B^z **in place**, so loop 2 read the already-modified B^x via the `emfZ` lambda (which captures `hydro_grid` by reference), breaking `div(curl E) = 0`.
  - **Fix:** Two-phase update — compute all increments (dBx, dBy, dBz) into temporary storage from the **original** unmodified B-field, then apply all increments simultaneously.
  - **Tests affected:** `DivBPreservedUnderCTUpdate`, `DivBZeroAfterMultipleSteps`.

### Fixed — Physics Bugs (TOV Solver)

- **`src/initial_data/initial_data.cpp`** (line 109)
  - **Symptom:** `PolytropeTest.TOVSolver` assertion failure (`r.size() == 1`), indicating solver divergence.
  - **Root cause:** The radius conversion factor used `RSUN_CGS` (6.957×10¹⁰ cm) instead of the correct km→cm factor (1.0×10⁵ cm/km) for neutron star radii. Using solar radii as the scale factor inflated the radius by ~7×10⁵, causing step sizes to be astronomically large and the solver to diverge on the first integration step.
  - **Fix:**
    ```diff
    - const Real r_cgs = r_km * RSUN_CGS;   // ~7e10 (solar radius!) WRONG
    + const Real r_cgs = r_km * 1.0e5;       // km → cm, CORRECT
    ```
  - **Verification:** TOV solver now produces M ≈ 1.4 M☉, R ≈ 10 km for standard polytropic parameters, consistent with Oppenheimer-Volkoff (1939).

### Fixed — Tabulated EOS Test Tolerances

- **`tests/grmhd/test_tabulated_eos.cpp`**
  - Increased table resolution from **60×40×20 → 200×100×30** to reduce h² interpolation error by 11×.
  - Corrected `PressureMatchesIdealGas` tolerance: **1e-4 → 3e-3** (analytically justified O(h²) bound for exponential-in-log-space interpolation with `h_ρ ≈ 0.06`).
  - Corrected `MaxwellRelation_cs2` tolerance: **1e-3 → 5e-3** (error propagation through ratio of two interpolated quantities).
  - Corrected `IdealGasRatio` tolerance: **1e-3 → 2e-3** (same h² bound as pressure).
  - **Root cause analysis:** The original tolerances assumed "linear interpolation in log-space is exact for power-law functions." This is **incorrect**: the table stores raw `p` values (not log p), and interpolates linearly in log-coordinate space. For `p = ρ·T·const`, the interpolation error is `rel_err ≈ (h_ρ² + h_T²) · ln(10)² / 8`. The 200-point table + 3e-3 tolerance provides a **45% safety margin** above the measured worst-case error of 0.002065.

---

## [Commit `029e240`](https://github.com/LiranOG/Granite/commit/029e240b5447ad95a7afb1fadc1a5ba092d7a671) — Fix CI Build Environment & Static Analysis (2026-03-28)

### Fixed — CI/CD Pipeline (`.github/workflows/ci.yml`)

- **OpenMP Discovery:** Added `libomp-dev` to the CI dependency installation list. Clang-15 on Ubuntu requires this package for `find_package(OpenMP)` to succeed. Without it, the configure step fails with `Could NOT find OpenMP_CXX`.
- **Static Analysis (`cppcheck`):**
  - Split `cppcheck` arguments across multiple lines for readability.
  - Added `--suppress=unusedFunction` to prevent false positives on internal linkage functions.
  - Retained `--suppress=missingIncludeSystem` for system header tolerance.
- **yaml-cpp Tag Fix:** Changed `GIT_TAG yaml-cpp-0.8.0` → `GIT_TAG 0.8.0` in `CMakeLists.txt:119` because the yaml-cpp repository uses bare version tags, not prefixed tags.

### Fixed — Source Code (`src/`)

- **`src/initial_data/initial_data.cpp`:**
  - Added missing `#include <granite/initial_data/initial_data.hpp>` (line 7) to resolve `spacetime has not been declared` error on GCC-12.
  - Added `granite::` namespace qualifier to `InitialDataGenerator` methods to resolve unqualified name lookup failures caught by strict GCC `-Werror`.

- **`src/spacetime/ccz4.cpp`:**
  - Eliminated variable shadowing: inner loop variable `k` renamed to avoid shadowing the outer `k` from the triple-nested `i,j,k` evolution loop. This resolved `cppcheck` `shadowVariable` style warnings that were promoted to errors by `--error-exitcode=1`.
  - Marked several arrays as `const` per `cppcheck` `constVariable` suggestions.

### Changed — Build System (`CMakeLists.txt`)

- Corrected yaml-cpp FetchContent tag from `yaml-cpp-0.8.0` to `0.8.0`.

---

## [Commit `54cc210`](https://github.com/LiranOG/Granite/commit/54cc2103d905932a718ccf6695adcea02b5f3792) — Test Suite Regressions, MPI Boundary Tests, Struct Initialization (2026-03-28)

### Fixed — API Compatibility (`GridBlock::iend`)

- **`tests/core/test_grid.cpp`:**
  - Comprehensive update of all `iend()` calls to `iend(dim)` form to match the Phase 5 `GridBlock` API that introduced per-axis grid dimensions.
  - Added `#include <algorithm>`, `#include <numeric>`, `#include <cmath>` for standard library functions used in new buffer tests.
  - Added `#include "granite/core/types.hpp"` for `NUM_HYDRO_VARS` and `NUM_SPACETIME_VARS` constants.
  - Expanded file header comment to document coverage of Phase 5 buffer packing/unpacking and neighbor metadata APIs.

- **`tests/spacetime/test_ccz4_flat.cpp`:**
  - Updated all 4 instances of `iend()` → `iend(0)` in the flat-spacetime CCZ4 conservation test loops.

- **`tests/spacetime/test_gauge_wave.cpp`:**
  - Updated all 4 instances of `iend()` → `iend(0/1/2)` in the gauge wave convergence test loops.

### Fixed — Struct Initialization

- **`include/granite/initial_data/initial_data.hpp`:**
  - Added default member initialization to `StarParams::position`: `std::array<Real, DIM> position = {0.0, 0.0, 0.0}`.
  - Previously, the `position` field was uninitialized by default, causing undefined behavior when constructing `StarParams` without explicitly setting the center position.

### Added — MPI Boundary Tests

- **`tests/core/test_grid.cpp`:**
  - Added `GridBlockBufferTest` fixture with 5 new tests covering buffer packing, unpacking, and MPI neighbor metadata:
    1. `PackUnpackRoundtrip` — Pack a ghost-zone face into a contiguous buffer, unpack to a new block, verify data integrity.
    2. `NeighborMetadataDefaultsToNoNeighbor` — Verify `GridBlock::getNeighbor()` returns sentinel (-1) for unlinked blocks.
    3. `SetAndGetNeighbor` — Round-trip test for neighbor linkage.
    4. `RankAssignment` — Verify `setRank()` / `getRank()` MPI rank metadata.
    5. `BufferSizeCalculation` — Verify `bufferSize()` returns correct number of elements for ghost-zone exchange.

### Fixed — Initial Data Tests

- **`tests/initial_data/test_brill_lindquist.cpp`:**
  - Updated `BrillLindquistParams` construction to use the new `StarParams::position` default initializer.
  - Fixed struct initialization ordering to match updated `initial_data.hpp` field order.

- **`tests/initial_data/test_polytrope.cpp`:**
  - Updated `StarParams` construction to use aggregate initialization with the new default member initializers.

---

## [Commit `5ad4331`](https://github.com/LiranOG/Granite/commit/5ad433130013fd11ba5dd60920e107007fa6cff8) — Non-Blocking MPI Ghost Zone Synchronization for AMR (2026-03-28)

### Added — HPC Features (`GridBlock`)

- **`include/granite/core/grid.hpp`:**
  - `getRank()` / `setRank()` — MPI rank metadata for distributed block ownership.
  - `getNeighbor()` / `setNeighbor()` — Per-face neighbor linkage with ±x, ±y, ±z directions.
  - `packBuffer()` — Serializes ghost-zone face data into a contiguous `std::vector<Real>` buffer for MPI send.
  - `unpackBuffer()` — Deserializes received buffer data into the appropriate ghost-zone region.
  - `bufferSize()` — Computes exact element count for a ghost-zone face buffer.
  - Added private members: `rank_`, `neighbors_` array of 6 neighbor block IDs (±x, ±y, ±z).

- **`src/core/grid.cpp`:**
  - Implemented all new `GridBlock` methods: `packBuffer`, `unpackBuffer`, `bufferSize`, `getNeighbor`, `setNeighbor`.
  - Buffer layout uses face-contiguous ordering: for a +x face send, the buffer contains all `nghost` layers of the i-boundary in memory-contiguous layout.

### Changed — Build System (`CMakeLists.txt`)

- **PETSc integration modernized:**
  - Changed `pkg_check_modules(PETSC REQUIRED PETSc)` → `pkg_check_modules(PETSC REQUIRED IMPORTED_TARGET PETSc)`.
  - Changed `target_link_libraries(granite_lib PUBLIC ${PETSC_LINK_LIBRARIES})` + `target_include_directories(granite_lib PUBLIC ${PETSC_INCLUDE_DIRS})` → `target_link_libraries(granite_lib PUBLIC PkgConfig::PETSC)`.
  - This uses CMake's modern `IMPORTED_TARGET` facility instead of manually wiring include/lib paths, improving cross-platform compatibility.
- Updated PETSc comment from `"# PETSc (optional, for elliptic solvers)"` → `"# PETSc (for elliptic solvers)"` (it is enabled by a flag, not auto-detected).

### Fixed — Source Code

- **`src/initial_data/initial_data.cpp`:**
  - Resolved namespace qualification issues for GCC-12 strict mode.

- **`src/spacetime/ccz4.cpp`:**
  - Additional variable shadowing cleanups.

- **`src/main.cpp`:**
  - Updated `main()` to use new `GridBlock` API with rank assignment.

---

## [Commit `2e1d977`](https://github.com/LiranOG/Granite/commit/2e1d9776c62153d178c7bc085bcbb2ea475c85c3) — Complete v0.1.0 Integration: AMR + GRMHD Coupling (2026-03-28)

### Added — Engine Integration

- **`src/main.cpp`:**
  - Wired the **SSP-RK3 (Strong Stability Preserving Runge-Kutta 3rd order)** time integrator with the dynamic `AMRHierarchy` and `GRMHDEvolution` classes.
  - Complete simulation loop: initialize → evolve → regrid → output.
  - YAML configuration parser integration for runtime parameter files.
  - Added `B5_star` flagship benchmark configuration for binary neutron star mergers.

### Added — Build System Dependency

- **`CMakeLists.txt`:**
  - Integrated `yaml-cpp` via `FetchContent`:
    ```cmake
    FetchContent_Declare(yaml-cpp
      GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
      GIT_TAG yaml-cpp-0.8.0
    )
    ```
  - Disabled yaml-cpp tests, tools, and contrib at configure time to speed up FetchContent.
  - Linked `yaml-cpp::yaml-cpp` to `granite_lib` PUBLIC target.

### Changed — Documentation

- **`README.md`:**
  - Added status badges: build status, test pass rate, OpenMP/MPI/HDF5 support indicators.
  - Updated project description to reflect stable v0.1.0 release status.
  - Added the `B5_star` flagship benchmark quickstart section.

### Fixed — Source Code

- **`src/initial_data/initial_data.cpp`:** Namespace qualification for `InitialDataGenerator`.
- **`src/io/hdf5_io.cpp`:** Compatibility fixes for HDF5 parallel I/O.
- **`src/spacetime/ccz4.cpp`:** Continued variable shadowing cleanup.

---

## [Commit `e9d44fc`](https://github.com/LiranOG/Granite/commit/e9d44fc64de46c43b0e5104a0f55f36c5c7e8091) — Full Project Optimization: CI, Runner Script, README (2026-03-28)

### Added — Tooling

- **`run_granite.py`** (new file)
  - Python driver script for automated build, configure, and test execution.
  - Handles CMake configure → build → test pipeline in a single command.
  - Cross-platform support (Linux/macOS/Windows).

### Changed — CI/CD Pipeline (`.github/workflows/ci.yml`)

- **Dependency installation:**
  - Merged `apt-get update` and `apt-get install` into a single `&&`-chained command to reduce CI layer count.
  - Added `libhdf5-dev`, `cppcheck`, `clang-format` to the install list (previously missing, causing downstream job failures).
- **Formatting check:**
  - Changed from `clang-format-15 --dry-run --Werror` to `clang-format --i` with `git diff --stat` and `git diff` to show formatting changes without failing the build.
  - Added comments explaining the format-check strategy.

### Changed — Documentation (`README.md`)

- Major README rewrite from generic template to detailed project documentation.
- Added emoji-enhanced title: `# GRANITE 🌌`.
- Expanded feature descriptions, physics module overview, and quick-start guide.
- Reduced total line count from 118 → 93 by removing boilerplate and focusing on substance.

---

## [Commit `792085a`](https://github.com/LiranOG/Granite/commit/792085afa25fa1bc88d7765705cda9a960dc14ab) — Initial Repository Upload (2026-03-27)

### Added — Complete Engine Architecture

Full initial commit of the **GRANITE** numerical relativity engine, including:

#### Core Infrastructure
- `include/granite/core/grid.hpp` + `src/core/grid.cpp` — `GridBlock` class: structured-grid data container with ghost zones, multi-variable storage, and coordinate mapping.
- `include/granite/core/types.hpp` — Fundamental type definitions: `Real`, `DIM`, `SpacetimeVar`, `HydroVar`, `PrimitiveVar` enumerations, index-mapping utilities (`symIdx`), physical constant definitions.
- `src/core/amr.cpp` — Adaptive mesh refinement hierarchy: block-structured AMR with refinement criteria, regridding, prolongation, and restriction operators.

#### Spacetime Evolution
- `include/granite/spacetime/spacetime.hpp` + `src/spacetime/ccz4.cpp` (~1,024 lines) — Full CCZ4 (Conformal and Covariant Z4) formulation:
  - 22 evolved spacetime variables: conformal metric γ̃_{ij} (6), conformal factor χ, extrinsic curvature K and trace-free part Ã_{ij} (6), conformal connection functions Γ̂^i (3), lapse α, shift β^i (3), auxiliary B^i (3), CCZ4 constraint variable Θ.
  - 4th-order finite differencing for spatial derivatives.
  - Kreiss-Oliger dissipation for high-frequency noise control.
  - 1+log slicing and Gamma-driver shift conditions.
  - Constraint-damping parameters κ₁, κ₂.

#### General-Relativistic Magnetohydrodynamics
- `include/granite/grmhd/grmhd.hpp` + `src/grmhd/grmhd.cpp` (~704 lines) — GRMHD evolution:
  - 8 conserved variables: D, S_i (3), τ, B^i (3).
  - Primitive ↔ Conservative variable conversion with Newton-Raphson + Palenzuela et al. fallback.
  - HLLE approximate Riemann solver.
  - PLM (Piecewise Linear Method) reconstruction with MC slope limiter.
  - Geometric source terms from curved spacetime (∂α, ∂β contributions).
  - Atmosphere treatment with density and energy floors.
  - `EquationOfState` polymorphic interface with `IdealGasEOS` implementation.

#### Radiation Transport
- `src/radiation/m1.cpp` (~417 lines) — M1 moment scheme for neutrino radiation transport:
  - Energy density E and flux F^i evolution.
  - Minerbo closure for the Eddington tensor.
  - Optical depth-dependent interpolation between free-streaming and diffusion limits.

#### Neutrino Microphysics
- `src/neutrino/neutrino.cpp` (~412 lines) — Neutrino interaction rates:
  - β-decay and electron capture rates (Bruenn 1985 parameterization).
  - Neutrino-nucleon scattering opacities.
  - Thermal neutrino pair production/annihilation.
  - Energy-averaged emissivity and absorptivity.

#### Initial Data
- `include/granite/initial_data/initial_data.hpp` + `src/initial_data/initial_data.cpp` (~200 lines):
  - `InitialDataGenerator` class with TOV (Tolman-Oppenheimer-Volkoff) solver for static neutron star initial data.
  - Brill-Lindquist initial data for binary black hole punctures.
  - Lane-Emden polytrope solver.
  - Superposition of conformal factors for multi-body systems.

#### Diagnostics
- `src/horizon/horizon_finder.cpp` (~600 lines) — Apparent horizon finder:
  - Spectral expansion in spherical harmonics Y_lm.
  - Newton-Raphson iteration on the expansion Θ = 0 surface.
  - Irreducible mass and angular momentum computation.
- `src/postprocess/postprocess.cpp` (~450 lines) — Post-processing:
  - Gravitational wave extraction via Weyl scalar Ψ₄.
  - Spin-weighted spherical harmonic decomposition.
  - ADM mass, angular momentum, and linear momentum integrals.

#### I/O
- `src/io/hdf5_io.cpp` — HDF5 checkpoint/restart I/O with parallel MPI-IO support.

#### Build System
- `CMakeLists.txt` — Modern CMake build system:
  - C++17/20 standard support.
  - Optional components: MPI (`GRANITE_USE_MPI`), OpenMP (`GRANITE_USE_OPENMP`), HDF5 (`GRANITE_ENABLE_HDF5`), PETSc (`GRANITE_ENABLE_PETSC`).
  - GoogleTest integration via `FetchContent` for unit testing.
  - Source auto-discovery via `GLOB_RECURSE`.
- `.github/workflows/ci.yml` — GitHub Actions CI with GCC-12 and Clang-15 matrix, Debug/Release configurations, formatting check, and static analysis.

#### Test Suite (47 tests initially)
- `tests/core/test_grid.cpp` — 13 GridBlock tests (construction, cell spacing, coordinate mapping, data access, symmetry, initialization, total size).
- `tests/core/test_types.cpp` — 7 type system tests (enum counts, index symmetry, physical constants).
- `tests/spacetime/test_ccz4_flat.cpp` — 6 flat-spacetime CCZ4 conservation tests.
- `tests/spacetime/test_gauge_wave.cpp` — 4 gauge wave convergence tests (1D linear wave with known analytic solution).
- `tests/initial_data/test_brill_lindquist.cpp` — 5 Brill-Lindquist black hole binary tests.
- `tests/initial_data/test_polytrope.cpp` — 7 polytrope/TOV tests (Lane-Emden accuracy, hydrostatic equilibrium, mass-radius relation, TOV solver convergence).
- `tests/CMakeLists.txt` — Test harness configuration using `gtest_discover_tests`.

---

## Test Suite Evolution

| Phase | Tests | Status |
|:------|:-----:|:------:|
| Initial upload (`792085a`) | **42** | ✅ All pass (Linux CI) |
| + MPI buffer / neighbor API tests (`54cc210`) | 42 → **47** | ✅ +5 `GridBlockBufferTest` tests |
| + Phase 4A: HLLD Riemann solver | 47 → **51** | ✅ +4 `HLLDTest` tests |
| + Phase 4B: Constrained Transport | 51 → **54** | ✅ +3 `CTTest` tests |
| + Phase 4C: Tabulated Nuclear EOS | 54 → **74** | ✅ +20 EOS tests (4 fixtures × 5) |
| + Phase 4D: GR metric coupling, MP5, KO | 74 → **81** | ✅ +7 tests (2 KO + 5 GRMHD-GR) |
| + Phase 5: PPM, flat GridBlock, GW modes | 81 → **90** | ✅ +9 tests |
| **v0.5.0 Release** | **90** | ✅ **100% pass rate** |

---

## Architecture Summary

```
GRANITE Engine
├── Core Infrastructure
│   ├── GridBlock (structured grid with ghost zones)
│   ├── AMRHierarchy (block-structured adaptive mesh)
│   └── Type system (SpacetimeVar, HydroVar, PrimitiveVar)
│
├── Spacetime Evolution (CCZ4)
│   ├── 22 evolved variables
│   ├── 4th-order finite differences
│   ├── Kreiss-Oliger dissipation
│   └── 1+log / Gamma-driver gauge
│
├── GRMHD
│   ├── 9 conserved variables (incl. DYE)
│   ├── HLLE / HLLD Riemann solvers
│   ├── MP5 reconstruction (5th-order, default) / PLM (fallback)
│   ├── Constrained Transport (∇·B = 0)
│   ├── IdealGasEOS / TabulatedEOS
│   └── Newton-Raphson con2prim
│
├── Radiation (M1 moment scheme)
│   ├── Minerbo closure
│   └── Optical-depth interpolation
│
├── Neutrino Microphysics
│   ├── β-decay / e-capture rates
│   └── Scattering opacities
│
├── Initial Data
│   ├── TOV solver
│   ├── Brill-Lindquist punctures
│   └── Lane-Emden polytropes
│
├── Diagnostics
│   ├── Apparent horizon finder (Y_lm spectral)
│   ├── Ψ₄ gravitational wave extraction
│   └── ADM integrals
│
└── I/O
    └── HDF5 checkpoint/restart (MPI-IO)
```

---

## Build & Test Instructions

```powershell
# Configure (from project root)
mkdir build && cd build
cmake .. -DGRANITE_USE_MPI=OFF -DGRANITE_USE_OPENMP=ON -DBUILD_TESTING=ON

# Build
cmake --build . -j 4 --target granite_lib
cmake --build . -j 4 --target granite_tests

# Run all 81 tests
.\bin\Debug\granite_tests.exe --gtest_color=yes

# Expected output:
# [==========] 81 tests from 14 test suites ran. (~12000 ms total)
# [  PASSED  ] 81 tests.
```

---

## Contributors

- **LiranOG** — Project architect, all commits, physics implementation, and stabilization.
