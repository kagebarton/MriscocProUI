---
name: proui-lib-serial-layout
description: "Keep HAS_CGCODE off: the prebuilt libproui.a hard-faults at boot with this fork's RX_BUFFER_SIZE 2048"
metadata:
  node_type: memory
  type: project
  originSessionId: 1b7719ec-1b37-4f08-b42c-7d79756789ff
  modified: 2026-09-23T22:31:29.329Z
---

`Marlin/lib/proui/*/libproui_*.a` (MRiscoC's closed-source ProUI part) was compiled for Marlin's default serial buffers, RX 128 / TX 64. That gives a 320-byte `HardwareSerial`. It reaches the `SerialBase` part of `MSerial1` at a hard-coded `MSerial1+0x144`.

This fork sets `RX_BUFFER_SIZE 2048` / `TX_BUFFER_SIZE 128` for 500k serial ([[printer-serial-stepper-isr-patch]]). That makes `HardwareSerial` 2304 B, so the real offset is +0x904.

The library's own `ProUIClass::C115()` and `C29/C412/C562/C810/C851_report()` then call `SerialBase::write` with a pointer into the RX buffer. That loads a zero vtable, jumps to the bootloader's SP and hard-faults. The hard fault also stops UART TX, so any unflushed serial lines are lost.

- Those library functions are reached only with `HAS_CGCODE`: `ProEx.C115()` in setup() right after `hal.init_board()`, and custom_gcodes.cpp.
- Library copies of the shared serial templates, such as `SERIAL_ECHO<float>`, are safe. The linker keeps Marlin's own copies.
- Upstream commit c892617ff4 (classicrocker883, 2026-02-02, "Update - configurations") turned `HAS_CGCODE` on. KT-Sep-2025 had it commented out.
- On 2026-09-23 the KT-Sep-2026 boot hang at the Voxelab logo was traced to exactly this, and `HAS_CGCODE` was commented out in Configuration.h.

**Why:** a fast-forward re-enabled it silently and bricked boot. The screen stays on the DWIN's own logo and serial shows nothing.
**How to apply:**
- After every upstream merge, check that `HAS_CGCODE` is still off (or that RX/TX buffers are back to default).
- To check a built ELF: search `.text` for the literal `MSerial1+0x144`. It should have no hits **while RX/TX are enlarged**.
  - With default buffers (RX 128 / TX 64, the low-RAM builds of 2026-09-29), +0x144 *is* the real SerialBase offset. Dec+ configs have no MEATPACK, so Marlin's own SERIAL_ECHO code references it directly: 59 hits in Dec/latest low-RAM images, all harmless. Check instead that `ProUIClass::C115` is absent from `nm -C`.
- Also dropped upstream in d65034a176 (Dec 2025): `MEATPACK_ON_SERIAL_PORT_1` and `M114_DETAIL`. The user's old build had both.
