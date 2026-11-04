"""A faster TracrModel for the final evaluation only (the writer's passes and its speed measurements use
tracr_policy.TracrModel unchanged, so nothing the writer observed changes mid-run).

The only difference is flush-to-zero: queries, keys, attention weights and attention outputs below float32's smallest normal
number (~1.2e-38) are set to 0. Subnormal floats are extremely slow on x86 CPUs, and Tracr's own JAX/XLA execution
on CPU flushes them to zero as well, so this is, if anything, closer to Tracr's arithmetic. The logits are checked
against TracrModel's on every evaluated network (eval/evaluate.py); they agree up to float32 summation order."""
import math

import numpy as np

from .tracr_policy import MAX_SEQ_LEN, TracrModel, TracrPolicy

TINY = np.finfo(np.float32).tiny


class FastTracrModel(TracrModel):
    def _attn_weights(self, h, x, n, T):
        q = x[:, h["rq"]] @ h["q"] + h["bq"]
        k = x[:, h["rk"]] @ h["k"] + h["bk"]
        q[np.abs(q) < TINY] = 0.0
        k[np.abs(k) < TINY] = 0.0
        q = q.reshape(n, T, -1)
        kt = np.ascontiguousarray(k.reshape(n, T, -1).transpose(0, 2, 1))  # a contiguous operand keeps BLAS
        logit = np.matmul(q, kt) * np.float32(1.0 / math.sqrt(self.K))
        logit -= logit.max(axis=-1, keepdims=True)
        w = np.exp(np.maximum(logit, -87.0))
        w[logit <= -87.0] = 0.0
        w /= w.sum(axis=-1, keepdims=True)
        return w

    def _forward_chunk(self, ids):
        n, T = ids.shape
        x = self._embed(ids)
        for lay in self.layers:
            upd = []
            for h in lay["heads"]:
                w = h["w"] if (h["w"] is not None and T == MAX_SEQ_LEN + 1) else self._attn_weights(h, x, n, T)
                v = (x[:, h["rv"]] @ h["v"] + h["bv"]).reshape(n, T, -1)
                u = np.matmul(w, v).reshape(n * T, -1) @ h["o"]
                u[np.abs(u) < TINY] = 0.0
                upd.append((h["co"], u))
            for co, u in upd:
                x[:, co] += u
            if lay["bo"].any():
                x += lay["bo"]
            if len(lay["b1"]):
                hdn = np.maximum(x[:, lay["r1"]] @ lay["W1"] + lay["b1"], 0.0)
                x[:, lay["c2"]] += hdn @ lay["W2"]
            if lay["b2"].any():
                x += lay["b2"]
        return x.reshape(n, T, self.D)


class FastTracrPolicy(TracrPolicy):
    def __init__(self, path, name="tracr"):
        self.model = FastTracrModel(path)
        self.name = name
