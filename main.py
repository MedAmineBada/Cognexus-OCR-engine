import re
import json

from fastapi import FastAPI, UploadFile, File
from starlette.responses import Response
from api.main_router import router
from config import llm
from config.env_config import env
from utils.image_util import preprocess_image_to_data_uri

app = FastAPI()
app.include_router(router)


# ── Prompts (simplified = more reliable) ───────────────────────────

SYSTEM_PROMPT = """\
You are a handwriting OCR assistant. Transcribe all text from images.

For math: wrap each self-contained mathematical expression in <m> and </m> tags.
Use LaTeX inside the tags. Use single backslashes.

What counts as ONE math expression:
- A full equation: <m>x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}</m>
- A standalone formula: <m>ax^2 + bx + c = 0</m>
- A condition: <m>a \\neq 0</m>
- A single variable or term used mathematically: <m>b^2 - 4ac</m>

Rules:
- NEVER put plain English words inside <m> tags
- NEVER split one equation across multiple tags
- Every <m> must have a matching </m> on the same expression
- All non-math text stays outside the tags exactly as written

Example:
Image: "Quadratic Formula: x = (-b ± √(b²-4ac)) / 2a"
Output: Quadratic Formula: <m>x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}</m>

Example:
Image: "Solve ax² + bx + c = 0 where a ≠ 0"
Output: Solve <m>ax^2 + bx + c = 0</m> where <m>a \\neq 0</m>

Return ONLY the transcription with <m> tags. Nothing else.\
"""

USER_PROMPT = """\
Transcribe everything in this image. Wrap each math expression in <m>...</m> tags.
Return only the transcription.\
"""


# ── Helpers ────────────────────────────────────────────────────────

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


# ── Endpoint ───────────────────────────────────────────────────────

@app.post("/")
async def scan(file: UploadFile = File(...)):
    image_bytes = await file.read()
    data_uri = preprocess_image_to_data_uri(image_bytes, max_side=env.MAX_SIDE)

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {"type": "text", "text": USER_PROMPT},
                ],
            },
        ],
        max_tokens=4096,
        temperature=0.1,
        repeat_penalty=1.0,
        top_p=1.0,
    )

    raw_content = response["choices"][0]["message"]["content"]
    usage = response.get("usage", {})
    result = extract_math(raw_content)

    payload = {
        "text": result["text"],
        "math": result["math"],
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }

    raw_json = json.dumps(payload, ensure_ascii=False)
    raw_json = raw_json.replace("\\\\", "\\")

    return Response(content=raw_json, media_type="application/json")