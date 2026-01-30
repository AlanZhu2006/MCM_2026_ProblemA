"""
Demo script for the A_MCM_A battery model.
This script builds a small usage schedule and runs a short simulation,
printing a summary and a few trajectory checkpoints.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from battery_model import BatteryModel


def run_demo():
    model = BatteryModel(Q_Ah=3.8, V_nom=3.85, T_env_init=25.0, verbose=False)
    # Total duration: 2 hours, step every 60 seconds
    duration_s = 2 * 60 * 60
    dt_s = 60

    usage_day = {
        "start": 0,
        "end": 60 * 60,
        "usage": {
            "brightness": 0.9,
            "cpu_load": 0.8,
            "network": True,
            "gps": True,
            "background": True,
        },
    }
    usage_after = {
        "start": 60 * 60,
        "end": duration_s,
        "usage": {
            "brightness": 0.4,
            "cpu_load": 0.3,
            "network": True,
            "gps": False,
            "background": True,
        },
    }
    schedule = [usage_day, usage_after]

    ambient = [{"start": 0, "end": duration_s, "ambient_T": 25.0}]

    trajectory = model.simulate(duration_s, dt_s, schedule, ambient)
    # Ensure output directory exists for CSV export
    out_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "trajectory_demo.csv")
    try:
        model.export_csv(trajectory, csv_path)
        print(f"[Demo] CSV trajectory exported to: {csv_path}")
    except Exception as e:
        print("[Demo] Failed to export CSV:", e)

    print("[Demo] Final SOC: {:.3f}".format(trajectory["SOC"][-1]))
    print("[Demo] Final Temperature: {:.2f} C".format(trajectory["temp_C"][-1]))
    # Quick estimate of Time-To-Empty (very rough): use average current in last 5 steps
    if len(trajectory["I_A"]) >= 5:
        I_last = sum(trajectory["I_A"][-5:]) / 5.0
    else:
        I_last = trajectory["I_A"][-1] if trajectory["I_A"] else 0.0
    if I_last > 1e-6:
        # remaining Coulombs = Q_Ah * 3600 * SOC
        Q_left = model.Q_Ah * 3600.0 * trajectory["SOC"][-1]
        t_to_empty_s = Q_left / max(I_last, 1e-9)
        print("[Demo] Rough Time-to-Empty (s):", t_to_empty_s)
        print("[Demo] Rough Time-to-Empty (h):", t_to_empty_s / 3600.0)
    else:
        print("[Demo] Insufficient current data for TTE estimate.")


if __name__ == "__main__":
    run_demo()
