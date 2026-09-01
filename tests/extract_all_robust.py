import json
import re
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
lecture_files = sorted([f.name for f in LECTURES_DIR.glob("*.html") if re.match(r"^\d{2}-.*\.html$", f.name)])

def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_all():
    total_qas = 0
    total_tasks = 0
    lectures_info = []

    for fname in lecture_files:
        content = (LECTURES_DIR / fname).read_text(encoding="utf-8")

        # QA blocks: <details class="qa"> <summary> ... </summary> <div class="ans"> ... </div> </details>
        qa_pattern = re.compile(r'<details\s+class=["\'][^"\']*?\bqa\b[^"\']*?["\']>(.*?)</details>', re.DOTALL)
        qas = []
        for m in qa_pattern.finditer(content):
            qa_html = m.group(1)
            summary_m = re.search(r'<summary>(.*?)</summary>', qa_html, re.DOTALL)
            summary = summary_m.group(1).strip() if summary_m else ""
            ans_m = re.search(r'<div\s+class=["\']ans["\']>(.*?)</div>', qa_html, re.DOTALL)
            ans = ans_m.group(1).strip() if ans_m else qa_html[summary_m.end():].strip() if summary_m else qa_html

            clean_summary = clean_html(summary)
            clean_ans = clean_html(ans)
            qas.append({
                "summary": clean_summary,
                "body": clean_ans,
                "raw_html": m.group(0)
            })

        # Micro-task blocks: <div class="task"> ... </div>
        task_chunks = re.split(r'<div\s+class=["\']task["\'][^>]*>', content)[1:]
        tasks = []
        for c in task_chunks:
            end_match = re.search(r'(<div\s+class=["\']task["\']|<h2\b|<div\s+class=["\']navrow["\']|<div\s+class=["\']cheat["\'])', c)
            task_body = c[:end_match.start()] if end_match else c

            tt_m = re.search(r'<div\s+class=["\']tt["\']>(.*?)</div>', task_body, re.DOTALL)
            sol_m = re.search(r'<div\s+class=["\']sol["\']>(.*?)</div>', task_body, re.DOTALL)

            det_pos = task_body.find("<details")
            prob_raw = task_body[:det_pos] if det_pos != -1 else task_body
            if tt_m:
                prob_raw = prob_raw.replace(tt_m.group(0), "")

            clean_problem = clean_html(prob_raw)
            clean_sol = clean_html(sol_m.group(1)) if sol_m else ""

            tasks.append({
                "problem": clean_problem,
                "solution_summary": clean_html(tt_m.group(1)) if tt_m else "Решение",
                "solution": clean_sol,
                "has_sol": len(clean_sol) > 0,
                "raw_html": task_body
            })

        # Pills
        pill_matches = re.findall(r'<span\s+class=["\']pill[^"\']*["\']>(.*?)</span>', content)
        clean_pills = [clean_html(p) for p in pill_matches]

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
