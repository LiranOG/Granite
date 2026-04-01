#!/usr/bin/env python3
"""
GRANITE DEV_BENCHMARK — Developer Diagnostic Runner
=====================================================
Runs the single_puncture benchmark and provides real-time physics analysis:
  • Lapse collapse/recovery tracking
  • Hamiltonian constraint ||H||₂ trend monitoring
  • NaN propagation forensics (variable, location, direction)
  • Physics health indicators (CFL, advection, gauge stability)
  • Mathematical diagnostics (constraint growth rate, instability fingerprint)

Press Ctrl+C at any time for a full summary report.
Logs are saved to: dev_benchmark_<timestamp>.log

Usage:
    python3 dev_benchmark.py [--benchmark single_puncture] [--verbose]

Author: GRANITE Dev (Liran)
"""

import subprocess
import sys
import os
import re
import time
import signal
import argparse
import math
from datetime import datetime
from collections import deque

# ── OUTPUT DIRECTORY ──────────────────────────────────────────────────────────
# All dev logs and plots go here — keeps the repo root clean.
DEV_LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dev_logs")
os.makedirs(DEV_LOGS_DIR, exist_ok=True)

# ── ANSI COLORS ──────────────────────────────────────────────────────────────
R  = "\033[91m"   # Red
Y  = "\033[93m"   # Yellow
G  = "\033[92m"   # Green
B  = "\033[94m"   # Blue
M  = "\033[95m"   # Magenta
C  = "\033[96m"   # Cyan
W  = "\033[97m"   # White bold
DIM= "\033[2m"    # Dim
RST= "\033[0m"    # Reset
BLD= "\033[1m"    # Bold

# ── PHYSICS CONSTANTS ─────────────────────────────────────────────────────────
ALPHA_RECOVERY_THRESHOLD = 0.01    # lapse below this = "deep collapse"
ALPHA_TRUMPET_TARGET     = 0.3     # lapse should asymptote toward this
H_HEALTHY                = 0.5     # ||H||₂ below this = healthy
H_WARNING                = 2.0     # ||H||₂ above this = warning
H_CRITICAL               = 10.0    # ||H||₂ above this = critical

# SpacetimeVar enum (matches C++ enum order)
ST_VAR_NAMES = {
    0:  "CHI (conformal factor χ)",
    1:  "GAMMA_XX (γ̃_xx)",
    2:  "GAMMA_XY (γ̃_xy)",
    3:  "GAMMA_XZ (γ̃_xz)",
    4:  "GAMMA_YY (γ̃_yy)",
    5:  "GAMMA_YZ (γ̃_yz)",
    6:  "GAMMA_ZZ (γ̃_zz)",
    7:  "A_XX (Ã_xx — traceless K)",
    8:  "A_XY (Ã_xy)",
    9:  "A_XZ (Ã_xz)",
    10: "A_YY (Ã_yy)",
    11: "A_YZ (Ã_yz)",
    12: "A_ZZ (Ã_zz)",
    13: "K (mean extrinsic curvature)",
    14: "GAMMA_HAT_X (Γ̃^x)",
    15: "GAMMA_HAT_Y (Γ̃^y)",
    16: "GAMMA_HAT_Z (Γ̃^z)",
    17: "THETA (CCZ4 damping scalar)",
    18: "LAPSE (α)",
    19: "SHIFT_X (β^x)",
    20: "SHIFT_Y (β^y)",
    21: "SHIFT_Z (β^z)",
}

HY_VAR_NAMES = {
    0: "RHO (matter energy density)",
    1: "MOM_X (momentum density x)",
    2: "MOM_Y (momentum density y)",
    3: "MOM_Z (momentum density z)",
    4: "TAU (energy — atmosphere)",
}

# ── DATA STORE ────────────────────────────────────────────────────────────────
class SimData:
    def __init__(self):
        self.steps      = []       # step numbers
        self.times      = []       # simulation times [M]
        self.alpha_c    = []       # lapse at center
        self.ham        = []       # ||H||₂
        self.nan_steps  = {}       # step → list of (var_type, var_id, i, j, k, value)
        self.raw_log    = []       # all raw output lines
        self.start_wall = time.time()
        self.step_times = []       # wall-clock time at each output step
        self.dx         = None
        self.dt         = None
        self.t_final    = None
        self.ncells     = None
        self.nan_first  = None     # (step, var, loc) of first NaN
        self.crashed    = False
        self.crash_step = None

data = SimData()

# ── PARSERS ───────────────────────────────────────────────────────────────────
RE_GRID    = re.compile(r"dx\s*=\s*([\d.]+),\s*dt\s*=\s*([\d.]+)")
RE_TFINAL  = re.compile(r"t_final\s*=\s*([\d.]+)")
RE_NCELLS  = re.compile(r"AMR.*?(\d+)x(\d+)x(\d+)")
RE_STEP    = re.compile(
    r"step=(\d+)\s+t=([\d.]+)\s+α_center=([-\d.e+nan]+)\s+\|\|H\|\|₂=([-\d.e+nan]+)")
RE_NAN_ST  = re.compile(r"\[NaN@step=(\d+)\]\s+ST\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*([-\d.e+naninf]+)")
RE_NAN_HY  = re.compile(r"\[NaN@step=(\d+)\]\s+HY\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*([-\d.e+naninf]+)")
RE_NAN_OK  = re.compile(r"\[NaN@step=(\d+)\]\s+all finite")
RE_DIAG_ST = re.compile(r"\[NaN-DIAG\]\s+ST_RHS:\s+(.*)")
RE_DIAG_HY = re.compile(r"\[NaN-DIAG\]\s+HY_RHS:\s+(.*)")
RE_CHECKPOINT = re.compile(r"Writing checkpoint.*t=([\d.]+)")

def safe_float(s):
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except:
        return None

# ── LIVE ANALYSIS ─────────────────────────────────────────────────────────────
def classify_ham(h):
    if h is None: return R + "NaN/∞" + RST, "CRASH"
    if h < H_HEALTHY:  return G + f"{h:.4f}" + RST, "OK"
    if h < H_WARNING:  return Y + f"{h:.4f}" + RST, "WARN"
    if h < H_CRITICAL: return R + f"{h:.4f}" + RST, "HIGH"
    return R + BLD + f"{h:.3e}" + RST, "CRIT"

def classify_alpha(a):
    if a is None: return R + "NaN" + RST, "CRASH"
    if a <= 1e-5:  return R + BLD + f"{a:.2e}" + RST, "FLOOR"
    if a < 0.005:  return R + f"{a:.5f}" + RST, "COLLAPSE"
    if a < 0.02:   return Y + f"{a:.5f}" + RST, "DEEP"
    if a < 0.1:    return C + f"{a:.5f}" + RST, "RECOVER"
    return G + f"{a:.5f}" + RST, "HEALTHY"

def growth_rate(vals, times):
    """Exponential growth rate of the last N data points: ||H||₂ ~ exp(γ t)"""
    N = min(5, len(vals))
    if N < 2: return None
    v = vals[-N:]
    t = times[-N:]
    try:
        pos = [(vi, ti) for vi, ti in zip(v, t) if vi and vi > 0]
        if len(pos) < 2: return None
        lv = [math.log(vi) for vi, _ in pos]
        lt = [ti for _, ti in pos]
        dt_ = lt[-1] - lt[0]
        if dt_ < 1e-10: return None
        return (lv[-1] - lv[0]) / dt_
    except:
        return None

def physics_phase(step_history):
    """Determine the physical phase of the simulation."""
    if not step_history: return "Initializing", W
    last = step_history[-1]
    a = last['alpha']
    h = last['ham']
    step = last['step']

    if a is None or h is None: return "CRASHED (NaN)", R
    if a <= 1e-5: return "Lapse at floor — NaN imminent", R
    if a < 0.005 and step < 40: return "Initial lapse collapse (normal)", Y
    if a < 0.02 and h is not None and h < 0.3: return "Trumpet forming — gauge settling", C
    if a > 0.01 and len(step_history) >= 3:
        prev = step_history[-3]['alpha']
        if prev and a > prev: return "Lapse recovering — trumpet stable ✓", G
    if h and h > H_CRITICAL: return "CONSTRAINT EXPLOSION", R
    if h and h > H_WARNING: return "Growing constraint violation!", Y
    return "Evolving — monitoring...", B

STEP_HISTORY = deque(maxlen=20)

def print_step_analysis(step, t, alpha_raw, ham_raw, verbose=False):
    alpha = safe_float(alpha_raw)
    ham   = safe_float(ham_raw)

    STEP_HISTORY.append({'step': step, 'alpha': alpha, 'ham': ham, 't': t})
    data.steps.append(step)
    data.times.append(t)
    data.alpha_c.append(alpha)
    data.ham.append(ham)
    data.step_times.append(time.time() - data.start_wall)

    h_str, h_cls  = classify_ham(ham)
    a_str, a_cls  = classify_alpha(alpha)
    phase, p_color = physics_phase(list(STEP_HISTORY))

    # Growth rate
    gr = growth_rate(
        [x for x in data.ham if x is not None],
        [data.times[i] for i,x in enumerate(data.ham) if x is not None]
    )
    gr_str = ""
    if gr is not None:
        gr_col = G if gr < 0 else (Y if gr < 0.5 else R)
        gr_str = f"  γ={gr_col}{gr:+.3f}{RST}/M"

    # Wall-clock speed
    wall = time.time() - data.start_wall
    steps_done = len(data.steps)
    speed = t / wall if wall > 0 else 0
    eta_str = ""
    if data.t_final and speed > 0:
        eta_s = (data.t_final - t) / speed
        h, rem = divmod(int(eta_s), 3600)
        m, s_  = divmod(rem, 60)
        eta_str = f"  ETA {h}h{m:02d}m{s_:02d}s" if h > 0 else f"  ETA {m}m{s_:02d}s"

    # Main step output line
    print(f"\n{BLD}{'─'*72}{RST}")
    print(f"  {BLD}step={W}{step}{RST}  {DIM}t={RST}{C}{t:.4f}M{RST}  "
          f"wall={DIM}{wall:.1f}s{RST}  sim-speed={DIM}{speed:.3f}M/s{RST}{eta_str}")
    print(f"  α_center = {a_str}  [{a_cls}]")
    print(f"  ‖H‖₂     = {h_str}  [{h_cls}]{gr_str}")
    print(f"  Phase    : {p_color}{phase}{RST}")

    if verbose:
        # CFL diagnostic for advection
        if data.dt and data.dx:
            # Rough estimate: |β| ~ 0.75 * |Γ̂| / η ~ 0.75 * 2 * t_approx
            beta_rough = min(0.375 * t * 2, 8.0)   # rough estimate
            cfl_adv = beta_rough * data.dt / data.dx
            cfl_col = G if cfl_adv < 0.8 else (Y if cfl_adv < 1.2 else R)
            print(f"  Advection CFL (|β|·dt/dx) ≈ {cfl_col}{cfl_adv:.3f}{RST} "
                  f"  {'✓ stable' if cfl_adv < 1.0 else '⚠ UNSTABLE — upwinding critical!'}")

    # Warnings
    if h_cls in ("HIGH", "CRIT"):
        print(f"  {R}⚠ CONSTRAINT ALERT: ||H||₂ = {ham:.3e} — growing fast!{RST}")
    if a_cls == "FLOOR":
        print(f"  {R}⚠ LAPSE FLOOR HIT — α → 0 (gauge collapse ongoing){RST}")
        data.crashed = True
        data.crash_step = step

def print_nan_event(step, var_type, var_id, i, j, k, value, verbose=False):
    """Annotate a NaN detection event with physical context."""
    if step not in data.nan_steps:
        data.nan_steps[step] = []
    entry = (var_type, var_id, i, j, k, value)
    data.nan_steps[step].append(entry)

    if data.nan_first is None:
        data.nan_first = (step, var_type, var_id, i, j, k, value)

    if var_type == "ST":
        vname = ST_VAR_NAMES.get(var_id, f"ST_var{var_id}")
    else:
        vname = HY_VAR_NAMES.get(var_id, f"HY_var{var_id}")

    print(f"  {R}💥 NaN@step={step}  {var_type} var={var_id} ({i},{j},{k}) = {value}{RST}")
    print(f"     Variable: {Y}{vname}{RST}")

    # Physical interpretation
    if var_id == 13:  # K
        print(f"     {Y}↳ K exploding → likely Physical Laplacian bug or advection CFL violation{RST}")
    elif var_id in (7,8,9,10,11,12):  # Atilde
        print(f"     {Y}↳ Ã_ij: could be Ricci tensor overflow or metric degeneracy{RST}")
    elif var_id == 0:  # chi
        print(f"     {Y}↳ χ→0 (puncture): chi floor should catch this — check applyFloors{RST}")
    elif var_id == 18:  # lapse
        print(f"     {Y}↳ Lapse: 1+log gauge collapse — α→0 then NaN via K equation{RST}")
    elif var_id in (14,15,16):  # Gamma-hat
        print(f"     {Y}↳ Γ̃^i: Galilean shift growing too fast — Γ-driver issue{RST}")

    # Direction of NaN propagation (if we have prior NaN in same step/nearby steps)
    prev_nans = []
    for prev_step in range(max(1, step-3), step):
        if prev_step in data.nan_steps:
            for (vt, vid, pi, pj, pk, pval) in data.nan_steps[prev_step]:
                if vt == var_type and vid == var_id:
                    prev_nans.append((prev_step, pi, pj, pk))
    if prev_nans:
        ps, pi, pj, pk = prev_nans[-1]
        di = i - pi; dj = j - pj; dk = k - pk
        speed = math.sqrt(di**2+dj**2+dk**2) / max(1, step - ps)
        print(f"     {M}↳ NaN propagating: ({pi},{pj},{pk})→({i},{j},{k}) over {step-ps} steps "
              f"@ {speed:.1f} cells/step{RST}")

# ── SUMMARY REPORT ───────────────────────────────────────────────────────────
def print_summary():
    wall = time.time() - data.start_wall
    print(f"\n\n{'═'*72}")
    print(f"  {BLD}{W}GRANITE DEV_BENCHMARK — SIMULATION SUMMARY{RST}")
    print(f"{'═'*72}")

    # Run info
    print(f"\n  {BLD}► Run Parameters{RST}")
    print(f"    Grid:     {data.ncells or '?'} cells   dx={data.dx}M  dt={data.dt}M")
    print(f"    t_final:  {data.t_final}M")
    print(f"    Elapsed:  {wall:.1f}s  ({wall/60:.1f} min)")

    if not data.steps:
        print(f"\n  {R}No step data captured.{RST}")
        return

    t_reached = data.times[-1]
    print(f"    Evolved:  {t_reached:.3f}M  ({len(data.steps)} output steps)")
    if data.t_final:
        pct = 100 * t_reached / data.t_final
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = G + "█"*filled + DIM + "░"*(bar_len-filled) + RST
        print(f"    Progress: [{bar}] {pct:.1f}%")

    # Physics health
    print(f"\n  {BLD}► Physics Summary{RST}")
    alpha_min  = min((a for a in data.alpha_c if a is not None), default=None)
    alpha_last = next((a for a in reversed(data.alpha_c) if a is not None), None)
    ham_max    = max((h for h in data.ham if h is not None), default=None)
    ham_last   = next((h for h in reversed(data.ham) if h is not None), None)

    a_min_str  = f"{alpha_min:.5e}"  if alpha_min  is not None else "N/A"
    a_last_str = f"{alpha_last:.5e}" if alpha_last is not None else "N/A"
    h_max_str  = f"{ham_max:.4e}"    if ham_max   is not None else "N/A"
    h_last_str = f"{ham_last:.4e}"   if ham_last  is not None else "NaN"

    print(f"    α_center min:   {a_min_str}")
    print(f"    α_center final: {a_last_str}", end="")
    if alpha_last and alpha_min and alpha_last > alpha_min * 2:
        print(f"  {G}← RECOVERING ✓{RST}")
    else:
        print()

    print(f"    ‖H‖₂ max:    {h_max_str}")
    print(f"    ‖H‖₂ final:  {h_last_str}")

    # Constraint trend
    if len(data.ham) >= 5:
        finite_h = [(h, t) for h, t in zip(data.ham, data.times) if h and h > 0]
        if len(finite_h) >= 5:
            gamma = growth_rate([h for h,_ in finite_h], [t for _,t in finite_h])
            if gamma is not None:
                if gamma < 0:
                    print(f"    ‖H‖₂ growth rate: {G}γ = {gamma:+.4f}/M (DECAYING ✓){RST}")
                elif gamma < 0.2:
                    print(f"    ‖H‖₂ growth rate: {Y}γ = {gamma:+.4f}/M (slow growth){RST}")
                else:
                    print(f"    ‖H‖₂ growth rate: {R}γ = {gamma:+.4f}/M (EXPONENTIAL GROWTH ✗){RST}")

    # Phase determination
    phase, pc = physics_phase(list(STEP_HISTORY))
    print(f"    Final phase: {pc}{phase}{RST}")

    # NaN forensics
    print(f"\n  {BLD}► NaN Forensics{RST}")
    if not data.nan_steps:
        print(f"    {G}No NaN events detected ✓{RST}")
    else:
        total_nan_steps = len(data.nan_steps)
        print(f"    NaN events: {R}{total_nan_steps} steps affected{RST}")
        if data.nan_first:
            s, vt, vid, i, j, k, val = data.nan_first
            vname = (ST_VAR_NAMES if vt == "ST" else HY_VAR_NAMES).get(vid, f"var{vid}")
            print(f"    First NaN: step={s}, {vt} var={vid} ({i},{j},{k}) = {val}")
            print(f"    Variable:  {Y}{vname}{RST}")
            # Propagation speed
            nan_locs = []
            for ns in sorted(data.nan_steps.keys()):
                for (nvt, nvid, ni, nj, nk, nval) in data.nan_steps[ns]:
                    if nvt == vt and nvid == vid:
                        nan_locs.append((ns, ni, nj, nk))
            if len(nan_locs) >= 2:
                first = nan_locs[0]
                last  = nan_locs[-1]
                dist = math.sqrt((last[1]-first[1])**2+(last[2]-first[2])**2+(last[3]-first[3])**2)
                steps_span = max(1, last[0] - first[0])
                cell_speed = dist / steps_span
                phys_speed = cell_speed * (data.dx or 0.25)
                print(f"    Propagation: {dist:.1f} cells over {steps_span} steps "
                      f"= {phys_speed:.2f} M/step = {phys_speed/(data.dt or 0.0625):.1f} M/M")

    # Stability diagnosis
    print(f"\n  {BLD}► Stability Diagnosis{RST}")
    diags = []
    if data.crashed:
        # Look up the time by finding crash_step in the steps list
        try:
            crash_idx = data.steps.index(data.crash_step)
            crash_t   = f"{data.times[crash_idx]:.3f}"
        except (ValueError, IndexError):
            crash_t = "?"
        diags.append((R, f"LAPSE FLOOR HIT at step {data.crash_step} (t={crash_t}M)"))
    if ham_max and ham_max > H_CRITICAL:
        diags.append((R, f"Constraint explosion: max ||H||₂ = {ham_max:.2e}"))
    if data.nan_first:
        s0, vt0, vid0 = data.nan_first[:3]
        diags.append((R, f"NaN seeded at step {s0} in {vt0}_var{vid0} — propagates → instability"))
    if not diags:
        diags.append((G, "No catastrophic events detected — simulation appears stable"))

    # CFL advection estimate at final step
    if data.times and data.dx and data.dt:
        t_last = data.times[-1]
        beta_est = min(0.375 * t_last * 2, 8.0)
        cfl_est  = beta_est * data.dt / data.dx
        if cfl_est > 1.0:
            diags.append((Y, f"Advection CFL ≈ {cfl_est:.2f} > 1 — upwinded FD required!"))
        else:
            diags.append((G if cfl_est < 0.7 else Y,
                          f"Advection CFL ≈ {cfl_est:.2f} — {'OK' if cfl_est < 0.7 else 'borderline'}"))

    for col, msg in diags:
        print(f"    {col}• {msg}{RST}")

    # Step-by-step summary table
    if len(data.steps) > 0:
        print(f"\n  {BLD}► Step History Table{RST}")
        print(f"    {'step':>6}  {'t [M]':>8}  {'α_center':>12}  {'‖H‖₂':>12}  {'status'}")
        print(f"    {'──────':>6}  {'────────':>8}  {'────────────':>12}  {'────────────':>12}  {'──────'}")
        # Show all steps
        for s, t_, a, h in zip(data.steps, data.times, data.alpha_c, data.ham):
            nan_flag = f" {R}NaN{RST}" if s in data.nan_steps else ""
            a_s = f"{a:.5e}" if a is not None else "NaN"
            h_s = f"{h:.5e}" if h is not None else "NaN"
            # Color alpha
            if a and a > 0.02: a_col = G
            elif a and a > 0.005: a_col = Y
            else: a_col = R
            # Color H
            if h and h < H_HEALTHY: h_col = G
            elif h and h < H_WARNING: h_col = Y
            else: h_col = R
            print(f"    {s:>6}  {t_:>8.4f}  {a_col}{a_s:>12}{RST}  {h_col}{h_s:>12}{RST}{nan_flag}")

    print(f"\n{'═'*72}")
    print(f"  Full log saved to: {data.logfile_path}")
    print(f"{'═'*72}\n")

# ── MAIN RUNNER ───────────────────────────────────────────────────────────────
def run_dev_benchmark(benchmark: str, verbose: bool):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(DEV_LOGS_DIR, f"dev_benchmark_{timestamp}.log")
    data.logfile_path = logfile

    sim_exe = os.path.join("build", "bin", "granite_main")
    params_file = os.path.join("benchmarks", benchmark, "params.yaml")

    if not os.path.exists(sim_exe):
        print(f"{R}ERROR: Simulation binary not found: {sim_exe}{RST}")
        print(f"Run: python3 run_granite.py build")
        sys.exit(1)
    if not os.path.exists(params_file):
        print(f"{R}ERROR: Params file not found: {params_file}{RST}")
        sys.exit(1)

    # Banner
    print(f"\n{'═'*72}")
    print(f"  {BLD}{W}GRANITE DEV_BENCHMARK — {benchmark.upper()}{RST}")
    print(f"  Developer Diagnostic Mode  |  {timestamp}")
    print(f"  Sim:    {sim_exe}")
    print(f"  Params: {params_file}")
    print(f"  Log:    {logfile}")
    print(f"{'═'*72}")
    print(f"  {DIM}Press Ctrl+C for full summary at any time{RST}")
    print(f"{DIM}{'─'*72}{RST}\n")

    cmd = [sim_exe, params_file]
    process = None

    def signal_handler(sig, frame):
        print(f"\n\n  {Y}[Ctrl+C received — interrupting simulation...]{RST}")
        if process:
            process.terminate()

    signal.signal(signal.SIGINT, signal_handler)

    with open(logfile, "w") as lf:
        lf.write(f"GRANITE DEV_BENCHMARK — {benchmark}\n")
        lf.write(f"Started: {timestamp}\n")
        lf.write(f"{'='*72}\n\n")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            for raw_line in iter(process.stdout.readline, ''):
                line = raw_line.rstrip()
                data.raw_log.append(line)
                lf.write(line + "\n")
                lf.flush()

                # ─── Parse grid parameters ───────────────────────────────────
                m = RE_GRID.search(line)
                if m:
                    data.dx, data.dt = float(m.group(1)), float(m.group(2))
                    print(f"  {G}Grid: dx={data.dx}M  dt={data.dt}M  (CFL limit: |β|<{data.dx/data.dt:.1f}M){RST}")
                    continue

                m = RE_TFINAL.search(line)
                if m:
                    data.t_final = float(m.group(1))
                    print(f"  {G}t_final = {data.t_final}M{RST}")
                    continue

                m = RE_NCELLS.search(line)
                if m:
                    data.ncells = f"{m.group(1)}x{m.group(2)}x{m.group(3)}"
                    print(f"  {G}AMR grid: {data.ncells}{RST}")
                    continue

                # ─── NaN diagnostics ─────────────────────────────────────────
                m = RE_DIAG_ST.search(line)
                if m:
                    status = m.group(1).strip()
                    col = G if "all finite" in status else R
                    print(f"  {col}[DIAG] Spacetime RHS check: {status}{RST}")
                    continue

                m = RE_DIAG_HY.search(line)
                if m:
                    status = m.group(1).strip()
                    col = G if "all finite" in status else R
                    print(f"  {col}[DIAG] Hydro RHS check:     {status}{RST}")
                    continue

                # ─── NaN at specific cell ────────────────────────────────────
                m = RE_NAN_ST.search(line)
                if m:
                    step = int(m.group(1)); vid = int(m.group(2))
                    i,j,k = int(m.group(3)), int(m.group(4)), int(m.group(5))
                    val = m.group(6)
                    print_nan_event(step, "ST", vid, i, j, k, val, verbose)
                    continue

                m = RE_NAN_HY.search(line)
                if m:
                    step = int(m.group(1)); vid = int(m.group(2))
                    i,j,k = int(m.group(3)), int(m.group(4)), int(m.group(5))
                    val = m.group(6)
                    print_nan_event(step, "HY", vid, i, j, k, val, verbose)
                    continue

                # ─── NaN scan — all finite ────────────────────────────────────
                m = RE_NAN_OK.search(line)
                if m:
                    step = int(m.group(1))
                    if verbose:
                        print(f"  {DIM}[NaN@step={step}] all finite ✓{RST}")
                    continue

                # ─── Main step output ──────────────────────────────────────────
                m = RE_STEP.search(line)
                if m:
                    step  = int(m.group(1))
                    t_sim = float(m.group(2))
                    alpha_raw = m.group(3)
                    ham_raw   = m.group(4)
                    print_step_analysis(step, t_sim, alpha_raw, ham_raw, verbose)
                    continue

                # ─── Checkpoint ───────────────────────────────────────────────
                m = RE_CHECKPOINT.search(line)
                if m:
                    print(f"  {DIM}💾 Checkpoint written at t={m.group(1)}M{RST}")
                    continue

                # ─── Print other lines dimmed ─────────────────────────────────
                if line.strip():
                    # Only print important non-parsed lines
                    if any(kw in line for kw in ["ERROR","error","Warning","warning",
                                                  "GRANITE","Loading","Setting","Building",
                                                  "Brill","ADM"]):
                        print(f"  {DIM}{line}{RST}")

            process.wait()

        except Exception as e:
            print(f"\n  {R}Process error: {e}{RST}")

    # Final summary
    print_summary()

    # Attempt matplotlib plot if available
    try:
        import importlib
        mpl = importlib.util.find_spec("matplotlib")
        if mpl and len(data.steps) >= 3:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))
            t_arr = data.times
            h_fin = [h if h and h > 0 else float("nan") for h in data.ham]
            a_fin = [a if a and a > 0 else float("nan") for a in data.alpha_c]

            ax1.semilogy(t_arr, h_fin, 'r-o', ms=3, label="‖H‖₂")
            ax1.axhline(H_HEALTHY, color='g', ls='--', alpha=0.5, label="healthy")
            ax1.axhline(H_WARNING, color='y', ls='--', alpha=0.5, label="warning")
            ax1.axhline(H_CRITICAL,color='r', ls='--', alpha=0.5, label="critical")
            ax1.set_xlabel("t [M]"); ax1.set_ylabel("‖H‖₂  [log]")
            ax1.set_title(f"GRANITE {benchmark} — Hamiltonian Constraint")
            ax1.legend(); ax1.grid(True, alpha=0.3)

            ax2.semilogy(t_arr, a_fin, 'b-o', ms=3, label="α_center")
            ax2.axhline(ALPHA_TRUMPET_TARGET, color='g', ls='--', alpha=0.5, label="trumpet target")
            ax2.set_xlabel("t [M]"); ax2.set_ylabel("α [log]")
            ax2.set_title("Lapse Evolution")
            ax2.legend(); ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plot_file = os.path.join(DEV_LOGS_DIR, f"dev_benchmark_{timestamp}.png")
            plt.savefig(plot_file, dpi=150)
            print(f"  {G}📊 Plot saved: {plot_file}{RST}\n")
    except Exception:
        pass  # matplotlib optional


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GRANITE DEV_BENCHMARK — Developer Diagnostic Runner")
    parser.add_argument("--benchmark", default="single_puncture",
                        help="Benchmark name (default: single_puncture)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show all NaN-scan lines and CFL estimates per step")
    args = parser.parse_args()

    run_dev_benchmark(args.benchmark, args.verbose)
