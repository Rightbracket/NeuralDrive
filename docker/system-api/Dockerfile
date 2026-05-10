FROM python:3.11-slim

RUN pip install --no-cache-dir fastapi uvicorn psutil httpx

COPY config/includes.chroot/usr/lib/neuraldrive/api/neuraldrive_api /app/neuraldrive_api

WORKDIR /app

ENV NEURALDRIVE_CONTAINER=1

CMD ["uvicorn", "neuraldrive_api.main:app", "--host", "0.0.0.0", "--port", "3001"]
