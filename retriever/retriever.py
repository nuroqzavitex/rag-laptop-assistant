from __future__ import annotations
import time
from typing import Any
from config.settings import cfg
from core.logger import get_logger
from core.models import RetrievedDoc
from embedding.embedder import embed_texts
from vector_store import search as vector_search
from retriever.intent_parser import parse_intent, is_company_query
from retriever.filter_builder import build_where_clause, build_metadata_filter, post_filter_results
from retriever.bm25_reranker import bm25_rerank
from retriever.hybrid_scorer import compute_hybrid_scores

log = get_logger(__name__)

def retrieve_knowledge(query: str, top_k: int | None = None, final_top_k: int | None = None, query_emb: list | None = None, company_only: bool | None = None) -> tuple[list[RetrievedDoc], dict[str, Any], float]:
  # query: câu hỏi user, top_k: số doc lấy từ vector db ban đầu, final_top_k: số doc cuối cùng trả về, query_emb: embed của query nếu có, không phải gọi API embed lại lần nữa
  start = time.time()
  top_k = top_k or cfg.retrieval.top_k
  final_top_k = final_top_k or cfg.retrieval.final_top_k

  # 1. Parse intent
  if company_only is None:
    company_only = is_company_query(query)
  intent = parse_intent(query)
  where = build_where_clause(intent) # filter về hãng, giá,...
  if company_only:
    type_filter = {'type': {'$eq': 'company'}}
    where = type_filter if where is None else {'$and': [where, type_filter]}
  meta_filter = build_metadata_filter(intent) # filter về gpu, ram, storage

  # 2. Embed query
  if query_emb is None:
    query_emb = embed_texts(query)

  # 3. Vector search 
  raw = vector_search(
    collection_name=cfg.qdrant.knowledge_collection,
    query_embedding= query_emb,
    top_k=top_k,
    where=where
  )

  ids = raw['ids'][0] if raw['ids'] else [] # trong raw thuộc tính ids có dạng [[id1, id2,...]]
  
  # Ít kết quả trả về hoặc không có filter thì gắn thêm thông tin công ty và sản phẩm có liên quan
  if len(ids) < 2 and not company_only:
    log.info('Broadening search to include all knowledge types')
    broad_raw = vector_search(
      collection_name=cfg.qdrant.knowledge_collection,
      query_embedding=query_emb,
      top_k = top_k
    )

    existing_ids = set(ids) # Tạo set để tránh trùng lặp point
    for i, doc_id in enumerate(broad_raw['ids'][0]):
      if doc_id not in existing_ids:
        raw['ids'][0].append(doc_id)
        raw['documents'][0].append(broad_raw['documents'][0][i])
        raw['metadatas'][0].append(broad_raw['metadatas'][0][i])
        raw['distances'][0].append(broad_raw['distances'][0][i])
    
    ids = raw['ids'][0]

  if not ids:
    elapsed = (time.time() - start) * 1000
    return [], intent, elapsed
  
  # 4. Build candidate list
  documents = raw['documents'][0]
  metadatas = raw['metadatas'][0]
  distances = raw['distances'][0]

  candidates: list[dict[str, Any]] = []
  for i, doc_id in enumerate(ids):
    vector_score = 1.0 - distances[i]
    candidates.append({
      'id': doc_id,
      'text': documents[i],
      'metadata': metadatas[i],
      'vector_score': max(0, vector_score)
    })

  # 5. Filter các candidate điểm thấp
  min_score = cfg.retrieval.similarity_threshold
  candidates = [c for c in candidates if c['vector_score'] >= min_score]
  if not candidates:
    elapsed = (time.time() - start) * 1000
    return [], intent, elapsed
  
  # 6. Filter bằng meta_filter
  if company_only:
    candidates = [c for c in candidates if c['metadata'].get('type') == 'company']
  else:
    product_candidates = [c for c in candidates if c['metadata'].get('type') == 'product']
    other_candidates = [c for c in candidates if c['metadata'].get('type') != 'product']
    filtered_products = post_filter_results(product_candidates, meta_filter)
    candidates = filtered_products + other_candidates

  # 7. BM25 rerank
  candidates = bm25_rerank(query, candidates)

  # 8. Hybrid score
  candidates = compute_hybrid_scores(candidates)

  # 9. Take top results
  top_candidates = candidates[:final_top_k]

  # 10. Convert sang RetrivedDoc
  docs: list[RetrievedDoc] = []
  for c in top_candidates:
    docs.append(RetrievedDoc(
      text= c['text'],
      metadata = c['metadata'],
      score = c['hybrid_score'],
      source_type = c['metadata'].get('type', 'unknown')
    ))

  elapsed = (time.time() - start) * 1000
  log.info(f'Retrieved {len(docs)} knowledge chunks in {elapsed:.0f} ms')
  return docs, intent, elapsed


  


