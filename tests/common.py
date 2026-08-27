"""
Common utilities and constants for the Deep Learning course E2E test suite.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import List, Optional, Set, Tuple

# Course Paths
COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
DL_GUU_DIR = COURSE_ROOT / "dl_guu-dl_26"
INDEX_FILE = COURSE_ROOT / "index.html"

# Expected 28 Lectures (00 to 27)
EXPECTED_LECTURES = [
    "00-intro-ml.html",
    "01-fcnn.html",
    "02-autodiff-pinn.html",
    "03-losses-mle.html",
    "04-cnn-layers.html",
    "05-cnn-architectures.html",
    "06-optimizers.html",
    "07-hyperparams.html",
    "08-metric-learning.html",
    "09-contrastive-ssl.html",
    "10-vae.html",
    "11-gan.html",
    "12-diffusion.html",
    "13-cv-tasks.html",
    "14-rnn-lstm.html",
    "15-attention-seq2seq.html",
    "16-transformers.html",
    "17-self-attention.html",
    "18-lstm-vs-transformer.html",
    "19-text-word2vec.html",
    "20-mt-bleu.html",
    "21-enc-dec.html",
    "22-rl-intro.html",
    "23-bellman.html",
    "24-vi-pi-mc.html",
    "25-td-qlearning.html",
    "26-policy-gradient.html",
    "27-actor-critic.html",
]

# 25 Exam Tickets mapping & essential topic keywords
TICKETS_METADATA = {
    1: {
        "title": "Однослойные и многослойные полносвязные сети. Функции активации. Прямое и обратное распространение",
        "lectures": ["01-fcnn.html", "00-intro-ml.html"],
        "keywords": ["полносвязн", "активаци", "обратн", "backprop", "градиент", "перцептрон"],
    },
    2: {
        "title": "Автоматическое дифференцирование. PINN",
        "lectures": ["02-autodiff-pinn.html"],
        "keywords": ["автодифференцирован", "PINN", "невязк", "производн", "autograd"],
    },
    3: {
        "title": "Loss-функции. Метод максимального правдоподобия. Связь ММП и L2",
        "lectures": ["03-losses-mle.html"],
        "keywords": ["loss", "MSE", "MAE", "правдоподоби", "L2", "кросс-энтропи"],
    },
    4: {
        "title": "Слои свёрточных сетей",
        "lectures": ["04-cnn-layers.html"],
        "keywords": ["свёртк", "ядро", "stride", "padding", "BatchNorm", "пулинг"],
    },
    5: {
        "title": "Архитектуры CNN. Передача обучения",
        "lectures": ["05-cnn-architectures.html"],
        "keywords": ["LeNet", "ResNet", "skip-connection", "transfer learning", "fine-tuning"],
    },
    6: {
        "title": "Оптимизация: SGD, Momentum, Adam, RMSProp. Матричные производные",
        "lectures": ["06-optimizers.html"],
        "keywords": ["SGD", "Momentum", "Adam", "RMSProp", "матричн", "производн"],
    },
    7: {
        "title": "Аугментация, гиперпараметры, байесовская оптимизация",
        "lectures": ["07-hyperparams.html"],
        "keywords": ["аугментац", "гиперпараметр", "Байесовск", "Hyperband"],
    },
    8: {
        "title": "Метрические методы. Сиамские сети. Функции ошибок",
        "lectures": ["08-metric-learning.html"],
        "keywords": ["метрическ", "сиамск", "contrastive", "triplet", "margin"],
    },
    9: {
        "title": "Контрастивное обучение и self-supervised learning",
        "lectures": ["09-contrastive-ssl.html"],
        "keywords": ["контрастивн", "self-supervised", "InfoNCE", "SimCLR", "MoCo"],
    },
    10: {
        "title": "Автоэнкодеры: VAE, CVAE, репараметризационный трюк",
        "lectures": ["10-vae.html"],
        "keywords": ["автоэнкодер", "VAE", "CVAE", "ELBO", "репараметризац", "KL"],
    },
    11: {
        "title": "Генеративные модели: GAN",
        "lectures": ["11-gan.html"],
        "keywords": ["GAN", "генератор", "дискриминатор", "минимакс", "collapse"],
    },
    12: {
        "title": "Диффузионные модели и Задачи компьютерного зрения",
        "lectures": ["12-diffusion.html", "13-cv-tasks.html"],
        "keywords": ["диффузион", "DDPM", "сегментац", "детекция", "IoU", "mAP"],
    },
    13: {
        "title": "Рекуррентные сети. LSTM, biLSTM. Регрессия, авторегрессия, seq2seq",
        "lectures": ["14-rnn-lstm.html"],
        "keywords": ["рекуррентн", "LSTM", "biLSTM", "BPTT", "градиент"],
    },
    14: {
        "title": "Механизм внимания в seq2seq",
        "lectures": ["15-attention-seq2seq.html"],
        "keywords": ["внимани", "attention", "seq2seq", "Bahdanau", "Luong", "выравниван"],
    },
    15: {
        "title": "Трансформеры: архитектура, элементы, принцип работы",
        "lectures": ["16-transformers.html"],
        "keywords": ["трансформер", "Multi-Head Attention", "энкодер", "декодер", "LayerNorm"],
    },
    16: {
        "title": "Внимание и самовнимание. Q, K, V, Masked Attention",
        "lectures": ["17-self-attention.html"],
        "keywords": ["самовнимани", "self-attention", "Query", "Key", "Value", "маск"],
    },
    17: {
        "title": "LSTM vs Трансформер",
        "lectures": ["18-lstm-vs-transformer.html"],
        "keywords": ["LSTM", "трансформер", "параллелизм", "памят", "сложност"],
    },
    18: {
        "title": "Предобработка текстов. Word2vec. Что такое токен",
        "lectures": ["19-text-word2vec.html"],
        "keywords": ["предобработк", "токен", "word2vec", "CBOW", "Skip-gram"],
    },
    19: {
        "title": "Машинный перевод. Модель языка. BLEU",
        "lectures": ["20-mt-bleu.html"],
        "keywords": ["машинный перевод", "языковая модель", "BLEU", "beam search"],
    },
    20: {
        "title": "Архитектуры Энкодер, Декодер, Энкодер-Декодер",
        "lectures": ["21-enc-dec.html"],
        "keywords": ["энкодер", "декодер", "BERT", "GPT", "T5"],
    },
    21: {
        "title": "RL: строение агента. Стратегия, полезность, модель",
        "lectures": ["22-rl-intro.html"],
        "keywords": ["подкреплен", "агент", "MDP", "стратеги", "полезност"],
    },
    22: {
        "title": "Уравнение Беллмана, Итерации по полезностям/стратегиям, Монте-Карло",
        "lectures": ["23-bellman.html", "24-vi-pi-mc.html"],
        "keywords": ["Беллман", "оптимальност", "Value Iteration", "Policy Iteration", "Монте-Карло"],
    },
    23: {
        "title": "Базовые алгоритмы RL: TD, Q-learning",
        "lectures": ["25-td-qlearning.html"],
        "keywords": ["TD", "SARSA", "Q-learning", "DQN", "replay"],
    },
    24: {
        "title": "Алгоритмы на основе стратегии: CEM, Policy Gradient",
        "lectures": ["26-policy-gradient.html"],
        "keywords": ["стратеги", "Policy Gradient", "REINFORCE", "baseline"],
    },
    25: {
        "title": "Value-based vs Policy-based. Actor-Critic",
        "lectures": ["27-actor-critic.html"],
        "keywords": ["Actor-Critic", "актор-критик", "Value-based", "Advantage", "SAC"],
    },
}


def read_file(path: Path) -> str:
    """Read a text file with utf-8 encoding."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    clean = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean)


@dataclass
class CodeBlock:
    filename: str
    line_number: int
    raw_html: str
    clean_code: str
    is_python: bool


def extract_code_blocks(html_content: str, filename: str = "") -> List[CodeBlock]:
    """
    Extracts all code blocks inside <pre><code> or <pre> from HTML content.
    Cleans HTML tags and decodes entities.
    Determines if block represents Python code.
    """
    blocks: List[CodeBlock] = []

    # Match <pre ...><code ...>...</code></pre> or <pre ...>...</pre>
    pattern = re.compile(r"<pre[^>]*>(?:<code[^>]*>)?(.*?)(?:</code>)?</pre>", re.DOTALL | re.IGNORECASE)

    for match in pattern.finditer(html_content):
        start_pos = match.start()
        line_no = html_content[:start_pos].count("\n") + 1
        raw_code = match.group(1)

        # Clean tags: replace <span> and other tags with their text
        clean = re.sub(r"<[^>]+>", "", raw_code)
        clean = html.unescape(clean).strip()

        if not clean:
            continue

        # Determine if Python
        # Python heuristics
        py_keywords = [
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
        ]
        is_py = any(kw in clean for kw in py_keywords)

        # Also verify it's not pure bash/ascii diagram
        if clean.startswith("$ ") or clean.startswith("# ASCII") or "+---" in clean or "|---" in clean:
            is_py = False

        blocks.append(
            CodeBlock(
                filename=filename,
                line_number=line_no,
                raw_html=raw_code,
                clean_code=clean,
                is_python=is_py,
            )
        )

    return blocks


@dataclass
class MathBlock:
    filename: str
    line_number: int
    raw_latex: str
    is_display: bool  # True for $$, False for $


def extract_math_blocks(html_content: str, filename: str = "") -> List[MathBlock]:
    """
    Extracts all LaTeX math expressions ($$...$$ and $...$).
    Ignores math inside <pre>, <code>, <script>, <style>, and <!-- comments -->.
    """
    # First, mask out contents of <pre>, <code>, <script>, <style>, and comments
    masked = html_content

    # Replace <script>...</script> and <style>...</style> and comments and <pre>...</pre> and <code>...</code> with spaces to preserve line numbers
    def replace_with_whitespace(match):
        return "\n" * match.group(0).count("\n")

    masked = re.sub(r"<!--.*?-->", replace_with_whitespace, masked, flags=re.DOTALL)
    masked = re.sub(r"<script[^>]*>.*?</script>", replace_with_whitespace, masked, flags=re.DOTALL | re.IGNORECASE)
    masked = re.sub(r"<style[^>]*>.*?</style>", replace_with_whitespace, masked, flags=re.DOTALL | re.IGNORECASE)
    masked = re.sub(r"<pre[^>]*>.*?</pre>", replace_with_whitespace, masked, flags=re.DOTALL | re.IGNORECASE)
    masked = re.sub(r"<code[^>]*>.*?</code>", replace_with_whitespace, masked, flags=re.DOTALL | re.IGNORECASE)

    blocks: List[MathBlock] = []

    # Display math $$ ... $$
    display_pattern = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)
    for m in display_pattern.finditer(masked):
        start = m.start()
        line = masked[:start].count("\n") + 1
        blocks.append(MathBlock(filename=filename, line_number=line, raw_latex=m.group(1).strip(), is_display=True))

    # Mask display math so inline search doesn't match inner parts
    no_display = display_pattern.sub(lambda m: " " * len(m.group(0)), masked)

    # Inline math $ ... $
    # Must not match escaped \$ and single dollar without closing
    # Matches $...$ where content doesn't start or end with space and doesn't span more than 5 lines
    inline_pattern = re.compile(r"(?<!\\)\$(?!\$)(.*?)(?<!\\)\$", re.DOTALL)
    for m in inline_pattern.finditer(no_display):
        start = m.start()
        line = no_display[:start].count("\n") + 1
        content = m.group(1).strip()
        if content and "\n\n" not in content:
            blocks.append(MathBlock(filename=filename, line_number=line, raw_latex=content, is_display=False))

    return blocks


def validate_latex_syntax(raw_latex: str) -> List[str]:
    """
    Validates LaTeX syntax for balanced braces, brackets, and known syntax issues.
    Returns list of error messages (empty if valid).
    """
    errors = []

    # Check for unescaped HTML entities that corrupt LaTeX
    if "&lt;" in raw_latex or "&gt;" in raw_latex or "&amp;" in raw_latex:
        errors.append(f"Contains raw unescaped HTML entities in LaTeX: {raw_latex[:50]}")

    # Check brace balance {...} (strict in LaTeX)
    brace_count = 0
    i = 0
    n = len(raw_latex)
    while i < n:
        c = raw_latex[i]
        if c == "\\" and i + 1 < n:
            # Check for escaped braces \{ or \}
            if raw_latex[i + 1] in ("{", "}", "$", "%", "&", "_", "#"):
                i += 2
                continue
            cmd_match = re.match(r"\\[a-zA-Z]+", raw_latex[i:])
            if cmd_match:
                i += len(cmd_match.group(0))
                continue
        elif c == "{":
            brace_count += 1
        elif c == "}":
            brace_count -= 1
            if brace_count < 0:
                errors.append(f"Unmatched closing brace '}}' in: {raw_latex[:60]}")
                break
        i += 1

    if brace_count > 0:
        errors.append(f"Unclosed opening brace '{{' (deficit {brace_count}) in: {raw_latex[:60]}")

    # Check for malformed commands like \frac without second argument
    if re.search(r"\\frac\s*\{[^{}]*\}\s*$", raw_latex):
        errors.append(f"Incomplete \\frac command missing second group: {raw_latex[:60]}")

    # Check for \begin{env} without \end{env}
    begins = re.findall(r"\\begin\{([a-zA-Z*]+)\}", raw_latex)
    ends = re.findall(r"\\end\{([a-zA-Z*]+)\}", raw_latex)
    if sorted(begins) != sorted(ends):
        errors.append(f"Mismatched LaTeX environments: \\begin={begins} vs \\end={ends}")

    # Check for \left without \right
    left_count = len(re.findall(r"\\left(?:\(|\[|\\\{|\||\.)", raw_latex))
    right_count = len(re.findall(r"\\right(?:\)|\]|\\\}|\||\.)", raw_latex))
    if left_count != right_count:
        errors.append(f"Mismatched \\left ({left_count}) and \\right ({right_count}) in: {raw_latex[:60]}")

    return errors


class CourseStructureParser(HTMLParser):
    """
    HTML parser that extracts:
    - details.qa elements
    - div.task elements and sol blocks
    - div.cheat elements
    - a.backlink elements
    - navrow prev/next links
    - pills (.pill)
    - all element IDs (anchors)
    - all <a href="..."> links
    """

    def __init__(self):
        super().__init__()
        self.qa_count = 0
        self.task_count = 0
        self.sol_count = 0
        self.has_cheat = False
        self.cheat_text = ""
        self.backlinks: List[str] = []
        self.navrow_links: List[Tuple[str, str]] = []  # (href, text)
        self.pills: List[str] = []
        self.element_ids: Set[str] = set()
        self.all_hrefs: List[Tuple[str, int]] = []  # (href, line_number)

        # Internal state
        self._tag_stack: List[str] = []
        self._cheat_depth = 0
        self._in_pill = False
        self._in_navrow = False
        self._current_navrow_href: Optional[str] = None
        self._current_navrow_text = ""
        self._current_pill_text = ""

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        classes = attr_dict.get("class", "").split()
        tag_id = attr_dict.get("id")

        if tag_id:
            self.element_ids.add(tag_id)

        href = attr_dict.get("href")
        if href is not None and tag == "a":
            self.all_hrefs.append((href, self.getpos()[0]))

        if tag == "details" and "qa" in classes:
            self.qa_count += 1

        if tag == "div" and "task" in classes:
            self.task_count += 1

        if ("sol" in classes) or (tag == "details" and "sol" in classes):
            self.sol_count += 1

        if tag == "div":
            if "cheat" in classes:
                self.has_cheat = True
                self._cheat_depth = 1
            elif self._cheat_depth > 0:
                self._cheat_depth += 1

        if "pill" in classes:
            self._in_pill = True
            self._current_pill_text = ""

        if tag == "a" and "backlink" in classes and href:
            self.backlinks.append(href)

        if "navrow" in classes:
            self._in_navrow = True

        if self._in_navrow and tag == "a" and href:
            self._current_navrow_href = href
            self._current_navrow_text = ""

        self._tag_stack.append(tag)

    def handle_endtag(self, tag: str):
        if tag == "div" and self._cheat_depth > 0:
            self._cheat_depth -= 1

        if self._in_pill and tag in ("span", "div", "a"):
            self._in_pill = False
            self.pills.append(self._current_pill_text.strip())

        if self._in_navrow and tag == "div":
            self._in_navrow = False

        if self._current_navrow_href is not None and tag == "a":
            self.navrow_links.append((self._current_navrow_href, self._current_navrow_text.strip()))
            self._current_navrow_href = None

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

    def handle_data(self, data: str):
        if self._cheat_depth > 0:
            self.cheat_text += data
        if self._in_pill:
            self._current_pill_text += data
        if self._current_navrow_href is not None:
            self._current_navrow_text += data


def parse_lecture_structure(html_content: str) -> CourseStructureParser:
    """Parse lecture HTML and extract structure metadata."""
    parser = CourseStructureParser()
    parser.feed(html_content)
    return parser
