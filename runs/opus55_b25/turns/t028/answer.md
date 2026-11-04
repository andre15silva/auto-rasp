```python
import numpy as np, json
d = np.load('/work/pass_2/compiled.npz', allow_pickle=True)
pref = {k.rsplit('_',1)[0]: k for k in d.files if '_' in k}
inp = json.load(open('/work/pass_2/inputs.json'))
def chains(b):  # b: list of 81 chars '.', 'x','o'
    seen = {}; res = {}
    for i in range(81):
        if b[i] in 'xo' and i not in seen:
            stack=[i]; grp=set([i]); 
            while stack:
                j=stack.pop()
                for n in __import__('builtins').__dict__['list'](nb(j)):
                    if b[n]==b[i] and n not in grp: grp.add(n); stack.append(n)
            libs=set(n for j in grp for n in nb(j) if b[n]=='.')
            for j in grp: seen[j]=(frozenset(grp), frozenset(libs))
    return seen
def nb(i):
    r,c=divmod(i,9); out=[]
    for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
        if 0<=r+dr<9 and 0<=c+dc<9: out.append((r+dr)*9+c+dc)
    return out
def libs_after(b, p):
    b2=list(b); b2[p]='x'
    # remove captured o
    for n in nb(p):
        if b2[n]=='o':
            ch=chains(b2)[n]
            if len(ch[1])==0:
                for j in ch[0]: b2[j]='.'
    return len(chains(b2)[p][1])
errs=0
for pos, item in enumerate(inp):
    toks = item['tokens'] if 'tokens' in item else item.get('input_tokens')
    b = toks[:81]
    ch = chains(b)
    for i in range(81):
        if b[i] in 'xo':
            nl = len(ch[i][1])
            exp = ('X' if b[i]=='x' else 'O') + ('1' if nl==1 else 'm')
            got = str(d[pref['stA']][pos][i])
            expB = ('X' if b[i]=='x' else 'O') + ('2' if nl<=2 else '3')
            gotB = str(d[pref['stB']][pos][i])
            if exp!=got or expB!=gotB:
                errs+=1; print('stone', pos, divmod(i,9), 'libs', nl, got, gotB)
        else:
            la = libs_after(b, i)
            ru = str(d[pref['RU']][pos][i]); t1=str(d[pref['tab1']][pos][i]); t2=str(d[pref['tab2']][pos][i])
            # expected la class
            capt = any(b[n]=='o' and len(ch[n][1])==1 for n in nb(i))
            if not capt:
                lac = min(la,2)
                got_la = eval(t1)[2]
                if max(lac,1) != got_la:
                    errs+=1; print('empty', pos, divmod(i,9), 'la', la, 'tab1', t1, 'RU', ru)
print('errors', errs)
print(item.keys())
```