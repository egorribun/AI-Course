#!/usr/bin/env python3
"""
Anki TSV Deck Exporter for Deep Learning Course (GUU 2026).

Generates Anki-compatible TSV flashcard decks from lecture materials:
- questions.tsv: Q&A defense questions with detailed answers and tags
- microtasks.tsv: Practice micro-tasks with full calculation solutions
- cheatsheets.tsv: High-yield cheatsheet outlines for 3-minute ticket responses

Features:
- Pure standard library implementation (no third-party dependencies)
- Robust TSV sanitization (newline escaping, tab stripping, clean UTF-8)
- CLI support: --output-dir, --lectures-dir, --dry-run, --check, --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
DEFAULT_OUTPUT_DIR = COURSE_ROOT / "anki_decks"

try:
    from tools.build_exam_data import compile_exam_dataset
except ModuleNotFoundError:
    from build_exam_data import compile_exam_dataset


def sanitize_tsv_field(text: str) -> str:
    """
    Sanitize text for TSV format:
    - Normalizes internal newlines to HTML <br> tags.
    - Replaces tabs with spaces to prevent column corruption.
    - Strips leading and trailing whitespace.
    """
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\t", " ")
    text = text.replace("\n", "<br>")
    return text


def generate_questions_deck(dataset: list[dict[str, Any]]) -> str:
    """Generate TSV content for Q&A flashcards."""
    rows: list[str] = []
    for lec in dataset:
        ticket = lec.get("ticket", f"Лекция {lec['id']}")
        module = lec.get("module", "A")
        lec_id = lec["id"]
        for qa in lec.get("qas", []):
            front = sanitize_tsv_field(f"[{ticket}] {qa['question']}")
            back = sanitize_tsv_field(qa["answer"])
            tags = f"AI_Course Block_{module} Ticket_{lec_id}"
            rows.append(f"{front}\t{back}\t{tags}")
    return "\n".join(rows) + ("\n" if rows else "")


def generate_microtasks_deck(dataset: list[dict[str, Any]]) -> str:
    """Generate TSV content for micro-task calculation flashcards."""
    rows: list[str] = []
    for lec in dataset:
        ticket = lec.get("ticket", f"Лекция {lec['id']}")
        module = lec.get("module", "A")
        lec_id = lec["id"]
        for t in lec.get("tasks", []):
            title = t.get("title", "Микро-задача")
            problem = t.get("problem", "")
            front_text = (
                f"<b>[{ticket}] {title}</b><br><br>{problem}"
                if problem
                else f"<b>[{ticket}] {title}</b>"
            )
            front = sanitize_tsv_field(front_text)
            back = sanitize_tsv_field(t.get("solution", ""))
            tags = f"AI_Course Block_{module} Microtask Ticket_{lec_id}"
            rows.append(f"{front}\t{back}\t{tags}")
    return "\n".join(rows) + ("\n" if rows else "")


def generate_cheatsheets_deck(dataset: list[dict[str, Any]]) -> str:
    """Generate TSV content for cheatsheet outline flashcards."""
    rows: list[str] = []
    for lec in dataset:
        cheat_items = lec.get("cheat_items", [])
        if not cheat_items:
            continue
        ticket = lec.get("ticket", f"Лекция {lec['id']}")
        module = lec.get("module", "A")
        lec_id = lec["id"]
        front = sanitize_tsv_field(f"[{ticket}] Шпаргалка: Скелет ответа по билету (3:00)")
        back_list = "".join(f"<li>{item}</li>" for item in cheat_items)
        back = sanitize_tsv_field(f"<ol>{back_list}</ol>")
        tags = f"AI_Course Block_{module} Cheatsheet Ticket_{lec_id}"
        rows.append(f"{front}\t{back}\t{tags}")
    return "\n".join(rows) + ("\n" if rows else "")


def export_all_decks(dataset: list[dict[str, Any]]) -> dict[str, str]:
    """Compile all three decks into a dictionary of {filename: content}."""
    return {
        "questions.tsv": generate_questions_deck(dataset),
        "microtasks.tsv": generate_microtasks_deck(dataset),
        "cheatsheets.tsv": generate_cheatsheets_deck(dataset),
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for Anki deck exporter."""
    parser = argparse.ArgumentParser(
        description="Export course Q&As, microtasks, and cheatsheets into Anki TSV decks.",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Target directory for generated TSV files (default: {DEFAULT_OUTPUT_DIR})",
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
        help="Parse lectures and generate deck contents without writing to disk.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if exported TSV files match current lectures (exit 0 if fresh, exit 1 if diff/missing).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose export statistics.",
    )

    args = parser.parse_args(argv)

    try:
        dataset = compile_exam_dataset(args.lectures_dir)
    except Exception as e:
        sys.stderr.write(f"Error parsing lectures: {e}\n")
        return 1

    decks = export_all_decks(dataset)

    total_questions = sum(1 for line in decks["questions.tsv"].splitlines() if line)
    total_microtasks = sum(1 for line in decks["microtasks.tsv"].splitlines() if line)
    total_cheatsheets = sum(1 for line in decks["cheatsheets.tsv"].splitlines() if line)

    if args.verbose:
        print(f"Loaded {len(dataset)} lectures from {args.lectures_dir}")
        print(f"  questions.tsv:   {total_questions} cards")
        print(f"  microtasks.tsv:  {total_microtasks} cards")
        print(f"  cheatsheets.tsv: {total_cheatsheets} cards")

    if args.check:
        for filename, expected_content in decks.items():
            file_path = args.output_dir / filename
            if not file_path.exists():
                sys.stderr.write(f"Check failed: {file_path} does not exist.\n")
                return 1
            current_content = file_path.read_text(encoding="utf-8")
            if current_content != expected_content:
                sys.stderr.write(
                    f"Check failed: {file_path} is outdated. Run export_anki.py to update.\n"
                )
                return 1
        if args.verbose:
            print(f"Check passed: All decks in {args.output_dir} are up-to-date.")
        return 0

    if args.dry_run:
        print(
            f"Dry-run successful: Generated {total_questions} Q&As, "
            f"{total_microtasks} microtasks, {total_cheatsheets} cheatsheets. No files written."
        )
        return 0

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in decks.items():
        file_path = args.output_dir / filename
        file_path.write_text(content, encoding="utf-8")

    print(
        f"Exported Anki decks to {args.output_dir} "
        f"({total_questions} Q&As, {total_microtasks} tasks, {total_cheatsheets} cheatsheets)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
