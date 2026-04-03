# 🚀 GRANITE Quick-Run Guide (v0.6.0)

> This is a streamlined cheat-sheet for deploying GRANITE. If you encounter errors, please consult the complete technical guide: [`docs/INSTALL.md`](docs/INSTALL.md)

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
