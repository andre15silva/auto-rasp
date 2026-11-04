Logits are now exact table values. Let me check liberty classes against exact Go rules, and measure genuine vs. leaked masses in the diffused states.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
import goref
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_2/inputs.json'))
labels = [str(l) for l in d['residual_labels']]
res = d['residual']
keys = list(d.keys())
def K(prefix): return [k for k in keys if k.startswith(prefix)][0]
groups = {}
for i,l in enumerate(labels): groups.setdefault(l.split(':')[0], []).append(i)
srk = K('sr5'); sck = K('sc5')
srd = groups[srk]; scd = groups[sck]
print(srk, [labels[j] for j in srd])
def lc(a,b):
    if a==0 or b==0: return 0
    if a==1 and b==1: return 1
    if a>=3 or b>=3: return 3
    return 2
tot=0; bad=0; ex=[]; gen=[]; leak=[]; exact_bad=0; true_cls_counts = {}
conf = {}
for n,pos in enumerate(inp):
    board = goref.from_strings(pos['board'])
    for i in range(81):
        if board[i]==0: continue
        g, libs = goref.group(board, i)
        rows={l//9 for l in libs}; cols={l%9 for l in libs}
        e = lc(min(3,len(rows)), min(3,len(cols)))
        got = int(d[K('lcls')][n][i])
        tot+=1
        conf[(e,got)] = conf.get((e,got),0)+1
        if got!=e:
            bad+=1
            if len(ex)<12: ex.append((n,i,len(g),len(libs),sorted(rows),sorted(cols),e,got, d[K('nr')][n][i], d[K('nc')][n][i]))
        v = res[n][1+i][srd]
        for j,dd in enumerate(srd):
            val = labels[dd].split(':')[1]
            if val in ('D','Z'): continue
            (gen if int(val) in rows else leak).append(v[j])
print('stones',tot,'bad',bad)
print('confusion (expected,got):', sorted(conf.items()))
for e in ex: print(e)
gen=np.array(gen); leak=np.array(leak)
print('genuine q', np.quantile(gen,[0,0.001,0.01,0.05,0.5]))
print('leak q', np.quantile(leak,[0.5,0.9,0.99,0.999,1]))
```