import re

def clean_latex(latex: str) -> str:
    """Fix double backslashes the LLM sometimes produces."""
    latex = re.sub(r"\\\\([a-zA-Z])", r"\\\1", latex)
    latex = latex.replace("\\\\", "\\")
    return latex.strip()

def extract_math(raw_text: str) -> dict:
    """
    Extract <m>...</m> regions into indexed placeholders.
    Handles malformed tags gracefully.
    """
    # First, remove any broken/unclosed tags
    # Count opens and closes
    opens = [m.start() for m in re.finditer(r"<m>", raw_text)]
    closes = [m.start() for m in re.finditer(r"</m>", raw_text)]

    # Only process well-formed pairs
    math_expressions = []
    result_text = raw_text

    # Find all properly matched <m>...</m> pairs (no nesting)
    pattern = re.compile(r"<m>((?:(?!</?m>).)+?)</m>", re.DOTALL)
    matches = list(pattern.finditer(raw_text))

    if not matches:
        # No valid math tags found — strip any broken tag fragments
        cleaned = re.sub(r"</?m>", "", raw_text)
        return {"text": cleaned.strip(), "math": []}

    # Replace from last to first to preserve positions
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

    # Reverse the math list since we processed backwards
    math_expressions.reverse()

    # Re-index placeholders
    current = 0
    def reindex(m):
        nonlocal current
        idx = current
        current += 1
        return f"$math[{idx}]$"

    result_text = re.sub(r"\$math\[\d+\]\$", reindex, result_text)

    # Clean up any remaining broken tags
    result_text = re.sub(r"</?m>", "", result_text)

    # Clean whitespace
    result_text = re.sub(r"\s*(\$math\[\d+\]\$)\s*", r" \1 ", result_text)
    result_text = re.sub(r"  +", " ", result_text).strip()

    return {"text": result_text, "math": math_expressions}
