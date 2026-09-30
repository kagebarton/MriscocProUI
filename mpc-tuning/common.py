# Shared constants, paths and log parsing for the MPC tuning tools
import os, re, pathlib, numpy as np

HERE = pathlib.Path(__file__).resolve().parent
LOGS, FITS, SEQS = HERE / "logs", HERE / "fits", HERE / "seqs"

# OctoPrint connection. The API key is read from a file so it never appears in a command line or log.
OCTO_URL = os.environ.get("OCTOPRINT_URL", "http://192.168.1.3:5000")
OCTO_KEY_FILE = pathlib.Path(os.environ.get("OCTOPRINT_KEY_FILE", pathlib.Path.home() / "Downloads/octo.txt"))
def octo_headers(): return {"X-Api-Key": OCTO_KEY_FILE.read_text().strip()}
P = 53.0      # (W) heater power, M306 P
DT = 0.08     # (s) plant simulation step, half of the firmware's MPC_dT
MDT = 0.16    # (s) MPC_dT on this board

TEMP_RE = re.compile(r"T:([\d.]+) /([\d.]+) .*? @:(\d+) B@")

def log_path(fn):
    """A log given by bare name is looked up in logs/."""
    p = pathlib.Path(fn)
    return p if p.exists() else LOGS / p.name

def fit_path(fn):
    p = pathlib.Path(fn)
    return p if p.exists() or p.parent != pathlib.Path(".") else FITS / p.name

def load(fn):
    """Temperature reports from a log as rows of (t from first report, T, target, soft PWM 0..127)."""
    rows = []
    for ln in open(log_path(fn)):
        t, s = ln.rstrip().split("\t", 1)
        m = TEMP_RE.search(s)
        if m and "Recv" in s: rows.append((float(t), float(m[1]), float(m[2]), int(m[3])))
    a = np.array(rows); a[:, 0] -= a[0, 0]
    return a

def grid(a, tend=None):
    """Resample the reported PWM onto the plant step grid (zero-order hold)."""
    tend = tend or a[-1, 0]
    tg = np.arange(0, tend, DT)
    idx = np.searchsorted(a[:, 0], tg, side="right") - 1
    u = a[np.clip(idx, 0, None), 3] / 127.0
    return tg, u

def m109(tt, y, res, tgt=240.0, win=1.0, hyst=3.0):
    """When M109 would release: TEMP_WINDOW win, TEMP_HYSTERESIS hyst, TEMP_RESIDENCY_TIME res."""
    r = None
    for t, v in zip(tt, y):
        d = abs(tgt - v)
        if r is None:
            if d < win: r = t
        elif d > hyst: r = t
        if r is not None and t - r >= res: return t
    return np.nan
