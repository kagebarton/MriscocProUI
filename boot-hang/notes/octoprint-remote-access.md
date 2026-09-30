---
name: octoprint-remote-access
description: "How Claude drives the Aquila through the user's OctoPrint (octo4a): URL, key file, API approach, power-on order quirk, and dropped bytes in large replies"
metadata:
  node_type: memory
  type: reference
  originSessionId: 93a26742-bb7e-4de4-9f48-da761af91eea
  modified: 2026-09-29T19:49:11.933Z
---

The user lets Claude run printer tests through OctoPrint 1.11.6 on octo4a (Android) at `http://192.168.1.3:5000`. The API key is in `~/Downloads/octo.txt` (chmod 600, set 2026-09-23). Read it into a header and never print it. The serial port is `/dev/ttyOcto4a`. The firmware defaults to 500000, but use 250000 (see below). OctoPrint is set to try 250000 last when auto-detecting.

Approach used on 2026-09-23. Helper scripts saved on 2026-09-29 in `~/Downloads/aquila-bisect-tools/boottrace/`: `octo_connect.py <baud> <secs>` connects and streams the terminal, useful for reading a hung printer's boot trace. Rewrite them if missing:
- Send G-code with `POST /api/printer/command`. It returns 204 and not the reply.
- To read replies, get a user and session from `POST /api/login {"passive":true}`, then open `ws://…/sockjs/websocket` and send `{"auth":"user:session"}`. `current.logs` streams the `Send:`/`Recv:` terminal lines.
- Match each `ok` to its `Send:` in order, because OctoPrint's own polling lines are mixed in. The firmware has ADVANCED_OK (`ok P255 B7`) and AUTOREPORT_TEMP.
- After `POST /api/connection connect`, the state reads `Closed` for a moment before moving to `Connecting`. Don't treat that first `Closed` as a failure.

**Power-on order:** octo4a often doesn't see the printer unless things are powered in a certain order. The user thinks it's phone first, then printer, and blames the OTG cable. The user has taped over the 5 V pin of the OTG plug on the printer side so the phone can't feed the printer. That means the CH9340C runs only on printer power. Leading theory: like the CH340, the chip probably has no VBUS sense, so it signals it's plugged in as soon as the printer powers up. Printer first means the phone boots with the device already present, and octo4a may miss the attach event. Not confirmed. The test is to unplug and replug USB at the phone when octo4a can't see the printer. If the printer answers nothing at any baud, check this first.

**Dropped bytes at 500000, solved by 250000 (2026-09-23, firmware "2.1.3g-9Aquila-UBL" built Nov 22 2025):** at 500000, replies from the printer lose 0.5–1% of their bytes, in 1–5 byte holes about every 290 bytes (≈5.8 ms). These are clean deletions with no garbage characters. At 250000 (via `M575 B250000`), 11 runs of M115, M503 and M503 S0 lost 0 bytes. So the loss is on the receiving side: the CH9340C, the phone's USB reads or octo4a stall every few ms and overflow a small buffer. The printer's UART can't drop bytes it transmits. The phone and chip weren't isolated from each other; plugging the adapter into a PC at 500000 would do it. The fix without reflashing is the ProUI "250K baud" checkbox (`HMI_data.Baud250K`, saved in EEPROM), which injects `M575B250` at settings load. An M502 unticks it. Full replies are M115 = 1124 B, M503 = 2102 B. Related: [[printer-serial-stepper-isr-patch]], [[aquila-hardware-mods]].

**Re-tested 2026-09-29 with the reduced-buffer build** (M115 says `2.1.3g-11Aquila-UBL (Sep 29 2026 15:35:38)`; printer TX buffer 128→64, RX 2048→128, planner 64). At 500000 it still drops about 1% on M115 and M503 and about 0.4% on M503 S0. The holes are still about 291 B apart (≈5.8 ms) and fall at the same offsets from the start of the reply across runs. Halving the printer's TX buffer didn't change that spacing, so printer buffer sizes aren't the cause. That fits a limit on the receiving side, such as the host's USB read size. Watch out: comparing runs misses bytes that every run loses. For example, the M906 line lost `00 ` in all 5 runs (`Y10Z700`), so check the captured lines against the known config or formats too.

On connect the websocket replays old terminal lines in a `history` message. Read only `current.logs`, or stale output looks like fresh replies. OctoPrint sets autoreport to `M155 S2` on its own, so send `M155 S1` to get 1 Hz temperatures.

**BufferBuddy is ruled out as the cause of the drops.** OctoPrint 1.11.6 logs `Recv:` in `_readline()` before any `gcode.received` hook runs, and the plugin can only pass or swallow whole lines. The *installed* plugin is fflosi/BufferBuddy 0.1.1 (target `min(planner/2, 45)` = **45** in flight). It is not the user's fork github.com/kagebarton/BufferBuddy, whose target is `min(BUFSIZE-1, 255)` = 7. Both report version 0.1.1, and the fork's update config points at fflosi, so OctoPrint can't tell them apart. On 2026-09-23 the user set it to monitor only (`enabled` off).

**OctoPrint serial settings as of 2026-09-23:** `ackMax` 1 and `supportResendsWithoutOk` "always", meaning OctoPrint treats `Resend:` itself as an ok. `swallowOkAfterResend` is true but unused in 1.11.6's comm.py. The flashed firmware sends two oks per resend, and branch commit 174923c33c removes one, so a resend can count as up to three oks. The right pairing is "detect" plus the new firmware. OctoPrint's log only covers the current day.
