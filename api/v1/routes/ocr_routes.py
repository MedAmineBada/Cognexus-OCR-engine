from fastapi import APIRouter, UploadFile, File

from api.v1.services.ocr_services import ocr_scan

router = APIRouter()

@router.post("/scan")
async def scan(file: UploadFile = File(...)):
    return await ocr_scan(file)