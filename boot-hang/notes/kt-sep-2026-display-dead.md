---
name: kt-sep-2026-display-dead
description: "Open since 2026-09-23: newer MriscocProUI builds stick at the Voxelab logo on the user's Aquila. Causes found: RAM headroom, REINIT_NOISY_LCD (Jan 2026), Y/PC9. Latest: Jan vs Feb-A differ only by a 4-byte RAM shift (identical code), so a layout-sensitive bug; boot-tracer round sent. Where to resume, results table, recipes."
metadata:
  node_type: memory
  type: project
  originSessionId: 1b7719ec-1b37-4f08-b42c-7d79756789ff
  modified: 2026-09-29T20:49:59.652Z
---

## Where to resume (as of 2026-09-29, late)

**Approach (user, 2026-09-29): hybrid.** Keep flashing bisect images, but when a build hangs with the printer powered, also query it over OctoPrint ([[octoprint-remote-access]]) to troubleshoot directly.

**State:**
- Boots: Jan 2026 old recipe + REINIT_NOISY_LCD off, UART on E only (`aquila-2026-January-oldrecipe-E-only-noREINIT.bin`).
- Hangs: the same Jan tree with UART on all four axes + PC9 fix (`aquila-2026-January-noREINIT-allUART-PC9fix.bin`, 2026-09-29), and Feb images A and B.
- **Jan (boots) and Feb-A (hangs) compile to identical code.** The only differences are strings and a +4-byte shift of every .bss symbol from 0x20005210 on, caused by upstream 488bd82db0 (`Stepper::ne` renamed to `nle`). So it's a latent **RAM-layout-sensitive bug**, not a bad commit. That fits the marginal flips seen since Nov and makes further commit bisecting unreliable.
- With A flashed, OctoPrint got **no bytes** at 500000/250000/115200. So there's no reset loop, and setup never reaches loop() (or it faulted).

**Round sent 2026-09-29, results pending.** All E-only, low RAM, MPC, REINIT off; details and rebuild steps in the README section "Feb A/B HANG; layout-sensitivity finding; boot tracer round":
1. `~/Downloads/aquila-2026-Feb-A-trace.bin`: A + RAM-neutral boot tracer (`aquila-bisect-tools/boottrace/boottrace.cpp`). If it hangs, leave it powered ≥10 s and run `boottrace/octo_connect.py 500000 30`, then read the `BT …`/`FAULT …` lines. Symbolize with addr2line against `aquila-bisect-tools/elf/aquila-2026-Feb-A-trace.elf`, subtracting 1 from Thumb return addresses.
2. `aquila-2026-Feb-A-ne-JanRAMlayout.bin`: A with 488bd82db0 reversed, so the RAM map equals Jan's. The layout theory predicts BOOT.
3. `aquila-2026-January-nle-ARAMlayout.bin`: Jan + 488bd82db0, so the RAM map equals A's. The layout theory predicts HANG.
- Also free and not yet asked: boot a hanging image with the SD card removed. SdVolume::cacheBuffer_ is in the shifted region.
- If the trace gives a PC, add a trace to the all-UART Jan build as well (same tracer, same diff), since that is the goal config.

**Scratch trees** (`$S` = session scratchpad, may be wiped): wt_FAT, wt_FAne, wt_JanNle, wt_JanAll, wt_JanNR, wt_FA (build dirs pb_*). Everything needed to rebuild is in `~/Downloads/aquila-bisect-tools/` (boottrace/*.diff, the full patches, elf/).

## Older: standard-Marlin bisect (as of 2026-09-27)

**Finding:** classicrocker's monthly branches merge MarlinFirmware with the SHAs intact.
- 2025-November contains upstream 09e943a10c (2025-12-03); 2025-December contains c45354a38c (2025-12-25).
- Between those two, the fork's only firmware-code change is d65034a176 (queue.cpp). The fork's other edits differ only in comment whitespace.
- So the Nov→Dec boot break is **upstream Marlin code**. Standard Marlin alone is unlikely to fix it, but its linear history can be bisected: about 50 commits, ~6 steps.

**Round sent to the user on 2026-09-27** (all standard Marlin, KTOrigOct2025 config + current hardware values, UART on all 4 axes, no ISR patch, no PC9 fix):
- `~/Downloads/aquila-std-1-marlin-2025-12-03.bin`: expect BOOT, like Nov.
- `aquila-std-2-marlin-2025-12-12.bin`: midpoint b99f5c3618, just before "Single precision float" and "Clean up HAL/timers".
- `aquila-std-3-marlin-2025-12-25.bin`: expect HANG, like Dec.
- `aquila-std-4-marlin-2026-09-28.bin`: today's upstream HEAD, 124ad16e2f.
- If 1 boots and 3 hangs, keep bisecting on upstream (`git log --first-parent 09e943a10c..c45354a38c`), then revert the culprit on KT-Sep-2026.
- If 1 hangs too, standard Marlin differs from the fork in some boot-relevant way, and the bisect has no base.
- Recipe, resolver and configs: `~/Downloads/aquila-bisect-tools/std-marlin/README.txt`. `~/Marlin` now has remote `upstream` = MarlinFirmware.
- All four images: RAM 81 % static (53 KB of 64 KB).
- **UI:** all four images use standard Marlin's built-in ProUI (`DWIN_LCD_PROUI`); none links `libproui`, and `PROUI_EX` is ignored.
- **Every DWIN UI shares one handshake**, `dwinHandshake()` in `lcd/dwin/common/dwin_api.cpp`. ProUI, Creality and MarlinUI call it from `MarlinUI::init_lcd()` in `ui.init()`, after `tmc_serial_begin()` and before `stepper.init()`. Switching UI won't avoid the hang.
- **Diagnostic idea, offered 2026-09-27:** ProUI draws nothing until `dwinInitScreen()` at the end of `setup()`. `DWIN_MARLINUI_PORTRAIT` draws its boot screen right after the handshake.
  - A MarlinUI variant of a hanging image (e.g. Dec 25) would show where setup stops: Voxelab logo stays = handshake failed or an earlier stall; boot screen then freeze = a later stall.
  - It changes the memory layout, so it is a side test only. Keep the bisect on ProUI.

## Earlier state (as of 2026-09-24)

**Step-10 results (2026-09-24):**
- `aquila-test-dec-Yonly-PC9fix.bin`: **BOOT**. Y's trigger is the PC9/SDIO conflict, and the PC9 fix solves it.
- `aquila-test-dec-Yonly-ISRrevert.bin`: **HANG**.
- `aquila-test-dec-Zonly-ISRrevert.bin`: **HANG**. Z (PA13) is still unsolved.
- Checked on the way: the bootloader never touches IWDG, so it's not a bootloader watchdog reset loop. PA13 is only on the 4-pin debug header, and no other macro resolves to it. The variant pin map is correct (PA13 = 13 → PA_13). Oddity: the variant's `LED_BUILTIN` is PB11, the DWIN RX line.

**Step 11: "consolidate the wins", the user's last test of 2026-09-24.** Z standalone, UART on X/Y/E, PC9 fix, stock ISR:
- `aquila-test-dec-STOCK+UART-XYE+PC9fix.bin` (179,748 B): stock Dec config.
- `aquila-test-dec-USERCONFIG+UART-XYE+PC9fix.bin` (219,632 B): the Dec user config with `TMC_UART_PIN_Z` commented out and Z_DRIVER_TYPE TMC2208_STANDALONE, plus fork code, 174923c33c and 4df62af233. No ISR revert, no MPC patch. Full diff in `aquila-bisect-tools/dec-user-XYE-PC9fix-full.patch`; `axes.py` makes stock multi-axis configs.
- **Result (reported 2026-09-24): NEITHER BOOTS.**
- X, E and Y+PC9fix each boot alone, yet X+Y+E+PC9fix hangs, even on stock config.
- So it's **cumulative, not one bad pin**. Adding UART drivers pushes it over some threshold: setup time, SoftwareSerial/TIM7 load, RAM/heap from `new SoftwareSerial`, or timing. Z alone is just enough to tip it.
- That fits the marginal flips seen all along: the Nov ISR revert, and the user config vs stock.
- Next ideas, empirical:
  - Pairs on Dec stock: X+E, X+Y+PC9, Y+PC9+E. This finds how many UART drivers it takes.
  - If not every axis can keep UART, drop them in reverse order of this priority: **E > Y > X > Z**, as agreed with the user on 2026-09-24. Try Y+PC9+E first; E-only is the fallback, but it was only tested on stock config.
    - Why: the saved settings run every driver in stealthChop (`M569 S1`), which is what a standalone TMC2208 does anyway. So UART mostly buys current control, monitoring, and the option to switch modes.
    - E runs LA K0.04 in stealthChop, which only UART can move to spreadCycle.
    - An axis that loses UART reads current from its Vref pot again, so check the pot first.
  - The same trio on Nov code.
  - Boot a failing image with the SD card removed.
  - A failing image with USE_WATCHDOG off, which tests a reset loop.
  - Ask the user to watch OctoPrint (115200 for stock builds) during a failing boot: repeated `start` means a reset loop, a single banner means a stall.
- Older open ideas for Z (PA13), not yet tried:
  - Boot the Z-only image with the SD card removed; free, and tests whether SD is involved.
  - Nov code + Z-only (does Z alone hang in Nov? If not, commit-bisect Nov→Dec with this minimal config).
  - Z-only with USE_WATCHDOG off.
  - Z-only + PC9 fix.

**Latest state (end of 2026-09-24):**
- The step-11 consolidation (X+Y+E UART + PC9 fix, Z standalone) **hangs on both stock and user config**, although each of those axes boots alone.
- So the cause looks cumulative or marginal rather than one pin. See the step-11 notes below for the next empirical ideas: pairs, the same trio on Nov code, no SD card, no watchdog, and watching OctoPrint for reset loops.
- Once some Dec user build works: step forward month by month (2026-January … 2026-September) with the same recipe, then port the working recipe onto KT-Sep-2026. That branch still carries the MPC patch ([[mpc-deadtime-patch]]).
- Fallback that already works: `~/Downloads/aquila-bisect-2025-November.bin` (Nov code + the full user setup).

**User's direction (2026-09-24):** find which feature combinations boot, empirically. Don't spend effort on root-causing. The user is happy to flash 2–4 test images per round and report boot or hang.

## Symptom

- The DWIN stays on the display's own Voxelab logo; ProUI never draws anything.
- The logo stays up until `DWIN_InitScreen()` near the end of `setup()`. So "hang" can mean a stall anywhere in setup, as well as a dead display link.
- Trace 4, on a KT-Sep-2026 user-config build, showed setup completing with the DWIN handshake getting no reply. The stock-config failures haven't been traced.

## Results table (all env `STM32F103RE_creality`, flashed via the SD bootloader)

"User" means the user's config 3-way merged onto that branch's config. "Stock" means `configurations/Voxelab Aquila/Default`. "UART" means TMC2208 UART on X=PC6, Y=PC9, Z=PA13, E=PA15, via the fork's pins section. "Rev" means the Sep-2025 stepper-ISR revert.

| Code | Config | Rev | Other | Result |
|---|---|---|---|---|
| KT-Sep-2025 (rollback, Nov-2025 own build) | user | yes | | BOOT |
| upstream 2025-November | user | yes | | BOOT (`aquila-bisect-2025-November.bin`) |
| 2025-November | user | no | | BOOT (test-B) |
| 2025-November | stock+UART | no | | HANG |
| 2025-November | stock+UART | yes | | BOOT (test-A) |
| 2025-December | user | no | | HANG |
| 2025-December | user | yes | | HANG (test-D) |
| 2025-December | stock | no | no UART | BOOT |
| 2025-December | stock+UART | no | | HANG |
| 2025-December | stock+UART | no | PC9 fix | HANG |
| 2025-December | stock+UART | yes | | HANG (test-C) |
| 2025-December | stock + X only | no | | BOOT |
| 2025-December | stock + E only | no | | BOOT |
| 2025-December | stock + Y only (PC9) | no | | HANG |
| 2025-December | stock + Z only (PA13) | no | | HANG |
| 2025-December | stock + Y only | no | PC9 fix | BOOT |
| 2025-December | stock + Y only | yes | | HANG |
| 2025-December | stock + Z only | yes | | HANG |
| 2025-December | stock + X,Y,E (Z standalone) | no | PC9 fix | HANG (step 11) |
| 2025-December | user, Z standalone (X,Y,E UART) | no | PC9 fix | HANG (step 11) |
| KT-Sep-2026 (+ one-line isr_on fix 788f616313) | user | one-line | | HANG (all trace builds) |
| 2025-November (local KT-Nov-2025) | user | yes | MPC patch | HANG (2026-09-29) |
| KT-Sep-2025 | user | yes | MPC patch, RX128/TX64, BLOCK_BUFFER 64 (RAM 36%) | BOOT (`aquila-KT-Sep-2025-MPC-lowRAM.bin`, 2026-09-29) |
| 2025-November (KT-Nov-2025 export) | user | yes | MPC patch, RX128/TX64, BLOCK_BUFFER 64 (RAM 36%) | BOOT (`aquila-KT-Nov-2025-MPC-lowRAM.bin`, 2026-09-29) |
| KT-Sep-2026 | user | one-line | MPC, low RAM (36%) | HANG (lowRAM-A, 2026-09-29) |
| KT-Sep-2026 | user | one-line | MPC, low RAM, PC9 fix | HANG (lowRAM-B, 2026-09-29) |
| KT-Sep-2026 | user, E-only UART | one-line | MPC, low RAM | HANG (lowRAM-C, 2026-09-29) |
| 2025-December | user, E-only UART | one-line | MPC, low RAM | BOOT (2026-09-29) |
| 2026-March, 2026-June | user (KT-Sep-2026 delta), E-only | one-line | MPC, low RAM | HANG (2026-09-29) |
| 2026-January | user (old Dec recipe), E-only | one-line | MPC, low RAM | HANG (2026-09-29) |
| 2026-January | user (old Dec recipe), E-only | one-line | MPC, low RAM, REINIT_NOISY_LCD off | BOOT (2026-09-29) |
| KT-Sep-2026 | user, E-only UART | one-line | MPC, low RAM, REINIT_NOISY_LCD off | HANG (2026-09-29) |
| 2026-March | user (KT-Sep-2026 delta), E-only | one-line | MPC, low RAM, REINIT_NOISY_LCD off | HANG (2026-09-29) |
| 2026-Feb A (ed35a82c34) and B (9db148c90e) | user (old recipe), E-only | one-line | MPC, low RAM, REINIT off | HANG (2026-09-29); A's code is identical to Jan's, only +4 B RAM shift |
| 2026-January | user (old recipe), UART X/Y/Z/E | one-line | MPC, low RAM, REINIT off, PC9 fix | HANG (2026-09-29) |

**Lead (2026-09-29), not yet tested:** RAM headroom may be the "marginal/cumulative" factor.
- User builds sat at 82% static RAM (~11.7 KB left for heap and stack). Each SoftwareSerial for TMC UART is heap-allocated.
- Nov plus the MPC patch (+56 B) hung, while Nov alone booted.
- The low-RAM variant (BLOCK_BUFFER_SIZE 256→64 frees ~22 KB, serial buffers ~4 KB) booted.
- Try the same buffer cuts on a Dec+ or KT-Sep-2026 user build.
- **Test sent 2026-09-29:** `~/Downloads/aquila-KT-Nov-2025-MPC-lowRAM.bin` (223,572 B, RAM 23,612 B / 36%). It is exactly the hanging KT-Nov-2025 (b8328d9347) plus the same three buffer lines; built from an export, not committed.
  - BOOT means RAM was the Nov+MPC hang; then apply the cuts to KT-Sep-2026.
  - HANG means it's not RAM.
  - Either way the user reflashes `aquila-KT-Sep-2025-MPC-lowRAM.bin` afterwards.
  - **Result: BOOT (user, 2026-09-29).** RAM headroom was what made Nov+MPC hang.
- **Round sent 2026-09-29, the latest code:** KT-Sep-2026 HEAD 174923c33c (contains upstream/2026-September c485acf68f) + the uncommitted MPC diff + the same 3 buffer lines. RAM 23,504 B (35.9%). The one-liner ISR fix gives cpsid/cpsie 4. HAS_CGCODE off. Built from an export; not committed.
  - `~/Downloads/aquila-KT-Sep-2026-MPC-lowRAM-A.bin` (220,972 B): exactly that.
  - `~/Downloads/aquila-KT-Sep-2026-MPC-lowRAM-B-PC9fix.bin` (220,324 B): A + pc9fix.py (HAL_SD_ConfigWideBusOperation absent).
  - Why B: Dec stock + Y-only UART hung without the PC9 fix even though stock config uses little RAM (BLOCK_BUFFER 32), so PC9 is a separate Dec+ trigger. Z-only (PA13) also hung on Dec stock, still unexplained; if B hangs, the next variant is B + Z standalone.
  - Diffs: `aquila-bisect-tools/KT-Sep-2026-MPC-lowRAM-{A,B-PC9fix}.patch`.
  - **Result: NEITHER BOOTS (user, 2026-09-29).** So on the latest code, low RAM (and the PC9 fix) is not enough.
- **Next image sent 2026-09-29, at the user's request:** `~/Downloads/aquila-KT-Sep-2026-MPC-lowRAM-C-UART-E-only.bin` (217,764 B, RAM 35.6%). A with `TMC_UART_PIN_X/Y/Z` commented out and X/Y/Z `TMC2208_STANDALONE`; only `stepperE0` exists. Diff: `aquila-bisect-tools/KT-Sep-2026-MPC-lowRAM-C-UART-E-only.patch`.
  - X/Y/Z current then comes from the board's Vref pots.
  - **Result: HANG (user, 2026-09-29).**
- **Next image sent 2026-09-29, at the user's request:** `~/Downloads/aquila-dec-2025-MPC-lowRAM-UART-E-only.bin` (218,456 B, RAM 35.7%). upstream/2025-December (8ec6a31aa0) + `dec-user-XYE-PC9fix-full.patch` + MPC diff (HAS_CGCODE hunk skipped, already off) + one-liner 788f616313 + the 3 buffer lines + X/Y standalone (Z already was). Same recipe as latest-C, so it tests code age. Full diff: `aquila-bisect-tools/dec-2025-MPC-lowRAM-UART-E-only-full.patch`.
  - Dec *stock* + E-only UART booted before; this is the user config + low RAM.
  - **Result: BOOT (user, 2026-09-29).** So a second, post-Dec break hangs the user config even with E-only UART and low RAM.
- **Month bisect, agreed 2026-09-29:** find the post-Dec break with E only by halving (not month by month), then add axes on the newest month that boots (X, then Y + PC9 fix, Z last). Reason: axis results on Dec may not carry forward, and Sep-2025+MPC already runs all four UART axes.
  - Round 1 sent: `~/Downloads/aquila-2026-March-MPC-lowRAM-UART-E-only.bin` (217,348 B) and `aquila-2026-June-MPC-lowRAM-UART-E-only.bin` (217,404 B), both RAM 35.6%, only stepperE0, C115 absent, cpsid/cpsie 4.
  - Recipe: KT-Sep-2026's fork delta (`aquila-bisect-tools/fork-KT-Sep-2026.patch`) + MPC diff applied with `git apply --3way` in detached worktrees `$S/wt_March`, `$S/wt_June`; see the README section "2026 month bisect". Conflicts: .gitignore and MESH_INSET, both taken from the user side.
  - Round 2: March hangs → Jan + Feb; March boots, June hangs → Apr + May; June boots → Jul + Aug (Sep is known to hang).
  - **Result: March and June both HANG (user, 2026-09-29).**
  - Confound: Dec (boots) used the *old recipe* (Sep-2025-derived user config via `dec-user-XYE-PC9fix-full.patch`); March/June used KT-Sep-2026's delta. So the break may be the recipe, not the code month.
- **Round 2 sent 2026-09-29, old recipe at the user's request:** the booting Dec image's exact delta (`aquila-bisect-tools/dec-2025-oldrecipe-E-only.git.patch`) applied with `git apply --3way` onto Jan and Feb. Feb needed the queue.cpp M410 conflict resolved (`motion.quickstop_stepper()`) and HAS_CGCODE commented out by hand.
  - `~/Downloads/aquila-2026-January-oldrecipe-MPC-lowRAM-UART-E-only.bin` (218,416 B), `aquila-2026-February-oldrecipe-MPC-lowRAM-UART-E-only.bin` (218,252 B). RAM 35.7%, only stepperE0, C115 absent, cpsid/cpsie 4.
  - If both boot, the old vs new recipe difference (config) is the likely cause: next, the old recipe on March/June, or diff the two recipes' active defines with `defs.py`.
  - **Result: January HANGS (user, 2026-09-29).** So the break is in Dec→Jan code (Feb not needed).
- **Prime suspect: `REINIT_NOISY_LCD`** (found 2026-09-29).
  - Upstream 2048e8b173 ("Permit disable REINIT_NOISY_LCD", in the fork's first Jan "Merge w/Marlin" c50a821b7e) replaced an auto-define that *excluded* DWIN/ProUI with a plain `#define REINIT_NOISY_LCD` in Configuration_adv.h, on by default. The 3-way config merge carries it into every Jan+ user config.
  - Effect: `MarlinUI::media_changed()` calls `init_lcd()` on SD detect (ProUI: `delay(750)` + `DWIN_Handshake()` + SetDir + Update), so it fires at boot with the card in.
  - Evidence: DWARF shows it in every hanging Jan+ image (Jan, Feb, Mar, Jun, KT-Sep-2026 A/B/C) and in none that booted (Dec E-only, Nov low-RAM, Sep-2025). The hanging images have an extra `init_lcd` caller in `media_changed`.
  - The other Dec→Jan firmware changes, as fallback bisect points: the fork's `macros.h` edit ea19ad2827 and the second Marlin merge c85efb122f (SOFT_FEED_HOLD, ADC calc fix).
- **Round sent 2026-09-29:** four images, each an earlier hung build with only `REINIT_NOISY_LCD` commented out (verified absent; only `MarlinUI::init` calls `init_lcd`):
  1. `~/Downloads/aquila-2026-January-oldrecipe-E-only-noREINIT.bin` (218,408 B): the direct A/B vs the hung Jan image.
  2. `aquila-KT-Sep-2026-MPC-lowRAM-C-E-only-noREINIT.bin` (217,756 B): latest, E-only.
  3. `aquila-KT-Sep-2026-MPC-lowRAM-EY-PC9fix-noREINIT.bin` (218,364 B): latest, UART E+Y, PC9 fix, X/Z standalone.
  4. `aquila-KT-Sep-2026-MPC-lowRAM-B-allUART-PC9fix-noREINIT.bin` (220,316 B): latest, all four UART axes + PC9 fix. The goal image; may still hang from the separate Dec-era multi-axis issue (Dec stock X+Y+E+PC9fix hung with REINIT off).
  - Build trees: `$S/wt_{JanNR,latENR,latEYNR,latBNR}`, build dirs `pb_*`.
  - If 1 hangs, REINIT isn't it: bisect Jan at c50a821b7e and ea19ad2827.
  - **Result (user, 2026-09-29): 1 (Jan-noREINIT) BOOTS, 2 (latest E-only noREINIT) HANGS.** REINIT_NOISY_LCD confirmed as the Dec→Jan break; keep it commented out in every Jan+ build. A second break sits between Jan and Sep 2026. Images 3/4 not reported (moot while E-only hangs).
- **Recipes are equivalent in code** (checked 2026-09-29): the old and new recipe patches have identical hunks for queue.cpp, dwin.cpp, stepper.cpp, creality.ld and platformio.ini; they differ only in the PC9 fix (inactive with Y UART off) and where the MPC SanityCheck hunk lives. Active config differs only by upstream renames/additions (MAX_SAVED_MESHES from b08839e0fd, SDSORT options, SD_MAX_READ_ERRORS). So new-recipe month images test code month only.
- **Round sent 2026-09-29:** new recipe + REINIT off, E-only, low RAM, MPC, all verified (stepperE0 only, C115 absent, cps 4, only MarlinUI::init calls init_lcd):
  - `~/Downloads/aquila-2026-{March,April,June,August}-E-only-noREINIT.bin` (217,340 / 217,068 / 217,396 / 217,588 B).
  - Trees `$S/wt_{MarchNR,April,JuneNR,August}`; Apr/Aug patches in `aquila-bisect-tools/2026-{April,August}-MPC-lowRAM-E-only-noREINIT-full.patch`.
  - Suggested order: June first; boots → August; hangs → March, then April. Known ends: Jan boots, Sep hangs.
  - **Result (user, 2026-09-29): March HANGS.** Second break is Jan..March. The Jan-vs-March macro diff shows no config default flip, only code refactors (motion encapsulation, ProUI mesh bounds). libproui.a is unchanged in this range.
- **Round sent 2026-09-29, Feb split points:** old recipe + REINIT off + HAS_CGCODE off; queue.cpp resolves to `case 410: motion.quickstop_stepper();` from B on. All E-only, RAM 35.7%, verified as before.
  - A `~/Downloads/aquila-2026-Feb-A-first-merge-noREINIT.bin`: ed35a82c34 (02-06 Marlin merge + c892617ff4 configs).
  - B `aquila-2026-Feb-B-motion-refactor-noREINIT.bin`: 9db148c90e (02-12 merge: Motion encapsulation #27866, "Run motion logic before UI" 544f9e6104). Prime suspect.
  - C `aquila-2026-Feb-C-merge-0222-noREINIT.bin`: 86da338293 (+96328288d2 fork optimization, 3cc4c063ae, 86da338293 merges).
  - D `aquila-2026-Feb-D-head-noREINIT.bin`: 06c644d1af = upstream/2026-February (+82dd40dcb9 "new mesh set", 03-09 merge).
  - After D, up to March: dec709fc08 merge, 113b180631, bac98c2918, 90a4a00fc8 merge.
  - Order: B first; B hangs → A; B boots → D, then C if D hangs.
  - Trees `$S/wt_F{A,B,C,D}`; patches `aquila-bisect-tools/2026-Feb-F*-oldrecipe-noREINIT-full.patch`.
  - **Result (user, 2026-09-29): A and B both HANG.** Break is in the first Feb Marlin merge ed35a82c34 (11 upstream commits; the fork side only touches configs/Version.h).
- **Jan (boots) vs A (hangs) compile to identical code** (fnhash.py: 1889 functions, 0 changed; .text same size and address). Differences: .rodata strings (language re-export, date) and a **4-byte RAM shift**: upstream 488bd82db0 renamed `Stepper::ne` → `nle`, which reorders stepper statics and adds padding, so everything from 0x20005210 to .bss end (stepperE0, Temperature, SdVolume::cacheBuffer_, SoftwareSerial, IWatchdog, uwTick…) moves +4. Heap start is unchanged (ALIGN 8). Likely a layout-sensitive latent bug, which would explain the marginal flips all along.
- **Hybrid step (user, 2026-09-29):** use OctoPrint during hangs as well as bisect images. With A flashed the printer answered nothing at 500000/250000/115200, so setup never reaches loop() (or it faults).
  - Built then (verified and sent later the same day): `wt_FAT` (A + RAM-neutral tracer `$S/boottrace.cpp`: SysTick prints stacked PC/LR/return addresses every 2 s after 8 s if `!Marlin::isRunning()`, and fault handlers loop-print CFSR/HFSR/PC), `wt_FAne` (A with 488bd82db0 reversed = Jan RAM layout), `wt_JanNle` (Jan + 488bd82db0 = A RAM layout).
  - Free test not yet asked: boot A with the SD card removed.
- **2026-09-29:** the user asked for a Nov-lowRAM build with UART on all axes; `aquila-KT-Nov-2025-MPC-lowRAM.bin` already has it (stepperX/Y/Z/E0, TMC2208, pins PC6/PC9/PA13/PA15), so nothing was built.
- **Sent 2026-09-29, at the user's request:** `~/Downloads/aquila-2026-January-noREINIT-allUART-PC9fix.bin` (220,968 B, RAM 36.0%) = the booting Jan E-only noREINIT tree with X/Y/Z UART back on + PC9 fix active. Tree `$S/wt_JanAll`. Tests whether all-axis UART boots on Jan now that RAM and REINIT are fixed (Dec X+Y+E+PC9fix hung at 82% RAM). **Result: HANG (user, 2026-09-29).**
- **Tracer round sent 2026-09-29** (the three images built earlier, verified: RAM maps FAT==A, FAne==Jan, JanNle==A; fnhash 0 changed within each pair; fault vectors → tracer; HAL_SYSTICK_Callback tail-calls boottrace_tick). See "Where to resume" at the top.

**Takeaways:**
- The Y and Z UART pins are the triggers.
- PC9 is also SDIO_D1: the SD runs 4-bit, and SDIO and SoftwareSerial both reconfigure PC9.
- PA13 is SWDIO. `DISABLE_DEBUG` (pins_CREALITY_V4.h) switches SWJ off in setup() before `tmc_serial_begin()`, so there's no obvious conflict for Z.
- On Nov code, either the ISR revert or the user's config was enough to boot; on Dec, neither is.
- The step ISR only runs from `Stepper::init()` on. So the revert mattering means the Nov stock+UART stall is late in setup: after Stepper::init and before DWIN_InitScreen (watchdog init, BL24CXX, DWIN_InitScreen), or a reset loop.
- The system behaves marginally: small changes flip the result. The exact form of the ISR patch might matter too, since KT-Sep-2026 with the one-liner hung.

## Rebuild recipes (tools in `~/Downloads/aquila-bisect-tools/`, see its README)

- **pio:** `~/.platformio/penv/bin/pio` (not on PATH).
- **Build command:**
  ```
  PLATFORMIO_BUILD_DIR=<scratch>/pb_X PLATFORMIO_LIBDEPS_DIR=<scratch>/pl_X pio run -e STM32F103RE_creality
  ```
  Keep build dirs outside the repo, because VS Code wipes `.pio`.
- **Size limit:** keep images under 233,472 B (the bootloader limit).
- **Worktree:** `git worktree add --detach <scratch>/wt_X upstream/<YYYY-Month>`. Remote `upstream` = classicrocker883/MriscocProUI, branches 2025-October … 2026-September. They merge MarlinFirmware with the SHAs intact (not a linear history).
- **User config:** `git merge-file`, with ours = `origin/KT-Sep-2025:Marlin/Configuration*.h`, base = 44a4ec101f, theirs = the branch's config. Conflicts so far:
  - Bed PID: use the new names DEFAULT_BED_KP/KI/KD = 54.26 / 10.60 / 185.22.
  - NOZZLE_TO_PROBE_OFFSET: keep `{ 4.5, 26.5, -2.77 }`.
  - SDSORT block: keep the user's values, plus `SDSORT_QUICK true`.
  - Ready-made merges are in `configs/`.
- **Fork code:** `fork-code.patch` (≤ Nov) or `fork-code-dwin.patch` (≥ Dec, where the dwin.cpp path moved), applied with `git apply --3way`.
  - On Dec, the stepper.cpp hunk conflicts. Restore upstream's stepper.cpp, then run `port_revert.py`, or leave it stock.
  - Also apply 174923c33c (drops the double ok on resend) and, from Dec on, 4df62af233 (M401→M410 quickstop bug from d65034a176).
- **Stock+UART:** copy the three `configurations/Voxelab Aquila/Default/` files into `Marlin/`.
  - Add `#define TMC_UART_PIN_X PC6` (Y PC9, Z PA13, E PA15) and switch the `*_DRIVER_TYPE` lines to `TMC2208`. `one_axis.py` does a single axis.
  - Apply the pins UART section: `git diff 44a4ec101f origin/KT-Sep-2025 -- Marlin/src/pins/stm32f1/pins_CREALITY_V4.h`.
- **ISR revert port** (`port_revert.py`):
  1. Move `hal.isr_off()` from `HAL_STEP_TIMER_ISR()` into `Stepper::isr()` after its statics.
  2. Add `hal.isr_on()` at the top of the `do {` loop.
  3. Delete the standard-motion `hal.isr_on()` before "Time critical".
  - Verify: the `cpsid/cpsie` count in `Stepper::isr` is 4 with the revert, 3 stock.
- **PC9 fix** (`pc9fix.py`): in pins_CREALITY_V4.h, wrap SDIO_D1..D3 in `#ifndef TMC_UART_PIN_Y`. Also wrap HAL/STM32/sdio.h's own defaults in `#ifndef SDIO_D0_PIN`; it redefines D1..D3 unconditionally, so the pins-file edit alone does nothing.
  - Verify: `HAL_SD_ConfigWideBusOperation` is absent from the ELF.
- **HAS_CGCODE:** must stay off with the user's RX 2048 buffers ([[proui-lib-serial-layout]]). Upstream configs turn it on from Nov 2025. Check that no `MSerial1+0x144` literal is in the .bin.
- **MEATPACK:** upstream Dec configs dropped MEATPACK_ON_SERIAL_PORT_1 and M114_DETAIL (d65034a176). The code still supports MEATPACK; the Nov configs had it on.

## Ruled out or checked (don't redo)

- **Toolchain and framework:** GCC 9.2.1, STM32duino 1.9.0, MARLIN_F103Rx variant, TMCStepper 0.8.9 and libproui.a are the same in every build. The stock builds don't even link libproui (no PROUI_EX).
- **Nov vs Dec code up to the DWIN handshake:** identical after normalization (startup, ctors, ISRs, SoftwareSerial on TIM7, tmc_serial_begin, MarlinUI::init/init_lcd, DWIN_Handshake/Send, HardwareSerial). setup() differs only in the MEATPACK serial wrapper.
- **`-fsingle-precision-constant`:** added in Dec (89379cd373). It only changes float math (TMCStepper cs2rms, HardwareTimer getCount/getOverflow for non-TICK formats).
- **Bootloader tail-drop and single-bad-page theories:** refuted from the image layouts.
- **Trace 4 registers (KT-Sep-2026, user config):** clocks, VTOR 0x08007000, AFIO_MAPR 0x04000000, PB10/PB11 modes and USART3 115,385 baud were all correct. The handshake got 0 bytes back, and a red-clear test never showed.
- **Not yet tried:**
  - Trace 5 flash-CRC image (`~/Downloads/aquila-boottrace5-KT-Sep-2026.bin`). It prints `BTF` per-2K CRCs over OctoPrint at 500k; the expected values are zlib.crc32 of 2048-B slices of that .bin.
  - A pairwise-axis test.

## Hardware and bootloader

- **Chip:** the board came with an F103RCT6; the user swapped it for an RET6 (brand not stated) and flashed a Reddit bootloader with an ST-Link.
- **Bootloader:** `~/Downloads/bootloader.hex`. Creality V4-style: `/firmware/*.BIN`, drives the DWIN on USART3, app at 0x08007000.
- **Bootloader limits:** it rejects images over ~230K, and maple envs don't work with it. Upstream CI and releases use only the maple envs, so this non-maple env is barely tested by others.
- **Other mods:** the UART mod and the rest are in [[aquila-hardware-mods]]. The user says the electronics are otherwise stock Aquila.
- **Scratchpad:** `/tmp/claude-1000/...` was wiped by a reboot on 2026-09-24. Rely on `~/Downloads/aquila-bisect-tools/` and the `.bin` files in `~/Downloads`.
- **Scratch worktrees:** `wt_nov`, `wt_dec*`, `wt_nov_*` etc. are registered in the repo's `.git/worktrees`. If the scratchpad is gone, run `git worktree prune`. The repo's own KT-Sep-2026 working tree still holds the uncommitted MPC patch and HAS_CGCODE-off change.
- **OctoPrint:** at 192.168.1.3:5000 ([[octoprint-remote-access]]). Stock-config builds talk at 115200; user builds at 500000.
