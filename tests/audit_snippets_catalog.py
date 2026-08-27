"""
Analyze all 36 code snippets in depth and produce a comprehensive catalog.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent

def analyze_all_snippets():
    data_path = COURSE_ROOT / ".agents" / "explorer_code_1" / "snippets_detail.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = []

    for idx, s in enumerate(data["all_snippets"]):
        lec = s["lecture"]
        line = s["line"]
        clean = s["clean_code"]
        is_py = s["is_python"]
        is_bash = s["is_bash"]
        is_ascii = s["is_ascii"]

        entry = {
            "snippet_id": idx + 1,
            "lecture": lec,
            "line": line,
            "type": "Python" if is_py else ("Bash" if is_bash else "ASCII/Text"),
            "ast_valid": s["ast_valid"],
            "lines_count": s["lines_count"],
            "summary": "",
            "tensor_operations": [],
            "dependencies": [],
            "notes": "",
        }

        # Analyze code content
        if "torch" in clean:
            entry["dependencies"].append("torch")
        if "torch.nn" in clean or "nn." in clean:
            entry["dependencies"].append("torch.nn")
        if "torch.optim" in clean or "optim." in clean:
            entry["dependencies"].append("torch.optim")
        if "numpy" in clean or "np." in clean:
            entry["dependencies"].append("numpy")
        if "transformers" in clean:
            entry["dependencies"].append("transformers")
        if "gymnasium" in clean or "gym" in clean:
            entry["dependencies"].append("gymnasium")

        # Tensors
        tensor_ops = re.findall(r"torch\.[a-zA-Z0-9_]+|nn\.[a-zA-Z0-9_]+|F\.[a-zA-Z0-9_]+", clean)
        entry["tensor_operations"] = sorted(list(set(tensor_ops)))

        # Summary heuristics
        first_line = clean.splitlines()[0] if clean.splitlines() else ""
        entry["summary"] = first_line[:60]

        catalog.append(entry)

    out_catalog = COURSE_ROOT / ".agents" / "explorer_code_1" / "snippets_catalog.json"
    with open(out_catalog, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"Catalog created with {len(catalog)} items. Saved to {out_catalog}")

if __name__ == "__main__":
    analyze_all_snippets()
