"""Experiment 5: one reply, no tools, no feedback (the paper's protocol), for a RASP program.

    python -m harness.run_oneshot --game breakout --run-id opus55_minatar_breakout

One `claude -p` call (every Claude Code tool off, neutral system prompt, the prompt on stdin). The LAST ```python
block of the reply is written to work/program.py and compiled in the sandbox exactly as the evaluation does
(final/). If the call itself fails (API error, no reply), it is retried in a fresh session; the model never gets
any feedback on its answer.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from harness import passes, sandbox  # noqa: E402
from harness.prompt_minatar import task_prompt  # noqa: E402
from harness.run_writer import STRIP_ENV  # noqa: E402

PY_RE = re.compile(r"```python[^\n]*\n(.*?)```", re.DOTALL)


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="xhigh")
    ap.add_argument("--timeout", type=int, default=3 * 3600)
    ap.add_argument("--compile-only", action="store_true", help="re-read reply/answer.md and compile again")
    args = ap.parse_args()
    d = os.path.join(REPO, "runs", args.run_id)
    rep, work, fin = (os.path.join(d, x) for x in ("reply", "work", "final"))
    for x in (rep, work):
        os.makedirs(x, exist_ok=True)
    log = lambda m: (print(f"[{now()}] {m}", flush=True),  # noqa: E731
                     open(os.path.join(d, "loop.log"), "a").write(f"[{now()}] {m}\n"))
    if not args.compile_only:
        prompt = task_prompt(args.game)
        open(os.path.join(d, "message.txt"), "w").write(prompt)
        json.dump({"game": args.game, "model": args.model, "effort": args.effort, "protocol": "one-shot",
                   "vocab": "range(70)", "max_seq_len": 106}, open(os.path.join(d, "config.json"), "w"), indent=1)
        system = open(os.path.join(REPO, "harness", "instructions.md")).read().strip()
        cwd = os.path.join("/tmp", f"writer_{uuid.uuid4().hex[:8]}")
        os.makedirs(cwd, exist_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
        for attempt in range(6):
            sid = str(uuid.uuid4())
            cmd = ["claude", "-p", "--model", args.model, "--effort", args.effort, "--tools", "",
                   "--strict-mcp-config", "--safe-mode", "--disable-slash-commands", "--system-prompt", system,
                   "--output-format", "stream-json", "--verbose", "--session-id", sid]
            log(f"asking ({len(prompt):,} chars), attempt {attempt + 1}")
            t0 = time.time()
            try:
                p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd, env=env,
                                   timeout=args.timeout)
                out, err = p.stdout, p.stderr
            except subprocess.TimeoutExpired as e:
                out, err = (e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")), "timeout"
            wall = time.time() - t0
            sfx = "" if attempt == 0 else f".attempt{attempt + 1}"
            open(os.path.join(rep, f"events{sfx}.jsonl"), "w").write(out)
            open(os.path.join(rep, f"stderr{sfx}.log"), "w").write(err)
            events = []
            for line in out.splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            res = next((e for e in reversed(events) if e.get("type") == "result"), None)
            if res and not res.get("is_error") and res.get("result"):
                init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
                tools = [b for e in events if e.get("type") == "assistant"
                         for b in (e.get("message", {}).get("content") or []) if b.get("type") == "tool_use"]
                audit = {"tool_free": not tools and init.get("tools") == [] and init.get("mcp_servers") == [],
                         "init_tools": init.get("tools"), "init_mcp_servers": init.get("mcp_servers"),
                         "tool_uses": len(tools), "num_turns": res.get("num_turns")}
                if attempt:
                    for b in ("events", "stderr"):
                        ext = "jsonl" if b == "events" else "log"
                        os.replace(os.path.join(rep, f"{b}{sfx}.{ext}"), os.path.join(rep, f"{b}.{ext}"))
                json.dump({"cmd": cmd, "model": args.model, "effort": args.effort, "wall_s": round(wall, 1),
                           "usage": res.get("usage"), "model_usage": res.get("modelUsage"),
                           "cost_usd": res.get("total_cost_usd"), "stop_reason": res.get("stop_reason"),
                           "audit": audit, "attempts": attempt + 1, "session_id": sid},
                          open(os.path.join(rep, "run.json"), "w"), indent=1)
                open(os.path.join(rep, "answer.md"), "w").write(res["result"])
                log(f"reply received: {len(res['result']):,} chars, {wall:.0f}s, tool-free {audit['tool_free']}")
                break
            log(f"call failed (attempt {attempt + 1}): {(res or {}).get('result') or err[-300:]!r}")
            time.sleep(min(600, 30 * 2 ** attempt))
        else:
            log("giving up: no reply")
            return
    answer = open(os.path.join(rep, "answer.md")).read()
    blocks = PY_RE.findall(answer)
    if os.path.isdir(fin):
        shutil.rmtree(fin)
    os.makedirs(fin)
    if not blocks:
        json.dump({"ok": False, "error": "the reply has no ```python block"}, open(os.path.join(fin, "compile.json"), "w"))
        log("no python block in the reply: zero network")
        return
    open(os.path.join(work, "program.py"), "w").write(blocks[-1])
    passes.snapshot_sources(work, os.path.join(fin, "src"))
    res = sandbox.compile_in_sandbox(work, fin, task="minatar")
    log("final compile: " + json.dumps({k: v for k, v in res.items() if k != "error"})
        + (f" ERROR {res.get('error', '')[-800:]}" if not res.get("ok") else ""))


if __name__ == "__main__":
    main()
