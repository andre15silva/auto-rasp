79.3M params, MLP width 377, ≤3 heads, compile 315 s — comfortably within limits. The pair-class compression is verified to preserve the score function exactly. This is my final candidate (saving-capture bonus, ko downweighting, region/phase/cut features, slim schedule). Final games pass to validate it:

```games
{"games": {"strong": 96, "weak": 32}}
```