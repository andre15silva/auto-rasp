```python
import itertools, math
def man_window(q):
    r, c = divmod(q, 9); on, off = [], 0
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if (dr, dc) == (0, 0) or abs(dr) + abs(dc) > 2: continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < 9 and 0 <= cc < 9: on.append(rr * 9 + cc)
            else: off += 1
    return on, off
offs = sorted(set(man_window(q)[1] for q in range(81)))
print("off counts", offs, {o: sum(1 for q in range(81) if man_window(q)[1]==o) for o in offs})
GRID = [0, 1, 2, 4, 7]
tmpl = []
for E in offs + [12]:
    for X in GRID:
        for O in GRID:
            if X + O + E <= 12: tmpl.append((X, O, E))
print(len(tmpl))
```