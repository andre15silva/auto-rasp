"""Why does a MinAtar network die? Plays episodes exactly as in scoring (sticky actions 0.1, sampled actions) and,
for every step, tests each action on a copy of the game (analysis only; the policy itself uses no search):
  - cause of each death (Seaquest: collision / oxygen / surfacing without a diver; Asterix: collision);
  - whether some action would have survived the fatal step, and whether a sticky repeat played the fatal action;
  - over all steps, the probability the policy puts on actions that die this step while a safe one exists.

    python eval/diagnose_minatar.py --run runs/opus55_minatar_asterix
    python eval/diagnose_minatar.py --mlp networks/paper_minatar/asterix/hand.npz --game asterix --name astra_minatar_asterix
"""
import argparse
import copy
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from gorasp import minatar as M  # noqa: E402
from minatar import Environment  # noqa: E402


def fatal_actions(game_env):
    out = []
    for a in range(M.N_ACTIONS):
        g = copy.deepcopy(game_env)
        _, term = g.act(a)
        out.append(bool(term))
    return np.array(out)


def death_cause(game, g):
    if game == "seaquest":
        if g.oxygen <= 0:
            return "oxygen ran out"
        if g.sub_y == 0 and g.diver_count == 0:
            return "surfaced without a diver"
        return "hit by an enemy, enemy sub or bullet"
    return "hit by an enemy"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--mlp")
    ap.add_argument("--game")
    ap.add_argument("--name")
    ap.add_argument("--episodes", type=int, default=100)
    ap.add_argument("--seed", type=int, default=4242)
    args = ap.parse_args()
    if args.run:
        game = json.load(open(os.path.join(args.run, "config.json")))["game"]
        pol = M.TracrMinAtarPolicy(os.path.join(args.run, "final", "model.npz"))
        name = args.name or os.path.basename(args.run.rstrip("/"))
    else:
        game, pol, name = args.game, M.MLPPolicy(args.mlp), args.name
    idx = channel = M.channel_index(game)
    rng = np.random.default_rng(args.seed)
    deaths, steps, lengths, scores = [], 0, [], []
    unsafe_mass, unsafe_mass_when_avoidable, avoidable_steps = 0.0, 0.0, 0
    extra = {"surfacings_with_divers": 0, "divers_collected": 0, "max_divers": []}
    for ep in range(args.episodes):
        env = Environment(game, sticky_action_prob=0.1, difficulty_ramping=True)
        env.seed((args.seed * 1_000_003 + ep) % 2 ** 32)
        env.reset()
        score, t, maxd = 0.0, 0, 0
        while t < M.MAX_STEPS:
            fat = fatal_actions(env.env)
            o = M.obs6(env.state(), idx)[None]
            z = np.asarray(pol.logits(o), np.float64)[0]
            p = np.exp(z - z.max())
            p /= p.sum()
            a = int(min((np.cumsum(p) < rng.random()).sum(), M.N_ACTIONS - 1))
            steps += 1
            unsafe_mass += p[fat].sum()
            if fat.any() and not fat.all():
                avoidable_steps += 1
                unsafe_mass_when_avoidable += p[fat].sum()
            if game == "seaquest":
                d0, y0 = env.env.diver_count, env.env.sub_y
            before = copy.deepcopy(env.env)
            r, term = env.act(a)
            executed = env.last_action
            score += r
            t += 1
            if game == "seaquest":
                g = env.env
                maxd = max(maxd, g.diver_count)
                if g.diver_count > d0:
                    extra["divers_collected"] += 1
                if y0 > 0 and g.sub_y == 0 and d0 > 0 and not term:
                    extra["surfacings_with_divers"] += 1
            if term:
                deaths.append({"episode": ep, "step": t, "cause": death_cause(game, env.env),
                               "avoidable_this_step": bool(not fat.all()),
                               "sticky_repeat_played_it": bool(executed != a),
                               "policy_prob_on_fatal_actions": float(p[fat].sum()),
                               "argmax_was_fatal": bool(fat[int(np.argmax(z))]),
                               "oxygen": getattr(before, "oxygen", None),
                               "divers": getattr(before, "diver_count", None)})
                break
        lengths.append(t)
        scores.append(score)
        extra["max_divers"].append(maxd)
    causes = {}
    for d in deaths:
        causes[d["cause"]] = causes.get(d["cause"], 0) + 1
    av = [d for d in deaths if d["avoidable_this_step"]]
    out = {"name": name, "game": game, "episodes": args.episodes, "mean_score": float(np.mean(scores)),
           "mean_length": float(np.mean(lengths)), "deaths": len(deaths), "death_causes": causes,
           "deaths_avoidable_by_another_action_this_step": len(av),
           "of_those_caused_by_a_sticky_repeat": sum(d["sticky_repeat_played_it"] for d in av),
           "of_those_where_the_policy_itself_chose_a_fatal_action": sum(not d["sticky_repeat_played_it"] for d in av),
           "mean_policy_prob_on_fatal_actions_at_avoidable_deaths": float(np.mean(
               [d["policy_prob_on_fatal_actions"] for d in av])) if av else None,
           "avoidable_deaths_where_argmax_was_fatal": sum(d["argmax_was_fatal"] for d in av),
           "steps": steps, "steps_with_some_but_not_all_actions_fatal": avoidable_steps,
           "mean_prob_on_fatal_actions_at_those_steps": unsafe_mass_when_avoidable / max(1, avoidable_steps)}
    if game == "seaquest":
        out["surfacings_with_divers_per_episode"] = extra["surfacings_with_divers"] / args.episodes
        out["divers_collected_per_episode"] = extra["divers_collected"] / args.episodes
        out["mean_max_divers_held"] = float(np.mean(extra["max_divers"]))
        ox = [d for d in deaths if d["cause"] == "oxygen ran out"]
        out["divers_held_at_oxygen_deaths"] = [d["divers"] for d in ox][:30]
    d = os.path.join(REPO, "results", name)
    os.makedirs(d, exist_ok=True)
    json.dump({**out, "death_records": deaths}, open(os.path.join(d, "diagnosis.json"), "w"), indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
