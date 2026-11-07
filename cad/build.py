"""Parametric CAD for Unskinny Mk II (CadQuery). Exports STEP, STL and DXF into out/."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cadquery as cq
from params import *

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
ZP = PLATE_GAP / 2  # inner face of plates

def bar():
    tooth = 14.0
    pts = [(-BAR_L/2, -BAR_W/2 + tooth), (-BAR_L/2 + tooth, -BAR_W/2), (BAR_L/2, -BAR_W/2),
           (BAR_L/2, BAR_W/2 - tooth), (BAR_L/2 - tooth, BAR_W/2), (-BAR_L/2, BAR_W/2)]
    b = cq.Workplane("XY").polyline(pts).close().extrude(BAR_T).translate((0, 0, -BAR_T/2))
    b = b.faces(">Z").workplane().hole(BAR_BORE)
    b = b.faces(">Z").workplane().polarArray(BAR_HOLE_PCD/2, 45, 360, 4).hole(BAR_BOLT_D)
    # lightening pockets near hub keep mass at the tips (raises energy per gram)
    b = b.faces(">Z").workplane().pushPoints([(42, 0), (-42, 0)]).slot2D(28, 12).cutThruAll()
    return b

def plate_profile(wp):
    w = wp.center((PLATE_FRONT_X + PLATE_REAR_X)/2, 0).rect(PLATE_FRONT_X - PLATE_REAR_X, 2*PLATE_HALF_W)
    return w

def plate(top):
    z0 = ZP if top else -ZP - PLATE_T
    pod_x = POD_FRONT_X - 10
    pts = [(PLATE_REAR_X, -PLATE_HALF_W), (pod_x, -PLATE_HALF_W), (-40, -TONGUE_HALF_W - 6),
           (PLATE_FRONT_X, -TONGUE_HALF_W), (PLATE_FRONT_X, TONGUE_HALF_W), (-40, TONGUE_HALF_W + 6),
           (pod_x, PLATE_HALF_W), (PLATE_REAR_X, PLATE_HALF_W)]
    p = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(PLATE_T).edges("|Z").fillet(6)
    for s in (1, -1):
        p = p.cut(cq.Workplane("XY").box(WHEEL_D + 8, WHEEL_W + 6, 50)
                  .translate((WHEEL_X, s*(PLATE_HALF_W - (WHEEL_W + 6)/2 + 0.01), 0)))
    p = p.cut(cq.Workplane("XY").polarArray(12.5, 0, 360, 4).circle(2.1).extrude(60).translate((0, 0, -30)))
    p = p.cut(cq.Workplane("XY").circle(4.5).extrude(60).translate((0, 0, -30)))
    # lightening pockets over the battery/drive area
    p = p.cut(cq.Workplane("XY").pushPoints([(-175, 30), (-175, -30), (-215, 30), (-215, -30)])
              .rect(32, 22).extrude(60).translate((0, 0, -30)))
    holes = [(x, y) for x in (POD_FRONT_X - 6, PLATE_REAR_X + 8) for y in (-45, 0, 45)]
    p = p.cut(cq.Workplane("XY").pushPoints(holes).circle(1.7).extrude(60).translate((0, 0, -30)))
    return p

def frame():
    L = POD_FRONT_X - PLATE_REAR_X
    f = (cq.Workplane("XY").box(L, 2*PLATE_HALF_W - 2, PLATE_GAP)
         .translate(((POD_FRONT_X + PLATE_REAR_X)/2, 0, 0)).edges("|Z").fillet(10))
    # front face curved to follow the bar sweep (clearance 13 mm)
    f = f.cut(cq.Workplane("XY").circle(BAR_L/2 + 13.5).extrude(PLATE_GAP + 2).translate((0, 0, -PLATE_GAP/2 - 1)))
    # battery bay, ESC bay
    f = f.cut(cq.Workplane("XY").box(BATT[0] + 2, BATT[1] + 2, PLATE_GAP + 2).translate((BATT_X, 0, 0)))
    for ex, ey in ESC_BAYS:
        f = f.cut(cq.Workplane("XY").box(30, 28, PLATE_GAP + 2).translate((ex, ey, 0)))
    for s in (1, -1):
        f = f.cut(cq.Workplane("XY").box(WHEEL_D + 8, WHEEL_W + 6, PLATE_GAP + 2)
                  .translate((WHEEL_X, s*(PLATE_HALF_W - (WHEEL_W+6)/2), 0)))
        f = f.cut(cq.Workplane("XY").cylinder(DRIVE_L, DRIVE_D/2 + 0.3, direct=(0, 1, 0))
                  .translate((WHEEL_X, s*(PLATE_HALF_W - WHEEL_W - 6 - DRIVE_L/2), 0)))
    # motor-side boss: hub motor column is carried by plates only
    return f

def hub():
    return cq.Workplane("XY").circle(HUB_D/2).extrude(HUB_H - 0.5).translate((0, 0, -HUB_H/2 + 0.25))

def wheels():
    out = []
    for s in (1, -1):
        w = cq.Workplane("XY").cylinder(WHEEL_W, WHEEL_D/2, direct=(0, 1, 0)).translate((WHEEL_X, s*(PLATE_HALF_W - (WHEEL_W+6)/2), 0))
        out.append(w)
    return out

def drive_motors():
    return [cq.Workplane("XY").cylinder(DRIVE_L, DRIVE_D/2, direct=(0, 1, 0))
            .translate((WHEEL_X, s*(PLATE_HALF_W - WHEEL_W - 6 - DRIVE_L/2), 0)) for s in (1, -1)]

def battery():
    return cq.Workplane("XY").box(*BATT).translate((BATT_X, 0, 0))

def fork():
    """Titanium wedgelet bolted under the bottom plate's front edge, sloping forward to the floor."""
    floor = -WHEEL_D/2
    zt = -ZP - PLATE_T
    def one(y):
        return (cq.Workplane("XZ").polyline([(-10, zt), (PLATE_FRONT_X + 18, floor + 1.0 + FORK_T),
                (PLATE_FRONT_X + 18, floor + 1.0), (-10, zt - FORK_T)]).close()
                .extrude(-44).translate((0, y - 22, 0)))
    return [one(0)]

PARTS = {  # name: (builder, material or None for bought-in placeholder, color)
    "bar": (bar, "steel", (0.55, 0.6, 0.65)),
    "top_plate": (lambda: plate(True), "ti", (0.7, 0.72, 0.75)),
    "bottom_plate": (lambda: plate(False), "ti", (0.7, 0.72, 0.75)),
    "frame": (frame, "tpu", (0.9, 0.35, 0.1)),
}

def build_all():
    os.makedirs(OUT, exist_ok=True)
    solids, masses = {}, {}
    for name, (fn, mat, _) in PARTS.items():
        s = fn()
        solids[name] = s
        vol_cm3 = s.val().Volume() / 1000
        rho = RHO[mat] * (FRAME_INFILL if mat == "tpu" else 1)
        masses[name] = round(vol_cm3 * rho, 1)
    solids["fork"] = fork()[0]
    masses["fork"] = round(abs(solids["fork"].val().Volume()) / 1000 * RHO["ti"], 1)
    solids["hub_motor"] = hub(); solids["battery"] = battery()
    for i, w in enumerate(wheels()): solids[f"wheel_{i}"] = w
    for i, m in enumerate(drive_motors()): solids[f"drive_{i}"] = m

    for n, s in solids.items():
        cq.exporters.export(s, os.path.join(OUT, f"{n}.stl"), tolerance=0.1, angularTolerance=0.2)
    for n in ("bar", "top_plate", "bottom_plate"):
        cq.exporters.export(solids[n], os.path.join(OUT, f"{n}.step"))
        sec = solids[n].section()
        cq.exporters.export(sec, os.path.join(OUT, f"{n}.dxf"))
    cq.exporters.export(solids["frame"], os.path.join(OUT, "frame.step"))

    asm = cq.Assembly(name="unskinny_mk2")
    colors = {"bar": (0.55, 0.6, 0.65), "top_plate": (0.7, 0.72, 0.75), "bottom_plate": (0.7, 0.72, 0.75),
              "frame": (0.9, 0.35, 0.1)}
    for n, s in solids.items():
        asm.add(s, name=n, color=cq.Color(*colors.get(n, (0.2, 0.2, 0.22))))
    asm.export(os.path.join(OUT, "unskinny_mk2_assembly.step"))

    # bar inertia about z for the sims
    bar_solid = solids["bar"].val()
    I_cm = cq.Shape.matrixOfInertia(bar_solid)  # mm^5 for unit density
    Izz = I_cm[2][2] * RHO["steel"] * 1e3 * 1e-15  # kg m^2
    json.dump({"masses_g": masses, "bar_Izz_kgm2": Izz}, open(os.path.join(OUT, "cad_report.json"), "w"), indent=2)
    return solids, masses, Izz

if __name__ == "__main__":
    _, m, I = build_all()
    print(json.dumps(m, indent=2)); print("bar Izz kg m^2:", I)
