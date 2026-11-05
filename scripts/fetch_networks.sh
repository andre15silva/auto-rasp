#!/usr/bin/env bash
# Fetches the released Experiment-6 (Go) and Experiment-5 (MinAtar) networks of "Sparks of Weight-Space Programming" (CC BY 4.0,
# https://github.com/RikiyaT/lm_understand-logs) into networks/paper/. Pinned to the commit we used.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMIT=4d09ba6d6a7e891dd8063974dfe81b3d78e3494f
DEST="$ROOT/networks/paper"
TMP="$(mktemp -d)"
git clone --filter=blob:none --no-checkout https://github.com/RikiyaT/lm_understand-logs.git "$TMP/logs"
git -C "$TMP/logs" sparse-checkout set exp6_go_from_scratch/networks exp5_write_from_scratch/networks
git -C "$TMP/logs" checkout -q "$COMMIT"
mkdir -p "$DEST"
cp -r "$TMP/logs/exp6_go_from_scratch/networks/"* "$DEST/"
mkdir -p "$ROOT/networks/paper_minatar"
cp -r "$TMP/logs/exp5_write_from_scratch/networks/"* "$ROOT/networks/paper_minatar/"   # Experiment 5 (MinAtar)
rm -rf "$TMP"
ls "$DEST"
