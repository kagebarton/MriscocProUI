# KT-Sep-2026 boot hang: where to resume

Newer MriscocProUI builds stick at the Voxelab logo on the Aquila. This folder
holds everything needed to pick the investigation up again. It was copied on
2026-09-30 from `~/Downloads/aquila-bisect-tools/` (minus `elf/`) and from
Claude's memory notes.

- `README.txt`: full history, build recipes, and how to read a boot trace.
  Start at the section "2026-09-29 (late): Feb A/B HANG".
- `notes/kt-sep-2026-display-dead.md`: results table and "Where to resume".
- `notes/`: the other notes it links to (OctoPrint access, hardware mods,
  ProUI serial layout, ISR patch, repos).
- `boottrace/`: the RAM-neutral boot tracer, its SysTick hook, the OctoPrint
  terminal reader, and the diffs for each tracer-round image.
- Other `*.patch` / `*.diff`: the full tree diffs for every bisect image.

## Findings so far

- Fixed along the way: RAM headroom (smaller serial and planner buffers),
  REINIT_NOISY_LCD off (the Jan 2026 break), and the PC9/SDIO fix for Y's UART.
- Jan 2026 with UART on E only boots. The same tree with UART on all four axes
  hangs, and so do Feb images A and B.
- Jan (boots) and Feb-A (hangs) compile to identical code. The only change is a
  4-byte shift in .bss from 0x20005210 on, caused by upstream 488bd82db0
  (`stepper.ne` renamed to `nle`). So this is a latent, RAM-layout-sensitive
  bug, and further commit bisecting is unreliable.
- With A flashed, the printer sends nothing on serial at any baud: setup()
  never reaches loop(), or it faulted.

## Next step: the tracer round (built, not yet flashed)

Images in `~/Downloads`, flash in this order:

1. `aquila-2026-Feb-A-trace.bin`: A plus the boot tracer. If it hangs, leave it
   powered for 10 s or more, then run
   `python3 boot-hang/boottrace/octo_connect.py 500000 30` and read the `BT` or
   `FAULT` lines. Symbolize with
   `arm-none-eabi-addr2line -f -C -i -e ~/Downloads/aquila-bisect-tools/elf/aquila-2026-Feb-A-trace.elf 0x0800xxxx`
   (subtract 1 from Thumb return addresses).
2. `aquila-2026-Feb-A-ne-JanRAMlayout.bin`: A with the rename undone. The
   layout theory predicts it boots.
3. `aquila-2026-January-nle-ARAMlayout.bin`: Jan with the rename applied. The
   layout theory predicts it hangs.

Also worth trying: boot a hanging image with the SD card removed, since
`SdVolume::cacheBuffer_` is in the shifted region.

If the trace gives a PC, add the tracer to the Jan all-UART build next (the
target config). Then fix the bug on KT-Sep-2026 with all four UART axes,
restore settings from `~/Downloads/printer-backup-2026-09-23/`, and run the MPC
tests.

## Things that are not in this folder

- The ELFs (150 MB) stay in `~/Downloads/aquila-bisect-tools/elf/`. They are
  needed to symbolize a trace from the matching image. A rebuild from the diffs
  gives the same code addresses; only dates differ.
- The `.bin` images are in `~/Downloads`. As of 2026-09-30,
  `aquila-2026-January-noREINIT-allUART-PC9fix.bin` and
  `aquila-KT-Sep-2025-MPC-lowRAM.bin` are no longer there; rebuild them from
  `2026-January-noREINIT-allUART-vs-Eonly.diff` and branch `KT-Sep-2025-MPC`.
- The printer currently runs the KT-Nov-2025-MPC-side build from the MPC tuning
  work (branch `KT-Nov-2025-MPC-side`), which boots with UART on all four axes.

## Rebuilding

Env `STM32F103RE_creality`, image limit 233,472 B. Build outside the project
so VS Code's PlatformIO extension doesn't wipe `.pio` mid-build:

    PLATFORMIO_BUILD_DIR=/tmp/pb_X PLATFORMIO_LIBDEPS_DIR=/tmp/pl_X \
      ~/.platformio/penv/bin/pio run -e STM32F103RE_creality

`fnhash.py` compares two ELFs function by function, to confirm two images
differ only in RAM layout.
