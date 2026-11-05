"""Diagnostic replay (not the official score): the same network with sticky actions 0.1 and 0, 200 episodes each.
Usage: python eval/analysis/minatar_no_sticky.py opus|astra asterix|seaquest"""
import sys, json
import numpy as np
sys.path.insert(0, "/home/user/auto-rasp")
from gorasp import minatar as M
who, game = sys.argv[1], sys.argv[2]
pol = (M.TracrMinAtarPolicy(f"/home/user/auto-rasp/runs/opus55_minatar_{game}/final/model.npz") if who == "opus"
       else M.MLPPolicy(f"/home/user/auto-rasp/networks/paper_minatar/{game}/hand.npz"))
out = {}
for sticky in (0.1, 0.0):
    s, l = M.run_episodes(game, pol, 200, seed=2024, batch=100, sticky=sticky)
    out[f"sticky_{sticky}"] = {"mean": round(float(s.mean()), 2), "se": round(float(s.std(ddof=1) / np.sqrt(len(s))), 2),
                               "mean_length": round(float(l.mean()), 1), "cut_at_10000": int((l >= 10000).sum())}
print(who, game, json.dumps(out), flush=True)
