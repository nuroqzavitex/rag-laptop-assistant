from __future__ import annotations
import uuid
from typing import Any, Optional
from qdrant_client.models import PointStruct
from core.logger import get_logger
from vector_store.client import _get_client
from vector_store.collection import _ensure_collection
from vector_store.filters import _build_qdrant_filter

log = get_logger(__name__)

def _doc_id_to_uuid(doc_id: str) -> str:
  # Chuyển doc_id thành uuid không thể thay đổi đưa vào Qdrant
  return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))

def upsert_documents(collection_name: str, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict[str, Any]], batch_size: int = 100) -> None:
  # Upsert documents vào Qdrant collection
  _ensure_collection(collection_name, len(embeddings[0]) if embeddings else None)
  client = _get_client()

  for i in range(0, len(ids), batch_size):
    end = min(i+batch_size, len(ids))
    points = []
    for j in range(i, end):
      payload = {**metadatas[j], '_text': texts[j], "_doc_id": ids[j]}
      point_id = _doc_id_to_uuid(ids[j])
      points.append(
        PointStruct(
          id = point_id,
          vector = embeddings[j],
          payload = payload
        )
      )
    
    client.upsert(collection_name=collection_name, points=points)
    log.info(f'Upserted {end}/{len(ids)} docs into {collection_name}')

def search(collection_name: str, query_embedding: list[float], top_k: int = 10, where: Optional[dict[str, Any]] = None) -> dict[str, Any]:
  client = _get_client()
  if not client.collection_exists(collection_name):
    log.info(f'Collection {collection_name} does not exist, returning empty search results')
    return {'ids': [[]], 'documents': [[]], 'metadata': [[]], 'distances': [[]]}
  
  qdrant_filter = _build_qdrant_filter(where) if where else None

  try:
    # Lọc trước rồi mới vector search
    results = client.query_points(
      collection_name = collection_name,
      query = query_embedding,
      limit = top_k,
      query_filter = qdrant_filter,
      with_payload = True
    )

    ids_list = []
    docs_list = []
    meta_list = []
    dis_list = []
    
    for point in results.points:
      # Định dạng lại dữ liệu
      payload = point.payload or {}
      doc_id = payload.pop('_doc_id', str(point.id))
      text = payload.pop('_text', '')

      ids_list.append(doc_id)
      docs_list.append(text)
      meta_list.append(payload)
      dis_list.append(1.0 - point.score)

    return {
      'ids': [ids_list],
      'documents': [docs_list],
      'metadatas': [meta_list],
      'distances': [dis_list]
    }
  
  except Exception as e:
    log.error(f'Qdrant search error: {e}')
    return {'ids': [[]], 'documents': [[]], 'metadata': [[]], 'distances': [[]]}

def add_product_to_collection(collection_name: str, product_id: str, text: str, embedding: list[float], metadata: dict[str, Any]) -> None:
  _ensure_collection(collection_name, len(embedding))
  client = _get_client()

  point_id = _doc_id_to_uuid(product_id)
  payload = {**metadata, '_text': text, '_doc_id': product_id}
  client.upsert(
    collection_name = collection_name,
    points = [
      PointStruct(
        id = point_id,
        vector = embedding,
        payload = payload
      )
    ]
  )
  log.info(f'Added product {product_id} to {collection_name}')


