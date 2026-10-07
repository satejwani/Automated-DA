import json
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Try importing pymongo, fallback to lightweight JSON Document Store if unavailable
try:
    from pymongo import MongoClient
    HAS_PYMONGO = True
except ImportError:
    HAS_PYMONGO = False


class JSONCollection:
    """
    Emulates PyMongo Collection interface using persistent JSON file storage.
    """
    def __init__(self, name: str, store_path: Path):
        self.name = name
        self.store_path = store_path

    def _load_data(self) -> List[Dict[str, Any]]:
        if not self.store_path.exists():
            return []
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f).get(self.name, [])
        except Exception:
            return []

    def _save_data(self, items: List[Dict[str, Any]]):
        all_data = {}
        if self.store_path.exists():
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    all_data = json.load(f)
            except Exception:
                all_data = {}
        
        # Serialize datetime objects
        serialized = []
        for item in items:
            cleaned = {}
            for k, v in item.items():
                if isinstance(v, datetime):
                    cleaned[k] = v.isoformat()
                else:
                    cleaned[k] = v
            serialized.append(cleaned)

        all_data[self.name] = serialized
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2)

    def insert_one(self, doc: Dict[str, Any]):
        data = self._load_data()
        data.append(doc)
        self._save_data(data)
        return doc

    def find_one(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        data = self._load_data()
        for doc in data:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    def find(self, query: Dict[str, Any] = None, projection: Optional[Dict[str, Any]] = None):
        query = query or {}
        data = self._load_data()
        results = []
        for doc in data:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                results.append(doc)
        return JSONCursor(results)

    def count_documents(self, query: Dict[str, Any] = None) -> int:
        return len(self.find(query).to_list())

    def create_index(self, *args, **kwargs):
        pass


class JSONCursor:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def sort(self, key: str, direction: int = -1):
        reverse = True if direction < 0 else False
        self.data.sort(key=lambda x: x.get(key, ""), reverse=reverse)
        return self

    def limit(self, n: int):
        self.data = self.data[:n]
        return self

    def to_list(self) -> List[Dict[str, Any]]:
        return self.data

    def __iter__(self):
        return iter(self.data)


class JSONDatabase:
    """
    MongoDB-compatible Database wrapper.
    """
    def __init__(self, store_path: Path):
        self.store_path = store_path

    def __getitem__(self, collection_name: str) -> JSONCollection:
        return JSONCollection(collection_name, self.store_path)


# Singleton database reference
from backend.app.core.config import settings, BASE_DIR
store_file = BASE_DIR / "mongo_data_store.json"
json_db_instance = JSONDatabase(store_file)
mongo_db_instance = None


def get_db():
    global mongo_db_instance
    if HAS_PYMONGO:
        try:
            if mongo_db_instance is None:
                client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1500)
                client.admin.command('ping')
                mongo_db_instance = client[settings.MONGO_DB]
                logger.info(f"Connected to live MongoDB at {settings.MONGO_URI}")
            return mongo_db_instance
        except Exception:
            logger.info(f"Using MongoDB JSON Document Store at {store_file}")
            return json_db_instance
    else:
        logger.info(f"Using MongoDB JSON Document Store at {store_file}")
        return json_db_instance


def get_next_sequence_value(sequence_name: str) -> int:
    database = get_db()
    if HAS_PYMONGO and not isinstance(database, JSONDatabase):
        counter_col = database["counters"]
        doc = counter_col.find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return doc.get("seq", 1) if doc else 1
    else:
        seq_col = database["counters"]
        doc = seq_col.find_one({"_id": sequence_name})
        next_val = (doc.get("seq", 0) if doc else 0) + 1
        data = seq_col._load_data()
        updated = False
        for item in data:
            if item.get("_id") == sequence_name:
                item["seq"] = next_val
                updated = True
                break
        if not updated:
            data.append({"_id": sequence_name, "seq": next_val})
        seq_col._save_data(data)
        return next_val


def init_db_indexes():
    pass

def init_db():
    init_db_indexes()
