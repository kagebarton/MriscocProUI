# MPC tuning tools (Aquila, Volcano hotend)

These are the scripts, test logs and model fits used on 2026-09-30 to tune this fork's two MPC extensions:

- `MPC_DEADTIME`: `M306 D`, the heater dead time.
- `MPC_SIDE_MASS`: `M306 M` and `K`, a slow mass that soaks up heat from the block.

Everything talks to the printer through OctoPrint, using G-code only.

## Result

Saved to EEPROM and set as the `Configuration.h` defaults:

```
M306 E0 P53.00 C16.00 D5.50 M2.00 K0.0500 R0.2673 A0.0654 F0.1018 H0.0035
```

**The goal** was the fastest M109 release with overshoot capped at 2 K. `TEMP_RESIDENCY_TIME` is 3 s. Swinging within the ±3 K hysteresis doesn't matter unless it delays the release.

Every number below is reproducible from the logs with the scorers. Cold-start times are measured from when the nozzle passes 200 °C. Unless marked real, each "release" is the M109 release predicted for 3 s residency, even for the older logs recorded with 10 s. See *Accuracy* below.

| Test | Firmware and setting | Release | Overshoot | Log |
|---|---|---|---|---|
| Cold start to 240 | D only, C16.95 D4.5 | 23 s, with a −3.1 K dip on the edge of the hysteresis | +0.5 K | `cold1.log` |
| Cold start to 240 | D only, D6 | 46 s | +0.6 K | `cold_D6.log` |
| Cold start to 240 | side mass, C16 D6 M2 K0.1 | 25 s | +0.2 K | `side_cold1.log` |
| Cold start to 240 | side mass, D5 K0.1 | 20 s | +2.0 K | `side_D5.log` |
| 220 → 240 step | D5 K0.1 | 20.6 s (real) | +2.2 K | `side_D5.log` |
| 220 → 240 step | D4.5 K0.1 | 20.3 s (real) | +2.4 K | `side_D5.log` |
| PLA start, 210 | D5.5 K0.1 | 21.5 s at the wiper | +0.8 K | `real_start.log` |
| PETG start, 240 | D5.5 K0.1 | 26.1 s at the wiper, 56.7 s from M104 | +2.0 K | `real_start.log` |
| **PETG start, 240** | **D5.5 K0.05 (final)** | 27.0 s at the wiper, **56.8 s from M104** | **+1.5 K** | `real_petg_k05.log` |

Not measured on the printer:

- A cold start at the final D5.5 K0.05. `sweep.py` predicts about 24 s.
- The PLA start at K0.05. PLA had 1.2 K of headroom at K0.1.

Down-steps (240 → 220) take 30–31 s at any setting, because they're limited by cooling.

## Requirements

- **Python 3.11** with numpy, scipy, numba, requests and websockets. The `pik` conda env has them.
- **OctoPrint:**
  - `OCTOPRINT_URL` defaults to `http://192.168.1.3:5000`.
  - The API key is read from `OCTOPRINT_KEY_FILE` (default `~/Downloads/octo.txt`). It never appears on a command line or in a log.
- **Firmware** with `MPC_DEADTIME` and `MPC_SIDE_MASS`: branch `KT-Nov-2025-MPC-side`.

Scripts find logs in `logs/`, fits in `fits/` and sequences in `seqs/` by bare name. They can be run from any directory.

## Before a printer test

- **Only run tests when the printer is idle.** OctoPrint accepts these commands in the middle of a print.
- **The idle timeout.** Every sequence sends `M86 S0` first. Otherwise the hotend idle timeout cuts the heater 360 s after the nozzle passes 180 °C. The sequences restore your setting at the end with `M86 S360 T180 E0 B0`. If a run is cut short, send that yourself.
- **Head movement.** The `start_*.seq` sequences home the printer (G28) and park the nozzle at the wiper at X177 Y245 Z3.
- **Trying values.** Try candidates with `M306 E0 D<s> K<w/k>`, which stays in RAM until `M500`. Put the line after `M306;2` in a copy of the sequence.
- **Flashing a new build** resets EEPROM (`EEPROM_INIT_NOW`). If a build changes `MPC_t`, the UBL mesh storage moves too, so restore the mesh afterwards.

## Workflow

1. **Record** a test. Cold starts must start from room temperature; `octo_waitcold.sh` waits for that.
   ```
   python octo_seq.py logs/my_cold.log @cold_start.seq
   ./octo_waitcold.sh 35 logs/my_cold.log @cold_start.seq
   python octo_seq.py logs/my_petg.log @start_petg.seq
   ```
   A step is `"cmd;wait"`. `wait` is a number of seconds, or `ok` to wait for the command to finish, as with M109, M190 or G28. Steps can also go straight on the command line.

2. **Score** it:
   - `score_cold.py` scores cold starts.
   - `score_steps.py` compares real and predicted M109 releases.
   - `score_start.py` scores start sequences.

3. **Refit the plant** if the hotend has changed (nozzle, sock, heater or thermistor):
   - `fit_plant.py` fits the physical model to `cold1.log` and `steps1.log`. For new hardware, record a cold start with holds and a steps run, then change the file list and fit windows at the top of the script.
   - `validate.py fits/p6_L3.0.npy` checks the fit in closed loop.

4. **Rank settings** in the simulator:
   - `sweep.py` runs the joint grid over C, M, K, D and R.
   - `sweep.py 16 2 0.05 5.5` scores one setting.
   - The grid caps simulated overshoot at 1.5 K cold and 1.0 K per step, leaving room for the simulator's optimism.

5. **Check the best two or three settings on the printer** with the sequences. Then `M500` the winner and update the defaults in `Configuration.h`.

## M306 T with these extensions

M306 T's fit has no dead time or side mass, so it folds both into C and R. The fitted plants give C ≈ 17.5 and R ≈ 0.125 this way, and your real run once gave C20.1 R0.1225.

With D or M set, M306 T behaves differently:

- It keeps C, R, D, M and K, and measures only A and F.
- It runs the model through the heat-up, then holds with the tuned model.
- It extends the first settle by three side-mass time constants: 120 s at M2 K0.05.
- At the end it prints the lumped C and R, as a hint that the hotend has changed.

`simtune.py` replays both flows on the fitted plants. With the stock 20 s settle, the side mass is still soaking up heat and A reads 22% high. The extended settle brings it within 1%. The change was simulated but hasn't been run on the printer yet.

To run the stock full tune, send `M306 E0 D0 M0` first. That gives the lumped values. Going back to D and M afterwards needs C and R refitted with these tools.

## Accuracy

- **Release timing.** Releases are predicted from the logged temperatures, which arrive at about 3 per second. The printer released 0.5–1 s *earlier* than predicted, because one noisy 0.16 s sample can start the residency timer early. "Real" releases come from OctoPrint's ok, which arrives in batches about 0.5 s apart.
- **Overshoot.** The simulator reads overshoot 0.6–1.3 K low. Use it to rank settings, not to certify them.
- **Plant fit.** `validate.py` replays the D-only logs with 0.45 K and 0.54 K rms error.
- **What the fits can and can't pin down:**
  - **The physical plant** (`fit_plant.py`) has about 3 s of pure delay, a 10–11 s sensor lag, and a side mass of 7–8 J/K with an 18 s time constant. L3.0 fits best (weighted rms 1.16) and L2.0 next (1.26); `sweep.py` takes the worse of the two for each setting.
  - **The firmware's model structure** (`fit_ctlmodel.py`) gives C ≈ 16, M ≈ 1.5, K ≈ 0.03 and R 0.22–0.37 once D is 4.5–7 s. That is close to the tuned values.
  - **D can't be fitted.** The weighted rms only ranges from 4.08 to 4.25 across D 3.5–7 s. At D ≤ 4 the fit jumps to a solution with a 7–13 J/K side mass. D is what trades speed against overshoot, so pick it with closed-loop tests.

## Files

| File | What it does |
|---|---|
| `common.py` | Paths, constants (P 53 W, `MPC_dT` 0.16 s), log parsing, and the M109 release rule |
| `octo_seq.py` | Runs a sequence and logs every terminal line, polling M105 about 3 times a second |
| `octo_log.py` | Logs the terminal for N seconds, optionally polling M105 |
| `octo_send.sh` | Queues commands. 204 means queued |
| `octo_waitcold.sh` | Waits until the nozzle is below a threshold, then runs `octo_seq.py` |
| `seqs/*.seq` | `cold_start`, `steps`, `start_pla` and `start_petg`, each copied from a logged run |
| `score_cold.py`, `score_steps.py`, `score_start.py` | The scorers listed in Workflow step 2 |
| `plant.py` | The physical plant model ("p6"), as used by the fitting and closed-loop tools |
| `fit_plant.py` | Fits `plant.py` for pure delays of 0–5 s and writes `fits/p6_L*.npy` |
| `fit_ctlmodel.py` | Fits the firmware's own model structure for D 1–7 s and writes `fits/side_D*.npy` |
| `closedloop.py` | An exact port of `get_pid_output_hotend()` (MPC with dead time and side mass), driving the plant |
| `validate.py` | Replays the D-only logs through `closedloop.py` |
| `sweep.py` | Ranks settings in closed loop on the L2 and L3 plant fits |
| `simtune.py` | Replays M306 T on the plants |

### Logs

Each line is a Unix time, a tab, then either an OctoPrint terminal line (`Send:` or `Recv:`) or a mark (`#STEP cmd`, `#DONE cmd`, `#END`). Temperatures come from the `T:... @:pwm` reports.

| Log | Firmware | Content |
|---|---|---|
| `cold1.log` | D only, C16.95 D4.5, 10 s residency | Cold start to 240, then holds at 220 and 240 |
| `steps1.log` | D only | 220 ↔ 240 steps at D4.5, D3 and D6 |
| `cold_D6.log` | D only | Cold start at D6 |
| `side_cold1.log` | Side mass, C16 D6 M2 K0.1, 3 s residency | Cold start, then holds |
| `side_D5.log` | Side mass | Cold start at D5, then M109 steps at D5 and D4.5 |
| `real_start.log` | Side mass, D5.5 K0.1 | The PLA start sequence, then the PETG one |
| `real_petg_k05.log` | Side mass, D5.5 K0.05 | The PETG start sequence (the final setting) |
