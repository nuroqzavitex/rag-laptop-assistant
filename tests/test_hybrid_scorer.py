import pytest
from retriever.hybrid_scorer import compute_hybrid_scores

def test_compute_hybrid_scores_sorting():
  candidates = [
    {"id": "A", "vector_score": 0.8, "bm25_score": 0.2},
    {"id": "B", "vector_score": 0.5, "bm25_score": 0.9},
    {"id": "C", "vector_score": 0.7, "bm25_score": 0.7},
  ]

  results = compute_hybrid_scores(candidates, alpha = 0.5)
  
  # Kết quả phải được sắp xếp theo hybrid_score giảm dần
  assert results[0]["id"] in ["B", "C"]
  assert results[2]["id"] == "A"
  assert results[0]["hybrid_score"] == 0.7

def test_compute_hybrid_scores_alpha_weight():
  candidates = [
    {"id": "VectorHigh", "vector_score": 0.9, "bm25_score": 0.1},
    {"id": "BM25High", "vector_score": 0.1, "bm25_score": 0.9},
  ]

  # Nếu alpha cao, candidate có vector_score cao sẽ được ưu tiên hơn
  res_vec = compute_hybrid_scores(candidates.copy(), alpha = 0.9)
  assert res_vec[0]["id"] == "VectorHigh"

  # Nếu alpha thấp, candidate có bm25_score cao sẽ được ưu tiên hơn
  res_bm25 = compute_hybrid_scores(candidates.copy(), alpha = 0.1)
  assert res_bm25[0]["id"] == "BM25High"

def test_compute_hybrid_scores_missing_scores():
  candidates = [
    {"id": "Missing", "vector_score": 0.5},  # thiếu bm25_score
  ]

  results = compute_hybrid_scores(candidates, alpha = 0.5)
  assert results[0]["hybrid_score"] == 0.25  # 0.5 * 0.5 + 0.5 * 0 