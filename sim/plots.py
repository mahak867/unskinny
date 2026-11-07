"""Generate simulation plots, 3D renders and a spinning-weapon demo GIF into out/."""
import os, sys, math, json
import numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models import *

OUT = os.path.join(ROOT, "out")
COL = {"bar": "#7d8b94", "top_plate": "#b9bfc4", "bottom_plate": "#b9bfc4", "frame": "#e0662a",
       "hub_motor": "#2b2f33", "battery": "#2f6fb0", "fork": "#9aa3a8"}

def load_parts(skip=()):
    parts = {}
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".stl") and f[:-4] not in skip:
            parts[f[:-4]] = trimesh.load(os.path.join(OUT, f))
    return parts

def draw(ax, parts, bar_angle=0.0, alpha=1.0):
    for n, m in parts.items():
        v = m.vertices.copy()
        if n == "bar" and bar_angle:
            c, s = math.cos(bar_angle), math.sin(bar_angle)
            v[:, :2] = v[:, :2] @ np.array([[c, s], [-s, c]])
        a = 0.35 if n == "top_plate" else alpha
        ax.add_collection3d(Poly3DCollection(v[m.faces], facecolors=COL.get(n, "#3a3f44"),
                                             edgecolor="none", alpha=a, shade=True))
    ax.set_xlim(-240, 120); ax.set_ylim(-180, 180); ax.set_zlim(-180, 180)
    ax.set_box_aspect((1, 1, 1)); ax.axis("off")

def renders():
    parts = load_parts()
    for name, (el, az) in {"render_iso": (25, -60), "render_top": (89, -90), "render_front": (5, 0)}.items():
        fig = plt.figure(figsize=(8, 8), dpi=110); ax = fig.add_subplot(projection="3d")
        draw(ax, parts); ax.view_init(el, az)
        fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", transparent=False, facecolor="white"); plt.close(fig)

def spin_gif():
    parts = load_parts()
    fig = plt.figure(figsize=(5, 5), dpi=80); ax = fig.add_subplot(projection="3d")
    def frame(i):
        ax.clear(); draw(ax, parts, bar_angle=i * math.pi / 9); ax.view_init(30, -60 + i * 2)
    animation.FuncAnimation(fig, frame, frames=36).save(os.path.join(OUT, "demo_spin.gif"), writer="pillow", fps=12)
    plt.close(fig)

def sim_plots():
    rep = cad_report(); I = weapon_inertia(rep); m = total_mass_g(rep) / 1000
    t, w, e = spinup(I)
    fig, axs = plt.subplots(2, 2, figsize=(11, 8), dpi=110)
    ax = axs[0, 0]; ax.plot(t, w * 60 / (2 * math.pi), color="#c2410c"); ax.set(title="Weapon spin-up", xlabel="time (s)", ylabel="rpm"); ax.grid(alpha=.3)
    ax = axs[0, 1]; ax.plot(t, kinetic_energy(I, w), color="#3f5a66"); ax.set(title="Stored weapon energy", xlabel="time (s)", ylabel="J"); ax.grid(alpha=.3)
    td, v, x = drive_sim(m)
    ax = axs[1, 0]; ax.plot(td, v, color="#2f7d4f"); ax.set(title="Drive acceleration from standstill", xlabel="time (s)", ylabel="m/s"); ax.grid(alpha=.3)
    ws = np.linspace(100, w[-1], 50)
    ax = axs[1, 1]; ax.plot(ws * 60 / (2 * math.pi), [bite_mm(x) for x in ws], color="#7a5195")
    ax.set(title="Bite depth at 3 m/s closing", xlabel="weapon rpm", ylabel="mm"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "sim_results.png")); plt.close(fig)

    names = list(rep["masses_g"]) + list(BOUGHT); vals = list(rep["masses_g"].values()) + list(BOUGHT.values())
    fig, ax = plt.subplots(figsize=(9, 5), dpi=110)
    ax.barh(names, vals, color="#3f5a66"); ax.invert_yaxis()
    ax.set(title=f"Weight budget: {sum(vals):.0f} g of {WEIGHT_LIMIT_G} g", xlabel="grams"); ax.grid(axis="x", alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "weight_budget.png")); plt.close(fig)

if __name__ == "__main__":
    sim_plots(); renders(); spin_gif()
    json.dump(summary(), open(os.path.join(OUT, "sim_summary.json"), "w"), indent=2)
    print("done")
