# Score controller settings in the closed-loop sim on the two plant fits (worst case of the two).
# Test: cold start to 240 at t=2 s, 240 -> 220 at 400 s, 220 -> 240 at 550 s.
# Metrics: [cold M109 release (3 s residency) after passing 200 C, cold max over 240,
#           up-step M109 release, up-step max over 240, down-step undershoot below 220]
#
#   sweep.py                  joint grid over C, M, K, D, R; prints the best settings within the caps
#   sweep.py C M K D [R]      scores one setting, e.g. sweep.py 16 2 0.05 5.5
#
# The sim reads overshoot 0.6-1.3 K low against the printer. The caps below (1.5 K cold, 1.0 K step)
# leave room for that under the real 2 K cap. Use it to rank settings, then verify on the printer.
import sys, itertools, numpy as np
from common import DT, fit_path, m109
from closedloop import run

t = np.arange(0, 800, DT); g = np.zeros_like(t); g[t >= 2] = 240; g[t >= 400] = 220; g[t >= 550] = 240
ds = np.full(len(t), -1.0)
plants = [np.load(fit_path(f)) for f in ("p6_L3.0.npy", "p6_L2.0.npy")]

def metr(temp):
    c = t[np.argmax(temp >= 200)]; w = (t >= c) & (t < 380)
    up = (t >= 550) & (t < 700); dn = (t >= 400) & (t < 550)
    return np.array([m109(t[w] - c, temp[w], 3.0, 240), temp[w].max() - 240, m109(t[up] - 550, temp[up], 3.0, 240), temp[up].max() - 240, 220 - temp[dn].min()])

def evalc(C, M, K, D, R=0.2673, A=0.0654):
    ms = np.array([metr(run(pb[1:12], int(pb[0]), np.array([C, R, A, D, 0.25, 1.0, 1.0]), g, 23.0, 23.0, 1, 0.2, 23.0, 23.0, ds, M, K)[0]) for pb in plants])
    return ms.max(axis=0)

HDR = "[cold M109 (3 s), cold max, up M109 (3 s), up max, down under]"
if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(sys.argv[1:], np.round(evalc(*map(float, sys.argv[1:])), 1), HDR); sys.exit()
    print("saved C16 M2 K0.05 D5.5 R.2673:", np.round(evalc(16, 2, 0.05, 5.5), 1), HDR)
    res = []
    for C, M, K, D, R in itertools.product((13, 14, 15, 16, 17, 18, 19), (0, 1, 2, 3, 4), (0.05, 0.1, 0.15, 0.2, 0.3), (3, 3.5, 4, 4.5, 5, 5.5, 6, 7), (0.2673, 0.35, 0.45)):
        if M == 0 and K != 0.05: continue
        res.append(((C, M, K, D, R), evalc(C, M, K, D, R)))
    ok = [(k, v) for k, v in res if v[1] <= 1.5 and v[3] <= 1.0 and v[4] <= 1.0 and not np.isnan(v[0])]
    ok.sort(key=lambda kv: kv[1][0] + 0.2 * kv[1][2])
    print(f"{len(ok)} of {len(res)} within caps (sim cold max <= 1.5, step max <= 1.0)", HDR)
    for k, v in ok[:30]: print(k, np.round(v, 1))
