import time
import google.generativeai as genai
from core.load_settings import cfg
import logging

logger = logging.getLogger('embedder')

class Embedder:
  def __init__(self):
    genai.configure(api_key=cfg.GEMINI_API_KEY)
    self.model = cfg.EMBEDDING_MODEL

  def embed_texts(self, texts: list[str]) -> list[list[float]]:
    results = []
    for i, text in enumerate(texts):
      logger.info(f'Embedding {i+1}/{len(texts)}...')
      results.append(self._embed_one(text))
      time.sleep(0.1)  # Thêm delay để tránh rate limit
    return results
  
  def embed_query(self, query: str) -> list[float]:
    return self._embed_one(query)
  
  def _embed_one(self, text:str, max_retries: int = 3) -> list[float]:
    for attempt in range(max_retries):
      try:
        res = genai.embed_content(model = self.model, content = text)
        return res['embedding']
      except Exception as e:
        if attempt == max_retries - 1:
          raise RuntimeError(f'Failed to embed text after {max_retries} attempts: {e}')
        wait = 2**(attempt + 1)
        logger.error(f'Error embedding text (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait} seconds...')
        time.sleep(wait)
    return []