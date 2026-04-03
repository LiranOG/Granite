# =============================================================================
# GRANITE — General-Relativistic Adaptive N-body Integrated Tool
#            for Extreme Astrophysics
#
# Top-level CMake configuration
# =============================================================================
cmake_minimum_required(VERSION 3.20)

project(GRANITE
    VERSION 0.6.0
    DESCRIPTION "General-Relativistic Adaptive N-body Integrated Tool for Extreme Astrophysics"
    HOMEPAGE_URL "https://github.com/LiranOG/Granite"
    LANGUAGES CXX
)

# ---------------------------------------------------------------------------
# Build options
# ---------------------------------------------------------------------------
option(GRANITE_ENABLE_MPI      "Enable MPI parallelism"                   ON)
option(GRANITE_ENABLE_OPENMP   "Enable OpenMP threading"                  ON)
option(GRANITE_ENABLE_GPU      "Enable GPU acceleration (CUDA/HIP)"       OFF)
option(GRANITE_GPU_BACKEND     "GPU backend: CUDA or HIP"                 "CUDA")
option(GRANITE_ENABLE_HDF5     "Enable HDF5 I/O"                          ON)
option(GRANITE_ENABLE_PETSC    "Enable PETSc for elliptic solvers"         OFF)
option(GRANITE_ENABLE_TESTS    "Build unit and integration tests"          ON)
option(GRANITE_ENABLE_DOCS     "Build documentation"                       OFF)
option(GRANITE_ENABLE_PYTHON   "Install Python analysis package"           OFF)
option(GRANITE_DOUBLE_PRECISION "Use double precision (always true for NR)" ON)

# ---------------------------------------------------------------------------
# C++ standard
# ---------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ---------------------------------------------------------------------------
# Build type defaults
# ---------------------------------------------------------------------------
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Build type" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
        "Debug" "Release" "RelWithDebInfo" "MinSizeRel")
endif()

# ------------------------------------------------------------
# Compiler flags
# ------------------------------------------------------------
if(MSVC)
    set(GRANITE_WARNING_FLAGS "/W4 /wd4100 /wd4127 /wd4505")
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    set(GRANITE_WARNING_FLAGS "-Wall -Wextra -Wpedantic -Wshadow -Wconversion")
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${GRANITE_WARNING_FLAGS}")

if(MSVC)
    set(CMAKE_CXX_FLAGS_DEBUG "/Zi /Od /DGRANITE_DEBUG")
    set(CMAKE_CXX_FLAGS_RELEASE "/O2 /Ob2 /arch:AVX2 /fp:fast /MT /DNDEBUG")
else()
    set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -DGRANITE_DEBUG")
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native -ffast-math")
    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG")
endif()

# ---------------------------------------------------------------------------
# Output directories
# ---------------------------------------------------------------------------
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# ---------------------------------------------------------------------------
# Find required and optional dependencies
# ---------------------------------------------------------------------------

# WINDOWS NATIVE HINT:
# If compiling natively on Windows with MSVC, use vcpkg to install dependencies.
# Run cmake with -DCMAKE_TOOLCHAIN_FILE=[path_to_vcpkg]/scripts/buildsystems/vcpkg.cmake
# so that HDF5, MPI, and YAML-CPP are found natively.

# MPI
if(GRANITE_ENABLE_MPI)
    find_package(MPI REQUIRED COMPONENTS CXX)
    add_definitions(-DGRANITE_USE_MPI)
    message(STATUS "MPI enabled: ${MPI_CXX_COMPILER}")
endif()

# OpenMP
if(GRANITE_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED COMPONENTS CXX)
    add_definitions(-DGRANITE_USE_OPENMP)
    message(STATUS "OpenMP enabled: version ${OpenMP_CXX_VERSION}")
endif()

# GPU (CUDA or HIP)
if(GRANITE_ENABLE_GPU)
    if(GRANITE_GPU_BACKEND STREQUAL "CUDA")
        enable_language(CUDA)
        find_package(CUDAToolkit REQUIRED)
        add_definitions(-DGRANITE_USE_CUDA)
        set(CMAKE_CUDA_STANDARD 17)
        set(CMAKE_CUDA_ARCHITECTURES "70;80;90")
        message(STATUS "CUDA enabled: ${CUDAToolkit_VERSION}")
    elseif(GRANITE_GPU_BACKEND STREQUAL "HIP")
        find_package(hip REQUIRED)
        add_definitions(-DGRANITE_USE_HIP)
        message(STATUS "HIP enabled")
    else()
        message(FATAL_ERROR "Unknown GPU backend: ${GRANITE_GPU_BACKEND}")
    endif()
endif()

# HDF5
if(GRANITE_ENABLE_HDF5)
    set(HDF5_PREFER_PARALLEL TRUE)
    find_package(HDF5 REQUIRED COMPONENTS C CXX)
    add_definitions(-DGRANITE_USE_HDF5)
    message(STATUS "HDF5 enabled: ${HDF5_VERSION} (parallel: ${HDF5_IS_PARALLEL})")
endif()

# PETSc (for elliptic solvers)
if(GRANITE_ENABLE_PETSC)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(PETSC REQUIRED IMPORTED_TARGET PETSc)
    add_definitions(-DGRANITE_USE_PETSC)
    message(STATUS "PETSc enabled: ${PETSC_VERSION}")
endif()

# yaml-cpp (Required for parameter parsing)
# Prefer a system-installed yaml-cpp (e.g. from apt/Homebrew/conda) to avoid
# a slow network fetch during CI. Fall back to FetchContent only if not found.
find_package(yaml-cpp QUIET)
if(NOT yaml-cpp_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        yaml-cpp
        GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
        GIT_TAG        0.8.0
    )
    set(YAML_CPP_BUILD_TESTS   OFF CACHE BOOL "Disable yaml-cpp tests"   FORCE)
    set(YAML_CPP_BUILD_TOOLS   OFF CACHE BOOL "Disable yaml-cpp tools"   FORCE)
    set(YAML_CPP_BUILD_CONTRIB OFF CACHE BOOL "Disable yaml-cpp contrib" FORCE)
    FetchContent_MakeAvailable(yaml-cpp)
    message(STATUS "yaml-cpp: using FetchContent (system package not found)")
else()
    message(STATUS "yaml-cpp: using system installation (${yaml-cpp_VERSION})")
endif()

# ---------------------------------------------------------------------------
# Include directories
# ---------------------------------------------------------------------------
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/src
)

# ---------------------------------------------------------------------------
# Collect all source modules into a static library
# ---------------------------------------------------------------------------
# Core infrastructure
file(GLOB_RECURSE CORE_SOURCES       src/core/*.cpp)
file(GLOB_RECURSE SPACETIME_SOURCES  src/spacetime/*.cpp)
file(GLOB_RECURSE GRMHD_SOURCES     src/grmhd/*.cpp)
file(GLOB_RECURSE RADIATION_SOURCES  src/radiation/*.cpp)
file(GLOB_RECURSE NEUTRINO_SOURCES   src/neutrino/*.cpp)
file(GLOB_RECURSE AMR_SOURCES        src/amr/*.cpp)
file(GLOB_RECURSE INITIAL_SOURCES    src/initial_data/*.cpp)
file(GLOB_RECURSE HORIZON_SOURCES    src/horizon/*.cpp)
file(GLOB_RECURSE IO_SOURCES         src/io/*.cpp)
file(GLOB_RECURSE POSTPROC_SOURCES   src/postprocess/*.cpp)

add_library(granite_lib STATIC
    ${CORE_SOURCES}
    ${SPACETIME_SOURCES}
    ${GRMHD_SOURCES}
    ${RADIATION_SOURCES}
    ${NEUTRINO_SOURCES}
    ${AMR_SOURCES}
    ${INITIAL_SOURCES}
    ${HORIZON_SOURCES}
    ${IO_SOURCES}
    ${POSTPROC_SOURCES}
)

target_include_directories(granite_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Link dependencies
if(GRANITE_ENABLE_MPI)
    target_link_libraries(granite_lib PUBLIC MPI::MPI_CXX)
endif()
if(GRANITE_ENABLE_OPENMP)
    target_link_libraries(granite_lib PUBLIC OpenMP::OpenMP_CXX)
endif()
if(GRANITE_ENABLE_HDF5)
    target_link_libraries(granite_lib PUBLIC ${HDF5_LIBRARIES})
    target_include_directories(granite_lib PUBLIC ${HDF5_INCLUDE_DIRS})
endif()
if(GRANITE_ENABLE_PETSC)
    target_link_libraries(granite_lib PUBLIC PkgConfig::PETSC)
endif()
target_link_libraries(granite_lib PUBLIC yaml-cpp::yaml-cpp)

# ---------------------------------------------------------------------------
# Main executable
# ---------------------------------------------------------------------------
add_executable(granite_main src/main.cpp)
target_link_libraries(granite_main PRIVATE granite_lib)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if(GRANITE_ENABLE_TESTS)
    enable_testing()
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG        v1.14.0
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
    include(GoogleTest)
    add_subdirectory(tests)
endif()

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------
install(TARGETS granite_main granite_lib
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(DIRECTORY include/granite DESTINATION include)
install(DIRECTORY benchmarks DESTINATION share/granite)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
message(STATUS "")
message(STATUS "=== GRANITE Build Configuration ===")
message(STATUS "  Version:          ${PROJECT_VERSION}")
message(STATUS "  Build type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ compiler:     ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  MPI:              ${GRANITE_ENABLE_MPI}")
message(STATUS "  OpenMP:           ${GRANITE_ENABLE_OPENMP}")
message(STATUS "  GPU:              ${GRANITE_ENABLE_GPU} (${GRANITE_GPU_BACKEND})")
message(STATUS "  HDF5:             ${GRANITE_ENABLE_HDF5}")
message(STATUS "  PETSc:            ${GRANITE_ENABLE_PETSC}")
message(STATUS "  Tests:            ${GRANITE_ENABLE_TESTS}")
message(STATUS "  Double precision: ${GRANITE_DOUBLE_PRECISION}")
message(STATUS "===================================")
message(STATUS "")
