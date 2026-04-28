#!/usr/bin/env python3
"""
GRANITE HPC Orchestration Tool
--------------------------------
Enterprise-grade CLI wrapper for building, running, testing, and formatting
the GRANITE numerical relativity engine.

Features:
  - MPI-aware simulation launcher with graceful Ctrl+C / zombie prevention
  - Structured colour-coded logging (INFO / WARNING / ERROR)
  - Version-aware preflight dependency validation
  - Full CMake flag passthrough
  - OMP / environment variable injection
  - --dry-run and --verbose global flags
  - clang-format-18 targeting
  - ctest integration

Usage:
  python scripts/run_granite.py [--verbose] [--dry-run] <command> [options]

Commands:
  build   [--build-type TYPE] [--cmake-flag K=V ...]
  run     --benchmark NAME [--mpi-ranks N] [--omp-threads N] [--env K=V ...]
  test    [--timeout S] [--filter REGEX]
  clean   [--build-dir PATH]
  format  [--check-only]
"""

import argparse
import logging
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Colour-coded logging
# ---------------------------------------------------------------------------
_RESET  = "\033[0m"
_BOLD   = "\033[1m"
_RED    = "\033[31m"
_GREEN  = "\033[32m"
_YELLOW = "\033[33m"
_CYAN   = "\033[36m"
_GREY   = "\033[90m"

_LEVEL_COLOURS = {
    logging.DEBUG:    _GREY,
    logging.INFO:     _GREEN,
    logging.WARNING:  _YELLOW,
    logging.ERROR:    _RED,
    logging.CRITICAL: _RED + _BOLD,
}


class _ColourFormatter(logging.Formatter):
    """Applies ANSI colour codes to log level names; degrades gracefully on
    non-TTY streams (CI pipes, SLURM logs)."""

    _USE_COLOUR = sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        ts      = self.formatTime(record, "%H:%M:%S")
        level   = record.levelname.ljust(8)
        message = record.getMessage()

        if self._USE_COLOUR:
            colour = _LEVEL_COLOURS.get(record.levelno, "")
            level_str  = f"{colour}{_BOLD}{level}{_RESET}"
            prefix_str = f"{_GREY}{ts}{_RESET}"
            tag_str    = f"{_CYAN}[GRANITE]{_RESET}"
        else:
            level_str  = level
            prefix_str = ts
            tag_str    = "[GRANITE]"

        return f"{prefix_str} {level_str} {tag_str} {message}"


def _configure_logging(verbose: bool) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_ColourFormatter())
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)


log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global dry-run flag (set after arg parsing)
# ---------------------------------------------------------------------------
_DRY_RUN = False


# ---------------------------------------------------------------------------
# Physical core detection
# ---------------------------------------------------------------------------
_FALLBACK_CORES = 4


def _detect_physical_cores() -> tuple[int, str]:
    """Return (physical_core_count, method) — never raises."""

    try:
        import psutil
        cores = psutil.cpu_count(logical=False)
        if cores and cores > 0:
            return cores, "psutil"
    except ImportError:
        pass

    try:
        cores = os.cpu_count(logical=False)  # type: ignore[call-arg]
        if cores and cores > 0:
            return cores, "os.cpu_count(logical=False)"
    except TypeError:
        pass

    try:
        plat = sys.platform
        if plat == "win32":
            r = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfCores -Sum).Sum"],
                capture_output=True, text=True, timeout=5,
            )
            cores = int(r.stdout.strip())
        elif plat == "darwin":
            r = subprocess.run(
                ["sysctl", "-n", "hw.physicalcpu"],
                capture_output=True, text=True, timeout=5,
            )
            cores = int(r.stdout.strip())
        else:
            r = subprocess.run(
                ["bash", "-c", "grep '^core id' /proc/cpuinfo | sort -u | wc -l"],
                capture_output=True, text=True, timeout=5,
            )
            cores = int(r.stdout.strip())

        if cores and cores > 0:
            return cores, f"shell({plat})"
    except Exception:
        pass

    return _FALLBACK_CORES, "fallback"


def _inject_omp(env: dict, omp_threads: Optional[int]) -> dict:
    """Inject OMP_NUM_THREADS / OMP_PROC_BIND / OMP_PLACES into env."""
    if omp_threads is not None:
        env["OMP_NUM_THREADS"] = str(omp_threads)
        log.info("OMP_NUM_THREADS forced to %d via --omp-threads", omp_threads)
    elif "OMP_NUM_THREADS" not in env:
        cores, method = _detect_physical_cores()
        env["OMP_NUM_THREADS"] = str(cores)
        env.setdefault("OMP_PROC_BIND", "true")
        env.setdefault("OMP_PLACES",    "cores")
        suffix = "  ⚠ detection failed — fallback" if "fallback" in method else f"  [{method}]"
        log.info("[HPC] Auto-set OMP_NUM_THREADS=%d%s", cores, suffix)
        log.info("[HPC] OMP_PROC_BIND=true  |  OMP_PLACES=cores")
    else:
        log.info("[HPC] OMP_NUM_THREADS already set to %s — skipping auto-config",
                 env["OMP_NUM_THREADS"])
    return env


# ---------------------------------------------------------------------------
# Preflight: version-aware dependency validation
# ---------------------------------------------------------------------------
_MIN_CMAKE = (3, 18)
_MIN_GCC   = (11, 0)
_MIN_CLANG = (14, 0)


def _parse_semver(raw: str) -> tuple[int, ...]:
    """Extract leading integers from a version string."""
    parts = re.findall(r"\d+", raw)
    return tuple(int(p) for p in parts[:3]) if parts else (0,)


def _check_tool(name: str, version_flag: str = "--version") -> Optional[str]:
    """Return raw version output, or None if the tool is absent."""
    exe = shutil.which(name)
    if exe is None:
        return None
    try:
        r = subprocess.run([name, version_flag], capture_output=True, text=True, timeout=10)
        return (r.stdout + r.stderr).strip().splitlines()[0]
    except Exception:
        return None


def _require_tool_version(name: str, raw: Optional[str],
                          minimum: tuple[int, ...], label: str) -> None:
    if raw is None:
        log.error("PREFLIGHT FAIL: '%s' not found in PATH. %s", name, label)
        sys.exit(2)
    got = _parse_semver(raw)
    if got < minimum:
        min_str = ".".join(str(x) for x in minimum)
        got_str = ".".join(str(x) for x in got)
        log.error("PREFLIGHT FAIL: %s requires >= %s, found %s", name, min_str, got_str)
        sys.exit(2)
    log.debug("PREFLIGHT OK: %s  [%s]", name, raw.split("\n")[0][:80])


def preflight_build() -> None:
    """Validate cmake and a usable C++ compiler before attempting a build."""
    log.info("Running preflight checks …")

    cmake_raw = _check_tool("cmake")
    _require_tool_version("cmake", cmake_raw, _MIN_CMAKE,
                          "Download from https://cmake.org/download/")

    # Accept gcc-12 / g++-12 or any gcc/g++
    for gcc in ("gcc-12", "gcc"):
        raw = _check_tool(gcc)
        if raw is not None:
            _require_tool_version(gcc, raw, _MIN_GCC, "Install GCC >= 11")
            break
    else:
        # Try clang
        for clang in ("clang-18", "clang-14", "clang"):
            raw = _check_tool(clang)
            if raw is not None:
                _require_tool_version(clang, raw, _MIN_CLANG, "Install Clang >= 14")
                break
        else:
            log.error("PREFLIGHT FAIL: No usable C++ compiler found (gcc >= 11 or clang >= 14)")
            sys.exit(2)

    log.info("Preflight checks passed.")


def preflight_run(mpi_ranks: int) -> None:
    """Validate MPI launcher availability when --mpi-ranks > 1."""
    if mpi_ranks > 1:
        for launcher in ("mpiexec", "mpirun", "srun"):
            if shutil.which(launcher) is not None:
                log.debug("MPI launcher: %s", launcher)
                return
        log.error(
            "PREFLIGHT FAIL: --mpi-ranks=%d requested but no MPI launcher "
            "(mpiexec/mpirun/srun) found in PATH.", mpi_ranks
        )
        sys.exit(2)


# ---------------------------------------------------------------------------
# Safe subprocess execution (Tier A)
# ---------------------------------------------------------------------------
_active_proc: Optional[subprocess.Popen] = None


def _sigint_handler(signum, frame):
    """Gracefully terminate the active child process on Ctrl+C.

    Prevents MPI zombie ranks on shared HPC clusters.
    """
    if _active_proc is not None:
        log.warning("KeyboardInterrupt received — terminating child process (PID %d) …",
                    _active_proc.pid)
        try:
            _active_proc.terminate()
            _active_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            log.warning("Child did not exit in 5 s — sending SIGKILL.")
            _active_proc.kill()
            _active_proc.wait()
        except Exception as exc:
            log.error("Error during child termination: %s", exc)
    log.error("Interrupted by user.")
    sys.exit(130)  # Standard SIGINT exit code


def _run(cmd: list[str], env: Optional[dict] = None,
         cwd: Optional[Path] = None) -> int:
    """Execute *cmd*, wiring Ctrl+C → graceful teardown.

    In --dry-run mode the command is logged but never executed.
    Returns the child process exit code.
    """
    global _active_proc

    cmd_str = " ".join(str(c) for c in cmd)
    if _DRY_RUN:
        log.info("[DRY-RUN] Would execute: %s", cmd_str)
        return 0

    log.debug("Executing: %s", cmd_str)

    old_handler = signal.signal(signal.SIGINT, _sigint_handler)
    try:
        _active_proc = subprocess.Popen(cmd, env=env, cwd=cwd)
        rc = _active_proc.wait()
        return rc
    finally:
        _active_proc = None
        signal.signal(signal.SIGINT, old_handler)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------

def cmd_build(args) -> None:
    preflight_build()

    build_dir = Path(args.build_dir)
    build_dir.mkdir(exist_ok=True)

    build_type = args.build_type
    log.info("Configuring CMake [%s] …", build_type)

    config_cmd = [
        "cmake", "-B", str(build_dir), "-S", ".",
        f"-DCMAKE_BUILD_TYPE={build_type}",
    ]

    # Passthrough custom -D flags
    for flag in (args.cmake_flag or []):
        if not flag.startswith("-D"):
            flag = f"-D{flag}"
        config_cmd.append(flag)
        log.debug("CMake flag: %s", flag)

    rc = _run(config_cmd)
    if rc != 0:
        log.error("CMake configuration failed (exit %d).", rc)
        sys.exit(rc)

    log.info("Building project …")
    build_cmd = ["cmake", "--build", str(build_dir), f"-j{os.cpu_count() or 4}"]
    rc = _run(build_cmd)
    if rc != 0:
        log.error("Build failed (exit %d).", rc)
        sys.exit(rc)

    log.info("Build successful.")


def cmd_run(args) -> None:
    mpi_ranks = args.mpi_ranks
    preflight_run(mpi_ranks)

    # --- Locate binary ---
    build_dir = Path(args.build_dir)
    suffix    = ".exe" if sys.platform == "win32" else ""
    candidates = [
        build_dir / "bin" / f"granite_main{suffix}",
        build_dir / "bin" / "Release" / f"granite_main{suffix}",
        build_dir / "Release" / f"granite_main{suffix}",
        build_dir / f"granite_main{suffix}",
    ]
    exe = next((c for c in candidates if c.exists()), None)
    if exe is None:
        log.error("Executable not found. Searched: %s",
                  ", ".join(str(c) for c in candidates))
        log.error("Run 'build' first.")
        sys.exit(1)

    # --- Locate benchmark / param file ---
    benchmark_dir = Path("benchmarks") / args.benchmark
    param_file    = benchmark_dir / "params.yaml"

    if not benchmark_dir.exists():
        log.error("Benchmark directory '%s' not found.", benchmark_dir)
        sys.exit(1)

    if not param_file.exists():
        log.warning("Param file '%s' not found — running with compiled defaults.", param_file)

    sim_cmd = [str(exe)]
    if param_file.exists():
        sim_cmd.append(str(param_file))

    # --- MPI prefix ---
    if mpi_ranks > 1:
        launcher = next(
            (x for x in ("mpiexec", "mpirun", "srun") if shutil.which(x)),
            None,
        )
        sim_cmd = [launcher, "-np", str(mpi_ranks)] + sim_cmd
        log.info("[MPI] Launching %d ranks via %s", mpi_ranks, launcher)

    # --- Environment ---
    sim_env = os.environ.copy()

    # Passthrough --env K=V pairs
    for kv in (args.env or []):
        if "=" not in kv:
            log.warning("--env '%s' ignored — expected KEY=VALUE format.", kv)
            continue
        k, v = kv.split("=", 1)
        sim_env[k] = v
        log.debug("ENV inject: %s=%s", k, v)

    sim_env = _inject_omp(sim_env, args.omp_threads)

    log.info("Launching simulation: %s", " ".join(sim_cmd))
    rc = _run(sim_cmd, env=sim_env)
    if rc != 0:
        log.error("Simulation exited with code %d.", rc)
    sys.exit(rc)


def cmd_test(args) -> None:
    build_dir = Path(args.build_dir)
    if not (build_dir / "CTestTestfile.cmake").exists():
        log.error("CTest files not found in '%s'. Run 'build' first.", build_dir)
        sys.exit(1)

    ctest_cmd = [
        "ctest",
        "--test-dir", str(build_dir),
        "--output-on-failure",
        f"--timeout", str(args.timeout),
    ]
    if args.filter:
        ctest_cmd += ["-R", args.filter]

    log.info("Running test suite …")
    rc = _run(ctest_cmd)
    if rc != 0:
        log.error("Tests failed (ctest exit %d).", rc)
    else:
        log.info("All tests passed.")
    sys.exit(rc)


def cmd_clean(args) -> None:
    build_dir = Path(args.build_dir)
    if not build_dir.exists():
        log.info("Nothing to clean (directory '%s' does not exist).", build_dir)
        return

    if _DRY_RUN:
        log.info("[DRY-RUN] Would remove: %s", build_dir)
        return

    log.info("Removing '%s' …", build_dir)
    try:
        shutil.rmtree(build_dir)
        log.info("Clean successful.")
    except PermissionError as exc:
        log.error("Permission denied while removing '%s': %s", build_dir, exc)
        log.error("On NFS/shared mounts, manual removal may be required.")
        sys.exit(1)
    except OSError as exc:
        log.error("Failed to remove '%s': %s", build_dir, exc)
        sys.exit(1)


def cmd_format(args) -> None:
    # Prefer clang-format-18; fall back to clang-format
    formatter = None
    for candidate in ("clang-format-18", "clang-format"):
        if shutil.which(candidate) is not None:
            formatter = candidate
            break

    if formatter is None:
        log.error("clang-format not found. Install clang-format-18.")
        sys.exit(2)

    # Warn if we're not on version 18
    raw = _check_tool(formatter)
    ver = _parse_semver(raw or "")
    if ver and ver[0] != 18:
        log.warning(
            "Found %s version %s — project targets version 18. "
            "Formatting may differ from CI.", formatter, ".".join(str(x) for x in ver[:2])
        )

    extensions     = ["*.cpp", "*.hpp", "*.c", "*.h"]
    dirs_to_format = [Path("src"), Path("include"), Path("tests")]

    files = [
        f
        for d in dirs_to_format if d.exists()
        for ext in extensions
        for f in d.rglob(ext)
    ]

    if not files:
        log.warning("No source files found to format.")
        return

    mode = "--dry-run --Werror" if args.check_only else "-i"
    log.info("%s %d files with %s …",
             "Checking" if args.check_only else "Formatting", len(files), formatter)

    flags = ["--dry-run", "--Werror"] if args.check_only else ["-i"]
    failed = []
    for f in files:
        rc = _run([formatter] + flags + [str(f)])
        if rc != 0:
            failed.append(f)

    if args.check_only and failed:
        log.error("%d file(s) need formatting:", len(failed))
        for f in failed:
            log.error("  %s", f)
        sys.exit(1)
    elif not args.check_only:
        log.info("Formatted %d file(s).", len(files))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add --build-dir to subparsers that need it."""
    parser.add_argument(
        "--build-dir", default="build", metavar="PATH",
        help="CMake build directory (default: build/)"
    )


def main() -> None:
    # ---- Top-level parser ----
    root = argparse.ArgumentParser(
        prog="run_granite.py",
        description="GRANITE HPC Orchestration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/run_granite.py build\n"
            "  python scripts/run_granite.py build --cmake-flag GRANITE_ENABLE_MPI=ON\n"
            "  python scripts/run_granite.py run --benchmark B2_eq --mpi-ranks 4\n"
            "  python scripts/run_granite.py run --benchmark single_puncture --omp-threads 8\n"
            "  python scripts/run_granite.py run --benchmark B2_eq --env HDF5_USE_FILE_LOCKING=FALSE\n"
            "  python scripts/run_granite.py test --filter smoke\n"
            "  python scripts/run_granite.py clean\n"
            "  python scripts/run_granite.py format\n"
            "  python scripts/run_granite.py --dry-run build\n"
        )
    )
    root.add_argument("--verbose", "-v", action="store_true",
                      help="Enable DEBUG-level logging")
    root.add_argument("--dry-run", "-n", action="store_true",
                      help="Print commands without executing them")

    subs = root.add_subparsers(dest="command", metavar="<command>")

    # ---- build ----
    p_build = subs.add_parser("build", help="Configure and compile with CMake")
    _add_common_args(p_build)
    p_build.add_argument("--build-type", default="Release",
                         choices=["Debug", "Release", "RelWithDebInfo", "MinSizeRel"],
                         help="CMake build type (default: Release)")
    p_build.add_argument("--cmake-flag", action="append", metavar="KEY=VALUE",
                         help="Pass a -D flag to CMake (repeatable). "
                              "E.g. --cmake-flag GRANITE_ENABLE_MPI=ON")

    # ---- run ----
    p_run = subs.add_parser("run", help="Launch a GRANITE simulation")
    _add_common_args(p_run)
    p_run.add_argument("--benchmark", required=True, metavar="NAME",
                       help="Benchmark directory name (e.g. B2_eq, single_puncture)")
    p_run.add_argument("--mpi-ranks", type=int, default=1, metavar="N",
                       help="Number of MPI ranks (default: 1 — no MPI launcher)")
    p_run.add_argument("--omp-threads", type=int, default=None, metavar="N",
                       help="Force OMP_NUM_THREADS (default: auto-detect physical cores)")
    p_run.add_argument("--env", action="append", metavar="KEY=VALUE",
                       help="Inject an environment variable (repeatable). "
                            "E.g. --env HDF5_USE_FILE_LOCKING=FALSE")

    # ---- test ----
    p_test = subs.add_parser("test", help="Run the test suite via ctest")
    _add_common_args(p_test)
    p_test.add_argument("--timeout", type=int, default=120, metavar="S",
                        help="Per-test timeout in seconds (default: 120)")
    p_test.add_argument("--filter", default=None, metavar="REGEX",
                        help="Only run tests matching this regex (passed to ctest -R)")

    # ---- clean ----
    p_clean = subs.add_parser("clean", help="Remove build artifacts")
    _add_common_args(p_clean)

    # ---- format ----
    p_fmt = subs.add_parser("format", help="Format C++ sources with clang-format-18")
    p_fmt.add_argument("--check-only", action="store_true",
                       help="Check formatting without modifying files (exits non-zero if needed)")

    args = root.parse_args()

    # Apply globals
    _configure_logging(args.verbose)

    global _DRY_RUN
    _DRY_RUN = args.dry_run
    if _DRY_RUN:
        log.info("[DRY-RUN] No commands will be executed.")

    # Dispatch
    dispatch = {
        "build":  cmd_build,
        "run":    cmd_run,
        "test":   cmd_test,
        "clean":  cmd_clean,
        "format": cmd_format,
    }

    if args.command not in dispatch:
        root.print_help()
        sys.exit(0)

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
