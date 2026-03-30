Installation
============

Prerequisites
-------------

GRANITE requires the following software:

* **C++17 compiler**: GCC ≥ 10, Clang ≥ 14, or Intel ≥ 2023
* **CMake** ≥ 3.20
* **MPI**: OpenMPI ≥ 4.1 or MPICH ≥ 3.4
* **HDF5** ≥ 1.12 (parallel build)
* Optional: **CUDA** ≥ 12.0 or **HIP** ≥ 5.0 for GPU acceleration
* Optional: **PETSc** ≥ 3.18 for elliptic solvers

Building from Source
--------------------

.. code-block:: bash

   git clone https://github.com/granite-nr/granite.git
   cd granite
   mkdir build && cd build

   # CPU-only build
   cmake .. -DCMAKE_BUILD_TYPE=Release \
            -DGRANITE_ENABLE_MPI=ON \
            -DGRANITE_ENABLE_GPU=OFF

   make -j$(nproc)
   ctest --output-on-failure

GPU Build (NVIDIA)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cmake .. -DCMAKE_BUILD_TYPE=Release \
            -DGRANITE_ENABLE_GPU=ON \
            -DGRANITE_GPU_BACKEND=CUDA \
            -DCMAKE_CUDA_ARCHITECTURES="80;90"

   make -j$(nproc)

GPU Build (AMD)
~~~~~~~~~~~~~~~

.. code-block:: bash

   cmake .. -DCMAKE_BUILD_TYPE=Release \
            -DGRANITE_ENABLE_GPU=ON \
            -DGRANITE_GPU_BACKEND=HIP

   make -j$(nproc)

Docker
------

.. code-block:: bash

   docker build -t granite:dev containers/
   docker run -it --rm -v $(pwd):/workspace granite:dev

Singularity (HPC)
-----------------

.. code-block:: bash

   singularity build granite.sif containers/granite.def
   singularity run granite.sif params.yaml

Python Analysis Tools
---------------------

.. code-block:: bash

   pip install -e ".[dev]"
