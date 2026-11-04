"""Checks our Go engine, input encoding and sampling against numbers published with the paper:
head-to-heads of Astra's written networks against the same-size PPO networks (2,000 games each,
exp6_go_from_scratch/eval/ppo_same_size/ppo_big_eval/h2h_lr_scan.json)."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gorasp import policies as P, play as G  # noqa: E402

NET = os.path.join(os.path.dirname(__file__), "..", "networks", "paper")
PAPER = {  # written network's score, as Black, as White
    ("budget_0", "ppo_same_size_lr3e-5_s0"): (0.4255, 0.3110, 0.5400),
    ("budget_0", "ppo_same_size_lr3e-5_s1"): (0.2630, 0.1460, 0.3800),
    ("budget_50", "ppo_same_size_lr3e-5_s0"): (0.7415, 0.7050, 0.7780),
    ("budget_50", "ppo_same_size_lr3e-5_s2"): (0.7855, 0.8080, 0.7630),
}
n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
out = {}
for (a, b), ref in PAPER.items():
    t = time.time()
    s = G.summary(G.play(P.MLPPolicy(os.path.join(NET, a)), P.MLPPolicy(os.path.join(NET, b)), n, seed=31337))
    se = (ref[0] * (1 - ref[0]) / n) ** 0.5
    out[f"{a}_vs_{b}"] = {"ours": s, "paper": ref, "diff": s["score"] - ref[0], "se": se}
    print(f"{a} vs {b}: ours {s['score']:.4f} (B {s['score_as_black']:.3f} W {s['score_as_white']:.3f}) "
          f"paper {ref[0]:.4f} (B {ref[1]:.3f} W {ref[2]:.3f})  diff {s['score'] - ref[0]:+.4f} "
          f"(1 s.e. per run {se:.4f})  len {s['mean_length']:.1f}  [{time.time() - t:.0f}s]", flush=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "results"), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "validate_engine.json"), "w"), indent=1)
