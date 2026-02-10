import base64
import io

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from fastapi import FastAPI, UploadFile, File
from api.main_router import router
from config import llm

app = FastAPI()
app.include_router(router)


def preprocess_image_to_data_uri(
    image_bytes: bytes,
    max_side: int = 1024
) -> str:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pil_img.thumbnail((max_side, max_side), Image.LANCZOS)

        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG", optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return f"data:image/png;base64,{encoded}"

@app.post("/")
async def scan(file: UploadFile = File(...)):
    image_bytes = await file.read()

    data_uri = preprocess_image_to_data_uri(image_bytes, max_side=1440)

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert handwriting transcription assistant. "
                    "You read handwritten text with extreme precision, "
                    "including ambiguous letters, crossed-out words, "
                    "and unusual spacing. You never guess — if a word "
                    "is illegible, you mark it as [illegible]."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {
                        "type": "text",
                        "text": (
                            "Carefully extract ALL handwritten text from this image. "
                            "Preserve original line breaks and paragraph structure. "
                            "Pay close attention to:\n"
                            "- Letters that look similar (a/o, n/m, l/I, e/c)\n"
                            "- Punctuation and capitalization\n"
                            "- Numbers vs letters\n"
                            "Return ONLY the transcribed text, nothing else."
                        ),
                    },
                ],
            },
        ],
        max_tokens=4096,
        temperature=0.3,
        repeat_penalty=1.0,
        top_p=1.0
    )

    text = response["choices"][0]["message"]["content"]
    usage = response.get("usage", {})

    cleaned_text = " ".join(text.split())

    return {
        "text": cleaned_text,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        },
    }