import logging
import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from fastapi import FastAPI, HTTPException
from meilisearch import Client
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

app = FastAPI(title="Digital Library Service")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("digital-library")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}",
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

meili = Client(os.getenv("MEILISEARCH_URL"), os.getenv("MEILISEARCH_API_KEY"))

def load_cipher() -> Fernet:
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is required for digital-library")
    return Fernet(key.encode())

cipher = load_cipher()

class Literature(Base):
    __tablename__ = "literature"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    redacted = Column(Text)  # JSON of redaction info
    provenance = Column(Text)  # JSON of changes
    currency_date = Column(DateTime)  # For currency metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    links = relationship("LiteratureLink", back_populates="literature")
    versions = relationship("LiteratureVersion", back_populates="literature")

class LiteratureLink(Base):
    __tablename__ = "literature_links"
    id = Column(Integer, primary_key=True)
    literature_id = Column(Integer, ForeignKey("literature.id"))
    linked_id = Column(Integer, ForeignKey("literature.id"))
    link_type = Column(String)  # e.g., "related", "cites", "redacted_from"
    literature = relationship("Literature", foreign_keys=[literature_id], back_populates="links")
    linked = relationship("Literature", foreign_keys=[linked_id])

class LiteratureVersion(Base):
    __tablename__ = "literature_versions"
    id = Column(Integer, primary_key=True)
    literature_id = Column(Integer, ForeignKey("literature.id"))
    content = Column(Text)
    change_reason = Column(String)
    changed_by = Column(String)  # e.g., "user" or "system"
    changed_at = Column(DateTime, default=datetime.utcnow)
    literature = relationship("Literature", back_populates="versions")

Base.metadata.create_all(bind=engine)

class LiteratureCreate(BaseModel):
    title: str
    content: str
    redacted: bool = False
    redaction_reason: str = ""
    currency_date: str = None  # ISO format

class LinkCreate(BaseModel):
    linked_id: int
    link_type: str

class VersionUpdate(BaseModel):
    content: str
    change_reason: str
    changed_by: str = "user"

@app.post("/literature")
def create_literature(item: LiteratureCreate):
    with SessionLocal() as db:
        encrypted_content = cipher.encrypt(item.content.encode())
        redaction_info = {"redacted": item.redacted, "reason": item.redaction_reason} if item.redacted else {}
        try:
            currency = datetime.fromisoformat(item.currency_date) if item.currency_date else datetime.utcnow()
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid currency_date format. Use ISO 8601.")
        lit = Literature(
            title=item.title,
            content=encrypted_content.decode(),
            redacted=str(redaction_info),
            currency_date=currency,
        )
        try:
            db.add(lit)
            db.commit()
            db.refresh(lit)
        except Exception:
            db.rollback()
            logger.exception("Failed to persist literature")
            raise HTTPException(status_code=500, detail="Failed to create literature")
    try:
        meili.index('literature').add_documents([{"id": lit.id, "title": lit.title, "content": item.content}])
    except Exception:
        logger.exception("Failed to index literature %s", lit.id)
    return lit

@app.put("/literature/{id}")
def update_literature(id: int, update: VersionUpdate):
    with SessionLocal() as db:
        lit = db.query(Literature).filter(Literature.id == id).first()
        if not lit:
            raise HTTPException(status_code=404, detail="Not found")
        version = LiteratureVersion(
            literature_id=id,
            content=lit.content,
            change_reason=update.change_reason,
            changed_by=update.changed_by,
        )
        db.add(version)
        encrypted_content = cipher.encrypt(update.content.encode())
        lit.content = encrypted_content.decode()
        lit.provenance = str(
            {"last_change": update.change_reason, "changed_by": update.changed_by, "at": str(datetime.utcnow())}
        )
        try:
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to update literature %s", id)
            raise HTTPException(status_code=500, detail="Failed to update literature")
    try:
        meili.index('literature').update_documents([{"id": lit.id, "content": update.content}])
    except Exception:
        logger.exception("Failed to update index for literature %s", id)
    return lit

@app.post("/literature/{id}/link")
def add_link(id: int, link: LinkCreate):
    with SessionLocal() as db:
        lit = db.query(Literature).filter(Literature.id == id).first()
        if not lit:
            raise HTTPException(status_code=404, detail="Literature not found")
        linked = db.query(Literature).filter(Literature.id == link.linked_id).first()
        if not linked:
            raise HTTPException(status_code=404, detail="Linked literature not found")
        new_link = LiteratureLink(literature_id=id, linked_id=link.linked_id, link_type=link.link_type)
        db.add(new_link)
        try:
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Failed to link literature %s -> %s", id, link.linked_id)
            raise HTTPException(status_code=500, detail="Failed to create link")
    return {"status": "linked"}

@app.get("/literature/{id}/map")
def get_literature_map(id: int):
    with SessionLocal() as db:
        lit = db.query(Literature).filter(Literature.id == id).first()
        if not lit:
            raise HTTPException(status_code=404, detail="Not found")
        links = db.query(LiteratureLink).filter(LiteratureLink.literature_id == id).all()
        versions = db.query(LiteratureVersion).filter(LiteratureVersion.literature_id == id).all()
    map_data = {
        "id": lit.id,
        "title": lit.title,
        "links": [{"linked_id": l.linked_id, "type": l.link_type} for l in links],
        "versions": [{"id": v.id, "change_reason": v.change_reason, "changed_by": v.changed_by, "at": v.changed_at.isoformat()} for v in versions],
        "provenance": lit.provenance,
        "currency": lit.currency_date.isoformat() if lit.currency_date else None
    }
    return map_data

@app.get("/literature/currency")
def check_currency(days_old: int = 365):
    with SessionLocal() as db:
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        outdated = db.query(Literature).filter(Literature.currency_date < cutoff).all()
    return [{"id": l.id, "title": l.title, "currency_date": l.currency_date.isoformat()} for l in outdated]

@app.get("/literature/search")
def search_literature(q: str):
    try:
        results = meili.index('literature').search(q)
    except Exception:
        logger.exception("Search failed for query %s", q)
        raise HTTPException(status_code=500, detail="Search failed")
    return results

@app.get("/literature/{id}")
def get_literature(id: int):
    with SessionLocal() as db:
        lit = db.query(Literature).filter(Literature.id == id).first()
        if not lit:
            raise HTTPException(status_code=404, detail="Not found")
    decrypted = cipher.decrypt(lit.content.encode()).decode()
    return {
        "id": lit.id,
        "title": lit.title,
        "content": decrypted,
        "redacted": lit.redacted,
        "provenance": lit.provenance,
    }

@app.get("/health")
def health():
    try:
        meili_health = meili.health()
    except Exception:
        meili_health = {"status": "unreachable"}
    return {"status": "ok", "meili": meili_health}

@app.on_event("startup")
def ensure_meili_index():
    try:
        indexes = {i.uid for i in meili.get_indexes().results}
        if "literature" not in indexes:
            meili.create_index("literature", {"primaryKey": "id"})
            logger.info("Created Meilisearch index 'literature'")
    except Exception:
        logger.exception("Failed to ensure Meilisearch index exists")
