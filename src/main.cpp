/**
 * @file main.cpp
 * @brief GRANITE main entry point.
 *
 * Parses command-line arguments, reads a parameter file,
 * constructs initial data, and runs the evolution loop.
 *
 * @copyright 2026 GRANITE Collaboration
 */
#include "granite/core/grid.hpp"
#include "granite/core/types.hpp"
#include "granite/spacetime/ccz4.hpp"
#include "granite/initial_data/initial_data.hpp"
#include "granite/io/hdf5_io.hpp"
#include "granite/amr/amr.hpp"
#include "granite/grmhd/grmhd.hpp"

#include <yaml-cpp/yaml.h>
#include <cmath>
#include <iostream>
#include <string>
#include <map>
#include <set>
#include <memory>
#include <cmath>
#include <iostream>
#include <string>
#include <algorithm>
#include <vector>
#include <unordered_map>

#ifdef GRANITE_USE_PETSC
#include <petscsys.h>
#endif

#ifdef GRANITE_USE_MPI
#include <mpi.h>
#endif

namespace granite {

struct BlockBundle {
    int id;
    GridBlock* st; 
    std::unique_ptr<GridBlock> hydro;
    std::unique_ptr<GridBlock> prim;
    std::unique_ptr<GridBlock> st_rhs;
    std::unique_ptr<GridBlock> hydro_rhs;
    std::unique_ptr<GridBlock> st_stage;
    std::unique_ptr<GridBlock> hydro_stage;

    // Pre-allocated scratch buffers (avoid per-RK3-step heap allocation)
    std::vector<Real> rho_scratch;
    std::vector<std::array<Real, DIM>> Si_scratch;
    std::vector<std::array<Real, SYM_TENSOR_COMPS>> Sij_scratch;
    std::vector<Real> S_scratch;
    bool scratch_allocated = false;

    void allocateScratch(std::size_t total_size) {
        if (!scratch_allocated) {
            rho_scratch.resize(total_size, 0.0);
            Si_scratch.resize(total_size, {0.0, 0.0, 0.0});
            Sij_scratch.resize(total_size);
            S_scratch.resize(total_size, 0.0);
            scratch_allocated = true;
        }
    }

    void clearScratch() {
        std::fill(rho_scratch.begin(), rho_scratch.end(), 0.0);
        for (auto& s : Si_scratch) s = {0.0, 0.0, 0.0};
        for (auto& s : Sij_scratch) s = {0,0,0,0,0,0};
        std::fill(S_scratch.begin(), S_scratch.end(), 0.0);
    }
};

/**
 * @brief SSP-RK3 time integrator for the method-of-lines approach.
 *
 * u^(1) = u^n + Δt L(u^n)
 * u^(2) = (3/4)u^n + (1/4)u^(1) + (1/4)Δt L(u^(1))
 * u^{n+1} = (1/3)u^n + (2/3)u^(2) + (2/3)Δt L(u^(2))
 */
class TimeIntegrator {
public:
    static void sspRK3Step(
        std::vector<BlockBundle>& bundles,
        const std::unordered_map<int, size_t>& id_to_index,
        const spacetime::CCZ4Evolution& ccz4,
        const grmhd::GRMHDEvolution& grmhd,
        Real dt)
    {
        auto syncGhostZones = [&](bool use_stage) {
#ifdef GRANITE_USE_MPI
            int my_rank = 0;
            MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

            std::vector<MPI_Request> requests;
            std::vector<std::vector<Real>> send_bufs;
            std::vector<std::vector<Real>> recv_bufs;

            for (auto& bundle : bundles) {
                GridBlock* st = use_stage ? bundle.st_stage.get() : bundle.st;
                GridBlock* hy = use_stage ? bundle.hydro_stage.get() : bundle.hydro.get();
                for (int dir = 0; dir < 6; ++dir) {
                    int nbr_id = st->getNeighborId(dir);
                    if (nbr_id < 0) continue; 
                    
                    int nbr_rank = st->getNeighborRank(dir);
                    if (nbr_rank == my_rank) {
                        size_t nbr_idx = id_to_index.at(nbr_id);
                        GridBlock* nbr_st = use_stage ? bundles[nbr_idx].st_stage.get() : bundles[nbr_idx].st;
                        GridBlock* nbr_hy = use_stage ? bundles[nbr_idx].hydro_stage.get() : bundles[nbr_idx].hydro.get();
                        
                        std::vector<Real> buf_st, buf_hy;
                        st->packBoundary(dir, buf_st);
                        hy->packBoundary(dir, buf_hy);
                        
                        int opp_dir = dir ^ 1;
                        nbr_st->unpackBoundary(opp_dir, buf_st);
                        nbr_hy->unpackBoundary(opp_dir, buf_hy);
                    } else {
                        send_bufs.push_back(std::vector<Real>()); auto& sbuf_st = send_bufs.back();
                        st->packBoundary(dir, sbuf_st);
                        send_bufs.push_back(std::vector<Real>()); auto& sbuf_hy = send_bufs.back();
                        hy->packBoundary(dir, sbuf_hy);

                        int tag_st = bundle.id * 100 + dir;
                        int tag_hy = tag_st + 10;
                        
                        requests.push_back(MPI_REQUEST_NULL);
                        MPI_Isend(sbuf_st.data(), sbuf_st.size(), MPI_DOUBLE, nbr_rank, tag_st, MPI_COMM_WORLD, &requests.back());
                        requests.push_back(MPI_REQUEST_NULL);
                        MPI_Isend(sbuf_hy.data(), sbuf_hy.size(), MPI_DOUBLE, nbr_rank, tag_hy, MPI_COMM_WORLD, &requests.back());

                        recv_bufs.push_back(std::vector<Real>(sbuf_st.size())); auto& rbuf_st = recv_bufs.back();
                        recv_bufs.push_back(std::vector<Real>(sbuf_hy.size())); auto& rbuf_hy = recv_bufs.back();

                        int recv_tag_st = nbr_id * 100 + (dir ^ 1);
                        int recv_tag_hy = recv_tag_st + 10;
                        
                        requests.push_back(MPI_REQUEST_NULL);
                        MPI_Irecv(rbuf_st.data(), rbuf_st.size(), MPI_DOUBLE, nbr_rank, recv_tag_st, MPI_COMM_WORLD, &requests.back());
                        requests.push_back(MPI_REQUEST_NULL);
                        MPI_Irecv(rbuf_hy.data(), rbuf_hy.size(), MPI_DOUBLE, nbr_rank, recv_tag_hy, MPI_COMM_WORLD, &requests.back());
                    }
                }
            }

            if (!requests.empty()) {
                std::vector<MPI_Status> statuses(requests.size());
                MPI_Waitall(requests.size(), requests.data(), statuses.data());
            }

            int r_idx = 0;
            for (auto& bundle : bundles) {
                GridBlock* st = use_stage ? bundle.st_stage.get() : bundle.st;
                GridBlock* hy = use_stage ? bundle.hydro_stage.get() : bundle.hydro.get();
                for (int dir = 0; dir < 6; ++dir) {
                    int nbr_id = st->getNeighborId(dir);
                    if (nbr_id < 0) continue;
                    int nbr_rank = st->getNeighborRank(dir);
                    if (nbr_rank != my_rank) {
                        st->unpackBoundary(dir, recv_bufs[r_idx++]);
                        hy->unpackBoundary(dir, recv_bufs[r_idx++]);
                    }
                }
            }
#else
            for (auto& bundle : bundles) {
                GridBlock* st = use_stage ? bundle.st_stage.get() : bundle.st;
                GridBlock* hy = use_stage ? bundle.hydro_stage.get() : bundle.hydro.get();
                for (int dir = 0; dir < 6; ++dir) {
                    int nbr_id = st->getNeighborId(dir);
                    if (nbr_id < 0) continue;
                    size_t nbr_idx = id_to_index.at(nbr_id);
                    GridBlock* nbr_st = use_stage ? bundles[nbr_idx].st_stage.get() : bundles[nbr_idx].st;
                    GridBlock* nbr_hy = use_stage ? bundles[nbr_idx].hydro_stage.get() : bundles[nbr_idx].hydro.get();
                    
                    std::vector<Real> buf_st, buf_hy;
                    st->packBoundary(dir, buf_st);
                    hy->packBoundary(dir, buf_hy);
                    int opp_dir = dir ^ 1;
                    nbr_st->unpackBoundary(opp_dir, buf_st);
                    nbr_hy->unpackBoundary(opp_dir, buf_hy);
                }
            }
#endif
        };

        auto applyRHS = [&](bool use_stage) {
            for (auto& bundle : bundles) {
                GridBlock& st = use_stage ? *(bundle.st_stage) : *(bundle.st);
                GridBlock& hy = use_stage ? *(bundle.hydro_stage) : *(bundle.hydro);
                GridBlock& prim = *(bundle.prim);
                GridBlock& rhs_st = *(bundle.st_rhs);
                GridBlock& rhs_hy = *(bundle.hydro_rhs);

                grmhd.conservedToPrimitive(st, hy, prim);

                // Use pre-allocated scratch buffers instead of per-call heap allocation
                bundle.clearScratch();
                auto& rho = bundle.rho_scratch;
                auto& Si  = bundle.Si_scratch;
                auto& Sij = bundle.Sij_scratch;
                auto& S   = bundle.S_scratch;
                
                grmhd.computeMatterSources(st, prim, rho, Si, Sij, S);
                ccz4.computeRHS(st, rhs_st, rho, Si, Sij, S);
                grmhd.computeRHS(st, hy, prim, rhs_hy);
            }
        };

        auto combine = [&](bool write_stage, Real a1, bool s1_stage, Real a2, bool s2_stage, Real a3) {
            for (auto& bundle : bundles) {
                GridBlock& dst_st = write_stage ? *(bundle.st_stage) : *(bundle.st);
                GridBlock& dst_hy = write_stage ? *(bundle.hydro_stage) : *(bundle.hydro);
                GridBlock& s1_st = s1_stage ? *(bundle.st_stage) : *(bundle.st);
                GridBlock& s1_hy = s1_stage ? *(bundle.hydro_stage) : *(bundle.hydro);
                GridBlock& s2_st = s2_stage ? *(bundle.st_stage) : *(bundle.st);
                GridBlock& s2_hy = s2_stage ? *(bundle.hydro_stage) : *(bundle.hydro);
                GridBlock& rst = *(bundle.st_rhs);
                GridBlock& rhy = *(bundle.hydro_rhs);

                auto doCombine = [&](GridBlock& d, GridBlock& s1, GridBlock& s2, GridBlock& r) {
                    const int ie0 = d.iend(0);
                    const int ie1 = d.iend(1);
                    const int ie2 = d.iend(2);
                    const int is  = d.istart();
                    for(int v=0; v<d.getNumVars(); ++v) {
                        for(int k=is; k<ie2; ++k)
                        for(int j=is; j<ie1; ++j)
                        for(int i=is; i<ie0; ++i)
                            d.data(v,i,j,k) = a1*s1.data(v,i,j,k) + a2*s2.data(v,i,j,k) + a3*dt*r.data(v,i,j,k);
                    }
                };
                doCombine(dst_st, s1_st, s2_st, rst);
                doCombine(dst_hy, s1_hy, s2_hy, rhy);
            }
        };

        applyRHS(false);
        combine(true, 1.0, false, 0.0, false, 1.0);
        syncGhostZones(true);

        applyRHS(true);
        combine(true, 0.75, false, 0.25, true, 0.25);
        syncGhostZones(true);

        applyRHS(true);
        combine(false, 1.0/3.0, false, 2.0/3.0, true, 2.0/3.0);
        syncGhostZones(false);
    }
};

} // namespace granite

// ===========================================================================
// Main
// ===========================================================================

int main(int argc, char* argv[])
{
#ifdef GRANITE_USE_PETSC
    PetscInitialize(&argc, &argv, nullptr, nullptr);
#endif

    using namespace granite;

    std::cout << "================================================================\n";
    std::cout << " GRANITE v" << "0.1.0" << "\n";
    std::cout << " General-Relativistic Adaptive N-body Integrated Tool\n";
    std::cout << " for Extreme Astrophysics\n";
    std::cout << "================================================================\n\n";

    // --- Default parameters ---
    SimulationParams params;

    if (argc > 1) {
        std::string param_file = argv[1];
        std::cout << "Loading parameter file: " << param_file << "\n";
        try {
            YAML::Node config = YAML::LoadFile(param_file);
            if (config["grid"]) {
                auto grid = config["grid"];
                if (grid["ncells"]) {
                    params.ncells[0] = grid["ncells"][0].as<int>();
                    params.ncells[1] = grid["ncells"][1].as<int>();
                    params.ncells[2] = grid["ncells"][2].as<int>();
                }
                if (grid["domain_lo"]) {
                    params.domain_lo[0] = grid["domain_lo"][0].as<Real>();
                    params.domain_lo[1] = grid["domain_lo"][1].as<Real>();
                    params.domain_lo[2] = grid["domain_lo"][2].as<Real>();
                }
                if (grid["domain_hi"]) {
                    params.domain_hi[0] = grid["domain_hi"][0].as<Real>();
                    params.domain_hi[1] = grid["domain_hi"][1].as<Real>();
                    params.domain_hi[2] = grid["domain_hi"][2].as<Real>();
                }
                if (grid["ghost_cells"]) params.ghost_cells = grid["ghost_cells"].as<int>();
            }
            if (config["time"]) {
                auto time = config["time"];
                if (time["cfl"]) params.cfl = time["cfl"].as<Real>();
                if (time["t_final"]) params.t_final = time["t_final"].as<Real>();
                if (time["max_steps"]) params.max_steps = time["max_steps"].as<int>();
            }
            if (config["ccz4"]) {
                auto ccz4 = config["ccz4"];
                if (ccz4["kappa1"]) params.kappa1 = ccz4["kappa1"].as<Real>();
                if (ccz4["kappa2"]) params.kappa2 = ccz4["kappa2"].as<Real>();
                if (ccz4["eta"]) params.eta = ccz4["eta"].as<Real>();
                if (ccz4["ko_sigma"]) params.ko_sigma = ccz4["ko_sigma"].as<Real>();
            }
            if (config["io"]) {
                auto io = config["io"];
                if (io["output_dir"]) params.output_dir = io["output_dir"].as<std::string>();
                if (io["output_interval"]) params.output_interval = io["output_interval"].as<int>();
                if (io["checkpoint_interval"]) params.checkpoint_interval = io["checkpoint_interval"].as<int>();
            }
        } catch (const YAML::Exception& e) {
            std::cerr << "YAML parsing error: " << e.what() << "\n";
            return 1;
        }
    }

    // --- Create Grids & Systems ---
    grmhd::GRMHDParams grmhd_params;
    auto eos = std::make_shared<grmhd::IdealGasEOS>(5.0/3.0);
    grmhd::GRMHDEvolution grmhd(grmhd_params, eos);

    amr::AMRParams amr_params;
    amr_params.regrid_interval = params.regrid_interval;
    amr::AMRHierarchy hierarchy(amr_params, params);
    std::cout << "Initializing AMR Hierarchy...\n";
    hierarchy.initialize();

    std::vector<BlockBundle> active_bundles;
    std::unordered_map<int, size_t> id_to_index;

    auto syncBlocks = [&]() {
        auto active_blocks = hierarchy.getAllBlocks();
        std::set<int> active_ids;
        for (auto* b : active_blocks) {
            active_ids.insert(b->getId());
        }

        // Remove outdated bundles
        active_bundles.erase(
            std::remove_if(active_bundles.begin(), active_bundles.end(),
                [&](const BlockBundle& bundle) { return active_ids.find(bundle.id) == active_ids.end(); }),
            active_bundles.end()
        );

        // Add missing bundles and sync ST pointers
        std::set<int> existing_ids;
        for (const auto& bundle : active_bundles) existing_ids.insert(bundle.id);

        for (auto* b : active_blocks) {
            if (existing_ids.find(b->getId()) == existing_ids.end()) {
                BlockBundle bundle;
                bundle.id = b->getId();
                bundle.st = b;
                bundle.hydro = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_HYDRO_VARS);
                bundle.prim  = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_PRIMITIVE_VARS);
                bundle.st_rhs = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_SPACETIME_VARS);
                bundle.hydro_rhs = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_HYDRO_VARS);
                bundle.st_stage = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_SPACETIME_VARS);
                bundle.hydro_stage = std::make_unique<GridBlock>(b->getId(), b->getLevel(), params.ncells, b->lowerCorner(), b->upperCorner(), b->getNumGhost(), NUM_HYDRO_VARS);
                active_bundles.push_back(std::move(bundle));
            } else {
                // O(1) lookup via id_to_index map
                auto it = id_to_index.find(b->getId());
                if (it != id_to_index.end()) {
                    active_bundles[it->second].st = b;
                }
            }
        }

        // Synchronize O(1) neighbor/boundary lookup map
        id_to_index.clear();
        for (size_t i = 0; i < active_bundles.size(); ++i) {
            id_to_index[active_bundles[i].id] = i;
        }

        // Allocate scratch buffers (one-time per bundle)
        for (auto& bundle : active_bundles) {
            if (bundle.st) {
                bundle.allocateScratch(bundle.st->totalSize());
            }
        }
    };

    // --- Set initial data ---
    std::cout << "Setting initial data: flat Minkowski spacetime & GRMHD Atmosphere\n";
    syncBlocks();
    for(auto& bundle : active_bundles) {
        spacetime::setFlatSpacetime(*(bundle.st));
        auto& hy = *(bundle.hydro);
        for(int v=0; v<hy.getNumVars(); ++v) {
            for(int k=0; k<hy.totalCells(2); ++k)
            for(int j=0; j<hy.totalCells(1); ++j)
            for(int i=0; i<hy.totalCells(0); ++i)
                hy.data(v, i,j,k) = (v == 0 || v == 4) ? 1.0e-12 : 0.0;
        }
        grmhd.conservedToPrimitive(*(bundle.st), hy, *(bundle.prim));
    }

    // --- CCZ4 evolution ---
    spacetime::CCZ4Params ccz4_params;
    ccz4_params.kappa1 = params.kappa1;
    ccz4_params.kappa2 = params.kappa2;
    ccz4_params.eta    = params.eta;
    ccz4_params.ko_sigma = params.ko_sigma;

    spacetime::CCZ4Evolution ccz4(ccz4_params);

    // --- I/O Writer ---
    io::IOParams io_params;
    io_params.output_dir = params.output_dir;
    io_params.output_interval = params.output_interval;
    io_params.checkpoint_interval = params.checkpoint_interval;
    io::HDF5Writer writer(io_params);

    // --- Compute time step ---
    auto initial_blocks = hierarchy.getAllBlocks();
    GridBlock* base_block = initial_blocks[0];
    Real dx_min = std::min({base_block->dx(0),
                            base_block->dx(1),
                            base_block->dx(2)});
    Real dt = params.cfl * dx_min;

    std::cout << "Grid: " << params.ncells[0] << " x " << params.ncells[1]
              << " x " << params.ncells[2] << "\n";
    std::cout << "dx = " << dx_min << ", dt = " << dt << "\n";
    std::cout << "t_final = " << params.t_final << "\n\n";

    // --- Evolution loop ---
    Real t = 0.0;
    int step = 0;
    int initial_ncells = params.ncells[0]; 

    while (t < params.t_final && step < params.max_steps) {
        if (t + dt > params.t_final) dt = params.t_final - t;

        if (step > 0 && step % params.regrid_interval == 0) {
            hierarchy.regrid(amr::gradientChiTagger(params.refine_threshold));
            syncBlocks();
            hierarchy.fillGhostZones(0);
        }

        TimeIntegrator::sspRK3Step(active_bundles, id_to_index, ccz4, grmhd, dt);

        t += dt;
        step++;

        if (step % params.output_interval == 0) {
            std::vector<Real> ham;
            std::vector<std::array<Real, DIM>> mom;
            
            Real ham_l2 = 0.0;
            int count = 0;
            Real alpha_center = 1.0;

            for(auto* block : hierarchy.getAllBlocks()) {
                ccz4.computeConstraints(*block, ham, mom);
                int is = block->istart();
                int ie = block->iend();
                for (int k = is; k < ie; ++k)
                    for (int j = is; j < ie; ++j)
                        for (int i = is; i < ie; ++i) {
                            int flat = block->totalCells(0) * (block->totalCells(1) * k + j) + i;
                            ham_l2 += ham[flat] * ham[flat];
                            count++;
                        }
                if(block->getLevel() == 0) {
                   alpha_center = block->data(static_cast<int>(SpacetimeVar::LAPSE), 
                                              initial_ncells/2 + params.ghost_cells, 
                                              initial_ncells/2 + params.ghost_cells, 
                                              initial_ncells/2 + params.ghost_cells);
                }
            }
            if(count > 0) ham_l2 = std::sqrt(ham_l2 / count);

            std::cout << "  step=" << step
                      << "  t=" << t
                      << "  α_center=" << alpha_center
                      << "  ||H||₂=" << ham_l2
                      << "  [Blocks: " << hierarchy.numBlocks() << "]\n";
                      
            writer.appendTimeSeries(params.output_dir + "/timeseries.h5", "constraints/hamiltonian_l2", t, ham_l2);
        }

        if (step % params.checkpoint_interval == 0 || t >= params.t_final) {
            std::vector<const GridBlock*> c_blocks;
            for(auto* b : hierarchy.getAllBlocks()) c_blocks.push_back(b);
            writer.writeCheckpoint(c_blocks, step, t, params);
        }
    }

    std::cout << "Evolution complete.\n";

#ifdef GRANITE_USE_PETSC
    PetscFinalize();
#endif

    return 0;
}
