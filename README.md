# auto-rasp: weight-space programming through RASP and Tracr

A variant of **Experiment 6** of *Sparks of Weight-Space Programming: LLMs can understand and write neural network
weights* (Takehi, Teoh, Zhang and Khattab, 2026; [post](https://rikiyat.github.io/blog/weight-space-programming/),
[logs](https://github.com/RikiyaT/lm_understand-logs)).

In the paper, a frontier model ("Astra") writes the 1,480,274 weights of an MLP that plays 9x9 Go, from scratch and
without training. Here the model, **Claude Opus 5.5 via Claude Code**, instead writes a **RASP program**. The program
is compiled by [**Tracr**](https://github.com/google-deepmind/tracr) into transformer weights, and we check whether
**the compiled transformer** plays Go. Everything else follows the paper's protocol as closely as the released
material allows: the same game, the same budgets of 0/10/25/50 "passes", the same one-block-per-turn harness and
the same kind of hidden evaluation.

RESULTS_PLACEHOLDER

## Protocol

| | Paper, Experiment 6 | This repository |
|---|---|---|
| Writer | gpt-6-astra via `codex exec`, effort `xhigh`, every Codex tool off | `claude-opus-5-5` via `claude -p`, `--effort xhigh`, `--tools ""` (every Claude Code tool off), `--safe-mode`, `--strict-mcp-config`, neutral system prompt `Answer the user's request.` |
| What the writer produces | the values of a fixed 243→512×6→82 ReLU MLP (all zero at the start) | `/work/program.py`: a RASP program whose numerical output SOp gives the 82 move logits. The network is `compile_rasp_to_model(program(), vocab={".","x","o","B","W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=MLP_EXACTNESS)`, used exactly as Tracr produces it |
| Network input | 3 planes × 81 points from the mover's view, plus "White to move" | 83 tokens: `BOS`, then the 81 points from the mover's view (`x` own stone, `o` opponent's, `.` empty), then `B`/`W` (colour to move) at index 81 |
| Network output | 82 logits (81 points + pass) | the output SOp at indices 0..81 (index 81 = pass) |
| Policy | illegal moves masked, sampled at T = 1, no search | same |
| Turns | one reply per call; one ` ```python `, ` ```games ` or ` ```positions ` block per reply, run by the harness | same |
| Python sandbox | bubblewrap, no network, no Go library, numpy/scipy/sklearn/PyTorch/pandas/sympy/networkx, 900 s and 96 GB per run, 120 runs | bubblewrap, no network, no Go library, the same libraries plus tracr/jax/haiku, 900 s and 10 GB per run, 120 runs |
| "Do not run the network" (rule c) | stated in the prompt, audited | stated in the prompt; in the sandbox, `rasp.evaluate`, `RASPExpr.__call__` and the compiled model's `apply`/`forward` raise errors. Compiling and inspecting the compiled weights are allowed |
| Games pass | ≤ 128 games vs practice opponents "random", "weak" (REINFORCE), "strong" (PPO seed 1) | ≤ 128 games vs "random", "weak" (each move: "strong"'s with p = 0.7, else uniform random; beats random 94 %), "strong" (the paper's same-size PPO, seed 1; beats random 98.7 %) |
| Positions pass | ≤ 256 positions → top moves, logits, probabilities, hidden activations | ≤ 256 positions → top moves, logits, probabilities, the value of every SOp as read from the compiled network's residual stream, and optionally `rasp.evaluate`'s value of every SOp |
| Hidden evaluation | 2,000 games vs small PPO networks seeds 0 and 2 (243→32→32→82; main = their mean), REINFORCE networks and random | 2,000 games vs the paper's **same-size** PPO networks seeds 0 and 2 (main = their mean) and random, plus head-to-heads vs **Astra's four written networks** |

**Why different opponents.** The paper's hidden small-PPO and REINFORCE networks are not released. Its same-size PPO
networks (512×6, three seeds, 20.5 M self-play games each) and Astra's written networks are. So, as in the paper,
the writer practises against PPO seed 1 and is evaluated on seeds 0 and 2, which it never plays. Astra's networks are
evaluated under the identical protocol (table above), which makes the comparison direct. Our numbers are not
comparable to the post's headline numbers, which were measured against the smaller, unreleased PPO networks.

**Validation of the game engine.** `gorasp/go.py` runs pgx's own Go rules (the `Game` class behind
`pgx.make("go_9x9")`, without its colour shuffling). [`eval/validate_engine.py`](eval/validate_engine.py) replays
four head-to-heads that the paper published, 2,000 games each (`results/validate_engine.json`):

| head-to-head (written network's score) | paper | ours |
|---|---|---|
| Astra budget 0 vs PPO 512×6 seed 0 | 42.55 % | 42.80 % |
| Astra budget 0 vs PPO 512×6 seed 1 | 26.30 % | 24.90 % |
| Astra budget 50 vs PPO 512×6 seed 0 | 74.15 % | 72.55 % |
| Astra budget 50 vs PPO 512×6 seed 2 | 78.55 % | 80.25 % |

All four differences are within sampling noise (the s.e. of a difference of two 2,000-game runs is about 1.4
points), as are the game lengths (92.3 vs 92.6 moves for the first row).

**Validation of the Tracr runtime.** Every pass and the evaluation run the compiled weights with
[`gorasp/tracr_policy.py`](gorasp/tracr_policy.py). This is a sparse NumPy implementation of Tracr's own Haiku
forward pass: no layer norm, attention logits divided by √key_size, ReLU MLPs, and input-independent attention
patterns cached. It matches `AssembledTransformerModel.apply` to about 1e-5
([`tests/test_tracr_policy.py`](tests/test_tracr_policy.py)) and is roughly 10× faster.

### Two properties of stock Tracr that matter here

These were found while building the harness. The writer was not told about them; the prompt gives the exact forward
pass and says that compilation is not guaranteed to be exact.

1. **Soft attention.** Tracr builds attention heads with a softmax "coldness" of 100, but the Haiku model it
   assembles divides attention logits by √key_size (`tracr/transformer/attention.py`), and `key_size` is the largest
   query/key space of any head. A program with a categorical `Select` over `indices` (82 values) gets key_size ≈ 84
   and an effective coldness of about 11. A one-position look-up then reads 0.995 instead of 1, and a query that
   should select nothing (and so fall back to BOS) leaks about 0.13 from the other 82 positions.
2. **Value-set blow-up.** The compiler enumerates every value a numerical SOp can take. A numerical `Aggregate`
   over 82 positions has 83 possible values. Adding two of them with `LinearSequenceMap` gives 3,315; adding four
   gives millions, and a numerical `Map` on the sum then builds an MLP with one hidden unit per value. Our first
   harness test program used all 15 GB of the machine. Every compile therefore runs with a hard memory cap.

## Running it

```bash
apt-get install -y bubblewrap        # the sandbox
scripts/setup_envs.sh                # /opt/venvs/rasp (harness, with pgx) and /opt/venvs/sandbox (writer, no Go library)
scripts/fetch_networks.sh            # the paper's released Experiment-6 networks -> networks/paper/ (CC BY 4.0)
source /opt/venvs/rasp/bin/activate
python eval/validate_engine.py       # optional: reproduce the paper's head-to-heads
python -m harness.run_writer --budget 50 --run-id opus55_b50     # a writer run (resumable)
python eval/evaluate.py --run runs/opus55_b50                    # hidden evaluation of its final program
python eval/evaluate.py --mlp networks/paper/budget_50 --name astra_b50
python eval/summarize.py                                         # results/summary.md
```

`python -m harness.prompt 50` prints the exact task prompt (`runs/<id>/message.txt` holds the one each run got).

## Layout

| path | what |
|---|---|
| `gorasp/go.py` | batched pgx Go, the 243-plane encoding (for the paper's networks) and the token encoding (for Tracr) |
| `gorasp/policies.py`, `play.py`, `opponents.py` | policies, sampled batched play with the paper's summary fields, the opponent sets |
| `gorasp/tracr_policy.py` | compile, export the weights as sparse matrices, fast forward pass, residual-stream decoding |
| `harness/prompt.py` | the task prompt (the paper's, with the network, sandbox and rules rewritten for RASP/Tracr) |
| `harness/run_writer.py` | the turn loop around `claude -p` / `claude -p --resume`, with per-turn audit |
| `harness/sandbox.py`, `prelude.py`, `compile_worker.py` | the bubblewrap sandbox, the writer's predefined names, and the compile done for passes and the evaluation |
| `harness/passes.py` | the games and positions passes |
| `eval/` | engine validation, hidden evaluation, summary |
| `runs/<id>/` | one writer run: `message.txt` (task prompt), `turns/tNNN/` (`prompt.txt` sent, `answer.md` received, `events.jsonl` the raw Claude Code stream, `run.json` with usage and the tool-free audit), `tool_calls.jsonl` (every sandbox run's code and output and every pass), `work/` (the writer's files, pass summaries), `final/` (the final program's sources and compile record), `loop.log`, `state.json` |
| `results/` | evaluation results and `summary.md` |

Per-game records, boards, compiled weights and residual dumps are not committed (see `.gitignore`); they are
regenerated by the commands above.

## Notes on the runs

- **Context.** With all tools off, the writer's context is our task prompt, the neutral system prompt, and
  Claude Code's own automatic blocks: a short environment section (working directory, platform) and the account's
  user-email line. The writer ran from an empty temporary directory, without access to this repository, the
  paper's logs or the network. Its code ran only inside the sandbox, which sees nothing but `/work`.
- **Concurrency and one restart.** The four runs ran at the same time on one machine (4 CPUs, 15 GB). At first,
  every sandbox job (writer runs, pass compiles, passes) took one global lock. After 25 minutes, one 900-second
  compile timeout had held it for most of that time, so all four drivers were restarted onto a version with three
  slots. That version also puts all sandbox jobs in one shared 10.5 GB memory cgroup, so a job, never a harness or
  model process, is what gets killed if memory runs out. Each driver was killed only between model calls and
  resumed from its saved state: every message reached the model once, in order. A bug in the first resume code
  reused one turn number per run for the next call. The affected turn folders have a `NOTE.md` and an `orig/`
  copy, and one turn's raw event stream (budget 0, turn 9) is lost; its code and output are in `tool_calls.jsonl`.

## Licences

Code: MIT. The paper's networks fetched into `networks/paper/` and quoted parts of its prompt: CC BY 4.0, from
[RikiyaT/lm_understand-logs](https://github.com/RikiyaT/lm_understand-logs). Tracr: Apache 2.0. pgx: Apache 2.0.
