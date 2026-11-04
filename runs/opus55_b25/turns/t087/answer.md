```python
src = open('/work/program.py').read()
src = src.replace("        if capc >= 1: return ('cap', capc)\n", "        if capc >= 1: return ('cap', capc, int(nEc == 0 and not xn))\n")
src = src.replace("        if s[0] == 'cap': return TAC_CAP2 if s[1] >= 2 else TAC_CAP1\n",
                  "        if s[0] == 'cap':\n            if s[1] == 1 and s[2]: return TAC_KO\n            return TAC_CAP2 if s[1] >= 2 else TAC_CAP1\n")
src = src.replace("        if s[0] == 'cap': return BIG_CAP * capB\n",
                  "        if s[0] == 'cap':\n            if s[1] == 1 and s[2]: return (TAC_CAP1 - TAC_KO + BIG_CAP) if capB else 0\n            return BIG_CAP * capB\n")
src = src.replace("TAC_ESC_LADDER = 3", "TAC_ESC_LADDER = 3\nTAC_KO = -15")
open('/work/program.py','w').write(src)
import sys; sys.path.insert(0,'/work')
import importlib, program
importlib.reload(program)
res = compile_program()
```