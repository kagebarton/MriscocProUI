import asyncio, json, sys, time, pathlib, requests, websockets
URL = "http://192.168.1.3:5000"
H = {"X-Api-Key": pathlib.Path.home().joinpath("Downloads/octo.txt").read_text().strip()}
baud, secs = int(sys.argv[1]), float(sys.argv[2])
def get(p):
    try: return requests.get(URL+p, headers=H, timeout=15).json()
    except Exception as e: return {"err": repr(e)[:80]}
async def main():
    c = get("/api/connection").get("current", {})
    print("before:", c.get("state"), c.get("baudrate"))
    if c.get("state") not in ("Closed", "Offline", None) and not str(c.get("state")).startswith("Error"):
        requests.post(URL+"/api/connection", headers=H, json={"command":"disconnect"}, timeout=15); time.sleep(2)
    lg = requests.post(URL+"/api/login", headers=H, json={"passive": True}, timeout=15).json()
    async with websockets.connect(URL.replace("http","ws")+"/sockjs/websocket", max_size=None) as ws:
        await ws.send(json.dumps({"auth": f"{lg['name']}:{lg['session']}"}))
        await asyncio.sleep(0.5)
        r = requests.post(URL+"/api/connection", headers=H, json={"command":"connect","port":"/dev/ttyOcto4a","baudrate":baud,"autoconnect":False}, timeout=15)
        print("connect POST:", r.status_code, "baud", baud)
        end = time.time() + secs; last = None
        while time.time() < end:
            try: m = json.loads(await asyncio.wait_for(ws.recv(), timeout=max(0.1, end-time.time())))
            except asyncio.TimeoutError: break
            cur = m.get("current") or {}
            st = (cur.get("state") or {}).get("text")
            if st and st != last: print(f"[{secs-(end-time.time()):5.1f}s] STATE:", st); last = st
            for line in cur.get("logs", []): print(line)
asyncio.run(main())
