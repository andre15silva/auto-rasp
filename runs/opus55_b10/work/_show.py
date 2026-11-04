
import os, re, tracr
TR = os.path.dirname(tracr.__file__)
def show(path, pattern, before=5, after=40, maxn=3):
    src=open(os.path.join(TR,path)).read().split('\n')
    n=0
    for k,l in enumerate(src):
        if re.search(pattern,l):
            print(f'--- {path}:{k}'); print('\n'.join(src[max(0,k-before):k+after])); n+=1
            if n>=maxn: break
