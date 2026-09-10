import logging
from typing import Any, Dict, List, Optional
from bson import ObjectId
from config import settings

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    AsyncIOMotorClient = None
    MongoClient = None
    PyMongoError = Exception

logging.basicConfig(level=logging.INFO)


def _matches(document: dict, query: dict) -> bool:
    for key, value in query.items():
        if key not in document:
            return False
        if isinstance(value, dict):
            # support basic operators if needed
            if "$eq" in value:
                if document[key] != value["$eq"]:
                    return False
            else:
                return False
        else:
            doc_value = document[key]
            if key == "_id":
                if str(doc_value) != str(value):
                    return False
            elif isinstance(doc_value, list):
                if value not in doc_value:
                    return False
            elif isinstance(value, list):
                if doc_value not in value:
                    return False
            elif doc_value != value:
                return False
    return True


class InMemoryCursor:
    def __init__(self, docs: List[dict]):
        self._docs = docs.copy()
        self._index = 0

    def sort(self, field: str, direction: int = 1):
        self._docs.sort(key=lambda x: x.get(field), reverse=direction < 0)
        return self

    def skip(self, count: int):
        self._docs = self._docs[count:]
        return self

    def limit(self, count: int):
        self._docs = self._docs[:count]
        return self

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        if self._index >= len(self._docs):
            raise StopAsyncIteration
        item = self._docs[self._index]
        self._index += 1
        return item


class InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self._documents: List[dict] = []

    async def find_one(self, query: dict = None, sort: Optional[List[tuple]] = None, projection: Optional[dict] = None):
        query = query or {}
        matches = [doc for doc in self._documents if _matches(doc, query)]
        if sort:
            for field, direction in reversed(sort):
                matches.sort(key=lambda x: x.get(field), reverse=direction < 0)
        if not matches:
            return None
        return matches[0]

    async def insert_one(self, document: dict):
        if "_id" not in document:
            document["_id"] = ObjectId()
        self._documents.append(document)

        class Result:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id

        return Result(document["_id"])

    async def count_documents(self, query: dict = None):
        query = query or {}
        return sum(1 for doc in self._documents if _matches(doc, query))

    async def distinct(self, key: str, query: dict = None):
        query = query or {}
        return list({doc.get(key) for doc in self._documents if _matches(doc, query)})

    def find(self, query: dict = None, projection: Optional[dict] = None):
        query = query or {}
        docs = [doc for doc in self._documents if _matches(doc, query)]
        if projection is not None:
            projected = []
            for doc in docs:
                filtered = {k: v for k, v in doc.items() if k in projection and projection[k]}
                projected.append(filtered)
            docs = projected
        return InMemoryCursor(docs)

    async def aggregate(self, pipeline: List[dict]):
        docs = self._documents
        if pipeline and isinstance(pipeline[0], dict) and "$group" in pipeline[0]:
            group_spec = pipeline[0]["$group"]
            result = {}
            for doc in docs:
                key = None if group_spec.get("_id") is None else doc.get(group_spec["_id"].lstrip("$"))
                if key not in result:
                    result[key] = {"count": 0}
                    for field in group_spec:
                        if field != "_id":
                            result[key][field] = 0
                for field, expr in group_spec.items():
                    if field == "_id":
                        continue
                    if "$avg" in expr:
                        field_name = expr["$avg"].lstrip("$")
                        result[key][field] += doc.get(field_name, 0)
                    elif "$sum" in expr:
                        field_name = expr["$sum"].lstrip("$")
                        result[key][field] += doc.get(field_name, 0)
                result[key]["count"] += 1
            output = []
            for values in result.values():
                doc = {}
                for field, value in group_spec.items():
                    if field == "_id":
                        continue
                    if "$avg" in value:
                        field_name = value["$avg"].lstrip("$")
                        doc[field] = values[field] / values["count"] if values["count"] else 0
                    elif "$sum" in value:
                        doc[field] = values[field]
                output.append(doc)
            return InMemoryCursor(output)
        return InMemoryCursor(docs)


class InMemoryDatabase:
    def __init__(self):
        self._collections: Dict[str, InMemoryCollection] = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self._collections:
            self._collections[name] = InMemoryCollection(name)
        return self._collections[name]


def _create_mongo_database():
    if not settings.MONGODB_URL:
        raise ValueError("MONGODB_URL is not configured")
    if AsyncIOMotorClient is None or MongoClient is None:
        raise ImportError("MongoDB client libraries are not installed")

    try:
        sync_client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        sync_client.admin.command("ping")
        motor_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        return motor_client[settings.DATABASE_NAME]
    except PyMongoError as exc:
        logging.warning("MongoDB connection failed: %s", exc)
        return None


db = _create_mongo_database()
if db is None:
    logging.warning("Using in-memory fallback database because MongoDB is unavailable.")
    db = InMemoryDatabase()

# Collections
users_collection = db["users"]
projects_collection = db["projects"]
certificates_collection = db["certificates"]
metrics_collection = db["metrics"]
webhook_events_collection = db["webhook_events"]
notifications_collection = db["notifications"]
teams_collection = db["teams"]


async def get_database():
    return db
