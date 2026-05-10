import pytest
from unittest.mock import patch
import numpy as np
from retriever.semantic_router import SemanticRouter

@pytest.fixture
def mock_router():
  # Mock phần embedder để không phải call đến model thật trong quá trình test
  with patch('retriever.semantic_router.embed_batch') as mock_batch, \
       patch('retriever.semantic_router.embed_texts') as mock_texts:

    def dummy_embed_batch(texts):
      return [np.random.rand(768) for _ in texts] 
    
    mock_batch.side_effect = dummy_embed_batch # Mỗi câu sẽ được gán một vector ngẫu nhiên khác nhau, n câu thì n vector khác nhau
    mock_texts.return_value = np.random.rand(768) # Một vector ngẫu nhiên cho query

    router = SemanticRouter()
    return router
  
def test_router_normalization(mock_router):
  # Kiểm tra hàm normalize có thực sự chuẩn hóa vector về độ dài 1 không
  v = np.array([[3.0, 4.0]]) # norm = 5.0
  norm_v = mock_router._normalize(v)
  assert np.allclose(norm_v, np.array([[0.6, 0.8]]))
  assert np.linalg.norm(norm_v) == pytest.approx(1.0)

def test_classify_logic(mock_router):
  # Mocking embedding cho query thật gần với chitchat để kiểm tra phân loại đúng không
  mock_router.chitchat_embeddings = np.array([[1.0, 0.0]])
  mock_router.rag_embeddings = np.array([[0.0, 1.0]])

  # Query gần chitchat hơn
  with patch('retriever.semantic_router.embed_texts') as mock_texts:
    mock_texts.return_value = [1.0, 0.0]
    label, scores = mock_router.classify('hi')
    assert label == 'chitchat'
    assert scores['chitchat'] > scores['rag']

def test_classify_logic_rag(mock_router):
  mock_router.chitchat_embeddings = np.array([[1.0, 0.0]])
  mock_router.rag_embeddings = np.array([[0.0, 1.0]])

  with patch('retriever.semantic_router.embed_texts') as mock_texts:
    mock_texts.return_value = [0.0, 1.0]
    label, scores = mock_router.classify('laptop dell')
    assert label == 'rag'
    assert scores['rag'] > scores['chitchat']






