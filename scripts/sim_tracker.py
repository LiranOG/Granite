#!/usr/bin/env python3
# =============================================================================
#  sim_tracker.py — GRANITE Simulation Tracker (Context-Aware, Rich UI Mirror)
# =============================================================================
#
#  Author  : GRANITE Development Team
#  Version : 2.1.0
#  License : MIT
#
#  Overview
#  --------
#  This script launches and monitors a GRANITE simulation binary, providing:
#
#  1. Context-Aware State Machine  — Detects the simulation scenario (Single
#     Puncture vs. Binary BBH) from params.yaml or early stdout lines, then
#     applies the matching analytical Profile to drive physics heuristics and
#     phase labelling throughout the run.
#
#  2. Rich Terminal Dashboard      — Live progress bars, coloured metrics,
#     dynamic phase banners, AMR block counts, and a full final summary table.
#
#  3. 1:1 Log Mirror              — Every formatted dashboard line that hits the
#     terminal is simultaneously appended to the .log file (ANSI codes stripped,
#     all Unicode/UTF-8 glyphs preserved).
#
#  4. Perfect Exit Handling       — Natural completion and Ctrl+C both guarantee
#     the Final Summary block is flushed to *both* stdout and the log file
#     before the process exits.
#
#  Usage
#  -----
#  python scripts/sim_tracker.py <binary> <params.yaml>
#  python scripts/sim_tracker.py run      <params.yaml>   # 'run' alias
#
# =============================================================================

from __future__ import annotations

import math
import os
import re
import sys
import time
import signal
import argparse
import datetime
import subprocess
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# 0.  ANSI / LOCALE HARDENING
# ---------------------------------------------------------------------------
# Force UTF-8 on Windows so that Unicode glyphs (░ █ ◎ ═ ─ ⚡ …) survive.
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)

# ---------------------------------------------------------------------------
# 1.  CONSTANTS & COLOUR HELPERS
# ---------------------------------------------------------------------------

# ANSI escape sequences for terminal colour.
_C = {
    "RESET"  : "\x1B[0m",
    "CYAN"   : "\x1B[96m",
    "GREEN"  : "\x1B[92m",
    "RED"    : "\x1B[91m",
    "YELLOW" : "\x1B[93m",
    "BOLD"   : "\x1B[1m",
    "DIM"    : "\x1B[2m",
}

# Robust ANSI-stripping regex that preserves ALL Unicode / UTF-8 glyphs.
# Covers: ESC sequences (7-bit and 8-bit C1 controls).
_ANSI_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes while leaving Unicode glyphs untouched."""
    return _ANSI_RE.sub("", text)


def _col(colour: str, text: str) -> str:
    """Wrap *text* with the given ANSI colour code, then reset."""
    return f"{_C.get(colour, '')}{text}{_C['RESET']}"


# Progress-bar width (characters)
_BAR_WIDTH = 32

# ---------------------------------------------------------------------------
# 2.  SIMULATION PROFILES  (Context-Aware State Machine)
# ---------------------------------------------------------------------------

class Profile:
    """
    Abstract base for simulation-type profiles.

    Each profile defines:
      - name            : Human-readable label shown in dashboard.
      - id_type         : Identifier string used in Final Summary.
      - phase_sequence  : Ordered list of (label, trigger_fraction) pairs.
        The tracker advances to phase[i] when elapsed_t / t_final >= fraction.
      - tracked_metrics : Names of metrics relevant to this profile (for the
        Physics Summary section of the Final Summary block).
    """

    name: str = "Unknown"
    id_type: str = "Unknown"
    phase_sequence: list[tuple[str, float]] = []
    tracked_metrics: list[str] = []

    def current_phase(self, elapsed: float, t_final: float) -> str:
        """Return phase label for the given elapsed/t_final ratio."""
        if t_final <= 0:
            return self.phase_sequence[0][0] if self.phase_sequence else "—"
        frac = elapsed / t_final
        label = self.phase_sequence[0][0] if self.phase_sequence else "—"
        for lbl, threshold in self.phase_sequence:
            if frac >= threshold:
                label = lbl
        return label


class SinglePunctureProfile(Profile):
    """
    Profile A — Single Puncture / Trumpet Gauge
    =============================================
    Tracks coordinate drift, trumpet transition, and stationary stability.
    Phases are defined by the lapse α_center collapsing toward the trumpet
    value (~0.3) and then stabilising.
    """

    name    = "Single Puncture (1 BH) — Trumpet Gauge"
    id_type = "Single Puncture"
    tracked_metrics = ["α_center", "‖H‖₂", "Trumpet Transition", "Coordinate Drift"]
    phase_sequence = [
        ("◎ Pre-Collapse",        0.000),
        ("⚡ Trumpet Transition", 0.050),
        ("◎ Gauge Settling",      0.200),
        ("✔ Stationary",          0.500),
    ]


class BinaryBBHProfile(Profile):
    """
    Profile B — Binary Black Hole (Two-Punctures / Bowen-York)
    ===========================================================
    Tracks inspiral, plunge, merger, and ringdown phases based on
    elapsed coordinate time relative to t_final.

    Phase-awareness notes
    ---------------------
    • Early Inspiral  : Only α_center and ‖H‖₂ are available.  Individual
      black hole masses, spins, and momentum constraints are handled by
      separate diagnostic files — their *absence* in stdout is expected and
      must NOT be flagged as a warning or error.
    • Mid Inspiral+   : Extended metrics (separation, momentum) may appear
      once the engine activates its BH-tracker modules.
    """

    name    = "Binary BBH (2 BHs) — Two-Punctures / BY"
    id_type = "Two-Punctures"
    # ‖H‖₂ is the PRIMARY stability indicator for a BBH run.
    # Mass/spin/momentum are NOT expected from stdout during Early Inspiral.
    tracked_metrics = ["‖H‖₂ (primary)", "α_center", "AMR Blocks", "Merger Phase"]
    phase_sequence = [
        ("◎ Early Inspiral", 0.000),
        ("◎ Mid Inspiral",   0.350),
        ("⚡ Plunge",        0.700),
        ("⚡ Merger",        0.850),
        ("◎ Ringdown",       0.920),
    ]
    # Phases where individual BH properties are NOT expected in stdout.
    # The tracker will skip any mass/spin/momentum checks during these phases.
    phases_without_bh_diagnostics: frozenset[str] = frozenset({
        "◎ Early Inspiral",
    })


# ---------------------------------------------------------------------------
# Raw C++ noise patterns — lines matching these are SUPPRESSED from the .log.
# They are still shown on the terminal during the initialisation phase so the
# user can watch the engine boot sequence, but they never pollute the log file.
# ---------------------------------------------------------------------------
_RAW_CPP_PATTERNS = re.compile(
    r"(\[NaN@step=|\[DIAG\]|\[AMR\]|AMR:\s+Level|Setting initial data|"
    r"Two-Punctures:|Grid:|Loading parameter|GRANITE\s+v\d|"
    r"all\s+finite|block_id=|\[MERGED\]|Tracking sphere)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# 3.  DUAL-OUTPUT LOGGER
#     Writes every formatted dashboard line to BOTH stdout and the .log file.
# ---------------------------------------------------------------------------

class DualLogger:
    """
    Routes dashboard output to terminal (with ANSI colours) AND to the
    .log file (ANSI stripped, Unicode glyphs preserved).

    Usage
    -----
        dl = DualLogger(log_path)
        dl.emit("step=5  t=7.8125M  ...")   # → terminal + file
        dl.close()
    """

    def __init__(self, log_path: Path) -> None:
        self._log_path = log_path
        self._fh       = open(log_path, "a", encoding="utf-8", errors="replace")

    # ------------------------------------------------------------------
    def emit(self, text: str, end: str = "\n") -> None:
        """Print *text* to stdout (colour intact) and file (ANSI stripped)."""
        print(text, end=end, flush=True)
        clean = _strip_ansi(text)
        self._fh.write(clean + end)
        self._fh.flush()

    # ------------------------------------------------------------------
    def emit_raw_header(self, raw_line: str) -> None:
        """
        Emit an unformatted C++ stdout line to the TERMINAL only (not the log).
        These lines are the raw engine output and are intentionally excluded
        from the .log mirror to keep it clean.
        """
        print(raw_line, flush=True)

    # ------------------------------------------------------------------
    def close(self) -> None:
        if not self._fh.closed:
            self._fh.close()

    # ------------------------------------------------------------------
    @property
    def log_path(self) -> Path:
        return self._log_path


# ---------------------------------------------------------------------------
# 4.  SCENARIO DETECTOR  (parses params.yaml & early stdout)
# ---------------------------------------------------------------------------

class ScenarioDetector:
    """
    Identifies the simulation type from two sources:
      1. The params.yaml file (looks for `type =` or `id_type =` keys).
      2. The first N lines of C++ stdout (looks for `type='...'` patterns).

    Returns a Profile subclass instance.
    """

    # Regex that matches: type='two_punctures' / type="brill_lindquist" etc.
    _TYPE_RE = re.compile(r"type\s*[=:]\s*['\"]?(\w+)['\"]?", re.IGNORECASE)

    def __init__(self, params_path: str) -> None:
        self._params_path = params_path
        self._profile: Profile = BinaryBBHProfile()   # safe default

    def sniff_params(self) -> None:
        """Attempt to determine the scenario from the params file."""
        try:
            text = Path(self._params_path).read_text(encoding="utf-8", errors="ignore")
            self._classify(text)
        except OSError:
            pass   # File not accessible yet — will rely on stdout sniffing.

    def sniff_line(self, line: str) -> None:
        """Feed an early stdout line from the engine to refine detection."""
        self._classify(line)

    def _classify(self, text: str) -> None:
        m = self._TYPE_RE.search(text)
        if m:
            token = m.group(1).lower()
            if token in ("single_puncture", "brill_lindquist", "trumpet"):
                self._profile = SinglePunctureProfile()
            elif token in ("two_punctures", "bowen_york", "binary", "bbh"):
                self._profile = BinaryBBHProfile()

    @property
    def profile(self) -> Profile:
        return self._profile


# ---------------------------------------------------------------------------
# 5.  METRIC STORE  (rolling statistics for Physics Summary)
# ---------------------------------------------------------------------------

class MetricStore:
    """
    Stores per-step physics diagnostics and computes summary statistics
    used in the Final Summary block.

    Primary stability indicator
    ---------------------------
    ‖H‖₂ (Hamiltonian constraint) is the **primary** health metric for all
    simulation types.  α_center (lapse) is the secondary indicator.
    Individual BH masses and spin are NOT tracked here — they live in
    separate diagnostic files and are not expected in engine stdout.
    """

    def __init__(self) -> None:
        self.steps: list[dict] = []   # [{step, t, alpha, hamil, blocks, notes}]

        # Running extrema — α_center (lapse)
        self.alpha_min: tuple[float, int] = (float("inf"),  0)   # (value, step)
        self.alpha_max: tuple[float, int] = (float("-inf"), 0)

        # Running extrema — ‖H‖₂ (primary stability metric)
        self.hamil_max: tuple[float, int, float] = (0.0, 0, 0.0)  # (value, step, t)
        self.hamil_initial: float = float("nan")   # first recorded ‖H‖₂

        self.nan_events:    list[str] = []   # raw NaN trigger lines
        self.zombie_events: list[str] = []   # state-freeze diagnosis lines

        self.max_blocks:   int = 0
        self.final_blocks: int = 0
        self.engine_version: str = "Unknown"

        # Grid metadata (filled from early stdout)
        self.grid_desc: str = ""
        self.dx: str = ""
        self.dt: str = ""
        self.t_final: float = 0.0
        self.num_bhs: int = 0

        # Zombie / state-freeze detection state
        self._prev_step: int  = -1
        self._prev_t:    float = -1.0
        self._freeze_count: int = 0   # consecutive identical-step counter

    # ------------------------------------------------------------------
    def record_step(self, step: int, t: float, alpha: float,
                    hamil: float, blocks: int, notes: str = "") -> None:
        """
        Record one output step.  Also runs the zombie / state-freeze
        detector: if the engine reports the same (step, t) pair more than
        3 times in a row, it is considered stalled.
        """
        self.steps.append({
            "step": step, "t": t, "alpha": alpha,
            "hamil": hamil, "blocks": blocks, "notes": notes
        })

        # ── α extrema ─────────────────────────────────────────────────
        if alpha < self.alpha_min[0]:
            self.alpha_min = (alpha, step)
        if alpha > self.alpha_max[0]:
            self.alpha_max = (alpha, step)

        # ── ‖H‖₂ extrema (primary metric) ─────────────────────────────
        if math.isnan(self.hamil_initial):
            self.hamil_initial = hamil
        if abs(hamil) > abs(self.hamil_max[0]):
            self.hamil_max = (hamil, step, t)

        # ── AMR block bookkeeping ──────────────────────────────────────
        if blocks > self.max_blocks:
            self.max_blocks = blocks
        self.final_blocks = blocks

        # ── Zombie / state-freeze detection ───────────────────────────
        # A "zombie" is a simulation whose (step, t) pair does not advance
        # across consecutive output lines — indicating a stalled integrator.
        if step == self._prev_step and abs(t - self._prev_t) < 1e-12:
            self._freeze_count += 1
            if self._freeze_count >= 3:
                msg = (
                    f"State freeze detected: step={step} t={t:.4f}M "
                    f"repeated {self._freeze_count + 1} times"
                )
                # Only record once per unique freeze event.
                if not self.zombie_events or self.zombie_events[-1] != msg:
                    self.zombie_events.append(msg)
        else:
            self._freeze_count = 0
        self._prev_step = step
        self._prev_t    = t

    # ------------------------------------------------------------------
    @property
    def first(self) -> Optional[dict]:
        return self.steps[0] if self.steps else None

    @property
    def last(self) -> Optional[dict]:
        return self.steps[-1] if self.steps else None


# ---------------------------------------------------------------------------
# 6.  TRACKER  (main orchestrator)
# ---------------------------------------------------------------------------

class GraniteTracker:
    """
    Orchestrates launching the GRANITE binary, parsing its stdout line-by-line,
    updating the in-memory MetricStore, rendering the live dashboard, and
    writing every formatted dashboard string to the .log file via DualLogger.
    """

    # ------------------------------------------------------------------
    # 6.1  Regex patterns for parsing C++ engine stdout
    # ------------------------------------------------------------------

    # Step progress line: "step=X  t=Y.YYYYM  wall=Zs  ..."
    _RE_STEP   = re.compile(
        r"step\s*=\s*(\d+)\s+t\s*=\s*([\d.]+)\s*M?\s+"
        r"wall\s*=\s*([\d.]+)s"
    )
    # Lapse metric: "alpha_center = X.XXXX" or "α_center = X.XXXX"
    _RE_ALPHA  = re.compile(r"(?:alpha_center|α_center)\s*=\s*([\d.eE+\-]+)")
    # Hamiltonian constraint: "‖H‖₂ = X.XXXX" or "Ham = X.XXXX"
    _RE_HAMIL  = re.compile(r"(?:‖H‖₂|Ham(?:iltonian)?)\s*=\s*([\d.eE+\-]+)")
    # AMR block count: "Blocks = N" or "nblocks = N"
    _RE_BLOCKS = re.compile(r"(?:Blocks?|nblocks?)\s*=\s*(\d+)")
    # NaN detection: "[NaN@step=X]"
    _RE_NAN    = re.compile(r"\[NaN@step=(\d+)\]")
    # Engine version: "GRANITE v0.5.0"
    _RE_VER    = re.compile(r"GRANITE\s+v([\d.]+)")
    # Grid metadata: "Grid: dx=X dt=Y"
    _RE_GRID   = re.compile(r"dx\s*=\s*([\d.]+)\s*M?\s+dt\s*=\s*([\d.]+)\s*M?")
    # t_final: "t_final = 500.0M"
    _RE_TFINAL = re.compile(r"t_final\s*=\s*([\d.]+)\s*M?")
    # AMR grid size: "ncells=(WxHxD)"
    _RE_CELLS  = re.compile(r"ncells=\((\d+x\d+x\d+)\)")
    # Number of BHs: "2 BH(s)"  /  "1 BH"
    _RE_BHS    = re.compile(r"(\d+)\s+BH")

    # ------------------------------------------------------------------
    def __init__(self, binary: str, params: str, log_dir: Optional[str] = None) -> None:
        self._binary  = binary
        self._params  = params

        # ── Log file path setup ────────────────────────────────────────
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if log_dir:
            log_path = Path(log_dir) / f"sim_tracker_{ts}.log"
        else:
            # Place alongside the binary or next to params, whichever resolves.
            default_dir = Path(binary).parent.parent / "dev_logs"
            default_dir.mkdir(parents=True, exist_ok=True)
            log_path = default_dir / f"sim_tracker_{ts}.log"

        self._dl = DualLogger(log_path)
        self._store = MetricStore()
        self._start_dt = datetime.datetime.now()
        self._start_wall = time.monotonic()

        self._step_count  = 0
        self._current_t   = 0.0
        self._current_phase = ""
        self._alpha       = float("nan")
        self._hamil       = float("nan")
        self._blocks      = 0

        # ── Scenario detection ─────────────────────────────────────────
        self._detector = ScenarioDetector(params)
        self._detector.sniff_params()          # parse params.yaml first
        self._profile: Profile = self._detector.profile  # updated on first stdout

        # Flag: have we printed the header yet?
        self._header_printed = False
        # Flag: are we past the initialisation phase (engine header dump)?
        self._init_phase = True
        # Buffer for early stdout lines (sniffed for scenario detection).
        self._sniff_budget = 30   # sniff first 30 lines

        # Handle SIGINT gracefully so Final Summary always runs.
        signal.signal(signal.SIGINT, self._handle_interrupt)
        self._interrupted = False

    # ------------------------------------------------------------------
    # 6.2  Signal handling
    # ------------------------------------------------------------------

    def _handle_interrupt(self, signum, frame) -> None:  # noqa: ANN001
        """Catch Ctrl+C; let the main loop know to finalize gracefully."""
        self._interrupted = True

    # ------------------------------------------------------------------
    # 6.3  Dashboard rendering helpers
    # ------------------------------------------------------------------

    def _bar(self, fraction: float) -> str:
        """Return a Unicode progress bar string for the given [0,1] fraction."""
        filled = int(fraction * _BAR_WIDTH)
        empty  = _BAR_WIDTH - filled
        return "█" * filled + "░" * empty

    def _fmt_wall(self, seconds: float) -> str:
        """Format wall-clock seconds as  Xh YYm ZZs."""
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h}h {m:02d}m {s:02d}s"

    def _eta_str(self, elapsed_sim: float, wall_elapsed: float) -> str:
        """Estimate remaining wall time as  H:MM:SS."""
        if elapsed_sim <= 0 or wall_elapsed <= 0 or self._store.t_final <= 0:
            return "—"
        speed = elapsed_sim / wall_elapsed       # M/s
        remaining_sim = self._store.t_final - elapsed_sim
        eta_s = remaining_sim / speed if speed > 0 else 0
        h = int(eta_s // 3600)
        m = int((eta_s % 3600) // 60)
        s = int(eta_s % 60)
        return f"{h}:{m:02d}:{s:02d}"

    def _alpha_tag(self, alpha: float) -> str:
        """Colour-coded health tag for lapse α_center."""
        if alpha > 0.5:
            return _col("GREEN", "[HEALTHY]")
        if alpha > 0.25:
            return _col("YELLOW", "[WARNING]")
        return _col("RED", "[CRITICAL]")

    def _hamil_tag(self, hamil: float) -> str:
        """Colour-coded health tag for Hamiltonian constraint ‖H‖₂."""
        if hamil < 1e-3:
            return _col("GREEN", "[OK]")
        if hamil < 1e-1:
            return _col("YELLOW", "[MARGINAL]")
        return _col("RED", "[VIOLATED]")

    # ------------------------------------------------------------------
    # 6.4  Header block (printed once at startup)
    # ------------------------------------------------------------------

    def _print_header(self) -> None:
        """Print and log the opening banner."""
        W = 72
        border = "═" * W
        thin   = "─" * W
        ts     = self._start_dt.strftime("%Y-%m-%d %H:%M:%S")
        binary_label = f"{self._binary} {self._params}"

        lines = [
            f"  {border}",
            f"  GRANITE SIM TRACKER — CONTEXT-AWARE DASHBOARD",
            f"  {ts}",
            f"  Scenario: {self._profile.name}",
            f"  Source  : {binary_label}",
            f"  Log     : {self._dl.log_path}",
            f"  {border}",
            f"  Append-only output — press Ctrl+C for full summary",
            f"  {thin}",
        ]
        for line in lines:
            self._dl.emit(line)
        self._header_printed = True

    # ------------------------------------------------------------------
    # 6.5  Per-step dashboard line
    # ------------------------------------------------------------------

    def _print_step(self, step: int, t: float, wall: float, speed: float) -> None:
        """Render and emit the coloured per-step progress line."""
        t_final = self._store.t_final or 1.0
        frac    = min(t / t_final, 1.0)
        bar     = self._bar(frac)
        eta     = self._eta_str(t, wall)
        pct     = frac * 100.0
        tag     = "[BBH]" if isinstance(self._profile, BinaryBBHProfile) else "[SP]"

        # ── Main progress line ─────────────────────────────────────────
        step_line = (
            f"  {_col('CYAN', f'step={step}  t={t:.4f}M  wall={wall:.1f}s  '
                              f'{speed:.4f} M/s  ETA {eta}')}  "
            f"[{bar}]   {pct:.1f}%  {tag}"
        )
        self._dl.emit(step_line)

        # ── Metrics sub-lines ──────────────────────────────────────────
        # ‖H‖₂ is the PRIMARY stability metric — always shown first.
        if not _is_nan(self._hamil):
            htag = self._hamil_tag(self._hamil)
            self._dl.emit(f"  ‖H‖₂     = {self._hamil:.4e}  {htag}  [PRIMARY]")

        if not _is_nan(self._alpha):
            atag = self._alpha_tag(self._alpha)
            self._dl.emit(f"  α_center = {self._alpha:.5f}  {atag}")

        phase = self._profile.current_phase(t, self._store.t_final)
        self._current_phase = phase

        # During Early Inspiral (BBH), individual BH diagnostics are in separate
        # files — only global constraints are available from stdout.
        phase_note = ""
        if (
            isinstance(self._profile, BinaryBBHProfile)
            and phase in self._profile.phases_without_bh_diagnostics
        ):
            phase_note = "  (BH diagnostics → separate file)"

        self._dl.emit(f"  Blocks   = {self._blocks}  Phase: {phase}{phase_note}")

    # ------------------------------------------------------------------
    # 6.6  Final Summary block
    # ------------------------------------------------------------------

    def _print_final_summary(self) -> None:
        """Construct, print, and log the GRANITE SIMULATION TRACKER — FINAL SUMMARY block."""
        W = 72
        border = "═" * W
        thin   = "─" * W

        wall_total = time.monotonic() - self._start_wall
        store      = self._store
        profile    = self._profile

        # Timing
        ts_now     = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t_final_s  = f"{store.t_final:.1f}M" if store.t_final else "?"
        final_t    = store.last["t"]  if store.last  else 0.0
        avg_speed  = (final_t / wall_total) if wall_total > 0 else 0.0
        t_final    = store.t_final or 1.0
        frac       = min(final_t / t_final, 1.0)
        bar_done   = self._bar(frac)
        steps_done = len(store.steps)

        # Phase
        last_phase = (store.last and self._profile.current_phase(
            store.last["t"], store.t_final)) or "—"

        # Prepare section helper
        def emit(text: str = "") -> None:
            self._dl.emit(text)

        emit()
        emit(f"  {border}")
        emit(f"  GRANITE SIMULATION TRACKER — FINAL SUMMARY")
        emit(f"  {border}")
        emit()

        # ── Run Metadata ───────────────────────────────────────────────
        emit(f"  ► Run Metadata")
        emit(f"    Timestamp   : {ts_now}")
        emit(f"    Benchmark   : {self._params}")
        emit(f"    Engine ver  : {store.engine_version}")
        emit(f"    Scenario    : {profile.name.split(' — ')[0].strip()}")
        emit(f"    ID type     : {profile.id_type}")
        if store.grid_desc:
            emit(f"    Grid        : {store.grid_desc}   dx={store.dx}M   dt={store.dt}M")
        emit(f"    t_final     : {t_final_s}")
        emit(f"    Log file    : {self._dl.log_path}")
        emit()

        # ── Timing ────────────────────────────────────────────────────
        emit(f"  ► Timing")
        emit(f"    Wall time   : {self._fmt_wall(wall_total)}  ({wall_total:.1f}s)")
        emit(f"    Final time  : {final_t:.4f} M")
        emit(f"    Steps done  : {steps_done}  output steps")
        emit(f"    Completed   : [{bar_done}] {frac*100:.1f}%")
        emit(f"    Avg speed   : {avg_speed:.5f} M/s")
        emit()

        # ── Physics Summary ────────────────────────────────────────────
        emit(f"  ► Physics Summary")

        # Annotate that mass/spin are held in separate diagnostic files
        # during Early Inspiral so the reader knows this is expected.
        is_bbh = isinstance(profile, BinaryBBHProfile)
        if is_bbh:
            emit(f"    Note: Individual BH mass/spin/momentum diagnostics are")
            emit(f"          written to separate files by the engine — their")
            emit(f"          absence from this log is expected and correct.")
            emit()

        if store.first:
            # ‖H‖₂ — PRIMARY stability indicator (shown first, emphasised)
            emit(f"    ‖H‖₂  [PRIMARY STABILITY METRIC]:")
            h_init = store.hamil_initial if not math.isnan(store.hamil_initial) \
                     else store.first['hamil']
            emit(f"      Initial  = {h_init:.4e}")
            emit(f"      Max      = {store.hamil_max[0]:.4e}  "
                 f"(step {store.hamil_max[1]}, t={store.hamil_max[2]:.3f}M)")
            emit(f"      Final    = {store.last['hamil']:.4e}")
            emit()

            # α_center — secondary indicator
            emit(f"    α_center  [secondary]:")
            emit(f"      Initial  = {store.first['alpha']:.6e}")
            emit(f"      Min      = {store.alpha_min[0]:.6e}  (step {store.alpha_min[1]})")
            emit(f"      Max      = {store.alpha_max[0]:.6e}")
            emit(f"      Final    = {store.last['alpha']:.6e}")

        emit(f"    Final phase    : {last_phase}")
        emit(f"    Max AMR blocks : {store.max_blocks}  (final: {store.final_blocks})")
        emit()

        # ── NaN Forensics ─────────────────────────────────────────────
        emit(f"  ► NaN Forensics")
        if store.nan_events:
            for ev in store.nan_events:
                emit(f"    {_col('RED', ev)}")
        else:
            emit(f"    No NaN events detected ✓")
        emit()

        # ── State Freeze Diagnosis ─────────────────────────────────────
        # Zombie detection: stalled integrator (same step/t ≥ 3 consecutive
        # output lines).  Events are recorded by MetricStore.record_step().
        emit(f"  ► State Freeze Diagnosis")
        if store.zombie_events:
            for ev in store.zombie_events:
                emit(f"    {_col('YELLOW', '⚠ ' + ev)}")
        else:
            emit(f"    No zombie state detected ✓")
        emit()

        # ── Stability Summary ──────────────────────────────────────────
        emit(f"  ► Stability Summary")
        if store.nan_events or store.zombie_events:
            emit(f"    {_col('RED', '• Instability detected — review NaN Forensics above.')}")
        else:
            emit(f"    • No catastrophic events — simulation appears healthy ✓")
        emit()

        # ── Step History Table ─────────────────────────────────────────
        emit(f"  ► Step History Table")
        hdr = (f"    {'step':>6}  {'t [M]':>9}  {'α_center':>14}  "
               f"{'‖H‖₂':>12}  {'Blk':>4}  Notes")
        emit(hdr)
        emit(f"    {thin}")
        for rec in store.steps:
            note_str = rec.get("notes", "")
            emit(f"    {rec['step']:>6}  {rec['t']:>9.4f}  {rec['alpha']:>14.5e}  "
                 f"{rec['hamil']:>12.5e}  {rec['blocks']:>4}  {note_str}")
        emit()

        emit(f"  {border}")
        emit(f"  Log saved to: {self._dl.log_path}")
        emit(f"  {border}")

    # ------------------------------------------------------------------
    # 6.7  Parse a single raw stdout line from the engine
    # ------------------------------------------------------------------

    def _parse_line(self, raw: str) -> None:
        """
        Classify a raw C++ stdout line, update internal state, and decide
        whether to emit it verbatim to the terminal (never to the .log).
        """
        line = raw.rstrip()

        # ── Sniff early lines for scenario detection ───────────────────
        if self._sniff_budget > 0:
            self._detector.sniff_line(line)
            self._profile = self._detector.profile
            self._sniff_budget -= 1

        # ── Engine version ─────────────────────────────────────────────
        m = self._RE_VER.search(line)
        if m:
            self._store.engine_version = f"GRANITE v{m.group(1)}"

        # ── t_final ────────────────────────────────────────────────────
        m = self._RE_TFINAL.search(line)
        if m:
            self._store.t_final = float(m.group(1))

        # ── Grid metadata ──────────────────────────────────────────────
        m = self._RE_GRID.search(line)
        if m:
            self._store.dx = m.group(1)
            self._store.dt = m.group(2)

        m = self._RE_CELLS.search(line)
        if m:
            self._store.grid_desc = m.group(1) + " cells"

        m = self._RE_BHS.search(line)
        if m:
            self._store.num_bhs = int(m.group(1))

        # ── NaN detection ──────────────────────────────────────────────
        m = self._RE_NAN.search(line)
        if m:
            self._store.nan_events.append(line)

        # ── Step progress ──────────────────────────────────────────────
        m = self._RE_STEP.search(line)
        if m:
            step   = int(m.group(1))
            t      = float(m.group(2))
            wall   = float(m.group(3))
            speed  = t / wall if wall > 0 else 0.0

            self._step_count = step
            self._current_t  = t
            self._init_phase = False   # First step line → leave init phase

            # Collect inline α and ‖H‖₂ if present on same line
            am = self._RE_ALPHA.search(line)
            if am:
                self._alpha = float(am.group(1))
            hm = self._RE_HAMIL.search(line)
            if hm:
                self._hamil = float(hm.group(1))
            bm = self._RE_BLOCKS.search(line)
            if bm:
                self._blocks = int(bm.group(1))

            # Record into MetricStore (we may update α/hamil from next lines)
            self._store.record_step(
                step=step, t=t,
                alpha=self._alpha if not _is_nan(self._alpha) else 0.0,
                hamil=self._hamil if not _is_nan(self._hamil) else 0.0,
                blocks=self._blocks,
            )
            self._print_step(step, t, wall, speed)
            return   # Step line completely handled → do NOT emit raw

        # ── Inline metric lines (follow a step line) ───────────────────
        m = self._RE_ALPHA.search(line)
        if m:
            self._alpha = float(m.group(1))
            # Update the last recorded step if we have one
            if self._store.last:
                self._store.last["alpha"] = self._alpha
                # Also update extrema
                if self._alpha < self._store.alpha_min[0]:
                    self._store.alpha_min = (self._alpha, self._store.last["step"])
                if self._alpha > self._store.alpha_max[0]:
                    self._store.alpha_max = (self._alpha, self._store.last["step"])

        m = self._RE_HAMIL.search(line)
        if m:
            self._hamil = float(m.group(1))
            if self._store.last:
                self._store.last["hamil"] = self._hamil
                if abs(self._hamil) > abs(self._store.hamil_max[0]):
                    self._store.hamil_max = (
                        self._hamil, self._store.last["step"], self._store.last["t"]
                    )

        m = self._RE_BLOCKS.search(line)
        if m:
            self._blocks = int(m.group(1))
            if self._store.last:
                self._store.last["blocks"] = self._blocks

        # ── Raw engine init-phase lines → terminal only (not log) ──────
        if self._init_phase:
            self._dl.emit_raw_header(f"  {line}")
        # Once we pass init phase, suppress raw C++ lines from BOTH.

    # ------------------------------------------------------------------
    # 6.8  Subprocess environment builder
    # ------------------------------------------------------------------

    @staticmethod
    def _subprocess_env() -> dict:
        """
        Build an environment for the child process that forces UTF-8 output
        on all platforms.  This prevents the engine from emitting Latin-1 or
        system-locale encoded bytes that would corrupt Unicode glyphs in the
        log mirror.
        """
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"   # for any Python sub-processes
        env["LANG"]             = "en_US.UTF-8"
        env["LC_ALL"]           = "en_US.UTF-8"
        return env

    # ------------------------------------------------------------------
    # 6.9  Main run loop
    # ------------------------------------------------------------------

    def run(self) -> int:
        """
        Launch the GRANITE binary, stream its stdout line-by-line,
        and handle completion or interrupt.

        Returns the process exit code (0 = success).
        """
        # ── Print dashboard header ─────────────────────────────────────
        self._print_header()

        # ── Launch subprocess ──────────────────────────────────────────
        cmd = [self._binary, self._params]
        ret = 0
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,   # merge stderr → stdout pipe
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
                env=self._subprocess_env(),  # UTF-8 locale pin
            )
        except FileNotFoundError:
            self._dl.emit(f"{_col('RED', f'ERROR: Binary not found → {self._binary}')}")
            ret = 1
            proc = None

        # ── Stream output (only if process launched) ───────────────────
        # The outer try/finally guarantees _finalise() is ALWAYS called,
        # even if the stream raises an unexpected exception.
        try:
            if proc is not None:
                try:
                    for raw_line in proc.stdout:
                        if self._interrupted:
                            proc.terminate()
                            break
                        self._parse_line(raw_line)
                except Exception as exc:  # noqa: BLE001
                    self._dl.emit(f"{_col('RED', f'Stream error: {exc}')}")
                finally:
                    proc.wait()
                    if ret == 0:
                        ret = proc.returncode or 0

            # ── Handle interrupt banner ────────────────────────────────
            if self._interrupted:
                self._dl.emit()
                self._dl.emit(f"  ✋ Interrupted at step {self._step_count}.")
                self._dl.emit()
                ret = 0

        finally:
            # ── Final summary — ALWAYS executed ───────────────────────
            # Covers: natural completion, Ctrl+C, stream errors, and any
            # other exception path.  The log is closed inside _finalise.
            self._finalise(interrupted=self._interrupted)

        return ret

    # ------------------------------------------------------------------
    def _finalise(self, interrupted: bool) -> None:
        """Print the Final Summary block then close the log."""
        self._print_final_summary()
        self._dl.close()


# ---------------------------------------------------------------------------
# 7.  UTILITY
# ---------------------------------------------------------------------------

def _is_nan(v: float) -> bool:
    """True if *v* is NaN or non-numeric (uses top-level math import)."""
    try:
        return math.isnan(v)
    except (TypeError, ValueError):
        return True


def _resolve_binary(binary_arg: str) -> str:
    """
    Resolve the binary path.  Accepts:
      - 'run'           → search for `granite_main` in common build locations.
      - An absolute path  → used as-is.
      - A relative path   → resolved relative to CWD.
    """
    if binary_arg.lower() == "run":
        # Search heuristic: look in build/bin relative to CWD or parent dirs.
        candidates = [
            Path("build/bin/granite_main"),
            Path("build/bin/granite_main.exe"),
            Path("../build/bin/granite_main"),
            Path("../build/bin/granite_main.exe"),
        ]
        for c in candidates:
            if c.exists():
                return str(c.resolve())
        # Fallback: just return the string and let Popen fail with a clear error.
        return "granite_main"
    return binary_arg


# ---------------------------------------------------------------------------
# 8.  CLI ENTRY POINT
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sim_tracker.py",
        description=(
            "GRANITE Simulation Tracker — context-aware dashboard with 1:1 log mirroring."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "binary",
        help='Path to granite_main binary, or "run" to auto-detect.',
    )
    p.add_argument(
        "params",
        help="Path to the params.yaml configuration file.",
    )
    p.add_argument(
        "--log-dir",
        metavar="DIR",
        default=None,
        help="Directory for the .log file (default: <binary-parent>/../dev_logs/).",
    )
    return p


def main() -> None:
    parser = _build_parser()
    args   = parser.parse_args()

    binary = _resolve_binary(args.binary)

    tracker = GraniteTracker(
        binary   = binary,
        params   = args.params,
        log_dir  = args.log_dir,
    )

    try:
        exit_code = tracker.run()
    except KeyboardInterrupt:
        # Secondary safety net: if the SIGINT handler was bypassed (e.g., the
        # process was already inside a C extension at interrupt time), set the
        # flag and let _finalise() run via the try/finally in run().
        tracker._interrupted = True
        # Do NOT call run() again — just trigger finalise directly.
        tracker._finalise(interrupted=True)
        exit_code = 0

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
