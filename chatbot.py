from __future__ import annotations
import time
from core.logger import get_logger
from core.models import ChatResponse
from retriever.semantic_router import classify_query, check_keyword
from retriever.retriever import retrieve_knowledge
from retriever.intent_parser import is_company_query
from llm.generator import generate_response, contextualize_query
from chitchat import handle_chitchat
from embedding.embedder import embed_texts
from core.history import get_history, add_to_history, reset_history

log = get_logger(__name__)

_CONTEXT_PRONOUNS = [
    "nó", "cái này", "cái đó", "mẫu đó", "cái kia", "của nó", "loại đó",
    "loại này", "máy đó", "máy này", "chộ đó", "máy ấy", "cái ấy"
]

def _need_contextualize(query: str) -> bool:
  q = query.lower()
  if any(p in q for p in _CONTEXT_PRONOUNS):
    return True
  # Câu ngắn quá cũng có thể cần context trước đó
  if len(query.split()) <= 4:
    return True
  return False

class Chatbot:
  def __init__(self):
    pass
  
  def _get_history(self, user_id: str, session_id: str) -> list[dict[str, str]]:
    return get_history(user_id=user_id, session_id=session_id)
  
  def _add_to_history(self, user_id: str, session_id: str, role: str, content: str) -> None:
    add_to_history(user_id, session_id, role, content)
  
  def reset_history(self, user_id: str, session_id: str) -> None:
    reset_history(user_id=user_id, session_id=session_id)

  def chat(self, query: str, user_id: str, session_id: str = 'default', save_history: bool = True) -> ChatResponse:
    start = time.time()
    history = self._get_history(user_id, session_id) if save_history else []

    # 0. Kiểm tra keyword matching trên câu GỐC trước!
    kw_route = check_keyword(query)
    
    if kw_route:
      # Nếu match keyword (chitchat hoặc rag) thì không cần contextualize
      standalone_query = query
      query_emb = None
      route = kw_route
      log.info(f"Final query (keyword bypassed): '{standalone_query}' | Route: {route}")
    else:
      # Gắn thêm ngữ cảnh nếu cần thiết
      if history and _need_contextualize(query):
        standalone_query = contextualize_query(query, history)
      else:
        standalone_query = query

      # 1. Embed query 
      query_emb = embed_texts(standalone_query)

      # 2. Phân loại query
      route, scores = classify_query(standalone_query, query_emb)
      log.info(f"Final query: '{standalone_query}' | Route: {route}")

    # 3. Xử lý theo route
    if route == 'chitchat':
      answer = handle_chitchat(standalone_query, history)
      if save_history:
        self._add_to_history(user_id, session_id, 'user', query)
        self._add_to_history(user_id, session_id, 'assistant', answer)
      elapsed = (time.time() - start) * 1000
      return ChatResponse(
        answer = answer,
        products=[],
        docs = [],
        route='chitchat',
        retrieval_time_ms=elapsed
      )
    else:
      company_only = is_company_query(standalone_query)
      docs, intent, retrieval_ms = retrieve_knowledge(
        standalone_query, query_emb=query_emb, company_only=company_only
      )
      answer = generate_response(standalone_query, docs, history)

      products = []
      if not company_only:
        for doc in docs:
          if doc.metadata.get('type') == 'product':
            meta = doc.metadata
            products.append({
              'id': meta.get('product_id', ''),
              'name': meta.get('name', ''),
              'price': meta.get('price', ''),
              'stock': meta.get('stock', ''),
              'image_url': meta.get('image_url', ''),
              'product_url': meta.get('product_url', ''),
              'brand': meta.get('brand', ''),
              'score': doc.score
            })

      if save_history:
        self._add_to_history(user_id, session_id, 'user', query)
        self._add_to_history(user_id, session_id, 'assistant', answer)

      elapsed = (time.time() - start) * 1000
      return ChatResponse(
        answer = answer,
        products=products,
        docs = docs,
        route='company' if company_only else 'rag',
        retrieval_time_ms=elapsed
      )

chatbot = Chatbot()

  