"""End-to-end harness test with scripted replies instead of the model (no API calls)."""
import os
import shutil
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from harness import run_writer  # noqa: E402

SAMPLE = open(os.path.join(os.path.dirname(__file__), "sample_program.py")).read().replace("ROUNDS = 3", "ROUNDS = 1")
args = types.SimpleNamespace(run_id="_test", budget=3, model="none", effort="low", max_turns=10, turn_timeout=10,
                             seed=1, finalize_only=False)
d = os.path.join(run_writer.REPO, "runs", "_test")
shutil.rmtree(d, ignore_errors=True)
r = run_writer.Run(args)
replies = [
    "```python\nopen('/work/program.py','w').write(" + repr(SAMPLE) + ")\nres = compile_program()\n"
    "print(len(res['residual_labels']))\ntry:\n    rasp.evaluate(rasp.tokens, ['.'])\nexcept RuntimeError as e:\n"
    "    print('blocked:', e)\nimport socket\ntry:\n    socket.create_connection(('example.com', 80), 2)\n"
    "except Exception as e:\n    print('net:', type(e).__name__)\nprint(os.listdir('/'))\n```",
    "```games\n{\"games\": {\"strong\": 4, \"random\": 2}}\n```",
    "```games\n{\"games\": {\"strong\": 3}}\n```",
    "```positions\n{\"positions\": [{\"moves\": [40, 41, 31]}, {\"board\": [\".........\", \"..X......\", \".XOX.....\", "
    "\".........\", \".........\", \".........\", \".........\", \".........\", \".........\"], \"to_move\": \"black\"}], "
    "\"activations\": true, \"rasp\": true}\n```",
    "Two blocks ```python\nprint(1)\n``` and ```games\n{}\n```",
    "Final answer without blocks.",
]
for a in replies:
    kind, msg = r.act(a)
    print("=====", kind, "\n", (msg or "")[:1500])
print(sorted(os.listdir(os.path.join(d, "work"))), sorted(os.listdir(os.path.join(d, "work", "pass_2"))))
import numpy as np  # noqa: E402
c = np.load(os.path.join(d, "work", "pass_2", "compiled.npz"))
ra = np.load(os.path.join(d, "work", "pass_2", "rasp.npz"))
print("compiled sops", len(c.files), "rasp sops", len(ra.files), "common", len(set(c.files) & set(ra.files)))
