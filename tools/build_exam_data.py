#!/usr/bin/env python3
"""
Exam Data Builder for Deep Learning Course (GUU 2026).

Parses all 28 lecture HTML files in lectures/ and compiles a unified,
validated JavaScript dataset (js/exam_data.js) for the interactive exam
simulator and SM-2 flashcard trainer.

Features:
- Pure standard library implementation (no third-party dependencies)
- Full extraction of Q&A defense questions, micro-tasks with solutions, and ticket outlines
- Modular 4-block mapping (Blocks A, B, C, D)
- CLI support: --output, --dry-run, --check, --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
DEFAULT_OUTPUT_PATH = COURSE_ROOT / "js" / "exam_data.js"

TICKET_MAPPING: dict[str, str] = {
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


def get_block_for_lecture(lec_id: str) -> str:
    """Return the course block identifier ('A', 'B', 'C', 'D') for a lecture ID."""
    try:
        num = int(lec_id)
    except ValueError:
        return "A"
    if 0 <= num <= 7:
        return "A"
    if 8 <= num <= 13:
        return "B"
    if 14 <= num <= 21:
        return "C"
    if 22 <= num <= 27:
        return "D"
    return "A"


def clean_html_text(text: str) -> str:
    """Normalize whitespace and strip stray carriage returns."""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("\t", " ").replace("\r", "")
    return text


def clean_text_plain(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_lecture_data(html_path: Path) -> dict[str, Any]:
    """Parse a single lecture HTML file and extract structured exam metadata."""
    lec_id = html_path.name.split("-")[0]
    content = html_path.read_text(encoding="utf-8")

    title_match = re.search(r"<h1>(.*?)</h1>", content, re.DOTALL)
    title = clean_text_plain(title_match.group(1)) if title_match else html_path.stem

    # Extract Q&As
    qas: list[dict[str, str]] = []
    qa_pattern = re.compile(
        r"""<details\s+class=["']qa["'][^>]*>\s*<summary>(.*?)</summary>\s*<div\s+class=["']ans["']>(.*?)</div>\s*</details>""",
        re.DOTALL,
    )
    for q_raw, a_raw in qa_pattern.findall(content):
        q_clean = re.sub(
            r"""<span\s+class=["']item-check["'].*?</span>""",
            "",
            q_raw,
            flags=re.DOTALL,
        )
        qas.append({
            "question": clean_html_text(q_clean),
            "answer": clean_html_text(a_raw),
        })

    # Extract Micro-tasks
    tasks: list[dict[str, str]] = []
    task_split_pattern = re.compile(r"""<div\s+class=["']task["'][^>]*>""")
    chunks = task_split_pattern.split(content)[1:]
    for c in chunks:
        end_match = re.search(
            r"""(<div\s+class=["']task["']|<h2\b|<div\s+class=["']navrow["']|<div\s+class=["']cheat["'])""",
            c,
        )
        task_body = c[: end_match.start()] if end_match else c

        tt = re.search(r"""<div\s+class=["']tt["']>(.*?)</div>""", task_body, re.DOTALL)
        sol = re.search(r"""<div\s+class=["']sol["']>(.*?)</div>""", task_body, re.DOTALL)

        title_task = clean_text_plain(tt.group(1)) if tt else "Задача"
        solution = clean_html_text(sol.group(1)) if sol else ""

        det_pos = task_body.find("<details")
        prob_part = task_body[:det_pos] if det_pos != -1 else task_body
        prob_part = re.sub(r"""<div\s+class=["']tt["'].*?</div>""", "", prob_part, flags=re.DOTALL)
        prob_part = re.sub(r"""<span\s+class=["']item-check["'].*?</span>""", "", prob_part, flags=re.DOTALL)
        problem = clean_html_text(prob_part)

        tasks.append({
            "title": title_task,
            "problem": problem,
            "solution": solution,
        })

    # Extract Cheat outline
    cheat_match = re.search(
        r"""<div\s+class=["']cheat["'][^>]*>\s*<div\s+class=["']bt["']>(.*?)</div>\s*<ol>(.*?)</ol>\s*</div>""",
        content,
        re.DOTALL,
    )
    cheat_items: list[str] = []
    if cheat_match:
        items = re.findall(r"<li>(.*?)</li>", cheat_match.group(2), re.DOTALL)
        cheat_items = [clean_html_text(it) for it in items]

    return {
        "id": lec_id,
        "filename": html_path.name,
        "title": title,
        "ticket": TICKET_MAPPING.get(lec_id, f"Лекция {lec_id}"),
        "module": get_block_for_lecture(lec_id),
        "qas": qas,
        "tasks": tasks,
        "cheat_items": cheat_items,
    }


def compile_exam_dataset(lectures_dir: Path) -> list[dict[str, Any]]:
    """Parse all lecture HTML files in directory and return sorted dataset."""
    html_files = sorted(lectures_dir.glob("*.html"))
    if not html_files:
        raise FileNotFoundError(f"No lecture HTML files found in {lectures_dir}")

    dataset: list[dict[str, Any]] = []
    for lf in html_files:
        data = extract_lecture_data(lf)
        dataset.append(data)
    return dataset


def build_js_content(dataset: list[dict[str, Any]]) -> str:
    """Serialize the dataset into formatted JavaScript string."""
    # Build aggregate structures
    questions: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    tickets_map: dict[str, dict[str, Any]] = {}

    for lec in dataset:
        lec_id = lec["id"]
        ticket_name = lec["ticket"]
        module = lec["module"]

        if ticket_name not in tickets_map:
            tickets_map[ticket_name] = {
                "ticket": ticket_name,
                "module": module,
                "lectures": [],
                "qas_count": 0,
                "tasks_count": 0,
            }
        tickets_map[ticket_name]["lectures"].append(lec_id)
        tickets_map[ticket_name]["qas_count"] += len(lec["qas"])
        tickets_map[ticket_name]["tasks_count"] += len(lec["tasks"])

        for q_idx, qa in enumerate(lec["qas"]):
            questions.append({
                "id": f"l{lec_id}_qa{q_idx}",
                "lecture_id": lec_id,
                "ticket": ticket_name,
                "module": module,
                "question": qa["question"],
                "answer": qa["answer"],
            })

        for t_idx, t in enumerate(lec["tasks"]):
            tasks.append({
                "id": f"l{lec_id}_t{t_idx}",
                "lecture_id": lec_id,
                "ticket": ticket_name,
                "module": module,
                "title": t["title"],
                "problem": t["problem"],
                "solution": t["solution"],
            })

    json_lectures = json.dumps(dataset, ensure_ascii=False, indent=2)

    js_code = (
        "/**\n"
        " * Pre-compiled dataset for DL Exam Course Simulator & SM-2 Engine (GUU 2026).\n"
        " * Generated automatically by tools/build_exam_data.py — DO NOT EDIT MANUALLY.\n"
        " */\n"
        f"window.EXAM_DATA = {json_lectures};\n"
    )
    return js_code


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for exam data builder."""
    parser = argparse.ArgumentParser(
        description="Compile lecture content into js/exam_data.js dataset for web simulator.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Target path for generated JS file (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--lectures-dir",
        "-l",
        type=Path,
        default=LECTURES_DIR,
        help=f"Directory containing lecture HTML files (default: {LECTURES_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse lectures and validate without writing to disk.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if output file matches current lectures (exit 0 if fresh, exit 1 if diff).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose compilation details.",
    )

    args = parser.parse_args(argv)

    try:
        dataset = compile_exam_dataset(args.lectures_dir)
    except Exception as e:
        sys.stderr.write(f"Error parsing lectures: {e}\n")
        return 1

    total_qas = sum(len(l["qas"]) for l in dataset)
    total_tasks = sum(len(l["tasks"]) for l in dataset)
    total_cheats = sum(len(l["cheat_items"]) for l in dataset)

    if args.verbose:
        print(f"Loaded {len(dataset)} lectures from {args.lectures_dir}")
        for l in dataset:
            print(
                f"  [{l['id']}] Block {l['module']}: {l['title']} | "
                f"Q&As: {len(l['qas'])}, Tasks: {len(l['tasks'])}, Cheats: {len(l['cheat_items'])}"
            )
        print(f"Total metrics: {len(dataset)} lectures, {total_qas} Q&As, {total_tasks} tasks, {total_cheats} cheats")

    js_content = build_js_content(dataset)

    if args.check:
        if not args.output.exists():
            sys.stderr.write(f"Check failed: {args.output} does not exist.\n")
            return 1
        current_content = args.output.read_text(encoding="utf-8")
        if current_content != js_content:
            sys.stderr.write(f"Check failed: {args.output} is outdated. Run build_exam_data.py to update.\n")
            return 1
        if args.verbose:
            print(f"Check passed: {args.output} is up-to-date.")
        return 0

    if args.dry_run:
        print(f"Dry-run successful: Parsed {len(dataset)} lectures ({total_qas} Q&As, {total_tasks} tasks). No files written.")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(js_content, encoding="utf-8")
    print(f"Generated {args.output} ({len(dataset)} lectures, {total_qas} Q&As, {total_tasks} tasks).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
