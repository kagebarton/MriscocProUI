Standard MarlinFirmware (not MriscocProUI) test builds, 2026-09-27.
Repo: ~/Marlin, remote `upstream` = MarlinFirmware/Marlin bugfix-2.1.x.

Config = origin/KTOrigOct2025 (3026cd9840, booted on the Aquila in Oct 2025)
3-way merged onto the target commit's config, then current KT-Sep-2026 hardware
values ported:
  for f in Configuration.h Configuration_adv.h; do
    git show 3026cd9840:Marlin/$f > ours_$f
    git show 37b5b49cce:Marlin/$f > base_$f
    git merge-file -L user -L oct2025 -L target ours_$f base_$f <worktree>/Marlin/$f
    python3 resolve_cfg.py ours_$f        # conflicts + hardware values
  done
  # If the UBL inset / probe offset merged cleanly (older targets) also:
  sed -i 's/^\(\s*#define MESH_INSET\) 15 /\1 25 /; s/-2.58 }/-2.77 }/' ours_Configuration.h
  python3 defs2.py ours_Configuration.h ours_Configuration_adv.h \
      ~/MriscocProUI/Marlin/Configuration.h ~/MriscocProUI/Marlin/Configuration_adv.h   # check
Code: git apply --3way kt-code.patch (pins_CREALITY_V4 UART section + BLOCK_BUFFER_SIZE 512 sanity).
No ISR patch, no PC9 fix, no extra ok_to_send (matches the Oct 2025 build).
Build: PLATFORMIO_BUILD_DIR=... PLATFORMIO_LIBDEPS_DIR=... ~/.platformio/penv/bin/pio run -e STM32F103RE_creality

classicrocker branch -> upstream Marlin commit it contains:
  2025-November -> 09e943a10c (2025-12-03)   2025-December -> c45354a38c (2025-12-25)
