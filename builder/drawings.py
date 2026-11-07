"""Dimensioned 2D manufacturing drawings generated from the CadQuery model."""
import os, sys, math, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "cad")]
import cadquery as cq
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import build
from params import *

OUT = os.path.join(ROOT, "builder", "drawings")
INK, DIM, CL = "#111", "#1f4e79", "#999"

def section_polys(solid, z=None):
    """Outline + holes of the part's top face, as polylines (exact CAD edges)."""
    polys = []
    for e in solid.faces(">Z").edges().vals():
        n = max(6, int(e.Length() / 1.0))
        polys.append([(p.x, p.y) for p in [e.positionAt(i / n) for i in range(n + 1)]])
    return polys

def hdim(ax, x1, x2, y, text, off=8):
    ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", color=DIM, lw=.8, shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + 1.5, text, ha="center", va="bottom", color=DIM, fontsize=8)

def vdim(ax, x, y1, y2, text):
    ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<->", color=DIM, lw=.8, shrinkA=0, shrinkB=0))
    ax.text(x - 2, (y1 + y2) / 2, text, ha="right", va="center", color=DIM, fontsize=8, rotation=90)

def ext(ax, pts):
    for (x1, y1), (x2, y2) in pts:
        ax.plot([x1, x2], [y1, y2], color=DIM, lw=.4)

def title_block(fig, part, no, material, thk, qty, process, notes):
    tb = fig.add_axes([0.0, 0.0, 1.0, 0.16]); tb.axis("off")
    tb.add_patch(Rectangle((0.01, 0.05), 0.98, 0.9, fill=False, lw=1.2, color=INK, transform=tb.transAxes))
    cells = [("PART", part, .01, .30), ("DWG NO.", no, .31, .12), ("MATERIAL", material, .43, .22), ("THICKNESS", thk, .65, .10),
             ("QTY", qty, .75, .06), ("UNITS / SCALE", "mm / fit", .81, .18)]
    for lab, val, x, w in cells:
        tb.add_patch(Rectangle((x, .5), w, .45, fill=False, lw=.6, color=INK, transform=tb.transAxes))
        tb.text(x + .005, .88, lab, fontsize=6, color="#555", transform=tb.transAxes, va="top")
        tb.text(x + .005, .58, val, fontsize=9, weight="bold", transform=tb.transAxes)
    tb.add_patch(Rectangle((.01, .05), .98, .45, fill=False, lw=.6, color=INK, transform=tb.transAxes))
    tb.text(.015, .42, "PROCESS: " + process, fontsize=7.5, transform=tb.transAxes, va="top")
    tb.text(.015, .26, "NOTES: " + notes, fontsize=7, transform=tb.transAxes, va="top", wrap=True)
    tb.text(.985, .1, f"UNSKINNY MK II · REV A · {datetime.date.today():%Y-%m-%d} · Drawn: Mahak · Master geometry: STEP/DXF in out/",
            fontsize=6.5, ha="right", transform=tb.transAxes, color="#444")

def sheet(name):
    fig = plt.figure(figsize=(11.69, 8.27), dpi=150)  # A4 landscape
    ax = fig.add_axes([0.04, 0.2, 0.92, 0.76]); ax.set_aspect("equal"); ax.axis("off")
    return fig, ax

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png")); fig.savefig(os.path.join(OUT, name + ".svg")); plt.close(fig)

def draw_polys(ax, polys, lw=1.2):
    for p in polys:
        xs, ys = zip(*p); ax.plot(xs, ys, color=INK, lw=lw)

def centerlines(ax, xr, yr):
    ax.plot(xr, [0, 0], color=CL, lw=.6, ls=(0, (12, 3, 2, 3))); ax.plot([0, 0], yr, color=CL, lw=.6, ls=(0, (12, 3, 2, 3)))

def bar_drawing(s):
    fig, ax = sheet("bar")
    draw_polys(ax, section_polys(s["bar"], 0))
    L, W = BAR_L, BAR_W
    centerlines(ax, [-L/2 - 10, L/2 + 10], [-W/2 - 10, W/2 + 10])
    hdim(ax, -L/2, L/2, W/2 + 18, f"{L:.0f}"); ext(ax, [((-L/2, W/2), (-L/2, W/2 + 20)), ((L/2, W/2), (L/2, W/2 + 20))])
    vdim(ax, -L/2 - 14, -W/2, W/2, f"{W:.0f}"); ext(ax, [((-L/2, -W/2), (-L/2 - 16, -W/2)), ((-L/2, W/2), (-L/2 - 16, W/2))])
    ax.annotate(f"Ø{BAR_BORE:.0f} THRU (pilot)", (0, 0), (25, -W/2 - 22), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate(f"4× Ø{BAR_BOLT_D} THRU on Ø{BAR_HOLE_PCD:.0f} PCD, 45°\nfor M5 grade 12.9 to hub bell", (15*math.cos(math.pi/4), -15*math.sin(math.pi/4)),
                (-95, -W/2 - 30), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("2× slot 28 × 12, R6 ends, centres ±42", (42, 0), (60, W/2 + 30), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("Tooth chamfer 14 × 45°\n(impact face, 2 places)", (L/2 - 7, W/2 - 7), (L/2 - 40, W/2 + 42), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    hdim(ax, 0, 42, -W/2 - 8, "42")
    ax.text(-L/2, -W/2 - 48, "Direction of rotation: counter-clockwise viewed from top. Leading edges = chamfered corners.", fontsize=8)
    ax.set_xlim(-L/2 - 40, L/2 + 30); ax.set_ylim(-W/2 - 60, W/2 + 60)
    title_block(fig, "Weapon bar", "UMK2-001", "AR500 (or S7 tool steel)", f"{BAR_T} mm", "2 (1 spare)",
                "Waterjet or laser from bar.dxf. Grind 30° bevel on impact faces. Static + dynamic balance to < 0.5 g·mm.",
                "General tol ±0.2; bolt holes +0.1/-0; bore concentric to PCD within 0.05. Break all edges 0.3. Mass 304 g ± 5 g.")
    save(fig, "UMK2-001_weapon_bar")

def plate_drawing(s, top):
    fig, ax = sheet("plate")
    solid = s["top_plate" if top else "bottom_plate"]
    z = (PLATE_GAP/2 + PLATE_T/2) * (1 if top else -1)
    draw_polys(ax, section_polys(solid, z))
    centerlines(ax, [PLATE_REAR_X - 10, PLATE_FRONT_X + 15], [-PLATE_HALF_W - 10, PLATE_HALF_W + 10])
    y0 = PLATE_HALF_W + 18
    hdim(ax, PLATE_REAR_X, PLATE_FRONT_X, y0 + 14, f"{PLATE_FRONT_X - PLATE_REAR_X:.0f} overall")
    hdim(ax, 0, PLATE_FRONT_X, y0, f"{PLATE_FRONT_X:.0f}")
    hdim(ax, POD_FRONT_X - 10, 0, y0, f"{-(POD_FRONT_X - 10):.0f}")
    ext(ax, [((PLATE_REAR_X, 0), (PLATE_REAR_X, y0 + 16)), ((PLATE_FRONT_X, 0), (PLATE_FRONT_X, y0 + 16)), ((0, 0), (0, y0 + 2))])
    vdim(ax, PLATE_REAR_X - 14, -PLATE_HALF_W, PLATE_HALF_W, f"{2*PLATE_HALF_W:.0f}")
    vdim(ax, PLATE_FRONT_X + 12, -TONGUE_HALF_W, TONGUE_HALF_W, f"{2*TONGUE_HALF_W:.0f}")
    ax.annotate("Weapon axis (datum A)\n4× Ø4.2 on Ø25 PCD (M4 motor)\nØ9 shaft clearance", (0, 0), (-70, -PLATE_HALF_W - 45), fontsize=8, color=DIM,
                arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("6× Ø3.4 (M3 into heat-set inserts)", (POD_FRONT_X - 6, -45), (POD_FRONT_X + 10, -PLATE_HALF_W - 22), fontsize=8, color=DIM,
                arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("Wheel slot 70 × 24, both sides", (WHEEL_X, PLATE_HALF_W - 12), (WHEEL_X - 60, PLATE_HALF_W + 45), fontsize=8, color=DIM,
                arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("4× lightening pocket 32 × 22 THRU", (-215, -30), (-250, -PLATE_HALF_W - 22), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.set_xlim(PLATE_REAR_X - 40, PLATE_FRONT_X + 40); ax.set_ylim(-PLATE_HALF_W - 60, PLATE_HALF_W + 60)
    name = "Top plate" if top else "Bottom plate"
    title_block(fig, name, "UMK2-002" if top else "UMK2-003", "Ti-6Al-4V (grade 5)", f"{PLATE_T} mm", "1 (+1 spare)",
                "Laser or waterjet from " + ("top" if top else "bottom") + "_plate.dxf. Deburr. Motor holes reamed for location.",
                "Tol ±0.15; corner radii R6; motor PCD true position Ø0.1 to datum A. Bottom plate also carries the fork (drill 2× Ø3.4 per fork drawing).")
    save(fig, "UMK2-002_top_plate" if top else "UMK2-003_bottom_plate")

def frame_drawing(s):
    fig, ax = sheet("frame")
    draw_polys(ax, section_polys(s["frame"], 0))
    L0, L1 = PLATE_REAR_X, POD_FRONT_X
    hdim(ax, L0 + 0, -BAR_L/2 - 13.5, PLATE_HALF_W + 16, f"{-BAR_L/2 - 13.5 - L0:.0f} (to sweep arc)")
    vdim(ax, L0 - 12, -PLATE_HALF_W + 1, PLATE_HALF_W - 1, f"{2*PLATE_HALF_W - 2:.0f}")
    ax.annotate(f"Front face R{BAR_L/2 + 13.5:.1f} about weapon axis (13.5 mm clearance)", (-BAR_L/2 - 13.5, 0), (-110, -PLATE_HALF_W - 25),
                fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate(f"Battery bay {BATT[0]+2:.0f} × {BATT[1]+2:.0f} THRU", (BATT_X, 0), (BATT_X - 70, -PLATE_HALF_W - 40), fontsize=8, color=DIM,
                arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("2× ESC bay 30 × 28", (-150, 60), (-130, PLATE_HALF_W + 35), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate(f"2× drive motor bore Ø{DRIVE_D + 0.6:.1f}, axis x={WHEEL_X:.0f}", (WHEEL_X, 40), (WHEEL_X - 25, PLATE_HALF_W + 50), fontsize=8, color=DIM,
                arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.text(L0, -PLATE_HALF_W - 62, f"Height {PLATE_GAP:.0f} mm (between plates). x positions measured from weapon axis (datum A).", fontsize=8)
    ax.set_xlim(L0 - 40, -60); ax.set_ylim(-PLATE_HALF_W - 70, PLATE_HALF_W + 60)
    title_block(fig, "Frame (rear pod)", "UMK2-004", "TPU 95A", f"{PLATE_GAP:.0f} mm tall", "1 (+1 spare)",
                "FDM print from frame.stl/frame.step: 0.2 mm layers, 5 walls, 45% gyroid, 0.4 nozzle, 230 °C, slow (30 mm/s).",
                "Install 12× M3 heat-set inserts (6 top, 6 bottom) at plate hole positions. Print flat. Check bores with a drive motor before final assembly.")
    save(fig, "UMK2-004_frame")

def fork_drawing(s):
    fig, ax = sheet("fork")
    ax.plot([0, 70], [0, 0], color=INK, lw=1.2)  # flat developed length
    ax.plot([0, 0, 70, 70, 0], [0, 44, 44, 0, 0], color=INK, lw=1.2)
    ax.plot([10, 10], [0, 44], color=DIM, lw=.8, ls="--")
    for y in (12, 32): ax.add_patch(plt.Circle((5, y), 1.7, fill=False, color=INK, lw=1))
    hdim(ax, 0, 70, 52, "70 (developed)"); vdim(ax, -8, 0, 44, "44")
    ax.annotate("Bend line, bend down ≈ 9.5°, R ≥ 3t", (10, 22), (25, 60), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.annotate("2× Ø3.4 (M3 to bottom plate)", (5, 12), (20, -15), fontsize=8, color=DIM, arrowprops=dict(arrowstyle="-", color=DIM, lw=.6))
    ax.text(0, -30, "Tip must sit 0.5–1.0 mm above the floor with wheels loaded. Sharpen leading edge to 30°.", fontsize=8)
    ax.set_xlim(-25, 110); ax.set_ylim(-40, 75)
    title_block(fig, "Front fork (wedgelet)", "UMK2-005", "Ti-6Al-4V (or hardened spring steel)", f"{FORK_T} mm", "1 (+2 spares)",
                "Laser cut flat, bend on brake.", "Fit-check height on a flat surface; shim with washers if needed.")
    save(fig, "UMK2-005_fork")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    s, _, _ = build.build_all()
    bar_drawing(s); plate_drawing(s, True); plate_drawing(s, False); frame_drawing(s); fork_drawing(s)
    print(sorted(os.listdir(OUT)))
