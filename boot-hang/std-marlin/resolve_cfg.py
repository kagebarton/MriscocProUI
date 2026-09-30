#!/usr/bin/env python3
"""Resolve KTOrigOct2025 -> upstream Marlin config merge conflicts, then port
current (MriscocProUI KT-Sep-2026) hardware values.  Usage: resolve_cfg.py FILE"""
import re, sys

path = sys.argv[1]
src = open(path).read().split('\n')

def setdef(text, name, value):
  pat = re.compile(r'^(\s*)(#define\s+' + name + r')\b(\s+)?(.*?)(\s*//.*)?$')
  out, hits = [], 0
  for line in text.split('\n'):
    m = pat.match(line)
    if m:
      hits += 1
      line = f"{m.group(1)}{m.group(2)} {value}" + (f" {m.group(5).strip()}" if m.group(5) else '')
    out.append(line)
  if not hits: raise SystemExit(f"{path}: {name} not found")
  return '\n'.join(out)

def enable(text, name):
  n = 0
  def f(m):
    nonlocal n; n += 1
    return m.group(1) + '#define ' + name + m.group(2)
  text = re.sub(r'^(\s*)//\s*#define ' + name + r'\b(.*)$', f, text, flags=re.M)
  if not n and not re.search(r'^\s*#define ' + name + r'\b', text, flags=re.M):
    raise SystemExit(f"{path}: cannot enable {name}")
  return text

# Handlers keyed by a marker in the user's ("ours") side; each gets upstream's side.
handlers = [
  ('DEFAULT_Kp',            lambda t: setdef(setdef(setdef(t, 'DEFAULT_KP', '13.19'), 'DEFAULT_KI', '0.77'), 'DEFAULT_KD', '56.05')),
  ('DEFAULT_bedKp',         lambda t: setdef(setdef(setdef(t, 'DEFAULT_BED_KP', '54.26'), 'DEFAULT_BED_KI', '10.60'), 'DEFAULT_BED_KD', '185.22')),
  ('S_CURVE_ACCELERATION',  lambda t: enable(t, 'S_CURVE_ACCELERATION')),
  ('STRING_CONFIG_H_AUTHOR',lambda t: t),
  ('NOZZLE_TO_PROBE_OFFSET',lambda t: setdef(t, 'NOZZLE_TO_PROBE_OFFSET', '{ 4.5, 26.5, -2.77 }')),
  ('GRID_MAX_POINTS_X 7',   lambda t: setdef(setdef(t, 'MESH_INSET', '25'), 'GRID_MAX_POINTS_X', '7')),   # UBL
  ('GRID_MAX_POINTS_X 5',   lambda t: setdef(setdef(t, 'MESH_INSET', '10'), 'GRID_MAX_POINTS_X', '5')),   # MBL
  ('SHOW_CUSTOM_BOOTSCREEN',lambda t: t),
  ('SDSORT_LIMIT',          lambda t: setdef(setdef(setdef(setdef(t, 'SDSORT_QUICK', 'true'), 'SDSORT_LIMIT', '10'), 'SDSORT_GCODE', 'true'), 'SDSORT_USES_STACK', 'true')),
  ('LIN_ADVANCE',           lambda t: enable(t, 'LIN_ADVANCE')),
  ('ARC_P_CIRCLES',         lambda t: enable(t, 'ARC_P_CIRCLES')),
]

out, i, n = [], 0, 0
while i < len(src):
  if src[i].startswith('<<<<<<< '):
    j = src.index('=======', i); k = next(x for x in range(j, len(src)) if src[x].startswith('>>>>>>> '))
    ours, theirs = '\n'.join(src[i+1:j]), '\n'.join(src[j+1:k])
    for key, fn in handlers:
      if key in ours: out.append(fn(theirs)); break
    else: raise SystemExit(f"{path}: unhandled conflict at line {i+1}:\n{ours}")
    i, n = k + 1, n + 1
  else:
    out.append(src[i]); i += 1
text = '\n'.join(out)

# Hardware values that changed since Oct 2025 (from the current KT-Sep-2026 config)
if path.endswith('Configuration.h'):
  for name, val in [
    ('TEMP_SENSOR_0', '11'),
    ('DEFAULT_AXIS_STEPS_PER_UNIT', '{ 80, 80, 400, 702 }'),
    ('DEFAULT_ACCELERATION', '800'), ('DEFAULT_RETRACT_ACCELERATION', '800'), ('DEFAULT_TRAVEL_ACCELERATION', '1000'),
    ('MPC_HEATER_POWER', '{ 53.0f }'), ('MPC_BLOCK_HEAT_CAPACITY', '{ 16.95f }'),
    ('MPC_SENSOR_RESPONSIVENESS', '{ 0.2673f }'), ('MPC_AMBIENT_XFER_COEFF', '{ 0.0654f }'),
    ('MPC_AMBIENT_XFER_COEFF_FAN255', '{ 0.1018f }'), ('FILAMENT_HEAT_CAPACITY_PERMM', '{ 3.5e-3f }'),
    ('MPC_SMOOTHING_FACTOR', '0.25f'), ('MPC_STEADYSTATE', '1.0f'), ('MPC_TUNING_POS', '{ X_CENTER, Y_CENTER, 0.1f }'),
    ('Y_MAX_POS', 'Y_BED_SIZE +10'),
    ('NOZZLE_PARK_POINT', '{ 153, 245, 50 }'),
    ('NOZZLE_CLEAN_STROKES', '5'),
    ('NOZZLE_CLEAN_START_POINT', '{ { 177, 242, (Z_MIN_POS + 1) } }'),
    ('NOZZLE_CLEAN_END_POINT', '{ { 153, 242, (Z_MIN_POS + 1) } }'),
  ]: text = setdef(text, name, val)
else:
  for name, val in [
    ('X_CURRENT', '900'), ('Y_CURRENT', '1000'), ('Z_CURRENT', '700'), ('E0_CURRENT', '800'),
    ('SHAPING_FREQ_X', '48.40'), ('SHAPING_FREQ_Y', '44.40'), ('SHAPING_ZETA_X', '0.20'), ('SHAPING_ZETA_Y', '0.10'),
    ('ENCODER_10X_STEPS_PER_SEC', '70'), ('ENCODER_100X_STEPS_PER_SEC', '110'),
  ]: text = setdef(text, name, val)

open(path, 'w').write(text)
print(f"{path}: {n} conflicts resolved")
