All 50 passes are used. `/work/program.py` (which imports `/work/gonet4.py`, with `MLP_EXACTNESS = 500000`) is the final network. It compiles in about 39 s and runs at about 11 s per 1,000 positions on the evaluation machine, well under the 60 s limit.

**Results of the final network** (practice opponents, about 3,800 games in total):
- **Strong RL policy:** about 41.6% wins over 3,200 games. It wins about 30% as Black and about 53% as White, the difference being mostly komi.
- **Weak opponent:** about 70% wins over 128 games.
- **Random player:** 100% wins.

The hidden RL opponents beat a random player 97–98% of the time, slightly less than "strong" (98.7%). I therefore expect a score of about 40–50% against them and about 100% against the random player.

**How the program is built.** The design is shaped by how the timing harness works. Attention heads whose query and key read only position information have their pattern computed once, so they are nearly free; every head that depends on the board costs about 1 s per 1,000 positions. The network therefore uses only 9 board-dependent heads. Everything else is position-based attention or small lookup MLPs.

1. **Local view.** Position-based heads copy each point's 8 neighbours. Index 81, the side-to-move token, stands in for "off board".
2. **Runs.** For each point, one head finds the start of its horizontal run of same-coloured points and another the start of its vertical run. Each step of the search is far enough apart in attention score that losing candidates get exactly zero weight. This exactness matters: small leftover weights produced denormal numbers that made earlier versions 4–25 times slower.
3. **Group information in one bundle.** Each point carries one categorical vector holding:
   - which of 8 liberty "buckets" its empty neighbours fall into (bucket = (row + 3·col) mod 8);
   - whether it touches our stones or the opponent's.

   This vector is averaged along horizontal and vertical runs in alternation, 7 times, one head per step. Averaging keeps every bucket that is present anywhere in the group, so each stone ends up knowing its group's liberty buckets. The values are thresholded only once at the end. The bucket count gives 1, 2 or 3+ liberties; it misreads only about 1–3% of groups. The same pass gives Tromp-Taylor regions (empty areas touching only us, only them, or both).
4. **Tactical score for each empty point.** It is looked up from its four neighbours' classes:
   - neighbour classes are empty, edge, our group with 1, 2 or 3+ liberties, or their group with 1 or 2 liberties;
   - a group's size is approximated by whether it has more than one stone;
   - the score covers captures, escaping atari, self-atari and suicide, putting the opponent in atari, defending our 2-liberty groups, moves that gain no liberty, and contact shape.
5. **Positional terms:**
   - large penalties for filling real eyes and smaller ones for false eyes;
   - small penalties for playing inside our own or the opponent's region;
   - a preference by distance from the edge that depends on the game phase (counted by stones on the board), favouring the centre early;
   - a bonus or penalty from counts of our and their stones within distance 2.
6. **Pass and endgame decisions.** One head averages over the whole board to get an exact Tromp-Taylor score estimate and a count of neutral points.
   - Pass only when nothing better is left; passing earlier gave the opponent about 2.5 free moves per game.
   - When the estimate says we are losing in a settled position, invade the opponent's regions. An invading stone left uncaptured neutralises the whole region under this scoring, and the opponent bot often misplays or fills its own eyes in such positions.

**Why I expect it to win some games.** The tactics are exact enough that random play is beaten every time. Against the RL policies, the win rate rose from 1.5% with a local-only first version, to 30% with group tactics, to about 42% after fixing a silent bug. Tracr's categorical-to-numerical layers clip negative values to zero, so all penalties had been ignored; adding constant offsets made them work.

Most remaining losses are close (within about 10 points), mainly as Black. They come from reading fights and endgame precision that this static evaluation cannot capture.