# Usage: octo_seq.py OUTFILE STEP ...   STEP = "cmd;wait" or @file (one step per line, # comments)
#   wait = seconds, or "ok" to wait for that command's ok (M109, M190, G28)
# Sends each command through OctoPrint and appends every terminal line to OUTFILE with a timestamp,
# plus #STEP / #DONE / #END marks. While waiting on seconds after M155 or an "ok" step, M105 is polled 3x/s.
import asyncio, json, pathlib, sys, time, requests, websockets
from common import OCTO_URL as URL, octo_headers, SEQS
H = octo_headers()
out = sys.argv[1]; steps = []
for a in sys.argv[2:]:
    if a.startswith("@"):
        p = pathlib.Path(a[1:]); p = p if p.exists() else SEQS / p.name
        steps += [ln.strip() for ln in open(p) if ln.strip() and not ln.lstrip().startswith("#")]
    else: steps.append(a)
def send(c): requests.post(URL+"/api/printer/command", headers=H, json={"command": c}, timeout=10)
async def main():
    lg = requests.post(URL+"/api/login", headers=H, json={"passive": True}, timeout=15).json()
    async with websockets.connect(URL.replace("http","ws")+"/sockjs/websocket", max_size=None) as ws:
        await ws.send(json.dumps({"auth": f"{lg['name']}:{lg['session']}"}))
        f = open(out, "a", buffering=1); loop = asyncio.get_running_loop()
        state = {"oks": 0, "sent": None, "ok_after": 0}
        async def reader():
            while True:
                m = json.loads(await ws.recv())
                for line in (m.get("current") or {}).get("logs", []):
                    f.write(f"{time.time():.3f}\t{line}\n")
                    if state["sent"] and line.startswith("Send: " + state["sent"]): state["ok_after"] = 0; state["seen"] = True
                    if line.startswith("Recv: ok"):
                        state["oks"] += 1
                        if state.get("seen"): state["ok_after"] += 1
        async def poller():
            while True:
                await loop.run_in_executor(None, send, "M105"); await asyncio.sleep(0.33)
        rt = asyncio.create_task(reader()); pt = None
        for s in steps:
            cmd, wait = s.split(";")
            f.write(f"{time.time():.3f}\t#STEP {cmd}\n")
            if wait == "ok":
                if pt: pt.cancel(); pt = None
                await asyncio.sleep(1)
                state["sent"] = cmd; state["seen"] = False; state["ok_after"] = 0
                await loop.run_in_executor(None, send, cmd)
                # M109 blocks the queue; wait for the first ok after OctoPrint logs "Send: <cmd>"
                while not (state["seen"] and state["ok_after"] > 0): await asyncio.sleep(0.1)
                state["sent"] = None; state["seen"] = False
                f.write(f"{time.time():.3f}\t#DONE {cmd}\n")
                pt = asyncio.create_task(poller())
            else:
                await loop.run_in_executor(None, send, cmd)
                if pt is None and cmd.startswith("M155"): pt = asyncio.create_task(poller())
                await asyncio.sleep(float(wait))
        f.write(f"{time.time():.3f}\t#END\n")
        rt.cancel()
asyncio.run(main())
