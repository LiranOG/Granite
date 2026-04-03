#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        GRANITE sim_tracker.py — Universal Live Simulation Tracker          ║
║        Append-only colorful log + professional exhaustive summary          ║
╚══════════════════════════════════════════════════════════════════════════════╝

Parses live output from ANY granite benchmark and provides:
  • Append-only step-by-step color-coded diagnostics (no cursor clearing)
  • Real-time phase classification (Inspiral, Merger, Ringdown ...)
  • AMR block count tracking and zombie-state detection
  • Constraint growth rate (γ = d ln‖H‖₂/dt) computed per step
  • Simulation speed [M/s] and ETA
  • NaN forensics with variable identification and propagation tracking
  • Full statistical summary on exit (Ctrl+C or natural end)
  • Optional matplotlib plots saved to dev_logs/

Usage:
    # Launch granite and track it:
    python3 scripts/sim_tracker.py ./build/granite benchmarks/B2_eq.yaml

    # Track any benchmark by name (looks in benchmarks/<name>.yaml):
    python3 scripts/sim_tracker.py --benchmark B2_eq

    # Track a running granite process via pipe:
    ./build/granite benchmarks/B2_eq.yaml 2>&1 | python3 scripts/sim_tracker.py --stdin

    # Disable colors (for log files):
    python3 scripts/sim_tracker.py --benchmark single_puncture --no-color

Press Ctrl+C at any time for a full summary and exit.
Logs saved to: dev_logs/sim_tracker_<timestamp>.log
"""

import subprocess
import sys
import os
import re
import time
import signal
import argparse
import math
from datetime import datetime, timedelta
from collections import deque

# ── OUTPUT DIRECTORY ──────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DEV_LOGS_DIR = os.path.join(PROJECT_ROOT, "dev_logs")
os.makedirs(DEV_LOGS_DIR, exist_ok=True)

# ── ANSI COLORS ──────────────────────────────────────────────────────────────
R   = "\033[91m"    # Red
Y   = "\033[93m"    # Yellow
G   = "\033[92m"    # Green
B   = "\033[94m"    # Blue
M   = "\033[95m"    # Magenta
C   = "\033[96m"    # Cyan
W   = "\033[97m"    # White
DIM = "\033[2m"     # Dim
RST = "\033[0m"     # Reset
BLD = "\033[1m"     # Bold
UND = "\033[4m"     # Underline

def supports_color():
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

USE_COLOR = supports_color()

def c(text, *codes):
    if not USE_COLOR:
        return str(text)
    return "".join(codes) + str(text) + RST

def sep(char="─", width=74, color=DIM):
    return c(char * width, color)

# ── PHYSICS THRESHOLDS ────────────────────────────────────────────────────────
ALPHA_TRUMPET  = 0.30    # lapse asymptotes here in moving-puncture gauge
ALPHA_WARN     = 0.05    # lapse below this → deep collapse
ALPHA_FLOOR    = 1.0e-4  # numerical floor — crash imminent
H_HEALTHY      = 0.5e-3  # ‖H‖₂ below this → excellent
H_WARNING      = 1.0e-2  # ‖H‖₂ above this → growing
H_CRITICAL     = 0.1     # ‖H‖₂ above this → constraint explosion
ZOMBIE_WINDOW  = 6       # steps to check for frozen state
ZOMBIE_TOL     = 1.0e-7  # min change in α or H to not be "zombie"

# ── VARIABLE NAME MAPS ────────────────────────────────────────────────────────
ST_VAR_NAMES = {
    0:  "CHI (χ — conformal factor)",
    1:  "GAMMA_XX (γ̃_xx)",  2: "GAMMA_XY (γ̃_xy)",  3: "GAMMA_XZ (γ̃_xz)",
    4:  "GAMMA_YY (γ̃_yy)",  5: "GAMMA_YZ (γ̃_yz)",  6: "GAMMA_ZZ (γ̃_zz)",
    7:  "A_XX (Ã_xx)",       8: "A_XY (Ã_xy)",       9: "A_XZ (Ã_xz)",
    10: "A_YY (Ã_yy)",      11: "A_YZ (Ã_yz)",      12: "A_ZZ (Ã_zz)",
    13: "K (mean extrinsic curvature)",
    14: "GAMMA_HAT_X (Γ̃^x)", 15: "GAMMA_HAT_Y (Γ̃^y)", 16: "GAMMA_HAT_Z (Γ̃^z)",
    17: "THETA (CCZ4 damping scalar)",
    18: "LAPSE (α)", 19: "SHIFT_X (β^x)", 20: "SHIFT_Y (β^y)", 21: "SHIFT_Z (β^z)",
}
HY_VAR_NAMES = {
    0: "D (baryon density)", 1: "S_X (mom. x)", 2: "S_Y (mom. y)",
    3: "S_Z (mom. z)", 4: "TAU (energy)",
}

# ── REGEX PATTERNS ────────────────────────────────────────────────────────────
RE_STEP   = re.compile(
    r"step=(\d+)\s+t=([\d.eE+\-]+)\s+α_center=([\d.eE+\-nan]+)\s+\|+H\|+[₂2]=([\d.eE+\-nan]+)"
    r".*?\[Blocks:\s*(\d+)\]"
)
RE_STEP_NOBLOCKS = re.compile(
    r"step=(\d+)\s+t=([\d.eE+\-]+)\s+α_center=([\d.eE+\-nan]+)\s+\|+H\|+[₂2]=([\d.eE+\-nan]+)"
)
RE_TFINAL  = re.compile(r"t_final\s*=\s*([\d.eE+\-]+)")
RE_GRID    = re.compile(r"dx\s*=\s*([\d.eE+\-]+),?\s*dt\s*=\s*([\d.eE+\-]+)")
RE_NCELLS  = re.compile(r"(?:AMR.*?|Grid:)\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)")
RE_NAN_ST  = re.compile(r"\[NaN@step=(\d+)\]\s+ST\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*([\S]+)")
RE_NAN_HY  = re.compile(r"\[NaN@step=(\d+)\]\s+HY\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*([\S]+)")
RE_NAN_BLK = re.compile(r"\[NaN@step=(\d+)\]\s+ST\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\).*block\s+(\d+)")
RE_NAN_OK  = re.compile(r"\[NaN@step=(\d+)\]\s+all.*(finite|blocks)")
RE_DIAG_ST = re.compile(r"\[NaN-DIAG\]\s+ST_RHS:\s*(.*)")
RE_DIAG_HY = re.compile(r"\[NaN-DIAG\]\s+HY_RHS:\s*(.*)")
RE_CFL_G   = re.compile(r"\[CFL-GUARD\].*CFL=([\d.eE+\-]+)")
RE_CFL_W   = re.compile(r"\[CFL-WARN\].*CFL=([\d.eE+\-]+)")
RE_AMR_SPH = re.compile(r"\[AMR\]\s+Tracking sphere")
RE_GRANITE = re.compile(r"GRANITE\s+v([\d.]+)")
RE_ID_TYPE = re.compile(r"(Two-Punctures|Brill-Lindquist|Bowen-York|Gauge wave|Flat Minkowski)", re.I)
RE_COMPLETE= re.compile(r"Evolution complete")
RE_CHKPT   = re.compile(r"(?:Writing checkpoint|Checkpoint).*?t=([\d.eE+\-]+)")

# ── DATA STORE ────────────────────────────────────────────────────────────────
class SimData:
    def __init__(self):
        self.steps       = []
        self.times       = []
        self.alpha_c     = []
        self.ham         = []
        self.blocks      = []
        self.step_walls  = []        # wall-clock seconds at each output step
        self.nan_steps   = {}        # step → list of (type, var_id, i, j, k, val)
        self.nan_first   = None
        self.raw_log     = []
        self.start_wall  = time.time()
        self.dx          = None
        self.dt          = None
        self.t_final     = None
        self.ncells      = None
        self.version     = "?"
        self.id_type     = "unknown"
        self.logfile     = None
        self.crashed     = False
        self.crash_step  = None
        self.zombie_detected_step = None
        self.cfl_guards  = []        # (step, cfl_value)
        self.benchmark   = "?"

data = SimData()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def safe_float(s):
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except Exception:
        return None

def growth_rate(vals, times, window=8):
    """Exponential growth rate γ of ‖H‖₂ ~ exp(γ·t) over last `window` points."""
    N = min(window, len(vals))
    if N < 3:
        return None
    v = vals[-N:]; t = times[-N:]
    try:
        pos = [(vi, ti) for vi, ti in zip(v, t) if vi and vi > 0]
        if len(pos) < 3:
            return None
        lv = [math.log(p[0]) for p in pos]
        lt = [p[1] for p in pos]
        dt_span = lt[-1] - lt[0]
        if dt_span < 1e-10:
            return None
        return (lv[-1] - lv[0]) / dt_span
    except Exception:
        return None

def classify_alpha(a):
    """Returns (color_string, status_tag)."""
    if a is None:               return c("NaN", R + BLD),     "CRASH"
    if a <= ALPHA_FLOOR:        return c(f"{a:.3e}", R + BLD), "FLOOR"
    if a < 0.005:               return c(f"{a:.5f}", R),       "COLLAPSE"
    if a < ALPHA_WARN:          return c(f"{a:.5f}", Y),       "DEEP"
    if a < 0.1:                 return c(f"{a:.5f}", C),       "RECOVER"
    if a < ALPHA_TRUMPET + 0.1: return c(f"{a:.5f}", G),       "TRUMPET"
    return c(f"{a:.5f}", G + BLD),                              "HEALTHY"

def classify_ham(h):
    """Returns (color_string, status_tag)."""
    if h is None:          return c("NaN/∞", R + BLD), "CRASH"
    if h < H_HEALTHY:      return c(f"{h:.4e}", G),     "OK"
    if h < H_WARNING:      return c(f"{h:.4e}", Y),     "WARN"
    if h < H_CRITICAL:     return c(f"{h:.4e}", R),     "HIGH"
    return c(f"{h:.3e}", R + BLD),                       "CRIT"

def classify_phase(alpha, ham, blocks, t, t_final):
    """Narrative BBH merger phase based on live diagnostics."""
    if t == 0.0 or alpha is None:
        return "Initializing", W
    if alpha <= ALPHA_FLOOR:
        return "🔥 Gauge Collapse — NaN Imminent", R + BLD
    if ham and ham > H_CRITICAL:
        return "⚡ Constraint Explosion", R + BLD
    if alpha < 0.02 and (t / max(t_final or 1, 1)) < 0.15:
        return "Lapse Collapse — Trumpet Forming (normal)", Y
    if alpha < 0.05:
        return "Deep Trumpet / Late Plunge", M
    if blocks and blocks > 4:
        if alpha < 0.25:
            return "⟳ Post-Merger Ringdown", M + BLD
        return "⇝ Plunge / Close Binary", Y + BLD
    frac = t / max(t_final or 1, 1)
    if frac < 0.3:  return "◎ Early Inspiral", G
    if frac < 0.65: return "◎ Mid Inspiral",   G
    if frac < 0.90: return "◎ Late Inspiral",  C
    return "◎ Final Approach", C + BLD

# ── ZOMBIE DETECTOR ───────────────────────────────────────────────────────────
_alpha_window = deque(maxlen=ZOMBIE_WINDOW)
_ham_window   = deque(maxlen=ZOMBIE_WINDOW)

def zombie_check(step, alpha, ham):
    """Returns True if state is frozen (zombie)."""
    if alpha is not None: _alpha_window.append(alpha)
    if ham   is not None: _ham_window.append(ham)
    if len(_alpha_window) < ZOMBIE_WINDOW:
        return False
    span_a = max(_alpha_window) - min(_alpha_window)
    span_h = max(_ham_window)   - min(_ham_window)
    frozen = span_a < ZOMBIE_TOL and span_h < ZOMBIE_TOL
    if frozen and data.zombie_detected_step is None:
        data.zombie_detected_step = step
    return frozen

# ── LIVE STEP PRINTER ─────────────────────────────────────────────────────────
STEP_HISTORY = deque(maxlen=20)

def print_step(step, t, alpha_raw, ham_raw, blocks_raw, verbose=False):
    alpha  = safe_float(alpha_raw)
    ham    = safe_float(ham_raw)
    blocks = int(blocks_raw) if blocks_raw else 1

    STEP_HISTORY.append({'step': step, 'alpha': alpha, 'ham': ham, 't': t})
    wall = time.time() - data.start_wall
    data.steps.append(step)
    data.times.append(t)
    data.alpha_c.append(alpha)
    data.ham.append(ham)
    data.blocks.append(blocks)
    data.step_walls.append(wall)

    a_str, a_tag = classify_alpha(alpha)
    h_str, h_tag = classify_ham(ham)
    phase, p_col = classify_phase(alpha, ham, blocks, t, data.t_final)

    # Growth rate
    fin_h = [(h, t_) for h, t_ in zip(data.ham, data.times) if h and h > 0]
    gr = growth_rate([p[0] for p in fin_h], [p[1] for p in fin_h]) if len(fin_h) >= 3 else None
    if gr is not None:
        gr_col  = G if gr < 0 else (Y if gr < 0.3 else R)
        gr_str  = f"  γ={c(f'{gr:+.3f}', gr_col)}/M"
    else:
        gr_str = ""

    # Speed / ETA
    speed     = t / wall if wall > 0.1 else 0.0
    speed_str = f"{speed:.4f} M/s" if speed > 0 else "---"
    if data.t_final and speed > 1e-9:
        eta_s   = (data.t_final - t) / speed
        eta_str = str(timedelta(seconds=int(eta_s)))
    else:
        eta_str = "---"

    # Progress bar (compact, 30 chars)
    if data.t_final:
        frac   = min(t / data.t_final, 1.0)
        filled = int(30 * frac)
        bar_col = G if frac < 0.7 else (Y if frac < 0.9 else M)
        bar    = c("█" * filled + "░" * (30 - filled), bar_col)
        prog   = f"  [{bar}] {frac*100:5.1f}%"
    else:
        prog = ""

    # Zombie warning
    is_zombie = zombie_check(step, alpha, ham)
    zombie_str = c("  ⚠ ZOMBIE STATE!", R + BLD) if is_zombie else ""

    # Print — append only, no cursor movement
    print(f"\n{sep()}")
    print(
        f"  {c('step', BLD)}={c(step, W + BLD)}  "
        f"{c('t', BLD)}={c(f'{t:.4f}M', C)}  "
        f"{c('wall', DIM)}={c(f'{wall:.1f}s', DIM)}  "
        f"{c('speed', DIM)}={c(speed_str, DIM)}  "
        f"{c('ETA', DIM)} {c(eta_str, Y)}"
        f"{prog}"
    )
    print(f"  {c('α_center', BLD)} = {a_str}  [{c(a_tag, W)}]")
    print(f"  {c('‖H‖₂', BLD)}     = {h_str}  [{c(h_tag, W)}]{gr_str}")
    print(f"  {c('Blocks', BLD)}   = {c(blocks, C + BLD)}  "
          f"{c('Phase:', BLD)} {c(phase, p_col)}{zombie_str}")

    # Warnings
    if h_tag in ("HIGH", "CRIT"):
        print(f"  {c('⚠ CONSTRAINT ALERT:', R + BLD)} ‖H‖₂ = {ham:.3e} — diverging!")
    if a_tag == "FLOOR":
        print(f"  {c('⚠ LAPSE FLOOR HIT', R + BLD)} — α → 0, NaN cascade imminent")
        data.crashed = True
        data.crash_step = step
    if is_zombie:
        print(f"  {c('⚠ ZOMBIE STATE:', R + BLD)} α and ‖H‖₂ unchanged for {ZOMBIE_WINDOW}+ steps.")
        print(f"    {c('→ Check hierarchy.setLevelDt() and evolve_func mapping.', Y)}")

    if verbose:
        if data.dx and data.dt and t > 0:
            beta_rough = min(0.375 * t * 2, 8.0)
            cfl_est    = beta_rough * data.dt / data.dx
            cfl_col    = G if cfl_est < 0.8 else (Y if cfl_est < 1.2 else R)
            print(f"  Advection CFL ≈ {c(f'{cfl_est:.3f}', cfl_col)} "
                  f"({'✓ stable' if cfl_est < 1.0 else '⚠ UNSTABLE'})")

# ── NaN EVENT PRINTER ─────────────────────────────────────────────────────────
def print_nan_event(step, var_type, var_id, i, j, k, value):
    if step not in data.nan_steps:
        data.nan_steps[step] = []
    entry = (var_type, var_id, i, j, k, value)
    data.nan_steps[step].append(entry)
    if data.nan_first is None:
        data.nan_first = (step, var_type, var_id, i, j, k, value)

    names = ST_VAR_NAMES if var_type == "ST" else HY_VAR_NAMES
    vname = names.get(var_id, f"{var_type}_var{var_id}")

    print(f"  {c('💥 NaN', R + BLD)} @step={step}  {var_type} var={var_id} "
          f"({i},{j},{k}) = {value}")
    print(f"     Variable: {c(vname, Y)}")

    # Physical interpretation
    hints = {
        0:  "χ→0 near puncture — chi floor should catch this; check applyFloors()",
        13: "K exploding → Physical Laplacian bug or advection CFL violation",
        18: "α→0: 1+log gauge collapse — K feeds back into lapse",
    }
    for r_range, msg in [
        (range(7, 13),  "Ã_ij overflow → Ricci tensor bug or metric degeneracy"),
        (range(14, 17), "Γ̃^i growing → Γ-driver instability or dt too large"),
    ]:
        if var_id in r_range:
            hints[var_id] = msg
    if var_id in hints:
        print(f"     {c(f'→ {hints[var_id]}', Y)}")

    # Propagation tracking
    prev = []
    for ps in range(max(1, step - 4), step):
        for (pvt, pvid, pi, pj, pk, _) in data.nan_steps.get(ps, []):
            if pvt == var_type and pvid == var_id:
                prev.append((ps, pi, pj, pk))
    if prev:
        ps0, pi0, pj0, pk0 = prev[-1]
        dist  = math.sqrt((i-pi0)**2 + (j-pj0)**2 + (k-pk0)**2)
        dstep = max(1, step - ps0)
        cspd  = dist / dstep
        print(f"     {c(f'→ Propagating: ({pi0},{pj0},{pk0})→({i},{j},{k}) '  , M)}"
              f"{c(f'over {dstep} steps @ {cspd:.1f} cells/step', M)}")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
def print_summary(label="SIMULATION TRACKER"):
    wall = time.time() - data.start_wall
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n\n{'═'*74}")
    print(f"  {c(f'GRANITE {label} — FINAL SUMMARY', W + BLD + UND)}")
    print(f"{'═'*74}")

    # ── Run metadata ──────────────────────────────────────────────────────────
    print(f"\n  {c('► Run Metadata', BLD)}")
    print(f"    Timestamp   : {c(now, C)}")
    print(f"    Benchmark   : {c(data.benchmark, W)}")
    print(f"    Engine ver  : GRANITE v{data.version}")
    print(f"    ID type     : {c(data.id_type, Y)}")
    print(f"    Grid        : {data.ncells or '?'} cells   "
          f"dx={data.dx}M   dt={data.dt}M")
    print(f"    t_final     : {data.t_final}M")
    print(f"    Log file    : {data.logfile}")

    # ── Timing ────────────────────────────────────────────────────────────────
    print(f"\n  {c('► Timing', BLD)}")
    hh, rem = divmod(int(wall), 3600)
    mm, ss  = divmod(rem, 60)
    print(f"    Wall time   : {c(f'{hh}h {mm:02d}m {ss:02d}s  ({wall:.1f}s)', C)}")

    if not data.steps:
        print(f"\n  {c('No step data captured — did the simulation start correctly?', R)}")
        print(f"{'═'*74}\n")
        return

    t_reached = data.times[-1]
    n_steps   = len(data.steps)
    print(f"    Final time  : {c(f'{t_reached:.4f} M', C)}")
    print(f"    Steps done  : {c(n_steps, W)}  output steps")
    if data.t_final:
        pct    = 100.0 * t_reached / data.t_final
        filled = int(40 * pct / 100)
        bar_c  = G if pct >= 99 else (Y if pct >= 50 else R)
        bar    = c("█" * filled, bar_c) + c("░" * (40 - filled), DIM)
        print(f"    Completed   : [{bar}] {c(f'{pct:.1f}%', bar_c + BLD)}")

    # Average simulation speed
    if wall > 0 and t_reached > 0:
        avg_speed = t_reached / wall
        print(f"    Avg speed   : {c(f'{avg_speed:.5f} M/s', G)}")

    # ── Physics diagnostics ───────────────────────────────────────────────────
    print(f"\n  {c('► Physics Summary', BLD)}")

    finite_alpha = [a for a in data.alpha_c if a is not None]
    finite_ham   = [h for h in data.ham if h is not None]

    if finite_alpha:
        a_min  = min(finite_alpha)
        a_max  = max(finite_alpha)
        a_init = finite_alpha[0]
        a_last = finite_alpha[-1]
        print(f"    α_center:")
        print(f"      Initial  = {c(f'{a_init:.6e}', W)}")
        print(f"      Min      = {c(f'{a_min:.6e}', R if a_min < ALPHA_WARN else Y)}"
              f"  (step {data.steps[data.alpha_c.index(a_min)]})")
        print(f"      Max      = {c(f'{a_max:.6e}', G)}")
        print(f"      Final    = {c(f'{a_last:.6e}', G if a_last > 0.1 else Y)}", end="")
        if a_last > a_min * 2:
            print(f"  {c('← RECOVERING ✓', G + BLD)}")
        else:
            print()

    if finite_ham:
        # Find step indices where ham values occurred
        ham_indexed = [(h, data.steps[i], data.times[i])
                       for i, h in enumerate(data.ham) if h is not None]
        h_max, h_max_step, h_max_t = max(ham_indexed, key=lambda x: x[0])
        h_init = finite_ham[0]
        h_last = finite_ham[-1]
        print(f"    ‖H‖₂:")
        print(f"      Initial  = {c(f'{h_init:.4e}', W)}")
        print(f"      Max      = {c(f'{h_max:.4e}', R if h_max > H_WARNING else Y)}"
              f"  (step {h_max_step}, t={h_max_t:.3f}M)")
        print(f"      Final    = {c(f'{h_last:.4e}', G if h_last < H_WARNING else R)}")

        # Growth rate over full run
        fin_pairs = [(h, t) for h, t in zip(data.ham, data.times) if h and h > 0]
        gr_all = growth_rate([p[0] for p in fin_pairs], [p[1] for p in fin_pairs], window=len(fin_pairs))
        gr_rec = growth_rate([p[0] for p in fin_pairs], [p[1] for p in fin_pairs], window=8)
        if gr_all is not None:
            col = G if gr_all < 0 else (Y if gr_all < 0.2 else R)
            print(f"    ‖H‖₂ growth rate (full run)  : {c(f'γ = {gr_all:+.5f} /M', col)}")
        if gr_rec is not None:
            col = G if gr_rec < 0 else (Y if gr_rec < 0.2 else R)
            tag = "DECAYING ✓" if gr_rec < 0 else ("slow growth" if gr_rec < 0.2 else "EXPONENTIAL GROWTH ✗")
            print(f"    ‖H‖₂ growth rate (last 8 pts): {c(f'γ = {gr_rec:+.5f} /M  ({tag})', col)}")

    # Phase at end
    last_alpha  = data.alpha_c[-1] if data.alpha_c else None
    last_ham    = data.ham[-1]     if data.ham     else None
    last_blocks = data.blocks[-1]  if data.blocks  else 1
    phase, p_col = classify_phase(last_alpha, last_ham, last_blocks, t_reached, data.t_final)
    print(f"    Final phase : {c(phase, p_col)}")

    # AMR block stats
    if data.blocks:
        max_blocks = max(data.blocks)
        print(f"    Max AMR blocks : {c(max_blocks, C + BLD)}"
              f"  (final: {c(data.blocks[-1], C)})")

    # ── CFL guards ────────────────────────────────────────────────────────────
    if data.cfl_guards:
        print(f"\n  {c('► CFL Guard Events', BLD)}")
        print(f"    Total CFL guards triggered: {c(len(data.cfl_guards), Y)}")
        for step_g, cfl_v in data.cfl_guards[:5]:
            print(f"    step={step_g}  CFL={cfl_v:.4f}")
        if len(data.cfl_guards) > 5:
            print(f"    ... and {len(data.cfl_guards)-5} more")

    # ── NaN forensics ─────────────────────────────────────────────────────────
    print(f"\n  {c('► NaN Forensics', BLD)}")
    if not data.nan_steps:
        print(f"    {c('No NaN events detected ✓', G + BLD)}")
    else:
        n_nan_steps = len(data.nan_steps)
        n_nan_total = sum(len(v) for v in data.nan_steps.values())
        print(f"    {c(f'{n_nan_steps} steps affected, {n_nan_total} NaN instances total', R)}")
        if data.nan_first:
            s, vt, vid, i, j, k, val = data.nan_first
            names = ST_VAR_NAMES if vt == "ST" else HY_VAR_NAMES
            vname = names.get(vid, f"var{vid}")
            try:
                idx_s  = data.steps.index(s)
                t_s    = data.times[idx_s]
            except ValueError:
                t_s = "?"
            print(f"    First NaN  : step={c(s, R + BLD)}, t={t_s}M")
            print(f"    Location   : {vt} var={vid} ({i},{j},{k}) = {val}")
            print(f"    Variable   : {c(vname, Y)}")

            # Propagation
            locs = []
            for ns in sorted(data.nan_steps):
                for (nvt, nvid, ni, nj, nk, _) in data.nan_steps[ns]:
                    if nvt == vt and nvid == vid:
                        locs.append((ns, ni, nj, nk))
            if len(locs) >= 2:
                f0, l0 = locs[0], locs[-1]
                dist  = math.sqrt((l0[1]-f0[1])**2+(l0[2]-f0[2])**2+(l0[3]-f0[3])**2)
                dstep = max(1, l0[0] - f0[0])
                spd_c = dist / dstep
                spd_p = spd_c * (data.dx or 0.25)
                spd_n = spd_p / (data.dt or 0.05)
                print(f"    Propagation: {dist:.1f} cells over {dstep} steps "
                      f"= {c(f'{spd_n:.1f} M/M', M)}")

    # ── Zombie / freeze diagnosis ─────────────────────────────────────────────
    print(f"\n  {c('► State Freeze (Zombie) Diagnosis', BLD)}")
    if data.zombie_detected_step is not None:
        print(f"    {c('⚠ ZOMBIE STATE DETECTED', R + BLD)} at step {data.zombie_detected_step}")
        print(f"    {c('→ Root cause: AMR level dt was likely 0.0 (not injected before subcycle)', Y)}")
        print(f"    {c('→ Fix: hierarchy.setLevelDt(0, dt) before each subcycle() call', Y)}")
    else:
        print(f"    {c('No zombie state detected ✓', G)}")

    # ── Stability diagnosis ───────────────────────────────────────────────────
    print(f"\n  {c('► Stability Diagnosis', BLD)}")
    diags = []
    if data.crashed:
        try:
            idx = data.steps.index(data.crash_step)
            t_cr = f"{data.times[idx]:.3f}"
        except ValueError:
            t_cr = "?"
        diags.append((R, f"Lapse floor hit at step {data.crash_step} (t={t_cr}M) — crash"))
    if finite_ham and max(finite_ham) > H_CRITICAL:
        diags.append((R, f"Constraint explosion: max ‖H‖₂ = {max(finite_ham):.2e}"))
    if data.nan_first:
        s0, vt0, vid0 = data.nan_first[:3]
        diags.append((R, f"NaN seeded at step {s0} in {vt0}_var{vid0} → propagation"))
    if data.zombie_detected_step:
        diags.append((R, f"Zombie state from step {data.zombie_detected_step} — physics frozen"))
    if not diags:
        diags.append((G, "No catastrophic events — simulation appears healthy ✓"))
    for col, msg in diags:
        print(f"    {c('•', col)} {c(msg, col)}")

    # ── Step history table ────────────────────────────────────────────────────
    print(f"\n  {c('► Step History Table', BLD)}")
    hdr = f"{'step':>6}  {'t [M]':>8}  {'α_center':>12}  {'‖H‖₂':>12}  {'Blocks':>6}  Notes"
    print(f"    {c(hdr, W + BLD)}")
    print(f"    {sep('─', 74)}")
    max_rows = 60
    step_data = list(zip(data.steps, data.times, data.alpha_c, data.ham, data.blocks))
    if len(step_data) > max_rows:
        # Show first 5, last 5, and evenly sampled middle
        indices = (
            list(range(5)) +
            list(range(5, len(step_data) - 5,
                       max(1, (len(step_data) - 10) // (max_rows - 10)))) +
            list(range(len(step_data) - 5, len(step_data)))
        )
        indices = sorted(set(indices))
        rows    = [step_data[i] for i in indices]
        abridged = True
    else:
        rows = step_data
        abridged = False

    prev_idx = -1
    for pos, (s, t_, a, h, blk) in enumerate(rows):
        real_idx = data.steps.index(s)
        if abridged and prev_idx >= 0 and real_idx > prev_idx + 1:
            print(f"    {c('... (rows omitted) ...', DIM)}")
        prev_idx = real_idx

        nan_flag = f" {c('NaN', R + BLD)}" if s in data.nan_steps else ""
        a_s = f"{a:.5e}" if a is not None else c("NaN", R)
        h_s = f"{h:.5e}" if h is not None else c("NaN", R)
        a_c = G if (a and a > ALPHA_WARN) else (Y if (a and a > 0.005) else R)
        h_c = G if (h and h < H_WARNING) else (Y if (h and h < H_CRITICAL) else R)
        blk_str = c(str(blk), C)
        print(f"    {s:>6}  {t_:>8.4f}  {c(a_s, a_c):>12}  {c(h_s, h_c):>12}  {blk_str:>6}{nan_flag}")

    if abridged:
        print(f"    {c(f'[Table abridged: {len(step_data)} total rows → {len(rows)} shown]', DIM)}")

    # ── Footer ────────────────────────────────────────────────────────────────
    print(f"\n{'═'*74}")
    print(f"  {c('Log saved to:', DIM)} {data.logfile}")
    print(f"{'═'*74}\n")

# ── MAIN RUNNER ───────────────────────────────────────────────────────────────
def run(args):
    timestamp       = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile         = os.path.join(DEV_LOGS_DIR, f"sim_tracker_{timestamp}.log")
    data.logfile    = logfile
    data.benchmark  = args.benchmark or (args.params[0] if args.params else "unknown")
    data.start_wall = time.time()

    # Resolve executable + params
    if args.stdin:
        source_desc = "stdin"
    else:
        exe  = args.executable or os.path.join("build", "granite")
        if not os.path.isabs(exe):
            exe = os.path.join(PROJECT_ROOT, exe)
        bm_file = None
        if args.benchmark:
            bm_file = os.path.join(PROJECT_ROOT, "benchmarks", f"{args.benchmark}.yaml")
            if not os.path.exists(bm_file):
                bm_file = os.path.join(PROJECT_ROOT, "benchmarks",
                                       args.benchmark, "params.yaml")
        params = [bm_file] if bm_file else args.params
        cmd    = [exe] + (params or [])
        source_desc = " ".join(cmd)

    # Banner
    print(f"\n{'═'*74}")
    print(f"  {c('GRANITE SIM TRACKER — UNIVERSAL LIVE DASHBOARD', W + BLD + UND)}")
    print(f"  {c(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), C)}")
    print(f"  Source  : {c(source_desc, Y)}")
    print(f"  Log     : {c(logfile, DIM)}")
    print(f"{'═'*74}")
    print(f"  {c('Append-only output — press Ctrl+C for full summary', DIM)}")
    print(f"{sep()}\n")

    # ─────────────────────────────────────────────────────────────────────────
    def process_line(raw):
        line = raw.rstrip("\n")
        data.raw_log.append(line)
        if data.logfile:
            _log_fh.write(line + "\n")
            _log_fh.flush()

        stripped = line.strip()
        if not stripped:
            return

        # Version
        m = RE_GRANITE.search(line)
        if m:
            data.version = m.group(1)

        # ID type
        m = RE_ID_TYPE.search(line)
        if m:
            data.id_type = m.group(1)

        # Grid params
        m = RE_GRID.search(line)
        if m:
            data.dx, data.dt = float(m.group(1)), float(m.group(2))
            print(c(f"  ► Grid: dx={data.dx}M  dt={data.dt}M", G))
            return

        m = RE_TFINAL.search(line)
        if m:
            data.t_final = float(m.group(1))
            print(c(f"  ► t_final = {data.t_final}M", G))
            return

        m = RE_NCELLS.search(line)
        if m:
            data.ncells = f"{m.group(1)}×{m.group(2)}×{m.group(3)}"

        # Main step line
        m = RE_STEP.search(line)
        if not m:
            m2 = RE_STEP_NOBLOCKS.search(line)
            if m2:
                print_step(int(m2.group(1)), float(m2.group(2)),
                           m2.group(3), m2.group(4), None, args.verbose)
                return
        if m:
            print_step(int(m.group(1)), float(m.group(2)),
                       m.group(3), m.group(4), m.group(5), args.verbose)
            return

        # NaN events
        for pat, tag in [(RE_NAN_ST, "ST"), (RE_NAN_HY, "HY")]:
            mn = pat.search(line)
            if mn:
                print_nan_event(int(mn.group(1)), tag, int(mn.group(2)),
                                int(mn.group(3)), int(mn.group(4)),
                                int(mn.group(5)), mn.group(6))
                return

        # NaN OK
        m = RE_NAN_OK.search(line)
        if m:
            if args.verbose:
                step_n = int(m.group(1))
                print(c(f"  [NaN@step={step_n}] all finite ✓", DIM))
            return

        # Diag lines
        m = RE_DIAG_ST.search(line)
        if m:
            status = m.group(1).strip()
            col = G if "all finite" in status else R
            print(c(f"  [DIAG] Spacetime RHS: {status}", col))
            return

        m = RE_DIAG_HY.search(line)
        if m:
            status = m.group(1).strip()
            col = G if "all finite" in status else R
            print(c(f"  [DIAG] Hydro RHS: {status}", col))
            return

        # CFL guard
        m = RE_CFL_G.search(line)
        if m:
            cfl_v = float(m.group(1))
            step_g = data.steps[-1] if data.steps else 0
            data.cfl_guards.append((step_g, cfl_v))
            print(c(f"  [CFL-GUARD] Advection CFL={cfl_v:.4f} > 0.95 → dt reduced", Y + BLD))
            return

        m = RE_CFL_W.search(line)
        if m:
            print(c(f"  [CFL-WARN] {line.strip()}", Y))
            return

        # AMR sphere
        if RE_AMR_SPH.search(line):
            print(c(f"  {line.strip()}", M))
            return

        # Completion
        if RE_COMPLETE.search(line):
            print(f"\n{c('  ✓ Evolution complete!', G + BLD)}")
            return

        # Checkpoint
        m = RE_CHKPT.search(line)
        if m:
            print(c(f"  💾 Checkpoint @t={m.group(1)}M", DIM))
            return

        # General important lines (not step output)
        important = any(kw in line for kw in [
            "GRANITE", "Loading", "Setting", "Brill", "Two-Punct", "Bowen",
            "Gauge wave", "Flat Mink", "AMR:", "Warning", "ERROR", "error",
            "Tracking sphere",
        ])
        if important:
            print(c(f"  {stripped}", DIM))

    # ─────────────────────────────────────────────────────────────────────────
    process = None

    def signal_handler(sig, frame):
        print(c(f"\n\n  ✋ Interrupted at step {data.steps[-1] if data.steps else 0}.", Y))
        if process:
            process.terminate()

    signal.signal(signal.SIGINT, signal_handler)

    with open(logfile, "w", encoding="utf-8") as _log_fh:
        # Bind so process_line can use it
        import builtins
        builtins._log_fh = _log_fh   # workaround for closure

        globals()["_log_fh"] = _log_fh  # inject into module scope for process_line

        if args.stdin:
            for raw in sys.stdin:
                process_line(raw)
        else:
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                for raw in iter(process.stdout.readline, ""):
                    process_line(raw)
                process.wait()
            except FileNotFoundError:
                print(c(f"\n  ERROR: Binary not found: {exe}", R + BLD))
                print(c("  Run: make -j  (from the build directory)", Y))
            except Exception as e:
                print(c(f"\n  Process error: {e}", R))

    print_summary()

    # Optional matplotlib
    try:
        import importlib
        if importlib.util.find_spec("matplotlib") and len(data.steps) >= 3:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
            t_arr = data.times
            h_arr = [h if h and h > 0 else float("nan") for h in data.ham]
            a_arr = [a if a and a > 0 else float("nan") for a in data.alpha_c]

            ax1.semilogy(t_arr, h_arr, "r-o", ms=2.5, lw=1.2, label="‖H‖₂")
            ax1.axhline(H_HEALTHY,  color="g", ls="--", alpha=0.5, label="healthy")
            ax1.axhline(H_WARNING,  color="y", ls="--", alpha=0.5, label="warning")
            ax1.axhline(H_CRITICAL, color="r", ls="--", alpha=0.5, label="critical")
            ax1.set_ylabel("‖H‖₂  [log scale]")
            ax1.set_title(f"GRANITE {data.benchmark} — Hamiltonian Constraint")
            ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

            ax2.semilogy(t_arr, a_arr, "b-o", ms=2.5, lw=1.2, label="α_center")
            ax2.axhline(ALPHA_TRUMPET, color="g", ls="--", alpha=0.5, label="trumpet")
            ax2.set_xlabel("t [M]"); ax2.set_ylabel("α [log scale]")
            ax2.set_title("Lapse Evolution")
            ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plot_path = os.path.join(DEV_LOGS_DIR, f"sim_tracker_{timestamp}.png")
            plt.savefig(plot_path, dpi=150)
            print(c(f"  📊 Plot saved: {plot_path}\n", G))
    except Exception:
        pass


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
_log_fh = None   # module-level handle filled in by run()

def main():
    parser = argparse.ArgumentParser(
        description="GRANITE Universal Simulation Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("executable", nargs="?", default=None,
                        help="Path to granite binary (default: build/granite)")
    parser.add_argument("params", nargs="*",
                        help="Arguments forwarded to granite binary")
    parser.add_argument("--benchmark", "-b", default=None,
                        help="Benchmark name — looks up benchmarks/<name>.yaml")
    parser.add_argument("--stdin", action="store_true",
                        help="Read granite output from stdin instead of launching")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show NaN-OK scan lines and per-step CFL estimates")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI color (for log-file piping)")
    args = parser.parse_args()

    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    run(args)


if __name__ == "__main__":
    main()
