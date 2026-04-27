# GRANITE – Quality Assurance & Testing (tests/)

> [!NOTE]
> **Welcome to the Testing Arena.** This directory contains the complete suite of Google Test (gtest) unit and integration tests that physically enforce the mathematical correctness of the GRANITE engine.

## Directory Overview

| Test Suite / Component | Coverage Domain |
|------------------------|-----------------|
| `amr/` | Prolongation exactness, restriction averaging, and subcycling invariants. |
| `core/` | Foundational data structures, memory layouts, and parsing rules. |
| `grmhd/` | Shock-capturing methods, C2P inversions, and ideal fluid hydrodynamics. |
| `horizon/` | Newton-Raphson finder convergence and irreducible mass geometry. |
| `initial_data/` | Analytic formulation accuracy and boundary condition compatibility. |
| `io/` | HDF5 state serialization, memory consistency, and restart capabilities. |
| `radiation/` | Grey M1 transport, variable Eddington closures, and asymptotic limits. |
| `spacetime/` | BSSN/CCZ4 formulation invariants, ADM constraints, and gauge propagation. |
| `CMakeLists.txt` | Test suite build configuration. |

## Directory Structure

```text
tests/
├── amr/                          # e.g., test_amr_basic.cpp
├── core/                         # Foundational logic tests
├── grmhd/                        # e.g., test_hlle_fluxes.cpp
├── horizon/                      # e.g., test_schwarzschild_horizon.cpp
├── initial_data/                 # e.g., test_brill_lindquist.cpp
├── io/                           # e.g., test_hdf5_roundtrip.cpp
├── radiation/                    # e.g., test_m1_diffusion.cpp
├── spacetime/                    # e.g., test_ccz4_rhs.cpp
├── README.md                     # You are here
└── CMakeLists.txt                # Build rules for the test harness
```

> [!IMPORTANT]
> **Test Execution:** The master test suite currently consists of **92 passing tests**. Run them locally via the orchestrated Python script: `python3 scripts/run_granite.py test`. Direct `ctest` execution is possible but may bypass environmental configuration.
