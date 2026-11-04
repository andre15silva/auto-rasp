```python
import numpy as np
d = np.load('/work/pass_1/compiled.npz', allow_pickle=True)
lg = np.load('/work/pass_1/logits.npy')
pref = {k.rsplit('_',1)[0]: k for k in d.files if '_' in k}
def show(pos, names, idxs):
    for i in idxs:
        print(pos, i, divmod(i,9), 'logit', round(float(lg[pos][i]),2))
        print('   ', {n: d[pref[n]][pos][i] for n in names})
names = ['kind','W','RS1','RS2','stA','stB','U','RU','labA','escO','o2O','tab1','tab2','zone','gainR','tacP','tacN','linev','a2']
show(1, names, [9, 0, 1, 39, 30])
```