```python
import re
root='/opt/venvs/sandbox/lib/python3.11/site-packages/tracr'
def show(rel, start=0, end=None):
    src=open(root+rel).read()
    # strip license header
    lines=src.split('\n')
    out=[l for l in lines if not l.startswith('#')]
    s='\n'.join(out[start:end])
    print(f'===== {rel} =====')
    print(s)
show('/compiler/expr_to_craft_graph.py', 14)
show('/compiler/basis_inference.py', 14)
```