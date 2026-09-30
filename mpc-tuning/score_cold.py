# Score the cold start to 240 in a log from the first "M109" step (cold_start.seq, steps.seq).
# Times are from the moment the nozzle passes 200 C, so the full-power climb, which no tuning changes, drops out.
# M109 release is predicted from the logged temperatures; the printer releases up to ~1 s earlier (see README).
# Usage: score_cold.py LOG ...
import sys, numpy as np
from common import TEMP_RE, log_path, m109

def load(fn):
    rows = []; st = None; mpc = ""
    for ln in open(log_path(fn)):
        t, s = ln.rstrip("\n").split("\t", 1); t = float(t)
        if s.startswith("#STEP M109") and st is None: st = t
        if s.startswith("#STEP M306 E0") and st is None: mpc += s[14:] + " "
        m = TEMP_RE.search(s)
        if m and "Recv" in s: rows.append((t, float(m[1]), float(m[2]), int(m[3])))
    a = np.array(rows); a = a[a[:, 0] >= st]
    return a, mpc.strip() or "(saved)"

def score(fn):
    a, mpc = load(fn)
    a = a[a[:, 2] == 240]; brk = np.nonzero(np.diff(a[:, 0]) > 5)[0]
    if len(brk): a = a[: brk[0] + 1]
    tt, y = a[:, 0], a[:, 1]
    c = tt[np.argmax(y >= 200)]; w = (tt >= c) & (tt < c + 130); tw, yw = tt[w] - c, y[w]
    r239 = tw[np.argmax(yw >= 239)] if (yw >= 239).any() else np.nan
    k = np.argmax(yw >= 239); dip = yw[k:].min() - 240
    return mpc, r239, yw.max() - 240, dip, m109(tw, yw, 10), m109(tw, yw, 3)

if __name__ == "__main__":
    for fn in sys.argv[1:]:
        mpc, r239, mx, dip, r10, r3 = score(fn)
        print(f"{fn:18s} {mpc:22s} first within 1K +{r239:4.0f}s  max {mx:+.1f}  dip after {dip:+.1f}  M109 release (3s residency) +{r3:4.0f}s  (10s residency +{r10:4.0f}s)")
