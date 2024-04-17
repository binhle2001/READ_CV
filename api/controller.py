from fastapi import APIRouter, Request, Depends, Response, status, BackgroundTasks
from .schema import ProcessStatus, Hook
from fastapi.responses import JSONResponse
import logging

from ai_core.source.reading_cv import push_data_to_DB


router = APIRouter(
    prefix = "/cv-reader/api/v1",
    tags = ["HRM-CV-READER"],
    dependencies = [],
    responses = {},
)

@router.get(
    "/api-hook",
    summary= "api hook for get and extract CV email"
)
async def get_all_candidate_info(item: Hook, background_tasks: BackgroundTasks):
    if item.tenant_id in ProcessStatus.list_tenant and ProcessStatus.list_tenant[item.tenant_id]:
            response = {
                "http_code": status.HTTP_400_BAD_REQUEST,
                "content": "Tiến trình đang tồn tại"
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response)
    background_tasks.add_task(push_data_to_DB, item.tenant_id)
    response = {
        "http_code": status.HTTP_200_OK,
        "content": "Tiến trình đang chạy"
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


    