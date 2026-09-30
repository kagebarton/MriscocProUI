# Replay M306 T (MPC_autotune) against the fitted plants: the stock flow, and the flow that keeps a tuned
# dead-time/side-mass model, with and without the longer settle. Reports the A each would measure against
# the plant's steady-state A, and whether the hold would trip the firmware's 15 K abort window.
import sys, numpy as np
from common import P, DT, MDT, fit_path
NS = int(8.0 / MDT) + 1

class Plant:
    def __init__(s, pb, T0=23.0, Ta=23.0, noise=0.2, seed=1):
        s.d = int(pb[0]); (s.Ch, s.Cb, s.khb, s.A, s.tau, s.Cm, s.kbm, s.beta, s.gam, s.Ce, s.ke) = pb[1:12]
        s.h = s.b = s.m = s.s = T0; s.e = Ta; s.Ta = Ta; s.u = [0.0] * (s.d + 1); s.noise = noise
        s.rng = np.random.default_rng(seed)
    def step(s, pwm):  # one plant step of DT with heater command pwm (0..127)
        s.u.append(pwm / 127.0); ud = s.u.pop(0)
        cf = 1.0 + s.beta * (s.b - 150.0) / 100.0
        qhb = s.khb * (s.h - s.b); qbm = s.kbm * (s.b - s.m)
        loss = s.A * (s.b - s.e) * (1.0 + s.gam * (s.b - 200.0) / 100.0)
        s.h += DT * (P * ud - qhb) / (s.Ch * cf)
        s.b += DT * (qhb - qbm - loss) / (s.Cb * cf)
        s.m += DT * qbm / (s.Cm * cf)
        s.e += DT * (loss - s.ke * (s.e - s.Ta)) / s.Ce
        s.s += DT * (s.b - s.s) / s.tau
    def read(s): return s.s + s.noise * s.rng.standard_normal()

class MPC:  # get_pid_output_hotend() with MPC_DEADTIME and MPC_SIDE_MASS
    def __init__(s, C, R, A, D, M, K, SM=0.25, SS=1.0, MINAMB=1.0):
        s.C, s.R, s.A, s.D, s.M, s.K, s.SM, s.SS, s.MINAMB = C, R, A, D, M, K, SM, SS, MINAMB
        s.hist = [0] * NS; s.hi = 0
    def reset(s, T, Ta):
        s.mb = s.ms = s.mside = T; s.ma = Ta; s.hist = [0] * NS
    def out(s, celsius, tgt, pwm):
        ds = min(int(max(s.D, 0) / MDT + 0.5), NS - 1)
        s.hi = (s.hi + 1) % NS; s.hist[s.hi] = pwm
        inflight = sum(s.hist[(s.hi + NS - k) % NS] for k in range(ds))
        mpwm = s.hist[(s.hi + NS - ds) % NS]
        sflow = (s.mb - s.mside) * s.K if s.M > 0 else 0.0
        btd = mpwm * P * (MDT / 127) / s.C + ((s.ma - s.mb) * s.A - sflow) * MDT / s.C
        s.mb += btd
        if s.M > 0: s.mside += sflow * MDT / s.M
        else: s.mside = s.mb
        s.ms += (s.mb - s.ms) * (s.R * MDT)
        dta = (celsius - s.ms) * s.SM; s.mb += dta; s.ms += dta
        if 1 <= pwm <= 126 or abs(btd + dta) < s.SS * MDT:
            s.ma += max(dta, s.MINAMB * MDT) if dta > 0 else min(dta, -s.MINAMB * MDT)
        pb = s.mb + (inflight * P * (MDT / 127) + ((s.ma - s.mb) * s.A - sflow) * (ds * MDT)) / s.C
        power = 0.0
        if tgt != 0:
            power = (tgt - pb) * s.C * 0.5 - (s.ma - pb) * s.A
            if s.M > 0: power += (pb - s.mside) * s.K
        o = min(max(power * 254.0 / P + 1.0, 0.0), 255.0)
        return int(o) >> 1

def autotune(pb, tuned, keep, extend=True, amb=23.0, seed=1):
    pl = Plant(pb, seed=seed); ctl = MPC(*tuned)
    t = 0.0; cur = pl.read(); log = []
    def tick(pwm, n=2):  # one MPC_dT
        nonlocal t, cur
        for _ in range(n): pl.step(pwm)
        t += MDT; cur = pl.read(); log.append((t, cur, pwm))
    if keep: ctl.reset(cur, amb)
    # measure_heatup: full power; 1 s tests
    t0 = t; nxt = 1.0; samples = [cur] * 3; rate_f = 0.0; cnt = 0; dist = 1; buf = []; t1_time = 0.0
    while True:
        if keep: ctl.out(cur, 200, 127)
        tick(127)
        if t - t0 >= nxt - 1e-9:
            if cur < 100:
                samples = samples[1:] + [cur]; nxt += 1.0
            elif cur < 200:
                if cnt == 16: buf = buf[::2]; cnt //= 2; dist *= 2
                if cnt == 0: t1_time = t - t0
                buf.append(cur); cnt += 1; nxt += 1.0 * dist
            else: break
    elapsed = t - t0
    if cnt % 2 == 0: cnt -= 1
    t1, t2, t3 = buf[0], buf[(cnt - 1) >> 1], buf[cnt - 1]; interval = dist * (cnt >> 1)
    asy = (t2 * t2 - t1 * t3) / (2 * t2 - t1 - t3); resp = -np.log((t2 - asy) / (t1 - asy)) / interval
    A0 = P / (asy - amb); Cfit = A0 / resp
    Rfit = resp / (1 - (amb - asy) * np.exp(-resp * t1_time) / (t1 - asy))
    fitted = asy + (amb - asy) * np.exp(-resp * elapsed)
    if not keep:
        ctl = MPC(Cfit, Rfit, A0, 0.0, 0.0, 0.0); ctl.mb = fitted; ctl.ms = cur; ctl.ma = amb; ctl.mside = fitted
    target = int(fitted)
    # measure_transfer, fan 0 phase only (the plants have no fan term)
    settle = 20.0 + (min(3 * ctl.M / ctl.K, 300.0) if keep and extend and ctl.M > 0 and ctl.K > 0 else 0.0)
    ts = t; E = 0.0; last = cur; pwm = 0; peak = cur; fail = False
    while t - ts < settle + 20.0:
        pwm = ctl.out(cur, target, pwm)
        tick(pwm); peak = max(peak, cur)
        if settle <= t - ts < settle + 20.0: E += P * pwm / 127 * MDT + (last - cur) * ctl.C
        last = cur
        if not (t3 - 15 <= cur <= target + 15): fail = True
    Ameas = E / 20.0 / (target - amb)
    # reference: hold to steady state, A = mean power / (T - amb)
    tr = t; pw = []; tt = []
    while t - tr < 1500:
        pwm = ctl.out(cur, target, pwm); tick(pwm)
        if t - tr > 1200: pw.append(pwm); tt.append(cur)
    Ass = P * np.mean(pw) / 127 / (np.mean(tt) - amb)
    return dict(C=Cfit, R=Rfit, fitted=fitted, target=target, peak=peak - target, Ameas=Ameas, Ass=Ass, fail=fail, settle=settle, log=np.array(log))

if __name__ == "__main__":
    tuned = (16.0, 0.2673, 0.0654, 5.5, 2.0, 0.05)
    for f in ("p6_L3.0.npy", "p6_L2.0.npy"):
        pb = np.load(fit_path(f))
        for name, keep, ext in (("stock flow (D0 M0)", False, False), ("keep, 20 s settle", True, False), ("keep, extended settle", True, True)):
            r = [autotune(pb, tuned, keep, ext, seed=s) for s in (1, 2, 3)]
            print(f"{f} {name:22s} lumped C {np.mean([x['C'] for x in r]):5.2f} R {np.mean([x['R'] for x in r]):.4f}  target {r[0]['target']}"
                  f"  peak {max(x['peak'] for x in r):+.1f}K  fail {any(x['fail'] for x in r)}  settle {r[0]['settle']:.0f}s"
                  f"  A measured {np.mean([x['Ameas'] for x in r]):.4f} (sd {np.std([x['Ameas'] for x in r]):.4f})  steady-state A {np.mean([x['Ass'] for x in r]):.4f}")
