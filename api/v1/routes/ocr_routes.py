"""
This module defines the API routes for OCR operations.
"""
from fastapi import APIRouter, UploadFile, File
from api.v1.services.ocr_services import ocr_scan

router = APIRouter()


@router.post("/scan")
async def scan(file: UploadFile = File(...)):
    """
    Endpoint to scan an uploaded image file and perform OCR.
    """
    return await ocr_scan(file)
