#!/bin/bash
# octo_send.sh "G1" "M2" ...  -- queue commands via OctoPrint; prints the HTTP status (204 = queued)
URL=${OCTOPRINT_URL:-http://192.168.1.3:5000}
K=$(cat "${OCTOPRINT_KEY_FILE:-$HOME/Downloads/octo.txt}")
for c in "$@"; do curl -s -o /dev/null -w "%{http_code} $c\n" -H "X-Api-Key: $K" -H 'Content-Type: application/json' -d "{\"command\":\"$c\"}" "$URL/api/printer/command"; done
