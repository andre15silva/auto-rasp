"""Tracr-compiled Go policies.

The network is whatever tracr.compiler.compiling.compile_rasp_to_model produces for the writer's RASP program,
with these fixed settings:
    vocab = {".", "x", "o", "B", "W"}, max_seq_len = 82, compiler_bos = "BOS", causal = False,
    mlp_exactness = the program's MLP_EXACTNESS (default 100).
Input: ["BOS"] + 81 point tokens (row-major, from the mover's view: "x" mover's stone, "o" opponent's, "." empty)
+ ["B" or "W"] (colour to move). Output: the program's numerical SOp at positions 1..82 = the 82 move logits
(row*9+col, 81 = pass).

`export` stores the assembled weights as sparse matrices (weights only, no code). `TracrModel` runs them with the
same arithmetic as Tracr's Haiku model (tracr/transformer/model.py): no layer norm, attention logits
(x Wq)(x Wk)^T / sqrt(key_size), softmax over all positions, ReLU MLPs, residual adds; the output is the residual
coordinate of the program's output SOp. It is checked against Tracr's own `apply` in tests/test_tracr_policy.py.
"""
import json
import math

import numpy as np
import scipy.sparse as sp

VOCAB = (".", "x", "o", "B", "W")
MAX_SEQ_LEN = 82
BOS = "BOS"


def compile_sop(sop, mlp_exactness=100, vocab=VOCAB, max_seq_len=MAX_SEQ_LEN):
    from tracr.compiler import compiling
    from tracr.rasp import rasp
    if not isinstance(sop, rasp.SOp):
        raise TypeError(f"program() must return a rasp.SOp, got {type(sop).__name__}")
    if not rasp.is_numerical(sop):
        raise ValueError("the output SOp must be numerical (wrap it in rasp.numerical(...)): its value at each "
                         "position is that move's logit")
    return compiling.compile_rasp_to_model(sop, vocab=set(vocab), max_seq_len=max_seq_len, compiler_bos=BOS,
                                           mlp_exactness=mlp_exactness)


def model_stats(m):
    dense = nnz = 0
    for d in m.params.values():
        for a in d.values():
            a = np.asarray(a)
            dense += a.size
            nnz += int(np.count_nonzero(a))
    c = m.model_config
    return {"layers": c.num_layers, "heads": c.num_heads, "key_size": c.key_size,
            "mlp_hidden_size": c.mlp_hidden_size, "residual_dims": len(m.residual_labels),
            "dense_params": int(dense), "nonzero_params": int(nnz)}


def export(m, sop, path, extra=None, vocab=VOCAB, max_seq_len=MAX_SEQ_LEN):
    arrays = {}
    for mod, d in m.params.items():
        for name, a in d.items():
            a = np.asarray(a, np.float32)
            key = f"{mod}/{name}"
            if a.ndim == 2:
                s = sp.csr_matrix(a)
                arrays[key + "#data"], arrays[key + "#indices"], arrays[key + "#indptr"] = s.data, s.indices, s.indptr
                arrays[key + "#shape"] = np.array(a.shape, np.int64)
            else:
                arrays[key] = a
    c = m.model_config
    labels = list(m.residual_labels)
    meta = {"num_heads": c.num_heads, "num_layers": c.num_layers, "key_size": c.key_size,
            "mlp_hidden_size": c.mlp_hidden_size, "causal": bool(c.causal), "layer_norm": bool(c.layer_norm),
            "residual_labels": labels, "input_encoding": {str(k): int(v) for k, v in
                                                          m.input_encoder.encoding_map.items()},
            "output_label": sop.label, "output_index": labels.index(sop.label), "vocab": list(vocab),
            "max_seq_len": max_seq_len, "bos": BOS, "stats": model_stats(m)}
    meta.update(extra or {})
    np.savez_compressed(path, meta=np.array(json.dumps(meta)), **arrays)
    return meta


def _ix(idx):
    """Index array -> slice when it is a contiguous range (much faster gathers / scatter-adds)."""
    idx = np.asarray(idx)
    if len(idx) and np.array_equal(idx, np.arange(idx[0], idx[0] + len(idx))):
        return slice(int(idx[0]), int(idx[0]) + len(idx))
    return idx


class TracrModel:
    def __init__(self, path, max_rows=1 << 15):
        z = np.load(path, allow_pickle=False)
        self.meta = meta = json.loads(str(z["meta"]))
        assert not meta["layer_norm"] and not meta["causal"]
        self.H, self.K, self.L = meta["num_heads"], meta["key_size"], meta["num_layers"]
        self.labels = meta["residual_labels"]
        self.D = len(self.labels)
        self.enc = meta["input_encoding"]
        self.vocab = meta.get("vocab", list(VOCAB))
        self.max_seq_len = meta.get("max_seq_len", MAX_SEQ_LEN)
        self.out_index = meta["output_index"]
        self.max_rows = max_rows

        def mat(key):
            return sp.csr_matrix((z[key + "#data"], z[key + "#indices"], z[key + "#indptr"]),
                                 shape=tuple(z[key + "#shape"]))

        self.tok_emb = np.ascontiguousarray(mat("token_embed/embeddings").toarray(), np.float32)
        self.pos_emb = np.ascontiguousarray(mat("pos_embed/embeddings").toarray(), np.float32)
        positional = np.array([lab.startswith("indices:") or lab in ("one", f"tokens:{BOS}") for lab in self.labels])
        self.layers = []
        for l in range(self.L):
            p = f"transformer/layer_{l}"
            Wq, Wk, Wv, Wo = (mat(f"{p}/attn/{n}/w") for n in ("query", "key", "value", "linear"))
            bq, bk, bv, bo = (z[f"{p}/attn/{n}/b"] for n in ("query", "key", "value", "linear"))
            heads = []
            for h in range(self.H):
                cs = slice(h * self.K, (h + 1) * self.K)
                q, k, v, o = (Wq[:, cs].toarray(), Wk[:, cs].toarray(), Wv[:, cs].toarray(), Wo[cs, :].tocsr())
                qk = np.flatnonzero(q.any(0) | k.any(0) | (bq[cs] != 0) | (bk[cs] != 0))
                vo = np.flatnonzero((v.any(0) | (bv[cs] != 0)) & (np.diff(o.indptr) > 0))
                if len(vo) == 0:
                    continue  # this head writes nothing
                q, k, v, o = q[:, qk], k[:, qk], v[:, vo], o[vo, :].toarray()
                rq, rk, rv = (np.flatnonzero(a.any(1)) for a in (q, k, v))
                co = np.flatnonzero(o.any(0))
                hd = dict(rq=_ix(rq), q=q[rq], bq=bq[cs][qk], rk=_ix(rk), k=k[rk], bk=bk[cs][qk],
                          rv=_ix(rv), v=v[rv], bv=bv[cs][vo], co=_ix(co), o=o[:, co], w=None)
                if positional[rq].all() and positional[rk].all():
                    # the pattern depends only on positions: compute it once (same arithmetic as below)
                    x0 = np.full((1, self.max_seq_len + 1), self.enc[str(self.vocab[0])], np.int64)
                    x0[0, 0] = self.enc[BOS]
                    x0 = self._embed(x0)
                    hd["w"] = self._attn_weights(hd, x0, 1, self.max_seq_len + 1)[0]
                heads.append(hd)
            W1, W2 = mat(f"{p}/mlp/linear_1/w"), mat(f"{p}/mlp/linear_2/w")
            b1, b2 = z[f"{p}/mlp/linear_1/b"], z[f"{p}/mlp/linear_2/b"]
            W1c, W2r = W1.tocsc(), W2.tocsr()
            hid = np.flatnonzero(((np.diff(W1c.indptr) > 0) | (b1 != 0)) & (np.diff(W2r.indptr) > 0))
            W1h, W2h = W1c[:, hid].toarray(), W2r[hid, :].toarray()
            r1, c2 = np.flatnonzero(W1h.any(1)), np.flatnonzero(W2h.any(0))
            self.layers.append(dict(heads=heads, bo=bo, r1=_ix(r1), W1=W1h[r1], b1=b1[hid], c2=_ix(c2),
                                    W2=W2h[:, c2], b2=b2))

    # ---- inputs
    def encode(self, token_rows):
        """token_rows: (n, max_seq_len) array of vocab tokens (no BOS) -> (n, max_seq_len + 1) int ids."""
        rows = np.asarray(token_rows)
        if all(isinstance(t, int) for t in self.vocab):  # integer vocab (MinAtar): array lookup
            lut = np.zeros(max(self.vocab) + 1, np.int64)
            for t in self.vocab:
                lut[t] = self.enc[str(t)]
            ids = lut[rows.astype(np.int64)]
        else:
            lut = {t: self.enc[str(t)] for t in self.vocab}
            ids = np.vectorize(lut.__getitem__, otypes=[np.int64])(rows)
        return np.concatenate([np.full((len(ids), 1), self.enc[BOS]), ids], axis=1)

    # ---- forward
    def _embed(self, ids):
        n, T = ids.shape
        x = np.take(self.tok_emb, ids, axis=0)
        x += self.pos_emb[:T][None]
        return x.reshape(n * T, self.D)

    def _attn_weights(self, h, x, n, T):
        q = (x[:, h["rq"]] @ h["q"] + h["bq"]).reshape(n, T, -1)
        k = (x[:, h["rk"]] @ h["k"] + h["bk"]).reshape(n, T, -1)
        logit = np.matmul(q, k.transpose(0, 2, 1)) * np.float32(1.0 / math.sqrt(self.K))
        logit -= logit.max(axis=-1, keepdims=True)
        w = np.exp(logit)
        w /= w.sum(axis=-1, keepdims=True)
        return w

    def _forward_chunk(self, ids):
        n, T = ids.shape
        x = self._embed(ids)
        for lay in self.layers:
            upd = []
            for h in lay["heads"]:
                w = h["w"] if (h["w"] is not None and T == self.max_seq_len + 1) else self._attn_weights(h, x, n, T)
                v = (x[:, h["rv"]] @ h["v"] + h["bv"]).reshape(n, T, -1)
                a = np.matmul(w, v).reshape(n * T, -1)
                upd.append((h["co"], a @ h["o"]))
            for co, u in upd:  # all heads read the same residual, then write
                x[:, co] += u
            if lay["bo"].any():
                x += lay["bo"]
            if len(lay["b1"]):
                hdn = np.maximum(x[:, lay["r1"]] @ lay["W1"] + lay["b1"], 0.0)
                x[:, lay["c2"]] += hdn @ lay["W2"]
            if lay["b2"].any():
                x += lay["b2"]
        return x.reshape(n, T, self.D)

    def residual(self, ids):
        """Final residual stream (n, 83, D). Tracr never overwrites a subspace, so every SOp can be read here."""
        ids = np.asarray(ids)
        step = max(1, self.max_rows // ids.shape[1])
        return np.concatenate([self._forward_chunk(ids[i:i + step]) for i in range(0, len(ids), step)], axis=0)

    def logits_from_tokens(self, token_rows):
        res = self.residual(self.encode(token_rows))
        return res[:, 1:, self.out_index]

    # ---- policy interface
    def logits(self, board, color, legal):
        from . import go
        return self.logits_from_tokens(go.tokens(board, color))

    # ---- decoding the residual stream into SOp values
    def sop_layout(self):
        groups = {}
        for i, lab in enumerate(self.labels):
            name, sep, val = lab.partition(":")
            groups.setdefault(name, []).append((i, val if sep else None))
        return groups

    def decode(self, res, names=None):
        """{sop name: (n, 83) values}: numerical SOps give their coordinate, categorical ones the arg-max value."""
        out = {}
        for name, dims in self.sop_layout().items():
            if names is not None and name not in names:
                continue
            if len(dims) == 1 and dims[0][1] is None:
                out[name] = res[:, :, dims[0][0]]
            else:
                idx = np.array([d[0] for d in dims])
                vals = np.array([d[1] for d in dims], dtype=object)
                out[name] = vals[np.argmax(res[:, :, idx], axis=-1)]
        return out


class TracrPolicy:
    def __init__(self, path, name="tracr"):
        self.model = TracrModel(path)
        self.name = name

    def logits(self, board, color, legal):
        return self.model.logits(board, color, legal)
