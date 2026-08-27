"""
Inspect each snippet's full text, line number, and context.
"""
from pathlib import Path
import json

COURSE_ROOT = Path(__file__).resolve().parent.parent

def inspect_all():
    data_path = COURSE_ROOT / ".agents" / "explorer_code_1" / "snippets_detail.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, s in enumerate(data["all_snippets"]):
        print(f"=== SNIPPET #{i+1}: [{s['lecture']}:{s['line']}] ===")
        print(f"is_py: {s['is_python']}, is_bash: {s['is_bash']}, is_ascii: {s['is_ascii']}")
        print(f"AST valid: {s['ast_valid']}")
        print("CODE:")
        print(s["clean_code"])
        print("-" * 50)

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    inspect_all()
