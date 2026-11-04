I'll start by exploring the sandbox and the Tracr installation.

```python
import os, sys, subprocess
print(sys.version)
import tracr
print(tracr.__file__)
print(os.listdir('/work'))
print(subprocess.run(['bash','-c','ls -la /work; ls $(dirname %s); ls $(dirname %s)/compiler; nproc; free -g' % (tracr.__file__, tracr.__file__)],capture_output=True,text=True).stdout)
print([k for k in globals().keys() if not k.startswith('_')])
```