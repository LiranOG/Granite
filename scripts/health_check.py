import os
import sys
import argparse
from pathlib import Path

# Terminal coloring codes
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_header():
    print(f"\n{Colors.BOLD}{Colors.CYAN}=================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}       GRANITE Diagnostics & Health Check         {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}=================================================={Colors.RESET}")

def report(issue, status, ok=True):
    color = Colors.GREEN if ok else Colors.RED
    icon = "[OK]" if ok else "[FAIL]"
    
    # If it's a warning rather than a fail, we check 'ok' value and color overrides
    if status == "WARNING":
        color = Colors.YELLOW
        icon = "[WARN]"
        
    print(f" {Colors.BOLD}{issue.ljust(35)}{Colors.RESET} {color}{icon} {status}{Colors.RESET}")

def check_openmp():
    # Hardware validation
    hw_cores = os.cpu_count()
    env_cores = os.environ.get("OMP_NUM_THREADS", "NOT_SET")
    
    report("System Logical Cores", f"{hw_cores} detected", ok=True)
    
    if env_cores == "NOT_SET":
        report("OMP_NUM_THREADS", "WARNING: Not explicitly set (OS default)", ok=False)
        print(f"\n   {Colors.YELLOW}>> Tip: Set OMP_NUM_THREADS={hw_cores} to guarantee thread saturation.{Colors.RESET}")
    else:
        try:
            if int(env_cores) < hw_cores:
                report("OMP_NUM_THREADS", f"WARNING: Set to {env_cores} (Under-saturating {hw_cores} cores)", ok=False)
            elif int(env_cores) == hw_cores:
                report("OMP_NUM_THREADS", f"{env_cores} (Perfect Hardware Match)", ok=True)
            else:
                report("OMP_NUM_THREADS", f"WARNING: Over-saturation ({env_cores} > {hw_cores})", ok=False)
        except ValueError:
             report("OMP_NUM_THREADS", f"WARNING: Invalid format ({env_cores})", ok=False)
             
def scan_cmake_cache():
    cache_path = Path("build/CMakeCache.txt")
    if not cache_path.exists():
         print(f"\n{Colors.RED}❌ ERROR: CMakeCache.txt not found in build/. Have you compiled the engine?{Colors.RESET}")
         sys.exit(1)
         
    print(f"\n{Colors.BOLD}--- Compiling Flags & Pipeline ---{Colors.RESET}")
    
    with open(cache_path, "r") as f:
        content = f.read()
        
    lines = content.splitlines()
    
    build_type = "UNKNOWN"
    mpi = False
    openmp = False
    cxx_flags = ""
    compiler = "UNKNOWN"
    
    for line in lines:
        if line.startswith("CMAKE_BUILD_TYPE:STRING="):
            build_type = line.split("=")[1].strip()
        elif line.startswith("GRANITE_ENABLE_MPI:BOOL="):
            mpi = line.split("=")[1].strip() == "ON"
        elif line.startswith("GRANITE_ENABLE_OPENMP:BOOL="):
            openmp = line.split("=")[1].strip() == "ON"
        elif line.startswith("CMAKE_CXX_FLAGS_RELEASE:STRING="):
            cxx_flags = line.split("=")[1].strip()
        elif line.startswith("CMAKE_CXX_COMPILER_ID:STRING="):
             compiler = line.split("=")[1].strip()
             
    # Evaluate Build Type
    if build_type.upper() == "RELEASE":
         report("CMAKE_BUILD_TYPE", "Release (Maximum Power)", ok=True)
    elif build_type.upper() == "DEBUG":
         report("CMAKE_BUILD_TYPE", "Debug (Extremely Slow)", ok=False)
         print(f"   {Colors.RED}>> FATAL: Debug builds are ~40x slower. Rebuild with -DCMAKE_BUILD_TYPE=Release!{Colors.RESET}")
    else:
         report("CMAKE_BUILD_TYPE", build_type, ok=False)

    # Evaluate Compiler & Flags
    report("C++ Compiler Engine", compiler, ok=True)
    
    # Identify non-optimal missing flags based on compiler
    if compiler == "MSVC":
         if "/arch:AVX2" not in cxx_flags and "/O2" not in cxx_flags:
              report("MSVC Release Flags", f"Sub-optimal ({cxx_flags})", ok=False)
         else:
              report("MSVC Release Flags", "AVX2 & Rapid Inlining detected", ok=True)
    elif compiler in ["GNU", "Clang", "AppleClang"]:
         if "-march=native" not in cxx_flags and "-O3" not in cxx_flags:
              report("GNU/Clang Release Flags", f"Sub-optimal ({cxx_flags})", ok=False)
         else:
              report("GNU/Clang Release Flags", "Architecture tuning (-march) detected", ok=True)
              
    # Evaluate MPI and OpenMP
    print(f"\n{Colors.BOLD}--- Hardware Acceleration Linking ---{Colors.RESET}")
    if openmp:
         report("OpenMP Linkage", "Enabled in CMake", ok=True)
    else:
         report("OpenMP Linkage", "Disabled / Failed to Link", ok=False)
         
    if mpi:
         report("MPI Multi-Node Linkage", "Enabled in CMake", ok=True)
    else:
         report("MPI Multi-Node Linkage", "Disabled", ok=True) # It's okay if they don't have MPI

def main():
    print_header()
    
    print(f"{Colors.BOLD}--- Thread Saturation Analysis ---{Colors.RESET}")
    check_openmp()
    
    scan_cmake_cache()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}=================================================={Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}   Health Check Complete. Consult Output          {Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}=================================================={Colors.RESET}\n")

if __name__ == '__main__':
    main()
