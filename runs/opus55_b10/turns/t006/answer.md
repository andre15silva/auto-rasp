```python
import cProfile, pstats, io, sys, time
sys.path.insert(0,'/work')
code = open('/work/program.py').read().replace('range(6)','range(4)')
open('/work/prog_test.py','w').write(code)
import prog_test
from tracr.compiler import compiling
t0=time.time()
pr = cProfile.Profile(); pr.enable()
m = compiling.compile_rasp_to_model(prog_test.program(), vocab={".","x","o","B","W"}, max_seq_len=82, compiler_bos="BOS", mlp_exactness=100)
pr.disable()
print('time', time.time()-t0)
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('tottime').print_stats(25); print(s.getvalue()[:6000])
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(30); print(s.getvalue()[:7000])
```