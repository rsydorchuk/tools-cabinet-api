import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.session import get_session
from ...schemas.job import JobStatus
from ...services import job_service
from ..deps import get_current_user_id

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(
    job_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
):
    result = await job_service.get_job_status(session, job_id, user_id)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    return result
