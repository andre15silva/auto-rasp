"""Drives one writer run: Claude (via the Claude Code CLI, all tools switched off) writes a RASP program for 9x9 Go.

Mirrors the paper's harness: one model turn per CLI call (`claude -p`, then `claude -p --resume <session>`), the
prompt on stdin. Each reply may hold exactly one ```python block (run in our sandbox), one ```games or
```positions block (a pass), or none (the final answer). We send back the output as the next message.

    python -m harness.run_writer --budget 50 --run-id b50            # new run (or resumes runs/b50 if it exists)
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from harness import passes, sandbox  # noqa: E402
from harness.prompt import task_prompt  # noqa: E402

BLOCK_RE = re.compile(r"```(python|games|positions)[^\n]*\n(.*?)```", re.DOTALL)
MAX_PY = 120
STRIP_ENV = ("CLAUDE_CODE_USER_EMAIL", "CLAUDE_CODE_REMOTE_SESSION_ID", "CLAUDE_CODE_SESSION_ID",
             "CLAUDE_CODE_ACCOUNT_UUID", "CLAUDE_CODE_ORGANIZATION_UUID")


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")


class Run:
    def __init__(self, args):
        self.args = args
        self.dir = os.path.join(REPO, "runs", args.run_id)
        self.work = os.path.join(self.dir, "work")
        self.cc_cwd = os.path.join("/tmp", f"writer_{uuid.uuid4().hex[:8]}")
        os.makedirs(self.work, exist_ok=True)
        os.makedirs(os.path.join(self.dir, "turns"), exist_ok=True)
        os.makedirs(self.cc_cwd, exist_ok=True)
        self.state_path = os.path.join(self.dir, "state.json")
        if os.path.exists(self.state_path):
            self.state = json.load(open(self.state_path))
        else:
            self.state = {"budget": args.budget, "model": args.model, "effort": args.effort, "session_id": None,
                          "turn": 0, "runs": 0, "passes": 0, "requests": 0, "done": False, "next": None,
                          "started": now()}
        self.budget = self.state["budget"]
        self.log_path = os.path.join(self.dir, "loop.log")
        self.calls_path = os.path.join(self.dir, "tool_calls.jsonl")

    def log(self, msg):
        line = f"[{now()}] {msg}"
        print(line, flush=True)
        open(self.log_path, "a").write(line + "\n")

    def save(self):
        json.dump(self.state, open(self.state_path, "w"), indent=1)

    # ---- one model turn
    def call_model(self, message):
        st = self.state
        tdir = os.path.join(self.dir, "turns", f"t{st['turn']:03d}")
        os.makedirs(tdir, exist_ok=True)
        open(os.path.join(tdir, "prompt.txt"), "w").write(message)
        base = ["claude", "-p", "--model", st["model"], "--effort", st["effort"], "--tools", "",
                "--strict-mcp-config", "--safe-mode", "--disable-slash-commands",
                "--system-prompt", open(os.path.join(REPO, "harness", "instructions.md")).read().strip(),
                "--output-format", "stream-json", "--verbose"]
        env = {k: v for k, v in os.environ.items() if k not in STRIP_ENV}
        for attempt in range(8):
            new = not st.get("session_started")
            if new:  # (re)start the conversation under a fresh id until its first turn succeeds
                st["session_id"] = str(uuid.uuid4())
                self.save()
            cmd = base + (["--session-id", st["session_id"]] if new else ["--resume", st["session_id"]])
            t0 = time.time()
            try:
                p = subprocess.run(cmd, input=message, capture_output=True, text=True, cwd=self.cc_cwd, env=env,
                                   timeout=self.args.turn_timeout)
                stdout, stderr, rc = p.stdout, p.stderr, p.returncode
            except subprocess.TimeoutExpired as e:
                stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
                stderr, rc = "timeout", -9
            wall = time.time() - t0
            sfx = "" if attempt == 0 else f".fail{attempt}"
            open(os.path.join(tdir, f"events{sfx}.jsonl"), "w").write(stdout)
            open(os.path.join(tdir, f"stderr{sfx}.log"), "w").write(stderr)
            events = []
            for line in stdout.splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            result = next((e for e in reversed(events) if e.get("type") == "result"), None)
            if result is not None and not result.get("is_error") and result.get("result") is not None:
                st["session_started"] = True
                init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
                tool_uses = [b for e in events if e.get("type") == "assistant"
                             for b in (e.get("message", {}).get("content") or []) if b.get("type") == "tool_use"]
                audit = {"tool_free": not tool_uses and init.get("tools") == [] and init.get("mcp_servers") == [],
                         "init_tools": init.get("tools"), "init_mcp_servers": init.get("mcp_servers"),
                         "tool_uses": len(tool_uses)}
                if attempt:  # keep the successful attempt under the plain names
                    os.replace(os.path.join(tdir, f"events{sfx}.jsonl"), os.path.join(tdir, "events.jsonl"))
                    os.replace(os.path.join(tdir, f"stderr{sfx}.log"), os.path.join(tdir, "stderr.log"))
                run = {"cmd": cmd, "model": st["model"], "effort": st["effort"], "wall_s": round(wall, 1),
                       "usage": result.get("usage"), "model_usage": result.get("modelUsage"),
                       "cost_usd": result.get("total_cost_usd"), "num_turns": result.get("num_turns"),
                       "stop_reason": result.get("stop_reason"), "audit": audit, "attempts": attempt + 1}
                json.dump(run, open(os.path.join(tdir, "run.json"), "w"), indent=1)
                answer = result["result"]
                open(os.path.join(tdir, "answer.md"), "w").write(answer)
                if not audit["tool_free"]:
                    self.log(f"WARNING: turn {st['turn']} audit failed: {audit}")
                return answer, audit
            self.log(f"turn {st['turn']}: model call failed (attempt {attempt + 1}, rc {rc}): "
                     f"{(result or {}).get('result') or stderr[-300:]!r}")
            time.sleep(min(600, 30 * 2 ** attempt))
        raise RuntimeError("model call failed 8 times")

    # ---- the harness's reply to one model answer
    def act(self, answer):
        st, budget = self.state, self.budget
        blocks = BLOCK_RE.findall(answer)
        left = budget - st["passes"]
        if not blocks:
            if left > 0:
                return "reminder", (f"You still have {left} of your {budget} passes. The session continues until "
                                    "every pass is used: use them (reply with one ```games or ```positions block), "
                                    "then finish.")
            return "final", None
        if len(blocks) > 1:
            return "error", (f"Your reply contained {len(blocks)} blocks (```python / ```games / ```positions); reply "
                             "with exactly one. Nothing was run.")
        kind, body = blocks[0]
        if kind == "python":
            if st["runs"] >= MAX_PY:
                return "error", f"You have used all {MAX_PY} Python runs; nothing was run."
            st["runs"] += 1
            out = sandbox.run_writer_code(body, self.work, self.calls_path)
            return "python", f"OUTPUT of Python run {st['runs']} of at most {MAX_PY}:\n```\n{out}\n```"
        if budget == 0:
            return "error", "You have no pass tools (budget 0); nothing was run."
        if left <= 0:
            return "error", f"All {budget} passes are used; nothing was run."
        st["requests"] += 1
        try:
            req = json.loads(body)
        except json.JSONDecodeError as e:
            res = {"ok": False, "error": f"invalid JSON: {e}"}
        else:
            k = st["passes"] + 1
            t0 = time.time()
            try:
                if kind == "games":
                    res = passes.games_pass(req, self.dir, k, seed=self.args.seed * 100 + k)
                else:
                    res = passes.positions_pass(req, self.dir, k)
            except Exception as e:  # noqa: BLE001  (a harness-side failure is reported, not counted)
                import traceback
                res = {"ok": False, "error": f"the pass failed: {type(e).__name__}: {e}"}
                self.log("pass exception:\n" + traceback.format_exc())
            if res.get("ok") and kind == "games" and (res.get("seconds_per_1000_positions") or 0) > 60:
                res = {"ok": False, "error": f"your compiled network takes {res['seconds_per_1000_positions']} s per "
                                             "1,000 positions, over the limit of 60 s; its games were not counted"}
            with open(self.calls_path, "a") as f:
                f.write(json.dumps({"t": time.time(), "kind": kind, "s": round(time.time() - t0, 1), "request": req,
                                    "result": {k2: v for k2, v in res.items() if k2 != "top3"}}) + "\n")
            os.makedirs(os.path.join(self.dir, "requests"), exist_ok=True)
            json.dump(req, open(os.path.join(self.dir, "requests", f"{kind}_{st['requests']}.json"), "w"))
        if not res.get("ok"):
            return "error", (f"The {kind} pass request failed and was not counted:\n```\n{res.get('error')}\n```\n"
                             f"Passes left: {budget - st['passes']}.")
        st["passes"] += 1
        top3 = res.pop("top3", None)
        msg = f"{kind.capitalize()} pass {st['passes']} of {budget} done.\n```\n{json.dumps(res)}\n```\n"
        if top3:
            msg += "Top 3 moves per position:\n```\n" + "\n".join(top3) + "\n```\n"
        return kind, msg + f"Passes left: {budget - st['passes']}."

    def _pending_answer(self):
        """After a restart: (the current turn's answer if the model answered but the harness had not acted,
        whether the model must be asked again within the same turn)."""
        st = self.state
        if st["turn"] < 1 or st.get("acted") == st["turn"]:
            return None, False
        tdir = os.path.join(self.dir, "turns", f"t{st['turn']:03d}")
        answered = os.path.exists(os.path.join(tdir, "run.json")) and os.path.exists(os.path.join(tdir, "answer.md"))
        same_prompt = (os.path.exists(os.path.join(tdir, "prompt.txt"))
                       and open(os.path.join(tdir, "prompt.txt")).read() == st["next"])
        if "acted" not in st and not same_prompt:
            return None, False  # (state from before 'acted' existed) the turn was completed
        if answered:  # act on it; the next model call is a new turn
            return open(os.path.join(tdir, "answer.md")).read(), False
        return None, True  # interrupted during the model call: ask again in the same turn

    def loop(self):
        st = self.state
        if st["done"]:
            self.log("run already finished")
            return
        msg = st["next"] or task_prompt(self.budget)
        if st["turn"] == 0:
            open(os.path.join(self.dir, "message.txt"), "w").write(msg)
            json.dump({"budget": self.budget, "model": st["model"], "effort": st["effort"]},
                      open(os.path.join(self.dir, "config.json"), "w"))
        pending, same_turn = self._pending_answer()
        while True:
            if pending is not None:
                answer = pending
                audit = json.load(open(os.path.join(self.dir, "turns", f"t{st['turn']:03d}", "run.json")))["audit"]
                self.log(f"turn {st['turn']}: resumed after a restart; acting on the saved answer")
                pending = None
            else:
                if not same_turn:
                    if st["turn"] >= self.args.max_turns:
                        self.log(f"stopped at the turn limit ({self.args.max_turns})")
                        break
                    st["turn"] += 1
                same_turn = False
                st["next"] = msg
                self.save()
                self.log(f"turn {st['turn']}: {'new session' if st['turn'] == 1 else 'resume'} ({len(msg):,} chars)")
                answer, audit = self.call_model(msg)
            kind, msg = self.act(answer)
            st["acted"] = st["turn"]
            self.log(f"turn {st['turn']}: {kind}; runs {st['runs']}, passes {st['passes']}/{self.budget}, "
                     f"tool-free {audit['tool_free']}")
            if kind == "final":
                open(os.path.join(self.dir, "final_answer.md"), "w").write(answer)
                st["done"], st["next"], st["finished"] = True, None, now()
                self.save()
                break
            st["next"] = msg
            self.save()
        self.finalize()

    def finalize(self):
        """Compiles the final /work/program.py exactly as the evaluation does -> runs/<id>/final/."""
        import shutil
        fin = os.path.join(self.dir, "final")
        if os.path.isdir(fin):
            shutil.rmtree(fin)
        os.makedirs(fin)
        passes.snapshot_sources(self.work, os.path.join(fin, "src"))
        res = sandbox.compile_in_sandbox(self.work, fin)
        if res.get("ok") and res.get("seconds_per_1000_positions", 0) > 60:
            res["ok"] = False
            res["error"] = f"too slow: {res['seconds_per_1000_positions']} s per 1,000 positions (limit 60)"
            json.dump(res, open(os.path.join(fin, "compile.json"), "w"), indent=1)
        self.log(f"final compile: {json.dumps({k: v for k, v in res.items() if k != 'error'})}"
                 + (f" ERROR {res.get('error', '')[-500:]}" if not res.get("ok") else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="xhigh")
    ap.add_argument("--max-turns", type=int, default=400)
    ap.add_argument("--turn-timeout", type=int, default=3 * 3600)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--finalize-only", action="store_true")
    args = ap.parse_args()
    r = Run(args)
    if args.finalize_only:
        r.finalize()
    else:
        r.loop()


if __name__ == "__main__":
    main()
