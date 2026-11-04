"""The two pass tools (the only ways the writer's network is ever run before the evaluation).

games pass:     {"games": {"strong": 64, "weak": 32, "random": 32}} -> plays up to 128 games of the compiled
                network against practice opponents.
positions pass: {"positions": [{"board": [...9 strings...], "to_move": "black"|"white"} | {"moves": [...]}, ...],
                 "activations": bool, "rasp": bool} -> runs the compiled network on up to 256 positions.
Every pass compiles /work/program.py afresh in the sandbox (cached by source hash), exactly as the final
evaluation does. A request that fails (bad JSON, compile error) is not counted.
"""
import hashlib
import json
import os
import shutil
import time

import numpy as np

from gorasp import go, opponents
from gorasp.play import play, summary
from gorasp.policies import masked_probs
from gorasp.tracr_policy import TracrModel, TracrPolicy

from . import sandbox

GAMES_README = ("games.json: one entry per game (opponent, net_color, result +1/-1, margin = net's area score minus "
                "the opponent's incl. komi, end, stones captured / lost, moves: ply, by, move (row*9+col, 81 = pass), "
                "and for the network's moves its top-5 [move, probability]). boards.npy: (games, 162, 81) int8, the "
                "board AFTER each ply (1 Black, -1 White, 0 empty; index row*9+col); valid.npy: (games, 162) which "
                "plies were played.")
POSITIONS_README = ("inputs.json: the positions as given, each with its board (9 strings: X Black, O White), "
                    "to_move and its 82 input tokens (after BOS); legal.npy (n, 82) bool; logits.npy (n, 82): the "
                    "network's output at positions 1..82 (move row*9+col, 81 = pass); probs.npy (n, 82): softmax over "
                    "the legal moves. compiled.npz (if activations): for every SOp of your program, keyed by its "
                    "label, its value at each of the 82 input positions as read from the compiled network's residual "
                    "stream (numerical SOps: their coordinate; categorical SOps: the value whose dimension is "
                    "largest), plus 'residual' (n, 83, D) when D <= 2048 and 'residual_labels'. rasp.npz (if rasp): "
                    "rasp.evaluate's value of every SOp on the same inputs ('None' / nan where RASP gives None).")


def source_hash(work_dir):
    h = hashlib.sha256()
    for root, _, files in sorted(os.walk(work_dir)):
        if os.path.basename(root).startswith("pass_"):
            continue
        for f in sorted(files):
            if f.endswith(".py"):
                p = os.path.join(root, f)
                h.update(os.path.relpath(p, work_dir).encode())
                h.update(open(p, "rb").read())
    return h.hexdigest()[:16]


def snapshot_sources(work_dir, dest):
    for root, _, files in os.walk(work_dir):
        if os.path.basename(root).startswith("pass_"):
            continue
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                q = os.path.join(dest, os.path.relpath(p, work_dir))
                os.makedirs(os.path.dirname(q), exist_ok=True)
                shutil.copy(p, q)


def compile_current(run_dir, rasp_inputs=None):
    """Compiles the writer's current /work/program.py; returns (compile.json dict, model.npz path, out dir)."""
    work = os.path.join(run_dir, "work")
    key = source_hash(work)
    out = os.path.join(run_dir, "compiled", key)
    if rasp_inputs is not None:  # positions with RASP reference values: a fresh folder per request
        out = os.path.join(run_dir, "compiled", f"{key}_rasp_{int(time.time())}")
    cj = os.path.join(out, "compile.json")
    if rasp_inputs is None and os.path.exists(cj) and json.load(open(cj)).get("ok"):
        return json.load(open(cj)), os.path.join(out, "model.npz"), out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    snapshot_sources(work, os.path.join(out, "src"))
    res = sandbox.compile_in_sandbox(work, out, rasp_inputs=rasp_inputs)
    return res, os.path.join(out, "model.npz"), out


def _compile_error(res):
    return {"ok": False, "error": "your program could not be compiled, so nothing was run (this pass is not "
                                  "counted):\n" + res.get("error", "")}


def games_pass(req, run_dir, k, seed):
    g = req.get("games") if isinstance(req, dict) else None
    prac = opponents.practice()
    if not isinstance(g, dict) or not g:
        return {"ok": False, "error": 'expected {"games": {"strong": 64, "weak": 32, "random": 32}}'}
    for name, n in g.items():
        if name not in prac:
            return {"ok": False, "error": f"unknown opponent {name!r}; choose from {sorted(prac)}"}
        if not isinstance(n, int) or n <= 0 or n % 2:
            return {"ok": False, "error": f"the number of games against {name} must be a positive even integer"}
    if sum(g.values()) > 128:
        return {"ok": False, "error": "at most 128 games in total"}
    res, model_path, _ = compile_current(run_dir)
    if not res.get("ok"):
        return _compile_error(res)
    pdir = os.path.join(run_dir, "work", f"pass_{k}")
    os.makedirs(pdir, exist_ok=True)
    net = TracrPolicy(model_path)
    net.model.max_rows = 8192
    per, games, boards, valid = {}, [], [], []
    t0 = time.time()
    with sandbox.heavy_lock():
        for j, (name, n) in enumerate(g.items()):
            r = play(net, prac[name], n, seed=seed * 1000 + j, record=True)
            per[name] = summary(r)
            for i in range(n):
                ln = int(r["length"][i])
                moves = []
                for ply in range(ln):
                    by = "net" if (ply % 2 == 0) == bool(r["net_black"][i]) else "opponent"
                    e = {"ply": ply, "by": by, "move": int(r["moves"][i, ply])}
                    if by == "net":
                        e["top5"] = r["tops"].get((i, ply), [])
                    moves.append(e)
                games.append({"opponent": name, "net_color": "black" if r["net_black"][i] else "white",
                              "result": int(r["result"][i]), "margin": float(r["margin"][i]), "end": str(r["end"][i]),
                              "captured": int(r["captured"][i]), "lost": int(r["lost"][i]), "moves": moves})
                boards.append(r["boards"][i])
                valid.append(np.arange(go.MAX_PLIES) < ln)
    secs = time.time() - t0
    json.dump(games, open(os.path.join(pdir, "games.json"), "w"))
    np.save(os.path.join(pdir, "boards.npy"), np.array(boards, np.int8))
    np.save(os.path.join(pdir, "valid.npy"), np.array(valid, bool))
    out = {"ok": True, "pass": k, "kind": "games", "per_opponent": per, "network": res["stats"],
           "seconds_per_1000_positions": res.get("seconds_per_1000_positions"), "seconds": round(secs, 1),
           "files": f"/work/pass_{k}/", "readme": GAMES_README}
    json.dump(out, open(os.path.join(pdir, "summary.json"), "w"), indent=1)
    open(os.path.join(pdir, "README.txt"), "w").write(GAMES_README + "\n")
    return out


def _parse_positions(plist):
    boards, colors, legal, info = [], [], [], []
    for i, p in enumerate(plist):
        if not isinstance(p, dict):
            raise ValueError(f"position {i}: expected an object")
        if "moves" in p:
            g, ok, msg = go.replay(p["moves"])
            if not ok:
                raise ValueError(f"position {i}: {msg}")
            b, c, lg = g.board[0], int(g.color[0]), g.legal()[0]
        elif "board" in p:
            b = go.board_from_strings(p["board"])
            tm = p.get("to_move")
            if tm not in ("black", "white"):
                raise ValueError(f'position {i}: "to_move" must be "black" or "white"')
            c = 0 if tm == "black" else 1
            lg = np.append(b == 0, True)  # empty points and pass (suicide and ko not checked)
        else:
            raise ValueError(f'position {i}: give "board" + "to_move" or "moves"')
        boards.append(b)
        colors.append(c)
        legal.append(lg)
        info.append({"board": go.board_to_strings(b), "to_move": "black" if c == 0 else "white",
                     **({"moves": p["moves"]} if "moves" in p else {})})
    return np.array(boards, np.int8), np.array(colors), np.array(legal, bool), info


def _mv(m):
    return "pass" if m == go.PASS else f"{m} ({m // 9},{m % 9})"


def positions_pass(req, run_dir, k):
    plist = req.get("positions") if isinstance(req, dict) else None
    if not isinstance(plist, list) or not plist:
        return {"ok": False, "error": 'expected {"positions": [...], "activations": true/false}'}
    if len(plist) > 256:
        return {"ok": False, "error": "at most 256 positions"}
    try:
        boards, colors, legal, info = _parse_positions(plist)
    except (ValueError, AssertionError, KeyError, TypeError) as e:
        return {"ok": False, "error": str(e)}
    toks = go.tokens(boards, colors)
    want_rasp = bool(req.get("rasp", False))
    res, model_path, cdir = compile_current(run_dir, rasp_inputs=toks.tolist() if want_rasp else None)
    if not res.get("ok"):
        return _compile_error(res)
    pdir = os.path.join(run_dir, "work", f"pass_{k}")
    os.makedirs(pdir, exist_ok=True)
    with sandbox.heavy_lock():
        tm = TracrModel(model_path, max_rows=8192)
        resid = tm.residual(tm.encode(toks))
    logits = resid[:, 1:, tm.out_index]
    probs = masked_probs(logits, legal)
    for i, row in enumerate(toks):
        info[i]["tokens"] = list(row)
    json.dump(info, open(os.path.join(pdir, "inputs.json"), "w"))
    np.save(os.path.join(pdir, "legal.npy"), legal)
    np.save(os.path.join(pdir, "logits.npy"), logits.astype(np.float32))
    np.save(os.path.join(pdir, "probs.npy"), probs.astype(np.float32))
    if req.get("activations", False):
        dec = tm.decode(resid)
        arrays = {name: (v[:, 1:].astype(np.float32) if v.dtype != object else v[:, 1:].astype(str))
                  for name, v in dec.items()}
        arrays["residual_labels"] = np.array(tm.labels)
        if tm.D <= 2048:
            arrays["residual"] = resid.astype(np.float32)
        np.savez_compressed(os.path.join(pdir, "compiled.npz"), **arrays)
    if want_rasp and os.path.exists(os.path.join(cdir, "rasp.npz")):
        shutil.copy(os.path.join(cdir, "rasp.npz"), os.path.join(pdir, "rasp.npz"))
    top = []
    for i in range(len(toks)):
        order = np.argsort(-probs[i])[:3]
        top.append(f"#{i} {info[i]['to_move']} to move: " + ", ".join(
            f"{_mv(int(m))} p={probs[i, m]:.3f} logit={logits[i, m]:.3f}" for m in order if probs[i, m] > 0))
    out = {"ok": True, "pass": k, "kind": "positions", "n": len(toks), "network": res["stats"],
           "files": f"/work/pass_{k}/", "readme": POSITIONS_README}
    json.dump(out, open(os.path.join(pdir, "summary.json"), "w"), indent=1)
    out["top3"] = top
    return out
