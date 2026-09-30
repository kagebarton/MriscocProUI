# Fit the physical plant (plant.py) to the open-loop-ish logs, for pure heater delays L = 0..5 s.
# Writes fits/p6_L<L>.npy = [d, Ch, Cb, khb, A, tau, Cm, kbm, beta, gam, Ce, ke, e0, m0].
# Inputs: logs/cold1.log (cold start and holds) and logs/steps1.log (220 <-> 240 steps at D3/4.5/6),
# both from the D-only firmware. The closed-loop tools use the L2.0 and L3.0 fits.
import numpy as np
from scipy.optimize import least_squares
from common import load, grid, DT, FITS
from plant import simj

sets = []
for fn, tend, win in (("cold1.log", 525, ((80, 180), (226, 300), (376, 430))), ("steps1.log", None, None)):
    a = load(fn); tg, u = grid(a, tend or a[-1, 0] - 1)
    T = np.interp(tg, a[:, 0], a[:, 1]); w = np.where(tg > 3, 1.0, 0.0)
    if win:
        for lo_, hi_ in win: w[(tg >= lo_) & (tg < hi_)] = 3.0
    else:
        g = a[np.clip(np.searchsorted(a[:, 0], tg, side="right") - 1, 0, None), 2]
        for c in np.nonzero(np.diff(g) != 0)[0]: w[c:c + int(90 / DT)] = 3.0
    sets.append((u, T, w, a[0, 1]))

# Extra params: env and side-mass start temperatures for steps1 (cold1 starts fully at ambient)
def unpack(p): return np.asarray(p[:11]), p[11], p[12]
def res(p, d):
    pp, e0, m0 = unpack(p); out = []
    for k, (u, T, w, T0) in enumerate(sets):
        out.append(w * (simj(d, pp, u, T0, 23.0, 23.0 if k == 0 else e0, T0 if k == 0 else m0) - T))
    return np.concatenate(out)

if __name__ == "__main__":
    lo = [0.2, 1, 0.05, 0.03, 0.3, 0.2, 0.0, -0.5, -0.5, 1, 0.01, 23, 30]; hi = [25, 30, 20, 0.5, 15, 40, 5, 0.8, 1.5, 2000, 5, 120, 150]
    for L in np.arange(0, 5.01, 1.0):
        d = int(round(L / DT)); bl = None
        for p0 in ([3, 12, 1, 0.1, 4, 5, 0.3, 0, 0, 100, 0.2, 40, 60], [2.5, 1, 0.1, 0.1, 2.5, 8, 0.11, -0.04, -0.2, 300, 0.1, 50, 60], [0.5, 14, 5, 0.1, 4, 2, 0.03, 0, 0, 50, 0.3, 45, 60], [6, 2, 0.4, 0.08, 3, 3, 0.04, 0, 0, 500, 0.1, 50, 58]):
            r = least_squares(res, p0, bounds=(lo, hi), args=(d,), x_scale="jac")
            if bl is None or r.cost < bl.cost: bl = r
        e = res(bl.x, d); print(f"L {L:.1f} wrms {np.sqrt(np.mean(e**2)):.3f}", " ".join(f"{v:.4g}" for v in bl.x), flush=True)
        np.save(FITS / f"p6_L{L:.1f}.npy", np.concatenate([[d], bl.x]))
