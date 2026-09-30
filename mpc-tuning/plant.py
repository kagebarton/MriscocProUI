# Physical model of the Volcano hotend ("p6"), fitted by fit_plant.py:
#   heater node h -> block b <-> slow side mass m, block -> sensor s (first-order lag tau),
#   loss from b to an environment node e (air and duct around the block), which leaks ke to the room.
#   Heater input reaches h after d plant steps of DT. Heat capacities scale with 1 + beta*(b-150)/100,
#   and the loss with 1 + gam*(b-200)/100.
# p = Ch, Cb, khb, A, tau, Cm, kbm, beta, gam, Ce, ke. Saved fits are [d, *p, e0, m0] (see fit_plant.py).
import numpy as np, numba
from common import P, DT

@numba.njit(cache=True)
def simj(d, p, u, T0, Ta, e0, m0):
    """Open-loop sensor temperature for heater fractions u (0..1) on the DT grid."""
    Ch, Cb, khb, A, tau, Cm, kbm, beta, gam, Ce, ke = p
    n = len(u); h = T0; b = T0; m = m0; s = T0; e = e0; out = np.empty(n)
    for i in range(n):
        ui = u[i - d] if i >= d else 0.0
        cf = 1.0 + beta * (b - 150.0) / 100.0
        qhb = khb * (h - b); qbm = kbm * (b - m)
        loss = A * (b - e) * (1.0 + gam * (b - 200.0) / 100.0)
        h += DT * (P * ui - qhb) / (Ch * cf)
        b += DT * (qhb - qbm - loss) / (Cb * cf)
        m += DT * qbm / (Cm * cf)
        e += DT * (loss - ke * (e - Ta)) / Ce
        s += DT * (b - s) / tau
        out[i] = s
    return out
