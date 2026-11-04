"""Batched 9x9 Go on pgx's own rules engine (the implementation behind pgx.make("go_9x9")).

Rules (as in the paper's Experiment 6): Black first; suicide illegal; simple ko illegal; a move that repeats an
earlier whole-board position ends the game and its maker loses; the game ends after two consecutive passes or
162 moves; area scoring with komi 7.5 (no draws).

We call pgx's Game class directly instead of pgx.make("go_9x9") so that colours are not shuffled between player
ids: here index 0 of rewards / num_captured is always Black and 1 is White.
"""
import jax
import jax.numpy as jnp
import numpy as np
from pgx._src.games.go import Game, _count_scores

SIZE = 9
N_POINTS = 81
PASS = 81
N_ACTIONS = 82
MAX_PLIES = 162
KOMI = 7.5
GAME = Game(size=SIZE, komi=KOMI)
assert GAME.max_termination_steps == MAX_PLIES


def _step_one(s, a, active):
    s2 = GAME.step(s, a)
    return jax.tree_util.tree_map(lambda new, old: jnp.where(active, new, old), s2, s)


_init = jax.jit(jax.vmap(lambda _: GAME.init()))
_step = jax.jit(jax.vmap(_step_one))
_legal = jax.jit(jax.vmap(GAME.legal_action_mask))
_terminal = jax.jit(jax.vmap(GAME.is_terminal))
_rewards = jax.jit(jax.vmap(GAME.rewards))
_scores = jax.jit(jax.vmap(lambda s: _count_scores(s, SIZE)))


class Batch:
    """n games played in lockstep. Finished games are frozen."""

    def __init__(self, n):
        self.n = n
        self.state = _init(jnp.arange(n))

    @property
    def board(self):  # (n, 81) int8: 1 Black, -1 White, 0 empty
        return np.clip(np.asarray(self.state.board), -1, 1).astype(np.int8)

    @property
    def color(self):  # (n,) 0 = Black to move, 1 = White to move
        return np.asarray(self.state.step_count) % 2

    @property
    def ply(self):
        return np.asarray(self.state.step_count)

    def legal(self):  # (n, 82) bool, pass always legal
        return np.asarray(_legal(self.state))

    def terminal(self):
        return np.asarray(_terminal(self.state))

    def step(self, actions, active):
        self.state = _step(self.state, jnp.asarray(actions, jnp.int32), jnp.asarray(active, bool))

    def rewards(self):  # (n, 2): +1/-1 for (Black, White) once terminal
        return np.asarray(_rewards(self.state))

    def area_scores(self):  # (n, 2) area score (Black, White), komi not included
        return np.asarray(_scores(self.state))

    def captured(self):  # (n, 2) stones captured BY (Black, White)
        return np.asarray(self.state.num_captured)

    def is_psk(self):
        return np.asarray(self.state.is_psk)

    def consecutive_passes(self):
        return np.asarray(self.state.consecutive_pass_count)


def planes(board, color):
    """The paper's 243-number input: (row*9+col)*3 + plane; plane 0 mover's stones, 1 opponent's, 2 White to move."""
    board = np.asarray(board, np.int8)
    sign = np.where(np.asarray(color) == 0, 1, -1).astype(np.int8)[:, None]
    rel = board * sign
    x = np.zeros((board.shape[0], N_POINTS, 3), np.float32)
    x[:, :, 0] = rel > 0
    x[:, :, 1] = rel < 0
    x[:, :, 2] = (np.asarray(color) == 1)[:, None]
    return x.reshape(board.shape[0], N_POINTS * 3)


def tokens(board, color):
    """Token sequence for the Tracr model (without BOS): 81 points then the colour to move.
    Point tokens are from the mover's point of view: "x" mover's stone, "o" opponent's stone, "." empty.
    Position 81 holds "B" (Black to move) or "W" (White to move); its output is the pass logit."""
    board = np.asarray(board, np.int8)
    sign = np.where(np.asarray(color) == 0, 1, -1).astype(np.int8)[:, None]
    rel = board * sign
    out = np.full((board.shape[0], N_POINTS + 1), ".", dtype="<U1")
    out[:, :N_POINTS][rel > 0] = "x"
    out[:, :N_POINTS][rel < 0] = "o"
    out[:, N_POINTS] = np.where(np.asarray(color) == 0, "B", "W")
    return out


def board_from_strings(rows):
    """9 strings of 9 chars, X = Black, O = White, . = empty -> (81,) int8."""
    assert len(rows) == 9 and all(len(r) == 9 for r in rows), "board must be 9 strings of 9 characters"
    m = {"X": 1, "O": -1, ".": 0}
    return np.array([m[c] for r in rows for c in r.upper()], np.int8)


def board_to_strings(board):
    ch = {1: "X", -1: "O", 0: "."}
    b = np.asarray(board).reshape(9, 9)
    return ["".join(ch[int(v)] for v in row) for row in b]


def replay(moves):
    """Replays a move list (row*9+col or 'pass'/81) from the empty board; returns (Batch of 1, ok, message)."""
    g = Batch(1)
    for k, m in enumerate(moves):
        a = PASS if m in ("pass", PASS) else int(m)
        if g.terminal()[0]:
            return g, False, f"the game is already over before move {k}"
        if not (0 <= a <= PASS) or not g.legal()[0, a]:
            return g, False, f"move {k} ({m}) is illegal"
        g.step([a], [True])
    if g.terminal()[0]:
        return g, False, "the position is terminal (game over)"
    return g, True, ""
