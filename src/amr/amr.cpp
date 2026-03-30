/**
 * @file amr.cpp
 * @brief Minimal viable AMR implementation — single-level, single-block.
 *
 * Provides the AMRHierarchy interface with a single level-0 block.
 * Multi-level refinement, prolongation, restriction, and load
 * balancing are deferred to Phase 2.
 *
 * @copyright 2026 GRANITE Collaboration
 */
#include "granite/amr/amr.hpp"

#include <algorithm>
#include <cmath>
#include <iostream>

namespace granite::amr {

// ===========================================================================
// AMRHierarchy
// ===========================================================================

AMRHierarchy::AMRHierarchy(const AMRParams& params,
                           const SimulationParams& sim_params)
    : params_(params), sim_params_(sim_params)
{}

void AMRHierarchy::initialize()
{
    levels_.clear();

    // Create single level-0 block covering the entire domain
    Level l0;
    l0.level_id = 0;
    l0.dt = 0.0; // Will be set by CFL condition in main

    auto blk = std::make_unique<GridBlock>(
        0,                          // id
        0,                          // level
        sim_params_.ncells,
        sim_params_.domain_lo,
        sim_params_.domain_hi,
        sim_params_.ghost_cells,
        NUM_SPACETIME_VARS
    );

    l0.blocks.push_back(std::move(blk));
    levels_.push_back(std::move(l0));

    std::cout << "AMR: Initialized with 1 level, 1 block ("
              << sim_params_.ncells[0] << "x"
              << sim_params_.ncells[1] << "x"
              << sim_params_.ncells[2] << ")\n";
}

void AMRHierarchy::regrid(const TaggingFunction& /*tagger*/)
{
    // Single-level stub: no refinement
    // Full implementation requires: tag cells → cluster → create/destroy blocks
}

std::vector<GridBlock*> AMRHierarchy::getLevel(int level)
{
    std::vector<GridBlock*> result;
    if (level >= 0 && level < static_cast<int>(levels_.size())) {
        for (auto& blk : levels_[level].blocks)
            result.push_back(blk.get());
    }
    return result;
}

const std::vector<GridBlock*> AMRHierarchy::getLevel(int level) const
{
    std::vector<GridBlock*> result;
    if (level >= 0 && level < static_cast<int>(levels_.size())) {
        for (auto& blk : levels_[level].blocks)
            result.push_back(blk.get());
    }
    return result;
}

std::vector<GridBlock*> AMRHierarchy::getAllBlocks()
{
    std::vector<GridBlock*> result;
    for (auto& lev : levels_)
        for (auto& blk : lev.blocks)
            result.push_back(blk.get());
    return result;
}

int AMRHierarchy::numLevels() const
{
    return static_cast<int>(levels_.size());
}

int AMRHierarchy::numBlocks() const
{
    int count = 0;
    for (const auto& lev : levels_)
        count += static_cast<int>(lev.blocks.size());
    return count;
}

void AMRHierarchy::fillGhostZones(int level)
{
    // Zero-gradient boundary conditions for single-block:
    // Copy nearest interior values into ghost zones
    if (level < 0 || level >= static_cast<int>(levels_.size())) return;

    for (auto& blk : levels_[level].blocks) {
        int ng = blk->getNumGhost();
        int nv = blk->getNumVars();

        for (int var = 0; var < nv; ++var) {
            // X-direction ghost fill
            for (int k = 0; k < blk->totalCells(2); ++k) {
                for (int j = 0; j < blk->totalCells(1); ++j) {
                    for (int g = 0; g < ng; ++g) {
                        // Low-x ghost
                        blk->data(var, g, j, k) = blk->data(var, ng, j, k);
                        // High-x ghost
                        int ie = blk->iend(0);
                        blk->data(var, ie + g, j, k) = blk->data(var, ie - 1, j, k);
                    }
                }
            }
            // Y-direction ghost fill
            for (int k = 0; k < blk->totalCells(2); ++k) {
                for (int i = 0; i < blk->totalCells(0); ++i) {
                    for (int g = 0; g < ng; ++g) {
                        blk->data(var, i, g, k) = blk->data(var, i, ng, k);
                        int je = blk->iend(1);
                        blk->data(var, i, je + g, k) = blk->data(var, i, je - 1, k);
                    }
                }
            }
            // Z-direction ghost fill
            for (int j = 0; j < blk->totalCells(1); ++j) {
                for (int i = 0; i < blk->totalCells(0); ++i) {
                    for (int g = 0; g < ng; ++g) {
                        blk->data(var, i, j, g) = blk->data(var, i, j, ng);
                        int ke = blk->iend(2);
                        blk->data(var, i, j, ke + g) = blk->data(var, i, j, ke - 1);
                    }
                }
            }
        }
    }
}

void AMRHierarchy::prolongate(int /*fine_level*/)
{
    // Stub: no prolongation for single-level
}

void AMRHierarchy::restrict(int /*fine_level*/)
{
    // Stub: no restriction for single-level
}

void AMRHierarchy::addTrackingSphere(std::array<Real, DIM> /*center*/,
                                      Real /*radius*/, int /*min_level*/)
{
    // Stub: tracking spheres stored but not used in single-level mode
}

void AMRHierarchy::redistributeBlocks()
{
    // Stub: no load balancing for single-rank / single-block
}

Real AMRHierarchy::effectiveResolution(const std::array<Real, DIM>& /*point*/) const
{
    // Return coarsest level dx
    if (levels_.empty() || levels_[0].blocks.empty())
        return 1.0;
    return levels_[0].blocks[0]->dx(0);
}

// ===========================================================================
// Tagging functions
// ===========================================================================

TaggingFunction gradientChiTagger(Real threshold)
{
    return [threshold](const GridBlock& block, int i, int j, int k) -> bool {
        int chi_idx = static_cast<int>(SpacetimeVar::CHI);
        Real chi_c = block.data(chi_idx, i, j, k);

        // Compute gradient magnitude using central differences
        Real grad2 = 0.0;
        for (int d = 0; d < DIM; ++d) {
            int ip[3] = {i, j, k}; ip[d] += 1;
            int im[3] = {i, j, k}; im[d] -= 1;
            Real dchi = (block.data(chi_idx, ip[0], ip[1], ip[2]) -
                         block.data(chi_idx, im[0], im[1], im[2])) /
                        (2.0 * block.dx(d));
            grad2 += dchi * dchi;
        }

        return std::sqrt(grad2) / (std::abs(chi_c) + 1e-30) > threshold;
    };
}

TaggingFunction gradientRhoTagger(Real threshold)
{
    return [threshold](const GridBlock& block, int i, int j, int k) -> bool {
        // Use conserved density (HydroVar::D) if available
        if (block.getNumVars() <= static_cast<int>(HydroVar::D)) return false;

        int rho_idx = static_cast<int>(HydroVar::D);
        Real rho_c = block.data(rho_idx, i, j, k);
        if (rho_c < 1e-10) return false;

        Real grad2 = 0.0;
        for (int d = 0; d < DIM; ++d) {
            int ip[3] = {i, j, k}; ip[d] += 1;
            int im[3] = {i, j, k}; im[d] -= 1;
            Real drho = (block.data(rho_idx, ip[0], ip[1], ip[2]) -
                         block.data(rho_idx, im[0], im[1], im[2])) /
                        (2.0 * block.dx(d));
            grad2 += drho * drho;
        }

        return std::sqrt(grad2) / (rho_c + 1e-30) > threshold;
    };
}

TaggingFunction gradientLapseTagger(Real threshold)
{
    return [threshold](const GridBlock& block, int i, int j, int k) -> bool {
        int alpha_idx = static_cast<int>(SpacetimeVar::LAPSE);
        Real alpha_c = block.data(alpha_idx, i, j, k);

        Real grad2 = 0.0;
        for (int d = 0; d < DIM; ++d) {
            int ip[3] = {i, j, k}; ip[d] += 1;
            int im[3] = {i, j, k}; im[d] -= 1;
            Real dalpha = (block.data(alpha_idx, ip[0], ip[1], ip[2]) -
                           block.data(alpha_idx, im[0], im[1], im[2])) /
                          (2.0 * block.dx(d));
            grad2 += dalpha * dalpha;
        }

        return std::sqrt(grad2) / (std::abs(alpha_c) + 1e-30) > threshold;
    };
}

TaggingFunction compositeTagger(std::vector<TaggingFunction> taggers)
{
    return [taggers = std::move(taggers)](const GridBlock& block,
                                          int i, int j, int k) -> bool {
        for (const auto& tagger : taggers) {
            if (tagger(block, i, j, k)) return true;
        }
        return false;
    };
}

} // namespace granite::amr
