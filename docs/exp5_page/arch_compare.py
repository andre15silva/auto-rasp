# Size and work of the two kinds of MinAtar network, for the page's "Two very different networks" section.
# Astra's hand-written MLP: networks/paper_minatar/{game}/hand.npz (600 -> 32 -> 32 -> 6, tanh).
# Opus's compiled Tracr transformer: runs/opus55_minatar_{game}/final/model.npz, run over T = 107 positions
# (BOS + 100 cell tokens + 6 action tokens).
# Multiply-adds per move: "dense" counts every weight as assembled (Tracr: full Q/K/V/O, the T x T scores and the
# weighted sum per head, both MLP matrices); "nonzero" counts only nonzero weights, plus the T x T attention work at
# each head's own (trimmed) width. Biases count as parameters, not as multiply-adds.
# Run from the repo root in the rasp venv:  python docs/exp5_page/arch_compare.py [out.json]
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.getcwd())
from gorasp.tracr_policy import TracrModel  # noqa: E402

T = 107


def astra(game):
    z = np.load(f"networks/paper_minatar/{game}/hand.npz")
    Ws = [z["actor/dense1/kernel"], z["actor/dense2/kernel"], z["actor/logits/kernel"]]
    bs = [z["actor/dense1/bias"], z["actor/dense2/bias"], z["actor/logits/bias"]]
    return {"dense_params": int(sum(w.size for w in Ws) + sum(b.size for b in bs)),
            "nonzero_params": int(sum(np.count_nonzero(w) for w in Ws) + sum(np.count_nonzero(b) for b in bs)),
            "mac_dense": int(sum(w.size for w in Ws)),
            "mac_nonzero": int(sum(np.count_nonzero(w) for w in Ws)),
            "inputs_used": int((np.abs(Ws[0]).sum(1) > 0).sum()),
            "units_used": [int((np.abs(Ws[0]).sum(0) > 0).sum()), int((np.abs(Ws[1]).sum(0) > 0).sum())],
            "layers": [600, 32, 32, 6],
            "w_nnz": [int(np.count_nonzero(w)) for w in Ws]}


def opus(game):
    m = TracrModel(f"runs/opus55_minatar_{game}/final/model.npz")
    meta, st = m.meta, m.meta["stats"]
    D, H, K, L, M = m.D, meta["num_heads"], meta["key_size"], meta["num_layers"], meta["mlp_hidden_size"]
    mac_dense = L * (4 * D * H * K * T + 2 * H * T * T * K + 2 * D * M * T)
    mac_nz, heads = 0, 0
    for lay in m.layers:
        for h in lay["heads"]:
            heads += 1
            mac_nz += T * sum(int(np.count_nonzero(h[x])) for x in ("q", "k", "v", "o"))
            mac_nz += T * T * (h["q"].shape[1] + h["v"].shape[1])
        mac_nz += T * (int(np.count_nonzero(lay["W1"])) + int(np.count_nonzero(lay["W2"])))
    return {"dense_params": st["dense_params"], "nonzero_params": st["nonzero_params"], "mac_dense": int(mac_dense),
            "mac_nonzero": int(mac_nz), "layers": L, "residual": D, "heads": heads, "key_size": K, "mlp_max": M,
            "positions": T}


def main(path):
    out = {}
    for g in ("breakout", "seaquest", "asterix"):
        a, o = astra(g), opus(g)
        out[g] = {"astra": a, "opus": o}
        print(f"{g}: params {a['dense_params']:,} vs {o['dense_params']:,} (x{o['dense_params'] / a['dense_params']:.0f}); "
              f"nonzero {a['nonzero_params']:,} vs {o['nonzero_params']:,} (x{o['nonzero_params'] / a['nonzero_params']:.1f}); "
              f"MACs nonzero {a['mac_nonzero']:,} vs {o['mac_nonzero']:,} (x{o['mac_nonzero'] / a['mac_nonzero']:.0f}); "
              f"MACs dense {a['mac_dense']:,} vs {o['mac_dense']:,}")
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "docs/exp5_page/arch_compare.json")
