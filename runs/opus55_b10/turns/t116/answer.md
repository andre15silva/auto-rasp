The final program is in place: `/work/program.py` imports `program()` from `/work/go.py` and sets `MLP_EXACTNESS = 1000000`. It compiles in about 200 s into a 55M-parameter network with 28 layers and at most 2 heads per layer.

**This exact final version was never played in a games pass.** After the last pass I removed two features for speed. Every piece it still contains was checked in earlier passes, but not this combination.

## Results from the practice passes
| Pass | Version | vs strong | vs weak |
|---|---|---|---|
| 3 | first version | 61% | 87.5% |
| 4 | sharper positional play | 67.5% | 87.5% |
| 7 | + phase, cut and territory features | 67.7% | 87.5% |
| 8 | + saving-capture bonus, ko change (100M params) | 75% | 87.5% |
| 9 | slimmed, no cut feature | 62.5% | 94% |
| 10 | slimmed, cut feature restored (79M params) | 65.6% | 78% |

- **Random opponent:** 100% in every pass that included it.
- **Expected strength:** roughly 60–70% against RL nets like the practice "strong" one, and near 100% against random. Differences of about 5–10 points between passes are within noise at 96 games.
- **Why I slimmed it:** the pass machine measured 52 s and 54 s per 1,000 positions for the 100M and 79M models, close to the 60 s limit. Going over it would mean all-zero logits (uniform random play). Removing the territory and cut features, neither of which showed a clear gain, cut parameters by 30%; scaling its last reading suggests about 38 s.

## How the network decides
**Group liberties.** For every stone, the network computes how many liberties its group has: 1, 2, or 3 or more.
- Each stone starts with the rows and columns of its adjacent empty points.
- This information is averaged across its group six times, alternating along straight row and column segments of same-coloured stones.
- After each round, tiny amounts that leak in from unrelated points are subtracted off, so they cannot add up.
- The group has 1 liberty exactly when all its liberties share one row and one column; it has 3 or more when they span 3 rows or 3 columns. Otherwise it counts as 2.
- In a check against exact Go rules on 100 realistic positions, 99.8% of stones got the right class.

**Move score.** Each empty point is scored from the liberty classes of its four neighbours:
- capturing a group in atari: +10, but only +3 for a ko-shaped capture, which reduces losses from repeated positions;
- an extra bonus for capturing a stone that is itself attacking one of our groups in atari;
- saving our own group in atari: +7 to +10, depending on how many liberties it ends up with;
- putting an opponent group in atari, or giving our 2-liberty group more liberties: smaller bonuses;
- self-atari: −12, and a smaller penalty when it might be self-atari;
- filling one of our own eyes: −15.

A positional score is added on top:
- the density of each colour within distance 2 and whether the point touches our or the opponent's stones;
- the distance to the edge, with heavier penalties for 1st- and 2nd-line moves in the opening;
- moves inside our own area are scored below passing, so the network passes only when nothing useful is left.

## Engineering notes
- **Custom selectors:** relations such as "is a neighbour of" are written as Python objects used as selector values.
- **Attention is soft:** Tracr divides attention scores by the square root of the key size (85), which makes attention noticeably soft. Every selector therefore always matches at least one position, and any count fed to `SelectorWidth` is first rounded back to an exact value.
- **Map merging:** consecutive `rasp.Map`s are combined by default, which silently removed my thresholds; every Map uses `simplify=False`.
- **Compile time:** Tracr's graph builder duplicates work for every path through the program, so the program was built to keep that count low. That keeps compilation at about 200 s.
- **Layer scheduling:** the ordering of operations was arranged so attention heads spread evenly across layers and no layers are wasted.