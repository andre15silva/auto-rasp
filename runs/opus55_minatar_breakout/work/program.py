from tracr.rasp import rasp

MLP_EXACTNESS = 100

LOGIT = 30.0


def _fold(u):
    # MinAtar wall behaviour in unfolded coordinates (clamp + flip => period 20)
    v = u % 20
    return v if v < 10 else 19 - v


def program():
    tokens = rasp.tokens
    indices = rasp.indices

    # ---------------- per-cell features (MLP of layer 0) ----------------
    is_ball = rasp.categorical(
        rasp.Map(lambda t: bool(t < 64 and (t & 8)), tokens)).named("is_ball")
    is_trail = rasp.categorical(
        rasp.Map(lambda t: bool(t < 64 and (t & 16)), tokens)).named("is_trail")
    is_pad = rasp.categorical(
        rasp.Map(lambda t: bool(t < 64 and (t & 1)), tokens)).named("is_pad")
    col = rasp.categorical(rasp.Map(lambda i: i % 10, indices)).named("col")
    row = rasp.categorical(
        rasp.Map(lambda i: min(i // 10, 9), indices)).named("row")
    slot = rasp.categorical(
        rasp.Map(lambda i: "L" if i == 101 else ("R" if i == 103 else "N"),
                 indices)).named("slot")

    # ---------------- broadcast positions (attention of layer 1) ----------------
    sel_ball = rasp.Select(is_ball, col, lambda k, q: bool(k)).named("sel_ball")
    sel_trail = rasp.Select(is_trail, col, lambda k, q: bool(k)).named("sel_trail")
    sel_pad = rasp.Select(is_pad, col, lambda k, q: bool(k)).named("sel_pad")

    bx = rasp.categorical(rasp.Aggregate(sel_ball, col)).named("bx")
    by = rasp.categorical(rasp.Aggregate(sel_ball, row)).named("by")
    tx = rasp.categorical(rasp.Aggregate(sel_trail, col)).named("tx")
    ty = rasp.categorical(rasp.Aggregate(sel_trail, row)).named("ty")
    px = rasp.categorical(rasp.Aggregate(sel_pad, col)).named("px")

    # ---------------- direction inference ----------------
    def e_fn(b, t):
        # horizontal: +-1 if it moved, +-2 if clamped at a wall (or reset)
        if b > t:
            return 1
        if b < t:
            return -1
        return 2 if b == 0 else -2
    e = rasp.SequenceMap(e_fn, bx, tx).named("e")

    def vs_fn(b, t):
        # vertical state: D = moving down, U = moving up, C = just caught (up)
        if b == 8 and t == 8:
            return "C"
        if b > t:
            return "D"
        if b < t:
            return "U"
        if b == 1:
            return "U"
        return "D"
    vs = rasp.SequenceMap(vs_fn, by, ty).named("vs")

    pb = rasp.SequenceMap(lambda p, b: p == b, px, bx).named("pb")
    pslot = rasp.SequenceMap(lambda p, s: (p, s), px, slot).named("pslot")

    def kvs_fn(b, v):
        # number of unfolded horizontal steps until the ball is on row 8
        if v == "D":
            k = 8 - b
        elif b >= 4:
            k = b + 1          # assume bounce off a row-3 brick (earliest case)
        elif b >= 2:
            k = 9 - b          # assume bounce at the current row
        elif b == 1:
            k = 10             # goes to row 0, then the top wall
        else:
            k = 9              # top wall bounce
        k = max(0, min(10, k))
        return (k, v == "C")
    kvs = rasp.SequenceMap(kvs_fn, by, vs).named("kvs")

    epb = rasp.SequenceMap(lambda a, c: (a, bool(c)), e, pb).named("epb")

    def kd_fn(kv, ep):
        k, is_c = kv
        ev, pbv = ep
        d = 1 if ev > 0 else -1
        # reversing catch (paddle under the ball's new column): direction flipped
        if is_c and pbv and abs(ev) == 1:
            d = -d
        return (k, d)
    kd = rasp.SequenceMap(kd_fn, kvs, epb).named("kd")

    # ---------------- target region at the paddle row ----------------
    def reg_fn(b, kdv):
        k, d = kdv
        a = _fold(b + k * d)
        c = _fold(b + (k + 1) * d)
        return (min(a, c), max(a, c))
    reg = rasp.SequenceMap(reg_fn, bx, kd).named("reg")

    # ---------------- action selection per output slot ----------------
    def lg_fn(r, ps):
        lo, hi = r
        p, s = ps
        if p < lo:
            want = "R"
        elif p > hi:
            want = "L"
        else:
            want = "N"
        return want == s
    lg = rasp.SequenceMap(lg_fn, reg, pslot).named("lg")

    out = rasp.numerical(
        rasp.Map(lambda v: LOGIT if v else 0.0, lg)).named("out")
    return out
