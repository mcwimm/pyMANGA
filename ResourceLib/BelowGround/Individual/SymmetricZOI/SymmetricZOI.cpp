// ResourceLib/BelowGround/Individual/SymmetricZOI/SymmetricZOI.cpp
//
// Summary
// -------
// Pybind11 C++ core for the Symmetric Zone of Influence (ZOI) below-ground
// competition model. Plants share grid cells proportionally when their root
// zones overlap. The per-plant belowground resource factor is computed as:
// plant_wins / plant_counts, where plant_wins is the sum of 1/n for each
// cell (n = number of plants sharing that cell).
//
// Notes
// -----
// - Inputs are provided as NumPy arrays (float64) from Python.
// - All internal computation uses double precision to match the Python path.
// - OpenMP (if available) parallelizes the loop over grid cells.
//
// Safety / Validation
// -------------------
// - Consistency checks for array sizes and grid shapes.
// - Detects oversize grids for 32-bit indexing safety.
// - Throws on NaN in the final result to surface unexpected conditions.

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <vector>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <limits>
#include <sstream>
namespace py = pybind11;

#ifdef _OPENMP
  #include <omp.h>
#endif

// compute_belowground_resources
// Parameters
//   xe, ye      : 1D (n_plants) arrays of plant positions
//   r_root      : 1D (n_plants) root radii
//   grid_x/y    : 2D (gy x gx) coordinate arrays for the grid
//   mesh_size   : grid mesh size used for minimum-radius handling
// Returns
//   1D (n_plants) float64 array with per-plant belowground resource factor ∈ [0, 1]
py::array_t<double> compute_belowground_resources(
    py::array_t<double, py::array::c_style | py::array::forcecast> xe,
    py::array_t<double, py::array::c_style | py::array::forcecast> ye,
    py::array_t<double, py::array::c_style | py::array::forcecast> r_root,
    py::array_t<double, py::array::c_style | py::array::forcecast> grid_x,
    py::array_t<double, py::array::c_style | py::array::forcecast> grid_y,
    double mesh_size, int n_threads /* -1 -> auto */) {

    // Basic input validation & grid bookkeeping
    const int n_plants = (int)xe.size();
    if (ye.size() != xe.size() || r_root.size() != xe.size())
        throw std::invalid_argument("xe, ye, r_root must have same length");
    if (grid_x.ndim() != 2 || grid_y.ndim() != 2)
        throw std::invalid_argument("grid_x and grid_y must be 2D");
    if (grid_x.shape(0) != grid_y.shape(0) || grid_x.shape(1) != grid_y.shape(1))
        throw std::invalid_argument("grid_x and grid_y must have same shape");

    const int gy = (int)grid_x.shape(0), gx = (int)grid_x.shape(1);
    if (gy <= 0 || gx <= 0 || (long long)gy * (long long)gx > INT32_MAX)
        throw std::runtime_error("grid too large for 32-bit indexing");
    const int grid_size = gy * gx;

#ifdef _OPENMP
    omp_set_dynamic(0);
    if (n_threads > 0)
        omp_set_num_threads(n_threads);
    else
        omp_set_num_threads(omp_get_num_procs());
#endif

    // Tolerance for checking whether a plant covers a grid cell (e^-20)
    const double allowed_error = std::exp(-20.0);

    // Raw pointers for tight loops
    const double* px = xe.data();
    const double* py_ = ye.data();
    const double* pr = r_root.data();
    const double* pgx = grid_x.data();
    const double* pgy = grid_y.data();

    // Working buffers
    // plant_counts : per-plant number of grid cells within its root zone
    // plant_wins   : per-plant sum of 1/n for each cell it occupies
    std::vector<double> plant_counts(n_plants, 0.0);
    std::vector<double> plant_wins(n_plants, 0.0);

    // Step 1: Count how many plants occupy each grid cell
    std::vector<int> cell_plant_count(grid_size, 0);

    // First pass: count plants per cell and plant_counts
    for (int i = 0; i < n_plants; ++i) {
        double x = px[i], y = py_[i], r = pr[i];
        const double r_with_tol = r + allowed_error;
        int local_count = 0;

#ifdef _OPENMP
        #pragma omp parallel for schedule(static) reduction(+:local_count)
#endif
        for (int idx = 0; idx < grid_size; ++idx) {
            double dx = pgx[idx] - x;
            double dy = pgy[idx] - y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (r_with_tol >= dist) {
                local_count += 1;
#ifdef _OPENMP
                #pragma omp atomic
#endif
                cell_plant_count[idx] += 1;
            }
        }
        plant_counts[i] = (double)local_count;
    }

    // Second pass: for each plant, accumulate wins (1/n for each occupied cell)
    for (int i = 0; i < n_plants; ++i) {
        double x = px[i], y = py_[i], r = pr[i];
        const double r_with_tol = r + allowed_error;
        double local_wins = 0.0;

#ifdef _OPENMP
        #pragma omp parallel for schedule(static) reduction(+:local_wins)
#endif
        for (int idx = 0; idx < grid_size; ++idx) {
            double dx = pgx[idx] - x;
            double dy = pgy[idx] - y;
            double dist = std::sqrt(dx * dx + dy * dy);
            if (r_with_tol >= dist) {
                int n_sharing = cell_plant_count[idx];
                if (n_sharing > 0) {
                    local_wins += 1.0 / (double)n_sharing;
                }
            }
        }
        plant_wins[i] = local_wins;
    }

    // Normalize to get per-plant resource factor; NaN guard
    py::array_t<double> out(n_plants);
    auto o = out.mutable_unchecked<1>();
    for (int i = 0; i < n_plants; ++i) {
        double denom = plant_counts[i];
        o(i) = (denom > 0.0) ? (plant_wins[i] / denom) : std::numeric_limits<double>::quiet_NaN();
        if (o(i) != o(i)) // NaN check
            throw std::runtime_error(
                "NaN detected in belowground_resources for plants at indices: [" +
                std::to_string(i) + "]"
            );
    }
    return out;
}


// pybind11 module declaration
// Exposes the function `compute_belowground_resources` to Python as:
PYBIND11_MODULE(symzoi, m) {
    m.doc() = "Symmetric ZOI CPP core (keeps Python API unchanged)";
    m.def("compute_belowground_resources", &compute_belowground_resources,
          py::arg("xe"), py::arg("ye"), py::arg("r_root"),
          py::arg("grid_x"), py::arg("grid_y"),
          py::arg("mesh_size"),
          py::arg("n_threads") = -1);
}
