from __future__ import annotations
import time
from google import genai
from google.genai import types, errors
from config.settings import cfg
from core.logger import get_logger

log = get_logger(__name__)

_client: genai.Client | None = None

def _get_client() -> genai.Client:
  global _client # Sử dụng biến toàn cục để lưu trữ client đã khởi tạo
  if _client is None:
    _client = genai.Client(api_key = cfg.gemini.api_key)
  return _client

def embed_texts(text: str) -> list[float]:
  client = _get_client()
  for attempt in range(3):
    try:
      result = client.models.embed_content(
        model = cfg.gemini.embedding_model,
        contents = text
      )
      return result.embeddings[0].values
    except errors.ClientError as e:
      # Lỗi 429 thường do giới hạn tốc độ, nên thử lại sau một khoảng thời gian
      if "429" in str(e) and attempt < 2:
        log.warning(f'Rate limit (429). Waiting 10s... (Attempt {attempt + 1}/3)')
        time.sleep(10)
        continue
      raise e
  return []

def embed_batch(texts: list[str], batch_size: int = 50) -> list[list[float]]:
  client = _get_client()
  all_embeddings: list[list[float]] = []

  for i in range(0, len(texts), batch_size):
    batch = texts[i: i+batch_size]
    batch_num = i// batch_size + 1
    log.info(f"Embedding batch {batch_num} with {len(batch)} texts...")

    success = False
    attempts = 0
    while not success and attempts < 5:
      try:
        result = client.models.embed_content(
          model = cfg.gemini.embedding_model,
          contents = batch
        )
        for emb in result.embeddings:
          all_embeddings.append(emb.values)
        success = True
        time.sleep(2) # Thêm delay nhỏ giữa các batch để giảm nguy cơ bị rate limit
      
      except errors.ClientError as e:
        attempts += 1
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e): # Nếu gặp lỗi giới hạn tốc độ hoặc tài nguyên, tăng thời gian chờ theo cấp số nhân
          wait_time = 15 * attempts
          log.warning(f'Rate limit or resource exhausted. Waiting {wait_time}s... (Attempt {attempts}/5)')
          time.sleep(wait_time)
        else:
          log.error(f"Error embedding batch {batch_num}: {e}")
          raise e
        
  return all_embeddings