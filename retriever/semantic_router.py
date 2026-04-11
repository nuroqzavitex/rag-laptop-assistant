# Phân loại câu hỏi user là hỏi về sản phẩm và công ty hay câu hỏi ngoài lề

from __future__ import annotations
import numpy as np
from embedding.embedder import embed_batch, embed_texts
from core.logger import get_logger

log = get_logger(__name__)

_CHITCHAT_SAMPLE = [
  "chào bạn", "xin chào", "hello", "hi there", "hey",
  "bạn là ai", "tên bạn là gì", "mày là ai", "bạn có phải chatbot không",
  "cảm ơn bạn", "thank you", "thanks", "tạm biệt", "bye", "hẹn gặp lại",
  "haha", "hihi", "vui quá", "hôm nay thế nào", "bạn khỏe không"
]

_RAG_SAMPLES = [
  "giá laptop dell xps", "tư vấn mua laptop tầm 20tr", "macbook air m1 còn hàng không",
  "địa chỉ shop ở đâu", "cửa hàng ở hà nội", "số điện thoại liên hệ",
  "chính sách bảo hành như thế nào", "có ship code không", "phí vận chuyển bao nhiêu",
  "laptop gaming msi giá rẻ", "thông số kỹ thuật dell inspiron 14", "core i5 ram 16gb",
  "shop có hỗ trợ trả góp không", "giờ mở cửa của shop", "showroom hùng nhữ"
]

class SemanticRouter:
  def __init__(self):
    log.info('Initializing SemanticRouter')

    chitchat_raw = self._get_embedding(_CHITCHAT_SAMPLE) # dim = (N, dim_embed)
    rag_raw = self._get_embedding(_RAG_SAMPLES)

    self.chitchat_embeddings = self._normalize(chitchat_raw)
    self.rag_embeddings = self._nomarlize(rag_raw)
    log.info('Semantic router anchors initialized and normalized')

  def _get_embeddings(self, texts: list[str]) -> np.ndarray:
    return np.array(embed_batch(texts))
  
  def _normalize(self, v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis = 1, keepdims=True) # 
    norm[norm == 0] = 1 # tránh chia cho 0
    return v/norm

  def classify(self, query: str, query_emb: list | None = None) -> tuple[str, dict[str, float]]:
    # Phân loại query 
    if query_emb is not None:
      query_emb_raw = np.array([query_emb])
    else:
      query_emb_raw = np.array([embed_texts(query)])

    query_emb_norm = self._normalize(query_emb_raw)

    sim_chitchat = np.dot(query_emb_norm, self.chitchat_embeddings.T) # dim = (1, N) gồm N điểm tương đồng giữa query với mỗi câu chitchat
    max_chitchat = float(np.max(sim_chitchat)) # Lấy điểm tương đồng cao nhất

    sim_rag = np.dot(query_emb_norm, self.rag_embeddings.T)
    max_rag = float(np.max(sim_rag))

    log.info(f'Router scores -> chitchat: {max_chitchat:.3f}, rag: {max_rag:.3f}')

    if max_chitchat > max_rag and max_chitchat > 0.6:
      return 'chitchat', {'chitchat': max_chitchat, 'rag': max_rag}
    else:
      return 'rag', {'chitchat': max_chitchat, 'rag': max_rag}

_router = None

def init_router():
  global _router # đảm bảo router chỉ chạy 1 lần
  if _router is None:
    _router = SemanticRouter()

def classify_query(query: str, query_emb: list | None = None) -> tuple[str, dict[str, float]]:
  global _router
  if _router is None:
    _router = SemanticRouter()
  return _router.classify(query, query_emb=query_emb)
