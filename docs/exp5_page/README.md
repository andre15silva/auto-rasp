# "RASP Plays MinAtar" page

The published write-up of Experiment 5 (one-shot MinAtar RASP programs vs the paper's Astra networks).

- `gather.py` collects every number from `results/` and `runs/`. It also reads Astra's replies from a local clone of
  the paper's logs (`L` at the top), compiles nothing, and renders one real frame per game with the compiled
  network. Output: `data.json`.
- `arch_compare.py` measures both kinds of network for the "Two very different networks" section: Astra's
  hand-written 600→32→32→6 MLP and Opus's compiled Tracr transformer (parameters as assembled and nonzero,
  multiply-adds per move as assembled and over nonzero weights only, which inputs and hidden units Astra uses).
  Run from the repo root in the rasp venv. Output: `arch_compare.json`.
- `build.py` fills `template.html` with `data.json` and `arch_compare.json` (including the Breakout schematic drawn
  to scale and the log-scale size chart) and writes `rasp-plays-minatar.html`, the page as published.

`gather.py` and `build.py` use absolute paths from the session that built the page; adjust `R`, `L` and `A` to rerun them.
