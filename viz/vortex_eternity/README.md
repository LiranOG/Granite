<div align="center">

# VORTEX ETERNITY 🌀
### **The Zero-Allocation Numerical Relativity WebGL Frontend**

[![Engine](https://img.shields.io/badge/Engine-Custom_WebGL-blue.svg)]()
[![Integrator](https://img.shields.io/badge/Integrator-Hermite--4-purple.svg)]()
[![Precision](https://img.shields.io/badge/Precision-Kahan_Summation-red.svg)]()
[![Physics](https://img.shields.io/badge/Physics-2.5PN_Relativity-green.svg)]()

</div>

## 📖 Abstract

**VORTEX ETERNITY** is an elite, high-performance N-Body visualization and simulation engine operating entirely within the browser. Designed as the vanguard frontend for the **GRANITE** ecosystem, VORTEX bridges the gap between intense computational astrophysics and frictionless, real-time 3D rendering. 

Operating strictly on a **Zero-Allocation Architecture** (mutating pre-allocated mathematical vectors in-place), VORTEX completely bypasses JavaScript Garbage Collection stalls, allowing for seamless 60 FPS integration of highly non-linear orbital dynamics, strong-field relativity approximations, and massive particle swarms.

---

> [!IMPORTANT]
>### 🛠️ Status & Developer’s Note
>
>***VORTEX ETERNITY*** was born out of a spontaneous and intense 48-hour development sprint. While I have pushed the limits to ensure the engine is physically realistic, numerically stable, and architecturally sound, it is important to note that it is not yet "100% perfect." 
>
>In such a rapid development cycle, minor bugs or edge-case anomalies may exist. However, every line of code was written with a commitment to high-fidelity physics and maximum performance. I am currently balancing the simultaneous development of both the **GRANITE** backend and the **VORTEX** frontend, along with several other critical subsystems. 
>
>I do not have ten hands, but I am putting every bit of my energy and expertise into this project. As development continues, I will be refining, patching, and evolving VORTEX until it reaches absolute perfection.
>
>My commitment to this massive project goes beyond just "doing my best"—it is a mission to create a tool that will fundamentally transform the way we conduct and visualize astrophysical research.

---

## ⚙️ Core Architecture & Physics Engine

VORTEX is not a simple Newtonian gravity simulator. It is an actively dissipative, post-Newtonian relativistic engine designed to model the extreme dynamics of compact objects (Black Holes, Neutron Stars) in the strong-field regime.

### 1. The Integrator: Hermite 4th-Order Predictor-Corrector
Standard Runge-Kutta methods fail to maintain symplectic stability in highly chaotic N-Body environments. VORTEX employs the **Hermite 4th-Order Predictor-Corrector** scheme (Makino & Aarseth 1992), which computes both acceleration ($a$) and its time derivative, the jerk ($\dot{a}$).
* **Aarseth Adaptive Timestepping:** The integration step dynamically scales according to $\Delta t = \eta \sqrt{|a|/|\dot{a}|}$ to flawlessly resolve ultra-close encounters without energy blow-up.

### 2. Numerical Resilience
* **Kahan Compensated Summation:** Global Hamiltonian energy accumulators use Kahan summation to eliminate $O(N \cdot \epsilon_{mach})$ catastrophic cancellation typical in IEEE-754 floating-point arithmetic.
* **NaN-Shielding & Bisection Recovery:** If a singularity causes numerical overflow, the engine catches the `NaN` state, reverts to the previous step, and bisects the timestep up to 6 depth levels. If the singularity persists, the corrupted body is surgically excised to preserve the global simulation.

### 3. Post-Newtonian (PN) Relativity
VORTEX dynamically expands Newtonian gravity with analytically derived post-Newtonian terms:
* **1PN (Einstein-Infeld-Hoffmann):** Conservative corrections of order $(v/c)^2$ accounting for perihelion precession and relativistic mass-energy equivalence.
* **1.5PN (Lense-Thirring Spin-Orbit):** Implements Barker-O'Connell frame-dragging. Spin vectors actively perturb the orbital plane. The intrinsic spin of bodies is evolved using the exact **Rodrigues' rotation formula**, completely avoiding Euler-step magnitude inflation.
* **2.5PN (Radiation Reaction):** Dissipative terms simulating the emission of gravitational waves, driving binary systems to inspiral and eventually merge.

---

## 🔭 Astrophysical Phenomena

* **Mass-Defect Mergers & GW Recoil:** Upon collision of compact objects, VORTEX computes the mass radiated away as gravitational waves ($\Delta M_{rad} \approx 0.048 (4\eta)^2 M$). Momentum conservation dictates the resulting asymmetric GW recoil kick, which can eject the remnant from the host system.
* **Tidal Disruption Events (TDE):** Calculated strictly via the physical Roche Limit ($d \le 2.44 R (M/m)^{1/3}$). When a star crosses an SMBH's Roche limit, it undergoes spaghettification, generating a Novikov-Thorne accretion disk and triggering intense localized shockwaves.
* **Quasi-Normal Modes (QNM):** Following a black hole merger, the engine calculates the fundamental ringdown frequency ($\omega$) and damping time ($\tau$) of the newly formed Kerr black hole.

---

## 📊 Live Telemetry Matrix (Dashboard Guide)

The right-side control panel acts as your Mission Control. Below is the strict physical definition of every telemetry metric displayed in real-time:

### Global System Metrics
| Metric | Description |
|:---|:---|
| **Hamiltonian $H(q,p)$** | The total invariant energy of the system. Tracked via Kahan summation. |
| **Symplectic Error** $|\Delta E/E_0|$ | The absolute fractional drift of the Hamiltonian. A value $< 10^{-6}$ indicates excellent integrator stability. |
| **Geometric Lapse** $\alpha_{min}$ | Derived from $\sqrt{1 - 2\Phi/c^2}$. Measures the maximal time dilation in the simulation. $\alpha \to 0$ indicates approach to an event horizon. |
| **PN Parameter** $x$ | $max(v^2/c^2, GM/rc^2)$. The strength of relativistic effects. If $x > 0.1$, the PN approximation begins to break down, necessitating full CCZ4 numerical relativity (via GRANITE backend). |

### Dominant Binary & Gravitational Waves
The engine automatically detects the most gravitationally bound pair and tracks their specific dynamics:
| Metric | Description |
|:---|:---|
| **$L_{GW}$ (Peters Quad.)** | The total gravitational wave luminosity radiating from the system. |
| **$M_{rad}$ (Mass Defect)** | The cumulative physical mass converted into pure gravitational wave energy over the simulation's lifetime. |
| **Strain $h_+, h_\times$** | The instantaneous quadrupole gravitational wave strain components. |
| **$f_{GW}$** | The dominant emission frequency of the gravitational waves. |
| **Chirp Mass & $T_{merge}$** | $M_c = (m_1 m_2)^{3/5} / (m_1+m_2)^{1/5}$. Used alongside Peters' timescale equations to predict the exact time until the binary inspirals and merges. |
| **$|S_{total}|$ & $\chi_{eff}$** | The total spin angular momentum vector magnitude, and the effective dimensionless spin parameter projected onto the orbital angular momentum axis. |

---

## 🎮 Interaction & Controls

VORTEX is designed for total user interactivity.

### Camera & Flight Modes
* **Free Orbit:** Standard OrbitControls mapping (Left Click = Rotate, Right Click = Pan, Scroll = Zoom).
* **Track CoM:** Camera smoothly interpolates to track the barycenter of the entire system.
* **Binary Tracking:** Locks focus strictly on the center of mass of the dominant binary.
* **WASD Flight Mode (FPS):** Toggle with `E`. Dive into the simulation like a drone.
  * `W/A/S/D` = Translation
  * `Mouse` = Look (Pointer Locked)
  * `Shift` = Sprint ($3.5\times$ speed)
  * `Space` = Precision Creep ($0.15\times$ speed)
  * `Esc` = Exit Flight Mode

### The Sandbox & Solar Forge
Toggle **Sandbox Mode** (`N`) to pause the simulation and enter the Solar Forge. 
1. **Select a Template:** Choose from Stars, Neutron Stars, Black Holes (SMBH), or Planets.
2. **Tune Parameters:** Adjust Mass, Radius, and Spin ($\chi$).
3. **Place (Hologram Mode):** Click anywhere on the geometric $Y=0$ plane to place the body. 
4. **Drag for Velocity:** Dragging away from the placement point applies a velocity vector. The engine displays a live **Keplerian Osculating Orbit** prediction (Ellipse, Parabola, or Hyperbola) to help you achieve stable circularization before engaging physics.

### Visual Modifiers
* **Gravitational Lensing:** Toggle (`L`). Bends background starfield light around compact objects based on their Schwarzschild compactness ($C = GM/c^2 R \ge 0.25$).
* **MACRO-COSMOS:** Expands the simulation bounds by $5\times$, optimizing fog, bloom, and grid scales for ultra-wide orbital systems (e.g., the Oort cloud or outer Solar System).

---

## 🔮 The v1.0 Architectural Roadmap

Currently, VORTEX solves its own dynamics via Post-Newtonian expansions. However, its ultimate destination is to serve as the unified visualization layer for the **GRANITE** supercomputing backend.

In upcoming releases (v1.0), the intensely heavy PDE workload—solving the full CCZ4 formulation and Valencia GRMHD equations on Adaptive Mesh Refinement (AMR) hierarchies—will remain exclusively within the C++ backend. 

VORTEX will transition to a **3D Playback Dashboard**. Utilizing our Python toolchain (`granite_analysis`), raw HDF5 tensor data will be distilled into lightweight JSON kinematic streams. VORTEX will ingest these streams, rendering mathematically exact supercomputer trajectories, apparent horizon shapes, and $\Psi_4$ wave strains seamlessly in the browser. 

*If future resource constraints allow, VORTEX will be upgraded with a WebSocket layer to allow Real-Time In-Situ Steering of the running HPC cluster directly from the WebGL interface.*
