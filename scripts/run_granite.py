#!/usr/bin/env python3
"""
GRANITE Execution & Build Wrapper
-----------------------------------
Provides clean CLI commands for building, running, cleaning, and formatting
the GRANITE numerical relativity engine.

HPC Feature: Auto-detects physical core count and sets OMP_NUM_THREADS
             if not already present in the environment, ensuring peak
             CCZ4/GRMHD performance on any platform.
"""

import argparse
import os
import platform
import subprocess
import sys
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Physical core detection  (same logic as health_check.py — zero-failure)
# ---------------------------------------------------------------------------
_FALLBACK_CORES = 4


def _detect_physical_cores() -> tuple[int, str]:
    """Return (physical_core_count, method) — never raises."""

    # Method 1: psutil
    try:
        import psutil
        cores = psutil.cpu_count(logical=False)
        if cores and cores > 0:
            return cores, "psutil"
    except ImportError:
        pass

    # Method 2: Python 3.13+ os.cpu_count(logical=False)
    try:
        cores = os.cpu_count(logical=False)  # type: ignore[call-arg]
        if cores and cores > 0:
            return cores, "os.cpu_count(logical=False)"
    except TypeError:
        pass

    # Method 3: Platform shell commands
    try:
        plat = sys.platform
        if plat == "win32":
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum"],
                capture_output=True, text=True, timeout=5
            )
            cores = int(result.stdout.strip())
        elif plat == "darwin":
            result = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True, text=True, timeout=5
            )
            cores = int(result.stdout.strip())
        else:  # Linux / WSL2
            result = subprocess.run(
                ["bash", "-c",
                 "grep '^core id' /proc/cpuinfo | sort -u | wc -l"],
                capture_output=True, text=True, timeout=5
            )
            cores = int(result.stdout.strip())

        if cores and cores > 0:
            return cores, f"shell ({plat})"
    except Exception:
        pass

    return _FALLBACK_CORES, f"fallback (detection failed — defaulting to {_FALLBACK_CORES})"


def _ensure_omp_threads(env: dict) -> dict:
    """
    If OMP_NUM_THREADS is absent, detect physical cores, inject it into
    the supplied env dict, and print an [HPC] advisory. Returns the env dict.
    """
    if "OMP_NUM_THREADS" not in env:
        cores, method = _detect_physical_cores()
        env["OMP_NUM_THREADS"] = str(cores)
        env.setdefault("OMP_PROC_BIND", "true")
        env.setdefault("OMP_PLACES",    "cores")

        warn_suffix = ""
        if "fallback" in method:
            warn_suffix = "  ⚠ (fallback — could not query hardware)"

        print(
            f"\n[HPC] Auto-setting OMP_NUM_THREADS to {cores} (Physical Core Count) "
            f"for peak performance.{warn_suffix}"
        )
        print(
            f"[HPC] Method: {method}  |  "
            f"OMP_PROC_BIND=true  |  OMP_PLACES=cores\n"
        )
    else:
        print(f"[HPC] OMP_NUM_THREADS already set to {env['OMP_NUM_THREADS']} — skipping auto-config.")

    return env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def check_command(cmd: str):
    if shutil.which(cmd) is None:
        print(f"Error: '{cmd}' is not installed or not available in PATH.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------
def build(args):
    check_command("cmake")
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    print("Configuring with CMake...")
    config_cmd = ["cmake", "-B", "build", "-S", ".", "-DCMAKE_BUILD_TYPE=Release"]
    result = subprocess.run(config_cmd)
    if result.returncode != 0:
        print("CMake configuration failed.")
        sys.exit(result.returncode)

    print("Building project...")
    build_cmd = ["cmake", "--build", "build", "-j"]
    result = subprocess.run(build_cmd)
    if result.returncode != 0:
        print("Build failed.")
        sys.exit(result.returncode)

    print("Build successful!")


def run_sim(args):
    # Locate the compiled binary
    if sys.platform == "win32":
        candidates = [
            Path("build/bin/granite_main.exe"),
            Path("build/bin/Release/granite_main.exe"),
            Path("build/Release/granite_main.exe"),
            Path("build/granite_main.exe"),
        ]
    else:
        candidates = [
            Path("build/bin/granite_main"),
            Path("build/granite_main"),
        ]

    exe_path = next((c for c in candidates if c.exists()), None)
    if exe_path is None:
        searched = ", ".join(str(c) for c in candidates)
        print(f"Error: Executable not found. Searched: {searched}")
        print("Did you run 'build' first?")
        sys.exit(1)

    # Resolve benchmark / param file
    benchmark_dir = Path("benchmarks") / args.benchmark
    param_file    = benchmark_dir / "params.yaml"

    if not benchmark_dir.exists():
        print(f"Error: Benchmark directory '{benchmark_dir}' not found.")
        sys.exit(1)

    cmd = [str(exe_path), str(param_file)] if param_file.exists() else [str(exe_path)]
    if not param_file.exists():
        print(f"Warning: Param file '{param_file}' not found. Running with defaults.")

    # --- HPC: auto-inject OMP_NUM_THREADS if missing ---
    sim_env = os.environ.copy()
    sim_env = _ensure_omp_threads(sim_env)

    print(f"Running simulation: {' '.join(cmd)}")
    subprocess.run(cmd, env=sim_env)


def clean(args):
    build_dir = Path("build")
    if build_dir.exists():
        print("Removing build directory...")
        shutil.rmtree(build_dir, ignore_errors=True)
        print("Clean successful.")
    else:
        print("Nothing to clean.")


def format_code(args):
    try:
        check_command("clang-format")
    except SystemExit:
        print("clang-format not found. Cannot format codebase.")
        return

    print("Formatting C++ codebase...")
    extensions    = ["*.cpp", "*.hpp", "*.c", "*.h"]
    dirs_to_format = [Path("src"), Path("include"), Path("tests")]

    files_to_format = [
        f
        for d in dirs_to_format if d.exists()
        for ext in extensions
        for f in d.rglob(ext)
    ]

    if not files_to_format:
        print("No source files found to format.")
        return

    for f in files_to_format:
        subprocess.run(["clang-format", "-i", "-style=file", str(f)])
    print(f"Formatted {len(files_to_format)} files.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="GRANITE Execution & Build Wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/run_granite.py build\n"
            "  python scripts/run_granite.py run --benchmark B2_eq\n"
            "  python scripts/run_granite.py run --benchmark single_puncture\n"
            "  python scripts/run_granite.py clean\n"
            "  python scripts/run_granite.py format\n"
        )
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("build",  help="Build the GRANITE project using CMake")

    run_parser = subparsers.add_parser("run", help="Run a GRANITE simulation benchmark")
    run_parser.add_argument(
        "--benchmark", type=str, required=True,
        help="Name of the benchmark directory (e.g., B2_eq, single_puncture)"
    )

    subparsers.add_parser("clean",  help="Remove build artifacts")
    subparsers.add_parser("format", help="Format the codebase using clang-format")

    args = parser.parse_args()

    if   args.command == "build":   build(args)
    elif args.command == "run":     run_sim(args)
    elif args.command == "clean":   clean(args)
    elif args.command == "format":  format_code(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
