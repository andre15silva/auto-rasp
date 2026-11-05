55.4M params (−30%), 28 layers, ≤2 heads, compile 203 s. That gives a much safer speed margin (≈38 s expected on the pass machine by scaling its last reading). Let me review the final program body for consistency.

```python
s = open('/work/go.py').read()
print(s[s.index('def program():'):])
print(open('/work/program.py').read())
```