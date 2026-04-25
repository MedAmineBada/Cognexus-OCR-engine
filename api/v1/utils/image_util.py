import base64
import io
from typing import Any

from PIL import Image

"""
Utility functions for image processing.

This module provides functionalities such as resizing and encoding
images for use within the OCR engine.
"""


def preprocess_image(
    image_bytes: bytes, max_side: int = 1440
) -> str:
    """
    Preprocesses an image by resizing it and converting it to a base64 string.

    Args:
        image_bytes: The raw bytes of the input image.
        max_side: The maximum size for the longest side of the image.
                  Defaults to 1440 pixels.

    Returns:
        A base64 encoded string of the processed image,
        prefixed with "data:image/png;base64,".
    """
    pil_img: Image.Image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pil_img.thumbnail((max_side, max_side), Image.LANCZOS)

    buffer: io.BytesIO = io.BytesIO()
    pil_img.save(buffer, format="PNG", optimize=True)
    encoded: str = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"
