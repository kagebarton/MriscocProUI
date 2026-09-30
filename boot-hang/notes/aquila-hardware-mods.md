---
name: aquila-hardware-mods
description: "Hardware mods on the user's Voxelab Aquila (probe, extruder, hotend, Z, TMC UART pin mapping) and the open PC9/SDIO pin conflict"
metadata:
  node_type: memory
  type: project
  originSessionId: ca5c4853-f283-4271-b91b-49c353e17ab3
  modified: 2026-09-30T19:52:18.720Z
---

Voxelab Aquila, GD32F103RET6 board (BOARD_VOXELAB_AQUILA → pins_CREALITY_V4.h), ProUI with PROUI_EX. Mods as of 2026-09-23:

- Sherpa-style direct drive extruder (E steps 702).
- Kevinakasam belted Z mod (Z steps still 400 in config; whether it's self-locking was asked but not yet answered).
- Kevinakasam Frankenduct 1.0 with a hardened Volcano nozzle and a cartridge thermistor (TEMP_SENSOR_0 11). MPC is used, not PID.
- Heater and thermistor parts come from Taobao shop 同拓展志; the listings are saved as ~/Downloads/heater.pdf and thermistor.pdf. Heater: 6x20 mm cartridge, 50 W nominal, NiCr 2080 wire (not PTC); sold in 12 V and 24 V variants, and which one the user has is unconfirmed (24 V/50 W should measure about 11.5 Ω). Thermistor: MF58D glass NTC, 100k 1%, B25/50 = 3950, in a 3x20 mm stainless tube; its lead wire is rated 150 °C and the heat-shrink 125 °C. Table 11 matches it within 1 K.
- Kevinakasam Klackender probe: MAG_MOUNTED_PROBE on the Z-min pin, dock near X=247 Y=114, 235 mm bed.
- TMC2208 UART mod: a spare MCU pin is soldered to each driver's PDN_UART. X=PC6, Y=PC9, Z=PA13, E=PA15, TMC_BAUD_RATE 19200.

**Open issue (flagged 2026-09-23):** PC9 is also SDIO_D1. HAL/STM32 runs the onboard SD in 4-bit mode because SDIO_D1..D3 are defined in pins_CREALITY_V4.h. SoftwareSerial for the Y driver and the SDIO init each reconfigure PC9.
- The firmware-only fix is to drop D1–D3 so SDIO stays 1-bit. HAL/STM32/sdio.h also has to stop redefining them; see `pc9fix.py` in `~/Downloads/aquila-bisect-tools/`.
- Also see [[printer-serial-stepper-isr-patch]].

**2026-09-30:** the PC9 fix is committed on `KT-Nov-2025-MPC` (18c013bd76) and flashed. It is not on any other branch yet. Belted Z holds position unpowered but needs a rehome.

**2026-09-24:** on upstream 2025-December, enabling UART on only Y (PC9) or only Z (PA13) makes the printer hang at the Voxelab logo; X and E alone are fine. Details in [[kt-sep-2026-display-dead]].

**Why:** the user often forgets to mention hardware mods up front, and the mods change which config values are right.
**How to apply:** check new pin, current or probe advice against this list. Confirm whether the PC9 conflict was fixed before assuming SD printing works.
