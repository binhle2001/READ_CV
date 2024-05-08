from fastapi import APIRouter, Request, Depends, Response, status, BackgroundTasks
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from .schema import ProcessStatus, Hook
from fastapi.responses import JSONResponse
import httpx

from ai_core.source.reading_cv import extract_candidate_info #, push_data_to_DB


router = APIRouter(
    prefix = "/cv-reader/api/v1",
    tags = ["HRM-CV-READER"],
    dependencies = [],
    responses = {},
)

@router.get("/")
async def read_root():
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get("http://example.com")
        return response.text
    
@router.post(
    "/read-cv",
    summary= "api hook for get and extract CV email"
)
async def get_all_candidate_info(file: UploadFile = File(...)):

    contents = await file.read()
    candidate_info = extract_candidate_info(contents)
    return JSONResponse(status_code=status.HTTP_200_OK, content=candidate_info)


    