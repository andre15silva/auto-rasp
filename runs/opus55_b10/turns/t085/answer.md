The pass logit varies (41.8 / 36.5 / 34.8): index 81 (the side token) is not a run start anymore (its fetched left/up token is itself), so it joins position 80's run and picks up region flags. Easy fix. Let me now check liberty-class accuracy, region classification, cuts and phase against exact Go-rule computations.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
import goref, go
d = np.load('/work/pass_6/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_6/inputs.json'))
keys = list(d.keys())
def K(prefix): return [k for k in keys if k.startswith(prefix)][0]
cst = d[K('cst')]; region = d[K('region')]; cuts = d[K('cuts')]; phase = d[K('phase')]
def lc(a,b):
    if a==0 or b==0: return 0
    if a==1 and b==1: return 1
    if a>=3 or b>=3: return 3
    return 2
conf = {}; tot=0
reg_conf = {}; cut_bad = 0; cut_tot = 0; ph_bad = 0
for n,pos in enumerate(inp):
    board = goref.from_strings(pos['board']); toks = pos['tokens']
    me = 1 if pos['to_move']=='black' else 2
    nst = sum(1 for v in board if v)
    exp_ph = 0 if nst <= 12 else (1 if nst <= 33 else 2)
    if int(phase[n][0]) != exp_ph: ph_bad += 1
    # regions
    seen = {}
    for i in range(81):
        if board[i] == 0 and i not in seen:
            st=[i]; comp={i}; border=set()
            while st:
                j=st.pop()
                for k in goref.NBR[j]:
                    if board[k]==0 and k not in comp: comp.add(k); st.append(k)
                    elif board[k]: border.add('x' if board[k]==me else 'o')
            for j in comp: seen[j] = (int('x' in border), int('o' in border), len(comp))
    for i in range(81):
        if board[i]:
            g, libs = goref.group(board, i)
            rows={l//9 for l in libs}; cols={l%9 for l in libs}
            e = lc(min(3,len(rows)), min(3,len(cols)))
            got = cst[n][i]; gl = int(got[1]) if got[0] in 'XO' else -1
            conf[(e,gl)] = conf.get((e,gl),0)+1
        else:
            ex = seen[i][:2]; gr = tuple(int(v) for v in str(region[n][i]).strip('()').split(','))
            key = (ex, gr, 'big' if seen[i][2] > 12 else 'small')
            reg_conf[key] = reg_conf.get(key, 0) + 1
            # cuts
            r, c = divmod(i, 9)
            def t(rr, cc):
                if 0<=rr<9 and 0<=cc<9: return toks[rr*9+cc]
                return 'N'
            ec = set()
            for (a,b,dg) in [((r-1,c),(r,c+1),(r-1,c+1)),((r-1,c),(r,c-1),(r-1,c-1)),((r+1,c),(r,c+1),(r+1,c+1)),((r+1,c),(r,c-1),(r+1,c-1))]:
                A, B, D = t(*a), t(*b), t(*dg)
                if A=='x' and B=='x' and D=='o': ec.add('our')
                if A=='o' and B=='o' and D=='x': ec.add('their')
            gc = cuts[n][i]
            gcs = set(x.strip(" '") for x in str(gc).strip('()').split(',') if x.strip(" '"))
            cut_tot += 1
            if gcs != ec: cut_bad += 1
print('liberty class confusion (exp, got):', sorted(conf.items()))
print('phase mismatches', ph_bad)
print('cut mismatches', cut_bad, 'of', cut_tot)
for k in sorted(reg_conf): print('region exp/got/size', k, reg_conf[k])
```