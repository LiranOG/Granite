#!/usr/bin/env python3
import argparse
import subprocess
import sys
import shutil
from pathlib import Path

def check_command(cmd):
    if shutil.which(cmd) is None:
        print(f"Error: '{cmd}' is not installed or not available in PATH.")
        sys.exit(1)

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
    # CMakeLists.txt sets CMAKE_RUNTIME_OUTPUT_DIRECTORY to build/bin/
    # Try all known locations in order of likelihood
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

    exe_path = None
    for candidate in candidates:
        if candidate.exists():
            exe_path = candidate
            break

    if exe_path is None:
        # Show all locations we searched so the user knows exactly what happened
        searched = ", ".join(str(c) for c in candidates)
        print(f"Error: Executable not found. Searched: {searched}")
        print("Did you run 'build' first?")
        sys.exit(1)

    benchmark_dir = Path("benchmarks") / args.benchmark
    param_file = benchmark_dir / "params.yaml"
    
    if not benchmark_dir.exists():
        print(f"Error: Benchmark directory '{benchmark_dir}' not found.")
        sys.exit(1)
        
    if not param_file.exists():
        print(f"Warning: Param file '{param_file}' not found. Running with defaults.")
        cmd = [str(exe_path)]
    else:
        cmd = [str(exe_path), str(param_file)]
        
    print(f"Running simulation: {' '.join(cmd)}")
    subprocess.run(cmd)

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
    extensions = ["*.cpp", "*.hpp", "*.c", "*.h"]
    dirs_to_format = [Path("src"), Path("include"), Path("tests")]
    
    files_to_format = []
    for d in dirs_to_format:
        if d.exists():
            for ext in extensions:
                files_to_format.extend(list(d.rglob(ext)))
                
    if not files_to_format:
        print("No source files found to format.")
        return
        
    for f in files_to_format:
        subprocess.run(["clang-format", "-i", "-style=file", str(f)])
    print(f"Formatted {len(files_to_format)} files.")

def main():
    parser = argparse.ArgumentParser(description="GRANITE Execution and Build Script")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build parser
    build_parser = subparsers.add_parser("build", help="Build the GRANITE project using CMake")
    
    # Run parser
    run_parser = subparsers.add_parser("run", help="Run a GRANITE simulation benchmark")
    run_parser.add_argument("--benchmark", type=str, required=True, help="Name of the benchmark (e.g., single_puncture)")
    
    # Clean parser
    clean_parser = subparsers.add_parser("clean", help="Clean up build artifacts")
    
    # Format parser
    format_parser = subparsers.add_parser("format", help="Format the codebase using clang-format")
    
    args = parser.parse_args()
    
    if args.command == "build":
        build(args)
    elif args.command == "run":
        run_sim(args)
    elif args.command == "clean":
        clean(args)
    elif args.command == "format":
        format_code(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
