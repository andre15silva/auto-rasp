Key finding: Tracr divides attention logits by sqrt(key_size)=sqrt(85) without compensation, so attention has effective coldness ≈10.85 (selected-key weight ≈0.994, each unselected key ≈1.9e-5). Let me measure how this affected the liberty decode by comparing nr/nc/lcls with exact Go-rule values, and by looking at genuine vs. leaked masses in the diffused row states.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
import goref
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_1/inputs.json'))
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
srdims = [i for i,l in enumerate(labels) if l.split(':')[0]=='sr_final_42']
print([labels[i] for i in srdims])
tot = 0; bad_nr = 0; bad_cls = 0; bad_examples = []
gen_masses = []; leak_masses = []
for n, pos in enumerate(inp):
    board = goref.from_strings(pos['board'])
    color = 1 if pos['to_move']=='black' else 2
    for i in range(81):
        if board[i] == 0: continue
        g, libs = goref.group(board, i)
        rows = {l//9 for l in libs}; cols = {l%9 for l in libs}
        enr, enc = min(3,len(rows)), min(3,len(cols))
        def lc(a,b):
            if a==0 or b==0: return 0
            if a==1 and b==1: return 1
            if a>=3 or b>=3: return 3
            return 2
        exp = lc(enr, enc)
        got_nr = int(d['nr_29'][n][i]); got = int(d['lcls_22'][n][i])
        tot += 1
        if got_nr != enr: bad_nr += 1
        if got != exp:
            bad_cls += 1
            if len(bad_examples) < 15: bad_examples.append((n, i, len(g), sorted(libs), exp, got, got_nr, enr))
        v = res[n][1+i][srdims]
        for j, l in enumerate([labels[k] for k in srdims]):
            val = l.split(':')[1]
            if val == 'D': continue
            if int(val) in rows: gen_masses.append(v[j])
            else: leak_masses.append(v[j])
print('stones', tot, 'nr wrong', bad_nr, 'class wrong', bad_cls)
for e in bad_examples: print(e)
gen = np.array(gen_masses); leak = np.array(leak_masses)
print('genuine mass quantiles', np.quantile(gen, [0, 0.001, 0.01, 0.05, 0.5]))
print('leak mass quantiles', np.quantile(leak, [0.5, 0.9, 0.99, 0.999, 1]))
```