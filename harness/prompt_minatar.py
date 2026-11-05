"""Experiment 5 (one-shot MinAtar) prompt for a RASP program compiled by Tracr.

Kept from the paper's prompt (exp5_write_from_scratch/runs/<game>/message.txt): THE GAME paragraph, the game's exact
MinAtar 1.0.15 source (inserted here from the installed package, which is byte-identical), the channel
descriptions, how the 6 channels are built, and the scoring. Rewritten for RASP/Tracr: the task paragraph, THE
INPUT/OUTPUT encoding, THE NETWORK and how to write the answer. Added, as the analog of giving the game's source:
THE COMPILER, every non-test source file of the installed Tracr.
"""
import importlib
import inspect
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PARTS = json.load(open(os.path.join(HERE, "minatar_prompt_parts.json")))
TRACR_COMMIT = "9ce2b8c82b6ba10e62e86cf6f390e7536d4fd2cd"

TASK = (
    "YOUR TASK: write, from scratch, a RASP program that Tracr compiles into a policy network that plays this game as "
    "well as possible. The network's weights are exactly what Tracr produces from your program; you do not set them "
    "yourself. There is no training: no data, no loss, no gradients, no fine-tuning; you choose every part of the "
    "program yourself. You have no tools: no code execution, no compiler, no calculator, nothing to run. This is a "
    "single response and you will get no feedback. First describe your design briefly (the strategy, and what the "
    "program computes), then write the program.")

INPUT = (
    "THE INPUT (106 tokens after \"BOS\"): the compiled network reads 107 tokens: \"BOS\", then the 100 cells of the "
    "10 x 10 grid (rows 0 top to 9 bottom, columns 0 left to 9 right) in the order row * 10 + column, then 6 action "
    "tokens. In your program, rasp.indices of the cell at row r, column c is r * 10 + c, and the action tokens are at "
    "indices 100..105. A cell's token is an integer 0..63 whose bit ch (value 2 ** ch) is 1 when the cell is 1 in "
    "channel ch of the 6 channels below; for example token 0 is an empty cell and token 9 (= 1 + 8) is a cell that is "
    "1 in channels 0 and 3. The token at index 100 + a is always 64 + a (a = 0..5). In this game:\n")

OUTPUT = (
    "THE OUTPUT: program() must return a numerical SOp (rasp.numerical); its values at indices 100..105 in the "
    "compiled network are the logits of the actions 0 no-op, 1 left, 2 up, 3 right, 4 down, 5 fire (its values at "
    "the other indices are not used); the action is sampled from the softmax of the logits. With probability 0.1 the "
    "game repeats the previous action instead (sticky actions).")

NETWORK = (
    "THE NETWORK: a transformer compiled by Tracr (THE COMPILER, below) from your RASP program:\n"
    "  compiling.compile_rasp_to_model(program(), vocab=set(range(70)), max_seq_len=106, compiler_bos=\"BOS\", "
    "mlp_exactness=MLP_EXACTNESS)\n"
    "(from tracr.compiler import compiling; causal = False), used exactly as Tracr produces it: you choose the "
    "program, not the weights. It is run with Tracr's own forward pass (tracr/transformer/model.py): x = token "
    "embedding + position embedding (107 x D); then for each layer x = x + MultiHeadAttention(x), with attention "
    "weights softmax((x W_Q)(x W_K)^T / sqrt(key_size)) over all 107 positions, and x = x + relu(x W_1 + b_1) W_2 + "
    "b_2; no layer norm. The logit of action a is x[101 + a, d], where d is the residual dimension of your output SOp. "
    "Tracr's compilation is not guaranteed to be exact, so the compiled network's outputs can differ from what "
    "rasp.evaluate gives for your program: what plays is the compiled network. Compiling must succeed within 900 "
    "seconds and 10 GB of memory; if your code raises an error, does not compile, or exceeds these limits, your "
    "network outputs all-zero logits (uniform random play).")

SCORED = (
    "HOW YOUR NETWORK IS SCORED: its mean score per episode over 1,000 episodes, each action sampled from the softmax "
    "of the logits (with the sticky actions above); an episode also stops after 10,000 steps. It is compared with "
    "policy networks trained by reinforcement learning on this game.")

HOW = (
    "HOW TO WRITE THE PROGRAM (nothing is run before scoring). Write a code block whose opening line is three "
    "backticks followed by the word python. It must define a function program() that builds and returns the output "
    "SOp, and it may set MLP_EXACTNESS (an integer, default 100). The block is executed once, with Python 3.11, "
    "tracr (THE COMPILER, below) and numpy, only to build and compile the program: it must not read or write files "
    "or evaluate the program on any input. Only the LAST python block of your reply is read.")


def tracr_source():
    import tracr
    root = os.path.dirname(tracr.__file__)
    files = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".py") or f.endswith("_test.py") or f in ("tests_common.py", "test_cases.py"):
                continue
            p = os.path.join(dp, f)
            text = open(p).read()
            if f == "__init__.py" and len(text.strip().splitlines()) <= 15:
                continue  # licence header only
            files.append((os.path.relpath(p, os.path.dirname(root)), text))
    files.sort()
    out = [f"THE COMPILER: Tracr, the exact version that compiles your program (github.com/google-deepmind/tracr, "
           f"commit {TRACR_COMMIT[:7]}); every source file except its tests ({len(files)} files)."]
    for path, text in files:
        out.append(f"### {path}\n```python\n{text.rstrip()}\n```")
    return "\n\n".join(out)


def game_source(game):
    return inspect.getsource(importlib.import_module(f"minatar.environments.{game}")).rstrip("\n")


def task_prompt(game):
    p = PARTS[game]
    return "\n\n".join([
        TASK,
        p["game_text"] + "\n\n```python\n" + game_source(game) + "\n```",
        INPUT + "\n".join(p["channel_lines"]) + "\n" + p["how_built"],
        OUTPUT, NETWORK, SCORED, HOW, tracr_source()])


if __name__ == "__main__":
    import sys
    print(task_prompt(sys.argv[1] if len(sys.argv) > 1 else "breakout"))
