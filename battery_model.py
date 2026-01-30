"""
MCM A - Smartphone Battery Drain: Lightweight Continuous-Time Model
This module provides a simple, parameterizable battery model suitable for quick
coding experiments and prototyping. It uses a continuous-time perspective by
updating State-of-Charge (SOC) with a time step dt using the instantaneous power
draw and an environment/temperature dependent effective capacity.

Model highlights (kept intentionally simple but extensible):
- SOC evolves via dSOC/dt = -(I(t) * dt) / (Q_eff * 3600)
- I(t) = P(t) / V_nom, P(t) is a sum of base and component powers
- Q_eff = Q_Ah * exp(-k_temp * (T - T_ref))  (temperature dependent capacity)
- Temperature dynamics approximated with a first-order thermal model:
  dT/dt = (P - h*(T - T_env)) / C_th

This is a pragmatic starting point: you can plug in different usage profiles and
ambient temperatures to study how SOC evolves under realistic but controllable settings.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class BatteryModel:
    def __init__(
        self,
        Q_Ah: float = 3.8,  # nominal capacity [Ah]
        V_nom: float = 3.85,  # nominal voltage [V]
        T_ref: float = 25.0,  # reference temperature for capacity [C]
        k_temp: float = 0.02,  # temperature sensitivity for capacity
        P_base: float = 0.20,  # baseline power (idle) [W]
        P_screen_base: float = 0.30,  # screen power factor baseline [W]
        P_screen_exp: float = 1.0,  # exponent for screen power (nonlinearity)
        P_cpu_idle: float = 0.10,  # CPU idle power [W]
        P_cpu_peak: float = 0.90,  # CPU peak power at full load [W]
        P_network: float = 0.25,  # network activity power [W]
        P_gps: float = 0.04,  # GPS power [W]
        P_background: float = 0.05,  # background apps power [W]
        P_cpu_exp: float = 1.0,  # exponent for CPU power curve used in P_CPU
        C_th: float = 600.0,  # thermal capacitance [J/K]
        h: float = 5.0,  # thermal conductance to environment [W/K]
        T_env_init: float = 25.0,  # ambient temp [C]
        verbose: bool = False,
    ) -> None:
        self.Q_Ah = Q_Ah
        self.V_nom = V_nom
        self.T_ref = T_ref
        self.k_temp = k_temp
        self.P_base = P_base
        self.P_screen_base = P_screen_base
        self.P_cpu_idle = P_cpu_idle
        self.P_cpu_peak = P_cpu_peak
        self.P_network = P_network
        self.P_gps = P_gps
        self.P_background = P_background
        self.P_screen_exp = P_screen_exp
        self.P_cpu_exp = P_cpu_exp
        self.C_th = C_th
        self.h = h
        self.T_env = float(T_env_init)
        self.T = float(T_env_init)
        self.SOC = 1.0  # 0..1
        self.verbose = verbose

    def reset(self, soc: float = 1.0, T: Optional[float] = None) -> None:
        self.SOC = max(0.0, min(1.0, soc))
        if T is not None:
            self.T = float(T)
            self.T_env = float(T)
        else:
            self.T = self.T_env

    def compute_power(self, usage: Dict[str, Any]) -> float:
        brightness = usage.get("brightness", 0.5)
        cpu_load = usage.get("cpu_load", 0.5)
        network = usage.get("network", True)
        gps = usage.get("gps", True)
        background = usage.get("background", True)
        P_screen = self.P_screen_base * (brightness**self.P_screen_exp)
        P_CPU = self.P_cpu_idle + (self.P_cpu_peak - self.P_cpu_idle) * (
            cpu_load**self.P_cpu_exp
        )
        P_network = self.P_network if network else 0.0
        P_GPS = self.P_gps if gps else 0.0
        P_background = self.P_background if background else 0.0
        P = self.P_base + P_screen + P_CPU + P_network + P_GPS + P_background
        # store per-component powers for later export
        self._last_p_components = {
            "P_screen": P_screen,
            "P_CPU": P_CPU,
            "P_network": P_network,
            "P_GPS": P_GPS,
            "P_background": P_background,
        }
        return max(0.0, P)

    def step(
        self, dt_s: float, usage: Dict[str, Any], ambient_T: Optional[float] = None
    ) -> Dict[str, float]:
        P = self.compute_power(usage)
        # pull per-component powers from the last computation
        comps = getattr(self, "_last_p_components", {})
        P_screen = comps.get("P_screen", 0.0)
        P_CPU = comps.get("P_CPU", 0.0)
        P_network = comps.get("P_network", 0.0)
        P_GPS = comps.get("P_GPS", 0.0)
        P_background = comps.get("P_background", 0.0)
        if ambient_T is not None:
            self.T_env = float(ambient_T)
        # Temperature dynamics (first-order)
        self.T += dt_s * (P - self.h * (self.T - self.T_env)) / float(self.C_th)
        # Effective capacity depends on temperature
        Q_eff = self.Q_Ah * math.exp(-self.k_temp * (self.T - self.T_ref))
        Q_eff = max(Q_eff, 0.1 * self.Q_Ah)
        I = P / max(self.V_nom, 1e-6)
        dSOC = -(I * dt_s) / (Q_eff * 3600.0)
        self.SOC = max(0.0, min(1.0, self.SOC + dSOC))
        return {
            "SOC": self.SOC,
            "T": self.T,
            "P": P,
            "I": I,
            "Q_eff": Q_eff,
            "P_screen": P_screen,
            "P_CPU": P_CPU,
            "P_network": P_network,
            "P_GPS": P_GPS,
            "P_background": P_background,
        }

    def _get_usage_at_time(
        self, t: float, schedule: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        if not schedule:
            return {
                "brightness": 0.6,
                "cpu_load": 0.5,
                "network": True,
                "gps": True,
                "background": True,
            }
        for seg in schedule:
            if seg.get("start", 0) <= t < seg.get("end", float("inf")):
                return seg.get(
                    "usage",
                    {
                        "brightness": 0.6,
                        "cpu_load": 0.5,
                        "network": True,
                        "gps": True,
                        "background": True,
                    },
                )
        return {
            "brightness": 0.6,
            "cpu_load": 0.5,
            "network": True,
            "gps": True,
            "background": True,
        }

    def _get_ambient_at_time(self, t: float, ambient_schedule: Optional[Any]) -> float:
        if ambient_schedule is None:
            return self.T_env
        if isinstance(ambient_schedule, list):
            for seg in ambient_schedule:
                if seg.get("start", 0) <= t < seg.get("end", float("inf")):
                    return seg.get("ambient_T", self.T_env)
            return self.T_env
        if isinstance(ambient_schedule, dict):
            if "ambient_T" in ambient_schedule:
                return ambient_schedule["ambient_T"]
        return self.T_env

    def simulate(
        self,
        duration_s: float,
        dt_s: float,
        usage_schedule: Optional[List[Dict[str, Any]]],
        ambient_schedule: Optional[Any] = None,
    ) -> Dict[str, List[Any]]:
        times: List[float] = []
        socs: List[float] = []
        temps: List[float] = []
        powers: List[float] = []
        currents: List[float] = []
        q_effs: List[float] = []
        brightness_seq: List[float] = []
        cpu_load_seq: List[float] = []
        network_seq: List[bool] = []
        gps_seq: List[bool] = []
        background_seq: List[bool] = []
        ambient_seq: List[float] = []
        P_screen_seq: List[float] = []
        P_CPU_seq: List[float] = []
        P_network_seq: List[float] = []
        P_GPS_seq: List[float] = []
        P_background_seq: List[float] = []
        t = 0.0
        while t < duration_s:
            usage = self._get_usage_at_time(t, usage_schedule)
            ambient = self._get_ambient_at_time(t, ambient_schedule)
            # basic usage fields
            brightness_seq.append(usage.get("brightness", 0.5))
            cpu_load_seq.append(usage.get("cpu_load", 0.5))
            network_seq.append(bool(usage.get("network", True)))
            gps_seq.append(bool(usage.get("gps", True)))
            background_seq.append(bool(usage.get("background", True)))
            ambient_seq.append(float(ambient))
            res = self.step(dt_s, usage, ambient)
            times.append(t)
            socs.append(res["SOC"])
            temps.append(res["T"])
            powers.append(res["P"])
            currents.append(res["I"])
            q_effs.append(res["Q_eff"])
            # per-component powers (from last step computation)
            P_screen_seq.append(res.get("P_screen", 0.0))
            P_CPU_seq.append(res.get("P_CPU", 0.0))
            P_network_seq.append(res.get("P_network", 0.0))
            P_GPS_seq.append(res.get("P_GPS", 0.0))
            P_background_seq.append(res.get("P_background", 0.0))
            t += dt_s
        return {
            "time_s": times,
            "SOC": socs,
            "temp_C": temps,
            "P_W": powers,
            "I_A": currents,
            "Q_eff_Ah": q_effs,
            # per-step inputs for CSV export
            "brightness": brightness_seq,
            "cpu_load": cpu_load_seq,
            "network": network_seq,
            "gps": gps_seq,
            "background": background_seq,
            "ambient_T": ambient_seq,
            # per-step component power breakdown (W)
            "P_screen_W": P_screen_seq,
            "P_CPU_W": P_CPU_seq,
            "P_network_W": P_network_seq,
            "P_GPS_W": P_GPS_seq,
            "P_background_W": P_background_seq,
        }

    def report_summary(self) -> str:
        return "SOC={:.3f}, T={:.2f}C, V_nom={:.2f}V".format(
            self.SOC, self.T, self.V_nom
        )

    def export_csv(self, trajectory: Dict[str, List[Any]], filename: str) -> None:
        """Export a trajectory dictionary to a structured CSV file.

        Expected trajectory keys:
          time_s, SOC, temp_C, P_W, I_A, Q_eff_Ah,
          brightness, cpu_load, network, gps, background, ambient_T
        """
        import csv
        import os

        keys = [
            "time_s",
            "SOC",
            "temp_C",
            "P_W",
            "I_A",
            "Q_eff_Ah",
            "brightness",
            "cpu_load",
            "network",
            "gps",
            "background",
            "ambient_T",
            "P_screen_W",
            "P_CPU_W",
            "P_network_W",
            "P_GPS_W",
            "P_background_W",
        ]
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
        # Write CSV
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            n = len(trajectory.get("time_s", []))
            for i in range(n):
                row = {
                    "time_s": trajectory["time_s"][i],
                    "SOC": trajectory["SOC"][i],
                    "temp_C": trajectory["temp_C"][i],
                    "P_W": trajectory["P_W"][i],
                    "I_A": trajectory["I_A"][i],
                    "Q_eff_Ah": trajectory["Q_eff_Ah"][i],
                    "brightness": trajectory["brightness"][i],
                    "cpu_load": trajectory["cpu_load"][i],
                    "network": int(trajectory["network"][i]),
                    "gps": int(trajectory["gps"][i]),
                    "background": int(trajectory["background"][i]),
                    "ambient_T": trajectory["ambient_T"][i],
                    "P_screen_W": trajectory["P_screen_W"][i],
                    "P_CPU_W": trajectory["P_CPU_W"][i],
                    "P_network_W": trajectory["P_network_W"][i],
                    "P_GPS_W": trajectory["P_GPS_W"][i],
                    "P_background_W": trajectory["P_background_W"][i],
                }
                writer.writerow(row)
