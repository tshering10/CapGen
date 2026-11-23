import os

import redis

from .models import SubtitleDocument


redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
use_redis = os.getenv("CAPGEN_DOCUMENT_STORE", "memory")
redis_client = (
    redis.Redis.from_url(redis_url, decode_responses=True)
    if use_redis == "redis"
    else None
)
documents: dict[str, SubtitleDocument] = {}


def create_document(document: SubtitleDocument) -> None:
    document_id = str(document.id)
    if redis_client is None:
        documents[document_id] = document
        return
    redis_client.set(f"capgen:document:{document_id}", document.model_dump_json())


def get_document(document_id: str) -> SubtitleDocument | None:
    if redis_client is None:
        return documents.get(document_id)
    value = redis_client.get(f"capgen:document:{document_id}")
    if value is None:
        return None
    return SubtitleDocument.model_validate_json(value)


def update_document(document: SubtitleDocument) -> None:
    create_document(document)
