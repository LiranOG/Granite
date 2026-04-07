# GRANITE Diagnostic Handbook: Interpreting Simulation Telemetry

---

## 1. Introduction: The Pulse of the Grid

In the high-stakes architecture of numerical relativity, monitoring a simulation is not a passive observation of a progress bar; it is an active interrogation of spacetime. As we evolve the Einstein field equations via the CCZ4 formalism, we are not merely running code — we are maintaining the structural integrity of a digital universe.

To master the GRANITE engine, the researcher must adopt a posture of **epistemological discipline**. You are a numerical architect, and the telemetry is the "pulse" of your grid. If the physics begins to fail, the signals appear long before the terminal crash. We evaluate simulation health through three primary pillars:

1. **Gauge Stability ($\alpha$):** Ensuring our coordinate observers do not "crunch" or oscillate, maintaining a stable "Trumpet" geometry.
2. **Physical Validity ($\|H\|_2$):** Verifying that the Hamiltonian constraint remains near zero, ensuring the simulation stays within Epistemic Tier B (testable structural correspondence) rather than devolving into Tier D (metaphysical nonsense).
3. **Numerical Integrity (NaN Forensics):** Detecting the first signs of "numerical infection" — Not-a-Number values that signal a total system divergence.

> [!NOTE]
> The grid is a witness to your math; the following sections teach you how to hear its testimony.

---

## 2. Anatomy of the GRANITE Live Dashboard

The Universal Live Dashboard is your primary diagnostic window. Below is the standard telemetry output provided by `sim_tracker.py` and the core C++ engine.

| Field Name | Physical Meaning | Health Indicators |
|---|---|---|
| `step` | Iteration count. | — |
| `t` | Simulation time in Geometric Mass (M). | — |
| `α_center` | Central Lapse (VAR 18). The "rate of time" at the coordinate center. | `[HEALTHY]`, `[COLLAPSE]`, `[RECOVER]` |
| `‖H‖₂` | Hamiltonian Constraint (L2 Norm). Deviation from Einstein's equations. | `[OK]` (<0.5), `[HIGH]` (0.5–2.0), `[CRIT]` (>10) |
| `speed` | Throughput in M per wall-clock second (M/s). | Signal of Computational Density. |
| `ETA` | Estimated time remaining. | Reflects Berger-Oliger overhead. |

### The "So What?" of Speed and Computational Density

In GRANITE, **speed is a physical diagnostic**. A sharp drop in M/s usually coincides with the expansion of Adaptive Mesh Refinement (AMR). When the physics becomes "violent" — such as a binary black hole (BBH) merger — the engine creates more blocks to resolve steep gradients. This increases the Berger-Oliger subcycling overhead.

> [!IMPORTANT]
> If speed stalls while $\|H\|_2$ grows, the AMR is failing to resolve the gradient, leading to "numerical stalling." Your hardware is being outpaced by the complexity of the spacetime curvature.

---

## 3. Gauge Stability: The Story of the Lapse ($\alpha$)

In moving-puncture simulations, the Lapse ($\alpha$) represents the "flow of time" relative to the grid. A healthy puncture follows a specific **Lapse Life-Cycle**:

1. **Initial State:** $\alpha = 1.0$. Spacetime is flat; time flows normally.
2. **Lapse Collapse:** $\alpha$ drops precipitously to $\approx 0.003$. This signals that the coordinates have "frozen" near the puncture to avoid the singularity.
3. **Trumpet Stability:** The lapse recovers and asymptotes toward $\approx 0.3$. This recovery is critical — it indicates the coordinate system has reached a stationary "Trumpet" geometry.

### Diagnostic Contrast: SP5 vs. 2BH

**The Gold Standard (SP5):** At step 25, we see $\alpha = 0.27060$ and recovering. This is a "Trumpet Stable" gauge, allowing the simulation to run indefinitely.

> [!CAUTION]
> **Mathematical Delirium (2BH):** In `DEV_LOG_2BH_2.txt`, the lapse reaches $2.19 \times 10^9$ at step 6. This is nonsensical. Once the lapse exceeds $1.0$ in a puncture run, the gauge has shattered. The coordinates are no longer mapping a physical manifold.

---

## 4. The Hamiltonian Constraint ($\|H\|_2$): Measuring Accuracy

The Hamiltonian constraint ($\|H\|_2$) is the "Law of Gravity" for your simulation. In a perfect universe, it is zero. In our grid, it is the measure of our sin.

| Level | Threshold | Meaning |
|---|---|---|
| **HEALTHY** | $< 0.5$ | The Einstein equations are well-satisfied. |
| **WARNING** | $0.5 – 2.0$ | Numerical noise is increasing; the "last warning" before instability. |
| **CRITICAL** | $> 10.0$ | Physical validity is lost. The simulation has drifted into Tier D. |
| **CRASH** | NaN / $\infty$ | The math has exploded. |

### Forensic Analysis of a "Constraint Explosion"

In the 2BH log, look at the transition from Step 2 to Step 4. At step 2, $\|H\|_2 = 7.11 \times 10^{-2}$ (labeled `[HIGH]`). **This is the architect's final chance to intervene.** By step 4, it has jumped to $3.12 \times 10^{40}$.

> [!WARNING]
> This is not a gradual drift; it is a **Constraint Explosion**. This typically identifies a failure in the CCZ4 damping parameters ($\kappa$) or a catastrophic CFL violation, where the time step $dt$ is too large to resolve the spatial speed of the gauge waves.

---

## 5. NaN Forensics: Tracking Numerical Infection

A NaN (Not-a-Number) is not a crash; it is an **infection**. NaN Forensics is the process of locating "Patient Zero."

### The "Clean Summary" Paradox

In `DEV_LOG_2BH_2.txt`, a paradox exists: the step log shows $\|H\|_2 = \text{NaN}$, yet the Final Summary claims "No NaN events detected ✓".

> [!IMPORTANT]
> **Pro-Tip:** Manual log inspection always supersedes summary reports. This discrepancy occurs when a crash is so catastrophic (e.g., $10^{43}$ CFL guards) that it bypasses the internal diagnostic buffers, or the engine terminates before the tracker can flush the event to the summary.

### Forensic Checklist

1. **Check the RHS:** Ensure Spacetime RHS and Hydro RHS were "all finite" at $t = 0$.
2. **Identify the Source:** Which variable failed first?
   - $\chi$ **(VAR 0):** Often fails at the puncture due to insufficient resolution.
   - $\alpha$ **(VAR 18):** Gauge failure or "Lapse hit floor."
3. **Locate the Grid Point:** The `(i, j, k)` coordinate tells you where the infection started.
   - If it's at the **boundary** → check your Sommerfeld conditions.
   - If it's at the **center** → check your AMR resolution.

---

## 6. AMR and Grid Health

Adaptive Mesh Refinement (AMR) is the architect's primary tool for resolving "violent" physics. GRANITE uses **Tracking Spheres** to force high resolution around moving punctures.

In the 2BH log, note the creation of "Level 2" merged blocks at `(0, 0, 0.1)`. This is not random; it corresponds exactly to the user-defined `Tracking sphere @ (0,0,0.1) R=0.5`.

> [!WARNING]
> If the simulation fails at a Tracking Sphere location, it means the sphere is too small or the resolution `dx` is insufficient to capture the gradient. The **CFL Guard Events** in the 2BH run (showing values like $10^{14}$ and $10^{43}$) are the "smoking gun" — the time-step has become unphysical because the grid cannot resolve the curvature.

---

## 7. The Health Check Checklist

| Diagnostic Check | Ideal Result | Failure Signal |
|---|---|---|
| **CFL Guard Events** | 0 events | Values > 1.0 (e.g., $10^{43}$) — "Mathematical Delirium." |
| **NaN Forensics** | "No NaN events detected" | Any NaN in Spacetime RHS; check VAR 18 or VAR 0. |
| **State Freeze** | "No zombie state detected" | Zombie State: time $t$ stops while `step` increases. |
| **Stability Diagnosis** | Growth rate $\gamma \approx 0$ | Exponential growth in $\|H\|_2$ between steps. |
| **Lapse Status** | "Trumpet stable" | $\alpha$ exploding to $10^9$ or failing to recover from 0.003. |
| **Epistemic Tier** | Tier B | Deviation to Tier D (physical validity lost). |

---

## 8. Closing: The Epistemological Boundary

As a Lead Architect, I remind you: **"Doubt is the conscience of consciousness."** In numerical relativity, a "successful" simulation is not one that merely finishes — it is one that maintains **Epistemological Discipline** through every M of time.

> [!IMPORTANT]
> If your constraints explode, your simulation is no longer an analog of the universe; it is a collection of meaningless bits. A "Healthy" result requires **Tier B verification** — directly testable structural correspondence. When the telemetry screams, listen.
>
> **The grid does not lie, and a NaN is the universe's way of telling you that your math no longer belongs to reality.**
