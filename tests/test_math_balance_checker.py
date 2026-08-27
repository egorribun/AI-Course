"""
Adversarial MathJax Delimiter and Formula Balance Checker.
"""

from __future__ import annotations

import re
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"

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

def check_math_balance():
    print("=== Checking LaTeX Delimiter Balance and Structure in All 28 Lectures ===")
    total_display_pairs = 0
    total_inline_pairs = 0
    unpaired_errors = []

    for lec in EXPECTED_LECTURES:
        content = (LECTURES_DIR / lec).read_text(encoding="utf-8", errors="replace")

        # Mask non-math containers
        def repl(m):
            return "\n" * m.group(0).count("\n")

        masked = content
        masked = re.sub(r"(?s)<!--.*?-->", repl, masked)
        masked = re.sub(r"(?is)<script[^>]*>.*?</script>", repl, masked)
        masked = re.sub(r"(?is)<style[^>]*>.*?</style>", repl, masked)
        masked = re.sub(r"(?is)<pre[^>]*>.*?</pre>", repl, masked)
        masked = re.sub(r"(?is)<code[^>]*>.*?</code>", repl, masked)

        # 1. Check $$ delimiters
        # Find all double dollars
        dd_matches = list(re.finditer(r"\$\$", masked))
        if len(dd_matches) % 2 != 0:
            unpaired_errors.append(f"[{lec}] Odd count of $$ delimiters ({len(dd_matches)})")
        else:
            total_display_pairs += len(dd_matches) // 2

        # Replace valid $$...$$ with spaces
        no_dd = re.sub(r"\$\$(.*?)\$\$", lambda m: " " * len(m.group(0)), masked, flags=re.DOTALL)

        # 2. Check inline $ delimiters
        # In MathJax, inline math is $...$, but single $ outside math shouldn't break or should be balanced.
        # Find all remaining unescaped single $
        # Note: in regex, negative lookbehind (?<!\\)\$ and negative lookahead (?!\$)
        single_matches = list(re.finditer(r"(?<!\\)\$(?!\$)", no_dd))
        if len(single_matches) % 2 != 0:
            unpaired_errors.append(f"[{lec}] Odd count of inline $ delimiters ({len(single_matches)})")
            for m in single_matches:
                line = no_dd[:m.start()].count("\n") + 1
                snip = no_dd[max(0, m.start()-15):min(len(no_dd), m.start()+25)].replace("\n", " ")
                print(f"  [{lec}:{line}] single $ at: ...{snip}...")
        else:
            total_inline_pairs += len(single_matches) // 2

    print(f"Total Display Math pairs ($$...$$): {total_display_pairs}")
    print(f"Total Inline Math pairs ($...$): {total_inline_pairs}")
    print(f"Total Unpaired Delimiter Errors: {len(unpaired_errors)}")
    for e in unpaired_errors:
        print(f"  ERROR: {e}")
    assert len(unpaired_errors) == 0, "Found unbalanced LaTeX delimiters!"
    print("ALL LATEX DELIMITERS ARE 100% BALANCED!")

if __name__ == "__main__":
    check_math_balance()
