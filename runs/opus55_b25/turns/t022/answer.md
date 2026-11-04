```python
import numpy as np, json
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
keys = [k for k in d.files if k not in ('residual','residual_labels')]
print(keys)
lg = np.load('/work/pass_1/logits.npy')
def show(pos, names, idxs):
    for i in idxs:
        print(pos, i, divmod(i,9), {n: d[n][pos][i] for n in names}, 'logit', round(float(lg[pos][i]),2))
names = ['kind','W','RS1','RS2','stA','stB','RU','labA','escO','o2O','tab1','tab2','zone','gainR','tacP','tacN']
names = [n for n in names if n in d.files]
show(1, names, [9, 0, 1, 39, 30])
show(3, names, [17, 16, 8, 26])
show(2, names, [59, 58, 73, 64])
```