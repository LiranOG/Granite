Installation Guide
==================

This guide walks you through every step required to install **GRANITE**
on your platform — from cloning the repository to running your first benchmark.

.. contents:: On This Page
   :local:
   :depth: 2

----

Prerequisites
-------------

The table below lists **all required and optional dependencies** before building.

.. list-table:: Required Dependencies
   :widths: 25 20 55
   :header-rows: 1

   * - Tool
     - Minimum Version
     - Purpose
   * - **Git**
     - 2.30+
     - Clone the repository
   * - **Python**
     - 3.10+
     - Run ``run_granite.py`` and analysis scripts
   * - **CMake**
     - 3.20+
     - Configure and compile the C++ engine
   * - **C++17 Compiler**
     - GCC 12+ / Clang 15+ / MSVC 2022+
     - Build the simulation binary
   * - **HDF5** (dev headers, parallel)
     - 1.12+
     - Parallel I/O for simulation checkpoints
   * - **OpenMPI** (dev headers)
     - 4.0+
     - Multi-rank distributed-memory parallelism
   * - **OpenMP**
     - (bundled with compiler)
     - Shared-memory threading within each rank

.. list-table:: Optional Dependencies
   :widths: 25 20 55
   :header-rows: 1

   * - Tool
     - Minimum Version
     - Purpose
   * - **CUDA Toolkit**
     - 12.0+
     - NVIDIA GPU acceleration
   * - **ROCm / HIP**
     - 5.0+
     - AMD GPU acceleration
   * - **PETSc**
     - 3.18+
     - Elliptic solvers (initial data / constraint damping)
   * - **clang-format**
     - 15+
     - Auto-format C++ source (``scripts/run_granite.py format``)
   * - **Sphinx + breathe**
     - 7.0+ / 4.35+
     - Build this documentation locally

.. important::

   **yaml-cpp** is fetched automatically via CMake ``FetchContent`` — you do **not**
   need to install it by hand.  Google Test is also fetched automatically when
   ``GRANITE_ENABLE_TESTS=ON`` (the default).

----

Quick-Start (TL;DR)
-------------------

For users on Ubuntu / WSL2 / Debian who want the fastest path:

.. code-block:: bash

   # 1. Install system deps
   sudo apt update && sudo apt install -y \
       git python3 python3-pip build-essential cmake \
       libhdf5-dev libopenmpi-dev

   # 2. Clone & build
   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python3 scripts/run_granite.py build

   # 3. Run the single-puncture benchmark
   python3 scripts/run_granite.py run --benchmark single_puncture

----

Platform-Specific Setup
------------------------

Windows (WSL2 — Recommended ⭐)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WSL2 provides a full Linux layer inside Windows and is the **strongly recommended**
path for all HPC dependencies.

**Step 1 — Enable WSL2** (PowerShell as Administrator):

.. code-block:: powershell

   wsl --install

Restart your PC when prompted.  Ubuntu will be installed automatically.

**Step 2 — Install dependencies** (inside the Ubuntu terminal):

.. code-block:: bash

   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git python3 python3-pip build-essential cmake \
       libhdf5-dev libopenmpi-dev

**Step 3 — Clone & build:**

.. code-block:: bash

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python3 scripts/run_granite.py build

**Step 4 — Run a benchmark:**

.. code-block:: bash

   python3 scripts/run_granite.py run --benchmark single_puncture

Windows (Conda / Miniforge)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this if you work inside a **Miniforge Prompt**, **Anaconda Prompt**, or any
Conda environment.

**Step 1 — Create a dedicated environment:**

.. code-block:: bash

   conda create -n granite_env python=3.10
   conda activate granite_env

**Step 2 — Install build tools via conda-forge:**

.. code-block:: bash

   conda install -c conda-forge cmake hdf5 openmpi git

.. important::

   On **Windows Miniforge**, the C/C++ compiler must come from **Visual Studio
   Build Tools 2022**.  Download the installer from
   https://visualstudio.microsoft.com/visual-cpp-build-tools/ and select
   *"Desktop development with C++"*.  CMake will detect it automatically.

**Step 3 — Clone & build:**

.. code-block:: bash

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python scripts/run_granite.py build

Windows (Native PowerShell / CMD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this only when WSL2 and Conda are not available.

1. **Git** — https://git-scm.com/downloads (accept all defaults)
2. **CMake** — https://cmake.org/download/ → select *"Add CMake to PATH"*
3. **Visual Studio Build Tools 2022** — select *"Desktop development with C++"*
4. **Python** — https://www.python.org/downloads/ → check *"Add Python to PATH"*

.. warning::

   HDF5 and OpenMPI are **difficult to install natively on Windows without Conda or
   vcpkg**.  If you encounter missing-library errors, switch to WSL2 or Conda.
   Advanced users: install HDF5 via `vcpkg <https://vcpkg.io/>`_ and pass
   ``-DCMAKE_TOOLCHAIN_FILE`` to CMake.

.. code-block:: powershell

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python scripts/run_granite.py build
   python scripts/run_granite.py run --benchmark single_puncture

Linux — Ubuntu / Debian
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git python3 python3-pip build-essential cmake \
       libhdf5-dev libopenmpi-dev

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python3 scripts/run_granite.py build
   python3 scripts/run_granite.py run --benchmark single_puncture

Linux — Fedora / RHEL / Rocky Linux
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo dnf groupinstall -y "Development Tools"
   sudo dnf install -y git python3 cmake hdf5-devel openmpi-devel

   # Load MPI module (required on RHEL / Rocky before building)
   module load mpi/openmpi-x86_64

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python3 scripts/run_granite.py build
   python3 scripts/run_granite.py run --benchmark single_puncture

macOS
~~~~~

.. code-block:: bash

   # 1. Install Homebrew (if not already present)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # 2. Install dependencies
   brew install git python3 cmake hdf5 open-mpi

   # 3. Clone, build, and test
   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   python3 scripts/run_granite.py build
   python3 scripts/run_granite.py run --benchmark single_puncture

----

Building Manually with CMake
-----------------------------

``scripts/run_granite.py build`` calls CMake internally, but you can invoke CMake directly
for full control over build flags.

CPU-Only Build (default)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/LiranOG/Granite.git
   cd Granite
   cmake -B build -S . \
       -DCMAKE_BUILD_TYPE=Release \
       -DGRANITE_ENABLE_MPI=ON \
       -DGRANITE_ENABLE_OPENMP=ON \
       -DGRANITE_ENABLE_GPU=OFF
   cmake --build build -j$(nproc)
   ctest --test-dir build --output-on-failure

GPU Build — NVIDIA CUDA
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cmake -B build -S . \
       -DCMAKE_BUILD_TYPE=Release \
       -DGRANITE_ENABLE_GPU=ON \
       -DGRANITE_GPU_BACKEND=CUDA \
       "-DCMAKE_CUDA_ARCHITECTURES=80;90"
   cmake --build build -j$(nproc)

.. note::

   CUDA architectures: ``70`` = Volta (V100), ``80`` = Ampere (A100),
   ``90`` = Hopper (H100).  Set only the architectures you actually target
   to reduce build time.

GPU Build — AMD HIP / ROCm
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cmake -B build -S . \
       -DCMAKE_BUILD_TYPE=Release \
       -DGRANITE_ENABLE_GPU=ON \
       -DGRANITE_GPU_BACKEND=HIP
   cmake --build build -j$(nproc)

CMake Options Reference
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 35 12 53
   :header-rows: 1

   * - Option
     - Default
     - Description
   * - ``GRANITE_ENABLE_MPI``
     - ``ON``
     - Enable MPI distributed-memory parallelism
   * - ``GRANITE_ENABLE_OPENMP``
     - ``ON``
     - Enable OpenMP shared-memory threading
   * - ``GRANITE_ENABLE_GPU``
     - ``OFF``
     - Enable GPU acceleration (CUDA or HIP)
   * - ``GRANITE_GPU_BACKEND``
     - ``CUDA``
     - GPU backend selector: ``CUDA`` or ``HIP``
   * - ``GRANITE_ENABLE_HDF5``
     - ``ON``
     - Enable HDF5 parallel I/O
   * - ``GRANITE_ENABLE_PETSC``
     - ``OFF``
     - Enable PETSc elliptic solvers
   * - ``GRANITE_ENABLE_TESTS``
     - ``ON``
     - Build unit and integration tests (fetches GoogleTest)
   * - ``GRANITE_DOUBLE_PRECISION``
     - ``ON``
     - Use double precision (required for NR; do not disable)
   * - ``GRANITE_ENABLE_DOCS``
     - ``OFF``
     - Build Sphinx documentation
   * - ``GRANITE_ENABLE_PYTHON``
     - ``OFF``
     - Install Python analysis package

----

Container Builds
----------------

Docker
~~~~~~

.. code-block:: bash

   docker build -t granite:dev containers/
   docker run -it --rm -v $(pwd):/workspace granite:dev

Singularity / Apptainer (HPC clusters)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   singularity build granite.sif containers/granite.def
   singularity run granite.sif benchmarks/single_puncture/params.yaml

----

Python Analysis Tools
---------------------

Install the ``granite-analysis`` Python package (NumPy, SciPy, h5py, Matplotlib)
into your active environment:

.. code-block:: bash

   # Minimal runtime install
   pip install -e .

   # With development extras (pytest, black, mypy)
   pip install -e ".[dev]"

   # With Sphinx documentation extras
   pip install -e ".[docs]"

Requirements: Python ≥ 3.10, pip ≥ 23.

----

Available ``run_granite.py`` Commands
--------------------------------------

.. code-block:: bash

   # Build the project (wraps cmake configure + build)
   python3 scripts/run_granite.py build

   # Run the single-puncture benchmark (basic correctness test)
   python3 scripts/run_granite.py run --benchmark single_puncture

   # Run the flagship 5-BH + 2-star scenario
   python3 scripts/run_granite.py run --benchmark B5_star

   # Auto-format all C++ source files (requires clang-format ≥ 15)
   python3 scripts/run_granite.py format

   # Remove all build artifacts and start fresh
   python3 scripts/run_granite.py clean

.. note::

   On **Windows** (PowerShell / CMD), use ``python`` instead of ``python3``.
   On **WSL2, Linux, and macOS**, use ``python3``.

----

Verifying the Build
-------------------

After a successful build, the compiled binary is placed at:

* **Linux / macOS / WSL2**: ``build/bin/granite_main``
* **Windows (MSVC)**: ``build/bin/Release/granite_main.exe``  or
  ``build/bin/granite_main.exe``

Run the unit tests to confirm everything is correct:

.. code-block:: bash

   ctest --test-dir build --output-on-failure

Or via the runner:

.. code-block:: bash

   python3 scripts/run_granite.py run --benchmark single_puncture

A healthy run will print timestep lines to stdout and produce HDF5 checkpoint
files in ``output/single_puncture/``.

----

Troubleshooting
---------------

``remote: Repository not found`` / ``fatal: repository not found``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The repository URL is wrong.  Always use:

.. code-block:: bash

   git clone https://github.com/LiranOG/Granite.git

The username (``LiranOG``) and repository name (``Granite``) are case-sensitive.

``cd: The system cannot find the path specified``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``git clone`` failed (see above), so the folder was never created.

1. Confirm the clone succeeded: the output should end with
   ``Resolving deltas: 100%``.
2. Verify what was created: ``dir`` (Windows) or ``ls`` (Linux/macOS).
3. Enter the directory with the exact name: ``cd Granite``.

``Error: 'cmake' is not installed or not available in PATH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CMake is not installed, or was installed but not added to ``PATH``.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Environment
     - Fix
   * - Windows (native)
     - Re-run the CMake ``.msi`` installer and check *"Add CMake to PATH"*; restart terminal.
   * - Conda / Miniforge
     - ``conda install -c conda-forge cmake``
   * - Ubuntu / Debian / WSL2
     - ``sudo apt install cmake``  or  ``sudo snap install cmake --classic``
   * - Fedora / RHEL
     - ``sudo dnf install cmake``
   * - macOS
     - ``brew install cmake``

Verify with: ``cmake --version`` → must show ``3.20`` or higher.

``CMake Error: CMake 3.20 or higher is required``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your installed CMake is too old.  Upgrade:

* **Conda**: ``conda install -c conda-forge cmake``
* **Ubuntu**: ``sudo snap install cmake --classic``
* **macOS**: ``brew upgrade cmake``

``Could NOT find HDF5`` during CMake configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HDF5 development headers are not installed or not on the library search path.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Environment
     - Fix
   * - Ubuntu / Debian / WSL2
     - ``sudo apt install libhdf5-dev``
   * - Fedora / RHEL
     - ``sudo dnf install hdf5-devel``
   * - Conda
     - ``conda install -c conda-forge hdf5``
   * - macOS
     - ``brew install hdf5``

``Could NOT find MPI`` during CMake configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OpenMPI development headers are not installed.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Environment
     - Fix
   * - Ubuntu / Debian / WSL2
     - ``sudo apt install libopenmpi-dev``
   * - Fedora / RHEL
     - ``sudo dnf install openmpi-devel && module load mpi/openmpi-x86_64``
   * - Conda
     - ``conda install -c conda-forge openmpi``
   * - macOS
     - ``brew install open-mpi``

``Error: Executable not found. Did you run 'build' first?``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``run`` command was invoked before a successful build, or the build exited
with errors.

1. Run ``python3 scripts/run_granite.py build`` and read the full output carefully.
2. Fix any missing dependency reported by CMake (see sections above).
3. After a *"Build successful!"* message, retry the ``run`` command.

``Error: 'cl' is not recognized`` / ``MSVC compiler not found``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Visual Studio Build Tools are not installed or not on ``PATH`` (Windows only).

Install `Visual Studio Build Tools 2022 <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_
and select *"Desktop development with C++"*.  Then reopen your terminal.

``python: command not found``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Linux / macOS / WSL2, only ``python3`` is available by default.
Use ``python3`` everywhere in those environments.

``Permission denied`` when running the executable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The compiled binary lacks execute permission (Linux / macOS):

.. code-block:: bash

   chmod +x build/bin/granite_main

``Nothing to clean.`` when running ``scripts/run_granite.py clean``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is **not an error**.  It means the ``build/`` directory does not exist —
either because you never built, or a previous ``clean`` already removed it.

----

Getting Help
------------

If you encounter an error not listed here, please open an **Issue** on the
`GitHub repository <https://github.com/LiranOG/Granite/issues>`_ and include:

1. Your operating system, terminal type, and compiler version.
2. The complete output of ``python3 scripts/run_granite.py build``.
3. The output of ``cmake --version``, ``python3 --version``, and
   (if relevant) ``mpirun --version``.
