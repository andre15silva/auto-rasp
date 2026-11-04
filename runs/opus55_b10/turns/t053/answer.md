Strong first result: 61% vs the strong RL net, 87.5% vs weak, 100% vs random — with heavy capturing (56.7 stones captured per game vs strong). The measured speed on the pass machine was 43.6 s/1000, so I must not grow the model. Let me analyze the losses.

```python
import json, numpy as np
g = json.load(open('/work/pass_3/games.json'))
print(len(g), g[0].keys())
boards = np.load('/work/pass_3/boards.npy'); valid = np.load('/work/pass_3/valid.npy')
for i, gm in enumerate(g):
    if gm['opponent'] == 'strong' and gm['result'] < 0:
        mv = gm['moves']
        npass = sum(1 for m in mv if m['move'] == 81 and m['by'] == 'net')
        print(i, gm['net_color'], 'margin', gm['margin'], 'end', gm['end'], 'cap', gm.get('stones_captured'), 'lost', gm.get('stones_lost'), 'len', len(mv), 'netpasses', npass)
print('repetition games:', [(i, gm['opponent'], gm['result'], gm['net_color']) for i, gm in enumerate(g) if gm['end'] == 'repetition'])
print(g[0]['moves'][:6])
```