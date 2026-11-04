Leak grows roughly linearly with rounds (max 1e-4 after round 1 → 4e-4 after round 6), while undercounts come from very large groups not fully covered. Plan: add per-round cleaning x←relu(x−θ) via a SequenceMap with a "near-one" constant (θ≈1e-4, obtained from BOS's share in an attention over 40 keys), which prevents leak accumulation, and lower the decode threshold. First, let me verify the rest of the pipeline (fetch/combine/tactical and positional tables) is exact given the network's own stone categories.

```python
import numpy as np, json, sys, importlib
sys.path.insert(0,'/work')
import goref, go
importlib.reload(go)
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
keys = list(d.keys())
def K(prefix): return [k for k in keys if k.startswith(prefix)][0]
cst = d[K('cst')]; tcat = d[K('tcat')]; pcat = d[K('pcat')]; logit = np.load('/work/pass_2/logits.npy')
bad_t = 0; bad_p = 0; bad_l = 0; tot = 0
for n,pos in enumerate(inp):
    toks = pos['tokens']
    for i in range(82):
        if i < 81:
            r, c = divmod(i, 9)
            nb = []
            for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
                rr, cc = r+dr, c+dc
                nb.append(cst[n][rr*9+cc] if 0<=rr<9 and 0<=cc<9 else 'N')
            exp_t = go.tactic_score(tuple(sorted(nb)))
            hasx = any(toks[j]=='x' for j in go.NB[i]); haso = any(toks[j]=='o' for j in go.NB[i])
            near = [j for j in range(81) if 1 <= go.man(i,j) <= 2]
            ex2 = any(toks[j]=='x' for j in near); eo2 = any(toks[j]=='o' for j in near)
            exp_p = go.pos_score(int(ex2), int(eo2), int(hasx), int(haso), go.line_of(i))
        else:
            exp_t = 0.0; exp_p = go.PASS_LOGIT
        tot += 1
        if abs(float(tcat[n][i]) - exp_t) > 1e-6: bad_t += 1
        if abs(float(pcat[n][i]) - exp_p) > 1e-6:
            bad_p += 1
            if bad_p < 4: print('pos mismatch', n, i, pcat[n][i], exp_p)
        if abs(logit[n][i] - (exp_t + exp_p + go.T_OFF + go.P_OFF)) > 0.01:
            bad_l += 1
            if bad_l < 4: print('logit mismatch', n, i, logit[n][i], exp_t + exp_p + go.T_OFF + go.P_OFF)
print('total', tot, 'tcat mismatches', bad_t, 'pcat mismatches', bad_p, 'logit mismatches', bad_l)
```