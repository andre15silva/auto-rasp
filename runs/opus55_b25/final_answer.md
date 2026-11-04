The final network in `/work/program.py` beat the practice "strong" RL opponent in about **79% of games** (380 of 480, pooled over four passes). Against "weak" it won 94% and against random 100%, 16 games each. It compiles to 27 layers and 51M dense parameters. The passes timed it at 4–18 s per 1,000 positions, well under the 60 s limit.

The win rates for this exact configuration varied from pass to pass: 82%, 80.5%, 80.2% and 74.2% against strong (the 80.5% run used a sharper output scale). So expect roughly 75–82% against similar RL nets. Earlier versions without the contact bonus scored about 40%.

## How the program works
It is a set of local Go features computed by attention and small lookup tables, combined into an additive score for each move. A few properties of Tracr shaped the design:
- **Selector scores can be real numbers, not just true/false.** That gives weighted averages over chosen board points, histograms of neighbour types, and heads that pick the best-scoring "prototype" or threshold a linear function.
- **Tracr divides attention scores by √84.** I multiply every selector value by √84 to undo this.
- **Unselected keys get a very large negative score.** Without this, the forward pass produced near-zero (denormal) numbers that made the network about 17 times too slow (274 s per 1,000 positions) in two pass attempts.

**1. Liberties of each chain.** Every empty point gets one of 13 hash classes, chosen so that two points with the same class are at least 5 apart.
- Each stone gathers the classes of the empty points next to it and passes them along its own chain for 6 steps.
- Readout heads then decide whether a chain has 1, 2, or 3+ liberties.
- A second propagation of 4 more steps catches stones that can see more liberties further away, which reduces false atari calls on long chains.
- At each empty point the same machinery estimates how many liberties my stone would have there, which detects self-atari.
- A short local check marks chains of 3+ stones as "big".

**2. Neighbourhood summary.** At each empty point, the counts of each neighbour type (empty, edge, my or opponent chains by liberty count and size) are matched exactly against every possible combination of four neighbours.

**3. Move score.**
- Big positive: captures (more for big chains), escaping atari when the escape reaches 3+ liberties (much less when it only reaches 2, since that is likely a ladder), defending my 2-liberty chains, and putting opponent chains in atari.
- Big negative: self-atari and filling my own eyes.
- **Ko captures are pushed below pass.** This removed most losses by repeated board position, which had cost us games we were winning.
- **Contact bonus (+4) for safe moves touching an opponent stone.** This was the largest single gain, from about 40% to about 80%. The RL opponents often fall apart in close fights and lose whole groups.
- Positional terms: an influence map that classifies empty points as mine, theirs or contested, rewards claiming contested area, and penalises moves deep in the opponent's area or inside my own territory. A line table favours the centre and penalises the edge.
- Pass scores 0, so we pass only when every legal move is an eye-fill or self-atari. Early passing had been the main cause of losses in early versions.

## Why I expect it to win
The hidden opponents are RL policies sampled at temperature 1, like the practice opponent. Our net almost never misses a capture or an atari escape, and avoids self-atari and eye-filling. It also fights in contact, where these opponents often blunder whole groups: about 60% of our wins were total wipe-outs, with the opponent left with nothing on the board.

## Remaining weaknesses
- **Black is weaker than White.** About 73% versus 80%, because Black has to overcome 7.5 komi.
- **Big groups still die in capturing races.** Losses typically involve 15–20 of our stones being captured.
- **Some games are still lost by repeated board position.** This comes from rare false atari calls on very large chains (up to 6 per 128 games); I tried two fixes for it and both scored lower.