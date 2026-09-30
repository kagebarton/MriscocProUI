#!/bin/bash
# octo_waitcold.sh THRESH OUTFILE STEP ...  -- wait for the nozzle to drop below THRESH C, then run octo_seq.py
URL=${OCTOPRINT_URL:-http://192.168.1.3:5000}
K=$(cat "${OCTOPRINT_KEY_FILE:-$HOME/Downloads/octo.txt}"); th=$1; shift
while :; do
  T=$(curl -s -m 5 -H "X-Api-Key: $K" "$URL/api/printer" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['temperature']['tool0']['actual'])" 2>/dev/null)
  echo "$(date +%T) $T"; [ -n "$T" ] && python3 -c "import sys; sys.exit(0 if $T < $th else 1)" && break
  sleep 30
done
exec python3 "$(dirname "$0")/octo_seq.py" "$@"
