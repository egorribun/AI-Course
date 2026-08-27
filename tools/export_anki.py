"""
Anki Exporter for Deep Learning Exam Course (GUU 2026).
Extracts all 280+ Q&A defense questions, 170+ micro-tasks, and 28 3-minute cheatsheets
from lectures/*.html and exports them to TSV decks and a structured JS dataset.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
ANKI_DIR = COURSE_ROOT / "anki_decks"
JS_DIR = COURSE_ROOT / "js"

TICKET_MAPPING = {
    "00": "Разгон (Основы ML)",
    "01": "Билет 1: Полносвязные сети, Активации, Backprop",
    "02": "Билет 2: Автодифференцирование, PINN",
    "03": "Билет 3: Loss-функции, MLE, MAP / L2",
    "04": "Билет 4: Слои свёрточных сетей",
    "05": "Билет 5: Архитектуры CNN, Transfer Learning",
    "06": "Билет 6: Оптимизаторы: SGD, Momentum, Adam, Матричные производные",
    "07": "Билет 7: Аугментация, Тюнинг гиперпараметров",
    "08": "Билет 8: Метрические методы, Сиамские сети",
    "09": "Билет 9: Контрастивное обучение, SSL, InfoNCE",
    "10": "Билет 10: Автоэнкодеры: VAE, ELBO, CVAE",
    "11": "Билет 11: Генеративные модели: GAN",
    "12": "Билет 12 (ч.1): Диффузионные модели",
    "13": "Билет 12 (ч.2): Задачи Computer Vision",
    "14": "Билет 13: Рекуррентные сети, LSTM, biLSTM",
    "15": "Билет 14: Механизм внимания в seq2seq",
    "16": "Билет 15: Архитектура Transformer",
    "17": "Билет 16: Внимание и самовнимание (Q, K, V, маски)",
    "18": "Билет 17: LSTM vs Трансформер",
    "19": "Билет 18: Тексты, токенизация, Word2Vec",
    "20": "Билет 19: Машинный перевод, BLEU",
    "21": "Билет 20: Архитектуры Энкодер, Декодер, Энкодер-Декодер",
    "22": "Билет 21: RL: Строение агента, MDP",
    "23": "Билет 22 (ч.1): Уравнение Беллмана",
    "24": "Билет 22 (ч.2): Value/Policy Iteration, Монте-Карло",
    "25": "Билет 23: TD-обучение, SARSA, Q-learning",
    "26": "Билет 24: Policy Gradient, REINFORCE",
    "27": "Билет 25: Value-based vs Policy-based, Actor-Critic",
}


def clean_html_for_anki(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\t", " ").replace("\r", "")
    return text


def clean_text_plain(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_lecture_data(html_path: Path) -> dict:
    lec_id = html_path.name.split("-")[0]
    content = html_path.read_text(encoding="utf-8")

    title_match = re.search(r"<h1>(.*?)</h1>", content, re.DOTALL)
    title = clean_text_plain(title_match.group(1)) if title_match else html_path.stem

    # Q&As
    qas = []
    qa_pattern = re.compile(r"""<details\s+class=["']qa["'][^>]*>\s*<summary>(.*?)</summary>\s*<div\s+class=["']ans["']>(.*?)</div>\s*</details>""", re.DOTALL)
    for q_raw, a_raw in qa_pattern.findall(content):
        q_clean = re.sub(r"""<span\s+class=["']item-check["'].*?</span>""", "", q_raw, flags=re.DOTALL)
        qas.append({
            "question": clean_html_for_anki(q_clean),
            "answer": clean_html_for_anki(a_raw)
        })

    # Robust Task Extraction
    tasks = []
    task_split_pattern = re.compile(r"""<div\s+class=["']task["'][^>]*>""")
    chunks = task_split_pattern.split(content)[1:]
    for c in chunks:
        end_match = re.search(r"""(<div\s+class=["']task["']|<h2\b|<div\s+class=["']navrow["']|<div\s+class=["']cheat["'])""", c)
        task_body = c[:end_match.start()] if end_match else c

        tt = re.search(r"""<div\s+class=["']tt["']>(.*?)</div>""", task_body, re.DOTALL)
        sol = re.search(r"""<div\s+class=["']sol["']>(.*?)</div>""", task_body, re.DOTALL)

        title_task = clean_text_plain(tt.group(1)) if tt else "Задача"
        solution = clean_html_for_anki(sol.group(1)) if sol else ""

        det_pos = task_body.find("<details")
        prob_part = task_body[:det_pos] if det_pos != -1 else task_body
        prob_part = re.sub(r"""<div\s+class=["']tt["'].*?</div>""", "", prob_part, flags=re.DOTALL)
        prob_part = re.sub(r"""<span\s+class=["']item-check["'].*?</span>""", "", prob_part, flags=re.DOTALL)
        problem = clean_html_for_anki(prob_part)

        tasks.append({
            "title": title_task,
            "problem": problem,
            "solution": solution
        })

    # Cheat sheet
    cheat_match = re.search(
        r"""<div\s+class=["']cheat["'][^>]*>\s*<div\s+class=["']bt["']>(.*?)</div>\s*<ol>(.*?)</ol>\s*</div>""",
        content,
        re.DOTALL,
    )
    cheat_items = []
    if cheat_match:
        items = re.findall(r"<li>(.*?)</li>", cheat_match.group(2), re.DOTALL)
        cheat_items = [clean_html_for_anki(it) for it in items]

    return {
        "id": lec_id,
        "filename": html_path.name,
        "title": title,
        "ticket": TICKET_MAPPING.get(lec_id, f"Лекция {lec_id}"),
        "qas": qas,
        "tasks": tasks,
        "cheat_items": cheat_items
    }


def main():
    ANKI_DIR.mkdir(parents=True, exist_ok=True)
    JS_DIR.mkdir(parents=True, exist_ok=True)

    all_lectures_data = []
    lecture_files = sorted(LECTURES_DIR.glob("*.html"))

    total_qas = 0
    total_tasks = 0

    for lf in lecture_files:
        data = extract_lecture_data(lf)
        all_lectures_data.append(data)
        total_qas += len(data["qas"])
        total_tasks += len(data["tasks"])

    print(f"Parsed {len(all_lectures_data)} lectures. Total Q&A: {total_qas}, Total Tasks: {total_tasks}")

    # 1. Export TSV: Q&As
    qa_tsv_lines = ["Front (Question)\tBack (Answer)\tLecture\tExam Ticket"]
    for l in all_lectures_data:
        for idx, qa in enumerate(l["qas"], 1):
            q_clean = qa["question"].replace("\t", " ")
            a_clean = qa["answer"].replace("\t", " ")
            tag_lec = f"Лекция_{l['id']}"
            tag_ticket = l["ticket"].replace(" ", "_").replace(":", "").replace(",", "")
            qa_tsv_lines.append(f"{q_clean}\t{a_clean}\t{tag_lec}\t{tag_ticket}")

    (ANKI_DIR / "ai_course_exam_qas.tsv").write_text("\n".join(qa_tsv_lines) + "\n", encoding="utf-8")
    print(f"Generated {ANKI_DIR / 'ai_course_exam_qas.tsv'} ({len(qa_tsv_lines)-1} cards)")

    # 2. Export TSV: Micro-tasks
    task_tsv_lines = ["Task Statement & Title\tStep-by-Step Solution\tLecture\tExam Ticket"]
    for l in all_lectures_data:
        for t in l["tasks"]:
            front = f"<b>{t['title']}</b><br>{t['problem']}".replace("\t", " ")
            back = t["solution"].replace("\t", " ")
            tag_lec = f"Лекция_{l['id']}"
            tag_ticket = l["ticket"].replace(" ", "_").replace(":", "").replace(",", "")
            task_tsv_lines.append(f"{front}\t{back}\t{tag_lec}\t{tag_ticket}")

    (ANKI_DIR / "ai_course_microtasks.tsv").write_text("\n".join(task_tsv_lines) + "\n", encoding="utf-8")
    print(f"Generated {ANKI_DIR / 'ai_course_microtasks.tsv'} ({len(task_tsv_lines)-1} cards)")

    # 3. Export TSV: 3-min cheatsheets
    cheat_tsv_lines = ["Exam Ticket / Topic\t3-Minute Defense Skeleton & Key Points\tLecture"]
    for l in all_lectures_data:
        if l["cheat_items"]:
            front = f"<b>{l['ticket']}</b><br>{l['title']}".replace("\t", " ")
            back = "<ol>" + "".join(f"<li>{it}</li>" for it in l["cheat_items"]) + "</ol>"
            tag_lec = f"Лекция_{l['id']}"
            cheat_tsv_lines.append(f"{front}\t{back}\t{tag_lec}")

    (ANKI_DIR / "ai_course_3min_cheatsheets.tsv").write_text("\n".join(cheat_tsv_lines) + "\n", encoding="utf-8")
    print(f"Generated {ANKI_DIR / 'ai_course_3min_cheatsheets.tsv'} ({len(cheat_tsv_lines)-1} cards)")

    # 4. Generate js/exam_data.js for client-side instant simulator
    js_content = f"/** Pre-compiled dataset for DL Exam Course Simulator **/\nwindow.EXAM_DATA = {json.dumps(all_lectures_data, ensure_ascii=False, indent=2)};\n"
    (JS_DIR / "exam_data.js").write_text(js_content, encoding="utf-8")
    print(f"Generated {JS_DIR / 'exam_data.js'}")


if __name__ == "__main__":
    main()
