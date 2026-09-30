# Check a plant fit in closed loop: replay the targets and M306 D changes from the D-only firmware logs
# through closedloop.run, and compare with what the printer did.
# Usage: validate.py fits/p6_L3.0.npy
import sys, numpy as np
from common import load, log_path, DT, fit_path
from closedloop import run

pb = np.load(fit_path(sys.argv[1])); d = int(pb[0]); pp = pb[1:12]; e0, m0 = pb[12], pb[13]
for fn in ("cold1.log", "steps1.log"):
    a = load(fn); tg = np.arange(0, a[-1, 0] - 1, DT)
    idx = np.clip(np.searchsorted(a[:, 0], tg, side="right") - 1, 0, None); targets = a[idx, 2]
    # D schedule from the "#STEP M306 E0 D<x>" marks
    ds = np.full(len(tg), -1.0); marks = []; rows0 = None
    for ln in open(log_path(fn)):
        t, s = ln.rstrip().split("\t", 1)
        if rows0 is None and "T:" in s and "Recv" in s: rows0 = float(t)
        if s.startswith("#STEP M306 E0 D"): marks.append((float(t), float(s.split("D")[1])))
    for t, D in marks: ds[np.searchsorted(tg, t - rows0):] = D
    ctl = np.array([16.95, 0.2673, 0.0654, 4.5, 0.25, 1.0, 1.0])   # the firmware's constants in these runs
    k = fn == "steps1.log"
    temp, pw = run(pp, d, ctl, targets, a[0, 1], 23.0, 1, 0.2, e0 if k else 23.0, m0 if k else a[0, 1], ds, 0.0, 0.0)
    Tm = np.interp(tg, a[:, 0], a[:, 1])
    print(fn, "closed-loop rms %.2f K" % np.sqrt(np.mean((temp - Tm)[tg > 5] ** 2)))
    for c in np.nonzero(np.diff(targets) != 0)[0]:
        g = targets[c + 1]; sl = slice(c + 1, min(c + 1 + int(100 / DT), len(tg)))
        if g == 0: continue
        up = g > Tm[c]
        f = (lambda x: (x[sl] - g).max()) if up else (lambda x: (g - x[sl]).max())
        # Undershoot after first arriving within 0.3 K of an up-step target
        fm = (lambda x: (g - x[sl][np.argmax(x[sl] >= g - 0.3):]).max() if (x[sl] >= g - 0.3).any() else np.nan) if up else (lambda x: 0)
        print(f"  t={tg[c]:5.0f} ->{g:.0f}  real over {f(Tm):+.1f} under {fm(Tm):+.1f}   sim over {f(temp):+.1f} under {fm(temp):+.1f}")
