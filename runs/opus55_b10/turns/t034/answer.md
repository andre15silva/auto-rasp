Now 28 layers, max 4 heads, 122M params, ~31 s/1000 positions, compile 100 s — within limits. Before a second verification pass, let me add some structured test positions with big, winding groups (to probe diffusion coverage and leak), keeping the original 76 for comparison.

```python
import sys, json, random
sys.path.insert(0,'/work')
import goref
prev = json.load(open('/work/pass1_positions.json'))
positions = list(prev['positions'])
rng = random.Random(7)
def cluster_board(rng, nwalks, steps):
    b = [0]*81
    for w in range(nwalks):
        col = 1 + (w % 2)
        p = rng.randrange(81)
        for s in range(steps):
            if b[p] == 0: b[p] = col
            r, c = divmod(p, 9)
            dr, dc = rng.choice([(0,1),(0,-1),(1,0),(-1,0)])
            r = min(8, max(0, r+dr)); c = min(8, max(0, c+dc)); p = r*9+c
    # remove groups without liberties
    changed = True
    while changed:
        changed = False
        for i in range(81):
            if b[i]:
                g, l = goref.group(b, i)
                if not l:
                    for s_ in g: b[s_] = 0
                    changed = True
    return b
extra = []
for k in range(24):
    b = cluster_board(rng, rng.choice([4,6,8,10]), rng.choice([8,12,16,20]))
    extra.append({"board": goref.to_strings(b), "to_move": rng.choice(["black","white"])})
positions += extra
json.dump({'positions': positions}, open('/work/pass2_positions.json','w'))
req = {"positions": positions, "activations": True, "rasp": False}
txt = json.dumps(req, separators=(',',':'))
print(len(positions), len(txt))
print(json.dumps({"positions": extra, "activations": True, "rasp": False}, separators=(',',':'))[:200])
# sizes of groups in extra
for e in extra[:24]:
    b = goref.from_strings(e['board']); seen=set(); sizes=[]
    for i in range(81):
        if b[i] and i not in seen:
            g,l = goref.group(b,i); seen|=g; sizes.append((len(g),len(l)))
    print(sorted(sizes, reverse=True)[:5], end=' | ')
```