# Usage: octo_log.py OUTFILE SECS [POLL_HZ]  -- timestamped OctoPrint terminal log; optional M105 polling
import asyncio, json, sys, time, requests, websockets
from common import OCTO_URL as URL, octo_headers
H = octo_headers()
out, secs = sys.argv[1], float(sys.argv[2]); hz = float(sys.argv[3]) if len(sys.argv) > 3 else 0
async def poll():
    loop = asyncio.get_running_loop()
    while hz:
        await loop.run_in_executor(None, lambda: requests.post(URL+"/api/printer/command", headers=H, json={"command":"M105"}, timeout=5))
        await asyncio.sleep(1/hz)
async def main():
    lg = requests.post(URL+"/api/login", headers=H, json={"passive": True}, timeout=15).json()
    async with websockets.connect(URL.replace("http","ws")+"/sockjs/websocket", max_size=None) as ws:
        await ws.send(json.dumps({"auth": f"{lg['name']}:{lg['session']}"}))
        t = asyncio.create_task(poll()) if hz else None
        end = time.time() + secs
        with open(out, "a", buffering=1) as f:
            while time.time() < end:
                try: m = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(0.1, end-time.time())))
                except asyncio.TimeoutError: break
                for line in (m.get("current") or {}).get("logs", []): f.write(f"{time.time():.3f}\t{line}\n")
        if t: t.cancel()
asyncio.run(main())
