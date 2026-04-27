/**
 * @file test_schwarzschild_horizon.cpp
 * @author Liran M. Schwartz
 * @version v0.6.7
 * @brief High-fidelity smoke tests for the apparent horizon finder on a Schwarzschild spacetime.
 *
 * P1-01 remediation: Adds the first unit coverage for src/horizon/horizon_finder.cpp (565 lines).
 * Test suite: SchwarzschildHorizonTest
 *
 * @details
 * These tests systematically verify the apparent horizon tracking algorithm
 * using analytic Brill-Lindquist initial data for a static black hole.
 *
 * Test matrix:
 *   - T1: Execution Safety (Algorithm runs without exception on BL data)
 *   - T2: Geometric Accuracy (Found horizon radius bounds: [1.5M, 2.5M] ±25%)
 *   - T3: Mass Consistency (Irreducible mass M_irr bounds: ±30% of ADM mass)
 */
#include <gtest/gtest.h>
#include "granite/horizon/horizon_finder.hpp"
#include "granite/initial_data/initial_data.hpp"
#include "granite/core/grid.hpp"
#include "granite/core/types.hpp"

#include <cmath>

using namespace granite;
using namespace granite::horizon;
using namespace granite::initial_data;

class SchwarzschildHorizonTest : public ::testing::Test {
protected:
    void SetUp() override {
        ncells_ = {16, 16, 16};
        lo_     = {-6.0, -6.0, -6.0};
        hi_     = { 6.0,  6.0,  6.0};
        nghost_ = 4;
        mass_   = 1.0;

        grid_ = std::make_unique<GridBlock>(
            0, 0, ncells_, lo_, hi_, nghost_, NUM_SPACETIME_VARS);

        BrillLindquistParams bl_params;
        bl_params.n_bh    = 1;
        bl_params.mass[0] = mass_;
        bl_params.pos[0]  = {0.0, 0.0, 0.0};

        BrillLindquistInitialData bl_solver(bl_params);
        bl_solver.initialize(*grid_);

        finder_params_.r_init      = 3.0 * mass_;
        finder_params_.n_theta     = 12;
        finder_params_.n_phi       = 24;
        finder_params_.max_iter    = 50;
        finder_params_.convergence = 1.0e-4;
    }

    std::array<int,  3> ncells_;
    std::array<Real, 3> lo_, hi_;
    int    nghost_;
    Real   mass_;
    std::unique_ptr<GridBlock> grid_;
    HorizonFinderParams finder_params_;
};

// ===========================================================================
// === TEST CASE T1: Execution Safety ===
// Verifies that the Newton-Raphson finder iteration converges or gracefully 
// exits without throwing an exception when presented with standard BL data.
// ===========================================================================
TEST_F(SchwarzschildHorizonTest, FinderDoesNotCrash) {
    HorizonFinder finder(finder_params_);
    HorizonResult result;
    EXPECT_NO_THROW(result = finder.find(*grid_))
        << "HorizonFinder::find threw on Schwarzschild BL data.";
}

// ===========================================================================
// === TEST CASE T2: Geometric Accuracy ===
// Verifies that the dynamically found coordinate radius of the apparent 
// horizon is physically consistent with the theoretical r ≈ 2M expected 
// in isotropic Brill-Lindquist coordinates (±25% coarse grid tolerance).
// ===========================================================================
TEST_F(SchwarzschildHorizonTest, HorizonRadiusWithinBounds) {
    HorizonFinder finder(finder_params_);
    HorizonResult result = finder.find(*grid_);

    ASSERT_TRUE(result.found)
        << "HorizonFinder did not find a horizon on a Schwarzschild puncture.";

    Real R = result.mean_radius;
    EXPECT_GE(R, 0.75 * 2.0 * mass_) << "Horizon radius too small: " << R;
    EXPECT_LE(R, 1.25 * 2.0 * mass_) << "Horizon radius too large: " << R;
}

// ===========================================================================
// === TEST CASE T3: Mass Consistency ===
// Verifies that the Christodoulou irreducible mass calculated from the 
// horizon proper area approximates the ADM mass M (±30% coarse grid tolerance).
// ===========================================================================
TEST_F(SchwarzschildHorizonTest, HorizonMassConsistency) {
    HorizonFinder finder(finder_params_);
    HorizonResult result = finder.find(*grid_);
    ASSERT_TRUE(result.found);

    Real M_irr = std::sqrt(result.area / (16.0 * M_PI));
    EXPECT_GE(M_irr, 0.70 * mass_) << "M_irr too small: " << M_irr;
    EXPECT_LE(M_irr, 1.30 * mass_) << "M_irr too large: " << M_irr;
}
