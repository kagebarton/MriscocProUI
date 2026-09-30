# Fit the firmware's own model structure to the logs, for dead times D = 1..7 s:
#   heater delayed D -> block C <-> side mass M (coupling K), loss A to an env node, sensor lag R.
# This is the physical answer to "what are D, M and K?". It gave a side mass of ~8-11 J/K, but the values
# that met the M109 goal on the printer were D5.5 M2 K0.05, so treat these as a starting point only.
# Writes fits/side_D<D>.npy = [d, C, M, K, R, A, Ce, ke, e0/m0 per extra run].
import numpy as np, numba
from scipy.optimize import least_squares
from common import load, grid, P, DT, FITS

@numba.njit(cache=True)
def sm(d, C, M, K, R, A, Ce, ke, u, T0, Ta, e0, m0):
    n = len(u); b = T0; m = m0; s = T0; e = e0; out = np.empty(n)
    for i in range(n):
        ui = u[i - d] if i >= d else 0.0
        qbm = K * (b - m); loss = A * (b - e)
        b += DT * (P * ui - qbm - loss) / C
        m += DT * qbm / M
        e += DT * (loss - ke * (e - Ta)) / Ce
        s += DT * (b - s) * R
        out[i] = s
    return out

runs = []
for fn, tend in (("cold1.log", 525), ("steps1.log", None), ("cold_D6.log", None)):
    a = load(fn); tg, u = grid(a, tend or a[-1, 0] - 1)
    T = np.interp(tg, a[:, 0], a[:, 1]); w = np.where(tg > 3, 1.0, 0.0)
    g = a[np.clip(np.searchsorted(a[:, 0], tg, side="right") - 1, 0, None), 2]
    for c in np.nonzero(np.diff(g) != 0)[0]: w[c:c + int(90 / DT)] = 3.0
    w[(T > 195) & (g == 240) & (tg < 250) & (fn != "steps1.log")] = 3.0   # cold-start arrival
    runs.append((u, T, w, a[0, 1]))

def res(p, d):
    C, M, K, R, A, Ce, ke = p[:7]; out = []
    for k, (u, T, w, T0) in enumerate(runs):
        e0 = 23.0 if k == 0 else p[7 + 2 * (k - 1)]; m0 = T0 if k == 0 else p[8 + 2 * (k - 1)]
        out.append(w * (sm(d, C, M, K, R, A, Ce, ke, u, T0, 23.0, e0, m0) - T))
    return np.concatenate(out)

if __name__ == "__main__":
    lo = [3, 0.5, 0.01, 0.02, 0.03, 1, 0.01, 23, 25, 23, 25]; hi = [40, 60, 5, 3, 0.5, 3000, 5, 150, 160, 150, 160]
    seeds = ([7.9, 8.4, 0.46, 0.092, 0.077, 41, 0.40, 44, 54, 30, 32], [10, 7, 0.3, 0.15, 0.07, 60, 0.3, 45, 55, 30, 32], [12, 5, 0.2, 0.25, 0.066, 100, 0.2, 45, 55, 30, 32])
    prev = None
    for D in np.arange(1.0, 7.01, 0.5):
        d = int(round(D / DT)); bl = None
        for p0 in seeds + ((prev,) if prev is not None else ()):
            r = least_squares(res, np.clip(p0, np.array(lo) + 1e-6, np.array(hi) - 1e-6), bounds=(lo, hi), args=(d,), x_scale="jac")
            if bl is None or r.cost < bl.cost: bl = r
        prev = bl.x; e = res(bl.x, d); n0 = 0; per = []
        for (u, T, w, T0) in runs: per.append(np.sqrt(np.mean(e[n0:n0+len(u)]**2))); n0 += len(u)
        print(f"D {D:.1f} wrms {np.sqrt(np.mean(e**2)):.3f} ({' '.join(f'{v:.2f}' for v in per)})  C {bl.x[0]:.2f} M {bl.x[1]:.2f} K {bl.x[2]:.3f} R {bl.x[3]:.3f} A {bl.x[4]:.4f} | Ce {bl.x[5]:.0f} ke {bl.x[6]:.3f}", flush=True)
        np.save(FITS / f"side_D{D:.1f}.npy", np.concatenate([[d], bl.x]))
