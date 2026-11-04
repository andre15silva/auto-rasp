"""Move policies. A policy maps (board (n,81) int8 with 1 Black/-1 White, color (n,) 0 Black/1 White to move,
legal (n,82) bool) -> logits (n,82). The player masks illegal moves and samples from softmax(logits) at T = 1."""
import json
import os

import numpy as np

from . import go


class RandomPolicy:
    name = "random"

    def logits(self, board, color, legal):
        return np.zeros((len(board), go.N_ACTIONS), np.float32)


class MLPPolicy:
    """The paper's network format: arch.json + L1..L{depth}.{W,b} + out.{W,b}; h = relu(x @ W + b)."""

    def __init__(self, path, name=None):
        arch = json.load(open(os.path.join(path, "arch.json")))
        self.depth = arch["depth"]
        self.W = [np.load(os.path.join(path, f"L{k}.W.npy")).astype(np.float32) for k in range(1, self.depth + 1)]
        self.b = [np.load(os.path.join(path, f"L{k}.b.npy")).astype(np.float32) for k in range(1, self.depth + 1)]
        self.oW = np.load(os.path.join(path, "out.W.npy")).astype(np.float32)
        self.ob = np.load(os.path.join(path, "out.b.npy")).astype(np.float32)
        self.name = name or os.path.basename(path.rstrip("/"))

    def logits(self, board, color, legal):
        h = go.planes(board, color)
        for W, b in zip(self.W, self.b):
            h = np.maximum(h @ W + b, 0.0)
        return h @ self.oW + self.ob


class MixPolicy:
    """With probability p plays like `base`, otherwise uniformly at random among legal moves."""

    def __init__(self, base, p, name):
        self.base, self.p, self.name = base, p, name

    def logits(self, board, color, legal):
        z = np.where(legal, self.base.logits(board, color, legal), -np.inf)
        z = z - z.max(axis=1, keepdims=True)
        pb = np.exp(z)
        pb /= pb.sum(axis=1, keepdims=True)
        pu = legal / legal.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore"):
            return np.log(self.p * pb + (1 - self.p) * pu)


def masked_probs(logits, legal):
    z = np.where(legal, np.asarray(logits, np.float64), -np.inf)
    z = z - z.max(axis=1, keepdims=True)
    p = np.exp(z)
    return p / p.sum(axis=1, keepdims=True)


def sample(logits, legal, rng):
    """Samples one legal move per row from softmax(logits) restricted to legal moves (temperature 1)."""
    p = masked_probs(logits, legal)
    u = rng.random((len(p), 1))
    a = (np.cumsum(p, axis=1) < u).sum(axis=1)
    a = np.minimum(a, go.N_ACTIONS - 1)
    # guard against round-off picking an illegal move at the end of the cumsum
    bad = ~legal[np.arange(len(a)), a]
    if bad.any():
        a[bad] = np.argmax(p[bad], axis=1)
    return a, p
