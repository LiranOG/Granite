# GRANITE – Orchestration Scripts (scripts/)

> [!NOTE]
> **Welcome to the Command Center.** This directory contains the central Python CLI and auxiliary shell scripts used to orchestrate builds, run benchmarks, execute tests, and enforce repository standards for the GRANITE engine.

## Directory Overview

| Script | Responsibility |
|--------|----------------|
| `dev_benchmark.py` | Developer performance benchmark wrapper. |
| `dev_stability_test.py` | Automated correctness and physics stability testing. |
| `health_check.py` | Pre-flight validation of optimization flags and core topology. |
| `run_granite.py` | The master Python-based CLI. Wraps CMake, CTest, and formatting. |
| `run_granite_hpc.py` | Specialized wrapper for Slurm/HPC environments. |
| `setup_windows.ps1` | Environment provisioning script for Windows (WSL2/Conda). |
| `sim_tracker.py` | Live telemetry dashboard for monitoring active simulations. |

## Directory Structure

```text
scripts/
├── dev_benchmark.py              # Performance tests
├── dev_stability_test.py         # Physics correctness validations
├── health_check.py               # Pre-flight environment check
├── run_granite.py                # Main execution entrypoint
├── run_granite_hpc.py            # Slurm/Cluster job submission
├── setup_windows.ps1             # Windows bootstrap
├── sim_tracker.py                # Telemetry UI
└── README.md                     # You are here
```

> [!IMPORTANT]
> **Usage Rule:** The `run_granite.py` script must always be executed from the root of the repository, not from within this `scripts/` directory. 
> Example: `python3 scripts/run_granite.py build --release`
