"""Code prepended to every writer Python run (inside the sandbox)."""
PRELUDE = r'''
import json, os, sys, time, importlib, numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=160)
sys.path.insert(0, "/work")
sys.path.insert(1, "/harness")
from tracr.rasp import rasp
from tracr.compiler import compiling
VOCAB = {".", "x", "o", "B", "W"}
MAX_SEQ_LEN = 82
BOS = "BOS"
PASS = 81
def pt(row, col):
    return row * 9 + col

def _not_allowed(*args, **kwargs):
    raise RuntimeError("not allowed: running the RASP program or the compiled network on an input outside the "
                       "pass tools (rule c)")
rasp.evaluate = _not_allowed
rasp.DefaultRASPEvaluator.evaluate = _not_allowed
rasp.RASPExpr.__call__ = _not_allowed
from tracr.compiler import assemble as _assemble
_assemble.AssembledTransformerModel.apply = _not_allowed
_compile_rasp_to_model = compiling.compile_rasp_to_model
def _compile_no_forward(*args, **kwargs):
    _m = _compile_rasp_to_model(*args, **kwargs)
    _m.forward = _not_allowed
    _m.get_compiled_model = _not_allowed
    return _m
compiling.compile_rasp_to_model = _compile_no_forward

def compile_program(path="/work/program.py", verbose=True):
    """Compiles path (default /work/program.py) exactly as the passes and the evaluation do and returns its size
    and speed; the compiled network is not run on any board (the speed is timed on dummy inputs, outputs
    discarded)."""
    import tracr_policy as _TP
    for _name in list(sys.modules):  # re-import the program and its helper modules from /work afresh
        _f = getattr(sys.modules[_name], "__file__", None) or ""
        if _f.startswith("/work/"):
            del sys.modules[_name]
    _spec = importlib.util.spec_from_file_location("program", path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _exact = int(getattr(_mod, "MLP_EXACTNESS", 100))
    _t0 = time.time()
    _sop = _mod.program()
    _m = _TP.compile_sop(_sop, mlp_exactness=_exact)
    _secs = time.time() - _t0
    _meta = _TP.export(_m, _sop, "/tmp/_model.npz")
    _tm = _TP.TracrModel("/tmp/_model.npz")
    _toks = np.array([["."] * 81 + ["B"]] * 128)
    _tm.logits_from_tokens(_toks[:8])
    _t1 = time.time()
    _tm.logits_from_tokens(_toks)
    _speed = (time.time() - _t1) * 1000 / 128
    os.remove("/tmp/_model.npz")
    _res = dict(_meta["stats"], mlp_exactness=_exact, compile_seconds=round(_secs, 1),
                seconds_per_1000_positions=round(_speed, 2), output_label=_meta["output_label"],
                residual_labels=_meta["residual_labels"])
    if verbose:
        print("compiled:", {k: v for k, v in _res.items() if k != "residual_labels"})
    return _res
'''
