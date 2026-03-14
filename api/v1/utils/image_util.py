"""
Utility functions for image processing.
"""
import base64
import io

from PIL import Image


def preprocess_image(
        image_bytes: bytes,
        max_side: int = 1440
) -> str:
    """
    Preprocesses an image by resizing it and converting it to a base64 string.

    Args:
        image_bytes (bytes): The raw image bytes.
        max_side (int): The maximum size for the longest side of the image.

    Returns:
        str: The base64 encoded string of the processed image.
    """
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pil_img.thumbnail((max_side, max_side), Image.LANCZOS)

    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{encoded}"
