import json
import uuid

from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

from ..config import get_settings


async def publish_job_ready(job_id: uuid.UUID) -> None:
    settings = get_settings()
    async with ServiceBusClient.from_connection_string(settings.servicebus_connection_string) as client:
        async with client.get_queue_sender(settings.queue_name) as sender:
            await sender.send_messages(ServiceBusMessage(json.dumps({"job_id": str(job_id)})))
