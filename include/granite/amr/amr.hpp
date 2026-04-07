/**
 * @file granite/amr/amr.hpp
 * @brief Adaptive Mesh Refinement module — public interface.
 *
 * Block-structured AMR with Berger-Oliger subcycling, gradient-based
 * refinement tagging, tracking spheres, and inter-level restrictions.
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
#include <array>

namespace granite::amr {

struct AMRParams {
    int max_levels          = 3;      ///< Maximum refinement levels
    int refinement_ratio    = 2;      ///< Ratio between consecutive levels
    int regrid_interval     = 4;      ///< Coarse steps between regridding
    int buffer_width        = 4;      ///< Buffer cells around tagged region
    Real refine_threshold   = 0.1;    ///< Gradient threshold for tagging
    Real derefine_threshold = 0.05;   ///< Threshold for de-refinement
    bool subcycling         = true;   ///< Berger-Oliger time subcycling
    bool use_truncation_error = false; ///< Enable Richardson truncation-error tagger (off by default)
};

struct TrackingSphere {
    std::array<Real, DIM> center;
    Real radius;
    int min_level;                    ///< Minimum AMR level to force within sphere
};

/// Refinement criterion function type
using TaggingFunction = std::function<bool(const GridBlock& block, int i, int j, int k)>;

/// Signature for single-level physics evolution step, used by AMRHierarchy::subcycle
using EvolutionStepFunc = std::function<void(std::vector<GridBlock*>& blocks, Real dt)>;

/**
 * @class AMRHierarchy
 * @brief Manages the block-structured AMR grid hierarchy.
 */
class AMRHierarchy {
public:
    explicit AMRHierarchy(const AMRParams& params,
                          const SimulationParams& sim_params);
    ~AMRHierarchy() = default;

    /// Initialize the hierarchy recursively with internal tagging
    void initialize(const TaggingFunction& tagger);

    /// Core Berger-Oliger recursive timestep subcycling loop
    void subcycle(int level, const EvolutionStepFunc& evolve_func, const TaggingFunction& tagger);

    /// Regrid: tag cells, cluster, create child blocks, and prolongate recursively
    void regrid(int level, const TaggingFunction& tagger);

    /// Get all blocks at a given refinement level
    std::vector<GridBlock*> getLevel(int level);
    const std::vector<GridBlock*> getLevel(int level) const;

    /// Get all blocks across all levels
    std::vector<GridBlock*> getAllBlocks();

    /// Number of active refinement levels
    int numLevels() const;

    /// Total number of active blocks
    int numBlocks() const;

    /// Inject a time step into a specific level (must be called before subcycle).
    /// This is the mechanism by which main.cpp keeps level dt in sync with the
    /// global CFL-controlled dt.
    void setLevelDt(int level, Real dt);

    /// Propagate the level-0 dt down ALL levels with Berger-Oliger scaling:
    ///   level L gets dt_level0 / refinement_ratio^L
    /// This is the correct way to enforce CFL ≤ 0.5 on fine levels without
    /// modifying main.cpp's global time step. Call this instead of setLevelDt(0,dt).
    void propagateDt(Real dt_level0);

    /// Fill ghost zones (inter-block communication + boundary conditions)
    void fillGhostZones(int level);

    /// Prolongation: trilinear interpolation from coarse to fine level.
    /// @param fill_interior  If true (default), fills ALL cells including interior
    ///                       (used only at block-creation time in regrid()).
    ///                       If false, fills ONLY ghost-zone cells — interior cells
    ///                       are owned by the physics RHS and must not be overwritten
    ///                       during normal ghost-fill operations.
    void prolongate(const GridBlock& coarse, GridBlock& fine,
                    bool fill_interior = true) const;

    /// Restriction: cell-averaging injection with reflux conservation
    void restrict_data(const GridBlock& fine, GridBlock& coarse) const;

    /// Add a tracking sphere (e.g., around moving BH punctures)
    void addTrackingSphere(std::array<Real, DIM> center, Real radius, int min_level);
    
    /// Dynamically update centers of existing tracking spheres
    void updateTrackingSpheres(const std::vector<std::array<Real, DIM>>& new_centers);

    /// Compute load-balancing distribution (Hilbert SFC)
    void redistributeBlocks();

    /// Get the effective resolution at a given spatial point
    Real effectiveResolution(const std::array<Real, DIM>& point) const;

    const AMRParams& params() const { return params_; }

    /// Notify the AMR hierarchy of the current global simulation step counter.
    /// Used by diagnostic taggers (e.g. truncation-error tagger) that need
    /// step-parity information for Richardson extrapolation scheduling.
    void setGlobalStep(int step);

private:
    AMRParams params_;
    SimulationParams sim_params_;

    struct Level {
        int level_id;
        std::vector<std::unique_ptr<GridBlock>> blocks;
        Real dt;              ///< Time step for this level
        Real current_time;    ///< Local evolution time 
    };

    std::vector<Level> levels_;
    std::vector<TrackingSphere> tracking_spheres_;
    int global_step_ = 0;   ///< Current global step counter, set via setGlobalStep()
};

// ===========================================================================
// Default tagging functions
// ===========================================================================

TaggingFunction gradientChiTagger(Real threshold);
TaggingFunction gradientRhoTagger(Real threshold);
TaggingFunction gradientLapseTagger(Real threshold);
TaggingFunction truncationErrorTagger(Real threshold);   ///< Richardson extrapolation-based truncation error tagger
TaggingFunction compositeTagger(std::vector<TaggingFunction> taggers);

} // namespace granite::amr
