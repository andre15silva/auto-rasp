"""Opponents. All networks are the released Experiment-6 networks of the paper (networks/paper/, fetched by
scripts/fetch_networks.sh): the same-size PPO networks (512 x 6, lr 3e-5, seeds 0/1/2, 20.5 M self-play games)
and Astra's written networks (budgets 0/10/25/50).

As in the paper, the writer practises against seed 1 ("strong") and is evaluated on seeds 0 and 2, which it never
plays. The paper's hidden small PPO networks and its REINFORCE networks are not released, so "weak" is a mixture:
each move is PPO seed 1's with probability WEAK_P, otherwise uniform random."""
import os

from .policies import MixPolicy, MLPPolicy, RandomPolicy

NET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "networks", "paper")
WEAK_P = 0.7


def _mlp(name, label):
    return MLPPolicy(os.path.join(NET, name), name=label)


def practice():
    strong = _mlp("ppo_same_size_lr3e-5_s1", "strong")
    return {"random": RandomPolicy(), "weak": MixPolicy(strong, WEAK_P, "weak"), "strong": strong}


HIDDEN_MAIN = ("ppo_s0", "ppo_s2")


def hidden():
    return {"ppo_s0": _mlp("ppo_same_size_lr3e-5_s0", "ppo_s0"), "ppo_s2": _mlp("ppo_same_size_lr3e-5_s2", "ppo_s2"),
            "random": RandomPolicy()}


def reference():
    """Astra's (gpt-6-astra) weight-space-programmed networks from the paper, for head-to-heads."""
    return {f"astra_b{b}": _mlp(f"budget_{b}", f"astra_b{b}") for b in (0, 10, 25, 50)}
