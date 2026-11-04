Big improvement: 97% of stones now get the right liberty class. Remaining errors are mostly overcounts from leaked mass hovering around the 3e-4 threshold, plus a few undercounts. Let me look at how leak and genuine masses evolve per diffusion round, and inspect the undercount cases.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
import goref
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
keys = list(d.keys())
groups = {}
for i,l in enumerate(labels): groups.setdefault(l.split(':')[0], []).append(i)
def K(prefix): return [k for k in keys if k.startswith(prefix)][0]
names = [K('seed_r')] + [K('sr%d'%k) for k in range(6)]
for nm in names:
    dd = groups[nm]; gen=[]; leak=[]
    for n,pos in enumerate(inp):
        board = goref.from_strings(pos['board'])
        for i in range(81):
            if board[i]==0: continue
            g, libs = goref.group(board, i)
            rows={l//9 for l in libs}
            v = res[n][1+i][dd]
            for j,x in enumerate(dd):
                val = labels[x].split(':')[1]
                if val in ('D','Z'): continue
                (gen if int(val) in rows else leak).append(v[j])
    gen=np.array(gen); leak=np.array(leak)
    print(nm, 'leak q50/99/max', np.round(np.quantile(leak,[0.5,0.99,1]),6), ' genuine(>0) q1/5/50', np.round(np.quantile(gen[gen>1e-6],[0.01,0.05,0.5]),5), 'n_gen<1e-6', int((gen<1e-6).sum()))
# undercount examples
def lc(a,b):
    if a==0 or b==0: return 0
    if a==1 and b==1: return 1
    if a>=3 or b>=3: return 3
    return 2
for n,pos in enumerate(inp):
    board = goref.from_strings(pos['board'])
    for i in range(81):
        if board[i]==0: continue
        g, libs = goref.group(board, i)
        rows={l//9 for l in libs}; cols={l%9 for l in libs}
        e = lc(min(3,len(rows)),min(3,len(cols))); got=int(d[K('lcls')][n][i])
        if got < e:
            print('UNDER', n, i, 'size', len(g), 'libs', sorted(libs), 'exp', e, 'got', got, 'sr5', np.round(res[n][1+i][groups[K('sr5')]],5))
            break
```