`/work/program.py` is finished. It compiles in about 25 s to 17 layers, 3 heads, residual width 2,226 and about 69M dense parameters. `compile_program()` timed it at 13–33 s per 1,000 positions, under the 60 s limit. I could not run the network, so none of the behaviour below has been observed in play; it rests on the design and my reasoning about Tracr's arithmetic.

**Timing risk.** The sandbox timing was very noisy: the same model measured 13 s and then 33 s. Earlier, larger versions (107–200M parameters) measured up to 54–59 s. I cut the design to this size so it stays under 60 s even when the machine is slow.

**What I dropped to get there.**
- **Two-liberty detection:** an exact two-liberty check for our own groups worked but added about 4 layers. Without it, a move that takes one of our two-liberty groups down to one liberty gets only a mild penalty, so some self-ataris will get through.
- **Atari-giving:** it needs the opponent's two-liberty count, so it is not in the network.
- **Opponent group size:** all captures are valued the same, whatever the number of stones taken.

**How the network computes things**
- **Attention as a lookup:** Tracr turns a selector's predicate value into the attention score. I return real numbers instead of true/false, so one head can do a weighted average over positions or pick the best-scoring one.
- **Groups:**
  - Every stone first takes the leftmost stone of its horizontal run as its label.
  - Three rounds then pass the smallest label through each group, with each stone also copying the label of the stone it points to. A group is labelled correctly if every stone is within about 7 steps of its smallest-index stone, which covers most real groups. Larger snaking groups can end up split into parts.
- **Liberties and atari:** each stone collects its empty neighbours. Averaging that over all stones with the same label gives the group's set of liberties.
  - **Atari:** one head checks whether that set has exactly one point.
  - **Big groups:** another counts stones and marks a group as big at 3 or more stones.
- **Garbage at the BOS position:** where an earlier result is used as an attention key, I pass it through a small MLP first so the BOS position can't interfere.

**How moves are scored.** Each empty point classifies its four neighbours: empty, edge, our stone in atari (small or big), our safe stone, opponent stone in atari, opponent safe stone. Lookup heads score that neighbour pattern, plus one pattern over a radius-2 window, and the four scores are summed:
- **Capture:** +25, plus a bit more for each extra adjacent stone in atari.
- **Saving our groups:** a big group in atari gets up to +30 if the escape gains liberties. A small one gets +8. A futile extension is penalised.
- **Self-atari:** −12.
- **Eyes and own territory:** filling our own eye is −40; filling a nearly closed own-territory point is −7.
- **Contact:** +1 for touching an opponent stone while keeping two empty neighbours.
- **Position and influence (radius-2 window):** third line and inside is +1, the first line is penalised. Contested areas get a bonus, deep own or opponent territory a penalty.
- **Pass:** scores −5 overall, so the network passes only when every remaining move is an eye fill, self-atari or own-territory fill.

All scores are multiplied by 3 to give the logits.

**Why I expect it to beat the weak RL policies.** They sample at temperature 1 and make tactical mistakes, and this network reliably:
- captures stones left in atari;
- rescues groups in atari, preferring big ones;
- avoids self-atari and never fills its own eyes;
- reduces and captures opponent stones inside its territory before passing, which matters because scoring removes no dead stones;
- plays reasonable opening points, with some randomness, among the central 5×5 points.

Its weak spots are ladders, deliberate eye-making, and the self-ataris described above.

The program is split across these files in `/work`:
- `program.py`
- `gocore.py`
- `gowin.py`
- `gotmpl10.py`