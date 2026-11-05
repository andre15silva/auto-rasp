import json, sys, os
import numpy as np
R = "/home/user/auto-rasp"
sys.path.insert(0, R)
from gorasp import minatar as M
from gorasp.tracr_policy import TracrModel
from minatar import Environment

L = "/tmp/claude-0/-home-user-auto-rasp/de2b9d70-6f3e-5db7-b3e0-915adfdce244/scratchpad/ext/lm_understand-logs/exp5_write_from_scratch"
paper = json.load(open(f"{R}/results/minatar_paper_eval.json"))
sticky = json.load(open(f"{R}/results/minatar_sticky_analysis.json"))
data = {"games": {}}
for g in M.GAMES:
    ev = json.load(open(f"{R}/results/opus55_minatar_{g}/eval.json"))
    ea = json.load(open(f"{R}/results/astra_minatar_{g}/eval.json"))
    fa = json.load(open(f"{R}/results/opus55_minatar_{g}/faithfulness.json"))
    run = json.load(open(f"{R}/runs/opus55_minatar_{g}/reply/run.json"))
    comp = json.load(open(f"{R}/runs/opus55_minatar_{g}/final/compile.json"))
    ppo = {k: v for k, v in paper[g].items() if k.startswith("ppo")}
    best = lambda pre: max(((k, v) for k, v in ppo.items() if k.startswith(pre)), key=lambda kv: kv[1]["mean"])
    b100, b500 = best("ppo100"), best("ppo500")
    apply_ = json.load(open(f"{L}/runs/{g}/apply.json"))
    arun = json.load(open(f"{L}/runs/{g}/reply/run.json"))
    # architecture per layer
    tm = TracrModel(f"{R}/runs/opus55_minatar_{g}/final/model.npz")
    layers = []
    for lay in tm.layers:
        hs = lay["heads"]
        layers.append({"heads": len(hs), "static": sum(h["w"] is not None for h in hs),
                       "mlp": int(len(lay["b1"]))})
    groups = tm.sop_layout()
    cat = {k: len(v) for k, v in groups.items() if not (len(v) == 1 and v[0][1] is None)}
    num = [k for k, v in groups.items() if len(v) == 1 and v[0][1] is None]
    inputs = {k: cat[k] for k in ("tokens", "indices") if k in cat}
    prog = open(f"{R}/runs/opus55_minatar_{g}/work/program.py").read()
    ans = open(f"{R}/runs/opus55_minatar_{g}/reply/answer.md").read()
    design = ans.split("```python")[0].strip()
    astra_design = open(f"{L}/runs/{g}/reply/answer.md").read().split("```edits")[0].strip()
    # one real frame under Opus's policy
    pol = M.TracrMinAtarPolicy(f"{R}/runs/opus55_minatar_{g}/final/model.npz")
    env = Environment(g, sticky_action_prob=0.0); env.seed(11); env.reset()
    idx = M.channel_index(g); rng = np.random.default_rng(3)
    stop = {"breakout": 37, "seaquest": 46, "asterix": 64}[g]
    for t in range(stop):
        o = M.obs6(env.state(), idx)[None]
        z = pol.logits(o)[0]; p = np.exp(z - z.max()); p /= p.sum()
        a = int(min((np.cumsum(p) < rng.random()).sum(), 5)); env.act(a)
    o = M.obs6(env.state(), idx)
    toks = M.tokens_from_obs6(o[None])[0]
    z = pol.logits(o[None])[0]
    data["games"][g] = {
        "opus": {k: ev[k] for k in ("mean", "se", "episodes", "max", "mean_length", "episodes_cut_at_max_steps")},
        "astra_ours": {k: ea[k] for k in ("mean", "se", "episodes", "mean_length")},
        "astra_paper": {k: paper[g]["hand"][k] for k in ("mean", "se", "mean_length")},
        "ppo100_best": {"name": b100[0], **{k: b100[1][k] for k in ("mean", "se")}},
        "ppo500_best": {"name": b500[0], **{k: b500[1][k] for k in ("mean", "se")}},
        "ppo_all": {k: round(v["mean"], 2) for k, v in ppo.items()},
        "faith": fa, "compile": comp, "layers": layers,
        "residual": {"dims": tm.D, "sops_categorical": len(cat) - len(inputs), "sops_numerical": len(num),
                     "input_dims": inputs, "largest_categorical": sorted(cat.items(), key=lambda kv: -kv[1])[:4]},
        "run": {"wall_s": run["wall_s"], "cost_usd": round(run["cost_usd"], 2),
                "output_tokens": run["usage"]["output_tokens"], "tool_free": run["audit"]["tool_free"]},
        "astra_run": {"wall_s": arun["wall_s"], "output_tokens": arun["audit"]["usage"]["output_tokens"],
                      "statements": apply_.get("statements_read") or apply_.get("statements"),
                      "nonzero": apply_.get("nonzero_weights") or apply_.get("nonzero")},
        "program": prog, "design": design, "astra_design": astra_design,
        "frame": {"obs": o.astype(int).tolist(), "tokens": toks.tolist(), "logits": [round(float(x), 2) for x in z], "step": stop},
    }
    if g != "breakout":
        dg = json.load(open(f"{R}/results/opus55_minatar_{g}/diagnosis.json")); dg.pop("death_records")
        da = json.load(open(f"{R}/results/astra_minatar_{g}/diagnosis.json")); da.pop("death_records")
        data["games"][g]["diag"] = {"opus": dg, "astra": da}
        data["games"][g]["sticky"] = {"replay": sticky["no_sticky_replay"][g], "hazard": sticky["sticky_hazard"][g]}
    print(g, "apply keys:", list(apply_.keys())[:12])
json.dump(data, open("/tmp/claude-0/-home-user-auto-rasp/de2b9d70-6f3e-5db7-b3e0-915adfdce244/scratchpad/artifact/data.json", "w"))
for g, d in data["games"].items():
    print(g, d["opus"]["mean"], d["astra_ours"]["mean"], d["ppo100_best"], d["ppo500_best"], d["layers"], d["residual"], d["astra_run"], d["frame"]["logits"])
