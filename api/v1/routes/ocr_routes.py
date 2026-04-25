from typing import List, Any

from fastapi import APIRouter, UploadFile, Form

from api.v1.services.ocr_services import ocr_scan

"""
API route definitions for OCR operations.

This module exposes endpoints for scanning documents and images using
the internal OCR service.
"""

router: APIRouter = APIRouter()


@router.post("/scan")
async def scan(
    files: List[UploadFile],
    user_prompt: str = Form(...),
    system_prompt: str = Form(...),
) -> Any:
    """
    Performs an OCR scan on the provided files.

    Args:
        files: A list of uploaded files to be processed.
        user_prompt: Specific instructions or query from the user.
        system_prompt: System-level instructions for the OCR model.

    Returns:
        The processed OCR results from the service layer.
    """
    return await ocr_scan(files, system_prompt, user_prompt)
