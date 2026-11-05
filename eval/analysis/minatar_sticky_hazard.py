"""How exposed is a policy to sticky actions? Per step: is replaying the previous action fatal now; how often the
policy moves / changes action; its action distribution (60 episodes). Usage: python eval/analysis/minatar_sticky_hazard.py <game>"""
import copy, sys, json
import numpy as np
sys.path.insert(0, "/home/user/auto-rasp")
from gorasp import minatar as M
from minatar import Environment
from eval.diagnose_minatar import fatal_actions

def run(pol, game, episodes=60, seed=99):
    idx = M.channel_index(game)
    rng = np.random.default_rng(seed)
    n = haz = moves = changes = 0
    acts = np.zeros(6)
    for ep in range(episodes):
        env = Environment(game, sticky_action_prob=0.1, difficulty_ramping=True)
        env.seed((seed * 1_000_003 + ep) % 2 ** 32); env.reset()
        prev = 0
        for t in range(M.MAX_STEPS):
            fat = fatal_actions(env.env)
            z = np.asarray(pol.logits(M.obs6(env.state(), idx)[None]), np.float64)[0]
            p = np.exp(z - z.max()); p /= p.sum()
            a = int(min((np.cumsum(p) < rng.random()).sum(), 5))
            n += 1; haz += fat[prev]; acts[a] += 1
            moves += a in (1, 2, 3, 4); changes += a != prev
            r, term = env.act(a); prev = env.last_action
            if term: break
    return {"steps": n, "frac_steps_where_replaying_previous_action_is_fatal": round(haz / n, 4),
            "frac_steps_moving": round(moves / n, 3), "frac_steps_changing_action": round(changes / n, 3),
            "action_distribution": (acts / n).round(3).tolist()}

game = sys.argv[1] if len(sys.argv) > 1 else "asterix"
print("opus ", json.dumps(run(M.TracrMinAtarPolicy("/home/user/auto-rasp/runs/opus55_minatar_" + game + "/final/model.npz"), game)))
print("astra", json.dumps(run(M.MLPPolicy("/home/user/auto-rasp/networks/paper_minatar/" + game + "/hand.npz"), game)))
