import json
from typing import List, Dict, Any

from fastapi import UploadFile
from starlette.responses import Response

from api.v1.utils.image_util import preprocess_image
from api.v1.utils.math_ocr_utils import extract_math
from config import VLM, env

"""
Core business logic for OCR processing services.

This module coordinates image preprocessing, Vision-Language Model (VLM)
interaction, and extraction of mathematical content.
"""


async def ocr_scan(
    files: List[UploadFile], system_prompt: str, user_prompt: str
) -> Response:
    """
    Processes uploaded files through the OCR engine.

    Iterates through each file, applies image preprocessing, invokes the VLM
    for text generation, and extracts structured mathematical expressions.

    Args:
        files: List of uploaded image or document files.
        system_prompt: System-level context for the VLM.
        user_prompt: Specific query or instructions for the OCR task.

    Returns:
        A Response object containing a JSON-encoded list of OCR results per file.
    """
    results: List[Dict[str, Any]] = []

    for file in files:
        image_bytes: bytes = await file.read()
        data_uri: str = preprocess_image(image_bytes, max_side=env.MAX_SIDE)

        response: Dict[str, Any] = VLM.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": user_prompt},
                    ],
                },
            ],
            max_tokens=4096,
            temperature=0.1,
            repeat_penalty=1.0,
            top_p=1.0,
        )

        raw_content: str = response["choices"][0]["message"]["content"]
        usage: Dict[str, int] = response.get("usage", {})
        extracted: Dict[str, Any] = extract_math(raw_content)

        payload: Dict[str, Any] = {
            "filename": file.filename,
            "text": extracted["text"],
            "math": extracted["math"],
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
        }
        results.append(payload)

    raw_json: str = json.dumps(results, ensure_ascii=False)
    return Response(content=raw_json, media_type="application/json")
