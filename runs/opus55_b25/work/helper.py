
root='/opt/venvs/sandbox/lib/python3.11/site-packages/tracr'
def show(rel, start=0, end=None, strip_doc=False):
    src=open(root+rel).read()
    lines=src.split('\n')
    out=[l for l in lines if not l.lstrip().startswith('#')]
    s='\n'.join(out[start:end])
    if strip_doc:
        import re
        s=re.sub(r'"""[\s\S]*?"""','',s)
    print(f'===== {rel} =====')
    print(s)
