from datetime import datetime, timedelta, timezone

from azure.identity.aio import DefaultAzureCredential
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient

from ..config import get_settings


async def _issue_sas(container: str, blob_name: str, permission: BlobSasPermissions) -> tuple[str, datetime]:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.sas_ttl_minutes)

    if settings.azure_storage_connection_string:
        async with BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        ) as service_client:
            sas = generate_blob_sas(
                account_name=service_client.account_name,
                container_name=container,
                blob_name=blob_name,
                account_key=service_client.credential.account_key,
                permission=permission,
                expiry=expires_at,
            )
    else:
        async with (
            DefaultAzureCredential() as credential,
            BlobServiceClient(account_url=settings.azure_storage_account_url, credential=credential) as service_client,
        ):
            delegation_key = await service_client.get_user_delegation_key(
                key_start_time=datetime.now(timezone.utc),
                key_expiry_time=expires_at,
            )
            sas = generate_blob_sas(
                account_name=service_client.account_name,
                container_name=container,
                blob_name=blob_name,
                user_delegation_key=delegation_key,
                permission=permission,
                expiry=expires_at,
            )

    url = f"{settings.azure_storage_public_blob_endpoint}/{container}/{blob_name}?{sas}"
    return url, expires_at


async def issue_upload_sas(blob_name: str) -> tuple[str, datetime]:
    return await _issue_sas("uploads", blob_name, BlobSasPermissions(write=True, create=True))


async def issue_download_sas(blob_name: str) -> tuple[str, datetime]:
    return await _issue_sas("outputs", blob_name, BlobSasPermissions(read=True))
