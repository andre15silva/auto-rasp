```python
import cProfile, pstats, io, sys
sys.path.insert(0,'/work')
code = open('/work/program.py').read().replace('range(6)','range(2)')
open('/work/prog_test.py','w').write(code)
import importlib, prog_test
from tracr.compiler import compiling
pr = cProfile.Profile(); pr.enable()
m = compiling.compile_rasp_to_model(prog_test.program(), vocab={".","x","o","B","W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(40); print(s.getvalue()[:8000])
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('tottime').print_stats(20); print(s.getvalue()[:5000])
```