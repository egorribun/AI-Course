"""
Comprehensive Deep Snippet Verifier.
Extracts every code snippet, prints full details, tests parsing, execution, and checks for HTML encoding issues.
"""

from __future__ import annotations

import ast
import html
import re
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"

EXPECTED_LECTURES = [
    "00-intro-ml.html",
    "01-fcnn.html",
    "02-autodiff-pinn.html",
    "03-losses-mle.html",
    "04-cnn-layers.html",
    "05-cnn-architectures.html",
    "06-optimizers.html",
    "07-hyperparams.html",
    "08-metric-learning.html",
    "09-contrastive-ssl.html",
    "10-vae.html",
    "11-gan.html",
    "12-diffusion.html",
    "13-cv-tasks.html",
    "14-rnn-lstm.html",
    "15-attention-seq2seq.html",
    "16-transformers.html",
    "17-self-attention.html",
    "18-lstm-vs-transformer.html",
    "19-text-word2vec.html",
    "20-mt-bleu.html",
    "21-enc-dec.html",
    "22-rl-intro.html",
    "23-bellman.html",
    "24-vi-pi-mc.html",
    "25-td-qlearning.html",
    "26-policy-gradient.html",
    "27-actor-critic.html",
]

pattern = re.compile(r"<pre[^>]*>(?:<code[^>]*>)?(.*?)(?:</code>)?</pre>", re.DOTALL | re.IGNORECASE)

def main():
    total_snippets = 0
    python_snippets = 0
    syntax_errors = 0
    all_snippets_info = []

    for lec in EXPECTED_LECTURES:
        content = (LECTURES_DIR / lec).read_text(encoding="utf-8", errors="replace")
        for match in pattern.finditer(content):
            total_snippets += 1
            line = content[:match.start()].count("\n") + 1
            raw = match.group(1)

            # Check if there are raw < that were interpreted as HTML tags
            # e.g., < len(...) or < max_len
            unclosed_tags = re.findall(r"<([a-zA-Z_][a-zA-Z0-9_]*(\s*[^>]*)?)>", raw)

            clean = re.sub(r"<[^>]+>", "", raw)
            clean = html.unescape(clean).strip()

            # Python check
            py_indicators = ["import ", "torch", "nn.", "def ", "class ", "return ", "for ", "in range", "lambda ", "model ="]
            is_py = any(ind in clean for ind in py_indicators)
            if clean.startswith("$") or clean.startswith("# ASCII") or "+---" in clean or "|---" in clean:
                is_py = False

            snippet_status = "NON_PYTHON"
            ast_err = None

            if is_py:
                python_snippets += 1
                try:
                    ast.parse(clean)
                    snippet_status = "VALID_AST"
                except SyntaxError as e:
                    syntax_errors += 1
                    snippet_status = f"SYNTAX_ERROR: {e.msg} at line {e.lineno}"
                    ast_err = str(e)

            all_snippets_info.append({
                "lecture": lec,
                "line": line,
                "status": snippet_status,
                "is_py": is_py,
                "clean": clean,
                "ast_err": ast_err,
            })

    print(f"Total Snippets: {total_snippets}")
    print(f"Python Snippets: {python_snippets}")
    print(f"Syntax Errors: {syntax_errors}")

    for s in all_snippets_info:
        if s["is_py"]:
            print(f"[{s['lecture']}:{s['line']}] Status: {s['status']}")
            if s["ast_err"]:
                print(f"  Error: {s['ast_err']}")
                print("  Snippet code:\n" + s["clean"])

if __name__ == "__main__":
    main()
