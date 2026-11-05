"""Per-run statistics of the writer runs -> results/run_stats.json (and a printed table)."""
import datetime
import glob
import hashlib
import json
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ts(line):
    m = re.match(r"\[([^\]]+)\]", line)
    return datetime.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S%z") if m else None


out = {}
for d in sorted(glob.glob(os.path.join(REPO, "runs", "opus55_b*"))):
    name = os.path.basename(d)
    st = json.load(open(os.path.join(d, "state.json")))
    log = open(os.path.join(d, "loop.log")).read().splitlines()
    t0, t1 = ts(log[0]), next(ts(l) for l in reversed(log) if ts(l))
    seen, cost, wall, tok, audits = set(), 0.0, 0.0, {"input": 0, "cache_read": 0, "cache_write": 0, "output": 0}, []
    for f in glob.glob(os.path.join(d, "turns", "t*", "run.json")) + glob.glob(os.path.join(d, "turns", "t*", "orig", "run.json")):
        raw = open(f, "rb").read()
        h = hashlib.sha256(raw).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        r = json.loads(raw)
        if "usage" not in r:
            continue
        cost += r.get("cost_usd") or 0
        wall += r.get("wall_s") or 0
        u = r["usage"] or {}
        tok["input"] += u.get("input_tokens", 0)
        tok["cache_read"] += u.get("cache_read_input_tokens", 0)
        tok["cache_write"] += u.get("cache_creation_input_tokens", 0)
        tok["output"] += u.get("output_tokens", 0)
        audits.append(r["audit"]["tool_free"])
    calls = [json.loads(l) for l in open(os.path.join(d, "tool_calls.jsonl"))]
    games = [c["result"] for c in calls if c["kind"] == "games"]
    positions = [c["result"] for c in calls if c["kind"] == "positions"]
    traj = [{"pass": g["pass"], "network_layers": g["network"]["layers"],
             **{o: round(v["score"], 3) for o, v in g["per_opponent"].items()},
             **{f"n_{o}": v["games"] for o, v in g["per_opponent"].items()}} for g in games if g.get("ok")]
    fin = json.load(open(os.path.join(d, "final", "compile.json")))
    out[name] = {
        "budget": st["budget"], "turns": st["turn"], "python_runs": st["runs"], "passes": st["passes"],
        "games_passes": sum(1 for g in games if g.get("ok")), "positions_passes": sum(1 for p in positions if p.get("ok")),
        "failed_pass_requests": sum(1 for x in games + positions if not x.get("ok")),
        "wall_hours": round((t1 - t0).total_seconds() / 3600, 2), "model_wall_hours": round(wall / 3600, 2),
        "model_calls_recorded": len(audits), "all_turns_tool_free": all(audits), "cost_usd": round(cost, 2),
        "tokens": tok, "final_network": fin.get("stats"), "final_mlp_exactness": fin.get("mlp_exactness"),
        "final_seconds_per_1000_positions": fin.get("seconds_per_1000_positions"), "practice_games_passes": traj}
json.dump(out, open(os.path.join(REPO, "results", "run_stats.json"), "w"), indent=1)
for n, s in out.items():
    print(n, {k: v for k, v in s.items() if k not in ("practice_games_passes", "final_network", "tokens")})
    print("   tokens", s["tokens"], "| final", s["final_network"])
    print("   strong-score trajectory:", [p.get("strong") for p in s["practice_games_passes"]])
