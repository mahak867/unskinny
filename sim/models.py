"""Physics models for Unskinny Mk II. All functions are pure so they can be unit tested."""
import json, math, os, sys
import numpy as np
from scipy.integrate import solve_ivp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from params import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = 9.81

def cad_report():
    return json.load(open(os.path.join(ROOT, "out", "cad_report.json")))

def total_mass_g(rep=None):
    rep = rep or cad_report()
    return sum(rep["masses_g"].values()) + sum(BOUGHT.values())

def weapon_inertia(rep=None):
    rep = rep or cad_report()
    return rep["bar_Izz_kgm2"] + HUB_BELL_INERTIA

def v_batt(sag=0.9):
    return CELLS * V_CELL * sag

def spinup(I, kv=WEAPON_KV, R=WEAPON_R_OHM, i_lim=WEAPON_I_LIMIT, V=None, drag=2.0e-7, t_end=6.0):
    """DC-motor model of a brushless weapon with ESC current limit and aero drag (tau = drag*w^2)."""
    V = V or v_batt()
    kv_rad = kv * 2 * math.pi / 60
    kt = 1 / kv_rad
    def f(t, y):
        w = y[0]
        i = min(i_lim, max(0.0, (V - w / kv_rad) / R))
        return [(kt * i - drag * w * w) / I, i * V]
    sol = solve_ivp(f, (0, t_end), [0.0, 0.0], max_step=0.005)
    return sol.t, sol.y[0], sol.y[1]  # time, omega (rad/s), energy drawn from battery (J)

def time_to_fraction(t, w, frac=0.9):
    target = frac * w[-1]
    return float(t[np.argmax(w >= target)])

def kinetic_energy(I, w):
    return 0.5 * I * w ** 2

def bar_centrifugal_stress_mpa(w, kt_hole=3.0):
    """Peak hoop/tensile stress at the bar centre for a uniform bar, times a bolt-hole stress concentration."""
    r = BAR_L / 2000
    return RHO["steel"] * 1000 * w ** 2 * r ** 2 / 2 * kt_hole / 1e6

def bite_mm(w, closing_speed=3.0, teeth=2):
    rev_s = w / (2 * math.pi)
    return closing_speed / (teeth * rev_s) * 1000

def drive_top_speed(eff=0.8):
    wheel_rpm = DRIVE_KV * v_batt() * eff / DRIVE_GEAR
    return wheel_rpm * math.pi * WHEEL_D / 1000 / 60

def drive_accel(mass_kg, mu=0.9, eff=0.8):
    kt = 60 / (2 * math.pi * DRIVE_KV)
    f_motor = 2 * kt * DRIVE_I_LIMIT * DRIVE_GEAR * eff / (WHEEL_D / 2000)
    f = min(f_motor, mu * mass_kg * G)
    return f / mass_kg, f_motor, mu * mass_kg * G

def drive_sim(mass_kg, t_end=1.5):
    vmax = drive_top_speed(); a0, _, _ = drive_accel(mass_kg)
    t = np.linspace(0, t_end, 300)
    v = np.minimum(vmax, vmax * (1 - np.exp(-a0 * t / vmax)))
    x = np.cumsum(v) * (t[1] - t[0])
    return t, v, x

def gyro_tilt_ratio(I, w, turn_rate=6.0, mass_kg=1.33, half_track=0.07):
    """Ratio of gyroscopic torque from turning (I*w*Omega) to the gravity torque that keeps the bot flat."""
    return (I * w * turn_rate) / (mass_kg * G * half_track)

def match_energy_wh(I, w_full, spinups=8, weapon_eff=0.6, drive_avg_a=4.0, weapon_hold_w=25.0, t=180.0):
    weapon = spinups * kinetic_energy(I, w_full) / weapon_eff + weapon_hold_w * t
    drive = drive_avg_a * v_batt() * t
    return (weapon + drive) / 3600

def summary():
    rep = cad_report(); I = weapon_inertia(rep); m = total_mass_g(rep)
    t, w, e = spinup(I)
    wf = w[-1]
    a, fmot, ftrac = drive_accel(m / 1000)
    return {
        "total_mass_g": round(m, 1), "weight_margin_g": round(WEIGHT_LIMIT_G - m, 1),
        "weapon_inertia_kgm2": I,
        "weapon_rpm": round(wf * 60 / (2 * math.pi)),
        "spinup_90pct_s": round(time_to_fraction(t, w), 2),
        "weapon_energy_J": round(kinetic_energy(I, wf)),
        "tip_speed_mps": round(wf * BAR_L / 2000, 1),
        "bar_peak_stress_mpa": round(bar_centrifugal_stress_mpa(wf), 1),
        "bar_safety_factor": round(AR500_YIELD_MPA / bar_centrifugal_stress_mpa(wf), 1),
        "bite_mm_at_3mps": round(bite_mm(wf), 1),
        "drive_top_speed_mps": round(drive_top_speed(), 2),
        "drive_accel_mps2": round(a, 1), "drive_traction_limited": fmot > ftrac,
        "gyro_tilt_ratio_full_turn": round(gyro_tilt_ratio(I, wf, mass_kg=m / 1000), 1),
        "match_energy_wh": round(match_energy_wh(I, wf), 2),
        "battery_usable_wh": round(BATT_WH * 0.8, 2),
    }

if __name__ == "__main__":
    print(json.dumps(summary(), indent=2))
