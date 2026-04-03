# 🔥 Universal Deployment & Performance Optimization

This guide outlines the professional "Maximum Power" protocols for deploying the GRANITE numerical relativity engine. The engine uses massive dense grid computations natively, making compiler optimization thresholds and thread saturation mission-critical.

---

## 1. The "Maximum Power" Build Protocol

We enforce stringent Release flags on all compilers. If you build using the standard CLI instructions, `CMakeLists.txt` automatically triggers the following flags:

### 🪟 Windows Native (MSVC / cl.exe)
If compiling via Visual Studio Build Tools, we force:
- `/O2`: Aggressive overarching optimization.
- `/Ob2`: Maximum function inlining (drastically improves CCZ4 inner loop speed).
- `/arch:AVX2`: Forces the compiler to emit Advanced Vector Extensions instructions natively supported by modern CPUs.
- `/fp:fast`: Overrides standard IEEE 754 precision to allow algebraic simplifications in heavily-nested floating point code, massively boosting speed.

**Native MSVC Checkpoint:** Ensure you are running CMake from a "Developer Command Prompt for VS 2022" or passing the correct architecture flag to `vcvars64.bat`. 

### 🐧 Linux / macOS (GCC / Apple Clang)
If compiling via WSL2, Ubuntu, Fedora, or Homebrew, we force:
- `-O3`: Aggressive loop vectorization and optimization.
- `-march=native`: Extremely powerful flag that tunes GCC directly to the physical silicon architecture running the build (e.g. AVX-512). *Warning: The resulting binary cannot be shared directly with an older machine!*
- `-ffast-math`: Disables strict NaN propagation and algebraic safety to maximize FMA (Fused Multiply Accumulate) pipelines.

---

## 2. Hardware Validation (OpenMP Thread Saturation)

By default, GRANITE utilizes OpenMP to parallelize the RK3 time integration and CCZ4 spatial derivatives across all available physical and logical cores.

### How to check thread saturation:

1. Look closely at the terminal output when running a simulation.
2. The initial log will output: `[OpenMP] Allocated N threads for AMR subcycling.`
3. If `N` does not match your total CPU cores (`os.cpu_count()`), you have a saturation failure.

### Resolving Saturation Bottlenecks

OpenMP limits are heavily influenced by your session environment variables. To force saturation, execute the following before running the Python script:

**Linux / WSL2 / macOS (Bash):**
```bash
export OMP_NUM_THREADS=$(nproc)
export OMP_PROC_BIND=true
export OMP_PLACES=cores
```

**Windows (PowerShell):**
```powershell
$env:OMP_NUM_THREADS = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$env:OMP_PROC_BIND = "true"
$env:OMP_PLACES = "cores"
```

*Note: `OMP_PROC_BIND=true` prevents the OS from migrating threads between cores, which drastically improves cache coherency on L3/L2 caches when processing massive `GridBlock` vectors.*

---

## 3. Diagnostic Health Check 

If your simulation is running slow, immediately run the included diagnostic tool:

```bash
python scripts/health_check.py
```

This Python script performs a post-build forensic analysis:
1. **Cache Inspection:** It reads `build/CMakeCache.txt`.
2. **Build Type:** It alerts you if `-DCMAKE_BUILD_TYPE=Debug` sneaked into your build (which results in a 40x speed penalty).
3. **OpenMP Linkage:** It validates whether `find_package(OpenMP ...)` successfully routed to your compiler's threaded backend.
4. **Hardware Validation:** It cross-references your physical logical cores with the OpenMP environmental allocations.

---

## 4. Cross-Platform Execution Cheat-Sheet

Once correctly built, simulate anywhere exactly the same way:

| Goal | Command (Bash - Linux/Mac) | Command (PowerShell - Windows) |
| --- | --- | --- |
| **Diagnostic Mode (Dev)** | `python3 scripts/dev_benchmark.py` | `python scripts/dev_benchmark.py` |
| **Live Tracking (Verbose)**| `python3 scripts/dev_benchmark.py --verbose` | `python scripts/dev_benchmark.py --verbose` |
| **Long-Term Run (50M)** | `python3 scripts/dev_stability_test.py` | `python scripts/dev_stability_test.py` |
| **Clean Output** | `python3 scripts/run_granite.py clean` | `python scripts/run_granite.py clean` |
