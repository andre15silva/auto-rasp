#!/usr/bin/env bash
# Restarts live writer runs onto the current harness code, killing each driver only while it is NOT inside a
# model call (no `claude` child), so the turn in progress is resumed from state.json without loss.
cd "$(dirname "$0")/.."
for b in "$@"; do
  id="opus55_b$b"
  pid=$(pgrep -f "run_writer --budget $b --run-id $id$")
  if [ -z "$pid" ]; then echo "$id: not running"; continue; fi
  for i in $(seq 1 1800); do
    if ! pgrep -P "$pid" -f "claude -p" >/dev/null; then break; fi
    sleep 1
  done
  if pgrep -P "$pid" -f "claude -p" >/dev/null; then echo "$id: still in a model call, skipped"; continue; fi
  kill -TERM -- "-$(ps -o pgid= "$pid" | tr -d ' ')"
  sleep 3
  setsid nohup bash -c "source /opt/venvs/rasp/bin/activate && PYTHONWARNINGS=ignore python -m harness.run_writer --budget $b --run-id $id" >> "runs/driver_$id.log" 2>&1 < /dev/null &
  echo "$id: restarted (old pid $pid)"
done
