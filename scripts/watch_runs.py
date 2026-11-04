"""Prints one line per new games/positions pass result, failed request, final answer or warning, across runs."""
import glob
import json
import os
import sys
import time

STATE = "/tmp/autorasp_watch_state.json"  # remembers what was already printed across restarts
seen = json.load(open(STATE)) if os.path.exists(STATE) else {}
runs = sys.argv[1:] or sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "runs", "opus55_*")))
while True:
    for r in runs:
        name = os.path.basename(r)
        for path, kind in ((os.path.join(r, "tool_calls.jsonl"), "calls"), (os.path.join(r, "loop.log"), "log")):
            if not os.path.exists(path):
                continue
            lines = open(path).read().splitlines()
            start = seen.get(path, 0)
            for line in lines[start:]:
                if kind == "calls":
                    e = json.loads(line)
                    if e["kind"] == "games":
                        res = e["result"]
                        if res.get("ok"):
                            sc = {o: round(v["score"], 2) for o, v in res["per_opponent"].items()}
                            print(f"{name} pass {res['pass']} games {sc} net {res['network']['layers']}L "
                                  f"{res['network']['residual_dims']}D {res.get('seconds_per_1000_positions')}s/1k",
                                  flush=True)
                        else:
                            print(f"{name} games FAILED: {str(res.get('error'))[:200]!r}", flush=True)
                    elif e["kind"] == "positions":
                        res = e["result"]
                        print(f"{name} positions pass {res.get('pass', '-')} ok={res.get('ok')}", flush=True)
                elif any(w in line for w in ("final", "WARNING", "failed", "stopped", "Traceback")):
                    print(f"{name} | {line[:300]}", flush=True)
            seen[path] = len(lines)
    json.dump(seen, open(STATE, "w"))
    if all(os.path.exists(os.path.join(r, "final", "compile.json")) for r in runs):
        print("ALL RUNS FINISHED", flush=True)
        break
    time.sleep(20)
