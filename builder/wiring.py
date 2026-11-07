"""Electrical wiring diagram for Unskinny Mk II: every wire on its own route, colour-coded."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drawings")
os.makedirs(OUT, exist_ok=True)
RED, BLK, SIG, PH, INK = "#c62828", "#222222", "#1565c0", "#6a1b9a", "#111"

fig, ax = plt.subplots(figsize=(16, 10), dpi=150); ax.set_xlim(-1, 23); ax.set_ylim(-2.2, 11.2); ax.axis("off"); ax.set_aspect("equal")

def box(x, y, w, h, title, sub, col="#f4f6f8"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=col, ec=INK, lw=1.6))
    ax.text(x + w/2, y + h - 0.3, title, ha="center", va="top", fontsize=11, weight="bold")
    ax.text(x + w/2, y + h - 0.75, sub, ha="center", va="top", fontsize=8, color="#444", linespacing=1.3)
def pin(x, y, name, side):
    ax.plot(x, y, "o", ms=4, color=INK)
    ax.text(x + (0.12 if side == "L" else -0.12), y, name, ha="left" if side == "L" else "right", va="center", fontsize=8.5, family="monospace")
def wire(pts, col, lw=2.2, label=None, lpos=None):
    xs, ys = zip(*pts); ax.plot(xs, ys, color=col, lw=lw, solid_capstyle="round", zorder=1)
    if label: ax.text(*lpos, label, fontsize=8, color=col, ha="center", va="bottom", weight="bold")
def dot(x, y, col): ax.plot(x, y, "o", ms=6, color=col, zorder=3)
def motor(x, y, label):
    ax.add_patch(Circle((x, y), 0.55, fc="white", ec=PH, lw=2)); ax.text(x, y, "M\n3~", ha="center", va="center", fontsize=8.5, color=PH, weight="bold")
    ax.text(x + 0.75, y, label, ha="left", va="center", fontsize=8.5, color=PH)

# --- Battery, connector, power link ---
box(-0.6, 7.2, 3.0, 2.4, "BATTERY", "4S LiPo 650 mAh 75C\n14.8 V nom / 16.8 V full\nXT30 lead", "#fff4e5")
pin(2.4, 9.0, "+", "R"); pin(2.4, 7.8, "−", "R")
wire([(2.4, 9.0), (3.4, 9.0)], RED); ax.text(2.9, 9.12, "XT30", fontsize=8, ha="center", va="bottom")
box(3.4, 8.4, 2.2, 1.25, "POWER LINK", "removable / switch", "#fdecea")
wire([(5.6, 9.0), (11.0, 9.0)], RED, label="+ BUS  14 AWG", lpos=(12.3, 9.1))
wire([(2.4, 7.8), (2.8, 7.8), (2.8, 6.4), (0.3, 6.4), (0.3, -0.8), (17.0, -0.8)], BLK, label="GND BUS  14 AWG", lpos=(15.5, -0.7))

# --- Weapon ESC ---
WX, WY = 11.0, 5.6
box(WX, WY, 3.6, 2.8, "WEAPON ESC", "60–80 A · 4S\nAM32 / BLHeli_32\nno BEC · 1–2 s ramp")
for n, y in (("+", 7.8), ("−", 7.3), ("SIG", 6.6), ("S−", 6.1)): pin(WX, y, n, "L")
for n, y in (("A", 7.6), ("B", 7.0), ("C", 6.4)): pin(WX + 3.6, y, n, "R")
wire([(10.4, 9.0), (10.4, 7.8), (WX, 7.8)], RED); dot(10.4, 9.0, RED)
wire([(WX, 7.3), (9.9, 7.3), (9.9, -0.8)], BLK); dot(9.9, -0.8, BLK)
for y in (7.6, 7.0, 6.4): wire([(WX + 3.6, y), (17.2, y)], PH)
wire([(17.2, 7.6), (17.2, 6.4)], PH); wire([(17.2, 7.0), (17.8, 7.0)], PH)
ax.text(16.0, 7.75, "3 × 14 AWG", fontsize=8, color=PH, ha="center")
motor(18.35, 7.0, "WEAPON\n2812 hub motor\n~900 kV")

# --- Drive ESC ---
DX, DY = 11.0, 0.2
box(DX, DY, 3.6, 4.6, "DRIVE ESC", "dual brushless · 4S\nreversing · BEC 5 V")
for n, y in (("+", 3.0), ("−", 2.6), ("CH1", 2.0), ("CH2", 1.6), ("5V", 1.2), ("S−", 0.8)): pin(DX, y, n, "L")
for n, y in (("L-A", 3.9), ("L-B", 3.4), ("L-C", 2.9), ("R-A", 2.0), ("R-B", 1.5), ("R-C", 1.0)): pin(DX + 3.6, y, n, "R")
wire([(9.4, 9.0), (9.4, 3.0), (DX, 3.0)], RED, label="18 AWG", lpos=(8.95, 5.0)); dot(9.4, 9.0, RED)
wire([(DX, 2.6), (8.9, 2.6), (8.9, -0.8)], BLK); dot(8.9, -0.8, BLK)
for ys, cx, lab in (((3.9, 3.4, 2.9), 17.2, "LEFT DRIVE\n24 mm brushless\n27:1 planetary"), ((2.0, 1.5, 1.0), 17.2, "RIGHT DRIVE\n24 mm brushless\n27:1 planetary")):
    for y in ys: wire([(DX + 3.6, y), (cx, y)], PH)
    wire([(cx, ys[0]), (cx, ys[2])], PH); wire([(cx, ys[1]), (cx + 0.6, ys[1])], PH); motor(cx + 1.15, ys[1], lab)
ax.text(16.0, 4.05, "3 × 18 AWG each", fontsize=8, color=PH, ha="center")

# --- Receiver ---
RX, RY = 1.0, 1.0
box(RX, RY, 3.0, 4.6, "RECEIVER", "ELRS / FrSky / FlySky\nFAILSAFE: all outputs OFF")
pins = {"CH1": 4.0, "CH2": 3.5, "CH3": 3.0, "5V": 2.0, "GND": 1.5}
for n, y in pins.items(): pin(RX + 3.0, y, n, "R")
ax.text(RX + 0.2, 4.0, "steer", fontsize=7.5, color="#555"); ax.text(RX + 0.2, 3.5, "throttle", fontsize=7.5, color="#555"); ax.text(RX + 0.2, 3.0, "weapon", fontsize=7.5, color="#555")
X0 = RX + 3.0
wire([(X0, 3.0), (5.0, 3.0), (5.0, 6.6), (WX, 6.6)], SIG)                     # CH3 -> weapon SIG
wire([(X0, 1.5), (4.6, 1.5), (4.6, 6.1), (WX, 6.1)], BLK, lw=1.4); wire([(2.5, RY), (2.5, -0.8)], BLK, lw=0)             # GND -> weapon S-
wire([(X0, 4.0), (6.0, 4.0), (6.0, 2.0), (DX, 2.0)], SIG)                     # CH1
wire([(X0, 3.5), (6.6, 3.5), (6.6, 1.6), (DX, 1.6)], SIG)                     # CH2
wire([(X0, 2.0), (7.2, 2.0), (7.2, 1.2), (DX, 1.2)], RED, lw=1.4)             # 5V from BEC
wire([(X0, 1.5), (7.8, 1.5), (7.8, 0.8), (DX, 0.8)], BLK, lw=1.4)             # GND
dot(4.6, 1.5, BLK)
ax.text(5.3, 6.75, "CH3 signal", fontsize=8, color=SIG); ax.text(5.2, 4.75, "CH1/CH2 signal + 5 V/GND\n(servo leads, 26 AWG)", fontsize=8, color=SIG)

# legend + notes
for i, (c, t) in enumerate(((RED, "Battery + / 5 V"), (BLK, "Ground"), (SIG, "PWM / PPM signal"), (PH, "Motor phases"))):
    ax.plot([17.6, 18.2], [4.9 - i*0.35 - 0.2] * 2, color=c, lw=3) if False else (ax.plot([18.0, 18.6], [10.6 - i*0.35] * 2, color=c, lw=3), ax.text(18.75, 10.6 - i*0.35, t, va="center", fontsize=8.5))
notes = ("NOTES  1. Receiver is powered ONLY from the drive-ESC BEC; weapon ESC has no BEC (if yours has one, remove its red servo wire).   "
         "2. Swap any two phase wires to reverse a motor.\n3. Arcade mixing on the transmitter OR the ESC, not both.   "
         "4. All joints soldered + heat-shrunk; strain-relief every lead; keep phase wires short.   5. Power link must be reachable with the robot fully assembled.")
ax.text(-0.6, -1.7, notes, fontsize=8, va="center")
ax.text(-0.6, 10.9, "UMK2-E01 · Wiring diagram · Rev A", ha="left", fontsize=11, weight="bold")
fig.savefig(os.path.join(OUT, "UMK2-E01_wiring.png"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "UMK2-E01_wiring.svg"), bbox_inches="tight")
print("ok")
