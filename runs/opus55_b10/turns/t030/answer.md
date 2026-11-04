The seeds are correct, but the first row-run round already averages the stone with some other position. Let me check whether the run ids from SelectorWidth are correct.

```python
import numpy as np, json, sys
sys.path.insert(0,'/work')
import goref
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
inp = json.load(open('/work/pass_1/inputs.json'))
toks = inp[0]['tokens']
print(len(toks), toks[:5], toks[-2:])
ridr = d['ridr_78'][0]; ridc = d['ridc_65'][0]
print('ridr grid'); print(np.array(ridr[:81]).reshape(9,9))
# expected
starts = []
for i in range(82):
    t = toks[i]
    if i == 81: st = True
    else:
        l = toks[i-1] if i % 9 else toks[81]
        st = (t not in ('x','o')) or (t != l)
    starts.append(st)
exp = [sum(1 for k in range(i+1) if starts[k]) for i in range(82)]
print('expected'); print(np.array(exp[:81]).reshape(9,9))
print(ridr[81], exp[81])
sw = d['ridr_78_selector_width_attn_output'][0]
print('attn out', np.round(sw[:20],4))
print('expected 1/(w+1)', np.round([1/(e+1) for e in exp[:20]],4))
```