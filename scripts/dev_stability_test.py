#!/usr/bin/env python3
"""
GRANITE Dev Stability Test — Automated pass/fail for single_puncture.

Runs the single_puncture benchmark and monitors three stability criteria:
  1. α_center stabilizes to [0.1, 0.4] by t=50M
  2. ‖H‖₂ stays below 1.0 for all t < 500M
  3. Advection CFL stays below 0.9 at all times

Usage:
    python3 dev_stability_test.py [--binary path/to/granite_main]
                                   [--params path/to/params.yaml]
                                   [--timeout SECONDS]
                                   [--t-target T_FINAL_M]
"""

import argparse
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StepRecord:
    step: int
    t: float
    alpha_center: float
    ham_l2: float
    adv_cfl: float = 0.0


@dataclass
class StabilityResult:
    passed: bool = True
    failures: List[str] = field(default_factory=list)
    records: List[StepRecord] = field(default_factory=list)
    wall_time: float = 0.0
    final_step: int = 0
    final_t: float = 0.0


def parse_output_line(line: str) -> Optional[StepRecord]:
    """Parse a diagnostic output line from granite_main."""
    # Match lines like: "  step=10  t=0.6250  α_center=0.01270  ||H||₂=0.3194  [Blocks: 1]"
    step_match = re.search(r'step=(\d+)', line)
    t_match = re.search(r't=([\d.]+)', line)
    alpha_match = re.search(r'α_center=([\d.eE+-]+)', line)
    ham_match = re.search(r'\|\|H\|\|.*?=([\d.eE+-]+|nan|NaN|inf)', line)

    if step_match and t_match and alpha_match and ham_match:
        ham_str = ham_match.group(1).lower()
        ham_val = float('nan') if ham_str in ('nan', 'inf') else float(ham_str)
        return StepRecord(
            step=int(step_match.group(1)),
            t=float(t_match.group(1)),
            alpha_center=float(alpha_match.group(1)),
            ham_l2=ham_val,
        )
    return None


def parse_cfl_line(line: str) -> Optional[float]:
    """Extract advection CFL from CFL-WARN/CFL-GUARD lines."""
    cfl_match = re.search(r'CFL=([\d.eE+-]+)', line)
    if cfl_match:
        return float(cfl_match.group(1))
    return None


def run_stability_test(
    binary: str,
    params: str,
    timeout: int = 7200,
    t_target: float = 100.0,
) -> StabilityResult:
    """Run granite_main and collect stability diagnostics."""
    result = StabilityResult()

    if not os.path.isfile(binary):
        result.passed = False
        result.failures.append(f"Binary not found: {binary}")
        return result

    if not os.path.isfile(params):
        result.passed = False
        result.failures.append(f"Params not found: {params}")
        return result

    start_time = time.time()

    try:
        proc = subprocess.Popen(
            [binary, params],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as e:
        result.passed = False
        result.failures.append(f"Failed to launch: {e}")
        return result

    max_cfl_seen = 0.0

    try:
        for line in proc.stdout:
            line = line.rstrip()
            print(line)  # echo to terminal

            # Parse step records
            record = parse_output_line(line)
            if record:
                result.records.append(record)
                result.final_step = record.step
                result.final_t = record.t

            # Parse CFL warnings
            cfl_val = parse_cfl_line(line)
            if cfl_val is not None:
                max_cfl_seen = max(max_cfl_seen, cfl_val)

            # Check for NaN crash
            if 'NaN' in line and 'all finite' not in line and 'NaN-DIAG' not in line:
                if 'ST var=' in line or 'CRASH' in line:
                    result.passed = False
                    result.failures.append(f"NaN detected: {line.strip()}")

            # Early exit if we've reached target time
            if result.records and result.records[-1].t >= t_target:
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=10)
                break

            # Timeout check
            elapsed = time.time() - start_time
            if elapsed > timeout:
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=10)
                result.failures.append(f"Timeout after {elapsed:.0f}s")
                break

    except Exception as e:
        result.failures.append(f"Error during monitoring: {e}")
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()

    result.wall_time = time.time() - start_time

    # ── Criterion 1: α_center stabilizes to [0.1, 0.4] by t=50M ──
    late_records = [r for r in result.records if r.t >= 50.0]
    if late_records:
        for r in late_records:
            if r.alpha_center < 0.1 or r.alpha_center > 0.4:
                result.passed = False
                result.failures.append(
                    f"CRIT-1 FAIL: α_center={r.alpha_center:.6e} at t={r.t:.2f}M "
                    f"(outside [0.1, 0.4])"
                )
                break
    elif t_target >= 50.0:
        result.passed = False
        result.failures.append("CRIT-1 FAIL: simulation did not reach t=50M")

    # ── Criterion 2: ‖H‖₂ < 1.0 for all t < 500M ──
    for r in result.records:
        if r.t < 500.0 and (r.ham_l2 > 1.0 or r.ham_l2 != r.ham_l2):  # NaN check
            result.passed = False
            result.failures.append(
                f"CRIT-2 FAIL: ||H||_2={r.ham_l2:.4e} at t={r.t:.2f}M (must be < 1.0)"
            )
            break

    # ── Criterion 3: max advection CFL < 0.9 ──
    if max_cfl_seen > 0.9:
        result.passed = False
        result.failures.append(
            f"CRIT-3 FAIL: max advection CFL={max_cfl_seen:.4f} (must be < 0.9)"
        )

    if result.failures:
        result.passed = False

    return result


def main():
    parser = argparse.ArgumentParser(description="GRANITE stability test")
    parser.add_argument(
        "--binary",
        default="build/bin/granite_main",
        help="Path to granite_main binary",
    )
    parser.add_argument(
        "--params",
        default="benchmarks/single_puncture/params.yaml",
        help="Path to parameter file",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=7200,
        help="Maximum wall time in seconds (default: 7200 = 2h)",
    )
    parser.add_argument(
        "--t-target",
        type=float,
        default=100.0,
        help="Target simulation time in M (default: 100.0)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  GRANITE DEV STABILITY TEST")
    print(f"  Binary: {args.binary}")
    print(f"  Params: {args.params}")
    print(f"  Target: t={args.t_target}M  (timeout={args.timeout}s)")
    print("=" * 70)

    result = run_stability_test(
        binary=args.binary,
        params=args.params,
        timeout=args.timeout,
        t_target=args.t_target,
    )

    print("\n" + "=" * 70)
    print("  STABILITY TEST RESULTS")
    print("=" * 70)
    print(f"  Wall time:   {result.wall_time:.1f}s")
    print(f"  Final step:  {result.final_step}")
    print(f"  Final t:     {result.final_t:.4f}M")

    if result.records:
        final = result.records[-1]
        print(f"  α_center:    {final.alpha_center:.6e}")
        print(f"  ||H||₂:     {final.ham_l2:.6e}")

    print()
    if result.passed:
        print("  ✅ PASS — all stability criteria met")
    else:
        print("  ❌ FAIL — stability criteria violated:")
        for f in result.failures:
            print(f"    • {f}")

    print("=" * 70)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
