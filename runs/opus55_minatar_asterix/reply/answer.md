## Design

**Strategy.** The policy does a one-step lookahead with risk scoring for each of the 5 distinct moves. It relies on three facts from the game source:

1. Each row holds at most one entity, because slot *i* is always row *i*+1.
2. Entities only move horizontally.
3. The trail cell sits directly behind the entity.

So an entity at distance *d* in the target row is approaching the target cell **iff the cell next to it on the target's side is not a trail cell**. Entities at the edge with no visible trail are handled correctly by the same rule.

For each action, the target cell T is the player position plus the move. Moves blocked by a wall, and `fire`, are treated as no-op. The score for T is:

- **Base value:** 60 if T is safe. It is 0 if T holds an enemy, which means certain death. It is +20 if T holds gold, which is an immediate reward.
- **Enemies approaching T at distance 1 / 2 / 3:** −30 / −10 / −4. These are conservative, because the move timer can't be observed.
- **Gold approaching T at distance 1 / 2 / 3:** +8 / +3 / +1.
- **Gold-seeking:** a bonus when gold lies in the move's direction. Vertical moves count gold in any row above or below. Horizontal moves count gold in the player's own row. The bonus is +4 for near gold, +3 for medium distance and +2 for any distance, and these add up.
- **Edge penalties:** −5 for target columns 0/9 and −2 for columns 1/8, because enemies spawn there. −1 for rows 1/8, which leave fewer escape routes.

**What the RASP program computes.**

1. **Per-cell maps:** row, column, cell class (enemy / gold / trail / none), a player flag, a gold flag, and the action id.
2. **Player position:** one attention head broadcasts the player's row and column to every position.
3. **Per-cell keys and effective action:** each cell gets a relative-position code for a 9×3 window around the player (−1 outside it), and a gold-direction key. Each action token gets its "effective action", with blocked moves and `fire` mapped to no-op.
4. **Neighbour lookups:** 7 attention heads let each action token fetch the class of T and of T±1, T±2 and T±3. These are categorical aggregates that select exactly one cell; off-grid cells give "none".
5. **Gold-seeking heads:** 3 heads detect whether any gold matches the action's direction and distance bucket.
6. **Scoring:** categorical pair-maps turn the lookups into approach / danger codes. These become non-negative numerical terms, which are summed exactly with `LinearSequenceMap` trees: positive terms minus penalty terms.

**Compiler-related choices.**

- All query and key spaces are kept small; the largest is about 29 dimensions. This keeps the attention sharp after Tracr's 1/√key_size scaling, with an effective coldness of about 18.6.
- It also keeps every categorical aggregate's output smaller than key_size.
- Every aggregate is categorical, so there is no fractional averaging.
- Categorical→numerical maps only output values ≥ 0, because the compiled MLP has a ReLU.
- Numerical value sets stay tiny.

```python
from tracr.rasp import rasp

MLP_EXACTNESS = 100

# cell classes
C_N, C_R, C_G, C_E = 0, 1, 2, 3
# effective action -> (dx, dy) of the target cell
OFFS = {0: (0, 0), 1: (-1, 0), 2: (0, -1), 3: (1, 0), 4: (0, 1)}
WX = 4  # half width of the relative window (dx in [-4, 4], dy in [-1, 1])

BASE = 60
GOLD_HERE = 20
PEN = {1: 30, 2: 10, 3: 4}     # enemy approaching target at distance d
BON = {1: 8, 2: 3, 3: 1}       # gold approaching target at distance d
GOLD_SEEK = {1: 4, 2: 3, 3: 2}  # near / mid / any gold in move direction
DIR_KEY = {1: 30, 2: 10, 3: 40, 4: 20}  # left->L*, up->U*, right->R*, down->D*


def _code(dx, dy):
    return (dx + WX) + (2 * WX + 1) * (dy + 1)


def _cell_class(t):
    if t >= 64:
        return C_N
    if t & 2:
        return C_E
    if t & 4:
        return C_G
    if t & 16:
        return C_R
    return C_N


def _is_player(t):
    return 1 if (t < 64 and (t & 1)) else 0


def _is_gold(t):
    return 1 if (t < 64 and (t & 4)) else 0


def _act(t):
    return t - 64 if t >= 64 else -1


def _eff_h(a, pc):
    if a == 5:
        return 0
    if a == 1 and pc <= 0:
        return 0
    if a == 3 and pc >= 9:
        return 0
    return a


def _eff_v(a, pr):
    if a == 2 and pr <= 1:
        return 0
    if a == 4 and pr >= 8:
        return 0
    return a


def _rel(a, b):
    if -WX <= a <= WX and -1 <= b <= 1:
        return _code(a, b)
    return -1


def _fetch_pred(s):
    def pred(k, q):
        if q not in OFFS:
            return False
        ox, oy = OFFS[q]
        return k == _code(ox + s, oy)
    return pred


def _approach(cnear, cfar):
    # entity at the far cell moves toward the target unless the cell between
    # (or the target itself) is its trail
    if cnear == C_R:
        return 0
    if cfar == C_E:
        return 2
    if cfar == C_G:
        return 1
    return 0


def _base_score(c):
    if c == C_E:
        return 0
    if c == C_G:
        return BASE + GOLD_HERE
    return BASE


def _gold_v(g, d):
    if g != 1:
        return 99
    if d <= -4:
        return -3
    if d <= -2:
        return -2
    if d == -1:
        return -1
    if d == 0:
        return 0
    if d == 1:
        return 1
    if d <= 3:
        return 2
    return 3


def _gold_key(v, x):
    if v == 99:
        return 0
    if v < 0:
        return 10 - v   # 11..13 : gold above
    if v > 0:
        return 20 + v   # 21..23 : gold below
    if x == 0:
        return 0
    ax = abs(x)
    b = 1 if ax <= 2 else (2 if ax <= 5 else 3)
    return (30 if x < 0 else 40) + b  # 31..33 left, 41..43 right


def _gold_pred(maxb):
    def pred(k, q):
        if q not in DIR_KEY:
            return False
        b = DIR_KEY[q]
        return b + 1 <= k <= b + maxb
    return pred


def _tc(pc, a):
    if a not in OFFS:
        return -1
    return pc + OFFS[a][0]


def _tr(pr, a):
    if a not in OFFS:
        return -1
    return pr + OFFS[a][1]


def _col_pen(c):
    if c in (0, 9):
        return 5
    if c in (1, 8):
        return 2
    return 0


def _row_pen(r):
    return 1 if r in (1, 8) else 0


def _num_map(sop, f, name):
    return rasp.numerical(rasp.Map(f, sop)).named(name)


def _lin(a, b, fa, fb, name):
    return rasp.numerical(rasp.LinearSequenceMap(a, b, fa, fb)).named(name)


def _tree_sum(terms, prefix):
    terms = list(terms)
    level = 0
    while len(terms) > 1:
        nxt = []
        for i in range(0, len(terms) - 1, 2):
            nxt.append(_lin(terms[i], terms[i + 1], 1, 1,
                            "%s_%d_%d" % (prefix, level, i)))
        if len(terms) % 2 == 1:
            nxt.append(terms[-1])
        terms = nxt
        level += 1
    return terms[0]


def program():
    tokens = rasp.tokens
    indices = rasp.indices

    # ---- per-position features (MLP) ----
    row = rasp.Map(lambda i: i // 10, indices).named("row")
    col = rasp.Map(lambda i: i % 10, indices).named("col")
    is_player = rasp.Map(_is_player, tokens).named("is_player")
    is_gold = rasp.Map(_is_gold, tokens).named("is_gold")
    cls = rasp.Map(_cell_class, tokens).named("cls")
    act = rasp.Map(_act, tokens).named("act")

    # ---- broadcast player position ----
    sel_player = rasp.Select(is_player, is_player,
                             lambda k, q: k == 1).named("sel_player")
    prow = rasp.Aggregate(sel_player, row).named("prow")
    pcol = rasp.Aggregate(sel_player, col).named("pcol")

    # ---- relative coordinates and effective action ----
    dx = rasp.SequenceMap(lambda c, pc: c - pc, col, pcol).named("dx")
    dy = rasp.SequenceMap(lambda r, pr: r - pr, row, prow).named("dy")
    eff_h = rasp.SequenceMap(_eff_h, act, pcol).named("eff_h")
    eff = rasp.SequenceMap(_eff_v, eff_h, prow).named("eff")
    rel = rasp.SequenceMap(_rel, dx, dy).named("rel")

    # ---- fetch classes of target cell and its horizontal neighbours ----
    fetched = {}
    for s in (0, -1, 1, -2, 2, -3, 3):
        sel = rasp.Select(rel, eff, _fetch_pred(s)).named("sel_cell_%d" % (s + 3))
        fetched[s] = rasp.Aggregate(sel, cls).named("cell_%d" % (s + 3))

    pos_terms = []
    neg_terms = []

    # base value of the target cell (0 = enemy there, bonus for gold there)
    pos_terms.append(_num_map(fetched[0], _base_score, "base"))

    # approaching enemies / gold at distance 1..3 on both sides
    for side in (-1, 1):
        for d in (1, 2, 3):
            near = fetched[side * (d - 1)]
            far = fetched[side * d]
            ap = rasp.SequenceMap(_approach, near, far).named(
                "appr_%d_%d" % (side + 1, d))
            neg_terms.append(_num_map(
                ap, lambda v, w=PEN[d]: w if v == 2 else 0,
                "pen_%d_%d" % (side + 1, d)))
            pos_terms.append(_num_map(
                ap, lambda v, w=BON[d]: w if v == 1 else 0,
                "bon_%d_%d" % (side + 1, d)))

    # ---- gold seeking ----
    gv = rasp.SequenceMap(_gold_v, is_gold, dy).named("gold_v")
    gkey = rasp.SequenceMap(_gold_key, gv, dx).named("gold_key")
    for mb in (1, 2, 3):
        sel = rasp.Select(gkey, eff, _gold_pred(mb)).named("sel_gold_%d" % mb)
        agg = rasp.Aggregate(sel, is_gold).named("gold_dir_%d" % mb)
        pos_terms.append(_num_map(
            agg, lambda v, w=GOLD_SEEK[mb]: w if v == 1 else 0,
            "gold_bonus_%d" % mb))

    # ---- edge penalties (spawn risk / fewer escape routes) ----
    tc = rasp.SequenceMap(_tc, pcol, eff).named("tcol")
    tr = rasp.SequenceMap(_tr, prow, eff).named("trow")
    neg_terms.append(_num_map(tc, _col_pen, "pen_col"))
    neg_terms.append(_num_map(tr, _row_pen, "pen_row"))

    # ---- final logits ----
    spos = _tree_sum(pos_terms, "spos")
    sneg = _tree_sum(neg_terms, "sneg")
    logits = _lin(spos, sneg, 1, -1, "logits")
    return logits
```