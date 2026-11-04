"""Batched games between a subject policy ("net") and an opponent; the net is Black in the first half."""
import numpy as np

from . import go
from .policies import sample


def play(net, opp, n_games, seed, record=False, topk=5, collect=False):
    """collect=True also returns every position the net faced: positions = (boards, colors, legal)."""
    assert n_games % 2 == 0, "n_games must be even"
    rng = np.random.default_rng(seed)
    g = go.Batch(n_games)
    net_black = np.arange(n_games) < n_games // 2
    net_color = np.where(net_black, 0, 1)
    done = np.zeros(n_games, bool)
    net_passes = np.zeros(n_games, int)
    first_pass_ply = np.full(n_games, -1)
    moves = np.full((n_games, go.MAX_PLIES), -1, np.int16)
    boards = np.zeros((n_games, go.MAX_PLIES, go.N_POINTS), np.int8) if record else None
    tops = {} if record else None
    seen = [] if collect else None
    for ply in range(go.MAX_PLIES):
        active = ~done
        if not active.any():
            break
        board, color, legal = g.board, g.color, g.legal()
        net_turn = (color == net_color)
        actions = np.full(n_games, go.PASS, np.int64)
        for who, sel in ((net, active & net_turn), (opp, active & ~net_turn)):
            if sel.any():
                if collect and who is net:
                    seen.append((board[sel], color[sel], legal[sel]))
                z = who.logits(board[sel], color[sel], legal[sel])
                a, p = sample(z, legal[sel], rng)
                actions[sel] = a
                if record and who is net:
                    order = np.argsort(-p, axis=1)[:, :topk]
                    for gi, row, prow in zip(np.flatnonzero(sel), order, p):
                        tops[(int(gi), ply)] = [[int(m), round(float(prow[m]), 4)] for m in row if prow[m] > 0]
        is_net_pass = active & net_turn & (actions == go.PASS)
        net_passes += is_net_pass
        first_pass_ply[is_net_pass & (first_pass_ply < 0)] = ply
        moves[active, ply] = actions[active]
        g.step(actions, active)
        if record:
            boards[:, ply] = g.board
        done = g.terminal()
    rew = g.rewards()
    scores = g.area_scores().astype(float)
    cap = g.captured()
    idx = np.arange(n_games)
    result = rew[idx, net_color]
    margin_black = scores[:, 0] - go.KOMI - scores[:, 1]
    margin = np.where(net_black, margin_black, -margin_black)
    psk = g.is_psk()
    length = g.ply
    end = np.where(psk, "repetition", np.where(g.consecutive_passes() >= 2, "two_passes", "move_limit"))
    out = dict(result=result, margin=margin, net_black=net_black, length=length, end=end,
               captured=cap[idx, net_color], lost=cap[idx, 1 - net_color], net_passes=net_passes,
               first_pass_ply=first_pass_ply, moves=moves)
    if record:
        out["boards"], out["tops"] = boards, tops
    if collect:
        out["positions"] = tuple(np.concatenate([x[i] for x in seen]) for i in range(3))
    return out


def summary(r):
    res, nb = r["result"], r["net_black"]
    return {
        "games": int(len(res)),
        "score": float((res > 0).mean()),
        "wins": int((res > 0).sum()),
        "losses": int((res < 0).sum()),
        "score_as_black": float((res[nb] > 0).mean()),
        "score_as_white": float((res[~nb] > 0).mean()),
        "mean_margin": float(r["margin"].mean()),
        "mean_length": float(r["length"].mean()),
        "stones_captured_per_game": float(r["captured"].mean()),
        "stones_lost_per_game": float(r["lost"].mean()),
        "passes_per_game": float(r["net_passes"].mean()),
        "games_with_a_pass_before_move_60": int(((r["first_pass_ply"] >= 0) & (r["first_pass_ply"] < 60)).sum()),
        "end_two_passes": int((r["end"] == "two_passes").sum()),
        "end_repetition": int((r["end"] == "repetition").sum()),
        "end_move_limit": int((r["end"] == "move_limit").sum()),
    }
