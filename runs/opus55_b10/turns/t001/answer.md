```python
import os, sys, inspect, subprocess, re
import tracr
TR = os.path.dirname(tracr.__file__)
print(sys.version); print(TR)
print(subprocess.run(['bash','-lc','ls -la /work; nproc; free -g; python -c "import numpy; print(numpy.__version__)"'],capture_output=True,text=True).stdout)
def show(path, pattern, before=5, after=40, maxn=3):
    src=open(os.path.join(TR,path)).read().split('\n')
    n=0
    for k,l in enumerate(src):
        if re.search(pattern,l):
            print(f'--- {path}:{k}'); print('\n'.join(src[max(0,k-before):k+after])); n+=1
            if n>=maxn: break
show('compiler/basis_inference.py', r'is_numerical\(expr\)|Aggregate', 3, 30, 2)
show('rasp/rasp.py', r'class Comparison', 0, 45, 1)
show('rasp/rasp.py', r'class Select\(', 0, 30, 1)
show('craft/chamber/numerical_mlp.py', r'def _get_discretising_layer', 0, 60, 1)
try:
    print(inspect.getsource(compile_program)[:3000])
except Exception as e: print(e)
```