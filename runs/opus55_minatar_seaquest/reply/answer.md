## Design

**Strategy.** The policy is a hand-written reactive heuristic. It is computed relative to the submarine's front cell.

1. **Never step into danger.** For each move, the network looks at the destination cell D. The move is heavily penalised (−30) if any danger (fish, enemy sub or enemy bullet) is at D or horizontally next to it. It is also penalised if an enemy bullet is two cells beside D, because bullets move every step and sticky actions can repeat a now-fatal action. This danger check also covers no-op and fire, which leave the sub where it is.
2. **Shoot.**
   - Fire gets +12 when an enemy is in the sub's row in the direction it faces.
   - Left or right gets +6 when that move turns the sub toward an enemy behind it.
   - Up or down gets +4 when there are enemies in rows above or below.
3. **Divers.** The sub moves toward a diver in its own row, or vertically toward divers above or below. These bonuses are boosted when oxygen is low and the sub carries no diver.
4. **Oxygen and surfacing.** Gauge cell (9,2) is lit only while oxygen is at least 60. Gauge cell (9,8), when oxygen is low, is lit only if the sub carries at least one diver.
   - If oxygen is low and the sub has a diver, it heads up and surfaces.
   - Otherwise, moving up from row 1 is forbidden (−45), since surfacing with no diver is fatal.
   - Moving from row 2 into row 1 is discouraged, so a sticky repeat of "up" cannot surface the sub by accident.
   - In row 0 the sub prefers going down.
5. **Edges.** Moves into column 0 or 9 are discouraged, because enemies spawn there. Moves that would only bump a wall are treated as unsafe.
6. **Default.** With nothing else going on, no-op scores slightly higher than the moves. Fire without a target scores lower.

**What the program computes.** Every selector query, key and value space has at most 57 dimensions. This keeps Tracr's attention sharp: logits of about 13 against about 6.6 for BOS, after the 1/√key_size scaling.

1. **Per-cell maps.** From each token's bits the program computes:
   - whether the cell is the front or back of the sub,
   - whether it holds danger, a bullet, an enemy, a diver or a gauge bit,
   - the cell's row and column, and the action id.
2. **Broadcast (attention).** The front cell's row and column, the back cell's column, and gauge cells 92 and 98 are copied to every position.
3. **Relative position (MLPs).** Each cell computes its offset from the player, (dr clipped to ±2, dc clipped to ±5), as one code `rel`. Each action position builds a query code from the action and the sub's facing. A global context code is built from the row class, column class and oxygen/diver state.
4. **Per-action features (attention).** Four numerical-mean heads, each `Select(rel, query)`, gather the cells relevant to each action:
   - danger near the destination,
   - bullets two cells beside the destination,
   - enemies in the line of fire, the turn direction, or the rows above/below,
   - divers in the move's direction.

   The player's own cell is always selected, so no selection is ever empty.
5. **Thresholds.** Each mean is thresholded to a boolean with `MLP_EXACTNESS = 1000`. Every true mean is at least 1/81, so the cut-off at 0.0047 separates them cleanly.
6. **Logit table.** Categorical SequenceMaps combine (action, danger, enemy, diver) with the global context into an integer logit from a lookup table. A final map turns it into a numerical output, with every logit kept at 0 or above.

```python
from tracr.rasp import rasp

MLP_EXACTNESS = 1000

_DEST = {0: (0, 0), 1: (0, -1), 2: (-1, 0), 3: (0, 1), 4: (1, 0), 5: (0, 0)}


def _dec(k):
  return k // 11 - 2, k % 11 - 5


def _near(k, q, lo, hi):
  if k == 99 or q == 99:
    return False
  r, c = _dec(k)
  if r == 0 and c == 0:
    return True
  dr, dc = _DEST[q // 2]
  return r == dr and lo <= abs(c - dc) <= hi


def _pred_dang(k, q):
  return _near(k, q, 0, 1)


def _pred_b2(k, q):
  return _near(k, q, 2, 2)


def _pred_eline(k, q):
  if k == 99 or q == 99:
    return False
  r, c = _dec(k)
  if r == 0 and c == 0:
    return True
  a, f = q // 2, q % 2
  if a == 5:
    return r == 0 and ((c > 0) if f == 1 else (c < 0))
  if a == 1:
    return f == 1 and r == 0 and c < 0
  if a == 3:
    return f == 0 and r == 0 and c > 0
  if a == 2:
    return r < 0
  if a == 4:
    return r > 0
  return False


def _pred_diver(k, q):
  if k == 99 or q == 99:
    return False
  r, c = _dec(k)
  if r == 0 and c == 0:
    return True
  a = q // 2
  if a == 1:
    return r == 0 and c < 0
  if a == 3:
    return r == 0 and c > 0
  if a == 2:
    return r < 0
  if a == 4:
    return r > 0
  return False


def _logit(acode, gcode):
  a1, a2 = acode // 4, acode % 4
  a, dg = a1 // 2, a1 % 2
  el, dv = a2 // 2, a2 % 2
  g1, osv = gcode // 3, gcode % 3
  prc, pcc = g1 // 5, g1 % 5
  if a > 5:
    return 0
  s = 40
  if a == 0:
    s += 2
  elif a == 5:
    s += 12 if el else -3
  elif a in (1, 3) and el:
    s += 6
  if osv == 1:
    if a == 2:
      if prc == 1:
        s += 25
      elif prc >= 2:
        s += 12
    elif a == 4:
      s -= 6
  else:
    if a in (2, 4) and el:
      s += 4
    if dv:
      b = 4 if a in (1, 3) else (3 if a in (2, 4) else 0)
      if osv == 2 and b > 0:
        b += 7
      s += b
  if a == 2:
    if prc == 0:
      s -= 3
    elif prc == 1 and osv != 1:
      s -= 45
    elif prc == 2 and osv == 0:
      s -= 10
  elif a == 4:
    if prc == 0:
      s += 6
    elif prc == 1 and osv != 1:
      s += 3
    elif prc == 4:
      s -= 35
  elif a == 1:
    if pcc == 0:
      s -= 35
    elif pcc == 1:
      s -= 8
  elif a == 3:
    if pcc == 4:
      s -= 35
    elif pcc == 3:
      s -= 8
  if dg:
    s -= 30
  return max(s, 0)


def _cmap(f, x, name):
  return rasp.categorical(rasp.Map(f, x)).named(name)


def _nmap(f, x, name):
  return rasp.numerical(rasp.Map(f, x)).named(name)


def _cseq(f, x, y, name):
  return rasp.categorical(rasp.SequenceMap(f, x, y)).named(name)


def program():
  tok = rasp.tokens
  idx = rasp.indices

  # per-position maps
  is_front = _cmap(lambda t: 1 if (t < 64 and (t & 1) and not (t & 16)) else 0, tok, "is_front")
  is_back = _cmap(lambda t: 1 if (t < 64 and (t & 1) and (t & 16)) else 0, tok, "is_back")
  gbit = _cmap(lambda t: 1 if (t < 64 and (t & 32)) else 0, tok, "gbit")
  aid = _cmap(lambda t: t - 64 if t >= 64 else 9, tok, "aid")
  row = _cmap(lambda i: i // 10 if i < 100 else 10, idx, "row")
  col = _cmap(lambda i: i % 10 if i < 100 else 10, idx, "col")
  gkey = _cmap(lambda i: 1 if i == 92 else (2 if i == 98 else 0), idx, "gkey")

  v_dang = _nmap(lambda t: 1 if (t < 64 and (t & 2)) else 0, tok, "v_dang")
  v_bul = _nmap(lambda t: 1 if (t < 64 and (t & 2) and not (t & 4)) else 0, tok, "v_bul")
  v_enemy = _nmap(lambda t: 1 if (t < 64 and (t & 2) and (t & 4)) else 0, tok, "v_enemy")
  v_diver = _nmap(lambda t: 1 if (t < 64 and (t & 4) and not (t & 2)) else 0, tok, "v_diver")

  # broadcast player position / gauges
  sel_front = rasp.Select(is_front, is_front, lambda k, q: k == 1)
  sel_back = rasp.Select(is_back, is_front, lambda k, q: k == 1)
  sel_g2 = rasp.Select(gkey, is_front, lambda k, q: k == 1)
  sel_g8 = rasp.Select(gkey, is_front, lambda k, q: k == 2)
  PR = rasp.categorical(rasp.Aggregate(sel_front, row)).named("PR")
  PC = rasp.categorical(rasp.Aggregate(sel_front, col)).named("PC")
  BC = rasp.categorical(rasp.Aggregate(sel_back, col)).named("BC")
  G2 = rasp.categorical(rasp.Aggregate(sel_g2, gbit)).named("G2")
  G8 = rasp.categorical(rasp.Aggregate(sel_g8, gbit)).named("G8")

  # relative coordinates and context
  dr = _cseq(lambda r, p: max(-2, min(2, r - p)) if (r < 10 and p < 10) else 9, row, PR, "dr")
  dc = _cseq(lambda c, p: max(-5, min(5, c - p)) if (c < 10 and p < 10) else 9, col, PC, "dc")
  facing = _cseq(lambda p, b: 1 if b < p else 0, PC, BC, "facing")
  osurf = _cseq(lambda a, b: 0 if a == 1 else (1 if b == 1 else 2), G2, G8, "osurf")
  PRc = _cmap(lambda p: 0 if p == 0 else (1 if p == 1 else (2 if p == 2 else (4 if p >= 8 else 3))), PR, "PRc")
  PCc = _cmap(lambda p: 0 if p == 0 else (1 if p == 1 else (3 if p == 8 else (4 if p >= 9 else 2))), PC, "PCc")

  rel = _cseq(lambda a, b: (a + 2) * 11 + (b + 5) if (a != 9 and b != 9) else 99, dr, dc, "rel")
  qq = _cseq(lambda a, f: a * 2 + f if a < 6 else 99, aid, facing, "qq")
  G1 = _cseq(lambda r, c: r * 5 + c, PRc, PCc, "G1")
  G = _cseq(lambda g, o: g * 3 + o, G1, osurf, "G")

  # per-action feature heads
  def head(pred, val, name):
    return rasp.numerical(
        rasp.Aggregate(rasp.Select(rel, qq, pred), val, default=0)).named(name)

  H_dang = head(_pred_dang, v_dang, "H_dang")
  H_b2 = head(_pred_b2, v_bul, "H_b2")
  H_el = head(_pred_eline, v_enemy, "H_el")
  H_dv = head(_pred_diver, v_diver, "H_dv")

  thr = lambda x: 1 if x > 0.003 else 0
  Dg1 = _cmap(thr, H_dang, "Dg1")
  Db = _cmap(thr, H_b2, "Db")
  El = _cmap(thr, H_el, "El")
  Dv = _cmap(thr, H_dv, "Dv")

  # combine into logits
  Dg = _cseq(lambda x, y: 1 if (x == 1 or y == 1) else 0, Dg1, Db, "Dg")
  A2 = _cseq(lambda e, v: e * 2 + v, El, Dv, "A2")
  A1 = _cseq(lambda a, d: a * 2 + d, aid, Dg, "A1")
  A = _cseq(lambda x, y: x * 4 + y, A1, A2, "A")
  LC = _cseq(_logit, A, G, "LC")
  out = _nmap(lambda v: v, LC, "out")
  return out
```