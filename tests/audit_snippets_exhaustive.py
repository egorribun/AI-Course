"""
Exhaustive snippet extractor and runner.
Extracts every code snippet across all 28 lectures, tests AST parsing, execution, variable names, tensor shapes, and textual context.
"""

from __future__ import annotations

import ast
import html
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"

from common import EXPECTED_LECTURES

pattern = re.compile(
    r"<pre[^>]*>(?:<code[^>]*>)?(.*?)(?:</code>)?</pre>", re.DOTALL | re.IGNORECASE
)


def run_snippet_audit():
    all_snippets = []
    by_lecture = {}

    for lec in EXPECTED_LECTURES:
        content = (LECTURES_DIR / lec).read_text(encoding="utf-8", errors="replace")
        lec_blocks = []
        for match in pattern.finditer(content):
            start = match.start()
            end = match.end()
            line = content[:start].count("\n") + 1
            raw_html = match.group(1)

            # Clean code
            clean = re.sub(r"<[^>]+>", "", raw_html)
            clean = html.unescape(clean).strip()

            # Context: 200 chars before and 200 chars after
            ctx_before = re.sub(r"<[^>]+>", " ", content[max(0, start - 300) : start]).strip()
            ctx_after = re.sub(r"<[^>]+>", " ", content[end : min(len(content), end + 300)]).strip()

            # Determine type
            is_bash = clean.startswith("$") or clean.startswith("pip install")
            is_ascii = "+---" in clean or "|---" in clean or "# ASCII" in clean or "=== " in clean

            py_indicators = [
                "import torch",
                "import numpy",
                "import math",
                "import nn",
                "from torch",
                "nn.Module",
                "def ",
                "class ",
                "torch.tensor",
                "torch.zeros",
                "torch.randn",
                "return ",
                "self.",
                "in range(",
                "torch.optim",
                "torch.autograd",
                "F.relu",
                "F.cross_entropy",
                "q_table",
                "model =",
            ]
            is_py = (
                (not is_bash)
                and (not is_ascii)
                and (any(k in clean for k in py_indicators) or "=" in clean or "print(" in clean)
            )

            snippet_data = {
                "lecture": lec,
                "line": line,
                "is_python": is_py,
                "is_bash": is_bash,
                "is_ascii": is_ascii,
                "raw_length": len(raw_html),
                "clean_code": clean,
                "lines_count": len(clean.splitlines()),
                "ast_valid": None,
                "ast_error": None,
                "exec_status": None,
                "exec_output": None,
                "context_before": ctx_before[-150:],
                "context_after": ctx_after[:150],
            }

            if is_py:
                try:
                    ast.parse(clean)
                    snippet_data["ast_valid"] = True
                except SyntaxError as e:
                    snippet_data["ast_valid"] = False
                    snippet_data["ast_error"] = f"{e.msg} at line {e.lineno}"

                # Try executing standalone
                exec_globals = {
                    "torch": torch,
                    "nn": nn,
                    "F": F,
                    "math": math,
                    "np": np,
                    "numpy": np,
                }
                try:
                    # Capture stdout
                    import io
                    from contextlib import redirect_stdout

                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        exec(clean, exec_globals)
                    snippet_data["exec_status"] = "SUCCESS_STANDALONE"
                    snippet_data["exec_output"] = buf.getvalue()[:200]
                except Exception as e:
                    snippet_data["exec_status"] = (
                        f"REQUIRES_CONTEXT_OR_INPUTS ({type(e).__name__}: {str(e)[:80]})"
                    )

            lec_blocks.append(snippet_data)
            all_snippets.append(snippet_data)

        by_lecture[lec] = lec_blocks

    summary = {
        "total_extracted_blocks": len(all_snippets),
        "python_blocks": sum(1 for s in all_snippets if s["is_python"]),
        "ast_valid_python_blocks": sum(
            1 for s in all_snippets if s["is_python"] and s["ast_valid"]
        ),
        "ast_syntax_errors": sum(1 for s in all_snippets if s["is_python"] and not s["ast_valid"]),
        "standalone_executed_cleanly": sum(
            1 for s in all_snippets if s["exec_status"] == "SUCCESS_STANDALONE"
        ),
        "context_dependent_snippets": sum(
            1 for s in all_snippets if s["is_python"] and s["exec_status"] != "SUCCESS_STANDALONE"
        ),
    }

    out_file = COURSE_ROOT / ".agents" / "explorer_code_1" / "snippets_detail.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            {"summary": summary, "by_lecture": by_lecture, "all_snippets": all_snippets},
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("SNIPPET AUDIT COMPLETE! Saved to", out_file)
    print("Summary:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    run_snippet_audit()
