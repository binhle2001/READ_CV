from fastapi import APIRouter, Request, Depends, Response, status, BackgroundTasks
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from .schema import ProcessStatus, Hook
from fastapi.responses import JSONResponse
import httpx
from typing import List

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
async def get_all_candidate_info(files: List[UploadFile] = File(...)):
    candidate_infors = []
    for file in files:
        contents = await file.read()
        candidate_infor = extract_candidate_info(contents)
        candidate_infors.append({
            "file_name": file.filename,
            "candidate_info": candidate_infor
        })
    response = {
        "http_code": status.HTTP_200_OK,
        "data": candidate_infors
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


    