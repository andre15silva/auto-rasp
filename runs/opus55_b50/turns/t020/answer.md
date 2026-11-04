```python
def board_at(gi, ply): return B[gi, ply]
for gi in [0]:
    for ply in [9, 19, 29, 39, 49, 59, 79, 106]:
        print('ply', ply, 'net is', g[gi]['net_color'])
        print(show2(board_at(gi, ply))); print()
```