"""Hidden evaluation of a written network (never shown to the writer).

    python eval/evaluate.py --run runs/opus55_b0            # the run's final Tracr-compiled program
    python eval/evaluate.py --mlp networks/paper/budget_0 --name astra_b0   # a paper network, same protocol

2,000 games (the subject Black in half, sampled moves, seed 777 + j as in the paper's evaluate script) against:
  hidden:    ppo_s0, ppo_s2 (same-size PPO, lr 3e-5, seeds 0/2; main = their mean) and a uniform random player;
  reference: Astra's written networks astra_b0/b10/b25/b50 (head-to-head).
For a Tracr network it also measures faithfulness: on 256 positions from its games against ppo_s0 it compares the
compiled network's logits with rasp.evaluate of the same program (computed in the sandbox).
"""
import argparse
import concurrent.futures as cf
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def make_subject(spec):
    from gorasp.policies import MLPPolicy, RandomPolicy
    from gorasp.tracr_fast import FastTracrPolicy
    kind, path = spec
    if kind == "tracr":
        p = FastTracrPolicy(path)
        p.model.max_rows = 8192
        return p
    if kind == "mlp":
        return MLPPolicy(path)
    return RandomPolicy()


def make_opponent(name):
    from gorasp import opponents as O
    return {**O.hidden(), **O.reference()}[name]


def job(spec, opp, games, seed, collect):
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    from gorasp.play import play, summary
    t = time.time()
    r = play(make_subject(spec), make_opponent(opp), games, seed=seed, collect=collect)
    s = summary(r)
    s["seconds"] = round(time.time() - t, 1)
    pos = r.get("positions") if collect else None
    return opp, s, pos


def check_fast(model_path, positions, n=256, seed=1):
    """The evaluation's flush-to-zero runtime vs the reference runtime used in the passes, on real positions."""
    from gorasp import go
    from gorasp.tracr_fast import FastTracrModel
    from gorasp.tracr_policy import TracrModel
    boards, colors, _ = positions
    idx = np.random.default_rng(seed).choice(len(boards), size=min(n, len(boards)), replace=False)
    toks = go.tokens(boards[idx], colors[idx])
    a = TracrModel(model_path, max_rows=8192).logits_from_tokens(toks)
    b = FastTracrModel(model_path, max_rows=8192).logits_from_tokens(toks)
    return {"positions": int(len(toks)), "max_abs_logit_diff": float(np.abs(a - b).max())}


def faithfulness(run_dir, positions, n=256, seed=0):
    """Compiled logits vs rasp.evaluate of the program, on n positions the network actually faced."""
    from gorasp import go
    from gorasp.policies import masked_probs
    from gorasp.tracr_policy import TracrModel
    from harness import sandbox
    boards, colors, legal = positions
    idx = np.random.default_rng(seed).choice(len(boards), size=min(n, len(boards)), replace=False)
    boards, colors, legal = boards[idx], colors[idx], legal[idx]
    toks = go.tokens(boards, colors)
    out = os.path.join(run_dir, "final_faithfulness")
    res = sandbox.compile_in_sandbox(os.path.join(run_dir, "work"), out, rasp_inputs=toks.tolist(), timing=False)
    if not res.get("ok") or not os.path.exists(os.path.join(out, "rasp.npz")):
        return {"ok": False, "error": res.get("error", "no rasp.npz")[-2000:]}
    rasp_info = {k: res.get(k) for k in ("rasp_sops", "rasp_sops_failed", "rasp_output_failed", "rasp_first_error")}
    tm = TracrModel(os.path.join(out, "model.npz"))
    comp = tm.logits_from_tokens(toks).astype(np.float64)
    ref = np.load(os.path.join(out, "rasp.npz"))[res["output_label"]].astype(np.float64)
    defined = ~np.isnan(ref)
    m = legal & defined
    full = (defined | ~legal).all(axis=1)  # RASP gives a value for every legal move
    diff = np.abs(comp - ref)[m]
    pc = masked_probs(comp, legal)
    agree, tv = [], []
    for i in np.flatnonzero(full):
        pr = masked_probs(ref[i:i + 1], legal[i:i + 1])[0]
        agree.append(np.argmax(np.where(legal[i], comp[i], -np.inf)) == np.argmax(np.where(legal[i], ref[i], -np.inf)))
        tv.append(0.5 * np.abs(pc[i] - pr).sum())
    return {"ok": True, "positions": int(len(toks)), "rasp_seconds": res.get("rasp_seconds"), **rasp_info,
            "legal_entries_rasp_defined": float(m.sum() / legal.sum()),
            "positions_rasp_defined_on_all_legal_moves": int(full.sum()),
            "mean_abs_logit_diff": float(diff.mean()) if len(diff) else None,
            "max_abs_logit_diff": float(diff.max()) if len(diff) else None,
            "argmax_agreement": float(np.mean(agree)) if agree else None,
            "mean_total_variation": float(np.mean(tv)) if tv else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--mlp")
    ap.add_argument("--name")
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--ref-games", type=int, default=None, help="games vs the Astra reference networks "
                    "(default: --games)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--faithfulness-only", action="store_true",
                    help="(re)run only the faithfulness check of --run on positions from 64 games vs ppo_s0, "
                         "merging it into the existing eval.json")
    ap.add_argument("--opponents", default="ppo_s0,ppo_s2,random,astra_b0,astra_b10,astra_b25,astra_b50")
    args = ap.parse_args()
    out = {"games": args.games, "ref_games": args.ref_games or args.games}
    if args.run:
        run_dir = os.path.abspath(args.run)
        name = args.name or os.path.basename(run_dir.rstrip("/"))
        comp = json.load(open(os.path.join(run_dir, "final", "compile.json")))
        out["compile"] = comp
        spec = ("tracr", os.path.join(run_dir, "final", "model.npz")) if comp.get("ok") else ("random", None)
        out["subject"] = "tracr" if comp.get("ok") else "zero network (final program failed to compile)"
    else:
        name = args.name or os.path.basename(args.mlp.rstrip("/"))
        spec, out["subject"] = ("mlp", os.path.abspath(args.mlp)), "mlp"
    if args.faithfulness_only:
        d = os.path.join(REPO, "results", name)
        prev = json.load(open(os.path.join(d, "eval.json")))
        _, _, pos = job(spec, "ppo_s0", 64, 777, True)
        prev["fast_runtime_check"] = check_fast(spec[1], pos)
        prev["faithfulness"] = faithfulness(run_dir, pos)
        prev["faithfulness"]["positions_from"] = "64 games vs ppo_s0 (seed 777), sampled"
        json.dump(prev, open(os.path.join(d, "eval.json"), "w"), indent=1)
        print("faithfulness:", json.dumps(prev["faithfulness"]), flush=True)
        return
    opps = [o for o in args.opponents.split(",") if o != name]
    t0 = time.time()
    per, positions = {}, None
    with cf.ProcessPoolExecutor(args.workers, mp_context=mp.get_context("spawn")) as ex:
        ng = lambda o: args.ref_games if (o.startswith("astra_") and args.ref_games) else args.games  # noqa: E731
        futs = [ex.submit(job, spec, o, ng(o), 777 + j, o == "ppo_s0" and spec[0] == "tracr")
                for j, o in enumerate(opps)]
        for f in cf.as_completed(futs):
            o, s, pos = f.result()
            per[o] = s
            positions = pos if pos is not None else positions
            print(f"{name} vs {o}: {s['score']:.4f} (B {s['score_as_black']:.3f} W {s['score_as_white']:.3f}) "
                  f"[{s['seconds']}s]", flush=True)
    out["per_opponent"] = {o: per[o] for o in opps}
    main_opps = [o for o in ("ppo_s0", "ppo_s2") if o in per]
    out["main"] = float(np.mean([per[o]["score"] for o in main_opps])) if main_opps else None
    out["seconds"] = round(time.time() - t0, 1)
    if spec[0] == "tracr" and positions is not None:
        out["fast_runtime_check"] = check_fast(spec[1], positions)
        print("fast runtime vs reference:", out["fast_runtime_check"], flush=True)
        out["faithfulness"] = faithfulness(run_dir, positions)
        print("faithfulness:", json.dumps(out["faithfulness"]), flush=True)
    d = os.path.join(REPO, "results", name)
    os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, "eval.json"), "w"), indent=1)
    print(f"{name}: main {out['main']}", flush=True)


if __name__ == "__main__":
    main()
