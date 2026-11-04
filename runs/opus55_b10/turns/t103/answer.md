Now 81.5M params with ≤3 heads per layer (was 100M). Let me look at the pass-8 losses for remaining failure modes before finalizing.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import goref
g = json.load(open('/work/pass_8/games.json'))
boards = np.load('/work/pass_8/boards.npy'); valid = np.load('/work/pass_8/valid.npy')
st = [x for x in g if x['opponent']=='strong']
for res in [1, -1]:
    sel = [x for x in st if x['result']==res]
    print(res, len(sel), 'cap', np.mean([x['captured'] for x in sel]).round(1), 'lost', np.mean([x['lost'] for x in sel]).round(1), 'margin', np.mean([x['margin'] for x in sel]).round(1))
print(sorted([(x['margin'], x['net_color'], x['lost']) for x in st if x['result'] < 0]))
# missed saves as before
missed = 0; events = 0
for i, x in enumerate(g):
    if x['opponent'] != 'strong' or x['result'] > 0: continue
    me = 1 if x['net_color']=='black' else -1
    for p in range(2, int(valid[i].sum())):
        dead = np.nonzero((boards[i][p-1] == me) & (boards[i][p] == 0))[0]
        if len(dead) < 4: continue
        b = [0 if v == 0 else (1 if v == me else 2) for v in boards[i][p-2]]
        d0 = int(dead[0])
        if b[d0] != 1: continue
        grp, libs = goref.group(b, d0)
        if len(libs) != 1: continue
        events += 1
        lib = next(iter(libs)); saves = []
        r = goref.play(b, lib, 1)
        if r is not None:
            nb, cap, _ = r; g2, l2 = goref.group(nb, lib)
            if len(l2) >= 2: saves.append(('extend', lib, len(l2)))
        for s_ in grp:
            for k in goref.NBR[s_]:
                if b[k] == 2:
                    go_, lo_ = goref.group(b, k)
                    if len(lo_) == 1:
                        c = next(iter(lo_))
                        if goref.play(b, c, 1) is not None: saves.append(('capture', c))
        if saves:
            missed += 1
            mv = x['moves'][p-1]
            print('missed', i, p, len(dead), saves[:3], 'played', mv['move'], mv['top5'][:3])
print('events', events, 'with available save', missed)
```