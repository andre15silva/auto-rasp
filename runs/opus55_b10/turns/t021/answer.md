Now 88M params and 13 s/1000 positions with ≤4 heads per layer. Before spending a pass, let me write an independent Go-rules reference (liberties, captures, legal moves) to generate test positions and to later check the compiled network's activations against what the features should be. I'll also name key SOps so they're identifiable in the activation dumps.

```python
ref = r'''
import random
N = 9
def nbrs(i):
    r, c = divmod(i, 9); out = []
    for dr, dc in ((-1,0),(0,-1),(0,1),(1,0)):
        rr, cc = r+dr, c+dc
        if 0 <= rr < 9 and 0 <= cc < 9: out.append(rr*9+cc)
    return out
NBR = [nbrs(i) for i in range(81)]
def group(board, i):
    col = board[i]; st = [i]; seen = {i}; libs = set()
    while st:
        j = st.pop()
        for k in NBR[j]:
            if board[k] == 0: libs.add(k)
            elif board[k] == col and k not in seen:
                seen.add(k); st.append(k)
    return seen, libs
def play(board, move, color, ko=None):
    """returns (newboard, captured_list, new_ko) or None if illegal. color 1=black 2=white"""
    if board[move] != 0 or move == ko: return None
    b = list(board); b[move] = color; opp = 3 - color; cap = []
    for k in NBR[move]:
        if b[k] == opp:
            g, l = group(b, k)
            if not l:
                for s in g: b[s] = 0
                cap.extend(g)
    g, l = group(b, move)
    if not l: return None
    newko = None
    if len(cap) == 1 and len(g) == 1 and len(l) == 1:
        newko = cap[0]
    return b, cap, newko
def legal_moves(board, color, ko=None):
    return [m for m in range(81) if play(board, m, color, ko) is not None]
def random_game(nmoves, rng, avoid_eyes=True):
    board = [0]*81; color = 1; ko = None; moves = []
    hist = {tuple(board)}
    for t in range(nmoves):
        lm = legal_moves(board, color, ko)
        if avoid_eyes:
            lm2 = [m for m in lm if not all(board[k] == color for k in NBR[m])]
            if lm2: lm = lm2
        rng.shuffle(lm)
        done = False
        for m in lm:
            nb, cap, nko = play(board, m, color, ko)
            if tuple(nb) in hist: continue
            board, ko = nb, nko; hist.add(tuple(board)); moves.append(m); done = True
            break
        if not done:
            moves.append('pass'); ko = None
        color = 3 - color
    return moves, board, color
def board_from_moves(moves):
    board = [0]*81; color = 1; ko = None
    for m in moves:
        if m == 'pass': ko = None
        else:
            board, cap, ko = play(board, m, color, ko)
        color = 3 - color
    return board, color, ko
def to_strings(board):
    ch = {0: '.', 1: 'X', 2: 'O'}
    return [''.join(ch[board[r*9+c]] for c in range(9)) for r in range(9)]
def from_strings(rows):
    m = {'.': 0, 'X': 1, 'O': 2}
    return [m[rows[r][c]] for r in range(9) for c in range(9)]
def tokens(board, color):
    return [('.' if v == 0 else ('x' if v == color else 'o')) for v in board] + ['B' if color == 1 else 'W']
'''
open('/work/goref.py','w').write(ref)

# name key SOps in go.py
s = open('/work/go.py').read()
s = s.replace("    lcls = smap(lclass, nr, nc)", "    lcls = smap(lclass, nr, nc).named('lcls')")
s = s.replace("    cst = smap(catf, lcls, tok)", "    cst = smap(catf, lcls, tok).named('cst')")
s = s.replace("    tcat = smap(lambda t, e: tactic_score(msum(t, (e,))) + T_OFF, tW, cE)", "    tcat = smap(lambda t, e: tactic_score(msum(t, (e,))) + T_OFF, tW, cE).named('tcat')")
s = s.replace("    pcat = smap(lambda e, a: pfin(e, a) + P_OFF, e2, adjl)", "    pcat = smap(lambda e, a: pfin(e, a) + P_OFF, e2, adjl).named('pcat')")
s = s.replace("""    nr = decode_distinct(sr, 9)
    nc = decode_distinct(sc, 9)""", """    sr = sr.named('sr_final'); sc = sc.named('sc_final')
    nr = decode_distinct(sr, 9).named('nr')
    nc = decode_distinct(sc, 9).named('nc')""")
s = s.replace("    pNS = smap(", "    cN = cN.named('cN'); cS = cS.named('cS'); cW = cW.named('cW'); cE = cE.named('cE')\n    pNS = smap(")
s = s.replace("    ridr = rasp.SelectorWidth(rasp.Select(ksr, idx, LEQ))", "    ridr = rasp.SelectorWidth(rasp.Select(ksr, idx, LEQ)).named('ridr')")
s = s.replace("    ridc = rasp.SelectorWidth(rasp.Select(ksc, qA, LEQ))", "    ridc = rasp.SelectorWidth(rasp.Select(ksc, qA, LEQ)).named('ridc')")
s = s.replace("    return add(tact, pos)", "    return add(tact, pos).named('logit')")
open('/work/go.py','w').write(s)
import sys; sys.path.insert(0,'/work')
import importlib, go; importlib.reload(go)
p = go.program()
print(p.label)
import goref, random
rng = random.Random(1)
mv, b, col = goref.random_game(60, rng)
print(goref.to_strings(b), col, len(mv))
```