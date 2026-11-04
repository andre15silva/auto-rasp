#!/usr/bin/env bash
# Creates the two Python environments: /opt/venvs/rasp (harness + evaluation, with pgx) and /opt/venvs/sandbox
# (the writer's sandbox: tracr, jax, haiku, numpy, scipy, scikit-learn, PyTorch CPU, pandas, sympy, networkx;
# deliberately no Go library). Also needs bubblewrap (apt-get install bubblewrap) and the `claude` CLI.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRACR="git+https://github.com/google-deepmind/tracr@9ce2b8c82b6ba10e62e86cf6f390e7536d4fd2cd"
uv venv --python 3.11 /opt/venvs/rasp
uv pip install --python /opt/venvs/rasp/bin/python -r "$ROOT/requirements.txt"
uv venv --python 3.11 /opt/venvs/sandbox
uv pip install --python /opt/venvs/sandbox/bin/python "jax[cpu]==0.10.2" "dm-haiku==0.0.17" "numpy==2.4.6" scipy \
  scikit-learn pandas sympy networkx "$TRACR"
uv pip install --python /opt/venvs/sandbox/bin/python torch --index-url https://download.pytorch.org/whl/cpu
