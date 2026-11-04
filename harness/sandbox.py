"""The writer's Python sandbox (bubblewrap), modelled on the paper's harness/sandbox.py.

/work (read-write, kept between runs) is the only writable folder; the rest of the file system is the read-only
/usr and the sandbox venv (tracr, jax, haiku, numpy, scipy, scikit-learn, PyTorch CPU, pandas, sympy, networkx;
no Go library). No network, a clean environment, TIMEOUT seconds and MEM bytes of address space per run, output
cut at MAX_OUT characters. All sandbox jobs (writer runs, pass compiles) of all concurrent experiment runs share
one global lock so that together they never exceed the machine's memory.
"""
import contextlib
import fcntl
import json
import os
import subprocess
import time

SANDBOX_VENV = os.environ.get("AUTORASP_SANDBOX_VENV", "/opt/venvs/sandbox")
TIMEOUT, MAX_OUT, MEM = 900, 20_000, 10 << 30
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCK = os.environ.get("AUTORASP_LOCK", "/tmp/autorasp-heavy.lock")
THREADS = "4"


@contextlib.contextmanager
def heavy_lock():
    """Serializes memory-heavy work (sandbox runs, compiles, passes) across all experiment runs on this machine."""
    with open(LOCK, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def bwrap_cmd(binds, code, chdir="/work"):
    cmd = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--clearenv",
           "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64",
           "--symlink", "usr/bin", "/bin", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
           "--ro-bind", SANDBOX_VENV, SANDBOX_VENV]
    for kind, src, dst in binds:
        cmd += [{"rw": "--bind", "ro": "--ro-bind"}[kind], src, dst]
    cmd += ["--chdir", chdir, "--setenv", "HOME", "/tmp", "--setenv", "PATH", "/usr/bin",
            "--setenv", "OMP_NUM_THREADS", THREADS, "--setenv", "OPENBLAS_NUM_THREADS", THREADS,
            "--setenv", "JAX_PLATFORMS", "cpu", "--setenv", "PYTHONWARNINGS", "ignore",
            "--setenv", "TF_CPP_MIN_LOG_LEVEL", "3",
            f"{SANDBOX_VENV}/bin/python", "-I", "-c", code]
    return cmd


def run(cmd, timeout=TIMEOUT):
    t0 = time.time()
    try:
        p = subprocess.run(["prlimit", f"--as={MEM}", "--"] + cmd, capture_output=True, text=True, timeout=timeout)
        out = p.stdout + (("\n[stderr]\n" + p.stderr[-6000:]) if p.stderr.strip() else "")
        rc = p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")) + f"\n[timed out after {timeout} s]"
        rc = -9
    return out, rc, time.time() - t0


def run_writer_code(code, work_dir, log):
    """One writer Python run: PRELUDE + code inside the sandbox; returns the (cut) printed output."""
    from .prelude import PRELUDE
    binds = [("rw", work_dir, "/work"),
             ("ro", os.path.join(REPO, "gorasp", "tracr_policy.py"), "/harness/tracr_policy.py")]
    with heavy_lock():
        out, rc, secs = run(bwrap_cmd(binds, PRELUDE + "\n" + code))
    if len(out) > MAX_OUT:
        out = out[:MAX_OUT] + f"\n[output cut at {MAX_OUT:,} characters]"
    with open(log, "a") as f:
        f.write(json.dumps({"t": time.time(), "kind": "python", "s": round(secs, 2), "code": code,
                            "out": out[:6000], "returncode": rc}) + "\n")
    return out or "(no output)"


def compile_in_sandbox(work_dir, out_dir, rasp_inputs=None, timing=True):
    """Compiles /work/program.py (read-only) exactly as the evaluation does; writes out_dir/model.npz and
    out_dir/compile.json (and out_dir/rasp.npz if rasp_inputs). Returns the compile.json dict."""
    os.makedirs(out_dir, exist_ok=True)
    if rasp_inputs is not None:
        json.dump(rasp_inputs, open(os.path.join(out_dir, "rasp_inputs.json"), "w"))
    worker = open(os.path.join(HERE, "compile_worker.py")).read()
    binds = [("ro", work_dir, "/work"), ("rw", out_dir, "/out"),
             ("ro", os.path.join(REPO, "gorasp", "tracr_policy.py"), "/harness/tracr_policy.py")]
    code = worker + f"\nmain(timing={bool(timing)})\n"
    with heavy_lock():
        out, rc, secs = run(bwrap_cmd(binds, code))
    res_path = os.path.join(out_dir, "compile.json")
    res = json.load(open(res_path)) if os.path.exists(res_path) else {}
    if not res.get("ok"):
        res = {"ok": False, "error": res.get("error") or out[-4000:] or f"compile failed (return code {rc})"}
    res["seconds_total"] = round(secs, 1)
    json.dump(res, open(res_path, "w"), indent=1)
    return res
