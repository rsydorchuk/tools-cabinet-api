from contextlib import asynccontextmanager

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import CorsRule
from azure.storage.blob.aio import BlobServiceClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import auth, health, jobs, uploads
from .config import get_settings
from .db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.azure_storage_connection_string:
        async with BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        ) as client:
            for name in ("uploads", "outputs"):
                try:
                    await client.create_container(name)
                except ResourceExistsError:
                    pass

            # Browser PUTs straight to Blob using the SAS url (bytes never pass
            # through the api) — Azurite, like real Blob Storage, rejects that
            # cross-origin PUT's preflight until a CORS rule allows it. "*" is
            # fine for a local emulator nothing external can reach; the real
            # storage account needs the same rule via the portal (Settings ->
            # Resource sharing (CORS)), scoped to the real app origins.
            await client.set_service_properties(
                cors=[
                    CorsRule(
                        allowed_origins=["*"],
                        allowed_methods=["GET", "PUT", "OPTIONS", "HEAD"],
                        allowed_headers=["*"],
                        exposed_headers=["*"],
                        max_age_in_seconds=3600,
                    )
                ]
            )

    yield
    await engine.dispose()


app = FastAPI(title="Personal Tools Cabinet API", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(jobs.router)
