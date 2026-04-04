"""
GRANITE Universal Simulation Tracker
=====================================
Context-aware live dashboard for the GRANITE NR engine.
Dynamically adapts its display, physics phase labelling, and analytics
to the scenario detected from the benchmark's params.yaml.

Scenarios supported
-------------------
  single_puncture  — one BH (Brill-Lindquist / Schwarzschild)
  binary           — two+ BHs (Two-Punctures / Bowen-York)
  gauge_wave       — gauge-wave self-consistency test
  flat             — flat Minkowski / vacuum test

Usage
-----
  python sim_tracker.py <binary> [params.yaml] [options]
  python sim_tracker.py --stdin < output.txt
  python sim_tracker.py -b B2_eq        # benchmark shortcut
"""

# ── stdlib imports ────────────────────────────────────────────────────────────
from __future__ import annotations
import argparse
import math
import os
import re
import signal
import subprocess
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple

# ── optional dependency: yaml (graceful fallback) ─────────────────────────────
try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ── Project root ──────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).resolve().parent.parent
DEV_LOGS_DIR   = PROJECT_ROOT / "dev_logs"
DEV_LOGS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. ANSI colour palette
# ─────────────────────────────────────────────────────────────────────────────
USE_COLOR = sys.stdout.isatty()

class _ANSI:
    RST = "\033[0m"
    BLD = "\033[1m"
    DIM = "\033[2m"
    UND = "\033[4m"
    R   = "\033[31m"
    G   = "\033[32m"
    Y   = "\033[33m"
    B   = "\033[34m"
    M   = "\033[35m"
    C   = "\033[36m"
    W   = "\033[97m"

A = _ANSI()

def c(text: object, *codes: str) -> str:
    """Wrap *text* in ANSI escape codes if colour is enabled."""
    if not USE_COLOR or not codes:
        return str(text)
    return "".join(codes) + str(text) + A.RST

def sep(char: str = "─", width: int = 74, col: str = A.DIM) -> str:
    return c(char * width, col)

def heavy(width: int = 74) -> str:
    return c("═" * width, A.W + A.BLD)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Physics thresholds
# ─────────────────────────────────────────────────────────────────────────────
class Thresh:
    ALPHA_TRUMPET = 0.30    # moving-puncture asymptote
    ALPHA_WARN    = 0.05    # deep collapse warning
    ALPHA_FLOOR   = 1.0e-4  # crash floor
    H_OK          = 5.0e-4  # excellent
    H_WARN        = 1.0e-2  # growing
    H_CRIT        = 0.10    # explosion
    ZOMBIE_WIN    = 6       # steps to check for frozen state
    ZOMBIE_TOL    = 1.0e-7  # minimum living variation

# ─────────────────────────────────────────────────────────────────────────────
# 3. Scenario detection & phase classification
# ─────────────────────────────────────────────────────────────────────────────
SCENARIO_SINGLE  = "single_puncture"
SCENARIO_BINARY  = "binary"
SCENARIO_GAUGE   = "gauge_wave"
SCENARIO_FLAT    = "flat"
SCENARIO_UNKNOWN = "unknown"


def detect_scenario(params_file: Optional[Path]) -> Tuple[str, int, dict]:
    """
    Parse params.yaml and return (scenario_tag, n_black_holes, raw_params_dict).
    Falls back gracefully if yaml is missing or file not found.
    """
    raw: dict = {}
    if params_file and params_file.exists() and _HAS_YAML:
        try:
            with open(params_file, encoding="utf-8") as fh:
                raw = _yaml.safe_load(fh) or {}
        except Exception:
            pass

    id_type = (raw.get("initial_data") or {}).get("type", "").lower()
    bhs     = raw.get("black_holes", []) or []
    n_bhs   = len(bhs) if isinstance(bhs, list) else 0

    if "gauge" in id_type:
        return SCENARIO_GAUGE, 0, raw
    if "flat" in id_type or "minkowski" in id_type:
        return SCENARIO_FLAT, 0, raw
    if n_bhs == 1:
        return SCENARIO_SINGLE, 1, raw
    if n_bhs >= 2 or "two_punc" in id_type or "bowen" in id_type:
        return SCENARIO_BINARY, max(n_bhs, 2), raw
    if n_bhs == 0 and id_type in ("brill_lindquist",):
        return SCENARIO_SINGLE, 1, raw
    return SCENARIO_UNKNOWN, n_bhs, raw


# ── Phase logic ───────────────────────────────────────────────────────────────
def _phase_single(t: float, alpha: Optional[float],
                  ham: Optional[float], t_final: float) -> Tuple[str, str]:
    """Moving-puncture phases for a single Schwarzschild BH."""
    frac = t / max(t_final, 1.0)
    if alpha is None:
        return "💥 NaN Crash", A.R + A.BLD
    if alpha <= Thresh.ALPHA_FLOOR:
        return "🔴 Gauge Collapse", A.R + A.BLD
    if ham and ham > Thresh.H_CRIT:
        return "⚡ Constraint Explosion", A.R + A.BLD
    if alpha > 0.85:
        return "🌐 Initial Data / Gauge Setup", A.C
    if alpha > Thresh.ALPHA_TRUMPET + 0.05:
        return "🎺 Trumpet Transition", A.Y + A.BLD
    if abs(alpha - Thresh.ALPHA_TRUMPET) < 0.06:
        return "🎺 Trumpet State   (α ≈ {:.3f})".format(alpha), A.G + A.BLD
    if frac > 0.85:
        return "✅ Stationary Trumpet", A.G + A.BLD
    return "✅ Stable Evolution", A.G


def _phase_binary(t: float, alpha: Optional[float],
                  ham: Optional[float], blocks: int,
                  t_final: float) -> Tuple[str, str]:
    """Inspiral / merger phases for a BBH system."""
    frac = t / max(t_final, 1.0)
    if alpha is None:
        return "💥 NaN Crash", A.R + A.BLD
    if alpha <= Thresh.ALPHA_FLOOR:
        return "🔴 Gauge Collapse", A.R + A.BLD
    if ham and ham > Thresh.H_CRIT:
        return "⚡ Constraint Explosion", A.R + A.BLD
    if alpha < 0.05 and frac > 0.5:
        return "⟳ Ringdown", A.M + A.BLD
    if alpha < 0.10 and blocks > 4:
        return "🌀 Merger / Plunge", A.M + A.BLD
    if frac < 0.30:
        return "◎ Early Inspiral", A.G
    if frac < 0.65:
        return "◎ Mid Inspiral", A.G
    if frac < 0.90:
        return "◎ Late Inspiral", A.C
    return "◎ Final Approach", A.C + A.BLD


def classify_phase(scenario: str, t: float, alpha: Optional[float],
                   ham: Optional[float], blocks: int,
                   t_final: float) -> Tuple[str, str]:
    if scenario == SCENARIO_SINGLE:
        return _phase_single(t, alpha, ham, t_final)
    if scenario == SCENARIO_BINARY:
        return _phase_binary(t, alpha, ham, blocks, t_final)
    return "◎ Evolving", A.G


def classify_alpha(a: Optional[float]) -> Tuple[str, str]:
    if a is None:
        return c("NaN", A.R + A.BLD), "CRASH"
    if a <= Thresh.ALPHA_FLOOR:
        return c(f"{a:.3e}", A.R + A.BLD), "FLOOR"
    if a < 0.005:
        return c(f"{a:.5f}", A.R), "COLLAPSE"
    if a < Thresh.ALPHA_WARN:
        return c(f"{a:.5f}", A.Y), "DEEP"
    if a < 0.10:
        return c(f"{a:.5f}", A.C), "RECOVER"
    if a < Thresh.ALPHA_TRUMPET + 0.10:
        return c(f"{a:.5f}", A.G), "TRUMPET"
    return c(f"{a:.5f}", A.G + A.BLD), "HEALTHY"


def classify_ham(h: Optional[float]) -> Tuple[str, str]:
    if h is None:
        return c("NaN/∞", A.R + A.BLD), "CRASH"
    if h < Thresh.H_OK:
        return c(f"{h:.4e}", A.G), "OK"
    if h < Thresh.H_WARN:
        return c(f"{h:.4e}", A.Y), "WARN"
    if h < Thresh.H_CRIT:
        return c(f"{h:.4e}", A.R), "HIGH"
    return c(f"{h:.3e}", A.R + A.BLD), "CRIT"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Data model
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class CflEvent:
    step: int
    value: float


@dataclass
class NanEvent:
    step: int
    var_type: str  # ST or HY
    var_id: int
    i: int
    j: int
    k: int
    value: str


@dataclass
class StepRecord:
    step: int
    t: float
    alpha: Optional[float]
    ham: Optional[float]
    blocks: int
    wall: float  # seconds since sim start


@dataclass
class SimSession:
    """All telemetry captured during one simulation run."""
    # Metadata
    scenario:    str = SCENARIO_UNKNOWN
    n_bhs:       int = 0
    version:     str = "?"
    id_type:     str = "unknown"
    benchmark:   str = "?"
    logfile:     Optional[Path] = None
    raw_params:  dict = field(default_factory=dict)

    # Grid
    dx:      Optional[float] = None
    dt:      Optional[float] = None
    ncells:  Optional[str]   = None
    t_final: Optional[float] = None

    # Time series
    records: List[StepRecord] = field(default_factory=list)

    # Events
    cfl_events: List[CflEvent] = field(default_factory=list)
    nan_events: List[NanEvent] = field(default_factory=list)

    # Flags
    crashed: bool = False
    crash_step: Optional[int] = None
    zombie_step: Optional[int] = None

    # Internal helpers
    _start_wall: float = field(default_factory=time.time)
    _alpha_win:  Deque[float] = field(default_factory=lambda: deque(maxlen=Thresh.ZOMBIE_WIN))
    _ham_win:    Deque[float] = field(default_factory=lambda: deque(maxlen=Thresh.ZOMBIE_WIN))
    _log_fh = None  # open file handle — set at runtime


# ─────────────────────────────────────────────────────────────────────────────
# 5. Regex catalogue
# ─────────────────────────────────────────────────────────────────────────────
class RE:
    """All compiled regex patterns in one namespace."""
    STEP = re.compile(
        r"step=(\d+)\s+t=([\d.eE+\-]+)\s+"
        r"α_center=([\d.eE+\-nan]+)\s+"
        r"\|+H\|+[₂2]=([\d.eE+\-nan]+)"
        r"(?:.*?\[Blocks:\s*(\d+)\])?"
    )
    TFINAL  = re.compile(r"t_final\s*=\s*([\d.eE+\-]+)")
    GRID    = re.compile(r"dx\s*=\s*([\d.eE+\-]+),?\s*dt\s*=\s*([\d.eE+\-]+)")
    NCELLS  = re.compile(r"(?:AMR.*?|Grid:)\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)")
    NAN_ST  = re.compile(r"\[NaN@step=(\d+)\]\s+ST\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*(\S+)")
    NAN_HY  = re.compile(r"\[NaN@step=(\d+)\]\s+HY\s+var=(\d+)\s+\((\d+),(\d+),(\d+)\)\s*=\s*(\S+)")
    CFL_W   = re.compile(r"\[CFL-(?:WARN|GUARD)\].*CFL=([\d.eE+\-]+)")
    GRANITE = re.compile(r"GRANITE\s+v([\d.]+)")
    ID_TYPE = re.compile(r"(Two-Punctures|Brill-Lindquist|Bowen-York|Gauge wave|Flat Minkowski)", re.I)
    COMPLETE= re.compile(r"Evolution complete")
    CHKPT   = re.compile(r"(?:Writing checkpoint|Checkpoint).*?t=([\d.eE+\-]+)")
    DIAG_ST = re.compile(r"\[NaN-DIAG\]\s+ST_RHS:\s*(.*)")
    DIAG_HY = re.compile(r"\[NaN-DIAG\]\s+HY_RHS:\s*(.*)")
    PUNCH   = re.compile(r"Puncture[_\s]+(\d+).*?x=([\d.\-]+).*?y=([\d.\-]+).*?z=([\d.\-]+)", re.I)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Helper utilities
# ─────────────────────────────────────────────────────────────────────────────
def safe_float(s: str) -> Optional[float]:
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def growth_rate(vals: List[float], times: List[float], window: int = 8) -> Optional[float]:
    """Estimate exponential growth rate γ of ‖H‖₂ ~ exp(γ·t) over last *window* pts."""
    n = min(window, len(vals))
    if n < 3:
        return None
    v = vals[-n:]; t = times[-n:]
    try:
        pos = [(vi, ti) for vi, ti in zip(v, t) if vi and vi > 0]
        if len(pos) < 3:
            return None
        lv = [math.log(p[0]) for p in pos]
        lt = [p[1]            for p in pos]
        dt_span = lt[-1] - lt[0]
        if dt_span < 1e-10:
            return None
        return (lv[-1] - lv[0]) / dt_span
    except Exception:
        return None


def fmt_duration(seconds: float) -> str:
    hh, rem = divmod(int(seconds), 3600)
    mm, ss  = divmod(rem, 60)
    return f"{hh}h {mm:02d}m {ss:02d}s"


def fmt_eta(t_now: float, t_final: float, wall: float) -> str:
    speed = t_now / wall if wall > 0.1 else 0.0
    if speed < 1e-9 or t_final is None:
        return "---"
    return str(timedelta(seconds=int((t_final - t_now) / speed)))


def progress_bar(frac: float, width: int = 32) -> str:
    frac    = max(0.0, min(frac, 1.0))
    filled  = int(width * frac)
    col     = A.G if frac < 0.70 else (A.Y if frac < 0.90 else A.M)
    bar     = c("█" * filled + "░" * (width - filled), col)
    return f"[{bar}] {frac*100:5.1f}%"


def _zombie_check(sess: SimSession, step: int,
                  alpha: Optional[float], ham: Optional[float]) -> bool:
    if alpha is not None:
        sess._alpha_win.append(alpha)
    if ham is not None:
        sess._ham_win.append(ham)
    if len(sess._alpha_win) < Thresh.ZOMBIE_WIN:
        return False
    span_a = max(sess._alpha_win) - min(sess._alpha_win)
    span_h = max(sess._ham_win)   - min(sess._ham_win)
    frozen = span_a < Thresh.ZOMBIE_TOL and span_h < Thresh.ZOMBIE_TOL
    if frozen and sess.zombie_step is None:
        sess.zombie_step = step
    return frozen


# ─────────────────────────────────────────────────────────────────────────────
# 7. Live step printer
# ─────────────────────────────────────────────────────────────────────────────
_STEP_HIST: Deque[StepRecord] = deque(maxlen=20)


def print_step(sess: SimSession, rec: StepRecord, verbose: bool = False) -> None:
    """Render one step's telemetry block to stdout."""
    _STEP_HIST.append(rec)
    sess.records.append(rec)

    wall  = rec.wall
    alpha = rec.alpha
    ham   = rec.ham

    a_str, a_tag = classify_alpha(alpha)
    h_str, h_tag = classify_ham(ham)
    phase, p_col = classify_phase(sess.scenario, rec.t, alpha, ham,
                                  rec.blocks, sess.t_final or 1.0)

    # ── Growth rate ──────────────────────────────────────────────────────────
    fin_h = [(r.ham, r.t) for r in sess.records if r.ham and r.ham > 0]
    gr    = growth_rate([p[0] for p in fin_h],
                        [p[1] for p in fin_h]) if len(fin_h) >= 3 else None
    if gr is not None:
        gr_col = A.G if gr < 0 else (A.Y if gr < 0.3 else A.R)
        gr_str = f"   γ={c(f'{gr:+.3f}', gr_col)}/M"
    else:
        gr_str = ""

    # ── Speed / ETA ──────────────────────────────────────────────────────────
    speed     = rec.t / wall if wall > 0.1 else 0.0
    speed_str = f"{speed:.4f} M/s" if speed > 0 else "---"
    eta_str   = fmt_eta(rec.t, sess.t_final, wall)

    # ── Progress ─────────────────────────────────────────────────────────────
    prog = progress_bar(rec.t / sess.t_final if sess.t_final else 0.0)

    # ── Zombie ───────────────────────────────────────────────────────────────
    is_zombie  = _zombie_check(sess, rec.step, alpha, ham)
    zombie_str = c("  ⚠ ZOMBIE STATE!", A.R + A.BLD) if is_zombie else ""

    # ── Scenario badge ────────────────────────────────────────────────────────
    badges = {
        SCENARIO_SINGLE:  c("  [1BH]",    A.C  + A.BLD),
        SCENARIO_BINARY:  c("  [BBH]",    A.M  + A.BLD),
        SCENARIO_GAUGE:   c("  [GAUGE]",  A.B  + A.BLD),
        SCENARIO_FLAT:    c("  [FLAT]",   A.DIM),
        SCENARIO_UNKNOWN: "",
    }
    badge = badges.get(sess.scenario, "")

    print(f"\n{sep()}")
    print(
        f"  {c('step', A.BLD)}={c(rec.step, A.W + A.BLD)}"
        f"  {c('t', A.BLD)}={c(f'{rec.t:.4f}M', A.C)}"
        f"  {c('wall', A.DIM)}={c(f'{wall:.1f}s', A.DIM)}"
        f"  {c(speed_str, A.DIM)}"
        f"  {c('ETA', A.DIM)} {c(eta_str, A.Y)}"
        f"  {prog}{badge}"
    )
    print(f"  {c('α_center', A.BLD)} = {a_str}  [{c(a_tag, A.W)}]")
    print(f"  {c('‖H‖₂', A.BLD)}     = {h_str}  [{c(h_tag, A.W)}]{gr_str}")
    print(f"  {c('Blocks', A.BLD)}   = {c(rec.blocks, A.C + A.BLD)}"
          f"  {c('Phase:', A.BLD)} {c(phase, p_col)}{zombie_str}")

    # ── Scenario-specific analytics ──────────────────────────────────────────
    if sess.scenario == SCENARIO_SINGLE and alpha is not None and alpha > 0:
        target_diff = abs(alpha - Thresh.ALPHA_TRUMPET)
        stab_col    = A.G if target_diff < 0.05 else (A.Y if target_diff < 0.15 else A.C)
        print(f"  {c('Trumpet Δα', A.DIM)} = {c(f'{target_diff:.4f}', stab_col)}"
              f"  (target α≈{Thresh.ALPHA_TRUMPET:.2f})")

    elif sess.scenario == SCENARIO_BINARY:
        # Puncture separation — extracted from logs if available
        positions = [r for r in getattr(sess, '_puncture_positions', [])]
        if positions and len(positions) >= 2:
            p1, p2 = positions[-2], positions[-1]
            sep_d   = math.sqrt(sum((a - b)**2 for a, b in zip(p1, p2)))
            sep_col = A.G if sep_d > 2.0 else (A.Y if sep_d > 0.5 else A.R)
            print(f"  {c('Coord sep.', A.DIM)} = {c(f'{sep_d:.3f}M', sep_col)}")

    # ── Warnings ─────────────────────────────────────────────────────────────
    if h_tag in ("HIGH", "CRIT"):
        print(f"  {c('⚠ CONSTRAINT ALERT:', A.R + A.BLD)} ‖H‖₂ = {ham:.3e} — diverging!")
    if a_tag == "FLOOR":
        print(f"  {c('⚠ LAPSE FLOOR HIT', A.R + A.BLD)} — α → 0, NaN cascade imminent")
        sess.crashed = True
        sess.crash_step = rec.step
    if is_zombie:
        print(f"  {c('⚠ ZOMBIE STATE:', A.R + A.BLD)} α and ‖H‖₂ unchanged for {Thresh.ZOMBIE_WIN}+ steps.")
        print(f"    {c('→ Check hierarchy.setLevelDt() and evolve_func mapping.', A.Y)}")

    if verbose:
        if sess.dx and sess.dt and rec.t > 0:
            beta_rough = min(0.375 * rec.t * 2, 8.0)
            cfl_est    = beta_rough * sess.dt / sess.dx
            cfl_col    = A.G if cfl_est < 0.8 else (A.Y if cfl_est < 1.2 else A.R)
            print(f"  Advection CFL ≈ {c(f'{cfl_est:.3f}', cfl_col)} "
                  f"({'✓ stable' if cfl_est < 1.0 else '⚠ UNSTABLE'})")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Final summary
# ─────────────────────────────────────────────────────────────────────────────
_ST_VARS: Dict[int, str] = {
    0:  "CHI (χ)", 1: "γ̃_xx", 2: "γ̃_xy", 3: "γ̃_xz",
    4:  "γ̃_yy",   5: "γ̃_yz", 6: "γ̃_zz",
    7:  "Ã_xx",   8: "Ã_xy",  9: "Ã_xz",
    10: "Ã_yy",   11: "Ã_yz", 12: "Ã_zz",
    13: "K",
    14: "Γ̃^x",   15: "Γ̃^y", 16: "Γ̃^z",
    17: "Θ",
    18: "α (LAPSE)", 19: "β^x", 20: "β^y", 21: "β^z",
}


def _scenario_label(sess: SimSession) -> str:
    labels = {
        SCENARIO_SINGLE:  f"Single Puncture  ({sess.n_bhs} BH)",
        SCENARIO_BINARY:  f"Binary BBH  ({sess.n_bhs} BHs)",
        SCENARIO_GAUGE:   "Gauge Wave",
        SCENARIO_FLAT:    "Flat Minkowski",
        SCENARIO_UNKNOWN: "Unknown",
    }
    return labels.get(sess.scenario, "Unknown")


def print_summary(sess: SimSession) -> None:
    wall = time.time() - sess._start_wall
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n\n{heavy()}")
    print(f"  {c('GRANITE SIMULATION TRACKER — FINAL SUMMARY', A.W + A.BLD + A.UND)}")
    print(f"{heavy()}")

    # ── Run metadata ──────────────────────────────────────────────────────────
    print(f"\n  {c('► Run Metadata', A.BLD)}")
    print(f"    Timestamp   : {c(now, A.C)}")
    print(f"    Benchmark   : {c(sess.benchmark, A.W)}")
    print(f"    Engine ver  : GRANITE v{sess.version}")
    print(f"    Scenario    : {c(_scenario_label(sess), A.Y + A.BLD)}")
    print(f"    ID type     : {c(sess.id_type, A.Y)}")
    print(f"    Grid        : {sess.ncells or '?'} cells   "
          f"dx={sess.dx}M   dt={sess.dt}M")
    print(f"    t_final     : {sess.t_final}M")
    print(f"    Log file    : {sess.logfile}")

    # ── Timing ────────────────────────────────────────────────────────────────
    print(f"\n  {c('► Timing', A.BLD)}")
    print(f"    Wall time   : {c(fmt_duration(wall) + f'  ({wall:.1f}s)', A.C)}")

    if not sess.records:
        print(f"\n  {c('No step data captured — did the simulation start correctly?', A.R)}")
        print(f"{heavy()}\n")
        return

    t_reached = sess.records[-1].t
    n_steps   = len(sess.records)
    print(f"    Final time  : {c(f'{t_reached:.4f} M', A.C)}")
    print(f"    Steps done  : {c(n_steps, A.W)}  output steps")
    if sess.t_final:
        pct    = 100.0 * t_reached / sess.t_final
        filled = int(40 * pct / 100)
        bar_c  = A.G if pct >= 99 else (A.Y if pct >= 50 else A.R)
        bar    = c("█" * filled, bar_c) + c("░" * (40 - filled), A.DIM)
        print(f"    Completed   : [{bar}] {c(f'{pct:.1f}%', bar_c + A.BLD)}")
    if wall > 0 and t_reached > 0:
        avg_speed = t_reached / wall
        print(f"    Avg speed   : {c(f'{avg_speed:.5f} M/s', A.G)}")

    # ── Physics summary ───────────────────────────────────────────────────────
    print(f"\n  {c('► Physics Summary', A.BLD)}")
    fin_alpha = [r.alpha for r in sess.records if r.alpha is not None]
    fin_ham   = [r.ham   for r in sess.records if r.ham   is not None]

    if fin_alpha:
        a_min  = min(fin_alpha); a_max = max(fin_alpha)
        a_init = fin_alpha[0];   a_last = fin_alpha[-1]
        min_step = sess.records[[r.alpha for r in sess.records].index(a_min)].step
        print(f"    α_center:")
        print(f"      Initial  = {c(f'{a_init:.6e}', A.W)}")
        print(f"      Min      = {c(f'{a_min:.6e}', A.R if a_min < Thresh.ALPHA_WARN else A.Y)}"
              f"  (step {min_step})")
        print(f"      Max      = {c(f'{a_max:.6e}', A.G)}")
        print(f"      Final    = {c(f'{a_last:.6e}', A.G if a_last > 0.1 else A.Y)}", end="")
        if a_last > a_min * 2:
            print(f"  {c('← RECOVERING ✓', A.G + A.BLD)}")
        else:
            print()

        # Scenario-specific lapse analysis
        if sess.scenario == SCENARIO_SINGLE and a_last is not None:
            delta = abs(a_last - Thresh.ALPHA_TRUMPET)
            stab  = delta < 0.05
            print(f"      Trumpet Δα (final) = "
                  f"{c(f'{delta:.4f}', A.G if stab else A.Y)}"
                  f"  {'✅ Stabilised' if stab else '⏳ Still transitioning'}")

    if fin_ham:
        ham_recs   = [(r.ham, r.step, r.t) for r in sess.records if r.ham is not None]
        h_max, h_max_step, h_max_t = max(ham_recs, key=lambda x: x[0])
        h_init = fin_ham[0]; h_last = fin_ham[-1]
        print(f"    ‖H‖₂:")
        print(f"      Initial  = {c(f'{h_init:.4e}', A.W)}")
        print(f"      Max      = {c(f'{h_max:.4e}', A.R if h_max > Thresh.H_WARN else A.Y)}"
              f"  (step {h_max_step}, t={h_max_t:.3f}M)")
        print(f"      Final    = {c(f'{h_last:.4e}', A.G if h_last < Thresh.H_WARN else A.R)}")
        fin_pairs = [(r.ham, r.t) for r in sess.records if r.ham and r.ham > 0]
        gr_all = growth_rate([p[0] for p in fin_pairs], [p[1] for p in fin_pairs],
                              window=len(fin_pairs))
        gr_rec = growth_rate([p[0] for p in fin_pairs], [p[1] for p in fin_pairs], window=8)
        if gr_all is not None:
            col = A.G if gr_all < 0 else (A.Y if gr_all < 0.2 else A.R)
            print(f"    ‖H‖₂ growth (full run)  : {c(f'γ = {gr_all:+.5f} /M', col)}")
        if gr_rec is not None:
            col = A.G if gr_rec < 0 else (A.Y if gr_rec < 0.2 else A.R)
            tag = "DECAYING ✓" if gr_rec < 0 else ("slow growth" if gr_rec < 0.2 else "EXPONENTIAL GROWTH ✗")
            print(f"    ‖H‖₂ growth (last 8 pts): {c(f'γ = {gr_rec:+.5f} /M  ({tag})', col)}")

    # Final phase
    last = sess.records[-1] if sess.records else None
    if last:
        phase, p_col = classify_phase(sess.scenario, last.t, last.alpha,
                                       last.ham, last.blocks, sess.t_final or 1.0)
        print(f"    Final phase : {c(phase, p_col)}")
    if sess.records:
        max_blk = max(r.blocks for r in sess.records)
        print(f"    Max AMR blocks : {c(max_blk, A.C + A.BLD)}"
              f"  (final: {c(sess.records[-1].blocks, A.C)})")

    # ── CFL events ────────────────────────────────────────────────────────────
    if sess.cfl_events:
        print(f"\n  {c('► CFL Warning Events', A.BLD)}")
        print(f"    Total: {c(len(sess.cfl_events), A.Y)}")
        for ev in sess.cfl_events[:5]:
            print(f"    step={ev.step}  CFL={ev.value:.4e}")
        if len(sess.cfl_events) > 5:
            print(f"    … and {len(sess.cfl_events)-5} more")

    # ── NaN forensics ─────────────────────────────────────────────────────────
    print(f"\n  {c('► NaN Forensics', A.BLD)}")
    if not sess.nan_events:
        print(f"    {c('No NaN events detected ✓', A.G + A.BLD)}")
    else:
        print(f"    {c(f'{len(sess.nan_events)} NaN instances total', A.R)}")
        first = sess.nan_events[0]
        vname = _ST_VARS.get(first.var_id, f"var{first.var_id}")
        print(f"    First NaN  : step={c(first.step, A.R + A.BLD)}")
        print(f"    Location   : {first.var_type} var={first.var_id} ({first.i},{first.j},{first.k}) = {first.value}")
        print(f"    Variable   : {c(vname, A.Y)}")

    # ── Zombie diagnosis ──────────────────────────────────────────────────────
    print(f"\n  {c('► State Freeze Diagnosis', A.BLD)}")
    if sess.zombie_step is not None:
        print(f"    {c('⚠ ZOMBIE STATE DETECTED', A.R + A.BLD)} at step {sess.zombie_step}")
        print(f"    {c('→ Root cause: AMR level dt was likely 0.0', A.Y)}")
    else:
        print(f"    {c('No zombie state detected ✓', A.G)}")

    # ── Stability summary ─────────────────────────────────────────────────────
    print(f"\n  {c('► Stability Summary', A.BLD)}")
    diags: List[Tuple[str, str]] = []
    if sess.crashed:
        diags.append((A.R, f"Lapse floor hit at step {sess.crash_step} — crash"))
    if fin_ham and max(fin_ham) > Thresh.H_CRIT:
        diags.append((A.R, f"Constraint explosion: max ‖H‖₂ = {max(fin_ham):.2e}"))
    if sess.nan_events:
        first_nan = sess.nan_events[0]
        diags.append((A.R, f"NaN seeded at step {first_nan.step} in {first_nan.var_type}_var{first_nan.var_id}"))
    if sess.zombie_step:
        diags.append((A.R, f"Zombie state from step {sess.zombie_step}"))
    if not diags:
        diags.append((A.G, "No catastrophic events — simulation appears healthy ✓"))
    for col, msg in diags:
        print(f"    {c('•', col)} {c(msg, col)}")

    # ── Step history table ────────────────────────────────────────────────────
    print(f"\n  {c('► Step History Table', A.BLD)}")
    hdr = f"{'step':>6}  {'t [M]':>8}  {'α_center':>12}  {'‖H‖₂':>12}  {'Blk':>4}  Notes"
    print(f"    {c(hdr, A.W + A.BLD)}")
    print(f"    {sep('─', 70)}")
    max_rows = 60
    recs = sess.records
    if len(recs) > max_rows:
        indices = (list(range(5)) +
                   list(range(5, len(recs) - 5, max(1, (len(recs) - 10) // (max_rows - 10)))) +
                   list(range(len(recs) - 5, len(recs))))
        indices = sorted(set(indices))
        rows    = [recs[i] for i in indices]
        abridged = True
    else:
        rows     = recs
        abridged = False

    nan_steps = {ev.step for ev in sess.nan_events}
    prev_idx  = -1
    for pos, rec in enumerate(rows):
        real_idx = sess.records.index(rec)
        if abridged and prev_idx >= 0 and real_idx > prev_idx + 1:
            print(f"    {c('... (rows omitted) ...', A.DIM)}")
        prev_idx = real_idx

        nan_flag = f" {c('NaN', A.R + A.BLD)}" if rec.step in nan_steps else ""
        a_s = f"{rec.alpha:.5e}" if rec.alpha is not None else c("NaN", A.R)
        h_s = f"{rec.ham:.5e}"   if rec.ham   is not None else c("NaN", A.R)
        a_c = A.G if (rec.alpha and rec.alpha > Thresh.ALPHA_WARN) else (A.Y if (rec.alpha and rec.alpha > 0.005) else A.R)
        h_c = A.G if (rec.ham and rec.ham < Thresh.H_WARN) else (A.Y if (rec.ham and rec.ham < Thresh.H_CRIT) else A.R)
        print(f"    {rec.step:>6}  {rec.t:>8.4f}  {c(a_s, a_c):>12}  {c(h_s, h_c):>12}  {c(rec.blocks, A.C):>4}{nan_flag}")

    if abridged:
        print(f"    {c(f'[Abridged: {len(recs)} rows → {len(rows)} shown]', A.DIM)}")

    # ── Footer ────────────────────────────────────────────────────────────────
    print(f"\n{heavy()}")
    print(f"  {c('Log saved to:', A.DIM)} {sess.logfile}")
    print(f"{heavy()}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 9. Line processor
# ─────────────────────────────────────────────────────────────────────────────
def process_line(line: str, sess: SimSession, verbose: bool) -> None:
    """Parse a single output line and update the session."""
    raw = line.rstrip("\n")
    if sess._log_fh:
        sess._log_fh.write(raw + "\n")
        sess._log_fh.flush()

    stripped = raw.strip()
    if not stripped:
        return

    # Version
    m = RE.GRANITE.search(raw)
    if m:
        sess.version = m.group(1)

    # ID type
    m = RE.ID_TYPE.search(raw)
    if m:
        sess.id_type = m.group(1)

    # Grid params — dx / dt
    m = RE.GRID.search(raw)
    if m:
        sess.dx, sess.dt = float(m.group(1)), float(m.group(2))
        print(c(f"  ► Grid: dx={sess.dx}M  dt={sess.dt}M", A.G))
        return

    # t_final
    m = RE.TFINAL.search(raw)
    if m:
        sess.t_final = float(m.group(1))
        print(c(f"  ► t_final = {sess.t_final}M", A.G))
        return

    # ncells
    m = RE.NCELLS.search(raw)
    if m:
        sess.ncells = f"{m.group(1)}×{m.group(2)}×{m.group(3)}"

    # Main step line
    m = RE.STEP.search(raw)
    if m:
        step   = int(m.group(1))
        t      = float(m.group(2))
        alpha  = safe_float(m.group(3))
        ham    = safe_float(m.group(4))
        blocks = int(m.group(5)) if m.group(5) else 1
        wall   = time.time() - sess._start_wall
        rec    = StepRecord(step=step, t=t, alpha=alpha, ham=ham,
                            blocks=blocks, wall=wall)
        print_step(sess, rec, verbose)
        return

    # NaN events
    for pat, tag in [(RE.NAN_ST, "ST"), (RE.NAN_HY, "HY")]:
        mn = pat.search(raw)
        if mn:
            ev = NanEvent(step=int(mn.group(1)), var_type=tag,
                          var_id=int(mn.group(2)),
                          i=int(mn.group(3)), j=int(mn.group(4)), k=int(mn.group(5)),
                          value=mn.group(6))
            sess.nan_events.append(ev)
            vname = _ST_VARS.get(ev.var_id, f"var{ev.var_id}")
            print(f"  {c('💥 NaN', A.R + A.BLD)} @step={ev.step}"
                  f"  {tag} var={ev.var_id} ({ev.i},{ev.j},{ev.k}) = {ev.value}")
            print(f"     Variable: {c(vname, A.Y)}")
            return

    # CFL warning (passive — dt is NOT modified)
    m = RE.CFL_W.search(raw)
    if m:
        cfl_v  = float(m.group(1))
        step_g = sess.records[-1].step if sess.records else 0
        sess.cfl_events.append(CflEvent(step=step_g, value=cfl_v))
        print(c(f"  [CFL-WARN] Advection CFL={cfl_v:.4e} > 0.95"
                f"  (diagnostic only — dt unchanged)", A.Y))
        return

    # Diagnostics
    m = RE.DIAG_ST.search(raw)
    if m:
        status = m.group(1).strip()
        print(c(f"  [DIAG] Spacetime RHS: {status}", A.G if "finite" in status else A.R))
        return
    m = RE.DIAG_HY.search(raw)
    if m:
        status = m.group(1).strip()
        print(c(f"  [DIAG] Hydro RHS: {status}", A.G if "finite" in status else A.R))
        return

    # Completion
    if RE.COMPLETE.search(raw):
        print(f"\n{c('  ✓ Evolution complete!', A.G + A.BLD)}")
        return

    # Checkpoint
    m = RE.CHKPT.search(raw)
    if m:
        print(c(f"  💾 Checkpoint @t={m.group(1)}M", A.DIM))
        return

    # General passthrough for important metadata lines
    important = any(kw in raw for kw in [
        "GRANITE", "Loading", "Setting", "Brill", "Two-Punct", "Bowen",
        "Gauge wave", "Flat Mink", "AMR:", "Warning", "ERROR",
        "Tracking sphere", "block_id",
    ])
    if important:
        print(c(f"  {stripped}", A.DIM))


# ─────────────────────────────────────────────────────────────────────────────
# 10. Main runner
# ─────────────────────────────────────────────────────────────────────────────
def run(args: argparse.Namespace) -> None:
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile     = DEV_LOGS_DIR / f"sim_tracker_{timestamp}.log"

    # ── Detect params.yaml for scenario context ───────────────────────────────
    params_file: Optional[Path] = None
    if args.params:
        for p in args.params:
            candidate = Path(p)
            if candidate.suffix in (".yaml", ".yml") and candidate.exists():
                params_file = candidate
                break
    if params_file is None and not getattr(args, "benchmark", None) is None:
        for suffix in [f"{args.benchmark}.yaml",
                       f"benchmarks/{args.benchmark}/params.yaml",
                       f"benchmarks/{args.benchmark}.yaml"]:
            cand = PROJECT_ROOT / suffix
            if cand.exists():
                params_file = cand
                break

    scenario, n_bhs, raw_params = detect_scenario(params_file)

    sess               = SimSession()
    sess.scenario      = scenario
    sess.n_bhs         = n_bhs
    sess.raw_params    = raw_params
    sess.logfile       = logfile
    sess.benchmark     = getattr(args, "benchmark", None) or (
        args.params[0] if args.params else "unknown")
    sess._start_wall   = time.time()

    # Seed t_final from params.yaml if available
    if raw_params:
        sess.t_final = (raw_params.get("time") or {}).get("t_final", None)

    # ── Banner ────────────────────────────────────────────────────────────────
    if args.stdin:
        source_desc = "stdin"
    else:
        exe     = getattr(args, "executable", None) or str(PROJECT_ROOT / "build" / "granite")
        if not os.path.isabs(exe):
            exe = str(PROJECT_ROOT / exe)
        bm_file = None
        if getattr(args, "benchmark", None):
            for suffix in [f"benchmarks/{args.benchmark}.yaml",
                           f"benchmarks/{args.benchmark}/params.yaml"]:
                cand = PROJECT_ROOT / suffix
                if cand.exists():
                    bm_file = str(cand)
                    break
        params   = [bm_file] if bm_file else (args.params or [])
        cmd      = [exe] + params
        source_desc = " ".join(cmd)

    scenario_line = {
        SCENARIO_SINGLE:  c("Single Puncture (1 BH) — Schwarzschild / BL", A.C + A.BLD),
        SCENARIO_BINARY:  c(f"Binary BBH ({n_bhs} BHs) — Two-Punctures / BY", A.M + A.BLD),
        SCENARIO_GAUGE:   c("Gauge Wave test", A.B + A.BLD),
        SCENARIO_FLAT:    c("Flat Minkowski vacuum", A.DIM),
        SCENARIO_UNKNOWN: c("Unknown scenario", A.Y),
    }.get(scenario, "")

    print(f"\n{heavy()}")
    print(f"  {c('GRANITE SIM TRACKER — CONTEXT-AWARE DASHBOARD', A.W + A.BLD + A.UND)}")
    print(f"  {c(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), A.C)}")
    print(f"  Scenario: {scenario_line}")
    print(f"  Source  : {c(source_desc, A.Y)}")
    print(f"  Log     : {c(str(logfile), A.DIM)}")
    print(f"{heavy()}")
    print(f"  {c('Append-only output — press Ctrl+C for full summary', A.DIM)}")
    print(f"{sep()}\n")

    process  = None

    def _sigint(sig, frame):
        last_step = sess.records[-1].step if sess.records else 0
        print(c(f"\n\n  ✋ Interrupted at step {last_step}.", A.Y))
        if process:
            process.terminate()

    signal.signal(signal.SIGINT, _sigint)

    with open(logfile, "w", encoding="utf-8") as _fh:
        sess._log_fh = _fh

        if args.stdin:
            for raw in sys.stdin:
                process_line(raw, sess, args.verbose)
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
                    process_line(raw, sess, args.verbose)
                process.wait()
            except FileNotFoundError:
                print(c(f"\n  ERROR: Binary not found: {exe}", A.R + A.BLD))
                print(c("  Run: cmake --build build --config Release", A.Y))
            except Exception as exc:
                print(c(f"\n  Process error: {exc}", A.R))

    print_summary(sess)

    # ── Optional matplotlib plot ──────────────────────────────────────────────
    try:
        import importlib.util as _ilu
        if _ilu.find_spec("matplotlib") and len(sess.records) >= 3:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            t_arr = [r.t     for r in sess.records]
            h_arr = [r.ham   if (r.ham   and r.ham   > 0) else float("nan") for r in sess.records]
            a_arr = [r.alpha if (r.alpha and r.alpha > 0) else float("nan") for r in sess.records]

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
            ax1.semilogy(t_arr, h_arr, "r-o", ms=2.5, lw=1.2, label="‖H‖₂")
            ax1.axhline(Thresh.H_OK,   color="g", ls="--", alpha=0.5, label="healthy")
            ax1.axhline(Thresh.H_WARN, color="y", ls="--", alpha=0.5, label="warning")
            ax1.axhline(Thresh.H_CRIT, color="r", ls="--", alpha=0.5, label="critical")
            ax1.set_ylabel("‖H‖₂  [log scale]")
            ax1.set_title(f"GRANITE {sess.benchmark} — Hamiltonian Constraint")
            ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

            ax2.semilogy(t_arr, a_arr, "b-o", ms=2.5, lw=1.2, label="α_center")
            ax2.axhline(Thresh.ALPHA_TRUMPET, color="g", ls="--", alpha=0.5, label="trumpet")
            ax2.set_xlabel("t [M]"); ax2.set_ylabel("α [log scale]")
            ax2.set_title("Lapse Evolution")
            ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plot_path = DEV_LOGS_DIR / f"sim_tracker_{timestamp}.png"
            plt.savefig(str(plot_path), dpi=150)
            print(c(f"  📊 Plot saved: {plot_path}\n", A.G))
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# 11. Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="GRANITE Context-Aware Simulation Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("executable", nargs="?", default=None,
                        help="Path to granite binary (default: build/granite)")
    parser.add_argument("params", nargs="*",
                        help="Arguments forwarded to granite binary")
    parser.add_argument("--benchmark", "-b", default=None,
                        help="Benchmark name — e.g. B2_eq or single_puncture")
    parser.add_argument("--stdin", action="store_true",
                        help="Read granite output from stdin")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show NaN-OK scan lines and per-step CFL estimates")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI colour (for log-file piping)")
    args = parser.parse_args()

    global USE_COLOR
    if args.no_color:
        USE_COLOR = False

    run(args)


if __name__ == "__main__":
    main()
