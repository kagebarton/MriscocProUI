# Real vs predicted M109 release for each hot M109 step in a log (steps.seq). Cold starts are skipped;
# use score_cold.py for those. "Real" is when OctoPrint saw the ok, which arrives in ~0.5 s batches.
# Usage: score_steps.py LOG ...
import re, sys, numpy as np
from common import TEMP_RE, log_path, m109

for fn in sys.argv[1:]:
    rows, ev = [], []
    for ln in open(log_path(fn)):
        t, s = ln.rstrip("\n").split("\t", 1); t = float(t)
        if s.startswith("#"): ev.append((t, s)); continue
        if s.startswith("Send: M109") or s.startswith("Send: M104"): ev.append((t, s))
        m = TEMP_RE.search(s)
        if m and "Recv" in s: rows.append((t, float(m[1]), float(m[2]), int(m[3])))
    a = np.array(rows); lab = ""
    for i, (t, s) in enumerate(ev):
        if s.startswith("#STEP M306 E0"): lab = s[14:]
        if not s.startswith("Send: M109"): continue
        cmd = s[6:]; tgt = float(re.search(r"[SR]([\d.]+)", cmd)[1])
        done = next(t2 for t2, s2 in ev[i:] if s2.startswith("#DONE"))
        nxt = next((t2 for t2, s2 in ev[i + 1:] if s2.startswith("#STEP") and not s2.startswith("#STEP M105")), a[-1, 0])
        r = a[(a[:, 0] > t) & (a[:, 0] < nxt)]; tt = r[:, 0] - t
        if r[0, 1] < 150: continue  # cold start
        up = tgt > r[0, 1]
        pred = m109(tt, r[:, 1], 3, tgt=tgt)
        over = (r[:, 1] - tgt).max() if up else (tgt - r[:, 1]).max()
        print(f"{fn:14s} {lab:5s} {cmd:10s} real release +{done - t:5.1f}s  predicted +{pred:5.1f}s  overshoot {over:+.1f} K")
