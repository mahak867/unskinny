"""Exploded isometric assembly drawing with numbered balloons."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import numpy as np, trimesh, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
OUTD = os.path.join(ROOT, "builder", "drawings"); SRC = os.path.join(ROOT, "out")
# part file, item no, name, explode offset (mm), colour
P = [("top_plate", 2, "Top plate UMK2-002", (0, 0, 120), "#c9ced3"), ("detail_bolts_top", 9, "M3/M4 cap screws", (0, 0, 140), "#333"),
     ("bar", 1, "Weapon bar UMK2-001", (0, 0, 60), "#8794a0"), ("detail_bolts_bar", 10, "4× M5×12 12.9 + Loctite 243", (0, 0, 75), "#333"),
     ("hub_motor", 6, "2812 hub motor", (0, 0, 0), "#2b2f33"), ("frame", 4, "Frame UMK2-004 (TPU)", (0, 0, 0), "#e0662a"),
     ("battery", 8, "4S 650 mAh LiPo", (0, 0, 95), "#2f6fb0"), ("detail_esc_0", 11, "Weapon ESC", (0, 30, 70), "#3b6e4d"),
     ("detail_esc_1", 12, "Drive ESC", (0, -30, 70), "#3b6e4d"), ("detail_receiver", 13, "Receiver", (0, 30, 105), "#111"),
     ("detail_switch", 14, "Power link", (0, -30, 105), "#c9a227"),
     ("drive_0", 7, "Drive motor (L/R)", (0, 45, 0), "#9aa0a6"), ("drive_1", 7, "", (0, -45, 0), "#9aa0a6"),
     ("wheel_0", 5, "Wheel + hub (L/R)", (0, 95, 0), "#1c1d1f"), ("wheel_1", 5, "", (0, -95, 0), "#1c1d1f"),
     ("bottom_plate", 3, "Bottom plate UMK2-003", (0, 0, -90), "#c9ced3"), ("detail_bolts_bottom", 9, "", (0, 0, -105), "#333"),
     ("fork", 15, "Fork UMK2-005", (40, 0, -125), "#9aa3a8")]
fig = plt.figure(figsize=(14, 10), dpi=150); ax = fig.add_axes([0, 0.06, 0.72, 0.92], projection="3d")
light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)
for f, n, name, off, col in P:
    m = trimesh.load(os.path.join(SRC, f + ".stl")); v = m.vertices + np.array(off)
    tri = v[m.faces]; nrm = m.face_normals; shade = 0.55 + 0.45 * np.clip(nrm @ light, 0, 1)
    base = np.array(matplotlib.colors.to_rgb(col)); fc = np.clip(base[None, :] * shade[:, None] + 0.08, 0, 1)
    ax.add_collection3d(Poly3DCollection(tri, facecolors=fc, edgecolors="none"))
    if name:
        c = v.mean(axis=0); tip = c + np.array([0, 0, 0])
        lab = c + np.array([-60 if c[0] < -100 else 70, 0, 45])
        ax.plot(*zip(tip, lab), color="#1f4e79", lw=.7)
        ax.text(*lab, f" {n} ", fontsize=9, weight="bold", color="white", bbox=dict(boxstyle="circle,pad=0.25", fc="#1f4e79", ec="none"))
ax.set_xlim(-260, 140); ax.set_ylim(-200, 200); ax.set_zlim(-200, 200); ax.set_box_aspect((1, 1, 1)); ax.axis("off"); ax.view_init(24, -58)
# parts list table
items = {}
for f, n, name, off, col in P:
    if name: items[n] = name
qty = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 1, 7: 2, 8: 1, 9: "12+4", 10: 4, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1}
tx = fig.add_axes([0.72, 0.1, 0.27, 0.85]); tx.axis("off")
tx.text(0, 1, "ITEM  QTY  DESCRIPTION", fontsize=9, weight="bold", family="monospace", va="top")
for i, n in enumerate(sorted(items)):
    tx.text(0, 0.96 - i * 0.045, f"{n:>3}   {str(qty[n]):>4}  {items[n]}", fontsize=8.5, family="monospace", va="top")
tx.text(0, 0.22, "Assembly order: 4 → 7 → 5 → 3 → 15 → 6 → 1 + 10\n→ 11/12/13/14/8 → 2 + 9.\nThreadlocker on all metal-metal threads.\nTorques: M3 0.8 N·m (into inserts 0.5),\nM4 2.0 N·m, M5 4.5 N·m.", fontsize=8.5, va="top")
fig.text(0.01, 0.02, "UMK2-A01 · Exploded assembly · Rev A · Unskinny Mk II", fontsize=11, weight="bold")
fig.savefig(os.path.join(OUTD, "UMK2-A01_exploded_assembly.png")); plt.close(fig); print("ok")
