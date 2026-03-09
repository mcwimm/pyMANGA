# C++ Backend for Resource Modules

## Overview

Several resource competition modules in pyMANGA offer optional C++ backends built with [pybind11](https://github.com/pybind/pybind11). These compiled extensions accelerate the grid-based Zone-of-Influence (ZOI) calculations using OpenMP parallelism, which can significantly reduce runtime for large populations or fine spatial resolutions.

The C++ backends are **fully optional**. If the compiled extension is not found, pyMANGA automatically falls back to the pure-Python implementation with identical results.

## Supported Modules

| Module | Extension name | Source file |
|--------|---------------|-------------|
| `ResourceLib.AboveGround.AsymmetricZOI` | `asymzoi` | `AsymmetricZOI.cpp` |
| `ResourceLib.BelowGround.Individual.SymmetricZOI` | `symzoi` | `SymmetricZOI.cpp` |

## XML Configuration

Use the `<backend_type>` tag inside the resource module's XML block to select the backend:

```xml
<aboveground>
    <type>AsymmetricZOI</type>
    <backend_type>cpp</backend_type>
    <!-- ... other parameters ... -->
</aboveground>
```

### Accepted values

| Value | Behavior |
|-------|----------|
| `cpp` | Use the C++ backend. Falls back to Python with a warning if the compiled module is not found. |
| `python` | Force the pure-Python implementation. |
| *(omitted)* | Auto-detect: use C++ if available, otherwise Python. |

## Compilation

Building the C++ backends requires three steps: install prerequisites, run CMake, and verify the output.

### Step 1 — Install prerequisites

| Requirement | Notes |
|-------------|-------|
| **CMake** >= 3.18 | Build system generator |
| **pybind11** | Python ↔ C++ binding library |
| **C++17 compiler** | GCC or MSVC |
| **OpenMP** *(optional)* | Enables multi-threaded grid evaluation. Bundled with GCC and MSVC |

```bash
# conda (recommended)
conda install -c conda-forge cmake pybind11

# or pip
pip install cmake pybind11
```

On **Windows**, also install [Visual Studio 2022](https://visualstudio.microsoft.com/downloads/) with the **Desktop development with C++** workload.

### Step 2 — Build

**Linux**

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DPYBIND11_FINDPYTHON=ON
cmake --build build
```

**Windows (MSVC)**

```powershell
cmake -S . -B build-msvc -G "Visual Studio 17 2022" -A x64 `
  -DCMAKE_BUILD_TYPE=Release `
  -DPYBIND11_FINDPYTHON=ON
cmake --build build-msvc --config Release -- /m
```

### Step 3 — Verify

After a successful build, the compiled extensions (`.so` on Linux, `.pyd` on Windows) are placed directly into the corresponding source directories, for example:

```
ResourceLib/AboveGround/AsymmetricZOI/asymzoi.cpython-310-x86_64-linux-gnu.so
```

No manual copying or installation is needed — Python imports them from these locations automatically.

## Advanced Options

### CMake variables

| Option | Default | Description |
|--------|---------|-------------|
| `PYMANGA_DEV_LAYOUT` | `ON` | Write compiled extensions into the source tree for development use |
| `PYMANGA_BUILD_LIST` | *(empty = all)* | Semicolon-separated list of modules to build (see below) |
| `PYMANGA_ENABLE_LTO` | `OFF` | Enable link-time optimization |

### Building selected modules only

To compile only specific backends, set `PYMANGA_BUILD_LIST`:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DPYBIND11_FINDPYTHON=ON \
  -DPYMANGA_BUILD_LIST="asymzoi"
```

### Controlling OpenMP thread count

Both `asymzoi` and `symzoi` use OpenMP to parallelize the per-plant grid evaluation loop. Control the thread count via the standard environment variable:

```bash
export OMP_NUM_THREADS=4
```

No thread configuration is needed in the XML project file. If OpenMP is not installed, the build still succeeds but runs single-threaded.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `WARNING: C++ core not found. Falling back to python.` | The compiled extension was not found. Run the build commands in Step 2. |
| CMake cannot find pybind11 | Ensure pybind11 is installed in the **same** Python environment. Try `pip install pybind11` or `conda install -c conda-forge pybind11`. |
| OpenMP not detected | Install an OpenMP-capable compiler (GCC on Linux, MSVC on Windows). |
| Import errors after build | Verify the `.so`/`.pyd` file exists in the correct module directory (see Step 3). |
