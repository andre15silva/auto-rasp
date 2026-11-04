The categorical values are right, but attention is noticeably soft (fetches give 0.9956 instead of 1). That matches logits being scaled by 1/sqrt(key_size)=1/sqrt(85), i.e. effective coldness ≈10.85. This means leakage of ~2e-5 per unselected key, which would break my tiny decode thresholds. Let me check how Tracr determines key_size and how bad the liberty decode actually is.

```python
import sys; sys.path.insert(0,'/work')
from _show import show
show('compiler/assemble.py', r'def _get_model_config_and_module_names', 0, 45, 1)
show('compiler/assemble.py', r'def _make_transformer_weights|query|w_qk', 2, 25, 3)
```