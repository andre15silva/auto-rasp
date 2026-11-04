In nearly every case the group was already in atari on our previous turn. Let me determine whether a real save existed at that moment (extend to ≥2 liberties, or capture an adjacent attacker) and what we played instead.

```python
import json, numpy as np, sys
sys.path.insert(0,'/work')
import goref
g = json.load(open('/work/pass_7/games.json'))
boards = np.load('/work/pass_7/boards.npy'); valid = np.load('/work/pass_7/valid.npy')
rep = []
for i, x in enumerate(g):
    if x['opponent'] != 'strong': continue
    me = 1 if x['net_color']=='black' else -1
    for p in range(2, int(valid[i].sum())):
        dead = np.nonzero((boards[i][p-1] == me) & (boards[i][p] == 0))[0]
        if len(dead) < 3: continue
        b = [0 if v == 0 else (1 if v == me else 2) for v in boards[i][p-2]]   # before our move at ply p-1
        d0 = int(dead[0])
        if b[d0] != 1: continue
        grp, libs = goref.group(b, d0)
        if len(libs) != 1: continue
        lib = next(iter(libs))
        saves = []
        # extension at the liberty
        r = goref.play(b, lib, 1)
        if r is not None:
            nb, cap, _ = r
            g2, l2 = goref.group(nb, lib)
            if len(l2) >= 2: saves.append(('extend', lib, len(l2)))
        # capture adjacent opponent group in atari
        adjo = set()
        for s_ in grp:
            for k in goref.NBR[s_]:
                if b[k] == 2:
                    go_, lo_ = goref.group(b, k)
                    if len(lo_) == 1: adjo |= lo_
        for c in adjo:
            if goref.play(b, c, 1) is not None: saves.append(('capture', c))
        mv = x['moves'][p-1]
        rep.append((i, p, len(dead), saves, mv['move'], mv.get('top5')[:3]))
for r_ in rep: print(r_)
```