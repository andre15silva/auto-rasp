```python
import collections
labels = res['residual_labels']
cnt = collections.Counter(l.split(':')[0] for l in labels)
print(len(labels))
print(sorted(cnt.items(), key=lambda kv: -kv[1])[:60])
```