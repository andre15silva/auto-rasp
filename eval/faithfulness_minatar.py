"""Does the compiled network compute what the RASP program says? On n observations from the network's own games,
compares the compiled logits (indices 100..105) with rasp.evaluate of the same program (run in the sandbox).

    python eval/faithfulness_minatar.py --run runs/opus55_minatar_asterix
"""
import argparse
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from gorasp import minatar as M  # noqa: E402
from harness import sandbox  # noqa: E402


class Recorder:
    def __init__(self, pol):
        self.pol, self.seen = pol, []

    def logits(self, o):
        self.seen.append(np.asarray(o, bool).copy())
        return self.pol.logits(o)


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    p = np.exp(z)
    return p / p.sum(axis=1, keepdims=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--episodes", type=int, default=8)
    args = ap.parse_args()
    run = os.path.abspath(args.run)
    game = json.load(open(os.path.join(run, "config.json")))["game"]
    model = os.path.join(run, "final", "model.npz")
    rec = Recorder(M.TracrMinAtarPolicy(model))
    M.run_episodes(game, rec, args.episodes, seed=777, batch=args.episodes, max_steps=2000)
    obs = np.concatenate(rec.seen)
    obs = obs[np.random.default_rng(0).choice(len(obs), size=min(args.n, len(obs)), replace=False)]
    toks = M.tokens_from_obs6(obs)
    comp = rec.pol.logits(obs).astype(np.float64)
    out = os.path.join(run, "final_faithfulness")
    res = sandbox.compile_in_sandbox(os.path.join(run, "work"), out, rasp_inputs=toks.tolist(), timing=False,
                                     task="minatar")
    r = {"positions": int(len(toks)), **{k: res.get(k) for k in ("rasp_sops", "rasp_sops_failed",
                                                                    "rasp_output_failed", "rasp_first_error",
                                                                    "rasp_seconds")}}
    if res.get("ok") and os.path.exists(os.path.join(out, "rasp.npz")):
        ref = np.load(os.path.join(out, "rasp.npz"))[res["output_label"]][:, 100:106].astype(np.float64)
        ok = ~np.isnan(ref).any(axis=1)
        r["positions_rasp_defined"] = int(ok.sum())
        e = ~np.isnan(ref)  # entry-wise: every (state, action) logit RASP gives a value for
        r["logit_entries_rasp_defined"] = float(e.mean())
        if e.any():
            d = np.abs(comp - ref)[e]
            r["entrywise_max_abs_logit_diff"] = float(d.max())
            r["entrywise_mean_abs_logit_diff"] = float(d.mean())
        if ok.any():
            c, f = comp[ok], ref[ok]
            r["max_abs_logit_diff"] = float(np.abs(c - f).max())
            r["mean_abs_logit_diff"] = float(np.abs(c - f).mean())
            pc, pf = softmax(c), softmax(f)
            r["mean_total_variation"] = float(0.5 * np.abs(pc - pf).sum(axis=1).mean())
            r["argmax_agreement"] = float((c.argmax(1) == f.argmax(1)).mean())
            r["positions_policy_differs_by_tv_over_0.1"] = int((0.5 * np.abs(pc - pf).sum(axis=1) > 0.1).sum())
    else:
        r["error"] = res.get("error", "")[-1500:]
    p = os.path.join(REPO, "results", os.path.basename(run.rstrip("/")), "faithfulness.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(r, open(p, "w"), indent=1)
    print(json.dumps(r))


if __name__ == "__main__":
    main()
