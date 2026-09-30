# Closed loop: an exact port of get_pid_output_hotend() (MPC with MPC_DEADTIME and MPC_SIDE_MASS)
# driving the fitted plant from plant.py, with sensor noise. The controller runs every MPC_dT (two plant steps).
#
# run(pp, d, ctl, targets, T0, Ta, seed, noise, e0, m0, dsched, SMM, SMK) -> (sensor temps, PWM) on the DT grid
#   pp, d:   plant params and heater delay steps, from a fits/p6_*.npy as pb[1:12], int(pb[0])
#   ctl:     controller C, R, A, D, smoothing factor, MPC_STEADYSTATE, MPC_MIN_AMBIENT_CHANGE
#   targets: target per plant step (0 = off)
#   dsched:  D per plant step to switch dead time mid-run, or -1 to keep it
#   SMM/SMK: side mass M (0 = off) and K
import numpy as np, numba
from common import P, DT, MDT
NS = int(8.0 / MDT) + 1   # MPC_DEADTIME_SAMPLES

@numba.njit(cache=True)
def run(pp, d, ctl, targets, T0, Ta, seed, noise, e0, m0, dsched, SMM, SMK):
    Ch, Cb, khb, A_, tau, Cm, kbm, beta, gam, Ce, ke = pp
    C, R, A, D, SM, SS, MINAMB = ctl
    np.random.seed(seed)
    n = len(targets); h = T0; b = T0; m = m0; s = T0; e = e0
    temp = np.empty(n); pwmo = np.empty(n)
    hist = np.zeros(NS, np.int64); hi = 0
    mb = T0; ms = T0; mside = T0; ma = min(30.0, T0); init = False; pwm = 0; celsius = T0
    dsteps = min(int(max(D, 0.0) / MDT + 0.5), NS - 1)
    for i in range(n):
        if i % 2 == 0:
            celsius = s + noise * np.random.randn()
            tgt = targets[i]
            if dsched[i] >= 0: dsteps = min(int(dsched[i] / MDT + 0.5), NS - 1)
            if not init:
                ma = min(30.0, celsius); mb = celsius; ms = celsius; mside = celsius
                for k in range(NS): hist[k] = pwm
                init = True
            hi = (hi + 1) % NS; hist[hi] = pwm
            inflight = 0
            for k in range(dsteps): inflight += hist[(hi + NS - k) % NS]
            mpwm = hist[(hi + NS - dsteps) % NS]
            sflow = (mb - mside) * SMK if SMM > 0 else 0.0
            btd = mpwm * P * (MDT / 127) / C + (ma - mb) * A * MDT / C - sflow * MDT / C
            if SMM > 0: mside += sflow * MDT / SMM
            mb += btd
            ms += (mb - ms) * (R * MDT)
            dta = (celsius - ms) * SM
            mb += dta; ms += dta
            if (pwm >= 1 and pwm <= 126) or abs(btd + dta) < SS * MDT:
                ma += max(dta, MINAMB * MDT) if dta > 0 else min(dta, -MINAMB * MDT)
            pb = mb + (inflight * P * (MDT / 127) + (ma - mb) * A * (dsteps * MDT) - sflow * (dsteps * MDT)) / C
            power = 0.0
            if tgt != 0:
                power = (tgt - pb) * C * 0.5 - (ma - pb) * A + ((pb - mside) * SMK if SMM > 0 else 0.0)
            out = power * 254.0 / P + 1.0
            out = min(max(out, 0.0), 255.0)
            pwm = int(out) >> 1
        # Plant: the heater command reaches it after d plant steps
        temp[i] = s; pwmo[i] = pwm
        u_del = pwmo[i - d] / 127.0 if i >= d else 0.0
        cf = 1.0 + beta * (b - 150.0) / 100.0
        qhb = khb * (h - b); qbm = kbm * (b - m)
        loss = A_ * (b - e) * (1.0 + gam * (b - 200.0) / 100.0)
        h += DT * (P * u_del - qhb) / (Ch * cf)
        b += DT * (qhb - qbm - loss) / (Cb * cf)
        m += DT * qbm / (Cm * cf)
        e += DT * (loss - ke * (e - Ta)) / Ce
        s += DT * (b - s) / tau
    return temp, pwmo
