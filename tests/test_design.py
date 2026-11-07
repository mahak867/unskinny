"""Design verification tests: geometry interference, weight, and physics limits."""
import os, sys, math, itertools
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "cad"), os.path.join(ROOT, "sim")]
import cadquery as cq
import build, models
from params import *

@pytest.fixture(scope="session")
def solids():
    s, _, _ = build.build_all()
    return s

def vol(a, b):
    try:
        return abs(a.intersect(b).val().Volume())
    except Exception:
        return 0.0

def test_no_part_interference(solids):
    """No two physical parts may overlap by more than 1 mm^3 (tessellation noise)."""
    names = ["bar", "top_plate", "bottom_plate", "frame", "fork", "hub_motor", "battery",
             "wheel_0", "wheel_1", "drive_0", "drive_1"]
    allowed = {frozenset(("bar", "hub_motor"))}  # bar bolts onto the hub bell
    clashes = [(a, b, round(vol(solids[a], solids[b]), 1)) for a, b in itertools.combinations(names, 2)
               if frozenset((a, b)) not in allowed and vol(solids[a], solids[b]) > 1.0]
    assert not clashes, clashes

def test_bar_sweep_clears_everything(solids):
    """The full 360 deg sweep of the bar, grown by 3 mm, must not touch any non-rotating part."""
    sweep = cq.Workplane("XY").circle(BAR_L / 2 + 3).circle(HUB_D / 2 + 0.5).extrude(BAR_T + 6).translate((0, 0, -BAR_T / 2 - 3))
    for n in ("frame", "top_plate", "bottom_plate", "fork", "battery", "wheel_0", "wheel_1", "drive_0", "drive_1"):
        assert vol(sweep, solids[n]) < 1.0, n

def test_wheels_touch_floor_both_ways_up():
    """Wheels must stick out past both plates so the bot drives when flipped."""
    outer = PLATE_GAP / 2 + PLATE_T
    assert WHEEL_D / 2 - outer >= 2.0

def test_fork_reaches_floor(solids):
    bb = solids["fork"].val().BoundingBox()
    assert -WHEEL_D / 2 < bb.zmin < -WHEEL_D / 2 + 3

def test_weight_under_limit():
    assert models.total_mass_g() <= WEIGHT_LIMIT_G - 15, "keep >= 15 g margin for wiring/paint"

def test_bar_is_balanced(solids):
    c = solids["bar"].val().Center()
    assert math.hypot(c.x, c.y) < 0.05  # mm

def test_weapon_energy_and_spinup():
    s = models.summary()
    assert s["weapon_energy_J"] > 500
    assert s["spinup_90pct_s"] < 3.0

def test_bar_survives_centrifugal_load():
    assert models.summary()["bar_safety_factor"] >= 3.0

def test_drive_is_competitive():
    s = models.summary()
    assert s["drive_top_speed_mps"] >= 2.0 and s["drive_traction_limited"]

def test_battery_lasts_a_match():
    s = models.summary()
    assert s["match_energy_wh"] < s["battery_usable_wh"]

def test_spinup_converges_to_no_load_speed():
    I = models.weapon_inertia()
    t, w, _ = models.spinup(I, drag=0.0, t_end=20)
    ideal = WEAPON_KV * 2 * math.pi / 60 * models.v_batt()
    assert abs(w[-1] - ideal) / ideal < 0.01

def test_energy_formula():
    assert models.kinetic_energy(2.0, 3.0) == pytest.approx(9.0)
