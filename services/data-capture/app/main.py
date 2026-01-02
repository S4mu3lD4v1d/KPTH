import json
import logging
import os
from typing import Optional

import boto3
from cryptography.fernet import Fernet
from fastapi import FastAPI, File, HTTPException, UploadFile
from kafka import KafkaProducer
from pydantic import BaseModel, Field

app = FastAPI(title="Data Capture Service")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("data-capture")

producer = KafkaProducer(
    bootstrap_servers=os.getenv("REDPANDA_BROKERS", "redpanda:9092"),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

s3 = boto3.client(
    's3',
    endpoint_url=f"http://{os.getenv('MINIO_ENDPOINT', 'minio:9000')}",
    aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('MINIO_SECRET_KEY')
)

bucket_name = os.getenv("MINIO_BUCKET", "kindpath-data")

def load_cipher() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is required for data-capture")
    return Fernet(key.encode())

cipher = load_cipher()

class IngestResponse(BaseModel):
    status: str
    file: str
    metadata: Optional[str] = Field(default=None, description="Metadata payload passed through")

@app.post("/ingest")
async def ingest_data(file: UploadFile = File(...), metadata: str = ""):
    encrypted_data = cipher.encrypt(await file.read())
    try:
        s3.put_object(Bucket=bucket_name, Key=file.filename, Body=encrypted_data)
    except Exception:
        logger.exception("Failed to write to bucket %s", bucket_name)
        raise HTTPException(status_code=500, detail="Failed to store encrypted file")
    message = {"filename": file.filename, "metadata": metadata}
    try:
        producer.send(os.getenv("REDPANDA_TOPIC_DATA", "data_topic"), message)
        producer.flush()
    except Exception:
        logger.exception("Failed to publish ingest message")
        raise HTTPException(status_code=500, detail="Failed to publish ingest message")
    return IngestResponse(status="ingested", file=file.filename, metadata=metadata)

@app.get("/health")
def health():
    return {"status": "ok", "bucket": bucket_name}

@app.on_event("startup")
def ensure_bucket():
    try:
        existing = s3.list_buckets().get("Buckets", [])
        if not any(b["Name"] == bucket_name for b in existing):
            s3.create_bucket(Bucket=bucket_name)
            logger.info("Created bucket %s", bucket_name)
    except Exception:
        logger.exception("Failed to ensure bucket %s exists", bucket_name)
