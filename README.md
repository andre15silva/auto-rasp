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

## Results

**The compiled transformers play Go, and well.** At every budget, Opus 5.5's RASP program compiled with stock
Tracr into a network that beats the paper's same-size PPO networks. These are 512×6 MLPs trained on 20.5 M
self-play games, and the writer never played them. At 0, 10 and 25 passes the compiled networks score 21–31
points above Astra's directly written weights on the main measure, under the identical protocol. They also win
the same-budget head-to-heads: narrowly at 0 and 10 passes, decisively at 25. At 50 passes the order reverses.

| passes | Opus 5.5 → RASP → Tracr: main | Astra → MLP weights: main | Opus vs Astra at the same budget (head-to-head) |
|---|---|---|---|
| 0 | **61.7 %** | 39.0 % | 54.5 % |
| 10 | **71.5 %** | 51.2 % | 54.5 % |
| 25 | **79.4 %** | 48.6 % | 81.1 % |
| 50 | 54.6 % | **78.5 %** | 15.7 % |

"main" is the paper's main measure: the win rate against the hidden RL opponents, averaged over the two PPO
networks (2,000 games each, s.e. ≈ 1.1 points). Head-to-heads are 1,000 games (s.e. ≈ 1.6).

- **No passes at all (budget 0).** Without ever running its network, Opus wrote a 17-layer program that wins 60.0 %
  and 63.5 % against the two PPO networks. Astra's zero-pass network scores 40.6 % and 37.5 %.
- **Best network (budget 25).** It wins 80.2 % and 78.5 % against the PPO networks, level with Astra's best
  (50-pass) network on the main measure. It beats every Astra network head-to-head, including the 50-pass one
  66.9 % of the time.
- **Budget 50 fell behind.** Its practice score against "strong" plateaued at about 40 % from its third games pass
  to its last (46 games passes). It used 118 of its 120 Python runs. It also designed around the speed limit (see
  the notes below), keeping only 9 board-dependent attention heads. Its network beats the PPO networks
  (55.4 % and 53.8 %) but loses to every Astra network head-to-head (15.7–38.9 %).
- **Head-to-heads are not transitive.** Budget 50 is above Astra's 0-pass network against PPO (54.6 vs 39.0 %) but
  loses to it head-to-head (38.9 %). Budget 0 is above Astra's 25-pass network against PPO (61.7 vs 48.6 %) but
  loses to it head-to-head (43.6 %).
- **Random.** Every network beats a uniform random player 99.7–100 % of the time.
- **One run per budget.** Run-to-run variance is unknown. The drop from budget 25 to budget 50 should not be read
  as an effect of the budget. Astra's own scores under this protocol are not monotonic either (10 passes: 51.2 %,
  25 passes: 48.6 %).
- **Ko and repetition.** Budget 0's network, which never saw a game, loses more games to the repeated-position rule
  (end by repetition in 159 and 108 of 2,000 games against the two PPO networks, against 16–33 for budgets 10 and
  25). The writers with passes learned to push ko recaptures below pass.

### Full evaluation

| writer | passes | vs PPO s0 | vs PPO s2 | **main** | vs random | vs Astra b0 | vs Astra b10 | vs Astra b25 | vs Astra b50 | compiled network |
|---|---|---|---|---|---|---|---|---|---|---|
| Opus 5.5 → RASP → Tracr | 0 | 60.0 | 63.5 | **61.7** | 99.7 | 54.5 | 49.6 | 43.6 | 35.9 | 17 layers, 2,226 dims, 148,742 nonzero of 69.5 M |
| Opus 5.5 → RASP → Tracr | 10 | 71.3 | 71.7 | **71.5** | 100.0 | 65.8 | 54.5 | 58.3 | 40.5 | 28 layers, 1,398 dims, 24,330 nonzero of 55.4 M |
| Opus 5.5 → RASP → Tracr | 25 | 80.2 | 78.5 | **79.4** | 100.0 | 94.9 | 80.4 | 81.1 | 66.9 | 27 layers, 829 dims, 174,536 nonzero of 51.3 M |
| Opus 5.5 → RASP → Tracr | 50 | 55.4 | 53.8 | **54.6** | 99.8 | 38.9 | 32.9 | 32.1 | 15.7 | 25 layers, 1,225 dims, 48,453 nonzero of 207.2 M |
| Astra (paper) → MLP weights | 0 | 40.6 | 37.5 | **39.0** | 99.8 | — | 45.6 | 51.7 | 14.6 | 243→512×6→82 (1.48 M) |
| Astra (paper) → MLP weights | 10 | 45.8 | 56.6 | **51.2** | 99.4 | 53.8 | — | 41.4 | 22.4 | same |
| Astra (paper) → MLP weights | 25 | 45.1 | 52.0 | **48.6** | 99.1 | 49.2 | 57.9 | — | 37.7 | same |
| Astra (paper) → MLP weights | 50 | 75.4 | 81.6 | **78.5** | 100.0 | 85.2 | 78.5 | 61.0 | — | same |

Win rates are in % for the row's network. It is Black in half of the games, and both sides sample at temperature 1.
There are 2,000 games per cell against PPO and random. Head-to-heads with Astra's networks are 2,000 games in the
Astra rows and 1,000 in the Opus rows. Sources: `results/<name>/eval.json` and `results/summary.md`.

The Astra rows are not the post's numbers. The post evaluated against smaller PPO networks that are not released;
see Protocol. Under our engine Astra's networks reproduce the paper's published head-to-heads (validation table
below).

### Practice games against "strong" (PPO seed 1), in pass order

| run | win rate vs "strong" per games pass (%) |
|---|---|
| budget 10 | 61 · 68 · 65 · 68 · 75 · 62 · 66 |
| budget 25 | 30 · 41 · 41 · 44 · 40 · 33 · 40 · **78** · 69 · 76 · 82 · 77 · 80 · 75 · 78 · 74 · 77 · 80 · 77 · 70 · 74 |
| budget 50 | 2 · 30 · 39 · 41 · 42 · 36 · 40 · 37 · 36 · 45 · 42 · 44 · 37 · 46 · 36 · 41 · 44 · 40 · 41 · 48 · … (46 passes, mean of the last 30: 42) |

Budget 25's jump at its 8th games pass came from one change, which its final answer describes: a +4 "contact"
bonus for safe moves that touch an opponent stone. In its words, "the RL opponents often fall apart in close fights
and lose whole groups".

### Writer runs

| run | turns | Python runs | games / positions passes | rejected pass requests | wall time | model time | cost (Claude Code's estimate) | output tokens | all turns tool-free |
|---|---|---|---|---|---|---|---|---|---|
| budget 0 | 61 | 61 | – | 0 | 3.6 h | 1.5 h | $809 | 0.59 M | yes |
| budget 10 | 116 | 106 | 7 / 3 | 0 | 6.3 h | 1.6 h | $1,872 | 0.55 M | yes |
| budget 25 | 128 | 101 | 21 / 4 | 2 | 4.5 h | 1.3 h | $1,671 | 0.43 M | yes |
| budget 50 | 170 | 118 | 46 / 4 | 2 | 8.4 h | 1.4 h | $2,717 | 0.45 M | yes |

The cost is Claude Code's list-price estimate (`total_cost_usd`), summed over turns: about $7,070 in total. Most
of it comes from re-reading the cached conversation on every turn (25–74 M cache-read tokens per run). Wall time
beyond model time went to sandbox runs, Tracr compiles (up to several minutes each) and passes, on a machine
shared by the four runs. Full numbers: `results/run_stats.json`.

### Did the compiled model do what the program says?

The evaluation was meant to check that the compiled network computes what the RASP program means, by comparing it
with `rasp.evaluate` of the same program. That check turned out to be mostly undefined: all four programs rely on
Tracr implementation details that RASP's reference evaluator does not share (see *What the writers found out
about Tracr* below). On positions from each
network's own games, `rasp.evaluate` fails on 46 of 61 SOps (budget 0), 131 of 163 (budget 10), 80 of 95
(budget 25) and 77 of 117 (budget 50), each time including the output. The programs were written for, and
iterated against, the compiled network, which is the only thing their move scores are defined for. The compiled
networks themselves were run with a NumPy forward pass that matches Tracr's own (`fast_runtime_check` = 0.0 on
256 positions for every network; the reference runtime matches Tracr's `apply` to about 1e-5).

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
| Hidden evaluation | 2,000 games vs small PPO networks seeds 0 and 2 (243→32→32→82; main = their mean), REINFORCE networks and random | 2,000 games vs the paper's **same-size** PPO networks seeds 0 and 2 (main = their mean) and random, plus 1,000-game head-to-heads vs **Astra's four written networks** (2,000 among Astra's own) |

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

**Validation of the Tracr runtime.** Every pass runs the compiled weights with
[`gorasp/tracr_policy.py`](gorasp/tracr_policy.py). This is a sparse NumPy implementation of Tracr's own Haiku
forward pass: no layer norm, attention logits divided by √key_size, ReLU MLPs, and input-independent attention
patterns cached. It matches `AssembledTransformerModel.apply` to about 1e-5
([`tests/test_tracr_policy.py`](tests/test_tracr_policy.py)). The hidden evaluation uses a faster variant,
[`gorasp/tracr_fast.py`](gorasp/tracr_fast.py), whose logits were identical to the reference on every evaluated
network (see Notes on the runs).

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
python eval/run_stats.py                                         # results/run_stats.json
python eval/summarize.py                                         # results/summary.md
```

The evaluations reported here ran with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`, `nice -n 19`, `--workers 2`
and `--ref-games 1000`.

`python -m harness.prompt 50` prints the exact task prompt (`runs/<id>/message.txt` holds the one each run got).

## Layout

| path | what |
|---|---|
| `gorasp/go.py` | batched pgx Go, the 243-plane encoding (for the paper's networks) and the token encoding (for Tracr) |
| `gorasp/policies.py`, `play.py`, `opponents.py` | policies, sampled batched play with the paper's summary fields, the opponent sets |
| `gorasp/tracr_policy.py` | compile, export the weights as sparse matrices, the reference forward pass (used by the passes), residual-stream decoding |
| `gorasp/tracr_fast.py` | the evaluation's forward pass: identical logits, with subnormals flushed to zero and a contiguous q·kᵀ matmul |
| `harness/prompt.py` | the task prompt (the paper's, with the network, sandbox and rules rewritten for RASP/Tracr) |
| `harness/run_writer.py` | the turn loop around `claude -p` / `claude -p --resume`, with per-turn audit |
| `harness/sandbox.py`, `prelude.py`, `compile_worker.py` | the bubblewrap sandbox, the writer's predefined names, and the compile done for passes and the evaluation |
| `harness/passes.py` | the games and positions passes |
| `eval/` | engine validation (`validate_engine.py`), hidden evaluation (`evaluate.py`), run statistics (`run_stats.py`), summary (`summarize.py`) |
| `scripts/` | environment setup, fetching the paper's networks, the run watcher and the safe driver restart used during the runs |
| `tests/` | the Tracr runtime test, an end-to-end harness test with scripted replies, and the harness-test RASP program (never shown to the writers) |
| `runs/<id>/` | one writer run: `message.txt` (task prompt), `turns/tNNN/` (`prompt.txt` sent, `answer.md` received, `events.jsonl` the raw Claude Code stream, `run.json` with usage and the tool-free audit), `tool_calls.jsonl` (every sandbox run's code and output and every pass), `work/` (the writer's files, pass summaries), `final/` (the final program's sources and compile record), `loop.log`, `state.json` |
| `results/` | `<name>/eval.json` per network, `summary.md`, `run_stats.json`, `validate_engine.json` and the evaluation logs |

Per-game records, boards, compiled weights and residual dumps are not committed (see `.gitignore`); they are
regenerated by the commands above.

## What the writers found out about Tracr

Each run read Tracr's source in its sandbox, as the prompt allowed, and wrote programs that target the compiler
rather than RASP's textbook semantics:

- **Selector predicates that return numbers.** All four final programs use predicates that return real numbers,
  not booleans. Tracr multiplies the predicate's value into the attention logit, so one head can compute a weighted
  average, pick the best-scoring key, or threshold a linear function. Budgets 0 and 25 also multiply their
  predicate values by √84 (`LSC = 100/sqrt(84)`, `FSC = sqrt(84)`) to undo the √key_size division described above.
  Budget 50 uses explicit "selected"/"unselected" score constants.
- **Subnormal numbers.** Budget 25 traced a 274 s per 1,000 positions timing to near-zero (subnormal) attention
  weights and changed its "unselected" score to a large negative one. Budget 50 found the same effect: "small
  leftover weights produced denormal numbers that made earlier versions 4–25 times slower".
- **MLP exactness.** Budgets 10 and 50 set `MLP_EXACTNESS` to 1,000,000 and 500,000; Tracr's default is 100.
- **Design around the speed limit.** Budget 50 noticed that heads whose query and key read only positions are
  nearly free in our runtime, since their pattern is cached, while each board-dependent head cost about 1 s per
  1,000 positions. Its final network has only 9 board-dependent heads.

**The programs are not valid RASP.** RASP's reference evaluator (`rasp.evaluate`) reads `bool(predicate)`, and a
categorical `Aggregate` over several selected keys raises an error there. So the "faithfulness" check planned for
the evaluation, which compares the compiled network's logits with `rasp.evaluate` of the same program, is mostly
undefined. The table under Results gives, for each program, how many of its SOps the reference evaluator can
compute at all. For budget 0 it fails on 46 of 61 SOps, including the output. These programs mean something only
as Tracr compilations.

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
- **Container restart.** At 00:07 UTC the container restarted and every process died. Budgets 10 and 50 were each
  in the middle of acting on a model answer that had already been saved. The restarted drivers acted on the saved
  answers, so again no model call was lost or repeated.
- **The speed limit was imperfect.** The prompt requires at most 60 s per 1,000 positions, measured by our runtime
  on 128 dummy positions (empty boards). Four problems emerged:
  1. **Load noise.** The four runs shared four cores, often at load 8–13, and a single timing varied up to 10×.
     From 22:00 UTC the check used the best of three timings, which affects only the passes and final checks after
     that time.
  2. **Stale cache.** Pass compiles are cached by source hash, so a program first timed under load kept its bad
     timing. We deleted three such cache entries, one in budget 25 and two in budget 50, so that they would be
     re-timed. Four pass requests in total were rejected as too slow: two in budget 25 and two in budget 50.
     Rejected requests did not count against the budget, but their games had already been played.
  3. **Unrepresentative inputs.** Empty boards are much cheaper than real positions, up to 4–6× for some networks.
  4. **A slow runtime.** The reference runtime's batched q·kᵀ matmul uses a transposed, non-contiguous key matrix,
     on which NumPy drops from BLAS to a loop about 60× slower.

  Problems 3 and 4 push in opposite directions. Overall the limit was looser than stated for some designs and
  tighter for others, especially those with many board-dependent attention heads. Budget 50 explicitly designed
  around it. We did not change the passes' runtime while runs were still going.
- **Evaluation runtime.** The hidden evaluation uses `gorasp/tracr_fast.py`. It flushes subnormal values to zero, as
  XLA does on CPU, and uses a contiguous key matrix. On 256 positions from each network's own games it gives
  logits identical to the reference runtime (`fast_runtime_check` in each `eval.json`), and it runs 2–5× faster.

## Licences

Code: MIT. The paper's networks fetched into `networks/paper/` and quoted parts of its prompt: CC BY 4.0, from
[RikiyaT/lm_understand-logs](https://github.com/RikiyaT/lm_understand-logs). Tracr: Apache 2.0. pgx: Apache 2.0.
