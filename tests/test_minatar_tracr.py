"""Checks the Tracr runtimes on an integer-vocabulary (MinAtar) program against Tracr's own apply.
The program here is a harness test only (never shown to the writers): it moves toward the ball's column."""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gorasp import minatar as M, tracr_fast as TF, tracr_policy as TP  # noqa: E402
from tracr.rasp import rasp  # noqa: E402


def program():
    toks, idx = rasp.tokens, rasp.indices
    col = rasp.categorical(rasp.Map(lambda i: (i % 10) if i < 100 else 0, idx))
    ball_col = rasp.categorical(rasp.Aggregate(rasp.Select(toks, idx, lambda k, q: k < 64 and bool(k & 8)), col))
    pad_col = rasp.categorical(rasp.Aggregate(rasp.Select(toks, idx, lambda k, q: k < 64 and bool(k & 1)), col))
    d = rasp.categorical(rasp.SequenceMap(lambda b, p: (b > p) - (b < p), ball_col, pad_col))
    z = rasp.categorical(rasp.SequenceMap(lambda dd, i: dd if i == 103 else (-dd if i == 101 else 0), d, idx))
    return rasp.numerical(rasp.Map(lambda v: 2.0 * v, z)).named("logits")


def main():
    sop = program()
    m = TP.compile_sop(sop, vocab=M.TRACR_VOCAB, max_seq_len=M.TRACR_MAX_SEQ_LEN)
    path = os.path.join(tempfile.mkdtemp(), "m.npz")
    TP.export(m, sop, path, vocab=M.TRACR_VOCAB, max_seq_len=M.TRACR_MAX_SEQ_LEN)
    rng = np.random.default_rng(0)
    o = np.zeros((8, 10, 10, 6), bool)
    for k in range(8):  # one paddle on the bottom row, one ball
        o[k, 9, rng.integers(10), 0] = True
        o[k, rng.integers(9), rng.integers(10), 3] = True
        o[k, 1:4, :, 2] = rng.random((3, 10)) < 0.7
    toks = M.tokens_from_obs6(o)
    ref = np.array([m.apply(["BOS"] + [int(t) for t in row]).decoded[1:] for row in toks], np.float64)
    for cls in (TP.TracrModel, TF.FastTracrModel):
        tm = cls(path)
        ours = tm.logits_from_tokens(toks)
        err = np.abs(ours - ref).max()
        print(cls.__name__, "max |ours - tracr apply| =", err)
        assert err < 1e-3, err
    pol = M.TracrMinAtarPolicy(path)
    z = pol.logits(o)
    assert z.shape == (8, 6) and np.allclose(z, ref[:, 100:106], atol=1e-3)
    print("OK")


if __name__ == "__main__":
    main()
