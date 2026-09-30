Aquila KT-Sep-2026 "stuck at Voxelab logo" bisect tools (2026-09-24). Copies of scratchpad files so they survive a reboot.
Full context: Claude memory "kt-sep-2026-display-dead".

fork-code.patch        Non-config fork changes, 44a4ec101f..origin/KT-Sep-2025 (stepper revert, queue ok, pins UART section, ld, platformio.ini, dwin.cpp, SanityCheck). For branches <= 2025-November.
fork-code-dwin.patch   Same, with the dwin.cpp path moved to lcd/dwin/proui/ (2025-December and later).
stepper-revert.patch   The Sep-2025 stepper ISR revert (e0ab61e6d9), applies to 2025-November.
port_revert.py FILE    The same revert, applied by text edits to a 2025-December stepper.cpp.
pc9fix.py ROOT         1-bit SDIO: skip SDIO_D1..D3 when TMC_UART_PIN_Y is defined, and make HAL/STM32/sdio.h respect the pins file.
one_axis.py SRC DST AX Stock config SRC -> DST with only axis AX (X|Y|Z|E) on TMC2208 UART.
defs.py                Diff the active #defines of two configs.
fnhash.py A.elf B.elf  List functions whose normalized code differs between two builds.
pages.py               Map display-related functions to 2K flash pages.
*-full.patch           Full diffs of the Nov user build, Dec user build, Dec user+ISR revert (D), Dec stock+UART+PC9 fix.
configs/               The user's config 3-way merged onto the upstream 2025-November and 2025-December configs.

2026 month bisect (E-only UART, low RAM, MPC), 2026-09-29:
  git worktree add --detach <wt> upstream/2026-<Month>
  cd <wt>; git apply --3way fork-KT-Sep-2026.patch      # = git diff upstream/2026-September KT-Sep-2026 (user's 14 commits)
    conflicts so far: .gitignore (take the patch side), MESH_INSET (take the patch side, 25); then git add both
  git apply --3way mpc-deadtime-KT-Sep-2026-wt.patch     # MPC dead time + HAS_CGCODE off
  Configuration_adv.h: TX 128->64, RX 2048->128, BLOCK_BUFFER_SIZE 256->64 (3x)
  Configuration.h: comment out TMC_UART_PIN_X/Y/Z, X/Y/Z_DRIVER_TYPE TMC2208_STANDALONE
  Full diffs: 2026-<Month>-MPC-lowRAM-UART-E-only-full.patch

Old recipe carried forward (2026-09-29): dec-2025-oldrecipe-E-only.git.patch is the exact source delta of the
Dec image that booted (aquila-dec-2025-MPC-lowRAM-UART-E-only.bin) as a git diff vs upstream/2025-December.
  git worktree add --detach <wt> upstream/2026-<Month>; cd <wt>; git apply --3way dec-2025-oldrecipe-E-only.git.patch
  Feb+: queue.cpp conflicts (upstream now calls motion.quickstop_stepper()); resolve to "case 410: motion.quickstop_stepper();"
  Feb+: upstream config has HAS_CGCODE on; comment it out by hand (the Dec delta has no hunk for it).

REINIT_NOISY_LCD (2026-09-29): prime suspect for the post-Dec hang.
  Upstream 2048e8b173 (Jan 2026, "Permit disable REINIT_NOISY_LCD") moved it from an auto-define that excluded
  DWIN/ProUI into Configuration_adv.h, on by default. The 3-way config merge carried it into every Jan+ build.
  Effect: MarlinUI::media_changed() calls init_lcd() (ProUI: delay 750 ms + DWIN_Handshake) on SD detect.
  Every image that booted lacks it; every hanging Jan+ image (Jan, Feb, Mar, Jun, KT-Sep-2026 A/B/C) has it.
  Fix: comment out "  #define REINIT_NOISY_LCD" in Configuration_adv.h (that is the only change in the images below).
  Verify: no REINIT_NOISY_LCD in objdump --dwarf=macro; only MarlinUI::init calls _ZN8MarlinUI8init_lcdEv.
  aquila-2026-January-oldrecipe-E-only-noREINIT.bin          = hung Jan old-recipe image minus REINIT
  aquila-KT-Sep-2026-MPC-lowRAM-C-E-only-noREINIT.bin        = latest C minus REINIT
  aquila-KT-Sep-2026-MPC-lowRAM-EY-PC9fix-noREINIT.bin       = latest B with X/Z standalone, minus REINIT
  aquila-KT-Sep-2026-MPC-lowRAM-B-allUART-PC9fix-noREINIT.bin = latest B minus REINIT

Jan-noREINIT BOOTS, latest C-noREINIT (E-only) HANGS (user, 2026-09-29). So REINIT_NOISY_LCD was the Dec->Jan break,
and a second break sits between Jan and Sep 2026. Old and new recipes have identical code hunks (PC9 fix inactive with
Y UART off) and near-identical active config, so new-recipe month images test code month only.
Round (new recipe as in "2026 month bisect" + REINIT_NOISY_LCD commented out), E-only, low RAM, MPC:
  aquila-2026-March-E-only-noREINIT.bin   (wt_March copy + REINIT off)
  aquila-2026-April-E-only-noREINIT.bin   (2026-April-MPC-lowRAM-E-only-noREINIT-full.patch)
  aquila-2026-June-E-only-noREINIT.bin    (wt_June copy + REINIT off)
  aquila-2026-August-E-only-noREINIT.bin  (2026-August-MPC-lowRAM-E-only-noREINIT-full.patch)
  Apr/Aug conflicts: same as Mar/Jun (.gitignore, MESH_INSET -> patch side 25).

March-noREINIT HANGS (user, 2026-09-29): second break is Jan..March. No config default flipped (macro diff Jan vs Mar
shows only code refactors). libproui.a unchanged in this range. Split points, old recipe + REINIT off (+ HAS_CGCODE off,
queue.cpp "case 410: motion.quickstop_stepper();" from B on):
  A aquila-2026-Feb-A-first-merge-noREINIT.bin     ed35a82c34 (2026-02-06 Merge w/Marlin + c892617ff4 configs)
  B aquila-2026-Feb-B-motion-refactor-noREINIT.bin 9db148c90e (2026-02-12 Merge: Motion encapsulation #27866, Run motion logic before UI 544f9e6104)
  C aquila-2026-Feb-C-merge-0222-noREINIT.bin      86da338293 (+96328288d2 optimization, 3cc4c063ae, 86da338293 merges)
  D aquila-2026-Feb-D-head-noREINIT.bin            06c644d1af = upstream/2026-February head (+82dd40dcb9 new mesh set, merge 03-09)
  After D, up to March: dec709fc08 merge, 113b180631, bac98c2918, 90a4a00fc8 merge.
  Patches: 2026-Feb-F{A,B,C}-<sha>-oldrecipe-noREINIT-full.patch; D = 2026-February-oldrecipe patch + REINIT off.

== 2026-09-29: January noREINIT with UART on all four axes ==
aquila-2026-January-noREINIT-allUART-PC9fix.bin (220,968 B, RAM 36.0%): the booting
aquila-2026-January-oldrecipe-E-only-noREINIT.bin tree ($S/wt_JanNR) with TMC_UART_PIN_X/Y/Z
re-enabled and X/Y/Z back to TMC2208 (diff: 2026-January-noREINIT-allUART-vs-Eonly.diff).
PC9 fix active (HAL_SD_ConfigWideBusOperation absent). stepperX/Y/Z/E0 present, C115 0,
cpsid/cpsie 4, REINIT_NOISY_LCD absent, RX128/TX64/BLOCK64, MPC D 4.5.

== 2026-09-29 (late): Feb A/B HANG; layout-sensitivity finding; boot tracer round ==
Results: Feb A (ed35a82c34) and B both HANG. January noREINIT + UART on all 4 axes + PC9 fix
(aquila-2026-January-noREINIT-allUART-PC9fix.bin) also HANGS.

Finding: the booting Jan E-only noREINIT image and hanging image A compile to IDENTICAL code
(fnhash.py: 1889 functions, 0 changed; .text same size/address). Only differences:
  - .rodata strings (language re-export, dates), +0x20 bytes
  - RAM: upstream 488bd82db0 ("stepper.ne => stepper.nle") reorders Stepper statics, +4 B
    padding, so every .bss symbol from 0x20005210 to _end moves +4 (stepperE0, Temperature,
    SdVolume::cacheBuffer_, SoftwareSerial, IWatchdog, uwTick, malloc state...). Heap start
    unchanged (ALIGN 8 -> 0x20005b50 in both).
  => looks like a latent RAM-layout-sensitive bug (overrun / uninit / race), not a bad commit.
     Consistent with the "marginal" flips seen since Nov.
With A flashed, OctoPrint got NO bytes at 500000/250000/115200 (no banner, no reset loop).

Images (all E-only UART, low RAM, MPC, REINIT off, HAS_CGCODE off; verified stepperE0 only,
C115 0, cps 4, only MarlinUI::init calls init_lcd):
  aquila-2026-Feb-A-trace.bin          (219,272 B)  A + boot tracer. RAM map identical to A.
  aquila-2026-Feb-A-ne-JanRAMlayout.bin (218,440 B) A with 488bd82db0 reversed. RAM map == Jan.
  aquila-2026-January-nle-ARAMlayout.bin (218,408 B) Jan + 488bd82db0. RAM map == A.
  Layout theory predicts: A-ne BOOTS, Jan-nle HANGS. Code of each pair is identical (fnhash 0).
Rebuild: FA tree = 2026-Feb-FA-ed35a82c34-oldrecipe-noREINIT-full.patch; JanNR tree =
  2026-January-oldrecipe-MPC-lowRAM-UART-E-only-full.patch + REINIT_NOISY_LCD commented out.
  Then boottrace/{FAT-vs-FA,FAne-vs-FA,JanNle-vs-JanNR}.diff. JanAll = JanNR +
  2026-January-noREINIT-allUART-vs-Eonly.diff.

Boot tracer (boottrace/boottrace.cpp -> Marlin/src/HAL/STM32/, hook = HAL-systick-hook.diff):
  - No static/global variables (RAM map must match the untraced build; check with nm).
  - SysTick: once uptime >= 8 s and !Marlin::isRunning(), every 2 s polls out on USART1
    (500000): "BT t=<ms> st=<MarlinState> pc= lr= psr= exc= sp= ra: <code addrs on stack>".
    Finds the SysTick exception frame by scanning MSP for EXC_RETURN (index 7 in this build).
  - HardFault/MemManage/BusFault/UsageFault: "FAULT ipsr= pc= lr= psr= exc= cfsr= hfsr= mmfar=
    bfar= sp= st= ra:" repeated ~every 1-2 s forever, refreshing IWDG.
  - Nothing printed on a normal boot (setup reaches MF_RUNNING before 8 s).
Reading it: leave the hung printer powered >= 10 s, then
    python3 ~/Downloads/aquila-bisect-tools/boottrace/octo_connect.py 500000 30
  (connects OctoPrint and streams Recv: lines; key from ~/Downloads/octo.txt, never printed).
  Symbolize (Thumb return addresses: subtract 1):
    ~/.platformio/packages/toolchain-gccarmnoneeabi@1.90201.191206/bin/arm-none-eabi-addr2line \
      -f -C -i -e elf/aquila-2026-Feb-A-trace.elf 0x0800xxxx ...
  No output at all => IRQs disabled forever, lockup, reset loop before 8 s (would show "start"
  banners), or the USB link isn't up (power-on order quirk: unplug/replug OTG at the phone).
  If A-trace BOOTS: the tracer only moved flash/code addresses, so suspect flash layout/timing.
elf/ keeps the ELFs of A, A-trace, Jan E-only noREINIT and Jan allUART for symbolizing/diffing.
