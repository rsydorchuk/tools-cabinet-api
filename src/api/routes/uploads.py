import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_session
from ...schemas.job import UploadRequest, UploadResponse
from ...services import job_service
from ..deps import get_current_user_id

router = APIRouter(tags=["jobs"])


@router.post("/uploads", response_model=UploadResponse, status_code=201)
async def create_upload(
    payload: UploadRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    return await job_service.create_job(session, user_id, payload)


@router.post("/uploads/{job_id}/complete", status_code=204)
async def complete_upload(
    job_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    job = await job_service.confirm_upload(session, user_id, job_id)
    if job is None:
        raise HTTPException(404, "Job not found or already processed")
