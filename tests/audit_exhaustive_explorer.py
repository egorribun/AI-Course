"""
Exhaustive Explorer Code, DOM & Test Suite Diagnostic Script.
Analyzes all 28 lectures + index.html in detail and outputs complete forensic data.
"""

from __future__ import annotations

import ast
import glob
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_PATH = COURSE_ROOT / "index.html"

from common import (
    EXPECTED_LECTURES,
    extract_code_blocks,
    extract_math_blocks,
    parse_lecture_structure,
    read_file,
    validate_latex_syntax,
)

def run_exhaustive_audit():
    results = {
        "lectures": {},
        "summary": {},
        "index_page": {},
    }

    total_qa = 0
    total_tasks = 0
    total_sols = 0
    total_snippets = 0
    total_python_snippets = 0
    total_clean_ast = 0
    total_syntax_errors = 0
    total_nav_errors = 0
    total_pill_mismatches = 0
    total_missing_cheats = 0
    broken_links = []

    # 1. Audit index.html
    if INDEX_PATH.is_file():
        index_content = read_file(INDEX_PATH)
        idx_struct = parse_lecture_structure(index_content)
        results["index_page"] = {
            "title": re.search(r"<title>(.*?)</title>", index_content).group(1) if re.search(r"<title>(.*?)</title>", index_content) else "",
            "all_hrefs_count": len(idx_struct.all_hrefs),
            "element_ids_count": len(idx_struct.element_ids),
        }

    # 2. Audit each lecture
    for idx, lec_filename in enumerate(EXPECTED_LECTURES):
        lec_path = LECTURES_DIR / lec_filename
        if not lec_path.is_file():
            results["lectures"][lec_filename] = {"error": "File not found"}
            continue

        content = read_file(lec_path)
        struct = parse_lecture_structure(content)
        code_blocks = extract_code_blocks(content, filename=lec_filename)

        # Title
        title_m = re.search(r"<title>(.*?)</title>", content)
        title = title_m.group(1) if title_m else ""
        h1_m = re.search(r"<h1>(.*?)</h1>", content)
        h1 = h1_m.group(1) if h1_m else ""

        # Pills extraction
        pills_raw = re.findall(r'<span class=["\']pill["\'][^>]*>(.*?)</span>', content)
        qa_pill_m = re.search(r'(\d+)\s+вопрос', content)
        task_pill_m = re.search(r'(\d+)\s+микро-задач', content)
        dur_pill_m = re.search(r'(\d+)\s+мин', content)

        qa_pill_val = int(qa_pill_m.group(1)) if qa_pill_m else None
        task_pill_val = int(task_pill_m.group(1)) if task_pill_m else None
        dur_pill_val = int(dur_pill_m.group(1)) if dur_pill_m else None

        # DOM counts
        qa_count = struct.qa_count
        task_count = struct.task_count
        sol_count = struct.sol_count
        has_cheat = struct.has_cheat
        cheat_len = len(struct.cheat_text.strip())

        total_qa += qa_count
        total_tasks += task_count
        total_sols += sol_count

        # Pill check
        pill_sync = True
        pill_sync_notes = []
        if qa_pill_val is None:
            pill_sync = False
            pill_sync_notes.append("Missing QA pill badge")
            total_pill_mismatches += 1
        elif qa_pill_val != qa_count:
            pill_sync = False
            pill_sync_notes.append(f"QA pill {qa_pill_val} != actual QA {qa_count}")
            total_pill_mismatches += 1

        if task_pill_val is None:
            pill_sync = False
            pill_sync_notes.append("Missing Task pill badge")
            total_pill_mismatches += 1
        elif task_pill_val != task_count:
            pill_sync = False
            pill_sync_notes.append(f"Task pill {task_pill_val} != actual Task {task_count}")
            total_pill_mismatches += 1

        if not has_cheat or cheat_len < 50:
            total_missing_cheats += 1

        # Navigation checks
        backlink = struct.backlinks[0] if struct.backlinks else None
        backlink_ok = bool(backlink and ("index.html" in backlink or backlink == "../"))

        nav_links = struct.navrow_links
        nav_hrefs = [h for h, _ in nav_links]
        nav_ok = True
        nav_notes = []

        if idx == 0:
            next_expected = EXPECTED_LECTURES[1]
            if not any(next_expected in h for h in nav_hrefs):
                nav_ok = False
                nav_notes.append(f"Expected next '{next_expected}' not in {nav_hrefs}")
                total_nav_errors += 1
        elif idx == len(EXPECTED_LECTURES) - 1:
            prev_expected = EXPECTED_LECTURES[idx - 1]
            if not any(prev_expected in h for h in nav_hrefs):
                nav_ok = False
                nav_notes.append(f"Expected prev '{prev_expected}' not in {nav_hrefs}")
                total_nav_errors += 1
        else:
            prev_expected = EXPECTED_LECTURES[idx - 1]
            next_expected = EXPECTED_LECTURES[idx + 1]
            if not any(prev_expected in h for h in nav_hrefs):
                nav_ok = False
                nav_notes.append(f"Expected prev '{prev_expected}' missing")
                total_nav_errors += 1
            if not any(next_expected in h for h in nav_hrefs):
                nav_ok = False
                nav_notes.append(f"Expected next '{next_expected}' missing")
                total_nav_errors += 1

        # Code snippets inspection
        lec_snippets = []
        for b in code_blocks:
            total_snippets += 1
            snippet_info = {
                "line": b.line_number,
                "is_python": b.is_python,
                "length_lines": len(b.clean_code.splitlines()),
                "syntax_valid": None,
                "syntax_error": None,
                "preview": b.clean_code[:100].replace("\n", " "),
            }
            if b.is_python:
                total_python_snippets += 1
                try:
                    ast.parse(b.clean_code)
                    snippet_info["syntax_valid"] = True
                    total_clean_ast += 1
                except SyntaxError as e:
                    snippet_info["syntax_valid"] = False
                    snippet_info["syntax_error"] = f"{e.msg} at line {e.lineno}"
                    total_syntax_errors += 1

            lec_snippets.append(snippet_info)

        results["lectures"][lec_filename] = {
            "index": idx,
            "title": title,
            "h1": h1,
            "qa_count": qa_count,
            "task_count": task_count,
            "sol_count": sol_count,
            "qa_pill_val": qa_pill_val,
            "task_pill_val": task_pill_val,
            "duration_min": dur_pill_val,
            "pills_count": len(pills_raw),
            "has_cheat": has_cheat,
            "cheat_len": cheat_len,
            "backlink": backlink,
            "backlink_ok": backlink_ok,
            "nav_links": nav_links,
            "nav_ok": nav_ok,
            "nav_notes": nav_notes,
            "pill_sync": pill_sync,
            "pill_sync_notes": pill_sync_notes,
            "total_snippets": len(code_blocks),
            "python_snippets": sum(1 for b in code_blocks if b.is_python),
            "snippets": lec_snippets,
        }

    results["summary"] = {
        "total_lectures": len(EXPECTED_LECTURES),
        "total_qa": total_qa,
        "avg_qa": round(total_qa / len(EXPECTED_LECTURES), 2),
        "min_qa": min(res["qa_count"] for res in results["lectures"].values()),
        "max_qa": max(res["qa_count"] for res in results["lectures"].values()),
        "total_tasks": total_tasks,
        "avg_tasks": round(total_tasks / len(EXPECTED_LECTURES), 2),
        "min_tasks": min(res["task_count"] for res in results["lectures"].values()),
        "max_tasks": max(res["task_count"] for res in results["lectures"].values()),
        "total_sols": total_sols,
        "total_snippets": total_snippets,
        "total_python_snippets": total_python_snippets,
        "total_clean_ast": total_clean_ast,
        "total_syntax_errors": total_syntax_errors,
        "total_pill_mismatches": total_pill_mismatches,
        "total_missing_cheats": total_missing_cheats,
        "total_nav_errors": total_nav_errors,
    }

    out_path = COURSE_ROOT / ".agents" / "explorer_code_1" / "audit_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("AUDIT COMPLETE! Saved data to", out_path)
    print("Summary:", json.dumps(results["summary"], indent=2))

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    run_exhaustive_audit()
