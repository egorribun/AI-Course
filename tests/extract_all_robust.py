"""
Extract all Q&As and Micro-Tasks with robust regex / tag matching and inspect them.
"""
import glob
import json
import re
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
lecture_files = sorted([f.name for f in LECTURES_DIR.glob("*.html") if re.match(r"^\d{2}-.*\.html$", f.name)])

def extract_all():
    total_qas = 0
    total_tasks = 0
    lectures_info = []

    for fname in lecture_files:
        content = (LECTURES_DIR / fname).read_text(encoding="utf-8")
        
        # QA blocks: <details class="...qa..."> ... </details>
        qa_pattern = re.compile(r'<details\s+class=["\'][^"\']*?\bqa\b[^"\']*?["\']>(.*?)</details>', re.DOTALL)
        qas = []
        for m in qa_pattern.finditer(content):
            qa_html = m.group(1)
            summary_m = re.search(r'<summary>(.*?)</summary>', qa_html, re.DOTALL)
            summary = summary_m.group(1).strip() if summary_m else ""
            body = qa_html[summary_m.end():].strip() if summary_m else qa_html.strip()
            clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
            clean_body = re.sub(r'<[^>]+>', '', body).strip()
            qas.append({
                "summary": clean_summary,
                "body": clean_body,
                "raw_html": m.group(0)
            })
            
        # Micro-task blocks: <div class="task"> ... </div>
        task_pattern = re.compile(r'<div\s+class=["\'][^"\']*?\btask\b[^"\']*?["\']>(.*?)(?=(?:<div\s+class=["\'][^"\']*?\btask\b|<section|</main>|\Z))', re.DOTALL)
        tasks = []
        for m in task_pattern.finditer(content):
            task_raw = m.group(1)
            # Sol block: details with class sol OR details containing <summary>Решение or <div class="sol">
            sol_m = re.search(r'<details(?:\s+class=["\'][^"\']*?\bsol\b[^"\']*?["\'])?[^>]*?>\s*<summary>\s*Решение.*?</details>', task_raw, re.DOTALL)
            if not sol_m:
                sol_m = re.search(r'<details\s+class=["\'][^"\']*?\bsol\b[^"\']*?["\']>(.*?)</details>', task_raw, re.DOTALL)
                
            if sol_m:
                sol_html = sol_m.group(0)
                sol_summary_m = re.search(r'<summary>(.*?)</summary>', sol_html, re.DOTALL)
                sol_summary = sol_summary_m.group(1).strip() if sol_summary_m else ""
                sol_body = sol_html[sol_summary_m.end():].replace('</details>', '').strip() if sol_summary_m else sol_html.strip()
                problem_html = task_raw[:sol_m.start()]
            else:
                sol_summary = ""
                sol_body = ""
                problem_html = task_raw
                
            clean_problem = re.sub(r'<[^>]+>', '', problem_html).strip()
            clean_sol = re.sub(r'<[^>]+>', '', sol_body).strip()
            
            tasks.append({
                "problem": clean_problem,
                "solution_summary": re.sub(r'<[^>]+>', '', sol_summary).strip(),
                "solution": clean_sol,
                "has_sol": sol_m is not None and len(clean_sol) > 0,
                "raw_html": m.group(0)
            })
            
        # Pills
        pill_matches = re.findall(r'<span\s+class=["\']pill["\']>(.*?)</span>', content)
        clean_pills = [re.sub(r'<[^>]+>', '', p).strip() for p in pill_matches]
        
        qa_pill = None
        task_pill = None
        for p in clean_pills:
            qm = re.search(r'(\d+)\s+(?:вопрос|QA|Q&A|вопросов)', p, re.I)
            if qm: qa_pill = int(qm.group(1))
            tm = re.search(r'(\d+)\s+(?:задач|микро-задач|задачи|tasks)', p, re.I)
            if tm: task_pill = int(tm.group(1))
            
        total_qas += len(qas)
        total_tasks += len(tasks)
        
        lectures_info.append({
            "filename": fname,
            "qa_count": len(qas),
            "qa_pill": qa_pill,
            "task_count": len(tasks),
            "task_pill": task_pill,
            "qas": qas,
            "tasks": tasks
        })

    print(f"TOTAL QA BLOCKS: {total_qas}")
    print(f"TOTAL MICRO-TASKS: {total_tasks}")
    
    with open(COURSE_ROOT / "tests" / "all_qas_tasks_dump.json", "w", encoding="utf-8") as f:
        json.dump(lectures_info, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    extract_all()
