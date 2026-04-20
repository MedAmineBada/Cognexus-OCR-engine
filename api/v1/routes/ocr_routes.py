"""
This module defines the API routes for OCR operations.
"""
from typing import List

from fastapi import APIRouter, UploadFile, File
from api.v1.services.ocr_services import ocr_scan

router = APIRouter()


@router.post("/scan")
async def scan(files: List[UploadFile]):
    """
    Endpoint to scan an uploaded image file and perform OCR.
    """
    return await ocr_scan(files)
