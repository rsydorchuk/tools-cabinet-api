import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Job
from ..schemas.job import JobStatus, UploadRequest, UploadResponse
from .queue import publish_job_ready
from .sas import issue_download_sas, issue_upload_sas


async def create_job(session: AsyncSession, user_id: uuid.UUID, payload: UploadRequest) -> UploadResponse:
    job_id = uuid.uuid4()
    blob_name = f"{job_id}/{payload.filename}"

    job = Job(
        id=job_id,
        user_id=user_id,
        tool=payload.tool,
        from_format=payload.from_format,
        to_format=payload.to_format,
        status="pending",
        source_blob_path=blob_name,
    )
    session.add(job)
    await session.commit()

    upload_url, expires_at = await issue_upload_sas(blob_name)
    return UploadResponse(job_id=job_id, upload_url=upload_url, expires_at=expires_at)


async def get_job_for_user(session: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> Job | None:
    job = await session.get(Job, job_id)
    if job is None or job.user_id != user_id:
        return None
    return job


async def confirm_upload(session: AsyncSession, user_id: uuid.UUID, job_id: uuid.UUID) -> Job | None:
    job = await get_job_for_user(session, job_id, user_id)
    if job is None or job.status != "pending":
        return None
    await publish_job_ready(job_id)
    return job


async def get_job_status(session: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> JobStatus | None:
    job = await get_job_for_user(session, job_id, user_id)
    if job is None:
        return None

    output_url = None
    if job.status == "done" and job.output_blob_path is not None:
        output_url, _ = await issue_download_sas(job.output_blob_path)

    return JobStatus(job_id=job.id, status=job.status, output_url=output_url, error=job.error)
