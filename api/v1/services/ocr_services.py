import json

from fastapi import UploadFile
from starlette.responses import Response

from api.v1.utils.image_util import preprocess_image
from api.v1.utils.math_ocr_utils import extract_math
from api.v1.vlm_prompts import SYSTEM_PROMPT_MIXED, USER_PROMPT_MIXED
from config import VLM
from config.env_config import env

async def ocr_scan(file: UploadFile):
    image_bytes = await file.read()
    data_uri = preprocess_image(image_bytes, max_side=env.MAX_SIDE)

    response = VLM.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_MIXED},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {"type": "text", "text": USER_PROMPT_MIXED},
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