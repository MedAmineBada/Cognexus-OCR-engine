from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/ocr")

@router.post("/scan")
async def scan():
    pass