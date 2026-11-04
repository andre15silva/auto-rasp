```python
import sys, json, random
sys.path.insert(0,'/work')
import goref
rng = random.Random(12345)
positions = []
meta = []
for L in [15, 30, 45, 60, 75, 90, 105, 120, 135, 150]:
    for rep in range(6):
        mv, b, col = goref.random_game(L, rng)
        positions.append({"board": goref.to_strings(b), "to_move": "black" if col == 1 else "white"})
        meta.append(('rand', L))
crafted = [
 # snake X group with single liberty at (8,8); O fills around
 (["XXXXXXXXO","OOOOOOOXO","XXXXXXOXO","XOOOOXOXO","XOXXOXOXO","XOXOOXOXO","XOXXXXOXO","XOOOOOOXO","XXXXXXXX."], "white"),
 (["XXXXXXXXO","OOOOOOOXO","XXXXXXOXO","XOOOOXOXO","XOXXOXOXO","XOXOOXOXO","XOXXXXOXO","XOOOOOOXO","XXXXXXXX."], "black"),
 # O group two liberties far apart
 ([".OOOOOOOX","XXXXXXXOX","........X","XXXXXXXX.",".........",".........",".........",".........","........."], "black"),
 ([".OOOOOOOX","XXXXXXXOX","........X","XXXXXXXX.",".........",".........",".........",".........","........."], "white"),
 # simple atari captures / saves
 ([".........",".........","...X.....","..XO.....","...X.....",".........",".........",".........","........."], "black"),
 ([".........",".........","...X.....","..XO.....","...X.....",".........",".........",".........","........."], "white"),
 # eyes
 (["XXXX.....",".X.X.....","XXXX.....",".........","....OOO..","....O.O..","....OOO..",".........","........."], "black"),
 (["XXXX.....",".X.X.....","XXXX.....",".........","....OOO..","....O.O..","....OOO..",".........","........."], "white"),
 # corner ladders / edge
 (["OX.......","X........",".........",".........",".........",".........",".........","........O",".......OX"], "black"),
 (["OX.......","X........",".........",".........",".........",".........",".........","........O",".......OX"], "white"),
 # 2x2 box liberties: O group with libs forming L
 ([".........",".XXXX....","XOOOOX...","XO..OX...","XOO.OX...","XOOOOX...",".XXXX....",".........","........."], "black"),
 ([".........",".XXXX....","XOOOOX...","XO..OX...","XOO.OX...","XOOOOX...",".XXXX....",".........","........."], "white"),
 # empty board
 (["........."]*9, "black"),
 # one stone center
 ([".........",".........",".........",".........","....X....",".........",".........",".........","........."], "white"),
 # spiral X group many turns, liberties only at center
 (["XXXXXXXXX","OOOOOOOOX","XXXXXXXOX","XOOOOOXOX","XOX.XOXOX","XOXXXOXOX","XOOOOOXOX","XXXXXXXOX","OOOOOOOOX"], "white"),
 (["XXXXXXXXX","OOOOOOOOX","XXXXXXXOX","XOOOOOXOX","XOX.XOXOX","XOXXXOXOX","XOOOOOXOX","XXXXXXXOX","OOOOOOOOX"], "black"),
]
for rows, tm in crafted:
    assert all(len(r)==9 for r in rows) and len(rows)==9, rows
    positions.append({"board": rows, "to_move": tm})
    meta.append(('crafted', 0))
json.dump({'positions': positions, 'meta': meta}, open('/work/pass1_positions.json','w'))
req = {"positions": positions, "activations": True, "rasp": False}
txt = json.dumps(req, separators=(',',':'))
print(len(positions), len(txt))
print(txt)
```