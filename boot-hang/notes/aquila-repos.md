---
name: aquila-repos
description: "The user's two Aquila firmware repos (~/MriscocProUI fork vs ~/Marlin standard), their remotes and key branches; `upstream` means different things in each"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1b7719ec-1b37-4f08-b42c-7d79756789ff
  modified: 2026-09-29T19:36:19.844Z
---

The user's Aquila firmware work spans two repos. `upstream` points somewhere different in each, so check which repo you are in before resolving a ref.

**~/MriscocProUI:** the user's fork of classicrocker883's MRiscoC ProUI fork. It links the closed `libproui.a`.
- `origin` = kagebarton/MriscocProUI; `upstream` = classicrocker883/MriscocProUI, which has monthly branches `2025-October` … `2026-September`.
- Local ref `marlin/bugfix-2.1.x` was fetched from ~/Marlin on 2026-09-27.
- Working branch: `KT-Sep-2026`, not pushed. Its working tree holds the uncommitted MPC dead-time patch and HAS_CGCODE off ([[mpc-deadtime-patch]]).
- Last build known to work on the printer: `origin/KT-Sep-2025`. `Mriscoc-2023` is an old, unrelated line.
- Local `KT-Nov-2025` (2026-09-29, not pushed): upstream/2025-November, the last monthly branch that boots, plus the user's setup and the MPC dead-time patch. It hangs too.
- Local `KT-Sep-2025-MPC` (2026-09-29, not pushed, no tracking): origin/KT-Sep-2025 + f1d2a64609 (MPC) + dbd23a2f21 (buffers: RX 128, TX 64, BLOCK_BUFFER_SIZE 64). It is the firmware on the printer and boots ([[mpc-deadtime-patch]]).

**~/Marlin:** the user's fork of standard MarlinFirmware.
- `origin` = kagebarton/Marlin; `upstream` = MarlinFirmware/Marlin (remote added 2026-09-27).
- Local `bugfix-2.1.x` is stale (2024-09-29); use `upstream/bugfix-2.1.x`.
- `origin/KTOrigOct2025` (3026cd9840) is upstream at 2025-10-20 plus the user's config ("Minimum merge from CR883's setup"). It **booted on the Aquila with TMC UART on all four axes**, so it is the base config for standard-Marlin test builds.
- `origin/Oct2025` is plain upstream at 2025-10-20.

**Shared history:** classicrocker's monthly branches merge MarlinFirmware commits with their SHAs intact, so an upstream commit can be found in either repo.
- The `2025-November` branch contains upstream 09e943a10c (2025-12-03).
- The `2025-December` branch contains upstream c45354a38c (2025-12-25).
- `git merge-base upstream/<month> marlin/bugfix-2.1.x`, run in ~/MriscocProUI, gives the upstream commit for any other month.

**Memory copies:** the Aquila memories exist in both projects' memory folders; they were copied from ~/MriscocProUI to ~/Marlin on 2026-09-27. The two copies can drift apart. The boot-hang bisect ([[kt-sep-2026-display-dead]]) continues in ~/Marlin.

**Why:** both repos have an `upstream` remote, and a ref copied from notes written in the other repo resolves to the wrong project or fails.
**How to apply:** before running a git command on a ref taken from memory, check which repo the note means. Put fixes meant for the user's real build onto KT-Sep-2026 in ~/MriscocProUI, unless the user moves to standard Marlin.
