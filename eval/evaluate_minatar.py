"""Experiment 5 scoring: mean score over 1,000 episodes of MinAtar 1.0.15 (sticky actions 0.1, difficulty
ramping, actions sampled from the softmax of the logits, episodes cut at 10,000 steps).

    python eval/evaluate_minatar.py --run runs/opus55_minatar_breakout       # the run's compiled RASP program
    python eval/evaluate_minatar.py --mlp <hand.npz> --game breakout --name astra_minatar_breakout
"""
import argparse
import json
import os
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from gorasp import minatar as M  # noqa: E402

PAPER = os.path.join(REPO, "results", "minatar_paper_eval.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--mlp")
    ap.add_argument("--game")
    ap.add_argument("--name")
    ap.add_argument("--episodes", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=12345)
    args = ap.parse_args()
    out = {"episodes_requested": args.episodes, "seed": args.seed}
    if args.run:
        run_dir = os.path.abspath(args.run)
        cfg = json.load(open(os.path.join(run_dir, "config.json")))
        game = cfg["game"]
        name = args.name or os.path.basename(run_dir.rstrip("/"))
        comp = json.load(open(os.path.join(run_dir, "final", "compile.json")))
        out["compile"] = comp
        if comp.get("ok"):
            pol = M.TracrMinAtarPolicy(os.path.join(run_dir, "final", "model.npz"))
            out["subject"] = "tracr"
        else:
            pol = M.ZeroPolicy()
            out["subject"] = "zero network (the reply's program did not compile)"
    else:
        game, name = args.game, args.name
        pol, out["subject"] = M.MLPPolicy(args.mlp), "mlp"
    out["game"] = game
    t0 = time.time()

    def progress(start, t, alive):
        print(f"  [{name}] episodes {start}+: step {t + 1}, {alive} still playing, {time.time() - t0:.0f}s",
              flush=True)

    s, l = M.run_episodes(game, pol, args.episodes, seed=args.seed, batch=args.batch, progress=progress)
    out.update(M.summarize(s, l))
    out["seconds"] = round(time.time() - t0, 1)
    if hasattr(pol, "forward_positions"):
        out["distinct_observations_run"] = pol.forward_positions
    out["scores"] = s.tolist()
    out["lengths"] = l.tolist()
    if os.path.exists(PAPER):
        out["paper"] = json.load(open(PAPER)).get(game)
    d = os.path.join(REPO, "results", name)
    os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, "eval.json"), "w"), indent=1)
    print(f"{name} ({game}): mean {out['mean']:.2f} ± {out['se']:.2f} over {out['episodes']} episodes, "
          f"mean length {out['mean_length']:.0f}, {out['seconds']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
