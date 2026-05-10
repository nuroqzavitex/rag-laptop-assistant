from __future__ import annotations
import re
from typing import Any
from rank_bm25 import BM25Okapi
from core.logger import get_logger
from pyvi import ViTokenizer

log = get_logger(__name__)

def _normalize(text: str) -> str:
  text = text.lower()
  text = re.sub(r"[^\w\s]", " ", text)
  text = re.sub(r"\s+", " ", text).strip()
  return text

def _tokenize(text: str) -> list[str]:
  if not text:
    return []
  clean_text = _normalize(text)
  return ViTokenizer.tokenize(clean_text).split() # token thành các cụm từ như máy_tính giá_rẻ

def bm25_rerank(query: str, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]: # Gán thêm bm25_score cho mỗi doc trong candidates
  if not candidates:
    return candidates
  
  corpus: list[list[str]] = []
  for c in candidates:
    meta = c.get('metadata', {})
    segmented = meta.get('segmented_text') 
    if segmented:
      corpus.append(segmented.lower().split())
    else:
      corpus.append(_tokenize(c.get('text','')))
  
  bm25 = BM25Okapi(corpus)

  query_tokens = _tokenize(query)
  scores = bm25.get_scores(query_tokens)

  # Chuẩn hóa score về [0, 1]
  max_score = max(scores) if max(scores) > 0 else 1.0
  for i, candidate in enumerate(candidates):
    candidate['bm25_score'] = float(scores[i] / max_score)
  
  log.debug(f'BM25 rerank done for {len(candidates)} candidates')
  return candidates