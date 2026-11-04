```python
import numpy as np, json
d = np.load('/work/pass_5/compiled.npz', allow_pickle=True)
pref = {k.rsplit('_',1)[0]: k for k in d.files if '_' in k}
inp = json.load(open('/work/pass_5/inputs.json'))
def nb(i):
    r,c=divmod(i,9); out=[]
    for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
        if 0<=r+dr<9 and 0<=c+dc<9: out.append((r+dr)*9+c+dc)
    return out
def chains(b):
    seen={}
    for i in range(81):
        if b[i] in 'xo' and i not in seen:
            stack=[i]; grp={i}
            while stack:
                j=stack.pop()
                for n in nb(j):
                    if b[n]==b[i] and n not in grp: grp.add(n); stack.append(n)
            libs=frozenset(n for j in grp for n in nb(j) if b[n]=='.')
            for j in grp: seen[j]=(frozenset(grp), libs)
    return seen
def libs_after(b,p):
    b2=list(b); b2[p]='x'
    for n in nb(p):
        if b2[n]=='o':
            ch=chains(b2)[n]
            if len(ch[1])==0:
                for j in ch[0]: b2[j]='.'
    return len(chains(b2)[p][1])
for pos,item in enumerate(inp):
    b=item['tokens'][:81]; ch=chains(b); errs=[]
    for i in range(81):
        if b[i] in 'xo':
            # only care about stones adjacent to empties
            if not any(b[n]=='.' for n in nb(i)): continue
            nl=len(ch[i][1]); col='X' if b[i]=='x' else 'O'
            exp=col+('1' if nl==1 else 'm'); expB=col+('2' if nl<=2 else '3')
            got=str(d[pref['stA']][pos][i]); gotB=str(d[pref['stB']][pos][i])
            if exp!=got or expB!=gotB: errs.append(('stone',divmod(i,9),nl,got,gotB))
        else:
            t1=str(d[pref['tab1']][pos][i]); t2=str(d[pref['tab2']][pos][i])
            capt=any(b[n]=='o' and len(ch[n][1])==1 for n in nb(i))
            la=libs_after(b,i)
            exp_t2 = 'cap' if capt else ('SA' if la<=1 else 'ok')
            got_t2 = 'cap' if int(t2)>=20 else ('SA' if int(t2) in (-20,) else ('eye' if int(t2)==-25 else 'ok'))
            if got_t2=='eye': continue
            if exp_t2!=got_t2: errs.append(('empty',divmod(i,9),'la',la,'capt',capt,t1,t2))
    print(pos, len(errs), errs[:6])
```