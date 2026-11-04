Now 281 s — the moderate logits (87) made it much slower. This confirms the float32 tiny-value theory: weights like e^-82 ≈ 2e-36 sit right at the denormal boundary. Exactness (logit gaps ≥ ~110 so losing weights underflow to exactly 0) is what keeps it fast. Let me restore exact gaps.

```python
s = open('/work/gonet.py').read()
s = s.replace("SEL = 8.0            # units; logit = 100*u/sqrt(K) ~ 10.9*u  -> 87", "SEL = 10.6           # units; logit = 100*u/sqrt(K) ~ 10.9*u -> 115.7 (gap to BOS 110 => exact 0 in float32)")
s = s.replace("G_LO, G_HI = 5.5, 11.0   # graded run-start search: farthest .. nearest candidate", "G_LO, G_HI = 10.6, 10.6 + 10.2 * 8   # graded: consecutive candidates 111 logits apart")
open('/work/gonet.py','w').write(s)
r = compile_program()
```