import base64
import io

from PIL import Image


def preprocess_image_to_data_uri(
        image_bytes: bytes,
        max_side: int = 1440
) -> str:
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pil_img.thumbnail((max_side, max_side), Image.LANCZOS)

    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"
