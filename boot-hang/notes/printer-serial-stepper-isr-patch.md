---
name: printer-serial-stepper-isr-patch
description: "User's Aquila/OctoPrint serial setup and why their fork must carry a stepper-ISR interrupt patch on every upstream rebase"
metadata:
  node_type: memory
  type: project
  originSessionId: 64483e31-a1bf-4f85-b8e0-51446e6ae127
  modified: 2026-09-24T14:37:15.055Z
---

Printer: Voxelab Aquila, GD32F103RET6 board, built with env `STM32F103RE_creality` (HAL/STM32). Host: OctoPrint via octo4a on Android, through a CH9340C USB-C UART soldered to the onboard CH340G's TX/RX, at BAUDRATE 500000 (1M had trouble on big dumps). On 2026-09-23 500000 was also shown to lose 0.5–1% of the bytes the printer sends, while 250000 lost none; see [[octoprint-remote-access]].

The user's working branch is `origin/KT-Sep-2025` = upstream classicrocker883/MriscocProUI `2025-September` (44a4ec101f) + 11 personal commits. The local checkout `Mriscoc-2023` is an old, unrelated line. Upstream publishes monthly branches (`2026-September` was newest on 2026-09-23).

Upstream Marlin #27131 (5d591fd91d, Dec 2024) keeps interrupts masked through step-pulse generation. On STM32 `hal.isr_off()` is `cpsid i`, so the USART RX IRQ can't run, the 1-byte RX register overruns at 500k, and OctoPrint sees high resend rates. The user's commit e0ab61e6d9 reverts it. On 2026-09-23 the fix was ported as a single `hal.isr_on();` at the top of the `do {` loop in `Stepper::isr()`.

On 2026-09-23 the local branch `KT-Sep-2026` (not pushed) was rebased onto upstream `2026-September` (c485acf68f). A remote named `upstream` was added. The branch carries one extra commit fixing a fork bug: upstream d65034a176 made `get_serial_commands()` quickstop on `M401` instead of `M410`, and M401 deploys the user's Klackender. Drop that commit if upstream fixes it.

**Two forms of the fix exist:**
- The Sep-2025 revert e0ab61e6d9 moves `isr_off` into `Stepper::isr()`, adds `isr_on` at the top of the loop, and drops the later `isr_on`.
- The KT-Sep-2026 one-liner 788f616313 only adds the `isr_on`.

On 2026-09-24 the full revert turned out to matter for **booting** with the TMC UART mod on upstream 2025-November: stock+UART hung without it and booted with it. It didn't rescue 2025-December. See [[kt-sep-2026-display-dead]]. `port_revert.py` in `~/Downloads/aquila-bisect-tools/` applies the full form to Dec-era stepper.cpp.

**Why:** upstream still had the #27131 structure as of 2026-September. Standard MarlinFirmware bugfix-2.1.x still has it at 124ad16e2f (2026-09-28): `hal.isr_off()` is in `HAL_STEP_TIMER_ISR()`. A standard-Marlin build therefore needs the same one-liner before printing at 500k. Every rebase has to re-apply the patch.
**How to apply:** when helping rebase or update this fork, carry the one-line ISR patch forward and check whether upstream changed that loop. Don't suggest `SERIAL_DMA` as a drop-in. On F0/F1 it clears the wrong bit in `Serial_DMA_Read_Enable()`, so any re-`begin()` (M575, or ProUI settings load with the 250K box ticked) hangs until the watchdog fires. It also stops the emergency parser from working during blocking waits.
