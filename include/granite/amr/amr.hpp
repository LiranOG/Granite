/**
 * @file granite/amr/amr.hpp
 * @brief Adaptive Mesh Refinement module — public interface.
 *
 * Block-structured AMR with Berger-Oliger subcycling, gradient-based
 * refinement tagging, and load balancing via space-filling curves.
 *
 * @copyright 2026 GRANITE Collaboration
 * @license GPL-3.0-or-later
 */
#pragma once

#include "granite/core/grid.hpp"
#include "granite/core/types.hpp"

#include <functional>
#include <memory>
#include <vector>

namespace granite::amr {

struct AMRParams {
    int max_levels          = 15;     ///< Maximum refinement levels
    int refinement_ratio    = 2;      ///< Ratio between consecutive levels
    int regrid_interval     = 4;      ///< Coarse steps between regridding
    int buffer_width        = 2;      ///< Buffer cells around tagged region
    Real refine_threshold   = 0.1;    ///< Gradient threshold for tagging
    Real derefine_threshold = 0.05;   ///< Threshold for de-refinement
    bool subcycling         = true;   ///< Berger-Oliger time subcycling
};

/// Refinement criterion function type
using TaggingFunction = std::function<bool(const GridBlock& block, int i, int j, int k)>;

/**
 * @class AMRHierarchy
 * @brief Manages the block-structured AMR grid hierarchy.
 */
class AMRHierarchy {
public:
    explicit AMRHierarchy(const AMRParams& params,
                          const SimulationParams& sim_params);
    ~AMRHierarchy() = default;

    /// Initialize the hierarchy with the coarsest level
    void initialize();

    /// Regrid: tag cells, cluster into patches, create/destroy blocks
    void regrid(const TaggingFunction& tagger);

    /// Get all blocks at a given refinement level
    std::vector<GridBlock*> getLevel(int level);
    const std::vector<GridBlock*> getLevel(int level) const;

    /// Get all blocks across all levels
    std::vector<GridBlock*> getAllBlocks();

    /// Number of active refinement levels
    int numLevels() const;

    /// Total number of active blocks
    int numBlocks() const;

    /// Fill ghost zones (inter-block communication + boundary conditions)
    void fillGhostZones(int level);

    /// Prolongation: interpolate from coarse to fine level
    void prolongate(const GridBlock& coarse, GridBlock& fine) const;

    /// Restriction: average from fine to coarse level
    void restrict_data(const GridBlock& fine, GridBlock& coarse) const;

    /// Add a tracking sphere (e.g. around a BH horizon)
    void addTrackingSphere(std::array<Real, DIM> center, Real radius, int min_level);

    /// Compute load-balancing distribution (Hilbert SFC)
    void redistributeBlocks();

    /// Get the effective resolution at a given spatial point
    Real effectiveResolution(const std::array<Real, DIM>& point) const;

    const AMRParams& params() const { return params_; }

private:
    AMRParams params_;
    SimulationParams sim_params_;

    struct Level {
        int level_id;
        std::vector<std::unique_ptr<GridBlock>> blocks;
        Real dt;  ///< Time step for this level
    };

    std::vector<Level> levels_;
};

// ===========================================================================
// Default tagging functions
// ===========================================================================

/// Tag based on gradient of conformal factor χ
TaggingFunction gradientChiTagger(Real threshold);

/// Tag based on gradient of rest-mass density
TaggingFunction gradientRhoTagger(Real threshold);

/// Tag based on gradient of lapse α
TaggingFunction gradientLapseTagger(Real threshold);

/// Composite tagger: tag if any sub-tagger triggers
TaggingFunction compositeTagger(std::vector<TaggingFunction> taggers);

} // namespace granite::amr
