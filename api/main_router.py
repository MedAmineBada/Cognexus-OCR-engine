from fastapi import APIRouter

from api.v1.routes import ocr_router

router = APIRouter(prefix="/api/v1/ocr")
router.include_router(ocr_router)