"""Single source of truth for Unskinny Mk II dimensions and component data (SI units unless noted)."""
# Geometry (mm). Origin = weapon axis, bar plane at z=0, +x = front.
BAR_L, BAR_W, BAR_T = 229.0, 38.0, 5.0
BAR_HOLE_PCD, BAR_BOLT_D, BAR_BORE = 30.0, 5.3, 8.0
PLATE_T = 1.2            # grade 5 titanium
PLATE_GAP = 40.0            # inner distance between plates
PLATE_FRONT_X, PLATE_REAR_X, PLATE_HALF_W = 30.0, -230.0, 82.0
TONGUE_HALF_W = 26.0      # narrow plate section that carries the hub motor
POD_FRONT_X = -128.0        # frame starts behind the bar sweep (r=114.5 + clearance)
HUB_D, HUB_H = 36.0, PLATE_GAP
WHEEL_D, WHEEL_W, WHEEL_X = 62.0, 18.0, -195.0
DRIVE_D, DRIVE_L = 24.0, 55.0
BATT = (36.0, 72.0, 26.0)   # 4S 650 mAh pack, mounted sideways (x, y, z)
BATT_X = -150.0
ESC_BAYS = [(-150.0, 60.0), (-150.0, -60.0)]  # 30 x 28 mm bays
FORK_T = 1.5

# Densities (g/cm^3)
RHO = {"steel": 7.85, "ti": 4.43, "tpu": 1.21, "al7075": 2.81}
FRAME_INFILL = 0.45         # effective density fraction of printed TPU

# Bought-in component masses (g) - manufacturer/typical values, verify on arrival
BOUGHT = {"hub_motor_2812": 175, "drive_motors_x2": 120, "wheels_hubs_x2": 70,
          "lipo_4s_650": 85, "weapon_esc": 35, "drive_esc": 15, "rx_switch": 15,
          "wiring": 40, "fasteners": 30}
WEIGHT_LIMIT_G = 1361

# Electrical / motor models (assumptions - verify against datasheets)
CELLS, V_CELL = 4, 3.7
WEAPON_KV, WEAPON_R_OHM, WEAPON_I_LIMIT = 900.0, 0.045, 80.0
HUB_BELL_INERTIA = 0.30e-4  # kg m^2, rotating bell of 2812 hub (estimate)
DRIVE_KV, DRIVE_GEAR, DRIVE_R_OHM, DRIVE_I_LIMIT = 2100.0, 27.0, 0.12, 30.0
BATT_WH = CELLS * V_CELL * 0.65

# Materials
AR500_YIELD_MPA = 1250.0
