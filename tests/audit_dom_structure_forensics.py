"""
Forensic DOM structure verification across all 28 lectures + index.html.
Produces detailed table and validation flags for every single requirement.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_PATH = COURSE_ROOT / "index.html"

from common import EXPECTED_LECTURES, parse_lecture_structure, read_file

def audit_dom_forensics():
    matrix = []

    for idx, lec in enumerate(EXPECTED_LECTURES):
        filepath = LECTURES_DIR / lec
        content = read_file(filepath)
        struct = parse_lecture_structure(content)

        # Title & H1
        title_match = re.search(r"<title>(.*?)</title>", content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        h1_match = re.search(r"<h1>(.*?)</h1>", content, re.DOTALL)
        h1 = h1_match.group(1).strip() if h1_match else ""

        # Pills
        pills = re.findall(r'<span\s+class=["\']pill["\'][^>]*>(.*?)</span>', content, re.DOTALL)
        pills_clean = [re.sub(r"<[^>]+>", "", p).strip() for p in pills]

        qa_pill_m = re.search(r'(\d+)\s+вопрос', content)
        task_pill_m = re.search(r'(\d+)\s+микро-задач', content)
        dur_pill_m = re.search(r'(\d+)\s+мин', content)

        qa_pill = int(qa_pill_m.group(1)) if qa_pill_m else None
        task_pill = int(task_pill_m.group(1)) if task_pill_m else None
        dur_pill = int(dur_pill_m.group(1)) if dur_pill_m else None

        # QA Blocks
        qa_matches = re.findall(r'<details\s+class=["\']qa["\'][^>]*>(.*?)</details>', content, re.DOTALL)
        qa_count = struct.qa_count
        empty_qa_summaries = 0
        empty_qa_bodies = 0
        for q in qa_matches:
            s_match = re.search(r"<summary>(.*?)</summary>", q, re.DOTALL)
            if not s_match or not s_match.group(1).strip():
                empty_qa_summaries += 1
            body = re.sub(r"<summary>.*?</summary>", "", q, flags=re.DOTALL)
            if not body.strip():
                empty_qa_bodies += 1

        # Task Blocks
        task_count = struct.task_count
        sol_count = struct.sol_count

        # Cheat Sheet
        has_cheat = struct.has_cheat
        cheat_len = len(struct.cheat_text.strip())

        # Top Backlink
        backlink = struct.backlinks[0] if struct.backlinks else None
        backlink_ok = bool(backlink and ("index.html" in backlink or backlink == "../"))

        # Bottom Navrow
        nav_links = [{"href": href, "text": txt} for href, txt in struct.navrow_links]
        nav_hrefs = [h for h, _ in struct.navrow_links]

        # Nav validation
        nav_ok = True
        nav_error_detail = []
        if idx == 0:
            next_target = EXPECTED_LECTURES[1]
            if not any(next_target in h for h in nav_hrefs):
                nav_ok = False
                nav_error_detail.append(f"L00 missing next link to {next_target}")
        elif idx == len(EXPECTED_LECTURES) - 1:
            prev_target = EXPECTED_LECTURES[idx - 1]
            if not any(prev_target in h for h in nav_hrefs):
                nav_ok = False
                nav_error_detail.append(f"L27 missing prev link to {prev_target}")
        else:
            prev_target = EXPECTED_LECTURES[idx - 1]
            next_target = EXPECTED_LECTURES[idx + 1]
            if not any(prev_target in h for h in nav_hrefs):
                nav_ok = False
                nav_error_detail.append(f"Missing prev link to {prev_target}")
            if not any(next_target in h for h in nav_hrefs):
                nav_ok = False
                nav_error_detail.append(f"Missing next link to {next_target}")

        row = {
            "index": idx,
            "filename": lec,
            "title": title,
            "h1": h1,
            "qa_count": qa_count,
            "qa_pill": qa_pill,
            "qa_sync": qa_count == qa_pill,
            "qa_min_pass": qa_count >= 10,
            "empty_qa_summaries": empty_qa_summaries,
            "empty_qa_bodies": empty_qa_bodies,
            "task_count": task_count,
            "task_pill": task_pill,
            "task_sync": task_count == task_pill,
            "task_min_pass": task_count >= 6,
            "sol_count": sol_count,
            "sol_match": sol_count >= task_count,
            "dur_pill": dur_pill,
            "pills_total": len(pills_clean),
            "pills_list": pills_clean,
            "has_cheat": has_cheat,
            "cheat_len": cheat_len,
            "cheat_pass": has_cheat and cheat_len >= 50,
            "backlink_href": backlink,
            "backlink_ok": backlink_ok,
            "nav_links": nav_links,
            "nav_ok": nav_ok,
            "nav_error_detail": nav_error_detail,
        }
        matrix.append(row)

    out_matrix = COURSE_ROOT / ".agents" / "explorer_code_1" / "dom_forensics_matrix.json"
    with open(out_matrix, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)

    print(f"DOM Forensics Matrix created with {len(matrix)} lectures. Saved to {out_matrix}")

    # Print summary table
    print(f"{'#':<3} | {'Lecture':<25} | {'QA':<4} | {'Q-Pill':<6} | {'Tasks':<5} | {'T-Pill':<6} | {'Sol':<4} | {'Dur':<4} | {'Cheat':<5} | {'Backlink':<8} | {'NavSeq':<6}")
    print("-" * 95)
    for r in matrix:
        print(f"{r['index']:<3} | {r['filename']:<25} | {r['qa_count']:<4} | {str(r['qa_pill']):<6} | {r['task_count']:<5} | {str(r['task_pill']):<6} | {r['sol_count']:<4} | {str(r['dur_pill']) + 'm':<4} | {'PASS' if r['cheat_pass'] else 'FAIL':<5} | {'PASS' if r['backlink_ok'] else 'FAIL':<8} | {'PASS' if r['nav_ok'] else 'FAIL':<6}")

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    audit_dom_forensics()
