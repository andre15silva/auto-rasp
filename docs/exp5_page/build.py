import json, html, math, re
A = "/tmp/claude-0/-home-user-auto-rasp/de2b9d70-6f3e-5db7-b3e0-915adfdce244/scratchpad/artifact"
D = json.load(open(f"{A}/data.json"))["games"]
G = ["breakout", "seaquest", "asterix"]
NAME = {"breakout": "Breakout", "seaquest": "Seaquest", "asterix": "Asterix"}
esc = html.escape
f1 = lambda x: f"{x:,.1f}"
REPO = "https://github.com/andre15silva/auto-rasp/tree/claude/weight-space-rasp-tracr-4qob1j"
POST = "https://rikiyat.github.io/blog/weight-space-programming/"
LOGS = "https://github.com/RikiyaT/lm_understand-logs/tree/main/exp5_write_from_scratch"

# ---------- results chart (small multiples of horizontal bars)
SCALE = {"breakout": 600, "seaquest": 100, "asterix": 60}
TICKS = {"breakout": [0, 200, 400, 600], "seaquest": [0, 25, 50, 75, 100], "asterix": [0, 20, 40, 60]}
def results_chart():
    out = []
    for g in G:
        d = D[g]
        rows = [("Opus 5.5 · RASP → Tracr", "opus", d["opus"]["mean"], d["opus"]["se"], "our evaluation, 1,000 episodes"),
                ("Astra · MLP weights", "astra", d["astra_ours"]["mean"], d["astra_ours"]["se"], "our re-scoring of the paper's released network, 1,000 episodes"),
                ("PPO · 500M steps", "ppo", d["ppo500_best"]["mean"], d["ppo500_best"]["se"], f"paper, best of 3 seeds ({d['ppo500_best']['name']})"),
                ("PPO · 100M steps", "ppo", d["ppo100_best"]["mean"], d["ppo100_best"]["se"], f"paper, best seed ({d['ppo100_best']['name']})")]
        s = SCALE[g]
        bars = []
        for label, cls, m, se, src in rows:
            w = 100 * m / s
            tip = f"{label}<br><b>{m:,.1f} ± {se:.1f}</b><br><span>{esc(src)}</span>"
            bars.append(f'''<div class="hb-row"><div class="hb-label">{esc(label)}</div>
<div class="hb-track"><div class="hb-bar {cls}" style="width:{w:.2f}%" tabindex="0" data-tip="{esc(tip)}"></div><span class="hb-val" style="left:{w:.2f}%">{m:,.1f}</span></div></div>''')
        ticks = "".join(f'<span style="left:{100 * t / s:.2f}%">{t:,}</span>' for t in TICKS[g])
        grid = "".join(f'<i style="left:{100 * t / s:.2f}%"></i>' for t in TICKS[g])
        out.append(f'''<div class="sm"><h4>{NAME[g]}</h4><div class="hb">{''.join(bars)}<div class="hb-grid">{grid}</div></div>
<div class="hb-axis"><div></div><div class="hb-ticks">{ticks}</div></div></div>''')
    return "".join(out)

# ---------- game frames
def frame_grid(g, show_tokens=False):
    fr = D[g]["frame"]
    o, toks = fr["obs"], fr["tokens"]
    cells = []
    for r in range(10):
        for c in range(10):
            ch = o[r][c]
            fills = [n for n, k in (("player", 0), ("danger", 1), ("reward", 2), ("projectile", 3)) if ch[k]]
            cls = ["cell"]
            style = ""
            if show_tokens:
                t = toks[r * 10 + c]
                cls.append("tok" if t else "tok zero")
                inner = str(t)
            else:
                inner = ""
                if len(fills) >= 2:
                    style = f' style="background:linear-gradient(135deg,var(--ch-{fills[0]}) 50%,var(--ch-{fills[1]}) 50%)"'
                elif fills:
                    cls.append(f"f-{fills[0]}")
                elif ch[5]:
                    cls.append("f-gauge")
                if ch[4]:
                    cls.append("trail")
            names = [n for n, k in zip(("player", "danger", "reward", "projectile", "trail", "gauge"), range(6)) if ch[k]]
            tip = f"row {r}, column {c}<br>token {toks[r * 10 + c]}" + (f"<br>{', '.join(names)}" if names else "<br>empty")
            cells.append(f'<div class="{" ".join(cls)}"{style} data-tip="{esc(tip)}">{inner}</div>')
    return f'<div class="grid10">{"".join(cells)}</div>'

def action_slots(g):
    fr = D[g]["frame"]
    z = fr["logits"]
    mx = max(z)
    p = [math.exp(v - mx) for v in z]
    s = sum(p)
    p = [v / s for v in p]
    names = ["no-op", "left", "up", "right", "down", "fire"]
    out = []
    for a in range(6):
        out.append(f'''<div class="slot" data-tip="{esc(f'index {100 + a}, token {64 + a}<br>action {a}: {names[a]}<br>logit {z[a]:.2f}, probability {p[a]:.3f}')}">
<div class="slot-tok">{64 + a}</div><div class="slot-name">{names[a]}</div><div class="slot-logit">{z[a]:.0f}</div><div class="slot-p">{p[a] * 100:.0f}%</div></div>''')
    return "".join(out)

# ---------- architecture
LOGMAX = math.log10(4201)
def arch(g):
    d = D[g]
    c = d["compile"]["stats"]
    rows = []
    for i, L in enumerate(d["layers"]):
        pips = "".join('<i></i>' for _ in range(L["heads"])) or '<span class="none">none</span>'
        w = 100 * math.log10(L["mlp"] + 1) / LOGMAX if L["mlp"] else 0
        rows.append(f'''<div class="lm-row"><div class="lm-l">{i + 1}</div><div class="lm-heads" data-tip="{esc(f'layer {i + 1}: {L["heads"]} attention head(s), every one reading the board (none purely positional)')}">{pips}</div>
<div class="lm-mlp"><div class="lm-bar" style="width:{w:.1f}%" data-tip="{esc(f'layer {i + 1}: MLP with {L["mlp"]:,} hidden units in use')}"></div><span>{L["mlp"]:,}</span></div></div>''')
    res = d["residual"]
    an = d["astra_run"]["nonzero"]
    astra_nz = sum(an.values())
    facts = [("Layers", f'{c["layers"]}'), ("Attention heads, total", f'{sum(L["heads"] for L in d["layers"])} (at most {c["heads"]} in a layer)'),
             ("Key size", f'{c["key_size"]}'), ("Widest MLP", f'{c["mlp_hidden_size"]:,} hidden units'),
             ("Residual stream", f'{res["dims"]} dimensions'), ("SOps", f'{res["sops_categorical"]} categorical, {res["sops_numerical"]} numerical'),
             ("Parameters", f'{c["dense_params"]:,} dense, {c["nonzero_params"]:,} nonzero'),
             ("MLP_EXACTNESS", f'{d["compile"]["mlp_exactness"]:,}'), ("Compile time", f'{d["compile"]["compile_seconds"]:.0f} s'),
             ("Speed", f'{d["compile"]["seconds_per_1000_positions"]:.1f} s per 1,000 positions')]
    fl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in facts)
    return f'''<div class="arch"><div class="lm"><div class="lm-head"><span>Layer</span><span>Attention heads</span><span>MLP hidden units (log scale)</span></div>{''.join(rows)}</div>
<div class="arch-facts"><dl>{fl}</dl><p class="vs">Astra's network for the same game: 600 → 32 → 32 → 6 tanh, 20,486 parameters, {astra_nz:,} nonzero.</p></div></div>'''

# ---------- death causes (tall segmented bars)
def deaths():
    rows = []
    for g in ("asterix", "seaquest"):
        for who, label in (("opus", "Opus 5.5 · RASP"), ("astra", "Astra · MLP")):
            dg = D[g]["diag"][who]
            st = dg["of_those_caused_by_a_sticky_repeat"]
            po = dg["of_those_where_the_policy_itself_chose_a_fatal_action"]
            no = dg["deaths"] - dg["deaths_avoidable_by_another_action_this_step"]
            segs = []
            for n, cls, nm in ((st, "s-sticky", "a sticky repeat played the fatal action"),
                               (po, "s-policy", "the policy itself chose the fatal action"),
                               (no, "s-none", "no action would have survived the step")):
                if n == 0:
                    continue
                lab = str(n) if n >= 7 else ""
                segs.append(f'<div class="seg {cls}" style="flex:{n} 0 0" tabindex="0" data-tip="{esc(f"{NAME[g]}, {label}<br><b>{n} of 100 deaths</b>: {nm}")}">{lab}</div>')
            rows.append(f'''<div class="sb-row"><div class="sb-label"><b>{NAME[g]}</b> {esc(label)}</div><div class="sb">{''.join(segs)}</div>
<div class="sb-len">{dg["mean_length"]:,.0f} steps</div></div>''')
    return "".join(rows)

# ---------- sticky on/off dumbbell
def dumbbell():
    rows = []
    S = 160
    for g in ("asterix", "seaquest"):
        for who, label, cls in (("opus", "Opus 5.5 · RASP", "opus"), ("astra", "Astra · MLP", "astra")):
            rp = D[g]["sticky"]["replay"][who]
            on, off = rp["sticky_0.1"], rp["sticky_0.0"]
            a, b = 100 * on["mean"] / S, 100 * off["mean"] / S
            rows.append(f'''<div class="db-row"><div class="db-label"><b>{NAME[g]}</b> {esc(label)}</div><div class="db-track">
<div class="db-line {cls}" style="left:{min(a, b):.2f}%;width:{abs(b - a):.2f}%"></div>
<div class="db-dot on {cls}" style="left:{a:.2f}%" tabindex="0" data-tip="{esc(f'{NAME[g]}, {label}<br>sticky actions 0.1 (official): <b>{on["mean"]:.1f} ± {on["se"]:.1f}</b><br>mean episode {on["mean_length"]:,.0f} steps')}"></div>
<span class="db-v on" style="left:{a:.2f}%">{on["mean"]:.0f}</span>
<div class="db-dot off {cls}" style="left:{b:.2f}%" tabindex="0" data-tip="{esc(f'{NAME[g]}, {label}<br>sticky actions off: <b>{off["mean"]:.1f} ± {off["se"]:.1f}</b><br>mean episode {off["mean_length"]:,.0f} steps')}"></div>
<span class="db-v off" style="left:{b:.2f}%">{off["mean"]:.0f}</span></div></div>''')
    ticks = "".join(f'<span style="left:{100 * t / S:.2f}%">{t}</span>' for t in (0, 40, 80, 120, 160))
    grid = "".join(f'<i style="left:{100 * t / S:.2f}%"></i>' for t in (0, 40, 80, 120, 160))
    return f'<div class="db">{"".join(rows)}<div class="db-grid">{grid}</div></div><div class="db-axis"><div></div><div class="db-ticks">{ticks}</div></div>'

# ---------- architecture comparison
AC = json.load(open(f"{A}/arch_compare.json"))

def schematic_breakout():
    sc = 0.2  # px per unit, the same for both networks
    a, o = AC["breakout"]["astra"], AC["breakout"]["opus"]
    lay = D["breakout"]["layers"]
    res = D["breakout"]["residual"]
    W = 920
    out = [f'<svg class="schem" viewBox="0 0 {W} 470" role="img" aria-label="Breakout: Astra\'s 600-32-32-6 MLP and the 7-layer Tracr transformer, drawn with one unit scale">']
    # scale ruler
    out.append(f'<rect x="{W - 40}" y="20" width="8" height="{100 * sc}" class="sv-ruler"/><text x="{W - 46}" y="{20 + 100 * sc / 2 + 4}" class="sv-small" text-anchor="end">100 units</text>')
    # ---- Astra row
    cy = 112
    out.append(f'<text x="0" y="22" class="sv-title">Astra · MLP weights</text><text x="0" y="40" class="sv-small">20,486 parameters, 815 set · one pass per move</text>')
    st = [(80, 600, "600 inputs", f"{a['inputs_used']} read"), (360, 32, "32 tanh", f"{a['units_used'][0]} used"),
          (560, 32, "32 tanh", f"{a['units_used'][1]} used"), (740, 6, "6 logits", "")]
    fan = [f"W1 · 600 × 32 · {a['w_nnz'][0]} set", f"W2 · 32 × 32 · {a['w_nnz'][1]} set", f"W3 · 32 × 6 · {a['w_nnz'][2]} set"]
    for i in range(3):
        x1, u1 = st[i][0], st[i][1]; x2, u2 = st[i + 1][0], st[i + 1][1]
        h1, h2 = max(2, u1 * sc), max(2, u2 * sc)
        out.append(f'<polygon points="{x1 + 7},{cy - h1 / 2} {x2 - 7},{cy - h2 / 2} {x2 - 7},{cy + h2 / 2} {x1 + 7},{cy + h1 / 2}" class="sv-fan-a" data-tip="{esc(fan[i])}"/>')
        tx, ty = ((x1 + x2) / 2 - 40, cy + 4) if i == 0 else ((x1 + x2) / 2, cy - 16)
        out.append(f'<text x="{tx}" y="{ty}" class="sv-small" text-anchor="middle">{esc(fan[i])}</text>')
    for x, u, lab, used in st:
        h = max(2, u * sc)
        out.append(f'<rect x="{x - 7}" y="{cy - h / 2}" width="14" height="{h}" rx="2" class="sv-astra" data-tip="{esc(lab + (", " + used if used else ""))}"/>')
        out.append(f'<text x="{x}" y="{cy + max(h, 8) / 2 + 18}" class="sv-label" text-anchor="middle">{esc(lab)}</text>')
        if used:
            out.append(f'<text x="{x}" y="{cy + max(h, 8) / 2 + 34}" class="sv-small" text-anchor="middle">{esc(used)}</text>')
    # ---- Opus row
    cy = 352
    x0, x1 = 80, 800
    bh = res["dims"] * sc
    out.append(f'<text x="0" y="246" class="sv-title">Opus 5.5 · RASP program compiled by Tracr</text><text x="0" y="264" class="sv-small">{o["dense_params"]:,} parameters, {o["nonzero_params"]:,} nonzero · every block runs at all {o["positions"]} positions</text>')
    for k in (2, 1):
        out.append(f'<rect x="{x0 + 7 * k}" y="{cy - bh / 2 - 7 * k}" width="{x1 - x0}" height="{bh}" rx="3" class="sv-ghost"/>')
    out.append(f'<rect x="{x0}" y="{cy - bh / 2}" width="{x1 - x0}" height="{bh}" rx="3" class="sv-band" data-tip="{esc(f'residual stream: {res["dims"]} numbers per position ({res["input_dims"]["indices"]} encode the position, {res["input_dims"]["tokens"]} the token, the rest the program\'s own values)')}"/>')
    out.append(f'<text x="{x1 + 18}" y="{cy - bh / 2 - 4}" class="sv-small">× {o["positions"]} positions</text>')
    n = len(lay)
    xs = [x0 + 60 + i * (x1 - x0 - 120) / (n - 1) for i in range(n)]
    for i, (x, L) in enumerate(zip(xs, lay)):
        h = max(2, L["mlp"] * sc)
        out.append(f'<rect x="{x - 6}" y="{cy - h / 2}" width="12" height="{h}" rx="2" class="sv-opus" data-tip="{esc(f'layer {i + 1}: MLP with {L["mlp"]:,} hidden units' + (f', after {L["heads"]} attention heads' if L["heads"] else ''))}"/>')
        for j in range(L["heads"]):
            out.append(f'<rect x="{x - 26 + j * 11}" y="{cy - bh / 2 - 22}" width="8" height="8" rx="1.5" class="sv-opus" data-tip="{esc(f'layer {i + 1}: attention head {j + 1} of {L["heads"]}, mixing information across the {o["positions"]} positions')}"/>')
        out.append(f'<text x="{x}" y="{cy + bh / 2 + 18}" class="sv-label" text-anchor="middle">L{i + 1}</text><text x="{x}" y="{cy + bh / 2 + 34}" class="sv-small" text-anchor="middle">{L["mlp"]:,}</text>')
    out.append(f'<text x="{x0 - 10}" y="{cy + 4}" class="sv-small" text-anchor="end">{res["dims"]}</text>')
    out.append(f'<text x="{(x0 + x1) / 2}" y="{cy + bh / 2 + 56}" class="sv-small" text-anchor="middle">squares: attention heads · bars: MLP hidden units per layer (numbers below) · band: the residual stream each block reads and writes</text>')
    out.append("</svg>")
    return "".join(out)

LOG_LO, LOG_HI = 2, 10
def lpos(v):
    return 100 * (math.log10(v) - LOG_LO) / (LOG_HI - LOG_LO)

def fmt_big(v):
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if v >= div:
            x = v / div
            return f"{x:.1f}{suf}" if x < 10 else f"{x:.0f}{suf}"
    return f"{v:,.0f}"

def size_chart():
    measures = [("dense_params", "Parameters", "every number in the weight matrices"),
                ("nonzero_params", "Nonzero parameters", "the weights that are actually set"),
                ("mac_nonzero", "Multiply-adds per move", "counting only nonzero weights, plus attention over position pairs"),
                ("mac_dense", "Multiply-adds per move, as assembled", "every matrix entry, zeros included")]
    panels = []
    for key, title, sub in measures:
        rows = []
        for g in G:
            a, o = AC[g]["astra"][key], AC[g]["opus"][key]
            pa, po = lpos(a), lpos(o)
            ratio = f"{o / a:.1f}" if o / a < 10 else f"{o / a:,.0f}"
            ta = esc(f"{NAME[g]}, Astra · MLP<br>{title}: <b>{a:,}</b>")
            to = esc(f"{NAME[g]}, Opus · Tracr transformer<br>{title}: <b>{o:,}</b>")
            rows.append(f'''<div class="lg-row"><div class="lg-label">{NAME[g]}</div><div class="lg-track">
<div class="lg-line" style="left:{pa:.2f}%;width:{po - pa:.2f}%"></div>
<div class="lg-dot astra" style="left:{pa:.2f}%" tabindex="0" data-tip="{ta}"></div><span class="lg-v a" style="left:{pa:.2f}%">{fmt_big(a)}</span>
<div class="lg-dot opus" style="left:{po:.2f}%" tabindex="0" data-tip="{to}"></div><span class="lg-v o{' end' if po > 88 else ''}" style="left:{po:.2f}%">{fmt_big(o)}</span>
</div><div class="lg-ratio">×{ratio}</div></div>''')
        grid = "".join(f'<i style="left:{lpos(10 ** e):.2f}%"></i>' for e in range(LOG_LO, LOG_HI + 1))
        panels.append(f'''<div class="lg-panel"><div class="lg-title">{esc(title)} <span>{esc(sub)}</span></div><div class="lg-rows">{"".join(rows)}<div class="lg-grid">{grid}</div></div></div>''')
    labels = {2: "100", 3: "1K", 4: "10K", 5: "100K", 6: "1M", 7: "10M", 8: "100M", 9: "1B", 10: "10B"}
    ticks = "".join(f'<span style="left:{lpos(10 ** e):.2f}%">{labels[e]}</span>' for e in range(LOG_LO, LOG_HI + 1, 2))
    return "".join(panels) + f'<div class="lg-axis"><div></div><div class="lg-ticks">{ticks}</div><div></div></div>'

# ---------- tables
def results_table():
    rows = []
    for g in G:
        d = D[g]
        rows.append(f'''<tr><th scope="row">{NAME[g]}</th><td class="hl">{d["opus"]["mean"]:,.1f} <small>± {d["opus"]["se"]:.1f}</small></td>
<td>{d["astra_ours"]["mean"]:,.1f} <small>± {d["astra_ours"]["se"]:.1f}</small></td><td>{d["astra_paper"]["mean"]:,.1f} <small>± {d["astra_paper"]["se"]:.1f}</small></td>
<td>{d["ppo100_best"]["mean"]:,.1f}</td><td>{d["ppo500_best"]["mean"]:,.1f}</td></tr>''')
    return "".join(rows)

def faith_rows():
    out = []
    for g in G:
        f = D[g]["faith"]
        defined = f.get("logit_entries_rasp_defined", 0)
        out.append(f'''<tr><th scope="row">{NAME[g]}</th><td>{f["rasp_sops_failed"]} of {f["rasp_sops"]}</td><td>{defined * 100:.1f}%</td>
<td>{f.get("entrywise_max_abs_logit_diff", float("nan")):.2g}</td><td>{(f"{f['argmax_agreement'] * 100:.0f}%" if f.get("argmax_agreement") is not None else "–")}</td>
<td>{(f"{f['mean_total_variation']:.3f}" if f.get("mean_total_variation") is not None else "–")}</td></tr>''')
    return "".join(out)

def behaviour_rows():
    out = []
    names = ["no-op", "left", "up", "right", "down", "fire"]
    for g in ("asterix", "seaquest"):
        for who, label in (("opus", "Opus 5.5 · RASP"), ("astra", "Astra · MLP")):
            h = D[g]["sticky"]["hazard"][who]
            ad = h["action_distribution"]
            top = max(range(6), key=lambda i: ad[i])
            lr = ad[1] + ad[3]
            out.append(f'''<tr><th scope="row">{NAME[g]} · {esc(label)}</th><td>{h["frac_steps_moving"] * 100:.0f}%</td><td>{h["frac_steps_changing_action"] * 100:.0f}%</td>
<td>{h["frac_steps_where_replaying_previous_action_is_fatal"] * 100:.2f}%</td><td>{names[top]} {ad[top] * 100:.0f}%</td><td>{lr * 100:.0f}%</td></tr>''')
    return "".join(out)

def effort_rows():
    out = []
    for g in G:
        d = D[g]
        out.append(f'''<tr><th scope="row">{NAME[g]}</th><td>{d["astra_run"]["output_tokens"]:,}</td><td>{d["astra_run"]["wall_s"] / 60:.0f} min</td>
<td>{d["run"]["output_tokens"]:,}</td><td>{d["run"]["wall_s"] / 60:.0f} min</td><td>${d["run"]["cost_usd"]:.2f}</td><td>{d["program"].count(chr(10))} lines</td></tr>''')
    return "".join(out)

QUOTES = {
    "breakout": ("The policy predicts the column where the paddle must be when the ball comes down, and moves the paddle there early.",
                 "The first layer computes four landing-position errors and two direction indicators."),
    "seaquest": ("The policy is a hand-written reactive heuristic. It is computed relative to the submarine's front cell.",
                 "The policy stays at the starting column, firing left while changing rows to intercept divers and attack enemies."),
    "asterix": ("The policy does a one-step lookahead with risk scoring for each of the 5 distinct moves.",
                "I use a conservative interception policy: stay in column 5, approach nearby incoming treasure, and wait in its row."),
}
SUMMARY = {
    "breakout": "Wall bounces are handled by unfolding the board into a periodic coordinate. The ball's direction comes from comparing the ball cell with its trail cell, and the predicted landing column becomes a two-cell target region. Five attention heads in one layer copy the ball, trail and paddle positions to every position. A chain of exact categorical lookup MLPs then turns them into one wanted action, which gets logit 30.",
    "seaquest": "Every move is checked against danger at its destination cell. Fire is rewarded when an enemy is ahead, and divers attract the sub. It surfaces only when oxygen is low and a diver is aboard, read from two cells of the gauge row. The program keeps every attention space at 57 dimensions or fewer so that Tracr's scaled attention stays sharp, and it raises MLP_EXACTNESS to 1,000.",
    "asterix": "Each row holds at most one entity and entities move only sideways. An enemy is approaching a cell when the cell beside it on that side is not its trail. Each of the five distinct moves gets a base score of 60 if its target is safe, minus penalties for approaching enemies and plus bonuses for gold.",
}

def game_section(g):
    d = D[g]
    q_opus, q_astra = QUOTES[g]
    code = esc(d["program"].rstrip())
    n = d["program"].count("\n")
    return f'''<section class="game" id="{g}">
<div class="game-head"><h3>{NAME[g]}</h3><div class="chips"><span class="chip opus">Opus · RASP {d["opus"]["mean"]:,.1f}</span><span class="chip astra">Astra · MLP {d["astra_ours"]["mean"]:,.1f}</span></div></div>
<div class="plans"><figure class="plan"><figcaption>Opus 5.5's plan</figcaption><blockquote>{esc(q_opus)}</blockquote></figure>
<figure class="plan"><figcaption>Astra's plan, from the paper's logs</figcaption><blockquote>{esc(q_astra)}</blockquote></figure></div>
<p>{esc(SUMMARY[g])}</p>
<details class="code"><summary>The whole program, {n} lines, as written in the reply</summary><pre><code class="language-python">{code}</code></pre></details>
<h4 class="sub">What Tracr compiled it to</h4>
{arch(g)}
</section>'''

frames_small = "".join(f'''<figure class="mini"><div class="frame-wrap">{frame_grid(g)}</div><figcaption>{NAME[g]}, step {D[g]["frame"]["step"]}</figcaption></figure>''' for g in ("seaquest", "asterix"))

page = open(f"{A}/template.html").read()
for k, v in {
    "%%RESULTS_CHART%%": results_chart(), "%%RESULTS_TABLE%%": results_table(),
    "%%FRAME_BREAKOUT%%": frame_grid("breakout"), "%%TOKENS_BREAKOUT%%": frame_grid("breakout", True),
    "%%ACTIONS_BREAKOUT%%": action_slots("breakout"), "%%FRAMES_SMALL%%": frames_small,
    "%%GAMES%%": "".join(game_section(g) for g in G), "%%FAITH_ROWS%%": faith_rows(),
    "%%DEATHS%%": deaths(), "%%DUMBBELL%%": dumbbell(), "%%BEHAVIOUR_ROWS%%": behaviour_rows(),
    "%%EFFORT_ROWS%%": effort_rows(), "%%REPO%%": REPO, "%%POST%%": POST, "%%LOGS%%": LOGS,
    "%%BK_STEP%%": str(D["breakout"]["frame"]["step"]),
    "%%ARCH_SCHEMATIC%%": schematic_breakout(), "%%SIZE_CHART%%": size_chart(),
}.items():
    page = page.replace(k, v)
assert "%%" not in page, re.findall("%%[A-Z_]+%%", page)
open(f"{A}/rasp-plays-minatar.html", "w").write(page)
print("written", len(page))
