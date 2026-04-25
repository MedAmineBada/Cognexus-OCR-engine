from fastapi import APIRouter
from api.v1.routes import ocr_router

"""
Router configuration for version 1 of the OCR API.

This module aggregates all version-specific sub-routers under
the '/api/v1/ocr' prefix.
"""

router: APIRouter = APIRouter(prefix="/api/v1/ocr")
router.include_router(ocr_router)
