# Deep Audit Brief: Numerical Instability (NaN) in GRANITE Engine

## Executive Summary
The GRANITE numerical relativity engine is experiencing a critical numerical collapse (NaN propagation) during the evolution of the `single_puncture` benchmark. Despite several mitigation attempts, including boundary condition (BC) stabilization and physics floors, the simulation consistently fails between steps 10 and 20 (t ≈ 0.6-1.25). At this point, the lapse function at the center (`alpha_center`) and the Hamiltonian constraint norm (`||H||₂`) become `-nan`.

## Technical Context
*   **Physics Framework**: 3+1 Numerical Relativity using the **CCZ4** formulation (Alic et al. 2012).
*   **Gauge Conditions**: Moving Puncture gauge (1+log slicing, Gamma-driver shift).
*   **Numerical Discretization**: 4th-order centered finite differences with 5th/6th-order Kreiss-Oliger (KO) dissipation.
*   **Time Integration**: SSP-RK3 (3rd-order Strong Stability Preserving Runge-Kutta).
*   **Initial Configuration**: Brill-Lindquist or Bowen-York puncture data.

## Symptoms & Observed Timeline
1.  **Initial State (t=0)**: All RHS calculations are reported as finite. The Hamiltonian constraint is initially small (~1e-4) but mathematically consistent.
2.  **Stable Evolution**: Stability is maintained for the first ~8-9 steps.
3.  **Numerical Divergence (Steps 10-20)**: 
    *   Diagnostics report `[NaN-DIAG] ST_RHS var=... val=nan`.
    *   `alpha_center` drops from its physical value toward 0 and then flips to `-nan`.
    *   `||H||₂` explodes, indicating the solution is no longer satisfying Einstein's equations.
    *   The instability appears to originate at the **puncture center** (scalar singularity) rather than the boundaries in the most recent runs.

## Recent Mitigation Attempts (Current Code State)
The following measures have been implemented in the provided codebase:
1.  **Outer Boundary Stabilization**: Replaced linear extrapolation with **zeroth-order outflow (copy)** in `src/main.cpp`. This prevents the exponential growth of gradients at the domain faces.
2.  **Static Physics Floors**: 
    *   **Conformal Factor ($\chi$)**: Hard floor at $1.0 \times 10^{-4}$ in both the RHS calculation and the grid update.
    *   **Lapse ($\alpha$)**: Hard floor at $1.0 \times 10^{-6}$ to prevent time-step collapse.
3.  **Enhanced Diagnostics**: A per-step NaN scanner in the main loop (`src/main.cpp`) identifies the first variable and cell coordinate to fail.

## Critical Hypotheses for Audit
Please investigate these specific areas in the codebase:

### 1. Conformal Singularities (`ccz4.cpp`)
In the CCZ4 system, terms involving $1/\chi$ or $\partial_i \chi / \chi$ are highly sensitive near the puncture. 
- **Check**: Are the floors applied consistently *before* these divisions?
- **Check**: Verify the implementation of equation (11) from Alic et al. (2012) for the $\hat{\Gamma}^i$ RHS. A single sign error or missing factor of $\chi$ here is a common source of NaN.

### 2. Puncture Regularization (`initial_data.cpp`)
We use a regularization parameter (e.g., $10^{-20}$) to prevent division by zero at the exact puncture coordinate.
- **Problem**: If the grid resolution ($dx=0.25$) is too coarse to resolve the regularized profile, the finite difference stencil will produce massive artifacts.
- **Check**: Is the regularization scale appropriate for the 4th-order stencils used in `src/spacetime/ccz4.cpp`?

### 3. Gauge Stability (Gamma-Driver)
The moving puncture gauge requires specific parameters for the shift damping ($\eta$) and the lapse slicing.
- **Check**: Are the values for $\kappa_1$, $\kappa_2$, and $\eta$ set correctly for a single puncture evolution? (Current defaults: `kappa1=0.02`, `kappa2=0;`, `eta=2.0`).

### 4. Ghost Zone Synchronization
- **Check**: In `src/main.cpp`, verify that the `syncGhostZones` and `applyOuterBC` calls include all stages of the RK3 integrator. A missing sync between substeps will cause the 4th-order stencil to read uninitialized data.

## Claude's Audit Goal
1.  **Code Consistency**: Verify that the C++ implementation of CCZ4 and GRMHD equations is mathematically sound and free of "silent" overflows.
2.  **Stability Upgrade**: Propose any missing stabilization techniques (e.g., advection term treatment, upwinding for shift terms, or improved puncture handling).
3.  **Detailed Report**: Provide a line-by-line analysis of problematic sections and suggest the necessary fixes to achieve t=1000 stability.
