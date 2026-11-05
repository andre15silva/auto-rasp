| writer | passes | vs PPO s0 | vs PPO s2 | **main** | vs random | vs Astra b0 | vs Astra b10 | vs Astra b25 | vs Astra b50 | network |
|---|---|---|---|---|---|---|---|---|---|---|
| Opus 5.5 → RASP → Tracr | 0 | 60.0 | 63.5 | **61.7** | 99.7 | 54.5 | 49.6 | 43.6 | 35.9 | 17 layers, 2226 dims, 148,742 nonzero / 69,471,022 |
| Opus 5.5 → RASP → Tracr | 10 | 71.3 | 71.7 | **71.5** | 100.0 | 65.8 | 54.5 | 58.3 | 40.5 | 28 layers, 1398 dims, 24,330 nonzero / 55,421,648 |
| Opus 5.5 → RASP → Tracr | 25 | 80.2 | 78.5 | **79.4** | 100.0 | 94.9 | 80.4 | 81.1 | 66.9 | 27 layers, 829 dims, 174,536 nonzero / 51,326,847 |
| Opus 5.5 → RASP → Tracr | 50 | 55.4 | 53.8 | **54.6** | 99.8 | 38.9 | 32.9 | 32.1 | 15.7 | 25 layers, 1225 dims, 48,453 nonzero / 207,175,250 |
| Astra (paper) → MLP weights | 0 | 40.6 | 37.5 | **39.0** | 99.8 | — | 45.6 | 51.7 | 14.6 | 243→512×6→82 |
| Astra (paper) → MLP weights | 10 | 45.8 | 56.6 | **51.2** | 99.4 | 53.8 | — | 41.4 | 22.4 | 243→512×6→82 |
| Astra (paper) → MLP weights | 25 | 45.1 | 52.0 | **48.6** | 99.1 | 49.2 | 57.9 | — | 37.7 | 243→512×6→82 |
| Astra (paper) → MLP weights | 50 | 75.4 | 81.6 | **78.5** | 100.0 | 85.2 | 78.5 | 61.0 | — | 243→512×6→82 |

Win rates in % of the row's network, Black in half of the games, both sides sampling at temperature 1. 2,000 games per cell against PPO and random (1 s.e. ≈ 1.1 points at 50 %); head-to-heads against Astra's networks: 2,000 games in the Astra rows, 1,000 in the Opus rows (1 s.e. ≈ 1.6 points). main = mean of the two PPO columns (the paper's main measure, here with its same-size PPO networks).

Can RASP's reference evaluator run the program? (`rasp.evaluate` per SOp on 256 positions from the network's games vs PPO s0; and the evaluation runtime vs the passes' reference runtime)

| run | SOps | SOps rasp.evaluate fails on | output evaluable | first error | eval runtime vs reference (max abs logit diff) |
|---|---|---|---|---|---|
| opus55_b0 | 61 | 46 | no | ValueError: Only types int, bool, and float are supported for aggregation. | 0.0 |
| opus55_b10 | 163 | 131 | no | ValueError: Only types int, bool, and float are supported for aggregation. | 0.0 |
| opus55_b25 | 95 | 80 | no | ValueError: Only types int, bool, and float are supported for aggregation. | 0.0 |
| opus55_b50 | 117 | 77 | no | ValueError: Only types int, bool, and float are supported for aggregation. | 0.0 |

Writer runs:

| run | turns | Python runs | passes used | finished |
|---|---|---|---|---|
| opus55_b0 | 61 | 61 | 0/0 | True |
| opus55_b10 | 116 | 106 | 10/10 | True |
| opus55_b25 | 128 | 101 | 25/25 | True |
| opus55_b50 | 170 | 118 | 50/50 | True |
