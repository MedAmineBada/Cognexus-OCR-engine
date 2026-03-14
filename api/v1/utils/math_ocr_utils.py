"""
Utility functions for processing and extracting mathematical expressions from OCR output.
"""
import re

def clean_latex(latex: str) -> str:
    """
    Fixes common issues in LaTeX strings, specifically double backslashes
    that might be produced by the LLM.

    Args:
        latex (str): The raw LaTeX string.

    Returns:
        str: The cleaned LaTeX string.
    """
    latex = re.sub(r"\\\\([a-zA-Z])", r"\\\1", latex)
    latex = latex.replace("\\\\", "\\")
    return latex.strip()

def extract_math(raw_text: str) -> dict:
    """
    Extracts mathematical expressions enclosed in <m>...</m> tags from a given text.
    It cleans the extracted LaTeX, filters out non-math content, and replaces
    math expressions with placeholders in the main text.

    Args:
        raw_text (str): The input text containing potential math expressions
                        enclosed in <m> and </m> tags.

    Returns:
        dict: A dictionary containing:
            - "text" (str): The text with math expressions replaced by placeholders
                            like "$math[0]$".
            - "math" (list): A list of cleaned LaTeX strings for each extracted
                             math expression.
    """
    opens = [m.start() for m in re.finditer(r"<m>", raw_text)]
    closes = [m.start() for m in re.finditer(r"</m>", raw_text)]

    math_expressions = []
    result_text = raw_text

    pattern = re.compile(r"<m>((?:(?!</?m>).)+?)</m>", re.DOTALL)
    matches = list(pattern.finditer(raw_text))

    if not matches:
        # No valid math tags found — strip any broken tag fragments
        cleaned = re.sub(r"</?m>", "", raw_text)
        return {"text": cleaned.strip(), "math": []}

    for match in reversed(matches):
        latex = clean_latex(match.group(1))
        # Skip if it's mostly English words (LLM error)
        words = latex.split()
        english_words = sum(1 for w in words if re.match(r'^[a-zA-Z]{3,}$', w)
                           and w.lower() not in ('sin', 'cos', 'tan', 'log',
                                                  'ln', 'lim', 'inf', 'max',
                                                  'min', 'det', 'dim', 'mod',
                                                  'gcd', 'lcm', 'exp'))
        if len(words) > 2 and english_words > len(words) * 0.5:
            # More than half are plain English — not math, unwrap it
            result_text = (result_text[:match.start()] +
                          match.group(1) +
                          result_text[match.end():])
            continue

        idx = len(math_expressions)
        math_expressions.append(latex)
        result_text = (result_text[:match.start()] +
                      f"$math[{idx}]$" +
                      result_text[match.end():])

    math_expressions.reverse()

    current = 0
    def reindex(m):
        nonlocal current
        idx = current
        current += 1
        return f"$math[{idx}]$"

    result_text = re.sub(r"\$math\[\d+\]\$", reindex, result_text)

    result_text = re.sub(r"</?m>", "", result_text)

    # Clean whitespace
    result_text = re.sub(r"\s*(\$math\[\d+\]\$)\s*", r" \1 ", result_text)
    result_text = re.sub(r"  +", " ", result_text).strip()

    return {"text": result_text, "math": math_expressions}
