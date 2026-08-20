# syntax=docker/dockerfile:1
#
# Same image for local and dev/prod — env-selected config, not build-time branching.
# Container Apps pulls linux/amd64 only: pass --platform linux/amd64 when building
# on ARM hardware.

FROM python:3.12-slim AS base
WORKDIR /app
# libmagic1: runtime lib for python-magic (magic-byte content detection, not extension)
RUN apt-get update && apt-get install -y --no-install-recommends libmagic1 \
    && rm -rf /var/lib/apt/lists/*

FROM base AS deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS runtime
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin
COPY src ./src
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
