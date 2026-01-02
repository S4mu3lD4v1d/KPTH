import base64
import json
import logging
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from kafka import KafkaConsumer
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI(title="Ecological Evaluation Service")
templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("ecological-eval")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB')}",
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EcoData(Base):
    __tablename__ = "eco_data"
    id = Column(Integer, primary_key=True)
    location = Column(String)
    metric = Column(String)
    value = Column(Float)
    map_data = Column(Text)  # JSON for mapping info
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class EcoCreate(BaseModel):
    location: str = Field(..., min_length=1)
    metric: str = Field(..., min_length=1)
    value: float
    map_coords: Dict[str, float] = Field(default_factory=dict, description="e.g., {'lat': 0, 'lon': 0}")

class EcoItem(BaseModel):
    id: int
    location: str
    metric: str
    value: float
    map: Dict[str, float]
    timestamp: datetime

    class Config:
        orm_mode = True

def load_cipher() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is required for ecological-eval")
    return Fernet(key.encode())

def load_signing_key() -> rsa.RSAPrivateKey:
    key_raw = os.getenv("SIGNING_KEY")
    if not key_raw:
        logger.warning("SIGNING_KEY not provided; generating ephemeral signing key")
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)
    for candidate in (key_raw, _maybe_decode_base64(key_raw)):
        if not candidate:
            continue
        try:
            return serialization.load_pem_private_key(candidate.encode(), password=None)
        except Exception:
            continue
    logger.warning("Failed to load SIGNING_KEY; falling back to ephemeral key")
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def _maybe_decode_base64(value: str) -> Optional[str]:
    try:
        return base64.b64decode(value).decode()
    except Exception:
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

cipher = load_cipher()
private_key = load_signing_key()
public_key = private_key.public_key()

EXPORT_TIMEOUT = int(os.getenv("EXPORT_TIMEOUT_SECONDS", "5"))
ECO_TOPIC = os.getenv("REDPANDA_TOPIC_ECO", "eco_topic")
DISABLE_KAFKA_CONSUMER = os.getenv("DISABLE_KAFKA_CONSUMER", "false").lower() == "true"
CONSUMER_STOP_EVENT = threading.Event()
CONSUMER_THREAD: Optional[threading.Thread] = None

def _serialize_eco_row(row: EcoData, decrypted_map: Dict[str, float]) -> Dict[str, object]:
    return {
        "id": row.id,
        "location": row.location,
        "metric": row.metric,
        "value": row.value,
        "map": decrypted_map,
        "timestamp": row.timestamp,
    }

def _send_exports(payload: Dict[str, object]) -> None:
    endpoints = [os.getenv("EXPORT_ENDPOINT_1"), os.getenv("EXPORT_ENDPOINT_2")]
    if not any(endpoints):
        logger.info("No export endpoints configured; skipping export dispatch")
        return
    encrypted_bundle = cipher.encrypt(json.dumps(payload).encode())
    signature = private_key.sign(
        encrypted_bundle,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    export_payload = {"bundle": encrypted_bundle.decode(), "signature": signature.hex()}
    for endpoint in endpoints:
        if not endpoint:
            continue
        try:
            response = requests.post(endpoint, json=export_payload, timeout=EXPORT_TIMEOUT)
            response.raise_for_status()
            logger.info("Exported bundle to %s", endpoint)
        except Exception as exc:
            logger.warning("Failed to export bundle to %s: %s", endpoint, exc)

@app.post("/eco-data", response_model=EcoItem)
def create_eco_data(item: EcoCreate):
    map_json = json.dumps(item.map_coords)
    encrypted_map = cipher.encrypt(map_json.encode())
    with SessionLocal() as db:
        data = EcoData(
            location=item.location,
            metric=item.metric,
            value=item.value,
            map_data=encrypted_map.decode(),
        )
        try:
            db.add(data)
            db.commit()
            db.refresh(data)
        except Exception:
            db.rollback()
            logger.exception("Failed to persist eco_data record")
            raise HTTPException(status_code=500, detail="Failed to save data")
    bundle = {"data": _serialize_eco_row(data, item.map_coords), "timestamp": datetime.utcnow().isoformat()}
    _send_exports(bundle)
    return _serialize_eco_row(data, item.map_coords)

@app.get("/eco-data/map", response_model=List[EcoItem])
def get_map_data():
    with SessionLocal() as db:
        data = db.query(EcoData).all()
    decrypted = []
    for d in data:
        decrypted_map = cipher.decrypt(d.map_data.encode()).decode()
        decrypted.append(_serialize_eco_row(d, json.loads(decrypted_map)))
    return decrypted

@app.get("/eco-data", response_model=List[EcoItem])
def get_eco_data():
    with SessionLocal() as db:
        rows = db.query(EcoData).all()
    payload = []
    for row in rows:
        try:
            decrypted_map = json.loads(cipher.decrypt(row.map_data.encode()).decode())
        except Exception:
            logger.warning("Failed to decrypt map for eco_data id=%s", row.id)
            decrypted_map = {}
        payload.append(_serialize_eco_row(row, decrypted_map))
    return payload

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Consumer thread
def consume_eco_topic(stop_event: threading.Event):
    logger.info("Starting Kafka consumer for topic '%s'", ECO_TOPIC)
    consumer = KafkaConsumer(
        ECO_TOPIC,
        bootstrap_servers=os.getenv("REDPANDA_BROKERS"),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=1000,
    )
    try:
        while not stop_event.is_set():
            for message in consumer:
                data = message.value
                with SessionLocal() as db:
                    eco = EcoData(
                        location=data.get("location", "unknown"),
                        metric=data.get("metric", "unknown"),
                        value=data.get("value", 0.0),
                    )
                    try:
                        db.add(eco)
                        db.commit()
                    except Exception:
                        db.rollback()
                        logger.exception("Failed to persist consumed eco data")
                        continue
            # Loop again to check stop flag after timeout
    finally:
        consumer.close()
        logger.info("Kafka consumer for '%s' stopped", ECO_TOPIC)

@app.on_event("startup")
def start_consumer():
    if DISABLE_KAFKA_CONSUMER:
        logger.info("Kafka consumer disabled via DISABLE_KAFKA_CONSUMER")
        return
    global CONSUMER_THREAD
    if CONSUMER_THREAD and CONSUMER_THREAD.is_alive():
        return
    CONSUMER_STOP_EVENT.clear()
    CONSUMER_THREAD = threading.Thread(target=consume_eco_topic, args=(CONSUMER_STOP_EVENT,), daemon=True)
    CONSUMER_THREAD.start()

@app.on_event("shutdown")
def stop_consumer():
    CONSUMER_STOP_EVENT.set()
    if CONSUMER_THREAD:
        CONSUMER_THREAD.join(timeout=2)

@app.post("/eco-data/congruence")
def send_for_congruence():
    with SessionLocal() as db:
        data = db.query(EcoData).all()
    # Aggregate data for global analysis
    aggregated = {}
    for d in data:
        key = f"{d.location}_{d.metric}"
        if key not in aggregated:
            aggregated[key] = []
        aggregated[key].append(d.value)
    # Send to global institution
    payload = {"data": aggregated, "source": "KindPath"}
    try:
        response = requests.post(
            os.getenv("GLOBAL_INSTITUTION_ENDPOINT", "https://global-climate.org/api/congruence"),
            json=payload,
            timeout=EXPORT_TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        logger.exception("Failed to send congruence payload")
        raise HTTPException(status_code=500, detail="Failed to send for congruence")
    congruence_report = response.json()
    return {"status": "sent", "report": congruence_report}

@app.get("/health")
def health():
    return {"status": "ok"}
