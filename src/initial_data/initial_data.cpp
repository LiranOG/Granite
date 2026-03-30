/**
 * @file initial_data.cpp
 * @brief Initial data construction — Brill-Lindquist, TOV/polytrope.
 *
 * @copyright 2026 GRANITE Collaboration
 */
#include "granite/initial_data/initial_data.hpp"
#include <cmath>
#include <iostream>
#include <numeric>
#include "granite/spacetime/ccz4.hpp"

#ifdef GRANITE_USE_PETSC
#include <petscsnes.h>

namespace granite {
namespace initial_data {

struct BowenYorkCtx {
    int nx, ny, nz, nghost;
    Real dx2;
    const std::vector<Real>* psi_BL;
    const std::vector<Real>* Atilde2;
};

static PetscErrorCode FormFunction(SNES snes, Vec x, Vec f, void *ctx) {
    BowenYorkCtx* app = static_cast<BowenYorkCtx*>(ctx);
    const PetscScalar* xx;
    PetscScalar* ff;
    VecGetArrayRead(x, &xx);
    VecGetArray(f, &ff);

    int nx = app->nx, ny = app->ny, nz = app->nz, nghost = app->nghost;
    Real dx2 = app->dx2;
    const auto& psi_BL = *(app->psi_BL);
    const auto& Atilde2 = *(app->Atilde2);

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                int flat = i + nx*(j + ny*k);
                if (i < nghost || i >= nx-nghost || j < nghost || j >= ny-nghost || k < nghost || k >= nz-nghost) {
                    ff[flat] = xx[flat];
                    continue;
                }
                
                Real u_c = xx[flat];
                Real u_avg = xx[flat + 1] + xx[flat - 1] + xx[flat + nx] + xx[flat - nx] + xx[flat + nx*ny] + xx[flat - nx*ny];
                Real D2u = (u_avg - 6.0 * u_c) / dx2;
                Real psi = psi_BL[flat] + u_c;
                Real source = 0.125 * Atilde2[flat] / std::pow(psi, 7.0);
                
                ff[flat] = D2u + source;
            }
        }
    }

    VecRestoreArrayRead(x, &xx);
    VecRestoreArray(f, &ff);
    return 0;
}

} // namespace initial_data
} // namespace granite
#endif

namespace granite::initial_data {

// ===========================================================================
// Brill-Lindquist
// ===========================================================================

BrillLindquist::BrillLindquist(const std::vector<BlackHoleParams>& bhs)
    : bhs_(bhs) {}

Real BrillLindquist::conformalFactor(Real x, Real y, Real z) const
{
    Real psi = 1.0;
    for (const auto& bh : bhs_) {
        Real dx = x - bh.position[0];
        Real dy = y - bh.position[1];
        Real dz = z - bh.position[2];
        Real r = std::sqrt(dx*dx + dy*dy + dz*dz + 1.0e-30);
        psi += bh.mass / (2.0 * r);
    }
    return psi;
}

Real BrillLindquist::admMass() const
{
    return std::accumulate(bhs_.begin(), bhs_.end(), 0.0,
        [](Real sum, const BlackHoleParams& bh) { return sum + bh.mass; });
}

void BrillLindquist::apply(GridBlock& grid) const
{
    // First set flat spacetime
    spacetime::setFlatSpacetime(grid);

    const int nx = grid.totalCells(0);
    const int ny = grid.totalCells(1);
    const int nz = grid.totalCells(2);

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                Real x = grid.x(0, i);
                Real y = grid.x(1, j);
                Real z = grid.x(2, k);

                Real psi = conformalFactor(x, y, z);
                // χ = ψ^{-4}
                Real chi = 1.0 / (psi * psi * psi * psi);
                // α = ψ^{-2} (isotropic gauge)
                Real alpha = 1.0 / (psi * psi);

                grid.data(static_cast<int>(SpacetimeVar::CHI), i, j, k) = chi;
                grid.data(static_cast<int>(SpacetimeVar::LAPSE), i, j, k) = alpha;

                // Conformal metric remains flat: γ̃_{ij} = δ_{ij}
                // Physical metric: γ_{ij} = ψ⁴ δ_{ij}
            }
        }
    }
}

// ===========================================================================
// Bowen-York (stub — requires elliptic solver)
// ===========================================================================

BowenYorkPuncture::BowenYorkPuncture(const std::vector<BlackHoleParams>& bhs)
    : bhs_(bhs) {}

void BowenYorkPuncture::solve(GridBlock& grid) const
{
    // Step 1: Set Brill-Lindquist background
    BrillLindquist bl(bhs_);
    bl.apply(grid);

    // Step 2: Set Bowen-York extrinsic curvature
    setBowenYorkExtrinsicCurvature(grid);

    // Step 3: Solve Hamiltonian constraint for correction u(r)
    const int nx = grid.totalCells(0);
    const int ny = grid.totalCells(1);
    const int nz = grid.totalCells(2);
    const int nghost = grid.getNumGhost();
    
    std::vector<Real> u(grid.totalSize(), 0.0);
    std::vector<Real> u_new(grid.totalSize(), 0.0);
    std::vector<Real> psi_BL(grid.totalSize(), 1.0);
    std::vector<Real> Atilde2(grid.totalSize(), 0.0);
    
    Real dx = grid.dx(0);
    Real dx2 = dx * dx;

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                int flat = i + nx*(j + ny*k);
                Real x = grid.x(0, i);
                Real y = grid.x(1, j);
                Real z = grid.x(2, k);
                
                psi_BL[flat] = bl.conformalFactor(x, y, z);
                
                Real Axx = grid.data(static_cast<int>(SpacetimeVar::A_XX), i, j, k);
                Real Axy = grid.data(static_cast<int>(SpacetimeVar::A_XY), i, j, k);
                Real Axz = grid.data(static_cast<int>(SpacetimeVar::A_XZ), i, j, k);
                Real Ayy = grid.data(static_cast<int>(SpacetimeVar::A_YY), i, j, k);
                Real Ayz = grid.data(static_cast<int>(SpacetimeVar::A_YZ), i, j, k);
                Real Azz = grid.data(static_cast<int>(SpacetimeVar::A_ZZ), i, j, k);
                
                Atilde2[flat] = Axx*Axx + Ayy*Ayy + Azz*Azz + 2.0*(Axy*Axy + Axz*Axz + Ayz*Ayz);
            }
        }
    }

#ifdef GRANITE_USE_PETSC
    std::cout << "Using PETSc SNES solver for Bowen-York constraint...\n";

    SNES snes;
    Vec x, r;
    Mat J;
    int N = grid.totalSize();
    
    VecCreateMPI(PETSC_COMM_WORLD, N, PETSC_DETERMINE, &x);
    VecDuplicate(x, &r);
    VecSet(x, 0.0);
    
    BowenYorkCtx ctx = {nx, ny, nz, nghost, dx2, &psi_BL, &Atilde2};
    
    SNESCreate(PETSC_COMM_WORLD, &snes);
    SNESSetFunction(snes, r, FormFunction, &ctx);
    
    MatCreateMPIAIJ(PETSC_COMM_WORLD, N, N, PETSC_DETERMINE, PETSC_DETERMINE, 7, NULL, 7, NULL, &J);
    SNESSetJacobian(snes, J, J, SNESComputeJacobianDefault, &ctx);

    KSP ksp;
    PC pc;
    SNESGetKSP(snes, &ksp);
    KSPGetPC(ksp, &pc);
    PCSetType(pc, PCGAMG); 
    
    SNESSetFromOptions(snes);
    SNESSolve(snes, NULL, x);
    
    PetscInt iters;
    SNESGetIterationNumber(snes, &iters);
    
    PetscReal norm;
    SNESGetFunctionNorm(snes, &norm);
    std::cout << "PETSc SNES converged in " << iters << " iterations, residual=" << norm << "\n";
    
    const PetscScalar* xx;
    VecGetArrayRead(x, &xx);
    for(int i=0; i<N; ++i) u_new[i] = xx[i];
    VecRestoreArrayRead(x, &xx);
    u.swap(u_new);
    
    MatDestroy(&J);
    VecDestroy(&x);
    VecDestroy(&r);
    SNESDestroy(&snes);
#else
    // Jacobi / Gauss-Seidel Relaxation Iterator
    const int max_iter = 500;
    const Real tol = 1.0e-5;
    Real residual = 1.0;
    int iter = 0;

    while (iter < max_iter && residual > tol) {
        residual = 0.0;
        for (int k = nghost; k < nz - nghost; ++k) {
            for (int j = nghost; j < ny - nghost; ++j) {
                for (int i = nghost; i < nx - nghost; ++i) {
                    int flat = i + nx*(j + ny*k);
                    
                    Real u_avg = u[flat + 1] + u[flat - 1] + 
                                 u[flat + nx] + u[flat - nx] + 
                                 u[flat + nx*ny] + u[flat - nx*ny];
                    
                    Real psi7_inv = 1.0 / std::pow(psi_BL[flat] + u[flat], 7.0);
                    Real rhs = -0.125 * Atilde2[flat] * psi7_inv;
                    Real unew = (u_avg - dx2 * rhs) / 6.0;
                    
                    u_new[flat] = unew;
                    Real diff = unew - u[flat];
                    residual += diff * diff;
                }
            }
        }
        u.swap(u_new);
        residual = std::sqrt(residual / grid.totalSize());
        iter++;
    }

    std::cout << "Bowen-York Gauss-Seidel solver: " << iter << " iterations, residual=" << residual << "\n";
#endif

    // Set final physical data
    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                int flat = i + nx*(j + ny*k);
                Real psi = psi_BL[flat] + u[flat];
                grid.data(static_cast<int>(SpacetimeVar::CHI), i, j, k) = 1.0 / (psi*psi*psi*psi);
                grid.data(static_cast<int>(SpacetimeVar::LAPSE), i, j, k) = 1.0 / (psi*psi);
            }
        }
    }
}

void BowenYorkPuncture::setBowenYorkExtrinsicCurvature(GridBlock& grid) const
{
    const int nx = grid.totalCells(0);
    const int ny = grid.totalCells(1);
    const int nz = grid.totalCells(2);

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                Real x = grid.x(0, i);
                Real y = grid.x(1, j);
                Real z = grid.x(2, k);

                // Bowen-York Ã_{ij} for each puncture:
                // Ã_{ij}^{BY} = (3/2r²) [2P_{(i} n_{j)} - (δ_{ij} - n_i n_j) P^k n_k]
                //             + (3/r³) [ε_{kl(i} S^l n_{j)} n^k]
                Real Atilde[6] = {};

                for (const auto& bh : bhs_) {
                    Real dx = x - bh.position[0];
                    Real dy = y - bh.position[1];
                    Real dz = z - bh.position[2];
                    Real r2 = dx*dx + dy*dy + dz*dz + 1.0e-30;
                    Real r = std::sqrt(r2);
                    Real inv_r2 = 1.0 / r2;

                    Real n[3] = {dx/r, dy/r, dz/r};
                    Real P[3] = {bh.momentum[0], bh.momentum[1], bh.momentum[2]};
                    Real Pn = P[0]*n[0] + P[1]*n[1] + P[2]*n[2];

                    // Linear momentum contribution
                    for (int a = 0; a < 3; ++a) {
                        for (int b = a; b < 3; ++b) {
                            Real delta_ab = (a == b) ? 1.0 : 0.0;
                            Real val = 1.5 * inv_r2 * (
                                P[a]*n[b] + P[b]*n[a] -
                                (delta_ab - n[a]*n[b]) * Pn
                            );
                            Atilde[symIdx(a, b)] += val;
                        }
                    }

                    // Spin contribution: (3/r³) ε_{kl(i} S^l n_{j)} n^k
                    Real S[3] = {bh.spin[0], bh.spin[1], bh.spin[2]};
                    Real inv_r3 = inv_r2 / r;

                    // ε_{kli} S^l n_j n^k (symmetrized over ij)
                    // Using Levi-Civita: ε_{012}=1, etc.
                    auto levi = [](int a, int b, int c) -> Real {
                        if ((a==0&&b==1&&c==2)||(a==1&&b==2&&c==0)||(a==2&&b==0&&c==1))
                            return 1.0;
                        if ((a==0&&b==2&&c==1)||(a==1&&b==0&&c==2)||(a==2&&b==1&&c==0))
                            return -1.0;
                        return 0.0;
                    };

                    for (int ii = 0; ii < 3; ++ii) {
                        for (int jj = ii; jj < 3; ++jj) {
                            Real spin_term = 0.0;
                            for (int kk = 0; kk < 3; ++kk) {
                                for (int ll = 0; ll < 3; ++ll) {
                                    spin_term += levi(kk, ll, ii) * S[ll] * n[jj] * n[kk]
                                               + levi(kk, ll, jj) * S[ll] * n[ii] * n[kk];
                                }
                            }
                            Atilde[symIdx(ii, jj)] += 3.0 * inv_r3 * 0.5 * spin_term;
                        }
                    }
                }

                // Write to grid (conformal traceless extrinsic curvature)
                grid.data(static_cast<int>(SpacetimeVar::A_XX), i, j, k) = Atilde[0];
                grid.data(static_cast<int>(SpacetimeVar::A_XY), i, j, k) = Atilde[1];
                grid.data(static_cast<int>(SpacetimeVar::A_XZ), i, j, k) = Atilde[2];
                grid.data(static_cast<int>(SpacetimeVar::A_YY), i, j, k) = Atilde[3];
                grid.data(static_cast<int>(SpacetimeVar::A_YZ), i, j, k) = Atilde[4];
                grid.data(static_cast<int>(SpacetimeVar::A_ZZ), i, j, k) = Atilde[5];
            }
        }
    }
}

Real BowenYorkPuncture::admMass() const
{
    Real M = 0.0;
    for (const auto& bh : bhs_) M += bh.mass;
    return M;
}

std::array<Real, DIM> BowenYorkPuncture::admAngularMomentum() const
{
    std::array<Real, DIM> J = {0, 0, 0};
    for (const auto& bh : bhs_) {
        J[0] += bh.spin[0];
        J[1] += bh.spin[1];
        J[2] += bh.spin[2];
    }
    return J;
}

// ===========================================================================
// Superposed Kerr-Schild (stub)
// ===========================================================================

SuperposedKerrSchild::SuperposedKerrSchild(const std::vector<BlackHoleParams>& bhs)
    : bhs_(bhs) {}

Real SuperposedKerrSchild::kerrSchildH(Real mass, Real spin_a,
                                       Real x, Real y, Real z)
{
    // Kerr-Schild scalar for a BH with mass M and spin a along z
    // H = Mr³ / (r⁴ + a²z²)
    // where r is the Kerr radial coordinate satisfying:
    // x² + y² + z² = r² + a² - a²z²/r²
    Real a2 = spin_a * spin_a;
    Real rho2 = x*x + y*y + z*z - a2;
    Real r2 = 0.5 * (rho2 + std::sqrt(rho2*rho2 + 4.0*a2*z*z));
    Real r = std::sqrt(r2 + 1.0e-30);
    return mass * r * r2 / (r2*r2 + a2*z*z + 1.0e-30);
}

void SuperposedKerrSchild::apply(GridBlock& grid) const
{
    const int nx = grid.totalCells(0);
    const int ny = grid.totalCells(1);
    const int nz = grid.totalCells(2);

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                Real x = grid.x(0, i);
                Real y = grid.x(1, j);
                Real z = grid.x(2, k);

                Real g[3][3] = {{1,0,0}, {0,1,0}, {0,0,1}};
                Real shift[3] = {0,0,0};
                Real H_total = 0.0;
                
                for (const auto& bh : bhs_) {
                    Real dx_ = x - bh.position[0];
                    Real dy_ = y - bh.position[1];
                    Real dz_ = z - bh.position[2];
                    
                    Real a = bh.spin[2] / (bh.mass + 1e-30); 
                    Real H = kerrSchildH(bh.mass, a, dx_, dy_, dz_);
                    H_total += H;
                    
                    Real rho2 = dx_*dx_ + dy_*dy_ + dz_*dz_ - a*a;
                    Real r2 = 0.5 * (rho2 + std::sqrt(rho2*rho2 + 4.0*a*a*dz_*dz_));
                    Real r = std::sqrt(r2 + 1e-30);
                    
                    Real l[3] = {
                        (r * dx_ + a * dy_) / (r2 + a*a),
                        (r * dy_ - a * dx_) / (r2 + a*a),
                        dz_ / r
                    };
                    
                    for(int ii=0; ii<3; ++ii) {
                        for(int jj=0; jj<3; ++jj) {
                            g[ii][jj] += 2.0 * H * l[ii] * l[jj];
                        }
                    }
                    for(int ii=0; ii<3; ++ii) {
                        shift[ii] += 2.0 * H * l[ii];
                    }
                }

                Real detg = g[0][0]*(g[1][1]*g[2][2] - g[1][2]*g[2][1])
                          - g[0][1]*(g[1][0]*g[2][2] - g[1][2]*g[2][0])
                          + g[0][2]*(g[1][0]*g[2][1] - g[1][1]*g[2][0]);
                          
                Real chi = std::pow(detg, -1.0/3.0);
                Real alpha = 1.0 / std::sqrt(1.0 + 2.0 * H_total);

                grid.data(static_cast<int>(SpacetimeVar::LAPSE), i, j, k) = alpha;
                grid.data(static_cast<int>(SpacetimeVar::CHI), i, j, k) = chi;
                
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_XX), i, j, k) = chi * g[0][0];
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_XY), i, j, k) = chi * g[0][1];
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_XZ), i, j, k) = chi * g[0][2];
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_YY), i, j, k) = chi * g[1][1];
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_YZ), i, j, k) = chi * g[1][2];
                grid.data(static_cast<int>(SpacetimeVar::GAMMA_ZZ), i, j, k) = chi * g[2][2];
                
                grid.data(static_cast<int>(SpacetimeVar::SHIFT_X), i, j, k) = alpha * alpha * shift[0];
                grid.data(static_cast<int>(SpacetimeVar::SHIFT_Y), i, j, k) = alpha * alpha * shift[1];
                grid.data(static_cast<int>(SpacetimeVar::SHIFT_Z), i, j, k) = alpha * alpha * shift[2];
            }
        }
    }
}

// ===========================================================================
// Stellar initial data
// ===========================================================================

StellarInitialData::StellarInitialData(const std::vector<StarParams>& stars)
    : stars_(stars) {}

StellarInitialData::StellarProfile
StellarInitialData::solvePolytrope(const StarParams& star) const
{
    // Solve the Lane-Emden equation for a polytrope: p = K ρ^Γ
    // Using the dimensionless form: (1/ξ²) d/dξ (ξ² dθ/dξ) = -θ^n
    // where n = 1/(Γ-1), ρ = ρ_c θ^n, ξ = r/α with α = √(K(n+1)ρ_c^{1/n-1}/(4π))

    const Real Gamma = star.polytropic_gamma;
    const Real n = 1.0 / (Gamma - 1.0);
    const Real rho_c = star.central_density;
    const Real K = star.polytropic_K;

    // Characteristic length scale
    Real alpha_scale = std::sqrt(
        (n + 1.0) * K * std::pow(rho_c, 1.0/n - 1.0) /
        (4.0 * constants::PI * constants::G_CGS)
    );

    // Integrate Lane-Emden with RK4
    const int N_steps = 10000;
    const Real dxi = 0.001;

    StellarProfile profile;
    Real theta = 1.0;       // θ(0) = 1
    Real dtheta = 0.0;      // dθ/dξ(0) = 0
    Real enclosed_mass = 0.0;

    for (int step = 0; step < N_steps; ++step) {
        Real xi = step * dxi + 1.0e-10;
        Real r = xi * alpha_scale;

        Real rho = rho_c * std::pow(std::max(theta, 0.0), n);
        Real p = K * std::pow(rho, Gamma);
        Real eps = p / (rho * (Gamma - 1.0) + 1.0e-30);

        if (theta <= 0.0 || r > star.radius * constants::RSUN_CGS) break;

        profile.r.push_back(r);
        profile.rho.push_back(rho);
        profile.press.push_back(p);
        profile.eps.push_back(eps);
        enclosed_mass += 4.0 * constants::PI * rho * r * r * alpha_scale * dxi;
        profile.mass.push_back(enclosed_mass);

        // RK4 step for Lane-Emden
        auto f_theta = [](Real, Real dth) { return dth; };
        auto f_dtheta = [n](Real xi_val, Real th, Real dth) {
            if (xi_val < 1.0e-10) return -th * th * th / 3.0; // L'Hôpital at origin
            return -std::pow(std::max(th, 0.0), n) - 2.0 * dth / xi_val;
        };

        Real k1_t = dxi * f_theta(xi, dtheta);
        Real k1_d = dxi * f_dtheta(xi, theta, dtheta);
        Real k2_t = dxi * f_theta(xi + 0.5*dxi, dtheta + 0.5*k1_d);
        Real k2_d = dxi * f_dtheta(xi + 0.5*dxi, theta + 0.5*k1_t, dtheta + 0.5*k1_d);
        Real k3_t = dxi * f_theta(xi + 0.5*dxi, dtheta + 0.5*k2_d);
        Real k3_d = dxi * f_dtheta(xi + 0.5*dxi, theta + 0.5*k2_t, dtheta + 0.5*k2_d);
        Real k4_t = dxi * f_theta(xi + dxi, dtheta + k3_d);
        Real k4_d = dxi * f_dtheta(xi + dxi, theta + k3_t, dtheta + k3_d);

        theta  += (k1_t + 2*k2_t + 2*k3_t + k4_t) / 6.0;
        dtheta += (k1_d + 2*k2_d + 2*k3_d + k4_d) / 6.0;
    }

    return profile;
}

StellarInitialData::StellarProfile
StellarInitialData::solveTOV(const StarParams& star) const
{
    // TOV equations:
    // dp/dr = -(ρ + p/c²)(m + 4πr³p/c²) / (r(r - 2Gm/c²))
    // dm/dr = 4πρr²

    const Real rho_c = star.central_density;
    const Real Gamma = star.polytropic_gamma;
    const Real K_poly = star.polytropic_K;

    const Real G = constants::G_CGS;
    const Real c2 = constants::C_CGS * constants::C_CGS;

    // star.radius is in km (neutron star scale); convert to cm.
    const Real R_cm = star.radius * 1.0e5;  // km -> cm
    const int N_steps = 50000;
    const Real dr = R_cm / N_steps;

    StellarProfile profile;
    Real p = K_poly * std::pow(rho_c, Gamma);
    Real m = 0.0;
    const Real p0 = p; // central pressure for termination check

    for (int step = 0; step < N_steps; ++step) {
        Real r = (step + 0.5) * dr;
        if (r < 1.0e-5) r = 1.0e-5;

        Real rho = std::pow(std::max(p / K_poly, 0.0), 1.0/Gamma);
        Real eps = (rho > 1.0e-30) ? p / (rho * (Gamma - 1.0)) : 0.0;

        if (p <= 0.0 || rho <= 0.0) break;

        profile.r.push_back(r);
        profile.rho.push_back(rho);
        profile.press.push_back(p);
        profile.eps.push_back(eps);
        profile.mass.push_back(m);

        // TOV equations (in CGS)
        Real Schwarzschild_term = r - 2.0 * G * m / c2;
        Real denom = r * Schwarzschild_term;
        if (std::abs(denom) < 1.0e-30 || Schwarzschild_term <= 0.0) break;

        Real dp_dr = -(rho + p/c2) * (m + 4.0*constants::PI*r*r*r*p/c2) * G / denom;
        Real dm_dr = 4.0 * constants::PI * rho * r * r;

        p += dp_dr * dr;
        m += dm_dr * dr;

        if (p < 0.0 || p < 1.0e-10 * p0) break;
    }

    return profile;
}

void StellarInitialData::apply(GridBlock& spacetime_grid,
                               GridBlock& hydro_grid) const
{
    for (const auto& star : stars_) {
        StellarProfile profile;
        if (star.model == StellarModel::POLYTROPE) {
            profile = solvePolytrope(star);
        } else if (star.model == StellarModel::TOV) {
            profile = solveTOV(star);
        }
        // else: MESA_TABLE — TODO

        if (profile.r.empty()) continue;

        Real R_star = profile.r.back();

        const int nx = hydro_grid.totalCells(0);
        const int ny = hydro_grid.totalCells(1);
        const int nz = hydro_grid.totalCells(2);

        for (int k = 0; k < nz; ++k) {
            for (int j = 0; j < ny; ++j) {
                for (int i = 0; i < nx; ++i) {
                    Real x = hydro_grid.x(0, i) - star.position[0];
                    Real y = hydro_grid.x(1, j) - star.position[1];
                    Real z = hydro_grid.x(2, k) - star.position[2];
                    Real r = std::sqrt(x*x + y*y + z*z);

                    if (r > R_star) continue;

                    // Linear interpolation in the profile
                    std::size_t idx = 0;
                    for (std::size_t n = 0; n < profile.r.size() - 1; ++n) {
                        if (r >= profile.r[n] && r < profile.r[n+1]) {
                            idx = n;
                            break;
                        }
                    }

                    Real frac = (r - profile.r[idx]) /
                                (profile.r[idx+1] - profile.r[idx] + 1e-30);
                    Real rho = profile.rho[idx] + frac *
                               (profile.rho[idx+1] - profile.rho[idx]);
                    Real p   = profile.press[idx] + frac *
                               (profile.press[idx+1] - profile.press[idx]);
                    Real eps = profile.eps[idx] + frac *
                               (profile.eps[idx+1] - profile.eps[idx]);

                    hydro_grid.data(static_cast<int>(PrimitiveVar::RHO), i, j, k) = rho;
                    hydro_grid.data(static_cast<int>(PrimitiveVar::PRESS), i, j, k) = p;
                    hydro_grid.data(static_cast<int>(PrimitiveVar::EPS), i, j, k) = eps;
                    hydro_grid.data(static_cast<int>(PrimitiveVar::TEMP), i, j, k) =
                        star.temperature;
                    hydro_grid.data(static_cast<int>(PrimitiveVar::YE), i, j, k) =
                        star.Ye;
                }
            }
        }

        // Add seed magnetic field
        addMagneticField(hydro_grid, star);
    }
}

void StellarInitialData::addMagneticField(GridBlock& hydro_grid,
                                          const StarParams& star) const
{
    const int nx = hydro_grid.totalCells(0);
    const int ny = hydro_grid.totalCells(1);
    const int nz = hydro_grid.totalCells(2);

    Real B0 = star.B_field_seed;
    Real R_star = star.radius * constants::RSUN_CGS;

    for (int k = 0; k < nz; ++k) {
        for (int j = 0; j < ny; ++j) {
            for (int i = 0; i < nx; ++i) {
                Real x = hydro_grid.x(0, i) - star.position[0];
                Real y = hydro_grid.x(1, j) - star.position[1];
                Real z = hydro_grid.x(2, k) - star.position[2];
                Real r = std::sqrt(x*x + y*y + z*z + 1e-30);

                if (r > R_star) continue;

                // Dipolar field: B = B0 (R/r)³ [2 cos(θ) r̂ + sin(θ) θ̂]
                // In Cartesian: Bz dominates at center
                Real ratio = (r < 1e-10) ? 1.0 : std::pow(R_star / r, 3);
                Real cos_th = z / r;
                Real sin_th = std::sqrt(x*x + y*y) / r;

                // Simplified: uniform field B0 ẑ (inside star)
                // (full dipole requires vector potential for div-free)
                hydro_grid.data(static_cast<int>(PrimitiveVar::BZ), i, j, k) = B0;
            }
        }
    }
}

// ===========================================================================
// Benchmark scenario setup
// ===========================================================================

void setupBenchmarkScenario(GridBlock& spacetime_grid,
                            GridBlock& hydro_grid,
                            Real Mbh, Real Mstar, Real R0, int N)
{
    // Create N BHs at regular polygon vertices
    std::vector<BlackHoleParams> bhs(N);
    for (int A = 0; A < N; ++A) {
        Real angle = 2.0 * constants::PI * A / N;
        bhs[A].mass = Mbh;
        bhs[A].position = {R0 * std::cos(angle),
                           R0 * std::sin(angle),
                           0.0};
        bhs[A].momentum = {0.0, 0.0, 0.0};
        bhs[A].spin     = {0.0, 0.0, 0.0};
    }

    // Set BH spacetime
    BrillLindquist bl(bhs);
    bl.apply(spacetime_grid);

    // Create 2 stars at the center
    std::vector<StarParams> stars(2);
    for (int s = 0; s < 2; ++s) {
        stars[s].mass           = Mstar;
        stars[s].radius         = 500.0; // R_sun
        stars[s].position       = {0.0, 0.0, 0.0};
        stars[s].model          = StellarModel::POLYTROPE;
        stars[s].polytropic_gamma = 4.0 / 3.0;
        stars[s].central_density  = 1.0; // g/cm³
        stars[s].B_field_seed     = 1.0e4; // G
    }

    StellarInitialData stellar(stars);
    stellar.apply(spacetime_grid, hydro_grid);
}

} // namespace granite::initial_data
