# Score a realistic start sequence (start_pla.seq, start_petg.seq): for each full-temperature M104,
# how long the nozzle waited at the wiper after M109 was sent, total M104 -> release, and the overshoot.
# Usage: score_start.py LOG ...
import re, sys, numpy as np
from common import TEMP_RE, log_path

for fn in sys.argv[1:]:
    rows, ev = [], []
    for ln in open(log_path(fn)):
        t, s = ln.rstrip("\n").split("\t", 1); t = float(t)
        if s.startswith("#") or s.startswith("Send: M10") or s.startswith("Send: G28"): ev.append((t, s))
        m = TEMP_RE.search(s)
        if m and "Recv" in s: rows.append((t, float(m[1]), float(m[2]), int(m[3])))
    a = np.array(rows); lab = ""
    for i, (t, s) in enumerate(ev):
        if s.startswith("#STEP M306 E0"): lab = s[14:]
        m = re.match(r"Send: M104 S(2\d\d)", s)
        if not m: continue
        tgt = float(m[1])
        i109 = next(j for j in range(i, len(ev)) if ev[j][1].startswith(f"Send: M109 S{m[1]}"))
        t109 = ev[i109][0]; done = next(t2 for t2, s2 in ev[i109:] if s2.startswith("#DONE"))
        r = a[(a[:, 0] >= t) & (a[:, 0] < done + 45)]; T109 = np.interp(t109, a[:, 0], a[:, 1])
        after = r[r[:, 0] >= t109]
        print(f"{fn} {lab}: target {tgt:.0f}  start {r[0,1]:.0f}C  at M109 send {T109:.1f}C (+{t109-t:.0f}s after M104)  "
              f"WAIT AT WIPER {done-t109:4.1f}s  M104->release {done-t:4.1f}s  overshoot {after[:,1].max()-tgt:+.1f}K  min after release {r[r[:,0]>done][:,1].min()-tgt:+.1f}K")
