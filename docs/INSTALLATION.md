## A Note from the Developer: Supported Platforms

Welcome to GRANITE. This project was born from a simple but overwhelming ambition: to simulate the unimaginable. I wanted to build an engine capable of modeling scenarios that still feel like science fiction—multiple supermassive black holes merging, tearing through stars, and interacting with extreme matter, all happening simultaneously. Currently, existing engines struggle to couple all these physics (CCZ4 spacetime evolution, GRMHD, and Adaptive Mesh Refinement) without collapsing under the computational weight. My goal is to build the architecture that finally solves this.

But here is the reality: I am currently building, optimizing, and debugging this entirely alone.

Making all these complex engines communicate perfectly, optimizing OpenMP threads to balance the load, and managing AMR grids so they don't crash the hardware takes an immense amount of time and energy. Because my focus must remain 100% on the physics, the math, and the engine's stability, I have to make a hard choice regarding deployment.

**Currently, native Windows (CMD/PowerShell) and macOS are STRICTLY UNSUPPORTED.**
Trying to troubleshoot package managers, compilers, and terminal quirks across every operating system is draining resources I simply do not have right now. To run GRANITE, **you must use Linux or Windows Subsystem for Linux (WSL2)**. The engine is optimized for environments where dependencies are natively supported, allowing you to bypass installation headaches and focus on the science.

My promise to you: In the future, once the core engine is flawless and perfectly optimized, I will dedicate the time to make GRANITE a true plug-and-play experience across every operating system, terminal, and platform.

Until then, I am asking for your help.
To the scientific community, physicists, and HPC administrators: The foundational math and architecture are here, but transforming this into a universally trusted scientific instrument requires more than one pair of hands. I warmly invite you to review the code, test it on your clusters, point out the flaws, and submit PRs. Let's look past the current rough edges and build the ultimate open-source engine for extreme astrophysics together.

---

# 🚀 GRANITE Quick-Run Guide (v0.6.5)

> This is a streamlined cheat-sheet for deploying GRANITE on **Linux or WSL2 only**. If you encounter errors, please consult the complete technical guide: [`docs/INSTALL.md`](https://github.com/LiranOG/Granite/blob/main/docs/INSTALL.md)

---

## 1️⃣ Clone the Repository
```bash
git clone https://github.com/LiranOG/Granite.git
cd Granite
```

## 2️⃣ Install Dependencies & Build

Choose the command block for your environment.

### 🐧 Ubuntu / Debian / WSL2 (Recommended)
```bash
sudo apt update && sudo apt install -y build-essential cmake libhdf5-dev libopenmpi-dev libyaml-cpp-dev
python3 scripts/run_granite.py build
```

### 🍎 macOS (Homebrew)
```bash
brew install cmake hdf5 open-mpi yaml-cpp
python3 scripts/run_granite.py build
```

### 🐍 Windows (Miniforge / Conda)
*Requires Visual Studio Build Tools to be installed separately.*
```bash
conda install -c conda-forge cmake hdf5 openmpi yaml-cpp
python scripts/run_granite.py build
```

### 🪟 Windows (Native PowerShell / CMD)
*Requires `git`, `cmake`, `python`, and Visual Studio Build Tools.*
```powershell
# Go up one directory to clone vcpkg alongside Granite
cd ..
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install hdf5 mpi yaml-cpp
cd ..\Granite
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE="../vcpkg/scripts/buildsystems/vcpkg.cmake" -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

---

## 3️⃣ Verify the Build

Run the integrated Developer Benchmark tests to ensure your engine is stable and tracking constraints properly.

```bash
# Pre-Flight Diagnostic (Health Check)
python3 scripts/health_check.py

# General validation
python3 scripts/dev_benchmark.py

# Complete test suite (92 tests)
build/bin/granite_tests
```

> **Windows Users:** use `python` instead of `python3`, and ensure executable tests are run via `.\build\bin\Release\granite_tests.exe` (MSVC Native) or `.\build\bin\granite_tests.exe` (Conda).
