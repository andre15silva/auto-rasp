# "RASP Plays MinAtar" page

The published write-up of Experiment 5 (one-shot MinAtar RASP programs vs the paper's Astra networks).

- `gather.py` collects every number from `results/` and `runs/`. It also reads Astra's replies from a local clone of
  the paper's logs (`L` at the top), compiles nothing, and renders one real frame per game with the compiled
  network. Output: `data.json`.
- `build.py` fills `template.html` with that data and writes `rasp-plays-minatar.html`, the page as published.

Both scripts use absolute paths from the session that built the page; adjust `R`, `L` and `A` to rerun them.
