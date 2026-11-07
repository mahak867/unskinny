# Unskinny Mk II: 3 lb horizontal bar spinner

**Interactive demo:** [`unskinny-mk2.html`](unskinny-mk2.html). Download it and open it in any browser; it works offline. It has a 3D model, stress map, design lab and fight simulator.

A ground-up redesign of the 2013 "Unskinny Bot" beetleweight (3 lb / 1361 g) combat robot, using the layout that current competitive horizontal spinners use: a direct-drive brushless hub-motor weapon, brushless geared drive and 4S power.

Everything is **parametric and verified by code**. One parameter file drives the CAD, the physics simulations and an automated test suite.

![iso render](out/render_iso.png)

## Results (from `out/sim_summary.json`)

| Metric | Value |
|---|---|
| Total mass (CAD + bought parts) | 1328 g (33 g under limit) |
| Weapon | 229 × 38 × 5 mm AR500 bar, 304 g |
| Weapon speed / energy | ~11,000 rpm, ~940 J, 2.0 s to 90% speed |
| Tip speed | ~132 m/s |
| Bar safety factor (centrifugal, with hole Kt=3) | 6.1 |
| Bite at 3 m/s closing | 8.2 mm |
| Drive top speed / accel | 2.7 m/s, 8.8 m/s² (traction-limited) |
| 3-minute match energy | 7.4 Wh of 7.7 Wh usable |

![simulations](out/sim_results.png)

## What's in the repo

```
params.py          single source of truth: dimensions, materials, motor data
cad/build.py       CadQuery model -> STEP (assembly + parts), STL, DXF
sim/models.py      weapon spin-up ODE, energy, stress, bite, drive, gyro, battery models
sim/plots.py       plots, 3D renders, spinning demo GIF
showcase/          interactive page: 3D viewer, stress map, design lab, fight simulator
tools/             build_standalone.py bundles the page into one offline HTML file
docs/              copy of the standalone page, ready for GitHub Pages
tests/             12 pytest checks: part interference, bar-sweep clearance,
                   weight limit, balance, stress, spin-up, battery
out/               generated files (cut-ready DXFs, printable STLs, STEP)
```

## Run it

```bash
pip install -r requirements.txt
make          # builds CAD, runs simulations, runs tests
```

## Manufacturing outputs

| File | Process |
|---|---|
| `out/bar.dxf` | Waterjet/laser, 5 mm AR500, then bevel the teeth |
| `out/top_plate.dxf`, `out/bottom_plate.dxf` | Laser/waterjet, 1.2 mm grade 5 titanium |
| `out/frame.stl` | 3D print in TPU 95A, ~45% gyroid |
| `out/fork.stl` / `.step` | Bend from 1.5 mm titanium |
| `out/unskinny_mk2_assembly.step` | Full assembly for any CAD tool |

## Engineering findings

- **The first concept was 444 g overweight.** A full 50 × 9.5 mm bar weighs 773 g and full-width titanium plates weigh ~400 g each. The CAD mass check caught this. The fix was a thinner bar with lightening slots near the hub (most energy is stored at the tips), a tapered "tongue" plate and pocketed plates.
- **Gyroscopic effect is large.** Turning at 6 rad/s with the weapon at full speed creates ~11× more pitch torque than gravity resists, so the bot will lift a wheel during fast turns. This is normal for horizontal spinners; the mitigation is to turn gently at full spin and keep the wheelbase wide.
- **The battery is tight.** The model predicts 7.4 Wh used per match against 7.7 Wh usable. An 850 mAh pack (+~25 g) fits inside the weight margin if testing shows the pack running low.

## Assumptions to verify

Motor kV (900), winding resistance, bell inertia, drive motor masses and aero drag are estimates. Update `params.py` once parts arrive and run `make`; the tests will flag anything that no longer fits.

## Credits

Based on [Unskinny Bot](https://www.instructables.com/Unskinny-Bot-3-lb-Horizontal-Spinner-Combat-Bot/) by lewisb42.
