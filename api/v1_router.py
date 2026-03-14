"""
API router for version 1 of the OCR service.

This module sets up the API router for the /api/v1/ocr endpoint
and includes the OCR-specific routes.
"""
from fastapi import APIRouter
from api.v1.routes import ocr_router

router = APIRouter(prefix="/api/v1/ocr")
router.include_router(ocr_router)
