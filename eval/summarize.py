"""Builds results/summary.md from results/*/eval.json and runs/*/state.json."""
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = ["astra_b0", "astra_b10", "astra_b25", "astra_b50"]


def pct(x):
    return "–" if x is None else f"{100 * x:.1f}"


rows = []
for f in sorted(glob.glob(os.path.join(REPO, "results", "*", "eval.json"))):
    name = os.path.basename(os.path.dirname(f))
    e = json.load(open(f))
    po = e["per_opponent"]
    g = lambda o: po[o]["score"] if o in po else None  # noqa: E731
    run = os.path.join(REPO, "runs", name, "state.json")
    st = json.load(open(run)) if os.path.exists(run) else {}
    writer = (f"Opus 5.5 → RASP → Tracr" if name.startswith("opus") else "Astra (paper) → MLP weights")
    budget = st.get("budget", name.split("_b")[-1] if "_b" in name else "")
    c = e.get("compile", {})
    size = (f"{c['stats']['layers']} layers, {c['stats']['residual_dims']} dims, "
            f"{c['stats']['nonzero_params']:,} nonzero / {c['stats']['dense_params']:,}" if c.get("ok") else
            ("compile failed" if c else "243→512×6→82"))
    fa = e.get("faithfulness") or {}
    rows.append((writer, budget, name, g("ppo_s0"), g("ppo_s2"), e.get("main"), g("random"),
                 [g(r) for r in REF], size, fa, st))

order = {"Astra (paper) → MLP weights": 1}
rows.sort(key=lambda r: (order.get(r[0], 0), int(r[1]) if str(r[1]).isdigit() else 0))
lines = ["| writer | passes | vs PPO s0 | vs PPO s2 | **main** | vs random | vs Astra b0 | vs Astra b10 | "
         "vs Astra b25 | vs Astra b50 | network |", "|" + "---|" * 11]
for w, b, n, s0, s2, m, rnd, ref, size, fa, st in rows:
    lines.append(f"| {w} | {b} | {pct(s0)} | {pct(s2)} | **{pct(m)}** | {pct(rnd)} | "
                 + " | ".join("—" if n == r else pct(x) for r, x in zip(REF, ref)) + f" | {size} |")
lines += ["", "Win rates in % of the row's network, Black in half of the games, both sides sampling at "
          "temperature 1. 2,000 games per cell against PPO and random (1 s.e. ≈ 1.1 points at 50 %); head-to-heads "
          "against Astra's networks: 2,000 games in the Astra rows, 1,000 in the Opus rows (1 s.e. ≈ 1.6 points). "
          "main = mean of the two PPO columns (the paper's main measure, here with its same-size PPO networks).", ""]
fl = [r for r in rows if r[9]]
if fl:
    lines += ["Can RASP's reference evaluator run the program? (`rasp.evaluate` per SOp on 256 positions from the "
              "network's games vs PPO s0; and the evaluation runtime vs the passes' reference runtime)", "",
              "| run | SOps | SOps rasp.evaluate fails on | output evaluable | first error | eval runtime vs reference "
              "(max abs logit diff) |", "|---|---|---|---|---|---|"]
    for r in fl:
        fa = r[9]
        ev = json.load(open(os.path.join(REPO, "results", r[2], "eval.json")))
        fr = (ev.get("fast_runtime_check") or {}).get("max_abs_logit_diff")
        if fa.get("ok") and fa.get("rasp_sops") is not None:
            err = (fa.get("rasp_first_error") or "").split(" Received")[0][:90]
            lines.append(f"| {r[2]} | {fa['rasp_sops']} | {fa['rasp_sops_failed']} | "
                         f"{'no' if fa['rasp_output_failed'] else 'yes'} | {err} | {fr} |")
        else:
            lines.append(f"| {r[2]} | | | | failed: {str(fa.get('error', ''))[:80]} | {fr} |")
    lines.append("")
st_rows = [r for r in rows if r[10]]
if st_rows:
    lines += ["Writer runs:", "", "| run | turns | Python runs | passes used | finished |", "|---|---|---|---|---|"]
    for r in st_rows:
        st = r[10]
        lines.append(f"| {r[2]} | {st['turn']} | {st['runs']} | {st['passes']}/{st['budget']} | {st.get('done')} |")
open(os.path.join(REPO, "results", "summary.md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
