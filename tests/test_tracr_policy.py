"""Checks that TracrModel (sparse numpy) reproduces Tracr's own Haiku forward pass on random Go positions."""
import os
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from gorasp import go, tracr_policy as TP  # noqa: E402
import sample_program  # noqa: E402


def random_boards(n, rng):
    b = rng.choice([-1, 0, 1], size=(n, 81), p=[0.3, 0.4, 0.3]).astype(np.int8)
    return b, rng.integers(0, 2, n)


def main(rounds=1, n=16):
    t = time.time()
    sop = sample_program.program(rounds)
    m = TP.compile_sop(sop)
    print("compiled", TP.model_stats(m), f"{time.time() - t:.0f}s", flush=True)
    path = os.path.join(tempfile.mkdtemp(), "model.npz")
    TP.export(m, sop, path)
    tm = TP.TracrModel(path)
    rng = np.random.default_rng(0)
    board, color = random_boards(n, rng)
    toks = go.tokens(board, color)
    t = time.time()
    ours = tm.logits_from_tokens(toks)
    print(f"numpy forward {n} positions: {time.time() - t:.2f}s")
    ref = np.array([m.apply(["BOS"] + list(row)).decoded[1:] for row in toks], dtype=np.float64)
    err = np.abs(ours - ref).max()
    print("max |numpy - tracr apply| =", err)
    assert err < 1e-3, err
    from tracr.rasp import rasp
    ev = np.array([rasp.evaluate(sop, list(row)) for row in toks], dtype=np.float64)
    print("max |compiled - rasp.evaluate| =", np.abs(ours - ev).max(), " mean", np.abs(ours - ev).mean())
    print("OK")


if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:]))
