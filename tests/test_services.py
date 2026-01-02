import importlib.util
import os
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


class FakeIndex:
    def __init__(self):
        self.documents = {}

    def add_documents(self, docs):
        for doc in docs:
            self.documents[doc["id"]] = doc

    def update_documents(self, docs):
        for doc in docs:
            self.documents[doc["id"]] = doc

    def search(self, q):
        hits = [doc for doc in self.documents.values() if q.lower() in (doc.get("title") or "").lower()]
        return {"hits": hits}


class FakeMeili:
    def __init__(self):
        self.index_obj = FakeIndex()

    def index(self, _name):
        return self.index_obj

    def get_indexes(self):
        class _Result:
            @property
            def results(self):
                return []

        return _Result()

    def create_index(self, uid, options=None):
        return {"uid": uid, "options": options}

    def health(self):
        return {"status": "available"}


def test_ecological_eval_create_and_read(tmp_path, monkeypatch):
    db_file = tmp_path / "eco.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    os.environ["DISABLE_KAFKA_CONSUMER"] = "true"
    eco_main = load_module(Path("services/ecological-eval/app/main.py"), "eco_main")
    client = TestClient(eco_main.app)

    payload = {"location": "Sydney", "metric": "temp", "value": 1.2, "map_coords": {"lat": -33.86, "lon": 151.2}}
    created = client.post("/eco-data", json=payload)
    assert created.status_code == 200
    body = created.json()
    assert body["location"] == "Sydney"
    assert body["map"]["lat"] == payload["map_coords"]["lat"]

    listed = client.get("/eco-data")
    assert listed.status_code == 200
    data = listed.json()
    assert len(data) == 1
    assert data[0]["metric"] == "temp"


def test_digital_library_create_and_search(tmp_path, monkeypatch):
    db_file = tmp_path / "library.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
    os.environ["MEILISEARCH_URL"] = "http://example.meili"
    os.environ["MEILISEARCH_API_KEY"] = "test"
    dl_main = load_module(Path("services/digital-library/app/main.py"), "dl_main")
    dl_main.meili = FakeMeili()

    client = TestClient(dl_main.app)
    created = client.post("/literature", json={"title": "Test Doc", "content": "Hello world"})
    assert created.status_code == 200
    lit = created.json()
    assert lit["title"] == "Test Doc"

    fetched = client.get(f"/literature/{lit['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["content"] == "Hello world"

    search = client.get("/literature/search", params={"q": "test"})
    assert search.status_code == 200
    assert search.json()["hits"]
