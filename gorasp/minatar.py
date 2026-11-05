"""MinAtar games for Experiment 5, exactly as the paper scores them.

Official MinAtar 1.0.15 (`minatar.Environment`, sticky actions 0.1, difficulty ramping on), actions sampled from the
softmax of the policy's 6 logits (0 no-op, 1 left, 2 up, 3 right, 4 down, 5 fire), episodes cut at 10,000 steps,
mean score over 1,000 episodes.

Observation: the paper's 10 x 10 x 6 binary grid (player, danger, reward, projectile, trail, gauge), each built as
the OR of some of the game's own channels (the "How the 6 channels are built" line of each prompt).
  - MLP networks (Astra's hand.npz): x[(row * 10 + col) * 6 + ch], 600 numbers.
  - Tracr networks: 106 tokens after BOS: the 100 cells row-major, each an integer 0..63 with bit ch set when the
    cell is 1 in channel ch, then the 6 action tokens 64..69. The logit of action a is the output at index 100 + a.
"""
import numpy as np
from minatar import Environment

GAMES = ("breakout", "seaquest", "asterix")
MAX_STEPS = 10_000
N_ACTIONS = 6
CHANNELS = ("player", "danger", "reward", "projectile", "trail", "gauge")
SOURCES = {  # paper's channel c <- OR of these game channels
    "breakout": (("paddle",), (), ("brick",), ("ball",), ("trail",), ()),
    "seaquest": (("sub_front", "sub_back"), ("enemy_fish", "enemy_sub", "enemy_bullet"),
                 ("enemy_fish", "enemy_sub", "diver"), ("friendly_bullet",), ("trail", "sub_back"),
                 ("oxygen_guage", "diver_guage")),
    "asterix": (("player",), ("enemy",), ("gold",), (), ("trail",), ()),
}
TRACR_VOCAB = tuple(range(70))
TRACR_MAX_SEQ_LEN = 106
ACTION_TOKENS = tuple(range(64, 70))


def channel_index(game):
    ch = Environment(game).env.channels
    return [[ch[s] for s in srcs] for srcs in SOURCES[game]]


def obs6(state, idx):
    """(10, 10, n) game state -> (10, 10, 6) bool, the paper's channels."""
    out = np.zeros((10, 10, 6), bool)
    for c, srcs in enumerate(idx):
        if srcs:
            out[:, :, c] = state[:, :, srcs].any(axis=-1)
    return out


def tokens_from_obs6(o):
    """(n, 10, 10, 6) bool -> (n, 106) int tokens (no BOS)."""
    o = np.asarray(o, np.int64)
    cells = (o * (1 << np.arange(6))).sum(axis=-1).reshape(len(o), 100)
    return np.concatenate([cells, np.tile(np.array(ACTION_TOKENS), (len(o), 1))], axis=1)


class MLPPolicy:
    """The paper's 600 -> 32 -> 32 -> 6 tanh network (hand.npz layout)."""

    def __init__(self, path):
        z = np.load(path)
        self.W = [z[f"actor/dense{k}/kernel"].astype(np.float32) for k in (1, 2)] + [z["actor/logits/kernel"]]
        self.b = [z[f"actor/dense{k}/bias"].astype(np.float32) for k in (1, 2)] + [z["actor/logits/bias"]]

    def logits(self, o):
        h = np.asarray(o, np.float32).reshape(len(o), 600)
        h = np.tanh(h @ self.W[0] + self.b[0])
        h = np.tanh(h @ self.W[1] + self.b[1])
        return h @ self.W[2] + self.b[2]


class TracrMinAtarPolicy:
    """A Tracr-compiled network; logits read at indices 100..105. Caches logits per distinct observation."""

    def __init__(self, path, fast=True):
        from .tracr_fast import FastTracrModel
        from .tracr_policy import TracrModel
        self.model = (FastTracrModel if fast else TracrModel)(path, max_rows=8192)
        assert self.model.meta["max_seq_len"] == TRACR_MAX_SEQ_LEN
        self.cache = {}
        self.max_cache = 2_000_000
        self.forward_positions = 0

    def logits(self, o):
        o = np.asarray(o, bool)
        keys = [x.tobytes() for x in np.packbits(o.reshape(len(o), -1), axis=1)]
        miss = [i for i, k in enumerate(keys) if k not in self.cache]
        if miss:
            if len(self.cache) > self.max_cache:
                self.cache.clear()
            toks = tokens_from_obs6(o[miss])
            # copy: a view would keep the whole (n, 107, D) residual alive for as long as the cache holds it
            z = np.array(self.model.residual(self.model.encode(toks))[:, 1 + 100:1 + 106, self.model.out_index],
                         dtype=np.float32, copy=True)
            self.forward_positions += len(miss)
            for i, row in zip(miss, z):
                self.cache[keys[i]] = row
        return np.stack([self.cache[k] for k in keys])


class ZeroPolicy:
    def logits(self, o):
        return np.zeros((len(o), N_ACTIONS), np.float32)


def run_episodes(game, policy, n_episodes, seed, max_steps=MAX_STEPS, batch=None, progress=None, starts=None):
    """Plays n_episodes in lockstep batches of `batch` episodes; returns per-episode (score, length).
    Episode i is seeded with seed and i; each batch samples actions from its own stream default_rng([seed, start]),
    so results do not depend on how batches are spread over processes (`starts` = the batches to play here)."""
    idx = channel_index(game)
    batch = batch or n_episodes
    scores, lengths = np.full(n_episodes, np.nan), np.zeros(n_episodes, int)
    for start in (range(0, n_episodes, batch) if starts is None else starts):
        rng = np.random.default_rng([seed, start])
        ids = list(range(start, min(n_episodes, start + batch)))
        envs = []
        for i in ids:
            e = Environment(game, sticky_action_prob=0.1, difficulty_ramping=True)
            e.seed((seed * 1_000_003 + i) % (2 ** 32))
            e.reset()
            envs.append(e)
        alive = np.ones(len(ids), bool)
        for t in range(max_steps):
            act = np.flatnonzero(alive)
            if not len(act):
                break
            o = np.stack([obs6(envs[j].state(), idx) for j in act])
            z = np.asarray(policy.logits(o), np.float64)
            z -= z.max(axis=1, keepdims=True)
            p = np.exp(z)
            p /= p.sum(axis=1, keepdims=True)
            a = (np.cumsum(p, axis=1) < rng.random((len(act), 1))).sum(axis=1).clip(0, N_ACTIONS - 1)
            for j, aj in zip(act, a):
                r, term = envs[j].act(int(aj))
                scores[ids[j]] = (0.0 if np.isnan(scores[ids[j]]) else scores[ids[j]]) + r
                lengths[ids[j]] += 1
                if term:
                    alive[j] = False
            if progress and t % 1000 == 999:
                progress(start, t, int(alive.sum()))
    return scores, lengths


def summarize(scores, lengths):
    n = len(scores)
    return {"mean": float(scores.mean()), "se": float(scores.std(ddof=1) / np.sqrt(n)) if n > 1 else None,
            "episodes": int(n), "max": float(scores.max()), "mean_length": float(lengths.mean()),
            "episodes_cut_at_max_steps": int((lengths >= MAX_STEPS).sum())}
