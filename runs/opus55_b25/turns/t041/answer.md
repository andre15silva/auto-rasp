```python
import json, numpy as np
G = json.load(open('/work/pass_4/games.json'))
B = np.load('/work/pass_4/boards.npy')
def board_str(arr):
    ch = {1:'X',-1:'O',0:'.'}
    return [''.join(ch[int(v)] for v in arr[r*9:(r+1)*9]) for r in range(9)]
pos = []
for gi_, ply in [(36,51),(41,71),(31,67),(40,69)]:
    g = G[gi_]
    pos.append({"board": board_str(B[gi_, ply]), "to_move": g['net_color']})
old = [
 {"board": ["XO.......", ".........", "...X.....", "..XOX....", ".........", ".........", ".........", ".......XX", ".......X."], "to_move": "white"},
 {"board": [".........", ".........", ".........", ".........", "....OO...", "...OXXO..", "......O..", "O....O...", "X.O......"], "to_move": "black"},
 {"board": ["OOOOOOOO.", "XXXXXXXX.", "OOOOOOOO.", ".........", ".........", ".........", ".........", ".........", "........."], "to_move": "white"},
 {"board": [".........", "..X......", ".XOX.....", "..O..O...", "..X.XO...", "...XO....", "....O....", ".........", "........."], "to_move": "black"}]
allpos = pos + old
json.dump(allpos, open('/work/test_positions.json','w'))
print(json.dumps({"positions": allpos, "activations": True, "rasp": False}))
```