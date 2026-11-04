Timing is inconsistent with any simple size model. Let me look for the implementation of `compile_program`/the timing code on disk.

```python
import subprocess
out = subprocess.run(['bash','-c','grep -rl "seconds_per_1000_positions" / --include=*.py 2>/dev/null | head; ls -la /opt /opt/* 2>/dev/null | head -50'],capture_output=True,text=True)
print(out.stdout[-5000:], out.stderr[-2000:])
```