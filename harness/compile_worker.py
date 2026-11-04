# Runs INSIDE the sandbox (see sandbox.compile_in_sandbox): /work read-only, /out writable.
# Imports /work/program.py, compiles program() with the fixed settings, exports the weights to /out/model.npz,
# times the compiled network (timing only; outputs discarded) and, if /out/rasp_inputs.json exists, evaluates
# the RASP program on those token sequences for every SOp (memoized RASP evaluator) -> /out/rasp.npz.
import importlib.util
import json
import os
import sys
import time
import traceback

sys.path.insert(0, "/harness")
sys.path.insert(0, "/work")


def _fail(msg):
    json.dump({"ok": False, "error": msg[-6000:]}, open("/out/compile.json", "w"))
    sys.exit(0)


def main(timing=True):
    import numpy as np
    import tracr_policy as TP
    from tracr.rasp import rasp
    if not os.path.exists("/work/program.py"):
        _fail("/work/program.py does not exist")
    t0 = time.time()
    try:
        spec = importlib.util.spec_from_file_location("program", "/work/program.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        exact = int(getattr(mod, "MLP_EXACTNESS", 100))
        sop = mod.program()
        m = TP.compile_sop(sop, mlp_exactness=exact)
    except BaseException:
        _fail("compiling /work/program.py failed:\n" + traceback.format_exc())
    t_compile = time.time() - t0
    meta = TP.export(m, sop, "/out/model.npz", extra={"mlp_exactness": exact})
    res = {"ok": True, "stats": meta["stats"], "mlp_exactness": exact, "compile_seconds": round(t_compile, 1),
           "output_label": meta["output_label"]}
    if timing:
        # best of 3: the machine is shared by concurrent runs, and contention can only make a timing slower
        tm = TP.TracrModel("/out/model.npz")
        toks = np.array([["."] * 81 + ["B"]] * 128)
        tm.logits_from_tokens(toks[:8])
        times = []
        for _ in range(3):
            t1 = time.time()
            tm.logits_from_tokens(toks)
            times.append((time.time() - t1) * 1000 / 128)
        res["seconds_per_1000_positions"] = round(min(times), 2)
        res["timings_per_1000_positions"] = [round(t, 2) for t in times]
    rin = "/out/rasp_inputs.json"
    if os.path.exists(rin):
        rows = json.load(open(rin))
        from tracr.compiler import rasp_to_graph, nodes

        class Memo(rasp.DefaultRASPEvaluator):
            def __init__(self):
                super().__init__()
                self.cache = {}

            def evaluate(self, expr, xs):
                k = id(expr)
                if k not in self.cache:
                    self.cache[k] = rasp.DefaultRASPEvaluator.evaluate(self, expr, xs)
                return self.cache[k]

        graph = rasp_to_graph.extract_rasp_graph(sop).graph
        sops = [d[nodes.EXPR] for _, d in graph.nodes(data=True) if isinstance(d[nodes.EXPR], rasp.SOp)]
        vals = {s.label: [] for s in sops}
        t1 = time.time()
        for row in rows:
            ev = Memo()
            for s in sops:
                vals[s.label].append(ev.evaluate(s, list(row)))
        arrays = {}
        for s in sops:
            v = vals[s.label]
            if rasp.is_numerical(s):
                arrays[s.label] = np.array([[np.nan if x is None else float(x) for x in r] for r in v], np.float64)
            else:
                arrays[s.label] = np.array([[str(x) for x in r] for r in v])
        np.savez_compressed("/out/rasp.npz", **arrays)
        res["rasp_seconds"] = round(time.time() - t1, 1)
    json.dump(res, open("/out/compile.json", "w"), indent=1)
