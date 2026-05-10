import pytest
from unittest.mock import patch
from retriever.bm25_reranker import _normalize, _tokenize, bm25_rerank

def test_normalize():
  # Test loại bỏ dấu câu và chuyển về chữ thường
  text = "Chào bạn! Tôi muốn mua Laptop Dell XPS 13, giá rẻ?"
  expected = "chào bạn tôi muốn mua laptop dell xps 13 giá rẻ"
  assert _normalize(text) == expected

def test_tokenize():
  with patch('retriever.bm25_reranker.ViTokenizer.tokenize') as mock_tokenize:
    mock_tokenize.return_value = 'laptop_gaming msi'
    tokens = _tokenize('laptop gaming msi')
    assert tokens == ['laptop_gaming', 'msi']

def test_bm25_rerank_basic():
  query = 'dell'
  candidates = [
    {"text": "Laptop Asus gaming mạnh mẽ", "metadata": {}},
    {"text": "Dell XPS 13 sang trọng", "metadata": {}},
    {"text": "HP Spectre x360", "metadata": {}},
    {"text": "Macbook Air M2", "metadata": {}}
  ]

  results = bm25_rerank(query, candidates)
  results.sort(key=lambda x: x['bm25_score'], reverse=True)
  assert 'Dell' in results[0]['text']
  assert results[0]['bm25_score'] > 0

def test_bm25_rerank_with_pretokenized_meta():
  query = 'lenovo'
  candidates = [
    {
      "text": "Laptop Lenovo Legion 5", 
      "metadata": {"segmented_text": "laptop lenovo 5"}
    },
    {"text": "Macbook Pro", "metadata": {"segmented_text": "macbook pro"}},
    {"text": "Dell XPS", "metadata": {"segmented_text": "dell xps"}},
    {"text": "Asus Vivobook", "metadata": {"segmented_text": "asus vivobook"}}
  ]

  results = bm25_rerank(query, candidates)
  assert results[0]['bm25_score'] > 0
  assert 'Lenovo' in results[0]['text']
  